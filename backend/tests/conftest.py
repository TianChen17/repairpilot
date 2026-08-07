from pathlib import Path

import pytest
from app.models import ContextSnapshot, EvidenceItem


@pytest.fixture
def context() -> ContextSnapshot:
    return ContextSnapshot(
        asset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,northstar.stg_orders,PROD)",
        column_urn="urn:li:schemaField:(stg_orders,gross_amount)",
        owners=["Revenue Analytics"],
        tags=["Tier1", "FinancialMetric", "SLA-1h"],
        domain="Finance Analytics",
        downstream_assets=[
            "int_order_revenue",
            "fct_daily_revenue",
            "mart_executive_revenue",
        ],
        downstream_dashboards=["Executive Revenue Pulse"],
        queries=["SELECT SUM(gross_amount) FROM mart_executive_revenue"],
        assertions=["not_null_gross_amount"],
        schema_fields=["order_id", "gross_amount"],
        evidence=[
            EvidenceItem(
                source="datahub_mcp",
                tool="get_lineage",
                summary="Verified test evidence",
            )
        ],
    )


@pytest.fixture
def runtime_dir(tmp_path: Path) -> Path:
    path = tmp_path / "runtime"
    path.mkdir()
    return path
