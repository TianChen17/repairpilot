#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

test "$(uname -m)" = "aarch64"
test "$(df --output=avail -B1 "$repo_root" | tail -1)" -gt 12000000000
sudo docker info --format '{{.Architecture}}' | grep -Eqx 'arm64|aarch64'
sudo docker compose version >/dev/null
test -x "$repo_root/.venv/bin/python"
test -s "$repo_root/warehouse/seeds/raw_orders.csv"
test "$(wc -l < "$repo_root/warehouse/seeds/raw_orders.csv")" -eq 1201

if git -C "$repo_root" grep -nE '(DEEPSEEK_API_KEY|GITHUB_PAT_[A-Za-z0-9_]+)=[^[:space:]]+' -- ':!*.example'; then
  echo "secret_pattern=failed" >&2
  exit 1
fi

echo "q0_preflight=pass"
