import asyncio
from pathlib import Path

from .models import IncidentEvent, IncidentRecord, IncidentState, utc_now


class IncidentStore:
    def __init__(self, runtime_dir: Path) -> None:
        self.path = runtime_dir / "incidents"
        self.path.mkdir(parents=True, exist_ok=True)
        self._records: dict[str, IncidentRecord] = {}
        self._conditions: dict[str, asyncio.Condition] = {}

    def reset(self) -> None:
        self._records.clear()
        self._conditions.clear()
        for item in self.path.glob("*.json"):
            item.unlink()

    def create(self, record: IncidentRecord) -> IncidentRecord:
        record.events.append(
            IncidentEvent(sequence=1, state=record.state, message="Dangerous schema diff detected")
        )
        self._records[record.run_id] = record
        self._conditions[record.run_id] = asyncio.Condition()
        self._persist(record)
        return record

    def get(self, run_id: str) -> IncidentRecord | None:
        if run_id in self._records:
            return self._records[run_id]
        file_path = self.path / f"{run_id}.json"
        if file_path.exists():
            record = IncidentRecord.model_validate_json(file_path.read_text())
            self._records[run_id] = record
            self._conditions[run_id] = asyncio.Condition()
            return record
        return None

    async def transition(self, record: IncidentRecord, state: IncidentState, message: str) -> None:
        record.state = state
        record.updated_at = utc_now()
        record.events.append(
            IncidentEvent(sequence=len(record.events) + 1, state=state, message=message)
        )
        self._persist(record)
        condition = self._conditions[record.run_id]
        async with condition:
            condition.notify_all()

    def save(self, record: IncidentRecord) -> None:
        record.updated_at = utc_now()
        self._persist(record)

    async def wait_for_events(
        self, run_id: str, after: int, timeout: float = 15
    ) -> list[IncidentEvent]:
        record = self.get(run_id)
        if record is None:
            return []
        events = [event for event in record.events if event.sequence > after]
        if events:
            return events
        condition = self._conditions[run_id]
        try:
            async with condition:
                await asyncio.wait_for(condition.wait(), timeout=timeout)
        except TimeoutError:
            pass
        return [event for event in record.events if event.sequence > after]

    def _persist(self, record: IncidentRecord) -> None:
        destination = self.path / f"{record.run_id}.json"
        temporary = destination.with_suffix(".tmp")
        temporary.write_text(record.model_dump_json(indent=2))
        temporary.replace(destination)
