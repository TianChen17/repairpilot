#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

./scripts/preflight.sh
.venv/bin/ruff check backend scripts video/scripts
.venv/bin/ruff format --check backend scripts video/scripts
.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=75 backend/tests
.venv/bin/dbt parse --project-dir warehouse --profiles-dir warehouse
npm --prefix frontend run build
npm --prefix video run lint
curl --fail --silent --show-error https://repairpilot.145-241-207-154.sslip.io/api/health \
  | jq -e '.status == "ok" and .mode == "live"' >/dev/null
curl --fail --silent --show-error --head https://catalog.145-241-207-154.sslip.io >/dev/null

echo "local_quality_gates=pass"
