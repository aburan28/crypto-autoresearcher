"""Closures M_D and W_D over B = F_2[v_0..v_{nv-1}]/(v_i^2 + v_i), with
certificate extraction. EXP-CERTBIN-e94b27 (RC-1), written under
TASK-20260924-41c7be.

Generic in the number of variables nv and equations neq (the self-test runs it
on 6-variable systems; the experiment on nv = 18, neq = 17).

Conventions (identical to EXP-CERTBIN-4e92d7, spec object.macaulay_M_D):
  * monomials are bit masks (bit i = v_i); the multilinear product of two
    monomials is the OR of their masks;
  * row multipliers mu: degree ascending, then ascending sorted index tuple;
    Macaulay row index = mu_index * neq + k; zero rows retained;
  * columns: descending degrevlex (v_0 > ... > v_{nv-1}), constant LAST
    (macaulay.column_order, copied from EXP-CERTBIN-4e92d7);
  * bit-packed rows: column c is bit (c & 63) of word (c >> 6).

W_D (spec object.mutant_closure_W_D) is computed by the iteration
  W^(0) = rowspace(M_D),
  W^(i+1) = W^(i) + span{ v_j * b : b in a basis of W^(i) cap B_{<=D-1} }.
Implementation note (exactness): v_j * b for b in W^(i-1) cap B_{<=D-1} already
lies in W^(i), so it suffices to add the products of a COMPLEMENT of
W^(i-1) cap B_{<=D-1} inside W^(i) cap B_{<=D-1}. The echelon rows whose
leading monomial has degree <= D-1 and did not lead a row at iteration i-1 are
such a complement (their leading monomials are distinct and not leading
monomials of W^(i-1) cap B_{<=D-1}). The iterates W^(i), their dimensions, the
fixpoint index and the first iteration containing 1 are therefore identical to
the literal iteration's.

Certificates: every elimination keeps its operation log (pivot p, column c,
rows X that received row p). The row that equals 1 is traced back through the
log(s) to a set of pairs (mu, k) with sum mu * f_k = 1 in B (products v_j * g
push the multiplier into mu, because multilinear reduction is a ring map).
"""
import signal

import numpy as np

from macaulay import column_order, mu_order, mono_mask

ONE = np.uint64(1)


class WatchdogExpired(Exception):
    pass


def _alarm(signum, frame):
    raise WatchdogExpired()


def echelon(M, C, keep_log=True):
    """Column-major forward elimination (the EXP-CERTBIN-4e92d7 column pass,
    re-implemented with int32 logs): for each column c, the smallest unused
    row index with a 1 in c is the pivot p; row p is XORed into every other
    unused row with a 1 in c (set X). M is modified in place.
    Returns (ps int64, cs int64, Xs list of int32 arrays or None)."""
    R, W = M.shape
    unused = np.ones(R, dtype=bool)
    ps, cs, Xs = [], [], []
    shifts = [np.uint64(b) for b in range(64)]
    for c in range(C):
        w = c >> 6
        col = ((M[:, w] >> shifts[c & 63]) & ONE).astype(bool)
        col &= unused
        idx = np.flatnonzero(col)
        if idx.size == 0:
            continue
        p = int(idx[0])
        X = idx[1:]
        if X.size:
            M[X, w:] ^= M[p, w:]
        unused[p] = False
        ps.append(p)
        cs.append(c)
        if keep_log:
            Xs.append(X.astype(np.int32))
    return (np.array(ps, dtype=np.int64), np.array(cs, dtype=np.int64),
            Xs if keep_log else None)


def backtrace(ps, Xs, S):
    """S (n_rows, nw) uint64: bit t of row r says that row r (FINAL state)
    belongs to target t. Returns S expressed over the ORIGINAL row states
    (modified in place)."""
    for k in range(len(ps) - 1, -1, -1):
        X = Xs[k]
        if X.size:
            par = np.bitwise_xor.reduce(S[X], axis=0)
            if par.any():
                S[ps[k]] ^= par
    return S


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
        for j in range(nv):
            bj = np.int64(1 << j)
            has = (self.col_mask[low] & bj) != 0
            A = low[~has]
            tA = self.mask2col[self.col_mask[A] | bj]
            assert np.all(tA >= 0)
            self.maps.append((A, tA, low[has]))

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
        """eqs: list of neq lists of monomial masks (each f_k, deg <= 2).
        Returns the packed M_D (R x W)."""
        assert len(eqs) == self.neq
        dense = np.zeros((self.R, self.C), dtype=np.uint8)
        base = np.arange(len(self.mus), dtype=np.int64) * self.neq
        for k, f in enumerate(eqs):
            rows = base + k
            for m in f:
                cols = self.mask2col[self.mu_mask | np.int64(m)]
                assert np.all(cols >= 0)
                dense[rows, cols] ^= 1
        return self.pack(dense)

    def row_pair(self, r):
        return int(self.mu_mask[r // self.neq]), int(r % self.neq)

    # ---- products v_j * rows (rows lie in B_{<=D-1}) ------------------------
    def products(self, rows, chunk=2048):
        """Returns (18 * n) packed rows, j-major: row j*n + f = v_j * rows[f]."""
        n = rows.shape[0]
        out = np.zeros((self.nv * n, self.W), dtype=np.uint64)
        if n == 0:
            return out
        for s in range(0, n, chunk):
            d = self.unpack(rows[s:s + chunk])
            m = d.shape[0]
            for j in range(self.nv):
                A, tA, Bc = self.maps[j]
                o = np.zeros_like(d)
                o[:, tA] = d[:, A]
                o[:, Bc] ^= d[:, Bc]
                out[j * n + s:j * n + s + m] = self.pack(o)
        return out

    # ---- closures ------------------------------------------------------------
    def macaulay_closure(self, eqs, want_cert=True):
        M = self.build_M(eqs)
        ps, cs, Xs = echelon(M, self.C, keep_log=want_cert)
        one = bool(self.const_col in set(cs.tolist()))
        res = {"rank": int(len(ps)), "one": one}
        leads = np.sort(cs)
        res["dims_by_deg"] = [int((self.col_deg[leads] <= d).sum()) for d in range(self.D + 1)]
        cert = None
        if one and want_cert:
            pstar = int(ps[np.flatnonzero(cs == self.const_col)[0]])
            cert = self._extract([{"ps": ps, "Xs": Xs, "origin": None}], pstar)
        return res, cert

    def w_closure(self, eqs, want_cert=True, deadline_s=None, M0=None):
        """Least fixpoint W_D. Returns (record, certificate or None).
        deadline_s: per-instance watchdog (signal.alarm); on expiry raises
        WatchdogExpired."""
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
        its = []          # per iteration: ps, Xs, origin (for certificate extraction)
        ps, cs, Xs = echelon(M, self.C, keep_log=want_cert)
        dims = [int(len(ps))]
        one_first = 0 if self.const_col in set(cs.tolist()) else None
        its.append({"ps": ps, "Xs": Xs, "origin": None})
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
            ps2, cs2, Xs2 = echelon(M, self.C, keep_log=keep)
            if keep:
                its.append({"ps": ps2, "Xs": Xs2,
                            "origin": {"nb": int(len(prow)), "prow": prow,
                                       "newrows": prow[new], "nnew": int(new.size)}})
            if len(ps2) == dims[-1]:
                # fixpoint: W^(i+1) = W^(i); W_D = W^(i)
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
            pstar = self._pstar_cache(itl, one_first)
            cert = self._extract(itl, pstar)
        return rec, cert

    def _pstar_cache(self, itl, one_first):
        # the echelon that first contained 1: its last pivot is the constant
        # column (the constant column is the last column)
        return int(itl[one_first]["ps"][-1])

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
        """Trace the row pstar of the last iteration in itl (whose final state
        is the constant 1) back to Macaulay rows. Returns the certificate as a
        sorted list of (mu_mask, k) pairs (XOR semantics already applied)."""
        cur = {pstar: {0}}              # row -> set of multiplier masks (sparse)
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
            backtrace(it["ps"], it["Xs"], S)
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
    """Engine-side check (NOT the independent verifier): sum mu*f_k as a set of
    monomial masks."""
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
