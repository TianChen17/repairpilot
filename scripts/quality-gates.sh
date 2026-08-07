#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

./scripts/preflight.sh
.venv/bin/ruff check backend scripts
.venv/bin/pytest --cov=app --cov-report=term-missing --cov-fail-under=75 backend/tests
.venv/bin/dbt parse --project-dir warehouse --profiles-dir warehouse
npm --prefix frontend run build

echo "local_quality_gates=pass"

