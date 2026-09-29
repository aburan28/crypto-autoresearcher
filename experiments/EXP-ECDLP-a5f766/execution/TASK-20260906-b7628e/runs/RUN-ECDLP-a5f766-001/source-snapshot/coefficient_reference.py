"""Implementation R: independent coefficient-formula reference.

Closed-form first-order formulas only; no dual-number pair arithmetic.
This module must not import direct_dual_numbers.
"""


def F0_formula(p, x0, A0):
    inv = pow(A0 % p, -1, p)
    return (x0 * x0 * inv) % p


def J_formula(p, x0, x1, A0, A1):
    inv = pow(A0 % p, -1, p)
    inv2 = (inv * inv) % p
    return (2 * x0 * x1 * inv - x0 * x0 * A1 * inv2) % p


def gauge_transform(p, u0, v, coeffs):
    x0, x1, y0, y1, A0, A1, B0, B1 = coeffs
    u2 = pow(u0, 2, p)
    u3 = pow(u0, 3, p)
    u4 = pow(u0, 4, p)
    u6 = pow(u0, 6, p)
    return (
        (u2 * x0) % p,
        (u2 * (x1 + 2 * v * x0)) % p,
        (u3 * y0) % p,
        (u3 * (y1 + 3 * v * y0)) % p,
        (u4 * A0) % p,
        (u4 * (A1 + 4 * v * A0)) % p,
        (u6 * B0) % p,
        (u6 * (B1 + 6 * v * B0)) % p,
    )


def pullback_transform(p, c, coeffs):
    x0, x1, y0, y1, A0, A1, B0, B1 = coeffs
    return (x0, (c * x1) % p, y0, (c * y1) % p,
            A0, (c * A1) % p, B0, (c * B1) % p)


def F_jet(p, coeffs):
    x0, x1, _y0, _y1, A0, A1, _B0, _B1 = coeffs
    return (F0_formula(p, x0, A0), J_formula(p, x0, x1, A0, A1))
