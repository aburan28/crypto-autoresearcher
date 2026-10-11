"""Dual-route Möbius / ANF degree of F_p-valued functions on {0,1}^N.

Route A: in-place subset Möbius transform.
Route B: naive inclusion-exclusion over submasks.
Amazon Bedrock is not selected.
"""
from __future__ import annotations


def popcount(x: int) -> int:
    return x.bit_count()


def mobius_fast(values: list[int], p: int) -> list[int]:
    """Route A. values[mask] = f(mask); returns ANF coefficients."""
    table = [v % p for v in values]
    n = len(table)
    bit = 1
    while bit < n:
        for mask in range(n):
            if mask & bit:
                table[mask] = (table[mask] - table[mask ^ bit]) % p
        bit <<= 1
    return table


def mobius_naive(values: list[int], p: int) -> list[int]:
    """Route B. Direct sum_{T ⊆ S} (-1)^{|S|-|T|} f(T)."""
    n = len(values)
    out = [0] * n
    for mask in range(n):
        acc = 0
        bits = popcount(mask)
        sub = mask
        while True:
            sign = 1 if ((bits - popcount(sub)) % 2 == 0) else -1
            acc += sign * (values[sub] % p)
            if sub == 0:
                break
            sub = (sub - 1) & mask
        out[mask] = acc % p
    return out


def anf_degree(coeffs: list[int]) -> int:
    deg = -1
    for mask, c in enumerate(coeffs):
        if c:
            deg = max(deg, popcount(mask))
    return deg


def pointwise_inv(values: list[int], p: int) -> list[int] | None:
    out = []
    for v in values:
        v %= p
        if v == 0:
            return None
        out.append(pow(v, p - 2, p))
    return out


def dual_degree(values: list[int], p: int) -> tuple[int, int, bool]:
    a = anf_degree(mobius_fast(values, p))
    b = anf_degree(mobius_naive(values, p))
    return a, b, a == b
