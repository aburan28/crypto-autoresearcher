#!/usr/bin/env python3
"""
TASK-20260731-003 -- VALIDATOR'S OWN, INDEPENDENT recomputation of the
EXP-SSI-002 / RUN-SSI-002 fit from raw-timings.json ALONE.

fit_analysis.py is NOT imported, NOT copied and NOT called.  Every quantity
below is derived by this file's own route:

  * OLS by explicit second-moment sums (Sxx, Sxy), not by a library solver;
  * residual standard error by its own sum-of-squares;
  * the t quantile from scipy.stats.t (an independent library path);
  * the bootstrap by this file's own resampler;
  * every gate re-evaluated from this file's own numbers.

Outputs independent_fit_output.json: my numbers beside the producer's, with
the signed difference and its size for every compared quantity.
"""

import json
import math
import os
import statistics
import sys

from scipy.stats import t as student_t

RUN = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "../../../../../../../../experiments/EXP-SSI-002/runs/RUN-SSI-002",
)
RUN = os.path.normpath(RUN)

raw = json.load(open(os.path.join(RUN, "raw-timings.json")))
prod = json.load(open(os.path.join(RUN, "fit_report.json")))
prod_ctrl = json.load(open(os.path.join(RUN, "controls.json")))
prod_sum = json.load(open(os.path.join(RUN, "summary.json")))

OUT = {"validator": "TASK-20260731-003", "independent_of": "fit_analysis.py"}


# ---------------------------------------------------------------- primitives
def ols1(xs, ys):
    """Simple linear regression by explicit sums.  My own route."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    a = my - slope * mx
    pred = [a + slope * x for x in xs]
    res = [y - p for y, p in zip(ys, pred)]
    sse = sum(r * r for r in res)
    sst = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst > 0 else 0.0
    dof = n - 2
    rse = math.sqrt(sse / dof) if dof > 0 else float("nan")
    adj = 1.0 - (1.0 - r2) * (n - 1) / dof if dof > 0 else None
    se = rse / math.sqrt(sxx) if dof > 0 else float("nan")
    return {
        "a": a,
        "slope": slope,
        "r2": r2,
        "adj_r2": adj,
        "rse_bits": rse,
        "slope_stderr": se,
        "residuals": res,
        "sse": sse,
        "n": n,
        "df": dof,
    }


def ols0(ys):
    """Null model: intercept only."""
    n = len(ys)
    a = sum(ys) / n
    res = [y - a for y in ys]
    sse = sum(r * r for r in res)
    # two candidate normalisations are both computed and both reported
    return {
        "a": a,
        "residuals": res,
        "sse": sse,
        "n": n,
        "rse_df_n_minus_1": math.sqrt(sse / (n - 1)),
        "rse_df_n_minus_2": math.sqrt(sse / (n - 2)) if n > 2 else None,
        "rse_df_n": math.sqrt(sse / n),
    }


def ci_t(fit, level=0.95):
    q = student_t.ppf(0.5 + level / 2.0, fit["df"])
    return {
        "lo": fit["slope"] - q * fit["slope_stderr"],
        "hi": fit["slope"] + q * fit["slope_stderr"],
        "t_quantile": q,
        "df": fit["df"],
    }


def ci_boot(xs, ys, seed, resamples=2000):
    """My own resampler: python's Mersenne Twister, index resampling."""
    import random

    rng = random.Random(seed)
    n = len(xs)
    slopes = []
    discarded = 0
    for _ in range(resamples):
        idx = [rng.randrange(n) for _ in range(n)]
        if len(set(idx)) < 3:
            discarded += 1
            continue
        sx = [xs[i] for i in idx]
        sy = [ys[i] for i in idx]
        mx = sum(sx) / n
        sxx = sum((x - mx) ** 2 for x in sx)
        if sxx == 0:
            discarded += 1
            continue
        my = sum(sy) / n
        sxy = sum((x - mx) * (y - my) for x, y in zip(sx, sy))
        slopes.append(sxy / sxx)
    slopes.sort()
    if not slopes:
        return {"lo": None, "hi": None, "usable": 0, "discarded": discarded}

    def pct(p):
        k = (len(slopes) - 1) * p
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return slopes[int(k)]
        return slopes[f] * (c - k) + slopes[c] * (k - f)

    return {
        "lo": pct(0.025),
        "hi": pct(0.975),
        "usable": len(slopes),
        "discarded": discarded,
    }


def sign_pattern(res):
    return "".join("+" if r >= 0 else "-" for r in res)


def longest_monotone_run(res):
    """Longest run of consecutive residuals of the same sign."""
    best = cur = 1
    for i in range(1, len(res)):
        if (res[i] >= 0) == (res[i - 1] >= 0):
            cur += 1
            best = max(best, cur)
        else:
            cur = 1
    return best


# --------------------------------------------------- rebuild the cell tables
tmul = {c["log2p_target"]: c["t_mul_s"] for c in raw["ctrl_cal"]}
tinv = {c["log2p_target"]: c["t_inv_s"] for c in raw["ctrl_cal"]}
tnoop = {c["log2p_target"]: c["t_noop_s"] for c in raw["ctrl_cal"]}
null1 = {c["log2p_target"]: c["null1_sha256_4kib_s"] for c in raw["ctrl_null"]}
null2 = {c["log2p_target"]: c["null2_dict_1000_insert_lookup_s"] for c in raw["ctrl_null"]}

cells = raw["cells"]

# ---- raw/summary agreement, and the downsampling audit -----------------
raw_audit = []
for c in cells:
    st = c["steps_downsampled"]
    per_entry = [s["wall_ns"] / 1e9 / s["produced"] for s in st if s["produced"] > 0]
    stats = c["T_entry_s_stats_over_steps"]
    ds = c.get("downsampling", {})
    ent = c["entries_charged_to_timed_windows"]
    tot = c["timed_window_total_s"]
    recomputed_total_over_entries = tot / ent
    # sum of the retained step walls, scaled by the thinning factor, vs the total
    k = ds.get("k", 1)
    sum_kept = sum(s["wall_ns"] for s in st) / 1e9
    entries_kept = sum(s["produced"] for s in st)
    raw_audit.append(
        {
            "cell_id": c["cell_id"],
            "entries_charged": ent,
            "pre_downsampling_step_count": ds.get("pre_downsampling_step_count"),
            "kept_step_count": ds.get("kept_step_count"),
            "kept_len_actual": len(st),
            "k": k,
            "cap_multiplier_m": ds.get("cap_enforcement_multiplier_m"),
            "kept_equals_pre_over_k": (
                ds.get("kept_step_count") == math.ceil(ds.get("pre_downsampling_step_count", 0) / k)
                if k
                else None
            ),
            "kept_len_matches_declared": len(st) == ds.get("kept_step_count"),
            "producer_median_over_FULL_steps": stats["median"],
            "validator_median_over_KEPT_steps": statistics.median(per_entry) if per_entry else None,
            "median_abs_diff": (
                abs(statistics.median(per_entry) - stats["median"]) if per_entry else None
            ),
            "median_rel_diff": (
                abs(statistics.median(per_entry) - stats["median"]) / stats["median"]
                if per_entry and stats["median"]
                else None
            ),
            "producer_mean_over_FULL_steps": stats["mean"],
            "validator_mean_over_KEPT_steps": (
                sum(per_entry) / len(per_entry) if per_entry else None
            ),
            "producer_n_steps": stats["n"],
            "producer_T_entry_s_total_over_entries": c["T_entry_s_total_over_entries"],
            "validator_total_over_entries": recomputed_total_over_entries,
            "total_over_entries_abs_diff": abs(
                recomputed_total_over_entries - c["T_entry_s_total_over_entries"]
            ),
            "kept_entries_share": entries_kept / ent if ent else None,
            "kept_wall_share_of_total": sum_kept / tot if tot else None,
            "component_split_sums_to_total_rel_err": (
                abs(sum(c["component_split_s"].values()) - tot) / tot if tot else None
            ),
            "table_size_L_total_matches_sum_per_curve": c["table_size_L_total"]
            == sum(c["table_size_L_per_curve"]),
            "admissible_producer": c["admissible"],
            "admissible_validator": ent >= 300,
            "cap_fired": c["cap_fired"],
            "terminal_status": c["terminal_status"],
        }
    )
OUT["raw_audit"] = raw_audit

# ---- series construction ------------------------------------------------
def cell_lookup(bset, variant, seeding, roles=("PRIMARY", "PRIMARY+DRIFT-START")):
    out = {}
    for c in cells:
        if (
            c["B_setting"] == bset
            and c["variant"] == variant
            and c["seeding"] == seeding
            and c["role"] in roles
        ):
            out[c["log2p_target"]] = c
    return out


SERIES = {}
for bset in ("B-ASY", "B-FIX-8", "B-FIX-32"):
    for variant in ("V-1", "V-2"):
        cl = cell_lookup(bset, variant, "SEED-A")
        if not cl:
            continue
        ks = sorted(cl)
        med = [cl[k]["T_entry_s_stats_over_steps"]["median"] for k in ks]
        phi_per_entry = [
            cl[k]["phi_generic_build_seconds_total_for_this_prime_set"]
            / cl[k]["entries_charged_to_timed_windows"]
            for k in ks
        ]
        SERIES[f"{bset}|{variant}|SEED-A|T_entry_ops_amortised"] = (
            ks,
            [m / tmul[k] for m, k in zip(med, ks)],
        )
        SERIES[f"{bset}|{variant}|SEED-A|T_entry_ops_fully_charged"] = (
            ks,
            [(m + ph) / tmul[k] for m, ph, k in zip(med, phi_per_entry, ks)],
        )
        SERIES[f"{bset}|{variant}|SEED-A|T_entry_s_median_PRIMARY"] = (ks, med)
        SERIES[f"{bset}|{variant}|SEED-A|T_entry_s_fully_charged"] = (
            ks,
            [m + ph for m, ph in zip(med, phi_per_entry)],
        )

# control series
SERIES["CTRL-CAL|t_mul"] = (sorted(tmul), [tmul[k] for k in sorted(tmul)])
SERIES["CTRL-CAL|t_inv"] = (sorted(tinv), [tinv[k] for k in sorted(tinv)])
SERIES["CTRL-CAL|t_noop"] = (sorted(tnoop), [tnoop[k] for k in sorted(tnoop)])
SERIES["CTRL-NULL|NULL-1"] = (sorted(null1), [null1[k] for k in sorted(null1)])
SERIES["CTRL-NULL|NULL-2"] = (sorted(null2), [null2[k] for k in sorted(null2)])

BOOT_SEED = 20260731001

results = {}
for sid, (ks, yl) in SERIES.items():
    ylog = [math.log2(v) for v in yl]
    xa = [math.sqrt(k) for k in ks]
    # k IS ALREADY log2 p, so the M-B regressor log2(log2 p) is log2(k).
    xb = [math.log2(k) for k in ks]
    fa = ols1(xa, ylog)
    fb = ols1(xb, ylog)
    f0 = ols0(ylog)
    # my collinearity: Pearson between the two regressors
    n = len(xa)
    mxa, mxb = sum(xa) / n, sum(xb) / n
    num = sum((p - mxa) * (q - mxb) for p, q in zip(xa, xb))
    den = math.sqrt(sum((p - mxa) ** 2 for p in xa) * sum((q - mxb) ** 2 for q in xb))
    entry = {
        "log2p_points": ks,
        "y_linear": yl,
        "y_log2": ylog,
        "collinearity_pearson": num / den,
        "M-A": {
            "a": fa["a"],
            "c": fa["slope"],
            "r2": fa["r2"],
            "adj_r2": fa["adj_r2"],
            "rse_bits": fa["rse_bits"],
            "slope_stderr": fa["slope_stderr"],
            "residuals_by_log2p": dict(zip(map(str, ks), fa["residuals"])),
            "sign_pattern": sign_pattern(fa["residuals"]),
            "longest_monotone_run": longest_monotone_run(fa["residuals"]),
            "max_abs_residual_bits": max(abs(r) for r in fa["residuals"]),
            "CI_T": ci_t(fa),
            "CI_BOOT": ci_boot(xa, ylog, BOOT_SEED),
        },
        "M-B": {
            "a": fb["a"],
            "gamma": fb["slope"],
            "r2": fb["r2"],
            "rse_bits": fb["rse_bits"],
            "slope_stderr": fb["slope_stderr"],
            "residuals_by_log2p": dict(zip(map(str, ks), fb["residuals"])),
            "sign_pattern": sign_pattern(fb["residuals"]),
            "max_abs_residual_bits": max(abs(r) for r in fb["residuals"]),
            "CI_T": ci_t(fb),
        },
        "M-0": {
            "a": f0["a"],
            "rse_bits_df_n_minus_1": f0["rse_df_n_minus_1"],
            "rse_bits_df_n_minus_2": f0["rse_df_n_minus_2"],
            "rse_bits_df_n": f0["rse_df_n"],
            "residuals_by_log2p": dict(zip(map(str, ks), f0["residuals"])),
            "sign_pattern": sign_pattern(f0["residuals"]),
            "max_abs_residual_bits": max(abs(r) for r in f0["residuals"]),
        },
    }
    # gates, my own evaluation
    wider = "CI-T" if (ci_t(fa)["hi"] - ci_t(fa)["lo"]) >= (
        (entry["M-A"]["CI_BOOT"]["hi"] or 0) - (entry["M-A"]["CI_BOOT"]["lo"] or 0)
    ) else "CI-BOOT"
    entry["carried_interval_validator"] = {
        "from": wider,
        "lo": entry["M-A"]["CI_T"]["lo"] if wider == "CI-T" else entry["M-A"]["CI_BOOT"]["lo"],
        "hi": entry["M-A"]["CI_T"]["hi"] if wider == "CI-T" else entry["M-A"]["CI_BOOT"]["hi"],
    }
    for lbl, r0 in (
        ("n_minus_1", f0["rse_df_n_minus_1"]),
        ("n_minus_2", f0["rse_df_n_minus_2"]),
        ("n", f0["rse_df_n"]),
    ):
        if r0:
            entry.setdefault("GOF-3_under_each_M0_normalisation", {})[lbl] = {
                "rse_M0": r0,
                "rse_MA": fa["rse_bits"],
                "reduction_factor": r0 / fa["rse_bits"],
                "fired": (r0 / fa["rse_bits"]) < 2.0,
            }
    entry["GOF-1_fired"] = max(abs(r) for r in fa["residuals"]) > 0.5
    entry["GOF-2_fired"] = longest_monotone_run(fa["residuals"]) >= 6
    results[sid] = entry

OUT["series"] = results


# -------------------------------------------- comparison with the producer
def get(d, *path, default=None):
    for p in path:
        if d is None:
            return default
        d = d.get(p) if isinstance(d, dict) else None
    return d if d is not None else default


diffs = []


def cmp(name, mine, theirs, tol=1e-9):
    if mine is None or theirs is None:
        diffs.append({"quantity": name, "validator": mine, "producer": theirs, "diff": None,
                      "status": "MISSING_ON_ONE_SIDE"})
        return
    if isinstance(mine, str) or isinstance(theirs, str):
        diffs.append({"quantity": name, "validator": mine, "producer": theirs,
                      "status": "AGREE" if mine == theirs else "DISAGREE"})
        return
    d = mine - theirs
    diffs.append(
        {
            "quantity": name,
            "validator": mine,
            "producer": theirs,
            "diff": d,
            "abs_diff": abs(d),
            "rel_diff": abs(d) / abs(theirs) if theirs else None,
            "status": "AGREE" if abs(d) <= tol * max(1.0, abs(theirs)) else "DISAGREE",
        }
    )


for sid, pf in prod["fits"].items():
    mine = results.get(sid)
    if mine is None:
        diffs.append({"quantity": f"{sid}:series", "status": "SERIES_NOT_RECONSTRUCTED"})
        continue
    cmp(f"{sid}:M-A.c", mine["M-A"]["c"], pf["M-A"]["c"])
    cmp(f"{sid}:M-A.a", mine["M-A"]["a"], pf["M-A"]["a"])
    cmp(f"{sid}:M-A.r2", mine["M-A"]["r2"], pf["M-A"]["r2"])
    cmp(f"{sid}:M-A.adj_r2", mine["M-A"]["adj_r2"], pf["M-A"]["adj_r2"])
    cmp(f"{sid}:M-A.rse", mine["M-A"]["rse_bits"], pf["M-A"]["rse_bits"])
    cmp(f"{sid}:M-A.stderr", mine["M-A"]["slope_stderr"], pf["M-A"]["slope_stderr"])
    cmp(f"{sid}:M-A.CI_T.lo", mine["M-A"]["CI_T"]["lo"], pf["M-A"]["CI_T"]["lo"])
    cmp(f"{sid}:M-A.CI_T.hi", mine["M-A"]["CI_T"]["hi"], pf["M-A"]["CI_T"]["hi"])
    cmp(f"{sid}:M-A.CI_BOOT.lo", mine["M-A"]["CI_BOOT"]["lo"], pf["M-A"]["CI_BOOT"]["lo"])
    cmp(f"{sid}:M-A.CI_BOOT.hi", mine["M-A"]["CI_BOOT"]["hi"], pf["M-A"]["CI_BOOT"]["hi"])
    cmp(f"{sid}:M-A.CI_BOOT.usable", float(mine["M-A"]["CI_BOOT"]["usable"]), float(pf["M-A"]["CI_BOOT"]["usable"]))
    cmp(f"{sid}:M-A.CI_BOOT.discarded", float(mine["M-A"]["CI_BOOT"]["discarded"]), float(pf["M-A"]["CI_BOOT"]["discarded"]))
    cmp(f"{sid}:carried_from", mine["carried_interval_validator"]["from"], pf["M-A"]["carried_interval"]["carried_from"])
    cmp(f"{sid}:carried.lo", mine["carried_interval_validator"]["lo"], pf["M-A"]["carried_interval"]["lo"])
    cmp(f"{sid}:carried.hi", mine["carried_interval_validator"]["hi"], pf["M-A"]["carried_interval"]["hi"])
    cmp(f"{sid}:M-A.sign_pattern", mine["M-A"]["sign_pattern"], pf["M-A"]["residual_sign_pattern"])
    cmp(f"{sid}:M-B.slope", mine["M-B"]["gamma"], pf["M-B"]["slope"])
    cmp(f"{sid}:M-B.rse", mine["M-B"]["rse_bits"], pf["M-B"]["rse_bits"])
    cmp(f"{sid}:M-0.a", mine["M-0"]["a"], pf["M-0"]["a"])
    cmp(f"{sid}:M-0.rse[n-1]", mine["M-0"]["rse_bits_df_n_minus_1"], pf["M-0"]["rse_bits"])
    # residual-by-residual
    for k, v in pf["M-A"]["residuals_signed_by_log2p"].items():
        cmp(f"{sid}:M-A.residual[{k}]", mine["M-A"]["residuals_by_log2p"].get(k), v)
    # y values
    for i, v in enumerate(pf["y_linear_values"]):
        cmp(f"{sid}:y_linear[{pf['log2p_points'][i]}]", mine["y_linear"][i], v, tol=1e-12)
    # gates
    cmp(f"{sid}:GOF-1.fired", str(mine["GOF-1_fired"]), str(pf["goodness_of_fit"]["GOF-1"]["fired"]))
    cmp(f"{sid}:GOF-2.fired", str(mine["GOF-2_fired"]), str(pf["goodness_of_fit"]["GOF-2"]["fired"]))
    g3 = mine["GOF-3_under_each_M0_normalisation"]["n_minus_1"]
    cmp(f"{sid}:GOF-3.reduction_factor", g3["reduction_factor"],
        pf["goodness_of_fit"]["GOF-3"]["reduction_factor"])
    cmp(f"{sid}:GOF-3.fired", str(g3["fired"]), str(pf["goodness_of_fit"]["GOF-3"]["fired"]))
    cmp(f"{sid}:collinearity", mine["collinearity_pearson"],
        pf["regressor_collinearity_pearson_sqrt_vs_loglog"])

# CTRL-CAL gate, my own evaluation
cal = results["CTRL-CAL|t_mul"]
prim = results[prod["primary_series_id"]]
cal_lo, cal_hi = cal["carried_interval_validator"]["lo"], cal["carried_interval_validator"]["hi"]
p_lo, p_hi = prim["carried_interval_validator"]["lo"], prim["carried_interval_validator"]["hi"]
overlap = not (cal_hi < p_lo or p_hi < cal_lo)
OUT["CTRL_CAL_GATE_validator"] = {
    "t_mul_c": cal["M-A"]["c"],
    "t_mul_interval": [cal_lo, cal_hi],
    "primary_interval": [p_lo, p_hi],
    "overlaps": overlap,
    "fired": overlap,
    "producer_fired": get(prod_ctrl, "CTRL-CAL", "CTRL-CAL-GATE", "fired"),
}

nullgate = {}
for lbl, sid in (("NULL-1", "CTRL-NULL|NULL-1"), ("NULL-2", "CTRL-NULL|NULL-2")):
    r = results[sid]
    lo, hi = r["carried_interval_validator"]["lo"], r["carried_interval_validator"]["hi"]
    excl0 = not (lo <= 0.0 <= hi)
    ov = not (hi < p_lo or p_hi < lo)
    nullgate[lbl] = {
        "slope": r["M-A"]["c"],
        "interval": [lo, hi],
        "excludes_zero": excl0,
        "overlaps_primary": ov,
        "fires": excl0 and ov,
    }
nullgate["fired"] = any(v["fires"] for v in nullgate.values() if isinstance(v, dict))
nullgate["producer_fired"] = get(prod_ctrl, "CTRL-NULL", "CTRL-NULL-GATE", "fired")
OUT["CTRL_NULL_GATE_validator"] = nullgate

# ST-B / ST-V, my own
def iv(sid):
    r = results[sid]
    return r["carried_interval_validator"]["lo"], r["carried_interval_validator"]["hi"]


def disj(a, b):
    return a[1] < b[0] or b[1] < a[0]


ib = {b: iv(f"{b}|V-1|SEED-A|T_entry_ops_amortised") for b in ("B-ASY", "B-FIX-8", "B-FIX-32")}
OUT["ST_B_validator"] = {
    "intervals": {k: list(v) for k, v in ib.items()},
    "pairwise_disjoint": {
        "B-ASY vs B-FIX-8": disj(ib["B-ASY"], ib["B-FIX-8"]),
        "B-ASY vs B-FIX-32": disj(ib["B-ASY"], ib["B-FIX-32"]),
        "B-FIX-8 vs B-FIX-32": disj(ib["B-FIX-8"], ib["B-FIX-32"]),
    },
}
OUT["ST_B_validator"]["all_pairwise_disjoint"] = all(
    OUT["ST_B_validator"]["pairwise_disjoint"].values()
)
v1 = iv("B-FIX-8|V-1|SEED-A|T_entry_ops_amortised")
v2 = iv("B-FIX-8|V-2|SEED-A|T_entry_ops_amortised")
OUT["ST_V_validator"] = {"V-1": list(v1), "V-2": list(v2), "disjoint": disj(v1, v2)}

# ST-SEED, my own: ratio of medians at the two SEED-B primes
seedrows = []
for k in (20, 40):
    a = [c for c in cells if c["log2p_target"] == k and c["seeding"] == "SEED-A"
         and c["B_setting"] == "B-FIX-8" and c["variant"] == "V-1"
         and c["role"] == "PRIMARY+DRIFT-START"]
    b = [c for c in cells if c["log2p_target"] == k and c["seeding"] == "SEED-B"]
    if a and b:
        ma = a[0]["T_entry_s_stats_over_steps"]["median"]
        mb = b[0]["T_entry_s_stats_over_steps"]["median"]
        seedrows.append(
            {
                "log2p": k,
                "SEED-A_median": ma,
                "SEED-B_median": mb,
                "ratio_A_over_B": ma / mb,
                "inside_band_0.90_1.10": 0.90 <= ma / mb <= 1.10,
                "SEED-A_entries": a[0]["entries_charged_to_timed_windows"],
                "SEED-B_entries": b[0]["entries_charged_to_timed_windows"],
            }
        )
OUT["ST_SEED_validator"] = {"rows": seedrows,
                            "SEED_GATE_fired": any(not r["inside_band_0.90_1.10"] for r in seedrows)}

# ST-NORM: ops interval vs seconds interval on the primary B setting
ops = iv("B-ASY|V-1|SEED-A|T_entry_ops_amortised")
sec = iv("B-ASY|V-1|SEED-A|T_entry_s_median_PRIMARY")
OUT["ST_NORM_validator"] = {"ops": list(ops), "seconds": list(sec), "disjoint": disj(ops, sec)}

# CTRL-DRIFT, my own from the raw start/end cells
drift = []
for k in (20, 40):
    s = [c for c in cells if c["log2p_target"] == k and c["role"] == "PRIMARY+DRIFT-START"]
    e = [c for c in cells if c["log2p_target"] == k and c["role"] == "DRIFT-END+CTRL-DET"]
    if s and e:
        ms = s[0]["T_entry_s_stats_over_steps"]["median"]
        me = e[0]["T_entry_s_stats_over_steps"]["median"]
        drift.append(
            {
                "log2p": k,
                "start_median": ms,
                "end_median": me,
                "ratio_end_over_start": me / ms,
                "inside_band_0.85_1.18": 0.85 <= me / ms <= 1.18,
                "start_jset_sha256": s[0]["jset_sha256"],
                "end_jset_sha256": e[0]["jset_sha256"],
                "jset_IDENTICAL_by_digest": s[0]["jset_sha256"] == e[0]["jset_sha256"],
                "entries_start": s[0]["entries_charged_to_timed_windows"],
                "entries_end": e[0]["entries_charged_to_timed_windows"],
                "entries_match": s[0]["entries_charged_to_timed_windows"]
                == e[0]["entries_charged_to_timed_windows"],
                "table_size_start": s[0]["table_size_L_total"],
                "table_size_end": e[0]["table_size_L_total"],
                "table_match": s[0]["table_size_L_total"] == e[0]["table_size_L_total"],
                "seeds_start": [c["seed"] for c in s[0]["curves"]],
                "seeds_end": [c["seed"] for c in e[0]["curves"]],
                "seeds_match": [c["seed"] for c in s[0]["curves"]]
                == [c["seed"] for c in e[0]["curves"]],
                "start_j_start": [c["start_j"] for c in s[0]["curves"]],
                "start_j_end": [c["start_j"] for c in e[0]["curves"]],
                "start_j_match": [c["start_j"] for c in s[0]["curves"]]
                == [c["start_j"] for c in e[0]["curves"]],
            }
        )
OUT["CTRL_DRIFT_and_DET_validator"] = drift

# seed integrity across all cells
seeds = {}
for c in cells:
    for cu in c["curves"]:
        seeds.setdefault(cu["seed"], []).append((c["cell_id"], cu["seed_label"]))
OUT["seed_integrity"] = {
    "total_curve_records": sum(len(c["curves"]) for c in cells),
    "distinct_seeds": len(seeds),
    "seeds_present_on_every_curve": all(
        cu.get("seed") is not None for c in cells for cu in c["curves"]
    ),
    "labels_all_distinct": len(
        {cu["seed_label"] for c in cells for cu in c["curves"]}
    )
    == sum(len(c["curves"]) for c in cells),
    "reused_seeds": {
        str(k): v for k, v in seeds.items() if len(v) > 1
    },
}

# cell/run counts
OUT["counts"] = {
    "cells_present": len(cells),
    "cells_not_reached": len(raw["cells_not_reached"]),
    "mandatory_cell_count_from_contract": 34,
    "cells_by_role": {},
    "admissible_cells": sum(1 for c in cells if c["entries_charged_to_timed_windows"] >= 300),
    "cells_below_300_entries": [
        c["cell_id"] for c in cells if c["entries_charged_to_timed_windows"] < 300
    ],
    "distinct_primes": sorted({c["log2p_target"] for c in cells}),
}
for c in cells:
    OUT["counts"]["cells_by_role"][c["role"]] = OUT["counts"]["cells_by_role"].get(c["role"], 0) + 1

OUT["diffs"] = diffs
OUT["diff_summary"] = {
    "compared": len(diffs),
    "agree": sum(1 for d in diffs if d.get("status") == "AGREE"),
    "disagree": sum(1 for d in diffs if d.get("status") == "DISAGREE"),
    "other": sum(1 for d in diffs if d.get("status") not in ("AGREE", "DISAGREE")),
    "max_abs_diff": max((d.get("abs_diff") or 0.0) for d in diffs),
}
OUT["disagreements"] = [d for d in diffs if d.get("status") != "AGREE"]

def sanitize(o):
    if isinstance(o, dict):
        return {str(k): sanitize(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [sanitize(v) for v in o]
    if hasattr(o, "item"):
        return o.item()
    return o


json.dump(sanitize(OUT), open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                           "independent_fit_output.json"), "w"), indent=1)

print("compared:", OUT["diff_summary"])
print("primary c (validator):", results[prod["primary_series_id"]]["M-A"]["c"])
print("primary CI-T:", {k: float(v) for k, v in results[prod["primary_series_id"]]["M-A"]["CI_T"].items()})
print("primary CI-BOOT:", results[prod["primary_series_id"]]["M-A"]["CI_BOOT"])
print("GOF-3 (primary):",
      results[prod["primary_series_id"]]["GOF-3_under_each_M0_normalisation"])
print("CTRL-CAL:", OUT["CTRL_CAL_GATE_validator"])
print("CTRL-NULL:", json.dumps(OUT["CTRL_NULL_GATE_validator"], default=str))
print("ST-B:", json.dumps(OUT["ST_B_validator"], default=str))
print("ST-V:", json.dumps(OUT["ST_V_validator"], default=str))
print("ST-NORM:", json.dumps(OUT["ST_NORM_validator"], default=str))
print("ST-SEED:", json.dumps(OUT["ST_SEED_validator"], default=str))
print("DRIFT/DET:", json.dumps(OUT["CTRL_DRIFT_and_DET_validator"], default=str)[:2000])
print("counts:", json.dumps(OUT["counts"], default=str))
print("seed_integrity:", json.dumps(OUT["seed_integrity"], default=str)[:1200])
print("N DISAGREEMENTS:", len(OUT["disagreements"]))
for d in OUT["disagreements"][:80]:
    print("  DISAGREE", json.dumps(d, default=str)[:300])
