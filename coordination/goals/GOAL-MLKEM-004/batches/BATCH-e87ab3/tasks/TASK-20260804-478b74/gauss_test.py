#!/usr/bin/env python3
"""
gauss_test.py — TASK-20260804-478b74 / BATCH-e87ab3 / GOAL-MLKEM-004
Batch 6 of 6 (FINAL): gauss_sieve algorithm control test.

Uses gauss_sieve (NOT bgj1_sieve) on the same LWE instance as batches 2–5.
If variance_ratio_gauss is also > 1, the inflation is algorithm-independent
(not a bgj1-specific QEMU/SIMD emulation artifact). If ratio ≈ 1.0, it is
bgj1-specific.

ALGORITHM CHANGE (vs prior batches):
  - Prior batches: g.bgj1_sieve()  (probabilistic, SIMD-heavy)
  - This batch:    g.gauss_sieve() (combinatorial, no SIMD-specific code paths)

LWE INSTANCE (FROZEN — identical to all prior batches):
  instance_seed  = 20260803001
  fpylll_seed    = 20260803005
  m=35, n=25, q=127, eta=2, sigma=2.0  → D=60

SIEVER SEEDS (pre-registered, different from all prior batches):
  numpy.random.default_rng(20260804004).integers(0, 2**32, size=50).tolist()

METRICS:
  - variance_ratio_gauss = Var[T_N_gauss] / (N_run0 * within_env_single_score_var)
  - chi2_gauss, p_value_gauss, 95% CI (ddof=n-1)
  - RC-3: Pearson r of T_N[even-indexed] vs T_N[odd-indexed]

OUTPUTS ONLY observations. States NO finding. No comparison against MATZOV.Nf.
  states_a_finding: false
  compared_against_matzov_nf: false
  rule12_status: "UNMET and UNWAIVED"

WALL-CLOCK BUDGET:
  Soft limit: 5400s (90 min). If elapsed >= 5400s and at least 20 runs done,
  terminate early and record actual count. Minimum 20 runs required.
"""

import argparse
import json
import os
import platform
import resource
import sys
import time

import numpy as np
import scipy.stats

from fpylll import IntegerMatrix, LLL, FPLLL
from g6k import Siever, SieverParams

SCRIPT_VERSION = "1.0.0"
TASK = "TASK-20260804-478b74"
BATCH = "BATCH-e87ab3"
GOAL = "GOAL-MLKEM-004"

# ---- Frozen LWE parameters (identical to all prior batches) ----
M, N_LWE, Q = 35, 25, 127
D = M + N_LWE   # lattice dimension = 60
ETA = 2
SIGMA = 2.0
INSTANCE_SEED = 20260803001
FPYLLL_SEED = 20260803005
SIEVE_ALGO = "gauss_sieve"   # <-- KEY CHANGE vs prior batches
SIEVE_THREADS = 1

# ---- Pre-registered seed expression (verbatim) ----
SIEVER_SEEDS_EXPRESSION = (
    "numpy.random.default_rng(20260804004).integers(0, 2**32, size=50).tolist()"
)
SIEVER_SEEDS = np.random.default_rng(20260804004).integers(0, 2**32, size=50).tolist()

# ---- Wall-clock budget ----
WALL_CLOCK_SOFT_LIMIT_S = 5400   # 90 minutes
MIN_RUNS = 20

# ---- Prior-batch reference values (for report only, never used in computation) ----
BATCH3_VARIANCE_RATIO = 1.3915756694338621
BATCH5_NULL_VARIANCE_RATIO = 1.5332


# ---------------------------------------------------------------------------
# LWE helpers
# ---------------------------------------------------------------------------

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
    return np.array(
        [[A[i, j] for j in range(A.ncols)] for i in range(A.nrows)],
        dtype=np.int64
    )


def build_instance_and_lll():
    """Build LWE instance + LLL-reduced basis. Returns (A, s, e, b, Bred_fp)."""
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


def run_single_sieve_gauss(Bred_fp, siever_seed):
    """Run gauss_sieve with given seed. Returns (coeffs, Bused, N, t_sieve)."""
    g = Siever(Bred_fp, SieverParams(threads=SIEVE_THREADS), seed=siever_seed)
    g.initialize_local(0, 0, D)
    t0 = time.time()
    g.gauss_sieve()   # <-- gauss_sieve, not bgj1_sieve
    t_sieve = time.time() - t0
    coeffs = np.array([tuple(v) for v in g.itervalues()], dtype=np.int64)
    Bused = from_intmat(g.M.B)
    return coeffs, Bused, coeffs.shape[0], t_sieve


def compute_TN(coeffs, Bused, b, s, q, m, n):
    """Compute T_N = sum of cosine scores for the correct secret s.
    Also returns per-vector scores array."""
    V = coeffs.dot(Bused)   # N x d
    X = V[:, :m]             # N x m
    Y = V[:, m:]             # N x n
    phases = center_mod(X.dot(b) - Y.dot(s), q)
    scores = np.cos(2.0 * np.pi * phases / q)
    T_N = float(scores.sum())
    return T_N, int(V.shape[0]), scores


def compute_single_score_var_from_run0(coeffs, Bused, b, s, q, m, n):
    """Within-environment single-score variance from run-0 sieve vectors."""
    V = coeffs.dot(Bused)
    X = V[:, :m]
    Y = V[:, m:]
    phases = center_mod(X.dot(b) - Y.dot(s), q)
    single_scores = np.cos(2.0 * np.pi * phases / q)
    ssv = float(np.var(single_scores, ddof=1))
    ssm = float(np.mean(single_scores))
    return ssv, ssm, int(single_scores.shape[0])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--repo-root", default=None)
    ap.add_argument("--n-runs", type=int, default=50,
                    help="Max number of sieve runs (default: 50, minimum recorded: 20)")
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

    say("gauss_test.py %s: up_to=%d runs, sieve=%s" % (
        SCRIPT_VERSION, args.n_runs, SIEVE_ALGO))
    say("TASK=%s BATCH=%s GOAL=%s" % (TASK, BATCH, GOAL))
    say("instance_seed=%d fpylll_seed=%d" % (INSTANCE_SEED, FPYLLL_SEED))
    say("siever_seeds_expression: %s" % SIEVER_SEEDS_EXPRESSION)
    say("first 5 seeds: %s" % SIEVER_SEEDS[:5])
    say("platform: %s" % platform.platform())
    say("algorithm: gauss_sieve (NOT bgj1_sieve) — key control difference")
    say("wall_clock_soft_limit=%ds min_runs=%d" % (WALL_CLOCK_SOFT_LIMIT_S, MIN_RUNS))

    # Build instance ONCE
    A, s, e, b, Bred_fp = build_instance_and_lll()
    say("instance built: |s|_inf=%d |e|_inf=%d" % (
        int(np.abs(s).max()), int(np.abs(e).max())))

    TN_values = []
    run_records = []
    n_runs_completed = 0
    stopped_early = False
    early_stop_reason = None

    single_score_var = None
    single_score_mean_run0 = None
    N_run0 = None
    independence_predicted_var = None

    n_runs_actual = min(args.n_runs, len(SIEVER_SEEDS))

    for i in range(n_runs_actual):
        # Wall-clock soft limit: stop if past limit AND have at least MIN_RUNS
        elapsed = time.time() - t_start
        if elapsed >= WALL_CLOCK_SOFT_LIMIT_S and n_runs_completed >= MIN_RUNS:
            stopped_early = True
            early_stop_reason = (
                "wall_clock_soft_limit_exceeded: elapsed=%.1fs >= %ds "
                "and n_runs_completed=%d >= %d; stopping." % (
                    elapsed, WALL_CLOCK_SOFT_LIMIT_S, n_runs_completed, MIN_RUNS)
            )
            say("EARLY STOP: %s" % early_stop_reason)
            break

        seed_i = SIEVER_SEEDS[i]
        t0_run = time.time()
        try:
            coeffs, Bused, N_i, t_sieve = run_single_sieve_gauss(Bred_fp, seed_i)
            T_N_i, n_vec, scores_i = compute_TN(coeffs, Bused, b, s, Q, M, N_LWE)
            t_run = time.time() - t0_run

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

    say("Completed %d/%d runs (stopped_early=%s)" % (
        n_runs_completed, n_runs_actual, stopped_early))

    # ---- Variance statistics ----
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

    # ---- Chi-squared test ----
    variance_ratio = None
    chi2_stat = None
    p_value = None
    ci_lower_var = None
    ci_upper_var = None
    variance_ratio_ci = None
    chi2_df = None

    if (empirical_var_TN is not None
            and independence_predicted_var is not None
            and independence_predicted_var > 0):
        df = n_runs_completed - 1
        chi2_df = df
        chi2_stat = float(df * empirical_var_TN / independence_predicted_var)
        p_value = float(1.0 - scipy.stats.chi2.cdf(chi2_stat, df=df))
        variance_ratio = empirical_var_TN / independence_predicted_var

        ci_lower_var = empirical_var_TN * df / scipy.stats.chi2.ppf(0.975, df)
        ci_upper_var = empirical_var_TN * df / scipy.stats.chi2.ppf(0.025, df)
        variance_ratio_ci = [
            ci_lower_var / independence_predicted_var,
            ci_upper_var / independence_predicted_var,
        ]

        say("variance_ratio=%.4f chi2=%.4f df=%d p=%.6f" % (
            variance_ratio, chi2_stat, df, p_value))
        say("95%%CI_ratio=[%.4f, %.4f]" % (variance_ratio_ci[0], variance_ratio_ci[1]))

    # ---- RC-3 cross-run correlation test ----
    rc3_r = None
    rc3_p = None
    rc3_n_pairs = None
    rc3_note = None

    if len(TN_values) >= 4:
        TN_even = [TN_values[i] for i in range(0, len(TN_values), 2)]
        TN_odd  = [TN_values[i] for i in range(1, len(TN_values), 2)]
        min_len = min(len(TN_even), len(TN_odd))
        TN_even = TN_even[:min_len]
        TN_odd  = TN_odd[:min_len]
        if min_len >= 3:
            rc3_r_raw, rc3_p_raw = scipy.stats.pearsonr(TN_even, TN_odd)
            rc3_r = float(rc3_r_raw)
            rc3_p = float(rc3_p_raw)
            rc3_n_pairs = min_len
            rc3_note = (
                "Pearson r of T_N[0,2,4,...] vs T_N[1,3,5,...]. "
                "r≈0 is consistent with independence. "
                "No conclusion drawn."
            )
            say("RC-3: r=%.4f p=%.4f n_pairs=%d" % (rc3_r, rc3_p, min_len))
        else:
            rc3_note = "insufficient pairs (< 3) for Pearson r"
            say("RC-3: %s" % rc3_note)
    else:
        rc3_note = "insufficient runs (< 4) for RC-3"
        say("RC-3: %s" % rc3_note)

    # ---- Assemble gauss_results.json ----
    gauss_results = {
        "task": TASK,
        "sieve_algorithm": SIEVE_ALGO,
        "parameters": {
            "instance_seed": INSTANCE_SEED,
            "fpylll_seed": FPYLLL_SEED,
            "siever_seeds_expression": SIEVER_SEEDS_EXPRESSION,
            "n_runs_requested": args.n_runs,
            "n_runs_completed": n_runs_completed,
            "stopped_early": stopped_early,
            "early_stop_reason": early_stop_reason,
        },
        "TN_values": TN_values,
        "variance_stats": {
            "empirical_var_TN": empirical_var_TN,
            "within_env_single_score_var_run0": single_score_var,
            "N_vectors_run0": N_run0,
            "independence_predicted_var": independence_predicted_var,
            "variance_ratio": variance_ratio,
            "chi2_stat": chi2_stat,
            "chi2_df": chi2_df,
            "p_value": p_value,
            "ci_95_ratio": variance_ratio_ci,
        },
        "rc3_cross_run": {
            "r_even_vs_odd": rc3_r,
            "p": rc3_p,
            "n_pairs": rc3_n_pairs,
            "note": rc3_note,
        },
        "mean_TN": mean_TN,
        "states_a_finding": False,
        "compared_against_matzov_nf": False,
        "rule12_status": "UNMET and UNWAIVED",
        "run_records": run_records,
        "log": log,
        "platform": platform.platform(),
        "wall_seconds": round(time.time() - t_start, 3),
    }

    out_path = os.path.join(args.out_dir, "gauss_results.json")
    with open(out_path, "w") as f:
        json.dump(gauss_results, f, indent=2)
    say("wrote %s" % out_path)

    # Flush log summary
    say("DONE: sieve=%s n_runs=%d variance_ratio=%s p=%s rc3_r=%s" % (
        SIEVE_ALGO,
        n_runs_completed,
        ("%.4f" % variance_ratio) if variance_ratio is not None else "None",
        ("%.6f" % p_value) if p_value is not None else "None",
        ("%.4f" % rc3_r) if rc3_r is not None else "None",
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
