#!/bin/bash
cd "$(dirname "$0")"
P="python3 pilot4.py"
$P pre n9-poly full --sel unsat:20,sat:8
$P pre m4-n7 full
$P win m4-n7 w2
$P pre n11-poly full --sel unsat:10,sat:5
$P win m4-n9 w2 --sel unsat:10,sat:4
$P pre m4-n9 full --sel unsat:10,sat:4
$P win m5-n9k3 w2 --sel unsat:5,sat:3 --timeout 1800
$P win m4-n11 w2 --sel unsat:10,sat:2 --timeout 1800
$P pre m5-n9k3 L2 --sel unsat:5,sat:3 --timeout 2400
echo LANE_A_DONE
