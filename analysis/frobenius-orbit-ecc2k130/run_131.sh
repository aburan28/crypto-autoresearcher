#!/bin/sh
# The real ECC2K-130 cell: F_2[z]/(z^131+z^13+z^2+z+1), y^2+xy=x^3+1, l'=58.
D=/home/user/crypto-autoresearcher/analysis/frobenius-orbit-ecc2k130
python3 $D/solve_cost_ladder.py --n 131 --targets 2 --seed 11 \
  --encoding stagew --baseline-encoding direct --order shift_first \
  --conf-budget 100000 --cell-wall 2100 --gt-cap 0 --planted \
  --baseline-sample 5 --mem-gib 6.0 \
  --out $D/logs/cell_n131_planted.json > $D/logs/cell_n131_planted.out 2> $D/logs/cell_n131_planted.err
python3 $D/solve_cost_ladder.py --n 131 --targets 2 --seed 13 \
  --encoding stagew --baseline-encoding direct --order shift_first \
  --conf-budget 100000 --cell-wall 3000 --gt-cap 0 \
  --baseline-sample 5 --mem-gib 6.0 \
  --out $D/logs/cell_n131_random.json > $D/logs/cell_n131_random.out 2> $D/logs/cell_n131_random.err
