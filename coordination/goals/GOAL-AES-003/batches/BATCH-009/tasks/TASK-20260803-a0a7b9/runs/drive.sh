#!/bin/bash
# TASK-20260803-a0a7b9 arm driver. Preregistered arms only.
cd /home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-009/tasks/TASK-20260803-a0a7b9
B=src/yoyo_sbox_v4
run(){ name=$1; shift; s=$(date +%s)
  $B arm "$name" "$@" > runs/$name.json 2> runs/$name.err; rc=$?
  e=$(date +%s); echo "$name rc=$rc elapsed_s=$((e-s)) cmd=$B arm $name $*" >> runs/arms_timing.txt; }
echo "# commands, TASK-20260803-a0a7b9" > runs/commands.txt
for c in "P1-R5-PAIR aes 5 1 1 30 531001 1 2" "N1-IDEAL-P30 ideal 5 1 1 30 531001 1 2" \
         "P2-R10-PAIR aes 10 1 1 30 531001 1 2" "N2-IDEAL-P33 ideal 5 1 1 33 531001 1 2"; do
  echo "$PWD/$B arm $c" >> runs/commands.txt; done
run P1-R5-PAIR aes 5 1 1 30 531001 1 2 &
run N1-IDEAL-P30 ideal 5 1 1 30 531001 1 2 &
wait
run P2-R10-PAIR aes 10 1 1 30 531001 1 2 &
run N2-IDEAL-P33 ideal 5 1 1 33 531001 1 2 &
wait
echo "ALL_ARMS_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/arms_timing.txt
