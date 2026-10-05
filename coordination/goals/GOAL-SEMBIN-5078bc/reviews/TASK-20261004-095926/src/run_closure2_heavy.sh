#!/bin/bash
# how to reproduce: bash src/run_closure2_heavy.sh NAME   (from out/).  The independent second implementation (closure2 -i: dense non-reduced echelon,
# one-pivot head reduction, different column order) on one real N=40 window system; compare results/closure2/NAME.lm with results/closure/NAME.lm.
cd "$(dirname "$0")/.."
ulimit -v 4194304
b=$1
mkdir -p results/closure2
nice -n 15 python3 src/timed.py src/closure2 results/closure/$b.masks -i -o results/closure2/$b > results/closure2/$b.out 2> results/closure2/$b.err
