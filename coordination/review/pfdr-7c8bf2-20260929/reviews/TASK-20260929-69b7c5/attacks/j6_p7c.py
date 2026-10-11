"""J6: the descriptive P7(c) randomized-PIT KS comparison and the m = 7 rejection.

Reads the committed primary-series mitm rows (P3), forms X_t = table_entries,
X_s = 2*search, mu = 2*X_t*X_s/N per P7(c), pooled c_m = sum(r)/sum(mu), randomized PIT
with V from random.Random("pit-7c8bf2|<file>|<bits>|<curve>|<fb>|<m>") as frozen, and the
two-sided one-sample KS test.  The exact KS p-value function is the committed
analyze_floor.ks_pvalue, loaded by file path (module body only defines functions; main()
is not executed; no solver is imported).

  A. observed per-m (anchor only; J3 is the validator's) + per-rung PIT/q structure
  B. the same test with the smallest rungs removed (12; 12+14), c re-estimated
  C. exact 1% critical values D_crit(n) by bisection on ks_pvalue
  D. simulated nulls, K = 2000 replicates per m and model (fresh PIT randomisation V):
       S0  correctly specified: r_i ~ Poisson(c*mu_i) at the observed effort mu_i (no stop)
       S1  stopping rule, Poisson arrivals: stop at the observed count r_i, effort
           mu_i* ~ Gamma(r_i, 1/c) (time of the r_i-th arrival), r_i reported
       S2  plan's wording: stop at rank |F|+1 with Poisson arrivals, every relation
           raising rank: r_i = fb_size_i + 1, mu_i* ~ Gamma(r_i, 1/c)
       S3  UPPER BRACKET, not a model of the engine: stopping rule with per-attempt
           arrivals, success probability P_i = r_i/attempts_i per target, stop at r_i
           successes, attempts* = r_i + NegBin(r_i, P_i) failures, mu_i* = attempts* x
           (mu_i/attempts_i).  Each row keeps its OBSERVED yield as its true rate, so the
           observed row-to-row heterogeneity is planted and then re-noised.
     each: rejection rate at 1% (D >= D_crit), P(D >= D_obs(m)), family-wise over 5 m.
Seeds: numpy default_rng([0x69b7c5, 7, m, model_index]).
"""
import importlib.util
import math
import os
import random
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "rt69b7c5_analyze_floor", os.path.join(C.WT, "experiments", "EXP-PFDR-7c8bf2", "analyze_floor.py"))
AF = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AF)
ks_pvalue = AF.ks_pvalue
assert not [m for m in sys.modules if m.startswith("crypto_autoresearcher")], "solver module loaded"

K = 2000
MS = [3, 4, 5, 6, 7]


def rows_for_m(m):
    out = []
    for name in C.SERIES:
        f, mm, fb = C.SERIES[name]
        if mm != m:
            continue
        for r in C.series_rows(name):
            S, T = r["s3_solves"], r["table_s3_solves"]
            mu = 2 * r["table_entries"] * (2 * (S - T)) / r["N"]
            out.append({"file": f, "bits": r["bits"], "curve": r["curve"], "fb": fb, "m": m,
                        "r": r["relations"], "mu": mu, "F": r["fb_size"], "att": r["attempts"]})
    return out


def pois_cdf_vec(n, g):
    """P(Pois(g) <= n) for integer n >= -1 and array g (log-space summation)."""
    g = np.asarray(g, float)
    if n < 0:
        return np.zeros_like(g)
    k = np.arange(n + 1)
    lg = np.array([math.lgamma(i + 1) for i in k])
    logp = -g[..., None] + k[None, :] * np.log(g)[..., None] - lg[None, :]
    return np.minimum(1.0, np.exp(logp).sum(-1))


def ks_D(U):
    """U: (K, n) -> two-sided KS statistic per row against Uniform(0,1)."""
    U = np.sort(U, axis=1)
    n = U.shape[1]
    i = np.arange(n)
    return np.maximum(((i + 1) / n - U).max(1), (U - i / n).max(1))


def observed(rows, m):
    c = sum(x["r"] for x in rows) / sum(x["mu"] for x in rows)
    us = []
    for x in rows:
        V = random.Random(f"pit-7c8bf2|{x['file']}|{x['bits']}|{x['curve']}|{x['fb']}|{m}").random()
        F1 = AF.poisson_cdf(x["r"], c * x["mu"])
        F0 = AF.poisson_cdf(x["r"] - 1, c * x["mu"])
        us.append(F0 + V * (F1 - F0))
    D = float(ks_D(np.array([us]))[0])
    return c, us, D, ks_pvalue(D, len(us))


def dispersion_index(bits, r, mu, c):
    """Within-rung variance of z = c*mu/r times mean r, averaged over rungs.

    Under Poisson arrivals stopped at count r (S1), c*mu ~ Gamma(r, 1) so Var(z) = 1/r and the
    index is about 1; homogeneous per-attempt (Bernoulli) arrivals with success probability P
    give about 1 - P < 1; row-to-row rate heterogeneity or extra effort scatter gives > 1.
    Within-rung |F| and N differences are not removed (they inflate the index)."""
    bits = np.asarray(bits)
    vals = []
    for b in np.unique(bits):
        sel = bits == b
        z = c * mu[..., sel] / r[..., sel]
        vals.append(z.var(axis=-1, ddof=1) * r[..., sel].mean(axis=-1))
    return np.mean(vals, axis=0)


def d_crit(n, alpha=0.01):
    # bracket around the asymptotic 1% value 1.628/sqrt(n) (keeps the exact matrix small)
    lo, hi = 0.6 * 1.628 / math.sqrt(n), 1.4 * 1.628 / math.sqrt(n)
    assert ks_pvalue(lo, n) > alpha > ks_pvalue(hi, n)
    for _ in range(40):
        mid = (lo + hi) / 2
        if ks_pvalue(mid, n) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


res = {"K": K, "per_m": {}, "family_wise": {}}
obs = {}
for m in MS:
    rows = rows_for_m(m)
    c, us, D, p = observed(rows, m)
    obs[m] = (rows, c, D)
    per_rung = {}
    for b in sorted({x["bits"] for x in rows}):
        idx = [i for i, x in enumerate(rows) if x["bits"] == b]
        per_rung[b] = {"mean_pit": statistics.fmean(us[i] for i in idx),
                       "median_q_over_c": statistics.median(rows[i]["r"] / rows[i]["mu"] / c for i in idx),
                       "relations": [rows[i]["r"] for i in idx]}
    trimmed = {}
    for drop in ((12,), (12, 14)):
        sub = [x for x in rows if x["bits"] not in drop]
        c2, us2, D2, p2 = observed(sub, m)
        trimmed["drop_" + "+".join(map(str, drop))] = {"n": len(sub), "c_m": c2, "D": D2, "p": p2, "reject_1pct": p2 < 0.01}
    n = len(rows)
    dec = np.histogram(us, bins=10, range=(0, 1))[0].tolist()
    disp = float(dispersion_index([x["bits"] for x in rows], np.array([x["r"] for x in rows], float),
                                  np.array([x["mu"] for x in rows]), c))
    res["per_m"][m] = {"n": n, "c_m": c, "D_obs": D, "p_obs": p, "reject_1pct_obs": p < 0.01,
                       "pit_decile_counts": dec, "dispersion_index_obs": disp,
                       "median_attempts_per_relation": statistics.median(x["att"] / x["r"] for x in rows),
                       "D_crit_1pct": d_crit(n), "per_rung": per_rung, "trimmed": trimmed}
    print("m=%d n=%d c=%.4f D=%.4f p=%.4f Dcrit=%.4f disp=%.3f att/rel=%.2f deciles=%s" % (
        m, n, c, D, p, res["per_m"][m]["D_crit_1pct"], disp, res["per_m"][m]["median_attempts_per_relation"], dec),
          {k: "D=%.3f p=%.4f" % (v["D"], v["p"]) for k, v in trimmed.items()},
          {b: "%.2f/%.2f" % (v["mean_pit"], v["median_q_over_c"]) for b, v in per_rung.items()}, flush=True)


def simulate(m, model, rng):
    rows, c, D_obs = obs[m]
    n = len(rows)
    r = np.array([x["r"] for x in rows])
    mu = np.array([x["mu"] for x in rows])
    F = np.array([x["F"] for x in rows])
    att = np.array([x["att"] for x in rows])
    if model == "S0":
        R = rng.poisson(c * mu[None, :], size=(K, n))
        MU = np.broadcast_to(mu, (K, n)).copy()
    elif model in ("S1", "S2"):
        rr = r if model == "S1" else F + 1
        R = np.broadcast_to(rr, (K, n)).copy()
        MU = rng.gamma(shape=rr[None, :], scale=1.0 / c, size=(K, n))
    elif model == "S3":
        P = r / att
        R = np.broadcast_to(r, (K, n)).copy()
        fails = rng.negative_binomial(r[None, :], P[None, :], size=(K, n))
        MU = (r[None, :] + fails) * (mu / att)[None, :]
    chat = R.sum(1) / MU.sum(1)
    G = chat[:, None] * MU
    U = np.empty((K, n))
    V = rng.random((K, n))
    for j in range(n):
        if model == "S0":
            kmax = int(R[:, j].max())
            k = np.arange(kmax + 1)
            lg = np.array([math.lgamma(i + 1) for i in k])
            pm = np.exp(-G[:, j, None] + k[None, :] * np.log(G[:, j, None]) - lg[None, :])
            cdf = np.minimum(1.0, np.cumsum(pm, 1))
            F1 = cdf[np.arange(K), R[:, j]]
            F0 = np.where(R[:, j] > 0, cdf[np.arange(K), np.maximum(R[:, j] - 1, 0)], 0.0)
        else:
            F1 = pois_cdf_vec(int(R[0, j]), G[:, j])
            F0 = pois_cdf_vec(int(R[0, j]) - 1, G[:, j])
        U[:, j] = F0 + V[:, j] * (F1 - F0)
    Ds = ks_D(U)
    dcrit = res["per_m"][m]["D_crit_1pct"]
    disp = dispersion_index([x["bits"] for x in rows], R.astype(float), MU, chat[:, None])
    DS_STORE[(model, m)] = Ds
    return Ds >= dcrit, {"reject_rate_1pct": float((Ds >= dcrit).mean()),
                         "median_dispersion_index": float(np.median(disp)),
                         "p_dispersion_le_obs": float((disp <= res["per_m"][m]["dispersion_index_obs"]).mean()),
                         "p_D_ge_D_obs": float((Ds >= D_obs).mean()),
                         "median_D": float(np.median(Ds)), "q99_D": float(np.quantile(Ds, 0.99))}


DS_STORE = {}
rej = {}
for mi, model in enumerate(("S0", "S1", "S2", "S3")):
    rej[model] = {}
    for m in MS:
        rng = np.random.default_rng([0x69b7c5, 7, m, mi])
        flags, summ = simulate(m, model, rng)
        rej[model][m] = flags
        res["per_m"][m].setdefault("sim", {})[model] = summ
        print(model, "m=%d" % m, {k: round(v, 4) for k, v in summ.items()}, flush=True)
    M = np.stack([rej[model][m] for m in MS], 1)
    res["family_wise"][model] = {"p_at_least_one_of_5_reject_1pct": float(M.any(1).mean()),
                                 "per_m_rate": {m: float(rej[model][m].mean()) for m in MS},
                                 "independence_formula_nominal": 1 - 0.99 ** 5}
    print("FW", model, res["family_wise"][model], flush=True)

# pattern check: the observed p-values are below 0.09 at four of five m (0.069, 0.082, 0.078,
# 0.0098).  How often does a simulated null give >= 4 of 5 m with p < 0.09?
def d_at(n, alpha):
    lo, hi = 0.3 * 1.628 / math.sqrt(n), 1.6 * 1.628 / math.sqrt(n)
    for _ in range(40):
        mid = (lo + hi) / 2
        if ks_pvalue(mid, n) > alpha:
            lo = mid
        else:
            hi = mid
    return hi


d09 = {m: d_at(res["per_m"][m]["n"], 0.09) for m in MS}
obs_count = sum(1 for m in MS if res["per_m"][m]["p_obs"] < 0.09)
res["pattern_p_below_0_09"] = {"D_at_p_0_09": d09, "observed_count": obs_count}
for model in ("S0", "S1", "S2", "S3"):
    cnt = sum((DS_STORE[(model, m)] >= d09[m]).astype(int) for m in MS)
    res["pattern_p_below_0_09"][model] = {"p_count_ge_observed": float((cnt >= obs_count).mean())}
print("pattern", res["pattern_p_below_0_09"], flush=True)
print(C.dump("j6_p7c.json", res))
