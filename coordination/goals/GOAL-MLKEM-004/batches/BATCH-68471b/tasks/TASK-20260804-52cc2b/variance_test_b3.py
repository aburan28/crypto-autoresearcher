#!/usr/bin/env python3
"""
Variance test for TASK-20260804-52cc2b / BATCH-68471b / GOAL-MLKEM-004.
Batch 3 of 6 — adequate-power chi-squared independence test (n=150).

Run 150 independent bgj1_sieve runs on the SAME LWE instance (instance_seed=20260803001)
with 150 DIFFERENT g6k Siever seeds drawn from:
    numpy.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()

For each run:
1. Re-generate the SAME LWE instance (A, s, e) from instance_seed=20260803001.
2. Re-run LLL with fpylll_seed=20260803005.
3. Run bgj1_sieve with siever_seeds[i].
4. Score the correct secret s against b = A*s + e.
5. Compute T_N_i = sum of all N correct-candidate cosine scores.

After run 0 (index 0):
- Compute single_score_var from run-0 sieve vectors (within-environment):
  single_scores = cos(2*pi * center_mod(X@b - Y@s, q) / q)
  single_score_var = np.var(single_scores, ddof=1)
  N_0 = number of sieve vectors from run 0
  independence_predicted_var = N_0 * single_score_var

After all runs:
- Compute empirical_var_TN = Var(T_N_0, ..., T_N_149) (sample variance, ddof=1).
- chi2_stat = (n_runs_completed - 1) * empirical_var_TN / independence_predicted_var
- p_value = 1 - scipy.stats.chi2.cdf(chi2_stat, df=n_runs_completed - 1)
- 95% CI for variance_ratio

Mean T_N comparison:
- batch-1 expected: 17919 * 0.42738 = 7659.3
- batch-2 mean: 7554.2
- Report whether this batch's mean is consistent with batch-2 or different.

OUTPUTS ONLY observations. States no finding. No comparison against MATZOV.Nf.
states_a_finding: false
compared_against_matzov_nf: false

INFRASTRUCTURE NOTE: This script requires g6k 0.1.2. g6k uses x86-specific SIMD
intrinsics and cannot be built on ARM64 (Apple Silicon) macOS. This script is written
correctly for execution on Linux x86_64 (the batch-1/batch-2 environment). On ARM64
it will fail at import with ImportError: No module named 'g6k'. That is an
infrastructure_error.

SEED EXPRESSION (verbatim, as pre-registered):
    numpy.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()
"""

import argparse
import hashlib
import json
import os
import platform
import resource
import sys
import time

import numpy as np
import scipy.stats

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams  # requires x86 Linux build

SCRIPT_VERSION = "1.0.0"
TASK = "TASK-20260804-52cc2b"
BATCH = "BATCH-68471b"
GOAL = "GOAL-MLKEM-004"

# ---- Frozen parameters (identical to batch-2 for everything except siever_seeds and n_runs)
M, N_LWE, Q = 35, 25, 127
D = M + N_LWE          # lattice dimension = 60
ETA = 2                # CB secret eta
SIGMA = 2.0            # error std dev
INSTANCE_SEED = 20260803001   # FIXED across all 150 runs
FPYLLL_SEED = 20260803005     # FIXED across all 150 runs
SIEVE_ALGO = "bgj1_sieve"
SIEVE_THREADS = 1
TARGET_N = 17919       # match batch-1/batch-2 expected sieve vector count

# Pre-registered seed expression (verbatim):
# numpy.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()
SIEVER_SEEDS_EXPRESSION = "numpy.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()"
SIEVER_SEEDS = np.random.default_rng(20260804001).integers(0, 2**32, size=150).tolist()

# Cross-batch reference values
BATCH1_EXPECTED_MEAN_TN = 17919 * 0.42738   # = 7659.3
BATCH2_MEAN_TN = 7554.2


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


def build_dual_basis(A, q, m, n):
    d = m + n
    B = np.zeros((d, d), dtype=np.int64)
    B[:m, :m] = np.eye(m, dtype=np.int64)
    B[:m, m:] = A
    B[m:, m:] = q * np.eye(n, dtype=np.int64)
    return B


def to_intmat(M_np):
    A = IntegerMatrix(M_np.shape[0], M_np.shape[1])
    for i in range(M_np.shape[0]):
        for j in range(M_np.shape[1]):
            A[i, j] = int(M_np[i, j])
    return A


def from_intmat(A):
    return np.array([[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
                    dtype=np.int64)


def build_instance_and_lll():
    """Build LWE instance + LLL-reduced basis; returns (A, s, e, b, Bred_fp)."""
    rng = np.random.default_rng(INSTANCE_SEED)
    A = rng.integers(0, Q, size=(M, N_LWE), dtype=np.int64)
    s = centered_binomial(rng, ETA, N_LWE)
    e = rounded_gaussian(rng, SIGMA, M)
    b = np.mod(A.dot(s) + e, Q)

    Bnp = build_dual_basis(A, Q, M, N_LWE)
    Bfp = to_intmat(Bnp)
    FPLLL.set_random_seed(FPYLLL_SEED)
    Bred_fp = LLL.reduction(Bfp)
    return A, s, e, b, Bred_fp


def run_single_sieve(Bred_fp, siever_seed):
    """Run bgj1_sieve with given seed. Returns (coeffs, Bused, N, t_sieve)."""
    g = Siever(Bred_fp, SieverParams(threads=SIEVE_THREADS), seed=siever_seed)
    g.initialize_local(0, 0, D)
    t0 = time.time()
    g.bgj1_sieve()
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    Bused = from_intmat(g.M.B)
    return coeffs, Bused, coeffs.shape[0], t_sieve


def compute_TN(coeffs, Bused, b, s, q, m, n):
    """Compute T_N = sum of cosine scores for the correct secret s.
    Also returns the per-vector scores array for variance computation."""
    V = coeffs.dot(Bused)    # N x d
    X = V[:, :m]             # N x m
    Y = V[:, m:]             # N x n
    xb = X.dot(b)
    ys = Y.dot(s)
    phases = center_mod(xb - ys, q)
    scores = np.cos(2.0 * np.pi * phases / q)
    T_N = float(scores.sum())
    return T_N, int(V.shape[0]), scores


def compute_single_score_var_from_run0(coeffs, Bused, b, s, q, m, n):
    """
    Within-environment single-score variance from run-0 sieve vectors.
    single_scores = cos(2*pi * center_mod(X@b - Y@s, q) / q)
    single_score_var = np.var(single_scores, ddof=1)
    Returns (single_score_var, single_score_mean, N_0).
    """
    V = coeffs.dot(Bused)    # N x d
    X = V[:, :m]             # N x m
    Y = V[:, m:]             # N x n
    phases = center_mod(X.dot(b) - Y.dot(s), q)
    single_scores = np.cos(2.0 * np.pi * phases / q)
    ssv = float(np.var(single_scores, ddof=1))
    ssm = float(np.mean(single_scores))
    return ssv, ssm, int(single_scores.shape[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--repo-root", default=None,
                    help="Repository root (unused in batch-3; kept for interface compatibility)")
    ap.add_argument("--n-runs", type=int, default=150,
                    help="Number of sieve runs (default: 150)")
    ap.add_argument("--mem-cap-gb", type=float, default=6.0)
    args = ap.parse_args()

    t_start = time.time()

    if args.mem_cap_gb > 0:
        cap = int(args.mem_cap_gb * (1 << 30))
        resource.setrlimit(resource.RLIMIT_AS, (cap, cap))

    log = []

    def say(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        log.append(line)

    say("variance_test_b3.py %s: %d runs, sieve=%s" % (SCRIPT_VERSION, args.n_runs, SIEVE_ALGO))
    say("TASK=%s BATCH=%s GOAL=%s" % (TASK, BATCH, GOAL))
    say("instance_seed=%d fpylll_seed=%d" % (INSTANCE_SEED, FPYLLL_SEED))
    say("siever_seeds_expression: %s" % SIEVER_SEEDS_EXPRESSION)
    say("first 5 seeds: %s" % SIEVER_SEEDS[:5])
    say("platform: %s" % platform.platform())

    # Build instance (ONCE, reuse across all runs)
    A, s, e, b, Bred_fp = build_instance_and_lll()
    say("instance built: |s|_inf=%d |e|_inf=%d" % (
        int(np.abs(s).max()), int(np.abs(e).max())))

    # 150-run variance measurement
    TN_values = []
    run_records = []
    n_runs_completed = 0

    # Within-environment single-score variance (from run 0)
    single_score_var = None
    single_score_mean_run0 = None
    N_run0 = None
    independence_predicted_var = None

    n_runs_actual = min(args.n_runs, len(SIEVER_SEEDS))

    for i in range(n_runs_actual):
        seed_i = SIEVER_SEEDS[i]
        t0_run = time.time()
        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve(Bred_fp, seed_i)
            T_N_i, n_vec, scores_i = compute_TN(coeffs, Bused, b, s, Q, M, N_LWE)
            t_run = time.time() - t0_run

            # After run 0: compute within-environment single_score_var
            if i == 0:
                single_score_var, single_score_mean_run0, N_run0 = \
                    compute_single_score_var_from_run0(coeffs, Bused, b, s, Q, M, N_LWE)
                independence_predicted_var = N_run0 * single_score_var
                say("run-0 within-env: N_0=%d single_score_mean=%.6f single_score_var=%.6f" % (
                    N_run0, single_score_mean_run0, single_score_var))
                say("independence_predicted_var = %d * %.6f = %.6f" % (
                    N_run0, single_score_var, independence_predicted_var))

            run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": n_vec,
                "T_N": T_N_i,
                "sieve_seconds": round(t_sieve, 3),
                "run_wall_seconds": round(t_run, 3),
                "valid": True,
            })
            TN_values.append(T_N_i)
            n_runs_completed += 1
            say("run %03d/%d: seed=%u N=%d T_N=%.3f sieve=%.1fs" % (
                i, n_runs_actual - 1, seed_i, n_vec, T_N_i, t_sieve))
        except Exception as exc:
            t_run = time.time() - t0_run
            say("run %03d/%d: seed=%u FAILED: %s" % (i, n_runs_actual - 1, seed_i, exc))
            run_records.append({
                "run_index": i,
                "siever_seed": seed_i,
                "N_vectors": None,
                "T_N": None,
                "error": str(exc),
                "run_wall_seconds": round(t_run, 3),
                "valid": False,
            })

    say("Completed %d/%d runs" % (n_runs_completed, n_runs_actual))

    # ---- Variance statistics
    if len(TN_values) < 2:
        say("ERROR: fewer than 2 valid runs; cannot compute variance")
        empirical_var_TN = None
        mean_TN = None
        std_TN = None
        min_TN = None
        max_TN = None
    else:
        TN_arr = np.array(TN_values, dtype=np.float64)
        empirical_var_TN = float(np.var(TN_arr, ddof=1))
        mean_TN = float(np.mean(TN_arr))
        std_TN = float(np.std(TN_arr, ddof=1))
        min_TN = float(np.min(TN_arr))
        max_TN = float(np.max(TN_arr))
        say("T_N stats: mean=%.3f std=%.3f var=%.6f min=%.3f max=%.3f" % (
            mean_TN, std_TN, empirical_var_TN, min_TN, max_TN))

    # ---- Chi-squared test
    variance_ratio = None
    chi2_stat = None
    p_value = None
    ci_lower = None
    ci_upper = None
    variance_ratio_ci = None
    chi2_df = None

    if empirical_var_TN is not None and independence_predicted_var is not None and independence_predicted_var > 0:
        df = n_runs_completed - 1
        chi2_df = df
        chi2_stat = df * empirical_var_TN / independence_predicted_var
        p_value = float(1.0 - scipy.stats.chi2.cdf(chi2_stat, df=df))
        variance_ratio = empirical_var_TN / independence_predicted_var

        ci_lower = empirical_var_TN * df / scipy.stats.chi2.ppf(0.975, df)
        ci_upper = empirical_var_TN * df / scipy.stats.chi2.ppf(0.025, df)
        variance_ratio_ci = [
            ci_lower / independence_predicted_var,
            ci_upper / independence_predicted_var,
        ]

        say("chi2_stat=%.4f df=%d p_value=%.6f" % (chi2_stat, df, p_value))
        say("variance_ratio=%.4f 95ci=[%.4f, %.4f]" % (
            variance_ratio, variance_ratio_ci[0], variance_ratio_ci[1]))

    # ---- Mean T_N cross-batch characterisation
    mean_TN_comparison = None
    if mean_TN is not None:
        delta_vs_b1_expected = mean_TN - BATCH1_EXPECTED_MEAN_TN
        delta_vs_b2 = mean_TN - BATCH2_MEAN_TN
        mean_TN_comparison = {
            "batch1_expected_mean_TN": round(BATCH1_EXPECTED_MEAN_TN, 1),
            "batch1_formula": "17919 * 0.42738",
            "batch2_mean_TN": BATCH2_MEAN_TN,
            "batch3_mean_TN": round(mean_TN, 3),
            "delta_vs_batch1_expected": round(delta_vs_b1_expected, 3),
            "delta_vs_batch2": round(delta_vs_b2, 3),
            "note": (
                "Observation only. No finding. "
                "delta_vs_batch2 < 2*std_TN is consistent; "
                "large delta would warrant an anomaly note."
            ),
        }
        say("mean T_N cross-batch: b1_exp=%.1f b2=%.1f b3=%.3f d_b1=%.3f d_b2=%.3f" % (
            BATCH1_EXPECTED_MEAN_TN, BATCH2_MEAN_TN, mean_TN,
            delta_vs_b1_expected, delta_vs_b2))

    # ---- Write results
    variance_results = {
        "task": TASK,
        "batch": BATCH,
        "goal": GOAL,
        "script_version": SCRIPT_VERSION,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "parameters": {
            "m": M,
            "n": N_LWE,
            "q": Q,
            "eta": ETA,
            "sigma": SIGMA,
            "instance_seed": INSTANCE_SEED,
            "fpylll_seed": FPYLLL_SEED,
            "sieve_algo": SIEVE_ALGO,
            "sieve_threads": SIEVE_THREADS,
            "siever_seeds_expression": SIEVER_SEEDS_EXPRESSION,
            "siever_seeds": SIEVER_SEEDS[:n_runs_actual],
            "target_N": TARGET_N,
            "n_runs_requested": args.n_runs,
            "n_runs_completed": n_runs_completed,
        },
        "TN_values": TN_values,
        "TN_statistics": {
            "empirical_var_TN": empirical_var_TN,
            "mean_TN": mean_TN,
            "std_TN": std_TN,
            "min_TN": min_TN,
            "max_TN": max_TN,
        },
        "independence_test": {
            "single_score_source": "within-environment run-0 sieve vectors",
            "single_score_var": single_score_var,
            "single_score_mean_run0": single_score_mean_run0,
            "N_run0": N_run0,
            "independence_predicted_var": independence_predicted_var,
            "variance_ratio": variance_ratio,
            "chi2_stat": chi2_stat,
            "chi2_df": chi2_df,
            "p_value": p_value,
            "ci_lower_var": ci_lower,
            "ci_upper_var": ci_upper,
            "variance_ratio_95ci": variance_ratio_ci,
            "interpretation_note": (
                "ratio=1.0 is consistent with i.i.d.; ratio>1.0 means more variance "
                "than independence predicts; ratio<1.0 means less. "
                "No conclusion is drawn here. states_a_finding=false."
            ),
        },
        "mean_TN_comparison": mean_TN_comparison,
        "run_records": run_records,
        "log": log,
        "platform": platform.platform(),
        "wall_seconds": round(time.time() - t_start, 3),
    }

    out_path = os.path.join(args.out_dir, "variance_results.json")
    with open(out_path, "w") as f:
        json.dump(variance_results, f, indent=2)
    say("wrote %s" % out_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
