#!/bin/bash
# Dose-response of block product loss (mutant MJ): drop LEN consecutive products at NPOS positions of one iteration.
. $(dirname $0)/00_env.sh
cd $SP/work
SD="python3 $WS/scripts/w5_singledrop.py out/dose.jsonl"
for LEN in 1 10 100 1000 5000; do
  $SD chained_n9_m3_t3_k4_d0 3 6 0.0265228 0.0530455 1 $LEN
  $SD chained_n9_m3_t3_k4_d0 2 6 0.0265228 0.0530455 1 $LEN
  $SD null_n16_m2_t2_k8_d0 2 6 0.0029501 0.0088503 1 $LEN
  $SD null_n16_m2_t2_k8_d0 1 6 0.0029501 0.0088503 1 $LEN
  $SD chained_n16_m2_t2_k8_d0 2 6 0.0029501 0.0088503 1 $LEN
done
echo DOSE_DONE
