"""Shared toy prime generator for the H-ECDLP-bd1572 battery.

Byte-identical copies live in every EXP-ECDLP-* implementation directory of
the battery so that the special primes and their matched random primes are the
same objects across contracts. Pure Python 3 standard library.

Special prime: p = m^d - c, c in C_LIST (|c| >= 2, squarefree, so x^d - c is
irreducible over Q by Capelli's theorem), m scanned upward from
ceil(2^((bits-1)/d)) until m^d >= 2^bits, p required prime with exactly
`bits` bits. Matched random prime: the first prime at or above a seeded
uniform integer with exactly `bits` bits.
"""
from __future__ import annotations

import math
import random

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def is_prime(n: int, rounds: int = 64) -> bool:
    if n < 2:
        return False
    for q in SMALL_PRIMES:
        if n % q == 0:
            return n == q
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    if n < 3_317_044_064_679_887_385_961_981:
        bases = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    else:
        rng = random.Random(n)
        bases = [rng.randrange(2, n - 1) for _ in range(rounds)]
    for a in bases:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def squarefree(n: int) -> bool:
    n = abs(n)
    q = 2
    while q * q <= n:
        if n % (q * q) == 0:
            return False
        q += 1
    return True


C_LIST = [c for c in sorted(range(-31, 32), key=lambda c: (abs(c), c > 0))
          if abs(c) >= 2 and squarefree(c)]


def special_primes(d: int, bits: int, count: int) -> list[dict]:
    """The first `count` special primes p = m^d - c with exactly `bits` bits."""
    found: list[dict] = []
    m = max(2, math.ceil(2 ** ((bits - 1) / d)))
    while m ** d < 2 ** bits and len(found) < count:
        for c in C_LIST:
            p = m ** d - c
            if p.bit_length() == bits and is_prime(p):
                found.append({"p": p, "m": m, "c": c, "d": d})
                if len(found) >= count:
                    break
        m += 1
    return found


def matched_random_prime(bits: int, seed: int, tag: str) -> dict:
    rng = random.Random(f"H-ECDLP-bd1572:{seed}:{tag}")
    start = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
    p = start
    while not is_prime(p):
        p += 2
    if p.bit_length() != bits:  # wrapped past 2^bits; restart lower
        p = (1 << (bits - 1)) + 1
        while not is_prime(p):
            p += 2
    return {"p": p, "seed": seed, "tag": tag, "start": start}


def balanced_digits(n: int, base: int, count: int) -> list[int] | None:
    """Balanced base-`base` digits of n, least significant first.

    Returns None when n does not fit in `count` digits.
    """
    digits = []
    r = n
    for _ in range(count):
        dig = r % base
        if dig > base // 2:
            dig -= base
        digits.append(dig)
        r = (r - dig) // base
    return digits if r == 0 else None


def monic_base_m_poly(p: int, m: int, d: int) -> list[int] | None:
    """Coefficients (low to high) of x^d + g(x), g = balanced base-m digits of p - m^d."""
    g = balanced_digits(p - m ** d, m, d)
    if g is None:
        return None
    return g + [1]


def primes_upto(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(sieve[i * i::i]))
    return [i for i in range(n + 1) if sieve[i]]
