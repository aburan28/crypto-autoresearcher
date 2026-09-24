"""Curve E_{A,B}: Y^2 + XY = X^3 + A X^2 + B over F_2^17, and S_3.

TASK-20260924-7e2d94. Written from EXP-CERTBIN-4e92d7 object.curve and
KN-TECH-b18366 only. The group law below is derived here from the curve
equation (chord-and-tangent), not copied:

  chord (x1 != x2): lam = (y1 + y2)/(x1 + x2),
                    x3 = lam^2 + lam + x1 + x2 + A,
                    y3 = lam*(x1 + x3) + x3 + y1;
  tangent (x1 != 0): lam = x1 + y1/x1,
                     x3 = lam^2 + lam + A,
                     y3 = x1^2 + (lam + 1)*x3;
  negation: -(x, y) = (x, x + y).

S_3(x1, x2, x3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B   (KN-TECH-b18366).
"""
import numpy as np

import gf2n as F


class Curve:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    # ------------------------------------------------------------ points; None is O
    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        lhs = F.sqr(y) ^ F.mul(x, y)
        rhs = F.mul(F.sqr(x), x) ^ F.mul(self.A, F.sqr(x)) ^ self.B
        return lhs == rhs

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x1:           # Q = -P (covers the 2-torsion point x = 0 too)
                return None
            # P == Q: doubling
            if x1 == 0:
                return None
            lam = x1 ^ F.div(y1, x1)
            x3 = F.sqr(lam) ^ lam ^ self.A
            y3 = F.sqr(x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        lam = F.div(y1 ^ y2, x1 ^ x2)
        x3 = F.sqr(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def smul(self, k, P):
        R = None
        Q = P
        if k < 0:
            k = -k
            Q = self.neg(P)
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.add(Q, Q)
            k >>= 1
        return R

    def lift_x(self, x):
        """A point with abscissa x, or None if x is not an abscissa (x != 0)."""
        if x == 0:
            # y^2 = B: y = B^(2^16)
            return (0, F.power(self.B, 1 << (F.N - 1)))
        c = x ^ self.A ^ F.div(self.B, F.sqr(x))   # z^2 + z = x + A + B/x^2, y = x z
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        return (x, F.mul(x, z))

    def random_point(self, rng):
        while True:
            x = int(rng.integers(1, 1 << F.N))
            P = self.lift_x(x)
            if P is not None:
                if rng.integers(0, 2):
                    P = self.neg(P)
                return P

    def S3(self, x1, x2, x3):
        s = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
        return F.sqr(s) ^ F.mul(F.mul(x1, x2), x3) ^ self.B

    def count_points_vectorised(self):
        """#E = 1 (O) + 1 (x = 0) + 2 * #{x != 0 : Tr(x + A + B/x^2) = 0}."""
        x = np.arange(1, 1 << F.N, dtype=np.uint64)
        # B/x^2 = B * (x^-1)^2 ; x^-1 = x^(2^17 - 2) by square-and-multiply
        e = F.ORDER_MULT - 1
        r = np.ones_like(x)
        base = x.copy()
        while e:
            if e & 1:
                r = F.vmul(r, base)
            base = F.vmul(base, base)
            e >>= 1
        xinv = r
        c = x ^ np.uint64(self.A) ^ F.vmul(np.uint64(self.B), F.vmul(xinv, xinv))
        s = c.copy()
        y = c.copy()
        for _ in range(F.N - 1):
            y = F.vmul(y, y)
            s ^= y
        # trace is 0 or 1
        assert np.all((s == 0) | (s == 1))
        n_tr0 = int(np.count_nonzero(s == 0))
        return 2 + 2 * n_tr0
