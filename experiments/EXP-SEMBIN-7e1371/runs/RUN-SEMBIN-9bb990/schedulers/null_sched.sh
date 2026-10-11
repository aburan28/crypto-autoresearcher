#!/bin/bash
# matched_null control: shape-matched random Boolean systems.
# Single-level blocks at every m=2 window cell (cheap), and the degree-4 closure
# at two cells for the rank contrast against the chained system of the same shape.
cd /home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code
R=/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990
L=/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_null.log
python3 run_wrapper.py "$R/null_single" --groups m2_window,sweep_n17 --families matched_null \
  --draw-list 0 --subspaces low_degree_polynomial --b-modes B_equals_1 \
  --no-closure --skip-f4 --skip-f4-reason "null control: single-level block only in this pass" \
  --single-d3 --single-max-cols 1500000 --closure-mem-cap 2.0 --controls none --resume >> $L 2>&1
# wait for a memory window before the two closures
while [ "$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo)" -lt 7 ]; do sleep 60; done
python3 run_wrapper.py "$R/null_closure" --cells 17:3:3:6,40:2:2:20 --families matched_null \
  --draw-list 0 --subspaces low_degree_polynomial --b-modes B_equals_1 \
  --no-single --skip-f4 --skip-f4-reason "null control: closure only in this pass" \
  --closure-mem-cap 2.5 --closure-max-cols 200000 --d-max 4 --controls none --resume >> $L 2>&1
echo "null done" >> $L
