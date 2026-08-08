# YouTube and Devpost publishing package

## YouTube

**Title**

```text
RepairPilot — DataHub Incident-to-Repair Autopilot | Agents That Do Real Work
```

**Description**

```text
RepairPilot turns a dangerous dbt schema change into a governed repair workflow.

Live demo: https://repairpilot.145-241-207-154.sslip.io
Public source: https://github.com/TianChen17/repairpilot
Read-only DataHub: https://catalog.145-241-207-154.sslip.io

RepairPilot reads live lineage, ownership, governance, quality, and query context through DataHub MCP; deterministically blocks a high-risk release; asks DeepSeek V4 Flash for a bounded repair; reproduces the failure and proves the fix with a real isolated dbt build; requires owner approval; creates a reviewable GitHub PR; and writes an Incident, Assertion, verified Tag, and reusable Runbook back to DataHub.

00:00 One renamed field, four downstream failures
00:13 Block. Repair. Prove. Remember.
00:24 Live DataHub MCP context
00:43 Deterministic release block
00:56 Bounded AI repair
01:12 Real isolated dbt proof
01:30 Owner approval
01:41 GitHub pull request
01:54 DataHub write-back
02:15 Immutable Evidence Receipt
02:31 Safety and repeatability
02:45 RepairPilot

All Northstar Commerce business data, dashboard metadata, and query metadata are deterministic synthetic demonstration data. DataHub, MCP, Postgres, dbt, DeepSeek, Git, GitHub, approvals, and write-back execution are real.

Built for the DataHub Hackathon — Agents That Do Real Work.
```

**Tags**

```text
DataHub, DataHub MCP, AI Agent, dbt, Data Engineering, Data Governance, Incident Response, DeepSeek, PostgreSQL, FastAPI, React, Hackathon
```

**Thumbnail**

Use `docs/images/repairpilot-video-cover.png`. Keep the full 16:9 image and do
not add extra YouTube text over the URLs.

**Upload settings**

- Visibility: Public
- Audience: Not made for kids
- Language: English
- Captions: embedded/open captions are already present
- License: Standard YouTube License is fine; the source repository remains
  Apache-2.0
- Allow embedding: enabled
- Comments: optional

## Devpost gallery order

1. `docs/images/repairpilot-video-cover.png` — **RepairPilot: Block. Repair.
   Prove. Remember.**
2. `docs/images/repairpilot-control-room.png` — **A deterministic block,
   bounded AI repair, real dbt proof, approval, and DataHub write-back in one
   control room.**
3. `docs/images/datahub-writeback.png` — **The verified `gross_revenue`
   Assertion is written back into the real DataHub OSS catalog.**
4. `docs/images/github-repair-pr.png` — **The approved repair becomes a public,
   reviewable four-file GitHub draft PR.**

## Final entrant-only steps

1. Upload `repairpilot-demo.mp4` and choose Public visibility.
2. Confirm the public video opens in an incognito browser and remains below
   three minutes.
3. Replace `YOUTUBE_PUBLIC_URL_TO_BE_ADDED_AFTER_UPLOAD` in
   `docs/DEVPOST_SUBMISSION.md` with the public URL.
4. Paste the prepared fields from `docs/DEVPOST_SUBMISSION.md` into the existing
   Devpost draft and upload the four gallery images in the order above.
5. Confirm personal eligibility, team representation, originality, ownership,
   and any feedback-prize choices. These declarations cannot be made by the
   automation agent.
6. Click Submit before **August 10, 2026 at 5:00 PM EDT**, then verify the entry
   page shows a submitted status.
