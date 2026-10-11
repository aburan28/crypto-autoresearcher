#!/bin/bash
cd "$(dirname "$0")"
export KEEP_LOGS=1 CLOSURE_VERBOSE=1
python3 pilot.py run n19-poly M4,W3 1 4 --sel unsat:2,sat:0
python3 pilot.py run n19-poly W4 1 7.5 --sel unsat:2,sat:0 --timeout 4800
