"""Bit-packed dense linear algebra over F_2 with numpy only.

A matrix with ncols columns is stored as an (R, W) uint64 array; column c is
bit (c & 63) of word (c >> 6). All eliminations here are plain Gauss-Jordan:
columns are processed in increasing index; the pivot for a column is the
UNUSED row of smallest current index with a 1 in that column; rows never move.
Ranks, subspace dimensions and membership do not depend on this rule (BR-1).
"""
import numpy as np

U64 = np.uint64
ONE = np.uint64(1)


def nwords(ncols):
    return (ncols + 63) >> 6


def pack(dense):
    """dense: (R, C) uint8/bool 0-1 -> (R, W) uint64."""
    dense = np.ascontiguousarray(dense, dtype=np.uint8)
    R, C = dense.shape
    W = nwords(C)
    pad = W * 64 - C
    if pad:
        dense = np.concatenate([dense, np.zeros((R, pad), dtype=np.uint8)], axis=1)
    b = np.packbits(dense, axis=1, bitorder="little")          # (R, W*8) uint8
    return np.ascontiguousarray(b).view(np.uint64).reshape(R, W).copy()


def unpack(A, ncols):
    A = np.ascontiguousarray(A, dtype=np.uint64)
    R = A.shape[0]
    b = A.view(np.uint8).reshape(R, -1)
    d = np.unpackbits(b, axis=1, bitorder="little")
    return d[:, :ncols]


def getbit(A, c):
    return ((A[..., c >> 6] >> U64(c & 63)) & ONE).astype(bool)


def bits_at(y, cols):
    """Bits of the packed vector y at the given columns (bool array)."""
    cols = np.asarray(cols, dtype=np.int64)
    if cols.size == 0:
        return np.zeros(0, dtype=bool)
    return ((y[cols >> 6] >> (cols & 63).astype(np.uint64)) & ONE).astype(bool)


def rref(A, ncols, full=True, compact_every=128):
    """Gauss-Jordan (full=True) or forward elimination (full=False) on the
    first ncols columns of A (extra words beyond are carried along, e.g. for
    tracking). Returns (rows, pivot_cols, pivot_orig_idx):
      rows            the pivot rows after elimination, in pivot-column order;
      pivot_cols      list of pivot columns (increasing);
      pivot_orig_idx  the ORIGINAL row index chosen as pivot for each column.
    The original rows at pivot_orig_idx form a basis of the row space.
    With full=True the returned rows are the reduced row echelon form."""
    A = np.array(A, dtype=np.uint64, copy=True)
    R, W = A.shape
    orig = np.arange(R)
    used = np.zeros(R, dtype=bool)
    piv_cols = []
    piv_orig = []
    piv_local = []           # indices into current A (tracked through compaction)
    steps_since = 0
    for c in range(ncols):
        if A.shape[0] == 0:
            break
        w = c >> 6
        col = ((A[:, w] >> U64(c & 63)) & ONE).astype(bool)
        cand = np.flatnonzero(col & ~used)
        if cand.size == 0:
            continue
        p = cand[0]
        used[p] = True
        if full:
            col[p] = False
            others = np.flatnonzero(col)
        else:
            others = cand[1:]
        if others.size:
            A[others, w:] ^= A[p, w:]
        piv_cols.append(c)
        piv_orig.append(int(orig[p]))
        piv_local.append(p)
        steps_since += 1
        if compact_every and steps_since >= compact_every:
            steps_since = 0
            # drop unused all-zero rows (they can never become pivots again)
            zero = ~A.any(axis=1)
            drop = zero & ~used
            if drop.any():
                keep = ~drop
                newidx = np.cumsum(keep) - 1
                piv_local = [int(newidx[q]) for q in piv_local]
                A = A[keep]
                orig = orig[keep]
                used = used[keep]
    rows = A[piv_local] if piv_local else np.zeros((0, W), dtype=np.uint64)
    return rows, piv_cols, piv_orig


def reduce_by_rref(P, Rrows, piv_cols):
    """P <- P + (bits of P at the pivot columns) * Rrows, for Rrows in RREF.
    Uses 8-row lookup tables (the method of four Russians). Returns a new
    array; afterwards P has zeros in every pivot column."""
    P = np.array(P, dtype=np.uint64, copy=True)
    if P.shape[0] == 0 or len(piv_cols) == 0:
        return P
    W = P.shape[1]
    r = len(piv_cols)
    for g in range(0, r, 8):
        grp = Rrows[g:g + 8]
        cols = piv_cols[g:g + 8]
        L = len(cols)
        T = np.zeros((1 << L, W), dtype=np.uint64)
        for i in range(L):
            T[1 << i: 2 << i] = T[0: 1 << i] ^ grp[i]
        idx = np.zeros(P.shape[0], dtype=np.int64)
        for i, c in enumerate(cols):
            idx |= (((P[:, c >> 6] >> U64(c & 63)) & ONE).astype(np.int64) << i)
        nz = np.flatnonzero(idx)
        if nz.size:
            P[nz] ^= T[idx[nz]]
    return P


def reduce_vec(y, Rrows, piv_cols):
    return reduce_by_rref(y.reshape(1, -1), Rrows, piv_cols)[0]


def is_zero(v):
    return not np.any(v)
