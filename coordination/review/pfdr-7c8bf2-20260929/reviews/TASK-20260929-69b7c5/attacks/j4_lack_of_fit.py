"""J4: is there between-rung structure the stratified bootstrap cannot see?

stats.bootstrap_slope resamples curves WITHIN each rung, so its interval reflects only
curve-to-curve scatter; systematic rung-to-rung departures from a straight line (lower-order
terms) are held fixed in every replicate.  Lack-of-fit statistic per series (12..32):
  F_lof = [sum_k n_k * rbar_k^2 / (K - 2)] / [sum_i (y_i - ybar_k(i))^2 / (n - K)]
(rbar_k = mean OLS residual in rung k; K = 11 rungs).  Null: per-rung Gaussian with the
observed within-rung SD around the fitted line (heteroscedastic, no lack of fit), 20000
draws, p = P(F_null >= F_obs).  Also the rung-mean residual pattern.
Seeds: numpy default_rng([0x69b7c5, 17, series_index]).
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

K = 20000
res = {}


def lof(x, Y, g):
    """Y: (R, n).  Returns F_lof per row."""
    xc = x - x.mean()
    b = (Y - Y.mean(1, keepdims=True)) @ xc / (xc @ xc)
    a = Y.mean(1) - b * x.mean()
    Rz = Y - (a[:, None] + b[:, None] * x[None, :])
    ks = np.unique(g)
    ss_lof = np.zeros(Y.shape[0])
    ss_pe = np.zeros(Y.shape[0])
    for k in ks:
        s = g == k
        rb = Rz[:, s].mean(1)
        ss_lof += s.sum() * rb ** 2
        ss_pe += ((Y[:, s] - Y[:, s].mean(1, keepdims=True)) ** 2).sum(1)
    return (ss_lof / (len(ks) - 2)) / (ss_pe / (len(x) - len(ks)))


for si, name in enumerate(C.SERIES):
    rows = C.series_rows(name)
    x = np.array([r["log2N"] for r in rows])
    y = np.array([math.log2(C.ratio(r)) for r in rows])
    g = np.array([r["bits"] for r in rows])
    F_obs = float(lof(x, y[None, :], g)[0])
    b, a = C.ols(x, y)
    rng = np.random.default_rng([0x69b7c5, 17, si])
    E = np.empty((K, len(x)))
    for k in np.unique(g):
        s = np.where(g == k)[0]
        E[:, s] = rng.normal(0, y[s].std(ddof=1), size=(K, len(s)))
    Fn = lof(x, (a + b * x)[None, :] + E, g)
    rbar = {int(k): float((y - (a + b * x))[g == k].mean()) for k in np.unique(g)}
    res[name] = {"F_lof_obs": F_obs, "p_parametric_null": float((Fn >= F_obs).mean()),
                 "rung_mean_residual_log2": rbar,
                 "within_rung_sd_log2": {int(k): float(y[g == k].std(ddof=1)) for k in np.unique(g)}}
    print("%-22s F_lof=%.2f p=%.4f rbar=%s" % (name, F_obs, res[name]["p_parametric_null"],
                                               {k: round(v, 3) for k, v in rbar.items()}), flush=True)
print(C.dump("j4_lack_of_fit.json", res))
