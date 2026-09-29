"""Jacobian elliptic-curve arithmetic over Z/p^r Z.

Division-free group law (PD-3): the only inversion is affine-x extraction,
which refuses a non-unit Z. Addition refuses a zero-divisor H that is not
exactly zero (the H==0 branch is the genuine equal-or-inverse case).
"""
from __future__ import annotations

from dataclasses import dataclass


class NonUnitDenominator(Exception):
    """A Jacobian formula would have inverted a zero-divisor (PD-3)."""


@dataclass(frozen=True)
class Curve:
    p: int
    A: int
    B: int

    def disc_mod_p(self) -> int:
        return (-16 * (4 * self.A**3 + 27 * self.B**2)) % self.p


def valuation(x: int, p: int, cap: int, mod: int) -> int:
    x %= mod
    if x == 0:
        return cap
    e = 0
    while x % p == 0 and e < cap:
        x //= p
        e += 1
    return e


def jac_infinity():
    return (0, 1, 0)


def is_infinity(P, mod: int) -> bool:
    return P[2] % mod == 0


def curve_ok(curve: Curve, P, mod: int) -> bool:
    X, Y, Z = P
    A, B = curve.A, curve.B
    return (Y * Y) % mod == (X**3 + A * X * Z**4 + B * Z**6) % mod


def _normalize_jac(curve: Curve, P, mod: int):
    """Cancel Jacobian-weighted p-content (X:wt 2, Y:wt 3, Z:wt 1)."""
    X, Y, Z = P
    if Z % mod == 0:
        return jac_infinity()
    cap = 64
    vx = valuation(X, curve.p, cap, mod)
    vy = valuation(Y, curve.p, cap, mod)
    vz = valuation(Z, curve.p, cap, mod)
    v = min(vz, vx // 2, vy // 3)
    if v == 0:
        return (X % mod, Y % mod, Z % mod)
    return (
        (X // curve.p ** (2 * v)) % mod,
        (Y // curve.p ** (3 * v)) % mod,
        (Z // curve.p**v) % mod,
    )


def jac_dbl(curve: Curve, P, mod: int):
    X1, Y1, Z1 = P
    if Z1 % mod == 0:
        return jac_infinity()
    Ssq = (4 * X1 * Y1 * Y1) % mod
    M = (3 * X1 * X1 + curve.A * pow(Z1, 4, mod)) % mod
    X3 = (M * M - 2 * Ssq) % mod
    Y3 = (M * (Ssq - X3) - 8 * pow(Y1, 4, mod)) % mod
    Z3 = (2 * Y1 * Z1) % mod
    return _normalize_jac(curve, (X3, Y3, Z3), mod)


def jac_add(curve: Curve, P, Q, mod: int):
    X1, Y1, Z1 = P
    X2, Y2, Z2 = Q
    if Z1 % mod == 0:
        return Q
    if Z2 % mod == 0:
        return P
    Z1Z1 = (Z1 * Z1) % mod
    Z2Z2 = (Z2 * Z2) % mod
    U1 = (X1 * Z2Z2) % mod
    U2 = (X2 * Z1Z1) % mod
    S1 = (Y1 * Z2 * Z2Z2) % mod
    S2 = (Y2 * Z1 * Z1Z1) % mod
    H = (U2 - U1) % mod
    R = (S2 - S1) % mod
    if H == 0:
        if R == 0:
            return jac_dbl(curve, P, mod)
        return jac_infinity()
    # H nonzero: use the generic polynomial formulas even when H is a
    # zero-divisor (PD-3). Affine addition would invert H and silently
    # fail; these formulas do not invert. Counted by the caller if needed.
    I = (4 * H * H) % mod
    J = (H * I) % mod
    rr = (2 * R) % mod
    V = (U1 * I) % mod
    X3 = (rr * rr - J - 2 * V) % mod
    Y3 = (rr * (V - X3) - 2 * S1 * J) % mod
    Z3 = (((Z1 + Z2) ** 2 - Z1Z1 - Z2Z2) * H) % mod
    return _normalize_jac(curve, (X3, Y3, Z3), mod)


def scalar_mult(k: int, P, mod: int, curve: Curve):
    """Double-and-add. k may be 0."""
    if k < 0:
        raise ValueError("scalar_mult requires k >= 0")
    Rp = jac_infinity()
    Q = P
    while k > 0:
        if k & 1:
            Rp = jac_add(curve, Rp, Q, mod)
        Q = jac_dbl(curve, Q, mod)
        k >>= 1
    return Rp


def affine_xy(curve: Curve, P, mod: int):
    """Jacobian to affine. Refuses a non-unit Z (PD-3)."""
    X, Y, Z = P
    if valuation(Z, curve.p, 64, mod) != 0:
        raise NonUnitDenominator(
            f"affine extraction: Z is not a unit (PD-3): Z={Z} mod {mod}"
        )
    zi = pow(Z, -1, mod)
    return ((X * zi * zi) % mod, (Y * zi * zi * zi) % mod)


def _cancel_div(num: int, den: int, p: int, mod: int) -> int:
    """num/den in Z/p^r when the quotient is a p-adic integer.

    Cancels shared p-powers on integer representatives, then inverts the
    unit part. Raises NonUnitDenominator if the quotient is not integral
    or the remaining denominator is 0.
    """
    num %= mod
    den %= mod
    if den == 0:
        raise NonUnitDenominator("denominator is 0")
    while den % p == 0:
        if num % p != 0:
            raise NonUnitDenominator("quotient is not a p-adic integer")
        den //= p
        num //= p
    return (num * pow(den, -1, mod)) % mod


def affine_add(curve: Curve, P, Q, mod: int):
    """Affine addition over Z/p^r with honest p-power cancellation (PD-3)."""
    if P is None:
        return Q
    if Q is None:
        return P
    (x1, y1), (x2, y2) = P, Q
    dx = (x2 - x1) % mod
    dy = (y2 - y1) % mod
    if dx == 0:
        if dy == 0:
            return affine_dbl(curve, P, mod)
        return None
    lam = _cancel_div(dy, dx, curve.p, mod)
    x3 = (lam * lam - x1 - x2) % mod
    y3 = (lam * (x1 - x3) - y1) % mod
    return (x3, y3)


def affine_dbl(curve: Curve, P, mod: int):
    if P is None:
        return None
    x1, y1 = P
    if y1 % curve.p == 0 and (2 * y1) % mod == 0:
        return None
    lam = _cancel_div((3 * x1 * x1 + curve.A) % mod, (2 * y1) % mod, curve.p, mod)
    x3 = (lam * lam - 2 * x1) % mod
    y3 = (lam * (x1 - x3) - y1) % mod
    return (x3, y3)


def affine_scalar(k: int, P, mod: int, curve: Curve):
    if k < 0:
        raise ValueError("affine_scalar requires k >= 0")
    R = None
    Q = P
    while k > 0:
        if k & 1:
            R = affine_add(curve, R, Q, mod)
        Q = affine_dbl(curve, Q, mod)
        k >>= 1
    return R


def hensel_lift_y(curve: Curve, x0: int, y0_modp: int, mod: int) -> int:
    """Newton-lift Y^2 = x0^3 + A x0 + B from y0 mod p. Requires y0 != 0 mod p."""
    p = curve.p
    if y0_modp % p == 0:
        raise NonUnitDenominator("hensel_lift_y: 2-torsion (2y not a unit)")
    c = (pow(x0, 3, mod) + curve.A * x0 + curve.B) % mod
    y = y0_modp % p
    prec = 1
    bound = mod.bit_length() + 8
    while True:
        newprec = min(2 * prec, prec + 64)
        m = min(p**newprec, mod)
        yy = y % m
        fval = (yy * yy - c) % m
        fpinv = pow(2 * yy, -1, m)
        y = (yy - fval * fpinv) % m
        prec = newprec
        if m >= mod:
            break
        if prec > bound:
            break
    return y % mod
