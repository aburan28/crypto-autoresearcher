#!/usr/bin/env python3
"""Independent verifier for EXP-ECDLP-RECURSIVE-002-v1.

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


PROTOCOL = "EXP-ECDLP-RECURSIVE-002-v1"
VERIFIER_PROTOCOL = "EXP-ECDLP-RECURSIVE-002-v1-independent-verifier"
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
    "null_calibrated_coverage_sha256": "f2c0a9456758931c3c46651e2482330e05b76b6efb7253995c3b712572a3dc4f",
    "prior_independent_arithmetic_verifier_sha256": "d677d1bc9c7efa9c3a94704eddd2f80ea651074f55c4a8452e5295f5d9797552",
    "recursive_expansion_sha256": "c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d",
    "coordinate_energy_sha256": "7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71",
}
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
CANDIDATE_FAMILIES = ["x_interval", "square_map", "rational_union"]
NULL_FAMILIES = ["random", "random_x"]
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [2473001, 2473002, 2473003],
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
        trace = p + 1 - order
        if trace == 0:
            rejections["trace_zero"] += 1
            continue
        if trace == 1:
            rejections["anomalous_trace_one"] += 1
            continue
        if not PRIOR.is_prime(order):
            rejections["composite_order"] += 1
            continue
        j_value = j_invariant(p, a, b)
        if j_value in (0, 1728 % p):
            rejections["special_j"] += 1
            continue
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


def make_base(family: str, p: int, a: int, b: int, q: int, generator: Point, size: int, seed: int) -> dict[str, Any]:
    # factor_base is independently reconstructed in EXP-001's independent verifier.
    return PRIOR.factor_base(family, "sign_complete", p, a, b, q, generator, size, seed)


def support_chain(p: int, a: int, points: list[Point], maximum: int) -> tuple[list[dict[Point, tuple[int, ...]]], Any]:
    return PRIOR.support_chain(p, a, points, maximum)


def compile_base(p: int, a: int, q: int, factor_base: dict[str, Any], targets: list[dict[str, Any]], order_seeds: list[int]) -> dict[str, Any]:
    points = [tuple(point) for point in factor_base["points"]]
    compiler_chain, compiler_ops = support_chain(p, a, points, 4)
    expansion_chain, expansion_ops = support_chain(p, a, points, 8)
    advice_map, exact_support = compiler_chain[4], expansion_chain[8]
    canonical_items = sorted(advice_map.items(), key=lambda item: point_key(item[0]))
    order_results: list[dict[str, Any]] = []
    first_witness: dict[str, Any] | None = None
    for order_index, order_seed in enumerate(order_seeds):
        ordered_items = list(canonical_items)
        random.Random(order_seed ^ factor_base["seed"]).shuffle(ordered_items)
        ops, lookups, successes = PRIOR.VerifyOps(), 0, 0
        per_target_ops: list[int] = []
        for target_index, record in enumerate(targets):
            target = tuple(record["point"])
            before = ops.group_operations
            found: tuple[int, ...] | None = None
            for partial, partial_witness in ordered_items:
                complement = PRIOR.point_add(target, PRIOR.point_neg(partial, p), p, a, ops)
                lookups += 1
                other = advice_map.get(complement)
                if other is not None:
                    found = partial_witness + other
                    break
            per_target_ops.append(ops.group_operations - before)
            if (found is not None) != (target in exact_support):
                raise AssertionError("shuffled split scan disagrees with exact support")
            if found is not None:
                successes += 1
                recovered: Point = None
                for index in found:
                    recovered = PRIOR.point_add(recovered, points[index], p, a)
                if recovered != target:
                    raise AssertionError("shuffled split witness failed independent arithmetic")
                if first_witness is None and order_index == 0:
                    first_witness = {"order_seed": order_seed, "target_index": target_index, "indices": list(found), "target": record["point"]}
        order_results.append({
            "order_seed": order_seed, "sampled_successful_targets": successes,
            "online_group_operations": ops.group_operations, "online_lookups": lookups,
            "average_online_group_operations_per_target": statistics.fmean(per_target_ops),
            "median_online_group_operations_per_target": statistics.median(per_target_ops),
            "maximum_online_group_operations_per_target": max(per_target_ops),
        })
    averages = [row["average_online_group_operations_per_target"] for row in order_results]
    robust = statistics.median(averages)
    advice_entries = len(advice_map)
    exact_epsilon = len(exact_support) / q
    compiler_dict = asdict(compiler_ops)
    return {
        "name": factor_base["name"], "seed": factor_base["seed"], "size": factor_base["size"],
        "factor_base_digest": stable_digest(factor_base), "build_ops": factor_base["build_ops"],
        "build_diagnostics": factor_base["build_diagnostics"], "compiler_ops": compiler_dict,
        "diagnostic_expansion_ops": asdict(expansion_ops),
        "offline_ops": {key: factor_base["build_ops"][key] + compiler_dict[key] for key in compiler_dict},
        "four_term_support_size": advice_entries,
        "generic_signed_four_term_maximum": signed_class_count(len(points) // 2, 4),
        "eight_term_support_size": len(exact_support), "exact_success_probability": exact_epsilon,
        "coverage_efficiency": len(exact_support) / (advice_entries**2), "advice_entries": advice_entries,
        "advice_map_deep_bytes": PRIOR.deep_size(advice_map), "factor_base_deep_bytes": PRIOR.deep_size(points),
        "compiled_artifact_deep_bytes": PRIOR.deep_size({"factor_base": points, "advice": advice_map}),
        "order_results": order_results, "order_robust_online_group_operations_per_target": robust,
        "order_variation_ratio": max(averages) / min(averages),
        "functional_frontier_score": PRIOR.deep_size({"factor_base": points, "advice": advice_map}) * robust**2 / (exact_epsilon * q),
        "estimated_lookup_traffic_bytes": int(statistics.median(row["online_lookups"] for row in order_results) * 64),
        "first_witness": first_witness,
    }


def empirical_percentile(value: float, distribution: list[float], higher_is_better: bool) -> float:
    if not distribution:
        raise AssertionError("empty null distribution")
    favorable = sum(item < value for item in distribution) if higher_is_better else sum(item > value for item in distribution)
    tied = sum(item == value for item in distribution)
    return (1 + favorable + 0.5 * tied) / (len(distribution) + 1)


def distribution_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    directions = {"eight_term_support_size": True, "coverage_efficiency": True, "functional_frontier_score": False, "four_term_support_size": True, "offline_group_operations": False}
    summary: dict[str, Any] = {"replicates": len(rows)}
    for metric in directions:
        values = [row["offline_ops"]["group_operations"] if metric == "offline_group_operations" else row[metric] for row in rows]
        summary[metric] = {"values": values, "minimum": min(values), "median": statistics.median(values), "maximum": max(values)}
    return summary


def attach_percentiles(candidate: dict[str, Any], null_rows: dict[str, list[dict[str, Any]]]) -> None:
    candidate["null_percentiles"] = {}
    for name, rows in null_rows.items():
        candidate["null_percentiles"][name] = {
            "eight_term_support": empirical_percentile(candidate["eight_term_support_size"], [row["eight_term_support_size"] for row in rows], True),
            "coverage_efficiency": empirical_percentile(candidate["coverage_efficiency"], [row["coverage_efficiency"] for row in rows], True),
            "functional_frontier": empirical_percentile(candidate["functional_frontier_score"], [row["functional_frontier_score"] for row in rows], False),
        }
    random_x_offline = statistics.median(row["offline_ops"]["group_operations"] for row in null_rows["random_x"])
    candidate["offline_group_operations_ratio_to_random_x_median"] = candidate["offline_ops"]["group_operations"] / random_x_offline
    candidate["split_support_ratio_to_random_medians"] = {name: candidate["four_term_support_size"] / statistics.median(row["four_term_support_size"] for row in rows) for name, rows in null_rows.items()}
    candidate["instance_gate_passed"] = (
        all(values["eight_term_support"] >= .95 and values["coverage_efficiency"] >= .95 and values["functional_frontier"] >= .90 for values in candidate["null_percentiles"].values())
        and candidate["order_variation_ratio"] <= 1.25
        and candidate["offline_group_operations_ratio_to_random_x_median"] <= 4.0
    )
    candidate["split_compression_gate_passed"] = all(ratio <= .8 for ratio in candidate["split_support_ratio_to_random_medians"].values())


def validate_config(config: Any, enforce_frozen: bool) -> dict[str, Any]:
    if type(config) is not dict or set(config) != set(FROZEN_CONFIG):
        raise AssertionError("config keys do not match protocol")
    for label, minimum in (("bit_sizes", 8), ("seeds", None), ("order_seeds", None)):
        values = config[label]
        if type(values) is not list or not values:
            raise AssertionError(f"config.{label} must be a nonempty list")
        for index, value in enumerate(values):
            require_exact_int(value, f"config.{label}[{index}]", minimum)
    for label, minimum in (("null_replicates_per_family", 2), ("m", 8), ("target_count", 1), ("rho_trials", 1)):
        require_exact_int(config[label], f"config.{label}", minimum)
    if len(set(config["order_seeds"])) != len(config["order_seeds"]):
        raise AssertionError("config.order_seeds must be distinct")
    if config["rho_trials"] > config["target_count"]:
        raise AssertionError("rho trials exceed target count")
    occupancy = config["occupancy_lambda"]
    if type(occupancy) not in (int, float) or isinstance(occupancy, bool) or not math.isfinite(occupancy) or occupancy <= 0:
        raise AssertionError("config.occupancy_lambda must be finite and positive")
    if config["candidate_families"] != CANDIDATE_FAMILIES or config["null_families"] != NULL_FAMILIES or config["m"] != 8 or config["symmetry_mode"] != "sign_complete":
        raise AssertionError("factor-base family or m=8 sign-complete schedule mismatch")
    if enforce_frozen:
        assert_exact(config, FROZEN_CONFIG, "document.config")
    return config


def reconstruct_document(config: dict[str, Any]) -> dict[str, Any]:
    instances: list[dict[str, Any]] = []
    for seed_index, seed in enumerate(config["seeds"]):
        previous_q = 0
        for bits in config["bit_sizes"]:
            curve = reconstruct_clean_curve(bits, seed + bits * 1009)
            p, a, b, q = curve["p"], curve["a"], curve["b"], curve["q"]
            if q <= previous_q:
                raise AssertionError("clean subgroup schedule is not strictly increasing")
            previous_q = q
            if curve["trace"] in (0, 1) or curve["j_invariant"] in (0, 1728 % p):
                raise AssertionError("clean curve policy failed")
            generator = tuple(curve["generator"])
            if not PRIOR.on_curve(generator, p, a, b) or PRIOR.point_mul(q, generator, p, a) is not None:
                raise AssertionError("generator failed independent subgroup check")
            targets_rng = random.Random(seed ^ (bits << 24) ^ 0x1F83D9AB)
            targets = [{"scalar": scalar, "point": list(PRIOR.point_mul(scalar, generator, p, a))} for scalar in targets_rng.sample(range(1, q), config["target_count"])]
            size = PRIOR.choose_factor_base_size(q, 8, config["occupancy_lambda"])
            null_rows: dict[str, list[dict[str, Any]]] = {}
            for family_index, family in enumerate(NULL_FAMILIES):
                rows = []
                for replicate in range(config["null_replicates_per_family"]):
                    base_seed = seed ^ (bits << 20) ^ (family_index * 0x9E3779B1) ^ (replicate * 0x85EBCA6B)
                    base = make_base(family, p, a, b, q, generator, size, base_seed)
                    base["seed"] = base_seed
                    row = compile_base(p, a, q, base, targets, config["order_seeds"])
                    row["replicate"] = replicate
                    rows.append(row)
                null_rows[family] = rows
            candidates = []
            for family_index, family in enumerate(CANDIDATE_FAMILIES):
                base_seed = seed ^ (bits << 20) ^ 0xC2B2AE35 ^ (family_index * 0x27D4EB2F)
                base = make_base(family, p, a, b, q, generator, size, base_seed)
                base["seed"] = base_seed
                row = compile_base(p, a, q, base, targets, config["order_seeds"])
                attach_percentiles(row, null_rows)
                candidates.append(row)
            control_seed = seed ^ (bits << 20) ^ 0x165667B1
            control_base = make_base("scalar_progression_positive_control", p, a, b, q, generator, size, control_seed)
            control_base["seed"] = control_seed
            control = compile_base(p, a, q, control_base, targets, config["order_seeds"])
            control["positive_control_passed"] = control["four_term_support_size"] < statistics.median(row["four_term_support_size"] for row in null_rows["random"]) and control["eight_term_support_size"] < statistics.median(row["eight_term_support_size"] for row in null_rows["random"])
            rho_trials = []
            for trial_index in range(config["rho_trials"]):
                target = tuple(targets[trial_index]["point"])
                trial = PRIOR.replay_rho(p, a, q, generator, target, seed ^ (bits << 12) ^ trial_index)
                trial["known_scalar"] = targets[trial_index]["scalar"]
                if trial["recovered_scalar"] != trial["known_scalar"]:
                    raise AssertionError("rho recovered wrong scalar")
                rho_trials.append(trial)
            instances.append({
                "seed_index": seed_index, "seed": seed, "curve": curve, "factor_base_size": size, "targets": targets,
                "null_distributions": {family: distribution_summary(rows) for family, rows in null_rows.items()},
                "null_rows": null_rows, "candidate_rows": candidates, "scalar_progression_control": control,
                "rho": {"trials": rho_trials, "median_group_operations": statistics.median(row["ops"]["group_operations"] for row in rho_trials), "analytic_sqrt_q": math.sqrt(q)},
            })
    counts = {family: 0 for family in CANDIDATE_FAMILIES}
    sizes = {family: set() for family in CANDIDATE_FAMILIES}
    seeds = {family: set() for family in CANDIDATE_FAMILIES}
    for instance in instances:
        for row in instance["candidate_rows"]:
            if row["instance_gate_passed"]:
                family = row["name"]
                counts[family] += 1
                sizes[family].add(instance["curve"]["bits"])
                seeds[family].add(instance["seed"])
    promoted = sorted(family for family in CANDIDATE_FAMILIES if counts[family] >= 6 and sizes[family] == set(config["bit_sizes"]) and seeds[family] == set(config["seeds"]))
    return {
        "protocol": PROTOCOL, "claim_status": CLAIM_STATUS, "valid": True,
        "source": {key: EXPECTED_HASHES[key] for key in ("null_calibrated_coverage_sha256", "recursive_expansion_sha256", "coordinate_energy_sha256")},
        "config": copy.deepcopy(config), "instances": instances,
        "summary": {
            "instances_completed": len(instances),
            "all_curves_clean": all(row["curve"]["trace"] not in (0, 1) and row["curve"]["j_invariant"] not in (0, 1728 % row["curve"]["p"]) and row["curve"]["q"] == row["curve"]["order"] for row in instances),
            "all_positive_controls_passed": all(row["scalar_progression_control"]["positive_control_passed"] for row in instances),
            "all_rho_trials_verified": all(trial["verified"] for row in instances for trial in row["rho"]["trials"]),
            "family_pass_counts": counts, "family_pass_sizes": {family: sorted(value) for family, value in sizes.items()},
            "family_pass_seeds": {family: sorted(value) for family, value in seeds.items()}, "promoted_families": promoted,
            "preflight_gate_passed": bool(promoted), "split_compression_claim": False, "breakthrough_claim": False,
            "boundary": "A promotion is a replicated toy additive-geometry signal only; rank, descent, exponent, and deployment remain untested.",
        },
    }


def verify_document(document: Any, enforce_frozen: bool = True) -> dict[str, Any]:
    if type(document) is not dict or document.get("protocol") != PROTOCOL:
        raise AssertionError("unexpected top-level document or protocol")
    hashes = verify_source_hashes()
    config = validate_config(document.get("config"), enforce_frozen)
    expected = reconstruct_document(config)
    assert_exact(document, expected)
    return {
        "valid": True, "protocol": VERIFIER_PROTOCOL, "source": hashes,
        "summary": {
            "instances_verified": len(expected["instances"]), "exact_integer_types_verified": True,
            "curve_orders_recomputed": True, "clean_curve_rejections_replayed": True,
            "targets_factor_bases_and_31_plus_31_nulls_replayed": True,
            "four_and_eight_term_supports_orders_witnesses_percentiles_and_family_gate_replayed": True,
            "operation_counters_memory_bytes_and_rho_replayed": True,
            "preflight_gate_passed": expected["summary"]["preflight_gate_passed"], "breakthrough_claim": False,
            "frozen_config_enforced": enforce_frozen,
            "boundary": "Independent arithmetic verification of frozen toy evidence only." if enforce_frozen else "Independent arithmetic verification of a reduced toy test configuration only.",
        },
    }


def duplicate_rejecting_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def parse_json(raw: bytes) -> Any:
    return json.loads(raw, object_pairs_hook=duplicate_rejecting_object, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"non-finite JSON constant {value}")))


def expect_rejection(document: dict[str, Any], label: str) -> str:
    try:
        verify_document(document, enforce_frozen=False)
    except (AssertionError, ValueError, TypeError, OverflowError) as error:
        return f"{label}:{type(error).__name__}"
    raise AssertionError(f"mutation {label!r} was accepted")


def run_self_test() -> dict[str, Any]:
    hashes = verify_source_hashes()
    tiny = {**copy.deepcopy(FROZEN_CONFIG), "bit_sizes": [8], "seeds": [1701], "null_replicates_per_family": 2, "target_count": 8, "order_seeds": [11, 13], "occupancy_lambda": 0.15, "rho_trials": 1}
    fixture = reconstruct_document(tiny)
    verify_document(fixture, enforce_frozen=False)
    checks = ["tiny_round_trip_exact", "all_four_source_hashes_enforced"]
    mutations: list[tuple[str, Any]] = []
    changed = copy.deepcopy(fixture); changed["instances"][0]["curve"]["trace"] = 1; mutations.append(("anomalous_trace_acceptance", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["curve"]["j_invariant"] = 0; mutations.append(("special_j_curve_rejected", changed))
    changed = copy.deepcopy(fixture); changed["source"]["null_calibrated_coverage_sha256"] = "0" * 64; mutations.append(("source_hash", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["null_rows"]["random"][0]["eight_term_support_size"] += 1; mutations.append(("null_replicate_metric", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["candidate_rows"][0]["null_percentiles"]["random"]["coverage_efficiency"] += .1; mutations.append(("percentile", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["candidate_rows"][0]["order_results"][0]["order_seed"] += 1; mutations.append(("order_seed_result", changed))
    witness_row = next(row for row in fixture["instances"][0]["candidate_rows"] if row["first_witness"] is not None)
    changed = copy.deepcopy(fixture); next(row for row in changed["instances"][0]["candidate_rows"] if row["name"] == witness_row["name"])["first_witness"]["target_index"] += 1; mutations.append(("witness", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["targets"][0]["scalar"] = True; mutations.append(("bool_for_exact_int", changed))
    changed = copy.deepcopy(fixture); changed["instances"][0]["factor_base_size"] = float(changed["instances"][0]["factor_base_size"]); mutations.append(("float_for_exact_int", changed))
    changed = copy.deepcopy(fixture); changed["summary"]["preflight_gate_passed"] = not changed["summary"]["preflight_gate_passed"]; mutations.append(("promotion_family_gate", changed))
    checks.extend(expect_rejection(document, label) for label, document in mutations)
    for label, raw in (("duplicate_json_key_rejected", b'{"x":1,"x":2}'), ("nonfinite_json_rejected", b'{"x":NaN}')):
        try:
            parse_json(raw)
        except ValueError:
            checks.append(label)
        else:
            raise AssertionError(f"{label} failed")
    encoded = json.dumps(fixture, sort_keys=True, separators=(",", ":")).encode()
    return {"valid": True, "protocol": f"{VERIFIER_PROTOCOL}-selftest", "source": hashes, "tests": checks, "tiny_fixture": {"sha256": hashlib.sha256(encoded).hexdigest(), "bytes": len(encoded), "instances": 1}, "experiment_harness_executed": False}


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
