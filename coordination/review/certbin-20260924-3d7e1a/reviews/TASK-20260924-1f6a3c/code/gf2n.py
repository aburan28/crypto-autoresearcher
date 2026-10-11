"""F_{2^17} = F_2[t]/(t^17 + t^3 + 1), written from EXP-CERTBIN-4e92d7 object.field.

Element <-> 17-bit integer, bit j = coefficient of t^j.
Blind re-derivation TASK-20260924-1f6a3c. Written from the statement only.
"""

N = 17
MOD = (1 << 17) | (1 << 3) | 1
MASK = (1 << N) - 1
ORDER = (1 << N) - 1  # multiplicative group order


def clmul(a, b):
    """Carry-less product of two F_2[t] polynomials (ints)."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m):
    """a mod m in F_2[t]."""
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def mul(a, b):
    return pmod(clmul(a, b), MOD)


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
        raise ZeroDivisionError("inverse of 0")
    return power(a, ORDER - 1)  # a^(2^17 - 2)


def trace(a):
    """Absolute trace to F_2: sum_{i<17} a^(2^i)."""
    s = 0
    x = a
    for _ in range(N):
        s ^= x
        x = sq(x)
    assert s in (0, 1)
    return s


def half_trace(c):
    """H(c) = sum_{i=0}^{(n-1)/2} c^(2^(2i)); for n odd, H(c)^2 + H(c) = c + Tr(c)."""
    s = 0
    x = c
    for i in range((N - 1) // 2 + 1):
        s ^= x
        x = sq(sq(x))
    return s


def sqrt(a):
    """Unique square root: a^(2^(n-1))."""
    x = a
    for _ in range(N - 1):
        x = sq(x)
    return x


def irreducibility_report():
    """Rabin-style check requested by the spec and card:
    gcd(t^(2^i) - t, f) = 1 for i = 1..8, and t^(2^17) = t mod f."""
    t = 2
    res = {"gcd_checks": {}, "frobenius_17_fixes_t": None}
    x = t
    ok = True
    for i in range(1, 18):
        x = pmod(clmul(x, x), MOD)  # t^(2^i) mod f
        if i <= 8:
            g = pgcd(MOD, x ^ t)
            res["gcd_checks"][str(i)] = g
            if g != 1:
                ok = False
        if i == 17:
            res["frobenius_17_fixes_t"] = (x == t)
            ok = ok and (x == t)
    res["irreducible"] = ok
    return res
