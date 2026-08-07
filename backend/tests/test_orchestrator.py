import asyncio
from pathlib import Path

import pytest
from app.config import Settings
from app.deepseek import DeepSeekRepairGenerator
from app.models import (
    IncidentState,
    ValidationReceipt,
    WritebackReceipt,
)
from app.orchestrator import IncidentOrchestrator
from app.store import IncidentStore


class FakeDataHub:
    def __init__(self, context):
        self.context = context

    async def collect_context(self):
        return self.context

    async def write_back(self, **kwargs):
        return WritebackReceipt(
            incident_document_urn="urn:li:document:test-incident",
            runbook_document_urn="urn:li:document:test-runbook",
            updated_entity_urns=[self.context.asset_urn],
            assertion_urns=["urn:li:assertion:test"],
        )


class FakeGenerator:
    async def generate(self, context, risk, *, replay=False):
        return DeepSeekRepairGenerator.replay_proposal()


class FakeWarehouse:
    def validate_repair(self, run_id, proposal):
        return ValidationReceipt(
            breaking_change_reproduced=True,
            repair_verified=True,
            invocation_id="invocation-test",
            command_results=[],
            tests_passed=8,
            tests_failed=0,
            patch_sha256="a" * 64,
            patch_path=f"runtime/{run_id}/repair.patch",
            base_commit="b" * 40,
            repair_commit="c" * 40,
        )

    def reset_demo_schemas(self):
        return None


async def wait_for_state(store, run_id, expected, timeout=2):
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        record = store.get(run_id)
        if record and record.state == expected:
            return record
        await asyncio.sleep(0.01)
    raise AssertionError(f"incident did not reach {expected}")


@pytest.mark.asyncio
async def test_high_risk_flow_requires_approval_and_learns(tmp_path: Path, context):
    settings = Settings(
        repairpilot_runtime_dir=tmp_path / "runtime",
        repairpilot_repo_root=tmp_path,
        github_canonical_pr_url="https://github.com/TianChen17/repairpilot/pull/1",
    )
    store = IncidentStore(settings.repairpilot_runtime_dir)
    orchestrator = IncidentOrchestrator(
        settings,
        store,
        FakeDataHub(context),
        FakeGenerator(),
        FakeWarehouse(),
    )

    record = orchestrator.start("live")
    record = await wait_for_state(store, record.run_id, IncidentState.AWAITING_APPROVAL)
    assert record.risk is not None and record.risk.action == "BLOCK"
    assert record.validation is not None and record.validation.repair_verified

    await orchestrator.approve(record, "approve", "Revenue Analytics Owner")
    learned = await wait_for_state(store, record.run_id, IncidentState.LEARNED)
    assert learned.writeback is not None
    assert learned.approval is not None
    assert learned.approval.decision == "approve"


@pytest.mark.asyncio
async def test_rejection_never_publishes(tmp_path: Path, context):
    settings = Settings(
        repairpilot_runtime_dir=tmp_path / "runtime", repairpilot_repo_root=tmp_path
    )
    store = IncidentStore(settings.repairpilot_runtime_dir)
    orchestrator = IncidentOrchestrator(
        settings,
        store,
        FakeDataHub(context),
        FakeGenerator(),
        FakeWarehouse(),
    )

    record = orchestrator.start("live")
    record = await wait_for_state(store, record.run_id, IncidentState.AWAITING_APPROVAL)
    rejected = await orchestrator.approve(record, "reject", "Revenue Analytics Owner")

    assert rejected.state == IncidentState.REJECTED
    assert rejected.writeback is None
