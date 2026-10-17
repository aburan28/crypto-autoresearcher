#!/bin/sh
# PILOT #3 extension driver (run after driver.sh): cells beyond the request, local variants only
# where the full W_4 was not feasible in pilot #2 (m=5 n=9 k=3: 124,314 columns) or sparse (m=4 n=11).
cd "$(dirname "$0")"
P="python3 pilot3.py run"
$P m5-n9k3 L1,L2      3 --sel unsat:10,sat:3 --timeout 1200
$P m4-n11  L1,L2      3 --sel unsat:10,sat:2 --timeout 1200
$P m5-n7   L1,L2,full 3 --sel unsat:10,sat:1 --timeout 1200
