"""Route closed-form: k-specific stars-and-bars. Isolated from the falling-product route."""

from __future__ import annotations

from fractions import Fraction


def m_k(m: int, B: int) -> int:
    k = m // 2
    if k == 1:
        return B
    if k == 2:
        return B * (B + 1) // 2
    if k == 3:
        return B * (B + 1) * (B + 2) // 6
    raise ValueError(f"closed-form route covers k in {{1,2,3}}, got k={k} from m={m}")


def m_pair(B: int) -> int:
    return (B * (B - 1)) // 2


def r_mem(m: int, B: int) -> Fraction:
    return Fraction(m_k(m, B), m_pair(B))


ROUTE_ID = "closedform"
