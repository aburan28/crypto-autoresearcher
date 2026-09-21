#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
EXPORTER_PATH = SCRIPT_PATH.with_name(
    "export_direct_equality_pair_coefficients.py"
)
Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, int]
Point = tuple[int, int] | None
Projective = tuple[int, int, int]


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    ).hexdigest()


def decode_point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def encode_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def normalize(poly: Polynomial, modulus: int) -> Polynomial:
    return {
        monomial: coefficient % modulus
        for monomial, coefficient in poly.items()
        if coefficient % modulus
    }


def plus(
    left: Polynomial, right: Polynomial, modulus: int
) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = (
            result.get(monomial, 0) + coefficient
        ) % modulus
    return normalize(result, modulus)


def minus(
    left: Polynomial, right: Polynomial, modulus: int
) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = (
            result.get(monomial, 0) - coefficient
        ) % modulus
    return normalize(result, modulus)


def times_scalar(
    poly: Polynomial, scalar: int, modulus: int
) -> Polynomial:
    return normalize(
        {
            monomial: coefficient * scalar
            for monomial, coefficient in poly.items()
        },
        modulus,
    )


def cubic_normal_form(
    poly: Polynomial,
    modulus: int,
    curve_a: int,
    curve_b: int,
) -> Polynomial:
    work = list(poly.items())
    answer: Polynomial = {}
    while work:
        (x_degree, y_degree, z_degree), coefficient = work.pop()
        coefficient %= modulus
        if not coefficient:
            continue
        if x_degree <= 2:
            key = (x_degree, y_degree, z_degree)
            answer[key] = (answer.get(key, 0) + coefficient) % modulus
            continue
        work.append(
            (
                (x_degree - 3, y_degree + 2, z_degree + 1),
                coefficient,
            )
        )
        work.append(
            (
                (x_degree - 2, y_degree, z_degree + 2),
                -curve_a * coefficient,
            )
        )
        work.append(
            (
                (x_degree - 3, y_degree, z_degree + 3),
                -curve_b * coefficient,
            )
        )
    return normalize(answer, modulus)


def product(
    left: Polynomial,
    right: Polynomial,
    modulus: int,
    curve_a: int,
    curve_b: int,
) -> Polynomial:
    expanded: Polynomial = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            key = tuple(lm[index] + rm[index] for index in range(3))
            expanded[key] = (
                expanded.get(key, 0) + lc * rc
            ) % modulus
    return cubic_normal_form(
        expanded, modulus, curve_a, curve_b
    )


def constant(value: int, modulus: int) -> Polynomial:
    return {} if value % modulus == 0 else {(0, 0, 0): value % modulus}


def variables() -> tuple[Polynomial, Polynomial, Polynomial]:
    return (
        {(1, 0, 0): 1},
        {(0, 1, 0): 1},
        {(0, 0, 1): 1},
    )


def complete_add_polynomials(
    left: tuple[Polynomial, Polynomial, Polynomial],
    right: Projective,
    modulus: int,
    curve_a: int,
    curve_b: int,
) -> tuple[Polynomial, Polynomial, Polynomial]:
    x1, y1, z1 = left
    x2, y2, z2 = (constant(value, modulus) for value in right)
    mul = lambda u, v: product(
        u, v, modulus, curve_a, curve_b
    )
    add = lambda u, v: plus(u, v, modulus)
    sub = lambda u, v: minus(u, v, modulus)
    triple_b = 3 * curve_b % modulus
    t0 = mul(x1, x2)
    t1 = mul(y1, y2)
    t2 = mul(z1, z2)
    t3 = mul(add(x1, y1), add(x2, y2))
    t3 = sub(t3, add(t0, t1))
    t4 = mul(add(x1, z1), add(x2, z2))
    t4 = sub(t4, add(t0, t2))
    t5 = mul(add(y1, z1), add(y2, z2))
    t5 = sub(t5, add(t1, t2))
    z3 = add(times_scalar(t4, curve_a, modulus), times_scalar(t2, triple_b, modulus))
    x3 = sub(t1, z3)
    z3 = add(t1, z3)
    y3 = mul(x3, z3)
    t1 = add(add(t0, t0), t0)
    t2 = times_scalar(t2, curve_a, modulus)
    t4 = times_scalar(t4, triple_b, modulus)
    t1 = add(t1, t2)
    t2 = times_scalar(sub(t0, t2), curve_a, modulus)
    t4 = add(t4, t2)
    y3 = add(y3, mul(t1, t4))
    x3 = sub(mul(t3, x3), mul(t5, t4))
    z3 = add(mul(t5, z3), mul(t3, t1))
    return x3, y3, z3


def basis(degree: int) -> list[Monomial]:
    return [
        (x_degree, y_degree, degree - x_degree - y_degree)
        for x_degree in range(min(2, degree) + 1)
        for y_degree in range(degree - x_degree + 1)
    ]


def vector(poly: Polynomial, ordered_basis: list[Monomial]) -> list[int]:
    if any(monomial not in set(ordered_basis) for monomial in poly):
        raise AssertionError("unreduced monomial outside basis")
    return [poly.get(monomial, 0) for monomial in ordered_basis]


def suffix_vectors(
    r_points: list[Point],
    suffix_axes: int,
    modulus: int,
    curve_a: int,
    curve_b: int,
    ordered_basis: list[Monomial],
) -> list[list[list[int]]]:
    result = []
    for indices in itertools.product(
        *(range(len(r_points)) for _ in range(suffix_axes))
    ):
        state = variables()
        for index in indices:
            point = r_points[index]
            if point is None:
                right = (0, 1, 0)
            else:
                right = (point[0], point[1], 1)
            state = complete_add_polynomials(
                state, right, modulus, curve_a, curve_b
            )
        result.append([vector(poly, ordered_basis) for poly in state])
    return result


def row_rank(matrix: list[list[int]], modulus: int) -> int:
    if not matrix:
        return 0
    work = [[value % modulus for value in row] for row in matrix]
    rank = 0
    columns = len(work[0])
    for column in range(columns):
        pivot = next(
            (
                row
                for row in range(rank, len(work))
                if work[row][column]
            ),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], modulus - 2, modulus)
        work[rank] = [
            value * inverse % modulus for value in work[rank]
        ]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                (left - scale * right) % modulus
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def specialize(
    coordinates: list[list[list[int]]],
    target: Point,
    modulus: int,
) -> tuple[list[list[int]], list[list[int]]]:
    if target is None:
        xq, yq, zq = 0, 1, 0
    else:
        xq, yq, zq = target[0], target[1], 1
    vx = [
        [
            (zq * x - xq * z) % modulus
            for x, z in zip(row[0], row[2])
        ]
        for row in coordinates
    ]
    vy = [
        [
            (zq * y - yq * z) % modulus
            for y, z in zip(row[1], row[2])
        ]
        for row in coordinates
    ]
    return vx, vy


def affine_add(
    left: Point, right: Point, modulus: int, curve_a: int
) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % modulus == 0:
        return None
    numerator = (
        3 * x1 * x1 + curve_a if left == right else y2 - y1
    ) % modulus
    denominator = (
        2 * y1 if left == right else x2 - x1
    ) % modulus
    slope = numerator * pow(denominator, modulus - 2, modulus) % modulus
    x3 = (slope * slope - x1 - x2) % modulus
    return x3, (slope * (x1 - x3) - y1) % modulus


def affine_sum(
    points: Iterable[Point], modulus: int, curve_a: int
) -> Point:
    result: Point = None
    for point in points:
        result = affine_add(result, point, modulus, curve_a)
    return result


def evaluate(
    coefficient_vector: list[int],
    ordered_basis: list[Monomial],
    point: Projective,
    modulus: int,
) -> int:
    x, y, z = point
    return sum(
        coefficient
        * pow(x, monomial[0], modulus)
        * pow(y, monomial[1], modulus)
        * pow(z, monomial[2], modulus)
        for coefficient, monomial in zip(
            coefficient_vector, ordered_basis
        )
    ) % modulus


def replay_witness(
    cut: int,
    witness: dict[str, Any] | None,
    coordinates: list[list[list[int]]],
    ordered_basis: list[Monomial],
    a_points: list[Point],
    r_points: list[Point],
    target: Point,
    modulus: int,
    curve_a: int,
) -> dict[str, Any]:
    if witness is None:
        return {"present": False}
    indices = [int(value) for value in witness["r_indices"]]
    prefix_affine = affine_sum(
        [
            a_points[int(witness["a_index"])],
            *(r_points[index] for index in indices[: cut - 1]),
        ],
        modulus,
        curve_a,
    )
    prefix = (
        (0, 1, 0)
        if prefix_affine is None
        else (prefix_affine[0], prefix_affine[1], 1)
    )
    flat = 0
    for index in indices[cut - 1 :]:
        flat = flat * len(r_points) + index
    output = tuple(
        evaluate(vector_, ordered_basis, prefix, modulus)
        for vector_ in coordinates[flat]
    )
    if output[2] == 0:
        output_affine: Point = None
    else:
        inverse = pow(output[2], modulus - 2, modulus)
        output_affine = (
            output[0] * inverse % modulus,
            output[1] * inverse % modulus,
        )
    expected = affine_sum(
        [
            a_points[int(witness["a_index"])],
            *(r_points[index] for index in indices),
        ],
        modulus,
        curve_a,
    )
    residual_zero = output_affine == target
    mutated = (
        None
        if target is None
        else ((target[0] + 1) % modulus, target[1])
    )
    return {
        "present": True,
        "a_index": int(witness["a_index"]),
        "r_indices": indices,
        "suffix_flat_index": flat,
        "affine_output": encode_point(output_affine),
        "affine_output_matches": output_affine == target,
        "expected_affine_matches": output_affine == expected,
        "residual_zero": residual_zero,
        "mutated_target_residual_nonzero": output_affine != mutated,
    }


def replay_cut(
    recorded: dict[str, Any],
    curve: dict[str, Any],
    family: dict[str, Any],
    targets: dict[str, Point],
    witnesses: dict[str, dict[str, Any] | None],
) -> dict[str, Any]:
    modulus, curve_a, curve_b = (
        curve["p"],
        curve["a"],
        curve["b"],
    )
    cut = recorded["cut"]
    ordered_basis = basis(2 ** (5 - cut))
    r_points = [
        decode_point(value) for value in family["factor_base"]["points"]
    ]
    a_points = [
        decode_point(value) for value in family["progression"]["points"]
    ]
    coordinates = suffix_vectors(
        r_points,
        5 - cut,
        modulus,
        curve_a,
        curve_b,
        ordered_basis,
    )
    chunk_checks = []
    for chunk in recorded["chunks"]:
        chunk_checks.append(
            digest(coordinates[chunk["start"] : chunk["stop"]])
            == chunk["sha256"]
        )
    coordinate_ranks = [
        row_rank(
            [coordinate[index] for coordinate in coordinates],
            modulus,
        )
        for index in range(3)
    ]
    target_checks = {}
    for name, target in targets.items():
        vx, vy = specialize(coordinates, target, modulus)
        old = recorded["targets"][name]
        target_checks[name] = (
            digest(vx) == old["vx_digest"]
            and digest(vy) == old["vy_digest"]
            and row_rank(vx, modulus) == old["vx_rank"]
            and row_rank(vy, modulus) == old["vy_rank"]
            and row_rank(
                [[*left, *right] for left, right in zip(vx, vy)],
                modulus,
            )
            == old["combined_rank"]
        )
    witness_checks = {
        name: replay_witness(
            cut,
            witnesses[name],
            coordinates,
            ordered_basis,
            a_points,
            r_points,
            target,
            modulus,
            curve_a,
        )
        for name, target in targets.items()
    }
    samples_match = all(
        coordinates[int(index)] == vectors
        for index, vectors in recorded["samples"].items()
    )
    rejected_unreduced = False
    try:
        vector({(3, 0, recorded["degree"] - 3): 1}, ordered_basis)
    except AssertionError:
        rejected_unreduced = True
    return {
        "cut": cut,
        "basis_matches": recorded["basis"]
        == [list(monomial) for monomial in ordered_basis],
        "basis_dimension_matches": len(ordered_basis)
        == recorded["basis_dimension"],
        "suffix_count_matches": len(coordinates)
        == recorded["suffix_count"],
        "chunks_match": all(chunk_checks),
        "coordinate_digest_matches": digest(coordinates)
        == recorded["coordinate_digest"],
        "coordinate_ranks_match": coordinate_ranks
        == recorded["coordinate_ranks"],
        "samples_match": samples_match,
        "targets_match": all(target_checks.values()),
        "witnesses": witness_checks,
        "witnesses_valid": all(
            (
                not check["present"]
                or (
                    check["affine_output_matches"]
                    and check["expected_affine_matches"]
                    and check["residual_zero"]
                    and check["mutated_target_residual_nonzero"]
                )
            )
            for check in witness_checks.values()
        ),
        "unreduced_monomial_rejected": rejected_unreduced,
    }


def verify(
    raw_path: Path,
    typed_override: Path | None,
    v1_override: Path | None,
    v2_override: Path | None,
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    v1_path = v1_override or Path(raw["config"]["v1_input"])
    v2_path = v2_override or Path(raw["config"]["v2_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    v2 = json.loads(v2_path.read_text(encoding="utf-8"))
    typed_rows = {
        (instance["curve"]["id"], family["family"]): (
            instance["curve"],
            family,
        )
        for instance in typed["instances"]
        for family in instance["families"]
    }
    target_rows = {
        (row["curve_id"], row["family"]): {
            name: decode_point(record["target"])
            for name, record in row["cuts"][0]["targets"].items()
        }
        for row in v1["rows"]
    }
    witness_rows = {
        (row["curve_id"], row["family"]): row["first_witness"]
        for row in v2["rows"]
    }
    row_receipts = []
    for row in raw["rows"]:
        key = (row["curve_id"], row["family"])
        curve, family = typed_rows[key]
        cuts = [
            replay_cut(
                cut,
                curve,
                family,
                target_rows[key],
                witness_rows[key],
            )
            for cut in row["cuts"]
        ]
        fields = [
            "basis_matches",
            "basis_dimension_matches",
            "suffix_count_matches",
            "chunks_match",
            "coordinate_digest_matches",
            "coordinate_ranks_match",
            "samples_match",
            "targets_match",
            "witnesses_valid",
            "unreduced_monomial_rejected",
        ]
        valid = row["valid"] is True and all(
            cut[field] for cut in cuts for field in fields
        )
        row_receipts.append(
            {
                "curve_id": key[0],
                "family": key[1],
                "cuts": cuts,
                "valid": valid,
            }
        )
    top_checks = {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v3-independent-coefficients"
        ),
        "exporter_hash": raw["source"]["exporter_sha256"]
        == file_hash(EXPORTER_PATH),
        "typed_input_hash": raw["source"]["typed_input_sha256"]
        == file_hash(typed_path),
        "v1_input_hash": raw["source"]["v1_input_sha256"]
        == file_hash(v1_path),
        "v2_input_hash": raw["source"]["v2_input_sha256"]
        == file_hash(v2_path),
        "all_exports_valid": raw["summary"]["all_exports_valid"] is True,
        "independent_gate_initially_false": raw["summary"][
            "independent_coefficient_verification_complete"
        ]
        is False,
        "index_gate_false": raw["summary"]["succinct_index_constructed"]
        is False,
        "promotion_gate_false": raw["summary"]["algorithm_promotion_gate"]
        is False,
        "breakthrough_claim_false": raw["summary"]["breakthrough_claim"]
        is False,
    }
    valid = all(top_checks.values()) and all(
        row["valid"] for row in row_receipts
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v3-independent-coefficients-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "exporter_sha256": file_hash(EXPORTER_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "v1_input_sha256": file_hash(v1_path),
        "v2_input_sha256": file_hash(v2_path),
        "top_checks": top_checks,
        "row_receipts": row_receipts,
        "valid": valid,
        "boundary": (
            "Independent coefficient reconstruction and witness evaluation. "
            "It does not construct a simultaneous-zero index."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--typed-input", type=Path)
    parser.add_argument("--v1-input", type=Path)
    parser.add_argument("--v2-input", type=Path)
    args = parser.parse_args()
    receipt = verify(
        args.raw_result,
        args.typed_input,
        args.v1_input,
        args.v2_input,
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
