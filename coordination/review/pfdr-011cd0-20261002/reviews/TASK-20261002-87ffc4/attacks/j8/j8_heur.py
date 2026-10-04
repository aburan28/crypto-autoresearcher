"""J8: the O-HEUR readings recomputed with this reviewer's own code from the archived counts
(extract of the canonical rows), per attacks/j8/00-readings-before-computing.yaml.

Seeds: bootstrap SeedSequence([0x87ffc4, 300]); KS Monte-Carlo SeedSequence([0x87ffc4, 310, k]);
PIT uniforms: the FROZEN random.Random(f"pit-011cd0|{bits}|{c}|{m}|{arm}|{class}").
Command: nice -n 19 $PY attacks/j8/j8_heur.py --out attacks/j8/out/heur.json
"""
import argparse
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L  # noqa: E402

BOOT = 20000


def curve_records(rows, design, cls, m):
    """Per curve of the 30-32 band: list of (b, c, [(fam, arm, rec) x 6])."""
    panel = L.PANEL[cls]
    out = []
    for b in L.BAND:
        for c in L.curve_list(design, panel, m, b):
            recs = []
            for fam in ("SUB", "DICK"):
                rs = [(fam, a, rows.get((b, c, m, a, panel))) for a in L.RANDOMS[fam]]
                if any(r is None or r["status"] != "completed_valid" for _, _, r in rs):
                    continue
                recs += rs
            if recs:
                out.append((b, c, recs))
    return out


def pairs_of(r, cls):
    return r["SSx"]["pairs"] if cls == "SS" else r[cls]["pairs"]


def rel_of(r, cls):
    return r["SSx"]["n"] if cls == "SS" else r[cls]["n"]


def hist_of(r, cls):
    return r["SSx"]["hist"] if cls == "SS" else r[cls]["hist"]


def mu_pairs(r, cls):
    N = r["N"]
    if cls == "TT":
        return r["Ep"] * (r["Ep"] - 1) / N
    if cls == "TB":
        return 2.0 * r["Ep"] * r["s"] / N
    X = r["SSx"]["X"]
    return X * (X - 1) / N


def boot_ci99(rng, n, fn, est):
    vals = []
    for st in range(0, BOOT, 2000):
        ii = rng.integers(0, n, size=(min(2000, BOOT - st), n))
        with np.errstate(divide="ignore", invalid="ignore"):
            vals.append(fn(ii))
    v = np.concatenate(vals)
    v = v[np.isfinite(v)]
    lo, hi = np.quantile(v, [0.005, 0.995])
    corr = math.sqrt(n / (n - 1))
    return [float(est + corr * (lo - est)), float(est + corr * (hi - est))], [float(lo), float(hi)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--ks-mc", type=int, default=400)
    a = ap.parse_args()
    t0 = time.time()
    design = L.load_design()
    rows = L.load_extract()
    groups_pf, rho1, _ = L.build_groups(rows, design, rho1_mode="per_family")
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 300]))
    res = {"task": "TASK-20261002-87ffc4", "joint": "J8", "H1a": {}, "H1b": {}, "H1c": {}, "H5": {},
           "hist_summary": {}, "censored_SS_random_instances": 0}
    for (cls, m) in L.FAM1_CM:
        key = f"{cls}{m}"
        cr = curve_records(rows, design, cls, m)
        n = len(cr)
        y = np.array([sum(pairs_of(r, cls) for _, _, r in recs) for _, _, recs in cr], dtype=float)
        x = np.array([sum(mu_pairs(r, cls) for _, _, r in recs) for _, _, recs in cr], dtype=float)
        if cls == "SS":
            res["censored_SS_random_instances"] += sum(1 for _, _, recs in cr for _, _, r in recs if r["SSx"]["censored"])
        R = y.sum() / x.sum()
        se = math.sqrt(n / (n - 1) * ((y - R * x) ** 2).sum()) / x.sum()
        tq = L.t_quantile(0.995, n - 1)
        ci_t = [R - tq * se, R + tq * se]
        ci_b, _ = boot_ci99(rng, n, lambda ii: y[ii].sum(1) / x[ii].sum(1), R)
        res["H1a"][key] = {"ratio": R, "ci99_t": ci_t, "ci99_boot": ci_b, "curves": n,
                           "refuted": ci_t[1] < 0.90 or ci_t[0] > 1.10,
                           "refuted_boot": ci_b[1] < 0.90 or ci_b[0] > 1.10}
        # within-curve per-family triples
        s2p, nbp, s2r, nbr, M1, M2, Ns = [], [], [], [], [], [], []
        hist = Counter()
        for _, _, recs in cr:
            a_s2p = a_nbp = a_s2r = a_nbr = 0.0
            m1 = m2 = 0
            for fam in ("SUB", "DICK"):
                tri = [r for f_, _, r in recs if f_ == fam]
                if len(tri) != 3:
                    continue
                pl = np.array([pairs_of(r, cls) for r in tri], dtype=float)
                rl = np.array([rel_of(r, cls) for r in tri], dtype=float)
                a_s2p += pl.var(ddof=1)
                a_nbp += pl.mean()
                a_s2r += rl.var(ddof=1)
                a_nbr += rl.mean()
                for r in tri:
                    Ns.append(r["N"])
                    for k, v in hist_of(r, cls).items():
                        hist[int(k)] += v
                        m1 += int(k) * v
                        m2 += int(k) * int(k) * v
            s2p.append(a_s2p)
            nbp.append(a_nbp)
            s2r.append(a_s2r)
            nbr.append(a_nbr)
            M1.append(m1)
            M2.append(m2)
        s2p, nbp, s2r, nbr = map(np.array, (s2p, nbp, s2r, nbr))
        M1, M2 = np.array(M1, dtype=float), np.array(M2, dtype=float)
        Nbar = float(np.mean(Ns))
        DP = s2p.sum() / nbp.sum()
        DPpred = (1 - 1 / Nbar) * M2.sum() / M1.sum()
        ratio = DP / DPpred
        ci, raw = boot_ci99(rng, n, lambda ii: (s2p[ii].sum(1) / nbp[ii].sum(1)) /
                            ((1 - 1 / Nbar) * M2[ii].sum(1) / M1[ii].sum(1)), ratio)
        # heavy-tail diagnostic: share of sum M^2 carried by the top 1% of curves
        order = np.sort(M2)[::-1]
        top = order[: max(1, n // 100)].sum() / M2.sum() if M2.sum() else None
        res["H1b"][key] = {"D_P_hat": DP, "D_P_pred": DPpred, "ratio": ratio, "ci99": ci,
                           "ci99_uncorrected": raw, "refuted": ci[1] < 0.8 or ci[0] > 1.25,
                           "share_of_sumM2_in_top1pct_curves": top}
        DR = s2r.sum() / nbr.sum()
        ci, raw = boot_ci99(rng, n, lambda ii: s2r[ii].sum(1) / nbr[ii].sum(1), DR)
        ent = {"D_R": DR, "ci99": ci, "ci99_uncorrected": raw, "curves": n}
        mean_M = M1.sum() / sum(hist.values()) if hist else None
        res["hist_summary"][key] = {"relations": int(sum(hist.values())), "pairs_from_hist": int(M1.sum()),
                                    "mean_M": mean_M, "max_M": max(hist) if hist else None,
                                    "generic_M": (L.MGEN[cls][L.H_OF_M[m]] if cls != "SS" else None),
                                    "share_relations_at_generic_M": (hist[L.MGEN[cls][L.H_OF_M[m]]] / sum(hist.values())
                                                                     if cls != "SS" and hist else None)}
        if cls == "SS":
            ent["refuted_H5"] = ci[0] > 4
            res["H5"][key] = ent
        else:
            ent["refuted_dispersion_clause"] = ci[1] < 0.8 or ci[0] > 1.25
            # PIT KS, both rho1 readings
            for mode in ("pooled", "per_family"):
                pit = []
                inst = []
                for b, c, recs in cr:
                    for fam, arm, r in recs:
                        r1 = rho1[(("pooled" if mode == "pooled" else fam), cls, m, b)]
                        mj = r1 * L.mu_model(r, cls, m)
                        u = random.Random(f"pit-011cd0|{b}|{c}|{m}|{arm}|{cls}").random()
                        nn = rel_of(r, cls)
                        Fm = L.poisson_cdf(nn - 1, mj)
                        F = L.poisson_cdf(nn, mj)
                        pit.append(Fm + u * (F - Fm))
                        inst.append((b, fam, L.mu_model(r, cls, m)))
                u_ = np.sort(np.array(pit))
                nn2 = len(u_)
                D = float(max(np.max(np.arange(1, nn2 + 1) / nn2 - u_), np.max(u_ - np.arange(0, nn2) / nn2)))
                ent[f"pit_ks_{mode}"] = {"n": nn2, "D": D, "p_asymptotic": L.kolmogorov_sf(D, nn2),
                                         "rejects_1pct": L.kolmogorov_sf(D, nn2) < 0.01}
                if mode == "pooled":
                    # Monte-Carlo null of the whole procedure: Poisson counts at the fitted means,
                    # rho1 re-estimated per replicate, fresh PIT uniforms
                    mcr = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 310, L.FAM1_CM.index((cls, m))]))
                    mus = np.array([x[2] for x in inst])
                    bs = np.array([x[0] for x in inst])
                    r1v = np.array([rho1[("pooled", cls, m, b)] for b in bs])
                    Dsim = []
                    for _ in range(a.ks_mc):
                        cnt = mcr.poisson(r1v * mus)
                        # re-estimate rho1 per rung
                        r1h = np.zeros_like(r1v)
                        for b in L.BAND:
                            sel = bs == b
                            r1h[sel] = cnt[sel].sum() / mus[sel].sum()
                        lam = r1h * mus
                        # Poisson CDF vectorised via cumulative sums is heavy for large n; use
                        # the regularised gamma through a cumulative product on small counts
                        kmax = int(cnt.max()) + 1
                        Fm = np.zeros(len(cnt))
                        F = np.zeros(len(cnt))
                        term = np.exp(-lam)
                        cum = term.copy()
                        Fm[cnt == 0] = 0.0
                        F[cnt == 0] = cum[cnt == 0]
                        for k in range(1, kmax + 1):
                            sel = cnt == k
                            Fm[sel] = cum[sel]
                            term = term * lam / k
                            cum = cum + term
                            F[sel] = cum[sel]
                        uu = mcr.random(len(cnt))
                        pv = np.sort(Fm + uu * (F - Fm))
                        Dsim.append(float(max(np.max(np.arange(1, len(pv) + 1) / len(pv) - pv),
                                              np.max(pv - np.arange(0, len(pv)) / len(pv)))))
                    Dsim = np.array(Dsim)
                    ent["pit_ks_pooled"]["p_monte_carlo"] = float(np.mean(Dsim >= D))
                    ent["pit_ks_pooled"]["mc_replicates"] = int(len(Dsim))
                    ent["pit_ks_pooled"]["null_rejection_rate_of_asymptotic_1pct"] = float(
                        np.mean([L.kolmogorov_sf(d, nn2) < 0.01 for d in Dsim]))
            res["H1c"][key] = ent
        print(key, json.dumps({"H1a": res["H1a"][key], "H1b": res["H1b"][key]}, default=str)[:900], flush=True)
    # H3 (A3R): all rungs, every arm
    acc = defaultdict(list)
    for k, r in rows.items():
        b, c, m, arm, mode = k
        if r["status"] != "completed_valid":
            continue
        for cls in (("TT", "TB") if mode == "table" else ("SS",)):
            st = r[cls]
            if st["R_star"] >= 10:
                acc[(arm, cls, m)].append(st["irank"] / min(st["R_star"], r["U"]))
    h3 = {}
    for (arm, cls, m), v in sorted(acc.items()):
        h3[f"{arm}|{cls}{m}"] = {"qualifying": len(v), "median": float(np.median(v)),
                                 "evaluated": len(v) >= 20, "share_below_095": float(np.mean(np.array(v) < 0.95)),
                                 "min": float(np.min(v)),
                                 "median_ge_095": (float(np.median(v)) >= 0.95) if len(v) >= 20 else None}
    res["H3_A3R"] = h3
    # which (random arm, class, m) of the FAM-1 set are NOT evaluable
    res["H3_not_evaluable_random"] = sorted(
        f"{arm}|{cls}{m}" for (cls, m) in L.FAM1_CM for fam in ("SUB", "DICK") for arm in L.RANDOMS[fam]
        if f"{arm}|{cls}{m}" not in h3 or not h3[f"{arm}|{cls}{m}"]["evaluated"])
    # SS relation dispersion at X_fix PER RUNG (random arms, both families): de-confounds the TA-1
    # comparison (P0 inputs were at 22-24 bits AND at scope A_fix; the band is 30-32 at X_fix)
    ssr = {}
    for m in (3, 4, 5):
        for b in L.RUNGS:
            s2 = nb = 0.0
            ncur = 0
            for c in L.curve_list(design, "search", m, b):
                for fam in ("SUB", "DICK"):
                    tri = [rows.get((b, c, m, x, "search")) for x in L.RANDOMS[fam]]
                    if any(r is None or r["status"] != "completed_valid" for r in tri):
                        continue
                    v = np.array([r["SSx"]["n"] for r in tri], dtype=float)
                    s2 += v.var(ddof=1)
                    nb += v.mean()
                ncur += 1
            ssr[f"SS{m}|{b}"] = {"curves": ncur, "D_R_pooled_within_curve": s2 / nb if nb else None,
                                 "mean_relations_per_instance": nb / (2 * ncur) if ncur else None}
    res["SS_dispersion_per_rung_X_fix"] = ssr
    res["seconds"] = time.time() - t0
    L.jdump(a.out, res)
    print("done", round(time.time() - t0))


if __name__ == "__main__":
    main()
