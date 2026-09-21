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


NORM = load_module("typed_s4_norm_for_factor_geometry", NORM_SOURCE)


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def actual_matrix(
    values: Sequence[int], shape: Sequence[int], cut: int
) -> tuple[list[list[int]], int, int]:
    left = math.prod(shape[:cut])
    right = math.prod(shape[cut:])
    if len(values) != left * right:
        raise ValueError("tensor shape mismatch")
    return (
        [
            list(values[row * right : (row + 1) * right])
            for row in range(left)
        ],
        left,
        right,
    )


def rank_factor(
    values: Sequence[int],
    shape: Sequence[int],
    cut: int,
    p: int,
) -> dict[str, Any]:
    matrix, left, right = actual_matrix(values, shape, cut)
    basis: list[dict[str, Any]] = []
    coefficients: list[list[int]] = []
    operations = {
        "field_multiplications": 0,
        "field_subtractions": 0,
        "field_inversions": 0,
        "row_updates": 0,
    }
    for original in matrix:
        row = list(original)
        expression = [0] * len(basis)
        for basis_index, record in enumerate(basis):
            factor = row[record["pivot"]]
            if factor == 0:
                continue
            expression[basis_index] = factor
            operations["row_updates"] += 1
            for position in range(record["pivot"], right):
                row[position] = (
                    row[position]
                    - factor * record["row"][position]
                ) % p
                operations["field_multiplications"] += 1
                operations["field_subtractions"] += 1
        pivot = next(
            (index for index, value in enumerate(row) if value), None
        )
        if pivot is not None:
            pivot_value = row[pivot]
            inverse = pow(pivot_value, -1, p)
            operations["field_inversions"] += 1
            for position in range(pivot, right):
                row[position] = row[position] * inverse % p
                operations["field_multiplications"] += 1
            basis.append({"pivot": pivot, "row": row})
            expression.append(pivot_value)
        coefficients.append(expression)
    rank = len(basis)
    u_vectors = [
        row + [0] * (rank - len(row)) for row in coefficients
    ]
    v_vectors = [record["row"] for record in basis]
    mismatches = 0
    zero_mismatches = 0
    for row_index, row in enumerate(matrix):
        for column in range(right):
            rebuilt = sum(
                u_vectors[row_index][index]
                * v_vectors[index][column]
                for index in range(rank)
            ) % p
            mismatches += int(rebuilt != row[column])
            zero_mismatches += int(
                (rebuilt == 0) != (row[column] == 0)
            )
    return {
        "u_internal": u_vectors,
        "v_internal": [
            [v_vectors[index][column] for index in range(rank)]
            for column in range(right)
        ],
        "summary": {
            "cut": cut,
            "left_count": left,
            "right_count": right,
            "rank": rank,
            "reconstruction_mismatches": mismatches,
            "zero_set_mismatches": zero_mismatches,
            "u_digest": canonical_digest(u_vectors),
            "v_basis_digest": canonical_digest(v_vectors),
            "operations": operations,
        },
    }


def canonical_projective(vector: Sequence[int], p: int) -> tuple[int, ...]:
    pivot = next((value for value in vector if value % p), None)
    if pivot is None:
        return tuple(0 for _ in vector)
    inverse = pow(pivot, -1, p)
    return tuple(value * inverse % p for value in vector)


def vector_rank(vectors: list[list[int]], p: int) -> int:
    if not vectors:
        return 0
    width = len(vectors[0])
    return NORM.rank_mod(
        [value for vector in vectors for value in vector],
        [len(vectors), width],
        1,
        p,
    )["rank"]


def affine_rank(vectors: list[list[int]], p: int) -> int:
    if len(vectors) <= 1:
        return 0
    origin = vectors[0]
    differences = [
        [
            (value - origin[index]) % p
            for index, value in enumerate(vector)
        ]
        for vector in vectors[1:]
    ]
    return vector_rank(differences, p)


def unravel(index: int, shape: Sequence[int]) -> tuple[int, ...]:
    values = []
    for dimension in reversed(shape):
        values.append(index % dimension)
        index //= dimension
    return tuple(reversed(values))


def side_geometry(vectors: list[list[int]], p: int) -> dict[str, Any]:
    projective = [canonical_projective(vector, p) for vector in vectors]
    unique = len(set(projective))
    return {
        "count": len(vectors),
        "dimension": len(vectors[0]) if vectors else 0,
        "linear_span_rank": vector_rank(vectors, p),
        "affine_span_rank": affine_rank(vectors, p),
        "projective_unique": unique,
        "projective_unique_fraction": unique / max(1, len(vectors)),
        "zero_vectors": sum(
            all(value == 0 for value in vector) for vector in vectors
        ),
        "digest": canonical_digest(vectors),
    }


def source_orbit_count(shape: Sequence[int], cut: int) -> int:
    a_size = shape[0]
    r_size = shape[1]
    left_r_axes = cut - 1
    return a_size * math.comb(
        r_size + left_r_axes - 1, left_r_axes
    )


def a_fiber_geometry(
    u_vectors: list[list[int]], shape: Sequence[int], cut: int, p: int
) -> dict[str, Any]:
    a_size = shape[0]
    trailing_shape = shape[1:cut]
    fibers = []
    for trailing in itertools.product(
        *(range(dimension) for dimension in trailing_shape)
    ):
        vectors = [
            u_vectors[
                NORM.flat_index((a_index, *trailing), shape[:cut])
            ]
            for a_index in range(a_size)
        ]
        fibers.append(
            {
                "affine_rank": affine_rank(vectors, p),
                "projective_unique": len(
                    {
                        canonical_projective(vector, p)
                        for vector in vectors
                    }
                ),
            }
        )
    affine_ranks = [record["affine_rank"] for record in fibers]
    projective_unique = [
        record["projective_unique"] for record in fibers
    ]
    return {
        "fiber_count": len(fibers),
        "a_size": a_size,
        "affine_rank_min": min(affine_ranks),
        "affine_rank_median": statistics.median(affine_ranks),
        "affine_rank_max": max(affine_ranks),
        "affine_rank_saturation_fraction": sum(
            value == a_size - 1 for value in affine_ranks
        )
        / len(affine_ranks),
        "projective_unique_min": min(projective_unique),
        "projective_unique_median": statistics.median(
            projective_unique
        ),
        "projective_unique_max": max(projective_unique),
    }


def incidence_geometry(
    values: Sequence[int], shape: Sequence[int], cut: int
) -> dict[str, Any]:
    left = math.prod(shape[:cut])
    right = math.prod(shape[cut:])
    degrees_left = [0] * left
    degrees_right = [0] * right
    canonical = set()
    ordered = 0
    for row in range(left):
        left_indices = unravel(row, shape[:cut])
        for column in range(right):
            if values[row * right + column] != 0:
                continue
            ordered += 1
            degrees_left[row] += 1
            degrees_right[column] += 1
            right_indices = unravel(column, shape[cut:])
            indices = (*left_indices, *right_indices)
            canonical.add((indices[0], *sorted(indices[1:])))
    positive_left = [value for value in degrees_left if value]
    positive_right = [value for value in degrees_right if value]
    return {
        "ordered_zero_pairs": ordered,
        "canonical_s4_witnesses": len(canonical),
        "ordered_per_canonical": ordered / max(1, len(canonical)),
        "supported_left": len(positive_left),
        "supported_right": len(positive_right),
        "left_degree_max": max(degrees_left, default=0),
        "right_degree_max": max(degrees_right, default=0),
        "left_positive_degree_median": (
            statistics.median(positive_left) if positive_left else 0
        ),
        "right_positive_degree_median": (
            statistics.median(positive_right) if positive_right else 0
        ),
        "canonical_digest": canonical_digest(sorted(canonical)),
    }


def random_vector(label: str, index: int, width: int, p: int) -> list[int]:
    return [
        int.from_bytes(
            hashlib.sha256(
                f"{label}|{index}|{coordinate}".encode("ascii")
            ).digest(),
            "big",
        )
        % p
        for coordinate in range(width)
    ]


def dense_control(
    label: str,
    left: int,
    right: int,
    rank: int,
    p: int,
    trials: int,
) -> dict[str, Any]:
    zero_counts = []
    rank_checks = []
    geometry_checks = []
    for trial in range(trials):
        u_vectors = [
            random_vector(f"{label}|{trial}|U", index, rank, p)
            for index in range(left)
        ]
        v_vectors = [
            random_vector(f"{label}|{trial}|V", index, rank, p)
            for index in range(right)
        ]
        rank_checks.append(
            {
                "u_rank": vector_rank(u_vectors, p),
                "v_rank": vector_rank(v_vectors, p),
            }
        )
        u_geometry = side_geometry(u_vectors, p)
        v_geometry = side_geometry(v_vectors, p)
        geometry_checks.append(
            {
                "u_projective_unique_fraction": u_geometry[
                    "projective_unique_fraction"
                ],
                "v_projective_unique_fraction": v_geometry[
                    "projective_unique_fraction"
                ],
                "u_affine_span_rank": u_geometry[
                    "affine_span_rank"
                ],
                "v_affine_span_rank": v_geometry[
                    "affine_span_rank"
                ],
            }
        )
        zeros = 0
        for u_vector in u_vectors:
            for v_vector in v_vectors:
                zeros += int(
                    sum(
                        left_value * right_value
                        for left_value, right_value in zip(
                            u_vector, v_vector
                        )
                    )
                    % p
                    == 0
                )
        zero_counts.append(zeros)
    return {
        "trials": trials,
        "theoretical_expected_zeros": left * right / p,
        "zero_counts": zero_counts,
        "zero_count_mean": statistics.mean(zero_counts),
        "zero_count_min": min(zero_counts),
        "zero_count_max": max(zero_counts),
        "rank_checks": rank_checks,
        "geometry_checks": geometry_checks,
        "all_rank_matched": all(
            record["u_rank"] == rank and record["v_rank"] == rank
            for record in rank_checks
        ),
        "all_geometry_generic": all(
            record["u_projective_unique_fraction"] == 1
            and record["v_projective_unique_fraction"] == 1
            and record["u_affine_span_rank"]
            == min(left - 1, rank)
            and record["v_affine_span_rank"]
            == min(right - 1, rank)
            for record in geometry_checks
        ),
    }


def reconstruct_cell(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    a_variant: str,
) -> dict[str, Any]:
    p = curve_record["p"]
    q = curve_record["q"]
    a = curve_record["a"]
    b = curve_record["b"]
    curve = NORM.TYPED_EC.Curve(p, a, b)
    r_points = [
        NORM.point_from_json(value)
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
        a_record = NORM.build_random_a(
            curve,
            q,
            len(progression["points"]),
            family_record["run_seed"] ^ 0xA4093822,
            set(r_points),
        )
    else:
        raise ValueError(f"unsupported A variant: {a_variant}")
    a_points = [
        NORM.point_from_json(value) for value in a_record["points"]
    ]
    source = NORM.tensor_source(p, a, b, a_points, r_points)
    planted_indices = NORM.hashed_indices(
        (
            "EXP-ECDLP-COORD-EXPANSION-001|TYPED-S4-NORM-RANK|"
            f"{curve_record['id']}|{family_record['family']}|{a_variant}"
        ),
        source["summary"]["shape"],
    )
    planted_points = [
        a_points[planted_indices[0]],
        *(
            r_points[planted_indices[mode]]
            for mode in range(1, 5)
        ),
    ]
    target = NORM.sum_affine(planted_points, p, a)
    locator = NORM.locator_tensors(
        source, target, p, NORM.nonsquare(p), [1]
    )
    return {
        "p": p,
        "q": q,
        "a_record": a_record,
        "planted_indices": list(planted_indices),
        "source": source["summary"],
        "h_internal": locator["tensors_internal"]["h^1"],
        "locator": locator["summary"],
    }


def run_cell(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
    a_variant: str,
    cuts: list[int],
    dense_controls: int,
) -> dict[str, Any]:
    reconstructed = reconstruct_cell(
        curve_record, family_record, a_variant
    )
    p = reconstructed["p"]
    shape = reconstructed["source"]["shape"]
    factors = []
    for cut in cuts:
        factor = rank_factor(
            reconstructed["h_internal"], shape, cut, p
        )
        summary = factor["summary"]
        if (
            summary["reconstruction_mismatches"]
            or summary["zero_set_mismatches"]
        ):
            raise AssertionError("rank factor reconstruction failed")
        control = dense_control(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|"
                f"{curve_record['id']}|{family_record['family']}|"
                f"{a_variant}|cut={cut}"
            ),
            summary["left_count"],
            summary["right_count"],
            summary["rank"],
            p,
            dense_controls,
        )
        if (
            not control["all_rank_matched"]
            or not control["all_geometry_generic"]
        ):
            raise AssertionError("dense factor control failed")
        u_geometry = side_geometry(factor["u_internal"], p)
        orbit_count = source_orbit_count(shape, cut)
        u_geometry["source_symmetry_orbit_count"] = orbit_count
        u_geometry["projective_unique_fraction_of_source_orbits"] = (
            u_geometry["projective_unique"] / orbit_count
        )
        factors.append(
            {
                **summary,
                "u_geometry": u_geometry,
                "v_geometry": side_geometry(
                    factor["v_internal"], p
                ),
                "a_fibers": a_fiber_geometry(
                    factor["u_internal"], shape, cut, p
                ),
                "incidence": incidence_geometry(
                    reconstructed["h_internal"], shape, cut
                ),
                "dense_control": control,
            }
        )
    if (
        reconstructed["source"]["invalid_projective_count"]
        or reconstructed["source"]["affine_replay_mismatches"]
        or reconstructed["locator"]["zero_set_mismatches"]
        or reconstructed["locator"]["witness_count"] < 1
    ):
        raise AssertionError("source or locator semantic mismatch")
    return {
        "curve_id": curve_record["id"],
        "p": p,
        "q": reconstructed["q"],
        "family": family_record["family"],
        "a_variant": a_variant,
        "a_record": reconstructed["a_record"],
        "planted_indices": reconstructed["planted_indices"],
        "source": reconstructed["source"],
        "locator": reconstructed["locator"],
        "factors": factors,
        "peak_rss_bytes_after_cell": rss_bytes(),
    }


def factor_by_cut(cell: dict[str, Any], cut: int) -> dict[str, Any]:
    return next(
        factor for factor in cell["factors"] if factor["cut"] == cut
    )


def matched_comparisons(
    cells: list[dict[str, Any]], cuts: list[int]
) -> list[dict[str, Any]]:
    lookup = {
        (cell["curve_id"], cell["family"], cell["a_variant"]): cell
        for cell in cells
    }
    comparisons = []
    for curve_id, family in sorted(
        {(cell["curve_id"], cell["family"]) for cell in cells}
    ):
        progression = lookup[(curve_id, family, "progression")]
        random_a = lookup[(curve_id, family, "random")]
        cut_records = []
        for cut in cuts:
            left = factor_by_cut(progression, cut)
            right = factor_by_cut(random_a, cut)
            unique_ratio = (
                left["u_geometry"]["projective_unique_fraction"]
                / max(
                    right["u_geometry"][
                        "projective_unique_fraction"
                    ],
                    1e-300,
                )
            )
            fiber_ratio = (
                left["a_fibers"]["affine_rank_median"]
                / max(
                    right["a_fibers"]["affine_rank_median"], 1e-300
                )
            )
            cut_records.append(
                {
                    "cut": cut,
                    "u_projective_unique_fraction_ratio": unique_ratio,
                    "a_fiber_affine_rank_median_ratio": fiber_ratio,
                    "joint_20_percent_collapse": (
                        unique_ratio <= 0.8 and fiber_ratio <= 0.8
                    ),
                }
            )
        comparisons.append(
            {
                "curve_id": curve_id,
                "q": progression["q"],
                "family": family,
                "cuts": cut_records,
                "all_cuts_collapse": all(
                    record["joint_20_percent_collapse"]
                    for record in cut_records
                ),
            }
        )
    return comparisons


def run(
    result_path: Path,
    families: list[str],
    a_variants: list[str],
    cuts: list[int],
    dense_controls: int,
) -> dict[str, Any]:
    if set(a_variants) != {"progression", "random"}:
        raise ValueError("both progression and random A are required")
    if sorted(set(cuts)) != [2, 3]:
        raise ValueError("cuts must contain exactly 2 and 3")
    if dense_controls < 1:
        raise ValueError("at least one dense control is required")
    typed_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    cells = []
    for instance in typed_result["instances"]:
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
                        cuts,
                        dense_controls,
                    )
                )
    comparisons = matched_comparisons(cells, cuts)
    curve_ids = {cell["curve_id"] for cell in cells}
    promoted = []
    for family in families:
        rows = [
            comparison
            for comparison in comparisons
            if comparison["family"] == family
        ]
        if (
            len(rows) == len(curve_ids)
            and all(row["all_cuts_collapse"] for row in rows)
        ):
            promoted.append(family)
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "typed-s4-factor-geometry-v1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "source": {
            "typed_s4_factor_geometry_sha256": NORM.sha256_file(
                SCRIPT_PATH
            ),
            "typed_s4_norm_rank_sha256": NORM.sha256_file(NORM_SOURCE),
            "input_result_sha256": NORM.sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "a_variants": a_variants,
            "cuts": cuts,
            "dense_controls": dense_controls,
        },
        "cells": cells,
        "comparisons": comparisons,
        "summary": {
            "cells": len(cells),
            "matched_comparisons": len(comparisons),
            "promoted_families": promoted,
            "positive_gate": len(promoted) >= 3,
            "all_semantics_valid": all(
                cell["source"]["invalid_projective_count"] == 0
                and cell["source"]["affine_replay_mismatches"] == 0
                and cell["locator"]["zero_set_mismatches"] == 0
                and cell["locator"]["witness_count"] >= 1
                and all(
                    factor["reconstruction_mismatches"] == 0
                    and factor["zero_set_mismatches"] == 0
                    and factor["dense_control"]["all_rank_matched"]
                    and factor["dense_control"]["all_geometry_generic"]
                    for factor in cell["factors"]
                )
                for cell in cells
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Enumerative invariant-geometry diagnostic only. A "
                "positive signal would require a constructive indexed join."
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
    parser.add_argument("--cuts", nargs="+", type=int, required=True)
    parser.add_argument("--dense-controls", type=int, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(
                args.result,
                args.families,
                args.a_variants,
                args.cuts,
                args.dense_controls,
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
