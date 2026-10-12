"""J-DISP: dispersion robustness of the small_x reading, and (for J-COV) coverage of the
frozen bound under departure laws consistent with the null arms. TASK-20261009-bfdc5b.

Part 1 (written before analyze_a.py was opened): rho_A, rho_M by the frozen
dispersion_robustness formula with a curve-cluster bootstrap 95% interval (resampling
curves within rung), z_A with V x max(1, upper end).
Part 2: departure laws fitted to the four null arms (departures.py), each at its 99%
upper end; per law: t_A_alt, t_dec_alt, z_A against it, the signed and |dev| bounds
simulated under the law at small_x's kappa_hat, power at kappa 1.10 / 1.15, and the
coverage of the FROZEN G-NB-R bound (bank A grid) on designs drawn from the law.
Part 3: leave-top-10-curves-out and per-rung splits.

Seeds: bootstrap SeedSequence([0xBFDC5B, 12]) 20000; law L: SeedSequence([0xBFDC5B, 14, L, task])
with task 0 t_A (20000), 1 power (4000 per kappa), 2 dev at kappa_hat (20000),
3 coverage (4000 per kappa); part 3 bounds SeedSequence([0xBFDC5B, 15, v, f]).
All reduced counts are declared; Monte Carlo SE reported.
"""
import json
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C
import bounds as B
import departures as DP

OUT = sys.argv[2]
cal = json.load(open(sys.argv[3]))
t_perm = cal["t_perm"]["mean"]
t_dec = cal["t_dec"]
d = C.load()
fit = C.fit_gnbr(d)
model = C.Model(d, fit)
A = d["cnt_small_x"].astype(float)
M = d["cnt_small_x_offset"].astype(float)
R = np.vstack([d[f"cnt_random_sub_r{i}"] for i in range(3)]).astype(float)
KN = d["cnt_known_null_sub"].astype(float)
nbar = R.mean(axis=0)
s2 = R.var(axis=0, ddof=1)
bits = d["bits"]
obsA = C.cc8(A, *R)
kh, SE = obsA["kappa_rel"], obsA["SE"]


# ------------------------------------------------------------------ part 1
def rho_of(X, idx):
    nb = nbar[idx]
    ss = s2[idx]
    x = X[idx]
    k = x.sum() / nb.sum()
    dj = x - nb
    DA = (((dj - (k - 1) * nb) ** 2).sum() - ss.sum() / 3) / nb.sum()
    DR = ss.sum() / nb.sum()
    return DA / DR, DA, DR


rng = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 12]))
idx30 = np.nonzero(bits == 30)[0]
idx32 = np.nonzero(bits == 32)[0]
allidx = np.arange(len(A))
rho_res = {}
for name, X in (("small_x", A), ("small_x_offset", M), ("known_null_sub", KN)):
    est = rho_of(X, allidx)
    bs = np.empty(20000)
    rng_b = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 12, len(name)]))
    for i in range(20000):
        ii = np.concatenate([rng_b.choice(idx30, len(idx30)), rng_b.choice(idx32, len(idx32))])
        bs[i] = rho_of(X, ii)[0]
    lo, hi = np.quantile(bs, [0.025, 0.975])
    rho_res[name] = {"rho": est[0], "D_A_hat": est[1], "D_R_hat": est[2], "boot95": [float(lo), float(hi)],
                     "boot_replicates": 20000}
upA = rho_res["small_x"]["boot95"][1]
Vs = obsA["V"] * max(1.0, upA)
z_scaled = (obsA["C_A"] - obsA["C_R"]) / np.sqrt(4 * Vs / 3)
part1 = {"rho": rho_res, "z_A": obsA["z"], "z_A_V_scaled_by_upper": z_scaled, "V_scale": max(1.0, upA),
         "U_signed_scaled_approx": None}
print("part1", json.dumps(part1, default=float), flush=True)

# ------------------------------------------------------------------ fit departure laws
nullX = np.vstack([R, KN[None, :]])  # 4 x n
m = model.m
Dc = model.D


def loglik_pmf(pmf):  # pmf: (n, K+1) per curve; nullX counts
    ll = 0.0
    for a in range(4):
        x = nullX[a].astype(int)
        ll += np.log(np.maximum(pmf[np.arange(len(x)), np.minimum(x, pmf.shape[1] - 1)], 1e-300)).sum()
    return ll


KM = 10


def nb_pmf_curves(mean, Dpc):
    out = np.empty((len(mean), KM + 1))
    for Dv in np.unique(Dpc):
        s = Dpc == Dv
        out[s] = C.nb_pmf_table(mean[s], Dv, KM)
    return out


def zinf_pmf(pi):
    p = nb_pmf_curves(m / (1 - pi), Dc) * (1 - pi)
    p[:, 0] += pi
    return p


def cluster_pmf(c):
    c = np.asarray(c, float)
    lam = m / np.sum((np.arange(len(c)) + 1) * c)
    p = np.zeros((len(m), KM + 1))
    p[:, 0] = 1.0
    for i, ci in enumerate(c):
        k = i + 1
        q = C.nb_pmf_table(lam * ci, 1.0, KM)  # Poisson pmf of the number of size-k clusters
        qq = np.zeros((len(m), KM + 1))
        for j in range(0, KM // k + 1):
            qq[:, j * k] = q[:, j]
        # convolve p with qq
        new = np.zeros_like(p)
        for a in range(KM + 1):
            new[:, a:] += p[:, [a]] * qq[:, :KM + 1 - a]
        p = new
    return p


ll0 = loglik_pmf(nb_pmf_curves(m, Dc))
LR99 = 6.6349 / 2
fits = {}
# zero inflation: profile over pi
pis = np.linspace(0, 0.30, 301)
lls = np.array([loglik_pmf(zinf_pmf(p)) for p in pis])
best = pis[lls.argmax()]
ok = pis[lls >= lls.max() - LR99]
fits["zinf"] = {"pi_hat": float(best), "pi_upper99": float(ok.max()), "ll_gain_at_hat": float(lls.max() - ll0)}
# clusters of size 3 (c = (1 - c3, 0, c3)) and of size 2
for name, mk in (("cluster3", lambda t: (1 - t, 0.0, t)), ("cluster2", lambda t: (1 - t, t))):
    ts = np.linspace(0, 0.10, 201)
    lls = np.array([loglik_pmf(cluster_pmf(mk(t))) for t in ts])
    ok = ts[lls >= lls.max() - LR99]
    fits[name] = {"c_hat": float(ts[lls.argmax()]), "c_upper99": float(ok.max()), "ll_gain_at_hat": float(lls.max() - loglik_pmf(cluster_pmf(mk(0.0))))}
# NB D: per-rung 99% bootstrap upper end of D_hat (J-CAL H1c)
fits["nb_D"] = {"D_upper99": {30: cal["H1c"]["b30"]["boot99"][1], 32: cal["H1c"]["b32"]["boot99"][1]}}
# curve effect tau2 from cross-arm covariance with curve bootstrap
def tau2_of(idx):
    X = nullX[:, idx] - m[idx]
    cr = 0.0
    for a in range(4):
        for b in range(a + 1, 4):
            cr += (X[a] * X[b]).sum()
    return cr / (6 * (m[idx] ** 2).sum())


t2 = tau2_of(allidx)
rng_t = np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 12, 99]))
bt = np.array([tau2_of(np.concatenate([rng_t.choice(idx30, len(idx30)), rng_t.choice(idx32, len(idx32))])) for _ in range(4000)])
fits["gamma"] = {"tau2_hat": float(t2), "tau2_boot99": [float(np.quantile(bt, 0.005)), float(np.quantile(bt, 0.995))]}
tau2_up = max(1e-6, float(np.quantile(bt, 0.995)))
rhoA_up = max(1.307, upA)
print("fits", json.dumps(fits), flush=True)

laws = [
    ("nb_D_upper99", DP.Law(model, "nb_D", D=fits["nb_D"]["D_upper99"])),
    ("zero_inflated_pi_upper99", DP.Law(model, "zinf", pi=max(fits["zinf"]["pi_upper99"], 1e-9))),
    ("cluster3_c_upper99", DP.Law(model, "cluster", c=(1 - fits["cluster3"]["c_upper99"], 0.0, fits["cluster3"]["c_upper99"]))),
    ("gamma_shared_tau2_upper99", DP.Law(model, "gamma_shared", tau2=tau2_up)),
    ("gamma_unshared_A_tau2_upper99", DP.Law(model, "gamma_unshared_A", tau2=tau2_up)),
    ("A_overdispersed_rhoA_%.3f" % rhoA_up, DP.Law(model, "A_overdispersed", rhoA=rhoA_up)),
]
CRa = np.load(f"{C.SCR}/bank_CR.npy")
Va = np.load(f"{C.SCR}/bank_V.npy")
bA = B.Bounds(model, CRa, Va, 5, seed_tag=5)
bA._q_lo = np.load(f"{C.SCR}/grid_qlo_A.npy")
bA._q_abs = np.load(f"{C.SCR}/grid_qabs_A.npy")
law_res = {}
for L, (name, law) in enumerate(laws):
    sd = lambda t: np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 14, L, t]))
    CR, V, CA = law.joint(sd(0), 20000, 1.0)
    z0 = C.z_from(CA, CR, V)
    tA = float(np.quantile(z0, 0.99))
    sec = [np.quantile(z0[i::5], 0.99) for i in range(5)]
    tA_se = float(np.std(sec, ddof=1) / np.sqrt(5))
    tdec_alt = max(tA, t_perm)
    pw = {}
    for kap in (1.10, 1.15):
        CR1, V1, CA1 = law.joint(sd(1), 4000, kap)
        p = float((C.z_from(CA1, CR1, V1) > tdec_alt).mean())
        pw[f"{kap:.2f}"] = [p, float(np.sqrt(p * (1 - p) / 4000))]
    CR2, V2, CA2 = law.joint(sd(2), 20000, kh)
    dev = (CA2 / CR2 - kh) / (np.sqrt(4 * V2 / 3) / CR2)
    qlo = float(np.quantile(dev, 0.05))
    qab = float(np.quantile(np.abs(dev), 0.95))
    U_s = kh - qlo * SE
    U_a = kh + qab * SE
    covr = {}
    for kap in (1.00, 1.10, 1.15):
        CR3, V3, CA3 = law.joint(sd(3), 4000, kap)
        khs = CA3 / CR3
        SEs = np.sqrt(4 * V3 / 3) / CR3
        covr[f"{kap:.2f}"] = B.coverage(bA, khs, SEs, kap)
    xrel_le_115 = pw["1.15"][0] >= 0.5
    cls = "O-A3" if (obsA["z"] <= tdec_alt and max(U_s, U_a) <= 1.15 and xrel_le_115) else (
        "excess" if obsA["z"] > tdec_alt else "O-A4")
    law_res[name] = {"t_A_alt": tA, "t_A_alt_mc_se": tA_se, "t_dec_alt": tdec_alt, "z_A": obsA["z"],
                     "z_A_gt_t_dec_alt": bool(obsA["z"] > tdec_alt), "power": pw,
                     "U_signed_alt": U_s, "U_absdev_alt": U_a, "q_lo_alt": qlo, "q_abs_alt": qab,
                     "frozen_bound_coverage_on_law": covr, "X_rel_le_1.15_alt": bool(xrel_le_115),
                     "outcome_class_alt": cls,
                     "replicates": {"t_A": 20000, "power": 4000, "dev": 20000, "coverage": 4000}}
    print(name, json.dumps(law_res[name], default=float), flush=True)

# ------------------------------------------------------------------ part 3
var = {}
# (a) leave the 10 curves with the largest small_x contribution (n_A - nbar) out
contrib = A - nbar
order = np.lexsort((d["curve"], bits, -contrib))
drop = order[:10]
keep = np.ones(len(A), bool)
keep[drop] = False
# (b) leave the 10 curves with the largest null-arm mean out
order2 = np.lexsort((d["curve"], bits, -nbar))
keep2 = np.ones(len(A), bool)
keep2[order2[:10]] = False
for vi, (name, mask) in enumerate((("leave_top10_small_x_contrib_out", keep), ("leave_top10_null_mean_out", keep2),
                                   ("rung_30", bits == 30), ("rung_32", bits == 32))):
    c = C.cc8(A[mask], *(R[i][mask] for i in range(3)))
    fit_m = C.fit_gnbr(d, mask=mask) if name.startswith("leave") else C.fit_gnbr(d)
    mdl = C.Model(d, fit_m, mask=mask)
    rngs = [np.random.default_rng(np.random.SeedSequence([C.REVIEW_TOKEN, 15, vi, f])) for f in range(5)]
    CRv, Vv = C.random_bank(mdl, rngs[0], 20000)
    zz = C.z_from(mdl.null_total(rngs[1], 20000).astype(float), CRv, Vv)
    tA_v = float(np.quantile(zz, 0.99))
    bnd = B.Bounds(mdl, CRv, Vv, 5, seed_tag=15)
    qlo, qab, _, _ = bnd.quantiles_at(c["kappa_rel"], rngs)
    pw115 = B.power_at(mdl, CRv, Vv, max(tA_v, t_perm), rngs[2], 1.15, "poisson")
    var[name] = {"curves": int(mask.sum()), "dropped": [(int(bits[i]), int(d["curve"][i])) for i in np.nonzero(~mask)[0]][:10],
                 "C_A": c["C_A"], "C_R": c["C_R"], "z_A": c["z"], "kappa_hat": c["kappa_rel"], "SE": c["SE"],
                 "t_A_variant": tA_v, "U_signed": c["kappa_rel"] - qlo * c["SE"], "U_absdev": c["kappa_rel"] + qab * c["SE"],
                 "power_1.15": pw115, "replicates": "20000 (4 x 5000 per family for the bound)"}
    print(name, json.dumps(var[name], default=float), flush=True)

res = {"task": "TASK-20261009-bfdc5b", "joint": "J-DISP", "t_dec": t_dec, "t_perm": t_perm,
       "part1": part1, "fits_to_null_arms": fits, "laws": law_res, "subset_variants": var}
C.jdump(res, OUT)
