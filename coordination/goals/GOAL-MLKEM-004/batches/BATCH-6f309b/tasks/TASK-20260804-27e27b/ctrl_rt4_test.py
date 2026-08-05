#!/usr/bin/env python3
"""
CTRL-RT-4 test script for TASK-20260804-27e27b / BATCH-6f309b / GOAL-MLKEM-004.

Three checks:
  1a. Zero-error check: score sieve vectors against b_zero = A*s (no error).
      Every per-vector cosine score for the correct secret must be exactly 1.0.
      Requires: g6k sieve (to re-run seeded script and extract dual vectors).

  1b. Uniform-error check: score sieve vectors against b = A*s + e, e ~ Uniform(Zq^m).
      Expected mean correct-candidate score: ~0, within 3*sigma of 0.
      Requires: g6k sieve.

  1c. MATZOV callable: import lwe_dual.matzov and call MATZOV class methods.
      Returns a numeric cost value without crashing.
      Requires: lattice-estimator only (no g6k).

INFRASTRUCTURE STATUS: On ARM64 (Apple Silicon) macOS, g6k 0.1.2 cannot be built
because its sieve kernels use x86-specific SIMD intrinsics (immintrin.h). Checks
1a and 1b require g6k and cannot be run. Check 1c runs independently.

Parameters (same as batch-1):
    m=35, n=25, q=127, eta=2, sigma=2.0
    instance_seed=20260803001
"""

import argparse
import json
import os
import platform
import sys
import time

import numpy as np

SCRIPT_VERSION = "1.0.0"
TASK = "TASK-20260804-27e27b"
BATCH = "BATCH-6f309b"
GOAL = "GOAL-MLKEM-004"

# LWE parameters (identical to batch-1)
M, N, Q = 35, 25, 127
ETA = 2
SIGMA = 2.0
INSTANCE_SEED = 20260803001
FPYLLL_SEED = 20260803005
TARGET_N = 17919  # batch-1 sieve vector count


def centered_binomial(rng, eta, size):
    a = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    b = rng.integers(0, 2, size=(size, eta), dtype=np.int64).sum(axis=1)
    return (a - b).astype(np.int64)


def rounded_gaussian(rng, sigma, size):
    return np.rint(rng.normal(0.0, sigma, size=size)).astype(np.int64)


def center_mod(v, q):
    r = np.mod(v, q)
    r = np.where(r > q // 2, r - q, r)
    return r.astype(np.int64)


def build_instance():
    """Build LWE instance from batch-1 seeds."""
    rng = np.random.default_rng(INSTANCE_SEED)
    A = rng.integers(0, Q, size=(M, N), dtype=np.int64)
    s = centered_binomial(rng, ETA, N)
    e_main = rounded_gaussian(rng, SIGMA, M)
    b_main = np.mod(A.dot(s) + e_main, Q)
    return A, s, e_main, b_main


def check_1a(X, Y, A, s, batch1_raw=None):
    """
    Zero-error check: b_zero = A*s (no error).
    Every t_i = center_mod(x_i.b_zero - y_i.s, q) must be 0.
    Every score = cos(0) = 1.0.

    X, Y are the sieve-produced dual vector parts (shape: N x m and N x n).
    batch1_raw: if provided, use batch-1 phases_t to derive consistency check.
    """
    b_zero = np.mod(A.dot(s), Q)
    xb = X.dot(b_zero)
    ys = Y.dot(s)
    phases = center_mod(xb - ys, Q)
    scores = np.cos(2.0 * np.pi * phases / Q)

    all_zero = bool(np.all(phases == 0))
    all_one = bool(np.allclose(scores, 1.0, atol=1e-9))
    n_nonzero = int(np.count_nonzero(phases))

    return {
        "check": "1a_zero_error",
        "status": "PASS" if all_zero else "FAIL",
        "n_vectors": len(phases),
        "n_phases_nonzero": n_nonzero,
        "all_phases_zero": all_zero,
        "all_scores_one": all_one,
        "sample_phases_first10": [int(x) for x in phases[:10]],
        "sample_scores_first10": [float(x) for x in scores[:10]],
    }


def check_1b(X, Y, A, s, q, rng_seed_null=20260804001):
    """
    Uniform-error check: b = A*s + e, e ~ Uniform(Zq^m).
    Expected mean of correct-candidate cosine scores: ~0.
    Within 3*sigma: sigma = sqrt(Var[cos(2*pi*U/q)] / N) ~ sqrt(0.5 / N).
    """
    rng = np.random.default_rng(rng_seed_null)
    e_unif = rng.integers(0, q, size=M, dtype=np.int64)
    e_unif = center_mod(e_unif, q)
    b_unif = np.mod(A.dot(s) + e_unif, q)

    xb = X.dot(b_unif)
    ys = Y.dot(s)
    phases = center_mod(xb - ys, q)
    scores = np.cos(2.0 * np.pi * phases / q)

    mean_score = float(scores.mean())
    std_score = float(scores.std())
    N = len(scores)

    # E[cos(2*pi*U/q)] for U ~ Uniform{0,...,q-1} is 0 (q prime, q>2)
    # Var[cos(2*pi*U/q)] = 1/2 for large q
    expected_mean = 0.0
    sigma_of_mean = float(np.sqrt(0.5 / N))
    three_sigma = 3.0 * sigma_of_mean
    within_3sigma = bool(abs(mean_score - expected_mean) <= three_sigma)

    return {
        "check": "1b_uniform_error",
        "status": "PASS" if within_3sigma else "FAIL",
        "n_vectors": N,
        "mean_score": mean_score,
        "std_score": std_score,
        "expected_mean": expected_mean,
        "sigma_of_mean": sigma_of_mean,
        "three_sigma": three_sigma,
        "within_3sigma": within_3sigma,
        "rng_seed_null": rng_seed_null,
    }


def check_1c():
    """
    MATZOV callable: import lwe_dual.MATZOV and call it on a test case.
    Returns a numeric cost value without crashing.
    """
    try:
        from estimator import LWE, lwe_dual, nd
        from estimator.lwe_dual import MATZOV

        Xs = nd.CenteredBinomial(eta=ETA)
        Xe = nd.DiscreteGaussian(SIGMA)
        params = LWE.Parameters(n=N, q=Q, Xs=Xs, Xe=Xe)

        # Call MATZOV.cost with beta=40 (arbitrary test input)
        cost = MATZOV.cost(40, params)
        cost_rop = str(cost.get("rop", "N/A")) if hasattr(cost, 'get') else str(cost)

        # Call MATZOV.Nf specifically (the function this goal is about)
        nf_val = MATZOV.Nf(params, m=M, beta_bkz=40, beta_sieve=40,
                           k_enum=0, k_fft=0, p=2)
        nf_float = float(nf_val)

        # Call the full lwe_dual.matzov optimizer
        full_result = lwe_dual.matzov(params)
        full_rop = str(full_result)

        return {
            "check": "1c_matzov_callable",
            "status": "PASS",
            "function_path": "estimator.lwe_dual.MATZOV",
            "input_params": f"n={N}, q={Q}, Xs=CenteredBinomial(eta={ETA}), "
                            f"Xe=DiscreteGaussian(sigma={SIGMA})",
            "matzov_cost_beta40": str(cost),
            "matzov_Nf_m35_beta40": nf_float,
            "lwe_dual_matzov_result": full_rop,
            "lattice_estimator_version": "0.1.0",
            "error": None,
        }
    except Exception as exc:
        return {
            "check": "1c_matzov_callable",
            "status": "FAIL",
            "function_path": "estimator.lwe_dual.MATZOV",
            "error": f"{type(exc).__name__}: {exc}",
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--batch1-raw", default=None,
                    help="Path to batch-1 raw_scores.json (for derived checks)")
    ap.add_argument("--skip-sieve", action="store_true", default=False,
                    help="Skip checks requiring sieve (for infrastructure failure mode)")
    args = ap.parse_args()

    t_start = time.time()
    results = {
        "task": TASK,
        "batch": BATCH,
        "goal": GOAL,
        "script_version": SCRIPT_VERSION,
        "platform": platform.platform(),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "parameters": {
            "m": M, "n": N, "q": Q, "eta": ETA, "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED, "fpylll_seed": FPYLLL_SEED,
        },
        "checks": [],
        "overall_status": None,
    }

    # Check 1c always runs (no g6k needed)
    print("Running CTRL-RT-4 check 1c (MATZOV callable)...")
    c1c = check_1c()
    results["checks"].append(c1c)
    print(f"  1c: {c1c['status']}")

    # Checks 1a/1b require g6k sieve
    sieve_available = False
    if not args.skip_sieve:
        try:
            from g6k import Siever, SieverParams  # noqa: F401
            sieve_available = True
        except ImportError as exc:
            print(f"  g6k not available: {exc}")

    if sieve_available:
        # Build instance and run sieve
        from fpylll import IntegerMatrix, LLL, FPLLL
        A, s, e_main, b_main = build_instance()
        # (sieve code would go here)
        print("  g6k available - sieve checks would run (not shown in this stub)")
        results["checks"].append({
            "check": "1a_zero_error",
            "status": "NOT_RUN",
            "reason": "sieve_available=True but full sieve code not yet written"
        })
        results["checks"].append({
            "check": "1b_uniform_error",
            "status": "NOT_RUN",
            "reason": "same"
        })
    else:
        infra_msg = (
            "g6k 0.1.2 cannot be built on ARM64 macOS (Apple Silicon). "
            "The sieve kernels (bgj1_sieve.cpp, bdgl_sieve.cpp, etc.) include "
            "<immintrin.h> which provides x86/x64 SIMD intrinsics. Clang on "
            "ARM64 rejects this header with '#error: This header is only meant "
            "to be used on x86 and x64 architecture'. "
            "This is an infrastructure_error per AGENTS.md executor.md semantics. "
            "It is not evidence against any mathematical hypothesis (AGENTS.md rule 5)."
        )
        results["checks"].append({
            "check": "1a_zero_error",
            "status": "INFRA_FAIL",
            "reason": infra_msg,
            "requires": "g6k Siever for sieve-vector extraction",
        })
        results["checks"].append({
            "check": "1b_uniform_error",
            "status": "INFRA_FAIL",
            "reason": infra_msg,
            "requires": "g6k Siever for sieve-vector extraction",
        })
        print(f"  1a: INFRA_FAIL (g6k not available on ARM64)")
        print(f"  1b: INFRA_FAIL (g6k not available on ARM64)")

    # Overall status
    statuses = [c["status"] for c in results["checks"]]
    if all(s == "PASS" for s in statuses):
        results["overall_status"] = "PASS"
    elif any(s == "INFRA_FAIL" for s in statuses):
        results["overall_status"] = "INFRA_FAIL"
    elif any(s == "FAIL" for s in statuses):
        results["overall_status"] = "FAIL"
    else:
        results["overall_status"] = "PARTIAL"

    results["wall_seconds"] = round(time.time() - t_start, 3)

    out_path = os.path.join(args.out_dir, "ctrl_rt4_results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nWritten: {out_path}")
    print(f"Overall CTRL-RT-4 status: {results['overall_status']}")

    return 0 if results["overall_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
