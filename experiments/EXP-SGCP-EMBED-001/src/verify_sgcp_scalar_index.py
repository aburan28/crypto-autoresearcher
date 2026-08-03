#!/usr/bin/env python3
"""Independent scalar-index P2 oracle for EXP-SGCP-EMBED-001.

The coordinate fixture is used only to attest the scalar orbit and to derive
the coordinate-defined factor bases.  All P2 witness evaluation, collision
testing, exhaustive subset search, objectives, and retention accounting then
take place in Z/23Z.  This file imports neither SGCP implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence, Tuple


SCHEMA = "sgcp-embed-001-scalar-index-oracle-v1"
EXPERIMENT_ID = "EXP-SGCP-EMBED-001"
P = 19
A = 2
B_COEFFICIENT = 9
Q = 23
GENERATOR = (0, 3)
FACTOR_BASE_SIZES = (4, 6, 8)
SCALAR_TABLE_SHA256 = (
    "c73fdf6300e4d83ac581a07935a31dbaf6c4af3fb6b3cbe762f4266170c3f44c"
)
OUTCOME_ORDER = "lexicographic_subset_universe_indices"
SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_OUTPUT = SCRIPT_PATH.parents[1] / "oracles" / "scalar-index-oracle-v1.json"

# Frozen development expectations independently reported in source-red-team-v2
# and tests/test_sgcp_embed.py.  The CLI refuses to emit an artifact unless the
# scalar-index recount reproduces every value exactly.
EXPECTED_ROWS: dict[int, dict[str, Any]] = {
    4: {
        "candidate_count": 31,
        "valid_candidate_count": 12,
        "conflict_count": 20,
        "direct_subset_count": 4096,
        "objective": [13, 5, 20, 26],
        "lexicographic_outcome_sha256": (
            "8f95f52fd06e7c636b017f8f1b720985a797d871982274596b4c078dffb15257"
        ),
    },
    6: {
        "candidate_count": 68,
        "valid_candidate_count": 8,
        "conflict_count": 4,
        "direct_subset_count": 256,
        "objective": [7, 4, 17, 20],
        "lexicographic_outcome_sha256": (
            "c571d463baf72995f5b34df987771302e847029d192a10339c07429433f76b72"
        ),
    },
    8: {
        "candidate_count": 124,
        "valid_candidate_count": 14,
        "conflict_count": 53,
        "direct_subset_count": 16384,
        "objective": [7, 4, 14, 21],
        "lexicographic_outcome_sha256": (
            "38f0c54a812f47913bde99808f779590c7f2cad46f5e5fb670d3d728c8e70c37"
        ),
    },
}

Point = Optional[Tuple[int, int]]
Formal = tuple[int, ...]


def canonical_json(value: Any) -> bytes:
    """Return deterministic RFC-8259 JSON bytes with no non-finite numbers."""

    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("ascii")


def digest_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON constant: {token}")


def strict_loads(payload: bytes) -> Any:
    text = payload.decode("utf-8")
    return json.loads(
        text,
        object_pairs_hook=strict_pairs,
        parse_constant=reject_json_constant,
    )


def require_json_types(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if isinstance(value, list):
        for index, child in enumerate(value):
            require_json_types(child, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, child in value.items():
            if type(key) is not str:
                raise TypeError(f"{path}: JSON object key is not a string")
            require_json_types(child, f"{path}.{key}")
        return
    raise TypeError(f"{path}: unsupported JSON value type {type(value).__name__}")


def point_label(point: Point) -> str:
    return "O" if point is None else f"{point[0]}:{point[1]}"


def point_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def on_curve(point: Point) -> bool:
    if point is None:
        return True
    x, y = point
    return (y * y - (x * x * x + A * x + B_COEFFICIENT)) % P == 0


def add_points(left: Point, right: Point) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if left == right:
        numerator = (3 * x1 * x1 + A) % P
        denominator = (2 * y1) % P
    else:
        numerator = (y2 - y1) % P
        denominator = (x2 - x1) % P
    slope = numerator * pow(denominator, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    result = (x3, y3)
    if not on_curve(result):
        raise AssertionError(f"fixture addition left the curve: {left}+{right}={result}")
    return result


def build_scalar_orbit() -> tuple[list[Point], dict[Point, int]]:
    orbit: list[Point] = []
    current: Point = None
    for scalar in range(Q):
        if current in orbit:
            raise AssertionError(f"generator repeated before order {Q} at scalar {scalar}")
        orbit.append(current)
        current = add_points(current, GENERATOR)
    if current is not None:
        raise AssertionError(f"generator does not have declared order {Q}")

    enumerated = {
        (x, y)
        for x in range(P)
        for y in range(P)
        if on_curve((x, y))
    }
    enumerated.add(None)
    if set(orbit) != enumerated or len(orbit) != Q:
        raise AssertionError("generator orbit is not the complete declared prime-order group")
    if digest_json([point_label(point) for point in orbit]) != SCALAR_TABLE_SHA256:
        raise AssertionError("scalar orbit digest differs from the frozen verifier digest")
    return orbit, {point: scalar for scalar, point in enumerate(orbit)}


def factor_base_record(
    orbit: Sequence[Point], scalar_by_point: dict[Point, int], size: int
) -> tuple[list[int], dict[str, Any]]:
    fibers: dict[int, list[Point]] = defaultdict(list)
    for point in orbit:
        if point is not None:
            fibers[point[0]].append(point)
    roots = sorted(x for x, points in fibers.items() if len(points) == 2)[: size // 2]
    points = sorted(
        (point for root in roots for point in fibers[root]),
        key=point_key,
    )
    if len(points) != size:
        raise AssertionError(f"factor base B={size} has {len(points)} points")
    scalars = [scalar_by_point[point] for point in points]
    if 0 in scalars or len(set(scalars)) != size:
        raise AssertionError(f"factor base B={size} is not a distinct nonzero scalar set")
    records = [
        {
            "factor_index": index,
            "point": point_label(point),
            "scalar_index": scalars[index],
        }
        for index, point in enumerate(points)
    ]
    return scalars, {"B": size, "coordinate_roots": roots, "factors": records}


def evaluate(formal: Formal, factor_scalars: Sequence[int]) -> int:
    return sum(factor_scalars[index] for index in formal) % Q


def submultisets(formal: Formal) -> set[Formal]:
    result: set[Formal] = {()}
    for degree in range(1, len(formal) + 1):
        result.update(itertools.combinations(formal, degree))
    return result


def base_family(size: int) -> set[Formal]:
    return {(), *((index,) for index in range(size))}


def generated_family(size: int, maxima: Iterable[Formal]) -> set[Formal]:
    family = base_family(size)
    for maximum in maxima:
        family.update(submultisets(maximum))
    return family


def first_collision(
    family: Iterable[Formal], factor_scalars: Sequence[int]
) -> dict[str, Any] | None:
    by_scalar: dict[int, list[Formal]] = defaultdict(list)
    for formal in sorted(set(family), key=lambda item: (len(item), item)):
        by_scalar[evaluate(formal, factor_scalars)].append(formal)
    choices = [
        (scalar, values[0], values[1])
        for scalar, values in by_scalar.items()
        if len(values) > 1
    ]
    if not choices:
        return None
    scalar, left, right = min(
        choices,
        key=lambda row: (row[0], len(row[1]), row[1], len(row[2]), row[2]),
    )
    return {
        "scalar_index": scalar,
        "left_witness": list(left),
        "right_witness": list(right),
    }


def candidate_universe(
    size: int, factor_scalars: Sequence[int]
) -> tuple[list[Formal], dict[Formal, list[tuple[Formal, Formal]]]]:
    degree2_by_scalar: dict[int, list[Formal]] = defaultdict(list)
    for formal in itertools.combinations_with_replacement(range(size), 2):
        degree2_by_scalar[evaluate(formal, factor_scalars)].append(formal)
    canonical_nodes = [
        min(witnesses)
        for scalar, witnesses in degree2_by_scalar.items()
        if scalar != 0
    ]

    parents: dict[Formal, set[tuple[Formal, Formal]]] = defaultdict(set)
    for left_position, left in enumerate(canonical_nodes):
        for right in canonical_nodes[left_position:]:
            parent_pair = tuple(sorted((left, right)))
            flattened = tuple(sorted(left + right))
            parents[flattened].add(parent_pair)
    ordered = sorted(parents)
    return ordered, {
        formal: sorted(parent_pairs) for formal, parent_pairs in parents.items()
    }


def star_profile(
    family: set[Formal], factor_scalars: Sequence[int]
) -> tuple[int, int]:
    if first_collision(family, factor_scalars) is not None:
        raise AssertionError("star profile requires an injective generated family")
    nonempty = sorted((formal for formal in family if formal), key=lambda row: (len(row), row))
    edges: set[tuple[int, int, int]] = set()
    for left_position, left in enumerate(nonempty):
        for right in nonempty[left_position:]:
            union = tuple(sorted(left + right))
            if union not in family:
                continue
            left_scalar = evaluate(left, factor_scalars)
            right_scalar = evaluate(right, factor_scalars)
            output_scalar = evaluate(union, factor_scalars)
            edge = (
                min(left_scalar, right_scalar),
                max(left_scalar, right_scalar),
                output_scalar,
            )
            if edge in edges:
                raise AssertionError("injective family produced a duplicate scalar-index edge")
            edges.add(edge)

    constrained = {0}
    for left, right, output in edges:
        constrained.update((left, right))
        if left != output and right != output:
            constrained.add(output)
    return len(constrained), len(edges)


def target_witness_map(outputs: Iterable[int]) -> dict[int, list[list[int]]]:
    distinct = sorted(set(outputs))
    targets: dict[int, list[list[int]]] = defaultdict(list)
    for left_position, left in enumerate(distinct):
        for right in distinct[left_position:]:
            targets[(left + right) % Q].append([left, right])
    return {target: targets[target] for target in sorted(targets)}


def exact_ratio(numerator: int, denominator: int) -> dict[str, int]:
    if denominator <= 0:
        raise ValueError("ratio denominator must be positive")
    divisor = math.gcd(numerator, denominator)
    return {"numerator": numerator // divisor, "denominator": denominator // divisor}


def retention_record(raw_outputs: Iterable[int], retained_outputs: Iterable[int]) -> dict[str, Any]:
    raw_four = sorted(set(raw_outputs))
    retained_four = sorted(set(retained_outputs))
    raw_targets = target_witness_map(raw_four)
    retained_targets = target_witness_map(retained_four)

    def encode_map(targets: dict[int, list[list[int]]]) -> dict[str, list[list[int]]]:
        return {str(target): witnesses for target, witnesses in targets.items()}

    def count_map(targets: dict[int, list[list[int]]]) -> dict[str, int]:
        return {str(target): len(witnesses) for target, witnesses in targets.items()}

    def histogram(targets: dict[int, list[list[int]]]) -> dict[str, int]:
        counts = Counter(len(witnesses) for witnesses in targets.values())
        return {str(multiplicity): counts[multiplicity] for multiplicity in sorted(counts)}

    return {
        "pair_convention": "unordered_with_replacement_over_distinct_four_term_outputs",
        "raw_four_term_scalar_indices": raw_four,
        "retained_four_term_scalar_indices": retained_four,
        "raw_final_support": len(raw_targets),
        "retained_final_support": len(retained_targets),
        "support_ratio": exact_ratio(len(retained_targets), len(raw_targets) or 1),
        "raw_absolute_group_coverage": exact_ratio(len(raw_targets), Q),
        "retained_absolute_group_coverage": exact_ratio(len(retained_targets), Q),
        "raw_support_scalar_indices": sorted(raw_targets),
        "retained_support_scalar_indices": sorted(retained_targets),
        "raw_target_witness_map": encode_map(raw_targets),
        "retained_target_witness_map": encode_map(retained_targets),
        "raw_target_witness_counts": count_map(raw_targets),
        "retained_target_witness_counts": count_map(retained_targets),
        "raw_target_witness_histogram": histogram(raw_targets),
        "retained_target_witness_histogram": histogram(retained_targets),
    }


def build_row(
    orbit: Sequence[Point], scalar_by_point: dict[Point, int], size: int
) -> dict[str, Any]:
    factor_scalars, factor_record = factor_base_record(orbit, scalar_by_point, size)
    universe, parent_pairs = candidate_universe(size, factor_scalars)
    universe_rows = [
        {
            "universe_index": index,
            "witness": list(formal),
            "scalar_output": evaluate(formal, factor_scalars),
            "parent_pairs": [
                [list(left), list(right)] for left, right in parent_pairs[formal]
            ],
        }
        for index, formal in enumerate(universe)
    ]

    valid: list[Formal] = []
    valid_universe_indices: list[int] = []
    valid_families: list[set[Formal]] = []
    invalid_rows: list[dict[str, Any]] = []
    for universe_index, formal in enumerate(universe):
        family = generated_family(size, [formal])
        collision = first_collision(family, factor_scalars)
        if collision is None:
            valid.append(formal)
            valid_universe_indices.append(universe_index)
            valid_families.append(family)
        else:
            invalid_rows.append(
                {
                    "universe_index": universe_index,
                    "witness": list(formal),
                    "collision": collision,
                }
            )

    conflict_masks = [0] * len(valid)
    conflict_rows: list[dict[str, Any]] = []
    for left_position in range(len(valid)):
        for right_position in range(left_position + 1, len(valid)):
            collision = first_collision(
                valid_families[left_position] | valid_families[right_position],
                factor_scalars,
            )
            if collision is None:
                continue
            conflict_masks[left_position] |= 1 << right_position
            conflict_masks[right_position] |= 1 << left_position
            conflict_rows.append(
                {
                    "left_universe_index": valid_universe_indices[left_position],
                    "right_universe_index": valid_universe_indices[right_position],
                    "collision": collision,
                }
            )

    outcomes: list[dict[str, Any]] = []
    mismatch_count = 0
    feasible_subset_count = 0
    best_key = (0, 0, -1, 0)
    best_witnesses: tuple[Formal, ...] = ()
    best_positions: tuple[int, ...] = ()
    for mask in range(1 << len(valid)):
        positions = tuple(
            position for position in range(len(valid)) if mask & (1 << position)
        )
        graph_feasible = all(
            not (conflict_masks[position] & mask) for position in positions
        )
        witnesses = tuple(valid[position] for position in positions)
        family = generated_family(size, witnesses)
        direct_feasible = first_collision(family, factor_scalars) is None
        outcomes.append(
            {
                "subset_universe_indices": [
                    valid_universe_indices[position] for position in positions
                ],
                "graph_feasible": graph_feasible,
                "direct_feasible": direct_feasible,
            }
        )
        if graph_feasible != direct_feasible:
            mismatch_count += 1
            continue
        if not direct_feasible:
            continue
        feasible_subset_count += 1
        constrained_count, edge_count = star_profile(family, factor_scalars)
        retained_outputs = [evaluate(formal, factor_scalars) for formal in witnesses]
        retained_support = len(target_witness_map(retained_outputs))
        key = (retained_support, len(witnesses), -constrained_count, -edge_count)
        if key > best_key or (key == best_key and witnesses < best_witnesses):
            best_key = key
            best_witnesses = witnesses
            best_positions = positions

    if mismatch_count:
        raise AssertionError(f"B={size}: conflict graph has {mismatch_count} direct mismatches")
    outcomes.sort(key=lambda row: row["subset_universe_indices"])
    selected_universe_indices = [
        valid_universe_indices[position] for position in best_positions
    ]
    selected_outputs = [evaluate(formal, factor_scalars) for formal in best_witnesses]
    raw_outputs = [evaluate(formal, factor_scalars) for formal in universe]
    objective = {
        "retained_final_support": best_key[0],
        "retained_degree4_formal_multisets": best_key[1],
        "constrained_count": -best_key[2],
        "unordered_nonidentity_edges": -best_key[3],
    }
    return {
        "B": size,
        "factor_base": factor_record,
        "candidate_count": len(universe),
        "valid_candidate_count": len(valid),
        "invalid_candidate_count": len(invalid_rows),
        "conflict_count": len(conflict_rows),
        "direct_subset_count": 1 << len(valid),
        "feasible_subset_count": feasible_subset_count,
        "graph_direct_mismatch_count": mismatch_count,
        "candidate_universe": universe_rows,
        "candidate_universe_sha256": digest_json(universe_rows),
        "valid_universe_indices": valid_universe_indices,
        "individually_invalid": invalid_rows,
        "conflicts": conflict_rows,
        "selected": {
            "universe_indices": selected_universe_indices,
            "witnesses": [list(formal) for formal in best_witnesses],
            "scalar_outputs": selected_outputs,
        },
        "objective_order": [
            "maximize_retained_final_support",
            "maximize_retained_degree4_formal_multisets",
            "minimize_constrained_count",
            "minimize_unordered_nonidentity_edges",
            "minimize_lexicographic_witness_list",
        ],
        "objective": objective,
        "lexicographic_outcome_order": OUTCOME_ORDER,
        "lexicographic_outcome_sha256": digest_json(outcomes),
        "retention": retention_record(raw_outputs, selected_outputs),
    }


def expected_objective_vector(row: dict[str, Any]) -> list[int]:
    objective = row["objective"]
    return [
        objective["retained_final_support"],
        objective["retained_degree4_formal_multisets"],
        objective["constrained_count"],
        objective["unordered_nonidentity_edges"],
    ]


def enforce_frozen_expectations(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    by_size = {row["B"]: row for row in rows}
    if set(by_size) != set(EXPECTED_ROWS):
        raise AssertionError("oracle row sizes differ from frozen expectations")
    for size in FACTOR_BASE_SIZES:
        row = by_size[size]
        expected = EXPECTED_ROWS[size]
        observed = {
            "candidate_count": row["candidate_count"],
            "valid_candidate_count": row["valid_candidate_count"],
            "conflict_count": row["conflict_count"],
            "direct_subset_count": row["direct_subset_count"],
            "objective": expected_objective_vector(row),
            "lexicographic_outcome_sha256": row["lexicographic_outcome_sha256"],
        }
        if observed != expected:
            raise AssertionError(
                f"B={size}: frozen scalar-index expectation mismatch: "
                f"expected {expected!r}, observed {observed!r}"
            )
        checks.append(
            {
                "B": size,
                "checked_fields": sorted(expected),
                "match": True,
            }
        )
    return checks


def build_oracle_document() -> dict[str, Any]:
    orbit, scalar_by_point = build_scalar_orbit()
    rows = [build_row(orbit, scalar_by_point, size) for size in FACTOR_BASE_SIZES]
    expectation_checks = enforce_frozen_expectations(rows)
    document = {
        "schema": SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "status": "INDEPENDENT_DEVELOPMENT_ORACLE",
        "claim_boundary": (
            "five-bit P2 implementation differential only; no ECDLP or performance claim"
        ),
        "implementation": {
            "dependencies": "python_standard_library_only",
            "imports_sgcp_embed": False,
            "imports_verify_sgcp_embed": False,
            "p2_representation": "scalar_indices_mod_q",
            "coordinate_use": "fixture_and_coordinate_factor_base_attestation_only",
            "search": "exhaustive_all_subsets_of_individually_valid_candidates",
        },
        "fixture": {
            "p": P,
            "a": A,
            "b": B_COEFFICIENT,
            "q": Q,
            "generator": list(GENERATOR),
            "factor_base_sizes": list(FACTOR_BASE_SIZES),
            "scalar_table_entry_count": len(orbit),
            "scalar_table_sha256": digest_json(
                [point_label(point) for point in orbit]
            ),
            "scalar_table": [
                {"scalar_index": scalar, "point": point_label(point)}
                for scalar, point in enumerate(orbit)
            ],
        },
        "rows": rows,
        "frozen_expectation_checks": expectation_checks,
        "valid": True,
    }
    require_json_types(document)
    payload = canonical_json(document)
    if strict_loads(payload) != document:
        raise AssertionError("strict JSON round trip changed the oracle document")
    if canonical_json(strict_loads(payload)) != payload:
        raise AssertionError("strict JSON round trip is not byte-canonical")
    return document


def build_document() -> dict[str, Any]:
    """Backward-compatible alias for early development callers."""

    return build_oracle_document()


def write_or_compare(path: Path, payload: bytes, check_only: bool) -> str:
    path = path.resolve()
    file_payload = payload + b"\n"
    if path.exists():
        existing = path.read_bytes()
        strict_loads(existing)
        if existing != file_payload:
            raise FileExistsError(f"refusing to overwrite differing oracle artifact: {path}")
        return "verified"
    if check_only:
        raise FileNotFoundError(f"oracle artifact does not exist: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(file_payload)
    except BaseException:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise
    return "created"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="write or verify an exact strict JSON artifact instead of printing it",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="require an existing byte-identical artifact and do not create one",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    document = build_oracle_document()
    payload = canonical_json(document)
    if args.output is None and not args.check:
        sys.stdout.buffer.write(payload + b"\n")
        return 0

    output = args.output if args.output is not None else DEFAULT_OUTPUT
    status = write_or_compare(output, payload, args.check)
    receipt = {
        "artifact_sha256": hashlib.sha256(payload + b"\n").hexdigest(),
        "bytes": len(payload) + 1,
        "output": str(output.resolve()),
        "status": status,
        "valid": True,
    }
    sys.stdout.buffer.write(canonical_json(receipt) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
