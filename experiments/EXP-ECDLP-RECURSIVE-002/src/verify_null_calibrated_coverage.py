#!/usr/bin/env python3
"""Independent verifier for EXP-ECDLP-RECURSIVE-002-v2.

This verifier never imports the EXP-ECDLP-RECURSIVE-002 generator.  It uses
the prior independent arithmetic verifier only as an independently-written
affine-arithmetic component, and SHA-256 binds that component, both original
dependencies, and the read-only generator before replaying a document.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import random
import statistics
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


PROTOCOL = "EXP-ECDLP-RECURSIVE-002-v2"
VERIFIER_PROTOCOL = "EXP-ECDLP-RECURSIVE-002-v2-independent-verifier"
SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENTS_ROOT = SCRIPT_PATH.parents[2]
GENERATOR_PATH = SCRIPT_PATH.with_name("null_calibrated_coverage.py")
PRIOR_VERIFIER_PATH = (
    EXPERIMENTS_ROOT
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "verify_recursive_expansion.py"
)
RECURSIVE_SOURCE_PATH = (
    EXPERIMENTS_ROOT
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)
ENERGY_SOURCE_PATH = (
    EXPERIMENTS_ROOT
    / "EXP-ECDLP-ENERGY-001"
    / "src"
    / "coordinate_energy.py"
)
EXPECTED_HASHES = {
    "null_calibrated_coverage_sha256": "b3c9cd083af9e838c009bf76f83ac4fd6909c4c9160fcaada122d9f0a6de95bd",
    "prior_independent_arithmetic_verifier_sha256": "d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552",
    "recursive_expansion_sha256": "c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d",
    "coordinate_energy_sha256": "7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71",
}
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
CANDIDATE_FAMILIES = ["x_interval", "square_map", "rational_union"]
NULL_FAMILIES = ["random", "random_x"]
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [2473001, 2473004, 2473012],
    "candidate_families": CANDIDATE_FAMILIES,
    "null_families": NULL_FAMILIES,
    "null_replicates_per_family": 31,
    "m": 8,
    "symmetry_mode": "sign_complete",
    "target_count": 128,
    "order_seeds": [811, 821, 823, 827],
    "occupancy_lambda": 0.5,
    "rho_trials": 2,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_hashes() -> dict[str, str]:
    actual = {
        "null_calibrated_coverage_sha256": sha256_file(GENERATOR_PATH),
        "prior_independent_arithmetic_verifier_sha256": sha256_file(PRIOR_VERIFIER_PATH),
        "recursive_expansion_sha256": sha256_file(RECURSIVE_SOURCE_PATH),
        "coordinate_energy_sha256": sha256_file(ENERGY_SOURCE_PATH),
    }
    if actual != EXPECTED_HASHES:
        raise AssertionError(
            "source hash mismatch; generator/dependency changes require an "
            f"explicit verifier update: expected {EXPECTED_HASHES!r}, observed {actual!r}"
        )
    return actual


def load_prior_arithmetic() -> Any:
    """Load the prior *independent verifier*, never the new generator."""
    spec = importlib.util.spec_from_file_location("recursive_001_independent", PRIOR_VERIFIER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prior arithmetic verifier: {PRIOR_VERIFIER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRIOR = load_prior_arithmetic()
Point = tuple[int, int] | None


def require_exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} must be an exact integer, got {type(value).__name__}")
    if minimum is not None and value < minimum:
        raise AssertionError(f"{label} must be at least {minimum}")
    return value


def assert_exact(actual: Any, expected: Any, path: str = "document") -> None:
    if type(actual) is not type(expected):
        raise AssertionError(f"{path}: type mismatch: got {type(actual).__name__}, expected {type(expected).__name__}")
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(f"{path}: key mismatch: missing={sorted(set(expected)-set(actual))}, extra={sorted(set(actual)-set(expected))}")
        for key in expected:
            assert_exact(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: length mismatch: got {len(actual)}, expected {len(expected)}")
        for index, (got, want) in enumerate(zip(actual, expected)):
            assert_exact(got, want, f"{path}[{index}]")
    elif isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"{path}: float mismatch: got {actual!r}, expected {expected!r}")
    elif actual != expected:
        raise AssertionError(f"{path}: mismatch: got {actual!r}, expected {expected!r}")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def j_invariant(p: int, a: int, b: int) -> int:
    four_a3 = 4 * pow(a, 3, p) % p
    denominator = (four_a3 + 27 * pow(b, 2, p)) % p
    if denominator == 0:
        raise AssertionError("singular curve has no j-invariant")
    return 1728 * four_a3 * pow(denominator, -1, p) % p


def curve_rejection_reason(p: int, a: int, b: int, order: int) -> str | None:
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        return "singular"
    trace = p + 1 - order
    if trace == 0:
        return "trace_zero"
    if trace == 1:
        return "anomalous_trace_one"
    if not PRIOR.is_prime(order):
        return "composite_order"
    if j_invariant(p, a, b) in (0, 1728 % p):
        return "special_j"
    return None


def reconstruct_clean_curve(bits: int, seed: int, max_attempts: int = 256) -> dict[str, Any]:
    p = PRIOR.field_prime(bits, seed ^ 0x6A09E667)
    rng = random.Random((seed << 17) ^ bits ^ 0x510E527F)
    rejections = {"singular": 0, "trace_zero": 0, "anomalous_trace_one": 0, "composite_order": 0, "special_j": 0}
    counted_orders = 0
    for attempt in range(1, max_attempts + 1):
        a, b = rng.randrange(1, p), rng.randrange(1, p)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            rejections["singular"] += 1
            continue
        counted_orders += 1
        order = PRIOR.curve_order(p, a, b)
        rejection = curve_rejection_reason(p, a, b, order)
        if rejection is not None:
            rejections[rejection] += 1
            continue
        trace = p + 1 - order
        j_value = j_invariant(p, a, b)
        ops = PRIOR.VerifyOps()
        start = rng.randrange(p)
        generator: Point = None
        source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = PRIOR.square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = (x, y)
            if PRIOR.point_mul(order, candidate, p, a, ops) is None:
                generator, source_x = candidate, x
                break
        if generator is not None:
            return {
                "id": f"nullcal-toy-p{p}-a{a}-b{b}-q{order}", "bits": bits, "p": p,
                "p_mod_4": p % 4, "field_modulus_policy": "seeded bits-bit prime constrained to p mod 4 = 3",
                "a": a, "b": b, "j_invariant": j_value, "order": order, "trace": trace,
                "q": order, "cofactor": 1, "generator": list(generator), "generator_source_x": source_x,
                "curve_attempts": attempt, "order_count_legendre_tests": counted_orders * p,
                "generator_ops": asdict(ops), "p_minus_1_factors": PRIOR.prime_factors(p - 1),
                "rejections": rejections,
                "selection_policy": "first seeded nonsingular prime-order curve with trace not 0 or 1 and j not 0 or 1728",
            }
    raise AssertionError(f"clean prime-order curve search exhausted at {bits} bits")


def point_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def signed_class_count(fiber_count: int, terms: int) -> int:
    total = 0
    for residue_terms in range(terms % 2, terms + 1, 2):
        if residue_terms == 0:
            total += 1
        else:
            for support_size in range(1, min(fiber_count, residue_terms) + 1):
                total += math.comb(fiber_count, support_size) * math.comb(residue_terms - 1, support_size - 1) * 2**support_size
    return total


def binary_pow_field_multiplications(exponent: int) -> int:
    if exponent < 1:
        return 0
    return exponent.bit_length() - 1 + exponent.bit_count() - 1


def charged_build_diagnostics(
    factor_base: dict[str, Any], p: int
) -> dict[str, Any]:
    diagnostics = dict(factor_base["build_diagnostics"])
    square_root_tests = diagnostics["square_root_tests"]
    successful_roots = diagnostics["subgroup_tests"]
    legendre_multiplications = square_root_tests * binary_pow_field_multiplications(
        (p - 1) // 2
    )
    root_multiplications = successful_roots * (
        binary_pow_field_multiplications((p + 1) // 4) + 1
    )
    map_multiplications = 0
    map_inversions = 0
    if factor_base["name"] == "square_map":
        map_multiplications = square_root_tests
    elif factor_base["name"] == "rational_union":
        final_source = factor_base["fibers"][-1]["source"]
        final_t = final_source["t"]
        zero_denominator_t = (-final_source["e"]) % p
        map_inversions = final_t - int(zero_denominator_t < final_t)
        map_inversions += int(final_source["map"] == "mobius")
        map_multiplications = final_t + 1 + map_inversions
    diagnostics.update(
        {
            "legendre_exponentiations": square_root_tests,
            "square_root_exponentiations": successful_roots,
            "charged_pow_field_multiplications": (
                legendre_multiplications + root_multiplications
            ),
            "coordinate_rhs_field_multiplications": 3 * square_root_tests,
            "map_field_multiplications": map_multiplications,
            "map_field_inversions": map_inversions,
            "charged_cost_model": (
                "binary-square-and-multiply field-multiplication proxy; "
                "successful roots conservatively include one root verification"
            ),
        }
    )
    return diagnostics


def make_base(family: str, p: int, a: int, b: int, q: int, generator: Point, size: int, seed: int) -> dict[str, Any]:
    # factor_base is independently reconstructed in EXP-001's independent verifier.
    result = PRIOR.factor_base(
        family, "sign_complete", p, a, b, q, generator, size, seed
    )
    result["seed"] = seed
    result["build_diagnostics"] = charged_build_diagnostics(result, p)
    return result


def support_chain(p: int, a: int, points: list[Point], maximum: int) -> tuple[list[dict[Point, tuple[int, ...]]], Any]:
    return PRIOR.support_chain(p, a, points, maximum)


def compile_base(
    p: int,
    a: int,
    q: int,
    factor_base: dict[str, Any],
    targets: list[dict[str, Any]],
    order_seeds: list[int],
) -> dict[str, Any]:
    points = [tuple(point) for point in factor_base["points"]]
    compiler_chain, compiler_ops = support_chain(p, a, points, 4)
    expansion_chain, expansion_ops = support_chain(p, a, points, 8)
    advice_map = compiler_chain[4]
    exact_support = expansion_chain[8]
    advice_entries = len(advice_map)
    advice_map_bytes = PRIOR.deep_size(advice_map)
    factor_base_bytes = PRIOR.deep_size(points)
    compiled_artifact_bytes = PRIOR.deep_size(
        {"factor_base": points, "advice": advice_map}
    )
    exact_epsilon = len(exact_support) / q

    canonical_items = sorted(advice_map.items(), key=lambda item: point_key(item[0]))
    exact_order_control_ops = PRIOR.VerifyOps()
    target_order_expectations: list[dict[str, Any]] = []
    for target_index, target_record in enumerate(targets):
        target = tuple(target_record["point"])
        successful_partials = 0
        for partial, _ in canonical_items:
            complement = PRIOR.point_add(
                target,
                PRIOR.point_neg(partial, p),
                p,
                a,
                exact_order_control_ops,
            )
            successful_partials += int(complement in advice_map)
        exact_membership = target in exact_support
        if (successful_partials > 0) != exact_membership:
            raise AssertionError("exact first-hit count disagrees with support")
        numerator = advice_entries + 1 if successful_partials else advice_entries
        denominator = successful_partials + 1 if successful_partials else 1
        target_order_expectations.append(
            {
                "target_index": target_index,
                "successful_partials": successful_partials,
                "exact_membership": exact_membership,
                "expected_first_hit_numerator": numerator,
                "expected_first_hit_denominator": denominator,
                "expected_first_hit_lookups": numerator / denominator,
            }
        )
    exact_uniform_average = statistics.fmean(
        row["expected_first_hit_lookups"] for row in target_order_expectations
    )

    order_results: list[dict[str, Any]] = []
    first_witness: dict[str, Any] | None = None
    for order_index, order_seed in enumerate(order_seeds):
        ordered_items = list(canonical_items)
        random.Random(order_seed ^ factor_base["seed"]).shuffle(ordered_items)
        ops = PRIOR.VerifyOps()
        lookups = 0
        per_target_ops: list[int] = []
        per_target_lookups: list[int] = []
        successes = 0
        for target_index, target_record in enumerate(targets):
            target = tuple(target_record["point"])
            before_ops = ops.group_operations
            before_lookups = lookups
            found: tuple[int, ...] | None = None
            for partial, partial_witness in ordered_items:
                complement = PRIOR.point_add(
                    target, PRIOR.point_neg(partial, p), p, a, ops
                )
                lookups += 1
                other_witness = advice_map.get(complement)
                if other_witness is None:
                    continue
                found = partial_witness + other_witness
                break
            per_target_ops.append(ops.group_operations - before_ops)
            per_target_lookups.append(lookups - before_lookups)
            exact_membership = target in exact_support
            if (found is not None) != exact_membership:
                raise AssertionError("shuffled split scan disagrees with exact support")
            if found is not None:
                successes += 1
                recovered: Point = None
                for index in found:
                    recovered = PRIOR.point_add(recovered, points[index], p, a)
                if recovered != target:
                    raise AssertionError(
                        "shuffled split witness failed independent arithmetic"
                    )
                if first_witness is None and order_index == 0:
                    first_witness = {
                        "order_seed": order_seed,
                        "target_index": target_index,
                        "indices": list(found),
                        "target": target_record["point"],
                    }
        sampled_average = statistics.fmean(per_target_lookups)
        order_results.append(
            {
                "order_seed": order_seed,
                "sampled_successful_targets": successes,
                "online_group_operations": ops.group_operations,
                "online_lookups": lookups,
                "per_target_group_operations": per_target_ops,
                "per_target_lookups": per_target_lookups,
                "average_online_group_operations_per_target": statistics.fmean(
                    per_target_ops
                ),
                "median_online_group_operations_per_target": statistics.median(
                    per_target_ops
                ),
                "maximum_online_group_operations_per_target": max(per_target_ops),
                "relative_error_to_exact_uniform_expectation": abs(
                    sampled_average - exact_uniform_average
                )
                / exact_uniform_average,
            }
        )

    order_averages = [
        row["average_online_group_operations_per_target"]
        for row in order_results
    ]
    sampled_median_online = statistics.median(order_averages)
    order_variation = max(order_averages) / min(order_averages)
    sampled_expectation_error = max(
        row["relative_error_to_exact_uniform_expectation"] for row in order_results
    )
    order_control_passed = (
        order_variation <= 1.25 and sampled_expectation_error <= 0.25
    )
    frontier_score = (
        compiled_artifact_bytes * exact_uniform_average**2 / (exact_epsilon * q)
    )
    compiler_dict = asdict(compiler_ops)
    offline_ops = {
        key: factor_base["build_ops"][key] + compiler_dict[key]
        for key in compiler_dict
    }
    build_diagnostics = factor_base["build_diagnostics"]
    offline_charged_cost = {
        "group_operations": offline_ops["group_operations"],
        "charged_field_multiplications": (
            offline_ops["field_multiplications"]
            + build_diagnostics["charged_pow_field_multiplications"]
            + build_diagnostics["coordinate_rhs_field_multiplications"]
            + build_diagnostics["map_field_multiplications"]
        ),
        "charged_field_inversions": (
            offline_ops["field_inversions"]
            + build_diagnostics["map_field_inversions"]
        ),
        "model": (
            "curve-operation counters plus binary-pow multiplication proxy, "
            "coordinate RHS arithmetic, and explicit map arithmetic"
        ),
    }
    median_lookups = statistics.median(
        row["online_lookups"] for row in order_results
    )
    return {
        "name": factor_base["name"],
        "seed": factor_base["seed"],
        "size": factor_base["size"],
        "factor_base_digest": stable_digest(factor_base),
        "build_ops": factor_base["build_ops"],
        "build_diagnostics": build_diagnostics,
        "compiler_ops": compiler_dict,
        "diagnostic_expansion_ops": asdict(expansion_ops),
        "offline_ops": offline_ops,
        "offline_charged_cost": offline_charged_cost,
        "four_term_support_size": advice_entries,
        "generic_signed_four_term_maximum": signed_class_count(
            len(points) // 2, 4
        ),
        "eight_term_support_size": len(exact_support),
        "exact_success_probability": exact_epsilon,
        "coverage_efficiency": len(exact_support) / (advice_entries**2),
        "advice_entries": advice_entries,
        "advice_map_deep_bytes": advice_map_bytes,
        "factor_base_deep_bytes": factor_base_bytes,
        "compiled_artifact_deep_bytes": compiled_artifact_bytes,
        "functional_artifact_retention": (
            "reconstructible from factor-base digest and frozen sources; "
            "not duplicated in the result document"
        ),
        "target_order_expectations": target_order_expectations,
        "exact_order_control_group_operations": (
            exact_order_control_ops.group_operations
        ),
        "exact_uniform_average_first_hit_lookups_per_target": (
            exact_uniform_average
        ),
        "order_results": order_results,
        "sampled_median_online_group_operations_per_target": (
            sampled_median_online
        ),
        "order_independent_online_group_operations_per_target": (
            exact_uniform_average
        ),
        "order_variation_ratio": order_variation,
        "maximum_sampled_expectation_relative_error": sampled_expectation_error,
        "order_control_passed": order_control_passed,
        "functional_frontier_score": frontier_score,
        "lookup_traffic_model": {
            "lookups_at_sampled_median": median_lookups,
            "assumed_bytes_per_lookup": 64,
            "assumed_traffic_bytes": int(median_lookups * 64),
            "boundary": "assumption only; lookup count is measured",
        },
        "first_witness": first_witness,
    }


def empirical_percentile(
    value: float, distribution: list[float], higher_is_better: bool
) -> float:
    return empirical_percentile_detail(value, distribution, higher_is_better)[
        "percentile"
    ]


def empirical_percentile_detail(
    value: float, distribution: list[float], higher_is_better: bool
) -> dict[str, Any]:
    if not distribution:
        raise AssertionError("empty null distribution")
    favorable = (
        sum(item < value for item in distribution)
        if higher_is_better
        else sum(item > value for item in distribution)
    )
    tied = sum(item == value for item in distribution)
    denominator = len(distribution) + 1
    return {
        "percentile": (1 + favorable + 0.5 * tied) / denominator,
        "favorable_null_count": favorable,
        "tied_null_count": tied,
        "null_count": len(distribution),
        "finite_null_denominator": denominator,
        "higher_is_better": higher_is_better,
    }


def distribution_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    directions = {
        "eight_term_support_size": True,
        "coverage_efficiency": True,
        "functional_frontier_score": False,
        "four_term_support_size": True,
        "offline_group_operations": False,
        "offline_charged_field_multiplications": False,
        "offline_charged_field_inversions": False,
    }
    summary: dict[str, Any] = {"replicates": len(rows)}
    for metric in directions:
        values = [
            (
                row["offline_ops"]["group_operations"]
                if metric == "offline_group_operations"
                else row["offline_charged_cost"][metric.removeprefix("offline_")]
                if metric.startswith("offline_charged_")
                else row[metric]
            )
            for row in rows
        ]
        summary[metric] = {
            "values": values,
            "minimum": min(values),
            "median": statistics.median(values),
            "maximum": max(values),
        }
    return summary


def attach_percentiles(
    candidate: dict[str, Any], null_rows: dict[str, list[dict[str, Any]]]
) -> None:
    candidate["null_percentiles"] = {}
    candidate["null_rank_details"] = {}
    for name, rows in null_rows.items():
        rank_details = {
            "eight_term_support": empirical_percentile_detail(
                candidate["eight_term_support_size"],
                [row["eight_term_support_size"] for row in rows],
                True,
            ),
            "coverage_efficiency": empirical_percentile_detail(
                candidate["coverage_efficiency"],
                [row["coverage_efficiency"] for row in rows],
                True,
            ),
            "functional_frontier": empirical_percentile_detail(
                candidate["functional_frontier_score"],
                [row["functional_frontier_score"] for row in rows],
                False,
            ),
        }
        candidate["null_rank_details"][name] = rank_details
        candidate["null_percentiles"][name] = {
            metric: detail["percentile"] for metric, detail in rank_details.items()
        }
    candidate["offline_cost_ratios_to_random_x_median"] = {}
    for metric in (
        "group_operations",
        "charged_field_multiplications",
        "charged_field_inversions",
    ):
        candidate_value = candidate["offline_charged_cost"][metric]
        random_x_median = statistics.median(
            row["offline_charged_cost"][metric] for row in null_rows["random_x"]
        )
        candidate["offline_cost_ratios_to_random_x_median"][metric] = (
            candidate_value / random_x_median if random_x_median else 1.0
        )
    candidate["split_support_ratio_to_random_medians"] = {
        name: candidate["four_term_support_size"]
        / statistics.median(row["four_term_support_size"] for row in rows)
        for name, rows in null_rows.items()
    }
    candidate["instance_gate_passed"] = (
        all(
            values["eight_term_support"] >= 0.95
            and values["coverage_efficiency"] >= 0.95
            and values["functional_frontier"] >= 0.90
            for values in candidate["null_percentiles"].values()
        )
        and candidate["order_control_passed"]
        and all(
            ratio <= 4.0
            for ratio in candidate[
                "offline_cost_ratios_to_random_x_median"
            ].values()
        )
    )
    candidate["split_compression_gate_passed"] = all(
        ratio <= 0.8
        for ratio in candidate["split_support_ratio_to_random_medians"].values()
    )


def validate_config(config: Any, enforce_frozen: bool) -> dict[str, Any]:
    if type(config) is not dict or set(config) != set(FROZEN_CONFIG):
        raise AssertionError("config keys do not match protocol")
    for label, minimum in (("bit_sizes", 8), ("seeds", None), ("order_seeds", None)):
        values = config[label]
        if type(values) is not list or not values:
            raise AssertionError(f"config.{label} must be a nonempty list")
        for index, value in enumerate(values):
            require_exact_int(value, f"config.{label}[{index}]", minimum)
    for label, minimum in (
        ("null_replicates_per_family", 2),
        ("m", 8),
        ("target_count", 1),
        ("rho_trials", 1),
    ):
        require_exact_int(config[label], f"config.{label}", minimum)
    for label in ("bit_sizes", "seeds", "order_seeds"):
        if len(set(config[label])) != len(config[label]):
            raise AssertionError(f"config.{label} must be distinct")
    if config["rho_trials"] > config["target_count"]:
        raise AssertionError("rho trials exceed target count")
    occupancy = config["occupancy_lambda"]
    if (
        type(occupancy) not in (int, float)
        or isinstance(occupancy, bool)
        or not math.isfinite(occupancy)
        or occupancy <= 0
    ):
        raise AssertionError("config.occupancy_lambda must be finite and positive")
    if (
        type(config["candidate_families"]) is not list
        or type(config["null_families"]) is not list
        or type(config["symmetry_mode"]) is not str
    ):
        raise AssertionError("factor-base family and symmetry fields have wrong types")
    if (
        config["candidate_families"] != CANDIDATE_FAMILIES
        or config["null_families"] != NULL_FAMILIES
        or config["m"] != 8
        or config["symmetry_mode"] != "sign_complete"
    ):
        raise AssertionError("factor-base family or m=8 sign-complete schedule mismatch")
    if enforce_frozen:
        assert_exact(config, FROZEN_CONFIG, "document.config")
    return config


def aggregate_family_gate(
    instances: list[dict[str, Any]],
    candidate_families: list[str],
    bit_sizes: list[int],
    seeds: list[int],
    controls_passed: bool,
) -> dict[str, Any]:
    family_counts: dict[str, int] = {family: 0 for family in candidate_families}
    family_sizes: dict[str, set[int]] = {
        family: set() for family in candidate_families
    }
    family_seeds: dict[str, set[int]] = {
        family: set() for family in candidate_families
    }
    for instance in instances:
        for row in instance["candidate_rows"]:
            if not row["instance_gate_passed"]:
                continue
            family = row["name"]
            family_counts[family] += 1
            family_sizes[family].add(instance["curve"]["bits"])
            family_seeds[family].add(instance["seed"])
    promoted = []
    if controls_passed:
        promoted = sorted(
            family
            for family in candidate_families
            if family_counts[family] >= 6
            and family_sizes[family] == set(bit_sizes)
            and family_seeds[family] == set(seeds)
        )
    return {
        "family_pass_counts": family_counts,
        "family_pass_sizes": {
            family: sorted(values) for family, values in family_sizes.items()
        },
        "family_pass_seeds": {
            family: sorted(values) for family, values in family_seeds.items()
        },
        "promoted_families": promoted,
    }


def reconstruct_document(config: dict[str, Any]) -> dict[str, Any]:
    instances: list[dict[str, Any]] = []
    used_field_moduli: set[int] = set()
    used_base_seeds: set[int] = set()
    for seed_index, seed in enumerate(config["seeds"]):
        previous_q = 0
        for bits in config["bit_sizes"]:
            curve = reconstruct_clean_curve(bits, seed + bits * 1009)
            p, a, b, q = curve["p"], curve["a"], curve["b"], curve["q"]
            if p in used_field_moduli:
                raise AssertionError("field modulus repeated across scheduled curves")
            used_field_moduli.add(p)
            if q <= previous_q:
                raise AssertionError("clean subgroup schedule is not strictly increasing")
            previous_q = q
            if curve["trace"] in (0, 1) or curve["j_invariant"] in (
                0,
                1728 % p,
            ):
                raise AssertionError("clean curve policy failed")
            generator = tuple(curve["generator"])
            if (
                not PRIOR.on_curve(generator, p, a, b)
                or PRIOR.point_mul(q, generator, p, a) is not None
            ):
                raise AssertionError("generator failed independent subgroup check")
            targets_rng = random.Random(seed ^ (bits << 24) ^ 0x1F83D9AB)
            if config["target_count"] > q - 1:
                raise AssertionError(
                    "target count exceeds available nonzero subgroup points"
                )
            target_scalars = targets_rng.sample(
                range(1, q), config["target_count"]
            )
            targets = [
                {
                    "scalar": scalar,
                    "point": list(PRIOR.point_mul(scalar, generator, p, a)),
                }
                for scalar in target_scalars
            ]
            size = PRIOR.choose_factor_base_size(q, 8, config["occupancy_lambda"])

            def claim_base_seed(value: int) -> int:
                if value in used_base_seeds:
                    raise AssertionError("factor-base seed collision")
                used_base_seeds.add(value)
                return value

            null_rows: dict[str, list[dict[str, Any]]] = {}
            for family_index, family in enumerate(NULL_FAMILIES):
                rows = []
                for replicate in range(config["null_replicates_per_family"]):
                    base_seed = claim_base_seed(
                        seed
                        ^ (bits << 20)
                        ^ (family_index * 0x9E3779B1)
                        ^ (replicate * 0x85EBCA6B)
                    )
                    base = make_base(
                        family, p, a, b, q, generator, size, base_seed
                    )
                    row = compile_base(
                        p, a, q, base, targets, config["order_seeds"]
                    )
                    row["replicate"] = replicate
                    rows.append(row)
                null_rows[family] = rows

            candidates = []
            for family_index, family in enumerate(CANDIDATE_FAMILIES):
                base_seed = claim_base_seed(
                    seed
                    ^ (bits << 20)
                    ^ 0xC2B2AE35
                    ^ (family_index * 0x27D4EB2F)
                )
                base = make_base(family, p, a, b, q, generator, size, base_seed)
                row = compile_base(p, a, q, base, targets, config["order_seeds"])
                attach_percentiles(row, null_rows)
                candidates.append(row)

            control_seed = claim_base_seed(
                seed ^ (bits << 20) ^ 0x165667B1
            )
            control_base = make_base(
                "scalar_progression_positive_control",
                p,
                a,
                b,
                q,
                generator,
                size,
                control_seed,
            )
            control = compile_base(
                p, a, q, control_base, targets, config["order_seeds"]
            )
            random_split_median = statistics.median(
                row["four_term_support_size"] for row in null_rows["random"]
            )
            random_final_median = statistics.median(
                row["eight_term_support_size"] for row in null_rows["random"]
            )
            control["positive_control_passed"] = (
                control["four_term_support_size"] < random_split_median
                and control["eight_term_support_size"] < random_final_median
            )

            rho_trials = []
            for trial_index in range(config["rho_trials"]):
                target = tuple(targets[trial_index]["point"])
                trial = PRIOR.replay_rho(
                    p,
                    a,
                    q,
                    generator,
                    target,
                    seed ^ (bits << 12) ^ trial_index,
                )
                trial["known_scalar"] = targets[trial_index]["scalar"]
                if trial["recovered_scalar"] != trial["known_scalar"]:
                    raise AssertionError("rho recovered wrong scalar")
                rho_trials.append(trial)

            instances.append(
                {
                    "seed_index": seed_index,
                    "seed": seed,
                    "curve": curve,
                    "factor_base_size": size,
                    "targets": targets,
                    "null_distributions": {
                        family: distribution_summary(rows)
                        for family, rows in null_rows.items()
                    },
                    "null_rows": null_rows,
                    "candidate_rows": candidates,
                    "scalar_progression_control": control,
                    "rho": {
                        "trials": rho_trials,
                        "median_group_operations": statistics.median(
                            row["ops"]["group_operations"] for row in rho_trials
                        ),
                        "analytic_sqrt_q": math.sqrt(q),
                    },
                }
            )

    all_curves_clean = all(
        instance["curve"]["trace"] not in (0, 1)
        and instance["curve"]["j_invariant"]
        not in (0, 1728 % instance["curve"]["p"])
        and instance["curve"]["q"] == instance["curve"]["order"]
        for instance in instances
    )
    all_positive_controls_passed = all(
        instance["scalar_progression_control"]["positive_control_passed"]
        for instance in instances
    )
    all_rho_trials_verified = all(
        trial["verified"]
        for instance in instances
        for trial in instance["rho"]["trials"]
    )
    all_order_controls_passed = all(
        row["order_control_passed"]
        for instance in instances
        for row in [
            *instance["null_rows"]["random"],
            *instance["null_rows"]["random_x"],
            *instance["candidate_rows"],
            instance["scalar_progression_control"],
        ]
    )
    controls_passed = (
        all_curves_clean
        and all_positive_controls_passed
        and all_rho_trials_verified
        and all_order_controls_passed
        and len(used_field_moduli) == len(instances)
    )
    family_gate = aggregate_family_gate(
        instances,
        CANDIDATE_FAMILIES,
        config["bit_sizes"],
        config["seeds"],
        controls_passed,
    )
    return {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "valid": controls_passed,
        "source": {
            key: EXPECTED_HASHES[key]
            for key in (
                "null_calibrated_coverage_sha256",
                "recursive_expansion_sha256",
                "coordinate_energy_sha256",
            )
        },
        "config": copy.deepcopy(config),
        "instances": instances,
        "summary": {
            "instances_completed": len(instances),
            "distinct_field_moduli": len(used_field_moduli),
            "globally_unique_factor_base_seeds": len(used_base_seeds),
            "all_curves_clean": all_curves_clean,
            "all_positive_controls_passed": all_positive_controls_passed,
            "all_rho_trials_verified": all_rho_trials_verified,
            "all_order_controls_passed": all_order_controls_passed,
            **family_gate,
            "preflight_gate_passed": bool(family_gate["promoted_families"]),
            "split_compression_claim": False,
            "breakthrough_claim": False,
            "boundary": "An exploratory finite-null pass on at least six of nine distinct-field toy curves only; rank, descent, exponent, family-wise inference, and deployment remain untested.",
        },
    }


def verify_document(document: Any, enforce_frozen: bool = True) -> dict[str, Any]:
    if type(document) is not dict or document.get("protocol") != PROTOCOL:
        raise AssertionError("unexpected top-level document or protocol")
    hashes = verify_source_hashes()
    config = validate_config(document.get("config"), enforce_frozen)
    expected = reconstruct_document(config)
    scheduled_base_count = len(expected["instances"]) * (
        len(NULL_FAMILIES) * config["null_replicates_per_family"]
        + len(CANDIDATE_FAMILIES)
        + 1
    )
    if expected["summary"]["globally_unique_factor_base_seeds"] != scheduled_base_count:
        raise AssertionError("global factor-base seed accounting is incomplete")
    if enforce_frozen:
        if len(expected["instances"]) != 9:
            raise AssertionError("frozen protocol requires exactly nine instances")
        if expected["summary"]["distinct_field_moduli"] != 9:
            raise AssertionError("frozen protocol requires nine distinct field primes")
    assert_exact(document, expected)
    return {
        "valid": expected["valid"],
        "protocol": VERIFIER_PROTOCOL,
        "source": hashes,
        "summary": {
            "instances_verified": len(expected["instances"]),
            "distinct_field_moduli_verified": expected["summary"][
                "distinct_field_moduli"
            ],
            "globally_unique_factor_base_seeds_verified": expected["summary"][
                "globally_unique_factor_base_seeds"
            ],
            "exact_integer_types_verified": True,
            "curve_orders_recomputed": True,
            "clean_curve_rejections_replayed": True,
            "targets_factor_bases_and_nulls_replayed": True,
            "four_and_eight_term_supports_orders_witnesses_percentiles_and_family_gate_replayed": True,
            "exact_first_hit_expectations_and_per_order_vectors_replayed": True,
            "charged_coordinate_costs_and_all_offline_ratios_replayed": True,
            "raw_percentile_rank_and_tie_details_replayed": True,
            "operation_counters_memory_bytes_and_rho_replayed": True,
            "all_mandatory_controls_passed": (
                expected["summary"]["all_curves_clean"]
                and expected["summary"]["all_positive_controls_passed"]
                and expected["summary"]["all_rho_trials_verified"]
                and expected["summary"]["all_order_controls_passed"]
            ),
            "family_aggregation_control_block_replayed": True,
            "preflight_gate_passed": expected["summary"]["preflight_gate_passed"],
            "breakthrough_claim": False,
            "frozen_config_enforced": enforce_frozen,
            "boundary": (
                "Independent arithmetic verification of frozen v2 toy evidence only."
                if enforce_frozen
                else "Independent arithmetic verification of a reduced v2 toy test configuration only."
            ),
        },
    }


def duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_values(value: Any, path: str = "document") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"non-finite JSON number at {path}")
    if isinstance(value, dict):
        for key, item in value.items():
            reject_nonfinite_values(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_nonfinite_values(item, f"{path}[{index}]")


def parse_json(raw: bytes) -> Any:
    value = json.loads(
        raw,
        object_pairs_hook=duplicate_rejecting_object,
        parse_constant=lambda token: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {token}")
        ),
    )
    reject_nonfinite_values(value)
    return value


def expect_rejection(document: dict[str, Any], label: str) -> str:
    try:
        verify_document(document, enforce_frozen=False)
    except (AssertionError, ValueError, TypeError, OverflowError) as error:
        return f"{label}:{type(error).__name__}"
    raise AssertionError(f"mutation {label!r} was accepted")


def expect_rejection_group(
    mutations: list[tuple[str, dict[str, Any]]], label: str
) -> tuple[str, int]:
    for mutation_label, document in mutations:
        expect_rejection(document, f"{label}.{mutation_label}")
    return f"{label}:{len(mutations)}", len(mutations)


def run_self_test() -> dict[str, Any]:
    hashes = verify_source_hashes()
    for source_name in tuple(EXPECTED_HASHES):
        original_hash = EXPECTED_HASHES[source_name]
        EXPECTED_HASHES[source_name] = "0" * 64
        try:
            verify_source_hashes()
        except AssertionError:
            pass
        else:
            raise AssertionError(f"mutated source hash was accepted: {source_name}")
        finally:
            EXPECTED_HASHES[source_name] = original_hash
    tiny = {
        **copy.deepcopy(FROZEN_CONFIG),
        "bit_sizes": [10],
        "seeds": [73],
        "null_replicates_per_family": 2,
        "target_count": 8,
        "order_seeds": [11, 13],
        "occupancy_lambda": 0.2,
        "rho_trials": 1,
    }
    fixture = reconstruct_document(tiny)
    verification = verify_document(fixture, enforce_frozen=False)
    if not fixture["valid"] or not verification["valid"]:
        raise AssertionError("tiny v2 control fixture must be valid")
    checks = ["tiny_round_trip_exact", "all_four_source_hashes_enforced"]
    mutation_cases = 0

    frozen_moduli: list[int] = []
    for seed in FROZEN_CONFIG["seeds"]:
        previous_q = 0
        for bits in FROZEN_CONFIG["bit_sizes"]:
            curve = reconstruct_clean_curve(bits, seed + bits * 1009)
            if curve["q"] <= previous_q:
                raise AssertionError("frozen curve orders are not monotone by seed")
            previous_q = curve["q"]
            frozen_moduli.append(curve["p"])
    if len(frozen_moduli) != 9 or len(set(frozen_moduli)) != 9:
        raise AssertionError("frozen schedule does not have nine distinct fields")

    frozen_base_seeds: list[int] = []
    for seed in FROZEN_CONFIG["seeds"]:
        for bits in FROZEN_CONFIG["bit_sizes"]:
            for family_index in range(len(NULL_FAMILIES)):
                for replicate in range(FROZEN_CONFIG["null_replicates_per_family"]):
                    frozen_base_seeds.append(
                        seed
                        ^ (bits << 20)
                        ^ (family_index * 0x9E3779B1)
                        ^ (replicate * 0x85EBCA6B)
                    )
            for family_index in range(len(CANDIDATE_FAMILIES)):
                frozen_base_seeds.append(
                    seed
                    ^ (bits << 20)
                    ^ 0xC2B2AE35
                    ^ (family_index * 0x27D4EB2F)
                )
            frozen_base_seeds.append(seed ^ (bits << 20) ^ 0x165667B1)
    if len(frozen_base_seeds) != 594 or len(set(frozen_base_seeds)) != 594:
        raise AssertionError("frozen factor-base seeds are not globally unique")
    checks.append(
        "frozen_nine_distinct_fields_and_global_factor_base_seed_schedule_unique"
    )

    instance = fixture["instances"][0]
    candidate = instance["candidate_rows"][0]
    candidate_name = candidate["name"]

    curve_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["curve"]["trace"] = 1
    curve_mutations.append(("anomalous_trace", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["curve"]["j_invariant"] = 0
    curve_mutations.append(("special_j", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["curve"]["rejections"]["composite_order"] += 1
    curve_mutations.append(("rejection_count", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["curve"]["curve_attempts"] += 1
    curve_mutations.append(("selection_attempt", changed))
    label, count = expect_rejection_group(
        curve_mutations, "curve_selection_and_rejection_mutations"
    )
    checks.append(label)
    mutation_cases += count

    support_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["null_rows"]["random"][0][
        "four_term_support_size"
    ] += 1
    support_mutations.append(("four_term_support", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["null_rows"]["random"][0][
        "eight_term_support_size"
    ] += 1
    support_mutations.append(("eight_term_support", changed))
    witness_row = next(
        row
        for row in instance["candidate_rows"]
        if row["first_witness"] is not None
    )
    changed = copy.deepcopy(fixture)
    next(
        row
        for row in changed["instances"][0]["candidate_rows"]
        if row["name"] == witness_row["name"]
    )["first_witness"]["target_index"] += 1
    support_mutations.append(("first_witness", changed))
    label, count = expect_rejection_group(
        support_mutations, "exact_four_eight_support_and_witness_mutations"
    )
    checks.append(label)
    mutation_cases += count

    order_mutations: list[tuple[str, dict[str, Any]]] = []
    for field in (
        "successful_partials",
        "expected_first_hit_numerator",
        "expected_first_hit_denominator",
    ):
        changed = copy.deepcopy(fixture)
        changed["instances"][0]["candidate_rows"][0][
            "target_order_expectations"
        ][0][field] += 1
        order_mutations.append((field, changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0][
        "target_order_expectations"
    ][0]["expected_first_hit_lookups"] += 0.5
    order_mutations.append(("expected_first_hit_lookups", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0][
        "exact_uniform_average_first_hit_lookups_per_target"
    ] += 0.5
    order_mutations.append(("exact_uniform_average", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["order_results"][0][
        "per_target_lookups"
    ][0] += 1
    order_mutations.append(("per_target_lookups", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["order_results"][0][
        "per_target_group_operations"
    ][0] += 1
    order_mutations.append(("per_target_group_operations", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["order_results"][0][
        "relative_error_to_exact_uniform_expectation"
    ] += 0.1
    order_mutations.append(("sampled_expectation_error", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["order_variation_ratio"] += 0.1
    order_mutations.append(("order_variation_ratio", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0][
        "maximum_sampled_expectation_relative_error"
    ] += 0.1
    order_mutations.append(("maximum_sampled_expectation_error", changed))
    label, count = expect_rejection_group(
        order_mutations, "exact_order_expectation_and_vectors_mutations"
    )
    checks.append(label)
    mutation_cases += count

    cost_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["build_diagnostics"][
        "charged_pow_field_multiplications"
    ] += 1
    cost_mutations.append(("binary_pow_proxy", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["build_diagnostics"][
        "coordinate_rhs_field_multiplications"
    ] += 1
    cost_mutations.append(("coordinate_rhs", changed))
    changed = copy.deepcopy(fixture)
    next(
        row
        for row in changed["instances"][0]["candidate_rows"]
        if row["name"] == "square_map"
    )["build_diagnostics"]["map_field_multiplications"] += 1
    cost_mutations.append(("map_multiplications", changed))
    changed = copy.deepcopy(fixture)
    next(
        row
        for row in changed["instances"][0]["candidate_rows"]
        if row["name"] == "rational_union"
    )["build_diagnostics"]["map_field_inversions"] += 1
    cost_mutations.append(("map_inversions", changed))
    for metric in (
        "group_operations",
        "charged_field_multiplications",
        "charged_field_inversions",
    ):
        changed = copy.deepcopy(fixture)
        changed["instances"][0]["candidate_rows"][0]["offline_charged_cost"][
            metric
        ] += 1
        cost_mutations.append((f"offline_charged_{metric}", changed))
    for metric in (
        "group_operations",
        "charged_field_multiplications",
        "charged_field_inversions",
    ):
        changed = copy.deepcopy(fixture)
        changed["instances"][0]["candidate_rows"][0][
            "offline_cost_ratios_to_random_x_median"
        ][metric] += 0.25
        cost_mutations.append((f"offline_ratio_{metric}", changed))
    label, count = expect_rejection_group(
        cost_mutations, "charged_cost_accounting_and_ratios_mutations"
    )
    checks.append(label)
    mutation_cases += count

    rank_mutations: list[tuple[str, dict[str, Any]]] = []
    for field, delta in (
        ("favorable_null_count", 1),
        ("tied_null_count", 1),
        ("null_count", 1),
        ("finite_null_denominator", 1),
        ("percentile", 0.1),
    ):
        changed = copy.deepcopy(fixture)
        changed["instances"][0]["candidate_rows"][0]["null_rank_details"][
            "random"
        ]["coverage_efficiency"][field] += delta
        rank_mutations.append((field, changed))
    changed = copy.deepcopy(fixture)
    detail = changed["instances"][0]["candidate_rows"][0][
        "null_rank_details"
    ]["random"]["coverage_efficiency"]
    detail["higher_is_better"] = not detail["higher_is_better"]
    rank_mutations.append(("higher_is_better", changed))
    label, count = expect_rejection_group(
        rank_mutations, "percentile_rank_and_tie_mutations"
    )
    checks.append(label)
    mutation_cases += count

    control_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    control = changed["instances"][0]["scalar_progression_control"]
    control["positive_control_passed"] = not control["positive_control_passed"]
    control_mutations.append(("positive_control", changed))
    changed = copy.deepcopy(fixture)
    row = changed["instances"][0]["candidate_rows"][0]
    row["order_control_passed"] = not row["order_control_passed"]
    control_mutations.append(("order_control", changed))
    changed = copy.deepcopy(fixture)
    rho = changed["instances"][0]["rho"]["trials"][0]
    rho["verified"] = not rho["verified"]
    control_mutations.append(("rho_control", changed))
    for field in (
        "all_curves_clean",
        "all_positive_controls_passed",
        "all_rho_trials_verified",
        "all_order_controls_passed",
        "preflight_gate_passed",
    ):
        changed = copy.deepcopy(fixture)
        changed["summary"][field] = not changed["summary"][field]
        control_mutations.append((field, changed))
    changed = copy.deepcopy(fixture)
    changed["valid"] = not changed["valid"]
    control_mutations.append(("document_valid", changed))
    changed = copy.deepcopy(fixture)
    changed["summary"]["promoted_families"] = (
        []
        if changed["summary"]["promoted_families"]
        else [candidate_name]
    )
    control_mutations.append(("promoted_families", changed))

    synthetic_instances = [
        {
            "seed": seed,
            "curve": {"bits": bits},
            "candidate_rows": [
                {"name": family, "instance_gate_passed": family == candidate_name}
                for family in CANDIDATE_FAMILIES
            ],
        }
        for seed in FROZEN_CONFIG["seeds"]
        for bits in FROZEN_CONFIG["bit_sizes"]
    ]
    blocked = aggregate_family_gate(
        synthetic_instances,
        CANDIDATE_FAMILIES,
        FROZEN_CONFIG["bit_sizes"],
        FROZEN_CONFIG["seeds"],
        False,
    )
    allowed = aggregate_family_gate(
        synthetic_instances,
        CANDIDATE_FAMILIES,
        FROZEN_CONFIG["bit_sizes"],
        FROZEN_CONFIG["seeds"],
        True,
    )
    if blocked["promoted_families"] or allowed["promoted_families"] != [
        candidate_name
    ]:
        raise AssertionError("mandatory controls do not block family aggregation")
    label, count = expect_rejection_group(
        control_mutations, "mandatory_controls_and_promotion_mutations"
    )
    checks.append(label)
    mutation_cases += count

    source_mutations: list[tuple[str, dict[str, Any]]] = []
    for field in (
        "null_calibrated_coverage_sha256",
        "recursive_expansion_sha256",
        "coordinate_energy_sha256",
    ):
        changed = copy.deepcopy(fixture)
        changed["source"][field] = "0" * 64
        source_mutations.append((field, changed))
    label, count = expect_rejection_group(
        source_mutations, "source_hash_mutations"
    )
    checks.append(label)
    mutation_cases += count

    identity_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    changed["summary"]["distinct_field_moduli"] += 1
    identity_mutations.append(("distinct_field_moduli", changed))
    changed = copy.deepcopy(fixture)
    changed["summary"]["globally_unique_factor_base_seeds"] += 1
    identity_mutations.append(("globally_unique_factor_base_seeds", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["candidate_rows"][0]["seed"] = changed[
        "instances"
    ][0]["null_rows"]["random"][0]["seed"]
    identity_mutations.append(("duplicate_factor_base_seed", changed))
    label, count = expect_rejection_group(
        identity_mutations, "distinct_fields_and_global_seed_mutations"
    )
    checks.append(label)
    mutation_cases += count

    type_mutations: list[tuple[str, dict[str, Any]]] = []
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["targets"][0]["scalar"] = True
    type_mutations.append(("bool_for_exact_int", changed))
    changed = copy.deepcopy(fixture)
    changed["instances"][0]["factor_base_size"] = float(
        changed["instances"][0]["factor_base_size"]
    )
    type_mutations.append(("float_for_exact_int", changed))
    label, count = expect_rejection_group(type_mutations, "exact_type_mutations")
    checks.append(label)
    mutation_cases += count

    try:
        parse_json(b'{"x":1,"x":2}')
    except ValueError:
        checks.append("duplicate_json_key_rejected")
    else:
        raise AssertionError("duplicate_json_key_rejected failed")
    for raw in (b'{"x":NaN}', b'{"x":1e999}'):
        try:
            parse_json(raw)
        except ValueError:
            continue
        else:
            raise AssertionError("nonfinite_json_rejected failed")
    checks.append("nonfinite_json_rejected")

    encoded = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
    return {
        "valid": True,
        "protocol": f"{VERIFIER_PROTOCOL}-selftest",
        "source": hashes,
        "tests": checks,
        "mutation_cases_executed": mutation_cases,
        "frozen_schedule": {
            "instances": 9,
            "distinct_field_moduli": len(set(frozen_moduli)),
            "globally_unique_factor_base_seeds": len(set(frozen_base_seeds)),
        },
        "tiny_fixture": {
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "bytes": len(encoded),
            "instances": 1,
        },
        "experiment_harness_executed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("--allow-nonfrozen-test-config", action="store_true", help="clearly labelled reduced test configuration only")
    args = parser.parse_args()
    raw: bytes | None = None
    try:
        if args.self_test:
            if args.allow_nonfrozen_test_config:
                raise ValueError("--allow-nonfrozen-test-config is only valid with --input")
            print(json.dumps(run_self_test(), sort_keys=True, separators=(",", ":")))
            return 0
        raw = args.input.read_bytes()
        if len(raw) > 64 * 1024 * 1024:
            raise ValueError("input exceeds 64 MiB verifier limit")
        result = verify_document(parse_json(raw), enforce_frozen=not args.allow_nonfrozen_test_config)
        result["input"] = {"path": str(args.input), "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        print(json.dumps(result, sort_keys=True, separators=(",", ":")))
        return 0
    except (AssertionError, ValueError, TypeError, OverflowError, OSError) as error:
        failure: dict[str, Any] = {"valid": False, "protocol": VERIFIER_PROTOCOL, "error_type": type(error).__name__, "error": str(error)}
        if raw is not None:
            failure["input"] = {"sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
        print(json.dumps(failure, sort_keys=True, separators=(",", ":")))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
