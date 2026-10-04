"""E_{A,B}: Y^2 + XY = X^3 + A X^2 + B over F_{2^17} (spec `object.curve`).

Affine group law for ordinary binary curves (Weierstrass form above):
  -(x, y)            = (x, x + y)
  P + Q, x1 != x2    : l = (y1 + y2)/(x1 + x2), x3 = l^2 + l + x1 + x2 + A,
                       y3 = l (x1 + x3) + x3 + y1
  2P, x1 != 0        : l = x1 + y1/x1, x3 = l^2 + l + A, y3 = x1^2 + (l + 1) x3
  2P, x1 == 0        : O   ((0, sqrt(B)) has order 2)
The point at infinity O is None. Correctness is checked by the self-tests
(on-curve closure and [#E]P = O on random points), not assumed.
"""
import numpy as np

import gf2n as F


class Curve:
    def __init__(self, A: int, B: int):
        if B == 0:
            raise ValueError("B = 0 is singular")
        self.A, self.B = A, B

    # -------------------------------------------------------------- basics --
    def on_curve(self, P) -> bool:
        if P is None:
            return True
        x, y = P
        lhs = F.sq(y) ^ F.mul(x, y)
        rhs = F.mul(F.sq(x), x) ^ F.mul(self.A, F.sq(x)) ^ self.B
        return lhs == rhs

    @staticmethod
    def neg(P):
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def double(self, P):
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.sq(lam) ^ lam ^ self.A
        y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):          # Q = -P
                return None
            return self.double(P)        # Q = P
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

    def smul(self, k: int, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    # ------------------------------------------------------------- points --
    def lift_x(self, x: int, which: int = 0):
        """A point with abscissa x, or None if x is not an abscissa."""
        if x == 0:
            return (0, F.sqrt(self.B))
        c = x ^ self.A ^ F.mul(self.B, F.inv(F.sq(x)))
        if F.trace(c):
            return None
        z = F.half_trace(c)             # z^2 + z = c since Tr(c) = 0, n odd
        if which:
            z ^= 1
        return (x, F.mul(x, z))

    def random_point(self, rng):
        while True:
            x = int(rng.integers(1, F.SIZE))
            P = self.lift_x(x, int(rng.integers(0, 2)))
            if P is not None:
                return P

    # -------------------------------------------------------------- count --
    def order(self) -> int:
        """#E = 1 (O) + 1 (x = 0) + 2 #{x != 0 : Tr(x + A + B/x^2) = 0}."""
        xs = np.arange(1, F.SIZE, dtype=np.int64)
        c = xs ^ self.A ^ F.vmul(self.B, F.vinv(F.vsq(xs)))
        good = int(np.count_nonzero(F.vtrace(c) == 0))
        return 2 + 2 * good


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def cofactor_split(order: int):
    """Return (h, q) if #E = h*q with h in {2, 4} and q prime, else None."""
    for h in (2, 4):
        if order % h == 0 and is_prime(order // h):
            return h, order // h
    return None
