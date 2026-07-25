#!/usr/bin/env python3
"""
Lab 03 — Elliptic curves and the group law.

Companion to course modules 06-07. Run directly:

    python3 lab03_elliptic_curves.py

Implements short-Weierstrass curves  y^2 = x^3 + a x + b  over any field
whose elements follow the lab-02 interface (Fp or Fp2), with:

  * the chord-and-tangent group law,
  * double-and-add scalar multiplication,
  * brute-force point counting (small fields) + Hasse-bound check,
  * point order via the factored group order,
  * j-invariants and quadratic twists.

The point at infinity O is represented as Point(curve, None, None,
infinity=True); every finite point stores field elements x, y.
"""

from __future__ import annotations

import random

from lab01_arithmetic import factorize, legendre
from lab02_finite_fields import Fp, Fp2


class EllipticCurve:
    """y^2 = x^3 + a*x + b over the field of its coefficients (char > 3)."""

    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.field_one = a.one()
        if self.discriminant().is_zero():
            raise ValueError("singular curve: 4a^3 + 27b^2 = 0")

    def discriminant(self):
        """Delta = -16 (4 a^3 + 27 b^2); nonzero iff the cubic has three
        distinct roots iff the curve is smooth."""
        return (self.a ** 3 * 4 + self.b ** 2 * 27) * (-16)

    def j_invariant(self):
        """j = 1728 * 4a^3 / (4a^3 + 27b^2). Classifies the curve up to
        isomorphism over the algebraic closure."""
        four_a3 = self.a ** 3 * 4
        return four_a3 * 1728 / (four_a3 + self.b ** 2 * 27)

    def contains(self, P: "Point") -> bool:
        if P.inf:
            return True
        return P.y * P.y == P.x ** 3 + self.a * P.x + self.b

    def zero(self) -> "Point":
        return Point(self, None, None, infinity=True)

    def point(self, x, y) -> "Point":
        P = Point(self, x, y)
        if not self.contains(P):
            raise ValueError(f"({x}, {y}) is not on {self}")
        return P

    def lift_x(self, x) -> "Point | None":
        """A point with the given x-coordinate, if one exists."""
        rhs = x ** 3 + self.a * x + self.b
        y = rhs.sqrt()
        return None if y is None else Point(self, x, y)

    def random_point(self, rng: random.Random) -> "Point":
        while True:
            P = self.lift_x(self.a.random(rng))
            if P is not None:
                return P

    def quadratic_twist(self, d):
        """The twist y^2 = x^3 + a d^2 x + b d^3 for a non-square d.
        Over F_q: #E + #E^d = 2q + 2."""
        return EllipticCurve(self.a * d * d, self.b * d ** 3)

    def __eq__(self, other):
        return isinstance(other, EllipticCurve) and \
            self.a == other.a and self.b == other.b

    def __repr__(self):
        return f"E: y^2 = x^3 + ({self.a})*x + ({self.b})"


class Point:
    """A point on an EllipticCurve; the group operation is +."""

    __slots__ = ("curve", "x", "y", "inf")

    def __init__(self, curve, x, y, infinity: bool = False):
        self.curve = curve
        self.x = x
        self.y = y
        self.inf = infinity

    def is_zero(self) -> bool:
        return self.inf

    def __neg__(self) -> "Point":
        if self.inf:
            return self
        return Point(self.curve, self.x, -self.y)

    def __add__(self, Q: "Point") -> "Point":
        P = self
        if P.inf:
            return Q
        if Q.inf:
            return P
        if P.x == Q.x:
            if P.y == -Q.y:           # includes the y = 0 (2-torsion) case
                return self.curve.zero()
            # tangent line: lambda = (3 x^2 + a) / (2 y)
            lam = (P.x * P.x * 3 + self.curve.a) / (P.y * 2)
        else:
            # chord: lambda = (y2 - y1) / (x2 - x1)
            lam = (Q.y - P.y) / (Q.x - P.x)
        x3 = lam * lam - P.x - Q.x
        y3 = lam * (P.x - x3) - P.y
        return Point(self.curve, x3, y3)

    def __sub__(self, Q: "Point") -> "Point":
        return self + (-Q)

    def __rmul__(self, n: int) -> "Point":
        """Double-and-add: the elliptic-curve analogue of fast_pow."""
        if n < 0:
            return (-n) * (-self)
        result = self.curve.zero()
        addend = self
        while n:
            if n & 1:
                result = result + addend
            addend = addend + addend
            n >>= 1
        return result

    __mul__ = None  # use n * P, matching the additive notation of the course

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        if self.inf or other.inf:
            return self.inf and other.inf
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        if self.inf:
            return hash(("Point", "inf"))
        return hash(("Point", self.x, self.y))

    def __repr__(self):
        return "O" if self.inf else f"({self.x}, {self.y})"


# ----------------------------------------------------------------------
# Counting and orders (small fields only — this is the naive baseline
# that Schoof's algorithm, module 07, exists to beat)
# ----------------------------------------------------------------------

def count_points_Fp(curve: EllipticCurve) -> int:
    """#E(F_p) = 1 + sum_x (1 + legendre(x^3+ax+b, p)). O(p) time."""
    p = curve.a.p
    a, b = curve.a.v, curve.b.v
    total = 1  # the point at infinity
    for x in range(p):
        total += 1 + legendre(x * x % p * x + a * x + b, p)
    return total


def count_points_Fp2(curve: EllipticCurve) -> int:
    """#E(F_{p^2}) by brute force over all p^2 x-coordinates. O(p^2)
    Euler-criterion tests — only for classroom-sized p."""
    p = curve.a.p
    total = 1
    exp = (p * p - 1) // 2
    for xa in range(p):
        for xb in range(p):
            x = Fp2(p, xa, xb, curve.a.ns)
            rhs = x ** 3 + curve.a * x + curve.b
            if rhs.is_zero():
                total += 1
            elif rhs ** exp == curve.field_one:
                total += 2
    return total


def point_order(P: Point, group_order: int) -> int:
    """Exact order of P given a multiple of it (the group order):
    strip prime factors while the point stays at O."""
    if P.inf:
        return 1
    order = group_order
    for q in factorize(group_order):
        while order % q == 0 and (order // q * P).is_zero():
            order //= q
    return order


def group_structure(curve: EllipticCurve, n: int, rng: random.Random,
                    tries: int = 60) -> tuple[int, int]:
    """Heuristic (n1, n2) with E = Z/n1 x Z/n2, n1 | n2, n1*n2 = n:
    n2 = exponent, estimated as the lcm of many random point orders."""
    from math import gcd
    n2 = 1
    for _ in range(tries):
        o = point_order(curve.random_point(rng), n)
        n2 = n2 * o // gcd(n2, o)
    return n // n2, n2


# ----------------------------------------------------------------------
# Self-checks and demo
# ----------------------------------------------------------------------

def _selfcheck() -> None:
    from math import isqrt
    rng = random.Random(3)

    # Group axioms, subtraction, scalar arithmetic over F_p and F_{p^2}.
    for one in (Fp(431, 1), Fp2(101, 1)):
        E = EllipticCurve(one, one)           # y^2 = x^3 + x + 1
        O = E.zero()
        for _ in range(40):
            P, Q, R = (E.random_point(rng) for _ in range(3))
            assert E.contains(P + Q) and E.contains(2 * P)
            assert (P + Q) + R == P + (Q + R)      # associativity (spot check)
            assert P + Q == Q + P                  # commutativity
            assert P + O == P and (P - P).is_zero()
            assert 5 * P == P + P + P + P + P
            assert (3 * P) + (4 * P) == 7 * P

    # Hasse bound and Lagrange over several small prime fields.
    for p in (11, 61, 101, 431):
        E = EllipticCurve(Fp(p, 1), Fp(p, 1))
        n = count_points_Fp(E)
        assert abs(n - (p + 1)) <= 2 * isqrt(p) + 1, (p, n)
        for _ in range(20):
            P = E.random_point(rng)
            assert (n * P).is_zero()               # Lagrange's theorem
            o = point_order(P, n)
            assert n % o == 0 and (o * P).is_zero()
            assert not any((k * P).is_zero() for k in range(1, min(o, 50)))

    # Twist identity #E + #E^d = 2p + 2.
    p = 61
    E = EllipticCurve(Fp(p, 1), Fp(p, 1))
    d = Fp(p, 2)
    while d.is_square():
        d = d + 1
    assert count_points_Fp(E) + count_points_Fp(E.quadratic_twist(d)) == 2 * p + 2
    # Twists share the j-invariant without being isomorphic over F_p.
    assert E.j_invariant() == E.quadratic_twist(d).j_invariant()

    # F_{p^2} count for a supersingular curve: p = 3 mod 4 makes
    # y^2 = x^3 + x supersingular with #E(F_{p^2}) = (p+1)^2.
    p = 23
    E = EllipticCurve(Fp2(p, 1), Fp2(p, 0))
    assert count_points_Fp2(E) == (p + 1) ** 2

    # Same supersingular curve over F_p itself: #E(F_p) = p + 1 (trace 0).
    assert count_points_Fp(EllipticCurve(Fp(23, 1), Fp(23, 0))) == 24

    print("lab03: all self-checks passed")


def _demo() -> None:
    rng = random.Random(4)
    p = 61
    E = EllipticCurve(Fp(p, 1), Fp(p, 1))
    n = count_points_Fp(E)
    print(f"\n-- demo: {E} over F_{p} --")
    print(f"#E(F_{p}) = {n}   (Hasse interval: "
          f"[{p + 1 - 2 * int(p ** 0.5)}, {p + 1 + 2 * int(p ** 0.5)}])")
    print(f"j(E) = {E.j_invariant()}")
    n1, n2 = group_structure(E, n, rng)
    print(f"group structure: Z/{n1} x Z/{n2}")
    P = E.random_point(rng)
    print(f"random point P = {P}, order {point_order(P, n)}")
    print("first multiples:", ", ".join(repr(k * P) for k in range(1, 6)))
    Q = E.random_point(rng)
    print(f"Q = {Q},  P + Q = {P + Q},  2P = {2 * P}")
    # EXERCISE 3.1: tabulate #E(F_p) for y^2 = x^3 + x over all primes
    #   p = 3 mod 4 below 200 and observe #E = p + 1 (supersingular!).
    # EXERCISE 3.2: find a curve/prime pair whose group is NOT cyclic
    #   (n1 > 1) and verify n1 | gcd(n2, p - 1).
    # EXERCISE 3.3: implement affine "windowed" scalar multiplication and
    #   count field multiplications vs plain double-and-add.


if __name__ == "__main__":
    _selfcheck()
    _demo()
