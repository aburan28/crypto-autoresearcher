"""J4: what the excess should do as the parameter meant to destroy it grows.

A lower-order term in the 12..32 slope must shrink as the lowest rung of the fit rises; a
real exponent shift must not.  Frozen fit (stats.bootstrap_slope, groups = bits, 2000 reps,
seed 0) of each even-m series and of S7 on lo..32 for lo = 12, 14, ..., 24, reported as
slope - model value with the interval.  Also the same scan of the paired same-curve
contrasts S6 - S7 and S4 - S5.  No randomness beyond seed 0.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
res = {}
for name in ("S6-smallx", "S7-smallx", "S4-smallx", "S5-smallx"):
    th = C.model_value(C.SERIES[name][1])
    d = {}
    for lo in (12, 14, 16, 18, 20, 22, 24):
        xs, ys, gs = C.xs_ys(C.series_rows(name, lo))
        v = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=C.SEED)
        d[lo] = {**v, "excess": v["slope"] - th, "contains_model": v["lo"] <= th <= v["hi"]}
    res[name] = d
    print(name, " ".join("%d:%+.4f[%+.4f,%+.4f]" % (lo, v["excess"], v["lo"] - th, v["hi"] - th) for lo, v in d.items()))
for a, b in (("S6-smallx", "S7-smallx"), ("S4-smallx", "S5-smallx")):
    th = C.model_value(C.SERIES[a][1]) - C.model_value(C.SERIES[b][1])
    d = {}
    for lo in (12, 14, 16, 18, 20, 22, 24):
        ra = C.series_rows(a, lo)
        rb = {(r["bits"], r["curve"]): r for r in C.series_rows(b, lo)}
        xs = [r["log2N"] for r in ra]
        ys = [math.log2(C.ratio(r)) - math.log2(C.ratio(rb[(r["bits"], r["curve"])])) for r in ra]
        gs = [r["bits"] for r in ra]
        v = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=C.SEED)
        d[lo] = {**v, "excess": v["slope"] - th, "contains_model": v["lo"] <= th <= v["hi"]}
    res[f"{a} minus {b}"] = d
    print(a, "-", b, " ".join("%d:%+.4f[%+.4f,%+.4f]" % (lo, v["excess"], v["lo"] - th, v["hi"] - th) for lo, v in d.items()))
print(C.dump("j4_range_scan.json", res))

# ---- calibration of the scan itself: seven overlapping looks at one series under the model.
# Synthetic S6 / S4 series with the linear model slope true (R3: per-rung Gaussian with the
# observed within-rung SD), all seven lower ends fitted on the SAME synthetic series with the
# frozen procedure (FastBoot == stats.bootstrap_slope).  Seeds: rng([0x69b7c5, 19, j]); K = 20000.
import numpy as np  # noqa: E402

K = 20000
scan_cal = {}
for j, name in enumerate(("S6-smallx", "S4-smallx", "S7-smallx")):
    th = C.model_value(C.SERIES[name][1])
    rows = C.series_rows(name)
    x = np.array([r["log2N"] for r in rows])
    y = np.array([math.log2(C.ratio(r)) for r in rows])
    g = np.array([r["bits"] for r in rows])
    rng = np.random.default_rng([0x69b7c5, 19, j])
    E = np.empty((K, len(x)))
    for b_ in np.unique(g):
        pos = np.where(g == b_)[0]
        E[:, pos] = rng.normal(0, y[pos].std(ddof=1), size=(K, len(pos)))
    Y = th * x[None, :] + E
    ex = []
    for lo in (12, 14, 16, 18, 20, 22, 24):
        sel = np.where(g >= lo)[0]
        fbt = C.FastBoot(x[sel], list(g[sel]))
        _, l_, h_ = fbt.interval(Y[:, sel])
        ex.append((l_ > th) | (h_ < th))
    M = np.stack(ex, 1)
    scan_cal[name] = {"K": K, "p_exclude_per_look": M.mean(0).round(4).tolist(),
                      "p_at_least_one_of_7": float(M.any(1).mean()),
                      "p_at_least_two_of_7": float((M.sum(1) >= 2).mean()),
                      "p_first_and_last_both": float((M[:, 0] & M[:, -1]).mean())}
    print("scan calibration", name, scan_cal[name], flush=True)
res["scan_calibration_under_model"] = scan_cal
print(C.dump("j4_range_scan.json", res))
