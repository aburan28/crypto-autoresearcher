"""Public GF(2) kernels: native when available, numpy reference otherwise.

Both backends return identical results (tests/test_gf2_kernels.py). The op
log is an ``OpLog``: flat int32/int64 arrays instead of a list of per-step
arrays, so it crosses the C boundary without copies; ``OpLog.Xs`` gives the
list-of-arrays view the archived engines use.

Native calls release the GIL, so independent matrices can be processed on a
thread pool (``map_threads``).
"""
from __future__ import annotations

import ctypes
import hashlib
import json
import os
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from . import _native, reference


def backend() -> str:
    return "native" if _native.load() is not None else "reference"


def _ptr(a):
    return a.ctypes.data


# Calls touching fewer words than this keep the GIL (see _native.load_holding_gil).
GIL_RELEASE_WORDS = 1 << 15
# matrices below this many words run one elimination on one thread by
# default (measured crossover on 4 cores: threads start to pay near 1e7 words)
INNER_MIN_WORDS = 1 << 23
# words per super-block step of the "sb" column pass (1..8); speed only
SB_WORDS = int(os.environ.get("CRYPTO_AR_GF2_SB_WORDS", "2"))


def _lib_for(words):
    return _native.load() if words >= GIL_RELEASE_WORDS else _native.load_holding_gil()


def _need(a, dtype, name):
    if a.dtype != dtype or not a.flags.c_contiguous:
        raise ValueError(f"{name} must be a C-contiguous {np.dtype(dtype).name} array")


class XView:
    """Read-only sequence view of the X sets: ``view[k]`` is an int32 slice of
    the flat array (no per-step array objects are built up front)."""

    __slots__ = ("xoff", "xs")

    def __init__(self, xoff, xs):
        self.xoff, self.xs = xoff, xs

    def __len__(self):
        return int(self.xoff.size) - 1

    def __getitem__(self, k):
        if isinstance(k, slice):
            return [self[i] for i in range(*k.indices(len(self)))]
        n = len(self)
        if k < 0:
            k += n
        if not 0 <= k < n:
            raise IndexError(k)
        return self.xs[int(self.xoff[k]):int(self.xoff[k + 1])]

    def __iter__(self):
        xs, off = self.xs, self.xoff.tolist()
        for k in range(len(off) - 1):
            yield xs[off[k]:off[k + 1]]


class OpLog:
    """Elimination op log: step k chose pivot row ps[k] at column cs[k] and
    XORed it into rows xs[xoff[k]:xoff[k+1]] (ascending)."""

    __slots__ = ("ps", "cs", "xoff", "xs", "ops_strict")

    def __init__(self, ps, cs, xoff, xs, ops_strict):
        self.ps, self.cs, self.xoff, self.xs = ps, cs, xoff, xs
        self.ops_strict = int(ops_strict)

    @property
    def K(self) -> int:
        return int(self.ps.size)

    @property
    def has_X(self) -> bool:
        return self.xoff is not None

    @property
    def Xs(self):
        if self.xoff is None:
            return None
        return XView(self.xoff, self.xs)

    @classmethod
    def from_lists(cls, ps, cs, Xs, ops_strict=None):
        ps = np.ascontiguousarray(ps, dtype=np.int32)
        cs = np.ascontiguousarray(cs, dtype=np.int32)
        if Xs is None:
            return cls(ps, cs, None, None, ops_strict or 0)
        sizes = np.array([len(x) for x in Xs], dtype=np.int64)
        xoff = np.zeros(len(Xs) + 1, dtype=np.int64)
        np.cumsum(sizes, out=xoff[1:])
        xs = (np.concatenate([np.asarray(x, dtype=np.int32) for x in Xs])
              if len(Xs) and xoff[-1] else np.zeros(0, dtype=np.int32))
        return cls(ps, cs, xoff, xs, int(xoff[-1]) if ops_strict is None else ops_strict)


# ---------------------------------------------------------------------------
# column pass
# ---------------------------------------------------------------------------
def column_pass(M, C, keep_ops=True, algorithm="auto", threads=None) -> OpLog:
    """The declared column-major solver on packed M (modified in place).

    algorithm: "sb" (super-blocked: SB_WORDS words per step, Gray-code tables,
    threaded trailing update), "blocked" (one word per step), "direct"
    (per-column buckets) or "auto" (the default: "sb" with more than one
    thread, else "blocked", the faster of the two single-threaded). Every
    native form returns the reference's op log and final matrix; they are
    cross-checked in tests.

    threads: threads for the trailing update inside this one matrix (default:
    ``inner_threads()`` for matrices of at least INNER_MIN_WORDS words, else
    1). Any value gives identical output."""
    _need(M, np.uint64, "M")
    R, W = M.shape
    lib = _native.load()
    if lib is None:
        ps, cs, Xs, total = reference.column_pass(M, C, keep_ops)
        return OpLog.from_lists(ps, cs, Xs, total)
    tot = ctypes.c_int64(0)
    lib = _lib_for(R * W)
    if threads is None:
        nt = inner_threads() if R * W >= INNER_MIN_WORDS else 1
    else:
        nt = max(1, int(threads))
    if algorithm == "auto":
        algorithm = "sb" if nt > 1 else "blocked"
    if algorithm == "blocked":
        h = lib.gf2_column_pass_blocked_mt(_ptr(M), R, W, C, 1 if keep_ops else 0,
                                           ctypes.byref(tot), nt)
    elif algorithm == "sb":
        h = lib.gf2_column_pass_sb(_ptr(M), R, W, C, 1 if keep_ops else 0,
                                   ctypes.byref(tot), nt, SB_WORDS)
    elif algorithm == "direct":
        h = lib.gf2_column_pass(_ptr(M), R, W, C, 1 if keep_ops else 0, ctypes.byref(tot))
    else:
        raise ValueError(f"unknown algorithm {algorithm!r}")
    if not h:
        raise MemoryError("gf2_column_pass: allocation failed")
    K = lib.gf2_log_K(h)
    nx = lib.gf2_log_nx(h)
    ps = np.empty(K, dtype=np.int32)
    cs = np.empty(K, dtype=np.int32)
    xoff = np.empty(K + 1, dtype=np.int64)
    lib.gf2_log_copy_meta(h, _ptr(ps), _ptr(cs), _ptr(xoff))
    if not keep_ops or nx == 0:
        lib.gf2_log_free(h)
        xs = np.zeros(0, dtype=np.int32)
    else:
        # The X list is often hundreds of MB: view the C buffer in place and
        # free it with the view instead of copying it (a copy cost more than
        # half the elimination at nv = 24, D = 5).
        buf = (ctypes.c_int32 * nx).from_address(lib.gf2_log_xs(h))
        weakref.finalize(buf, _native.load().gf2_log_free, h)
        xs = np.frombuffer(buf, dtype=np.int32)
    if not keep_ops:
        return OpLog(ps, cs, None, None, tot.value)
    return OpLog(ps, cs, xoff, xs, tot.value)


# ---------------------------------------------------------------------------
# row pass
# ---------------------------------------------------------------------------
def row_pass(M0, C):
    """(Z list, sorted leading-column list); M0 is not modified."""
    _need(M0, np.uint64, "M0")
    lib = _native.load()
    if lib is None:
        return reference.row_pass(M0, C)
    R, W = M0.shape
    Z = np.empty(max(R, 1), dtype=np.int32)
    leads = np.empty(max(min(R, C), 1), dtype=np.int32)
    nl = ctypes.c_int64(0)
    lib = _lib_for(R * W)
    nz = lib.gf2_row_pass(_ptr(M0), R, W, C, _ptr(Z), _ptr(leads), ctypes.byref(nl))
    if nz < 0:
        raise MemoryError("gf2_row_pass: allocation failed")
    return Z[:nz].tolist(), leads[:nl.value].tolist()


def pack_eqs(eqs):
    """Equations (lists of monomial masks) -> (eoff int64[neq+1], emon uint64[])."""
    lens = np.array([len(f) for f in eqs], dtype=np.int64)
    eoff = np.zeros(len(eqs) + 1, dtype=np.int64)
    np.cumsum(lens, out=eoff[1:])
    emon = np.array([int(m) for f in eqs for m in f], dtype=np.uint64)
    return eoff, emon


def build_rows(eoff, emon, nv, D, mu, k, W=None, threads=None):
    """Macaulay rows mu[i] * f_{k[i]} in Closure(nv, D, .) column order.

    Returns (M or None, lead, weight): with W given, M is the (n x W) packed
    matrix (equal to the matching rows of Closure.build_M); lead is each row's
    lowest column (-1 for a zero row), weight its number of monomials."""
    mu = np.ascontiguousarray(mu, dtype=np.uint64)
    k = np.ascontiguousarray(k, dtype=np.int32)
    n = len(mu)
    lead = np.empty(n, dtype=np.int64)
    weight = np.empty(n, dtype=np.int64)
    M = np.zeros((n, W), dtype=np.uint64) if W is not None else None
    lib = _native.load()
    if lib is None:
        return reference.build_rows(eoff, emon, nv, D, mu, k, M, lead, weight)
    nt = inner_threads() if threads is None else max(1, int(threads))
    rc = _lib_for(n * 64).gf2_build_rows(_ptr(eoff), _ptr(emon) if len(emon) else None, nv, D, n,
                                         _ptr(mu), _ptr(k), W or 0,
                                         _ptr(M) if M is not None else None,
                                         _ptr(lead), _ptr(weight), nt)
    if rc != 0:
        raise MemoryError("gf2_build_rows failed")
    return M, lead, weight


def row_lead_weight(M):
    """(lead, weight) int64 arrays: lowest set column of each row (-1 for a zero
    row) and its popcount."""
    _need(M, np.uint64, "M")
    R, W = M.shape
    lib = _native.load()
    if lib is None:
        nz = M != 0
        has = nz.any(axis=1)
        fw = np.argmax(nz, axis=1)
        word = M[np.arange(R), fw]
        low = word & (~word + np.uint64(1))
        bit = np.zeros(R, dtype=np.int64)
        bit[has] = np.log2(low[has].astype(np.float64)).astype(np.int64)
        lead = np.where(has, fw.astype(np.int64) * 64 + bit, -1)
        weight = np.unpackbits(M.view(np.uint8), axis=1).sum(axis=1).astype(np.int64)
        return lead, weight
    lead = np.empty(R, dtype=np.int64)
    weight = np.empty(R, dtype=np.int64)
    _lib_for(R * W).gf2_row_lead_weight(_ptr(M), R, W, _ptr(lead), _ptr(weight))
    return lead, weight


def row_leads(M0, C):
    """Per-row leads in row order: int32 array, out[i] = the leading column row
    i adds to the span of rows 0..i-1, or -1 if it adds none. M0 is not
    modified."""
    _need(M0, np.uint64, "M0")
    lib = _native.load()
    if lib is None:
        return reference.row_leads(M0, C)
    R, W = M0.shape
    out = np.empty(R, dtype=np.int32)
    lib = _lib_for(R * W)
    if lib.gf2_row_leads(_ptr(M0), R, W, C, _ptr(out)) < 0:
        raise MemoryError("gf2_row_leads: allocation failed")
    return out


def _row_addrs(blocks):
    """blocks: [(M, rows, ...)] -> uint64 addresses of those rows."""
    out = []
    for blk in blocks:
        M, rows = blk[0], np.asarray(blk[1], dtype=np.int64)
        _need(M, np.uint64, "M")
        out.append(np.uint64(M.ctypes.data) + rows.astype(np.uint64) * np.uint64(M.shape[1] * 8))
    return np.concatenate(out) if out else np.zeros(0, np.uint64)


def annihilator(blocks, C):
    """Basis of U^perp as the columns of K (C x fw uint64 words; f = C - r
    columns, fw = ceil(f/64)), U = the span of an echelon row set given as
    blocks [(M, rows, leads), ...]: row rows[t] of M has lead leads[t], and
    all leads are distinct. Free column t (t-th non-lead column, ascending)
    has K[free_t] = e_t; see _kernels.c gf2_annihilator. No row is copied."""
    lead = np.concatenate([np.asarray(b[2], dtype=np.int64) for b in blocks]) if blocks else np.zeros(0, np.int64)
    r = len(lead)
    W = blocks[0][0].shape[1] if blocks else (C + 63) // 64
    f = C - r
    fw = max(1, (f + 63) // 64)
    order = np.argsort(-lead, kind="stable")
    ls = np.ascontiguousarray(lead[order])
    K = np.zeros((C, fw), dtype=np.uint64)
    lib = _native.load()
    if lib is None:
        E = (np.concatenate([b[0][np.asarray(b[1], dtype=np.int64)] for b in blocks]) if blocks
             else np.zeros((0, W), np.uint64))
        return reference.annihilator(np.ascontiguousarray(E[order]), ls, C, K)
    ptrs = np.ascontiguousarray(_row_addrs(blocks)[order])
    if _lib_for(r * W + C * fw).gf2_annihilator(_ptr(ptrs), r, W, C, _ptr(ls), _ptr(K), fw) != f:
        raise ValueError("annihilator: rows are not echelon with distinct leads")
    return K


def reduce_rows(Q, C, blocks, keep_ops=False, threads=None, full=False):
    """Reduce the rows of Q (in place) against an echelon basis given as
    blocks [(M, rows, leads, gids), ...] until each row's lead is not a basis
    lead (full: until no bit of the row is at a basis lead). Returns (lead,
    X): lead is int64, -1 for rows reduced to zero; with keep_ops X is
    (xoff, xs), CSR: xs[xoff[i]:xoff[i+1]] are the gids of the basis rows
    XORed into row i, in order, and None otherwise."""
    _need(Q, np.uint64, "Q")
    nq, W = Q.shape
    slot = np.zeros(C, dtype=np.uint64)
    sgid = np.full(C, -1, dtype=np.int64)
    for blk, addr in zip(blocks, [_row_addrs([b]) for b in blocks]):
        lead = np.asarray(blk[2], dtype=np.int64)
        slot[lead] = addr
        sgid[lead] = np.asarray(blk[3], dtype=np.int64)
    lib = _native.load()
    if lib is None:
        return reference.reduce_rows(Q, C, blocks, keep_ops, full)
    nt = inner_threads() if threads is None else max(1, int(threads))
    h = _lib_for(nq * W * 64).gf2_reduce_rows(_ptr(Q), nq, W, C, _ptr(slot), _ptr(sgid),
                                          1 if keep_ops else 0, 1 if full else 0, nt)
    if not h:
        raise MemoryError("gf2_reduce_rows failed")
    ps = np.empty(nq, dtype=np.int32)
    cs = np.empty(nq, dtype=np.int32)
    xoff = np.empty(nq + 1, dtype=np.int64)
    lib.gf2_log_copy_meta(h, _ptr(ps), _ptr(cs), _ptr(xoff))
    X = None
    if keep_ops:
        nx = lib.gf2_log_nx(h)
        xs = np.empty(max(nx, 1), dtype=np.int32)
        if nx:
            lib.gf2_log_copy(h, _ptr(ps), _ptr(cs), _ptr(xoff), _ptr(xs))
        X = (xoff, xs[:nx].astype(np.int64))
    lib.gf2_log_free(h)
    return cs.astype(np.int64), X


def syndromes(A, K, idx=None, threads=None):
    """S (n x fw uint64): S[i] = row i of A (row idx[i] when idx is given)
    times K. S[i] == 0 exactly when that row lies in the space K
    annihilates; rows are independent modulo that space exactly when their
    syndromes are independent."""
    _need(A, np.uint64, "A")
    _need(K, np.uint64, "K")
    W = A.shape[1]
    ix = None if idx is None else np.ascontiguousarray(idx, dtype=np.int64)
    R = A.shape[0] if ix is None else len(ix)
    fw = K.shape[1]
    S = np.zeros((R, fw), dtype=np.uint64)
    lib = _native.load()
    if lib is None:
        return reference.syndromes(A if ix is None else A[ix], K)
    nt = inner_threads() if threads is None else max(1, int(threads))
    _lib_for(R * W).gf2_syndromes(_ptr(A), R, W, _ptr(ix) if ix is not None else None,
                                  _ptr(K), fw, _ptr(S), nt)
    return S


def product_syndromes(addrs, W, C, colmap, nv, K, threads=None, rows=None):
    """S (nv*n x fw), j-major: S[j*n + f] = (v_j * row f) . K, where row f is
    at address addrs[f] (W words). The products are never formed. ``rows``
    (the same rows as an array) is used by the reference backend only."""
    _need(K, np.uint64, "K")
    addrs = np.ascontiguousarray(addrs, dtype=np.uint64)
    n = len(addrs)
    fw = K.shape[1]
    S = np.zeros((nv * n, fw), dtype=np.uint64)
    lib = _native.load()
    if lib is None:
        return reference.product_syndromes(rows, colmap, nv, C, K)
    if n:
        nt = inner_threads() if threads is None else max(1, int(threads))
        _lib_for(n * W * nv).gf2_product_syndromes(_ptr(addrs), n, W, C, _ptr(colmap), nv,
                                                   _ptr(K), fw, _ptr(S), nt)
    return S


def product_pairs(addrs, js, W, C, colmap, rows=None):
    """(n x W) packed rows: row p = v_{js[p]} * (the row at addrs[p]).
    ``rows`` (those rows as an array) is used by the reference backend only."""
    addrs = np.ascontiguousarray(addrs, dtype=np.uint64)
    js = np.ascontiguousarray(js, dtype=np.int64)
    out = np.zeros((len(addrs), W), dtype=np.uint64)
    lib = _native.load()
    if lib is None:
        return reference.product_pairs(rows, js, colmap, C, W)
    if len(addrs):
        _lib_for(len(addrs) * W).gf2_product_pairs(_ptr(addrs), _ptr(js), len(addrs), W, C,
                                                   _ptr(colmap), _ptr(out))
    return out


# ---------------------------------------------------------------------------
# canonical op-log JSON and trace hashes
# ---------------------------------------------------------------------------
def canon(obj) -> str:
    return json.dumps(obj, separators=(",", ":"))


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def ops_json_bytes(log: OpLog) -> bytes:
    """Exactly ``canon([[p, c, X.tolist()], ...]).encode()``."""
    if not log.has_X:
        raise ValueError("op log was recorded without X sets")
    lib = _native.load()
    if lib is None:
        return canon([[int(p), int(c), X.tolist()] for p, c, X in zip(log.ps, log.cs, log.Xs)]).encode()
    lib = _lib_for(int(log.xs.size))
    n = lib.gf2_ops_json_bound(log.K, int(log.xs.size))
    buf = np.empty(n, dtype=np.uint8)
    m = lib.gf2_ops_json(_ptr(log.ps), _ptr(log.cs), _ptr(log.xoff), _ptr(log.xs), log.K, _ptr(buf))
    return buf[:m].tobytes()


def _json_ints(v) -> bytes:
    lib = _native.load()
    v = np.ascontiguousarray(v, dtype=np.int32)
    if lib is None:
        return canon(v.tolist()).encode()
    buf = np.empty(12 * v.size + 2, dtype=np.uint8)
    lib = _lib_for(int(v.size))
    return buf[:lib.gf2_json_ints(_ptr(v), v.size, _ptr(buf))].tobytes()


def _json_pairs(a, b) -> bytes:
    lib = _native.load()
    if lib is None:
        return canon([[int(x), int(y)] for x, y in zip(a, b)]).encode()
    buf = np.empty(27 * a.size + 2, dtype=np.uint8)
    lib = _lib_for(int(a.size))
    return buf[:lib.gf2_json_pairs(_ptr(a), _ptr(b), a.size, _ptr(buf))].tobytes()


def trace_hashes(log: OpLog, Z):
    """h_rank, h_set, h_strict, h_ops exactly as EXP-CERTBIN-4e92d7 elim.eliminate:
    sha256 of canon(rank), canon([pivcols, Z]), canon([[p, c], ...]) and the
    canonical op log."""
    h = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    pivcols = np.sort(log.cs)
    return {
        "h_rank": sha(canon(log.K)),
        "h_set": h(b"[" + _json_ints(pivcols) + b"," + _json_ints(np.asarray(Z, dtype=np.int32)) + b"]"),
        "h_strict": h(_json_pairs(log.ps, log.cs)),
        "h_ops": h(ops_json_bytes(log)),
    }


# ---------------------------------------------------------------------------
# replays and back-trace
# ---------------------------------------------------------------------------
def replay_planes(planes, log: OpLog):
    """planes (P, R, W) modified in place -> e (P, K) uint8."""
    _need(planes, np.uint64, "planes")
    lib = _native.load()
    if lib is None:
        return reference.replay_planes(planes, log.ps, log.cs, log.Xs)
    P, R, W = planes.shape
    e = np.zeros((P, log.K), dtype=np.uint8)
    lib = _lib_for(P * R * W)
    lib.gf2_replay_planes(_ptr(planes), P, R, W, _ptr(log.ps), _ptr(log.cs), _ptr(log.xoff),
                          _ptr(log.xs), log.K, _ptr(e))
    return e


def replay_direct(M_orig, log: OpLog, stop_at_zero=False):
    """e (K,) uint8; entries after the first zero are 255 when stop_at_zero."""
    _need(M_orig, np.uint64, "M_orig")
    lib = _native.load()
    if lib is None:
        return reference.replay_direct(M_orig, log.ps, log.cs, log.Xs, stop_at_zero)
    M = M_orig.copy()
    R, W = M.shape
    e = np.full(log.K, 255, dtype=np.uint8)
    lib = _lib_for(R * W)
    lib.gf2_replay_direct(_ptr(M), R, W, _ptr(log.ps), _ptr(log.cs), _ptr(log.xoff), _ptr(log.xs),
                          log.K, 1 if stop_at_zero else 0, _ptr(e))
    return e


def backtrace(log: OpLog, S):
    """S (n_rows, nw) uint64 rewritten in place over the original rows."""
    _need(S, np.uint64, "S")
    lib = _native.load()
    if lib is None:
        return reference.backtrace(log.ps, log.Xs, S)
    lib = _lib_for(int(log.xs.size) * S.shape[1])
    lib.gf2_backtrace(_ptr(S), S.shape[1], _ptr(log.ps), _ptr(log.xoff), _ptr(log.xs), log.K)
    return S


def xor_bits(M, rows, cols):
    """M[rows[i], cols[i]] ^= 1 for every i (duplicates cancel, as XOR)."""
    _need(M, np.uint64, "M")
    rows = np.ascontiguousarray(rows, dtype=np.int64)
    cols = np.ascontiguousarray(cols, dtype=np.int64)
    lib = _native.load()
    if lib is None:
        np.bitwise_xor.at(M, (rows, cols >> 6), np.left_shift(np.uint64(1), (cols & 63).astype(np.uint64)))
        return M
    _lib_for(rows.size).gf2_xor_bits(_ptr(M), M.shape[1], _ptr(rows), _ptr(cols), rows.size)
    return M


def products(rows, colmap, maps, nv, C, W):
    """(nv*n, W) packed rows, j-major: row j*n + f = v_j * rows[f].

    colmap (nv, C) int32 is the native form of ``maps``; both describe the
    same map (see closure.Closure)."""
    _need(rows, np.uint64, "rows")
    lib = _native.load()
    if lib is None:
        return reference.products(rows, maps, nv, C, W)
    n = rows.shape[0]
    out = np.zeros((nv * n, W), dtype=np.uint64)
    if n:
        lib = _lib_for(nv * n * W)
        lib.gf2_products(_ptr(rows), n, W, C, _ptr(colmap), nv, _ptr(out))
    return out


# ---------------------------------------------------------------------------
# batching
# ---------------------------------------------------------------------------
def default_threads() -> int:
    env = os.environ.get("CRYPTO_AR_GF2_THREADS")
    if env:
        return max(1, int(env))
    return max(1, len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else os.cpu_count() or 1)


_tls = threading.local()


def inner_threads() -> int:
    """Threads one elimination may use for itself.

    $CRYPTO_AR_GF2_INNER_THREADS if set; otherwise 1 inside a ``map_threads``
    worker (the pool already fills the cores) and ``default_threads()``
    elsewhere. Only speed depends on it, never output."""
    env = os.environ.get("CRYPTO_AR_GF2_INNER_THREADS")
    if env:
        return max(1, int(env))
    if getattr(_tls, "in_pool", False):
        return 1
    return default_threads()


def _pooled(fn):
    def run(x):
        _tls.in_pool = True
        try:
            return fn(x)
        finally:
            _tls.in_pool = False
    return run


def map_threads(fn, items, threads=None):
    """``list(map(fn, items))`` on a thread pool, order preserved.

    Worth it when ``fn`` spends its time in native kernels (GIL released);
    with the reference backend it only adds overhead, so it runs serially.
    Inside the pool each elimination runs single-threaded (``inner_threads``)."""
    items = list(items)
    threads = threads or default_threads()
    if threads == 1 or backend() != "native" or len(items) < 2:
        return [fn(x) for x in items]
    with ThreadPoolExecutor(max_workers=threads) as ex:
        return list(ex.map(_pooled(fn), items))
