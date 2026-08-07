import json

from openai import AsyncOpenAI

from .config import Settings
from .models import ContextSnapshot, RepairProposal, RiskAssessment


class RepairGenerationError(RuntimeError):
    pass


class DeepSeekRepairGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(
        self, context: ContextSnapshot, risk: RiskAssessment, *, replay: bool = False
    ) -> RepairProposal:
        if replay:
            return self.replay_proposal()
        if not self.settings.deepseek_api_key:
            raise RepairGenerationError("DeepSeek credential is unavailable in LIVE mode")

        client = AsyncOpenAI(
            api_key=self.settings.deepseek_api_key,
            base_url=self.settings.deepseek_base_url,
            timeout=45,
            max_retries=1,
        )
        prompt = self._prompt(context, risk)
        response = await client.chat.completions.create(
            model=self.settings.deepseek_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior analytics engineer. Produce a bounded repair "
                        "proposal only. You cannot change risk, approval, or execution "
                        "policy. Never include secrets."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=1400,
            extra_body={"thinking": {"type": "disabled"}},
        )
        content = response.choices[0].message.content
        if not content:
            raise RepairGenerationError("DeepSeek returned no final repair content")
        try:
            proposal = RepairProposal.model_validate(json.loads(content))
        except (json.JSONDecodeError, ValueError) as exc:
            raise RepairGenerationError("DeepSeek returned an invalid repair contract") from exc
        self._validate(proposal)
        return proposal

    @staticmethod
    def _prompt(context: ContextSnapshot, risk: RiskAssessment) -> str:
        contract = {
            "root_cause": "string",
            "summary": "string",
            "operations": [
                {
                    "operation": "compatibility_alias|downstream_migration|schema_test",
                    "target": "allowlisted relative dbt file",
                    "rationale": "string",
                }
            ],
            "migration_note": "markdown string",
            "pr_title": "string",
            "pr_body": "markdown string",
            "confidence": "number 0..1",
        }
        context_payload = {
            "asset_urn": context.asset_urn,
            "column_urn": context.column_urn,
            "owners": context.owners,
            "tags": context.tags,
            "downstream_assets": context.downstream_assets,
            "downstream_dashboards": context.downstream_dashboards,
            "queries": context.queries,
            "assertions": context.assertions,
            "risk_score": risk.score,
            "risk_action": risk.action,
            "matched_rules": risk.matched_rules,
        }
        return (
            "A proposed dbt change renames gross_amount to gross_revenue and breaks existing "
            "downstream references. Generate JSON matching this exact contract:\n"
            f"{json.dumps(contract)}\n"
            "Include exactly these three operations: compatibility_alias targeting "
            "warehouse/models/staging/stg_orders.sql, downstream_migration targeting "
            "warehouse/models/intermediate/int_order_revenue.sql, and schema_test targeting "
            "warehouse/models/staging/schema.yml. Do not propose DROP, DELETE, shell commands, "
            "or files outside warehouse/. Context from DataHub MCP follows:\n"
            f"{json.dumps(context_payload, default=str)}"
        )

    @staticmethod
    def _validate(proposal: RepairProposal) -> None:
        required = {"compatibility_alias", "downstream_migration", "schema_test"}
        operations = {operation.operation for operation in proposal.operations}
        if operations != required:
            raise RepairGenerationError(
                "Repair proposal does not contain the required safe operations"
            )
        allowed = {
            "warehouse/models/staging/stg_orders.sql",
            "warehouse/models/intermediate/int_order_revenue.sql",
            "warehouse/models/staging/schema.yml",
        }
        if any(operation.target not in allowed for operation in proposal.operations):
            raise RepairGenerationError("Repair proposal targets a path outside the allowlist")
        unsafe = (
            "drop database",
            "drop schema",
            "delete from",
            "truncate ",
            "../",
            "/etc/",
            "ignore previous",
            "ignore all previous",
            "bypass approval",
            "auto-approve",
            "api key",
            "password",
            "secret",
            "access token",
            "curl ",
        )
        serialized = proposal.model_dump_json().casefold()
        if any(token in serialized for token in unsafe):
            raise RepairGenerationError("Repair proposal contains an unsafe operation")

    @staticmethod
    def replay_proposal() -> RepairProposal:
        return RepairProposal.model_validate(
            {
                "root_cause": "A breaking rename removed gross_amount before consumers migrated.",
                "summary": (
                    "Keep a compatibility alias, migrate the fact model, and add a contract test."
                ),
                "operations": [
                    {
                        "operation": "compatibility_alias",
                        "target": "warehouse/models/staging/stg_orders.sql",
                        "rationale": (
                            "Preserve the old contract while exposing the canonical field."
                        ),
                    },
                    {
                        "operation": "downstream_migration",
                        "target": "warehouse/models/intermediate/int_order_revenue.sql",
                        "rationale": "Move the controlled downstream model to gross_revenue.",
                    },
                    {
                        "operation": "schema_test",
                        "target": "warehouse/models/staging/schema.yml",
                        "rationale": "Prevent null canonical revenue values from shipping.",
                    },
                ],
                "migration_note": (
                    "`gross_revenue` is canonical. `gross_amount` remains as a compatibility "
                    "alias for one migration window and will be removed after consumers migrate."
                ),
                "pr_title": "fix(dbt): safely migrate gross_amount to gross_revenue",
                "pr_body": (
                    "Blocks the breaking rename, preserves compatibility, and proves the repair."
                ),
                "confidence": 0.96,
            }
        )
