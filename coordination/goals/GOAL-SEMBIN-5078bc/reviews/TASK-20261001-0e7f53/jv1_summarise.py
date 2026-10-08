"""JV-1: collect the per-degree figures quoted in validation_report.yaml from
the *_output.json files in this directory (no new computation)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(name):
    return json.loads((HERE / name).read_text())


fc = load("jv1_fill_charge_variants_output.json")
pre = load("jv1_precomputation_readings_output.json")
cm = load("jv1_continuous_minima_output.json")
dp = load("jv1_diff_primary_output.json")
fav = load("jv1_favourable_constants_output.json")
degs = ["97", "109", "131", "163", "191", "233", "239", "283", "409", "571"]
S = {}
for n in degs:
    v2 = fc["V2"]["per_degree_min"][n]
    vd = fc["VD"]["per_degree_min"][n]
    nf = fc["VNOFILL"]["per_degree_min"][n]
    r = pre["v2_rows"][n]["readings"]
    p3a = min(v["min_margin"] for k, v in r.items() if k.startswith("P3a") and "BLopt" not in k)
    p3b = min(v["min_margin"] for k, v in r.items() if k.startswith("P3b") and "BLopt" not in k)
    p3_neg = sum(v["negatives"] for k, v in r.items() if k.startswith("P3"))
    ext = pre["EXT_exploratory"][n]
    ext_t = {k: v for k, v in ext.items() if k.startswith("t")}
    S[n] = dict(
        v2_grid_margin_VOW=round(v2["margin_vs_VOW"], 3),
        realD_margin_VOW=round(dp["D5_per_degree_minimum"][n]["mine_continuous_margin_vs_VOW"], 3),
        grid_minus_realD=round(dp["D5_per_degree_minimum"][n]["mine_grid_margin_vs_VOW"]
                               - dp["D5_per_degree_minimum"][n]["mine_continuous_margin_vs_VOW"], 3),
        realD_minus_E2=round(dp["D5_per_degree_minimum"][n]["continuous_minus_E2"], 3),
        VD_margin_VOW=round(vd["margin_vs_VOW"], 3),
        VD_minus_v2=round(vd["TOTAL"] - v2["TOTAL"], 3),
        C2_alone_margin_VOW=round(nf["margin_vs_VOW"], 3),
        P1_min_margin_best_online=round(r["P1_vs_best_online"]["min_margin"], 2),
        P1_min_margin_VOW=round(r["P1_vs_VOW"]["min_margin"], 2),
        P1_min_margin_CGK=round(r["P1_vs_CGK"]["min_margin"], 2),
        P2_min_margin_best_online=round(r["P2_vs_best_online"]["min_margin"], 2),
        P2_min_margin_VOW=round(r["P2_vs_VOW"]["min_margin"], 3),
        P2_min_margin_CGK=round(r["P2_vs_CGK"]["min_margin"], 2),
        P3a_min_margin_best_multi=round(p3a, 2),
        P3b_min_margin_best_multi=round(p3b, 2),
        P_negatives_all_readings=sum(v["negatives"] for v in r.values()),
        EXT_min_vs_KS=round(min(v["KS"]["min_margin"] for v in ext_t.values()), 3),
        EXT_min_vs_BLopt=round(min(v["BLopt"]["min_margin"] for v in ext_t.values()), 3),
        EXT_min_vs_best=round(min(v["best"]["min_margin"] for v in ext_t.values()), 3),
        EXT_online_vs_BL_on=round(ext["online_vs_BL_on_a_le_N_over_2"]["min_margin"], 2),
        FAV_G1_margin_VOW=round(fav["G1"]["per_degree"][n]["margin_vs_VOW"], 2),
        FAV_G2_margin_VOW=round(fav["G2"]["per_degree"][n]["margin_vs_VOW"], 2),
    )
out = dict(per_degree=S,
           VDB_per_budget_largest_drop=None,
           continuous=dict(max_row_excess=cm["max_row_excess"], worst_per_budget=cm["worst_per_budget_excess"],
                           by_model=cm["by_model"]))
v2pb = fc["V2"]["per_budget_min_MITM_CAPPED"]
vdbpb = fc["VDB"]["per_budget_min_MITM_CAPPED"]
drops = {k: vdbpb[k]["TOTAL"] - v2pb[k]["TOTAL"] for k in v2pb}
worst = min(drops.items(), key=lambda kv: kv[1])
out["VDB_per_budget_largest_drop"] = dict(key=worst[0], drop=worst[1],
                                          min_margin_VOW=min(v["margin_vs_VOW"] for v in vdbpb.values()),
                                          B80_drops={k: round(v, 3) for k, v in drops.items() if k.endswith("|80")})
(HERE / "jv1_summary.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
