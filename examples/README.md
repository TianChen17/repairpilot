# Verified sample outputs

These files came from one **LIVE** RepairPilot run on the hosted service. They
are checked in so judges can inspect output quality without waiting for an agent
run.

| File | What it proves |
|---|---|
| `repair.patch` | Exact reviewable dbt compatibility repair |
| `repair-proposal.json` | Bounded DeepSeek V4 Flash output after policy block |
| `dbt-run-results.json` | Native dbt `run_results.json` from the repaired build |
| `dbt-command-results.json` | Expected failing build followed by passing build |
| `migration-note.md` | Consumer migration contract |
| `incident.md` | Root cause, policy result, and executable evidence |
| `runbook.md` | Reusable safe-column-rename procedure written to DataHub |
| `evidence-receipt.json` | Immutable hashes, commits, approval, PR, and DataHub URNs |
| `live-e2e-summary.jsonl` | Three consecutive Live runs with durations, stable patch hash, and idempotent Runbook |
| `final-live-e2e-summary.jsonl` | Final three-run regression after every downstream quality gate and video package |
| `video-quality-summary.json` | Final media metrics, loudness, peak, captions, black-frame result, and visual score |

Canonical review PR: <https://github.com/TianChen17/repairpilot/pull/1>

All business records and dashboard/query metadata are synthetic. The dbt runs,
DataHub reads and mutations, model request, Git commits, hashes, and approval
record are real.
