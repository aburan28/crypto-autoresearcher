"""Exact quadratic lift of prime-field coset membership for the archived m=8 base.

The x^d = c constraint is represented by a fixed addition chain of equations
q_e - q_a*q_b = 0, plus q_d - c = 0. Semaev S3 chain equations and the
separating form are copied unchanged from the prime-field engine. This builds
and checks an input system; it does not run Groebner elimination or measure a
relation, rank, target logarithm, or ECDLP cost.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from crypto_autoresearcher.index_calculus.curve import Curve  # noqa: E402
from crypto_autoresearcher.index_calculus.factor_base import FactorBase  # noqa: E402
from crypto_autoresearcher.index_calculus.msolve import (  # noqa: E402
    System, decomposition_system, evaluate,
)
from tools.icperf_explicit_base import verify_base_record  # noqa: E402

FIXTURE = ROOT / "research/icperf_prime_fixtures_20261017/n63_seed20261017.json"
BASE = ROOT / "research/icperf_explicit_divisor_20261017/n63_m8_subgroup_seed20261017.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_chain(exponent: int) -> list[tuple[int, int, int]]:
    """Deterministic square-and-multiply chain (out, left, right)."""
    if exponent < 2:
        raise ValueError("exponent must be at least two")
    powers = {1}
    steps = []
    e = 1
    for bit in bin(exponent)[3:]:
        steps.append((2 * e, e, e))
        e *= 2
        powers.add(e)
        if bit == "1":
            steps.append((e + 1, e, 1))
            e += 1
            powers.add(e)
    assert e == exponent and len(powers) == len(steps) + 1
    return steps


def _term(nvars: int, variables: tuple[int, ...]) -> tuple[int, ...]:
    exponents = [0] * nvars
    for variable in variables:
        exponents[variable] += 1
    return tuple(exponents)


def lift_system(E: Curve, fb: FactorBase, xR: int, m: int, seed: int):
    """Replace m direct coset equations with exact quadratic gate systems."""
    if fb.kind != "subgroup" or m < 2:
        raise ValueError("needs a subgroup coset base and arity >= 2")
    d, g = fb.params["d"], fb.params["coset"]
    if (E.p - 1) % d:
        raise ValueError("coset order must divide p-1")
    direct = decomposition_system(E, fb, xR, m, random.Random(seed))
    chain = binary_chain(d)
    names = list(direct.names)
    indices = []
    for i in range(m):
        by_exponent = {1: i}
        for out, _, _ in chain:
            by_exponent[out] = len(names)
            names.append(f"q{i + 1}_{out}")
        indices.append(by_exponent)
    nv, p = len(names), E.p
    polys = []
    for i in range(m):
        by_exponent = indices[i]
        for out, left, right in chain:
            z, a, b = (by_exponent[e] for e in (out, left, right))
            polys.append({_term(nv, (z,)): 1,
                          _term(nv, (a, b)): p - 1})
        polys.append({_term(nv, (by_exponent[d],)): 1,
                      _term(nv, ()): -pow(g, d, p) % p})
    polys.extend({exps + (0,) * (nv - len(direct.names)): c for exps, c in poly.items()}
                 for poly in direct.polys[m:])
    return System(names, polys, p, m), direct, chain, indices


def planted_values(E: Curve, fb: FactorBase, system: System, direct: System,
                   chain: list[tuple[int, int, int]], indices: list[dict[int, int]], m: int):
    """A known-point chain with independently added partial sums."""
    points = fb.points[:m]
    if len(points) != m:
        raise ValueError("base has fewer points than the requested arity")
    sums = []
    total = None
    independent = Curve(E.p, E.a, E.b, E.order)
    for point in points:
        assert independent.is_on_curve(point)
        total = independent.add(total, point)
        if total is None:
            raise ValueError("planted partial sum reaches infinity")
        sums.append(total)
    values = [0] * len(system.names)
    for i, point in enumerate(points):
        values[i] = point[0]
    for k in range(m - 2):
        values[m + k] = sums[k + 1][0]
    z_index = 2 * m - 2
    values[z_index] = -evaluate(direct.polys[-1], values[:len(direct.names)], E.p) % E.p
    for i in range(m):
        for out, left, right in chain:
            values[indices[i][out]] = (values[indices[i][left]]
                                       * values[indices[i][right]]) % E.p
    assert all(evaluate(poly, values, E.p) == 0 for poly in system.polys)
    assert all(evaluate(poly, values[:len(direct.names)], E.p) == 0
               for poly in direct.polys)
    return points, sums[-1], values


def serialize(system: System) -> dict:
    """Sparse monomial representation, with exact coefficients modulo p."""
    equations = []
    for poly in system.polys:
        equations.append([{"coefficient": int(coefficient),
                           "powers": [[i, power] for i, power in enumerate(exponents) if power]}
                          for exponents, coefficient in sorted(poly.items())])
    return {"variables": system.names, "equations": equations,
            "variable_count": len(system.names), "equation_count": len(system.polys),
            "monomial_occurrences": sum(len(poly) for poly in system.polys),
            "max_total_degree": max(sum(exponents) for poly in system.polys
                                    for exponents in poly)}


def build_record(m: int = 8, seed: int = 20261017) -> dict:
    fixture, base_record = json.loads(FIXTURE.read_bytes()), json.loads(BASE.read_bytes())
    verify_base_record(base_record, FIXTURE)
    curve = fixture["curve"]
    E = Curve(curve["p"], curve["a"], curve["b"], curve["order"])
    fb = FactorBase("subgroup", [tuple(point) for point in base_record["points"]],
                    dict(base_record["base_parameters"]), E.p)
    target = None
    for point in fb.points[:m]:
        target = E.add(target, point)
        if target is None:
            raise ValueError("planted target reaches infinity")
    lifted, direct, chain, indices = lift_system(E, fb, target[0], m, seed)
    points, checked_target, values = planted_values(E, fb, lifted, direct, chain, indices, m)
    assert checked_target == target
    # The field coset is larger than the curve-liftable factor base.
    d, g, zeta = (fb.params[k] for k in ("d", "coset", "zeta"))
    coset = {g * pow(zeta, j, E.p) % E.p for j in range(d)}
    accepted = {point[0] for point in fb.points}
    assert len(coset) == d and accepted <= coset
    rejected_lifts = sorted(coset - accepted)
    assert all(E.lift_x(x) is None for x in rejected_lifts)
    corrupt = values[:]
    corrupt[indices[0][chain[0][0]]] = (corrupt[indices[0][chain[0][0]]] + 1) % E.p
    assert any(evaluate(poly, corrupt, E.p) != 0 for poly in lifted.polys)
    lifted_data, direct_data = serialize(lifted), serialize(direct)
    grid = []
    grid_target = None
    for arity in range(2, 9):
        if arity == 2:
            grid_target = E.add(fb.points[0], fb.points[1])
        else:
            grid_target = E.add(grid_target, fb.points[arity - 1])
        if grid_target is None:
            raise ValueError("grid partial target reaches infinity")
        grid_lifted, grid_direct, _, _ = lift_system(E, fb, grid_target[0], arity, seed)
        grid.append({"m": arity, "planted_target_x": grid_target[0],
                     "direct": {k: serialize(grid_direct)[k] for k in
                                ("variable_count", "equation_count", "monomial_occurrences",
                                 "max_total_degree")},
                     "lifted": {k: serialize(grid_lifted)[k] for k in
                                ("variable_count", "equation_count", "monomial_occurrences",
                                 "max_total_degree")}})
    return {"schema": "icperf-prime-coset-quadratic-v1",
            "scope": "exact planted input equivalence and support; no Groebner run or ECDLP speed claim",
            "source_sha256": sha(Path(__file__)), "fixture_sha256": sha(FIXTURE),
            "base_sha256": sha(BASE), "base_point_sha256": base_record["point_sha256"],
            "curve": curve, "m": m, "seed": seed, "factor_base_size": len(fb),
            "coset_order": d, "coset_constant": pow(g, d, E.p),
            "coset_x_count": len(coset), "nonliftable_coset_x_count": len(rejected_lifts),
            "addition_chain": [{"out": out, "left": left, "right": right}
                               for out, left, right in chain],
            "arity_grid_input_counts": grid,
            "direct": direct_data, "lifted": lifted_data,
            "planted_input_points": [list(point) for point in points],
            "planted_target": list(target), "planted_assignment": values,
            "controls": {"all_direct_equations_zero": True,
                         "all_lifted_equations_zero": True,
                         "one_changed_auxiliary_rejected": True,
                         "all_nonliftable_coset_x_checked": True}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m", type=int, default=8, choices=range(2, 9))
    parser.add_argument("--seed", type=int, default=20261017)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build_record(args.m, args.seed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"m": args.m, "variables": result["lifted"]["variable_count"],
                      "equations": result["lifted"]["equation_count"],
                      "monomials": result["lifted"]["monomial_occurrences"]}, sort_keys=True))


if __name__ == "__main__":
    main()
