"""Minimal F_{2^n} arithmetic (polynomial basis) for Weil-descent experiments."""
import random

def deg(a):
    return a.bit_length() - 1

def clmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r

def pmod(a, f):
    df = deg(f)
    while a and deg(a) >= df:
        a ^= f << (deg(a) - df)
    return a

def pgcd(a, b):
    while b:
        a, b = b, pmod(a, b)
    return a

class Field:
    def __init__(self, n, f):
        self.n, self.f = n, f
        assert deg(f) == n
        assert is_irreducible(f), "modulus not irreducible"
    def mul(self, a, b):
        return pmod(clmul(a, b), self.f)
    def sq(self, a):
        return self.mul(a, a)
    def pow(self, a, e):
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.mul(a, a)
            e >>= 1
        return r
    def inv(self, a):
        assert a
        return self.pow(a, (1 << self.n) - 2)
    def trace(self, a):
        t, x = 0, a
        for _ in range(self.n):
            t ^= x
            x = self.sq(x)
        assert t in (0, 1)
        return t
    def halftrace(self, c):
        assert self.n % 2 == 1
        h, x = 0, c
        for _ in range((self.n - 1) // 2 + 1):
            h ^= x
            x = self.sq(self.sq(x))
        return h

def is_irreducible(f):
    n = deg(f)
    # Rabin: x^(2^n) = x mod f and gcd(x^(2^(n/p)) - x, f) = 1 for prime p | n
    def xpow2k(k):
        x = 2
        for _ in range(k):
            x = pmod(clmul(x, x), f)
        return x
    if xpow2k(n) != 2:
        return False
    for p in set(prime_factors(n)):
        if pgcd(f, xpow2k(n // p) ^ 2) != 1:
            return False
    return True

def prime_factors(n):
    out, p = [], 2
    while p * p <= n:
        while n % p == 0:
            out.append(p)
            n //= p
        p += 1
    if n > 1:
        out.append(n)
    return out

def find_modulus(n):
    """Lexicographically smallest irreducible trinomial, else pentanomial."""
    for k in range(1, n):
        f = (1 << n) | (1 << k) | 1
        if is_irreducible(f):
            return f
    for k3 in range(3, n):
        for k2 in range(2, k3):
            for k1 in range(1, k2):
                f = (1 << n) | (1 << k3) | (1 << k2) | (1 << k1) | 1
                if is_irreducible(f):
                    return f
    raise ValueError(n)
