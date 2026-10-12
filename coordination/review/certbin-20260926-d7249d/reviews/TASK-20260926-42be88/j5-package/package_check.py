"""J5 (1)(2): package integrity and the manifest_v2 supersession, from committed bytes.

(A) Per-file hash table: every path of the TASK-20260924-d0f80c receipt (path_sha256, path_size_bytes)
    against the archived bytes at the TASK-20260926-5d1557 archive commit (my git-archive export), and
    against executor_manifest.files (manifest.yaml 'files'); every mismatch explained (prefix / append test).
(B) Files present in the run package / impl / verifier but not bound by the d0f80c receipt.
(C) manifest_v2.yaml: YAML-level deep comparison of executor_manifest with manifest.yaml; every leaf of the
    added blocks traced to an executor value; sha256 against the registry and the 5d1557 SC-6 bindings.
(D) Required artifacts of the specification present.
usage: python3 package_check.py <snapshot_root>
"""
import hashlib
import json
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1]
EXP = "experiments/EXP-CERTBIN-060020"
RUNP = f"{EXP}/runs/RUN-CERTBIN-a3fc60"


def sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), "rb").read()).hexdigest()


def size(path):
    return os.path.getsize(os.path.join(ROOT, path))


rec = json.load(open(os.path.join(ROOT, "coordination/design/certbin-n19-20260924/archives/TASK-20260924-d0f80c/snapshot-receipt.json")))
man = yaml.safe_load(open(os.path.join(ROOT, RUNP, "manifest.yaml")))
v2 = yaml.safe_load(open(os.path.join(ROOT, RUNP, "manifest_v2.yaml")))
out = {}

# ---------------------------------------------------------------- (A)
table = []
for p, h in sorted(rec["path_sha256"].items()):
    exists = os.path.exists(os.path.join(ROOT, p))
    row = {"path": p, "receipt_sha256": h, "receipt_bytes": rec["path_size_bytes"].get(p),
           "archived_sha256": sha(p) if exists else None, "archived_bytes": size(p) if exists else None}
    row["archived_equals_receipt"] = exists and row["archived_sha256"] == h and row["archived_bytes"] == row["receipt_bytes"]
    if p.startswith(RUNP + "/"):
        rel = p[len(RUNP) + 1:]
        mf = (man.get("files") or {}).get(rel)
        if mf is not None:
            row["manifest_sha256"] = mf["sha256"]
            row["manifest_bytes"] = mf["bytes"]
            row["manifest_equals_archived"] = mf["sha256"] == row["archived_sha256"] and mf["bytes"] == row["archived_bytes"]
            if not row["manifest_equals_archived"] and exists:
                data = open(os.path.join(ROOT, p), "rb").read()
                pref = data[: mf["bytes"]]
                row["archived_prefix_of_manifest_length_sha256_equals_manifest"] = hashlib.sha256(pref).hexdigest() == mf["sha256"]
                row["appended_bytes"] = len(data) - mf["bytes"]
                row["appended_text"] = data[mf["bytes"]:].decode("utf-8", "replace")
    table.append(row)
out["receipt_paths"] = len(table)
out["receipt_paths_archived_equal"] = sum(1 for r in table if r["archived_equals_receipt"])
out["receipt_mismatches"] = [r for r in table if not r["archived_equals_receipt"]]
mf_rows = [r for r in table if "manifest_sha256" in r]
out["manifest_files_listed"] = len(man.get("files") or {})
out["manifest_files_compared"] = len(mf_rows)
out["manifest_vs_archived_mismatches"] = [{k: r[k] for k in r if k in ("path", "receipt_sha256", "receipt_bytes", "archived_sha256", "archived_bytes",
                                                                       "manifest_sha256", "manifest_bytes", "archived_prefix_of_manifest_length_sha256_equals_manifest",
                                                                       "appended_bytes", "appended_text")} for r in mf_rows if not r["manifest_equals_archived"]]
listed_not_in_receipt = [k for k in (man.get("files") or {}) if f"{RUNP}/{k}" not in rec["path_sha256"]]
out["manifest_files_not_in_receipt"] = listed_not_in_receipt
out["receipt_run_files_not_in_manifest_files"] = sorted(p[len(RUNP) + 1:] for p in rec["path_sha256"] if p.startswith(RUNP + "/") and p[len(RUNP) + 1:] not in (man.get("files") or {}))
out["per_file_table"] = [{k: r.get(k) for k in ("path", "receipt_sha256", "receipt_bytes", "archived_sha256", "archived_bytes", "archived_equals_receipt",
                                                "manifest_sha256", "manifest_bytes", "manifest_equals_archived")} for r in table]

# ---------------------------------------------------------------- (B)
present = []
for base in (f"{EXP}/impl", f"{EXP}/verifier", RUNP, f"{EXP}/trial-plan-v1.json", f"{EXP}/specification.yaml", f"{EXP}/amendments"):
    full = os.path.join(ROOT, base)
    if os.path.isfile(full):
        present.append(base)
    else:
        for dp, dn, fn in os.walk(full):
            for f in fn:
                present.append(os.path.relpath(os.path.join(dp, f), ROOT))
out["package_files_present"] = len(present)
out["present_not_bound_by_d0f80c"] = sorted(p for p in present if p not in rec["path_sha256"])
out["bound_but_absent"] = sorted(p for p in rec["path_sha256"] if not os.path.exists(os.path.join(ROOT, p)))

# ---------------------------------------------------------------- (C)
em = v2.get("executor_manifest")
out["manifest_v2_top_keys"] = list(v2.keys())
out["executor_manifest_equals_manifest_yaml"] = em == man


def leaves(o, path=()):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, path + (str(k),))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, path + (f"[{i}]",))
    else:
        yield path, o


def subtrees(o, path=()):
    yield path, o
    if isinstance(o, dict):
        for k, v in o.items():
            yield from subtrees(v, path + (str(k),))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from subtrees(v, path + (f"[{i}]",))


man_sub = {}
for pth, val in subtrees(man):
    man_sub.setdefault(json.dumps(val, sort_keys=True, default=str), []).append("/".join(pth))
trace = []
untraced = []


def walk(o, path):
    key = json.dumps(o, sort_keys=True, default=str)
    if key in man_sub and (isinstance(o, (dict, list)) or len(path) > 0):
        if isinstance(o, (dict, list)) or True:
            trace.append({"manifest_v2": "/".join(path), "executor_paths": man_sub[key][:3], "kind": type(o).__name__})
            return
    if isinstance(o, dict):
        for k, v in o.items():
            walk(v, path + (str(k),))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + (f"[{i}]",))
    else:
        untraced.append({"manifest_v2": "/".join(path), "value": o})


for k, v in v2.items():
    if k == "executor_manifest":
        continue
    walk(v, (k,))
out["manifest_v2_added_subtrees_traced_to_executor_values"] = trace
out["manifest_v2_leaves_not_found_among_executor_values"] = untraced
reg = yaml.safe_load(open(os.path.join(ROOT, "tools/run_supersession_registry.yaml")))
entries = reg if isinstance(reg, list) else (reg.get("records") or reg.get("supersessions") or reg.get("entries") or [])
ent = [e for e in entries if isinstance(e, dict) and e.get("run_id") == "RUN-CERTBIN-a3fc60"]
out["registry_entry_found"] = len(ent) == 1
if ent:
    e = ent[0]
    out["registry"] = {"superseded_sha256": e["superseded_sha256"], "superseding_sha256": e["superseding_sha256"],
                       "manifest_yaml_sha256": sha(f"{RUNP}/manifest.yaml"), "manifest_v2_sha256": sha(f"{RUNP}/manifest_v2.yaml"),
                       "superseded_equal": e["superseded_sha256"] == sha(f"{RUNP}/manifest.yaml"),
                       "superseding_equal": e["superseding_sha256"] == sha(f"{RUNP}/manifest_v2.yaml"),
                       "manifest_yaml_equals_d0f80c_receipt": rec["path_sha256"].get(f"{RUNP}/manifest.yaml") == sha(f"{RUNP}/manifest.yaml"),
                       "kind": e.get("supersession_kind")}
r5 = json.load(open(os.path.join(ROOT, "coordination/review/certbin-20260926-d7249d/archives/TASK-20260926-5d1557/snapshot-receipt.json")))
pcb = r5["SC-6"]["prior_commit_bindings"]
out["5d1557_SC6_prior_commit_bindings"] = {p: {"bound": b["sha256"], "archived": sha(p), "equal": b["sha256"] == sha(p)} for p, b in pcb.items()}
out["5d1557_receipt_paths_rehashed"] = {p: (sha(p) == h if os.path.exists(os.path.join(ROOT, p)) else "not rehashed (outside this validator's read set)")
                                       for p, h in r5["path_sha256"].items()}

# ---------------------------------------------------------------- (D)
req = ["trial-plan-v1.json", "impl/README.md", "impl/impl-provenance.json", "engine-provenance/", "selftest.json", "slice17.json", "inputs.json",
       "support.json", "draws-S3-PRIMARY.jsonl.gz", "draws-N-CONV19.jsonl.gz", "draws-N-ELL19.jsonl.gz", "draws-N-F219.jsonl.gz",
       "draws-N-AFF19.jsonl.gz", "draws-F-RANDX19.jsonl.gz", "instances.jsonl.gz", "predictions.jsonl.gz", "closures.jsonl.gz",
       "certificates.jsonl.gz", "annihilators.jsonl.gz", "certificate-verification.json", "annihilator-verification.json",
       "construction-verification.json", "draw-replay-verification.json", "negative-controls-certificates.jsonl.gz",
       "negative-controls-verification.json", "backend-check.json", "literal-check.json", "determinism.json", "instrument-checks.json",
       "decision-rules.json", "cell-summary.json", "manifest.yaml", "raw-result.json", "command.txt", "environment.json", "stdout.log",
       "stderr.log", "run-report.md"]
miss = []
for r in req:
    p = f"{EXP}/{r}" if r.startswith(("trial-plan", "impl/")) else f"{RUNP}/{r}"
    if not os.path.exists(os.path.join(ROOT, p.rstrip("/"))):
        miss.append(p)
out["required_artifacts_checked"] = len(req)
out["required_artifacts_missing"] = miss
json.dump(out, open(os.path.join(HERE, "package-check.json"), "w"), indent=1, default=str)
summary = {k: v for k, v in out.items() if k not in ("per_file_table", "manifest_v2_added_subtrees_traced_to_executor_values")}
print(json.dumps(summary, indent=1, default=str)[:9000])
print("traced subtrees:", len(trace))
for t in trace:
    print("  ", t["manifest_v2"], "<-", t["executor_paths"][:2])
