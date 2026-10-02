"""03 -- F6 (b) and (d): plug-in nulls for the per-instance predicate (choices F6-2, F6-3).

NULL-P  : on-mode r* = relations_obs + CP(mu_TT) + CP(mu_TB) + CP(mu_SS), mu_c = the row's own
          harvest poisson_mean at_stop (H1 first moments), jumps = pooled 02_bundles
          pairs-per-relation law of complete random-arm records of the same (m, class).
          Census mode: r* = relations_obs (no harvested rows are fed), so NULL-P cannot fire
          beyond the observed.
NULL-B  : NULL-P with every mu_c scaled by one factor so that E[r*] = X^2/N, X = 2*S_3 (on);
          census r* ~ Poisson(X^2/N) (unit jumps; decomposition relations come singly).
NULL-G  : stopping-count null for r_rank (both modes) and census r_frozen:
          u_tau ~ Gamma(q, 1/kappa), q = rank + 1 (k-determining row counted as the q-th event)
          for r_rank, q = relations for census r_frozen; fire iff u_tau < 0.81 * r with r = rank
          (r_rank) or relations (census r_frozen). kappa = 1 and kappa_hat (ratio of sums of q
          over sums of u = X^2/N on random arms, per (m, mode)).
Per-instance p_i are computed EXACTLY (FFT for compound Poisson, incomplete gamma) -- a
deviation from F6-3's Monte Carlo (DV-2), cross-checked by 200 seeds x 4000 draws on the
21 generic firing instances (MC-2). Expected counts per (panel, m, mode, class, rung) and
pooled; P(>= observed) by exact Poisson-binomial DP; family-wise rates (MC-4).
"""
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib575 import OUT, WT, dump  # noqa: E402
from numlib import cp_pmf, gammainc_lower_reg, poisson_binomial_tail, poisson_sf  # noqa: E402

BUNDLES = os.path.join(WT, "coordination", "review", "pfdr-1b78f7-20260929", "reviews",
                       "TASK-20260929-f29c96", "attacks", "out", "02_bundles.jsonl")
CLS = ("TT", "TB", "SS")


def jump_laws():
    agg = defaultdict(Counter)
    for line in open(BUNDLES):
        r = json.loads(line)
        if r["scope"] != "stop" or not r["complete"] or not r["arm"].startswith("random"):
            continue
        for k, v in r["mult_hist"].items():
            agg[(r["m"], r["class"])][int(k)] += v
    laws = {}
    for key, cnt in agg.items():
        kmax = max(cnt)
        pmf = np.zeros(kmax + 1)
        tot = sum(cnt.values())
        for k, v in cnt.items():
            pmf[k] = v / tot
        EJ = float(np.dot(np.arange(kmax + 1), pmf))
        EJ2 = float(np.dot(np.arange(kmax + 1) ** 2, pmf))
        laws[key] = {"pmf": pmf, "EJ": EJ, "D": EJ2 / EJ, "kmax": kmax, "relations": tot}
    return laws


def cp_tail(rel, mus, laws, m, thr):
    """P(rel + sum_c CP(mu_c) > thr) exactly; mus = {class: mean pairs}."""
    lam, mix = 0.0, None
    parts = []
    for c in CLS:
        mu = mus.get(c, 0.0)
        if mu <= 0:
            continue
        L = laws[(m, c)]
        lc = mu / L["EJ"]
        parts.append((lc, L["pmf"]))
        lam += lc
    need = thr - rel
    if need < 0:
        return 1.0
    if lam <= 0:
        return 0.0
    kmax = max(len(p) for _, p in parts)
    mix = np.zeros(kmax)
    for lc, p in parts:
        mix[:len(p)] += (lc / lam) * p
    f = cp_pmf(lam, mix)
    k = int(math.floor(need))  # fire iff CP > need  <=>  CP >= k + 1
    if k + 1 >= len(f):
        return 0.0
    return float(f[k + 1:].sum())


def main():
    laws = jump_laws()
    xs = [json.loads(l) for l in open(os.path.join(OUT, "instances.jsonl"))]
    ev = [x for x in xs if x["evaluable"] and x["src"] != "stage-r"]
    # kappa_hat per (m, mode) from random arms
    kap = {}
    for m in (3, 4, 5):
        for mode in ("census", "on"):
            rs = [x for x in ev if x["m"] == m and x["mode"] == mode and x["cls"] == "random"]
            u = sum(4 * x["S"] ** 2 / x["N"] for x in rs)
            kap[(m, mode, "rank")] = sum(x["rank"] + 1 for x in rs) / u
            kap[(m, mode, "rel")] = sum(x["relations"] for x in rs) / u
            kap[(m, mode, "frozen")] = sum(x["r_frozen"] for x in rs) / u
    recs = []
    for x in ev:
        S, N, m, mode = x["S"], x["N"], x["m"], x["mode"]
        u = 4 * S * S / N
        thr = u / 0.81
        rec = {"key": [x["panel"], x["bits"], x["curve"], m, x["arm"], mode], "cls": x["cls"], "m": m,
               "mode": mode, "bits": x["bits"], "panel": x["panel"],
               "fire_frozen": x["ratio"] < 0.9,
               "fire_rank": x["S"] / (0.5 * math.sqrt(x["rank"] * N)) < 0.9 if x["rank"] > 0 else None,
               "fire_rank1": x["S"] / (0.5 * math.sqrt((x["rank"] + 1) * N)) < 0.9,
               "u": u, "r_frozen": x["r_frozen"], "rank": x["rank"]}
        if mode == "on":
            mus = {c: x[f"mu_{c}"] for c in CLS}
            rec["mu_sum"] = sum(mus.values())
            rec["p_P"] = cp_tail(x["relations"], mus, laws, m, thr)
            phi = (u - x["relations"]) / rec["mu_sum"] if rec["mu_sum"] > 0 else 0.0
            rec["phi_B"] = phi
            rec["p_B"] = cp_tail(x["relations"], {c: phi * v for c, v in mus.items()}, laws, m, thr) if phi > 0 else 1.0
            rec["obs_over_H1"] = (x["r_frozen"] - x["relations"]) / rec["mu_sum"] if rec["mu_sum"] > 0 else None
        else:
            rec["p_P"] = 1.0 if x["relations"] > thr else 0.0
            k = int(math.floor(thr)) + 1
            rec["p_B"] = poisson_sf(k, u)  # P(Poisson(u) >= floor(thr)+1)
            rec["p_G_rel_k1"] = gammainc_lower_reg(x["relations"], 0.81 * x["relations"]) if x["relations"] > 0 else 0.0
            kh = kap[(m, mode, "rel")]
            rec["p_G_rel_khat"] = gammainc_lower_reg(x["relations"], 0.81 * x["relations"] * kh) if x["relations"] > 0 else 0.0
        q = x["rank"] + 1
        rec["p_G_rank_k1"] = gammainc_lower_reg(q, 0.81 * x["rank"]) if x["rank"] > 0 else 1.0
        kh = kap[(m, mode, "rank")]
        rec["p_G_rank_khat"] = gammainc_lower_reg(q, 0.81 * x["rank"] * kh) if x["rank"] > 0 else 1.0
        recs.append(rec)

    def fam(sel):
        return [r for r in recs if sel(r)]

    def summarize(rs, pkey, obskey):
        ps = [r[pkey] for r in rs if r.get(pkey) is not None]
        obs = sum(1 for r in rs if r.get(obskey))
        E = sum(ps)
        return {"n": len(ps), "observed": obs, "expected": E,
                "P_ge_observed": poisson_binomial_tail(ps, obs),
                "familywise_P_ge_1": 1 - float(np.prod([1 - p for p in ps]))}

    out = {"jump_laws": {f"m{m}|{c}": {"EJ": L["EJ"], "D_index": L["D"], "kmax": L["kmax"],
                                       "relations_in_law": L["relations"]}
                         for (m, c), L in sorted(laws.items())},
           "kappa_hat": {f"m{m}|{mo}|{w}": v for (m, mo, w), v in sorted(kap.items())},
           "families": {}, "cells": {}}
    classes = ("random", "structured", "j0_random", "known_log", "j0_coset")
    for mode in ("on", "census"):
        for cl in classes:
            for m in (3, 4, 5):
                rs = fam(lambda r, cl=cl, m=m, mode=mode: r["cls"] == cl and r["m"] == m and r["mode"] == mode)
                if not rs:
                    continue
                blk = {}
                if mode == "on":
                    blk["frozen_NULL_P"] = summarize(rs, "p_P", "fire_frozen")
                    blk["frozen_NULL_B"] = summarize(rs, "p_B", "fire_frozen")
                else:
                    blk["frozen_NULL_P"] = summarize(rs, "p_P", "fire_frozen")
                    blk["frozen_NULL_B_poisson_u"] = summarize(rs, "p_B", "fire_frozen")
                    blk["frozen_NULL_G_k1"] = summarize(rs, "p_G_rel_k1", "fire_frozen")
                    blk["frozen_NULL_G_khat"] = summarize(rs, "p_G_rel_khat", "fire_frozen")
                blk["rank_NULL_G_k1"] = summarize(rs, "p_G_rank_k1", "fire_rank")
                blk["rank_NULL_G_khat"] = summarize(rs, "p_G_rank_khat", "fire_rank")
                blk["rank1_observed"] = sum(1 for r in rs if r["fire_rank1"])
                out["families"][f"{mode}|{cl}|m{m}"] = blk
    # pooled generic families
    for mode in ("on", "census"):
        for name, sel in (("generic_all", lambda r: r["cls"] in ("random", "structured", "j0_random")),
                          ("random", lambda r: r["cls"] == "random"),
                          ("structured", lambda r: r["cls"] == "structured"),
                          ("all_evaluable", lambda r: True)):
            rs = [r for r in recs if r["mode"] == mode and sel(r)]
            blk = {"frozen_NULL_P": summarize(rs, "p_P", "fire_frozen"),
                   "frozen_NULL_B": summarize(rs, "p_B", "fire_frozen"),
                   "rank_NULL_G_k1": summarize(rs, "p_G_rank_k1", "fire_rank"),
                   "rank_NULL_G_khat": summarize(rs, "p_G_rank_khat", "fire_rank")}
            out["families"][f"{mode}|POOLED|{name}"] = blk
    # cells per (panel, m, mode, class, rung)
    cells = defaultdict(list)
    for r in recs:
        cells[(r["panel"], r["m"], r["mode"], r["cls"], r["bits"])].append(r)
    for k, rs in sorted(cells.items()):
        blk = {"n": len(rs), "obs_frozen": sum(r["fire_frozen"] for r in rs),
               "E_P": sum(r["p_P"] for r in rs), "E_B": sum(r["p_B"] for r in rs),
               "obs_rank": sum(1 for r in rs if r["fire_rank"]),
               "E_G_rank_k1": sum(r["p_G_rank_k1"] for r in rs),
               "E_G_rank_khat": sum(r["p_G_rank_khat"] for r in rs)}
        blk["P_ge_obs_P"] = poisson_binomial_tail([r["p_P"] for r in rs], blk["obs_frozen"])
        blk["P_ge_obs_B"] = poisson_binomial_tail([r["p_B"] for r in rs], blk["obs_frozen"])
        out["cells"]["|".join(map(str, k))] = blk
    out["firing_instances_generic"] = sorted(
        [{"key": r["key"], "cls": r["cls"], "p_P": r["p_P"], "p_B": r["p_B"], "phi_B": r.get("phi_B"),
          "obs_over_H1_mean": r.get("obs_over_H1"), "p_G_rank_k1": r["p_G_rank_k1"]}
         for r in recs if r["fire_frozen"] and r["cls"] in ("random", "structured")],
        key=lambda d: d["key"])
    out["observed_rank_firings"] = sorted([{"key": r["key"], "cls": r["cls"]} for r in recs if r["fire_rank"]],
                                          key=lambda d: d["key"])
    out["observed_rank1_firings"] = sorted([{"key": r["key"], "cls": r["cls"]} for r in recs if r["fire_rank1"]],
                                           key=lambda d: d["key"])
    # observed vs H1 mean on on-mode generic rows (all, not only firing)
    rat = [r["obs_over_H1"] for r in recs if r["mode"] == "on" and r["cls"] in ("random", "structured")
           and r.get("obs_over_H1") is not None]
    out["on_generic_harvested_rows_over_H1_mean"] = {
        "n": len(rat), "mean": float(np.mean(rat)), "median": float(np.median(rat)),
        "q90": float(np.quantile(rat, 0.9)), "q99": float(np.quantile(rat, 0.99)), "max": float(max(rat))}

    # ---- MC-2 cross-check: 200 seeds x 4000 draws on the 21 generic firing instances -----------
    xs_by_key = {(x["panel"], x["bits"], x["curve"], x["m"], x["arm"], x["mode"]): x for x in ev}
    mc = []
    for fr in out["firing_instances_generic"]:
        x = xs_by_key[tuple(fr["key"])]
        u = 4 * x["S"] ** 2 / x["N"]
        need = u / 0.81 - x["relations"]
        ests = []
        for seed in range(200):
            rng = np.random.default_rng(seed)
            tot = np.zeros(4000)
            for c in CLS:
                mu = x[f"mu_{c}"]
                if mu <= 0:
                    continue
                L = laws[(x["m"], c)]
                K = rng.poisson(mu / L["EJ"], 4000)
                draws = rng.choice(len(L["pmf"]), size=int(K.sum()), p=L["pmf"])
                idx = np.repeat(np.arange(4000), K)
                tot += np.bincount(idx, weights=draws, minlength=4000)
            ests.append(float(np.mean(tot > need)))
        mc.append({"key": fr["key"], "p_P_exact": fr["p_P"], "mc_mean_200x4000": float(np.mean(ests)),
                   "mc_sd_across_seeds": float(np.std(ests, ddof=1)),
                   "mc_se_of_mean": float(np.std(ests, ddof=1) / math.sqrt(200)),
                   "z_exact_vs_mc": (float(np.mean(ests)) - fr["p_P"]) / max(1e-12, float(np.std(ests, ddof=1)) / math.sqrt(200))})
    out["mc2_crosscheck_null_P"] = mc
    dump("03_f6_nulls.json", out)
    with open(os.path.join(OUT, "03_f6_instance_p.jsonl"), "w") as fh:
        for r in recs:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    show = {k: v for k, v in out["families"].items()}
    print(json.dumps(out["jump_laws"], indent=0))
    print(json.dumps(out["kappa_hat"], indent=0))
    print(json.dumps(show, indent=0)[:12000])


if __name__ == "__main__":
    main()
