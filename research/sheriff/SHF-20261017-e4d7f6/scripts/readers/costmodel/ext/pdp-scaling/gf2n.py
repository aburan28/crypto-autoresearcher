"""Arithmetic in F_{2^n} (polynomial basis) and on the binary curve

    E_b : y^2 + x y = x^3 + b        (a2 = 0; b = 1 is the Koblitz curve of ECC2K-130)

Elements of F_{2^n} are Python ints holding the coefficient vector of a
polynomial of degree < n; the modulus is the lexicographically first
irreducible polynomial of degree n with the fewest terms (a trinomial where
one exists, otherwise a pentanomial), found by a Ben-Or irreducibility test.
Speed is not the point of this module: it generates instances and checks
answers.  The solvers do the work.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from functools import cache
from itertools import combinations


def _pmod(a: int, mod: int) -> int:
    """a mod `mod` for polynomials over F_2 held in ints."""
    dm = mod.bit_length() - 1
    while a.bit_length() - 1 >= dm:
        a ^= mod << (a.bit_length() - 1 - dm)
    return a


def _pmulmod(a: int, b: int, mod: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> (mod.bit_length() - 1):
            a ^= mod
    return r


def _pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, _pmod(a, b)
    return a


def is_irreducible(f: int) -> bool:
    """Ben-Or: f of degree n is irreducible iff gcd(f, z^(2^i) - z) = 1 for i <= n/2."""
    n = f.bit_length() - 1
    if n <= 0:
        return False
    z = 2
    for _ in range(n // 2):
        z = _pmulmod(z, z, f)
        if _pgcd(f, z ^ 2) != 1:
            return False
    return True


@cache
def modulus(n: int) -> int:
    """Irreducible polynomial of degree n: a trinomial if one exists, else a pentanomial."""
    for k in range(1, n):
        f = (1 << n) | (1 << k) | 1
        if is_irreducible(f):
            return f
    for a, b, c in combinations(range(1, n), 3):
        f = (1 << n) | (1 << a) | (1 << b) | (1 << c) | 1
        if is_irreducible(f):
            return f
    raise ValueError(f"no irreducible tri/pentanomial of degree {n}")


class GF2n:
    """F_{2^n} in the polynomial basis {1, z, ..., z^(n-1)}."""

    def __init__(self, n: int, mod: int | None = None):
        self.n = n
        self.mod = mod if mod is not None else modulus(n)
        assert self.mod.bit_length() - 1 == n and is_irreducible(self.mod)

    def mul(self, a: int, b: int) -> int:
        return _pmulmod(a, b, self.mod)

    def sqr(self, a: int) -> int:
        return _pmulmod(a, a, self.mod)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.sqr(a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, (1 << self.n) - 2)

    def frob(self, a: int, k: int) -> int:
        """a^(2^k)."""
        for _ in range(k):
            a = self.sqr(a)
        return a

    def trace(self, a: int) -> int:
        t, x = 0, a
        for _ in range(self.n):
            t ^= x
            x = self.sqr(x)
        assert t in (0, 1)
        return t

    def half_trace(self, a: int) -> int:
        """For odd n: z with z^2 + z = a whenever Tr(a) = 0."""
        assert self.n % 2 == 1
        h, x = 0, a
        for _ in range((self.n + 1) // 2):
            h ^= x
            x = self.sqr(self.sqr(x))
        return h

    def sqrt(self, a: int) -> int:
        return self.frob(a, self.n - 1)

    def random(self, rng: random.Random) -> int:
        return rng.getrandbits(self.n)


@dataclass(frozen=True)
class Point:
    x: int
    y: int
    inf: bool = False


INF = Point(0, 0, True)


class Curve:
    """E_b : y^2 + xy = x^3 + b over F_{2^n}."""

    def __init__(self, F: GF2n, b: int):
        self.F = F
        self.b = b

    def on_curve(self, P: Point) -> bool:
        if P.inf:
            return True
        F = self.F
        lhs = F.sqr(P.y) ^ F.mul(P.x, P.y)
        rhs = F.mul(F.sqr(P.x), P.x) ^ self.b
        return lhs == rhs

    def neg(self, P: Point) -> Point:
        return P if P.inf else Point(P.x, P.x ^ P.y)

    def lift_x(self, x: int) -> Point | None:
        """A point with abscissa x, or None if there is none."""
        F = self.F
        if x == 0:
            return Point(0, F.sqrt(self.b))
        # y = x z:  z^2 + z = x + b / x^2
        c = x ^ F.mul(self.b, F.inv(F.sqr(x)))
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        P = Point(x, F.mul(x, z))
        assert self.on_curve(P)
        return P

    def add(self, P: Point, Q: Point) -> Point:
        if P.inf:
            return Q
        if Q.inf:
            return P
        F = self.F
        if P.x == Q.x:
            if P.y != Q.y:
                return INF
            # doubling: lambda = x + y/x
            if P.x == 0:
                return INF
            lam = P.x ^ F.mul(P.y, F.inv(P.x))
            x3 = F.sqr(lam) ^ lam
            y3 = F.sqr(P.x) ^ F.mul(lam ^ 1, x3)
            return Point(x3, y3)
        lam = F.mul(P.y ^ Q.y, F.inv(P.x ^ Q.x))
        x3 = F.sqr(lam) ^ lam ^ P.x ^ Q.x
        y3 = F.mul(lam, P.x ^ x3) ^ x3 ^ P.y
        return Point(x3, y3)

    def sum(self, pts: list[Point]) -> Point:
        R = INF
        for P in pts:
            R = self.add(R, P)
        return R

    def random_point(self, rng: random.Random) -> Point:
        while True:
            P = self.lift_x(self.F.random(rng))
            if P is not None:
                return P if rng.getrandbits(1) else self.neg(P)

    def random_factor_base_point(self, l: int, rng: random.Random) -> Point:
        """A point with x in V = span{1, z, ..., z^(l-1)}."""
        while True:
            P = self.lift_x(rng.getrandbits(l))
            if P is not None:
                return P if rng.getrandbits(1) else self.neg(P)
