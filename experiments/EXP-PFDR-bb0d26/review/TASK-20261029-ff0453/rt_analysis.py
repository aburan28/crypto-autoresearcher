#!/usr/bin/env python3
"""Red-team (TASK-20261029-ff0453, joint J5 + proves_too_much) computations on RECORDED data only.

Inputs (read only):
  experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-4d8c71/toy-main-jobs.jsonl   (job records)
  experiments/EXP-PFDR-bb0d26/runs/RUN-PFDR-089edc/analysis.json         (hash-bound reading)
No new curve, set, label or count is generated.  Every bootstrap / resampling here is a reviewer
resampling of recorded per-curve counts with a declared seed (sha256 of a label string).

Output: rt_analysis.json (summary) and rt_cells.json (per-cell tables) next to this script.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from collections import defaultdict

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
EXPD = os.path.join(ROOT, "experiments", "EXP-PFDR-bb0d26")
JOBS = os.path.join(EXPD, "runs", "RUN-PFDR-4d8c71", "toy-main-jobs.jsonl")
ANA = os.path.join(EXPD, "runs", "RUN-PFDR-089edc", "analysis.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rt_analysis.json")
TASK = "TASK-20261029-ff0453"
NREP = 20
B_MAIN = 2000          # bootstrap resamples (same count as the frozen contract)
B_MIX = 1000           # resamples per draw in the attenuated-plant sensitivity
MIX_DRAWS = 200


def seed_of(*labels) -> int:
    d = hashlib.sha256("|".join(map(str, (TASK,) + labels)).encode()).digest()
    return int.from_bytes(d[:8], "big")


def Phi(x: float) -> float:
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def two_sided_p(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def gammaincc(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x) (series / continued fraction, NR style)."""
    if x <= 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1.0:
        ap, s, d = a, 1.0 / a, 1.0 / a
        for _ in range(10000):
            ap += 1.0
            d *= x / ap
            s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return 1.0 - s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(x: float, k: int) -> float:
    return gammaincc(k / 2.0, x / 2.0)


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k), X ~ Bin(n, p)."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def rnd(x, d=6):
    if x is None:
        return None
    if isinstance(x, float):
        if x == 0 or not math.isfinite(x):
            return x
        return float(f"{x:.{d}g}")
    return x


# --------------------------------------------------------------------------- load
ana = json.load(open(ANA))
acells = {c["cell"]: c for c in ana["cells"]}
order = [c["cell"] for c in ana["cells"]]
recs = [json.loads(line) for line in open(JOBS)]
by = defaultdict(dict)
nonok = []
for r in recs:
    if r["status"] != "ok":
        nonok.append(r)
        continue
    nc = acells[r["cell"]]["n_curves"]
    if 0 <= r["c"] < nc and r["c"] not in by[r["cell"]]:
        by[r["cell"]][r["c"]] = r

CELL = {}
for cid in order:
    a = acells[cid]
    rs = [by[cid][c] for c in sorted(by[cid])]
    d = {"a": a, "c": np.array([r["c"] for r in rs]),
         "g": np.array([r["gap_C"] for r in rs], dtype=np.float64),
         "N0": np.array([r["null_C"] for r in rs], dtype=np.float64),
         "pl": np.array([r["plant_C"] for r in rs], dtype=np.float64),
         "dup": np.array([r["gap_meta"]["duplicate_skips"] for r in rs]),
         "inf": np.array([r["gap_meta"]["infinity_skips"] for r in rs]),
         "p": np.array([r["p"] for r in rs], dtype=np.float64),
         "n": a["n"], "bits": a["bits"], "r": a["r"]}
    CELL[cid] = d

powered = [cid for cid in order if acells[cid].get("powered")]
assert len(powered) == 44, len(powered)

out = {"task": TASK, "interpreter": {"version": sys.version, "executable": sys.executable,
                                      "numpy": np.__version__},
       "inputs": {"jobs": os.path.relpath(JOBS, ROOT), "analysis": os.path.relpath(ANA, ROOT),
                  "jobs_sha256": hashlib.sha256(open(JOBS, "rb").read()).hexdigest(),
                  "analysis_sha256": hashlib.sha256(open(ANA, "rb").read()).hexdigest(),
                  "records": len(recs), "non_ok": len(nonok)}}

# --------------------------------------------------------------------------- 0. consistency with the record
def stats(d):
    g, N0 = d["g"], d["N0"]
    m = N0.mean(1)
    v = N0.var(1, ddof=1)
    S, M, V = g.sum(), m.sum(), v.sum()
    z = (S - M) / math.sqrt(V * (1 + 1 / NREP))
    m19 = N0[:, 1:].mean(1)
    v19 = N0[:, 1:].var(1, ddof=1)
    zc = (N0[:, 0].sum() - m19.sum()) / math.sqrt(v19.sum() * (1 + 1 / (NREP - 1)))
    Pl = d["pl"].sum()
    ev = d["c"] % 2 == 0
    return {"S": S, "M": M, "V": V, "kappa": S / M, "z": z, "z_cal": zc,
            "plant_kappa": Pl / M, "plant_z": (Pl - M) / math.sqrt(V * (1 + 1 / NREP)),
            "kappa_even": g[ev].sum() / m[ev].sum(), "kappa_odd": g[~ev].sum() / m[~ev].sum()}


maxrel = 0.0
worst = None
for cid in powered:
    st = stats(CELL[cid])
    CELL[cid]["st"] = st
    for k, v in st.items():
        rec = acells[cid][k]
        rel = abs(v - rec) / max(abs(rec), 1e-300) if k not in ("z", "z_cal") else abs(v - rec)
        if rel > maxrel:
            maxrel, worst = rel, (cid, k)
out["consistency_with_analysis_json"] = {
    "fields": ["S", "M", "V", "kappa", "z(abs)", "z_cal(abs)", "plant_kappa", "plant_z(abs)", "kappa_even", "kappa_odd"],
    "max_rel_or_abs_diff": maxrel, "at": worst,
    "note": "reviewer recomputation from job records equals the recorded per-cell values (float rounding only); "
            "this is a consistency check that the reviewer reads the same data, not the blind re-derivation of J4"}


# --------------------------------------------------------------------------- 1. power per powered cell
def boot_idx_counts(n, B, seed):
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    W = np.zeros((B, n), dtype=np.float64)
    np.add.at(W, (np.repeat(np.arange(B), n), idx.ravel()), 1.0)
    return W


def pct_ci(bs):
    bs = np.sort(bs)
    L = len(bs)
    return [float(bs[int(0.025 * L)]), float(bs[int(0.975 * L) - 1])]


def classify(k, z, ci, planted=True, powered_=True):
    if not powered_:
        return "inconclusive_underpowered"
    if not planted:
        return "inconclusive_plant_not_recovered"
    if abs(k - 1) >= 0.10 and abs(z) > 4.0:
        return "flagged"
    if abs(k - 1) < 0.05 and ci is not None and 0.90 <= ci[0] and ci[1] <= 1.10:
        return "null"
    return "intermediate"


power = []
for cid in powered:
    d, a, st = CELL[cid], acells[cid], CELL[cid]["st"]
    lo, hi = a["ci95"]
    M, V = st["M"], st["V"]
    m = d["N0"].mean(1)
    v = d["N0"].var(1, ddof=1)
    sd_z = math.sqrt(V * (1 + 1 / NREP)) / M          # sd of kappa-hat implied by z's variance model
    sd_b = (hi - lo) / (2 * 1.959964)                 # sd implied by the recorded bootstrap interval
    sd = max(sd_z, sd_b)
    mde_z4 = 4 * sd_z                                  # observed |kappa-1| at which |z| crosses 4
    thr = max(0.10, mde_z4)
    hw_rel = (hi - lo) / 2 / st["kappa"]
    # probability that the frozen class rule reads 'null' if the true kappa is 1 (normal approx; CI side
    # condition is non-binding when 0.05 + half-width < 0.10)
    p_null_H1 = 2 * Phi(0.05 / sd) - 1
    power.append({
        "cell": cid, "curves": int(len(d["g"])), "M": rnd(M, 8), "V_over_M": rnd(V / M, 4),
        "per_curve_var_over_mean_median": rnd(float(np.median(v / m)), 4),
        "per_curve_var_over_mean_iqr": [rnd(float(np.percentile(v / m, 25)), 3), rnd(float(np.percentile(v / m, 75)), 3)],
        "kappa": rnd(st["kappa"], 6), "ci95": [rnd(lo, 6), rnd(hi, 6)],
        "ci_rel_halfwidth": rnd(hw_rel, 4), "sd_kappa_from_V": rnd(sd_z, 4), "sd_kappa_from_ci": rnd(sd_b, 4),
        "ci_over_V_sd_ratio": rnd(sd_b / sd_z, 3),
        "mde_abs_kappa_minus_1_at_absz_gt_4": rnd(mde_z4, 4),
        "flag_rule_nonvacuous_at_0p10": bool(mde_z4 < 0.10),
        "z_at_observed_10pct": rnd(0.10 / sd_z, 3),
        "power_flag_true_0p10": rnd(Phi((0.10 - thr) / sd), 3),
        "true_delta_for_80pct_flag": rnd(thr + 0.841621 * sd, 4),
        "true_delta_excluded_from_null_at_95pct": rnd(0.05 + 1.644854 * sd, 4),
        "p_null_given_kappa_1": rnd(p_null_H1, 6),
        "p_null_given_true_0p10": rnd(Phi((0.05 - 0.10) / sd) , 3),
        "band_side_condition_binding": bool(0.05 + max(hi - st["kappa"], st["kappa"] - lo) >= 0.10),
    })
out["power"] = power
wk = max(power, key=lambda r: r["mde_abs_kappa_minus_1_at_absz_gt_4"])
wid = max(power, key=lambda r: r["ci_rel_halfwidth"])
out["power_summary"] = {
    "min_M": min(power, key=lambda r: r["M"])["cell"] + " " + str(min(r["M"] for r in power)),
    "widest_ci_rel_halfwidth": {"cell": wid["cell"], "value": wid["ci_rel_halfwidth"]},
    "largest_mde_at_absz_gt_4": {"cell": wk["cell"], "value": wk["mde_abs_kappa_minus_1_at_absz_gt_4"],
                                 "true_delta_excluded_from_null_at_95pct": wk["true_delta_excluded_from_null_at_95pct"],
                                 "power_flag_true_0p10": wk["power_flag_true_0p10"],
                                 "true_delta_for_80pct_flag": wk["true_delta_for_80pct_flag"]},
    "V_over_M_range": [min(r["V_over_M"] for r in power), max(r["V_over_M"] for r in power)],
    "cells_flag_rule_vacuous_at_0p10": [r["cell"] for r in power if not r["flag_rule_nonvacuous_at_0p10"]],
    "cells_band_side_condition_binding": [r["cell"] for r in power if r["band_side_condition_binding"]],
    "max_ci_over_V_sd_ratio": max(r["ci_over_V_sd_ratio"] for r in power),
    "min_ci_over_V_sd_ratio": min(r["ci_over_V_sd_ratio"] for r in power),
}

# --------------------------------------------------------------------------- 2. distribution of the gap-arm z and of z_cal
zs = np.array([CELL[c]["st"]["z"] for c in powered])
zc = np.array([CELL[c]["st"]["z_cal"] for c in powered])
n44 = len(zs)


def zsummary(arr, tag):
    chi2 = float((arr ** 2).sum())
    p2, p3 = 2 * (1 - Phi(2)), 2 * (1 - Phi(3))
    k2, k3 = int((np.abs(arr) > 2).sum()), int((np.abs(arr) > 3).sum())
    mx = float(np.abs(arr).max())
    pind = 1 - (1 - two_sided_p(mx)) ** len(arr)
    return {"arm": tag, "n": len(arr), "mean": rnd(float(arr.mean()), 4), "pop_sd": rnd(float(arr.std()), 4),
            "rms": rnd(math.sqrt(chi2 / len(arr)), 4), "sum_z2": rnd(chi2, 5),
            "p_chi2_upper": rnd(chi2_sf(chi2, len(arr)), 3),
            "count_absz_gt_2": k2, "expected_gt_2": rnd(len(arr) * p2, 3), "p_binom_ge_gt_2": rnd(binom_sf(k2, len(arr), p2), 3),
            "count_absz_gt_3": k3, "expected_gt_3": rnd(len(arr) * p3, 3), "p_binom_ge_gt_3": rnd(binom_sf(k3, len(arr), p3), 3),
            "max_absz": rnd(mx, 4), "p_max_ge_obs_independent": rnd(pind, 3),
            "would_pass_calibration_band": bool(0.75 <= arr.std() <= 1.25 and abs(arr.mean()) <= 0.35)}


zd = {"gap_z": zsummary(zs, "gap (log-GAP vs null)"), "z_cal": zsummary(zc, "null rep 0 vs reps 1..19")}
strata = {}
for key, fn in (("r", lambda c: CELL[c]["r"]), ("bits", lambda c: CELL[c]["bits"]), ("n", lambda c: CELL[c]["n"])):
    grp = defaultdict(list)
    for c in powered:
        grp[fn(c)].append(CELL[c]["st"]["z"])
    strata[key] = {str(k): {"cells": len(v), "mean_z": rnd(float(np.mean(v)), 3),
                            "stouffer": rnd(float(np.sum(v) / math.sqrt(len(v))), 3),
                            "p_two_sided": rnd(two_sided_p(float(np.sum(v) / math.sqrt(len(v)))), 3),
                            "sum_z2": rnd(float(np.sum(np.square(v))), 4)} for k, v in sorted(grp.items())}
zd["gap_z_strata_post_hoc"] = strata
zd["cells_with_ci_excluding_1"] = [c for c in powered if acells[c]["ci95"][0] > 1 or acells[c]["ci95"][1] < 1]
zd["expected_ci_excluding_1"] = rnd(0.05 * n44, 3)
out["z_distribution"] = zd

# --------------------------------------------------------------------------- 3. within-cell second moment (variance of gap vs null)
sm = []
num_g = den_g = num_a = den_a = 0.0
t2g_all, t2a_all = [], []
for cid in powered:
    d = CELL[cid]
    N0, g = d["N0"], d["g"]
    m, v = N0.mean(1), N0.var(1, ddof=1)
    m19, v19 = N0[:, 1:].mean(1), N0[:, 1:].var(1, ddof=1)
    eg = g - m
    ea = N0[:, 0] - m19
    Rg = float((eg ** 2).sum() / ((1 + 1 / NREP) * v.sum()))
    Ra = float((ea ** 2).sum() / ((1 + 1 / (NREP - 1)) * v19.sum()))
    # z^2 = R + cross-curve term; cross term isolates a common (cell-level) shift
    z2 = CELL[cid]["st"]["z"] ** 2
    tg = eg / np.sqrt((1 + 1 / NREP) * v)
    ta = ea / np.sqrt((1 + 1 / (NREP - 1)) * v19)
    t2g_all.append(tg ** 2)
    t2a_all.append(ta ** 2)
    sm.append({"cell": cid, "R_gap": rnd(Rg, 4), "R_aa": rnd(Ra, 4), "z2": rnd(z2, 4),
               "z2_minus_R_gap(cross-curve)": rnd(z2 - Rg, 4),
               "mean_t2_gap": rnd(float((tg ** 2).mean()), 4), "mean_t2_aa": rnd(float((ta ** 2).mean()), 4)})
t2g = np.concatenate(t2g_all)
t2a = np.concatenate(t2a_all)
# curve-cluster bootstrap of the pooled mean t^2 difference
rng = np.random.default_rng(seed_of("t2diff"))
diff = t2g - t2a
bs = np.array([diff[rng.integers(0, len(diff), len(diff))].mean() for _ in range(2000)])
out["second_moment"] = {
    "per_cell": sm,
    "pooled_mean_t2_gap": rnd(float(t2g.mean()), 5), "pooled_mean_t2_aa": rnd(float(t2a.mean()), 5),
    "pooled_curves": int(len(t2g)),
    "pooled_mean_t2_diff_gap_minus_aa": rnd(float(diff.mean()), 4), "diff_ci95_curve_bootstrap": [rnd(x, 4) for x in pct_ci(bs)],
    "median_R_gap": rnd(float(np.median([s["R_gap"] for s in sm])), 4),
    "median_R_aa": rnd(float(np.median([s["R_aa"] for s in sm])), 4),
    "sum_z2_minus_R_gap_over_cells": rnd(float(sum(s["z2_minus_R_gap(cross-curve)"] for s in sm)), 4),
    "note": "t = per-curve standardized residual; for Student-t with 19 (gap) / 18 (aa) df E[t^2] is 1.118 / 1.125; "
            "R = sum of squared per-curve residuals over (variance factor x sum of per-curve null variances), E[R]=1 "
            "under exchangeability of the arm with the null replicates"}

# --------------------------------------------------------------------------- 4. cross-cell correlation from shared curves
def resid(cid, arm):
    d = CELL[cid]
    N0 = d["N0"]
    if arm == "gap":
        return d["c"], (d["g"] - N0.mean(1)) / np.sqrt((1 + 1 / NREP) * N0.var(1, ddof=1))
    m19, v19 = N0[:, 1:].mean(1), N0[:, 1:].var(1, ddof=1)
    return d["c"], (N0[:, 0] - m19) / np.sqrt((1 + 1 / (NREP - 1)) * v19)


corr = {}
for arm in ("gap", "aa"):
    per_bits = {}
    allz = []
    for bits in (20, 24, 28):
        cs = [c for c in powered if CELL[c]["bits"] == bits]
        rhos, fz = [], []
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                ci_, ri = resid(cs[i], arm)
                cj_, rj = resid(cs[j], arm)
                shared = np.intersect1d(ci_, cj_)
                xi = ri[np.searchsorted(ci_, shared)]
                xj = rj[np.searchsorted(cj_, shared)]
                rho = float(np.corrcoef(xi, xj)[0, 1])
                rhos.append(rho)
                fz.append(math.atanh(rho) * math.sqrt(len(shared) - 3))
        allz += fz
        per_bits[str(bits)] = {"pairs": len(rhos), "mean_rho": rnd(float(np.mean(rhos)), 4),
                               "sd_rho": rnd(float(np.std(rhos)), 4),
                               "fisher_z_mean": rnd(float(np.mean(fz)), 4), "fisher_z_sd": rnd(float(np.std(fz)), 4),
                               "max_abs_rho": rnd(float(np.max(np.abs(rhos))), 4)}
    allz = np.array(allz)
    corr[arm] = {"per_bits": per_bits, "fisher_z_mean_all_pairs": rnd(float(allz.mean()), 4),
                 "fisher_z_sd_all_pairs": rnd(float(allz.std()), 4),
                 "note": "Fisher z of per-pair curve-residual correlation scaled by sqrt(n_shared - 3); "
                         "N(0,1) per pair if curves carry no shared component (pairs are not independent)"}
out["shared_curve_correlation"] = corr

# simulation of tail check and calibration gate under within-bits equicorrelation of cell z
bits_of = np.array([CELL[c]["bits"] for c in powered])


def sim(rho, sdz=1.0, mu=0.0, n_sim=100000, seed_label="sim"):
    rng = np.random.default_rng(seed_of(seed_label, rho, sdz, mu))
    Z = rng.standard_normal((n_sim, n44)) * math.sqrt(1 - rho)
    for b in (20, 24, 28):
        sel = bits_of == b
        Z[:, sel] += math.sqrt(rho) * rng.standard_normal((n_sim, 1))
    Z = Z * sdz + mu
    mx = np.abs(Z).max(1)
    sd = Z.std(1)
    mn = Z.mean(1)
    gate = (sd >= 0.75) & (sd <= 1.25) & (np.abs(mn) <= 0.35)
    return {"rho_within_bits": rho, "true_sd": sdz, "true_mean": mu,
            "E_max_absz": rnd(float(mx.mean()), 4), "P_max_absz_ge_3.1315": rnd(float((mx >= 3.13146).mean()), 4),
            "P_count_gt3_ge_1": rnd(float(((np.abs(Z) > 3).sum(1) >= 1).mean()), 4),
            "P_count_gt2_ge_6": rnd(float(((np.abs(Z) > 2).sum(1) >= 6).mean()), 4),
            "P_sum_z2_ge_obs": rnd(float(((Z ** 2).sum(1) >= float((zs ** 2).sum())).mean()), 4),
            "sd_of_mean": rnd(float(mn.std()), 4), "sd_of_sample_sd": rnd(float(sd.std()), 4),
            "P_gate_pass": rnd(float(gate.mean()), 4),
            "P_abs_mean_ge_0.2676": rnd(float((np.abs(mn) >= 0.26757).mean()), 4)}


out["tail_and_gate_simulation"] = {
    "null_calibrated": [sim(r) for r in (0.0, 0.05, 0.1, 0.3)],
    "gate_power_against_miscalibration": [sim(0.0, s, m_) for s, m_ in ((1.3, 0.0), (1.5, 0.0), (0.7, 0.0), (1.0, 0.4), (1.27, 0.1))],
    "note": "44 cells in 3 bits-blocks (14/15/15), z within a block equicorrelated at rho; 100000 seeded draws"}

# --------------------------------------------------------------------------- 5. A/A comparisons under the frozen rule
aa_rep0, aa_loo, aa_eo = [], [], []
cnt = defaultdict(int)
for cid in powered:
    d = CELL[cid]
    N0 = d["N0"]
    n = len(d["g"])
    W = boot_idx_counts(n, B_MAIN, seed_of("aa", cid))
    tot = N0.sum(1)
    # leave-one-replicate-out j = 0..19 (j = 0 is C-aa-null as specified)
    WN = W @ N0                       # (B, 20) bootstrap sums of each replicate
    Wt = W @ tot                      # (B,)
    for j in range(NREP):
        s_j = N0[:, j]
        oth = np.delete(N0, j, axis=1)
        m_o, v_o = oth.mean(1), oth.var(1, ddof=1)
        S, M, V = s_j.sum(), m_o.sum(), v_o.sum()
        k = S / M
        z = (S - M) / math.sqrt(V * (1 + 1 / (NREP - 1)))
        bk = WN[:, j] / ((Wt - WN[:, j]) / (NREP - 1))
        ci = pct_ci(bk)
        cls = classify(k, z, ci)
        cnt[("loo", cls)] += 1
        cnt[("loo", "absz>3")] += int(abs(z) > 3)
        cnt[("loo", "absz>4")] += int(abs(z) > 4)
        cnt[("loo", "absz>2")] += int(abs(z) > 2)
        if j == 0:
            aa_rep0.append({"cell": cid, "kappa": rnd(k, 6), "z": rnd(z, 4), "ci95": [rnd(x, 6) for x in ci],
                            "cls": cls, "z_equals_recorded_z_cal": bool(abs(z - acells[cid]["z_cal"]) < 1e-9)})
    # even vs odd curve kappa (C-aa-curves): ratio kappa_even / kappa_odd
    ev = d["c"] % 2 == 0
    m, v = N0.mean(1), N0.var(1, ddof=1)
    ke = d["g"][ev].sum() / m[ev].sum()
    ko = d["g"][~ev].sum() / m[~ev].sum()
    var_e = (1 + 1 / NREP) * v[ev].sum() / m[ev].sum() ** 2
    var_o = (1 + 1 / NREP) * v[~ev].sum() / m[~ev].sum() ** 2
    ratio = ke / ko
    zeo = (ke - ko) / math.sqrt(var_e + var_o)
    rng = np.random.default_rng(seed_of("eo", cid))
    ie, io = np.where(ev)[0], np.where(~ev)[0]
    be = rng.integers(0, len(ie), (B_MAIN, len(ie)))
    bo = rng.integers(0, len(io), (B_MAIN, len(io)))
    ge, me = d["g"][ie], m[ie]
    go, mo = d["g"][io], m[io]
    br = (ge[be].sum(1) / me[be].sum(1)) / (go[bo].sum(1) / mo[bo].sum(1))
    ci = pct_ci(br)
    cls = classify(ratio, zeo, ci)
    cnt[("eo", cls)] += 1
    cnt[("eo", "absz>3")] += int(abs(zeo) > 3)
    cnt[("eo", "absz>2")] += int(abs(zeo) > 2)
    aa_eo.append({"cell": cid, "kappa_even": rnd(ke, 6), "kappa_odd": rnd(ko, 6), "ratio": rnd(ratio, 6),
                  "z": rnd(zeo, 4), "ci95_ratio": [rnd(x, 6) for x in ci], "cls": cls,
                  "even_odd_equal_recorded": bool(abs(ke - acells[cid]["kappa_even"]) < 1e-12 and abs(ko - acells[cid]["kappa_odd"]) < 1e-12)})
zeo_arr = np.array([r["z"] for r in aa_eo])
out["aa_comparisons"] = {
    "C_aa_null_rep0_vs_1_19": {"per_cell": aa_rep0,
                               "classes": {k: sum(1 for r in aa_rep0 if r["cls"] == k) for k in ("flagged", "intermediate", "null")}},
    "C_aa_null_leave_one_replicate_out": {
        "comparisons": 44 * NREP,
        "classes": {k: cnt[("loo", k)] for k in ("flagged", "intermediate", "null")},
        "count_absz_gt_2": cnt[("loo", "absz>2")], "expected_gt_2": rnd(44 * NREP * 2 * (1 - Phi(2)), 4),
        "count_absz_gt_3": cnt[("loo", "absz>3")], "expected_gt_3": rnd(44 * NREP * 2 * (1 - Phi(3)), 4),
        "count_absz_gt_4": cnt[("loo", "absz>4")], "expected_gt_4": rnd(44 * NREP * 2 * (1 - Phi(4)), 4),
        "note": "replicates of one curve share that curve; the 20 comparisons per cell are not independent"},
    "C_aa_curves_even_vs_odd": {"per_cell": aa_eo,
                                "classes": {k: cnt[("eo", k)] for k in ("flagged", "intermediate", "null")},
                                "count_absz_gt_2": cnt[("eo", "absz>2")], "count_absz_gt_3": cnt[("eo", "absz>3")],
                                "sum_z2": rnd(float((zeo_arr ** 2).sum()), 4),
                                "p_chi2_upper": rnd(chi2_sf(float((zeo_arr ** 2).sum()), 44), 3),
                                "pop_sd_z": rnd(float(zeo_arr.std()), 4)},
    "nominal_flag_rate_per_comparison": "two-sided |z|>4 alone: 6.3e-5; with |kappa-1| >= 0.10 lower still",
}

# --------------------------------------------------------------------------- 6. plant arm under the frozen class rule
plant = []
for cid in powered:
    d = CELL[cid]
    N0 = d["N0"]
    n = len(d["g"])
    m = N0.mean(1)
    W = boot_idx_counts(n, B_MAIN, seed_of("plant", cid))
    bk = (W @ d["pl"]) / (W @ m)
    ci = pct_ci(bk)
    st = d["st"]
    cls = classify(st["plant_kappa"], st["plant_z"], ci)
    plant.append({"cell": cid, "plant_kappa": rnd(st["plant_kappa"], 5), "plant_z": rnd(st["plant_z"], 4),
                  "ci95": [rnd(x, 5) for x in ci], "cls_if_read_as_structured_arm": cls,
                  "plant_m_median_over_n": rnd(float(np.median([by[cid][c]["plant_m"] for c in by[cid]])) / d["n"], 4)})
out["plant_arm_under_class_rule"] = {
    "per_cell": plant,
    "classes": {k: sum(1 for r in plant if r["cls_if_read_as_structured_arm"] == k) for k in ("flagged", "intermediate", "null")},
    "min_ci_lower": min(r["ci95"][0] for r in plant)}

# --------------------------------------------------------------------------- 7. attenuated-plant sensitivity on recorded counts
#     On each curve the 'structured' count is the recorded plant_C with probability q, else the recorded
#     null replicate 0; the comparison null is replicates 1..19.  q = delta / (plant_kappa - 1).  This is a
#     resampling of recorded counts (no new set): a heterogeneous excess of mean size delta.
mix = []
for cid in powered:
    d = CELL[cid]
    N0 = d["N0"]
    n = len(d["g"])
    m19, v19 = N0[:, 1:].mean(1), N0[:, 1:].var(1, ddof=1)
    M, V = m19.sum(), v19.sum()
    excess = d["pl"].sum() / M - 1
    W = boot_idx_counts(n, B_MIX, seed_of("mixW", cid))
    WM = W @ m19
    row = {"cell": cid}
    for delta in (0.05, 0.075, 0.10):
        q = min(1.0, delta / excess)
        rng = np.random.default_rng(seed_of("mix", cid, delta))
        res = defaultdict(int)
        for _ in range(MIX_DRAWS):
            pick = rng.random(n) < q
            s = np.where(pick, d["pl"], N0[:, 0])
            S = s.sum()
            k = S / M
            z = (S - M) / math.sqrt(V * (1 + 1 / (NREP - 1)))
            ci = pct_ci((W @ s) / WM)
            res[classify(k, z, ci)] += 1
        row[f"delta_{delta}"] = {c: res[c] / MIX_DRAWS for c in ("null", "intermediate", "flagged")}
    mix.append(row)
out["attenuated_plant_sensitivity"] = {
    "draws_per_cell_and_delta": MIX_DRAWS, "bootstrap_resamples": B_MIX, "per_cell": mix,
    "max_P_null_at_delta_0.10": max(r["delta_0.1"]["null"] for r in mix),
    "cell_max_P_null_at_delta_0.10": max(mix, key=lambda r: r["delta_0.1"]["null"])["cell"],
    "max_P_null_at_delta_0.075": max(r["delta_0.075"]["null"] for r in mix),
    "cell_max_P_null_at_delta_0.075": max(mix, key=lambda r: r["delta_0.075"]["null"])["cell"],
    "min_P_flag_at_delta_0.10": min(r["delta_0.1"]["flagged"] for r in mix),
    "cell_min_P_flag_at_delta_0.10": min(mix, key=lambda r: r["delta_0.1"]["flagged"])["cell"]}

# --------------------------------------------------------------------------- 8. short-relation (duplicate-skip) curves
dup_rows = []
tdup, tnodup = [], []
for cid in powered:
    d = CELL[cid]
    if d["r"] == 1:
        assert d["dup"].sum() == 0
        continue
    N0 = d["N0"]
    m, v = N0.mean(1), N0.var(1, ddof=1)
    has = d["dup"] > 0
    t = (d["g"] - m) / np.sqrt((1 + 1 / NREP) * v)
    tdup += list(t[has])
    tnodup += list(t[~has])
    row = {"cell": cid, "curves_with_dup": int(has.sum()), "max_dup": int(d["dup"].max()),
           "curves_with_inf_skip": int((d["inf"] > 0).sum())}
    if has.sum():
        S, M_, V_ = d["g"][has].sum(), m[has].sum(), v[has].sum()
        row.update(kappa_dup_subset=rnd(S / M_, 5), z_dup_subset=rnd((S - M_) / math.sqrt(V_ * 1.05), 3))
    dup_rows.append(row)
tdup, tnodup = np.array(tdup), np.array(tnodup)
out["short_relation_curves"] = {
    "per_cell_r2_r3": dup_rows,
    "pooled_curves_with_dup": int(len(tdup)),
    "pooled_mean_t_dup": rnd(float(tdup.mean()), 4) if len(tdup) else None,
    "pooled_stouffer_dup": rnd(float(tdup.sum() / math.sqrt(len(tdup) * 19 / 17)), 3) if len(tdup) else None,
    "pooled_mean_t_nodup_r2_r3": rnd(float(tnodup.mean()), 4),
    "note": "duplicate_skips > 0 means two half-box vectors gave the same label, i.e. a short integer relation "
            "among P_1..P_r (c - c' or c + c' kills the point); r = 1 cannot have one for n < N/2"}

# --------------------------------------------------------------------------- 9. invalid cell
inv = "b20-r3-n4096"
d = CELL[inv]
N0 = d["N0"]
m, v = N0.mean(1), N0.var(1, ddof=1)
S, M_, V_ = d["g"].sum(), m.sum(), v.sum()
out["invalid_cell"] = {
    "cell": inv, "ok_curves": int(len(d["g"])), "n_curves": acells[inv]["n_curves"],
    "degenerate_jobs": [{"c": r["c"], "p": r["p"], "N": r["N"], "gap_meta": r["gap_meta"]} for r in nonok],
    "half_box": {"T": 10, "size": (21 ** 3 - 1) // 2, "labels_needed": -(-(102 * 4096) // 100) + 8},
    "ok_curves_with_dup": int((d["dup"] > 0).sum()), "ok_curves_max_dup": int(d["dup"].max()),
    "descriptive_only_46_curve_kappa": rnd(S / M_, 6), "descriptive_only_46_curve_z": rnd((S - M_) / math.sqrt(V_ * 1.05), 3),
    "warning": "NOT a reading: the 4 missing curves are exactly the point triples with a short relation "
               "(missing not at random); the frozen rule makes the cell invalid and it is never null"}

# --------------------------------------------------------------------------- 10. extra summary numbers
kd = {c: abs(acells[c]["kappa"] - 1) for c in powered}
out["extra"] = {
    "p_binom_ge_6_of_44_ci_excluding_1_at_0.05": rnd(binom_sf(len(zd["cells_with_ci_excluding_1"]), n44, 0.05), 3),
    "bonferroni_11_strata_r3": rnd(min(1.0, 11 * strata["r"]["3"]["p_two_sided"]), 3),
    "bonferroni_11_strata_n256": rnd(min(1.0, 11 * strata["n"]["256"]["p_two_sided"]), 3),
    "max_abs_kappa_minus_1_all": rnd(max(kd.values()), 4),
    "max_abs_kappa_minus_1_n_ge_1024": rnd(max(v for c, v in kd.items() if CELL[c]["n"] >= 1024), 4),
    "max_abs_kappa_minus_1_n_ge_2048": rnd(max(v for c, v in kd.items() if CELL[c]["n"] >= 2048), 4),
}

# --------------------------------------------------------------------------- write: summary and per-cell tables
cells_out = {"power": out.pop("power"),
             "second_moment": out["second_moment"].pop("per_cell"),
             "aa_rep0": out["aa_comparisons"]["C_aa_null_rep0_vs_1_19"].pop("per_cell"),
             "aa_even_odd": out["aa_comparisons"]["C_aa_curves_even_vs_odd"].pop("per_cell"),
             "plant": out["plant_arm_under_class_rule"].pop("per_cell"),
             "attenuated_plant": out["attenuated_plant_sensitivity"].pop("per_cell"),
             "short_relation": out["short_relation_curves"].pop("per_cell_r2_r3")}
json.dump(out, open(OUT, "w"), indent=1, sort_keys=False)
OUT2 = OUT.replace("rt_analysis.json", "rt_cells.json")
OUT3 = OUT.replace("rt_analysis.json", "rt_cells_sensitivity.json")
json.dump({"attenuated_plant": cells_out.pop("attenuated_plant")}, open(OUT3, "w"), separators=(",", ":"))
json.dump(cells_out, open(OUT2, "w"), separators=(",", ":"))
for f in (OUT, OUT2, OUT3):
    print("wrote", f, os.path.getsize(f), "bytes")
