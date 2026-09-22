#!/usr/bin/env python3
"""Frobenius-stable and random F_2-subspaces of GF(2^n) for EXP-FROB-30006a.

The Frobenius sigma: x -> x^2 is F_2-linear on GF(2^n) with minimal polynomial
T^n - 1 (normal basis theorem), so GF(2^n) is a cyclic F_2[T]-module and for
every irreducible factor f of (T^n - 1)/(T - 1) the subspace

    V_f = ker f(sigma)

is sigma-stable of dimension deg f.  Over F_2 the factors of Phi_n(T) are the
cyclotomic-coset polynomials g_C(T) = prod_{i in C} (T - zeta^i), zeta a primitive
n-th root of unity in GF(2^k), k = ord_n(2), C a cyclotomic coset of 2 modulo n.
Everything here is computed from those definitions, in the polynomial basis of
`gf2n.GF2n`, and re-verified (f | T^n - 1, dim V_f = deg f, sigma(V_f) <= V_f).

Dimension table cross-check (IDEA-20260918-9abf42, dimension table only):
  n = 41: ord 20, f = 3 factors incl. (T-1), stable dims {0,1,20,21,40,41}
  n = 43: ord 14, f = 4 factors incl. (T-1), stable dims {0,1,14,15,28,29,42,43}
"""
from __future__ import annotations

import random
from typing import List, Tuple

from gf2n import GF2n, is_irreducible, lowest_weight_irreducible, poly_divmod, poly_mul


def ord_mod(a: int, n: int) -> int:
    k, x = 1, a % n
    while x != 1:
        x = (x * a) % n
        k += 1
    return k


def cyclotomic_cosets(n: int) -> List[List[int]]:
    """Cosets of <2> acting on Z/n \\ {0}, each sorted, in order of least element."""
    seen = set()
    cosets = []
    for j in range(1, n):
        if j in seen:
            continue
        c = []
        x = j
        while x not in c:
            c.append(x)
            x = (2 * x) % n
        seen.update(c)
        cosets.append(sorted(c))
    return cosets


def coset_polynomials(n: int) -> List[Tuple[List[int], int]]:
    """[(coset, g_C)] with g_C in F_2[T] as an int (bit i = coeff of T^i)."""
    k = ord_mod(2, n)
    K = GF2n(k, lowest_weight_irreducible(k))
    # primitive n-th root of unity: an element of order exactly n
    q = (1 << k) - 1
    assert q % n == 0
    zeta = None
    for g in range(2, 1 << k):
        z = K.pow(g, q // n)
        if z != 1 and all(K.pow(z, n // p) != 1 for p in _prime_factors(n)):
            zeta = z
            break
    assert zeta is not None
    out = []
    for C in cyclotomic_cosets(n):
        # poly with coefficients in K: list low-degree-first
        poly = [1]
        for i in C:
            root = K.pow(zeta, i)
            new = [0] * (len(poly) + 1)
            for d, cf in enumerate(poly):
                new[d + 1] ^= cf                 # T * cf
                new[d] ^= K.mul(cf, root)        # (-root) * cf, char 2
            poly = new
        assert all(cf in (0, 1) for cf in poly), "coset polynomial has a coefficient outside F_2"
        g = sum(cf << d for d, cf in enumerate(poly))
        assert is_irreducible(g) and len(C) == g.bit_length() - 1
        out.append((C, g))
    # product of all cosets' polynomials times (T - 1) equals T^n - 1
    prod = 0b11
    for _, g in out:
        prod = poly_mul(prod, g)
    assert prod == (1 << n) | 1, "factorisation does not multiply back to T^n - 1"
    return out


def _prime_factors(n: int) -> List[int]:
    fs, m, p = [], n, 2
    while p * p <= m:
        if m % p == 0:
            fs.append(p)
            while m % p == 0:
                m //= p
        p += 1
    if m > 1:
        fs.append(m)
    return fs


# ----------------------------------------------------------------------------- F_2 linear algebra (rows are ints)

def rref(rows: List[int]) -> List[int]:
    """Reduced row echelon basis of the span (pivot = highest set bit)."""
    basis: List[int] = []
    for r in rows:
        for b in basis:
            if r ^ b < r:
                r ^= b
        if r:
            basis.append(r)
            basis.sort(reverse=True)
    # full reduction
    for i in range(len(basis)):
        for j in range(len(basis)):
            if i != j and (basis[j] >> (basis[i].bit_length() - 1)) & 1:
                basis[j] ^= basis[i]
    basis.sort(reverse=True)
    return basis


def in_span(basis_rref: List[int], v: int) -> bool:
    for b in basis_rref:
        if v ^ b < v:
            v ^= b
    return v == 0


def kernel(rows: List[int], n: int) -> List[int]:
    """Kernel of the linear map a -> XOR_{i in a} rows[i] (a in F_2^n), as RREF basis."""
    # Solve M^T ... simpler: gaussian elimination on augmented [rows[i] | e_i]
    aug = [(rows[i], 1 << i) for i in range(n)]
    pivots = []
    for bit in reversed(range(n)):
        piv = None
        for idx, (r, tag) in enumerate(aug):
            if (r >> bit) & 1 and idx not in pivots:
                piv = idx
                break
        if piv is None:
            continue
        pivots.append(piv)
        pr, pt = aug[piv]
        for idx, (r, tag) in enumerate(aug):
            if idx != piv and (r >> bit) & 1:
                aug[idx] = (r ^ pr, tag ^ pt)
    ker = [tag for idx, (r, tag) in enumerate(aug) if r == 0]
    return rref(ker)


def poly_of_matrix(F: GF2n, g: int) -> List[int]:
    """Rows of g(sigma) acting on F = GF(2^n): row i = g(sigma)(t^i)."""
    S = F.squaring_matrix()
    rows = []
    for i in range(F.n):
        v = 1 << i
        acc = 0
        cur = v
        d = 0
        gg = g
        while gg:
            if gg & 1:
                acc ^= cur
            cur = F.apply_linear(S, cur)
            gg >>= 1
            d += 1
        rows.append(acc)
    return rows


def is_frobenius_stable(F: GF2n, basis: List[int]) -> bool:
    B = rref(basis)
    return all(in_span(B, F.sqr(v)) for v in B)


def stable_subspace(F: GF2n, g: int) -> List[int]:
    """RREF basis of ker g(sigma), g an irreducible factor of T^n - 1."""
    rows = poly_of_matrix(F, g)
    V = kernel(rows, F.n)
    assert len(V) == g.bit_length() - 1, f"dim ker g(sigma) = {len(V)} != deg g"
    assert is_frobenius_stable(F, V)
    return V


def random_subspace(F: GF2n, dim: int, rng: random.Random, max_tries: int = 1000) -> Tuple[List[int], int]:
    """Uniformly random dim-dimensional subspace (random full-rank generating set, RREF
    basis), rejected and resampled if it is Frobenius-stable.  Returns (basis, tries)."""
    for tries in range(1, max_tries + 1):
        rows = [rng.getrandbits(F.n) for _ in range(dim)]
        B = rref(rows)
        if len(B) != dim:
            continue
        if is_frobenius_stable(F, B):
            continue
        return B, tries
    raise RuntimeError("could not sample a non-stable subspace")


def coordinates(basis_rref: List[int], v: int) -> List[int]:
    """Coordinates of v in the RREF basis (pivot bits), or raise if v not in span."""
    coords = []
    for b in basis_rref:
        bit = (v >> (b.bit_length() - 1)) & 1
        coords.append(bit)
        if bit:
            v ^= b
    if v:
        raise ValueError("vector not in span")
    return coords


def selftest() -> dict:
    out = {}
    for n in (7, 17, 23, 31, 41, 43):
        F = GF2n(n, lowest_weight_irreducible(n))
        cps = coset_polynomials(n)
        dims = sorted({len(C) for C, _ in cps})
        out[n] = {"ord": ord_mod(2, n), "n_factors_excluding_T_minus_1": len(cps), "factor_degrees": [len(C) for C, _ in cps]}
        for C, g in cps:
            V = stable_subspace(F, g)
            assert len(V) == len(C)
        # random subspace of matched dimension is not stable
        rng = random.Random(7)
        V, tries = random_subspace(F, dims[0], rng)
        assert not is_frobenius_stable(F, V)
        out[n]["random_tries"] = tries
    return out


if __name__ == "__main__":
    import json
    print(json.dumps(selftest(), indent=1))
