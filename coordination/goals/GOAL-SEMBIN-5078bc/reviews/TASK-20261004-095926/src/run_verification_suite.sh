#!/bin/bash
# how to reproduce: bash src/run_verification_suite.sh (from out/, after run_all_closures.sh).  Re-runs closure_v (a superset build of closure.c with -V and -C)
# with a DIFFERENT batch size and thread count than the main run and writes results/verify/<name>.json:
#   - the final rows are evaluated at EVERY enumerated zero of the system (-V): violations must be 0;
#   - for the instances whose verdict is 'insufficient' the SATURATION VERIFIER (-C) re-multiplies every final row by every allowed multiplier;
#   - rank, LM counts and N_std must equal the main run (processing order / batching must not matter).
cd "$(dirname "$0")/.."
ulimit -v 10485760
mkdir -p results/verify
order="ch_n44_m2_t2_k22_low_B_ran_s20260913101_d5 ch_n45_m2_t2_k23_low_B_ran_s20260913101_d0 ch_n45_m2_t2_k23_low_B_ran_s20260913105_d4 ch_n40_m2_t2_k20_low_B_ran_s20260913102_d1 ch_n41_m2_t2_k21_low_B_ran_s20260913105_d4 ch_n42_m2_t2_k21_low_B_ran_s20260913102_d1 ch_n43_m2_t2_k22_low_B_ran_s20260913101_d0"
for b in $order; do
  extra=""
  case $b in *n44*d5|*n45*) extra="-C -B 1024";; *) extra="-B 128";; esac
  python3 src/timed.py src/closure_v results/closure/$b.masks -o results/verify/$b -t 3 -V results/V/$b.solutions_E1.txt $extra > results/verify/$b.json 2> results/verify/$b.log
done
echo DONE > results/verify/ALL_DONE.flag
