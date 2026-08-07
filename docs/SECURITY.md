# Security model

RepairPilot is a public, synthetic demonstration of a production-oriented
control pattern. It is not a general-purpose code execution service.

## Trust boundaries

| Boundary | Trusted input | Untrusted input | Control |
|---|---|---|---|
| Browser → API | Fixed scenario and approval enum | request body, run ID, artifact name | Pydantic contracts, rate limit, allowlists |
| DataHub → policy | MCP evidence for known URNs | missing or malformed context | required-marker validation, fail closed |
| Model → executor | JSON repair intent | all generated prose and fields | exact operations/paths, destructive/injection filters |
| Executor → host | fixed dbt and Git argument arrays | model-selected target attempts | no shell, detached worktree, temporary schema |
| API → GitHub | configured canonical review URL | judge actions | no hosted token and no per-run repository mutation |
| API → secrets | systemd credential file | logs, child processes, browser | encrypted credential, minimal child environments |

## Release invariants

1. A high-risk change never transitions directly from policy evaluation to
   publication.
2. Approval is accepted only from `AWAITING_APPROVAL`.
3. That state is reachable only after the breaking build fails and the repaired
   build plus every selected test pass.
4. Rejecting approval produces `REJECTED`; it performs no GitHub or DataHub
   writeback.
5. DataHub context failure, validation failure, or an unexpected exception keeps
   the release blocked.
6. The LLM has no reference to the state-transition, policy, approval, GitHub,
   or DataHub mutation methods.

## Secrets

The hosted DeepSeek key is encrypted with `systemd-creds` and mounted read-only
at service start. It is never stored in the repository or frontend. The MCP and
dbt/Git children receive small explicit environment allowlists, excluding the
DeepSeek credential path and unrelated server variables. The GitHub PAT is used
only for maintainer release operations with a one-command credential helper; it
is not loaded by RepairPilot.

## Network exposure

Caddy is the only public entry point. The API listens on `127.0.0.1:8766` and
DataHub frontend on `127.0.0.1:9002`. Postgres, GMS, Kafka, MySQL, and OpenSearch
also bind only to loopback. DataHub uses a dedicated Reader account for judges.

## Known scope limits

- The hosted demo exposes one fixed dbt column-rename scenario.
- Approval identity is a demonstration record, not enterprise SSO attestation.
- The canonical PR is pre-created so public judges cannot spend repository
  credentials or create unbounded branches.
- DataHub contains synthetic metadata only. Do not put production metadata into
  this public instance.
