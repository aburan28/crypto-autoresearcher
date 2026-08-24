#!/usr/bin/env python3
"""
Independent Validator probe: root-cause investigation of the
ReductionError('infinite loop in babai') failure reported by
TASK-20260814-ffd791's own stage0_feasibility.py::worker_main_cell.

HYPOTHESIS UNDER TEST: stage0_feasibility.py constructs
`BKZReduction(A)` from a raw fpylll.IntegerMatrix `A` (already
LLL-reduced by the top-level `LLL.reduction(A)` convenience function,
which defaults to method='wrapper' -- fplll's own automatic,
precision-ADAPTIVE strategy that escalates from double to long-double/
dpe/mpfr as needed). fpylll's own BKZReduction.__init__
(fpylll/algorithms/bkz.py, inherited by bkz2.BKZReduction), when given a
plain IntegerMatrix (not a pre-built GSO.Mat/LLL.Reduction object),
builds its OWN internal GSO via `GSO.Mat(A, flags=GSO.ROW_EXPO)` --
NOTE: no float_type argument is passed, so GSO.Mat's own DEFAULT
`float_type='double'` (53-bit) is used, WITHOUT the wrapper method's
precision escalation. This is a DIFFERENT (lower, fixed) precision
regime than the outer LLL.reduction(A) call that just succeeded on the
same matrix. If BKZReduction's own internal LLL/babai re-run then fails
with insufficient (fixed double) precision at this dimension, that is a
PARAMETER-CONSTRUCTION issue in how the producer's script invokes
fpylll's API (it does not pass an explicit higher-precision GSO to
BKZReduction), not necessarily an intrinsic fplll library limitation.

This probe tests three regimes on the IDENTICAL basis/seed as the
producer's own cell:
  (a) EXACT REPRODUCTION: BKZReduction(A) from a raw IntegerMatrix, as
      the producer's script does -- expected to fail (see
      probe_reproduce_cell.py for confirmation).
  (b) BKZReduction constructed from an explicit GSO.Mat(A,
      float_type='mpfr', precision=<explicit high value>) -- tests
      whether raising precision explicitly (unlike the producer's own
      out-of-band float_type='mpfr' diagnostic, which per environment.json
      did not report an explicit precision value) avoids the error.
  (c) BKZReduction constructed from an explicit GSO.Mat(A,
      float_type='long double') -- a cheaper higher-precision-than-double
      option that does not require MPFR's own extra overhead.

Usage: python3 probe_root_cause_precision.py <d> <beta> [precision_bits]
"""
import json
import sys
import time
import traceback

import numpy as np

SEED_ROOT = 715923


def try_regime(name, build_bkz_fn, d, beta, seed, strategies_path, timeout_note=""):
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL

    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
    t0 = time.time()
    LLL.reduction(A)
    lll_elapsed = time.time() - t0

    par = BKZ.Param(block_size=beta, strategies=strategies_path, flags=BKZ.AUTO_ABORT)
    out = {"regime": name, "d": d, "beta": beta, "seed_used": seed, "lll_elapsed_seconds": lll_elapsed}
    try:
        t1 = time.time()
        bkz = build_bkz_fn(A)
        construct_elapsed = time.time() - t1
        t2 = time.time()
        bkz(par, tracer=True)
        out["status"] = "COMPLETED"
        out["bkz_construct_seconds"] = construct_elapsed
        out["bkz_call_seconds"] = time.time() - t2
    except Exception as exc:
        out["status"] = "ERROR"
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["total_elapsed_since_lll"] = time.time() - t0
    return out


def main(d, beta, precision_bits):
    from fpylll import IntegerMatrix, LLL, BKZ, FPLLL, GSO
    from fpylll.algorithms.bkz2 import BKZReduction
    import os

    strategies_path = "/usr/share/libfplll8/strategies/default.json"
    if not os.path.exists(strategies_path):
        strategies_path = BKZ.DEFAULT_STRATEGY

    seed = int(np.random.default_rng([SEED_ROOT, 0, d, beta, 0, 0]).integers(0, 2 ** 31 - 1))

    results = []

    # (a) exact reproduction: raw IntegerMatrix -> BKZReduction's own default
    # internal GSO (float_type='double', unconditionally).
    def build_a(A):
        return BKZReduction(A)
    results.append(try_regime("a_raw_integermatrix_default_double_gso", build_a, d, beta, seed, strategies_path))

    # (b) explicit high-precision mpfr GSO passed to BKZReduction.
    def build_b(A):
        M = GSO.Mat(A, flags=GSO.ROW_EXPO, float_type="mpfr", precision=precision_bits)
        M.update_gso()
        L = LLL.Reduction(M, flags=LLL.DEFAULT)
        return BKZReduction(L)
    results.append(try_regime("b_explicit_mpfr_gso_precision_%d" % precision_bits, build_b, d, beta, seed, strategies_path))

    # (c) explicit long double GSO passed to BKZReduction.
    def build_c(A):
        M = GSO.Mat(A, flags=GSO.ROW_EXPO, float_type="long double")
        M.update_gso()
        L = LLL.Reduction(M, flags=LLL.DEFAULT)
        return BKZReduction(L)
    results.append(try_regime("c_explicit_long_double_gso", build_c, d, beta, seed, strategies_path))

    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    d = int(sys.argv[1])
    beta = int(sys.argv[2])
    precision_bits = int(sys.argv[3]) if len(sys.argv) > 3 else 212
    out = main(d, beta, precision_bits)
    with open("probe_root_cause_precision_d%d_beta%d.json" % (d, beta), "w") as f:
        json.dump(out, f, indent=2)
