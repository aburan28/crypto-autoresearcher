"""F_{2^17} = F_2[t]/(t^17 + t^3 + 1), written for TASK-20260926-f0e5a4 (J1).

Element <-> 17-bit integer, bit j = coefficient of t^j
(EXP-CERTBIN-4e92d7 object.field). Scalar (Python int) and vectorized
(numpy int64 arrays) arithmetic. Imports nothing from this repository.
"""
import numpy as np

N = 17
MOD = (1 << 17) | (1 << 3) | 1
MASK = (1 << N) - 1


def clmul(a, b):
    """Carry-less product of two polynomials over F_2 (ints)."""
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def reduce(r):
    """r mod MOD over F_2."""
    while r.bit_length() > N:
        d = r.bit_length() - 1
        r ^= MOD << (d - N)
    return r


def mul(a, b):
    return reduce(clmul(a, b))


def sq(a):
    return mul(a, a)


def power(a, e):
    r = 1
    x = a
    while e:
        if e & 1:
            r = mul(r, x)
        x = mul(x, x)
        e >>= 1
    return r


def inv(a):
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_2^17")
    return power(a, (1 << N) - 2)


def div(a, b):
    return mul(a, inv(b))


def trace(a):
    """Absolute trace Tr(a) = sum_{i<17} a^(2^i); returns 0 or 1."""
    t = 0
    x = a
    for _ in range(N):
        t ^= x
        x = sq(x)
    if t not in (0, 1):
        raise ArithmeticError("trace not in F_2: modulus or arithmetic wrong")
    return t


def half_trace(c):
    """H(c) = sum_{i=0}^{(n-1)/2} c^(2^(2i)); for n odd, H^2 + H = c + Tr(c)."""
    h = 0
    x = c
    for _ in range((N - 1) // 2 + 1):
        h ^= x
        x = sq(sq(x))
    return h


def sqrt(a):
    return power(a, 1 << (N - 1))


# ---- polynomial helpers over F_2 (for the irreducibility test) ----

def pmod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def irreducibility_test():
    """f of prime degree 17 is irreducible iff t^(2^17) = t mod f and f has no
    factor of degree < 17; the spec's test: gcd(t^(2^i) - t, f) = 1 for
    i = 1..8 and t^(2^17) = t mod f."""
    out = {"gcd_ones": {}, "t_pow_2_17_eq_t": None}
    x = 2  # t
    pows = {}
    for i in range(1, N + 1):
        x = sq(x)
        pows[i] = x
    for i in range(1, 9):
        out["gcd_ones"][i] = pgcd(MOD, pows[i] ^ 2) == 1
    out["t_pow_2_17_eq_t"] = pows[N] == 2
    out["pass"] = all(out["gcd_ones"].values()) and out["t_pow_2_17_eq_t"]
    return out


def field_axioms_test(rng, n_triples=10000):
    fails = 0
    for _ in range(n_triples):
        a = rng.randrange(1 << N)
        b = rng.randrange(1 << N)
        c = rng.randrange(1 << N)
        if mul(a, b) != mul(b, a):
            fails += 1
        if mul(mul(a, b), c) != mul(a, mul(b, c)):
            fails += 1
        if mul(a, b ^ c) != mul(a, b) ^ mul(a, c):
            fails += 1
        if a and mul(a, inv(a)) != 1:
            fails += 1
        if mul(a, 1) != a:
            fails += 1
        if sq(sqrt(a)) != a:
            fails += 1
        if trace(a ^ b) != trace(a) ^ trace(b):
            fails += 1
        hc = half_trace(a)
        if sq(hc) ^ hc != a ^ trace(a):
            fails += 1
    return {"triples": n_triples, "failures": fails, "pass": fails == 0}


# ---- vectorized (numpy int64) ----

def vmul(a, b):
    a = np.asarray(a, dtype=np.int64)
    b = np.asarray(b, dtype=np.int64)
    shape = np.broadcast(a, b).shape
    r = np.zeros(shape, dtype=np.int64)
    for i in range(N):
        r ^= ((b >> i) & 1) * (a << i)
    for d in range(2 * N - 2, N - 1, -1):
        r ^= ((r >> d) & 1) * (MOD << (d - N))
    return r


def vsq(a):
    return vmul(a, a)
