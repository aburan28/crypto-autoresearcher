"""Public GF(2) kernels: native when available, numpy reference otherwise.

Both backends return identical results (tests/test_gf2_kernels.py). The op
log is an ``OpLog``: flat int32/int64 arrays instead of a list of per-step
arrays, so it crosses the C boundary without copies; ``OpLog.Xs`` gives the
list-of-arrays view the archived engines use.

Native calls release the GIL, so independent matrices can be processed on a
thread pool (``map_threads``).
"""
from __future__ import annotations

import hashlib
import json
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from . import _native, reference


def backend() -> str:
    return "native" if _native.load() is not None else "reference"


def _ptr(a):
    return a.ctypes.data


# Calls touching fewer words than this keep the GIL (see _native.load_holding_gil).
GIL_RELEASE_WORDS = 1 << 15


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
def column_pass(M, C, keep_ops=True, algorithm="blocked") -> OpLog:
    """The declared column-major solver on packed M (modified in place).

    algorithm: "blocked" (word-blocked with Gray-code tables) or "direct"
    (per-column buckets); both native forms return the reference's op log and
    final matrix, and are cross-checked in tests."""
    _need(M, np.uint64, "M")
    R, W = M.shape
    lib = _native.load()
    if lib is None:
        ps, cs, Xs, total = reference.column_pass(M, C, keep_ops)
        return OpLog.from_lists(ps, cs, Xs, total)
    import ctypes
    tot = ctypes.c_int64(0)
    lib = _lib_for(R * W)
    fn = {"blocked": lib.gf2_column_pass_blocked, "direct": lib.gf2_column_pass}[algorithm]
    h = fn(_ptr(M), R, W, C, 1 if keep_ops else 0, ctypes.byref(tot))
    if not h:
        raise MemoryError("gf2_column_pass: allocation failed")
    try:
        K = lib.gf2_log_K(h)
        nx = lib.gf2_log_nx(h)
        ps = np.empty(K, dtype=np.int32)
        cs = np.empty(K, dtype=np.int32)
        xoff = np.empty(K + 1, dtype=np.int64)
        xs = np.empty(nx, dtype=np.int32)
        lib.gf2_log_copy(h, _ptr(ps), _ptr(cs), _ptr(xoff), _ptr(xs))
    finally:
        lib.gf2_log_free(h)
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
    import ctypes
    R, W = M0.shape
    Z = np.empty(max(R, 1), dtype=np.int32)
    leads = np.empty(max(min(R, C), 1), dtype=np.int32)
    nl = ctypes.c_int64(0)
    lib = _lib_for(R * W)
    nz = lib.gf2_row_pass(_ptr(M0), R, W, C, _ptr(Z), _ptr(leads), ctypes.byref(nl))
    if nz < 0:
        raise MemoryError("gf2_row_pass: allocation failed")
    return Z[:nz].tolist(), leads[:nl.value].tolist()


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


def map_threads(fn, items, threads=None):
    """``list(map(fn, items))`` on a thread pool, order preserved.

    Worth it when ``fn`` spends its time in native kernels (GIL released);
    with the reference backend it only adds overhead, so it runs serially."""
    items = list(items)
    threads = threads or default_threads()
    if threads == 1 or backend() != "native" or len(items) < 2:
        return [fn(x) for x in items]
    with ThreadPoolExecutor(max_workers=threads) as ex:
        return list(ex.map(fn, items))
