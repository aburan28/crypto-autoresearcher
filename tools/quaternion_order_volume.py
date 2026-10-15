#!/usr/bin/env python3
"""Exact rank, volume and multiplicative-closure controls in the Hurwitz order.

This supplied maximal order is the Hamilton quaternion model B_(2,infinity).
No supersingular elliptic curve, isogeny map or characteristic-prime torsion
division is implemented here.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path
import random
from datetime import datetime, timezone
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lattice_experiment_manifest import write_artifacts

ONE = (1, 0, 0, 0)
I = (0, 1, 0, 0)
J = (0, 0, 1, 0)
H = (0, 0, 0, 1)
K = (-1, -1, -1, 2)


def hamilton(x):
    a, b, c, d = map(F, x)
    return a + d / 2, b + d / 2, c + d / 2, d / 2


def hurwitz(x):
    a, b, c, d = x
    out = (a - d, b - d, c - d, 2 * d)
    if any(F(v).denominator != 1 for v in out):
        raise ValueError("Hamilton vector is outside the supplied Hurwitz order")
    return tuple(int(v) for v in out)


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def subtract(x, y):
    return tuple(a - b for a, b in zip(x, y))


def scale(k, x):
    return tuple(k * a for a in x)


def multiply(x, y):
    a, b, c, d = hamilton(x)
    e, f, g, h = hamilton(y)
    return hurwitz((a * e - b * f - c * g - d * h,
                    a * f + b * e + c * h - d * g,
                    a * g - b * h + c * e + d * f,
                    a * h + b * g - c * f + d * e))


def norm(x):
    out = sum(t * t for t in hamilton(x))
    if out.denominator != 1:
        raise ArithmeticError("norm of a Hurwitz element is not integral")
    return int(out)


def matrix(cols):
    return [[F(col[i]) for col in cols] for i in range(4)]


def determinant(A):
    B = [list(map(F, row)) for row in A]
    n = len(B)
    if any(len(row) != n for row in B):
        raise ValueError("square matrix required")
    det = F(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if B[r][col]), None)
        if pivot is None:
            return F(0)
        if pivot != col:
            B[pivot], B[col] = B[col], B[pivot]
            det = -det
        p = B[col][col]
        det *= p
        for r in range(col + 1, n):
            q = B[r][col] / p
            for c in range(col + 1, n):
                B[r][c] -= q * B[col][c]
    return det


def rank(A):
    B = [list(map(F, row)) for row in A]
    r = 0
    for c in range(len(B[0])):
        pivot = next((i for i in range(r, len(B)) if B[i][c]), None)
        if pivot is None:
            continue
        B[pivot], B[r] = B[r], B[pivot]
        p = B[r][c]
        B[r] = [v / p for v in B[r]]
        for i in range(r + 1, len(B)):
            q = B[i][c]
            B[i] = [x - q * y for x, y in zip(B[i], B[r])]
        r += 1
        if r == len(B):
            break
    return r


def coordinates(cols, x):
    B = [row + [F(x[i])] for i, row in enumerate(matrix(cols))]
    for c in range(4):
        pivot = next((r for r in range(c, 4) if B[r][c]), None)
        if pivot is None:
            raise ValueError("membership needs a full-rank supplied basis")
        B[pivot], B[c] = B[c], B[pivot]
        p = B[c][c]
        B[c] = [v / p for v in B[c]]
        for r in range(4):
            if r != c:
                q = B[r][c]
                B[r] = [a - q * b for a, b in zip(B[r], B[c])]
    return tuple(row[-1] for row in B)


def contains(cols, x):
    return all(v.denominator == 1 for v in coordinates(cols, x))


def gram(cols):
    standard = [hamilton(x) for x in cols]
    return [[2 * sum(a * b for a, b in zip(x, y)) for y in standard] for x in standard]


def lattice_certificate(cols):
    B = matrix(cols)
    r = rank(B)
    G = gram(cols)
    dg = determinant(G)
    if r < 4:
        return {"basis": cols, "rank": r, "gram_determinant": str(dg),
                "index_in_hurwitz": None, "unital_order": False,
                "reason": "missing quaternionic rank; no finite-index certificate"}
    index = abs(determinant(B))
    if index.denominator != 1 or dg != 4 * index * index:
        raise ArithmeticError("basis determinant and trace Gram disagree")
    counterexample = None
    for a in cols:
        for b in cols:
            ab = multiply(a, b)
            if not contains(cols, ab) and counterexample is None:
                counterexample = {"left": a, "right": b, "product": ab,
                                  "product_coordinates": list(map(str, coordinates(cols, ab)))}
    unital = contains(cols, ONE)
    return {"basis": cols, "rank": r, "gram": [[str(x) for x in row] for row in G],
            "gram_determinant": str(dg), "index_in_hurwitz": int(index),
            "contains_one": unital, "multiplicatively_closed": counterexample is None,
            "unital_order": unital and counterexample is None,
            "closure_counterexample": counterexample}


def pair_certificate(a, b):
    ab = multiply(a, b)
    ba = multiply(b, a)
    commutator_norm = norm(subtract(ab, ba))
    cols = (ONE, a, b, ab)
    B = matrix(cols)
    dg = determinant(gram(cols))
    r = rank(B)
    index = abs(determinant(B)) if r == 4 else None
    if dg != commutator_norm ** 2:
        raise ArithmeticError("independently calculated Gram/commutator identity failed")
    if index is not None and (index.denominator != 1 or dg != 4 * index * index):
        raise ArithmeticError("pair index identity failed")
    return {"a": a, "b": b, "norm_sum": norm(a) + norm(b),
            "commutes": ab == ba, "commutator_norm": commutator_norm,
            "rank": r, "index_in_hurwitz": int(index) if index is not None else None,
            "gram_determinant": str(dg)}


def run(seed=1729):
    fixtures = {
        "hurwitz": (ONE, I, J, H), "lipschitz": (ONE, I, J, K),
        "rank_two_commuting": (ONE, I, scale(2, I), scale(3, I)),
        "nonclosed_index_four": (ONE, I, J, scale(2, K)),
        "closed_index_four": (ONE, I, add(J, K), subtract(J, K)),
        "nonclosed_mixed": (ONE, scale(2, I), scale(2, J), scale(3, K)),
        "nonunital_scaled_hurwitz": tuple(scale(2, x) for x in (ONE, I, J, H)),
    }
    lattices = [{"label": label, **lattice_certificate(cols)} for label, cols in fixtures.items()]
    controls = {x["label"]: x for x in lattices}
    if (controls["hurwitz"]["index_in_hurwitz"] != 1
            or not controls["hurwitz"]["unital_order"]
            or controls["lipschitz"]["index_in_hurwitz"] != 2
            or controls["nonclosed_index_four"]["gram_determinant"] != controls["closed_index_four"]["gram_determinant"]
            or controls["nonclosed_index_four"]["unital_order"]
            or not controls["closed_index_four"]["unital_order"]):
        raise ArithmeticError("the planted closure/volume controls failed")
    candidates = list(product((-1, 0, 1), repeat=4))
    cases = [pair_certificate(a, b) for a in candidates for b in candidates]
    random.Random(seed).shuffle(cases)
    histogram = {}
    for case in cases:
        key = "rank_deficient" if case["index_in_hurwitz"] is None else str(case["index_in_hurwitz"])
        histogram[key] = histogram.get(key, 0) + 1
    nonzero_pairs = [c for c in cases if norm(c["a"]) and norm(c["b"])]
    full_rank_pairs = [c for c in nonzero_pairs if c["rank"] == 4]
    shortest = min(nonzero_pairs, key=lambda c: (c["norm_sum"], c["a"], c["b"]))
    shortest_full_rank = min(full_rank_pairs, key=lambda c: (c["norm_sum"], c["a"], c["b"]))
    minimum_index = min(full_rank_pairs, key=lambda c: (c["index_in_hurwitz"], c["norm_sum"], c["a"], c["b"]))
    selections = [{"policy": name, "selected_pair": case, "candidate_pairs_scored": count}
                  for name, case, count in (
                      ("shortest_norm", shortest, len(nonzero_pairs)),
                      ("shortest_full_rank", shortest_full_rank, len(full_rank_pairs)),
                      ("minimum_full_rank_index", minimum_index, len(full_rank_pairs)))]
    return {"schema_version": "quaternion-order-volume/v1", "direction": "quaternion_volume", "seed": seed,
            "parameters": {"p": 2, "quaternion_algebra": "Hamilton B(-1,-1)",
                           "hurwitz_basis": "1,i,j,(1+i+j+k)/2", "coordinate_values": [-1, 0, 1]},
            "cases": cases, "lattice_controls": lattices,
            "named_pair_controls": {"i_j": pair_certificate(I, J), "i_h": pair_certificate(I, H)},
            "selection_diagnostics": {"policies": selections, "enumerated_pairs": len(cases),
                                      "comparison_scope": "same supplied frozen candidate table",
                                      "accounting_status": "incomplete; no performance claim",
                                      "unpriced_work": ["pair enumeration and Gram/commutator evaluation",
                                                        "rank/index arithmetic", "sorting or comparison costs",
                                                        "isogeny discovery/evaluation and transport"]},
            "checks": {"candidate_elements": len(candidates), "ordered_pair_cases": len(cases),
                       "lattice_controls": len(lattices), "index_histogram": histogram,
                       "all_exact_checks_passed": True},
            "limitations": ["One supplied maximal quaternion order at p=2, not arbitrary supersingular curve maps.",
                            "A small Gram determinant measures additive index, not multiplicative closure or subgroup action.",
                            "Noncommuting generators can still give the proper Lipschitz suborder.",
                            "Enumeration and scoring exclude isogeny discovery/evaluation and establish no performance advantage.",
                            "Characteristic-prime division and finite-field realization remain separate unimplemented obligations."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        value = json.loads(args.check.read_text())
        if value != json.loads(json.dumps(run(value["seed"]))):
            raise ValueError("exact fixture replay disagrees; independent research review pending")
        print(json.dumps({"valid": True, "checker_scope": "exact fixture replay"}))
        return
    started = datetime.now(timezone.utc).isoformat()
    wall_start, cpu_start = time.monotonic(), time.process_time()
    value = run(args.seed)
    if args.output_dir:
        write_artifacts(value, args.output_dir, args.seed, started, wall_start, cpu_start)
    print(json.dumps(value["checks"]))


if __name__ == "__main__":
    main()
