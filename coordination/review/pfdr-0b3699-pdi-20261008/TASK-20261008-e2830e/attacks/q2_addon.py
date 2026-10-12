"""TASK-20261008-e2830e Q2 add-on (synthetic only; reads no data file).

Two checks beyond the card's D1-D3, using the machinery of q2_pcnullr_sim.py:

1. Departure placed in a RANDOM arm (r0), with the calibration RA-05 would actually compute:
   rho1_hat_b and D_b are estimated from r0..r2 (specification analysis.calibration_G-NB-R), so
   an excess kappa in r0 raises every calibrated mean by the factor 1 + (kappa - 1)/3, and an
   over-dispersed r0 raises D to about (1.3 + 2 D_b)/3. The calibrated joint law is recomputed
   at those expected values ("recal").
     D1_r0_kappa1.10_recal, D1_r0_kappa1.15_recal, D2_r0_dispersion1.3_recal
2. Exchangeable null with a curve-level random effect (N1): all four null arms on curve j have
   mean m_j g_j, g_j ~ Gamma(mean 1, CV c) drawn per curve and replicate. The arms stay
   exchangeable, so H4 holds; rho1_hat and D estimated from r0..r2 stay at their null values
   (E g = 1; s_j^2 is within-curve), so the standard calibrated law is the one RA-05 would use.
   A failure here is a false failure caused by mean misspecification, not a departure.
     N1_curve_effect_cv0.2, N1_curve_effect_cv0.4

Seeds: SeedSequence([0xE2830E, n_b, 50 + law_index, family]) for calibrations and
SeedSequence([0xE2830E, n_b, 60 + scenario_index, 2000]) for evaluations.

Usage: python -I q2_addon.py OUT_JSON N_B [N_B ...] [--reps-cal R] [--reps-eval R] [--fam F]
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True  # no __pycache__ in the review directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import q2_pcnullr_sim as base  # noqa: E402  (this task's own script, same directory)

TOKEN = base.TOKEN
CHUNK = base.CHUNK

# calibrated laws: (name, mean factor, D rule)
LAWS = [
    ("standard", 1.0, None),
    ("recal_kappa1.10", 1.0 + 0.10 / 3, None),
    ("recal_kappa1.15", 1.0 + 0.15 / 3, None),
    ("recal_disp1.3", 1.0, "third"),
]
# scenarios: (name, law index, kappa per arm, dispersion per arm, curve-effect CV)
SCEN = [
    ("D1_r0_kappa1.10_recal", 1, [1.10, 1.0, 1.0, 1.0], [None] * 4, 0.0),
    ("D1_r0_kappa1.15_recal", 2, [1.15, 1.0, 1.0, 1.0], [None] * 4, 0.0),
    ("D2_r0_dispersion1.3_recal", 3, [1.0] * 4, [1.3, None, None, None], 0.0),
    ("N1_curve_effect_cv0.2", 0, [1.0] * 4, [None] * 4, 0.2),
    ("N1_curve_effect_cv0.4", 0, [1.0] * 4, [None] * 4, 0.4),
    ("null_check_standard", 0, [1.0] * 4, [None] * 4, 0.0),
    ("D1_kn_kappa1.10", 0, [1.0, 1.0, 1.0, 1.10], [None] * 4, 0.0),
    ("D1_kn_kappa1.15", 0, [1.0, 1.0, 1.0, 1.15], [None] * 4, 0.0),
    ("D2_kn_dispersion1.3", 0, [1.0] * 4, [None, None, None, 1.3], 0.0),
    ("D3_all_kappa1.15", 0, [1.15] * 4, [None] * 4, 0.0),
]
# Replacement criterion evaluated beside (i) and (ii) (an OPTION for Q2 (d), not a recommendation):
#   (ii') passes iff P(max_e |z_e| >= observed max_e |z_e|) >= 0.01 under the simulated joint law
#   of the four null pseudo-cells, i.e. the observed max |z| is at most the joint law's 0.99 quantile.


def law_D(D, rule):
    if rule == "third":
        return (1.3 + 2.0 * D) / 3.0
    return D


def sim(rng, m, D, R, kap, dov, cv):
    Zs, ns = [], 0.0
    for c0 in range(0, R, CHUNK):
        B = min(CHUNK, R - c0)
        if cv > 0:
            k = 1.0 / (cv * cv)
            g = rng.gamma(k, 1.0 / k, size=(B, m.size))
        else:
            g = None
        X = np.empty((B, m.size, 4), dtype=np.int64)
        for a in range(4):
            Da = D if dov[a] is None else np.full_like(D, dov[a])
            if g is None:
                X[:, :, a] = base.draw(rng, m * kap[a], Da, B)
            else:
                # per-replicate, per-curve means: draw row by row of the chunk
                for r in range(B):
                    X[r, :, a] = base.draw(rng, m * kap[a] * g[r], Da, 1)[0]
        Z, NUM, _ = base.pseudo_cells(X)
        ns = max(ns, float(np.abs(NUM.sum(axis=1)).max()))
        Zs.append(Z)
    return np.concatenate(Zs), ns


def main(argv):
    out_path = argv[1]
    rest = argv[2:]
    nbs, reps_cal, reps_eval, fams = [], 10000, 5000, 2
    i = 0
    while i < len(rest):
        if rest[i] == "--reps-cal":
            reps_cal = int(rest[i + 1]); i += 2
        elif rest[i] == "--reps-eval":
            reps_eval = int(rest[i + 1]); i += 2
        elif rest[i] == "--fam":
            fams = int(rest[i + 1]); i += 2
        else:
            nbs.append(int(rest[i])); i += 1
    t0 = time.time()
    res = {"what": "TASK-20261008-e2830e Q2 add-on (synthetic; no data read)", "laws": [l[0] for l in LAWS],
           "scenarios": [s[0] for s in SCEN], "reps_cal_per_family": reps_cal, "families_cal": fams,
           "reps_eval": reps_eval, "by_n_b": {}}
    for n_b in nbs:
        m, D, _ = base.curve_means(n_b)
        cals = []
        for li, (lname, fac, drule) in enumerate(LAWS):
            mL, DL = m * fac, law_D(D, drule)
            Zf, tA_f, lo_f, hi_f = [], [], [], []
            for f in range(fams):
                rng = np.random.default_rng(np.random.SeedSequence([TOKEN, n_b, 50 + li, f]))
                Z, _ = sim(rng, mL, DL, reps_cal, [1.0] * 4, [None] * 4, 0.0)
                Zf.append(Z)
                tA_f.append(float(np.quantile(Z[:, 3], 0.99)))
            t_dec = float(np.mean(tA_f))
            for Z in Zf:
                mz = Z.mean(axis=1)
                lo_f.append(float(np.quantile(mz, 0.005)))
                hi_f.append(float(np.quantile(mz, 0.995)))
            Zc = np.concatenate(Zf)
            Kc = (Zc > t_dec).sum(axis=1)
            maxabs_q99 = float(np.mean([np.quantile(np.abs(Z).max(axis=1), 0.99) for Z in Zf]))
            cals.append({"law": lname, "t_dec": t_dec, "lo": float(np.mean(lo_f)), "hi": float(np.mean(hi_f)),
                         "PKge": {k: float(np.mean(Kc >= k)) for k in range(5)},
                         "mean_z_null_sd": float(Zc.mean(axis=1).std(ddof=1)),
                         "maxabs_z_q99": maxabs_q99})
        ev = {}
        for si, (sname, li, kap, dov, cv) in enumerate(SCEN):
            c = cals[li]
            rng = np.random.default_rng(np.random.SeedSequence([TOKEN, n_b, 60 + si, 2000]))
            Z, ns = sim(rng, m, D, reps_eval, kap, dov, cv)
            K = (Z > c["t_dec"]).sum(axis=1)
            pk = np.array([c["PKge"][int(k)] for k in K])
            mz = Z.mean(axis=1)
            fi = pk < 0.01
            fii = (mz < c["lo"]) | (mz > c["hi"])
            fiip = np.abs(Z).max(axis=1) > c["maxabs_z_q99"]
            ev[sname] = {"calibrated_law": c["law"], "P_fail_i": float(fi.mean()), "P_fail_ii": float(fii.mean()),
                         "P_fail_PC_NULL_R": float((fi | fii).mean()), "P_K_ge_2": float((K >= 2).mean()),
                         "P_fail_replacement_ii_prime_maxabs": float(fiip.mean()),
                         "P_fail_i_or_ii_prime": float((fi | fiip).mean()),
                         "mean_of_mean_z": float(mz.mean()), "sd_of_mean_z": float(mz.std(ddof=1)),
                         "max_abs_sum_of_four_numerators": ns}
        res["by_n_b"][str(n_b)] = {"calibrations": cals, "scenarios": ev}
        print(json.dumps({"n_b": n_b, "fail": {k: [v["P_fail_i"], v["P_fail_ii"]] for k, v in ev.items()},
                          "elapsed_s": round(time.time() - t0, 1)}), flush=True)
    res["elapsed_seconds"] = round(time.time() - t0, 1)
    with open(out_path, "w") as fh:
        json.dump(res, fh, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
