"""E_{A,B}: Y^2 + XY = X^3 + A X^2 + B over F_{2^17} (EXP-CERTBIN-4e92d7 object.curve).

Affine points are (x, y) tuples; the point at infinity is None.
Standard characteristic-2 chord-and-tangent formulas, written for this task.
"""
import gf2n as F


class Curve:
    def __init__(self, A, B):
        assert B != 0
        self.A = A
        self.B = B

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        lhs = F.sq(y) ^ F.mul(x, y)
        rhs = F.mul(F.sq(x), x) ^ F.mul(self.A, F.sq(x)) ^ self.B
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
            if y1 == y2 and x1 != 0:
                return self.dbl(P)
            return None  # Q = -P (or P = -P with x = 0)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def dbl(self, P):
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.sq(lam) ^ lam ^ self.A
        y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def lift_x(self, x):
        """Return a point with abscissa x, or None if x is not an abscissa.
        For x != 0, put y = x z: z^2 + z = x + A + B/x^2."""
        if x == 0:
            return (0, F.sqrt(self.B))
        c = x ^ self.A ^ F.mul(self.B, F.inv(F.sq(x)))
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        assert F.sq(z) ^ z == c
        return (x, F.mul(x, z))

    def random_point(self, rng):
        while True:
            x = int(rng.integers(1, 1 << F.N))
            P = self.lift_x(x)
            if P is not None:
                if int(rng.integers(0, 2)):
                    P = self.neg(P)
                assert self.on_curve(P)
                return P


def S3(x1, x2, x3, B):
    """S_3(x_1, x_2, x_3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B (KN-TECH-b18366)."""
    u = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.sq(u) ^ F.mul(F.mul(x1, x2), x3) ^ B
