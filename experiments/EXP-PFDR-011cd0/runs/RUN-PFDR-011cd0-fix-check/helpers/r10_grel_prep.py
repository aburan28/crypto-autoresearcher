"""Scratch-only view of R10 for G-REL: rows.jsonl.gz symlink + a merge-report whose harvest_rows_map
points to the scratch harvest rows of each job (R10 harvest rows are never archived)."""
import json, os, sys, hashlib
REPO = "/home/user/crypto-autoresearcher"
rd = os.path.join(REPO, sys.argv[1]); out = sys.argv[2]
os.makedirs(out)
os.symlink(os.path.join(rd, "rows.jsonl.gz"), os.path.join(out, "rows.jsonl.gz"))
mr = json.load(open(os.path.join(rd, "merge-report.json")))
idx = json.load(open(os.path.join(rd, "attempt-1", "jobs-index.json")))
by_job = {j["job"]: j.get("scratch_harvest_rows", {}).get("path") for j in idx["jobs"]}
hm = {}
for k, src in mr["per_key_source"].items():
    p = by_job.get(src["job"])
    hm[k] = {"harvest_rows_file": p, "sha256": hashlib.sha256(open(p, "rb").read()).hexdigest() if p else None}
json.dump({"harvest_rows_map": hm}, open(os.path.join(out, "merge-report.json"), "w"))
print(len(hm))
