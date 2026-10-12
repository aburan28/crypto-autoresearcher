"""Route B: multiplicative binomials, odd trial primality, uint64-word bitmap.

Must not import route_a.
"""
from __future__ import annotations
from array import array


def comb_b(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    acc = 1
    for i in range(k):
        acc = acc * (n - i) // (i + 1)
    return acc


def _is_prime_odd(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def next_prime_b(n: int) -> int:
    p = n + 1
    if p <= 2:
        return 2
    if p % 2 == 0:
        p += 1
    while not _is_prime_odd(p):
        p += 2
    return p


def card_sumset_b(xs: tuple[int, ...], js: tuple[int, ...], lo: int, hi: int) -> int:
    span = hi - lo + 1
    nwords = (span + 63) // 64
    words = array("Q", [0]) * nwords
    for j in js:
        for x in xs:
            v = x + j
            if lo <= v <= hi:
                k = v - lo
                words[k >> 6] |= 1 << (k & 63)
    return sum(bin(w).count("1") for w in words)
