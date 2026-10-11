#!/usr/bin/env python3
"""Frozen sparse GF(2) matrix generators for EXP-BINSTD-4c6404. Stdlib only."""
from __future__ import annotations

import random

R_N = {17: 32, 23: 48, 31: 64}
SURPLUS = (1.5, 2.0)
ROW_WEIGHT = 5  # odd: even weight puts 1 in the right kernel of every row.


def fold_square(rect: list[int], r: int) -> list[int]:
    """XOR-fold surplus rows onto an r x r operator, then force odd weight.

    Even-weight rows are orthogonal to the all-1s vector, so a square of
    even-weight rows is always singular. After the fold, if a row has even
    weight, flip column 0 (frozen; recorded in the matrix bytes both solvers
    receive).
    """
    square = [0] * r
    for i, row in enumerate(rect):
        square[i % r] ^= row
    for i, row in enumerate(square):
        if int(row).bit_count() % 2 == 0:
            square[i] ^= 1  # flip column 0
    return square


def ic_like_rect(r: int, surplus: float, rng: random.Random) -> list[int]:
    m = int(surplus * r + 0.999999)
    if m < r:
        m = r
    rect: list[int] = []
    for _ in range(m):
        cols = rng.sample(range(r), ROW_WEIGHT)
        row = 0
        for c in cols:
            row |= 1 << c
        rect.append(row)
    return rect


def bernoulli_rect(r: int, surplus: float, rng: random.Random) -> list[int]:
    m = int(surplus * r + 0.999999)
    if m < r:
        m = r
    p_num, p_den = ROW_WEIGHT, r
    rect: list[int] = []
    for _ in range(m):
        row = 0
        for c in range(r):
            if rng.randrange(p_den) < p_num:
                row |= 1 << c
        if row == 0:
            row = 1 << rng.randrange(r)
        rect.append(row)
    return rect


def full_rank_square(
    kind: str,
    n_label: int,
    surplus: float,
    seed: int,
    max_tries: int = 32,
) -> tuple[list[int], int, int, int] | None:
    """Return (square_rows, r, nnz, tries) or None if no full-rank square."""
    from gf2la import dense_ge_solve

    r = R_N[n_label]
    for t in range(max_tries):
        rng = random.Random(seed + t * 10007)
        if kind == "ic":
            rect = ic_like_rect(r, surplus, rng)
        elif kind == "null":
            rect = bernoulli_rect(r, surplus, rng)
        else:
            raise ValueError(kind)
        square = fold_square(rect, r)
        rhs = (1 << r) - 1
        x, rank = dense_ge_solve(square, rhs, r)
        if rank == r and x is not None:
            nnz = sum(int(row).bit_count() for row in square)
            return square, r, nnz, t + 1
    return None
