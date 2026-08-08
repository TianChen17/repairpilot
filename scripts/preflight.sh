#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)

test "$(uname -m)" = "aarch64"
test "$(df --output=avail -B1 "$repo_root" | tail -1)" -gt 8000000000
sudo docker info --format '{{.Architecture}}' | grep -Eqx 'arm64|aarch64'
sudo docker compose version >/dev/null
test -x "$repo_root/.venv/bin/python"
test -s "$repo_root/warehouse/seeds/raw_orders.csv"
test "$(wc -l < "$repo_root/warehouse/seeds/raw_orders.csv")" -eq 1201
test "$(git -C "$repo_root" remote get-url origin)" = "https://github.com/TianChen17/repairpilot.git"

bad_bindings=$(ss -ltnH | awk '$4 ~ /:(5433|8080|9002|9092|3306|9200)$/ && $4 !~ /^127\.0\.0\.1:/ && $4 !~ /^\[::1\]:/ {print $4}')
if [[ -n "$bad_bindings" ]]; then
  printf 'private_port_binding=failed %s\n' "$bad_bindings" >&2
  exit 1
fi

if git -C "$repo_root" grep -nE '(DEEPSEEK_API_KEY|GITHUB_PAT_[A-Za-z0-9_]+)=[^[:space:]]+' \
  -- ':!*.example' ':!scripts/submission-preflight.sh'; then
  echo "secret_pattern=failed" >&2
  exit 1
fi

echo "q0_preflight=pass"
