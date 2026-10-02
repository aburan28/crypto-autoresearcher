"""Product-space dimensions and subspace helpers for EXP-BINSTD-ef7fa4."""
from __future__ import annotations

from itertools import combinations_with_replacement

import numpy as np


def predicted_dim(l: int, k: int, n: int) -> int:
    return min(k * (l - 1) + 1, n)


def poly_basis(l: int) -> list[int]:
    """V = span{1, t, ..., t^{l-1}} as field-element list (powers of t)."""
    return [1 << j for j in range(l)]


def f2_span_dim(elems: list[int], n: int) -> int:
    """Rank of a list of F_{2^n} elements as F_2-vectors (bit columns)."""
    used: list[tuple[int, int]] = []
    for v in elems:
        x = int(v)
        for p, piv in used:
            if x & (1 << p):
                x ^= piv
        if x == 0:
            continue
        p = (x & -x).bit_length() - 1
        used.append((p, x))
    return len(used)


def product_space_elements(basis: list[int], k: int, F) -> list[int]:
    """All products of k (not necessarily distinct) basis elements, reduced in F."""
    out = set()
    for tup in combinations_with_replacement(basis, k):
        acc = 1
        for b in tup:
            acc = F.mul(acc, b)
        out.add(acc)
    # also include all F2-linear combinations? For dim of product space V^{(k)},
    # V^{(k)} = span{ products of k elements of V }.
    # Since V is an F2-vector space, products of general elements are F2-linear
    # combinations of products of basis elements. So span of basis-products
    # equals V^{(k)}.
    return sorted(out)


def explicit_product_dim(basis: list[int], k: int, F) -> int:
    elems = product_space_elements(basis, k, F)
    return f2_span_dim(elems, F.n)


def enumerate_subspace(basis: list[int], F) -> list[int]:
    """All F2-linear combinations of basis (as field elements)."""
    l = len(basis)
    out = []
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


def random_basis(l: int, n: int, rng: np.random.Generator) -> list[int]:
    """Size-l F2-linearly independent random subspace basis of F_{2^n}."""
    basis: list[int] = []
    used: list[tuple[int, int]] = []
    while len(basis) < l:
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


def coords_to_field(bits: int, basis: list[int]) -> int:
    acc = 0
    j = 0
    m = bits
    while m:
        if m & 1:
            acc ^= basis[j]
        m >>= 1
        j += 1
    return acc


def field_in_span(x: int, basis: list[int]) -> bool:
    """Whether x lies in span(basis) over F2."""
    used = []
    for b in basis:
        v = b
        for p, piv in used:
            if v & (1 << p):
                v ^= piv
        if v == 0:
            continue
        p = (v & -x if False else (v & -v).bit_length() - 1)
        p = (v & -v).bit_length() - 1
        used.append((p, v))
    # reduce x
    for p, piv in used:
        if x & (1 << p):
            x ^= piv
    return x == 0


def membership_mask(universe_bits: int, basis: list[int]) -> set[int]:
    return set(enumerate_subspace(basis, None))  # F unused
