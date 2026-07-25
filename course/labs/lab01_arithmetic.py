#!/usr/bin/env python3
"""
Lab 01 — Integer and modular arithmetic.

Companion to course modules 01 (modular arithmetic) and 04 (number theory
toolkit). Pure standard library; run it directly:

    python3 lab01_arithmetic.py

Everything downstream in this course (finite fields, curves, isogenies) is
built from the handful of primitives in this file: extended gcd, modular
inverse, fast exponentiation, CRT, Legendre symbols, and modular square
roots (Tonelli-Shanks).

EXERCISES are marked inline: try them after reading the matching module.
"""

from __future__ import annotations


# ----------------------------------------------------------------------
# Extended Euclid and modular inverses (module 01)
# ----------------------------------------------------------------------

def xgcd(a: int, b: int) -> tuple[int, int, int]:
    """Return (g, x, y) with a*x + b*y = g = gcd(a, b).

    Iterative extended Euclidean algorithm. Bezout's identity in code:
    the certificate (x, y) is what makes modular inversion possible.
    """
    old_r, r = a, b
    old_x, x = 1, 0
    old_y, y = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_x, x = x, old_x - q * x
        old_y, y = y, old_y - q * y
    # Normalise so the gcd is non-negative.
    if old_r < 0:
        old_r, old_x, old_y = -old_r, -old_x, -old_y
    return old_r, old_x, old_y


def modinv(a: int, n: int) -> int:
    """Inverse of a modulo n. Raises ValueError if gcd(a, n) != 1."""
    g, x, _ = xgcd(a % n, n)
    if g != 1:
        raise ValueError(f"{a} is not invertible mod {n} (gcd={g})")
    return x % n


def fast_pow(a: int, e: int, n: int) -> int:
    """Square-and-multiply. Same as Python's pow(a, e, n); written out
    because the identical loop reappears as scalar multiplication on
    elliptic curves (lab 03) — same algorithm, different group."""
    if e < 0:
        return fast_pow(modinv(a, n), -e, n)
    result = 1
    a %= n
    while e:
        if e & 1:
            result = result * a % n
        a = a * a % n
        e >>= 1
    return result


# ----------------------------------------------------------------------
# Chinese Remainder Theorem (module 04)
# ----------------------------------------------------------------------

def crt(residues: list[int], moduli: list[int]) -> int:
    """Solve x = r_i (mod n_i) for pairwise-coprime moduli.

    Returns the unique solution modulo the product of the moduli.
    CRT is the workhorse behind Pohlig-Hellman (lab 04) and Schoof's
    point-counting algorithm (module 07).
    """
    if len(residues) != len(moduli):
        raise ValueError("length mismatch")
    x, n = 0, 1
    for r_i, n_i in zip(residues, moduli):
        g, u, v = xgcd(n, n_i)
        if g != 1:
            raise ValueError("moduli must be pairwise coprime")
        # u*n + v*n_i = 1; the new solution agrees with x mod n and r_i mod n_i.
        x = (x * v * n_i + r_i * u * n) % (n * n_i)
        n *= n_i
    return x


# ----------------------------------------------------------------------
# Primality (Miller-Rabin, deterministic for our sizes)
# ----------------------------------------------------------------------

_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_probable_prime(n: int) -> bool:
    """Miller-Rabin with a fixed base set that is deterministic for
    n < 3.3 * 10^24 — far beyond anything in this course."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
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


def factorize(n: int) -> dict[int, int]:
    """Trial-division factorisation (fine for course-sized numbers).
    Returns {prime: exponent}."""
    factors: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def euler_phi(n: int) -> int:
    """Euler's totient via the factorisation of n."""
    result = n
    for p in factorize(n):
        result = result // p * (p - 1)
    return result


# ----------------------------------------------------------------------
# Quadratic residues and modular square roots (module 04)
# ----------------------------------------------------------------------

def legendre(a: int, p: int) -> int:
    """Legendre symbol (a/p) for odd prime p: 1 if a is a nonzero square
    mod p, -1 if a is a non-square, 0 if p | a. Euler's criterion:
    (a/p) = a^((p-1)/2) mod p."""
    a %= p
    if a == 0:
        return 0
    t = pow(a, (p - 1) // 2, p)
    return 1 if t == 1 else -1


def sqrt_mod_p(a: int, p: int) -> int | None:
    """A square root of a modulo odd prime p, or None if a is a non-square.

    Uses the p = 3 (mod 4) shortcut when available, otherwise full
    Tonelli-Shanks. The other root is p - r.
    """
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        # a^((p+1)/4) squares to a^((p+1)/2) = a * a^((p-1)/2) = a.
        return pow(a, (p + 1) // 4, p)
    # Tonelli-Shanks: write p - 1 = q * 2^s with q odd.
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # Any quadratic non-residue will do as the "progress" element.
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q + 1) // 2, p)
    while t != 1:
        # Find least 0 < i < m with t^(2^i) = 1.
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = b * b % p
        t = t * c % p
        r = r * b % p
    return r


# ----------------------------------------------------------------------
# Self-checks and demo
# ----------------------------------------------------------------------

def _selfcheck() -> None:
    import random
    rng = random.Random(1)

    for _ in range(200):
        a, b = rng.randrange(-10**6, 10**6), rng.randrange(-10**6, 10**6)
        g, x, y = xgcd(a, b)
        assert a * x + b * y == g
        assert g >= 0

    for p in (5, 101, 431, 1009, 2**31 - 1):
        for _ in range(50):
            a = rng.randrange(1, p)
            assert a * modinv(a, p) % p == 1
            e = rng.randrange(0, 10**6)
            assert fast_pow(a, e, p) == pow(a, e, p)
            # Fermat's little theorem.
            assert pow(a, p - 1, p) == 1

    assert crt([2, 3, 2], [3, 5, 7]) == 23  # Sunzi's classic example
    for _ in range(50):
        mods = [3, 5, 7, 11, 13]
        rs = [rng.randrange(m) for m in mods]
        x = crt(rs, mods)
        assert all(x % m == r for r, m in zip(rs, mods))

    assert [n for n in range(2, 30) if is_probable_prime(n)] == \
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert factorize(2**5 * 3**2 * 431) == {2: 5, 3: 2, 431: 1}
    assert euler_phi(12) == 4 and euler_phi(431) == 430

    for p in (11, 13, 431, 1009, 10007):  # both p mod 4 classes
        squares = {pow(x, 2, p) for x in range(1, p)}
        for a in range(1, min(p, 60)):
            ls = legendre(a, p)
            assert ls == (1 if a in squares else -1)
            r = sqrt_mod_p(a, p)
            if ls == 1:
                assert r is not None and r * r % p == a % p
            else:
                assert r is None
    print("lab01: all self-checks passed")


def _demo() -> None:
    p = 431
    print(f"\n-- demo: arithmetic mod p = {p} --")
    g, x, y = xgcd(240, 46)
    print(f"xgcd(240, 46) = {g} with 240*({x}) + 46*({y}) = {240*x+46*y}")
    print(f"modinv(7, {p})  = {modinv(7, p)}  (check: 7*{modinv(7, p)} mod {p} = {7*modinv(7,p)%p})")
    print(f"2^430 mod 431  = {fast_pow(2, 430, 431)}  (Fermat)")
    print(f"crt([2,3,2],[3,5,7]) = {crt([2,3,2],[3,5,7])}")
    print(f"legendre(2, {p}) = {legendre(2, p)}, legendre(3, {p}) = {legendre(3, p)}")
    r = sqrt_mod_p(2, p)
    print(f"sqrt(2) mod {p} = {r}  (check: {r}^2 mod {p} = {r*r%p})")
    # EXERCISE 1.1: find all p < 100 for which -1 is a square mod p and
    #   compare with p mod 4 (module 04 explains what you should see).
    # EXERCISE 1.2: time fast_pow vs naive repeated multiplication for a
    #   1024-bit exponent and explain the growth rates.


if __name__ == "__main__":
    _selfcheck()
    _demo()
