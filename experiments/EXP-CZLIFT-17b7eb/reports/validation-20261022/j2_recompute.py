#!/usr/bin/env python3
"""J2: validator's own recomputation of every frozen metric from raw-result.json.

Written for TASK-20261022-282b02 from the metric definitions in
experiments/EXP-CZLIFT-17b7eb/specification.yaml and ledger/hypotheses/H-CZLIFT-889c9d.yaml,
BEFORE reading implementation/check.py. Flags are recomputed from the recorded
valuations (vP, v_dj, e) and compared with the stored booleans; nothing is copied
from the manifest. Usage: j2_recompute.py <run_dir> [<run_dir> ...] > out.json
"""
import json
import math
import sys
from collections import Counter, defaultdict

CLASSES = ["canonical", "isomorphic", "pert_p", "pert_p2"]
SECTIONS = ["hensel_random", "naive", "teichmuller"]


def recompute(run_dir):
    raw = json.load(open(f"{run_dir}/raw-result.json"))
    curves = raw["raw"]["curves"]
    n = 0
    flag_mismatch = Counter()
    rule_dis = []
    nondeg = nondeg_succ = 0
    nondeg_vq_ne = 0
    deg = 0
    deg_def = deg_succ = 0
    inv_p = 0.0
    var_sum = 0.0
    deg_undef_reasons = Counter()
    deg_def_reason_mismatch = Counter()
    by_class = {c: Counter() for c in CLASSES}
    by_sec = {s: {"n": 0, "success": 0, "inv_p_sum": 0.0} for s in SECTIONS}
    per_curve_canon = {}
    per_curve_class = defaultdict(lambda: Counter())
    pert_p_degenerate_rows = defaultdict(Counter)
    vdj_by_class = defaultdict(Counter)
    vp_hist_by_class = defaultdict(Counter)
    succ_but_undefined = 0
    for c in curves:
        p, e = c["p"], c["e"]
        prec = c["precision"]
        canon_deg = canon_n = 0
        for r in c["rows"]:
            n += 1
            cls, sec = r["class"], r["section"]
            vP, vQ, vdj = r["vP"], r["vQ"], r["v_dj"]
            my_deg = vP >= 2
            my_pred = vdj >= 2 * e
            if my_deg != r["degenerate"]:
                flag_mismatch["degenerate"] += 1
            if my_pred != r["predicted_degenerate"]:
                flag_mismatch["predicted_degenerate"] += 1
            my_def = (vP == vQ)
            if my_def != r["ratio_defined"]:
                deg_def_reason_mismatch[(vP, vQ, r["ratio_defined"])] += 1
            if r["success"] and not r["ratio_defined"]:
                succ_but_undefined += 1
            if my_deg != my_pred:
                rule_dis.append({"D": c["D"], "p": p, "class": cls, "section": sec,
                                 "vP": vP, "v_dj": vdj})
            vdj_by_class[cls][vdj] += 1
            vp_hist_by_class[cls][vP] += 1
            b = by_class[cls]
            b["n"] += 1
            b["degenerate"] += int(my_deg)
            b["predicted_degenerate"] += int(my_pred)
            b["ratio_defined"] += int(r["ratio_defined"])
            b["success"] += int(bool(r["success"]))
            per_curve_class[(c["D"], p, cls)]["n"] += 1
            per_curve_class[(c["D"], p, cls)]["deg"] += int(my_deg)
            per_curve_class[(c["D"], p, cls)]["succ"] += int(bool(r["success"]))
            if cls == "canonical":
                canon_n += 1
                canon_deg += int(my_deg)
            if cls == "pert_p" and my_deg:
                pert_p_degenerate_rows[(c["D"], p)][(sec, vP, vQ, vdj, r["success"])] += 1
            if vP == 1:
                nondeg += 1
                nondeg_succ += int(bool(r["success"]))
                nondeg_vq_ne += int(vQ != 1)
            else:
                deg += 1
                if r["ratio_defined"]:
                    deg_def += 1
                    deg_succ += int(bool(r["success"]))
                    inv_p += 1.0 / p
                    var_sum += (1.0 / p) * (1 - 1.0 / p)
                    by_sec[sec]["n"] += 1
                    by_sec[sec]["success"] += int(bool(r["success"]))
                    by_sec[sec]["inv_p_sum"] += 1.0 / p
                else:
                    deg_undef_reasons[(vP, vQ, vP >= prec or vQ >= prec)] += 1
        per_curve_canon[f"{c['D']}:{p}"] = (canon_deg, canon_n)
    rate = deg_succ / deg_def
    ref = inv_p / deg_def
    z_pooled = (rate - ref) / math.sqrt(ref * (1 - ref) / deg_def)
    z_hetero = (deg_succ - inv_p) / math.sqrt(var_sum)
    out = {
        "run_dir": run_dir,
        "seed": raw["metrics"]["seed"],
        "curves": len(curves),
        "curve_list": [[c["D"], c["p"]] for c in curves],
        "samples_total": n,
        "flag_mismatches_vs_recomputed": dict(flag_mismatch),
        "ratio_defined_flag_vs_vP_eq_vQ_mismatch": {str(k): v for k, v in deg_def_reason_mismatch.items()},
        "success_but_ratio_undefined": succ_but_undefined,
        "rule_disagreements": len(rule_dis),
        "rule_disagreement_rows": rule_dis[:20],
        "rule_agreement": 1 - len(rule_dis) / n,
        "nondegenerate_samples": nondeg,
        "nondegenerate_successes": nondeg_succ,
        "nondegenerate_success_rate": nondeg_succ / nondeg,
        "nondegenerate_with_vQ_ne_1": nondeg_vq_ne,
        "degenerate_samples_all": deg,
        "degenerate_ratio_defined_samples": deg_def,
        "degenerate_ratio_undefined_by_(vP,vQ,at_cap)": {str(k): v for k, v in deg_undef_reasons.items()},
        "degenerate_successes": deg_succ,
        "degenerate_success_rate": rate,
        "degenerate_reference_inv_p": ref,
        "degenerate_z_score_pooled_binomial": z_pooled,
        "degenerate_z_score_heterogeneous_binomial": z_hetero,
        "by_class": {k: {**dict(v),
                         "frac_degenerate": v["degenerate"] / v["n"],
                         "frac_predicted_degenerate": v["predicted_degenerate"] / v["n"],
                         "success_rate": v["success"] / v["n"]} for k, v in by_class.items()},
        "degenerate_by_section": {s: {**v,
                                      "degenerate_success_rate": v["success"] / v["n"],
                                      "reference_inv_p": v["inv_p_sum"] / v["n"],
                                      "z_heterogeneous": None} for s, v in by_sec.items()},
        "canonical_frac_degenerate_every_curve": all(a == b for a, b in per_curve_canon.values()),
        "canonical_per_curve": per_curve_canon,
        "pert_p_degenerate_rows": {f"{k[0]}:{k[1]}": {str(kk): vv for kk, vv in v.items()}
                                   for k, v in pert_p_degenerate_rows.items()},
        "v_dj_hist_by_class": {k: dict(sorted(v.items())) for k, v in vdj_by_class.items()},
        "vP_hist_by_class": {k: dict(sorted(v.items())) for k, v in vp_hist_by_class.items()},
        "rows_per_curve_class": sorted({(k[2], v["n"]) for k, v in per_curve_class.items()}),
        "pert_p_per_curve_success": {f"{k[0]}:{k[1]}": [v["succ"], v["deg"], v["n"]]
                                     for k, v in per_curve_class.items() if k[2] == "pert_p"
                                     and v["succ"] != v["n"]},
    }
    # per-section heterogeneous z, recomputed from rows
    for s in SECTIONS:
        num = 0
        var = 0.0
        exp_ = 0.0
        for c in curves:
            p = c["p"]
            for r in c["rows"]:
                if r["section"] == s and r["vP"] >= 2 and r["ratio_defined"]:
                    num += int(bool(r["success"]))
                    exp_ += 1.0 / p
                    var += (1.0 / p) * (1 - 1.0 / p)
        out["degenerate_by_section"][s]["z_heterogeneous"] = (num - exp_) / math.sqrt(var)
    return out


def compare(mine, run_dir):
    man = json.load(open(f"{run_dir}/raw-result.json"))["metrics"]
    diffs = []

    def chk(key, a, b, tol=1e-12):
        if isinstance(a, float) or isinstance(b, float):
            ok = abs(a - b) <= tol
        else:
            ok = a == b
        if not ok:
            diffs.append({"key": key, "validator": a, "recorded": b})

    for k in ["samples_total", "rule_disagreements", "nondegenerate_samples",
              "degenerate_ratio_defined_samples", "curves"]:
        chk(k, mine[k], man[k])
    for k in ["rule_agreement", "nondegenerate_success_rate", "degenerate_success_rate",
              "degenerate_reference_inv_p"]:
        chk(k, mine[k], man[k])
    chk("curve_list", mine["curve_list"], man["curve_list"])
    for cls in CLASSES:
        for k, v in man["by_class"][cls].items():
            chk(f"by_class.{cls}.{k}", mine["by_class"][cls][k], v)
    for s in SECTIONS:
        for k, v in man["degenerate_by_section"][s].items():
            chk(f"degenerate_by_section.{s}.{k}", mine["degenerate_by_section"][s][k], v, 1e-9)
    zmatch = {
        "pooled": abs(mine["degenerate_z_score_pooled_binomial"] - man["degenerate_z_score"]) < 1e-9,
        "heterogeneous": abs(mine["degenerate_z_score_heterogeneous_binomial"] - man["degenerate_z_score"]) < 1e-9,
    }
    return {"diffs": diffs, "z_recorded": man["degenerate_z_score"], "z_form_matching": zmatch}


if __name__ == "__main__":
    res = {}
    for rd in sys.argv[1:]:
        m = recompute(rd)
        m["comparison_with_recorded_metrics"] = compare(m, rd)
        res[rd.rstrip("/").split("/")[-1]] = m
    print(json.dumps(res, indent=1, default=str))
