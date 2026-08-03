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
    "recursive_expansion_sha256": sha256_file(SCRIPT_PATH),
    "coordinate_energy_sha256": sha256_file(ENERGY_SOURCE_PATH),
}


def load_energy_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "coordinate_energy_v1", ENERGY_SOURCE_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite module: {ENERGY_SOURCE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENERGY = load_energy_module()
Curve = ENERGY.Curve
Ops = ENERGY.Ops


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    seen = seen or set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(deep_size(key, seen) + deep_size(item, seen) for key, item in value.items())
    elif isinstance(value, (list, tuple, set, frozenset)):
        size += sum(deep_size(item, seen) for item in value)
    return size


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def generate_prime_order_curve(bits: int, seed: int, max_attempts: int = 128) -> dict[str, Any]:
    p = ENERGY.find_field_prime(bits, seed ^ 0x6A09E667)
    rng = random.Random((seed << 17) ^ bits ^ 0xBB67AE85)
    order_count_attempts = 0
    for attempt in range(1, max_attempts + 1):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            continue
        curve = Curve(p, a, b)
        order_count_attempts += 1
        order = ENERGY.curve_order(curve)
        trace = p + 1 - order
        if trace == 0 or not ENERGY.is_prime(order):
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
            "id": f"recursive-toy-p{p}-a{a}-b{b}-q{order}",
            "bits": bits,
            "p": p,
            "p_mod_4": p % 4,
            "field_modulus_policy": "seeded bits-bit prime constrained to p mod 4 = 3",
            "a": a,
            "b": b,
            "order": order,
            "trace": trace,
            "q": order,
            "cofactor": 1,
            "generator": list(generator),
            "generator_source_x": generator_source_x,
            "curve_attempts": attempt,
            "order_count_legendre_tests": order_count_attempts * p,
            "generator_ops": asdict(generator_ops),
            "p_minus_1_factors": ENERGY.prime_factors(p - 1),
            "selection_policy": "first nonsingular ordinary prime-order curve from seeded coefficients",
        }
    raise RuntimeError(f"prime-order curve search exhausted at {bits} bits")


def choose_factor_base_size(q: int, m: int, occupancy_lambda: float) -> int:
    size = 2
    while math.comb(size + m - 1, m) / q < occupancy_lambda:
        size += 2
    return size


def make_factor_base(
    family: str,
    symmetry_mode: str,
    curve: Any,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    if symmetry_mode not in ("sign_canonical", "sign_complete"):
        raise ValueError(f"unsupported symmetry mode: {symmetry_mode}")
    raw_size = size * 2 if symmetry_mode == "sign_canonical" else size
    raw = (
        make_random_x_factor_base(curve, q, raw_size, seed)
        if family == "random_x"
        else ENERGY.make_factor_base(family, curve, q, generator, raw_size, seed)
    )
    if symmetry_mode == "sign_canonical":
        points = [fiber["points"][0] for fiber in raw["fibers"]]
    else:
        points = raw["points"]
    if len(points) != size:
        raise AssertionError("factor-base cardinality mismatch")
    return {
        "name": family,
        "symmetry_mode": symmetry_mode,
        "size": size,
        "points": points,
        "fibers": raw["fibers"],
        "build_ops": raw["build_ops"],
        "build_diagnostics": raw["build_diagnostics"],
        "raw_sign_complete_size": raw_size,
    }


def make_random_x_factor_base(curve: Any, q: int, size: int, seed: int) -> dict[str, Any]:
    if size % 2 != 0:
        raise ValueError("random-x raw factor base must be sign-complete and even")
    fiber_count = size // 2
    rng = random.Random(seed)
    ops = Ops()
    diagnostics = {"x_candidates": 0, "square_root_tests": 0, "subgroup_tests": 0}
    fibers: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    for draw_index, x in enumerate(rng.sample(range(curve.p), curve.p)):
        point = ENERGY.point_for_x(curve, q, x, ops, diagnostics)
        if point is None:
            continue
        pair = ENERGY.canonical_fiber(curve, point)
        if x in seen_x:
            continue
        seen_x.add(x)
        fibers.append(
            {
                "points": [list(pair[0]), list(pair[1])],
                "source": {
                    "kind": "random_x",
                    "draw_index": draw_index,
                    "x": x,
                },
            }
        )
        if len(fibers) == fiber_count:
            break
    if len(fibers) != fiber_count:
        raise RuntimeError("random-x factor-base generation exhausted the field")
    return {
        "name": "random_x",
        "size": size,
        "fibers": fibers,
        "points": [point for fiber in fibers for point in fiber["points"]],
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
    }


def point_from_json(value: list[int] | None) -> Point:
    return None if value is None else (value[0], value[1])


def support_chain(curve: Any, points: list[Point], maximum: int) -> tuple[list[dict[Point, tuple[int, ...]]], Any]:
    ops = Ops()
    chain: list[dict[Point, tuple[int, ...]]] = [{None: ()}]
    for _ in range(maximum):
        next_support: dict[Point, tuple[int, ...]] = {}
        for partial, witness in chain[-1].items():
            for index, point in enumerate(points):
                total = curve.add(partial, point, ops)
                next_support.setdefault(total, witness + (index,))
        chain.append(next_support)
    return chain, ops


def verify_witness(curve: Any, points: list[Point], indices: tuple[int, ...], target: Point) -> bool:
    recovered: Point = None
    for index in indices:
        recovered = curve.add(recovered, points[index])
    return recovered == target


def compile_configuration(
    curve: Any,
    q: int,
    factor_base: dict[str, Any],
    m: int,
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    points = [point_from_json(point) for point in factor_base["points"]]
    left_terms = m // 2
    right_terms = m - left_terms
    compiler_chain, compiler_ops = support_chain(curve, points, right_terms)
    expansion_chain, expansion_ops = support_chain(curve, points, m)
    left_map = compiler_chain[left_terms]
    right_map = compiler_chain[right_terms]
    shared_advice = left_terms == right_terms
    advice_entries = len(left_map) if shared_advice else len(left_map) + len(right_map)
    advice_bytes = deep_size(left_map) if shared_advice else deep_size(left_map) + deep_size(right_map)

    if len(left_map) <= len(right_map):
        iterate_map = left_map
        lookup_map = right_map
        iterate_is_left = True
    else:
        iterate_map = right_map
        lookup_map = left_map
        iterate_is_left = False

    online_ops = Ops()
    lookups = 0
    per_target_ops: list[int] = []
    per_target_lookups: list[int] = []
    successful = 0
    first_witness: dict[str, Any] | None = None
    for target_index, target_record in enumerate(targets):
        target = point_from_json(target_record["point"])
        before_ops = online_ops.group_operations
        before_lookups = lookups
        found: tuple[int, ...] | None = None
        for partial, partial_witness in iterate_map.items():
            complement = curve.add(target, curve.neg(partial), online_ops)
            lookups += 1
            other_witness = lookup_map.get(complement)
            if other_witness is None:
                continue
            found = (
                partial_witness + other_witness
                if iterate_is_left
                else other_witness + partial_witness
            )
            break
        per_target_ops.append(online_ops.group_operations - before_ops)
        per_target_lookups.append(lookups - before_lookups)
        exact_membership = target in expansion_chain[m]
        if (found is not None) != exact_membership:
            raise AssertionError("split lookup and exact m-fold support disagree")
        if found is not None:
            successful += 1
            if not verify_witness(curve, points, found, target):
                raise AssertionError("split witness failed exact arithmetic")
            if first_witness is None:
                first_witness = {
                    "target_index": target_index,
                    "indices": list(found),
                    "target": target_record["point"],
                }

    final_support = len(expansion_chain[m])
    exact_success_probability = final_support / q
    sampled_success_probability = successful / len(targets)
    offline_ops = {
        key: factor_base["build_ops"][key] + asdict(compiler_ops)[key]
        for key in asdict(compiler_ops)
    }
    average_online_ops = statistics.fmean(per_target_ops)
    epsilon = max(exact_success_probability, 1 / q)
    result = {
        **factor_base,
        "m": m,
        "split": [left_terms, right_terms],
        "support_sizes": [len(support) for support in expansion_chain],
        "final_support_size": final_support,
        "exact_success_probability": exact_success_probability,
        "sampled_successful_targets": successful,
        "sampled_target_count": len(targets),
        "sampled_success_probability": sampled_success_probability,
        "unordered_multiset_count": math.comb(len(points) + m - 1, m),
        "unordered_occupancy_lambda": math.comb(len(points) + m - 1, m) / q,
        "unordered_predicted_success": 1 - math.exp(-math.comb(len(points) + m - 1, m) / q),
        "compiler_support_sizes": {
            "left": len(left_map),
            "right": len(right_map),
        },
        "shared_advice": shared_advice,
        "advice_entries": advice_entries,
        "advice_deep_bytes": advice_bytes,
        "compiler_ops": asdict(compiler_ops),
        "diagnostic_expansion_ops": asdict(expansion_ops),
        "offline_ops": offline_ops,
        "online_ops": asdict(online_ops),
        "online_lookups": lookups,
        "online_group_operations_per_target": average_online_ops,
        "online_lookups_per_target": statistics.fmean(per_target_lookups),
        "online_group_operations_per_successful_target": (
            online_ops.group_operations / successful if successful else None
        ),
        "online_group_operations_distribution": per_target_ops,
        "first_witness": first_witness,
        "estimated_compiler_memory_traffic_bytes": compiler_ops.group_operations * 3 * 16,
        "s_t_squared_over_q": advice_entries * average_online_ops**2 / q,
        "s_t_squared_over_epsilon_q": advice_entries * average_online_ops**2 / (epsilon * q),
        "functional_advice_bytes_t_squared_over_epsilon_q": (
            advice_bytes * average_online_ops**2 / (epsilon * q)
        ),
        "offline_group_operations_per_supported_point": offline_ops["group_operations"] / final_support,
    }
    return result


def attach_random_ratios(configurations: list[dict[str, Any]]) -> None:
    groups: dict[tuple[int, str], dict[str, Any]] = {}
    random_x_groups: dict[tuple[int, str], dict[str, Any]] = {}
    for result in configurations:
        key = (result["m"], result["symmetry_mode"])
        if result["name"] == "random":
            groups[key] = result
        elif result["name"] == "random_x":
            random_x_groups[key] = result
    for result in configurations:
        random_result = groups[(result["m"], result["symmetry_mode"])]
        random_x_result = random_x_groups[(result["m"], result["symmetry_mode"])]
        result["final_support_ratio_to_random"] = (
            result["final_support_size"] / random_result["final_support_size"]
        )
        result["sampled_success_ratio_to_random"] = (
            result["sampled_success_probability"]
            / random_result["sampled_success_probability"]
            if random_result["sampled_success_probability"] > 0
            else None
        )
        result["advice_entries_ratio_to_random"] = (
            result["advice_entries"] / random_result["advice_entries"]
        )
        result["advice_deep_bytes_ratio_to_random"] = (
            result["advice_deep_bytes"] / random_result["advice_deep_bytes"]
        )
        result["online_group_operations_ratio_to_random"] = (
            result["online_group_operations_per_target"]
            / random_result["online_group_operations_per_target"]
        )
        result["offline_group_operations_ratio_to_random"] = (
            result["offline_ops"]["group_operations"]
            / random_result["offline_ops"]["group_operations"]
        )
        result["offline_group_operations_ratio_to_random_x"] = (
            result["offline_ops"]["group_operations"]
            / random_x_result["offline_ops"]["group_operations"]
        )
        result["success_adjusted_st2_ratio_to_random"] = (
            result["functional_advice_bytes_t_squared_over_epsilon_q"]
            / random_result["functional_advice_bytes_t_squared_over_epsilon_q"]
        )


def run_experiment(
    bit_sizes: list[int],
    seeds: list[int],
    m_values: list[int],
    target_count: int,
    rho_trials: int,
    occupancy_lambda: float,
) -> dict[str, Any]:
    for index, bits in enumerate(bit_sizes):
        exact_int(bits, f"bit_sizes[{index}]", 8)
    for index, seed in enumerate(seeds):
        exact_int(seed, f"seeds[{index}]")
    for index, m in enumerate(m_values):
        exact_int(m, f"m_values[{index}]", 2)
    exact_int(target_count, "target_count", 1)
    exact_int(rho_trials, "rho_trials", 1)
    if type(occupancy_lambda) not in (int, float) or isinstance(occupancy_lambda, bool):
        raise ValueError("occupancy_lambda must be numeric")
    if occupancy_lambda <= 0:
        raise ValueError("occupancy_lambda must be positive")

    families = [
        "random",
        "random_x",
        "x_interval",
        "square_map",
        "rational_union",
        "scalar_progression_positive_control",
    ]
    symmetry_modes = ["sign_canonical", "sign_complete"]
    instances: list[dict[str, Any]] = []
    for seed_index, seed in enumerate(seeds):
        previous_q = 0
        for bits in bit_sizes:
            curve_record = generate_prime_order_curve(bits, seed + bits * 1009)
            q = curve_record["q"]
            if q <= previous_q:
                raise AssertionError("prime subgroup schedule is not strictly increasing")
            previous_q = q
            curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
            generator = point_from_json(curve_record["generator"])
            target_rng = random.Random(seed ^ (bits << 24) ^ 0x3C6EF372)
            target_scalars = target_rng.sample(range(1, q), target_count)
            targets = [
                {"scalar": scalar, "point": list(curve.mul(scalar, generator))}
                for scalar in target_scalars
            ]
            configurations: list[dict[str, Any]] = []
            for m_index, m in enumerate(m_values):
                size = choose_factor_base_size(q, m, occupancy_lambda)
                for symmetry_index, symmetry_mode in enumerate(symmetry_modes):
                    for family_index, family in enumerate(families):
                        family_seed = (
                            seed
                            ^ (bits << 20)
                            ^ (m_index << 12)
                            ^ (symmetry_index << 8)
                            ^ (family_index * 0x9E3779B1)
                        )
                        factor_base = make_factor_base(
                            family,
                            symmetry_mode,
                            curve,
                            q,
                            generator,
                            size,
                            family_seed,
                        )
                        configurations.append(
                            compile_configuration(curve, q, factor_base, m, targets)
                        )
            attach_random_ratios(configurations)

            rho_results = []
            for trial_index in range(rho_trials):
                target_record = targets[trial_index]
                target = point_from_json(target_record["point"])
                rho = ENERGY.pollard_rho(
                    curve,
                    q,
                    generator,
                    target,
                    seed ^ (bits << 12) ^ trial_index,
                )
                rho["known_scalar"] = target_record["scalar"]
                rho["target"] = target_record["point"]
                if rho["recovered_scalar"] != target_record["scalar"]:
                    raise AssertionError("rho recovered the wrong scalar")
                rho_results.append(rho)
            instances.append(
                {
                    "seed_index": seed_index,
                    "seed": seed,
                    "curve": curve_record,
                    "targets": targets,
                    "configurations": configurations,
                    "rho": {
                        "trials": rho_results,
                        "median_group_operations": statistics.median(
                            trial["ops"]["group_operations"] for trial in rho_results
                        ),
                        "analytic_sqrt_q": math.sqrt(q),
                    },
                }
            )

    promotion_counts: dict[str, int] = {}
    for instance in instances:
        for result in instance["configurations"]:
            if result["name"] in (
                "random",
                "random_x",
                "scalar_progression_positive_control",
            ):
                continue
            key = f"{result['name']}|{result['symmetry_mode']}|m={result['m']}"
            passed = (
                result["final_support_ratio_to_random"] >= 0.8
                and result["success_adjusted_st2_ratio_to_random"] <= 0.8
                and result["offline_group_operations_ratio_to_random_x"] <= 4.0
            )
            if passed:
                promotion_counts[key] = promotion_counts.get(key, 0) + 1
    promoted = sorted(key for key, count in promotion_counts.items() if count >= 3)
    return {
        "protocol": "EXP-ECDLP-RECURSIVE-001-v2",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"],
        "valid": True,
        "source": dict(SOURCE_HASHES),
        "config": {
            "bit_sizes": bit_sizes,
            "seeds": seeds,
            "m_values": m_values,
            "target_count": target_count,
            "rho_trials": rho_trials,
            "occupancy_lambda": occupancy_lambda,
            "families": families,
            "symmetry_modes": symmetry_modes,
        },
        "instances": instances,
        "summary": {
            "instances_completed": len(instances),
            "all_curves_prime_order": all(
                instance["curve"]["q"] == instance["curve"]["order"]
                and instance["curve"]["cofactor"] == 1
                for instance in instances
            ),
            "all_rho_trials_verified": all(
                trial["verified"]
                for instance in instances
                for trial in instance["rho"]["trials"]
            ),
            "promotion_counts": promotion_counts,
            "promoted_configurations": promoted,
            "preflight_gate_passed": bool(promoted),
            "breakthrough_claim": False,
            "promotion_metric": "functional advice bytes * online group operations^2 / (exact success probability * subgroup order), normalized to matched random",
            "boundary": "A promotion signal would justify a source-tagged follow-up, not an ECDLP break.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bit-sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, required=True)
    parser.add_argument("--m-values", nargs="+", type=int, required=True)
    parser.add_argument("--targets", type=int, default=256)
    parser.add_argument("--rho-trials", type=int, default=4)
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_experiment(
        args.bit_sizes,
        args.seeds,
        args.m_values,
        args.targets,
        args.rho_trials,
        args.occupancy_lambda,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
