"""Stage C/D per-prime analysis (PM-3, PM-4, TC-1..TC-4, NULL-2 bounds, SEED-1,
SEED-2, KS-1, START-2, PC-3, secondary metrics).  Pure functions of the
per-sample and per-null records; called only after ALL sampling at a prime is
complete (SR-8, AC-5).
"""
import math

import numpy as np

import rho as rhomod
import stats

U_GRID = [1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 7]
TC2_M = [5, 20, 100]


def lnp2(p):
    return math.log(p) - math.log(2)


def B_of_u(p, u):
    return math.exp(lnp2(p) / (3 * u))


def admissible_table(p, N):
    """Computed BEFORE sampling from the validated rho; recorded in the manifest."""
    rows = []
    for u in U_GRID:
        B = B_of_u(p, u)
        r = rhomod.rho(u)
        rows.append({"u": u, "B": B, "rho": r, "N_rho": N * r, "B_ge_128": B >= 128, "N_rho_ge_30": N * r >= 30,
                     "admissible": (B >= 128 and N * r >= 30)})
    tc2 = []
    for m in TC2_M:
        um = rhomod.rho_inv(m / N)
        xm = lnp2(p) / (3 * um)
        tc2.append({"m": m, "u_m": um, "x_m": xm, "exp_x_m": math.exp(xm), "admissible": math.exp(xm) >= 128})
    x30 = lnp2(p) / (3 * rhomod.rho_inv(30.0 / N))
    return {"p": str(p), "N": N, "X_max": None, "cells": rows, "TC2_thresholds": tc2, "KS_region_x_ge": x30}


def smooth_count(ells, B):
    return int(sum(1 for e in ells if e < B))


def tc1_prob(rho_val, N):
    if rho_val <= 0:
        return 0.0
    if rho_val >= 1:
        return 1.0
    return -math.expm1(N * math.log1p(-rho_val))


def rho_or_zero(u):
    if u <= rhomod.KMAX:
        return rhomod.rho(u)
    return 0.0


def tc1(p, ells, N):
    M = min(ells)
    if M <= 1:
        return {"M": M, "u_star": None, "rho_u_star": 0.0, "Pr_min_le_M": 0.0,
                "consistent": False, "admissible": False, "note": "M = 1 (delta = 1 present)"}
    us = lnp2(p) / (3 * math.log(M))
    r = rho_or_zero(us)
    P = tc1_prob(r, N)
    return {"M": M, "u_star": us, "rho_u_star": r, "Pr_min_le_M": P, "consistent": 0.005 <= P <= 0.995,
            "admissible": M >= 128}


def tc1_size_matched(deltas, M):
    if M <= 1:
        return None
    lm = math.log(M)
    s = 0.0
    for d in deltas:
        if d <= M:
            return 1.0
        r = rho_or_zero(math.log(d) / lm)
        if r >= 1:
            return 1.0
        s += math.log1p(-r)
    return -math.expm1(s)


def ks_to_prediction(p, ells, N, x30):
    x = np.sort(np.log(np.array([float(e) for e in ells])))
    F = lambda xx: rho_or_zero(lnp2(p) / (3 * xx)) if xx > 0 else 0.0
    n = len(x)
    D = abs(np.searchsorted(x, x30, side="right") / n - F(x30))
    # evaluate at every distinct sample point in the region (both sides of the jump)
    vals = np.unique(x[x >= x30])
    for v in vals:
        fv = F(float(v))
        hi = np.searchsorted(x, v, side="right") / n
        lo = np.searchsorted(x, v, side="left") / n
        D = max(D, abs(hi - fv), abs(lo - fv))
    return float(D)


def two_sample_family(a_recs, b_recs, p, adm_u, alpha=0.01):
    """KS on ln delta + two-proportion smooth-count tests at admissible u; Bonferroni."""
    la = [math.log(r["delta"]) for r in a_recs]
    lb = [math.log(r["delta"]) for r in b_recs]
    d, pks = stats.ks_2samp(la, lb)
    tests = [{"test": "KS_ln_delta", "D": d, "p_value": pks}]
    ea = [r["ell_max"] for r in a_recs]
    eb = [r["ell_max"] for r in b_recs]
    for u in adm_u:
        B = B_of_u(p, u)
        ka, kb = smooth_count(ea, B), smooth_count(eb, B)
        z, pv = stats.two_prop_z(ka, len(ea), kb, len(eb))
        tests.append({"test": "smooth_count_u%s" % u, "k_a": ka, "n_a": len(ea), "k_b": kb, "n_b": len(eb), "z": z, "p_value": pv})
    m = len(tests)
    thr = alpha / m
    rej = [t["test"] for t in tests if t["p_value"] < thr]
    return {"family_size": m, "bonferroni_threshold": thr, "tests": tests, "rejected": rej, "reject": bool(rej)}


def analyze_prime(p, N, adm, main, r1, r2, null1, null2, arms=None, tc4=False):
    """main = r1 + r2 (N records).  Returns a dict of every metric and per-prime validity inputs."""
    out = {"p": str(p), "N": len(main)}
    assert len(main) == N
    deltas = [r["delta"] for r in main]
    ells = [r["ell_max"] for r in main]
    n1_ells = [r["ell_max"] for r in null1]
    n2_ells = [r["ell_max"] for r in null2]
    X = int(adm["X_max"])
    adm_u = [c["u"] for c in adm["cells"] if c["admissible"]]
    cells = []
    for c in adm["cells"]:
        u, B, rr = c["u"], c["B"], c["rho"]
        S = smooth_count(ells, B)
        S1 = smooth_count(n1_ells, B)
        S2 = smooth_count(n2_ells, B)
        f = S / N
        wl, wh = stats.wilson(S, N)
        uu = u ** (-u)
        T1, T1ci = stats.ratio_interval(S, S1)
        pred_sm = sum(rhomod.rho(math.log(d) / math.log(B)) if d > 1 else 1.0 for d in deltas)
        th = (lambda ff: (-math.log(ff) / (u * math.log(u))) if ff > 0 else None)
        cells.append({
            "u": u, "B": B, "admissible": c["admissible"], "rho_u": rr,
            "S_delta": S, "f_emp": f, "wilson99": [wl, wh], "R_max": f / rr,
            "wilson_upper_ge_rho": wh >= rr,
            "u_pow_minus_u": uu, "R_uu": f / uu,
            "theta_eff": th(f), "theta_eff_interval": [th(wh), th(wl)],
            "S_null1": S1, "f_null1": S1 / len(null1), "T1": T1, "T1_ci99": list(T1ci),
            "S_null2": S2, "f_null2": S2 / len(null2), "null2_over_rho": (S2 / len(null2)) / rr,
            "null2_bound_ok": 0.7 <= (S2 / len(null2)) / rr <= 2.0,
            "size_matched_prediction": pred_sm, "S_delta_over_size_matched": (S / pred_sm) if pred_sm > 0 else None,
            "fc_h1_cell": (wh < rr) and (T1ci[1] < 1),
        })
    out["cells"] = cells
    adm_cells = [c for c in cells if c["admissible"]]
    out["admissible_u"] = adm_u
    # tail checks
    t1 = tc1(p, ells, N)
    t1["size_matched_Pr_min_le_M"] = tc1_size_matched(deltas, t1["M"])
    n1min = min(n1_ells)
    t1["null1_smoothest"] = tc1(p, n1_ells, len(null1))
    out["TC-1"] = t1
    tc2 = []
    for th in adm["TC2_thresholds"]:
        cnt = sum(1 for e in ells if (e == 1 or math.log(e) < th["x_m"]))
        lo, hi = stats.poisson_interval(cnt)
        tc2.append({"m": th["m"], "x_m": th["x_m"], "exp_x_m": th["exp_x_m"], "admissible": th["admissible"],
                    "observed": cnt, "poisson99_two_sided": [lo, hi], "deficit": hi < th["m"],
                    "excess_reported": lo > th["m"]})
    out["TC-2"] = tc2
    isprime_d = sum(1 for r in main if r["delta"] > 1 and len(r["fac"]) == 1 and r["fac"][0][1] == 1)
    isprime_n = sum(1 for r in null1 if r["n"] > 1 and len(r["fac"]) == 1 and r["fac"][0][1] == 1)
    dd, dci = stats.diff_prop_wald(isprime_d, N, isprime_n, len(null1))
    out["TC-3"] = {"delta_prime_count": isprime_d, "null1_prime_count": isprime_n, "frac_delta": isprime_d / N,
                   "frac_null1": isprime_n / len(null1), "difference": dd, "wald99": list(dci)}
    if tc4:
        # TC-4: source's smoothest (12589-smooth) through TC-1's extreme-value interval
        us = lnp2(p) / (3 * math.log(12589))
        Psrc = tc1_prob(rhomod.rho(us), N)
        # interval of M with Pr[min <= M] in [0.005, 0.995]
        def M_for(P):
            # solve 1-(1-rho)^N = P for rho, then M = exp(ln(p/2)/(3 u))
            r = -math.expm1(math.log1p(-P) / N)
            return math.exp(lnp2(p) / (3 * rhomod.rho_inv(r)))
        out["TC-4"] = {"source_M": 12589, "source_u": us, "source_rho": rhomod.rho(us), "source_Pr_min_le_M": Psrc,
                       "source_in_interval": 0.005 <= Psrc <= 0.995,
                       "extreme_value_interval_M": [M_for(0.005), M_for(0.995)],
                       "observed_M": t1["M"], "observed_Pr_min_le_M": t1["Pr_min_le_M"],
                       "observed_in_interval": t1["consistent"]}
    # secondary
    pts = [(c["u"], math.log(c["T1"])) for c in adm_cells if c["T1"] not in (None, 0.0) and math.isfinite(c["T1"])]
    out["T1_trend"] = stats.ols_slope([x for x, _ in pts], [y for _, y in pts])
    tr = out["T1_trend"]
    out["T1_trend"]["significant_negative"] = bool(tr.get("ci") and tr["ci"][1] < 0)
    out["T1_trend"]["significant_positive"] = bool(tr.get("ci") and tr["ci"][0] > 0)
    out["KS_ECDF_vs_prediction"] = {"region_x_ge": adm["KS_region_x_ge"],
                                    "D": ks_to_prediction(p, ells, N, adm["KS_region_x_ge"])}
    lx = math.log(X)
    h = np.histogram([math.log(d) / lx for d in deltas], bins=20, range=(0.0, 1.0 + 1e-12))[0]
    out["ln_delta_over_ln_Xmax_histogram_descriptive"] = {"bins": 20, "range": [0, 1], "counts": [int(v) for v in h],
                                                          "note": "REPORTED, NOT TESTED (H-WESO-9dc201 size law not evaluated)"}
    out["delta_max"] = max(deltas)
    out["wall_seconds_per_sample"] = {"mean": float(np.mean([r["wall_s"] for r in main])),
                                      "median": float(np.median([r["wall_s"] for r in main])),
                                      "max": float(np.max([r["wall_s"] for r in main]))}
    # anchors / validity inputs
    out["C-2_violations"] = sum(1 for r in main if r["c2"] != 1) + sum(
        1 for arm in (arms or {}).values() for r in arm if r["c2"] != 1)
    out["C-2_max_delta_le_X"] = max(deltas) <= X
    out["U-2_failures"] = sum(1 for r in main if r["u2"] != 1)
    unver = sum(1 for r in main if r["fac_ok"] != 1) + sum(1 for r in null1 + null2 if r["fac_ok"] != 1)
    out["IV-1_unverified_factorisations"] = unver
    out["SEED-1"] = two_sample_family(r1, r2, p, adm_u)
    ndup = len(main) - len(set(r["order_hash"] for r in main))
    n_delta1 = sum(1 for d in deltas if d == 1)
    out["SEED-2"] = {"duplicate_order_hashes": ndup, "delta_eq_1_count": n_delta1,
                     "invalidates": ndup > 1 or n_delta1 > 2}
    out["NULL-2_bounds"] = {"cells_checked": [c["u"] for c in adm_cells],
                            "all_within_0.7_2.0": all(c["null2_bound_ok"] for c in adm_cells),
                            "verdict": "PASS" if all(c["null2_bound_ok"] for c in adm_cells) else "FAIL"}
    if arms:
        if "KS1" in arms:
            out["KS-1"] = two_sample_family(arms["KS1"], main, p, adm_u)
            out["KS-1"]["verdict"] = "REJECT" if out["KS-1"]["reject"] else "NOT_REJECTED"
        if "START2" in arms:
            out["START-2"] = two_sample_family(arms["START2"], main, p, adm_u)
            out["START-2"]["verdict"] = "REJECT" if out["START-2"]["reject"] else "NOT_REJECTED"
        if "PC3" in arms:
            d, pv = stats.ks_2samp([math.log(r["delta"]) for r in arms["PC3"]], [math.log(r["delta"]) for r in main])
            out["PC-3"] = {"KS_D": d, "p_value": pv, "threshold": 0.001, "verdict": "PASS" if pv < 0.001 else "FAIL"}
    # validity (IV-1, IV-2, IV-7)
    reasons = []
    if unver:
        reasons.append("IV-1: %d unverified factorisations" % unver)
    if out["SEED-1"]["reject"]:
        reasons.append("IV-2: SEED-1 rejection %s" % out["SEED-1"]["rejected"])
    if out["SEED-2"]["invalidates"]:
        reasons.append("IV-2: SEED-2 (duplicates %d, delta=1 count %d)" % (ndup, n_delta1))
    if arms and out.get("KS-1", {}).get("reject"):
        reasons.append("IV-7: KS-1 rejection (mixing-transfer failure)")
    if arms and out.get("START-2", {}).get("reject"):
        reasons.append("IV-7: START-2 rejection (mixing-transfer failure)")
    out["prime_valid"] = not reasons
    out["prime_invalid_reasons"] = reasons
    # criteria inputs at this prime
    adm_tc1 = t1["admissible"]
    adm_tc2 = [t for t in tc2 if t["admissible"]]
    out["criteria_inputs"] = {
        "a_every_admissible_wilson_upper_ge_rho": all(c["wilson_upper_ge_rho"] for c in adm_cells),
        "a_failing_cells": [c["u"] for c in adm_cells if not c["wilson_upper_ge_rho"]],
        "b_TC1_admissible": adm_tc1, "b_TC1_consistent": t1["consistent"],
        "b_pass": (not adm_tc1) or t1["consistent"],
        "c_admissible_TC2_deficits": [t["m"] for t in adm_tc2 if t["deficit"]],
        "c_pass": sum(1 for t in adm_tc2 if t["deficit"]) <= 1,
        "fc_h1_cells": [c["u"] for c in adm_cells if c["fc_h1_cell"]],
        "T1_interval_excludes_1_cells": [c["u"] for c in adm_cells if c["T1_ci99"][0] > 1 or c["T1_ci99"][1] < 1],
    }
    return out
