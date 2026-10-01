#!/usr/bin/env python3
"""NON-PROTOCOL power and proves-too-much check for the EXP-ICEX-153c34 design.

Every number this script uses is synthetic. It draws no protocol label, uses no
fixture of any experiment and reads no run output. The RNG seed is the fixed
integer below, labelled NON-PROTOCOL, and is not an EXP-ICEX-153c34 label.

What it checks (TASK-20261001-768475, DEC-20261001-9e675e NA-2):
  1. Calibration: the RUN-ICEX-0ad4d8-style analysis (6 fixtures, 16/20 bits,
     unstratified fixture bootstrap) at SD 0.78 must show the ~9% power the
     validator reported, so the simulator is comparable.
  2. The frozen exponent-panel analysis of EXP-ICEX-153c34 (5 sizes x 4
     fixtures, frozen L series, between-size slope, within-size bootstrap AND
     a within-size t interval, favourable only if both agree): power against a
     planted 0.40 and false-favourable rates at planted 0.50 and 0.60, at SD
     0.095 (residual given L in RUN-ICEX-0ad4d8), 0.20 (design expectation),
     0.40 and 0.78 (RUN-ICEX-0ad4d8 unconditioned residual).
  3. Reduced panels (impediment fallbacks): sizes 16-22 and 16-20.
  4. Proves-too-much objects for the decision rule: a fixed per-fixture setup
     cost (EV-ICEX-16e3ec F-2) and a constant per-query cost term, each with a
     true exponent >= 1, must not be called favourable by the frozen rule.
Run: TMPDIR=/Volumes/SSD990/.tmp-agent nice -n 10 python3 power_check.py
"""
from __future__ import annotations

import json
import math
import sys
import time

import numpy as np

SEED_NON_PROTOCOL = 768475_2026_1001
SIZES = [16, 18, 20, 22, 24]
T_15 = 2.131449545559323   # t_{0.975, 15}


def b_star(bits):
    """B*(b) = ceil((2^(b-0.5))^(1/5)), exact integer search."""
    target = 2 ** (bits - 0.5)
    b = int(target ** 0.2)
    while b ** 5 < target:
        b += 1
    return b


def window(bits):
    lo = max((b_star(bits) - 1) ** 5 + 1, 2 ** (bits - 1))
    hi = min(b_star(bits) ** 5, 2 ** bits - 1)
    return lo, hi


def l_star(bits):
    return (b_star(bits) + 1) // 2


def sample_lnq(rng, sizes, k):
    """ln q per fixture, q uniform in the frozen p window of its size."""
    out = np.empty((len(sizes), k))
    for i, b in enumerate(sizes):
        lo, hi = window(b)
        out[i] = np.log(rng.uniform(lo, hi, size=k))
    return out


def path_means(sizes):
    mu = []
    for b in sizes:
        lo, hi = window(b)
        xs = np.linspace(lo, hi, 4001)
        mu.append(float(np.mean(np.log(xs))))
    return np.array(mu)


def between_slope(xbar, ybar):
    """OLS slope of size means; xbar, ybar shape (..., S)."""
    xc = xbar - xbar.mean(axis=-1, keepdims=True)
    yc = ybar - ybar.mean(axis=-1, keepdims=True)
    return (xc * yc).sum(axis=-1) / (xc * xc).sum(axis=-1)


def analyse(lnq, y, rng, n_boot):
    """Frozen EXP-ICEX-153c34 exponent analysis on one panel.

    Returns slope, bootstrap percentile CI and within-size t CI."""
    S, k = lnq.shape
    xbar, ybar = lnq.mean(axis=1), y.mean(axis=1)
    slope = float(between_slope(xbar, ybar))
    idx = rng.integers(0, k, size=(n_boot, S, k))
    rows = np.arange(S)[None, :, None]
    bx = lnq[rows, idx].mean(axis=2)
    by = y[rows, idx].mean(axis=2)
    bs = between_slope(bx, by)
    lo_b, hi_b = np.quantile(bs, [0.025, 0.975])
    w = (xbar - xbar.mean()) / ((xbar - xbar.mean()) ** 2).sum()
    resid = y - y.mean(axis=1, keepdims=True)
    sp2 = (resid ** 2).sum() / (S * k - S)
    se = math.sqrt(sp2 / k * (w ** 2).sum())
    df = S * k - S
    tq = T_15 if df == 15 else t_quantile(df)
    return slope, (float(lo_b), float(hi_b)), (slope - tq * se, slope + tq * se)


def t_quantile(df):
    table = {9: 2.262157162740992, 12: 2.178812829663418, 15: T_15,
             35: 2.030107928250342, 75: 1.992102454547332}
    return table[df]


def verdict(slope, ci_b, ci_t):
    if ci_b[1] < 0.5 and ci_t[1] < 0.5:
        return "favourable"
    if ci_b[0] >= 0.5 and ci_t[0] >= 0.5:
        return "unfavourable"
    return "inconclusive"


def simulate_panel(rng, sizes, k, beta, sd, reps, n_boot, within_slope=1.0):
    mu = path_means(sizes)
    counts = {"favourable": 0, "unfavourable": 0, "inconclusive": 0}
    boot_only_fav = t_only_fav = 0
    slopes = []
    for _ in range(reps):
        lnq = sample_lnq(rng, sizes, k)
        y = 5.0 + beta * mu[:, None] + within_slope * (lnq - mu[:, None]) + rng.normal(0, sd, size=lnq.shape)
        s, cb, ct = analyse(lnq, y, rng, n_boot)
        slopes.append(s)
        counts[verdict(s, cb, ct)] += 1
        boot_only_fav += cb[1] < 0.5
        t_only_fav += ct[1] < 0.5
    return {
        "reps": reps, "n_boot": n_boot,
        "rate_favourable_frozen_rule": counts["favourable"] / reps,
        "rate_unfavourable_frozen_rule": counts["unfavourable"] / reps,
        "rate_inconclusive": counts["inconclusive"] / reps,
        "rate_upper_below_half_bootstrap_only": boot_only_fav / reps,
        "rate_upper_below_half_t_only": t_only_fav / reps,
        "slope_mean": float(np.mean(slopes)), "slope_sd": float(np.std(slopes)),
    }


def naive_pooled_bias(rng, sizes, k, beta, sd, reps):
    """Pooled OLS on all fixtures (rejected estimator): bias from within-size slope 1."""
    mu = path_means(sizes)
    sl = []
    for _ in range(reps):
        lnq = sample_lnq(rng, sizes, k)
        y = 5.0 + beta * mu[:, None] + (lnq - mu[:, None]) + rng.normal(0, sd, size=lnq.shape)
        x, yy = lnq.ravel(), y.ravel()
        sl.append(np.polyfit(x, yy, 1)[0])
    return {"planted": beta, "sd": sd, "pooled_ols_mean_slope": float(np.mean(sl)),
            "between_size_estimator_is_frozen": True}


def v4_calibration(rng, sd, beta, reps, n_boot):
    """RUN-ICEX-0ad4d8-style: 3 fixtures at 16 and 20 bits, pooled OLS slope,
    unstratified fixture bootstrap (single-size resamples allowed)."""
    fav = 0
    for _ in range(reps):
        lnq = np.concatenate([np.log(rng.uniform(2 ** 15, 2 ** 16, 3)), np.log(rng.uniform(2 ** 19, 2 ** 20, 3))])
        y = 3.0 + beta * lnq + rng.normal(0, sd, 6)
        idx = rng.integers(0, 6, size=(n_boot, 6))
        bx, by = lnq[idx], y[idx]
        xc = bx - bx.mean(axis=1, keepdims=True)
        den = (xc * xc).sum(axis=1)
        ok = den > 1e-12
        bs = (xc * (by - by.mean(axis=1, keepdims=True))).sum(axis=1)[ok] / den[ok]
        hi = np.quantile(bs, 0.975)
        fav += hi < 0.5
    return {"design": "RUN-ICEX-0ad4d8 style (6 fixtures, 2 sizes, unstratified bootstrap)",
            "planted": beta, "sd": sd, "rate_upper_below_half": fav / reps, "reps": reps}


def a_attempts(bits, q):
    L = l_star(bits)
    return q / (0.65 * math.comb(2 * L + 4, 5))


def proves_too_much(rng, reps, n_boot, sd=0.20):
    """Decision-rule controls. True asymptotic exponent >= 1 in both objects."""
    sizes, k = SIZES, 4
    mu = path_means(sizes)
    res = {}
    # PT-1: fixed per-fixture setup cost K (constant in q) on top of a variable
    # membership cost with planted exponent 1.0; K = 10x the 16-bit variable cost.
    for mult in (10, 1000):
        rates = {"complete_cost_fit_favourable": 0, "variable_cost_fit_favourable": 0}
        comp_slopes = []
        for _ in range(reps):
            lnq = sample_lnq(rng, sizes, k)
            yvar = 5.0 + 1.0 * mu[:, None] + (lnq - mu[:, None]) + rng.normal(0, sd, lnq.shape)
            K = mult * math.exp(5.0 + 1.0 * mu[0])
            ycomp = np.log(np.exp(yvar) + K)
            s, cb, ct = analyse(lnq, ycomp, rng, n_boot)
            comp_slopes.append(s)
            rates["complete_cost_fit_favourable"] += verdict(s, cb, ct) == "favourable"
            s, cb, ct = analyse(lnq, yvar, rng, n_boot)
            rates["variable_cost_fit_favourable"] += verdict(s, cb, ct) == "favourable"
        res[f"PT-1_fixed_setup_flattening_x{mult}"] = {
            "object": f"variable membership cost exponent 1.0 plus constant per-fixture setup = {mult}x the 16-bit variable cost",
            "reps": reps,
            "complete_cost_slope_mean": float(np.mean(comp_slopes)),
            "false_favourable_if_fit_on_complete_cost": rates["complete_cost_fit_favourable"] / reps,
            "false_favourable_frozen_rule_variable_cost": rates["variable_cost_fit_favourable"] / reps,
        }
    # PT-2: constant per-query term c_spec (q-independent specialisation work)
    # plus a grid term ~ L*^5 per attempt; c_spec = 100 x the 16-bit grid term.
    c_grid = 1.0
    c_spec = 100.0 * c_grid * l_star(16) ** 5
    naive = guard_b = guard_c = frozen = 0
    slopes_naive, slopes_grid = [], []
    for _ in range(reps):
        lnq = sample_lnq(rng, sizes, k)
        q = np.exp(lnq)
        noise = rng.normal(0, sd, lnq.shape)
        L = np.array([l_star(b) for b in sizes], dtype=float)[:, None]
        A = np.array([[a_attempts(b, qq) for qq in row] for b, row in zip(sizes, q)])
        y_tot = np.log((L + 27) * A * (c_spec + c_grid * L ** 5)) + noise
        y_grid = np.log((L + 27) * A * (c_grid * L ** 5)) + noise
        s, cb, ct = analyse(lnq, y_tot, rng, n_boot)
        v_tot = verdict(s, cb, ct) == "favourable"
        slopes_naive.append(s)
        s2, cb2, ct2 = analyse(lnq, y_grid, rng, n_boot)
        v_grid = verdict(s2, cb2, ct2) == "favourable"
        slopes_grid.append(s2)
        # absolute guard: membership cost per success with setup below T on every 24-bit fixture
        T = 13 * 0.886 * np.sqrt(q[-1]) / (L[-1] + 27)
        Ms = np.exp(y_tot[-1]) / (L[-1] + 27)
        v_abs = bool(np.all(Ms < T))
        naive += v_tot
        guard_b += v_tot and v_grid
        guard_c += v_tot and v_abs
        frozen += v_tot and v_grid and v_abs
    res["PT-2_constant_per_query_term"] = {
        "object": "per-attempt cost = c_spec + L*^5 with c_spec = 100 x 16-bit grid term; attempts/success from C(2L*+4,5)/q at yield factor 0.65; asymptotic exponent > 1",
        "reps": reps,
        "naive_slope_mean": float(np.mean(slopes_naive)),
        "grid_component_slope_mean": float(np.mean(slopes_grid)),
        "false_favourable_naive_total_variable_cost": naive / reps,
        "false_favourable_with_grid_component_guard": guard_b / reps,
        "false_favourable_with_absolute_threshold_guard": guard_c / reps,
        "false_favourable_frozen_rule_all_guards": frozen / reps,
    }
    return res


def main():
    t0 = time.time()
    rng = np.random.default_rng(SEED_NON_PROTOCOL)
    out = {
        "label": "NON-PROTOCOL synthetic cost tables; no fixture, label or run output used",
        "seed_non_protocol": SEED_NON_PROTOCOL,
        "panel": {str(b): {"B_star": b_star(b), "L_star": l_star(b), "p_window": window(b)} for b in SIZES},
        "calibration_v4_style": {},
        "frozen_design_5x4": {},
        "fallback_panels": {},
        "more_fixtures_at_sd_0.78": {},
        "pooled_ols_rejected": [],
    }
    R, NB = 2000, 2000
    for beta in (0.40, 0.50, 0.60):
        out["calibration_v4_style"][f"beta_{beta:.2f}"] = v4_calibration(rng, 0.78, beta, R, NB)
    for sd in (0.095, 0.20, 0.40, 0.78):
        for beta in (0.40, 0.50, 0.60):
            out["frozen_design_5x4"][f"sd_{sd}_beta_{beta:.2f}"] = simulate_panel(rng, SIZES, 4, beta, sd, R, NB)
    for name, sizes in (("sizes_16_18_20_22", SIZES[:4]), ("sizes_16_18_20", SIZES[:3])):
        for sd in (0.20, 0.78):
            for beta in (0.40, 0.50, 0.60):
                out["fallback_panels"][f"{name}_sd_{sd}_beta_{beta:.2f}"] = simulate_panel(
                    rng, sizes, 4, beta, sd, 1000, 1000)
    for k in (8, 16):
        for beta in (0.40, 0.50):
            out["more_fixtures_at_sd_0.78"][f"k_{k}_beta_{beta:.2f}"] = simulate_panel(
                rng, SIZES, k, beta, 0.78, 1000, 1000)
    for beta in (0.40, 0.60):
        out["pooled_ols_rejected"].append(naive_pooled_bias(rng, SIZES, 4, beta, 0.20, 1000))
    out["proves_too_much_decision_rule"] = proves_too_much(rng, 1000, 1000)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
