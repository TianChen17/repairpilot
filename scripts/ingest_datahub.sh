#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

export POSTGRES_HOST=${POSTGRES_HOST:-127.0.0.1}
export POSTGRES_PORT=${POSTGRES_PORT:-5433}
export POSTGRES_DB=${POSTGRES_DB:-repairpilot}
export POSTGRES_USER=${POSTGRES_USER:-repairpilot}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-repairpilot-local-only}
export DBT_TARGET_SCHEMA=analytics

.venv/bin/dbt build --project-dir warehouse --profiles-dir warehouse
cp warehouse/target/run_results.json warehouse/target/run_results_build.json
.venv/bin/dbt docs generate --project-dir warehouse --profiles-dir warehouse

.venv/bin/datahub ingest -c ingestion/postgres.yml
.venv/bin/datahub ingest -c ingestion/dbt.yml
.venv/bin/python scripts/seed_datahub.py
