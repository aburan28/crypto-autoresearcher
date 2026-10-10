#!/usr/bin/env python3
"""Volcano position versus index-calculus cost on the frozen presentation rows.

Blueprint H0/H1 (isogeny_ecdlp_ml_complete_blueprint.pdf, section 1) tested on
data that already exists: crypto/experiments/koblitz_presentation/pres_*.jsonl
(PR-landed rows of the presentation-vs-curve study, 2026-10-04).  Each row is
one (curve, random subspace V) cell of m = 2 Semaev index calculus on a member
of a Koblitz isogeny class over F_{2^n}; `depth` is the breadth-first distance
of the curve from the Koblitz crater K_a along the recorded ell-walk edges of
experiments/koblitz_isogeny_class_walk.json (descending edges of the
ell-volcano for ell | conductor), i.e. a volcano-position label.

Per curve we average the four subspace cells (the paired design), then ask
whether depth predicts anything, with the controls the blueprint prescribes:
a shuffled-label null (depth permuted across CURVES, never across cells), the
|F| covariate, and separate treatment of the one crater curve (z-score against
the floor distribution, since it is a single object).  Timing metrics from
curve-order runs are flagged as confounded, as the source note established.

No new measurements are made.  Exact integers in the rows are not converted.
"""
import json, math, sys, glob, os
from collections import defaultdict
import numpy as np

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/user/crypto"
OUT = sys.argv[2] if len(sys.argv) > 2 else "level_stratified_results.json"
PERMS = 20000
rng = np.random.default_rng(20261010)

walk = json.load(open(os.path.join(ROOT, "experiments/koblitz_isogeny_class_walk.json")))
cases = {(c["n"], c["a2"]): c for c in walk["cases"]}

FILES = {
    "pres_16_0_l8.jsonl": dict(n=16, a2=0, l=8, timing_valid=False, note="curve order; a2=1 file is an isomorphic duplicate"),
    "pres_17_1_l8.jsonl": dict(n=17, a2=1, l=8, timing_valid=False, note="curve order"),
    "pres_19_1_l9.jsonl": dict(n=19, a2=1, l=9, timing_valid=False, note="curve order; timing ICC 0.92 shown to be drift"),
    "pres_19_1_l9_shuffled_retime.jsonl": dict(n=19, a2=1, l=9, timing_valid=True, note="seeded random order re-timing, 32 curves"),
    "pres_23_1_l11.jsonl": dict(n=23, a2=1, l=11, timing_valid=True, note="seeded random order"),
    "pres_31_0_l16_geom.jsonl": dict(n=31, a2=0, l=16, timing_valid=True, note="geometric V, 32 curves; n=31 was out of budget for the ICC study"),
}

def spearman(x, y):
    rx = np.argsort(np.argsort(x)).astype(float); ry = np.argsort(np.argsort(y)).astype(float)
    if rx.std() == 0 or ry.std() == 0: return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])

def perm_p(stat_fn, labels, values, observed):
    cnt = 0
    for _ in range(PERMS):
        s = stat_fn(rng.permutation(labels), values)
        if abs(s) >= abs(observed) - 1e-15: cnt += 1
    return (cnt + 1) / (PERMS + 1)

results = {"schema": "level_stratified_analysis/v1", "permutations": PERMS, "files": {}}
for fname, meta in FILES.items():
    path = os.path.join(ROOT, "experiments/koblitz_presentation", fname)
    rows = [json.loads(l) for l in open(path) if l.strip()]
    rows = [r for r in rows if "skipped" not in r]
    case = cases.get((meta["n"], meta["a2"]))
    per_curve = defaultdict(list)
    for r in rows:
        F = r["factor_base_points"]
        per_curve[r["a6"]].append(dict(
            depth=r["depth"], F=F,
            yield_F2=r["relations"] / (r["probes"] * F * F),
            relations=r["relations"], probes=r["probes"],
            red=r["reductions"] / r["groebner_calls"],
            log_us=math.log(r["groebner_ns"] / r["groebner_calls"] / 1e3),
        ))
    curves = []
    for a6, cells in per_curve.items():
        d = {cells[0]["depth"]}
        assert len(d) == 1
        curves.append(dict(a6=a6, depth=cells[0]["depth"], cells=len(cells),
                           F=float(np.mean([c["F"] for c in cells])),
                           yield_F2=float(np.mean([c["yield_F2"] for c in cells])),
                           rel_rate=float(sum(c["relations"] for c in cells) / sum(c["probes"] for c in cells)),
                           red=float(np.mean([c["red"] for c in cells])),
                           log_us=float(np.mean([c["log_us"] for c in cells]))))
    depths = sorted({c["depth"] for c in curves})
    out = dict(meta=meta, class_conductor=case["conductor"] if case else None,
               walk_ells=case["ells"] if case else None, class_size=case.get("class_size_cm") if case else None,
               curves=len(curves), cells=len(rows), depth_counts={str(d): sum(c["depth"] == d for c in curves) for d in depths},
               per_depth={}, tests={})
    metrics = ["yield_F2", "red", "log_us"]
    for d in depths:
        sub = [c for c in curves if c["depth"] == d]
        out["per_depth"][str(d)] = {m: dict(mean=float(np.mean([c[m] for c in sub])),
                                             sd=float(np.std([c[m] for c in sub], ddof=1)) if len(sub) > 1 else None,
                                             n=len(sub)) for m in metrics + ["F"]}
    floor = [c for c in curves if c["depth"] >= 1]
    crater = [c for c in curves if c["depth"] == 0]
    # (a) crater curve against the floor distribution
    if crater and len(floor) > 2:
        z = {}
        for m in metrics:
            fv = np.array([c[m] for c in floor]); cv = crater[0][m]
            sd = fv.std(ddof=1)
            z[m] = dict(crater=float(cv), floor_mean=float(fv.mean()), floor_sd=float(sd),
                        z=float((cv - fv.mean()) / sd) if sd > 0 else None,
                        floor_rank_pct=float((fv < cv).mean() * 100))
        out["tests"]["crater_vs_floor_z"] = z
    # (b) depth among non-crater curves (needs >= 2 depth values)
    fd = sorted({c["depth"] for c in floor})
    if len(fd) >= 2:
        lab = np.array([c["depth"] for c in floor], dtype=float)
        t = {}
        for m in metrics:
            val = np.array([c[m] for c in floor])
            rho = spearman(lab, val)
            p_rho = perm_p(spearman, lab, val, rho)
            # difference of means between the two most populated depths
            d1, d2 = fd[0], fd[1]
            def dmean(l, v, d1=d1, d2=d2):
                return float(v[l == d1].mean() - v[l == d2].mean())
            dm = dmean(lab, val); p_dm = perm_p(dmean, lab, val, dm)
            pooled = val.std(ddof=1)
            t[m] = dict(spearman_depth=rho, p_perm=p_rho,
                        mean_diff=dict(depths=[d1, d2], diff=dm, diff_in_pooled_sd=float(dm / pooled) if pooled > 0 else None, p_perm=p_dm))
        # incremental value of depth beyond |F| for the raw relation rate
        Fv = np.array([c["F"] for c in floor]); y = np.array([c["rel_rate"] for c in floor])
        X0 = np.column_stack([np.ones_like(Fv), Fv, Fv ** 2])
        X1 = np.column_stack([X0, lab])
        def r2(X, y):
            b, *_ = np.linalg.lstsq(X, y, rcond=None); res = y - X @ b
            return 1 - res.var() / y.var()
        r0, r1 = r2(X0, y), r2(X1, y)
        def inc(l, v):
            return r2(np.column_stack([X0, l]), v) - r0
        obs = r1 - r0
        t["rel_rate_incremental_R2_of_depth_beyond_F"] = dict(R2_F_only=float(r0), R2_F_plus_depth=float(r1), increment=float(obs),
                                                             p_perm=perm_p(inc, lab, y, obs))
        out["tests"]["depth_among_floor"] = t
    results["files"][fname] = out

json.dump(results, open(OUT, "w"), indent=1)

# Markdown summary
lines = ["| file | n | conductor | walk ells | curves | depth:count | metric | depth means (curve-level) | crater z vs floor | depth test among floor |",
         "|---|---|---|---|---|---|---|---|---|---|"]
for fname, o in results["files"].items():
    for m in ["yield_F2", "red", "log_us"]:
        means = "; ".join(f"d{d}: {v[m]['mean']:.4g}" + (f"±{v[m]['sd']:.2g}" if v[m]['sd'] else "") for d, v in o["per_depth"].items())
        cz = o["tests"].get("crater_vs_floor_z", {}).get(m)
        czs = f"z={cz['z']:+.2f} (pct {cz['floor_rank_pct']:.0f})" if cz and cz["z"] is not None else "—"
        dt = o["tests"].get("depth_among_floor", {}).get(m)
        dts = f"ρ={dt['spearman_depth']:+.3f} p={dt['p_perm']:.3f}; Δ={dt['mean_diff']['diff_in_pooled_sd']:+.2f} sd p={dt['mean_diff']['p_perm']:.3f}" if dt else "—"
        flag = "" if (m != "log_us" or o["meta"]["timing_valid"]) else " (timing confounded by run order)"
        lines.append(f"| {fname} | {o['meta']['n']} | {o['class_conductor']} | {o['walk_ells']} | {o['curves']} | {o['depth_counts']} | {m}{flag} | {means} | {czs} | {dts} |")
    inc = o["tests"].get("depth_among_floor", {}).get("rel_rate_incremental_R2_of_depth_beyond_F")
    if inc:
        lines.append(f"| {fname} | | | | | | relations/probe: R² of |F|,|F|² = {inc['R2_F_only']:.3f}; adding depth = {inc['R2_F_plus_depth']:.3f} (Δ={inc['increment']:.4f}, perm p={inc['p_perm']:.3f}) | | | |")
open(OUT.replace(".json", ".md"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
