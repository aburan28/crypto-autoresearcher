"""J2a(5): digests of every file of the five run directories and every implementation source.

Read-only. Recomputes sha256 of every file and compares with every recorded binding:
  run files      -> execution-receipt.json artifact_sha256, TASK-20261022-207893 ledger-receipt path_sha256,
                    BATCH-8d6d84 dispatch_queue tasks[TASK-20261022-207893].archive.path_sha256,
                    journal unit_recorded artifacts / receipt_sha256 (RBS-PFDR-bb0d26, attempt 2)
  impl sources   -> trial-plan.json source_sha256 / input_sha256, every manifest code_sha256,
                    environment.json source_sha256, runbook binds, specification-declared sha256,
                    TASK-20261022-b6532d snapshot receipt and dispatch_queue tasks[b6532d] path_sha256
  spec / plan / runbook / journal -> every place that binds them
Also verifies the journal hash chain with an independent implementation of the documented entry hash
(sha256(b"crypto.autoresearch.runbook.journal/v1\\n" + canonical JSON of the entry without "hash")).

usage: python3 -I -B digests.py <repo-root> <out.json>
"""
import hashlib
import json
import os
import sys

import yaml

REPO = os.path.abspath(sys.argv[1])
OUT = sys.argv[2]
EXP = "experiments/EXP-PFDR-bb0d26"
RUNS = ["RUN-PFDR-e44a19", "RUN-PFDR-4d8c71", "RUN-PFDR-243425", "RUN-PFDR-cd03e2", "RUN-PFDR-089edc"]
B8 = "coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-8d6d84"


def sha(rel):
    h = hashlib.sha256()
    with open(os.path.join(REPO, rel), "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def jload(rel):
    with open(os.path.join(REPO, rel)) as f:
        return json.load(f)


def yload(rel):
    with open(os.path.join(REPO, rel)) as f:
        return yaml.safe_load(f)


checks = []          # {binding, path, recorded, computed, equal}


def cmp(binding, rel, recorded):
    comp = sha(rel) if os.path.isfile(os.path.join(REPO, rel)) else None
    checks.append({"binding": binding, "path": rel, "recorded": recorded, "computed": comp,
                   "equal": recorded == comp})


ledger = jload(f"{B8}/archives/TASK-20261022-207893/ledger-receipt.json")["path_sha256"]
queue = jload(f"{B8}/dispatch_queue.json")
qt = {t["id"]: t for t in queue["tasks"]}
q207 = qt["TASK-20261022-207893"]["archive"]["path_sha256"]
qb65 = qt["TASK-20261022-b6532d"]["archive"]["path_sha256"]
snap = jload(f"{B8}/archives/TASK-20261022-b6532d/snapshot-receipt.json")["path_sha256"]
plan = jload(f"{EXP}/trial-plan.json")
runbook = yload(f"{EXP}/runbook.yaml")
spec = yload(f"{EXP}/specification.yaml")["experiment"]
journal_rel = f"{EXP}/runbook-sessions/RBS-PFDR-bb0d26/journal.jsonl"
with open(os.path.join(REPO, journal_rel)) as f:
    journal = [json.loads(ln) for ln in f]

# ------------------------------------------------------------------ run directories
inventory = {}
coverage = {}
for run in RUNS:
    rd = f"{EXP}/runs/{run}"
    files = sorted(os.path.relpath(os.path.join(dp, fn), os.path.join(REPO, rd))
                   for dp, _, fns in os.walk(os.path.join(REPO, rd)) for fn in fns)
    inventory[run] = {fn: {"sha256": sha(f"{rd}/{fn}"), "bytes": os.path.getsize(os.path.join(REPO, rd, fn))}
                      for fn in files}
    rec = jload(f"{rd}/execution-receipt.json")
    for fn, want in rec["artifact_sha256"].items():
        cmp(f"{run}/execution-receipt.json artifact_sha256", f"{rd}/{fn}", want)
    for fn in files:
        rel = f"{rd}/{fn}"
        cmp("TASK-20261022-207893 ledger-receipt path_sha256", rel, ledger.get(rel))
        cmp("BATCH-8d6d84 dispatch_queue TASK-20261022-207893 archive.path_sha256", rel, q207.get(rel))
    not_in_receipt = sorted(set(files) - set(rec["artifact_sha256"]) - {"execution-receipt.json"})
    receipt_missing = sorted(set(rec["artifact_sha256"]) - set(files))
    ledger_extra = sorted(k[len(rd) + 1:] for k in ledger if k.startswith(rd + "/") and k[len(rd) + 1:] not in files)
    coverage[run] = {"files": len(files), "not_in_execution_receipt": not_in_receipt,
                     "in_execution_receipt_but_absent": receipt_missing,
                     "in_ledger_receipt_but_absent": ledger_extra,
                     "receipt_plan_sha256": rec["plan_sha256"], "receipt_status": rec["status"],
                     "receipt_returncode": rec["returncode"], "receipt_check_returncode": rec["check_returncode"]}

# journal unit_recorded (attempt 2, the latest per trial) artifacts + receipt sha
units = {}
for e in journal:
    if e["type"] == "unit_recorded":
        units[e["trial_id"]] = e
for tid, e in units.items():
    if e.get("run_dir"):
        cmp(f"journal seq {e['seq']} receipt_sha256", f"{e['run_dir']}/execution-receipt.json", e["receipt_sha256"])
        for fn, want in (e.get("artifacts") or {}).items():
            cmp(f"journal seq {e['seq']} artifacts", f"{e['run_dir']}/{fn}", want)

# ------------------------------------------------------------------ implementation sources
impl_files = sorted(os.path.relpath(os.path.join(dp, fn), REPO)
                    for dp, _, fns in os.walk(os.path.join(REPO, EXP, "implementation")) for fn in fns)
pycache = [f for f in impl_files if "__pycache__" in f]
for rel, want in plan["source_sha256"].items():
    cmp("trial-plan.json source_sha256", rel, want)
for rel, want in plan["input_sha256"].items():
    cmp("trial-plan.json input_sha256", rel, want)
for run in RUNS:
    man = yload(f"{EXP}/runs/{run}/manifest.yaml")["run"]
    for k, want in man["code"]["code_sha256"].items():
        cmp(f"{run}/manifest.yaml code_sha256", f"{EXP}/implementation/{k}", want)
    env = jload(f"{EXP}/runs/{run}/environment.json")
    for rel, want in env["source_sha256"].items():
        cmp(f"{run}/environment.json source_sha256", rel, want)
    cmp(f"{run}/environment.json specification_sha256", f"{EXP}/specification.yaml", env["specification_sha256"])
    cmp(f"{run}/manifest.yaml trial_plan_sha256", f"{EXP}/trial-plan.json", man["code"]["trial_plan_sha256"])
    rec = jload(f"{EXP}/runs/{run}/execution-receipt.json")
    cmp(f"{run}/execution-receipt.json plan_sha256", f"{EXP}/trial-plan.json", rec["plan_sha256"])
    lj = jload(f"{EXP}/runs/{run}/launch.json")
    cmp(f"{run}/launch.json plan_sha256", f"{EXP}/trial-plan.json", lj["plan_sha256"])
for b in runbook["binds"]:
    cmp("runbook.yaml binds", b["path"], b["sha256"])
for key in ("vendor_curve_py", "known_answer_fixture"):
    ib = spec["input_bindings"][key]
    cmp(f"specification input_bindings/{key}", ib["path"], ib["sha256"])
for f in spec["inputs"]["implementation_sources"]["files"]:
    if "sha256" in f:
        cmp("specification inputs/implementation_sources", f"{EXP}/implementation/{f['path']}", f["sha256"])
for rel, want in snap.items():
    cmp("TASK-20261022-b6532d snapshot-receipt path_sha256", rel, want) if rel.startswith(EXP) else None
for rel, want in qb65.items():
    cmp("BATCH-8d6d84 dispatch_queue TASK-20261022-b6532d archive.path_sha256", rel, want) if rel.startswith(EXP) else None
cmp("trial-plan.json specification_sha256", f"{EXP}/specification.yaml", plan["specification_sha256"])
cmp(f"dispatch_queue TASK-20261022-32fe8b trial_plan_sha256", f"{EXP}/trial-plan.json",
    qt["TASK-20261022-32fe8b"]["handoff"]["execution"]["trial_plan_sha256"])
cmp("journal seq 0 runbook_sha256", f"{EXP}/runbook.yaml", journal[0]["runbook_sha256"])
for b in journal[0]["binds"]:
    cmp("journal seq 0 binds", b["path"], b["sha256"])
cmp("TASK-20261022-207893 ledger-receipt path_sha256", journal_rel, ledger.get(journal_rel))
for rel, want in ledger.items():
    if rel.startswith(f"{EXP}/runbook-sessions/"):
        cmp("TASK-20261022-207893 ledger-receipt path_sha256 (session)", rel, want)
audit = jload(f"{EXP}/audits/AUD-20261029T012603Z-0b6353/audit.json")
cmp("AUD-20261029T012603Z-0b6353 audit.json runbook_sha256", f"{EXP}/runbook.yaml", audit["runbook_sha256"])

# DEC-20261022-9aec2b quotes receipt-recorded digests; each quoted 64-hex value must be a recomputed digest
import re  # noqa: E402
dec_rel = "ledger/decisions/DEC-20261022-9aec2b.yaml"
with open(os.path.join(REPO, dec_rel)) as f:
    quoted = sorted(set(re.findall(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", f.read())))
recomputed = {v["sha256"] for run in inventory.values() for v in run.values()} | {sha(f"{EXP}/trial-plan.json")}
for h in quoted:
    checks.append({"binding": "DEC-20261022-9aec2b quoted sha256 is a recomputed digest", "path": dec_rel,
                   "recorded": h, "computed": h if h in recomputed else None, "equal": h in recomputed})

# ------------------------------------------------------------------ journal chain (own implementation)
DOMAIN = b"crypto.autoresearch.runbook.journal/v1\n"
chain = []
prev = "0" * 64
for i, e in enumerate(journal):
    body = {k: v for k, v in e.items() if k != "hash"}
    h = hashlib.sha256(DOMAIN + json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                                           allow_nan=False).encode("utf-8")).hexdigest()
    chain.append({"seq": e["seq"], "type": e["type"], "seq_ok": e["seq"] == i, "prev_ok": e["prev"] == prev,
                  "hash_ok": h == e["hash"]})
    prev = e["hash"]
chain_ok = all(c["seq_ok"] and c["prev_ok"] and c["hash_ok"] for c in chain)

impl_inventory = {rel: {"sha256": sha(rel), "bytes": os.path.getsize(os.path.join(REPO, rel))} for rel in impl_files}
bound = set(plan["source_sha256"])
fails = [c for c in checks if not c["equal"]]
out = {
    "script": "scripts/digests.py",
    "python": sys.version,
    "executable": sys.executable,
    "repo_head": os.popen(f"git -C {REPO} rev-parse HEAD").read().strip(),
    "run_directory_inventory": inventory,
    "run_directory_coverage": coverage,
    "implementation_inventory": impl_inventory,
    "implementation_files_not_bound_by_trial_plan_source_sha256": sorted(set(impl_files) - bound),
    "pycache_in_implementation": pycache,
    "journal_chain": {"entries": len(journal), "tip": journal[-1]["hash"], "all_ok": chain_ok, "entries_detail": chain},
    "binding_checks": {"count": len(checks), "failures": len(fails), "failed": fails,
                       "by_binding": {}},
}
for c in checks:
    b = out["binding_checks"]["by_binding"].setdefault(c["binding"], {"checks": 0, "failures": 0, "paths_equal": []})
    b["checks"] += 1
    b["failures"] += (not c["equal"])
    if c["equal"]:
        b["paths_equal"].append(c["path"])
with open(OUT, "w") as f:
    json.dump(out, f, indent=1, sort_keys=True)
    f.write("\n")
print("binding checks", len(checks), "failures", len(fails), "| chain ok", chain_ok,
      "| impl files", len(impl_files), "unbound", sorted(set(impl_files) - bound))
for c in fails:
    print("FAIL", c)
