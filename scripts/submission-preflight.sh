#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

required=(
  LICENSE
  README.md
  docs/DEVPOST_SUBMISSION.md
  docs/JUDGE_GUIDE.md
  docs/QUALITY_REPORT.md
  docs/SECURITY.md
  docs/YOUTUBE_AND_DEVPOST.md
  video-spec.md
  examples/repair.patch
  examples/dbt-run-results.json
  examples/dbt-command-results.json
  examples/evidence-receipt.json
  examples/incident.md
  examples/runbook.md
  examples/migration-note.md
  examples/live-e2e-summary.jsonl
  examples/final-live-e2e-summary.jsonl
)
for path in "${required[@]}"; do
  test -s "$path"
done

test "$(sha256sum examples/repair.patch | cut -d' ' -f1)" = \
  "$(jq -r '.patch_sha256' examples/evidence-receipt.json)"
test "$(jq -s 'map(.run_id) | unique | length' examples/live-e2e-summary.jsonl)" -eq 3
test "$(jq -s 'map(.patch_sha256) | unique | length' examples/live-e2e-summary.jsonl)" -eq 1
test "$(jq -s 'map(.runbook_urn) | unique | length' examples/live-e2e-summary.jsonl)" -eq 1
test "$(jq -s 'map(.run_id) | unique | length' examples/final-live-e2e-summary.jsonl)" -eq 3
test "$(jq -s 'map(.patch_sha256) | unique | length' examples/final-live-e2e-summary.jsonl)" -eq 1
test "$(jq -s 'map(.runbook_urn) | unique | length' examples/final-live-e2e-summary.jsonl)" -eq 1

curl --fail --silent --show-error --head \
  https://repairpilot.145-241-207-154.sslip.io >/dev/null
curl --fail --silent --show-error --head \
  https://catalog.145-241-207-154.sslip.io >/dev/null
curl --fail --silent --show-error \
  https://api.github.com/repos/TianChen17/repairpilot \
  | jq -e '.private == false and .license.spdx_id == "Apache-2.0"' >/dev/null

if rg -n 'localhost|127\.0\.0\.1' docs/DEVPOST_SUBMISSION.md; then
  echo "Devpost copy contains a non-public host" >&2
  exit 1
fi

if rg -n --hidden --glob '!*.lock' --glob '!video/output/**' \
  --glob '!scripts/submission-preflight.sh' \
  '(DEEPSEEK_API_KEY=.{8}|github_pat_[A-Za-z0-9_]{20,}|ghp_[A-Za-z0-9]{20,})' \
  .; then
  echo "Potential secret material found" >&2
  exit 1
fi

echo "submission_preflight=ready_for_public_youtube_url_and_entrant_declarations"
