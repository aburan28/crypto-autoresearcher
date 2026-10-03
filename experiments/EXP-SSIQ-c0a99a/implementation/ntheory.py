"""Integer arithmetic for EXP-SSIQ-c0a99a (Arm I degree thinning).

No curves. No Magma/Sage. No Bedrock. Not an attack.
"""
from __future__ import annotations

from typing import Iterable


def miller_rabin(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if a >= n:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def integer_nth_root(n: int, k: int) -> int:
    if n < 0 or k < 1:
        raise ValueError("nth_root domain")
    if n < 2:
        return n
    x = 1 << ((n.bit_length() + k - 1) // k)
    while True:
        y = ((k - 1) * x + n // pow(x, k - 1)) // k
        if y >= x:
            return x
        x = y


def split_window_x(p: int, B: int) -> int:
    """X = floor(sqrt(B) * (p/2)^{1/6}) via integer roots (B a perfect square)."""
    return integer_nth_root(B, 2) * integer_nth_root(p // 2, 6)


def sieve_primes(limit: int) -> list[int]:
    if limit < 2:
        return []
    flags = bytearray(b"\x01") * (limit + 1)
    flags[0] = flags[1] = 0
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if flags[i]:
            start = i * i
            nslot = ((limit - start) // i) + 1
            flags[start : limit + 1 : i] = b"\x00" * nslot
    return [i for i in range(2, limit + 1) if flags[i]]


def jacobi(a: int, n: int) -> int:
    if n <= 0 or n % 2 == 0:
        raise ValueError("jacobi modulus")
    a %= n
    result = 1
    while a:
        while a % 2 == 0:
            a //= 2
            if n % 8 in (3, 5):
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0


def factor_trial(n: int, primes: Iterable[int]) -> list[tuple[int, int]]:
    """Return [(p,e), ...] for B-smooth n; remainder >1 means not fully factored."""
    out: list[tuple[int, int]] = []
    x = n
    for p in primes:
        if p * p > x:
            break
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        if e:
            out.append((p, e))
    if x > 1:
        if miller_rabin(x):
            out.append((x, 1))
        else:
            out.append((x, 0))
    return out


def is_bsmooth_factored(factors: list[tuple[int, int]], B: int) -> bool:
    if not factors:
        return False
    for p, e in factors:
        if e <= 0 or p > B:
            return False
    return True


def reconstruct(factors: list[tuple[int, int]]) -> int:
    n = 1
    for p, e in factors:
        n *= pow(p, e)
    return n
