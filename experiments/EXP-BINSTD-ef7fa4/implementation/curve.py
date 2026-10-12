"""Ordinary binary curve E_{A,B}: Y^2 + XY = X^3 + A X^2 + B over a Field.

Points are (x, y) tuples; the point at infinity is None.
"""
import numpy as np


class Curve:
    def __init__(self, F, A, B):
        assert B != 0
        self.F, self.A, self.B = F, A, B

    def on_curve(self, P):
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
        lam = x1 ^ F.div(y1, x1) if hasattr(F, "div") else x1 ^ F.mul(y1, F.inv(x1))
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
        lam = F.div(y1 ^ y2, dx) if hasattr(F, "div") else F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def mul(self, k, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    def rhs_c(self, x):
        """c = x + A + B/x^2 (x != 0); a point with abscissa x exists iff Tr(c) = 0."""
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x):
        """Deterministic lift: for x != 0, y = x * H(c) (half-trace root);
        for x = 0, y = sqrt(B). Returns None if no point has abscissa x."""
        F = self.F
        if x == 0:
            return (0, F.sqrt(self.B))
        c = self.rhs_c(x)
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        return (x, F.mul(x, z))

    def is_x_coord(self, x):
        if x == 0:
            return True
        return self.F.trace(self.rhs_c(x)) == 0

    def count_by_trace(self):
        """#E = 1 (infinity) + 1 (x = 0) + 2 * #{x != 0 : Tr(x + A + B/x^2) = 0}."""
        F = self.F
        if hasattr(F, "vmul"):
            xs = np.arange(1, F.q, dtype=np.int64)
            x2 = F.vmul(xs, xs)
            c = xs ^ self.A ^ F.vdiv(np.full_like(xs, self.B), x2)
            good = int(np.sum(F.vtrace(c) == 0))
        else:
            good = sum(1 for x in range(1, F.q) if F.trace(self.rhs_c(x)) == 0)
        return 2 + 2 * good

    def count_naive(self):
        """Independent naive count: enumerate all (x, y) pairs (small fields only)."""
        F = self.F
        cnt = 1
        for x in range(F.q):
            x2 = F.mul_school(x, x)
            rhs = F.mul_school(x2, x) ^ F.mul_school(self.A, x2) ^ self.B
            for y in range(F.q):
                if F.mul_school(y, y) ^ F.mul_school(x, y) == rhs:
                    cnt += 1
        return cnt


def s3_eval_school(F, B, x1, x2, x3):
    """S_3(x1,x2,x3) = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B, schoolbook arithmetic
    only (independent of table arithmetic and of oracle A)."""
    m = F.mul_school
    e = m(x1, x2) ^ m(x1, x3) ^ m(x2, x3)
    return m(e, e) ^ m(m(x1, x2), x3) ^ B


def is_prime(n):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True
