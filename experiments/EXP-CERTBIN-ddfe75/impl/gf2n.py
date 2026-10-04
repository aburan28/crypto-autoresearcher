"""Own F_{2^17} = F_2[t]/(t^17 + t^3 + 1) arithmetic (element = 17-bit int,
bit j = coefficient of t^j). Written for EXP-CERTBIN-ddfe75; nothing copied."""
from __future__ import annotations

N = 17
MOD = (1 << 17) | (1 << 3) | 1
MASK = (1 << N) - 1


def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a, m=MOD):
    dm = m.bit_length()
    while a.bit_length() >= dm:
        a ^= m << (a.bit_length() - dm)
    return a


def mul(a, b):
    return pmod(clmul(a, b))


def sq(a):
    return mul(a, a)


def pw(a, e):
    r = 1
    while e:
        if e & 1:
            r = mul(r, a)
        a = mul(a, a)
        e >>= 1
    return r


def inv(a):
    if a == 0:
        raise ZeroDivisionError("inverse of 0 in F_{2^17}")
    return pw(a, (1 << N) - 2)


def trace(a):
    s, x = 0, a
    for _ in range(N):
        s ^= x
        x = sq(x)
    assert s in (0, 1), s
    return s


def tpow(j):
    return pmod(1 << j)


def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a


def irreducible_check():
    """gcd(t^{2^i} - t, f) = 1 for i = 1..8 and t^{2^17} = t mod f."""
    t = 2
    x = t
    out = {"gcd_ok": [], "frob17_is_t": None}
    for i in range(1, N + 1):
        x = mul(x, x)  # t^{2^i}
        if i <= 8:
            out["gcd_ok"].append(pgcd(MOD, x ^ t) == 1)
    out["frob17_is_t"] = (x == t)
    out["irreducible"] = all(out["gcd_ok"]) and out["frob17_is_t"]
    return out
