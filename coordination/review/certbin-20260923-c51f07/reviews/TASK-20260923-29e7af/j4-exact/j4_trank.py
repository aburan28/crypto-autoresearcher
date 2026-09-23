#!/usr/bin/env python3
"""J4 step 2c (TASK-20260923-29e7af): (i) is the identical T_rank retention
across references explained by equal rank_4? Predict T_rank retention per
reference as the fraction of arm targets whose rank equals the reference rank,
from the per-target 'rank' and 'stratum' fields only (no match flag read).
(ii) T_strict prefix identity across references (references.json)."""
import gzip, json, os
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
HERE = os.path.dirname(os.path.abspath(__file__))
refs = json.load(open(os.path.join(RUN, "references.json")))["F-S3"]["references"]
T = []
with gzip.open(os.path.join(RUN, "targets-F-S3.jsonl.gz"), "rt") as f:
    for line in f:
        d = json.loads(line)
        if d["D"] == 4:
            T.append((d["idx"], d["stratum"], d["rank"]))
out = {"ref_rank_D4": {k: v["D4"]["rank"] for k, v in refs.items()}, "predicted_T_rank_retention": {}}
for lab, v in refs.items():
    rk = v["D4"]["rank"]
    pool = [t for t in T if t[1] != "degenerate" and (lab != "modal" or t[0] > 100)]
    ret = {}
    for arm in ("unsat", "sat"):
        a = [t for t in pool if t[1] == arm]
        ret[arm] = [sum(t[2] == rk for t in a), len(a), round(sum(t[2] == rk for t in a) / len(a), 4)]
    out["predicted_T_rank_retention"][lab] = ret
from collections import Counter
out["rank_distribution_by_arm"] = {arm: dict(Counter(t[2] for t in T if t[1] == arm)) for arm in ("unsat", "sat", "degenerate")}
labs = ["U1", "U2", "U3", "S1", "S2", "modal"]
pre = {}
for i, l1 in enumerate(labs):
    for l2 in labs[i + 1:]:
        a, b = refs[l1]["D4"]["T_strict"], refs[l2]["D4"]["T_strict"]
        n = 0
        for x, y in zip(a, b):
            if x == y: n += 1
            else: break
        pre[f"{l1}~{l2}"] = n
out["T_strict_prefix_identity_D4"] = pre
json.dump(out, open(os.path.join(HERE, "trank-D4.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
