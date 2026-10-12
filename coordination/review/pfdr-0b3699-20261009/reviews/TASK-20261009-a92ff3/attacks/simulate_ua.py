#!/usr/bin/env python3
"""TASK-20261009-a92ff3 (J-BLIND) -- U_A bounds and their coverages, written from
EXP-PFDR-0b3699 analysis.calibration_G-NB-R and analysis.upper_bound_U_A and
EXP-PFDR-011cd0 A-CAL / A-INT texts, under readings.yaml R-8..R-16.

No crypto_autoresearcher import; nothing under experiments/ is imported or read
(inputs are this task's own percurve.json.gz and counts.json).

Subcommands (all deterministic given the seeds of R-16):
  bank      <reading> <purpose>                  -> bank_<reading>_<purpose>.npz
  observed  <reading> <bank_purpose> <struct_purpose>  -> observed_<reading>_<bank>.json
  designs                                         -> designs.npz (adopted reading)
  coverage  <bank_purpose> <inner_base>           -> coverage_bank<p>.json (+ .npz per-design)

Seeds: numpy Generator(PCG64(SeedSequence([0xA92FF3, purpose, family]))).
"""
from __future__ import annotations

import gzip
import json
import math
import os
import sys
import time

import numpy as np

TOKEN = 0xA92FF3
FAMILIES = 5
REPS = int(os.environ.get("A92_REPS", "20000"))        # per family (bank and observed bound)
DESIGNS = int(os.environ.get("A92_DESIGNS", "4000"))   # per family per kappa (coverage)
# The overrides exist only for a smoke test; every reported value uses the defaults.
KAPPAS = (1.00, 1.10, 1.15)
CHUNK = 400
RANDOMS = ("random_sub_r0", "random_sub_r1", "random_sub_r2")


def gen(purpose: int, family: int) -> np.random.Generator:
    return np.random.Generator(np.random.PCG64(np.random.SeedSequence([TOKEN, purpose, family])))


def load(indir: str):
    curves = [json.loads(l) for l in gzip.open(os.path.join(indir, "percurve.json.gz"), "rt")]
    curves = [c for c in curves if c["A_F1"]]          # R-3 S1: the A cell's curves
    counts = json.load(open(os.path.join(indir, "counts.json")))
    return curves, counts


def model(curves, reading: str) -> dict:
    """G-NB-R parameters under a reading (R-8 MU, R-9 RH, R-10 DD)."""
    bits = np.array([c["bits"] for c in curves])
    s = np.array([c["s_sub"] for c in curves], dtype=float)
    N = np.array([c["N"] for c in curves], dtype=float)
    if reading == "MU2":
        V = s * (s - 1)
        mu = V * (V - 1) / 3.0 / N
    else:
        mu = np.array([c["mu_model"] for c in curves], dtype=float)
    r = np.array([[c["n"][a] for a in RANDOMS] for c in curves], dtype=float)
    nbar = r.mean(axis=1)
    s2 = r.var(axis=1, ddof=1)
    m = np.empty_like(mu)
    D = {}
    rho = {}
    for b in (30, 32):
        sel = bits == b
        if reading == "RH2":
            rho[b] = float(np.mean(nbar[sel] / mu[sel]))
        else:
            rho[b] = float(nbar[sel].sum() / mu[sel].sum())
        m[sel] = rho[b] * mu[sel]
        if reading == "DD2":
            D[b] = max(float(s2.sum() / nbar.sum()), 1.0)
        else:
            D[b] = max(float(s2[sel].sum() / nbar[sel].sum()), 1.0)
    Dc = np.where(bits == 30, D[30], D[32])
    rung = {}
    for b in (30, 32):
        sel = bits == b
        rung[b] = {"msum": float(m[sel].sum()), "D": D[b],
                   "nsum": float(m[sel].sum() / (D[b] - 1.0)) if D[b] > 1 else None,
                   "p": 1.0 / D[b]}
    return {"reading": reading, "m": m, "D_curve": Dc, "rho1_hat_b": rho, "D_b": D,
            "D_hat_b_raw": {b: float(s2[bits == b].sum() / nbar[bits == b].sum()) for b in (30, 32)},
            "rung": rung, "ncurves": len(curves)}


def draw_randoms(rng, mod, reps: int):
    """Per-curve r0, r1, r2 iid NB(m_j, D m_j); returns T = 3 C_R* and Q = 6 sum s_j^2 (int64)."""
    m, Dc = mod["m"], mod["D_curve"]
    nb = Dc > 1.0
    n = np.where(nb, m / np.where(nb, Dc - 1.0, 1.0), 1.0)
    p = 1.0 / Dc
    T = np.empty(reps, dtype=np.int64)
    Q = np.empty(reps, dtype=np.int64)
    done = 0
    while done < reps:
        c = min(CHUNK, reps - done)
        if nb.all():
            r = rng.negative_binomial(n, p, size=(c, 3, len(m)))
        else:
            r = np.where(nb, rng.negative_binomial(n, p, size=(c, 3, len(m))),
                         rng.poisson(m, size=(c, 3, len(m))))
        S = r.sum(axis=1)
        SS = (r * r).sum(axis=1)
        T[done:done + c] = S.sum(axis=1)
        Q[done:done + c] = (3 * SS - S * S).sum(axis=1)
        done += c
    return T, Q


def draw_struct_totals(rng, mod, kappa, size):
    """Structured-arm pooled total C_A* by the simulation rule, per rung in law:
    null NB rung total (common p within a rung), then + Poisson((kappa-1) sum m) for
    kappa > 1, Binomial(null, kappa) for kappa < 1, as drawn for kappa == 1.
    kappa may be an array broadcastable to size[:-1] + (1,)."""
    kappa = np.asarray(kappa, dtype=float)
    tot = np.zeros(size, dtype=np.int64)
    for b in (30, 32):
        R = mod["rung"][b]
        if R["nsum"] is not None:
            null = rng.negative_binomial(R["nsum"], R["p"], size=size)
        else:
            null = rng.poisson(R["msum"], size=size)
        k = np.broadcast_to(kappa if kappa.ndim == 0 else kappa.reshape(kappa.shape + (1,) * (len(size) - kappa.ndim)), size)
        up = k > 1.0
        dn = k < 1.0
        out = null.copy()
        if up.any():
            lam = np.where(up, (k - 1.0) * R["msum"], 0.0)
            out = out + rng.poisson(lam)
        if dn.any():
            out = np.where(dn, rng.binomial(null, np.where(dn, k, 1.0)), out)
        tot += out
    return tot


def se_of(T, Q):
    C_R = T / 3.0
    V = np.maximum(Q / 6.0, C_R)
    return C_R, np.sqrt(4.0 * V / 3.0) / C_R


def quantile_se(x, p, n):
    """Asymptotic SE of the p-quantile of a sample of size n from the pooled sample x."""
    h = 0.005
    lo, hi = np.quantile(x, [max(p - h, 1e-6), min(p + h, 1 - 1e-6)])
    dens = 2 * h / (hi - lo) if hi > lo else float("nan")
    return math.sqrt(p * (1 - p) / n) / dens


def bounds_from(dev_f, absdev_f, absfix_f, khat, SE):
    """dev_f etc: arrays (FAMILIES, REPS). Returns dict of the bounds under Q1/Q2, AB1/AB2."""
    qlo_f = np.quantile(dev_f, 0.05, axis=1)
    qab_f = np.quantile(absdev_f, 0.95, axis=1)
    qfx_f = np.quantile(absfix_f, 0.95, axis=1)
    pooled = dev_f.ravel()
    out = {
        "q_lo_per_family": qlo_f.tolist(), "q_abs_per_family": qab_f.tolist(),
        "q_lo_Q1": float(qlo_f.mean()), "q_abs_Q1": float(qab_f.mean()),
        "q_lo_Q2": float(np.quantile(pooled, 0.05)), "q_abs_Q2": float(np.quantile(absdev_f.ravel(), 0.95)),
        "q_absfixedSE_AB2_Q1": float(qfx_f.mean()),
    }
    out["U_signed_Q1"] = khat - out["q_lo_Q1"] * SE
    out["U_signed_Q2"] = khat - out["q_lo_Q2"] * SE
    out["U_absdev_Q1"] = khat + out["q_abs_Q1"] * SE
    out["U_absdev_Q2"] = khat + out["q_abs_Q2"] * SE
    out["U_absdev_AB2_Q1"] = khat + out["q_absfixedSE_AB2_Q1"] * SE
    n = dev_f.size
    se_qlo_asym = quantile_se(pooled, 0.05, n)
    se_qab_asym = quantile_se(absdev_f.ravel(), 0.95, n)
    se_qlo_fam = float(qlo_f.std(ddof=1) / math.sqrt(len(qlo_f)))
    se_qab_fam = float(qab_f.std(ddof=1) / math.sqrt(len(qab_f)))
    out["mc_se"] = {
        "U_signed_asymptotic": se_qlo_asym * SE, "U_signed_family_spread": se_qlo_fam * SE,
        "U_absdev_asymptotic": se_qab_asym * SE, "U_absdev_family_spread": se_qab_fam * SE,
        "U_signed_reported": max(se_qlo_asym, se_qlo_fam) * SE,
        "U_absdev_reported": max(se_qab_asym, se_qab_fam) * SE,
        "rule": "reported = max(asymptotic order-statistic SE on the pooled replicates, SD of the 5 family quantiles / sqrt 5), times SE",
    }
    return out


def cmd_bank(indir, outdir, reading, purpose):
    curves, _ = load(indir)
    mod = model(curves, reading)
    t0 = time.time()
    T = np.empty((FAMILIES, REPS), dtype=np.int64)
    Q = np.empty((FAMILIES, REPS), dtype=np.int64)
    for f in range(FAMILIES):
        T[f], Q[f] = draw_randoms(gen(purpose, f), mod, REPS)
    np.savez_compressed(os.path.join(outdir, f"bank_{reading}_{purpose}.npz"), T=T, Q=Q)
    m = mod["m"]
    diag = {"reading": reading, "purpose": purpose, "seconds": time.time() - t0,
            "mean_C_R_star": float((T / 3).mean()), "model_sum_m": float(m.sum()),
            "mean_sum_s2_star": float((Q / 6).mean()),
            "model_sum_D_m": float((mod["D_curve"] * m).sum()),
            "rho1_hat_b": mod["rho1_hat_b"], "D_b": mod["D_b"], "D_hat_b_raw": mod["D_hat_b_raw"],
            "rung": mod["rung"]}
    json.dump(diag, open(os.path.join(outdir, f"bank_{reading}_{purpose}.json"), "w"), indent=1)
    print(json.dumps(diag))


def cmd_observed(indir, outdir, reading, bank_purpose, struct_purpose):
    curves, counts = load(indir)
    mod = model(curves, reading)
    A = counts["cells"]["A_pooled"]
    CA, T3 = A["C_X"], A["three_C_R"]
    khat = CA / (T3 / 3.0)
    SE = A["SE"]
    bk = np.load(os.path.join(outdir, f"bank_{reading}_{bank_purpose}.npz"))
    T, Q = bk["T"], bk["Q"]
    dev = np.empty((FAMILIES, REPS))
    absfix = np.empty((FAMILIES, REPS))
    for f in range(FAMILIES):
        CAs = draw_struct_totals(gen(struct_purpose, f), mod, khat, (REPS,))
        C_R, SEs = se_of(T[f], Q[f])
        ks = CAs / C_R
        dev[f] = (ks - khat) / SEs
        absfix[f] = np.abs(ks - khat) / SE
    out = {"reading": reading, "bank_purpose": bank_purpose, "struct_purpose": struct_purpose,
           "families": FAMILIES, "reps_per_family": REPS,
           "kappa_hat": khat, "kappa_hat_lt_1": khat < 1, "SE": SE, "C_A": CA, "three_C_R": T3,
           "branch": "binomial thinning (kappa_hat < 1)" if khat < 1 else ("null as drawn" if khat == 1 else "Poisson-planted excess"),
           "rho1_hat_b": mod["rho1_hat_b"], "D_b": mod["D_b"], "D_hat_b_raw": mod["D_hat_b_raw"],
           "dev_mean": float(dev.mean()), "dev_sd": float(dev.std())}
    out.update(bounds_from(dev, np.abs(dev), absfix, khat, SE))
    json.dump(out, open(os.path.join(outdir, f"observed_{reading}_{bank_purpose}.json"), "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("reading", "kappa_hat", "U_signed_Q1", "U_absdev_Q1", "mc_se")}))


def cmd_designs(indir, outdir):
    curves, _ = load(indir)
    mod = model(curves, "adopted")
    t0 = time.time()
    res = {}
    for i, kt in enumerate(KAPPAS):
        Ts = np.empty((FAMILIES, DESIGNS), dtype=np.int64)
        Qs = np.empty((FAMILIES, DESIGNS), dtype=np.int64)
        CAs = np.empty((FAMILIES, DESIGNS), dtype=np.int64)
        for f in range(FAMILIES):
            rng = gen(10 + i, f)
            Ts[f], Qs[f] = draw_randoms(rng, mod, DESIGNS)
            CAs[f] = draw_struct_totals(rng, mod, kt, (DESIGNS,))
        res[f"T_{i}"], res[f"Q_{i}"], res[f"CA_{i}"] = Ts, Qs, CAs
    np.savez_compressed(os.path.join(outdir, "designs.npz"), **res)
    print("designs", time.time() - t0)


def cmd_coverage(indir, outdir, bank_purpose, inner_base):
    curves, _ = load(indir)
    mod = model(curves, "adopted")
    bk = np.load(os.path.join(outdir, f"bank_adopted_{bank_purpose}.npz"))
    T, Q = bk["T"], bk["Q"]
    C_Rb, SEb = se_of(T, Q)                     # (FAMILIES, REPS)
    ds = np.load(os.path.join(outdir, "designs.npz"))
    t0 = time.time()
    out = {"bank_purpose": bank_purpose, "inner_seed_purposes": [inner_base + i for i in range(3)],
           "design_seed_purposes": [10 + i for i in range(3)],
           "designs_per_family": DESIGNS, "families": FAMILIES, "inner_reps": [FAMILIES, REPS],
           "kappas": {}}
    per_design = {}
    B = 16
    # plug-in quantiles at kappa_true (diagnostic C3), from the bank with seed inner_base+9
    for i, kt in enumerate(KAPPAS):
        Ts, Qs, CAs = ds[f"T_{i}"].ravel(), ds[f"Q_{i}"].ravel(), ds[f"CA_{i}"].ravel()
        C_Rs, SEs = se_of(Ts, Qs)
        kh = CAs / C_Rs
        nd = len(kh)
        Us = np.empty(nd)
        Ua = np.empty(nd)
        Uf = np.empty(nd)
        rng = gen(inner_base + i, 0)
        for s0 in range(0, nd, B):
            sl = slice(s0, min(nd, s0 + B))
            k = kh[sl]
            exact1 = (3 * CAs[sl] == Ts[sl])
            k_eff = np.where(exact1, 1.0, k)
            tot = draw_struct_totals(rng, mod, k_eff, (len(k), FAMILIES, REPS))
            ks = tot / C_Rb[None]
            dev = (ks - k_eff[:, None, None]) / SEb[None]
            qlo = np.quantile(dev, 0.05, axis=2).mean(axis=1)
            qab = np.quantile(np.abs(dev), 0.95, axis=2).mean(axis=1)
            qfx = np.quantile(np.abs(ks - k_eff[:, None, None]) / SEs[sl][:, None, None], 0.95, axis=2).mean(axis=1)
            Us[sl] = k - qlo * SEs[sl]
            Ua[sl] = k + qab * SEs[sl]
            Uf[sl] = k + qfx * SEs[sl]
        # C3 plug-in diagnostic: quantiles at kappa_true
        rngp = gen(inner_base + 9, i)
        tot = draw_struct_totals(rngp, mod, kt, (FAMILIES, REPS))
        ksp = tot / C_Rb
        devp = (ksp - kt) / SEb
        qlo_p = float(np.quantile(devp, 0.05, axis=1).mean())
        qab_p = float(np.quantile(np.abs(devp), 0.95, axis=1).mean())
        Up_s = kh - qlo_p * SEs
        Up_a = kh + qab_p * SEs

        def cov(U):
            c = float(np.mean(U >= kt))
            return {"coverage": c, "mc_se": math.sqrt(c * (1 - c) / nd),
                    "per_family": [float(np.mean(U.reshape(FAMILIES, DESIGNS)[f] >= kt)) for f in range(FAMILIES)]}

        out["kappas"][f"{kt:.2f}"] = {
            "designs": nd, "kappa_hat_mean": float(kh.mean()), "kappa_hat_sd": float(kh.std()),
            "share_kappa_hat_lt_1": float(np.mean(kh < 1)),
            "signed": cov(Us), "absdev_AB1": cov(Ua), "absdev_AB2_fixedSE": cov(Uf),
            "plug_in_C3_signed": cov(Up_s), "plug_in_C3_absdev": cov(Up_a),
            "plug_in_quantiles": {"q_lo": qlo_p, "q_abs": qab_p},
            "U_signed_median": float(np.median(Us)), "U_absdev_median": float(np.median(Ua)),
        }
        per_design[f"kh_{i}"], per_design[f"Us_{i}"], per_design[f"Ua_{i}"] = kh, Us, Ua
        print(i, kt, out["kappas"][f"{kt:.2f}"]["signed"]["coverage"],
              out["kappas"][f"{kt:.2f}"]["absdev_AB1"]["coverage"], time.time() - t0, flush=True)
    out["seconds"] = time.time() - t0
    json.dump(out, open(os.path.join(outdir, f"coverage_bank{bank_purpose}.json"), "w"), indent=1)
    np.savez_compressed(os.path.join(outdir, f"coverage_bank{bank_purpose}_designs.npz"), **per_design)


if __name__ == "__main__":
    indir, outdir, cmd = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(outdir, exist_ok=True)
    a = sys.argv[4:]
    if cmd == "bank":
        cmd_bank(indir, outdir, a[0], int(a[1]))
    elif cmd == "observed":
        cmd_observed(indir, outdir, a[0], int(a[1]), int(a[2]))
    elif cmd == "designs":
        cmd_designs(indir, outdir)
    elif cmd == "coverage":
        cmd_coverage(indir, outdir, int(a[0]), int(a[1]))
    else:
        raise SystemExit("unknown command")
