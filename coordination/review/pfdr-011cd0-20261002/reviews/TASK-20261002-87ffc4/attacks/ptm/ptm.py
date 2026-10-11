"""Proves-too-much control (plan PTM-1, PTM-2, PTM-3) and the per-rung multiplicity check (J6),
with this reviewer's own code. Choices fixed in attacks/j4/00-readings-before-computing.yaml
(R-PTM1) and here, before computing:

PTM-1  each random r_k of a family scored as "structured" against the other two randoms plus the
       family's known-null arm as the third random (CC-8 unchanged, df 3), every FAM-1 (class, m),
       30-32 band: 2 families x 7 (class, m) x 3 = 42 pseudo-cells. Observed z against t*
       (producer's and own) and against the simulated law of the same construction (generator;
       seed SeedSequence([0x87ffc4, 50, f])).
PTM-2  (a) synthetic null counts from this reviewer's generator through CC-8 and t*: the family-
       wise excursion rate (from attacks/j4 null tables) and the A-INT one-sided coverage at
       kappa = 1 (attacks/j4/out/aint.json). (b) A REAL-DATA null that does not assume the NB
       shape: per (family, class, m) the four null arms on each curve (r0, r1, r2, known-null) are
       exchangeable under the null; each replicate picks one arm per curve uniformly as "A" and
       scores CC-8 against the other three. 4000 replicates, seed SeedSequence([0x87ffc4, 51]).
       Reported: the 0.95 quantile of the max over the 14 (family, class, m) cells, compared with
       the generator's 14-cell max quantile; per-cell P(z > t*).
PTM-3  planted augmentation at kappa_true in {1.02, 1.05, 1.10, 1.15, 1.25, 1.50} (and the full
       X grid), Poisson-, compound- (NB with the group's D) and clustered (3 per event)-planted:
       (A) conditional: the structured arm's OBSERVED counts plus the planted excess
           (mean (kappa_true - 1) * nbar_j per curve), observed randoms unchanged -- the plan's
           literal object; 2000 augmentation draws per kappa, seed SeedSequence([0x87ffc4, 52]).
       (C) real-noise unconditional: the PTM-2(b) real-data null replicate as base plus the
           planted excess (mean (kappa - 1) m_j), 4000 replicates, seed SeedSequence([0x87ffc4, 53]);
           X_C = smallest grid kappa with P(z > t*) >= 0.5, compared with the producer's X_rel.
Per-rung (J6): the number of FAM-1 per-rung cells and known-null per-rung cells with |z| > t*
       against the generator's joint law (subgroup/small_x sharing randoms), 4000 x 5 replicates,
       seed SeedSequence([0x87ffc4, 54, f]).
Command: nice -n 19 $PY attacks/ptm/ptm.py --out attacks/ptm/out/ptm.json --tstar-own <t>
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "j4"))
import j4lib as L  # noqa: E402

T_PROD = 2.848862284470068
XREL_PROD = {"TT3": 1.02, "TT4": 1.11, "TT5": 1.05, "SS3": 1.03, "SS4": 1.03, "SS5": 1.05, "TB3": 1.27}
KTRUE = (1.02, 1.05, 1.10, 1.15, 1.25, 1.50)


def null_arm_matrix(rows, groups, fam, cls, m, b):
    g = groups[(fam, cls, m, b)]
    arms = L.RANDOMS[fam] + (L.KNOWN_NULL[fam],)
    return np.stack([L.arm_counts(rows, g, a, cls, m, b) for a in arms], axis=1), g  # (n, 4)


def perm_scores(X, choice):
    """X (n, 4) counts; choice (reps, n) index of the 'A' arm -> (CA, CR, Q) per replicate."""
    S = X.sum(axis=1)
    S2 = (X * X).sum(axis=1)
    A = np.take_along_axis(np.broadcast_to(X, (choice.shape[0],) + X.shape), choice[..., None], axis=2)[..., 0]
    mean = (S - A) / 3.0
    var = ((S2 - A * A) - 3.0 * mean * mean) / 2.0
    return A.sum(axis=1), mean.sum(axis=1), var.sum(axis=1), A


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tstar-own", type=float, required=True)
    ap.add_argument("--npz", required=True)
    a = ap.parse_args()
    t0 = time.time()
    design = L.load_design()
    rows = L.load_extract()
    groups, rho1, _ = L.build_groups(rows, design, rho1_mode="per_family")
    nz = np.load(a.npz)
    res = {"task": "TASK-20261002-87ffc4", "control": "proves_too_much", "t_star_producer": T_PROD,
           "t_star_own": a.tstar_own}
    # ---------------- PTM-1
    p1 = []
    for fam in ("SUB", "DICK"):
        for (cls, m) in L.FAM1_CM:
            for k in range(3):
                arm = L.RANDOMS[fam][k]
                others = [x for x in L.RANDOMS[fam] if x != arm] + [L.KNOWN_NULL[fam]]
                o = L.observed_cell(rows, groups, arm, cls, m, L.BAND, fam=fam, randoms_override=others)
                p1.append({"fam": fam, "cell": f"{cls}{m}", "pseudo_structured": arm, "z": o["z"],
                           "kappa_rel": o["kappa_rel"]})
    zs = np.array([x["z"] for x in p1])
    # null law of a PTM-1 pseudo-cell = the law of a known-null band cell of the same (fam, cls, m)
    ref = []
    p_cell = []
    for x in p1:
        kn = L.KNOWN_NULL[x["fam"]]
        cls, m = x["cell"][:2], int(x["cell"][2])
        zn = nz[f"z|{kn}|{cls}|{m}"]
        ref.append(zn)
        p_cell.append(float(np.mean(zn > T_PROD)))
    refall = np.sort(np.concatenate(ref))
    D = L.ks_D_against(zs, refall)
    res["PTM1"] = {"pseudo_cells": len(p1), "excursions_z_gt_t_prod": int(np.sum(zs > T_PROD)),
                   "excursions_z_gt_t_own": int(np.sum(zs > a.tstar_own)),
                   "deficits_z_lt_minus_t_prod": int(np.sum(zs < -T_PROD)),
                   "expected_excursions_under_generator": float(np.sum(p_cell)),
                   "P_at_least_one_under_generator_independent_approx": float(1 - np.prod(1 - np.array(p_cell))),
                   "z_max": float(zs.max()), "z_min": float(zs.min()), "z_mean": float(zs.mean()),
                   "z_sd": float(zs.std(ddof=1)),
                   "ks_D_vs_generator": D, "ks_p_asymptotic": L.kolmogorov_sf(D, len(zs)),
                   "ks_note": "the 42 pseudo-cells share arms (three per family-(class, m)); the asymptotic p "
                              "assumes independence and is approximate",
                   "cells": p1}
    print("PTM1", {k: v for k, v in res["PTM1"].items() if k != "cells"}, flush=True)
    # ---------------- PTM-2 (a): generator FW rate with the producer's t* (own null tables)
    fz = nz["famzmax"]
    res["PTM2a"] = {"generator_replicates": int(len(fz)),
                    "FW_excursion_rate_at_t_prod": float(np.mean(fz > T_PROD)),
                    "FW_excursion_rate_at_t_own": float(np.mean(fz > a.tstar_own)),
                    "note": "A-INT one-sided coverage at kappa = 1 is in attacks/j4/out/aint.json (coverage)"}
    # ---------------- PTM-2 (b) + PTM-3 (C): real-data permutation null
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 51]))
    rngC = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 53]))
    REPS = 4000
    perm_max = np.full(REPS, -np.inf)
    gen14 = np.max(np.vstack([nz[f"z|{arm}|{cls}|{m}"] for (cls, m) in L.FAM1_CM for arm in ("subgroup", "dickson")]), axis=0)
    p2b = {}
    p3c = {}
    for fam in ("SUB", "DICK"):
        for (cls, m) in L.FAM1_CM:
            CA = np.zeros(REPS)
            CR = np.zeros(REPS)
            Q = np.zeros(REPS)
            Mmean = 0.0
            parts = []
            for b in L.BAND:
                X, g = null_arm_matrix(rows, groups, fam, cls, m, b)
                ch = rng.integers(0, 4, size=(REPS, X.shape[0]))
                ca, cr, q, _A = perm_scores(X, ch)
                CA += ca
                CR += cr
                Q += q
                Mmean += g.M
                parts.append(g)
            z = L.zvec(CA, CR, Q)
            perm_max = np.maximum(perm_max, z)
            key = f"{fam}|{cls}{m}"
            gen_z = nz[f"z|{L.KNOWN_NULL[fam]}|{cls}|{m}"]
            p2b[key] = {"P_z_gt_t_prod_perm": float(np.mean(z > T_PROD)),
                        "P_z_gt_t_prod_generator": float(np.mean(gen_z > T_PROD)),
                        "sd_z_perm": float(np.std(z)), "sd_z_generator": float(np.std(gen_z)),
                        "q99_perm": float(np.quantile(z, 0.99)), "q99_generator": float(np.quantile(gen_z, 0.99))}
            # PTM-3 (C): real-noise power on the grid (Poisson excess, mean (kappa - 1) M)
            pw = []
            for kap in L.GRID:
                ex = sum(rngC.poisson((kap - 1.0) * g.M, size=REPS) for g in parts) if kap > 1 else 0
                pw.append(float(np.mean(L.zvec(CA + ex, CR, Q) > T_PROD)))
            hit = [k for k, p in zip(L.GRID, pw) if p >= 0.5]
            xc = hit[0] if hit else None
            p3c[key] = {"X_C_real_noise": xc, "X_rel_producer": XREL_PROD[f"{cls}{m}"],
                        "power_at_producer_X_rel": pw[L.GRID.index(XREL_PROD[f"{cls}{m}"])],
                        "power_at_kappa_true": {str(k): pw[L.GRID.index(round(k, 2))] for k in KTRUE}}
    res["PTM2b_permutation_null"] = {
        "replicates": REPS, "cells": p2b,
        "max14_q95_perm": float(np.quantile(perm_max, 0.95)),
        "max14_q95_generator": float(np.quantile(gen14, 0.95)),
        "FW14_rate_at_t_prod_perm": float(np.mean(perm_max > T_PROD)),
        "FW14_rate_at_t_prod_generator": float(np.mean(gen14 > T_PROD)),
        "note": "14 cells = one per (family, class, m); the generator column is the same 14-cell maximum "
                "(subgroup and dickson cells) from this reviewer's G-NB-R tables"}
    res["PTM3_C_real_noise"] = p3c
    print("PTM2b", {k: v for k, v in res["PTM2b_permutation_null"].items() if k != "cells"}, flush=True)
    # ---------------- PTM-3 (A): conditional augmentation of the observed structured arm
    rngA = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 52]))
    p3a = {}
    NA = 2000
    for (cls, m) in L.FAM1_CM:
        for arm in L.FAM1_ARMS:
            fam = L.FAM_OF[arm]
            o = L.observed_cell(rows, groups, arm, cls, m, L.BAND)
            ent = {"z_obs": o["z"], "X_rel_producer": XREL_PROD[f"{cls}{m}"]}
            for kind in ("poisson", "compound", "clustered3"):
                pw = []
                for kap in L.GRID:
                    if kap == 1.0:
                        pw.append(float(o["z"] > T_PROD))
                        continue
                    CA = np.full(NA, o["C_A"])
                    for (b, A, R) in o["per_curve"]:
                        nb = R.mean(axis=1)
                        mu = (kap - 1.0) * nb.sum()
                        g = groups[(fam, cls, m, b)]
                        if kind == "poisson" or (kind == "compound" and g.D <= 1):
                            CA = CA + rngA.poisson(mu, size=NA)
                        elif kind == "compound":
                            CA = CA + rngA.negative_binomial(mu / (g.D - 1), 1 / g.D, size=NA)
                        else:
                            CA = CA + 3 * rngA.poisson(mu / 3, size=NA)
                    pw.append(float(np.mean(L.zvec(CA, np.full(NA, o["C_R"]), np.full(NA, o["sum_s2"])) > T_PROD)))
                hit = [k for k, p in zip(L.GRID, pw) if p >= 0.5]
                ent[f"X_cond_{kind}"] = hit[0] if hit else None
                ent[f"detect_at_kappa_true_{kind}"] = {str(k): pw[L.GRID.index(round(k, 2))] for k in KTRUE}
                ent[f"detect_at_producer_X_rel_{kind}"] = pw[L.GRID.index(XREL_PROD[f"{cls}{m}"])]
            if (cls, m) == ("SS", 4):
                ent["label"] = L.TA1_LABEL
            p3a[f"{arm}|{cls}{m}|band"] = ent
    res["PTM3_A_conditional"] = p3a
    print("PTM3A done", round(time.time() - t0), flush=True)
    # ---------------- per-rung |z| > t* multiplicity (J6)
    obs_f = sum(1 for (cls, m) in L.FAM1_CM for arm in L.FAM1_ARMS for b in L.RUNGS
                if abs(L.observed_cell(rows, groups, arm, cls, m, (b,))["z"]) > T_PROD)
    obs_k = sum(1 for (cls, m) in L.FAM1_CM for fam in ("SUB", "DICK") for b in L.RUNGS
                if abs(L.observed_cell(rows, groups, L.KNOWN_NULL[fam], cls, m, (b,))["z"]) > T_PROD)
    cnt_f, cnt_k = [], []
    for f in range(5):
        rg = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 54, f]))
        cf = np.zeros(4000, dtype=int)
        ck = np.zeros(4000, dtype=int)
        for (cls, m) in L.FAM1_CM:
            for fam in ("SUB", "DICK"):
                for b in L.RUNGS:
                    g = groups[(fam, cls, m, b)]
                    na = 3 if fam == "SUB" else 2
                    CR, Q, A = L.sim_group(rg, g, 4000, n_arms=na)
                    for j in range(na):
                        z = L.zvec(A[:, j], CR, Q)
                        if j == na - 1:
                            ck += np.abs(z) > T_PROD
                        else:
                            cf += np.abs(z) > T_PROD
        cnt_f.append(cf)
        cnt_k.append(ck)
    cnt_f = np.concatenate(cnt_f)
    cnt_k = np.concatenate(cnt_k)
    res["per_rung_multiplicity"] = {
        "FAM1_per_rung_cells": 147, "observed_abs_z_gt_t": obs_f, "expected_under_generator": float(cnt_f.mean()),
        "P_count_ge_observed": float(np.mean(cnt_f >= obs_f)),
        "known_null_per_rung_cells": 98, "observed_kn_abs_z_gt_t": obs_k,
        "expected_kn_under_generator": float(cnt_k.mean()), "P_kn_count_ge_observed": float(np.mean(cnt_k >= obs_k)),
        "P_combined_count_ge_observed": float(np.mean(cnt_f + cnt_k >= obs_f + obs_k))}
    print("per-rung", res["per_rung_multiplicity"], flush=True)
    res["seconds"] = time.time() - t0
    L.jdump(a.out, res)


if __name__ == "__main__":
    main()
