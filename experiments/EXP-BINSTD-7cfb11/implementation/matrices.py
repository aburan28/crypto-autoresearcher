"""Frozen GF(2) sparse matrix generators for EXP-BINSTD-7cfb11.

Relation-like: exactly w ones per row (toy IC relation sparsity).
Erdős–Rényi null: independent bits with p = w/ncols (same expected density).
No Magma/Sage/AUXIN. No curve arithmetic. No discrete-log collector.
"""
from __future__ import annotations

import math
import random


def nrows_for_surplus(ncols: int, surplus: float) -> int:
    return int(math.ceil(surplus * ncols))


def relation_like(nrows: int, ncols: int, weight: int, seed: int) -> tuple[list[set[int]], list[int]]:
    if not (1 <= weight <= ncols):
        raise ValueError("weight must lie in 1..ncols")
    rng = random.Random(seed)
    sets: list[set[int]] = []
    bits: list[int] = []
    for _ in range(nrows):
        cols = rng.sample(range(ncols), weight)
        s = set(cols)
        sets.append(s)
        bits.append(sum(1 << c for c in s))
    return sets, bits


def erdos_renyi(nrows: int, ncols: int, p: float, seed: int) -> tuple[list[set[int]], list[int]]:
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must lie in [0,1]")
    rng = random.Random(seed)
    sets: list[set[int]] = []
    bits: list[int] = []
    for _ in range(nrows):
        s: set[int] = set()
        mask = 0
        for c in range(ncols):
            if rng.random() < p:
                s.add(c)
                mask |= 1 << c
        sets.append(s)
        bits.append(mask)
    return sets, bits


def cell_seed(master: int, n: int, surplus_index: int, kind_code: int) -> int:
    return int(master) + 1000 * int(n) + 10 * int(surplus_index) + int(kind_code)
