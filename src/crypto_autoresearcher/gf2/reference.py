"""Numpy reference implementations of the GF(2) kernels.

These are the definitions the native kernels in ``_kernels.c`` must reproduce
output for output. Each function is copied from an archived CERTBIN engine
(bodies unchanged apart from dtype normalisation of the returned op log):

* ``column_pass``   -- experiments/EXP-CERTBIN-e94b27/impl/closure.py ``echelon``
                       (= EXP-CERTBIN-4e92d7/impl/elim.py ``column_pass``)
* ``row_pass``      -- experiments/EXP-CERTBIN-4e92d7/impl/elim.py ``row_pass``
* ``replay_planes`` -- experiments/EXP-CERTBIN-4e92d7/impl/elim.py
* ``replay_direct`` -- experiments/EXP-CERTBIN-4e92d7/impl/elim.py
* ``backtrace``     -- experiments/EXP-CERTBIN-e94b27/impl/closure.py
* ``products``      -- experiments/EXP-CERTBIN-e94b27/impl/closure.py
                       ``Closure.products``

The archived files are immutable run records; this module is a copy, so the
engines here can evolve without touching what a past run executed.
"""
from __future__ import annotations

import numpy as np

ONE = np.uint64(1)


def column_pass(M, C, keep_ops=True):
    """Column-major forward elimination on packed M (modified in place).

    Returns (ps int32, cs int32, Xs list of int32 arrays or None, ops_strict).
    """
    R, W = M.shape
    unused = np.ones(R, dtype=bool)
    ps, cs, Xs = [], [], []
    total = 0
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
        total += int(X.size)
        unused[p] = False
        ps.append(p)
        cs.append(c)
        if keep_ops:
            Xs.append(X.astype(np.int32))
    return (np.array(ps, dtype=np.int32), np.array(cs, dtype=np.int32),
            Xs if keep_ops else None, total)


def row_pass(M0, C):
    """Rows in original order; Z = rows in the span of earlier rows.

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


def replay_planes(planes, ps, cs, Xs):
    P = planes.shape[0]
    K = len(ps)
    e = np.zeros((P, K), dtype=np.uint8)
    for k in range(K):
        p, c, X = int(ps[k]), int(cs[k]), Xs[k]
        w = c >> 6
        e[:, k] = ((planes[:, p, w] >> np.uint64(c & 63)) & ONE).astype(np.uint8)
        if X.size:
            planes[:, X, w:] ^= planes[:, p, w:][:, None, :]
    return e


def replay_direct(M_orig, ps, cs, Xs, stop_at_zero=False):
    M = M_orig.copy()
    K = len(ps)
    e = np.full(K, 255, dtype=np.uint8)
    for k in range(K):
        p, c, X = int(ps[k]), int(cs[k]), Xs[k]
        w = c >> 6
        ek = int((M[p, w] >> np.uint64(c & 63)) & ONE)
        e[k] = ek
        if stop_at_zero and ek == 0:
            break
        if X.size:
            M[X, w:] ^= M[p, w:]
    return e


def backtrace(ps, Xs, S):
    for k in range(len(ps) - 1, -1, -1):
        X = Xs[k]
        if X.size:
            par = np.bitwise_xor.reduce(S[X], axis=0)
            if par.any():
                S[ps[k]] ^= par
    return S


def products(rows, maps, nv, C, W):
    """maps[j] = (A, tA, Bc) as built by the archived Closure.__init__."""

    def pack(dense):
        n = dense.shape[0]
        pad = W * 64 - C
        if pad:
            dense = np.concatenate([dense, np.zeros((n, pad), dtype=np.uint8)], axis=1)
        b = np.packbits(dense, axis=1, bitorder="little")
        return np.ascontiguousarray(b).view(np.uint64).reshape(n, W).copy()

    def unpack(M):
        b = M.view(np.uint8).reshape(M.shape[0], W * 8)
        return np.unpackbits(b, axis=1, bitorder="little")[:, :C]

    n = rows.shape[0]
    out = np.zeros((nv * n, W), dtype=np.uint64)
    if n == 0:
        return out
    chunk = 2048
    for s in range(0, n, chunk):
        d = unpack(rows[s:s + chunk])
        m = d.shape[0]
        for j in range(nv):
            A, tA, Bc = maps[j]
            o = np.zeros_like(d)
            o[:, tA] = d[:, A]
            o[:, Bc] ^= d[:, Bc]
            out[j * n + s:j * n + s + m] = pack(o)
    return out
