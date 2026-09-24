"""Short-Weierstrass curves y^2 = x^3 + a x + b over a prime field F_p."""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field

Point = tuple[int, int] | None  # None is the point at infinity


def is_probable_prime(n: int) -> bool:
    """Deterministic Miller-Rabin for n < 3.3e24, probabilistic beyond."""
    if n < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41)
    for q in small:
        if n % q == 0:
            return n == q
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


def next_prime(n: int) -> int:
    while not is_probable_prime(n):
        n += 1
    return n


def sqrt_mod(n: int, p: int) -> int | None:
    """A square root of n modulo the odd prime p (Tonelli-Shanks), or None."""
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c = i, b * b % p
        t, r = t * c % p, r * b % p
    return r


@dataclass
class OpCounter:
    """Counts charged group operations (additions/doublings)."""

    group_ops: int = 0


@dataclass
class Curve:
    p: int
    a: int
    b: int
    order: int | None = None
    ops: OpCounter = field(default_factory=OpCounter, repr=False, compare=False)

    def __post_init__(self) -> None:
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular curve")

    # -- predicates -------------------------------------------------------
    def rhs(self, x: int) -> int:
        return (x * x * x + self.a * x + self.b) % self.p

    def is_on_curve(self, P: Point) -> bool:
        if P is None:
            return True
        x, y = P
        return (y * y - self.rhs(x)) % self.p == 0

    def lift_x(self, x: int) -> Point:
        """The point with x-coordinate x and the smaller y, or None if absent."""
        y = sqrt_mod(self.rhs(x), self.p)
        if y is None:
            return None
        return (x % self.p, min(y, self.p - y))

    # -- group law --------------------------------------------------------
    def neg(self, P: Point) -> Point:
        return None if P is None else (P[0], (-P[1]) % self.p)

    def add(self, P: Point, Q: Point) -> Point:
        self.ops.group_ops += 1
        if P is None:
            return Q
        if Q is None:
            return P
        p = self.p
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            lam = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, p) % p
        else:
            lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (lam * lam - x1 - x2) % p
        return (x3, (lam * (x1 - x3) - y1) % p)

    def sub(self, P: Point, Q: Point) -> Point:
        return self.add(P, self.neg(Q))

    def mul(self, k: int, P: Point) -> Point:
        if k < 0:
            return self.mul(-k, self.neg(P))
        R: Point = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R

    def random_point(self, rng: random.Random) -> Point:
        while True:
            P = self.lift_x(rng.randrange(self.p))
            if P is not None:
                return P if rng.random() < 0.5 else self.neg(P)

    # -- point counting ---------------------------------------------------
    def point_order_in_hasse(self, P: Point) -> list[int]:
        """Every m in the Hasse interval with mP = O (baby-step giant-step)."""
        p = self.p
        lo = p + 1 - 2 * math.isqrt(p) - 2
        hi = p + 1 + 2 * math.isqrt(p) + 2
        width = hi - lo + 1
        s = math.isqrt(width) + 1
        baby: dict[Point, list[int]] = {}
        R: Point = None
        for j in range(s):
            baby.setdefault(R, []).append(j)
            R = self.add(R, P)
        # mP = O with m = lo + i*s + j  <=>  jP = -(lo + i*s)P.
        step = self.mul(s, P)
        G = self.mul(lo, P)
        hits = []
        for i in range(s + 1):
            for j in baby.get(self.neg(G), []):
                m = lo + i * s + j
                if lo <= m <= hi:
                    hits.append(m)
            G = self.add(G, step)
        return sorted(set(hits))


def _seeded_rng(*labels: object) -> random.Random:
    digest = hashlib.sha256("|".join(map(str, labels)).encode()).digest()
    return random.Random(int.from_bytes(digest, "big"))


def generate_prime_order_curve(bits: int, seed: int = 0) -> tuple[Curve, Point]:
    """A deterministic ordinary curve E/F_p of prime order, with a generator.

    p is a prime of ``bits`` bits.  The order is certified: BSGS finds the
    unique multiple m of a random point P in the Hasse interval, m is prime
    and m > 4 sqrt(p), so m is both ord(P) and #E(F_p).  Curves with a = 0
    or b = 0 (j = 1728 or j = 0) and anomalous curves (#E = p) are rejected.
    """
    if bits < 8:
        raise ValueError("bits must be >= 8")
    rng = _seeded_rng("crypto_autoresearcher.index_calculus.curve", bits, seed)
    p = next_prime(rng.randrange(1 << (bits - 1), 1 << bits) | 1)
    while p.bit_length() != bits:
        p = next_prime(rng.randrange(1 << (bits - 1), 1 << bits) | 1)
    while True:
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * a**3 + 27 * b**2) % p == 0:
            continue
        E = Curve(p, a, b)
        P = E.random_point(rng)
        hits = E.point_order_in_hasse(P)
        if len(hits) != 1:
            continue
        m = hits[0]
        if m == p or m <= 4 * math.isqrt(p) + 4 or not is_probable_prime(m):
            continue
        E.order = m
        E.ops.group_ops = 0
        return E, P
