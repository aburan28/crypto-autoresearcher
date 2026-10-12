"""J4 (a), (b): this reviewer's G-NB-R, t*, t_carry, calibrated p, PC-NULL (i) and (ii).

Declared before computing (attacks/j4/00-readings-before-computing.yaml):
  * rho1 per family (primary) and pooled over families (I-10) -- both run.
  * 5 seed families of MY OWN seeds: SeedSequence([0x87ffc4, 10 + variant, f]), f = 0..4,
    variant 0 = per-family rho1, 1 = pooled rho1; 20000 replicates per family.
  * per-rung known-null simulation for PC-NULL (ii): SeedSequence([0x87ffc4, 20, f]),
    4000 replicates per family; KS of the 98 observed per-rung known-null z against the pooled
    simulated null, with (a) the asymptotic Kolmogorov p (Stephens) and (b) a Monte-Carlo p
    from the joint per-replicate D distribution (keeps the within-family sharing and the
    discreteness).
Command: nice -n 19 $PY attacks/j4/j4_tstar.py --out attacks/j4/out/tstar.json --npz <scratch>/null-z.npz
"""
import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import j4lib as L  # noqa: E402

PRODUCER = {"t_star": 2.848862284470068, "t_carry": 2.306890430176141,
            "t_star_per_family": [2.8489978633710096, 2.8417213419693357, 2.8636491595038343,
                                  2.8442529590300807, 2.8456900984760787],
            "t_carry_per_family": [2.273863057526598, 2.3633875401039095, 2.3426605628041166,
                                   2.2558263296519834, 2.2987146607940976]}


def fam1_cell_list():
    cells = []
    for (cls, m) in L.FAM1_CM:
        for arm in L.FAM1_ARMS:
            cells.append((arm, cls, m))
    return cells


def kn_cell_list():
    return [(L.KNOWN_NULL[f], cls, m) for (cls, m) in L.FAM1_CM for f in ("SUB", "DICK")]


def band_sim(groups, seed_tag, f, reps, batch=500):
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, seed_tag, f]))
    fam_arms = {"SUB": ["subgroup", "small_x", "known_null_sub"], "DICK": ["dickson", "known_null_dick"]}
    cells = fam1_cell_list()
    kcells = kn_cell_list()
    Z = {c: [] for c in cells}
    K = {c: [] for c in kcells}
    Zc = []
    for st in range(0, reps, batch):
        B = min(batch, reps - st)
        acc = {}
        for (cls, m) in L.FAM1_CM:
            for fam in ("SUB", "DICK"):
                for b in L.BAND:
                    g = groups[(fam, cls, m, b)]
                    CR, Q, A = L.sim_group(rng, g, B, n_arms=len(fam_arms[fam]))
                    acc[(fam, cls, m, b)] = (CR, Q, A)
        gC = groups[("SUB", "TT", 3, 28)]
        CRc, Qc, Ac = L.sim_group(rng, gC, B, n_arms=1)
        Zc.append(L.zvec(Ac[:, 0], CRc, Qc))
        for (arm, cls, m) in cells + kcells:
            fam = L.FAM_OF[arm]
            j = fam_arms[fam].index(arm)
            CA = sum(acc[(fam, cls, m, b)][2][:, j] for b in L.BAND)
            CR = sum(acc[(fam, cls, m, b)][0] for b in L.BAND)
            Q = sum(acc[(fam, cls, m, b)][1] for b in L.BAND)
            z = L.zvec(CA, CR, Q)
            (Z if (arm, cls, m) in Z else K)[(arm, cls, m)].append(z)
    Z = {c: np.concatenate(v) for c, v in Z.items()}
    K = {c: np.concatenate(v) for c, v in K.items()}
    return Z, K, np.concatenate(Zc)


def rung_sim(groups, f, reps, batch=500):
    """Per-rung known-null z for the 98 per-rung pseudo-cells (2 families x 7 (class, m) x 7 rungs)."""
    rng = np.random.default_rng(np.random.SeedSequence([0x87FFC4, 20, f]))
    keys = [(fam, cls, m, b) for (cls, m) in L.FAM1_CM for fam in ("SUB", "DICK") for b in L.RUNGS]
    out = {k: [] for k in keys}
    for st in range(0, reps, batch):
        B = min(batch, reps - st)
        for k in keys:
            CR, Q, A = L.sim_group(rng, groups[k], B, n_arms=1)
            out[k].append(L.zvec(A[:, 0], CR, Q))
    return {k: np.concatenate(v) for k, v in out.items()}, keys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--npz", required=True)
    ap.add_argument("--reps", type=int, default=20000)
    ap.add_argument("--rung-reps", type=int, default=4000)
    a = ap.parse_args()
    t0 = time.time()
    design = L.load_design()
    rows = L.load_extract()
    res = {"task": "TASK-20261002-87ffc4", "joint": "J4", "reps_per_family": a.reps, "producer": PRODUCER}
    obs = {}
    variants = {}
    arrays = {}
    for vi, mode in enumerate(("per_family", "pooled")):
        groups, rho1, drops = L.build_groups(rows, design, rho1_mode=mode)
        if vi == 0:
            res["cc6_drops"] = drops
            res["groups_band"] = {"|".join(map(str, k)): {"n": len(g.curves), "D_hat": g.D_hat, "D": g.D,
                                                         "rho1": g.extra["rho1"], "M": g.M}
                                  for k, g in groups.items() if k[3] in (28, 30, 32)}
            # observed cells
            for (arm, cls, m) in fam1_cell_list() + kn_cell_list():
                o = L.observed_cell(rows, groups, arm, cls, m, L.BAND)
                obs[(arm, cls, m)] = {k: v for k, v in o.items() if k != "per_curve"}
            oc = L.observed_cell(rows, groups, "subgroup", "TT", 3, (28,))
            obs[("CARRY",)] = {k: v for k, v in oc.items() if k != "per_curve"}
            res["observed"] = {"|".join(map(str, k)): v for k, v in obs.items()}
        fams = []
        Zall = {}
        Kall = {}
        Call = []
        for f in range(5):
            Z, K, Zc = band_sim(groups, 10 + vi, f, a.reps)
            mx = np.max(np.vstack([Z[c] for c in fam1_cell_list()]), axis=0)
            fams.append({"t_star": float(np.quantile(mx, 0.95)), "t_carry": float(np.quantile(Zc, 0.99)),
                         "max14_q95": float(np.quantile(np.max(np.vstack([Z[c] for c in fam1_cell_list()
                                                                           if c[0] != "small_x"]), axis=0), 0.95))})
            for c in Z:
                Zall.setdefault(c, []).append(Z[c])
            for c in K:
                Kall.setdefault(c, []).append(K[c])
            Call.append(Zc)
            print(mode, f, fams[-1], round(time.time() - t0), flush=True)
        ts = float(np.mean([x["t_star"] for x in fams]))
        tc = float(np.mean([x["t_carry"] for x in fams]))
        Zall = {c: np.concatenate(v) for c, v in Zall.items()}
        Kall = {c: np.concatenate(v) for c, v in Kall.items()}
        Call = np.concatenate(Call)
        v = {"t_star": ts, "t_star_per_family": [x["t_star"] for x in fams],
             "t_star_spread": max(x["t_star"] for x in fams) - min(x["t_star"] for x in fams),
             "t_carry": tc, "t_carry_per_family": [x["t_carry"] for x in fams],
             "t_carry_spread": max(x["t_carry"] for x in fams) - min(x["t_carry"] for x in fams),
             "delta_t_star_vs_producer": ts - PRODUCER["t_star"],
             "delta_t_carry_vs_producer": tc - PRODUCER["t_carry"]}
        # calibrated p per FAM-1 cell, family max p, CARRY p
        mxall = np.max(np.vstack([Zall[c] for c in fam1_cell_list()]), axis=0)
        v["calibrated_p_fam1_band"] = {"|".join(map(str, c)): float(np.mean(Zall[c] >= obs[c]["z"]))
                                       for c in fam1_cell_list()}
        zmax_obs = max(obs[c]["z"] for c in fam1_cell_list())
        v["family_max_z_obs"] = zmax_obs
        v["p_family_max"] = float(np.mean(mxall >= zmax_obs))
        v["carry_p"] = float(np.mean(Call >= obs[("CARRY",)]["z"]))
        for tlabel, tval in (("own", ts), ("producer", PRODUCER["t_star"])):
            K_obs = sum(1 for c in kn_cell_list() if obs[c]["z"] > tval)
            Knull = np.sum(np.vstack([Kall[c] for c in kn_cell_list()]) > tval, axis=0)
            v[f"PC_NULL_i_{tlabel}_t"] = {"K_obs": K_obs, "K_null_mean": float(Knull.mean()),
                                          "P_K_null_ge_K_obs": float(np.mean(Knull >= K_obs)),
                                          "P_K_null_ge_1": float(np.mean(Knull >= 1)),
                                          "P_K_null_ge_2": float(np.mean(Knull >= 2)),
                                          "pass": float(np.mean(Knull >= K_obs)) >= 0.01}
            v[f"fam1_cells_z_gt_t_{tlabel}"] = [ "|".join(map(str, c)) for c in fam1_cell_list() if obs[c]["z"] > tval]
            v[f"carry_z_gt_t_carry_{tlabel}"] = obs[("CARRY",)]["z"] > (tc if tlabel == "own" else PRODUCER["t_carry"])
        variants[mode] = v
        if vi == 0:
            arrays.update({"famzmax": mxall.astype(np.float32), "carry": Call.astype(np.float32)})
            for c in fam1_cell_list() + kn_cell_list():
                arrays["z|" + "|".join(map(str, c))] = (Zall[c] if c in Zall else Kall[c]).astype(np.float32)
            # PC-NULL (ii): per-rung
            obs_r = {}
            for (cls, m) in L.FAM1_CM:
                for fam in ("SUB", "DICK"):
                    for b in L.RUNGS:
                        o = L.observed_cell(rows, groups, L.KNOWN_NULL[fam], cls, m, (b,))
                        obs_r[(fam, cls, m, b)] = o["z"]
            sims = {}
            keys = None
            for f in range(5):
                s, keys = rung_sim(groups, f, a.rung_reps)
                for k in keys:
                    sims.setdefault(k, []).append(s[k])
            sims = {k: np.concatenate(v_) for k, v_ in sims.items()}
            ref = np.sort(np.concatenate([sims[k] for k in keys]))
            zobs = np.array([obs_r[k] for k in keys])
            D_obs = L.ks_D_against(zobs, ref)
            # Monte-Carlo D distribution: replicate r gives one 98-vector
            R = len(sims[keys[0]])
            idx = np.arange(0, R, max(1, R // 4000))
            Ds = np.array([L.ks_D_against(np.array([sims[k][i] for k in keys]), ref) for i in idx])
            n_inf_obs = int(np.sum(~np.isfinite(zobs)))
            n_inf_ref = int(np.sum(~np.isfinite(ref)))
            res["PC_NULL_ii"] = {
                "n_cells": len(keys), "D_obs": D_obs, "p_asymptotic_stephens": L.kolmogorov_sf(D_obs, len(keys)),
                "p_monte_carlo": float(np.mean(Ds >= D_obs)), "mc_replicates": int(len(Ds)),
                "mc_D_q99": float(np.quantile(Ds, 0.99)),
                "asymptotic_p_at_mc_D_q99": L.kolmogorov_sf(float(np.quantile(Ds, 0.99)), len(keys)),
                "nonfinite_obs_z": n_inf_obs, "nonfinite_ref_z": n_inf_ref,
                "ref_size": int(len(ref)),
                "obs_z_min": float(np.min(zobs)), "obs_z_max": float(np.max(zobs)),
                "obs_abs_z_gt_t_star": [("|".join(map(str, k)), float(obs_r[k])) for k in keys
                                        if abs(obs_r[k]) > PRODUCER["t_star"]],
                "obs_z": {"|".join(map(str, k)): float(obs_r[k]) for k in keys}}
            print("PC_NULL_ii", {k: v_ for k, v_ in res["PC_NULL_ii"].items() if k != "obs_z"}, flush=True)
            for k in keys:
                arrays["rung|" + "|".join(map(str, k))] = sims[k].astype(np.float32)
    res["variants"] = variants
    res["seconds"] = time.time() - t0
    np.savez_compressed(a.npz, **arrays)
    L.jdump(a.out, res)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if not isinstance(vv, dict)} for k, v in variants.items()}, indent=1, default=str))


if __name__ == "__main__":
    main()
