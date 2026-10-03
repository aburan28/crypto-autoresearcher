"""Binary-field arithmetic for EXP-BINSTD-1a7892 Stage 2 toys.

Adapted from experiments/EXP-CERTBIN-e94b27/impl/gf2n.py (schoolbook path).
Elements of F_2[t]/(f) are Python ints; bit j is the coefficient of t^j.
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


def is_irreducible(mod: int):
    n = mod.bit_length() - 1
    details = {"n": n, "gcd_checks": []}
    x = 2
    cur = x
    ok = True
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2:
            g = pgcd(mod, cur ^ x)
            details["gcd_checks"].append({"i": i, "gcd": g})
            if g != 1:
                ok = False
    details["t_pow_2n_equals_t"] = cur == x
    return ok and cur == x, details


# Known irreducible polynomials for toy degrees used here.
IRRED = {
    4: (1 << 4) | (1 << 1) | 1,  # t^4 + t + 1
    5: (1 << 5) | (1 << 2) | 1,  # t^5 + t^2 + 1
    7: (1 << 7) | (1 << 1) | 1,  # t^7 + t + 1
    8: (1 << 8) | (1 << 4) | (1 << 3) | (1 << 1) | 1,
    9: (1 << 9) | (1 << 1) | 1,
    12: (1 << 12) | (1 << 3) | 1,
    20: (1 << 20) | (1 << 3) | 1,
    28: (1 << 28) | (1 << 1) | 1,  # may need validation
    36: (1 << 36) | (1 << 1) | 1,
}


class Field:
    """Generic schoolbook F_{2^n}."""

    def __init__(self, n: int, mod: int | None = None):
        self.n = n
        self.mod = mod if mod is not None else IRRED[n]
        self.q = 1 << n
        ok, _ = is_irreducible(self.mod)
        if not ok:
            raise ValueError(f"modulus not irreducible for n={n}: {self.mod:#x}")

    def mul_school(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    mul = mul_school

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

    def div(self, a: int, b: int) -> int:
        return self.mul(a, self.inv(b))

    def trace(self, a: int) -> int:
        # Absolute trace Tr_{F_{2^n}/F_2}(a) = a + a^2 + ... + a^{2^{n-1}}.
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.mul(x, x)
        return s & 1

    def half_trace(self, a: int) -> int:
        assert self.n % 2 == 1
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x = self.sqr(self.sqr(x))
        return s

    def sqrt(self, a: int) -> int:
        x = a
        for _ in range(self.n - 1):
            x = self.mul(x, x)
        return x
