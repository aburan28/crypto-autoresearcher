#!/usr/bin/env python3
"""Analysis of the m = 3 volcano-level panel (PROTOCOL-m3-level-panel.md).

Rows: crypto/experiments/levelpanel/levelpanel_16_0_l6_m3.jsonl, one per curve
(6 full-group probes, monomial V, l = 6, m = 3, production S4 Groebner solver).
Strata from per_ell_levels.json: (v_3(f_E), v_31(f_E)).

Per curve: reductions per call (algebraic, deterministic given the probe
stream), infeasible branches per call, refutations, unknown probes (budget
exhaustion), relations per probe with a Poisson interval, Groebner wall per
call (secondary).  Tests: between-stratum permutation statistic across floor
curves (20,000 draws, labels permuted across curves), crater z against the
pooled floor.  Missing cells are listed, never imputed.
"""
import json, math, os, sys
import numpy as np

ROWS = sys.argv[1]; LEVELS = sys.argv[2]; OUT = sys.argv[3]
PLANNED = [1, 31049, 40902, 45805, 63030, 34988, 34989, 36766, 36767, 1710, 5390, 45335, 61880]
rng = np.random.default_rng(20261013); PERMS = 20000
lv = json.load(open(LEVELS))["16_0"]["levels"]
rows = [json.loads(l) for l in open(ROWS) if l.strip()]
rows = [r for r in rows if "skipped" not in r]
done = {r["a6"] for r in rows}
curves = []
for r in rows:
    v = lv[str(r["a6"])]; strat = (v["3"], v["31"])
    calls = max(r["groebner_calls"], 1)
    curves.append(dict(a6=r["a6"], stratum=str(strat), red=r["reductions"] / calls, infeasible=r.get("infeasible_branches", 0) / calls,
                       refutations=r.get("refutations", 0), unknown=r.get("unknown_probes", 0), probes=r["probes"], relations=r["relations"],
                       rel_rate=r["relations"] / r["probes"], F=r["factor_base_points"], log_us=math.log(r["groebner_ns"] / calls / 1e3),
                       wall=r.get("cell_wall_s"), bsgs_ok=r.get("bsgs_ok")))

def kw(l, v):
    tot = v.mean(); return sum((v[l == g]).size * ((v[l == g]).mean() - tot) ** 2 for g in np.unique(l)) / len(v)
def perm_p(fn, l, v, obs):
    return (sum(fn(rng.permutation(l), v) >= obs - 1e-15 for _ in range(PERMS)) + 1) / (PERMS + 1)

res = {"schema": "m3_level_panel/v1", "planned": PLANNED, "completed": sorted(done), "missing": [a for a in PLANNED if a not in done],
       "all_bsgs_ok": all(c["bsgs_ok"] for c in curves), "curves": curves, "per_stratum": {}, "tests": {}}
METRICS = ["red", "infeasible", "rel_rate", "log_us", "F"]
for s in sorted({c["stratum"] for c in curves}):
    sub = [c for c in curves if c["stratum"] == s]
    res["per_stratum"][s] = {m: dict(n=len(sub), mean=float(np.mean([c[m] for c in sub])), sd=float(np.std([c[m] for c in sub], ddof=1)) if len(sub) > 1 else None) for m in METRICS}
    res["per_stratum"][s]["relations_total"] = int(sum(c["relations"] for c in sub)); res["per_stratum"][s]["probes_total"] = int(sum(c["probes"] for c in sub))
floor = [c for c in curves if c["stratum"] != "(0, 0)"]; crater = [c for c in curves if c["stratum"] == "(0, 0)"]
if len({c["stratum"] for c in floor}) >= 2:
    lab = np.array([c["stratum"] for c in floor])
    for m in ("red", "infeasible", "rel_rate", "log_us"):
        v = np.array([c[m] for c in floor]); obs = kw(lab, v)
        res["tests"][m] = dict(between_stratum_stat=float(obs), p_perm=float(perm_p(kw, lab, v, obs)), stratum_means={s: float(v[lab == s].mean()) for s in np.unique(lab)})
if crater and len(floor) > 2:
    for m in ("red", "infeasible", "rel_rate", "log_us"):
        fv = np.array([c[m] for c in floor]); sd = fv.std(ddof=1)
        res["tests"][f"crater_z_{m}"] = float((crater[0][m] - fv.mean()) / sd) if sd > 0 else None
# pooled relation rate with Poisson 95 % interval per stratum
for s, d in res["per_stratum"].items():
    k, n = d["relations_total"], d["probes_total"]
    lo = 0.5 * 2 * np.sum([1]) and (0.0 if k == 0 else k * (1 - 1 / (9 * k) - 1.96 / (3 * math.sqrt(k))) ** 3)  # Wilson-Hilferty approx
    hi = (k + 1) * (1 - 1 / (9 * (k + 1)) + 1.96 / (3 * math.sqrt(k + 1))) ** 3
    d["rel_rate_pooled"] = k / n; d["rel_rate_95"] = [lo / n, hi / n]
json.dump(res, open(OUT, "w"), indent=1)
lines = ["| stratum (v3, v31) | curves | reductions/call mean ± sd | infeasible branches/call | relations / probes (95 % Poisson) | log µs/call | \\|F\\| |", "|---|---|---|---|---|---|---|"]
for s, d in res["per_stratum"].items():
    r = d["red"]; lines.append(f"| {s} | {r['n']} | {r['mean']:.1f}" + (f" ± {r['sd']:.1f}" if r['sd'] else "") + f" | {d['infeasible']['mean']:.1f} | {d['relations_total']}/{d['probes_total']} = {d['rel_rate_pooled']:.3f} [{d['rel_rate_95'][0]:.3f}, {d['rel_rate_95'][1]:.3f}] | {d['log_us']['mean']:.2f} | {d['F']['mean']:.0f} |")
for m, t in res["tests"].items():
    if isinstance(t, dict):
        lines.append(f"| between-stratum, {m} | | stat {t['between_stratum_stat']:.3g}, perm p = {t['p_perm']:.3f} | | | | |")
    else:
        lines.append(f"| {m} | | z = {t:+.2f} | | | | |" if t is not None else f"| {m} | | — | | | | |")
lines.append(f"| completed {len(done)}/{len(PLANNED)}; missing a6: {res['missing']}; all transported logarithms BSGS-checked: {res['all_bsgs_ok']} | | | | | | |")
open(OUT.replace(".json", ".md"), "w").write("\n".join(lines) + "\n"); print("\n".join(lines))
