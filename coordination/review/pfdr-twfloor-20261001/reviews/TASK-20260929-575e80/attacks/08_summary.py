"""08 -- collect the numbers the report cites from out/*.json into out/summary.json, plus the
census on-mode generic firing rate by rung band (12..24 and 26..32) and the PTM-5 per-rung
on-mode firing rates (r_frozen), to show how the predicate's null rate moves with N.
No randomness; reads outputs only.
"""
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, dump  # noqa: E402


def J(name):
    return json.load(open(os.path.join(OUT, name)))


inv, f34, nul, rung, agg, rho, ptm, p5 = (J("01_inventory.json"), J("02_f3_f4_checks.json"), J("03_f6_nulls.json"),
                                         J("03c_f6_rung_laws.json"), J("04_f6_aggregate.json"), J("05_ptm2_rho.json"),
                                         J("06_ptm134.json"), J("07_ptm5_analysis.json"))
xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r"]
band = Counter()
bandn = Counter()
for x in ev:
    if x["mode"] == "on" and x["cls"] in ("random", "structured"):
        b = "12-24" if x["bits"] <= 24 else "26-32"
        bandn[f"m{x['m']}|{b}"] += 1
        band[f"m{x['m']}|{b}"] += x["ratio"] < 0.9
census_band = {k: {"n": bandn[k], "fire": band[k], "rate": band[k] / bandn[k]} for k in sorted(bandn)}
ptm5_by_rung = {k: {"fire": v["primary_frozen"]["fire"], "n": v["primary_frozen"]["n"],
                    "median": v["primary_frozen"]["median"]}
                for k, v in p5["cells"].items() if k.endswith("|on")}
on_med = {}
for m in (3, 4, 5):
    for b in (12, 16, 20, 24, 28, 32):
        vals = sorted(x["ratio"] for x in ev if x["mode"] == "on" and x["cls"] in ("random", "structured")
                      and x["m"] == m and x["bits"] == b)
        if vals:
            on_med[f"m{m}|b{b}"] = vals[len(vals) // 2]
out = {
    "inventory": {k: inv[k] for k in ("evaluable", "my_below_0_9", "producer_below_0_9", "below_0_9_key_sets_equal",
                                      "firing_by_class_mode_m", "stage_r_evaluable", "stage_r_below_0_9")},
    "G5": {k: f34[k]["counts"] for k in ("G5_firing_rows", "G5_census_twins", "G5_all_rows_with_harvest")},
    "Xtotal": {k: f34["Xtotal"][k] for k in ("survive_Xtotal", "survive_Xtotal_by_cls", "survive_Xcmp",
                                             "dropped_by_Xtotal", "max_free_share_firing", "max_free_share_all")},
    "c1_census": f34["c1_census"],
    "nullP_on_pooled": {k: v for k, v in nul["families"].items() if k.startswith("on|POOLED")},
    "null_by_m_on": {k: {"NULL_P": v.get("frozen_NULL_P"), "NULL_B": v.get("frozen_NULL_B")}
                     for k, v in nul["families"].items() if k.startswith("on|") and "POOLED" not in k},
    "rung_law_sensitivity": rung["families"],
    "aggregate_cells_on_generic_frozen_rank": {k: {"T": v["T"], "ci95": v["ci95"], "ci99": v["ci99"]}
                                               for k, v in agg["cells"].items()
                                               if "|on|" in k and (k.endswith("|frozen") or k.endswith("|rank"))},
    "coverage_mc5": agg["coverage_mc5"],
    "rho": {k: {kk: rho[k][kk] for kk in ("n", "fire_q1", "frac_q1", "fire_q2", "frac_q2", "median_q1")}
            for k in ("rho_R13", "rho_j0", "rho_all")},
    "rho_predictions_all": {k: rho["rho_all"][k] for k in ("pred_a_negfolded", "pred_b_fullpoint", "pred_c_design")},
    "ptm1": {k: v for k, v in ptm["PTM1_known_log"].items() if k != "detail"},
    "j0_coset_on": ptm["j0_coset_on"],
    "ptm3": {k: ptm[k] for k in ("PTM3_census_random", "PTM3_R05_R06", "PTM3_stage0_floor_rows",
                                 "PTM3_ptm5_census_quantiles")},
    "ptm4": ptm["PTM4_fisher"],
    "ptm5_pooled": p5["pooled"], "ptm5_aggregate_T": p5["aggregate_T"], "ptm5_first_moment_SS": p5["first_moment_SS"],
    "ptm5_vs_census_12_24_frozen_on": {k: v for k, v in p5["census_vs_ptm5_12_24"].items()
                                       if k.startswith("frozen|") and "|on|" in k},
    "census_on_generic_firing_by_band": census_band,
    "ptm5_on_frozen_by_rung": ptm5_by_rung,
    "census_on_generic_median_frozen_by_rung": on_med,
}
dump("summary.json", out)
print(json.dumps({k: out[k] for k in ("census_on_generic_firing_by_band", "census_on_generic_median_frozen_by_rung")}, indent=0))
