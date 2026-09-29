#!/usr/bin/env python3
# analysis.py -- TASK-20260901-3dffdc (BATCH-803af6, GOAL-AES-003).
#
# Decision arithmetic for the Stage-0 verdict of IDEA-20260901-ec54fe.
# Pure arithmetic on already-written run JSONs (not a run, per BATCH-015
# precedent). Garwood Poisson CI + exact conditional-binomial machinery is
# the campaign frozen-comparator statistics, ported from BATCH-015
# TASK-20260805-d408ac src/analysis.py (disclosed reuse of statistical
# convention; verified below against that task's published figures
# garwood(1,1)=[0.025,5.572], garwood(6,8)=[0.275,1.632], and the
# EV-AES-e4c091 14-vs-1 exact test p=9.765625e-4). No scipy dependency.
import json, math, sys
from fractions import Fraction

def _gammap_series(a, x):
    if x == 0.0: return 0.0
    ap = a; s = 1.0 / a; d = s
    for _ in range(1000):
        ap += 1.0; d *= x / ap; s += d
        if abs(d) < abs(s) * 1e-15: break
    return s * math.exp(-x + a * math.log(x) - math.lgamma(a))

def _gammaq_cf(a, x):
    b = x + 1.0 - a; c = 1e300; d = 1.0 / b; h = d
    for i in range(1, 1000):
        an = -i * (i - a); b += 2.0
        d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d; de = d * c; h *= de
        if abs(de - 1.0) < 1e-15: break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))

def gammainc_reg(a, x):
    if x <= 0: return 0.0
    return _gammap_series(a, x) if x < a + 1.0 else 1.0 - _gammaq_cf(a, x)

def qchisq(p, df):
    lo, hi = 0.0, df + 50.0 * math.sqrt(2.0 * df) + 200.0
    while gammainc_reg(df / 2.0, hi / 2.0) < p: hi *= 2
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if gammainc_reg(df / 2.0, mid / 2.0) < p: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)

def garwood_ci(x, m):
    lo = 0.0 if x == 0 else 0.5 * qchisq(0.025, 2 * x) / m
    hi = 0.5 * qchisq(0.975, 2 * x + 2) / m
    return [lo, hi]

def binom_tail_exact_ge(k, n, p_frac):
    q = Fraction(1) - p_frac
    s = Fraction(0)
    for i in range(k, n + 1):
        s += Fraction(math.comb(n, i)) * p_frac ** i * q ** (n - i)
    return s

def self_checks():
    sc = {}
    g1 = garwood_ci(1, 1.0)
    g6 = garwood_ci(6, 8.0)
    sc["garwood_ev_e4c091_N1"] = {"ci": g1, "published": [0.025, 5.572],
        "match": round(g1[0], 3) == 0.025 and round(g1[1], 3) == 5.572}
    sc["garwood_ev_e4c091_N2_R"] = {"ci": g6, "published": [0.275, 1.632],
        "match": round(g6[0], 3) == 0.275 and round(g6[1], 3) == 1.632}
    n, x_aes, x_sub = 15, 14, 1
    p0 = Fraction(1, 2)
    tail_ge = binom_tail_exact_ge(x_aes, n, p0)
    tail_le = binom_tail_exact_ge(n - x_aes, n, Fraction(1) - p0)
    p_val = float(min(Fraction(1), 2 * min(tail_ge, tail_le)))
    sc["exact_cond_binom_14_vs_1"] = {"p_value": p_val, "expected": 0.0009765625,
        "match": abs(p_val - 0.0009765625) < 1e-12}
    sc["all_pass"] = all(v["match"] for v in sc.values() if isinstance(v, dict))
    return sc

def main():
    runs = sys.argv[1] if len(sys.argv) > 1 else "runs"
    census = json.load(open(f"{runs}/census.json"))
    anchor = json.load(open(f"{runs}/anchor_recompute.json"))
    pick = json.load(open(f"{runs}/fixture_pick.json"))
    aarm = json.load(open(f"{runs}/arm_ANCHOR-P30.json"))
    farm = json.load(open(f"{runs}/arm_FIXTURE-P30.json"))

    out = {
        "task_id": "TASK-20260901-3dffdc",
        "idea_record": "IDEA-20260901-ec54fe",
        "self_checks": self_checks(),
        "decision_rule_source": "PREREGISTRATION.md section 3 (verbatim record preregistered_decision_rule, F1, F2, r*_aff definition)",
    }

    # ---------- anchor arm (PR-1) ----------
    nt = aarm["nontrivial_trials"]
    wge1 = aarm["W_ge1_nontrivial"]
    excess = wge1 / (nt * 2.0 ** -30)
    anchor_verdict = {
        "arm": aarm["arm"], "rounds": aarm["rounds"], "amask": aarm["amask"],
        "smask": aarm["smask"], "trials": aarm["trials"], "seed": aarm["seed"],
        "arm_id": aarm["arm_id"], "threads": aarm["threads"],
        "trivial_swaps_excluded": aarm["trivial_swaps_excluded"],
        "nontrivial_trials": nt,
        "W_ge1_nontrivial": wge1,
        "whist": aarm["whist"],
        "W_ge1_by_word": aarm["W_ge1_by_word"],
        "excess": excess,
        "frozen_excess_E": 2.0 ** 30,
        "excess_ratio_to_frozen": excess / 2.0 ** 30,
        "W3_on_100pct_nontrivial": aarm["whist"][3] == nt and aarm["whist"][0] == 0
                                     and aarm["whist"][1] == 0 and aarm["whist"][2] == 0
                                     and aarm["whist"][4] == 0,
        "ranks_recomputed_32_0_0_0": anchor["f1_gate"]["ranks_match"],
        "P_hit_census": anchor["record_census_object_T_at_anchor"]["P_Wge1_all_trials"],
        "PR1_pass": bool(anchor["f1_gate"]["pass"]
                         and aarm["whist"][3] == nt and wge1 == nt),
    }
    out["anchor_PR1"] = anchor_verdict

    # ---------- census summary ----------
    r_star = census["r_star_aff"]["value"]
    cells_summary = []
    for ce in census["cells"]:
        row = {"cell_id": ce["cell_id"], "A": ce["A"], "S": ce["S"], "rounds": {}}
        for c in ce["rounds"]:
            row["rounds"][str(c["r"])] = {
                "ranks": c["word_map_ranks"],
                "P_all_float": c["P_Wge1_all_trials"]["float"],
                "P_all_exact": f"{c['P_Wge1_all_trials']['num']}/{c['P_Wge1_all_trials']['den']}",
                "label": c["label"],
                "label_refined": c["label_refined"],
                "whist_nonzero_d": c["whist_nonzero_d"],
                "identity_law_P": c["identity_law_prediction"]["P_Wge1"],
                "identity_law_W": c["identity_law_prediction"]["W_on_every_nontrivial_trial"],
            }
        cells_summary.append(row)
    out["census_table"] = cells_summary
    out["r_star_aff"] = census["r_star_aff"]
    out["PR5_structure_destroyed_cell"] = census["PR5_structure_destroyed_cell"]
    out["null_cells_exact_2^-30"] = census["null_cells_exact_2^-30"]

    # ---------- fixture arm (PR-4) ----------
    fnt = farm["nontrivial_trials"]
    fx = farm["W_ge1_nontrivial"]
    m_null = fnt * 2.0 ** -30
    R = fx / m_null
    Rci = garwood_ci(fx, m_null)
    rate = fx / fnt
    rate_ci = [Rci[0] * 2.0 ** -30, Rci[1] * 2.0 ** -30]
    fixture_verdict = {
        "arm": farm["arm"], "rounds": farm["rounds"], "amask": farm["amask"],
        "smask": farm["smask"], "trials": farm["trials"], "seed": farm["seed"],
        "arm_id": farm["arm_id"], "threads": farm["threads"],
        "picked_cell": pick,
        "trivial_swaps_excluded": farm["trivial_swaps_excluded"],
        "nontrivial_trials": fnt,
        "W_ge1_nontrivial": fx,
        "whist": farm["whist"],
        "W_ge1_by_word": farm["W_ge1_by_word"],
        "null_expectation_analytic": m_null,
        "measured_rate": rate,
        "excess_factor_R": R,
        "R_garwood_95ci": Rci,
        "rate_garwood_95ci": rate_ci,
        "ci_contains_null": Rci[0] <= 1.0 <= Rci[1],
        "scaled_count_band_le_3_at_2^30": fx <= 3,
        "PR4_pass": bool(Rci[0] <= 1.0 <= Rci[1]),
        "F2_fires": bool(Rci[0] > 1.0),
        "census_prediction_for_cell": pick.get("census_prediction"),
        "identity_law_prediction_for_cell": pick.get("identity_law_prediction"),
    }
    out["fixture_PR4"] = fixture_verdict

    # ---------- census-vs-harness comparison on measured cells ----------
    measured = []
    c1r5 = next(c for c in census["cells"][0]["rounds"] if c["r"] == 5)
    measured.append({
        "cell_id": "C1", "r": 5, "A": [0], "S": [0],
        "census_P_all_exact": f"{c1r5['P_Wge1_all_trials']['num']}/{c1r5['P_Wge1_all_trials']['den']}",
        "census_label": c1r5["label"],
        "measured_W_ge1": wge1, "measured_nontrivial": nt,
        "measured_rate": wge1 / nt,
        "agrees_with_census_prediction": bool(wge1 == nt and c1r5["P_Wge1_all_trials"]["num"] == c1r5["P_Wge1_all_trials"]["den"]),
        "agrees_with_identity_law": bool(wge1 == nt),
    })
    fc = pick["cell_id"]
    fr = pick["r"]
    cellrec = next(ce for ce in census["cells"] if ce["cell_id"] == fc)
    crec = next(c for c in cellrec["rounds"] if c["r"] == fr)
    measured.append({
        "cell_id": fc, "r": fr, "A": cellrec["A"], "S": cellrec["S"],
        "census_P_all_exact": f"{crec['P_Wge1_all_trials']['num']}/{crec['P_Wge1_all_trials']['den']}",
        "census_label": crec["label"],
        "measured_W_ge1": fx, "measured_nontrivial": fnt,
        "measured_rate": fx / fnt,
        "measured_R_garwood_95ci": Rci,
        "agrees_with_census_prediction": bool(Rci[0] <= 1.0 <= Rci[1]) if crec["label"] == "SKELETON-NULL"
            else bool(False),
        "agrees_with_identity_law": bool(
            (fx == fnt) if len(cellrec["A"]) <= 3 else (fx == 0)),
    })
    out["measured_cells_comparison"] = measured
    all_measured_agree_with_census = all(m["agrees_with_census_prediction"] for m in measured)

    # ---------- record decision rule ----------
    if not anchor_verdict["PR1_pass"]:
        branch = "F1"
        reading = ("F1 fires: anchor reproduction failed; every census reading VOID; "
                   "invalid_measurement, never evidence against the skeleton (rule 5).")
    elif fixture_verdict["F2_fires"] or not all_measured_agree_with_census:
        branch = "F2_or_measured_disagreement"
        reading = ("A measured cell disagrees with its exact census prediction: F1/F2 fires, "
                   "all readings VOID as instrument/derivation defect, repair dispatched, "
                   "no mechanism conclusion recorded (record preregistered_decision_rule).")
    elif r_star == 6:
        branch = "MATCH"
        reading = ("r*_aff = 6 AND all measured cells agree with their census predictions: "
                   "record the conclusion 'the round-count location of the excess is carried "
                   "by the linear skeleton' at toy tier and route the residual question to "
                   "IDEA-20260901-bcb117.")
    elif r_star is None or r_star > 6:
        branch = "MISMATCH-ALIVE"
        reading = ("r*_aff > 6 (or skeleton never dies within r<=10) AND measured cells agree: "
                   "record 'the skeleton outlives the AES excess; death-round is "
                   "nonlinearity-driven' and the ramp becomes RANK 1.")
    else:
        branch = "MISMATCH-DEAD"
        reading = ("r*_aff <= 5: MISMATCH-DEAD; the affine reproduction at r=5 is unexplained "
                   "by the census and P1 is indicted (record P3).")
    out["stage0_verdict"] = {
        "branch": branch,
        "reading": reading,
        "r_star_aff": r_star,
        "all_measured_agree_with_census": all_measured_agree_with_census,
        "anchor_PR1_pass": anchor_verdict["PR1_pass"],
        "fixture_F2_fires": fixture_verdict["F2_fires"],
        "note": ("Executor applies the record's rule mechanically; no hypothesis status, "
                 "evidence strength, or promotion is interpreted here."),
    }
    out["parse_attestation"] = ("this file is machine-generated JSON; parsed whole with "
                                "python3 json.load before task completion (stated in RESULTS.json)")
    out["inference"] = {
        "policy": "executor-implementation",
        "requested_policy": "executor-implementation",
        "resolved_model_id": "fireworks-ai/accounts/fireworks/models/qwen3p8-max",
        "model_verified": False,
        "fallback_used": True,
        "fallback_reason": "session-backend transport under inference amendment DEC-20260831-0d1eeb",
        "degraded_requirements": [],
        "amendment": "DEC-20260831-0d1eeb",
        "standing_basis": "0137a051eb5828789eb267fa83c8278086578d4c",
    }
    with open(f"{runs}/decision_analysis.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps({
        "self_checks": out["self_checks"],
        "anchor_PR1_pass": anchor_verdict["PR1_pass"],
        "fixture_R": R, "fixture_R_ci": Rci, "fixture_PR4_pass": fixture_verdict["PR4_pass"],
        "F2_fires": fixture_verdict["F2_fires"],
        "r_star_aff": r_star,
        "branch": branch,
    }, indent=1))

if __name__ == "__main__":
    main()
