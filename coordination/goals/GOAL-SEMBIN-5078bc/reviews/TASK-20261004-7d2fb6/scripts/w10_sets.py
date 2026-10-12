#!/usr/bin/env python3
"""w10_sets.py -- joint W10 (1)(2)(4): the exclusion list, the digest file and the tracked set of RUN-SEMBIN-9bb990.
 (1) excluded paths == digest paths minus tracked paths; hashes agree between the two files; tracked files hash to their digest; sizes sum to total_bytes; every listed file
     is > 1 MiB and every tracked file under an instances/ directory is <= 1 MiB; the digest file's own entry set.
 (2) every result record whose instance has a listed file: the f4 record's msolve_input_sha256 equals the listed sha256 of its .ms; list which records exist per listed instance;
     and records naming a system hash (system_sha256) -- after w10_regen has produced regenerated system hashes (w10_analyze.py) they are compared there.
 Read-only. Writes outputs/w10_sets.json."""
import json, os, subprocess, hashlib, glob, collections, sys
REPO = "/home/user/crypto-autoresearcher"; WS = os.environ["WS"]
RUN = f"{REPO}/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"; REL = "experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-9bb990"
tracked = [p[len(REL) + 1:] for p in subprocess.run(["git", "-C", REPO, "ls-files", REL], capture_output=True, text=True).stdout.split("\n") if p]
dig = json.load(open(f"{RUN}/artifact-digests.json"))
ex = json.load(open(f"{RUN}/excluded-large-instances.json"))
exp = {f["path"]: f for f in ex["files"]}
res = {"tracked": len(tracked), "digest_entries": len(dig), "excluded_entries": len(exp), "declared_count": ex["count"], "declared_total_bytes": ex["total_bytes"], "sum_listed_bytes": sum(f["bytes"] for f in ex["files"])}
res["digest_minus_tracked"] = sorted(set(dig) - set(tracked)); res["tracked_minus_digest"] = sorted(set(tracked) - set(dig))
res["excluded_equals_digest_minus_tracked"] = set(exp) == set(dig) - set(tracked)
res["tracked_minus_digest_is_only_the_digest_file"] = res["tracked_minus_digest"] == ["artifact-digests.json"]
res["listed_hash_equals_digest_hash"] = all(dig.get(p) == f["sha256"] for p, f in exp.items())
res["all_listed_over_1MiB"] = all(f["bytes"] > 1048576 for f in exp.values())
bad = []
big_tracked = []
for p in tracked:
    if p == "artifact-digests.json": continue
    full = f"{RUN}/{p}"
    h = hashlib.sha256(open(full, "rb").read()).hexdigest()
    if dig.get(p) != h: bad.append(p)
    if "/instances/" in p and os.path.getsize(full) > 1048576: big_tracked.append(p)
res["tracked_files_not_matching_digest"] = bad; res["tracked_instance_files_over_1MiB"] = big_tracked
# local presence of the listed files on this host (NOT part of the package; host-specific)
present = sum(os.path.exists(f"{RUN}/{p}") for p in exp)
res["listed_files_present_on_this_host"] = present
mismatch_local = []
if present:
    for p, f in exp.items():
        fp = f"{RUN}/{p}"
        if os.path.exists(fp):
            h = hashlib.sha256(open(fp, "rb").read()).hexdigest()
            if h != f["sha256"]: mismatch_local.append(p)
res["local_copies_not_matching_listed_sha256"] = mismatch_local
# instances: pair up .ms/.json per instance, and check which records exist
by_inst = collections.defaultdict(dict)
for p, f in exp.items():
    base = os.path.basename(p); iid, ext = base.rsplit(".", 1); by_inst[iid][ext] = f
recs = [json.loads(l) for l in open(f"{RUN}/light_controls/cells/results.jsonl") if l.strip()]
res["listed_instances"] = len(by_inst); res["instances_with_both_ms_and_json"] = sum(1 for v in by_inst.values() if len(v) == 2)
rows = []
for iid, v in sorted(by_inst.items()):
    rs = [r for r in recs if r["instance_id"] == iid]
    f4 = next((r for r in rs if r["instrument"] == "f4_trace_msolve"), None)
    row = {"instance_id": iid, "files_listed": sorted(v), "instruments_in_records": sorted(r["instrument"] for r in rs), "system_sha256_in_records": sorted({r["system_sha256"] for r in rs})}
    if f4 and "ms" in v: row["f4_msolve_input_sha256_equals_listed_ms"] = (f4.get("msolve_input_sha256") == v["ms"]["sha256"])
    rows.append(row)
res["per_instance"] = rows
res["f4_input_hash_equals_listed_ms_all"] = all(r.get("f4_msolve_input_sha256_equals_listed_ms", True) for r in rows)
res["instances_with_a_listed_ms_but_no_f4_record"] = [r["instance_id"] for r in rows if "ms" in r["files_listed"] and "f4_msolve_input_sha256_equals_listed_ms" not in r]
res["instrument_set_over_listed_instances"] = dict(collections.Counter(i for r in rows for i in r["instruments_in_records"]))
json.dump(res, open(f"{WS}/outputs/w10_sets.json", "w"), indent=1)
for k, v in res.items():
    if k != "per_instance": print(k, ":", v if not isinstance(v, list) or len(v) < 6 else f"{len(v)} items {v[:3]}...")
