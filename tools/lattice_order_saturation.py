#!/usr/bin/env python3
"""Order-growth and faithful torsion-division experiments on planted CM orders.

Scores and selected-generator counts are diagnostics, not map-discovery costs
or measured end-to-end performance advantages.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import json
from math import gcd
from pathlib import Path
import random
from datetime import datetime, timezone
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lattice_experiment_manifest import write_artifacts

DISCRIMINANTS = (-3, -4, -7, -8, -11, -15, -20, -23)
CONDUCTORS = (1, 2, 3, 6)
PRIMES = (2, 3, 5, 7)
GENERATORS = ((0, 6), (0, 10), (0, 15), (1, 6), (2, 6), (3, 6), (0, -6),
              (1, 0), (2, 0), (3, 0), (4, 0), (5, 0))


def params(D):
    if D not in DISCRIMINANTS:
        raise ValueError("field outside the frozen panel")
    t = D % 2
    return t, (t * t - D) // 4


def multiply(D, f, x, y):
    t, n = params(D)
    a, b = x
    c, d = y
    return a * c - n * f * f * b * d, a * d + b * c + t * f * b * d


def norm(D, f, x):
    t, n = params(D)
    a, b = x
    return a * a + t * f * a * b + n * f * f * b * b


def action(D, f, x):
    """Multiply both supplied period generators to obtain a faithful action."""
    return tuple(tuple(multiply(D, f, x, ((1, 0), (0, 1))[j])[i]
                       for j in range(2)) for i in range(2))


def disc_from_trace(D, f, g):
    if not g:
        raise ValueError("rank-one scalar span has no quadratic-order discriminant")
    t, _ = params(D)
    theta = (0, g)
    square = multiply(D, f, theta, theta)
    trace_theta = t * f * g
    trace_square = 2 * square[0] + t * f * square[1]
    return 2 * trace_square - trace_theta * trace_theta


def extended_gcd(a, b):
    if b == 0:
        return abs(a), (1 if a >= 0 else -1), 0
    g, x, y = extended_gcd(b, a % b)
    return g, y, x - (a // b) * y


def bezout(values):
    g = 0
    coefficients = []
    for value in values:
        new, x, y = extended_gcd(g, value)
        coefficients = [x * c for c in coefficients] + [y]
        g = new
    if sum(c * v for c, v in zip(coefficients, values)) != g:
        raise ArithmeticError("Bezout witness failed")
    return g, coefficients


def select(D, f, pool, policy):
    if policy not in ("shortest_norm", "smallest_index"):
        raise ValueError("unknown policy")
    remaining = list(pool)
    steps = []
    g = 0
    norm_scores = 0
    gcd_scores = 0
    if policy == "shortest_norm":
        remaining.sort(key=lambda x: (norm(D, f, x), x))
        norm_scores = len(remaining)
    while remaining and g != 1:
        if policy == "smallest_index":
            scores = []
            for x in remaining:
                new_g = gcd(g, x[1])
                gcd_scores += 1
                scores.append((new_g if new_g else 10 ** 9, norm(D, f, x), x))
                norm_scores += 1
            chosen = min(scores)[2]
            remaining.remove(chosen)
        else:
            chosen = remaining.pop(0)
        before = g
        g = gcd(g, chosen[1])
        gcd_scores += 1
        steps.append({"generator": chosen, "norm": norm(D, f, chosen),
                      "rank": 2 if g else 1, "order_index": g if g else None,
                      "discriminant": disc_from_trace(D, f, g) if g else None,
                      "enlarges_order": g != before})
    final_g, certificate = bezout([s["generator"][1] for s in steps])
    if final_g != g:
        raise ArithmeticError("selection index/witness disagrees")
    return {"policy": policy, "steps": steps, "final_order_index": g if g else None,
            "selected_generators": len(steps), "norm_score_evaluations": norm_scores,
            "gcd_score_evaluations": gcd_scores, "bezout_coefficients": certificate,
            "operation_scope": "partial selection arithmetic counters; accounting incomplete",
            "unpriced_work": ["sorting comparisons", "list maintenance", "discriminant arithmetic",
                              "Bezout and certificate verification", "closure checks",
                              "generator discovery and map evaluation"]}


def division_control(D, f, x, ell):
    if ell not in PRIMES:
        raise ValueError("module prime outside the panel")
    A = action(D, f, x)
    basis_images = [[A[i][j] % ell for i in range(2)] for j in range(2)]
    full_zero = all(v == [0, 0] for v in basis_images)
    divided = [[str(Fraction(a, ell)) for a in row] for row in A]
    integral = all(a % ell == 0 for row in A for a in row)
    if integral != full_zero:
        raise ArithmeticError("faithful module and divisibility disagree")
    return {"ell": ell, "element": x, "action": A, "basis_images": basis_images,
            "kills_full_module": full_zero, "divided_action": divided,
            "division_integral_on_actual_lattice": integral}


def saturate(D, f, starting_coefficient=6):
    g = starting_coefficient
    steps = []
    for ell in PRIMES:
        while True:
            certificate = division_control(D, f, (0, g), ell)
            steps.append(certificate)
            if not certificate["kills_full_module"]:
                break
            g //= ell
    return {"initial_index": starting_coefficient, "steps": steps, "final_index": g}


def run(seed=1729):
    cases = []
    pool = list(GENERATORS)
    random.Random(seed).shuffle(pool)
    wrong_ambient = []
    for D in DISCRIMINANTS:
        for f in CONDUCTORS:
            policies = [select(D, f, pool, p) for p in ("shortest_norm", "smallest_index")]
            saturation = saturate(D, f)
            controls = [division_control(D, f, (0, b), ell) for b in (1, 6, 10, 15) for ell in PRIMES]
            for g in (1, 2, 3, 6, 10, 15):
                if disc_from_trace(D, f, g) != D * f * f * g * g:
                    raise ArithmeticError("trace-based discriminant/index check failed")
                for x in ((1, 0), (0, g), (2, -g)):
                    for y in ((1, 0), (0, g), (3, g)):
                        if multiply(D, f, x, y)[1] % g:
                            raise ArithmeticError("the generated quadratic suborder is not closed")
            for ell in PRIMES:
                actual = division_control(D, f, (0, 1), ell)
                maximal = division_control(D, 1, (0, f), ell)
                if maximal["kills_full_module"] and not actual["kills_full_module"]:
                    wrong_ambient.append({"D_K": D, "planted_f": f, "ell": ell,
                                          "actual_lattice_division_allowed": False,
                                          "wrong_maximal_order_module_allows_division": True})
            if any(p["final_order_index"] != 1 for p in policies) or saturation["final_index"] != 1:
                raise ArithmeticError("the frozen complete generator/saturation control failed")
            cases.append({"D_K": D, "planted_order_conductor": f, "generator_pool": pool,
                          "policies": policies, "saturation": saturation, "division_controls": controls})
    return {"schema_version": "lattice-order-saturation/v1", "direction": "order_saturation", "seed": seed,
            "parameters": {"D_K": DISCRIMINANTS, "conductors": CONDUCTORS,
                           "primary_generator_coefficients": [6, 10, 15], "module_primes": PRIMES},
            "cases": cases, "wrong_ambient_controls": wrong_ambient,
            "checks": {"order_cases": len(cases), "policy_arms": len(cases) * 2,
                       "division_controls": len(cases) * 16,
                       "wrong_ambient_collisions": len(wrong_ambient), "all_exact_checks_passed": True},
            "limitations": ["The actual ambient order and candidate generators are supplied, not discovered.",
                            "Selection counts omit isogeny construction/evaluation and are not performance claims.",
                            "Full additive rank is not full order saturation; scalar and redundant maps are retained controls.",
                            "Torsion division is certified only on the actual faithful supplied lattice.",
                            "No finite-field characteristic-prime division, subgroup solve, or ECDLP consequence was measured."]}


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
