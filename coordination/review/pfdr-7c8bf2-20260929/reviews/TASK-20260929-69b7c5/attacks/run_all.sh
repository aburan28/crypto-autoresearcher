#!/bin/sh
# Re-run every red-team computation of TASK-20260929-69b7c5 in the order used.
# j6_alternatives.py reads out/j4_lower_order.json, so j4_lower_order.py runs first.
set -e
cd "$(dirname "$0")"
for s in check_pipeline.py j4_coverage.py j4_lower_order.py j6_p7c.py j6_alternatives.py \
         j5_rho.py ptm_design_null.py j4_lack_of_fit.py j4_range_scan.py j6_q_lambda.py \
         j4_seed_dependence.py; do
  sh run.sh "$s" > /dev/null
  echo "done $s"
done
