"""J3a: power, equivalence bounds, calibration (leave-one-out), tail with cross-cell correlation, pooled strata,
and a distribution-level check (dispersion and PIT ranks) with the matched null-replicate control.

Inputs (read-only): RUN-PFDR-4d8c71/toy-main-jobs.jsonl (raw records), RUN-PFDR-089edc/analysis.json (recorded
cell values, used only for cross-checks and for the recorded ci95), RUN-PFDR-e44a19/design.json (n_curves).
Outputs: power-table.json, calibration-loo.json, tail-and-correlation.json, pooled-strata.json,
dispersion-pit.json under outputs/.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import math  # noqa: E402

import numpy as np  # noqa: E402

import common as C  # noqa: E402

Z_OBS_MAX = None  # filled from data


def chi2_sf(x, k):
    """Survival function of chi-square(k) via the regularized upper gamma (series / continued fraction)."""
    if x <= 0:
        return 1.0
    a, xx = k / 2.0, x / 2.0
    if xx < a + 1:
        s, t, n = 1.0 / a, 1.0 / a, a
        for _ in range(10000):
            n += 1
            t *= xx / n
            s += t
            if abs(t) < abs(s) * 1e-15:
                break
        return max(0.0, 1.0 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a)))
    b, c, d = xx + 1 - a, 1e300, 1.0 / (xx + 1 - a)
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-xx + a * math.log(xx) - math.lgamma(a)) * h


def main():
    recs = C.load_jobs()
    an = C.load_analysis()
    design = {c["cell"]: c for c in C.load_design()["toy_cells"]}
    rec_cells = {c["cell"]: c for c in an["cells"]}
    cells = C.by_cell(recs)
    order = [c["cell"] for c in C.load_design()["toy_cells"]]

    power_rows, cal_rows, disp_rows = [], [], []
    loo_by_k = np.zeros((0, 20))
    per_cell = {}
    maxdiff = {"kappa": 0.0, "z": 0.0, "z_cal": 0.0, "M": 0.0, "V": 0.0}
    S_int_mismatch = 0
    rank0_all = []
    rankk_all = []           # job-level rank of every replicate k among its 20 values (mid-rank)
    pit_rows = []
    for cid in order:
        d = design[cid]
        rs = cells.get(cid, [])
        rc = rec_cells[cid]
        if len(rs) < d["n_curves"]:
            power_rows.append({"cell": cid, "assessable": False, "cls_recorded": rc["cls"],
                               "reason": f"invalid: {len(rs)} ok of {d['n_curves']} main-census curves; frozen rule makes the cell invalid, so no power or equivalence bound is assessable"})
            continue
        g, m, s2, nulls = C.curve_arrays(rs)
        st = C.cell_stats_np(g, m, s2)
        # cross-check against the recorded analysis
        for k_ in ("kappa", "z", "M", "V"):
            maxdiff[k_] = max(maxdiff[k_], abs(st[k_] - rc[k_]) / max(1e-300, abs(rc[k_])))
        if int(round(st["S"])) != rc["S"]:
            S_int_mismatch += 1
        sig = st["sigma_kappa"]
        ci_rec = rc["ci95"]
        rng = C.review_np_rng("boot", cid)
        ci_mine, sd_boot = C.bootstrap_ci(g, m, 2000, rng)
        sig_b_rec = (ci_rec[1] - ci_rec[0]) / (2 * 1.959964)
        t_eff = max(C.GATES["flag_dev"], C.GATES["flag_z"] * sig)
        rows = {}
        for lab, sa in (("sigma_null", sig), ("sigma_emp", max(sig, sd_boot))):
            sa_p = sa * math.sqrt(1.10)   # Poisson-like scaling of the sd under a 10% excess
            sa_m = sa * math.sqrt(0.90)
            p_ex = C.phi((0.10 - t_eff) / sa_p)
            p_de = C.phi((0.10 - t_eff) / sa_m)
            u = min(1 + C.GATES["null_dev"], C.GATES["null_ci_hi"] - 1.959964 * sig_b_rec)
            lo = max(1 - C.GATES["null_dev"], C.GATES["null_ci_lo"] + 1.959964 * sig_b_rec)
            pn_ex = max(0.0, C.phi((u - 1.10) / sa_p) - C.phi((lo - 1.10) / sa_p))
            pn_de = max(0.0, C.phi((u - 0.90) / sa_m) - C.phi((lo - 0.90) / sa_m))
            rows[lab] = {"sigma_kappa_used": sa,
                         "flag_power_at_plus_0.10": p_ex, "flag_power_at_minus_0.10": p_de,
                         "flag_power_z_conjunct_only_at_plus_0.10": C.phi((0.10 - 4 * sig) / sa_p),
                         "delta_95_flag_excess": t_eff + 1.644854 * sa_p,
                         "delta_95_flag_deficit": t_eff + 1.644854 * sa_m,
                         "p_read_null_at_plus_0.10": pn_ex, "p_read_null_at_minus_0.10": pn_de,
                         "delta_null_hides_with_p0.05_excess": (u - 1) + 1.644854 * sa,
                         "delta_null_hides_with_p0.05_deficit": (1 - lo) + 1.644854 * sa}
            if lab == "sigma_emp":
                for k_ in ("flag_power_z_conjunct_only_at_plus_0.10", "delta_95_flag_deficit",
                           "delta_null_hides_with_p0.05_deficit"):
                    rows[lab].pop(k_)
        n_c = len(rs)
        exc_set = (st["S"] - st["M"]) / n_c
        boot_idx = C.review_np_rng("boot-exc", cid).integers(0, n_c, size=(2000, n_c))
        ex_b = np.sort((g[boot_idx] - m[boot_idx]).sum(axis=1) / n_c)
        pr = {"cell": cid, "assessable": True, "bits": d["bits"], "r": d["r"], "n": d["n"], "curves": n_c,
              "cls_recorded": rc["cls"], "S": st["S"], "M": st["M"], "V": st["V"], "kappa": st["kappa"],
              "z": st["z"], "sigma_kappa": sig, "V_over_M": st["V"] / st["M"],
              "delta_min_z_only": 4 * sig, "effective_flag_threshold": t_eff,
              "binding_conjunct": "effect size |kappa-1| >= 0.10" if t_eff == 0.10 else "|z| > 4",
              "ci95_recorded": ci_rec, "ci95_reviewer_bootstrap": ci_mine,
              "sd_kappa_bootstrap": sd_boot, "bootstrap_over_null_sd": sd_boot / sig,
              "equivalence_bound_recorded_ci": max(abs(ci_rec[0] - 1), abs(ci_rec[1] - 1)),
              "equivalence_bound_reviewer_ci": max(abs(ci_mine[0] - 1), abs(ci_mine[1] - 1)),
              "mean_null_count_per_set": st["M"] / n_c,
              "excess_coincidences_per_set": exc_set,
              "excess_per_set_ci95": [float(ex_b[50]), float(ex_b[1949])],
              "power": rows}
        pr["flag_power_below_0.95_at_10pct"] = rows["sigma_null"]["flag_power_at_plus_0.10"] < 0.95 or \
            rows["sigma_null"]["flag_power_at_minus_0.10"] < 0.95
        pr["delta_min_z_only_above_0.10"] = 4 * sig > 0.10
        power_rows.append(pr)

        # ---- calibration: leave-one-out z for every replicate k
        T = nulls.sum(axis=1)
        zk, numk = [], []
        for k in range(20):
            others = np.delete(nulls, k, axis=1)
            num = float((nulls[:, k] - others.mean(axis=1)).sum())
            den = math.sqrt(float(others.var(axis=1, ddof=1).sum()) * (1 + 1 / 19))
            zk.append(num / den)
            numk.append(num)
        zk = np.array(zk)
        maxdiff["z_cal"] = max(maxdiff["z_cal"], abs(zk[0] - rc["z_cal"]) / max(1e-300, abs(rc["z_cal"])))
        loo_by_k = np.vstack([loo_by_k, zk])
        cal_rows.append({"cell": cid, "mu_per_set": st["M"] / n_c, "z_cal_recorded": rc["z_cal"],
                         "z_loo_k0": float(zk[0]), "mean_over_k": float(zk.mean()),
                         "sd_over_k": float(zk.std(ddof=1)), "min_over_k": float(zk.min()),
                         "max_over_k": float(zk.max()), "sum_of_numerators_over_k": float(sum(numk)),
                         "sum_of_numerators_scale": float(abs(T).sum())})
        # job-level ranks of every replicate (mid-rank among its 20 values)
        for row in nulls:
            rk = (row[:, None] > row[None, :]).sum(axis=1) + 0.5 * ((row[:, None] == row[None, :]).sum(axis=1) - 1)
            rankk_all.append(rk)

        # ---- dispersion: gap vs the 20 LOO null replicates as matched null objects
        dgap = float(((g - m) ** 2).sum() / (1.05 * s2.sum()))
        dnull = []
        for k in range(20):
            others = np.delete(nulls, k, axis=1)
            mo, so = others.mean(axis=1), others.var(axis=1, ddof=1)
            dnull.append(float(((nulls[:, k] - mo) ** 2).sum() / ((1 + 1 / 19) * so.sum())))
        dnull = np.array(dnull)
        # PIT: randomized rank of the gap count among gap + 20 nulls, per job
        prng = C.review_np_rng("pit", cid)
        below = (nulls < g[:, None]).sum(axis=1)
        ties = (nulls == g[:, None]).sum(axis=1)
        R = below + np.floor(prng.random(n_c) * (ties + 1))
        # matched null PIT: replicate 0 among the other 19 (ranks 0..19)
        b0 = (nulls[:, 1:] < nulls[:, :1]).sum(axis=1)
        t0 = (nulls[:, 1:] == nulls[:, :1]).sum(axis=1)
        R0 = b0 + np.floor(prng.random(n_c) * (t0 + 1))
        per_cell[cid] = {"R": R, "R0": R0, "bits": d["bits"], "r": d["r"], "n": d["n"],
                         "resid": (g - m) / np.sqrt(np.where(s2 > 0, s2, np.nan) * 1.05),
                         "w": np.sqrt(s2) / math.sqrt(st["V"]), "c": np.array([r["c"] for r in rs]),
                         "z": st["z"], "kappa": st["kappa"], "sigma": sig, "z_cal": float(zk[0]),
                         "g": g, "m": m, "s2": s2,
                         "kappa_even": rc["kappa_even"], "kappa_odd": rc["kappa_odd"],
                         "nmf_rec": rc["null_mean_over_formula"],
                         "F": float(sum(3 * math.comb(r["n"], 4) / r["p"] for r in rs))}
        J = n_c
        disp_rows.append({"cell": cid, "dispersion_gap": dgap,
                          "dispersion_null_loo_mean": float(dnull.mean()), "dispersion_null_loo_sd": float(dnull.std(ddof=1)),
                          "dispersion_gap_rank_among_21": int((dnull < dgap).sum()),
                          "dispersion_gap_z_vs_loo": float((dgap - dnull.mean()) / dnull.std(ddof=1)),
                          "pit_mean_rank_gap": float(R.mean()), "pit_location_z_gap": float((R.mean() - 10) / math.sqrt(36.6667 / J)),
                          "pit_extreme_fraction_gap": float(((R == 0) | (R == 20)).mean()),
                          "pit_extreme_z_gap": float((((R == 0) | (R == 20)).mean() - 2 / 21) / math.sqrt((2 / 21) * (19 / 21) / J)),
                          "pit_extreme_fraction_null_rep0": float(((R0 == 0) | (R0 == 19)).mean()),
                          "pit_extreme_z_null_rep0": float((((R0 == 0) | (R0 == 19)).mean() - 2 / 20) / math.sqrt((2 / 20) * (18 / 20) / J)),
                          "curves": J})

    powered = [r for r in power_rows if r.get("assessable")]
    C.write_json("power-table.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a items (1) and (2)",
        "inputs": [C.rel(C.JOBS), C.rel(C.ANALYSIS), C.rel(C.DESIGN)],
        "method": (
            "Per cell from the raw job records: S, M, V (n-1 sample variances), kappa, z = (S-M)/sqrt(1.05 V) and "
            "sigma_kappa = sqrt(1.05 V)/M. delta_min_z_only = 4 sigma_kappa is the plan's formula (z conjunct only). The "
            "frozen flag rule is the conjunction |kappa-1| >= 0.10 AND |z| > 4, so its effective threshold on |kappa_hat-1| "
            "is max(0.10, 4 sigma_kappa). Normal approximation: kappa_hat ~ N(1+delta, sigma_alt^2) with sigma_alt = "
            "sigma*sqrt(1+delta) (Poisson-like scaling), for sigma = sigma_kappa (sigma_null) and for sigma = "
            "max(sigma_kappa, bootstrap sd of kappa) (sigma_emp). flag power = P(|kappa_hat-1| >= threshold, same sign). "
            "p_read_null = P(|kappa_hat-1| < 0.05 and kappa_hat +- 1.96 sigma_boot inside [0.90, 1.10]) with sigma_boot from "
            "the recorded ci95 width. Equivalence bound = max |ci95 - 1| of the recorded interval (and of a reviewer "
            "bootstrap: 2000 curve-cluster resamples, reviewer seed). excess_coincidences_per_set = (S-M)/curves."),
        "cross_check_vs_recorded_max_rel_diff": maxdiff, "S_integer_mismatches": S_int_mismatch,
        "summary": {
            "powered_cells": len(powered),
            "cells_flag_power_below_0.95_at_10pct": [r["cell"] for r in powered if r["flag_power_below_0.95_at_10pct"]],
            "cells_delta_min_z_only_above_0.10": [r["cell"] for r in powered if r["delta_min_z_only_above_0.10"]],
            "max_flag_power_at_plus_0.10": max(r["power"]["sigma_null"]["flag_power_at_plus_0.10"] for r in powered),
            "min_flag_power_at_plus_0.10": min(r["power"]["sigma_emp"]["flag_power_at_plus_0.10"] for r in powered),
            "max_delta_min_z_only": max(r["delta_min_z_only"] for r in powered),
            "max_delta_95_flag_excess_sigma_emp": max(r["power"]["sigma_emp"]["delta_95_flag_excess"] for r in powered),
            "max_p_read_null_at_10pct_sigma_emp": max(max(r["power"]["sigma_emp"]["p_read_null_at_plus_0.10"],
                                                          r["power"]["sigma_emp"]["p_read_null_at_minus_0.10"]) for r in powered),
            "max_equivalence_bound_recorded": max(r["equivalence_bound_recorded_ci"] for r in powered),
            "cell_of_max_equivalence_bound": max(powered, key=lambda r: r["equivalence_bound_recorded_ci"])["cell"],
            "V_over_M_range": [min(r["V_over_M"] for r in powered), max(r["V_over_M"] for r in powered)],
            "bootstrap_over_null_sd_range": [min(r["bootstrap_over_null_sd"] for r in powered),
                                             max(r["bootstrap_over_null_sd"] for r in powered)],
        },
        "cells": power_rows}, sig=6)

    # ---------------- calibration summary
    zc = loo_by_k[:, 0]
    kmeans = loo_by_k.mean(axis=0)
    ranks = np.array(rankk_all)                       # jobs x 20 mid-ranks in 0..19
    J = ranks.shape[0]
    rank_means = ranks.mean(axis=0)
    rank_se = math.sqrt((20 ** 2 - 1) / 12 / J)
    mus = np.array([r["mu_per_set"] for r in cal_rows])
    lo_half = zc[mus <= np.median(mus)]
    hi_half = zc[mus > np.median(mus)]
    b = float(zc.mean())
    C.write_json("calibration-loo.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a item (3)",
        "inputs": [C.rel(C.JOBS), C.rel(C.ANALYSIS)],
        "method": (
            "For every powered cell and every replicate k = 0..19: z_k = sum_c (X_kc - mean_{-k,c}) / sqrt(sum_c "
            "var_{-k,c} (1 + 1/19)); k = 0 is the recorded z_cal. Identity: for each curve sum_k (X_k - mean_{-k}) = 0 "
            "exactly, so the mean over k of the LOO numerators is zero by construction and the mean of z_k over k is "
            "near zero for every cell regardless of any bias; the LOO mean is therefore NOT an independent bias estimate. "
            "The informative tests are (a) whether replicate 0 is exchangeable with replicates 1..19 (job-level mid-rank "
            "of each replicate among its 20 values, mean rank 9.5 under exchangeability), (b) the position of the k = 0 "
            "cell-mean among the 20 per-k cell-means, and (c) the dependence of z_cal on the per-set null mean."),
        "recorded": {"n": an["calibration"]["n"], "mean": an["calibration"]["mean"], "sd": an["calibration"]["sd"]},
        "reviewer_z_cal": {"n": int(len(zc)), "mean": b, "population_sd": float(zc.std()),
                           "max_rel_diff_vs_recorded_z_cal": maxdiff["z_cal"]},
        "chance_assessment": {
            "se_of_mean_if_independent_unit_normal": 1 / math.sqrt(len(zc)),
            "z_of_mean": b * math.sqrt(len(zc)),
            "two_sided_p_if_independent": 2 * C.phi(-abs(b) * math.sqrt(len(zc))),
            "per_k_cell_means": [float(x) for x in kmeans],
            "per_k_cell_means_sd": float(kmeans.std(ddof=1)),
            "k0_rank_among_20_per_k_means_ascending": int((kmeans < kmeans[0]).sum()) + 1,
            "fraction_of_k_with_abs_mean_ge_observed": float((np.abs(kmeans) >= abs(b) - 1e-15).mean()),
            "job_level_mean_midrank_per_replicate": [float(x) for x in rank_means],
            "job_level_rank_se": rank_se, "jobs": J,
            "job_level_rank_z_replicate0": float((rank_means[0] - 9.5) / rank_se),
            "job_level_rank_z_all_replicates": [float((x - 9.5) / rank_se) for x in rank_means],
            "z_cal_mean_small_mu_half": float(lo_half.mean()), "z_cal_mean_large_mu_half": float(hi_half.mean()),
            "corr_z_cal_vs_log_mu": float(np.corrcoef(zc, np.log(mus))[0, 1]),
        },
        "pooled_loo": {"n_values": int(loo_by_k.size), "mean": float(loo_by_k.mean()),
                       "sd": float(loo_by_k.std(ddof=1)),
                       "per_cell_sd_over_k_mean": float(np.mean([r["sd_over_k"] for r in cal_rows]))},
        "effect_of_a_bias_equal_to_the_observed_mean": {
            "bias_b": b,
            "flag_false_positive_rate_per_cell_upper_tail": "P(z > max(4, 0.10/sigma_kappa) | z ~ N(b,1)); see per_cell",
            "max_over_cells_P_false_flag_excess": max(C.phi(-(max(4, 0.10 / p["sigma"]) - b)) for p in per_cell.values()),
            "max_over_cells_P_false_flag_deficit": max(C.phi(-(max(4, 0.10 / p["sigma"]) + b)) for p in per_cell.values()),
            "min_over_cells_0.10_over_sigma_kappa": min(0.10 / p["sigma"] for p in per_cell.values()),
            "shift_of_kappa_hat_equivalent_max": max(abs(b) * p["sigma"] for p in per_cell.values()),
            "note": ("The flag rule's effect-size conjunct requires |z| >= 0.10/sigma_kappa (>= 5.6 at every powered cell), "
                     "so a z bias of this size moves neither tail of the flag rule materially; the null class does not "
                     "use z at all. A bias would shift the gap z by b, i.e. kappa_hat by b*sigma_kappa (< 0.005)."),
        },
        "cells": cal_rows})

    # ---------------- tail and correlation
    ids = [c for c in order if c in per_cell]
    zs = np.array([per_cell[c]["z"] for c in ids])
    zmax_i = int(np.argmax(np.abs(zs)))
    zmax = float(abs(zs[zmax_i]))
    pair_rows = []
    num_w, den_w = {20: 0.0, 24: 0.0, 28: 0.0}, {20: 0.0, 24: 0.0, 28: 0.0}
    for i, a_ in enumerate(ids):
        for b_ in ids[i + 1:]:
            A, B = per_cell[a_], per_cell[b_]
            if A["bits"] != B["bits"]:
                continue
            common_c = np.intersect1d(A["c"], B["c"])
            ia = np.searchsorted(A["c"], common_c)
            ib = np.searchsorted(B["c"], common_c)
            ra, rb = A["resid"][ia], B["resid"][ib]
            ok = np.isfinite(ra) & np.isfinite(rb)
            rho = float(np.corrcoef(ra[ok], rb[ok])[0, 1])
            wsum = float((A["w"][ia] * B["w"][ib]).sum())
            pair_rows.append({"a": a_, "b": b_, "shared_curves": int(ok.sum()), "rho_resid": rho,
                              "overlap_weight": wsum, "implied_corr_z": rho * wsum})
            num_w[A["bits"]] += rho * ok.sum()
            den_w[A["bits"]] += ok.sum()
    rho_bits = {k: num_w[k] / den_w[k] for k in num_w}
    rho_all = sum(num_w.values()) / sum(den_w.values())
    # cell-level correlation matrix from pooled per-bits rho times overlap weight
    K = len(ids)
    Rm = np.eye(K)
    Rp = np.eye(K)
    idx = {c: i for i, c in enumerate(ids)}
    for pr in pair_rows:
        i, j = idx[pr["a"]], idx[pr["b"]]
        bits = per_cell[pr["a"]]["bits"]
        Rm[i, j] = Rm[j, i] = rho_bits[bits] * pr["overlap_weight"]
        Rp[i, j] = Rp[j, i] = pr["implied_corr_z"]

    def psd(R):
        w, v = np.linalg.eigh(R)
        w = np.clip(w, 1e-9, None)
        R2 = (v * w) @ v.T
        dd = np.sqrt(np.diag(R2))
        return R2 / np.outer(dd, dd), float(w.min())

    Rm2, minev_m = psd(Rm)
    Rp2, minev_p = psd(Rp)
    sim_rng = C.review_np_rng("tail-sim")
    res_sim = {}
    for lab, R in (("pooled_rho_by_bits", Rm2), ("pairwise_rho", Rp2), ("independent", np.eye(K))):
        L = np.linalg.cholesky(R)
        for bias_lab, bias in (("no_bias", 0.0), ("bias_eq_zcal_mean", b)):
            draws = 0
            hits = 0
            for _ in range(20):
                Z = sim_rng.standard_normal((20000, K)) @ L.T + bias
                hits += int((np.abs(Z).max(axis=1) >= zmax).sum())
                draws += 20000
            res_sim[f"{lab}|{bias_lab}"] = {"p_max_abs_z_ge_observed": hits / draws, "draws": draws}
    p1 = 2 * C.phi(-zmax)
    sidak = 1 - (1 - p1) ** K
    p1b = C.phi(-zmax - b) + C.phi(-zmax + b)
    sidak_b = 1 - (1 - p1b) ** K
    # deep dive on the largest |z| cell
    top = ids[zmax_i]
    T_ = per_cell[top]
    g, m, s2 = T_["g"], T_["m"], T_["s2"]
    ev = T_["c"] % 2 == 0
    def zsub(sel):
        return float((g[sel] - m[sel]).sum() / math.sqrt(1.05 * s2[sel].sum()))
    loo_curve = []
    for i in range(len(g)):
        sel = np.ones(len(g), bool)
        sel[i] = False
        loo_curve.append(zsub(sel))
    r1 = [c for c in ids if per_cell[c]["r"] == per_cell[top]["r"] and c != top]
    C.write_json("tail-and-correlation.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a item (4)",
        "inputs": [C.rel(C.JOBS), C.rel(C.ANALYSIS)],
        "method": (
            "Observed largest |z| over the powered cells. Sidak: 1-(1-2 Phi(-|z|max))^K. With a bias b: per-cell tail "
            "Phi(-|z|max-b)+Phi(-|z|max+b). Cross-cell correlation: per-curve standardized residual r = (g-m)/sqrt(1.05 s^2) "
            "for every cell; for every pair of cells at the same bits the Pearson correlation of r over shared curve "
            "indices; the implied correlation of the two cell z's is rho * sum_c w_a,c w_b,c with w = s_c/sqrt(V) (so that "
            "sum_c w^2 = 1). Two correlation matrices: pooled rho per bits times overlap weight, and the pairwise estimates "
            "(projected to PSD); 400,000 multivariate-normal draws each, with and without the bias."),
        "observed": {"cell": top, "z": float(zs[zmax_i]), "abs_z": zmax, "K": K,
                     "cells_abs_z_gt_3": [c for c in ids if abs(per_cell[c]["z"]) > 3],
                     "expected_count_abs_z_gt_3_independent": K * 2 * C.phi(-3.0)},
        "sidak_independent": sidak, "sidak_with_bias": sidak_b, "bias_b": b,
        "rho_resid_pooled_by_bits": rho_bits, "rho_resid_pooled_all": rho_all,
        "rho_resid_se_approx_by_bits": {k: 1 / math.sqrt(den_w[k]) for k in den_w},
        "max_abs_implied_corr_z": max(abs(pr["implied_corr_z"]) for pr in pair_rows),
        "min_eigenvalue_before_psd": {"pooled": minev_m, "pairwise": minev_p},
        "simulated": res_sim,
        "largest_cell_deep_dive": {
            "cell": top, "kappa": T_["kappa"], "kappa_minus_1": T_["kappa"] - 1, "sigma_kappa": T_["sigma"],
            "curves": int(len(g)), "z_even_curves": zsub(ev), "z_odd_curves": zsub(~ev),
            "fraction_curves_negative_residual": float((g < m).mean()),
            "leave_one_curve_out_z_range": [min(loo_curve), max(loo_curve)],
            "excess_coincidences_per_set": float((g - m).sum() / len(g)),
            "mean_null_count_per_set": float(m.mean()),
            "same_rank_other_cells_stouffer_z": float(sum(per_cell[c]["z"] for c in r1) / math.sqrt(len(r1))),
            "same_rank_other_cells": len(r1),
        },
        "pairs_note": "per-pair rows: pair_count_by_bits gives the count; the 15 largest |implied_corr_z| pairs are listed",
        "pair_count_by_bits": {k: sum(1 for pr in pair_rows if per_cell[pr["a"]]["bits"] == k) for k in (20, 24, 28)},
        "pairs_top15_abs_implied_corr": sorted(pair_rows, key=lambda pr: -abs(pr["implied_corr_z"]))[:15]}, sig=6)

    # ---------------- pooled strata
    def pool(sel):
        z_ = np.array([per_cell[c]["z"] for c in sel])
        k_ = np.array([per_cell[c]["kappa"] for c in sel])
        s_ = np.array([per_cell[c]["sigma"] for c in sel])
        w_ = 1 / s_ ** 2
        kb = float((w_ * k_).sum() / w_.sum())
        se = float(1 / math.sqrt(w_.sum()))
        Q = float((w_ * (k_ - kb) ** 2).sum())
        df = len(sel) - 1
        ii = [idx[c] for c in sel]
        var_sum = float(Rm2[np.ix_(ii, ii)].sum())
        return {"cells": len(sel), "stouffer_z_independent": float(z_.sum() / math.sqrt(len(sel))),
                "stouffer_z_corr_adjusted": float(z_.sum() / math.sqrt(var_sum)),
                "iv_pooled_kappa": kb, "iv_se": se, "iv_z": (kb - 1) / se,
                "Q": Q, "df": df, "p_Q": chi2_sf(Q, df) if df > 0 else None,
                "I2": max(0.0, (Q - df) / Q) if Q > 0 else 0.0,
                "unweighted_mean_kappa": float(k_.mean())}
    strata = {"all": pool(ids)}
    for key in ("r", "bits", "n"):
        for v in sorted(set(per_cell[c][key] for c in ids)):
            strata[f"{key}={v}"] = pool([c for c in ids if per_cell[c][key] == v])
    for bits in (20, 24, 28):
        for r in (1, 2, 3):
            sel = [c for c in ids if per_cell[c]["bits"] == bits and per_cell[c]["r"] == r]
            if sel:
                strata[f"bits={bits},r={r}"] = pool(sel)
    eo = []
    for c in ids:
        P = per_cell[c]
        ev = P["c"] % 2 == 0
        ke = P["g"][ev].sum() / P["m"][ev].sum()
        ko = P["g"][~ev].sum() / P["m"][~ev].sum()
        se_e = math.sqrt(1.05 * P["s2"][ev].sum()) / P["m"][ev].sum()
        se_o = math.sqrt(1.05 * P["s2"][~ev].sum()) / P["m"][~ev].sum()
        eo.append({"cell": c, "kappa_even": float(ke), "kappa_odd": float(ko),
                   "match_recorded": abs(ke - P["kappa_even"]) < 1e-9 and abs(ko - P["kappa_odd"]) < 1e-9,
                   "z_even_minus_odd": float((ke - ko) / math.sqrt(se_e ** 2 + se_o ** 2))})
    zeo = np.array([e["z_even_minus_odd"] for e in eo])
    nmf = []
    for c in ids:
        P = per_cell[c]
        M_ = P["m"].sum()
        nmf.append({"cell": c, "null_mean_over_formula": float(M_ / P["F"]), "recorded": P["nmf_rec"],
                    "z_M_vs_formula": float((M_ - P["F"]) / math.sqrt(P["s2"].sum() / 20)),
                    "bits": P["bits"], "n": P["n"]})
    zn = np.array([x["z_M_vs_formula"] for x in nmf])
    by_bits_nmf = {}
    for bits in (20, 24, 28):
        sel = [x for x in nmf if x["bits"] == bits]
        by_bits_nmf[bits] = {"stouffer_z": float(sum(x["z_M_vs_formula"] for x in sel) / math.sqrt(len(sel))),
                             "ratio_range": [min(x["null_mean_over_formula"] for x in sel),
                                             max(x["null_mean_over_formula"] for x in sel)]}
    C.write_json("pooled-strata.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a item (5)",
        "inputs": [C.rel(C.JOBS), C.rel(C.ANALYSIS)],
        "method": (
            "Stouffer Z = sum z / sqrt(k) (independent) and sum z / sqrt(1' R 1) with R the pooled-rho correlation "
            "matrix of tail-and-correlation.json; inverse-variance pooled kappa with w = 1/sigma_kappa^2, its z, "
            "Cochran Q, p_Q (chi-square, df k-1) and I^2. Even/odd A/A: z = (kappa_even - kappa_odd)/sqrt(se_e^2 + "
            "se_o^2), se = sqrt(1.05 V_half)/M_half. Null mean against the formula: M / sum_c 3 binom(n,4)/p_c and z = "
            "(M - F)/sqrt(V/20) (sampling sd of M)."),
        "break_criterion_from_plan": "a pooled stratum with |combined z| > 3",
        "strata": strata,
        "strata_with_abs_z_gt_3": [k for k, v in strata.items()
                                   if max(abs(v["stouffer_z_independent"]), abs(v["stouffer_z_corr_adjusted"]), abs(v["iv_z"])) > 3],
        "even_odd": {"cells": eo, "mean_z": float(zeo.mean()), "sd_z": float(zeo.std(ddof=1)),
                     "max_abs_z": float(np.abs(zeo).max()), "all_match_recorded": all(e["match_recorded"] for e in eo)},
        "null_mean_over_formula": {"cells": nmf, "range": [float(min(x["null_mean_over_formula"] for x in nmf)),
                                                           float(max(x["null_mean_over_formula"] for x in nmf))],
                                   "stouffer_z_all": float(zn.sum() / math.sqrt(len(zn))), "by_bits": by_bits_nmf,
                                   "anomalies_outside_0.8_1.25": [x["cell"] for x in nmf if not 0.8 <= x["null_mean_over_formula"] <= 1.25]},
    })

    # ---------------- dispersion / PIT strata
    def pit_pool(sel):
        R = np.concatenate([per_cell[c]["R"] for c in sel])
        R0 = np.concatenate([per_cell[c]["R0"] for c in sel])
        J_ = len(R)
        h = np.bincount(R.astype(int), minlength=21)
        h0 = np.bincount(R0.astype(int), minlength=20)
        chi = float(((h - J_ / 21) ** 2 / (J_ / 21)).sum())
        chi0 = float(((h0 - J_ / 20) ** 2 / (J_ / 20)).sum())
        ext = float(((R == 0) | (R == 20)).mean())
        ext0 = float(((R0 == 0) | (R0 == 19)).mean())
        return {"jobs": J_, "gap_mean_rank": float(R.mean()), "gap_location_z": float((R.mean() - 10) / math.sqrt(36.6667 / J_)),
                "gap_extreme_fraction": ext, "gap_extreme_z": float((ext - 2 / 21) / math.sqrt((2 / 21) * (19 / 21) / J_)),
                "gap_chi2_21bins": chi, "gap_chi2_p": chi2_sf(chi, 20),
                "null_rep0_extreme_fraction": ext0,
                "null_rep0_extreme_z": float((ext0 - 0.1) / math.sqrt(0.09 / J_)),
                "null_rep0_chi2_20bins": chi0, "null_rep0_chi2_p": chi2_sf(chi0, 19),
                "gap_histogram": h.tolist()}
    pit_strata = {"all": pit_pool(ids)}
    for bits in (20, 24, 28):
        for r in (1, 2, 3):
            sel = [c for c in ids if per_cell[c]["bits"] == bits and per_cell[c]["r"] == r]
            if sel:
                pit_strata[f"bits={bits},r={r}"] = pit_pool(sel)
    dg = np.array([d_["dispersion_gap_z_vs_loo"] for d_ in disp_rows])
    C.write_json("dispersion-pit.json", {
        "task": "TASK-20261029-11526b", "joint": "J3a (added attack: distribution, not only the pooled mean)",
        "inputs": [C.rel(C.JOBS)],
        "method": (
            "H1 as stated (labels behave as independent uniform elements of L) implies that per curve the log-GAP count is "
            "exchangeable with the 20 null counts, not only that the pooled means agree. (a) Dispersion ratio per cell "
            "D = sum_c (g_c - m_c)^2 / (1.05 sum_c s_c^2), compared with the same statistic for each null replicate k "
            "treated as the structured arm against the other 19 (factor 1 + 1/19): the matched null-object control. (b) "
            "PIT: per job the randomized rank of g among g and its 20 null counts (ties broken by a reviewer stream), "
            "uniform on 0..20 under exchangeability; location z, extreme-rank fraction (ranks 0 or 20, expected 2/21) and "
            "a 21-bin chi-square; the same for null replicate 0 among the other 19 as the null control."),
        "summary": {"dispersion_gap_z_vs_loo_mean": float(dg.mean()), "dispersion_gap_z_vs_loo_sd": float(dg.std(ddof=1)),
                    "cells_dispersion_gap_rank_20_of_20": [d_["cell"] for d_ in disp_rows if d_["dispersion_gap_rank_among_21"] == 20],
                    "cells_dispersion_gap_rank_0_of_20": [d_["cell"] for d_ in disp_rows if d_["dispersion_gap_rank_among_21"] == 0]},
        "pit_strata": pit_strata, "cells": disp_rows})
    print("done", maxdiff, S_int_mismatch)


if __name__ == "__main__":
    main()
