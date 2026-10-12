"""F_{2^17} = F_2[t]/(t^17 + t^3 + 1), written from the statement only.

Element <-> 17-bit integer, bit j = coefficient of t^j.
Scalar arithmetic on Python ints; vectorized arithmetic on numpy uint64 arrays.
No module of the repository is imported.
"""
import numpy as np

N = 17
MOD = (1 << 17) | (1 << 3) | 1          # t^17 + t^3 + 1
MASK = (1 << N) - 1
ORDER = 1 << N


# ----------------------------------------------------------------------------
# generic polynomial arithmetic over F_2 (ints as bit-polynomials)
# ----------------------------------------------------------------------------
def pdeg(a):
    return a.bit_length() - 1


def pmod(a, m):
    dm = pdeg(m)
    while a and pdeg(a) >= dm:
        a ^= m << (pdeg(a) - dm)
    return a


def pmulmod(a, b, m):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> pdeg(m) & 1:
            a ^= m
    return r


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
    return r


# ----------------------------------------------------------------------------
# field arithmetic
# ----------------------------------------------------------------------------
def add(a, b):
    return a ^ b


def mul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> N:
            a ^= MOD
    return r


def sqr(a):
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
        raise ZeroDivisionError("inverse of 0 in F_2^17")
    return power(a, ORDER - 2)


def div(a, b):
    return mul(a, inv(b))


def trace(c):
    s = 0
    x = c
    for _ in range(N):
        s ^= x
        x = mul(x, x)
    assert s in (0, 1), s
    return s


def half_trace(c):
    """H(c) = sum_{i=0}^{(n-1)/2} c^{4^i}; for Tr(c) = 0, H(c)^2 + H(c) = c."""
    s = 0
    x = c
    for _ in range((N - 1) // 2 + 1):
        s ^= x
        x = mul(x, x)      # x^2
        x = mul(x, x)      # x^4
    return s


def solve_quadratic_z(c):
    """Roots of z^2 + z = c in F_2^17, as a list (0 or 2 roots)."""
    if trace(c) != 0:
        return []
    z = half_trace(c)
    return [z, z ^ 1]


def t_pow(j):
    """t^j reduced mod f."""
    return pmod(1 << j, MOD) if j >= N else (1 << j)


def irreducibility_checks():
    """Returns a dict of checks of f = t^17 + t^3 + 1."""
    out = {}
    t = 2
    # t^{2^17} == t mod f
    x = t
    for _ in range(N):
        x = pmulmod(x, x, MOD)
    out["t_pow_2_17_equals_t"] = (x == t)
    # gcd(t^{2^i} - t, f) == 1 for i = 1..8
    gcds = {}
    x = t
    for i in range(1, 9):
        x = pmulmod(x, x, MOD)
        g = pgcd(MOD, x ^ t)
        gcds[i] = g
    out["gcd_t_2i_minus_t_f_is_1_for_i_1_8"] = all(g == 1 for g in gcds.values())
    # independent brute force: no divisor of degree 1..8
    has_small_factor = False
    for d in range(1, 9):
        for low in range(1 << d):
            p = (1 << d) | low
            if pmod(MOD, p) == 0:
                has_small_factor = True
                break
        if has_small_factor:
            break
    out["no_factor_of_degree_1_to_8_by_trial_division"] = (not has_small_factor)
    out["irreducible"] = all(out.values())
    return out


# ----------------------------------------------------------------------------
# vectorized (numpy uint64 arrays of reduced elements)
# ----------------------------------------------------------------------------
_U1 = np.uint64(1)
_MODU = np.uint64(MOD)


def vmul(a, b):
    a = np.asarray(a, dtype=np.uint64).copy()
    b = np.asarray(b, dtype=np.uint64)
    a, b = np.broadcast_arrays(a, b)
    a = a.copy()
    r = np.zeros(a.shape, dtype=np.uint64)
    for i in range(N):
        bit = (b >> np.uint64(i)) & _U1
        r ^= a * bit
        a = a << _U1
        hi = (a >> np.uint64(N)) & _U1
        a ^= hi * _MODU
    return r


def vsqr(a):
    return vmul(a, a)
