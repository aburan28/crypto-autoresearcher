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
from typing import Any, Iterable, Sequence


Point = tuple[int, int] | None
Projective = tuple[int, int, int]
SCRIPT_PATH = Path(__file__).resolve()
TYPED_EC_SOURCE = SCRIPT_PATH.with_name("typed_five_ec.py")
TT_SOURCE = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-TT-NORM-RANK-001"
    / "src"
    / "generate_tt_norm_rank.py"
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TYPED_EC = load_module("typed_five_ec_typed_s4_rank", TYPED_EC_SOURCE)
TT = load_module("tt_norm_rank_typed_s4_rank", TT_SOURCE)


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


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def affine_to_projective(point: Point) -> Projective:
    return (0, 1, 0) if point is None else (point[0], point[1], 1)


def nonsquare(p: int) -> int:
    for value in range(2, p):
        if pow(value, (p - 1) // 2, p) == p - 1:
            return value
    raise RuntimeError("nonsquare search exhausted")


def shape_size(shape: Sequence[int]) -> int:
    return math.prod(shape)


def flat_index(indices: Sequence[int], shape: Sequence[int]) -> int:
    value = 0
    for index, dimension in zip(indices, shape):
        if not 0 <= index < dimension:
            raise ValueError("tensor index out of range")
        value = value * dimension + index
    return value


def matrix_rows(
    values: Sequence[int], shape: Sequence[int], cut: int
) -> tuple[list[list[int]], int, int]:
    left = math.prod(shape[:cut])
    right = math.prod(shape[cut:])
    if len(values) != left * right:
        raise ValueError("tensor shape mismatch")
    if left <= right:
        return [
            list(values[row * right : (row + 1) * right])
            for row in range(left)
        ], left, right
    return [
        [values[row * right + column] for row in range(left)]
        for column in range(right)
    ], right, left


def rank_mod(
    values: Sequence[int], shape: Sequence[int], cut: int, p: int
) -> dict[str, Any]:
    rows, row_count, column_count = matrix_rows(values, shape, cut)
    basis: dict[int, list[int]] = {}
    operations = {
        "pivot_reads": 0,
        "row_updates": 0,
        "field_multiplications": 0,
        "field_subtractions": 0,
        "field_inversions": 0,
    }
    for row in rows:
        cursor = 0
        while cursor < column_count:
            operations["pivot_reads"] += 1
            if row[cursor] == 0:
                cursor += 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = pow(row[cursor], -1, p)
                operations["field_inversions"] += 1
                for position in range(cursor, column_count):
                    row[position] = row[position] * inverse % p
                    operations["field_multiplications"] += 1
                basis[cursor] = row
                break
            factor = row[cursor]
            operations["row_updates"] += 1
            for position in range(cursor, column_count):
                row[position] = (
                    row[position] - factor * prior[position]
                ) % p
                operations["field_multiplications"] += 1
                operations["field_subtractions"] += 1
            cursor += 1
    rank = len(basis)
    ambient = min(row_count, column_count)
    return {
        "cut": cut,
        "left_dimension": math.prod(shape[:cut]),
        "right_dimension": math.prod(shape[cut:]),
        "elimination_rows": row_count,
        "elimination_columns": column_count,
        "rank": rank,
        "ambient_rank": ambient,
        "rank_fraction": rank / ambient,
        "operations": operations,
    }


def hashed_indices(label: str, shape: Sequence[int]) -> tuple[int, ...]:
    return tuple(
        int.from_bytes(
            hashlib.sha256(f"{label}|{mode}".encode("ascii")).digest(),
            "big",
        )
        % dimension
        for mode, dimension in enumerate(shape)
    )


def sum_affine(
    points: Sequence[Point], p: int, a: int
) -> Point:
    total: Point = None
    for point in points:
        total = TT.affine_add(total, point, p, a)
    return total


def build_random_a(
    curve: Any,
    q: int,
    size: int,
    seed: int,
    forbidden: set[Point],
) -> dict[str, Any]:
    points = []
    sources = []
    used = set(forbidden)
    for index in range(size):
        point, source, _ = TYPED_EC.hash_to_curve_point(
            curve,
            q,
            seed,
            f"TYPED-S4-NORM-RANK|RANDOM-A|{index}",
            used,
        )
        points.append(point)
        sources.append(source)
        used.add(point)
    record = {
        "kind": "public_hash_to_curve_random_a",
        "points": [TYPED_EC.point_json(point) for point in points],
        "sources": sources,
    }
    record["digest"] = canonical_digest(record)
    return record


def tensor_source(
    p: int,
    a: int,
    b: int,
    a_points: list[Point],
    r_points: list[Point],
) -> dict[str, Any]:
    shape = [len(a_points)] + [len(r_points)] * 4
    mode_points = [
        [affine_to_projective(point) for point in a_points],
        *[
            [affine_to_projective(point) for point in r_points]
            for _ in range(4)
        ],
    ]
    outputs = []
    affine_sums = []
    invalid = 0
    replay_mismatches = 0
    started = time.perf_counter()
    for indices in itertools.product(
        *(range(dimension) for dimension in shape)
    ):
        inputs = [
            mode_points[mode][index]
            for mode, index in enumerate(indices)
        ]
        output = TT.sum_five(inputs, p, a, b)
        expected = sum_affine(
            [
                a_points[indices[0]],
                *(r_points[indices[mode]] for mode in range(1, 5)),
            ],
            p,
            a,
        )
        invalid += int(not TT.projective_on_curve(output, p, a, b))
        replay_mismatches += int(
            TT.projective_to_affine(output, p) != expected
        )
        outputs.append(output)
        affine_sums.append(expected)
    return {
        "shape": shape,
        "outputs_internal": outputs,
        "affine_sums_internal": affine_sums,
        "summary": {
            "shape": shape,
            "tuple_count": shape_size(shape),
            "rcb_calls": 4 * shape_size(shape),
            "invalid_projective_count": invalid,
            "affine_replay_mismatches": replay_mismatches,
            "output_digest": canonical_digest(
                [list(output) for output in outputs]
            ),
            "output_words": 3 * len(outputs),
            "wall_seconds": time.perf_counter() - started,
        },
    }


def locator_tensors(
    source: dict[str, Any],
    target: Point,
    p: int,
    nu: int,
    powers: list[int],
) -> dict[str, Any]:
    target_projective = affine_to_projective(target)
    xq, yq, zq = target_projective
    h = []
    zero_mismatches = 0
    witnesses = 0
    for output, affine_sum in zip(
        source["outputs_internal"], source["affine_sums_internal"]
    ):
        x, y, z = output
        ex = (zq * x - xq * z) % p
        ey = (zq * y - yq * z) % p
        value = (ex * ex - nu * ey * ey) % p
        expected_zero = affine_sum == target
        zero_mismatches += int((value == 0) != expected_zero)
        witnesses += int(value == 0)
        h.append(value)
    tensors = {"h^1": h}
    for exponent in powers:
        if exponent == 1:
            continue
        tensors[f"h^{exponent}"] = [
            pow(value, exponent, p) for value in h
        ]
    tensors["indicator"] = [int(value == 0) for value in h]
    return {
        "tensors_internal": tensors,
        "summary": {
            "target": TYPED_EC.point_json(target),
            "nu": nu,
            "zero_set_mismatches": zero_mismatches,
            "witness_count": witnesses,
            "tensor_digests": {
                name: canonical_digest(values)
                for name, values in tensors.items()
            },
        },
    }


def rank_schedule(
    tensors: dict[str, list[int]],
    shape: list[int],
    p: int,
) -> list[dict[str, Any]]:
    records = []
    for name, values in tensors.items():
        cuts = (
            (1, 2, 3, 4)
            if name in ("h^1", "indicator")
            else (2, 3)
        )
        for cut in cuts:
            record = rank_mod(values, shape, cut, p)
            record["tensor"] = name
            records.append(record)
    return records


def rank_controls() -> dict[str, Any]:
    p = 101
    shape = [3, 4, 2]
    separable = [
        (i + 1) * (j + 2) * (k + 3) % p
        for i in range(shape[0])
        for j in range(shape[1])
        for k in range(shape[2])
    ]
    spike = [0] * shape_size(shape)
    spike[flat_index((1, 2, 0), shape)] = 1
    dense = [
        int.from_bytes(
            hashlib.sha256(f"{i}|{j}|{k}".encode("ascii")).digest(),
            "big",
        )
        % p
        for i in range(shape[0])
        for j in range(shape[1])
        for k in range(shape[2])
    ]
    tensors = {
        "rank_one_separable": separable,
        "single_spike": spike,
        "deterministic_dense_hash": dense,
    }
    records = {}
    for name, values in tensors.items():
        records[name] = [
            rank_mod(values, shape, cut, p) for cut in (1, 2)
        ]
    valid = (
        all(
            record["rank"] == 1
            for name in ("rank_one_separable", "single_spike")
            for record in records[name]
        )
        and all(
            record["rank"] == record["ambient_rank"]
            for record in records["deterministic_dense_hash"]
        )
    )
    return {
        "field": p,
        "shape": shape,
        "records": records,
        "all_expected": valid,
    }


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def run_cell(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    a_variant: str,
    powers: list[int],
) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    a = curve_record["a"]
    b = curve_record["b"]
    curve = TYPED_EC.Curve(p, a, b)
    r_points = [
        point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    progression = family_record["progression"]
    if a_variant == "progression":
        a_record = {
            "kind": "public_unknown_log_progression",
            "points": progression["points"],
            "digest": progression["digest"],
        }
    elif a_variant == "random":
        a_record = build_random_a(
            curve,
            q,
            len(progression["points"]),
            family_record["run_seed"] ^ 0xA4093822,
            set(r_points),
        )
    else:
        raise ValueError(f"unsupported A variant: {a_variant}")
    a_points = [point_from_json(value) for value in a_record["points"]]
    source = tensor_source(p, a, b, a_points, r_points)
    planted_indices = hashed_indices(
        (
            "EXP-ECDLP-COORD-EXPANSION-001|TYPED-S4-NORM-RANK|"
            f"{curve_record['id']}|{family_record['family']}|{a_variant}"
        ),
        source["summary"]["shape"],
    )
    planted_points = [
        a_points[planted_indices[0]],
        *(r_points[planted_indices[mode]] for mode in range(1, 5)),
    ]
    target = sum_affine(planted_points, p, a)
    locator = locator_tensors(
        source, target, p, nonsquare(p), powers
    )
    if locator["summary"]["witness_count"] < 1:
        raise AssertionError("planted target has no witness")
    if (
        source["summary"]["invalid_projective_count"]
        or source["summary"]["affine_replay_mismatches"]
        or locator["summary"]["zero_set_mismatches"]
    ):
        raise AssertionError("source or locator semantic mismatch")
    ranks = rank_schedule(
        locator["tensors_internal"], source["summary"]["shape"], p
    )
    return {
        "curve_id": curve_record["id"],
        "q": q,
        "family": family_record["family"],
        "a_variant": a_variant,
        "a_record": a_record,
        "planted_indices": list(planted_indices),
        "source": source["summary"],
        "locator": locator["summary"],
        "ranks": ranks,
        "peak_rss_bytes_after_cell": rss_bytes(),
    }


def rank_lookup(cell: dict[str, Any], tensor: str, cut: int) -> int:
    return next(
        record["rank"]
        for record in cell["ranks"]
        if record["tensor"] == tensor and record["cut"] == cut
    )


def attach_matched_ratios(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = {}
    for cell in cells:
        grouped[
            (cell["curve_id"], cell["family"], cell["a_variant"])
        ] = cell
    comparisons = []
    for key in sorted(
        {
            (cell["curve_id"], cell["family"])
            for cell in cells
        }
    ):
        progression = grouped[(*key, "progression")]
        random_a = grouped[(*key, "random")]
        ratios = {}
        for tensor in ("h^1", "h^2", "h^8", "indicator"):
            cuts = (1, 2, 3, 4) if tensor in ("h^1", "indicator") else (2, 3)
            for cut in cuts:
                left = rank_lookup(progression, tensor, cut)
                right = rank_lookup(random_a, tensor, cut)
                ratios[f"{tensor}|cut={cut}"] = left / max(1, right)
        comparisons.append(
            {
                "curve_id": key[0],
                "q": progression["q"],
                "family": key[1],
                "progression_over_random_a_rank_ratios": ratios,
                "h8_joint_20_percent_reduction": (
                    ratios["h^8|cut=2"] <= 0.8
                    and ratios["h^8|cut=3"] <= 0.8
                ),
                "h2_same_direction": (
                    ratios["h^2|cut=2"] <= 1
                    and ratios["h^2|cut=3"] <= 1
                ),
            }
        )
    return comparisons


def run(
    result_path: Path,
    families: list[str],
    a_variants: list[str],
    powers: list[int],
) -> dict[str, Any]:
    if set(a_variants) != {"progression", "random"}:
        raise ValueError("both progression and random A controls are required")
    if not {1, 2, 8}.issubset(powers) or any(
        exponent < 1 or exponent & (exponent - 1)
        for exponent in powers
    ):
        raise ValueError(
            "powers must include 1, 2, and 8 and contain powers of two"
        )
    if len(set(powers)) != len(powers):
        raise ValueError("powers must not contain duplicates")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    controls = rank_controls()
    if not controls["all_expected"]:
        raise AssertionError("tensor rank control failed")
    cells = []
    for instance in result["instances"]:
        curve_record = instance["curve"]
        by_family = {
            row["family"]: row for row in instance["families"]
        }
        for family in families:
            for a_variant in a_variants:
                cells.append(
                    run_cell(
                        curve_record,
                        by_family[family],
                        a_variant,
                        powers,
                    )
                )
    comparisons = attach_matched_ratios(cells)
    curve_ids = sorted({cell["curve_id"] for cell in cells})
    promoted_families = []
    for family in families:
        rows = [
            row for row in comparisons if row["family"] == family
        ]
        if (
            len(rows) == len(curve_ids)
            and all(row["h8_joint_20_percent_reduction"] for row in rows)
            and all(row["h2_same_direction"] for row in rows)
        ):
            promoted_families.append(family)
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-s4-norm-rank-v1",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "typed_s4_norm_rank_sha256": sha256_file(SCRIPT_PATH),
            "typed_five_ec_sha256": sha256_file(TYPED_EC_SOURCE),
            "tt_norm_rank_sha256": sha256_file(TT_SOURCE),
            "input_result_sha256": sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "a_variants": a_variants,
            "powers": powers,
        },
        "controls": controls,
        "cells": cells,
        "comparisons": comparisons,
        "summary": {
            "cells": len(cells),
            "matched_comparisons": len(comparisons),
            "promoted_families": promoted_families,
            "positive_gate": len(promoted_families) >= 3,
            "all_controls_valid": controls["all_expected"],
            "all_semantics_valid": all(
                cell["source"]["invalid_projective_count"] == 0
                and cell["source"]["affine_replay_mismatches"] == 0
                and cell["locator"]["zero_set_mismatches"] == 0
                and cell["locator"]["witness_count"] >= 1
                for cell in cells
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Enumerative dense-rank diagnostic only. Low rank would "
                "authorize a constructive core-generation successor, not "
                "an S4 compiler or ECDLP improvement."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument(
        "--a-variants",
        nargs="+",
        choices=("progression", "random"),
        required=True,
    )
    parser.add_argument("--powers", nargs="+", type=int, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.result,
                args.families,
                args.a_variants,
                args.powers,
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
