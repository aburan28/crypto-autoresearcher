#!/bin/bash
# how to reproduce: bash src/run_V.sh   (from out/ ; needs gcc, python3). Produces results/V/*.txt
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-2}
[ -x src/count_solutions ] || gcc -O3 -march=native -fopenmp -o src/count_solutions src/count_solutions.c
for f in $(find ../experiments -name '*.ms' | sort); do
  b=$(basename $f .ms)
  python3 src/to_masks.py $f corpus/masks/$b.masks
  N=$(head -1 corpus/masks/$b.masks | cut -d' ' -f1); k=$((N/2))
  echo "== $b" > results/V/$b.A.txt
  { python3 src/timed.py src/count_solutions A corpus/masks/$b.masks 0 $k results/V/$b.solutions_E1.txt 100000 ; } >> results/V/$b.A.txt 2>&1
  echo "== $b" > results/V/$b.B.txt
  { python3 src/timed.py src/count_solutions A corpus/masks/$b.masks $k $k results/V/$b.solutions_E2.txt 100000 ; } >> results/V/$b.B.txt 2>&1
done
