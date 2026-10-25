#!/usr/bin/env python3
"""plan vs plan-aa: same method_id and same algorithm_seed per (workload, round) -> a deterministic
pipeline must give identical answers and operation counts. Compares cost.total_gae, phases (minus wall),
counters, field_ops, factor_base, recovered. (SHF-20261021-477d51 receipts reader)"""
import json, sys
from collections import OrderedDict
B = sys.argv[1]
out = OrderedDict()
def strip(r):
    ph = [{k: v for k, v in p.items() if "wall" not in k and k != "native"} for p in r.get("phases") or []]
    return (r["outcome"]["recovered"], r["cost"]["total_gae"], json.dumps(ph, sort_keys=True), json.dumps(r.get("counters"), sort_keys=True),
            json.dumps(r.get("field_ops"), sort_keys=True), json.dumps(r.get("factor_base"), sort_keys=True))
for s in ["c24", "c28", "c30", "r24", "r26", "r28"]:
    by = {}
    for l in open(f"{B}/sessions/{s}/records.jsonl"):
        r = json.loads(l)
        by[(r["arm"], r["workload"]["workload_id"], r["round"])] = r
    pairs = [(k, by[("plan-aa",) + k[1:]]) for k in by if k[0] == "plan"]
    same_mid = all(by[k]["method"]["method_id"] == aa["method"]["method_id"] for k, aa in pairs)
    same_seed = all(by[k]["algorithm_seed"] == aa["algorithm_seed"] for k, aa in pairs)
    ident = sum(strip(by[k]) == strip(aa) for k, aa in pairs)
    out[s] = OrderedDict(pairs=len(pairs), same_method_id=same_mid, same_seed=same_seed, identical_counts=ident)
    print(s, dict(out[s]))
json.dump(out, open(sys.argv[2], "w"), indent=1)
