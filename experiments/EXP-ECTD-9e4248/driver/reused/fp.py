"""
fp.py -- prime field F_p arithmetic primitives for EXP-ECTD-001.

Pure Python standard library only. No SageMath, no external CAS at runtime.
All curve/isogeny/Semaev code in this driver is built on top of this module.
"""
import random


def inv(a, p):
    """Modular inverse of a mod p (p prime). Raises ZeroDivisionError if a%p==0."""
    a %= p
    if a == 0:
        raise ZeroDivisionError("inverse of 0 mod p")
    return pow(a, p - 2, p)


def legendre(a, p):
    """Legendre symbol (a/p) in {-1,0,1} for odd prime p."""
    a %= p
    if a == 0:
        return 0
    r = pow(a, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


def is_qr(a, p):
    return legendre(a, p) == 1


def sqrt_mod(a, p):
    """Tonelli-Shanks: return one square root of a mod p (odd prime p), or None if non-residue."""
    a %= p
    if a == 0:
        return 0
    if legendre(a, p) != 1:
        return None
    if p % 4 == 3:
        r = pow(a, (p + 1) // 4, p)
        return r
    # General Tonelli-Shanks
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    # find a quadratic non-residue z
    z = 2
    while legendre(z, p) != -1:
        z += 1
    m = s
    c = pow(z, q, p)
    t = pow(a, q, p)
    r = pow(a, (q + 1) // 2, p)
    while t != 1:
        # find least i, 0<i<m, such that t^(2^i)=1
        i = 0
        t2i = t
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
            if i == m:
                return None  # shouldn't happen if a is a genuine QR
        b = pow(c, 1 << (m - i - 1), p)
        m = i
        c = (b * b) % p
        t = (t * c) % p
        r = (r * b) % p
    return r


def is_probable_prime(n, rounds=40, rng=None):
    """Deterministic-enough Miller-Rabin primality test for our toy scale (<= ~60 bits).
    Uses fixed witness bases known to be deterministic for n < 3,317,044,064,679,887,385,961,981
    (~ 2^81), which covers our full 40-56 bit range with certainty (not merely probabilistic).
    """
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for sp in small_primes:
        if n == sp:
            return True
        if n % sp == 0:
            return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    # deterministic witness set for n < 3.3*10^24
    witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for a in witnesses:
        if a >= n:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(r - 1):
            x = (x * x) % n
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True


def random_prime(bits, rng):
    """Random probable prime with exactly `bits` bits, using is_probable_prime (deterministic
    witness set for our size range)."""
    lo = 1 << (bits - 1)
    hi = (1 << bits) - 1
    while True:
        cand = rng.randint(lo, hi) | 1
        if is_probable_prime(cand):
            return cand
