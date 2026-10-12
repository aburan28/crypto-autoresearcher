"""J-CAL (extra): shape of the G-NB-R mean model across curves and rungs, and where the
observed PC-NULL-R statistics sit in the simulated joint law. Deterministic except the
joint-law bank of j_cal.py (SeedSequence([0xBFDC5B, 1, f]), 5 x 20000). TASK-20261009-bfdc5b.
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
X = np.vstack([d[f"cnt_{a}"] for a in C.NULLS]).astype(float)  # 4 x n
mu = d["mu_model"]
out = {}
# mean-model shape: deciles of mu_model, per rung; observed (4 null arms) vs fitted 4 m_j
for b in C.RUNGS:
    s = d["bits"] == b
    qs = np.quantile(mu[s], np.linspace(0, 1, 11))
    g = np.clip(np.digitize(mu[s], qs[1:-1]), 0, 9)
    rows = []
    chi = 0.0
    for k in range(10):
        sel = g == k
        o = X[:, s][:, sel].sum()
        e = 4 * model.m[s][sel].sum()
        chi += (o - e) ** 2 / (model.rung_D[b] * e)
        rows.append({"decile": k, "curves": int(sel.sum()), "mu_mean": float(mu[s][sel].mean()),
                     "observed_4arms": o, "fitted_4arms": e, "ratio": o / e})
    # least-squares slope of log(ratio) on log(mu_mean) (power-law misfit)
    lx = np.log([r["mu_mean"] for r in rows])
    ly = np.log([r["ratio"] for r in rows])
    slope = float(np.polyfit(lx, ly, 1)[0])
    out[str(b)] = {"deciles": rows, "pearson_chi2": chi, "df": 9, "loglog_slope_ratio_vs_mu": slope}
# where do the observed PC-NULL-R statistics sit
bank = np.load(f"{C.SCR}/pc_z_bank.npy")
obs = []
for i in range(4):
    others = [X[j] for j in range(4) if j != i]
    obs.append(C.cc8(X[i], *others)["z"])
mz = float(np.mean(obs))
mb = bank.mean(axis=1)
out["pc_null_mean_z"] = {"observed": mz, "sim_quantiles_0.005_0.5_0.995": np.quantile(mb, [0.005, 0.5, 0.995]).tolist(),
                         "sim_P_le_observed": float((mb <= mz).mean()),
                         "sum_of_numerators_identity": "sum_i (C_i - C_R(i)) = 0 exactly for the four pseudo-cells",
                         "sum_of_numerators_observed": float(sum(X[i].sum() - (X.sum() - X[i].sum()) / 3 for i in range(4)))}
# informative alternatives to criterion (i) on the same joint law (reviewer controls, not frozen rules)
ss_b = (bank ** 2).sum(axis=1)
mx_b = bank.max(axis=1)
ss_o = float(np.sum(np.square(obs)))
mx_o = float(np.max(obs))
out["pc_null_alternatives"] = {"sum_z2": {"observed": ss_o, "sim_q99": float(np.quantile(ss_b, 0.99)),
                                          "P_ge_observed": float((ss_b >= ss_o).mean())},
                               "max_z": {"observed": mx_o, "sim_q99": float(np.quantile(mx_b, 0.99)),
                                         "P_ge_observed": float((mx_b >= mx_o).mean())},
                               "replicates": len(bank)}
out["per_rung_rho1_and_D"] = {str(b): {k: fit[b][k] for k in ("rho1_hat", "D_hat", "D")} for b in C.RUNGS}
C.jdump(out, OUT)
print(json.dumps(out, indent=1, default=float))
