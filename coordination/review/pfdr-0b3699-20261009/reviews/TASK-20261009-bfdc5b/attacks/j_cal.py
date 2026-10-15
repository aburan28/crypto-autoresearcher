"""J-CAL: re-implementation of analysis.calibration_G-NB-R from the text, plus fit tests.

TASK-20261009-bfdc5b. Written before analyze_a.py was opened (see common.py).
Seeds (this review's own; never the producer's 0x0b3699 families):
  G-NB-R families     SeedSequence([0xBFDC5B, 1, f]), f = 0..4, 20000 replicates each
  permutation null    SeedSequence([0xBFDC5B, 2, f]), f = 0..4, 20000 replicates each
  H1c bootstrap       SeedSequence([0xBFDC5B, 3]), 20000 replicates
Outputs: attacks/out/j_cal.json; scratch bank files for J-PTM / J-PCNULLR / J-COV.
"""
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
FAM = 5
import os
REPS = int(os.environ.get("BFDC_REPS", "20000"))
CHUNK = 400

d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
n = model.ncurves
obs = {a: d[f"cnt_{a}"] for a in C.NULLS}

# ---------------------------------------------------------------- simulation
fam_out = []
pc_z_all = []          # (FAM*REPS, 4) null pseudo-cell z
bankCR, bankV = [], []  # r0..r2 bank for reuse
feat_sim = {k: [] for k in ("zero", "disp", "tail", "top10", "Dhat_b30", "Dhat_b32", "Dhat")}
# per-curve 0.99 predictive quantile of NB(m_j, D) (for the tail feature)
KMAX = 12
PMF = np.empty((n, KMAX + 1))
for b in C.RUNGS:
    s = model.bits == b
    PMF[s] = C.nb_pmf_table(model.m[s], model.rung_D[b], KMAX)
CDF = np.cumsum(PMF, axis=1)
q99 = np.argmax(CDF >= 0.99, axis=1).astype(np.float64)


def features(x, m):
    """x: (k, curves) counts of one arm. Returns per-replicate features."""
    x = x.astype(np.float64)
    zero = (x == 0).mean(axis=1)
    disp = ((x - m) ** 2).sum(axis=1) / m.sum()
    tail = (x > q99).sum(axis=1)
    srt = np.sort(x, axis=1)[:, -10:]
    top10 = srt.sum(axis=1) / x.sum(axis=1)
    return zero, disp, tail, top10


for f in range(FAM):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 1, f]))
    zA, zDel, zkn = [], [], []
    done = 0
    while done < REPS:
        k = min(CHUNK, REPS - done)
        x = model.draw_curves(rng, k, 4).astype(np.float64)  # r0, r1, r2, kn
        T = x.sum(axis=1)
        Q = (x * x).sum(axis=1)
        tot = x.sum(axis=2)  # (k, 4)
        z4 = np.empty((k, 4))
        for i in range(4):
            Ti = T - x[:, i, :]
            Qi = Q - x[:, i, :] ** 2
            s2 = ((Qi - Ti * Ti / 3.0) / 2.0).sum(axis=1)
            CR = Ti.sum(axis=1) / 3.0
            V = np.maximum(s2, CR)
            z4[:, i] = (tot[:, i] - CR) / np.sqrt(4 * V / 3)
            if i == 3:
                bankCR.append(CR.copy())
                bankV.append(V.copy())
                CR3, V3 = CR, V
                Dh = {}
                for b in C.RUNGS:
                    sb = model.bits == b
                    Dh[b] = (((Qi - Ti * Ti / 3.0) / 2.0)[:, sb].sum(axis=1)) / (Ti[:, sb].sum(axis=1) / 3.0)
                feat_sim["Dhat_b30"].append(Dh[30])
                feat_sim["Dhat_b32"].append(Dh[32])
                feat_sim["Dhat"].append(((Qi - Ti * Ti / 3.0) / 2.0).sum(axis=1) / CR)
        pc_z_all.append(z4)
        zkn.append(z4[:, 3])
        # independent pseudo-structured arms A, M as closed-form totals (RD-5)
        A = model.null_total(rng, k).astype(np.float64)
        M = model.null_total(rng, k).astype(np.float64)
        zA.append((A - CR3) / np.sqrt(4 * V3 / 3))
        zDel.append((A - M) / np.sqrt(2 * V3))
        if f == 0:
            fe = features(x[:, 0, :], model.m)
            for key, v in zip(("zero", "disp", "tail", "top10"), fe):
                feat_sim[key].append(v)
        done += k
    zA = np.concatenate(zA); zDel = np.concatenate(zDel); zkn = np.concatenate(zkn)
    fam_out.append({"family": f, "t_A_closed_form_arm": float(np.quantile(zA, 0.99)),
                    "t_A_per_curve_known_null_arm": float(np.quantile(zkn, 0.99)),
                    "t_A_0999": float(np.quantile(zA, 0.999)),
                    "t_Delta": float(np.quantile(zDel, 0.95)),
                    "mean_zA": float(zA.mean()), "sd_zA": float(zA.std())})
    print("family", f, fam_out[-1], flush=True)

pc_z = np.concatenate(pc_z_all)
np.save(f"{C.SCR}/pc_z_bank.npy", pc_z)
np.save(f"{C.SCR}/bank_CR.npy", np.concatenate(bankCR))
np.save(f"{C.SCR}/bank_V.npy", np.concatenate(bankV))


def avg(key):
    v = np.array([fo[key] for fo in fam_out])
    return {"mean": float(v.mean()), "per_family": v.tolist(), "spread_min_max": [float(v.min()), float(v.max())],
            "sd_across_families": float(v.std(ddof=1)), "mc_se_of_mean": float(v.std(ddof=1) / np.sqrt(len(v)))}


t_A = avg("t_A_closed_form_arm")
t_A_kn = avg("t_A_per_curve_known_null_arm")
t_Delta = avg("t_Delta")

# --------------------------------------------------------- permutation null
cnt4 = np.vstack([obs[a] for a in C.NULLS]).astype(np.float64)  # (4, n)
T4 = cnt4.sum(axis=0)
Q4 = (cnt4 ** 2).sum(axis=0)
perm = []
for f in range(FAM):
    rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 2, f]))
    zs = []
    done = 0
    while done < REPS:
        k = min(2000, REPS - done)
        idx = rng.integers(0, 4, size=(k, n))
        X = np.take_along_axis(np.broadcast_to(cnt4, (k, 4, n)), idx[:, None, :], axis=1)[:, 0, :]
        Ti = T4 - X
        Qi = Q4 - X * X
        CR = Ti.sum(axis=1) / 3
        V = np.maximum(((Qi - Ti * Ti / 3) / 2).sum(axis=1), CR)
        zs.append((X.sum(axis=1) - CR) / np.sqrt(4 * V / 3))
        done += k
    zs = np.concatenate(zs)
    perm.append({"family": f, "t_perm": float(np.quantile(zs, 0.99))})
tp = np.array([p["t_perm"] for p in perm])
t_perm = {"mean": float(tp.mean()), "per_family": tp.tolist(), "mc_se_of_mean": float(tp.std(ddof=1) / np.sqrt(FAM))}
t_dec = max(t_A["mean"], t_perm["mean"])

# ----------------------------------------------------------------- fit tests
fit_tests = {}
for key in ("zero", "disp", "tail", "top10"):
    feat_sim[key] = np.concatenate(feat_sim[key])
for a in C.NULLS:
    x = obs[a][None, :]
    ofe = features(x, model.m)
    row = {}
    for key, v in zip(("zero", "disp", "tail", "top10"), ofe):
        sim = feat_sim[key]
        lo, hi = np.quantile(sim, [0.005, 0.995])
        row[key] = {"observed": float(v[0]), "pred99": [float(lo), float(hi)],
                    "inside": bool(lo <= v[0] <= hi),
                    "upper_tail_p": float((sim >= v[0]).mean()), "lower_tail_p": float((sim <= v[0]).mean())}
    fit_tests[a] = row
fit_tests["predictive_note"] = ("plug-in predictive under the fitted G-NB-R (family 0, 20000 replicates of one arm); "
                                "parameter uncertainty of rho1_hat and D not propagated, so the ranges are slightly narrow")
# count histogram vs model expectation (per value)
exp_hist = {}
for v in range(6):
    exp_hist[v] = float(PMF[:, v].sum())
fit_tests["expected_histogram_per_arm"] = exp_hist
fit_tests["observed_histograms"] = {a: np.bincount(obs[a], minlength=6).tolist() for a in C.NULLS}
p_ge3 = 1.0 - CDF[:, 2]
fit_tests["curves_ge3_expected_per_arm"] = float(p_ge3.sum())
fit_tests["curves_ge3_observed"] = {a: int((obs[a] >= 3).sum()) for a in C.NULLS}
fit_tests["curves_ge3_observed_total_4arms"] = int(sum((obs[a] >= 3).sum() for a in C.NULLS))
fit_tests["curves_ge3_poisson_upper_p_4arms"] = float(C.poisson_sf(fit_tests["curves_ge3_observed_total_4arms"] - 1,
                                                                   4 * p_ge3.sum()))

# ------------------------------------------------------------------- H1c
R = np.vstack([obs[f"random_sub_r{i}"] for i in range(3)]).astype(np.float64)
s2 = R.var(axis=0, ddof=1)
nb = R.mean(axis=0)
rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 3]))
boot = {}
for name, sel in (("pooled", np.ones(n, bool)), ("b30", d["bits"] == 30), ("b32", d["bits"] == 32)):
    idx_all = np.nonzero(sel)[0]
    est = s2[sel].sum() / nb[sel].sum()
    bs = np.empty(20000)
    for i in range(0, 20000, 1000):
        if name == "pooled":
            # resample curves within rung (curve-cluster bootstrap, stratified by rung)
            parts_s, parts_n = 0, 0
            for b in C.RUNGS:
                ib = np.nonzero(d["bits"] == b)[0]
                ii = rng.choice(ib, size=(1000, len(ib)))
                parts_s = parts_s + s2[ii].sum(axis=1)
                parts_n = parts_n + nb[ii].sum(axis=1)
            bs[i:i + 1000] = parts_s / parts_n
        else:
            ii = rng.choice(idx_all, size=(1000, len(idx_all)))
            bs[i:i + 1000] = s2[ii].sum(axis=1) / nb[ii].sum(axis=1)
    lo, hi = np.quantile(bs, [0.005, 0.995])
    boot[name] = {"D_hat": float(est), "boot99": [float(lo), float(hi)],
                  "inside_0.8_1.25": bool(lo >= 0.8 and hi <= 1.25),
                  "entirely_outside_0.8_1.25": bool(hi < 0.8 or lo > 1.25)}
for key in ("Dhat_b30", "Dhat_b32", "Dhat"):
    v = np.concatenate(feat_sim[key])
    boot[f"model_null_{key}_q005_q995"] = [float(np.quantile(v, 0.005)), float(np.quantile(v, 0.995))]

res = {
    "task": "TASK-20261009-bfdc5b", "joint": "J-CAL",
    "readings": "common.py RD-1..RD-4",
    "seeds": {"G-NB-R": "SeedSequence([0xBFDC5B, 1, f]) f=0..4", "perm": "SeedSequence([0xBFDC5B, 2, f]) f=0..4",
              "H1c_boot": "SeedSequence([0xBFDC5B, 3])"},
    "replicates": {"families": FAM, "per_family": REPS, "H1c_boot": 20000},
    "fit": {str(b): fit[b] for b in C.RUNGS},
    "t_A": t_A, "t_A_per_curve_known_null_arm": t_A_kn, "t_Delta": t_Delta, "t_perm": t_perm, "t_dec": t_dec,
    "families": fam_out, "perm_families": perm,
    "fit_tests": fit_tests, "H1c": boot,
}
C.jdump(res, OUT)
print("t_A", t_A, "\nt_Delta", t_Delta, "\nt_perm", t_perm, "\nfit", fit)
