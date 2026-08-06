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
run Y-AES-main aes 5 1 1 31 431001 1 2
run Y-R1-main rand:20260803001 5 1 1 31 431002 2 2
run Y-R2-main rand:20260803002 5 1 1 31 431003 3 2
run Y-AES-sd aes 5 15 1 30 431004 4 2
run Y-R1-sd rand:20260803001 5 15 1 30 431005 5 2
run Y-R2-sd rand:20260803002 5 15 1 30 431006 6 2
echo DONE >> runs/arms_timing.txt
