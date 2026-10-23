#!/bin/bash
# PILOT driver stage 1 (n = 9, 11, 13 + nulls). Logged to logs/driver1.log
cd "$(dirname "$0")"
P="python3 pilot.py run"
$P n9-poly M3,M4,M5,M6,W3,W4,myM4,myW4 4 3 --sel unsat:60,sat:20
$P n9-poly W5,myW5,myM5 4 3 --sel unsat:20,sat:20
$P n9-poly M3,M4,M5,W3,W4,W5,myW4 4 3 --sel unsat:0,sat:0,null:40,nullonly:1
$P n11-poly M3,M4,M5,W3,W4 4 3 --sel unsat:40,sat:15
$P n11-poly myM4,myW4 4 3 --sel unsat:20,sat:5
$P n11-poly M6 3 4 --sel unsat:10,sat:3
$P n11-poly M3,M4,M5,W3,W4 4 3 --sel unsat:0,sat:0,null:30,nullonly:1
$P n13-poly M3,M4,M5,W3,W4 4 3 --sel unsat:40,sat:10
$P n13-poly myW4 4 3 --sel unsat:5,sat:2
$P n13-poly M3,M4,W3,W4 4 3 --sel unsat:0,sat:0,null:20,nullonly:1
