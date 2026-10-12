#!/bin/bash
# how to reproduce: bash src/run_small_tests.sh   (from out/).  Re-runs the small-N validation of the instrument with logs in results/logs_small/.
cd "$(dirname "$0")/.."
export TMPDIR=${TMPDIR:-/tmp}
mkdir -p results/logs_small
L=results/logs_small
python3 src/test_parser.py > $L/test_parser.log 2>&1
python3 src/test_counters.py > $L/test_counters.log 2>&1
python3 src/check_parse_vs_python.py > $L/check_parse_vs_python.log 2>&1
python3 src/diff_c_vs_ref.py 8 12 3 > $L/diff_c_vs_ref_8_12.log 2>&1
cp results/diff_13_16.log $L/diff_c_vs_ref_13_16.log
python3 src/diff_c_vs_ref.py 17 19 2 quad cubic bilinear toeplitz > $L/diff_c_vs_ref_17_19.log 2>&1
cp results/diff_c_vs_c2_14_22.log $L/diff_c_vs_c2_14_22.log
cp results/diff_n23_24.log $L/diff_n23_24.log
python3 src/polarity_check.py 60 > $L/polarity_check.log 2>&1
python3 src/identity_check.py 40 > $L/identity_check.log 2>&1
python3 src/order_experiment.py 9 12 3 > $L/order_9_12.log 2>&1
cp results/order_13_16.log $L/order_13_16.log; cp results/order_14_18.log $L/order_14_18.log
python3 src/repro_w1_artifacts.py > $L/repro_w1_artifacts.log 2>&1
echo DONE > $L/DONE.flag
