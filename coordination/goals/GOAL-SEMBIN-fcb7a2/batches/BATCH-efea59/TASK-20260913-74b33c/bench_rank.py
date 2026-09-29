#!/usr/bin/env python3
"""Calibrate the runtime constant in size_macaulay.py against a real GF(2) rank.

size_macaulay.py's `sec` column charges only the XOR traffic of an incremental
pivot-basis elimination.  That undercounts: the pivot scan, the dict lookups,
and the Python interpreter loop are all real, and at narrow rows they dominate.
This script measures the whole inner loop on RANDOM matrices of the shapes the
contract declares, so the contract's wall-clock budget rests on a measured
constant rather than on a throughput figure for one instruction.

It computes ranks of RANDOM GF(2) matrices only.  It builds no Weil descent,
touches no Semaev polynomial, and measures no first fall degree.
"""

from __future__ import annotations

import random
import time


def rank_gf2(rows_iter) -> int:
    """Incremental pivot-basis rank.  Memory = rank rows, not all rows."""
    pivots: dict[int, int] = {}
    rank = 0
    for row in rows_iter:
        while row:
            top = row.bit_length() - 1
            piv = pivots.get(top)
            if piv is None:
                pivots[top] = row
                rank += 1
                break
            row ^= piv
    return rank


def gen(nrows: int, ncols: int, seed: int, weight_frac: float):
    """Random rows of the declared width.

    A Macaulay row is sparse relative to its column count: a monomial times a
    quadratic or cubic generator has at most (#terms of f) monomials.  Using a
    DENSE random row is therefore pessimistic for row construction but
    OPTIMISTIC for nothing -- once a row has been reduced against a few pivots
    it is dense regardless.  Both regimes are timed.
    """
    rnd = random.Random(seed)
    if weight_frac >= 0.5:
        for _ in range(nrows):
            yield rnd.getrandbits(ncols)
    else:
        w = max(1, int(ncols * weight_frac))
        for _ in range(nrows):
            row = 0
            for _ in range(w):
                row |= 1 << rnd.randrange(ncols)
            yield row


SHAPES = [
    # (label, rows, cols) from size_macaulay.py's declared cell list, D = 4
    ("n=20 m=2 k=10", 3800, 6196),
    ("n=15 m=3 k=5", 6975, 31931),
    ("n=24 m=2 k=12", 6624, 12951),
    ("n=12 m=4 k=3", 8424, 66712),
    ("n=10 m=5 k=2", 9000, 102091),
]


def main() -> None:
    print("Measured GF(2) incremental-rank wall clock on RANDOM matrices of the")
    print("declared shapes.  sparse = 0.5% density rows (Macaulay-like input);")
    print("dense  = uniform rows (worst case).")
    print()
    hdr = (f"{'shape':16s} {'rows':>7s} {'cols':>8s} {'rank':>7s} "
           f"{'sparse s':>9s} {'dense s':>9s} {'dense GB/s':>11s}")
    print(hdr)
    print("-" * len(hdr))
    for label, nrows, ncols in SHAPES:
        t0 = time.perf_counter()
        r1 = rank_gf2(gen(nrows, ncols, 1, 0.005))
        t_sparse = time.perf_counter() - t0
        t0 = time.perf_counter()
        r2 = rank_gf2(gen(nrows, ncols, 2, 1.0))
        t_dense = time.perf_counter() - t0
        # traffic model used by size_macaulay.py
        rowb = (ncols + 7) // 8
        xor_gb = nrows * (min(nrows, ncols) / 2) * rowb / 2**30
        print(f"{label:16s} {nrows:7d} {ncols:8d} {max(r1, r2):7d} "
              f"{t_sparse:9.1f} {t_dense:9.1f} {xor_gb/max(t_dense,1e-9):11.2f}")
    print()
    print("READ THIS AS THE CONTRACT'S BUDGET BASIS: the dense column is the")
    print("worst case and the effective GB/s it implies is the constant the")
    print("declared wall clock must be sized against, NOT the 20+ GB/s a bare")
    print("int-XOR microbenchmark reports.")


if __name__ == "__main__":
    main()
