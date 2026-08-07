from app.models import RiskAction, RiskLevel
from app.policy import ChangeFacts, assess_risk


def test_high_risk_breaking_change_is_blocked(context):
    assessment = assess_risk(context, ChangeFacts(breaking_schema_change=True))

    assert assessment.level == RiskLevel.HIGH
    assert assessment.action == RiskAction.BLOCK
    assert assessment.score == 100
    assert "BREAKING_SCHEMA_CHANGE" in assessment.matched_rules
    assert "DASHBOARD_IMPACT" in assessment.matched_rules


def test_documentation_change_is_allowed(context):
    assessment = assess_risk(
        context.model_copy(update={"downstream_assets": [], "downstream_dashboards": []}),
        ChangeFacts(breaking_schema_change=False, documentation_only=True),
    )

    assert assessment.level == RiskLevel.LOW
    assert assessment.action == RiskAction.ALLOW


def test_medium_change_requires_approval(context):
    assessment = assess_risk(
        context.model_copy(
            update={
                "tags": [],
                "downstream_assets": ["one_model"],
                "downstream_dashboards": [],
            }
        ),
        ChangeFacts(breaking_schema_change=False),
    )

    assert assessment.level == RiskLevel.LOW
    assert assessment.action == RiskAction.ALLOW


def test_breaking_change_with_limited_impact_requires_approval(context):
    assessment = assess_risk(
        context.model_copy(
            update={
                "tags": [],
                "downstream_assets": ["one_model"],
                "downstream_dashboards": [],
            }
        ),
        ChangeFacts(breaking_schema_change=True),
    )

    assert assessment.level == RiskLevel.MEDIUM
    assert assessment.action == RiskAction.REQUIRE_APPROVAL
