#!/usr/bin/env python3
"""worker4.py -- LEADS PILOT #4. EXPLORATORY; not program evidence. One job per process.
job kinds:
  cap : one closure (Lmax, du, winmask=all), stop at 1; witness evaluation
  pre : the same closure twice: from scratch (single phase) and two-phase (z-free part to
        fixpoint, then the target block); reports both
  win : windowed message passing over 2-block windows (see pilot4.py)
"""
import ctypes, json, resource, sys, time
from array import array
from pathlib import Path
HERE = Path(__file__).resolve().parent
lib = ctypes.CDLL(str(HERE / "libmyclosure4.so"))
lib.my_closure4.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long,
                            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int,
                            ctypes.c_uint64, ctypes.c_uint64, ctypes.c_int, ctypes.c_void_p]
lib.my_eval.restype = ctypes.c_long; lib.my_eval.argtypes = [ctypes.c_uint64]
lib.my_project.restype = ctypes.c_long
lib.my_project.argtypes = [ctypes.c_uint64, ctypes.c_long, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long]
ALL = (1 << 64) - 1

def closure(N, D, eqs, ngens0, stop, lo, hi, Lmax, adj, winmask, umask, du):
    ptr = array("q", [0]); masks = array("Q")
    for e in eqs:
        masks.extend(e); ptr.append(len(masks))
    pb = (ctypes.c_long * len(ptr)).from_buffer(ptr)
    mb = (ctypes.c_uint64 * max(1, len(masks))).from_buffer(masks)
    clo = (ctypes.c_int * N)(*lo); chi = (ctypes.c_int * N)(*hi)
    st = (ctypes.c_double * 11)()
    rc = lib.my_closure4(N, D, len(eqs), ctypes.addressof(pb), ctypes.addressof(mb), ngens0, stop,
                         ctypes.addressof(clo), ctypes.addressof(chi), Lmax, adj, winmask, umask, du, st)
    k = ["rank1", "prod1", "drop1", "sec1", "rank", "one", "prod", "drop", "sec2", "ncols"]
    o = {kk: st[i] for i, kk in enumerate(k)}
    o["rc"] = rc; o["one"] = bool(o["one"])
    for kk in ("rank1", "prod1", "drop1", "rank", "prod", "drop", "ncols"):
        o[kk] = int(o[kk])
    return o

def project(keep, cap_rows=400000, cap_masks=40_000_000):
    op = (ctypes.c_long * (cap_rows + 1))(); om = (ctypes.c_uint64 * cap_masks)()
    nr = lib.my_project(keep, cap_rows, ctypes.addressof(op), ctypes.addressof(om), cap_masks)
    if nr < 0:
        raise SystemExit("project overflow")
    return [list(om[op[i]:op[i + 1]]) for i in range(nr)]

def evalpoly(p, a):
    v = 0
    for mm in p:
        if mm & a == mm: v ^= 1
    return v

def main():
    job = json.load(open(sys.argv[1])); out = {}
    N, D, eqs, lo, hi = job["N"], job["D"], job["equations"], job["lo"], job["hi"]
    wit = job.get("witnesses", [])[:16]
    t0 = time.time()
    if job["kind"] == "cap":
        o = closure(N, D, eqs, len(eqs), 1, lo, hi, job["Lmax"], -1, ALL, job["umask"], job["du"])
        if o["rc"] == 0:
            o["eval_rows_not_vanishing"] = [int(lib.my_eval(ctypes.c_uint64(w))) for w in wit]
        lib.my_free(); out = o
    elif job["kind"] == "pre":
        a = closure(N, D, eqs, len(eqs), 1, lo, hi, job["Lmax"], -1, ALL, job["umask"], job["du"]); lib.my_free()
        b = closure(N, D, eqs, job["ngens0"], 1, lo, hi, job["Lmax"], -1, ALL, job["umask"], job["du"])
        if b["rc"] == 0:
            b["eval_rows_not_vanishing"] = [int(lib.my_eval(ctypes.c_uint64(w))) for w in wit]
        lib.my_free(); out = {"scratch": a, "two_phase": b}
    elif job["kind"] == "win":
        W = job["windows"]   # list of {"mask": int, "gens": [eq idx], "left": overlap mask or 0, "right": ...}
        msgs = [[] for _ in W]   # incoming messages per window (polys)
        dims = {}               # (window, side) -> projected dimension seen
        sched = list(range(len(W))) + list(range(len(W) - 2, 0, -1))
        hist = []; one = False; sweeps = 0; changed = True; bad = 0
        while changed and not one and sweeps < job.get("max_sweeps", 6):
            changed = False; sweeps += 1
            for a in (sched if sweeps == 1 else sched):
                w = W[a]
                g = [eqs[i] for i in w["gens"]] + msgs[a]
                o = closure(N, D, g, len(g), 1, lo, hi, 99, -1, w["mask"], job["umask"], job["du"])
                rec = {"sweep": sweeps, "window": a, "ngens": len(g), "ncols": o["ncols"], "rank": o["rank"],
                       "one": o["one"], "prod": o["prod"], "sec": o["sec2"], "rc": o["rc"]}
                if o["rc"] != 0:
                    hist.append(rec); lib.my_free(); out["error"] = o["rc"]; changed = False; break
                if o["one"]:
                    hist.append(rec); lib.my_free(); one = True; break
                for side, nb in (("left", a - 1), ("right", a + 1)):
                    if 0 <= nb < len(W):
                        P = project(w[side])
                        rec[side + "_dim"] = len(P)
                        if len(P) > dims.get((a, side), -1):
                            dims[(a, side)] = len(P); changed = True
                            # replace the neighbour's message from this window
                            msgs[nb] = [p for p in msgs[nb] if p is not None]
                            W[nb].setdefault("from", {})[a] = P
                            bad += sum(evalpoly(p, x) for p in P for x in wit)
                lib.my_free(); hist.append(rec)
                for b_ in range(len(W)):
                    msgs[b_] = [p for src in W[b_].get("from", {}).values() for p in src]
        out.update({"one": one, "sweeps": sweeps, "history": hist, "message_witness_nonvanishing": bad,
               "max_window_cols": max(h["ncols"] for h in hist)})
    out["wall_s"] = time.time() - t0
    out["peak_rss_mb"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    json.dump(out, open(sys.argv[2], "w"))

if __name__ == "__main__":
    main()
