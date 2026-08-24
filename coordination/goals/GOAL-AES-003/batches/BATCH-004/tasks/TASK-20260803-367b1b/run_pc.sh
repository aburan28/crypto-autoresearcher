#!/bin/bash
cd "$(dirname "$0")"
S=$(date +%s.%N)
timeout 400 ./sq_slot attack6n 2b7e151628aed2a6abf7158809cf4f3c 53787ef6b300ea19f0a43d4915afd440 6 2 90009 2 0 mask > runs/PC-TRUE.json 2> runs/PC-TRUE.err
E=$?
T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
echo "PC-TRUE exit=$E wall=$T" >> runs/arms_timing.txt
echo "PC-TRUE ./sq_slot attack6n 2b7e151628aed2a6abf7158809cf4f3c 53787ef6b300ea19f0a43d4915afd440 6 2 90009 2 0 mask" >> runs/commands.txt
