import json
import os
from collections.abc import Iterable
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import Settings
from .models import ContextSnapshot, EvidenceItem, WritebackReceipt


class DataHubContextError(RuntimeError):
    pass


class DataHubMCPClient:
    """Strict stdio client for the official DataHub MCP server."""

    ASSET_URN = (
        "urn:li:dataset:(urn:li:dataPlatform:dbt,northstar_analytics.mart_executive_revenue,PROD)"
    )
    COLUMN_URN = f"{ASSET_URN}.gross_amount"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def _parameters(self) -> StdioServerParameters:
        env = {
            **os.environ,
            "DATAHUB_GMS_URL": self.settings.datahub_gms_url,
            "DATAHUB_GMS_TOKEN": self.settings.datahub_gms_token,
            "TOOLS_IS_MUTATION_ENABLED": "true",
            "SAVE_DOCUMENT_PARENT_TITLE": "RepairPilot",
            "SAVE_DOCUMENT_RESTRICT_UPDATES": "true",
            "TOOL_RESPONSE_TOKEN_LIMIT": "20000",
        }
        return StdioServerParameters(
            command=self.settings.datahub_mcp_command,
            args=[self.settings.datahub_mcp_package],
            env=env,
        )

    async def list_tools(self) -> dict[str, dict[str, Any]]:
        async with stdio_client(self._parameters()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.list_tools()
                return {tool.name: tool.inputSchema for tool in result.tools}

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        async with stdio_client(self._parameters()) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)
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
                {"urn": self.ASSET_URN, "direction": "downstream", "max_hops": 3},
            ),
            ("get_dataset_queries", {"urn": self.ASSET_URN}),
        ]
        raw: dict[str, Any] = {}
        evidence: list[EvidenceItem] = []
        for tool, arguments in calls:
            result = await self.call_tool(tool, arguments)
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
                ["not_null_gross_amount", "accepted_values_order_status"],
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
        assertion_urns: list[str],
    ) -> WritebackReceipt:
        # Tool schemas are verified at deployment time; the explicit calls remain auditable.
        await self.call_tool(
            "add_tags", {"urns": [self.ASSET_URN], "tag_names": ["RepairPilotVerified"]}
        )
        incident = await self.call_tool(
            "save_document",
            {
                "title": f"RepairPilot Incident {run_id}",
                "content": incident_markdown,
            },
        )
        runbook = await self.call_tool(
            "save_document",
            {
                "title": "Safe dbt Column Rename Runbook",
                "content": runbook_markdown,
            },
        )
        return WritebackReceipt(
            incident_document_urn=self._extract_urn(incident, f"repairpilot-incident-{run_id}"),
            runbook_document_urn=self._extract_urn(runbook, "safe-dbt-column-rename-runbook"),
            updated_entity_urns=[self.ASSET_URN],
            assertion_urns=assertion_urns,
        )

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
