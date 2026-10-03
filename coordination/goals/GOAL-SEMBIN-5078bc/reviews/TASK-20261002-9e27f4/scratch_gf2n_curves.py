"""SCRATCH (TASK-20261002-9e27f4, validator). Not a run record, not a measurement.

Minimal F_{2^n} and binary-curve arithmetic used only to test STATEMENTS of
TASK-20261001-9b3e70's drafts on hand-sized toy curves. Standard library only.
No N_2 or decomposition-count statistic of any F_V is computed anywhere in this
directory (card constraint: that is the V1 contract's job).

Curve: y^2 + x y = x^3 + a x^2 + b over F_{2^n}; points are (x, y) ints or None (O).
"""
import random


def find_irreducible(n):
    """Smallest-weight irreducible x^n + x^k + 1 (trinomial) or pentanomial."""
    def is_irred(f):
        # Rabin-style test via x^(2^n) == x mod f and gcd checks (n prime here).
        return _x_pow_2k_mod(f, n) == 2 and all(
            _gcd(_x_pow_2k_mod(f, n // q) ^ 2, f) == 1 for q in _prime_factors(n))
    for k in range(1, n):
        f = (1 << n) | (1 << k) | 1
        if is_irred(f):
            return f
    for k1 in range(1, n):
        for k2 in range(1, k1):
            for k3 in range(1, k2):
                f = (1 << n) | (1 << k1) | (1 << k2) | (1 << k3) | 1
                if is_irred(f):
                    return f
    raise ValueError(n)


def _prime_factors(n):
    out, d = [], 2
    while d * d <= n:
        if n % d == 0:
            out.append(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        out.append(n)
    return out


def _deg(a):
    return a.bit_length() - 1


def _mulmod_raw(a, b, f):
    n = _deg(f)
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if (a >> n) & 1:
            a ^= f
    return r


def _x_pow_2k_mod(f, k):
    a = 2  # the polynomial x
    for _ in range(k):
        a = _mulmod_raw(a, a, f)
    return a


def _gcd(a, b):
    while b:
        while a and _deg(a) >= _deg(b):
            a ^= b << (_deg(a) - _deg(b))
        a, b = b, a
    return a


class GF2n:
    def __init__(self, n, poly=None):
        self.n = n
        self.f = poly or find_irreducible(n)

    def mul(self, a, b):
        return _mulmod_raw(a, b, self.f)

    def sq(self, a):
        return self.mul(a, a)

    def inv(self, a):
        assert a
        # a^(2^n - 2)
        r, e, base = 1, (1 << self.n) - 2, a
        while e:
            if e & 1:
                r = self.mul(r, base)
            base = self.sq(base)
            e >>= 1
        return r

    def tr(self, a):
        t, s = 0, a
        for _ in range(self.n):
            t ^= s
            s = self.sq(s)
        assert t in (0, 1)
        return t

    def halftrace(self, c):
        """For odd n: z with z^2 + z = c + Tr(c)."""
        assert self.n % 2 == 1
        z, s = 0, c
        for i in range(self.n):
            if i % 2 == 0:
                z ^= s
            s = self.sq(s)
        return z


class BinCurve:
    def __init__(self, F, a, b):
        self.F, self.a, self.b = F, a, b

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
            if y1 ^ y2 == x2:  # Q == -P
                return None
            if y1 == y2:
                return self.dbl(P)
        lam = F.mul(y1 ^ y2, F.inv(x1 ^ x2))
        x3 = F.sq(lam) ^ lam ^ x1 ^ x2 ^ self.a
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def dbl(self, P):
        F = self.F
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ F.mul(y1, F.inv(x1))
        x3 = F.sq(lam) ^ lam ^ self.a
        y3 = F.sq(x1) ^ F.mul(lam ^ 1, x3)
        return (x3, y3)

    def mul(self, k, P):
        R, Q = None, P
        if k < 0:
            k, Q = -k, self.neg(P)
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.dbl(Q)
            k >>= 1
        return R

    def frob(self, P):
        if P is None:
            return None
        return (self.F.sq(P[0]), self.F.sq(P[1]))

    def on_curve(self, P):
        if P is None:
            return True
        F = self.F
        x, y = P
        return F.sq(y) ^ F.mul(x, y) == F.mul(F.sq(x), x) ^ F.mul(self.a, F.sq(x)) ^ self.b

    def random_point(self, rng):
        F = self.F
        while True:
            x = rng.randrange(1, 1 << F.n)
            c = x ^ self.a ^ F.mul(self.b, F.inv(F.sq(x)))
            if F.tr(c) == 0:
                z = F.halftrace(c)
                P = (x, F.mul(x, z))
                assert self.on_curve(P)
                return P if rng.random() < 0.5 else self.neg(P)


def is_probable_prime(n):
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
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


def koblitz_order(n, a):
    """#E_a(F_{2^n}) for y^2+xy=x^3+a x^2+1 via Lucas: t1 = 1 if a==1 else -1."""
    t = 1 if a == 1 else -1
    V0, V1 = 2, t
    for _ in range(n - 1):
        V0, V1 = V1, t * V1 - 2 * V0
    return (1 << n) + 1 - V1, t


def sqrt_mod(a, p):
    """Tonelli-Shanks."""
    a %= p
    if a == 0:
        return 0
    assert pow(a, (p - 1) // 2, p) == 1
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, r = s, pow(z, q, p), pow(a, q, p), pow(a, (q + 1) // 2, p)
    while t != 1:
        i, tt = 0, t
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    return r
