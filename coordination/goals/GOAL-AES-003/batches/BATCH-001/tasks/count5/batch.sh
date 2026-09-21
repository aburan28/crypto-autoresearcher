#!/bin/bash
cd /tmp/claude-0/-home-user-crypto-autoresearcher/42d1537b-7158-5124-bdad-0c8e3df17d46/scratchpad/count5
g(){ echo "GROUP $* @ $(date -u +%H:%M:%S)"; for c in "$@"; do python3 driver.py $c & done; wait; echo "DONE @ $(date -u +%H:%M:%S)"; }
g "r4 0 1" "r3 0 1" "r5 0 1"
g "r5 1 2" "r5 2 3" "r5 3 4"
g "r5 4 5" "r5 5 6" "r6 0 1"
g "nulls sibling 0 1" "nulls randperm 0 1" "r6 1 2"
g "r5 6 7" "r5 7 8" "nulls indeprk 0 1"
g "r6 2 3" "nulls randpt 0 1" "r5 8 9"
