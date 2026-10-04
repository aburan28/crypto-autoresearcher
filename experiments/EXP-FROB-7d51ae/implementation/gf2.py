#!/usr/bin/env python3
"""Minimal F_2[t]/(f) arithmetic for EXP-FROB-7d51ae Stages 0-1.

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
    if n <= 0:
        return False
    if n == 1:
        return True
    x = 2
    cur = x
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2 and pgcd(mod, cur ^ x) != 1:
            return False
    return cur == x


class Field:
    """Elements are Python ints; bit j is the coefficient of t^j.

    Construct with either an irreducible modulus (bit poly) or via
    field_f2k(k) for small k and n=19.
    """

    def __init__(self, modulus: int, *, n: int | None = None):
        if n == 1 or modulus == 0:
            self.n = 1
            self.mod = 0
            return
        if not is_irreducible(modulus):
            raise ValueError(f"modulus not irreducible: {modulus:#x}")
        self.mod = modulus
        self.n = modulus.bit_length() - 1

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        if self.n == 1:
            return (a & 1) & (b & 1)
        mask = (1 << self.n) - 1
        return pmod(clmul(a & mask, b & mask), self.mod)

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
        if self.n == 1:
            return 1
        return self.pow(a, (1 << self.n) - 2)

    def trace(self, a: int) -> int:
        """Absolute trace F_{2^n} -> F_2."""
        if self.n == 1:
            return a & 1
        s = 0
        x = a & ((1 << self.n) - 1)
        for _ in range(self.n):
            s ^= x & 1
            x = self.square(x)
        return s & 1


def field_f2k(k: int) -> Field:
    """Construct F_{2^k} for point counts (k=1,2) and the n=19 toy field."""
    if k == 1:
        return Field(0, n=1)
    if k == 2:
        return Field(0b111)  # t^2 + t + 1
    if k == 19:
        return Field(MOD_F2_19)
    raise ValueError(f"unsupported extension degree {k}")


# Frozen irreducible for F_{2^{19}} (recorded in artifacts).
# t^19 + t^5 + t^2 + t + 1
MOD_F2_19 = (1 << 19) | (1 << 5) | (1 << 2) | (1 << 1) | 1
