#!/usr/bin/env python3
"""TASK-20260929-c40e48 J3: raw/summary agreement for RUN-PFDR-7c8bf2-stage0.

Recomputes, from the ARCHIVED raw per-row output floor-rows.jsonl.gz (and, for
the rho de-duplication count and rho_ratio, from the five committed inputs),
every summary number in fits.json and raw-result.json, and checks fits.json
against raw-result.json and manifest.yaml / stdout.log against raw-result.json.

Independence, stated plainly:
  - P3/P4 fits, tails, P5: recomputed with the frozen stats.py (loaded by file
    path) on rows taken from floor-rows; J2 already reproduced them blind.
  - P6: re-implemented to the letter of the archived script (sorted rungs,
    random.Random(0), stats.py order statistics) for an EXACT raw->summary check;
    J2's independent P6 agrees to Monte Carlo error.
  - P7(a,b,d): frozen stats.py / statistics.median on floor-rows fields.
  - P7(c): c_m, mu_TS and PIT recomputed; the Poisson CDF is taken from mpmath's
    regularized upper incomplete gamma (independent of the script's summation),
    and the KS p-value is checked against a Monte Carlo null of D_n (numpy),
    independent of the script's Marsaglia-Tsang-Wang code.

Usage: python raw_summary.py <run dir> <results dir> <stats.py> <out.json>
"""
import gzip
import importlib.util
import json
import math
import random
import statistics
import sys

import mpmath
import numpy as np
import yaml

SERIES = {
    "S3-smallx-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "small_x"),
    "S3-random-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "random"),
    "S3-subgroup-filtered": ("sweep-minfill-20260926.jsonl.gz", 3, "subgroup"),
    "S3-smallx-unfiltered": ("sweep-arity-minfill-20260926.jsonl.gz", 3, "small_x"),
    "S4-smallx": ("sweep-arity-minfill-20260926.jsonl.gz", 4, "small_x"),
    "S5-smallx": ("sweep-arity-minfill-20260926.jsonl.gz", 5, "small_x"),
    "S6-smallx": ("sweep-arity67-20260928.jsonl.gz", 6, "small_x"),
    "S7-smallx": ("sweep-arity67-20260928.jsonl.gz", 7, "small_x"),
}
FILES = ["sweep-minfill-20260926.jsonl.gz", "sweep-arity-minfill-20260926.jsonl.gz",
         "sweep-arity67-20260928.jsonl.gz", "sweep-mitm-20260926.jsonl.gz",
         "sweep-arity-20260926.jsonl.gz"]


def close(a, b, tol=1e-12):
    if a is None or b is None:
        return a is b
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def main(run, resdir, stats_path, out_path):
    spec = importlib.util.spec_from_file_location("frozen_stats_7c8bf2", stats_path)
    stats = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(stats)
    raw = json.load(open(f"{run}/raw-result.json"))
    fits = json.load(open(f"{run}/fits.json"))
    man = yaml.safe_load(open(f"{run}/manifest.yaml"))
    rows = [json.loads(l) for l in gzip.open(f"{run}/floor-rows.jsonl.gz", "rt")]
    ic = [x for x in rows if x.get("kind") != "rho"]
    rho = [x for x in rows if x.get("kind") == "rho"]
    checks = []

    def chk(name, recomputed, reported, ok):
        checks.append({"quantity": name, "recomputed": recomputed, "reported": reported, "agree": bool(ok)})

    # per-row internal consistency of floor-rows
    bad = 0
    for x in ic:
        fl = 0.5 * math.sqrt(x["relations"] * x["N"])
        ok = (close(fl, x["floor"]) and close(x["S"] / fl, x["ratio"]) and x["search"] == x["S"] - x["T"]
              and close(x["T"] / x["S"], x["table_share"]) and close(math.log2(x["N"]), x["log2N"]))
        if x["engine"] == "mitm":
            mu = 2 * x["X_t"] * x["X_s"] / x["N"]
            ok &= x["X_t"] == x["table_entries"] and x["X_s"] == 2 * x["search"] and close(mu, x["mu_TS"]) \
                and close(x["relations"] / mu, x["q"])
        bad += not ok
    chk("floor-rows IC rows: floor, ratio, search, table_share, log2N, X_t, X_s, mu_TS, q self-consistent",
        f"{len(ic) - bad}/{len(ic)} rows consistent", "-", bad == 0)
    bad_rho = sum(not close(x["walk_ops"] / (0.886 * math.sqrt(x["N"])), x["rho_ratio"]) for x in rho)
    chk("floor-rows rho rows: rho_ratio = walk_ops/(0.886 sqrt N)", f"{len(rho) - bad_rho}/{len(rho)}", "-", bad_rho == 0)
    # rho dedup count from the inputs
    keys, per_label = set(), {}
    for f in FILES:
        for l in gzip.open(f"{resdir}/{f}", "rt"):
            r = json.loads(l)
            if r["method"] != "rho":
                continue
            k = (r["p"], r["a"], r["b"], r["curve"], r["bits"])
            if k in keys:
                continue
            keys.add(k)
            per_label[r["p_filter"]] = per_label.get(r["p_filter"], 0) + 1
    chk("P2 IC rows", len(ic), raw["P2_rows"]["ic_rows"], len(ic) == raw["P2_rows"]["ic_rows"])
    chk("P2 rho rows after (p,a,b,curve,bits) first-seen dedup, from the five inputs", len(keys),
        raw["P2_rows"]["rho_rows_deduplicated"], len(keys) == raw["P2_rows"]["rho_rows_deduplicated"] == len(rho))
    chk("P7(a) rho n per p_filter label, from the five inputs", per_label,
        {k: v["n"] for k, v in raw["P7_controls"]["a_rho"].items()},
        per_label == {k: v["n"] for k, v in raw["P7_controls"]["a_rho"].items()})

    def series_rows(name):
        f, m, fb = SERIES[name]
        return [x for x in ic if x["file"] == f and x["m"] == m and x["fb"] == fb and x["engine"] == "mitm"]

    # P3/P4 + tails
    for name in SERIES:
        sel = series_rows(name)
        for lab, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
            ss = [x for x in sel if lo <= x["bits"] <= 32]
            o = stats.bootstrap_slope([x["log2N"] for x in ss], [math.log2(x["ratio"]) for x in ss],
                                      groups=[x["bits"] for x in ss], reps=2000, level=0.95, seed=0)
            rep = raw["P3_P4_fits"][name][lab]
            chk(f"P4 {name} {lab}", o, rep, o == rep and fits["series"][name][lab] == rep)
        xs = [x["log2N"] for x in sel]; ys = [math.log2(x["ratio"]) for x in sel]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
        c0 = my - b * mx
        big = max(((abs(y - (c0 + b * x)), s) for x, y, s in zip(xs, ys, sel)), key=lambda t: t[0])
        small = min(sel, key=lambda x: x["ratio"])
        t = raw["tail_checks"][name]
        ok = (close(big[0], t["largest_abs_residual_12_32"]["abs_residual_log2"], 1e-9)
              and (big[1]["bits"], big[1]["curve"]) == (t["largest_abs_residual_12_32"]["bits"], t["largest_abs_residual_12_32"]["curve"])
              and small["ratio"] == t["smallest_ratio_row"]["ratio"]
              and (small["bits"], small["curve"]) == (t["smallest_ratio_row"]["bits"], t["smallest_ratio_row"]["curve"]))
        chk(f"tail checks {name}", {"resid": big[0], "resid_row": [big[1]["bits"], big[1]["curve"]],
                                    "smallest": [small["bits"], small["curve"], small["ratio"]]}, t, ok)
    # P5
    mn = min(ic, key=lambda x: x["ratio"])
    below = [x for x in ic if x["ratio"] < 1.0]
    chk("P5 min ratio", mn["ratio"], raw["P5_min"]["min_ratio"],
        mn["ratio"] == raw["P5_min"]["min_ratio"] == fits["min_ratio"] and not below
        and raw["P5_min"]["rows_below_1"] == [] == fits["rows_below_1"])
    # P6, to the letter of the archived algorithm
    p6 = {}
    for fb in ("small_x", "random", "subgroup"):
        sel = [x for x in ic if x["file"] == "sweep-minfill-20260926.jsonl.gz" and x["m"] == 3 and x["fb"] == fb
               and x["engine"] == "mitm" and 20 <= x["bits"] <= 32]
        by = {}
        for x in sel:
            by.setdefault(x["bits"], []).append(math.log(x["ratio"]))
        allv = [v for vs in by.values() for v in vs]
        gm = math.exp(sum(allv) / len(allv))
        rng = random.Random(0)
        boots = []
        for _ in range(2000):
            smp = [rng.choice(by[b_]) for b_ in sorted(by) for _ in by[b_]]
            boots.append(math.exp(sum(smp) / len(smp)))
        boots.sort()
        ci = [boots[int(math.floor(0.025 * 1999))], boots[int(math.ceil(0.975 * 1999))]]
        rep = raw["P6_bases"]["per_base"][fb]
        p6[fb] = ci
        chk(f"P6 {fb} geo mean and ci95", {"gm": gm, "ci": ci}, {"gm": rep["geometric_mean_ratio"], "ci": rep["ci95"]},
            gm == rep["geometric_mean_ratio"] and ci == rep["ci95"])
    chk("fits.json m3_base_geometric_means == raw-result P6_bases", "-", "-",
        fits["m3_base_geometric_means"] == raw["P6_bases"])
    # P7(a)
    for lab, rep in raw["P7_controls"]["a_rho"].items():
        sel = [x for x in rho if x["p_filter"] == lab]
        per = {str(b): statistics.median(x["rho_ratio"] for x in sel if x["bits"] == b)
               for b in sorted({x["bits"] for x in sel})}
        we = stats.bootstrap_slope([x["log2N"] for x in sel], [math.log2(x["walk_ops"]) for x in sel],
                                   groups=[x["bits"] for x in sel], reps=2000, level=0.95, seed=0)
        chk(f"P7(a) rho '{lab}' medians per rung and walk exponent", {"n": len(sel), "walk": we},
            {"n": rep["n"], "walk": rep["walk_exponent"]},
            per == rep["median_rho_ratio_per_rung"] and we == rep["walk_exponent"] and len(sel) == rep["n"])
    chk("fits.json rho == raw-result P7_controls.a_rho", "-", "-", fits["rho"] == raw["P7_controls"]["a_rho"])
    # P7(b)
    for name in SERIES:
        ss = [x for x in series_rows(name) if 20 <= x["bits"] <= 32]
        o = stats.bootstrap_slope([x["log2N"] for x in ss], [math.log2(x["relations"] / x["fb_size"]) for x in ss],
                                  groups=[x["bits"] for x in ss], reps=2000, level=0.95, seed=0)
        rep = raw["P7_controls"]["b_H2_relations_per_fb_slope_20_32"][name]
        chk(f"P7(b) H2 {name}", o, rep, o == rep)
    # P7(c)
    prim = [x for name in SERIES for x in series_rows(name)]
    gen = np.random.Generator(np.random.PCG64(20260929))
    for m in sorted({x["m"] for x in prim}):
        sel = [x for x in prim if x["m"] == m]
        c_m = sum(x["relations"] for x in sel) / sum(x["mu_TS"] for x in sel)
        us = []
        for x in sel:
            mu = c_m * x["mu_TS"]
            n = x["relations"]
            V = random.Random(f"pit-7c8bf2|{x['file']}|{x['bits']}|{x['curve']}|{x['fb']}|{m}").random()
            F1 = float(mpmath.gammainc(n + 1, mu, mpmath.inf, regularized=True))
            F0 = float(mpmath.gammainc(n, mu, mpmath.inf, regularized=True)) if n >= 1 else 0.0
            us.append(F0 + V * (F1 - F0))
        xs = sorted(us)
        N = len(xs)
        D = max(max((i + 1) / N - u, u - i / N) for i, u in enumerate(xs))
        # Monte Carlo null of D_N: 200000 uniform samples, chunked
        ge, tot = 0, 0
        for _ in range(20):
            U = np.sort(gen.random((10_000, N)), axis=1)
            i = np.arange(N)
            Dn = np.maximum(((i + 1) / N - U).max(axis=1), (U - i / N).max(axis=1))
            ge += int((Dn >= D - 1e-12).sum()); tot += Dn.size
        p_mc = ge / tot
        se = math.sqrt(p_mc * (1 - p_mc) / tot)
        rep = raw["P7_controls"]["c_H1_descriptive"]["per_m"][str(m)]
        ks = rep["ks_randomized_pit_vs_poisson"]
        medq = statistics.median(x["q"] for x in sel)
        ok = (close(c_m, rep["c_m"]) and close(D, ks["D"], 1e-9) and N == ks["n"] and close(medq, rep["median_q"])
              and abs(p_mc - ks["p"]) <= 4 * se + 1e-9 and (ks["p"] < 0.01) == ks["reject_1pct"])
        chk(f"P7(c) m={m} c_m, median q, KS D and p", {"c_m": c_m, "median_q": medq, "D": D, "n": N,
                                                      "p_montecarlo_2e5": p_mc, "p_mc_se": se},
            {"c_m": rep["c_m"], "median_q": rep["median_q"], "D": ks["D"], "n": ks["n"], "p": ks["p"],
             "reject_1pct": ks["reject_1pct"]}, ok)
    # P7(d)
    for name in SERIES:
        sel = [x for x in series_rows(name) if x["bits"] == 32]
        vals = [x["table_share"] for x in sel]
        rep = raw["P7_controls"]["d_table_share_at_32_bits"][name]
        chk(f"P7(d) {name}", {"median": statistics.median(vals)}, {"median": rep["median"]},
            statistics.median(vals) == rep["median"] and vals == rep["values"])
    # cross-record agreement
    s = man["run"]["result"]["summary"]
    chk("manifest summary outcome/conditions/invalidations/solver modules == raw-result",
        {"outcome": s["outcome_id"], "cond": s["outcome_conditions_met"], "inv": s["invalidations"],
         "mods": s["solver_modules_loaded"]},
        {"outcome": raw["outcome_id"], "cond": raw["outcome_conditions_met"], "inv": raw["invalidations"],
         "mods": raw["solver_modules_loaded"]},
        s["outcome_id"] == raw["outcome_id"] and s["outcome_conditions_met"] == raw["outcome_conditions_met"]
        and s["invalidations"] == raw["invalidations"] and s["solver_modules_loaded"] == raw["solver_modules_loaded"])
    tw = sum(v["mitm_rows_checked"] for v in raw["P1_consistency"].values())
    chk("manifest twin_consistency text vs raw-result P1", s["twin_consistency"], tw,
        tw == 330 and all(not v["missing_twin"] and not v["unequal"] for v in raw["P1_consistency"].values()))
    so = json.load(open(f"{run}/stdout.log"))
    chk("stdout.log == raw-result outcome/conditions/invalidations", so,
        {"outcome_id": raw["outcome_id"], "conditions_met": raw["outcome_conditions_met"], "invalidations": raw["invalidations"]},
        so == {"outcome_id": raw["outcome_id"], "conditions_met": raw["outcome_conditions_met"], "invalidations": raw["invalidations"]})
    chk("manifest inputs.bootstrap reps/seed/level == raw-result bootstrap",
        {k: man["run"]["inputs"]["bootstrap"].get(k) for k in ("reps", "seed", "level")}, raw["bootstrap"],
        all(man["run"]["inputs"]["bootstrap"].get(k) == raw["bootstrap"][k] for k in ("reps", "seed", "level")))
    n_ok = sum(c["agree"] for c in checks)
    out = {"n_checks": len(checks), "n_agree": n_ok, "checks": checks,
           "manifest_bootstrap_block_as_parsed": man["run"]["inputs"]["bootstrap"]}
    json.dump(out, open(out_path, "w"), indent=1, default=str)
    print(f"{n_ok}/{len(checks)} agree")
    for c in checks:
        if not c["agree"]:
            print("DISAGREE:", json.dumps(c, default=str)[:600])
    print("manifest bootstrap block as parsed:", man["run"]["inputs"]["bootstrap"])


if __name__ == "__main__":
    main(*sys.argv[1:5])
