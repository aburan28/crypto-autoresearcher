"""Schoolbook F_{2^n} for EXP-SATIC-ba99a8. Integers; bit j is t^j.

No Sage/Magma/numpy. Two multiply orders live in s3_eval.py, not here.
Amazon Bedrock is not selected.
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


class Field:
    def __init__(self, n: int, mod: int) -> None:
        if n < 1 or mod.bit_length() - 1 != n:
            raise ValueError("modulus degree must equal n")
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.sqr(a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError
        return self.pow(a, self.q - 2)

    def sqrt(self, a: int) -> int:
        x = a
        for _ in range(self.n - 1):
            x = self.sqr(x)
        return x

    def trace(self, a: int) -> int:
        s = 0
        x = a
        for _ in range(self.n):
            s ^= x
            x = self.sqr(x)
        if s not in (0, 1):
            raise RuntimeError("trace not in F2")
        return s

    def half_trace(self, a: int) -> int:
        if self.n % 2 == 0:
            raise ValueError("half-trace requires odd n")
        s = 0
        x = a
        for _ in range((self.n - 1) // 2 + 1):
            s ^= x
            x = self.sqr(self.sqr(x))
        return s
