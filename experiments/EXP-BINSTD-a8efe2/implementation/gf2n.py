"""F_2[t]/(f) arithmetic for EXP-BINSTD-a8efe2 (n=9 dual-modulus cell).

Schoolbook multiply + polynomial reduction. Certificate-style re-verify
uses this path only. Adapted from EXP-CERTBIN-e94b27/impl/gf2n.py patterns.
"""
from __future__ import annotations


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> tuple[bool, dict]:
    """Rabin-style irreducibility test over F_2."""
    n = mod.bit_length() - 1
    details: dict = {"n": n, "gcd_checks": []}
    x = 2  # t
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)  # t^{2^i}
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = cur == x
    ok = ok and cur == x
    return ok, details


def poly_to_string(mod: int) -> str:
    n = mod.bit_length() - 1
    terms = []
    for i in range(n, -1, -1):
        if (mod >> i) & 1:
            if i == 0:
                terms.append("1")
            elif i == 1:
                terms.append("x")
            else:
                terms.append(f"x^{i}")
    return " + ".join(terms) if terms else "0"


def weight(mod: int) -> int:
    return bin(mod).count("1")


class Field:
    """Generic schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n
        ok, details = is_irreducible(mod)
        if not ok or details["n"] != n:
            raise ValueError(f"modulus not irreducible of degree {n}: {poly_to_string(mod)}")

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)

    def add(self, a: int, b: int) -> int:
        return a ^ b


# Frozen Stage-0 dual moduli for n=9 (re-verified irreducible).
N = 9
TRINOMIAL_MOD = (1 << 9) | (1 << 1) | 1  # x^9 + x + 1
PENTANOMIAL_MOD = (1 << 9) | (1 << 4) | (1 << 2) | (1 << 1) | 1  # x^9 + x^4 + x^2 + x + 1

MODULI = {
    "trinomial": TRINOMIAL_MOD,
    "pentanomial": PENTANOMIAL_MOD,
}
