"""J2 red-team scratch analysis for RUN-ICEX-0ad4d8 (TASK-20261001-d367dd).

Reads only the run's own metrics.json, fxa_nonverdict.json and cells/*/result.json.
Performs no scientific run and no frozen-label draw; pure arithmetic on recorded values.
"""
import json
import math
import os
import random
import sys
from math import comb, log

RUN = sys.argv[1]
OUT = sys.argv[2]
M = json.load(open(os.path.join(RUN, "metrics.json")))
FXA = {r["fixture_id"]: r["fxa_nonverdict"]
       for r in json.load(open(os.path.join(RUN, "fxa_nonverdict.json")))["per_fixture"]}
rho = {r["fixture_id"]: r for r in M["rho_baseline"]}
out = {}


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    res = [y - a - b * x for x, y in zip(xs, ys)]
    s2 = sum(r * r for r in res) / (n - 2) if n > 2 else float("nan")
    return b, a, math.sqrt(s2 / sxx), math.sqrt(s2), sxx


def ols2(X, y):
    """least squares with intercept + columns of X (list of lists)."""
    import itertools
    rows = [[1.0] + list(r) for r in X]
    k = len(rows[0])
    A = [[sum(r[i] * r[j] for r in rows) for j in range(k)] for i in range(k)]
    bvec = [sum(r[i] * yy for r, yy in zip(rows, y)) for i in range(k)]
    # gaussian elimination
    for i in range(k):
        p = max(range(i, k), key=lambda r: abs(A[r][i]))
        A[i], A[p] = A[p], A[i]
        bvec[i], bvec[p] = bvec[p], bvec[i]
        for r in range(k):
            if r != i:
                f = A[r][i] / A[i][i]
                A[r] = [a - f * c for a, c in zip(A[r], A[i])]
                bvec[r] -= f * bvec[i]
    beta = [bvec[i] / A[i][i] for i in range(k)]
    res = [yy - sum(b * v for b, v in zip(beta, r)) for r, yy in zip(rows, y)]
    return beta, res


# ---------------------------------------------------------------- per fixture table
cells = {}
for fid in [f["fixture_id"] for f in M["per_fixture"]]:
    cells[fid] = json.load(open(os.path.join(RUN, "cells", f"{fid}__primary", "result.json")))["result"]

rows = []
for pf in M["per_fixture"]:
    fid = pf["fixture_id"]
    c = cells[fid]
    q, L = pf["q"], pf["L"]
    B = c["factor_base"]["B"]
    s1 = c["stage1"]
    att, rel = s1["n_attempts"], s1["n_relations"]
    desc_units = c["descents"]["units"]
    # descent attempt total from FX-A record (rj_descent_attempts counts descent attempts)
    d_att = FXA[fid]["rj_descent_attempts"]
    per_att_s1 = s1["units"] / att
    per_att_d = desc_units / d_att
    yield_s1 = rel / att
    yield_d = 16 / d_att
    pooled_yield = (rel + 16) / (att + d_att)
    succ = rel + 16
    units_per_success = (s1["units"] + desc_units) / succ
    ref = 13 * 0.886 * math.sqrt(q)
    # combinatorial predictions
    n_trip = comb(L + 2, 3)
    n_pair = comb(L + 1, 2)
    pred_scan = n_trip * 8 * (13 + 1) + n_pair * 4 * 13 + L * 2 * 13  # B0 prefix-shared scan
    pred_yield_ub = comb(2 * L + 4, 5) / q  # signed multisets of size 5 over 2L points / q
    rows.append(dict(
        fixture_id=fid, bits=pf["bits"], q=q, B=B, L=L, L_over_B=L / B,
        stage1_attempts=att, relations=rel, descent_attempts=d_att,
        units_per_attempt_stage1=round(per_att_s1, 1),
        units_per_attempt_descent=round(per_att_d, 1),
        predicted_scan_units_excl_Rj=pred_scan,
        yield_stage1=yield_s1, yield_descent=yield_d, yield_pooled=pooled_yield,
        predicted_yield_upper=pred_yield_ub,
        pooled_yield_over_prediction=pooled_yield / pred_yield_ub,
        units_per_successful_membership=round(units_per_success),
        rho_reference_units=ref,
        rho_measured_mean_units=rho[fid]["mean_units"],
        rho_measured_walk_units=rho[fid]["mean_walk_units"],
        one_descent_over_rho_reference=(desc_units / 16) / ref,
        one_descent_over_rho_measured=(desc_units / 16) / rho[fid]["mean_units"],
        complete_units=pf["complete_units"],
        ratio_frozen=pf["ratio"],
        ratio_vs_measured_rho_mean=pf["complete_units"] / rho[fid]["mean_units"],
        ratio_vs_measured_rho_walk=pf["complete_units"] / rho[fid]["mean_walk_units"],
        ratio_fxa_with_descents=FXA[fid]["ratio_rj_incremental_with_descents_nonverdict"],
        ratio_fxa_with_descents_vs_rho_mean=FXA[fid]["complete_units_rj_incremental_with_descents"] / rho[fid]["mean_units"],
        share_b0_membership=(pf["components"]["stage1"] + pf["components"]["descents"]) / pf["complete_units"],
        share_stage3=pf["components"]["stage3"] / pf["complete_units"],
        share_descents=pf["shares"]["descents"],
    ))
out["per_fixture"] = rows

# probe vs point-add share of a scan (13-unit flat charge sensitivity, OQ-1)
for r in rows:
    L = r["L"]
    probes = comb(L + 2, 3) * 8
    r["probe_share_of_scan"] = probes / r["predicted_scan_units_excl_Rj"]

# ---------------------------------------------------------------- 20-bit minimums
b20 = [r for r in rows if r["bits"] == 20]
out["min_20bit"] = {k: min(r[k] for r in b20) for k in
                    ["ratio_frozen", "ratio_vs_measured_rho_mean", "ratio_vs_measured_rho_walk",
                     "ratio_fxa_with_descents", "ratio_fxa_with_descents_vs_rho_mean",
                     "one_descent_over_rho_reference", "one_descent_over_rho_measured"]}
out["min_all"] = {k: min(r[k] for r in rows) for k in out["min_20bit"]}

# ---------------------------------------------------------------- exponent fits
lq = [log(r["q"]) for r in rows]
lc = [log(r["complete_units"]) for r in rows]
lL = [log(r["L"]) for r in rows]
b, a, se, s, sxx = ols(lq, lc)
out["fit_complete_vs_q"] = dict(slope=b, se_ols=se, resid_sd_log=s, sxx=sxx,
                                range_ln_q=max(lq) - min(lq), q_ratio=max(r["q"] for r in rows) / min(r["q"] for r in rows))
# residual vs L
res = [y - a - b * x for x, y in zip(lq, lc)]
bL, aL, seL, sL, _ = ols(lL, res)
out["residual_vs_lnL"] = dict(slope=bL, se=seL, corr=None)
mres, mL = sum(res) / 6, sum(lL) / 6
corr = sum((x - mL) * (y - mres) for x, y in zip(lL, res)) / math.sqrt(
    sum((x - mL) ** 2 for x in lL) * sum((y - mres) ** 2 for y in res))
out["residual_vs_lnL"]["corr"] = corr
beta, res2 = ols2([[x, l] for x, l in zip(lq, lL)], lc)
out["fit_complete_vs_q_and_L"] = dict(intercept=beta[0], coef_lnq=beta[1], coef_lnL=beta[2],
                                      resid_sd_log=math.sqrt(sum(r * r for r in res2) / 3))

# model-based explanation: cost ~ (rel+16 successes) / yield * scan
# test: log(complete) vs log(q * (L+27) * L^3 / C(2L+4,5))
pred = [r["q"] * (r["L"] + 1 + 10 + 16) * r["predicted_scan_units_excl_Rj"] / comb(2 * r["L"] + 4, 5) for r in rows]
bp, ap, sep, sp, _ = ols([log(x) for x in pred], lc)
out["fit_complete_vs_b0_model"] = dict(slope=bp, se=sep, resid_sd_log=sp,
                                       model="q*(L+27)*scan(L)/C(2L+4,5)",
                                       mean_complete_over_model=sum(c / p for c, p in zip([r["complete_units"] for r in rows], pred)) / 6)

# method ceiling: B0 complete cost with L at its expected value ~ (#liftable x < B) ~ B/2, B = ceil(q^(1/5))
def model_cost(q, Lfn):
    L = max(1, Lfn(q))
    return q * (L + 27) * (comb(L + 2, 3) * 112 + comb(L + 1, 2) * 52 + 26 * L) / comb(2 * L + 4, 5)

ceiling = {}
for bits in (16, 20, 24, 28, 32, 40, 48, 64):
    q = 2 ** bits
    B = math.ceil(q ** 0.2)
    L = max(1, round(B / 2))
    y = comb(2 * L + 4, 5) / q
    c = model_cost(q, lambda _q: L)
    ceiling[bits] = dict(B=B, L_expected=L, yield_upper=min(1.0, y), model_units=c,
                         ratio_to_rho_ref=c / (13 * 0.886 * math.sqrt(q)))
out["b0_model_extrapolation"] = ceiling
# local slopes of the model between successive sizes
bl = sorted(ceiling)
out["b0_model_local_slopes"] = {f"{x}-{y}": (log(ceiling[y]["model_units"]) - log(ceiling[x]["model_units"])) / ((y - x) * log(2))
                                for x, y in zip(bl, bl[1:])}

# ---------------------------------------------------------------- rho exponent from the measured cells
rq = [log(r["q"]) for r in M["rho_baseline"]]
for key in ("mean_units", "mean_walk_units"):
    bb, aa, ss, sd, _ = ols(rq, [log(r[key]) for r in M["rho_baseline"]])
    out[f"rho_fit_{key}"] = dict(slope=bb, se=ss, resid_sd_log=sd)

# ---------------------------------------------------------------- power: can 16-20 bits separate 0.5 vs 0.6?
s_obs = out["fit_complete_vs_q"]["resid_sd_log"]
gap = sum(x for x in lq if x > 12) / 3 - sum(x for x in lq if x < 12) / 3
power = {}
for sd in (s_obs, out["fit_complete_vs_q_and_L"]["resid_sd_log"], 0.1):
    # per-size n fixtures, two clusters separated by gap: se = sd*sqrt(2/n)/gap
    need = {}
    for target_halfwidth in (0.1, 0.05):
        n = math.ceil(2 * (1.96 * sd / (target_halfwidth * gap)) ** 2)
        need[str(target_halfwidth)] = n
    power[f"sd={sd:.3f}"] = dict(fixtures_per_size_needed_for_CI_halfwidth=need,
                                 se_slope_with_3_per_size=sd * math.sqrt(2 / 3) / gap)
out["power_two_size_design"] = dict(gap_ln_q=gap, cases=power)

# slope difference 0.5 vs 0.6 over the observed q range -> cost ratio to resolve
out["cost_ratio_separating_0p5_from_0p6_over_range"] = math.exp(0.1 * gap)
out["L_driven_cost_spread_within_size"] = {
    "16": max(r["complete_units"] for r in rows if r["bits"] == 16) / min(r["complete_units"] for r in rows if r["bits"] == 16),
    "20": max(r["complete_units"] for r in rows if r["bits"] == 20) / min(r["complete_units"] for r in rows if r["bits"] == 20)}

# ---------------------------------------------------------------- planted-exponent sanity of the fit design (descriptive only)
rng = random.Random(0xd367dd)
plant = {}
for e in (0.40, 0.50, 0.60):
    hits_excl_below = 0
    hits_excl_above = 0
    T = 400
    for _ in range(T):
        ys = [e * x + rng.gauss(0, s_obs) for x in lq]
        bs = []
        for _b in range(500):
            idx = [rng.randrange(6) for _ in range(6)]
            xs_ = [lq[i] for i in idx]
            if max(xs_) - min(xs_) < 1e-9:
                continue
            bs.append(ols(xs_, [ys[i] for i in idx])[0] if len(set(xs_)) > 1 and len(set(round(v, 6) for v in xs_)) > 1 else None)
        bs = sorted(v for v in bs if v is not None and not math.isnan(v))
        lo, hi = bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs)) - 1]
        hits_excl_below += hi < 0.5
        hits_excl_above += lo >= 0.5
    plant[str(e)] = dict(frac_upperCI_below_half=hits_excl_below / T, frac_lowerCI_at_or_above_half=hits_excl_above / T,
                         trials=T, noise_sd=s_obs, note="my own resampling of 6 fixtures; not the frozen analysis code")
out["planted_exponent_power_at_observed_noise"] = plant

# relation yield: interval FB vs random-x null
out["null_randfb_yield"] = [dict(fixture_id=r["fixture_id"], L=r["L"], interval=r["interval_relation_yield"],
                                 random_x=r["relation_yield"], ratio_interval_over_random=r["interval_relation_yield"] / r["relation_yield"])
                            for r in M["null_randfb"]]
gm = math.exp(sum(log(d["ratio_interval_over_random"]) for d in out["null_randfb_yield"]) / 6)
out["null_randfb_geomean_ratio"] = gm

# stage-cost-only m=6, m=8 vs m=5 stage1 at the same fixture
sc = []
for r in M["stage_cost_only"]:
    p5 = next(x for x in rows if x["fixture_id"] == r["fixture_id"])
    sc.append(dict(fixture_id=r["fixture_id"], m=r["m"], B=r["B"], L=r["L"], attempts=r["attempts"],
                   stage1_units=r["stage1_units"], over_m5_stage1=r["stage1_units"] / cells[r["fixture_id"]]["stage1"]["units"]))
out["stage_cost_m6_m8_vs_m5"] = sc

json.dump(out, open(OUT, "w"), indent=1, default=float)
print(json.dumps(out, indent=1, default=float))
