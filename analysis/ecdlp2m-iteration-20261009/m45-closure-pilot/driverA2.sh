#!/bin/bash
# PILOT #2 driver A2 (replaces driverA after W_3 refuted m5-n9): one worker, large cells, serial.
cd "$(dirname "$0")"
P="python3 pilot2.py run"
$P m5-n9 myM3,myW3 1 3 --sel unsat:30
$P m4-n11 M3,W3 1 3 --sel unsat:30,sat:7
$P m5-n9k3 M3,W3,myW3 1 3 --sel unsat:30,sat:10
$P m4-n11 W4 1 6.5 --sel unsat:2,sat:1 --timeout 4200
$P m5-n9 W4 1 6.5 --sel unsat:1 --timeout 5400
$P m4-n11 W4 1 6.5 --sel unsat:4,sat:1 --timeout 4200
$P m5-n9 M4 1 6.5 --sel unsat:2 --timeout 3600
