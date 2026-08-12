"""EXP-FB3-001 core: curves, factor-base geometries, exact decomposition counting.

Frozen contract: experiments/EXP-FB3-001/specification.yaml (version 1, approved).
Frozen operational definitions: experiments/EXP-FB3-001/amendment-001.yaml
(EXP-FB3-001-AMD-001, approved).

Counting convention (inherited verbatim from the H016 record in
inputs/h100_session/h016_base_yield.json so that the new cells are comparable
with the two prior cells):

  * a factor base is a set D of B distinct nonzero elements of a cyclic group of
    prime order N, identified with their discrete logs;
  * a decomposition of target r is a MULTISET {i <= j <= k} of base elements
    with d_i + d_j + d_k = r  (m = 3, no signs);
  * discrete logs are known BY CONSTRUCTION.  They are used only to count
    decompositions.  No cost, speedup, or attack claim follows from their
    availability, and nothing here is a step of an attack.

All counting in this module is exact integer arithmetic over the whole target
space (all N targets), per amendment change AMD-2-exact-yield.  Sampling error
is therefore absent from the primary metric; the only remaining randomness is
the replicate axis (curves x seeds) and the matched-random null draws.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field

import numpy as np
import sympy

# --------------------------------------------------------------------------
# Frozen operational constants.  These are executor pinnings of quantities the
# frozen contract leaves in prose; they are recorded in every run's
# raw-result.json and in implementation/implementation.md.  They are fixed
# before execution and are not adjusted after seeing any measurement.
# --------------------------------------------------------------------------

FROZEN = {
    "m": 3,
    "matched_size_rule": "B = ceil((6*N)**(1/3))",
    "size_window_rel": 0.02,        # |N - N_target| / N_target <= 0.02
    "p_window_rel": 0.005,          # p drawn within +-0.5% of N_target
    "curve_seed_base": 20260724,
    "cell_seed_base": 70160724,
    "null_draws": 100,              # >= 100 per (curve, N, seed) per typing pattern
    "bootstrap_resamples": 2000,
    "bootstrap_seed": 4242,
    "pvalue_convention": "(r+1)/(n+1), r = #{null draws at least as extreme}",
    "family_size_per_size": 8,      # 6 new geometries + 2 prior (H016/H017) cells
    "holm_alpha": 0.05,
    "concentration_statistic": "sum_r c(r)*(c(r)-1) / n_targets (ordered pairs "
                              "of distinct decompositions of the same target)",
    "height_H_schedule": [16, 32, 64, 128, 256, 512, 1024],
    "greedy_pool_factor": 4,
    "greedy_split_rule": "seeded permutation of [0,N); first floor(N/2) indices "
                         "are TRAINING, remainder is HELD-OUT",
    "mixed_sub_base_sizes": "ceil(B/2) x-interval, floor(B/2) small multiples",
    "mixed_primary_typing": "two from sub-base 1 (x-interval), one from "
                            "sub-base 2 (small multiples): pre-declared as the "
                            "cell's primary typing because with B1 >= B2 its "
                            "closed-form total C(B1+1,2)*B2 is the larger of "
                            "the two typings -- a size-only rule fixed before "
                            "any measurement.  Both typings are reported.",
    "asym_ladder_weights": [[1, 1, 1], [2, 1, 1], [4, 1, 1], [8, 1, 1]],
    "asym_primary_split_weights": [8, 1, 1],
    "asym_element_choice": "sub-bases are disjoint uniform random logs from the "
                           "recorded cell seed; the frozen definition pins only "
                           "the SIZES, so elements are left unstructured to "
                           "isolate the sizing effect that H004 claims.",
    "typed_family_control": "untyped matched-random base of the same TOTAL size "
                            "B (the frozen control 'matched random base, same "
                            "size'); the same-typing matched-random control is "
                            "also reported for every typed cell.",
    "coset_order": "ascending x within each coset, cosets in order i = 0,1,2,...",
}


def matched_size(n_order: int) -> int:
    """B = ceil((6 N)^(1/3)) (frozen matched_size rule)."""
    b = int(round((6.0 * n_order) ** (1.0 / 3.0)))
    while b ** 3 < 6 * n_order:
        b += 1
    while (b - 1) ** 3 >= 6 * n_order:
        b -= 1
    return b


def total_untyped_m3(b: int) -> int:
    """binomial(B+2, 3) -- the exact total over all targets (conservation)."""
    return b * (b + 1) * (b + 2) // 6


# --------------------------------------------------------------------------
# Curve arithmetic over F_p:  y^2 = x^3 + a x + b, short Weierstrass.
# --------------------------------------------------------------------------

Point = tuple[int, int] | None   # None is the point at infinity


def ec_add(p: int, a: int, pt1: Point, pt2: Point) -> Point:
    if pt1 is None:
        return pt2
    if pt2 is None:
        return pt1
    x1, y1 = pt1
    x2, y2 = pt2
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_mul(p: int, a: int, k: int, pt: Point) -> Point:
    """Double-and-add scalar multiplication (independent of the table build)."""
    res: Point = None
    cur = pt
    while k:
        if k & 1:
            res = ec_add(p, a, res, cur)
        cur = ec_add(p, a, cur, cur)
        k >>= 1
    return res


def on_curve(p: int, a: int, b: int, pt: Point) -> bool:
    if pt is None:
        return True
    x, y = pt
    return (y * y - x * x * x - a * x - b) % p == 0


def qr_table(p: int) -> np.ndarray:
    """Boolean table: is v a nonzero quadratic residue mod p."""
    tab = np.zeros(p, dtype=bool)
    s = (np.arange(1, p, dtype=np.int64) ** 2) % p
    tab[s] = True
    return tab


def curve_order_char_sum(p: int, a: int, b: int, isqr: np.ndarray | None = None) -> int:
    """#E(F_p) = p + 1 + sum_x legendre(x^3 + a x + b, p)  (exact character sum)."""
    if isqr is None:
        isqr = qr_table(p)
    x = np.arange(p, dtype=np.int64)
    v = (x * x % p * x + a * x + b) % p
    nz = v != 0
    hit = isqr[v]
    n_res = int(np.count_nonzero(hit & nz))
    n_non = int(np.count_nonzero(~hit & nz))
    # legendre = +1 on nonzero residues, -1 on non-residues, 0 on v == 0
    return p + 1 + (n_res - n_non)


def hasse_interval(p: int) -> tuple[float, float]:
    r = 2.0 * math.sqrt(p)
    return (p + 1 - r, p + 1 + r)


@dataclass
class Curve:
    bits: int
    curve_index: int
    seed: int
    p: int
    a: int
    b: int
    n_order: int
    tries: int
    window_rejects: int
    order_rejects: int
    gx: int
    gy: int
    xs: np.ndarray = field(repr=False)          # xs[k] = x(kG), k = 1..N-1
    log_of_x: np.ndarray = field(repr=False)    # log of the canonical point at x, else 0
    checks: dict = field(default_factory=dict)

    @property
    def point_xs(self) -> np.ndarray:
        """Ascending array of every x that is the x-coordinate of a point."""
        return np.flatnonzero(self.log_of_x > 0)


def find_curve(bits: int, curve_index: int, n_target: int) -> Curve:
    """Frozen curve generation (amendment frozen_definitions.group_and_curves)."""
    seed = FROZEN["curve_seed_base"] * 1000 + bits * 10 + curve_index
    rng = np.random.default_rng(seed)
    lo = int(n_target * (1.0 - FROZEN["p_window_rel"]))
    hi = int(n_target * (1.0 + FROZEN["p_window_rel"]))
    p = int(sympy.nextprime(int(rng.integers(lo, hi))))
    isqr = qr_table(p)
    wlo = n_target * (1.0 - FROZEN["size_window_rel"])
    whi = n_target * (1.0 + FROZEN["size_window_rel"])
    tries = 0
    window_rejects = 0
    order_rejects = 0
    while True:
        tries += 1
        a = int(rng.integers(0, p))
        b = int(rng.integers(0, p))
        if (4 * a * a * a + 27 * b * b) % p == 0:      # singular
            order_rejects += 1
            continue
        n_order = curve_order_char_sum(p, a, b, isqr)
        if not sympy.isprime(n_order):
            order_rejects += 1
            continue
        if not (wlo <= n_order <= whi):
            window_rejects += 1
            continue
        break
    # Take G as any point of that order: prime order => any affine point works.
    gx, gy = None, None
    for x in range(1, p):
        v = (x * x * x + a * x + b) % p
        if v == 0 or not isqr[v]:
            continue
        y = int(sympy.sqrt_mod(v, p))
        gx, gy = x, min(y, p - y)
        break
    assert gx is not None
    xs, ys = _enumerate_multiples(p, a, n_order, gx, gy)
    log_of_x = np.zeros(p, dtype=np.int64)
    canon = (2 * ys[1:n_order]) < p           # exactly one of k, N-k is canonical
    idx = np.flatnonzero(canon) + 1
    log_of_x[xs[idx]] = idx
    curve = Curve(bits=bits, curve_index=curve_index, seed=seed, p=p, a=a, b=b,
                  n_order=n_order, tries=tries, window_rejects=window_rejects,
                  order_rejects=order_rejects, gx=gx, gy=gy, xs=xs,
                  log_of_x=log_of_x)
    curve.checks = verify_curve(curve, ys)
    return curve


def _enumerate_multiples(p: int, a: int, n_order: int, gx: int, gy: int):
    """xs[k], ys[k] = affine coordinates of k*G for k = 1..N-1 (exact table)."""
    xs = np.zeros(n_order, dtype=np.int64)
    ys = np.zeros(n_order, dtype=np.int64)
    xs[1], ys[1] = gx, gy
    x, y = gx, gy
    for k in range(2, n_order):
        if x == gx and y == gy:
            lam = (3 * x * x + a) * pow(2 * y, -1, p) % p       # k == 2: doubling
        elif x == gx:
            # (k-1)G == -G would mean k-1 == N-1, i.e. k == N, outside this loop.
            raise AssertionError("premature return to -G: order mismatch")
        else:
            lam = (y - gy) * pow(x - gx, -1, p) % p
        x2 = (lam * lam - x - gx) % p
        y2 = (lam * (x - x2) - y) % p
        x, y = x2, y2
        xs[k], ys[k] = x, y
    return xs, ys


def verify_curve(curve: Curve, ys: np.ndarray) -> dict:
    """Independent verification of the group order and the dlog table.

    The character-sum order is cross-checked by a completely different route:
    the enumeration closes exactly at N, N*G = O by double-and-add, N is prime
    and lies in the Hasse interval.  Since ord(G) = N divides #E and
    #E <= p + 1 + 2 sqrt(p) < 2N, this forces #E = N.
    """
    p, a, n = curve.p, curve.a, curve.n_order
    lo, hi = hasse_interval(p)
    xs = curve.xs
    checks = {
        "order_prime": bool(sympy.isprime(n)),
        "order_in_hasse_interval": bool(lo <= n <= hi),
        "hasse_interval": [lo, hi],
        "generator_on_curve": on_curve(p, a, b=curve.b, pt=(curve.gx, curve.gy)),
        "N_times_G_is_identity": ec_mul(p, a, n, (curve.gx, curve.gy)) is None,
        "table_closes_at_N": bool(xs[n - 1] == curve.gx
                                  and (ys[n - 1] + curve.gy) % p == 0),
        "distinct_x_count": int(np.unique(xs[1:n]).size),
        "expected_distinct_x_count": (n - 1) // 2,
        "hasse_uniqueness_argument": ("ord(G)=N divides #E and "
                                      "#E <= p+1+2sqrt(p) < 2N, so #E = N"),
    }
    checks["distinct_x_ok"] = (checks["distinct_x_count"]
                               == checks["expected_distinct_x_count"])
    checks["point_x_count"] = int(np.count_nonzero(curve.log_of_x > 0))
    checks["point_x_count_ok"] = checks["point_x_count"] == (n - 1) // 2
    # y-pairing: for every k, x(kG) == x((N-k)G) and the y's sum to p.
    k = np.arange(1, n)
    checks["x_pairing_ok"] = bool(np.array_equal(xs[k], xs[n - k]))
    checks["y_pairing_ok"] = bool(np.all((ys[k] + ys[n - k]) % p == 0))
    # Independent spot check of the table with double-and-add.
    rng = np.random.default_rng(curve.seed + 7)
    spot = sorted(int(v) for v in rng.integers(1, n, size=20))
    ok = True
    for kk in spot:
        pt = ec_mul(p, a, kk, (curve.gx, curve.gy))
        ok = ok and pt is not None and pt[0] == int(xs[kk]) and pt[1] == int(ys[kk])
    checks["double_and_add_spot_check"] = {"k": spot, "all_match": bool(ok)}
    # dlog table is a bijection from canonical points onto logs.
    logs = curve.log_of_x[curve.log_of_x > 0]
    checks["dlog_table_bijection"] = bool(np.unique(logs).size == logs.size)
    checks["all_ok"] = bool(checks["order_prime"] and checks["order_in_hasse_interval"]
                            and checks["generator_on_curve"]
                            and checks["N_times_G_is_identity"]
                            and checks["table_closes_at_N"]
                            and checks["distinct_x_ok"] and checks["point_x_count_ok"]
                            and checks["x_pairing_ok"] and checks["y_pairing_ok"]
                            and ok and checks["dlog_table_bijection"])
    return checks


# --------------------------------------------------------------------------
# Exact decomposition counters.  Three independent implementations:
#   counts_untyped_m3        -- Burnside orbit count via exact integer bincount
#   counts_untyped_m3_direct -- direct enumeration of multisets i <= j <= k
#   counts_untyped_m3_fft    -- cyclic-convolution/FFT route (rounding audited)
# --------------------------------------------------------------------------

def _bincount_sums(sums: np.ndarray, n_order: int) -> np.ndarray:
    return np.bincount(sums.ravel(), minlength=n_order).astype(np.int64)


def counts_untyped_m3(n_order: int, logs: np.ndarray) -> np.ndarray:
    """Exact per-target multiset-of-3 counts, all N targets, integer arithmetic.

    Burnside over S_3 acting on ordered triples:
        c = (T + 3 U + 2 V) / 6
    with T = #ordered triples summing to r, U = #(2 d_i + d_j = r),
    V = #(3 d_i = r).  No floating point anywhere.
    """
    logs = np.asarray(logs, dtype=np.int64)
    b = logs.size
    pair = (logs[:, None] + logs[None, :]).ravel() % n_order          # B^2
    total = np.zeros(n_order, dtype=np.int64)
    step = max(1, int(4_000_000 // max(1, pair.size)))
    for s in range(0, b, step):
        blk = (pair[:, None] + logs[None, s:s + step]) % n_order
        total += _bincount_sums(blk, n_order)
    u = _bincount_sums((2 * logs[:, None] + logs[None, :]).ravel() % n_order, n_order)
    v = _bincount_sums((3 * logs) % n_order, n_order)
    num = total + 3 * u + 2 * v
    if np.any(num % 6):
        raise AssertionError("Burnside numerator not divisible by 6 "
                             "(implementation_error)")
    return num // 6


def counts_untyped_m3_direct(n_order: int, logs: np.ndarray) -> np.ndarray:
    """Exact counts by direct enumeration of multisets i <= j <= k."""
    logs = np.asarray(logs, dtype=np.int64)
    b = logs.size
    ii, jj = np.triu_indices(b)
    pair = logs[ii] + logs[jj]
    out = np.zeros(n_order, dtype=np.int64)
    for k in range(b):
        sel = jj <= k
        out += _bincount_sums((pair[sel] + logs[k]) % n_order, n_order)
    return out


def counts_untyped_m3_fft(n_order: int, logs: np.ndarray) -> tuple[np.ndarray, float]:
    """Exact counts via cyclic convolution (FFT), with rounding audit.

    c = (irfft(F(A)^3 + 3 F(A) F(A2)) + 2 A3) / 6, per the amendment's
    O(N log N) route.  Returns (counts, max |value - round(value)|).
    """
    logs = np.asarray(logs, dtype=np.int64) % n_order
    vec_a = np.zeros(n_order)
    vec_a[logs] = 1.0
    vec_a2 = np.zeros(n_order)
    vec_a2[(2 * logs) % n_order] = 1.0
    vec_a3 = np.zeros(n_order)
    vec_a3[(3 * logs) % n_order] = 1.0
    fa = np.fft.rfft(vec_a)
    fa2 = np.fft.rfft(vec_a2)
    conv = np.fft.irfft(fa ** 3 + 3.0 * fa * fa2, n=n_order)
    raw = conv + 2.0 * vec_a3
    rounded = np.rint(raw)
    err = float(np.max(np.abs(raw - rounded)))
    num = rounded.astype(np.int64)
    if np.any(num % 6):
        raise AssertionError("FFT numerator not divisible by 6 after rounding")
    return num // 6, err


def counts_typed_111(n_order: int, l1, l2, l3) -> np.ndarray:
    """Exact counts for typed decompositions: one element from each sub-base."""
    l1 = np.asarray(l1, dtype=np.int64)
    l2 = np.asarray(l2, dtype=np.int64)
    l3 = np.asarray(l3, dtype=np.int64)
    pair = (l1[:, None] + l2[None, :]).ravel() % n_order
    out = np.zeros(n_order, dtype=np.int64)
    step = max(1, int(4_000_000 // max(1, pair.size)))
    for s in range(0, l3.size, step):
        blk = (pair[:, None] + l3[None, s:s + step]) % n_order
        out += _bincount_sums(blk, n_order)
    return out


def counts_typed_1_2(n_order: int, l_single, l_pair) -> np.ndarray:
    """Exact counts: one element from l_single, a 2-multiset from l_pair."""
    l_single = np.asarray(l_single, dtype=np.int64)
    l_pair = np.asarray(l_pair, dtype=np.int64)
    ii, jj = np.triu_indices(l_pair.size)
    pair = (l_pair[ii] + l_pair[jj]) % n_order
    out = np.zeros(n_order, dtype=np.int64)
    step = max(1, int(4_000_000 // max(1, pair.size)))
    for s in range(0, l_single.size, step):
        blk = (pair[:, None] + l_single[None, s:s + step]) % n_order
        out += _bincount_sums(blk, n_order)
    return out


def brute_force_counts(n_order: int, logs) -> np.ndarray:
    """Reference counter: literal enumeration of multisets, pure Python."""
    out = np.zeros(n_order, dtype=np.int64)
    for combo in itertools.combinations_with_replacement(list(map(int, logs)), 3):
        out[sum(combo) % n_order] += 1
    return out


def brute_force_typed_111(n_order: int, l1, l2, l3) -> np.ndarray:
    out = np.zeros(n_order, dtype=np.int64)
    for x in map(int, l1):
        for y in map(int, l2):
            for z in map(int, l3):
                out[(x + y + z) % n_order] += 1
    return out


def brute_force_typed_1_2(n_order: int, l_single, l_pair) -> np.ndarray:
    out = np.zeros(n_order, dtype=np.int64)
    lp = list(map(int, l_pair))
    for x in map(int, l_single):
        for y, z in itertools.combinations_with_replacement(lp, 2):
            out[(x + y + z) % n_order] += 1
    return out


# --------------------------------------------------------------------------
# Cell statistics over an evaluation domain (whole group, or a held-out mask).
# --------------------------------------------------------------------------

def cell_stats(counts: np.ndarray, mask: np.ndarray | None = None) -> dict:
    sub = counts if mask is None else counts[mask]
    n = int(sub.size)
    tot = int(sub.sum())
    return {
        "n_targets": n,
        "sum_counts": tot,
        "mean": tot / n,
        "coverage": float(np.count_nonzero(sub) / n),
        "concentration": float(np.sum(sub * (sub - 1)) / n),
        "variance": float(np.var(sub.astype(np.float64))),
        "max_count": int(sub.max()) if n else 0,
    }


STAT_KEYS = ("mean", "coverage", "concentration")


# --------------------------------------------------------------------------
# Factor-base geometries (frozen_definitions.geometries).
# --------------------------------------------------------------------------

class Infeasible(Exception):
    """Raised when a geometry cannot reach matched size B on a curve."""


def geom_high_bit_interval(curve: Curve, b: int) -> dict:
    """H018: point-x in the top window [p-W, p), W minimal for >= B points."""
    xs = curve.point_xs
    if xs.size < b:
        raise Infeasible(f"only {xs.size} point-x values available, need {b}")
    top = xs[-b:]                       # the B largest point-x == top window
    w = int(curve.p - top[0])
    logs = curve.log_of_x[top]
    return {"logs": np.sort(logs), "window_W": w, "x_min": int(top[0]),
            "x_max": int(top[-1]),
            "window_density": float(b / w)}


def geom_x_interval_low(curve: Curve, b: int) -> dict:
    """Smallest-x interval base (used as sub-base 1 of mixed_two_base)."""
    xs = curve.point_xs
    if xs.size < b:
        raise Infeasible(f"only {xs.size} point-x values available, need {b}")
    low = xs[:b]
    return {"logs": np.sort(curve.log_of_x[low]), "x_min": int(low[0]),
            "x_max": int(low[-1])}


def height_map_enumerated(p: int, h_max: int) -> dict[int, int]:
    """h(x) = min over x = u v^{-1} mod p of max(|u|,|v|), for all h(x) <= h_max.

    Enumerates every coprime (u, v) with |u| <= h_max, 1 <= v <= h_max.  Any x
    reachable with height <= h_max is found, with its exact height, because the
    minimising representation of such an x is itself inside the enumerated box.
    """
    best: dict[int, int] = {}
    for v in range(1, h_max + 1):
        vinv = pow(v, -1, p)
        for u in range(-h_max, h_max + 1):
            if math.gcd(abs(u), v) != 1:
                continue
            h = max(abs(u), v)
            x = (u * vinv) % p
            cur = best.get(x)
            if cur is None or h < cur:
                best[x] = h
    return best


def height_cf(x: int, p: int) -> int:
    """Same height, computed from the continued-fraction convergents of x/p."""
    # r_{-1}=p, r_0=x ; v_{-1}=0, v_0=1 ; |x v_i - k_i p| = r_i
    r_prev, r_cur = p, x % p
    v_prev, v_cur = 0, 1
    best = max(r_cur, v_cur) if r_cur or v_cur else p
    while r_cur:
        q = r_prev // r_cur
        r_prev, r_cur = r_cur, r_prev - q * r_cur
        v_prev, v_cur = v_cur, v_prev + q * v_cur
        if r_cur:
            best = min(best, max(r_cur, v_cur))
    return best


def geom_small_height(curve: Curve, b: int) -> dict:
    """H019: the B point-x values of smallest rational-reconstruction height."""
    for h_max in FROZEN["height_H_schedule"]:
        hmap = height_map_enumerated(curve.p, h_max)
        cand = [(h, x) for x, h in hmap.items() if curve.log_of_x[x] > 0]
        if len(cand) >= b:
            cand.sort()
            chosen = cand[:b]
            logs = np.array([curve.log_of_x[x] for _, x in chosen], dtype=np.int64)
            return {"logs": np.sort(logs), "h_max_used": h_max,
                    "height_of_selected": [int(h) for h, _ in chosen],
                    "max_selected_height": int(chosen[-1][0]),
                    "n_candidates_at_h_max": len(cand)}
    raise Infeasible("height schedule exhausted before reaching size B")


def geom_small_multiples(curve: Curve, b: int) -> dict:
    """H017 convention: x(jG), j = 1, 2, ... deduplicated by x, truncated to B.

    In log space the dedup is a no-op for j <= 2B < N/2, so the base is
    {1, ..., B}.  Verified against the table rather than assumed.
    """
    seen: dict[int, int] = {}
    j = 1
    while len(seen) < b and j <= 2 * b:
        x = int(curve.xs[j % curve.n_order])
        if x not in seen:
            seen[x] = j
        j += 1
    if len(seen) < b:
        raise Infeasible(f"only {len(seen)} distinct x among j <= 2B")
    logs = np.array(sorted(seen.values())[:b], dtype=np.int64)
    return {"logs": np.sort(logs), "pool_before_truncate": len(seen),
            "is_initial_segment": bool(np.array_equal(
                np.sort(logs), np.arange(1, b + 1, dtype=np.int64)))}


def geom_qr_walk(curve: Curve, b: int, seed: int, r_walk: int = 20,
                 c_bound: int = 1 << 10) -> dict:
    """H016 QR base, same-family reconstruction of the recorded convention.

    Recorded convention (inputs/h100_session/h016_base_yield.json): "first B
    distinct points of a deterministic r-adding walk (r=20, c_j in [1,2^10))
    off G with x a QR mod p".  The recorded file does NOT pin the walk's RNG
    stream, its index function, or its starting point, so this is a same-family
    reconstruction, not a bit-identical replay.  Reported only in the
    exploratory section, never as a pre-registered cell.
    """
    p, n = curve.p, curve.n_order
    isqr = qr_table(p)
    rng = np.random.default_rng(seed)
    mult = [int(v) for v in rng.integers(1, c_bound, size=r_walk)]
    logs: list[int] = []
    seen: set[int] = set()
    log_cur = 1                                    # start at G
    steps = 0
    max_steps = 200 * b + 1000
    while len(logs) < b and steps < max_steps:
        x = int(curve.xs[log_cur])
        if x not in seen and isqr[x]:
            seen.add(x)
            lg = int(curve.log_of_x[x])
            if lg > 0:
                logs.append(lg)
        log_cur = (log_cur + mult[x % r_walk]) % n
        if log_cur == 0:
            log_cur = 1
        steps += 1
    if len(logs) < b:
        raise Infeasible(f"QR walk stalled at {len(logs)} points")
    return {"logs": np.sort(np.array(logs, dtype=np.int64)), "steps": steps,
            "r_walk": r_walk, "c_bound": c_bound, "multipliers": mult,
            "walk_seed": seed}


def geom_mixed_two_base(curve: Curve, b: int) -> dict:
    """H020: x-interval sub-base (ceil(B/2)) + small-multiples sub-base (floor(B/2))."""
    b1 = (b + 1) // 2
    b2 = b // 2
    s1 = geom_x_interval_low(curve, b1)
    s2 = geom_small_multiples(curve, b2)
    l1, l2 = s1["logs"], s2["logs"]
    overlap = int(np.intersect1d(l1, l2).size)
    return {"sub_bases": [l1, l2], "sizes": [b1, b2], "overlap": overlap,
            "sub_base_1": {k: v for k, v in s1.items() if k != "logs"},
            "sub_base_2": {k: v for k, v in s2.items() if k != "logs"}}


def geom_coset_union(curve: Curve, b: int) -> dict:
    """H021: union of multiplicative cosets g^i H, |H| = largest divisor of p-1 <= B."""
    p = curve.p
    divs = [d for d in sympy.divisors(p - 1) if d <= b]
    d = max(divs)
    g = int(sympy.primitive_root(p))
    gen_h = pow(g, (p - 1) // d, p)
    subgroup = []
    cur = 1
    for _ in range(d):
        subgroup.append(cur)
        cur = cur * gen_h % p
    subgroup = np.array(sorted(set(subgroup)), dtype=np.int64)
    if subgroup.size != d:
        raise AssertionError("subgroup size mismatch (implementation_error)")
    logs: list[int] = []
    seen_x: set[int] = set()
    n_cosets = 0
    gi = 1
    max_cosets = (p - 1) // d
    while len(logs) < b and n_cosets < max_cosets:
        coset = np.sort((subgroup * gi) % p)
        n_cosets += 1
        for x in coset.tolist():
            if x in seen_x:
                continue
            lg = int(curve.log_of_x[x])
            if lg > 0:
                seen_x.add(x)
                logs.append(lg)
                if len(logs) == b:
                    break
        gi = gi * g % p
    if len(logs) < b:
        raise Infeasible(f"coset union exhausted at {len(logs)} points")
    return {"logs": np.sort(np.array(logs, dtype=np.int64)), "subgroup_order_d": d,
            "n_cosets_used": n_cosets, "primitive_root": g,
            "divisors_of_p_minus_1_le_B": divs}


# ---------------------- greedy (H022) --------------------------------------

def _cyc_shift(bits: int, s: int, n: int, mask: int) -> int:
    s %= n
    if s == 0:
        return bits
    return ((bits << s) | (bits >> (n - s))) & mask


def bits_from_indices(idx, n: int) -> int:
    out = 0
    for i in map(int, idx):
        out |= 1 << (i % n)
    return out


def greedy_select(n_order: int, pool: np.ndarray, train_bits: int, b: int) -> dict:
    """H022 exact submodular-style greedy on TRAINING targets only.

    The held-out mask is not an argument of this function, which is the
    structural enforcement of the frozen stopping rule "any use of held-out
    targets during selection invalidates this arm".
    """
    mask = (1 << n_order) - 1
    s_bits = 0        # indicator of the chosen set S
    s2_bits = 0       # indicator of Sigma_2(S)  (2-multiset sums)
    r_bits = 0        # indicator of Sigma_3(S)  (3-multiset sums)
    chosen: list[int] = []
    gains: list[int] = []
    remaining = [int(v) for v in pool]
    for _ in range(b):
        avail = train_bits & ~r_bits
        best_gain, best_d = -1, None
        for d in remaining:
            cand = (_cyc_shift(s2_bits, d, n_order, mask)
                    | _cyc_shift(s_bits, 2 * d, n_order, mask)
                    | (1 << (3 * d % n_order))) & avail
            g = cand.bit_count()
            if g > best_gain or (g == best_gain and (best_d is None or d < best_d)):
                best_gain, best_d = g, d
        d = best_d
        chosen.append(d)
        gains.append(best_gain)
        remaining.remove(d)
        s2_bits |= _cyc_shift(s_bits, d, n_order, mask) | (1 << (2 * d % n_order))
        s_bits |= 1 << d
        r_bits |= _cyc_shift(s2_bits, d, n_order, mask)
    return {"logs": np.sort(np.array(chosen, dtype=np.int64)),
            "selection_order": chosen, "marginal_gains": gains,
            "sigma3_size_at_stop": r_bits.bit_count(),
            "train_targets_covered_at_stop": (r_bits & train_bits).bit_count(),
            "pool_size": int(pool.size)}


def greedy_split(n_order: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Frozen deterministic split: seeded permutation, first half TRAINING."""
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n_order)
    half = n_order // 2
    train = np.zeros(n_order, dtype=bool)
    train[perm[:half]] = True
    return train, ~train


# ---------------------- asymmetric sizing (H004) ---------------------------

def asym_split_sizes(b: int, weights) -> tuple[int, int, int]:
    """Ladder split: floor of the weight share for B2, B3; remainder to B1."""
    w = list(weights)
    tot = float(sum(w))
    b2 = max(1, int(math.floor(w[1] / tot * b)))
    b3 = max(1, int(math.floor(w[2] / tot * b)))
    b1 = b - b2 - b3
    if not (b1 >= b2 >= b3 >= 1):
        raise AssertionError(f"ladder split violates B1>=B2>=B3>=1 for B={b}, w={w}")
    return b1, b2, b3


def distinct_logs(rng, n_order: int, k: int) -> np.ndarray:
    """k distinct uniform logs in [1, N) -- the frozen matched-random convention.

    Rejection top-up gives a uniform random k-subset and avoids materialising a
    length-N permutation for every one of the >= 100 null draws.
    """
    if k >= n_order - 1:
        raise Infeasible(f"cannot draw {k} distinct logs from {n_order - 1}")
    seen: set[int] = set()
    while len(seen) < k:
        need = k - len(seen)
        for v in rng.integers(1, n_order, size=need):
            if len(seen) < k:
                seen.add(int(v))
    return np.sort(np.fromiter(seen, dtype=np.int64, count=k))


def random_disjoint_sub_bases(n_order: int, sizes, rng) -> list[np.ndarray]:
    tot = int(sum(sizes))
    logs = distinct_logs(rng, n_order, tot)
    logs = logs[rng.permutation(tot)]
    out = []
    off = 0
    for s in sizes:
        out.append(np.sort(logs[off:off + s]))
        off += s
    return out


def random_base(n_order: int, b: int, rng) -> np.ndarray:
    return distinct_logs(rng, n_order, b)


# --------------------------------------------------------------------------
# Statistics: empirical p-values, Holm-Bonferroni, bootstrap, growth slope.
# --------------------------------------------------------------------------

def empirical_p(observed: float, null_vals: np.ndarray, two_sided: bool = True,
                direction: str = "greater") -> dict:
    null_vals = np.asarray(null_vals, dtype=np.float64)
    n = null_vals.size
    centre = float(null_vals.mean())
    if two_sided:
        r = int(np.count_nonzero(np.abs(null_vals - centre)
                                 >= abs(observed - centre) - 1e-15))
    elif direction == "greater":
        r = int(np.count_nonzero(null_vals >= observed - 1e-15))
    else:
        r = int(np.count_nonzero(null_vals <= observed + 1e-15))
    return {"p": (r + 1) / (n + 1), "p_raw_fraction": r / n if n else None,
            "n_null": n, "n_at_least_as_extreme": r,
            "null_mean": centre,
            "null_sd": float(null_vals.std(ddof=1)) if n > 1 else 0.0,
            "null_band_95": [float(np.percentile(null_vals, 2.5)),
                             float(np.percentile(null_vals, 97.5))],
            "null_min": float(null_vals.min()), "null_max": float(null_vals.max()),
            "two_sided": two_sided}


def empirical_p_h016(observed: float, null_vals: np.ndarray) -> float:
    """The recorded H016 two-sided convention: 2*min(tail)/n.

    Identified exactly (all four recorded cells) in the port-fidelity control:
    2 * min(#{null >= obs}, #{null <= obs}) / n.  Reported for family
    comparability with the prior cells.  It can return 0, so the valid
    (r+1)/(n+1) convention is used for the Holm family.
    """
    null_vals = np.asarray(null_vals, dtype=np.float64)
    n = null_vals.size
    hi = int(np.count_nonzero(null_vals >= observed - 1e-15))
    lo = int(np.count_nonzero(null_vals <= observed + 1e-15))
    return min(1.0, 2.0 * min(hi, lo) / n)


def holm(pvals: dict[str, float], alpha: float = 0.05) -> dict:
    """Holm-Bonferroni over a family; missing (None) p-values still occupy a slot."""
    m = len(pvals)
    items = [(k, v) for k, v in pvals.items() if v is not None]
    items.sort(key=lambda kv: kv[1])
    out: dict[str, dict] = {}
    running = 0.0
    for i, (k, v) in enumerate(items):
        adj = min(1.0, max(running, (m - i) * v))
        running = adj
        out[k] = {"p_raw": v, "p_holm": adj, "rank": i + 1,
                  "multiplier": m - i, "reject_at_alpha": bool(adj < alpha)}
    for k, v in pvals.items():
        if v is None:
            out[k] = {"p_raw": None, "p_holm": None, "rank": None,
                      "multiplier": None, "reject_at_alpha": False,
                      "note": "p-value unavailable; slot retained so the family "
                              "size stays 8 (conservative)"}
    return {"family_size": m, "alpha": alpha, "cells": out}


def bootstrap_ci(values, n_boot: int, seed: int, levels=(95.0, 99.375)) -> dict:
    vals = np.asarray(values, dtype=np.float64)
    if vals.size == 0:
        return {"n": 0}
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, vals.size, size=(n_boot, vals.size))
    means = vals[idx].mean(axis=1)
    out = {"n": int(vals.size), "point_estimate": float(vals.mean()),
           "sd_across_replicates": float(vals.std(ddof=1)) if vals.size > 1 else 0.0,
           "min": float(vals.min()), "max": float(vals.max()),
           "n_boot": n_boot, "degenerate_zero_width": bool(np.ptp(vals) == 0.0)}
    for lv in levels:
        lo = (100.0 - lv) / 2.0
        out[f"ci{lv:g}"] = [float(np.percentile(means, lo)),
                            float(np.percentile(means, 100.0 - lo))]
    return out


def cluster_bootstrap_ci(values_by_cluster: dict, n_boot: int, seed: int,
                         levels=(95.0, 99.375)) -> dict:
    """Resample whole curves (the true independent-instance axis)."""
    keys = sorted(values_by_cluster)
    per = [float(np.mean(values_by_cluster[k])) for k in keys]
    return bootstrap_ci(per, n_boot, seed, levels) | {"clusters": keys}


def ols_slope(xs, ys) -> float:
    xs = np.asarray(xs, dtype=np.float64)
    ys = np.asarray(ys, dtype=np.float64)
    xm, ym = xs.mean(), ys.mean()
    den = float(np.sum((xs - xm) ** 2))
    if den == 0.0:
        return float("nan")
    return float(np.sum((xs - xm) * (ys - ym)) / den)


def growth_slope(per_size: dict[int, list], n_boot: int, seed: int,
                 levels=(95.0, 99.375)) -> dict:
    """OLS slope of a ratio against log2(N), bootstrapped within each size."""
    sizes = sorted(per_size)
    xs, ys = [], []
    for s in sizes:
        for v in per_size[s]:
            xs.append(float(s))
            ys.append(float(v))
    if len(set(xs)) < 2:
        return {"slope": None, "note": "fewer than two sizes measured"}
    slope = ols_slope(xs, ys)
    rng = np.random.default_rng(seed)
    boots = np.empty(n_boot)
    arrs = {s: np.asarray(per_size[s], dtype=np.float64) for s in sizes}
    for t in range(n_boot):
        bx, by = [], []
        for s in sizes:
            a = arrs[s]
            pick = a[rng.integers(0, a.size, size=a.size)]
            bx.extend([float(s)] * a.size)
            by.extend(pick.tolist())
        boots[t] = ols_slope(bx, by)
    out = {"slope": slope, "sizes_log2N": sizes,
           "per_size_mean": {str(s): float(np.mean(arrs[s])) for s in sizes},
           "per_size_sd": {str(s): (float(np.std(arrs[s], ddof=1))
                                    if arrs[s].size > 1 else 0.0) for s in sizes},
           "n_boot": n_boot,
           "degenerate_zero_width": bool(np.ptp(boots) == 0.0)}
    for lv in levels:
        lo = (100.0 - lv) / 2.0
        out[f"ci{lv:g}"] = [float(np.percentile(boots, lo)),
                            float(np.percentile(boots, 100.0 - lo))]
    return out
