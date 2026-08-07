import time
from collections import defaultdict, deque
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from .config import settings
from .datahub_mcp import DataHubMCPClient
from .deepseek import DeepSeekRepairGenerator
from .models import ApprovalRequest, IncidentCreateRequest, IncidentRecord, IncidentState
from .orchestrator import IncidentOrchestrator
from .store import IncidentStore
from .warehouse import WarehouseRunner

store = IncidentStore(settings.repairpilot_runtime_dir)
orchestrator = IncidentOrchestrator(
    settings,
    store,
    DataHubMCPClient(settings),
    DeepSeekRepairGenerator(settings),
    WarehouseRunner(settings),
)

app = FastAPI(
    title="RepairPilot API",
    version="0.1.0",
    description="Fail-closed incident-to-repair orchestration for governed dbt changes.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.repairpilot_public_url, "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

requests_by_ip: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def public_rate_limit(request: Request, call_next):  # type: ignore[no-untyped-def]
    if request.method == "POST":
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        history = requests_by_ip[client]
        while history and history[0] < now - 3600:
            history.popleft()
        if len(history) >= 20:
            return JSONResponse(status_code=429, content={"detail": "Demo rate limit reached"})
        history.append(now)
    return await call_next(request)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "mode": settings.repairpilot_mode}


@app.post("/api/v1/demo/reset")
async def reset_demo() -> dict[str, str]:
    try:
        await orchestrator.reset()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {"status": "reset", "mode": settings.repairpilot_mode}


@app.post("/api/v1/incidents", response_model=IncidentRecord, status_code=202)
async def create_incident(body: IncidentCreateRequest) -> IncidentRecord:
    if body.execution_mode == "live" and settings.repairpilot_mode == "replay":
        raise HTTPException(status_code=503, detail="Hosted service is in replay-only mode")
    return orchestrator.start(body.execution_mode)


@app.get("/api/v1/incidents/{run_id}", response_model=IncidentRecord)
async def get_incident(run_id: str) -> IncidentRecord:
    record = store.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found")
    return record


@app.get("/api/v1/incidents/{run_id}/events")
async def incident_events(run_id: str, after: int = 0) -> StreamingResponse:
    if not store.get(run_id):
        raise HTTPException(status_code=404, detail="Incident not found")

    async def stream() -> AsyncIterator[str]:
        sequence = after
        terminal = {
            IncidentState.LEARNED,
            IncidentState.REJECTED,
            IncidentState.CONTEXT_UNAVAILABLE,
            IncidentState.VALIDATION_FAILED,
            IncidentState.MANUAL_REVIEW,
        }
        while True:
            events = await store.wait_for_events(run_id, sequence)
            if not events:
                yield ": keepalive\n\n"
                continue
            for event in events:
                sequence = event.sequence
                yield f"id: {event.sequence}\ndata: {event.model_dump_json()}\n\n"
            current = store.get(run_id)
            if current and current.state in terminal:
                break

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/v1/incidents/{run_id}/approval", response_model=IncidentRecord)
async def approve_incident(run_id: str, body: ApprovalRequest) -> IncidentRecord:
    record = store.get(run_id)
    if not record:
        raise HTTPException(status_code=404, detail="Incident not found")
    try:
        return await orchestrator.approve(record, body.decision, body.actor)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/v1/incidents/{run_id}/artifacts/{artifact}")
async def download_artifact(run_id: str, artifact: str) -> FileResponse:
    allowed = {
        "repair.patch",
        "evidence-receipt.json",
        "run_results.json",
        "dbt-command-results.json",
    }
    if artifact not in allowed:
        raise HTTPException(status_code=404, detail="Artifact not found")
    path = settings.repairpilot_runtime_dir / "artifacts" / run_id / artifact
    if not path.exists():
        raise HTTPException(status_code=404, detail="Artifact not ready")
    media_type = "application/json" if artifact.endswith(".json") else "text/x-diff"
    return FileResponse(path, media_type=media_type, filename=artifact)
