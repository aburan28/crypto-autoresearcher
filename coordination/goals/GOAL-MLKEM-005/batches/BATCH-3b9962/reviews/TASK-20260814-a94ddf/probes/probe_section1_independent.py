#!/usr/bin/env python3
"""
Independent Validator probe: re-derive PREREG-8 section 1's three checks
from scratch, WITHOUT importing TASK-20260814-ffd791's own
infra_verification.py module. Written independently against FIPS 203's
published definitions and this protocol's own text (prereg.md section 1),
not against the producer's code.

Run by TASK-20260814-a94ddf (Validator), independent session.
"""
import itertools
import json
import math
import time
import traceback

import numpy as np

SEED_ROOT = 715923
RESULTS = {"seed_root": SEED_ROOT}


def check1_fpylll():
    out = {}
    try:
        import fpylll
        out["fpylll_version"] = fpylll.__version__
        from fpylll import IntegerMatrix, LLL, BKZ, FPLLL

        FPLLL.set_random_seed(SEED_ROOT)
        d = 20
        A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
        LLL.reduction(A)

        # Independently locate a strategies file (do not assume the
        # producer's own path resolution logic).
        strategies_path = None
        try:
            wheel_default = fpylll.BKZ.DEFAULT_STRATEGY
            if isinstance(wheel_default, bytes):
                wheel_default = wheel_default.decode()
        except Exception:
            wheel_default = None
        for candidate in (wheel_default, "/usr/share/libfplll8/strategies/default.json"):
            if candidate:
                try:
                    with open(candidate):
                        strategies_path = candidate
                        break
                except OSError:
                    continue
        out["wheel_default_strategy_path"] = wheel_default
        out["strategies_file_used"] = strategies_path
        if strategies_path is None:
            out["pass"] = False
            out["error"] = "no strategies file found"
            return out

        par = BKZ.Param(block_size=10, strategies=strategies_path)
        t0 = time.time()
        BKZ.reduction(A, par)
        out["smoke_test_elapsed_seconds"] = time.time() - t0
        out["pass"] = True
        return out
    except Exception as exc:
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def check2_cbd_and_compression():
    """Independently re-derived from FIPS 203's published definitions
    (Algorithm 8 SamplePolyCBD_eta; Compress_d/Decompress_d), NOT by
    importing infra_verification.py's cbd_exact_pmf / fips203_compress
    functions -- this probe writes its own implementation from the spec."""
    out = {}
    try:
        q = 3329
        rng = np.random.default_rng([SEED_ROOT, 99, 99, 99, 99, 99])  # deliberately different sub-seed than producer's

        def exact_cbd_pmf(eta):
            counts = {}
            for bits in itertools.product((0, 1), repeat=2 * eta):
                a = sum(bits[:eta])
                b = sum(bits[eta:])
                v = a - b
                counts[v] = counts.get(v, 0) + 1
            tot = 2 ** (2 * eta)
            return {k: c / tot for k, c in counts.items()}

        def sample_cbd(eta, n):
            bits = rng.integers(0, 2, size=(n, 2 * eta))
            a = bits[:, :eta].sum(axis=1)
            b = bits[:, eta:].sum(axis=1)
            return a - b

        cbd_results = []
        for eta in (2, 3):
            pmf = exact_cbd_pmf(eta)
            mean = sum(v * p for v, p in pmf.items())
            var = sum(v * v * p for v, p in pmf.items()) - mean ** 2
            samples = sample_cbd(eta, 200_000)
            # independent chi-square via scipy
            from scipy import stats
            vals = sorted(pmf)
            obs = np.array([np.sum(samples == v) for v in vals], dtype=float)
            exp = np.array([pmf[v] * 200_000 for v in vals], dtype=float)
            chi2 = float(np.sum((obs - exp) ** 2 / exp))
            p = float(stats.chi2.sf(chi2, len(vals) - 1))
            cbd_results.append({
                "eta": eta, "mean": mean, "variance": var,
                "expected_variance_eta_over_2": eta / 2.0,
                "variance_ok": abs(var - eta / 2.0) < 1e-9,
                "chi2": chi2, "chi2_p": p, "chi2_pass_alpha_0.001": p > 0.001,
                "support_ok": bool(np.all(samples >= -eta) and np.all(samples <= eta)),
            })
        out["cbd_results"] = cbd_results

        def compress(x, dbits):
            # FIPS 203 Eq: Compress_d(x) = round((2^d/q) x) mod 2^d
            return math.floor((2 ** dbits) * x / q + 0.5) % (2 ** dbits)

        def decompress(y, dbits):
            return math.floor(q * y / (2 ** dbits) + 0.5)

        comp_results = []
        for dbits in (10, 4):
            xs = rng.integers(0, q, size=2000)
            max_err = 0
            for x in xs:
                x = int(x)
                y = compress(x, dbits)
                xr = decompress(y, dbits)
                err = min((xr - x) % q, (x - xr) % q)
                max_err = max(max_err, err)
            bound = round(q / (2 ** (dbits + 1)))
            comp_results.append({"d": dbits, "max_err": max_err, "bound": bound, "within_bound": max_err <= bound})
        out["compression_results"] = comp_results

        out["pass"] = all(c["variance_ok"] and c["chi2_pass_alpha_0.001"] and c["support_ok"] for c in cbd_results) \
            and all(c["within_bound"] for c in comp_results)
        return out
    except Exception as exc:
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def check3_batched_babai():
    """Independent scalar-vs-batched Babai exactness check, own
    Gram-Schmidt and own babai implementations, not imported from the
    producer's file."""
    out = {}
    try:
        from fpylll import IntegerMatrix, LLL, FPLLL
        rng = np.random.default_rng([SEED_ROOT, 7, 7, 7, 7, 7])
        FPLLL.set_random_seed(SEED_ROOT + 777)

        def gso(B):
            d = B.shape[0]
            Bstar = np.zeros_like(B, dtype=np.float64)
            mu = np.zeros((d, d))
            for i in range(d):
                Bstar[i] = B[i].astype(np.float64)
                for j in range(i):
                    mu[i, j] = np.dot(B[i], Bstar[j]) / np.dot(Bstar[j], Bstar[j])
                    Bstar[i] -= mu[i, j] * Bstar[j]
            r = np.array([np.dot(Bstar[i], Bstar[i]) for i in range(d)])
            return Bstar, r

        def babai_scalar(B, Bstar, r, targets):
            d = B.shape[0]
            res = []
            for t in targets:
                w = t.astype(np.float64).copy()
                c = np.zeros(d, dtype=np.int64)
                for i in range(d - 1, -1, -1):
                    ci = int(round(np.dot(w, Bstar[i]) / r[i]))
                    c[i] = ci
                    w = w - ci * B[i]
                res.append((w, c))
            return res

        def babai_batched(B, Bstar, r, targets):
            d = B.shape[0]
            W = targets.astype(np.float64).copy()
            C = np.zeros((targets.shape[0], d), dtype=np.int64)
            for i in range(d - 1, -1, -1):
                ci = np.round((W @ Bstar[i]) / r[i]).astype(np.int64)
                C[:, i] = ci
                W = W - np.outer(ci.astype(np.float64), B[i])
            return W, C

        instances = []
        for d in (4, 6, 8, 10, 14):  # includes one dimension the producer did not test (14)
            A = IntegerMatrix.random(d, "qary", k=d // 2, q=3329)
            LLL.reduction(A)
            B = np.array([[A[i, j] for j in range(d)] for i in range(d)], dtype=np.int64)
            Bstar, r = gso(B)
            targets = rng.integers(-3329, 3329, size=(25, d)).astype(np.int64)
            scalar = babai_scalar(B, Bstar, r, targets)
            Wb, Cb = babai_batched(B, Bstar, r, targets)
            max_w = max(float(np.max(np.abs(w - Wb[i]))) for i, (w, c) in enumerate(scalar))
            max_c = max(int(np.max(np.abs(c - Cb[i]))) for i, (w, c) in enumerate(scalar))
            instances.append({"d": d, "max_w_diff": max_w, "max_c_diff": max_c,
                               "exact": max_w == 0.0 and max_c == 0})
        out["instances"] = instances
        out["pass"] = all(i["exact"] for i in instances)
        return out
    except Exception as exc:
        out["pass"] = False
        out["error"] = "%s: %s" % (type(exc).__name__, exc)
        out["traceback"] = traceback.format_exc()
        return out


def main():
    t0 = time.time()
    r1 = check1_fpylll()
    RESULTS["check1_fpylll"] = r1
    r2 = check2_cbd_and_compression()
    RESULTS["check2_cbd_compression"] = r2
    r3 = check3_batched_babai()
    RESULTS["check3_batched_babai"] = r3
    RESULTS["all_pass"] = bool(r1.get("pass") and r2.get("pass") and r3.get("pass"))
    RESULTS["wall_clock_seconds"] = time.time() - t0
    print(json.dumps(RESULTS, indent=2))
    return RESULTS


if __name__ == "__main__":
    result = main()
    with open("probe_section1_independent_results.json", "w") as f:
        json.dump(result, f, indent=2)
