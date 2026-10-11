"""Toy Koblitz Bailey-style walk + three-arm Semaev m=2 yield helpers.

EXP-BINSTD-a3cfee / TASK-20261001-3d2adf.
Mechanism replica at n in {17,23}; no n=131 transfer claim.
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass

from curve import Curve
from gf2n import Field, TableField, is_irreducible, pmod, clmul

# Irreducible moduli (trinomials) for toy cells.
MODULI = {
    17: (1 << 17) | (1 << 3) | 1,  # t^17+t^3+1
    23: (1 << 23) | (1 << 5) | 1,  # t^23+t^5+1
}


def make_field(n: int) -> TableField:
    mod = MODULI[n]
    ok, _ = is_irreducible(mod)
    if not ok:
        raise RuntimeError(f"modulus for n={n} failed irreducibility")
    return TableField(n=n, mod=mod)


def make_koblitz(F: Field) -> Curve:
    """Ordinary binary Koblitz analog: Y^2 + XY = X^3 + 1 (A=0, B=1)."""
    return Curve(F, A=0, B=1)


def find_normal_element(F: Field) -> int:
    """Find β whose conjugates {β, β^2, ..., β^{2^{n-1}}} are F_2-linearly independent."""
    n = F.n
    for cand in range(1, F.q):
        rows = []
        x = cand
        ok = True
        for _ in range(n):
            rows.append(x)
            x = F.sqr(x)
        # Gaussian elim over F_2 on bit matrix rows
        mat = rows[:]
        rank = 0
        used = [False] * n
        for col in range(n):
            pivot = None
            for r in range(rank, n):
                if (mat[r] >> col) & 1:
                    pivot = r
                    break
            if pivot is None:
                ok = False
                break
            mat[rank], mat[pivot] = mat[pivot], mat[rank]
            for r in range(n):
                if r != rank and (mat[r] >> col) & 1:
                    mat[r] ^= mat[rank]
            rank += 1
        if ok and rank == n:
            return cand
    raise RuntimeError("no normal element found")


def to_normal_coords(F: Field, beta: int, x: int) -> int:
    """Return bit-mask of coefficients of x in the normal basis (β^{2^i})."""
    n = F.n
    # Solve sum c_i β^{2^i} = x over F_2 via Gaussian elimination on the basis matrix.
    basis = []
    b = beta
    for _ in range(n):
        basis.append(b)
        b = F.sqr(b)
    # columns = basis elements; solve basis * c = x
    mat = basis[:]
    aug = x
    # We treat each basis[i] as a column vector of bits; build n x n and RHS.
    # Use bit-sliced gauss on rows = bit positions.
    # Represent system as list of row masks for coefficients + rhs bit.
    rows = [0] * n  # low n bits = coeffs, bit n = rhs
    for bit in range(n):
        row = 0
        for j in range(n):
            if (basis[j] >> bit) & 1:
                row |= 1 << j
        if (x >> bit) & 1:
            row |= 1 << n
        rows[bit] = row
    for col in range(n):
        pivot = None
        for r in range(col, n):
            if (rows[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            # dependent; leave coeff 0 (should not happen for normal basis + any x)
            continue
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(n):
            if r != col and (rows[r] >> col) & 1:
                rows[r] ^= rows[col]
    coeffs = 0
    for col in range(n):
        if (rows[col] >> n) & 1:
            coeffs |= 1 << col
    return coeffs


def hw_normal(F: Field, beta: int, x: int) -> int:
    return to_normal_coords(F, beta, x).bit_count()


def frobenius_point(curve: Curve, P):
    """σ: (x,y) -> (x^2, y^2) on binary curves (Frobenius)."""
    if P is None:
        return None
    F = curve.F
    return (F.sqr(P[0]), F.sqr(P[1]))


def frobenius_power(curve: Curve, P, j: int):
    R = P
    for _ in range(j):
        R = frobenius_point(curve, R)
    return R


@dataclass
class WalkConfig:
    n: int
    cutoff_c: int
    beta: int
    max_steps: int = 1 << 20


def bailey_step(curve: Curve, beta: int, P):
    """P_{i+1} = σ^j(P_i) ⊕ P_i with j = ((HW(x)/2) mod 8) + 3."""
    if P is None or P[0] == 0:
        return None, 0, 0
    hw = hw_normal(curve.F, beta, P[0])
    j = ((hw // 2) % 8) + 3
    sp = frobenius_power(curve, P, j)
    return curve.add(sp, P), hw, j


def is_distinguished(curve: Curve, beta: int, P, cutoff_c: int) -> bool:
    if P is None or P[0] == 0:
        return False
    return hw_normal(curve.F, beta, P[0]) <= cutoff_c


def seed_start_point(curve: Curve, G, seed: int, n_coeffs: int = 64):
    """Start = Σ c_i σ^i(G) from seed bits (toy AES-free expansion via SHA256)."""
    F = curve.F
    # Expand seed to bitstring
    buf = hashlib.sha256(seed.to_bytes(8, "little")).digest()
    while len(buf) * 8 < n_coeffs:
        buf += hashlib.sha256(buf).digest()
    R = None
    Pi = G
    for i in range(n_coeffs):
        bit = (buf[i // 8] >> (i % 8)) & 1
        if bit:
            R = curve.add(R, Pi)
        Pi = frobenius_point(curve, Pi)
    return R


def walk_until_dp(curve: Curve, beta: int, start, cutoff_c: int, max_steps: int):
    """Return (dp_point, steps, ok). Aborts early on cycle (toy-group artifact)."""
    P = start
    seen = {}
    for steps in range(1, max_steps + 1):
        key = None if P is None else (P[0], P[1])
        if key is not None:
            if key in seen:
                return None, steps, False  # cycle without DP
            seen[key] = steps
        P, hw, j = bailey_step(curve, beta, P)
        if P is None:
            return None, steps, False
        if is_distinguished(curve, beta, P, cutoff_c):
            return P, steps, True
    return None, max_steps, False


def replay_walk(curve: Curve, beta: int, start, cutoff_c: int, expected_steps: int):
    P = start
    for steps in range(1, expected_steps + 1):
        P, _, _ = bailey_step(curve, beta, P)
        if P is None:
            return None, False
        if is_distinguished(curve, beta, P, cutoff_c):
            return P, steps == expected_steps
    return P, False


def random_curve_point(curve: Curve, rng: random.Random):
    F = curve.F
    for _ in range(10000):
        x = rng.randrange(1, F.q)
        P = curve.lift_x(x)
        if P is not None:
            if rng.randrange(2):
                P = curve.neg(P)
            return P
    raise RuntimeError("failed to sample curve point")


def find_generator(curve: Curve, rng: random.Random, order_hint: int | None = None):
    """Pick a random non-identity point as walk generator (toy; not proven primitive)."""
    for _ in range(100):
        P = random_curve_point(curve, rng)
        if P is not None and P[0] != 0:
            return P
    raise RuntimeError("no generator")


def build_dp_pool(curve: Curve, beta: int, G, cutoff_c: int, N: int, seed: int, max_steps: int):
    rng = random.Random(seed)
    pool = []  # list of dicts
    seen_x = set()
    collisions = 0
    attempts = 0
    while len(pool) < N and attempts < N * 50:
        attempts += 1
        s = rng.getrandbits(64)
        start = seed_start_point(curve, G, s)
        if start is None:
            continue
        dp, steps, ok = walk_until_dp(curve, beta, start, cutoff_c, max_steps)
        if not ok or dp is None:
            continue
        # replay check
        dp2, replay_ok = replay_walk(curve, beta, start, cutoff_c, steps)
        if not replay_ok or dp2 is None or dp2[0] != dp[0] or dp2[1] != dp[1]:
            continue
        if dp[0] in seen_x:
            collisions += 1
            continue
        seen_x.add(dp[0])
        pool.append(
            {
                "x": dp[0],
                "y": dp[1],
                "seed": s,
                "steps": steps,
                "start_x": start[0],
                "start_y": start[1],
            }
        )
    return pool, collisions, attempts


def build_uniform_pool(curve: Curve, N: int, seed: int):
    rng = random.Random(seed)
    pool = []
    seen = set()
    while len(pool) < N:
        P = random_curve_point(curve, rng)
        if P[0] in seen:
            continue
        seen.add(P[0])
        pool.append({"x": P[0], "y": P[1], "seed": None, "steps": None})
    return pool


def build_hw_filter_only_pool(curve: Curve, beta: int, cutoff_c: int, N: int, seed: int):
    rng = random.Random(seed)
    pool = []
    seen = set()
    attempts = 0
    while len(pool) < N and attempts < N * 200000:
        attempts += 1
        P = random_curve_point(curve, rng)
        if not is_distinguished(curve, beta, P, cutoff_c):
            continue
        if P[0] in seen:
            continue
        seen.add(P[0])
        pool.append({"x": P[0], "y": P[1], "seed": None, "steps": None})
    return pool, attempts


def pool_index(pool):
    """Map x -> (x,y) and also store negations for mitt."""
    idx = {}
    for e in pool:
        idx[e["x"]] = (e["x"], e["y"])
    return idx


def reverify_decomposition(curve: Curve, P, Q, R) -> bool:
    """Independent re-check on a fresh Curve object: P+Q == R."""
    F2 = Field(curve.F.n, curve.F.mod)  # schoolbook path
    c2 = Curve(F2, curve.A, curve.B)
    S = c2.add(P, Q)
    return S is not None and S[0] == R[0] and S[1] == R[1]


def semaev_m2_yield(curve: Curve, pool, n_attempts: int, seed: int, group_order: int):
    """Count m=2 decompositions R = P+Q with P,Q in pool (P.x <= Q.x), random R."""
    rng = random.Random(seed)
    idx = pool_index(pool)
    xs = list(idx.keys())
    N = len(xs)
    hits = []
    hit_flags = []
    cert_pass = 0
    cert_fail = 0
    for attempt in range(n_attempts):
        R = random_curve_point(curve, rng)
        found = None
        for x1 in xs:
            P = idx[x1]
            Q_target = curve.sub(R, P)
            if Q_target is None:
                continue
            if Q_target[0] in idx:
                Q_use = Q_target
                if reverify_decomposition(curve, P, Q_use, R):
                    found = {
                        "attempt": attempt,
                        "R": list(R),
                        "P": list(P),
                        "Q": list(Q_use),
                    }
                    cert_pass += 1
                    break
                else:
                    cert_fail += 1
        if found:
            hits.append(found)
            hit_flags.append(1)
        else:
            hit_flags.append(0)
    count = len(hits)
    # Modeled baseline: E[count] ≈ N^2 / (2 * |G|) * attempts  (unordered pairs heuristic)
    # Spec formula |F|^m/(m!*N_group) is per-target success expectation with m!=2 => /2.
    expected_per_target = (N * N) / (2.0 * group_order) if group_order else float("nan")
    expected_count = expected_per_target * n_attempts
    return {
        "relation_count": count,
        "n_attempts": n_attempts,
        "pool_size_N": N,
        "yield_rate": count / n_attempts if n_attempts else 0.0,
        "expected_count_modeled": expected_count,
        "expected_per_target_modeled": expected_per_target,
        "certificate_pass_count": cert_pass,
        "certificate_fail_count": cert_fail,
        "certificate_pass_rate": (
            cert_pass / (cert_pass + cert_fail) if (cert_pass + cert_fail) else 1.0
        ),
        "hits_sample": hits[:5],
        "hit_flags": hit_flags,
    }


def pairwise_permutation_pvalue(a_hits_flags, b_hits_flags, rng: random.Random, n_perm=2000):
    """Two-sample test on Bernoulli attempt outcomes via permutation of labels."""
    a = list(a_hits_flags)
    b = list(b_hits_flags)
    na, nb = len(a), len(b)
    obs = (sum(a) / na) - (sum(b) / nb)
    pooled = a + b
    extreme = 0
    for _ in range(n_perm):
        rng.shuffle(pooled)
        da = sum(pooled[:na]) / na
        db = sum(pooled[na:]) / nb
        if abs(da - db) >= abs(obs) - 1e-15:
            extreme += 1
    return extreme / n_perm, obs


def expand_hit_flags(yield_result):
    """Approximate per-attempt hit flags from count (contiguous prefix) — for p-value only.
    Better: recompute. Here we store exact via re-run in driver when needed.
    """
    n = yield_result["n_attempts"]
    c = yield_result["relation_count"]
    return [1] * c + [0] * (n - c)


def choose_cutoff(n: int) -> int:
    """Freeze cutoff approximately matching 1/sqrt(2^n) DP density.

    At toy n the pure Bailey walk enters short cycles; c is chosen so a
    non-trivial fraction of seeds still hit a DP before cycling, while
    remaining within an order of magnitude of the target density. Exact
    ECC2K-130 c=34 is NOT used. Disclosed confounder in Stage-0 freeze.
    """
    if n == 17:
        return 4  # binomial proxy dens≈0.0245 vs target≈0.00276 (~9× denser)
    if n == 23:
        return 5  # dens≈0.0053 vs target≈0.00035 (~15× denser)
    raise ValueError(n)


def choose_N(n: int) -> int:
    """Pool size so E[relations] with 250 attempts is >>1 at uniform arm."""
    if n == 17:
        return 96
    if n == 23:
        return 256
    raise ValueError(n)


def group_order_estimate(curve: Curve) -> int:
    """Exact #E via trace enumeration (toy n only)."""
    return curve.count_by_trace()


def binomial_hw_density(n: int, c: int) -> float:
    return sum(math.comb(n, k) for k in range(c + 1)) / (1 << n)
