"""Ordinary binary curve E_{A,B}: Y^2 + XY = X^3 + A X^2 + B.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/curve.py.
Points are (x, y) tuples; infinity is None.
"""
from __future__ import annotations


class Curve:
    def __init__(self, F, A: int, B: int):
        assert B != 0
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.mul(y, y) ^ F.mul(x, y)
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.A, x2) ^ self.B
        return lhs == rhs

    def neg(self, P):
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def double(self, P):
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.div(y1, x1)
        x3 = F.mul(lam, lam) ^ lam ^ self.A
        y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P, Q):
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
        lam = F.div(y1 ^ y2, dx)
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul(self, k: int, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    def rhs_c(self, x: int) -> int:
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int):
        """Lift x to a point; brute-force y when field is small / n even."""
        F = self.F
        if x == 0:
            # y^2 = B
            for y in range(F.q):
                if F.mul(y, y) == self.B:
                    return (0, y)
            return None
        # y^2 + x y = x^3 + A x^2 + B
        x2 = F.mul(x, x)
        rhs = F.mul(x2, x) ^ F.mul(self.A, x2) ^ self.B
        for y in range(F.q):
            if (F.mul(y, y) ^ F.mul(x, y)) == rhs:
                return (x, y)
        return None

    def is_x_coord(self, x: int) -> bool:
        return self.lift_x(x) is not None

    def enumerate_points(self):
        pts = [None]
        for x in range(self.F.q):
            P = self.lift_x(x)
            if P is None:
                continue
            pts.append(P)
            N = self.neg(P)
            if N != P:
                pts.append(N)
        return pts
