"""EXP-CZLIFT-8c50ea driver: small points of E(K), K = Q(2^{1/3}), versus E(F_p) coverage.

The degree-3 SNFS-type field replaces the quadratic stand-in of
EXP-CZLIFT-a255fc. For each ladder curve enumerate every K-point with
x = alpha / d^2, alpha in Z[theta] with coordinates in [-H, H], d <= dmax
(harness/czlift_cubic.py: exact square test in Z[theta] through the three
embeddings), count N_K(H) and its rational part N_Q(H), fit the growth slope
of log N_K against log log H on a height grid, and at primes p = 1 mod 3 with
2 a cube (where theta reduces to F_p) measure the distinct residues of those
points in E(F_p) against the uniform model N_p (1 - (1 - 1/N_p)^N).
Observations only.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import sympy

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import czlift_cubic as C  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402

EXP_ID = "EXP-CZLIFT-8c50ea"
CURVES = [("11a1", [0, -1, 1, -10, -20], 0), ("37a1", [0, 0, 1, -1, 0], 1), ("389a1", [0, 1, 1, -2, 0], 2),
          ("5077a1", [0, 0, 1, -7, 6], 3), ("234446a1", [1, -1, 0, -79, 289], 4), ("19047851a1", [0, 0, 1, -79, 342], 5)]
H_GRID = [2, 4, 8, 12, 16, 24, 32]


def disc(ai):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2; b4 = 2 * a4 + a1 * a3; b6 = a3 * a3 + 4 * a6; b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    return -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6


def order_mod_p(ai, p):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2; b4 = 2 * a4 + a1 * a3; b6 = a3 * a3 + 4 * a6
    total = 1
    for x in range(p):
        g = (4 * x ** 3 + b2 * x * x + 2 * b4 * x + b6) % p
        total += 1 if g == 0 else (2 if pow(g, (p - 1) // 2, p) == 1 else 0)
    return total


def split_primes(pmin, pmax, count):
    out = []
    for p in sympy.primerange(pmin, pmax):
        if p % 3 == 1 and pow(2, (p - 1) // 3, p) == 1:
            out.append(p)
    step = max(1, len(out) // count)
    return out[::step][:count]


def fit_slope(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    return None if sxx == 0 else sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def measure_curve(label, ai, rank, *, hmax, dmax, primes):
    pts = C.search_points(ai, hmax, dmax)
    grid = [H for H in H_GRID if H <= hmax]
    counts = {H: 1 + sum(1 for q in pts if C.height(q) <= H) for H in grid}
    counts_q = {H: 1 + sum(1 for q in pts if C.height(q) <= H and q[0][1] == 0 and q[0][2] == 0) for H in grid}
    xs = [math.log(math.log(H)) for H in grid if H >= 4 and counts[H] >= 3]
    ys = [math.log(counts[H]) for H in grid if H >= 4 and counts[H] >= 3]
    good = [p for p in primes if (6 * disc(ai)) % p]
    coverage = []
    for p in good:
        N_p = order_mod_p(ai, p)
        root = C.cube_roots_of_2(p)[0]
        for H in grid:
            sub = [q for q in pts if C.height(q) <= H]
            hit = {C.reduce_point(ai, q, p, root) for q in sub} | {"O"}
            n_pts = len(sub) + 1
            model = N_p * (1 - (1 - 1 / N_p) ** n_pts)
            coverage.append({"p": p, "H": H, "N_p": N_p, "n_points": n_pts, "distinct": len(hit), "model_distinct": model,
                             "ratio_to_model": len(hit) / model})
    return {"label": label, "ainvs": ai, "rank_recalled_over_Q": rank, "hmax": hmax, "dmax": dmax,
            "counts_K": {str(H): counts[H] for H in grid}, "counts_Q": {str(H): counts_q[H] for H in grid},
            "growth_slope_K": fit_slope(xs, ys), "primes": good, "coverage": coverage,
            "points_sample": [[list(q[0]), q[1], list(q[2])] for q in sorted(pts, key=C.height)[:10]]}


def summarize(curves):
    cells = [c for cv in curves for c in cv["coverage"] if c["n_points"] >= 20 and c["model_distinct"] <= 0.9 * c["N_p"]]
    ratios = sorted(c["ratio_to_model"] for c in cells)
    return {"coverage_cells": len(cells), "coverage_ratio_median": ratios[len(ratios) // 2] if ratios else None,
            "coverage_ratio_frac_above_1p5": (sum(1 for r in ratios if r > 1.5) / len(ratios)) if ratios else None,
            "coverage_ratio_frac_below_0p5": (sum(1 for r in ratios if r < 0.5) / len(ratios)) if ratios else None,
            "growth": {cv["label"]: {"slope_K": cv["growth_slope_K"], "N_K_at_hmax": cv["counts_K"][str(cv["hmax"])],
                                     "N_Q_at_hmax": cv["counts_Q"][str(cv["hmax"])], "rank_Q_recalled": cv["rank_recalled_over_Q"]} for cv in curves},
            "cubic_gain_median": sorted(cv["counts_K"][str(cv["hmax"])] / max(1, cv["counts_Q"][str(cv["hmax"])]) for cv in curves)[len(curves) // 2]}


def build(hmax, dmax, n_primes):
    primes = split_primes(101, 5000, n_primes)
    curves = [measure_curve(l, ai, r, hmax=hmax, dmax=dmax, primes=primes) for l, ai, r in CURVES]
    m = summarize(curves); m.update({"hmax": hmax, "dmax": dmax, "n_primes": len(primes)})
    return m, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True); ap.add_argument("--run-id", required=True)
    ap.add_argument("--hmax", type=int, default=32); ap.add_argument("--dmax", type=int, default=4); ap.add_argument("--n-primes", type=int, default=12)
    a = ap.parse_args(argv)
    t0 = time.time(); m, raw = build(a.hmax, a.dmax, a.n_primes); t1 = time.time()
    write_run_record(a.run_dir, run_id=a.run_id, exp_id=EXP_ID, status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=[os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift_cubic.py"), os.path.join(REPO, "harness", "czlift_run.py")],
                     seed=None, parameters={"hmax": a.hmax, "dmax": a.dmax, "n_primes": a.n_primes, "field": "Q(2^(1/3))", "tier": "toy", "deterministic": True},
                     metrics=m, raw=raw, started=t0, finished=t1, curve_id="rank-ladder-over-Q(cuberoot2)", stdout=json.dumps(m, indent=1) + "\n")
    print(json.dumps({k: v for k, v in m.items() if k != "growth"})); print(json.dumps(m["growth"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
