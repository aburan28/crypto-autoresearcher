"""Candidate lambda enumeration for EXP-QSP-70b731.

Rule from the approved contract: EVERY non-linearized lambda in F_2[X] of
exact degree 3..7 — 244 candidates per n'. Affine (linearized-plus-constant)
shapes ARE included and marked. The 4 linearized degree-4 shapes are excluded
from the census (handled by the linearized control).

Bit-packed: bit i = coefficient of X^i; leading bit at degree d is always 1.
"""
from __future__ import annotations

from typing import Dict, Iterator, List, Tuple


def is_linearized(poly: int) -> bool:
    """True iff poly is F_2-linearized: only powers X^{2^i}, no constant term."""
    if poly & 1:
        return False  # nonzero constant
    i = 0
    p = poly
    while p:
        if p & 1:
            # degree i must be a power of 2
            if i == 0 or (i & (i - 1)) != 0:
                return False
        p >>= 1
        i += 1
    return True


def is_affine_linearized(poly: int) -> bool:
    """Linearized plus optional constant (affine)."""
    return is_linearized(poly ^ (poly & 1))


def degree(poly: int) -> int:
    return -1 if poly == 0 else poly.bit_length() - 1


def linearized_degree4() -> List[int]:
    """The four exact-degree-4 linearized shapes: X^4, X^4+X, X^4+X^2, X^4+X^2+X."""
    out = []
    for c1 in (0, 1):
        for c0 in (0, 1):
            # X^4 + c1 X^2 + c0 X
            out.append((1 << 4) | (c1 << 2) | (c0 << 1))
    return out


def iter_monic_exact_degree(d: int) -> Iterator[int]:
    """All monic polys of exact degree d over F_2 (2^d of them)."""
    leading = 1 << d
    for lower in range(1 << d):
        yield leading | lower


def census_candidates(d_min: int = 3, d_max: int = 7) -> List[Dict]:
    """244 non-linearized exact-degree d_min..d_max candidates (default 3..7)."""
    exclude = set(linearized_degree4())
    rows = []
    for d in range(d_min, d_max + 1):
        for poly in iter_monic_exact_degree(d):
            if poly in exclude:
                continue
            if is_linearized(poly):
                # other linearized degrees (2,8,...) — degree 2,8 not in 3..7 exact
                # degree 8 would be d=8; within 3..7 only deg 4 linearized exist among powers of 2
                continue
            rows.append({
                "lambda": poly,
                "lambda_hex": format(poly, "x"),
                "degree": d,
                "affine_linearized": is_affine_linearized(poly),
                "square": is_square_poly(poly),
            })
    return rows


def toy_candidates(d_min: int = 2, d_max: int = 7) -> List[Dict]:
    """Stage-1 toy set: all F_2[X] exact degree 2..7 (252), including linearized."""
    rows = []
    for d in range(d_min, d_max + 1):
        for poly in iter_monic_exact_degree(d):
            rows.append({
                "lambda": poly,
                "lambda_hex": format(poly, "x"),
                "degree": d,
                "linearized": is_linearized(poly),
                "affine_linearized": is_affine_linearized(poly),
                "square": is_square_poly(poly),
            })
    return rows


def is_square_poly(poly: int) -> bool:
    """True if poly = mu^2 for some mu in F_2[X] (only even exponents)."""
    i = 0
    p = poly
    while p:
        if (p & 1) and (i & 1):
            return False
        p >>= 1
        i += 1
    return poly != 0


def qr_decomposition(n: int, n_prime: int) -> Tuple[int, int]:
    """n = q n' + r with 0 <= r < n'."""
    if n_prime <= 0:
        raise ValueError("n' must be positive")
    q, r = divmod(n, n_prime)
    return q, r


def bound_A(n: int, n_prime: int, d: int) -> int:
    """Derivation (A) bound: max(2^{n'-r}, d^{q+1}) when H != 0."""
    q, r = qr_decomposition(n, n_prime)
    term1 = 1 << (n_prime - r)
    term2 = d ** (q + 1)
    return max(term1, term2)
