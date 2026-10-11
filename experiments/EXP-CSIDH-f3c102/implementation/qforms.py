#!/usr/bin/env python3
"""Quadratic-form machinery for EXP-CSIDH-f3c102.

Self-contained classical library: fundamental-discriminant check, the two
frozen form enumerations (E1 direct reduced listing, E2 box enumeration
plus Gauss reduction), and two independent Kronecker-symbol
implementations that the run and the self-test cross-check. Exact rational
arithmetic only (fractions.Fraction); no floating point anywhere.
"""
from __future__ import annotations

from fractions import Fraction
from math import gcd, isqrt


def is_fundamental(disc: int) -> bool:
    """Fundamental discriminant: D ≡ 1 (mod 4) squarefree, or D = 4m with
    m ≡ 2 or 3 (mod 4) squarefree."""
    if disc >= 0:
        return False
    if disc % 4 == 1:
        n = -disc
        for p in range(2, isqrt(n) + 1):
            if n % (p * p) == 0:
                return False
        return True
    if disc % 4 == 0:
        m = disc // 4
        n = abs(m)
        for p in range(2, isqrt(n) + 1):
            if n % (p * p) == 0:
                return False
        return m % 4 in (2, 3)
    return False


def _squarefree(n: int) -> bool:
    for p in range(2, isqrt(n) + 1):
        if n % (p * p) == 0:
            return False
    return True


def is_reduced(a: int, b: int, c: int) -> bool:
    if not (-a < b <= a <= c):
        return False
    if (abs(b) == a or a == c) and b < 0:
        return False
    return True


def gauss_reduce(a: int, b: int, c: int, disc: int) -> tuple[int, int, int]:
    """Gauss reduction of a primitive positive-definite form."""
    for _ in range(64):
        if is_reduced(a, b, c):
            return a, b, c
        r = b % (2 * a)
        if r > a:
            r -= 2 * a
        b = r
        c = (b * b - disc) // (4 * a)
        if a > c:
            a, c = c, a
            b = -b
        if a == c and b < 0:
            b = -b
    raise ValueError("gauss_reduce did not terminate")


def enumerate_reduced(disc: int) -> list[tuple[int, int, int]]:
    """E1: the direct reduced-form listing under the frozen convention."""
    if disc >= 0:
        raise ValueError("discriminant must be negative")
    out: list[tuple[int, int, int]] = []
    a = 1
    while a * a <= -disc // 3 + 1:
        for b in range(-a + 1, a + 1):
            num = b * b - disc
            if num % (4 * a):
                continue
            c = num // (4 * a)
            if c < a:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            out.append((a, b, c))
        a += 1
    out.sort()
    return out


def enumerate_orbits(disc: int, a_max: int, c_max: int) -> set[tuple[int, int, int]]:
    """E2: box enumeration plus Gauss reduction, deduplicated.

    Every primitive positive-definite form (a, b, c) of the given
    discriminant with 0 < a <= a_max, 0 <= b <= a, 0 < c <= c_max is
    reduced; the set of reduced representatives is the class set.
    """
    reps: set[tuple[int, int, int]] = set()
    for a in range(1, a_max + 1):
        for b in range(0, a + 1):
            num = b * b - disc
            if num % (4 * a):
                continue
            c = num // (4 * a)
            if c <= 0 or c > c_max:
                continue
            if gcd(gcd(a, b), c) != 1:
                raise ValueError(f"imprimitive form in box: {(a, b, c)}")
            reps.add(gauss_reduce(a, b, c, disc))
    return reps


def _jacobi_odd(a: int, n: int) -> int:
    """Jacobi symbol (a/n) for odd positive n; a any integer."""
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


def kronecker(d: int, n: int) -> int:
    """Kronecker symbol (d/n), first implementation: sign/2-part split
    plus quadratic reciprocity (Jacobi) on the odd part."""
    if n == 1:
        return 1
    if n <= 0:
        raise ValueError("n must be positive")
    result = 1
    m = n
    while m % 2 == 0:
        m //= 2
    if m > 1 and d < 0 and m % 4 == 3:
        result = -result  # (-1/n) = -1 iff n = 3 mod 4
    e = 0
    m = n
    while m % 2 == 0:
        m //= 2
        e += 1
    if e:
        if d % 2 == 0:
            return 0
        r = d % 8
        result *= (1 if r in (1, 7) else -1) ** e
    if m > 1:
        result *= _jacobi_odd(abs(d), m)
    return result


def kronecker_euler(d: int, n: int) -> int:
    """Second implementation: factor n, Euler's criterion per odd prime."""
    if n == 1:
        return 1
    result = 1
    m = n
    factors: list[tuple[int, int]] = []
    p = 2
    while p * p <= m:
        e = 0
        while m % p == 0:
            m //= p
            e += 1
        if e:
            factors.append((p, e))
        p += 1
    if m > 1:
        factors.append((m, 1))
    for (p, e) in factors:
        if p == 2:
            r = d % 8
            sym = 1 if r in (1, 7) else (-1 if r in (3, 5) else 0)
        else:
            r = d % p
            if r == 0:
                sym = 0
            else:
                x = pow(r % p, (p - 1) // 2, p)
                sym = 1 if x == 1 else -1
        for _ in range(e):
            result *= sym
            if sym == 0:
                return 0
    return result


def sqrt_rational_bounds(x: int, digits: int) -> tuple[Fraction, Fraction]:
    """Exact rational enclosure lo < sqrt(x) < hi at 10^-digits width."""
    scale = 10 ** digits
    s = isqrt(x * scale * scale)
    lo = Fraction(s, scale)
    hi = Fraction(s + 1, scale)
    if lo * lo >= x:
        lo = Fraction(s - 1, scale)
    if hi * hi <= x:
        hi = Fraction(s + 2, scale)
    return lo, hi


PI_LOW = Fraction(333, 106)
PI_HIGH = Fraction(355, 113)
PI_PROVENANCE = (
    "333/106 < pi < 355/113: classical continued-fraction convergents of "
    "pi (convergents of [3; 7, 15, 1, 292, ...]); 333/106 is below and "
    "355/113 above pi. Frozen as instrument constants by "
    "EXP-CSIDH-f3c102; not retightened after seeing any interval."
)


def interval_mul(x: tuple[Fraction, Fraction], y: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    products = [x[0] * y[0], x[0] * y[1], x[1] * y[0], x[1] * y[1]]
    return min(products), max(products)


def interval_scale(x: tuple[Fraction, Fraction], k: Fraction) -> tuple[Fraction, Fraction]:
    if k == 0:
        return Fraction(0), Fraction(0)
    products = [x[0] * k, x[1] * k]
    return min(products), max(products)


def nearest_integer_gates(lo: Fraction, hi: Fraction) -> tuple[str, int | None]:
    """Apply the frozen interval gates.

    Returns (status, r). r is the unique integer NEAREST TO EVERY POINT of
    the interval (the idea's wording), not an integer contained in it: r
    is the integer k with k - 1/2 < lo and hi < k + 1/2. Status is one of
    {"ok", "too_long", "two_integers", "half_integer", "inconsistent"}.
    """
    half = Fraction(1, 2)
    if hi - lo >= half:
        return "too_long", None
    # defensive: with length below 1/2 the interval contains at most one
    # integer; two would contradict the length gate.
    r1 = -((-lo.numerator) // lo.denominator)  # ceil(lo)
    r2 = hi.numerator // hi.denominator          # floor(hi)
    if r1 < r2:
        return "two_integers", None
    # half-integer met: some k + 1/2 in [lo, hi]
    two_lo = 2 * lo
    two_hi = 2 * hi
    k1 = -((-two_lo.numerator) // two_lo.denominator)  # ceil(2 lo)
    k2 = two_hi.numerator // two_hi.denominator          # floor(2 hi)
    for k in range(k1, k2 + 1):
        if k % 2 == 1:
            return "half_integer", None
    # the nearest integer to every point of the interval
    import math
    r = math.floor(lo + half)
    if not (r - half < lo and hi < r + half):
        return "inconsistent", None
    return "ok", r
