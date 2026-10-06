"""J6 / P7(c): does the per-row yield q = r / mu_TS track the design's decomposition density?

lambda_i = (2 |F|)^m / (m! N) is the engine's own expected number of decompositions per
target at the committed fb_size (factor_base.default_fb_size docstring's approximation; a
deterministic function of N through fb_size = max(4, ceil(...))).  If H1's "ordering
constant" were a constant, log q would be uncorrelated with log lambda within a rung.
Reports, per m (primary-series rows, P3): corr(log q, log lambda) over all rows and after
removing rung means; corr(log q, log attempts/relation) within rung (the stochastic part);
within-rung SD of log q; per-rung median q / c_m and median attempts per relation and
table share.  Deterministic (no randomness).
"""
import math
import os
import statistics
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

res = {}
for m in (3, 4, 5, 6, 7):
    rows = [r for n in C.SERIES if C.SERIES[n][1] == m for r in C.series_rows(n)]
    mu = np.array([2 * r["table_entries"] * 2 * (r["s3_solves"] - r["table_s3_solves"]) / r["N"] for r in rows])
    rel = np.array([r["relations"] for r in rows], float)
    c = rel.sum() / mu.sum()
    q = np.log(rel / mu)
    lam = np.log(np.array([(2 * r["fb_size"]) ** m / math.factorial(m) / r["N"] for r in rows]))
    ar = np.log(np.array([r["attempts"] / r["relations"] for r in rows]))
    b = np.array([r["bits"] for r in rows])
    qd, ld, ad = q.copy(), lam.copy(), ar.copy()
    per_rung = {}
    for g in np.unique(b):
        s = b == g
        qd[s] -= q[s].mean()
        ld[s] -= lam[s].mean()
        ad[s] -= ar[s].mean()
        idx = np.where(s)[0]
        per_rung[int(g)] = {
            "median_q_over_c": float(np.median(np.exp(q[s]) / c)),
            "median_lambda": float(np.median(np.exp(lam[s]))),
            "median_attempts_per_relation": float(np.median(np.exp(ar[s]))),
            "median_table_share": statistics.median(rows[i]["table_s3_solves"] / rows[i]["s3_solves"] for i in idx),
            "relations": [rows[i]["relations"] for i in idx]}
    res[m] = {"n": len(rows), "c_m": float(c),
              "corr_logq_loglambda_all": float(np.corrcoef(q, lam)[0, 1]),
              "corr_logq_loglambda_within_rung": float(np.corrcoef(qd, ld)[0, 1]),
              "corr_logq_log_att_per_rel_within_rung": float(np.corrcoef(qd, ad)[0, 1]),
              "within_rung_sd_logq": float(qd.std(ddof=1)), "per_rung": per_rung}
    print("m=%d c=%.4f corr(q,lam) all=%.2f within=%.2f corr(q,att/rel) within=%.2f sd=%.3f" % (
        m, c, res[m]["corr_logq_loglambda_all"], res[m]["corr_logq_loglambda_within_rung"],
        res[m]["corr_logq_log_att_per_rel_within_rung"], res[m]["within_rung_sd_logq"]))
    print("   ", {g: "q/c=%.2f lam=%.2f a/r=%.2f T=%.3f" % (v["median_q_over_c"], v["median_lambda"],
                                                         v["median_attempts_per_relation"], v["median_table_share"])
                  for g, v in per_rung.items()})
print(C.dump("j6_q_lambda.json", res))
