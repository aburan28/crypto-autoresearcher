#!/usr/bin/env python3
"""J4 comparison step, TASK-20260924-c83b05: recomputed.json (own aggregation)
beside the RECORDED decision-rules.json, cell-summary.json and run-report.md
of RUN-CERTBIN-c417e0. Run only after j4_aggregate.py wrote recomputed.json.

For every item: recorded value, recomputed value, equal?, and the RV-10
floor/ceiling caveat (does the value sit at an end of its range, so that
agreement says little about the implementation?). CP95 comparisons check that
the validator's exact bracket (width < 2^-100) lies INSIDE the recorded
bracket (width < 2^-80).

Supplement S (clearly separate; produces no number of the run): the producer's
impl/stats_exact.clopper_pearson is evaluated at INTERIOR points
(x in {1, 6, 7, 31, 32, 55, 56, 61} of 62) beside the validator's cp95, to
say whether CP agreement at the run's boundary values (0/62, 62/62) is the
only evidence about that code.
Output: j4-recompute/comparison.json
"""
import json
import os
import re
import sys
from decimal import Decimal

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 6))
RUN = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0")
IMPL = os.path.join(REPO, "experiments/EXP-CERTBIN-e94b27/impl")
sys.path.insert(0, HERE)
import j4_aggregate as mine  # noqa: E402


def inside(own, rec):
    """own bracket [lo, hi] inside recorded bracket [lo, hi] (decimal strings)."""
    if own is None or rec is None:
        return own is None and rec is None
    o = [Decimal(x) for x in own]
    r = [Decimal(x) for x in rec]
    return r[0] <= o[0] and o[1] <= r[1]


def main():
    me = json.load(open(os.path.join(HERE, "recomputed.json")))
    dr = json.load(open(os.path.join(RUN, "decision-rules.json")))["rules"]
    cs = json.load(open(os.path.join(RUN, "cell-summary.json")))
    rep = open(os.path.join(RUN, "run-report.md")).read()
    rows = []

    def row(item, recorded, recomputed, caveat, equal=None):
        e = (recorded == recomputed) if equal is None else equal
        rows.append({"item": item, "recorded": recorded, "recomputed": recomputed, "equal": bool(e), "floor_ceiling": caveat})

    CEIL = "CEILING (x = n): a constant 'refuted' engine gives the same count; agreement checks the aggregation only at the boundary"
    FLOOR = "FLOOR (x = 0): a constant 'not refuted' engine gives the same count; agreement checks the aggregation only at the boundary"
    # MR1-MR3
    for name, rk, mk, key in (("MR1 a", "MR1_w4_refuted_U62", "MR1", "a"), ("MR2 b", "MR2_m5_refuted_U62", "MR2", "b"),
                              ("MR3 r", "MR3_refuted_at_D_le_5_U62", "MR3", "r")):
        rv = cs[rk][key]
        mv = me[mk][key]
        row(f"{name} (count of 62)", rv, mv, CEIL if mv == 62 else (FLOOR if mv == 0 else "interior"))
        row(f"{name} CP95 lower bracket (own inside recorded)", cs[rk]["CP95"]["lower_bracket"], me[mk]["CP95"]["lower_bracket"],
            "closed form 0.025^(1/62) at x = n; interior bisection untested by these data",
            equal=inside(me[mk]["CP95"]["lower_bracket"], cs[rk]["CP95"]["lower_bracket"]))
        row(f"{name} CP95 upper bracket", cs[rk]["CP95"]["upper_bracket"], me[mk]["CP95"]["upper_bracket"],
            "exactly 1 at x = n by definition", equal=inside(me[mk]["CP95"]["upper_bracket"], cs[rk]["CP95"]["upper_bracket"]))
    row("MR1 = DR-1 input a (decision-rules.json)", dr["RC1-DR-1"]["inputs"]["a"], me["MR1"]["a"], CEIL)
    row("MR3 labels", cs["MR3_refuted_at_D_le_5_U62"]["label_counts"], me["MR3"]["label_counts"],
        "all 62 in one label (W4, with M5 also verified); the other five labels are empty, so the label-precedence code is exercised on one branch only",
        equal=cs["MR3_refuted_at_D_le_5_U62"]["label_counts"] == {"W4": 62} and me["MR3"]["label_counts"] == {"W4 (and M5)": 62})
    # MR4
    for s in ("N-AFF62", "N-F262"):
        for c in ("W_4", "M_5", "W_5"):
            rr = cs["MR4_null_refutation_rates"][s][c]
            mm = me["MR4"][s][c]
            cav = ("UNDEFINED (0/0): W_5 never ran on a null instance; no interval, consumed by no rule" if mm["ran_on"] == 0 else
                   CEIL if mm["verified_refuted"] == mm["ran_on"] else FLOOR if mm["verified_refuted"] == 0 else "interior")
            row(f"MR4 {s} {c} count", [rr["verified_refuted"], rr["n"]], [mm["verified_refuted"], mm["ran_on"]], cav)
            if mm["CP95"]["defined"]:
                row(f"MR4 {s} {c} CP95 upper bracket", rr["CP95"]["upper_bracket"], mm["CP95"]["upper_bracket"],
                    "closed form 1 - 0.025^(1/62) at x = 0" if mm["verified_refuted"] == 0 else "1 at x = n",
                    equal=inside(mm["CP95"]["upper_bracket"], rr["CP95"]["upper_bracket"]))
                row(f"MR4 {s} {c} CP95 lower bracket", rr["CP95"]["lower_bracket"], mm["CP95"]["lower_bracket"],
                    "0 at x = 0" if mm["verified_refuted"] == 0 else "closed form 0.025^(1/62) at x = n",
                    equal=inside(mm["CP95"]["lower_bracket"], rr["CP95"]["lower_bracket"]))
            else:
                row(f"MR4 {s} {c} CP95", [rr["CP95"].get("lower"), rr["CP95"].get("upper")], "undefined (n = 0)",
                    "undefined", equal=rr["CP95"].get("lower") is None and rr["CP95"].get("upper") is None)
    # MR5
    m5 = cs["MR5_soundness_and_certificates"]
    row("MR5 C-PS1 refuted satisfiable (W_4, M_5, W_5)", [m5["C-PS1_refuted_satisfiable"][c] for c in ("W_4", "M_5", "W_5")],
        [me["MR5"]["C-PS1"][c]["refuted_reported"] for c in ("W_4", "M_5", "W_5")], "FLOOR (0 of 62, 62, 10)")
    row("MR5 C-PS1 checked", [m5["C-PS1_checked"][c] for c in ("W_4", "M_5", "W_5")],
        [me["MR5"]["C-PS1"][c]["checked"] for c in ("W_4", "M_5", "W_5")], "set sizes")
    for k, v in m5["certificates"].items():
        mm = me["MR5"]["certificates_per_closure_set"].get(k)
        if mm is None:
            row(f"MR5 certificates {k}", v, "closure not run on this set (no record)", "n/a",
                equal=all(x == 0 for x in v.values()))
            continue
        row(f"MR5 certificates {k}", [v[x] for x in ("reported_refutations", "submitted", "verified", "failed", "uncertified")],
            [mm[x] for x in ("reported_refutations", "submitted", "verified", "failed", "uncertified")],
            "every per-set count sits at 0 or at the set size")
    row("MR5 totals (submitted, verified, failed, uncertified)",
        [m5["totals"][x] for x in ("submitted", "verified", "failed", "uncertified")],
        [me["MR5"]["totals"][x] for x in ("submitted", "verified", "failed", "uncertified")], "verified = submitted (CEILING); failed, uncertified 0 (FLOOR)")
    # secondary
    sec = cs["secondary"]
    row("2 x 2 tables (U62, N-AFF62, N-F262)", sec["two_by_two"], me["secondary"]["two_by_two"], "each table has a single non-empty cell")
    d = sec["plain_macaulay_D_star_unsat_arm"]
    row("D* extension {4, 5, >5}", [d["4"], d["5"], d[">5"]],
        [me["secondary"]["D_star_extension"][k] for k in ("4 (1 in R_4, inherited)", "5 (b)", ">5 (62 - b)")], "b at CEILING")
    cr = sec["combined_unsat_arm_rates"]
    row("combined W_4 rate", [cr["W_4"]["numerator"], cr["W_4"]["denominator"]],
        [me["secondary"]["combined_unsat_arm_rates"]["W_4"]["num"], me["secondary"]["combined_unsat_arm_rates"]["W_4"]["den"]],
        "CEILING; 324 of the 386 are inherited through monotonicity, not measured")
    row("combined any-closure rate", [cr["any_closure_D_le_5"]["numerator"], cr["any_closure_D_le_5"]["denominator"]],
        [me["secondary"]["combined_unsat_arm_rates"]["any_closure_D_le_5"]["num"], me["secondary"]["combined_unsat_arm_rates"]["any_closure_D_le_5"]["den"]],
        "CEILING; same inheritance")
    row("U62 W_4 first iteration of 1", sec["U62_W4_first_iteration_of_1"], me["secondary"]["U62_W4_first_iteration_of_1"], "constant (all 1)")
    row("U62 ell in W_4 cap B_<=1", sec["U62_ell_in_W4_le1"], me["secondary"]["U62_ell_in_W4_le1"], "CEILING; implied by 1 in W_4")
    for c in ("W_4", "M_5"):
        a_ = sec["certificate_sizes"][c]
        b_ = me["secondary"]["certificate_sizes"][c]
        row(f"certificate sizes {c} (count, min, median, max, max-deg distribution)",
            [a_["count"], a_["min"], a_["median"], a_["max"], a_["max_deg_mu_distribution"]],
            [b_["count"], b_["min"], b_["median"], b_["max"], b_["maxdeg"]], "interior values (a real check of the counting)")
    # decision rules
    row("RC1-DR-1 verdict", dr["RC1-DR-1"]["verdict"], me["decision_rules"]["RC1-DR-1"]["verdict"],
        "a = 62 is far from both thresholds (56, 6): a >= 56 vs a > 56 comparator errors are invisible")
    row("RC1-DR-1 E-A falsified / E-G falsified", [dr["RC1-DR-1"]["E-A_falsified_(a<=31)"], dr["RC1-DR-1"]["E-G_falsified_(a>=32)"]],
        [me["decision_rules"]["RC1-DR-1"]["E-A_falsified"], me["decision_rules"]["RC1-DR-1"]["E-G_falsified"]], "far from 31/32")
    row("RC1-DR-2 L1, L2, verdict, residue", [dr["RC1-DR-2"]["L1"], dr["RC1-DR-2"]["L2"], dr["RC1-DR-2"]["verdict"], dr["RC1-DR-2"]["residue_idx"]],
        [me["decision_rules"]["RC1-DR-2"]["L1"], me["decision_rules"]["RC1-DR-2"]["L2"], me["decision_rules"]["RC1-DR-2"]["verdict"], me["decision_rules"]["RC1-DR-2"]["residue_idx"]],
        "0 not refuted and 0 undetermined: L1 = L2 trivially; the L1/L2 split is never exercised")
    row("RC1-DR-2 denominators", [dr["RC1-DR-2"]["inputs"]["L1_denominator"], dr["RC1-DR-2"]["inputs"]["L2_denominator"]],
        [me["decision_rules"]["RC1-DR-2"]["L1_denominator"], me["decision_rules"]["RC1-DR-2"]["L2_denominator"]], "no exclusions")
    row("RC1-DR-3 verdict and 2 x 2", [dr["RC1-DR-3"]["verdict"], dr["RC1-DR-3"]["inputs"]["two_by_two_U62"]],
        [me["decision_rules"]["RC1-DR-3"]["verdict"], me["decision_rules"]["RC1-DR-3"]["two_by_two_U62"]], "b at CEILING")
    for X in ("W_4", "M_5"):
        row(f"RC1-DR-4 {X} verdict", dr["RC1-DR-4"][X]["verdict"], me["decision_rules"]["RC1-DR-4"][X]["verdict"],
            "U62 62/62 against nulls 0/62: separated under any interval method" if X == "W_4" else
            "U62 62/62 against nulls 62/62: not separated under any interval method")
        row(f"RC1-DR-4 {X} separation flags", dr["RC1-DR-4"][X]["U62_lower_exceeds_null_upper"],
            me["decision_rules"]["RC1-DR-4"][X]["separated"], "extreme counts")
    row("RC1-DR-5 verdict (own control readings from J3)", dr["RC1-DR-5"]["verdict"], me["decision_rules"]["RC1-DR-5"]["verdict"],
        "not a count; own readings come from j3-checks, not instrument-checks.json")
    row("RC1-DR-5 per control", dr["RC1-DR-5"]["instrument_controls"], me["decision_rules"]["RC1-DR-5"]["own_control_readings"], "booleans")
    row("RC1-DR-6 flag", [dr["RC1-DR-6"]["RC1-DR-2_verdict"], dr["RC1-DR-6"]["clean_or_near_clean"]],
        [me["decision_rules"]["RC1-DR-6"]["RC1-DR-2_verdict"], me["decision_rules"]["RC1-DR-6"]["clean_or_near_clean"]], "follows DR-2")
    row("RC1-DR-7 primary", dr["RC1-DR-7"]["primary"], me["decision_rules"]["RC1-DR-7"]["primary"], "follows DR-1, DR-2")
    # run-report readings
    def rep_has(pattern):
        return re.search(pattern, rep) is not None
    row("run-report PA-1 reading", "held (a >= 56, E-A threshold)" if rep_has(r"PA-1: a = 62\. held \(a >= 56") else "?",
        "E-A threshold met" if me["PA"]["PA-1"]["E-A_threshold_a>=56"] else "not met", "a at CEILING",
        equal=rep_has(r"PA-1: a = 62\. held \(a >= 56") and me["PA"]["PA-1"]["E-A_threshold_a>=56"])
    row("run-report PA-2 reading", "CLEAN" if rep_has(r"PA-2: r = 62; label CLEAN") else "?", me["PA"]["PA-2"]["label"], "r at CEILING")
    row("run-report PA-3 reading", "held" if rep_has(r"PA-3: refuted satisfiable controls = 0; held") else "?",
        "held" if me["PA"]["PA-3"]["held"] else "failed", "FLOOR")
    pri = me["pre_data_prior"]
    row("run-report prior (a)", "overturned" if rep_has(r"\(a\) modal expectation a in \[15, 50\] \(MIXED\): observed a = 62 -> overturned") else "?",
        "overturned" if not pri["(a) modal a in [15, 50] (MIXED)"]["in_modal_range"] else "consistent", "a at CEILING, outside [15, 50]")
    row("run-report prior (b)", "consistent" if rep_has(r"\(b\).*-> consistent") else "?",
        "consistent" if pri["(b) b >= 56 and DR-2 CLEAN or NEAR-CLEAN"]["consistent"] else "overturned", "b at CEILING")
    kc = "(c) NOT DISTINGUISHED at M_5; nulls near 0 at W_4; if a >= 10 then S_3-SPECIFIC at W_4"
    row("run-report prior (c)", "consistent" if rep_has(r"\(c\).*-> consistent") else "?",
        "consistent" if pri[kc]["consistent"] else "overturned", "null counts at FLOOR (W_4) and CEILING (M_5)")
    row("run-report prior (d)", "consistent" if rep_has(r"\(d\).*-> consistent") else "?",
        "consistent" if pri["(d) every W_4 / M_5 refutation certifies"]["consistent"] else "overturned", "failed/uncertified at FLOOR")
    # Supplement S: producer CP code at interior points (no number of the run)
    sys.path.insert(0, IMPL)
    import stats_exact as prod
    sup = []
    for x in (1, 6, 7, 31, 32, 55, 56, 61):
        p = prod.clopper_pearson(x, 62)
        o = mine.cp95(x, 62)
        sup.append({"x": x, "n": 62, "producer_lower_bracket": p["lower_bracket"], "own_lower_bracket": o["lower_bracket"],
                    "producer_upper_bracket": p["upper_bracket"], "own_upper_bracket": o["upper_bracket"],
                    "own_inside_producer": inside(o["lower_bracket"], p["lower_bracket"]) and inside(o["upper_bracket"], p["upper_bracket"])})
    out = {"task_id": "TASK-20260924-c83b05", "joint": "J4", "rows": rows,
           "all_equal": all(r["equal"] for r in rows), "n_rows": len(rows), "unequal": [r for r in rows if not r["equal"]],
           "supplement_producer_cp_at_interior_points": {"note": "stats_exact.py only (never analysis.py); no run value is produced", "rows": sup,
                                                         "all_agree": all(s["own_inside_producer"] for s in sup)}}
    json.dump(out, open(os.path.join(HERE, "comparison.json"), "w"), indent=1)
    print(json.dumps({"all_equal": out["all_equal"], "n_rows": out["n_rows"], "unequal": out["unequal"],
                      "supplement_all_agree": out["supplement_producer_cp_at_interior_points"]["all_agree"]}, indent=1))


if __name__ == "__main__":
    main()
