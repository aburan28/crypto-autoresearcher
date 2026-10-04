#!/bin/sh
# Small-budget ECC2K-130 cell: guarantees a complete record (CNF size, build
# time, conflict rate, memory) even when the larger-budget cell is still running.
D=/home/user/crypto-autoresearcher/analysis/frobenius-orbit-ecc2k130
python3 $D/solve_cost_ladder.py --n 131 --targets 1 --seed 11 \
  --encoding stagew --baseline-encoding direct --order shift_first \
  --conf-budget 500 --cell-wall 2400 --gt-cap 0 --planted \
  --baseline-sample 1 --mem-gib 5.0 \
  --out $D/logs/cell_n131_smallbudget.json > $D/logs/cell_n131_smallbudget.out 2> $D/logs/cell_n131_smallbudget.err
