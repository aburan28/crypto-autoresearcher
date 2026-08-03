#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import itertools
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
BASE_VERIFIER_PATH = SCRIPT_PATH.with_name(
    "verify_direct_equality_pair_cross_tree.py"
)


def load_base() -> Any:
    spec = importlib.util.spec_from_file_location(
        "cross_tree_base_verifier_for_strict", BASE_VERIFIER_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load base verifier")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASE = load_base()
Point = BASE.Point
Shape = BASE.Shape


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def canonical_digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    ).hexdigest()


def on_curve(point: Point, modulus: int, curve_a: int, curve_b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (
        y * y - x * x * x - curve_a * x - curve_b
    ) % modulus == 0


def expected_rows(
    typed: dict[str, Any], families: list[str]
) -> list[tuple[str, str]]:
    return [
        (instance["curve"]["id"], family)
        for instance in typed["instances"]
        for family in families
    ]


def tracked_add(
    left: Point,
    right: Point,
    modulus: int,
    curve_a: int,
    counts: dict[str, int],
) -> Point:
    counts["additions"] += 1
    if left is None or right is None:
        counts["identity_returns"] += 1
        return right if left is None else left
    if left[0] == right[0] and (left[1] + right[1]) % modulus == 0:
        counts["inverse_returns"] += 1
        return None
    if left == right:
        counts["doublings"] += 1
        counts["multiplications"] += 4
    else:
        counts["multiplications"] += 2
    counts["inversions"] += 1
    counts["multiplications"] += 4
    return BASE.ec_sum(left, right, modulus, curve_a)


def tracked_fold(
    values: tuple[Point, ...],
    modulus: int,
    curve_a: int,
    counts: dict[str, int],
) -> Point:
    result: Point = None
    for value in values:
        result = tracked_add(
            result, value, modulus, curve_a, counts
        )
    return result


def tracked_tree(
    shape: Shape,
    leaves: tuple[Point, ...],
    modulus: int,
    curve_a: int,
    counts: dict[str, int],
    cache: dict[Shape, Point],
) -> Point:
    if shape in cache:
        return cache[shape]
    if isinstance(shape, int):
        result = leaves[shape]
    else:
        result = tracked_add(
            tracked_tree(
                shape[0], leaves, modulus, curve_a, counts, cache
            ),
            tracked_tree(
                shape[1], leaves, modulus, curve_a, counts, cache
            ),
            modulus,
            curve_a,
            counts,
        )
    cache[shape] = result
    return result


def replay_operations(
    curve: dict[str, Any], family: dict[str, Any]
) -> dict[str, int]:
    modulus, curve_a = curve["p"], curve["a"]
    progression = tuple(
        BASE.decode_point(value)
        for value in family["progression"]["points"]
    )
    factor_base = tuple(
        BASE.decode_point(value)
        for value in family["factor_base"]["points"]
    )
    shapes = BASE.enumerate_shapes(0, 5)
    counts = {
        "additions": 0,
        "doublings": 0,
        "identity_returns": 0,
        "inverse_returns": 0,
        "inversions": 0,
        "multiplications": 0,
    }
    for multiset in itertools.combinations_with_replacement(
        range(len(factor_base)), 4
    ):
        for a_point in progression:
            for permutation in sorted(set(itertools.permutations(multiset))):
                leaves = (
                    a_point,
                    *(factor_base[index] for index in permutation),
                )
                tracked_fold(leaves, modulus, curve_a, counts)
                cache: dict[Shape, Point] = {}
                for shape in shapes:
                    tracked_tree(
                        shape,
                        leaves,
                        modulus,
                        curve_a,
                        counts,
                        cache,
                    )
                tracked_add(
                    tracked_fold(
                        leaves[:2], modulus, curve_a, counts
                    ),
                    tracked_fold(
                        leaves[2:], modulus, curve_a, counts
                    ),
                    modulus,
                    curve_a,
                    counts,
                )
                tracked_add(
                    tracked_fold(
                        leaves[:3], modulus, curve_a, counts
                    ),
                    tracked_fold(
                        leaves[3:], modulus, curve_a, counts
                    ),
                    modulus,
                    curve_a,
                    counts,
                )
    return counts


def row_valid(row: dict[str, Any]) -> bool:
    return (
        row["tree_count"] == 14
        and all(row["controls"].values())
        and row["tree_mismatches"] == 0
        and row["cut2_mismatches"] == 0
        and row["cut3_mismatches"] == 0
        and row["zero_semantic_mismatches"] == 0
        and row["projective_scale_mismatches"] == 0
        and row["mutation_control_failures"] == 0
        and row["witness_counts"]["planted"] > 0
    )


def envelope_checks(
    raw: dict[str, Any],
    typed: dict[str, Any],
    v1: dict[str, Any],
) -> dict[str, bool]:
    families = raw["config"]["families"]
    expected = expected_rows(typed, families)
    actual = [
        (row["curve_id"], row["family"]) for row in raw["rows"]
    ]
    typed_map = {
        (instance["curve"]["id"], family["family"]): (
            instance["curve"],
            family,
        )
        for instance in typed["instances"]
        for family in instance["families"]
    }
    v1_map = {
        (row["curve_id"], row["family"]): row for row in v1["rows"]
    }
    tree_digest = canonical_digest(BASE.enumerate_shapes(0, 5))
    rows_present = actual == expected and len(actual) == len(set(actual))
    row_controls = all(
        row["tree_digest"] == tree_digest
        and row["valid"] == row_valid(row)
        and row["operations"]
        == replay_operations(*typed_map[(row["curve_id"], row["family"])])
        for row in raw["rows"]
    ) if rows_present else False
    target_checks = True
    if rows_present:
        for row in raw["rows"]:
            key = (row["curve_id"], row["family"])
            curve, _ = typed_map[key]
            cut_targets = [
                {
                    name: BASE.decode_point(record["target"])
                    for name, record in cut["targets"].items()
                }
                for cut in v1_map[key]["cuts"]
            ]
            target_checks = target_checks and cut_targets[0] == cut_targets[1]
            target_checks = target_checks and all(
                target is not None
                and on_curve(
                    target, curve["p"], curve["a"], curve["b"]
                )
                for target in cut_targets[0].values()
            )
    summary = raw["summary"]
    summary_checks = rows_present and (
        summary["family_rows"] == len(raw["rows"])
        and summary["all_rows_valid"]
        == all(row["valid"] for row in raw["rows"])
        and summary["total_ordered_tuples"]
        == sum(row["ordered_tuple_count"] for row in raw["rows"])
        and summary["total_tree_evaluations"]
        == sum(row["tree_evaluations"] for row in raw["rows"])
        and summary["total_planted_witnesses"]
        == sum(
            row["witness_counts"]["planted"] for row in raw["rows"]
        )
        and summary["total_held_out_witnesses"]
        == sum(
            row["witness_counts"]["held_out"] for row in raw["rows"]
        )
        and summary["total_infinity_outputs"]
        == sum(row["infinity_outputs"] for row in raw["rows"])
    )
    return {
        "expected_row_sequence_exact": rows_present,
        "row_controls_validity_tree_and_operations": row_controls,
        "summary_totals_exact": summary_checks,
        "targets_finite_on_curve_and_equal_across_cuts": target_checks,
    }


def mutation_suite(
    raw: dict[str, Any],
    typed: dict[str, Any],
    v1: dict[str, Any],
) -> dict[str, bool]:
    mutations: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    dropped = copy.deepcopy(raw)
    dropped["rows"].pop()
    mutations["dropped_row"] = (dropped, v1)
    duplicate = copy.deepcopy(raw)
    duplicate["rows"].append(copy.deepcopy(duplicate["rows"][0]))
    mutations["duplicate_row"] = (duplicate, v1)
    total = copy.deepcopy(raw)
    total["summary"]["total_ordered_tuples"] += 1
    mutations["summary_total"] = (total, v1)
    control = copy.deepcopy(raw)
    first_control = next(iter(control["rows"][0]["controls"]))
    control["rows"][0]["controls"][first_control] = False
    mutations["control"] = (control, v1)
    operation = copy.deepcopy(raw)
    operation["rows"][0]["operations"]["additions"] += 1
    mutations["operation"] = (operation, v1)
    tree = copy.deepcopy(raw)
    tree["rows"][0]["tree_digest"] = "0" * 64
    mutations["tree_digest"] = (tree, v1)
    mutation = copy.deepcopy(raw)
    mutation["rows"][0]["mutation_control_failures"] += 1
    mutations["mutation_counter"] = (mutation, v1)
    target_v1 = copy.deepcopy(v1)
    target_v1["rows"][0]["cuts"][1]["targets"]["planted"][
        "target"
    ][0] += 1
    mutations["cross_cut_target"] = (raw, target_v1)
    return {
        name: not all(
            envelope_checks(candidate, typed, candidate_v1).values()
        )
        for name, (candidate, candidate_v1) in mutations.items()
    }


def verify(
    raw_path: Path,
    typed_override: Path | None,
    v1_override: Path | None,
) -> dict[str, Any]:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    typed_path = typed_override or Path(raw["config"]["typed_input"])
    v1_path = v1_override or Path(raw["config"]["v1_input"])
    typed = json.loads(typed_path.read_text(encoding="utf-8"))
    v1 = json.loads(v1_path.read_text(encoding="utf-8"))
    base_receipt = BASE.verify(raw_path, typed_path, v1_path)
    envelope = envelope_checks(raw, typed, v1)
    mutations = mutation_suite(raw, typed, v1)
    valid = (
        base_receipt["valid"]
        and all(envelope.values())
        and all(mutations.values())
    )
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "direct-equality-pair-v2-strict-verifier"
        ),
        "raw_result_sha256": file_hash(raw_path),
        "base_verifier_sha256": file_hash(BASE_VERIFIER_PATH),
        "strict_verifier_sha256": file_hash(SCRIPT_PATH),
        "typed_input_sha256": file_hash(typed_path),
        "v1_input_sha256": file_hash(v1_path),
        "base_arithmetic_replay_valid": base_receipt["valid"],
        "envelope_checks": envelope,
        "mutation_rejections": mutations,
        "held_out_target_derivation_regenerated": False,
        "valid": valid,
        "boundary": (
            "Closed fixed-fixture envelope plus independent arithmetic "
            "replay. Held-out target selection is not regenerated."
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
