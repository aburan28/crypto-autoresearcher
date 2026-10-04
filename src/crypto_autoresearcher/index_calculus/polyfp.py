"""Dense univariate polynomials over F_p: just enough to find roots.

A polynomial is a list of coefficients, lowest degree first, reduced mod p
and without trailing zeros; [] is the zero polynomial.  ``roots`` returns the
distinct roots in F_p: gcd with x^p - x isolates the product of the linear
factors, and Cantor-Zassenhaus splitting separates them.
"""

from __future__ import annotations

import random


def trim(f: list[int], p: int) -> list[int]:
    f = [c % p for c in f]
    while f and f[-1] == 0:
        f.pop()
    return f


def evaluate(f: list[int], x: int, p: int) -> int:
    acc = 0
    for c in reversed(f):
        acc = (acc * x + c) % p
    return acc


def mul(f: list[int], g: list[int], p: int) -> list[int]:
    if not f or not g:
        return []
    out = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        if a:
            for j, b in enumerate(g):
                out[i + j] += a * b
    return trim(out, p)


def divmod_(f: list[int], g: list[int], p: int) -> tuple[list[int], list[int]]:
    g = trim(g, p)
    if not g:
        raise ZeroDivisionError("polynomial division by zero")
    r = trim(f, p)
    inv = pow(g[-1], -1, p)
    q = [0] * max(0, len(r) - len(g) + 1)
    while len(r) >= len(g):
        c = r[-1] * inv % p
        shift = len(r) - len(g)
        q[shift] = c
        for k, b in enumerate(g):
            r[shift + k] = (r[shift + k] - c * b) % p
        r = trim(r, p)
    return trim(q, p), r


def mod(f: list[int], g: list[int], p: int) -> list[int]:
    return divmod_(f, g, p)[1]


def monic(f: list[int], p: int) -> list[int]:
    if not f:
        return f
    inv = pow(f[-1], -1, p)
    return [c * inv % p for c in f]


def gcd(f: list[int], g: list[int], p: int) -> list[int]:
    f, g = trim(f, p), trim(g, p)
    while g:
        f, g = g, mod(f, g, p)
    return monic(f, p)


def powmod(base: list[int], e: int, m: list[int], p: int) -> list[int]:
    result, base = [1], mod(base, m, p)
    while e:
        if e & 1:
            result = mod(mul(result, base, p), m, p)
        base = mod(mul(base, base, p), m, p)
        e >>= 1
    return result


def from_roots(roots, p: int) -> list[int]:
    f = [1]
    for r in roots:
        f = mul(f, [(-r) % p, 1], p)
    return f


def roots(f: list[int], p: int, seed: int = 0) -> list[int]:
    """Distinct roots in F_p of f (p an odd prime), ascending."""
    f = trim(f, p)
    if len(f) <= 1:
        return []
    xp = powmod([0, 1], p, f, p)
    split = gcd(f, _sub_x(xp, p), p)  # product of the distinct linear factors
    rng = random.Random(seed)
    out: list[int] = []
    _split(split, p, rng, out)
    return sorted(out)


def _sub_x(g: list[int], p: int) -> list[int]:
    g = g + [0] * max(0, 2 - len(g))
    g[1] = (g[1] - 1) % p
    return trim(g, p)


def _split(g: list[int], p: int, rng: random.Random, out: list[int]) -> None:
    """Append the roots of g, a product of distinct linear factors."""
    if len(g) <= 1:
        return
    if len(g) == 2:
        out.append((-g[0]) * pow(g[1], -1, p) % p)
        return
    while True:
        a = rng.randrange(p)
        h = powmod([a, 1], (p - 1) // 2, g, p)
        h = gcd(g, _sub_one(h, p), p)
        if 1 < len(h) < len(g):
            _split(h, p, rng, out)
            _split(divmod_(g, h, p)[0], p, rng, out)
            return


def _sub_one(h: list[int], p: int) -> list[int]:
    h = h + [0] * max(0, 1 - len(h))
    h[0] = (h[0] - 1) % p
    return trim(h, p)
