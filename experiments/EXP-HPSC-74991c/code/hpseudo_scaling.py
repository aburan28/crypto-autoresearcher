"""EXP-HPSC-74991c -- what does the H-PSEUDO constant C(p) actually do?

The corpus records three incompatible readings of the same quantity:

  KN-FIND-d4f820  mean C over p in {1009,4001,9001,50021} -> "best fit C ~ p^{0.055}"
  KN-FIND-4c9e71  adversarial max C, first "bounded ~ 4, NOT growing", then
                  corrected to "BOTH mean and max scale as ~ p^{0.079}"
  KN-FIND-e7a3b1  states C(p) ~ p^{0.079} as the empirical characterization

and KN-FIND-5c1a03 / KN-FIND-f8c290 lean on the resulting yield error term being
negligible at crypto scale, which is an exponent-sensitive claim.

The prior measurements also used WILDLY UNMATCHED sample counts per prime --
152 curves at p=1009 against 6 at p=50021 (KN-FIND-4c9e71's own table). The
maximum of a sample is a function of the sample size, so a max-over-curves
compared across primes at 152 vs 6 draws is not a comparison of the same
statistic. That confound alone can move the fitted exponent, in either
direction, and no record adjusts for it.

This battery recomputes both statistics on ONE implementation with the sample
count MATCHED at every prime, over a wider range, with bootstrap intervals on
the fitted exponents.

Definitions, fixed here so that the two statistics can never again be conflated.
E/F_p has prime order N, G a generator, and

    F_t = { P in E(F_p) : x(P) < t },     B = |F_t|,
    Chat(k) = | sum_{P in F_t} e(2*pi*i*k*DL_G(P)/N) |,
    C       = max_{k != 0} Chat(k) / sqrt(B).

`C_mean(p)`  = mean of C over the curve sample at p.
`C_max(p)`   = max  of C over the curve sample at p (the "adversarial" reading).

No third-party dependency except numpy, used only for the FFT and for point
counting.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time

import numpy as np

SEED = 20260807


# ---------------------------------------------------------------------------
# curve arithmetic
# ---------------------------------------------------------------------------


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def qr_table(p: int) -> np.ndarray:
    """Boolean table: is_square[v] for v in F_p."""
    t = np.zeros(p, dtype=bool)
    xs = np.arange(p, dtype=np.int64)
    t[(xs * xs) % p] = True
    return t


def curve_order(p: int, A: int, B: int, sq: np.ndarray) -> int:
    """#E(F_p) = p + 1 + sum_x chi(f(x)), by direct enumeration."""
    x = np.arange(p, dtype=np.int64)
    f = (((x * x) % p) * x + A * x + B) % p
    zero = f == 0
    sqr = sq[f] & ~zero
    # sum_x chi(f(x)) = #{squares != 0} - #{non-squares}
    #                 = sqr - ((#nonzero) - sqr) = 2*sqr - #nonzero
    return int(p + 1 + 2 * int(sqr.sum()) - int((~zero).sum()))


def find_prime_order_curves(p: int, count: int, rng: random.Random) -> list[tuple[int, int, int]]:
    """`count` curves y^2 = x^3+Ax+B over F_p with #E(F_p) prime."""
    sq = qr_table(p)
    out, tried = [], 0
    while len(out) < count and tried < 4000:
        tried += 1
        A, B = rng.randrange(p), rng.randrange(p)
        if (4 * A**3 + 27 * B**2) % p == 0:
            continue
        N = curve_order(p, A, B, sq)
        if is_prime(N) and _order_is_correct(p, A, B, N):
            out.append((A, B, N))
    return out


def _order_is_correct(p: int, A: int, B: int, N: int) -> bool:
    """Independent check that #E = N: verify [N]P = O for a random point.

    The point-count formula is easy to get wrong by a term (it was, in the
    first draft), and a wrong N corrupts every downstream number silently.
    """
    for x0 in range(p):
        v = (pow(x0, 3, p) + A * x0 + B) % p
        if v and pow(v, (p - 1) // 2, p) == 1:
            y0 = tonelli(v, p)
            return _scalar_mul(p, A, (x0, y0), N) is None
    return False


def _scalar_mul(p: int, A: int, P, k: int):
    R, Q = None, P
    while k:
        if k & 1:
            R = _padd(p, A, R, Q)
        Q = _padd(p, A, Q, Q)
        k >>= 1
    return R


def _padd(p: int, A: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + A) * pow(2 * y1, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def indicator_vector(p: int, A: int, B: int, N: int, t: int) -> tuple[np.ndarray, int, tuple]:
    """u[j] = 1 iff x([j]G) < t, for j = 1..N-1, walking the group once.

    Returns (u, B_size, generator). u[0] corresponds to j=0 (the identity,
    which has no x-coordinate) and is set to 0.
    """
    # a generator: any affine point, since N is prime
    G = None
    for x0 in range(p):
        v = (pow(x0, 3, p) + A * x0 + B) % p
        if v == 0:
            continue
        if pow(v, (p - 1) // 2, p) == 1:
            y0 = pow(v, (p + 1) // 4, p) if p % 4 == 3 else tonelli(v, p)
            G = (x0, y0)
            break
    assert G is not None

    u = np.zeros(N, dtype=np.float64)
    gx, gy = G
    px, py = G
    for j in range(1, N):
        if px < t:
            u[j] = 1.0
        # P <- P + G
        if j == N - 1:
            break
        if px == gx:
            if (py + gy) % p == 0:
                break  # P = -G, next is identity; loop is over
            num = (3 * px * px + A) % p
            den = (2 * py) % p
        else:
            num = (gy - py) % p
            den = (gx - px) % p
        lam = num * pow(den, p - 2, p) % p
        nx = (lam * lam - px - gx) % p
        ny = (lam * (px - nx) - py) % p
        px, py = nx, ny
    return u, int(u.sum()), G


def tonelli(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = next(n for n in range(2, p) if pow(n, (p - 1) // 2, p) == p - 1)
    m, c, tt, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while tt != 1:
        i, t2 = 0, tt
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        tt, r = tt * c % p, r * b % p
    return r


def constant_C(u: np.ndarray, Bsize: int) -> float:
    """max_{k != 0} |FFT(u)[k]| / sqrt(B), full k-range."""
    spec = np.abs(np.fft.fft(u))
    spec[0] = 0.0  # k = 0 is the trivial B
    return float(spec.max() / math.sqrt(Bsize))


# ---------------------------------------------------------------------------
# scaling fit
# ---------------------------------------------------------------------------


def fit_exponent(ps: list[int], ys: list[float]) -> float:
    """Least-squares slope of log(y) against log(p)."""
    lx = np.log(np.array(ps, dtype=float))
    ly = np.log(np.array(ys, dtype=float))
    return float(np.polyfit(lx, ly, 1)[0])


# --- model comparison -------------------------------------------------------
#
# The corpus fits a POWER LAW to C(p) and extrapolates it 240 bits. But the
# textbook heuristic for a pseudorandom subset of size B in Z/N is
# max_k |1hat_F(k)| ~ sqrt(B log N), i.e. C ~ sqrt(log p) -- a LOGARITHM, not a
# power. Over a range of p spanning a factor of a few hundred, sqrt(log p) is
# nearly indistinguishable from a small power, so a power-law fit will find a
# small positive exponent whether or not any power law exists. The two models
# disagree violently on extrapolation, which is the only place the fit is used:
#
#     at p = 2^256,   a*p^0.079  ~ 10^6      vs    a*sqrt(log p) ~ 13
#
# so this comparison, not the exponent, is the decision-relevant quantity.

MODELS = {
    "power_law:   C = a * p^b": lambda p: None,          # handled separately
    "sqrt_log:    C = a + b*sqrt(ln p)": lambda p: np.sqrt(np.log(p)),
    "log:         C = a + b*ln p": lambda p: np.log(p),
    "constant:    C = a": lambda p: np.zeros_like(np.asarray(p, dtype=float)),
}


def compare_models(ps: list[int], ys: list[float]) -> dict:
    """Fit each 2-parameter model, report RMS residual in C and the 2^256 value."""
    P = np.array(ps, dtype=float)
    Y = np.array(ys, dtype=float)
    out = {}
    for name, basis in MODELS.items():
        if name.startswith("power_law"):
            b, loga = np.polyfit(np.log(P), np.log(Y), 1)
            pred = np.exp(loga) * P**b
            extrap = float(np.exp(loga) * (2.0**256) ** b)
            params = {"a": float(np.exp(loga)), "b": float(b)}
        else:
            X = basis(P)
            A = np.vstack([np.ones_like(P), X]).T
            coef, *_ = np.linalg.lstsq(A, Y, rcond=None)
            pred = A @ coef
            x256 = basis(np.array([2.0**256]))[0]
            extrap = float(coef[0] + coef[1] * x256)
            params = {"a": float(coef[0]), "b": float(coef[1])}
        out[name] = {
            "params": {k: round(v, 6) for k, v in params.items()},
            "rms_residual": round(float(np.sqrt(np.mean((Y - pred) ** 2))), 5),
            "max_abs_residual": round(float(np.max(np.abs(Y - pred))), 5),
            "extrapolated_C_at_p_2^256": round(extrap, 3),
        }
    best = min(out, key=lambda k: out[k]["rms_residual"])
    out["_best_by_rms"] = best
    out["_spread_of_2^256_extrapolations"] = {
        k: v["extrapolated_C_at_p_2^256"] for k, v in out.items()
        if isinstance(v, dict) and "extrapolated_C_at_p_2^256" in v
    }
    return out


def bootstrap_exponent(ps, per_prime_values, stat, rng: np.random.Generator, reps=2000):
    """Bootstrap CI for the fitted exponent, resampling curves within each prime."""
    slopes = []
    for _ in range(reps):
        ys = []
        for vals in per_prime_values:
            draw = rng.choice(vals, size=len(vals), replace=True)
            ys.append(float(np.mean(draw)) if stat == "mean" else float(np.max(draw)))
        slopes.append(fit_exponent(ps, ys))
    lo, hi = np.percentile(slopes, [2.5, 97.5])
    return float(lo), float(hi)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="raw-result.json")
    ap.add_argument("--curves", type=int, default=24,
                    help="curves per prime -- MATCHED across primes, which is the point")
    ap.add_argument("--primes", type=int, nargs="*",
                    default=[1009, 4001, 9001, 50021, 100003, 200003])
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(SEED)
    nprng = np.random.default_rng(SEED)

    per_prime = []
    for p in args.primes:
        curves = find_prime_order_curves(p, args.curves, rng)
        vals = []
        for (A, B, N) in curves:
            u, Bsize, G = indicator_vector(p, A, B, N, p // 2)
            # VALIDITY GATE: the walk must have visited all N-1 affine points,
            # i.e. B/N must sit near 1/2. A wrong order silently truncates the
            # walk and inflates C; this is exactly the defect that produced
            # C = 20.7 in the first draft of this file.
            if not (0.3 < Bsize / N < 0.7):
                raise AssertionError(
                    f"walk truncated: p={p} A={A} B={B} N={N} |F|/N={Bsize/N:.3f}")
            vals.append(constant_C(u, Bsize))
        per_prime.append({
            "p": p,
            "log2_p": round(math.log2(p), 3),
            "curves_measured": len(curves),
            "B_over_N_mean": None,
            "C_mean": float(np.mean(vals)),
            "C_max": float(np.max(vals)),
            "C_std": float(np.std(vals, ddof=1)) if len(vals) > 1 else None,
            "C_values": [round(v, 4) for v in vals],
        })
        print(f"p={p:<8} n={len(curves):<3} C_mean={np.mean(vals):.3f} "
              f"C_max={np.max(vals):.3f}", file=sys.stderr, flush=True)

    ps = [r["p"] for r in per_prime]
    vals_by_p = [np.array(r["C_values"]) for r in per_prime]
    means = [r["C_mean"] for r in per_prime]
    maxes = [r["C_max"] for r in per_prime]

    e_mean = fit_exponent(ps, means)
    e_max = fit_exponent(ps, maxes)
    ci_mean = bootstrap_exponent(ps, vals_by_p, "mean", nprng)
    ci_max = bootstrap_exponent(ps, vals_by_p, "max", nprng)

    def verdict(name, e, ci):
        return {
            "statistic": name,
            "fitted_exponent": round(e, 4),
            "bootstrap_95_ci": [round(ci[0], 4), round(ci[1], 4)],
            "recorded_0.079_inside_ci": ci[0] <= 0.079 <= ci[1],
            "recorded_0.055_inside_ci": ci[0] <= 0.055 <= ci[1],
            "zero_inside_ci_i_e_no_growth": ci[0] <= 0.0 <= ci[1],
        }

    results = {
        "experiment_id": "EXP-HPSC-74991c",
        "seed": SEED,
        "curves_per_prime_matched": args.curves,
        "definition": {
            "factor_base": "F_t = {P in E(F_p) : x(P) < t} with t = floor(p/2)",
            "C": "max_{k != 0} |sum_{P in F_t} e(2 pi i k DL_G(P)/N)| / sqrt(|F_t|)",
            "k_range": "full, 1..N-1, via FFT -- not a truncated range",
        },
        "per_prime": per_prime,
        "scaling": {
            "C_mean": verdict("C_mean", e_mean, ci_mean),
            "C_max": verdict("C_max", e_max, ci_max),
            "mean_and_max_share_an_exponent": (
                max(ci_mean[0], ci_max[0]) <= min(ci_mean[1], ci_max[1])
            ),
        },
        "model_comparison": {
            "why": "The fitted exponent is only ever used to extrapolate to crypto "
                   "scale. A power law and a sqrt(log) are indistinguishable over "
                   "this range of p and disagree by ~5 orders of magnitude at "
                   "2^256, so which MODEL holds dominates what its parameter is.",
            "C_mean": compare_models(ps, means),
            "C_max": compare_models(ps, maxes),
        },
        "crypto_scale_extrapolation": {
            "note": "Extrapolation over ~240 bits from a fit spanning ~9 bits. "
                    "Reported because prior records report it, NOT because any of "
                    "it is reliable.",
            "p_bits": 256,
            "C_max_under_fitted_power_exponent": round(2 ** (256 * e_max), 2),
            "C_max_under_recorded_0.079": round(2 ** (256 * 0.079), 2),
            "C_max_under_sqrt_log_heuristic": round(math.sqrt(256 * math.log(2)), 2),
        },
    }
    blob = json.dumps(results, indent=2, sort_keys=True)
    open(args.out, "w").write(blob + "\n")
    print(blob)
    print(f"elapsed_seconds: {round(time.time()-t0,2)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
