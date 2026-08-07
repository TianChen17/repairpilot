import asyncio
import json
import os
from collections.abc import Iterable
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import Settings
from .models import ContextSnapshot, EvidenceItem, WritebackReceipt, utc_now


class DataHubContextError(RuntimeError):
    pass


class DataHubMCPClient:
    """Strict stdio client for the official DataHub MCP server."""

    ASSET_URN = (
        "urn:li:dataset:(urn:li:dataPlatform:dbt,repairpilot.analytics_staging.stg_orders,PROD)"
    )
    COLUMN_URN = f"urn:li:schemaField:({ASSET_URN},gross_amount)"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _parameters(self) -> StdioServerParameters:
        # The MCP subprocess gets only the runtime values it requires. In particular,
        # never inherit DEEPSEEK_API_KEY_FILE or unrelated credentials from systemd.
        safe_parent_env = {
            key: value
            for key, value in os.environ.items()
            if key in {"HOME", "LANG", "LC_ALL", "PATH", "PYTHONIOENCODING", "TMPDIR"}
        }
        env = {
            **safe_parent_env,
            "DATAHUB_GMS_URL": self.settings.datahub_gms_url,
            "DATAHUB_GMS_TOKEN": self.settings.datahub_gms_token,
            "TOOLS_IS_MUTATION_ENABLED": "true",
            "SAVE_DOCUMENT_PARENT_TITLE": "RepairPilot",
            "SAVE_DOCUMENT_RESTRICT_UPDATES": "true",
            "TOOL_RESPONSE_TOKEN_LIMIT": "20000",
        }
        return StdioServerParameters(
            command=self.settings.datahub_mcp_command,
            args=([self.settings.datahub_mcp_package] if self.settings.datahub_mcp_package else []),
            env=env,
        )

    async def list_tools(self) -> dict[str, dict[str, Any]]:
        async with stdio_client(self._parameters()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return {tool.name: tool.inputSchema for tool in result.tools}

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return (await self.call_tools([(name, arguments)]))[0]

    async def call_tools(self, calls: list[tuple[str, dict[str, Any]]]) -> list[Any]:
        values: list[Any] = []
        async with stdio_client(self._parameters()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for name, arguments in calls:
                    result = await session.call_tool(name, arguments)
                    values.append(self._decode_result(name, result))
        return values

    @staticmethod
    def _decode_result(name: str, result: Any) -> Any:
        if result.isError:
            raise DataHubContextError(f"DataHub MCP tool {name} returned an error")
        texts = [getattr(item, "text", "") for item in result.content]
        combined = "\n".join(text for text in texts if text)
        try:
            return json.loads(combined)
        except json.JSONDecodeError:
            return combined

    async def collect_context(self) -> ContextSnapshot:
        calls = [
            ("search", {"query": "mart_executive_revenue"}),
            ("get_entities", {"urns": [self.ASSET_URN]}),
            ("list_schema_fields", {"urn": self.ASSET_URN}),
            (
                "get_lineage",
                {
                    "urn": self.ASSET_URN,
                    "column": "gross_amount",
                    "upstream": False,
                    "max_hops": 4,
                    "max_results": 30,
                },
            ),
            ("get_dataset_queries", {"urn": self.ASSET_URN}),
        ]
        raw: dict[str, Any] = {}
        evidence: list[EvidenceItem] = []
        results = await self.call_tools(calls)
        for (tool, arguments), result in zip(calls, results, strict=True):
            raw[tool] = result
            evidence.append(
                EvidenceItem(
                    source="datahub_mcp",
                    tool=tool,
                    summary=f"Official DataHub MCP {tool} evidence captured",
                    payload={"arguments": arguments, "result": result},
                )
            )

        evidence_text = json.dumps(raw, default=str).casefold()
        required_markers = {
            "asset": "mart_executive_revenue",
            "field": "gross_amount",
            "owner": "revenue analytics",
            "tag": "tier1",
        }
        missing = [name for name, marker in required_markers.items() if marker not in evidence_text]
        if missing:
            raise DataHubContextError(
                "DataHub MCP evidence is incomplete: " + ", ".join(sorted(missing))
            )

        return ContextSnapshot(
            asset_urn=self.ASSET_URN,
            column_urn=self.COLUMN_URN,
            owners=["Revenue Analytics"],
            tags=self._present(evidence_text, ["Tier1", "FinancialMetric", "SLA-1h"]),
            domain="Finance Analytics" if "finance analytics" in evidence_text else None,
            downstream_assets=self._present(
                evidence_text,
                ["int_order_revenue", "fct_daily_revenue", "mart_executive_revenue"],
            ),
            downstream_dashboards=self._present(evidence_text, ["Executive Revenue Pulse"]),
            queries=self._query_markers(evidence_text),
            assertions=self._present(
                evidence_text,
                ["All assertions are passing"],
            ),
            schema_fields=self._present(
                evidence_text,
                ["order_id", "ordered_at", "region", "currency", "gross_amount"],
            ),
            evidence=evidence,
        )

    async def write_back(
        self,
        *,
        run_id: str,
        incident_markdown: str,
        runbook_markdown: str,
        patch_sha256: str,
        invocation_id: str,
    ) -> WritebackReceipt:
        # Tool schemas are verified at deployment time; the explicit calls remain auditable.
        assertion_urn = await asyncio.to_thread(
            self._upsert_validation_assertion,
            patch_sha256,
            invocation_id,
        )
        document_state = self._load_document_state()
        incident_urn = document_state.get("incidents", {}).get(run_id)
        runbook_urn = document_state.get("runbook")
        incident_arguments: dict[str, Any] = {
            "document_type": "Analysis",
            "title": f"RepairPilot Incident {run_id}",
            "content": incident_markdown,
            "topics": ["RepairPilot", "incident", "synthetic-demo"],
            "related_assets": [self.ASSET_URN],
        }
        if incident_urn:
            incident_arguments["urn"] = incident_urn
        runbook_arguments: dict[str, Any] = {
            "document_type": "Decision",
            "title": "Safe dbt Column Rename Runbook",
            "content": runbook_markdown,
            "topics": ["RepairPilot", "dbt", "runbook"],
            "related_assets": [self.ASSET_URN],
        }
        if runbook_urn:
            runbook_arguments["urn"] = runbook_urn

        mutation_calls = [
            (
                "add_tags",
                {
                    "entity_urns": [self.ASSET_URN],
                    "tag_urns": ["urn:li:tag:RepairPilotVerified"],
                },
            ),
            (
                "save_document",
                incident_arguments,
            ),
            (
                "save_document",
                runbook_arguments,
            ),
        ]
        _, incident, runbook = await self.call_tools(mutation_calls)
        self._require_successful_mutation("incident document", incident)
        self._require_successful_mutation("runbook document", runbook)
        incident_urn = self._extract_urn(incident, f"repairpilot-incident-{run_id}")
        runbook_urn = self._extract_urn(runbook, "safe-dbt-column-rename-runbook")
        document_state.setdefault("incidents", {})[run_id] = incident_urn
        document_state["runbook"] = runbook_urn
        self._save_document_state(document_state)
        return WritebackReceipt(
            incident_document_urn=incident_urn,
            runbook_document_urn=runbook_urn,
            updated_entity_urns=[self.ASSET_URN],
            assertion_urns=[assertion_urn],
        )

    def _upsert_validation_assertion(self, patch_sha256: str, invocation_id: str) -> str:
        from datahub.emitter import mce_builder
        from datahub.emitter.mcp import MetadataChangeProposalWrapper
        from datahub.emitter.rest_emitter import DatahubRestEmitter
        from datahub.metadata import schema_classes as models

        assertion_urn = mce_builder.make_assertion_urn("repairpilot-gross-revenue-not-null")
        audit = models.AuditStampClass(
            time=int(utc_now().timestamp() * 1000),
            actor="urn:li:corpuser:datahub",
        )
        emitter = DatahubRestEmitter(
            self.settings.datahub_gms_url,
            token=self.settings.datahub_gms_token or None,
        )
        aspects = [
            models.AssertionInfoClass(
                type=models.AssertionTypeClass.DATASET,
                description=(
                    "RepairPilot-verified dbt contract: gross_revenue must remain non-null."
                ),
                customProperties={
                    "patch_sha256": patch_sha256,
                    "dbt_invocation_id": invocation_id,
                    "data_classification": "synthetic",
                },
                source=models.AssertionSourceClass(
                    type=models.AssertionSourceTypeClass.EXTERNAL,
                    created=audit,
                ),
                lastUpdated=audit,
                entityUrn=self.ASSET_URN,
                datasetAssertion=models.DatasetAssertionInfoClass(
                    dataset=self.ASSET_URN,
                    scope=models.DatasetAssertionScopeClass.DATASET_COLUMN,
                    operator=models.AssertionStdOperatorClass.NOT_NULL,
                    fields=[mce_builder.make_schema_field_urn(self.ASSET_URN, "gross_revenue")],
                    aggregation=models.AssertionStdAggregationClass.IDENTITY,
                    nativeType="not_null",
                    nativeParameters={"column_name": "gross_revenue"},
                ),
            ),
            models.AssertionRunEventClass(
                timestampMillis=audit.time,
                runId=invocation_id,
                asserteeUrn=self.ASSET_URN,
                status=models.AssertionRunStatusClass.COMPLETE,
                assertionUrn=assertion_urn,
                result=models.AssertionResultClass(
                    type=models.AssertionResultTypeClass.SUCCESS,
                    nativeResults={
                        "validated_by": "dbt build --select stg_orders+",
                        "patch_sha256": patch_sha256,
                    },
                ),
            ),
            models.StatusClass(removed=False),
            models.GlobalTagsClass(
                tags=[
                    models.TagAssociationClass(tag="urn:li:tag:RepairPilotVerified"),
                    models.TagAssociationClass(tag="urn:li:tag:SyntheticDemo"),
                ]
            ),
        ]
        for aspect in aspects:
            emitter.emit_mcp(
                MetadataChangeProposalWrapper(
                    entityUrn=assertion_urn,
                    aspect=aspect,
                ),
                async_flag=False,
            )
        emitter.flush()
        return assertion_urn

    @staticmethod
    def _present(haystack: str, values: Iterable[str]) -> list[str]:
        return [value for value in values if value.casefold() in haystack]

    @staticmethod
    def _query_markers(haystack: str) -> list[str]:
        candidates = [
            "SELECT region, SUM(gross_amount)",
            "SELECT ordered_at::date, SUM(gross_amount)",
            "SELECT currency, AVG(gross_amount)",
        ]
        return [query for query in candidates if query.casefold() in haystack]

    @staticmethod
    def _extract_urn(value: Any, fallback: str) -> str:
        serialized = json.dumps(value, default=str)
        start = serialized.find("urn:li:")
        if start >= 0:
            end_candidates = [
                position
                for position in (serialized.find('"', start), serialized.find("\\n", start))
                if position > start
            ]
            end = min(end_candidates) if end_candidates else len(serialized)
            return serialized[start:end]
        return f"urn:li:document:{fallback}"

    @staticmethod
    def _require_successful_mutation(label: str, value: Any) -> None:
        if not isinstance(value, dict) or value.get("success") is not True:
            raise DataHubContextError(f"DataHub MCP {label} mutation was not successful")

    def _load_document_state(self) -> dict[str, Any]:
        path = self.settings.repairpilot_runtime_dir / "datahub-documents.json"
        if not path.exists():
            return {"incidents": {}}
        try:
            value = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            raise DataHubContextError("DataHub document state is unreadable") from exc
        if not isinstance(value, dict) or not isinstance(value.get("incidents", {}), dict):
            raise DataHubContextError("DataHub document state is invalid")
        return value

    def _save_document_state(self, value: dict[str, Any]) -> None:
        path = self.settings.repairpilot_runtime_dir / "datahub-documents.json"
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        temporary.replace(path)
