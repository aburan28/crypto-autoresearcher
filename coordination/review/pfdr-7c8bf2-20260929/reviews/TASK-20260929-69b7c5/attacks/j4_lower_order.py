"""J4 / J6 / proves_too_much: lower-order structure of the per-series ratio slopes.

All intervals: stratified percentile bootstrap with the frozen resampling scheme
(random.Random(0), strata = bits in first-appearance order, 2000 reps, 95%).  Where the
statistic is the OLS slope of y on log2N, stats.bootstrap_slope itself is called; other
statistics use common.stratified_boot_generic, which draws the same indices.

  M1  y = a + b*x + c/x                       -> b (asymptotic slope), 12..32
  M2  y = a + b*(x - x32) + c*(x - x32)^2     -> b (tangent slope at the 32-bit rung mean)
  M3  leave-one-rung-out frozen fits (S6, S7, S4) and 16..32
  M4  paired same-curve differences (frozen fit of the difference series): the even-m gap
      net of lower-order terms shared by arities on identical (bits, curve) instances
  M5  exact OLS attribution of the observed slope into components:
        log2 ratio = log2(S/search) + log2(search/attempts) + log2(attempts/r)
                     + 0.5*log2(r/|F|) + 0.5*log2|F| - 0.5*log2N - 1
      against the model's component values at the design's own |F| slope b_F
  M6  model value at the committed design (no cost measurement enters):
        theta_design = 1/2 + (1/2 - h) * b_F,  b_F = OLS slope of log2 fb_size on log2N,
      fb_size = max(4, ceil(((m! N)/2)^(1/m)/2)) (deterministic in N; checked in check_pipeline).
      This is the model S ~ attempts*|F|^(m-h), attempts ~ r*N/|F|^m, r ~ |F|, table ignored.
      theta_star adds the table: ratio_model = (cT*F^h + cS*r*N*F^-h) / (0.5*sqrt(r*N)) with the
      theory exponents and cT, cS calibrated as geometric means of the committed table and
      search columns (exponents are not fitted); theta_star = OLS slope of log2 ratio_model.
  M7  |F|-adjusted residual slope: y - [0.5*log2N + (0.5-h)*log2 fb_size] against log2N
      (model value 0 for a search-dominated even-m series), frozen bootstrap.
No randomness beyond the frozen bootstrap seed 0.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
names = list(C.SERIES)


def fb(xs, ys, gs):
    return stats.bootstrap_slope(list(xs), list(ys), groups=list(gs), reps=C.REPS, level=C.LEVEL, seed=C.SEED)


def lstsq_coef(X, y):
    return np.linalg.lstsq(X, y, rcond=None)[0]


def y_of(r):
    return math.log2(C.ratio(r))


res = {"series": {}, "loro": {}, "paired": {}}
for name in names:
    f, m, fbase = C.SERIES[name]
    h = C.table_arity(m)
    theta = C.model_value(m)
    out = {"m": m, "h": h, "theta_asymptotic": theta}
    for label, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
        rows = C.series_rows(name, lo)
        x = np.array([r["log2N"] for r in rows])
        y = np.array([y_of(r) for r in rows])
        g = [r["bits"] for r in rows]
        F = np.array([r["fb_size"] for r in rows], float)
        rr = np.array([r["relations"] for r in rows], float)
        N = np.array([r["N"] for r in rows], float)
        S = np.array([r["s3_solves"] for r in rows], float)
        T = np.array([r["table_s3_solves"] for r in rows], float)
        A = np.array([r["attempts"] for r in rows], float)
        srch = S - T
        frozen = fb(x, y, g)
        cell = {"frozen": frozen}
        # M1 / M2
        X1 = np.column_stack([np.ones_like(x), x, 1 / x])
        b1 = float(lstsq_coef(X1, y)[1])
        lo1, hi1 = C.stratified_boot_generic(lambda idx: float(lstsq_coef(X1[idx], y[idx])[1]), g)
        x32 = float(x[np.array(g) == 32].mean())
        X2 = np.column_stack([np.ones_like(x), x - x32, (x - x32) ** 2])
        b2 = float(lstsq_coef(X2, y)[1])
        lo2, hi2 = C.stratified_boot_generic(lambda idx: float(lstsq_coef(X2[idx], y[idx])[1]), g)
        cell["M1_inverse_x_term"] = {"b_asymptotic": b1, "lo": lo1, "hi": hi1,
                                     "contains_theta": lo1 <= theta <= hi1}
        cell["M2_quadratic_slope_at_32bit_rung"] = {"x_at": x32, "b": b2, "lo": lo2, "hi": hi2,
                                                   "contains_theta": lo2 <= theta <= hi2}
        # M5 attribution
        bF = C.ols(x, np.log2(F))[0]
        comp = {
            "t1_log2_S_over_search": C.ols(x, np.log2(S / srch))[0],
            "t2_log2_search_per_attempt": C.ols(x, np.log2(srch / A))[0],
            "t3_log2_attempts_per_relation": C.ols(x, np.log2(A / rr))[0],
            "t4_half_log2_r_over_F": 0.5 * C.ols(x, np.log2(rr / F))[0],
            "t5_half_log2_F": 0.5 * bF,
            "t6_minus_half_log2N": -0.5,
        }
        model_comp = {"t1_log2_S_over_search": 0.0, "t2_log2_search_per_attempt": (m - h) * bF,
                      "t3_log2_attempts_per_relation": 1 - m * bF, "t4_half_log2_r_over_F": 0.0,
                      "t5_half_log2_F": 0.5 * bF, "t6_minus_half_log2N": -0.5}
        cell["M5_attribution"] = {"observed": comp, "observed_sum": sum(comp.values()),
                                  "model_at_design_bF": model_comp,
                                  "observed_minus_model": {k: comp[k] - model_comp[k] for k in comp},
                                  "table_share_median_by_rung": {
                                      int(b): float(np.median((T / S)[np.array(g) == b])) for b in sorted(set(g))}}
        # M6 design model values
        theta_design = 0.5 + (0.5 - h) * bF
        cT = 2 ** float(np.mean(np.log2(T) - h * np.log2(F)))
        cS = 2 ** float(np.mean(np.log2(srch) - np.log2(rr) - np.log2(N) + h * np.log2(F)))
        ymodel = np.log2((cT * F ** h + cS * rr * N * F ** (-h)) / (0.5 * np.sqrt(rr * N)))
        theta_star = C.ols(x, ymodel)[0]
        cell["M6_design_model_value"] = {
            "b_F": bF, "one_over_m": 1 / m, "theta_design_search_only": theta_design,
            "theta_star_table_plus_search": theta_star, "cT": cT, "cS": cS,
            "frozen_interval_contains_theta_asymptotic": frozen["lo"] <= theta <= frozen["hi"],
            "frozen_interval_contains_theta_design": frozen["lo"] <= theta_design <= frozen["hi"],
            "frozen_interval_contains_theta_star": frozen["lo"] <= theta_star <= frozen["hi"]}
        # M7 |F|-adjusted residual slope (model 0 for search-dominated series)
        yadj = y - (0.5 * x + (0.5 - h) * np.log2(F))
        adj = fb(x, yadj, g)
        cell["M7_F_adjusted_residual_slope"] = {**adj, "model": 0.0, "contains_model": adj["lo"] <= 0.0 <= adj["hi"],
                                                "note": "search-only model; exact for the even-m series only up to the table share"}
        out[label] = cell
        print(name, label, "frozen %.4f [%.4f, %.4f] theta=%.4f | 1/x: %.4f [%.4f, %.4f] | quad@32: %.4f [%.4f, %.4f]"
              " | bF=%.4f theta_design=%.4f theta_star=%.4f | adj %.4f [%.4f, %.4f]" % (
                  frozen["slope"], frozen["lo"], frozen["hi"], theta, b1, lo1, hi1, b2, lo2, hi2, bF, theta_design,
                  theta_star, adj["slope"], adj["lo"], adj["hi"]), flush=True)
    res["series"][name] = out

# M3 leave-one-rung-out
for name in ("S6-smallx", "S7-smallx", "S4-smallx"):
    theta = C.model_value(C.SERIES[name][1])
    rows = C.series_rows(name)
    d = {}
    for drop in [None, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, "12+14"]:
        dropset = {12, 14} if drop == "12+14" else ({drop} if drop is not None else set())
        sel = [r for r in rows if r["bits"] not in dropset]
        xs, ys, gs = C.xs_ys(sel)
        v = fb(xs, ys, gs)
        v["excludes_theta"] = not (v["lo"] <= theta <= v["hi"])
        d[str(drop)] = v
    res["loro"][name] = d
    print("LORO", name, {k: "%.4f[%.4f,%.4f]%s" % (v["slope"], v["lo"], v["hi"], "X" if v["excludes_theta"] else "")
                          for k, v in d.items()}, flush=True)

# M4 paired same-curve differences
PAIRS = [("S6-smallx", "S7-smallx"), ("S6-smallx", "S5-smallx"), ("S4-smallx", "S5-smallx"),
         ("S4-smallx", "S3-smallx-unfiltered"), ("S6-smallx", "S4-smallx"),
         ("S7-smallx", "S5-smallx"), ("S5-smallx", "S3-smallx-unfiltered"), ("S7-smallx", "S3-smallx-unfiltered")]
for A_, B_ in PAIRS:
    mA, mB = C.SERIES[A_][1], C.SERIES[B_][1]
    th = C.model_value(mA) - C.model_value(mB)
    d = {"model_difference_asymptotic": th}
    for label, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
        ra = C.series_rows(A_, lo)
        rb = {(r["bits"], r["curve"]): r for r in C.series_rows(B_, lo)}
        assert all((r["p"], r["N"]) == (rb[(r["bits"], r["curve"])]["p"], rb[(r["bits"], r["curve"])]["N"]) for r in ra)
        xs = [r["log2N"] for r in ra]
        ys = [y_of(r) - y_of(rb[(r["bits"], r["curve"])]) for r in ra]
        gs = [r["bits"] for r in ra]
        v = fb(xs, ys, gs)
        # design model difference
        tdA = res["series"][A_][label]["M6_design_model_value"]
        tdB = res["series"][B_][label]["M6_design_model_value"]
        v["model_difference_design_search_only"] = tdA["theta_design_search_only"] - tdB["theta_design_search_only"]
        v["model_difference_design_star"] = tdA["theta_star_table_plus_search"] - tdB["theta_star_table_plus_search"]
        v["contains_asymptotic"] = v["lo"] <= th <= v["hi"]
        v["contains_design_star"] = v["lo"] <= v["model_difference_design_star"] <= v["hi"]
        d[label] = v
    res["paired"][f"{A_} minus {B_}"] = d
    print("PAIR", A_, "-", B_, "model %.4f" % th, {k: "%.4f[%.4f,%.4f] design*=%.4f" % (
        v["slope"], v["lo"], v["hi"], v["model_difference_design_star"]) for k, v in d.items() if isinstance(v, dict)},
        flush=True)

print(C.dump("j4_lower_order.json", res))
