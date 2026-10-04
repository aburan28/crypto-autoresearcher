#!/usr/bin/env bash
# TASK-20260926-59169c: rebuild every J8 output from the archived commit.
# Usage: bash run_all.sh <scratch dir outside the repository>
# Zero trials; every step under RLIMIT_AS 3 GB (capped.py); no bytecode written.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
REPO=/home/user/crypto-autoresearcher
COMMIT=a524be32e41fbbdf738276c896dfcced34a277c3
SCR=${1:?scratch dir}
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=$(dirname "$HERE")
SNAP=$SCR/snap
rm -rf "$SNAP" && mkdir -p "$SNAP"
( cd "$REPO" && git archive "$COMMIT" \
    coordination/review/certbin-20260926-089841/review-plan.yaml \
    coordination/review/certbin-20260926-089841/blind-inputs-key.json \
    coordination/review/certbin-20260926-089841/blind-phase-hygiene.yaml \
    coordination/review/certbin-20260926-089841/blind \
    coordination/review/certbin-20260926-089841/archives \
    coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf \
    coordination/review/certbin-20260926-089841/reviews/TASK-20260926-f0e5a4 \
    coordination/design/certbin-nconv-20260924/archives/TASK-20260924-40b2ca/snapshot-receipt.json \
    experiments/EXP-CERTBIN-ddfe75 ) | tar -x -C "$SNAP"
cd "$HERE"
python3 capped.py wdag_check.py
python3 capped.py cp1_verify.py --root "$SNAP" --wt "$REPO" --out cp1_verify.out.json
python3 capped.py cp3_run.py --snap "$SNAP" --out cp3_wdag_check.out.json
python3 capped.py cp3_negctl.py --snap "$SNAP" --out cp3_negctl.out.json
python3 capped.py compare.py --snap "$SNAP" --out comparison-core.json
python3 capped.py compare_selftest.py --snap "$SNAP" --work "$SCR/mut" --out compare_selftest.out.json
python3 capped.py cp4_third_counting.py --snap "$SNAP" --out cp4_third_counting.out.json
python3 capped.py cp3_witness.py --snap "$SNAP" --cp3 cp3_wdag_check.out.json --out cp3_witness.out.json
python3 capped.py floor_ceiling.py --snap "$SNAP" --out floor_ceiling.out.json
python3 capped.py extra_cell_trace.py --snap "$SNAP" --out extra_cell_trace.out.json
python3 capped.py assemble.py --snap "$SNAP" --checks "$HERE" --out "$OUT/comparison.json"
sha256sum "$OUT/comparison.json" ./*.out.json comparison-core.json
