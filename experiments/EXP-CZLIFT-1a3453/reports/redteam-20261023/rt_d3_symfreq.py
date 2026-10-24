#!/usr/bin/env python3
"""Pooled follow-up of rt_d3_outlier.py, class fixed before looking at the other rows:
frequency class F = {t : t(1-lam) = +-1 or t(1-lam^2) = +-1 mod n} (the class of the outlier t = 39).
For each D=-3 power-bearing y-digit row (40 rows; the discovering row reported separately), the real
max over psi and t in F, and its rank among 100 symmetry-matched null draws (same F).
Usage: rt_d3_symfreq.py OUT.json"""
import json, math, random, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt_d3 as R
rng = random.Random("rt-d3-symfreq")
rows = []
for e in json.load(open(R.REPLAY)):
    if e["label"] != "D=-3":
        continue
    p, n = e["p"], e["n"]; h = (n - 1) // 2
    if h <= math.log((p - 1) * n) + 12:
        continue
    M = p ** R.K
    raw = json.load(open(f"{R.BASE}/runs/{e['run']}/raw-result.json"))["raw"]["curves"][e["index"]]
    A, B = raw["A"] % M, raw["B"] % M
    T1 = tuple(e["replay"]["T1"])
    ys = [0, T1[1]]; cur = (T1[0], T1[1], 1)
    for k in range(2, n):
        cur = R.rcb_add(cur, (T1[0], T1[1], 1), A, 3 * B % M, M); ys.append(R.affine(cur, M)[1])
    lam = next(l for l in range(2, n) if (l * l + l + 1) % n == 0)
    F = sorted({t for t in range(1, n) if (t * (1 - lam)) % n in (1, n - 1) or (t * (1 - lam * lam)) % n in (1, n - 1)})
    orbit_of, reps = {}, []
    for k in range(1, n):
        if k in orbit_of: continue
        reps.append(k)
        for s in (1, lam, lam * lam % n):
            orbit_of[s * k % n] = (k, 1); orbit_of[(-s * k) % n] = (k, -1)
    def statF(d):
        a = np.arange(1, p, dtype=np.int64)[:, None]
        z = np.zeros((p - 1, n), dtype=np.complex128)
        z[:, 1:h + 1] = np.exp(2j * np.pi * ((a * d[None, 1:h + 1]) % p) / p)
        X = np.abs(np.fft.fft(z, axis=1)) ** 2 / h
        return float(X[:, F].max())
    for i in (1, 2, 3, 4):
        d = np.array([0] + [R.digit(int(v), p, i) for v in ys[1:]], dtype=np.int64)
        real = statF(d)
        null = []
        for _ in range(100):
            vals = {r: rng.randrange(M) for r in reps}
            dm = np.array([0] + [R.digit((orbit_of[k][1] * vals[orbit_of[k][0]]) % M, p, i) for k in range(1, n)], dtype=np.int64)
            null.append(statF(dm))
        rank = (1 + sum(x >= real for x in null)) / 101
        rows.append({"run": e["run"], "p": p, "n": n, "digit": f"y{i}", "F": F, "real": real,
                     "null_mean": float(np.mean(null)), "rank": rank,
                     "discovering_row": (p, n, i) == (439, 151, 4) and e["run"] == "RUN-CZLIFT-037e5f"})
others = [r for r in rows if not r["discovering_row"]]
fisher = -2 * sum(math.log(r["rank"]) for r in others)
out = {"class": "t(1-lam) = +-1 or t(1-lam^2) = +-1 mod n", "rows": rows,
       "others": {"rows": len(others), "mean_rank": float(np.mean([r["rank"] for r in others])),
                  "ranks_below_0.05": sum(r["rank"] < 0.05 for r in others),
                  "fisher_chi2": fisher, "fisher_dof": 2 * len(others),
                  "note": "under the matched null ranks ~ U(0,1) (discretised to 1/101); chi2 mean = dof"},
       "discovering_row": [r for r in rows if r["discovering_row"]]}
json.dump(out, open(sys.argv[1], "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))
