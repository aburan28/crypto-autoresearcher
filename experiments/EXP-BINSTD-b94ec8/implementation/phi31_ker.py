#!/usr/bin/env python3
"""Explicit Phi_31-ker Frobenius-stable bases for EXP-BINSTD-b94ec8.

Constructs V5 = ker(g(σ)) for one irreducible quintic factor g of Phi_31
over F_2, and V6 = F_2 + V5, as required by H-BINSTD-dfc684 / DEC-20261003-031dba
refine (EV-BINSTD-671f89). Distinct from polynomial-window bases of the same
dimension. Self-contained; does not import Magma/Sage/AUXIN.
"""
from __future__ import annotations

from typing import Any

from gf2 import Field, field_for, is_irreducible, pmod


def _phi_n_poly(n: int) -> int:
    """Phi_n(x) = (x^n - 1)/(x - 1) over F_2 = 1 + x + ... + x^{n-1}."""
    if n <= 1 or n % 2 == 0:
        raise ValueError(f"Phi_n poly expects odd n>1, got {n}")
    return (1 << n) - 1  # bits 0..n-1 set


def irreducible_quintic_factors_of_phi31() -> list[int]:
    """The six monic irreducible degree-5 factors of Phi_31 over F_2."""
    phi = _phi_n_poly(31)
    factors: list[int] = []
    for lower in range(1 << 5):
        g = lower | (1 << 5)  # monic quintic
        if not is_irreducible(g):
            continue
        if pmod(phi, g) == 0:
            factors.append(g)
    if len(factors) != 6:
        raise RuntimeError(
            f"expected 6 irreducible quintic factors of Phi_31, got {len(factors)}"
        )
    return factors


def _poly_coeffs(g: int) -> list[int]:
    d = g.bit_length() - 1
    return [(g >> i) & 1 for i in range(d + 1)]


def apply_linearized(coeffs: list[int], x: int, field: Field) -> int:
    """sum_i a_i * x^{2^i} with a_i in F_2."""
    acc = 0
    cur = x
    for a in coeffs:
        if a:
            acc ^= cur
        cur = field.square(cur)
    return acc


def ker_of_linearized(coeffs: list[int], field: Field) -> list[int]:
    """F_2-basis of {x in F_{2^n} : g(σ)(x) = 0}."""
    n = field.n
    images = [apply_linearized(coeffs, 1 << j, field) for j in range(n)]
    rows = [0] * n
    for c in range(n):
        v = images[c]
        for r in range(n):
            if (v >> r) & 1:
                rows[r] |= 1 << c
    A = list(rows)
    rnk = 0
    pivot_for_col = [-1] * n
    for col in range(n):
        piv = None
        for i in range(rnk, n):
            if (A[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        A[rnk], A[piv] = A[piv], A[rnk]
        for i in range(n):
            if i != rnk and ((A[i] >> col) & 1):
                A[i] ^= A[rnk]
        pivot_for_col[col] = rnk
        rnk += 1
    basis: list[int] = []
    for free in range(n):
        if pivot_for_col[free] != -1:
            continue
        vec = 1 << free
        for col in range(n):
            prow = pivot_for_col[col]
            if prow != -1 and ((A[prow] >> free) & 1):
                vec ^= 1 << col
        basis.append(vec)
    return basis


def f2_rank(rows: list[int], width: int) -> int:
    mats = list(rows)
    rank = 0
    for col in range(width):
        pivot = None
        for i in range(rank, len(mats)):
            if (mats[i] >> col) & 1:
                pivot = i
                break
        if pivot is None:
            continue
        mats[rank], mats[pivot] = mats[pivot], mats[rank]
        for i in range(len(mats)):
            if i != rank and ((mats[i] >> col) & 1):
                mats[i] ^= mats[rank]
        rank += 1
    return rank


def in_span(v: int, basis: list[int], width: int) -> bool:
    A = [b for b in basis if b]
    r = 0
    pivot_col: dict[int, int] = {}
    for col in range(width):
        piv = None
        for i in range(r, len(A)):
            if (A[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(len(A)):
            if i != r and ((A[i] >> col) & 1):
                A[i] ^= A[r]
        pivot_col[col] = r
        r += 1
    x = v
    for col, prow in pivot_col.items():
        if (x >> col) & 1:
            x ^= A[prow]
    return x == 0


def subspace_frobenius_stable(basis: list[int], field: Field) -> bool:
    if not basis:
        return True
    for b in basis:
        if b and not in_span(field.square(b), basis, field.n):
            return False
    return True


def spans_equal(a: list[int], b: list[int], width: int) -> bool:
    if f2_rank(a, width) != f2_rank(b, width):
        return False
    return f2_rank(a + b, width) == f2_rank(a, width)


def window_basis(l: int) -> list[int]:
    return [1 << i for i in range(l)]


def build_phi31_ker_bases(seed_factor_index: int = 0) -> dict[str, Any]:
    """Build explicit V5/V6 Phi_31-ker bases on F_{2^31}.

    seed_factor_index selects which of the six quintics is g (deterministic).
    """
    n = 31
    F = field_for(n)
    factors = irreducible_quintic_factors_of_phi31()
    idx = seed_factor_index % len(factors)
    g = factors[idx]
    coeffs = _poly_coeffs(g)
    v5 = ker_of_linearized(coeffs, F)
    if len(v5) != 5:
        raise RuntimeError(f"ker(g(σ)) dim {len(v5)} != 5 for g={g:#x}")
    if not subspace_frobenius_stable(v5, F):
        raise RuntimeError("V5 not Frobenius-stable")
    one_in_v5 = in_span(1, v5, n)
    v6 = list(v5) if one_in_v5 else list(v5) + [1]
    if f2_rank(v6, n) != 6:
        raise RuntimeError(f"V6 = F_2+V5 has rank {f2_rank(v6, n)} != 6")
    if not subspace_frobenius_stable(v6, F):
        raise RuntimeError("V6 not Frobenius-stable")
    w5 = window_basis(5)
    w6 = window_basis(6)
    distinct_v5 = not spans_equal(v5, w5, n)
    distinct_v6 = not spans_equal(v6, w6, n)
    if not distinct_v5 or not distinct_v6:
        raise RuntimeError("Phi_31-ker bases coincide with window_deg controls")
    return {
        "n": n,
        "modulus": hex(F.mod),
        "phi_31_factor_count": len(factors),
        "phi_31_factors_hex": [hex(f) for f in factors],
        "selected_factor_index": idx,
        "selected_factor_hex": hex(g),
        "selected_factor_coeffs": coeffs,
        "kind": "phi31_ker",
        "bases": {
            "stable_V5": {
                "kind": "phi31_ker",
                "l": 5,
                "basis_hex": [hex(b) for b in v5],
                "basis": v5,
                "frobenius_stable": True,
                "distinct_from_window_deg": True,
                "construction": "ker(g(σ)) for irreducible quintic g | Phi_31",
            },
            "stable_V6": {
                "kind": "phi31_ker",
                "l": 6,
                "basis_hex": [hex(b) for b in v6],
                "basis": v6,
                "frobenius_stable": True,
                "distinct_from_window_deg": True,
                "one_in_v5": one_in_v5,
                "construction": "F_2 + V5",
            },
            "window_deg_5": {
                "kind": "window_deg",
                "l": 5,
                "basis_hex": [hex(b) for b in w5],
                "basis": w5,
            },
            "window_deg_6": {
                "kind": "window_deg",
                "l": 6,
                "basis_hex": [hex(b) for b in w6],
                "basis": w6,
            },
        },
        "window_proxy": False,
        "amazon_bedrock": "NOT_USED",
    }


__all__ = [
    "build_phi31_ker_bases",
    "irreducible_quintic_factors_of_phi31",
    "subspace_frobenius_stable",
    "spans_equal",
]
