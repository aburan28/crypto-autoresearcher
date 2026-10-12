#!/bin/bash
# how to reproduce: bash src/run_single_level.sh (from out/).  Literal single-level span (closure -S): raw generators g times every square-free mu with |mu| <= 4 - deg g,
# NOTHING else (no products of products).  Output results/single_level/<name>.json and .lm
cd "$(dirname "$0")/.."
ulimit -v 10485760
mkdir -p results/single_level
for f in $(find ../experiments -name '*.ms' | sort); do
  b=$(basename $f .ms)
  python3 src/timed.py src/closure results/closure/$b.masks -S -E -t 3 -q -o results/single_level/$b > results/single_level/$b.json 2> results/single_level/$b.run.txt
done
echo DONE > results/single_level/DONE.flag
