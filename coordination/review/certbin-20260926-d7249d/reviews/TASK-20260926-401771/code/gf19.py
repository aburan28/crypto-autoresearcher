"""F_{2^19} and curve arithmetic for the J1 verifier (TASK-20260926-401771).

Written from EXP-CERTBIN-060020 specification object.field / object.curve and
KN-TECH-b18366 only. Element <-> 19-bit integer, bit j = coefficient of t^j.
Modulus t^19 + t^5 + t^2 + t + 1 (integer 524327).
Curve E: Y^2 + XY = X^3 + A X^2 + B (ordinary, characteristic 2).
Points are (x, y) tuples; the point at infinity is None.
"""

N = 19
MOD = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1  # 524327
ORDER_MASK = (1 << N) - 1


def mul(a, b):
    """Schoolbook carry-less product then reduction modulo MOD."""
    r = 0
    x = a
    while b:
        if b & 1:
            r ^= x
        b >>= 1
        x <<= 1
    # reduce: degree of r <= 36
    for i in range(r.bit_length() - 1, N - 1, -1):
        if (r >> i) & 1:
            r ^= MOD << (i - N)
    return r


def sq(a):
    return mul(a, a)


def power(a, e):
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a):
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_2^19")
    return power(a, (1 << N) - 2)


def trace(a):
    """Tr(a) = sum_{i<19} a^(2^i), returned as 0/1."""
    s = 0
    x = a
    for _ in range(N):
        s ^= x
        x = sq(x)
    if s not in (0, 1):
        raise AssertionError("trace not in F_2")
    return s


def half_trace(c):
    """For odd n: H(c) = sum_{i=0}^{(n-1)/2} c^(2^(2i)); if Tr(c) = 0 then
    z = H(c) solves z^2 + z = c."""
    s = 0
    x = c
    for _ in range((N - 1) // 2 + 1):
        s ^= x
        x = sq(sq(x))
    return s


# ---------------------------------------------------------------- polynomials
def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def pmulmod(a, b, m):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a.bit_length() >= m.bit_length():
            a ^= m
    return pmod(r, m)


def irreducible(f):
    """Rabin-style test for prime degree n: f irreducible iff
    t^(2^n) = t mod f and gcd(t^(2^i) - t, f) = 1 for i = 1..floor(n/2)."""
    n = f.bit_length() - 1
    t = 2
    x = t
    for i in range(1, n + 1):
        x = pmulmod(x, x, f)
        if 1 <= i <= n // 2:
            if pgcd(f, x ^ t) != 1:
                return False
    return x == t


# ---------------------------------------------------------------- curve
class Curve:
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (sq(y) ^ mul(x, y)) == (mul(sq(x), x) ^ mul(self.A, sq(x)) ^ self.B)

    def neg(self, P):
        if P is None:
            return None
        x, y = P
        return (x, x ^ y)

    def add(self, P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):  # Q = -P (includes the 2-torsion point x = 0)
                return None
            return self.double(P)
        lam = mul(y1 ^ y2, inv(x1 ^ x2))
        x3 = sq(lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def double(self, P):
        if P is None:
            return None
        x1, y1 = P
        if x1 == 0:
            return None
        lam = x1 ^ mul(y1, inv(x1))
        x3 = sq(lam) ^ lam ^ self.A
        y3 = sq(x1) ^ mul(lam, x3) ^ x3
        return (x3, y3)

    def mult(self, k, P):
        R = None
        Q = P
        while k:
            if k & 1:
                R = self.add(R, Q)
            Q = self.double(Q)
            k >>= 1
        return R

    def lift_x(self, x):
        """Return a point with abscissa x, or None if x does not lift."""
        if x == 0:
            return (0, power(self.B, 1 << (N - 1)))  # y^2 = B
        c = x ^ self.A ^ mul(self.B, inv(sq(x)))
        if trace(c) != 0:
            return None
        z = half_trace(c)
        y = mul(x, z)
        P = (x, y)
        assert self.on_curve(P)
        return P


def S3(x1, x2, x3, B):
    """KN-TECH-b18366: S_3 = (x1x2 + x1x3 + x2x3)^2 + x1x2x3 + B."""
    s = mul(x1, x2) ^ mul(x1, x3) ^ mul(x2, x3)
    return sq(s) ^ mul(mul(x1, x2), x3) ^ B
