#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any, Iterable


Point = tuple[int, int] | None


@dataclass
class Ops:
    group_operations: int = 0
    point_additions: int = 0
    point_doublings: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0

    def add(self, other: "Ops") -> None:
        for key, value in asdict(other).items():
            setattr(self, key, getattr(self, key) + value)


class Curve:
    def __init__(self, p: int, a: int, b: int) -> None:
        self.p = p
        self.a = a % p
        self.b = b % p

    def neg(self, point: Point) -> Point:
        if point is None:
            return None
        return point[0], (-point[1]) % self.p

    def on_curve(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def add(self, left: Point, right: Point, ops: Ops | None = None) -> Point:
        if ops is not None:
            ops.group_operations += 1
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if ops is not None:
                ops.point_doublings += 1
                ops.field_multiplications += 4
                ops.field_inversions += 1
            slope = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p) % self.p
        else:
            if ops is not None:
                ops.point_additions += 1
                ops.field_multiplications += 3
                ops.field_inversions += 1
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        y3 = (slope * (x1 - x3) - y1) % self.p
        return x3, y3

    def mul(self, scalar: int, point: Point, ops: Ops | None = None) -> Point:
        if scalar < 0:
            return self.mul(-scalar, self.neg(point), ops)
        result: Point = None
        addend = point
        while scalar:
            if scalar & 1:
                result = self.add(result, addend, ops)
            scalar >>= 1
            if scalar:
                addend = self.add(addend, addend, ops)
        return result


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for prime in small:
        if value % prime == 0:
            return value == prime
    d = value - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2
    for base in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if base % value == 0:
            continue
        x = pow(base, d, value)
        if x in (1, value - 1):
            continue
        for _ in range(s - 1):
            x = x * x % value
            if x == value - 1:
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


def find_field_prime(bits: int, seed: int) -> int:
    span = max(1, 1 << max(1, bits - 5))
    candidate = (1 << bits) - 1 - 2 * (seed % span)
    candidate -= (candidate - 3) % 4
    lower = 1 << (bits - 1)
    while candidate >= lower:
        if is_prime(candidate):
            return candidate
        candidate -= 4
    raise RuntimeError(f"no {bits}-bit prime congruent to 3 mod 4 found")


def curve_order(curve: Curve) -> int:
    total = 1
    exponent = (curve.p - 1) // 2
    for x in range(curve.p):
        rhs = (x * x * x + curve.a * x + curve.b) % curve.p
        if rhs == 0:
            total += 1
        elif pow(rhs, exponent, curve.p) == 1:
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


def point_for_x(curve: Curve, q: int, x: int, ops: Ops, stats: dict[str, int]) -> Point:
    stats["x_candidates"] += 1
    rhs = (x * x * x + curve.a * x + curve.b) % curve.p
    stats["square_root_tests"] += 1
    y = square_root(rhs, curve.p)
    if y is None:
        return None
    point = (x, y)
    stats["subgroup_tests"] += 1
    if curve.mul(q, point, ops) is not None:
        return None
    if y == 0:
        return None
    return point


def generate_curve(bits: int, seed: int, max_attempts: int = 64) -> dict[str, Any]:
    p = find_field_prime(bits, seed ^ 0x9E3779B9)
    rng = random.Random((seed << 16) ^ bits ^ 0xC0DEC0DE)
    order_count_attempts = 0
    for attempt in range(1, max_attempts + 1):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        curve = Curve(p, a, b)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            continue
        order_count_attempts += 1
        order = curve_order(curve)
        trace = p + 1 - order
        if trace == 0:
            continue
        factors = prime_factors(order)
        q = max(factors)
        h = order // q
        if not is_prime(q) or q < p // 16 or h > 16:
            continue
        start = rng.randrange(p)
        generator: Point = None
        generator_source_x = None
        generator_ops = Ops()
        for offset in range(p):
            x = (start + offset) % p
            y = square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = curve.mul(h, (x, y), generator_ops)
            if candidate is not None and curve.mul(q, candidate, generator_ops) is None:
                generator = candidate
                generator_source_x = x
                break
        if generator is None:
            continue
        return {
            "id": f"toy-p{p}-a{a}-b{b}-q{q}",
            "bits": bits,
            "p": p,
            "a": a,
            "b": b,
            "order": order,
            "trace": trace,
            "q": q,
            "cofactor": h,
            "generator": list(generator),
            "generator_source_x": generator_source_x,
            "curve_attempts": attempt,
            "order_count_legendre_tests": order_count_attempts * p,
            "generator_ops": asdict(generator_ops),
            "p_minus_1_factors": prime_factors(p - 1),
        }
    raise RuntimeError(f"curve search exhausted at {bits} bits")


def canonical_fiber(curve: Curve, point: Point) -> list[Point]:
    assert point is not None
    x, y = point
    canonical = (x, min(y, (-y) % curve.p))
    return [canonical, curve.neg(canonical)]


def canonical_scalar(curve: Curve, q: int, scalar: int, point: Point) -> tuple[int, Point]:
    assert point is not None
    canonical = canonical_fiber(curve, point)[0]
    if point == canonical:
        return scalar % q, canonical
    return (-scalar) % q, canonical


def factor_base_size(q: int) -> int:
    size = max(8, int(round(q ** 0.2)))
    return size if size % 2 == 0 else size + 1


def make_factor_base(
    name: str,
    curve: Curve,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    fiber_count = size // 2
    ops = Ops()
    stats = {"x_candidates": 0, "square_root_tests": 0, "subgroup_tests": 0}
    fibers: list[dict[str, Any]] = []
    seen_x: set[int] = set()

    def append_point(point: Point, source: dict[str, Any]) -> None:
        assert point is not None
        pair = canonical_fiber(curve, point)
        x = pair[0][0]
        if x in seen_x:
            return
        seen_x.add(x)
        fibers.append(
            {
                "points": [list(pair[0]), list(pair[1])],
                "source": source,
            }
        )

    rng = random.Random(seed)
    if name == "random":
        for scalar in rng.sample(range(1, (q + 1) // 2), fiber_count):
            point = curve.mul(scalar, generator, ops)
            canonical_s, canonical = canonical_scalar(curve, q, scalar, point)
            append_point(
                canonical,
                {
                    "kind": "scalar",
                    "sampled_scalar": scalar,
                    "canonical_scalar": canonical_s,
                },
            )
    elif name == "scalar_progression_positive_control":
        scalar = 1
        while len(fibers) < fiber_count:
            point = curve.mul(scalar, generator, ops)
            canonical_s, canonical = canonical_scalar(curve, q, scalar, point)
            append_point(
                canonical,
                {
                    "kind": "scalar_progression",
                    "sampled_scalar": scalar,
                    "canonical_scalar": canonical_s,
                },
            )
            scalar += 1
    elif name == "x_interval":
        for x in range(curve.p):
            point = point_for_x(curve, q, x, ops, stats)
            if point is not None:
                append_point(point, {"kind": "x_interval", "x": x})
            if len(fibers) == fiber_count:
                break
    elif name == "square_map":
        c = rng.randrange(curve.p)
        for t in range(2 * curve.p):
            x = (t * t + c) % curve.p
            point = point_for_x(curve, q, x, ops, stats)
            if point is not None:
                append_point(
                    point,
                    {"kind": "square_map", "t": t, "c": c, "x": x},
                )
            if len(fibers) == fiber_count:
                break
    elif name == "rational_union":
        c = rng.randrange(curve.p)
        d = rng.randrange(curve.p)
        e = rng.randrange(curve.p)
        t = 0
        while t < 2 * curve.p and len(fibers) < fiber_count:
            candidates = [("square", (t * t + c) % curve.p)]
            denominator = (t + e) % curve.p
            if denominator:
                candidates.append(
                    ("mobius", (t + d) * pow(denominator, -1, curve.p) % curve.p)
                )
            for map_name, x in candidates:
                point = point_for_x(curve, q, x, ops, stats)
                if point is not None:
                    append_point(
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
        raise ValueError(f"unknown factor-base family: {name}")

    if len(fibers) != fiber_count:
        raise RuntimeError(f"{name} produced {len(fibers)} of {fiber_count} fibers")
    points = [point for fiber in fibers for point in fiber["points"]]
    return {
        "name": name,
        "size": len(points),
        "fibers": fibers,
        "points": points,
        "build_ops": asdict(ops),
        "build_diagnostics": stats,
    }


def _deep_size(value: Any, seen: set[int] | None = None) -> int:
    seen = seen or set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        size += sum(_deep_size(key, seen) + _deep_size(item, seen) for key, item in value.items())
    elif isinstance(value, (list, tuple, set, frozenset, Counter)):
        size += sum(_deep_size(item, seen) for item in value)
    return size


def serialize_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def deserialize_points(points: Iterable[list[int]]) -> list[Point]:
    return [(point[0], point[1]) for point in points]


def compile_family(
    curve: Curve,
    q: int,
    factor_base: dict[str, Any],
    targets: list[dict[str, Any]],
) -> dict[str, Any]:
    points = deserialize_points(factor_base["points"])
    compile_ops = Ops()
    pair_counts: Counter[Point] = Counter()
    pair_witness: dict[Point, tuple[int, int]] = {}
    for i, left in enumerate(points):
        for j, right in enumerate(points):
            total = curve.add(left, right, compile_ops)
            pair_counts[total] += 1
            pair_witness.setdefault(total, (i, j))

    three_counts: Counter[Point] = Counter()
    three_witness: dict[Point, tuple[int, int, int]] = {}
    for pair_sum, multiplicity in pair_counts.items():
        for k, point in enumerate(points):
            total = curve.add(pair_sum, point, compile_ops)
            three_counts[total] += multiplicity
            if total not in three_witness:
                i, j = pair_witness[pair_sum]
                three_witness[total] = (i, j, k)

    online_ops = Ops()
    representation_counts: list[int] = []
    first_witness: dict[str, Any] | None = None
    for target_index, target_record in enumerate(targets):
        target = tuple(target_record["point"])
        count = 0
        witness: tuple[int, int, int, int, int] | None = None
        for pair_sum, pair_multiplicity in pair_counts.items():
            complement = curve.add(target, curve.neg(pair_sum), online_ops)
            triple_multiplicity = three_counts.get(complement, 0)
            if triple_multiplicity:
                count += pair_multiplicity * triple_multiplicity
                if witness is None:
                    i, j = pair_witness[pair_sum]
                    k, ell, m = three_witness[complement]
                    witness = (i, j, k, ell, m)
        representation_counts.append(count)
        if witness is not None and first_witness is None:
            recovered: Point = None
            witness_ops = Ops()
            for index in witness:
                recovered = curve.add(recovered, points[index], witness_ops)
            if recovered != target:
                raise AssertionError("internal five-term witness did not recover target")
            first_witness = {
                "target_index": target_index,
                "indices": list(witness),
                "sum": serialize_point(recovered),
            }

    size = len(points)
    successes = sum(count > 0 for count in representation_counts)
    energy = sum(value * value for value in pair_counts.values())
    advice_entries = len(pair_counts) + len(three_counts)
    success_probability = successes / len(targets)
    online_per_target = online_ops.group_operations / len(targets)
    online_per_success = (
        online_ops.group_operations / successes if successes else None
    )
    epsilon = max(success_probability, 1 / len(targets))
    return {
        **factor_base,
        "pair_additive_energy": energy,
        "pair_sumset_size": len(pair_counts),
        "pair_max_multiplicity": max(pair_counts.values()),
        "three_sumset_size": len(three_counts),
        "three_max_multiplicity": max(three_counts.values()),
        "compiled_advice_entries": advice_entries,
        "compiled_storage_deep_bytes": _deep_size(pair_counts) + _deep_size(three_counts),
        "compile_ops": asdict(compile_ops),
        "offline_ops": {
            key: factor_base["build_ops"][key] + asdict(compile_ops)[key]
            for key in asdict(compile_ops)
        },
        "online_ops": asdict(online_ops),
        "online_group_operations_per_target": online_per_target,
        "online_group_operations_per_successful_target": online_per_success,
        "target_count": len(targets),
        "successful_targets": successes,
        "target_success_probability": success_probability,
        "representation_counts": representation_counts,
        "mean_representations_per_target": statistics.fmean(representation_counts),
        "first_witness": first_witness,
        "random_sum_lambda": size**5 / q,
        "random_sum_predicted_success": 1 - math.exp(-(size**5 / q)),
        "s_t_squared_over_q": advice_entries * online_per_target**2 / q,
        "s_t_squared_over_epsilon_q": advice_entries * online_per_target**2 / (epsilon * q),
    }


def rho_step(
    curve: Curve,
    q: int,
    generator: Point,
    target: Point,
    state: tuple[Point, int, int],
    salt: int,
    ops: Ops,
) -> tuple[Point, int, int]:
    point, a, b = state
    partition = salt % 3 if point is None else (point[0] + salt) % 3
    if partition == 0:
        return curve.add(point, generator, ops), (a + 1) % q, b
    if partition == 1:
        return curve.add(point, point, ops), (2 * a) % q, (2 * b) % q
    return curve.add(point, target, ops), a, (b + 1) % q


def pollard_rho(
    curve: Curve,
    q: int,
    generator: Point,
    target: Point,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    ops = Ops()
    max_steps = max(100, 20 * math.isqrt(q))
    for restart in range(32):
        a = rng.randrange(q)
        b = rng.randrange(q)
        state_point = curve.add(
            curve.mul(a, generator, ops), curve.mul(b, target, ops), ops
        )
        tortoise = (state_point, a, b)
        hare = tortoise
        salt = rng.randrange(q)
        for step in range(1, max_steps + 1):
            tortoise = rho_step(curve, q, generator, target, tortoise, salt, ops)
            hare = rho_step(curve, q, generator, target, hare, salt, ops)
            hare = rho_step(curve, q, generator, target, hare, salt, ops)
            if tortoise[0] != hare[0]:
                continue
            denominator = (tortoise[2] - hare[2]) % q
            if denominator == 0:
                break
            recovered = (hare[1] - tortoise[1]) * pow(denominator, -1, q) % q
            verified = curve.mul(recovered, generator) == target
            if verified:
                return {
                    "recovered_scalar": recovered,
                    "verified": True,
                    "restart": restart,
                    "cycle_steps": step,
                    "ops": asdict(ops),
                }
            break
    raise RuntimeError("Pollard rho exhausted deterministic restarts")


def fit_exponent(points: list[tuple[int, float]]) -> float | None:
    usable = [(q, cost) for q, cost in points if q > 1 and cost > 0]
    if len(usable) < 3:
        return None
    xs = [math.log2(q) for q, _ in usable]
    ys = [math.log2(cost) for _, cost in usable]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((x - x_mean) ** 2 for x in xs)
    if denominator == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def run_experiment(bit_sizes: list[int], seed: int, target_count: int, rho_trials: int) -> dict[str, Any]:
    if len(bit_sizes) < 1 or any(type(bits) is not int or bits < 8 for bits in bit_sizes):
        raise ValueError("bit sizes must be exact integers >= 8")
    if type(seed) is not int or type(target_count) is not int or type(rho_trials) is not int:
        raise ValueError("seed, target count, and rho trials must be exact integers")
    if target_count < 1 or rho_trials < 1:
        raise ValueError("target count and rho trials must be positive")
    families = [
        "random",
        "x_interval",
        "square_map",
        "rational_union",
        "scalar_progression_positive_control",
    ]
    instances: list[dict[str, Any]] = []
    for bits in bit_sizes:
        curve_record = generate_curve(bits, seed + bits * 1009)
        curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
        q = curve_record["q"]
        generator = tuple(curve_record["generator"])
        size = factor_base_size(q)
        target_rng = random.Random(seed ^ (bits << 24) ^ 0xA11CE)
        target_scalars: list[int] = []
        seen_scalars: set[int] = set()
        while len(target_scalars) < target_count:
            scalar = target_rng.randrange(1, q)
            if scalar not in seen_scalars:
                seen_scalars.add(scalar)
                target_scalars.append(scalar)
        targets = [
            {"scalar": scalar, "point": list(curve.mul(scalar, generator))}
            for scalar in target_scalars
        ]

        family_results = []
        for family_index, family in enumerate(families):
            factor_base = make_factor_base(
                family,
                curve,
                q,
                generator,
                size,
                seed ^ (bits << 20) ^ (family_index * 0x9E3779B1),
            )
            family_results.append(compile_family(curve, q, factor_base, targets))

        random_result = family_results[0]
        for result in family_results:
            random_success = random_result["target_success_probability"]
            result["pair_additive_energy_ratio_to_random"] = (
                result["pair_additive_energy"] / random_result["pair_additive_energy"]
            )
            result["five_term_target_success_ratio_to_random"] = (
                result["target_success_probability"] / random_success
                if random_success > 0
                else None
            )
            result["offline_group_operations_ratio_to_random"] = (
                result["offline_ops"]["group_operations"]
                / random_result["offline_ops"]["group_operations"]
            )
            random_online_success = random_result[
                "online_group_operations_per_successful_target"
            ]
            result["online_ops_per_success_ratio_to_random"] = (
                result["online_group_operations_per_successful_target"]
                / random_online_success
                if result["online_group_operations_per_successful_target"] is not None
                and random_online_success is not None
                else None
            )

        rho_results = []
        for index in range(rho_trials):
            target = tuple(targets[index % len(targets)]["point"])
            known_scalar = targets[index % len(targets)]["scalar"]
            result = pollard_rho(
                curve,
                q,
                generator,
                target,
                seed ^ (bits << 12) ^ index,
            )
            result["known_scalar"] = known_scalar
            result["target"] = list(target)
            if result["recovered_scalar"] != known_scalar:
                raise AssertionError("rho recovered a different scalar in a prime-order group")
            rho_results.append(result)
        instances.append(
            {
                "curve": curve_record,
                "factor_base_size": size,
                "targets": targets,
                "families": family_results,
                "rho": {
                    "trials": rho_results,
                    "median_group_operations": statistics.median(
                        trial["ops"]["group_operations"] for trial in rho_results
                    ),
                    "mean_group_operations": statistics.fmean(
                        trial["ops"]["group_operations"] for trial in rho_results
                    ),
                    "analytic_sqrt_q": math.sqrt(q),
                },
            }
        )

    coordinate_families = ["x_interval", "square_map", "rational_union"]
    promotion_counts = {name: 0 for name in coordinate_families}
    family_fits: dict[str, Any] = {}
    for name in families:
        rows = [
            next(item for item in instance["families"] if item["name"] == name)
            for instance in instances
        ]
        family_fits[name] = {
            "offline_group_operations_exponent": fit_exponent(
                [
                    (instance["curve"]["q"], row["offline_ops"]["group_operations"])
                    for instance, row in zip(instances, rows)
                ]
            ),
            "online_group_operations_per_target_exponent": fit_exponent(
                [
                    (instance["curve"]["q"], row["online_group_operations_per_target"])
                    for instance, row in zip(instances, rows)
                ]
            ),
            "amortized_total_group_operations_per_target_exponent": fit_exponent(
                [
                    (
                        instance["curve"]["q"],
                        row["offline_ops"]["group_operations"] / target_count
                        + row["online_group_operations_per_target"],
                    )
                    for instance, row in zip(instances, rows)
                ]
            ),
            "interpretation": "exploratory toy fit; not an asymptotic claim",
        }
    for instance in instances:
        for result in instance["families"]:
            if result["name"] not in promotion_counts:
                continue
            if (
                result["pair_additive_energy_ratio_to_random"] >= 2.0
                and result["five_term_target_success_ratio_to_random"] is not None
                and result["five_term_target_success_ratio_to_random"] >= 1.5
                and result["offline_group_operations_ratio_to_random"] <= 4.0
            ):
                promotion_counts[result["name"]] += 1
    promoted = [name for name, count in promotion_counts.items() if count >= 2]
    return {
        "protocol": "EXP-ECDLP-ENERGY-001-v1",
        "claim_status": ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"],
        "valid": True,
        "config": {
            "bit_sizes": bit_sizes,
            "seed": seed,
            "target_count": target_count,
            "rho_trials": rho_trials,
            "families": families,
        },
        "instances": instances,
        "summary": {
            "sizes_completed": len(instances),
            "all_rho_trials_verified": all(
                trial["verified"]
                for instance in instances
                for trial in instance["rho"]["trials"]
            ),
            "promotion_counts": promotion_counts,
            "promoted_coordinate_families": promoted,
            "preflight_gate_passed": bool(promoted),
            "family_fits": family_fits,
            "breakthrough_claim": False,
            "boundary": "No exponent or deployment claim is justified by this toy preflight.",
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bit-sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--targets", type=int, default=128)
    parser.add_argument("--rho-trials", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_experiment(args.bit_sizes, args.seed, args.targets, args.rho_trials)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
