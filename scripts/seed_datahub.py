#!/usr/bin/env python3
"""Create the synthetic governance and usage context used by the live demo."""

from __future__ import annotations

import hashlib
import time

from datahub.emitter.mce_builder import (
    make_dashboard_urn,
    make_dataset_urn,
    make_domain_urn,
    make_tag_urn,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata import schema_classes as models
from datahub.metadata.urns import CorpGroupUrn, QueryUrn

GMS = "http://127.0.0.1:8080"
ACTOR = "urn:li:corpuser:datahub"
GROUP_URN = CorpGroupUrn("revenue-analytics").urn()
DOMAIN_URN = make_domain_urn("finance-analytics")
STG_URN = make_dataset_urn("dbt", "repairpilot.analytics_staging.stg_orders", "PROD")
INT_URN = make_dataset_urn("dbt", "repairpilot.analytics_intermediate.int_order_revenue", "PROD")
FACT_URN = make_dataset_urn("dbt", "repairpilot.analytics_marts.fct_daily_revenue", "PROD")
MART_URN = make_dataset_urn("dbt", "repairpilot.analytics_marts.mart_executive_revenue", "PROD")
DASHBOARD_URN = make_dashboard_urn("repairpilot_demo", "executive-revenue-pulse")


def emit(emitter: DatahubRestEmitter, urn: str, aspect: object) -> None:
    emitter.emit_mcp(
        MetadataChangeProposalWrapper(entityUrn=urn, aspect=aspect),
        async_flag=False,
    )


def query_urn(statement: str) -> str:
    digest = hashlib.sha256(statement.encode()).hexdigest()
    return QueryUrn(digest).urn()


def main() -> None:
    now_ms = int(time.time() * 1000)
    audit = models.AuditStampClass(time=now_ms, actor=ACTOR)
    emitter = DatahubRestEmitter(GMS)

    emit(
        emitter,
        GROUP_URN,
        models.CorpGroupInfoClass(
            admins=[],
            members=[],
            groups=[],
            displayName="Revenue Analytics",
            description=("Synthetic owner group for the Northstar Commerce RepairPilot demo."),
        ),
    )
    emit(
        emitter,
        DOMAIN_URN,
        models.DomainPropertiesClass(
            name="Finance Analytics",
            description=("Synthetic finance domain used only by the RepairPilot demonstration."),
        ),
    )

    tag_definitions = {
        "Tier1": ("Critical executive reporting asset.", "EF4444"),
        "FinancialMetric": ("Contains a synthetic financial measure.", "3B82F6"),
        "SLA-1h": ("Synthetic one-hour data freshness expectation.", "F59E0B"),
        "SyntheticDemo": ("Generated demonstration metadata; no production data.", "8B5CF6"),
        "RepairPilotVerified": ("Repair verified by the RepairPilot safety loop.", "22C55E"),
    }
    for name, (description, color) in tag_definitions.items():
        emit(
            emitter,
            make_tag_urn(name),
            models.TagPropertiesClass(name=name, description=description, colorHex=color),
        )

    ownership = models.OwnershipClass(
        owners=[
            models.OwnerClass(
                owner=GROUP_URN,
                type=models.OwnershipTypeClass.DATAOWNER,
            )
        ]
    )
    governed_tags = models.GlobalTagsClass(
        tags=[
            models.TagAssociationClass(tag=make_tag_urn(name))
            for name in ("Tier1", "FinancialMetric", "SLA-1h", "SyntheticDemo")
        ]
    )
    domain = models.DomainsClass(domains=[DOMAIN_URN])
    for urn in (STG_URN, INT_URN, FACT_URN, MART_URN):
        emit(emitter, urn, ownership)
        emit(emitter, urn, governed_tags)
        emit(emitter, urn, domain)

    emit(
        emitter,
        DASHBOARD_URN,
        models.DashboardInfoClass(
            title="Executive Revenue Pulse",
            description=(
                "Synthetic dashboard metadata for the RepairPilot demo. "
                "No Looker or other BI runtime is claimed or required."
            ),
            lastModified=models.ChangeAuditStampsClass(
                created=audit,
                lastModified=audit,
            ),
            customProperties={
                "data_classification": "synthetic",
                "runtime": "metadata-only demo adapter",
                "source_project": "RepairPilot",
            },
            datasets=[MART_URN],
            dashboardUrl=("https://repairpilot.145-241-207-154.sslip.io/#synthetic-dashboard"),
        ),
    )
    emit(emitter, DASHBOARD_URN, models.StatusClass(removed=False))
    emit(emitter, DASHBOARD_URN, ownership)
    emit(emitter, DASHBOARD_URN, governed_tags)
    emit(emitter, DASHBOARD_URN, domain)

    statements = [
        (
            "Revenue by region",
            "SELECT region, SUM(gross_amount) FROM "
            "repairpilot.analytics_staging.stg_orders GROUP BY region",
        ),
        (
            "Daily gross revenue",
            "SELECT ordered_at::date, SUM(gross_amount) FROM "
            "repairpilot.analytics_staging.stg_orders GROUP BY 1",
        ),
        (
            "Average order value",
            "SELECT currency, AVG(gross_amount) FROM "
            "repairpilot.analytics_staging.stg_orders GROUP BY currency",
        ),
    ]
    for name, statement in statements:
        urn = query_urn(statement)
        emit(
            emitter,
            urn,
            models.QueryPropertiesClass(
                statement=models.QueryStatementClass(
                    value=statement,
                    language=models.QueryLanguageClass.SQL,
                ),
                source=models.QuerySourceClass.MANUAL,
                name=name,
                description=(
                    "Stored synthetic example query used to demonstrate DataHub usage context."
                ),
                created=audit,
                lastModified=audit,
                origin=STG_URN,
                customProperties={"data_classification": "synthetic"},
            ),
        )
        emit(
            emitter,
            urn,
            models.QuerySubjectsClass(subjects=[models.QuerySubjectClass(entity=STG_URN)]),
        )
        emit(emitter, urn, models.StatusClass(removed=False))

    emitter.flush()
    print("synthetic_context=seeded")
    print(f"governed_assets={4}")
    print(f"stored_queries={len(statements)}")
    print("dashboard_metadata=synthetic")


if __name__ == "__main__":
    main()
