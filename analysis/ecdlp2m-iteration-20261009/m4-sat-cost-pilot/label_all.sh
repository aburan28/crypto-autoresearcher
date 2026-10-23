#!/bin/sh
LAB=/home/user/crypto-autoresearcher/analysis/ecdlp2m-iteration-20261009/m4-sat-cost-pilot/label.py
for c in "3 13 4" "4 15 4" "4 17 3" "4 17 4" "3 17 5" "3 19 6" "4 19 5" "4 17 5" "3 23 7" "3 23 5" "3 23 6" "4 23 4" "4 23 5" "4 23 6"; do
  set -- $c
  echo "=== cell m$1 n$2 k$3 $(date +%T)"
  python3 $LAB $1 $2 $3 14 2>&1 | grep -v "^  "
done
echo DONE
