"""E: Y^2 + XY = X^3 + A X^2 + B over F_{2^n}; affine points, O = None."""
from __future__ import annotations

import numpy as np


class Curve:
    def __init__(self, F, a, b):
        self.F, self.a, self.b = F, a, b

    def on_curve(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y) ^ F.mul(x, y)
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.a, x2) ^ self.b
        return lhs == rhs

    def neg(self, P):
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 == y2:
                return self.dbl(P)
            return None  # Q = -P
        lam = F.div(y1 ^ y2, x1 ^ x2)
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.a
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def dbl(self, P):
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.div(y1, x1)
        x3 = F.mul(lam, lam) ^ lam ^ self.a
        y3 = F.mul(x1, x1) ^ F.mul(lam, x3) ^ x3
        return (x3, y3)

    def mul(self, k, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.dbl(Q)
            k >>= 1
        return R

    def lift_x(self, x):
        """A point with x-coordinate x, or None if x is not liftable (x != 0)."""
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.b))
        c = x ^ self.a ^ F.div(self.b, F.mul(x, x))
        if F.trace(c):
            return None
        z = F.halftrace(c)
        assert F.mul(z, z) ^ z == c
        return (x, F.mul(x, z))

    def count_points(self):
        """#E = 1 + 1 + 2 * #{x != 0 : Tr(x + A + B/x^2) = 0} (exact)."""
        F = self.F
        xs = np.arange(1, F.size, dtype=np.int64)
        c = xs ^ self.a ^ F.vmul(self.b, F.vinv(F.vmul(xs, xs)))
        tr = F.vtrace(c)
        return 2 + 2 * int((tr == 0).sum())


def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True
