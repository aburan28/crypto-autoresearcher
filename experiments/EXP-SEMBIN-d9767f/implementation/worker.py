#!/usr/bin/env python3
"""worker.py -- PILOT (m3closure). One closure job per process (clean peak RSS).

usage: worker.py job.json out.json
job: {"N", "equations", "kind": "M"|"W"|"myM"|"myW", "D", "mem_cap_gb",
      "witnesses": [mask, ...] (known Boolean solutions, may be empty),
      "evalcheck": bool (use the -DECH_EVALCHECK build with witnesses[0])}
M  = plain single-level Macaulay M_D (closure_cert.macaulay_single_level path,
     libclosure / M4RI PLUQ); W = mutant closure W_D to fixpoint (closure_run,
     max_iter 64, stops when 1 enters). myM/myW = independent C eliminator.
"""
import ctypes
import json
import os
import resource
import sys
import time
from array import array
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))


def csr(equations):
    ptr = array("q", [0]); masks = array("Q")
    for e in equations:
        masks.extend(e); ptr.append(len(masks))
    return ptr, masks


def run_libclosure(job):
    import closure_cert as cc
    if job.get("evalcheck"):
        lib = ctypes.CDLL(str(HERE / "vendor" / "libclosure_eval.so"))
        # mirror the restype/argtypes closure_cert sets on its own handle
        lib.closure_run.restype = ctypes.c_int
        lib.closure_run.argtypes = cc._lib.closure_run.argtypes
        for fn, rt in [("closure_rank", ctypes.c_long), ("closure_ncols", ctypes.c_long),
                       ("closure_count_deg", ctypes.c_long), ("closure_dropped_terms", ctypes.c_longlong),
                       ("closure_elimination", ctypes.c_char_p), ("closure_resumed", ctypes.c_long),
                       ("closure_ech_faults", ctypes.c_long), ("closure_m4ri_library", ctypes.c_char_p),
                       ("closure_row_masks", ctypes.c_long), ("closure_standard_count", ctypes.c_long),
                       ("closure_eval_rows", ctypes.c_long)]:
            getattr(lib, fn).restype = rt
        lib.closure_count_deg.argtypes = [ctypes.c_int]
        lib.closure_lm_dump.argtypes = [ctypes.c_void_p]
        lib.closure_row_masks.argtypes = [ctypes.c_long, ctypes.c_void_p]
        lib.closure_standard_count.argtypes = [ctypes.c_long]
        lib.closure_free.restype = None
        lib.closure_reset_dropped.restype = None
        lib.closure_set_witness.argtypes = [ctypes.c_uint64]
        lib.closure_set_witness(ctypes.c_uint64(job["witnesses"][0]))
        cc._lib = lib
        cc.ELIMINATION = lib.closure_elimination().decode()
    lib = cc._lib
    lib.closure_eval_rows.restype = ctypes.c_long
    lib.closure_eval_rows.argtypes = [ctypes.c_uint64, ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_long)]
    lib.closure_ech_stats.argtypes = [ctypes.POINTER(ctypes.c_long)] * 3
    lib.closure_ech_reset()
    N, D, eqs = job["N"], job["D"], job["equations"]
    max_iter = 1 if job["kind"] == "M" else 64
    res = cc._run(N, D, eqs, max_iter, job["mem_cap_gb"])
    out = {"status": res["status"], "ncols": res["ncols"], "rank": res["rank"],
           "contains_one": res["contains_one"], "iterations": res["iterations"],
           "max_rows_seen": res["max_rows_seen"], "lib_wall_s": res["wall_s"],
           "dropped_terms_above_D": res["dropped_terms_above_D"], "elimination": res["elimination"],
           "elimination_faults": res["elimination_faults"], "m4ri_library": res["m4ri_library"]}
    if job["kind"] == "M":
        # Macaulay row count: generators * multipliers (iteration 1 'rows')
        out["rows"] = res["iterations"][1]["rows"] if len(res["iterations"]) > 1 else res["iterations"][0]["rows"]
    else:
        out["rows"] = res["max_rows_seen"]
    if res["status"] == "completed":
        out["dims_by_lmdeg"] = [lib.closure_count_deg(d) for d in range(D + 1)]
        if not res["contains_one"]:
            c = lib.closure_standard_count(1000000)
            out["standard_monomials"] = c if c <= 1000000 else None
        # evaluation check at every known zero (all basis rows must vanish)
        bad = []
        for w in job.get("witnesses", [])[:64]:
            fb, fc = ctypes.c_long(0), ctypes.c_long(0)
            bad.append(int(lib.closure_eval_rows(ctypes.c_uint64(w), ctypes.byref(fb), ctypes.byref(fc))))
        out["eval_rows_not_vanishing"] = bad
        # nnz of the final basis (echelon form)
        buf = (ctypes.c_uint64 * (res["ncols"] + 1))()
        nnz = 0
        for i in range(res["rank"]):
            nnz += lib.closure_row_masks(i, ctypes.addressof(buf))
        out["basis_nnz"] = nnz
    calls, mism, first = ctypes.c_long(0), ctypes.c_long(0), ctypes.c_long(0)
    lib.closure_ech_stats(ctypes.byref(calls), ctypes.byref(mism), ctypes.byref(first))
    out["ech_calls"], out["ech_evalcheck_mismatch"] = calls.value, mism.value
    lib.closure_free()
    return out


def run_mine(job):
    lib = ctypes.CDLL(str(HERE / "libmyclosure.so"))
    lib.my_macaulay.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p,
                                ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.c_void_p,
                                ctypes.POINTER(ctypes.c_long)]
    lib.my_closure.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int,
                               ctypes.POINTER(ctypes.c_long), ctypes.POINTER(ctypes.c_int), ctypes.c_void_p,
                               ctypes.POINTER(ctypes.c_long)]
    lib.my_eval.restype = ctypes.c_long
    lib.my_eval.argtypes = [ctypes.c_uint64]
    lib.my_ncols.restype = ctypes.c_long
    N, D, eqs = job["N"], job["D"], job["equations"]
    ptr, masks = csr(eqs)
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    rank, one, cnt = ctypes.c_long(0), ctypes.c_int(0), ctypes.c_long(0)
    dims = (ctypes.c_long * (D + 1))()
    if job["kind"] == "myM":
        rc = lib.my_macaulay(N, D, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb),
                             ctypes.byref(rank), ctypes.byref(one), dims, ctypes.byref(cnt))
    else:
        rc = lib.my_closure(N, D, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), int(job.get("stop_at_one", 1)),
                            ctypes.byref(rank), ctypes.byref(one), dims, ctypes.byref(cnt))
    out = {"status": "completed" if rc == 0 else f"error_rc{rc}", "rank": rank.value, "contains_one": bool(one.value),
           "dims_by_lmdeg": list(dims), "rows": cnt.value, "ncols": lib.my_ncols(),
           "eval_rows_not_vanishing": [int(lib.my_eval(ctypes.c_uint64(w))) for w in job.get("witnesses", [])[:16]]}
    lib.my_free()
    return out


def main():
    job = json.load(open(sys.argv[1]))
    t0 = time.time()
    out = run_mine(job) if job["kind"].startswith("my") else run_libclosure(job)
    out["wall_s"] = time.time() - t0
    out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    json.dump(out, open(sys.argv[2], "w"))


if __name__ == "__main__":
    main()
