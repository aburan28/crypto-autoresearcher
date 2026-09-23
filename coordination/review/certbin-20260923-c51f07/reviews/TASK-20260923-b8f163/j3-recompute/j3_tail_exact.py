#!/usr/bin/env python3
"""TASK-20260923-b8f163 J3: exact recomputation of the M2 tail-extremes check
(spec tail_checks, first bullet) from the validator's own P2 set, under the null
the producer states: independent Binomial(S_k, 1/2) per pivot in the set.
Exact arithmetic (mpmath, 150 digits; 60 cannot resolve 1 - (1 - 1e-75)). Compares with cell-summary M2 tail_extremes."""
import json, os
import mpmath as mp
mp.mp.dps = 150
HERE = os.path.dirname(os.path.abspath(__file__))
J3 = json.load(open(os.path.join(HERE, "j3_recompute.json")))
P2 = J3["M2"]["P2"]
hs = [p["h"] for p in P2]; mn, mx = min(hs), max(hs)
def pmf(k, n): return mp.binomial(n, k) / mp.mpf(2) ** n
def sf(k, n): return mp.fsum(pmf(i, n) for i in range(k, n + 1))   # P(X >= k)
def cdf(k, n): return mp.fsum(pmf(i, n) for i in range(0, k + 1))  # P(X <= k)
pa = mp.mpf(1); pb = mp.mpf(1)
for p in P2:
    S = p["S_k"]
    pa *= sf(int(mp.floor(mn * S)) + 1, S)
    pb *= cdf(int(mp.ceil(mx * S)) - 1, S)
exact_min = 1 - pa; exact_max = 1 - pb
approx = mp.fsum(mp.mpf(2) ** (-p["S_k"]) for p in P2)
RUN = os.path.abspath(os.path.join(HERE, *[".."] * 6, "experiments/EXP-CERTBIN-4e92d7/runs/RUN-CERTBIN-3b7e05"))
cs = json.load(open(os.path.join(RUN, "cell-summary.json")))["M2"]["tail_extremes"]
out = {"observed_min_h": mn, "observed_max_h": mx,
       "exact_P_null_min_le_observed": mp.nstr(exact_min, 6), "sum_2^-S_k_check": mp.nstr(approx, 6),
       "log10_exact_P_min": mp.nstr(mp.log10(exact_min), 6),
       "exact_P_null_max_ge_observed": mp.nstr(exact_max, 12),
       "producer_P_null_min_le_observed": cs["P_null_min_le_observed"],
       "producer_P_null_max_ge_observed": cs["P_null_max_ge_observed"],
       "S_k_of_zero_hazard_pairs": sorted(p["S_k"] for p in P2 if p["h"] == 0)}
json.dump(out, open(os.path.join(HERE, "j3_tail_exact.json"), "w"), indent=1)
print(json.dumps(out, indent=1))
