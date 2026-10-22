#!/usr/bin/env python3
"""Prospective all-core FROB object-arm re-enumeration, without the Sage driver.

Uses the archived checker's field/curve primitives and independent matrix,
membership, and tuple enumeration code. This does not complete C8 controls.
"""

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from math import isqrt, prod
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RUN = ROOT / "experiments/EXP-FROB-91ee9c/runs/TASK-20260914-7119f2"
SPLIT = HERE / "recheck_split.py"
OUTPUT = HERE / "core-object-replay.json"
CONFIG = {
    "FROB-SPLIT-q11n5": (11, [[2, 1], [6, 1], [7, 1], [8, 1]],
                          "x^5 + 2*x^4 + 1", ["x + 2", "x + 6", "x + 7", "x + 8"]),
    "FROB-NOLATTICE-q13n5": (13, [[1, 1, 1, 1, 1]],
                              "x^5 + 8*x^4 + 1", ["x^4 + x^3 + x^2 + x + 1"]),
    "FROB-EQDEG-q19n5": (19, [[1, 5, 1], [1, 15, 1]],
                          "x^5 + 3*x^4 + 1", ["x^2 + 5*x + 1", "x^2 + 15*x + 1"]),
}


def load_split():
    spec = importlib.util.spec_from_file_location("frob_split_audit", SPLIT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def matrix_mul(a, b, q):
    n = len(a)
    return [[sum(a[r][k] * b[k][c] for k in range(n)) % q
             for c in range(n)] for r in range(n)]


def poly_matrix(coefficients, matrix, q):
    n = len(matrix)
    result = [[0] * n for _ in range(n)]
    power = [[int(i == j) for j in range(n)] for i in range(n)]
    for coefficient in coefficients:
        for i in range(n):
            for j in range(n):
                result[i][j] = (result[i][j] + coefficient * power[i][j]) % q
        power = matrix_mul(power, matrix, q)
    return result


def kernel_basis(matrix, q):
    n = len(matrix)
    rows = [[x % q for x in row] for row in matrix]
    pivots = []
    rank = 0
    for c in range(n):
        pivot = next((i for i in range(rank, n) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = pow(rows[rank][c], -1, q)
        rows[rank] = [scale * x % q for x in rows[rank]]
        for i in range(n):
            if i != rank and rows[i][c]:
                factor = rows[i][c]
                rows[i] = [(a - factor * b) % q for a, b in zip(rows[i], rows[rank])]
        pivots.append(c)
        rank += 1
    free = [c for c in range(n) if c not in pivots]
    basis = []
    for f in free:
        vector = [0] * n
        vector[f] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -rows[row][f] % q
        assert all(sum(a * b for a, b in zip(row, vector)) % q == 0 for row in matrix)
        basis.append(vector)
    return basis


def coordinates(field, factors, split):
    q, n = field.q, field.n
    basis = [[int(i == j) for i in range(n)] for j in range(n)]
    frob_cols = [field.frobenius(v) for v in basis]
    frob = [[frob_cols[c][r] for c in range(n)] for r in range(n)]
    blocks = []
    for factor in ([q - 1, 1], *factors):
        block = kernel_basis(poly_matrix(factor, frob, q), q)
        assert len(block) == len(factor) - 1
        blocks.append(block)
    columns = [v for block in blocks for v in block]
    assert len(columns) == n
    matrix = [[columns[c][r] for c in range(n)] for r in range(n)]
    cinv = split.inverse(matrix, q)
    for c, v in enumerate(columns):
        cv = [sum(row[j] * v[j] for j in range(n)) % q for row in cinv]
        assert cv == [int(i == c) for i in range(n)]
    dims = [len(block) for block in blocks]
    return cinv, dims


def signature(x, cinv, dims, q):
    coords = [sum(row[j] * x[j] for j in range(len(x))) % q for row in cinv]
    offsets = [sum(dims[:i]) for i in range(len(dims))]
    nonzero = [any(coords[start:start + dim]) for start, dim in zip(offsets, dims)]
    return nonzero[0], sum(1 << i for i, present in enumerate(nonzero[1:]) if present)


def ratio(union_size, distinct, n_order, extra):
    f = (Fraction(union_size, 2) + 1 + extra) / Fraction(distinct, n_order - 1)
    return [f.numerator, f.denominator]


def replay_curve(curve, field, checker, split, cinv, dims):
    q, n = field.q, field.n
    n_order = curve["N"]
    A, B = curve["curve"]["A"], curve["curve"]["B"]
    ec = checker.EC(field, [A] + [0] * (n - 1), [B] + [0] * (n - 1))
    encoded = curve["curve"]["G_enc"]
    generator = (split.decode(encoded[0], q, n), split.decode(encoded[1], q, n))
    assert ec.on_curve(generator) and generator is not None
    assert n_order > 1 and all(n_order % d for d in range(2, isqrt(n_order) + 1))
    assert ec.scalar_mul(n_order, generator) is None
    mu = curve["curve"]["mu"]
    assert pow(mu, n, n_order) == 1
    assert all(pow(mu, j, n_order) != 1 for j in range(1, n))
    assert (field.frobenius(generator[0]), field.frobenius(generator[1])) == ec.scalar_mul(mu, generator)

    points = [None] * n_order
    by_mask = {}
    point = generator
    for k in range(1, n_order):
        points[k] = point
        v0, mask = signature(point[0], cinv, dims, q)
        if not v0:
            by_mask.setdefault(mask, []).append(k)
        point = ec.add(point, generator)
    assert point is None

    counts = {"ok": 0, "empty_base": 0}
    tuple_checks = 0
    multi_slot = 0
    for part in curve["object_arm_partitions"]:
        block_masks = [sum(1 << i for i in block) for block in part["partition_blocks"]]
        bases = [[k for mask, values in by_mask.items() if mask & ~bm == 0 for k in values]
                 for bm in block_masks]
        assert part["block_sizes"] == [len(base) for base in bases]
        if any(not base for base in bases):
            assert part["status"] == "empty_base"
            counts["empty_base"] += 1
            continue
        assert part["status"] == "ok"
        counts["ok"] += 1
        for base in bases:
            base_set = set(base)
            assert all((-k) % n_order in base_set for k in base)
        union = set().union(*(set(base) for base in bases))
        targets = set()
        for tup in itertools.product(*bases):
            target = sum(tup) % n_order
            point_sum = None
            for k in tup:
                point_sum = ec.add(point_sum, points[k])
            assert point_sum == points[target]
            if target:
                targets.add(target)
            tuple_checks += 1
            if len(tup) > 1:
                multi_slot += 1
        assert part["prod_tuple_count"] == prod(len(base) for base in bases)
        assert part["B_union_size"] == len(union)
        assert part["distinct_targets"] == len(targets)
        assert part["U_neg"] == [len(union), 2]
        assert part["p_m"] == [len(targets), n_order - 1]
        for extra in (0, 8, 32):
            assert part["cost_ratio_neg"][str(extra)] == {
                "denominator_zero": False,
                "value": ratio(len(union), len(targets), n_order, extra),
            }
    return {"N": n_order, "A": A, "B": B, "points_classified": n_order - 1,
            "partition_statuses": counts, "tuple_identities": tuple_checks,
            "multi_slot_sums": multi_slot}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    start = time.time()
    split = load_split()
    checker = split.load_checker()
    raw_by_cell = {record["cell"]: record["data"] for record in
                   (json.loads(line) for line in (RUN / "raw.jsonl").read_text().splitlines())}
    cells = []
    for cell_name, (q, factors, modulus, factor_strings) in CONFIG.items():
        raw = raw_by_cell[cell_name]
        assert raw["field_modulus"] == modulus
        assert raw["factorisation"]["atomic_factors"] == factor_strings
        field = checker.FQN(q, 5, checker.find_first_irreducible(q, 5))
        cinv, dims = coordinates(field, factors, split)
        curves = [replay_curve(c, field, checker, split, cinv, dims) for c in raw["curves"]]
        cells.append({"cell": cell_name, "q": q, "kernel_dimensions": dims, "curves": curves})
    all_curves = [curve for cell in cells for curve in cell["curves"]]
    totals = {
        "curves": len(all_curves),
        "points_classified": sum(c["points_classified"] for c in all_curves),
        "object_partitions": sum(sum(c["partition_statuses"].values()) for c in all_curves),
        "object_partitions_ok": sum(c["partition_statuses"]["ok"] for c in all_curves),
        "tuple_identities": sum(c["tuple_identities"] for c in all_curves),
        "multi_slot_sums": sum(c["multi_slot_sums"] for c in all_curves),
    }
    assert totals == {
        "curves": 6, "points_classified": 370100, "object_partitions": 36,
        "object_partitions_ok": 8, "tuple_identities": 20960, "multi_slot_sums": 400,
    }
    result = {
        "schema": "frob-c8-core-object-replay/v1",
        "source_run": "RUN-FROB-91ee9c-7119f2",
        "checker_sha256": hashlib.sha256((RUN / "checker.py").read_bytes()).hexdigest(),
        "raw_jsonl_sha256": hashlib.sha256((RUN / "raw.jsonl").read_bytes()).hexdigest(),
        "cells": cells,
        "totals": totals,
        "limit": "All three core object arms only; no C2/C3/C4 control-arm replay or original source custody",
    }
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
    elif OUTPUT.read_text() != serialized:
        print("core-object-replay.json is stale", file=sys.stderr)
        return 1
    else:
        print("FROB core object replay is byte-exact and current")
    print(f"elapsed_seconds={time.time() - start:.3f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
