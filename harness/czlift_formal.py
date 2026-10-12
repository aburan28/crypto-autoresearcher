"""Formal-group logarithm and exponential for y^2 = x^3 + a x + b over Z/p^k.

New module for IDEA-20261009-00514a (EXP-CZLIFT-7c8d73); harness/czlift.py is
reused unmodified. Everything is a truncated power series in the formal
parameter z = -x/y with coefficients in Z/p^k, truncated at z^(k+1): a point
of the formal group has v_p(z) >= 1, so z^m vanishes mod p^k for m > k, and
for k < p every denominator that appears (m or m! with m <= k) is a p-adic
unit, so the series are exact mod p^k.

    w(z) = z^3 + a z w^2 + b w^3           (fixed-point iteration)
    x = z / w,  y = -1 / w
    omega = dx / (2 y)  =  (x'(z) / (2 y(z))) dz
    log_F(z) = integral of omega,  exp_F = compositional inverse.

Independent of the z-valuation reading of EXP-CZLIFT-17b7eb: that reads
v_p(z([p]P^)); this constructs the p-torsion lift explicitly as
P^ - exp_F(log_F(z([p]P^)) / p) whenever log_F(z([p]P^)) is divisible by p^2,
and verifies it by curve arithmetic.
"""
from __future__ import annotations

from harness.czlift import ZpCurve, Proj, val_p


class Series:
    """Truncated power series sum c_i z^i, i < N, coefficients mod M."""

    def __init__(self, coeffs, M: int, N: int):
        self.M, self.N = M, N
        c = [x % M for x in coeffs[:N]]
        self.c = c + [0] * (N - len(c))

    @classmethod
    def z(cls, M, N):
        return cls([0, 1], M, N)

    def __add__(self, o):
        return Series([(a + b) for a, b in zip(self.c, o.c)], self.M, self.N)

    def __sub__(self, o):
        return Series([(a - b) for a, b in zip(self.c, o.c)], self.M, self.N)

    def __mul__(self, o):
        if isinstance(o, int):
            return Series([a * o for a in self.c], self.M, self.N)
        out = [0] * self.N
        for i, a in enumerate(self.c):
            if a == 0:
                continue
            for j, b in enumerate(o.c[: self.N - i]):
                out[i + j] = (out[i + j] + a * b) % self.M
        return Series(out, self.M, self.N)

    def deriv(self):
        return Series([(i * self.c[i]) for i in range(1, self.N)], self.M, self.N)

    def integ(self):
        """Antiderivative with zero constant term; needs i+1 invertible mod M for i+1 < N."""
        out = [0]
        for i in range(self.N - 1):
            out.append(self.c[i] * pow(i + 1, -1, self.M) % self.M)
        return Series(out, self.M, self.N)

    def inverse_unit(self):
        """1 / self for self with unit constant term (Newton / long division)."""
        c0 = pow(self.c[0], -1, self.M)
        out = [c0] + [0] * (self.N - 1)
        for n in range(1, self.N):
            s = 0
            for i in range(1, n + 1):
                s += self.c[i] * out[n - i]
            out[n] = (-s * c0) % self.M
        return Series(out, self.M, self.N)

    def compose(self, inner):
        """self(inner(z)) for inner with zero constant term."""
        out = Series([0], self.M, self.N)
        power = Series([1], self.M, self.N)
        for a in self.c:
            if a:
                out = out + power * a
            power = power * inner
        return out

    def eval(self, z: int) -> int:
        acc = 0
        for a in reversed(self.c):
            acc = (acc * z + a) % self.M
        return acc


def formal_series(E: ZpCurve):
    """(w, log_F, exp_F) as Series over Z/p^k truncated at z^(k+1)... with margin."""
    p, k = E.p, E.k
    if k >= p:
        raise ValueError("series are exact only for precision k < p")
    M, N = E.M, k + 1
    z = Series.z(M, N)
    w = Series([0], M, N)
    for _ in range(N + 1):
        w = z * z * z + z * (w * w) * E.a + (w * w * w) * E.b
    winv = Series([w.c[3], *w.c[4:], 0, 0, 0], M, N)  # placeholder, replaced below
    # x = z / w = z^{-2} * (z^3 / w): write w = z^3 u with u a unit series
    u = Series(w.c[3:] + [0, 0, 0], M, N)
    uinv = u.inverse_unit()
    # x = z^{-2} uinv, y = -z^{-3} uinv; omega = dx/(2y) = (-2 z^{-3} uinv + z^{-2} uinv') / (-2 z^{-3} uinv) dz
    #       = (1 - z uinv'/(2 uinv)) dz = (1 + z u'/(2u)) dz  since uinv'/uinv = -u'/u
    du = u.deriv()
    inv2 = pow(2, -1, M)
    omega = Series([1], M, N) + (z * du * uinv) * inv2
    log_F = omega.integ()
    # exp_F: compositional inverse of log_F (log_F = z + ...), by Newton-free iteration
    exp_F = Series.z(M, N)
    for _ in range(N):
        exp_F = exp_F - (log_F.compose(exp_F) - z)
    return w, log_F, exp_F


def point_from_z(E: ZpCurve, w: Series, z: int) -> Proj:
    """Projective point with formal parameter z (needs v_p(z) >= 1): (x : y : 1) = (z/w : -1/w : 1) = (z : -1 : w)."""
    return (z % E.M, (-1) % E.M, w.eval(z))


def p_torsion_lift(E: ZpCurve, Phat: Proj):
    """Explicit p-torsion lift of red(Phat) on an anomalous curve, if it exists.

    Returns (valuation of log_F(z([p]P^)), lifted point or None, verified flag).
    """
    p, k = E.p, E.k
    w, log_F, exp_F = formal_series(E)
    T = E.mul(p, Phat)
    zT = E.z_param(T)
    lam = log_F.eval(zT)
    v = val_p(lam, p, k)
    if v < 2:
        return v, None, False
    if v >= k:
        # log is 0 mod p^k: T is O at this precision; P^ itself is p-torsion to precision k
        return v, Phat, E.is_zero(E.mul(p, Phat))
    mu = (lam // p) % E.M  # lam / p, valuation v - 1 >= 1
    zU = exp_F.eval(mu)
    U = point_from_z(E, w, zU)
    ok_curve = E.on_curve(U)
    ok_mult = E.eq(E.mul(p, U), T, prec=k - 1)
    Pt = E.sub(Phat, U)
    ok_tor = E.is_zero(E.mul(p, Pt), prec=k - 1)
    return v, Pt, bool(ok_curve and ok_mult and ok_tor)
