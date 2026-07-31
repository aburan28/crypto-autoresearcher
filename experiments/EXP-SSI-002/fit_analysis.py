#!/usr/bin/env sage-python
# -*- coding: utf-8 -*-
"""
EXP-SSI-002 / RUN-SSI-002 -- fit_analysis.py

FITTING AND GATE-EVALUATION STAGE.

It recomputes EVERY fitted quantity FROM raw-timings.json ALONE, so that an
independent session can rerun it against the archived raw data without
re-executing any Sage computation.  It reads no other measurement input.

It evaluates the frozen contract's gates MECHANICALLY (GOF-1/2/3, ST-B, ST-V,
ST-SEED/SEED-GATE, ST-NORM, CTRL-CAL-GATE, CTRL-NULL-GATE, CTRL-DRIFT-GATE,
CTRL-COUNT-GATE, CTRL-DET) and records which pre-registered reading fired.
IT WRITES NO INTERPRETATION, NO DISPOSITION AND NO RECOMMENDATION.

Extrapolation is computed by SUBSTITUTION INTO THE COMMITTED, UNMODIFIED
experiments/EXP-P13VOW-001/cost_model.py.  That file is imported, never
edited, never re-derived; its main() is not executed.  Its sha256 is recorded.

p <= 2^40 IS NOT CRYPTOGRAPHIC SIZE.  Every margin figure emitted here is an
EXTRAPOLATION carrying EA-1..EA-6.
"""

import argparse
import hashlib
import importlib.util
import json
import math
import os
import random
import sys

BOOT_RESAMPLES = 2000
BOOT_SEED = 20260731001
GOF1_MAX_ABS_RESID_BITS = 0.5
GOF2_MONOTONE_RUN = 6
GOF3_RSE_FACTOR = 2.0
SEED_GATE_LO, SEED_GATE_HI = 0.90, 1.10
DRIFT_GATE_LO, DRIFT_GATE_HI = 0.85, 1.18
ADMISSIBLE_MIN_ENTRIES = 300
MIN_ADMISSIBLE_PRIMES = 6
IRREPRODUCIBILITY_BAND_BITS = 3.51      # DEC-20260724-016
CSTAR_TOL = 1e-9
SECURITY_LEVELS = [256, 384, 512, 576, 768]
MARGIN_MEMORY_BUDGET_LOG2W = 30

EA = {
    "EA-1": "The fitted per-entry cost shape holds unchanged from log2 p in [20, 40] out to log2 p = 256 and beyond. UNTESTED; a 6.4-fold extrapolation in log2 p from at most 8 points.",
    "EA-2": "The per-entry table-construction cost is the ONLY hidden overhead entering the model. FALSE AS STATED AND FLAGGED AS SUCH: the o(1) in P0, the tightness of the Psi estimate, Algorithm 2's final matching loop, Algorithm 3's random walks and memory access across ~2^92 entries are NOT measured here and are NOT zero. The extrapolated margin is OPTIMISTIC-FOR-THE-ATTACKER on overhead.",
    "EA-3": "THE MEASURED B REGIME DOES NOT REACH THE OPERATING REGIME. This sweep measures B <= 32 with ell <= 31; the B the committed model selects at log2 p = 256 is far larger and Lemma 3.3's cost carries a B^{O(1)} factor. THE FITTED c IS MEASURED WHERE B IS TINY AND MAY NOT TRANSFER. SINGLE LARGEST LIMITATION.",
    "EA-4": "One host, one Sage build, interpreted Python, no batching of modular polynomial evaluations. The measured per-entry cost is an UPPER BOUND on an optimised implementation's cost, which is why a large c does not establish safety.",
    "EA-5": "The committed model's reproduction of the frozen source's five concrete pairs deviates by 0.05 to 3.51 bits (partial control failure, RUN-P13VOW-001). EVERY MARGIN HERE INHERITS THAT BAND ADDITIVELY.",
    "EA-6": "Heuristic 1 is assumed throughout exactly as H-P13-001 states, and is NOT tested, validated or weakened by anything in this experiment.",
}


# --------------------------------------------------------------- statistics
def mean(xs):
    return sum(xs) / len(xs)


def ols(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None
    b = sxy / sxx
    a = my - b * mx
    fit = [a + b * x for x in xs]
    resid = [y - f for y, f in zip(ys, fit)]
    sse = sum(r * r for r in resid)
    sst = sum((y - my) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst > 0 else None
    adj = 1.0 - (1.0 - r2) * (n - 1) / (n - 2) if (r2 is not None and n > 2) else None
    rse = math.sqrt(sse / (n - 2)) if n > 2 else None
    se_b = math.sqrt(sse / (n - 2) / sxx) if (n > 2 and sxx > 0) else None
    return {"a": a, "slope": b, "fitted": fit, "residuals": resid,
            "sse": sse, "r2": r2, "adj_r2": adj, "rse_bits": rse,
            "slope_stderr": se_b, "n": n}


def ols_const(ys):
    n = len(ys)
    my = mean(ys)
    resid = [y - my for y in ys]
    sse = sum(r * r for r in resid)
    rse = math.sqrt(sse / (n - 1)) if n > 1 else None
    return {"a": my, "slope": 0.0, "fitted": [my] * n, "residuals": resid,
            "sse": sse, "r2": 0.0, "adj_r2": None, "rse_bits": rse,
            "slope_stderr": None, "n": n}


def _betacf(a, b, x):
    MAXIT, EPS, FPMIN = 300, 3e-16, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    lbeta = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
             + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return math.exp(lbeta) * _betacf(a, b, x) / a
    return 1.0 - math.exp(lbeta) * _betacf(b, a, 1.0 - x) / b


def t_cdf(t, df):
    x = df / (df + t * t)
    p = 0.5 * betai(0.5 * df, 0.5, x)
    return 1.0 - p if t > 0 else p


def t_quantile(q, df):
    lo, hi = -200.0, 200.0
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if t_cdf(mid, df) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def ci_t(fit, level=0.95):
    if fit is None or fit["slope_stderr"] is None or fit["n"] <= 2:
        return None
    df = fit["n"] - 2
    tq = t_quantile(0.5 + level / 2.0, df)
    h = tq * fit["slope_stderr"]
    return {"method": "CI-T", "lo": fit["slope"] - h, "hi": fit["slope"] + h,
            "width": 2 * h, "df": df, "t_quantile": tq, "level": level}


def ci_boot(xs, ys, seed=BOOT_SEED, n=BOOT_RESAMPLES):
    rng = random.Random(seed)
    N = len(xs)
    slopes = []
    discarded = 0
    for _ in range(n):
        idx = [rng.randrange(N) for _ in range(N)]
        if len(set(xs[i] for i in idx)) < 3:
            discarded += 1
            continue
        f = ols([xs[i] for i in idx], [ys[i] for i in idx])
        if f is None:
            discarded += 1
            continue
        slopes.append(f["slope"])
    if len(slopes) < 20:
        return {"method": "CI-BOOT", "lo": None, "hi": None, "width": None,
                "resamples": n, "usable": len(slopes), "discarded": discarded,
                "seed": seed, "note": "too few usable resamples"}
    slopes.sort()
    def pct(q):
        pos = q * (len(slopes) - 1)
        lo = int(math.floor(pos))
        hi = min(lo + 1, len(slopes) - 1)
        return slopes[lo] + (pos - lo) * (slopes[hi] - slopes[lo])
    lo, hi = pct(0.025), pct(0.975)
    return {"method": "CI-BOOT", "lo": lo, "hi": hi, "width": hi - lo,
            "resamples": n, "usable": len(slopes), "discarded": discarded,
            "seed": seed}


def carry_wider(a, b):
    cand = [c for c in (a, b) if c and c.get("width") is not None]
    if not cand:
        return None
    w = max(cand, key=lambda c: c["width"])
    return {"carried_from": w["method"], "lo": w["lo"], "hi": w["hi"],
            "width": w["width"],
            "rule": "the WIDER of CI-T and CI-BOOT is carried into every "
                    "downstream statement (fitting_protocol.intervals_reporting_rule)"}


def pearson(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def sign_pattern(res):
    return "".join("+" if r > 0 else ("-" if r < 0 else "0") for r in res)


def longest_monotone_run(pat):
    best = cur = 0
    prev = None
    for ch in pat:
        if ch == prev:
            cur += 1
        else:
            cur = 1
            prev = ch
        best = max(best, cur)
    return best


def disjoint(i1, i2):
    if not i1 or not i2 or i1.get("lo") is None or i2.get("lo") is None:
        return None
    return i1["hi"] < i2["lo"] or i2["hi"] < i1["lo"]


def overlaps(i1, i2):
    d = disjoint(i1, i2)
    return None if d is None else (not d)


# --------------------------------------------------------------- fit driver
def fit_block(points, series_id, y_label):
    """points: list of (log2p, y_linear). Fits M-A, M-B, M-0 on log2(y)."""
    pts = [(lp, y) for lp, y in points if y is not None and y > 0]
    pts.sort()
    if len(pts) < 3:
        return {"series_id": series_id, "y": y_label, "n_points": len(pts),
                "fit_reported": False,
                "reason": "fewer than 3 admissible points; no fit is reported"}
    lps = [p[0] for p in pts]
    ys = [math.log2(p[1]) for p in pts]
    xa = [math.sqrt(lp) for lp in lps]
    # M-B regressor: log2(log2 p); lp IS log2 p, so this is log2(lp).
    xb = [math.log2(lp) for lp in lps]

    fa = ols(xa, ys)
    fb = ols(xb, ys)
    f0 = ols_const(ys)

    out = {"series_id": series_id, "y": y_label, "n_points": len(pts),
           "log2p_points": lps,
           "y_linear_values": [p[1] for p in pts],
           "y_log2_values": ys,
           "regressor_collinearity_pearson_sqrt_vs_loglog": pearson(xa, xb),
           "collinearity_note":
               "PRE-REGISTERED EXPECTED LIMITATION: over log2 p in [20,40], "
               "sqrt(log2 p) and log2(log2 p) are nearly collinear, so the data "
               "are unlikely to discriminate M-A from M-B. A FITTED c IS A SLOPE "
               "IN A CHOSEN PARAMETERISATION AND IS NOT EVIDENCE THAT THE TRUE "
               "FUNCTIONAL FORM IS sqrt(log2 p).",
           "fit_reported": True}

    for mid, f, slope_name, form in (
            ("M-A", fa, "c", "log2(T) = a + c * sqrt(log2 p)"),
            ("M-B", fb, "gamma", "log2(T) = a + gamma * log2(log2 p)"),
            ("M-0", f0, None, "log2(T) = a")):
        blk = {"model": mid, "form": form, "a": f["a"],
               "r2": f["r2"], "adj_r2": f["adj_r2"], "rse_bits": f["rse_bits"],
               "residuals_signed_by_log2p":
                   {str(lp): r for lp, r in zip(lps, f["residuals"])},
               "residual_sign_pattern": sign_pattern(f["residuals"]),
               "max_abs_residual_bits": max(abs(r) for r in f["residuals"])}
        if slope_name:
            xs = xa if mid == "M-A" else xb
            cit = ci_t(f)
            cib = ci_boot(xs, ys)
            blk[slope_name] = f["slope"]
            blk["slope"] = f["slope"]
            blk["slope_stderr"] = f["slope_stderr"]
            blk["CI_T"] = cit
            blk["CI_BOOT"] = cib
            blk["carried_interval"] = carry_wider(cit, cib)
        out[mid] = blk

    # ---- goodness-of-fit gates, applied to the reported model M-A
    ma = out["M-A"]
    gof1 = ma["max_abs_residual_bits"] > GOF1_MAX_ABS_RESID_BITS
    run = longest_monotone_run(ma["residual_sign_pattern"])
    gof2 = run >= GOF2_MONOTONE_RUN
    rse0 = out["M-0"]["rse_bits"]
    rsea = ma["rse_bits"]
    ratio = (rse0 / rsea) if (rse0 and rsea and rsea > 0) else None
    gof3 = (ratio is None) or (ratio < GOF3_RSE_FACTOR)
    out["goodness_of_fit"] = {
        "GOF-1": {"rule": "max |residual| > 0.5 bit => FIT NOT ADEQUATE",
                  "max_abs_residual_bits": ma["max_abs_residual_bits"],
                  "fired": bool(gof1),
                  "verdict": "NOT ADEQUATE" if gof1 else "adequate"},
        "GOF-2": {"rule": "monotone residual-sign run >= 6 of 8 => FIT NOT ADEQUATE",
                  "sign_pattern": ma["residual_sign_pattern"],
                  "longest_monotone_run": run, "n_points": len(pts),
                  "fired": bool(gof2),
                  "verdict": "NOT ADEQUATE" if gof2 else "adequate"},
        "GOF-3": {"rule": "M-A must reduce residual standard error vs the null M-0 "
                          "by at least a factor 2",
                  "rse_M0_bits": rse0, "rse_MA_bits": rsea,
                  "reduction_factor": ratio,
                  "fired": bool(gof3),
                  "verdict": ("NO p-DEPENDENCE DETECTED IN THIS REGIME" if gof3
                              else "p-dependence detected against the null")},
        "any_fired": bool(gof1 or gof2 or gof3),
        "exponent_identified": (not (gof1 or gof2 or gof3)),
    }
    return out


# --------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--cost-model", required=True)
    args = ap.parse_args()

    raw = json.load(open(os.path.join(args.run_dir, "raw-timings.json")))
    cells = raw["cells"]
    cal = {c["log2p_target"]: c for c in raw["ctrl_cal"]}
    nulls = {c["log2p_target"]: c for c in raw["ctrl_null"]}

    # ---------------------------------------------------------- cost model
    cm_sha = hashlib.sha256(open(args.cost_model, "rb").read()).hexdigest()
    spec = importlib.util.spec_from_file_location("committed_cost_model", args.cost_model)
    cm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cm)          # module import only; main() NOT executed
    ug, log2rho = cm.dickman_log2_grid()

    def psi_committed(X, B):
        """Psi(X,B) via the COMMITTED Dickman machinery: the committed model
        writes log2 M = 2 log2 X + log2 rho(w) for M = Psi(X,B) * X with
        w = log X / log B (cost_model.py cost_for_B), i.e. Psi = X * rho(w)."""
        if X <= 1 or B <= 1:
            return None
        w = math.log(X) / math.log(B)
        if w < 1.0:
            w = 1.0
        return X * (2.0 ** cm.log2_rho(ug, log2rho, w))

    # ------------------------------------------------------ per-cell summary
    summary_cells = []
    for c in cells:
        k = c["log2p_target"]
        tmul = cal[k]["t_mul_s"] if k in cal else None
        n = c["entries_charged_to_timed_windows"]
        med = c["T_entry_s_stats_over_steps"]["median"]
        mn = c["T_entry_s_stats_over_steps"]["mean"]
        phi_charge = (c["phi_generic_build_seconds_total_for_this_prime_set"] / n) if n else None
        rec = dict(c)
        rec.pop("steps_downsampled", None)
        rec["t_mul_s_from_CTRL_CAL"] = tmul
        rec["T_entry_s_median_PRIMARY"] = med
        rec["T_entry_s_mean"] = mn
        rec["mean_over_median_ratio"] = (mn / med) if (med and mn) else None
        rec["T_entry_s_fully_charged"] = (med + phi_charge) if (med is not None and phi_charge is not None) else None
        rec["phi_retrieval_charge_per_entry_s"] = phi_charge
        rec["T_entry_ops_amortised"] = (med / tmul) if (med and tmul) else None
        rec["T_entry_ops_fully_charged"] = ((med + phi_charge) / tmul) if (med and tmul and phi_charge is not None) else None
        # CTRL-COUNT bounds
        X, B = c["X"], c["B_realised"]
        psi = psi_committed(X, B)
        psi_exact = None
        try:
            lim = int(math.floor(X))
            cnt = 0
            for d in range(1, lim + 1):
                m = d
                for l in c["prime_set_ell"]:
                    while m % l == 0:
                        m //= l
                if m == 1:
                    cnt += 1
            psi_exact = cnt
        except Exception:
            pass
        # cast out of numpy scalars: a numpy bool is not JSON-serialisable and
        # would be written as the STRING "False", which is truthy.
        psi = float(psi) if psi is not None else None
        lower = float(psi * X) if psi else None
        upper = float(psi * X * (math.log(X) + 2.0)) if psi else None
        largest_table = max(c["table_size_L_per_curve"]) if c["table_size_L_per_curve"] else 0
        rec["ctrl_count"] = {
            "X": X, "B": B,
            "Psi_committed_dickman": psi,
            "Psi_exact_note": "Psi_committed_dickman is the COMMITTED model's Dickman "
                              "estimate X*rho(log X/log B); the exact enumerated count is "
                              "reported beside it as a diagnostic. At these very small X "
                              "the two differ substantially and BOTH ARE REPORTED.",
            "Psi_exact_enumerated_diagnostic": psi_exact,
            "lemma_3_2_upper_bound_Psi_X_logX_plus_2": upper,
            "section_4_1_lower_bound_Psi_X": lower,
            "largest_single_table_L": largest_table,
            "table_completed_for_that_curve":
                not any(cc["truncated_by_entry_ceiling"] or cc["cap_fired"]
                        for cc in c["curves"]),
            "upper_bound_violated": bool(largest_table > upper) if upper else None,
            "below_section_4_1_lower_bound": bool(largest_table < lower) if lower else None,
            "spot_checks": c["ctrl_count_spot"],
            "note": "The Lemma 3.2 UPPER bound comparison remains valid under a "
                    "truncated table (truncated <= full <= bound). The Section 4.1 "
                    "LOWER bound comparison is only meaningful where "
                    "table_completed_for_that_curve is true. A realised size below "
                    "the Section 4.1 lower bound is recorded as an OBSERVATION about "
                    "that bound at this scale and is EXPLICITLY NOT a claim that "
                    "Section 4.1 is wrong; that defect is carried, not re-litigated.",
        }
        summary_cells.append(rec)

    by_id = {c["cell_id"]: c for c in summary_cells}

    def series(bid, variant, seeding, roles=("PRIMARY", "PRIMARY+DRIFT-START")):
        out = []
        for c in summary_cells:
            if c["B_setting"] == bid and c["variant"] == variant \
                    and c["seeding"] == seeding and c["role"] in roles:
                out.append(c)
        out.sort(key=lambda c: c["log2p_target"])
        return out

    def make_points(cs, key):
        pts, excl = [], []
        for c in cs:
            if not c["admissible"]:
                excl.append({"cell_id": c["cell_id"],
                             "entries": c["entries_charged_to_timed_windows"],
                             "reason": "UNDER-SAMPLED: fewer than %d timed entries; "
                                       "EXCLUDED FROM EVERY FIT" % ADMISSIBLE_MIN_ENTRIES})
                continue
            if c["ctrl_count"]["upper_bound_violated"] or \
                    c["ctrl_count"]["spot_checks"]["phi_zero_fail"] or \
                    c["ctrl_count"]["spot_checks"]["filter_fail"]:
                excl.append({"cell_id": c["cell_id"],
                             "entries": c["entries_charged_to_timed_windows"],
                             "reason": "CTRL-COUNT-GATE fired: cell invalid, excluded from every fit"})
                continue
            v = c.get(key)
            if v is None:
                excl.append({"cell_id": c["cell_id"],
                             "entries": c["entries_charged_to_timed_windows"],
                             "reason": "metric %s missing" % key})
                continue
            pts.append((c["log2p_target"], v))
        return pts, excl

    fits = {}
    exclusions = {}
    YKEYS = [("T_entry_ops_amortised", "T_entry_ops (host-normalised, Phi amortised) -- PRIMARY"),
             ("T_entry_ops_fully_charged", "T_entry_ops (host-normalised, Phi retrieval FULLY CHARGED)"),
             ("T_entry_s_median_PRIMARY", "T_entry_s (raw seconds, median, Phi amortised) -- SECONDARY (ST-NORM)"),
             ("T_entry_s_fully_charged", "T_entry_s (raw seconds, Phi retrieval FULLY CHARGED)")]

    SERIES_DEFS = [("B-ASY", "V-1", "SEED-A"), ("B-FIX-8", "V-1", "SEED-A"),
                   ("B-FIX-32", "V-1", "SEED-A"), ("B-FIX-8", "V-2", "SEED-A")]
    for bid, var, sd in SERIES_DEFS:
        cs = series(bid, var, sd)
        for key, lab in YKEYS:
            pts, excl = make_points(cs, key)
            sid = "%s|%s|%s|%s" % (bid, var, sd, key)
            fits[sid] = fit_block(pts, sid, lab)
            fits[sid]["n_admissible_primes"] = len(pts)
            fits[sid]["fit_not_reported_as_exponent_reason"] = (
                None if len(pts) >= MIN_ADMISSIBLE_PRIMES else
                "A FIT RUN ON FEWER THAN %d ADMISSIBLE PRIMES IS NOT REPORTED AS A "
                "FITTED EXPONENT AT ALL (cells.cell_admissibility)." % MIN_ADMISSIBLE_PRIMES)
            exclusions[sid] = excl

    # ------------------------------------------------------------- FIT-ELL
    fit_ell = {}
    for l in ("2", "3"):
        cs = series("B-FIX-8", "V-1", "SEED-A")
        pts, excl = [], []
        for c in cs:
            m = c["mix1_per_ell"].get(l)
            if not m or not m["median_per_entry_s"] or m["entries"] < ADMISSIBLE_MIN_ENTRIES:
                excl.append({"cell_id": c["cell_id"],
                             "ell": l,
                             "entries_for_this_ell": (m or {}).get("entries", 0),
                             "reason": "fewer than %d entries at this ell in this cell"
                                       % ADMISSIBLE_MIN_ENTRIES})
                continue
            tmul = c["t_mul_s_from_CTRL_CAL"]
            pts.append((c["log2p_target"], m["median_per_entry_s"] / tmul))
        sid = "FIT-ELL|ell=%s|B-FIX-8|V-1|SEED-A|T_entry_ops" % l
        fit_ell[sid] = fit_block(pts, sid, "T_entry_ops restricted to ell = %s" % l)
        fit_ell[sid]["n_admissible_primes"] = len(pts)
        fit_ell[sid]["exclusions"] = excl
        fit_ell[sid]["fit_not_reported_as_exponent_reason"] = (
            None if len(pts) >= MIN_ADMISSIBLE_PRIMES else
            "A FIT RUN ON FEWER THAN %d ADMISSIBLE PRIMES IS NOT REPORTED AS A FITTED "
            "EXPONENT AT ALL (cells.cell_admissibility). Only %d primes had at least %d "
            "entries at this ell." % (MIN_ADMISSIBLE_PRIMES, len(pts), ADMISSIBLE_MIN_ENTRIES))
        fit_ell[sid]["why_mandatory"] = (
            "A pooled fit mixes a genuine p-dependence with a changing ell-mixture; "
            "holding ell fixed isolates the pure p-dependence. IF THE POOLED c AND "
            "THE FIXED-ell c DISAGREE BEYOND THEIR INTERVALS, THE POOLED c IS AN "
            "ARTIFACT OF THE MIXTURE.")

    # ---------------------------------------------------- primary series pick
    PRIMARY_SID = "B-ASY|V-1|SEED-A|T_entry_ops_amortised"
    primary = fits[PRIMARY_SID]
    primary_ci = primary.get("M-A", {}).get("carried_interval") if primary.get("fit_reported") else None

    # compare pooled vs fixed-ell
    fitell_vs_pooled = {}
    pooled8 = fits["B-FIX-8|V-1|SEED-A|T_entry_ops_amortised"]
    for sid, blk in fit_ell.items():
        if (blk.get("fit_reported") and pooled8.get("fit_reported")
                and blk.get("fit_not_reported_as_exponent_reason") is None):
            i1 = pooled8["M-A"]["carried_interval"]
            i2 = blk["M-A"]["carried_interval"]
            d = disjoint(i1, i2)
            fitell_vs_pooled[sid] = {
                "pooled_interval_B-FIX-8": i1, "fixed_ell_interval": i2,
                "disjoint_beyond_intervals": d,
                "verdict": ("POOLED c AND FIXED-ell c DISAGREE BEYOND THEIR INTERVALS: "
                            "THE POOLED c IS AN ARTIFACT OF THE ell-MIXTURE" if d
                            else "pooled and fixed-ell intervals overlap")}
        else:
            fitell_vs_pooled[sid] = {
                "verdict": "NOT COMPARABLE: no fitted exponent is reported for this "
                           "series (" + str(blk.get("fit_not_reported_as_exponent_reason")
                                            or "no fit reported") + ")"}

    # ------------------------------------------------------------ stability
    def ci_of(sid):
        b = fits.get(sid)
        if not b or not b.get("fit_reported"):
            return None
        return b["M-A"]["carried_interval"]

    stb = {b: ci_of("%s|V-1|SEED-A|T_entry_ops_amortised" % b)
           for b in ("B-ASY", "B-FIX-8", "B-FIX-32")}
    pairs = [("B-ASY", "B-FIX-8"), ("B-ASY", "B-FIX-32"), ("B-FIX-8", "B-FIX-32")]
    pw = {"%s vs %s" % pr: disjoint(stb[pr[0]], stb[pr[1]]) for pr in pairs}
    all_disjoint = all(v is True for v in pw.values())
    ST_B = {"rule": "fit c separately at B-ASY, B-FIX-8 and B-FIX-32 (V-1, SEED-A)",
            "intervals": stb, "pairwise_disjoint": pw,
            "all_three_pairwise_disjoint": all_disjoint,
            "verdict": ("c IS B-DEPENDENT AND IS NOT AN EXPONENT IN THIS REGIME - IT IS "
                        "AN ARTIFACT OF THE B SETTING" if all_disjoint
                        else "the three intervals are not pairwise disjoint")}

    v1 = ci_of("B-FIX-8|V-1|SEED-A|T_entry_ops_amortised")
    v2 = ci_of("B-FIX-8|V-2|SEED-A|T_entry_ops_amortised")
    dv = disjoint(v1, v2)
    ST_V = {"rule": "fit c separately for V-1 and V-2 at B-FIX-8, SEED-A",
            "V-1_interval": v1, "V-2_interval": v2, "disjoint": dv,
            "verdict": ("THE FITTED c IS A PROPERTY OF THE IMPLEMENTATION AND NOT OF "
                        "THE ALGORITHM; NO SINGLE c MAY BE REPORTED AS THE ALGORITHM'S "
                        "OVERHEAD EXPONENT" if dv else
                        "the V-1 and V-2 intervals are not disjoint")}

    seed_rows = []
    for c in summary_cells:
        if c["seeding"] == "SEED-B":
            k = c["log2p_target"]
            a = None
            for cc in summary_cells:
                if cc["log2p_target"] == k and cc["B_setting"] == "B-FIX-8" \
                        and cc["variant"] == "V-1" and cc["seeding"] == "SEED-A" \
                        and cc["role"] == "PRIMARY+DRIFT-START":
                    a = cc
            if a:
                ra = a["T_entry_s_median_PRIMARY"]
                rb = c["T_entry_s_median_PRIMARY"]
                ratio = ra / rb if rb else None
                seed_rows.append({
                    "log2p": k,
                    "SEED-A_cell": a["cell_id"], "SEED-B_cell": c["cell_id"],
                    "SEED-A_entries": a["entries_charged_to_timed_windows"],
                    "SEED-B_entries": c["entries_charged_to_timed_windows"],
                    "SEED-A_T_entry_s_median": ra, "SEED-B_T_entry_s_median": rb,
                    "SEED-A_seed_seconds": a["seed_seconds"],
                    "SEED-B_seed_seconds": c["seed_seconds"],
                    "seed_seconds_inside_timed_window": False,
                    "ratio_A_over_B": ratio,
                    "inside_SEED_GATE_band": (SEED_GATE_LO <= ratio <= SEED_GATE_HI)
                                             if ratio else None,
                    "SEED-A_intercept_a_MA": None})
    seed_gate_fired = any(r["inside_SEED_GATE_band"] is False for r in seed_rows)
    ST_SEED = {
        "rows": seed_rows,
        "SEED_GATE": {"band": [SEED_GATE_LO, SEED_GATE_HI],
                      "fired": bool(seed_gate_fired),
                      "verdict": ("THE REPORTED CONSTANT IS SEEDING-SENSITIVE: every "
                                  "artifact quoting the per-entry cost must quote the "
                                  "strategy with it" if seed_gate_fired
                                  else "the SEED-A/SEED-B ratio lies inside [0.90, 1.10] "
                                       "at every tested prime")},
        "NO_SEED_B_SLOPE_IS_FITTED":
            "Only two primes run under SEED-B. TWO POINTS CANNOT SUPPORT A SLOPE WITH "
            "AN INTERVAL, SO NO SEED-B SLOPE IS REPORTED AS A FITTED EXPONENT.",
        "effect_on_the_fitted_intercept":
            {"note": "the SEED-A intercept a of M-A per series is reported in "
                     "fits[...]['M-A']['a']; no SEED-B intercept is fitted because "
                     "two points do not support a fit with an interval"},
        "gap_1_statement":
            "Supplying a seeding strategy is an implementation decision of EXP-SSI-002. "
            "IT IS NOT A REPAIR OF THE FROZEN TEXT AND GAP-1 REMAINS AN OPEN RECORDED "
            "DEFECT OF SRC-P13-WESOLOWSKI-2026.",
    }

    ST_NORM = {}
    for bid, var, sd in SERIES_DEFS:
        a = ci_of("%s|%s|%s|T_entry_ops_amortised" % (bid, var, sd))
        b = ci_of("%s|%s|%s|T_entry_s_median_PRIMARY" % (bid, var, sd))
        d = disjoint(a, b)
        ST_NORM["%s|%s|%s" % (bid, var, sd)] = {
            "normalised_ops_interval": a, "raw_seconds_interval": b,
            "disjoint": d,
            "verdict": ("DISAGREEMENT BEYOND THE INTERVALS: reported as a finding about "
                        "the normalisation, not resolved by preference" if d
                        else "normalised and raw-seconds intervals overlap")}

    # amortised vs fully charged
    amort_vs_full = {}
    for bid, var, sd in SERIES_DEFS:
        a = ci_of("%s|%s|%s|T_entry_ops_amortised" % (bid, var, sd))
        b = ci_of("%s|%s|%s|T_entry_ops_fully_charged" % (bid, var, sd))
        d = disjoint(a, b)
        amort_vs_full["%s|%s|%s" % (bid, var, sd)] = {
            "amortised_interval": a, "fully_charged_interval": b, "disjoint": d,
            "verdict": ("THE MEASUREMENT IS DOMINATED BY PRECOMPUTATION LOADING AT THIS "
                        "SCALE AND THE PER-ENTRY ARITHMETIC COST IS NOT WHAT IS BEING "
                        "FITTED" if d else
                        "amortised and fully charged fits agree within the intervals")}

    # -------------------------------------------------------------- controls
    ks = sorted(cal.keys())
    cal_fits = {}
    for name, key in (("t_mul", "t_mul_s"), ("t_inv", "t_inv_s"), ("t_noop", "t_noop_s")):
        pts = [(k, cal[k][key]) for k in ks if cal[k][key]]
        cal_fits[name] = fit_block(pts, "CTRL-CAL|%s" % name, name)
    cal_ci = cal_fits["t_mul"]["M-A"]["carried_interval"] if cal_fits["t_mul"].get("fit_reported") else None
    cal_overlap = overlaps(cal_ci, primary_ci)
    CTRL_CAL = {
        "per_prime": [cal[k] for k in ks],
        "fits": cal_fits,
        "CTRL-CAL-GATE": {
            "rule": "fit M-A to t_mul(p); if its interval overlaps the primary fit's "
                    "interval, the primary fit is NOT separated from host and "
                    "interpreter effects",
            "t_mul_interval": cal_ci, "primary_interval": primary_ci,
            "overlaps": cal_overlap,
            "fired": bool(cal_overlap) if cal_overlap is not None else None,
            "verdict": ("THE PRIMARY FIT IS NOT SEPARATED FROM HOST AND INTERPRETER "
                        "EFFECTS" if cal_overlap else
                        "the t_mul interval does not overlap the primary interval"
                        if cal_overlap is not None else "not evaluable")},
    }

    null_fits = {}
    for name, key in (("NULL-1_sha256_fixed_4KiB", "null1_sha256_4kib_s"),
                      ("NULL-2_dict_1000_fixed_keys", "null2_dict_1000_insert_lookup_s")):
        pts = [(k, nulls[k][key]) for k in sorted(nulls) if nulls[k][key]]
        null_fits[name] = fit_block(pts, "CTRL-NULL|%s" % name, name)
    null_gate = {}
    fired_any = False
    for name, blk in null_fits.items():
        if not blk.get("fit_reported"):
            null_gate[name] = {"evaluable": False}
            continue
        ci = blk["M-A"]["carried_interval"]
        excl0 = (ci["lo"] > 0 or ci["hi"] < 0) if ci else None
        ov = overlaps(ci, primary_ci)
        f = bool(excl0 and ov)
        fired_any = fired_any or f
        null_gate[name] = {"interval": ci, "excludes_zero": excl0,
                           "overlaps_primary": ov, "fired": f}
    CTRL_NULL = {
        "per_prime": [nulls[k] for k in sorted(nulls)],
        "fits": null_fits,
        "CTRL-NULL-GATE": {
            "rule": "if either slope interval EXCLUDES ZERO and ALSO OVERLAPS the "
                    "primary fit's interval, the measurement is contaminated, the "
                    "primary fit is NOT-INTERPRETABLE and no c is carried into the "
                    "extrapolation",
            "per_null": null_gate, "fired": bool(fired_any),
            "verdict": ("MEASUREMENT CONTAMINATED; PRIMARY FIT NOT-INTERPRETABLE"
                        if fired_any else "no contamination detected by this gate")},
    }

    drift_rows = []
    for c in summary_cells:
        if c["role"] == "DRIFT-END+CTRL-DET":
            k = c["log2p_target"]
            s = None
            for cc in summary_cells:
                if cc["log2p_target"] == k and cc["role"] == "PRIMARY+DRIFT-START":
                    s = cc
            if s:
                r = (c["T_entry_s_median_PRIMARY"] / s["T_entry_s_median_PRIMARY"]) \
                    if s["T_entry_s_median_PRIMARY"] else None
                drift_rows.append({
                    "log2p": k, "start_cell": s["cell_id"], "end_cell": c["cell_id"],
                    "start_T_entry_s_median": s["T_entry_s_median_PRIMARY"],
                    "end_T_entry_s_median": c["T_entry_s_median_PRIMARY"],
                    "end_over_start_ratio": r,
                    "inside_band": (DRIFT_GATE_LO <= r <= DRIFT_GATE_HI) if r else None,
                    "start_wall_s": s["wall_seconds"], "end_wall_s": c["wall_seconds"],
                    "start_cpu_s": s["cpu_seconds"], "end_cpu_s": c["cpu_seconds"]})
    drift_fired = any(r["inside_band"] is False for r in drift_rows)
    widening = 0.0
    if drift_fired:
        for r in drift_rows:
            if r["end_over_start_ratio"]:
                widening = max(widening, abs(math.log2(r["end_over_start_ratio"])))
    CTRL_DRIFT = {
        "rows": drift_rows,
        "cell_execution_order": [c["cell_id"] for c in summary_cells],
        "ordering_note": "cells are scheduled CONFIG-MAJOR / PRIME-MINOR, i.e. "
                         "ROUND-ROBIN ACROSS PRIMES rather than blocked by prime, so a "
                         "monotone host drift cannot masquerade as a monotone "
                         "p-dependence. Wall and CPU time are recorded separately for "
                         "every cell and every timed window.",
        "CTRL-DRIFT-GATE": {"band": [DRIFT_GATE_LO, DRIFT_GATE_HI],
                            "fired": bool(drift_fired),
                            "interval_widening_bits_applied": widening,
                            "verdict": ("SESSION IS DRIFT-AFFECTED: every confidence "
                                        "interval is widened to cover the observed drift"
                                        if drift_fired else
                                        "both start/end ratios lie inside [0.85, 1.18]")},
    }

    det_rows = []
    for c in summary_cells:
        if c["role"] == "DRIFT-END+CTRL-DET":
            k = c["log2p_target"]
            s = None
            for cc in summary_cells:
                if cc["log2p_target"] == k and cc["role"] == "PRIMARY+DRIFT-START":
                    s = cc
            if s:
                same = (s["entries_charged_to_timed_windows"] == c["entries_charged_to_timed_windows"]
                        and s["table_size_L_total"] == c["table_size_L_total"]
                        and s["jset_sha256"] == c["jset_sha256"])
                det_rows.append({
                    "log2p": k, "cell_a": s["cell_id"], "cell_b": c["cell_id"],
                    "entries_a": s["entries_charged_to_timed_windows"],
                    "entries_b": c["entries_charged_to_timed_windows"],
                    "table_size_a": s["table_size_L_total"],
                    "table_size_b": c["table_size_L_total"],
                    "jset_sha256_a": s["jset_sha256"], "jset_sha256_b": c["jset_sha256"],
                    "exact_reproduction": bool(same),
                    "timing_ratio": (c["T_entry_s_median_PRIMARY"] / s["T_entry_s_median_PRIMARY"])
                                    if s["T_entry_s_median_PRIMARY"] else None})
    det_fail = any(not r["exact_reproduction"] for r in det_rows)
    CTRL_DET = {"rows": det_rows, "fired": bool(det_fail),
                "verdict": ("MISMATCH IN ENTRY COUNTS, TABLE SIZES OR j-INVARIANT SETS: "
                            "the affected cells are INVALID" if det_fail else
                            "entry counts, table sizes and j-invariant sets reproduce "
                            "EXACTLY under the same seeds"),
                "note": "timings are not expected to reproduce exactly and are compared "
                        "only as a ratio, which is folded into CTRL-DRIFT"}

    cc_viol = [c["cell_id"] for c in summary_cells if c["ctrl_count"]["upper_bound_violated"]]
    cc_spot = [c["cell_id"] for c in summary_cells
               if c["ctrl_count"]["spot_checks"]["phi_zero_fail"]
               or c["ctrl_count"]["spot_checks"]["filter_fail"]]
    CTRL_COUNT = {
        "per_cell": {c["cell_id"]: c["ctrl_count"] for c in summary_cells},
        "psi_provenance": {
            "source_path": args.cost_model,
            "sha256": cm_sha,
            "imported_not_reimplemented": True,
            "functions_used": ["dickman_log2_grid", "log2_rho"],
            "line_range_of_the_Psi_relation": "cost_model.py lines 162-175 (cost_for_B): "
                                              "log2M = 2*log2X + log2_rho(w), M = Psi(X,B)*X",
        },
        "CTRL-COUNT-GATE": {
            "cells_violating_lemma_3_2_upper_bound": cc_viol,
            "cells_with_failing_spot_checks": cc_spot,
            "fired": bool(cc_viol or cc_spot),
            "n_cells_fired": len(set(cc_viol) | set(cc_spot)),
            "verdict": ("IMPLEMENTATION DEFECT: the listed cells are INVALID and are "
                        "excluded from every fit. THIS IS NEVER A MATHEMATICAL FINDING "
                        "ABOUT THE FROZEN SOURCE." if (cc_viol or cc_spot)
                        else "no upper-bound violation and no failing spot check")},
    }

    MIX1 = {c["cell_id"]: c["mix1_per_ell"] for c in summary_cells}

    # ----------------------------------------------- root-count characterisation
    root_obs = {}
    for c in cells:
        agg = {}
        for s in c["steps_downsampled"]:
            key = str(s["ell"])
            a = agg.setdefault(key, {"steps": 0, "distinct_lt_withmult": 0,
                                     "withmult_equals_ell_plus_1": 0,
                                     "poly_degree_equals_ell_plus_1": 0})
            a["steps"] += 1
            if s["roots_distinct"] < s["roots_with_multiplicity"]:
                a["distinct_lt_withmult"] += 1
            if s["roots_with_multiplicity"] == s["ell"] + 1:
                a["withmult_equals_ell_plus_1"] += 1
            if s["poly_degree"] is not None and s["poly_degree"] == s["ell"] + 1:
                a["poly_degree_equals_ell_plus_1"] += 1
        root_obs[c["cell_id"]] = agg

    # -------------------------------------------------------- extrapolation
    per_field = {}
    for b2p in SECURITY_LEVELS:
        opt = cm.optimize_B(b2p, ug, log2rho)
        per_field[b2p] = {"log2T_full": opt["log2T"], "log2M": opt["log2M"],
                          "log2B_opt": opt["log2B"], "log2TDG": b2p / 2.0}

    def margin(b2p, c, lw=MARGIN_MEMORY_BUDGET_LOG2W):
        """COPIED VERBATIM from experiments/EXP-P13VOW-001/cost_model.py
        lines 266-277 (sha256 recorded above); NOT reimplemented from its
        English description and NOT re-derived.  Inputs log2T_full / log2M come
        from the committed optimize_B, unmodified."""
        f = per_field[b2p]
        overhead_bits = c * math.sqrt(b2p)
        log2Tw = f["log2T_full"] - 0.5 * min(lw, f["log2M"]) + overhead_bits
        log2speedup = f["log2TDG"] - log2Tw
        return {"overhead_bits": overhead_bits, "log2T_w": log2Tw,
                "log2speedup_vs_DG": log2speedup}

    # verify the margin definition reproduces the recorded DEC-20260724-016 figures
    margin_identification = {
        "definition": "margin(c) at log2 p := log2speedup_vs_DG of the committed model "
                      "at memory budget w = 2^%d" % MARGIN_MEMORY_BUDGET_LOG2W,
        "why_this_w": "It is the memory budget at which the committed model reproduces "
                      "BOTH figures NC-2 names: margin(c=0) and margin(c=2) at "
                      "log2 p = 256. The contract does not name a memory budget; this "
                      "identification is VERIFIED BY REPRODUCTION below, not asserted.",
        "reproduction_check": {
            "margin_c0_log2p256": margin(256, 0.0)["log2speedup_vs_DG"],
            "margin_c2_log2p256": margin(256, 2.0)["log2speedup_vs_DG"],
            "DEC-20260724-016_recorded_NIST-I_margin_bits": 2.3,
            "NC-2_recorded_framing_bits": [34, 2]},
        "all_memory_budgets_also_reported": True,
    }

    def solve_cstar(b2p=256, target=IRREPRODUCIBILITY_BAND_BITS, tol=CSTAR_TOL):
        lo, hi = 0.0, 50.0
        f = lambda c: margin(b2p, c)["log2speedup_vs_DG"] - target
        if f(lo) < 0:
            return {"c_star": None, "note": "margin already below the band at c = 0"}
        it = 0
        while hi - lo > tol and it < 500:
            mid = 0.5 * (lo + hi)
            if f(mid) > 0:
                lo = mid
            else:
                hi = mid
            it += 1
        return {"c_star": 0.5 * (lo + hi), "tolerance": tol, "iterations": it,
                "solved_by": "numerical bisection on the COMMITTED model's own margin "
                             "expression; no hand arithmetic",
                "target_bits": target,
                "target_provenance": "the 3.51-bit irreproducibility band recorded at "
                                     "DEC-20260724-016"}

    cstar = solve_cstar()

    # ------------------------------------------------- pre-registered reading
    ni_reasons = []
    if primary.get("fit_reported"):
        g = primary["goodness_of_fit"]
        for gid in ("GOF-1", "GOF-2", "GOF-3"):
            if g[gid]["fired"]:
                ni_reasons.append("%s fired on the primary series (%s)" % (gid, PRIMARY_SID))
    else:
        ni_reasons.append("no fit was reported for the primary series %s" % PRIMARY_SID)
    if ST_B["all_three_pairwise_disjoint"]:
        ni_reasons.append("ST-B: the three B intervals are pairwise disjoint")
    if ST_V["disjoint"] is True:
        ni_reasons.append("ST-V: the V-1 and V-2 intervals are disjoint")
    if CTRL_NULL["CTRL-NULL-GATE"]["fired"]:
        ni_reasons.append("CTRL-NULL-GATE fired")
    if CTRL_CAL["CTRL-CAL-GATE"]["fired"]:
        ni_reasons.append("CTRL-CAL-GATE fired")
    if primary.get("n_admissible_primes", 0) < MIN_ADMISSIBLE_PRIMES:
        ni_reasons.append("fewer than %d admissible primes remain" % MIN_ADMISSIBLE_PRIMES)

    extrapolation = None
    if ni_reasons:
        reading = "READING-NOT-IDENTIFIED"
        reading_text = ("NO EXPONENT IS IDENTIFIED IN THIS REGIME. NO c IS CARRIED INTO "
                        "THE EXTRAPOLATION AND NO MARGIN FIGURE IS PRODUCED. The measured "
                        "per-entry costs are still reported in full as the batch's result, "
                        "together with the NAMED reason the fit was not adequate. THIS "
                        "READING TAKES PRECEDENCE OVER READING-SMALL-C, READING-LARGE-C "
                        "AND READING-STRADDLE.")
    else:
        ci = primary_ci
        clo, chi = ci["lo"], ci["hi"]
        cs = cstar["c_star"]
        if chi < cs:
            reading = "READING-SMALL-C"
        elif clo > cs:
            reading = "READING-LARGE-C"
        else:
            reading = "READING-STRADDLE"
        reading_text = "evaluated mechanically from the carried interval against c_star"
        cfit = primary["M-A"]["c"]
        rows = {}
        for b2p in SECURITY_LEVELS:
            rows[str(b2p)] = {
                "LABEL": "EXTRAPOLATION",
                "margin_c_lo_bits": margin(b2p, clo)["log2speedup_vs_DG"],
                "margin_c_fit_bits": margin(b2p, cfit)["log2speedup_vs_DG"],
                "margin_c_hi_bits": margin(b2p, chi)["log2speedup_vs_DG"],
                "all_memory_budgets": {
                    "w=2^%d" % lw: {"margin_c_lo_bits": margin(b2p, clo, lw)["log2speedup_vs_DG"],
                                    "margin_c_fit_bits": margin(b2p, cfit, lw)["log2speedup_vs_DG"],
                                    "margin_c_hi_bits": margin(b2p, chi, lw)["log2speedup_vs_DG"]}
                    for lw in (30, 40, 50, 60, 70, 80)},
                "EA-1..EA-6": EA,
                "EA-3_restated_beside_the_number": EA["EA-3"],
                "EA-5_band_carried_additively_bits": IRREPRODUCIBILITY_BAND_BITS,
                "measured_or_modeled": {"c": "MEASURED (fitted from this run's timings)",
                                        "margin": "MODELED (computed by the committed "
                                                  "EXP-P13VOW-001 cost model)"},
            }
        extrapolation = {
            "STATUS": "EVERY NUMBER IN THIS BLOCK IS AN EXTRAPOLATION. THE NIST-I MARGIN "
                      "IS NOT MEASURED BY THIS EXPERIMENT. p <= 2^40 IS NOT CRYPTOGRAPHIC "
                      "SIZE; log2 p = 40 against a NIST-I target of 256 is a 6.4-fold "
                      "extrapolation in log2 p.",
            "carried_interval_used": ci, "c_fit": cfit,
            "per_security_level": rows}

    reading_block = {
        "fired": reading,
        "text": reading_text,
        "contributing_gates_named": {
            "GOF-1": primary.get("goodness_of_fit", {}).get("GOF-1", {}).get("fired"),
            "GOF-2": primary.get("goodness_of_fit", {}).get("GOF-2", {}).get("fired"),
            "GOF-3": primary.get("goodness_of_fit", {}).get("GOF-3", {}).get("fired"),
            "ST-B_all_pairwise_disjoint": ST_B["all_three_pairwise_disjoint"],
            "ST-V_disjoint": ST_V["disjoint"],
            "CTRL-CAL-GATE": CTRL_CAL["CTRL-CAL-GATE"]["fired"],
            "CTRL-NULL-GATE": CTRL_NULL["CTRL-NULL-GATE"]["fired"],
            "CTRL-DRIFT-GATE": CTRL_DRIFT["CTRL-DRIFT-GATE"]["fired"],
            "CTRL-COUNT-GATE": CTRL_COUNT["CTRL-COUNT-GATE"]["fired"],
            "CTRL-DET": CTRL_DET["fired"],
            "SEED-GATE": ST_SEED["SEED_GATE"]["fired"],
            "n_admissible_primes_primary": primary.get("n_admissible_primes"),
        },
        "not_identified_reasons": ni_reasons,
        "c_star": cstar,
        "margin_identification": margin_identification,
        "evaluated": "MECHANICALLY, by the rules frozen in EXP-SSI-002. The executor "
                     "records which reading fired and writes no interpretation.",
    }

    # ------------------------------------------------------------------ write
    summary = {
        "schema": "EXP-SSI-002.summary.v1",
        "experiment_id": "EXP-SSI-002", "run_id": "RUN-SSI-002",
        "cells": summary_cells,
        "cells_not_reached": raw["cells_not_reached"],
        "mandatory_cell_accounting": {
            "mandatory_cell_count_declared": 34,
            "cells_executed_total": len(summary_cells),
            "primary_role_cells": len([c for c in summary_cells
                                       if c["role"].startswith("PRIMARY")]),
            "seed_b_cells": len([c for c in summary_cells if c["seeding"] == "SEED-B"]),
            "re_execution_cells": len([c for c in summary_cells
                                       if c["role"] == "DRIFT-END+CTRL-DET"]),
            "under_sampled_cells": [{"cell_id": c["cell_id"],
                                     "entries": c["entries_charged_to_timed_windows"]}
                                    for c in summary_cells if not c["admissible"]],
            "optional_if_budget_skipped_by_name":
                ["B-FIX-32 under V-2 at every prime (OPTIONAL-IF-BUDGET in the contract)"],
        },
        "root_count_observation_phi_vs_velu": root_obs,
        "root_count_observation_scope": "aggregated over the RETAINED per-step records "
            "(the downsampling k is recorded per cell). The invariant tested per step is "
            "roots_with_multiplicity == ell + 1 for V-1 and n_isogenies == ell + 1 for V-2.",
        "sage_startup_seconds": raw["sage_startup_seconds"],
        "budget_used": raw["budget_used"],
        "stopped_reason": raw["stopped_reason"],
    }
    fit_report = {
        "schema": "EXP-SSI-002.fit_report.v1",
        "experiment_id": "EXP-SSI-002", "run_id": "RUN-SSI-002",
        "recomputed_from": "raw-timings.json ALONE",
        "primary_series_id": PRIMARY_SID,
        "primary_series_selection_note":
            "SPECIFICATION AMBIGUITY REPORTED, NOT RESOLVED BY PREFERENCE: the frozen "
            "contract names V-1, SEED-A, T_entry_ops and the AMORTISED Phi accounting as "
            "primary, but names NO primary B setting. B-ASY is used as the primary series "
            "because the contract's own rationale for it ('the paper's own asymptotic "
            "parameter choice, so its fitted c is the one comparable to the red team's "
            "c ~ 1.8 calibration') is the one tied to the parameterisation the "
            "extrapolation substitutes into. ALL THREE B SERIES ARE REPORTED WITH EQUAL "
            "COMPLETENESS and the extrapolation is computed for all of them, so the "
            "choice is not load-bearing.",
        "fits": fits,
        "fit_exclusions_named": exclusions,
        "FIT_ELL": fit_ell,
        "FIT_ELL_vs_pooled": fitell_vs_pooled,
        "stability": {"ST-B": ST_B, "ST-V": ST_V, "ST-SEED": ST_SEED,
                      "ST-NORM": ST_NORM,
                      "amortised_vs_fully_charged": amort_vs_full},
        "extrapolation": extrapolation,
        "c_star": cstar,
        "margin_identification": margin_identification,
        "pre_registered_reading": reading_block,
        "cost_model_provenance": {
            "path": args.cost_model, "sha256": cm_sha,
            "modified": False, "main_executed": False,
            "usage": "imported as a module; optimize_B / dickman_log2_grid / log2_rho "
                     "called unmodified; the margin expression is COPIED VERBATIM from "
                     "cost_model.py lines 266-277 and is not re-derived",
        },
        "extrapolation_for_all_series": {
            sid: ({"carried_interval": fits[sid]["M-A"]["carried_interval"],
                   "c_fit": fits[sid]["M-A"]["c"],
                   "gof_any_fired": fits[sid]["goodness_of_fit"]["any_fired"],
                   "LABEL": "EXTRAPOLATION",
                   "margins_at_log2p": {
                       str(b): {"margin_c_lo_bits": margin(b, fits[sid]["M-A"]["carried_interval"]["lo"])["log2speedup_vs_DG"],
                                "margin_c_fit_bits": margin(b, fits[sid]["M-A"]["c"])["log2speedup_vs_DG"],
                                "margin_c_hi_bits": margin(b, fits[sid]["M-A"]["carried_interval"]["hi"])["log2speedup_vs_DG"]}
                       for b in SECURITY_LEVELS},
                   "EA-3_restated_beside_the_number": EA["EA-3"],
                   "note": "REPORTED FOR COMPLETENESS SO THE PRIMARY-SERIES CHOICE IS NOT "
                           "LOAD-BEARING. If the pre-registered reading is "
                           "READING-NOT-IDENTIFIED, NO c IS CARRIED and these figures are "
                           "reported as arithmetic on a fit that was declared not "
                           "adequate, NOT as a margin claim."}
                  if (fits[sid].get("fit_reported")
                      and fits[sid]["M-A"]["carried_interval"]
                      and fits[sid]["M-A"]["carried_interval"]["lo"] is not None)
                  else {"fit_reported": bool(fits[sid].get("fit_reported")),
                        "note": "no carried interval available; no margin arithmetic performed"})
            for sid in fits if sid.endswith("T_entry_ops_amortised")},
    }
    controls = {
        "schema": "EXP-SSI-002.controls.v1",
        "experiment_id": "EXP-SSI-002", "run_id": "RUN-SSI-002",
        "CTRL-CAL": CTRL_CAL, "CTRL-NULL": CTRL_NULL, "CTRL-DRIFT": CTRL_DRIFT,
        "CTRL-COUNT": CTRL_COUNT, "CTRL-DET": CTRL_DET, "MIX-1": MIX1,
        "root_count_observation_phi_vs_velu": root_obs,
    }

    for name, obj in (("summary.json", summary), ("fit_report.json", fit_report),
                      ("controls.json", controls)):
        with open(os.path.join(args.run_dir, name), "w") as f:
            json.dump(obj, f, indent=1, sort_keys=False, default=str)
        print("wrote %s" % name)

    print("\nPRIMARY SERIES: %s" % PRIMARY_SID)
    if primary.get("fit_reported"):
        ma = primary["M-A"]
        print("  M-A c = %.5f  CI-T [%s]  CI-BOOT [%s]  CARRIED [%.5f, %.5f] from %s"
              % (ma["c"],
                 "%.5f, %.5f" % (ma["CI_T"]["lo"], ma["CI_T"]["hi"]) if ma["CI_T"] else "n/a",
                 "%.5f, %.5f" % (ma["CI_BOOT"]["lo"], ma["CI_BOOT"]["hi"]) if ma["CI_BOOT"]["lo"] is not None else "n/a",
                 ma["carried_interval"]["lo"], ma["carried_interval"]["hi"],
                 ma["carried_interval"]["carried_from"]))
        print("  residual sign pattern %s   max|resid| %.4f bits   R2 %.4f"
              % (ma["residual_sign_pattern"], ma["max_abs_residual_bits"], ma["r2"]))
        g = primary["goodness_of_fit"]
        for gid in ("GOF-1", "GOF-2", "GOF-3"):
            print("  %s fired=%s : %s" % (gid, g[gid]["fired"], g[gid]["verdict"]))
    print("  c_star = %s" % cstar.get("c_star"))
    print("  READING FIRED: %s" % reading_block["fired"])
    for r in ni_reasons:
        print("    reason: %s" % r)
    return 0


if __name__ == "__main__":
    sys.exit(main())
