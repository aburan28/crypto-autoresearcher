#!/usr/bin/env python3
"""N3(6) corrected: manifest.yaml's `artifacts` block is a MAPPING
filename -> {sha256, bytes}, which own_n3.py's first version mis-parsed as a
list (it therefore reported 0 matches; that was my bug, not the run's).  Also:
categorise every numeric difference between the two driver executions, and
check what the RENAMED keys' values were, since a renamed control flag can
change a control OUTCOME and not only a label."""
import hashlib
import json
import os

import yaml

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
RECEIPT = ("/workspace/coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/"
           "archives/TASK-20260913-a10007/snapshot-receipt.json")
out = {}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


man = yaml.safe_load(open(RUN + "manifest.yaml"))["run"]   # everything sits under `run:`
arts = man["artifacts"]
assert isinstance(arts, dict), type(arts)
on_disk = {f: sha(RUN + f) for f in sorted(os.listdir(RUN)) if os.path.isfile(RUN + f)}
rows = []
for f, rec in sorted(arts.items()):
    d = on_disk.get(f)
    rows.append(dict(file=f, manifest_sha256=rec["sha256"], on_disk_sha256=d,
                     match=(rec["sha256"] == d),
                     manifest_bytes=rec["bytes"],
                     on_disk_bytes=os.path.getsize(RUN + f) if d else None,
                     bytes_match=(d is not None and rec["bytes"] == os.path.getsize(RUN + f))))
out["manifest_vs_disk"] = rows
out["manifest_artifacts_listed"] = len(arts)
out["run_dir_files"] = len(on_disk)
out["manifest_all_match"] = all(r["match"] for r in rows)
out["manifest_all_bytes_match"] = all(r["bytes_match"] for r in rows)
out["in_run_dir_not_in_manifest"] = [f for f in on_disk if f not in arts]
out["in_manifest_not_on_disk"] = [f for f in arts if f not in on_disk]
print(f"(6a) manifest lists {len(arts)} artifacts, run dir has {len(on_disk)} files")
print(f"     sha256 matches: {sum(r['match'] for r in rows)}/{len(rows)}; "
      f"byte-count matches: {sum(r['bytes_match'] for r in rows)}/{len(rows)}")
print(f"     in run dir but not in manifest: {out['in_run_dir_not_in_manifest']}")
print(f"     in manifest but not on disk:    {out['in_manifest_not_on_disk']}")

rc = json.load(open(RECEIPT))
rec_rows = [dict(path=p, receipt=h, on_disk=sha("/workspace/" + p), match=(h == sha("/workspace/" + p)))
            for p, h in rc["path_sha256"].items()]
out["receipt_vs_disk"] = dict(paths=len(rec_rows), all_match=all(r["match"] for r in rec_rows),
                              mismatches=[r["path"] for r in rec_rows if not r["match"]],
                              code_paths=sum(1 for r in rec_rows if "/code/" in r["path"]),
                              run_paths=sum(1 for r in rec_rows if "/runs/" in r["path"]))
# cross: does the manifest's own hash of each file agree with the receipt's?
cross = []
for p, h in rc["path_sha256"].items():
    b = os.path.basename(p)
    if b in arts and "/runs/" in p:
        cross.append((b, arts[b]["sha256"] == h))
out["manifest_and_receipt_agree_on"] = dict(files=len(cross), all_agree=all(v for _, v in cross),
                                            disagreements=[b for b, v in cross if not v])
out["declared_source_artifacts_present"] = {
    p: (os.path.exists("/workspace/" + p) and p in rc["path_sha256"])
    for p in rc["declared_source_artifacts"]}
print(f"(6b) snapshot receipt: {len(rec_rows)} paths ({out['receipt_vs_disk']['code_paths']} code, "
      f"{out['receipt_vs_disk']['run_paths']} run); all match on disk: {out['receipt_vs_disk']['all_match']}")
print(f"     manifest and receipt agree on {len(cross)} shared run files: "
      f"{out['manifest_and_receipt_agree_on']['all_agree']}")
print(f"     all 10 declared_source_artifacts present and hashed: "
      f"{all(out['declared_source_artifacts_present'].values())}")

# ---- manifest completeness against the artifact policy ----------------------
policy = {
    "exact command": man.get("code", {}).get("command"),
    "git commit": man.get("code", {}).get("commit"),
    "dirty-tree state": man.get("code", {}).get("dirty"),
    "environment": bool(man.get("environment")),
    "dependency versions": man.get("environment", {}).get("dependencies"),
    "seeds": man.get("inputs", {}).get("seed"),
    "seed formula": man.get("inputs", {}).get("seed_formula"),
    "requested policy": man.get("inference", {}).get("requested_policy"),
    "resolved model id": man.get("inference", {}).get("resolved_model_id"),
    "model_verified": man.get("inference", {}).get("model_verified"),
    "fallback_used": man.get("inference", {}).get("fallback_used"),
    "reasoning effort": man.get("inference", {}).get("reasoning_effort"),
    "stdout present": os.path.getsize(RUN + "stdout.log"),
    "stderr present (0 bytes ok)": os.path.getsize(RUN + "stderr.log"),
    "validity status": man.get("result", {}).get("valid"),
    "invalid_reason": man.get("result", {}).get("invalid_reason"),
    "timestamps": [man.get("timing", {}).get("started_at"), man.get("timing", {}).get("finished_at")],
    "resources": man.get("resources"),
    "status": man.get("status"),
}
out["artifact_policy_fields"] = policy
print("\n(6c) artifact-policy fields in manifest.yaml:")
for k, v in policy.items():
    print(f"     {k:<30} {str(v)[:110]}")

# ---- (6d) driver-execution differences, categorised -------------------------
def walk(a, b, path, nums, strs, struct):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in a or k not in b:
                only = "exec-2" if k in a else "exec-1"
                struct.append((path + "/" + str(k), only, a.get(k) if k in a else b.get(k)))
            else:
                walk(a[k], b[k], path + "/" + str(k), nums, strs, struct)
    elif isinstance(a, list) and isinstance(b, list):
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", nums, strs, struct)
    elif isinstance(a, bool) or isinstance(b, bool):
        if a != b:
            nums.append((path, a, b))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if a != b:
            nums.append((path, a, b))
    elif isinstance(a, str) and isinstance(b, str):
        if a != b:
            strs.append((path, a, b))


a = json.load(open(RUN + "raw-result.json"))
b = json.load(open(RUN + "raw-result.driver-exec-1.json"))
nums, strs, struct = [], [], []
walk(a, b, "", nums, strs, struct)
timing = [x for x in nums if x[0].endswith("wall_seconds") or "wall_seconds" in x[0]
          or x[0].endswith("cpu_seconds") or x[0].endswith("started_at")]
non_timing = [x for x in nums if x not in timing]
out["driver_diff_raw_result"] = dict(
    numeric_or_boolean_differences=len(nums),
    all_are_wall_clock=len(non_timing) == 0,
    non_timing_differences=non_timing,
    timing_difference_paths=sorted({x[0].rsplit("[", 1)[0] for x in timing}),
    string_differences=[(p, x[:120], y[:120]) for p, x, y in strs],
    keys_only_in_one=[(p, o, (v if not isinstance(v, (dict, list)) else type(v).__name__))
                      for p, o, v in struct])
print(f"\n(6d) raw-result: {len(nums)} numeric/boolean differences; all wall-clock timings: "
      f"{len(non_timing) == 0}; non-timing numeric differences: {non_timing}")
print(f"     string differences: {[p for p, _, _ in strs]}")
print(f"     keys present in only one execution: {len(struct)}")
for p, o, v in struct[:40]:
    print(f"       {p:<105} only in {o}   value={str(v)[:40]}")

r2 = json.load(open(RUN + "reproduction.json"))
r1 = json.load(open(RUN + "reproduction.driver-exec-1.json"))
nums2, strs2, struct2 = [], [], []
walk(r2, r1, "", nums2, strs2, struct2)
out["driver_diff_reproduction"] = dict(
    numeric_or_boolean_differences=len(nums2), differences=nums2,
    string_differences=[(p, x[:120], y[:120]) for p, x, y in strs2],
    keys_only_in_one=[(p, o, str(v)[:80]) for p, o, v in struct2])
print(f"\n(6e) reproduction: {len(nums2)} numeric/boolean differences; "
      f"{len(struct2)} keys present in only one execution")
for p, o, v in struct2:
    print(f"       {p:<100} only in {o}   value={str(v)[:50]}")
print("\n     exec-1 control block:", json.dumps(r1["uncorrected_figures_control"].get(
    "eq11_pipeline_against_uncorrected_targets"), indent=1)[:900])
print("     exec-1 summary flag  :",
      r1["uncorrected_figures_control"].get("eq11_pipeline_reproduces_any_uncorrected_figure"))
print("     exec-2 summary flag  :",
      r2["uncorrected_figures_control"].get(
          "eq11_pipeline_reproduces_an_uncorrected_figure_where_it_differs_from_corrected"))
out["control_flag_exec1"] = r1["uncorrected_figures_control"].get(
    "eq11_pipeline_reproduces_any_uncorrected_figure")
out["control_flag_exec2"] = r2["uncorrected_figures_control"].get(
    "eq11_pipeline_reproduces_an_uncorrected_figure_where_it_differs_from_corrected")
out["gate_pass_both_executions"] = [r1.get("passed"), r2.get("passed")]
out["worst_error_both_executions"] = [r1.get("worst_abs_error_bits_1e-3_cells"),
                                      r2.get("worst_abs_error_bits_1e-3_cells")]
print(f"     gate passed in both executions: {out['gate_pass_both_executions']}; "
      f"worst 1e-3-cell error: {out['worst_error_both_executions']}")

json.dump(out, open("own_n3b.json", "w"), indent=1, default=str)
print("\nwrote own_n3b.json")
