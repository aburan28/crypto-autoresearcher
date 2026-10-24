#!/usr/bin/env python3
"""J2 recomputation for EXP-CZLIFT-7c8d73 (validator TASK-20261022-d7d57f).

Written from the specification / hypothesis definitions BEFORE reading check.py.
Reads only raw-result.json and manifest.yaml of each run (paths given on argv).

Definitions used (from the specification and H-CZLIFT-d3dc4b statement):
  series split flag     S  := v_p(lambda) >= 2          (lambda = log_F(z([p]P^)))
  j-distance rule       R  := v_p(j(E^) - j_can) >= 2e
  rule_agreement        := #(S == R) / #samples
  construction_verified_rate := #(verified) / #(S)            [hypothesis: whenever v_p(lambda) >= 2 ...]
  construction_reduces_rate  := #(reduces)  / #(S)
  nonsplit_with_construction := #(v_p(lambda) == 1 and constructed)   [hypothesis: 'when v_p(lambda) = 1 no
                                such lift is constructed']
  control C1 (as written): 'pert_p (non-split) must never yield a construction; canonical, isomorphic and
                            pert_p2 must always.'  evaluated literally on the class label.
Alternative denominators/definitions are computed too and reported side by side.
"""
import json
import sys
from collections import Counter, defaultdict

out = {}
for run_dir in sys.argv[1:]:
    raw = json.load(open(f"{run_dir}/raw-result.json"))
    man = raw["metrics"]
    curves = raw["raw"]["curves"]
    rows = []
    for c in curves:
        for i, r in enumerate(c["rows"]):
            rows.append(dict(r, p=c["p"], D=c["D"], e=c["e"], A=c["A"], B=c["B"], prec=c["precision"], idx=i))
    n = len(rows)
    res = {"samples_total": n, "curves": len(curves)}

    # internal consistency of stored flags with their definitions
    S_def = [r["v_log"] >= 2 for r in rows]
    R_def = [r["v_dj"] >= 2 * r["e"] for r in rows]
    res["flag_split_equals_vlog_ge_2"] = sum(r["split"] == s for r, s in zip(rows, S_def))
    res["flag_predicted_equals_vdj_ge_2e"] = sum(r["predicted_split"] == q for r, q in zip(rows, R_def))
    res["constructed_equals_split_flag"] = sum(r["constructed"] == r["split"] for r in rows)
    res["verified_implies_constructed"] = sum((not r["verified"]) or r["constructed"] for r in rows)
    res["reduces_implies_constructed"] = sum((not r["reduces"]) or r["constructed"] for r in rows)

    S = S_def
    R = R_def
    agree = sum(s == q for s, q in zip(S, R))
    res["rule_agreement"] = agree / n
    res["rule_disagreements"] = n - agree
    split_n = sum(S)
    res["split_samples"] = split_n
    ver_on_split = sum(r["verified"] for r, s in zip(rows, S) if s)
    red_on_split = sum(r["reduces"] for r, s in zip(rows, S) if s)
    res["construction_verified_rate"] = ver_on_split / split_n
    res["construction_reduces_rate"] = red_on_split / split_n
    constructed_n = sum(r["constructed"] for r in rows)
    res["alt_verified_over_constructed"] = sum(r["verified"] for r in rows if r["constructed"]) / constructed_n
    res["alt_verified_over_rule_split"] = sum(r["verified"] for r, q in zip(rows, R) if q) / sum(R)
    res["nonsplit_with_construction(v_log==1 & constructed)"] = sum(
        1 for r in rows if r["v_log"] == 1 and r["constructed"])
    res["alt_nonsplit_with_construction(not S & constructed)"] = sum(
        1 for r, s in zip(rows, S) if (not s) and r["constructed"])
    res["alt_nonsplit_with_construction(not R & constructed)"] = sum(
        1 for r, q in zip(rows, R) if (not q) and r["constructed"])
    res["alt_nonsplit_with_construction(class pert_p & constructed)"] = sum(
        1 for r in rows if r["class"] == "pert_p" and r["constructed"])

    by = defaultdict(lambda: Counter())
    for r, s in zip(rows, S):
        b = by[r["class"]]
        b["n"] += 1
        b["split"] += s
        b["verified"] += r["verified"]
        b["constructed"] += r["constructed"]
        b["reduces"] += r["reduces"]
    res["by_class"] = {k: dict(v, frac_split=v["split"] / v["n"]) for k, v in by.items()}

    # control C1 literally
    c1_pert_p_constructions = [(r["p"], r["D"], r["idx"], r["v_log"], r["v_dj"]) for r in rows
                               if r["class"] == "pert_p" and r["constructed"]]
    c1_others_missing = [(r["p"], r["class"], r["idx"]) for r in rows
                         if r["class"] != "pert_p" and not r["constructed"]]
    res["C1_pert_p_with_construction"] = len(c1_pert_p_constructions)
    res["C1_pert_p_with_construction_rows"] = c1_pert_p_constructions
    res["C1_split_classes_without_construction"] = len(c1_others_missing)

    # distributions for borderline probing
    res["v_log_hist"] = dict(sorted(Counter(r["v_log"] for r in rows).items()))
    res["v_dj_hist_by_e"] = {e: dict(sorted(Counter(r["v_dj"] for r in rows if r["e"] == e).items()))
                             for e in sorted({r["e"] for r in rows})}
    res["v_dj_minus_2e_hist"] = dict(sorted(Counter(r["v_dj"] - 2 * r["e"] for r in rows).items()))
    res["v_log_by_class"] = {k: dict(sorted(Counter(r["v_log"] for r in rows if r["class"] == k).items()))
                             for k in sorted(by)}
    res["v_dj_by_class_and_e"] = {f"{k}/e={e}": dict(sorted(Counter(r["v_dj"] for r in rows
                                                                    if r["class"] == k and r["e"] == e).items()))
                                  for k in sorted(by) for e in sorted({r["e"] for r in rows})}
    res["v_log_at_cap(prec)"] = sum(r["v_log"] >= r["prec"] for r in rows)
    res["v_log_eq_0"] = sum(r["v_log"] <= 0 for r in rows)
    res["v_dj_eq_2e_exactly"] = sum(r["v_dj"] == 2 * r["e"] for r in rows)
    res["v_dj_eq_2e_minus_1"] = sum(r["v_dj"] == 2 * r["e"] - 1 for r in rows)
    res["rows_per_curve"] = dict(Counter(Counter((r["p"], r["D"]) for r in rows).values()))
    res["rows_per_curve_class"] = dict(Counter(Counter((r["p"], r["D"], r["class"]) for r in rows).values()))
    res["duplicate_curves(p,D)"] = [k for k, v in Counter((c["p"], c["D"]) for c in curves).items() if v > 1]
    res["precision_field"] = sorted({c["precision"] for c in curves})

    # compare with recorded metrics
    cmp = {}
    for k in ["samples_total", "rule_agreement", "rule_disagreements", "split_samples",
              "construction_verified_rate", "construction_reduces_rate", "curves"]:
        cmp[k] = {"recomputed": res[k], "recorded": man.get(k), "equal": res[k] == man.get(k)}
    cmp["nonsplit_with_construction"] = {
        "recomputed": res["nonsplit_with_construction(v_log==1 & constructed)"],
        "recorded": man["nonsplit_with_construction"],
        "equal": res["nonsplit_with_construction(v_log==1 & constructed)"] == man["nonsplit_with_construction"]}
    for k, v in man["by_class"].items():
        mine = res["by_class"][k]
        cmp[f"by_class.{k}"] = {"recomputed": {x: mine[x] for x in ("n", "split", "verified", "frac_split")},
                                "recorded": v,
                                "equal": all(mine[x] == v[x] for x in ("n", "split", "verified", "frac_split"))}
    res["comparison_with_recorded_metrics"] = cmp
    out[run_dir.rstrip("/").split("/")[-1]] = res

json.dump(out, sys.stdout, indent=1, default=str)
print()
