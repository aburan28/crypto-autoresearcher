#!/bin/bash
# usage: batch_c3.sh basis seed count D n1:k1 n2:k2 ...  (logs to logc3_<basis>.txt)
basis=$1; seed=$2; count=$3; D=$4; shift 4
for nk in "$@"; do
  n=${nk%:*}; k=${nk#*:}; dir=sysc3${basis}$n
  python3 gen3.py $n $k $count $seed $basis unsat $dir >> logc3_${basis}.txt 2>&1
  for f in $dir/c3_n${n}_k${k}_${basis}_${seed}_*.sys; do
    s=$(date +%s.%N)
    out=$(./lfdclose2 $D 1 < $f 2>>logc3_${basis}.err | tr '\n' ' ')
    printf "n=%s k=%s %s | %s t=%.1fs\n" $n $k $(basename $f) "$out" $(echo "$(date +%s.%N) - $s" | bc) >> logc3_${basis}.txt
  done
done
echo DONE >> logc3_${basis}.txt
