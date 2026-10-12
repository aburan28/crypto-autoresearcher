#!/usr/bin/env python3
"""Twin N_var meters for descended S_3 XOR-SAT size (EXP-BINSTD-5b2fd0).

Encoding (frozen pin): Weil-descend S_3(x1, x2, xR) with x_i in span(basis),
xR a frozen field element, curve constant B frozen. Boolean variables:
nv0 = 2 * ell.

N_var is the number of variables that still appear in the nonlinear part
after Gaussian elimination of the F_2-linear equations extracted from the
descended system (KR-IC-style remaining-variable count at fixed ell).

Twin A: bit-packed XOR elimination on the linear slice.
Twin B: dense GF(2) row-echelon on the same linear matrix (independent code).
"""
from __future__ import annotations

from itertools import combinations


def _pmul(F, P, Q):
    out = {}
    for m1, c1 in P.items():
        for m2, c2 in Q.items():
            m = tuple(sorted(set(m1) | set(m2)))
            out[m] = out.get(m, 0) ^ F.mul(c1, c2)
    return out


def _padd(*Ps):
    out = {}
    for P in Ps:
        for m, c in P.items():
            out[m] = out.get(m, 0) ^ c
    return out


def _pscal(F, P, c):
    return {m: F.mul(v, c) for m, v in P.items()}


def _psq(F, P):
    out = {}
    for m, c in P.items():
        out[m] = out.get(m, 0) ^ F.mul(c, c)
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def descend_s3(F, B: int, basis: list[int], xR: int):
    """Descend S3; return (eqs_by_bit, meta) with nv = 2*len(basis)."""
    L = len(basis)
    X1 = {(j,): basis[j] for j in range(L) if basis[j]}
    X2 = {(L + j,): basis[j] for j in range(L) if basis[j]}
    s12 = _pmul(F, X1, X2)
    e1 = _padd(s12, _pscal(F, X1, xR), _pscal(F, X2, xR))
    S = _padd(_psq(F, e1), _pscal(F, s12, xR), {(): B})
    n = F.n
    eqs = [[] for _ in range(n)]
    for m, c in S.items():
        if c == 0:
            continue
        mask = mono_mask(m)
        for k in range(n):
            if (c >> k) & 1:
                eqs[k].append(mask)
    meta = {"nv": 2 * L, "neq": n, "L": L, "n_terms": len(S)}
    return eqs, meta


def _split_linear_nonlinear(eqs: list[list[int]], nv: int):
    """Partition monomials: degree <=1 vs degree >=2."""
    linear_rows: list[list[int]] = []  # each row length nv, RHS separate
    linear_rhs: list[int] = []
    nonlinear_vars: set[int] = set()
    for masks in eqs:
        # Combine XOR of masks into one polynomial over GF2
        # Represent as coeff of constants and of single vars, plus higher.
        const = 0
        lin = [0] * nv
        higher = False
        seen = {}
        for mask in masks:
            seen[mask] = seen.get(mask, 0) ^ 1
        for mask, bit in seen.items():
            if bit == 0:
                continue
            if mask == 0:
                const ^= 1
                continue
            # popcount
            pc = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
            if pc == 1:
                # single variable
                v = (mask & -mask).bit_length() - 1
                if 0 <= v < nv:
                    lin[v] ^= 1
                else:
                    higher = True
            else:
                higher = True
                # mark vars in nonlinear support
                m = mask
                while m:
                    lsb = m & -m
                    v = lsb.bit_length() - 1
                    if v < nv:
                        nonlinear_vars.add(v)
                    m ^= lsb
        if any(lin) or const:
            # keep linear equation even if higher terms also present:
            # only pure-linear equations enter the elimination twin.
            if not higher:
                linear_rows.append(lin)
                linear_rhs.append(const)
        if higher:
            # already collected nonlinear_vars from higher masks
            pass
    return linear_rows, linear_rhs, nonlinear_vars


def _rank_and_pivot_vars_a(rows: list[list[int]], nv: int) -> tuple[int, set[int]]:
    """Twin A: bit-packed XOR Gaussian elimination."""
    packed = []
    for row in rows:
        w = 0
        for j, b in enumerate(row):
            if b:
                w |= 1 << j
        packed.append(w)
    pivots: set[int] = set()
    for col in range(nv):
        # find pivot
        piv = None
        for i, w in enumerate(packed):
            if (w >> col) & 1:
                # ensure not already used as earlier pivot row somehow — just take first
                piv = i
                break
        if piv is None:
            continue
        pivots.add(col)
        pw = packed[piv]
        for i, w in enumerate(packed):
            if i != piv and ((w >> col) & 1):
                packed[i] ^= pw
        # move pivot row aside by clearing others already done; mark used by zeroing its lower?
        packed[piv] = 0  # consume
    return len(pivots), pivots


def _rank_and_pivot_vars_b(rows: list[list[int]], nv: int) -> tuple[int, set[int]]:
    """Twin B: dense list-of-lists row echelon (independent implementation)."""
    mat = [row[:] for row in rows]
    pivots: set[int] = set()
    row_i = 0
    for col in range(nv):
        # find pivot row at/after row_i
        piv = None
        for r in range(row_i, len(mat)):
            if mat[r][col]:
                piv = r
                break
        if piv is None:
            continue
        mat[row_i], mat[piv] = mat[piv], mat[row_i]
        pivots.add(col)
        for r in range(len(mat)):
            if r != row_i and mat[r][col]:
                mat[r] = [a ^ b for a, b in zip(mat[r], mat[row_i])]
        row_i += 1
        if row_i >= len(mat):
            break
    return len(pivots), pivots


def n_var_from_eqs(eqs, nv: int) -> tuple[int, int, bool, dict]:
    """Return (N_var_A, N_var_B, agree, details)."""
    lin_rows, _rhs, nonlinear_vars = _split_linear_nonlinear(eqs, nv)
    if not lin_rows:
        # no pure linear equations: N_var = nv (all free) but still report twin
        a = b = nv
        return a, b, True, {
            "lin_rank_a": 0,
            "lin_rank_b": 0,
            "nonlinear_support": sorted(nonlinear_vars),
            "nv0": nv,
        }
    ra, pa = _rank_and_pivot_vars_a(lin_rows, nv)
    rb, pb = _rank_and_pivot_vars_b(lin_rows, nv)
    # Remaining variables = those not pivoted away, restricted to those that
    # still appear in nonlinear support if nonempty; else nv - rank.
    if nonlinear_vars:
        n_var_a = len(nonlinear_vars - pa)
        n_var_b = len(nonlinear_vars - pb)
    else:
        n_var_a = nv - ra
        n_var_b = nv - rb
    return n_var_a, n_var_b, (n_var_a == n_var_b and ra == rb), {
        "lin_rank_a": ra,
        "lin_rank_b": rb,
        "pivots_a": sorted(pa),
        "pivots_b": sorted(pb),
        "nonlinear_support": sorted(nonlinear_vars),
        "nv0": nv,
    }


def encode_n_var(F, B: int, basis: list[int], xR: int) -> tuple[int, int, bool, dict]:
    eqs, meta = descend_s3(F, B, basis, xR)
    n_a, n_b, ok, det = n_var_from_eqs(eqs, meta["nv"])
    det["meta"] = meta
    return n_a, n_b, ok, det


# Silence unused import warning for combinations if linters care — kept for parity.
_ = combinations
