#!/bin/sh
# PILOT #3 driver, as run (one worker process at a time, 3 GB RSS cap, 20 min per job).
cd "$(dirname "$0")"
P="python3 pilot3.py run"
$P n9-poly  full,L1,adj0,adj1            3 --sel unsat:60,sat:8   --timeout 1200
$P m4-n7    L1,L2,full,adj0,adj1,L1adj0  3 --sel unsat:25,sat:4   --timeout 1200
$P n11-poly L1,full,adj1                 3 --sel unsat:20,sat:10  --timeout 1200
$P m4-n9    L1,L2,full                   3 --sel unsat:10,sat:4   --timeout 1200
$P m4-n9    adj1,L2adj1                  3 --sel unsat:10,sat:4   --timeout 1200
