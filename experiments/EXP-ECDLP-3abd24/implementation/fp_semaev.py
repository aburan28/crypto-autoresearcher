"""Prime-field S_3 and Weierstrass arithmetic for EXP-ECDLP-3abd24.

Two independent S_3 expansions (route A / route B). No Magma/Sage/AUXIN.
Amazon Bedrock is not selected.
"""
from __future__ import annotations


def modinv(a: int, p: int) -> int:
    a %= p
    if a == 0:
        raise ZeroDivisionError("no inverse")
    return pow(a, p - 2, p)


def is_prime(n: int) -> bool:
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


def least_prime_above(n: int) -> int:
    x = n + 1
    if x % 2 == 0:
        x += 1
    while not is_prime(x):
        x += 2
    return x


def s3_eval_a(a_curve: int, b_curve: int, x1: int, x2: int, x3: int, p: int) -> int:
    """Standard Semaev S_3 expansion (route A)."""
    t = (
        (x1 - x2) ** 2 * x3**2
        - 2 * ((x1 + x2) * (x1 * x2 + a_curve) + 2 * b_curve) * x3
        + ((x1 * x2 - a_curve) ** 2 - 4 * b_curve * (x1 + x2))
    )
    return t % p


def s3_eval_b(a_curve: int, b_curve: int, x1: int, x2: int, x3: int, p: int) -> int:
    """Expanded Semaev S_3 (route B); algebraically the same polynomial."""
    x1x2 = x1 * x2
    s = x1 + x2
    t = (
        x3 * x3 * (x1 * x1 - 2 * x1 * x2 + x2 * x2)
        - 2 * (x1x2 * s + a_curve * s + 2 * b_curve) * x3
        + (x1x2 * x1x2 - 2 * a_curve * x1x2 + a_curve * a_curve - 4 * b_curve * s)
    )
    return t % p


def on_curve(p: int, a_curve: int, b_curve: int, x: int, y: int) -> bool:
    return (y * y - (x * x * x + a_curve * x + b_curve)) % p == 0


def point_add(
    p: int,
    a_curve: int,
    p1: tuple[int, int] | None,
    p2: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if p1 == p2:
        if y1 % p == 0:
            return None
        lam = ((3 * x1 * x1 + a_curve) * modinv(2 * y1, p)) % p
    else:
        lam = ((y2 - y1) * modinv((x2 - x1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def digit_eval(bits: int, s: int) -> int:
    """l(a) = sum_{i<s} 2^i a_i."""
    total = 0
    pow2 = 1
    for i in range(s):
        if bits >> i & 1:
            total += pow2
        pow2 *= 2
    return total
