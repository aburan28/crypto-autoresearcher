"""EXP-ECDLP-e962f6 verification instrument (Stages 1-2).

ONE code path for all objects; the object is selected by configuration:
  - walk object: uniformly random function | uniformly random permutation
  - distinguishing rule: uniform theta | non-uniform {0, 2theta}

Key derivation (splitmix64 finalizer, walk_keys) is byte-identical to the
committed EXP-ECDLP-869870 instrument (experiments/EXP-ECDLP-869870/source/
instrument.py at origin/main e5859ae9bb) so that the DP marking is the same
instrument as the committed runs.

Key-derivation convention for this contract (recorded in every manifest):
  - "walk_key seed s"  -> K  = walk_keys(s)[0]   (the walk-key component)
  - "dp_key seed s"    -> K2 = walk_keys(s)[1]   (the DP-key component,
    i.e. mix64_int((s*GOLDEN+2) & MASK) ^ 0xA5A5A5A5A5A5A5A5, exactly the
    DP-key derivation of the committed instrument)

Non-uniform {0, 2theta} rule (RUN-006), a deterministic function of the
point: h(x) = mix64(x XOR K2); the "even-hash half" is h(x) & 1 == 0.
  - even-hash half: marked iff h(x) < 2*threshold  (density 2theta within
    the half, since threshold = floor(2^64 / W) = 2^64 * theta)
  - odd-hash half:  never marked (density 0)
  - average density = (1/2)(2theta) + (1/2)(0) = theta

Observations only; no interpretation.
"""
from __future__ import annotations

import math

import numpy as np

MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
C1 = np.uint64(0xbf58476d1ce4e5b9)
C2 = np.uint64(0x94d049bb133111eb)
GOLDEN = 0x9E3779B97F4A7C15


def mix64(z: np.ndarray) -> np.ndarray:
    """splitmix64 finalizer on uint64 arrays (wraparound multiply)."""
    z = z.astype(np.uint64, copy=True)
    z ^= z >> np.uint64(30)
    z *= C1
    z ^= z >> np.uint64(27)
    z *= C2
    z ^= z >> np.uint64(31)
    return z


def mix64_int(x: int) -> int:
    x &= 0xFFFFFFFFFFFFFFFF
    x ^= x >> 30
    x = (x * 0xbf58476d1ce4e5b9) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 27
    x = (x * 0x94d049bb133111eb) & 0xFFFFFFFFFFFFFFFF
    x ^= x >> 31
    return x


def walk_keys(seed: int) -> tuple[int, int]:
    """Walk key K and independent DP-predicate key K2 from a seed.
    Byte-identical to the committed EXP-ECDLP-869870 instrument."""
    K = mix64_int((seed * GOLDEN + 0x1) & 0xFFFFFFFFFFFFFFFF)
    K2 = mix64_int((seed * GOLDEN + 0x2) & 0xFFFFFFFFFFFFFFFF) ^ 0xA5A5A5A5A5A5A5A5
    return K, K2


def cell_params(log2N: int, T: int, a: float) -> dict:
    """N = 2^log2N; W = sqrt(a N / T); theta = 1/W; threshold = floor(2^64/W).
    The contract's definition W = sqrt(a N / T) is the authoritative one."""
    N = 1 << log2N
    W = math.sqrt(a * N / T)
    theta = 1.0 / W
    dp_threshold = int(math.floor(2.0 ** 64 / W))
    cap8 = int(round(8 * W))
    return {"log2N": log2N, "N": N, "T": T, "a": a, "W": W, "theta": theta,
            "dp_threshold": dp_threshold, "dp_density_exact": dp_threshold / 2.0 ** 64,
            "cap8": cap8}


def step_fn(x: np.ndarray, K: int, log2N: int) -> np.ndarray:
    """f(x) = top log2N bits of mix64(x XOR K) (uniformly random function)."""
    z = mix64(x.astype(np.uint64) ^ np.uint64(K))
    return (z >> np.uint64(64 - log2N)).astype(np.int32)


def is_dp_fn(x: np.ndarray, K2: int, threshold: int) -> np.ndarray:
    """Uniform DP predicate: hash64(x) < floor(2^64 / W) with key K2."""
    z = mix64(x.astype(np.uint64) ^ np.uint64(K2))
    return z < np.uint64(threshold)


def is_dp_nonuniform_fn(x: np.ndarray, K2: int, threshold: int) -> np.ndarray:
    """Non-uniform {0, 2theta} rule (see module docstring)."""
    z = mix64(x.astype(np.uint64) ^ np.uint64(K2))
    even = (z & np.uint64(1)) == np.uint64(0)
    return even & (z < np.uint64(2 * threshold))


def build_map(N: int, log2N: int, K: int, K2: int, threshold: int,
              rule: str = "uniform", chunk: int = 1 << 21):
    """f and the DP indicator over all of [0, N), chunked to bound temporaries."""
    f = np.empty(N, dtype=np.int32)
    isdp = np.empty(N, dtype=bool)
    dp_fn = is_dp_fn if rule == "uniform" else is_dp_nonuniform_fn
    for lo in range(0, N, chunk):
        hi = min(N, lo + chunk)
        x = np.arange(lo, hi, dtype=np.int64)
        f[lo:hi] = step_fn(x, K, log2N)
        isdp[lo:hi] = dp_fn(x, K2, threshold)
    return f, isdp


def random_permutation(N: int, seed: int) -> np.ndarray:
    """Uniformly random permutation on [0, N) via the Fisher-Yates draw
    (numpy's permutation of an integer range is a Fisher-Yates shuffle)."""
    rng = np.random.default_rng(seed)
    return rng.permutation(N).astype(np.int32)


def exact_first_dp(f: np.ndarray, isdp: np.ndarray, N: int):
    """Pointer jumping with DPs as absorbing fixed points.

    Returns (p, d, reach, rounds): p[x] = first DP on the forward orbit of x
    (or an arbitrary non-DP point if none is reached), d[x] = exact number of
    walk steps from x to p[x] (exact whenever reach[x]), reach[x] = the orbit
    hits a DP at all (no cap). Identical to the committed EXP-ECDLP-869870
    instrument. Works for random functions and for permutations alike.
    """
    idx = np.arange(N, dtype=np.int32)
    p = np.where(isdp, idx, f).astype(np.int32)
    d = np.where(isdp, 0, 1).astype(np.int32)
    rounds = 0
    k = 1
    while True:
        dp_ = d[p]
        d = d + dp_
        p = p[p]
        rounds += 1
        k *= 2
        del dp_
        if k > N:
            break
        if rounds >= 8 and bool(np.all(isdp[p] | (d > N))):
            break
    reach = isdp[p]
    return p, d, reach, rounds


def basin_sizes_at_cap(p, d, reach, N, cap):
    """Exact basin size of every point index at cap (nonzero only at DPs).
    Basin includes the DP itself (distance 0)."""
    ok = reach & (d <= cap)
    bs = np.bincount(p[ok], minlength=N).astype(np.int64)
    capped_mass = int(np.count_nonzero(reach & (d > cap)))
    cycle_mass = int(np.count_nonzero(~reach))
    return bs, ok, capped_mass, cycle_mass


def basin_sizes_uncapped(p, d, reach, N):
    """Basin sizes with no cap (used by the permutation control, whose
    contract text specifies full cycle segments)."""
    bs = np.bincount(p[reach], minlength=N).astype(np.int64)
    return bs


def compressed_hist(values: np.ndarray) -> dict:
    """{size: count} for a multiset of positive ints, plus top-1000 sizes."""
    v = np.asarray(values)
    v = v[v > 0]
    u, c = np.unique(v, return_counts=True)
    top = np.sort(v)[::-1][:1000]
    return {"sizes": u.tolist(), "counts": c.tolist(), "top1000": top.tolist(),
            "n_basins": int(v.size), "total_mass": int(v.sum())}


def select_top(stat: np.ndarray, perm: np.ndarray, T: int) -> np.ndarray:
    """Indices of the T largest stat, ties broken by the seeded permutation
    (larger perm value first, purely conventional). Same as the committed
    instrument."""
    order = np.lexsort((perm, stat))[::-1]
    return order[:T]


def table_hash(dps: np.ndarray) -> str:
    import hashlib
    s = np.sort(np.asarray(dps, dtype=np.int64))
    return hashlib.sha256(s.tobytes()).hexdigest()


# ---------------------------------------------------------------------------
# MODELED quantities (B1)-(B3) of IDEA-20260906-aed829, as carried in
# IDEA-20260906-ac100b. Everything here is a MODEL number.
# ---------------------------------------------------------------------------

def c_rand(a_m: float) -> float:
    """(B1) unselected law: 1 - (1 + 2 a_m)^{-1/2}."""
    return 1.0 - (1.0 + 2.0 * a_m) ** -0.5


def _g(x: float) -> float:
    """Root-equation LHS: 2 x^{-1/2} e^{-x/2} - sqrt(2 pi) erfc(sqrt(x/2))."""
    return 2.0 * x ** -0.5 * math.exp(-x / 2.0) - math.sqrt(2.0 * math.pi) * math.erfc(math.sqrt(x / 2.0))


def _gprime(x: float) -> float:
    """d/dx of _g: -e^{-x/2} x^{-3/2} (derived; g is strictly decreasing)."""
    return -math.exp(-x / 2.0) * x ** -1.5


def solve_xstar(a: float, bisect_iters: int = 100, newton_iters: int = 60) -> float:
    """(B2): x* solving _g(x) = a sqrt(2 pi). Method per the frozen contract:
    bisection bracketing plus Newton refinement; erfc from math.erfc
    (Python standard library)."""
    target = a * math.sqrt(2.0 * math.pi)
    lo, hi = 1e-9, 50.0
    for _ in range(bisect_iters):
        mid = 0.5 * (lo + hi)
        if _g(mid) > target:
            lo = mid
        else:
            hi = mid
    x = 0.5 * (lo + hi)
    for _ in range(newton_iters):
        residual = _g(x) - target
        gpx = _gprime(x)
        if gpx == 0.0:
            break
        x_new = x - residual / gpx
        if x_new <= 0.0:
            x_new = 0.5 * x
        if abs(x_new - x) <= 1e-16 * max(1.0, abs(x)):
            x = x_new
            break
        x = x_new
    return x


def c_max(a: float) -> float:
    """(B2) oracle ceiling C_max(a) = erfc(sqrt(x*/2))."""
    return math.erfc(math.sqrt(solve_xstar(a) / 2.0))


def b3_oracle_constant(a: float) -> float:
    """(B3): L sqrt(T/N) = sqrt(a) / C_max(a)."""
    return math.sqrt(a) / c_max(a)


def borel_log_pmf(mu: float, nmax: int) -> np.ndarray:
    """log P(n) for n = 1..nmax of Borel(mu): e^{-mu n} (mu n)^{n-1} / n!."""
    n = np.arange(1, nmax + 1, dtype=np.float64)
    log_fact = np.cumsum(np.log(n))
    lp = -mu * n + (n - 1.0) * np.log(mu * n) - log_fact
    out = np.full(nmax + 1, -np.inf)
    out[1:] = lp
    return out


def borel_max_band(theta: float, K: float, W: float, q_lo=0.005, q_hi=0.995) -> dict:
    """99% band for the maximum of K i.i.d. Borel(1 - theta) samples
    (the contract's 'Borel(1-theta) N/W-sample order-statistic 99% band').
    Same estimator as the committed EXP-ECDLP-869870 model. MODEL number."""
    mu = 1.0 - theta
    nmax = int(max(1000, 80 * W * W))
    lp = borel_log_pmf(mu, nmax)
    pmf = np.exp(lp[1:])
    cdf = np.cumsum(pmf)
    total = float(cdf[-1])
    cdf = np.minimum(cdf, 1.0)
    logF = np.log(np.clip(cdf, 1e-300, 1.0))
    P = np.exp(K * logF)
    n = np.arange(1, nmax + 1)
    lo = int(n[np.searchsorted(P, q_lo)]) if P[-1] >= q_lo else None
    hi = int(n[np.searchsorted(P, q_hi)]) if P[-1] >= q_hi else None
    return {"n_lo": lo, "n_hi": hi, "K": K, "mu": mu, "pmf_mass_to_nmax": total, "nmax": nmax}


def geometric_cdf_zero_based(k, theta: float):
    """CDF of the zero-based Geometric(theta): P(L <= k) = 1 - (1-theta)^{k+1}
    for integer k >= 0 (L = number of steps to the first mark, 0 if the start
    is marked). Matches the measured distance array d[x]."""
    k = np.asarray(k, dtype=np.float64)
    out = np.zeros_like(k)
    m = k >= 0
    out[m] = 1.0 - (1.0 - theta) ** (k[m] + 1.0)
    return out


def geometric_cdf_one_based(k, theta: float):
    """CDF of the one-based Geometric(theta) (scipy convention):
    P(L <= k) = 1 - (1-theta)^k for integer k >= 1, 0 for k < 1. Mean W."""
    k = np.asarray(k, dtype=np.float64)
    out = np.zeros_like(k)
    m = k >= 1
    out[m] = 1.0 - (1.0 - theta) ** k[m]
    return out


def geometric_cdf_segment(k, theta: float):
    """CDF for cycle-segment sizes (permutation control): the segment includes
    its DP, so S >= 1 with P(S = k) = (1-theta)^{k-1} theta; CDF
    P(S <= k) = 1 - (1-theta)^k for k >= 1."""
    return geometric_cdf_one_based(k, theta)


def ks_against_cdf(samples: np.ndarray, cdf) -> tuple[float, float]:
    """Two-sided KS statistic and asymptotic p-value of integer samples
    against a reference CDF (function of the sample value)."""
    from scipy import stats
    res = stats.kstest(np.asarray(samples, dtype=np.float64), cdf)
    return float(res.statistic), float(res.pvalue)


def spearman_rho(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (Pearson on ranks)."""
    rx = np.argsort(np.argsort(x)).astype(np.float64)
    ry = np.argsort(np.argsort(y)).astype(np.float64)
    return float(np.corrcoef(rx, ry)[0, 1])


def spearman_pvalue(rho: float, n: int) -> float:
    """Two-sided p-value via the t approximation t = rho sqrt((n-2)/(1-rho^2))."""
    from scipy import stats
    if n < 3 or abs(rho) >= 1.0:
        return 0.0
    t = rho * math.sqrt((n - 2) / (1.0 - rho * rho))
    return float(2.0 * stats.t.sf(abs(t), n - 2))
