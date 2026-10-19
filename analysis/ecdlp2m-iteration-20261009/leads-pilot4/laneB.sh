#!/bin/bash
cd "$(dirname "$0")"
P="python3 pilot4.py"
for v in fullu2 fullu3; do $P cap n9-poly $v --sel unsat:20,sat:8; done
for v in fullu2 fullu3; do $P cap n11-poly $v --sel unsat:10,sat:5; done
for v in L1u2 L2u2 fullu2 fullu3; do $P cap m4-n7 $v; done
for v in L1u2 L2u2 L2u3; do $P cap m4-n9 $v --sel unsat:10,sat:4; done
for v in L2u2 L2u3; do $P cap m5-n9k3 $v --sel unsat:5,sat:3 --timeout 1800; done
$P cap m4-n11 L1u2 --sel unsat:10,sat:2
echo LANE_B_DONE
