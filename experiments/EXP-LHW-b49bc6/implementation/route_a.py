"""Route A: Pascal product binomials, 6k±1 primality, bytearray bitmap sumset.

Must not import route_b.
"""
from __future__ import annotations


def comb_a(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(1, k + 1):
        num *= n - k + i
        den *= i
    return num // den


def _is_prime_6k(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    d = 5
    while d * d <= n:
        if n % d == 0 or n % (d + 2) == 0:
            return False
        d += 6
    return True


def next_prime_a(n: int) -> int:
    p = n + 1
    if p <= 2:
        return 2
    if p % 2 == 0:
        p += 1
    while not _is_prime_6k(p):
        p += 2
    return p


def card_sumset_a(xs: tuple[int, ...], js: tuple[int, ...], lo: int, hi: int) -> int:
    span = hi - lo + 1
    bits = bytearray((span + 7) // 8)
    for j in js:
        for x in xs:
            v = x + j
            if lo <= v <= hi:
                k = v - lo
                bits[k >> 3] |= 1 << (k & 7)
    return sum(bin(b).count("1") for b in bits)
