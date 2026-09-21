"""Z/N integer-arithmetic arms for EXP-RELN-f202be: base-size conventions,
forced-value-table derivations, the Z/N interval / random / Bose-Chowla /
q-decay-ladder base constructions, and their direct enumeration.

Uses source/direct_enumerator.py's generic multiset engine (Z/N as the
group: add = (a+b) % N, key = identity). This is part of the "direct"
implementation family; it shares no code with source/spectral_crosscheck.py.
"""
from __future__ import annotations

import hashlib
import math
from math import comb

import sympy

import direct_enumerator as de


# ---------------------------------------------------------------------------
# Base-size conventions (recomputed from the ACTUAL N; binding per spec).
# ---------------------------------------------------------------------------

def compute_B1(N: int) -> dict:
    raw = math.ceil((6 * N) ** (1.0 / 3.0))
    # guard against float rounding at the boundary
    while raw ** 3 < 6 * N:
        raw += 1
    while (raw - 1) ** 3 >= 6 * N:
        raw -= 1
    even = raw if raw % 2 == 0 else raw + 1
    return {"B1_unrounded": raw, "B1_even": even}


def compute_B2(N: int) -> dict:
    """Largest prime power q with 3(q^3 - 1) < N."""
    best = None
    q = 2
    while 3 * (q ** 3 - 1) < N:
        if sympy.isprime(q) or _is_prime_power(q):
            best = q
        q += 1
    if best is None:
        return {"B2": None, "inequality_holds": False}
    return {"B2": best, "inequality_holds": True, "check_3(q3-1)<N": 3 * (best ** 3 - 1) < N}


def _is_prime_power(n: int) -> bool:
    f = sympy.factorint(n)
    return len(f) == 1


def M_of(B: int) -> int:
    return comb(B + 2, 3)


def mu_of(M: int, N: int) -> float:
    return M / N


# ---------------------------------------------------------------------------
# Base constructions
# ---------------------------------------------------------------------------

def zn_interval_base(B: int) -> list[int]:
    """[1, B] as integers mod N (N not needed here; caller reduces mod N,
    but for B < N these are already in range)."""
    return list(range(1, B + 1))


def seed_draw_int(master_seed: int, rung_k: int, curve_seed: int, arm: str,
                   b_conv: str, draw_i: int, salt: str = "") -> int:
    """SHA256('{master}:{k}:{seed}:{arm}:{conv}:{i}{salt}') as a 64-bit int,
    per replication.null_draw_derivation."""
    tag = f"{master_seed}:{rung_k}:{curve_seed}:{arm}:{b_conv}:{draw_i}{salt}"
    h = hashlib.sha256(tag.encode()).hexdigest()
    return int(h[:16], 16)  # 64-bit


class SeededPCG:
    """A simple seeded, reproducible integer stream (PCG64-like via numpy's
    Generator seeded from a 64-bit integer -- deterministic, documented in
    environment.json as the sampler)."""

    def __init__(self, seed64: int):
        import numpy as np
        self.rng = np.random.Generator(np.random.PCG64(seed64))

    def randint(self, lo: int, hi_exclusive: int) -> int:
        return int(self.rng.integers(lo, hi_exclusive))

    def uniform01(self) -> float:
        return float(self.rng.random())


def zn_random_subset(N: int, B: int, seed64: int) -> list[int]:
    """Uniform random B-subset of nonzero residues mod N, distinct."""
    pcg = SeededPCG(seed64)
    chosen: set[int] = set()
    while len(chosen) < B:
        x = pcg.randint(1, N)
        chosen.add(x)
    return sorted(chosen)


def q_decay_base(N: int, B: int, q_frac: float, seed64: int) -> list[int]:
    """[1,B] with round(q*B) elements replaced by uniformly random nonzero
    residues distinct from the rest."""
    base = list(range(1, B + 1))
    n_replace = round(q_frac * B)
    if n_replace == 0:
        return base
    pcg = SeededPCG(seed64)
    kept_idx = set(range(B))
    remove_idx = set()
    # deterministic choice of which positions to replace, seeded
    positions = list(range(B))
    # simple seeded shuffle-select: draw n_replace distinct positions
    while len(remove_idx) < n_replace:
        remove_idx.add(pcg.randint(0, B))
    kept = [base[i] for i in range(B) if i not in remove_idx]
    replacements = set()
    existing = set(kept)
    while len(replacements) < n_replace:
        x = pcg.randint(1, N)
        if x not in existing and x not in replacements:
            replacements.add(x)
    return sorted(kept + list(replacements))


# ---------------------------------------------------------------------------
# Bose-Chowla B_3 set construction (q prime only; prime-power q not
# implemented -- see implementation.md for the documented scope limit).
# ---------------------------------------------------------------------------

def bose_chowla_set(q: int, bsgs_seed: int = 12345):
    """Bose-Chowla B_3 set of size q in Z/(q^3-1), for q PRIME.
    Returns (indices_sorted, order=q^3-1). Verified exhaustively by the
    caller (B_3 property: all C(q+2,3) 3-sums distinct) before use."""
    from sympy.polys.galoistools import gf_irreducible, gf_mul, gf_rem, gf_pow_mod
    from sympy.polys.domains import ZZ

    if not sympy.isprime(q):
        raise NotImplementedError(
            f"bose_chowla_set only implemented for prime q; q={q} is a "
            "non-prime prime power (documented scope limit, see implementation.md)"
        )
    p = q
    mod = gf_irreducible(3, p, ZZ)
    order = q ** 3 - 1
    factors = sympy.factorint(order)

    def mul(a, b):
        return gf_rem(gf_mul(a, b, p, ZZ), mod, p, ZZ)

    def powmod(a, n):
        return gf_pow_mod(a, n, mod, p, ZZ)

    def is_generator(g):
        if g in ([], [0]):
            return False
        for r in factors:
            if powmod(g, order // r) == [1]:
                return False
        return True

    g = None
    for a2 in range(p):
        for a1 in range(p):
            for a0 in range(p):
                if a2 == 0 and a1 == 0 and a0 == 0:
                    continue
                cand = [a2, a1, a0] if a2 != 0 else ([a1, a0] if a1 != 0 else [a0])
                if is_generator(cand):
                    g = cand
                    break
            if g:
                break
        if g:
            break
    if g is None:
        raise RuntimeError(f"no generator found for GF({q}^3)*")

    m = math.isqrt(order) + 1
    table: dict = {}
    cur = [1]
    for i in range(m):
        table.setdefault(tuple(cur), i)
        cur = mul(cur, g)
    ginv_m = powmod(g, order - m)

    inds = []
    for a in range(q):
        elt = [1, a % p]
        gamma = elt
        found = None
        for j in range(m):
            key = tuple(gamma)
            if key in table:
                found = j * m + table[key]
                break
            gamma = mul(gamma, ginv_m)
        if found is None:
            raise RuntimeError("BSGS discrete log failed to find index")
        inds.append(found % order)
    return inds, order


def verify_B3_property(inds: list[int], order: int) -> dict:
    import itertools
    from collections import Counter

    q = len(inds)
    cnt: Counter = Counter()
    dup = 0
    for i, j, k in itertools.combinations_with_replacement(range(q), 3):
        s = (inds[i] + inds[j] + inds[k]) % order
        cnt[s] += 1
        if cnt[s] > 1:
            dup += 1
    total = comb(q + 2, 3)
    return {"q": q, "order": order, "total_sums": total, "duplicate_sum_events": dup,
            "is_B3": dup == 0, "M_2": total}


# ---------------------------------------------------------------------------
# Enumeration wrapper (Z/N group)
# ---------------------------------------------------------------------------

def enumerate_zn(base: list[int], N: int, negation_closed: bool = False) -> dict:
    """Direct-enumerate a Z/N base. If negation_closed, `base` must already
    be W = V union -V and neg_index is computed here."""
    add_fn = lambda a, b: (a + b) % N
    key_fn = lambda a: int(a)
    neg_index = None
    if negation_closed:
        pos = {v: i for i, v in enumerate(base)}
        neg_index = []
        for v in base:
            nv = (-v) % N
            neg_index.append(pos.get(nv, -1))
    result = de.enumerate_triples([v % N for v in base], add_fn, key_fn, neg_index)
    return result


# ---------------------------------------------------------------------------
# Forced value table (stage 0)
# ---------------------------------------------------------------------------

def poisson_tail_prob(mu: float, k: int) -> float:
    """P[Poisson(mu) >= k] = 1 - CDF(k-1)."""
    # sum_{i=0}^{k-1} e^{-mu} mu^i / i!
    s = 0.0
    term = math.exp(-mu)
    s += term
    for i in range(1, k):
        term *= mu / i
        s += term
    return max(0.0, 1.0 - s)


def forced_value_table_for_curve(N: int) -> dict:
    b1 = compute_B1(N)
    b2 = compute_B2(N)
    B1_even = b1["B1_even"]
    B1_unrounded = b1["B1_unrounded"]
    M = M_of(B1_even)
    M_red = M - (B1_even ** 2) // 2
    mu = mu_of(M, N)
    M_unrounded = M_of(B1_unrounded)
    mu_unrounded = mu_of(M_unrounded, N)

    row = {
        "N": N,
        "B1_unrounded": B1_unrounded,
        "B1_even": B1_even,
        "M": M,
        "M_red": M_red,
        "mu": mu,
        "M_unrounded_plain": M_unrounded,
        "mu_unrounded_plain": mu_unrounded,
        "B2": b2["B2"],
        "B2_inequality_holds": b2["inequality_holds"],
    }
    if b2["B2"] is not None:
        M2 = M_of(b2["B2"])
        row["M2"] = M2
        row["mu2"] = mu_of(M2, N)
        row["bose_chowla_forced_delta"] = 1.0 - row["mu2"]

    row["forced_negation_gap"] = (B1_even ** 3) / (4.0 * M)
    row["zn_interval_threshold_0.05B2"] = 0.05 * (B1_unrounded ** 2)

    # design SD figure (HEUR-001), not asserted, reported alongside measured
    row["design_sd_delta_random"] = math.sqrt(mu + 6 * mu ** 2 + 4 * mu ** 3) / (mu * math.sqrt(N))
    row["random_base_mean_1_minus_1_over_N"] = 1.0 - 1.0 / N

    # predicate analytic-null SD depends on sigma and M/M_red, computed later
    # per predicate cell in analysis.py.

    # N * P[Poisson(mu) >= k] for k=1..8
    row["poisson_tail_counts"] = {str(k): N * poisson_tail_prob(mu, k) for k in range(1, 9)}

    return row
