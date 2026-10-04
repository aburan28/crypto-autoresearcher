"""The declared deterministic GF(2) elimination (the SOLVER), the separate
row-sequential pass for Z_D, trace encodings and fixed-schedule replays.

Matrices are bit-packed: uint64 array (R, W); column c is bit (c & 63) of word
(c >> 6). Columns are already laid out in the declared column order.
"""
import hashlib
import json

import numpy as np

ONE = np.uint64(1)


def canon(obj):
    return json.dumps(obj, separators=(",", ":"))


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


class ElimResult:
    __slots__ = ("p", "c", "X", "rank", "pivcols", "Z", "h_rank", "h_set",
                 "h_strict", "h_ops", "ops_strict")


def column_pass(M, C, keep_ops=True):
    """Forward elimination, column-major. For each column c in order: among
    rows not yet used as pivot rows, pick the smallest ORIGINAL row index with a
    1 in column c; record (p, c) and XOR row p into every other unused row with
    a 1 in column c (set X). Rows never move.

    Returns (p_list, c_list, X_list). M is modified in place.
    Invariant used for speed (proved in impl/README.md): after columns < c are
    processed, every unused row is zero in all columns < c, so the XOR can start
    at word c >> 6. The pivot row p is also unused, hence equally zero there.
    """
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
        Xs.append(X if keep_ops else None)
    return ps, cs, Xs


def row_pass(M0, C):
    """SEPARATE row-sequential pass: incremental echelon basis (kept fully
    reduced) in original row order. Z = rows lying in the span of earlier rows.
    Returns (Z list, sorted leading-column list)."""
    R, W = M0.shape
    basis = np.zeros((R, W), dtype=np.uint64)
    lw = np.zeros(R, dtype=np.int64)
    lb = np.zeros(R, dtype=np.uint64)
    leads = []
    nb = 0
    Z = []
    for i in range(R):
        v = M0[i].copy()
        if not v.any():
            Z.append(i)
            continue
        if nb:
            hit = ((v[lw[:nb]] >> lb[:nb]) & ONE).astype(bool)
            if hit.any():
                v ^= np.bitwise_xor.reduce(basis[:nb][hit], axis=0)
        nzw = np.flatnonzero(v)
        if nzw.size == 0:
            Z.append(i)
            continue
        w = int(nzw[0])
        word = int(v[w])
        bit = (word & -word).bit_length() - 1
        lc = w * 64 + bit
        # keep the basis fully reduced: clear column lc from existing vectors
        if nb:
            has = np.flatnonzero((basis[:nb, w] >> np.uint64(bit)) & ONE)
            if has.size:
                basis[has] ^= v
        basis[nb] = v
        lw[nb] = w
        lb[nb] = bit
        leads.append(lc)
        nb += 1
    return Z, sorted(leads)


def eliminate(M_orig, C, keep_ops=True, with_row_pass=True):
    """Full instrument for one matrix: column pass + traces (+ row pass)."""
    M = M_orig.copy()
    ps, cs, Xs = column_pass(M, C, keep_ops=True)
    res = ElimResult()
    res.p = ps
    res.c = cs
    res.rank = len(ps)
    res.pivcols = sorted(cs)
    ops_list = [[p, c, X.tolist()] for p, c, X in zip(ps, cs, Xs)]
    res.ops_strict = int(sum(len(o[2]) for o in ops_list))
    res.h_ops = sha(canon(ops_list))
    res.X = Xs if keep_ops else None
    res.h_rank = sha(canon(res.rank))
    res.h_strict = sha(canon([[p, c] for p, c in zip(ps, cs)]))
    if with_row_pass:
        Z, leads = row_pass(M_orig, C)
        res.Z = Z
        res.h_set = sha(canon([res.pivcols, Z]))
        cpass = (leads == res.pivcols) and (len(Z) == M_orig.shape[0] - res.rank)
        return res, cpass, leads
    return res, None, None


def ops_json_list(res):
    return [[p, c, X.tolist()] for p, c, X in zip(res.p, res.c, res.X)]


# ---------------------------------------------------------------------------
# Fixed-schedule replays
# ---------------------------------------------------------------------------
def replay_planes(planes, ps, cs, Xs):
    """Apply the op log to a stack of matrices (P, R, W) simultaneously and
    return e (P, K) uint8: entry (p_k, c_k) of each plane immediately BEFORE
    step k's XORs. Columns < c_k are never read again, so XORs start at word
    c_k >> 6 (reads at later steps are at columns > c_k)."""
    P = planes.shape[0]
    K = len(ps)
    e = np.zeros((P, K), dtype=np.uint8)
    for k in range(K):
        p, c, X = ps[k], cs[k], Xs[k]
        w = c >> 6
        e[:, k] = ((planes[:, p, w] >> np.uint64(c & 63)) & ONE).astype(np.uint8)
        if X.size:
            planes[:, X, w:] ^= planes[:, p, w:][:, None, :]
    return e


def affine_forms(planes_E0_Ej, ps, cs, Xs):
    """planes: (18, R, W) = [M(E^0), M(E^0'), ..., M(E^16)] -> (a0 uint8 (K,),
    a int64 (K,) 17-bit linear parts) with e_k(r) = a0_k + <a_k, r>."""
    e = replay_planes(planes_E0_Ej.copy(), ps, cs, Xs)
    a0 = e[0].astype(np.uint8)
    a = np.zeros(e.shape[1], dtype=np.int64)
    for j in range(1, e.shape[0]):
        a |= e[j].astype(np.int64) << (j - 1)
    return a0, a


def eval_forms(a0, a, rs):
    """e (T, K) for targets with r values rs (T,)."""
    rs = np.asarray(rs, dtype=np.int64)
    par = (np.bitwise_count(rs[:, None] & a[None, :]) & 1).astype(np.uint8)
    return par ^ a0[None, :]


def replay_direct(M_orig, ps, cs, Xs, stop_at_zero=False):
    """Direct fixed-schedule replay on one matrix. Returns e (K,) uint8 (up to
    and including the first zero if stop_at_zero; later entries = 255)."""
    M = M_orig.copy()
    K = len(ps)
    e = np.full(K, 255, dtype=np.uint8)
    for k in range(K):
        p, c, X = ps[k], cs[k], Xs[k]
        w = c >> 6
        ek = int((M[p, w] >> np.uint64(c & 63)) & ONE)
        e[k] = ek
        if stop_at_zero and ek == 0:
            break
        if X.size:
            M[X, w:] ^= M[p, w:]
    return e


def gf2_rank_rows(rows_packed):
    """Rank of a small packed matrix (independent simple elimination)."""
    A = rows_packed.copy()
    n, W = A.shape
    rank = 0
    for w in range(W):
        for b in range(64):
            if rank >= n:
                return rank
            bit = np.uint64(b)
            col = ((A[rank:, w] >> bit) & ONE).astype(bool)
            idx = np.flatnonzero(col)
            if idx.size == 0:
                continue
            piv = rank + int(idx[0])
            if piv != rank:
                A[[rank, piv]] = A[[piv, rank]]
            others = np.flatnonzero(((A[:, w] >> bit) & ONE).astype(bool))
            others = others[others != rank]
            if others.size:
                A[others] ^= A[rank]
            rank += 1
    return rank


def int_rank(vals):
    """F_2-rank of a list of Python ints (bit vectors)."""
    basis = {}
    for v in vals:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return len(basis)
