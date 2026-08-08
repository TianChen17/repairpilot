# RepairPilot Quality Report

- Final verification: **2026-08-08 09:42 UTC**
- Verified implementation commit: `9898e8d51f6f481900a02bc60516bf454b25779c`
- Release policy: **0 P0 · 0 P1 · 0 judge-path P2 · 0 known flaky tests**

A gate is PASS only when its command and resulting artifact were checked against
the deployed release candidate. Q7 is intentionally separated from the entrant's
identity-bound YouTube and Devpost actions.

| Gate | Status | Verified result |
|---|---|---|
| Q0 Environment and credentials | **PASS** | Ubuntu 24.04 ARM64; Docker and disk preflight; real GitHub PAT auth; real DeepSeek V4 Flash calls; encrypted production credential |
| Q1 Data authenticity | **PASS** | 1,200 Postgres rows; baseline dbt build; native DataHub schema, Owner, Domain, Tags, Queries, Assertions, Documents, and field lineage |
| Q2 Safety policy | **PASS** | 27 tests; 83.37% coverage; fail-closed policy, injection/path/SQL rejection, approval and run-start rate-limit tests |
| Q3 Repair correctness | **PASS** | Original failure reproduced; four-file repair; 14 tests and zero failures; Patch SHA verified |
| Q4 Repeatability | **PASS** | Three consecutive Live runs in 33s, 30s, and 31s; stable patch and Runbook; clean reset |
| Q5 Public deployment | **PASS** | Both HTTPS services; Reader journey; 1920×1080 and 1440×900 browser QA; no console/page errors |
| Q6 Video | **PASS** | 158.000s; 34 shots; zero black/flash frames; -16.00 LUFS; 46 semantic anchors; 97/100 manual review |
| Q7 Submission package | **READY — USER ACTIONS ONLY** | Public Apache-2.0 repo, final MP4, four Gallery images, Devpost copy, test instructions, and checksums prepared |

## Q0 — Environment and credentials

- The host is Ubuntu 24.04 on `aarch64`. ARM64 Docker, Compose, available disk,
  seed count, private-port bindings, and tracked-secret scans pass
  `scripts/preflight.sh`.
- The exact variable `GITHUB_PAT_TianChen_17` authenticated as `TianChen17` and
  has the repository/workflow scopes required for publication. Its value was
  never printed, logged, committed, captured, or placed in a remote URL.
- `DEEPSEEK_API_KEY` authenticated with `deepseek-v4-flash`; final Live runs each
  exercised the real structured repair call. Production loads the key through
  a systemd encrypted credential unavailable to the frontend, dbt, MCP, logs,
  screenshots, and video.

## Q1 — Real execution and synthetic boundary

- `warehouse/seeds/raw_orders.csv` contains exactly 1,200 deterministic,
  privacy-safe rows. The Northstar Commerce identity, Owner, dashboard, and
  stored usage queries are synthetic and labeled as such.
- PostgreSQL, dbt models, build artifacts, DataHub OSS, official DataHub MCP
  reads/mutations, DeepSeek inference, Git operations, GitHub PR, and DataHub
  write-back execute for real.
- MCP supplies schema, Owner, Domain, Tags, quality, stored queries, and lineage;
  judge-facing context is not a hard-coded substitute for MCP results.
- dbt ingestion includes `git_info.url_subdir: warehouse`. The DataHub source
  links for `stg_orders.sql` and `int_order_revenue.sql` both return HTTP 200.
- A real per-run Incident body and the shared Runbook body are visible in native
  DataHub pages; the final video no longer stops at the Documents folder.

## Q2 — Authority and safety

- Policy `2026-08-07.1` alone scores the canonical change `HIGH · 100/100` and
  returns `BLOCK`; the LLM cannot change risk, publish, or bypass approval.
- Missing DataHub context, failed dbt validation, rejected approval, unexpected
  model output, path traversal, arbitrary SQL/shell, and out-of-scope files fail
  closed.
- The public service allows one execution at a time and rate-limits only Agent
  run starts. Reset and Approval do not consume expensive-run quota. Client IP
  forwarding is trusted only from the loopback Caddy proxy.
- A regression found that all POST actions previously shared one hourly bucket,
  causing the third quality run to receive 429 after earlier capture traffic.
  Two tests reproduced the defect before the fix; both pass after route-scoped,
  per-judge rate limiting. The original three-run workflow then passed.
- Final suite: **27 passed**, **83.37% coverage**, one documented upstream
  TestClient deprecation warning, and zero known flaky tests.

## Q3 — Repair proof

- RepairPilot first applies the unsafe rename and must observe the downstream
  dbt failure.
- The bounded repair preserves `gross_amount`, exposes `gross_revenue`, migrates
  the controlled consumer, adds a real `not_null` schema test, and writes a
  migration note.
- `dbt build --select stg_orders+` passes **14 tests with zero failures** inside
  a detached Git worktree and per-run Postgres schemas.
- The patch applies to a clean baseline, changes exactly four files, and matches
  the Evidence Receipt and public draft PR. Verified SHA-256:

```text
588e2b4ba90abf9c65a1c53da7913c25d531ccbe9304bc98a82577ed877f13e7
```

## Q4 — Three consecutive Live runs

The final post-rework batch ran without terminal intervention:

| Run | Duration | State | Patch SHA | Knowledge |
|---:|---:|---|---|---|
| 1 | 33s | LEARNED | `588e2b4b…` | unique Incident · shared Runbook |
| 2 | 30s | LEARNED | `588e2b4b…` | unique Incident · shared Runbook |
| 3 | 31s | LEARNED | `588e2b4b…` | unique Incident · shared Runbook |

The final reset reports `schemas=0 worktrees=0`. The machine-readable records
are in `examples/final-live-e2e-summary.jsonl`.

## Q5 — Public judge journey

- RepairPilot: <https://repairpilot.145-241-207-154.sslip.io>
- DataHub: <https://catalog.145-241-207-154.sslip.io>
- A fresh 1440×900 session verified the ready state and judge controls. A fresh
  1920×1080 session completed Run → Block → Go to approval → Approve → DataHub
  write-back, with no browser console or page errors.
- The ready page exposes `Synthetic business data · Real execution`, a visible
  three-step route, `LIVE SERVICE`, a labeled Reset control, progress/ETA,
  approval jump, and DataHub Reader instructions.
- RepairPilot measured approximately 0.04 seconds to first byte from the host.
  Caddy and the API/DataHub systemd units are active; PostgreSQL, GMS, MCP, and
  Docker data services remain loopback-only.

## Q6 — Final video

The withdrawn 175-second version is archived and is not a submission asset. The
final judge cut is composed in Remotion 4.0.506 from native RepairPilot,
DataHub, GitHub, and dbt evidence, with Edge TTS word timings and one H.264 video
encode. Audio was normalized separately and remuxed with `-c:v copy`.

Objective results from `video/scripts/validate_video.sh`:

| Metric | Result |
|---|---:|
| Duration / format | 158.000s · 1920×1080 · 30fps · H.264/AAC · BT.709 |
| Loudness / true peak | -16.00 LUFS · -1.29 dBTP |
| Black frames | 0 |
| Single-frame luminance dips / spikes | 0 / 0 |
| Narration/script | 296 words · 10 chapters |
| Caption phrases | 48 · exact word boundaries · ≤7 words |
| Semantic synchronization | 46 anchors · maximum error 117ms |
| OCR evidence | 7/7 terms found |
| Manual review | 34/34 shots · PASS |

Manual content score:

| Criterion | Score |
|---|---:|
| Problem clarity in first 15 seconds | 15/15 |
| DataHub usage evidence | 20/20 |
| Agent takes real action | 20/20 |
| Repair and verification credibility | 20/20 |
| UI and caption readability | 9/10 |
| Pacing and narration | 8/10 |
| Compliance and disclosure | 5/5 |
| **Total** | **97/100** |

Every full-frame fade was removed. Static 3840×2160 PNG sources replaced JPEG
intermediates and Ken Burns scaling. Captions moved to the lower safe area, and
the DataHub Incident, Assertion, Owner, Tags, Queries, Lineage, and Runbook were
reviewed at final 1080p resolution.

## Q7 — Submission readiness

- Public source: <https://github.com/TianChen17/repairpilot>
- Draft repair PR: <https://github.com/TianChen17/repairpilot/pull/1>
- Apache License 2.0 is present at the repository root.
- README, Judge Guide, Devpost copy, Real/Synthetic disclosure, architecture,
  security boundary, local setup, tests, and sample outputs are consistent.
- The final delivery folder contains one unambiguous submission MP4, cover,
  exactly four Gallery images, copy, quality evidence, and SHA-256 checksums.
- The remaining YouTube upload, entrant declarations, and Devpost Submit require
  the entrant's own identity and are intentionally not automated.

## Closed defect ledger

| Severity | Finding | Root cause | Verified resolution |
|---|---|---|---|
| P1 | Reset left run schemas | cleanup predicate excluded valid suffixes | strict schema matching, integration test, three-run clean reset |
| P2 | UI status copy became stale | notice updated only at start | state-driven copy and two-resolution browser journey |
| P2 | Third regression run received 429 | all POST actions and proxied judges shared quota | run-start-only, trusted-proxy client buckets; red/green tests and rerun |
| P2/Q6 | Black flashes at shot cuts | every shot faded from opacity zero | no full-frame opacity transitions; 4,740-frame luma audit |
| P2/Q6 | DataHub UI softened | scaling, JPEG intermediates, and double encode | 2× PNG sources, static crops, CRF 14 single encode |
| P2/Q6 | Narration crossed chapters | visual and audio timing were independent | one canonical timeline; 46-anchor audit |
| P2/Q6 | Write-back proof showed only folder | capture did not open Incident | real Incident and Runbook bodies in final cut |
| P2/Q6 | Captions reduced evidence space | subtitle block sat too high | 34px captions at 52px bottom safe area |

Final open defects: **P0 0 · P1 0 · judge-path P2 0 · flaky 0**.

## Reproduction commands

```bash
./scripts/quality-gates.sh
REPAIRPILOT_E2E_RUNS=3 ./scripts/live-e2e.sh
./video/scripts/validate_video.sh video/output/repairpilot-demo.mp4
./scripts/submission-preflight.sh
```
