#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip wheel setuptools
.venv/bin/python -m pip install -e '.[dev]' uv
npm --prefix frontend install
./scripts/generate_seed.py
sudo docker compose up -d postgres

for attempt in $(seq 1 30); do
  if sudo docker compose exec -T postgres pg_isready -U repairpilot -d repairpilot >/dev/null 2>&1; then
    echo "postgres=ready"
    exit 0
  fi
  sleep 1
done

echo "postgres=unhealthy" >&2
exit 1
