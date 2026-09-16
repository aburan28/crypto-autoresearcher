#!/usr/bin/env python3
"""Validator's own R3 comparisons. Reads only: frozen results.jsonl copy, my scratch
summary.json outputs, the two v3_reduce.json files and the archived frozen summary.json."""
import json, statistics, sys
from pathlib import Path

R3 = Path("/tmp/val3f4b52/r3")
REV = Path("/workspace/coordination/review/icperf-20260913-66fd51/TASK-20260913-6c5729")
FROZEN_SUMMARY = Path("/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3/summary.json")

rep = json.load(open(R3 / "repaired/summary.json"))
fro = json.load(open(R3 / "frozen/summary.json"))
fro_archived = json.load(open(FROZEN_SUMMARY))
assert fro == fro_archived, "frozen control differs from archived summary.json"
v3_art = json.load(open(REV / "artifacts/v3_reduce.json"))
v3_work = json.load(open(REV / "work/v3_reduce.json"))

out = {}

# ---------------------------------------------------------------- (a) the 156 definition
ALIAS = {"cms_xor": "cryptominisat5/cnf_xor", "cms_pure_cnf": "cryptominisat5/pure_cnf",
         "m2_f4": "macaulay2/f4", "singular": "singular/std",
         "cadical_pure_cnf": "cadical/pure_cnf", "minisat_pure_cnf": "minisat/pure_cnf"}

def close(a, b):
    if a is None and b is None: return True
    if a is None or b is None: return False
    if a == b: return True
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))

def celldiff_156(summary):
    """Verbatim logic of work/v3_celldiff.py against work/v3_reduce.json per_cell_table."""
    mine = v3_work["per_cell_table"]
    n_checked = n_match = 0
    mism = []; missing = []; unparsed = []
    for cell, labels in summary["cells"].items():
        for label, flat in labels.items():
            myrow = mine.get(f"{cell}/{label}", {})
            for k, v in flat.items():
                if k.endswith("_wall_s"): base, field = k[:-7], "median_wall_s"
                elif k.endswith("_conflicts"): base, field = k[:-10], "median_conflicts"
                elif k.endswith("_n"): base, field = k[:-2], "n_finished"
                else:
                    unparsed.append(f"{cell}/{label}/{k}"); continue
                mykey_ec = ALIAS.get(base) or (lambda e, _, c: f"{e}/{c}")(*base.partition("_"))
                mysub = myrow.get(mykey_ec)
                if mysub is None:
                    missing.append(f"{cell}/{label}/{k}"); continue
                mv = mysub.get(field)
                ok = close(mv, v)
                n_checked += 1; n_match += int(ok)
                if not ok: mism.append({"where": f"{cell}/{label}/{k}", "summary": v, "validator_work": mv})
    return {"n_values_checked": n_checked, "n_values_matching": n_match, "mismatches": mism,
            "keys_missing_in_validator_work_reduction": len(missing), "unparsed_keys": len(unparsed)}

out["a_156_definition_recovered"] = {
    "definition": "work/v3_celldiff.py: count of summary.json cells[*][*] keys ending _wall_s/_conflicts/_n that have a counterpart in work/v3_reduce.json per_cell_table; agreement to 1e-9 rel",
    "against_frozen_summary": celldiff_156(fro),
    "against_repaired_summary": celldiff_156(rep),
}

# ---------------------------------------------------------------- (b) artifacts/v3_reduce.json cells
def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from leaves(v, f"{p}/{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o): yield from leaves(v, f"{p}[{i}]")
    else: yield p, o

isnum = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
art_cells = dict(leaves(v3_art["cells"]))
rep_cells = dict(leaves(rep["cells"]))
fro_cells = dict(leaves(fro["cells"]))
shared = sorted(set(art_cells) & set(rep_cells))
shared_num = [p for p in shared if isnum(art_cells[p])]
agree_any = sum(1 for p in shared if close(art_cells[p], rep_cells[p]) if isnum(art_cells[p]) or art_cells[p] == rep_cells[p])
agree_any = sum(1 for p in shared if (close(art_cells[p], rep_cells[p]) if (isnum(art_cells[p]) and isnum(rep_cells[p])) else art_cells[p] == rep_cells[p]))
agree_num = sum(1 for p in shared_num if isnum(rep_cells[p]) and close(art_cells[p], rep_cells[p]))
art_num_all = [p for p in art_cells if isnum(art_cells[p])]
out["b_artifacts_v3_reduce_cells"] = {
    "shared_keys_any_type": f"{agree_any}/{len(shared)}",
    "shared_keys_numeric_in_validator": f"{agree_num}/{len(shared_num)}",
    "numeric_values_in_validator_cells": len(art_num_all),
    "validator_numeric_without_counterpart": len([p for p in art_num_all if p not in rep_cells]),
    "disagreements": [{"where": p, "validator": art_cells[p], "repaired": rep_cells[p]} for p in shared
                      if not ((close(art_cells[p], rep_cells[p]) if (isnum(art_cells[p]) and isnum(rep_cells[p])) else art_cells[p] == rep_cells[p]))],
}

# ---------------------------------------------------------------- (c) cells block unchanged frozen -> repaired
out["c_cells_block_frozen_vs_repaired"] = {
    "n_leaves_frozen": len(fro_cells), "n_leaves_repaired": len(rep_cells),
    "identical": fro["cells"] == rep["cells"],
    "moved": [p for p in set(fro_cells) | set(rep_cells) if fro_cells.get(p, "ABSENT") != rep_cells.get(p, "ABSENT")],
}

# ---------------------------------------------------------------- (d) leaf diff with MY attribution
fl = dict(leaves(fro)); rl = dict(leaves(rep))
NEW_FIELDS = {"evaluated", "reason", "unevaluable", "n_clauses", "n_evaluated"}
NEW_P3_CMS_FIELDS = {"cryptominisat5_pure_cnf_wall_s", "wdsat_default_wall_s"}
diffs = []
for p in sorted(set(fl) | set(rl)):
    a, b = fl.get(p, "ABSENT"), rl.get(p, "ABSENT")
    if a == b and type(a) == type(b): continue
    if isnum(a) and isnum(b) and close(a, b): continue
    parts = p.strip("/").split("/")
    last = parts[-1]
    field = last.partition("[")[0]  # leaves() emits list elements as `<field>[i]`
    cls = "UNATTRIBUTED"
    if field in NEW_FIELDS: cls = "new_reporting_field (D3b/c)"
    elif p.startswith("/predictions/P3/cells") and "cms_pure_cnf_over_wdsat" in p:
        if last == "ratio" and a != "ABSENT": cls = "D3a loop-variable leak (ratio corrected)"
        elif last == "holds": cls = "D3a (holds recomputed from corrected ratio)"
        elif last in NEW_P3_CMS_FIELDS: cls = "new_reporting_field (D3a names the two rows a ratio is formed from)"
    elif p.startswith("/predictions/P5/cells") and "m2_S_over_U_cpu" in p and a == "ABSENT":
        cls = "D3b P5 Groebner clause now recorded as unevaluated"
    elif p.startswith("/predictions/P5/cells") and last in {"S", "U"} and a == "ABSENT":
        cls = "new_reporting_field (D3b names the two medians a ratio is formed from)"
    elif p.startswith("/predictions/P2/cells") and a == "ABSENT":
        cls = "D3b P2 clause now recorded as unevaluated (frozen P2.cells was {})"
    elif p in ("/predictions/P5/holds", "/predictions/P6/holds"):
        cls = "D3b/c top-level holds true -> null"
    elif p.startswith("/predictions/P6/") and last == "note": cls = "new_reporting_field (note text)"
    elif p.startswith("/predictions/P2/") and last == "note": cls = "new_reporting_field (note text)"
    elif p.startswith("/predictions/P4/cells") and last == "note" and b == "ABSENT": cls = "D3c P4 note moved into reason field"
    diffs.append({"where": p, "frozen": a, "repaired": b, "class": cls})
by = {}
for d in diffs: by.setdefault(d["class"], []).append(d["where"])
out["d_leaf_diff_my_attribution"] = {
    "n_leaves_frozen": len(fl), "n_leaves_repaired": len(rl), "n_differences": len(diffs),
    "by_class_counts": {k: len(v) for k, v in by.items()},
    "unattributed": [d for d in diffs if d["class"] == "UNATTRIBUTED"],
    "frozen_P2_cells": fro["predictions"]["P2"]["cells"],
    "twelve_ratio_none": [d for d in diffs if d["where"].startswith("/predictions/P2/cells") and d["where"].endswith("/ratio")],
}

# ---------------------------------------------------------------- (e) l=6 pure-CNF ratios: all-10 form from repaired, matched subset from raw rows
rows = [json.loads(l) for l in open(R3 / "repaired/results.jsonl") if l.strip()]
def finished(r):
    s = r.get("status", ""); return not (s.startswith("budget_stop") or s.startswith("infrastructure") or s == "unknown")
def med(xs):
    xs = [x for x in xs if x is not None]; return statistics.median(xs) if xs else None
ratios = {}
for cell in ("n17l6", "n19l6"):
    for lab in ("S", "U"):
        rep_r = rep["predictions"]["P3"]["cells"][f"{cell}/{lab}/cms_pure_cnf_over_wdsat"]["ratio"]
        fro_r = fro["predictions"]["P3"]["cells"][f"{cell}/{lab}/cms_pure_cnf_over_wdsat"]["ratio"]
        cms = [r for r in rows if r.get("engine") == "cryptominisat5" and r.get("config") == "pure_cnf" and r.get("cell") == cell and r.get("label") == lab and finished(r)]
        wd_all = [r for r in rows if r.get("engine") == "wdsat" and r.get("config") == "default" and r.get("cell") == cell and r.get("label") == lab and finished(r)]
        stems = {r["instance"] for r in cms}
        wd_matched = [r for r in wd_all if r["instance"] in stems]
        all10 = med([r["wall_s"] for r in cms]) / med([r["wall_s"] for r in wd_all])
        matched = med([r["wall_s"] for r in cms]) / med([r["wall_s"] for r in wd_matched])
        ratios[f"{cell}/{lab}"] = {"repaired_summary": rep_r, "frozen_summary": fro_r,
                                   "my_all10_from_rows": all10, "my_matched_subset_from_rows": matched,
                                   "n_cms": len(cms), "n_wdsat_all": len(wd_all), "n_wdsat_matched": len(wd_matched)}
out["e_l6_pure_cnf_ratios"] = ratios
out["e_reference_all10"] = [10.396, 34.472, 67.460, 83.500]
out["e_reference_matched"] = [26.071, 34.468, 327.664, 82.629]

# ---------------------------------------------------------------- (f) uniform reporting on the as-is input
def pred_summary(P):
    return {k: {"holds": v.get("holds"), "unevaluable": v.get("unevaluable"), "n_clauses": v.get("n_clauses"),
                "n_evaluated": v.get("n_evaluated")} for k, v in P.items()}
out["f_predictions_repaired"] = pred_summary(rep["predictions"])
out["f_predictions_frozen_holds"] = {k: v.get("holds") for k, v in fro["predictions"].items()}
p5 = rep["predictions"]["P5"]["cells"]
out["f_P5_groebner_clauses"] = {k: v for k, v in p5.items() if k.endswith("m2_S_over_U_cpu")}
out["f_P6"] = rep["predictions"]["P6"]

json.dump(out, open(R3 / "compare_out.json", "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items() if k not in ("f_P5_groebner_clauses", "f_P6", "d_leaf_diff_my_attribution")}, indent=1, default=str))
d = out["d_leaf_diff_my_attribution"]
print(json.dumps({k: d[k] for k in ("n_leaves_frozen", "n_leaves_repaired", "n_differences", "by_class_counts", "unattributed", "frozen_P2_cells")}, indent=1))
print("twelve ratio None sample:", d["twelve_ratio_none"][:2])
print(json.dumps(out["f_P5_groebner_clauses"], indent=1)[:1500])
print(json.dumps(out["f_P6"], indent=1)[:1500])
