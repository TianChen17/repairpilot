from dataclasses import dataclass

from .models import ContextSnapshot, RiskAction, RiskAssessment, RiskLevel


@dataclass(frozen=True)
class ChangeFacts:
    breaking_schema_change: bool
    documentation_only: bool = False
    additive_only: bool = False


def assess_risk(context: ContextSnapshot, change: ChangeFacts) -> RiskAssessment:
    """Evaluate deterministic release policy. The model has no input to this decision."""
    rules: list[str] = []
    score = 0

    if change.documentation_only or (change.additive_only and not context.downstream_assets):
        rules.append("SAFE_ADDITIVE_OR_DOCUMENTATION")
        return RiskAssessment(
            score=10,
            level=RiskLevel.LOW,
            action=RiskAction.ALLOW,
            matched_rules=rules,
            rationale="The change is additive or documentation-only with no governed blast radius.",
        )

    if change.breaking_schema_change:
        score += 55
        rules.append("BREAKING_SCHEMA_CHANGE")

    critical_tags = {tag.casefold() for tag in context.tags}
    if critical_tags & {"tier1", "critical", "sla-1h", "financialmetric"}:
        score += 25
        rules.append("GOVERNED_OR_TIER1_ASSET")

    downstream_count = len(context.downstream_assets) + len(context.downstream_dashboards)
    if downstream_count >= 3:
        score += 10
        rules.append("THREE_OR_MORE_DOWNSTREAM_ASSETS")
    elif downstream_count:
        score += 5
        rules.append("DOWNSTREAM_ASSET_IMPACT")

    if context.downstream_dashboards:
        score += 10
        rules.append("DASHBOARD_IMPACT")

    score = min(score, 100)
    if score >= 75:
        level, action = RiskLevel.HIGH, RiskAction.BLOCK
    elif score >= 40:
        level, action = RiskLevel.MEDIUM, RiskAction.REQUIRE_APPROVAL
    else:
        level, action = RiskLevel.LOW, RiskAction.ALLOW

    return RiskAssessment(
        score=score,
        level=level,
        action=action,
        matched_rules=rules,
        rationale=(
            f"Deterministic policy found {downstream_count} downstream assets and "
            f"matched {len(rules)} safety rules."
        ),
    )
