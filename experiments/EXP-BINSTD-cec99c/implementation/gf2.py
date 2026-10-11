#!/usr/bin/env python3
"""Schoolbook F_2[t]/(f) for EXP-BINSTD-cec99c. Stdlib only. No numpy."""
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


def is_irreducible(mod: int) -> bool:
    n = mod.bit_length() - 1
    x = 2
    cur = x
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2 and pgcd(mod, cur ^ x) != 1:
            return False
    return cur == x


class Field:
    def __init__(self, modulus: int):
        if not is_irreducible(modulus):
            raise ValueError(f"modulus not irreducible: {modulus:#x}")
        self.mod = modulus
        self.n = modulus.bit_length() - 1
        self.q = 1 << self.n

    def mul(self, a: int, b: int) -> int:
        mask = self.q - 1
        return pmod(clmul(a & mask, b & mask), self.mod)

    def square(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        a &= self.q - 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("invert 0")
        return self.pow(a, self.q - 2)

    def sqrt(self, a: int) -> int:
        return self.pow(a, 1 << (self.n - 1))

    def trace(self, a: int) -> int:
        s = 0
        x = a & (self.q - 1)
        for _ in range(self.n):
            s ^= x & 1
            x = self.square(x)
        return s & 1

    def half_trace(self, a: int) -> int:
        if self.n % 2 == 0:
            raise NotImplementedError("half-trace for even n not used")
        z = 0
        x = a & (self.q - 1)
        for _ in range((self.n + 1) // 2):
            z ^= x
            x = self.square(self.square(x))
        return z


MODULI = {
    17: (1 << 17) | (1 << 3) | 1,
    23: (1 << 23) | (1 << 5) | 1,
    31: (1 << 31) | (1 << 3) | 1,
}


def field_for(n: int) -> Field:
    if n not in MODULI:
        raise KeyError(f"no frozen modulus for n={n}")
    return Field(MODULI[n])
