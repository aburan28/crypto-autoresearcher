"""
Plain (uninstrumented) affine short-Weierstrass EC arithmetic, used only for
STRUCTURAL purposes: finding a point on a curve, and the fast order
certificate used to verify class-walk edges without repeating an O(p) point
count on every vertex (see class_walk.py docstring and implementation.md,
"edge certificate method"). This module is NOT used for any Q1/Q2/Q3 cost
measurement -- those use the separately instrumented engines in
ec_group_ops.py (Q1, common coordinate system) and ec_jacobian.py (Q2,
per-member cheapest model), so that no structural bookkeeping code
contaminates a counted metric.
"""
from __future__ import annotations

import random

from curve_utils import legendre_int


def find_smallest_point(a, b, p):
    """Deterministic (no RNG): the point with the smallest x >= 0 that
    lies on the curve, used as the FIXED generator P for a curve so that
    every seed/run for that curve starts from an identical, reproducible
    base point."""
    for x in range(p):
        f = (x * x * x + a * x + b) % p
        if f == 0:
            return (x, 0)
        if legendre_int(f, p) == 1:
            if p % 4 == 3:
                y = pow(f, (p + 1) // 4, p)
            else:
                y = tonelli_shanks(f, p)
            return (x, y)
    raise RuntimeError("no point found (singular curve?)")


def find_point(a, b, p, rng=None):
    """Find a random affine point (x, y) on y^2 = x^3+ax+b over F_p."""
    r = rng or random
    for _ in range(10000):
        x = r.randrange(0, p)
        f = (x * x * x + a * x + b) % p
        if f == 0:
            return (x, 0)
        if legendre_int(f, p) == 1:
            if p % 4 == 3:
                y = pow(f, (p + 1) // 4, p)
            else:
                y = tonelli_shanks(f, p)
            return (x, y)
    raise RuntimeError("could not find a curve point after many tries")


def tonelli_shanks(n, p):
    n %= p
    if n == 0:
        return 0
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    z = 2
    while legendre_int(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2i = 0, t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def ec_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        if y1 == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow((2 * y1) % p, p - 2, p) % p
    else:
        lam = (y2 - y1) * pow((x2 - x1) % p, p - 2, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def ec_scalar_mult(k, P, a, p):
    if k == 0 or P is None:
        return None
    if k < 0:
        return ec_scalar_mult(-k, negate(P, p), a, p)
    R = None
    Q = P
    while k:
        if k & 1:
            R = ec_add(R, Q, a, p)
        Q = ec_add(Q, Q, a, p)
        k >>= 1
    return R


def negate(P, p):
    if P is None:
        return None
    return (P[0], (-P[1]) % p)


def fast_order_certificate(a, b, p, N, rng=None, tries=5):
    """
    Independent, fast confirmation that #E(F_p) == N, GIVEN that N is prime
    and lies in the Hasse interval for p (both checked by the caller before
    calling this). Method: find a random nonzero point P; if [N]P == O and
    P != O, then ord(P) | N, and since N is prime and P != O, ord(P) == N,
    so N | #E(F_p) (Lagrange). Since N is prime and #E(F_p) lies in the
    Hasse interval [p+1-2sqrt(p), p+1+2sqrt(p)] of width < 4*sqrt(p) < N for
    every p handled by this experiment (toy scale, N ~ p >> 16), N is the
    UNIQUE multiple of N in that interval, so #E(F_p) == N is thereby
    established. This is independent of, and far cheaper than, a full O(p)
    point count, and is repeated `tries` times with fresh random points as
    a defense against a degenerate unlucky point (e.g. P of small order due
    to a coding error elsewhere, which a single trial could miss only if
    #E(F_p) had a small-order point AND N | #E(F_p) coincidentally for the
    wrong reason -- ruled out here by N being prime and > 4*sqrt(p)).
    """
    r = rng or random
    hasse_width = 4 * (int(p ** 0.5) + 2)
    if hasse_width >= N:
        raise ValueError(
            "fast_order_certificate precondition violated: N is not large "
            "enough relative to p for uniqueness in the Hasse interval"
        )
    for _ in range(tries):
        P = find_point(a, b, p, rng=r)
        if P is None or P[1] == 0:
            continue
        Q = ec_scalar_mult(N, P, a, p)
        if Q is not None:
            return False
    return True
