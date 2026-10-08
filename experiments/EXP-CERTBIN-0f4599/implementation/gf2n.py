"""Schoolbook F_{2^n} arithmetic for EXP-CERTBIN-0f4599.

Elements are Python ints; bit j is the coefficient of t^j.
Two multiply paths (schoolbook vs expand-and-reduce) are cross-checked
in the Stage-0 self-test. No numpy. No Magma/Sage/AUXIN/Bedrock.
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
    n = mod.bit_length() - 1
    details: dict = {"n": n, "gcd_checks": []}
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


class Field:
    def __init__(self, n: int, mod: int) -> None:
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul_school(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def mul_expand(self, a: int, b: int) -> int:
        r = 0
        aa = a
        bb = b
        while bb:
            if bb & 1:
                r ^= aa
            aa <<= 1
            if aa >> self.n:
                aa ^= self.mod
            bb >>= 1
        return pmod(r, self.mod)

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

    def trace(self, a: int) -> int:
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
