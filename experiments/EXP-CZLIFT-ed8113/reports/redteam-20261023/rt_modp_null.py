"""Red-team null-object control for EXP-CZLIFT-ed8113 (TASK-20261023-62eb31).

The identical bounded relation search, run on the RESIDUES mod p of the
replayed producer inputs (rt_replay_inputs.json) instead of on their lifts
over Q. A relation over Q reduces to the same relation mod p, so the
mod-p rate is an upper bound on the Q rate that the lift cannot exceed
(JKSST 2000, proof of Thm 4.1: Pr ~ (2C)^r / p). Also records, per trial, the
smallest max-norm relation mod p (the coefficient size an xedni attacker needs
to lift), searched up to BMAX[r]. Independent affine arithmetic mod p; uses no
producer code.
"""
from __future__ import annotations

import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
BOUND = 6
BMAX = {2: 2000, 3: 80}


def add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None
        lam = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)


def neg(P, p):
    return None if P is None else (P[0], (-P[1]) % p)


def multiples(P, B, a, p):
    """dict k -> kP for |k| <= B."""
    t = {0: None}
    R = None
    for k in range(1, B + 1):
        R = add(R, P, a, p)
        t[k] = R
        t[-k] = neg(R, p)
    return t


def min_relation(pts, a, p, B):
    """Smallest max|n| over nonzero n in [-B,B]^r with sum n_i P_i = O mod p; None if none."""
    r = len(pts)
    tabs = [multiples(P, B, a, p) for P in pts]
    if r == 2:
        best_for = {}  # point -> smallest |n1| (nonzero if point is O handled separately)
        for n1 in range(-B, B + 1):
            Q = tabs[0][n1]
            if Q is None and n1 == 0:
                continue
            if Q not in best_for or abs(n1) < best_for[Q]:
                best_for[Q] = abs(n1)
        best = None
        for n2 in range(0, B + 1):
            target = neg(tabs[1][n2], p)
            if n2 == 0:
                c = best_for.get(None)  # nonzero n1 with n1 P1 = O
            else:
                c = 0 if target is None else best_for.get(target)
            if c is not None:
                m = max(c, n2)
                if best is None or m < best:
                    best = m
        return best
    if r == 3:
        best12 = {}
        for n1 in range(-B, B + 1):
            for n2 in range(-B, B + 1):
                if n1 == 0 and n2 == 0:
                    continue
                Q = add(tabs[0][n1], tabs[1][n2], a, p)
                m = max(abs(n1), abs(n2))
                if Q not in best12 or m < best12[Q]:
                    best12[Q] = m
        best = None
        for n3 in range(0, B + 1):
            target = neg(tabs[2][n3], p)
            if n3 == 0:
                c = best12.get(None)
            else:
                c = 0 if target is None else best12.get(target)
            if c is not None:
                m = max(c, n3)
                if best is None or m < best:
                    best = m
        return best
    raise ValueError(r)


def main():
    d = json.load(open(os.path.join(HERE, "rt_replay_inputs.json")))
    out = {"bound": BOUND, "bmax": BMAX, "cells": []}
    for seed in ("20261009", "20261010"):
        rows = d[seed]["rows"]
        cells = {}
        for row in rows:
            p, r, a = row["p"], row["r"], row["a"]
            pts = [(int(x) % p, int(y) % p) for x, y in row["pts"]]
            # residues reproduce E(F_p)
            for x, y in pts:
                assert (y * y - x ** 3 - a * x - row["b"]) % p == 0
            m = min_relation(pts, a, p, BMAX[r])
            cells.setdefault((p, r), []).append(m)
        for (p, r), ms in sorted(cells.items()):
            found = [m for m in ms if m is not None]
            out["cells"].append({
                "seed": int(seed), "p": p, "r": r, "trials": len(ms),
                "modp_bounded_relation_rate": sum(1 for m in found if m <= BOUND) / len(ms),
                "modp_bounded_relation_count": sum(1 for m in found if m <= BOUND),
                "min_relation_found_within_bmax": len(found),
                "min_relation_median": statistics.median(found) if found else None,
                "min_relation_min": min(found) if found else None,
                "pigeonhole_scale_p_pow_1_over_r": round(p ** (1 / r), 2),
                "naive_expected_rate_(13^r-1)/2/p": round(((13 ** r - 1) / 2) / p, 4),
            })
            print(seed, p, r, out["cells"][-1]["modp_bounded_relation_count"], "/", len(ms),
                  "median_min_rel", out["cells"][-1]["min_relation_median"],
                  "found", len(found), "p^(1/r)", round(p ** (1 / r), 1))
    json.dump(out, open(os.path.join(HERE, "rt_modp_null.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
