from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class IncidentState(StrEnum):
    DETECTED = "DETECTED"
    CONTEXT_COLLECTED = "CONTEXT_COLLECTED"
    POLICY_EVALUATED = "POLICY_EVALUATED"
    BLOCKED = "BLOCKED"
    REPAIR_PROPOSED = "REPAIR_PROPOSED"
    VALIDATING = "VALIDATING"
    VERIFIED = "VERIFIED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    PUBLISHED = "PUBLISHED"
    LEARNED = "LEARNED"
    CONTEXT_UNAVAILABLE = "CONTEXT_UNAVAILABLE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class RiskLevel(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RiskAction(StrEnum):
    ALLOW = "ALLOW"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    BLOCK = "BLOCK"


class EvidenceItem(BaseModel):
    source: Literal["datahub_mcp", "git", "dbt", "policy", "approval", "github"]
    tool: str
    summary: str
    payload: dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime = Field(default_factory=utc_now)


class ContextSnapshot(BaseModel):
    asset_urn: str
    column_urn: str
    owners: list[str]
    tags: list[str]
    domain: str | None = None
    downstream_assets: list[str]
    downstream_dashboards: list[str]
    queries: list[str]
    assertions: list[str]
    schema_fields: list[str]
    evidence: list[EvidenceItem]


class RiskAssessment(BaseModel):
    policy_version: str = "2026-08-07.1"
    score: int = Field(ge=0, le=100)
    level: RiskLevel
    action: RiskAction
    matched_rules: list[str]
    rationale: str


class RepairOperation(BaseModel):
    operation: Literal["compatibility_alias", "downstream_migration", "schema_test"]
    target: str
    rationale: str


class RepairProposal(BaseModel):
    root_cause: str
    summary: str
    operations: list[RepairOperation]
    migration_note: str
    pr_title: str
    pr_body: str
    confidence: float = Field(ge=0, le=1)


class CommandResult(BaseModel):
    command: str
    return_code: int
    duration_ms: int
    stdout_tail: str


class ValidationReceipt(BaseModel):
    breaking_change_reproduced: bool
    repair_verified: bool
    invocation_id: str
    command_results: list[CommandResult]
    tests_passed: int
    tests_failed: int
    patch_sha256: str
    patch_path: str


class ApprovalRecord(BaseModel):
    decision: Literal["approve", "reject"]
    actor: str
    decided_at: datetime = Field(default_factory=utc_now)


class WritebackReceipt(BaseModel):
    incident_document_urn: str
    runbook_document_urn: str
    updated_entity_urns: list[str]
    assertion_urns: list[str]
    completed_at: datetime = Field(default_factory=utc_now)


class IncidentEvent(BaseModel):
    sequence: int
    state: IncidentState
    message: str
    timestamp: datetime = Field(default_factory=utc_now)


class IncidentRecord(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    run_id: str
    scenario: Literal["breaking-column-rename"] = "breaking-column-rename"
    mode: Literal["live", "replay"] = "live"
    state: IncidentState = IncidentState.DETECTED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    context: ContextSnapshot | None = None
    risk: RiskAssessment | None = None
    repair: RepairProposal | None = None
    validation: ValidationReceipt | None = None
    approval: ApprovalRecord | None = None
    writeback: WritebackReceipt | None = None
    evidence: list[EvidenceItem] = Field(default_factory=list)
    events: list[IncidentEvent] = Field(default_factory=list)
    error: str | None = None


class IncidentCreateRequest(BaseModel):
    scenario: Literal["breaking-column-rename"] = "breaking-column-rename"
    execution_mode: Literal["live", "replay"] = "live"


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    actor: str = Field(default="Revenue Analytics Owner", min_length=2, max_length=80)


class EvidenceReceipt(BaseModel):
    run_id: str
    mode: Literal["live", "replay"]
    generated_at: datetime
    state: IncidentState
    datahub_urns: list[str]
    policy_version: str
    risk_score: int
    risk_action: RiskAction
    matched_rules: list[str]
    model: str
    patch_sha256: str
    dbt_invocation_id: str
    approval: ApprovalRecord | None
    pull_request_url: str | None
    writeback_urns: list[str]
