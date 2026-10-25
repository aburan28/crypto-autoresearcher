"""Red-team library for EXP-CZLIFT-14f6d5 (TASK-20261023-7b5dc6).

Independent of the producer's code (the lane-1 library was not read).  Conventions
follow the run records: x = a/d^2 in lowest terms, naive height H(x) = max(|a|, d^2),
N_E(H) counts O plus every affine point (P and -P separately).

Point test: (2y + a1 x + a3)^2 = 4x^3 + b2 x^2 + 2 b4 x + b6, so with x = a/d^2 the
point exists iff g(a, d) = 4a^3 + b2 a^2 d^2 + 2 b4 a d^4 + b6 d^6 is a perfect square.
A modular quadratic-residue sieve (necessary condition) filters candidates; every
survivor is decided by exact integer arithmetic (math.isqrt).
"""
from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

MODULI = [64, 63, 65, 11, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]


def b_invariants(ai):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return b2, b4, b6, b8


def discriminant(ai):
    b2, b4, b6, b8 = b_invariants(ai)
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def g_exact(a, d, b2, b4, b6):
    d2 = d * d
    return 4 * a ** 3 + b2 * a * a * d2 + 2 * b4 * a * d2 * d2 + b6 * d2 * d2 * d2


def enumerate_points(ai, hmax):
    """Return list of (a, d, c) with c >= 0, c^2 = g(a, d), gcd(a, d) = 1, max(|a|, d^2) <= hmax."""
    b2, b4, b6, _ = b_invariants(ai)
    a_arr = np.arange(-hmax, hmax + 1, dtype=np.int64)
    amods = {m: (a_arr % m).astype(np.int64) for m in MODULI}
    sq = {m: np.zeros(m, dtype=bool) for m in MODULI}
    for m in MODULI:
        for t in range(m):
            sq[m][(t * t) % m] = True
    out = []
    for d in range(1, math.isqrt(hmax) + 1):
        mask = None
        for m in MODULI:
            tab = np.fromiter((sq[m][g_exact(r, d, b2, b4, b6) % m] for r in range(m)), dtype=bool, count=m)
            sel = tab[amods[m]]
            mask = sel if mask is None else (mask & sel)
        for a in a_arr[mask].tolist():
            if math.gcd(a, d) != 1:
                continue
            g = g_exact(a, d, b2, b4, b6)
            if g < 0:
                continue
            c = math.isqrt(g)
            if c * c == g:
                out.append((a, d, c))
    return out


def counts_from_points(pts, grid):
    res = {}
    for H in grid:
        n = 1
        for a, d, c in pts:
            if max(abs(a), d * d) <= H:
                n += 1 if c == 0 else 2
        res[H] = n
    return res


# ---------------------------------------------------------------- group law (affine, exact)

def point_from_adc(ai, a, d, c, sign=1):
    a1, a2, a3, a4, a6 = ai
    x = Fraction(a, d * d)
    # 2y + a1 x + a3 = sign * c / d^3
    y = (Fraction(sign * c, d ** 3) - a1 * x - a3) / 2
    return (x, y)


def on_curve(ai, P):
    if P is None:
        return True
    a1, a2, a3, a4, a6 = ai
    x, y = P
    return y * y + a1 * x * y + a3 * y == x ** 3 + a2 * x * x + a4 * x + a6


def neg(ai, P):
    if P is None:
        return None
    a1, a2, a3, a4, a6 = ai
    x, y = P
    return (x, -y - a1 * x - a3)


def add(ai, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    a1, a2, a3, a4, a6 = ai
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 + y2 + a1 * x2 + a3 == 0:
            return None
        lam = (3 * x1 * x1 + 2 * a2 * x1 + a4 - a1 * y1) / (2 * y1 + a1 * x1 + a3)
    else:
        lam = (y2 - y1) / (x2 - x1)
    nu = y1 - lam * x1
    x3 = lam * lam + a1 * lam - a2 - x1 - x2
    y3 = -(lam + a1) * x3 - nu - a3
    return (x3, y3)


def naive_logh(x: Fraction) -> float:
    n, d = abs(x.numerator), x.denominator
    m = max(n, d)
    # log of a big int without overflow
    return math.log(m) if m < (1 << 1000) else (m.bit_length() - 64) * math.log(2) + math.log(m >> (m.bit_length() - 64))


def x_double(ai, x: Fraction):
    """x(2P) from x(P) via the division-polynomial formula; None if 2P = O."""
    b2, b4, b6, b8 = b_invariants(ai)
    num = x ** 4 - b4 * x * x - 2 * b6 * x - b8
    den = 4 * x ** 3 + b2 * x * x + 2 * b4 * x + b6
    if den == 0:
        return None
    return num / den


def canonical_height(ai, P, n=6):
    """Silverman normalisation: hhat(P) = 1/2 lim 4^-k h(x(2^k P)).  Returns (estimate at n, estimate at n-1)."""
    if P is None:
        return 0.0, 0.0
    x = P[0]
    ests = []
    for k in range(n + 1):
        if x is None:
            return 0.0, 0.0
        ests.append(naive_logh(x) / (2 * 4 ** k))
        if k < n:
            x = x_double(ai, x)
    return ests[-1], ests[-2]
