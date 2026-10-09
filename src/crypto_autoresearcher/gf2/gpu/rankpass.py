"""Column pass for the rank-profile solver with the matrix on a GPU.

Same pivots (ps, cs, in the same order) and the same final matrix as
``kernels.column_pass(M, C, keep_ops=False, algorithm="blocked")``; no op log.

The pass works one 64-column word block at a time, as the blocked CPU pass
does. Per block only the active rows' word w (one uint64 per row) goes to
the host, where ``gf2_block_elim`` picks the pivots and records, per active
row, the set of the block's pivots it absorbed (``coef``). The trailing
update -- ~88% of the CPU pass -- runs on the device: the pivots' pre-block
tails are combined into 8-bit Gray-code tables and every active row with a
nonzero ``coef`` takes one table row per byte of it, which is the CPU
kernel's update (``_kernels.c tail_chunk``) and so gives the same bits.

``xp`` is the array module: ``cupy`` on a GPU, ``numpy`` to run the very same
code on the CPU (the tests do that, so the algorithm is checked without a
device).
"""
from __future__ import annotations

import numpy as np

from .. import _native

XP = None   # array module override (tests set numpy to run this path without a device)


def block_elim(val, nbits):
    """(val, coef, piv_a, piv_b) after one 64-column step on the active rows'
    words ``val`` (see _kernels.c gf2_block_elim)."""
    val = np.ascontiguousarray(val, dtype=np.uint64).copy()
    na = len(val)
    coef = np.zeros(na, dtype=np.uint64)
    piv_a = np.zeros(64, dtype=np.int32)
    piv_b = np.zeros(64, dtype=np.int32)
    lib = _native.load()
    if lib is None:
        return _block_elim_py(val, nbits)
    n = lib.gf2_block_elim(val.ctypes.data, na, int(nbits), coef.ctypes.data,
                           piv_a.ctypes.data, piv_b.ctypes.data)
    if n < 0:
        raise MemoryError("gf2_block_elim failed")
    return val, coef, piv_a[:n].astype(np.int64), piv_b[:n].astype(np.int64)


def _block_elim_py(val, nbits):
    na = len(val)
    v = [int(x) for x in val]
    cf = [0] * na
    used = [False] * na
    pa, pb = [], []
    for b in range(nbits):
        cand = [a for a in range(na) if not used[a] and v[a] and (v[a] & -v[a]).bit_length() - 1 == b]
        if not cand:
            continue
        p = cand[0]
        slot = len(pa)
        pa.append(p)
        pb.append(b)
        used[p] = True
        pv, pc = v[p], cf[p] ^ (1 << slot)
        for x in cand[1:]:
            v[x] ^= pv
            cf[x] ^= pc
    return (np.array(v, dtype=np.uint64), np.array(cf, dtype=np.uint64),
            np.array(pa, dtype=np.int64), np.array(pb, dtype=np.int64))


def _lead_words(xp, Md):
    nz = Md != 0
    has = nz.any(axis=1)
    return xp.where(has, nz.argmax(axis=1), -1).astype(xp.int64)


def column_pass(M, C, xp=None):
    """Eliminate M (R x W uint64, host array, modified in place) column by
    column. Returns (ps, cs) as int64 arrays: pivot rows and pivot columns in
    pivot order."""
    if xp is None:
        xp = XP
    if xp is None:
        import cupy as xp  # noqa: N813
    R, W = M.shape
    on_host = xp is np
    Md = M if on_host else xp.asarray(M)
    lw = _lead_words(xp, Md)
    ps, cs = [], []
    u8 = np.uint64(0xFF)
    for w in range(W):
        act = xp.flatnonzero(lw == w)
        na = int(act.size)
        if not na:
            continue
        act_h = act if on_host else act.get()
        val_h = Md[act, w]
        val_h = val_h if on_host else val_h.get()
        val_h, coef, piv_a, piv_b = block_elim(val_h, min(64, C - 64 * w))
        npiv = len(piv_a)
        ps.append(act_h[piv_a])
        cs.append(64 * w + piv_b)
        tail = W - w - 1
        sel = np.flatnonzero(coef)
        if tail > 0 and npiv and len(sel):
            Bs = Md[act[xp.asarray(piv_a)], w + 1:]          # pivots' pre-block tails
            rows = act[xp.asarray(sel)]
            cf = xp.asarray(coef[sel])
            upd = None
            for g in range((npiv + 7) // 8):
                k = min(8, npiv - 8 * g)
                T = xp.zeros((1 << k, tail), dtype=xp.uint64)
                for lb in range(k):                     # Gray-code doubling
                    T[1 << lb:2 << lb] = T[:1 << lb] ^ Bs[8 * g + lb]
                part = T[((cf >> np.uint64(8 * g)) & u8).astype(xp.int64)]
                upd = part if upd is None else upd ^ part
            Md[rows, w + 1:] = Md[rows, w + 1:] ^ upd
        Md[act, w] = val_h if on_host else xp.asarray(val_h)
        isp = np.zeros(na, dtype=bool)
        isp[piv_a] = True
        lw[act[xp.asarray(np.flatnonzero(isp))]] = -1
        nonp = act[xp.asarray(np.flatnonzero(~isp))]
        if int(nonp.size):
            if tail:
                sub = Md[nonp, w + 1:] != 0
                lw[nonp] = xp.where(sub.any(axis=1), w + 1 + sub.argmax(axis=1), -1)
            else:
                lw[nonp] = -1
    if not on_host:
        M[...] = Md.get()
    ps = np.concatenate(ps).astype(np.int64) if ps else np.zeros(0, np.int64)
    cs = np.concatenate(cs).astype(np.int64) if cs else np.zeros(0, np.int64)
    return ps, cs
