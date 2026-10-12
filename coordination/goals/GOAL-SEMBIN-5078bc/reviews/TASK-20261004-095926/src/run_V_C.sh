#!/bin/bash
# how to reproduce: bash src/run_V_C.sh  (from out/; after run_V.sh).  Mode C = direct term evaluation per assignment.
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2}
for f in $(find ../experiments -name '*.ms' | sort); do
  b=$(basename $f .ms)
  N=$(head -1 corpus/masks/$b.masks | cut -d' ' -f1); k=$((N/2))
  echo "== $b" > results/V/$b.C1.txt
  python3 src/timed.py src/count_solutions C corpus/masks/$b.masks 0 $k >> results/V/$b.C1.txt 2>&1
  echo "== $b" > results/V/$b.C2.txt
  python3 src/timed.py src/count_solutions C corpus/masks/$b.masks $k $k >> results/V/$b.C2.txt 2>&1
done
echo DONE > results/V/C_done.flag
