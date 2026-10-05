#!/usr/bin/env python3
"""w10_analyze.py -- joint W10 (2)(3): join the regeneration results (all 92 listed files) with the lane records of RUN-SEMBIN-9bb990/light_controls:
for every listed file, the record(s) naming that instance carry a system_sha256; compare it with the system hash of the REGENERATED system, and for .ms files compare the f4 record's
msolve_input_sha256 with the listed sha256. Read-only."""
import json, glob, os, collections
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"
regen = [json.load(open(p)) for p in glob.glob(f"{WS}/outputs/w10_regen_*.json") if os.path.getsize(p) > 20000]
rows = [r for rg in regen for r in rg]
byidx = {}
for r in rows: byidx[r["path"]] = r
recs = [json.loads(l) for l in open(f"{RUN}/light_controls/cells/results.jsonl") if l.strip()]
sysh = collections.defaultdict(set); msh = {}
for r in recs:
    sysh[r["instance_id"]].add(r["system_sha256"])
    if r["instrument"] == "f4_trace_msolve": msh[r["instance_id"]] = r.get("msolve_input_sha256")
out = {"files_regenerated": len(byidx), "sha256_equal": sum(r["sha256_equal"] for r in byidx.values()), "bytes_equal": sum(r["bytes_equal"] for r in byidx.values())}
bad_sys, bad_ms = [], []
for p, r in byidx.items():
    iid = os.path.basename(p).rsplit(".", 1)[0]
    if sysh[iid] != {r["system_sha256_regenerated"]}: bad_sys.append((p, sorted(sysh[iid]), r["system_sha256_regenerated"]))
    if p.endswith(".ms") and msh.get(iid) != r["listed_sha256"]: bad_ms.append((p, msh.get(iid), r["listed_sha256"]))
out["records_system_sha256_differs_from_regenerated_system"] = bad_sys; out["f4_msolve_input_sha256_differs_from_listed_ms"] = bad_ms
out["distinct_instances_covered"] = len({os.path.basename(p).rsplit('.', 1)[0] for p in byidx})
out["max_regen_seconds"] = max(r["seconds"] for r in byidx.values()); out["sum_regen_seconds"] = round(sum(r["seconds"] for r in byidx.values()))
json.dump(out, open(f"{WS}/outputs/w10_analysis.json", "w"), indent=1)
print(json.dumps(out, indent=1))
