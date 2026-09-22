#!/bin/sh
# Ladder sweep: direct encoding, shift-first branching prefix, budgeted.
D=/home/user/crypto-autoresearcher/analysis/frobenius-orbit-ecc2k130
for N in 29 31 37 41; do
  python3 $D/solve_cost_ladder.py --n $N --targets 4 --seed 7 \
    --encoding direct --baseline-encoding direct --order shift_first \
    --conf-budget 4000000 --cell-wall 2400 --gt-cap 16 --mem-gib 3.5 \
    --out $D/logs/cell_n$N.json > $D/logs/cell_n$N.out 2> $D/logs/cell_n$N.err
done
