#!/bin/bash
# J2 -- Validator TASK-20260826-9605ae. Real subprocess kills against
# rt_ctrl_1_matched_pair_v2.py.  Only a real subprocess can be really killed.
# Every cell is d=64, beta=20, mpfr_bits=53 -- acceptance scale.  NO d=512, NO
# mpfr_bits=100, NO --scale-run-authorisation is ever passed.
set -u
V=/tmp/claude-0/-home-user-crypto-autoresearcher/15de1654-2503-5954-afd1-67e6db6674e9/scratchpad/sagevenv/bin/python
INSTR=/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/tasks/TASK-20260826-602395/rt_ctrl_1_matched_pair_v2.py
BASE=/home/user/crypto-autoresearcher/coordination/goals/GOAL-MLKEM-005/batches/BATCH-762807/reviews/TASK-20260826-9605ae/probes/j2
mkdir -p "$BASE"

launch () {  # $1=tag  $2=delay  $3=sigspec(or NONE)  $4...=extra args
  local tag="$1"; shift
  local delay="$1"; shift
  local sigs="$1"; shift
  local d="$BASE/$tag"
  rm -rf "$d"; mkdir -p "$d"
  "$V" "$INSTR" run --out-dir "$d" --prefix p --d 64 --beta 20 \
       "$@" > "$d/proc_stdout.log" 2>&1 &
  local pid=$!
  if [ "$sigs" != "NONE" ]; then
    sleep "$delay"
    for s in $sigs; do kill -"$s" "$pid" 2>/dev/null; done
  fi
  wait $pid; local rc=$?
  echo "$tag rc=$rc pid=$pid signals=[$sigs] delay=$delay" | tee "$d/outcome.txt"
}

echo "### T1 PTM-2(i) normal completion, NO signal delivered"
launch T1_no_signal 0 NONE --mpfr-bits 53 --heartbeat-seconds 0.25

echo "### T2 PTM-2(ii) SIGKILL -- no handler may run"
launch T2_sigkill 2.0 KILL --mpfr-bits 53,53,53,53,53,53 --heartbeat-seconds 0.25

echo "### T3 SIGTERM mid-run (reproduce the producer's own S1)"
launch T3_sigterm 2.0 TERM --mpfr-bits 53,53,53,53,53,53 --heartbeat-seconds 0.25

echo "### T4 SIGINT mid-run"
launch T4_sigint 2.0 INT --mpfr-bits 53,53,53,53,53,53 --heartbeat-seconds 0.25

echo "### T5 SIGTERM delivered TWICE back to back"
launch T5_double_term 2.0 "TERM TERM" --mpfr-bits 53,53,53,53,53,53 --heartbeat-seconds 0.25

echo "### T6 signal STORM: 30 mixed signals, tiny heartbeat, refresh in flight"
launch T6_storm 2.0 "TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT TERM INT" \
       --mpfr-bits 53,53,53,53,53,53 --heartbeat-seconds 0.001

echo "### T7 SIGTERM immediately at startup (racing the arming path)"
launch T7_startup 0.0 TERM --mpfr-bits 53 --heartbeat-seconds 0.25

echo "### T8 SIGTERM during an inter-tour sleep (handler runs in Python, not in C)"
launch T8_in_sleep 2.0 TERM --mpfr-bits 53 --heartbeat-seconds 0.05 \
       --simulate-slow-tour-seconds 0.5

echo "### T9 SIGALRM via the instrument's OWN cell timeout"
launch T9_alarm 0 NONE --mpfr-bits 53 --heartbeat-seconds 0.25 \
       --simulate-slow-tour-seconds 0.4 --cell-timeout-seconds 1.5

echo "### T10 SIGTERM very late, aimed at the exit path"
launch T10_late 3.4 TERM --mpfr-bits 53 --heartbeat-seconds 0.05 \
       --simulate-slow-tour-seconds 0.25
echo "ALL LAUNCHES DONE"
