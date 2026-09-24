"""Semaev's third summation polynomial and the root-finding decomposition needs.

For E: y^2 = x^3 + a x + b, S_3(x1, x2, x3) = 0 exactly when there are points
P_i with x(P_i) = x_i and P_1 +/- P_2 +/- P_3 = O (Semaev 2004).  It is
symmetric and of degree 2 in each variable:

    S_3 = (x1 - x2)^2 x3^2 - 2((x1 + x2)(x1 x2 + a) + 2b) x3
          + (x1 x2 - a)^2 - 4b(x1 + x2).
"""

from __future__ import annotations

from .curve import Curve, sqrt_mod


def s3(E: Curve, x1: int, x2: int, x3: int) -> int:
    A, B, C = s3_coefficients(E, x1, x2)
    return (A * x3 * x3 + B * x3 + C) % E.p


def s3_coefficients(E: Curve, x1: int, x2: int) -> tuple[int, int, int]:
    """Coefficients (A, B, C) of S_3(x1, x2, X) = A X^2 + B X + C."""
    p, a, b = E.p, E.a, E.b
    A = (x1 - x2) ** 2 % p
    B = -2 * ((x1 + x2) * (x1 * x2 + a) + 2 * b) % p
    C = ((x1 * x2 - a) ** 2 - 4 * b * (x1 + x2)) % p
    return A, B, C


def s3_roots(E: Curve, x1: int, x2: int) -> list[int]:
    """All X in F_p with S_3(x1, x2, X) = 0 (at most two unless degenerate)."""
    p = E.p
    A, B, C = s3_coefficients(E, x1, x2)
    if A == 0:
        if B == 0:
            return []  # identically zero only in degenerate cases we skip
        return [(-C) * pow(B, -1, p) % p]
    disc = (B * B - 4 * A * C) % p
    r = sqrt_mod(disc, p)
    if r is None:
        return []
    inv = pow(2 * A, -1, p)
    roots = {(-B + r) * inv % p, (-B - r) * inv % p}
    return sorted(roots)
