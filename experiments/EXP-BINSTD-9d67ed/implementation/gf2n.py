#!/usr/bin/env python3
"""Stdlib F_{2^n} arithmetic for EXP-BINSTD-9d67ed. No numpy/Sage/Magma."""
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
    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)
