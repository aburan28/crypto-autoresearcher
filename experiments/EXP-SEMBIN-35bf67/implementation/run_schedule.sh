#!/bin/sh
# EXP-SEMBIN-35bf67 Stage 2 / Stage 3 schedule per implementation/schedule-allocation.md.
# Runs only if stage1/engine-gate.json SR2 passed and stage1/baseline-smoke.json shows a
# complete smoke without SR-3 failure or dual-rank artifact (SR-2 / SR-3).
# Usage: run_schedule.sh  (env SEMBIN_BIN, SEMBIN_WORK set; run from the experiment dir)
set -u
EXPD=$(cd "$(dirname "$0")/.." && pwd)
cd "$EXPD"
python3 - <<'EOF' || { echo "Stage-1 gate not passed: Stage 2 not started"; exit 3; }
import json, sys
eg = json.load(open("stage1/engine-gate.json"))
sm = json.load(open("stage1/baseline-smoke.json"))
ok = eg["SR2_engine_gate_pass"] and sm["smoke_complete_8_per_stratum"] and not sm["SR3_failure_rate_gt_0.10_in_any_stratum"] and not sm["dual_rank_artifact_present"]
print("stage1 gate:", ok)
sys.exit(0 if ok else 1)
EOF
run() { # RUN-ID args...
  id=$1; shift
  mkdir -p "runs/$id"
  echo "[$(date -u +%FT%TZ)] start $id $*"
  python3 implementation/stage23.py cell "$id" "$@" >> "runs/$id/stdout.log" 2>> "runs/$id/stderr.log"
  echo "[$(date -u +%FT%TZ)] end $id rc=$?"
}
#            RUN-ID            stage  n  m t k  SAT UNSAT NULL HOURS NULL_T PRIMARY_FRACTION
run RUN-SEMBIN-24e9d9 stage2 30 2 2 15 100 100 100 1.0 0 0.85
run RUN-SEMBIN-633f0c stage2 40 2 2 20 100 100 100 6.5 2 0.55
run RUN-SEMBIN-2fa33f stage2 21 3 3 7  100 100 100 2.0 0 1.0
run RUN-SEMBIN-ccbf15 stage2 45 2 2 23 100 100 100 3.5 0 1.0
run RUN-SEMBIN-8d8b15 stage3 40 2 2 21 50  50  0   2.0 0 1.0
run RUN-SEMBIN-8c9c1a stage3 40 2 2 22 50  50  0   2.5 0 1.0
echo "[$(date -u +%FT%TZ)] schedule complete"
