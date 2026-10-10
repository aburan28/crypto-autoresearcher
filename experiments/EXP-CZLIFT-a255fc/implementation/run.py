"""EXP-CZLIFT-a255fc driver: small rational points versus E(F_p) coverage.

For eight curves E/Q of (literature-recalled) rank 0..7, enumerate EVERY
rational point of naive height H(x) = max(|a|, d^2) <= H_max (x = a/d^2), by a
vectorized quadratic-residue sieve followed by an exact square test, and
measure

  N_E(H)          the number of rational points of height <= H on a grid of H;
  growth slope    of log N_E(H) against log log H (Neron: N ~ c (log H)^{r/2});
  coverage(H, p)  the fraction of E(F_p) hit by the reductions of those points,
                  against the uniform-reduction model N_p (1 - (1 - 1/N_p)^N);
  H_half(p)       the smallest grid height whose points cover half of E(F_p);
  twist gain      for K = Q(sqrt(D)): the K-points of height <= H are, up to
                  finite index, E(Q) + E^D(Q); the extra coverage of E(F_p)
                  at primes where D is a square is measured against the same
                  model with N_E + N_{E^D} points.

Observations only; the driver decides nothing. Rank labels are recalled from
the standard minimal-conductor tables and are NOT verified here; the growth
slope is the internal consistency check on them.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")
import numpy as np  # noqa: E402
import sympy

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness.czlift_run import write_run_record  # noqa: E402

EXP_ID = "EXP-CZLIFT-a255fc"

# (label, [a1, a2, a3, a4, a6], rank_recalled, conductor_recalled)
CURVES = [
    ("11a1", [0, -1, 1, -10, -20], 0, 11),
    ("37a1", [0, 0, 1, -1, 0], 1, 37),
    ("389a1", [0, 1, 1, -2, 0], 2, 389),
    ("5077a1", [0, 0, 1, -7, 6], 3, 5077),
    ("234446a1", [1, -1, 0, -79, 289], 4, 234446),
    ("19047851a1", [0, 0, 1, -79, 342], 5, 19047851),
    ("5187563742a1", [1, 1, 0, -2582, 48720], 6, 5187563742),
    ("382623908456a1", [0, 0, 0, -10012, 346900], 7, 382623908456),
]
H_GRID = [10, 30, 100, 300, 1000, 3000, 10_000, 30_000, 100_000, 300_000, 1_000_000]
TWIST_D = [-1, 2, -3, 5, -7, 13]
SIEVE_MODULI = (64, 63, 65, 11, 17, 19, 23)


def b_invariants(ai):
    a1, a2, a3, a4, a6 = ai
    b2 = a1 * a1 + 4 * a2
    b4 = 2 * a4 + a1 * a3
    b6 = a3 * a3 + 4 * a6
    b8 = a1 * a1 * a6 + 4 * a2 * a6 - a1 * a3 * a4 + a2 * a3 * a3 - a4 * a4
    disc = -b2 * b2 * b8 - 8 * b4 ** 3 - 27 * b6 * b6 + 9 * b2 * b4 * b6
    return b2, b4, b6, disc


def g_exact(a: int, d: int, b2: int, b4: int, b6: int) -> int:
    return 4 * a ** 3 + b2 * a * a * d * d + 2 * b4 * a * d ** 4 + b6 * d ** 6


def square_tables(D: int):
    """Residues r mod m with r = D * s^2 mod m for some s."""
    tabs = []
    for m in SIEVE_MODULI:
        ok = np.zeros(m, dtype=bool)
        for s in range(m):
            ok[(D * s * s) % m] = True
        tabs.append((m, ok))
    return tabs


def search_points(ai, H: int, D: int = 1):
    """All (a, d, c) with D c^2 = g(a, d), gcd(a, d) = 1, max(|a|, d^2) <= H."""
    b2, b4, b6, _ = b_invariants(ai)
    tabs = square_tables(D)
    points = []
    a_all = np.arange(-H, H + 1, dtype=np.int64)
    dmax = math.isqrt(H)
    for d in range(1, dmax + 1):
        mask = np.ones(a_all.shape, dtype=bool)
        for m, ok in tabs:
            am = a_all % m
            dm = d % m
            g = (4 * am ** 3 + (b2 % m) * am * am * dm * dm
                 + (2 * b4 % m) * am * (dm ** 4 % m) + (b6 % m) * (dm ** 6 % m)) % m
            mask &= ok[g]
            if not mask.any():
                break
        if not mask.any():
            continue
        cand = a_all[mask]
        cand = cand[np.gcd(np.abs(cand), d) == 1]
        for a in cand.tolist():
            g = g_exact(a, d, b2, b4, b6)
            if g % D:
                continue
            q = g // D
            if q < 0:
                continue
            c = math.isqrt(q)
            if c * c != q:
                continue
            points.append((a, d, c))
            if c:
                points.append((a, d, -c))
    return points


def height(pt) -> int:
    a, d, _ = pt
    return max(abs(a), d * d)


def curve_order_mod_p(ai, p: int) -> int:
    b2, b4, b6, _ = b_invariants(ai)
    total = 1
    for x in range(p):
        g = (4 * x ** 3 + b2 * x * x + 2 * b4 * x + b6) % p
        if g == 0:
            total += 1
        elif pow(g, (p - 1) // 2, p) == 1:
            total += 2
    return total


def reduce_points(ai, points, p: int, D: int = 1):
    """Set of residues in E(F_p) ('O' or (x, y)) hit by the points (twist by D)."""
    a1, a2, a3, a4, a6 = ai
    sD = 1
    if D != 1:
        sD = sympy.sqrt_mod(D % p, p)
        if sD is None:
            return None
    inv2 = pow(2, -1, p)
    out = set()
    for a, d, c in points:
        if d % p == 0:
            out.add("O")
            continue
        di = pow(d % p, -1, p)
        x = a * di * di % p
        Y = sD * c * di * di * di % p
        y = (Y - a1 * x - a3) * inv2 % p
        out.add((x, y))
    return out


def model_distinct(N_p: int, n_pts: int) -> float:
    return N_p * (1 - (1 - 1 / N_p) ** n_pts)


def primes_for_coverage(pmin: int, pmax: int, count: int):
    out = []
    x = pmin
    ratio = (pmax / pmin) ** (1 / (count - 1))
    for _ in range(count):
        out.append(int(sympy.nextprime(int(x))))
        x *= ratio
    return sorted(set(out))


def fit_slope(xs, ys):
    if len(xs) < 2:
        return None
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx


def measure_curve(label, ai, rank, conductor, *, hmax: int, primes, twists, twist_hmax: int) -> dict:
    b2, b4, b6, disc = b_invariants(ai)
    pts = search_points(ai, hmax)
    grid = [H for H in H_GRID if H <= hmax]
    counts = {H: 1 + sum(1 for q in pts if height(q) <= H) for H in grid}  # +1 for O
    xs = [math.log(math.log(H)) for H in grid if H >= 100 and counts[H] >= 3]
    ys = [math.log(counts[H]) for H in grid if H >= 100 and counts[H] >= 3]
    slope = fit_slope(xs, ys)
    good_primes = [p for p in primes if (6 * disc) % p != 0]
    coverage = []
    h_half = {}
    for p in good_primes:
        N_p = curve_order_mod_p(ai, p)
        for H in grid:
            sub = [q for q in pts if height(q) <= H]
            hit = reduce_points(ai, sub, p)
            hit.add("O")
            n_pts = len(sub) + 1
            expected = model_distinct(N_p, n_pts)
            coverage.append({"p": p, "H": H, "N_p": N_p, "n_points": n_pts,
                             "distinct": len(hit), "model_distinct": expected,
                             "coverage": len(hit) / N_p,
                             "ratio_to_model": len(hit) / expected})
            if p not in h_half and len(hit) / N_p >= 0.5:
                h_half[p] = H
    twist_rows = []
    for D in twists:
        tp = search_points(ai, twist_hmax, D)
        n_twist = 1 + sum(1 for q in tp if height(q) <= twist_hmax)
        base = [q for q in pts if height(q) <= twist_hmax]
        for p in good_primes:
            if p == abs(D) or sympy.legendre_symbol(D % p, p) != 1:
                continue
            N_p = curve_order_mod_p(ai, p)
            hit_base = reduce_points(ai, base, p)
            hit_base.add("O")
            hit_tw = reduce_points(ai, tp, p, D)
            hit_tw.add("O")
            union = hit_base | hit_tw
            n_union_pts = len(base) + 1 + n_twist
            twist_rows.append({"D": D, "p": p, "N_p": N_p, "H": twist_hmax,
                               "n_base_points": len(base) + 1, "n_twist_points": n_twist,
                               "distinct_base": len(hit_base), "distinct_twist": len(hit_tw),
                               "distinct_union": len(union),
                               "model_union": model_distinct(N_p, n_union_pts),
                               "ratio_union_to_model": len(union) / model_distinct(N_p, n_union_pts),
                               "gain_over_base": len(union) / len(hit_base)})
    return {"label": label, "ainvs": ai, "rank_recalled": rank, "conductor_recalled": conductor,
            "discriminant": disc, "hmax": hmax, "counts": {str(H): counts[H] for H in grid},
            "growth_slope": slope, "growth_slope_predicted": rank / 2,
            "primes": good_primes, "coverage": coverage,
            "h_half": {str(p): h for p, h in h_half.items()},
            "twists": twist_rows,
            "points_sample": [list(q) for q in sorted(pts, key=height)[:12]]}


def summarize(curves: list[dict]) -> dict:
    cells = [c for cv in curves for c in cv["coverage"]
             if c["n_points"] >= 30 and c["model_distinct"] <= 0.9 * c["N_p"]]
    ratios = sorted(c["ratio_to_model"] for c in cells)
    med = ratios[len(ratios) // 2] if ratios else None
    frac_excess = (sum(1 for r in ratios if r > 1.5) / len(ratios)) if ratios else None
    frac_deficit = (sum(1 for r in ratios if r < 0.5) / len(ratios)) if ratios else None
    slopes = {cv["label"]: {"measured": cv["growth_slope"], "predicted": cv["growth_slope_predicted"],
                            "rank_recalled": cv["rank_recalled"]} for cv in curves}
    # H_half scaling: log log H_half vs log p, per curve with >= 3 resolved primes
    hh = {}
    for cv in curves:
        pts = [(math.log(int(p)), math.log(math.log(h))) for p, h in cv["h_half"].items() if h >= 10]
        if len(pts) >= 3:
            s = fit_slope([a for a, _ in pts], [b for _, b in pts])
            r = cv["rank_recalled"]
            hh[cv["label"]] = {"slope": s, "predicted_2_over_r": (2 / r) if r else None,
                               "resolved_primes": len(pts)}
    tw = [t for cv in curves for t in cv["twists"] if t["n_base_points"] + t["n_twist_points"] >= 30
          and t["model_union"] <= 0.9 * t["N_p"]]
    tw_ratios = sorted(t["ratio_union_to_model"] for t in tw)
    return {
        "coverage_cells": len(cells),
        "coverage_ratio_median": med,
        "coverage_ratio_frac_above_1p5": frac_excess,
        "coverage_ratio_frac_below_0p5": frac_deficit,
        "growth_slopes": slopes,
        "h_half_scaling": hh,
        "twist_cells": len(tw),
        "twist_union_ratio_median": tw_ratios[len(tw_ratios) // 2] if tw_ratios else None,
        "twist_union_ratio_frac_above_1p5": (sum(1 for r in tw_ratios if r > 1.5) / len(tw_ratios)) if tw_ratios else None,
    }


def build(hmax: int, twist_hmax: int, twist_curves: int, n_primes: int) -> tuple[dict, dict]:
    primes = primes_for_coverage(101, 20_000, n_primes)
    curves = []
    for idx, (label, ai, rank, cond) in enumerate(CURVES):
        tw = TWIST_D if idx < twist_curves else []
        curves.append(measure_curve(label, ai, rank, cond, hmax=hmax, primes=primes,
                                    twists=tw, twist_hmax=min(twist_hmax, hmax)))
    metrics = summarize(curves)
    metrics.update({"hmax": hmax, "twist_hmax": min(twist_hmax, hmax), "n_primes": len(primes),
                    "twist_curves": twist_curves})
    return metrics, {"curves": curves}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--hmax", type=int, default=100_000)
    ap.add_argument("--twist-hmax", type=int, default=30_000)
    ap.add_argument("--twist-curves", type=int, default=4)
    ap.add_argument("--n-primes", type=int, default=16)
    args = ap.parse_args(argv)
    t0 = time.time()
    metrics, raw = build(args.hmax, args.twist_hmax, args.twist_curves, args.n_primes)
    t1 = time.time()
    sources = [os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift_run.py")]
    write_run_record(args.run_dir, run_id=args.run_id, exp_id=EXP_ID,
                     status="completed_valid", command=[sys.executable] + sys.argv,
                     sources=sources, seed=None,
                     parameters={"hmax": args.hmax, "twist_hmax": args.twist_hmax,
                                 "twist_curves": args.twist_curves, "n_primes": args.n_primes,
                                 "tier": "toy", "deterministic": True},
                     metrics=metrics, raw=raw, started=t0, finished=t1,
                     curve_id="rank-ladder-11a1..382623908456a1",
                     stdout=json.dumps(metrics, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("growth_slopes", "h_half_scaling")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
