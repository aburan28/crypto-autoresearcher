"""Red-team library for EXP-CZLIFT-ae0a13 (TASK-20261023-1d45b5).

Written independently of harness/czlift.py, which this task does not read
(it is outside the task card's read_scope). Pure Python, exact integer
arithmetic only.

  * E(F_p): affine short-Weierstrass arithmetic and point counting.
  * E^(Z/p^K): projective arithmetic with the complete addition law of
    Bosma-Lenstra / Renes-Costello-Batina (2016, eq. (1)), valid for every
    input pair on a curve with no F_p-rational 2-torsion. Computing the
    polynomial formula over Z/p^K is exact: the output is the reduction mod
    p^K of the Z_p-point, because its reduction mod p is never (0:0:0).
  * z = -X/Y, the formal-group parameter at O; v_p of it.
  * Sections: naive (x = integer rep), Teichmuller (x = omega(x0)), Hensel
    random, torsion (two formulas).
"""
from __future__ import annotations

import random

O_AFF = None


# ----------------------------------------------------------------- F_p
def legendre(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    return 1 if pow(a, (p - 1) // 2, p) == 1 else -1


def sqrt_mod(a: int, p: int) -> int | None:
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    for y in range(p):  # toy p only
        if y * y % p == a:
            return y
    return None


def count_points(p: int, A: int, B: int) -> int:
    return p + 1 + sum(legendre(x * x * x + A * x + B, p) for x in range(p))


def aff_add(P, Q, p, A):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def aff_neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def aff_mul(k, P, p, A):
    R = None
    if k < 0:
        k, P = -k, aff_neg(P, p)
    while k:
        if k & 1:
            R = aff_add(R, P, p, A)
        P = aff_add(P, P, p, A)
        k >>= 1
    return R


def random_point(p, A, B, rng):
    while True:
        x = rng.randrange(p)
        y = sqrt_mod(x * x * x + A * x + B, p)
        if y is not None:
            if rng.randrange(2):
                y = (-y) % p
            return (x, y)


def point_of_order(p, A, B, N, n, rng):
    h = N // n
    while True:
        P = aff_mul(h, random_point(p, A, B, rng), p, A)
        if P is not None:
            assert aff_mul(n, P, p, A) is None
            return P


# ------------------------------------------------------------ Z/p^K
class ZpCurve:
    """y^2 = x^3 + A x + B over Z/p^K, projective points (X, Y, Z)."""

    def __init__(self, p: int, K: int, A: int, B: int):
        self.p, self.K, self.M = p, K, p ** K
        self.A, self.B = A % self.M, B % self.M
        self.b3 = 3 * self.B % self.M
        self.O = (0, 1, 0)

    def on_curve(self, P) -> bool:
        X, Y, Z = P
        M = self.M
        return (Y * Y * Z - (X ** 3 + self.A * X * Z * Z + self.B * Z ** 3)) % M == 0

    def add(self, P, Q):
        """Complete addition (Renes-Costello-Batina eq. (1), general a)."""
        M, a, b3 = self.M, self.A, self.b3
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        XX, YY, ZZ = X1 * X2, Y1 * Y2, Z1 * Z2
        XYp = X1 * Y2 + X2 * Y1
        XZp = X1 * Z2 + X2 * Z1
        YZp = Y1 * Z2 + Y2 * Z1
        u = YY - a * XZp - b3 * ZZ
        w = YY + a * XZp + b3 * ZZ
        s = a * XX + b3 * XZp - a * a * ZZ
        t = 3 * XX + a * ZZ
        X3 = (XYp * u - YZp * s) % M
        Y3 = (w * u + t * s) % M
        Z3 = (YZp * w + XYp * t) % M
        return (X3, Y3, Z3)

    def neg(self, P):
        return (P[0], (-P[1]) % self.M, P[2])

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P):
        if k < 0:
            k, P = -k, self.neg(P)
        R = self.O
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def eq(self, P, Q, prec: int | None = None) -> bool:
        m = self.M if prec is None else self.p ** prec
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        return ((X1 * Y2 - X2 * Y1) % m == 0 and (X1 * Z2 - X2 * Z1) % m == 0
                and (Y1 * Z2 - Y2 * Z1) % m == 0)

    def reduce(self, P):
        p = self.p
        X, Y, Z = P
        if Z % p == 0:
            return None
        zi = pow(Z, -1, p)
        return (X * zi % p, Y * zi % p)

    def z_param(self, P) -> int:
        X, Y, _ = P
        assert Y % self.p != 0, "z-parameter needs a point in the residue disc of O"
        return (-X * pow(Y, -1, self.M)) % self.M

    def val(self, z: int) -> int:
        if z % self.M == 0:
            return self.K
        v = 0
        while z % self.p == 0:
            z //= self.p
            v += 1
        return v

    def lead(self, z: int):
        """(valuation, leading unit digit mod p) of a formal-group parameter."""
        v = self.val(z)
        if v >= self.K:
            return (self.K, 0)
        return (v, (z // self.p ** v) % self.p)

    # --------------------------------------------------- lifting
    def hensel_y(self, xh: int, y0: int) -> int:
        M, p = self.M, self.p
        f = (xh ** 3 + self.A * xh + self.B) % M
        y = y0 % p
        assert (y * y - f) % p == 0 and y % p != 0
        for _ in range(self.K + 1):
            y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
        assert (y * y - f) % M == 0
        return y

    def lift_x(self, R, xh: int):
        return (xh % self.M, self.hensel_y(xh, R[1]), 1)

    def naive(self, R):
        return self.lift_x(R, R[0])

    def teich_x(self, x0: int) -> int:
        if x0 % self.p == 0:
            return 0
        return pow(x0, self.p ** (self.K - 1), self.M)

    def teichmuller(self, R):
        return self.lift_x(R, self.teich_x(R[0]))

    def hensel_random(self, R, rng):
        x = R[0] + self.p * rng.randrange(self.p ** (self.K - 1))
        return self.lift_x(R, x)

    def torsion_F1(self, Rh, n: int):
        """Rh - [n^{-1} mod p^K]([n]Rh): the record's formula."""
        return self.sub(Rh, self.mul(pow(n, -1, self.M), self.mul(n, Rh)))

    def torsion_F2(self, Rh, n: int):
        """[e]Rh with e = 1 mod n, e = 0 mod p^(K-1): an independent projection."""
        q = self.p ** (self.K - 1)
        e = q * pow(q, -1, n) % (n * q)
        return self.mul(e, Rh)

    # --------------------------------------------------- Smart ratio
    def smart_ratio(self, sP, sQ, n: int):
        """Leading digit of z([n]sQ)/z([n]sP); conventions as run.py tau_ratio."""
        vP, uP = self.lead(self.z_param(self.mul(n, sP)))
        vQ, uQ = self.lead(self.z_param(self.mul(n, sQ)))
        if vP >= self.K or vQ < vP:
            return None, vP, vQ
        if vQ > vP:
            return 0, vP, vQ
        return uQ * pow(uP, -1, self.p) % self.p, vP, vQ


def self_test(seed: int = 1) -> dict:
    """Complete-addition law vs affine F_p arithmetic; on-curve mod p^K."""
    rng = random.Random(seed)
    out = {"aff_vs_proj": 0, "on_curve": 0, "torsion_F1_eq_F2": 0, "n_tor_is_O": 0}
    for p, A, B in ((67, 0, 2), (101, 47, 91), (157, -9504, 365904)):
        N = count_points(p, A % p, B % p)
        E = ZpCurve(p, 4, A, B)
        pts = [random_point(p, A % p, B % p, rng) for _ in range(12)] + [None]
        for P in pts:
            for Q in pts + [aff_neg(P, p) if P else None, P]:
                Ph = E.O if P is None else E.naive(P)
                Qh = E.O if Q is None else E.naive(Q)
                Sh = E.add(Ph, Qh)
                assert E.on_curve(Sh)
                assert E.reduce(Sh) == aff_add(P, Q, p, A % p), (p, P, Q)
                out["aff_vs_proj"] += 1
                out["on_curve"] += 1
        # torsion section on a prime-order piece
        n = max(q for q in range(2, N + 1) if N % q == 0 and all(q % r for r in range(2, q)))
        if n != p:
            P = point_of_order(p, A % p, B % p, N, n, rng)
            for _ in range(5):
                Rh = E.hensel_random(P, rng)
                t1, t2 = E.torsion_F1(Rh, n), E.torsion_F2(Rh, n)
                assert E.eq(t1, t2)
                out["torsion_F1_eq_F2"] += 1
                assert E.val(E.z_param(E.mul(n, t1))) >= E.K
                out["n_tor_is_O"] += 1
    return out


if __name__ == "__main__":
    print(self_test())
