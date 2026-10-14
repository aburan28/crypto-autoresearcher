#!/usr/bin/env python3
"""Exact CM Hom-degree fixtures; no finite-field curve maps or timing claims.

The supplied curves are C/O_f. Complete Hom bases are constructed from
integer lattice-preservation constraints. Planted sublattice indices remain
known fixture data, rather than being inferred from degree consistency.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations
import json
from math import gcd, isqrt, lcm
from pathlib import Path
import random
from datetime import datetime, timezone
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lattice_experiment_manifest import write_artifacts

DISCRIMINANTS = (-3, -4, -7, -8, -11, -15, -20, -23)
CONDUCTORS = tuple(range(1, 13))
TRANSFORMS = {
    "complete": ((1, 0), (0, 1)),
    "uniform_two": ((2, 0), (0, 2)),
    "anisotropic_two": ((2, 0), (0, 1)),
    "unimodular_shear": ((1, 1), (0, 1)),
    "index_six": ((2, 1), (0, 3)),
}


def trace_norm(D: int) -> tuple[int, int]:
    if D not in DISCRIMINANTS:
        raise ValueError("this frozen pilot accepts only its listed field discriminants")
    t = D % 2
    return t, (t * t - D) // 4


def norm(D: int, a: int, b: int) -> int:
    t, n = trace_norm(D)
    return a * a + t * a * b + n * b * b


def preserves(D: int, f: int, g: int, a: int, b: int) -> bool:
    """Multiplication by a+b*omega sends O_f into O_g."""
    t, _ = trace_norm(D)
    if min(f, g) < 1:
        raise ValueError("conductors must be positive")
    return b % g == 0 and (f * a + f * b * t) % g == 0


def hom_basis(f: int, g: int) -> tuple[tuple[int, int], tuple[int, int]]:
    if min(f, g) < 1:
        raise ValueError("conductors must be positive")
    # a is a multiple of g/gcd(f,g); b is a multiple of g.
    return (g // gcd(f, g), 0), (0, g)


def degree(D: int, f: int, g: int, a: int, b: int) -> int:
    if not preserves(D, f, g, a, b):
        raise ValueError("the proposed multiplier is not a Hom element")
    value = Fraction(f, g) * norm(D, a, b)
    if value.denominator != 1:
        raise ArithmeticError("degree of a certified map must be integral")
    return value.numerator


def form(D: int, f: int, g: int, P: tuple) -> tuple[int, int, int]:
    u, v = hom_basis(f, g)
    cols = [tuple(P[0][j] * u[k] + P[1][j] * v[k] for k in range(2))
            for j in range(2)]
    a = degree(D, f, g, *cols[0])
    c = degree(D, f, g, *cols[1])
    b = degree(D, f, g, *(cols[0][k] + cols[1][k] for k in range(2))) - a - c
    return a, b, c


def invariants(q: tuple[int, int, int]) -> tuple[int, int]:
    a, b, c = q
    if a <= 0 or c <= 0 or b * b >= 4 * a * c:
        raise ValueError("positive definite nondegenerate form required")
    return b * b - 4 * a * c, gcd(gcd(a, abs(b)), c)


def pair_product(D: int, q: tuple[int, int, int]) -> Fraction:
    disc, content = invariants(q)
    return Fraction(disc, D * content)


def complete_form_constraints(D: int, q: tuple[int, int, int], f: int, g: int) -> bool:
    """Necessary complete-Hom constraints; not a sufficient basis certificate."""
    disc, content = invariants(q)
    return disc == D * lcm(f, g) ** 2 and content == lcm(f, g) // gcd(f, g)


def triangle(products: tuple[int | Fraction, int | Fraction, int | Fraction]) -> tuple[int, int, int]:
    p12, p13, p23 = map(Fraction, products)
    if min(p12, p13, p23) <= 0:
        raise ValueError("positive pair products required")
    out = []
    for square in (p12 * p13 / p23, p12 * p23 / p13, p13 * p23 / p12):
        root = isqrt(square.numerator)
        if square.denominator != 1 or root * root != square.numerator:
            raise ValueError("pair products have no integral triangle reconstruction")
        out.append(root)
    return tuple(out)


def graph_assignments(edges: list[tuple[int, int, int]], vertices: int, bound: int) -> list[list[int]]:
    """Bounded positive-integer reconstruction from supplied products only."""
    if vertices < 1 or bound < 1 or any(p <= 0 for _, _, p in edges):
        raise ValueError("invalid bounded graph fixture")
    solutions = []
    for root in range(1, bound + 1):
        values = {0: Fraction(root)}
        changed = True
        while changed:
            changed = False
            for i, j, product in edges:
                if i in values and j not in values:
                    values[j] = Fraction(product) / values[i]
                    changed = True
                elif j in values and i not in values:
                    values[i] = Fraction(product) / values[j]
                    changed = True
        if len(values) != vertices:
            raise ValueError("this fixture requires a connected graph")
        if all(v.denominator == 1 and 1 <= v <= bound for v in values.values()) and all(
                values[i] * values[j] == product for i, j, product in edges):
            solutions.append([int(values[i]) for i in range(vertices)])
    return solutions


def run(seed: int = 1729) -> dict:
    cases = []
    for D in DISCRIMINANTS:
        for f in CONDUCTORS:
            for g in CONDUCTORS:
                transforms = []
                for label, P in TRANSFORMS.items():
                    q = form(D, f, g, P)
                    disc, content = invariants(q)
                    index = abs(P[0][0] * P[1][1] - P[0][1] * P[1][0])
                    if disc != D * lcm(f, g) ** 2 * index ** 2:
                        raise ArithmeticError("discriminant/index control failed")
                    transforms.append({"label": label, "basis_transform": P,
                                       "planted_index": index, "coefficients": q,
                                       "discriminant": disc, "content": content,
                                       "naive_pair_product": str(pair_product(D, q)),
                                       "basis_status": "complete" if index == 1 else "uncertified_sublattice"})
                if pair_product(D, tuple(transforms[0]["coefficients"])) != f * g:
                    raise ArithmeticError("complete-basis reconstruction failed")
                cases.append({"D_K": D, "planted_conductors": [f, g], "transforms": transforms})
    triples = []
    for fs in combinations(CONDUCTORS, 3):
        ps = tuple(pair_product(-4, form(-4, fs[i], fs[j], TRANSFORMS["complete"]))
                   for i, j in ((0, 1), (0, 2), (1, 2)))
        recovered = triangle(ps)
        scaled = triangle(tuple(4 * p for p in ps))
        if recovered != fs or scaled != tuple(2 * f for f in fs):
            raise ArithmeticError("triangle or scaled false-consistency control failed")
        pairs = ((0, 1), (0, 2), (1, 2))
        scaled_constraints = all(complete_form_constraints(
            -4, form(-4, fs[i], fs[j], TRANSFORMS["uniform_two"]), scaled[i], scaled[j])
            for i, j in pairs)
        if scaled_constraints:
            raise ArithmeticError("the full discriminant/content gate accepted a uniform scaled control")
        triples.append({"planted": fs, "recovered": recovered,
                        "uniform_two_naive_recovered": scaled,
                        "uniform_two_is_a_false_certificate": True,
                        "full_discriminant_content_gate_rejects_uniform_two": not scaled_constraints})
    graphs = [
        {"name": "triangle", "edges": [(0, 1, 60), (0, 2, 90), (1, 2, 150)], "vertices": 3},
        {"name": "bipartite_cycle", "edges": [(0, 1, 6), (1, 2, 12), (2, 3, 24), (3, 0, 12)], "vertices": 4},
    ]
    for graph in graphs:
        graph["solutions_with_conductors_at_most_60"] = graph_assignments(graph["edges"], graph["vertices"], 60)
    random.Random(seed).shuffle(cases)
    return {"schema_version": "lattice-hom-degree/v1", "direction": "hom_degree_forms", "seed": seed,
            "parameters": {"D_K": DISCRIMINANTS, "conductors": CONDUCTORS, "graph_bound": 60},
            "cases": cases, "triangles": triples, "graphs": graphs,
            "checks": {"pair_cases": len(cases), "form_cases": len(cases) * len(TRANSFORMS),
                       "triangle_cases": len(triples), "all_exact_checks_passed": True},
            "limitations": ["Only the principal supplied order lattices C/O_f are implemented.",
                            "Full Hom bases and their control sublattice indices are planted and certified algebraically.",
                            "Triangle consistency cannot certify completeness of an unknown Hom lattice.",
                            "No finite-field maps, map-discovery cost, performance advantage, or ECDLP consequence was measured."]}


def check_result(path: Path) -> None:
    stored = json.loads(path.read_text())
    expected = json.loads(json.dumps(run(stored["seed"])))
    if stored != expected:
        raise ValueError("result differs from the exact frozen fixtures; this checker is not independent research review")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    if args.check:
        check_result(args.check)
        print(json.dumps({"valid": True, "checker_scope": "exact fixture replay; independent review pending"}))
        return
    started = datetime.now(timezone.utc).isoformat()
    wall_start, cpu_start = time.monotonic(), time.process_time()
    result = run(args.seed)
    if args.output_dir:
        write_artifacts(result, args.output_dir, args.seed, started, wall_start, cpu_start)
    print(json.dumps(result["checks"]))


if __name__ == "__main__":
    main()
