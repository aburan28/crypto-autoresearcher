#!/bin/bash
# PILOT #2 driver A4 (replaces A3, same wait): one worker, large cells, serial.
cd "$(dirname "$0")"
while kill -0 4991 2>/dev/null; do sleep 15; done
P="python3 pilot2.py run"
$P m5-n9 W4 1 6.5 --sel unsat:1 --timeout 3600
$P m5-n9k3 W4 1 6.5 --sel unsat:1 --timeout 5400
$P m4-n11 W4 1 6.5 --sel unsat:6,sat:2 --timeout 4200
$P m5-n9 W4 1 6.5 --sel unsat:2 --timeout 3600
$P m5-n9k3 W4 1 6.5 --sel unsat:1,sat:1 --timeout 5400
$P m4-n11 W4 1 6.5 --sel unsat:12,sat:4 --timeout 4200
