"""MC-6 (J6(d)): design-evaluated comparators in place of asymptotic ones.

(1) A2's null slope: under kappa = 1, y_b = log2 max(kappa_b - 1, SD_null_b / C_R_b) tracks
    -(1/2) log2 C_R_b, so its OLS slope over the resolved 20..32 rungs is not 0 under the null.
    Simulated per (A, c, m) on the actual design (kept curves, per-curve random means, x_b =
    the cell's mean log2 N) under G-POIS, G-NB, G-CP; R = 4000; numpy default_rng(20261101 + k).
(2) The m = 4 model exponent (m+1)/(2m) = 0.625 and the 0.66 threshold evaluated on the actual
    sizes: beta_eff = OLS slope of log2 |F| (s_sub, from the rows' fb_size) on log2 N over the
    main-panel design, and (1 + beta_eff)/2 (the same model with the design's |F|).  A design
    quantity only: no S_3 value and no floor ratio is computed.
(3) Baseline consistency: census-mode (harvest-off-equivalent) s3_solves exponents against the
    committed min_fill sweeps at the same m (stats.fit_exponent, seed 0, 2000 replicates).
Output: attacks/out/07_mc6_comparators.json
"""
import gzip
import json
import math
import os
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, P, RUNS, RUNGS, WT, canonical_rows, load_stats, m_of, usable  # noqa: E402
from j6design import Design, gen_counts, zstat  # noqa: E402

STATS = load_stats()
CELLS = {(c["arm"], c["class"], c["m"], c["bits"]): c
         for c in (json.loads(l) for l in open(os.path.join(RUNS, P + "analysis", "kappa-cells.jsonl")))}
FITS = json.load(open(os.path.join(RUNS, P + "analysis", "fits.json")))


def null_slopes(des, gen, rng, A, c, m, R):
    rungs = [b for b in RUNGS if 20 <= b <= 32 and CELLS[(A, c, m, b)]["resolved"]]
    if len(rungs) < 4:
        return None, rungs
    xs = np.array([CELLS[(A, c, m, b)]["mean_log2N"] for b in rungs])
    ys = np.zeros((R, len(rungs)))
    ok = np.ones(R, dtype=bool)
    fam = "dik" if A == "dickson" else "sub"
    for bi, b in enumerate(rungs):
        d = des.cells[(c, m, b)]
        kept = d["kept"][A]
        mu = [statistics.mean(d["rand"][fam][j]) for j in kept]
        X = gen_counts(gen, rng, mu, (R, 4), c, m, b, des)
        z, C_R, kap = zstat(X[:, 0, :], X[:, 1:4, :])
        s2 = X[:, 1:4, :].var(axis=1, ddof=1).sum(axis=1)
        V = np.maximum(s2, C_R)
        SD = np.sqrt(4 * V / 3)
        with np.errstate(divide="ignore", invalid="ignore"):
            v = np.maximum(kap - 1, SD / C_R)
            y = np.where((C_R > 0) & (v > 0), np.log2(v), np.nan)
        res = C_R >= 10
        ok &= res & ~np.isnan(y)
        ys[:, bi] = y
    xm = xs - xs.mean()
    ysg = ys[ok]
    sl = (ysg - ysg.mean(axis=1, keepdims=True)) @ xm / (xm @ xm)
    return sl, rungs


def beta_eff():
    rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5")
    out = {}
    for m in (3, 4, 5):
        seen = {}
        for r in rows:
            if m_of(r) == m and r.get("arm") == "random_sub_r0" and r.get("mode") == "census" and r.get("fb_size"):
                seen[(r["bits"], r["curve"])] = (r["log2N"], r["fb_size"])
        xs = [v[0] for v in seen.values()]
        ys = [math.log2(v[1]) for v in seen.values()]
        b = STATS.ols_slope(xs, ys)
        bh = STATS.ols_slope([x for x, (bb, cc) in zip(xs, seen) if bb >= 20],
                             [y for y, (bb, cc) in zip(ys, seen) if bb >= 20])
        out[str(m)] = {"beta_eff_12_32": b, "beta_eff_20_32": bh, "nominal_beta": 1 / m,
                       "model_exponent_(m+1)/(2m)": (m + 1) / (2 * m),
                       "model_exponent_on_design_(1+beta_eff)/2": (1 + b) / 2,
                       "model_exponent_on_design_20_32": (1 + bh) / 2,
                       "n_curves": len(seen)}
    return out


def committed(path):
    with gzip.open(path, "rt") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def baseline():
    res_dir = os.path.join(WT, "src", "crypto_autoresearcher", "index_calculus", "results")
    ar = committed(os.path.join(res_dir, "sweep-arity-minfill-20260926.jsonl.gz"))
    mf = committed(os.path.join(res_dir, "sweep-minfill-20260926.jsonl.gz"))
    rows = canonical_rows("census-m3") + canonical_rows("census-m4") + canonical_rows("census-m5")
    out = {}
    for m in (3, 4, 5):
        for fb, src, name in (("small_x", ar, "sweep-arity-minfill-20260926"),) + (
                (("small_x", mf, "sweep-minfill-20260926"), ("random", mf, "sweep-minfill-20260926"),
                 ("subgroup", mf, "sweep-minfill-20260926")) if m == 3 else ()):
            cm = [r for r in src if r.get("method") == f"ic_m{m}" and r.get("fb") == fb and r.get("engine") == "mitm"
                  and r.get("ok")]
            fc = STATS.fit_exponent(cm, "s3_solves", reps=2000)
            arm = {"small_x": ("small_x",), "random": ("random_sub_r0", "random_sub_r1", "random_sub_r2"),
                   "subgroup": ("subgroup",)}[fb]
            cen = [r for r in rows if m_of(r) == m and r.get("arm") in arm and r.get("mode") == "census"
                   and usable(r) and r.get("k_verified")]
            fe = STATS.fit_exponent(cen, "s3_solves", reps=2000)
            out[f"{m}|{fb}|{name}"] = {"committed": {"slope": fc["slope"], "lo": fc["lo"], "hi": fc["hi"], "n": fc["n"]},
                                       "census_mode": {"slope": fe["slope"], "lo": fe["lo"], "hi": fe["hi"], "n": fe["n"]},
                                       "difference": fe["slope"] - fc["slope"],
                                       "intervals_overlap": not (fe["hi"] < fc["lo"] or fc["hi"] < fe["lo"])}
    return out


def main():
    des = Design()
    out = {"A2_null_slope": {}, "m4_model_on_design": beta_eff(), "baseline_consistency": baseline()}
    fam = [(A, c, m) for A in ("subgroup", "small_x", "dickson") for c in ("TT", "SS") for m in (3, 4, 5)]
    for gi, gen in enumerate(("G-POIS", "G-NB", "G-CP")):
        rng = np.random.default_rng(20261101 + gi)
        g = {}
        for (A, c, m) in fam:
            sl, rungs = null_slopes(des, gen, rng, A, c, m, 4000)
            key = f"{A}|{c}|{m}"
            if sl is None:
                g[key] = {"status": "UNRESOLVED (fewer than 4 resolved rungs in 20..32)"}
                continue
            obs = FITS["A2_slopes"][key]["slope"]
            g[key] = {"rungs": rungs, "null_slope_mean": float(np.mean(sl)), "null_slope_sd": float(np.std(sl)),
                      "null_slope_q025": float(np.quantile(sl, 0.025)), "null_slope_q975": float(np.quantile(sl, 0.975)),
                      "P_null_slope_gt_0": float(np.mean(sl > 0)), "observed_slope": obs,
                      "observed_null_quantile": float(np.mean(sl <= obs)), "replicates_used": int(len(sl))}
        out["A2_null_slope"][gen] = g
        print(gen, {k: (round(v.get("null_slope_mean", float("nan")), 3), round(v.get("observed_slope", float("nan")) or 0, 3),
                        round(v.get("observed_null_quantile", float("nan")), 3)) for k, v in g.items() if "null_slope_mean" in v},
              file=sys.stderr)
    with open(os.path.join(OUT, "out", "07_mc6_comparators.json"), "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(json.dumps(out["m4_model_on_design"], indent=1), file=sys.stderr)
    print(json.dumps(out["baseline_consistency"], indent=1), file=sys.stderr)


if __name__ == "__main__":
    main()
