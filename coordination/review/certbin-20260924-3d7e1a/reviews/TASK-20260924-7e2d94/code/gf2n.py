"""F_{2^17} = F_2[t]/(t^17 + t^3 + 1), written from the statement only.

TASK-20260924-7e2d94 (J1, author-independent certificate verifier).
Nothing here is copied from, or shaped by, any producer code.

Encoding (EXP-CERTBIN-4e92d7 object.field): an element is a 17-bit integer,
bit j = coefficient of t^j.

Two implementations of multiplication are provided on purpose:
  * mul()  -- scalar, pure Python, shift-and-add then long division;
  * vmul() -- vectorised numpy over uint64 arrays, bit-serial.
They are cross-checked in the self-tests.
"""
import numpy as np

N = 17
MOD = (1 << 17) | (1 << 3) | 1          # t^17 + t^3 + 1
MASK = (1 << N) - 1
ORDER_MULT = (1 << N) - 1               # |F^*|


# ---------------------------------------------------------------- polynomials over F_2 (as ints)
def pdeg(a):
    return a.bit_length() - 1


def pmod(a, m):
    dm = pdeg(m)
    while a and pdeg(a) >= dm:
        a ^= m << (pdeg(a) - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def clmul(a, b):
    """Carry-less product of two F_2[t] polynomials."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


# ---------------------------------------------------------------- scalar field arithmetic
def reduce(x):
    return pmod(x, MOD)


def add(a, b):
    return a ^ b


def mul(a, b):
    return reduce(clmul(a, b))


def sqr(a):
    return mul(a, a)


def power(a, e):
    r = 1
    base = a
    while e:
        if e & 1:
            r = mul(r, base)
        base = mul(base, base)
        e >>= 1
    return r


def inv(a):
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_2^17")
    return power(a, ORDER_MULT - 1)          # a^(2^17 - 2)


def div(a, b):
    return mul(a, inv(b))


def trace(a):
    """Absolute trace to F_2: sum_{i=0}^{16} a^(2^i)."""
    s = a
    x = a
    for _ in range(N - 1):
        x = sqr(x)
        s ^= x
    return s


def half_trace(c):
    """H(c) = sum_{i=0}^{(n-1)/2} c^(2^(2i)) for odd n; H^2 + H = c + Tr(c)."""
    h = c
    x = c
    for _ in range((N - 1) // 2):
        x = sqr(sqr(x))
        h ^= x
    return h


def modulus_irreducibility_report():
    """Irreducibility of t^17 + t^3 + 1 over F_2 by two criteria.

    (i) gcd(t^(2^i) - t, f) = 1 for i = 1..8 (no factor of degree <= 8, which
        suffices for degree 17), and t^(2^17) = t mod f;
    (ii) Rabin for prime n = 17: t^(2^17) = t mod f and gcd(t^2 - t, f) = 1.
    """
    t = 2
    out = {"gcd_checks": {}, "t_pow_2_17_equals_t": None}
    x = t
    for i in range(1, N + 1):
        x = pmod(clmul(x, x), MOD)           # x = t^(2^i) mod f
        if i <= 8:
            g = pgcd(MOD, x ^ t)
            out["gcd_checks"][str(i)] = g
        if i == N:
            out["t_pow_2_17_equals_t"] = (x == t)
    out["irreducible"] = all(g == 1 for g in out["gcd_checks"].values()) and out["t_pow_2_17_equals_t"]
    return out


# ---------------------------------------------------------------- vectorised field arithmetic
_U = np.uint64


def vmul(a, b):
    """Elementwise product of uint64 arrays (or broadcastable scalars) in F_2^17."""
    a = np.asarray(a, dtype=_U)
    b = np.asarray(b, dtype=_U)
    a, b = np.broadcast_arrays(a, b)
    r = np.zeros(a.shape, dtype=_U)
    one = _U(1)
    for i in range(N):
        bit = (b >> _U(i)) & one
        r ^= (a << _U(i)) * bit
    for i in range(2 * N - 2, N - 1, -1):     # degrees 32 .. 17
        hi = (r >> _U(i)) & one
        r ^= _U(MOD << (i - N)) * hi
    return r
