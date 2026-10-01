#!/usr/bin/env python3
"""TASK-20260929-c40e48 J2 supplement (blind): large-rep (2,000,000) limit of the
stratified percentile bootstrap endpoints for S6-smallx and S7-smallx (12..32),
own numpy implementation (rederive.own_boot_slopes), to locate the
reps -> infinity percentile interval relative to the model values."""
import gzip, json, math, sys
import numpy as np
sys.path.insert(0, ".")
from rederive import own_boot_slopes  # own code in this directory; imports only numpy/stdlib
rows = [json.loads(l) for l in gzip.open("j2-floor-rows.jsonl.gz", "rt")]
out = {}
for name, m, model in (("S6-smallx", 6, 1 / 12), ("S7-smallx", 7, 0.0)):
    sel = [x for x in rows if x["file"] == "sweep-arity67-20260928" and x["m"] == m and x["engine"] == "mitm"]
    xs = [x["log2N"] for x in sel]; ys = [math.log2(x["ratio"]) for x in sel]; gs = [x["bits"] for x in sel]
    b = np.sort(own_boot_slopes(xs, ys, gs, 2_000_000, 99_000_001))
    n = len(b)
    lo_idx, hi_idx = b[int(math.floor(0.025 * (n - 1)))], b[int(math.ceil(0.975 * (n - 1)))]
    # binomial MC error of the 2.5% order statistic, as an index band of +-2 sd
    sd_idx = math.sqrt(n * 0.025 * 0.975)
    band = (float(b[int(0.025 * n - 2 * sd_idx)]), float(b[int(0.025 * n + 2 * sd_idx)]))
    out[name] = {"reps": n, "model": model, "lo_statspy_idx": float(lo_idx), "hi_statspy_idx": float(hi_idx),
                 "lo_linear": float(np.quantile(b, 0.025)), "hi_linear": float(np.quantile(b, 0.975)),
                 "lo_2sd_band": band, "lower_minus_model": float(lo_idx) - model,
                 "bootstrap_prob_slope_below_model": float(np.mean(b < model))}
print(json.dumps(out, indent=1))
json.dump(out, open("j2-limit-2m.json", "w"), indent=1)
