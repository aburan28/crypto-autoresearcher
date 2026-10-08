"""Ordinary binary curve E_{A,B}: Y^2 + XY = X^3 + A X^2 + B.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/curve.py.
Points are (x, y) tuples; infinity is None.
"""
from __future__ import annotations

import numpy as np


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

    def sub(self, P, Q):
        return self.add(P, self.neg(Q))

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
        """Deterministic lift via half-trace (n odd)."""
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

    def count_by_trace(self) -> int:
        """#E = 1 + 1 + 2 * #{x != 0 : Tr(x+A+B/x^2)=0}."""
        F = self.F
        if hasattr(F, "vmul") and hasattr(F, "vdiv") and hasattr(F, "vtrace"):
            xs = np.arange(1, F.q, dtype=np.int64)
            x2 = F.vmul(xs, xs)
            c = xs ^ self.A ^ F.vdiv(np.full_like(xs, self.B), x2)
            good = int(np.sum(F.vtrace(c) == 0))
        else:
            # Chunked schoolbook path (n=29): use linear trace + schoolbook inv/mul.
            good = 0
            q = F.q
            B = self.B
            A = self.A
            for x in range(1, q):
                x2 = F.mul(x, x)
                c = x ^ A ^ F.mul(B, F.inv(x2))
                if F.trace(c) == 0:
                    good += 1
        return 2 + 2 * good

    def class_bit(self, P) -> int:
        """P |-> Tr(x_P) + Tr(A); infinity treated as 0."""
        if P is None:
            return 0
        return self.F.trace(P[0]) ^ self.F.trace(self.A)


def s3_eval(F, B, x1, x2, x3):
    """S_3(x1,x2,x3) = (x1x2+x1x3+x2x3)^2 + x1x2x3 + B."""
    m = F.mul
    e = m(x1, x2) ^ m(x1, x3) ^ m(x2, x3)
    return m(e, e) ^ m(m(x1, x2), x3) ^ B


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


def factor_out_small(N: int, bound: int = 100000):
    """Trial-factor N; return (h, r_candidate) with r_candidate hopefully prime."""
    h = 1
    n = N
    p = 2
    while p * p <= n and p <= bound:
        while n % p == 0:
            if n // p == 1:
                break
            if p == 2 or (n // p) > p:
                h *= p
                n //= p
            else:
                break
        p = 3 if p == 2 else p + 2
    return h, n


def hasse_trace_bsgs(curve: Curve, max_trials: int = 32) -> int:
    """Return #E(F_q) via Hasse bound + BSGS on random points.

    For q=2^n: #E = q+1-t with |t| <= 2*sqrt(q). For random P,
    [q+1]P = [t]P, so recover t by BSGS in [-W,W].
    """
    F = curve.F
    q = F.q
    W = int(2 * (1 << ((F.n + 1) // 2))) + 4  # >= 2*sqrt(q)
    # baby step size
    m = int(W**0.5) + 2

    def random_point(rng):
        for _ in range(10000):
            x = rng.randrange(0, q)
            P = curve.lift_x(x)
            if P is not None:
                return P
        raise RuntimeError("failed to sample curve point")

    import random as _random

    rng = _random.Random(0xC0FFEE ^ F.n ^ (curve.A & 0xFFFF))
    for trial in range(max_trials):
        P = random_point(rng)
        # Skip if P has tiny order
        if curve.mul(2, P) is None:
            continue
        Q = curve.mul(q + 1, P)  # should equal [t]P
        # BSGS: find t in [-W,W] with [t]P = Q
        # Write t = i - j*m with 0<=i<m, 0<=j<=ceil(2W/m)
        babies = {}
        R = None  # [0]P
        # store [i]P for i=0..m-1; key by (x,y)
        for i in range(m):
            if R is None:
                key = ("O",)
            else:
                key = (R[0], R[1])
            babies[key] = i
            R = curve.add(R, P) if R is not None else P
        # giant: check Q + [j*m]P in babies  => t = i - j*m
        # Also Q - [j*m]P for positive orientation
        Gm = curve.mul(m, P)
        # Search j such that Q + [j]Gm = [i]P => t = i - j*m
        cur = Q
        found = None
        jmax = (2 * W) // m + 3
        for j in range(jmax):
            key = ("O",) if cur is None else (cur[0], cur[1])
            if key in babies:
                i = babies[key]
                t = i - j * m
                if abs(t) <= W:
                    found = t
                    break
            cur = curve.add(cur, Gm)
        if found is None:
            # try negative giants: Q - [j]Gm
            cur = Q
            nGm = curve.neg(Gm) if Gm is not None else None
            for j in range(1, jmax):
                cur = curve.add(cur, nGm)
                key = ("O",) if cur is None else (cur[0], cur[1])
                if key in babies:
                    i = babies[key]
                    t = i + j * m
                    if abs(t) <= W:
                        found = t
                        break
        if found is None:
            continue
        nE = q + 1 - found
        # verify on a fresh point
        P2 = random_point(rng)
        if curve.mul(nE, P2) is None:
            return nE
    raise RuntimeError("hasse_trace_bsgs failed to recover #E")
