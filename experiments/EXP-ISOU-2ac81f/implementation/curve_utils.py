"""
Structural curve utilities independent of the isogeny/rho machinery:
  - exact point counting via a quadratic-residue sieve (O(p) time, O(p)
    memory), used to (a) select/verify the base curve, (b) INDEPENDENTLY
    verify every walk edge (this doubles as part of the edge certificate:
    a Velu-constructed curve is only accepted if its independently counted
    order equals N), and (c) size the null-object controls;
  - j-invariant;
  - class number h(D) of the imaginary quadratic order of discriminant D via
    direct enumeration of reduced primitive binary quadratic forms
    (Gauss's algorithm), independent of anything isogeny-related;
  - fundamental-discriminant check.
"""
from __future__ import annotations

import math


def build_qr_table(p: int) -> bytearray:
    """Quadratic-residue indicator table for F_p, O(p) time/space. Depends
    only on p, so callers scanning many (a, b) candidates at the same p
    build this ONCE and reuse it (point_count_with_qr)."""
    qr = bytearray(p)
    half = (p - 1) // 2
    for v in range(1, half + 1):
        qr[(v * v) % p] = 1
    return qr


def point_count_with_qr(p: int, a: int, b: int, qr: bytearray) -> int:
    total = 0
    for x in range(p):
        f = (x * x * x + a * x + b) % p
        if f == 0:
            continue
        total += 1 if qr[f] else -1
    return p + 1 + total


def point_count(p: int, a: int, b: int) -> int:
    """
    #E(F_p) for y^2 = x^3+ax+b via #E = p + 1 + sum_x chi(x^3+ax+b), where
    chi is the quadratic character mod p (chi(0)=0). O(p) time using a
    quadratic-residue sieve instead of per-element modular exponentiation.
    """
    qr = build_qr_table(p)
    return point_count_with_qr(p, a, b, qr)


def j_invariant(a: int, b: int, p: int) -> int:
    a %= p
    b %= p
    num = (1728 * 4 * pow(a, 3, p)) % p
    den = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
    if den == 0:
        raise ValueError("singular curve (discriminant 0)")
    return (num * pow(den, p - 2, p)) % p


def is_fundamental_discriminant(D: int) -> bool:
    """D < 0 assumed (imaginary quadratic order). Fundamental iff
    D == 1 mod 4 and squarefree, OR D = 4m with m == 2,3 mod 4 and m
    squarefree."""
    if D % 4 == 1:
        return _squarefree(abs(D))
    if D % 4 == 0:
        m = D // 4
        r = m % 4
        if r < 0:
            r += 4
        if r not in (2, 3):
            return False
        return _squarefree(abs(m))
    return False


def _squarefree(n: int) -> bool:
    n = abs(n)
    if n == 0:
        return False
    i = 2
    while i * i <= n:
        if n % (i * i) == 0:
            return False
        if n % i == 0:
            n //= i
        else:
            i += 1
    return True


def class_number(D: int) -> int:
    """
    h(D) for a negative discriminant D (D == 0 or 1 mod 4), via direct
    enumeration of reduced primitive positive-definite binary quadratic
    forms (a,b,c), b^2-4ac=D, with the reduction conditions
        -a < b <= a <= c   (and b >= 0 if a == c or a == b).
    This is Gauss's classical algorithm; independent of any isogeny code.
    """
    assert D < 0
    h = 0
    a_max = int(math.isqrt(abs(D) // 3)) + 1
    for a in range(1, a_max + 1):
        for b in range(-a + 1, a + 1):
            num = b * b - D
            if num % (4 * a) != 0:
                continue
            c = num // (4 * a)
            if c < a:
                continue
            if math.gcd(math.gcd(a, b), c) != 1:
                continue
            if a == c and b < 0:
                continue
            if a == b and c < a:
                continue
            h += 1
    return h


def legendre_int(a: int, p: int) -> int:
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else 1
