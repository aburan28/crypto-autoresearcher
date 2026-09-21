#!/usr/bin/env python3
"""Bit-packed F_2[X] and F_{2^n} arithmetic for EXP-QSP-82a906 I2.

Convention: F_2[X] is a Python int, bit i = coefficient of X^i.
A K = F_{2^n} element is a Python int, bit i = coefficient of z^i,
reduced modulo the declared field polynomial.
"""
from __future__ import annotations


def deg(a: int) -> int:
    return a.bit_length() - 1


def clmul(a: int, b: int) -> int:
    if a.bit_count() > b.bit_count():
        a, b = b, a
    r = 0
    while a:
        low = a & -a
        r ^= b << (low.bit_length() - 1)
        a ^= low
    return r


def polymod(a: int, m: int) -> int:
    dm = deg(m)
    if dm < 0:
        raise ValueError("mod 0")
    while a and deg(a) >= dm:
        a ^= m << (deg(a) - dm)
    return a


def polydivmod(a: int, m: int) -> tuple[int, int]:
    if m == 0:
        raise ValueError("div 0")
    q = 0
    dm = deg(m)
    while a and deg(a) >= dm:
        s = deg(a) - dm
        q |= 1 << s
        a ^= m << s
    return q, a


def f2pow(a: int, e: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = clmul(r, a)
        a = clmul(a, a)
        e >>= 1
    return r


def gcd_f2(a: int, b: int) -> int:
    while b:
        a = polymod(a, b)
        a, b = b, a
    return a


def gf_mul(a: int, b: int, mod: int) -> int:
    return polymod(clmul(a, b), mod)


def gf_pow(a: int, e: int, mod: int) -> int:
    r = 1
    while e:
        if e & 1:
            r = gf_mul(r, a, mod)
        a = gf_mul(a, a, mod)
        e >>= 1
    return r


def gf_inv(a: int, n: int, mod: int) -> int:
    if a == 0:
        raise ZeroDivisionError("inv 0")
    return gf_pow(a, (1 << n) - 2, mod)


def gf_eval_f2poly(poly: int, x: int, mod: int) -> int:
    """Evaluate an F_2[X] polynomial at x in K."""
    r = 0
    p = poly
    xp = 1
    while p:
        if p & 1:
            r ^= xp
        xp = gf_mul(xp, x, mod)
        p >>= 1
    return r
