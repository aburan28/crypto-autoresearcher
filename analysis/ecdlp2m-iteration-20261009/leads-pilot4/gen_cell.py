#!/usr/bin/env python3
"""gen_cell.py <src cell> <m> <out name>: same curve, field, basis V and target list (z values) as
<src cell>, chained S_3 at arity m. Labels and Boolean solution masks by explicit chain enumeration
with closed-form quadratic roots (zfree_fast.make); every solution mask is checked against the
descended Boolean system of pilot3.build_chain (each equation must vanish)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE / "vendor"))
import pilot3
from zfree_fast import make
src, m, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
cell = json.load(open(HERE / "instances" / f"{src}.json"))
n, k = cell["n"], cell["k"]; mul, roots = make(n, cell["modulus"]); b = cell["b"]; basis = cell["basis"]
V = []
for c in range(1 << k):
    v = 0
    for i in range(k):
        if c >> i & 1: v ^= basis[i]
    V.append((v, c))
def R(x, y):
    s = x ^ y; p = mul(x, y)
    r = roots(mul(s, s), p, mul(p, p) ^ b)
    assert r is not None
    return r
# partial chains: list of (u_last, [u_0..u_last], [c_0..c_{j}])
parts = []
for x0, c0 in V:
    for x1, c1 in V:
        for u in R(x0, x1): parts.append((u, [u], [c0, c1]))
for i in range(1, m - 2):
    nxt = []
    for u, us, cs in parts:
        for x, c in V:
            for u2 in R(u, x): nxt.append((u2, us + [u2], cs + [c]))
    parts = nxt
byu = {}
for u, us, cs in parts: byu.setdefault(u, []).append((us, cs))
N = (m - 2) * n + m * k
def mask(us, cs):
    mm = 0
    for i, u in enumerate(us): mm |= u << (i * n)
    for i, c in enumerate(cs): mm |= c << ((m - 2) * n + i * k)
    return mm
insts = []; seen = set()
for s0 in cell["instances"]:
    z = s0["z"]; dup = z in seen; seen.add(z)
    sols = []
    for u, lst in byu.items():
        for x, c in V:
            if u in R(x, z):
                for us, cs in lst: sols.append(mask(us, cs + [c]))
    sysm = pilot3.build_chain(n, k, m, basis, b, z, cell["modulus"])
    for w in sols[:64]:
        for e in sysm["equations"]:
            assert sum(1 for mm in e if mm & w == mm) % 2 == 0, "solution does not satisfy the Boolean system"
    insts.append({"id": f"m{m}-n{n}k{k}-S3-{len(insts):04d}", "family": "S3", "m": m, "n": n, "k": k, "N": N, "z": z,
                  "dup_target": dup, "nsol": len(sols), "solutions": sols[:64], "label_source": "chain enumeration (gen_cell.py)"})
outc = {kk: cell[kk] for kk in cell if kk != "instances"}; outc["m"] = m; outc["instances"] = insts
outc["derived_from"] = src
json.dump(outc, open(HERE / "instances" / f"{out}.json", "w"))
U = sum(1 for x in insts if x["nsol"] == 0 and not x["dup_target"]); S = sum(1 for x in insts if x["nsol"] > 0 and not x["dup_target"])
print(out, "m", m, "N", N, "zfree", len(parts) * len(V), "UNSAT", U, "SAT", S)
