"""
Velu's isogeny formula in Kohel's kernel-polynomial form: given a monic
kernel polynomial h(x) = prod (x - x_i), i=1..d, d=(ell-1)/2, whose roots are
the x-coordinates of one representative per +/-pair of the ell-1 nonzero
kernel points of an ell-isogeny from E: y^2=x^3+ax+b, compute the codomain
curve E': y^2=x^3+A'x+B' directly from the power sums of h's roots -- no
extension field and no explicit point y-coordinates are ever needed, because
every kernel point used here has odd order ell (not 2-torsion), so Velu's
per-point quantities (t_Q, u_Q) depend only on x_Q:

    t_Q = 2*(3*x_Q^2 + a)
    u_Q = 4*(x_Q^3 + a*x_Q + b)      [ = 4*y_Q^2 ]

summed over the d representative roots:
    t = sum t_Q = 6*s2 + 2*a*d
    w = sum (u_Q + x_Q*t_Q) = 10*s3 + 6*a*s1 + 4*b*d

    A' = a - 5*t
    B' = b - 7*w

s1, s2, s3 are the first three power sums of h's roots, obtained from h's
coefficients via Newton's identities (poly.power_sums_from_monic).

Reference: Velu 1971; Kohel 1996 thesis (kernel-polynomial form).
"""
from __future__ import annotations

from poly import power_sums_from_monic, pdeg, _field_mul_tally


class VeluError(Exception):
    pass


def isogenous_curve_from_kernel(h_coeffs_asc, a: int, b: int, p: int, ell: int):
    """
    h_coeffs_asc: little-endian coefficient tuple of the monic kernel
    polynomial (as returned by poly.pgcd, which normalizes to monic).
    Returns (a_new, b_new).
    """
    d = (ell - 1) // 2
    deg = pdeg(h_coeffs_asc)
    if deg != d:
        raise VeluError(f"kernel polynomial has degree {deg}, expected {d}")
    # power_sums_from_monic expects descending-order coefficients
    coeffs_desc = list(reversed(h_coeffs_asc))
    if coeffs_desc[0] % p != 1:
        raise VeluError("kernel polynomial is not monic after gcd normalization")
    s1, s2, s3 = power_sums_from_monic(coeffs_desc, 3, p)

    t = (6 * s2 + 2 * a * d) % p
    w = (10 * s3 + 6 * a * s1 + 4 * b * d) % p
    _field_mul_tally[0] += 6  # 6*s2, 2*a*d, 10*s3, 6*a*s1, 4*b*d, plus one below

    a_new = (a - 5 * t) % p
    b_new = (b - 7 * w) % p
    _field_mul_tally[0] += 2  # 5*t, 7*w
    return a_new, b_new


def two_isogenous_curve(a: int, b: int, p: int, x0: int):
    """
    Explicit degree-2 Velu isogeny from a rational 2-torsion point (x0, 0).
    Included for completeness / the ell=2 branch of the walk, even though
    for our curves (N prime and odd) no rational 2-torsion ever exists and
    this branch is provably never taken (see class_walk.py); kept as a
    documented, testable primitive rather than silently omitted.
    """
    t_q = (3 * x0 * x0 + a) % p
    u_q = 0
    t = t_q
    w = (u_q + x0 * t_q) % p
    a_new = (a - 5 * t) % p
    b_new = (b - 7 * w) % p
    return a_new, b_new
