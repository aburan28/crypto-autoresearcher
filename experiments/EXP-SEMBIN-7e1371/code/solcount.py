#!/usr/bin/env python3
"""solcount.py -- ctypes binding for count_m2.c, the exact |V(I)| of the
m = t = 2 systems, plus its self-check against an O(2^{2k}) reference count.

Used to decide the degree-4 certificate's verdict at the n = 40..45 window,
where no Groebner completion is affordable on this host and |V(I)| would
otherwise be unknown.  The count is exhaustive over V x V, so it is exact and
it is not evidence about Groebner behaviour -- it is the denominator the
verdict is compared against.
"""
from __future__ import annotations

import ctypes
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
_lib = ctypes.CDLL(str(HERE / "libcountm2.so"))
_lib.count_m2.restype = ctypes.c_longlong
_lib.count_m2.argtypes = [ctypes.c_int, ctypes.c_uint64, ctypes.c_int,
                          ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint64, ctypes.c_uint64,
                          ctypes.POINTER(ctypes.c_longlong), ctypes.POINTER(ctypes.c_longlong)]
_lib.count_m2_reference.restype = ctypes.c_longlong
_lib.count_m2_reference.argtypes = [ctypes.c_int, ctypes.c_uint64, ctypes.c_int,
                                    ctypes.POINTER(ctypes.c_uint64), ctypes.c_uint64, ctypes.c_uint64]


def _basis_array(basis):
    arr = (ctypes.c_uint64 * len(basis))(*[ctypes.c_uint64(b).value for b in basis])
    return arr


def count(inst: dict, reference: bool = False) -> dict:
    """Exact |V(I)| for a chained_S3_eq5 instance with t = 2 (or the identical
    single_S_eq4 instance at m = 2)."""
    if inst["t"] != 2:
        return {"status": "not_applicable", "reason": f"t = {inst['t']} != 2"}
    n, k = inst["n"], inst["k"]
    if n > 63:
        return {"status": "not_applicable", "reason": f"n = {n} > 63 (uint64 field element)"}
    arr = _basis_array(inst["subspace_basis"])
    pc = ctypes.c_longlong(0)
    mx = ctypes.c_longlong(0)
    t0 = time.time()
    total = _lib.count_m2(n, inst["modulus"], k, arr, inst["z"], inst["B"],
                          ctypes.byref(pc), ctypes.byref(mx))
    out = {"status": "completed", "instrument": "exhaustive_count_over_V", "solutions": int(total),
           "x1_with_solution": int(pc.value), "max_solutions_per_x1": int(mx.value),
           "enumerated": 1 << k, "wall_s": time.time() - t0,
           "method": "Gray-code enumeration of x1 in V; F_2 linear solve for x2 in V"}
    if reference:
        t0 = time.time()
        ref = _lib.count_m2_reference(n, inst["modulus"], k, arr, inst["z"], inst["B"])
        out["reference_solutions"] = int(ref)
        out["reference_wall_s"] = time.time() - t0
        out["reference_agrees"] = int(ref) == int(total)
    return out


_chain = ctypes.CDLL(str(HERE / "libcountchain.so"))
_chain.count_chain.restype = ctypes.c_longlong
_chain.count_chain.argtypes = [ctypes.c_int, ctypes.c_uint64, ctypes.c_int, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_uint64), ctypes.POINTER(ctypes.c_uint64),
                               ctypes.c_long, ctypes.c_uint64, ctypes.c_uint64,
                               ctypes.POINTER(ctypes.c_longlong)]


def count_chained(inst: dict) -> dict:
    """Exact |V(I)| for a chained_S3_eq5 instance at any t >= 2, by walking the
    chain: every equation is F_2-affine in the one unknown it is solved for."""
    if inst.get("family") != "chained_S3_eq5":
        return {"status": "not_applicable", "reason": f"family {inst.get('family')}"}
    n, k, t = inst["n"], inst["k"], inst["t"]
    if n > 63:
        return {"status": "not_applicable", "reason": f"n = {n} > 63 (uint64 field element)"}
    if k > 26:
        return {"status": "not_applicable", "reason": f"k = {k} > 26: |V|^(t-1) enumeration too large"}
    basis = inst["subspace_basis"]
    vlist = [0] * (1 << k)
    for mask in range(1 << k):
        v = 0
        mm = mask
        while mm:
            j = (mm & -mm).bit_length() - 1
            v ^= basis[j]
            mm &= mm - 1
        vlist[mask] = v
    barr = _basis_array(basis)
    varr = _basis_array(vlist)
    ko = ctypes.c_longlong(0)
    t0 = time.time()
    total = _chain.count_chain(n, inst["modulus"], t, k, barr, varr, len(vlist),
                               inst["z"], inst["B"], ctypes.byref(ko))
    return {"status": "completed" if ko.value == 0 else "completed_with_skipped_fibres",
            "instrument": "exhaustive_count_chain", "solutions": int(total),
            "kernel_overflow_fibres": int(ko.value), "enumerated_V": len(vlist),
            "wall_s": time.time() - t0,
            "method": "chain walk: each equation is F_2-affine in the unknown solved for"}
