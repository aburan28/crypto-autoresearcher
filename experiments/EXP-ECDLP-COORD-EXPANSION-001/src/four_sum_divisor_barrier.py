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
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
TYPED_SOURCE = SCRIPT_PATH.with_name("typed_five_ec.py")
Point = tuple[int, int] | None


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TYPED = load_module("typed_five_ec_for_divisor_barrier", TYPED_SOURCE)


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


def point_key(point: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if point is None else (1, point[0], point[1])


def point_payload(points: Iterable[Point]) -> list[list[int] | None]:
    return [
        TYPED.point_json(point)
        for point in sorted(points, key=point_key)
    ]


def sum_indices(
    curve: Any, points: list[Point], indices: tuple[int, ...]
) -> Point:
    total: Point = None
    ops = TYPED.Ops()
    for index in indices:
        total = curve.add(total, points[index], ops)
    return total


def support_level(
    curve: Any, points: list[Point], arity: int
) -> dict[str, Any]:
    counter: Counter[Point] = Counter()
    tuple_count = 0
    group_additions = 0
    for indices in itertools.combinations_with_replacement(
        range(len(points)), arity
    ):
        counter[sum_indices(curve, points, indices)] += 1
        tuple_count += 1
        group_additions += arity
    multiplicities = list(counter.values())
    probabilities = [value / tuple_count for value in multiplicities]
    entropy = -sum(
        probability * math.log2(probability)
        for probability in probabilities
    )
    x_support = {
        None if point is None else point[0] for point in counter
    }
    return {
        "support_internal": set(counter),
        "summary": {
            "arity": arity,
            "canonical_tuple_count": tuple_count,
            "unique_point_support": len(counter),
            "unique_x_support": len(x_support),
            "support_fraction": len(counter) / tuple_count,
            "collision_count": tuple_count - len(counter),
            "multiplicity_min": min(multiplicities),
            "multiplicity_median": statistics.median(multiplicities),
            "multiplicity_max": max(multiplicities),
            "multiplicity_entropy_bits": entropy,
            "group_additions_charged": group_additions,
            "support_digest": canonical_digest(
                point_payload(counter)
            ),
            "multiplicity_digest": canonical_digest(
                [
                    [TYPED.point_json(point), counter[point]]
                    for point in sorted(counter, key=point_key)
                ]
            ),
        },
    }


def d2_pair_support(
    curve: Any, d2_support: set[Point]
) -> dict[str, Any]:
    points = sorted(d2_support, key=point_key)
    support = set()
    attempts = 0
    ops = TYPED.Ops()
    for left_index, left in enumerate(points):
        for right in points[left_index:]:
            support.add(curve.add(left, right, ops))
            attempts += 1
    return {
        "support_internal": support,
        "summary": {
            "unique_d2_points": len(points),
            "canonical_pair_attempts": attempts,
            "unique_point_support": len(support),
            "group_operations": ops.group_operations,
            "field_multiplications": ops.field_multiplications,
            "field_inversions": ops.field_inversions,
            "support_digest": canonical_digest(point_payload(support)),
        },
    }


def run_family(
    curve_record: dict[str, Any],
    family_record: dict[str, Any],
) -> dict[str, Any]:
    curve = TYPED.Curve(
        curve_record["p"], curve_record["a"], curve_record["b"]
    )
    points = [
        TYPED.point_from_json(value)
        for value in family_record["factor_base"]["points"]
    ]
    levels = {
        arity: support_level(curve, points, arity)
        for arity in (2, 3, 4)
    }
    d2_pair = d2_pair_support(curve, levels[2]["support_internal"])
    direct_d4 = levels[4]["support_internal"]
    symmetric_difference = direct_d4 ^ d2_pair["support_internal"]
    d4_size = len(direct_d4)
    b_size = len(points)
    q = curve_record["q"]
    word_bytes = max(1, (curve_record["p"].bit_length() + 7) // 8)
    return {
        "curve_id": curve_record["id"],
        "p": curve_record["p"],
        "q": q,
        "family": family_record["family"],
        "attack_eligible": family_record["attack_eligible"],
        "r_size": b_size,
        "levels": {
            str(arity): record["summary"]
            for arity, record in levels.items()
        },
        "d2_plus_d2": d2_pair["summary"],
        "d4_support_symmetric_difference": len(symmetric_difference),
        "d4_support_symmetric_difference_digest": canonical_digest(
            point_payload(symmetric_difference)
        ),
        "reduced_divisor_degree": d4_size,
        "minimum_dense_pole_degree": d4_size,
        "explicit_coordinate_algebra_dimension": d4_size,
        "dense_final_coefficient_field_elements": d4_size + 1,
        "dense_final_coefficient_bytes": (d4_size + 1) * word_bytes,
        "d4_support_over_b2_5": d4_size / b_size**2.5,
        "d4_support_over_sqrt_q": d4_size / math.sqrt(q),
        "explicit_barrier_signal": (
            not symmetric_difference
            and d4_size > b_size**2.5
            and d4_size > math.sqrt(q)
        ),
        "valid": not symmetric_difference,
        "peak_rss_bytes_after_family": rss_bytes(),
    }


def fit_exponent(points: list[tuple[int, int]]) -> float:
    xs = [math.log(q) for q, _ in points]
    ys = [math.log(value) for _, value in points]
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    return sum(
        (x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)
    ) / sum((x - x_mean) ** 2 for x in xs)


def run(
    result_path: Path,
    families: list[str],
    positive_control: str,
) -> dict[str, Any]:
    source_result = json.loads(result_path.read_text(encoding="utf-8"))
    started = time.perf_counter()
    requested = [*families, positive_control]
    rows = []
    for instance in source_result["instances"]:
        by_family = {
            record["family"]: record for record in instance["families"]
        }
        for family in requested:
            rows.append(
                run_family(instance["curve"], by_family[family])
            )
    curve_ids = sorted({row["curve_id"] for row in rows})
    candidate_rows = [
        row for row in rows if row["family"] in families
    ]
    control_rows = [
        row for row in rows if row["family"] == positive_control
    ]
    control_compression = all(
        control["reduced_divisor_degree"]
        < min(
            row["reduced_divisor_degree"]
            for row in candidate_rows
            if row["curve_id"] == control["curve_id"]
        )
        for control in control_rows
    )
    promoted_families = [
        family
        for family in families
        if len(
            [
                row
                for row in candidate_rows
                if row["family"] == family
                and row["explicit_barrier_signal"]
            ]
        )
        == len(curve_ids)
    ]
    rho_payload_barrier_families = [
        family
        for family in families
        if len(
            [
                row
                for row in candidate_rows
                if row["family"] == family
                and row["valid"]
                and row["d4_support_over_sqrt_q"] > 1
            ]
        )
        == len(curve_ids)
    ]
    scaling = {
        family: {
            "d2_support": fit_exponent(
                [
                    (row["q"], row["levels"]["2"]["unique_point_support"])
                    for row in rows
                    if row["family"] == family
                ]
            ),
            "d3_support": fit_exponent(
                [
                    (row["q"], row["levels"]["3"]["unique_point_support"])
                    for row in rows
                    if row["family"] == family
                ]
            ),
            "d4_support": fit_exponent(
                [
                    (row["q"], row["levels"]["4"]["unique_point_support"])
                    for row in rows
                    if row["family"] == family
                ]
            ),
        }
        for family in requested
    }
    return {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "four-sum-divisor-barrier-v1"
        ),
        "claim_status": [
            "RESTRICTED THEOREM",
            "OBSERVATION",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "four_sum_divisor_barrier_sha256": sha256_file(
                SCRIPT_PATH
            ),
            "typed_five_ec_sha256": sha256_file(TYPED_SOURCE),
            "input_result_sha256": sha256_file(result_path),
        },
        "config": {
            "input_result": str(result_path.resolve()),
            "families": families,
            "positive_control": positive_control,
        },
        "rows": rows,
        "scaling": scaling,
        "summary": {
            "family_rows": len(rows),
            "candidate_rows": len(candidate_rows),
            "control_rows": len(control_rows),
            "all_support_reconstructions_valid": all(
                row["valid"] for row in rows
            ),
            "positive_control_compressed": control_compression,
            "promoted_explicit_barrier_families": promoted_families,
            "explicit_divisor_barrier_gate": (
                len(promoted_families) == len(families)
                and control_compression
            ),
            "rho_payload_barrier_families": (
                rho_payload_barrier_families
            ),
            "rho_payload_barrier_gate": (
                len(rho_payload_barrier_families) == len(families)
                and control_compression
            ),
            "succinct_circuit_barrier_claim": False,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
            "boundary": (
                "Explicit reduced-divisor and dense-function barrier only. "
                "No arithmetic-circuit, resultant, or structured-quotient "
                "lower bound follows."
            ),
        },
        "peak_rss_bytes": rss_bytes(),
        "total_wall_seconds": time.perf_counter() - started,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("result", type=Path)
    parser.add_argument("--families", nargs="+", required=True)
    parser.add_argument("--positive-control", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            run(args.result, args.families, args.positive_control),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
