"""EXP-CZLIFT-ed8113 driver: the xedni dependence rate as a measurement.

For each prime p and r in {2, 3}: draw r random points P_i of E(F_p) on a
random curve y^2 = x^3 + a x + b, lift their coordinates to the symmetric
integer representatives (X_i, Y_i) in (-p/2, p/2], and solve for the lifted
curve through them. For r = 2 the short model Y^2 = X^3 + A X + B is
determined (two linear equations in A, B over Q); for r = 3 the model
Y^2 = X^3 + A2 X^2 + A X + B is determined. The lifted curve reduces to E mod
p whenever the linear system is nonsingular mod p (checked). Then search
EXACTLY, by rational-point arithmetic on the lifted curve, for a relation
sum m_i P~_i = O with 0 < max |m_i| <= B (B = RELATION_BOUND), i.e. the
dependence an xedni attack would turn into a relation mod p. Record the
dependence rate, the naive heights of the lifted points (against log p), and
the height of the lifted curve's discriminant. An instrument control plants
P~_2 = [2] P~_1 on a lifted curve and must be detected. Observations only.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from fractions import Fraction

import sympy

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from harness import czlift  # noqa: E402
from harness.czlift_run import write_run_record  # noqa: E402
from harness.toycurve import EllipticCurve  # noqa: E402

EXP_ID = "EXP-CZLIFT-ed8113"
RELATION_BOUND = 6
PRIMES = (101, 211, 401, 809, 1601, 3203, 6421, 12809)


def sym(v: int, p: int) -> int:
    v %= p
    return v - p if v > p // 2 else v


# -- exact arithmetic on Y^2 = X^3 + A2 X^2 + A4 X + A6 over Q -----------------

def q_add(P, Q, A2, A4):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0:
            return None
        lam = (3 * x1 * x1 + 2 * A2 * x1 + A4) / (2 * y1)
    else:
        lam = (y2 - y1) / (x2 - x1)
    x3 = lam * lam - A2 - x1 - x2
    y3 = lam * (x1 - x3) - y1
    return (x3, y3)


def q_neg(P):
    return None if P is None else (P[0], -P[1])


def q_mul(m, P, A2, A4):
    if m < 0:
        return q_mul(-m, q_neg(P), A2, A4)
    R = None
    A = P
    while m:
        if m & 1:
            R = q_add(R, A, A2, A4)
        m >>= 1
        if m:
            A = q_add(A, A, A2, A4)
    return R


def naive_log_height(x: Fraction) -> float:
    return math.log(max(abs(x.numerator), abs(x.denominator), 1))


def lift_curve(points, p):
    """(A2, A4, A6) over Q through the integer lifts; None if singular mod p."""
    r = len(points)
    if r == 2:
        (X1, Y1), (X2, Y2) = points
        det = X1 - X2
        if det % p == 0:
            return None
        A4 = Fraction((Y1 * Y1 - X1 ** 3) - (Y2 * Y2 - X2 ** 3), det)
        A6 = Fraction(Y1 * Y1 - X1 ** 3) - A4 * X1
        return (Fraction(0), A4, A6)
    if r == 3:
        rows = [[Fraction(X * X), Fraction(X), Fraction(1), Fraction(Y * Y - X ** 3)] for X, Y in points]
        M = sympy.Matrix([[int(X * X), int(X), 1] for X, Y in points])
        if int(M.det()) % p == 0:
            return None
        sol = sympy.Matrix([[sympy.Rational(c) for c in row[:3]] for row in rows]).solve(
            sympy.Matrix([sympy.Rational(row[3]) for row in rows]))
        return tuple(Fraction(int(v.p), int(v.q)) for v in sol)
    raise ValueError(r)


def dependent(lifted, A2, A4, bound):
    """Smallest relation (by max |m|) with 0 < max|m_i| <= bound, or None."""
    r = len(lifted)
    multiples = []
    for P in lifted:
        table = {0: None}
        for m in range(1, bound + 1):
            table[m] = q_mul(m, P, A2, A4)
            table[-m] = q_neg(table[m])
        multiples.append(table)
    rng = range(-bound, bound + 1)
    best = None
    import itertools
    for ms in itertools.product(rng, repeat=r):
        if all(m == 0 for m in ms):
            continue
        if best is not None and max(abs(m) for m in ms) >= best[0]:
            continue
        S = None
        for P_table, m in zip(multiples, ms):
            S = q_add(S, P_table[m], A2, A4)
        if S is None:
            best = (max(abs(m) for m in ms), list(ms))
    return None if best is None else best[1]


def trial(p, a, b, r, rng):
    Efp = EllipticCurve(p, a, b)
    pts = []
    while len(pts) < r:
        P = czlift.random_point(Efp, rng)
        if all(P[0] != Q[0] for Q in pts):
            pts.append(P)
    lifts = [(sym(P[0], p), sym(P[1], p)) for P in pts]
    model = lift_curve(lifts, p)
    if model is None:
        return {"singular_mod_p": True}
    A2, A4, A6 = model
    for (X, Y) in lifts:
        assert Fraction(Y * Y) == X ** 3 + A2 * X * X + A4 * X + A6
    disc_num = (-16 * (4 * A4 ** 3 + 27 * A6 ** 2)) if r == 2 else None
    lifted = [(Fraction(X), Fraction(Y)) for X, Y in lifts]
    rel = dependent(lifted, A2, A4, RELATION_BOUND)
    return {"singular_mod_p": False, "relation": rel,
            "log_height_points": [naive_log_height(Fraction(X)) for X, _ in lifts],
            "log_p": math.log(p),
            "log_height_A4": naive_log_height(A4), "log_height_A6": naive_log_height(A6),
            "log_height_disc": (naive_log_height(disc_num) if disc_num is not None else None)}


def planted_control(p, rng):
    """Lift P, set P~_2 = [2]P~_1 on the lifted curve through P~_1; must be detected."""
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p:
            break
    Efp = EllipticCurve(p, a, b)
    P = czlift.random_point(Efp, rng)
    X1, Y1 = sym(P[0], p), sym(P[1], p)
    A4 = Fraction(a + p * rng.randrange(1, 5))
    A6 = Fraction(Y1 * Y1 - X1 ** 3) - A4 * X1
    P1 = (Fraction(X1), Fraction(Y1))
    P2 = q_mul(2, P1, Fraction(0), A4)
    rel = dependent([P1, P2], Fraction(0), A4, RELATION_BOUND)
    return rel == [2, -1] or rel == [-2, 1]


def build(seed: int, trials_per_cell: int, primes) -> tuple[dict, dict]:
    rng = random.Random(seed)
    cells = []
    for p in primes:
        for r in (2, 3):
            rows = []
            for _ in range(trials_per_cell):
                while True:
                    a, b = rng.randrange(p), rng.randrange(p)
                    if (4 * a ** 3 + 27 * b * b) % p:
                        break
                rows.append(trial(p, a, b, r, rng))
            valid = [x for x in rows if not x["singular_mod_p"]]
            dep = [x for x in valid if x["relation"] is not None]
            cells.append({"p": p, "r": r, "trials": len(rows), "valid": len(valid),
                          "dependent": len(dep), "dependence_rate": len(dep) / len(valid) if valid else None,
                          "relations": [x["relation"] for x in dep],
                          "mean_log_height_point": (sum(h for x in valid for h in x["log_height_points"]) / (r * len(valid))) if valid else None,
                          "mean_log_height_A4": (sum(x["log_height_A4"] for x in valid) / len(valid)) if valid else None,
                          "log_p": math.log(p)})
    controls = [planted_control(p, rng) for p in primes for _ in range(3)]
    metrics = {
        "cells": len(cells),
        "valid_trials_total": sum(c["valid"] for c in cells),
        "dependent_total": sum(c["dependent"] for c in cells),
        "dependence_rate_overall": (sum(c["dependent"] for c in cells) / sum(c["valid"] for c in cells)),
        "dependence_rate_by_r": {str(r): (sum(c["dependent"] for c in cells if c["r"] == r)
                                          / max(1, sum(c["valid"] for c in cells if c["r"] == r))) for r in (2, 3)},
        "control_detection_rate": sum(controls) / len(controls),
        "controls": len(controls),
        "height_ratio_point_over_log_p": {str(c["p"]): round(c["mean_log_height_point"] / c["log_p"], 4) for c in cells if c["r"] == 2 and c["mean_log_height_point"]},
        "relation_bound": RELATION_BOUND, "seed": seed, "primes": list(primes),
    }
    return metrics, {"cells": cells, "controls": controls}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--trials-per-cell", type=int, default=100)
    ap.add_argument("--pmax", type=int, default=20000)
    args = ap.parse_args(argv)
    primes = [p for p in PRIMES if p <= args.pmax]
    t0 = time.time()
    metrics, raw = build(args.seed, args.trials_per_cell, primes)
    t1 = time.time()
    sources = [os.path.abspath(__file__), os.path.join(REPO, "harness", "czlift.py"),
               os.path.join(REPO, "harness", "czlift_run.py"), os.path.join(REPO, "harness", "toycurve.py")]
    write_run_record(args.run_dir, run_id=args.run_id, exp_id=EXP_ID, status="completed_valid",
                     command=[sys.executable] + sys.argv, sources=sources, seed=args.seed,
                     parameters={"trials_per_cell": args.trials_per_cell, "pmax": args.pmax,
                                 "relation_bound": RELATION_BOUND, "tier": "toy"},
                     metrics=metrics, raw=raw, started=t0, finished=t1,
                     stdout=json.dumps(metrics, indent=1) + "\n")
    print(json.dumps(metrics))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
