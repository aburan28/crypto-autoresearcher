#!/bin/bash
# second dose-response pass: larger blocks (continuation of run_doseresponse.sh)
. $(dirname $0)/00_env.sh
cd $SP/work
SD="python3 $WS/scripts/w5_singledrop.py out/dose.jsonl"
for LEN in 3000 8000 15000; do
  $SD chained_n9_m3_t3_k4_d0 2 6 0.0265228 0.0530455 2 $LEN
  $SD chained_n9_m3_t3_k4_d0 3 6 0.0265228 0.0530455 2 $LEN
  $SD null_n16_m2_t2_k8_d0 1 6 0.0029501 0.0088503 2 $LEN
  $SD null_n16_m2_t2_k8_d0 2 6 0.0029501 0.0088503 2 $LEN
  $SD chained_n16_m2_t2_k8_d0 2 6 0.0029501 0.0088503 2 $LEN
done
echo DOSE2_DONE
