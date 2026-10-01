"""J6: the outcome under single-convention alternatives the specification did not choose.

Each alternative changes exactly ONE convention of P2-P4 and recomputes, on the committed
rows: the eight primary slopes and frozen intervals (stats.bootstrap_slope, groups = bits,
2000 reps, seed 0, 12..32 and 20..32), the P5 minimum ratio over every IC row of the five
files (mitm and enumerate, twins included), the P6 m = 3 base geometric means (20..32,
2000 reps, random.Random(0) per base, curves resampled with replacement within rung), and
the outcome id by the analysis_outcomes table in its stated order with the frozen windows.

  A0   frozen conventions (anchor; must reproduce the archived outcome)
  A1   S excludes the table: S = s3_solves - table_s3_solves
  A2a  r = rank (logged; = relations - 1 on every primary row)
  A2b  r = fb_size + 1 (full-rank requirement)
  A3a  one encoding per S_3 unit: floor = sqrt(r*N) (constant factor 2)
  A3b  one point per x-key (collision probability 1/N): floor = sqrt(r*N/2) (constant sqrt 2)
  A3c  table charged per stored tail: S = search + table_entries
  A4a  regressor = nominal bits
  A4b  regressor = log2 p
  A5   min_index twin rows in place of min_fill rows (S3 filtered from sweep-mitm,
       S3-unfiltered/S4/S5 from sweep-arity; S6/S7 have no twin and keep min_fill)
  A6a  F-2/F-3 model value evaluated at the committed |F| design: theta_design =
       1/2 + (1/2 - h) b_F (search-only model; b_F from fb_size, which is a function of N only)
  A6b  as A6a with the table term: theta_star (see j4_lower_order.py M6)
  A7   estimand = slope of log2(per-rung arithmetic MEAN ratio) on per-rung mean log2N
       (the model is a statement about expected cost), interval by the same stratified
       resampling of curves, recomputing the rung means
  A8   estimand = slope of log2(per-rung MEDIAN ratio) (the README's table convention)
No randomness beyond seed 0 of the frozen bootstrap and P6's random.Random(0).
"""
import json
import math
import os
import random
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
names = list(C.SERIES)
WINDOWS = {3: (-0.03, 0.03), 5: (-0.03, 0.03), 7: (-0.03, 0.03), 4: (0.095, 0.155), 6: (0.053, 0.113)}
TWIN_FILE = {"sweep-minfill-20260926.jsonl.gz": "sweep-mitm-20260926.jsonl.gz",
             "sweep-arity-minfill-20260926.jsonl.gz": "sweep-arity-20260926.jsonl.gz"}
lo_des = json.load(open(os.path.join(C.OUT, "j4_lower_order.json")))


def S_frozen(r):
    return r["s3_solves"]


def rows_of(name, lo, twin=False):
    f, m, fb = C.SERIES[name]
    if twin and f in TWIN_FILE:
        f = TWIN_FILE[f]
    return [r for r in C.all_rows()[f] if r["method"] == f"ic_m{m}" and r["fb"] == fb
            and r.get("engine") == "mitm" and r["ok"] and lo <= r["bits"] <= 32]


def all_ic_rows():
    out = []
    for f in C.FILES:
        for r in C.all_rows()[f]:
            if r["method"].startswith("ic_") and r["ok"]:
                out.append(r)
    return out


def make(Sfun=S_frozen, rfun=lambda r: r["relations"], floor_k=0.5):
    def ratio(r):
        eng = r.get("engine", "enumerate")
        if eng != "mitm":  # enumerate rows: T = 0 by P2, S unchanged by table conventions
            S = r["s3_solves"]
        else:
            S = Sfun(r)
        return S / (floor_k * math.sqrt(rfun(r) * r["N"]))
    return ratio


def slope_fit(rows, ratio, xfun, estimand):
    gs = [r["bits"] for r in rows]
    if estimand == "ols":
        xs = [xfun(r) for r in rows]
        ys = [math.log2(ratio(r)) for r in rows]
        return stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=C.SEED)
    agg = statistics.fmean if estimand == "mean" else statistics.median
    X = np.array([xfun(r) for r in rows])
    Y = np.array([ratio(r) for r in rows])
    G = np.array(gs)

    def fit(idx):
        idx = np.asarray(idx)
        xg, yg = [], []
        for g in sorted(set(gs)):
            sel = idx[G[idx] == g]
            xg.append(statistics.fmean(X[sel]))
            yg.append(math.log2(agg(Y[sel])))
        return C.ols(xg, yg)[0]
    s = fit(list(range(len(rows))))
    lo, hi = C.stratified_boot_generic(fit, gs)
    return {"slope": s, "lo": lo, "hi": hi, "n": len(rows)}


def p6(ratio):
    out = {}
    for fb in ("small_x", "random", "subgroup"):
        rows = [r for r in C.all_rows()["sweep-minfill-20260926.jsonl.gz"] if r["method"] == "ic_m3"
                and r["fb"] == fb and r.get("engine") == "mitm" and r["ok"] and 20 <= r["bits"] <= 32]
        by = {}
        for r in rows:
            by.setdefault(r["bits"], []).append(math.log(ratio(r)))
        allv = [v for vs in by.values() for v in vs]
        rng = random.Random(0)
        boots = []
        for _ in range(C.REPS):
            smp = [rng.choice(by[b]) for b in sorted(by) for _ in by[b]]
            boots.append(math.exp(sum(smp) / len(smp)))
        boots.sort()
        out[fb] = (math.exp(sum(allv) / len(allv)), boots[int(math.floor(0.025 * 1999))],
                   boots[int(math.ceil(0.975 * 1999))])
    nm = list(out)
    overlap = all(out[a][1] <= out[b][2] and out[b][1] <= out[a][2] for i, a in enumerate(nm) for b in nm[i + 1:])
    return out, overlap


def evaluate(label, ratio=make(), xfun=lambda r: r["log2N"], twin=False, estimand="ols", model="asymptotic"):
    fits, excl, miss = {}, [], []
    for name in names:
        m = C.SERIES[name][1]
        rec = {}
        for rl, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
            rec[rl] = slope_fit(rows_of(name, lo, twin), ratio, xfun, estimand)
        if model == "asymptotic":
            theta = C.model_value(m)
        elif model == "design":
            theta = lo_des["series"][name]["primary_12_32"]["M6_design_model_value"]["theta_design_search_only"]
        else:
            theta = lo_des["series"][name]["primary_12_32"]["M6_design_model_value"]["theta_star_table_plus_search"]
        rec["model_value"] = theta
        pf = rec["primary_12_32"]
        rec["excludes_model_value"] = not (pf["lo"] <= theta <= pf["hi"])
        if rec["excludes_model_value"]:
            excl.append(name)
        w = WINDOWS[m]
        if not (w[0] <= pf["slope"] <= w[1]):
            miss.append(name)
        fits[name] = rec
    ic = all_ic_rows()
    ratios = [ratio(r) for r in ic]
    mn = min(ratios)
    p6v, overlap = p6(ratio)
    conds = []
    if mn < 0.9:
        conds.append("OUT-FLOOR-VIOLATION")
    if excl:
        conds.append("OUT-SLOPE-INTERVAL")
    if miss or not overlap or 0.9 <= mn < 1.0:
        conds.append("OUT-PREDICTION-MISS")
    outcome = next((o for o in ("OUT-FLOOR-VIOLATION", "OUT-SLOPE-INTERVAL", "OUT-PREDICTION-MISS") if o in conds),
                   "OUT-CONSISTENT")
    res = {"fits": fits, "slope_interval_exclusions": excl, "point_estimates_outside_window": miss,
           "min_ratio": mn, "rows_below_1": sum(1 for v in ratios if v < 1.0),
           "rows_below_0_9": sum(1 for v in ratios if v < 0.9), "p6": p6v, "p6_pairwise_overlap": overlap,
           "conditions_met": conds, "outcome_id": outcome}
    s4, s6 = fits["S4-smallx"], fits["S6-smallx"]
    print("%-5s outcome=%-20s S4 %.4f [%.4f, %.4f] (20..32 %.4f [%.4f, %.4f]) S6 %.4f [%.4f, %.4f] (20..32 %.4f [%.4f, %.4f])"
          " excl=%s miss=%s min=%.4f p6overlap=%s" % (
              label, outcome, s4["primary_12_32"]["slope"], s4["primary_12_32"]["lo"], s4["primary_12_32"]["hi"],
              s4["sensitivity_20_32"]["slope"], s4["sensitivity_20_32"]["lo"], s4["sensitivity_20_32"]["hi"],
              s6["primary_12_32"]["slope"], s6["primary_12_32"]["lo"], s6["primary_12_32"]["hi"],
              s6["sensitivity_20_32"]["slope"], s6["sensitivity_20_32"]["lo"], s6["sensitivity_20_32"]["hi"],
              excl, miss, mn, overlap), flush=True)
    return res


out = {}
out["A0_frozen"] = evaluate("A0")
out["A1_S_excludes_table"] = evaluate("A1", make(Sfun=lambda r: r["s3_solves"] - r["table_s3_solves"]))
out["A2a_r_is_rank"] = evaluate("A2a", make(rfun=lambda r: r["rank"]))
out["A2b_r_is_fb_size_plus_1"] = evaluate("A2b", make(rfun=lambda r: r["fb_size"] + 1))
out["A3a_one_encoding_per_S3_unit"] = evaluate("A3a", make(floor_k=1.0))
out["A3b_one_point_per_x_key"] = evaluate("A3b", make(floor_k=math.sqrt(0.5)))
out["A3c_table_charged_per_tail"] = evaluate("A3c", make(Sfun=lambda r: r["s3_solves"] - r["table_s3_solves"] + r["table_entries"]))
out["A4a_regressor_bits"] = evaluate("A4a", xfun=lambda r: float(r["bits"]))
out["A4b_regressor_log2p"] = evaluate("A4b", xfun=lambda r: math.log2(r["p"]))
out["A5_min_index_twins"] = evaluate("A5", twin=True)
out["A6a_model_value_at_design_search_only"] = evaluate("A6a", model="design")
out["A6b_model_value_at_design_table_plus_search"] = evaluate("A6b", model="star")
out["A7_log_of_rung_mean"] = evaluate("A7", estimand="mean")
out["A8_log_of_rung_median"] = evaluate("A8", estimand="median")
print(C.dump("j6_alternatives.json", out))
