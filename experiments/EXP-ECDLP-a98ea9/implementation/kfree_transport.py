"""k-free canonical prime-to-p lift.

This module is the Stage 1 transport code path. It MUST NOT read a
discrete-log scalar. The only point it sees is an F_p affine point of
known prime order n, together with the curve, n, and the precision.

Function surface (static-provenance gate reads this file by AST):
    hensel_lift_without_projection(curve, P_fp, precision)
    canonical_order_n_lift(curve, P_fp, n, precision)
    ordinary_base_p_digits(value, p, precision)
    affine_digits(curve, P_jac, precision)

None of those names takes a discrete-log scalar.
"""
from __future__ import annotations

from ec_jac import (
    Curve,
    affine_xy,
    curve_ok,
    hensel_lift_y,
    is_infinity,
    scalar_mult,
)


def hensel_lift_without_projection(curve: Curve, P_fp, precision: int):
    """NULL-2: Hensel-lift the Weierstrass equation and STOP.

    x is the F_p representative. No [p^{precision-1}] projection, no
    multiplication by the inverse of p^{precision-1} mod n.
    """
    if precision < 1:
        raise ValueError("precision must be >= 1")
    mod = curve.p**precision
    x0, y0 = P_fp
    y = hensel_lift_y(curve, x0 % mod, y0, mod)
    P = (x0 % mod, y, 1)
    if not curve_ok(curve, P, mod):
        raise RuntimeError("hensel lift is not on the curve")
    if (P[0] % curve.p) != (x0 % curve.p) or (P[1] % curve.p) != (y0 % curve.p):
        raise RuntimeError("hensel lift does not reduce to the F_p point")
    return P


def canonical_order_n_lift(curve: Curve, P_fp, n: int, precision: int):
    """Canonical prime-to-p order-n lift of P_fp.

    Construction (k-free):
      1. Hensel-lift P_fp to E(Z/p^r Z) and stop (same as NULL-2).
      2. U = [p^{r-1}] P_tilde.
      3. m = (p^{r-1})^{-1} mod n.  (exists because gcd(n, p) = 1)
      4. return [m] U.

    At r = 1 the projection is the identity: p^{0} = 1, m = 1, so the
    return value equals the Hensel lift, which equals the F_p point
    itself. That is the declared width-zero cell of NULL-2.
    """
    if n <= 1:
        raise ValueError("n must be an integer > 1")
    if curve.p % n == 0 or n % curve.p == 0:
        raise ValueError("gcd(n, p) = 1 is required; the order-n lift does not exist")
    P_tilde = hensel_lift_without_projection(curve, P_fp, precision)
    mod = curve.p**precision
    # p^{r-1} is 1 when r = 1 (vacuous projection).
    # Apply [p] exactly (r-1) times instead of double-and-add of p^{r-1}.
    # That keeps every intermediate reduction equal to [p^j] P_fp ≠ O
    # (because gcd(n,p)=1), so the running point never enters the kernel.
    U = P_tilde
    for _ in range(precision - 1):
        U = scalar_mult(curve.p, U, mod, curve)
        if is_infinity(U, mod):
            raise RuntimeError("[p] of the running lift is infinity; lift failed")
    power = curve.p ** (precision - 1)
    if is_infinity(U, mod):
        raise RuntimeError("[p^{r-1}] of the Hensel lift is infinity; lift failed")
    m = pow(power % n, -1, n)
    lifted = scalar_mult(m, U, mod, curve)
    if is_infinity(lifted, mod):
        raise RuntimeError("canonical lift is infinity")
    if not curve_ok(curve, lifted, mod):
        raise RuntimeError("canonical lift is not on the curve")
    ax, ay = affine_xy(curve, lifted, mod)
    if ax % curve.p != P_fp[0] % curve.p or ay % curve.p != P_fp[1] % curve.p:
        raise RuntimeError("canonical lift does not reduce to the F_p point")
    return (ax, ay, 1)


def ordinary_base_p_digits(value: int, p: int, precision: int):
    """Ordinary base-p digits of the unique representative in [0, p^r)."""
    mod = p**precision
    x = value % mod
    digits = []
    for _ in range(precision):
        digits.append(x % p)
        x //= p
    return digits


def affine_digits(curve: Curve, P_jac, precision: int):
    """Ordinary base-p digits of affine x of a Jacobian point mod p^r."""
    mod = curve.p**precision
    ax, _ay = affine_xy(curve, P_jac, mod)
    return ordinary_base_p_digits(ax, curve.p, precision)
