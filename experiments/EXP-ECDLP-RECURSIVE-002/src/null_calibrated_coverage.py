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
        trace = p + 1 - order
        if trace == 0:
            rejections["trace_zero"] += 1
            continue
        if trace == 1:
            rejections["anomalous_trace_one"] += 1
            continue
        if not ENERGY.is_prime(order):
            rejections["composite_order"] += 1
            continue
        j_value = j_invariant(p, a, b)
        if j_value in (0, 1728 % p):
            rejections["special_j"] += 1
            continue

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
    order_results: list[dict[str, Any]] = []
    first_witness: dict[str, Any] | None = None
    for order_index, order_seed in enumerate(order_seeds):
        ordered_items = list(canonical_items)
        random.Random(order_seed ^ factor_base["seed"]).shuffle(ordered_items)
        ops = Ops()
        lookups = 0
        per_target_ops: list[int] = []
        successes = 0
        for target_index, target_record in enumerate(targets):
            target = PRIOR.point_from_json(target_record["point"])
            before = ops.group_operations
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
        order_results.append(
            {
                "order_seed": order_seed,
                "sampled_successful_targets": successes,
                "online_group_operations": ops.group_operations,
                "online_lookups": lookups,
                "average_online_group_operations_per_target": statistics.fmean(
                    per_target_ops
                ),
                "median_online_group_operations_per_target": statistics.median(
                    per_target_ops
                ),
                "maximum_online_group_operations_per_target": max(per_target_ops),
            }
        )

    order_averages = [
        result["average_online_group_operations_per_target"]
        for result in order_results
    ]
    robust_online = statistics.median(order_averages)
    order_variation = max(order_averages) / min(order_averages)
    frontier_score = (
        compiled_artifact_bytes * robust_online**2 / (exact_epsilon * q)
    )
    offline_ops = {
        key: factor_base["build_ops"][key] + asdict(compiler_ops)[key]
        for key in asdict(compiler_ops)
    }
    return {
        "name": factor_base["name"],
        "seed": factor_base["seed"],
        "size": factor_base["size"],
        "factor_base_digest": stable_digest(factor_base),
        "build_ops": factor_base["build_ops"],
        "build_diagnostics": factor_base["build_diagnostics"],
        "compiler_ops": asdict(compiler_ops),
        "diagnostic_expansion_ops": asdict(expansion_ops),
        "offline_ops": offline_ops,
        "four_term_support_size": advice_entries,
        "generic_signed_four_term_maximum": signed_class_count(len(points) // 2, 4),
        "eight_term_support_size": len(exact_support),
        "exact_success_probability": exact_epsilon,
        "coverage_efficiency": len(exact_support) / (advice_entries**2),
        "advice_entries": advice_entries,
        "advice_map_deep_bytes": advice_map_bytes,
        "factor_base_deep_bytes": factor_base_bytes,
        "compiled_artifact_deep_bytes": compiled_artifact_bytes,
        "order_results": order_results,
        "order_robust_online_group_operations_per_target": robust_online,
        "order_variation_ratio": order_variation,
        "functional_frontier_score": frontier_score,
        "estimated_lookup_traffic_bytes": int(
            statistics.median(result["online_lookups"] for result in order_results)
            * 64
        ),
        "first_witness": first_witness,
    }


def empirical_percentile(
    value: float, distribution: list[float], higher_is_better: bool
) -> float:
    if not distribution:
        raise ValueError("empty null distribution")
    if higher_is_better:
        favorable = sum(item < value for item in distribution)
    else:
        favorable = sum(item > value for item in distribution)
    tied = sum(item == value for item in distribution)
    return (1 + favorable + 0.5 * tied) / (len(distribution) + 1)


def distribution_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {
        "eight_term_support_size": True,
        "coverage_efficiency": True,
        "functional_frontier_score": False,
        "four_term_support_size": True,
        "offline_group_operations": False,
    }
    summary: dict[str, Any] = {"replicates": len(rows)}
    for metric in metrics:
        values = [
            row["offline_ops"]["group_operations"]
            if metric == "offline_group_operations"
            else row[metric]
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
    for null_name, rows in null_rows.items():
        candidate["null_percentiles"][null_name] = {
            "eight_term_support": empirical_percentile(
                candidate["eight_term_support_size"],
                [row["eight_term_support_size"] for row in rows],
                True,
            ),
            "coverage_efficiency": empirical_percentile(
                candidate["coverage_efficiency"],
                [row["coverage_efficiency"] for row in rows],
                True,
            ),
            "functional_frontier": empirical_percentile(
                candidate["functional_frontier_score"],
                [row["functional_frontier_score"] for row in rows],
                False,
            ),
        }
    random_x_offline = statistics.median(
        row["offline_ops"]["group_operations"] for row in null_rows["random_x"]
    )
    candidate["offline_group_operations_ratio_to_random_x_median"] = (
        candidate["offline_ops"]["group_operations"] / random_x_offline
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
        and candidate["order_variation_ratio"] <= 1.25
        and candidate["offline_group_operations_ratio_to_random_x_median"] <= 4.0
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
    return result


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
    for seed_index, seed in enumerate(seeds):
        previous_q = 0
        for bits in bit_sizes:
            selection_seed = seed + bits * 1009
            curve_record = generate_clean_curve(bits, selection_seed)
            q = curve_record["q"]
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
            used_base_seeds: set[int] = set()

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
    promoted = sorted(
        family
        for family in candidate_families
        if family_counts[family] >= 6
        and family_sizes[family] == set(bit_sizes)
        and family_seeds[family] == set(seeds)
    )
    return {
        "protocol": "EXP-ECDLP-RECURSIVE-002-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"],
        "valid": True,
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
            "all_curves_clean": all(
                instance["curve"]["trace"] not in (0, 1)
                and instance["curve"]["j_invariant"]
                not in (0, 1728 % instance["curve"]["p"])
                and instance["curve"]["q"] == instance["curve"]["order"]
                for instance in instances
            ),
            "all_positive_controls_passed": all(
                instance["scalar_progression_control"]["positive_control_passed"]
                for instance in instances
            ),
            "all_rho_trials_verified": all(
                trial["verified"]
                for instance in instances
                for trial in instance["rho"]["trials"]
            ),
            "family_pass_counts": family_counts,
            "family_pass_sizes": {
                family: sorted(values) for family, values in family_sizes.items()
            },
            "family_pass_seeds": {
                family: sorted(values) for family, values in family_seeds.items()
            },
            "promoted_families": promoted,
            "preflight_gate_passed": bool(promoted),
            "split_compression_claim": False,
            "breakthrough_claim": False,
            "boundary": "A promotion is a replicated toy additive-geometry signal only; rank, descent, exponent, and deployment remain untested.",
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
