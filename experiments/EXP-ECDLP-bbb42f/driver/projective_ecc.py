"""
Projective short-Weierstrass EC arithmetic over the RING Z/nZ (n need not
be prime -- this module is used with n = p^2 for the SSSA anomalous-curve
p-adic lift in sssa.py, where the point p*P reduces to the point at
infinity mod p, which affine coordinates cannot represent without a
non-invertible denominator). Curve: Y^2*Z = X^3 + a*X*Z^2 + b*Z^3.

The addition and doubling formulas below use ONLY ring multiplication and
addition (no inversion), so they are well-defined over any commutative
ring, including Z/p^2Z where many elements are zero divisors. They were
NOT taken from memory: they were derived mechanically in
tests/derive_projective.py and tests/derive_projective_double2.py by
symbolically clearing denominators from this driver's own AFFINE formulas
(ecc.py), which are independently verified against brute-force point
counting and homomorphism checks. They are re-verified here against affine
arithmetic over small prime fields in tests/test_projective.py.
"""
from __future__ import annotations


def is_zero_proj(Pp, n: int) -> bool:
    X, Y, Z = Pp
    return Z % n == 0


def to_affine(Pp, n: int):
    X, Y, Z = Pp
    if Z % n == 0:
        return None
    Zinv = pow(Z % n, -1, n)
    return ((X * Zinv) % n, (Y * Zinv) % n)


def from_affine(P, n: int):
    if P is None:
        return (0, 1, 0)
    x, y = P
    return (x % n, y % n, 1)


def proj_double(Pp, a: int, n: int):
    X1, Y1, Z1 = Pp
    if Z1 % n == 0 or Y1 % n == 0:
        return (0, 1, 0)
    X3 = (2 * Y1 * Z1 * (9 * X1**4 + 6 * X1**2 * Z1**2 * a - 8 * X1 * Y1**2 * Z1 + Z1**4 * a**2)) % n
    Y3 = (-27 * X1**6 - 27 * X1**4 * Z1**2 * a + 36 * X1**3 * Y1**2 * Z1
          - 9 * X1**2 * Z1**4 * a**2 + 12 * X1 * Y1**2 * Z1**3 * a
          - 8 * Y1**4 * Z1**2 - Z1**6 * a**3) % n
    Z3 = (8 * Y1**3 * Z1**3) % n
    return (X3, Y3, Z3)


def proj_add(P1p, P2p, a: int, n: int):
    X1, Y1, Z1 = P1p
    X2, Y2, Z2 = P2p
    if Z1 % n == 0:
        return P2p
    if Z2 % n == 0:
        return P1p
    same_x = (X1 * Z2 - X2 * Z1) % n == 0
    same_y = (Y1 * Z2 - Y2 * Z1) % n == 0
    if same_x:
        if same_y:
            return proj_double(P1p, a, n)
        else:
            return (0, 1, 0)  # P1 == -P2

    # Literal transcription of the sympy-derived expressions (no manual
    # substitution / shorthand, to eliminate transcription sign errors):
    #   X3 = (X1*Z2 - X2*Z1) * (X1**3*Z2**3 - X1**2*X2*Z1*Z2**2 - X1*X2**2*Z1**2*Z2
    #         + X2**3*Z1**3 - Y1**2*Z1*Z2**3 + 2*Y1*Y2*Z1**2*Z2**2 - Y2**2*Z1**3*Z2)
    #   Y3 = -X1**3*Y1*Z2**4 + 2*X1**3*Y2*Z1*Z2**3 - 3*X1**2*X2*Y2*Z1**2*Z2**2
    #        + 3*X1*X2**2*Y1*Z1**2*Z2**2 - 2*X2**3*Y1*Z1**3*Z2 + X2**3*Y2*Z1**4
    #        + Y1**3*Z1*Z2**4 - 3*Y1**2*Y2*Z1**2*Z2**3 + 3*Y1*Y2**2*Z1**3*Z2**2 - Y2**3*Z1**4*Z2
    #   Z3 = -Z1*Z2*(X1*Z2 - X2*Z1)**3
    X3 = ((X1 * Z2 - X2 * Z1) * (X1**3 * Z2**3 - X1**2 * X2 * Z1 * Z2**2 - X1 * X2**2 * Z1**2 * Z2
          + X2**3 * Z1**3 - Y1**2 * Z1 * Z2**3 + 2 * Y1 * Y2 * Z1**2 * Z2**2
          - Y2**2 * Z1**3 * Z2)) % n
    Y3 = (-X1**3 * Y1 * Z2**4 + 2 * X1**3 * Y2 * Z1 * Z2**3 - 3 * X1**2 * X2 * Y2 * Z1**2 * Z2**2
          + 3 * X1 * X2**2 * Y1 * Z1**2 * Z2**2 - 2 * X2**3 * Y1 * Z1**3 * Z2 + X2**3 * Y2 * Z1**4
          + Y1**3 * Z1 * Z2**4 - 3 * Y1**2 * Y2 * Z1**2 * Z2**3 + 3 * Y1 * Y2**2 * Z1**3 * Z2**2
          - Y2**3 * Z1**4 * Z2) % n
    Z3 = (-Z1 * Z2 * (X1 * Z2 - X2 * Z1)**3) % n
    return (X3, Y3, Z3)


def proj_scalar_mult(k: int, Pp, a: int, n: int):
    R = (0, 1, 0)
    base = Pp
    while k > 0:
        if k & 1:
            R = proj_add(R, base, a, n)
        base = proj_double(base, a, n)
        k >>= 1
    return R
