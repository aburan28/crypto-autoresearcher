"""Exact rational-point arithmetic over Q via fractions.Fraction, for the
global curve E: y^2 = x^3 + a x + b (integer a, b) and an integer point S^.
This is the one place exact global arithmetic is used (per the contract):
it produces the real bit-size growth of x(m S^) being measured in Stage 2.
"""
from __future__ import annotations

from fractions import Fraction

Point = tuple  # (Fraction, Fraction) or None for O


def is_on_curve(a: int, b: int, pt) -> bool:
    if pt is None:
        return True
    x, y = pt
    return y * y == x ** 3 + a * x + b


def negate(pt):
    if pt is None:
        return None
    x, y = pt
    return (x, -y)


def add(a: int, b: int, P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and y1 + y2 == 0:
        return None
    if x1 == x2 and y1 == y2:
        lam = Fraction(3 * x1 * x1 + a, 2 * y1)
    else:
        lam = Fraction(y2 - y1, x2 - x1)
    x3 = lam * lam - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


def mul(a: int, b: int, k: int, P):
    if P is None:
        return None
    if k < 0:
        return mul(a, b, -k, negate(P))
    result = None
    addend = P
    while k > 0:
        if k & 1:
            result = add(a, b, result, addend)
        addend = add(a, b, addend, addend)
        k >>= 1
    return result
