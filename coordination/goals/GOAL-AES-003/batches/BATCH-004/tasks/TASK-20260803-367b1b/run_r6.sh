#!/bin/bash
cd "$(dirname "$0")"
run(){ name=$1; shift
  S=$(date +%s.%N)
  ./yoyo_sbox arm $name "$@" > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T" >> runs/arms_timing.txt
  echo "./yoyo_sbox arm $name $*" >> runs/commands.txt
}
run Y-R2-main-r6 rand:20260803002 6 1 1 31 431003 3 2
run Y-AES-main-r6 aes 6 1 1 31 431001 1 2
run Y-R1-main-r6 rand:20260803001 6 1 1 31 431002 2 2
echo DONE_R6 >> runs/arms_timing.txt
