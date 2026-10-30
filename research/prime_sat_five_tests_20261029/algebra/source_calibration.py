"""Ordinary homogeneous initial-segment matrix calibration, without rank guesses.

This reconstructs the mechanism specified by the authors' public slides and
algebraic_tools.sage. The full papers were unavailable (HTTP 403); no theorem
or published table is claimed reproduced. No third-party code is copied.
"""
from __future__ import annotations
import itertools


def monomials(n, degree):
    result = []
    for factors in itertools.combinations_with_replacement(range(n), degree):
        result.append(tuple(factors.count(i) for i in range(n)))
    return result


def rank_mod(rows, p):
    rows = [list(row) for row in rows]
    rank = 0
    operations = 0
    width = len(rows[0]) if rows else 0
    for col in range(width):
        pivot = next((j for j in range(rank, len(rows)) if rows[j][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, p)
        rows[rank] = [v * inv % p for v in rows[rank]]
        operations += width + 1
        for j in range(len(rows)):
            if j == rank or not rows[j][col]:
                continue
            c = rows[j][col]
            rows[j] = [(a - c * b) % p for a, b in zip(rows[j], rows[rank])]
            operations += 2 * width
        rank += 1
        if rank == len(rows):
            break
    return rank, operations, rows


def run_calibration(config):
    p = config["p"]
    equations = [{tuple(m): c % p for m, c in poly} for poly in config["polynomials"]]
    n = len(config["variables"])
    matrices = []
    for degree in range(2, config["max_degree"] + 1):
        multipliers = monomials(n, degree - 2)
        for prefix in range(1, len(multipliers) + 1):
            rows = []
            row_labels = []
            for mult in multipliers[:prefix]:
                for i, poly in enumerate(equations):
                    rows.append({tuple(a + b for a, b in zip(mon, mult)): c for mon, c in poly.items()})
                    row_labels.append([list(mult), i])
            columns = sorted(set().union(*(row.keys() for row in rows)))
            dense = [[row.get(mon, 0) for mon in columns] for row in rows]
            rank, operations, echelon = rank_mod(dense, p)
            matrices.append({"degree": degree, "prefix_multipliers": prefix,
                             "full_layer": prefix == len(multipliers),
                             "row_labels": row_labels, "columns": [list(m) for m in columns],
                             "matrix": dense, "rank": rank, "nullity": len(columns) - rank,
                             "counted_elimination_operations": operations, "rref": echelon})
    # Exhaustive projective oracle, including H=0, runs only after construction.
    points = []
    for values in itertools.product(range(p), repeat=n):
        first = next((i for i, v in enumerate(values) if v), None)
        if first is None or values[first] != 1:
            continue
        if all(sum(c * _monomial_eval(m, values, p) for m, c in poly.items()) % p == 0 for poly in equations):
            points.append(list(values))
    return {"status": "MATRIX_CONSTRUCTION_CALIBRATION", "p": p,
            "input": config, "matrices": matrices, "projective_models": points,
            "homogeneous_degrees_verified": all(sum(m) == 2 for poly in equations for m in poly),
            "source_algorithm_reproduction": False,
            "remaining_gap": "Full-paper assumptions and rank predictor reproduction; published multi-homogeneous XL algorithm and valid multi-homogenization of the target system are not implemented."}


def _monomial_eval(m, values, p):
    value = 1
    for power, x in zip(m, values):
        value = value * pow(x, power, p) % p
    return value
