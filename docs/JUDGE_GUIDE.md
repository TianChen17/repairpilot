# Judge Guide

The shortest path takes about 60–90 seconds and requires no API key, signup, or
payment.

## Live path

1. Open <https://repairpilot.145-241-207-154.sslip.io>. The banner explicitly
   distinguishes synthetic business data from real execution.
2. Click **Run live incident**. The progress line shows the active phase and
   estimated time remaining.
3. Watch the trace reach **BLOCKED**. Confirm that DataHub MCP found the Revenue
   Analytics owner, governed tags, three dbt models, one dashboard, three usage
   queries, and passing quality health.
4. Wait for **AWAITING APPROVAL**, then use the visible **Go to approval** link.
   The page shows the expected failing build, passing repaired build, 14 tests,
   two Git commits, and Patch SHA.
5. Click **Approve repair**. Approval is unavailable until executable proof
   exists; **Reject** leaves the change blocked and creates no PR.
6. Inspect the Incident, Assertion, Runbook, and GitHub PR links shown in the
   final panel. Download the Git patch directly from the proof panel.
7. Click **New run / Reset** before trying another run.

The service permits only one run at a time. If another judge is testing, the UI
shows a plain-language message: wait briefly or use the clearly labeled Replay.

## Inspect DataHub

Use **Inspect DataHub** in RepairPilot for these instructions and a direct
`stg_orders` link, or open <https://catalog.145-241-207-154.sslip.io> and use:

```text
username: judge@repairpilot.demo
password: RepairPilot-Judge-2026!
role: Reader
```

On first login, close the **Welcome Tour**. After the first search, also dismiss
the **Narrow your search** tip if it appears. These are standard DataHub browser
onboarding dialogs.

Search for `stg_orders`, choose the dbt model—not the Postgres relation—and
inspect:

- column `gross_amount` and downstream lineage;
- Owner `Revenue Analytics` and Domain `Finance Analytics`;
- Tags `Tier1`, `FinancialMetric`, `SLA-1h`, and `SyntheticDemo`;
- health/Assertions;
- the `Executive Revenue Pulse` dashboard;
- RepairPilot Documents and `RepairPilotVerified` tag after an approved run.
- **View in GitHub**, which opens the real file under `warehouse/models/`.

The dashboard and stored queries are demonstration metadata and are labeled as
such. DataHub itself, its graph, MCP reads/mutations, and all written entities are
real.

## Inspect outputs without running

- [Canonical repair PR](https://github.com/TianChen17/repairpilot/pull/1)
- [Verified sample outputs](../examples/)
- [Quality report](QUALITY_REPORT.md)
- [Security model](SECURITY.md)

## Replay fallback

If an upstream model provider is temporarily unavailable, reset and click
**Replay evidence**. The UI always labels this `REPLAY`; it never presents
captured MCP/model content as a live response. The dbt failure and repair build
remain executable.
