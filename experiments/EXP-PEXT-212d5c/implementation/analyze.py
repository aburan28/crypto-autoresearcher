#!/usr/bin/env python3
"""Analysis of EXP-PEXT-212d5c from recorded run directories only (no computation beyond counting).

analyze(up) takes {"regression": dir, "construct": dir, "char2": dir, "census": dir, "lean": dir} and returns the
analysis.json object: validity gates, the n = 7 floor table by stratum, the (m, r) spectrum, every pre-registered
prediction of H-PEXT-d536a1 with its frozen rule and outcome, the configuration-to-curve consistency at q = 3, the
heuristic H1 scaling, and a one-line headline. Thresholds are the contract's; nothing here is tuned to data.
"""
from __future__ import annotations

import json
import math
import os

# derived floors (H-PEXT-d536a1, Lemma E7, Prop. T7, Lemma O7), per census stratum
DERIVED_FLOOR = {"split": 7, "Z2_0mod4": 161, "Z2_2mod4": 193, "odd": 193, "odd_jFq": 577}
STRATA = ("split", "Z2_0mod4", "Z2_2mod4", "odd", "odd_jFq")
M_PREDICTED = [1, 3, 4, 6, 7]
H1_SLOPE_BAND = (-3.5, -2.5)      # slope of log(rate) on log(q) between q = 5 and q = 7
H1_RATIO_BAND = (0.8, 1.25)       # (rate q^3 at q = 7) / (rate q^3 at q = 5)


def _jsonl(path: str) -> list:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def analyze(up: dict) -> dict:
    invalid: list = []
    reg = _json(os.path.join(up["regression"], "regression.json"))
    if not reg["pass"]:
        invalid.append("regression fixture failed: " + ", ".join(c["name"] for c in reg["checks"] if not c["identical"]))
    cons = {}
    for q in (3, 5, 7):
        recs = _jsonl(os.path.join(up["construct"], f"construct-q{q}.jsonl"))
        summ = next(r for r in recs if r["rec"] == "construct")
        cons[q] = {"summary": summ, "j7": {r["j_idx"] for r in recs if r["rec"] == "construct_curve"},
                   "curves": [r for r in recs if r["rec"] == "construct_curve"]}
        if summ["configs_other"] != 0:
            invalid.append(f"construct q={q}: {summ['configs_other']} configurations are not (m, r) = (3, 7)")
    char2 = _jsonl(os.path.join(up["char2"], "char2.jsonl"))
    census = _jsonl(os.path.join(up["census"], "census-n7-q3.jsonl"))
    curves = [r for r in census if r["rec"] == "curve"]
    totals = next(r for r in census if r["rec"] == "totals")
    dchk = next(r for r in census if r["rec"] == "derived_checks")
    mr = [r for r in census if r["rec"] == "mr"]
    if totals["mismatches"] != 0:
        invalid.append(f"census subcover-sum mismatches: {totals['mismatches']}")
    lean_path = os.path.join(up["lean"], "lean.json") if up.get("lean") else ""
    lean = _json(lean_path) if lean_path and os.path.isfile(lean_path) else {"status": "not_run_or_missing"}

    # floor table by stratum (picks only for 'self'; neighbours enter the <= 1 step minimum)
    table = {}
    for s in STRATA:
        picks = [c for c in curves if c["role"] == s]
        allm = [c for c in curves if c["stratum"] == s]
        hist_self, hist_2 = {}, {}
        for c in picks:
            hist_self[c["min_genus"]] = hist_self.get(c["min_genus"], 0) + 1
            hist_2[c["min_genus_2isog"]] = hist_2.get(c["min_genus_2isog"], 0) + 1
        mins = [c["min_genus"] for c in allm if not (s == "odd_jFq" and c["j0"])]
        floor = DERIVED_FLOOR[s]
        table[s] = {"derived_floor": floor, "picked": len(picks), "models_in_stratum_incl_neighbours": len(allm),
                    "min_genus_self_hist": {str(k): v for k, v in sorted(hist_self.items())},
                    "min_genus_2isog_hist": {str(k): v for k, v in sorted(hist_2.items())},
                    "observed_min": min(mins) if mins else None,
                    "below_floor": sum(1 for g in mins if g < floor),
                    "attaining_floor": sum(1 for g in mins if g == floor),
                    "status": ("derived; attained in census" if mins and min(mins) == floor else
                               "derived; not attained in this sample" if mins else "derived; no model in sample")}
    m_seen = sorted({r["m"] for r in mr})
    mr_hist = {}
    for r in mr:
        k = f"{r['m']},{r['r']},E2={r['E2']}"
        mr_hist[k] = mr_hist.get(k, 0) + r["structures"]

    # configuration-to-curve consistency at q = 3 (split models of the census against the q = 3 enumeration)
    j7 = cons[3]["j7"]
    split_models = [c for c in curves if c["E2"] == 4]
    cc_bad = [c for c in split_models if (c["min_genus"] == 7) != (c["j_idx"] in j7)]
    if cc_bad:
        invalid.append(f"configuration-to-curve map: {len(cc_bad)} censused split models disagree with the q = 3 enumeration")

    preds = {}
    viol = dchk["violations"]
    pos7_ok = all(cons[q]["summary"]["j_genus7"] > 0 for q in (3, 5, 7))
    g7_structs = [c for c in curves if "7" in c["structures_by_genus"]]
    g7_nonsplit = [c for c in g7_structs if c["E2"] != 4]
    g7_not_37 = [c for c in g7_structs if any(t["m"] != 3 or t["r"] != 7 for t in c["types_at_min"]) and c["min_genus"] == 7]
    preds["P1_spectrum"] = {"rule": "set of m over all censused structures equals {1, 3, 4, 6, 7}; any m outside refutes; a proper subset is "
                                    "under-coverage, not refutation", "observed": m_seen,
                            "outcome": ("refuted" if any(m not in M_PREDICTED for m in m_seen) else
                                        "confirmed" if m_seen == M_PREDICTED else "consistent_subset")}
    preds["P2_split_floor_7"] = {"rule": "genus 7 attained at q = 3, 5 and 7 (enumeration), only through (m, r) = (3, 7), only on split curves; "
                                         "a sampled split curve at q = 3 reaches 7 in the census",
                                 "observed": {"j_genus7": {q: cons[q]["summary"]["j_genus7"] for q in (3, 5, 7)},
                                              "census_split_picks_at_7": table["split"]["attaining_floor"],
                                              "genus7_nonsplit_models": len(g7_nonsplit), "genus7_not_3_7_models": len(g7_not_37)},
                                 "outcome": ("refuted" if g7_nonsplit or g7_not_37 else
                                             "confirmed" if pos7_ok and table["split"]["attaining_floor"] > 0 else "not_attained")}
    nonsplit_below = sum(table[s]["below_floor"] for s in STRATA if s != "split")
    preds["P3_nonsplit_floors"] = {"rule": "no non-split model below its derived floor (Z/2 with 4 | #E: 161; 2 mod 4: 193; odd: 193; "
                                           "odd with j in F_q, j != 0: 577); each below-floor model is a counterexample certificate",
                                   "observed": {s: table[s]["observed_min"] for s in STRATA if s != "split"},
                                   "outcome": "refuted" if nonsplit_below else "confirmed"}
    odd_picks = [c for c in curves if c["stratum"] == "odd"]
    preds["P4_odd_193"] = {"rule": "every odd-order model with j not in F_q has minimum exactly 193 attained by exactly one structure (O7)",
                           "observed": {"models": len(odd_picks), "min_genus_values": sorted({c["min_genus"] for c in odd_picks}),
                                        "structures_at_193": sorted({c["structures_by_genus"].get("193", 0) for c in odd_picks})},
                           "outcome": ("refuted" if any(c["min_genus"] != 193 or c["structures_by_genus"].get("193", 0) != 1 for c in odd_picks)
                                       else "confirmed" if odd_picks else "not_tested")}
    preds["P5_derived_checks"] = {"rule": "zero violations of every n = 7 derived statement compiled into the tool, on every censused model",
                                  "observed": viol, "outcome": "confirmed" if not viol else "refuted"}
    c2ok = all(r["matches_prediction"] and r["m_equals_deg_lcm_ord_b_x_plus_1_mismatches"] == 0 for r in char2)
    preds["P6_char2_magic"] = {"rule": "classical magic numbers at N = 7 l, l = 1, 2, 3: m in {1, 4, 7} with counts q - 1, 2 q^4 - 2 q, "
                                       "q^7 - 2 q^4 + q, and m = deg lcm(Ord_b, x + 1) for every b",
                               "observed": [{"l": r["l"], "m_hist": r["m_hist"], "lcm_mismatches": r["m_equals_deg_lcm_ord_b_x_plus_1_mismatches"]} for r in char2],
                               "outcome": "confirmed" if c2ok else "refuted"}
    preds["P7_configuration_map"] = {"rule": "every censused split model at q = 3 has minimum 7 iff its j is in the q = 3 enumeration "
                                             "(a disagreement invalidates, it does not refute)",
                                     "observed": {"split_models": len(split_models), "disagreements": len(cc_bad)},
                                     "outcome": "confirmed" if not cc_bad else "invalid"}
    r5, r7 = cons[5]["summary"]["rate"], cons[7]["summary"]["rate"]
    slope = (math.log(r7) - math.log(r5)) / (math.log(7) - math.log(5)) if r5 > 0 and r7 > 0 else None
    ratio = (cons[7]["summary"]["rate_times_q3"] / cons[5]["summary"]["rate_times_q3"]) if cons[5]["summary"]["rate_times_q3"] else None
    h1_ok = slope is not None and H1_SLOPE_BAND[0] <= slope <= H1_SLOPE_BAND[1] and H1_RATIO_BAND[0] <= ratio <= H1_RATIO_BAND[1]
    preds["H1_rate_q_minus_3"] = {"rule": f"out of sample (q = 5, 7): slope of log rate on log q in {list(H1_SLOPE_BAND)} and the ratio of "
                                          f"rate q^3 (q = 7 over q = 5) in {list(H1_RATIO_BAND)}; q = 3 was seen before freezing and is reported only",
                                  "observed": {"rate": {q: cons[q]["summary"]["rate"] for q in (3, 5, 7)},
                                               "rate_times_q3": {q: cons[q]["summary"]["rate_times_q3"] for q in (3, 5, 7)},
                                               "slope_q5_q7": slope, "ratio_q7_over_q5": ratio},
                                  "outcome": "consistent" if h1_ok else "inconsistent"}
    valid = not invalid
    refuted = [k for k, v in preds.items() if v["outcome"] == "refuted"]
    if not valid:
        headline = "INVALID: " + "; ".join(invalid)
    elif refuted:
        headline = "REFUTED (scoped): " + ", ".join(refuted)
    elif preds["P2_split_floor_7"]["outcome"] == "confirmed" and preds["P1_spectrum"]["outcome"] == "confirmed":
        headline = "SUPPORT_SCOPED: n = 7 spectrum {1,3,4,6,7}; split floor 7 via (3,7); non-split floors held"
    else:
        headline = "INCONCLUSIVE: no refutation; " + ", ".join(k for k, v in preds.items() if v["outcome"] not in ("confirmed", "consistent"))
    return {"experiment": "EXP-PEXT-212d5c", "valid": valid, "invalid_reasons": invalid, "headline": headline,
            "floor_table": table, "m_values_observed": m_seen, "structures_by_m_r_E2": mr_hist,
            "census_totals": totals, "derived_check_violations": viol, "predictions": preds,
            "construct": {q: cons[q]["summary"] for q in (3, 5, 7)}, "char2": char2, "lean": lean,
            "regression": {"pass": reg["pass"], "checks": [{"name": c["name"], "identical": c["identical"]} for c in reg["checks"]]}}


def floor_table_md(an: dict) -> str:
    lines = ["# n = 7 GHS cover genus floor table (EXP-PEXT-212d5c), q = 3 census and q = 3, 5, 7 enumeration", "",
             "Recorded values only. Floors are derived (H-PEXT-d536a1); the census measures attainment in a stratified sample.", "",
             "| stratum | derived floor | picked | observed min (incl. neighbours) | attaining floor | below floor | status |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for s, row in an["floor_table"].items():
        lines.append(f"| {s} | {row['derived_floor']} | {row['picked']} | {row['observed_min']} | {row['attaining_floor']} | "
                     f"{row['below_floor']} | {row['status']} |")
    lines += ["", f"Headline: {an['headline']}", ""]
    for k, v in an["predictions"].items():
        lines.append(f"- {k}: {v['outcome']}")
    return "\n".join(lines) + "\n"
