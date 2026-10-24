"""Validator-owned p-adic elliptic-curve arithmetic for the blind re-derivation.

TASK-20261022-93fb1c, phase 1 (sealed). Written from general mathematics only,
without reading harness/czlift*.py, the implementation/ folder, raw results or
decisions.

Curve: Y^2 Z = X^3 + a X Z^2 + b Z^3 over Z/p^K (good reduction, p >= 5).
Group law: the Bosma-Lenstra / Renes-Costello-Batina complete projective
addition for a1 = a2 = a3 = 0.  Over F_p it is exception-free when E(F_p) has
no 2-torsion (odd order); over Z/p^K the output's reduction is the F_p output,
which is a nonzero projective point, so a unit coordinate exists and the
representative is valid.  The formula is verified against affine chord-tangent
arithmetic in self_test() rather than trusted from memory.

Formal group: z = -X/Y, w = -Z/Y.  For short Weierstrass,
log(z) = z + (2a/5) z^5 + (3b/7) z^7 + ..., so for v_p(z) >= 1 and p > 7,
log(z) == z mod p^5, and z is additive on E^1/E^5.
"""

from __future__ import annotations

import random

O = (0, 1, 0)


def vp(x: int, p: int, cap: int) -> int:
    """p-adic valuation of a residue mod p^cap; returns cap when x == 0 mod p^cap."""
    x %= p ** cap
    if x == 0:
        return cap
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


class Curve:
    def __init__(self, p: int, a: int, b: int, K: int):
        self.p, self.K = p, K
        self.M = p ** K
        self.a = a % self.M
        self.b = b % self.M
        self.b3 = (3 * b) % self.M
        self.ops = 0  # complete-addition count (additions and doublings alike)

    # --- group law -----------------------------------------------------
    def add(self, P, Q):
        self.ops += 1
        M, a, b3 = self.M, self.a, self.b3
        X1, Y1, Z1 = P
        X2, Y2, Z2 = Q
        xx = X1 * X2 % M
        yy = Y1 * Y2 % M
        zz = Z1 * Z2 % M
        xy = (X1 * Y2 + X2 * Y1) % M
        yz = (Y1 * Z2 + Y2 * Z1) % M
        xz = (X1 * Z2 + X2 * Z1) % M
        A = (yy - a * xz - b3 * zz) % M
        B = (yy + a * xz + b3 * zz) % M
        C = (a * xx + b3 * xz - a * a % M * zz) % M
        D = (3 * xx + a * zz) % M
        X3 = (xy * A - yz * C) % M
        Y3 = (D * C + B * A) % M
        Z3 = (yz * B + xy * D) % M
        return (X3, Y3, Z3)

    def neg(self, P):
        return (P[0], (-P[1]) % self.M, P[2])

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, m: int, P):
        """Left-to-right double-and-add; m >= 0. Cost = (bits-1) + (popcount-1)."""
        if m < 0:
            return self.mul(-m, self.neg(P))
        if m == 0:
            return O
        R = P
        for bit in bin(m)[3:]:
            R = self.add(R, R)
            if bit == "1":
                R = self.add(R, P)
        return R

    # --- representation ------------------------------------------------
    def on_curve(self, P) -> bool:
        X, Y, Z = P
        M = self.M
        return (Y * Y * Z - (X ** 3 + self.a * X * Z * Z + self.b * Z ** 3)) % M == 0

    def unit(self, t: int) -> bool:
        return t % self.p != 0

    def normalize(self, P, k: int | None = None):
        """Canonical tuple mod p^k: ('aff', x, y) if Z unit, else ('inf', X/Y, Z/Y)."""
        k = self.K if k is None else k
        Mk = self.p ** k
        X, Y, Z = P
        if self.unit(Z):
            zi = pow(Z, -1, self.M)
            return ("aff", X * zi % Mk, Y * zi % Mk)
        if not self.unit(Y):
            raise ArithmeticError("non-unit Y and Z: invalid projective representative")
        yi = pow(Y, -1, self.M)
        return ("inf", X * yi % Mk, Z * yi % Mk)

    def eq(self, P, Q, k: int | None = None) -> bool:
        return self.normalize(P, k) == self.normalize(Q, k)

    def is_O(self, P, k: int | None = None) -> bool:
        n = self.normalize(P, k)
        return n[0] == "inf" and n[1] == 0 and n[2] == 0

    def z(self, P) -> int:
        """Formal parameter z = -X/Y mod p^K (Y must be a unit, i.e. P in E^1 or near it)."""
        X, Y, Z = P
        if not self.unit(Y):
            raise ArithmeticError("Y not a unit")
        return (-X * pow(Y, -1, self.M)) % self.M

    def point_from_z(self, z: int):
        """The point of E^1 with formal parameter z (v_p(z) >= 1): (z : -1 : w(z))."""
        M = self.M
        assert z % self.p == 0
        w = 0
        for _ in range(3 * self.K + 3):
            w = (z ** 3 + self.a * z * w * w + self.b * w ** 3) % M
        P = (z % M, M - 1, w)
        assert self.on_curve(P)
        return P

    def reduce_mod_p(self, P):
        return self.normalize(P, 1)

    # --- lifting -------------------------------------------------------
    def hensel_lift(self, x0: int, y0: int, r: int = 0):
        """Lift (x0, y0) in E(F_p) to Z/p^K with x^ = x0 + p r, y^ by Newton."""
        M, p = self.M, self.p
        x = (x0 + p * r) % M
        f = (x ** 3 + self.a * x + self.b) % M
        y = y0 % p
        assert (y * y - f) % p == 0 and y % p != 0
        for _ in range(self.K + 2):
            y = (y - (y * y - f) * pow(2 * y, -1, M)) % M
        P = (x, y, 1)
        assert self.on_curve(P)
        return P


# --- F_p helpers -------------------------------------------------------------

def legendre(t: int, p: int) -> int:
    t %= p
    if t == 0:
        return 0
    return 1 if pow(t, (p - 1) // 2, p) == 1 else -1


def count_points(p: int, a: int, b: int) -> int:
    return p + 1 + sum(legendre(x ** 3 + a * x + b, p) for x in range(p))


def sqrt_mod(t: int, p: int) -> int | None:
    t %= p
    if t == 0:
        return 0
    if legendre(t, p) != 1:
        return None
    # Tonelli-Shanks
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    zn = 2
    while legendre(zn, p) != -1:
        zn += 1
    m, c, tt, r = s, pow(zn, q, p), pow(t, q, p), pow(t, (q + 1) // 2, p)
    while tt != 1:
        i, t2 = 0, tt
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        bb = pow(c, 1 << (m - i - 1), p)
        m, c, tt, r = i, bb * bb % p, tt * bb * bb % p, r * bb % p
    return r


def random_affine_point(p: int, a: int, b: int, rng: random.Random):
    while True:
        x = rng.randrange(p)
        y = sqrt_mod(x ** 3 + a * x + b, p)
        if y is not None and y != 0:
            if rng.random() < 0.5:
                y = (-y) % p
            return x, y


def prime_factors(N: int) -> list[int]:
    out, d = [], 2
    while d * d <= N:
        while N % d == 0:
            out.append(d)
            N //= d
        d += 1
    if N > 1:
        out.append(N)
    return out


def is_prime(n: int) -> bool:
    return n >= 2 and prime_factors(n) == [n]


# --- affine F_p reference arithmetic (for testing the complete formula) ------

def aff_add(P, Q, p, a):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def self_test(seed: int = 1) -> dict:
    """Check the complete formula against affine arithmetic over F_p and group
    identities over Z/p^K on odd-order curves."""
    rng = random.Random(seed)
    checks = 0
    for p in (53, 61, 101, 127, 547):
        for _ in range(6):
            while True:
                a, b = rng.randrange(p), rng.randrange(1, p)
                if (4 * a ** 3 + 27 * b ** 2) % p and count_points(p, a, b) % 2 == 1:
                    break
            E1 = Curve(p, a, b, 1)
            for _ in range(20):
                P = random_affine_point(p, a, b, rng)
                Q = random_affine_point(p, a, b, rng)
                for (U, V) in ((P, Q), (P, P), (P, (P[0], (-P[1]) % p))):
                    ref = aff_add(U, V, p, a)
                    got = E1.normalize(E1.add((U[0], U[1], 1), (V[0], V[1], 1)), 1)
                    exp = ("inf", 0, 0) if ref is None else ("aff", ref[0], ref[1])
                    assert got == exp, (p, a, b, U, V, got, exp)
                    checks += 1
                got = E1.normalize(E1.add(O, (P[0], P[1], 1)), 1)
                assert got == ("aff", P[0], P[1])
                checks += 1
            # Z/p^K group identities
            K = 5
            E = Curve(p, a, b, K)
            N = count_points(p, a, b)
            for _ in range(4):
                x0, y0 = random_affine_point(p, a, b, rng)
                P = E.hensel_lift(x0, y0, rng.randrange(p ** (K - 1)))
                Q = E.hensel_lift(*random_affine_point(p, a, b, rng), rng.randrange(p ** (K - 1)))
                R = E.hensel_lift(*random_affine_point(p, a, b, rng), 0)
                assert E.eq(E.add(E.add(P, Q), R), E.add(P, E.add(Q, R)))
                assert E.is_O(E.mul(N * p ** (K - 1), P))
                assert E.eq(E.mul(7, P), E.add(E.mul(3, P), E.mul(4, P)))
                assert E.on_curve(E.add(P, Q))
                checks += 4
    return {"self_test_checks": checks, "ok": True}


if __name__ == "__main__":
    print(self_test())
