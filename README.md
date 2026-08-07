# RepairPilot

> **Block. Repair. Prove. Remember.**

RepairPilot is an incident-to-repair autopilot for dangerous data changes. It uses
DataHub's context graph and official MCP server to find the real blast radius of a
dbt schema change, applies deterministic release policy, generates a compatibility
repair with DeepSeek V4 Flash, proves the repair with a real dbt build, requests
owner approval, and writes the evidence and runbook back to DataHub.

This repository is a new entry for **Build with DataHub: The Agent Hackathon** in
the **Agents That Do Real Work** category.

## Status

Active implementation. The public judge guide and reproducible setup will remain
accurate at every tagged release. See [Quality Report](docs/QUALITY_REPORT.md).

## Safety model

- Deterministic code—not the LLM—owns risk classification and release authority.
- The original breaking change is never applied to the shared demo schema.
- Generated edits run only inside an isolated worktree and allowlisted dbt paths.
- DataHub or dbt failure is fail-closed.
- All business data is deterministic, synthetic, and free of personal information.

## Local development

```bash
cp .env.example .env
make bootstrap
make warehouse-build
make test
```

More detailed installation and judge instructions will be added as each quality
gate is completed.

## License

Apache License 2.0.

