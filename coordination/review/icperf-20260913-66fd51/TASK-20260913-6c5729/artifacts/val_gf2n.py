"""Validator's own GF(2^n) and binary-curve arithmetic for joint V1 of
REVIEW-ICPERF-20260913-66fd51 (TASK-20260913-6c5729).

Written fresh by the validator session on 2026-09-15 WITHOUT reading
experiments/EXP-ICPERF-66fd51/code/binec.py, code/convert.py,
inputs/TRIMOSKA-ECICB-2024/upstream/Weil_descent.sage, or the contents of
any file under this task's scratch/ directory. Sources used: the curve
equation in find_points.sage line 8/24 (y^2 + xy = x^3 + x^2 + 1), the
INFO-file modulus string (little-endian F_2 coefficient string, x^0 first,
as written by find_points.sage lines 10-12), and textbook binary-field /
binary-curve formulas.

Element representation: Python int, bit i = coefficient of a^i, where a is
the class of x in F_2[x]/(modulus).
"""


class GF2n:
    def __init__(self, n, modulus_int):
        assert modulus_int >> n == 1, "modulus must have degree exactly n"
        self.n = n
        self.mod = modulus_int
        self.order = (1 << n) - 1
        # trace mask: Tr(x) = parity(x & mask), because Tr is F_2-linear
        mask = 0
        for i in range(n):
            if self.trace_slow(1 << i):
                mask |= 1 << i
        self.trmask = mask

    @classmethod
    def from_info_modulus(cls, n, s):
        s = s.strip()
        assert len(s) == n + 1, (len(s), n)
        m = 0
        for i, ch in enumerate(s):
            if ch == '1':
                m |= 1 << i
            else:
                assert ch == '0'
        return cls(n, m)

    def modulus_str(self):
        terms = [f"x^{i}" if i > 1 else ("x" if i == 1 else "1")
                 for i in range(self.n, -1, -1) if (self.mod >> i) & 1]
        return " + ".join(terms)

    def mul(self, x, y):
        r = 0
        n = self.n
        mod = self.mod
        while y:
            if y & 1:
                r ^= x
            y >>= 1
            x <<= 1
            if (x >> n) & 1:
                x ^= mod
        return r

    def sq(self, x):
        return self.mul(x, x)

    def pow(self, x, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, x)
            x = self.mul(x, x)
            e >>= 1
        return r

    def inv(self, x):
        assert x != 0, "inverse of zero"
        return self.pow(x, self.order - 1)

    def trace_slow(self, x):
        t = 0
        y = x
        for _ in range(self.n):
            t ^= y
            y = self.mul(y, y)
        assert t in (0, 1), "trace must land in F_2"
        return t

    def trace(self, x):
        return bin(x & self.trmask).count('1') & 1

    def half_trace(self, c):
        """For odd n: H(c) = sum_{i=0}^{(n-1)/2} c^(2^(2i)); H^2 + H = c + Tr(c)."""
        assert self.n % 2 == 1
        h = 0
        y = c
        for _ in range((self.n - 1) // 2 + 1):
            h ^= y
            y = self.sq(self.sq(y))
        return h

    def solve_quadratic(self, c):
        """Return the two roots z of z^2 + z = c in F_{2^n}, or [] if none."""
        if self.trace(c) != 0:
            return []
        z = self.half_trace(c)
        assert self.sq(z) ^ z == c, "half-trace root failed its own check"
        return [z, z ^ 1]


def decode_le(bits):
    """Generator convention (find_points.sage coefficients(sparse=False)):
    character i is the coefficient of a^i."""
    v = 0
    for i, ch in enumerate(bits.strip()):
        if ch == '1':
            v |= 1 << i
        else:
            assert ch == '0', bits
    return v


def decode_be(bits):
    """Big-endian reading: the string is the binary numeral, first char most
    significant."""
    return int(bits.strip(), 2)


class BinaryCurve:
    """y^2 + xy = x^3 + a2 x^2 + a6 over GF(2^n) (a1 = 1, a3 = a4 = 0)."""

    def __init__(self, F, a2, a6):
        self.F = F
        self.a2 = a2
        self.a6 = a6

    def rhs(self, x):
        F = self.F
        return F.mul(F.mul(x, x), x) ^ F.mul(self.a2, F.mul(x, x)) ^ self.a6

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        F = self.F
        return F.mul(y, y) ^ F.mul(x, y) == self.rhs(x)

    def x_criterion(self, x):
        """Tr(x + a2 + a6 / x^2) for x != 0: 0 iff x is an x-coordinate of a
        point of E(F_{2^n}); returns None for x = 0 (where y^2 = a6 always has
        the unique root sqrt(a6))."""
        F = self.F
        if x == 0:
            return None
        return F.trace(x ^ self.a2 ^ F.mul(self.a6, F.sq(F.inv(x))))

    def ys(self, x):
        """All y in F_{2^n} with (x, y) on the curve."""
        F = self.F
        if x == 0:
            # y^2 = a6; squaring is a bijection, sqrt(a6) = a6^(2^(n-1))
            y = F.pow(self.a6, 1 << (F.n - 1))
            assert F.sq(y) == self.a6
            return [y]
        c = x ^ self.a2 ^ F.mul(self.a6, F.sq(F.inv(x)))
        zs = F.solve_quadratic(c)
        out = [F.mul(x, z) for z in zs]
        for y in out:
            assert self.on_curve((x, y))
        return out

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P, Q):
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y1 ^ y2 == x1:  # Q = -P (covers the 2-torsion point x = 0)
                return None
            # doubling, x1 != 0 here (x = 0 point is 2-torsion, handled above)
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sq(lam) ^ lam ^ self.a2
            y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
        else:
            lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
            x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.a2
            y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        R = (x3, y3)
        assert self.on_curve(R), "addition left the curve: formula error"
        return R


def summation_poly_f3(F, X1, X2, X3, x):
    """f3 exactly as written in find_points.sage line 40 (with e1,e2,e3 from
    lines 37-39), evaluated over F. Characteristic 2, so +/- coincide."""
    m = F.mul
    e1 = X1 ^ X2 ^ X3
    e2 = m(X1, X2) ^ m(X2, X3) ^ m(X1, X3)
    e3 = m(m(X1, X2), X3)
    p = F.pow
    x2 = p(x, 2); x3 = p(x, 3); x4 = p(x, 4)
    t = 0
    t ^= x4
    t ^= p(e1, 4)
    t ^= p(e3, 4)
    t ^= m(p(e2, 4), x4)
    t ^= m(p(e3, 3), x)
    t ^= m(m(e3, p(e2, 2)), x3)
    t ^= m(m(e3, p(e1, 2)), x)
    t ^= m(e3, x3)
    t ^= m(m(p(e1, 2), p(e3, 2)), x2)
    t ^= m(p(e3, 2), x4)
    t ^= p(e3, 2)
    t ^= m(p(e2, 2), x2)
    return t


class GF2n_ext2:
    """F_{2^{2n}} = F_{2^n}[z]/(z^2 + z + 1), valid when n is odd (Tr_n(1) = 1
    makes z^2 + z + 1 irreducible over F_{2^n}). Elements are pairs (u, v)
    meaning u + v z."""

    def __init__(self, F):
        assert F.n % 2 == 1
        self.F = F

    def add(self, A, B):
        return (A[0] ^ B[0], A[1] ^ B[1])

    def mul(self, A, B):
        F = self.F
        u1, v1 = A
        u2, v2 = B
        vv = F.mul(v1, v2)  # coefficient of z^2 = z + 1
        return (F.mul(u1, u2) ^ vv, F.mul(u1, v2) ^ F.mul(u2, v1) ^ vv)

    def inv(self, A):
        F = self.F
        u, v = A
        # conjugate: z -> z + 1; (u + v z)(u + v + v z) = u^2 + uv + v^2 in F
        N = F.sq(u) ^ F.mul(u, v) ^ F.sq(v)
        assert N != 0
        Ni = F.inv(N)
        return (F.mul(u ^ v, Ni), F.mul(v, Ni))

    def embed(self, u):
        return (u, 0)

    def is_zero(self, A):
        return A == (0, 0)


class BinaryCurveExt2:
    """The same curve y^2 + xy = x^3 + a2 x^2 + a6 with points over F_{2^{2n}}."""

    def __init__(self, K, a2, a6):
        self.K = K
        self.a2 = K.embed(a2)
        self.a6 = K.embed(a6)

    def on_curve(self, P):
        if P is None:
            return True
        K = self.K
        x, y = P
        lhs = K.add(K.mul(y, y), K.mul(x, y))
        rhs = K.add(K.add(K.mul(K.mul(x, x), x), K.mul(self.a2, K.mul(x, x))), self.a6)
        return lhs == rhs

    def ys_for_base_x(self, x_base):
        """y in F_{2^{2n}} for x in F_{2^n}: y = x w with w^2 + w = c,
        c = x + a2 + a6/x^2 in F_{2^n}. If Tr_n(c) = 0, w in F_{2^n} (half
        trace). If Tr_n(c) = 1 (n odd), w = H(c + 1) + z, since
        (H(c+1) + z)^2 + (H(c+1) + z) = (c + 1) + (z^2 + z) = c + 1 + 1 = c."""
        F = self.K.F
        K = self.K
        assert x_base != 0
        c = x_base ^ self.a2[0] ^ F.mul(self.a6[0], F.sq(F.inv(x_base)))
        if F.trace(c) == 0:
            w = (F.half_trace(c), 0)
        else:
            w = (F.half_trace(c ^ 1), 1)
        assert K.add(K.mul(w, w), w) == (c, 0)
        x = K.embed(x_base)
        y = K.mul(x, w)
        out = [y, K.add(y, x)]
        for yy in out:
            assert self.on_curve((x, yy))
        return out

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, self.K.add(x, y))

    def add(self, P, Q):
        K = self.K
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if K.add(y1, y2) == x1:
                return None
            lam = K.add(x1, K.mul(y1, K.inv(x1)))
            x3 = K.add(K.add(K.mul(lam, lam), lam), self.a2)
            y3 = K.add(K.mul(x1, x1), K.mul(K.add(lam, (1, 0)), x3))
        else:
            lam = K.mul(K.add(y1, y2), K.inv(K.add(x1, x2)))
            x3 = K.add(K.add(K.add(K.add(K.mul(lam, lam), lam), x1), x2), self.a2)
            y3 = K.add(K.add(K.mul(lam, K.add(x1, x3)), x3), y1)
        R = (x3, y3)
        assert self.on_curve(R), "ext addition left the curve: formula error"
        return R
