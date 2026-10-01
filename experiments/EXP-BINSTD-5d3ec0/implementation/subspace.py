"""F_2-subspaces V' and membership tests for EXP-BINSTD-5d3ec0."""
from __future__ import annotations

import numpy as np


def _bits(x: int, n: int) -> np.ndarray:
    return np.array([(x >> i) & 1 for i in range(n)], dtype=np.uint8)


def _from_bits(v: np.ndarray) -> int:
    x = 0
    for i, b in enumerate(v):
        if b:
            x |= 1 << i
    return int(x)


def random_subspace_basis(n: int, l_prime: int, rng) -> np.ndarray:
    """Return n x l' full-rank matrix over F_2 (columns = basis of V')."""
    while True:
        B = rng.integers(0, 2, size=(n, l_prime), dtype=np.uint8)
        # rank check
        M = B.copy().astype(np.uint8)
        rank = 0
        used = [False] * l_prime
        for r in range(n):
            piv = None
            for c in range(l_prime):
                if not used[c] and M[r, c]:
                    piv = c
                    break
            if piv is None:
                continue
            used[piv] = True
            rank += 1
            for c2 in range(l_prime):
                if c2 != piv and M[r, c2]:
                    M[:, c2] ^= M[:, piv]
        if rank == l_prime:
            return B


class Subspace:
    def __init__(self, basis: np.ndarray):
        """basis: n x l' over F_2."""
        self.basis = basis.astype(np.uint8)
        self.n, self.l_prime = basis.shape
        # Precompute all elements for small l' (l'<=12 => 4096)
        self.elements = []
        self.member = set()
        for mask in range(1 << self.l_prime):
            v = np.zeros(self.n, dtype=np.uint8)
            for j in range(self.l_prime):
                if (mask >> j) & 1:
                    v ^= self.basis[:, j]
            x = _from_bits(v)
            self.elements.append(x)
            self.member.add(x)

    def contains(self, x: int) -> bool:
        return x in self.member

    def random_element(self, rng) -> int:
        return int(rng.choice(self.elements))


def transport_rep_set(group_order: int, size: int, rng) -> set:
    """Relabelled Z/(4l) representative set: random subset of given size."""
    out = set()
    while len(out) < size:
        out.add(rng.randrange(0, group_order))
    return out
