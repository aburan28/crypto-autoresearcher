"""Validator's own GF(2^n) and binary-curve arithmetic for joint V1.

Written for TASK-20260913-6c5729 WITHOUT reading
experiments/EXP-ICPERF-66fd51/code/binec.py, code/convert.py, or
inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent.sage.

Sources used: the curve equation from find_points.sage line 8
(E = EllipticCurve(K,[1,1,0,0,1])  ->  y^2 + x*y = x^3 + x^2 + 1) and
line 24 (f = y^2 + X*y - X^3 - X^2 - 1), the field modulus from line 2 of
each INFO*.dimacs (Sage IRR.coefficients(sparse=False), i.e. constant term
first), and standard char-2 Weierstrass formulas.
"""

from __future__ import annotations


class GF2n:
    def __init__(self, n: int, modulus_bits_lsb_first: str):
        assert len(modulus_bits_lsb_first) == n + 1, (n, len(modulus_bits_lsb_first))
        m = 0
        for i, c in enumerate(modulus_bits_lsb_first):
            if c == "1":
                m |= 1 << i
        assert m >> n == 1, "leading coefficient must be 1"
        self.n = n
        self.mod = m
        self.one = 1
        self.zero = 0

    # ---- basic arithmetic -------------------------------------------------
    def add(self, a: int, b: int) -> int:
        return a ^ b

    def reduce(self, a: int) -> int:
        n = self.n
        m = self.mod
        while a.bit_length() > n:
            a ^= m << (a.bit_length() - 1 - n)
        return a

    def mul(self, a: int, b: int) -> int:
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
        return self.reduce(r)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        assert a != 0, "no inverse of 0"
        return self.pow(a, (1 << self.n) - 2)

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    # ---- trace / half-trace ----------------------------------------------
    def trace(self, a: int) -> int:
        t = 0
        x = a
        for _ in range(self.n):
            t ^= x
            x = self.mul(x, x)
        assert t in (0, 1), "trace must land in F_2"
        return t

    def half_trace(self, c: int) -> int:
        """H(c) = sum_{i=0}^{(n-1)/2} c^(4^i); defined for odd n.

        H(c)^2 + H(c) = c + Tr(c), so H(c) solves z^2 + z = c when Tr(c) = 0.
        """
        assert self.n % 2 == 1, "half-trace formula here assumes odd n"
        h = 0
        x = c
        for _ in range((self.n + 1) // 2):
            h ^= x
            x = self.mul(self.mul(x, x), self.mul(x, x))  # x^4
        return h

    def solve_quad(self, c: int):
        """All z with z^2 + z = c."""
        if c == 0:
            return [0, 1]
        if self.trace(c) != 0:
            return []
        z = self.half_trace(c)
        assert self.add(self.mul(z, z), z) == c, "half-trace failed"
        return [z, z ^ 1]

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    # ---- encoding ---------------------------------------------------------
    def from_bits_lsb_first(self, s: str) -> int:
        v = 0
        for i, c in enumerate(s):
            if c == "1":
                v |= 1 << i
        return v

    def from_bits_msb_first(self, s: str) -> int:
        v = 0
        for i, c in enumerate(reversed(s)):
            if c == "1":
                v |= 1 << i
        return v


INF = ("INF",)


class BinaryCurve:
    """y^2 + x*y = x^3 + a*x^2 + b  over GF(2^n).  Here a = b = 1."""

    def __init__(self, F: GF2n, a: int = 1, b: int = 1):
        self.F = F
        self.a = a
        self.b = b

    def is_x_coord(self, x: int) -> bool:
        F = self.F
        if x == 0:
            return True  # y^2 = b always solvable in char 2
        c = F.add(F.add(x, self.a), F.div(self.b, F.mul(x, x)))
        return F.trace(c) == 0

    def points_with_x(self, x: int):
        F = self.F
        if x == 0:
            return [(0, F.sqrt(self.b))]
        c = F.add(F.add(x, self.a), F.div(self.b, F.mul(x, x)))
        zs = F.solve_quad(c)
        return [(x, F.mul(x, z)) for z in zs]

    def on_curve(self, P) -> bool:
        if P is INF:
            return True
        F = self.F
        x, y = P
        lhs = F.add(F.mul(y, y), F.mul(x, y))
        rhs = F.add(F.add(F.mul(F.mul(x, x), x), F.mul(self.a, F.mul(x, x))), self.b)
        return lhs == rhs

    def neg(self, P):
        if P is INF:
            return INF
        x, y = P
        return (x, self.F.add(y, x))

    def add(self, P, Q):
        if P is INF:
            return Q
        if Q is INF:
            return P
        F = self.F
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == F.add(y1, x1):
                return INF
            assert y1 == y2, "same x, y not equal and not negative: impossible on E"
            if x1 == 0:
                return INF
            lam = F.add(x1, F.div(y1, x1))
            x3 = F.add(F.add(F.mul(lam, lam), lam), self.a)
            y3 = F.add(F.mul(x1, x1), F.mul(F.add(lam, 1), x3))
            return (x3, y3)
        lam = F.div(F.add(y1, y2), F.add(x1, x2))
        x3 = F.add(F.add(F.add(F.add(F.mul(lam, lam), lam), x1), x2), self.a)
        y3 = F.add(F.add(F.mul(lam, F.add(x1, x3)), x3), y1)
        return (x3, y3)


def f3_summation(F: GF2n, X1: int, X2: int, X3: int, xr: int) -> int:
    """The fourth summation polynomial specialised exactly as written in
    find_points.sage line 40 (S_4 with the three x_i substituted through the
    elementary symmetric functions e1, e2, e3)."""
    m = F.mul
    a = F.add
    e1 = a(a(X1, X2), X3)
    e2 = a(a(m(X1, X2), m(X2, X3)), m(X1, X3))
    e3 = m(m(X1, X2), X3)

    def p(u, k):
        return F.pow(u, k)

    terms = [
        p(xr, 4),
        p(e1, 4),
        p(e3, 4),
        m(p(e2, 4), p(xr, 4)),
        m(p(e3, 3), xr),
        m(m(e3, p(e2, 2)), p(xr, 3)),
        m(m(e3, p(e1, 2)), xr),
        m(e3, p(xr, 3)),
        m(m(p(e1, 2), p(e3, 2)), p(xr, 2)),
        m(p(e3, 2), p(xr, 4)),
        p(e3, 2),
        m(p(e2, 2), p(xr, 2)),
    ]
    r = 0
    for t in terms:
        r = a(r, t)
    return r


def parse_info(path: str):
    with open(path) as fh:
        lines = [ln.strip() for ln in fh if ln.strip()]
    n, l = (int(v) for v in lines[0].split())
    modulus = lines[1]
    xr_bits = lines[2]
    label = lines[3]
    cert = lines[4]
    assert len(modulus) == n + 1, (path, len(modulus))
    assert len(xr_bits) == n, (path, len(xr_bits))
    return {
        "n": n,
        "l": l,
        "modulus_bits": modulus,
        "xr_bits": xr_bits,
        "label": label,
        "cert_raw": cert,
    }
