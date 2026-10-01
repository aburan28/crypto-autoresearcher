"""F_{2^n} field arithmetic for EXP-QSP-70b731.

Elements are bit-packed ints of width n (bit i = coefficient of z^i).
Default n=131 uses the ECC2K-130 reduction polynomial
z^131 + z^13 + z^2 + z + 1 from the approved contract.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import gf2_poly as gp


# Irreducible moduli (bit-packed). Verified small-n choices are standard;
# n=131 is the contract field polynomial.
_DEFAULT_MODULI: Dict[int, int] = {
    4: 0b10011,  # z^4 + z + 1
    7: 0b10000011,  # z^7 + z + 1
    11: 0b100000000101,  # z^11 + z^2 + 1
    12: 0b1000000011001,  # z^12 + z^3 + 1? check: use z^12+z^6+z^4+z+1 common
    13: 0b10000000011011,  # z^13 + z^4 + z^3 + z + 1
    31: (1 << 31) | (1 << 3) | 1,  # z^31 + z^3 + 1
    131: (1 << 131) | (1 << 13) | (1 << 2) | (1 << 1) | 1,
}

# Fix n=12: z^12 + z^3 + 1 = bits 12,3,0
_DEFAULT_MODULI[12] = (1 << 12) | (1 << 3) | 1


@dataclass(frozen=True)
class FieldF2n:
    n: int
    modulus: int

    @staticmethod
    def for_n(n: int, modulus: Optional[int] = None) -> "FieldF2n":
        if modulus is None:
            if n not in _DEFAULT_MODULI:
                raise ValueError(f"no default irreducible for n={n}")
            modulus = _DEFAULT_MODULI[n]
        if gp.degree(modulus) != n:
            raise ValueError("modulus degree must equal n")
        return FieldF2n(n=n, modulus=modulus)

    def add(self, a: int, b: int) -> int:
        return (a ^ b) & ((1 << self.n) - 1) if self.n < 512 else (a ^ b)

    def mul(self, a: int, b: int) -> int:
        return gp.mod(gp.mul(a & mask(self.n), b & mask(self.n)), self.modulus)

    def square(self, a: int) -> int:
        return gp.mod(gp.square(a & mask(self.n)), self.modulus)

    def pow(self, a: int, e: int) -> int:
        res = 1
        base = a & mask(self.n)
        while e > 0:
            if e & 1:
                res = self.mul(res, base)
            base = self.square(base)
            e >>= 1
        return res

    def frobenius(self, a: int, k: int = 1) -> int:
        """a |-> a^{2^k}."""
        for _ in range(k):
            a = self.square(a)
        return a

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("inv(0)")
        # a^{2^n - 2} = a^{-1}
        return self.pow(a, (1 << self.n) - 2)

    def eval_f2_poly(self, poly: int, x: int) -> int:
        """Evaluate GF(2)-coefficient poly at field element x."""
        acc = 0
        d = gp.degree(poly)
        for i in range(d, -1, -1):
            acc = self.mul(acc, x)
            if (poly >> i) & 1:
                acc ^= 1
        return acc

    def all_elements(self):
        if self.n > 20:
            raise ValueError("full enumeration only for n <= 20")
        for i in range(1 << self.n):
            yield i


def mask(n: int) -> int:
    return (1 << n) - 1


def is_irreducible_f2(mod: int, n: int) -> bool:
    """Rabin irreducibility test over F_2."""
    if gp.degree(mod) != n:
        return False
    # X^{2^n} ≡ X mod mod
    x = gp.monomial(1)
    for _ in range(n):
        x = gp.mod(gp.square(x), mod)
    if x != gp.monomial(1):
        return False
    # For prime n, also check gcd(mod, X^{2^{n/p}} - X) = 1 for prime factors p of n
    # Full Rabin: for each prime p|n, gcd(mod, X^{(2^n-1)/p} - 1) = 1 — use distinct-degree form:
    from math import isqrt

    primes = _prime_factors(n)
    for p in primes:
        # gcd(mod, X^{2^{n/p}} - X) should be 1
        xp = gp.monomial(1)
        for _ in range(n // p):
            xp = gp.mod(gp.square(xp), mod)
        g = gp.gcd(mod, xp ^ gp.monomial(1))
        if gp.degree(g) > 0:
            return False
    return True


def _prime_factors(n: int) -> List[int]:
    factors = []
    d = 2
    nn = n
    while d * d <= nn:
        if nn % d == 0:
            factors.append(d)
            while nn % d == 0:
                nn //= d
        d += 1
    if nn > 1:
        factors.append(nn)
    return factors
