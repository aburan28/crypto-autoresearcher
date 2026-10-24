#!/usr/bin/env python3
"""J2: independent recomputation of the frozen metrics of EXP-CZLIFT-f5e06c from raw-result.json.

Written from the specification's metric names, success and falsification criteria and the
hypothesis ("every success rate sits within 4 standard errors of 1/p") BEFORE reading
implementation/check.py. Definitions used:
  rule_agreement            = #(degenerate == predicted_degenerate) / #rows
  nondegenerate_success_rate= #(success and not degenerate) / #(not degenerate)
  degenerate_z_score        = (S - sum q) / sqrt(sum q(1-q)), q = 1/p, over degenerate rows with ratio_defined
  torsion rates             = mean of the per-row booleans over all torsion rows
  section identity_rate     = mean identity_holds per section per arm (and 'all')
  section z_score           = (S - sum q) / sqrt(sum q(1-q)) over rows with ratio_defined
Compares with raw-result.json 'metrics', manifest.yaml result.metrics, stdout.log.
"""
import json
import math
import os
import sys

ROOT = sys.argv[1]
EXP = "experiments/EXP-CZLIFT-f5e06c"
RUNS = ["RUN-CZLIFT-032a92", "RUN-CZLIFT-6447f0"]
SECTIONS = ["hensel_random", "naive", "teichmuller"]


def z(rows_q, succ):
    s = sum(rows_q)
    var = sum(q * (1 - q) for q in rows_q)
    return (succ - s) / math.sqrt(var) if var > 0 else None


def recompute(raw):
    m = {}
    ca, ct = raw["curves_anomalous"], raw["curves_torsion"]
    rows = [(cu["p"], r) for cu in ca for r in cu["rows"]]
    n = len(rows)
    agree = sum(r["degenerate"] == r["predicted_degenerate"] for _, r in rows)
    nd = [(p, r) for p, r in rows if not r["degenerate"]]
    dg = [(p, r) for p, r in rows if r["degenerate"] and r["ratio_defined"]]
    dg_all = [(p, r) for p, r in rows if r["degenerate"]]
    a = {
        "samples_total": n,
        "rule_agreement": agree / n,
        "rule_disagreements": n - agree,
        "nondegenerate_samples": len(nd),
        "nondegenerate_success_rate": sum(r["success"] for _, r in nd) / len(nd) if nd else None,
        "nondegenerate_ratio_undefined": sum(not r["ratio_defined"] for _, r in nd),
        "degenerate_samples_all": len(dg_all),
        "degenerate_ratio_defined_samples": len(dg),
        "degenerate_success_rate": sum(r["success"] for _, r in dg) / len(dg) if dg else None,
        "degenerate_reference_inv_p": sum(1 / p for p, _ in dg) / len(dg) if dg else None,
        "degenerate_z_score": z([1 / p for p, _ in dg], sum(r["success"] for _, r in dg)),
        "curves": len(ca),
    }
    m["anomalous"] = a
    bycls = {}
    for cls in sorted({r["class"] for _, r in rows}):
        rr = [r for _, r in rows if r["class"] == cls]
        bycls[cls] = {
            "n": len(rr),
            "degenerate": sum(r["degenerate"] for r in rr),
            "success": sum(r["success"] for r in rr),
            "ratio_defined": sum(r["ratio_defined"] for r in rr),
            "predicted_degenerate": sum(r["predicted_degenerate"] for r in rr),
            "frac_degenerate": sum(r["degenerate"] for r in rr) / len(rr),
            "frac_predicted_degenerate": sum(r["predicted_degenerate"] for r in rr) / len(rr),
            "success_rate": sum(r["success"] for r in rr) / len(rr),
        }
    m["anomalous_by_class"] = bycls
    bysec = {}
    for sec in SECTIONS:
        rr = [(p, r) for p, r in dg if r["section"] == sec]
        bysec[sec] = {"n": len(rr), "success": sum(r["success"] for _, r in rr),
                      "inv_p_sum": sum(1 / p for p, _ in rr),
                      "degenerate_success_rate": sum(r["success"] for _, r in rr) / len(rr),
                      "reference_inv_p": sum(1 / p for p, _ in rr) / len(rr)}
    m["anomalous_degenerate_by_section"] = bysec

    trows = [(cu["p"], cu["arm"], r) for cu in ct for r in cu["rows"]]
    nt = len(trows)
    rate = lambda key: sum(bool(r[key]) for _, _, r in trows) / nt
    t = {
        "pairs_total": nt,
        "canonicity_rate": rate("canonical"),
        "homomorphism_rate_torsion": rate("hom_tor"),
        "degeneracy_rate_torsion": rate("degenerate_tor"),
        "torsion_reduces_rate": rate("tor_reduces"),
        "scalar_mult_equivariance_rate": rate("scalar_mult_tor"),
        "torsion_cost_mean_additions": sum(r["tor_cost_additions"] for _, _, r in trows) / nt,
        "torsion_cost_max_additions": max(r["tor_cost_additions"] for _, _, r in trows),
    }
    m["torsion"] = t
    ts = {}
    for sec in SECTIONS:
        ts[sec] = {}
        for arm in ("all", "cm_canonical", "random_naive"):
            rr = [(p, r["sections"][sec]) for p, a_, r in trows if arm == "all" or a_ == arm]
            rd = [(p, s) for p, s in rr if s["ratio_defined"]]
            ts[sec][arm] = {
                "n": len(rr),
                "n_ratio_defined": len(rd),
                "frac_valuation_1": sum(s["vP"] == 1 and s["vQ"] == 1 for _, s in rr) / len(rr),
                "frac_vP_1": sum(s["vP"] == 1 for _, s in rr) / len(rr),
                "success_rate": sum(s["success"] for _, s in rd) / len(rd) if rd else None,
                "reference_inv_p": sum(1 / p for p, _ in rd) / len(rd) if rd else None,
                "z_score": z([1 / p for p, _ in rd], sum(s["success"] for _, s in rd)),
                "identity_rate": sum(s["identity_holds"] for _, s in rr) / len(rr),
                "homomorphism_rate_prec2": sum(s["hom_prec2"] for _, s in rr) / len(rr),
            }
    m["torsion_sections"] = ts
    return m


def criteria(m):
    a, t, ts = m["anomalous"], m["torsion"], m["torsion_sections"]
    five = ["canonicity_rate", "homomorphism_rate_torsion", "degeneracy_rate_torsion",
            "torsion_reduces_rate", "scalar_mult_equivariance_rate"]
    sec_ok = all(ts[s][arm]["identity_rate"] == 1.0 and abs(ts[s][arm]["z_score"]) <= 4
                 for s in SECTIONS for arm in ts[s])
    success = (a["rule_agreement"] == 1.0 and a["nondegenerate_success_rate"] == 1.0
               and abs(a["degenerate_z_score"]) <= 4 and all(t[k] == 1.0 for k in five) and sec_ok)
    falsify = (a["rule_disagreements"] > 0
               or any(ts[s][arm]["identity_rate"] < 1.0 for s in SECTIONS for arm in ts[s])
               or any(ts[s][arm]["z_score"] > 4 for s in SECTIONS for arm in ts[s]))
    zs = {"anomalous.degenerate_z_score": a["degenerate_z_score"]}
    zs.update({f"torsion_sections.{s}.{arm}.z_score": ts[s][arm]["z_score"] for s in SECTIONS for arm in ts[s]})
    return {"success_criterion_met": success, "falsification_condition_met": falsify,
            "max_abs_z": max(abs(v) for v in zs.values()),
            "z_with_abs_ge_0.1": {k: v for k, v in zs.items() if abs(v) >= 0.1}}


def compare(mine, theirs, path=""):
    diffs, matched = [], 0
    for k, v in theirs.items():
        p = f"{path}.{k}" if path else k
        if k not in mine:
            continue
        if isinstance(v, dict):
            d, c = compare(mine[k], v, p)
            diffs += d
            matched += c
        else:
            mv = mine[k]
            same = (mv == v) or (isinstance(v, float) and isinstance(mv, float) and math.isclose(mv, v, rel_tol=1e-12, abs_tol=1e-15))
            matched += 1
            if not same:
                diffs.append({"metric": p, "recorded": v, "recomputed": mv})
    return diffs, matched


def load_manifest_metrics(path):
    # minimal YAML read without a dependency: use PyYAML if available
    try:
        import yaml
        return yaml.safe_load(open(path))["run"]["result"]["metrics"]
    except ImportError:
        return None


out = {}
for run in RUNS:
    rd = os.path.join(ROOT, EXP, "runs", run)
    doc = json.load(open(os.path.join(rd, "raw-result.json")))
    mine = recompute(doc["raw"])
    rec = doc["metrics"]
    d_raw, c_raw = compare(mine, rec)
    man = load_manifest_metrics(os.path.join(rd, "manifest.yaml"))
    d_man, c_man = compare(mine, man) if man else (None, 0)
    stdout = json.loads(open(os.path.join(rd, "stdout.log")).read())
    d_out, c_out = compare(mine, stdout)
    # manifest vs raw-result metrics block, field by field (exact)
    d_mr, c_mr = compare(rec, man) if man else (None, 0)
    out[run] = {
        "recomputed": mine,
        "criteria": criteria(mine),
        "vs_raw_metrics": {"matched_fields": c_raw, "diffs": d_raw},
        "vs_manifest_metrics": {"matched_fields": c_man, "diffs": d_man},
        "vs_stdout": {"matched_fields": c_out, "diffs": d_out},
        "manifest_vs_raw_metrics": {"matched_fields": c_mr, "diffs": d_mr},
        "recorded_keys_not_recomputed": sorted(set(rec) - set(mine)),
        "manifest_curve_list_matches_raw": (man or {}).get("anomalous_curve_list") ==
            [[cu["D"], cu["p"]] for cu in doc["raw"]["curves_anomalous"]] if man else None,
        "seed_recorded": rec.get("seed"),
    }
json.dump(out, sys.stdout, indent=1, default=str)
print()
