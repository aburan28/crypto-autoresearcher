#!/usr/bin/env python3
"""Pure-Python GF(2) dense GE and scalar Wiedemann. No Magma/Sage/numpy."""
from __future__ import annotations

import hashlib
from typing import Sequence


def popcount(x: int) -> int:
    return int(x).bit_count()


def parity(x: int) -> int:
    return popcount(x) & 1


def matvec(rows: Sequence[int], x: int) -> int:
    y = 0
    for i, row in enumerate(rows):
        if parity(row & x):
            y |= 1 << i
    return y


def matrix_sha256(rows: Sequence[int], n: int) -> str:
    h = hashlib.sha256()
    h.update(n.to_bytes(4, "little"))
    for row in rows:
        h.update(int(row).to_bytes((n + 7) // 8, "little"))
    return h.hexdigest()


def dense_ge_solve(rows: list[int], b: int, n: int) -> tuple[int | None, int]:
    """Solve A x = b over GF(2). Returns (x or None, rank)."""
    a = list(rows)
    rhs = [1 if (b >> i) & 1 else 0 for i in range(n)]
    pivots: list[int] = []
    col = 0
    r = 0
    for col in range(n):
        piv = None
        for i in range(r, n):
            if (a[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        a[r], a[piv] = a[piv], a[r]
        rhs[r], rhs[piv] = rhs[piv], rhs[r]
        pivots.append(col)
        for i in range(n):
            if i != r and ((a[i] >> col) & 1):
                a[i] ^= a[r]
                rhs[i] ^= rhs[r]
        r += 1
        if r == n:
            break
    for i in range(r, n):
        if rhs[i]:
            return None, r
    x = 0
    for k, c in enumerate(pivots):
        if rhs[k]:
            x |= 1 << c
    return x, r


def solve_column_span(cols: list[int], target: int, n: int) -> int | None:
    """Solve K y = target over GF(2), columns of K packed as n-bit ints.

    Returns y as a k-bit mask, or None if target is not in the column span.
    """
    k = len(cols)
    if k == 0:
        return 0 if target == 0 else None
    rows = [0] * n
    for i in range(n):
        row = 0
        for j in range(k):
            if (cols[j] >> i) & 1:
                row |= 1 << j
        if (target >> i) & 1:
            row |= 1 << k
        rows[i] = row
    r = 0
    pivots: list[tuple[int, int]] = []
    for col in range(k):
        piv = None
        for i in range(r, n):
            if (rows[i] >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        for i in range(n):
            if i != r and ((rows[i] >> col) & 1):
                rows[i] ^= rows[r]
        pivots.append((r, col))
        r += 1
    for i in range(r, n):
        if (rows[i] >> k) & 1:
            return None
    y = 0
    for pr, col in pivots:
        if (rows[pr] >> k) & 1:
            y |= 1 << col
    return y


def wiedemann_solve(rows: list[int], b: int, n: int, u: int) -> tuple[int | None, int]:
    """Krylov/Wiedemann reconstruction for A x = b over GF(2).

    Builds {b, Ab, A^2 b, ...} by sparse matvec until A^k b lies in the span,
    then reconstructs x from the linear dependence. The probe ``u`` is unused
    (kept so the race call site stays stable); dependence is detected on the
    vector Krylov, not a scalar projection, because a scalar Berlekamp–Massey
    minpoly need not annihilate A^i b over GF(2).
    """
    del u
    if b == 0:
        return 0, n
    vecs: list[int] = []
    v = b
    for _ in range(n + 1):
        if vecs:
            coef = solve_column_span(vecs, v, n)
            if coef is not None:
                if (coef & 1) == 0:
                    return None, 0
                x = vecs[-1]
                k = len(vecs)
                for j in range(1, k):
                    if (coef >> j) & 1:
                        x ^= vecs[j - 1]
                if matvec(rows, x) != b:
                    return None, 0
                return x, n
        vecs.append(v)
        v = matvec(rows, v)
    return None, 0


def median_sort(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    m = len(ys)
    return float(ys[m // 2]) if m % 2 else 0.5 * (ys[m // 2 - 1] + ys[m // 2])


def median_insert(xs: list[float]) -> float | None:
    if not xs:
        return None
    ys = list(xs)
    n = len(ys)
    for i in range(n):
        j = i
        v = ys[i]
        while j > 0 and ys[j - 1] > v:
            ys[j] = ys[j - 1]
            j -= 1
        ys[j] = v
    return float(ys[n // 2]) if n % 2 else 0.5 * (ys[n // 2 - 1] + ys[n // 2])
