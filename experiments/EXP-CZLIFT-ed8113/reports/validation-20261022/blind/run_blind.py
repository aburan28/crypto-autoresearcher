"""Phase-1 blind driver (validator TASK-20261022-67902e).

Computes, from the statement only:
  1. planted controls P~_2 = [2] P~_1 at every frozen prime (three constructions),
  2. PTM-1: the 389a1 generators in three models (must give no relation),
  3. an instrument positive check on a known torsion point (11a1),
  4. a blind sampler of the statement (own RNG, own seed) giving the expected count
     and type of accidental relations per (p, r) cell.
Usage: python3 run_blind.py OUT.json [--trials N] [--seed S]
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import relsearch as rs  # noqa: E402

PRIMES = [101, 211, 401, 809, 1601, 3203, 6421, 12809]
BOUND = 6


def pt(P):
    return None if P is None else [str(P[0]), str(P[1])]


def curve_str(E):
    return [str(a) for a in E.ainvs()]


def random_curve(rng, p):
    while True:
        a, b = rng.randrange(p), rng.randrange(p)
        if (4 * a ** 3 + 27 * b ** 2) % p:
            return a, b


def random_points(rng, pts, r, need_nonzero_y_first=False):
    while True:
        chosen = [rng.choice(pts) for _ in range(r)]
        if len({x for x, _ in chosen}) < r:
            continue
        if need_nonzero_y_first and chosen[0][1] == 0:
            continue
        return chosen


def torsion_order_upto12(E, P):
    Q = None
    for k in range(1, 13):
        Q = E.add(Q, P)
        if Q is None:
            return k
    return None  # Mazur: no rational torsion of order > 12, so P has infinite order


def run_control(E, pts, planted, brute=True):
    rels = rs.relation_search(E, pts, BOUND)
    out = {
        "curve_ainvs": curve_str(E),
        "points": [pt(P) for P in pts],
        "on_curve": all(E.on_curve(P) for P in pts),
        "relations": [list(m) for m in rels],
        "planted": list(planted),
        "detected": tuple(planted) in set(rels),
    }
    g = list(planted)
    out["all_relations_multiples_of_planted"] = all(
        any(tuple(k * v for v in g) == m for k in range(-BOUND, BOUND + 1) if k) for m in rels
    )
    if brute:
        bf = rs.relation_search_bruteforce(E, pts, BOUND)
        out["bruteforce_agrees"] = bf == rels
    out["P1_torsion_order"] = torsion_order_upto12(E, pts[0])
    out["naive_heights"] = [rs.naive_height(P) for P in pts]
    return out


def controls(rng):
    res = []
    for p in PRIMES:
        allpts_cache = {}
        # A: r = 2 short-model fit through two lifts, then P~_2 := [2] P~_1 (3 per prime)
        for c in range(3):
            a, b = random_curve(rng, p)
            pts = rs.affine_points(a, b, p)
            (P1, P2) = random_points(rng, pts, 2, need_nonzero_y_first=True)
            L = [(rs.sym(x, p), rs.sym(y, p)) for x, y in (P1, P2)]
            E = rs.fit(L)
            Pt1 = (Fr(L[0][0]), Fr(L[0][1]))
            Pt2 = E.mul(2, Pt1)
            d = run_control(E, [Pt1, Pt2], (2, -1))
            d.update({"p": p, "construction": "A_fit_r2_then_plant", "a": a, "b": b,
                      "mod_p_points": [list(P1), list(P2)]})
            res.append(d)
        # B: lifted curve through P~_1 alone: A = sym(a), B = y1^2 - x1^3 - A x1 (1 per prime)
        a, b = random_curve(rng, p)
        pts = rs.affine_points(a, b, p)
        (P1,) = random_points(rng, pts, 1, need_nonzero_y_first=True)
        x1, y1 = rs.sym(P1[0], p), rs.sym(P1[1], p)
        A = rs.sym(a, p)
        E = rs.Curve(0, 0, 0, A, y1 * y1 - x1 ** 3 - A * x1)
        Pt1 = (Fr(x1), Fr(y1))
        d = run_control(E, [Pt1, E.mul(2, Pt1)], (2, -1))
        d.update({"p": p, "construction": "B_alift_through_P1", "a": a, "b": b, "mod_p_points": [list(P1)]})
        res.append(d)
        # C: r = 3 fit with X^2 term, then (P~_1, [2] P~_1, P~_3) (1 per prime)
        a, b = random_curve(rng, p)
        pts = rs.affine_points(a, b, p)
        Ps = random_points(rng, pts, 3, need_nonzero_y_first=True)
        L = [(rs.sym(x, p), rs.sym(y, p)) for x, y in Ps]
        E = rs.fit(L)
        T = [(Fr(x), Fr(y)) for x, y in L]
        d = run_control(E, [T[0], E.mul(2, T[0]), T[2]], (2, -1, 0))
        d.update({"p": p, "construction": "C_fit_r3_then_plant", "a": a, "b": b,
                  "mod_p_points": [list(P) for P in Ps]})
        res.append(d)
    return res


def ptm_389a1():
    models = [
        ("389a1 [0,1,1,-2,0]", rs.Curve(0, 1, 1, -2, 0), [(-1, 1), (0, 0)]),
        ("389a1 integral a2-model [0,4,0,-32,16] (x=4X, y=8Y+4)", rs.Curve(0, 4, 0, -32, 16), [(-4, 12), (0, 4)]),
        ("389a1 short model [0,0,0,-3024,46224]", rs.Curve(0, 0, 0, -3024, 46224), [(-24, 324), (12, 108)]),
    ]
    out = []
    for name, E, P in models:
        pts = [(Fr(x), Fr(y)) for x, y in P]
        rels6 = rs.relation_search(E, pts, 6)
        bf6 = rs.relation_search_bruteforce(E, pts, 6)
        rels12 = rs.relation_search(E, pts, 12)
        out.append({
            "model": name, "ainvs": curve_str(E), "disc": str(E.disc()),
            "points": [pt(Q) for Q in pts], "on_curve": all(E.on_curve(Q) for Q in pts),
            "torsion_orders_upto12": [torsion_order_upto12(E, Q) for Q in pts],
            "relations_bound6": [list(m) for m in rels6], "bruteforce_bound6_agrees": bf6 == rels6,
            "relations_bound12": [list(m) for m in rels12],
        })
    # unplanted positive check on the same curve: (1,0) lies in the span of the generators
    E = rs.Curve(0, 1, 1, -2, 0)
    pts = [(Fr(-1), Fr(1)), (Fr(0), Fr(0)), (Fr(1), Fr(0))]
    rels = rs.relation_search(E, pts, 6)
    out.append({"model": "389a1 with third point (1,0) (expected: a short relation exists)",
                "points": [pt(Q) for Q in pts], "relations_bound6": [list(m) for m in rels],
                "bruteforce_bound6_agrees": rs.relation_search_bruteforce(E, pts, 6) == rels})
    return out


def torsion_positive():
    E = rs.Curve(0, -1, 1, -10, -20)  # 11a1
    P = (Fr(5), Fr(5))
    Q = (Fr(16), Fr(60))
    return {
        "curve": "11a1 [0,-1,1,-10,-20]", "disc": str(E.disc()),
        "r1_point_(5,5)_relations": [list(m) for m in rs.relation_search(E, [P], 6)],
        "r2_points_(5,5),(16,60)_relations": [list(m) for m in rs.relation_search(E, [P, Q], 6)],
        "r2_bruteforce_agrees": rs.relation_search_bruteforce(E, [P, Q], 6) == rs.relation_search(E, [P, Q], 6),
    }


def simulate(rng, trials):
    rows = []
    for p in PRIMES:
        for r in (2, 3):
            for t in range(trials):
                a, b = random_curve(rng, p)
                pts = rs.affine_points(a, b, p)
                Ps = random_points(rng, pts, r)
                L = [(rs.sym(x, p), rs.sym(y, p)) for x, y in Ps]
                E = rs.fit(L)
                D = E.disc()
                Dp = rs.frac_mod_p(D, p)
                row = {"p": p, "r": r, "t": t, "a": a, "b": b, "mod_p_points": [list(P) for P in Ps],
                       "lifts": [list(l) for l in L], "ainvs": curve_str(E),
                       "singular_mod_p": Dp is None or Dp == 0, "disc_zero_Q": D == 0,
                       "has_y0": any(y == 0 for _, y in L)}
                if row["singular_mod_p"] or row["disc_zero_Q"]:
                    row["relations"] = None
                    rows.append(row)
                    continue
                T = [(Fr(x), Fr(y)) for x, y in L]
                row["on_curve"] = all(E.on_curve(P) for P in T)
                rels = rs.relation_search(E, T, BOUND)
                row["relations"] = [list(m) for m in rels]
                row["class"] = rs.classify(rels, r)
                row["height_ratio"] = sum(rs.naive_height(P) for P in T) / len(T) / math.log(p)
                rows.append(row)
    return rows


def summarize(rows):
    cells = {}
    for row in rows:
        k = f"p={row['p']},r={row['r']}"
        c = cells.setdefault(k, {"trials": 0, "excluded_singular": 0, "valid": 0, "dependent": 0,
                                 "dependent_classes": {}, "trials_with_y0": 0,
                                 "dependent_without_y0": 0, "valid_without_y0": 0, "hr_sum": 0.0})
        c["trials"] += 1
        if row["relations"] is None:
            c["excluded_singular"] += 1
            continue
        c["valid"] += 1
        c["hr_sum"] += row["height_ratio"]
        if row["has_y0"]:
            c["trials_with_y0"] += 1
        else:
            c["valid_without_y0"] += 1
        if row["relations"]:
            c["dependent"] += 1
            c["dependent_classes"][row["class"]] = c["dependent_classes"].get(row["class"], 0) + 1
            if not row["has_y0"]:
                c["dependent_without_y0"] += 1
    tot = {"valid": 0, "dependent": 0, "valid_without_y0": 0, "dependent_without_y0": 0, "excluded_singular": 0}
    for c in cells.values():
        c["mean_height_ratio"] = c.pop("hr_sum") / c["valid"] if c["valid"] else None
        for k in tot:
            tot[k] += c[k]
    tot["dependence_rate"] = tot["dependent"] / tot["valid"]
    tot["dependence_rate_without_y0"] = tot["dependent_without_y0"] / tot["valid_without_y0"]
    return cells, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--trials", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0x67902E)
    ap.add_argument("--no-sim", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    rng = random.Random(args.seed)
    out = {"validator_task": "TASK-20261022-67902e", "phase": 1, "seed": args.seed, "bound": BOUND,
           "primes": PRIMES, "python": sys.version}
    out["controls"] = controls(rng)
    cs = out["controls"]
    out["controls_summary"] = {
        "n": len(cs), "detected": sum(c["detected"] for c in cs),
        "bruteforce_agrees_all": all(c.get("bruteforce_agrees", True) for c in cs),
        "all_relations_multiples_of_planted": all(c["all_relations_multiples_of_planted"] for c in cs),
        "P1_torsion_cases": sum(c["P1_torsion_order"] is not None for c in cs),
        "per_prime_detected": {str(p): f"{sum(c['detected'] for c in cs if c['p'] == p)}/"
                               f"{sum(1 for c in cs if c['p'] == p)}" for p in PRIMES},
    }
    out["ptm_389a1"] = ptm_389a1()
    out["torsion_positive_11a1"] = torsion_positive()
    if not args.no_sim:
        rng2 = random.Random(args.seed + 1)
        rows = simulate(rng2, args.trials)
        cells, tot = summarize(rows)
        out["simulation"] = {"trials_per_cell": args.trials, "cells": cells, "totals": tot,
                             "dependent_rows": [r for r in rows if r.get("relations")]}
    out["elapsed_seconds"] = round(time.time() - t0, 2)
    Path(args.out).write_text(json.dumps(out, indent=1, sort_keys=False) + "\n")
    print(json.dumps({"controls_summary": out["controls_summary"],
                      "ptm": [(m["model"], m.get("relations_bound6")) for m in out["ptm_389a1"]],
                      "torsion_positive": out["torsion_positive_11a1"],
                      "sim_totals": out.get("simulation", {}).get("totals"),
                      "elapsed": out["elapsed_seconds"]}, indent=1))


if __name__ == "__main__":
    main()
