#!/usr/bin/env python3
"""Red team TASK-20261023-792040, R1 (unanticipated): generator-covariant leaks through EVEN and ODD digits.

x(-R) = x(R), so any x-digit is an even function of k; y(-R) = -y(R), so a y-digit at i >= 1 satisfies
a_i(-k) = p-1-a_i(k) (odd-type). A DL leak that does not depend on which generator P the experiment drew
must be covariant under P -> uP, k -> u^-1 k. For a multiplier j (unknown, random relative to the drawn P):
  FOLD_j (even, x-type):  f(k) = floor(p r(jk) / n),  r(x) = min(x mod n, n - x mod n)   -> reveals +-jk
  ODD_j  (odd, y-type):   f(k) = floor(p (jk mod n) / n) if jk mod n <= h else p-1-floor(p (n - jk mod n) / n)
FOLD_1 is the plan's PTM-1 on the half range. Runs the producer's unchanged run.spectrum at every (p, n)
of the 72 records with 5 random j != +-1 each (seeded) and reports spikes by record.
Usage: rt_fold.py OUT.json"""
import json, math, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO, "experiments", "EXP-CZLIFT-1a3453", "implementation"))
import run as driver  # noqa: E402
BASE = os.path.join(REPO, "experiments", "EXP-CZLIFT-1a3453")
seen = {}
for run in ("RUN-CZLIFT-037e5f", "RUN-CZLIFT-d37ca4"):
    for c in json.load(open(os.path.join(BASE, "runs", run, "raw-result.json")))["raw"]["curves"]:
        seen.setdefault((c["p"], c["n"]), 0)
        seen[(c["p"], c["n"])] += 1
rows = []
for (p, n), w in sorted(seen.items()):
    h = (n - 1) // 2
    T = math.log((p - 1) * n) + 12.0
    rng = random.Random(f"rt-fold-{p}-{n}")
    js = [1] + [rng.choice([j for j in range(2, n - 1)]) for _ in range(5)] if n > 5 else [1]
    for j in js:
        fe = np.zeros(n, dtype=np.int64); fo = np.zeros(n, dtype=np.int64)
        for k in range(1, n):
            x = j * k % n
            r = min(x, n - x)
            fe[k] = (p * r // n) % p
            fo[k] = (p * x // n) % p if x <= h else (p - 1 - (p * (n - x) // n)) % p
        be, ae, _ = driver.spectrum(fe, p, n)
        bo, ao, _ = driver.spectrum(fo, p, n)
        rows.append({"p": p, "n": n, "records": w, "h": h, "T": T, "j": j, "fold_max": be, "fold_above": ae,
                     "odd_max": bo, "odd_above": ao, "fold_ratio_to_h": be / h, "odd_ratio_to_h": bo / h})
def agg(sel):
    out = {}
    for key in ("fold", "odd"):
        rec_sp = sum(r["records"] for r in sel if r[f"{key}_above"] > 0)
        out[key] = {"cases": len(sel), "records_weighted": sum(r["records"] for r in sel), "records_weighted_spiking": rec_sp,
                    "median_X_over_h": float(np.median([r[f"{key}_ratio_to_h"] for r in sel]))}
    return out
pb = [r for r in rows if r["h"] > r["T"]]
res = {"j_eq_1_power_bearing": agg([r for r in pb if r["j"] == 1]),
       "j_random_power_bearing": agg([r for r in pb if r["j"] != 1]),
       "fold_random_j_spike_rate_by_n": {}, "rows": rows}
for lo, hi in ((43, 100), (100, 200), (200, 300), (300, 700)):
    s = [r for r in pb if r["j"] != 1 and lo <= r["n"] < hi]
    if s:
        res["fold_random_j_spike_rate_by_n"][f"{lo}-{hi}"] = {"cases": len(s), "spiking": sum(r["fold_above"] > 0 for r in s),
                                                             "odd_spiking": sum(r["odd_above"] > 0 for r in s)}
# minimum n at which a random-j fold leak spikes in every case
ok = sorted({r["n"] for r in pb if r["j"] != 1})
res["smallest_n_with_all_random_j_fold_spiking"] = next((n for n in ok if all(r["fold_above"] > 0 for r in pb if r["j"] != 1 and r["n"] >= n)), None)
res["power_bearing_records_with_n_ge_that"] = sum(r["records"] for r in pb if r["j"] == 1 and res["smallest_n_with_all_random_j_fold_spiking"] and r["n"] >= res["smallest_n_with_all_random_j_fold_spiking"])
json.dump(res, open(sys.argv[1], "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "rows"}, indent=1))
