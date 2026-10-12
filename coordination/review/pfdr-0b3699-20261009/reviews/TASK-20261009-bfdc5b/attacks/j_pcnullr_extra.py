"""J-PCNULLR (extra): the cheapest non-degenerate replacement for criterion (i), evaluated
on the same departures. Statistic S2 = sum of the four null pseudo-cell z^2 and Zmax = max z,
each against its 0.99 quantile under the simulated joint law (pc_z_bank.npy, j_cal.py).
Reviewer control only; changes no frozen rule. TASK-20261009-bfdc5b.
Seeds SeedSequence([0xBFDC5B, 17, scenario]); 5000 replicates per scenario (declared).
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
bank = np.load(f"{C.SCR}/pc_z_bank.npy")
q_ss = float(np.quantile((bank ** 2).sum(axis=1), 0.99))
q_mx = float(np.quantile(bank.max(axis=1), 0.99))
REPS = 5000
res = {"q99_sum_z2": q_ss, "q99_max_z": q_mx, "replicates": REPS, "scenarios": {}}
for si, (name, arms, kap) in enumerate([("null", [], 1.0), ("kn_1.10", [3], 1.10), ("r0_1.10", [0], 1.10),
                                         ("kn_1.15", [3], 1.15), ("r0_1.15", [0], 1.15)]):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 17, si]))
    zs = []
    done = 0
    while done < REPS:
        k = min(250, REPS - done)
        x = model.draw_curves(rng, k, 4).astype(np.float64)
        for a in arms:
            x[:, a, :] += rng.poisson((kap - 1) * model.m, size=(k, model.ncurves))
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
    p_ss = float(((zs ** 2).sum(axis=1) > q_ss).mean())
    p_mx = float((zs.max(axis=1) > q_mx).mean())
    res["scenarios"][name] = {"reject_sum_z2": p_ss, "reject_sum_z2_mc_se": float(np.sqrt(max(p_ss * (1 - p_ss), 1 / REPS) / REPS)),
                              "reject_max_z": p_mx, "reject_max_z_mc_se": float(np.sqrt(max(p_mx * (1 - p_mx), 1 / REPS) / REPS))}
    print(name, res["scenarios"][name], flush=True)
C.jdump(res, OUT)
