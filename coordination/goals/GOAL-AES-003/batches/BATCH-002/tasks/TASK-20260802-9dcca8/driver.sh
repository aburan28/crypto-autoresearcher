#!/bin/bash
# TASK-20260802-9dcca8 wrong-hint null driver. Sequential, 4 threads per run.
ulimit -v 8388608
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-9dcca8
STOP=1785693407      # binding_stop_epoch
RESERVE=300          # seconds reserved for writing artifacts
TARGET=2b7e151628aed2a6abf7158809cf4f3c
mapfile -t WK < $D/wrong_keys.txt
LOG=$D/runs/run_ledger.jsonl
run(){ # name mode hintkey rounds nstruct seed nwrong est
  local name=$1 mode=$2 hk=$3 rounds=$4 ns=$5 seed=$6 nw=$7 est=$8
  local now=$(date -u +%s)
  if (( now + est + RESERVE > STOP )); then
    echo "{\"run\":\"$name\",\"status\":\"skipped_budget\",\"reason\":\"projected finish past binding_stop minus reserve\",\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"est_seconds\":$est}" >> $LOG
    return 0
  fi
  local cmd="$D/sq_null $mode $TARGET $hk $rounds $ns $seed 4 $nw"
  local s=$(date -u +%s)
  timeout 400 $cmd > $D/runs/$name.json 2> $D/runs/$name.err
  local rc=$?
  local e=$(date -u +%s)
  echo "{\"run\":\"$name\",\"command\":\"$cmd\",\"exit_status\":$rc,\"start_utc\":\"$(date -u -d @$s +%Y-%m-%dT%H:%M:%SZ)\",\"end_utc\":\"$(date -u -d @$e +%Y-%m-%dT%H:%M:%SZ)\",\"wall_seconds\":$((e-s)),\"stdout\":\"runs/$name.json\",\"stderr\":\"runs/$name.err\",\"status\":\"$([ $rc -eq 0 ] && echo completed || echo failed)\"}" >> $LOG
}
run TRUE6      attack6n ${WK[0]} 6 2 90001 0 75
run TRUE7      attack7n ${WK[0]} 7 2 90001 0 115
for i in 0 1 2 3 4 5 6 7; do
  s6=$((90001+i))
  run WRONG6-0$((i+1)) attack6n ${WK[$i]} 6 2 $s6 3 75
  run WRONG7-0$((i+1)) attack7n ${WK[$i]} 7 2 $s6 3 115
done
run PART6-01 attack6n ${WK[0]} 6 2 90009 1 75
run PART7-01 attack7n ${WK[0]} 7 2 90009 1 115
run PART6-02 attack6n ${WK[1]} 6 2 90010 1 75
run PART7-02 attack7n ${WK[1]} 7 2 90010 1 115
echo "{\"marker\":\"DRIVER_DONE\",\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> $LOG
