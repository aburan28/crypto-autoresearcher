#!/usr/bin/env python3
"""
TASK-20260814-ffd791 -- PREREG-8 section 1: infrastructure re-verification.

Runs, in order, and gates everything below on ALL THREE passing:
  1. fpylll installed, version recorded, BKZ.reduction callable with an
     explicit block_size (and the strategies file it needs to run).
  2. Real CBD(eta) sampler and FIPS 203 Compress_d/Decompress_d, independently
     re-derived from FIPS 203's own mathematical definitions and checked
     against ML-KEM-512/768 Table 2 (eta1=3 [512] / eta1=2 [768], eta2=2,
     d_u=10, d_v=4).
  3. A from-scratch scalar (Python-loop) nearest-plane Babai implementation
     and a from-scratch batched (numpy-vectorized) nearest-plane Babai
     implementation, both built independently of fpylll's own GSO.babai(),
     agree bit-for-bit on small, hand-checkable random instances.

No hand-rolled BKZ substitute is used anywhere in this file if point 1 fails
-- point 1 failing is fatal for the WHOLE package (T-PROJNOISE-NODATA) and
the script exits before attempting points 2/3 or Stage 0.

SEED_ROOT = 715923 (PREREG-8 section 3.5). stage_index = 0 is reserved for
Stage 0 (feasibility) draws; this file's own checks are section-1
infrastructure checks, not Stage-0 measurement draws, and use a distinct,
clearly-labelled fixed sub-seed (arm_index string) under the SAME
default_rng([SEED_ROOT, ...]) convention so every random draw in this
package traces to one documented seed root.
"""
import itertools
import json
import math
import subprocess
import sys
import time
import traceback

import numpy as np

SEED_ROOT = 715923
RESULTS = {
    "seed_root": SEED_ROOT,
    "section_1_point_1_fpylll": None,
    "section_1_point_2_cbd_and_compression": None,
    "section_1_point_3_batched_babai_exactness": None,
    "overall_pass": None,
    "termination_branch": None,
}


def check_fpylll():
    """Section 1 point 1: fpylll installed, version recorded, BKZ.reduction
    callable with an explicit block_size and a default strategies file."""
    out = {"check": "fpylll_install_and_bkz_callable"}
    try:
        import fpylll
        out["fpylll_version"] = fpylll.__version__
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL

        FPLLL.set_random_seed(SEED_ROOT)
        d = 20
        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        LLL.reduction(A)

        # The wheel's own BKZ.DEFAULT_STRATEGY path
        # (/project/local/share/fplll/strategies/default.json, a build-time
        # path baked into the wheel) does not exist on this host; the
        # strategies file IS present, but at the OS package path instead
        # (/usr/share/libfplll8/strategies/default.json). This is recorded
        # as a protocol deviation, not a failure: BKZ.reduction is still
        # callable with an explicit block_size and *a* default strategies
        # file, exactly as section 1 point 1 requires -- it is just not at
        # the wheel-internal default path.
        default_path = None
        try:
            default_path = fpylll.BKZ.DEFAULT_STRATEGY
            if isinstance(default_path, bytes):
                default_path = default_path.decode()
        except Exception:
            pass

        candidate_paths = [
            default_path,
            "/usr/share/libfplll8/strategies/default.json",
        ]
        strategies_path = None
        for p in candidate_paths:
            if not p:
                continue
            try:
                with open(p):
                    strategies_path = p
                    break
            except OSError:
                continue

        if strategies_path is None:
            out["pass"] = False
            out["error"] = (
                "No BKZ strategies file found at wheel default (%r) or at "
                "the OS package path." % (default_path,)
            )
            return out

        out["strategies_file_used"] = strategies_path
        out["strategies_file_deviation"] = (
            strategies_path != default_path
        )
        out["wheel_default_strategy_path"] = default_path

        par = BKZ.Param(block_size=10, strategies=strategies_path)
        t0 = time.time()
        BKZ.reduction(A, par)
        elapsed = time.time() - t0

        out["explicit_block_size_used"] = 10
        out["smoke_test_dimension"] = d
        out["smoke_test_elapsed_seconds"] = elapsed
        out["pass"] = True
        return out
    except Exception as exc:  # noqa: BLE001 -- must record exact error, never swallow
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def cbd_exact_pmf(eta):
    """Exact PMF of CBD(eta) via brute-force enumeration of all 2*eta
    independent fair bits (FIPS 203 Algorithm 8 SamplePolyCBD_eta, applied
    to a single coordinate): a = sum of first eta bits, b = sum of next eta
    bits, sample = a - b in {-eta, ..., eta}."""
    counts = {}
    n_bits = 2 * eta
    total = 2 ** n_bits
    for bits in itertools.product((0, 1), repeat=n_bits):
        a = sum(bits[:eta])
        b = sum(bits[eta:])
        v = a - b
        counts[v] = counts.get(v, 0) + 1
    pmf = {k: c / total for k, c in counts.items()}
    return pmf


def cbd_sample(eta, rng, n):
    """Independent CBD(eta) sampler, implemented directly from FIPS 203
    Algorithm 8's own definition (sum of eta fair bits minus sum of eta
    further fair bits), NOT via numpy's binomial (which would be a
    different, if equivalent-in-law, code path -- this is the actual
    sampler under test)."""
    bits = rng.integers(0, 2, size=(n, 2 * eta), dtype=np.int8)
    a = bits[:, :eta].sum(axis=1)
    b = bits[:, eta:].sum(axis=1)
    return (a - b).astype(np.int64)


def chi_square_gof(samples, pmf, n_total):
    """Chi-square goodness-of-fit of empirical samples against the exact
    combinatorial PMF derived independently above."""
    values = sorted(pmf.keys())
    observed = np.array([np.sum(samples == v) for v in values], dtype=float)
    expected = np.array([pmf[v] * n_total for v in values], dtype=float)
    chi2 = float(np.sum((observed - expected) ** 2 / expected))
    dof = len(values) - 1
    # Wilson-Hilferty approximation for the chi-square upper tail p-value
    # (avoids requiring scipy.stats for this specific check; scipy IS
    # available in this environment and is used directly below instead,
    # since it is already a verified dependency -- see environment.json).
    from scipy import stats

    p_value = float(stats.chi2.sf(chi2, dof))
    return chi2, dof, p_value, observed.tolist(), expected.tolist()


def fips203_compress(x, d, q):
    """FIPS 203 Eq. Compress_d(x) = round((2^d / q) * x) mod 2^d, using
    round-half-up (FIPS 203's own round-to-nearest-with-ties-up convention),
    re-derived directly from the published formula, not copied from any
    existing implementation in this repository."""
    y = (2 ** d) * x / q
    r = math.floor(y + 0.5)
    return r % (2 ** d)


def fips203_decompress(y, d, q):
    """Decompress_d(y) = round((q / 2^d) * y), same rounding convention."""
    x = q * y / (2 ** d)
    return math.floor(x + 0.5)


def check_cbd_and_compression():
    out = {"check": "cbd_sampler_and_fips203_compression"}
    try:
        rng = np.random.default_rng([SEED_ROOT, 0, 0, 0, 0, 0])
        q = 3329

        # ---- Table 2 constants under this protocol's own scope ----
        # PREREG-8 section 9: eta1=3, eta2=2, d_u=10, d_v=4 -- these are the
        # published FIPS 203 ML-KEM-512 parameters exactly (ML-KEM-768
        # shares d_u=10, d_v=4 and eta2=2 but uses eta1=2, NOT eta1=3; this
        # is stated explicitly here rather than silently conflating the two
        # parameter sets, since the task card's own phrase "ML-KEM-512/768
        # Table 2 values" is imprecise about eta1 -- d_u/d_v ARE shared,
        # eta1 is NOT).
        table2 = {
            "ml_kem_512": {"eta1": 3, "eta2": 2, "d_u": 10, "d_v": 4},
            "ml_kem_768": {"eta1": 2, "eta2": 2, "d_u": 10, "d_v": 4},
        }
        out["table2_reference_values"] = table2
        out["protocol_scope_values"] = {
            "eta1": 3, "eta2": 2, "d_u": 10, "d_v": 4,
            "note": "matches ml_kem_512 exactly; d_u/d_v also match ml_kem_768",
        }

        # ---- CBD sampler: exact PMF vs. large-N empirical chi-square ----
        cbd_checks = []
        n_samples = 200_000
        for eta in (2, 3):
            pmf = cbd_exact_pmf(eta)
            # Independent sanity re-derivation of mean/variance from the
            # exact PMF itself (not the sampler): CBD(eta) is the
            # difference of two Binomial(eta, 1/2) variables, each with
            # variance eta/4, so Var = eta/2, Mean = 0 -- checked against
            # the PMF via direct summation, not asserted.
            mean_from_pmf = sum(v * p for v, p in pmf.items())
            var_from_pmf = sum((v ** 2) * p for v, p in pmf.items()) - mean_from_pmf ** 2
            expected_var = eta / 2.0

            samples = cbd_sample(eta, rng, n_samples)
            support_ok = bool(np.all(samples >= -eta) and np.all(samples <= eta))
            chi2, dof, p_value, observed, expected = chi_square_gof(samples, pmf, n_samples)

            cbd_checks.append({
                "eta": eta,
                "exact_pmf": {str(k): v for k, v in sorted(pmf.items())},
                "mean_from_exact_pmf": mean_from_pmf,
                "variance_from_exact_pmf": var_from_pmf,
                "expected_variance_eta_over_2": expected_var,
                "variance_matches_eta_over_2": abs(var_from_pmf - expected_var) < 1e-9,
                "n_samples": n_samples,
                "support_within_[-eta,eta]": support_ok,
                "chi_square_statistic": chi2,
                "degrees_of_freedom": dof,
                "chi_square_p_value": p_value,
                "chi_square_pass_at_alpha_0.001": p_value > 0.001,
            })

        out["cbd_checks"] = cbd_checks
        cbd_pass = all(
            c["support_within_[-eta,eta]"]
            and c["variance_matches_eta_over_2"]
            and c["chi_square_pass_at_alpha_0.001"]
            for c in cbd_checks
        )

        # ---- Compress_d / Decompress_d: round-trip error bound check ----
        comp_checks = []
        for d in (10, 4):
            max_err = 0
            n_test = 2000
            xs = rng.integers(0, q, size=n_test)
            for x in xs:
                x = int(x)
                y = fips203_compress(x, d, q)
                assert 0 <= y < 2 ** d, "compressed value out of range"
                xr = fips203_decompress(y, d, q)
                # circular distance on Z_q
                err = min((xr - x) % q, (x - xr) % q)
                max_err = max(max_err, err)
            # theoretical worst-case round-trip error bound for Compress/
            # Decompress at modulus d (standard FIPS 203 / Kyber result):
            # |Decompress(Compress(x)) - x| <= round(q / 2^(d+1))
            theoretical_bound = round(q / (2 ** (d + 1)))
            comp_checks.append({
                "d": d,
                "n_test_points": n_test,
                "measured_max_round_trip_error": max_err,
                "theoretical_bound_q_over_2^(d+1)": theoretical_bound,
                "within_theoretical_bound": max_err <= theoretical_bound,
            })
        out["compression_checks"] = comp_checks
        comp_pass = all(c["within_theoretical_bound"] for c in comp_checks)

        out["pass"] = bool(cbd_pass and comp_pass)
        if not out["pass"]:
            out["error"] = "CBD or compression re-derivation failed its check; see cbd_checks/compression_checks"
        return out
    except Exception as exc:  # noqa: BLE001
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def gram_schmidt(B):
    """Independent (non-fpylll) Gram-Schmidt: returns Bstar (d x d) and mu
    (d x d, mu[i][j] for j<i), computed directly from the basis B (numpy,
    float64) so the Babai exactness check below does not depend on
    fpylll's own internal GSO machinery at all."""
    d = B.shape[0]
    Bstar = np.zeros_like(B, dtype=np.float64)
    mu = np.zeros((d, d), dtype=np.float64)
    for i in range(d):
        Bstar[i] = B[i].astype(np.float64)
        for j in range(i):
            mu[i, j] = np.dot(B[i], Bstar[j]) / np.dot(Bstar[j], Bstar[j])
            Bstar[i] = Bstar[i] - mu[i, j] * Bstar[j]
    r = np.array([np.dot(Bstar[i], Bstar[i]) for i in range(d)])
    return Bstar, mu, r


def babai_scalar(B, Bstar, r, targets):
    """Reference scalar (per-target Python loop) nearest-plane Babai.
    Returns, per target, the residual vector w = t - sum(c_i b_i) and the
    integer coefficient vector c."""
    d = B.shape[0]
    results = []
    for t in targets:
        w = t.astype(np.float64).copy()
        c = np.zeros(d, dtype=np.int64)
        for i in range(d - 1, -1, -1):
            coeff = np.dot(w, Bstar[i]) / r[i]
            ci = int(round(coeff))
            c[i] = ci
            w = w - ci * B[i]
        results.append((w.copy(), c.copy()))
    return results


def babai_batched(B, Bstar, r, targets):
    """Batched (numpy-vectorized over all targets simultaneously) nearest-
    plane Babai -- the SAME algorithm as babai_scalar, reordered to process
    the whole target matrix at once per basis-vector step, exactly the
    style Stage 1's own >= 2^20-target harness would use via BLAS."""
    d = B.shape[0]
    M = targets.shape[0]
    W = targets.astype(np.float64).copy()
    C = np.zeros((M, d), dtype=np.int64)
    for i in range(d - 1, -1, -1):
        coeff = (W @ Bstar[i]) / r[i]
        ci = np.round(coeff).astype(np.int64)
        C[:, i] = ci
        W = W - np.outer(ci.astype(np.float64), B[i])
    return W, C


def check_batched_babai_exactness():
    out = {"check": "batched_vs_scalar_babai_exactness"}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL

        rng = np.random.default_rng([SEED_ROOT, 0, 0, 0, 1, 0])
        FPLLL.set_random_seed(SEED_ROOT + 1)

        instances = []
        # A handful of small, hand-checkable instances at increasing d,
        # matching CTRL-BATCHED-BABAI-EXACTNESS's own "hand-checkable"
        # requirement.
        for d in (4, 6, 8, 10):
            A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
            LLL.reduction(A)
            B = np.array([[A[i, j] for j in range(d)] for i in range(d)], dtype=np.int64)
            Bstar, mu, r = gram_schmidt(B)

            n_targets = 20
            targets = rng.integers(-3329, 3329, size=(n_targets, d)).astype(np.int64)

            scalar_results = babai_scalar(B, Bstar, r, targets)
            W_batched, C_batched = babai_batched(B, Bstar, r, targets)

            max_w_diff = 0.0
            max_c_diff = 0
            for idx, (w_s, c_s) in enumerate(scalar_results):
                w_diff = float(np.max(np.abs(w_s - W_batched[idx])))
                c_diff = int(np.max(np.abs(c_s - C_batched[idx])))
                max_w_diff = max(max_w_diff, w_diff)
                max_c_diff = max(max_c_diff, c_diff)

            instances.append({
                "d": d,
                "n_targets": n_targets,
                "max_residual_vector_abs_diff": max_w_diff,
                "max_coefficient_abs_diff": max_c_diff,
                "exact_match": (max_w_diff == 0.0) and (max_c_diff == 0),
            })

        out["instances"] = instances
        out["pass"] = all(inst["exact_match"] for inst in instances)
        if not out["pass"]:
            out["error"] = "batched Babai disagreed with scalar Babai on at least one instance"
        return out
    except Exception as exc:  # noqa: BLE001
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def main():
    t_start = time.time()

    r1 = check_fpylll()
    RESULTS["section_1_point_1_fpylll"] = r1
    if not r1["pass"]:
        RESULTS["overall_pass"] = False
        RESULTS["termination_branch"] = "T-PROJNOISE-NODATA"
        RESULTS["termination_reason"] = (
            "Section 1 point 1 (fpylll install/callable) failed: %s" % r1.get("error")
        )
        RESULTS["wall_clock_seconds"] = time.time() - t_start
        print(json.dumps(RESULTS, indent=2))
        return RESULTS

    r2 = check_cbd_and_compression()
    RESULTS["section_1_point_2_cbd_and_compression"] = r2
    if not r2["pass"]:
        RESULTS["overall_pass"] = False
        RESULTS["termination_branch"] = "T-PROJNOISE-NODATA"
        RESULTS["termination_reason"] = (
            "Section 1 point 2 (CBD/compression re-derivation) failed: %s" % r2.get("error")
        )
        RESULTS["wall_clock_seconds"] = time.time() - t_start
        print(json.dumps(RESULTS, indent=2))
        return RESULTS

    r3 = check_batched_babai_exactness()
    RESULTS["section_1_point_3_batched_babai_exactness"] = r3
    if not r3["pass"]:
        RESULTS["overall_pass"] = False
        RESULTS["termination_branch"] = "T-PROJNOISE-NODATA"
        RESULTS["termination_reason"] = (
            "Section 1 point 3 (batched-vs-scalar Babai exactness) failed: %s" % r3.get("error")
        )
        RESULTS["wall_clock_seconds"] = time.time() - t_start
        print(json.dumps(RESULTS, indent=2))
        return RESULTS

    RESULTS["overall_pass"] = True
    RESULTS["termination_branch"] = "CLEARED -- proceed to Stage 0 (section 2)"
    RESULTS["wall_clock_seconds"] = time.time() - t_start
    print(json.dumps(RESULTS, indent=2))
    return RESULTS


if __name__ == "__main__":
    result = main()
    with open("infra_verification_results.json", "w") as f:
        json.dump(result, f, indent=2)
    sys.exit(0 if result["overall_pass"] else 1)
