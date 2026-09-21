#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("direct_equality_pair_cross_tree.py")
Point = tuple[int, int] | None
Shape = int | tuple["Shape", "Shape"]


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def decode_point(value: Any) -> Point:
    return None if value is None else (int(value[0]), int(value[1]))


def encode_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def ec_sum(left: Point, right: Point, modulus: int, curve_a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    lx, ly = left
    rx, ry = right
    if lx == rx and (ly + ry) % modulus == 0:
        return None
    if left == right:
        top = (3 * lx * lx + curve_a) % modulus
        bottom = (2 * ly) % modulus
    else:
        top = (ry - ly) % modulus
        bottom = (rx - lx) % modulus
    gradient = top * pow(bottom, modulus - 2, modulus) % modulus
    out_x = (gradient * gradient - lx - rx) % modulus
    out_y = (gradient * (lx - out_x) - ly) % modulus
    return out_x, out_y


def sum_sequence(
    points: Iterable[Point], modulus: int, curve_a: int
) -> Point:
    answer: Point = None
    for point in points:
        answer = ec_sum(answer, point, modulus, curve_a)
    return answer


def enumerate_shapes(first_leaf: int, leaf_count: int) -> list[Shape]:
    if leaf_count == 1:
        return [first_leaf]
    answer: list[Shape] = []
    for split in range(1, leaf_count):
        left_shapes = enumerate_shapes(first_leaf, split)
        right_shapes = enumerate_shapes(
            first_leaf + split, leaf_count - split
        )
        answer.extend(
            (left, right)
            for left in left_shapes
            for right in right_shapes
        )
    return answer


def shape_value(
    shape: Shape,
    leaves: tuple[Point, ...],
    modulus: int,
    curve_a: int,
) -> Point:
    if isinstance(shape, int):
        return leaves[shape]
    return ec_sum(
        shape_value(shape[0], leaves, modulus, curve_a),
        shape_value(shape[1], leaves, modulus, curve_a),
        modulus,
        curve_a,
    )


def homogeneous(point: Point, multiplier: int, modulus: int) -> tuple[int, int, int]:
    if point is None:
        return 0, multiplier % modulus, 0
    return (
        point[0] * multiplier % modulus,
        point[1] * multiplier % modulus,
        multiplier % modulus,
    )


def residual(
    output: tuple[int, int, int],
    target: tuple[int, int, int],
    modulus: int,
) -> tuple[int, int]:
    ox, oy, oz = output
    tx, ty, tz = target
    return (
        (tz * ox - tx * oz) % modulus,
        (tz * oy - ty * oz) % modulus,
    )


def normalize_residual(pair: tuple[int, int], modulus: int) -> tuple[int, int]:
    if pair == (0, 0):
        return pair
    pivot = pair[0] if pair[0] else pair[1]
    factor = pow(pivot, modulus - 2, modulus)
    return pair[0] * factor % modulus, pair[1] * factor % modulus


def scale_for(label: str, modulus: int) -> int:
    integer = int(hashlib.sha256(label.encode("ascii")).hexdigest(), 16)
    return integer % (modulus - 1) + 1


def feed(state: Any, value: Any) -> None:
    state.update(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
        + b"\n"
    )


def extract_targets(v1: dict[str, Any]) -> dict[tuple[str, str], dict[str, Point]]:
    answer: dict[tuple[str, str], dict[str, Point]] = {}
    for row in v1["rows"]:
        answer[(row["curve_id"], row["family"])] = {
            name: decode_point(record["target"])
            for name, record in row["cuts"][0]["targets"].items()
        }
    return answer


def replay_row(
    curve: dict[str, Any],
    family: dict[str, Any],
    targets: dict[str, Point],
) -> dict[str, Any]:
    modulus = curve["p"]
    curve_a = curve["a"]
    progression = [
        decode_point(value) for value in family["progression"]["points"]
    ]
    factor_base = [
        decode_point(value) for value in family["factor_base"]["points"]
    ]
    shapes = enumerate_shapes(0, 5)
    row_state = hashlib.sha256()
    witness_state = hashlib.sha256()
    counts = {
        "canonical_tuple_count": 0,
        "ordered_tuple_count": 0,
        "tree_evaluations": 0,
        "tree_mismatches": 0,
        "cut2_mismatches": 0,
        "cut3_mismatches": 0,
        "zero_semantic_mismatches": 0,
        "projective_scale_mismatches": 0,
        "infinity_outputs": 0,
    }
    witness_counts = {name: 0 for name in targets}
    first_witness: dict[str, dict[str, Any] | None] = {
        name: None for name in targets
    }

    for multiset in itertools.combinations_with_replacement(
        range(len(factor_base)), 4
    ):
        counts["canonical_tuple_count"] += 1
        for a_index, a_point in enumerate(progression):
            for permutation in sorted(set(itertools.permutations(multiset))):
                counts["ordered_tuple_count"] += 1
                leaves = (
                    a_point,
                    *(factor_base[index] for index in permutation),
                )
                expected = sum_sequence(leaves, modulus, curve_a)
                counts["infinity_outputs"] += int(expected is None)
                for shape in shapes:
                    counts["tree_evaluations"] += 1
                    counts["tree_mismatches"] += int(
                        shape_value(
                            shape, leaves, modulus, curve_a
                        )
                        != expected
                    )
                cut2 = ec_sum(
                    sum_sequence(leaves[:2], modulus, curve_a),
                    sum_sequence(leaves[2:], modulus, curve_a),
                    modulus,
                    curve_a,
                )
                cut3 = ec_sum(
                    sum_sequence(leaves[:3], modulus, curve_a),
                    sum_sequence(leaves[3:], modulus, curve_a),
                    modulus,
                    curve_a,
                )
                counts["cut2_mismatches"] += int(cut2 != expected)
                counts["cut3_mismatches"] += int(cut3 != expected)
                zero_flags: dict[str, bool] = {}
                for target_name, target in sorted(targets.items()):
                    if target is None:
                        raise AssertionError("V1 target unexpectedly infinity")
                    unscaled = residual(
                        homogeneous(expected, 1, modulus),
                        homogeneous(target, 1, modulus),
                        modulus,
                    )
                    is_zero = unscaled == (0, 0)
                    zero_flags[target_name] = is_zero
                    counts["zero_semantic_mismatches"] += int(
                        is_zero != (expected == target)
                    )
                    if is_zero:
                        witness_counts[target_name] += 1
                        witness = {
                            "a_index": a_index,
                            "r_indices": list(permutation),
                            "output": encode_point(expected),
                        }
                        feed(witness_state, [target_name, witness])
                        if first_witness[target_name] is None:
                            first_witness[target_name] = witness

                    label = (
                        f"{curve['id']}|{family['family']}|{a_index}|"
                        f"{','.join(map(str, permutation))}|{target_name}"
                    )
                    transformed = residual(
                        homogeneous(
                            expected,
                            scale_for(label + "|output", modulus),
                            modulus,
                        ),
                        homogeneous(
                            target,
                            scale_for(label + "|target", modulus),
                            modulus,
                        ),
                        modulus,
                    )
                    counts["projective_scale_mismatches"] += int(
                        normalize_residual(transformed, modulus)
                        != normalize_residual(unscaled, modulus)
                    )
                    counts["projective_scale_mismatches"] += int(
                        (transformed == (0, 0)) != is_zero
                    )
                feed(
                    row_state,
                    [
                        a_index,
                        list(permutation),
                        encode_point(expected),
                        zero_flags,
                    ],
                )
    return {
        **counts,
        "witness_counts": witness_counts,
        "first_witness": first_witness,
        "row_digest": row_state.hexdigest(),
        "witness_digest": witness_state.hexdigest(),
        "tree_count": len(shapes),
    }


def verify(
    raw_path: Path,
    typed_override: Path | None,
    v1_override: Path | None,
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = (
        typed_override
        if typed_override is not None
        else Path(raw["config"]["typed_input"])
    )
    v1_path = (
        v1_override
        if v1_override is not None
        else Path(raw["config"]["v1_input"])
    )
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    target_table = extract_targets(v1)
    typed_rows = {
        (instance["curve"]["id"], family["family"]): (
            instance["curve"],
            family,
        )
        for instance in typed["instances"]
        for family in instance["families"]
    }
    row_checks = []
    for recorded in raw["rows"]:
        key = (recorded["curve_id"], recorded["family"])
        curve, family = typed_rows[key]
        replayed = replay_row(curve, family, target_table[key])
        fields = [
            "canonical_tuple_count",
            "ordered_tuple_count",
            "tree_evaluations",
            "tree_mismatches",
            "cut2_mismatches",
            "cut3_mismatches",
            "zero_semantic_mismatches",
            "projective_scale_mismatches",
            "infinity_outputs",
            "witness_counts",
            "first_witness",
            "row_digest",
            "witness_digest",
            "tree_count",
        ]
        checks = {
            field: recorded[field] == replayed[field] for field in fields
        }
        checks["recorded_valid"] = recorded["valid"] is True
        row_checks.append(
            {
                "curve_id": key[0],
                "family": key[1],
                "checks": checks,
                "valid": all(checks.values()),
            }
        )
    top_checks = {
        "protocol": raw.get("protocol")
        == (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v2-independent-cross-tree"
        ),
        "generator_hash": raw["source"]["generator_sha256"]
        == file_hash(GENERATOR_PATH),
        "typed_input_hash": raw["source"]["typed_input_sha256"]
        == file_hash(typed_path),
        "v1_input_hash": raw["source"]["v1_input_sha256"]
        == file_hash(v1_path),
        "family_rows": raw["summary"]["family_rows"] == len(raw["rows"]),
        "all_rows_valid": raw["summary"]["all_rows_valid"] is True,
        "factor_gate_false": raw["summary"][
            "factor_polynomials_independently_verified"
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
        row["valid"] for row in row_checks
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v2-independent-cross-tree-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "generator_sha256": file_hash(GENERATOR_PATH),
        "verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "v1_input_sha256": file_hash(v1_path),
        "top_checks": top_checks,
        "row_checks": row_checks,
        "valid": valid,
        "boundary": (
            "Independent affine semantic replay. It does not verify the "
            "V1 polynomial factor construction."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("raw_result", type=Path)
    parser.add_argument("--typed-input", type=Path)
    parser.add_argument("--v1-input", type=Path)
    args = parser.parse_args()
    receipt = verify(
        args.raw_result, args.typed_input, args.v1_input
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":")))
    return 0 if receipt["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
