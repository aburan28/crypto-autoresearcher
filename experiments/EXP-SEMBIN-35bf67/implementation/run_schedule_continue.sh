#!/bin/sh
# EXP-SEMBIN-35bf67 continuation schedule after the 2026-10-05 container restart.
# Written 2026-10-05 before 13:23:40Z, BEFORE any continuation run started. New file; run_schedule.sh is
# unchanged and must NOT be re-invoked (it would resume, and so modify, the completed run
# RUN-SEMBIN-24e9d9 and the interrupted run RUN-SEMBIN-633f0c).
# Same stage23.py arguments as run_schedule.sh items 2-8 (implementation/schedule-allocation.md),
# new run ids minted with tools/allocate_id.py and --check'ed. Seeds depend on stage/cell/arm/index
# only, so the instances are those the original schedule would have produced.
# Extras rule: implementation/continuation-allocation.md (pre-declared, outcome-independent).
# Usage: SEMBIN_BIN=... SEMBIN_WORK=... sh implementation/run_schedule_continue.sh
set -u
EXPD=$(cd "$(dirname "$0")/.." && pwd)
cd "$EXPD"
LOG=implementation/schedule-continue.log
python3 - <<'EOF' || { echo "Stage-1 gate not passed: Stage 2 not started" | tee -a "$LOG"; exit 3; }
import json, sys
eg = json.load(open("stage1/engine-gate.json"))
sm = json.load(open("stage1/baseline-smoke.json"))
ok = eg["SR2_engine_gate_pass"] and sm["smoke_complete_8_per_stratum"] and not sm["SR3_failure_rate_gt_0.10_in_any_stratum"] and not sm["dual_rank_artifact_present"]
print("stage1 gate:", ok)
sys.exit(0 if ok else 1)
EOF
T0=$(date +%s)
run() { # RUN-ID args...
  id=$1; shift
  if [ -e "runs/$id/manifest.yaml" ]; then echo "[$(date -u +%FT%TZ)] skip $id (manifest exists)" >> "$LOG"; return; fi
  if [ -e "runs/$id" ]; then
    echo "[$(date -u +%FT%TZ)] STOP: runs/$id exists without manifest (interrupted?). Not resuming in place; a new run id is required." >> "$LOG"
    exit 4
  fi
  mkdir -p "runs/$id"
  echo "[$(date -u +%FT%TZ)] start $id $*" >> "$LOG"
  python3 implementation/stage23.py cell "$id" "$@" >> "runs/$id/stdout.log" 2>> "runs/$id/stderr.log"
  echo "[$(date -u +%FT%TZ)] end $id rc=$?" >> "$LOG"
}
#            RUN-ID            stage  n  m t k  SAT UNSAT NULL HOURS NULL_T PRIMARY_FRACTION
run RUN-SEMBIN-cfd1a7 stage2 40 2 2 20 100 100 100 6.5 2 0.55   # supersedes interrupted RUN-SEMBIN-633f0c
run RUN-SEMBIN-20fdd9 stage2 21 3 3 7  100 100 100 2.0 0 1.0
run RUN-SEMBIN-5bea99 stage2 45 2 2 23 100 100 100 3.5 0 1.0
run RUN-SEMBIN-9d540c stage3 40 2 2 21 50  50  0   2.0 0 1.0
run RUN-SEMBIN-bb6ee8 stage3 40 2 2 22 50  50  0   2.5 0 1.0
# Extras (schedule-allocation.md: "If wall time remains after item 8, cells 6 then 5 receive one
# SAT and one UNSAT instance each"). Remaining = 86400 - 12083 (pre-interruption executor run
# wall, 06:12:28Z..09:33:51Z) - continuation wall so far; see continuation-allocation.md.
rem() { echo $(( 86400 - 12083 - ($(date +%s) - T0) )); }
R=$(rem); echo "[$(date -u +%FT%TZ)] extras: remaining session seconds $R" >> "$LOG"
if [ "$R" -gt 0 ]; then
  run RUN-SEMBIN-32150f stage2 50 2 2 25 1 1 0 $(python3 -c "print(round($R/3600,3))") 0 1.0
  R=$(rem); echo "[$(date -u +%FT%TZ)] extras: remaining session seconds $R" >> "$LOG"
  if [ "$R" -gt 0 ]; then
    run RUN-SEMBIN-b666d2 stage2 25 3 3 9 1 1 0 $(python3 -c "print(round($R/3600,3))") 0 1.0
  else
    echo "[$(date -u +%FT%TZ)] extras: (25,3,3,9) not run, session budget used" >> "$LOG"
  fi
else
  echo "[$(date -u +%FT%TZ)] extras: (50,2,2,25) and (25,3,3,9) not run, session budget used" >> "$LOG"
fi
echo "[$(date -u +%FT%TZ)] continuation schedule complete" >> "$LOG"
