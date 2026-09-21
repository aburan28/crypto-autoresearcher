"""EXP-ECDLP-869870 basin-partition coverage instrument (generic arm).

One code path for every selection rule; the rule is a configuration value.
All costs are counted group operations (one per walk step). Wall clock is
recorded by the wrapper and is never a decision variable here.

Seeds (contract seed_policy): walk-key seed s; target/online seed 100 + s;
generation-start stream 200 + s (NOT named by the contract -- a recorded
executor choice, see implementation.md); relabelling stream 300 + s;
tie-break permutation 400 + s; noise stream 500 + s.
"""
from __future__ import annotations

import hashlib
import math

import numpy as np

MASK64 = np.uint64(0xFFFFFFFFFFFFFFFF)
C1 = np.uint64(0xbf58476d1ce4e5b9)
C2 = np.uint64(0x94d049bb133111eb)
GOLDEN = 0x9E3779B97F4A7C15

RULES = ("published_weight", "count_only", "unselected", "generated_oracle", "global_oracle")


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
    """Walk key K and independent DP-predicate key K2 from the walk-key seed."""
    K = mix64_int((seed * GOLDEN + 0x1) & 0xFFFFFFFFFFFFFFFF)
    K2 = mix64_int((seed * GOLDEN + 0x2) & 0xFFFFFFFFFFFFFFFF) ^ 0xA5A5A5A5A5A5A5A5
    return K, K2


def cell_params(log2N: int, T: int, a: float, N: int | None = None) -> dict:
    """N defaults to 2^log2N (generic arm); the curve arm passes its prime N."""
    N = (1 << log2N) if N is None else int(N)
    W = math.sqrt(a * N / T)
    theta = 1.0 / W
    dp_threshold = int(math.floor(2.0 ** 64 / W))
    cap8 = int(round(8 * W))
    cap20 = int(round(20 * W))
    return {"log2N": log2N, "N": N, "T": T, "a": a, "W": W, "theta": theta,
            "dp_threshold": dp_threshold, "dp_density_exact": dp_threshold / 2.0 ** 64,
            "cap8": cap8, "cap20": cap20, "bits_per_entry": 2 * log2N}


def step_fn(x: np.ndarray, K: int, log2N: int) -> np.ndarray:
    """f(x) = top log2N bits of mix64(x XOR K)."""
    z = mix64(x.astype(np.uint64) ^ np.uint64(K))
    return (z >> np.uint64(64 - log2N)).astype(np.int64)


def is_dp_fn(x: np.ndarray, K2: int, threshold: int) -> np.ndarray:
    """DP predicate: hash64(x) < floor(2^64 / W) with the independent key K2."""
    z = mix64(x.astype(np.uint64) ^ np.uint64(K2))
    return z < np.uint64(threshold)


def build_map(N: int, log2N: int, K: int, K2: int, threshold: int, chunk: int = 1 << 21):
    """f and the DP indicator over all of [0, N), chunked to bound temporaries."""
    f = np.empty(N, dtype=np.int32)
    isdp = np.empty(N, dtype=bool)
    for lo in range(0, N, chunk):
        hi = min(N, lo + chunk)
        x = np.arange(lo, hi, dtype=np.int64)
        f[lo:hi] = step_fn(x, K, log2N)
        isdp[lo:hi] = is_dp_fn(x, K2, threshold)
    return f, isdp


def exact_first_dp(f: np.ndarray, isdp: np.ndarray, N: int):
    """Pointer jumping with DPs as absorbing fixed points.

    Returns (p, d, reach): p[x] = first DP on the forward orbit of x (or an
    arbitrary non-DP point if none is reached), d[x] = exact number of walk
    steps from x to p[x] (exact whenever reach[x]); reach[x] = the orbit hits
    a DP at all (no cap). A point with reach False lies on, or leads into, a
    DP-free cycle. Distances are exact for every reaching point since the
    doubling continues until 2^k exceeds N > any possible distance.
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
        # early exit: every point either points at a DP or its distance
        # already exceeds N (impossible for a reaching point)
        if rounds >= 8 and bool(np.all(isdp[p] | (d > N))):
            break
    reach = isdp[p]
    return p, d, reach, rounds


def basin_sizes_at_cap(p, d, reach, isdp, N, cap):
    """Exact basin size of every point index at cap (nonzero only at DPs).
    Basin includes the DP itself (distance 0)."""
    ok = reach & (d <= cap)
    bs = np.bincount(p[ok], minlength=N).astype(np.int64)
    capped_mass = int(np.count_nonzero(reach & (d > cap)))
    cycle_mass = int(np.count_nonzero(~reach))
    return bs, ok, capped_mass, cycle_mass


def compressed_hist(values: np.ndarray) -> dict:
    """{size: count} for a multiset of positive ints, plus top-1000 sizes."""
    v = np.asarray(values)
    v = v[v > 0]
    u, c = np.unique(v, return_counts=True)
    top = np.sort(v)[::-1][:1000]
    return {"sizes": u.tolist(), "counts": c.tolist(), "top1000": top.tolist(),
            "n_basins": int(v.size), "total_mass": int(v.sum())}


def survival_slope(sizes_u: np.ndarray, counts: np.ndarray, n_lo: float, n_hi: float,
                   n_points: int = 30):
    """Log-log least-squares slope of the survival function S(n) = P(|B| >= n)
    on n in [n_lo, n_hi] at a log-spaced grid. Returns (slope, intercept, grid used)."""
    total = counts.sum()
    if n_hi <= n_lo * 1.5:
        return float("nan"), float("nan"), 0
    grid = np.unique(np.round(np.exp(np.linspace(math.log(n_lo), math.log(n_hi), n_points))).astype(np.int64))
    # S(n) = sum counts over sizes >= n
    order = np.argsort(sizes_u)
    su = sizes_u[order]
    cc = counts[order]
    tail = np.cumsum(cc[::-1])[::-1]  # tail[i] = count with size >= su[i]
    pos = np.searchsorted(su, grid, side="left")
    S = np.where(pos < su.size, tail[np.minimum(pos, su.size - 1)], 0) / total
    m = S > 0
    if m.sum() < 3:
        return float("nan"), float("nan"), int(m.sum())
    X = np.log(grid[m]); Y = np.log(S[m])
    A = np.vstack([X, np.ones_like(X)]).T
    sol, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return float(sol[0]), float(sol[1]), int(m.sum())


def cutoff_fit(sizes_u: np.ndarray, counts: np.ndarray, W: float, n_lo: float = 10.0):
    """Joint fit log density(n) = c + b log n - n / n_c on log-binned density,
    n in [n_lo, 32 W^2]. Linear in (c, b, g = 1/n_c). Returns (b, n_c, n_c theta^2 / 2)."""
    n_hi = 32.0 * W * W
    edges = np.exp(np.arange(math.log(n_lo), math.log(n_hi) + 0.2, 0.2))
    edges = np.unique(np.round(edges)).astype(np.float64)
    if edges.size < 6:
        return float("nan"), float("nan"), float("nan"), 0
    h, _ = np.histogram(sizes_u.astype(np.float64), bins=edges, weights=counts.astype(np.float64))
    width = np.diff(edges)
    mid = np.sqrt(edges[:-1] * edges[1:])
    dens = h / width / counts.sum()
    m = dens > 0
    if m.sum() < 5:
        return float("nan"), float("nan"), float("nan"), int(m.sum())
    X1 = np.log(mid[m]); X2 = -mid[m]; Y = np.log(dens[m])
    A = np.vstack([np.ones_like(X1), X1, X2]).T
    sol, *_ = np.linalg.lstsq(A, Y, rcond=None)
    c, b, g = sol
    n_c = 1.0 / g if g > 0 else float("inf")
    theta = 1.0 / W
    return float(b), float(n_c), float(n_c * theta * theta / 2.0), int(m.sum())


def bootstrap_multiset(sizes_u, counts, fn, rng, reps=200):
    """Bootstrap a statistic of a basin multiset by multinomial resampling of
    its compressed histogram."""
    total = int(counts.sum())
    probs = counts / total
    vals = []
    for _ in range(reps):
        c = rng.multinomial(total, probs)
        vals.append(fn(sizes_u, c))
    vals = np.array(vals, dtype=np.float64)
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        return [float("nan"), float("nan")]
    return [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float, float]:
    if n == 0:
        return float("nan"), float("nan"), float("nan")
    ph = k / n
    den = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / den
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / den
    return ph, centre - half, centre + half


def table_hash(dps: np.ndarray) -> str:
    s = np.sort(np.asarray(dps, dtype=np.int64))
    return hashlib.sha256(s.tobytes()).hexdigest()


def select_top(stat: np.ndarray, perm: np.ndarray, T: int) -> np.ndarray:
    """Indices (into the pool) of the T largest stat, ties broken by the seeded
    permutation (larger perm value first, purely conventional). Every rule
    goes through this one function."""
    order = np.lexsort((perm, stat))[::-1]  # primary: stat desc, secondary: perm desc
    return order[:T]


def select_rule(rule: str, pool: dict, T: int, perm: np.ndarray, W: float,
                bs_cap: np.ndarray, all_dps_sizes=None, all_dps_perm=None, all_dps=None):
    """ONE code path: returns the selected DP identities for a rule.
    pool: {'dps', 'h', 'S'} arrays over the generated pool.
    """
    if rule == "published_weight":
        stat = pool["S"].astype(np.float64) + 4.0 * W * pool["h"].astype(np.float64)
    elif rule == "count_only":
        stat = pool["h"].astype(np.float64)
    elif rule == "unselected":
        stat = np.zeros(pool["dps"].size, dtype=np.float64)   # permutation alone decides
    elif rule == "generated_oracle":
        stat = bs_cap[pool["dps"]].astype(np.float64)
    elif rule == "global_oracle":
        idx = select_top(all_dps_sizes.astype(np.float64), all_dps_perm, T)
        return all_dps[idx]
    else:
        raise ValueError(rule)
    idx = select_top(stat, perm, T)
    return pool["dps"][idx]


def rule_statistic(rule: str, pool: dict, W: float) -> np.ndarray:
    if rule == "published_weight":
        return pool["S"].astype(np.float64) + 4.0 * W * pool["h"].astype(np.float64)
    if rule == "count_only":
        return pool["h"].astype(np.float64)
    raise ValueError(rule)


def exact_coverage(table: np.ndarray, bs: np.ndarray, N: int) -> float:
    return float(bs[table].sum()) / N


def online_eval(table: np.ndarray, term_dp: np.ndarray, term_ok: np.ndarray, lengths: np.ndarray,
                N: int, T: int, isdp_table_mask: np.ndarray) -> dict:
    """Sampled coverage and the paper's cost metric for a table over the M
    online walks. lengths already include the cap charge for capped walks."""
    M = term_dp.size
    hit = term_ok & isdp_table_mask[term_dp]
    hits = int(hit.sum())
    total_steps = int(lengths.sum())
    ph, lo, hi = wilson(hits, M)
    scaled = (total_steps / hits / math.sqrt(N / T)) if hits else float("inf")
    return {"M": M, "hits": hits, "c_hat": ph, "wilson_lo": lo, "wilson_hi": hi,
            "total_steps": total_steps, "scaled_cost_sampled": scaled}
