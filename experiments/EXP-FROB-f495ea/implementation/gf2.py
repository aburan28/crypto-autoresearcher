#!/usr/bin/env python3
"""Minimal F_2[t]/(f) arithmetic for EXP-FROB-f495ea Stages 0-1.

Self-contained (no numpy). Used for point counts of Artin-Schreier curves
y^2 + y = f(x) over F_{2^k}, k <= 6. No Magma/Sage/AUXIN/Bedrock.
"""
from __future__ import annotations


def clmul(a: int, b: int) -> int:
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pmod(a: int, m: int) -> int:
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


def pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, pmod(a, b)
    return a


def is_irreducible(mod: int) -> bool:
    n = mod.bit_length() - 1
    x = 2
    cur = x
    for i in range(1, n + 1):
        cur = pmod(clmul(cur, cur), mod)
        if i <= n // 2 and pgcd(mod, cur ^ x) != 1:
            return False
    return cur == x


# Frozen irreducible polynomials for F_{2^k}, k=1..6 (bit j = coeff of t^j).
# k=1: F_2 itself, modulus unused (n=1 special-cased).
MODULI: dict[int, int] = {
    1: 0b11,  # t + 1 (F_2 as F_2[t]/(t+1) is degenerate; use n=1 direct)
    2: 0b111,  # t^2 + t + 1
    3: 0b1011,  # t^3 + t + 1
    4: 0b10011,  # t^4 + t + 1
    5: 0b100101,  # t^5 + t^2 + 1
    6: 0b1000011,  # t^6 + t + 1
}


class Field:
    """Elements are Python ints; bit j is the coefficient of t^j."""

    def __init__(self, n: int):
        if n < 1 or n > 6:
            raise ValueError(f"unsupported extension degree {n}")
        self.n = n
        if n == 1:
            self.mod = 0
        else:
            self.mod = MODULI[n]
            if not is_irreducible(self.mod):
                raise ValueError(f"modulus not irreducible: {self.mod:#x}")

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        if self.n == 1:
            return (a & 1) & (b & 1)
        mask = (1 << self.n) - 1
        return pmod(clmul(a & mask, b & mask), self.mod)

    def square(self, a: int) -> int:
        return self.mul(a, a)

    def trace(self, a: int) -> int:
        """Absolute trace F_{2^n} -> F_2."""
        if self.n == 1:
            return a & 1
        s = 0
        x = a & ((1 << self.n) - 1)
        for _ in range(self.n):
            s ^= x & 1
            x = self.square(x)
        return s & 1


def eval_poly_f2(coeffs: int, x: int, field: Field) -> int:
    """Evaluate polynomial with F_2 coefficients (bit i = coeff of x^i) at x in field."""
    r = 0
    # Horner from high degree
    deg = coeffs.bit_length() - 1
    for i in range(deg, -1, -1):
        r = field.mul(r, x)
        if (coeffs >> i) & 1:
            r ^= 1
    return r


def poly_add(a: int, b: int) -> int:
    return a ^ b


def poly_compose_x_plus_b(f: int, b: int) -> int:
    """Return f(x+b) for f in F_2[x], b in {0,1} (only F_2 translations used in normal form)."""
    if b == 0:
        return f
    # f(x+1): expand via binomial; over F_2, (x+1)^k = sum_{j<=k} C(k,j) x^j with C mod 2 = Lucas
    out = 0
    deg = f.bit_length() - 1
    for k in range(deg + 1):
        if (f >> k) & 1:
            # (x+1)^k
            term = 0
            for j in range(k + 1):
                if bin(k & j).count("1") == bin(j).count("1"):  # Lucas: C(k,j) odd iff j subset k
                    # Actually Lucas for p=2: C(k,j) odd iff (j & k) == j
                    if (j & k) == j:
                        term ^= 1 << j
            out ^= term
    return out


def as_add_h2_h(f: int, h: int) -> int:
    """f + h^2 + h in F_2[x]."""
    # h^2: if h = sum h_i x^i then h^2 = sum h_i x^{2i}
    h2 = 0
    i = 0
    tmp = h
    while tmp:
        if tmp & 1:
            h2 ^= 1 << (2 * i)
        tmp >>= 1
        i += 1
    return f ^ h2 ^ h


def poly_degree(f: int) -> int:
    return -1 if f == 0 else f.bit_length() - 1


def is_monic_degree(f: int, d: int) -> bool:
    return poly_degree(f) == d and ((f >> d) & 1) == 1
