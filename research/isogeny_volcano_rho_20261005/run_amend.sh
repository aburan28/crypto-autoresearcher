#!/bin/bash
set -e; cd "$(dirname "$0")"; mkdir -p raw_amend
declare -A B; while IFS=, read id lev b; do [ "$id" = id ] || B[$id]=$b; done < sample.csv
ARMS="0:0 0:1 1:0 2:0 101:0 102:0 201:0 202:0"
for r in $(seq 0 19); do for a in $ARMS; do id=${a%:*}; m=${a#*:}
  taskset -c 0 ./rho run ${B[$id]} 0 $m 100 $((500000+100*id+10*m+r)) raw_amend/c${id}_m${m}_r${r}.csv; done; done
echo AMEND DONE
