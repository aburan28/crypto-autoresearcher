#!/usr/bin/env python3
"""Blueprint H0 on the prime-field dataset of ml-cryptanalysis/data/curves.jsonl.

H0: endomorphism-conductor and isogeny-graph features have no incremental
predictive value for measured ECDLP cost beyond matched controls.

Target: log of the measured automorphism-class rho cost S (aut_S_total_mean,
counted group operations / sqrt(r), averaged over seeds) and of the plain
(structure-blind) rho arm.  Controls: log2 r, |Aut| one-hot, family one-hot,
log2 p, cofactor.  Candidate block: log2 f_End, log2 f_pi, v2(f), v3(f),
End_maximal, h_End, log2 h_K, n_isog, n_up, n_down, n_horizontal,
n_rational_2isog, tors2_rank, has_3tors, cl_two_rank, cl_cyclic,
vol_level/height per ell in {2,3,5,7}, kron_K per ell.

Model: ridge regression (closed form), evaluated out-of-fold with folds that
keep every curve of an isogeny class (same p and N) in one fold.  Statistic:
the gain in out-of-fold R^2 from adding the candidate block.  Null: the
candidate block is permuted ACROSS curves within the same prime p (so the
control structure and the per-field cost scale are preserved), 1000 times.
Measurement noise is reported through the per-curve SEM so the ceiling on
any explainable variance is visible.
"""
import json, math, sys
import numpy as np
from collections import defaultdict

path = sys.argv[1]; out = sys.argv[2]
rows = [json.loads(l) for l in open(path)]
rows = [r for r in rows if r.get("aut_S_total_mean") and r.get("plain_S_total_mean") and not r.get("supersingular")]
rng = np.random.default_rng(20261010)

def l2(x): return math.log2(max(float(x), 1))
def tot(v):
    if isinstance(v, dict): return float(sum(x for x in v.values() if x is not None))
    return float(v or 0)
def per_ell(r, key, ell):
    v = r.get(key)
    if isinstance(v, dict): return v.get(str(ell), v.get(ell))
    return None
fams = sorted({r["family"] for r in rows}); auts = sorted({r["aut_order"] for r in rows})

def controls(r):
    return [1.0, l2(r["r"]), l2(r["p"]), l2(r["cofactor"])] + [1.0 if r["aut_order"] == a else 0.0 for a in auts[1:]] + [1.0 if r["family"] == f else 0.0 for f in fams[1:]]
cand_names = ["log2_f_End", "log2_f_pi", "v2_f", "v3_f", "End_maximal", "log2_h_End", "log2_h_K", "n_isog", "n_up", "n_down", "n_horizontal",
              "n_rational_2isog", "tors2_rank", "has_3tors", "cl_two_rank", "cl_cyclic"] + [f"{k}{e}" for e in (2, 3, 5, 7) for k in ("vol_level", "vol_height", "kron")]
def cand(r):
    v = [l2(r.get("f_End", 1)), l2(r.get("f", 1)), float(r.get("v2_f") or 0), float(r.get("v3_f") or 0), float(bool(r.get("End_maximal"))),
         l2(r.get("h_End", 1)), l2(r.get("h_K", 1)), tot(r.get("n_isog")), tot(r.get("n_up")), tot(r.get("n_down")),
         tot(r.get("n_horizontal")), float(r.get("n_rational_2isog") or 0), float(r.get("tors2_rank") or 0), float(bool(r.get("has_3tors"))),
         float(r.get("cl_two_rank") or 0), float(bool(r.get("cl_cyclic")))]
    for e in (2, 3, 5, 7):
        for k in ("vol_level", "vol_height", "kron_K"):
            x = per_ell(r, k, e); v.append(float(x) if x is not None else 0.0)
    return v

Xc = np.array([controls(r) for r in rows]); Xk = np.array([cand(r) for r in rows])
# standardise candidate block (ridge is scale-sensitive)
mu, sd = Xk.mean(0), Xk.std(0); sd[sd == 0] = 1; Xk = (Xk - mu) / sd
groups = np.array([hash((r["p"], r["N"])) for r in rows]); primes = np.array([r["p"] for r in rows])
targets = {"log_aut_S_total": np.log(np.array([r["aut_S_total_mean"] for r in rows])),
           "log_plain_S_total": np.log(np.array([r["plain_S_total_mean"] for r in rows]))}
sem_ratio = {k: float(np.mean([r[k.replace("log_", "").replace("_total", "_total_sem")] / r[k.replace("log_", "").replace("_total", "_total_mean")] for r in rows])) for k in targets}

uniq = np.unique(groups); K = 5
fold_of_group = {g: i % K for i, g in enumerate(rng.permutation(uniq))}
folds = np.array([fold_of_group[g] for g in groups])
LAM = 1.0
def oof_r2(X, y):
    pred = np.zeros_like(y)
    for k in range(K):
        tr, te = folds != k, folds == k
        A = X[tr]; I = np.eye(X.shape[1]); I[0, 0] = 0
        b = np.linalg.solve(A.T @ A + LAM * I, A.T @ y[tr]); pred[te] = X[te] @ b
    return 1 - ((y - pred) ** 2).mean() / y.var(), pred

results = {"schema": "prime_field_nested_test/v1", "curves": len(rows), "isogeny_classes": int(len(uniq)), "primes": int(len(np.unique(primes))),
           "folds": K, "ridge_lambda": LAM, "candidate_features": cand_names, "control_features": "1, log2 r, log2 p, log2 cofactor, |Aut| one-hot, family one-hot",
           "mean_sem_over_mean": sem_ratio, "targets": {}}
PERMS = 1000
for name, y in targets.items():
    r0, _ = oof_r2(Xc, y); r1, _ = oof_r2(np.hstack([Xc, Xk]), y); gain = r1 - r0
    null = []
    for _ in range(PERMS):
        Xp = Xk.copy()
        for p in np.unique(primes):
            idx = np.where(primes == p)[0]; Xp[idx] = Xk[rng.permutation(idx)]
        rp, _ = oof_r2(np.hstack([Xc, Xp]), y); null.append(rp - r0)
    null = np.array(null)
    # single-feature univariate gains for the two headline features
    uni = {}
    for fname in ("log2_f_End", "vol_level2", "vol_level3", "log2_h_End", "n_down"):
        j = cand_names.index(fname); rj, _ = oof_r2(np.hstack([Xc, Xk[:, [j]]]), y); uni[fname] = float(rj - r0)
    _, pred0 = oof_r2(Xc, y); resid_sd = float((y - pred0).std())
    results["targets"][name] = dict(oof_R2_controls=float(r0), oof_R2_controls_plus_candidates=float(r1), gain=float(gain),
                                    residual_sd_after_controls_log_units=resid_sd, noise_floor_mean_sem_over_mean=sem_ratio[name],
                                    residual_sd_over_noise_floor=float(resid_sd / sem_ratio[name]),
                                    null_gain_mean=float(null.mean()), null_gain_95pct=float(np.percentile(null, 95)), null_gain_max=float(null.max()),
                                    p_perm=float(((null >= gain).sum() + 1) / (PERMS + 1)), univariate_gains=uni)
json.dump(results, open(out, "w"), indent=1)
for name, t in results["targets"].items():
    print(f"{name}: R2 controls={t['oof_R2_controls']:.4f}  +candidates={t['oof_R2_controls_plus_candidates']:.4f}  gain={t['gain']:+.4f}  null95={t['null_gain_95pct']:+.4f} nullmax={t['null_gain_max']:+.4f}  p={t['p_perm']:.3f}  uni={ {k: round(v,4) for k,v in t['univariate_gains'].items()} }")
print("curves", len(rows), "classes", len(uniq), "sem/mean", sem_ratio)
