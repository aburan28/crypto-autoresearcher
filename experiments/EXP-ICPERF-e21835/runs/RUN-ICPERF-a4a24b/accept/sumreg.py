#!/usr/bin/env python3
"""D3 / A6 / C-SUMREG: the repaired reduction over the FROZEN RUN-ICPERF-305ca3 table.

Nothing is written under experiments/EXP-ICPERF-66fd51/. The frozen results.jsonl is copied
(byte-identically, hash recorded) into two directories under THIS run, and summary.py writes
its summary.json beside its own copy:

  summary_regression/repaired/       the repaired summary.py  (the object under test)
  summary_regression/frozen_control/ the FROZEN summary.py    (a control: it must reproduce
                                     the archived summary.json from the copied input, which
                                     is what proves the copy and the invocation are faithful
                                     and that every later difference is the repair's)

Three comparisons are then recorded:
  1. repaired vs the validator's independent reduction v3_reduce.json, per-cell values;
  2. frozen summary.py over the copy vs the archived summary.json (the control above);
  3. repaired vs the archived summary.json, EVERY difference classified as a declared D3
     site, a new reporting field, or UNEXPLAINED.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys

from common import CODE, FROZEN_CODE, FROZEN_RUN, LOGS, REVIEW, RUN_DIR, emit, host_state

BASE = RUN_DIR / "summary_regression"

# Keys that the repaired reduction adds by design. Anything outside this set that differs
# from the frozen summary.json is reported as UNEXPLAINED rather than absorbed.
NEW_REPORTING_KEYS = {"evaluated", "reason", "unevaluable", "n_clauses", "n_evaluated",
                      "cryptominisat5_pure_cnf_wall_s", "wdsat_default_wall_s", "S", "U"}
DECLARED_D3_SITES = {
    "D3a_pure_cnf_ratio": "predictions/P3/cells/*/cms_pure_cnf_over_wdsat/ratio",
    "D3b_p5_groebner_clause": "predictions/P5/cells/*/m2_S_over_U_cpu",
    "D3b_unevaluated_clause_visible": "predictions/*/cells/* newly present with evaluated=false",
    "D3c_top_level_holds_null": "predictions/*/holds",
}


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def prepare(sub: str) -> "object":
    d = BASE / sub
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FROZEN_RUN / "results.jsonl", d / "results.jsonl")
    return d


def run_reduction(code_dir, work_dir, tag):
    argv = [sys.executable, str(code_dir / "summary.py"), str(work_dir)]
    p = subprocess.run(argv, capture_output=True, text=True, timeout=600)
    (LOGS / f"{tag}.out").write_text(p.stdout)
    (LOGS / f"{tag}.err").write_text(p.stderr)
    return {"argv": argv, "returncode": p.returncode, "stdout": p.stdout[-2000:],
            "stderr_tail": p.stderr[-2000:]}


def flatten(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flatten(v, f"{prefix}/{k}" if prefix else str(k)))
    elif isinstance(obj, list):
        out[prefix] = json.dumps(obj, sort_keys=True, default=str)
    else:
        out[prefix] = obj
    return out


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-9
    return a == b


def classify(path, frozen_val, repaired_val):
    leaf = path.split("/")[-1]
    if leaf in NEW_REPORTING_KEYS:
        return "new_reporting_field"
    if path.startswith("predictions/P3/cells/") and path.endswith("cms_pure_cnf_over_wdsat/ratio"):
        return "D3a_pure_cnf_ratio"
    if path.startswith("predictions/P5/cells/") and "m2_S_over_U_cpu" in path:
        return "D3b_p5_groebner_clause"
    if path.endswith("/holds") and path.count("/") == 2:
        return "D3c_top_level_holds_null"
    if path in ("predictions/P2/holds", "predictions/P3/holds", "predictions/P4/holds",
                "predictions/P5/holds", "predictions/P6/holds"):
        return "D3c_top_level_holds_null"
    if leaf == "holds" and (frozen_val is None or repaired_val is None):
        return "D3bc_clause_holds_now_explicitly_unevaluated"
    if leaf == "note":
        return "new_reporting_field"
    return "UNEXPLAINED"


def main():
    out = {"host_at_start": host_state(),
           "frozen_input": {
               "path": str((FROZEN_RUN / "results.jsonl").relative_to(RUN_DIR.parents[3])),
               "sha256": sha256(FROZEN_RUN / "results.jsonl")},
           "frozen_summary_json_sha256": sha256(FROZEN_RUN / "summary.json")}

    rep_dir = prepare("repaired")
    fro_dir = prepare("frozen_control")
    out["input_copies_byte_identical"] = {
        "repaired": sha256(rep_dir / "results.jsonl") == out["frozen_input"]["sha256"],
        "frozen_control": sha256(fro_dir / "results.jsonl") == out["frozen_input"]["sha256"]}

    out["repaired_reduction"] = run_reduction(CODE, rep_dir, "sumreg_repaired")
    out["frozen_reduction_control"] = run_reduction(FROZEN_CODE, fro_dir, "sumreg_frozen_control")

    frozen_archived = json.loads((FROZEN_RUN / "summary.json").read_text())
    frozen_rerun = json.loads((fro_dir / "summary.json").read_text())
    repaired = json.loads((rep_dir / "summary.json").read_text())
    validator = json.loads((REVIEW / "v3_reduce.json").read_text())

    # --- control: the frozen reduction over the copied input reproduces the archived file
    fa, fr = flatten(frozen_archived), flatten(frozen_rerun)
    ctrl_diffs = [{"where": k, "archived": fa.get(k, "MISSING"), "rerun": fr.get(k, "MISSING")}
                  for k in sorted(set(fa) | set(fr)) if not same(fa.get(k, "MISSING"), fr.get(k, "MISSING"))]
    out["control_frozen_code_reproduces_archived_summary"] = {
        "n_leaf_values_compared": len(set(fa) | set(fr)),
        "n_differences": len(ctrl_diffs), "differences": ctrl_diffs[:40]}

    # --- comparison 1: repaired per-cell values vs the validator's independent reduction
    vc, rc = validator["cells"], repaired["cells"]
    checks = {"shared_keys_all": [], "shared_keys_numeric_nonnull": [], "numeric_in_validator": []}
    disagreements = []
    for cell in rc:
        for lab in rc[cell]:
            for k, v in rc[cell][lab].items():
                if k not in vc.get(cell, {}).get(lab, {}):
                    continue
                w = vc[cell][lab][k]
                ok = same(v, w)
                checks["shared_keys_all"].append(ok)
                if isinstance(w, (int, float)) and not isinstance(w, bool):
                    checks["shared_keys_numeric_nonnull"].append(ok)
                if not ok:
                    disagreements.append({"where": f"cells/{cell}/{lab}/{k}",
                                          "repaired": v, "validator": w})
    for cell in vc:
        for lab in vc[cell]:
            for k, w in vc[cell][lab].items():
                if isinstance(w, (int, float)) and not isinstance(w, bool):
                    checks["numeric_in_validator"].append(
                        k in rc.get(cell, {}).get(lab, {}) and same(rc[cell][lab][k], w))
    out["comparison_1_repaired_vs_validator_v3_reduce"] = {
        "reference_in_contract": "156 per-cell numeric values agree to the last printed digit",
        "counts_under_each_reconstructible_definition": {
            "shared_keys_of_any_type": {
                "n": len(checks["shared_keys_all"]), "n_agree": sum(checks["shared_keys_all"])},
            "shared_keys_whose_validator_value_is_a_number": {
                "n": len(checks["shared_keys_numeric_nonnull"]),
                "n_agree": sum(checks["shared_keys_numeric_nonnull"])},
            "every_numeric_value_in_v3_reduce_cells": {
                "n": len(checks["numeric_in_validator"]), "n_agree": sum(checks["numeric_in_validator"])}},
        "disagreements": disagreements,
        "note": ("the contract's count of 156 is not reconstructible from v3_reduce.json;"
                 " every reconstructible count is reported instead of choosing one, and the"
                 " frozen reference is not adjusted")}

    # --- comparison 2: the four l = 6 pure-CNF ratios (D3a)
    l6 = {}
    for k, v in repaired["predictions"]["P3"]["cells"].items():
        if k.endswith("cms_pure_cnf_over_wdsat"):
            l6[k] = v.get("ratio")
    frozen_l6 = {k: v.get("ratio") for k, v in frozen_archived["predictions"]["P3"]["cells"].items()
                 if k.endswith("cms_pure_cnf_over_wdsat")}
    val_l6 = {k: v["ratio_vs_all10"] for k, v in validator["predictions"]["P3c"]["cells"].items()}
    val_l6_matched = {k: v["ratio_matched"] for k, v in validator["predictions"]["P3c"]["cells"].items()}
    out["comparison_2_l6_pure_cnf_ratios"] = {
        "repaired": l6, "frozen_summary_json": frozen_l6,
        "validator_all10_median_form": val_l6,
        "validator_matched_subset_form": val_l6_matched,
        "repaired_values_distinct": len(set(l6.values())) == len(l6),
        "frozen_values_distinct": len(set(frozen_l6.values())) == len(frozen_l6),
        "reference_all10": [10.396, 34.472, 67.460, 83.500],
        "repaired_rounded_sorted": sorted(round(v, 3) for v in l6.values() if v is not None)}

    # --- comparison 3: P5 Groebner clause and P6 unevaluable
    p5 = repaired["predictions"]["P5"]
    p6 = repaired["predictions"]["P6"]
    out["comparison_3_uniform_reporting"] = {
        "P5_groebner_clauses": {k: v for k, v in p5["cells"].items() if "m2_S_over_U_cpu" in k},
        "P5_unevaluable": p5["unevaluable"], "P5_holds": p5["holds"],
        "P5_holds_frozen": frozen_archived["predictions"]["P5"]["holds"],
        "P6_unevaluable": p6["unevaluable"], "P6_holds": p6["holds"],
        "P6_holds_frozen": frozen_archived["predictions"]["P6"]["holds"],
        "P4_unevaluable": repaired["predictions"]["P4"]["unevaluable"],
        "P4_holds": repaired["predictions"]["P4"]["holds"],
        "P4_holds_frozen": frozen_archived["predictions"]["P4"]["holds"],
        "P2_unevaluable": repaired["predictions"]["P2"]["unevaluable"],
        "P2_holds": repaired["predictions"]["P2"]["holds"],
        "P2_holds_frozen": frozen_archived["predictions"]["P2"]["holds"],
        "P3_unevaluable": repaired["predictions"]["P3"]["unevaluable"],
        "P3_holds": repaired["predictions"]["P3"]["holds"],
        "P3_holds_frozen": frozen_archived["predictions"]["P3"]["holds"],
        "P1_holds": repaired["predictions"]["P1"]["holds"],
        "P1_holds_frozen": frozen_archived["predictions"]["P1"]["holds"]}

    # --- comparison 4: every difference from the archived summary.json, classified
    ra = flatten(repaired)
    all_keys = sorted(set(fa) | set(ra))
    diffs = []
    for k in all_keys:
        a, b = fa.get(k, "ABSENT"), ra.get(k, "ABSENT")
        if same(a, b):
            continue
        diffs.append({"where": k, "frozen": a, "repaired": b, "class": classify(k, a, b)})
    by_class = {}
    for d in diffs:
        by_class.setdefault(d["class"], []).append(d["where"])
    out["comparison_4_repaired_vs_frozen_summary_json"] = {
        "n_leaf_values_compared": len(all_keys), "n_differences": len(diffs),
        "differences_by_class": {k: {"n": len(v), "where": v} for k, v in sorted(by_class.items())},
        "unexplained_differences": [d for d in diffs if d["class"] == "UNEXPLAINED"],
        "differences": diffs}

    # --- the fix boundary: no median, ratio or threshold moved where both sides evaluated it
    moved = []
    for k in all_keys:
        if not k.startswith("cells/"):
            continue
        a, b = fa.get(k, "ABSENT"), ra.get(k, "ABSENT")
        if not same(a, b):
            moved.append({"where": k, "frozen": a, "repaired": b})
    out["fix_boundary_cells_block_unchanged"] = {"n_moved": len(moved), "moved": moved}

    out["host_at_end"] = host_state()
    (RUN_DIR / "summary_regression.json").write_text(json.dumps(out, indent=1, default=str))
    emit("sumreg", {k: out[k] for k in
                    ("host_at_start", "input_copies_byte_identical",
                     "control_frozen_code_reproduces_archived_summary",
                     "comparison_1_repaired_vs_validator_v3_reduce",
                     "comparison_2_l6_pure_cnf_ratios", "comparison_3_uniform_reporting",
                     "fix_boundary_cells_block_unchanged")})
    print("n_differences vs frozen summary.json:",
          out["comparison_4_repaired_vs_frozen_summary_json"]["n_differences"],
          "unexplained:", len(out["comparison_4_repaired_vs_frozen_summary_json"]["unexplained_differences"]))


if __name__ == "__main__":
    main()
