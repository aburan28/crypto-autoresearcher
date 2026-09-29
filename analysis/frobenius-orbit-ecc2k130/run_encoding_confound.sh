#!/bin/sh
# How much does the CNF encoding itself cost?  The n=131 one-hot arm can only be
# built in a staged encoding; this measures the staging penalty where the direct
# encoding is still feasible.  Run at low priority (nice) beside the main sweeps.
D=/home/user/crypto-autoresearcher/analysis/frobenius-orbit-ecc2k130
for E in direct stagew staged; do
  for O in default shift_first; do
    nice -n 19 python3 $D/solve_cost_ladder.py --n 19 --targets 4 --seed 7 \
      --encoding $E --baseline-encoding $E --order $O \
      --conf-budget 4000000 --cell-wall 1800 --gt-cap 16 --mem-gib 2.0 \
      --out $D/logs/enc_n19_${E}_${O}.json > $D/logs/enc_n19_${E}_${O}.out 2>&1
  done
done
