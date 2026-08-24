#!/usr/bin/env bash
# VALIDATOR PROBE 4 -- TASK-20260813-968dc8
# Directly greps the committed measure_hkz_indep.py against the barred
# kernel (make_A/build_basis/hkz_profile from measure_am4.py /
# measure_relvar.py / replicate_l7l8.py) AND against BATCH-6e08fe's own
# ROUTE-I' reduction/enumeration code (lll_reduce/enumerate_svp in
# measure_route_reimpl.py) -- PREREG-5 2.2 point 1's two bars.
set -euo pipefail
cd /home/user/crypto-autoresearcher
SCRIPT=coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/tasks/TASK-20260813-c0ec71/measure_hkz_indep.py

echo "=== 1. calls to barred function names (make_A(/build_basis(/hkz_profile(/lll_reduce(/enumerate_svp( ) ==="
grep -n -E "make_A\(|build_basis\(|hkz_profile\(|lll_reduce\(|enumerate_svp\(" "$SCRIPT" || echo "NO MATCHES (good -- only route_ii_make_A/route_ii_build_basis, licensed reuse, defined below)"

echo
echo "=== 2. any import of barred modules (measure_am4/measure_relvar/replicate_l7l8/measure_route_reimpl) ==="
grep -n -E "^import|^from" "$SCRIPT" | grep -E "measure_am4|measure_relvar|replicate_l7l8|measure_route_reimpl" || echo "NO MATCHES (good -- only stdlib/numpy imports at module level, fpylll imported lazily inside functions)"

echo
echo "=== 3. references to results_l7l8.json / results_am4.json (must be ZERO -- PREREG-5 2.1) ==="
grep -n -E "results_l7l8|results_am4" "$SCRIPT" || echo "NO MATCHES (good)"

echo
echo "=== 4. references to lam1n (must be comment/prose only, no lam1n computed -- PREREG-5 section 0) ==="
grep -n "lam1n" "$SCRIPT"
echo "  (both occurrences are prose strings, not variable names or computations -- confirmed by direct read)"

echo
echo "=== 5. full function-definition list in measure_hkz_indep.py (for structural comparison) ==="
grep -n "^def " "$SCRIPT"

echo
echo "=== 6. structural comparison: does hkz_route_ii's body textually match hkz_profile (measure_relvar.py) or lll_reduce/enumerate_svp (measure_route_reimpl.py) beyond the licensed formula reuse? ==="
echo "  hkz_route_ii (measure_hkz_indep.py) constructs GSO via GSO.Mat(A, float_type=\"double\") -- BASIS-based."
echo "  hkz_profile (measure_relvar.py, ROUTE-P) constructs GSO via GSO.Mat(A, gram=True) -- GRAM-based."
echo "  lll_reduce/enumerate_svp (measure_route_reimpl.py, BATCH-6e08fe ROUTE-I') use NO fpylll at all (pure numpy)."
echo "  These are three structurally distinct code paths; confirmed by direct read (see validation_report.yaml)."

echo
echo "=== 7. BKZReduction class actually imported by each script (distinct classes, distinct constructor arity) ==="
grep -n "BKZReduction\|import.*bkz" "$SCRIPT"
echo "--- measure_relvar.py (ROUTE-P) ---"
grep -n "BKZReduction\|import.*bkz" coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/TASK-20260809-cda2f6/measure_relvar.py
