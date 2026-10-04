"""J4: programmatic comparison of the validator's own recomputation (recomputed.json) with the archived
decision-rules.json and cell-summary.json, plus an exact recomputation of trial-plan-v1.json's power table
(compared at 18 significant digits / log10 to 1e-12) and of secondary distributions from the raw records.
usage: python3 compare.py <run_dir> <trial_plan_path>
"""
import gzip
import json
import math
import os
import statistics
import sys
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
RUN, PLAN = sys.argv[1], sys.argv[2]
mine = json.load(open(os.path.join(HERE, "recomputed.json")))
dr = json.load(open(os.path.join(RUN, "decision-rules.json")))
cs = json.load(open(os.path.join(RUN, "cell-summary.json")))
plan = json.load(open(PLAN))
rows = []


def cmp(item, m, a, floor_ceiling):
    rows.append({"item": item, "recomputed": m, "recorded": a, "equal": m == a, "floor_or_ceiling": floor_ceiling})


def r6(x):
    return None if x is None else round(float(x), 6)


D1 = dr["N19-DR-1"]
cmp("N19-DR-1 w", mine["N19-DR-1"]["w"], D1["inputs"]["w"], "CEILING (w = N = 400)")
cmp("N19-DR-1 N_L1 / N_L2", [mine["N19-DR-1"]["N_L1"], mine["N19-DR-1"]["N_L2"]], [D1["inputs"]["N_L1"], D1["inputs"]["N_L2"]], "CEILING (no uncertified, no undetermined system)")
cmp("N19-DR-1 labels L1 / L2", [mine["N19-DR-1"]["L1"], mine["N19-DR-1"]["L2"]], [D1["label_L1"], D1["label_L2"]], "CEILING")
cmp("N19-DR-1 verdict", mine["N19-DR-1"]["verdict"], D1["verdict"], "CEILING")
cmp("N19-DR-1 CP95 (L1)", [r6(x) for x in mine["N19-DR-1"]["cp95_L1"]], [r6(x) for x in D1["inputs"]["cp95_L1"]["cp95"]], "CEILING (x = n: lower = 0.025^(1/400) closed form)")
cmp("N19-DR-1 E-PERSIST / E-DECAY falsified", [mine["N19-DR-1"]["E-PERSIST_falsified"], mine["N19-DR-1"]["E-DECAY_falsified"]],
    [D1["E-PERSIST_falsified_L1"], D1["E-DECAY_falsified_L1"]], "CEILING")
cmp("N19-DR-1 n = 17 CP95 lower of 386/386", r6(mine["N19-DR-1"]["n17_cp95_lower_386_of_386"]), r6(float(D1["n17_reference"]["cp95_lower_386_386"])), "CEILING (x = n closed form 0.025^(1/386))")
cmp("N19-DR-1 n = 17 comparison line", mine["N19-DR-1"]["n17_comparison"], D1["n17_comparison"], "CEILING (both upper bounds are 1)")
D2 = dr["N19-DR-2"]
cmp("N19-DR-2 m (verified M_4, S3-U400)", mine["N19-DR-2"]["m_verified_M4"], D2["inputs"]["m"], "FLOOR (0/400)")
cmp("N19-DR-2 CP95", [r6(x) for x in mine["N19-DR-2"]["cp95"]], [r6(x) for x in D2["inputs"]["cp95"]["cp95"]], "FLOOR (x = 0: upper = 1 - 0.025^(1/400))")
cmp("N19-DR-2 verdict", mine["N19-DR-2"]["verdict"], D2["verdict"], "FLOOR")
cmp("N19-DR-2 conditional W_4 rate on M_4-non-refuted", [mine["N19-DR-2"]["conditional_W4_rate_on_M4_nonrefuted"]["x"], mine["N19-DR-2"]["conditional_W4_rate_on_M4_nonrefuted"]["n"]],
    [D2["inputs"]["W_4_rate_on_S3-U400_not_M4_refuted"]["k"], D2["inputs"]["W_4_rate_on_S3-U400_not_M4_refuted"]["n"]], "CEILING (400/400)")
cmp("N19-DR-2 M_3 count", mine["N19-DR-2"]["M3_count_engine"], D2["inputs"]["M_3_count"], "FLOOR (0)")
D3 = dr["N19-DR-3"]
m3 = mine["N19-DR-3"]
cmp("N19-DR-3 N_b", m3["N_b"], D3["inputs"]["N_b"], "CEILING (400/400 applicable)")
cmp("N19-DR-3 sigma >0 / =0 / <0", [m3["sigma_gt_0"], m3["sigma_eq_0"], m3["sigma_lt_0"]],
    [D3["inputs"]["sigma_gt_0"], D3["inputs"]["sigma_eq_0"], D3["inputs"]["sigma_lt_0"]], "CEILING for sigma > 0 (400/400); FLOOR for = 0 and < 0")
cmp("N19-DR-3 FULL (1160)", [m3["full_1160"], m3["full_fraction"]], [D3["inputs"]["FULL_1160"], D3["inputs"]["FULL_fraction"]], "FLOOR (0)")
cmp("N19-DR-3 R'_4 profile distribution", m3["R4_profile_distribution"], D3["inputs"]["profile_distribution"], "not at a bound: a 14-profile distribution; INFORMATIVE")
cmp("N19-DR-3 verdict", m3["verdict"], D3["verdict"], "CEILING")
D4 = dr["N19-DR-4"]["comparisons"]
for X in ("N-F219", "N-AFF19", "N-ELL19"):
    for c in ("W_4", "M_4"):
        rec = D4[X][c]
        mm = mine["N19-DR-4"][c][X]
        cmp(f"N19-DR-4 {c} vs {X}: verdict and counts",
            [mm["verdict"], mm["X_count"], r6(mm["X_cp95_upper"]), r6(mm["S3_cp95_lower"])],
            [rec["verdict"], f"{rec['X']['k']}/{rec['X']['n']}", r6(rec["X"]["cp95"][1]), r6(rec["S3"]["cp95"][0])],
            "BOTH ARMS AT BOUNDS (S3 ceiling / X floor at W_4; both floor at M_4)")
famrec = dr["N19-DR-4"]["inputs"]["per_family_N-AFF19"]
fam_m = mine["N19-DR-4"]["W_4"]["N-AFF19_per_family"]
cmp("N19-DR-4 N-AFF19 per-family unsat counts (W_4, M_4)",
    {d: [fam_m[str(d)]["X_count"], mine["N19-DR-4"]["M_4"]["N-AFF19_per_family"][str(d)]["X_count"]] for d in range(1, 6)},
    {d: [f"{famrec[f'{d}|unsat']['W_4']['k']}/{famrec[f'{d}|unsat']['W_4']['n']}", f"{famrec[f'{d}|unsat']['M_4']['k']}/{famrec[f'{d}|unsat']['M_4']['n']}"] for d in range(1, 6)},
    "FLOOR (0/40 each)")
D5 = dr["N19-DR-5"]
m5 = mine["N19-DR-5"]
cmp("N19-DR-5 w_c / n_c, verdict, AT S3 RATE, ABOVE N-ELL19, ABOVE N-F219",
    [m5["w_c"], m5["n_c"], m5["verdict"], m5["AT_S3_RATE"], m5["N-CONV19_ABOVE_N-ELL19"], m5["N-CONV19_ABOVE_N-F219"]],
    [D5["inputs"]["w_c"], D5["inputs"]["n_c"], D5["verdict"], D5["AT_S3_RATE"], D5["N-CONV19_ABOVE_N-ELL19"], D5["N-CONV19_ABOVE_N-F219"]],
    "CEILING (200/200)")
p2 = D5["inputs"]["paired_2x2_on_shared_x_R"]
cmp("N19-DR-5 paired 2 x 2 (W_4, M_4)",
    {c: [m5["paired_2x2_on_shared_x_R"][c][k] for k in ("S3_ref&CONV_ref", "S3_ref&CONV_not", "S3_not&CONV_ref", "S3_not&CONV_not")] for c in ("W_4", "M_4")},
    {c: [p2[c][k] for k in ("S3+ CONV+", "S3+ CONV-", "S3- CONV+", "S3- CONV-")] for c in ("W_4", "M_4")},
    "DEGENERATE (all mass in one cell each)")
D6 = dr["N19-DR-6"]["results"]
for c in ("M_4", "W_4"):
    cmp(f"N19-DR-6 {c}: table, Fisher p, verdict, X2E replicates primary",
        [mine["N19-DR-6"][c]["X2E"], mine["N19-DR-6"][c]["pooled_XE-NOT-2E+TWIST"], mine["N19-DR-6"][c]["fisher_one_sided_p"], mine["N19-DR-6"][c]["verdict"], mine["N19-DR-6"][c]["RANDX_X2E_REPLICATES_PRIMARY"]],
        [f"{D6[c]['table']['X2E'][0]}/{sum(D6[c]['table']['X2E'])}", f"{D6[c]['table']['pooled XE-NOT-2E + TWIST'][0]}/{sum(D6[c]['table']['pooled XE-NOT-2E + TWIST'])}", D6[c]["fisher_one_sided_p"], D6[c]["verdict"], D6[c]["RANDX_X2E_REPLICATES_PRIMARY"]],
        "SATURATED: " + ("FLOOR (0 refuted in both groups)" if c == "M_4" else "CEILING (all refuted in both groups)"))
D7 = dr["N19-DR-7"]["per_arm"]
for a, v in D7.items():
    mm = mine["N19-DR-7"][a]["both_roles"]
    cmp(f"N19-DR-7 {a} (both roles)", [mm["n"], mm["with_reference_profile"], mm["verdict"], mm["T5_fraction"]],
        [v["systems"], v["with_reference_profile"], v["verdict"], v["T5_applicable_fraction"]],
        "AT A BOUND (fraction " + str(mm["fraction"]) + ")")
cmp("N19-DR-7 unsat-only reading gives the same verdict on every arm", all(mine["N19-DR-7"][a]["readings_agree"] for a in mine["N19-DR-7"]), True, "n/a")
cmp("N19-DR-9 mechanical flag", mine["N19-DR-9"]["mechanical_flag"], dr["N19-DR-9"]["flag"], "follows N19-DR-1 at its ceiling")
cmp("N19-DR-10 primary", mine["N19-DR-10"]["primary"], dr["N19-DR-10"]["primary"], "n/a")
# cell-summary MR items
cmp("MR19-1 w / N / CP95", [mine["MR19-1"]["w"], mine["MR19-1"]["N"], [r6(x) for x in mine["MR19-1"]["cp95"]]],
    [cs["MR19-1"]["w"], cs["MR19-1"]["N"], [r6(x) for x in cs["MR19-1"]["cp95"]["cp95"]]], "CEILING")
cmp("MR19-1 counts wdag-v1 only (0 flat W_4 certificates with max|mu| <= 2)", mine["MR19-1"]["flat_W4_certs_counting_toward_W4"], 0, "n/a")
cmp("MR19-2 counts", mine["MR19-2"], {k: cs["MR19-2"][k] for k in ("N_b", "sigma_gt_0", "sigma_eq_0", "sigma_lt_0")} | {"full_1160": cs["MR19-2"]["FULL_1160"]}, "CEILING / FLOOR as N19-DR-3")
cmp("MR19-3 certificates per (closure, arm, format)", {k: {kk: v[kk] for kk in ("submitted", "verified", "failed", "counting")} for k, v in mine["certificate_recount"].items()},
    cs["MR19-3"]["certificates"], "CEILING (all verified; 0 failed)")
pa = cs["MR19-3"]["per_arm"]
mp = mine["MR19-3"]["per_arm_unsat"]
def cnt(s):
    return s.split(" ")[0] if isinstance(s, str) else f"{s['k']}/{s['n']}"
recp = {a: [f"{pa[a + '|unsat']['W_4']['k']}/{pa[a + '|unsat']['W_4']['n']}", f"{pa[a + '|unsat']['M_4']['k']}/{pa[a + '|unsat']['M_4']['n']}", f"{pa[a + '|unsat']['M_3']['k']}/{pa[a + '|unsat']['M_3']['n']}"] for a in mp}
myp = {a: [f"{mp[a]['W_4']['x']}/{mp[a]['W_4']['n']}", f"{mp[a]['M_4']['x']}/{mp[a]['M_4']['n']}", f"{mp[a]['M_3_engine']}/{mp[a]['W_4']['n']}"] for a in mp}
cmp("MR19-3 per-arm unsat counts (W_4, M_4, M_3)", myp, recp, "EVERY ARM AT A BOUND (0 or all)")
cmp("MR19-3 per-arm CP95 upper bounds at 0/n and lower at n/n", {a: [r6(mp[a]["W_4"]["cp95"][0]), r6(mp[a]["W_4"]["cp95"][1])] for a in mp},
    {a: [r6(pa[a + '|unsat']["W_4"]["cp95"][0]), r6(pa[a + '|unsat']["W_4"]["cp95"][1])] for a in mp}, "BOUNDS (closed forms)")
cmp("MR19-3 C-PS: refuted satisfiable controls, codim < s, codim = s among s <= 31",
    [mine["C-PS_recount"]["refuted_any"], mine["C-PS_recount"]["codim_lt_s"], [mine["C-PS_recount"]["codim_eq_s_where_s_le_31"], mine["C-PS_recount"]["s_le_31"]]],
    [cs["MR19-3"]["C-PS"]["refuted_W_4"] + cs["MR19-3"]["C-PS"]["refuted_M_4"] + cs["MR19-3"]["C-PS"]["refuted_M_3"], 300 - cs["MR19-3"]["C-PS"]["codim_ge_s"], cs["MR19-3"]["C-PS"]["codim_eq_s_among_s_le_31"]],
    "FLOOR for refutations (0); codim = s 150/300 is NOT at a bound (informative)")
cmp("MR19-3 ann-v1 submitted / verified", [mine["ann-v1"]["submitted"], mine["ann-v1"]["verified_recount"]], [cs["MR19-3"]["ann_v1"]["submitted"], cs["MR19-3"]["ann_v1"]["verified"]], "CEILING (15/15)")

# ---------------------------------------------------------------- secondary distributions from raw records
clo = [json.loads(l) for l in gzip.open(os.path.join(RUN, "closures.jsonl.gz"), "rt")]
der = {}
for arm in sorted({r["arm"] for r in clo}):
    rs = [r for r in clo if r["arm"] == arm]
    dd = {}
    for f in ("P", "fallen", "linear_forms", "syzygy_excess"):
        vals = [r["derived"][f] for r in rs]
        # own derivation from the M_4 record
        own = []
        for r in rs:
            d = r["M_4"]["dims_by_deg"]
            own.append({"P": r["M_4"]["rank"] - d[3], "fallen": d[3], "linear_forms": d[1] - d[0], "syzygy_excess": 3819 - r["M_4"]["rank"]}[f])
        assert own == vals, (arm, f)
        dd[f] = {"max": max(vals), "median": float(statistics.median(vals)), "min": min(vals),
                 "mode_counts": {str(k): v for k, v in sorted(Counter(vals).items())}}
    der[arm] = dd
recder = cs["secondary"]["derived_distributions"]
cmp("secondary derived distributions (P, fallen, linear_forms, syzygy_excess) recomputed from M_4 records", der,
    {a: {f: {"max": v[f]["max"], "median": float(v[f]["median"]), "min": v[f]["min"], "mode_counts": {str(k): c for k, c in sorted(((int(k), c) for k, c in v[f]["mode_counts"].items()))}} for f in v} for a, v in recder.items()},
    "mixed; several at constants (P, N-F219/N-AFF19 all 0 excess)")
# explanation check: the recorded mode_counts is a TOP-5 truncation (by count) of the full distribution
rec_norm = {a: {f: {"max": v[f]["max"], "median": float(v[f]["median"]), "min": v[f]["min"], "mode_counts": v[f]["mode_counts"]} for f in v} for a, v in recder.items()}
trunc_ok = True
for a in der:
    for f in der[a]:
        full = {k: c for k, c in der[a][f]["mode_counts"].items()}
        recm = {str(k): c for k, c in rec_norm[a][f]["mode_counts"].items()}
        top_counts = sorted(full.values(), reverse=True)[:5]
        same_summary = all(der[a][f][x] == rec_norm[a][f][x] for x in ("max", "median", "min"))
        subset = all(full.get(k) == c for k, c in recm.items())
        is_top5 = len(recm) == min(5, len(full)) and sorted(recm.values(), reverse=True) == top_counts
        trunc_ok &= same_summary and subset and is_top5
cmp("secondary derived distributions: recorded mode_counts equal the TOP-5 (by count) of my full distributions; max/median/min equal", trunc_ok, True,
    "explains the DIFF above: undisclosed top-5 truncation in a descriptive field; no value differs")
it = Counter(f"{r['arm']}|{r['role']}|it={r['W_4']['iterations_to_fixpoint']},first1={r['W_4']['one_first_iteration']}" for r in clo)
recit = {f"{k}|{kk}": v for k, d in cs["secondary"]["W_4_iteration_distribution"].items() for kk, v in d.items()}
cmp("secondary W_4 iteration distribution", dict(sorted(it.items())), dict(sorted(recit.items())), "every arm-role at a single value")
# draw statistics from the ARCHIVED draw logs and from the validator's replay logs
ds = {}
for arm in ("S3-PRIMARY", "N-CONV19", "N-ELL19", "N-F219", "N-AFF19", "F-RANDX19"):
    L = [json.loads(l) for l in gzip.open(os.path.join(RUN, f"draws-{arm}.jsonl.gz"), "rt")]
    Lm = [json.loads(l) for l in gzip.open(os.path.join(HERE, "..", "j2-population", f"my-draws-{arm}.jsonl.gz"), "rt")]
    with_s = [r for r in L if "s" in r]
    ds[arm] = {"attempts": len(L), "outcomes": dict(Counter(r["outcome"] for r in L)), "with_s": len(with_s),
               "unsat_fraction_among_classified": sum(1 for r in with_s if r["s"] == 0) / len(with_s),
               "replay_outcomes_equal": Counter(r["outcome"] for r in L) == Counter(r["outcome"] for r in Lm)}
recds = cs["secondary"]["draw_statistics"]
cmp("secondary draw statistics", {a: [v["attempts"], v["outcomes"], v["with_s"], round(v["unsat_fraction_among_classified"], 12)] for a, v in ds.items()},
    {a: [v["attempts"], v["outcomes"], v["with_s"], round(v["unsat_fraction_among_classified"], 12)] for a, v in recds.items()}, "descriptive")
cmp("draw statistics: my replay's outcome counts equal the archived logs", all(v["replay_outcomes_equal"] for v in ds.values()), True, "n/a")


# ---------------------------------------------------------------- power table (exact)
def cdf_le(x, n, p):
    q = 1 - p
    return sum(Fraction(math.comb(n, k)) * p ** k * q ** (n - k) for k in range(x + 1))


def dec(f):
    return Decimal(f.numerator) / Decimal(f.denominator)


pt_bad = []
for row in plan["power_table"]["rows"]:
    p = Fraction(row["p"])
    vals = {"N400_P(w>=360)": 1 - cdf_le(359, 400, p), "N400_P(w<=40)": cdf_le(40, 400, p), "N400_P(w<=200)": cdf_le(200, 400, p),
            "n200_P(count>=180)": 1 - cdf_le(179, 200, p), "n200_P(count<=20)": cdf_le(20, 200, p)}
    for k, f in vals.items():
        rec = Decimal(row[k]["value"])
        mv = dec(f)
        if mv == 0:
            ok = rec == 0
        else:
            ok = abs(rec - mv) / abs(mv) < Decimal("1e-18")
        lg = (Decimal(f.numerator).ln() - Decimal(f.denominator).ln()) / Decimal(10).ln() if f else None
        okl = lg is not None and abs(Decimal(row[k]["log10"]) - lg) < Decimal("1e-12")
        if not (ok and okl):
            pt_bad.append({"p": row["p"], "item": k, "recorded": row[k], "mine": str(mv)[:30], "mine_log10": str(lg)[:30]})
cp_bad = []
mine_cp = mine["power_table_recomputed"]["cp95"]
for k, v in plan["power_table"]["cp95_bounds"].items():
    if [round(v[0], 8), round(v[1], 8)] != [round(x, 8) for x in mine_cp[k]]:
        cp_bad.append({k: [v, mine_cp[k]]})
cmp("trial-plan power table (40 exact tail values, value to 1e-18 relative and log10 to 1e-12)", len(pt_bad), 0, "n/a")
cmp("trial-plan CP95 bounds at 0/200, 200/200, 0/400, 400/400, 386/386 (8 decimals)", cp_bad, [], "n/a")

res = {"rows": rows, "n_items": len(rows), "n_equal": sum(1 for r in rows if r["equal"]),
       "all_equal": all(r["equal"] for r in rows), "power_table_mismatches": pt_bad,
       "trial_plan_written_utc": plan.get("written_utc"), "power_table_method_recorded": plan["power_table"].get("method")}
json.dump(res, open(os.path.join(HERE, "comparison-table.json"), "w"), indent=1, default=str)
for r in rows:
    print(("OK  " if r["equal"] else "DIFF") + " | " + r["item"] + " | " + r["floor_or_ceiling"])
print("ALL_EQUAL", res["all_equal"], res["n_equal"], "/", res["n_items"])
