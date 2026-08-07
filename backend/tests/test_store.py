from app.models import IncidentRecord, IncidentState
from app.store import IncidentStore


def test_store_persists_and_reloads(runtime_dir):
    store = IncidentStore(runtime_dir)
    record = store.create(IncidentRecord(run_id="test-run", mode="replay"))
    assert record.state == IncidentState.DETECTED

    reloaded = IncidentStore(runtime_dir).get("test-run")
    assert reloaded is not None
    assert reloaded.run_id == "test-run"
    assert reloaded.events[0].message == "Dangerous schema diff detected"
