#!/bin/bash
# TASK-20260802-9dcca8 SEGMENT 2. Sequential, 4 threads per run, uncontended machine.
ulimit -v 8388608
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-9dcca8
STOP=1785696012      # segment-2 binding_stop_epoch (2026-08-02T18:40:12Z)
RESERVE=260
TARGET=2b7e151628aed2a6abf7158809cf4f3c
mapfile -t WK  < $D/wrong_keys.txt
mapfile -t WK2 < $D/wrong_keys_seg2.txt
LOG=$D/runs/run_ledger.jsonl
run(){ # name mode hintkey rounds seed nwrong est timeout
  local name=$1 mode=$2 hk=$3 rounds=$4 seed=$5 nw=$6 est=$7 tmo=$8
  local now=$(date -u +%s)
  if (( now + est + RESERVE > STOP )); then
    echo "{\"run\":\"$name\",\"segment\":2,\"status\":\"skipped_budget\",\"reason\":\"projected finish past segment-2 binding_stop minus reserve\",\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"est_seconds\":$est}" >> $LOG
    return 0
  fi
  local cmd="$D/sq_null $mode $TARGET $hk $rounds 2 $seed 4 $nw"
  local s=$(date -u +%s)
  timeout $tmo $cmd > $D/runs/$name.json 2> $D/runs/$name.err
  local rc=$?
  local e=$(date -u +%s)
  echo "{\"run\":\"$name\",\"segment\":2,\"command\":\"$cmd\",\"exit_status\":$rc,\"start_utc\":\"$(date -u -d @$s +%Y-%m-%dT%H:%M:%SZ)\",\"end_utc\":\"$(date -u -d @$e +%Y-%m-%dT%H:%M:%SZ)\",\"wall_seconds\":$((e-s)),\"threads\":4,\"concurrent_batch\":false,\"machine\":\"sole producer, sequential\",\"stdout\":\"runs/$name.json\",\"stderr\":\"runs/$name.err\",\"status\":\"$([ $rc -eq 0 ] && echo completed || echo failed_or_timeout)\"}" >> $LOG
}
# ---- PRIORITY 1: partial-hint arms ----
run PART6-1of3-A attack6n ${WK[0]}  6 90009 1 150 600
run PART7-1of3-A attack7n ${WK[0]}  7 90009 1 400 900
run PART6-1of3-B attack6n ${WK[1]}  6 90010 1 150 600
run PART6-2of3-A attack6n ${WK[2]}  6 90011 2 150 600
run PART7-1of3-B attack7n ${WK[1]}  7 90010 1 400 900
run PART7-2of3-A attack7n ${WK[2]}  7 90011 2 400 900
run PART6-2of3-B attack6n ${WK[3]}  6 90012 2 150 600
# ---- PRIORITY 2: further all-wrong trials, fresh keys and seeds ----
run WRONG6-B01 attack6n ${WK2[0]} 6 90021 3 150 600
run WRONG6-B02 attack6n ${WK2[1]} 6 90022 3 150 600
run WRONG7-B01 attack7n ${WK2[2]} 7 90023 3 400 900
run WRONG6-B03 attack6n ${WK2[3]} 6 90024 3 150 600
run WRONG6-B04 attack6n ${WK2[4]} 6 90025 3 150 600
run WRONG7-B02 attack7n ${WK2[5]} 7 90026 3 400 900
run WRONG6-B05 attack6n ${WK2[6]} 6 90027 3 150 600
run WRONG6-B06 attack6n ${WK2[7]} 6 90028 3 150 600
echo "{\"marker\":\"DRIVER3_DONE\",\"segment\":2,\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> $LOG
