#!/bin/bash
# ITEM 2: structure-destroyed controls RAISED to 2^31 (BATCH-004 ran 2^30).
# Waits for ITEM 1 to finish so that at most 2 threads are ever in flight.
cd "$(dirname "$0")"
while ! grep -q BLOCK_K3_DONE runs/timing.txt 2>/dev/null; do sleep 5; done
run(){ name=$1; shift
  S=$(date +%s.%N)
  ./yoyo_sbox_v2 arm $name "$@" > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T" >> runs/timing.txt
  echo "./yoyo_sbox_v2 arm $name $*" >> runs/commands.txt
}
run SD31-AES aes              5 15 1 31 531001 1 2
run SD31-R1  rand:20260803001 5 15 1 31 531001 1 2
run SD31-R2  rand:20260803002 5 15 1 31 531001 1 2
echo ITEM2_DONE >> runs/timing.txt
