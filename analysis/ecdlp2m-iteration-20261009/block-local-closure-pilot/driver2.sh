#!/bin/sh
# PILOT #3 extension driver (as run, after driver.sh): cells beyond the request, local
# variants only, where the full W_4 was infeasible in pilot #2 (m=5 n=9 k=3: 124,314
# columns) or had only 2 UNSAT instances (m=4 n=11). Trimmed to the remaining wall budget.
cd "$(dirname "$0")"
P="python3 pilot3.py run"
$P m5-n9k3 L1  3 --sel unsat:10,sat:3 --timeout 600
$P m4-n11  L1  3 --sel unsat:10,sat:2 --timeout 600
$P m5-n9k3 L2  3 --sel unsat:5,sat:0  --timeout 600
$P m4-n11  L2  3 --sel unsat:5,sat:0  --timeout 600
