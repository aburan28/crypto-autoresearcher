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
DIRECT_SOURCE = SCRIPT_PATH.with_name("direct_prefix_factor.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


DIRECT = load_module("direct_prefix_for_equality_pair", DIRECT_SOURCE)
NORM = DIRECT.NORM
TYPED = DIRECT.TYPED
TT = DIRECT.TT
Point = DIRECT.Point
Projective = DIRECT.Projective
Polynomial = DIRECT.Polynomial


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


def canonical_pair(left: int, right: int, p: int) -> tuple[int, int]:
    left %= p
    right %= p
    if left == 0 and right == 0:
        return 0, 0
    pivot = left if left else right
    inverse = pow(pivot, -1, p)
    return left * inverse % p, right * inverse % p


def residual_pair(
    output: Projective, target: Point, p: int
) -> tuple[int, int]:
    x, y, z = output
    xq, yq, zq = NORM.affine_to_projective(target)
    return (
        (zq * x - xq * z) % p,
        (zq * y - yq * z) % p,
    )


def derive_suffix_coordinates(
    suffix_points: Sequence[Point],
    p: int,
    a: int,
    b: int,
) -> tuple[Polynomial, Polynomial, Polynomial]:
    state = DIRECT.variables()
    for point in suffix_points:
        state = DIRECT.rcb_add_polynomial(
            state, NORM.affine_to_projective(point), p, a, b
        )
    return state


def specialize_vectors(
    coordinate_vectors: list[list[list[int]]],
    target: Point,
    p: int,
) -> tuple[list[list[int]], list[list[int]]]:
    xq, yq, zq = NORM.affine_to_projective(target)
    x_vectors = []
    y_vectors = []
    for x_vector, y_vector, z_vector in coordinate_vectors:
        x_vectors.append(
            [
                (zq * x - xq * z) % p
                for x, z in zip(x_vector, z_vector)
            ]
        )
        y_vectors.append(
            [
                (zq * y - yq * z) % p
                for y, z in zip(y_vector, z_vector)
            ]
        )
    return x_vectors, y_vectors


def run_cut(
    cut: int,
    p: int,
    a: int,
    b: int,
    a_points: list[Point],
    r_points: list[Point],
    targets: dict[str, Point],
) -> dict[str, Any]:
    suffix_axes = 5 - cut
    degree = 2 ** (5 - cut)
    monomials = DIRECT.basis(degree)
    if len(monomials) != 3 * degree:
        raise AssertionError("unexpected equality-pair basis")
    prefix_indices = list(
        itertools.product(
            range(len(a_points)),
            *(range(len(r_points)) for _ in range(cut - 1)),
        )
    )
    suffix_indices = list(
        itertools.product(
            *(range(len(r_points)) for _ in range(suffix_axes))
        )
    )
    prefixes = [
        DIRECT.prefix_projective(
            [
                a_points[indices[0]],
                *(r_points[index] for index in indices[1:]),
            ],
            p,
            a,
            b,
        )
        for indices in prefix_indices
    ]
    u_vectors = [
        DIRECT.evaluate_basis(monomials, point, p)
        for point in prefixes
    ]
    coordinate_vectors = []
    coordinate_degrees = set()
    coordinate_nnz = []
    for indices in suffix_indices:
        coordinates = derive_suffix_coordinates(
            [r_points[index] for index in indices], p, a, b
        )
        coordinate_degrees.update(
            DIRECT.polynomial_degree(poly) for poly in coordinates
        )
        vectors = [
            DIRECT.coefficient_vector(poly, monomials)
            for poly in coordinates
        ]
        coordinate_vectors.append(vectors)
        coordinate_nnz.extend(
            sum(value != 0 for value in vector) for vector in vectors
        )
    target_rows = {}
    nu = NORM.nonsquare(p)
    for target_name, target in targets.items():
        vx_vectors, vy_vectors = specialize_vectors(
            coordinate_vectors, target, p
        )
        factor_mismatches = 0
        norm_mismatches = 0
        zero_mismatches = 0
        affine_section_mismatches = 0
        permutation_mismatches = 0
        permutation_classes: dict[
            tuple[int, tuple[int, ...]], tuple[int, int]
        ] = {}
        factor_pairs = []
        exact_pairs = []
        for prefix_index, _ in enumerate(prefix_indices):
            prefix = prefixes[prefix_index]
            for suffix_index, indices in enumerate(suffix_indices):
                ex = sum(
                    left * right
                    for left, right in zip(
                        u_vectors[prefix_index],
                        vx_vectors[suffix_index],
                    )
                ) % p
                ey = sum(
                    left * right
                    for left, right in zip(
                        u_vectors[prefix_index],
                        vy_vectors[suffix_index],
                    )
                ) % p
                output = prefix
                for index in indices:
                    output = TT.rcb_add(
                        output,
                        NORM.affine_to_projective(r_points[index]),
                        p,
                        a,
                        b,
                    )
                exact_ex, exact_ey = residual_pair(output, target, p)
                factor_pairs.append([ex, ey])
                exact_pairs.append([exact_ex, exact_ey])
                factor_mismatches += int(
                    (ex, ey) != (exact_ex, exact_ey)
                )
                norm = (ex * ex - nu * ey * ey) % p
                exact_norm = NORM.locator_tensors(
                    {
                        "outputs_internal": [output],
                        "affine_sums_internal": [
                            TT.projective_to_affine(output, p)
                        ],
                    },
                    target,
                    p,
                    nu,
                    [1],
                )["tensors_internal"]["h^1"][0]
                norm_mismatches += int(norm != exact_norm)
                affine = TT.projective_to_affine(output, p)
                zero_mismatches += int(
                    (ex == 0 and ey == 0) != (affine == target)
                )
                canonical = canonical_pair(ex, ey, p)
                if affine is not None:
                    affine_pair = residual_pair(
                        NORM.affine_to_projective(affine), target, p
                    )
                    affine_section_mismatches += int(
                        canonical
                        != canonical_pair(*affine_pair, p)
                    )
                key = (prefix_index, tuple(sorted(indices)))
                prior = permutation_classes.setdefault(key, canonical)
                permutation_mismatches += int(prior != canonical)
        word_bytes = max(1, (p.bit_length() + 7) // 8)
        target_rows[target_name] = {
            "target": TYPED.point_json(target),
            "vx_rank": DIRECT.vector_rank(vx_vectors, p),
            "vy_rank": DIRECT.vector_rank(vy_vectors, p),
            "combined_v_rank": DIRECT.vector_rank(
                [
                    [*vx, *vy]
                    for vx, vy in zip(vx_vectors, vy_vectors)
                ],
                p,
            ),
            "vx_digest": canonical_digest(vx_vectors),
            "vy_digest": canonical_digest(vy_vectors),
            "specialized_advice_field_elements": (
                2 * len(suffix_indices) * len(monomials)
            ),
            "specialized_advice_bytes": (
                2
                * len(suffix_indices)
                * len(monomials)
                * word_bytes
            ),
            "specialization_multiplications": (
                4 * len(suffix_indices) * len(monomials)
            ),
            "pair_verifications": (
                len(prefix_indices) * len(suffix_indices)
            ),
            "factor_mismatches": factor_mismatches,
            "norm_reconstruction_mismatches": norm_mismatches,
            "zero_set_mismatches": zero_mismatches,
            "affine_section_mismatches": affine_section_mismatches,
            "permutation_class_count": len(permutation_classes),
            "permutation_mismatches": permutation_mismatches,
            "factor_pair_digest": canonical_digest(factor_pairs),
            "exact_pair_digest": canonical_digest(exact_pairs),
        }
    word_bytes = max(1, (p.bit_length() + 7) // 8)
    return {
        "cut": cut,
        "degree": degree,
        "basis_dimension": len(monomials),
        "basis_digest": canonical_digest(monomials),
        "prefix_count": len(prefix_indices),
        "suffix_count": len(suffix_indices),
        "u_rank": DIRECT.vector_rank(u_vectors, p),
        "u_digest": canonical_digest(u_vectors),
        "coordinate_degrees": sorted(coordinate_degrees),
        "coordinate_nnz_min": min(coordinate_nnz),
        "coordinate_nnz_median": statistics.median(coordinate_nnz),
        "coordinate_nnz_max": max(coordinate_nnz),
        "coordinate_digest": canonical_digest(coordinate_vectors),
        "target_independent_advice_field_elements": (
            3 * len(suffix_indices) * len(monomials)
        ),
        "target_independent_advice_bytes": (
            3 * len(suffix_indices) * len(monomials) * word_bytes
        ),
        "targets": target_rows,
    }


def run_family(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
) -> dict[str, Any]:
    p = curve_record["p"]
    a = curve_record["a"]
    b = curve_record["b"]
    a_points = [
        NORM.point_from_json(value)
        for value in family_record["progression"]["points"]
    ]
    r_points = [
        NORM.point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    targets = DIRECT.build_targets(
        curve_record, family_record, a_points, r_points
    )
    cuts = [
        run_cut(cut, p, a, b, a_points, r_points, targets)
        for cut in (2, 3)
    ]
    valid = all(
        row["basis_dimension"] == 3 * row["degree"]
        and row["coordinate_degrees"] == [row["degree"]]
        and all(
            target["factor_mismatches"] == 0
            and target["norm_reconstruction_mismatches"] == 0
            and target["zero_set_mismatches"] == 0
            and target["affine_section_mismatches"] == 0
            and target["permutation_mismatches"] == 0
            and target["factor_pair_digest"]
            == target["exact_pair_digest"]
            for target in row["targets"].values()
        )
        for row in cuts
    )
    return {
        "curve_id": curve_record["id"],
        "p": p,
        "q": curve_record["q"],
        "family": family_record["family"],
        "a_size": len(a_points),
        "r_size": len(r_points),
        "cuts": cuts,
        "valid": valid,
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def controls() -> dict[str, Any]:
    p = 101
    pair = (7, 19)
    scale = 23
    return {
        "canonical_pair_scale_invariant": (
            canonical_pair(*pair, p)
            == canonical_pair(
                scale * pair[0], scale * pair[1], p
            )
        ),
        "zero_pair_distinct": canonical_pair(0, 0, p) == (0, 0),
        "cut_dimensions": {
            "cut_2": len(DIRECT.basis(8)),
            "cut_3": len(DIRECT.basis(4)),
        },
    }


def run(result_path: Path, families: list[str]) -> dict[str, Any]:
    source_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    control = controls()
    if (
        not control["canonical_pair_scale_invariant"]
        or not control["zero_pair_distinct"]
        or control["cut_dimensions"] != {"cut_2": 24, "cut_3": 12}
    ):
        raise AssertionError("equality-pair control failed")
    rows = []
    for instance in source_result["instances"]:
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        for family in families:
            rows.append(
                run_family(instance["curve"], by_family[family])
            )
    scaling = {}
    for cut in (2, 3):
        scaling[f"cut_{cut}"] = {
            "target_independent_advice_field_elements": (
                DIRECT.fit_exponent(
                    [
                        (
                            row["q"],
                            next(
                                item
                                for item in row["cuts"]
                                if item["cut"] == cut
                            )["target_independent_advice_field_elements"],
                        )
                        for row in rows
                        if row["family"] == families[0]
                    ]
                )
            ),
            "specialized_advice_field_elements": (
                DIRECT.fit_exponent(
                    [
                        (
                            row["q"],
                            next(
                                item
                                for item in row["cuts"]
                                if item["cut"] == cut
                            )["targets"]["planted"][
                                "specialized_advice_field_elements"
                            ],
                        )
                        for row in rows
                        if row["family"] == families[0]
                    ]
                )
            ),
        }
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-direct-equality-pair-v1"
        ),
        "claim_status": [
            "RESTRICTED THEOREM",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "direct_equality_pair_sha256": sha256_file(SCRIPT_PATH),
            "direct_prefix_factor_sha256": sha256_file(DIRECT_SOURCE),
            "typed_s4_norm_rank_sha256": sha256_file(
                DIRECT.NORM_SOURCE
            ),
            "typed_five_ec_sha256": sha256_file(
                NORM.TYPED_EC_SOURCE
            ),
            "tt_norm_rank_sha256": sha256_file(NORM.TT_SOURCE),
            "input_result_sha256": sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
        },
        "controls": control,
        "rows": rows,
        "scaling": scaling,
        "summary": {
            "family_rows": len(rows),
            "all_controls_valid": (
                control["canonical_pair_scale_invariant"]
                and control["zero_pair_distinct"]
                and control["cut_dimensions"]
                == {"cut_2": 24, "cut_3": 12}
            ),
            "all_factorizations_valid": all(
                row["valid"] for row in rows
            ),
            "gauge_invariant_pair_gate": all(
                row["valid"] for row in rows
            ),
            "simultaneous_zero_index_constructed": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": (
                "Exact projective equality-pair factor compiler. It "
                "does not provide a simultaneous-zero reporting index."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.result, args.families),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
