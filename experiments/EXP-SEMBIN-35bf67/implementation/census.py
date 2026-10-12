#!/usr/bin/env python3
"""EXP-SEMBIN-35bf67 census + mechanical label application (OP-NULL, OP-SEP, OP-KOSTERS, OP-LABEL).

Reads every runs/*/params.json + raw-result.json, plus stage1/*.json, and writes
  stage2/census.json, stage3/offdiagonal.json, stage3/shortfall.json, stage2/label-trace.json
Observations and the pre-registered mechanical rule only; no interpretation.
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stats  # noqa: E402

EXP = os.path.dirname(HERE)
STAGE2_CELLS = [[30, 2, 2, 15], [40, 2, 2, 20], [21, 3, 3, 7], [45, 2, 2, 23], [25, 3, 3, 9], [50, 2, 2, 25]]
OFFDIAG = [([40, 2, 2, 21], [40, 2, 2, 20]), ([40, 2, 2, 22], [40, 2, 2, 20]), ([25, 3, 3, 10], [25, 3, 3, 9])]


def load_runs():
    runs = {}
    for p in sorted(glob.glob(os.path.join(EXP, "runs", "RUN-SEMBIN-*", "params.json"))):
        rd = os.path.dirname(p)
        rr = os.path.join(rd, "raw-result.json")
        if not os.path.exists(rr):
            continue
        params = json.load(open(p))
        raw = json.load(open(rr))
        key = (params["stage"], tuple(params["cell"]))
        runs.setdefault(key, []).append((os.path.basename(rd), raw))
    return runs


def cell_entry(runs, stage, cell):
    lst = runs.get((stage, tuple(cell)), [])
    if not lst:
        return {"cell": cell, "executed": False, "run_ids": []}
    if len(lst) > 1:
        raise SystemExit("more than one run for %s %s; census rule needs an explicit merge record" % (stage, cell))
    run_id, raw = lst[0]
    e = {"cell": cell, "executed": True, "run_ids": [run_id], "targets": raw["params"]["targets"],
         "allocation_hours": raw["params"]["allocation_hours"], "shortfall": raw["shortfall"],
         "cell_artifact": raw["cell_artifact"], "classification": raw["classification"],
         "null_arm_note": raw["params"].get("null_arm_note"), "arms": {}}
    for arm, blk in raw["arms"].items():
        e["arms"][arm] = {st: {k: blk[st][k] for k in ("n", "failures", "rate", "clopper_pearson_95",
                                                        "bootstrap_percentile_95", "not_solv4_indices",
                                                        "eval_rank_lt_s_indices", "closure_round_counts",
                                                        "s_values")}
                          for st in ("SAT", "UNSAT")}
        e["arms"][arm]["status_counts"] = blk["status_counts"]
        e["arms"][arm]["artifact_instances"] = blk["artifact_instances"]
        e["arms"][arm]["censored_instances"] = blk["censored_instances"]
        e["arms"][arm]["failed_infrastructure_instances"] = blk["failed_infrastructure_instances"]
        e["arms"][arm]["resources_measured"] = blk["resources_measured"]
        e["arms"][arm]["dual_rank_agree_all_valid"] = blk["dual_rank_agree_all_valid"]
    return e


def null_match(e):
    """OP-NULL. Returns dict with per-stratum Fisher p and the verdict (True/False/None)."""
    if not e.get("executed") or "null" not in e["arms"] or "primary" not in e["arms"]:
        return {"evaluable": False, "reason": "null or primary arm not executed"}
    res, evaluated = {}, []
    for st in ("SAT", "UNSAT"):
        p, q = e["arms"]["primary"][st], e["arms"]["null"][st]
        if p["n"] >= 10 and q["n"] >= 10:
            pv = stats.fisher_two_sided(p["failures"], p["n"] - p["failures"], q["failures"], q["n"] - q["failures"])
            res[st] = {"primary": [p["failures"], p["n"]], "null": [q["failures"], q["n"]], "fisher_p": pv}
            evaluated.append(pv >= 0.05)
        else:
            res[st] = {"primary": [p["failures"], p["n"]], "null": [q["failures"], q["n"]],
                       "fisher_p": None, "note": "fewer than 10 instances in a stratum: not evaluated"}
    if not evaluated:
        return {"evaluable": False, "per_stratum": res, "reason": "no stratum with >= 10 in both arms"}
    return {"evaluable": True, "per_stratum": res, "matches": all(evaluated)}


def separation(off, diag):
    if not off.get("executed") or not diag.get("executed"):
        return {"evaluable": False, "reason": "cell not executed"}
    res, any_sep, any_eval = {}, False, False
    for st in ("SAT", "UNSAT"):
        a, b = off["arms"]["primary"][st], diag["arms"]["primary"][st]
        if a["n"] >= 10 and b["n"] >= 10:
            pv = stats.fisher_two_sided(a["failures"], a["n"] - a["failures"], b["failures"], b["n"] - b["failures"])
            res[st] = {"offdiag": [a["failures"], a["n"]], "diag": [b["failures"], b["n"]], "fisher_p": pv}
            any_eval = True
            any_sep = any_sep or pv < 0.05
        else:
            res[st] = {"offdiag": [a["failures"], a["n"]], "diag": [b["failures"], b["n"]], "fisher_p": None,
                       "note": "fewer than 10 instances in a stratum: not evaluated"}
    return {"evaluable": any_eval, "per_stratum": res, "separates": any_sep if any_eval else None}


def main():
    runs = load_runs()
    s1 = {}
    for f in ("engine-gate.json", "baseline-smoke.json", "builder-check.json"):
        p = os.path.join(EXP, "stage1", f)
        s1[f] = json.load(open(p)) if os.path.exists(p) else None
    census = {"document": "EXP-SEMBIN-35bf67 Stage-2 census. Observations; frozen comparisons per "
                          "stage0/preregistered-predictions.json. No interpretation.",
              "cells": [cell_entry(runs, "stage2", c) for c in STAGE2_CELLS]}
    byc = {tuple(e["cell"]): e for e in census["cells"]}
    for e in census["cells"]:
        e["OP_NULL"] = null_match(e)
    # frozen comparisons
    b = byc[(40, 2, 2, 20)]
    comp = {}
    if b["executed"]:
        comp["P-C2-baseline"] = {
            "band": "< 0.02 both strata; falsifier > 0.10",
            "SAT": b["arms"]["primary"]["SAT"], "UNSAT": b["arms"]["primary"]["UNSAT"],
            "rate_gt_0.10_any_stratum": any((b["arms"]["primary"][st]["rate"] or 0) > 0.10 for st in ("SAT", "UNSAT")
                                            if b["arms"]["primary"][st]["n"]),
            "within_band_lt_0.02_both": all(b["arms"]["primary"][st]["n"] and b["arms"]["primary"][st]["rate"] < 0.02
                                            for st in ("SAT", "UNSAT"))}
    kz = byc[(45, 2, 2, 23)]
    if kz["executed"]:
        sat, uns = kz["arms"]["primary"]["SAT"], kz["arms"]["primary"]["UNSAT"]
        comp["P-C2-kosters"] = {
            "band": "> 0.10 over >= 100 SAT instances", "SAT": sat, "UNSAT": uns,
            "n_SAT_ge_100": sat["n"] >= 100,
            "OP_KOSTERS_condition_met": sat["n"] >= 100 and uns["n"] >= 100 and sat["failures"] == 0 and uns["failures"] == 0}
        comp["P-resource"] = {"band": "< 8 CPU-hours and < 4 GiB at n=45 m=2 degree 4 (per certified cell)",
                              "measured": kz["arms"]["primary"]["resources_measured"]}
    comp["P-C1-dphidk"] = {"status": "NOT EVALUATED: specification gap G2 (no fit model/estimator in the frozen contract)",
                           "raw_inputs_m2_diagonal": {str(c): (byc[tuple(c)]["arms"]["primary"] if byc[tuple(c)]["executed"] else None)
                                                      for c in ([30, 2, 2, 15], [40, 2, 2, 20], [45, 2, 2, 23], [50, 2, 2, 25])}}
    comp["P-C1-fixedk"] = {"status": "NOT EVALUATED: Stage-3 fixed-k ladders BLOCKED by specification gap G1"}
    census["frozen_comparisons"] = comp
    # stage 3 off-diagonal
    off = {"document": "EXP-SEMBIN-35bf67 Stage-3 off-diagonal gate (SR-6, OP-SEP). Observations only.", "cells": []}
    for oc, dc in OFFDIAG:
        oe = cell_entry(runs, "stage3", oc)
        de = byc.get(tuple(dc), {"executed": False})
        oe["diagonal_cell"] = dc
        oe["OP_SEP"] = separation(oe, de)
        off["cells"].append(oe)
    sep_eval = [c["OP_SEP"] for c in off["cells"] if c["OP_SEP"].get("evaluable")]
    off["O_CEILING_rule"] = {"evaluable_cells": len(sep_eval),
                             "any_separates": any(x["separates"] for x in sep_eval) if sep_eval else None,
                             "ceiling": (not any(x["separates"] for x in sep_eval)) if sep_eval else None}
    shortfall = {"document": "EXP-SEMBIN-35bf67 Stage-3 shortfall record.",
                 "fixed_k_ladders": {"status": "NOT RUN (BLOCKED)",
                                     "clause": "specification.yaml scope.included Stage 3: \"fixed-k ladders k=4 (n=13..28) and k=7 (n=19..30) as far as budget\"",
                                     "gaps": ["G1: (m, t) of the ladders not stated; arity_m levels {2,3} exclude Semaev's m=t=4 k=4 rows",
                                              "G2: dphi/dk and dphi/dn fit model, estimator and interval method not stated"],
                                     "requested": "Coordinator protocol_amendment fixing (m, t) per ladder and the fit"},
                 "offdiagonal_shortfall": {str(c["cell"]): (c.get("shortfall") if c.get("executed") else "not executed")
                                           for c in off["cells"]}}
    # label application (OP-LABEL)
    trace = []
    eg = s1["engine-gate.json"]
    sm = s1["baseline-smoke.json"]
    label = None
    if eg is None or not eg["SR2_engine_gate_pass"] or (sm and sm["dual_rank_artifact_present"]):
        label = "O-ENGINE-FAIL"
        trace.append("(1) SR-2 engine gate failed or smoke dual-rank artifact -> O-ENGINE-FAIL")
    else:
        trace.append("(1) SR-2 engine gate passed")
    if label is None:
        if sm is None or not sm["smoke_complete_8_per_stratum"]:
            label = "O-IMPEDIMENT"
            trace.append("(2) smoke incomplete -> cannot evaluate SR-3 -> O-IMPEDIMENT")
        elif sm["SR3_failure_rate_gt_0.10_in_any_stratum"] or comp.get("P-C2-baseline", {}).get("rate_gt_0.10_any_stratum"):
            label = "O-BASELINE-FAIL"
            trace.append("(2) SR-3 smoke or Stage-2 (40,2,2,20) rate > 0.10 -> O-BASELINE-FAIL")
        else:
            trace.append("(2) SR-3 not triggered (smoke and Stage-2 baseline rates <= 0.10 in both strata)")
    if label is None:
        arts = [e["cell"] for e in census["cells"] if e.get("executed") and e["cell_artifact"]]
        if arts:
            label = "O-ARTIFACT"
            trace.append("(3) Stage-2 cell(s) invalidated by SR-4/s mismatch: %s -> O-ARTIFACT" % arts)
        else:
            trace.append("(3) no Stage-2 cell invalidated by SR-4 or s mismatch")
    if label is None:
        nm = byc[(40, 2, 2, 20)]["OP_NULL"]
        if nm.get("evaluable") and nm["matches"]:
            label = "O-NULL-COLLAPSE"
            trace.append("(4) OP-NULL matches at (40,2,2,20) -> O-NULL-COLLAPSE")
        else:
            trace.append("(4) OP-NULL at (40,2,2,20): %s" % ("evaluable, does not match" if nm.get("evaluable") else "NOT evaluable (%s)" % nm.get("reason")))
    if label is None:
        ce = off["O_CEILING_rule"]
        if ce["evaluable_cells"] and ce["ceiling"]:
            label = "O-CEILING"
            trace.append("(5) no executed off-diagonal cell separates -> O-CEILING")
        else:
            trace.append("(5) O-CEILING rule: %s" % ("some off-diagonal cell separates" if ce["evaluable_cells"] else "NOT evaluable (no off-diagonal cell with >= 10 per stratum in both cells)"))
    if label is None:
        if comp.get("P-C2-kosters", {}).get("OP_KOSTERS_condition_met"):
            label = "O-KOSTERS-NOREPRO"
            trace.append("(6) OP-KOSTERS met -> O-KOSTERS-NOREPRO")
        else:
            trace.append("(6) OP-KOSTERS not met (requires >= 100 SAT and >= 100 UNSAT at (45,2,2,23), all SOLV4)")
    if label is None:
        trace.append("(7) dphi/dk and fixed-k criteria NOT evaluable (G1, G2)")
        label = "O-IMPEDIMENT"
        trace.append("(8) undeterminable criteria are undeterminable because of specification gaps G1/G2 -> O-IMPEDIMENT")
    secondary = []
    for e in census["cells"]:
        if not e.get("executed"):
            secondary.append({"cell": e["cell"], "label": "O-CENSORED/shortfall", "note": "not executed in session allocation"})
            continue
        for arm in e["arms"]:
            if e["arms"][arm]["censored_instances"]:
                secondary.append({"cell": e["cell"], "arm": arm, "label": "O-CENSORED (instances)",
                                  "instances": [x["index"] for x in e["arms"][arm]["censored_instances"]]})
        if e["OP_NULL"].get("evaluable") and e["OP_NULL"]["matches"] and e["cell"] != [40, 2, 2, 20]:
            secondary.append({"cell": e["cell"], "label": "O-NULL-COLLAPSE (cell-level reading, SR-5)"})
    lab = {"document": "EXP-SEMBIN-35bf67 mechanical application of pre-registered OP-LABEL (stage0). "
                       "Pending Coordinator ratification of OP-* operationalizations (gap G3).",
           "primary_label": label, "trace": trace, "secondary_labels": secondary}
    os.makedirs(os.path.join(EXP, "stage2"), exist_ok=True)
    os.makedirs(os.path.join(EXP, "stage3"), exist_ok=True)
    json.dump(census, open(os.path.join(EXP, "stage2", "census.json"), "w"), indent=1)
    json.dump(off, open(os.path.join(EXP, "stage3", "offdiagonal.json"), "w"), indent=1)
    json.dump(shortfall, open(os.path.join(EXP, "stage3", "shortfall.json"), "w"), indent=1)
    json.dump(lab, open(os.path.join(EXP, "stage2", "label-trace.json"), "w"), indent=1)
    print(json.dumps(lab, indent=1))


if __name__ == "__main__":
    main()
