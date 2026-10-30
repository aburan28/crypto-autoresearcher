"""J2a(1)-(3): compare replay outputs with the recorded run files, byte for byte and leaf by leaf.

Exact comparison for the CPython 3.11 replay. For the CPython 3.13 replay: float leaves compared with
math.isclose(rel_tol=1e-9, abs_tol=1e-12); ints, strings, bools, nulls, key sets, list lengths and leaf types
exact; the result is labelled matched_within_tolerance (never matched) when only float leaves differ within
tolerance. Read-only on experiments/.

usage: python3 -I -B compare.py <repo-root> <outputs-dir>
"""
import hashlib
import json
import math
import os
import sys

import yaml

REPO, OUTD = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
RUNS = os.path.join(REPO, "experiments/EXP-PFDR-bb0d26/runs")
REL_TOL, ABS_TOL = 1e-9, 1e-12
UNITS = {
    "selftest": ("RUN-PFDR-e44a19", ["selftest.json", "design.json", "raw-result.json"]),
    "analyze-main": ("RUN-PFDR-243425", ["analysis-main.json", "flags.json", "raw-result.json"]),
    "analyze-final": ("RUN-PFDR-089edc", ["analysis.json", "flags.json", "raw-result.json"]),
}


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def kind(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, int):
        return "int"
    if isinstance(v, float):
        return "float"
    if isinstance(v, str):
        return "str"
    if isinstance(v, list):
        return "list"
    if isinstance(v, dict):
        return "dict"
    return type(v).__name__


def walk(a, b, ptr, tol, acc):
    ka, kb = kind(a), kind(b)
    if ka != kb:
        acc["nonfloat_diffs"].append({"pointer": ptr, "recorded": a, "replay": b, "why": f"type {ka} vs {kb}"})
        return
    if ka == "dict":
        if set(a) != set(b):
            acc["nonfloat_diffs"].append({"pointer": ptr, "why": "key sets differ",
                                          "only_recorded": sorted(set(a) - set(b)),
                                          "only_replay": sorted(set(b) - set(a))})
        for k in sorted(set(a) & set(b)):
            walk(a[k], b[k], f"{ptr}/{k}", tol, acc)
        return
    if ka == "list":
        if len(a) != len(b):
            acc["nonfloat_diffs"].append({"pointer": ptr, "why": f"list length {len(a)} vs {len(b)}"})
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{ptr}/{i}", tol, acc)
        return
    acc["leaves"] += 1
    if ka == "float":
        acc["float_leaves"] += 1
        if a == b:
            return
        ad = abs(a - b)
        rd = ad / max(abs(a), abs(b)) if max(abs(a), abs(b)) > 0 else 0.0
        ok = tol and math.isclose(a, b, rel_tol=REL_TOL, abs_tol=ABS_TOL)
        rec = {"pointer": ptr, "recorded": a, "replay": b, "abs": ad, "rel": rd}
        acc["float_diffs"].append(rec)
        if not ok:
            acc["float_out_of_tolerance"].append(rec)
        return
    if a != b:
        acc["nonfloat_diffs"].append({"pointer": ptr, "recorded": a, "replay": b})


def compare_json(rec_path, rep_path, tol, keep_float_detail):
    with open(rec_path) as f:
        a = json.load(f)
    with open(rep_path) as f:
        b = json.load(f)
    acc = {"leaves": 0, "float_leaves": 0, "float_diffs": [], "float_out_of_tolerance": [], "nonfloat_diffs": []}
    walk(a, b, "", tol, acc)
    fam = {}
    for d in acc["float_diffs"]:
        parts = d["pointer"].split("/")
        key = "/".join(p if not p.isdigit() else "#" for p in parts)
        fam[key] = fam.get(key, 0) + 1
    res = {
        "leaves": acc["leaves"], "float_leaves": acc["float_leaves"],
        "nonfloat_differences": acc["nonfloat_diffs"],
        "float_leaves_differing": len(acc["float_diffs"]),
        "float_leaves_out_of_tolerance": acc["float_out_of_tolerance"],
        "max_rel_float_difference": max((d["rel"] for d in acc["float_diffs"]), default=0.0),
        "max_abs_float_difference": max((d["abs"] for d in acc["float_diffs"]), default=0.0),
        "differing_float_families": dict(sorted(fam.items())),
    }
    if keep_float_detail or len(acc["float_diffs"]) <= 6:
        res["float_differences"] = acc["float_diffs"]
    else:
        top = sorted(acc["float_diffs"], key=lambda d: -d["rel"])[:3]
        res["float_differences_largest_rel_3"] = top
    if acc["nonfloat_diffs"] or acc["float_out_of_tolerance"]:
        res["result"] = "mismatch"
    elif acc["float_diffs"]:
        res["result"] = "matched_within_tolerance" if tol else "mismatch"
    else:
        res["result"] = "exact"
    return res, a, b


def cells_section(a, b, tol):
    """/cells: per field, how many cells compare exact / within tolerance / out; cls, S, kappa listed."""
    out = {}
    for i, (ra, rb) in enumerate(zip(a["cells"], b["cells"])):
        for k in sorted(set(ra) | set(rb)):
            st = out.setdefault(k, {"exact": 0, "within_tolerance": 0, "differ": 0})
            x, y = ra.get(k, "<absent>"), rb.get(k, "<absent>")
            if json.dumps(x, sort_keys=True) == json.dumps(y, sort_keys=True):
                st["exact"] += 1
                continue
            acc = {"leaves": 0, "float_leaves": 0, "float_diffs": [], "float_out_of_tolerance": [], "nonfloat_diffs": []}
            walk(x, y, f"/cells/{i}/{k}", tol, acc)
            if acc["nonfloat_diffs"] or acc["float_out_of_tolerance"]:
                st["differ"] += 1
            else:
                st["within_tolerance"] += 1
    return {"cells": len(a["cells"]), "cells_replay": len(b["cells"]), "per_field": out}


def manifest_compare(run_id, rep_dir):
    with open(os.path.join(RUNS, run_id, "manifest.yaml")) as f:
        a = yaml.safe_load(f)["run"]
    with open(os.path.join(rep_dir, "manifest.yaml")) as f:
        b = yaml.safe_load(f)["run"]
    keys = {
        "code.code_sha256": (a["code"]["code_sha256"], b["code"]["code_sha256"]),
        "code.trial_plan_sha256": (a["code"]["trial_plan_sha256"], b["code"]["trial_plan_sha256"]),
        "code.dirty": (a["code"]["dirty"], b["code"]["dirty"]),
        "code.commit": (a["code"]["commit"], b["code"]["commit"]),
        "environment.python_version": (a["environment"]["python_version"], b["environment"]["python_version"]),
        "environment.gcc_version": (a["environment"]["gcc_version"], b["environment"]["gcc_version"]),
        "status": (a["status"], b["status"]),
        "validity": (a["validity"], b["validity"]),
        "inputs": (a["inputs"], b["inputs"]),
        "result": (a["result"], b["result"]),
        "artifacts": (a["artifacts"], b["artifacts"]),
        "resources": (a["resources"], b["resources"]),
    }
    return {k: ({"equal": True} if v[0] == v[1] else {"recorded": v[0], "replay": v[1], "equal": False})
            for k, v in keys.items()}


report = {"script": "scripts/compare.py", "python": sys.version, "executable": sys.executable,
          "tolerance_declared_for_py313": {"float_leaves": {"rel_tol": REL_TOL, "abs_tol": ABS_TOL},
                                           "exact": "ints, strings, bools, nulls, key sets, list lengths, leaf types",
                                           "label": "matched_within_tolerance, never matched"},
          "replays": {}}
replay_objs = {}
for interp, tol in (("replay-py311", False), ("replay-py313", True)):
    with open(os.path.join(OUTD, interp, "interpreter.json")) as f:
        ij = json.load(f)
    sect = {"interpreter": ij, "comparison_mode": "toleranced" if tol else "exact", "units": {}}
    for unit, (run_id, files) in UNITS.items():
        rep_dir = os.path.join(OUTD, interp, unit)
        with open(os.path.join(rep_dir, "replay.exit.json")) as f:
            ex = json.load(f)
        u = {"recorded_run": run_id, "route": "bound driver trial entry point: run.py trial --run-dir <outputs>/" +
             f"{interp}/{unit} --run-id {run_id} --trial-id {unit} --plan experiments/EXP-PFDR-bb0d26/trial-plan.json",
             "replay_exit_code": ex["exit_code"], "files": {}}
        for fn in files:
            rp, pp = os.path.join(RUNS, run_id, fn), os.path.join(rep_dir, fn)
            byte_eq = open(rp, "rb").read() == open(pp, "rb").read()
            res, a, b = compare_json(rp, pp, tol, keep_float_detail=(fn == "raw-result.json"))
            ent = {"recorded_sha256": sha(rp), "replay_sha256": sha(pp), "byte_identical": byte_eq,
                   "leaf_by_leaf": res}
            if fn == "raw-result.json":
                r2, _, _ = compare_json(rp, pp, tol, True)
                ent["summary_pointer"] = "/summary (included in the leaf walk above)"
            if fn.startswith("analysis"):
                ent["cells"] = cells_section(a, b, tol)
                replay_objs[(interp, unit)] = b
            u["files"][fn] = ent
        so_rec = open(os.path.join(RUNS, run_id, "stdout.log"), "rb").read()
        so_rep = open(os.path.join(rep_dir, "replay.stdout.log"), "rb").read()
        u["stdout_byte_identical_to_recorded_stdout_log"] = so_rec == so_rep
        u["stderr_empty"] = os.path.getsize(os.path.join(rep_dir, "replay.stderr.log")) == 0
        u["manifest_fields"] = manifest_compare(run_id, rep_dir)
        sect["units"][unit] = u
    report["replays"][interp] = sect

# recorded analysis-main vs recorded analysis (final): every key except stage should agree
with open(os.path.join(RUNS, "RUN-PFDR-243425", "analysis-main.json")) as f:
    am = json.load(f)
with open(os.path.join(RUNS, "RUN-PFDR-089edc", "analysis.json")) as f:
    af = json.load(f)
acc = {"leaves": 0, "float_leaves": 0, "float_diffs": [], "float_out_of_tolerance": [], "nonfloat_diffs": []}
walk(am, af, "", False, acc)
report["recorded_analysis_main_vs_final"] = {
    "note": "recorded RUN-PFDR-243425/analysis-main.json (left) against recorded RUN-PFDR-089edc/analysis.json (right)",
    "nonfloat_differences": [{"pointer": d["pointer"], "analysis-main.json": d.get("recorded"), "analysis.json": d.get("replay")}
                             for d in acc["nonfloat_diffs"]],
    "float_differences": len(acc["float_diffs"])}
# py313 replay vs py311 replay (interpreter drift isolated from the record)
d = {}
for unit, fn in (("analyze-main", "analysis-main.json"), ("analyze-final", "analysis.json")):
    res, _, _ = compare_json(os.path.join(OUTD, "replay-py311", unit, fn), os.path.join(OUTD, "replay-py313", unit, fn),
                             True, False)
    d[unit] = {k: res[k] for k in ("result", "nonfloat_differences", "float_leaves_differing",
                                   "max_rel_float_difference", "max_abs_float_difference")}
report["py313_replay_vs_py311_replay"] = d

with open(os.path.join(OUTD, "replay-compare.json"), "w") as f:
    json.dump(report, f, indent=1, sort_keys=True)
    f.write("\n")
for interp, sect in report["replays"].items():
    for unit, u in sect["units"].items():
        for fn, ent in u["files"].items():
            print(interp, unit, fn, "bytes" if ent["byte_identical"] else "BYTES-DIFFER", ent["leaf_by_leaf"]["result"],
                  "floatdiff", ent["leaf_by_leaf"]["float_leaves_differing"], "nonfloat",
                  len(ent["leaf_by_leaf"]["nonfloat_differences"]), "maxrel", ent["leaf_by_leaf"]["max_rel_float_difference"])
        print("   stdout identical", u["stdout_byte_identical_to_recorded_stdout_log"],
              {k: v["equal"] for k, v in u["manifest_fields"].items()})
print("recorded main vs final", report["recorded_analysis_main_vs_final"])
print("py313 vs py311", d)
