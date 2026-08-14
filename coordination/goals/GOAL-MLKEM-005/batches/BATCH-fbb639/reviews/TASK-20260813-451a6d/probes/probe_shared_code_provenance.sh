#!/usr/bin/env bash
# probe_shared_code_provenance.sh -- TASK-20260813-451a6d (Validator)
#
# Addresses the task envelope's explicit instruction: "if D_route is
# genuinely 0.0 at every covered cell (bit-identical routes), that is a
# STRONG and somewhat surprising claim... Build your own null or check to
# see whether this is plausible, or whether it suggests the two
# 'independent' routes are less independent than PREREG-3 assumed (e.g. one
# transcribing the other, or both computing the same quantity through the
# same code path despite being filed as separate sources)."
#
# This probe traces the PROVENANCE of the core numerical kernel that
# produces lam1n/hkz (hkz_profile, and the basis-construction helpers
# make_A/build_basis) across the three scripts PREREG-3 names as ROUTE-P
# and ROUTE-I sources:
#   measure_am4.py       (BATCH-cbe023,  results_am4.json  -- ROUTE-I @ L9/L11)
#   measure_relvar.py    (BATCH-9e3584,  results_relvar.json -- ROUTE-P, all cells)
#   replicate_l7l8.py    (BATCH-4ed139,  results_l7l8.json -- ROUTE-I @ L7)
#
# by (a) grepping each file's own docstrings for explicit provenance
# statements, and (b) diffing the actual function bodies line-for-line.

set -u
cd /home/user/crypto-autoresearcher

AM4=coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/measure_am4.py
RELVAR=coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
L7L8=coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/replicate_l7l8.py

echo "=== 1. explicit provenance statements (grep for 'CARRIED VERBATIM') ==="
echo "--- measure_am4.py (the earliest of the three, BATCH-cbe023) ---"
grep -n "CARRIED VERBATIM\|def hkz_profile\|def make_A\|def build_basis" "$AM4"
echo "--- measure_relvar.py (BATCH-9e3584) ---"
grep -n "CARRIED VERBATIM\|def hkz_profile\|def make_A\|def build_basis" "$RELVAR"
echo "--- replicate_l7l8.py (BATCH-4ed139, PREREG-3's own ROUTE-I source for L7) ---"
grep -n "CARRIED VERBATIM\|def hkz_profile\|def make_A\|def build_basis" "$L7L8"

echo
echo "=== 2. line-for-line diff of hkz_profile's function body across the three files ==="
sed -n '/^def hkz_profile/,/^def [a-z]/p' "$AM4" | head -n -1 > /tmp/hkz_am4.txt
sed -n '/^def hkz_profile/,/^def [a-z]/p' "$RELVAR" | head -n -1 > /tmp/hkz_relvar.txt
sed -n '/^def hkz_profile/,/^def [a-z]/p' "$L7L8" | head -n -1 > /tmp/hkz_l7l8.txt
echo "--- diff: measure_am4.py vs measure_relvar.py (blank = identical body, up to docstring/formatting) ---"
diff /tmp/hkz_am4.txt /tmp/hkz_relvar.txt
echo "--- diff: measure_relvar.py vs replicate_l7l8.py (blank = identical body) ---"
diff /tmp/hkz_relvar.txt /tmp/hkz_l7l8.txt

echo
echo "=== 3. line-for-line diff of make_A (the basis-construction seed formula) ==="
sed -n '/^def make_A/,/^def [a-z]/p' "$AM4" | head -n -1 > /tmp/makeA_am4.txt
sed -n '/^def make_A/,/^def [a-z]/p' "$RELVAR" | head -n -1 > /tmp/makeA_relvar.txt
sed -n '/^def make_A/,/^def [a-z]/p' "$L7L8" | head -n -1 > /tmp/makeA_l7l8.txt
echo "--- diff: measure_am4.py vs measure_relvar.py ---"
diff /tmp/makeA_am4.txt /tmp/makeA_relvar.txt
echo "--- diff: measure_relvar.py vs replicate_l7l8.py ---"
diff /tmp/makeA_relvar.txt /tmp/makeA_l7l8.txt

echo
echo "=== 4. rawtail's own kernel (raw_gso_logs / x_rawtail_of), for comparison: is IT also shared? ==="
echo "(context: PREREG-3 itself excludes TASK-20260812-56b9da's rawtail recomputation as"
echo " non-independent because its own report says these functions were transcribed verbatim."
echo " Checking whether the SAME transcription pattern silently underlies the lam1n/hkz"
echo " comparison, which PREREG-3 does NOT flag as sharing code.)"
grep -n "def raw_gso_logs\|def x_rawtail_of\|CARRIED VERBATIM\|TRANSCRIBED" "$RELVAR" \
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/measure_gvar2.py

echo
echo "=== 5. environments the two 'routes' actually differ in, per report_c3lane.md's own text ==="
grep -n "environment\|macOS\|Linux\|numpy\|scipy\|Python 3" \
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/report_c3lane.md \
  coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/run_manifest.yaml \
  | grep -i "environment\|host\|os\|python_version\|numpy_version\|scipy_version" | head -20

echo
echo "=== 6. contrast: near-machine-epsilon (NOT bit-identical) residuals elsewhere in this corpus,"
echo "    where the compared quantities are ALGEBRAICALLY related but NOT the same code path ==="
python3 -B -c "
import json
relvar = json.load(open('coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/results_relvar.json'))
fa = relvar['forced_arithmetic']
for k in ('rdet_T1_ambient_isometry_residual', 'rdet_T2_permutation_residual', 'rdet_T3_unimodular_residual', 'rawtail_T1_ambient_isometry_residual_beta5'):
    print(' ', k, '=', fa.get(k))
"
