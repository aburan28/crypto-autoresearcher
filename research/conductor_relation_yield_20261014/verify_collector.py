"""Independent Python replay and rank check for a prepared collector output.

This checks every reported relation. Completeness is checked separately by
test_collector.py on a fully enumerated small group.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from functools import lru_cache
from math import isqrt
from pathlib import Path

if not __debug__:
    raise RuntimeError("verification requires Python assertions enabled")


@dataclass(frozen=True)
class Curve:
    p: int
    a: int
    b: int
    r: int


@lru_cache(maxsize=None)
def is_prime_exact(value):
    if value < 2:
        return False
    if value in (2, 3):
        return True
    if value % 2 == 0 or value % 3 == 0:
        return False
    divisor = 5
    while divisor * divisor <= value:
        if value % divisor == 0 or value % (divisor + 2) == 0:
            return False
        divisor += 6
    return True


def certify_group(curve, generator):
    assert is_prime_exact(curve.p) and is_prime_exact(curve.r)
    assert (4 * curve.a**3 + 27 * curve.b**2) % curve.p != 0
    hasse_radius = isqrt(4 * curve.p)
    assert abs(curve.r - (curve.p + 1)) <= hasse_radius
    assert 2 * curve.r > curve.p + 1 + hasse_radius
    assert generator is not None and on_curve(generator, curve)
    assert multiply(curve.r, generator, curve) is None
    # The prime-order generator forces r | #E, and Hasse permits only r.


def negative(point, curve):
    return None if point is None else (point[0], (-point[1]) % curve.p)


def on_curve(point, curve):
    if point is None:
        return True
    x, y = point
    return 0 <= x < curve.p and 0 <= y < curve.p and (
        y * y - x**3 - curve.a * x - curve.b
    ) % curve.p == 0


def add(left, right, curve):
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % curve.p == 0:
        return None
    if left == right:
        slope = ((3 * x1 * x1 + curve.a) * pow(2 * y1, -1, curve.p)) % curve.p
    else:
        slope = ((y2 - y1) * pow(x2 - x1, -1, curve.p)) % curve.p
    x3 = (slope * slope - x1 - x2) % curve.p
    return x3, (slope * (x1 - x3) - y1) % curve.p


def multiply(scalar, point, curve):
    result = None
    while scalar:
        if scalar & 1:
            result = add(result, point, curve)
        point = add(point, point, curve)
        scalar >>= 1
    return result


def parse_input(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    h = lines[0].split()
    assert h[0] == "curve" and len(h) == 7
    curve = Curve(*map(int, h[1:5]))
    nbase, ntarget = map(int, h[5:])
    assert len(lines) == 1 + nbase + ntarget
    base = []
    for index, line in enumerate(lines[1 : 1 + nbase]):
        tag, point_id, x, y = line.split()
        assert tag == "base" and int(point_id) == index
        point = int(x), int(y)
        assert on_curve(point, curve)
        base.append(point)
    assert nbase % 2 == 0
    assert len({base[index][0] for index in range(0, nbase, 2)}) == nbase // 2
    for index in range(0, nbase, 2):
        assert base[index + 1] == negative(base[index], curve)
    targets = []
    seen = set()
    for index, line in enumerate(lines[1 + nbase :]):
        tag, target_id, alpha, beta, x, y = line.split()
        assert tag == "target" and int(target_id) == index
        alpha, beta = int(alpha), int(beta)
        point = int(x), int(y)
        assert 0 <= alpha < curve.r and 1 <= beta < curve.r
        assert point is not None and point not in seen and on_curve(point, curve)
        seen.add(point)
        targets.append((alpha, beta, point))
    return curve, base, targets


def column_layout(base, generator, q, curve):
    g_orbit = next((j for j in range(len(base) // 2) if base[2 * j][0] == generator[0]), None)
    g_log = None
    if g_orbit is not None:
        g_log = 1 if base[2 * g_orbit] == generator else -1
        assert base[2 * g_orbit] in (generator, negative(generator, curve))
    q_orbit = next((j for j in range(len(base) // 2) if base[2 * j][0] == q[0]), None)
    q_sign = None
    if q_orbit is not None:
        q_sign = 1 if base[2 * q_orbit] == q else -1
    columns = {}
    for j in range(len(base) // 2):
        if j != g_orbit:
            columns[j] = len(columns)
    q_column = len(columns) if q_orbit is None else None
    return g_orbit, g_log, q_orbit, q_sign, columns, q_column


def row_for(triple, alpha, beta, base, curve, layout):
    g_orbit, g_log, q_orbit, q_sign, columns, q_column = layout
    row = [0] * (len(columns) + (q_column is not None))
    rhs = alpha
    for point_id in triple:
        orbit = point_id // 2
        sign = 1 if point_id % 2 == 0 else -1
        if orbit == g_orbit:
            rhs -= sign * g_log
        else:
            row[columns[orbit]] += sign
    if q_orbit is None:
        row[q_column] -= beta
    elif q_orbit == g_orbit:
        rhs += beta * q_sign * g_log
    else:
        row[columns[q_orbit]] -= beta * q_sign
    return tuple(value % curve.r for value in row), rhs % curve.r


def add_rank(row, basis, modulus):
    vector = list(row)
    for pivot in sorted(basis):
        if vector[pivot]:
            factor = vector[pivot]
            reference = basis[pivot]
            vector = [(x - factor * y) % modulus for x, y in zip(vector, reference)]
    pivot = next((index for index, value in enumerate(vector) if value), None)
    if pivot is None:
        return False
    inverse = pow(vector[pivot], -1, modulus)
    basis[pivot] = [(value * inverse) % modulus for value in vector]
    return True


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify(input_path, output_path, generator, q, prefixes):
    curve, base, targets = parse_input(input_path)
    certify_group(curve, generator)
    assert q is not None and on_curve(q, curve)
    assert multiply(curve.r, q, curve) is None
    for alpha, beta, point in targets:
        assert point == add(multiply(alpha, generator, curve), multiply(beta, q, curve), curve)
    layout = column_layout(base, generator, q, curve)
    lines = Path(output_path).read_text(encoding="utf-8").splitlines()
    h = lines[0].split("\t")
    assert h == ["collector-v1", str(curve.p), str(curve.r), str(len(base)), str(len(targets))]
    summaries = {}
    triples = {}
    current = None
    for line in lines[1:]:
        fields = line.split("\t")
        if fields[0] == "target":
            assert len(fields) == 7
            index, alpha, beta, unordered, ordered, useful = map(int, fields[1:])
            assert index == len(summaries) and (alpha, beta) == targets[index][:2]
            summaries[index] = unordered, ordered, useful
            triples[index] = []
            current = index
        else:
            assert fields[0] == "triple" and len(fields) == 5
            index, i, j, k = map(int, fields[1:])
            assert index == current and 0 <= i <= j <= k < len(base)
            triples[index].append((i, j, k))
    assert len(summaries) == len(targets)
    basis = {}
    rank_prefix = {}
    useful_targets = 0
    total_triples = 0
    for index, (alpha, beta, point) in enumerate(targets):
        group = triples[index]
        assert group == sorted(set(group))
        unordered, ordered, useful = summaries[index]
        assert unordered == len(group)
        recomputed_ordered = 0
        recomputed_useful = 0
        for i, j, k in group:
            assert add(add(base[i], base[j], curve), base[k], curve) == point
            recomputed_ordered += 1 if i == k else 3 if i == j or j == k else 6
            if i != j and j != k and len({i // 2, j // 2, k // 2}) == 3:
                row, _rhs = row_for((i, j, k), alpha, beta, base, curve, layout)
                if any(row):
                    recomputed_useful += 1
                    add_rank(row, basis, curve.r)
        assert (ordered, useful) == (recomputed_ordered, recomputed_useful)
        useful_targets += useful > 0
        total_triples += unordered
        if index + 1 in prefixes:
            rank_prefix[index + 1] = len(basis)
    return {
        "schema": "arity3-independent-replay/v1",
        "status": "valid",
        "input_sha256": sha256(input_path),
        "output_sha256": sha256(output_path),
        "targets": len(targets),
        "useful_targets": useful_targets,
        "raw_unordered_triples": total_triples,
        "unknown_columns": len(layout[4]) + (layout[5] is not None),
        "rank_prefix": rank_prefix,
        "limits": "all reported triples and target equations replayed; full-size no-hit completeness is not independently established",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--gx", type=int, required=True)
    parser.add_argument("--gy", type=int, required=True)
    parser.add_argument("--qx", type=int, required=True)
    parser.add_argument("--qy", type=int, required=True)
    parser.add_argument("--prefixes", default="512,2048,8192,32768")
    args = parser.parse_args()
    receipt = verify(
        args.input, args.output, (args.gx, args.gy), (args.qx, args.qy),
        {int(value) for value in args.prefixes.split(",") if value},
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
