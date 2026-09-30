#!/usr/bin/env python3
"""Frozen m=2 chain: S_3 at xi=1, phi-composition, per-variable degrees."""
from __future__ import annotations

from f2arith import clmul, deg


# S^{(0)} = X1^2 X2^2 + X1^2 + X2^2 + X1 X2 + 1
# as Y = X2 polynomial with F_2[X] coeffs (X = X1):
#   Y^2 * (X^2+1) + Y * X + (X^2+1)
S0_Y: list[int] = [0b101, 0b10, 0b101]  # X^2+1, X, X^2+1


def expand_s3_at_xi1() -> list[int]:
    """(X1 X2 + X1 + X2)^2 + X1 X2 + 1 in char 2, as Y-coeffs."""
    # (X Y + X + Y)^2 = X^2 Y^2 + X^2 + Y^2
    # + X Y + 1
    return [0b101, 0b10, 0b101]


def ytrim(f: list[int]) -> list[int]:
    r = list(f)
    while r and r[-1] == 0:
        r.pop()
    return r


def ydeg(f: list[int]) -> int:
    f = ytrim(f)
    return len(f) - 1 if f else -1


def deg_x_of_ycoeffs(f: list[int]) -> int:
    d = -1
    for c in f:
        if c:
            d = max(d, deg(c))
    return d


def compose_lambda_y(f: list[int], lam: int) -> list[int]:
    """S(lambda(X), lambda(Y)): f has Y-coeffs in F_2[X]; substitute.

    f = sum_j c_j(X) Y^j.  Result = sum_j c_j(lambda(X)) lambda(Y)^j.
    lambda in F_2[X]; lambda(Y)^j via repeated clmul in Y (F_2[Y] as ints
    with a parallel F_2[X] coeff ring — here c_j(lambda(X)) is F_2[X]).
    """
    # lambda(Y) as Y-poly: bits of lam become F_2[X] constants 0 or 1
    lam_y = []
    tmp = lam
    i = 0
    while tmp:
        if tmp & 1:
            while len(lam_y) <= i:
                lam_y.append(0)
            lam_y[i] = 1
        tmp >>= 1
        i += 1
    lam_y = ytrim(lam_y)

    def ymul(a: list[int], b: list[int]) -> list[int]:
        if not a or not b:
            return []
        r = [0] * (len(a) + len(b) - 1)
        for i, ca in enumerate(a):
            if not ca:
                continue
            for j, cb in enumerate(b):
                if cb:
                    r[i + j] ^= clmul(ca, cb)
        return ytrim(r)

    def ypow(base: list[int], e: int) -> list[int]:
        r = [1]
        b = base
        while e:
            if e & 1:
                r = ymul(r, b)
            b = ymul(b, b)
            e >>= 1
        return r

    # c_j(lambda(X)): Horner compose each F_2[X] coeff with lam
    def compose_x(c: int, lam: int) -> int:
        r = 0
        p = c
        # Horner from high bit
        for k in range(deg(c), -1, -1):
            r = clmul(r, lam)
            if (p >> k) & 1:
                r ^= 1
        return r

    acc: list[int] = []
    for j, cj in enumerate(f):
        if not cj:
            continue
        cj_sub = compose_x(cj, lam)
        pow_y = ypow(lam_y, j)
        term = [clmul(c, cj_sub) for c in pow_y]
        n = max(len(acc), len(term))
        nxt = [0] * n
        for i in range(n):
            if i < len(acc):
                nxt[i] ^= acc[i]
            if i < len(term):
                nxt[i] ^= term[i]
        acc = ytrim(nxt)
    return acc


def per_variable_degrees(f: list[int]) -> tuple[int, int]:
    """(deg_X, deg_Y) of a bivariate given as Y-coeffs in F_2[X]."""
    return deg_x_of_ycoeffs(f), ydeg(f)
