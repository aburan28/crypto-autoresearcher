#!/bin/bash
# Executes PROTOCOL.md: interleaved solves, then interleaved per-step benchmark. Pinned to CPU 0.
set -e
cd "$(dirname "$0")"
mapfile -t BS < <(grep EXPORT_CURVE curves.txt | awk '{print $3}')
NAMES=(K-tau K-neg I1 I2 I3 I4 I5 I6 I7 I8)
CURVE_B=(1 1 "${BS[@]}"); MODES=(1 0 0 0 0 0 0 0 0 0)
mkdir -p raw bench
for round in $(seq 0 9); do
  for i in $(seq 0 9); do
    taskset -c 0 ./rho run "${CURVE_B[$i]}" 0 "${MODES[$i]}" 500 $((1000*i+round)) "raw/${NAMES[$i]}_r${round}.csv"
  done
  echo "solve round $round done $(date +%T)"
done
for rep in $(seq 0 20); do
  for i in $(seq 0 9); do
    taskset -c 0 ./rho bench "${CURVE_B[$i]}" 0 "${MODES[$i]}" 1048576 $((77+i)) 1 | awk -v n="${NAMES[$i]}" -v r=$rep '{print n","r","$1}' >> bench/ns_per_step.csv
  done
done
echo "ALL DONE $(date +%T)"
