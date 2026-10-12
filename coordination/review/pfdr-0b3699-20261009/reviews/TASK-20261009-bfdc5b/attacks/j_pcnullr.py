"""J-PCNULLR: PC-NULL-R recomputed, degeneracy of criterion (i), and the common-mode attack.
TASK-20261009-bfdc5b.
Seeds: departure simulations SeedSequence([0xBFDC5B, 13, scenario_index]), 20000 replicates
each (a declared smaller count than the frozen 5 x 20000; Monte Carlo SE reported).
Uses pc_z_bank.npy (j_cal.py, 5 x 20000, SeedSequence([0xBFDC5B, 1, f])) for the joint law.
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
t_dec = cal["t_dec"]
d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
obs = [d[f"cnt_{a}"] for a in C.NULLS]


def pc_cells(x4):
    """x4: list of 4 per-curve arrays (r0, r1, r2, kn). Returns 4 pseudo-cell cc8 dicts."""
    out = []
    for i in range(4):
        others = [x4[j] for j in range(4) if j != i]
        out.append(C.cc8(x4[i], *others))
    return out


cells = pc_cells(obs)
z_obs = np.array([c["z"] for c in cells])
K = int((z_obs > t_dec).sum())
bank = np.load(f"{C.SCR}/pc_z_bank.npy")
Kb = (bank > t_dec).sum(axis=1)
mean_b = bank.mean(axis=1)
pK = float((Kb >= K).mean())
lo, hi = np.quantile(mean_b, [0.005, 0.995])
Kdist = np.bincount(Kb, minlength=5) / len(Kb)
# smallest K at which (i) fails
k_fail = next((k for k in range(5) if (Kb >= k).mean() < 0.01), None)
per_rung = {}
for b in C.RUNGS:
    s = d["bits"] == b
    per_rung[b] = [c["z"] for c in pc_cells([x[s] for x in obs])]
obs_block = {"z_null_pseudo_cells": dict(zip(["r0_vs_r1r2kn", "r1_vs_r0r2kn", "r2_vs_r0r1kn", "kn_vs_r0r1r2"], z_obs.tolist())),
             "kappa_null_pseudo_cells": [c["kappa_rel"] for c in cells], "K": K, "P_Knull_ge_K": pK,
             "P_Knull_ge_K_mc_se": float(np.sqrt(pK * (1 - pK) / len(Kb))),
             "criterion_i_pass": pK >= 0.01, "mean_z": float(z_obs.mean()), "mean_z_sim99": [float(lo), float(hi)],
             "criterion_ii_pass": bool(lo <= z_obs.mean() <= hi), "K_null_distribution": Kdist.tolist(),
             "K_at_which_i_fails": k_fail, "replicates": len(Kb), "per_rung_z": {str(b): v for b, v in per_rung.items()}}

# ---------------------------------------------------------- degeneracy of (i)
REPS = 20000
scen = [("null", None, 1.0), ("kn_1.10", [3], 1.10), ("kn_1.15", [3], 1.15), ("r0_1.10", [0], 1.10),
        ("r0_1.15", [0], 1.15), ("r0+kn_1.15 (two-arm, extra)", [0, 3], 1.15),
        ("r0_overdispersed_D2 (extra)", "od0", 2.0)]
deg = {}
for si, (name, arms, kap) in enumerate(scen):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 13, si]))
    zs = []
    done = 0
    while done < REPS:
        k = min(400, REPS - done)
        x = model.draw_curves(rng, k, 4).astype(np.float64)
        if isinstance(arms, list):
            for a in arms:
                x[:, a, :] += rng.poisson((kap - 1) * model.m, size=(k, model.ncurves))
        elif arms == "od0":
            # r0 replaced by an arm with dispersion 2 x D (same mean)
            for b in C.RUNGS:
                s = model.bits == b
                Dd = model.rung_D[b] * kap
                x[:, 0, s] = rng.negative_binomial(model.m[s] / (Dd - 1), 1 / Dd, size=(k, s.sum()))
        T = x.sum(axis=1)
        Q = (x * x).sum(axis=1)
        tot = x.sum(axis=2)
        z4 = np.empty((k, 4))
        for i in range(4):
            Ti = T - x[:, i, :]
            Qi = Q - x[:, i, :] ** 2
            CR = Ti.sum(axis=1) / 3
            V = np.maximum(((Qi - Ti * Ti / 3) / 2).sum(axis=1), CR)
            z4[:, i] = (tot[:, i] - CR) / np.sqrt(4 * V / 3)
        zs.append(z4)
        done += k
    zs = np.concatenate(zs)
    Ks = (zs > t_dec).sum(axis=1)
    f_i = float((Ks >= k_fail).mean()) if k_fail is not None else 0.0
    mz = zs.mean(axis=1)
    f_ii = float(((mz < lo) | (mz > hi)).mean())
    f_any = float(((Ks >= (k_fail if k_fail is not None else 99)) | (mz < lo) | (mz > hi)).mean())
    deg[name] = {"fail_i": f_i, "fail_i_mc_se": float(np.sqrt(max(f_i * (1 - f_i), 1 / REPS) / REPS)),
                 "fail_ii": f_ii, "fail_ii_mc_se": float(np.sqrt(f_ii * (1 - f_ii) / REPS)),
                 "fail_either": f_any, "K_distribution": (np.bincount(Ks, minlength=5) / REPS).tolist(),
                 "replicates": REPS}
    print(name, deg[name], flush=True)

# ---------------------------------------------------------------- common mode
ref_rate = {30: 521.3333333333334 / 2000, 32: 513.6666666666666 / 2000}  # spec mu_30, mu_32
ref_sum_mu = {30: 505.4262270960486, 32: 508.59252619230404}  # design.json inputs_read (011cd0 curves)
ref_rho1_p0 = {30: 1.0229146601280728, 32: 1.00430380038165}  # design.json rho1_hat_b (P0, sum_mj)
R = np.vstack(obs[:3]).astype(float)
cm = {}
for b in C.RUNGS + ("pooled",):
    s = np.ones(len(d["bits"]), bool) if b == "pooled" else d["bits"] == b
    n = int(s.sum())
    CR = R[:, s].sum() / 3
    rate = CR / n
    D = fit[30]["D"] if b == 30 else (fit[32]["D"] if b == 32 else max(fit[30]["D"], fit[32]["D"]))
    if b == "pooled":
        refCR = ref_rate[30] * 2000 + ref_rate[32] * 2000
        ref_n = 4000
        ref_mu = ref_sum_mu[30] + ref_sum_mu[32]
    else:
        refCR = ref_rate[b] * 2000
        ref_n = 2000
        ref_mu = ref_sum_mu[b]
    # (a) raw rate ratio; log-scale SE from count noise (Var C_R = D C_R / 3 each side) plus curve-mix
    mu_here = d["mu_model"][s]
    cv2_mix_here = mu_here.var(ddof=1) / n / mu_here.mean() ** 2
    cv2_mix_ref = mu_here.var(ddof=1) / ref_n / mu_here.mean() ** 2  # same generator assumed
    se_raw = np.sqrt(D / (3 * CR) + D / (3 * refCR) + cv2_mix_here + cv2_mix_ref)
    f_raw = rate / (refCR / ref_n)
    # (b) mu_model-normalised ratio (no curve-mix term)
    rho_here = CR / mu_here.sum()
    rho_ref = refCR / ref_mu
    se_norm = np.sqrt(D / (3 * CR) + D / (3 * refCR))
    f_norm = rho_here / rho_ref
    cm[str(b)] = {"curves": n, "C_R": CR, "rate_here": rate, "rate_ref_011cd0": refCR / ref_n,
                  "f_raw": f_raw, "f_raw_99": [f_raw * np.exp(-2.5758 * se_raw), f_raw * np.exp(2.5758 * se_raw)],
                  "rho1_here": rho_here, "rho1_ref_localise": rho_ref,
                  "f_norm": f_norm, "f_norm_99": [f_norm * np.exp(-2.5758 * se_norm), f_norm * np.exp(2.5758 * se_norm)],
                  "f_vs_P0_rho1": rho_here / (ref_rho1_p0[b] if b != "pooled" else
                                              (ref_rho1_p0[30] * ref_sum_mu[30] + ref_rho1_p0[32] * ref_sum_mu[32]) / ref_mu)}

# propagate to small_x: null arms off by common factor f relative to the true null (f = here/true)
A = d["cnt_small_x"]
obsA = C.cc8(A, *obs[:3])
import os
GRID = np.round(np.arange(0.80, 1.40 + 1e-9, 0.0025), 6)
QLO = np.load(f"{C.SCR}/grid_qlo_A.npy") if os.path.exists(f"{C.SCR}/grid_qlo_A.npy") else None
lo_f = min(cm["pooled"]["f_norm_99"][0], cm["pooled"]["f_raw_99"][0], cm["30"]["f_norm_99"][0])
hi_f = max(cm["pooled"]["f_norm_99"][1], cm["pooled"]["f_raw_99"][1], cm["32"]["f_norm_99"][1])


def propagate(f):
    CRt = obsA["C_R"] / f
    Vt = obsA["V"] / f
    SD = np.sqrt(4 * Vt / 3)
    kap = obsA["C_A"] / CRt
    z = (obsA["C_A"] - CRt) / SD
    SE = SD / CRt
    out = {"f": f, "kappa_rel": kap, "z_A": z, "SE": SE, "U_signed_approx_qlo_-1.645": kap + 1.645 * SE}
    if QLO is not None:
        out["U_signed_grid"] = kap - float(np.interp(kap, GRID, QLO)) * SE
    return out


# the f that would carry small_x to z = t_dec and to U = 1.15 (same convention)
f_z = None
for f in np.arange(1.0, 1.3, 0.0005):
    if propagate(f)["z_A"] > t_dec:
        f_z = float(f)
        break
f_U = None
for f in np.arange(1.0, 1.3, 0.0005):
    pr = propagate(f)
    if pr.get("U_signed_grid", pr["U_signed_approx_qlo_-1.645"]) > 1.15:
        f_U = float(f)
        break
prop = {"convention": "f = (null-arm rate here) / (true null rate); small_x true null = C_R / f",
        "admitted_f_interval_99_widest": [lo_f, hi_f],
        "at_lower_end": propagate(lo_f), "at_upper_end": propagate(hi_f),
        "reverse_convention_note": "if f is read as reference/here, the ends map to 1/f",
        "at_1_over_lower_end": propagate(1 / lo_f), "at_1_over_upper_end": propagate(1 / hi_f),
        "f_needed_for_z_gt_t_dec": f_z, "f_needed_for_U_gt_1.15": f_U}

res = {"task": "TASK-20261009-bfdc5b", "joint": "J-PCNULLR", "t_dec": t_dec, "observed": obs_block,
       "degeneracy": deg, "common_mode": cm, "propagation": prop}
C.jdump(res, OUT)
print(json.dumps({"observed": obs_block, "common_mode": cm, "propagation": prop}, indent=1, default=str))
