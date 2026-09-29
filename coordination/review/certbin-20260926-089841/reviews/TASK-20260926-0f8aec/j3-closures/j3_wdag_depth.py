#!/usr/bin/env python3
"""TASK-20260926-0f8aec J3: structural check of EVERY wdag-v1 line (no algebra;
algebraic validity is J1's): DAG depth == archived W_4 one_first_iteration
(C-WDAG "depth used"); depth-0 wdags are one node with no prods; exactly one
wdag-v1 per W_4-refuted system and none elsewhere. Plus one algebraic check of
an iteration-0 (M_4) wdag, N-CONV:0:unsat, with own arithmetic. Reports
violation counts only. Imports nothing from impl/, verifier/, src/."""
import gzip, json, sys
from itertools import combinations
from pathlib import Path
RUN = Path(sys.argv[1]) / "experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e"
MONOS2 = [()] + [(i,) for i in range(18)] + list(combinations(range(18), 2))
w4 = {}
for l in gzip.open(RUN / "closures.jsonl.gz", "rt"):
    r = json.loads(l)
    if r["closure"] == "W_4":
        w4[r["key"]] = r
V = {}
def bad(k, x): V.setdefault(k, []).append(x)
seen = {}
for l in gzip.open(RUN / "certificates.jsonl.gz", "rt"):
    c = json.loads(l)
    if c["format"] != "wdag-v1":
        continue
    seen[c["key"]] = seen.get(c["key"], 0) + 1
    b = c["body"]; lv = {}
    for n in sorted(b["nodes"], key=lambda n: n["id"]):
        lv[n["id"]] = max([lv[ch] + 1 for _, ch in n["prods"]], default=0)
    d = lv[b["output"]]
    rec = w4.get(c["key"])
    if rec is None or not rec["one"]:
        bad("wdag on a system not W_4-refuted", c["key"])
    elif d != rec["one_first_iteration"]:
        bad("wdag depth != W_4 one_first_iteration", c["key"])
    if d == 0 and (len(b["nodes"]) != 1 or b["nodes"][0]["prods"]):
        bad("depth-0 wdag not a single flat node", c["key"])
    if c.get("node_count") != len(b["nodes"]):
        bad("node_count field", c["key"])
for k, r in w4.items():
    if r["one"] and seen.get(k, 0) != 1:
        bad("W_4-refuted system without exactly one wdag-v1 (UNCERTIFIED)", k)
# algebraic check of one iteration-0 wdag
inst = {json.loads(l)["key"]: json.loads(l) for l in gzip.open(RUN / "instances.jsonl.gz", "rt")}
K = "N-CONV:0:unsat"
eqs = []
for h in inst[K]["E_hex"]:
    r = int(h, 16); f = set()
    for col, m in enumerate(MONOS2):
        if (r >> col) & 1:
            f ^= {sum(1 << i for i in m)}
    eqs.append(f)
alg = None
for l in gzip.open(RUN / "certificates.jsonl.gz", "rt"):
    c = json.loads(l)
    if c["key"] == K and c["format"] == "wdag-v1":
        n = c["body"]["nodes"][0]; acc = set()
        for mu, k in n["rows"]:
            mk = sum(1 << i for i in mu)
            for m in eqs[k]:
                acc ^= {mk | m}
        alg = {"key": K, "nodes": len(c["body"]["nodes"]), "prods": n["prods"], "rows": len(n["rows"]),
               "max_mu": max(len(mu) for mu, _ in n["rows"]), "sums_to_1": acc == {0},
               "archived_one_first_iteration": w4[K]["one_first_iteration"]}
out = {"wdag_lines": sum(seen.values()), "violations": {k: {"count": len(v), "examples": v[:5]} for k, v in V.items()},
       "iteration0_algebraic_check": alg}
json.dump(out, open(Path(__file__).resolve().parent / "j3-wdag-depth.json", "w"), indent=1)
print(json.dumps(out))
