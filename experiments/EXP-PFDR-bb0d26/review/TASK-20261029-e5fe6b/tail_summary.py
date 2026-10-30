#!/usr/bin/env python3
"""Descriptive tail statistics of the re-derived z values (TASK-20261029-e5fe6b, joint J4).

Reads cells.json (rederive.py) and ec_b20.json / ec_b24.json (ec_check.py) from this directory.
Reports: sd and mean of z and z_cal over powered valid cells, sum of z^2 against chi-square(k), counts of
|z| > 2 and > 3 against their N(0,1) expectations, cells whose bootstrap interval excludes 1, and for the
20- and 24-bit cells kappa and z against the exact uniform-subset expectation E_exact (no null noise:
z_exact = (S - sum E_exact) / sqrt(V)).
Usage: python3 -I tail_summary.py <dir> <out_json>
"""
import json
import math
import os
import sys

d = sys.argv[1]
cells = json.load(open(os.path.join(d, "cells.json")))["cells"]
ex = {}
for f in ("ec_b20.json", "ec_b24.json"):
    p = os.path.join(d, f)
    if os.path.exists(p):
        for c in json.load(open(p))["cells"]:
            ex[c["cell"]] = c


def chi2_sf(x, k):
    # regularized upper incomplete gamma Q(k/2, x/2) by series / continued fraction (no scipy)
    a, x2 = k / 2.0, x / 2.0
    if x2 < a + 1:
        s = term = 1.0 / a
        n = 1
        while abs(term) > 1e-15 * abs(s):
            term *= x2 / (a + n); s += term; n += 1
        return 1.0 - s * math.exp(-x2 + a * math.log(x2) - math.lgamma(a))
    b = x2 + 1 - a; c = 1e300; dd = 1 / b; h = dd
    for i in range(1, 500):
        an = -i * (i - a); b += 2
        dd = an * dd + b; dd = 1e-300 if abs(dd) < 1e-300 else dd
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        dd = 1 / dd; de = dd * c; h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x2 + a * math.log(x2) - math.lgamma(a)) * h


pw = [c for c in cells if c["cls"] != "invalid" and c.get("powered")]
k = len(pw)


def stats(vals):
    m = sum(vals) / len(vals)
    sd = math.sqrt(sum((v - m) ** 2 for v in vals) / len(vals))
    ss = sum(v * v for v in vals)
    return {"n": len(vals), "mean": m, "sd_pop": sd, "sum_sq": ss, "chi2_sf": chi2_sf(ss, len(vals)),
            "count_abs_gt_2": sum(1 for v in vals if abs(v) > 2), "expected_gt_2": len(vals) * 0.0455,
            "count_abs_gt_3": sum(1 for v in vals if abs(v) > 3), "expected_gt_3": len(vals) * 0.0027,
            "max_abs": max(map(abs, vals))}


out = {"z": stats([c["z"] for c in pw]), "z_cal": stats([c["z_cal"] for c in pw]),
       "plant_z_min": min(c["plant_z"] for c in pw)}
by_bits = {}
for b in (20, 24, 28):
    by_bits[b] = stats([c["z"] for c in pw if c["bits"] == b])
out["z_by_bits"] = by_bits
out["ci_excludes_1"] = [[c["cell"], c["kappa"], c["ci95"], c["z"]] for c in pw if c["ci95"][0] > 1 or c["ci95"][1] < 1]
out["cells_abs_z_gt_2"] = [[c["cell"], c["kappa"], c["z"]] for c in pw if abs(c["z"]) > 2]
rows = []
for c in pw:
    e = ex.get(c["cell"])
    if not e:
        continue
    E = e["sum_E_exact"]
    rows.append([c["cell"], c["S"] / E, (c["S"] - E) / math.sqrt(c["V"])])
out["kappa_vs_exact_b20_b24"] = rows
if rows:
    out["z_exact_stats"] = stats([r[2] for r in rows])
    out["max_abs_kappa_exact_minus_1"] = max(rows, key=lambda r: abs(r[1] - 1))
print(json.dumps({kk: vv for kk, vv in out.items() if kk != "kappa_vs_exact_b20_b24"}, indent=1))
with open(sys.argv[2], "w") as fh:
    json.dump(out, fh, separators=(",", ":"))
    fh.write("\n")
