#!/usr/bin/env python3
"""Ordinary binary curve Y^2 + XY = X^3 + A X^2 + B over a Field (stdlib).

Point at infinity is None. No numpy. Used by EXP-BINSTD-b94ec8 Stage 1 setup.
"""
from __future__ import annotations

from typing import Any, Optional, Tuple

Point = Optional[Tuple[int, int]]


class Curve:
    def __init__(self, F: Any, A: int, B: int):
        if B == 0:
            raise ValueError("B must be nonzero")
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y) ^ F.mul(x, y)
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.A, x2) ^ self.B
        return lhs == rhs

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def double(self, P: Point) -> Point:
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.mul(lam, lam) ^ lam ^ self.A
        y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):
                return None
            return self.double(P)
        dx = x1 ^ x2
        lam = F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul(self, k: int, P: Point) -> Point:
        R: Point = None
        Q = P
        kk = k
        while kk:
            if kk & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            kk >>= 1
        return R

    def rhs_c(self, x: int) -> int:
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int) -> Point:
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.B))
        c = self.rhs_c(x)
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        return (x, F.mul(x, z))

    def is_x_coord(self, x: int) -> bool:
        if x == 0:
            return True
        return self.F.trace(self.rhs_c(x)) == 0

    def frobenius(self, P: Point) -> Point:
        """Absolute Frobenius (x,y) -> (x^2, y^2)."""
        if P is None:
            return None
        F = self.F
        return (F.square(P[0]), F.square(P[1]))

    def count_by_trace(self) -> int:
        F = self.F
        good = sum(1 for x in range(1, F.q) if F.trace(self.rhs_c(x)) == 0)
        return 2 + 2 * good


def koblitz_order_lucas(n: int, a: int) -> int:
    """#E_a(F_{2^n}) via Lucas recurrence (AC-9). a in {0,1}, B=1."""
    t = 1 if a == 1 else -1
    if n == 0:
        return 2
    if n == 1:
        return (1 << 1) + 1 - t
    s0, s1 = 2, t
    for _ in range(2, n + 1):
        s0, s1 = s1, t * s1 - 2 * s0
    return (1 << n) + 1 - s1


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def factor_out_small(n: int) -> list[tuple[int, int]]:
    """Trial-factor n; return [(p,e), ...]. Sufficient for toy Koblitz orders."""
    factors: list[tuple[int, int]] = []
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            factors.append((p, e))
        p += 1 if p == 2 else 2
    if x > 1:
        factors.append((x, 1))
    return factors


def s3(F: Any, B: int, x1: int, x2: int, x3: int) -> int:
    """Semaev S_3 for binary curves: (x1x2+x1x3+x2x3)^2 + x1x2x3 + B."""
    m = F.mul
    e = m(x1, x2) ^ m(x1, x3) ^ m(x2, x3)
    return m(e, e) ^ m(m(x1, x2), x3) ^ B
