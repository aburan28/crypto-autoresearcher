#!/bin/bash
cd /home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-009/tasks/TASK-20260803-a0a7b9
B=src/yoyo_sbox_v4
run(){ n=$1; shift; s=$(date +%s); $B arm "$n" "$@" > runs/$n.json 2> runs/$n.err; rc=$?
  e=$(date +%s); echo "$n rc=$rc elapsed_s=$((e-s)) UNPREREGISTERED_GEOMETRY_EXTENSION cmd=$B arm $n $*" >> runs/arms_timing.txt; }
run G1-IDEAL-a2-s1  ideal 5 2  1  33 531001 1 2 &
run G2-IDEAL-a4-s1  ideal 5 4  1  33 531001 1 2 &
wait
run G3-IDEAL-a15-s1 ideal 5 15 1  33 531001 1 2 &
run G4-IDEAL-a1-s2  ideal 5 1  2  33 531001 1 2 &
wait
run G5-IDEAL-a1-s7  ideal 5 1  7  33 531001 1 2 &
run G6-IDEAL-a1-s13 ideal 5 1  13 33 531001 1 2 &
wait
echo "GEOM_ARMS_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/arms_timing.txt
