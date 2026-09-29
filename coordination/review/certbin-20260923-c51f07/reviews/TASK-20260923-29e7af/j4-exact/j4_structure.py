#!/usr/bin/env python3
"""J4 step 2b (TASK-20260923-29e7af): positions of the rank-increasing pivots
(IND / DEP_TAU) per reference, their survivor counts on F-S3 and F-RANDX
targets (recomputed from my forms and archived x_R only), and op-log prefix
identity across references. No hazard file is read."""
import gzip, json, os
from collections import defaultdict
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/home/user/crypto-autoresearcher/experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"
import importlib.util
spec = importlib.util.spec_from_file_location("jp", os.path.join(HERE, "j4_predict.py"))
jp = importlib.util.module_from_spec(spec); spec.loader.exec_module(jp)
forms = json.load(open(os.path.join(HERE, "forms-D4.json")))["refs"]
fams = {f: jp.targets(f) for f in ("F-S3", "F-RANDX")}
ops = defaultdict(list)
with gzip.open(os.path.join(RUN, "F-S3-reference-oplogs-D4.jsonl.gz"), "rt") as f:
    for line in f:
        d = json.loads(line); ops[d["ref"]].append((d["k"], d["p"], d["c"], tuple(d["X"])))
for v in ops.values(): v.sort()
out = {"rank_increasing_positions": {}, "oplog_prefix_identity": {}}
labs = ["U1", "U2", "U3", "S1", "S2", "modal"]
for lab in labs:
    F = forms[lab]; a0 = np.array(F["a0"], dtype=np.uint8); a = np.array(F["a"], dtype=np.int64)
    cls, rl, rm = jp.classify(a)
    pos = [k for k, c in enumerate(cls) if c in ("IND", "DEP_TAU")]
    row = []
    for fam in ("F-S3", "F-RANDX"):
        rs = [x for i, x, dg in fams[fam] if not dg and (lab != "modal" or fam != "F-S3" or i > 100)]
        Sk, zk, dep, full = jp.hazard(jp.evalf(a0, a, rs))
        row.append({int(k): [int(Sk[k]), int(zk[k])] for k in pos})
    out["rank_increasing_positions"][lab] = [
        {"k": k, "class": cls[k], "a_hex": hex(int(a[k])), "F-S3 [S_k, zeros]": row[0][k], "F-RANDX [S_k, zeros]": row[1][k]}
        for k in pos]
    tau_k = [k for k in range(len(a)) if int(a[k]) == 1]
    out["rank_increasing_positions"][lab + "_pivots_with_a_k_equal_tau"] = tau_k
for i, l1 in enumerate(labs):
    for l2 in labs[i + 1:]:
        n = 0
        for x, y in zip(ops[l1], ops[l2]):
            if x[1:] == y[1:]: n += 1
            else: break
        out["oplog_prefix_identity"][f"{l1}~{l2}"] = n
json.dump(out, open(os.path.join(HERE, "structure-D4.json"), "w"), indent=1)
for lab in labs:
    print(lab, [(r["k"], r["class"], r["F-S3 [S_k, zeros]"], r["F-RANDX [S_k, zeros]"]) for r in out["rank_increasing_positions"][lab]])
    print("   a_k == tau at k:", out["rank_increasing_positions"][lab + "_pivots_with_a_k_equal_tau"])
print(out["oplog_prefix_identity"])
