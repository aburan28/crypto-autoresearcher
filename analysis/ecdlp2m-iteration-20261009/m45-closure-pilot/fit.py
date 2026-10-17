#!/usr/bin/env python3
"""fit.py -- log2(wall) vs N for the M4RI W_4 closure on UNSAT S3 instances, per m
(OLS on per-cell medians, and OLS on per-instance rows; CI from the t distribution
with n-2 dof, computed without scipy via a small table / normal approx for dof>=30)."""
import glob, json, math, os, statistics
from collections import defaultdict
HERE = os.path.dirname(os.path.abspath(__file__))
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        12: 2.179, 15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042}
def t975(df):
    if df in T975: return T975[df]
    ks = sorted(T975); 
    for a, b in zip(ks, ks[1:]):
        if a < df < b: return T975[a] + (T975[b] - T975[a]) * (df - a) / (b - a)
    return 1.96
def ols(xs, ys):
    n = len(xs); mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx; a = my - b * mx
    if n > 2:
        se = math.sqrt(sum((y - a - b * x) ** 2 for x, y in zip(xs, ys)) / (n - 2) / sxx); ci = t975(n - 2) * se
    else:
        se = ci = float("nan")
    return a, b, ci
rows = []
for f in glob.glob(os.path.join(HERE, "results", "*.jsonl")):
    for l in open(f):
        r = json.loads(l); r.setdefault("m", 3); rows.append(r)
# pilot #1 m=3 W4 rows as a comparison series
for f in glob.glob(os.path.join(HERE, "results_pilot1", "n*-poly.jsonl")):
    for l in open(f):
        r = json.loads(l); r["m"] = 3; r["pilot1"] = True; rows.append(r)
out = ["| m | D | cells (N: median wall s, n) | slope of log2(wall) vs N on medians [95% CI] | slope on per-instance rows [95% CI] | doubling every ... variables |", "|---|---|---|---|---|---|"]
for D in (3, 4):
    for m in (3, 4, 5):
        sel = [r for r in rows if r["m"] == m and r["family"] == "S3" and r["nsol"] == 0 and r["kind"] == "W" and r["D"] == D
               and r.get("status") == "completed" and r.get("contains_one")]
        if not sel: continue
        byN = defaultdict(list)
        for r in sel: byN[r["N"]].append(math.log2(max(r["wall_s"], 1e-3)))
        if len(byN) < 2: 
            out.append(f"| {m}{' (pilot 1)' if m == 3 else ''} | {D} | " + ", ".join(f"{N}: {2**statistics.median(v):.1f}, {len(v)}" for N, v in sorted(byN.items())) + " | (one size) | | |"); continue
        xs = sorted(byN); ys = [statistics.median(byN[N]) for N in xs]
        a, b, ci = ols(xs, ys)
        xi = [r["N"] for r in sel]; yi = [math.log2(max(r["wall_s"], 1e-3)) for r in sel]
        a2, b2, ci2 = ols(xi, yi)
        out.append(f"| {m}{' (pilot 1)' if m == 3 else ''} | {D} | " + ", ".join(f"{N}: {2**statistics.median(byN[N]):.1f}, {len(byN[N])}" for N in xs)
                   + f" | {b:.2f} [{b-ci:.2f},{b+ci:.2f}] (k={len(xs)}) | {b2:.2f} [{b2-ci2:.2f},{b2+ci2:.2f}] (n={len(xi)}) | {1/b:.1f} |")
print("\n".join(out))
