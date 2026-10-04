#!/usr/bin/env python3
"""TASK-20260926-0f8aec, joint J4: instrument, package and procedure integrity.

Reads committed bytes at c7f5e3dfa only (the sparse worktree WT). Imports
nothing from impl/ or verifier/. It imports tools/validate_ledger.py from WT
(the archive head's copy) to run its check_run on this run's manifest. It
also re-runs no driver phase, no C-ENGINE replay and no verifier; it only
reads their archived records and recomputes what can be recomputed from raw
bytes.

Sections: B bindings (40b2ca receipt re-hash, 58d32c receipt and
prior_commit_bindings, impl/verifier hashes vs manifest, spec, trial plan,
predictions-t5, draw logs, instances, dev overrides); D D-1 (YAML key diff,
repair of each item, registry note, validate_ledger check_run with and
without the supersession); C controls (each control's archived record,
plus independent rechecks where raw bytes allow); P package completeness.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import os
import sys
from itertools import combinations
from pathlib import Path

import yaml

WT = Path(sys.argv[1])
OUTDIR = Path(__file__).resolve().parent
EXP = WT / "experiments/EXP-CERTBIN-ddfe75"
RUN = EXP / "runs/RUN-CERTBIN-6ebb0e"
R = {"task": "TASK-20260926-0f8aec", "joint": "J4"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def jl(p):
    return [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]


# ------------------------------------------------------------------ B bindings
B = {}
rc = json.load(open(WT / "coordination/design/certbin-nconv-20260924/archives/TASK-20260924-40b2ca/snapshot-receipt.json"))
mism = {p: (h, sha(WT / p) if (WT / p).exists() else None) for p, h in rc["path_sha256"].items()
        if not (WT / p).exists() or sha(WT / p) != h}
B["receipt_40b2ca"] = {"paths": len(rc["path_sha256"]), "mismatches": mism,
                       "archive_artifact_paths_equal_hashed_set": sorted(rc["archive_artifact_paths"]) == sorted(rc["path_sha256"])}
# every file in the run package / impl / verifier / spec / plan is hash-bound?
pkg = [str(p.relative_to(WT)) for p in sorted(EXP.rglob("*")) if p.is_file()]
unbound = [p for p in pkg if p not in rc["path_sha256"]]
B["package_files_not_bound_by_40b2ca"] = unbound
r58 = json.load(open(WT / "coordination/review/certbin-20260926-089841/archives/TASK-20260926-58d32c/snapshot-receipt.json"))
m58 = {p: h for p, h in r58["path_sha256"].items() if (WT / p).exists() and sha(WT / p) != h}
not_hashed_58 = sorted(p for p in r58["path_sha256"] if not (WT / p).exists())
pcb = r58["SC-6"]["prior_commit_bindings"]
B["receipt_58d32c"] = {"paths": len(r58["path_sha256"]), "mismatches": m58, "not_hashed_outside_my_inputs": not_hashed_58,
                       "prior_commit_bindings": {p: {"bound": v["sha256"], "actual": sha(WT / p),
                                                     "equal": sha(WT / p) == v["sha256"]} for p, v in pcb.items()}}
man = yaml.safe_load(open(RUN / "manifest.yaml"))
man2 = yaml.safe_load(open(RUN / "manifest_v2.yaml"))
code = man["run"]["code"]
B["impl_sha256_manifest_vs_archived"] = {f: {"manifest": h, "archived": sha(EXP / "impl" / f), "equal": sha(EXP / "impl" / f) == h}
                                         for f, h in code["impl_sha256"].items()}
B["impl_files_not_in_manifest"] = sorted(set(p.name for p in (EXP / "impl").iterdir() if p.is_file()) - set(code["impl_sha256"]))
B["verifier_sha256_manifest_vs_archived"] = {f: sha(EXP / "verifier" / f) == h for f, h in code["verifier_sha256"].items()}
B["spec"] = {"manifest_sha256": man["run"]["specification"]["sha256"], "archived_sha256": sha(EXP / "specification.yaml")}
B["spec"]["equal"] = B["spec"]["manifest_sha256"] == B["spec"]["archived_sha256"]
plog = [json.loads(l) for l in open(RUN / "phase-log.jsonl")]
p0end = [e for e in plog if e["phase"] == 0 and e["event"] == "end"][0]
ep = json.load(open(RUN / "engine-provenance/summary.json"))
tp = json.load(open(EXP / "trial-plan-v1.json"))
B["trial_plan"] = {"archived_sha256": sha(EXP / "trial-plan-v1.json"), "phase0_logged_sha256": p0end["trial_plan_sha256"],
                   "manifest_sha256": man["run"]["trial_plan"]["sha256"], "written_at": tp.get("written_at"),
                   "engine_provenance_started": ep["started"],
                   "phase0_start": [e for e in plog if e["phase"] == 0 and e["event"] == "start"][0]["at"],
                   "first_invocation_at": man["run"]["code"]["invocations"][0]["at"],
                   "untracked_at_first_invocation": "?? experiments/EXP-CERTBIN-ddfe75/trial-plan-v1.json" in code["dirty_paths_at_first_invocation"],
                   "top_level_keys": sorted(tp.keys())}
B["trial_plan"]["sha_equal"] = len({B["trial_plan"]["archived_sha256"], B["trial_plan"]["phase0_logged_sha256"],
                                    B["trial_plan"]["manifest_sha256"]}) == 1
B["trial_plan"]["written_before_engine_provenance_and_phase0"] = (
    tp.get("written_at") < ep["started"] < B["trial_plan"]["phase0_start"])
p3end = [e for e in plog if e["phase"] == 3 and e["event"] == "end"][0]
p4start = [e for e in plog if e["phase"] == 4 and e["event"] == "start"][0]
B["predictions_t5"] = {"archived_sha256": sha(RUN / "predictions-t5.jsonl.gz"), "logged_sha256": p3end["predictions_t5_sha256"],
                       "logged_at": p3end["at"], "phase4_start": p4start["at"]}
B["predictions_t5"]["equal"] = B["predictions_t5"]["archived_sha256"] == B["predictions_t5"]["logged_sha256"]
B["predictions_t5"]["hashed_before_phase4"] = p3end["at"] < p4start["at"]
dr = {}
for e in plog:
    if e["phase"] == 2 and e["event"].startswith("arm "):
        arm = e["event"][4:]
        dr[arm] = {"logged": e["draws_sha256"], "archived": sha(RUN / f"draws-{arm}.jsonl.gz")}
        dr[arm]["equal"] = dr[arm]["logged"] == dr[arm]["archived"]
B["draw_logs"] = dr
p2end = [e for e in plog if e["phase"] == 2 and e["event"] == "end"][0]
B["instances"] = {"logged": p2end["instances_sha256"], "archived": sha(RUN / "instances.jsonl.gz")}
B["instances"]["equal"] = B["instances"]["logged"] == B["instances"]["archived"]
env = json.load(open(RUN / "environment.json"))
B["environment_json"] = env
B["dev_overrides_unset"] = {"manifest_environment": man["run"]["environment"].get("dev_overrides_unset"),
                            "verifier_invocation": man["run"]["code"].get("verifier_invocation", {}).get("dev_overrides")}
B["invocations"] = [{"at": i["at"], "argv_tail": i["argv"][-2:], "commit": i["commit"], "dirty": i["dirty"],
                     "env": i["env"], "pid": i["pid"]} for i in man["run"]["code"]["invocations"]]
B["command_txt"] = open(RUN / "command.txt").read()
B["stderr_log_bytes"] = os.path.getsize(RUN / "stderr.log")
B["package_bytes"] = sum((RUN / p).stat().st_size for p in os.listdir(RUN) if (RUN / p).is_file()) + \
    sum(p.stat().st_size for p in (RUN / "checkpoint").iterdir()) + sum(p.stat().st_size for p in (RUN / "engine-provenance").iterdir())
R["B_bindings"] = B

# ------------------------------------------------------------------ D D-1
def flatten(x, pre=""):
    out = {}
    if isinstance(x, dict):
        if pre:
            out[pre] = "<map>"
        for k, v in x.items():
            out.update(flatten(v, f"{pre}.{k}" if pre else str(k)))
    elif isinstance(x, list):
        out[pre] = json.dumps(x, sort_keys=True, default=str)
    else:
        out[pre] = x
    return out


f1, f2 = flatten(man), flatten(man2)
added = sorted(set(f2) - set(f1))
removed = sorted(set(f1) - set(f2))
changed = sorted(k for k in set(f1) & set(f2) if f1[k] != f2[k])
leaf_added = [k for k in added if f2[k] != "<map>"]
map_added = [k for k in added if f2[k] == "<map>"]
D = {"added_paths_all": added, "added_count_all": len(added), "added_leaf_count": len(leaf_added),
     "added_map_count": len(map_added), "removed": removed, "changed": changed,
     "added_values": {k: f2[k] for k in added}}
# D-1 items
rb2 = man2["run"]
items = {
    "run.timing": isinstance(rb2.get("timing"), dict) and bool(rb2.get("timing")),
    "run.result": isinstance(rb2.get("result"), dict) and bool(rb2.get("result")),
    "run.code.commit": bool((rb2.get("code") or {}).get("commit")),
    "run.code.command": bool((rb2.get("code") or {}).get("command")),
    "run.result.certificate.kind in {discrete_log, decomposition, none}":
        ((rb2.get("result") or {}).get("certificate") or {}).get("kind") in ("discrete_log", "decomposition", "none"),
}
D["D1_items_repaired"] = items
# consistency of the added values with the source fields
chk = {}
chk["code.commit == commit_at_first_invocation"] = rb2["code"].get("commit") == man["run"]["code"]["commit_at_first_invocation"]
chk["code.dirty == dirty_at_first_invocation"] = rb2["code"].get("dirty") == man["run"]["code"]["dirty_at_first_invocation"]
chk["code.command"] = rb2["code"].get("command")
chk["command.txt exists"] = (RUN / "command.txt").exists()
tm = rb2.get("timing") or {}
ats = [e["at"] for evs in man["run"]["phase_timings"].values() for e in evs]
chk["timing"] = tm
chk["timing min/max of phase_timings"] = {"min": min(ats), "max": max(ats)}
res2 = rb2.get("result") or {}
chk["result"] = res2
chk["result.status == run.status"] = res2.get("status") == man["run"]["status"]
D["added_value_consistency"] = chk
reg = yaml.safe_load(open(WT / "tools/run_supersession_registry.yaml"))
recs = reg["records"] if isinstance(reg, dict) and "records" in reg else reg
entry = [e for e in (recs if isinstance(recs, list) else []) if e.get("run_id") == "RUN-CERTBIN-6ebb0e"]
D["registry_entry"] = entry[0] if entry else None
if entry:
    D["registry_hashes"] = {"superseded": sha(WT / entry[0]["superseded_path"]) == entry[0]["superseded_sha256"],
                            "superseding": sha(WT / entry[0]["superseding_path"]) == entry[0]["superseding_sha256"]}
# validate_ledger.check_run at the archive head (the WT copy)
spec_ = importlib.util.spec_from_file_location("vl_archive_head", WT / "tools/validate_ledger.py")
vl = importlib.util.module_from_spec(spec_)
spec_.loader.exec_module(vl)
sups_all = vl.load_run_supersessions()
mine = {k: v for k, v in sups_all.items() if v["run_id"] == "RUN-CERTBIN-6ebb0e"}
ctx_a = vl.Ctx(legacy_paths=set())
vl.check_run(str(RUN / "manifest.yaml"), ctx_a, None)
ctx_b = vl.Ctx(legacy_paths=set())
vl.check_run_supersessions(ctx_b, mine)
vl.check_run(str(RUN / "manifest.yaml"), ctx_b, mine)
D["validate_ledger_check_run"] = {
    "validator_file": "tools/validate_ledger.py at c7f5e3dfa",
    "without_supersession_errors": ctx_a.errors, "without_supersession_legacy_warnings": ctx_a.legacy_warnings,
    "with_supersession_errors": ctx_b.errors, "with_supersession_legacy_warnings": ctx_b.legacy_warnings,
    "supersession_entries_applied": len(mine), "run_registered": "RUN-CERTBIN-6ebb0e" in ctx_b.ids}
R["D_manifest_v2"] = D

# ------------------------------------------------------------------ C controls
C = {}
ic = json.load(open(RUN / "instrument-checks.json"))
C["instrument_checks_json_top_keys"] = list(ic.keys()) if isinstance(ic, dict) else None
st = json.load(open(RUN / "selftest.json"))
C["selftest_top_keys"] = list(st.keys())
det = json.load(open(RUN / "determinism.json"))
C["determinism"] = {"a_draw_logs": det["a_draw_logs"], "b_threads": det["b_recompute"]["threads"],
                    "b_systems": det["b_recompute"]["systems"], "b_mismatches": det["b_recompute"]["mismatches"],
                    "c_threads": det["c_threads1"]["threads"], "c_mismatches": det["c_threads1"]["mismatches"],
                    "pid": det.get("pid"), "phase4_pid": man["run"]["code"]["invocations"][0]["pid"],
                    "started": det.get("started"), "finished": det.get("finished"), "pass": det["pass"]}
C["determinism"]["a_logged_equals_archived"] = {a: v["sha256_file"] == sha(RUN / f"draws-{a}.jsonl.gz")
                                                for a, v in det["a_draw_logs"].items()}
ncv = json.load(open(RUN / "negative-controls-verification.json"))
C["negative_controls_top_keys"] = list(ncv.keys())
R["C_controls_raw"] = C
json.dump(R, open(OUTDIR / "j4-checks.json", "w"), indent=1, default=str)
print(json.dumps({"B": {k: (v if k not in ("environment_json", "impl_sha256_manifest_vs_archived", "invocations", "command_txt")
                            else "...") for k, v in B.items()}}, default=str)[:6000])
print("D", json.dumps({k: v for k, v in D.items() if k not in ("added_values", "registry_entry")}, default=str)[:6000])
print("C", json.dumps(C, default=str)[:3000])
