#!/bin/bash
cd "$(dirname "$0")"
while kill -0 19288
22545 2>/dev/null; do sleep 10; done
P="python3 pilot.py run"
$P n9-poly M4,W3,W4 4 3 --sel unsat:0,sat:0,null2:40,nullonly:1
$P n15-poly M3,M4,W3 4 3 --sel unsat:40,sat:10
$P n15-poly W4 4 3.2 --sel unsat:20,sat:5
$P n15-poly M5 4 3 --sel unsat:8,sat:2
$P n15-poly M4,W3,W4 4 3.2 --sel unsat:0,sat:0,null:12,nullonly:1
$P n13-rand M4,W3,W4 4 3 --sel unsat:16,sat:4
$P n9-rand M4,W3,W4 4 3 --sel unsat:30,sat:6
$P n17-poly M3,M4,W3 3 3 --sel unsat:12,sat:4
$P n17-poly W4 2 5.5 --sel unsat:5,sat:1 --timeout 3000
