"""Rank-profile solver for Macaulay closures M_D: same record, fewer rows.

``Closure.macaulay_closure`` runs the declared column pass on the full Macaulay
matrix and returns its op log; certificates are read back from that log. Many
callers need only what the record holds -- rank, whether 1 is in M_D, and the
dimensions by degree -- and those depend only on the column rank profile of the
matrix (the set of pivot columns in the fixed column order), which every
elimination of every spanning set of the same row space gives. This module
computes that profile with changes that leave the row space alone:

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
3. Speculate, then verify (``_Space``). Only the first min(R, C) rows in key
   order (SPLIT) are eliminated outright. For the others the annihilator K of
   the space found so far is built (cheap: the echelon rows are sparse), each
   row gets its syndrome r . K, and a column pass over the syndromes picks a
   maximal subset independent modulo the space. Only that subset is
   eliminated; every other row is proved to lie in the span, exactly. Most
   rows that reduce to zero are never reduced: 88 to 93% of the elimination
   work on the measured shapes went into such rows. W_D products are handled
   the same way, their syndromes computed from the basis rows without forming
   the products, after the products with a provably new lead have been added
   directly (see w_profile).
4. The ``blocked`` native column pass on the result (faster than ``sb`` on
   these row orders).

Rows are built natively straight from monomial masks (``kernels.build_rows``):
within a degree the column order is colex order, so a monomial's column is a
sum of binomials. No 2^nv table is built (``Closure`` builds one), only the
kept rows are materialised, and they are written already in pivot order.

The record equals ``Closure.macaulay_closure``'s field for field; tests check
that against the exact engine (with every path of step 3 forced on and off)
and against archived RC-1 records. The choices in step 3 change speed only. The
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

SOLVER = "rankprofile-v2"


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
        deg = _popcount(masks)
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


def _popcount(x):
    """Bit count of each uint64 (numpy >= 1.26 has no bitwise_count)."""
    x = np.ascontiguousarray(x, dtype=np.uint64)
    return np.unpackbits(x.view(np.uint8)).reshape(len(x), 64).sum(axis=1, dtype=np.int64)


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
    by_mask = np.argsort(sD.mu_mask)
    sorted_mask = sD.mu_mask[by_mask]
    for e in range(2, D - 1):                    # multiplier degree e = 2 .. D-2
        se = shape(nv, e)
        nmu = len(se.mu_mask)
        mu = np.tile(se.mu_mask, neq)            # grouped by equation k
        k = np.repeat(np.arange(neq, dtype=np.int32), nmu)
        Me, _, _ = kernels.build_rows(eoff, emon, nv, e, mu, k, W=se.W, threads=threads)
        lead = kernels.row_leads(Me, se.C).reshape(neq, nmu)
        rows = np.zeros(0, dtype=np.int64)        # multiplier indices of L(e, kk), cumulative
        for kk in range(neq):
            lk = lead[kk]
            lk = lk[lk >= 0]
            lk = lk[se.col_deg(lk) == e]
            if len(lk):
                m = se.masks[lk]
                rows = np.concatenate([rows, by_mask[np.searchsorted(sorted_mask, m)]])
            if len(rows):
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
    Dp = min(nv, int(_popcount(mu).max()) + 2)
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


# --- speculate, then verify ------------------------------------------------
#
# A space U = span(basis) is grown by candidate rows without eliminating the
# candidates that add nothing:
#   * K = annihilator of U (kernels.annihilator; cheap because the basis rows
#     from the lead-descending pass are sparse), f = C - dim U columns;
#   * each candidate r gets its syndrome r . K (f bits). r is in U exactly
#     when its syndrome is 0, and a set of candidates is independent modulo U
#     exactly when their syndromes are independent;
#   * a column pass over the syndromes (f columns, small) picks a maximal
#     independent subset; only those rows are eliminated, and every other
#     candidate lies in U + span(subset), by an exact argument, not a
#     probabilistic one.
# For W_D products v_j * n the syndrome is computed from n directly
# ((v_j n) . K = sum over the columns c of n of K[colmap[j][c]]), so the
# product matrix is never formed.

SPLIT = 1.0                 # M_D primal prefix: the first SPLIT * C rows in key order
PASS_ALGORITHM = "blocked"  # measured faster than "sb" on lead-descending rows, 1 and 4 threads
RESTACK = 1 / 16            # a block larger than RESTACK * rank is stacked under a copy of the basis
MAX_SYNDROME_WORDS = 256    # beyond f = 64 * this, candidates are eliminated without the test


class _Space:
    """Echelon basis of a growing space, kept as blocks, plus the provenance
    a certificate needs.

    Block b is one column pass: its input rows were reduced against the
    earlier blocks' basis rows first (kernels.reduce_rows, which only ever
    reads them), so the leads of all blocks are distinct and their pivot rows
    together are an echelon basis. Nothing is copied when a block is added.
    Every row of every block's matrix has a global id gid = base + row. Input
    row q of block b is, before reduction, either row prev[q] (a gid) times
    the monomial mask[q], or the Macaulay row mu[q] * f_{k[q]} (prev = -1);
    the reduction added the basis rows with gids extra[q]."""

    def __init__(self, C, threads, dual=True):
        self.C, self.threads, self.dual = C, threads, dual
        self.blocks = []
        self.next_gid = 0

    @property
    def active(self):
        return [b for b in self.blocks if b["active"]]

    @property
    def rank(self):
        return sum(len(b["cs"]) for b in self.active)

    @property
    def cs(self):
        a = self.active
        return np.concatenate([b["cs"] for b in a]) if a else np.zeros(0, np.int64)

    @property
    def gids(self):
        a = self.active
        return np.concatenate([b["base"] + b["ps"] for b in a]) if a else np.zeros(0, np.int64)

    def basis_blocks(self):
        return [(b["M"], b["ps"], b["cs"], b["base"] + b["ps"]) for b in self.active]

    def addrs_of(self, gids):
        """Addresses of the rows with these gids (for the native kernels)."""
        gids = np.asarray(gids, dtype=np.int64)
        out = np.zeros(len(gids), dtype=np.uint64)
        for b in self.blocks:
            sel = (gids >= b["base"]) & (gids < b["base"] + len(b["M"]))
            if sel.any():
                M = b["M"]
                rel = (gids[sel] - b["base"]).astype(np.uint64)
                out[sel] = np.uint64(M.ctypes.data) + rel * np.uint64(M.shape[1] * 8)
        return out

    def rows_of(self, gids):
        """Copies of the rows with these gids."""
        gids = np.asarray(gids, dtype=np.int64)
        W = self.blocks[0]["M"].shape[1]
        out = np.empty((len(gids), W), dtype=np.uint64)
        for b in self.blocks:
            sel = (gids >= b["base"]) & (gids < b["base"] + len(b["M"]))
            if sel.any():
                out[sel] = b["M"][gids[sel] - b["base"]]
        return out

    def basis_rows(self):
        """Copy of the basis rows, in gids order."""
        return np.concatenate([b["M"][b["ps"]] for b in self.active])

    def add(self, rows, prev, mask, mu, k, keep_ops, fresh=False):
        """Add rows (a fresh array; modified in place) as one new block.
        fresh: the rows have pairwise distinct leads that are not basis leads;
        then the block's pass XORs nothing, its leads stay distinct from the
        basis leads, and no reduction is needed."""
        extra = None
        nb = self.rank
        if fresh:
            pass
        elif nb and len(rows) > RESTACK * nb:
            # many rows: one pass over [basis; rows] (the M4RI-style pass beats
            # row-by-row reduction); the copied basis rows stay pivots, and the
            # old blocks remain only as provenance
            gids = self.gids
            rows = np.ascontiguousarray(np.concatenate([self.basis_rows(), rows]))
            prev = np.concatenate([gids, prev])
            mask = np.concatenate([np.zeros(nb, np.uint64), mask])
            mu = np.concatenate([np.zeros(nb, np.uint64), mu])
            k = np.concatenate([np.full(nb, -1, np.int32), k])
            for b in self.blocks:
                b["active"] = False
        elif self.blocks:
            lead, extra = kernels.reduce_rows(rows, self.C, self.basis_blocks(), keep_ops, self.threads,
                                              full=True)
            live = np.flatnonzero(lead >= 0)
            if not len(live):
                return
            lw, ww = kernels.row_lead_weight(rows)
            o = live[np.lexsort((ww[live], -lw[live]))]
            if len(o) != len(rows) or not np.array_equal(o, np.arange(len(rows))):
                rows = np.ascontiguousarray(rows[o])
                prev, mask, mu, k = prev[o], mask[o], mu[o], k[o]
                if extra is not None:
                    xoff, xs = extra
                    cnt = xoff[o + 1] - xoff[o]
                    extra = (np.concatenate([[0], np.cumsum(cnt)]).astype(np.int64),
                             xs[_csr_ranges(xoff[o], cnt)])
        log = kernels.column_pass(rows, self.C, keep_ops=keep_ops, algorithm=PASS_ALGORITHM,
                                  threads=self.threads)
        self.blocks.append({"M": rows, "ps": log.ps.astype(np.int64), "cs": log.cs.astype(np.int64),
                            "base": self.next_gid, "log": log if keep_ops else None,
                            "prev": np.asarray(prev, np.int64), "mask": np.asarray(mask, np.uint64),
                            "mu": np.asarray(mu, np.uint64), "k": np.asarray(k, np.int32),
                            "extra": extra, "active": True})
        self.next_gid += len(rows)

    def _annihilator(self):
        """K for the current space, or None when the test is not worth it."""
        f = self.C - self.rank
        if not self.dual or not self.blocks or f == 0 or (f + 63) // 64 > MAX_SYNDROME_WORDS:
            return None
        return kernels.annihilator(self.basis_blocks(), self.C)

    def _independent(self, S):
        """Positions of a maximal independent subset of the syndrome rows S,
        preferring earlier rows."""
        f = self.C - self.rank
        log = kernels.column_pass(np.ascontiguousarray(S), f, keep_ops=False, algorithm=PASS_ALGORITHM,
                                  threads=self.threads)
        return np.sort(log.ps.astype(np.int64))

    def _send(self, cand, idx, prev, mask, mu, k, keep_ops, lw=None):
        lc, wc = kernels.row_lead_weight(cand) if lw is None else lw
        idx = idx[lc[idx] >= 0]
        if not len(idx):
            return 0
        o = idx[np.lexsort((wc[idx], -lc[idx]))]
        self.add(np.ascontiguousarray(cand[o]), prev[o], mask[o], mu[o], k[o], keep_ops)
        return len(o)

    def grow(self, cand, prev, mask, mu, k, keep_ops):
        """Make the space span(basis) + span(cand). Returns the number of rows
        that went through elimination; the others were proved to lie in the
        span by their syndromes."""
        if len(cand) == 0 or self.rank == self.C:
            return 0
        lc, wc = kernels.row_lead_weight(cand)
        live = np.flatnonzero(lc >= 0)
        live = live[np.lexsort((wc[live], -lc[live]))]       # preference: sparse rows first
        K = self._annihilator()
        if K is None:
            return self._send(cand, live, prev, mask, mu, k, keep_ops, (lc, wc))
        S = kernels.syndromes(cand, K, idx=live, threads=self.threads)
        del K
        return self._send(cand, live[self._independent(S)], prev, mask, mu, k, keep_ops, (lc, wc))

    def grow_products(self, gids, nv, colmap, keep_ops, lead_cols=None, lead_masks=None):
        """Make the space span(basis) + span{v_j * row g : g in gids, all j}.
        lead_cols / lead_masks: the rows' leads and their monomial masks."""
        n = len(gids)
        if not n or self.rank == self.C:
            return 0
        W = self.blocks[0]["M"].shape[1]
        gids = np.asarray(gids, dtype=np.int64)
        sent = 0
        if self.dual and lead_masks is not None:
            # v_j * n has lead x_j * lead(n) when x_j is not in lead(n) (later
            # monomials of n stay later or drop in degree); the products whose
            # lead is not a basis lead, one per lead, are new and independent
            j = np.repeat(np.arange(nv, dtype=np.int64), n)
            f = np.tile(np.arange(n, dtype=np.int64), nv)
            ok = (lead_masks[f] >> j.astype(np.uint64)) & np.uint64(1) == 0
            j, f = j[ok], f[ok]
            pl = colmap[j, lead_cols[f]].astype(np.int64)
            have = np.zeros(self.C, dtype=bool)
            have[self.cs] = True
            ok = (pl >= 0) & ~have[np.maximum(pl, 0)]
            j, f, pl = j[ok], f[ok], pl[ok]
            if len(pl):
                _, first = np.unique(pl, return_index=True)
                j, f, pl = j[first], f[first], pl[first]
                addrs = self.addrs_of(gids[f])
                P = kernels.product_pairs(addrs, j, W, self.C, colmap,
                                          rows=self.rows_of(gids[f]) if kernels.backend() != "native" else None)
                lw, ww = kernels.row_lead_weight(P)
                good = lw == pl                    # guard: the lemma, checked; others go to the test below
                o = np.flatnonzero(good)[np.lexsort((ww[good], -lw[good]))]
                self.add(np.ascontiguousarray(P[o]), gids[f][o],
                         np.left_shift(np.uint64(1), j[o].astype(np.uint64)),
                         np.zeros(len(o), np.uint64), np.full(len(o), -1, np.int32), keep_ops, fresh=True)
                sent += len(o)
        if self.rank == self.C:
            return sent
        addrs = self.addrs_of(gids)
        rows = self.rows_of(gids) if kernels.backend() != "native" else None
        K = self._annihilator()
        if K is None:
            q = np.arange(nv * n)
        else:
            S = kernels.product_syndromes(addrs, W, self.C, colmap, nv, K, self.threads, rows=rows)
            del K
            q = self._independent(S)
            del S
        j, f = np.divmod(q, n)
        P = kernels.product_pairs(addrs[f], j, W, self.C, colmap,
                                  rows=None if rows is None else rows[f])
        prev = gids[f]
        mask = np.left_shift(np.uint64(1), j.astype(np.uint64))
        return sent + self._send(P, np.arange(len(q)), prev, mask, np.zeros(len(q), np.uint64),
                                 np.full(len(q), -1, np.int32), keep_ops)

    def certificate(self):
        """(mu, k) pairs summing to the basis row whose lead is the constant
        column (the last column). The trace is a set of (gid, mask) pairs
        taken with parity, walked back block by block."""
        const = self.C - 1
        hold = [i for i, b in enumerate(self.blocks) if (b["cs"] == const).any()][0]   # first, so logged
        b = self.blocks[hold]
        cur_g = np.array([b["base"] + b["ps"][np.flatnonzero(b["cs"] == const)[0]]], dtype=np.int64)
        cur_m = np.zeros(1, dtype=np.uint64)
        out_mu, out_k = [], []
        for b in reversed(self.blocks[:hold + 1]):
            lo, hi = b["base"], b["base"] + len(b["M"])
            sel = (cur_g >= lo) & (cur_g < hi)
            if not sel.any():
                continue
            g, m = cur_g[sel] - lo, cur_m[sel]
            cur_g, cur_m = cur_g[~sel], cur_m[~sel]
            ml, inv = np.unique(m, return_inverse=True)
            nw = (len(ml) + 63) // 64
            S = np.zeros((len(b["M"]), nw), dtype=np.uint64)
            np.bitwise_xor.at(S, (g, inv >> 6), np.left_shift(np.uint64(1), (inv & 63).astype(np.uint64)))
            kernels.backtrace(b["log"], S)
            bits = np.unpackbits(S.view(np.uint8), axis=1, bitorder="little")[:, :len(ml)]
            r, t = np.nonzero(bits)
            mm = ml[t]
            pr = b["prev"][r]
            isp = pr >= 0
            new_g, new_m = [cur_g, pr[isp]], [cur_m, mm[isp] | b["mask"][r[isp]]]
            out_mu.append(b["mu"][r[~isp]] | mm[~isp])
            out_k.append(b["k"][r[~isp]].astype(np.int64))
            if b["extra"] is not None:
                xoff, xs = b["extra"]
                cnt = xoff[r + 1] - xoff[r]
                new_g.append(xs[_csr_ranges(xoff[r], cnt)].astype(np.int64))
                new_m.append(np.repeat(mm, cnt))
            cur_g, cur_m = _odd_pairs(np.concatenate(new_g), np.concatenate(new_m))
        if len(cur_g):
            raise AssertionError("certificate trace did not reach the Macaulay rows")
        k, mu = _odd_pairs(np.concatenate(out_k), np.concatenate(out_mu))
        return sorted(zip(mu.tolist(), k.tolist()))


def _csr_ranges(starts, counts):
    """Concatenated index ranges [starts[i], starts[i] + counts[i])."""
    total = int(counts.sum())
    if not total:
        return np.zeros(0, dtype=np.int64)
    rep = np.repeat(starts - np.concatenate([[0], np.cumsum(counts)[:-1]]), counts)
    return rep + np.arange(total)


def _odd_pairs(a, b):
    """The (a, b) pairs that occur an odd number of times, sorted by (a, b)."""
    if not len(a):
        return a, b
    o = np.lexsort((b, a))
    a, b = a[o], b[o]
    start = np.r_[True, (a[1:] != a[:-1]) | (b[1:] != b[:-1])]
    first = np.flatnonzero(start)
    cnt = np.diff(np.r_[first, len(a)])
    keep = first[cnt & 1 == 1]
    return a[keep], b[keep]


def _key_order(mu, k):
    """Row permutation into key order (k, deg mu, -column of mu); within a
    degree the column order is mask order, so -column is mask descending."""
    return np.lexsort((~mu, _popcount(mu), k))


def _m_space(eqs, nv, D, keep_ops, use_f5=True, order="lead_desc", dual=True, threads=None):
    """Span of the Macaulay rows of M_D as a _Space, and the row counts."""
    neq = len(eqs)
    sh = shape(nv, D)
    R = len(sh.mu_mask) * neq
    idx = np.flatnonzero(f5_keep(nv, D, eqs, threads)) if use_f5 else np.arange(R)
    eoff, emon = kernels.pack_eqs(eqs)
    mu = sh.mu_mask[idx // max(neq, 1)]
    k = (idx % max(neq, 1)).astype(np.int32)
    sp = _Space(sh.C, threads, dual)
    n = len(mu)
    split = n if not dual else min(n, max(1, int(SPLIT * sh.C)))
    if dual and split < n:
        o = _key_order(mu, k)
        mu, k = mu[o], k[o]
    head, tail = slice(0, split), slice(split, n)
    mh, kh = mu[head], k[head]
    if order == "lead_desc":
        _, lead, weight = kernels.build_rows(eoff, emon, nv, D, mh, kh, threads=threads)
        perm = np.lexsort((weight, -lead))
        mh, kh = mh[perm], kh[perm]
    elif order != "built":
        raise ValueError(f"unknown order {order!r}")
    A, _, _ = kernels.build_rows(eoff, emon, nv, D, mh, kh, W=sh.W, threads=threads)
    nh = len(mh)
    sp.add(A, np.full(nh, -1, np.int64), np.zeros(nh, np.uint64), mh, kh, keep_ops)
    del A
    sent = nh
    if split < n:
        mt, kt = mu[tail], k[tail]
        Q, _, _ = kernels.build_rows(eoff, emon, nv, D, mt, kt, W=sh.W, threads=threads)
        nt = len(mt)
        sent += sp.grow(Q, np.full(nt, -1, np.int64), np.zeros(nt, np.uint64), mt, kt, keep_ops)
    return sp, R, n, sent


def macaulay_profile(eqs, nv, D, want_cert=True, use_f5=True, order="lead_desc", threads=None,
                     dual=True):
    """M_D record by rank profile -> (record, certificate or None, info).

    record: {"rank", "one", "dims_by_deg"}, equal to Closure.macaulay_closure.
    info: {"solver", "rows_total", "rows_kept", "rows_eliminated", "pivcols"}
    (pivcols = sorted pivot columns in Closure(nv, D, neq) column order;
    rows_eliminated = rows that went through a column pass, the rest were
    proved to lie in the span by the annihilator test)."""
    sh = shape(nv, D)
    sp, R, n, sent = _m_space(eqs, nv, D, want_cert, use_f5, order, dual, threads)
    leads = np.sort(sp.cs)
    one = bool(sp.rank) and int(leads[-1]) == sh.const_col
    deg = sh.col_deg(leads)
    rec = {"rank": sp.rank, "one": one,
           "dims_by_deg": [int((deg <= d).sum()) for d in range(D + 1)]}
    info = {"solver": SOLVER, "rows_total": R, "rows_kept": int(n), "rows_eliminated": int(sent),
            "pivcols": leads.tolist()}
    cert = None
    if one and want_cert:
        cert = sp.certificate()
        if not cert_sums_to_one(cert, eqs, nv, threads):
            raise AssertionError("rank-profile certificate does not sum to 1")
    return rec, cert, info


def w_profile(eqs, nv, D, want_cert=True, threads=None, dual=True):
    """W_D record by rank profile -> (record, certificate or None, info).

    record: the fields of Closure.w_closure (iterations_to_fixpoint, dims,
    final_dim, one, one_first_iteration, dims_by_deg, new_fallen_per_iteration,
    stack_rows_per_iteration), each a function of the spaces V_i alone, so
    equal to the exact engine's.

    Same iteration as Closure.w_closure, V_{i+1} = V_i + sum_j v_j * N_i with
    N_i the basis rows of degree <= D-1 whose leads are new. Any complement of
    the old low part in the new one gives the same V_{i+1} (v_j times the old
    low part already lies in V_i), so N_i is taken from this echelon basis.
    At i = 0 there is one more pruning: M_{D-1} is a subspace of M_D's low
    part and v_j * M_{D-1} lies in M_D (v_j * mu * f is a Macaulay row of
    M_D), so only basis rows whose leads are not leads of M_{D-1} -- a
    complement of M_{D-1} in V_0's low part, since leads of a subspace are a
    subset and distinct leads are independent -- need products. The products
    are added to the space by _Space.grow (speculate, then verify). The record
    reports the counts as the exact engine defines them.

    The certificate (when 1 is reached) is a flat list of (mu, k) pairs whose
    sum is 1, checked by cert_sums_to_one; mu may exceed degree D - 2 (product
    rows), as with Closure.w_closure. It is not the exact engine's
    certificate.

    Products: v_j * n has lead x_j * lead(n) whenever x_j is not in lead(n)
    (the other monomials of n of top degree stay after it in colex order and
    cannot coincide with it; those containing x_j or of lower degree end in a
    lower degree). The products whose predicted lead is not a lead of the
    space, one per lead, are therefore new and independent, and are added
    without reduction (the prediction is checked against the formed row). The
    rest go through the syndrome test of _Space.grow_products."""
    sh = shape(nv, D)
    col_deg = sh.col_deg(np.arange(sh.C))
    sp, R_full, n_kept, sent = _m_space(eqs, nv, D, want_cert, dual=dual, threads=threads)
    dims = [sp.rank]
    one_first = 0 if sp.rank and int(sp.cs.max()) == sh.const_col else None
    covered = set()
    if D >= 3:
        _, _, info_lo = macaulay_profile(eqs, nv, D - 1, want_cert=False, threads=threads, dual=dual)
        lo_masks = shape(nv, D - 1).masks[np.asarray(info_lo["pivcols"], dtype=np.int64)]
        covered = set(sh.cols_of(lo_masks).tolist())
    prev_low_exact = set()
    new_fallen, stack_rows = [], [R_full]
    colmap, _ = sh.product_tables
    i = 0
    while True:
        leads = sp.cs
        low = col_deg[leads] <= D - 1
        low_leads = set(int(x) for x in leads[low])
        new_exact = len(low_leads - prev_low_exact)
        skip = covered if i == 0 else prev_low_exact
        new = np.array([t for t in np.flatnonzero(low) if int(leads[t]) not in skip], dtype=np.int64)
        prev_low_exact = low_leads
        new_fallen.append(new_exact)
        stack_rows.append(sp.rank + nv * new_exact)
        keep = want_cert and one_first is None
        r0 = sp.rank
        sent += sp.grow_products(sp.gids[new], nv, colmap, keep, lead_cols=leads[new],
                                 lead_masks=sh.masks[leads[new]])
        if sp.rank == r0:
            break
        i += 1
        dims.append(sp.rank)
        if one_first is None and int(sp.cs.max()) == sh.const_col:
            one_first = i
    final_leads = sp.cs
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
    info = {"solver": SOLVER, "rows_total": R_full, "rows_kept": int(n_kept), "rows_eliminated": int(sent)}
    cert = None
    if one_first is not None and want_cert:
        cert = sp.certificate()
        if not cert_sums_to_one(cert, eqs, nv, threads):
            raise AssertionError("rank-profile W_D certificate does not sum to 1")
    return rec, cert, info
