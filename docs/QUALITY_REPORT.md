# RepairPilot Quality Report

- Last verified: **2026-08-08 01:08 UTC**
- Deployed product commit: `7ef3e29ea19d1513130c99a4c16fb70d78e4876e`
- Canonical repair branch commit: `d86d6a43dfe807c9a6c330854236644fa36816dd`

Release policy is zero P0, zero P1, zero judge-path P2, and zero known flaky
tests. A gate is marked PASS only when its command and resulting artifact were
verified against the deployed build.

| Gate | Status | Primary evidence |
|---|---|---|
| Q0 Environment and credentials | PASS | ARM64 preflight; real PAT auth; real DeepSeek V4 Flash response; encrypted systemd credential |
| Q1 Data authenticity | PASS | 1,200 Postgres rows; baseline dbt build; DataHub UI/MCP owner, tags, lineage, assertions, and queries |
| Q2 Safety policy | PASS | policy, API, injection, path, environment-isolation, reject, and fail-closed tests |
| Q3 Repair correctness | PASS | original failure reproduced; 14 tests pass; exact four-file patch and SHA-256 |
| Q4 Repeatability | PASS | final three consecutive Live runs in 33s, 31s, and 32s; clean reset verified |
| Q5 Public deployment | PASS | both HTTPS URLs; Reader access; loopback data services; enabled systemd units |
| Q6 Video | PASS | 175.000s; 1080p30; H.264/AAC; BT.709/yuv420p; -15.99 LUFS; -1.30 dBTP; zero black segments; score 95/100 |
| Q7 Submission | READY EXCEPT USER ACTIONS | public repo, license, examples, judge guide, and Devpost copy ready; YouTube URL and final Submit remain |

## Q0 — Environment and credentials

- Host is Ubuntu 24.04 on `aarch64`; the Docker ARM64 smoke container passed.
- Docker Engine 29.1.3 and Compose 2.40.3 are active.
- The approved cache cleanup was completed before installation. The installed
  stack retains more than the automated 8 GB free-space safety threshold.
- `GITHUB_PAT_TianChen_17` authenticated as `TianChen17`; repository and
  workflow permissions were verified without printing the value.
- `DEEPSEEK_API_KEY` authenticated against the live API and
  `deepseek-v4-flash` returned the exact smoke response `REPAIRPILOT_OK`.
- Production reads the model key from a systemd encrypted credential. The
  frontend, dbt subprocess, MCP subprocess, logs, repository, screenshots, and
  video receive no model or GitHub secret.
- `scripts/preflight.sh` checks architecture, disk, Docker, the seed count,
  tracked secret patterns, repository URL, and loopback-only private ports.

## Q1 — Data authenticity

- `warehouse/seeds/raw_orders.csv` contains exactly 1,200 deterministic rows.
- Baseline `dbt build` passes with five project nodes and thirteen tests.
- The verified repair artifact contains four successful model/seed results and
  fourteen passing tests.
- DataHub OSS contains the real dbt/Postgres metadata, `Revenue Analytics`
  ownership, `Finance Analytics` Domain, governance Tags, field schema,
  lineage, three stored Query entities, and Assertion entities.
- The service uses one official MCP session for `search`, `get_entities`,
  `list_schema_fields`, `get_lineage`, and `get_dataset_queries`; the UI is
  populated from that response. MCP mutations write Tags and Documents.
- The dashboard, orders, and query text are explicitly marked synthetic. No
  Looker or Airflow runtime is claimed.

## Q2 — Safety decision

- Policy `2026-08-07.1` scores the canonical change HIGH/100 and returns
  `BLOCK` from code, not from the model.
- The model cannot mutate risk, approval, publication, command, or target path.
- Repair operations and file paths are exact allowlists; arbitrary SQL, shell,
  traversal, and prompt-injection terms are rejected.
- DataHub context failure and dbt failure terminate in blocked states.
- The rejection test ends in `REJECTED`, has no PR result, and performs no
  DataHub write-back.
- The public endpoint has a scenario allowlist, global execution lock, rate
  limit, and synchronous approval transition to prevent reset races.
- Current suite: **26 passed**, one upstream deprecation warning, **83.33%**
  Python coverage, zero known flaky tests.

## Q3 — Repair correctness

- The unsafe rename is applied first and must reproduce the downstream dbt
  failure.
- The repair preserves `gross_amount`, exposes `gross_revenue`, migrates the
  controlled consumer, adds a `not_null` test, and creates a migration note.
- `dbt build --select stg_orders+` passes with **14 tests and zero failures** in
  run-specific Postgres schemas.
- The generated patch applies to a clean baseline and contains exactly four
  files. Its verified SHA-256 is:

```text
588e2b4ba90abf9c65a1c53da7913c25d531ccbe9304bc98a82577ed877f13e7
```

- The Evidence Receipt, public draft PR, and `examples/repair.patch` agree.
- Both current checks on PR #1 pass in GitHub Actions.

## Q4 — Repeatability and completed rework

The first three-run audit found a real P1 cleanup defect: schemas such as
`rp_<run>_staging` were not matched by the original cleanup predicate. The
failure evidence was retained, the root cause was fixed with a strict schema
name regular expression and identifier-safe SQL, and an integration test plus
`verify_runtime_clean.py` were added. All old generated schemas were removed.

The complete workflow was then rerun three times with no terminal intervention.
This post-fix batch is the one referenced by the finished video:

| Run | Duration | State | Patch hash | Runbook |
|---:|---:|---|---|---|
| 1 | 30s | LEARNED | `588e2b4b…` | shared stable URN |
| 2 | 31s | LEARNED | `588e2b4b…` | shared stable URN |
| 3 | 28s | LEARNED | `588e2b4b…` | shared stable URN |

The final reset reports `schemas=0 worktrees=0`. Machine-readable evidence is
stored in `examples/live-e2e-summary.jsonl`.

After final video packaging and all downstream gates, the workflow was run three
more consecutive times in **33s, 31s, and 32s**. It again produced one stable
Patch SHA, the same Runbook URN, three unique Incident URNs, and a final clean
reset with `schemas=0 worktrees=0`. This final regression batch is stored in
`examples/final-live-e2e-summary.jsonl`.

## Q5 — Public deployment

- RepairPilot: <https://repairpilot.145-241-207-154.sslip.io>
- DataHub: <https://catalog.145-241-207-154.sslip.io>
- DataHub provides a dedicated read-only Judge account documented in the Judge
  Guide; no registration or paid API key is required.
- Caddy, RepairPilot API, DataHub Quickstart, and Docker are active; the three
  application services are enabled for restart.
- PostgreSQL, DataHub GMS, Kafka, Elasticsearch, MySQL, and MCP are not directly
  exposed publicly. Quickstart bindings are hardened to `127.0.0.1`.
- Reader permissions were verified in the actual DataHub browser session.
- Browser visual QA found and fixed one judge-path P2: the top status message
  previously stayed on the initial investigation copy after later state
  transitions. The final page now follows every state through `LEARNED`.

## Q6 — Video gate

The Remotion source, 175-second editorial contract, 50-shot plan, 62 timed
caption phrases, 14 recoverable AI voice segments, real UI captures, and
objective validator are versioned under `video/`.

Two pre-render defects were corrected:

1. An external TTS stream returned a zero-byte seventh segment. Generation was
   changed to atomic per-scene output, finite backoff, and rate-bound cache
   sidecars.
2. The first narration was longer than three minutes. It was edited from 466 to
   329 words and regenerated at a measured natural pace.
3. A draft render revealed that sequential audio packing let the late narration
   drift ahead of its scenes. All fourteen segments were then explicitly
   anchored to their visual beats; the final phrase ends at 172.310 seconds
   inside the closing shot.
4. The first complete frame pass was terminated during muxing by the interactive
   command supervisor. Rendering was moved into a scoped transient user service
   so process lifetime is independent of the terminal while remaining observable
   through the system journal.
5. The first objective probe found full-range `yuvj420p` output from the browser
   capture pipeline. Final packaging now explicitly converts full-range source
   frames to broadcast-safe `yuv420p` with BT.709 metadata before validation.
6. The first AAC package measured -15.99 LUFS but peaked at -0.95 dBTP, 0.05 dB
   over the strict ceiling. The normalization target was lowered to -1.3 dBTP
   to preserve codec headroom; the ceiling itself was not relaxed.

The final output passed `video/scripts/validate_video.sh`: **175.000 seconds**,
1920×1080, 30 fps, H.264/AAC, BT.709 with `yuv420p`, -15.99 LUFS, -1.30 dBTP,
62 timed caption phrases, and zero detected black segments. Twelve chronological
contact frames passed a second manual review for safe areas, captions, evidence
cropping, color meaning, and final URL readability. `3×` labels are present on
accelerated browser footage.

| Content criterion | Score |
|---|---:|
| Problem clarity in first 15 seconds | 15/15 |
| DataHub usage evidence | 19/20 |
| Agent takes real action | 20/20 |
| Repair and verification credibility | 19/20 |
| UI and caption readability | 9/10 |
| Pacing and narration | 9/10 |
| Compliance and disclosure | 4/5 |
| **Total** | **95/100** |

Machine-readable evidence is in `examples/video-quality-summary.json`; the
review contact sheet is `docs/images/video-contact-sheet.png`.

## Q7 — Submission readiness

- Public source: <https://github.com/TianChen17/repairpilot>
- Draft repair PR: <https://github.com/TianChen17/repairpilot/pull/1>
- Apache 2.0 `LICENSE` is at repository root and detected by GitHub.
- Repository About includes the description, demo URL, and topic tags.
- English README, Judge Guide, Security model, examples, video source, and
  Devpost copy are present.
- The official constraints are satisfied: public functioning project, public
  source and setup instructions, English description, under-three-minute real
  demo footage, and free judge access through judging.
- Remaining actions require the entrant's YouTube/Devpost identity: upload the
  delivered MP4 as Public, insert its URL, confirm eligibility/originality, and
  click Submit before **August 10, 2026 at 5:00 PM EDT**.

## Defect ledger

| Severity | Finding | Root cause | Resolution | Status |
|---|---|---|---|---|
| P1 | Reset left run-specific Postgres schemas | cleanup predicate rejected valid suffixes | strict regex, safe identifiers, integration test, full three-run rerun | CLOSED |
| P2 | UI notice remained on initial state | notice only updated at run start | state-to-copy mapping and browser regression check | CLOSED |
| P2/Q6 | TTS produced incomplete segment | external streaming interruption | atomic output, sidecars, bounded retry | CLOSED |
| P2/Q6 | Narration exceeded time limit | first script too dense for measured voice | concise rewrite and measured regeneration | CLOSED |
| P2/Q6 | Late narration preceded its visual evidence | audio segments were packed sequentially | explicit scene anchors and full rerender | CLOSED |
| P2/Q6 | Interactive render exited during muxing | render outlived command supervisor | isolated transient user service with journaled status | CLOSED |
| P2/Q6 | Final pixel format was `yuvj420p` | JPEG-backed browser frames retained full-range signaling | explicit range conversion and H.264 `yuv420p` re-encode | CLOSED |
| P2/Q6 | AAC true peak measured -0.95 dBTP | inter-sample codec overshoot consumed 0.05 dB headroom | lower target to -1.3 dBTP and revalidate against unchanged -1.0 ceiling | CLOSED |

Current release-blocking defects: **P0 0 · P1 0 · judge-path P2 0 · flaky 0**.
