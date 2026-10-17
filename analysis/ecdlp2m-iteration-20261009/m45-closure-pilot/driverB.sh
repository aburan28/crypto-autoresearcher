#!/bin/bash
# PILOT #2 driver B: two workers, the small/medium cells. Logged to logs/driverB.log
cd "$(dirname "$0")"
P="python3 pilot2.py run"
$P m4-n7 M3,M4,W3,W4,myM4,myW4 2 3 --sel unsat:25,sat:4
$P m4-n7 M5,W5,myW5 2 3 --sel unsat:25,sat:4
$P m4-n7 M3,M4,W3,W4,W5,myW4 2 3 --sel unsat:0,sat:0,null:12,null2:12,nullonly:1
$P m5-n7 M3,W3 2 3 --sel unsat:28,sat:1
$P m4-n9 M3,W3 2 3 --sel unsat:30,sat:10
$P m5-n7 M4,W4 2 3.5 --sel unsat:12,sat:1
$P m4-n9 M4,W4 2 3.5 --sel unsat:12,sat:4
$P m5-n7 W4 2 3.5 --sel unsat:0,sat:0,null:6,null2:6,nullonly:1
$P m4-n9 W4 2 3.5 --sel unsat:0,sat:0,null:6,null2:6,nullonly:1
$P m5-n7 myW4 2 3.5 --sel unsat:3,sat:1
$P m4-n9 myW4 2 3.5 --sel unsat:3,sat:1
$P m5-n7 M4,W4 2 3.5 --sel unsat:20,sat:1
$P m4-n9 M4,W4 2 3.5 --sel unsat:20,sat:6
$P m4-n13 M3,W3 2 3 --sel unsat:30,sat:10
$P m5-n11 M3,W3 2 3 --sel unsat:30,sat:7
