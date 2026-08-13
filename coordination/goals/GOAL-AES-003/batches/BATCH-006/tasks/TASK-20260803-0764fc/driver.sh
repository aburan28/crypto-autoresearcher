#!/bin/bash
# TASK-20260803-0764fc driver. Budget-aware: never STARTS an arm that cannot
# finish before the binding stop. Skipped arms are NAMED in runs/dropped.txt.
cd "$(dirname "$0")"
STOP=1785778410          # binding stop epoch, = start 1785772410 + 6000
MARGIN=240               # reserve for analysis + RESULTS.json

need(){ # $1 = estimated seconds; returns 0 if we may start
  local now=$(date +%s)
  [ $(( now + $1 + MARGIN )) -lt $STOP ]
}

runarm(){ name=$1; est=$2; shift 2
  if ! need "$est"; then
    echo "$name DROPPED_ON_BUDGET est=${est}s cmd=./yoyo_sbox_v2 arm $name $*" >> runs/dropped.txt
    return 9
  fi
  S=$(date +%s.%N)
  timeout 900 ./yoyo_sbox_v2 arm "$name" "$@" > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T cmd=./yoyo_sbox_v2 arm $name $*" >> runs/arms_timing.txt
  echo "./yoyo_sbox_v2 arm $name $*" >> runs/commands.txt
}

# ---------------- SECTION A remainder (RANK 1) : sequential, alone ----------
runarm A2-R4-K1    200 aes 4 1 1 30 531001 1 2
runarm A3-R3-MAIN   60 aes 3 1 1 24 431001 1 2
runarm A4-R2-MAIN   60 aes 2 1 1 20 431001 1 2
runarm A5-R4-R1-K1 200 rand:20260803001 4 1 1 30 531001 1 2
echo "SECTION_A_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/arms_timing.txt

# ---------------- SECTION B (RANK 2, RC-8) ----------------------------------
# Pin + dump every drawn S-box BEFORE measuring it.
for i in $(seq -w 1 27); do
  s=202608037$i
  ./yoyo_sbox_v2 pin  "rand:$s" 60600002 > runs/pin_rand_$s.json 2> runs/pin_rand_$s.err
  echo "pin rand:$s exit=$?" >> runs/pins_timing.txt
  ./yoyo_sbox_v2 sbox "rand:$s" > sboxes/sbox_rand_$s.json 2> sboxes/sbox_rand_$s.err
done
echo "SECTION_B_PINS_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/arms_timing.txt

# AES reference at the same fresh arm seed, then the 27 draws, 2 concurrent.
runarm B0-AES-REF 220 aes 5 1 1 30 631001 1 2
for i in $(seq -w 1 27); do
  s=202608037$i
  runarm "B$i-RAND-$s" 260 "rand:$s" 5 1 1 30 631001 1 2 &
  # keep at most 2 arms (2 threads each) on the 4 available cores
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 2; done
done
wait
echo "SECTION_B_DONE $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> runs/arms_timing.txt
echo "DRIVER_EXIT $(date -u +%Y-%m-%dT%H:%M:%SZ) epoch=$(date +%s) stop=$STOP" >> runs/arms_timing.txt
