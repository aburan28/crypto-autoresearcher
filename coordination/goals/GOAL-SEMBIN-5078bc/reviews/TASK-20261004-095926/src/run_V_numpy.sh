#!/bin/bash
# how to reproduce: bash src/run_V_numpy.sh (from out/).  Method D (NumPy) for |V|, both role assignments, all twelve.  Output results/V/<name>.D1.txt/.D2.txt
cd "$(dirname "$0")/.."
for f in $(find ../experiments -name '*.ms' | sort); do
  b=$(basename $f .ms)
  python3 src/count_numpy.py $f 17 > results/V/$b.D1.txt
  python3 src/count_numpy.py $f 17 --roles2 > results/V/$b.D2.txt
done
echo DONE > results/V/D_done.flag
