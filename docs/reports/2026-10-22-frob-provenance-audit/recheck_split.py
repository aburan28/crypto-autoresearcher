#!/usr/bin/env python3
"""Independent object-arm replay for the frozen FROB-SPLIT-q11n5 cell.

Uses the archived checker field/curve primitives, not the Sage driver or its
enumeration code. This bounded replay is not a C8 completion certificate.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
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
OUTPUT = HERE / "split-object-replay.json"
CELL = "FROB-SPLIT-q11n5"
Q, DEGREE = 11, 5


def load_checker():
    path = RUN / "checker.py"
    spec = importlib.util.spec_from_file_location("frob_frozen_checker", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def decode(encoded: int, q: int, n: int) -> list[int]:
    out = []
    for _ in range(n):
        out.append(encoded % q)
        encoded //= q
    assert encoded == 0
    return out


def null_vector(matrix: list[list[int]], q: int) -> list[int]:
    n = len(matrix)
    rows = [[x % q for x in row] for row in matrix]
    pivots = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, n) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        scale = pow(rows[r][c], -1, q)
        rows[r] = [scale * x % q for x in rows[r]]
        for i in range(n):
            if i != r and rows[i][c]:
                factor = rows[i][c]
                rows[i] = [(a - factor * b) % q for a, b in zip(rows[i], rows[r])]
        pivots.append(c)
        r += 1
    free = [c for c in range(n) if c not in pivots]
    assert len(free) == 1, (pivots, free)
    vector = [0] * n
    vector[free[0]] = 1
    for row, pivot in enumerate(pivots):
        vector[pivot] = -sum(rows[row][c] * vector[c] for c in free) % q
    assert all(sum(a * b for a, b in zip(row, vector)) % q == 0 for row in matrix)
    return vector


def inverse(matrix: list[list[int]], q: int) -> list[list[int]]:
    n = len(matrix)
    rows = [row[:] + [int(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for c in range(n):
        pivot = next(i for i in range(c, n) if rows[i][c] % q)
        rows[c], rows[pivot] = rows[pivot], rows[c]
        scale = pow(rows[c][c], -1, q)
        rows[c] = [scale * x % q for x in rows[c]]
        for i in range(n):
            if i != c and rows[i][c]:
                factor = rows[i][c]
                rows[i] = [(a - factor * b) % q for a, b in zip(rows[i], rows[c])]
    assert all(rows[i][j] == int(i == j) for i in range(n) for j in range(n))
    return [row[n:] for row in rows]


def coordinate_matrix(field) -> list[list[int]]:
    n = field.n
    basis = [[int(i == j) for i in range(n)] for j in range(n)]
    frob_cols = [field.frobenius(v) for v in basis]
    frob = [[frob_cols[c][r] for c in range(n)] for r in range(n)]
    nontrivial_roots = [(-constant) % field.q for constant in (2, 6, 7, 8)]
    assert set(nontrivial_roots) == {r for r in range(2, field.q) if pow(r, n, field.q) == 1}
    roots = [1, *nontrivial_roots]
    eigenvectors = []
    for root in roots:
        mat = [[(frob[i][j] - (root if i == j else 0)) % field.q
                for j in range(n)] for i in range(n)]
        eigenvectors.append(null_vector(mat, field.q))
    columns = [[eigenvectors[c][r] for c in range(n)] for r in range(n)]
    cinv = inverse(columns, field.q)
    for c, eigenvector in enumerate(eigenvectors):
        coordinates = [sum(row[j] * eigenvector[j] for j in range(n)) % field.q
                       for row in cinv]
        assert coordinates == [int(i == c) for i in range(n)]
    return cinv


def signature(x: list[int], cinv: list[list[int]], q: int) -> tuple[bool, int]:
    coordinates = [sum(row[j] * x[j] for j in range(len(x))) % q for row in cinv]
    mask = sum(1 << i for i, value in enumerate(coordinates[1:]) if value)
    return coordinates[0] != 0, mask


def ratio(union_size: int, distinct: int, n_order: int, extra: int) -> list[int]:
    value = (Fraction(union_size, 2) + 1 + extra) / Fraction(distinct, n_order - 1)
    return [value.numerator, value.denominator]


def first_ok(curve: dict) -> dict:
    return next(p for p in curve["object_arm_partitions"] if p["status"] == "ok")


def replay_curve(curve: dict, field, checker, cinv: list[list[int]]) -> dict:
    n_order = curve["N"]
    A, B = curve["curve"]["A"], curve["curve"]["B"]
    ec = checker.EC(field, [A] + [0] * 4, [B] + [0] * 4)
    encoded = curve["curve"]["G_enc"]
    generator = (decode(encoded[0], Q, DEGREE), decode(encoded[1], Q, DEGREE))
    assert ec.on_curve(generator)
    assert ec.scalar_mul(n_order, generator) is None
    assert n_order > 1 and all(n_order % d for d in range(2, isqrt(n_order) + 1))
    mu = curve["curve"]["mu"]
    assert pow(mu, DEGREE, n_order) == 1
    assert all(pow(mu, j, n_order) != 1 for j in range(1, DEGREE))
    frob = (field.frobenius(generator[0]), field.frobenius(generator[1]))
    assert frob == ec.scalar_mul(mu, generator)

    points = [None] * n_order
    by_mask: dict[int, list[int]] = {}
    point = generator
    for k in range(1, n_order):
        points[k] = point
        v0, mask = signature(point[0], cinv, Q)
        if not v0:
            by_mask.setdefault(mask, []).append(k)
        point = ec.add(point, generator)
    assert point is None

    outcome_counts = {"ok": 0, "empty_base": 0}
    tuple_checks = 0
    for partition in curve["object_arm_partitions"]:
        block_masks = [sum(1 << i for i in block) for block in partition["partition_blocks"]]
        bases = [[k for mask, values in by_mask.items() if mask & ~block_mask == 0
                  for k in values] for block_mask in block_masks]
        assert partition["block_sizes"] == [len(base) for base in bases]
        if any(not base for base in bases):
            assert partition["status"] == "empty_base"
            outcome_counts["empty_base"] += 1
            continue
        assert partition["status"] == "ok"
        outcome_counts["ok"] += 1
        assert all((-k) % n_order in set(base) for base in bases for k in base)
        union = set().union(*(set(base) for base in bases))
        targets = set()
        for tup in itertools.product(*bases):
            target = sum(tup) % n_order
            signed_sum = None
            for k in tup:
                signed_sum = ec.add(signed_sum, points[k])
            assert signed_sum == points[target]
            if target:
                targets.add(target)
            tuple_checks += 1
        assert partition["prod_tuple_count"] == prod(len(base) for base in bases)
        assert partition["B_union_size"] == len(union)
        assert partition["distinct_targets"] == len(targets)
        assert partition["U_neg"] == [len(union), 2]
        assert partition["p_m"] == [len(targets), n_order - 1]
        for extra in (0, 8, 32):
            assert partition["cost_ratio_neg"][str(extra)] == {
                "denominator_zero": False,
                "value": ratio(len(union), len(targets), n_order, extra),
            }
    return {
        "N": n_order,
        "A": A,
        "B": B,
        "object_partition_status_counts": outcome_counts,
        "signed_point_tuple_checks": tuple_checks,
        "classified_subgroup_points": n_order - 1,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    start = time.time()
    checker = load_checker()
    raw = next(json.loads(line)["data"] for line in (RUN / "raw.jsonl").read_text().splitlines()
               if json.loads(line)["cell"] == CELL)
    g = checker.find_first_irreducible(Q, DEGREE)
    assert g == [1, 0, 0, 0, 2, 1]
    assert raw["field_modulus"] == "x^5 + 2*x^4 + 1"
    assert raw["factorisation"]["atomic_factors"] == ["x + 2", "x + 6", "x + 7", "x + 8"]
    field = checker.FQN(Q, DEGREE, g)
    cinv = coordinate_matrix(field)
    curves = [replay_curve(curve, field, checker, cinv) for curve in raw["curves"]]
    mutants = {}
    for name, mutate in (
        ("wrong_distinct_target_count", lambda c: first_ok(c).__setitem__(
            "distinct_targets", first_ok(c)["distinct_targets"] + 1)),
        ("wrong_slot_size", lambda c: first_ok(c)["block_sizes"].__setitem__(
            0, first_ok(c)["block_sizes"][0] + 1)),
        ("wrong_generator_x", lambda c: c["curve"]["G_enc"].__setitem__(
            0, c["curve"]["G_enc"][0] + 1)),
    ):
        changed = deepcopy(raw["curves"][1])
        mutate(changed)
        try:
            replay_curve(changed, field, checker, cinv)
        except AssertionError:
            mutants[name] = "rejected"
        else:
            raise AssertionError(f"mutation was accepted: {name}")
    receipt = {
        "schema": "frob-c8-split-object-pilot/v1",
        "source_run": "RUN-FROB-91ee9c-7119f2",
        "cell": CELL,
        "checker_sha256": hashlib.sha256((RUN / "checker.py").read_bytes()).hexdigest(),
        "raw_jsonl_sha256": hashlib.sha256((RUN / "raw.jsonl").read_bytes()).hexdigest(),
        "curves": curves,
        "negative_controls": mutants,
        "limit": "Object arm only in q11n5; no C2/C3/C4 replay and no other cell",
    }
    serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.write:
        OUTPUT.write_text(serialized)
        print(f"wrote {OUTPUT.relative_to(ROOT)}")
    elif OUTPUT.read_text() != serialized:
        print("split-object-replay.json is stale", file=sys.stderr)
        return 1
    else:
        print("FROB split object replay is byte-exact and current")
    print(f"elapsed_seconds={time.time() - start:.3f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
