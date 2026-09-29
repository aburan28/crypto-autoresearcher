"""MC-1, MC-2, MC-3 (J6(c)): seed, replicate and order sensitivity of every bootstrap-based
decision element, and order invariance of z, Stage R and the A4 medians.

Decision elements (analyze_census.py as pinned):
  A2 -- per (A, c in {TT, SS}, m): ci_above_zero (lower percentile end > 0) and Holm-adjusted
        one-sided p < 0.05 over the fixed 18-test family (frozen scheme: random.Random(seed),
        2000 replicates, curve indices resampled within each resolved rung 20..32, same indices
        for A and its three randoms; p = (1 + #{slope <= 0} + dropped) / (REPS + 1)).
  A4 (2) -- m = 4 small_x harvest-on exponent: met iff OLS point <= 0.66 (deterministic);
        falsified iff the stats.bootstrap_slope lower end > 0.66 (bootstrap).
  A4 (1b) -- met iff |point delta| <= 0.03 at m = 3, 5 for every base (deterministic in the
        pinned code); its paired-bootstrap CI (random.Random(0)) is reported, not decision-bearing.
Seeds: MC-1 random.Random(0) at 20000 replicates; MC-2 random.Random(s), s = 1..200, 2000
replicates; MC-3 random.Random(s).shuffle, s = 1..20, and reversal of the canonical order.
Output: attacks/out/06_mc_sweeps.json
"""
import json
import math
import os
import random
import statistics
import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import (OUT, P, RANDOMS, RUNS, RUNGS, STRUCT, build_index, canonical_rows,  # noqa: E402
                   iter_jsonl, kappa_cell, kappa_stats, load_stats, m_of, usable)

STATS = load_stats()
CELLS = [json.loads(l) for l in open(os.path.join(RUNS, P + "analysis", "kappa-cells.jsonl"))]
CELL = {(c["arm"], c["class"], c["m"], c["bits"]): c for c in CELLS}
FAMILY = [(A, c, m) for A in ("dickson", "small_x", "subgroup") for c in ("SS", "TT") for m in (3, 4, 5)]


def pct(vals, level=0.95):
    vals = sorted(vals)
    tail = (1 - level) / 2
    return vals[int(math.floor(tail * (len(vals) - 1)))], vals[int(math.ceil((1 - tail) * (len(vals) - 1)))]


def a2_prep(A, c, m, curve_perm=None):
    rungs = [b for b in RUNGS if 20 <= b <= 32 and CELL[(A, c, m, b)]["resolved"]]
    if len(rungs) < 4:
        return None
    data = []
    for b in rungs:
        cc = CELL[(A, c, m, b)]
        nA = np.array(cc["counts_A"], dtype=float)
        nR = np.array(cc["counts_R"], dtype=float)  # (n, 3)
        if curve_perm is not None:
            pm = curve_perm(len(nA))
            nA, nR = nA[pm], nR[pm]
        data.append((cc["mean_log2N"], nA, nR))
    return rungs, data


def y_vec(nA, nR):
    """nA: (reps, n); nR: (reps, n, 3) -> y per replicate (nan when undefined)."""
    C_A = nA.sum(axis=1)
    C_R = nR.sum(axis=(1, 2)) / 3.0
    s2 = nR.var(axis=2, ddof=1).sum(axis=1)
    V = np.maximum(s2, C_R)
    SD = np.sqrt(V * 4 / 3)
    with np.errstate(divide="ignore", invalid="ignore"):
        kap = np.where(C_R > 0, C_A / C_R, np.nan)
        v = np.maximum(kap - 1, SD / C_R)
        y = np.where((C_R > 0) & (v > 0), np.log2(v), np.nan)
    return y


def a2_boot(prep, seed, reps, scheme="python"):
    rungs, data = prep
    xs = np.array([d[0] for d in data])
    ns = [len(d[1]) for d in data]
    offs = np.cumsum([0] + ns)
    if scheme == "python":
        rng = random.Random(seed)
        rr = rng.randrange
        flat = [rr(n) for _ in range(reps) for n in ns for _ in range(n)]
        flat = np.array(flat, dtype=np.int64).reshape(reps, int(offs[-1]))
    ys = np.zeros((reps, len(data)))
    for bi, (_, nA, nR) in enumerate(data):
        n = len(nA)
        if scheme == "python":
            I = flat[:, offs[bi]:offs[bi + 1]]
        else:
            I = np.random.default_rng(seed * 1000 + bi).integers(0, n, size=(reps, n))
        ys[:, bi] = y_vec(nA[I], nR[I])
    bad = np.isnan(ys).any(axis=1)
    good = ys[~bad]
    xm = xs - xs.mean()
    slopes = (good - good.mean(axis=1, keepdims=True)) @ xm / (xm @ xm)
    lo, hi = pct(slopes.tolist()) if len(slopes) else (None, None)
    le0 = int((slopes <= 0).sum())
    p = (1 + le0 + int(bad.sum())) / (reps + 1)
    return {"lo": lo, "hi": hi, "p": p, "dropped": int(bad.sum())}


def holm(pv):
    items = sorted(pv.items(), key=lambda kv: kv[1])
    n = len(items)
    adj, run = {}, 0.0
    for i, (k, p) in enumerate(items):
        run = max(run, min(1.0, (n - i) * p))
        adj[k] = run
    return adj


def a2_decisions(seed, reps, scheme="python", curve_perm=None):
    res, pv = {}, {}
    for (A, c, m) in FAMILY:
        prep = a2_prep(A, c, m, curve_perm)
        if prep is None:
            res[(A, c, m)] = None
            pv[(A, c, m)] = 1.0
            continue
        r = a2_boot(prep, seed, reps, scheme)
        res[(A, c, m)] = r
        pv[(A, c, m)] = r["p"]
    adj = holm(pv)
    out = {}
    for k in FAMILY:
        r = res[k]
        out[k] = {"ci_above_zero": bool(r is not None and r["lo"] is not None and r["lo"] > 0),
                  "holm_lt_005": adj[k] < 0.05, "lo": None if r is None else r["lo"],
                  "hi": None if r is None else r["hi"], "p": pv[k], "holm": adj[k]}
    return out


# -- A4 -------------------------------------------------------------------------------------
GROUPS = {"subgroup": ("subgroup",), "dickson": ("dickson",), "small_x": ("small_x",),
          "random_sub": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
          "random_dick": ("random_dick_r0", "random_dick_r1", "random_dick_r2")}


def a4_pairs(main_rows):
    idx = build_index(main_rows)
    UM = set()
    for r in main_rows:
        if r.get("arm") in STRUCT and r.get("mode") == "census":
            for mode in ("census",):
                rr = [idx.get(("main", m_of(r), r["bits"], r["curve"], a, mode)) for a in RANDOMS[r["arm"]]]
                if rr[0] is not None and r.get("fb_size") != rr[0].get("fb_size"):
                    UM.add((m_of(r), r["bits"], r["curve"], r["arm"]))
    pairs = defaultdict(list)
    for r in main_rows:
        if r.get("mode") != "census" or r.get("arm") not in sum(GROUPS.values(), ()):
            continue
        mm = m_of(r)
        g = next(k for k, v in GROUPS.items() if r["arm"] in v)
        on = idx.get(("main", mm, r["bits"], r["curve"], r["arm"], "on"))
        if (mm, r["bits"], r["curve"], r["arm"]) in UM or not usable(r) or not r.get("k_verified"):
            continue
        if on is None or not usable(on) or not on.get("k_verified"):
            continue
        pairs[(mm, g)].append((r, on))
    return pairs


def a4_elements(pairs, seed=0, reps=2000):
    ps = pairs[(4, "small_x")]
    sel = [(c, o) for c, o in ps if 12 <= c["bits"] <= 32]
    fo = STATS.fit_exponent([o for _, o in sel], "s3_solves", reps=reps, seed=seed)
    deltas = {}
    for m in (3, 5):
        for g in GROUPS:
            ss = [(c, o) for c, o in pairs[(m, g)] if 12 <= c["bits"] <= 32]
            fc = STATS.ols_slope([c["log2N"] for c, _ in ss], [math.log2(c["s3_solves"]) for c, _ in ss])
            fn = STATS.ols_slope([c["log2N"] for c, _ in ss], [math.log2(o["s3_solves"]) for _, o in ss])
            deltas[f"{m}|{g}"] = fn - fc
    meds = {}
    for m in (3, 4, 5):
        for g in GROUPS:
            for b in (24, 26, 28, 30, 32):
                sel2 = [c["s3_solves"] / o["s3_solves"] for c, o in pairs[(m, g)] if c["bits"] == b]
                if sel2:
                    meds[f"{m}|{g}|{b}"] = statistics.median(sel2)
    return {"p2_slope": fo["slope"], "p2_lo": fo["lo"], "p2_hi": fo["hi"],
            "p2_met": fo["slope"] <= 0.66, "p2_falsified": fo["lo"] > 0.66,
            "deltas": deltas, "p1b_met": all(abs(v) <= 0.03 for v in deltas.values()),
            "medians": meds}


def paired_delta_ci(pairs, m, g, seed, reps, order=None):
    sel = [(c, o) for c, o in pairs[(m, g)] if 12 <= c["bits"] <= 32]
    if order is not None:
        sel = order(sel)
    strata = defaultdict(list)
    for i, (c, _) in enumerate(sel):
        strata[c["bits"]].append(i)
    rng = random.Random(seed)
    xs = [c["log2N"] for c, _ in sel]
    yc = [math.log2(c["s3_solves"]) for c, _ in sel]
    yo = [math.log2(o["s3_solves"]) for _, o in sel]
    boots = []
    for _ in range(reps):
        ii = [rng.choice(mem) for mem in strata.values() for _ in mem]
        sc = STATS.ols_slope([xs[i] for i in ii], [yc[i] for i in ii])
        so = STATS.ols_slope([xs[i] for i in ii], [yo[i] for i in ii])
        boots.append(so - sc)
    return pct(boots)


def main():
    out = {}
    # ---- A2: reproduce seed 0 (python scheme) against the archive -------------------------
    an = json.load(open(os.path.join(RUNS, P + "analysis", "fits.json")))["A2_slopes"]
    d0 = a2_decisions(0, 2000)
    repro = []
    for (A, c, m), v in d0.items():
        a = an[f"{A}|{c}|{m}"]
        if a.get("ci"):
            repro.append(abs(a["ci"][0] - v["lo"]) + abs(a["ci"][1] - v["hi"]) + abs(a["p_one_sided"] - v["p"]))
    out["A2_seed0_reproduction_max_abs_diff"] = max(repro) if repro else None
    # ---- MC-1: 20000 replicates, seed 0 -------------------------------------------------
    d1 = a2_decisions(0, 20000)
    # ---- MC-2: seeds 1..200 --------------------------------------------------------------
    flips = defaultdict(lambda: [0, 0])
    los = defaultdict(list)
    ps = defaultdict(list)
    for s in range(1, 201):
        ds = a2_decisions(s, 2000)
        for k, v in ds.items():
            flips[k][0] += v["ci_above_zero"] != d0[k]["ci_above_zero"]
            flips[k][1] += v["holm_lt_005"] != d0[k]["holm_lt_005"]
            if v["lo"] is not None:
                los[k].append(v["lo"])
            ps[k].append(v["p"])
    a2 = {}
    for k in FAMILY:
        key = "|".join(map(str, k))
        a2[key] = {"seed0_2000": {"lo": d0[k]["lo"], "hi": d0[k]["hi"], "p": d0[k]["p"], "holm": d0[k]["holm"],
                                  "ci_above_zero": d0[k]["ci_above_zero"], "holm_lt_005": d0[k]["holm_lt_005"]},
                   "seed0_20000": {"lo": d1[k]["lo"], "hi": d1[k]["hi"], "p": d1[k]["p"], "holm": d1[k]["holm"],
                                   "ci_above_zero": d1[k]["ci_above_zero"], "holm_lt_005": d1[k]["holm_lt_005"]},
                   "MC2_flip_fraction_ci_above_zero": flips[k][0] / 200,
                   "MC2_flip_fraction_holm_lt_005": flips[k][1] / 200,
                   "MC_sd_lower_end": statistics.pstdev(los[k]) if len(los[k]) > 1 else None,
                   "margin_lower_end_to_0": d0[k]["lo"],
                   "MC_sd_p": statistics.pstdev(ps[k])}
    out["A2"] = a2
    print("A2 done; reproduction max diff", out["A2_seed0_reproduction_max_abs_diff"], file=sys.stderr)
    # ---- MC-3 for A2: curve-order permutations within rungs (seed 0 scheme) -----------------
    fl = defaultdict(lambda: [0, 0])
    for s in range(1, 21):
        rr = random.Random(s)

        def perm(n, rr=rr):
            q = list(range(n))
            rr.shuffle(q)
            return np.array(q)
        ds = a2_decisions(0, 2000, curve_perm=perm)
        for k, v in ds.items():
            fl[k][0] += v["ci_above_zero"] != d0[k]["ci_above_zero"]
            fl[k][1] += v["holm_lt_005"] != d0[k]["holm_lt_005"]
    out["A2_MC3_curve_order_flip_fraction"] = {"|".join(map(str, k)): [v[0] / 20, v[1] / 20] for k, v in fl.items()}
    # ---- A4 ------------------------------------------------------------------------------
    main_rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5")
    pairs = a4_pairs(main_rows)
    e0 = a4_elements(pairs, 0, 2000)
    e1 = a4_elements(pairs, 0, 20000)
    fl2, lo2 = 0, []
    for s in range(1, 201):
        es = a4_elements(pairs, s, 2000)
        fl2 += es["p2_falsified"] != e0["p2_falsified"]
        lo2.append(es["p2_lo"])
    out["A4"] = {"prediction_2": {"seed0_2000": {k: e0[k] for k in ("p2_slope", "p2_lo", "p2_hi", "p2_met", "p2_falsified")},
                                  "seed0_20000": {k: e1[k] for k in ("p2_slope", "p2_lo", "p2_hi", "p2_met", "p2_falsified")},
                                  "MC2_flip_fraction_falsified": fl2 / 200,
                                  "MC_sd_lower_end": statistics.pstdev(lo2),
                                  "margin_lower_end_to_0.66": 0.66 - e0["p2_lo"]},
                 "prediction_1b": {"deltas_point": e0["deltas"], "met": e0["p1b_met"],
                                   "note": "deterministic in the pinned code (point delta); no seed can flip it",
                                   "margins_abs_delta_minus_0.03": {k: abs(v) - 0.03 for k, v in e0["deltas"].items()}}}
    # paired delta CI MC for the two elements nearest the 0.03 threshold
    dci = {}
    for (m, g) in ((5, "subgroup"), (5, "small_x"), (5, "random_sub")):
        c0 = paired_delta_ci(pairs, m, g, 0, 2000)
        c1 = paired_delta_ci(pairs, m, g, 0, 20000)
        lows = [paired_delta_ci(pairs, m, g, s, 2000) for s in range(1, 21)]
        dci[f"{m}|{g}"] = {"seed0_2000": c0, "seed0_20000": c1,
                           "MC_sd_lo_20seeds": statistics.pstdev([x[0] for x in lows]),
                           "MC_sd_hi_20seeds": statistics.pstdev([x[1] for x in lows])}
    out["A4"]["prediction_1b"]["paired_delta_ci_reported_not_decision_bearing"] = dci
    # ---- MC-3 for A4: row order (reverse + 20 shuffles) --------------------------------------
    orders = [("reverse", lambda rows: rows[::-1])]
    for s in range(1, 21):
        orders.append((f"shuffle{s}", lambda rows, s=s: random.Random(s).sample(rows, len(rows))))
    med_changes, p2_flips, p1b_flips = 0, 0, 0
    for name, f in orders:
        rows2 = f(main_rows)
        pr2 = a4_pairs(rows2)
        es = a4_elements(pr2, 0, 2000)
        med_changes += any(abs(es["medians"][k] - e0["medians"][k]) > 0 for k in e0["medians"])
        p2_flips += es["p2_falsified"] != e0["p2_falsified"]
        p1b_flips += es["p1b_met"] != e0["p1b_met"]
    out["A4_MC3_row_order"] = {"orders": len(orders), "median_changes": med_changes,
                               "p2_falsified_flips": p2_flips, "p1b_flips": p1b_flips}
    # ---- MC-3: z and Stage R invariance under row order ------------------------------------
    def all_z(rows):
        ix = build_index(rows)
        zz = {}
        for m in (3, 4, 5):
            for A in STRUCT:
                for c in ("TT", "TB", "SS"):
                    for b in RUNGS:
                        nA, nR, kept, _ = kappa_cell(ix, m, b, c, A, range(5))
                        st = kappa_stats(nA, nR) if kept else {"z": None}
                        zz[(A, c, m, b)] = st["z"]
        return zz
    z0 = all_z(main_rows)
    keys = [((r.get("panel"), m_of(r), r["bits"], r["curve"], r.get("arm"), r.get("mode"))) for r in main_rows if r.get("arm")]
    dup = len(keys) - len(set(keys))
    zchg = 0
    for name, f in orders:
        z1 = all_z(f(main_rows))
        zchg += any((z0[k] is None) != (z1[k] is None) or (z0[k] is not None and z0[k] != z1[k]) for k in z0)
    sr_rows = list(iter_jsonl(os.path.join(RUNS, P + "stage-r", "rows.jsonl.gz")))
    srk = [((r.get("panel"), m_of(r), r["bits"], r["curve"], r.get("arm"), r.get("mode"))) for r in sr_rows]

    def sr_z(rows):
        ix = build_index(rows)
        out_ = {}
        for (A, c, m, b) in (("subgroup", "TT", 3, 28), ("small_x", "SS", 4, 20), ("dickson", "SS", 4, 26), ("subgroup", "TT", 5, 16)):
            nA, nR, kept, _ = kappa_cell(ix, m, b, c, A, range(5, 10))
            out_[(A, c, m, b)] = kappa_stats(nA, nR)["z"]
        return out_
    s0 = sr_z(sr_rows)
    srchg = sum(sr_z(f(sr_rows)) != s0 for _, f in orders)
    out["MC3_invariance"] = {"canonical_main_duplicate_keys": dup, "stageR_duplicate_keys": len(srk) - len(set(srk)),
                             "orders_tested": len(orders), "orders_changing_any_A1_z": zchg,
                             "orders_changing_stageR_z": srchg, "orders_changing_A4_medians": med_changes}
    with open(os.path.join(OUT, "out", "06_mc_sweeps.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "A2"}, indent=1, default=str)[:4000], file=sys.stderr)


if __name__ == "__main__":
    main()
