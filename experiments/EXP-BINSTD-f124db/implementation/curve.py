"""Ordinary binary curve E_{A,B}: Y^2 + XY = X^3 + A X^2 + B.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/curve.py (schoolbook path).
Infinity is None. Uses Field.solve_artin_schreier for lift_x (even/odd n).
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
        lam = x1 ^ F.mul(y1, F.inv(x1))
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
        lam = F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def mul(self, k: int, P):
        R = None
        Q = P
        kk = k
        while kk:
            if kk & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            kk >>= 1
        return R

    def rhs_c(self, x: int) -> int:
        """c = x + A + B/x^2 (x != 0); point exists iff Tr(c) = 0."""
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int):
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.B))
        c = self.rhs_c(x)
        z = F.solve_artin_schreier(c)
        if z is None:
            return None
        return (x, F.mul(x, z))

    def count_by_trace(self) -> int:
        F = self.F
        good = 0
        for x in range(1, F.q):
            if F.trace(self.rhs_c(x)) == 0:
                good += 1
        return 2 + 2 * good

    def frobenius_point(self, P, m: int):
        """Apply (x,y) |-> (x^{2^m}, y^{2^m})."""
        if P is None:
            return None
        F = self.F
        return (F.frobenius(P[0], m), F.frobenius(P[1], m))

    def is_endomorphism_image_on_curve(self, P, m: int) -> bool:
        """True iff Frobenius^m(P) lands on this curve (endomorphism test)."""
        return self.on_curve(self.frobenius_point(P, m))
