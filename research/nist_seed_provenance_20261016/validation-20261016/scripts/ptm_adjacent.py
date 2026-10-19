#!/usr/bin/env python3
"""Proves-too-much, adjacent blocks: for each published prime seed (block i of run t, from
out/q1_seeds.json), take block i-1 and i+1 of srand48(t) and block i of srand48(t-1) and
srand48(t+1); each must differ from the seed AND must fail c * b_pub^2 == -27 (mod p).
Also checks the 0-based reading of the recorded orders' i column against my 1-based set.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

P = load_params()
q1 = json.load(open(os.path.join(ROOT, "out", "q1_seeds.json")))
out = {"adjacent": [], "index_base": {}}
for name in PRIME_CURVES:
    h = q1["seeds"][name]["hits"][0]
    t, i0 = h["t"], h["block0"]
    p, b = P[name]["p"], P[name]["b"]
    for label, tt, blk in (("prev_block", t, i0 - 1), ("next_block", t, i0 + 1),
                           ("t_minus_1", t - 1, i0), ("t_plus_1", t + 1, i0)):
        s = drand48_byte_stream(tt, 20 * (blk + 1))[20 * blk:]
        c = x962_c(s, p.bit_length())
        out["adjacent"].append({"curve": name, "object": label, "equals_seed": s == P[name]["seed_bytes"],
                                "x962_holds_with_published_b": (c * b * b + 27) % p == 0})
for t, field, count in RUNS:
    mine1 = set(int(x) for x in open(os.path.join(ROOT, "out", f"q4_candidates_{t}.txt")))
    rec = set(int(l.split()[0]) for l in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt")))
    mine0 = set(i - 1 for i in mine1)
    out["index_base"][str(t)] = {"recorded_vs_my_1based_equal": rec == mine1,
                                 "recorded_vs_my_0based_overlap": len(rec & mine0), "n": len(rec)}
with open(os.path.join(ROOT, "out", "ptm_adjacent.json"), "w") as f:
    json.dump(out, f, indent=1, sort_keys=True)
bad = [a for a in out["adjacent"] if a["equals_seed"] or a["x962_holds_with_published_b"]]
print("adjacent objects:", len(out["adjacent"]), "succeeding (must be 0):", len(bad), bad)
print("index base:", out["index_base"])
