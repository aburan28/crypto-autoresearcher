#!/usr/bin/env python3
"""Probe the one D=-3 non-DC elevation in rt_d3_output.json (RUN-CZLIFT-037e5f, p=439, n=151, y4,
non-DC max 17.72 vs matched-null mean 10.83): argmax (a, t), whether t sits on a symmetry frequency,
and its rank among 300 symmetry-matched null draws and 300 uniform-digit draws.
Usage: rt_d3_outlier.py OUT.json"""
import json, math, random, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt_d3 as R
BASE = R.BASE
e = next(x for x in json.load(open(R.REPLAY)) if x["run"] == "RUN-CZLIFT-037e5f" and x["p"] == 439 and x["n"] == 151)
p, n, K = 439, 151, R.K
M = p ** K
raw = json.load(open(f"{BASE}/runs/{e['run']}/raw-result.json"))["raw"]["curves"][e["index"]]
A, B = raw["A"] % M, raw["B"] % M
T1 = tuple(e["replay"]["T1"])
ys = [0, T1[1]]
cur = (T1[0], T1[1], 1)
for k in range(2, n):
    cur = R.rcb_add(cur, (T1[0], T1[1], 1), A, 3 * B % M, M)
    ys.append(R.affine(cur, M)[1])
h = (n - 1) // 2
def full(d):
    a = np.arange(1, p, dtype=np.int64)[:, None]
    z = np.zeros((p - 1, n), dtype=np.complex128)
    z[:, 1:h + 1] = np.exp(2j * np.pi * ((a * d[None, 1:h + 1]) % p) / p)
    return np.abs(np.fft.fft(z, axis=1)) ** 2 / h
d = np.array([0] + [R.digit(int(v), p, 4) for v in ys[1:]], dtype=np.int64)
X = full(d)
Xn = X[:, 1:]
ia, it = np.unravel_index(int(Xn.argmax()), Xn.shape)
a_star, t_star = int(ia) + 1, int(it) + 1
lam = next(l for l in range(2, n) if (l * l + l + 1) % n == 0)
sym = {"t*(1-lam) mod n": (t_star * (1 - lam)) % n, "t*(1+lam) mod n": (t_star * (1 + lam)) % n,
       "t*lam mod n": t_star * lam % n, "t*lam^2 mod n": t_star * lam * lam % n}
rng = random.Random("rt-d3-outlier")
orbit_of, reps = {}, []
for k in range(1, n):
    if k in orbit_of: continue
    reps.append(k)
    for s in (1, lam, lam * lam % n):
        orbit_of[s * k % n] = (k, 1); orbit_of[(-s * k) % n] = (k, -1)
mt, un = [], []
for _ in range(300):
    vals = {r: rng.randrange(M) for r in reps}
    dm = np.array([0] + [R.digit((orbit_of[k][1] * vals[orbit_of[k][0]]) % M, p, 4) for k in range(1, n)], dtype=np.int64)
    mt.append(float(full(dm)[:, 1:].max()))
    du = np.array([rng.randrange(p) for _ in range(n)], dtype=np.int64)
    un.append(float(full(du)[:, 1:].max()))
out = {"row": "RUN-CZLIFT-037e5f D=-3 p=439 n=151 y4", "T": math.log((p - 1) * n) + 12,
       "real_nondc_max": float(Xn.max()), "argmax_a": a_star, "argmax_t": t_star, "lambda": lam, "symmetry_images": sym,
       "values_at_symmetry_images_of_t": {str(t): float(X[a_star - 1, t]) for t in sorted({t_star * lam % n, t_star * lam * lam % n, (-t_star) % n})},
       "matched_null_nondc": {"draws": 300, "mean": float(np.mean(mt)), "p95": float(np.quantile(mt, 0.95)), "max": max(mt),
                              "frac_ge_real": sum(x >= float(Xn.max()) for x in mt) / 300},
       "uniform_nondc": {"draws": 300, "mean": float(np.mean(un)), "p95": float(np.quantile(un, 0.95)), "max": max(un),
                         "frac_ge_real": sum(x >= float(Xn.max()) for x in un) / 300},
       "rows_screened_for_this_max": 40}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps(out, indent=1))
