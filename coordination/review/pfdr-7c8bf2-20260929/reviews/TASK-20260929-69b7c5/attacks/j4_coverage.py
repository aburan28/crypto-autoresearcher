"""J4 + proves_too_much: coverage of the frozen interval procedure on the archived designs.

For every primary series and both ranges (12..32 primary, 20..32 sensitivity):
  design     = the series' own rows (log2N values, bits strata, row order) -- fixed.
  truth      = model value theta (0 at odd m, 1/(2m) at even m) by construction.
  noise      R1 (plan): residuals of the series' own OLS fit on that range, resampled with
                  replacement within rung;
             R2 (plan): pooled Gaussian, sigma^2 = RSS/(n-2) of that fit;
             R3 (added): per-rung Gaussian with the rung's own sample SD (ddof=1) of the
                  observed y -- pure within-rung scatter, heteroscedastic, no lack-of-fit.
  procedure  = stats.bootstrap_slope(xs, ys, groups=bits, reps=2000, level=0.95, seed=0),
               evaluated through common.FastBoot (exact linear form of the same draws);
               literal equality is re-checked on the first 200 replicates of S6/S4/S7 x R1/R2.
Reports: coverage of theta, P(lo > theta), P(hi < theta), mean width vs observed width,
ratio of bootstrap SD to the true sampling SD of the slope.

Family-wise (primary range, all eight series, every theta true):
  independent draws per series, and JOINT draws that resample the same curve index for
  every series of a curve set (filtered: 3 series; unfiltered: 5 series share (bits, curve)
  instances), so cross-series residual correlation on shared curves is preserved (R1-joint),
  plus a correlated-Gaussian version with the pooled cross-series correlation (R3-joint).

Seeds: numpy default_rng([0x69b7c5, series_index, range_index, model_index]) for the
synthetic noise; family-wise rng([0x69b7c5, 99, model_index]).  K = 20000 per cell.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

K = 20000
K_LITERAL = 200
stats = C.load_stats()
names = list(C.SERIES)
RANGES = {"primary_12_32": 12, "sensitivity_20_32": 20}


def design(name, lo):
    rows = C.series_rows(name, lo)
    xs, ys, gs = C.xs_ys(rows)
    return rows, np.array(xs), np.array(ys), gs


def noise_R1(rng, resid, gs, K):
    """Resample residuals with replacement within rung (each position draws independently)."""
    gs = np.asarray(gs)
    E = np.empty((K, len(resid)))
    for g in np.unique(gs):
        pos = np.where(gs == g)[0]
        pick = rng.integers(0, len(pos), size=(K, len(pos)))
        E[:, pos] = resid[pos][pick]
    return E


def noise_R2(rng, sigma, n, K):
    return rng.normal(0.0, sigma, size=(K, n))


def noise_R3(rng, ys, gs, K):
    gs = np.asarray(gs)
    E = np.empty((K, len(ys)))
    for g in np.unique(gs):
        pos = np.where(gs == g)[0]
        sd = ys[pos].std(ddof=1)
        E[:, pos] = rng.normal(0.0, sd, size=(K, len(pos)))
    return E


def summarize(theta, s, lo, hi, obs_width):
    K_ = len(s)
    cov = float(np.mean((lo <= theta) & (theta <= hi)))
    p_lo_above = float(np.mean(lo > theta))
    p_hi_below = float(np.mean(hi < theta))
    true_sd = float(np.std(s, ddof=1))
    # bootstrap SD is not returned by the frozen function; use width/(2*1.96) as its proxy
    width = hi - lo
    return {"K": K_, "coverage": cov, "coverage_mc_se": math.sqrt(cov * (1 - cov) / K_),
            "p_exclude": 1 - cov, "p_lo_above_theta": p_lo_above, "p_hi_below_theta": p_hi_below,
            "mean_slope": float(np.mean(s)), "true_sd_of_slope": true_sd,
            "mean_width": float(np.mean(width)), "observed_width": obs_width,
            "mean_width_over_2x1.96x_true_sd": float(np.mean(width) / (2 * 1.96 * true_sd))}


results = {"K": K, "per_series": {}, "literal_check": {}, "family_wise": {}}
for si, name in enumerate(names):
    f, m, fb = C.SERIES[name]
    theta = C.model_value(m)
    results["per_series"][name] = {"m": m, "theta": theta}
    for ri, (label, lo_b) in enumerate(RANGES.items()):
        rows, xs, ys, gs = design(name, lo_b)
        b, a = C.ols(xs, ys)
        resid = ys - (a + b * xs)
        sigma = math.sqrt(float((resid ** 2).sum()) / (len(ys) - 2))
        fbt = C.FastBoot(xs, gs)
        s0, l0, h0 = fbt.interval([ys])
        cell = {"observed": {"slope": float(s0[0]), "lo": float(l0[0]), "hi": float(h0[0])},
                "resid_sigma": sigma}
        base = a + theta * xs
        for mi, (mname, gen) in enumerate((
                ("R1_within_rung_residual_resample", lambda rng: noise_R1(rng, resid, gs, K)),
                ("R2_pooled_gaussian", lambda rng: noise_R2(rng, sigma, len(ys), K)),
                ("R3_per_rung_gaussian", lambda rng: noise_R3(rng, ys, gs, K)))):
            rng = np.random.default_rng([0x69b7c5, si, ri, mi])
            Y = base[None, :] + gen(rng)
            s, lo, hi = fbt.interval(Y)
            cell[mname] = summarize(theta, s, lo, hi, float(h0[0] - l0[0]))
            if label == "primary_12_32" and name in ("S6-smallx", "S4-smallx", "S7-smallx") and mi < 2:
                lit = [stats.bootstrap_slope(list(xs), list(Y[k]), groups=gs, reps=C.REPS,
                                             level=C.LEVEL, seed=C.SEED) for k in range(K_LITERAL)]
                L = np.array([[d["slope"], d["lo"], d["hi"]] for d in lit])
                diff = float(np.max(np.abs(L - np.stack([s[:K_LITERAL], lo[:K_LITERAL], hi[:K_LITERAL]], 1))))
                covl = float(np.mean((L[:, 1] <= theta) & (theta <= L[:, 2])))
                results["literal_check"][f"{name}|{mname}"] = {
                    "n_literal": K_LITERAL, "max_abs_diff_fast_vs_literal": diff,
                    "literal_coverage_first_200": covl,
                    "literal_p_lo_above_theta_first_200": float(np.mean(L[:, 1] > theta)),
                    "literal_p_hi_below_theta_first_200": float(np.mean(L[:, 2] < theta))}
        results["per_series"][name][label] = cell
        print(name, label, "obs [%.4f, %.4f]" % (l0[0], h0[0]),
              " | ".join("%s cov=%.3f lo>th=%.3f hi<th=%.3f w/w*=%.2f" % (
                  k[:2], v["coverage"], v["p_lo_above_theta"], v["p_hi_below_theta"],
                  v["mean_width_over_2x1.96x_true_sd"])
                  for k, v in cell.items() if k.startswith("R")), flush=True)

# ---------------------------------------------------------------- family-wise (primary range)
prim = {}
for name in names:
    rows, xs, ys, gs = design(name, 12)
    b, a = C.ols(xs, ys)
    resid = ys - (a + b * xs)
    prim[name] = {"rows": rows, "xs": xs, "ys": ys, "gs": gs, "a": a, "resid": resid,
                  "theta": C.model_value(C.SERIES[name][1]), "fbt": C.FastBoot(xs, gs),
                  "keys": [(r["bits"], r["curve"]) for r in rows]}

# empirical cross-series residual correlation on shared (bits, curve)
corr = {}
for setname in ("filtered", "unfiltered"):
    mem = [n for n in names if C.CURVE_SET[n] == setname]
    keys = prim[mem[0]]["keys"]
    Rm = np.array([[dict(zip(prim[n]["keys"], prim[n]["resid"]))[k] for k in keys] for n in mem])
    # standardize within rung to remove heteroscedasticity before correlating
    gs = np.array([k[0] for k in keys])
    Z = Rm.copy()
    for g in np.unique(gs):
        pos = gs == g
        Z[:, pos] = (Rm[:, pos] - Rm[:, pos].mean(1, keepdims=True)) / Rm[:, pos].std(1, ddof=1, keepdims=True)
    cm = np.corrcoef(Z)
    corr[setname] = {"series": mem, "within_rung_standardized_residual_correlation": cm.round(3).tolist()}
results["family_wise"]["residual_correlation"] = corr


def fw_run(model, joint, seed_idx):
    rng = np.random.default_rng([0x69b7c5, 99, seed_idx])
    excl = {}
    for setname in ("filtered", "unfiltered"):
        mem = [n for n in names if C.CURVE_SET[n] == setname]
        keys = prim[mem[0]]["keys"]
        gs = np.array([k[0] for k in keys])
        if model == "R1":
            def draw_pick():
                """Per replicate and position, a source curve (same rung) whose residual is used."""
                pk = np.empty((K, len(keys)), dtype=int)
                for g in np.unique(gs):
                    pos = np.where(gs == g)[0]
                    pk[:, pos] = pos[rng.integers(0, len(pos), size=(K, len(pos)))]
                return pk
            shared = draw_pick() if joint else None  # joint: one pick shared by the whole curve set
            for n in mem:
                P = prim[n]
                order = [keys.index(k) for k in P["keys"]]  # set key order -> series row order
                rkey = np.array([dict(zip(P["keys"], P["resid"]))[k] for k in keys])
                pk = shared if joint else draw_pick()
                E = rkey[pk][:, order]
                Y = (P["a"] + P["theta"] * P["xs"])[None, :] + E
                _, lo, hi = P["fbt"].interval(Y)
                excl[n] = (lo > P["theta"]) | (hi < P["theta"])
        else:  # R3: per-rung Gaussian scale, correlated across the set if joint
            cm = np.array(corr[setname]["within_rung_standardized_residual_correlation"]) if joint else np.eye(len(mem))
            Lc = np.linalg.cholesky(cm + 1e-12 * np.eye(len(mem)))
            Zs = rng.standard_normal((K, len(keys), len(mem))) @ Lc.T  # (K, positions, series)
            for j, n in enumerate(mem):
                P = prim[n]
                order = [keys.index(k) for k in P["keys"]]
                ykey = np.array([dict(zip(P["keys"], P["ys"]))[k] for k in keys])
                sd = np.empty(len(keys))
                for g in np.unique(gs):
                    pos = gs == g
                    sd[pos] = ykey[pos].std(ddof=1)
                E = (Zs[:, :, j] * sd[None, :])[:, order]
                Y = (P["a"] + P["theta"] * P["xs"])[None, :] + E
                _, lo, hi = P["fbt"].interval(Y)
                excl[n] = (lo > P["theta"]) | (hi < P["theta"])
    M = np.stack([excl[n] for n in names], 1)
    any_ = M.any(1)
    even = M[:, [i for i, n in enumerate(names) if C.SERIES[n][1] % 2 == 0]].any(1)
    odd = M[:, [i for i, n in enumerate(names) if C.SERIES[n][1] % 2 == 1]].any(1)
    return {"K": K, "p_at_least_one_of_8": float(any_.mean()),
            "mc_se": math.sqrt(any_.mean() * (1 - any_.mean()) / K),
            "p_at_least_one_even_m": float(even.mean()), "p_at_least_one_odd_m": float(odd.mean()),
            "p_exactly_one": float((M.sum(1) == 1).mean()),
            "mean_number_of_exclusions": float(M.sum(1).mean()),
            "per_series_p_exclude": {n: float(M[:, i].mean()) for i, n in enumerate(names)},
            "independence_formula_from_per_series": float(1 - np.prod([1 - M[:, i].mean() for i in range(len(names))]))}


for idx, (model, joint) in enumerate((("R1", False), ("R1", True), ("R3", False), ("R3", True))):
    key = f"{model}_{'joint_shared_curves' if joint else 'independent'}"
    results["family_wise"][key] = fw_run(model, joint, idx)
    v = results["family_wise"][key]
    print("FW", key, "P(>=1 of 8)=%.3f +- %.3f even=%.3f odd=%.3f E[#]=%.3f" % (
        v["p_at_least_one_of_8"], v["mc_se"], v["p_at_least_one_even_m"], v["p_at_least_one_odd_m"],
        v["mean_number_of_exclusions"]), flush=True)

print(C.dump("j4_coverage.json", results))
for k, v in results["literal_check"].items():
    print("literal", k, v)
