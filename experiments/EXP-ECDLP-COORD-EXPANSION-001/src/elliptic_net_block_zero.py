#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import platform
import resource
import statistics
import sys
import time
from pathlib import Path
from typing import Any, Sequence


SCRIPT_PATH = Path(__file__).resolve()
NORM_SOURCE = SCRIPT_PATH.with_name("typed_s4_norm_rank.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


NORM = load_module("typed_s4_norm_for_block_zero", NORM_SOURCE)
TYPED = NORM.TYPED_EC
TT = NORM.TT
Point = tuple[int, int] | None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def deterministic_values(label: str, count: int, p: int) -> list[int]:
    return [
        int.from_bytes(
            hashlib.sha256(f"{label}|{index}".encode("ascii")).digest(),
            "big",
        )
        % p
        for index in range(count)
    ]


def berlekamp_massey(sequence: Sequence[int], p: int) -> list[int]:
    connection = [1]
    prior = [1]
    order = 0
    shift = 1
    prior_discrepancy = 1
    for n in range(len(sequence)):
        discrepancy = sequence[n] % p
        for index in range(1, order + 1):
            discrepancy = (
                discrepancy
                + connection[index] * sequence[n - index]
            ) % p
        if discrepancy == 0:
            shift += 1
            continue
        old = list(connection)
        scale = discrepancy * pow(prior_discrepancy, -1, p) % p
        required = len(prior) + shift
        if len(connection) < required:
            connection.extend([0] * (required - len(connection)))
        for index, value in enumerate(prior):
            connection[index + shift] = (
                connection[index + shift] - scale * value
            ) % p
        if 2 * order <= n:
            order = n + 1 - order
            prior = old
            prior_discrepancy = discrepancy
            shift = 1
        else:
            shift += 1
    return connection[: order + 1]


def recurrence_violations(
    sequence: Sequence[int],
    connection: Sequence[int],
    p: int,
    start: int | None = None,
) -> int:
    order = len(connection) - 1
    first = order if start is None else max(order, start)
    return sum(
        (
            sequence[n]
            + sum(
                connection[index] * sequence[n - index]
                for index in range(1, order + 1)
            )
        )
        % p
        != 0
        for n in range(first, len(sequence))
    )


def train_test_recurrence(
    sequence: Sequence[int], p: int
) -> dict[str, Any]:
    split = max(2, (2 * len(sequence)) // 3)
    connection = berlekamp_massey(sequence[:split], p)
    order = len(connection) - 1
    held_out_terms = max(0, len(sequence) - max(split, order))
    held_out_violations = recurrence_violations(
        sequence, connection, p, split
    )
    return {
        "train_length": split,
        "order": order,
        "connection_digest": canonical_digest(connection),
        "train_violations": recurrence_violations(
            sequence[:split], connection, p
        ),
        "held_out_terms": held_out_terms,
        "held_out_violations": held_out_violations,
        "held_out_exact": held_out_terms > 0 and held_out_violations == 0,
    }


def solve_linear_system(
    rows: list[list[int]], width: int, p: int
) -> tuple[list[int] | None, int]:
    matrix = [[value % p for value in row] for row in rows]
    pivots: list[int] = []
    cursor = 0
    for column in range(width):
        pivot = next(
            (
                row
                for row in range(cursor, len(matrix))
                if matrix[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        matrix[cursor], matrix[pivot] = matrix[pivot], matrix[cursor]
        inverse = pow(matrix[cursor][column], -1, p)
        matrix[cursor] = [
            value * inverse % p for value in matrix[cursor]
        ]
        for row in range(len(matrix)):
            if row == cursor or matrix[row][column] == 0:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                (value - factor * base) % p
                for value, base in zip(matrix[row], matrix[cursor])
            ]
        pivots.append(column)
        cursor += 1
        if cursor == len(matrix):
            break
    if any(
        all(row[column] == 0 for column in range(width))
        and row[width] != 0
        for row in matrix
    ):
        return None, len(pivots)
    solution = [0] * width
    for row, column in enumerate(pivots):
        solution[column] = matrix[row][width]
    return solution, len(pivots)


def fit_somos4(sequence: Sequence[int], p: int) -> dict[str, Any]:
    rows = []
    for index in range(len(sequence) - 4):
        rows.append(
            [
                sequence[index + 3] * sequence[index + 1] % p,
                sequence[index + 2] ** 2 % p,
                sequence[index + 4] * sequence[index] % p,
            ]
        )
    coefficients, rank = solve_linear_system(rows, 2, p)
    if coefficients is None:
        return {
            "fit_exists": False,
            "equations": len(rows),
            "rank": rank,
            "violations": len(rows),
            "exact": False,
        }
    alpha, beta = coefficients
    violations = sum(
        (alpha * row[0] + beta * row[1] - row[2]) % p != 0
        for row in rows
    )
    return {
        "fit_exists": True,
        "equations": len(rows),
        "rank": rank,
        "alpha": alpha,
        "beta": beta,
        "violations": violations,
        "exact": bool(rows) and violations == 0,
    }


def planted_linear_sequence(
    p: int, length: int, order: int, label: str
) -> tuple[list[int], list[int]]:
    values = deterministic_values(f"{label}|initial", order, p)
    coefficients = [
        value or 1
        for value in deterministic_values(
            f"{label}|coefficients", order, p
        )
    ]
    while len(values) < length:
        values.append(
            -sum(
                coefficients[index] * values[-index - 1]
                for index in range(order)
            )
            % p
        )
    return values, [1, *coefficients]


def division_polynomial_sequence(
    p: int,
    a: int,
    b: int,
    point: Point,
    length: int,
) -> list[int]:
    if point is None:
        raise ValueError("EDS control requires an affine point")
    x, y = point
    psi2 = 2 * y % p
    if psi2 == 0:
        raise ValueError("EDS control requires nonzero 2y")
    memo = {
        0: 0,
        1: 1,
        2: psi2,
        3: (
            3 * x**4
            + 6 * a * x**2
            + 12 * b * x
            - a**2
        )
        % p,
        4: (
            4
            * y
            * (
                x**6
                + 5 * a * x**4
                + 20 * b * x**3
                - 5 * a**2 * x**2
                - 4 * a * b * x
                - 8 * b**2
                - a**3
            )
        )
        % p,
    }

    def psi(index: int) -> int:
        if index in memo:
            return memo[index]
        half = index // 2
        if index % 2:
            value = (
                psi(half + 2) * pow(psi(half), 3, p)
                - psi(half - 1) * pow(psi(half + 1), 3, p)
            ) % p
        else:
            value = (
                psi(half)
                * pow(psi2, -1, p)
                * (
                    psi(half + 2) * pow(psi(half - 1), 2, p)
                    - psi(half - 2) * pow(psi(half + 1), 2, p)
                )
            ) % p
        memo[index] = value
        return value

    return [psi(index) for index in range(length)]


def ward_violations(sequence: Sequence[int], p: int) -> int:
    if len(sequence) < 7:
        return 0
    w2_squared = sequence[2] ** 2 % p
    w3 = sequence[3]
    return sum(
        (
            sequence[index + 2] * sequence[index - 2]
            - sequence[index + 1]
            * sequence[index - 1]
            * w2_squared
            + w3 * sequence[index] ** 2
        )
        % p
        != 0
        for index in range(2, len(sequence) - 2)
    )


def controls(
    p: int, a: int, b: int, point: Point, length: int
) -> dict[str, Any]:
    linear, planted_connection = planted_linear_sequence(
        p, length, 4, "ELLIPTIC-NET-BLOCK-ZERO|LINEAR"
    )
    linear_connection = berlekamp_massey(linear, p)
    eds = division_polynomial_sequence(p, a, b, point, length)
    random_sequence = deterministic_values(
        "ELLIPTIC-NET-BLOCK-ZERO|RANDOM", length, p
    )
    factors = [
        planted_linear_sequence(
            p,
            length,
            2,
            f"ELLIPTIC-NET-BLOCK-ZERO|FACTOR|{index}",
        )[0]
        for index in range(6)
    ]
    product = [
        math.prod(factor[index] for factor in factors) % p
        for index in range(length)
    ]
    return {
        "planted_linear": {
            "planted_order": 4,
            "recovered_order": len(linear_connection) - 1,
            "recovered_violations": recurrence_violations(
                linear, linear_connection, p
            ),
            "planted_violations": recurrence_violations(
                linear, planted_connection, p
            ),
            "train_test": train_test_recurrence(linear, p),
        },
        "elliptic_divisibility": {
            "length": len(eds),
            "ward_violations": ward_violations(eds, p),
            "somos4": fit_somos4(eds, p),
            "bm_order": len(berlekamp_massey(eds, p)) - 1,
            "sequence_digest": canonical_digest(eds),
        },
        "deterministic_random": {
            "bm_order": len(berlekamp_massey(random_sequence, p)) - 1,
            "somos4": fit_somos4(random_sequence, p),
        },
        "six_low_order_factor_product": {
            "factor_order": 2,
            "factor_count": len(factors),
            "bm_order": len(berlekamp_massey(product, p)) - 1,
            "somos4": fit_somos4(product, p),
        },
    }


def extend_progression(
    curve: Any, progression: dict[str, Any], length: int
) -> list[Point]:
    point = TYPED.point_from_json(progression["p0"])
    step = TYPED.point_from_json(progression["d"])
    points = []
    ops = TYPED.Ops()
    for _ in range(length):
        points.append(point)
        point = curve.add(point, step, ops)
    if None in points or len(points) != len(set(points)):
        raise AssertionError("extended progression is not distinct/nonidentity")
    return points


def canonical_tuples(size: int) -> list[tuple[int, int, int, int]]:
    return list(itertools.combinations_with_replacement(range(size), 4))


def locator_value(
    output: tuple[int, int, int],
    target: Point,
    p: int,
    nu: int,
) -> int:
    xq, yq, zq = NORM.affine_to_projective(target)
    x, y, z = output
    ex = (zq * x - xq * z) % p
    ey = (zq * y - yq * z) % p
    return (ex * ex - nu * ey * ey) % p


def build_leaf_sequences(
    p: int,
    a: int,
    b: int,
    a_points: list[Point],
    r_points: list[Point],
    tuples: list[tuple[int, int, int, int]],
    targets: dict[str, Point],
) -> dict[str, Any]:
    leaves = {
        target_name: [[0] * len(a_points) for _ in tuples]
        for target_name in targets
    }
    invalid = 0
    replay_mismatches = 0
    zero_mismatches = {name: 0 for name in targets}
    nu = NORM.nonsquare(p)
    r_projective = [NORM.affine_to_projective(point) for point in r_points]
    for a_index, a_point in enumerate(a_points):
        a_projective = NORM.affine_to_projective(a_point)
        for tuple_index, indices in enumerate(tuples):
            inputs = [
                a_projective,
                *(r_projective[index] for index in indices),
            ]
            output = TT.sum_five(inputs, p, a, b)
            expected = NORM.sum_affine(
                [a_point, *(r_points[index] for index in indices)], p, a
            )
            actual = TT.projective_to_affine(output, p)
            invalid += int(not TT.projective_on_curve(output, p, a, b))
            replay_mismatches += int(actual != expected)
            for target_name, target in targets.items():
                value = locator_value(output, target, p, nu)
                leaves[target_name][tuple_index][a_index] = value
                zero_mismatches[target_name] += int(
                    (value == 0) != (expected == target)
                )
    return {
        "leaves_internal": leaves,
        "summary": {
            "a_count": len(a_points),
            "canonical_tuple_count": len(tuples),
            "target_count": len(targets),
            "locator_evaluations": (
                len(a_points) * len(tuples) * len(targets)
            ),
            "rcb_calls": 4 * len(a_points) * len(tuples),
            "invalid_projective_count": invalid,
            "affine_replay_mismatches": replay_mismatches,
            "zero_set_mismatches": zero_mismatches,
            "leaf_digests": {
                name: canonical_digest(values)
                for name, values in leaves.items()
            },
        },
    }


def sequence_metrics(sequence: Sequence[int], p: int) -> dict[str, Any]:
    connection = berlekamp_massey(sequence, p)
    return {
        "bm_order": len(connection) - 1,
        "normalized_bm_order": (
            (len(connection) - 1) / max(1, len(sequence))
        ),
        "connection_digest": canonical_digest(connection),
        "full_recurrence_violations": recurrence_violations(
            sequence, connection, p
        ),
        "train_test": train_test_recurrence(sequence, p),
        "somos4": fit_somos4(sequence, p),
        "zero_count": sum(value == 0 for value in sequence),
        "sequence_digest": canonical_digest(sequence),
        "connection_internal": connection,
    }


def tree_from_leaves(
    leaf_sequences: list[list[int]], p: int
) -> dict[str, Any]:
    levels = [
        [
            {"lo": index, "hi": index + 1, "sequence": sequence}
            for index, sequence in enumerate(leaf_sequences)
        ]
    ]
    multiplications = 0
    while len(levels[-1]) > 1:
        prior = levels[-1]
        current = []
        for index in range(0, len(prior), 2):
            left = prior[index]
            if index + 1 == len(prior):
                current.append(left)
                continue
            right = prior[index + 1]
            sequence = [
                x * y % p
                for x, y in zip(left["sequence"], right["sequence"])
            ]
            multiplications += len(sequence)
            current.append(
                {
                    "lo": left["lo"],
                    "hi": right["hi"],
                    "sequence": sequence,
                }
            )
        levels.append(current)
    return {
        "levels_internal": levels,
        "field_multiplications": multiplications,
    }


def level_summary(
    nodes: list[dict[str, Any]], p: int
) -> dict[str, Any]:
    metrics = [sequence_metrics(node["sequence"], p) for node in nodes]
    orders = [record["bm_order"] for record in metrics]
    sibling_pairs = len(nodes) // 2
    exact_shared = 0
    cross_exact = 0
    for index in range(0, 2 * sibling_pairs, 2):
        left = metrics[index]
        right = metrics[index + 1]
        exact_shared += int(
            left["connection_digest"] == right["connection_digest"]
        )
        cross_exact += int(
            recurrence_violations(
                nodes[index + 1]["sequence"],
                left["connection_internal"],
                p,
            )
            == 0
        )
    return {
        "node_count": len(nodes),
        "block_size_min": min(node["hi"] - node["lo"] for node in nodes),
        "block_size_max": max(node["hi"] - node["lo"] for node in nodes),
        "bm_order_min": min(orders),
        "bm_order_median": statistics.median(orders),
        "bm_order_max": max(orders),
        "normalized_bm_order_median": (
            statistics.median(
                record["normalized_bm_order"] for record in metrics
            )
        ),
        "train_test_exact_fraction": (
            sum(record["train_test"]["held_out_exact"] for record in metrics)
            / len(metrics)
        ),
        "somos4_exact_fraction": (
            sum(record["somos4"]["exact"] for record in metrics)
            / len(metrics)
        ),
        "connection_unique_count": len(
            {record["connection_digest"] for record in metrics}
        ),
        "sibling_pairs": sibling_pairs,
        "sibling_exact_shared_fraction": (
            exact_shared / sibling_pairs if sibling_pairs else None
        ),
        "sibling_cross_exact_fraction": (
            cross_exact / sibling_pairs if sibling_pairs else None
        ),
        "metrics_digest": canonical_digest(
            [
                {
                    key: value
                    for key, value in record.items()
                    if key != "connection_internal"
                }
                for record in metrics
            ]
        ),
    }


def descend_zero(
    levels: list[list[dict[str, Any]]],
    sequence_index: int,
    tuples: list[tuple[int, int, int, int]],
) -> dict[str, Any]:
    node_index = 0
    path = []
    for level_index in range(len(levels) - 1, 0, -1):
        lower = levels[level_index - 1]
        left_index = 2 * node_index
        right_index = left_index + 1
        candidates = [
            index
            for index in (left_index, right_index)
            if index < len(lower)
            and lower[index]["sequence"][sequence_index] == 0
        ]
        if not candidates:
            return {
                "found": False,
                "path": path,
                "reason": "zero parent had no zero child",
            }
        chosen = candidates[0]
        path.append(chosen)
        node_index = chosen
    leaf = levels[0][node_index]
    return {
        "found": True,
        "path": path,
        "leaf_index": leaf["lo"],
        "tuple": list(tuples[leaf["lo"]]),
        "leaf_zero": leaf["sequence"][sequence_index] == 0,
    }


def analyze_tree(
    leaf_sequences: list[list[int]],
    tuples: list[tuple[int, int, int, int]],
    p: int,
    word_bytes: int,
) -> dict[str, Any]:
    tree = tree_from_leaves(leaf_sequences, p)
    levels = tree["levels_internal"]
    summaries = [level_summary(level, p) for level in levels]
    root_sequence = levels[-1][0]["sequence"]
    root_metrics = sequence_metrics(root_sequence, p)
    zero_indices = [
        index for index, value in enumerate(root_sequence) if value == 0
    ]
    descent = (
        descend_zero(levels, zero_indices[0], tuples)
        if zero_indices
        else {"found": False, "reason": "root has no zero"}
    )
    field_elements = sum(
        len(node["sequence"]) for level in levels for node in level
    )
    return {
        "summary": {
            "leaf_count": len(leaf_sequences),
            "tree_levels": len(levels),
            "tree_nodes": sum(len(level) for level in levels),
            "materialized_field_elements": field_elements,
            "materialized_bytes": field_elements * word_bytes,
            "block_product_field_multiplications": tree[
                "field_multiplications"
            ],
            "root": {
                key: value
                for key, value in root_metrics.items()
                if key != "connection_internal"
            },
            "root_connection": root_metrics["connection_internal"],
            "root_zero_indices": zero_indices,
            "descent": descent,
            "levels": summaries,
        },
        "root_sequence_internal": root_sequence,
    }


def build_random_a(
    curve: Any,
    q: int,
    size: int,
    seed: int,
    forbidden: set[Point],
) -> list[Point]:
    return [
        NORM.point_from_json(value)
        for value in NORM.build_random_a(
            curve, q, size, seed, forbidden
        )["points"]
    ]


def run_family(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    length_multiplier: int,
) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    a = curve_record["a"]
    b = curve_record["b"]
    curve = TYPED.Curve(p, a, b)
    r_points = [
        NORM.point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    tuples = canonical_tuples(len(r_points))
    length = length_multiplier * len(r_points)
    progression_points = extend_progression(
        curve, family_record["progression"], length
    )
    planted_tuple_index = (
        int.from_bytes(
            hashlib.sha256(
                (
                    "ELLIPTIC-NET-BLOCK-ZERO|PLANTED-TUPLE|"
                    f"{curve_record['id']}|{family_record['family']}"
                ).encode("ascii")
            ).digest(),
            "big",
        )
        % len(tuples)
    )
    planted_a_index = (
        int.from_bytes(
            hashlib.sha256(
                (
                    "ELLIPTIC-NET-BLOCK-ZERO|PLANTED-A|"
                    f"{curve_record['id']}|{family_record['family']}"
                ).encode("ascii")
            ).digest(),
            "big",
        )
        % length
    )
    planted_tuple = tuples[planted_tuple_index]
    planted_target = NORM.sum_affine(
        [
            progression_points[planted_a_index],
            *(r_points[index] for index in planted_tuple),
        ],
        p,
        a,
    )
    held_out_target, held_out_source, _ = TYPED.hash_to_curve_point(
        curve,
        q,
        family_record["run_seed"] ^ 0x299F31D0,
        (
            "ELLIPTIC-NET-BLOCK-ZERO|HELD-OUT|"
            f"{curve_record['id']}|{family_record['family']}"
        ),
        set(r_points) | set(progression_points),
    )
    targets = {
        "planted": planted_target,
        "held_out": held_out_target,
    }
    variants = {
        "progression": progression_points,
        "random": build_random_a(
            curve,
            q,
            length,
            family_record["run_seed"] ^ 0x082EFA98,
            set(r_points),
        ),
    }
    variant_rows = {}
    word_bytes = max(1, (p.bit_length() + 7) // 8)
    for variant, a_points in variants.items():
        source = build_leaf_sequences(
            p, a, b, a_points, r_points, tuples, targets
        )
        trees = {}
        for target_name in targets:
            trees[target_name] = analyze_tree(
                source["leaves_internal"][target_name],
                tuples,
                p,
                word_bytes,
            )
        variant_rows[variant] = {
            "a_digest": canonical_digest(
                [TYPED.point_json(point) for point in a_points]
            ),
            "source": source["summary"],
            "trees": {
                name: row["summary"] for name, row in trees.items()
            },
            "root_sequences_internal": {
                name: row["root_sequence_internal"]
                for name, row in trees.items()
            },
        }
    progression = variant_rows["progression"]
    random_a = variant_rows["random"]
    root_sharing = {}
    for variant_name, row in variant_rows.items():
        planted = row["trees"]["planted"]
        held_out = row["trees"]["held_out"]
        planted_connection = planted["root_connection"]
        root_sharing[variant_name] = {
            "connection_digest_equal": (
                planted["root"]["connection_digest"]
                == held_out["root"]["connection_digest"]
            ),
            "planted_connection_on_held_out_violations": (
                recurrence_violations(
                    row["root_sequences_internal"]["held_out"],
                    planted_connection,
                    p,
                )
            ),
        }
    planted_progression = progression["trees"]["planted"]
    planted_random = random_a["trees"]["planted"]
    planted_descent = planted_progression["descent"]
    descent_replay = False
    if planted_descent["found"]:
        indices = tuple(planted_descent["tuple"])
        recovered = NORM.sum_affine(
            [
                progression_points[
                    planted_progression["root_zero_indices"][0]
                ],
                *(r_points[index] for index in indices),
            ],
            p,
            a,
        )
        descent_replay = recovered == planted_target
    semantics_valid = all(
        row["source"]["invalid_projective_count"] == 0
        and row["source"]["affine_replay_mismatches"] == 0
        and all(
            count == 0
            for count in row["source"]["zero_set_mismatches"].values()
        )
        for row in variant_rows.values()
    )
    leaf_sibling = planted_progression["levels"][0][
        "sibling_exact_shared_fraction"
    ]
    recurrence_signal = (
        planted_progression["root"]["bm_order"] <= 2 * len(r_points)
        and planted_progression["root"]["normalized_bm_order"]
        <= 0.8
        * planted_random["root"]["normalized_bm_order"]
        and planted_progression["root"]["train_test"]["held_out_exact"]
        and root_sharing["progression"]["connection_digest_equal"]
        and (leaf_sibling or 0) >= 0.5
        and planted_progression["root"]["somos4"]["exact"]
        and semantics_valid
        and descent_replay
    )
    public_variants = {}
    for variant_name, row in variant_rows.items():
        public_variants[variant_name] = {
            key: value
            for key, value in row.items()
            if key != "root_sequences_internal"
        }
    return {
        "curve_id": curve_record["id"],
        "p": p,
        "q": q,
        "family": family_record["family"],
        "r_size": len(r_points),
        "sequence_length": length,
        "canonical_tuple_count": len(tuples),
        "planted": {
            "a_index": planted_a_index,
            "tuple_index": planted_tuple_index,
            "tuple": list(planted_tuple),
            "target": TYPED.point_json(planted_target),
        },
        "held_out": {
            "target": TYPED.point_json(held_out_target),
            "source": held_out_source,
        },
        "variants": public_variants,
        "root_sharing": root_sharing,
        "planted_descent_replay": descent_replay,
        "semantics_valid": semantics_valid,
        "recurrence_signal": recurrence_signal,
        "explicit_state_over_b2_5": (
            planted_progression["materialized_field_elements"]
            / len(r_points) ** 2.5
        ),
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def run(
    result_path: Path,
    families: list[str],
    length_multiplier: int,
) -> dict[str, Any]:
    if length_multiplier < 6:
        raise ValueError("length multiplier must be at least 6")
    source_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    rows = []
    curve_controls = {}
    for instance in source_result["instances"]:
        curve_record = instance["curve"]
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        point = NORM.point_from_json(curve_record["generator"])
        curve_controls[curve_record["id"]] = controls(
            curve_record["p"],
            curve_record["a"],
            curve_record["b"],
            point,
            length_multiplier * max(
                by_family[family]["factor_base"]["size"]
                for family in families
            ),
        )
        for family in families:
            rows.append(
                run_family(
                    curve_record,
                    by_family[family],
                    length_multiplier,
                )
            )
    all_controls_valid = all(
        record["planted_linear"]["recovered_order"]
        <= record["planted_linear"]["planted_order"]
        and record["planted_linear"]["recovered_violations"] == 0
        and record["planted_linear"]["planted_violations"] == 0
        and record["planted_linear"]["train_test"]["held_out_exact"]
        and record["elliptic_divisibility"]["ward_violations"] == 0
        and record["elliptic_divisibility"]["somos4"]["exact"]
        and not record["deterministic_random"]["somos4"]["exact"]
        for record in curve_controls.values()
    )
    curve_ids = sorted({row["curve_id"] for row in rows})
    promoted_families = [
        family
        for family in families
        if len(
            [
                row
                for row in rows
                if row["family"] == family and row["recurrence_signal"]
            ]
        )
        == len(curve_ids)
    ]
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "elliptic-net-block-zero-v1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "elliptic_net_block_zero_sha256": sha256_file(SCRIPT_PATH),
            "typed_s4_norm_rank_sha256": sha256_file(NORM_SOURCE),
            "typed_five_ec_sha256": sha256_file(NORM.TYPED_EC_SOURCE),
            "tt_norm_rank_sha256": sha256_file(NORM.TT_SOURCE),
            "input_result_sha256": sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "length_multiplier": length_multiplier,
        },
        "controls": curve_controls,
        "rows": rows,
        "summary": {
            "family_rows": len(rows),
            "curve_count": len(curve_ids),
            "promoted_families": promoted_families,
            "recurrence_signal_gate": len(promoted_families) >= 3,
            "constructible_implicit_state": False,
            "algorithm_promotion_gate": False,
            "all_controls_valid": all_controls_valid,
            "all_semantics_valid": all(
                row["semantics_valid"] and row["planted_descent_replay"]
                for row in rows
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Enumerative toy diagnostic. A recurrence signal would "
                "authorize an implicit-state construction experiment; it "
                "would not establish sub-rho relation generation."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--length-multiplier", type=int, default=8)
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.result, args.families, args.length_multiplier),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
