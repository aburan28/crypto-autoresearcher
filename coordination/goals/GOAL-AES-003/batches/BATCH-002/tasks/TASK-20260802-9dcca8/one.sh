#!/bin/bash
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-9dcca8
name=$1 mode=$2 hk=$3 rounds=$4 seed=$5 nw=$6 nthr=$7 tmo=$8
cmd="$D/sq_null $mode 2b7e151628aed2a6abf7158809cf4f3c $hk $rounds 2 $seed $nthr $nw"
s=$(date -u +%s)
timeout $tmo $cmd > $D/runs/$name.json 2> $D/runs/$name.err
rc=$?
e=$(date -u +%s)
echo "{\"run\":\"$name\",\"command\":\"$cmd\",\"exit_status\":$rc,\"start_utc\":\"$(date -u -d @$s +%Y-%m-%dT%H:%M:%SZ)\",\"end_utc\":\"$(date -u -d @$e +%Y-%m-%dT%H:%M:%SZ)\",\"wall_seconds\":$((e-s)),\"concurrent_batch\":true,\"threads\":$nthr,\"stdout\":\"runs/$name.json\",\"stderr\":\"runs/$name.err\",\"status\":\"$([ $rc -eq 0 ] && echo completed || echo failed_or_timeout)\"}" >> $D/runs/run_ledger.jsonl
