#!/usr/bin/env python3
"""Exact transport, kernel and module controls on supplied CM order lattices."""
from __future__ import annotations

import argparse
from fractions import Fraction as F
import json
from math import gcd, lcm
from pathlib import Path
import random
from datetime import datetime, timezone
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lattice_experiment_manifest import write_artifacts

DISCRIMINANTS = (-3, -4, -7, -8, -11, -15, -20, -23)
CONDUCTORS = tuple(range(1, 13))
SCALES = (1, 2, 3)
PRIMES = (2, 3, 5, 7)
TRANSFORMS = {
    "complete": ((1, 0), (0, 1)), "uniform_two": ((2, 0), (0, 2)),
    "anisotropic_two": ((2, 0), (0, 1)),
    "unimodular_shear": ((1, 1), (0, 1)), "index_six": ((2, 1), (0, 3)),
}


def mul(X, Y):
    return tuple(tuple(sum(F(X[i][k]) * F(Y[k][j]) for k in range(2))
                       for j in range(2)) for i in range(2))


def inverse(X):
    d = F(X[0][0]) * X[1][1] - F(X[0][1]) * X[1][0]
    if not d:
        raise ValueError("singular lattice matrix")
    return ((F(X[1][1]) / d, -F(X[0][1]) / d),
            (-F(X[1][0]) / d, F(X[0][0]) / d))


def denominator(X):
    return lcm(*(F(x).denominator for row in X for x in row))


def params(D):
    if D not in DISCRIMINANTS:
        raise ValueError("field outside the frozen pilot")
    t = D % 2
    return t, (t * t - D) // 4


def action(D, f, k=1):
    """Integral matrix of k*f*omega on basis (1,f*omega)."""
    if f < 1 or k < 1:
        raise ValueError("positive conductor and generator scale required")
    t, n = params(D)
    return ((0, -n * k * f * f), (k, t * k * f))


def isogeny_matrix(f, g):
    d = gcd(f, g)
    if min(f, g) < 1:
        raise ValueError("positive conductors required")
    return ((g // d, 0), (0, f // d))


def transported(D, f, g, k=1, P=((1, 0), (0, 1))):
    M = isogeny_matrix(f, g)
    A = mul(mul(M, action(D, f, k)), inverse(M))
    return mul(mul(inverse(P), A), P)


def direct_action(D, f, g, k=1, P=((1, 0), (0, 1))):
    """Multiply both target period vectors, then solve their coordinates.

    This construction uses no transport matrix or gcd prediction.
    """
    t, n = params(D)
    B = ((P[0][0], P[0][1]), (g * P[1][0], g * P[1][1]))
    images = ((-n * k * f * B[1][0], -n * k * f * B[1][1]),
              (k * f * (B[0][0] + t * B[1][0]),
               k * f * (B[0][1] + t * B[1][1])))
    return mul(inverse(B), images)


def kernel_preservation(A, M):
    """Enumerate ker(phi)=M^-1 Z^2/Z^2 for the supplied diagonal M."""
    if M[0][1] or M[1][0] or min(M[0][0], M[1][1]) < 1:
        raise ValueError("kernel fixture requires a positive diagonal matrix")
    c1, c2 = M[0][0], M[1][1]
    checked = 0
    for x in range(c1):
        for y in range(c2):
            point = (F(x, c1), F(y, c2))
            image = tuple(sum(F(A[i][j]) * point[j] for j in range(2)) for i in range(2))
            checked += 1
            if (c1 * image[0]).denominator != 1 or (c2 * image[1]).denominator != 1:
                return {"preserves": False, "members_checked": checked,
                        "kernel_size": c1 * c2, "counterexample": {
                            "point": list(map(str, point)), "image": list(map(str, image))}}
    return {"preserves": True, "members_checked": checked,
            "kernel_size": c1 * c2, "counterexample": None}


def module_zero(A, ell):
    """Faithful full action on Lambda/ell Lambda, checked on its two generators."""
    if ell not in PRIMES or denominator(A) != 1:
        raise ValueError("integral source action and a frozen module prime required")
    images = [[int(A[i][j]) % ell for i in range(2)] for j in range(2)]
    return {"ell": ell, "basis_images": images, "kills_full_module": all(x == [0, 0] for x in images)}


def encode(X):
    return [[str(F(x)) for x in row] for row in X]


def run(seed=1729):
    cases = []
    changed_denominators = 0
    concealed = 0
    for D in DISCRIMINANTS:
        for f in CONDUCTORS:
            for g in CONDUCTORS:
                arms = []
                for k in SCALES:
                    A = action(D, f, k)
                    T = transported(D, f, g, k)
                    d = denominator(T)
                    prediction = g // gcd(k * f, g)
                    kernel = kernel_preservation(A, isogeny_matrix(f, g))
                    if d != prediction or kernel["preserves"] != (d == 1):
                        raise ArithmeticError("transport or independently enumerated kernel control failed")
                    reverse_d = denominator(transported(D, g, f, k))
                    concealed += k != 1 and d != g // gcd(f, g)
                    bases = []
                    for name, P in TRANSFORMS.items():
                        target = transported(D, f, g, k, P)
                        if target != direct_action(D, f, g, k, P):
                            raise ArithmeticError("direct multiplication coordinate oracle disagrees")
                        det = abs(P[0][0] * P[1][1] - P[0][1] * P[1][0])
                        dp = denominator(target)
                        if det == 1 and dp != d:
                            raise ArithmeticError("unimodular basis change altered denominator")
                        changed_denominators += dp != d
                        bases.append({"label": name, "period_basis_change": P, "index": det,
                                      "lattice_scope": "same_lattice" if det == 1 else "changed_lattice",
                                      "action": encode(target), "least_denominator": dp,
                                      "direct_multiplication_agrees": True})
                    modules = [module_zero(A, ell) for ell in PRIMES]
                    for control in modules:
                        divided = tuple(tuple(F(x, control["ell"]) for x in row) for row in A)
                        if control["kills_full_module"] != (denominator(divided) == 1):
                            raise ArithmeticError("faithful torsion division control failed")
                    arms.append({"generator_scale": k, "source_action": A,
                                 "standard_target_denominator": d, "reverse_denominator": reverse_d,
                                 "kernel": kernel, "basis_controls": bases, "module_controls": modules})
                cases.append({"D_K": D, "planted_conductors": [f, g], "arms": arms})
    fs = (6, 10, 15)
    edges = []
    for i, j in ((0, 1), (1, 2), (0, 2)):
        forward = denominator(transported(-4, fs[i], fs[j]))
        reverse = denominator(transported(-4, fs[j], fs[i]))
        edges.append({"endpoints": [i, j], "forward": forward, "reverse": reverse,
                      "ratio": str(F(forward, reverse))})
    anchored = [fs[0], int(F(fs[0]) * F(edges[0]["ratio"])),
                int(F(fs[0]) * F(edges[2]["ratio"]))]
    same = all(denominator(transported(-4, 2 * fs[i], 2 * fs[j])) == edges[h]["forward"]
               and denominator(transported(-4, 2 * fs[j], 2 * fs[i])) == edges[h]["reverse"]
               for h, (i, j) in enumerate(((0, 1), (1, 2), (0, 2))))
    if anchored != list(fs) or not same:
        raise ArithmeticError("anchored/unanchored identifiability control failed")
    random.Random(seed).shuffle(cases)
    return {"schema_version": "lattice-transport-denominators/v1", "direction": "transport_denominators",
            "seed": seed, "parameters": {"D_K": DISCRIMINANTS, "conductors": CONDUCTORS,
                                         "generator_scales": SCALES, "module_primes": PRIMES},
            "cases": cases, "graph": {"edges": edges, "anchor": {"vertex": 0, "conductor": 6},
                                        "anchored_recovered": anchored,
                                        "unanchored_indistinguishable": [fs, tuple(2 * f for f in fs)]},
            "checks": {"ordered_pair_cases": len(cases), "generator_arms": len(cases) * 3,
                       "basis_cases": len(cases) * 15, "nonprimitive_concealment_arms": concealed,
                       "changed_lattice_denominator_arms": changed_denominators,
                       "all_exact_checks_passed": True},
            "limitations": ["Supplied C/O_f principal lattices and known generators, not unknown finite-field rings.",
                            "Nonunimodular target changes can alter the order; original conductor formulas are not applied to them.",
                            "Nonprimitive generators can conceal conductor differences; an anchor is required for absolute scale.",
                            "Faithful synthetic modules are not a substitute for realizing geometric torsion or actual finite-field maps.",
                            "No map-discovery cost, practical speedup, ECDLP consequence or characteristic-prime division was measured."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        value = json.loads(args.check.read_text())
        if value != json.loads(json.dumps(run(value["seed"]))):
            raise ValueError("exact fixture replay disagrees; independent research review remains pending")
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
