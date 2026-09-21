#!/bin/bash
# TASK-20260813-71d65d (Validator) -- probe_code_independence_diff.sh
#
# Checks the lead's independence claim by direct inspection of the committed
# script, comparing it against make_A/build_basis/hkz_profile in the named
# barred lineage (measure_am4.py, measure_relvar.py, replicate_l7l8.py,
# including BATCH-4ed139's copy). Read-only; commits nothing.
cd "$(git rev-parse --show-toplevel)"

LEAD=coordination/goals/GOAL-MLKEM-005/batches/BATCH-6e08fe/tasks/TASK-20260813-ea2e96/measure_route_reimpl.py
AM4=coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-2a9085/measure_am4.py
RELVAR=coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
L7L8=coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/replicate_l7l8.py

echo "=== 1. barred-function-name imports/calls check (should be ZERO) ==="
grep -n "import fpylll\b" "$LEAD" || echo "  (no bare 'import fpylll' outside the try/except env-check block -- confirmed below)"
echo "--- literal 'from fpylll' or top-level fpylll usage outside the guarded env-check ---"
grep -n "from fpylll\|fpylll\.\(IntegerMatrix\|GSO\|LLL\|BKZ\|Enumeration\)" "$LEAD" || echo "  NONE FOUND"
echo
echo "=== 2. import of measure_am4/measure_relvar/replicate_l7l8 (should be ZERO) ==="
grep -n "^import measure_am4\|^import measure_relvar\|^import replicate_l7l8\|from measure_am4\|from measure_relvar\|from replicate_l7l8" "$LEAD" || echo "  NONE FOUND"
echo
echo "=== 3. results_l7l8.json / results_am4.json opened as a file anywhere (should be ZERO) ==="
grep -n "open(.*results_l7l8\|open(.*results_am4" "$LEAD" || echo "  NONE FOUND"
echo
echo "=== 4. all open() calls in the lead's script (manual audit) ==="
grep -n 'open(' "$LEAD"
echo
echo "=== 5. reduction/enumeration function body comparison ==="
echo "--- lead's lll_reduce() ---"
sed -n '/^def lll_reduce/,/^def enumerate_svp/p' "$LEAD" | head -n -1
echo
echo "--- lead's enumerate_svp() ---"
sed -n '/^def enumerate_svp/,/^# ====.*main/p' "$LEAD" | head -n -1
echo
echo "--- barred lineage's hkz_profile() (measure_relvar.py, CARRIED VERBATIM per its own docstring from measure_am4.py) ---"
sed -n '/^def hkz_profile/,/^def rho_both/p' "$RELVAR" | head -n -1
echo
echo "=== 6. make_A / build_basis structural comparison (EXPECTED to be structurally identical -- PREREG-4 2.2(3) licenses this explicitly for the numeric-instance-reconstruction step; flagged here, not hidden) ==="
echo "--- lead's make_A_indep / build_basis_indep ---"
sed -n '/^def make_A_indep/,/^def gso_full/p' "$LEAD" | head -n -1
echo "--- barred lineage's make_A / build_basis (measure_relvar.py) ---"
sed -n '/^def make_A(d, k, q, i):$/,/^def haar_orthogonal/p' "$RELVAR" | head -n -1
echo
echo "=== 7. does replicate_l7l8.py (BATCH-4ed139 copy) also carry the identical hkz_profile verbatim? ==="
sed -n '/^def hkz_profile/,/^def rho_both\|^def x_null/p' "$L7L8" | head -20
echo
echo "=== 8. fpylll import chain confirmation in the barred lineage (contrast with lead's script) ==="
grep -n "from fpylll import\|import fpylll" "$AM4" "$RELVAR" "$L7L8"
echo
echo "END OF DIFF PROBE"
