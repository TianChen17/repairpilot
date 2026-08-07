#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
base_url=${REPAIRPILOT_E2E_URL:-http://127.0.0.1:8766}
run_count=${REPAIRPILOT_E2E_RUNS:-3}
evidence_dir="$repo_root/runtime/quality/e2e"
mkdir -p "$evidence_dir"
summary="$evidence_dir/summary.jsonl"
: > "$summary"

request() {
  curl --fail --silent --show-error --retry 2 --retry-connrefused \
    --connect-timeout 5 --max-time 150 "$@"
}

wait_for_state() {
  local run_id=$1
  local expected=$2
  local deadline=$((SECONDS + 150))
  while (( SECONDS < deadline )); do
    local payload state
    payload=$(request "$base_url/api/v1/incidents/$run_id")
    state=$(jq -r '.state' <<<"$payload")
    if [[ "$state" == "$expected" ]]; then
      printf '%s' "$payload"
      return 0
    fi
    case "$state" in
      CONTEXT_UNAVAILABLE|VALIDATION_FAILED|MANUAL_REVIEW|REJECTED)
        printf '%s\n' "$payload" | jq . >&2
        return 1
        ;;
    esac
    sleep 1
  done
  echo "Timed out waiting for $expected" >&2
  return 1
}

for index in $(seq 1 "$run_count"); do
  started=$(date +%s)
  request -X POST "$base_url/api/v1/demo/reset" >/dev/null
  created=$(request -X POST "$base_url/api/v1/incidents" \
    -H 'content-type: application/json' \
    --data '{"scenario":"breaking-column-rename","execution_mode":"live"}')
  run_id=$(jq -r '.run_id' <<<"$created")
  waiting=$(wait_for_state "$run_id" AWAITING_APPROVAL)
  jq -e '
    .risk.level == "HIGH" and
    .risk.action == "BLOCK" and
    .validation.breaking_change_reproduced == true and
    .validation.repair_verified == true and
    .validation.tests_failed == 0 and
    (.repair.operations | length == 3)
  ' <<<"$waiting" >/dev/null

  learned=$(request -X POST "$base_url/api/v1/incidents/$run_id/approval" \
    -H 'content-type: application/json' \
    --data '{"decision":"approve","actor":"Revenue Analytics Owner"}')
  jq -e '
    .state == "LEARNED" and
    .approval.decision == "approve" and
    (.writeback.incident_document_urn | startswith("urn:li:document:")) and
    (.writeback.runbook_document_urn | startswith("urn:li:document:")) and
    (.writeback.assertion_urns | index("urn:li:assertion:repairpilot-gross-revenue-not-null"))
  ' <<<"$learned" >/dev/null

  receipt="$repo_root/runtime/artifacts/$run_id/evidence-receipt.json"
  jq -e --arg run_id "$run_id" '
    .run_id == $run_id and
    .mode == "live" and
    .state == "LEARNED" and
    .risk_action == "BLOCK" and
    (.patch_sha256 | length == 64) and
    (.base_commit | length == 40) and
    (.repair_commit | length == 40) and
    (.writeback_urns | length >= 4)
  ' "$receipt" >/dev/null

  elapsed=$(( $(date +%s) - started ))
  if (( elapsed >= 150 )); then
    echo "Run $run_id exceeded the 150 second target" >&2
    exit 1
  fi
  jq -cn \
    --argjson index "$index" \
    --arg run_id "$run_id" \
    --argjson elapsed_seconds "$elapsed" \
    --arg patch_sha256 "$(jq -r '.patch_sha256' "$receipt")" \
    --arg runbook_urn "$(jq -r '.writeback.runbook_document_urn' <<<"$learned")" \
    '{index:$index,run_id:$run_id,elapsed_seconds:$elapsed_seconds,patch_sha256:$patch_sha256,runbook_urn:$runbook_urn,state:"LEARNED"}' \
    | tee -a "$summary"
done

test "$(jq -s 'map(.run_id) | unique | length' "$summary")" -eq "$run_count"
test "$(jq -s 'map(.runbook_urn) | unique | length' "$summary")" -eq 1
test "$(jq -s 'map(.patch_sha256) | unique | length' "$summary")" -eq 1
request -X POST "$base_url/api/v1/demo/reset" >/dev/null
echo "q4_live_e2e=pass runs=$run_count"
