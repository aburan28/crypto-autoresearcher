"""ctypes wrapper for gf2k.c (TASK-20260926-401771). Library path from the
environment variable J1_LIB (default: ./build/libgf2k.so)."""
import ctypes
import os

import numpy as np

_LIB = None


def lib():
    global _LIB
    if _LIB is None:
        path = os.environ.get("J1_LIB", os.path.join(os.getcwd(), "build", "libgf2k.so"))
        L = ctypes.CDLL(path)
        u32p = np.ctypeslib.ndpointer(dtype=np.uint32, flags="C_CONTIGUOUS")
        u64p = np.ctypeslib.ndpointer(dtype=np.uint64, flags="C_CONTIGUOUS")
        i32p = np.ctypeslib.ndpointer(dtype=np.int32, flags="C_CONTIGUOUS")
        L.k_gfmul.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        L.k_gfmul.restype = ctypes.c_uint32
        L.k_s3_eval_all.argtypes = [ctypes.c_uint32, ctypes.c_uint32, u32p]
        L.k_s3_eval_all.restype = None
        L.k_mobius_u32.argtypes = [u32p, ctypes.c_int]
        L.k_mobius_u32.restype = None
        L.k_rref.argtypes = [u64p, ctypes.c_int, ctypes.c_int, ctypes.c_int, i32p]
        L.k_rref.restype = ctypes.c_int
        L.k_parity_check.argtypes = [u64p, ctypes.c_int, u64p, ctypes.c_int, ctypes.c_int, i32p, ctypes.c_void_p]
        L.k_parity_check.restype = ctypes.c_long
        L.k_mul_vj.argtypes = [u64p, u64p, ctypes.c_int, ctypes.c_int, ctypes.c_int, i32p, i32p]
        L.k_mul_vj.restype = ctypes.c_int
        L.k_closure_check.argtypes = [u64p, ctypes.c_int, u64p, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                      ctypes.c_int, i32p, i32p, i32p, i32p]
        L.k_closure_check.restype = ctypes.c_long
        L.k_reduce.argtypes = [u64p, u64p, ctypes.c_int, ctypes.c_int, i32p]
        L.k_reduce.restype = ctypes.c_int
        L.k_step_outside.argtypes = [u64p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     i32p, i32p, i32p, i32p, ctypes.c_int, i32p]
        L.k_step_outside.restype = ctypes.c_long
        _LIB = L
    return _LIB


def s3_eval_all(xR, B):
    out = np.zeros(1 << 20, dtype=np.uint32)
    lib().k_s3_eval_all(xR, B, out)
    return out


def mobius(a, n=20):
    a = np.ascontiguousarray(a, dtype=np.uint32).copy()
    lib().k_mobius_u32(a, n)
    return a


def pack_rows(dense_u8, ncols_padded_words):
    """dense 0/1 uint8 matrix (rows x cols) -> packed uint64 (rows x words)."""
    rows, cols = dense_u8.shape
    padded = np.zeros((rows, ncols_padded_words * 64), dtype=np.uint8)
    padded[:, :cols] = dense_u8
    packed = np.packbits(padded, axis=1, bitorder="little")
    return np.ascontiguousarray(packed.view(np.uint64))


def unpack_rows(packed_u64, ncols):
    b = np.unpackbits(packed_u64.view(np.uint8), axis=1, bitorder="little")
    return b[:, :ncols]


def rref(packed, ncols):
    """In-place RREF of a packed matrix copy. Returns (M, rank, piv)."""
    M = np.ascontiguousarray(packed.copy())
    rows, words = M.shape
    piv = np.zeros(max(rows, 1), dtype=np.int32)
    r = lib().k_rref(M, rows, words, ncols, piv)
    return M, r, piv[:r].copy()


def parity_check(Lp, Vp, want_per_v=False):
    nL, words = Lp.shape
    nV = Vp.shape[0]
    first = np.zeros(2, dtype=np.int32)
    bad = np.zeros(max(nV, 1), dtype=np.int32) if want_per_v else None
    n = lib().k_parity_check(np.ascontiguousarray(Lp), nL, np.ascontiguousarray(Vp), nV, words, first,
                             bad.ctypes.data if want_per_v else None)
    return n, (int(first[0]), int(first[1])), (bad[:nV] if want_per_v else None)


def closure_check(Lp, Kp, ncols, nv, mask_of_col, col_of_mask):
    nL, words = Lp.shape
    nK = Kp.shape[0]
    first = np.zeros(3, dtype=np.int32)
    ovf = np.zeros(1, dtype=np.int32)
    n = lib().k_closure_check(np.ascontiguousarray(Lp), nL, np.ascontiguousarray(Kp), nK, words, ncols, nv,
                              mask_of_col, col_of_mask, first, ovf)
    return n, tuple(int(x) for x in first), int(ovf[0])


def step_outside(R, rank, ncols, nv, Dm1, piv, deg_of_col, mask_of_col, col_of_mask, stop_first=False):
    words = R.shape[1]
    first = np.zeros(2, dtype=np.int32)
    n = lib().k_step_outside(np.ascontiguousarray(R), rank, words, ncols, nv, Dm1,
                             np.ascontiguousarray(piv, dtype=np.int32), deg_of_col, mask_of_col, col_of_mask,
                             1 if stop_first else 0, first)
    return n, (int(first[0]), int(first[1]))
