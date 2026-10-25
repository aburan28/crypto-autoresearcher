"""Red team TASK-20261023-20d7d9: decompose the random-generator (PTM-1) naive success rate.

For every prime 50 < p < 2000 and EVERY primitive root g (exhaustive over g), count the sub-p
chain {d in [2, p-3] : g^d < p} (certain successes; the producer's mechanism) and the band
{d : p <= g^d < p^2} (certain failures). For the rest region the exact success count is
enumerated for every root of the primes below 600 and for 16 sampled roots above (the rest
region has no generator-size structure). Output: the population rate under a uniformly random
primitive root, split into sub-p, band and rest, against 1/p.
Usage: python3 -B ptm1_b_decompose.py   (repository root)
"""
from __future__ import annotations

import json
import math
import random

from ptm1_generator_controls import primes_between, factor_set, is_primroot, padic_success

rng = random.Random(7)
P = primes_between(50, 2000)
acc = {"subp": 0.0, "band_rows": 0.0, "rest": 0.0, "inv_p": 0.0}
for p in P:
    fs = factor_set(p - 1)
    roots = [g for g in range(2, p) if is_primroot(g, p, fs)]
    dom = p - 4
    lp = math.log(p)
    sub = band = 0
    for g in roots:
        lg = math.log(g)
        sub += sum(1 for d in range(2, p - 2) if d * lg < lp - 1e-12)
        band += sum(1 for d in range(2, p - 2) if lp - 1e-12 <= d * lg < 2 * lp - 1e-12)
    acc["subp"] += sub / len(roots) / dom
    acc["band_rows"] += band / len(roots) / dom
    sample = roots if p < 600 else rng.sample(roots, min(16, len(roots)))
    rest = 0.0
    p2 = p * p
    for g in sample:
        wief = pow(g, p - 1, p2) == 1
        cur = g * g % p2
        lg = math.log(g)
        for d in range(2, p - 2):
            if d * lg >= 2 * lp - 1e-12:
                rest += padic_success(p, g, d) if wief else (cur < p)
            cur = cur * g % p2
    acc["rest"] += rest / len(sample) / dom
    acc["inv_p"] += 1 / p
n = len(P)
out = {k: v / n for k, v in acc.items()}
out["ratio_subp_to_inv_p"] = acc["subp"] / acc["inv_p"]
out["ratio_rest_to_inv_p"] = acc["rest"] / acc["inv_p"]
out["ratio_total_to_inv_p"] = (acc["subp"] + acc["rest"]) / acc["inv_p"]
out["note"] = "rates are per (p, d) pair averaged over primes; band rows can never succeed"
json.dump(out, open("experiments/EXP-CZLIFT-bdae69/reports/redteam-20261023/ptm1_b_decompose_output.json", "w"), indent=1)
print(json.dumps(out, indent=1))
