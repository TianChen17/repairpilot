import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from app.config import Settings
from app.datahub_mcp import DataHubContextError, DataHubMCPClient


def client(tmp_path: Path) -> DataHubMCPClient:
    settings = Settings(
        repairpilot_runtime_dir=tmp_path / "runtime",
        repairpilot_repo_root=tmp_path,
    )
    return DataHubMCPClient(settings)


def test_mcp_subprocess_environment_excludes_agent_credentials(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("DEEPSEEK_API_KEY_FILE", "/run/credentials/secret")
    monkeypatch.setenv("GITHUB_PAT_TianChen_17", "must-not-propagate")

    parameters = client(tmp_path)._parameters()

    assert "DEEPSEEK_API_KEY_FILE" not in parameters.env
    assert "GITHUB_PAT_TianChen_17" not in parameters.env
    assert parameters.env["DATAHUB_GMS_URL"] == "http://127.0.0.1:8080"


def test_decode_result_accepts_json_and_rejects_errors():
    success = SimpleNamespace(isError=False, content=[SimpleNamespace(text='{"ok": true}')])
    failure = SimpleNamespace(isError=True, content=[])

    assert DataHubMCPClient._decode_result("search", success) == {"ok": True}
    with pytest.raises(DataHubContextError, match="returned an error"):
        DataHubMCPClient._decode_result("search", failure)


@pytest.mark.asyncio
async def test_collect_context_is_derived_from_mcp_results(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    datahub = client(tmp_path)
    evidence = {
        "asset": "mart_executive_revenue int_order_revenue fct_daily_revenue",
        "schema": "order_id ordered_at region currency gross_amount",
        "governance": "Revenue Analytics Tier1 FinancialMetric SLA-1h Finance Analytics",
        "dashboard": "Executive Revenue Pulse All assertions are passing",
        "queries": (
            "SELECT region, SUM(gross_amount) "
            "SELECT ordered_at::date, SUM(gross_amount) "
            "SELECT currency, AVG(gross_amount)"
        ),
    }

    async def fake_call_tools(calls):
        assert [name for name, _ in calls] == [
            "search",
            "get_entities",
            "list_schema_fields",
            "get_lineage",
            "get_dataset_queries",
        ]
        return [evidence, evidence, evidence, evidence, evidence]

    monkeypatch.setattr(datahub, "call_tools", fake_call_tools)
    context = await datahub.collect_context()

    assert context.owners == ["Revenue Analytics"]
    assert context.tags == ["Tier1", "FinancialMetric", "SLA-1h"]
    assert context.domain == "Finance Analytics"
    assert len(context.downstream_assets) == 3
    assert context.downstream_dashboards == ["Executive Revenue Pulse"]
    assert len(context.queries) == 3
    assert len(context.evidence) == 5


@pytest.mark.asyncio
async def test_collect_context_fails_closed_when_mcp_evidence_is_incomplete(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    datahub = client(tmp_path)

    async def incomplete(calls):
        return [{} for _ in calls]

    monkeypatch.setattr(datahub, "call_tools", incomplete)
    with pytest.raises(DataHubContextError, match="evidence is incomplete"):
        await datahub.collect_context()


@pytest.mark.asyncio
async def test_writeback_is_idempotent_and_validates_mutations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    datahub = client(tmp_path)
    monkeypatch.setattr(
        datahub,
        "_upsert_validation_assertion",
        lambda patch_sha256, invocation_id: "urn:li:assertion:test",
    )
    calls_seen = []

    async def successful_calls(calls):
        calls_seen.append(calls)
        return [
            {"success": True},
            {"success": True, "urn": "urn:li:document:incident"},
            {"success": True, "urn": "urn:li:document:runbook"},
        ]

    monkeypatch.setattr(datahub, "call_tools", successful_calls)
    first = await datahub.write_back(
        run_id="run-1",
        incident_markdown="# Incident",
        runbook_markdown="# Runbook",
        patch_sha256="a" * 64,
        invocation_id="dbt-1",
    )
    second = await datahub.write_back(
        run_id="run-1",
        incident_markdown="# Incident updated",
        runbook_markdown="# Runbook",
        patch_sha256="a" * 64,
        invocation_id="dbt-2",
    )

    assert first.incident_document_urn == second.incident_document_urn
    assert first.runbook_document_urn == second.runbook_document_urn
    assert calls_seen[1][1][1]["urn"] == "urn:li:document:incident"
    assert calls_seen[1][2][1]["urn"] == "urn:li:document:runbook"


def test_document_state_and_mutation_fail_closed(tmp_path: Path):
    datahub = client(tmp_path)
    state_path = datahub.settings.repairpilot_runtime_dir / "datahub-documents.json"
    state_path.write_text("not-json")

    with pytest.raises(DataHubContextError, match="unreadable"):
        datahub._load_document_state()
    with pytest.raises(DataHubContextError, match="not successful"):
        datahub._require_successful_mutation("document", {"success": False})


def test_extract_urn_has_explicit_fallback():
    assert DataHubMCPClient._extract_urn({"urn": "urn:li:document:one"}, "fallback") == (
        "urn:li:document:one"
    )
    assert DataHubMCPClient._extract_urn({}, "fallback") == "urn:li:document:fallback"
    assert json.loads(json.dumps({"safe": True}))["safe"] is True
