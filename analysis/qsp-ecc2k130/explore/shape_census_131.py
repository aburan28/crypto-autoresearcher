#!/usr/bin/env python3
"""IDEA-20260916-a17f43 Stage 3, feasible part: the n = 131 census of the
conjugate-degree-2 shape L_R = X^{2^{a+1}} + c(X) X^{2^a} + e(X), c, e in
F_2[X] of degree <= d0, at admissible a (r <= q, 131 = q a + r) small enough
for the O(deg^2) gcd in gf2rc: a in {11, 13, 14, 16, 18} at d0 <= 3, a = 21
at d0 <= 2.  Triggered by the toy positives at (n, a, d0) = (31, 5, 3) and
(29, 5, 3).  Analysis, not evidence.  Output: shape_census_131.json."""
import json, subprocess, sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qsp_explore import clmul, deg, is_linearized, poly_str, polys_of_degree, root_count_batch

CELLS = [(11, 3), (13, 3), (14, 3), (16, 3), (18, 3), (21, 2)]
out = {}
for a, d0 in CELLS:
    q, r = divmod(131, a)
    assert r <= q, (a, q, r)
    t0 = time.time()
    items = []
    for dc in range(0, d0 + 1):
        for c in (range(2) if dc == 0 else polys_of_degree(dc)):
            for de in range(0, d0 + 1):
                for e in (range(2) if de == 0 else polys_of_degree(de)):
                    lam = (clmul(c, 1 << (1 << a))) ^ e if c else e
                    if lam == 0 or (deg(c) <= 0 and is_linearized(e)):
                        continue
                    items.append((c, e, lam))
    Ns = root_count_batch(131, [(a + 1, lam) for _, _, lam in items])
    hist = {}
    top = []
    for (c, e, lam), N in zip(items, Ns):
        hist[N] = hist.get(N, 0) + 1
        if N > 2:
            top.append({"c": poly_str(c) if c else "0", "e": poly_str(e) if e else "0", "N": N})
    out[f"a{a}_d0{d0}"] = {"q": q, "r": r, "candidates": len(items), "max_N": max(Ns), "needed": 1 << a,
                          "correspondence_bound": d0 ** (q + 1) + (2 ** (q + 1)) * (1 << (a - r)),
                          "histogram": dict(sorted(hist.items())), "candidates_with_N_gt_2": top, "seconds": round(time.time() - t0, 1)}
    print(a, d0, out[f"a{a}_d0{d0}"]["max_N"], out[f"a{a}_d0{d0}"]["seconds"], flush=True)
    json.dump(out, open("shape_census_131.json", "w"), indent=1)
