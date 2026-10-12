#!/usr/bin/env python3
"""POST-REVEAL K1b: K1 split by model; ENUM rows re-mapped to the statement's s = 1."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import blind_rederive as B, mpmath as mp
RAW = os.path.join(HERE, "../../../../../experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-be48b7/raw-result.json")
rows = json.load(open(RAW))["argmin_rows"]
res = {}
for model in ("MITM", "MITM_CAPPED", "ENUM"):
    for remap in ((False, True) if model == "ENUM" else (False,)):
        key = model + ("_as_s1" if remap else "")
        mx = {"PROBE": 0.0, "TOTAL": 0.0, "FILL": 0.0}; cnt = 0; s_seen = set()
        for r in rows:
            if r["model"] != model: continue
            s = 1 if remap else r["s"]; s_seen.add(r["s"])
            c = B.components(r["n"], r["m"], s, mp.mpf(r["d"]))
            cnt += 1
            mx["PROBE"] = max(mx["PROBE"], abs(float(c["probe"]) - r["PROBE"]))
            mx["FILL"] = max(mx["FILL"], abs(float(c["fill"]) - r["FILL"]))
            mx["TOTAL"] = max(mx["TOTAL"], abs(float(B.total(r["n"], r["m"], s, mp.mpf(r["d"]))) - r["TOTAL"]))
        res[key] = {"rows": cnt, "producer_s_values": sorted(s_seen), "max_abs_diff": mx}
print(json.dumps(res, indent=1))
