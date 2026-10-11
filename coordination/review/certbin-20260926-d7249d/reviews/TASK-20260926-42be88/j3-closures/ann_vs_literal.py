"""J3: bit-level check of the ann-v1 extractor output against the validator's OWN literal W_4.
For each chosen system of the archived ann set: decode L_hex with the coordinate order rebuilt from the
text ("all multilinear monomials of degree <= 4 in v_0..v_19 sorted by (-degree, bitmask ascending)",
bit c LSB-first = value on the c-th monomial); check that every functional vanishes on every basis
element of MY literal W_4, that rank(L) = 6196 - dim(my W_4) (so S = {g : L(g) = 0} equals my W_4
exactly), and that some functional has lambda(1) = 1.
usage: python3 ann_vs_literal.py <snapshot_root> KEY[,KEY...]
"""
import gzip
import json
import os
import sys
from itertools import combinations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "j2-population"))
import gf219 as G  # noqa: E402
from literal_w4 import Lit, eqs_from_E  # noqa: E402

ROOT = sys.argv[1]
KEYS = sys.argv[2].split(",")
RUN = os.path.join(ROOT, "experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60")
inst = {r["key"]: r for r in (json.loads(l) for l in gzip.open(os.path.join(RUN, "instances.jsonl.gz"), "rt"))}
anns = {}
for l in gzip.open(os.path.join(RUN, "annihilators.jsonl.gz"), "rt"):
    r = json.loads(l)
    if r["key"] in KEYS:
        anns[r["key"]] = r
ORDER = sorted([sum(1 << i for i in c) for d in range(5) for c in combinations(range(20), d)],
               key=lambda m: (-bin(m).count("1"), m))
C = len(ORDER)
L = Lit(20, 4)
# map my Lit positions -> ann coordinate index
ann_index = {m: c for c, m in enumerate(ORDER)}
perm = np.array([ann_index[m] for m in L.mons], dtype=np.int64)  # perm[mypos] = ann coordinate
out = []
for key in KEYS:
    r = inst[key]
    eqs = eqs_from_E(G.hex_to_E(r["E_hex"]))
    _, rec, _, piv = L.w_closure(eqs)
    body = anns[key]["body"]
    assert body["D"] == 4 and body["nv"] == 20 and body["neq"] == 19
    Lint = [int(h, 16) for h in body["L_hex"]]
    # functionals as ints over ann coordinates; my W_4 basis re-expressed in ann coordinates
    W = []
    for x in piv.values():
        pos = L.bits_of(x)
        y = 0
        for p in pos:
            y |= 1 << int(perm[p])
        W.append(y)
    bad = 0
    for lam in Lint:
        for w in W:
            if bin(lam & w).count("1") & 1:
                bad += 1
                break
    # rank of L
    pv = {}
    for lam in Lint:
        x = lam
        while x:
            h = x.bit_length() - 1
            if h in pv:
                x ^= pv[h]
            else:
                pv[h] = x
                break
    rankL = len(pv)
    const_c = ann_index[0]
    a3 = any((lam >> const_c) & 1 for lam in Lint)
    out.append({"key": key, "my_W4_dim": rec["final_dim"], "my_W4_one": rec["one"], "n_functionals": len(Lint),
                "rank_L": rankL, "codim_my_W4": C - rec["final_dim"],
                "functionals_not_vanishing_on_my_W4": bad,
                "S_equals_my_W4": bad == 0 and rankL == C - rec["final_dim"],
                "A3_some_lambda(1)=1": a3})
    print(out[-1], flush=True)
res = {"coordinate_order": "(-degree, bitmask ascending), rebuilt from the specification text", "results": out,
       "all_ok": all(o["S_equals_my_W4"] and o["A3_some_lambda(1)=1"] for o in out)}
json.dump(res, open(os.path.join(HERE, "ann-vs-literal.json"), "w"), indent=1)
print("ALL_OK", res["all_ok"])
