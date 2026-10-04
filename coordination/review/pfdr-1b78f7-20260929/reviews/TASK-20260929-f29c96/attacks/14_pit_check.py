"""Check by simulation (not recall) that the frozen randomized PIT with Poisson counts drawn at the
recorded means gives a KS 1% rejection rate near 0.01 (the basis of 08_a6.py's iid-uniform FWER
simulation).  (class, m) = TT|4 and TB|5 (small means, fast exact Poisson CDF).  2000 replicates each,
numpy default_rng(20261103).  Output: attacks/out/14_pit_check.json
"""
import json, math, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rtlib import OUT, RANDOM_ARMS, canonical_rows, m_of, usable
import importlib.util
spec = importlib.util.spec_from_file_location("a6", os.path.join(os.path.dirname(os.path.abspath(__file__)), "08_a6.py"))
a6 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a6)
rows = canonical_rows("census-m4") + canonical_rows("census-m5")
out = {}
rng = np.random.default_rng(20261103)
for (c, m) in (("TT", 4), ("TB", 5)):
    mus, hi = [], []
    for r in rows:
        if r.get("arm") in RANDOM_ARMS and r.get("mode") == "census" and usable(r) and m_of(r) == m:
            mus.append(r["harvest"][c]["at_stop"]["poisson_mean"]); hi.append(20 <= r["bits"] <= 32)
    mus, hi = np.array(mus), np.array(hi)
    Dc_all, Dc_hi = a6.d_crit(len(mus)), a6.d_crit(int(hi.sum()))
    rej = 0
    for _ in range(2000):
        n = rng.poisson(mus)
        V = rng.random(len(mus))
        F1 = np.array([a6.poisson_cdf(int(k), mu) for k, mu in zip(n, mus)])
        F0 = np.array([a6.poisson_cdf(int(k) - 1, mu) for k, mu in zip(n, mus)])
        u = F0 + V * (F1 - F0)
        rej += (a6.ks_D(u) > Dc_all) or (a6.ks_D(u[hi]) > Dc_hi)
    out[f"{c}|{m}"] = {"instances": len(mus), "max_mu": float(mus.max()), "reject_rate_either_range": rej / 2000,
                       "binomial_se": math.sqrt((rej / 2000) * (1 - rej / 2000) / 2000)}
json.dump(out, open(os.path.join(OUT, "out", "14_pit_check.json"), "w"), indent=1)
print(out)
