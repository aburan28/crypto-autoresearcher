"""J8 diagnostic (declared after reading heur.json, because the Monte-Carlo KS p of the H1c PIT came out
below the asymptotic p in all four cells, whereas a calibrated asymptotic p and an estimated-parameter
MC should give MC p >= asymptotic p): the null law of the PIT KS distance D for the actual TT5 and TT4
random-arm instances, (a) with the true means, (b) with rho1 re-estimated per rung, against the
Stephens-asymptotic Kolmogorov law. 1000 replicates each; seed SeedSequence([0x87ffc4, 320, k]).
Command: nice -n 19 $PY attacks/j8/j8_ks_diag.py --out attacks/j8/out/ks_diag.json"""
import argparse, json, os, sys, random
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L

def pit_D(cnt, lam, u):
    kmax = int(cnt.max()) + 1
    Fm = np.zeros(len(cnt)); F = np.zeros(len(cnt))
    term = np.exp(-lam); cum = term.copy()
    F[cnt == 0] = cum[cnt == 0]
    for k in range(1, kmax + 1):
        sel = cnt == k
        Fm[sel] = cum[sel]
        term = term * lam / k
        cum = cum + term
        F[sel] = cum[sel]
    pv = np.sort(Fm + u * (F - Fm)); n = len(pv)
    return float(max(np.max(np.arange(1, n + 1) / n - pv), np.max(pv - np.arange(0, n) / n)))

ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); a = ap.parse_args()
design = L.load_design(); rows = L.load_extract()
groups, rho1, _ = L.build_groups(rows, design)
out = {}
for k, (cls, m) in enumerate((("TT", 5), ("TT", 4), ("TT", 3), ("TB", 3))):
    mus, bs, obs = [], [], []
    for b in L.BAND:
        for c in L.curve_list(design, "table", m, b):
            for fam in ("SUB", "DICK"):
                for arm in L.RANDOMS[fam]:
                    r = rows[(b, c, m, arm, "table")]
                    mus.append(L.mu_model(r, cls, m)); bs.append(b); obs.append(r[cls]["n"])
    mus, bs, obs = np.array(mus), np.array(bs), np.array(obs)
    r1 = np.array([rho1[("pooled", cls, m, b)] for b in bs])
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 320, k]))
    Dt, De = [], []
    for _ in range(1000):
        cnt = rng.poisson(r1 * mus)
        Dt.append(pit_D(cnt, r1 * mus, rng.random(len(cnt))))
        r1h = np.zeros_like(r1)
        for b in L.BAND:
            s = bs == b
            r1h[s] = cnt[s].sum() / mus[s].sum()
        De.append(pit_D(cnt, r1h * mus, rng.random(len(cnt))))
    n = len(mus)
    Dt, De = np.array(Dt), np.array(De)
    pt = np.array([L.kolmogorov_sf(d, n) for d in Dt]); pe = np.array([L.kolmogorov_sf(d, n) for d in De])
    out[f"{cls}{m}"] = {"n": int(n), "true_means": {"mean_asymptotic_p": float(pt.mean()), "frac_p_lt_0.01": float(np.mean(pt < 0.01)), "D_median": float(np.median(Dt))},
                        "estimated_rho1": {"mean_asymptotic_p": float(pe.mean()), "frac_p_lt_0.01": float(np.mean(pe < 0.01)), "D_median": float(np.median(De))}}
    print(cls, m, out[f"{cls}{m}"], flush=True)
L.jdump(a.out, out)
