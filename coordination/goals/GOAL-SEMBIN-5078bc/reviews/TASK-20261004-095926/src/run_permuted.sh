#!/bin/bash
# how to reproduce: bash src/run_permuted.sh  (from out/).  Representation-independence check: variables relabelled by a seeded random permutation; the closure (different column order, different
# product patterns, different batches) must give the same rank and verdict class, and every final row must vanish at the permuted zeros.  Output results/permuted/
cd "$(dirname "$0")/.."
ulimit -v 10485760
mkdir -p results/permuted
for b in ch_n41_m2_t2_k21_low_B_ran_s20260913101_d0 ch_n40_m2_t2_k20_low_B_ran_s20260913102_d1 ch_n44_m2_t2_k22_low_B_ran_s20260913101_d5 ch_n45_m2_t2_k23_low_B_ran_s20260913101_d0; do
  python3 src/permute_masks.py results/closure/$b.masks results/permuted/$b.masks 20261005 results/V/$b.solutions_E1.txt results/permuted/$b.sol
  python3 src/timed.py src/closure_v results/permuted/$b.masks -t 3 -B 96 -V results/permuted/$b.sol -q -o results/permuted/$b > results/permuted/$b.json 2> results/permuted/$b.run.txt
done
echo DONE > results/permuted/DONE.flag
