"""Rank-profile solver for Macaulay closures M_D: same record, fewer rows.

``Closure.macaulay_closure`` runs the declared column pass on the full Macaulay
matrix and returns its op log; certificates are read back from that log. Many
callers need only what the record holds -- rank, whether 1 is in M_D, and the
dimensions by degree -- and those depend only on the column rank profile of the
matrix (the set of pivot columns in the fixed column order), which every
elimination of every spanning set of the same row space gives. This module
computes that profile with three changes that leave the row space alone:

1. F5/Frobenius row filter (``f5_keep``). In B = F_2[v]/(v_i^2 + v_i) let
   V(e, k) = span{nu*f_j : j <= k, deg nu <= e - 2} and let L(e, k) be the set
   of leading monomials of degree e of V(e, k) (leading = first in the column
   order, which puts higher degree first). If mu is in L(e, k), with
   deg mu = e, the row mu*f_k is dropped. Proof: take g in V(e, k) with
   leading monomial mu, g = sum_j h_j f_j (deg h_j <= e - 2). Then
       g*f_k = sum_{t in g} t*f_k = sum_{j<k} (h_j f_k)*f_j + h_k*f_k,
   using f_k*f_k = f_k in B. Every term other than mu*f_k is a Macaulay row
   of degree bound D with a smaller key (k, deg mu, -column position): the
   rows t*f_k for the other monomials t of g (same degree and later in the
   order, or lower degree), the rows of h_k*f_k (degree <= e - 2), and the
   rows of (h_j f_k)*f_j (an earlier equation; h_j f_k has degree <= e).
   So each dropped row is a sum of rows with smaller keys, and by induction
   on the key the kept rows span M_D. L(e, k) is read off small matrices
   (multiplier degree <= e - 2 <= D - 4) processed equation by equation.
   It removes every row that reduces to zero in the regular range (all of
   them at D <= 5 on the CERTBIN shapes, 38.8k of 57.3k at nv = 20, D = 6).
2. Row order ``lead_desc``: rows sorted by leading column descending, then by
   weight. The column pass then takes still-unreduced (sparse) rows as pivots
   before rows that earlier pivots have already filled in. The pivot set does
   not depend on row order.
3. The fast native column pass on the result.

The record equals ``Closure.macaulay_closure``'s field for field; tests check
that against the exact engine and against archived RC-1 records. The
certificate (when 1 is in M_D) is a valid flat list of (mu, k) Macaulay rows
summing to 1, checked by ``eval_cert`` before it is returned. It is usually not the
certificate the declared column pass extracts, so an experiment that pins
certificates or op-log hashes to that engine must keep using it. This is a
separate instrument; declare it as such.
"""
from __future__ import annotations

import numpy as np

from . import kernels
from .closure import cached_closure, eval_cert

SOLVER = "rankprofile-v1"


def _row_order(neq, nmu):
    """Macaulay row indices (mu_index * neq + k) grouped by equation k."""
    mi = np.arange(nmu, dtype=np.int64)
    return (mi[None, :] * neq + np.arange(neq, dtype=np.int64)[:, None]).ravel()


def f5_keep(nv, D, eqs):
    """Boolean mask over the rows of Closure(nv, D, len(eqs)) (row index
    mu_index * neq + k): False for rows the F5/Frobenius criterion proves lie
    in the span of the kept rows (module docstring)."""
    neq = len(eqs)
    cD = cached_closure(nv, D, neq)
    keep = np.ones(cD.R, dtype=bool)
    if D < 4:
        return keep
    mu_index = {int(m): i for i, m in enumerate(cD.mu_mask)}
    for e in range(2, D - 1):                    # multiplier degree e = 2 .. D-2
        ce = cached_closure(nv, e, neq)
        nmu = len(ce.mus)
        Me = np.ascontiguousarray(ce.build_M(eqs)[_row_order(neq, nmu)])
        lead = kernels.row_leads(Me, ce.C).reshape(neq, nmu)
        L = []
        for k in range(neq):
            lk = lead[k]
            lk = lk[lk >= 0]
            L.extend(int(m) for m in ce.col_mask[lk[ce.col_deg[lk] == e]])
            if L:
                rows = np.fromiter((mu_index[m] for m in L), dtype=np.int64, count=len(L))
                keep[rows * neq + k] = False
    return keep


def lead_desc_order(M, C):
    """Row permutation: leading column descending, then popcount ascending;
    zero rows last."""
    lead, weight = kernels.row_lead_weight(np.ascontiguousarray(M))
    return np.lexsort((weight, -lead))


def macaulay_profile(eqs, nv, D, want_cert=True, use_f5=True, order="lead_desc", threads=None):
    """M_D record by rank profile -> (record, certificate or None, info).

    record: {"rank", "one", "dims_by_deg"}, equal to Closure.macaulay_closure.
    info: {"solver", "rows_total", "rows_kept", "pivcols"} (pivcols = sorted
    pivot columns in Closure(nv, D, neq) column order)."""
    neq = len(eqs)
    cl = cached_closure(nv, D, neq)
    M = cl.build_M(eqs)
    idx = np.flatnonzero(f5_keep(nv, D, eqs)) if use_f5 else np.arange(cl.R)
    if order == "lead_desc":
        idx = idx[lead_desc_order(np.ascontiguousarray(M[idx]), cl.C)]
    elif order != "built":
        raise ValueError(f"unknown order {order!r}")
    A = np.ascontiguousarray(M[idx])
    log = kernels.column_pass(A, cl.C, keep_ops=want_cert, threads=threads)
    cs = log.cs
    one = bool((cs == cl.const_col).any())
    leads = np.sort(cs)
    rec = {"rank": log.K, "one": one,
           "dims_by_deg": [int((cl.col_deg[leads] <= d).sum()) for d in range(D + 1)]}
    info = {"solver": SOLVER, "rows_total": cl.R, "rows_kept": int(len(idx)),
            "pivcols": leads.tolist()}
    cert = None
    if one and want_cert:
        pstar = int(log.ps[np.flatnonzero(cs == cl.const_col)[0]])
        S = np.zeros((A.shape[0], 1), dtype=np.uint64)
        S[pstar, 0] = np.uint64(1)
        kernels.backtrace(log, S)
        par = {}
        for r in np.flatnonzero(S[:, 0]).tolist():
            key = cl.row_pair(int(idx[r]))
            par[key] = par.get(key, 0) ^ 1
        cert = sorted(k for k, p in par.items() if p)
        if eval_cert(cert, eqs) != [0]:
            raise AssertionError("rank-profile certificate does not sum to 1")
    return rec, cert, info
