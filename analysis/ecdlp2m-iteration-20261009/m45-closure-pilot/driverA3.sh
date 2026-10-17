#!/bin/bash
# PILOT #2 driver A3: waits for the orphaned m4-n11 W4 job (pid 4991, 3 jobs: 2 UNSAT + 1 SAT), then
# the m=5 k=3 probe above the column guidance, flagged; then more m4-n11 W4 if time remains.
cd "$(dirname "$0")"
while kill -0 4991 2>/dev/null; do sleep 15; done
P="python3 pilot2.py run"
$P m5-n9k3 W4 1 6.5 --sel unsat:1 --timeout 5400
$P m4-n11 W4 1 6.5 --sel unsat:4,sat:1 --timeout 4200
$P m5-n9k3 W4 1 6.5 --sel unsat:1,sat:1 --timeout 5400
