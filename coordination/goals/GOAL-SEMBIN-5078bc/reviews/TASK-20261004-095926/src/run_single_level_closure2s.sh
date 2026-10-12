#!/bin/bash
# how to reproduce: bash src/run_single_level_closure2s.sh NAME...  Independent (closure2s -s) literal single-level span on real window systems.
cd "$(dirname "$0")/.."
ulimit -v 6291456
mkdir -p results/single_level2
for b in "$@"; do
  nice -n 10 python3 src/timed.py src/closure2s results/closure/$b.masks -s -o results/single_level2/$b > results/single_level2/$b.json 2> results/single_level2/$b.run.txt
done
