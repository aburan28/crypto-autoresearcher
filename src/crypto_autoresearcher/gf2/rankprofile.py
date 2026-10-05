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

Rows are built natively straight from monomial masks (``kernels.build_rows``):
within a degree the column order is colex order, so a monomial's column is a
sum of binomials. No 2^nv table is built (``Closure`` builds one), only the
kept rows are materialised, and they are written already in pivot order.

The record equals ``Closure.macaulay_closure``'s field for field; tests check
that against the exact engine and against archived RC-1 records. The
certificate (when 1 is in M_D) is a valid flat list of (mu, k) Macaulay rows
summing to 1, checked by ``cert_sums_to_one`` (the parity test of
``closure.eval_cert``, done natively) before it is returned. It is usually not the
certificate the declared column pass extracts, so an experiment that pins
certificates or op-log hashes to that engine must keep using it. This is a
separate instrument; declare it as such.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations
from math import comb

import numpy as np

from . import kernels

SOLVER = "rankprofile-v1"


class Shape:
    """Column and multiplier bookkeeping of Closure(nv, D, .) without its
    2^nv tables: same column order (degree descending, then mask ascending),
    same multiplier order (degree ascending, then index tuple)."""

    def __init__(self, nv, D):
        self.nv, self.D = nv, D
        self.off = [0] * (D + 2)                 # first column of degree d
        for d in range(D - 1, -1, -1):
            self.off[d] = self.off[d + 1] + comb(nv, d + 1)
        self.C = self.off[0] + 1
        self.W = (self.C + 63) // 64
        self.const_col = self.C - 1
        # column c has degree d iff off[d] <= c < off[d-1] (off[-1] := C)
        self._starts = np.array([self.off[d] for d in range(D, -1, -1)], dtype=np.int64)
        mus = [m for d in range(max(D - 2, -1) + 1) for m in combinations(range(nv), d)]
        self.mu_mask = np.array([sum(1 << i for i in m) for m in mus], dtype=np.uint64)

    def col_deg(self, cols):
        cols = np.asarray(cols, dtype=np.int64)
        return self.D - (np.searchsorted(self._starts, cols, side="right") - 1)

    @property
    def masks(self):
        """Monomial mask of every column, in column order (uint64)."""
        if not hasattr(self, "_masks"):
            parts = []
            for d in range(self.D, -1, -1):
                parts.append(np.sort(np.array([sum(1 << i for i in m) for m in combinations(range(self.nv), d)],
                                              dtype=np.uint64)))
            self._masks = np.concatenate(parts)
        return self._masks

    def cols_of(self, masks):
        """Column of each monomial mask (vectorised colex rank)."""
        masks = np.asarray(masks, dtype=np.uint64)
        deg = np.array([bin(int(x)).count("1") for x in masks], dtype=np.int64)
        out = np.empty(len(masks), dtype=np.int64)
        for d in np.unique(deg).tolist():
            sel = deg == d
            lo, hi = self.off[d], (self.off[d - 1] if d > 0 else self.C)
            out[sel] = lo + np.searchsorted(self.masks[lo:hi], masks[sel])
        return out

    @property
    def product_tables(self):
        """(colmap, maps) for kernels.products, as Closure builds them."""
        if not hasattr(self, "_ptab"):
            masks = self.masks
            deg = self.col_deg(np.arange(self.C))
            low = np.flatnonzero(deg <= self.D - 1)
            colmap = np.full((self.nv, self.C), -1, dtype=np.int32)
            maps = []
            for j in range(self.nv):
                bj = np.uint64(1 << j)
                has = (masks[low] & bj) != 0
                A = low[~has]
                tA = self.cols_of(masks[A] | bj)
                maps.append((A, tA, low[has]))
                colmap[j, A] = tA
                colmap[j, low[has]] = low[has]
            self._ptab = (colmap, maps)
        return self._ptab

    def col_mask(self, c):
        """Monomial mask of column c (colex unrank)."""
        c = int(c)
        d = int(self.col_deg([c])[0])
        r, x = c - self.off[d], 0
        for i in range(d, 0, -1):
            b = i - 1
            while comb(b + 1, i) <= r:
                b += 1
            r -= comb(b, i)
            x |= 1 << b
        return x


@lru_cache(maxsize=64)
def shape(nv, D):
    return Shape(nv, D)


def f5_keep(nv, D, eqs, threads=None):
    """Boolean mask over the rows of Closure(nv, D, len(eqs)) (row index
    mu_index * neq + k): False for rows the F5/Frobenius criterion proves lie
    in the span of the kept rows (module docstring)."""
    neq = len(eqs)
    sD = shape(nv, D)
    keep = np.ones(len(sD.mu_mask) * neq, dtype=bool)
    if D < 4 or neq == 0:
        return keep
    eoff, emon = kernels.pack_eqs(eqs)
    mu_index = {int(m): i for i, m in enumerate(sD.mu_mask)}
    for e in range(2, D - 1):                    # multiplier degree e = 2 .. D-2
        se = shape(nv, e)
        nmu = len(se.mu_mask)
        mu = np.tile(se.mu_mask, neq)            # grouped by equation k
        k = np.repeat(np.arange(neq, dtype=np.int32), nmu)
        Me, _, _ = kernels.build_rows(eoff, emon, nv, e, mu, k, W=se.W, threads=threads)
        lead = kernels.row_leads(Me, se.C).reshape(neq, nmu)
        L = []
        for kk in range(neq):
            lk = lead[kk]
            lk = lk[lk >= 0]
            lk = lk[se.col_deg(lk) == e]
            L.extend(se.col_mask(c) for c in lk.tolist())
            if L:
                rows = np.fromiter((mu_index[m] for m in L), dtype=np.int64, count=len(L))
                keep[rows * neq + kk] = False
    return keep


def cert_sums_to_one(cert, eqs, nv, threads=None):
    """Does sum over (mu, k) in cert of mu*f_k equal 1 in B? Same parity
    computation as closure.eval_cert(cert, eqs) == [0], done natively: build
    every certificate row, XOR them together, and require that only the
    constant column remains."""
    if not cert:
        return False
    mu = np.array([m for m, _ in cert], dtype=np.uint64)
    k = np.array([kk for _, kk in cert], dtype=np.int32)
    Dp = min(nv, max(bin(int(m)).count("1") for m in mu.tolist()) + 2)
    sh = shape(nv, Dp)
    eoff, emon = kernels.pack_eqs(eqs)
    rows, _, _ = kernels.build_rows(eoff, emon, nv, Dp, mu, k, W=sh.W, threads=threads)
    acc = np.bitwise_xor.reduce(rows, axis=0)
    want = np.zeros(sh.W, dtype=np.uint64)
    want[sh.const_col >> 6] = np.uint64(1 << (sh.const_col & 63))
    return bool(np.array_equal(acc, want))


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
    sh = shape(nv, D)
    R = len(sh.mu_mask) * neq
    idx = np.flatnonzero(f5_keep(nv, D, eqs, threads)) if use_f5 else np.arange(R)
    eoff, emon = kernels.pack_eqs(eqs)
    mu = sh.mu_mask[idx // max(neq, 1)]
    k = (idx % max(neq, 1)).astype(np.int32)
    if order == "lead_desc":
        _, lead, weight = kernels.build_rows(eoff, emon, nv, D, mu, k, threads=threads)
        perm = np.lexsort((weight, -lead))
        mu, k = mu[perm], k[perm]
    elif order != "built":
        raise ValueError(f"unknown order {order!r}")
    A, _, _ = kernels.build_rows(eoff, emon, nv, D, mu, k, W=sh.W, threads=threads)
    log = kernels.column_pass(A, sh.C, keep_ops=want_cert, threads=threads)
    cs = log.cs
    one = bool((cs == sh.const_col).any())
    leads = np.sort(cs)
    deg = sh.col_deg(leads)
    rec = {"rank": log.K, "one": one,
           "dims_by_deg": [int((deg <= d).sum()) for d in range(D + 1)]}
    info = {"solver": SOLVER, "rows_total": R, "rows_kept": int(len(idx)),
            "pivcols": leads.tolist()}
    cert = None
    if one and want_cert:
        pstar = int(log.ps[np.flatnonzero(cs == sh.const_col)[0]])
        S = np.zeros((A.shape[0], 1), dtype=np.uint64)
        S[pstar, 0] = np.uint64(1)
        kernels.backtrace(log, S)
        par = {}
        for r in np.flatnonzero(S[:, 0]).tolist():
            key = (int(mu[r]), int(k[r]))
            par[key] = par.get(key, 0) ^ 1
        cert = sorted(key for key, p in par.items() if p)
        if not cert_sums_to_one(cert, eqs, nv, threads):
            raise AssertionError("rank-profile certificate does not sum to 1")
    return rec, cert, info


STACK_ORDER = "basis_first"   # how each stacked W_D matrix is ordered (speed only)


def w_profile(eqs, nv, D, want_cert=True, threads=None):
    """W_D record by rank profile -> (record, certificate or None, info).

    record: the fields of Closure.w_closure (iterations_to_fixpoint, dims,
    final_dim, one, one_first_iteration, dims_by_deg, new_fallen_per_iteration,
    stack_rows_per_iteration), each a function of the spaces V_i alone, so
    equal to the exact engine's.

    Same iteration as Closure.w_closure (V_{i+1} = V_i + sum_j v_j * N_i, N_i =
    the basis rows of degree <= D-1 whose leads are new), with V_0 = M_D from
    the rank-profile path, every stacked matrix reordered lead-descending, and
    one more pruning at i = 0: M_{D-1} is a subspace of M_D's low part and
    v_j * M_{D-1} lies in M_D (v_j * mu * f is a Macaulay row of M_D), so only
    the basis rows whose leads are not leads of M_{D-1} -- a complement of
    M_{D-1} in V_0's low part, since leads of a subspace are a subset and
    distinct leads are independent -- need products. V_1 is the same space;
    the record reports the counts as the exact engine defines them.

    The certificate (when 1 is reached) is a flat list of (mu, k) pairs whose
    sum is 1, checked by cert_sums_to_one; mu may exceed degree D - 2 (product rows),
    as with Closure.w_closure. It is not the exact engine's certificate."""
    neq = len(eqs)
    sh = shape(nv, D)
    R_full = len(sh.mu_mask) * neq
    eoff, emon = kernels.pack_eqs(eqs)
    col_deg = sh.col_deg(np.arange(sh.C))
    # level 0: filtered, ordered M_D
    idx = np.flatnonzero(f5_keep(nv, D, eqs, threads))
    mu = sh.mu_mask[idx // max(neq, 1)]
    k = (idx % max(neq, 1)).astype(np.int32)
    _, lead0, weight0 = kernels.build_rows(eoff, emon, nv, D, mu, k, threads=threads)
    perm = np.lexsort((weight0, -lead0))
    mu, k = mu[perm], k[perm]
    M, _, _ = kernels.build_rows(eoff, emon, nv, D, mu, k, W=sh.W, threads=threads)
    levels = [{"src": ("rows", mu, k)}]
    log = kernels.column_pass(M, sh.C, keep_ops=want_cert, threads=threads)
    levels[0]["log"] = log
    ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
    dims = [int(len(ps))]
    one_first = 0 if (cs == sh.const_col).any() else None
    # leads of M_{D-1}, in this column order (U_0 of the docstring)
    covered = set()
    if D >= 3:
        rec_lo, _, info_lo = macaulay_profile(eqs, nv, D - 1, want_cert=False, threads=threads)
        lo_masks = shape(nv, D - 1).masks[np.asarray(info_lo["pivcols"], dtype=np.int64)]
        covered = set(sh.cols_of(lo_masks).tolist())
    prev_low_exact = set()                       # the exact engine's prev_low
    new_fallen, stack_rows = [], [R_full]
    colmap, maps = sh.product_tables
    i = 0
    while True:
        order = np.argsort(cs, kind="stable")
        prow, leads = ps[order], cs[order]
        basis = M[prow]
        low = col_deg[leads] <= D - 1
        low_leads = set(int(x) for x in leads[low])
        new_exact = len(low_leads - prev_low_exact)
        skip = covered if i == 0 else prev_low_exact
        new = np.array([t for t in np.flatnonzero(low) if int(leads[t]) not in skip], dtype=np.int64)
        prev_low_exact = low_leads
        new_fallen.append(new_exact)
        stack_rows.append(int(len(prow)) + nv * new_exact)
        P = kernels.products(np.ascontiguousarray(basis[new]), colmap, maps, nv, sh.C, sh.W)
        stacked = np.concatenate([basis, P])
        del P
        sperm = _stack_order(stacked, len(prow))
        M = np.ascontiguousarray(stacked[sperm])
        del stacked
        keep = want_cert and one_first is None
        log2 = kernels.column_pass(M, sh.C, keep_ops=keep, threads=threads)
        ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
        if keep:
            levels.append({"src": ("stack", prow, new, sperm), "log": log2})
        if len(ps2) == dims[-1]:
            final_leads = leads
            break
        i += 1
        dims.append(int(len(ps2)))
        if one_first is None and (cs2 == sh.const_col).any():
            one_first = i
        ps, cs = ps2, cs2
    rec = {
        "iterations_to_fixpoint": i,
        "dims": dims,
        "final_dim": dims[-1],
        "one": one_first is not None,
        "one_first_iteration": one_first,
        "dims_by_deg": [int((col_deg[final_leads] <= d).sum()) for d in range(D + 1)],
        "new_fallen_per_iteration": new_fallen,
        "stack_rows_per_iteration": stack_rows,
    }
    info = {"solver": SOLVER, "rows_total": R_full, "rows_kept": int(len(idx))}
    cert = None
    if one_first is not None and want_cert:
        cert = _w_extract(levels[:one_first + 1], nv)
        if not cert_sums_to_one(cert, eqs, nv, threads):
            raise AssertionError("rank-profile W_D certificate does not sum to 1")
    return rec, cert, info


def _stack_order(stacked, nb):
    if STACK_ORDER == "built":
        return np.arange(stacked.shape[0])
    lw, ww = kernels.row_lead_weight(stacked)
    if STACK_ORDER == "lead_desc":
        return np.lexsort((ww, -lw))
    if STACK_ORDER == "basis_first":             # basis rows as built, products lead-descending
        tail = nb + np.lexsort((ww[nb:], -lw[nb:]))
        return np.concatenate([np.arange(nb), tail])
    if STACK_ORDER == "lead_asc":
        return np.lexsort((ww, lw))
    raise ValueError(STACK_ORDER)


def _w_extract(levels, nv):
    """Trace the constant row of the last level back to (mu, k) pairs."""
    last = levels[-1]["log"]
    pstar = int(last.ps[np.flatnonzero(last.cs == last.cs.max())[0]])
    cur = {pstar: {0}}                           # final row of a level -> multiplier masks
    for lev in range(len(levels) - 1, -1, -1):
        L = levels[lev]
        ml = sorted({m for s_ in cur.values() for m in s_})
        pos = {m: t for t, m in enumerate(ml)}
        nw = (len(ml) + 63) // 64
        nrows = L["log"].ps.max() + 1 if L["log"].K else 0
        nrows = max(nrows, max(cur) + 1)
        src = L["src"]
        if src[0] == "rows":
            nrows = max(nrows, len(src[1]))
        else:
            _, prow, new, sperm = src
            nrows = max(nrows, len(sperm))
        S = np.zeros((nrows, nw), dtype=np.uint64)
        for r, ms in cur.items():
            for m in ms:
                t = pos[m]
                S[r, t >> 6] ^= np.uint64(1 << (t & 63))
        kernels.backtrace(L["log"], S)
        nxt = {}
        for r in np.flatnonzero(S.any(axis=1)).tolist():
            bits = []
            for w in range(nw):
                word = int(S[r, w])
                while word:
                    b = (word & -word).bit_length() - 1
                    bits.append(ml[w * 64 + b])
                    word &= word - 1
            if src[0] == "rows":
                _, mu, k = src
                for m in bits:
                    key = (int(mu[r]) | m, int(k[r]))
                    nxt[key] = nxt.get(key, 0) ^ 1
            else:
                q = int(sperm[r])                # row of the stacked matrix before ordering
                if q < len(prow):
                    pr, jm = int(prow[q]), 0
                else:
                    j, f = divmod(q - len(prow), len(new))
                    pr, jm = int(prow[new[f]]), 1 << j
                s_ = nxt.setdefault(pr, set())
                for m in bits:
                    s_ ^= {m | jm}
        if src[0] == "rows":
            return sorted(key for key, p in nxt.items() if p)
        cur = {r: s_ for r, s_ in nxt.items() if s_}
    raise AssertionError("unreachable")
