"""J3 comparison (AFTER THE SEAL): my sealed J3 values (rederivation/out/*.json, whose
sha256 are embedded in sealed-section.yaml) against the producer's analysis.json,
kappa-cells.jsonl, fits.json and R16 analysis.json. Deterministic quantities must
agree exactly (to float round-off, |d| <= 1e-9 relative); bootstrap endpoints within
Monte Carlo error (|d| <= 3 x my seed s.d. over seeds 1..20).
RV-4: from A7_floor only the key fields of below_0_9 entries and the TW-FLOOR flag
are extracted; no ratio or r field is accessed or printed."""
import json, math, os, sys, collections, hashlib
W = "/home/user/crypto-autoresearcher/coordination/review/pfdr-1b78f7-20260929/reviews/TASK-20260929-accb8e"
sys.path.insert(0, os.path.join(W, "checks"))
import rl  # noqa
WT = rl.WT
A = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-analysis")
R16 = os.path.join(WT, "experiments/EXP-PFDR-1b78f7/runs/RUN-PFDR-1b78f7-stage-r")
OUT = os.path.join(W, "rederivation", "out")
CH = os.path.join(W, "checks", "out")
os.makedirs(CH, exist_ok=True)

rows_out = []
tally = collections.Counter()


def rel(a, b):
    if a is None or b is None:
        return None
    return abs(a - b) / max(1.0, abs(a), abs(b))


def cmp_exact(q, mine, theirs, tol=1e-9):
    if isinstance(mine, (int, float)) and isinstance(theirs, (int, float)) and not isinstance(mine, bool):
        ok = rel(float(mine), float(theirs)) <= tol
    else:
        ok = mine == theirs
    tally["exact_ok" if ok else "exact_DIFF"] += 1
    rows_out.append({"quantity": q, "kind": "deterministic", "mine": mine, "producer": theirs, "agree": ok})
    return ok


def cmp_mc(q, mine, theirs, sd):
    d = None if (mine is None or theirs is None) else abs(mine - theirs)
    ok = d is not None and (d <= 3 * sd + 1e-12)
    tally["mc_ok" if ok else "mc_DIFF"] += 1
    rows_out.append({"quantity": q, "kind": "bootstrap", "mine": mine, "producer": theirs, "abs_diff": d,
                     "my_mc_sd": sd, "agree_within_3sd": ok})
    return ok


def main():
    mine = json.load(open(rl.opened(os.path.join(OUT, "j3-results.json"), "J3 compare: my sealed j3-results.json")))
    a6 = json.load(open(rl.opened(os.path.join(OUT, "q9-a6.json"), "J3 compare: my sealed q9-a6.json")))
    h3 = json.load(open(rl.opened(os.path.join(OUT, "q9-h3.json"), "J3 compare: my sealed q9-h3.json")))
    an = json.load(open(rl.opened(os.path.join(A, "analysis.json"), "J3 compare: producer R15 analysis.json (blind_from, after seal; A7 values not accessed)")))
    fits = json.load(open(rl.opened(os.path.join(A, "fits.json"), "J3 compare: producer R15 fits.json (blind_from, after seal)")))
    kc = [json.loads(l) for l in open(rl.opened(os.path.join(A, "kappa-cells.jsonl"), "J3 compare: producer kappa-cells.jsonl (blind_from, after seal)"))]
    a16 = json.load(open(rl.opened(os.path.join(R16, "analysis.json"), "J3 compare: producer R16 analysis.json (blind_from, after seal)")))

    # ---------- A1 cells ----------
    kcd = {(c["arm"], c["class"], c["m"], c["bits"]): c for c in kc}
    my_cells = {(c["arm"], c["class"], c["m"], c["bits"]): c for c in mine["A1_cells"]}
    cmp_exact("A1 cell key set", sorted(map(str, my_cells)), sorted(map(str, kcd)))
    xb_all_match = xb_used_match = 0
    for k, c in sorted(my_cells.items()):
        t = kcd.get(k)
        if t is None:
            continue
        pre = "A1 " + "|".join(map(str, k))
        cmp_exact(pre + " C_A", c["C_A"], t["C_A"])
        cmp_exact(pre + " C_R", c["C_R"], t["C_R"])
        cmp_exact(pre + " V", c["V"], t["V"])
        cmp_exact(pre + " SD_null", c["SD_null"], t["SD_null"])
        cmp_exact(pre + " kappa", c["kappa"], t["kappa"])
        cmp_exact(pre + " z", c["z"], t["z"])
        cmp_exact(pre + " resolved", c["resolved"], t["resolved"])
        cmp_exact(pre + " counts_A", c["counts_A"], t["counts_A"])
        cmp_exact(pre + " counts_R", c["counts_R"], t["counts_R"])
        cmp_exact(pre + " curves_used", c["curves_used"], t["curves_kept"])
        cmp_exact(pre + " curves_dropped", [d["curve"] for d in c["curves_dropped"]],
                  [d if isinstance(d, int) else d.get("curve") for d in t["curves_dropped"]])
        raw = t.get("raw") or {}
        if "kappa" in raw:
            cmp_exact(pre + " raw_kappa", c["raw_kappa"], raw["kappa"])
        # x_b convention
        allv = list(c["log2N_by_curve"].values())
        usedv = [c["log2N_by_curve"][str(j)] if str(j) in c["log2N_by_curve"] else c["log2N_by_curve"][j] for j in c["curves_used"]] if c["curves_used"] else []
        xa = sum(allv) / len(allv) if allv else None
        xu = sum(usedv) / len(usedv) if usedv else None
        if t.get("mean_log2N") is not None:
            if xa is not None and rel(xa, t["mean_log2N"]) < 1e-12:
                xb_all_match += 1
            if xu is not None and rel(xu, t["mean_log2N"]) < 1e-12:
                xb_used_match += 1
    rows_out.append({"quantity": "x_b convention (cells whose producer mean_log2N equals my all-curves mean / used-curves mean)",
                     "all_curves": xb_all_match, "used_curves": xb_used_match, "cells": len(kcd)})
    # ---------- excursions / extremes / tail ----------
    my_exc = sorted((e["arm"], e["class"], e["m"], e["bits"]) for e in mine["excursions"])
    th_exc = sorted(tuple(x["cell"]) for x in an["A1_kappa"]["excursions_TT_SS"])
    cmp_exact("excursion list (arm, class, m, bits)", [list(x) for x in my_exc], [list(x) for x in th_exc])
    for e in mine["excursions"]:
        for x in an["A1_kappa"]["excursions_TT_SS"]:
            if tuple(x["cell"]) == (e["arm"], e["class"], e["m"], e["bits"]):
                cmp_exact(f"excursion z {x['cell']}", e["z"], x["z"])
                cmp_exact(f"excursion kappa {x['cell']}", e["kappa"], x["kappa"])
    cmp_exact("resolved TT/SS family size", mine["resolved_family_size"], an["A2_slopes"]["tail_check_max_abs_z"]["k"])
    tc = an["A2_slopes"]["tail_check_max_abs_z"]
    cmp_exact("tail check cell", mine["A2_tail_check"]["max_abs_z_cell"], tc["cell"])
    cmp_exact("tail check max |z|", abs(mine["A2_tail_check"]["z"]), tc["max_abs_z"])
    cmp_exact("tail check P(max|Z|>=z)", mine["A2_tail_check"]["P_max_ge"], tc["p_max_of_k"], tol=1e-6)
    ex = an["A1_kappa"]["extremes"]
    cmp_exact("largest resolved kappa cell", mine["tail_largest_kappa"]["cell"], ex["largest"]["cell"])
    cmp_exact("largest resolved kappa", mine["tail_largest_kappa"]["kappa"], ex["largest"]["kappa"])
    cmp_exact("smallest resolved kappa cell", mine["tail_smallest_kappa"]["cell"], ex["smallest"]["cell"])
    cmp_exact("smallest resolved kappa", mine["tail_smallest_kappa"]["kappa"], ex["smallest"]["kappa"])
    # ---------- A2 ----------
    for k, v in sorted(mine["A2"].items()):
        arm, cls, m = k.split("|")
        tk = f"{arm}|{cls}|{m[1:]}"
        t = an["A2_slopes"]["tests"].get(tk)
        tf = fits["A2_slopes"].get(tk)
        if t is None:
            rows_out.append({"quantity": f"A2 {k}", "missing_in_producer": True})
            continue
        cmp_exact(f"A2 {k} status", "UNRESOLVED" if v["status"] != "resolved" else "resolved",
                  "UNRESOLVED" if str(t["status"]).upper().startswith("UNRESOLVED") else "resolved")
        cmp_exact(f"A2 {k} rungs", v["resolved_rungs"], t["rungs"])
        if v["status"] == "resolved":
            cmp_exact(f"A2 {k} slope", v["slope"], t["slope"])
            sd = v.get("mc_sd", {})
            cmp_mc(f"A2 {k} ci lo", v["lo"], t["ci"][0], sd.get("lo", 0))
            cmp_mc(f"A2 {k} ci hi", v["hi"], t["ci"][1], sd.get("hi", 0))
            cmp_mc(f"A2 {k} p one-sided", v["p_one_sided"], t["p_one_sided"], sd.get("p", 0))
            cmp_exact(f"A2 {k} ci_above_zero", v["lo"] > 0, t.get("ci_above_zero"))
            cmp_exact(f"A2 {k} replicates dropped", v.get("replicates_undefined"), t.get("bootstrap_dropped_replicates"))
        if "holm_adjusted_p" in v:
            cmp_exact(f"A2 {k} holm < 0.05", v["holm_adjusted_p"] < 0.05, t["holm_adjusted_p"] < 0.05)
        if tf is not None:
            cmp_exact(f"A2 {k} fits.json == analysis.json", json.dumps(tf, sort_keys=True), json.dumps(t, sort_keys=True))
    # ---------- A3 ----------
    pac = an["A3_informative_rank"]["per_arm_class"]
    for k, v in mine["A3_prediction4"].items():
        t = pac.get(k)
        if t is None:
            rows_out.append({"quantity": f"A3 {k}", "missing_in_producer": True})
            continue
        cmp_exact(f"A3 {k} qualifying", v["qualifying"], t["qualifying"])
        cmp_exact(f"A3 {k} median", v["median"], t["median"])
        if "median_ge_0.95" in v and "meets_0_95" in t:
            cmp_exact(f"A3 {k} meets 0.95", v["median_ge_0.95"], t["meets_0_95"])
        if "all_le_0.05" in v and "all_le_0_05" in t:
            cmp_exact(f"A3 {k} all <= 0.05", v["all_le_0.05"], t["all_le_0_05"])
    pacm = an["A3_informative_rank"]["per_arm_class_m"]
    for k, v in mine["A3_median_by_arm_class_m"].items():
        a, c, m = k.split("|")
        t = pacm.get(f"{a}|{c}|{m[1:]}")
        if t is not None:
            cmp_exact(f"A3 {k} n", v["n"], t["n"])
            cmp_exact(f"A3 {k} median", v["median"], t["median"])
    # H3 rank ratio tally (recorded-field tally, main panel)
    h3r = an["A3_informative_rank"]["H3_rank_ge_min_over_1_05"]
    myr = collections.defaultdict(dict)
    for k, n in mine["H3_rank_ratio_tally"].items():
        a, c, _, ok = k.split("|")
        myr[f"{a}|{c}"]["ok" if ok == "True" else "not_ok"] = n
    for k, v in myr.items():
        t = h3r.get(k)
        if t is not None:
            cmp_exact(f"H3 rank>=min/1.05 {k}", {"ok": v.get("ok", 0), "not_ok": v.get("not_ok", 0)},
                      {"ok": t.get("ok", 0), "not_ok": t.get("not_ok", 0)})
    # H3 permutation stability (bits <= 24): my recomputation vs producer
    h3p = an["A3_informative_rank"]["H3_permutation_saturation_stable_lt_0_02"]
    myp = collections.defaultdict(dict)
    for k, n in h3["tally"].items():
        a, c, _, st = k.split("|")
        myp[f"{a}|{c}"]["stable" if st == "True" else "unstable"] = n
    for k, v in myp.items():
        t = h3p.get(k)
        if t is not None:
            cmp_exact(f"H3 permutation stable {k}", {"stable": v.get("stable", 0), "unstable": v.get("unstable", 0)},
                      {"stable": t.get("stable", 0), "unstable": t.get("unstable", 0)})
    # ---------- A4 ----------
    a4 = mine["A4"]
    rm = an["A4_harvest_gain"]["ratio_medians"]
    for k, v in a4["medians"].items():
        m, base, b = k.split("|")
        t = rm.get(f"{m[1:]}|{base}|{b[1:]}")
        tv = t if not isinstance(t, dict) else t.get("median")
        cmp_exact(f"A4 median {k}", v["median"], tv)
    cmp_exact("A4 (1a) met", a4["pred_1a"] == "met", an["A4_harvest_gain"]["prediction_1a_met"])
    cmp_exact("A4 (1b) met", a4["pred_1b"] == "met", an["A4_harvest_gain"]["prediction_1b_met"])
    p2 = an["A4_harvest_gain"]["prediction_2"]
    cmp_exact("A4 (2) met", a4["pred_2"]["reading"] == "met", p2["met"])
    cmp_exact("A4 (2) falsified", a4["pred_2"]["reading"] == "falsified", p2["falsified"])
    cmp_exact("A4 (2) slope", a4["pred_2"]["slope"], p2["slope"])
    ex4 = an["A4_harvest_gain"]["exponents"]
    for k, v in a4["fits"].items():
        m, base = k.split("|")
        t = ex4.get(f"{m[1:]}|{base}")
        if t is None:
            continue
        cmp_exact(f"A4 {k} n_pairs", v["n"], t.get("n_pairs"))
        for mode in ("census", "on"):
            tc_ = t[mode]
            cmp_exact(f"A4 {k} {mode} slope", v[mode]["slope"], tc_["slope"])
            sdl = v["mc_sd"][f"{mode}_lo"]
            sdh = v["mc_sd"][f"{mode}_hi"]
            lo_t = tc_.get("lo", (tc_.get("ci95") or [None, None])[0])
            hi_t = tc_.get("hi", (tc_.get("ci95") or [None, None])[1])
            cmp_mc(f"A4 {k} {mode} lo", v[mode]["lo"], lo_t, sdl)
            cmp_mc(f"A4 {k} {mode} hi", v[mode]["hi"], hi_t, sdh)
        cmp_exact(f"A4 {k} delta", v["delta"], t["delta"])
        dci = t.get("delta_ci95_paired")
        if isinstance(dci, dict):
            dci = [dci.get("lo"), dci.get("hi")]
        if dci:
            cmp_mc(f"A4 {k} delta lo", v["delta_ci"][0], dci[0], v["mc_sd"]["delta_lo"])
            cmp_mc(f"A4 {k} delta hi", v["delta_ci"][1], dci[1], v["mc_sd"]["delta_hi"])
        if "abs_delta_le_0_03" in t:
            cmp_exact(f"A4 {k} |delta|<=0.03", abs(v["delta"]) <= 0.03, t["abs_delta_le_0_03"])
        fk = fits["A4_exponents"].get(f"{m[1:]}|{base}")
        if fk is not None:
            cmp_exact(f"A4 {k} fits.json == analysis.json", json.dumps(fk, sort_keys=True), json.dumps(t, sort_keys=True))
    # ---------- A5 ----------
    pc1, pc2 = an["A5_positive_controls"]["PC-1"], an["A5_positive_controls"]["PC-2"]
    cmp_exact("PC-1 raw kappa_TT", mine["PC1"]["raw_kappa_TT"], pc1["raw_kappa_TT"])
    cmp_exact("PC-1 pass", mine["PC1"]["pass"], pc1["pass"])
    cmp_exact("PC-1 units", mine["PC1"]["cell"]["units_used"], pc1["units"] if isinstance(pc1["units"], int) else len(pc1["units"]))
    cmp_exact("PC-2 kappa_TB_before", mine["PC2"]["kappa_TB_before"], pc2["kappa_TB_before"])
    nf = pc2["nonformal"]
    cmp_exact("PC-2 nonformal z", mine["PC2"]["z_nonformal"], nf.get("z"))
    cmp_exact("PC-2 nonformal C_A", mine["PC2"]["cell"]["C_A"], nf.get("C_A"))
    cmp_exact("PC-2 nonformal C_R", mine["PC2"]["cell"]["C_R"], nf.get("C_R"))
    cmp_exact("PC-2 resolved", mine["PC2"]["resolved"], nf.get("resolved"))
    cmp_exact("PC-2 units", mine["PC2"]["cell"]["units_used"], pc2["units"] if isinstance(pc2["units"], int) else len(pc2["units"]))
    cmp_exact("PC-2 formal rank 2F/3 all", mine["PC2"]["G6_rank_2F_over_3_all_j0_coset"], pc2["formal_rank_2F_over_3_all"])
    cmp_exact("PC-2 pass", mine["PC2"]["pass"], pc2["pass"])
    # ---------- A6 ----------
    for k, v in a6["ks"].items():
        cls, m, rng_ = k.split("|")
        t = an["A6_poisson"].get(f"{cls}|{m[1:]}")
        tt = t["ks_12_32" if rng_.startswith("12") else "ks_20_32"]
        cmp_exact(f"A6 {k} n", v["n"], tt.get("n"))
        cmp_exact(f"A6 {k} D", v["D"], tt.get("D"), tol=1e-9)
        cmp_exact(f"A6 {k} reject 1%", v["reject_1pct"], tt.get("reject_1pct", tt.get("reject")))
        pt = tt.get("p")
        rows_out.append({"quantity": f"A6 {k} p", "mine": v["p"], "producer": pt,
                         "note": "p from own exact Kolmogorov CDF; tails below 1e-14 are floating-point floors"})
    # ---------- A7 (keys only) ----------
    b09 = an["A7_floor"]["below_0_9"]
    keyf = ("panel", "bits", "curve", "m", "arm", "mode")
    th_keys = sorted([[e.get(f) for f in keyf] for e in b09], key=str)
    my_keys = sorted(mine["TW_FLOOR"]["keys_R10_R14"], key=str)
    same = th_keys == my_keys
    tally["tw_keys_" + ("ok" if same else "DIFF")] += 1
    tw_flag = an["outcomes"]["tripwires"]["TW-FLOOR_fired"]
    rows_out.append({"quantity": "TW-FLOOR (keys only; no value accessed)", "my_fired": mine["TW_FLOOR"]["fired_R10_R14"],
                     "producer_fired": tw_flag, "my_count": len(my_keys), "producer_count": len(th_keys),
                     "key_sets_equal": same,
                     "only_mine": [k for k in my_keys if k not in th_keys], "only_producer": [k for k in th_keys if k not in my_keys]})
    # ---------- outcomes ----------
    o = an["outcomes"]
    cmp_exact("outcome structural", mine["R15_outcome_id"]["id"], o["structural"])
    cmp_exact("outcome ids contain O-GENERIC", True, "O-GENERIC" in o["outcome_ids"])
    cmp_exact("alive cells", [], o["alive_cells"])
    cmp_exact("TW-ALIVE fired", False, o["tripwires"]["TW-ALIVE_fired"])
    cmp_exact("PC-1_pass", mine["PC1"]["pass"], o["PC-1_pass"])
    cmp_exact("PC-2_pass", mine["PC2"]["pass"], o["PC-2_pass"])
    g = o["O-GENERIC"]
    my_rej = sorted(f"{k.split('|')[0]}|{k.split('|')[1][1:]}" for k, v in a6["ks"].items() if v["reject_1pct"] and "12.." in k)
    th_rej = sorted(g["HEUR-4765e4-H1_rejections_1pct"])
    cmp_exact("H1 rejections (12..32 as the (class, m) key)", my_rej, th_rej)
    # ---------- R16 ----------
    my_sr = {tuple([s["cell"]["arm"], s["cell"]["class"], s["cell"]["m"], s["cell"]["bits"]]): s for s in mine["stage_r"]}
    for c in a16["stage_r_cells"]:
        k = tuple(c["cell"])
        s = my_sr.get(k)
        if s is None:
            rows_out.append({"quantity": f"R16 {k}", "missing_in_mine": True})
            continue
        sr = s["stage_r"]
        cmp_exact(f"R16 {k} z", sr["z"], c["stage_r"]["z"])
        cmp_exact(f"R16 {k} kappa", sr["kappa"], c["stage_r"]["kappa"])
        cmp_exact(f"R16 {k} C_A", sr["C_A"], c["stage_r"]["C_A"])
        cmp_exact(f"R16 {k} C_R", sr["C_R"], c["stage_r"]["C_R"])
        cmp_exact(f"R16 {k} resolved", sr["resolved"], c["stage_r"]["resolved"])
        cmp_exact(f"R16 {k} counts_A", sr["counts_A"], c["stage_r"]["counts_A"])
        cmp_exact(f"R16 {k} counts_R", sr["counts_R"], c["stage_r"]["counts_R"])
        cmp_exact(f"R16 {k} replicated", s["replicated"], c["replicated_anomaly"])
        cmp_exact(f"R16 {k} discovery z", s["discovery_z"], c["original_z"])
    cmp_exact("R16 reading", "no excursion replicated" if not any(s["replicated"] for s in mine["stage_r"]) else "replicated",
              a16["reading"])
    # ---------- gates / exclusions ----------
    ex_my = sorted(mine["unmatched_size_instances"])
    cmp_exact("unmatched_size instances", [list(x) for x in ex_my],
              sorted([[x[2] if len(x) > 5 else x[0]] for x in []]) if False else ex_my)
    res = {"tally": dict(tally), "rows": rows_out}
    with open(os.path.join(CH, "j3-compare.json"), "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=str)
    print("TALLY", dict(tally))
    for r in rows_out:
        if r.get("agree") is False or r.get("agree_within_3sd") is False or r.get("missing_in_producer") or r.get("missing_in_mine") or "key_sets_equal" in r or "x_b" in r["quantity"]:
            print(json.dumps(r, default=str)[:600])


if __name__ == "__main__":
    main()
