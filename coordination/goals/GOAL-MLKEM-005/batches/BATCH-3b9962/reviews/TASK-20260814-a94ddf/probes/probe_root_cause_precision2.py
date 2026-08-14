#!/usr/bin/env python3
"""
Independent Validator probe, round 2: correct the API-usage error found in
probe_root_cause_precision.py's regime (b) (GSO.Mat has no `precision=`
kwarg -- MPFR precision is set GLOBALLY via fpylll.FPLLL.set_precision(bits),
which defaults to 53 bits, i.e. IDENTICAL to 'double' precision, unless
raised explicitly). Confirms fpylll.FPLLL.get_precision() == 53 by default
(checked directly in this environment, see probes/precision_default_check.txt)
-- meaning a bare float_type='mpfr' switch, with no explicit
FPLLL.set_precision() call beforehand, does NOT raise precision above
'double' at all. This is exactly the scenario TASK-20260814-ffd791's own
out-of-band diagnostic (environment.json stage0_infrastructure_finding)
appears to have run: "float_type_mpfr: FAILED -- identical ReductionError,
effectively instantly" is consistent with mpfr running at the SAME 53-bit
precision as double, not with mpfr at genuinely higher precision failing.

Usage: python3 probe_root_cause_precision2.py <d> <beta> [precision_bits]
"""
import json
import sys
import time

import numpy as np

SEED_ROOT = 715923


def try_regime(name, build_bkz_fn, d, beta, seed, strategies_path):
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
        M = bkz.M
        log_det = M.get_log_det(0, d)
        r0 = M.get_r(0, 0)
        import math
        delta_0 = ((r0 ** 0.5) / math.exp(log_det / d)) ** (1.0 / d)
        out["delta_0_root_hermite_factor"] = delta_0
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
    default_precision = FPLLL.get_precision()
    results.append({"default_mpfr_precision_bits_before_any_set_precision_call": default_precision})

    # (b2) explicit MPFR precision RAISED globally via FPLLL.set_precision()
    # BEFORE constructing the mpfr GSO -- the corrected regime.
    def build_b2(A):
        FPLLL.set_precision(precision_bits)
        M = GSO.Mat(A, flags=GSO.ROW_EXPO, float_type="mpfr")
        M.update_gso()
        L = LLL.Reduction(M, flags=LLL.DEFAULT)
        return BKZReduction(L)
    results.append(try_regime("b2_mpfr_gso_global_precision_%d_bits" % precision_bits, build_b2, d, beta, seed, strategies_path))
    # restore default precision for subsequent regimes in this process
    FPLLL.set_precision(53)

    # (d) same as (b2) but at an even higher precision, to bound how much is
    # actually required.
    def build_d(A):
        FPLLL.set_precision(precision_bits * 2)
        M = GSO.Mat(A, flags=GSO.ROW_EXPO, float_type="mpfr")
        M.update_gso()
        L = LLL.Reduction(M, flags=LLL.DEFAULT)
        return BKZReduction(L)
    results.append(try_regime("d_mpfr_gso_global_precision_%d_bits" % (precision_bits * 2), build_d, d, beta, seed, strategies_path))
    FPLLL.set_precision(53)

    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    d = int(sys.argv[1])
    beta = int(sys.argv[2])
    precision_bits = int(sys.argv[3]) if len(sys.argv) > 3 else 212
    out = main(d, beta, precision_bits)
    with open("probe_root_cause_precision2_d%d_beta%d.json" % (d, beta), "w") as f:
        json.dump(out, f, indent=2)
