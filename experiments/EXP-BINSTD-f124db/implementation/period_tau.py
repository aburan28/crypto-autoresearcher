"""Shared period / tau arithmetic for EXP-BINSTD-f124db Stages 0-1."""
from __future__ import annotations

from math import gcd


def n_period(c: int, d: int) -> int:
    """Conjugate period n(c) = d / gcd(c, d)."""
    g = gcd(c, d)
    return d // g


def divisors_of(n: int) -> list[int]:
    return [i for i in range(1, n + 1) if n % i == 0]


def tau(n: int) -> int:
    return len(divisors_of(n))


def d11575_stated_period(c: int, d: int, k: int) -> int:
    """Inherited d11575 special-case formulas for the two k-prime families.

    Family 1: c | d  ->  stated n = d/c
    Family 2: c = j*k with j | d  ->  stated n = d/j = d/(c/k)
    """
    if d % c == 0:
        return d // c
    if c % k == 0:
        j = c // k
        if d % j == 0:
            return d // j
    raise ValueError(f"c={c} not in d11575 two-family lattice for d={d}, k={k}")


def ten_divisors(d: int, k: int) -> list[int]:
    """Divisors of N=d*k when k is prime and gcd(d,k)=1: {1..d powers} U {k*those}."""
    base = divisors_of(d)
    return sorted(base + [k * b for b in base])
