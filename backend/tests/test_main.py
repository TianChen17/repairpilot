from pathlib import Path

import pytest
from app import main
from app.models import IncidentRecord, IncidentState
from fastapi.testclient import TestClient


class FakeStore:
    def __init__(self, record: IncidentRecord | None = None):
        self.record = record

    def get(self, run_id: str):
        if self.record and self.record.run_id == run_id:
            return self.record
        return None


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    main.requests_by_ip.clear()
    monkeypatch.setattr(main.settings, "repairpilot_runtime_dir", tmp_path)
    return TestClient(main.app, client=("127.0.0.1", 50000))


def test_health_and_create_contract(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    record = IncidentRecord(run_id="run-1")
    monkeypatch.setattr(
        main.orchestrator, "start", lambda mode: record.model_copy(update={"mode": mode})
    )

    assert api_client.get("/api/health").json()["status"] == "ok"
    response = api_client.post(
        "/api/v1/incidents",
        json={"scenario": "breaking-column-rename", "execution_mode": "replay"},
    )
    assert response.status_code == 202
    assert response.json()["mode"] == "replay"
    assert api_client.post("/api/v1/incidents", json={"scenario": "unknown"}).status_code == 422


def test_get_and_approval_boundaries(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    record = IncidentRecord(run_id="run-1", state=IncidentState.AWAITING_APPROVAL)
    monkeypatch.setattr(main, "store", FakeStore(record))

    async def approve(current, decision, actor):
        return current.model_copy(update={"state": IncidentState.REJECTED})

    monkeypatch.setattr(main.orchestrator, "approve", approve)
    assert api_client.get("/api/v1/incidents/missing").status_code == 404
    assert api_client.get("/api/v1/incidents/run-1").status_code == 200
    rejected = api_client.post(
        "/api/v1/incidents/run-1/approval",
        json={"decision": "reject", "actor": "Revenue Analytics Owner"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["state"] == "REJECTED"
    assert (
        api_client.post(
            "/api/v1/incidents/missing/approval",
            json={"decision": "approve", "actor": "Owner"},
        ).status_code
        == 404
    )


def test_reset_conflict_and_artifact_allowlist(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    async def blocked_reset():
        raise RuntimeError("A live incident is currently running")

    monkeypatch.setattr(main.orchestrator, "reset", blocked_reset)
    assert api_client.post("/api/v1/demo/reset").status_code == 409
    assert api_client.get("/api/v1/incidents/run-1/artifacts/../../.env").status_code == 404
    assert api_client.get("/api/v1/incidents/run-1/artifacts/not-allowed.txt").status_code == 404

    artifact = tmp_path / "artifacts/run-1/evidence-receipt.json"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("{}")
    response = api_client.get("/api/v1/incidents/run-1/artifacts/evidence-receipt.json")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_rate_limit_is_enforced(api_client: TestClient, monkeypatch: pytest.MonkeyPatch):
    record = IncidentRecord(run_id="run-rate")
    monkeypatch.setattr(main.orchestrator, "start", lambda mode: record)
    headers = {"x-forwarded-for": "203.0.113.10"}
    for _ in range(20):
        assert api_client.post("/api/v1/incidents", json={}, headers=headers).status_code == 202
    assert api_client.post("/api/v1/incidents", json={}, headers=headers).status_code == 429

    other_judge = {"x-forwarded-for": "203.0.113.11"}
    assert api_client.post("/api/v1/incidents", json={}, headers=other_judge).status_code == 202


def test_reset_and_approval_do_not_consume_run_quota(
    api_client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    async def clean_reset():
        return None

    record = IncidentRecord(run_id="run-after-control-actions")
    monkeypatch.setattr(main.orchestrator, "reset", clean_reset)
    monkeypatch.setattr(main.orchestrator, "start", lambda mode: record)
    headers = {"x-forwarded-for": "203.0.113.12"}

    for _ in range(10):
        assert api_client.post("/api/v1/demo/reset", headers=headers).status_code == 200
        assert (
            api_client.post(
                "/api/v1/incidents/missing/approval",
                json={"decision": "reject", "actor": "Owner"},
                headers=headers,
            ).status_code
            == 404
        )

    assert api_client.post("/api/v1/incidents", json={}, headers=headers).status_code == 202
