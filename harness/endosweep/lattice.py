"""Exact relation lattices and scalar decomposition (dependency-free LLL).

Given endomorphisms phi_1..phi_d acting on a cyclic group of prime order n as
scalars lambda_1..lambda_d (lambda_1 = 1 for the identity), the relation
lattice is

    L = { v in Z^d : sum_i v_i * lambda_i = 0 (mod n) },

of determinant n.  Writing k = sum_i k_i lambda_i (mod n) with every |k_i|
small is the same as finding a lattice vector close to (k, 0, ..., 0); Babai
rounding against an LLL-reduced basis gives |k_i| <= sum_j ||b_j||_inf / 2,
and that bound is a theorem about the basis, not a heuristic.

Everything is exact (Python integers and Fractions); dimensions here are at
most a dozen, so speed is irrelevant and auditability is not.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence


Vector = list[int]


def _dot(u: Sequence, v: Sequence):
    return sum(a * b for a, b in zip(u, v))


def lll(basis: Sequence[Sequence[int]], delta: Fraction = Fraction(99, 100)) -> list[Vector]:
    """Textbook LLL (Lenstra-Lenstra-Lovasz) over exact rationals."""
    B = [list(map(int, row)) for row in basis]
    n = len(B)
    if n == 0:
        return []

    def gram_schmidt():
        Bs: list[list[Fraction]] = []
        mu: list[list[Fraction]] = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):
            v = [Fraction(x) for x in B[i]]
            for j in range(i):
                denom = _dot(Bs[j], Bs[j])
                mu[i][j] = Fraction(_dot(B[i], Bs[j]), 1) / denom if denom else Fraction(0)
                v = [a - mu[i][j] * b for a, b in zip(v, Bs[j])]
            Bs.append(v)
        return Bs, mu

    Bs, mu = gram_schmidt()
    k = 1
    while k < n:
        for j in range(k - 1, -1, -1):
            q = round(mu[k][j])
            if q:
                B[k] = [a - q * b for a, b in zip(B[k], B[j])]
                Bs, mu = gram_schmidt()
        lhs = _dot(Bs[k], Bs[k])
        rhs = (delta - mu[k][k - 1] ** 2) * _dot(Bs[k - 1], Bs[k - 1])
        if lhs >= rhs:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            Bs, mu = gram_schmidt()
            k = max(k - 1, 1)
    return B


def relation_lattice_basis(lams: Sequence[int], n: int) -> list[Vector]:
    """A basis of {v : sum v_i lam_i = 0 mod n}; lams[0] must be 1."""
    lams = [x % n for x in lams]
    if lams[0] != 1:
        raise ValueError("the first generator must be the identity (eigenvalue 1)")
    d = len(lams)
    rows: list[Vector] = [[n] + [0] * (d - 1)]
    for i in range(1, d):
        row = [0] * d
        row[0] = (-lams[i]) % n
        row[i] = 1
        rows.append(row)
    return rows


def inf_norm(v: Sequence[int]) -> int:
    return max(abs(x) for x in v)


def l2_norm_sq(v: Sequence[int]) -> int:
    return sum(x * x for x in v)


@dataclass
class ReducedLattice:
    lams: list[int]
    n: int
    basis: list[Vector]              # LLL-reduced
    _inv: list[list[Fraction]] | None = None

    @property
    def dim(self) -> int:
        return len(self.lams)

    @property
    def babai_bound(self) -> int:
        """Provable bound on every decomposition coefficient (sum of half inf-norms)."""
        return sum(inf_norm(b) for b in self.basis) // 2 + 1

    @property
    def max_basis_inf_norm(self) -> int:
        return max(inf_norm(b) for b in self.basis)

    def _inverse(self) -> list[list[Fraction]]:
        if self._inv is None:
            self._inv = _invert(self.basis)
        return self._inv

    def decompose(self, k: int) -> list[int]:
        """k_1..k_d with sum k_i lam_i = k (mod n) and |k_i| <= babai_bound."""
        d = self.dim
        target = [Fraction(k % self.n)] + [Fraction(0)] * (d - 1)
        inv = self._inverse()
        coords = [sum(target[j] * inv[j][i] for j in range(d)) for i in range(d)]
        rounded = [round(c) for c in coords]
        v = [k % self.n] + [0] * (d - 1)
        for r, b in zip(rounded, self.basis):
            if r:
                v = [a - r * c for a, c in zip(v, b)]
        assert (sum(x * l for x, l in zip(v, self.lams)) - k) % self.n == 0
        return v


def _invert(M: Sequence[Sequence[int]]) -> list[list[Fraction]]:
    n = len(M)
    A = [[Fraction(x) for x in row] + [Fraction(int(i == j)) for j in range(n)]
         for i, row in enumerate(M)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        pv = A[col][col]
        A[col] = [x / pv for x in A[col]]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return [row[n:] for row in A]


def reduce(lams: Sequence[int], n: int) -> ReducedLattice:
    basis = lll(relation_lattice_basis(lams, n))
    basis.sort(key=l2_norm_sq)
    return ReducedLattice(list(x % n for x in lams), n, basis)


def coefficient_bits(red: ReducedLattice, samples: int = 64, seed: int = 1) -> dict:
    """Provable and empirical coefficient sizes for a reduced lattice.

    ``bound_bits`` is the Babai bound (a theorem); ``empirical_max_bits`` is
    the largest |k_i| over ``samples`` pseudo-random scalars (a measurement).
    ``balanced_bits`` = log2(n)/d is the ideal every coefficient would have
    if the lattice were perfectly balanced; the gap to it is what the sweeper
    reports as decomposition loss.
    """
    import random
    rng = random.Random(seed)
    worst = 0
    for _ in range(samples):
        k = rng.randrange(1, red.n)
        worst = max(worst, inf_norm(red.decompose(k)))
    return {
        "dim": red.dim,
        "bound_bits": red.babai_bound.bit_length(),
        "empirical_max_bits": worst.bit_length(),
        "balanced_bits": (red.n.bit_length() - 1) / red.dim,
        "basis_inf_norm_bits": [inf_norm(b).bit_length() for b in red.basis],
    }
