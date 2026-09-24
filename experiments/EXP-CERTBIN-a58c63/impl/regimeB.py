"""Regime B (new for EXP-CERTBIN-a58c63): the undescended system over F_{2^n}.

Ring F_{2^n}[x_1, x_2]; generators
  g_0 = c1 x1^2 x2^2 + c2 x1^2 + c3 x2^2 + c4 x1 x2 + c5
        (S_3 with x_3 = x_R: (c1..c5) = (1, x_R^2, x_R^2, x_R, B)),
  g_1 = L_V(x_1), g_2 = L_V(x_2), L_V(X) = prod_{v in V}(X - v) = sum_{i<=l} lambda_i X^{2^i}.
Macaulay matrix at D = 66 (spec object.regime_B):
  rows    block 0: mu*g_0, deg mu <= D - 4; block 1: nu*g_1, deg nu <= D - 2^l;
          block 2: nu*g_2. Within a block: degree ascending, then the exponent
          of x_1 DESCENDING. Row index = position in block 0, 1, 2.
  columns every x_1^a x_2^b with a + b <= D, DESCENDING degrevlex with
          x_1 > x_2 (higher degree first; within degree x_1^d, x_1^{d-1} x_2,
          ..., x_2^d); the constant LAST.
The elimination (THE REGIME-B SOLVER): column-major; at column c, among rows
not yet used as pivot rows, the one with the smallest ORIGINAL index and a
nonzero entry is the pivot p; record (p, c); for every other unused row i with
a nonzero entry at c: row_i <- row_i + (M[i, c] / M[p, c]) * row_p (set X).
Rows never move and pivot rows are not rescaled.

Speed invariant (same argument as the Stage-1 README): after the columns
before c are processed, every unused row is zero at every column before c, so
the row update may be restricted to the pivot row's nonzero columns >= c.
The self-test compares the op log with a literal transcription of the rule.
"""
import hashlib
import json

import numpy as np


def canon(obj):
    return json.dumps(obj, separators=(",", ":"))


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


# ---------------------------------------------------------------------------
def linearized_LV(F, l):
    """lambda_0..lambda_l of L_V(X) = prod_{v in V}(X - v), V = span{1, t, ..., t^{l-1}},
    by the subspace recursion L_{W + <w>}(X) = L_W(X)^2 + L_W(w) L_W(X),
    starting from L_{0}(X) = X. Returns a list of l + 1 field elements."""
    lam = [1]  # L_0(X) = X  -> coefficient of X^{2^0}
    for j in range(l):
        w = 1 << j
        # L_W(w) = sum lam_i w^{2^i}
        Lw = 0
        for i, li in enumerate(lam):
            p = w
            for _ in range(i):
                p = F.mul(p, p)
            Lw ^= F.mul(li, p)
        new = [0] * (len(lam) + 1)
        for i, li in enumerate(lam):
            new[i + 1] ^= F.mul(li, li)     # (sum li X^{2^i})^2 = sum li^2 X^{2^{i+1}}
            new[i] ^= F.mul(Lw, li)
        lam = new
    return lam


def eval_linearized(F, lam, x):
    acc = 0
    p = x
    for li in lam:
        acc ^= F.mul(li, p)
        p = F.mul(p, p)
    return acc


def monomials_upto(d):
    """Monomials (a, b) with a + b <= d in the BLOCK order: degree ascending,
    then exponent of x_1 descending."""
    out = []
    for e in range(d + 1):
        for a in range(e, -1, -1):
            out.append((a, e - a))
    return out


def column_monomials(D):
    """Descending degrevlex with x_1 > x_2; constant last."""
    out = []
    for e in range(D, -1, -1):
        for a in range(e, -1, -1):
            out.append((a, e - a))
    return out


class ShapeB:
    def __init__(self, F, l, D=66):
        self.F, self.l, self.D = F, l, D
        self.n = F.n
        self.cols = column_monomials(D)
        self.colidx = {m: i for i, m in enumerate(self.cols)}
        self.C = len(self.cols)
        self.const_col = self.C - 1
        assert self.cols[-1] == (0, 0)
        self.col_deg = np.array([a + b for a, b in self.cols], dtype=np.int64)
        self.mus0 = monomials_upto(D - 4)
        self.nus = monomials_upto(D - (1 << l)) if D >= (1 << l) else []
        self.n0 = len(self.mus0)
        self.n1 = len(self.nus)
        self.R = self.n0 + 2 * self.n1
        self.lam = linearized_LV(F, l)
        # block-0 column indices of the 5 terms of mu*g_0 (order c1..c5)
        idx0 = np.zeros((self.n0, 5), dtype=np.int64)
        for r, (a, b) in enumerate(self.mus0):
            idx0[r] = [self.colidx[(a + 2, b + 2)], self.colidx[(a + 2, b)], self.colidx[(a, b + 2)],
                       self.colidx[(a + 1, b + 1)], self.colidx[(a, b)]]
        self.idx0 = idx0
        idx1 = np.zeros((self.n1, l + 1), dtype=np.int64)
        idx2 = np.zeros((self.n1, l + 1), dtype=np.int64)
        for r, (a, b) in enumerate(self.nus):
            for i in range(l + 1):
                idx1[r, i] = self.colidx[(a + (1 << i), b)]
                idx2[r, i] = self.colidx[(a, b + (1 << i))]
        self.idx1, self.idx2 = idx1, idx2
        self.rows0 = np.arange(self.n0, dtype=np.int64)
        self.rows1 = self.n0 + np.arange(self.n1, dtype=np.int64)
        self.rows2 = self.n0 + self.n1 + np.arange(self.n1, dtype=np.int64)
        # the fixed (target-independent) part: blocks 1 and 2
        base = np.zeros((self.R, self.C), dtype=np.uint32)
        for i in range(l + 1):
            base[self.rows1, idx1[:, i]] = self.lam[i]
            base[self.rows2, idx2[:, i]] = self.lam[i]
        self.base = base
        a = np.array([m[0] for m in self.cols], dtype=np.int64)
        b = np.array([m[1] for m in self.cols], dtype=np.int64)
        self.col_a, self.col_b = a, b

    def row_order(self):
        out = []
        for r, (a, b) in enumerate(self.mus0):
            out.append({"row": r, "block": 0, "mult": [a, b]})
        for r, (a, b) in enumerate(self.nus):
            out.append({"row": self.n0 + r, "block": 1, "mult": [a, b]})
        for r, (a, b) in enumerate(self.nus):
            out.append({"row": self.n0 + self.n1 + r, "block": 2, "mult": [a, b]})
        return out

    def build(self, coeffs, reverse=False):
        M = self.base.copy()
        for k in range(5):
            M[self.rows0, self.idx0[:, k]] = coeffs[k]
        if reverse:
            M = M[::-1].copy()
        return M

    def eval_vector(self, x1, x2):
        """Evaluation of the column monomials at (x1, x2) in F_{2^n} (uint32)."""
        F = self.F
        pw1 = [1]
        pw2 = [1]
        for _ in range(self.D):
            pw1.append(F.mul(pw1[-1], x1))
            pw2.append(F.mul(pw2[-1], x2))
        p1 = np.array(pw1, dtype=np.int64)[self.col_a]
        p2 = np.array(pw2, dtype=np.int64)[self.col_b]
        return F.vmul(p1, p2)


# ---------------------------------------------------------------------------
class GFTabs:
    """Log/exp tables as int64 numpy arrays; exp has length 2(q-1) + 1."""

    def __init__(self, F):
        self.F = F
        self.q1 = F.q1
        self.log = F.np_log.astype(np.int64)
        exp = np.concatenate([F.np_exp, F.np_exp[:1]]).astype(np.int64)
        self.exp = exp

    def mulvec_scalar(self, vec, s):
        """vec (nonzero-or-zero entries) times scalar s."""
        if s == 0:
            return np.zeros_like(vec)
        z = vec == 0
        r = self.exp[self.log[vec] + self.log[s]]
        r[z] = 0
        return r


class ElimB:
    __slots__ = ("p", "c", "X", "rank", "pivcols", "Z", "h_rank", "h_set", "h_strict", "h_ops",
                 "ops_strict_B", "first_nonpivot_col", "classif", "pivot_vals")


def column_pass(M, T, refs=None, keep_ops=True, track=None):
    """THE REGIME-B SOLVER on M (uint32, modified in place).

    refs: optional list of (key, ref_p ndarray, ref_c ndarray). The first
    divergence of the target's T_strict from each reference is classified by
    the FIRST-MATCH RULE of AMD-20260924-3a9f06 ruling 1 (R0-R6), evaluated on
    the target's state S_k (after its first k steps; by Lemma 2B the same
    rational functions as the reference's state):
      R0 MATCH       : T_strict(t) = T_strict(r) (no entry is written)
      R1 PREFIX      : L_r = k < L_t (the reference's trace is a proper prefix)
      R2 EXTRA-PIVOT : L_r > k, L_t > k and c_k^t < c_k^r
      R3 COLUMN      : L_r > k and no unused row of S_k is nonzero at c_k^r;
                       prefix_flag = (L_t = k)
      R4 ZERO-PIVOT  : L_r > k and S_k[p_k^r, c_k^r] = 0
      R5 ROW-ORDER   : L_r > k, S_k[p_k^r, c_k^r] != 0 and a smaller-index
                       unused row is nonzero at c_k^r
      R6 UNCLASSIFIED: none of the above (a C-CLASS failure)
    track: optional (R, R2) matrix updated with the same row operations
    (for PS0' certificates)."""
    R, C = M.shape
    log, exp, q1 = T.log, T.exp, T.q1
    unused = np.ones(R, dtype=bool)
    ps, cs, Xs, pv = [], [], [], []
    first_np = None
    alive = {}
    classif = {}
    if refs:
        for key, rp, rc in refs:
            alive[key] = (rp, rc)
    k = 0
    for c in range(C):
        col = M[:, c]
        idx = np.flatnonzero(col)
        if idx.size:
            idx = idx[unused[idx]]
        if idx.size == 0:
            if first_np is None:
                first_np = c
            continue
        p = int(idx[0])
        if alive:
            for key in list(alive):
                rp, rc = alive[key]
                if k >= len(rp):
                    classif[key] = {"k": k, "type": "PREFIX", "rule": "R1", "prefix_flag": False,
                                    "p_ref": None, "c_ref": None, "p_t": p, "c_t": c, "div_col": c}
                    del alive[key]
                    continue
                if rp[k] == p and rc[k] == c:
                    continue
                classif[key] = _classify(M, unused, int(rp[k]), int(rc[k]), p, c, k)
                del alive[key]
        X = idx[1:]
        pval = int(M[p, c])
        if X.size:
            J = np.flatnonzero(M[p, c:])
            J += c
            lp = log[M[p, J]]
            lf = (log[M[X, c]] - log[pval]) % q1
            M[np.ix_(X, J)] ^= exp[lf[:, None] + lp[None, :]].astype(np.uint32)
            if track is not None:
                Jt = np.flatnonzero(track[p])
                if Jt.size:
                    lpt = log[track[p, Jt]]
                    track[np.ix_(X, Jt)] ^= exp[lf[:, None] + lpt[None, :]].astype(track.dtype)
        unused[p] = False
        ps.append(p)
        cs.append(c)
        pv.append(pval)
        if keep_ops:
            Xs.append(X)
        k += 1
    # end of the target's trace (L_t = k): every still-alive reference with a longer trace
    for key in list(alive):
        rp, rc = alive[key]
        if len(rp) > k:
            classif[key] = _classify(M, unused, int(rp[k]), int(rc[k]), None, None, k)
        # equal length and identical: MATCH (R0), no entry
    return ps, cs, Xs, pv, first_np, classif, unused


def _classify(M, unused, pr, cr, pt, ct, k):
    """R2-R6 at the target's state S_k (pt, ct = the target's step k, or None
    if the target's trace has ended: L_t = k)."""
    d = {"k": k, "p_ref": pr, "c_ref": cr, "p_t": pt, "c_t": ct}
    if ct is not None and ct < cr:
        d.update({"type": "EXTRA-PIVOT", "rule": "R2", "prefix_flag": False, "div_col": ct})
        return d
    colv = M[:, cr]
    nzu = np.flatnonzero(colv)
    nzu = nzu[unused[nzu]]
    entry = int(M[pr, cr])
    d["entry_at_ref_pivot"] = entry
    d["n_unused_nonzero_at_c_ref"] = int(nzu.size)
    d["div_col"] = cr
    if nzu.size == 0:
        d.update({"type": "COLUMN", "rule": "R3", "prefix_flag": ct is None})
    elif entry == 0:
        d.update({"type": "ZERO-PIVOT", "rule": "R4", "prefix_flag": False})
    elif int(nzu[0]) < pr:
        d.update({"type": "ROW-ORDER", "rule": "R5", "prefix_flag": False})
    else:
        d.update({"type": "UNCLASSIFIED", "rule": "R6", "prefix_flag": False})
    return d


def row_pass(M0, T, block=256):
    """SEPARATE row-sequential pass: Z = {i : row i in span(rows 0..i-1)} and the
    leading-column set of an echelon basis built in original row order.
    Blocked for speed: each block of consecutive rows is first reduced against
    the basis of all earlier rows (sweep over basis leads in column order), then
    processed row by row against the block's own new basis vectors. The result
    (Z, leading set) is unique, independent of the reduction schedule."""
    R, C = M0.shape
    log, exp, q1 = T.log, T.exp, T.q1
    basis = {}          # lead col -> (support cols ndarray, values ndarray)
    is_lead = np.zeros(C, dtype=bool)
    Z = []
    for s in range(0, R, block):
        V = M0[s:s + block].astype(np.int64)
        # sweep: every lead of the earlier rows, in increasing column order; a
        # basis vector is zero before its lead, so an update at lead c only
        # changes columns > c, which are visited later in this loop.
        if basis:
            for c in sorted(basis):
                rows = np.flatnonzero(V[:, c])
                if rows.size == 0:
                    continue
                J, vals = basis[c]
                lb = log[vals]
                lf = (log[V[rows, c]] - log[vals[0]]) % q1   # vals[0] is the lead entry (J[0] == c)
                V[np.ix_(rows, J)] ^= exp[lf[:, None] + lb[None, :]]
        # within the block, sequentially
        newleads = []
        for j in range(V.shape[0]):
            v = V[j]
            while True:
                nz = np.flatnonzero(v)
                if nz.size == 0:
                    break
                c = int(nz[0])
                if is_lead[c]:
                    # only a lead created inside this block can appear here
                    J, vals = basis[c]
                    f = (log[v[c]] - log[vals[0]]) % q1
                    v[J] ^= exp[f + log[vals]]
                    continue
                break
            nz = np.flatnonzero(v)
            if nz.size == 0:
                Z.append(s + j)
                continue
            c = int(nz[0])
            basis[c] = (nz.copy(), v[nz].copy())
            is_lead[c] = True
            newleads.append(c)
    leads = sorted(int(c) for c in basis)
    return Z, leads


def traces(ps, cs, Xs, Z, rank):
    ops_list = [[int(p), int(c), X.tolist()] for p, c, X in zip(ps, cs, Xs)]
    return {
        "h_rank": sha(canon(rank)),
        "h_set": sha(canon([sorted(int(c) for c in cs), sorted(int(z) for z in Z)])),
        "h_strict": sha(canon([[int(p), int(c)] for p, c in zip(ps, cs)])),
        "h_ops": sha(canon(ops_list)),
    }


def eliminate(M_orig, T, refs=None, with_row_pass=True, keep_ops=True):
    M = M_orig.copy()
    ps, cs, Xs, pv, first_np, classif, unused = column_pass(M, T, refs=refs, keep_ops=True)
    res = ElimB()
    res.p, res.c, res.X = ps, cs, Xs
    res.rank = len(ps)
    res.pivcols = sorted(cs)
    res.first_nonpivot_col = first_np
    res.classif = classif
    res.pivot_vals = pv
    C = M_orig.shape[1]
    res.ops_strict_B = int(sum(int(X.size) * (C - int(c)) for c, X in zip(cs, Xs)))
    cpass = None
    leads = None
    if with_row_pass:
        Z, leads = row_pass(M_orig, T)
        res.Z = Z
        cpass = (leads == res.pivcols) and (len(Z) == M_orig.shape[0] - res.rank)
    else:
        res.Z = sorted(set(range(M_orig.shape[0])) - set(ps))
    h = traces(ps, cs, Xs, res.Z, res.rank)
    res.h_rank, res.h_set, res.h_strict, res.h_ops = h["h_rank"], h["h_set"], h["h_strict"], h["h_ops"]
    return res, cpass, leads


def replay(M_orig, T, ref_p, ref_c, ref_X, stop_at_zero=True):
    """Fixed-schedule replay of a reference op log (p_k, c_k, X_k) on a target
    matrix, multipliers from the target's current entries (fixed control flow,
    target arithmetic). Returns dict: pivot entries e_k (list, up to the first
    zero), first_zero (k or None), first_invalid (first k at which some unused
    row outside X_k u {p_k} is nonzero at c_k, or None), survived (bool)."""
    M = M_orig.copy()
    R, C = M.shape
    log, exp, q1 = T.log, T.exp, T.q1
    unused = np.ones(R, dtype=bool)
    ek = []
    first_zero = None
    first_invalid = None
    K = len(ref_p)
    for k in range(K):
        p, c, X = int(ref_p[k]), int(ref_c[k]), ref_X[k]
        e = int(M[p, c])
        ek.append(e)
        if first_invalid is None:
            nz = np.flatnonzero(M[:, c])
            nz = nz[unused[nz]]
            outside = np.setdiff1d(nz, np.append(X, p))
            if outside.size:
                first_invalid = k
        if e == 0:
            first_zero = k
            if stop_at_zero:
                break
            unused[p] = False
            continue
        if X.size:
            J = np.flatnonzero(M[p, c:])
            J += c
            vx = M[X, c]
            nzx = vx != 0
            Xn = X[nzx]
            if Xn.size:
                lp = log[M[p, J]]
                lf = (log[M[Xn, c]] - log[e]) % q1
                M[np.ix_(Xn, J)] ^= exp[lf[:, None] + lp[None, :]].astype(np.uint32)
        unused[p] = False
    return {"e": ek, "first_zero": first_zero, "first_invalid": first_invalid,
            "survived": first_zero is None and len(ek) == K}


def guided(M_orig, T, ref_p, ref_c):
    """T_STRICT-GUIDED COMPUTATION (AMD-20260924-3a9f06 C-6): follow the
    reference's pivot sequence with full clearing. For k = 0..L_r-1: e_k = entry
    at (p_k^r, c_k^r); if 0, stop (the point breaks the pivot sequence at k);
    otherwise clear EVERY unused row i != p_k^r that is nonzero at c_k^r, then
    mark p_k^r used. Returns dict(e: pivot entries, broke_at: k or None,
    cleared: list of the cleared-row arrays per completed step)."""
    M = M_orig.copy()
    R, C = M.shape
    log, exp, q1 = T.log, T.exp, T.q1
    unused = np.ones(R, dtype=bool)
    e = []
    cleared = []
    broke = None
    for k in range(len(ref_p)):
        p, c = int(ref_p[k]), int(ref_c[k])
        ek = int(M[p, c])
        if ek == 0:
            broke = k
            break
        e.append(ek)
        nz = np.flatnonzero(M[:, c])
        nz = nz[unused[nz]]
        X = nz[nz != p]
        if X.size:
            J = np.flatnonzero(M[p, c:])
            J += c
            lp = log[M[p, J]]
            lf = (log[M[X, c]] - log[ek]) % q1
            M[np.ix_(X, J)] ^= exp[lf[:, None] + lp[None, :]].astype(np.uint32)
        cleared.append(X)
        unused[p] = False
    return {"e": e, "broke_at": broke, "cleared": cleared}
