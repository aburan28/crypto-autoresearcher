#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (
            y * y - (x * x * x + self.a * x + self.b)
        ) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], -point[1] % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            slope = (
                (3 * x1 * x1 + self.a)
                * pow(2 * y1, -1, self.p)
                % self.p
            )
        else:
            slope = (
                (y2 - y1)
                * pow((x2 - x1) % self.p, -1, self.p)
                % self.p
            )
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        return x3, y3

    def mul(self, scalar: int, point: Point) -> Point:
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            scalar >>= 1
            if scalar:
                addend = self.add(addend, addend)
        return result


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return value == divisor
        divisor = 3 if divisor == 2 else divisor + 2
    return True


def build_levels(
    curve: Curve, points: list[Point], maximum_depth: int
) -> list[dict[Point, tuple[int, ...]]]:
    levels: list[dict[Point, tuple[int, ...]]] = [{None: ()}]
    for _ in range(maximum_depth):
        witnesses: dict[Point, tuple[int, ...]] = {}
        for partial in sorted(levels[-1], key=point_sort_key):
            prefix = levels[-1][partial]
            for index, point in enumerate(points):
                total = curve.add(partial, point)
                candidate = prefix + (index,)
                incumbent = witnesses.get(total)
                if incumbent is None or candidate < incumbent:
                    witnesses[total] = candidate
        levels.append(witnesses)
    return levels


def serialize_support(
    support: dict[Point, tuple[int, ...]]
) -> list[list[Any]]:
    return [
        [point_json(point), list(witness)]
        for point, witness in sorted(
            support.items(), key=lambda item: point_sort_key(item[0])
        )
    ]


def relation_coefficients(
    a_index: int, witness: list[int], r_size: int
) -> list[int]:
    counts = [0] * r_size
    for index in witness:
        require(0 <= index < r_size, "R witness index out of range")
        counts[index] += 1
    require(sum(counts) == 4, "relation does not contain four R terms")
    return [1, a_index] + counts[1:]


def dot_mod(left: list[int], right: list[int], q: int) -> int:
    require(len(left) == len(right), "dot-product width mismatch")
    return sum(a * b for a, b in zip(left, right)) % q


def verify_witness(
    curve: Curve,
    a_points: list[Point],
    r_points: list[Point],
    a_index: int,
    witness: list[int],
    target: Point,
) -> None:
    require(0 <= a_index < len(a_points), "A index out of range")
    recovered = a_points[a_index]
    for index in witness:
        require(0 <= index < len(r_points), "R index out of range")
        recovered = curve.add(recovered, r_points[index])
    require(recovered == target, "typed point witness mismatch")


def solve(equations: list[dict[str, Any]], width: int, q: int) -> list[int]:
    matrix = [
        list(equation["coefficients"]) + [equation["rhs"]]
        for equation in equations
    ]
    pivot_row = 0
    for column in range(width):
        selected = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column] % q
            ),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = (
            matrix[selected],
            matrix[pivot_row],
        )
        inverse = pow(matrix[pivot_row][column] % q, -1, q)
        for index in range(column, width + 1):
            matrix[pivot_row][index] = (
                matrix[pivot_row][index] * inverse % q
            )
        for row in range(len(matrix)):
            if row == pivot_row:
                continue
            factor = matrix[row][column] % q
            if factor:
                for index in range(column, width + 1):
                    matrix[row][index] = (
                        matrix[row][index]
                        - factor * matrix[pivot_row][index]
                    ) % q
        pivot_row += 1
    require(pivot_row == width, "independent equation rank mismatch")
    solution = [0] * width
    for row in matrix:
        pivot = next(
            (index for index in range(width) if row[index] % q), None
        )
        if pivot is not None:
            solution[pivot] = row[-1] % q
    return solution


def census(curve: Curve, q: int, generator: Point) -> dict[Point, int]:
    values = {}
    point: Point = None
    for scalar in range(q):
        require(point not in values, "census repeated early")
        values[point] = scalar
        point = curve.add(point, generator)
    require(point is None and len(values) == q, "census closure mismatch")
    return values


def verify_selected_query(
    curve: Curve,
    a_points: list[Point],
    r_points: list[Point],
    d3: dict[Point, tuple[int, ...]],
    d4: dict[Point, tuple[int, ...]],
    target: Point,
    materialized: dict[str, Any],
    split: dict[str, Any],
) -> None:
    expected_materialized = None
    for a_index, a_point in enumerate(a_points):
        witness = d4.get(curve.add(target, curve.neg(a_point)))
        if witness is not None:
            expected_materialized = (a_index, list(witness))
            break
    require(
        materialized["success"] == (expected_materialized is not None),
        "materialized support mismatch",
    )
    if expected_materialized is not None:
        require(
            (materialized["a_index"], materialized["r_witness"])
            == expected_materialized,
            "materialized selected witness mismatch",
        )
    expected_split = None
    for a_index, a_point in enumerate(a_points):
        after_a = curve.add(target, curve.neg(a_point))
        for r_index, r_point in enumerate(r_points):
            witness = d3.get(curve.add(after_a, curve.neg(r_point)))
            if witness is not None:
                expected_split = (
                    a_index,
                    [r_index] + list(witness),
                )
                break
        if expected_split is not None:
            break
    require(
        split["success"] == (expected_split is not None),
        "R+D3 support mismatch",
    )
    if expected_split is not None:
        require(
            (split["a_index"], split["r_witness"]) == expected_split,
            "R+D3 selected witness mismatch",
        )


def verify_family(
    curve: Curve,
    q: int,
    generator: Point,
    family: dict[str, Any],
) -> dict[str, Any]:
    factor_base = family["factor_base"]
    progression = family["progression"]
    r_points = [point_from_json(value) for value in factor_base["points"]]
    a_points = [point_from_json(value) for value in progression["points"]]
    require(
        all(point is not None and curve.on_curve(point) for point in r_points),
        "invalid R point",
    )
    require(
        all(point is not None and curve.on_curve(point) for point in a_points),
        "invalid A point",
    )
    require(len(r_points) == len(set(r_points)), "duplicate R point")
    require(len(a_points) == len(set(a_points)), "duplicate A point")
    require(not set(r_points) & set(a_points), "A/R overlap")
    d = point_from_json(progression["d"])
    for index in range(1, len(a_points)):
        require(
            a_points[index] == curve.add(a_points[index - 1], d),
            "progression recurrence mismatch",
        )
    factor_without_digest = {
        key: value for key, value in factor_base.items() if key != "digest"
    }
    require(
        factor_base["digest"] == canonical_digest(factor_without_digest),
        "factor-base digest mismatch",
    )
    progression_without_digest = {
        key: value for key, value in progression.items() if key != "digest"
    }
    require(
        progression["digest"] == canonical_digest(progression_without_digest),
        "progression digest mismatch",
    )
    require(
        family["frozen_public_construction_digest"]
        == canonical_digest(
            {
                "factor_base_digest": factor_base["digest"],
                "progression_digest": progression["digest"],
            }
        ),
        "frozen construction digest mismatch",
    )

    levels = build_levels(curve, r_points, 4)
    d3 = levels[3]
    d4 = levels[4]
    require(
        len(d3) == family["compiler"]["d3_entries"],
        "D3 cardinality mismatch",
    )
    require(
        len(d4) == family["compiler"]["d4_entries"],
        "D4 cardinality mismatch",
    )
    compiler_payload = {
        "D3": serialize_support(d3),
        "D4": serialize_support(d4),
    }
    compiler_encoded = json.dumps(
        compiler_payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    require(
        hashlib.sha256(compiler_encoded).hexdigest()
        == family["compiler"]["digest"],
        "compiler digest mismatch",
    )
    support = {
        curve.add(a_point, d4_point)
        for a_point in a_points
        for d4_point in d4
    }
    require(
        len(support) == family["exact_support"]["support_entries"],
        "exact support mismatch",
    )
    require(
        len(support - {None})
        == family["exact_support"]["nonidentity_entries"],
        "nonidentity support mismatch",
    )

    relations = family["relations"]
    transcript = relations["target_transcript"]
    require(
        canonical_digest(transcript)
        == relations["target_transcript_digest"],
        "relation transcript digest mismatch",
    )
    require(
        len(transcript) == relations["targets_attempted"],
        "relation target count mismatch",
    )
    successful_targets = 0
    candidate_rows = 0
    for target_record in transcript:
        scalar = target_record["scalar"]
        target = point_from_json(target_record["target"])
        require(
            target == curve.mul(scalar, generator),
            "relation target scalar mismatch",
        )
        successful_targets += bool(target_record["hits"])
        candidate_rows += len(target_record["hits"])
        for hit in target_record["hits"]:
            verify_witness(
                curve,
                a_points,
                r_points,
                hit["a_index"],
                hit["r_witness"],
                target,
            )
    require(
        successful_targets == relations["successful_targets"],
        "successful relation targets mismatch",
    )
    require(
        candidate_rows == relations["candidate_relation_rows"],
        "candidate relation row count mismatch",
    )
    equations = relations["independent_equations"]
    width = relations["quotient_width"]
    require(len(equations) == width, "independent equation count mismatch")
    for equation in equations:
        coefficients = relation_coefficients(
            equation["a_index"], equation["r_witness"], len(r_points)
        )
        require(
            coefficients == equation["coefficients"],
            "relation coefficient mismatch",
        )
        target = curve.mul(equation["rhs"], generator)
        verify_witness(
            curve,
            a_points,
            r_points,
            equation["a_index"],
            equation["r_witness"],
            target,
        )
    solution = solve(equations, width, q)
    require(
        solution == relations["attack_solution"],
        "attack solution mismatch",
    )
    null = relations["gauge_null_vector"]
    require(
        len(null) == len(r_points) + 2,
        "gauge vector width mismatch",
    )
    for equation in equations:
        full_counts = [0] * len(r_points)
        for index in equation["r_witness"]:
            full_counts[index] += 1
        full = [1, equation["a_index"]] + full_counts
        require(dot_mod(full, null, q) == 0, "gauge is not a null vector")

    scalar_census = census(curve, q, generator)
    r_logs = [scalar_census[point] for point in r_points]
    p0 = point_from_json(progression["p0"])
    expected_solution = [
        (scalar_census[p0] + 4 * r_logs[0]) % q,
        scalar_census[d],
    ] + [
        (value - r_logs[0]) % q for value in r_logs[1:]
    ]
    require(solution == expected_solution, "diagnostic solution mismatch")
    require(
        canonical_digest(solution)
        == family["diagnostic"]["solution_digest"],
        "diagnostic solution digest mismatch",
    )

    descent = family["held_out_descent"]
    descent_transcript = descent["transcript"]
    require(
        canonical_digest(descent_transcript)
        == descent["transcript_digest"],
        "descent transcript digest mismatch",
    )
    require(
        len(descent_transcript) == descent["target_count"],
        "descent target count mismatch",
    )
    supported = 0
    for record in descent_transcript:
        scalar = record["scalar"]
        target = point_from_json(record["target"])
        require(
            target == curve.mul(scalar, generator),
            "descent target scalar mismatch",
        )
        verify_selected_query(
            curve,
            a_points,
            r_points,
            d3,
            d4,
            target,
            record["materialized_d4"],
            record["r_scan_plus_d3"],
        )
        if not record["materialized_d4"]["success"]:
            require(
                record["recovered_scalar"] is None,
                "unsupported target has recovered scalar",
            )
            continue
        supported += 1
        for key in ("materialized_d4", "r_scan_plus_d3"):
            selected = record[key]
            verify_witness(
                curve,
                a_points,
                r_points,
                selected["a_index"],
                selected["r_witness"],
                target,
            )
            coefficients = relation_coefficients(
                selected["a_index"],
                selected["r_witness"],
                len(r_points),
            )
            require(
                dot_mod(coefficients, solution, q) == scalar,
                "descent quotient evaluation mismatch",
            )
        require(
            record["recovered_scalar"] == scalar,
            "recorded recovered scalar mismatch",
        )
    require(
        supported == descent["supported_targets"]
        == descent["verified_targets"],
        "descent success count mismatch",
    )
    return {
        "family": family["family"],
        "q": q,
        "d3_entries": len(d3),
        "d4_entries": len(d4),
        "relation_rows_verified": candidate_rows,
        "quotient_rank": width,
        "descent_targets_verified": supported,
        "support_entries": len(support),
    }


def verify(result_path: Path) -> dict[str, Any]:
    result = json.loads(result_path.read_text(encoding="utf-8"))
    require(result["valid"], "result is not marked valid")
    require(
        result["protocol"]
        == "EXP-ECDLP-COORD-EXPANSION-001-typed-five-ec-v1",
        "protocol mismatch",
    )
    source_dir = SCRIPT_PATH.parent
    source_paths = {
        "typed_five_ec_sha256": source_dir / "typed_five_ec.py",
        "coordinate_expansion_sha256": source_dir / "coordinate_expansion.py",
        "typed_five_term_sha256": source_dir / "typed_five_term.py",
    }
    for key, path in source_paths.items():
        require(
            sha256_file(path) == result["source"][key],
            f"source hash mismatch: {key}",
        )
    rows = []
    for instance in result["instances"]:
        curve_record = instance["curve"]
        p = curve_record["p"]
        q = curve_record["q"]
        require(is_prime(p) and is_prime(q), "field/order primality mismatch")
        require(q == curve_record["order"], "group order mismatch")
        require(curve_record["cofactor"] == 1, "cofactor mismatch")
        require(curve_record["trace"] not in (0, 1), "excluded trace")
        curve = Curve(p, curve_record["a"], curve_record["b"])
        generator = point_from_json(curve_record["generator"])
        require(curve.on_curve(generator), "generator not on curve")
        require(curve.mul(q, generator) is None, "generator order mismatch")
        for family in instance["families"]:
            rows.append(verify_family(curve, q, generator, family))
    attack_rows = [
        family
        for instance in result["instances"]
        for family in instance["families"]
        if family["attack_eligible"]
    ]
    require(
        result["summary"]["attack_eligible_rows"] == len(attack_rows),
        "attack row count mismatch",
    )
    require(
        result["summary"]["success_gate"]
        == all(
            family["relations"]["quotient_rank"]
            == family["relations"]["quotient_width"]
            and family["diagnostic"]["quotient_solution_verified"]
            and family["held_out_descent"]["all_supported_verified"]
            and family["exact_support"]["nonidentity_probability"] >= 0.25
            for family in attack_rows
        ),
        "success gate mismatch",
    )
    require(
        result["summary"]["breakthrough_claim"] is False,
        "breakthrough claim must remain false",
    )
    return {
        "protocol": "verify-typed-five-ec-v1",
        "valid": True,
        "result_path": str(result_path.resolve()),
        "result_sha256": sha256_file(result_path),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "rows_verified": len(rows),
        "relation_rows_verified": sum(
            row["relation_rows_verified"] for row in rows
        ),
        "descent_targets_verified": sum(
            row["descent_targets_verified"] for row in rows
        ),
        "row_receipts": rows,
        "breakthrough_claim": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            verify(args.result),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
