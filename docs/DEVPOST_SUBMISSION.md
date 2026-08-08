# Devpost submission package

## Project name

RepairPilot — Block. Repair. Prove. Remember.

## Tagline

The DataHub-powered agent that blocks dangerous dbt changes, repairs them,
proves the fix, requests approval, and remembers the incident.

## Challenge

Agents That Do Real Work

## Project URL

<https://repairpilot.145-241-207-154.sslip.io>

## Public repository

<https://github.com/TianChen17/repairpilot>

## Demo video

`YOUTUBE_PUBLIC_URL_TO_BE_ADDED_AFTER_UPLOAD`

## Short description

RepairPilot turns a breaking dbt column rename into a governed repair workflow.
It reads live lineage, ownership, schema, usage, quality, and governance context
through DataHub MCP; deterministically blocks high-risk releases; asks DeepSeek
V4 Flash for a bounded repair; reproduces the failure and runs the repaired dbt
build in isolation; requires owner approval; publishes a reviewable GitHub PR;
and writes the Incident, Assertion, verification evidence, and Runbook back to
DataHub.

## Full description

### Inspiration

Most incident agents stop after explaining what broke and sending a message. A
data platform team still has to assess risk, edit production code, prove the
repair, collect authority, and preserve what was learned. RepairPilot closes that
gap while keeping the probabilistic model behind deterministic safety rails.

### What it does

The demo starts with Northstar Commerce renaming `gross_amount` to
`gross_revenue`. DataHub MCP reveals that the field is a Tier-1 governed
financial metric owned by Revenue Analytics, with three downstream dbt models,
an executive dashboard, three stored usage queries, and active quality checks.
A versioned policy scores it HIGH/100 and blocks the release.

DeepSeek V4 Flash proposes a compatibility alias, a controlled downstream
migration, and a new schema test. RepairPilot never executes generated shell or
SQL. It applies fixed, reviewed templates only to three allowlisted paths in a
detached Git worktree and temporary Postgres schema. The breaking build must
fail; the repaired `dbt build --select stg_orders+` must then pass. Only after 14
tests pass does the owner approval control unlock.

After approval, judges can inspect the real Git patch and GitHub PR. RepairPilot
also writes an Incident Document, reusable safe-rename Runbook,
`RepairPilotVerified` tag, and successful `gross_revenue` Assertion back to
DataHub so the next human or agent inherits the evidence.

### How we built it

- DataHub OSS 1.6.0 and official DataHub MCP Server 0.6.0
- PostgreSQL 16, dbt Core 1.10, and dbt-postgres
- FastAPI/Pydantic state machine and deterministic policy engine
- DeepSeek V4 Flash with a strict JSON repair contract
- React/Vite Repair Control Room
- Git worktrees, GitHub Actions, and a canonical review PR
- Caddy HTTPS and hardened systemd services on Ubuntu 24.04 ARM64
- Remotion for the under-three-minute product video

### Challenges

The hard part was proving that every impressive-looking step was real without
giving the model unsafe authority. DataHub MCP output had to be traced into the
UI, DataHub OSS version differences required fail-closed mutation validation,
and dbt had to demonstrate both the original failure and the repaired success in
clean isolation. Public hosting also required loopback-only data services,
credential isolation, a global run lock, and repeatable reset behavior.

### Accomplishments

- complete DataHub read/action/write-back loop rather than metadata chat;
- immutable receipt connecting DataHub URNs, policy version, Git commits, Patch
  SHA-256, dbt invocation, approval, PR, and writeback URNs;
- three consecutive Live runs with the same repair hash and idempotent Runbook;
- real failing and passing dbt builds with 14 tests;
- 83%+ Python coverage, public HTTPS deployment, and no known flaky tests;
- sample artifacts that judges can inspect without running the service.

### What we learned

Context makes an agent useful, but authority boundaries make it trustworthy.
DataHub is most valuable here not merely as a catalog lookup: it supplies the
governance facts that determine risk, then becomes the institutional memory for
the verified outcome.

### What's next

Add signed enterprise identity for approvals, policy-as-code packages per Domain,
automatic consumer migration windows, and optional Airflow/Dagster pause and
rerun adapters. The fixed demo templates would become repository-specific repair
skills reviewed by each data platform team.

## Data disclosure

All Northstar Commerce rows, people/groups, dashboard, and query metadata are
deterministic synthetic demonstration data. No personal, customer, or production
data is used. DataHub, dbt, Postgres, MCP, DeepSeek, Git, and GitHub executions
are real.

## Source/provenance disclosure

The project was newly created during the July 6–August 10, 2026 submission
period. It contains no pre-existing proprietary application code. It uses the
open-source packages and images declared in the repository and was developed
with AI coding assistance.

## Technologies

DataHub, DataHub MCP Server, dbt Core, dbt-postgres, PostgreSQL, FastAPI,
Pydantic, React, TypeScript, Vite, DeepSeek V4 Flash, Docker, Caddy, systemd,
GitHub Actions, Remotion.

## Final submission checklist

- [x] Working project URL is free to access through the judging period.
- [x] Public GitHub repository contains source and full setup instructions.
- [x] Apache 2.0 `LICENSE` is at repository root.
- [x] English text description and testing guide are complete.
- [x] Recommended sample outputs are present in `examples/`.
- [ ] Public YouTube video is under three minutes and linked here.
- [x] Repository About section contains description, website, and Apache-2.0
  license detection.
- [ ] User confirms eligibility, originality, ownership, and any team
  representation declarations.
- [ ] User optionally completes the feedback section for the feedback prize.
- [ ] User clicks Submit before **August 10, 2026 at 5:00 PM EDT** and confirms
  submission status.
