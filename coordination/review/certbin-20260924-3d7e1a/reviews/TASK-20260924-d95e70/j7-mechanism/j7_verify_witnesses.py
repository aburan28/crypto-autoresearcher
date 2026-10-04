#!/usr/bin/env python3
"""Standalone re-verification of the structured W^(1) witnesses
(w1-witnesses.jsonl.gz) against a SECOND construction of f_0..f_16: the run's
archived E_hex in instance-sets.json, decoded with my own decoder of the
documented 17 x 172 convention. Checks, per witness:
  (i)   sum_k c_k f_k is of degree <= 1 (so it is a row combination of M_2 <= M_4);
  (ii)  every (mu, k) in C_4 has deg mu <= 2 (an M_4 row);
  (iii) deg a <= 3;
  (iv)  sum_{C_4} mu f_k + (sum_k c_k f_k) * a = 1 exactly in B.
By the argument in j7a-derivation-verdict.yaml these four facts imply 1 in W^(1)
<= W_4, with no reference to the closure engine."""
import gzip
import json
import os
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0"
EQ = []
for d in range(3):
    EQ.extend(sum(1 << i for i in c) for c in combinations(range(18), d))


def dec(hexes):
    return [[EQ[j] for j in range(172) if (int(h, 16) >> j) & 1] for h in hexes]


def pc(m):
    return bin(m).count("1")


iset = json.load(open(os.path.join(RUN, "instance-sets.json")))["sets"]
E = {(s, i["idx"]): dec(i["E_hex"]) for s in ("U62", "C20") for i in iset[s]}
res = []
for line in gzip.open(os.path.join(HERE, "w1-witnesses.jsonl.gz"), "rt"):
    w = json.loads(line)
    fs = E[(w["set"], w["idx"])]
    ell = {}
    for k in range(17):
        if w["c"][k]:
            for m in fs[k]:
                ell[m] = ell.get(m, 0) ^ 1
    ell = [m for m, p in ell.items() if p]
    ok_i = max((pc(m) for m in ell), default=0) <= 1
    ok_ii = all(pc(mu) <= 2 for mu, k in w["C4"])
    ok_iii = max((pc(m) for m in w["a"]), default=0) <= 3
    acc = {}
    for mu, k in w["C4"]:
        for m in fs[k]:
            x = mu | m
            acc[x] = acc.get(x, 0) ^ 1
    for m1 in ell:
        for m2 in w["a"]:
            x = m1 | m2
            acc[x] = acc.get(x, 0) ^ 1
    total = sorted(x for x, p in acc.items() if p)
    ok_iv = total == [0]
    res.append({"set": w["set"], "idx": w["idx"], "linear_ell": ok_i, "C4_deg_le2": ok_ii, "deg_a_le3": ok_iii,
                "identity_is_1": ok_iv, "size_C4": len(w["C4"]), "terms_a": len(w["a"]),
                "ell_support": sorted(ell), "all_ok": ok_i and ok_ii and ok_iii and ok_iv})
summ = {"witnesses": len(res), "all_ok": sum(r["all_ok"] for r in res),
        "by_set": {s: sum(1 for r in res if r["set"] == s and r["all_ok"]) for s in ("U62", "C20")},
        "size_C4_range": [min(r["size_C4"] for r in res), max(r["size_C4"] for r in res)],
        "terms_a_range": [min(r["terms_a"] for r in res), max(r["terms_a"] for r in res)]}
json.dump({"summary": summ, "rows": res}, open(os.path.join(HERE, "w1-witness-reverification.json"), "w"), indent=1)
print(json.dumps(summ, indent=1))
