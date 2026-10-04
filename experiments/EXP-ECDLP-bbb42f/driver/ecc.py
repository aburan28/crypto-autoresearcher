"""
Prime-field short-Weierstrass elliptic curve arithmetic, affine coordinates,
with instrumented field-operation counters used by cost_model.py to derive
the group-operation-equivalent charging convention. No external EC library
is used; every operation below is elementary modular arithmetic.

Curve: y^2 = x^3 + a*x + b  (mod p), p > 3 prime.
Point at infinity represented as None.
"""
from __future__ import annotations
import random


def seeded_rng(*parts) -> random.Random:
    """Deterministic random.Random from an arbitrary tuple of seed
    components (random.Random only natively accepts int/float/str/bytes)."""
    return random.Random(repr(parts))


class OpCounter:
    """Global-ish counter injected into arithmetic calls; one instance per
    logical unit of work (a run, a solve attempt, an isogeny step) so costs
    are attributable. field_mults and field_invs are counted separately
    because inversion cost is charged via a stated modeled I/M ratio in
    cost_model.py, never silently folded into a multiplication count."""

    __slots__ = ("field_mults", "field_invs", "field_adds")

    def __init__(self):
        self.field_mults = 0
        self.field_invs = 0
        self.field_adds = 0

    def add(self, other: "OpCounter"):
        self.field_mults += other.field_mults
        self.field_invs += other.field_invs
        self.field_adds += other.field_adds

    def to_dict(self):
        return {
            "field_mults": self.field_mults,
            "field_invs": self.field_invs,
            "field_adds": self.field_adds,
        }


def inv_mod(x: int, p: int, ctr: OpCounter = None) -> int:
    if x % p == 0:
        raise ZeroDivisionError("inverse of 0 mod p")
    if ctr is not None:
        ctr.field_invs += 1
    return pow(x, -1, p)


def is_infinity(P) -> bool:
    return P is None


def on_curve(P, a: int, b: int, p: int) -> bool:
    if P is None:
        return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0


def point_add(P, Q, a: int, p: int, ctr: OpCounter = None):
    if ctr is None:
        ctr = OpCounter()
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 % p == 0:
            return None
        num = (3 * x1 * x1 + a) % p
        den = (2 * y1) % p
        ctr.field_mults += 2  # 3*x1*x1 counted as 2 mults (x1*x1, *3 is a scalar add-chain; charge conservatively as 1 mult)
        lam = (num * inv_mod(den, p, ctr)) % p
        ctr.field_mults += 1
    else:
        num = (y2 - y1) % p
        den = (x2 - x1) % p
        lam = (num * inv_mod(den, p, ctr)) % p
        ctr.field_mults += 1
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    ctr.field_mults += 2
    ctr.field_adds += 4
    return (x3, y3)


def point_neg(P, p: int):
    if P is None:
        return None
    x, y = P
    return (x, (-y) % p)


def scalar_mult(k: int, P, a: int, p: int, ctr: OpCounter = None):
    if ctr is None:
        ctr = OpCounter()
    if k < 0:
        return scalar_mult(-k, point_neg(P, p), a, p, ctr)
    R = None
    base = P
    k = k % (p * 2 + 2) if False else k  # no-op, keep k as given (caller reduces mod N when relevant)
    while k > 0:
        if k & 1:
            R = point_add(R, base, a, p, ctr)
        base = point_add(base, base, a, p, ctr)
        k >>= 1
    return R


def random_point(a: int, b: int, p: int, rng: random.Random):
    """Deterministic (seeded via rng) search for a point on the curve by
    trying x-coordinates in a seeded order until x^3+ax+b is a QR mod p."""
    for _ in range(10000):
        x = rng.randrange(0, p)
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            return (x, 0)
        y = tonelli_shanks(rhs, p)
        if y is not None:
            return (x, y)
    raise RuntimeError("failed to find a curve point after 10000 tries")


def legendre_symbol(a: int, p: int) -> int:
    a = a % p
    if a == 0:
        return 0
    ls = pow(a, (p - 1) // 2, p)
    return -1 if ls == p - 1 else ls


def tonelli_shanks(n: int, p: int):
    n = n % p
    if n == 0:
        return 0
    if legendre_symbol(n, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while legendre_symbol(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        t2i = t
        i = 0
        for i in range(1, m):
            t2i = (t2i * t2i) % p
            if t2i == 1:
                break
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r
