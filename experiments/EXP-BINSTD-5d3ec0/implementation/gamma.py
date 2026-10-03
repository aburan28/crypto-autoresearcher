"""Gamma_w scalar sets and Stage-0 product-law arithmetic for EXP-BINSTD-5d3ec0."""
from __future__ import annotations

import math
from itertools import combinations
from typing import Iterable


def binom(n: int, w: int) -> int:
    return math.comb(n, w)


def gamma_upper_bound(n: int, w: int) -> int:
    """|Gamma_w| <= C(n,w) * 2^w (exact pattern count before scalar collisions)."""
    return binom(n, w) * (1 << w)


def log2_exact(x: float) -> float:
    if x <= 0:
        return float("-inf")
    return math.log2(x)


def product_law_row(n: int, w: int) -> dict:
    ub = gamma_upper_bound(n, w)
    attempts = (1 << n) / ub
    return {
        "n": n,
        "w": w,
        "C_n_w": binom(n, w),
        "pattern_count_upper": ub,
        "gamma_log2_upper": log2_exact(ub),
        "attempts_free_upper": attempts,
        "attempts_free_log2_upper": log2_exact(attempts),
        "formula": " |Gamma_w| <= C(n,w)*2^w ; attempts_free = 2^n / |Gamma_w| ",
        "measured_vs_modeled": "modeled_arithmetic",
    }


def product_law_table(n: int, ws: Iterable[int]) -> list:
    return [product_law_row(n, w) for w in ws]


def find_mu(ell: int, n: int) -> int:
    """Find mu with mu^2+mu+2 ≡ 0 (mod ell) and ord_ell(mu) = n."""

    def tonelli(a: int, p: int):
        if pow(a, (p - 1) // 2, p) != 1:
            return None
        Q = p - 1
        S = 0
        while Q % 2 == 0:
            Q //= 2
            S += 1
        z = 2
        while pow(z, (p - 1) // 2, p) != p - 1:
            z += 1
        M = S
        c = pow(z, Q, p)
        R = pow(a, (Q + 1) // 2, p)
        t = pow(a, Q, p)
        while t != 1:
            i = 1
            t2 = (t * t) % p
            while t2 != 1:
                t2 = (t2 * t2) % p
                i += 1
                if i == M:
                    return None
            b = pow(c, 1 << (M - i - 1), p)
            R = (R * b) % p
            c = (b * b) % p
            t = (t * c) % p
            M = i
        return R

    disc = (-7) % ell
    sq = tonelli(disc, ell)
    if sq is None:
        raise RuntimeError("no sqrt(-7)")
    inv2 = pow(2, -1, ell)
    cands = [((-1 + sq) * inv2) % ell, ((-1 - sq) * inv2) % ell]
    for mu in cands:
        if (mu * mu + mu + 2) % ell != 0:
            continue
        # order
        x = 1
        for o in range(1, n + 2):
            x = (x * mu) % ell
            if x == 1:
                if o == n:
                    return mu
                break
    raise RuntimeError("no mu of exact order n")


def enum_gamma(mu: int, ell: int, n: int, w: int) -> list[int]:
    """Exact distinct scalars in Gamma_w = {sum e_i mu^{j_i} mod ell}."""
    powers = [pow(mu, j, ell) for j in range(n)]
    seen = set()
    for js in combinations(range(n), w):
        # all sign patterns e_i in {+1,-1}
        for mask in range(1 << w):
            s = 0
            for i, j in enumerate(js):
                term = powers[j]
                if (mask >> i) & 1:
                    s = (s - term) % ell
                else:
                    s = (s + term) % ell
            if s != 0:
                seen.add(s)
    return sorted(seen)


def random_scalar_set(size: int, ell: int, rng) -> list[int]:
    """Ordinary / null-object control: random nonzero scalars mod ell, size matched."""
    out = set()
    while len(out) < size:
        z = rng.randrange(1, ell)
        out.add(z)
    return sorted(out)
