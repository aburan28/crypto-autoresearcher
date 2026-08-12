#!/bin/bash
# ITEM 1: crossed 3 S-box x K seed design. Blocks in order; balanced on halt.
cd "$(dirname "$0")"
run(){ name=$1; shift
  S=$(date +%s.%N)
  ./yoyo_sbox_v2 arm $name "$@" > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T" >> runs/timing.txt
  echo "./yoyo_sbox_v2 arm $name $*" >> runs/commands.txt
}
run D-AES-K1 aes           5 1 1 30 531001 1 2
run D-R1-K1  rand:20260803001 5 1 1 30 531001 1 2
run D-R2-K1  rand:20260803002 5 1 1 30 531001 1 2
echo BLOCK_K1_DONE >> runs/timing.txt
run D-AES-K2 aes           5 1 1 30 531002 2 2
run D-R1-K2  rand:20260803001 5 1 1 30 531002 2 2
run D-R2-K2  rand:20260803002 5 1 1 30 531002 2 2
echo BLOCK_K2_DONE >> runs/timing.txt
run D-AES-K3 aes           5 1 1 30 531003 3 2
run D-R1-K3  rand:20260803001 5 1 1 30 531003 3 2
run D-R2-K3  rand:20260803002 5 1 1 30 531003 3 2
echo BLOCK_K3_DONE >> runs/timing.txt
