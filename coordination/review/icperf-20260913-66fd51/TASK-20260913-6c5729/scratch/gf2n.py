"""Validator's own GF(2^n) / binary-curve arithmetic for V1 (TASK-20260913-6c5729).

Written from: the INFO files (line 2 = field polynomial, coefficient string
lowest-degree first, per find_points.sage `coefficients(sparse=False)`), the curve
E: y^2 + x*y = x^3 + x^2 + 1 (EllipticCurve(K,[1,1,0,0,1])), and the polynomial
f3 on line 40 of find_points.sage.  NOT read before writing this: code/binec.py,
code/convert.py, Weil_descent.sage.

Field elements are Python ints; bit i is the coefficient of a^i.
"""

from __future__ import annotations


def poly_from_string_le(s: str) -> int:
    """'11100100000000000001' -> int with bit i = s[i] (lowest degree first)."""
    v = 0
    for i, ch in enumerate(s.strip()):
        if ch == "1":
            v |= 1 << i
        elif ch != "0":
            raise ValueError(s)
    return v


def poly_from_string_be(s: str) -> int:
    """Reverse convention: s[0] is the highest-degree coefficient."""
    return poly_from_string_le(s.strip()[::-1])


def to_string_le(x: int, width: int) -> str:
    return "".join("1" if (x >> i) & 1 else "0" for i in range(width))


def poly_deg(p: int) -> int:
    return p.bit_length() - 1


def poly_mulmod_raw(a: int, b: int, mod: int) -> int:
    """Carry-less multiply then reduce modulo `mod` (mod has leading bit set)."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
    return poly_mod(r, mod)


def poly_mod(r: int, mod: int) -> int:
    dm = poly_deg(mod)
    while r and poly_deg(r) >= dm:
        r ^= mod << (poly_deg(r) - dm)
    return r


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_mod(a, b)
    return a


class GF2n:
    def __init__(self, modulus_string_le: str):
        self.mod = poly_from_string_le(modulus_string_le)
        self.n = poly_deg(self.mod)
        if not self.is_irreducible():
            raise ValueError("modulus is not irreducible: %s" % modulus_string_le)

    # --- ring ops ---
    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        return poly_mulmod_raw(a, b, self.mod)

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
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, (1 << self.n) - 2)

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    def trace(self, a: int) -> int:
        t = 0
        x = a
        for _ in range(self.n):
            t ^= x
            x = self.sqr(x)
        assert t in (0, 1), "trace not in GF(2): modulus broken"
        return t

    def half_trace(self, a: int) -> int:
        """For odd n: H(a) = sum_{i=0}^{(n-1)/2} a^(2^(2i)); satisfies H^2 + H = a + Tr(a)."""
        assert self.n % 2 == 1
        h = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            h ^= x
            x = self.sqr(self.sqr(x))
        return h

    def solve_quadratic(self, c: int):
        """Roots z of z^2 + z = c, or None if Tr(c) = 1."""
        if self.trace(c) == 1:
            return None
        z = self.half_trace(c)
        assert self.sqr(z) ^ z == c
        return (z, z ^ 1)

    # --- Rabin irreducibility test ---
    def is_irreducible(self) -> bool:
        n = self.n
        mod = self.mod
        # x^(2^n) mod f
        x = 2
        xp = x
        for _ in range(n):
            xp = poly_mulmod_raw(xp, xp, mod)
        if xp != x:
            return False
        primes = [p for p in range(2, n + 1) if n % p == 0 and all(p % q for q in range(2, p))]
        for p in primes:
            xq = x
            for _ in range(n // p):
                xq = poly_mulmod_raw(xq, xq, mod)
            if poly_gcd(xq ^ x, mod) != 1:
                return False
        return True


class BinaryCurve:
    """y^2 + x*y = x^3 + a2*x^2 + a6 over GF2n.  Points: (x, y) tuples or None (= O)."""

    def __init__(self, F: GF2n, a2: int = 1, a6: int = 1):
        self.F = F
        self.a2 = a2
        self.a6 = a6

    def on_curve(self, P) -> bool:
        if P is None:
            return True
        F = self.F
        x, y = P
        lhs = F.sqr(y) ^ F.mul(x, y)
        rhs = F.mul(F.sqr(x), x) ^ F.mul(self.a2, F.sqr(x)) ^ self.a6
        return lhs == rhs

    def curve_rhs_trace_arg(self, x: int) -> int:
        """c(x) = x + a2 + a6/x^2; y = x*z with z^2 + z = c(x).  x != 0."""
        F = self.F
        return x ^ self.a2 ^ F.mul(self.a6, F.inv(F.sqr(x)))

    def x_on_curve(self, x: int) -> bool:
        F = self.F
        if x == 0:
            # y^2 = a6; always solvable in char 2 (squaring is a bijection)
            return True
        return F.trace(self.curve_rhs_trace_arg(x)) == 0

    def lift(self, x: int):
        """Both points with this x, or None."""
        F = self.F
        if x == 0:
            y = F.pow(self.a6, 1 << (F.n - 1))  # sqrt
            assert F.sqr(y) == self.a6
            P = (0, y)
            assert self.on_curve(P)
            return (P, P)  # (0,y) and (0, y+0) coincide
        c = self.curve_rhs_trace_arg(x)
        zs = F.solve_quadratic(c)
        if zs is None:
            return None
        pts = tuple((x, F.mul(x, z)) for z in zs)
        for P in pts:
            assert self.on_curve(P), P
        return pts

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
            if y1 ^ y2 == x1:  # Q = -P (includes x1 = 0 case where P = -P)
                return None
            # doubling, x1 != 0
            lam = x1 ^ F.div(y1, x1)
            x3 = F.sqr(lam) ^ lam ^ self.a2
            y3 = F.sqr(x1) ^ F.mul(lam ^ 1, x3)
        else:
            lam = F.div(y1 ^ y2, x1 ^ x2)
            x3 = F.sqr(lam) ^ lam ^ x1 ^ x2 ^ self.a2
            y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        R = (x3, y3)
        assert self.on_curve(R), ("addition left the curve", P, Q, R)
        return R


def f3_find_points(F: GF2n, X1: int, X2: int, X3: int, xR: int) -> int:
    """Line 40 of find_points.sage, verbatim structure:
    f3 = x^4 + e1^4 + e3^4 + e2^4*x^4 + e3^3*x + e3*e2^2*x^3 + e3*e1^2*x
         + e3*x^3 + e1^2*e3^2*x^2 + e3^2*x^4 + e3^2 + e2^2*x^2
    with e1 = X1+X2+X3, e2 = X1X2+X2X3+X1X3, e3 = X1X2X3, x = x_R."""
    m = F.mul
    e1 = X1 ^ X2 ^ X3
    e2 = m(X1, X2) ^ m(X2, X3) ^ m(X1, X3)
    e3 = m(m(X1, X2), X3)
    x = xR
    x2 = m(x, x)
    x3 = m(x2, x)
    x4 = m(x2, x2)
    e1_2 = m(e1, e1)
    e1_4 = m(e1_2, e1_2)
    e2_2 = m(e2, e2)
    e2_4 = m(e2_2, e2_2)
    e3_2 = m(e3, e3)
    e3_3 = m(e3_2, e3)
    e3_4 = m(e3_2, e3_2)
    v = 0
    v ^= x4
    v ^= e1_4
    v ^= e3_4
    v ^= m(e2_4, x4)
    v ^= m(e3_3, x)
    v ^= m(m(e3, e2_2), x3)
    v ^= m(m(e3, e1_2), x)
    v ^= m(e3, x3)
    v ^= m(m(e1_2, e3_2), x2)
    v ^= m(e3_2, x4)
    v ^= e3_2
    v ^= m(e2_2, x2)
    return v
