#!/usr/bin/env python3
"""Independent verifier for EXP-ECDLP-RECURSIVE-001-v2.

This module intentionally does not import the experiment implementation or its
coordinate-energy prerequisite.  It reconstructs the complete claimed result
from the frozen configuration with separate affine arithmetic, then performs a
type-strict recursive comparison.  In particular, Python's equality between
``True`` and ``1`` is never accepted for an exact integer field.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None

PROTOCOL = "EXP-ECDLP-RECURSIVE-001-v2"
VERIFIER_PROTOCOL = f"{PROTOCOL}-independent-verifier"
RECURSIVE_SOURCE_SHA256 = (
    "c8e6986dd48e341b3e585a170990a018210602f99fc6cd748b81902f1b4e446d"
)
COORDINATE_ENERGY_SOURCE_SHA256 = (
    "7e9b16c18c5855ef7786f78d42300e63fb2a3dcf768413355a31d14160c6ea71"
)
RECURSIVE_SOURCE_PATH = Path(__file__).with_name("recursive_expansion.py").resolve()
COORDINATE_ENERGY_SOURCE_PATH = (
    Path(__file__).resolve().parents[2]
    / "EXP-ECDLP-ENERGY-001"
    / "src"
    / "coordinate_energy.py"
)
FAMILIES = [
    "random",
    "random_x",
    "x_interval",
    "square_map",
    "rational_union",
    "scalar_progression_positive_control",
]
SYMMETRY_MODES = ["sign_canonical", "sign_complete"]
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
OP_FIELDS = (
    "group_operations",
    "point_additions",
    "point_doublings",
    "field_multiplications",
    "field_inversions",
)
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [1473001, 1473002],
    "m_values": [5, 6, 8],
    "target_count": 256,
    "rho_trials": 4,
    "occupancy_lambda": 0.5,
    "families": FAMILIES,
    "symmetry_modes": SYMMETRY_MODES,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_source_hashes() -> dict[str, str]:
    actual = {
        "recursive_expansion_sha256": sha256_file(RECURSIVE_SOURCE_PATH),
        "coordinate_energy_sha256": sha256_file(COORDINATE_ENERGY_SOURCE_PATH),
    }
    expected = {
        "recursive_expansion_sha256": RECURSIVE_SOURCE_SHA256,
        "coordinate_energy_sha256": COORDINATE_ENERGY_SOURCE_SHA256,
    }
    if actual != expected:
        raise AssertionError(
            f"source hash mismatch: expected {expected!r}, observed {actual!r}"
        )
    return actual


@dataclass
class VerifyOps:
    group_operations: int = 0
    point_additions: int = 0
    point_doublings: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0


def require_exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise AssertionError(
            f"{label} must be an exact integer, got {type(value).__name__}"
        )
    if minimum is not None and value < minimum:
        raise AssertionError(f"{label} must be at least {minimum}")
    return value


def assert_exact(actual: Any, expected: Any, path: str = "document") -> None:
    """Compare recursively without bool/int or int/float coercion."""
    if type(actual) is not type(expected):
        raise AssertionError(
            f"{path}: type mismatch: got {type(actual).__name__}, "
            f"expected {type(expected).__name__}"
        )
    if isinstance(expected, dict):
        actual_keys = set(actual)
        expected_keys = set(expected)
        if actual_keys != expected_keys:
            missing = sorted(expected_keys - actual_keys)
            extra = sorted(actual_keys - expected_keys)
            raise AssertionError(f"{path}: key mismatch: missing={missing}, extra={extra}")
        for key in expected:
            assert_exact(actual[key], expected[key], f"{path}.{key}")
        return
    if isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(
                f"{path}: length mismatch: got {len(actual)}, expected {len(expected)}"
            )
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            assert_exact(actual_item, expected_item, f"{path}[{index}]")
        return
    if isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"{path}: float mismatch: got {actual!r}, expected {expected!r}")
        return
    if actual != expected:
        raise AssertionError(f"{path}: mismatch: got {actual!r}, expected {expected!r}")


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd = value - 1
    powers = 0
    while odd % 2 == 0:
        powers += 1
        odd //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        residue = pow(base, odd, value)
        if residue in (1, value - 1):
            continue
        for _ in range(powers - 1):
            residue = residue * residue % value
            if residue == value - 1:
                break
        else:
            return False
    return True


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors.append(divisor)
            value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def field_prime(bits: int, seed: int) -> int:
    span = max(1, 1 << max(1, bits - 5))
    candidate = (1 << bits) - 1 - 2 * (seed % span)
    candidate -= (candidate - 3) % 4
    lower = 1 << (bits - 1)
    while candidate >= lower:
        if is_prime(candidate):
            return candidate
        candidate -= 4
    raise AssertionError("seeded field-prime search failed")


def point_neg(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def point_add(
    left: Point,
    right: Point,
    p: int,
    a: int,
    ops: VerifyOps | None = None,
) -> Point:
    if ops is not None:
        ops.group_operations += 1
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if ops is not None:
            ops.point_doublings += 1
            ops.field_multiplications += 4
            ops.field_inversions += 1
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        if ops is not None:
            ops.point_additions += 1
            ops.field_multiplications += 3
            ops.field_inversions += 1
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def point_mul(
    scalar: int,
    point: Point,
    p: int,
    a: int,
    ops: VerifyOps | None = None,
) -> Point:
    if scalar < 0:
        return point_mul(-scalar, point_neg(point, p), p, a, ops)
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = point_add(result, addend, p, a, ops)
        scalar >>= 1
        if scalar:
            addend = point_add(addend, addend, p, a, ops)
    return result


def on_curve(point: Point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (
        0 <= x < p
        and 0 <= y < p
        and (y * y - (x * x * x + a * x + b)) % p == 0
    )


def curve_order(p: int, a: int, b: int) -> int:
    total = 1
    exponent = (p - 1) // 2
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            total += 1
        elif pow(rhs, exponent, p) == 1:
            total += 2
    return total


def square_root(rhs: int, p: int) -> int | None:
    rhs %= p
    if rhs == 0:
        return 0
    if pow(rhs, (p - 1) // 2, p) != 1:
        return None
    root = pow(rhs, (p + 1) // 4, p)
    if root * root % p != rhs:
        return None
    return min(root, (-root) % p)


def reconstruct_curve(bits: int, selection_seed: int, max_attempts: int = 128) -> dict[str, Any]:
    p = field_prime(bits, selection_seed ^ 0x6A09E667)
    rng = random.Random((selection_seed << 17) ^ bits ^ 0xBB67AE85)
    counted_orders = 0
    for attempt in range(1, max_attempts + 1):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            continue
        counted_orders += 1
        order = curve_order(p, a, b)
        trace = p + 1 - order
        if trace == 0 or not is_prime(order):
            continue
        generator_ops = VerifyOps()
        start = rng.randrange(p)
        generator: Point = None
        source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = (x, y)
            if point_mul(order, candidate, p, a, generator_ops) is None:
                generator = candidate
                source_x = x
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
            "generator_source_x": source_x,
            "curve_attempts": attempt,
            "order_count_legendre_tests": counted_orders * p,
            "generator_ops": asdict(generator_ops),
            "p_minus_1_factors": prime_factors(p - 1),
            "selection_policy": "first nonsingular ordinary prime-order curve from seeded coefficients",
        }
    raise AssertionError(f"prime-order curve search exhausted at {bits} bits")


def canonical_pair(point: Point, p: int) -> list[Point]:
    assert point is not None
    canonical = (point[0], min(point[1], (-point[1]) % p))
    return [canonical, point_neg(canonical, p)]


def canonical_scalar(
    scalar: int, point: Point, q: int, p: int
) -> tuple[int, Point]:
    assert point is not None
    canonical = canonical_pair(point, p)[0]
    return (scalar % q, canonical) if point == canonical else ((-scalar) % q, canonical)


def point_for_x(
    p: int,
    a: int,
    b: int,
    q: int,
    x: int,
    ops: VerifyOps,
    diagnostics: dict[str, int],
) -> Point:
    diagnostics["x_candidates"] += 1
    diagnostics["square_root_tests"] += 1
    y = square_root((x * x * x + a * x + b) % p, p)
    if y is None:
        return None
    diagnostics["subgroup_tests"] += 1
    point = (x, y)
    if point_mul(q, point, p, a, ops) is not None or y == 0:
        return None
    return point


def raw_factor_base(
    name: str,
    p: int,
    a: int,
    b: int,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    fiber_count = size // 2
    ops = VerifyOps()
    diagnostics = {"x_candidates": 0, "square_root_tests": 0, "subgroup_tests": 0}
    fibers: list[dict[str, Any]] = []
    seen_x: set[int] = set()

    def append(point: Point, source: dict[str, Any]) -> None:
        assert point is not None
        pair = canonical_pair(point, p)
        x = pair[0][0]
        if x in seen_x:
            return
        seen_x.add(x)
        fibers.append(
            {"points": [list(pair[0]), list(pair[1])], "source": source}
        )

    rng = random.Random(seed)
    if name == "random":
        for scalar in rng.sample(range(1, (q + 1) // 2), fiber_count):
            point = point_mul(scalar, generator, p, a, ops)
            canonical_s, canonical = canonical_scalar(scalar, point, q, p)
            append(
                canonical,
                {
                    "kind": "scalar",
                    "sampled_scalar": scalar,
                    "canonical_scalar": canonical_s,
                },
            )
    elif name == "random_x":
        for draw_index, x in enumerate(rng.sample(range(p), p)):
            point = point_for_x(p, a, b, q, x, ops, diagnostics)
            if point is not None:
                append(
                    point,
                    {"kind": "random_x", "draw_index": draw_index, "x": x},
                )
            if len(fibers) == fiber_count:
                break
    elif name == "scalar_progression_positive_control":
        scalar = 1
        while len(fibers) < fiber_count:
            point = point_mul(scalar, generator, p, a, ops)
            canonical_s, canonical = canonical_scalar(scalar, point, q, p)
            append(
                canonical,
                {
                    "kind": "scalar_progression",
                    "sampled_scalar": scalar,
                    "canonical_scalar": canonical_s,
                },
            )
            scalar += 1
    elif name == "x_interval":
        for x in range(p):
            point = point_for_x(p, a, b, q, x, ops, diagnostics)
            if point is not None:
                append(point, {"kind": "x_interval", "x": x})
            if len(fibers) == fiber_count:
                break
    elif name == "square_map":
        c = rng.randrange(p)
        for t in range(2 * p):
            x = (t * t + c) % p
            point = point_for_x(p, a, b, q, x, ops, diagnostics)
            if point is not None:
                append(point, {"kind": "square_map", "t": t, "c": c, "x": x})
            if len(fibers) == fiber_count:
                break
    elif name == "rational_union":
        c = rng.randrange(p)
        d = rng.randrange(p)
        e = rng.randrange(p)
        t = 0
        while t < 2 * p and len(fibers) < fiber_count:
            candidates = [("square", (t * t + c) % p)]
            denominator = (t + e) % p
            if denominator:
                candidates.append(
                    ("mobius", (t + d) * pow(denominator, -1, p) % p)
                )
            for map_name, x in candidates:
                point = point_for_x(p, a, b, q, x, ops, diagnostics)
                if point is not None:
                    append(
                        point,
                        {
                            "kind": "rational_union",
                            "map": map_name,
                            "t": t,
                            "c": c,
                            "d": d,
                            "e": e,
                            "x": x,
                        },
                    )
                if len(fibers) == fiber_count:
                    break
            t += 1
    else:
        raise AssertionError(f"unknown factor-base family {name!r}")
    if len(fibers) != fiber_count:
        raise AssertionError(f"{name} produced {len(fibers)} of {fiber_count} fibers")
    return {
        "points": [point for fiber in fibers for point in fiber["points"]],
        "fibers": fibers,
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
    }


def factor_base(
    family: str,
    symmetry_mode: str,
    p: int,
    a: int,
    b: int,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    raw_size = size * 2 if symmetry_mode == "sign_canonical" else size
    raw = raw_factor_base(family, p, a, b, q, generator, raw_size, seed)
    if symmetry_mode == "sign_canonical":
        points = [fiber["points"][0] for fiber in raw["fibers"]]
    else:
        points = raw["points"]
    if len(points) != size:
        raise AssertionError("reconstructed factor-base cardinality mismatch")
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


def support_chain(
    p: int, a: int, points: list[Point], maximum: int
) -> tuple[list[dict[Point, tuple[int, ...]]], VerifyOps]:
    ops = VerifyOps()
    chain: list[dict[Point, tuple[int, ...]]] = [{None: ()}]
    for _ in range(maximum):
        next_support: dict[Point, tuple[int, ...]] = {}
        for partial, witness in chain[-1].items():
            for index, point in enumerate(points):
                total = point_add(partial, point, p, a, ops)
                next_support.setdefault(total, witness + (index,))
        chain.append(next_support)
    return chain, ops


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
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


def compile_configuration(
    p: int,
    a: int,
    q: int,
    base: dict[str, Any],
    m: int,
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    points: list[Point] = [tuple(point) for point in base["points"]]
    left_terms = m // 2
    right_terms = m - left_terms
    compiler_chain, compiler_ops = support_chain(p, a, points, right_terms)
    expansion_chain, expansion_ops = support_chain(p, a, points, m)
    left_map = compiler_chain[left_terms]
    right_map = compiler_chain[right_terms]
    shared_advice = left_terms == right_terms
    advice_entries = len(left_map) if shared_advice else len(left_map) + len(right_map)
    advice_bytes = (
        deep_size(left_map)
        if shared_advice
        else deep_size(left_map) + deep_size(right_map)
    )
    if len(left_map) <= len(right_map):
        iterate_map, lookup_map, iterate_is_left = left_map, right_map, True
    else:
        iterate_map, lookup_map, iterate_is_left = right_map, left_map, False

    online_ops = VerifyOps()
    lookups = 0
    per_target_ops: list[int] = []
    per_target_lookups: list[int] = []
    successful = 0
    first_witness: dict[str, Any] | None = None
    for target_index, target_record in enumerate(targets):
        target = tuple(target_record["point"])
        before_ops = online_ops.group_operations
        before_lookups = lookups
        found: tuple[int, ...] | None = None
        for partial, partial_witness in iterate_map.items():
            complement = point_add(target, point_neg(partial, p), p, a, online_ops)
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
            raise AssertionError("split replay disagrees with exact recursive support")
        if found is not None:
            successful += 1
            recovered: Point = None
            for index in found:
                recovered = point_add(recovered, points[index], p, a)
            if recovered != target:
                raise AssertionError("reconstructed first witness failed arithmetic")
            if first_witness is None:
                first_witness = {
                    "target_index": target_index,
                    "indices": list(found),
                    "target": target_record["point"],
                }

    final_support = len(expansion_chain[m])
    exact_probability = final_support / q
    sampled_probability = successful / len(targets)
    compiler_dict = asdict(compiler_ops)
    expansion_dict = asdict(expansion_ops)
    offline_ops = {
        key: base["build_ops"][key] + compiler_dict[key] for key in OP_FIELDS
    }
    average_online_ops = statistics.fmean(per_target_ops)
    epsilon = max(exact_probability, 1 / q)
    multiset_count = math.comb(len(points) + m - 1, m)
    return {
        **base,
        "m": m,
        "split": [left_terms, right_terms],
        "support_sizes": [len(support) for support in expansion_chain],
        "final_support_size": final_support,
        "exact_success_probability": exact_probability,
        "sampled_successful_targets": successful,
        "sampled_target_count": len(targets),
        "sampled_success_probability": sampled_probability,
        "unordered_multiset_count": multiset_count,
        "unordered_occupancy_lambda": multiset_count / q,
        "unordered_predicted_success": 1 - math.exp(-(multiset_count / q)),
        "compiler_support_sizes": {"left": len(left_map), "right": len(right_map)},
        "shared_advice": shared_advice,
        "advice_entries": advice_entries,
        "advice_deep_bytes": advice_bytes,
        "compiler_ops": compiler_dict,
        "diagnostic_expansion_ops": expansion_dict,
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
        "s_t_squared_over_epsilon_q": (
            advice_entries * average_online_ops**2 / (epsilon * q)
        ),
        "functional_advice_bytes_t_squared_over_epsilon_q": (
            advice_bytes * average_online_ops**2 / (epsilon * q)
        ),
        "offline_group_operations_per_supported_point": (
            offline_ops["group_operations"] / final_support
        ),
    }


def choose_factor_base_size(q: int, m: int, occupancy_lambda: float) -> int:
    size = 2
    while math.comb(size + m - 1, m) / q < occupancy_lambda:
        size += 2
    return size


def attach_ratios(configurations: list[dict[str, Any]]) -> None:
    controls = {
        (row["m"], row["symmetry_mode"]): row
        for row in configurations
        if row["name"] == "random"
    }
    random_x_controls = {
        (row["m"], row["symmetry_mode"]): row
        for row in configurations
        if row["name"] == "random_x"
    }
    for row in configurations:
        control = controls[(row["m"], row["symmetry_mode"])]
        random_x_control = random_x_controls[(row["m"], row["symmetry_mode"])]
        row["final_support_ratio_to_random"] = (
            row["final_support_size"] / control["final_support_size"]
        )
        row["sampled_success_ratio_to_random"] = (
            row["sampled_success_probability"]
            / control["sampled_success_probability"]
            if control["sampled_success_probability"] > 0
            else None
        )
        row["advice_entries_ratio_to_random"] = (
            row["advice_entries"] / control["advice_entries"]
        )
        row["advice_deep_bytes_ratio_to_random"] = (
            row["advice_deep_bytes"] / control["advice_deep_bytes"]
        )
        row["online_group_operations_ratio_to_random"] = (
            row["online_group_operations_per_target"]
            / control["online_group_operations_per_target"]
        )
        row["offline_group_operations_ratio_to_random"] = (
            row["offline_ops"]["group_operations"]
            / control["offline_ops"]["group_operations"]
        )
        row["offline_group_operations_ratio_to_random_x"] = (
            row["offline_ops"]["group_operations"]
            / random_x_control["offline_ops"]["group_operations"]
        )
        row["success_adjusted_st2_ratio_to_random"] = (
            row["functional_advice_bytes_t_squared_over_epsilon_q"]
            / control["functional_advice_bytes_t_squared_over_epsilon_q"]
        )


def rho_step(
    p: int,
    a: int,
    q: int,
    generator: Point,
    target: Point,
    state: tuple[Point, int, int],
    salt: int,
    ops: VerifyOps,
) -> tuple[Point, int, int]:
    point, a_scalar, b_scalar = state
    partition = salt % 3 if point is None else (point[0] + salt) % 3
    if partition == 0:
        return point_add(point, generator, p, a, ops), (a_scalar + 1) % q, b_scalar
    if partition == 1:
        return (
            point_add(point, point, p, a, ops),
            (2 * a_scalar) % q,
            (2 * b_scalar) % q,
        )
    return point_add(point, target, p, a, ops), a_scalar, (b_scalar + 1) % q


def replay_rho(
    p: int, a: int, q: int, generator: Point, target: Point, seed: int
) -> dict[str, Any]:
    rng = random.Random(seed)
    ops = VerifyOps()
    max_steps = max(100, 20 * math.isqrt(q))
    for restart in range(32):
        a_scalar = rng.randrange(q)
        b_scalar = rng.randrange(q)
        state_point = point_add(
            point_mul(a_scalar, generator, p, a, ops),
            point_mul(b_scalar, target, p, a, ops),
            p,
            a,
            ops,
        )
        tortoise = (state_point, a_scalar, b_scalar)
        hare = tortoise
        salt = rng.randrange(q)
        for cycle_steps in range(1, max_steps + 1):
            tortoise = rho_step(p, a, q, generator, target, tortoise, salt, ops)
            hare = rho_step(p, a, q, generator, target, hare, salt, ops)
            hare = rho_step(p, a, q, generator, target, hare, salt, ops)
            if tortoise[0] != hare[0]:
                continue
            denominator = (tortoise[2] - hare[2]) % q
            if denominator == 0:
                break
            recovered = (
                (hare[1] - tortoise[1]) * pow(denominator, -1, q) % q
            )
            if point_mul(recovered, generator, p, a) == target:
                return {
                    "recovered_scalar": recovered,
                    "verified": True,
                    "restart": restart,
                    "cycle_steps": cycle_steps,
                    "ops": asdict(ops),
                }
            break
    raise AssertionError("independent Pollard-rho replay exhausted restarts")


def promotion_decisions(
    instances: list[dict[str, Any]],
) -> tuple[dict[str, int], list[str]]:
    promotion_counts: dict[str, int] = {}
    for instance in instances:
        for row in instance["configurations"]:
            if row["name"] in (
                "random",
                "random_x",
                "scalar_progression_positive_control",
            ):
                continue
            key = f"{row['name']}|{row['symmetry_mode']}|m={row['m']}"
            passed = (
                row["final_support_ratio_to_random"] >= 0.8
                and row["success_adjusted_st2_ratio_to_random"] <= 0.8
                and row["offline_group_operations_ratio_to_random_x"] <= 4.0
            )
            if passed:
                promotion_counts[key] = promotion_counts.get(key, 0) + 1
    promoted = sorted(key for key, count in promotion_counts.items() if count >= 3)
    return promotion_counts, promoted


def validate_config(config: Any, enforce_frozen: bool) -> dict[str, Any]:
    if type(config) is not dict:
        raise AssertionError("config must be an object")
    required_keys = set(FROZEN_CONFIG)
    if set(config) != required_keys:
        raise AssertionError("config keys do not match protocol")
    bit_sizes = config["bit_sizes"]
    seeds = config["seeds"]
    m_values = config["m_values"]
    for label, values, minimum in (
        ("bit_sizes", bit_sizes, 8),
        ("seeds", seeds, None),
        ("m_values", m_values, 2),
    ):
        if type(values) is not list or not values:
            raise AssertionError(f"config.{label} must be a nonempty list")
        for index, value in enumerate(values):
            require_exact_int(value, f"config.{label}[{index}]", minimum)
    require_exact_int(config["target_count"], "config.target_count", 1)
    require_exact_int(config["rho_trials"], "config.rho_trials", 1)
    occupancy = config["occupancy_lambda"]
    if type(occupancy) not in (int, float) or not math.isfinite(occupancy) or occupancy <= 0:
        raise AssertionError("config.occupancy_lambda must be a finite positive number")
    if config["families"] != FAMILIES or config["symmetry_modes"] != SYMMETRY_MODES:
        raise AssertionError("family or symmetry schedule mismatch")
    if config["rho_trials"] > config["target_count"]:
        raise AssertionError("rho trial count exceeds target count")
    if enforce_frozen:
        assert_exact(config, FROZEN_CONFIG, "document.config")
    return config


def reconstruct_document(config: dict[str, Any]) -> dict[str, Any]:
    instances: list[dict[str, Any]] = []
    for seed_index, seed in enumerate(config["seeds"]):
        previous_q = 0
        for bits in config["bit_sizes"]:
            curve = reconstruct_curve(bits, seed + bits * 1009)
            p, a, b, q = curve["p"], curve["a"], curve["b"], curve["q"]
            if q <= previous_q:
                raise AssertionError("prime subgroup schedule is not strictly increasing")
            previous_q = q
            generator = tuple(curve["generator"])
            if not on_curve(generator, p, a, b) or point_mul(q, generator, p, a) is not None:
                raise AssertionError("reconstructed generator failed independent subgroup check")
            target_rng = random.Random(seed ^ (bits << 24) ^ 0x3C6EF372)
            target_scalars = target_rng.sample(range(1, q), config["target_count"])
            targets = [
                {"scalar": scalar, "point": list(point_mul(scalar, generator, p, a))}
                for scalar in target_scalars
            ]
            configurations: list[dict[str, Any]] = []
            for m_index, m in enumerate(config["m_values"]):
                size = choose_factor_base_size(q, m, config["occupancy_lambda"])
                for symmetry_index, symmetry_mode in enumerate(SYMMETRY_MODES):
                    for family_index, family in enumerate(FAMILIES):
                        family_seed = (
                            seed
                            ^ (bits << 20)
                            ^ (m_index << 12)
                            ^ (symmetry_index << 8)
                            ^ (family_index * 0x9E3779B1)
                        )
                        base = factor_base(
                            family,
                            symmetry_mode,
                            p,
                            a,
                            b,
                            q,
                            generator,
                            size,
                            family_seed,
                        )
                        configurations.append(
                            compile_configuration(p, a, q, base, m, targets)
                        )
            attach_ratios(configurations)
            rho_trials = []
            for trial_index in range(config["rho_trials"]):
                target_record = targets[trial_index]
                target = tuple(target_record["point"])
                trial = replay_rho(
                    p,
                    a,
                    q,
                    generator,
                    target,
                    seed ^ (bits << 12) ^ trial_index,
                )
                trial["known_scalar"] = target_record["scalar"]
                trial["target"] = target_record["point"]
                if trial["recovered_scalar"] != target_record["scalar"]:
                    raise AssertionError("rho replay recovered the wrong scalar")
                rho_trials.append(trial)
            instances.append(
                {
                    "seed_index": seed_index,
                    "seed": seed,
                    "curve": curve,
                    "targets": targets,
                    "configurations": configurations,
                    "rho": {
                        "trials": rho_trials,
                        "median_group_operations": statistics.median(
                            trial["ops"]["group_operations"] for trial in rho_trials
                        ),
                        "analytic_sqrt_q": math.sqrt(q),
                    },
                }
            )

    promotion_counts, promoted = promotion_decisions(instances)
    return {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "valid": True,
        "source": {
            "recursive_expansion_sha256": RECURSIVE_SOURCE_SHA256,
            "coordinate_energy_sha256": COORDINATE_ENERGY_SOURCE_SHA256,
        },
        "config": copy.deepcopy(config),
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


def verify_document(document: Any, enforce_frozen: bool = True) -> dict[str, Any]:
    if type(document) is not dict:
        raise AssertionError("top-level JSON value must be an object")
    if document.get("protocol") != PROTOCOL:
        raise AssertionError("unexpected protocol")
    source_hashes = verify_source_hashes()
    config = validate_config(document.get("config"), enforce_frozen)
    expected = reconstruct_document(config)
    assert_exact(document, expected)
    promotion_counts = expected["summary"]["promotion_counts"]
    promoted = expected["summary"]["promoted_configurations"]
    return {
        "valid": True,
        "protocol": VERIFIER_PROTOCOL,
        "source": source_hashes,
        "summary": {
            "instances_verified": len(expected["instances"]),
            "configurations_verified": sum(
                len(instance["configurations"]) for instance in expected["instances"]
            ),
            "exact_integer_types_verified": True,
            "curve_orders_recomputed": True,
            "seeded_generators_and_targets_replayed": True,
            "factor_base_sources_replayed": True,
            "recursive_supports_rebuilt": True,
            "split_advice_and_first_witnesses_replayed": True,
            "operation_counters_replayed": True,
            "rho_trials_replayed": True,
            "promotion_counts": promotion_counts,
            "promoted_configurations": promoted,
            "preflight_gate_passed": bool(promoted),
            "breakthrough_claim": False,
            "frozen_config_enforced": enforce_frozen,
            "promotion_metric": "functional advice bytes * online group operations^2 / (exact success probability * subgroup order), normalized to matched random",
            "boundary": (
                "Independent arithmetic verification of frozen toy evidence only."
                if enforce_frozen
                else "Independent arithmetic verification of a submitted toy test configuration only."
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


def parse_json(raw: bytes) -> Any:
    return json.loads(
        raw,
        object_pairs_hook=duplicate_rejecting_object,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant {value}")
        ),
    )


def expect_rejection(document: dict[str, Any], label: str) -> str:
    try:
        verify_document(document, enforce_frozen=False)
    except (AssertionError, ValueError, TypeError, OverflowError) as error:
        return f"{label}:{type(error).__name__}"
    raise AssertionError(f"mutation {label!r} was accepted")


def run_self_test() -> dict[str, Any]:
    source_hashes = verify_source_hashes()
    tiny_config = {
        "bit_sizes": [8],
        "seeds": [1701],
        "m_values": [2, 3],
        "target_count": 12,
        "rho_trials": 2,
        "occupancy_lambda": 0.15,
        "families": FAMILIES,
        "symmetry_modes": SYMMETRY_MODES,
    }
    validate_config(tiny_config, enforce_frozen=False)
    fixture = reconstruct_document(tiny_config)
    verify_document(fixture, enforce_frozen=False)
    checks = ["tiny_round_trip_exact", "generator_and_dependency_hashes_enforced"]

    try:
        parse_json(b'{"duplicate":1,"duplicate":2}')
    except ValueError:
        checks.append("duplicate_json_key_rejected")
    else:
        raise AssertionError("duplicate JSON key was accepted")

    try:
        parse_json(b'{"nonfinite":NaN}')
    except ValueError:
        checks.append("nonfinite_json_constant_rejected")
    else:
        raise AssertionError("non-finite JSON constant was accepted")

    bool_mutation = copy.deepcopy(fixture)
    bool_mutation["instances"][0]["targets"][0]["scalar"] = True
    checks.append(expect_rejection(bool_mutation, "bool_for_integer"))

    float_mutation = copy.deepcopy(fixture)
    float_mutation["instances"][0]["configurations"][0]["final_support_size"] = float(
        float_mutation["instances"][0]["configurations"][0]["final_support_size"]
    )
    checks.append(expect_rejection(float_mutation, "float_for_integer"))

    random_x_canonical_mutation = copy.deepcopy(fixture)
    random_x_canonical = next(
        row
        for row in random_x_canonical_mutation["instances"][0]["configurations"]
        if row["name"] == "random_x"
        and row["symmetry_mode"] == "sign_canonical"
    )
    random_x_canonical["fibers"][0]["source"]["draw_index"] += 1
    checks.append(
        expect_rejection(random_x_canonical_mutation, "random_x_canonical_source")
    )

    random_x_complete_mutation = copy.deepcopy(fixture)
    random_x_complete = next(
        row
        for row in random_x_complete_mutation["instances"][0]["configurations"]
        if row["name"] == "random_x"
        and row["symmetry_mode"] == "sign_complete"
    )
    random_x_complete["fibers"][0]["source"]["x"] += 1
    checks.append(
        expect_rejection(random_x_complete_mutation, "random_x_complete_source")
    )

    random_x_counter_mutation = copy.deepcopy(fixture)
    random_x_counter = next(
        row
        for row in random_x_counter_mutation["instances"][0]["configurations"]
        if row["name"] == "random_x"
    )
    random_x_counter["build_ops"]["group_operations"] += 1
    checks.append(expect_rejection(random_x_counter_mutation, "random_x_build_counter"))

    random_x_diagnostic_mutation = copy.deepcopy(fixture)
    random_x_diagnostic = next(
        row
        for row in random_x_diagnostic_mutation["instances"][0]["configurations"]
        if row["name"] == "random_x"
    )
    random_x_diagnostic["build_diagnostics"]["x_candidates"] += 1
    checks.append(
        expect_rejection(random_x_diagnostic_mutation, "random_x_diagnostic")
    )

    ratio_mutation = copy.deepcopy(fixture)
    ratio_mutation["instances"][0]["configurations"][0][
        "offline_group_operations_ratio_to_random_x"
    ] += 0.25
    checks.append(expect_rejection(ratio_mutation, "random_x_offline_ratio"))

    success_adjusted_mutation = copy.deepcopy(fixture)
    success_adjusted_mutation["instances"][0]["configurations"][0][
        "success_adjusted_st2_ratio_to_random"
    ] += 0.25
    checks.append(
        expect_rejection(success_adjusted_mutation, "success_adjusted_st2_ratio")
    )

    synthetic_gate_row = {
        "name": "x_interval",
        "symmetry_mode": "sign_canonical",
        "m": 2,
        "final_support_ratio_to_random": 0.8,
        "advice_entries_ratio_to_random": 0.8,
        "online_group_operations_ratio_to_random": 1.0,
        "offline_group_operations_ratio_to_random": 100.0,
        "offline_group_operations_ratio_to_random_x": 4.0,
        "success_adjusted_st2_ratio_to_random": 0.8,
    }
    synthetic_instances = [
        {"configurations": [copy.deepcopy(synthetic_gate_row)]} for _ in range(3)
    ]
    synthetic_counts, synthetic_promoted = promotion_decisions(synthetic_instances)
    synthetic_key = "x_interval|sign_canonical|m=2"
    if synthetic_counts != {synthetic_key: 3} or synthetic_promoted != [synthetic_key]:
        raise AssertionError("promotion gate did not charge offline work to random_x")
    checks.append("promotion_uses_random_x_offline_control")

    for instance in synthetic_instances:
        instance["configurations"][0][
            "offline_group_operations_ratio_to_random_x"
        ] = 4.0000000001
        instance["configurations"][0]["offline_group_operations_ratio_to_random"] = 0.01
    blocked_counts, blocked_promoted = promotion_decisions(synthetic_instances)
    if blocked_counts or blocked_promoted:
        raise AssertionError("random offline ratio incorrectly overrode random_x gate")
    checks.append("random_ratio_cannot_override_random_x_offline_gate")

    entry_only_instances = [
        {"configurations": [copy.deepcopy(synthetic_gate_row)]} for _ in range(3)
    ]
    for instance in entry_only_instances:
        row = instance["configurations"][0]
        row["advice_entries_ratio_to_random"] = 0.01
        row["online_group_operations_ratio_to_random"] = 0.01
        row["offline_group_operations_ratio_to_random_x"] = 0.01
        row["success_adjusted_st2_ratio_to_random"] = 0.8000000001
    entry_only_counts, entry_only_promoted = promotion_decisions(entry_only_instances)
    if entry_only_counts or entry_only_promoted:
        raise AssertionError("entry or online ratio bypassed the functional ST2 gate")
    checks.append("entry_and_online_ratios_cannot_override_functional_st2_gate")

    witness_mutation = copy.deepcopy(fixture)
    witness_row = next(
        row
        for row in witness_mutation["instances"][0]["configurations"]
        if row["first_witness"] is not None
    )
    witness_row["first_witness"]["target_index"] += 1
    checks.append(expect_rejection(witness_mutation, "first_witness"))

    counter_mutation = copy.deepcopy(fixture)
    counter_mutation["instances"][0]["rho"]["trials"][0]["ops"][
        "group_operations"
    ] += 1
    checks.append(expect_rejection(counter_mutation, "rho_counter"))

    promotion_mutation = copy.deepcopy(fixture)
    promotion_mutation["summary"]["preflight_gate_passed"] = not promotion_mutation[
        "summary"
    ]["preflight_gate_passed"]
    checks.append(expect_rejection(promotion_mutation, "promotion_decision"))

    fixture_bytes = json.dumps(
        fixture, sort_keys=True, separators=(",", ":")
    ).encode()
    return {
        "valid": True,
        "protocol": f"{VERIFIER_PROTOCOL}-selftest",
        "source": source_hashes,
        "tests": checks,
        "tiny_fixture": {
            "sha256": hashlib.sha256(fixture_bytes).hexdigest(),
            "bytes": len(fixture_bytes),
            "instances": len(fixture["instances"]),
            "configurations": len(fixture["instances"][0]["configurations"]),
        },
        "experiment_harness_executed": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", type=Path)
    group.add_argument("--self-test", action="store_true")
    parser.add_argument(
        "--allow-nonfrozen-test-config",
        action="store_true",
        help="verify a reduced test configuration while preserving exact replay checks",
    )
    return parser.parse_args()


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def main() -> int:
    args = parse_args()
    raw: bytes | None = None
    try:
        if args.self_test:
            if args.allow_nonfrozen_test_config:
                raise ValueError(
                    "--allow-nonfrozen-test-config is only valid with --input"
                )
            emit(run_self_test())
            return 0
        raw = args.input.read_bytes()
        if len(raw) > 64 * 1024 * 1024:
            raise ValueError("input exceeds 64 MiB verifier limit")
        document = parse_json(raw)
        result = verify_document(
            document,
            enforce_frozen=not args.allow_nonfrozen_test_config,
        )
        result["input"] = {
            "path": str(args.input),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
        emit(result)
        return 0
    except (AssertionError, ValueError, TypeError, OverflowError, OSError) as error:
        failure: dict[str, Any] = {
            "valid": False,
            "protocol": VERIFIER_PROTOCOL,
            "error_type": type(error).__name__,
            "error": str(error),
        }
        if raw is not None:
            failure["input"] = {
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        emit(failure)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
