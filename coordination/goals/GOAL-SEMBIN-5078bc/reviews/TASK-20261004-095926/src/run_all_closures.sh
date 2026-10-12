#!/bin/bash
# how to reproduce: bash src/run_all_closures.sh   (from out/; after run_V.sh).  Runs the closure on the twelve systems in order of
# increasing N (then file name), 3 threads, address-space cap 10 GB.  Output: results/closure/<name>.{closure.json,lm,closure.log,run.txt}
cd "$(dirname "$0")/.."
ulimit -v 10485760
export OMP_NUM_THREADS=3
for f in $(for g in $(find ../experiments -name '*.ms'); do echo "$(head -1 $g | tr ',' '\n' | wc -l) $g"; done | sort -k1,1n -k2,2 | cut -d' ' -f2); do
  python3 src/run_instance.py $f results/closure 3
done
echo DONE > results/closure/ALL_DONE.flag
