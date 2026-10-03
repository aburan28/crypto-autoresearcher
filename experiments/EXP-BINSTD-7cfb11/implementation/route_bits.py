"""Route B: GF(2) sparse Gauss–Jordan via integer bitmasks (XOR + popcount).

Does not import route_sets. Same pivot rule as the sets route: left-to-right
first unused pivot row; XOR-clears the pivot column from every other row.
"""
from __future__ import annotations


def gauss_jordan_fill_in(rows: list[int], ncols: int) -> dict:
    """Return nnz_initial, nnz_after, fill_in_ratio F, rank.

    ``rows`` is a list of bitmasks with bit i = column i (i < ncols).
    """
    if ncols < 0:
        raise ValueError("ncols must be nonnegative")
    mask = (1 << ncols) - 1 if ncols else 0
    matrix = [int(r) & mask for r in rows]
    nnz_initial = sum(r.bit_count() for r in matrix)
    used = [False] * len(matrix)
    rank = 0
    for col in range(ncols):
        bit = 1 << col
        piv = None
        for i, r in enumerate(matrix):
            if not used[i] and (r & bit):
                piv = i
                break
        if piv is None:
            continue
        used[piv] = True
        rank += 1
        pivot_row = matrix[piv]
        for j, r in enumerate(matrix):
            if j != piv and (r & bit):
                matrix[j] = r ^ pivot_row
    nnz_after = sum(r.bit_count() for r in matrix)
    if nnz_initial == 0:
        f = None
    else:
        f = nnz_after / nnz_initial
    return {
        "route": "bits",
        "nnz_initial": nnz_initial,
        "nnz_after": nnz_after,
        "fill_in_ratio": f,
        "rank": rank,
        "nrows": len(matrix),
        "ncols": ncols,
    }
