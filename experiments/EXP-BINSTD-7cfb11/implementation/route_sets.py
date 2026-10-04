"""Route A: GF(2) sparse Gauss–Jordan via row sets (symmetric difference).

Does not import route_bits. Left-to-right first unused pivot row; XOR-clears
the pivot column from every other row. Sparse-LA pin for EXP-BINSTD-7cfb11.
"""
from __future__ import annotations


def gauss_jordan_fill_in(rows: list[set[int]], ncols: int) -> dict:
    """Return nnz_initial, nnz_after, fill_in_ratio F, rank.

    ``rows`` is a list of column-index sets. Mutation is on a copy.
    """
    if ncols < 0:
        raise ValueError("ncols must be nonnegative")
    matrix = [set(r) for r in rows]
    nnz_initial = sum(len(r) for r in matrix)
    used = [False] * len(matrix)
    rank = 0
    for col in range(ncols):
        piv = None
        for i, r in enumerate(matrix):
            if not used[i] and col in r:
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        pivot_row = matrix[piv]
        for j, r in enumerate(matrix):
            if j != piv and col in r:
                matrix[j] = r.symmetric_difference(pivot_row)
    nnz_after = sum(len(r) for r in matrix)
    if nnz_initial == 0:
        f = None
    else:
        f = nnz_after / nnz_initial
    return {
        "route": "sets",
        "nnz_initial": nnz_initial,
        "nnz_after": nnz_after,
        "fill_in_ratio": f,
        "rank": rank,
        "nrows": len(matrix),
        "ncols": ncols,
    }
