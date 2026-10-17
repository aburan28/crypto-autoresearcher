#!/bin/sh
# second labelling pass (m4 k=6 dropped: infeasible for WDSat within the budget)
LAB=/home/user/crypto-autoresearcher/analysis/ecdlp2m-iteration-20261009/m4-sat-cost-pilot/label.py
for c in "4 17 5 12" "3 23 7 14" "3 23 5 14" "3 23 6 14" "4 23 4 14" "4 23 5 10"; do
  set -- $c
  echo "=== cell m$1 n$2 k$3 $(date +%T)"
  python3 $LAB $1 $2 $3 $4 2>&1 | grep -v "^  "
done
echo DONE
