"""Macaulay closures M_D and W_D over B = F_2[v]/(v_i^2 + v_i) on the fast
kernels, plus the trace instrument ``eliminate``.

Ported from experiments/EXP-CERTBIN-e94b27/impl/closure.py (``Closure``,
``eval_cert``, ``cert_to_json``) and EXP-CERTBIN-4e92d7/impl/elim.py
(``eliminate``). Conventions, iteration, fixpoint rule, record fields and
certificate extraction are unchanged; only the elimination, product and
back-trace kernels are swapped for ``kernels.*``. Equality with the archived
engines is tested in tests/test_gf2_kernels.py.

Conventions (EXP-CERTBIN-4e92d7 spec object.macaulay_M_D):
  * monomials are bit masks (bit i = v_i); multilinear product = OR;
  * row multipliers mu: degree ascending, then ascending sorted index tuple;
    Macaulay row index = mu_index * neq + k; zero rows retained;
  * columns: descending degrevlex (v_0 > ... > v_{nv-1}), constant LAST;
  * bit-packed rows: column c is bit (c & 63) of word (c >> 6).
"""
from __future__ import annotations

import signal
from itertools import combinations

import numpy as np

from . import kernels
from .kernels import OpLog


# ---------------------------------------------------------------------------
# monomial orders (EXP-CERTBIN-4e92d7 impl/macaulay.py)
# ---------------------------------------------------------------------------
def mu_order(dmax, nv):
    out = []
    for d in range(dmax + 1):
        out.extend(combinations(range(nv), d))
    return out


def mono_mask(m):
    s = 0
    for i in m:
        s |= 1 << i
    return s


def column_order(D, nv):
    return sorted(mu_order(D, nv), key=lambda m: (-len(m), mono_mask(m)))


# ---------------------------------------------------------------------------
# trace instrument (EXP-CERTBIN-4e92d7 elim.eliminate)
# ---------------------------------------------------------------------------
class ElimResult:
    """Fields as the archived ElimResult: p, c (lists), X (list of arrays or
    None), rank, pivcols, Z, ops_strict, h_rank, h_set, h_strict, h_ops; plus
    ``log`` (the OpLog)."""

    __slots__ = ("log", "p", "c", "X", "rank", "pivcols", "Z", "ops_strict",
                 "h_rank", "h_set", "h_strict", "h_ops")


def eliminate(M_orig, C, keep_ops=True, with_row_pass=True):
    """Column pass + trace hashes (+ separate row pass) on a copy of M_orig.

    Returns (res, cpass, leads) as the archived ``eliminate``; cpass/leads are
    None without the row pass. The archived function always kept the op log
    for h_ops; keep_ops=False here drops only the X view from ``res``."""
    M = M_orig.copy()
    log = kernels.column_pass(M, C, keep_ops=True)
    res = ElimResult()
    res.log = log
    res.p = log.ps.tolist()
    res.c = log.cs.tolist()
    res.X = log.Xs if keep_ops else None
    res.rank = log.K
    res.pivcols = sorted(res.c)
    res.ops_strict = log.ops_strict
    cpass = leads = None
    if with_row_pass:
        Z, leads = kernels.row_pass(M_orig, C)
        res.Z = Z
        cpass = (leads == res.pivcols) and (len(Z) == M_orig.shape[0] - res.rank)
    else:
        res.Z = None
    h = kernels.trace_hashes(log, res.Z if res.Z is not None else [])
    res.h_rank, res.h_strict, res.h_ops = h["h_rank"], h["h_strict"], h["h_ops"]
    res.h_set = h["h_set"] if with_row_pass else None
    return res, cpass, leads


# ---------------------------------------------------------------------------
# closures (EXP-CERTBIN-e94b27 impl/closure.py)
# ---------------------------------------------------------------------------
class WatchdogExpired(Exception):
    pass


def _alarm(signum, frame):
    raise WatchdogExpired()


class Closure:
    def __init__(self, nv, D, neq):
        self.nv, self.D, self.neq = nv, D, neq
        self.cols = column_order(D, nv)
        self.C = len(self.cols)
        self.W = (self.C + 63) // 64
        self.col_mask = np.array([mono_mask(m) for m in self.cols], dtype=np.int64)
        self.col_deg = np.array([len(m) for m in self.cols], dtype=np.int64)
        self.const_col = self.C - 1
        assert self.cols[-1] == ()
        self.mask2col = np.full(1 << nv, -1, dtype=np.int64)
        self.mask2col[self.col_mask] = np.arange(self.C)
        self.mus = mu_order(D - 2, nv)
        self.mu_mask = np.array([mono_mask(m) for m in self.mus], dtype=np.int64)
        self.R = len(self.mus) * neq
        low = np.flatnonzero(self.col_deg <= D - 1)
        self.maps = []
        # colmap[j, c]: column of v_j * (column c) for c of degree <= D-1, else -1
        self.colmap = np.full((nv, self.C), -1, dtype=np.int32)
        for j in range(nv):
            bj = np.int64(1 << j)
            has = (self.col_mask[low] & bj) != 0
            A = low[~has]
            tA = self.mask2col[self.col_mask[A] | bj]
            assert np.all(tA >= 0)
            self.maps.append((A, tA, low[has]))
            self.colmap[j, A] = tA
            self.colmap[j, low[has]] = low[has]

    # ---- packing -------------------------------------------------------
    def pack(self, dense):
        n = dense.shape[0]
        pad = self.W * 64 - self.C
        if pad:
            dense = np.concatenate([dense, np.zeros((n, pad), dtype=np.uint8)], axis=1)
        b = np.packbits(dense, axis=1, bitorder="little")
        return np.ascontiguousarray(b).view(np.uint64).reshape(n, self.W).copy()

    def unpack(self, M):
        b = M.view(np.uint8).reshape(M.shape[0], self.W * 8)
        return np.unpackbits(b, axis=1, bitorder="little")[:, :self.C]

    def vec(self, masks):
        d = np.zeros((1, self.C), dtype=np.uint8)
        for m in masks:
            d[0, self.mask2col[m]] ^= 1
        return self.pack(d)[0]

    # ---- Macaulay matrix --------------------------------------------------
    def build_M(self, eqs):
        """eqs: neq lists of monomial masks (each f_k, deg <= 2) -> packed M_D."""
        # Written straight into the packed layout with one scatter-XOR (the
        # archived build filled a dense uint8 matrix and packed it: 212 MB at
        # D = 5). XOR accumulation keeps the archived cancellation when two
        # products mu*m collapse to one monomial.
        assert len(eqs) == self.neq
        M = np.zeros((self.R, self.W), dtype=np.uint64)
        base = np.arange(len(self.mus), dtype=np.int64) * self.neq
        rr, cc = [], []
        for k, f in enumerate(eqs):
            if not len(f):
                continue
            ms = np.asarray(f, dtype=np.int64)
            cols = self.mask2col[self.mu_mask[None, :] | ms[:, None]]  # (|f|, nmu)
            assert np.all(cols >= 0)
            rr.append(np.broadcast_to(base + k, cols.shape).ravel())
            cc.append(cols.ravel())
        if rr:
            kernels.xor_bits(M, np.concatenate(rr), np.concatenate(cc))
        return M

    def row_pair(self, r):
        return int(self.mu_mask[r // self.neq]), int(r % self.neq)

    def products(self, rows):
        return kernels.products(np.ascontiguousarray(rows), self.colmap, self.maps,
                                self.nv, self.C, self.W)

    # ---- closures ------------------------------------------------------------
    def macaulay_closure(self, eqs, want_cert=True):
        M = self.build_M(eqs)
        log = kernels.column_pass(M, self.C, keep_ops=want_cert)
        cs = log.cs
        one = bool(self.const_col in set(cs.tolist()))
        res = {"rank": log.K, "one": one}
        leads = np.sort(cs)
        res["dims_by_deg"] = [int((self.col_deg[leads] <= d).sum()) for d in range(self.D + 1)]
        cert = None
        if one and want_cert:
            pstar = int(log.ps[np.flatnonzero(cs == self.const_col)[0]])
            cert = self._extract([{"log": log, "origin": None}], pstar)
        return res, cert

    def w_closure(self, eqs, want_cert=True, deadline_s=None, M0=None):
        """Least fixpoint W_D -> (record, certificate or None)."""
        if deadline_s:
            old = signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(int(deadline_s))
        try:
            return self._w_closure(eqs, want_cert, M0)
        finally:
            if deadline_s:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old)

    def _w_closure(self, eqs, want_cert, M0):
        D = self.D
        M = self.build_M(eqs) if M0 is None else M0.copy()
        its = []
        log = kernels.column_pass(M, self.C, keep_ops=want_cert)
        ps, cs = log.ps.astype(np.int64), log.cs.astype(np.int64)
        dims = [int(len(ps))]
        one_first = 0 if self.const_col in set(cs.tolist()) else None
        its.append({"log": log, "origin": None})
        prev_low = set()
        stack_rows = [int(M.shape[0])]
        new_fallen = []
        i = 0
        while True:
            order = np.argsort(cs, kind="stable")
            prow = ps[order]
            leads = cs[order]
            basis = M[prow]
            low = self.col_deg[leads] <= D - 1
            lowidx = np.flatnonzero(low)
            new = np.array([t for t in lowidx if int(leads[t]) not in prev_low], dtype=np.int64)
            prev_low = set(int(x) for x in leads[low])
            new_fallen.append(int(new.size))
            P = self.products(basis[new])
            M = np.concatenate([basis, P])
            del P
            stack_rows.append(int(M.shape[0]))
            keep = want_cert and one_first is None
            log2 = kernels.column_pass(M, self.C, keep_ops=keep)
            ps2, cs2 = log2.ps.astype(np.int64), log2.cs.astype(np.int64)
            if keep:
                its.append({"log": log2,
                            "origin": {"nb": int(len(prow)), "prow": prow,
                                       "newrows": prow[new], "nnew": int(new.size)}})
            if len(ps2) == dims[-1]:
                final_basis, final_leads = basis, leads
                break
            i += 1
            dims.append(int(len(ps2)))
            if one_first is None and self.const_col in set(cs2.tolist()):
                one_first = i
            ps, cs = ps2, cs2
        rec = {
            "iterations_to_fixpoint": i,
            "dims": dims,
            "final_dim": dims[-1],
            "one": one_first is not None,
            "one_first_iteration": one_first,
            "dims_by_deg": [int((self.col_deg[final_leads] <= d).sum()) for d in range(D + 1)],
            "new_fallen_per_iteration": new_fallen,
            "stack_rows_per_iteration": stack_rows,
        }
        self._final = (final_basis, final_leads)
        cert = None
        if one_first is not None and want_cert:
            itl = its[:one_first + 1]
            pstar = int(itl[one_first]["log"].ps[-1])
            cert = self._extract(itl, pstar)
        return rec, cert

    def member(self, masks):
        """Is the polynomial (list of monomial masks) in the last computed W_D?"""
        basis, leads = self._final
        v = self.vec(masks).copy()
        for t in range(len(leads)):
            c = int(leads[t])
            if (int(v[c >> 6]) >> (c & 63)) & 1:
                v ^= basis[t]
        return not v.any()

    # ---- certificate extraction ------------------------------------------------
    def _extract(self, itl, pstar):
        """Trace row pstar of the last iteration in itl (final state = 1) back to
        Macaulay rows -> sorted list of (mu_mask, k) pairs."""
        cur = {pstar: {0}}
        for level in range(len(itl) - 1, -1, -1):
            it = itl[level]
            ml = sorted({m for s in cur.values() for m in s})
            pos = {m: t for t, m in enumerate(ml)}
            nw = (len(ml) + 63) // 64
            nrows = self._nrows(itl, level)
            S = np.zeros((nrows, nw), dtype=np.uint64)
            for r, ms in cur.items():
                for m in ms:
                    t = pos[m]
                    S[r, t >> 6] ^= np.uint64(1 << (t & 63))
            kernels.backtrace(it["log"], S)
            nz = np.flatnonzero(S.any(axis=1))
            nxt = {}
            org = it["origin"]
            for r in nz.tolist():
                bits = []
                for w in range(nw):
                    word = int(S[r, w])
                    while word:
                        b = (word & -word).bit_length() - 1
                        bits.append(ml[w * 64 + b])
                        word &= word - 1
                if org is None:
                    for m in bits:
                        key = (m, r)
                        nxt[key] = nxt.get(key, 0) ^ 1
                else:
                    if r < org["nb"]:
                        pr, jm = int(org["prow"][r]), 0
                    else:
                        q = r - org["nb"]
                        j, f = divmod(q, org["nnew"])
                        pr, jm = int(org["newrows"][f]), 1 << j
                    s = nxt.setdefault(pr, set())
                    for m in bits:
                        s ^= {m | jm}
            if org is None:
                keys = {}
                for (m, r), par in nxt.items():
                    if not par:
                        continue
                    mu, k = self.row_pair(r)
                    kk = (m | mu, k)
                    keys[kk] = keys.get(kk, 0) ^ 1
                return sorted(kk for kk, par in keys.items() if par)
            cur = {r: s for r, s in nxt.items() if s}
        raise AssertionError("unreachable")

    def _nrows(self, itl, level):
        if level == 0:
            return self.R
        org = itl[level]["origin"]
        return org["nb"] + self.nv * org["nnew"]


def eval_cert(cert, eqs):
    """Engine-side check (NOT an independent verifier): sum mu*f_k as a set of
    monomial masks; a refutation certificate evaluates to [0] (the constant)."""
    acc = {}
    for mu, k in cert:
        for m in eqs[k]:
            x = mu | m
            acc[x] = acc.get(x, 0) ^ 1
    return sorted(x for x, p in acc.items() if p)


def cert_to_json(cert):
    """[(mu as sorted tuple of variable indices, k)] sorted."""
    out = []
    for mu, k in cert:
        out.append([[i for i in range(64) if (mu >> i) & 1], k])
    out.sort(key=lambda x: (x[0], x[1]))
    return out
