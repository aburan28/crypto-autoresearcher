#!/usr/bin/env python3
"""J7 (b): the P0 design path (AMD-20261002-c7ccde B-6 residual) re-derived in the validator's own code.

TASK-20261002-0114ff. Standard library plus numpy. Inputs: design.json's design curves
(N, X_fix, s_sub, s_dick per m) and its P0 inputs (rho1, D_R_ub95, Mbar per (class, m)),
i.e. the P0 estimates are taken as given; the design path downstream of them is re-derived:
  CC-9  E[C_R] per FAM-1 cell under the uniform model (no rho1) at the final n:
        TT: E'(E'-1)/N / (C(2h,h)/2), E' = s^2 (h = 2) or 4C(s+2,3) - 2C(s+1,2) (h = 3);
        TB: 2E's/N/(h+1); SS: X(X-1)/N / Mbar; summed over the band's design curves
        (c = 10 .. 10 + n - 1 at 30 and 32 bits), s = s_sub (subgroup, small_x) or s_dick.
  t*_plan  G-NB-R (A-CAL) at the design curves: every arm's count on curve j drawn from a
        negative binomial with mean rho1 x model_j and variance D x mean, D = max(ub95, 1) x 1.2
        (TT, TB) or x 1.5 (SS); the three randoms drawn once per replicate and family and shared
        by its structured arms; CC-8 z per FAM-1 cell; family max over the 21 cells; t* = mean
        over 5 seed families of the 0.95 quantile (20000 replicates each). Own seeds
        SeedSequence([0x0114ff, i]) (the producer used [0x011cd0, i]); agreement is expected
        within Monte Carlo error, never exactly.
  raise rule  per (panel, m): governing power = min(Poisson-planted, compound-planted) of
        P(z > t*_plan(declared design)) at kappa_target (1.15; TB3 1.5), 4000 replicates x 5
        families; if a cell is < 0.5 at the declared n, the smallest multiplier in
        {1.25, 1.5, 2, 2.5, 3} meeting 0.5 for every cell of that (panel, m).
Usage: j7_p0.py DESIGN_JSON OUT_JSON
"""
import json
import math
import sys

import numpy as np

CELLS = [("TT", 3), ("TT", 4), ("TT", 5), ("SS", 3), ("SS", 4), ("SS", 5), ("TB", 3)]
ARMS = {"SUB": ["subgroup", "small_x"], "DICK": ["dickson"]}
MULTS = [1.25, 1.5, 2.0, 2.5, 3.0]


def h_of(m):
    return max(1, min(m - 1, (m + 1) // 2))


def model(cls, m, s, N, X, Mbar):
    h = h_of(m)
    if cls in ("TT", "TB"):
        E = s * s if h == 2 else 4 * math.comb(s + 2, 3) - 2 * math.comb(s + 1, 2)
        if cls == "TT":
            return E * (E - 1) / N / (math.comb(2 * h, h) / 2)
        return 2 * E * s / N / (h + 1)
    return X * (X - 1) / N / Mbar


def main():
    d = json.load(open(sys.argv[1]))
    est = d["estimates"]
    curves = {(c["bits"], c["curve"]): c for c in d["curves"]}

    def band_means(cls, m, n, fam, with_rho=True):
        out = []
        for b in (30, 32):
            for c in range(10, 10 + n):
                cv = curves[(b, c)]
                sz = cv["sizes"][str(m)]
                s = sz["s_sub"] if fam == "SUB" else sz["s_dick"]
                mu = model(cls, m, s, cv["N"], cv["X_fix"], est[f"SS{m}"]["Mbar"] if cls == "SS" else None)
                out.append(mu * (est[f"{cls}{m}"]["rho1"] if with_rho else 1.0))
        return np.array(out)

    def n_of(panel, m, which):
        return d[which][panel][str(m)]["30"]

    res = {"E_C_R_uniform": {}}
    for cls, m in CELLS:
        panel = "search" if cls == "SS" else "table"
        for fam, arms in ARMS.items():
            v = float(band_means(cls, m, n_of(panel, m, "final_n"), fam, with_rho=False).sum())
            for a in arms:
                pid = f"{a}|{cls}{m}|band"
                p = d["cells"][pid]["E_C_R_uniform"]
                res["E_C_R_uniform"][pid] = {"own": v, "design": p, "rel_diff": abs(v - p) / p, "equal_1e-9": abs(v - p) <= 1e-9 * p,
                                             "meets_CC9_100": v >= 100}

    def Dof(cls, m):
        return max(est[f"{cls}{m}"]["D_R_ub95"], 1.0) * (1.2 if cls in ("TT", "TB") else 1.5)

    def simulate(nmap, reps, seed_fam, kappa=None, cell=None, mode=None, chunk=200):
        """Returns per-replicate family max z (kappa None), or z of `cell` with a planted excess."""
        rng = np.random.default_rng(np.random.SeedSequence([0x0114FF, seed_fam]))
        fam_max = np.full(reps, -np.inf)
        zc = np.empty(reps)
        for cls, m in CELLS:
            panel = "search" if cls == "SS" else "table"
            D = Dof(cls, m)
            p = 1.0 / D
            for fam, arms in ARMS.items():
                if kappa is not None and not any(cell == f"{a}|{cls}{m}|band" for a in arms):
                    continue
                mu = band_means(cls, m, nmap[(panel, m)], fam)
                r = mu / (D - 1.0)
                rsum, musum = r.sum(), mu.sum()
                for s0 in range(0, reps, chunk):
                    k = min(chunk, reps - s0)
                    R = rng.negative_binomial(np.broadcast_to(r, (k, 3, len(r))), p)
                    CR = R.sum(axis=(1, 2)) / 3.0
                    s2 = R.var(axis=1, ddof=1).sum(axis=1)
                    V = np.maximum(s2, CR)
                    SD = np.sqrt(V * 4.0 / 3.0)
                    for a in arms:
                        CA = rng.negative_binomial(rsum, p, size=k).astype(float)
                        if kappa is not None and cell == f"{a}|{cls}{m}|band":
                            ex = (kappa - 1.0) * musum
                            if mode == "poisson":
                                CA = CA + rng.poisson(ex, size=k)
                            else:
                                CA = CA + rng.negative_binomial(ex / (D - 1.0), p, size=k)
                        z = (CA - CR) / SD
                        if kappa is None:
                            fam_max[s0:s0 + k] = np.maximum(fam_max[s0:s0 + k], z)
                        elif cell == f"{a}|{cls}{m}|band":
                            zc[s0:s0 + k] = z
        return fam_max if kappa is None else zc

    declared = {(p_, int(m)): v["30"] for p_, dd in d["declared_n"].items() for m, v in dd.items()}
    final = {(p_, int(m)): v["30"] for p_, dd in d["final_n"].items() for m, v in dd.items()}
    out_t = {}
    for name, nmap in (("declared_design", declared), ("final_design", final)):
        per = [float(np.quantile(simulate(nmap, 20000, i), 0.95)) for i in range(5)]
        out_t[name] = {"t": float(np.mean(per)), "per_seed_family": per, "spread": max(per) - min(per)}
    res["t_star_plan_own"] = out_t
    res["t_star_plan_design"] = {"declared_design": d["t_star_plan_declared_design"], "final_design": d["t_star_plan"]}
    tdecl = out_t["declared_design"]["t"]
    # raise rule
    target = {"TT": 1.15, "SS": 1.15, "TB": 1.5}
    rule = {}
    for (panel, m) in sorted(declared):
        cells = [(a, cls) for cls, mm in CELLS for fam, arms in ARMS.items() for a in arms
                 if mm == m and (("search" if cls == "SS" else "table") == panel)]
        evals = []
        chosen = None
        for mult in [1.0] + MULTS:
            nmap = dict(declared)
            nmap[(panel, m)] = int(round(declared[(panel, m)] * mult))
            pw = {}
            for a, cls in cells:
                pid = f"{a}|{cls}{m}|band"
                gov = []
                for mode in ("poisson", "compound"):
                    hits = 0
                    for i in range(5):
                        z = simulate(nmap, 4000, 100 + i, kappa=target[cls], cell=pid, mode=mode)
                        hits += int((z > tdecl).sum())
                    gov.append(hits / 20000.0)
                pw[pid] = {"poisson": gov[0], "compound": gov[1], "governing": min(gov)}
            met = all(v["governing"] >= 0.5 for v in pw.values())
            evals.append({"multiplier": mult, "n": nmap[(panel, m)], "power": pw, "all_cells_met": met})
            if met:
                chosen = mult
                break
            if mult == 3.0:
                chosen = "3 x declared; target unattainable by design"
        rule[f"{panel}|{m}"] = {"chosen_multiplier": chosen, "final_n_own": evals[-1]["n"],
                                "final_n_design": final[(panel, m)], "equal": evals[-1]["n"] == final[(panel, m)],
                                "evaluations": evals}
    res["raise_rule_own"] = rule
    json.dump(res, open(sys.argv[2], "w"), indent=1)
    print(json.dumps({"E_C_R_all_equal": all(v["equal_1e-9"] for v in res["E_C_R_uniform"].values()),
                      "E_C_R_max_rel_diff": max(v["rel_diff"] for v in res["E_C_R_uniform"].values()),
                      "t_own": {k: v["t"] for k, v in out_t.items()}, "t_design": {k: v["t"] for k, v in res["t_star_plan_design"].items()},
                      "final_n": {k: [v["final_n_own"], v["final_n_design"], v["chosen_multiplier"]] for k, v in rule.items()}}, indent=1))


if __name__ == "__main__":
    main()
