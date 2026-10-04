#!/usr/bin/env python3
"""Twin dim(V·V) meters for EXP-BINSTD-5b2fd0.

Path A: span of pairwise products of a basis of V.
Path B: span of pairwise products of all elements of V (enumerate subspace).
Both return the F_2-dimension of V·V. Agreement is required before Spearman.
"""
from __future__ import annotations

from itertools import combinations_with_replacement


def f2_rank(elems: list[int], n: int) -> int:
    """Rank of field elements as F_2-bitvectors of length n."""
    used: list[tuple[int, int]] = []
    for v in elems:
        x = int(v) & ((1 << n) - 1)
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
    return len(used)


def enumerate_subspace(basis: list[int]) -> list[int]:
    l = len(basis)
    out: list[int] = []
    for mask in range(1 << l):
        acc = 0
        m = mask
        j = 0
        while m:
            if m & 1:
                acc ^= basis[j]
            m >>= 1
            j += 1
        out.append(acc)
    return out


def dim_vv_path_a(basis: list[int], F) -> int:
    """Twin A: span of products of basis elements (with replacement, k=2)."""
    prods: list[int] = []
    for a, b in combinations_with_replacement(basis, 2):
        prods.append(F.mul(a, b))
    # Also include squares of basis (already covered) and 0·anything = 0.
    return f2_rank(prods, F.n)


def dim_vv_path_b(basis: list[int], F) -> int:
    """Twin B: span of products of all pairs from the full subspace V."""
    V = enumerate_subspace(basis)
    prods: list[int] = []
    for i, a in enumerate(V):
        for b in V[i:]:
            prods.append(F.mul(a, b))
    return f2_rank(prods, F.n)


def dim_vv_agree(basis: list[int], F) -> tuple[int, int, bool]:
    a = dim_vv_path_a(basis, F)
    b = dim_vv_path_b(basis, F)
    return a, b, a == b


def poly_basis(ell: int) -> list[int]:
    return [1 << j for j in range(ell)]


def geometric_basis(ell: int, F, seed_elem: int = 3) -> list[int]:
    """span{1, g, g^2, ..., g^{ell-1}} for a frozen seed element g."""
    g = seed_elem % F.q
    if g == 0:
        g = 3
    basis = [1]
    acc = 1
    for _ in range(1, ell):
        acc = F.mul(acc, g)
        basis.append(acc)
    # Ensure F2-independence; pad with random-ish powers of t if needed.
    while f2_rank(basis, F.n) < ell:
        cand = 1 << (len(basis) % F.n)
        if f2_rank(basis + [cand], F.n) > f2_rank(basis, F.n):
            basis.append(cand)
        else:
            cand = F.mul(cand, g) ^ (1 << (len(basis) % F.n))
            basis.append(cand)
        if len(basis) > ell + 4:
            break
    # Trim / rebuild to exact ell via greedy independent set from poly + geo
    out: list[int] = []
    for v in basis + poly_basis(ell) + [1 << j for j in range(F.n)]:
        if f2_rank(out + [v], F.n) > f2_rank(out, F.n):
            out.append(v)
        if len(out) == ell:
            break
    return out


def random_basis(ell: int, n: int, rng) -> list[int]:
    basis: list[int] = []
    used: list[tuple[int, int]] = []
    while len(basis) < ell:
        v = int(rng.integers(1, 1 << n))
        x = v
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
        basis.append(v)
    return basis
