"""proves_too_much (added object): the model TRUE by construction on the committed |F| design.

The plan's synthetic objects put a straight line of slope theta through the rows.  The more
inconvenient object keeps the model's own exponents (so the asymptotic slope IS theta =
1/(2m) or 0) but evaluates it at the committed per-row (N, fb_size, relations), where
fb_size = max(4, ceil(((m! N)/2)^(1/m)/2)) is a deterministic function of N:
   V1 search-only : mu_i = 0.5*log2 N_i + (0.5 - h)*log2 F_i
   V2 table+search: mu_i = log2((cT*F^h + cS*r*N*F^-h) / (0.5*sqrt(r*N)))
                    (theory exponents; cT, cS = geometric means of the committed table and
                    search columns, as in j4_lower_order.py M6)
plus noise R1 (the frozen fit's residuals resampled within rung) or R3 (per-rung Gaussian
with the observed within-rung SD).  The frozen interval (FastBoot == stats.bootstrap_slope)
is tested against the ASYMPTOTIC model value exactly as F-2/F-3 do.  If it excludes that value
materially more often than 5%, the frozen F-2/F-3 test "falsifies" a model that is true.

Also: exclusion-probability curve for S6 when the finite-range slope is 1/12 + delta
(linear mean, R3 noise), delta in 0..0.03.
Seeds: numpy default_rng([0x69b7c5, 11, series_index, variant_index, noise_index]),
family-wise rng([0x69b7c5, 12, variant_index, noise_index]), curve rng([0x69b7c5, 13, j]).
K = 20000.
"""
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

K = 20000
names = list(C.SERIES)
res = {"K": K, "per_series": {}, "family_wise": {}, "s6_bias_curve": {}}

D = {}
for name in names:
    f, m, fb = C.SERIES[name]
    h = C.table_arity(m)
    rows = C.series_rows(name)
    x = np.array([r["log2N"] for r in rows])
    y = np.array([math.log2(C.ratio(r)) for r in rows])
    F = np.array([r["fb_size"] for r in rows], float)
    rr = np.array([r["relations"] for r in rows], float)
    N = np.array([r["N"] for r in rows], float)
    T = np.array([r["table_s3_solves"] for r in rows], float)
    srch = np.array([r["s3_solves"] for r in rows], float) - T
    g = np.array([r["bits"] for r in rows])
    cT = 2 ** float(np.mean(np.log2(T) - h * np.log2(F)))
    cS = 2 ** float(np.mean(np.log2(srch) - np.log2(rr) - np.log2(N) + h * np.log2(F)))
    mu = {"V1_search_only": 0.5 * np.log2(N) + (0.5 - h) * np.log2(F),
          "V2_table_plus_search": np.log2((cT * F ** h + cS * rr * N * F ** (-h)) / (0.5 * np.sqrt(rr * N)))}
    b, a = C.ols(x, y)
    D[name] = {"x": x, "y": y, "g": g, "resid": y - (a + b * x), "mu": mu, "theta": C.model_value(m),
               "fbt": C.FastBoot(x, list(g)), "keys": [(r["bits"], r["curve"]) for r in rows]}


def noise(rng, d, kind, K_):
    E = np.empty((K_, len(d["x"])))
    for gg in np.unique(d["g"]):
        pos = np.where(d["g"] == gg)[0]
        if kind == "R1":
            E[:, pos] = d["resid"][pos][rng.integers(0, len(pos), size=(K_, len(pos)))]
        else:
            E[:, pos] = rng.normal(0, d["y"][pos].std(ddof=1), size=(K_, len(pos)))
    return E


flags = {}
for si, name in enumerate(names):
    d = D[name]
    out = {"theta_asymptotic": d["theta"]}
    for vi, v in enumerate(("V1_search_only", "V2_table_plus_search")):
        finite_slope = C.ols(d["x"], d["mu"][v])[0]
        out[v] = {"finite_range_slope_of_true_mean": finite_slope}
        for ni, kind in enumerate(("R1", "R3")):
            rng = np.random.default_rng([0x69b7c5, 11, si, vi, ni])
            Y = d["mu"][v][None, :] + noise(rng, d, kind, K)
            s, lo, hi = d["fbt"].interval(Y)
            ex = (lo > d["theta"]) | (hi < d["theta"])
            flags[(name, v, kind)] = ex
            out[v][kind] = {"p_exclude_asymptotic": float(ex.mean()),
                            "p_lo_above": float((lo > d["theta"]).mean()),
                            "p_hi_below": float((hi < d["theta"]).mean())}
    res["per_series"][name] = out
    print(name, "theta=%.4f" % d["theta"], {v: "slope*=%.4f R1 excl=%.3f R3 excl=%.3f (lo>th %.3f)" % (
        out[v]["finite_range_slope_of_true_mean"], out[v]["R1"]["p_exclude_asymptotic"],
        out[v]["R3"]["p_exclude_asymptotic"], out[v]["R3"]["p_lo_above"]) for v in ("V1_search_only", "V2_table_plus_search")},
        flush=True)

for v in ("V1_search_only", "V2_table_plus_search"):
    for kind in ("R1", "R3"):
        M = np.stack([flags[(n, v, kind)] for n in names], 1)
        res["family_wise"][f"{v}|{kind}|independent"] = {
            "p_at_least_one_of_8": float(M.any(1).mean()),
            "p_at_least_one_even_m": float(M[:, [i for i, n in enumerate(names) if C.SERIES[n][1] % 2 == 0]].any(1).mean()),
            "mean_number": float(M.sum(1).mean())}
        print("FW", v, kind, res["family_wise"][f"{v}|{kind}|independent"], flush=True)

d = D["S6-smallx"]
for j, delta in enumerate([0.0, 0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02, 0.025, 0.03]):
    rng = np.random.default_rng([0x69b7c5, 13, j])
    Y = (d["theta"] + delta) * d["x"][None, :] + noise(rng, d, "R3", K)
    s, lo, hi = d["fbt"].interval(Y)
    res["s6_bias_curve"][str(delta)] = {"p_lo_above_1_12": float((lo > d["theta"]).mean())}
print("S6 bias curve", {k: round(v["p_lo_above_1_12"], 3) for k, v in res["s6_bias_curve"].items()})
print(C.dump("ptm_design_null.json", res))
