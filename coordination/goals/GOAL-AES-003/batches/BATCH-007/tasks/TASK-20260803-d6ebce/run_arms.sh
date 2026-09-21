#!/usr/bin/env bash
# TASK-20260803-d6ebce arm driver. Frozen instrument, unchanged, 2 threads.
set -u
BIN=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-004/tasks/TASK-20260803-367b1b/yoyo_sbox_v2
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-007/tasks/TASK-20260803-d6ebce
R=$D/runs
CMDS=$R/commands.txt
mkdir -p "$R"

run_arm () { # name sbox rounds amask smask log2N seed armid
  local name=$1
  shift
  local t0 t1 rc
  t0=$(date +%s.%N)
  "$BIN" arm "$name" "$@" 2 > "$R/$name.json" 2> "$R/$name.err"
  rc=$?
  t1=$(date +%s.%N)
  echo "$name|exit=$rc|secs=$(echo "$t1 - $t0" | bc)|$BIN arm $name $* 2" >> "$CMDS"
  echo "  [$name] exit=$rc $(echo "$t1 - $t0" | bc)s"
}

case "${1:-all}" in
S0)
  "$BIN" geom > "$R/geom.json" 2> "$R/geom.err"; echo "geom|exit=$?|$BIN geom" >> "$CMDS"
  "$BIN" pin aes 20260803701 > "$R/pin_aes.json" 2> "$R/pin_aes.err"; echo "pin_aes|exit=$?|$BIN pin aes 20260803701" >> "$CMDS"
  "$BIN" pin rand:20260803702 20260803701 > "$R/pin_rand.json" 2> "$R/pin_rand.err"; echo "pin_rand|exit=$?|$BIN pin rand:20260803702 20260803701" >> "$CMDS"
  ;;
S1)
  for AM in 1 2 4 8 3 5 6 9 12 7 15; do
    run_arm "S1-a$AM" aes 4 $AM 1 24 20260803701 $AM
  done
  ;;
S2)
  for RR in 1 2 3; do
    run_arm "S2-r$RR" aes $RR 2 1 24 20260803701 $((40+RR))
  done
  ;;
S3)
  for SM in 2 4 7 13; do
    run_arm "S3-s$SM" aes 4 2 $SM 24 20260803701 $((50+SM))
  done
  ;;
S4)
  run_arm "S4-rand-a4"   rand:20260803702 4 4  1 24 20260803701 61
  run_arm "S4-rand-a15"  rand:20260803702 4 15 1 24 20260803701 62
  run_arm "S4-key2-a4"   aes 4 4  1 24 20260803999 63
  run_arm "S4-key2-a2"   aes 4 2  1 24 20260803999 64
  run_arm "S4-rand-a2-s7" rand:20260803702 4 2 7 24 20260803701 65
  ;;
S5)
  run_arm "S5-r5-a2" aes 5 2 1 31 20260803701 71
  ;;
S6)
  run_arm "S6-r5-a4-key2" aes 5 4 1 31 20260803999 72
  ;;
S7)
  run_arm "S7-r5-a2-rand" rand:20260803702 5 2 1 31 20260803701 73
  ;;
esac
