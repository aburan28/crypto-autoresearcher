#!/usr/bin/env python3
"""worker3.py -- PILOT #3 (block-local closure). EXPLORATORY; not program evidence.
One closure job per process (clean peak RSS). Derived from pilot #1/#2 worker.py,
`run_mine` path only, calling my_closure_local (myclosure_local.c).

usage: worker3.py job.json out.json
job: {"N", "equations", "D", "lo": [..N], "hi": [..N], "Lmax", "adj",
      "stop_at_one", "witnesses": [mask, ...]}
"""
import ctypes
import json
import resource
import sys
import time
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent


def csr(equations):
    ptr = array("q", [0]); masks = array("Q")
    for e in equations:
        masks.extend(e); ptr.append(len(masks))
    return ptr, masks


def main():
    job = json.load(open(sys.argv[1]))
    t0 = time.time()
    lib = ctypes.CDLL(str(HERE / "libmyclosure_local.so"))
    lib.my_closure_local.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                                     ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                                     ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.c_void_p,
                                     ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]
    lib.my_eval.restype = ctypes.c_long
    lib.my_eval.argtypes = [ctypes.c_uint64]
    lib.my_ncols.restype = ctypes.c_long
    lib.my_basis_locality.argtypes = [ctypes.c_void_p, ctypes.c_int]
    N, D, eqs = job["N"], job["D"], job["equations"]
    ptr, masks = csr(eqs)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    lo = (ctypes.c_int * N)(*job["lo"]); hi = (ctypes.c_int * N)(*job["hi"])
    rank, one, nprod, ndrop = ctypes.c_long(0), ctypes.c_int(0), ctypes.c_long(0), ctypes.c_long(0)
    dims = (ctypes.c_long * (D + 1))()
    rc = lib.my_closure_local(N, D, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), int(job.get("stop_at_one", 1)),
                              ctypes.addressof(lo), ctypes.addressof(hi), int(job["Lmax"]), int(job["adj"]),
                              ctypes.byref(rank), ctypes.byref(one), dims, ctypes.byref(nprod), ctypes.byref(ndrop))
    out = {"status": "completed" if rc == 0 else f"error_rc{rc}", "rank": rank.value, "contains_one": bool(one.value),
           "dims_by_lmdeg": list(dims), "products": nprod.value, "products_dropped": ndrop.value,
           "rows": len(eqs) + nprod.value - ndrop.value, "ncols": lib.my_ncols()}
    if rc == 0:
        out["eval_rows_not_vanishing"] = [int(lib.my_eval(ctypes.c_uint64(w))) for w in job.get("witnesses", [])[:16]]
        hist = (ctypes.c_long * 8)()
        lib.my_basis_locality(ctypes.addressof(hist), 7)
        out["basis_by_locality"] = list(hist)
    lib.my_free()
    out["wall_s"] = time.time() - t0
    out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    json.dump(out, open(sys.argv[2], "w"))


if __name__ == "__main__":
    main()
