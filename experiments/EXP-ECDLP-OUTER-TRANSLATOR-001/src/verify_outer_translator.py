#!/usr/bin/env python3
"""Replay and independently audit outer-translator development artifacts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
GENERATOR_PATH = SCRIPT_PATH.with_name("outer_translator.py")
Point = tuple[int, int] | None
REPLAY_VOLATILE_DERIVED_KEYS = {
    "wall_time_ratio",
    "wall_time_improved_diagnostic",
    "practical_signal_gate",
    "batch_practical_signal_count",
    "all_timing_rows_pass",
    "conjunctive_batch_practical_signals",
}


def load_generator() -> Any:
    name = "outer_translator_verifier_generator"
    spec = importlib.util.spec_from_file_location(name, GENERATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load generator: {GENERATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


GENERATOR = load_generator()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json_strict(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_constant,
    )


def compare_exact(actual: Any, expected: Any, path: str = "$") -> None:
    if type(actual) is not type(expected):
        raise AssertionError(
            f"type mismatch at {path}: {type(actual).__name__} != "
            f"{type(expected).__name__}"
        )
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"mapping keys differ at {path}")
        for key in sorted(expected):
            compare_exact(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"list length differs at {path}")
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_exact(actual_item, expected_item, f"{path}[{index}]")
        return
    if isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"float differs at {path}: {actual!r} != {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"value differs at {path}: {actual!r} != {expected!r}")


def is_replay_volatile_key(key: str) -> bool:
    return (
        key == "generated_at_utc"
        or key in REPLAY_VOLATILE_DERIVED_KEYS
        or key.endswith("wall_seconds")
        or key.endswith("wall_time_seconds")
    )


def validate_replay_volatiles(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            item_path = f"{path}.{key}"
            if key == "generated_at_utc":
                if type(item) is not str or not item:
                    raise AssertionError(f"invalid generation timestamp at {item_path}")
            elif key.endswith("wall_seconds") or key.endswith("wall_time_seconds"):
                if type(item) not in (int, float) or not math.isfinite(item) or item < 0:
                    raise AssertionError(f"invalid wall-clock measurement at {item_path}")
            validate_replay_volatiles(item, item_path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            validate_replay_volatiles(item, f"{path}[{index}]")


def strip_replay_volatiles(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: strip_replay_volatiles(item)
            for key, item in value.items()
            if not is_replay_volatile_key(key)
        }
    if isinstance(value, list):
        return [strip_replay_volatiles(item) for item in value]
    return value


def validate_batch_timing_derivations(document: dict[str, Any]) -> None:
    signal_count = 0
    batch_context_rows: list[tuple[str, dict[str, Any]]] = []
    for instance in document["instances"]:
        field_bytes = max(1, math.ceil(instance["curve"]["p"].bit_length() / 8))
        for row in instance["rows"]:
            for batch in row["floor"]["batches"]:
                batch_context_rows.append((row["family"], batch))
                target_major = batch["target_major"]
                d2_major = batch["d2_major"]
                comparison = batch["comparison"]
                target_wall = target_major["wall_time_seconds"]
                d2_wall = d2_major["wall_time_seconds"]
                expected_ratio = None if target_wall == 0 else d2_wall / target_wall
                if comparison["wall_time_ratio"] != expected_ratio:
                    raise AssertionError("batch wall-time ratio is internally inconsistent")
                target_counters = target_major["counters"]
                batch_counters = d2_major["counters"]
                expected_extra = max(
                    0,
                    batch_counters["field_multiplications"]
                    - target_counters["field_multiplications"],
                )
                disclosed_extra = (
                    batch_counters["prefix_multiplications"]
                    + batch_counters["backward_multiplications"]
                )
                if comparison["observed_extra_field_multiplications"] != expected_extra:
                    raise AssertionError("batch multiplication delta is inconsistent")
                if (
                    comparison["disclosed_batch_inversion_multiplications"]
                    != disclosed_extra
                ):
                    raise AssertionError("batch multiplication disclosure is inconsistent")
                multiplication_pass = expected_extra <= disclosed_extra
                if (
                    comparison["multiplication_within_disclosed_tradeoff"]
                    != multiplication_pass
                ):
                    raise AssertionError("batch multiplication gate is inconsistent")
                target_count = d2_major["target_count"]
                index_bytes = max(
                    1,
                    math.ceil(max(1, (target_count - 1).bit_length()) / 8),
                )
                expected_workspace_bound = target_count * (
                    8 * field_bytes + 2 * index_bytes
                )
                observed_workspace = batch_counters[
                    "peak_batch_workspace_logical_bytes"
                ]
                if (
                    comparison["peak_batch_workspace_logical_bytes"]
                    != observed_workspace
                    or comparison["batch_workspace_logical_upper_bound_bytes"]
                    != expected_workspace_bound
                ):
                    raise AssertionError("batch workspace disclosure is inconsistent")
                workspace_pass = 0 <= observed_workspace <= expected_workspace_bound
                if comparison["workspace_within_disclosed_tradeoff"] != workspace_pass:
                    raise AssertionError("batch workspace gate is inconsistent")
                inversion_ratio = comparison["inversion_ratio"]
                read_ratio = comparison["d2_point_read_ratio"]
                cardinality_complete = (
                    batch["requested_count"] == batch["realized_count"]
                )
                if (
                    comparison["cardinality_gate"] != cardinality_complete
                    or comparison["cardinality_status"]
                    != ("EXACT" if cardinality_complete else "INSUFFICIENT_SUPPORT")
                ):
                    raise AssertionError("batch cardinality gate is inconsistent")
                deterministic_operation_signal = (
                    cardinality_complete
                    and comparison["solved_set_equal"]
                    and comparison["witnesses_equal"]
                    and inversion_ratio is not None
                    and inversion_ratio <= 0.8
                    and read_ratio is not None
                    and read_ratio <= 0.8
                    and multiplication_pass
                    and workspace_pass
                )
                if (
                    comparison["deterministic_operation_signal_gate"]
                    != deterministic_operation_signal
                    or comparison["timing_status"] != "UNVERIFIED_DIAGNOSTIC"
                    or comparison["timing_attested"] is not False
                    or comparison["wall_time_improved_diagnostic"]
                    != (expected_ratio is not None and expected_ratio < 1.0)
                    or comparison["practical_signal_gate"] is not False
                ):
                    raise AssertionError("batch timing gate is internally inconsistent")
                signal_count += False
    if document["aggregate"]["batch_practical_signal_count"] != signal_count:
        raise AssertionError("batch timing aggregate is internally inconsistent")
    expected_instance_count = len(document["configuration"]["bit_sizes"]) * len(
        document["configuration"]["seeds"]
    )
    expected_row_count = (
        expected_instance_count * document["configuration"]["batch_replicates"]
    )
    expected_groups: list[dict[str, Any]] = []
    for family in document["configuration"]["floor_families"]:
        for kind in ("supported", "uniform"):
            scales = sorted(
                {
                    batch["batch_scale"]
                    for row_family, batch in batch_context_rows
                    if row_family == family and batch["kind"] == kind
                }
            )
            for scale in scales:
                grouped = [
                    batch
                    for row_family, batch in batch_context_rows
                    if row_family == family
                    and batch["kind"] == kind
                    and batch["batch_scale"] == scale
                ]
                expected_groups.append(
                    {
                        "family": family,
                        "target_kind": kind,
                        "batch_scale": scale,
                        "observed_row_count": len(grouped),
                        "expected_row_count": expected_row_count,
                        "required_scale_for_practical_signal": scale in {"B", "16B"},
                        "all_operation_rows_pass": (
                            len(grouped) == expected_row_count
                            and all(
                                batch["comparison"][
                                    "deterministic_operation_signal_gate"
                                ]
                                for batch in grouped
                            )
                        ),
                        "all_timing_rows_pass": (
                            len(grouped) == expected_row_count
                            and all(
                                batch["comparison"]["practical_signal_gate"]
                                for batch in grouped
                            )
                        ),
                    }
                )
    if document["aggregate"]["batch_practical_signal_groups"] != expected_groups:
        raise AssertionError("batch timing groups are internally inconsistent")
    expected_operation_signals = [
        {
            "family": row["family"],
            "target_kind": row["target_kind"],
            "batch_scale": row["batch_scale"],
        }
        for row in expected_groups
        if row["required_scale_for_practical_signal"]
        and row["all_operation_rows_pass"]
    ]
    if (
        document["aggregate"]["conjunctive_batch_operation_signals"]
        != expected_operation_signals
    ):
        raise AssertionError("batch operation signal list is internally inconsistent")
    expected_signals = [
        {
            "family": row["family"],
            "target_kind": row["target_kind"],
            "batch_scale": row["batch_scale"],
        }
        for row in expected_groups
        if row["required_scale_for_practical_signal"]
        and row["all_timing_rows_pass"]
    ]
    if (
        document["aggregate"]["conjunctive_batch_practical_signals"]
        != expected_signals
    ):
        raise AssertionError("batch timing signal list is internally inconsistent")


def point_from_json(value: list[int] | None) -> Point:
    if value is None:
        return None
    if type(value) is not list or len(value) != 2:
        raise AssertionError("point must be null or an exact coordinate pair")
    if any(type(coordinate) is not int for coordinate in value):
        raise AssertionError("point coordinate is not an exact integer")
    return value[0], value[1]


class IndependentCurve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p
        if (4 * pow(self.a, 3, p) + 27 * pow(self.b, 2, p)) % p == 0:
            raise AssertionError("independent verifier received a singular curve")

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return 0 <= x < self.p and 0 <= y < self.p and (
            y * y - x * x * x - self.a * x - self.b
        ) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

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
            if y1 == 0:
                return None
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        result = x3, y3
        if not self.on_curve(result):
            raise AssertionError("independent affine addition left the curve")
        return result

    def mul(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point))
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend)
            scalar >>= 1
            if scalar:
                addend = self.add(addend, addend)
        return result

    def order(self) -> int:
        total = 1
        exponent = (self.p - 1) // 2
        for x in range(self.p):
            rhs = (x * x * x + self.a * x + self.b) % self.p
            if rhs == 0:
                total += 1
            else:
                symbol = pow(rhs, exponent, self.p)
                if symbol == 1:
                    total += 2
                elif symbol != self.p - 1:
                    raise AssertionError("Euler criterion returned an invalid value")
        return total


def independent_sum(curve: IndependentCurve, points: list[Point]) -> Point:
    total: Point = None
    for point in points:
        total = curve.add(total, point)
    return total


def independent_is_prime(value: int) -> bool:
    if type(value) is not int or value < 2:
        return False
    if value in (2, 3):
        return True
    if value % 2 == 0:
        return False
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def independent_embedding_degree(p: int, q: int) -> int:
    residue = p % q
    value = 1
    for degree in range(1, q):
        value = value * residue % q
        if value == 1:
            return degree
    raise AssertionError("independent embedding-degree search failed")


def evaluate_dense(coefficients: list[int], value: int, p: int) -> int:
    accumulator = 0
    for coefficient in reversed(coefficients):
        if type(coefficient) is not int:
            raise AssertionError("polynomial coefficient is not an exact integer")
        accumulator = (accumulator * value + coefficient) % p
    return accumulator


def independent_s3_compatibility(
    curve: IndependentCurve,
    target: Point,
    d2_points: list[Point],
) -> tuple[list[int], bool]:
    support = set(d2_points)
    roots: set[int] = set()
    identity_route = False
    for left in d2_points:
        complement = curve.add(target, curve.neg(left))
        if complement not in support:
            continue
        if left is None:
            identity_route = True
        else:
            roots.add(left[0])
    return sorted(roots), identity_route


def independent_s4_compatibility(
    curve: IndependentCurve,
    target: Point,
    factor_points: list[Point],
    d2_points: list[Point],
) -> tuple[list[int], bool]:
    support = set(d2_points)
    roots: set[int] = set()
    identity_route = False
    for left in d2_points:
        partial = curve.add(target, curve.neg(left))
        for factor in factor_points:
            complement = curve.add(partial, curve.neg(factor))
            if complement not in support:
                continue
            if left is None:
                identity_route = True
            else:
                roots.add(left[0])
    return sorted(roots), identity_route


def independent_f3_coefficients_in_z(
    p: int,
    a: int,
    b: int,
    x1: int,
    x2: int,
) -> tuple[int, int, int]:
    product = x1 * x2
    return (
        (x1 - x2) ** 2 % p,
        (-2 * ((x1 + x2) * (product + a) + 2 * b)) % p,
        ((product - a) ** 2 - 4 * b * (x1 + x2)) % p,
    )


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def independent_quadratic_resultant(
    p: int,
    left: tuple[int, int, int],
    right: tuple[int, int, int],
) -> int:
    a2, a1, a0 = left
    b2, b1, b0 = right
    sylvester = (
        (a2, a1, a0, 0),
        (0, a2, a1, a0),
        (b2, b1, b0, 0),
        (0, b2, b1, b0),
    )
    determinant = 0
    for permutation in itertools.permutations(range(4)):
        term = permutation_sign(permutation)
        for row, column in enumerate(permutation):
            term *= sylvester[row][column]
        determinant += term
    return determinant % p


def independent_direct_scalar_f4_scan(
    curve: IndependentCurve,
    target_x: int,
    factor_x_roots: list[int],
    d2_x_roots: list[int],
    stop_after_first: bool,
) -> tuple[list[int], int, int, int]:
    roots: set[int] = set()
    left_cache_keys: set[tuple[int, int]] = set()
    right_cache_keys: set[int] = set()
    tuple_tests = 0
    for factor_x in factor_x_roots:
        for left_x in d2_x_roots:
            for right_x in d2_x_roots:
                tuple_tests += 1
                left_cache_keys.add((factor_x, left_x))
                right_cache_keys.add(right_x)
                left = independent_f3_coefficients_in_z(
                    curve.p, curve.a, curve.b, factor_x, left_x
                )
                right = independent_f3_coefficients_in_z(
                    curve.p, curve.a, curve.b, right_x, target_x
                )
                if independent_quadratic_resultant(curve.p, left, right) == 0:
                    roots.add(left_x)
                    if stop_after_first:
                        return (
                            sorted(roots),
                            tuple_tests,
                            len(left_cache_keys),
                            len(right_cache_keys),
                        )
    return (
        sorted(roots),
        tuple_tests,
        len(left_cache_keys),
        len(right_cache_keys),
    )


def expected_direct_scalar_operations(
    tuple_tests: int,
    left_cache_entries: int,
    right_cache_entries: int,
) -> dict[str, int | str]:
    cache_entries = left_cache_entries + right_cache_entries
    return {
        "schema": "fp-polynomial-operations-v1",
        "coefficient_additions": 6 * cache_entries + 4 * tuple_tests,
        "coefficient_multiplications": 8 * cache_entries + 8 * tuple_tests,
        "coefficient_inversions": 0,
        "coefficient_zero_tests": tuple_tests,
    }


def verify_index_witness(
    curve: IndependentCurve,
    factor_points: list[Point],
    target: Point,
    witness: Any,
    label: str,
    leaf_count: int = 5,
) -> None:
    if type(witness) is not list or len(witness) != leaf_count:
        raise AssertionError(f"{label} is not a {leaf_count}-index witness")
    if any(
        type(index) is not int or not 0 <= index < len(factor_points)
        for index in witness
    ):
        raise AssertionError(f"{label} contains an invalid factor index")
    if independent_sum(curve, [factor_points[index] for index in witness]) != target:
        raise AssertionError(f"{label} does not sum to its target")


def map_source_value_independent(
    map_kind: str,
    root: int,
    params: dict[str, int],
    p: int,
) -> tuple[int, int]:
    if map_kind == "identity":
        return root % p, 1
    if map_kind == "square":
        return (root * root + params["c"]) % p, 1
    if map_kind == "mobius":
        denominator = (root + params["e"]) % p
        if denominator == 0:
            raise AssertionError("accepted source root has zero Mobius denominator")
        return (root + params["d"]) * pow(denominator, -1, p) % p, denominator
    raise AssertionError("unsupported source map in artifact")


def weighted_field_work_independent(record: dict[str, int]) -> dict[str, int]:
    multiplications = record.get("field_multiplications", 0)
    inversions = record.get("field_inversions", 0)
    return {
        str(weight): multiplications + weight * inversions
        for weight in GENERATOR.INVERSION_WEIGHTS
    }


def sum_integer_records(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {
        key: sum(record.get(key, 0) for record in records)
        for key in sorted(keys)
    }


def fit_log_slope_independent(rows: list[tuple[int, float]]) -> float | None:
    if len(rows) < 3 or any(value <= 0 for _, value in rows):
        return None
    x_values = [math.log(order) for order, _ in rows]
    y_values = [math.log(value) for _, value in rows]
    x_mean = sum(x_values) / len(x_values)
    y_mean = sum(y_values) / len(y_values)
    denominator = sum((value - x_mean) ** 2 for value in x_values)
    if denominator == 0:
        return None
    numerator = sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x_values, y_values)
    )
    return numerator / denominator


def verify_continuation_aggregate(document: dict[str, Any]) -> None:
    config = document["configuration"]
    translator_contexts = [
        (instance, row)
        for instance in document["instances"]
        for row in instance["rows"]
        if row["translator"] is not None
    ]
    expected_instance_count = len(config["bit_sizes"]) * len(config["seeds"])
    expected_slopes: dict[str, dict[str, float | None]] = {}
    expected_trends: list[dict[str, Any]] = []
    for family in config["translator_families"]:
        contexts = [
            (instance, row)
            for instance, row in translator_contexts
            if row["family"] == family
        ]

        def metric_rows(metric: Any) -> list[tuple[int, float]]:
            return [
                (instance["curve"]["q"], metric(row))
                for instance, row in contexts
            ]

        slopes = {
            f"candidate_weighted_{weight}": fit_log_slope_independent(
                metric_rows(
                    lambda row, weight=weight: statistics.fmean(
                        target["candidate_weighted_field_work"][str(weight)]
                        for target in (
                            row["translator"]["targets"]
                            + row["translator"]["matched_uniform_targets"]
                        )
                    )
                )
            )
            for weight in GENERATOR.INVERSION_WEIGHTS
        }
        slopes.update(
            {
                "combined_g_max_variable_degree": fit_log_slope_independent(
                    metric_rows(
                        lambda row: statistics.fmean(
                            max(target["combined_g"]["degrees"])
                            for target in (
                                row["translator"]["targets"]
                                + row["translator"]["matched_uniform_targets"]
                            )
                        )
                    )
                ),
                "combined_g_term_count": fit_log_slope_independent(
                    metric_rows(
                        lambda row: statistics.fmean(
                            target["combined_g"]["term_count"]
                            for target in (
                                row["translator"]["targets"]
                                + row["translator"]["matched_uniform_targets"]
                            )
                        )
                    )
                ),
                "combined_g_density": fit_log_slope_independent(
                    metric_rows(
                        lambda row: statistics.fmean(
                            target["combined_g"]["density"]
                            for target in (
                                row["translator"]["targets"]
                                + row["translator"]["matched_uniform_targets"]
                            )
                        )
                    )
                ),
                "explicit_h_coefficients": fit_log_slope_independent(
                    metric_rows(
                        lambda row: statistics.fmean(
                            target["h_coefficient_writes"]
                            for target in (
                                row["translator"]["targets"]
                                + row["translator"]["matched_uniform_targets"]
                            )
                        )
                    )
                ),
                "symmetry_d3_advice_bits": fit_log_slope_independent(
                    metric_rows(
                        lambda row: row["d3"]["symmetry_codec"][
                            "logical_advice_bits"
                        ]
                    )
                ),
            }
        )
        expected_slopes[family] = slopes
        materialization_slope = slopes["symmetry_d3_advice_bits"]
        bounded_names = [
            *(
                f"candidate_weighted_{weight}"
                for weight in GENERATOR.INVERSION_WEIGHTS
            ),
            "combined_g_max_variable_degree",
            "combined_g_term_count",
            "explicit_h_coefficients",
        ]
        bounded = {
            name: {
                "slope": slopes[name],
                "materialization_slope": materialization_slope,
                "pass": (
                    slopes[name] is not None
                    and materialization_slope is not None
                    and slopes[name] <= materialization_slope
                ),
            }
            for name in bounded_names
        }
        coverage = (
            len(contexts) == expected_instance_count
            and sorted({instance["bits"] for instance, _ in contexts})
            == sorted(config["bit_sizes"])
            and all(
                {
                    instance["seed"]
                    for instance, _ in contexts
                    if instance["bits"] == bits
                }
                == set(config["seeds"])
                for bits in config["bit_sizes"]
            )
        )
        all_defined = all(value is not None for value in slopes.values())
        density_slope = slopes["combined_g_density"]
        density_gate = density_slope is not None and density_slope <= 0
        trend_gate = (
            coverage
            and all_defined
            and density_gate
            and all(result["pass"] for result in bounded.values())
        )
        expected_trends.append(
            {
                "family": family,
                "observed_instance_count": len(contexts),
                "expected_instance_count": expected_instance_count,
                "observed_bit_sizes": sorted(
                    {instance["bits"] for instance, _ in contexts}
                ),
                "expected_bit_sizes": sorted(config["bit_sizes"]),
                "coverage_gate": coverage,
                "all_slopes_defined": all_defined,
                "bounded_by_d3_materialization": bounded,
                "density_slope": density_slope,
                "density_nonincreasing_gate": density_gate,
                "trend_gate": trend_gate,
                "status": "PASS" if trend_gate else "FAIL_CLOSED",
            }
        )
    aggregate = document["aggregate"]
    if (
        aggregate["exploratory_slopes"] != expected_slopes
        or aggregate["trend_gates"] != expected_trends
    ):
        raise AssertionError("aggregate trend derivation is inconsistent")
    trend_by_family = {row["family"]: row for row in expected_trends}
    for _, row in translator_contexts:
        translator = row["translator"]
        trend_gate = trend_by_family[row["family"]]["trend_gate"]
        if (
            translator["family_trend_gate"] != trend_gate
            or translator["coordinate_continuation_gate"]
            != (translator["coordinate_instance_gate"] and trend_gate)
        ):
            raise AssertionError("final continuation gate omits the trend gate")
    expected_family_rows: list[dict[str, Any]] = []
    for family in config["translator_families"]:
        family_translators = [
            row["translator"]
            for _, row in translator_contexts
            if row["family"] == family
        ]
        expected_family_rows.append(
            {
                "family": family,
                "observed_instance_count": len(family_translators),
                "expected_instance_count": expected_instance_count,
                "trend_gate": trend_by_family[family]["trend_gate"],
                "all_instances_pass": (
                    family != "random_x"
                    and len(family_translators) == expected_instance_count
                    and all(
                        translator["coordinate_continuation_gate"]
                        for translator in family_translators
                    )
                ),
            }
        )
    expected_rows = [
        {"curve_id": instance["curve"]["id"], "family": row["family"]}
        for instance, row in translator_contexts
        if row["translator"]["coordinate_continuation_gate"]
    ]
    expected_conjunctive = [
        row["family"] for row in expected_family_rows if row["all_instances_pass"]
    ]
    if (
        aggregate["translator_row_count"] != len(translator_contexts)
        or aggregate["verified_functional_translator_rows"]
        != sum(row["translator"]["functional_gate"] for _, row in translator_contexts)
        or aggregate["coordinate_continuation_rows"] != expected_rows
        or aggregate["coordinate_continuation_families"] != expected_family_rows
        or aggregate["conjunctive_continuation_families"]
        != expected_conjunctive
    ):
        raise AssertionError("aggregate continuation decision is inconsistent")


def verify_row(
    curve: IndependentCurve,
    q: int,
    row: dict[str, Any],
    requested_coordinate_targets: int,
) -> dict[str, int]:
    factor_base = row["factor_base"]
    factor_points = [point_from_json(value) for value in factor_base["points"]]
    if any(not curve.on_curve(point) or point is None for point in factor_points):
        raise AssertionError("factor base contains an invalid or infinite point")
    if len(factor_points) % 2:
        raise AssertionError("factor base is not sign complete")
    for index in range(0, len(factor_points), 2):
        if curve.neg(factor_points[index]) != factor_points[index + 1]:
            raise AssertionError("factor-base sign pair mismatch")

    d2_record = row["d2"]
    d2_points = [point_from_json(value) for value in d2_record["points"]]
    d2_witnesses = d2_record["witnesses"]
    brute_d2: set[Point] = set()
    for left in range(len(factor_points)):
        for right in range(left, len(factor_points)):
            brute_d2.add(curve.add(factor_points[left], factor_points[right]))
    if set(d2_points) != brute_d2 or len(d2_points) != len(brute_d2):
        raise AssertionError("independent D2 support mismatch")
    for point, witness in zip(d2_points, d2_witnesses):
        if len(witness) != 2 or independent_sum(
            curve, [factor_points[index] for index in witness]
        ) != point:
            raise AssertionError("independent D2 witness mismatch")

    d3_record = row["d3"]
    d3_points = [point_from_json(value) for value in d3_record["points"]]
    d3_witnesses = d3_record["witnesses"]
    brute_d3 = {
        curve.add(d2_point, factor_point)
        for d2_point in d2_points
        for factor_point in factor_points
    }
    if set(d3_points) != brute_d3 or len(d3_points) != len(brute_d3):
        raise AssertionError("independent D3 support mismatch")
    for point, witness in zip(d3_points, d3_witnesses):
        if len(witness) != 3 or independent_sum(
            curve, [factor_points[index] for index in witness]
        ) != point:
            raise AssertionError("independent D3 witness mismatch")

    verified_witnesses = 0
    d2_index = {point: index for index, point in enumerate(d2_points)}
    d3_index = {point: index for index, point in enumerate(d3_points)}
    symmetry = d3_record["symmetry_codec"]
    d3_x_values = {point[0] for point in d3_points if point is not None}
    index_bits = max(1, (len(factor_points) - 1).bit_length())
    expected_symmetry_bits = len(d3_x_values) * (
        curve.p.bit_length() + 3 * index_bits
    )
    if None in d3_index:
        expected_symmetry_bits += 1 + 3 * index_bits
    if (
        symmetry["x_orbit_count"] != len(d3_x_values)
        or symmetry["identity_present"] != (None in d3_index)
        or symmetry["logical_advice_bits"] != expected_symmetry_bits
    ):
        raise AssertionError("symmetry-compressed D3 accounting mismatch")
    for entry in symmetry["first_entries"]:
        x_value = entry["x"]
        matching = [point for point in d3_points if point is not None and point[0] == x_value]
        if len(matching) != 2:
            raise AssertionError("symmetry codec entry is not a full x orbit")
        canonical = min(matching, key=lambda point: point[1])
        witness = entry["canonical_witness"]
        if type(witness) is not list or len(witness) != 3:
            raise AssertionError("symmetry codec has an invalid witness shape")
        if independent_sum(
            curve, [factor_points[index] for index in witness]
        ) != canonical:
            raise AssertionError("symmetry codec witness does not match its orientation")

    for batch in row["floor"]["batches"]:
        targets = [point_from_json(value) for value in batch["targets"]]
        expected_order = (
            ["target_major", "d2_major"]
            if batch["replicate"] % 2 == 0
            else ["d2_major", "target_major"]
        )
        if batch["kernel_execution_order"] != expected_order:
            raise AssertionError("batch kernel execution order is inconsistent")
        if len(targets) != batch["realized_count"]:
            raise AssertionError("batch target count mismatch")
        independently_solved: list[int] = []
        for target_index, target in enumerate(targets):
            if any(
                curve.add(target, curve.neg(partial)) in d3_index
                for partial in d2_points
            ):
                independently_solved.append(target_index)
        for mode in ("target_major", "d2_major"):
            result = batch[mode]
            audit_result = batch["correctness_audit"][mode]
            stable_result = [
                {
                    key: query.get(key)
                    for key in (
                        "success",
                        "witness",
                        "d2_index",
                        "d3_index",
                        "complement",
                    )
                }
                for query in result["per_target"]
            ]
            stable_audit = [
                {
                    key: query.get(key)
                    for key in (
                        "success",
                        "witness",
                        "d2_index",
                        "d3_index",
                        "complement",
                    )
                }
                for query in audit_result["per_target"]
            ]
            if (
                stable_result != stable_audit
                or result["witness_verification_audit"]["performed"] is not False
                or audit_result["witness_verification_audit"]["performed"] is not True
            ):
                raise AssertionError(f"{mode} kernel/audit segregation failed")
            if result["solved_indices"] != independently_solved:
                raise AssertionError(f"{mode} solved set is not independently exact")
            if len(result["per_target"]) != len(targets):
                raise AssertionError(f"{mode} result count mismatch")
            for target, query in zip(targets, result["per_target"]):
                if not query["success"]:
                    if query["witness"] is not None:
                        raise AssertionError(f"{mode} miss carries a witness")
                    continue
                verify_index_witness(
                    curve,
                    factor_points,
                    target,
                    query["witness"],
                    f"{mode} witness",
                )
                verified_witnesses += 1
                left_index = query["d2_index"]
                right_index = query["d3_index"]
                if (
                    type(left_index) is not int
                    or type(right_index) is not int
                    or not 0 <= left_index < len(d2_points)
                    or not 0 <= right_index < len(d3_points)
                ):
                    raise AssertionError(f"{mode} route index is invalid")
                complement = curve.add(target, curve.neg(d2_points[left_index]))
                if complement != d3_points[right_index]:
                    raise AssertionError(f"{mode} route complement is invalid")

    partial = row["floor"]["partial_d3"]
    partial_targets = [point_from_json(value) for value in partial["targets"]]
    for cache in partial["caches"]:
        if len(cache["queries"]) != len(partial_targets):
            raise AssertionError("partial-D3 query count mismatch")
        for target, query in zip(partial_targets, cache["queries"]):
            expected_success = any(
                curve.add(target, curve.neg(point)) in d3_index for point in d2_points
            )
            if query["success"] != expected_success:
                raise AssertionError("partial-D3 fallback is not complete")
            if query["success"]:
                verify_index_witness(
                    curve,
                    factor_points,
                    target,
                    query["witness"],
                    "partial-D3 witness",
                )
                verified_witnesses += 1

    for query in row["floor"]["materialized_d4"]["queries"]:
        target = point_from_json(query["target"])
        if query["success"]:
            verify_index_witness(
                curve,
                factor_points,
                target,
                query["witness"],
                "materialized-D4 witness",
            )
            verified_witnesses += 1

    translator = row.get("translator")
    if translator:
        preprocessing = translator["preprocessing"]
        expected_d2_roots = sorted(
            {point[0] for point in d2_points if point is not None}
        )
        if preprocessing["d2_x_roots"] != expected_d2_roots:
            raise AssertionError("translator D2 x roots differ from independent D2")
        m2 = preprocessing["m2"]
        if len(m2) != len(expected_d2_roots) + 1 or m2[-1] % curve.p != 1:
            raise AssertionError("translator M2 is not monic of the expected degree")
        if any(evaluate_dense(m2, root, curve.p) != 0 for root in expected_d2_roots):
            raise AssertionError("translator M2 does not vanish on every D2 x root")

        covered_x: list[int] = []
        expected_incremental_coefficients = len(expected_d2_roots) + len(m2)
        expected_source_polynomial_coefficients = 0
        expected_source_root_count = 0
        for branch in preprocessing["branches"]:
            roots = branch["source_roots"]
            x_values = branch["x_values"]
            params = branch["params"]
            source_polynomial = branch["source_polynomial"]
            if len(roots) != len(x_values) or len(roots) != len(set(roots)):
                raise AssertionError("translator source roots are not distinct and aligned")
            if (
                len(source_polynomial) != len(roots) + 1
                or source_polynomial[-1] % curve.p != 1
            ):
                raise AssertionError("accepted-source polynomial has the wrong degree")
            if any(
                evaluate_dense(source_polynomial, root, curve.p) != 0
                for root in roots
            ):
                raise AssertionError("accepted-source polynomial misses a source root")
            mapped: list[int] = []
            for root in roots:
                x_value, _ = map_source_value_independent(
                    branch["map_kind"], root, params, curve.p
                )
                mapped.append(x_value)
            if mapped != x_values:
                raise AssertionError("source map does not reproduce its factor x values")
            covered_x.extend(mapped)
            expected_incremental_coefficients += len(roots) + len(params)
            expected_source_polynomial_coefficients += len(source_polynomial)
            expected_source_root_count += len(roots)
        expected_factor_x = sorted({point[0] for point in factor_points})
        if sorted(covered_x) != expected_factor_x or len(covered_x) != len(set(covered_x)):
            raise AssertionError("source branches do not exactly cover factor x orbits")
        if (
            preprocessing["incremental_coefficient_count"]
            != expected_incremental_coefficients
            or preprocessing["incremental_logical_bits"]
            != expected_incremental_coefficients * curve.p.bit_length()
            or preprocessing["executable_source_root_count"]
            != expected_source_root_count
            or preprocessing["diagnostic_source_polynomial_coefficient_count"]
            != expected_source_polynomial_coefficients
            or preprocessing["diagnostic_source_polynomial_logical_bits"]
            != expected_source_polynomial_coefficients * curve.p.bit_length()
        ):
            raise AssertionError("translator preprocessing advice accounting mismatch")
        extraction = preprocessing["source_extraction_traffic"]
        if (
            extraction["factor_fiber_reads"] != len(factor_base["fibers"])
            or extraction["source_scalar_reads"]
            != expected_source_root_count
            + sum(len(branch["params"]) for branch in preprocessing["branches"])
            or extraction["source_root_writes"] != expected_source_root_count
            or extraction["d2_root_reads"] != len(expected_d2_roots)
        ):
            raise AssertionError("source-extraction traffic accounting mismatch")
        expected_total_bits = (
            d2_record["logical_advice_bits"]
            + preprocessing["incremental_logical_bits"]
        )
        expected_symmetry_total = (
            d2_record["logical_advice_bits"] + symmetry["logical_advice_bits"]
        )
        if (
            preprocessing["total_logical_bits_including_d2"]
            != expected_total_bits
            or preprocessing["symmetry_d3_total_logical_bits"]
            != expected_symmetry_total
            or preprocessing["advice_ratio_to_symmetry_d3"]
            != expected_total_bits / expected_symmetry_total
        ):
            raise AssertionError("translator advice ratio is inconsistent")
        identity_control = translator["s3_identity_target_control"]
        expected_identity_roots = sorted(
            {point[0] for point in d2_points if point is not None}
        )
        if (
            identity_control["target"] is not None
            or identity_control["polynomial_input_defined"] is not False
            or identity_control["polynomial_roots_by_identity_branch"]
            != expected_identity_roots
            or identity_control["independent_expected_roots"]
            != expected_identity_roots
            or not identity_control["functional_gate"]
        ):
            raise AssertionError("identity-target S3 branch is incomplete")
        if len(identity_control["recovered_finite_roots"]) != len(
            expected_identity_roots
        ):
            raise AssertionError("identity-target S3 recovery count mismatch")
        for recovery in identity_control["recovered_finite_roots"]:
            verify_index_witness(
                curve,
                factor_points,
                None,
                recovery["witness"],
                "identity-target finite S3 witness",
                leaf_count=4,
            )
            verified_witnesses += 1
        identity_sentinel = identity_control["identity_sentinel"]
        if identity_sentinel is None:
            raise AssertionError("identity-target S3 sentinel is missing")
        verify_index_witness(
            curve,
            factor_points,
            None,
            identity_sentinel["witness"],
            "identity-target S3 sentinel witness",
            leaf_count=4,
        )
        verified_witnesses += 1

    translator_target_rows = (
        translator.get("targets", [])
        + translator.get("matched_uniform_targets", [])
        if translator
        else []
    )
    for target_row in translator_target_rows:
        target = point_from_json(target_row["target"])
        if not curve.on_curve(target) or target is None:
            raise AssertionError("translator target is invalid")
        independent_s3_roots, independent_s3_identity = independent_s3_compatibility(
            curve, target, d2_points
        )
        if (
            target_row["polynomial_s3_roots"] != independent_s3_roots
            or target_row["brute_s3"]["roots"] != independent_s3_roots
            or bool(target_row["brute_s3"]["identity_pair"])
            != independent_s3_identity
        ):
            raise AssertionError("S3 roots or identity route differ independently")
        independent_s4_roots, independent_s4_identity = independent_s4_compatibility(
            curve, target, factor_points, d2_points
        )
        if (
            target_row["polynomial_s4_roots"] != independent_s4_roots
            or target_row["brute_s4"]["roots"] != independent_s4_roots
            or bool(target_row["brute_s4"]["identity_route"])
            != independent_s4_identity
        ):
            raise AssertionError("S4 roots or identity route differ independently")
        factor_x_roots = sorted({point[0] for point in factor_points})
        for suffix, stop_after_first in (
            ("first_root", True),
            ("full_root_set", False),
        ):
            (
                expected_roots,
                expected_tuple_tests,
                expected_left_cache_entries,
                expected_right_cache_entries,
            ) = (
                independent_direct_scalar_f4_scan(
                    curve,
                    target[0],
                    factor_x_roots,
                    expected_d2_roots,
                    stop_after_first,
                )
            )
            direct = target_row[f"direct_scalar_f4_{suffix}"]
            if (
                direct["mode"]
                != "cached_direct_scalar_quadratic_resultant_per_tuple"
                or direct["roots"] != expected_roots
                or direct["tuple_tests"] != expected_tuple_tests
                or direct["left_cache_entries"]
                != expected_left_cache_entries
                or direct["right_cache_entries"]
                != expected_right_cache_entries
                or direct["cache_hits"]
                != 2 * expected_tuple_tests
                - expected_left_cache_entries
                - expected_right_cache_entries
                or direct["operations"]
                != expected_direct_scalar_operations(
                    expected_tuple_tests,
                    expected_left_cache_entries,
                    expected_right_cache_entries,
                )
            ):
                raise AssertionError(
                    "direct scalar f4 comparator differs from independent "
                    "Sylvester-determinant scan"
                )
            symbolic = target_row[f"symbolic_sparse_f4_{suffix}"]
            if (
                symbolic["mode"] != "sparse_symbolic_f4_evaluation"
                or symbolic["roots"] != expected_roots
                or symbolic["tuple_tests"] != expected_tuple_tests
                or symbolic["coefficient_writes"] != expected_tuple_tests
            ):
                raise AssertionError(
                    "symbolic f4 comparator differs from independent scalar scan"
                )
        if target_row["direct_scalar_f4_full_root_set"]["roots"] != (
            independent_s4_roots
        ):
            raise AssertionError("direct scalar f4 full roots miss an S4 route")
        all_root_identity = target_row["all_root_recovery_audit"]["identity"]
        if bool(all_root_identity) != independent_s4_identity:
            raise AssertionError("all-root recovery omitted or invented an identity route")
        workspace_coefficient_bound = target_row["f4"]["dense_coefficient_count"]
        previous_combined_dense = 1
        for branch in target_row["branches"]:
            preprocessing_branch = preprocessing["branches"][branch["branch_index"]]
            denominator_scalar = 1
            for root in preprocessing_branch["source_roots"]:
                _, denominator = map_source_value_independent(
                    branch["map_kind"], root, branch["params"], curve.p
                )
                denominator_scalar = (
                    denominator_scalar * pow(denominator, 4, curve.p)
                ) % curve.p
            if branch["denominator_scalar"] != denominator_scalar:
                raise AssertionError("source denominator scalar is inconsistent")
            source_template_dense = branch["source_template"][
                "dense_coefficient_count"
            ]
            source_product_dense = branch["source_product"][
                "dense_coefficient_count"
            ]
            combined_dense = branch["combined_after"]["dense_coefficient_count"]
            workspace_coefficient_bound = max(
                workspace_coefficient_bound,
                target_row["f4"]["dense_coefficient_count"]
                + previous_combined_dense
                + source_template_dense
                + 3 * source_product_dense
                + combined_dense,
            )
            previous_combined_dense = combined_dense
        reduced_degree_bound = max(1, len(m2) - 1)
        combined_v_degree = max(0, target_row["combined_g"]["degrees"][0])
        workspace_coefficient_bound = max(
            workspace_coefficient_bound,
            target_row["f4"]["dense_coefficient_count"]
            + target_row["combined_g"]["dense_coefficient_count"]
            + len(m2)
            + 3 * reduced_degree_bound
            + 2 * (combined_v_degree + 1),
        )
        coefficient_bytes = max(1, math.ceil(curve.p.bit_length() / 8))
        expected_workspace_bytes = (
            workspace_coefficient_bound * coefficient_bytes
            + len(independent_s4_roots) * coefficient_bytes
        )
        if (
            target_row["peak_target_workspace_coefficient_upper_bound"]
            != workspace_coefficient_bound
            or target_row["peak_target_workspace_logical_bytes"]
            != expected_workspace_bytes
        ):
            raise AssertionError("translator workspace upper bound is inconsistent")
        polynomial_ops = target_row["candidate_polynomial_operations"]
        expected_coefficient_reads = (
            2
            * (
                polynomial_ops["coefficient_additions"]
                + polynomial_ops["coefficient_multiplications"]
            )
            + polynomial_ops["coefficient_zero_tests"]
            + polynomial_ops["coefficient_inversions"]
        )
        expected_coefficient_writes = (
            polynomial_ops["coefficient_additions"]
            + polynomial_ops["coefficient_multiplications"]
            + polynomial_ops["coefficient_inversions"]
        )
        expected_root_reads = (
            len(expected_factor_x)
            + 2 * len(expected_d2_roots)
            + len(independent_s4_roots)
        )
        recovery_bytes = target_row["solver_recovery"]["logical_bytes_read"]
        expected_memory_bytes = (
            expected_coefficient_reads
            + expected_coefficient_writes
            + expected_root_reads
        ) * coefficient_bytes + recovery_bytes
        memory_record = target_row["candidate_memory_traffic_lower_bound"]
        if (
            memory_record["coefficient_reads"] != expected_coefficient_reads
            or memory_record["coefficient_writes"] != expected_coefficient_writes
            or memory_record["explicit_source_and_d2_root_scalar_reads"]
            != expected_root_reads
            or memory_record["witness_recovery_logical_bytes"] != recovery_bytes
            or memory_record["logical_bytes"] != expected_memory_bytes
        ):
            raise AssertionError("translator memory-traffic lower bound is inconsistent")
        expected_success = bool(independent_s4_roots) or independent_s4_identity
        for query_name in ("exact_d2_d3_query", "symmetry_d3_query"):
            query = target_row[query_name]
            if query["success"] != expected_success:
                raise AssertionError(f"{query_name} success differs independently")
            if query["success"]:
                verify_index_witness(
                    curve,
                    factor_points,
                    target,
                    query["witness"],
                    f"{query_name} witness",
                )
                verified_witnesses += 1
        polynomial_vector = {
            "field_additions": polynomial_ops["coefficient_additions"],
            "field_multiplications": polynomial_ops["coefficient_multiplications"],
            "field_inversions": polynomial_ops["coefficient_inversions"],
            "field_zero_tests": polynomial_ops["coefficient_zero_tests"],
        }
        candidate_total = sum_integer_records(
            polynomial_vector,
            target_row["solver_recovery"]["ops"],
        )
        candidate_weighted = weighted_field_work_independent(candidate_total)
        if (
            target_row["candidate_total_field_vector"] != candidate_total
            or target_row["candidate_weighted_field_work"] != candidate_weighted
        ):
            raise AssertionError("candidate total field vector is inconsistent")
        exact_query = target_row["exact_d2_d3_query"]
        exact_weighted = weighted_field_work_independent(
            exact_query["operation_record"]
        )
        if exact_query["weighted_field_work"] != exact_weighted:
            raise AssertionError("exact comparator weighted work is inconsistent")
        online_ratios = {
            str(weight): (
                None
                if exact_weighted[str(weight)] == 0
                else candidate_weighted[str(weight)] / exact_weighted[str(weight)]
            )
            for weight in GENERATOR.INVERSION_WEIGHTS
        }
        preprocessing_ops = preprocessing["operations"]
        translator_preprocessing = weighted_field_work_independent(
            {
                "field_multiplications": preprocessing_ops[
                    "coefficient_multiplications"
                ],
                "field_inversions": preprocessing_ops["coefficient_inversions"],
            }
        )
        comparator_preprocessing = weighted_field_work_independent(
            d3_record["build_ops"]
        )
        preprocessing_differential = {
            str(weight): max(
                0,
                translator_preprocessing[str(weight)]
                - comparator_preprocessing[str(weight)],
            )
            for weight in GENERATOR.INVERSION_WEIGHTS
        }
        crossovers: dict[str, int | None] = {}
        for weight in GENERATOR.INVERSION_WEIGHTS:
            key = str(weight)
            if candidate_weighted[key] >= exact_weighted[key]:
                crossovers[key] = None
            else:
                crossovers[key] = math.ceil(
                    preprocessing_differential[key]
                    / (exact_weighted[key] - candidate_weighted[key])
                )
        logical_baseline = max(1, math.ceil(symmetry["logical_advice_bits"] / 8))
        python_baseline = max(1, symmetry["python_deep_bytes"])
        workspace_ratio = (
            target_row["peak_target_workspace_logical_bytes"] / logical_baseline
        )
        retained_python_ratio = (
            target_row["peak_target_workspace_python_bytes"] / python_baseline
        )
        functional = (
            target_row["polynomial_s3_roots"] == independent_s3_roots
            and target_row["polynomial_s4_roots"] == independent_s4_roots
            and target_row["all_root_recovery_audit"][
                "all_requested_roots_recovered"
            ]
            and all(
                branch["equivalent_up_to_expected_scalar"]
                for branch in target_row["branches"]
            )
            and exact_query["success"]
            == target_row["solver_recovery"]["success"]
        )
        advice_pass = preprocessing["advice_ratio_to_symmetry_d3"] <= 0.8
        workspace_pass = workspace_ratio <= 0.8
        online_pass = all(
            ratio is not None and ratio <= 0.8 for ratio in online_ratios.values()
        )
        amortization_pass = all(
            value is not None and value <= len(factor_points)
            for value in crossovers.values()
        )
        gates = target_row["gates"]
        gate_expectations = {
            "functional_gate": functional,
            "advice_ratio_to_symmetry_d3": preprocessing[
                "advice_ratio_to_symmetry_d3"
            ],
            "advice_gate": advice_pass,
            "workspace_logical_ratio_to_symmetry_d3": workspace_ratio,
            "retained_python_ratio_to_symmetry_d3": retained_python_ratio,
            "workspace_gate": workspace_pass,
            "online_weighted_ratios_to_exact_d2_d3": online_ratios,
            "online_gate": online_pass,
            "preprocessing_crossover_targets": crossovers,
            "translator_preprocessing_weighted_work": translator_preprocessing,
            "comparator_d3_preprocessing_weighted_work": comparator_preprocessing,
            "crossover_preprocessing_differential": preprocessing_differential,
            "amortization_within_b_gate": amortization_pass,
            "pre_matched_coordinate_gate": (
                functional
                and advice_pass
                and workspace_pass
                and online_pass
                and amortization_pass
            ),
        }
        for key, expected in gate_expectations.items():
            if gates[key] != expected:
                raise AssertionError(f"translator gate {key} is inconsistent")
        for recovery_name in ("solver_recovery", "all_root_recovery_audit"):
            recovery = target_row[recovery_name]
            for recovered in recovery["recovered_roots"]:
                witness = recovered["witness"]
                if witness is None:
                    raise AssertionError(
                        f"{recovery_name} translator root lacks a full witness"
                    )
                if independent_sum(
                    curve, [factor_points[index] for index in witness]
                ) != target:
                    raise AssertionError(
                        f"{recovery_name} translator witness does not sum to target"
                    )
                verified_witnesses += 1
            identity = recovery.get("identity")
            if identity is not None:
                if independent_sum(
                    curve, [factor_points[index] for index in identity["witness"]]
                ) != target:
                    raise AssertionError(
                        f"{recovery_name} identity-route witness does not sum to target"
                    )
                verified_witnesses += 1

    if translator:
        projection = translator["amortized_projection"]
        matched_rows = translator["matched_uniform_targets"]
        available_supported = row["d5_audit"]["support_size"] - int(
            row["d5_audit"]["identity_present"]
        )
        realized_supported = min(
            requested_coordinate_targets, available_supported
        )
        expected_supported_cardinality = {
            "requested_count": requested_coordinate_targets,
            "available_count": available_supported,
            "realized_count": realized_supported,
            "count_was_clamped": (
                realized_supported != requested_coordinate_targets
            ),
            "cardinality_status": (
                "EXACT"
                if realized_supported == requested_coordinate_targets
                else "INSUFFICIENT_SUPPORT"
            ),
            "cardinality_gate": (
                realized_supported == requested_coordinate_targets
            ),
        }
        realized_matched = min(requested_coordinate_targets, q - 1)
        expected_matched_cardinality = {
            "requested_count": requested_coordinate_targets,
            "available_count": q - 1,
            "realized_count": realized_matched,
            "count_was_clamped": realized_matched != requested_coordinate_targets,
            "cardinality_status": (
                "EXACT"
                if realized_matched == requested_coordinate_targets
                else "INSUFFICIENT_SUPPORT"
            ),
            "cardinality_gate": realized_matched == requested_coordinate_targets,
        }
        if (
            translator["coordinate_target_cardinality"]
            != expected_supported_cardinality
            or translator["matched_uniform_target_cardinality"]
            != expected_matched_cardinality
            or len(translator["targets"]) != realized_supported
            or len(matched_rows) != realized_matched
            or translator["schedule"]["count"] != realized_supported
            or translator["matched_uniform_schedule"]["count"]
            != realized_matched
        ):
            raise AssertionError("translator target cardinality is inconsistent")
        expected_functional = (
            expected_supported_cardinality["cardinality_gate"]
            and expected_matched_cardinality["cardinality_gate"]
            and translator["s3_identity_target_control"]["functional_gate"]
            and all(
                target["gates"]["functional_gate"]
                for target in translator["targets"] + matched_rows
            )
        )
        expected_pre_matched = (
            expected_supported_cardinality["cardinality_gate"]
            and expected_matched_cardinality["cardinality_gate"]
            and translator["s3_identity_target_control"]["functional_gate"]
            and all(
                target["gates"]["pre_matched_coordinate_gate"]
                for target in translator["targets"] + matched_rows
            )
        )
        if (
            translator["functional_gate"] != expected_functional
            or translator["pre_matched_coordinate_gate"]
            != expected_pre_matched
        ):
            raise AssertionError("translator-wide gate conjunction is inconsistent")
        preprocessing_ops = preprocessing["operations"]
        translator_preprocessing = {
            str(weight): preprocessing_ops["coefficient_multiplications"]
            + weight * preprocessing_ops["coefficient_inversions"]
            for weight in GENERATOR.INVERSION_WEIGHTS
        }
        d3_build_ops = d3_record["build_ops"]
        comparator_preprocessing = {
            str(weight): d3_build_ops["field_multiplications"]
            + weight * d3_build_ops["field_inversions"]
            for weight in GENERATOR.INVERSION_WEIGHTS
        }
        if (
            projection["translator_preprocessing_weighted_work"]
            != translator_preprocessing
            or projection["comparator_d3_preprocessing_weighted_work"]
            != comparator_preprocessing
        ):
            raise AssertionError("translator projection preprocessing is inconsistent")
        support_count = sum(
            target["exact_d2_d3_query"]["success"] for target in matched_rows
        )
        support_rate = support_count / len(matched_rows)
        expected_counts = {1, len(factor_points), 16 * len(factor_points)}
        if {row["target_count"] for row in projection["rows"]} != expected_counts:
            raise AssertionError("translator projection target counts are incomplete")
        for projection_row in projection["rows"]:
            target_count = projection_row["target_count"]
            if (
                projection_row["sample_target_count"] != len(matched_rows)
                or projection_row["sample_supported_count"] != support_count
                or projection_row["sample_support_rate"] != support_rate
                or projection_row["projected_supported_targets"]
                != target_count * support_rate
            ):
                raise AssertionError("translator projection support accounting differs")
            for weight in GENERATOR.INVERSION_WEIGHTS:
                key = str(weight)
                candidate_online = statistics.fmean(
                    target["candidate_weighted_field_work"][key]
                    for target in matched_rows
                )
                comparator_online = statistics.fmean(
                    target["exact_d2_d3_query"]["weighted_field_work"][key]
                    for target in matched_rows
                )
                candidate_total = (
                    translator_preprocessing[key] + target_count * candidate_online
                )
                comparator_total = (
                    comparator_preprocessing[key] + target_count * comparator_online
                )
                expected = {
                    "candidate_mean_online": candidate_online,
                    "comparator_mean_online": comparator_online,
                    "candidate_projected_total": candidate_total,
                    "comparator_projected_total": comparator_total,
                    "candidate_to_comparator_total_ratio": (
                        None
                        if comparator_total == 0
                        else candidate_total / comparator_total
                    ),
                }
                if projection_row["weighted_field_work"][key] != expected:
                    raise AssertionError("translator projected totals are inconsistent")

    return {
        "factor_points": len(factor_points),
        "d2_points": len(d2_points),
        "d3_points": len(d3_points),
        "translator_witnesses": verified_witnesses,
    }


def verify_artifact(document: dict[str, Any], allow_development: bool) -> dict[str, Any]:
    if document["protocol"] != GENERATOR.PROTOCOL:
        raise AssertionError("protocol mismatch")
    if document["source_hashes"] != GENERATOR.bound_source_hashes():
        raise AssertionError("source-hash binding mismatch")
    source_recheck = document["source_hash_recheck"]
    if (
        source_recheck["performed"] is not bool(document["source_hashes"])
        or source_recheck["stable"] is not True
        or source_recheck["end_digest"]
        != GENERATOR.stable_digest(document["source_hashes"])
    ):
        raise AssertionError("source-hash boundary recheck is invalid")
    frozen = document["configuration_is_frozen"]
    if type(frozen) is not bool:
        raise AssertionError("configuration freeze flag is not boolean")
    if frozen:
        if document["development_only"]:
            raise AssertionError("frozen artifact is marked development-only")
    elif not allow_development:
        raise AssertionError("development artifact requires --allow-development")
    elif not document["development_only"]:
        raise AssertionError("nonfrozen artifact is not marked development-only")

    replay = GENERATOR.run_experiment(
        document["configuration"],
        frozen,
        bind_sources=bool(document["source_hashes"]),
    )
    validate_replay_volatiles(document)
    validate_replay_volatiles(replay)
    validate_batch_timing_derivations(document)
    validate_batch_timing_derivations(replay)
    compare_exact(strip_replay_volatiles(document), strip_replay_volatiles(replay))

    aggregate = {
        "instances": 0,
        "families": 0,
        "factor_points": 0,
        "d2_points": 0,
        "d3_points": 0,
        "translator_witnesses": 0,
    }
    preflight = document["curve_schedule_preflight"]
    if (
        preflight["curve_count"] != len(document["instances"])
        or preflight["unique_field_modulus_count"] != len(document["instances"])
        or preflight["mov_embedding_degree_threshold"]
        != GENERATOR.MOV_EMBEDDING_DEGREE_THRESHOLD
        or preflight["field_family_restriction"] != "p mod 4 = 3"
    ):
        raise AssertionError("curve-schedule preflight summary is inconsistent")
    expected_preflight_curves = [
        {
            "bits": instance["bits"],
            "seed": instance["seed"],
            "curve_id": instance["curve"]["id"],
            "p": instance["curve"]["p"],
            "q": instance["curve"]["q"],
            "embedding_degree": instance["curve"]["embedding_degree"],
        }
        for instance in document["instances"]
    ]
    if preflight["curves"] != expected_preflight_curves:
        raise AssertionError("curve-schedule preflight rows differ from instances")
    used_primes: set[int] = set()
    for instance in document["instances"]:
        curve_record = instance["curve"]
        if not independent_is_prime(curve_record["p"]):
            raise AssertionError("field modulus is not independently prime")
        if not independent_is_prime(curve_record["q"]):
            raise AssertionError("recorded group order is not independently prime")
        if curve_record["cofactor"] != 1 or curve_record["order"] != curve_record["q"]:
            raise AssertionError("curve is not recorded as cofactor-one prime order")
        curve = IndependentCurve(
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        if curve.order() != curve_record["q"]:
            raise AssertionError("independent curve order mismatch")
        degree = independent_embedding_degree(curve_record["p"], curve_record["q"])
        if (
            curve_record["p"] % 4 != 3
            or curve_record["field_family_restriction"] != "p mod 4 = 3"
            or curve_record["embedding_degree"] != degree
            or curve_record["mov_exceptional"] is not False
            or degree <= curve_record["mov_exclusion_threshold"]
        ):
            raise AssertionError("field-family or MOV preflight record is invalid")
        trace = curve_record["p"] + 1 - curve_record["q"]
        if trace in (0, 1) or curve_record["trace"] != trace:
            raise AssertionError("curve trace violates the clean-curve contract")
        denominator = (
            4 * pow(curve.a, 3, curve.p) + 27 * pow(curve.b, 2, curve.p)
        ) % curve.p
        j_invariant = 1728 * 4 * pow(curve.a, 3, curve.p) * pow(
            denominator, -1, curve.p
        ) % curve.p
        if (
            j_invariant in (0, 1728 % curve.p)
            or curve_record["j_invariant"] != j_invariant
        ):
            raise AssertionError("curve j-invariant violates the clean-curve contract")
        if curve_record["p"] in used_primes:
            raise AssertionError("field modulus repeated across instances")
        used_primes.add(curve_record["p"])
        generator = point_from_json(curve_record["generator"])
        if generator is None or not curve.on_curve(generator):
            raise AssertionError("generator is invalid")
        if curve.mul(curve_record["q"], generator) is not None:
            raise AssertionError("generator does not have the recorded order")
        aggregate["instances"] += 1
        matched_target_sets: list[list[Any]] = []
        translator_contexts: list[tuple[str, dict[str, Any]]] = []
        for row in instance["rows"]:
            counts = verify_row(
                curve,
                curve_record["q"],
                row,
                document["configuration"]["coordinate_targets"],
            )
            aggregate["families"] += 1
            for key, value in counts.items():
                aggregate[key] += value
            translator = row.get("translator")
            if translator:
                translator_contexts.append((row["family"], translator))
                matched_targets = [
                    target["target"]
                    for target in translator["matched_uniform_targets"]
                ]
                matched_target_sets.append(matched_targets)
                matched_record = translator["matched_random_x"]
                if matched_record["shared_target_count"] != len(matched_targets):
                    raise AssertionError("matched target count is inconsistent")
                support_count = sum(
                    target["exact_d2_d3_query"]["success"]
                    for target in translator["matched_uniform_targets"]
                )
                if matched_record["coordinate_support_count"] != support_count:
                    raise AssertionError("matched support count is inconsistent")
        if matched_target_sets and any(
            targets != matched_target_sets[0] for targets in matched_target_sets[1:]
        ):
            raise AssertionError("coordinate families do not share identical targets")
        if translator_contexts:
            random_translator = next(
                translator
                for family, translator in translator_contexts
                if family == "random_x"
            )
            random_targets = random_translator["matched_uniform_targets"]
            random_work = {
                str(weight): statistics.fmean(
                    target["candidate_weighted_field_work"][str(weight)]
                    for target in random_targets
                )
                for weight in GENERATOR.INVERSION_WEIGHTS
            }
            random_density = statistics.fmean(
                target["combined_g"]["density"] for target in random_targets
            )
            random_support = sum(
                target["exact_d2_d3_query"]["success"]
                for target in random_targets
            )
            for family, translator in translator_contexts:
                targets = translator["matched_uniform_targets"]
                ratios = {
                    str(weight): (
                        None
                        if random_work[str(weight)] == 0
                        else statistics.fmean(
                            target["candidate_weighted_field_work"][str(weight)]
                            for target in targets
                        )
                        / random_work[str(weight)]
                    )
                    for weight in GENERATOR.INVERSION_WEIGHTS
                }
                density = statistics.fmean(
                    target["combined_g"]["density"] for target in targets
                )
                density_ratio = (
                    None if random_density == 0 else density / random_density
                )
                support = sum(
                    target["exact_d2_d3_query"]["success"] for target in targets
                )
                support_not_worse = support >= random_support
                same_map = family == "x_interval"
                matched_pass = (
                    same_map
                    and support_not_worse
                    and (
                        all(
                            ratio is not None and ratio <= 0.8
                            for ratio in ratios.values()
                        )
                        or (density_ratio is not None and density_ratio <= 0.8)
                    )
                )
                record = translator["matched_random_x"]
                expected_fields = {
                    "weighted_work_ratios": ratios,
                    "combined_g_density_ratio": density_ratio,
                    "shared_target_count": len(targets),
                    "shared_target_digest": translator[
                        "matched_uniform_schedule"
                    ]["target_digest"],
                    "coordinate_support_count": support,
                    "random_x_support_count": random_support,
                    "support_not_worse": support_not_worse,
                    "same_map_null_available": same_map,
                    "comparison_status": (
                        "ELIGIBLE_IDENTITY_MAP_NULL"
                        if same_map
                        else "MAP_CONFOUNDED_NO_CONTINUATION"
                    ),
                    "matched_coordinate_gate": matched_pass,
                }
                for key, expected in expected_fields.items():
                    if record[key] != expected:
                        raise AssertionError(
                            f"matched random-x field {key} is inconsistent"
                        )
                expected_instance_gate = (
                    translator["functional_gate"]
                    and translator["pre_matched_coordinate_gate"]
                    and translator["coordinate_target_cardinality"][
                        "cardinality_gate"
                    ]
                    and translator["matched_uniform_target_cardinality"][
                        "cardinality_gate"
                    ]
                    and matched_pass
                )
                if translator["coordinate_instance_gate"] != expected_instance_gate:
                    raise AssertionError("coordinate instance gate is inconsistent")
    verify_continuation_aggregate(document)
    return aggregate


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--allow-development", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    document = load_json_strict(args.input)
    if type(document) is not dict:
        raise AssertionError("artifact must be one JSON object")
    counts = verify_artifact(document, args.allow_development)
    receipt = {
        "protocol": document["protocol"],
        "status": "verified",
        "development_only": document["development_only"],
        "canonical_configuration": document["configuration_is_frozen"],
        "input_file_sha256": sha256_file(args.input),
        "generator_sha256": sha256_file(GENERATOR_PATH),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "verified_instances": counts["instances"],
        "verified_families": counts["families"],
        "verified_factor_points": counts["factor_points"],
        "verified_d2_points": counts["d2_points"],
        "verified_d3_points": counts["d3_points"],
        "verified_translator_witnesses": counts["translator_witnesses"],
        "timing_status": "UNVERIFIED_DIAGNOSTIC",
        "boundary": (
            "Deterministic replay plus independent affine/order/support/root/"
            "witness audit; wall timings are unattested diagnostics, and "
            "verification is not an exponent result or ECDLP break."
        ),
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        if args.output.exists():
            raise FileExistsError(f"refusing to overwrite receipt: {args.output}")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
