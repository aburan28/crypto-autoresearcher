#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()
PRIOR_SOURCE_PATH = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)
ENERGY_SOURCE_PATH = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-ENERGY-001"
    / "src"
    / "coordinate_energy.py"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


SOURCE_HASHES = {
    "null_calibrated_coverage_sha256": sha256_file(SCRIPT_PATH),
    "recursive_expansion_sha256": sha256_file(PRIOR_SOURCE_PATH),
    "coordinate_energy_sha256": sha256_file(ENERGY_SOURCE_PATH),
}


def load_prior_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "recursive_expansion_v2", PRIOR_SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite module: {PRIOR_SOURCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRIOR = load_prior_module()
ENERGY = PRIOR.ENERGY
Curve = PRIOR.Curve
Ops = PRIOR.Ops


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def stable_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def j_invariant(p: int, a: int, b: int) -> int:
    four_a3 = 4 * pow(a, 3, p) % p
    denominator = (four_a3 + 27 * pow(b, 2, p)) % p
    if denominator == 0:
        raise ValueError("singular curve has no j-invariant")
    return 1728 * four_a3 * pow(denominator, -1, p) % p


def curve_rejection_reason(p: int, a: int, b: int, order: int) -> str | None:
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        return "singular"
    trace = p + 1 - order
    if trace == 0:
        return "trace_zero"
    if trace == 1:
        return "anomalous_trace_one"
    if not ENERGY.is_prime(order):
        return "composite_order"
    if j_invariant(p, a, b) in (0, 1728 % p):
        return "special_j"
    return None


def generate_clean_curve(
    bits: int, seed: int, max_attempts: int = 256
) -> dict[str, Any]:
    p = ENERGY.find_field_prime(bits, seed ^ 0x6A09E667)
    rng = random.Random((seed << 17) ^ bits ^ 0x510E527F)
    rejections = {
        "singular": 0,
        "trace_zero": 0,
        "anomalous_trace_one": 0,
        "composite_order": 0,
        "special_j": 0,
    }
    counted_orders = 0
    for attempt in range(1, max_attempts + 1):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            rejections["singular"] += 1
            continue
        curve = Curve(p, a, b)
        counted_orders += 1
        order = ENERGY.curve_order(curve)
        rejection = curve_rejection_reason(p, a, b, order)
        if rejection is not None:
            rejections[rejection] += 1
            continue
        trace = p + 1 - order
        j_value = j_invariant(p, a, b)

        generator_ops = Ops()
        start = rng.randrange(p)
        generator: Point = None
        generator_source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = ENERGY.square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = (x, y)
            if curve.mul(order, candidate, generator_ops) is None:
                generator = candidate
                generator_source_x = x
                break
        if generator is None:
            continue
        return {
            "id": f"nullcal-toy-p{p}-a{a}-b{b}-q{order}",
            "bits": bits,
            "p": p,
            "p_mod_4": p % 4,
            "field_modulus_policy": "seeded bits-bit prime constrained to p mod 4 = 3",
            "a": a,
            "b": b,
            "j_invariant": j_value,
            "order": order,
            "trace": trace,
            "q": order,
            "cofactor": 1,
            "generator": list(generator),
            "generator_source_x": generator_source_x,
            "curve_attempts": attempt,
            "order_count_legendre_tests": counted_orders * p,
            "generator_ops": asdict(generator_ops),
            "p_minus_1_factors": ENERGY.prime_factors(p - 1),
            "rejections": rejections,
            "selection_policy": "first seeded nonsingular prime-order curve with trace not 0 or 1 and j not 0 or 1728",
        }
    raise RuntimeError(f"clean prime-order curve search exhausted at {bits} bits")


def signed_class_count(fiber_count: int, terms: int) -> int:
    total = 0
    for residue_terms in range(terms % 2, terms + 1, 2):
        if residue_terms == 0:
            total += 1
            continue
        for support_size in range(1, min(fiber_count, residue_terms) + 1):
            total += (
                math.comb(fiber_count, support_size)
                * math.comb(residue_terms - 1, support_size - 1)
                * 2**support_size
            )
    return total


def point_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


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


def compile_base(
    curve: Any,
    q: int,
    factor_base: dict[str, Any],
    targets: list[dict[str, Any]],
    order_seeds: list[int],
) -> dict[str, Any]:
    points = [PRIOR.point_from_json(point) for point in factor_base["points"]]
    compiler_chain, compiler_ops = PRIOR.support_chain(curve, points, 4)
    expansion_chain, expansion_ops = PRIOR.support_chain(curve, points, 8)
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
    exact_order_control_ops = Ops()
    target_order_expectations: list[dict[str, Any]] = []
    for target_index, target_record in enumerate(targets):
        target = PRIOR.point_from_json(target_record["point"])
        successful_partials = 0
        for partial, _ in canonical_items:
            complement = curve.add(
                target, curve.neg(partial), exact_order_control_ops
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
        ops = Ops()
        lookups = 0
        per_target_ops: list[int] = []
        per_target_lookups: list[int] = []
        successes = 0
        for target_index, target_record in enumerate(targets):
            target = PRIOR.point_from_json(target_record["point"])
            before = ops.group_operations
            before_lookups = lookups
            found: tuple[int, ...] | None = None
            for partial, partial_witness in ordered_items:
                complement = curve.add(target, curve.neg(partial), ops)
                lookups += 1
                other_witness = advice_map.get(complement)
                if other_witness is None:
                    continue
                found = partial_witness + other_witness
                break
            per_target_ops.append(ops.group_operations - before)
            per_target_lookups.append(lookups - before_lookups)
            exact_membership = target in exact_support
            if (found is not None) != exact_membership:
                raise AssertionError("shuffled split scan disagrees with exact support")
            if found is not None:
                successes += 1
                if not PRIOR.verify_witness(curve, points, found, target):
                    raise AssertionError("shuffled split witness failed arithmetic")
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
        result["average_online_group_operations_per_target"]
        for result in order_results
    ]
    sampled_median_online = statistics.median(order_averages)
    order_variation = max(order_averages) / min(order_averages)
    sampled_expectation_error = max(
        row["relative_error_to_exact_uniform_expectation"]
        for row in order_results
    )
    order_control_passed = (
        order_variation <= 1.25 and sampled_expectation_error <= 0.25
    )
    frontier_score = (
        compiled_artifact_bytes * exact_uniform_average**2 / (exact_epsilon * q)
    )
    offline_ops = {
        key: factor_base["build_ops"][key] + asdict(compiler_ops)[key]
        for key in asdict(compiler_ops)
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
        result["online_lookups"] for result in order_results
    )
    return {
        "name": factor_base["name"],
        "seed": factor_base["seed"],
        "size": factor_base["size"],
        "factor_base_digest": stable_digest(factor_base),
        "build_ops": factor_base["build_ops"],
        "build_diagnostics": build_diagnostics,
        "compiler_ops": asdict(compiler_ops),
        "diagnostic_expansion_ops": asdict(expansion_ops),
        "offline_ops": offline_ops,
        "offline_charged_cost": offline_charged_cost,
        "four_term_support_size": advice_entries,
        "generic_signed_four_term_maximum": signed_class_count(len(points) // 2, 4),
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
        raise ValueError("empty null distribution")
    if higher_is_better:
        favorable = sum(item < value for item in distribution)
    else:
        favorable = sum(item > value for item in distribution)
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
    metrics = {
        "eight_term_support_size": True,
        "coverage_efficiency": True,
        "functional_frontier_score": False,
        "four_term_support_size": True,
        "offline_group_operations": False,
        "offline_charged_field_multiplications": False,
        "offline_charged_field_inversions": False,
    }
    summary: dict[str, Any] = {"replicates": len(rows)}
    for metric in metrics:
        values = [
            (
                row["offline_ops"]["group_operations"]
                if metric == "offline_group_operations"
                else row["offline_charged_cost"][
                    metric.removeprefix("offline_")
                ]
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
    candidate: dict[str, Any],
    null_rows: dict[str, list[dict[str, Any]]],
) -> None:
    candidate["null_percentiles"] = {}
    candidate["null_rank_details"] = {}
    for null_name, rows in null_rows.items():
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
        candidate["null_rank_details"][null_name] = rank_details
        candidate["null_percentiles"][null_name] = {
            metric: detail["percentile"]
            for metric, detail in rank_details.items()
        }
    candidate["offline_cost_ratios_to_random_x_median"] = {}
    for metric in (
        "group_operations",
        "charged_field_multiplications",
        "charged_field_inversions",
    ):
        candidate_value = candidate["offline_charged_cost"][metric]
        random_x_median = statistics.median(
            row["offline_charged_cost"][metric]
            for row in null_rows["random_x"]
        )
        candidate["offline_cost_ratios_to_random_x_median"][metric] = (
            candidate_value / random_x_median if random_x_median else 1.0
        )
    candidate["split_support_ratio_to_random_medians"] = {
        null_name: candidate["four_term_support_size"]
        / statistics.median(row["four_term_support_size"] for row in rows)
        for null_name, rows in null_rows.items()
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


def make_base(
    family: str,
    curve: Any,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    result = PRIOR.make_factor_base(
        family, "sign_complete", curve, q, generator, size, seed
    )
    result["seed"] = seed
    result["build_diagnostics"] = charged_build_diagnostics(result, curve.p)
    return result


def aggregate_family_gate(
    instances: list[dict[str, Any]],
    candidate_families: list[str],
    bit_sizes: list[int],
    seeds: list[int],
    controls_passed: bool,
) -> dict[str, Any]:
    family_counts: dict[str, int] = {family: 0 for family in candidate_families}
    family_sizes: dict[str, set[int]] = {family: set() for family in candidate_families}
    family_seeds: dict[str, set[int]] = {family: set() for family in candidate_families}
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


def run_experiment(
    bit_sizes: list[int],
    seeds: list[int],
    null_replicates: int,
    target_count: int,
    order_seeds: list[int],
    occupancy_lambda: float,
    rho_trials: int,
) -> dict[str, Any]:
    for index, bits in enumerate(bit_sizes):
        exact_int(bits, f"bit_sizes[{index}]", 8)
    for index, seed in enumerate(seeds):
        exact_int(seed, f"seeds[{index}]")
    if len(set(bit_sizes)) != len(bit_sizes) or len(set(seeds)) != len(seeds):
        raise ValueError("bit sizes and seeds must be distinct")
    exact_int(null_replicates, "null_replicates", 2)
    exact_int(target_count, "target_count", 1)
    exact_int(rho_trials, "rho_trials", 1)
    for index, order_seed in enumerate(order_seeds):
        exact_int(order_seed, f"order_seeds[{index}]")
    if len(set(order_seeds)) != len(order_seeds):
        raise ValueError("order seeds must be distinct")
    if type(occupancy_lambda) not in (int, float) or isinstance(
        occupancy_lambda, bool
    ):
        raise ValueError("occupancy_lambda must be numeric")
    if occupancy_lambda <= 0:
        raise ValueError("occupancy_lambda must be positive")

    candidate_families = ["x_interval", "square_map", "rational_union"]
    null_families = ["random", "random_x"]
    instances: list[dict[str, Any]] = []
    used_field_moduli: set[int] = set()
    used_base_seeds: set[int] = set()
    for seed_index, seed in enumerate(seeds):
        previous_q = 0
        for bits in bit_sizes:
            selection_seed = seed + bits * 1009
            curve_record = generate_clean_curve(bits, selection_seed)
            q = curve_record["q"]
            if curve_record["p"] in used_field_moduli:
                raise AssertionError("field modulus repeated across scheduled curves")
            used_field_moduli.add(curve_record["p"])
            if q <= previous_q:
                raise AssertionError("clean subgroup schedule is not strictly increasing")
            previous_q = q
            if curve_record["trace"] in (0, 1) or curve_record["j_invariant"] in (
                0,
                1728 % curve_record["p"],
            ):
                raise AssertionError("clean curve policy failed")
            curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
            generator = PRIOR.point_from_json(curve_record["generator"])
            target_rng = random.Random(seed ^ (bits << 24) ^ 0x1F83D9AB)
            if target_count > q - 1:
                raise ValueError("target count exceeds available nonzero subgroup points")
            target_scalars = target_rng.sample(range(1, q), target_count)
            targets = [
                {"scalar": scalar, "point": list(curve.mul(scalar, generator))}
                for scalar in target_scalars
            ]
            size = PRIOR.choose_factor_base_size(q, 8, occupancy_lambda)

            def claim_base_seed(value: int) -> int:
                if value in used_base_seeds:
                    raise AssertionError("factor-base seed collision")
                used_base_seeds.add(value)
                return value

            null_rows: dict[str, list[dict[str, Any]]] = {}
            for family_index, family in enumerate(null_families):
                rows = []
                for replicate in range(null_replicates):
                    base_seed = claim_base_seed(
                        seed
                        ^ (bits << 20)
                        ^ (family_index * 0x9E3779B1)
                        ^ (replicate * 0x85EBCA6B)
                    )
                    base = make_base(
                        family, curve, q, generator, size, base_seed
                    )
                    row = compile_base(curve, q, base, targets, order_seeds)
                    row["replicate"] = replicate
                    rows.append(row)
                null_rows[family] = rows

            candidate_rows = []
            for family_index, family in enumerate(candidate_families):
                base_seed = claim_base_seed(
                    seed
                    ^ (bits << 20)
                    ^ 0xC2B2AE35
                    ^ (family_index * 0x27D4EB2F)
                )
                base = make_base(family, curve, q, generator, size, base_seed)
                row = compile_base(curve, q, base, targets, order_seeds)
                attach_percentiles(row, null_rows)
                candidate_rows.append(row)

            control_seed = claim_base_seed(seed ^ (bits << 20) ^ 0x165667B1)
            control = compile_base(
                curve,
                q,
                make_base(
                    "scalar_progression_positive_control",
                    curve,
                    q,
                    generator,
                    size,
                    control_seed,
                ),
                targets,
                order_seeds,
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

            rho_results = []
            for trial_index in range(rho_trials):
                target = PRIOR.point_from_json(targets[trial_index]["point"])
                rho = ENERGY.pollard_rho(
                    curve,
                    q,
                    generator,
                    target,
                    seed ^ (bits << 12) ^ trial_index,
                )
                rho["known_scalar"] = targets[trial_index]["scalar"]
                if rho["recovered_scalar"] != targets[trial_index]["scalar"]:
                    raise AssertionError("rho recovered the wrong scalar")
                rho_results.append(rho)

            instances.append(
                {
                    "seed_index": seed_index,
                    "seed": seed,
                    "curve": curve_record,
                    "factor_base_size": size,
                    "targets": targets,
                    "null_distributions": {
                        family: distribution_summary(rows)
                        for family, rows in null_rows.items()
                    },
                    "null_rows": null_rows,
                    "candidate_rows": candidate_rows,
                    "scalar_progression_control": control,
                    "rho": {
                        "trials": rho_results,
                        "median_group_operations": statistics.median(
                            trial["ops"]["group_operations"]
                            for trial in rho_results
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
        instances, candidate_families, bit_sizes, seeds, controls_passed
    )
    return {
        "protocol": "EXP-ECDLP-RECURSIVE-002-v2",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"],
        "valid": controls_passed,
        "source": dict(SOURCE_HASHES),
        "config": {
            "bit_sizes": bit_sizes,
            "seeds": seeds,
            "candidate_families": candidate_families,
            "null_families": null_families,
            "null_replicates_per_family": null_replicates,
            "m": 8,
            "symmetry_mode": "sign_complete",
            "target_count": target_count,
            "order_seeds": order_seeds,
            "occupancy_lambda": occupancy_lambda,
            "rho_trials": rho_trials,
        },
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bit-sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--null-replicates", type=int, required=True)
    parser.add_argument("--targets", type=int, required=True)
    parser.add_argument("--order-seeds", nargs="+", type=int, required=True)
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    parser.add_argument("--rho-trials", type=int, default=2)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_experiment(
        args.bit_sizes,
        args.seeds,
        args.null_replicates,
        args.targets,
        args.order_seeds,
        args.occupancy_lambda,
        args.rho_trials,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
