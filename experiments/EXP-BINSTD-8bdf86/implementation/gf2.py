#!/usr/bin/env python3
"""Minimal stdlib F_{2^n} + Koblitz helpers for EXP-BINSTD-8bdf86.

Pure Python. No NumPy. No Magma/Sage/AUXIN/Bedrock.
Irreducible: t^17 + t^3 + 1 (same pin as EXP-BINSTD-a3cfee toys).
"""
from __future__ import annotations

from typing import List, Optional, Tuple

Point = Optional[Tuple[int, int]]

MODULI = {
    17: (1 << 17) | (1 << 3) | 1,  # t^17 + t^3 + 1
}


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


class Field:
    def __init__(self, n: int, mod: int):
        self.n = n
        self.mod = mod
        self.q = 1 << n

    def mul(self, a: int, b: int) -> int:
        return pmod(clmul(a, b), self.mod)

    def sqr(self, a: int) -> int:
        return self.mul(a, a)

    def inv(self, a: int) -> int:
        if a == 0:
            raise ZeroDivisionError("inv(0)")
        # a^{2^n - 2} via binary exponentiation
        return self.pow(a, self.q - 2)

    def pow(self, a: int, e: int) -> int:
        r = 1
        while e:
            if e & 1:
                r = self.mul(r, a)
            a = self.sqr(a)
            e >>= 1
        return r

    def trace(self, a: int) -> int:
        # Tr_{F_{2^n}/F_2}(a) = sum_{i=0}^{n-1} a^{2^i}
        s = a
        x = a
        for _ in range(self.n - 1):
            x = self.sqr(x)
            s ^= x
        return s & 1

    def half_trace(self, a: int) -> int:
        # For odd n: H(a) = sum_{i=0}^{(n-1)/2} a^{2^{2i}}
        if self.n % 2 == 0:
            raise ValueError("half_trace requires odd n")
        s = a
        x = a
        for _ in range((self.n - 1) // 2):
            x = self.sqr(self.sqr(x))
            s ^= x
        return s


def make_field(n: int) -> Field:
    if n not in MODULI:
        raise KeyError(f"no modulus pin for n={n}")
    return Field(n, MODULI[n])


class Curve:
    """Y^2 + XY = X^3 + A X^2 + B over Field (A=0, B=1 Koblitz analog)."""

    def __init__(self, F: Field, A: int = 0, B: int = 1):
        if B == 0:
            raise ValueError("B must be nonzero")
        self.F = F
        self.A = A
        self.B = B

    def neg(self, P: Point) -> Point:
        if P is None:
            return None
        return (P[0], P[0] ^ P[1])

    def add(self, P: Point, Q: Point) -> Point:
        F = self.F
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if y2 == (x1 ^ y1):
                return None
            # double
            if x1 == 0:
                return None
            lam = x1 ^ F.mul(y1, F.inv(x1))
            x3 = F.mul(lam, lam) ^ lam ^ self.A
            y3 = F.mul(x1, x1) ^ F.mul(lam ^ 1, x3)
            return (x3, y3)
        dx = x1 ^ x2
        lam = F.mul(y1 ^ y2, F.inv(dx))
        x3 = F.mul(lam, lam) ^ lam ^ x1 ^ x2 ^ self.A
        y3 = F.mul(lam, x1 ^ x3) ^ x3 ^ y1
        return (x3, y3)

    def rhs_c(self, x: int) -> int:
        F = self.F
        return x ^ self.A ^ F.mul(self.B, F.inv(F.mul(x, x)))

    def lift_x(self, x: int) -> Point:
        F = self.F
        if x == 0:
            # y^2 = B; for B=1, y=1
            return (0, 1)
        c = self.rhs_c(x)
        if F.trace(c) != 0:
            return None
        z = F.half_trace(c)
        return (x, F.mul(x, z))

    def frobenius_point(self, P: Point) -> Point:
        if P is None:
            return None
        F = self.F
        return (F.sqr(P[0]), F.sqr(P[1]))


def bit_rank(rows: List[int], n: int) -> int:
    mat = rows[:]
    rank = 0
    for col in range(n):
        pivot = None
        for r in range(rank, len(mat)):
            if (mat[r] >> col) & 1:
                pivot = r
                break
        if pivot is None:
            continue
        mat[rank], mat[pivot] = mat[pivot], mat[rank]
        for r in range(len(mat)):
            if r != rank and (mat[r] >> col) & 1:
                mat[r] ^= mat[rank]
        rank += 1
    return rank


def span_dim(gens: List[int], n: int) -> int:
    return bit_rank([g for g in gens if g], n)


def saturate_under_frobenius(F: Field, gens: List[int]) -> List[int]:
    """Return a spanning set for the τ-closure of span(gens), τ: x↦x²."""
    closed = list(gens)
    changed = True
    while changed:
        changed = False
        for g in list(closed):
            sg = F.sqr(g)
            if span_dim(closed + [sg], F.n) > span_dim(closed, F.n):
                closed.append(sg)
                changed = True
    return closed


def random_subspace_gens(rng, n: int, ell: int) -> List[int]:
    gens: List[int] = []
    while span_dim(gens, n) < ell:
        v = rng.randrange(1, 1 << n)
        if span_dim(gens + [v], n) > span_dim(gens, n):
            gens.append(v)
    return gens


def enumerate_subspace(gens: List[int], n: int) -> List[int]:
    """All elements of span(gens) as bitmasks (ints)."""
    # Reduce gens to a basis
    basis: List[int] = []
    for g in gens:
        if span_dim(basis + [g], n) > span_dim(basis, n):
            basis.append(g)
    out = [0]
    for b in basis:
        out.extend([x ^ b for x in out])
    return out


def is_tau_closed(F: Field, gens: List[int]) -> bool:
    d = span_dim(gens, F.n)
    return span_dim(saturate_under_frobenius(F, gens), F.n) == d
