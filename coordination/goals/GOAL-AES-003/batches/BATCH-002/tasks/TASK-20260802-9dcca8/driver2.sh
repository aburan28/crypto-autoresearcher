#!/bin/bash
ulimit -v 8388608
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-9dcca8
STOP=1785693407
RESERVE=270
TARGET=2b7e151628aed2a6abf7158809cf4f3c
mapfile -t WK < $D/wrong_keys.txt
LOG=$D/runs/run_ledger.jsonl
run(){
  local name=$1 mode=$2 hk=$3 rounds=$4 ns=$5 seed=$6 nw=$7 est=$8
  local now=$(date -u +%s)
  if (( now + est + RESERVE > STOP )); then
    echo "{\"run\":\"$name\",\"status\":\"skipped_budget\",\"reason\":\"projected finish past binding_stop minus reserve\",\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"est_seconds\":$est}" >> $LOG
    return 0
  fi
  local cmd="$D/sq_null $mode $TARGET $hk $rounds $ns $seed 4 $nw"
  local s=$(date -u +%s)
  timeout 500 $cmd > $D/runs/$name.json 2> $D/runs/$name.err
  local rc=$?
  local e=$(date -u +%s)
  echo "{\"run\":\"$name\",\"command\":\"$cmd\",\"exit_status\":$rc,\"start_utc\":\"$(date -u -d @$s +%Y-%m-%dT%H:%M:%SZ)\",\"end_utc\":\"$(date -u -d @$e +%Y-%m-%dT%H:%M:%SZ)\",\"wall_seconds\":$((e-s)),\"stdout\":\"runs/$name.json\",\"stderr\":\"runs/$name.err\",\"status\":\"$([ $rc -eq 0 ] && echo completed || echo failed)\"}" >> $LOG
}
run WRONG6-01 attack6n ${WK[0]} 6 2 90001 3 130
run WRONG6-02 attack6n ${WK[1]} 6 2 90002 3 130
run WRONG7-01 attack7n ${WK[0]} 7 2 90001 3 370
run WRONG6-03 attack6n ${WK[2]} 6 2 90003 3 130
run WRONG6-04 attack6n ${WK[3]} 6 2 90004 3 130
run WRONG6-05 attack6n ${WK[4]} 6 2 90005 3 130
run WRONG7-02 attack7n ${WK[1]} 7 2 90002 3 370
run WRONG6-06 attack6n ${WK[5]} 6 2 90006 3 130
run WRONG6-07 attack6n ${WK[6]} 6 2 90007 3 130
run WRONG6-08 attack6n ${WK[7]} 6 2 90008 3 130
run PART6-01  attack6n ${WK[0]} 6 2 90009 1 130
run PART7-01  attack7n ${WK[0]} 7 2 90009 1 370
run PART6-02  attack6n ${WK[1]} 6 2 90010 1 130
echo "{\"marker\":\"DRIVER2_DONE\",\"utc\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}" >> $LOG
