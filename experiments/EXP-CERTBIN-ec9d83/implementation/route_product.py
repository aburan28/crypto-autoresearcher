"""Route product: C(n, k) by falling product. Isolated from the closed-form route."""

from __future__ import annotations

from fractions import Fraction


def binomial(n: int, k: int) -> int:
    if k < 0 or n < 0:
        raise ValueError("binomial arguments must be nonnegative")
    if k == 0 or k == n:
        return 1
    if k > n:
        return 0
    k = min(k, n - k)
    acc = 1
    for i in range(k):
        acc = acc * (n - i) // (i + 1)
    return acc


def m_k(m: int, B: int) -> int:
    k = m // 2
    return binomial(B + k - 1, k)


def m_pair(B: int) -> int:
    return B * (B - 1) // 2


def r_mem(m: int, B: int) -> Fraction:
    return Fraction(m_k(m, B), m_pair(B))


ROUTE_ID = "product"
