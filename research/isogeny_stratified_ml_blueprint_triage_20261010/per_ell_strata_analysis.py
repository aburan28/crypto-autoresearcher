#!/usr/bin/env python3
"""Per-prime volcano strata (the blueprint's "prime-indexed arrays, never one
global depth") for the n = 16 Koblitz class, f = 3 * 31, on the frozen
presentation rows.  The earlier analysis lumped the 3-floor (4 curves) and the
31-floor (32 curves) into one "depth 1"; here each curve carries
(v_3(f_E), v_31(f_E)) read off the ell-labelled edges of the class walk.

Tests, all with curve-level aggregation over the 4 random subspaces:
  * one-way comparison of the three floor strata (1,0), (0,1), (1,1) by a
    Kruskal-type statistic (variance of stratum means weighted by size)
    against a 20,000-draw permutation of the stratum labels across curves;
  * the 31-level contrast (0,1) vs (1,1) [v_31 fixed, v_3 differs] and the
    3-level contrast (1,0) vs (1,1) [v_3 fixed... no: (1,0) vs (1,1) differ in
    v_31], each as a difference of means with permutation p;
  * incremental R^2 of the two indicator columns beyond |F|, |F|^2 for the
    relation rate.
Also recomputes the per-stratum table for every other walked class (one floor
stratum each) so the output is complete.
"""
import json, math, os, sys
from collections import defaultdict
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/crypto"
LEVELS = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "per_ell_levels.json")
OUT = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(__file__), "per_ell_strata_results.json")
PERMS = 20000
rng = np.random.default_rng(20261011)
levels = json.load(open(LEVELS))

FILES = {"pres_16_0_l8.jsonl": (16, 0), "pres_17_1_l8.jsonl": (17, 1), "pres_19_1_l9.jsonl": (19, 1),
         "pres_23_1_l11.jsonl": (23, 1), "pres_31_0_l16_geom.jsonl": (31, 0)}
METRICS = ["yield_F2", "red", "log_us"]

def load(fname):
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "experiments/koblitz_presentation", fname)) if l.strip()]
    rows = [r for r in rows if "skipped" not in r]
    per = defaultdict(list)
    for r in rows:
        F = r["factor_base_points"]
        per[r["a6"]].append(dict(F=F, yield_F2=r["relations"] / (r["probes"] * F * F), rel=r["relations"], probes=r["probes"],
                                 red=r["reductions"] / r["groebner_calls"], log_us=math.log(r["groebner_ns"] / r["groebner_calls"] / 1e3)))
    return per

def stratum_key(lv): return tuple(sorted((k, v) for k, v in lv.items()))

def kw_stat(labels, vals):
    # between-stratum variance of means, weighted by stratum size (monotone in Kruskal's H under equal variances)
    tot = vals.mean(); s = 0.0
    for g in np.unique(labels):
        v = vals[labels == g]; s += len(v) * (v.mean() - tot) ** 2
    return s / len(vals)

def perm_p(stat_fn, labels, vals, obs):
    c = 0
    for _ in range(PERMS):
        if stat_fn(rng.permutation(labels), vals) >= obs - 1e-15: c += 1
    return (c + 1) / (PERMS + 1)

results = {"schema": "per_ell_strata_analysis/v1", "permutations": PERMS, "classes": {}}
for fname, (n, a2) in FILES.items():
    per = load(fname); lv = levels[f"{n}_{a2}"]["levels"]
    curves = []
    for a6, cells in per.items():
        key = stratum_key(lv[str(a6)])
        curves.append(dict(a6=a6, stratum=str(key), **{m: float(np.mean([c[m] for c in cells])) for m in METRICS},
                           F=float(np.mean([c["F"] for c in cells])), rel_rate=sum(c["rel"] for c in cells) / sum(c["probes"] for c in cells)))
    strata = sorted({c["stratum"] for c in curves})
    out = dict(n=n, a2=a2, conductor=levels[f"{n}_{a2}"]["conductor"], ells=levels[f"{n}_{a2}"]["ells"], curves=len(curves),
               per_stratum={s: {m: dict(n=sum(c["stratum"] == s for c in curves), mean=float(np.mean([c[m] for c in curves if c["stratum"] == s])),
                                      sd=(float(np.std([c[m] for c in curves if c["stratum"] == s], ddof=1)) if sum(c["stratum"] == s for c in curves) > 1 else None))
                                for m in METRICS + ["F"]} for s in strata}, tests={})
    floor = [c for c in curves if not all(v == 0 for _, v in eval(c["stratum"]))]
    fl_strata = sorted({c["stratum"] for c in floor})
    if len(fl_strata) >= 2:
        lab = np.array([c["stratum"] for c in floor]); t = {}
        for m in METRICS:
            vals = np.array([c[m] for c in floor])
            obs = kw_stat(lab, vals); p = perm_p(kw_stat, lab, vals, obs)
            contrasts = {}
            for s1, s2 in [(fl_strata[i], fl_strata[j]) for i in range(len(fl_strata)) for j in range(i + 1, len(fl_strata))]:
                sel = (lab == s1) | (lab == s2); l2 = lab[sel]; v2 = vals[sel]
                def dm(l, v, s1=s1, s2=s2): return abs(v[l == s1].mean() - v[l == s2].mean())
                d = v2[l2 == s1].mean() - v2[l2 == s2].mean(); sd = v2.std(ddof=1)
                contrasts[f"{s1} - {s2}"] = dict(diff=float(d), diff_in_pooled_sd=float(d / sd) if sd > 0 else None, p_perm=perm_p(dm, l2, v2, abs(d)))
            t[m] = dict(between_stratum_stat=float(obs), p_perm=float(p), contrasts=contrasts)
        Fv = np.array([c["F"] for c in floor]); y = np.array([c["rel_rate"] for c in floor])
        X0 = np.column_stack([np.ones_like(Fv), Fv, Fv ** 2])
        ind = np.column_stack([(lab == s).astype(float) for s in fl_strata[1:]])
        def r2(X, y):
            b, *_ = np.linalg.lstsq(X, y, rcond=None); return 1 - (y - X @ b).var() / y.var()
        r0 = r2(X0, y); r1 = r2(np.hstack([X0, ind]), y)
        def inc(l, v): return r2(np.hstack([X0, np.column_stack([(l == s).astype(float) for s in fl_strata[1:]])]), v) - r0
        t["rel_rate_incremental_R2_of_strata_beyond_F"] = dict(R2_F_only=float(r0), R2_with_strata=float(r1), increment=float(r1 - r0), p_perm=perm_p(inc, lab, y, r1 - r0))
        out["tests"] = t
    results["classes"][fname] = out

json.dump(results, open(OUT, "w"), indent=1)
lines = ["| class | stratum (ell: v_ell(f_E)) | curves | yield/\\|F\\|² mean ± sd | reductions/call | \\|F\\| |", "|---|---|---|---|---|---|"]
for fname, o in results["classes"].items():
    for s, v in o["per_stratum"].items():
        y = v["yield_F2"]; lines.append(f"| n={o['n']} f={o['conductor']} | {s} | {y['n']} | {y['mean']:.4g}" + (f" ± {y['sd']:.2g}" if y['sd'] else "") + f" | {v['red']['mean']:.3f} | {v['F']['mean']:.1f} |")
    if o["tests"]:
        for m in METRICS:
            t = o["tests"][m]; lines.append(f"| n={o['n']} | between-stratum test, {m} | | stat {t['between_stratum_stat']:.3g}, perm p = {t['p_perm']:.3f} | " +
                                            "; ".join(f"{k}: Δ={c['diff_in_pooled_sd']:+.2f} sd p={c['p_perm']:.3f}" for k, c in t["contrasts"].items()) + " | |")
        i = o["tests"]["rel_rate_incremental_R2_of_strata_beyond_F"]
        lines.append(f"| n={o['n']} | relation rate: R² of \\|F\\|,\\|F\\|² = {i['R2_F_only']:.3f}; with strata = {i['R2_with_strata']:.3f} (Δ = {i['increment']:.4f}, perm p = {i['p_perm']:.3f}) | | | | |")
open(OUT.replace(".json", ".md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
