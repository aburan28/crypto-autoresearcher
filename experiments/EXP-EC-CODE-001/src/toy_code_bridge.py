#!/usr/bin/env python3
"""Exact, fixed-size toy check of elliptic relations and sparse codewords.

Standard library only. This enumerates a 991-point toy group, NOT a
cryptographic-sized instance. It checks an established Riemann--Roch
correspondence; it is not a faster-than-rho algorithm or benchmark.

Run: python toy_code_bridge.py --output toy_results.json
"""
from __future__ import annotations
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from math import isqrt
from random import Random

P = 1009
A = 2
B = 25
Point = tuple[int, int] | None


def is_prime(n: int) -> bool:
    return n >= 2 and all(n % d for d in range(2, isqrt(n) + 1))


def add(u: Point, v: Point) -> Point:
    if u is None:
        return v
    if v is None:
        return u
    x, y = u
    z, w = v
    if x == z and (y + w) % P == 0:
        return None
    if u == v:
        slope = (3*x*x + A) * pow(2*y, -1, P) % P
    else:
        slope = (w-y) * pow((z-x) % P, -1, P) % P
    nx = (slope*slope-x-z) % P
    return nx, (slope*(x-nx)-y) % P


def neg(u: Point) -> Point:
    return None if u is None else (u[0], -u[1] % P)


def rref(matrix: list[list[int]], modulus: int) -> tuple[list[list[int]], list[int]]:
    if not matrix:
        return [], []
    ncols = len(matrix[0])
    if any(len(row) != ncols for row in matrix):
        raise ValueError('Ragged matrix')
    rows = [[x % modulus for x in row] for row in matrix]
    pivots: list[int] = []
    r = 0
    for c in range(ncols):
        k = next((k for k in range(r, len(rows)) if rows[k][c]), None)
        if k is None:
            continue
        rows[r], rows[k] = rows[k], rows[r]
        inv = pow(rows[r][c], -1, modulus)
        rows[r] = [(v*inv) % modulus for v in rows[r]]
        for k in range(len(rows)):
            if k != r and rows[k][c]:
                t = rows[k][c]
                rows[k] = [(x-t*y) % modulus for x, y in zip(rows[k], rows[r])]
        pivots.append(c)
        r += 1
        if r == len(rows):
            break
    return rows, pivots


def rank(matrix: list[list[int]], modulus: int) -> int:
    return len(rref(matrix, modulus)[1])


def nullspace(matrix: list[list[int]], modulus: int) -> list[list[int]]:
    reduced, pivots = rref(matrix, modulus)
    if not matrix:
        raise ValueError('Need a nonempty matrix')
    out = []
    for c in range(len(matrix[0])):
        if c in pivots:
            continue
        v = [0] * len(matrix[0])
        v[c] = 1
        for r, pivot in enumerate(pivots):
            v[pivot] = -reduced[r][c] % modulus
        out.append(v)
    return out


def evaluation_matrix(points: list[tuple[int, int]]) -> list[list[int]]:
    return [[1 for x, y in points], [x for x, y in points],
            [y for x, y in points], [x*x % P for x, y in points]]


def square_dimension(rows: list[list[int]]) -> int:
    products = [[x*y % P for x, y in zip(rows[i], rows[j])]
                for i in range(len(rows)) for j in range(i, len(rows))]
    return rank(products, P)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    assert is_prime(P) and (4*A**3 + 27*B**2) % P
    roots: dict[int, list[int]] = {}
    for y in range(P):
        roots.setdefault(y*y % P, []).append(y)
    points = [(x, y) for x in range(P)
              for y in roots.get((x*x*x + A*x + B) % P, [])]
    order = len(points) + 1
    assert order == 991 and is_prime(order)
    # Coordinate-only construction: one sign per x, no point logarithms.
    base = [(x, ys[0]) for x in range(P)
            if (ys := roots.get((x*x*x + A*x + B) % P, []))][:32]
    v = evaluation_matrix(base)
    pair_sums = {(i, j): add(base[i], base[j])
                 for i, j in combinations(range(len(base)), 2)}
    relation_rows: list[list[int]] = []
    supports: list[tuple[int, ...]] = []
    tested = 0
    for inds in combinations(range(len(base)), 4):
        tested += 1
        sub = [[row[i] for i in inds] for row in v]
        singular = rank(sub, P) < 4
        i, j, k, l = inds
        group_relation = add(pair_sums[i, j], pair_sums[k, l]) is None
        assert singular == group_relation, ('correspondence mismatch', inds)
        if singular:
            supports.append(inds)
            relation_rows.append([int(i in inds) for i in range(len(base))])
    assert supports
    first = supports[0]
    sub = [[row[i] for i in first] for row in v]
    codeword = nullspace(sub, P)[0]
    assert all(codeword)
    function = nullspace(list(map(list, zip(*sub))), P)[0]
    # Display a polynomial with y coefficient one when possible.
    if function[2]:
        s = pow(function[2], -1, P)
        function = [s*c % P for c in function]
    assert all(sum(function[r]*sub[r][c] for r in range(4)) % P == 0
               for c in range(4))
    # Independent coordinate-chosen target; no preconstructed decomposition.
    target = points[350]
    assert target not in base and neg(target) not in base
    target_supports = []
    target_trials = 0
    totals = Counter()
    for inds in combinations(range(len(base)), 3):
        i, j, k = inds
        s = add(pair_sums[i, j], base[k])
        totals[s] += 1
        candidates = [base[i], base[j], base[k], neg(target)]
        assert all(point is not None for point in candidates)
        singular = rank(evaluation_matrix(candidates), P) < 4
        assert singular == (s == target), ('target mismatch', inds)
        target_trials += 1
        if singular:
            target_supports.append(inds)
    shortening_profiles = {}
    # Shortening: retain functions vanishing at selected evaluation points.
    # Keeping their forced-zero coordinates does not affect these ranks.
    for size in (1, 2, 3):
        dimensions = Counter()
        for inds in combinations(range(len(base)), size):
            constraints = [[row[i] for row in v] for i in inds]
            coefficients = nullspace(constraints, P)
            shortened = [[sum(c[r]*v[r][j] for r in range(4)) % P
                          for j in range(len(base))] for c in coefficients]
            dimensions[(len(coefficients), square_dimension(shortened))] += 1
        shortening_profiles[str(size)] = [
            {'dimension': d, 'schur_square_dimension': sq, 'subsets': count}
            for (d, sq), count in sorted(dimensions.items())
        ]
    rng = Random(20260907)
    random_matrix = [[rng.randrange(P) for _ in base] for _ in range(4)]
    relation_rank = rank(relation_rows, order)
    assert relation_rank <= len(base)-1
    assert relation_rank == len(base)-1 and target_supports
    log_basis = nullspace(relation_rows, order)
    assert len(log_basis) == 1 and log_basis[0][0]
    normalizer = pow(log_basis[0][0], -1, order)
    recovered_logs = [x*normalizer % order for x in log_basis[0]]
    target_logs = {sum(recovered_logs[i] for i in inds) % order
                   for inds in target_supports}
    assert len(target_logs) == 1
    target_log = next(iter(target_logs))
    check = None
    running = base[0]
    scalar = target_log
    while scalar:
        if scalar & 1:
            check = add(check, running)
        running = add(running, running)
        scalar >>= 1
    assert check == target
    report = {
        'scope': 'Fixed toy identity check, not a speedup claim.',
        'curve': {'p': P, 'a': A, 'b': B, 'group_order': order},
        'base_rule': 'First 32 increasing x with a point; choose smaller y root.',
        'factor_base': base,
        'four_subsets_checked': tested,
        'singular_four_subsets': len(supports),
        'correspondence_mismatches': 0,
        'relation_matrix_rank_mod_group_order': relation_rank,
        'maximum_possible_factor_only_rank': len(base)-1,
        'first_relation': {
            'indices_zero_based': first,
            'points': [base[i] for i in first],
            'evaluation_matrix_rows_1_x_y_x2': sub,
            'kernel_vector_mod_p': codeword,
            'function_coefficients_1_x_y_x2': function,
        },
        'row_code_dimension': rank(v, P),
        'row_code_schur_square_dimension': square_dimension(v),
        'random_comparator_dimension': rank(random_matrix, P),
        'random_comparator_schur_square_dimension': square_dimension(random_matrix),
        'shortening_profiles': shortening_profiles,
        'toy_log_recovery': {
            'generator': base[0],
            'recovered_factor_logs': recovered_logs,
            'recovered_target_log': target_log,
            'verified_by_scalar_multiplication': True,
            'used_only_factor_relations_and_target_decompositions': True,
        },
        'target': target,
        'target_three_subsets_checked': target_trials,
        'target_decompositions': [[base[i] for i in inds] for inds in target_supports],
        'target_correspondence_mismatches': 0,
        'distinct_three_subset_sums': len(totals),
        'number_of_subsets_per_target_histogram': {
            str(k): value for k, value in sorted(
                Counter(totals.get(t, 0) for t in [None]+points).items())
        },
    }
    text = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text+'\n', encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
