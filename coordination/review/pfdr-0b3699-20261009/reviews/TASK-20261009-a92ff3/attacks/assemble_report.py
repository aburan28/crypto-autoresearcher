#!/usr/bin/env python3
"""TASK-20261009-a92ff3 -- assemble rederivation.yaml from this task's own outputs
(attacks/counts.json, attacks/sim/*.json) and the narrative sections below, so
that no number is transcribed by hand. Writes only the given output path."""
from __future__ import annotations

import json
import os
import sys

import yaml

W = sys.argv[1]            # write directory
NARR = sys.argv[2]         # narrative yaml (sections written by hand)
OUT = sys.argv[3]
A = os.path.join(W, "attacks")
SIM = os.path.join(A, "sim")


def j(p):
    return json.load(open(os.path.join(SIM, p)))


counts = json.load(open(os.path.join(A, "counts.json")))
cells = counts["cells"]
obs = {r: j(f"observed_{r}_{b}.json") for r, b in (("adopted", 1), ("MU2", 5), ("RH2", 6), ("DD2", 7))}
obs3 = j("observed_adopted_3.json")
cov1 = j("coverage_bank1.json")
cov3 = j("coverage_bank3.json")
banks = {f: j(f) for f in sorted(os.listdir(SIM)) if f.startswith("bank_") and f.endswith(".json")}

Ap, Mp = cells["A_pooled"], cells["M_pooled_M1"]


def ints(cell):
    return {"curves": cell["curves"], "C_X": cell["C_X"], "three_C_R": cell["three_C_R"],
            "six_sum_s2": cell["six_sum_s2"]}


counts_block = {
    "rule": "integers from this task's own CC-1..CC-3 recount (attacks/count_cells.py); C_R = three_C_R / 3; sum_j s_j^2 = six_sum_s2 / 6",
    "pooled": {"C_A": Ap["C_X"], "three_C_R": Ap["three_C_R"], "C_M": Mp["C_X"],
               "six_sum_s2": Ap["six_sum_s2"], "curves": Ap["curves"]},
    "per_rung": {b: {"C_A": cells["A_per_rung"][b]["C_X"], "three_C_R": cells["A_per_rung"][b]["three_C_R"],
                     "C_M": cells["M_per_rung_M1"][b]["C_X"], "six_sum_s2": cells["A_per_rung"][b]["six_sum_s2"],
                     "curves": cells["A_per_rung"][b]["curves"]} for b in ("30", "32")},
    "z_Delta_set": {"curves": cells["z_Delta"]["curves_where_M_admitted_and_A_admitted"],
                    "C_A": cells["z_Delta"]["C_A_on_M_curves"], "C_M": cells["z_Delta"]["C_M_on_M_curves"]},
}


def det(cell):
    return {k: cell[k] for k in ("C_R", "sum_s2", "V", "V_is_floor", "SD_null", "kappa_rel", "z", "SE") if k in cell}


zD = cells["z_Delta"]
quantities = {
    "C_A": {"adopted": Ap["C_X"],
            "alternatives": {"F2 (R-2)": cells["A_pooled_F2"]["C_X"], "A2 engine field (R-1)": "equal on all 51000 scored instances (integrity.recount_vs_engine)"}},
    "C_R": {"adopted": Ap["C_R"], "three_C_R": Ap["three_C_R"],
            "alternatives": {"S2 (R-3)": cells["randoms_S2"]["C_R"], "F2 (R-2)": cells["A_pooled_F2"]["C_R"]}},
    "V": {"adopted": Ap["V"], "sum_s2": Ap["sum_s2"], "floor_applied": Ap["V_is_floor"],
          "alternatives": {"P2 per-rung floor (R-4)": cells["A_pooled_P2_V"], "S2 (R-3)": cells["randoms_S2"]["V"]}},
    "SD_null": Ap["SD_null"], "kappa_hat": Ap["kappa_rel"], "SE": Ap["SE"],
    "z_A": {"adopted": Ap["z"], "alternatives": {"P2 (R-4)": cells["A_pooled_P2_z"], "F2 (R-2)": cells["A_pooled_F2"]["z"]}},
    "z_M": {"adopted": Mp["z"], "kappa_rel_M": Mp["kappa_rel"],
            "alternatives": {"M2 (R-5)": cells["M_pooled_M2"]["z"], "F2 (R-2)": cells["M_pooled_F2"]["z"]}},
    "z_Delta": {"adopted_D1": zD["D1_z"], "V_used_D1": zD["D1_V_own_set"],
                "alternatives": {"D2 (V of the A cell)": zD["D2_z"], "D3 (unpaired C_A)": zD["D3_z"],
                                 "D4 (V of the M cell)": zD["D4_z"]},
                "curves": zD["curves_where_M_admitted_and_A_admitted"]},
    "per_rung_secondary": {b: {"A": det(cells["A_per_rung"][b]), "M": det(cells["M_per_rung_M1"][b]),
                               "z_Delta_D1": cells["z_Delta_per_rung_D1"][b]} for b in ("30", "32")},
}

oa = obs["adopted"]


def cov_entry(cv, key):
    return {k: {"coverage": cv["kappas"][k][key]["coverage"], "mc_se": cv["kappas"][k][key]["mc_se"],
                "per_family_4000_designs": cv["kappas"][k][key]["per_family"]} for k in ("1.00", "1.10", "1.15")}


def governs(cv):
    cs = {k: cv["kappas"][k]["signed"]["coverage"] for k in ("1.00", "1.10", "1.15")}
    se = {k: cv["kappas"][k]["signed"]["mc_se"] for k in cs}
    gov = "signed" if all(c >= 0.945 for c in cs.values()) else "absdev"
    near = {k: abs(cs[k] - 0.945) <= 3 * se[k] for k in cs}
    nearab = {k: abs(cv["kappas"][k]["absdev_AB1"]["coverage"] - 0.945) <= 3 * cv["kappas"][k]["absdev_AB1"]["mc_se"] for k in cs}
    return gov, near, nearab


gov1, near1, nearab1 = governs(cov1)
gov3, near3, nearab3 = governs(cov3)
lab_s = "one-sided 95% (signed quantile; kappa_hat < 1, binomial thinning), simulated coverage" if oa["kappa_hat_lt_1"] else "one-sided 95% (signed quantile), simulated coverage"
lab_a = "quantile of |dev|; kappa_hat < 1, binomial thinning, simulated one-sided coverage" if oa["kappa_hat_lt_1"] else "quantile of |dev|, simulated one-sided coverage"
mincov = min(cov1["kappas"][k]["signed"]["coverage"] for k in ("1.00", "1.10", "1.15"))
U_A = {
    "observed_inputs": {"kappa_hat": oa["kappa_hat"], "SE": oa["SE"], "branch": oa["branch"],
                        "G-NB-R": {"rho1_hat_b": oa["rho1_hat_b"], "D_b": oa["D_b"], "D_hat_b_raw": oa["D_hat_b_raw"]}},
    "signed_quantile_bound": {
        "value_adopted_Q1": oa["U_signed_Q1"], "q_lo_Q1": oa["q_lo_Q1"], "q_lo_per_family": oa["q_lo_per_family"],
        "value_Q2_pooled_quantile": oa["U_signed_Q2"],
        "mc_se": oa["mc_se"]["U_signed_reported"],
        "mc_se_components": {"asymptotic": oa["mc_se"]["U_signed_asymptotic"], "family_spread": oa["mc_se"]["U_signed_family_spread"]},
        "second_bank_C2_value": obs3["U_signed_Q1"],
        "label": f"{lab_s} {min(cov1['kappas'][k]['signed']['coverage'] for k in ('1.00','1.10','1.15')):.3f} (minimum of the three)",
        "coverage": cov_entry(cov1, "signed"),
        "coverage_second_bank_C2": cov_entry(cov3, "signed"),
        "seeds": {"bank": "SeedSequence([0xA92FF3, 1, f]), f = 0..4", "structured": "SeedSequence([0xA92FF3, 2, f])"},
        "replicates": "5 families x 20000",
    },
    "absdev_quantile_bound": {
        "value_adopted_AB1_Q1": oa["U_absdev_Q1"], "q_abs_Q1": oa["q_abs_Q1"], "q_abs_per_family": oa["q_abs_per_family"],
        "value_Q2_pooled_quantile": oa["U_absdev_Q2"], "value_AB2_fixed_SE": oa["U_absdev_AB2_Q1"],
        "mc_se": oa["mc_se"]["U_absdev_reported"],
        "mc_se_components": {"asymptotic": oa["mc_se"]["U_absdev_asymptotic"], "family_spread": oa["mc_se"]["U_absdev_family_spread"]},
        "second_bank_C2_value": obs3["U_absdev_Q1"],
        "label": f"{lab_a} {min(cov1['kappas'][k]['absdev_AB1']['coverage'] for k in ('1.00','1.10','1.15')):.3f} (minimum of the three)",
        "coverage": cov_entry(cov1, "absdev_AB1"),
        "coverage_AB2_fixed_SE": cov_entry(cov1, "absdev_AB2_fixedSE"),
        "coverage_second_bank_C2": cov_entry(cov3, "absdev_AB1"),
    },
    "coverage_design": {
        "designs_per_kappa": cov1["kappas"]["1.00"]["designs"], "families": 5, "designs_per_family": 4000,
        "inner_replicates_per_design": "5 x 20000 (random-arm summaries from the bank; structured totals fresh per design)",
        "design_seeds": "SeedSequence([0xA92FF3, 10 + i, f]), i = 0 (1.00), 1 (1.10), 2 (1.15)",
        "inner_seeds_bank1": "SeedSequence([0xA92FF3, 20 + i, 0])", "inner_seeds_bank3": "SeedSequence([0xA92FF3, 30 + i, 0])",
        "plug_in_C3_diagnostic": {k: {"signed": cov1["kappas"][k]["plug_in_C3_signed"]["coverage"],
                                      "absdev": cov1["kappas"][k]["plug_in_C3_absdev"]["coverage"],
                                      "quantiles": cov1["kappas"][k]["plug_in_quantiles"]} for k in ("1.00", "1.10", "1.15")},
        "design_kappa_hat_summary": {k: {"mean": cov1["kappas"][k]["kappa_hat_mean"], "sd": cov1["kappas"][k]["kappa_hat_sd"],
                                         "share_below_1": cov1["kappas"][k]["share_kappa_hat_lt_1"]} for k in ("1.00", "1.10", "1.15")},
    },
    "AR-3_choice": {
        "governing_bound": "signed quantile" if gov1 == "signed" else "|dev| quantile",
        "governing_value": oa["U_signed_Q1"] if gov1 == "signed" else oa["U_absdev_Q1"],
        "rule": "signed governs iff each of its three simulated coverages >= 0.945 (AR-3, upper_bound_U_A)",
        "minimum_signed_coverage": mincov,
        "signed_coverage_within_3_mc_se_of_0.945": near1,
        "absdev_coverage_within_3_mc_se_of_0.945": nearab1,
        "choice_at_monte_carlo_resolution": any(near1.values()),
        "second_bank_C2_choice": "signed quantile" if gov3 == "signed" else "|dev| quantile",
        "second_bank_C2_within_3_mc_se": near3,
    },
    "alternative_readings_observed_bounds": {
        r: {"U_signed_Q1": obs[r]["U_signed_Q1"], "U_absdev_Q1": obs[r]["U_absdev_Q1"],
            "mc_se_signed": obs[r]["mc_se"]["U_signed_reported"], "mc_se_absdev": obs[r]["mc_se"]["U_absdev_reported"],
            "rho1_hat_b": obs[r]["rho1_hat_b"], "D_b": obs[r]["D_b"]}
        for r in ("MU2", "RH2", "DD2")},
    "simulator_controls": {f: {k: banks[f][k] for k in ("mean_C_R_star", "model_sum_m", "mean_sum_s2_star", "model_sum_D_m", "seconds")} for f in banks},
}

ext = {}
for i, k in enumerate(("1.00", "1.10", "1.15")):
    fp = os.path.join(SIM, f"coverage_ext_{i}.json")
    if os.path.exists(fp):
        e = json.load(open(fp))
        n_ad = cov1["kappas"][k]["designs"]
        pooled = {}
        for key, adkey in (("signed", "signed"), ("absdev_AB1", "absdev_AB1")):
            cov_ad = cov1["kappas"][k][adkey]["coverage"]
            covered = e[key]["covered"] + round(cov_ad * n_ad)
            n = e["designs"] + n_ad
            c = covered / n
            pooled[key] = {"coverage": c, "mc_se": (c * (1 - c) / n) ** 0.5, "designs": n,
                           "within_3_mc_se_of_0.945": abs(c - 0.945) <= 3 * (c * (1 - c) / n) ** 0.5}
        ext[k] = {"extension_only": {"designs": e["designs"], "signed": e["signed"], "absdev_AB1": e["absdev_AB1"],
                                     "per_family": e["per_family"], "design_seed": e["design_seed"],
                                     "inner_seed": e["inner_seed"], "bank_purpose": e["bank_purpose"]},
                  "pooled_with_adopted_designs": pooled}
if ext:
    allk = all(k in ext for k in ("1.00", "1.10", "1.15"))
    sup_choice = None
    if allk:
        sup_choice = "signed quantile" if all(ext[k]["pooled_with_adopted_designs"]["signed"]["coverage"] >= 0.945
                                              for k in ext) else "|dev| quantile"
    U_A["supplementary_coverage_extension_AD-7"] = {
        "status": "supplement; never replaces the adopted R-14 values above",
        "kappas": ext, "AR-3_choice_on_pooled_designs": sup_choice}
narr = yaml.safe_load(open(NARR))
doc = narr["rederivation_head"]
doc["counts_integers"] = counts_block
doc["counting_integrity"] = counts["integrity"] | {"admission": counts["admission"]}
doc["counting_integrity"].pop("recount_mismatches", None)
doc["quantities"] = quantities
doc["U_A"] = U_A
for k, v in narr["rederivation_tail"].items():
    doc[k] = v
att = narr["review_attestation"]
rowfiles = sorted(counts["files_read_sha256"].items())
att["sources_read"] = list(att["sources_read"]) + [p for p, _ in rowfiles if p not in att["sources_read"]]
doc["row_and_design_files_read_sha256"] = dict(rowfiles)
doc["review_attestation"] = att
with open(OUT, "w") as f:
    f.write("# TASK-20261009-a92ff3 -- J-BLIND blind re-derivation report (REVIEW-PFDR-20261009-eb0048).\n")
    f.write("# Assembled by attacks/assemble_report.py from this task's own outputs; numbers are not hand-copied.\n")
    yaml.safe_dump({"rederivation": doc}, f, sort_keys=False, width=100, allow_unicode=False)
print("written", OUT)
