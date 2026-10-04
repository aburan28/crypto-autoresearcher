"""E_{A,B}: Y^2 + XY = X^3 + A X^2 + B over F_{2^17}, and S_3.

Own point arithmetic (affine, char 2, ordinary curve) and S_3 from
KN-TECH-b18366 / EXP-CERTBIN-4e92d7 object.summation_polynomial:
S_3(x1, x2, x3) = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + B.
Imports nothing from this repository.
"""
from gf2_17 import mul, sq, inv, trace, half_trace, sqrt, N

O = None  # point at infinity


class Curve:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def on_curve(self, P):
        if P is O:
            return True
        x, y = P
        lhs = sq(y) ^ mul(x, y)
        rhs = mul(sq(x), x) ^ mul(self.A, sq(x)) ^ self.B
        return lhs == rhs

    def neg(self, P):
        if P is O:
            return O
        x, y = P
        return (x, x ^ y)

    def double(self, P):
        if P is O:
            return O
        x, y = P
        if x == 0:
            return O  # the point of order 2
        lam = x ^ mul(y, inv(x))
        x3 = sq(lam) ^ lam ^ self.A
        y3 = sq(x) ^ mul(lam, x3) ^ x3
        return (x3, y3)

    def add(self, P, Q):
        if P is O:
            return Q
        if Q is O:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 == y2:
                return self.double(P)
            return O  # Q = -P
        lam = mul(y1 ^ y2, inv(x1 ^ x2))
        x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def smul(self, k, P):
        R = O
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    def lift(self, x):
        """A y with (x, y) on the curve, or None."""
        if x == 0:
            return sqrt(self.B)
        c = x ^ self.A ^ mul(self.B, inv(sq(x)))
        if trace(c) != 0:
            return None
        z = half_trace(c)
        return mul(x, z)


def S3(x1, x2, x3, B):
    s = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
    return sq(s) ^ mul(mul(x1, x2), x3) ^ B


def s3_point_addition_selftest(curve, rng, n_pairs):
    """For random curve points P1, P2 (P1 != +-P2), S_3(x1, x2, x(P1 +- P2)) = 0,
    S_3 symmetric under permutation, and S_3(x1, x2, z) != 0 for a random z
    not in {x(P1+P2), x(P1-P2)} (S_3 has degree 2 in x3)."""
    done = 0
    fails = []
    nonroot_checked = 0
    nonroot_fail = 0
    while done < n_pairs:
        xa = rng.randrange(1, 1 << N)
        xb = rng.randrange(1, 1 << N)
        ya = curve.lift(xa)
        yb = curve.lift(xb)
        if ya is None or yb is None or xa == xb:
            continue
        P1 = (xa, ya)
        P2 = (xb, yb)
        if not (curve.on_curve(P1) and curve.on_curve(P2)):
            fails.append({"reason": "lift not on curve", "x": [xa, xb]})
            done += 1
            continue
        Sp = curve.add(P1, P2)
        Sm = curve.add(P1, curve.neg(P2))
        if Sp is O or Sm is O:
            continue
        ok = True
        for R in (Sp, Sm):
            x3 = R[0]
            if not curve.on_curve(R):
                ok = False
            if S3(xa, xb, x3, curve.B) != 0:
                ok = False
            if S3(x3, xa, xb, curve.B) != 0 or S3(xb, x3, xa, curve.B) != 0:
                ok = False
        z = rng.randrange(1 << N)
        if z not in (Sp[0], Sm[0]):
            nonroot_checked += 1
            if S3(xa, xb, z, curve.B) == 0:
                nonroot_fail += 1
        if not ok:
            fails.append({"x1": xa, "x2": xb, "x_sum": Sp[0], "x_diff": Sm[0]})
        done += 1
    return {"pairs": done, "failures": len(fails), "failure_examples": fails[:5],
            "nonroot_checked": nonroot_checked, "nonroot_unexpected_zero": nonroot_fail,
            "pass": not fails and nonroot_fail == 0}
