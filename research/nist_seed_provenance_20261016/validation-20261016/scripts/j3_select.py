#!/usr/bin/env python3
"""J3 row selection, exactly as frozen on TASK-20261016-9bf74b.

nonce = SHA-256(ASCII of the 40-hex freeze-commit SHA)
named rows: all accepted, all bitlen rejects, all twist-only rows (my J5 classification)
per run, among rows outside the named ones: key(row) = SHA-256(nonce_hex + ":" + t + ":" + i)
(t and i in decimal, i = the recorded 1-based block index; keys compared as 256-bit
integers), take the 34 smallest. If fewer than 5 of the run's selection have N0 = 0, add
that run's smallest-key N0 = 0 rows (outside the selection) until there are 5; same for Nt = 0.
Writes out/j3_sample.json and tmp/j3_rows.txt.
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *

FREEZE = "dbd1b8d15845579aaaa3af47b827955e2b625e77"
NONCE = hashlib.sha256(FREEZE.encode("ascii")).hexdigest()
assert NONCE == "702c36f2b6afb1a50f1b561a7e6583df966d4a3e02dc4b0d90618421f8176f92"
cls = json.load(open(os.path.join(ROOT, "out", "j5_classification.json")))
res = {"freeze_commit": FREEZE, "nonce": NONCE, "runs": {}}
lines = []
for t, field, count in RUNS:
    r = cls["runs"][str(t)]
    named = set(r["accepted_idx"]) | set(r["bitlen_idx"]) | set(r["twist_only_idx"])
    rows = {}
    for line in open(os.path.join(BUNDLE, "census", f"orders_{t}.txt")):
        i, n0, nt = map(int, line.split())
        rows[i] = (n0, nt)
    def key(i):
        return int(hashlib.sha256(f"{NONCE}:{t}:{i}".encode()).hexdigest(), 16)
    rest = sorted((i for i in rows if i not in named), key=key)
    sel = rest[:34]
    added = {"N0": [], "Nt": []}
    for col, idx in (("N0", 0), ("Nt", 1)):
        have = sum(1 for i in sel if rows[i][idx] == 0)
        for i in rest[34:]:
            if have >= 5:
                break
            if rows[i][idx] == 0 and i not in sel:
                sel.append(i); added[col].append(i); have += 1
    counts = {"N0_zero": sum(1 for i in sel if rows[i][0] == 0),
              "N0_nonzero": sum(1 for i in sel if rows[i][0] != 0),
              "Nt_zero": sum(1 for i in sel if rows[i][1] == 0),
              "Nt_nonzero": sum(1 for i in sel if rows[i][1] != 0)}
    res["runs"][str(t)] = {"field": field, "named": sorted(named), "n_named": len(named),
                           "n_outside_named": len(rest), "sample": sel, "augmented": added,
                           "sample_counts": counts,
                           "sample_keys_hex": {str(i): "%064x" % key(i) for i in sel}}
    for i in sorted(named) + sel:
        lines.append(f"{t} {i}")
os.makedirs(os.path.join(ROOT, "tmp"), exist_ok=True)
with open(os.path.join(ROOT, "tmp", "j3_rows.txt"), "w") as f:
    f.write("\n".join(lines) + "\n")
with open(os.path.join(ROOT, "out", "j3_sample.json"), "w") as f:
    json.dump(res, f, indent=1, sort_keys=True)
tot_named = sum(v["n_named"] for v in res["runs"].values())
tot_sample = sum(len(v["sample"]) for v in res["runs"].values())
print("nonce", NONCE, "named", tot_named, "sampled", tot_sample, "total rows", len(lines),
      "outside named", sum(v["n_outside_named"] for v in res["runs"].values()))
for t, v in res["runs"].items():
    print(t, v["field"], "named", v["n_named"], "sample", len(v["sample"]), "augmented", v["augmented"],
          "counts", v["sample_counts"])
    print("   sample rows:", v["sample"])
