#!/usr/bin/env python3
"""Level-stratified yield proxies on the n = 51 general binary ordinary class
built by crypto/isogeny_algos/examples/binary_level_yield.rs.

Rows: one per vertex of the ell-isogeny component found around a random
ordinary curve over GF(2^51) whose Frobenius conductor has an odd prime ell
with v_ell(f_pi) >= 2.  Columns used: v_ell_f_E (level, 0 = crater),
fb_points |F|, fb_abscissae, yield2_exact (exact 2-sum relation yield for the
fixed monomial V), yield2_subgroup_exact and cofactor_balance_C (relations
usable in the prime-order subgroup), rational_ell_isogenies.

Tests (curve-level, permutation of the level label across vertices, 20,000
draws): between-level statistic on log yield2_exact, on |F| and on
yield2_exact / |F|^2; incremental R^2 of level beyond |F|, |F|^2.
"""
import json, math, sys, os
from collections import defaultdict
import numpy as np

path = sys.argv[1]; out = sys.argv[2]
rows = [json.loads(l) for l in open(path) if l.strip()]
rng = np.random.default_rng(20261012); PERMS = 20000
lv = np.array([r["v_ell_f_E"] for r in rows]); F = np.array([r["fb_points"] for r in rows], float)
y2 = np.array([r["yield2_exact"] for r in rows], float); ysub = np.array([r.get("yield2_subgroup_exact") or 0 for r in rows], float)
C = np.array([r.get("cofactor_balance_C") or 0 for r in rows], float); nis = np.array([r["rational_ell_isogenies"] for r in rows])
yF2 = y2 / (F * F)

def kw(l, v):
    tot = v.mean(); return sum((v[l == g]).size * ((v[l == g]).mean() - tot) ** 2 for g in np.unique(l)) / len(v)
def perm_p(fn, l, v, obs):
    return (sum(fn(rng.permutation(l), v) >= obs - 1e-18 for _ in range(PERMS)) + 1) / (PERMS + 1)

res = {"schema": "n51_level_yield/v1", "rows": len(rows), "n": rows[0]["n"], "ell": rows[0]["ell"], "height": rows[0]["height_ell"],
       "f_pi": rows[0]["f_pi"], "D_K": rows[0]["D_K"], "order": rows[0]["order"], "r": rows[0]["r"], "cofactor": rows[0]["cofactor"],
       "component_truncated": rows[0].get("component_truncated"), "samples_tried": rows[0].get("samples_tried"), "fb_dim": rows[0]["fb_dim"],
       "per_level": {}, "tests": {}}
for g in sorted(set(lv.tolist())):
    m = lv == g
    res["per_level"][str(g)] = dict(curves=int(m.sum()), F_mean=float(F[m].mean()), F_sd=float(F[m].std(ddof=1)) if m.sum() > 1 else None,
                                   yield2_mean=float(y2[m].mean()), yield2_sd=float(y2[m].std(ddof=1)) if m.sum() > 1 else None,
                                   yield2_over_F2_mean=float(yF2[m].mean()), yield2_over_F2_sd=float(yF2[m].std(ddof=1)) if m.sum() > 1 else None,
                                   subgroup_yield_mean=float(ysub[m].mean()), cofactor_balance_C_mean=float(C[m].mean()),
                                   rational_ell_isogenies=sorted(set(nis[m].tolist())))
floor = lv >= 1
if len(set(lv[floor].tolist())) >= 2:
    l = lv[floor]
    for name, v in (("log_yield2", np.log(y2[floor])), ("F", F[floor]), ("yield2_over_F2", yF2[floor])):
        obs = kw(l, v); res["tests"][name] = dict(between_level_stat=float(obs), p_perm=float(perm_p(kw, l, v, obs)),
                                                  level_means={str(g): float(v[l == g].mean()) for g in np.unique(l)})
    X0 = np.column_stack([np.ones(floor.sum()), F[floor], F[floor] ** 2]); y = y2[floor]
    def r2(X, y): b, *_ = np.linalg.lstsq(X, y, rcond=None); return 1 - (y - X @ b).var() / y.var()
    r0 = r2(X0, y); r1 = r2(np.column_stack([X0, l]), y)
    def inc(lab, v): return r2(np.column_stack([X0, lab]), v) - r0
    res["tests"]["yield2_incremental_R2_of_level_beyond_F"] = dict(R2_F_only=float(r0), R2_with_level=float(r1), increment=float(r1 - r0),
                                                                   p_perm=float(perm_p(inc, l, y, r1 - r0)))
crater = lv == 0
if crater.sum() == 1 and floor.sum() > 2:
    for name, v in (("yield2", y2), ("F", F), ("yield2_over_F2", yF2)):
        fv = v[floor]; res["tests"][f"crater_z_{name}"] = float((v[crater][0] - fv.mean()) / fv.std(ddof=1))
json.dump(res, open(out, "w"), indent=1)
print(json.dumps({k: res[k] for k in ("rows", "n", "ell", "height", "f_pi", "cofactor", "per_level", "tests")}, indent=1)[:4000])
