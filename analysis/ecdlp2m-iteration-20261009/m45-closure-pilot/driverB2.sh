#!/bin/bash
# PILOT #2 driver B2 (replaces driverB; W_5 at m4-n7 deferred to the end, 2 UNSAT + 1 SAT only). Two workers.
cd "$(dirname "$0")"
P="python3 pilot2.py run"
$P m4-n7 M3,M4,W3,W4,myW4 2 3 --sel unsat:0,sat:0,null:12,null2:12,nullonly:1
$P m5-n7 M3,W3,myW3 2 3 --sel unsat:28,sat:1
$P m4-n9 M3,W3 2 3 --sel unsat:30,sat:10
$P m5-n7 M4,W4 2 3.5 --sel unsat:10,sat:1
$P m4-n9 M4,W4 2 3.5 --sel unsat:10,sat:4
$P m5-n7 W3,W4 2 3.5 --sel unsat:0,sat:0,null:6,null2:6,nullonly:1
$P m4-n9 W3,W4 2 3.5 --sel unsat:0,sat:0,null:6,null2:6,nullonly:1
$P m5-n7 myW4 2 3.5 --sel unsat:3,sat:1
$P m4-n9 myW4 2 3.5 --sel unsat:3,sat:1
$P m4-n13 M3,W3 2 3 --sel unsat:30,sat:10
$P m5-n11 M3,W3 2 3 --sel unsat:30,sat:7
$P m5-n9k3 M4 2 3.5 --sel unsat:2,sat:1 --timeout 2400
$P m5-n7 M4,W4 2 3.5 --sel unsat:20,sat:1
$P m4-n9 M4,W4 2 3.5 --sel unsat:20,sat:6
$P m4-n7 M5,W5 2 3 --sel unsat:2,sat:1 --timeout 2400
