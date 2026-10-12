#!/usr/bin/env python3
"""GF(2^n) arithmetic, binary Koblitz curve arithmetic, and Semaev summation
polynomials for EXP-FROB-30006a.

Written from the definitions; no code is reused from the Trimoska generator
(Sage) or from WDSat.  Conventions:

* A field element is a Python int whose bit i is the coefficient of t^i in the
  polynomial basis {1, t, ..., t^(n-1)} modulo the declared irreducible `modulus`
  (bit i of `modulus` is the coefficient of t^i; degree exactly n).
* Curve E_a : y^2 + x y = x^3 + a x^2 + 1 over GF(2^n), a in {0, 1}  (b = 1).
* Points are (x, y) tuples; None is the point at infinity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple


# ----------------------------------------------------------------------------- polynomials over F_2

def poly_mulmod(a: int, b: int, mod: int, n: int) -> int:
    r = 0
    top = 1 << n
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a & top:
            a ^= mod
    return r


def poly_mul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
    return r


def poly_deg(a: int) -> int:
    return a.bit_length() - 1


def poly_divmod(a: int, b: int) -> Tuple[int, int]:
    if b == 0:
        raise ZeroDivisionError
    q = 0
    db = poly_deg(b)
    while a and poly_deg(a) >= db:
        s = poly_deg(a) - db
        q ^= 1 << s
        a ^= b << s
    return q, a


def poly_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, poly_divmod(a, b)[1]
    return a


def poly_powmod(base: int, e: int, mod: int) -> int:
    """base^e mod `mod` in F_2[t] (mod of any degree)."""
    n = poly_deg(mod)
    r = 1
    base = poly_divmod(base, mod)[1]
    while e:
        if e & 1:
            r = poly_mulmod(r, base, mod, n)
        base = poly_mulmod(base, base, mod, n)
        e >>= 1
    return r


def is_irreducible(f: int) -> bool:
    """Rabin's irreducibility test over F_2 for a polynomial of degree d >= 1."""
    d = poly_deg(f)
    if d < 1:
        return False
    if d == 1:
        return True
    # t^(2^d) == t mod f
    if poly_powmod(2, 1 << d, f) != 2:
        return False
    # for each prime p | d: gcd(f, t^(2^(d/p)) - t) == 1
    primes = []
    m = d
    p = 2
    while p * p <= m:
        if m % p == 0:
            primes.append(p)
            while m % p == 0:
                m //= p
        p += 1
    if m > 1:
        primes.append(m)
    for p in primes:
        h = poly_powmod(2, 1 << (d // p), f) ^ 2
        if poly_gcd(f, h) != 1:
            return False
    return True


def lowest_weight_irreducible(n: int) -> int:
    """The irreducible degree-n polynomial of lowest weight, then lowest integer
    encoding: trinomials t^n + t^k + 1 (k = 1..n-1) first, then pentanomials.
    Deterministic, so the field is reproducible from n alone."""
    for k in range(1, n):
        f = (1 << n) | (1 << k) | 1
        if is_irreducible(f):
            return f
    for k3 in range(3, n):
        for k2 in range(2, k3):
            for k1 in range(1, k2):
                f = (1 << n) | (1 << k3) | (1 << k2) | (1 << k1) | 1
                if is_irreducible(f):
                    return f
    raise ValueError("no low-weight irreducible found")


# ----------------------------------------------------------------------------- the field

@dataclass(frozen=True)
class GF2n:
    n: int
    modulus: int

    def __post_init__(self):
        if poly_deg(self.modulus) != self.n:
            raise ValueError("modulus degree must equal n")
        if not is_irreducible(self.modulus):
            raise ValueError("modulus is not irreducible")

    def mul(self, a: int, b: int) -> int:
        return poly_mulmod(a, b, self.modulus, self.n)

    def sqr(self, a: int) -> int:
        return poly_mulmod(a, a, self.modulus, self.n)

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
            raise ZeroDivisionError("inverse of 0")
        return self.pow(a, (1 << self.n) - 2)

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def trace(self, a: int) -> int:
        t = a
        for _ in range(self.n - 1):
            t = self.sqr(t) ^ a
        assert t in (0, 1)
        return t

    def half_trace(self, a: int) -> int:
        """n odd: H(a) = sum_{i=0}^{(n-1)/2} a^(4^i); H(a)^2 + H(a) = a + Tr(a)."""
        if self.n % 2 == 0:
            raise NotImplementedError("half-trace needs odd n")
        h = a
        for _ in range((self.n - 1) // 2):
            h = self.sqr(self.sqr(h)) ^ a
        return h

    def solve_quadratic(self, b: int, c: int) -> List[int]:
        """All roots z in GF(2^n) of z^2 + b z + c = 0 (0, 1 or 2 roots)."""
        if b == 0:
            return [self.sqrt(c)]
        d = self.mul(c, self.inv(self.sqr(b)))
        if self.trace(d) != 0:
            return []
        w = self.half_trace(d)
        assert self.sqr(w) ^ w == d
        z = self.mul(b, w)
        return [z, z ^ b]

    # linear algebra helpers (an element is a row vector in F_2^n)
    def squaring_matrix(self) -> List[int]:
        """Rows s_i = t^(2 i) as ints, so sqr(a) = XOR_{i in a} s_i."""
        return [self.sqr(1 << i) for i in range(self.n)]

    def apply_linear(self, rows: List[int], a: int) -> int:
        r = 0
        i = 0
        while a:
            if a & 1:
                r ^= rows[i]
            a >>= 1
            i += 1
        return r


# ----------------------------------------------------------------------------- the curve

Point = Optional[Tuple[int, int]]


@dataclass(frozen=True)
class KoblitzCurve:
    F: GF2n
    a: int  # a in {0, 1}; b = 1

    def rhs(self, x: int) -> int:
        F = self.F
        x2 = F.sqr(x)
        return F.mul(x2, x) ^ (x2 if self.a else 0) ^ 1

    def on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        F = self.F
        return F.sqr(y) ^ F.mul(x, y) == self.rhs(x)

    def lift_x(self, x: int) -> List[Tuple[int, int]]:
        """All affine points with abscissa x (0, 1 or 2)."""
        ys = self.F.solve_quadratic(x, self.rhs(x))
        pts = [(x, y) for y in ys]
        for P in pts:
            assert self.on_curve(P)
        return pts

    def is_x_coordinate(self, x: int) -> bool:
        F = self.F
        if x == 0:
            return True  # (0, 1) is the 2-torsion point since b = 1
        return F.trace(F.mul(self.rhs(x), F.inv(F.sqr(x)))) == 0

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 ^ y2) == x1 or x1 == 0:
                return None  # Q == -P, or doubling the 2-torsion point
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.sqr(lam) ^ lam ^ self.a
            y3 = F.sqr(x1) ^ F.mul(lam ^ 1, x3)
        else:
            lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
            x3 = F.sqr(lam) ^ lam ^ x1 ^ x2 ^ self.a
            y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        R = (x3, y3)
        assert self.on_curve(R), "addition left the curve"
        return R

    def sub(self, P: Point, Q: Point) -> Point:
        return self.add(P, self.neg(Q))

    def mul_scalar(self, k: int, P: Point) -> Point:
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def order(self) -> int:
        """#E_a(GF(2^n)) for the Koblitz curve: 2^n + 1 - (alpha^n + beta^n) with
        alpha, beta the roots of T^2 - t T + 2, t = trace of Frobenius over F_2:
        #E_a(F_2) = 4 (a = 0) or 2 (a = 1), so t = 3 - #E_a(F_2) = -1 or 1."""
        t = -1 if self.a == 0 else 1
        # Lucas sequence V_k = alpha^k + beta^k: V_0 = 2, V_1 = t, V_{k+1} = t V_k - 2 V_{k-1}
        n = self.F.n
        v0, v1 = 2, t
        for _ in range(n - 1):
            v0, v1 = v1, t * v1 - 2 * v0
        return (1 << n) + 1 - v1

    def random_point(self, rng) -> Tuple[int, int]:
        while True:
            x = rng.getrandbits(self.F.n)
            pts = self.lift_x(x)
            if pts:
                return pts[rng.randrange(len(pts))]


# ----------------------------------------------------------------------------- summation polynomials

def semaev_s3(F: GF2n, x1: int, x2: int, x3: int, b: int = 1) -> int:
    """S3(x1,x2,x3) = (x1 x2 + x1 x3 + x2 x3)^2 + x1 x2 x3 + b for y^2 + xy = x^3 + a x^2 + b.
    Vanishes iff there are affine points P_i with x(P_i) = x_i and P1 + P2 + P3 = O."""
    e2 = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    return F.sqr(e2) ^ F.mul(F.mul(x1, x2), x3) ^ b


def semaev_s4_from_e(F: GF2n, e1: int, e2: int, e3: int, xr: int) -> int:
    """Fourth summation polynomial S4(x1,x2,x3,xr), b = 1, written in the elementary
    symmetric functions e1, e2, e3 of x1, x2, x3 (the form used by the Trimoska
    generator, SRC-ICPERF-TRIMOSKA-ECICB-2024 Weil_descent.sage):
      Xr^4 + e1^4 + e3^4 + e2^4 Xr^4 + e3^3 Xr + e3 e2^2 Xr^3 + e3 e1^2 Xr + e3 Xr^3
      + e1^2 e3^2 Xr^2 + e3^2 Xr^4 + e3^2 + e2^2 Xr^2.
    It is the Sylvester resultant Res_X(S3(x1,x2,X), S3(x3,xr,X)); see the numeric
    checks in selftest()."""
    m, s = F.mul, F.sqr
    xr2 = s(xr)
    xr3 = m(xr2, xr)
    xr4 = s(xr2)
    e1_2, e2_2, e3_2 = s(e1), s(e2), s(e3)
    e1_4, e2_4, e3_4 = s(e1_2), s(e2_2), s(e3_2)
    e3_3 = m(e3_2, e3)
    r = xr4 ^ e1_4 ^ e3_4 ^ m(e2_4, xr4) ^ m(e3_3, xr) ^ m(m(e3, e2_2), xr3) ^ m(m(e3, e1_2), xr)
    r ^= m(e3, xr3) ^ m(m(e1_2, e3_2), xr2) ^ m(e3_2, xr4) ^ e3_2 ^ m(e2_2, xr2)
    return r


def semaev_s4(F: GF2n, x1: int, x2: int, x3: int, xr: int) -> int:
    e1 = x1 ^ x2 ^ x3
    e2 = F.mul(x1, x2) ^ F.mul(x1, x3) ^ F.mul(x2, x3)
    e3 = F.mul(F.mul(x1, x2), x3)
    return semaev_s4_from_e(F, e1, e2, e3, xr)


def resultant_quadratics(F: GF2n, a: int, b: int, c: int, d: int, e: int, f: int) -> int:
    """Res_X(a X^2 + b X + c, d X^2 + e X + f) over a char-2 field: (af + cd)^2 + (ae + bd)(bf + ce)."""
    m = F.mul
    return F.sqr(m(a, f) ^ m(c, d)) ^ m(m(a, e) ^ m(b, d), m(b, f) ^ m(c, e))


def s3_coeffs_in_x(F: GF2n, x1: int, x2: int, b: int = 1) -> Tuple[int, int, int]:
    """S3(x1, x2, X) = (x1+x2)^2 X^2 + x1 x2 X + (x1 x2)^2 + b as (A, B, C)."""
    p = F.mul(x1, x2)
    return F.sqr(x1 ^ x2), p, F.sqr(p) ^ b


# ----------------------------------------------------------------------------- self-test

def selftest(n: int = 17, trials: int = 200, seed: int = 1) -> dict:
    import random
    rng = random.Random(seed)
    F = GF2n(n, lowest_weight_irreducible(n))
    out = {"n": n, "modulus": F.modulus}
    # field axioms spot checks
    for _ in range(trials):
        a, b, c = (rng.getrandbits(n) for _ in range(3))
        assert F.mul(a, F.mul(b, c)) == F.mul(F.mul(a, b), c)
        assert F.mul(a, b ^ c) == F.mul(a, b) ^ F.mul(a, c)
        if a:
            assert F.mul(a, F.inv(a)) == 1
        assert F.sqr(F.sqrt(a)) == a
        assert F.apply_linear(F.squaring_matrix(), a) == F.sqr(a)
        z2 = F.solve_quadratic(a, b) if a else []
        for z in z2:
            assert F.sqr(z) ^ F.mul(a, z) ^ b == 0
    for a in (0, 1):
        E = KoblitzCurve(F, a)
        N = E.order()
        out[f"order_a{a}"] = N
        # order check: N * P == O for random points, and Hasse bound
        assert abs(N - (1 << n) - 1) <= 2 * (1 << ((n + 1) // 2))
        for _ in range(10):
            P = E.random_point(rng)
            assert E.mul_scalar(N, P) is None
        # S3 vanishes on P1 + P2 + P3 = O and (generically) not otherwise
        zeros = nonzeros = 0
        for _ in range(trials):
            P1, P2 = E.random_point(rng), E.random_point(rng)
            P3 = E.neg(E.add(P1, P2))
            if P3 is None:
                continue
            assert semaev_s3(F, P1[0], P2[0], P3[0]) == 0
            zeros += 1
            Q = E.random_point(rng)
            if semaev_s3(F, P1[0], P2[0], Q[0]) != 0:
                nonzeros += 1
        out[f"s3_zero_checks_a{a}"] = zeros
        out[f"s3_random_nonzero_a{a}"] = nonzeros
        # S4 vanishes on P1 + P2 + P3 + P4 = O and equals the Sylvester resultant
        zeros = agree = 0
        for _ in range(trials):
            P1, P2, P3 = (E.random_point(rng) for _ in range(3))
            P4 = E.neg(E.add(E.add(P1, P2), P3))
            if P4 is None:
                continue
            assert semaev_s4(F, P1[0], P2[0], P3[0], P4[0]) == 0
            zeros += 1
            x1, x2, x3, x4 = (rng.getrandbits(n) for _ in range(4))
            A, B, C = s3_coeffs_in_x(F, x1, x2)
            D, Ee, G = s3_coeffs_in_x(F, x3, x4)
            if resultant_quadratics(F, A, B, C, D, Ee, G) == semaev_s4(F, x1, x2, x3, x4):
                agree += 1
            else:
                raise AssertionError("S4 formula != Sylvester resultant")
        out[f"s4_zero_checks_a{a}"] = zeros
        out[f"s4_resultant_agreements_a{a}"] = agree
        # degenerate identity S4(x, x, z, z) == 0 (formal resultant with both leading coefficients 0)
        for _ in range(20):
            x, z = rng.getrandbits(n), rng.getrandbits(n)
            assert semaev_s4(F, x, x, z, z) == 0
    return out


if __name__ == "__main__":
    import json
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    print(json.dumps(selftest(n), indent=1))
