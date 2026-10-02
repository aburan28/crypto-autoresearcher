#!/usr/bin/env python3
"""Minimal F_2[t]/(f) arithmetic for EXP-FROB-8451c7 Stages 0-1.

Self-contained (no numpy). Field polynomials are frozen here and recorded in
run artifacts. Read-only reference pattern: EXP-CERTBIN-e94b27/impl/gf2n.py
(schoolbook clmul + reduction); this module does not import that path.
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
    """Elements are Python ints; bit j is the coefficient of t^j."""

    def __init__(self, modulus: int):
        if not is_irreducible(modulus):
            raise ValueError(f"modulus not irreducible: {modulus:#x}")
        self.mod = modulus
        self.n = modulus.bit_length() - 1

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a & ((1 << self.n) - 1), b & ((1 << self.n) - 1)), self.mod)

    def square(self, a: int) -> int:
        return self.mul(a, a)

    def pow(self, a: int, e: int) -> int:
        r = 1
        a &= (1 << self.n) - 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("invert 0")
        return self.pow(a, (1 << self.n) - 2)

    def trace(self, a: int) -> int:
        """Absolute trace F_{2^n} -> F_2."""
        s = 0
        x = a & ((1 << self.n) - 1)
        for _ in range(self.n):
            s ^= x & 1
            x = self.square(x)
        return s & 1


# Frozen irreducible polynomials (recorded in artifacts).
MOD_F2_8 = 0b100011011  # t^8 + t^4 + t^3 + t + 1
MOD_F2_17 = (1 << 17) | (1 << 3) | 1  # t^17 + t^3 + 1 (CERTBIN-e94b27)
