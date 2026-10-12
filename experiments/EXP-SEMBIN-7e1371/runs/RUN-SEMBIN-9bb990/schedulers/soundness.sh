#!/bin/bash
# certificate_soundness control: cells where a full Groebner completion IS
# affordable, run with BOTH instruments plus the exact counter, on
# solution-BEARING draws (chosen by the counter, not by any degree), so the
# agreement test is not the trivial one between two zeros.
cd /home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/code
R=/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990
L=/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/w_soundness.log
run() { python3 run_wrapper.py "$R/soundness_$4" --cells "$1" --families chained_eq5 \
   --draw-list "$2" --subspaces low_degree_polynomial --b-modes B_equals_1 \
   --no-single --wall-cap 2400 --mem-cap 4 --closure-mem-cap "$3" \
   --closure-max-cols 200000 --d-max 4 --controls none --resume >> $L 2>&1; }
run 17:3:3:6 5,0 1.5 n17k6
run 19:3:3:7 4,0 2.5 n19k7
run 13:4:4:4 2,0 3.0 n13k4
run 12:6:6:2 0   1.5 n12k2
echo "soundness done" >> $L
