"""Bit-packed GF(2)[X] arithmetic.

Convention: a polynomial sum_i c_i X^i is the Python int with bit i equal to c_i.
So X^3 + X + 1  <->  0b1011 = 11.
"""

def deg(a):
    return a.bit_length() - 1          # deg(0) = -1

def clmul(a, b):
    """Carry-less (GF(2)) product, 4-bit windowed."""
    if a == 0 or b == 0:
        return 0
    if a.bit_length() < b.bit_length():
        a, b = b, a
    t = [0] * 16
    t[1] = a
    t[2] = a << 1
    t[4] = a << 2
    t[8] = a << 3
    for i in (3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15):
        low = i & (-i)
        t[i] = t[i ^ low] ^ t[low]
    r = 0
    sh = 0
    while b:
        r ^= t[b & 15] << sh
        b >>= 4
        sh += 4
    return r

def sqr(a):
    """a(X)^2 = a(X^2): spread the bits."""
    if a == 0:
        return 0
    return int('0'.join(bin(a)[2:]), 2)

def polymod(a, m):
    """a mod m, m != 0."""
    dm = m.bit_length() - 1
    da = a.bit_length() - 1
    while da >= dm:
        a ^= m << (da - dm)
        da = a.bit_length() - 1
    return a

def polydivmod(a, m):
    dm = m.bit_length() - 1
    q = 0
    da = a.bit_length() - 1
    while da >= dm:
        q ^= 1 << (da - dm)
        a ^= m << (da - dm)
        da = a.bit_length() - 1
    return q, a

def polygcd(a, b):
    while b:
        a, b = b, polymod(a, b)
    return a

def polyegcd(a, b):
    """returns (g, u, v) with u*a + v*b = g."""
    r0, r1 = a, b
    s0, s1 = 1, 0
    t0, t1 = 0, 1
    while r1:
        q, r = polydivmod(r0, r1)
        r0, r1 = r1, r
        s0, s1 = s1, s0 ^ clmul(q, s1)
        t0, t1 = t1, t0 ^ clmul(q, t1)
    return r0, s0, t0

def mulmod(a, b, m):
    return polymod(clmul(a, b), m)

def sqrmod(a, m):
    return polymod(sqr(a), m)

def compose(f, g):
    """f(g(X)) by Horner."""
    r = 0
    for i in range(f.bit_length() - 1, -1, -1):
        r = clmul(r, g)
        if (f >> i) & 1:
            r ^= 1
    return r

def composemod(f, g, m):
    r = 0
    for i in range(f.bit_length() - 1, -1, -1):
        r = mulmod(r, g, m)
        if (f >> i) & 1:
            r ^= 1
    return polymod(r, m)

def frob_pow_mod(k, m):
    """X^(2^k) mod m."""
    r = polymod(2, m)          # X mod m
    for _ in range(k):
        r = sqrmod(r, m)
    return r

def is_irreducible(f):
    """Rabin's test over GF(2)."""
    n = f.bit_length() - 1
    if n <= 0:
        return False
    if polymod(frob_pow_mod(n, f) ^ 2, f) != 0:      # X^(2^n) == X mod f ?
        return False
    # for every prime p | n, gcd(X^(2^(n/p)) - X, f) must be 1
    pr, nn = set(), n
    d = 2
    while d * d <= nn:
        while nn % d == 0:
            pr.add(d); nn //= d
        d += 1
    if nn > 1:
        pr.add(nn)
    for p in pr:
        if deg(polygcd(frob_pow_mod(n // p, f) ^ 2, f)) != 0:
            return False
    return True

def poly_str(a, var='X'):
    if a == 0:
        return '0'
    terms = []
    for i in range(a.bit_length() - 1, -1, -1):
        if (a >> i) & 1:
            terms.append('1' if i == 0 else (var if i == 1 else f'{var}^{i}'))
    return ' + '.join(terms)
