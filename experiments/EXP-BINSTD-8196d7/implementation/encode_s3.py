#!/usr/bin/env python3
"""Twin Trace-linear rank and residual nonlinear-clause meters (EXP-BINSTD-8196d7).

Encoding (frozen pin): Weil-descend S_3(x1, x2, xR) with x_i in span(basis),
xR a frozen field element, curve constant B frozen. Boolean variables:
nv0 = 2 * ell.

Under KR-IC-f5c584 the Trace morphism forces pure-linear equations after
S_3 Weil descent (first fall degree 2). On this pin, r_Tr is the F_2-rank of
that pure-linear (degree ≤1) block. N_nl is the number of nonlinear clauses
(equations carrying a degree ≥2 monomial) that still involve at least one
non-pivot variable after Trace-linear elimination — the residual nonlinear
XOR-SAT clause count.

Twin A: bit-packed XOR elimination on the Trace-linear slice.
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


def _classify_eqs(eqs: list[list[int]], nv: int):
    """Return pure-linear rows/rhs and nonlinear clause var-supports."""
    linear_rows: list[list[int]] = []
    linear_rhs: list[int] = []
    nonlinear_supports: list[set[int]] = []
    for masks in eqs:
        const = 0
        lin = [0] * nv
        higher = False
        nl_vars: set[int] = set()
        seen: dict[int, int] = {}
        for mask in masks:
            seen[mask] = seen.get(mask, 0) ^ 1
        for mask, bit in seen.items():
            if bit == 0:
                continue
            if mask == 0:
                const ^= 1
                continue
            pc = mask.bit_count() if hasattr(int, "bit_count") else bin(mask).count("1")
            if pc == 1:
                v = (mask & -mask).bit_length() - 1
                if 0 <= v < nv:
                    lin[v] ^= 1
                else:
                    higher = True
            else:
                higher = True
                m = mask
                while m:
                    lsb = m & -m
                    v = lsb.bit_length() - 1
                    if v < nv:
                        nl_vars.add(v)
                    m ^= lsb
        if not higher and (any(lin) or const):
            linear_rows.append(lin)
            linear_rhs.append(const)
        if higher:
            # also include degree-1 vars that co-occur in a mixed equation
            for v, b in enumerate(lin):
                if b:
                    nl_vars.add(v)
            nonlinear_supports.append(nl_vars)
    return linear_rows, linear_rhs, nonlinear_supports


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
        piv = None
        for i, w in enumerate(packed):
            if (w >> col) & 1:
                piv = i
                break
        if piv is None:
            continue
        pivots.add(col)
        pw = packed[piv]
        for i, w in enumerate(packed):
            if i != piv and ((w >> col) & 1):
                packed[i] ^= pw
        packed[piv] = 0
    return len(pivots), pivots


def _rank_and_pivot_vars_b(rows: list[list[int]], nv: int) -> tuple[int, set[int]]:
    """Twin B: dense list-of-lists row echelon (independent implementation)."""
    mat = [row[:] for row in rows]
    pivots: set[int] = set()
    row_i = 0
    for col in range(nv):
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


def _nnl_after_pivots(nonlinear_supports: list[set[int]], pivots: set[int]) -> int:
    """Count nonlinear clauses that still involve a non-pivot variable."""
    n_nl = 0
    for support in nonlinear_supports:
        if support - pivots:
            n_nl += 1
    return n_nl


def trace_rank_and_nnl(eqs, nv: int) -> tuple[int, int, int, int, bool, dict]:
    """Return (rTr_A, rTr_B, Nnl_A, Nnl_B, agree, details)."""
    lin_rows, _rhs, nl_supports = _classify_eqs(eqs, nv)
    if not lin_rows:
        ra = rb = 0
        pa = pb = set()
    else:
        ra, pa = _rank_and_pivot_vars_a(lin_rows, nv)
        rb, pb = _rank_and_pivot_vars_b(lin_rows, nv)
    n_nl_a = _nnl_after_pivots(nl_supports, pa)
    n_nl_b = _nnl_after_pivots(nl_supports, pb)
    agree = ra == rb and n_nl_a == n_nl_b and pa == pb
    return ra, rb, n_nl_a, n_nl_b, agree, {
        "r_Tr_a": ra,
        "r_Tr_b": rb,
        "N_nl_a": n_nl_a,
        "N_nl_b": n_nl_b,
        "pivots_a": sorted(pa),
        "pivots_b": sorted(pb),
        "n_nonlinear_clauses_raw": len(nl_supports),
        "n_trace_linear_rows": len(lin_rows),
        "nv0": nv,
    }


def encode_trace_nnl(F, B: int, basis: list[int], xR: int) -> tuple[int, int, int, int, bool, dict]:
    eqs, meta = descend_s3(F, B, basis, xR)
    ra, rb, na, nb, ok, det = trace_rank_and_nnl(eqs, meta["nv"])
    det["meta"] = meta
    return ra, rb, na, nb, ok, det


# Kept for parity with sibling encode modules.
_ = combinations
