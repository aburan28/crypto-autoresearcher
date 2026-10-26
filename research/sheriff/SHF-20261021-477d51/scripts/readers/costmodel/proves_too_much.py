#!/usr/bin/env python3
"""Reader costmodel (SHF-20261021-477d51): proves-too-much control on the campaign's
argument "the plan beats each one-change neighbour (x0.5 and x2 base), so the
planner's base size is the better one".  Known-false objects: base sizes M that are
NOT the counted optimum (S(M) at least 3% / 5% above the fitted optimum).  Using the
per-curve 3-point fit S(N) = A N^2 + B/N + C (w = 0) from sessions_costmodel.out.json,
find the range of M for which the same x0.5/x2 neighbourhood test would still
'confirm' M (both neighbour ratios above 1.10, roughly the lower-CI>1 threshold the
campaign's ~+-8% paired intervals imply).  If that range contains clearly suboptimal M,
the test cannot tell the planner's N from them.  argv[1] = sessions_costmodel.out.json"""
import json, sys
d = json.load(open(sys.argv[1]))
out = {}
for c, info in d.items():
    f = info["three_point_fit"]["0.0"]
    A, B, C = f["A"], f["B"], f["C"]
    N = info["plan_N_in_spec"]
    S = lambda m: A * m * m + B / m + C
    nstar = f["N_star"]
    smin = S(nstar)
    passing = []
    for k in [x / 100 for x in range(40, 301)]:
        M = k * N
        if S(M / 2) / S(M) > 1.10 and S(2 * M) / S(M) > 1.10:
            passing.append((k, S(M) / smin))
    ks = [k for k, _ in passing]
    worst = max(passing, key=lambda t: t[1]) if passing else None
    out[c] = {"N": N, "N_star_over_N": nstar / N, "pass_range_k": [min(ks), max(ks)] if ks else None,
              "worst_passing_k_and_S_over_Smin": worst,
              "passing_with_S_over_Smin_ge_1.03": [k for k, r in passing if r >= 1.03][:1] + [k for k, r in passing if r >= 1.03][-1:],
              "passing_with_S_over_Smin_ge_1.05": [k for k, r in passing if r >= 1.05][:1] + [k for k, r in passing if r >= 1.05][-1:]}
json.dump(out, sys.stdout, indent=1)
