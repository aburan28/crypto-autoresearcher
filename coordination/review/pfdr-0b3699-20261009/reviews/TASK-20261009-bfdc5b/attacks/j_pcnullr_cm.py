"""J-PCNULLR (3), corrected propagation of the common-mode factor. TASK-20261009-bfdc5b.

j_pcnullr.py's "admitted_f_interval_99_widest" applied the 32-bit rung's interval end to the
POOLED count; that mixes a per-rung end into a pooled factor and is not an admitted pooled
factor. This script propagates, deterministically:
  (a) a pooled common-mode factor f (same at both rungs) at the ends of the pooled 99%
      interval (raw-rate and mu_model-normalised comparisons with the 011cd0 rates the
      specification states), and against U (rho1 = 1) as the reference;
  (b) rung-specific factors at both rungs' 99% upper (and lower) ends simultaneously
      (a corner, conservative), and the same corner with Bonferroni 2.807;
  (c) the pooled factor needed to carry small_x to z = t_dec and to U_gov = 1.15, with its
      distance from the pooled estimate in SE units.
Convention: f = (null-arm rate here) / (reference rate); small_x's null = sum_b C_R_b / f_b;
V scales by the same factor; U from the bank-A q grids (signed and |dev|).
"""
import json
import math
import sys
import numpy as np
sys.path.insert(0, sys.argv[1])
import common as C

OUT = sys.argv[2]
pc = json.load(open(sys.argv[3]))
cal = json.load(open(sys.argv[4]))
t_dec = cal["t_dec"]
t_dec_producer = 2.3491939034652773
d = C.load()
A = d["cnt_small_x"].astype(float)
R = np.vstack([d[f"cnt_random_sub_r{i}"] for i in range(3)]).astype(float)
GRID = np.round(np.arange(0.80, 1.40 + 1e-9, 0.0025), 6)
QLO = np.load(f"{C.SCR}/grid_qlo_A.npy")
QAB = np.load(f"{C.SCR}/grid_qabs_A.npy")
CRb = {b: R[:, d["bits"] == b].sum() / 3 for b in C.RUNGS}
Vb = {}
for b in C.RUNGS:
    s = d["bits"] == b
    Vb[b] = R[:, s].var(axis=0, ddof=1).sum()
CA = A.sum()


def prop(f30, f32):
    CRt = CRb[30] / f30 + CRb[32] / f32
    Vt = max(Vb[30] / f30 + Vb[32] / f32, CRt)
    SD = math.sqrt(4 * Vt / 3)
    k = CA / CRt
    SE = SD / CRt
    z = (CA - CRt) / SD
    Us = k - float(np.interp(k, GRID, QLO)) * SE
    Ua = k + float(np.interp(k, GRID, QAB)) * SE
    return {"f30": f30, "f32": f32, "null_for_small_x": CRt, "kappa_rel": k, "z_A": z,
            "z_gt_t_dec_review": z > t_dec, "z_gt_t_dec_producer": z > t_dec_producer,
            "U_signed": Us, "U_absdev": Ua, "U_gov_le_1.15": max(Us, Ua) <= 1.15}


cm = pc["common_mode"]
out = {"t_dec_review": t_dec, "t_dec_producer": t_dec_producer, "a_pooled": {}, "b_per_rung_corners": {}, "c_needed": {}}
for kind in ("f_raw_99", "f_norm_99"):
    lo, hi = cm["pooled"][kind]
    out["a_pooled"][kind] = {"interval": [lo, hi], "at_lower": prop(lo, lo), "at_upper": prop(hi, hi),
                             "point": prop(cm["pooled"][kind.replace("_99", "")], cm["pooled"][kind.replace("_99", "")])}
# U as the reference: rho1_here with here-only uncertainty
rho = cm["pooled"]["rho1_here"]
se_u = math.sqrt(max(C.fit_gnbr(d)[30]["D"], C.fit_gnbr(d)[32]["D"]) / (3 * cm["pooled"]["C_R"]))
out["a_pooled"]["vs_U_rho1_eq_1"] = {"f_hat": rho, "interval": [rho * math.exp(-2.5758 * se_u), rho * math.exp(2.5758 * se_u)],
                                     "at_upper": prop(rho * math.exp(2.5758 * se_u), rho * math.exp(2.5758 * se_u))}
for kind in ("f_raw_99", "f_norm_99"):
    out["b_per_rung_corners"][kind] = {"both_upper": prop(cm["30"][kind][1], cm["32"][kind][1]),
                                       "both_lower": prop(cm["30"][kind][0], cm["32"][kind][0])}
    # Bonferroni corner: widen each rung's log-interval from 2.576 to 2.807
    fb = {}
    for b in ("30", "32"):
        pt = cm[b][kind.replace("_99", "")]
        se = math.log(cm[b][kind][1] / pt) / 2.5758
        fb[b] = pt * math.exp(2.807 * se)
    out["b_per_rung_corners"][kind]["both_upper_bonferroni"] = prop(fb["30"], fb["32"])
    # how many SE of the pooled (rung-weighted) log factor is that corner from the estimate?
    w30 = CRb[30] / (CRb[30] + CRb[32])
    g_hat = w30 * math.log(cm["30"][kind.replace("_99", "")]) + (1 - w30) * math.log(cm["32"][kind.replace("_99", "")])
    se30 = math.log(cm["30"][kind][1] / cm["30"][kind.replace("_99", "")]) / 2.5758
    se32 = math.log(cm["32"][kind][1] / cm["32"][kind.replace("_99", "")]) / 2.5758
    se_g = math.sqrt((w30 * se30) ** 2 + ((1 - w30) * se32) ** 2)
    g_c = w30 * math.log(fb["30"]) + (1 - w30) * math.log(fb["32"])
    out["b_per_rung_corners"][kind]["bonferroni_corner_distance_in_pooled_SE"] = (g_c - g_hat) / se_g
for name, t in (("review_t_dec", t_dec), ("producer_t_dec", t_dec_producer)):
    f = 1.0
    while prop(f, f)["z_A"] <= t:
        f += 0.0001
    fz = f
    f = 1.0
    while max(prop(f, f)["U_signed"], prop(f, f)["U_absdev"]) <= 1.15:
        f += 0.0001
    fu = f
    dist = {}
    for kind in ("f_raw_99", "f_norm_99"):
        pt = cm["pooled"][kind.replace("_99", "")]
        se = math.log(cm["pooled"][kind][1] / pt) / 2.5758
        dist[kind] = {"z_cross_SE": math.log(fz / pt) / se, "U_cross_SE": math.log(fu / pt) / se}
    out["c_needed"][name] = {"f_for_z_gt_t": fz, "f_for_U_gov_gt_1.15": fu, "distance_from_estimate_in_SE": dist}
C.jdump(out, OUT)
print(json.dumps(out, indent=1, default=float))
