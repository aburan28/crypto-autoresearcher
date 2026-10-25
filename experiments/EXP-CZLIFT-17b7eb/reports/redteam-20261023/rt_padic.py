"""Red-team independent p-adic instrument for EXP-CZLIFT-17b7eb (TASK-20261023-856638).

Written from the hypothesis statement only; it does not import harness/ or the
producer's implementation.  Short Weierstrass curves y^2 = x^3 + A x + B over
Z/p^K, affine arithmetic for multiples m*P with m < ord(P) (all denominators
are units there), and the chord identity for the final step [n]P = [n-1]P + P,
where [n-1]P == -P mod p:

    mu = (x2 - x1)/(y2 - y1),  s = x1 + x2,
    z(R + P) = (mu - s mu^3) / (1 - (x1 + s) mu^2 + y1 mu^3),   z = -x/y.

z is exact mod p^K because y2 - y1 == 2 y2 is a unit.
"""
from __future__ import annotations

from fractions import Fraction


def vp(a: int, p: int, cap: int) -> int:
    """p-adic valuation of an integer residue mod p^cap, capped at cap."""
    a %= p ** cap
    if a == 0:
        return cap
    v = 0
    while a % p == 0:
        a //= p
        v += 1
    return v


def vp_frac(q: Fraction, p: int) -> float:
    if q == 0:
        return float("inf")
    v = 0
    n, d = q.numerator, q.denominator
    while n % p == 0:
        n //= p
        v += 1
    while d % p == 0:
        d //= p
        v -= 1
    return v


def j_inv(A: int, B: int) -> Fraction:
    return Fraction(1728 * 4 * A ** 3, 4 * A ** 3 + 27 * B ** 2)


# ---------------------------------------------------------------- F_p curve
def fp_points(p: int, A: int, B: int):
    sq = {}
    for y in range(p):
        sq.setdefault(y * y % p, []).append(y)
    pts = []
    for x in range(p):
        for y in sq.get((x ** 3 + A * x + B) % p, []):
            pts.append((x, y))
    return pts


def fp_add(P, Q, p, A):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def fp_mul(n, P, p, A):
    R = None
    Q = P
    while n:
        if n & 1:
            R = fp_add(R, Q, p, A)
        Q = fp_add(Q, Q, p, A)
        n >>= 1
    return R


def cyclic_enumeration(p, A, B, G=None):
    """Return list L with L[k] = kG for k = 0..N-1 (L[0] = None), N = #E(F_p)."""
    pts = fp_points(p, A, B)
    N = len(pts) + 1
    if G is None:
        G = pts[0]
    L = [None, G]
    for _ in range(2, N):
        L.append(fp_add(L[-1], G, p, A))
    return L, N


# ------------------------------------------------------------- Z/p^K curve
class ZpK:
    def __init__(self, p: int, K: int, A: int, B: int):
        self.p, self.K, self.M = p, K, p ** K
        self.A, self.B = A % self.M, B % self.M

    def f(self, x):
        return (x * x * x + self.A * x + self.B) % self.M

    def hensel_y(self, x, y0):
        M = self.M
        y = y0 % self.p
        assert (y * y - self.f(x)) % self.p == 0 and y % self.p != 0
        for _ in range(self.K + 1):
            y = (y - (y * y - self.f(x)) * pow(2 * y, -1, M)) % M
        assert (y * y - self.f(x)) % M == 0
        return y

    def teich(self, x0):
        x0 %= self.p
        if x0 == 0:
            return 0
        return pow(x0, self.p ** (self.K - 1), self.M)

    def lift(self, P, section, eps=0):
        x0, y0 = P
        if section == "naive":
            x = x0
        elif section == "hensel_random":
            x = (x0 + self.p * eps) % self.M
        elif section == "teichmuller":
            x = self.teich(x0)
        else:
            raise ValueError(section)
        return (x, self.hensel_y(x, y0))

    def add(self, P, Q):
        M, p = self.M, self.p
        x1, y1 = P
        x2, y2 = Q
        if P == Q:
            assert y1 % p
            lam = (3 * x1 * x1 + self.A) * pow(2 * y1, -1, M) % M
        else:
            assert (x2 - x1) % p, "non-unit chord"
            lam = (y2 - y1) * pow(x2 - x1, -1, M) % M
        x3 = (lam * lam - x1 - x2) % M
        return (x3, (lam * (x1 - x3) - y1) % M)

    def mul_small(self, n, P):
        """[n]P for 1 <= n < ord(P mod p): left-to-right, all chords unit."""
        bits = bin(n)[3:]
        R = P
        for b in bits:
            R = self.add(R, R)
            if b == "1":
                R = self.add(R, P)
        return R

    def z_mult(self, n, P):
        """z([n]P) mod p^K where n = ord(P mod p) (so [n]P lies in E_1)."""
        M = self.M
        R = self.mul_small(n - 1, P)
        x1, y1 = R
        x2, y2 = P
        assert (x1 - x2) % self.p == 0 and (y1 + y2) % self.p == 0
        mu = (x2 - x1) * pow(y2 - y1, -1, M) % M
        s = x1 + x2
        num = (mu - s * mu ** 3) % M
        den = (1 - (x1 + s) * mu * mu + y1 * mu ** 3) % M
        return num * pow(den, -1, M) % M


def ratio_digit(zP, zQ, p, K):
    """Smart's ratio at the first nonzero digit of z([p]P^).
    Returns (ratio or None, vP, vQ); ratio 0 when vQ > vP; None when vQ < vP or vP >= K."""
    vP, vQ = vp(zP, p, K), vp(zQ, p, K)
    if vP >= K or vQ < vP:
        return None, vP, vQ
    if vQ > vP:
        return 0, vP, vQ
    uP = (zP // p ** vP) % p
    uQ = (zQ // p ** vP) % p
    return uQ * pow(uP, -1, p) % p, vP, vQ


# --------------------------------------------------- exact rational check
def q_add(P, Q, A):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 == -y2:
        return None
    if P == Q:
        lam = (3 * x1 * x1 + A) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - x1 - x2
    return (x3, lam * (x1 - x3) - y1)


def q_mul(n, P, A):
    R = None
    Q = P
    while n:
        if n & 1:
            R = q_add(R, Q, A)
        Q = q_add(Q, Q, A)
        n >>= 1
    return R
