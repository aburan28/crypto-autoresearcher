#!/usr/bin/env python3
"""label.py -- m4-sat-cost-pilot. EXPLORATORY, hypothesis-generating; not program evidence.

Builds and labels chained-S_3 instances (t = m) for one cell (m, n, k) exactly as
pilot #2 does (pilot2.label), but with k given explicitly, and writes
<instdir>/m{m}-n{n}-k{k}.json. Labels come from the two exhaustive enumerators of
pilot #2: pilot2_lib.chain_solutions (curve-level root solving, numpy) and
pilot2_lib.boolean_count_chain (C enumerator over all 2^(mk) x-assignments with
affine u-solves). Their agreement is recorded per instance (enum_agree).

usage: label.py <m> <n> <k> <ntargets> [--pilot2 DIR] [--out DIR]
"""
import argparse
import json
import sys
import time
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("m", type=int); ap.add_argument("n", type=int); ap.add_argument("k", type=int)
ap.add_argument("ntargets", type=int)
ap.add_argument("--pilot2", default="/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/iterate/m45closure",
                help="directory holding pilot2_lib.py, pilot_lib.py, vendor/ and libcountchain.so "
                     "(repo copy: analysis/ecdlp2m-iteration-20261009/m45-closure-pilot, build the .so from count_chain.c)")
ap.add_argument("--out", default="/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/m4sat/instances")
ap.add_argument("--no-bool", action="store_true", help="skip the C enumerator (label from chain_solutions only)")
a = ap.parse_args()

sys.path.insert(0, a.pilot2)
import pilot_lib as L  # noqa: E402
import pilot2_lib as P  # noqa: E402

m, n, k = a.m, a.n, a.k
t0 = time.time()
cv = L.pick_curve(n, 0)
t_curve = time.time() - t0
basis = [1 << j for j in range(k)]
V = L.VSpace(cv["F"], basis)
zs = L.subgroup_targets(cv, a.ntargets, 0)
insts, seen = [], set()
for i, z in enumerate(zs):
    dup = z in seen; seen.add(z)
    t1 = time.time()
    sols = P.chain_solutions(cv["F"], V, cv["b"], z, m)
    t2 = time.time()
    sysm = P.build_chain(n, k, m, basis, cv["b"], z, cv["modulus"])
    if a.no_bool:
        cnt, bsols = len(sols), sols[:4096]
    else:
        cnt, bsols = P.boolean_count_chain(sysm)
    t3 = time.time()
    evals_ok = all(not any(L.eval_system(sysm["equations"], s)) for s in sols[:256])
    agree = (cnt == len(sols)) and (bsols == sols[:len(bsols)])
    insts.append({"id": f"m{m}-n{n}-k{k}-S3-{i:04d}", "m": m, "n": n, "k": k, "N": sysm["N"],
                  "neq": len(sysm["equations"]), "z": z, "dup_target": dup, "nsol": len(sols),
                  "nsol_boolean": cnt, "bool_enum": not a.no_bool, "enum_agree": bool(agree),
                  "eval_ok": bool(evals_ok), "solutions": sols[:64],
                  "enum_curve_s": t2 - t1, "enum_bool_s": t3 - t2})
    print(f"  {insts[-1]['id']} nsol={len(sols)} bool={cnt} agree={agree} t=({t2-t1:.1f},{t3-t2:.1f})", flush=True)
cell = {"m": m, "n": n, "k": k, "basis": basis, "modulus": cv["modulus"], "a": cv["a"], "b": cv["b"],
        "order": cv["order"], "q": cv["q"], "h": cv["h"], "curve_tries": cv["tries"], "curve_search_s": t_curve,
        "curve_seed": 0, "target_seed": 0, "instances": insts}
Path(a.out).mkdir(parents=True, exist_ok=True)
json.dump(cell, open(Path(a.out) / f"m{m}-n{n}-k{k}.json", "w"))
nu = sum(1 for x in insts if x["nsol"] == 0 and not x["dup_target"])
ns = sum(1 for x in insts if x["nsol"] > 0 and not x["dup_target"])
print(f"m{m}-n{n}-k{k}: N={insts[0]['N']} neq={insts[0]['neq']} b={cv['b']} q={cv['q']} curve_s={t_curve:.1f} "
      f"targets={len(insts)} unsat={nu} sat={ns} disagree={sum(not x['enum_agree'] for x in insts)} "
      f"eval_fail={sum(not x['eval_ok'] for x in insts)}", flush=True)
