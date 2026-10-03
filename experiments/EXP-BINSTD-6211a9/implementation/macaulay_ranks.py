"""Degree-by-degree Macaulay ranks over GF(2) for descended S_3 systems."""
from __future__ import annotations

from itertools import combinations

import numpy as np


def mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def gf2_rank(M: np.ndarray) -> int:
    """In-place-copy Gaussian elimination rank over GF(2)."""
    if M.size == 0:
        return 0
    A = M.copy()
    rows, cols = A.shape
    r = 0
    for c in range(cols):
        # find pivot
        piv = None
        for i in range(r, rows):
            if A[i, c]:
                piv = i
                break
        if piv is None:
            continue
        if piv != r:
            A[[r, piv]] = A[[piv, r]]
        # eliminate
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] ^= A[r]
        r += 1
        if r == rows:
            break
    return r


def macaulay_matrix_at_degree(E: np.ndarray, all_mons, nv: int, D: int, neq: int):
    """Build Macaulay matrix at total degree D.

    Equations have support in all_mons (deg <= 3). Multipliers: deg <= D-d_eq
    approximated by multiplying any eq-monomial by mu with |mu|+|m| <= D,
    multilin set-union.
    """
    # columns: all monomials of degree <= D
    cols = mu_order(D, nv)
    colidx = {m: i for i, m in enumerate(cols)}
    # rows: for each eq k and each multiplier mu with deg(mu) <= D - 2
    # (eqs have deg up to 3; use D-deg_m for each term — build via term expansion)
    max_mu = max(0, D)
    mus = mu_order(max_mu, nv)
    # Filter: keep mu such that there exists an eq monomial m with len(mu)+len(m)-overlap <= D
    # Simpler: all mu with deg <= D, build rows that land in deg<=D columns only.
    rows = []
    row_meta = []
    for a, mu in enumerate(mus):
        if len(mu) > D:
            continue
        smu = set(mu)
        for k in range(neq):
            # accumulate one row
            row = np.zeros(len(cols), dtype=np.uint8)
            nonempty = False
            for j, m in enumerate(all_mons):
                if E[k, j] == 0:
                    continue
                # multilinear product
                mm = tuple(sorted(smu | set(m)))
                if len(mm) > D:
                    continue
                row[colidx[mm]] ^= 1
                nonempty = True
            if nonempty:
                rows.append(row)
                row_meta.append((mu, k))
    if not rows:
        return np.zeros((0, len(cols)), dtype=np.uint8), cols
    return np.vstack(rows), cols


def rank_profile(E, all_mons, nv, neq, dmax=4):
    """Return {d: {rank, nrows, ncols, deficiency}} and first_fall_degree."""
    profile = {}
    first_fall = None
    prev_full = True
    for D in range(1, dmax + 1):
        M, cols = macaulay_matrix_at_degree(E, all_mons, nv, D, neq)
        rank = gf2_rank(M)
        nrows, ncols = M.shape
        # "full" if rank == min(nrows, ncols) — first fall when new degree
        # introduces unexpected deficiency relative to ideal membership.
        # Practical definition used here: first D where rank < ncols
        # (system does not yet span all monomials of deg<=D) after having
        # been underdetermined — report rank sequence; first_fall = first D
        # where deficiency increases beyond D=1 baseline trend.
        deficiency = ncols - rank
        profile[D] = {
            "rank": int(rank),
            "nrows": int(nrows),
            "ncols": int(ncols),
            "deficiency": int(deficiency),
        }
        if first_fall is None and deficiency > 0 and D >= 2:
            # candidate: when matrix fails to reach full column rank
            if rank < min(nrows, ncols):
                first_fall = D
    return profile, first_fall
