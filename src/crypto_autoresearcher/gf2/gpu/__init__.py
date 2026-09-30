"""CUDA trailing-update path for the dense GF(2) column pass.

Mirrors ``_kernels.c::tail_chunk``. Available only when CuPy sees a CUDA
device; otherwise ``available()`` is false and callers keep the CPU OpenMP
path. Bit-identical to the CPU kernel on every tested input (see
``tests/test_gf2_gpu_tail.py``).
"""
from __future__ import annotations

from pathlib import Path

_DIR = Path(__file__).resolve().parent
_mod = None
_reason = "not probed"


def available() -> tuple[bool, str]:
    global _reason
    try:
        import cupy  # noqa: F401
    except Exception as exc:
        _reason = f"cupy not importable: {exc}"
        return False, _reason
    try:
        import cupy as cp
        if cp.cuda.runtime.getDeviceCount() < 1:
            _reason = "cupy present but no CUDA device"
            return False, _reason
    except Exception as exc:
        _reason = f"no usable CUDA device: {exc}"
        return False, _reason
    _reason = "ok"
    return True, _reason


def _module():
    global _mod
    if _mod is not None:
        return _mod
    import cupy as cp
    src = (_DIR / "tail_update.cu").read_text()
    _mod = cp.RawModule(code=src, backend="nvrtc", options=("-std=c++14",))
    return _mod


def cpu_tail_chunk(M, W, w0, x0, ch, rows, cfs, cw, Bs, tail, npiv, tables):
    """Reference (numpy) of the same update, for differential tests."""
    import numpy as np
    nr = len(rows)
    ngroups = (npiv + 7) // 8
    if not tables:
        for a in range(nr):
            row = M[rows[a], w0 + x0:w0 + x0 + ch]
            for q in range(cw):
                cf = int(cfs[a, q]) if cfs.ndim == 2 else int(cfs[a * cw + q])
                while cf:
                    i = 64 * q + (cf & -cf).bit_length() - 1
                    cf &= cf - 1
                    row ^= Bs[i, x0:x0 + ch]
            M[rows[a], w0 + x0:w0 + x0 + ch] = row
        return
    T = np.zeros((ngroups, 256, ch), dtype=np.uint64)
    for g in range(ngroups):
        k = min(8, npiv - 8 * g)
        ns = 1 << k
        Tg = T[g]
        for s2 in range(1, ns):
            lb = (s2 & -s2).bit_length() - 1
            Tg[s2] = Tg[s2 & (s2 - 1)] ^ Bs[8 * g + lb, x0:x0 + ch]
    for a in range(nr):
        row = M[rows[a], w0 + x0:w0 + x0 + ch].copy()
        cf = cfs[a] if cfs.ndim == 2 else cfs[a * cw:(a + 1) * cw]
        tlist = []
        for g in range(ngroups):
            s2 = int((int(cf[g >> 3]) >> (8 * (g & 7))) & 0xFF)
            if s2:
                tlist.append(T[g, s2])
        for t in tlist:
            row ^= t
        M[rows[a], w0 + x0:w0 + x0 + ch] = row


def gpu_tail_chunk(M_host, W, w0, x0, ch, rows, cfs, cw, Bs, tail, npiv, tables):
    """Run the CUDA kernel on host numpy arrays; returns updated M copy.

    Allocates device buffers for this call. Fine for correctness and for
    one-shot benches; a production column_pass would keep M resident.
    """
    import cupy as cp
    import numpy as np

    ok, reason = available()
    if not ok:
        raise RuntimeError(f"gf2 GPU path unavailable: {reason}")

    M = np.ascontiguousarray(M_host, dtype=np.uint64).copy()
    rows = np.ascontiguousarray(rows, dtype=np.int32)
    cfs = np.ascontiguousarray(cfs, dtype=np.uint64)
    if cfs.ndim == 1:
        cfs = cfs.reshape(-1, cw)
    Bs = np.ascontiguousarray(Bs, dtype=np.uint64)
    if Bs.ndim == 1:
        Bs = Bs.reshape(npiv, tail)

    dM = cp.asarray(M)
    drows = cp.asarray(rows)
    dcfs = cp.asarray(cfs.ravel())
    dBs = cp.asarray(Bs.ravel())
    ngroups = (npiv + 7) // 8
    dT = cp.zeros(ngroups * 256 * ch, dtype=cp.uint64) if tables else cp.zeros(1, dtype=cp.uint64)

    kern = _module().get_function("gf2_tail_chunk")
    block = 128
    kern((1,), (block,),
         (dM, np.int64(W), np.int64(w0), np.int64(x0), np.int64(ch),
          drows, dcfs, np.int32(cw), np.int64(len(rows)),
          dBs, np.int64(tail), np.int32(npiv), np.int32(1 if tables else 0), dT))
    cp.cuda.Stream.null.synchronize()
    return cp.asnumpy(dM)
