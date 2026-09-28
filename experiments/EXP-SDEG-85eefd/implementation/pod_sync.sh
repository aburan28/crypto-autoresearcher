#!/usr/bin/env bash
# Sync the protocol files and the implementation to the charged-execution pod
# (AMD-20260928-7ce387 execution_host) and optionally run the non-Sage smoke
# path there. The pod tree mirrors the repository layout under $POD_ROOT, so
# driver.py's default --repo-root and protocol paths resolve unchanged.
#
#   pod_sync.sh sync            copy protocol files + implementation (no smoke/)
#   pod_sync.sh smoke           sync, then smoke.py --no-sage (L=8 seed 1, smoke
#                               labels) and a 4-worker charged driver dry run;
#                               copy results back to implementation/smoke/pod/
#   pod_sync.sh pull RUN-ID     copy runs/RUN-ID/charged back from the pod
#
# Env: POD_SSH (default below), POD_ROOT (default /workspace/sdeg).
set -euo pipefail
POD_HOST=${POD_HOST:-root@213.173.110.47}
POD_PORT=${POD_PORT:-19497}
POD_KEY=${POD_KEY:-$HOME/.ssh/id_ed25519}
POD_ROOT=${POD_ROOT:-/workspace/sdeg}
SSH="ssh -i $POD_KEY -p $POD_PORT -o ConnectTimeout=20"
HERE=$(cd "$(dirname "$0")" && pwd)
EXP=experiments/EXP-SDEG-85eefd
REPO=$(cd "$HERE/../../.." && pwd)
IMPL=$EXP/implementation

sync() {
  $SSH "$POD_HOST" "mkdir -p $POD_ROOT"
  (cd "$REPO" && rsync -a -R -e "$SSH" \
      --exclude '__pycache__' --exclude '.pytest_cache' --exclude 'implementation/smoke' \
      "$EXP/specification.yaml" \
      "$EXP/amendments/AMD-20260926-3479cf.yaml" \
      "$EXP/amendments/AMD-20260928-7ce387.yaml" \
      "$EXP/amendments/AMD-20260928-d3ed9e.yaml" \
      "$EXP/amendments/ic_leads_fixtures_v2.json" \
      "$EXP/amendments/ic_leads_fixtures_v2.py" \
      ledger/decisions/DEC-20260928-6b03c5.yaml \
      ledger/decisions/DEC-20260928-48a648.yaml \
      "$IMPL" \
      "$POD_HOST:$POD_ROOT/")
  # the pod has no git checkout: record what was synced
  (cd "$REPO" && git rev-parse HEAD) | $SSH "$POD_HOST" "cat > $POD_ROOT/SOURCE_COMMIT"
  $SSH "$POD_HOST" "cd $POD_ROOT/$IMPL && sha256sum *.py semaev_polys.json trial-plan-v2.json" \
      > "$HERE/smoke/pod_synced_sha256.txt"
  (cd "$HERE" && shasum -a 256 *.py semaev_polys.json trial-plan-v2.json) > "$HERE/smoke/mac_sha256.txt"
  diff <(awk '{print $1, $2}' "$HERE/smoke/mac_sha256.txt") \
       <(awk '{print $1, $2}' "$HERE/smoke/pod_synced_sha256.txt") && echo "synced files identical"
}

case "${1:-sync}" in
  sync) mkdir -p "$HERE/smoke"; sync ;;
  smoke)
    mkdir -p "$HERE/smoke"; sync
    $SSH "$POD_HOST" "cd $POD_ROOT/$IMPL && rm -rf smoke/pod smoke/driver_dryrun_pod && mkdir -p smoke && \
      nice -n 10 python3 smoke.py --no-sage --per-deck 16 --out-dir smoke/pod > smoke/pod.stdout 2> smoke/pod.stderr; \
      echo smoke_exit=\$?; \
      nice -n 10 python3 driver.py --mode charged --smoke-dry-run --run-id DRYRUN-v3-pod \
        --runs-dir smoke/driver_dryrun_pod --dry-per-deck 4 --workers 4 \
        --source-commit \$(cat $POD_ROOT/SOURCE_COMMIT) > smoke/driver_dryrun_pod.log 2>&1; \
      echo driver_exit=\$?; \
      TP=$POD_ROOT/.pytest_pkgs; echo 'pytest target (isolated from the run interpreter site-packages): '\$TP \
        > smoke/pod_pytest_install.txt; \
      python3 -c 'import pytest' 2>/dev/null || [ -d \$TP/pytest ] || \
        python3 -m pip install -q --target \$TP pytest >> smoke/pod_pytest_install.txt 2>&1 || true; \
      (PYTHONPATH=\$TP python3 -m pytest -q -p no:cacheprovider > smoke/pod_pytest.txt 2>&1 || true); \
      tail -3 smoke/pod_pytest.txt"
    rm -rf "$HERE/smoke/pod"; mkdir -p "$HERE/smoke/pod"
    rsync -a -e "$SSH" "$POD_HOST:$POD_ROOT/$IMPL/smoke/pod/" "$HERE/smoke/pod/smoke/"
    rsync -a -e "$SSH" "$POD_HOST:$POD_ROOT/$IMPL/smoke/driver_dryrun_pod" "$HERE/smoke/pod/"
    rsync -a -e "$SSH" "$POD_HOST:$POD_ROOT/$IMPL/smoke/pod.stdout" "$POD_HOST:$POD_ROOT/$IMPL/smoke/pod.stderr" \
      "$POD_HOST:$POD_ROOT/$IMPL/smoke/driver_dryrun_pod.log" "$POD_HOST:$POD_ROOT/$IMPL/smoke/pod_pytest.txt" \
      "$POD_HOST:$POD_ROOT/$IMPL/smoke/pod_pytest_install.txt" \
      "$HERE/smoke/pod/"
    ;;
  pull)
    RUN=${2:?RUN-ID}
    mkdir -p "$REPO/$EXP/runs/$RUN"
    rsync -a -e "$SSH" "$POD_HOST:$POD_ROOT/$EXP/runs/$RUN/charged" "$REPO/$EXP/runs/$RUN/"
    ;;
  *) echo "usage: $0 sync|smoke|pull RUN-ID" >&2; exit 2 ;;
esac
