#!/usr/bin/env python3
"""I3: non-constant common factor of two bivariates in F_2[X,Y]."""
from __future__ import annotations

from f2arith import clmul, deg, gcd_f2, polymod


def ytrim(f: list[int]) -> list[int]:
    r = list(f)
    while r and r[-1] == 0:
        r.pop()
    return r


def ydeg(f: list[int]) -> int:
    f = ytrim(f)
    return len(f) - 1 if f else -1


def yadd(f: list[int], g: list[int]) -> list[int]:
    n = max(len(f), len(g))
    r = [(f[i] if i < len(f) else 0) ^ (g[i] if i < len(g) else 0) for i in range(n)]
    return ytrim(r)


def yscale(f: list[int], a: int) -> list[int]:
    if a == 0 or not f:
        return []
    return ytrim([clmul(c, a) for c in f])


def prem(f: list[int], g: list[int]) -> list[int]:
    if not ytrim(g):
        raise ValueError("prem by 0")
    r = ytrim(f)
    dg = ydeg(g)
    while ydeg(r) >= dg:
        shift = ydeg(r) - dg
        lc_r = r[-1]
        lc_g = g[-1]
        # r := lc_g * r + lc_r * Y^shift * g
        scaled_r = yscale(r, lc_g)
        shifted_g = [0] * shift + g
        scaled_g = yscale(shifted_g, lc_r)
        r = yadd(scaled_r, scaled_g)
    return r


def content(f: list[int]) -> int:
    c = 0
    for a in f:
        c = gcd_f2(c, a)
    return c


def primitive_part(f: list[int]) -> list[int]:
    from f2arith import polydivmod
    f = ytrim(f)
    if not f:
        return []
    c = content(f)
    if c <= 1:
        return f
    out = []
    for a in f:
        q, r = polydivmod(a, c)
        if r:
            return f
        out.append(q)
    return ytrim(out)


def ygcd(f: list[int], g: list[int]) -> list[int]:
    f, g = primitive_part(f), primitive_part(g)
    while ytrim(g):
        r = prem(f, g)
        r = primitive_part(r)
        f, g = g, r
    return primitive_part(f)


def has_nonconstant_common_factor(f: list[int], g: list[int]) -> bool:
    d = ygcd(f, g)
    if not d:
        return False
    if ydeg(d) >= 1:
        return True
    # constant in Y: non-constant in X?
    return deg(d[0]) >= 1
