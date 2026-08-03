#!/bin/bash
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-002/tasks/TASK-20260802-9dcca8
for spec in "TRUE6-S2 attack6n 6 90031" "TRUE7-S2 attack7n 7 90031"; do
 set -- $spec; name=$1 mode=$2 rounds=$3 seed=$4
 cmd="$D/sq_null $mode 2b7e151628aed2a6abf7158809cf4f3c 5e507f2e41fa3fa088c222ebd038a81e $rounds 2 $seed 4 0"
 s=$(date -u +%s); timeout 400 $cmd > $D/runs/$name.json 2> $D/runs/$name.err; rc=$?; e=$(date -u +%s)
 echo "{\"run\":\"$name\",\"segment\":2,\"command\":\"$cmd\",\"exit_status\":$rc,\"start_utc\":\"$(date -u -d @$s +%Y-%m-%dT%H:%M:%SZ)\",\"end_utc\":\"$(date -u -d @$e +%Y-%m-%dT%H:%M:%SZ)\",\"wall_seconds\":$((e-s)),\"threads\":4,\"concurrent_batch\":false,\"machine\":\"sole producer, sequential\",\"stdout\":\"runs/$name.json\",\"stderr\":\"runs/$name.err\",\"status\":\"$([ $rc -eq 0 ] && echo completed || echo failed_or_timeout)\"}" >> $D/runs/run_ledger.jsonl
done
