"""Instrumented univariate polynomial arithmetic over F_p.

Polynomials are lists of ints, lowest degree first, trimmed so that the last
entry is non-zero; the zero polynomial is ``[]``. Every multiplication and
inversion is charged to the ``Fp`` counter (bulk counts equal the exact
number of products performed; see tests/test_poly.py).
"""

from __future__ import annotations

from fparith import Fp


def trim(a: list) -> list:
    while a and a[-1] == 0:
        a.pop()
    return a


def deg(a: list) -> int:
    return len(a) - 1  # -1 for the zero polynomial


def from_roots(F: Fp, roots) -> list:
    """prod (u - v) over roots; sequential, sum_i i mults (charged)."""
    p = F.p
    poly = [1]
    n_mul = 0
    for v in roots:
        nv = (-v) % p
        new = [0] * (len(poly) + 1)
        for i, c in enumerate(poly):
            new[i + 1] = (new[i + 1] + c) % p
            new[i] = (new[i] + c * nv) % p
        n_mul += len(poly)
        poly = new
    F.count_mul(n_mul)
    return poly


def evaluate(F: Fp, a: list, x: int) -> int:
    p = F.p
    acc = 0
    for c in reversed(a):
        acc = (acc * x + c) % p
    F.count_mul(max(len(a) - 1, 0))
    return acc


def scale(F: Fp, a: list, s: int) -> list:
    p = F.p
    F.count_mul(len(a))
    return trim([c * s % p for c in a])


def rem(F: Fp, a: list, b: list) -> list:
    """a mod b with one inversion of lc(b); (deg a - deg b + 1)(deg b + 1) mults."""
    p = F.p
    db = deg(b)
    if db < 0:
        raise ZeroDivisionError("polynomial division by zero")
    r = list(a)
    da = deg(r)
    if da < db:
        return trim(r)
    inv_lc = F.inv(b[-1])
    n_mul = 0
    for i in range(da, db - 1, -1):
        coef = r[i] * inv_lc % p
        n_mul += 1
        if coef:
            base = i - db
            for j in range(db):
                r[base + j] = (r[base + j] - coef * b[j]) % p
            n_mul += db
        r[i] = 0
    F.count_mul(n_mul)
    return trim(r[:db] if db > 0 else [])


def prem(F: Fp, a: list, b: list) -> list:
    """Pseudo-remainder lc(b)^(deg a - deg b + 1) * (a mod b).

    Over a field this equals the fraction-free (Collins) pseudo-division
    result coefficient for coefficient; it is computed through its field form
    so the charged cost is linear in deg a rather than quadratic.
    """
    delta = deg(a) - deg(b)
    r = rem(F, a, b)
    if not r or delta < 0:
        return r
    return scale(F, r, F.pow(b[-1], delta + 1))


def subresultant_prs(F: Fp, a: list, b: list) -> dict:
    """Collins/Brown subresultant PRS of (a, b) with early abort.

    Cohen, GTM 138, Algorithm 3.3.7 without content removal (field
    coefficients). Aborts at the first vanishing pseudo-remainder (the last
    non-zero element is then proportional to gcd(a, b)) or at the first
    constant one (coprime). No resultant or eliminant is ever expanded.
    Returns deg_gcd, the gcd polynomial (unnormalised), the degree sequence
    and the number of PRS steps.
    """
    a, b = trim(list(a)), trim(list(b))
    if not b:
        return dict(deg_gcd=deg(a), gcd=a, degrees=[deg(a), -1], steps=0, abort="b_zero")
    if not a:
        return dict(deg_gcd=deg(b), gcd=b, degrees=[-1, deg(b)], steps=0, abort="a_zero")
    if deg(a) < deg(b):
        a, b = b, a
    p = F.p
    g, hh = 1, 1
    degrees = [deg(a), deg(b)]
    steps = 0
    while True:
        if deg(b) == 0:
            return dict(deg_gcd=0, gcd=[1], degrees=degrees, steps=steps, abort="constant")
        delta = deg(a) - deg(b)
        r = prem(F, a, b)
        steps += 1
        degrees.append(deg(r))
        if not r:
            return dict(deg_gcd=deg(b), gcd=b, degrees=degrees, steps=steps, abort="vanishing")
        if deg(r) == 0:
            return dict(deg_gcd=0, gcd=[1], degrees=degrees, steps=steps, abort="constant")
        a = b
        divisor = F.mul(g, F.pow(hh, delta)) if delta else g % p
        b = scale(F, r, F.inv(divisor))
        g = a[-1]
        if delta == 0:
            hh = hh  # h^(1-0) g^0 = h
        else:
            hh = F.mul(F.pow(g, delta), F.inv(F.pow(hh, delta - 1))) if delta > 1 \
                else F.pow(g, delta)
