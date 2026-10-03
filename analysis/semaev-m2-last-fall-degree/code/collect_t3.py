#!/usr/bin/env python3
"""Collect m=t=3 closure outcomes from batch logs (logc3_<basis>.txt) into results/instances_t3.json."""
import json, glob, re, os
recs = []
for basis, lab in (("rand", "C"), ("poly", "D")):
    log = f"logc3_{basis}.txt"
    if not os.path.exists(log): continue
    outcome = {}
    for line in open(log):
        m = re.match(r"n=(\d+) k=(\d+) (\S+) \| M4_dims ([\d ]+) M4_one (\d) W4_dims ([\d ]+) W4_one (\d) iters (\d+) ncols (\d+)\s+t=([\d.]+)s", line.strip())
        if m:
            outcome[m.group(3)] = dict(M4_dims=list(map(int, m.group(4).split())), M4_one=int(m.group(5)),
                                       W4_dims=list(map(int, m.group(6).split())), W4_one=int(m.group(7)),
                                       iters=int(m.group(8)), ncols=int(m.group(9)), seconds=float(m.group(10)))
    for mf in sorted(glob.glob(f"sysc3{basis}*/meta_c3_*.json"), key=lambda x: int(re.search(r'_n(\d+)_', x).group(1))):
        for i, e in enumerate(json.load(open(mf))):
            fn = os.path.basename(e["file"])
            recs.append(dict(name=f"{lab}{e['n']}{'abcdefgh'[i]}", t=3, n=e["n"], k=e["k"], basis=basis, seed=int(re.search(r'_(\d+)_\d+\.sys', fn).group(1)),
                             modulus_hex=format(e["f"], "x"), a2=e["a2"], a6_hex=format(e["a6"], "x"), z_hex=format(e["z"], "x"),
                             V_basis_hex=[format(b, "x") for b in e["basis"]], boolean_solutions=e["nsol"],
                             closure_D4=outcome.get(fn), d_ref=("<=4" if outcome.get(fn, {}).get("W4_one") else (">=5" if fn in outcome else None))))
recs = [r for r in recs if r["closure_D4"] is not None]   # only instances whose closure has finished
json.dump(recs, open("results/instances_t3.json", "w"), indent=1)
for r in recs: print(r["name"], r["n"], r["k"], r["basis"], r["d_ref"])
