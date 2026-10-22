#!/bin/bash
cd "$(dirname "$0")"
python3 pilot4.py cap m6-n9k3 L2 --sel unsat:5,sat:2 --timeout 5400 --mem 5
echo LANE_C_DONE
