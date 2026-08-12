#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None


@dataclass
class VerifyOps:
    group_operations: int = 0
    point_additions: int = 0
    point_doublings: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} must be an exact integer, got {type(value).__name__}")
    if minimum is not None and value < minimum:
        raise AssertionError(f"{label} is below {minimum}")
    return value


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    for prime in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value % prime == 0:
            return value == prime
    odd = value - 1
    powers = 0
    while odd % 2 == 0:
        odd //= 2
        powers += 1
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


def find_field_prime(bits: int, seed: int) -> int:
    span = max(1, 1 << max(1, bits - 5))
    candidate = (1 << bits) - 1 - 2 * (seed % span)
    candidate -= (candidate - 3) % 4
    lower = 1 << (bits - 1)
    while candidate >= lower:
        if is_prime(candidate):
            return candidate
        candidate -= 4
    raise AssertionError("seed-derived field-prime search failed")


def on_curve(point: Point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return 0 <= x < p and 0 <= y < p and (y * y - x * x * x - a * x - b) % p == 0


def neg(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def add(left: Point, right: Point, p: int, a: int, ops: VerifyOps | None = None) -> Point:
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


def mul(scalar: int, point: Point, p: int, a: int, ops: VerifyOps | None = None) -> Point:
    if scalar < 0:
        return mul(-scalar, neg(point, p), p, a, ops)
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = add(result, addend, p, a, ops)
        scalar >>= 1
        if scalar:
            addend = add(addend, addend, p, a, ops)
    return result


def curve_order(p: int, a: int, b: int) -> int:
    order = 1
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            order += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            order += 2
    return order


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


def replay_curve_selection(bits: int, selection_seed: int, record: dict[str, Any]) -> None:
    p = find_field_prime(bits, selection_seed ^ 0x9E3779B9)
    if p != record["p"]:
        raise AssertionError("seed-derived field prime mismatch")
    rng = random.Random((selection_seed << 16) ^ bits ^ 0xC0DEC0DE)
    expected_attempt = exact_int(record["curve_attempts"], "curve.curve_attempts", 1)
    order_count_attempts = 0
    for attempt in range(1, expected_attempt + 1):
        a = rng.randrange(1, p)
        b = rng.randrange(1, p)
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            if attempt == expected_attempt:
                raise AssertionError("selected curve attempt is singular")
            continue
        order_count_attempts += 1
        order = curve_order(p, a, b)
        trace = p + 1 - order
        factors = prime_factors(order)
        q = max(factors)
        cofactor = order // q
        eligible = trace != 0 and is_prime(q) and q >= p // 16 and cofactor <= 16
        if attempt < expected_attempt and eligible:
            raise AssertionError("reported curve was not the first eligible seeded instance")
        if attempt != expected_attempt:
            continue
        expected_fields = {
            "a": a,
            "b": b,
            "order": order,
            "trace": trace,
            "q": q,
            "cofactor": cofactor,
        }
        for key, expected in expected_fields.items():
            if record[key] != expected:
                raise AssertionError(f"seed-derived curve field {key} mismatch")
        if not eligible:
            raise AssertionError("reported seeded curve does not meet eligibility rules")
        generator_ops = VerifyOps()
        start = rng.randrange(p)
        recovered_generator: Point = None
        recovered_source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = mul(cofactor, (x, y), p, a, generator_ops)
            if candidate is not None and mul(q, candidate, p, a, generator_ops) is None:
                recovered_generator = candidate
                recovered_source_x = x
                break
        if recovered_generator is None:
            raise AssertionError("seeded generator scan failed")
        if point_list(record["generator"], "curve.generator") != recovered_generator:
            raise AssertionError("seed-derived generator mismatch")
        if record["generator_source_x"] != recovered_source_x:
            raise AssertionError("generator source x mismatch")
        if record["generator_ops"] != asdict(generator_ops):
            raise AssertionError("generator operation counters mismatch")
        if record["order_count_legendre_tests"] != order_count_attempts * p:
            raise AssertionError("curve-order Legendre-test count mismatch")
        if record["p_minus_1_factors"] != prime_factors(p - 1):
            raise AssertionError("p-1 factorization diagnostic mismatch")
        expected_id = f"toy-p{p}-a{a}-b{b}-q{q}"
        if record["id"] != expected_id:
            raise AssertionError("curve identifier mismatch")
        return
    raise AssertionError("curve selection replay did not reach reported attempt")


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
    if mul(q, point, p, a, ops) is not None or y == 0:
        return None
    return point


def canonical_pair(point: Point, p: int) -> list[Point]:
    assert point is not None
    canonical = (point[0], min(point[1], (-point[1]) % p))
    return [canonical, neg(canonical, p)]


def point_list(value: Any, label: str) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise AssertionError(f"{label} is not a two-coordinate point")
    return exact_int(value[0], f"{label}.x"), exact_int(value[1], f"{label}.y")


def replay_factor_base(
    family: dict[str, Any],
    p: int,
    a: int,
    b: int,
    q: int,
    generator: Point,
    family_seed: int,
) -> tuple[list[Point], VerifyOps, dict[str, int]]:
    name = family["name"]
    expected_fibers = family["fibers"]
    fiber_count = exact_int(family["size"], f"{name}.size", 2) // 2
    if len(expected_fibers) != fiber_count:
        raise AssertionError(f"{name}: fiber count mismatch")
    ops = VerifyOps()
    diagnostics = {"x_candidates": 0, "square_root_tests": 0, "subgroup_tests": 0}
    replayed: list[tuple[Point, dict[str, Any]]] = []
    seen_x: set[int] = set()

    def append(point: Point, source: dict[str, Any]) -> None:
        assert point is not None
        canonical = canonical_pair(point, p)[0]
        if canonical[0] in seen_x:
            return
        seen_x.add(canonical[0])
        replayed.append((canonical, source))

    rng = random.Random(family_seed)
    if name == "random":
        expected_scalars = rng.sample(range(1, (q + 1) // 2), fiber_count)
        for index, fiber in enumerate(expected_fibers):
            source = fiber["source"]
            sampled = exact_int(source["sampled_scalar"], f"{name}.sampled_scalar", 1)
            if sampled != expected_scalars[index]:
                raise AssertionError(f"{name}: seed-derived scalar schedule mismatch")
            point = mul(sampled, generator, p, a, ops)
            append(point, source)
    elif name == "scalar_progression_positive_control":
        for index, fiber in enumerate(expected_fibers):
            source = fiber["source"]
            sampled = exact_int(source["sampled_scalar"], f"{name}.sampled_scalar", 1)
            if sampled != index + 1:
                raise AssertionError(f"{name}: progression schedule mismatch")
            point = mul(sampled, generator, p, a, ops)
            append(point, source)
    elif name == "x_interval":
        last_x = exact_int(expected_fibers[-1]["source"]["x"], "x_interval.last_x")
        for x in range(last_x + 1):
            point = point_for_x(p, a, b, q, x, ops, diagnostics)
            if point is not None:
                append(point, {"kind": "x_interval", "x": x})
            if len(replayed) == fiber_count:
                break
    elif name == "square_map":
        c = rng.randrange(p)
        last_t = exact_int(expected_fibers[-1]["source"]["t"], "square_map.last_t")
        for t in range(last_t + 1):
            x = (t * t + c) % p
            point = point_for_x(p, a, b, q, x, ops, diagnostics)
            if point is not None:
                append(point, {"kind": "square_map", "t": t, "c": c, "x": x})
            if len(replayed) == fiber_count:
                break
    elif name == "rational_union":
        c = rng.randrange(p)
        d = rng.randrange(p)
        e = rng.randrange(p)
        last_t = exact_int(expected_fibers[-1]["source"]["t"], "rational_union.last_t")
        for t in range(last_t + 1):
            candidates = [("square", (t * t + c) % p)]
            denominator = (t + e) % p
            if denominator:
                candidates.append(("mobius", (t + d) * pow(denominator, -1, p) % p))
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
                if len(replayed) == fiber_count:
                    break
            if len(replayed) == fiber_count:
                break
    else:
        raise AssertionError(f"unknown family {name!r}")

    if len(replayed) != fiber_count:
        raise AssertionError(f"{name}: replay did not recover all fibers")
    flattened: list[Point] = []
    for index, ((canonical, expected_source), expected) in enumerate(zip(replayed, expected_fibers)):
        actual_points = [point_list(item, f"{name}.fibers[{index}]") for item in expected["points"]]
        if actual_points != canonical_pair(canonical, p):
            raise AssertionError(f"{name}: noncanonical or non-sign-complete fiber {index}")
        source = expected["source"]
        if source != expected_source:
            raise AssertionError(f"{name}: source witness mismatch at fiber {index}")
        if name in ("random", "scalar_progression_positive_control"):
            canonical_scalar = exact_int(
                source["canonical_scalar"], f"{name}.canonical_scalar", 1
            )
            if mul(canonical_scalar, generator, p, a) != canonical:
                raise AssertionError(f"{name}: canonical scalar witness failed")
        flattened.extend(actual_points)
    reported_points = [point_list(item, f"{name}.points") for item in family["points"]]
    if flattened != reported_points:
        raise AssertionError(f"{name}: flattened points do not match fibers")
    return flattened, ops, diagnostics


def verify_family(
    family: dict[str, Any],
    p: int,
    a: int,
    b: int,
    q: int,
    generator: Point,
    targets: list[dict[str, Any]],
    family_seed: int,
) -> dict[str, Any]:
    name = family["name"]
    points, build_ops, diagnostics = replay_factor_base(
        family, p, a, b, q, generator, family_seed
    )
    if asdict(build_ops) != family["build_ops"]:
        raise AssertionError(f"{name}: build operation counters disagree")
    if diagnostics != family["build_diagnostics"]:
        raise AssertionError(f"{name}: build diagnostics disagree")
    for point in points:
        if not on_curve(point, p, a, b) or mul(q, point, p, a) is not None:
            raise AssertionError(f"{name}: point is outside claimed subgroup")

    compile_ops = VerifyOps()
    pairs: Counter[Point] = Counter()
    pair_witness: dict[Point, tuple[int, int]] = {}
    for i, left in enumerate(points):
        for j, right in enumerate(points):
            total = add(left, right, p, a, compile_ops)
            pairs[total] += 1
            pair_witness.setdefault(total, (i, j))
    triples: Counter[Point] = Counter()
    triple_witness: dict[Point, tuple[int, int, int]] = {}
    for pair_sum, multiplicity in pairs.items():
        for k, point in enumerate(points):
            total = add(pair_sum, point, p, a, compile_ops)
            triples[total] += multiplicity
            if total not in triple_witness:
                i, j = pair_witness[pair_sum]
                triple_witness[total] = (i, j, k)
    if asdict(compile_ops) != family["compile_ops"]:
        raise AssertionError(f"{name}: compile operation counters disagree")
    expected_offline_ops = {
        key: asdict(build_ops)[key] + asdict(compile_ops)[key]
        for key in asdict(compile_ops)
    }
    if family["offline_ops"] != expected_offline_ops:
        raise AssertionError(f"{name}: offline operation totals disagree")

    exact_metrics = {
        "pair_additive_energy": sum(value * value for value in pairs.values()),
        "pair_sumset_size": len(pairs),
        "pair_max_multiplicity": max(pairs.values()),
        "three_sumset_size": len(triples),
        "three_max_multiplicity": max(triples.values()),
        "compiled_advice_entries": len(pairs) + len(triples),
    }
    for key, expected in exact_metrics.items():
        if exact_int(family[key], f"{name}.{key}") != expected:
            raise AssertionError(f"{name}: {key} mismatch")
    exact_int(
        family["compiled_storage_deep_bytes"],
        f"{name}.compiled_storage_deep_bytes",
        1,
    )

    online_ops = VerifyOps()
    representation_counts: list[int] = []
    for target_record in targets:
        target = point_list(target_record["point"], "target.point")
        count = 0
        for pair_sum, pair_multiplicity in pairs.items():
            complement = add(target, neg(pair_sum, p), p, a, online_ops)
            count += pair_multiplicity * triples.get(complement, 0)
        representation_counts.append(count)
    if representation_counts != family["representation_counts"]:
        raise AssertionError(f"{name}: five-term representation counts disagree")
    if asdict(online_ops) != family["online_ops"]:
        raise AssertionError(f"{name}: online operation counters disagree")
    successes = sum(value > 0 for value in representation_counts)
    if successes != exact_int(family["successful_targets"], f"{name}.successful_targets"):
        raise AssertionError(f"{name}: target success count mismatch")

    witness = family["first_witness"]
    if successes == 0 and witness is not None:
        raise AssertionError(f"{name}: witness exists with no successful target")
    if witness is not None:
        target_index = exact_int(witness["target_index"], f"{name}.witness.target_index", 0)
        indices = [exact_int(item, f"{name}.witness.index", 0) for item in witness["indices"]]
        if len(indices) != 5 or any(index >= len(points) for index in indices):
            raise AssertionError(f"{name}: invalid witness indices")
        recovered: Point = None
        for index in indices:
            recovered = add(recovered, points[index], p, a)
        target = point_list(targets[target_index]["point"], "witness.target")
        if recovered != target or point_list(witness["sum"], "witness.sum") != target:
            raise AssertionError(f"{name}: five-term witness failed")
    target_count = len(targets)
    success_probability = successes / target_count
    online_per_target = online_ops.group_operations / target_count
    online_per_success = online_ops.group_operations / successes if successes else None
    expected_floats = {
        "target_success_probability": success_probability,
        "mean_representations_per_target": statistics.fmean(representation_counts),
        "online_group_operations_per_target": online_per_target,
        "random_sum_lambda": len(points) ** 5 / q,
        "random_sum_predicted_success": 1 - math.exp(-(len(points) ** 5 / q)),
    }
    for key, expected in expected_floats.items():
        if not math.isclose(family[key], expected, rel_tol=0, abs_tol=1e-15):
            raise AssertionError(f"{name}: {key} mismatch")
    if family["online_group_operations_per_successful_target"] != online_per_success:
        raise AssertionError(f"{name}: online cost per success mismatch")
    if exact_int(family["target_count"], f"{name}.target_count", 1) != target_count:
        raise AssertionError(f"{name}: target count field mismatch")
    advice_entries = exact_metrics["compiled_advice_entries"]
    epsilon = max(success_probability, 1 / target_count)
    tradeoffs = {
        "s_t_squared_over_q": advice_entries * online_per_target**2 / q,
        "s_t_squared_over_epsilon_q": advice_entries * online_per_target**2 / (epsilon * q),
    }
    for key, expected in tradeoffs.items():
        if not math.isclose(family[key], expected, rel_tol=0, abs_tol=1e-12):
            raise AssertionError(f"{name}: {key} mismatch")
    return {
        "name": name,
        "factor_points": len(points),
        "pair_sums": len(pairs),
        "triple_sums": len(triples),
        "successful_targets": successes,
        "integer_counts_verified": True,
    }


def rho_step(
    p: int,
    a_curve: int,
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
        return add(point, generator, p, a_curve, ops), (a_scalar + 1) % q, b_scalar
    if partition == 1:
        return (
            add(point, point, p, a_curve, ops),
            (2 * a_scalar) % q,
            (2 * b_scalar) % q,
        )
    return add(point, target, p, a_curve, ops), a_scalar, (b_scalar + 1) % q


def replay_rho(
    p: int,
    a_curve: int,
    q: int,
    generator: Point,
    target: Point,
    seed: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    ops = VerifyOps()
    max_steps = max(100, 20 * math.isqrt(q))
    for restart in range(32):
        a_scalar = rng.randrange(q)
        b_scalar = rng.randrange(q)
        state_point = add(
            mul(a_scalar, generator, p, a_curve, ops),
            mul(b_scalar, target, p, a_curve, ops),
            p,
            a_curve,
            ops,
        )
        tortoise = (state_point, a_scalar, b_scalar)
        hare = tortoise
        salt = rng.randrange(q)
        for cycle_steps in range(1, max_steps + 1):
            tortoise = rho_step(
                p, a_curve, q, generator, target, tortoise, salt, ops
            )
            hare = rho_step(p, a_curve, q, generator, target, hare, salt, ops)
            hare = rho_step(p, a_curve, q, generator, target, hare, salt, ops)
            if tortoise[0] != hare[0]:
                continue
            denominator = (tortoise[2] - hare[2]) % q
            if denominator == 0:
                break
            recovered = (
                (hare[1] - tortoise[1]) * pow(denominator, -1, q) % q
            )
            if mul(recovered, generator, p, a_curve) == target:
                return {
                    "recovered_scalar": recovered,
                    "verified": True,
                    "restart": restart,
                    "cycle_steps": cycle_steps,
                    "ops": asdict(ops),
                }
            break
    raise AssertionError("independent Pollard-rho replay exhausted restarts")


def expected_factor_base_size(q: int) -> int:
    size = max(8, int(round(q ** 0.2)))
    return size if size % 2 == 0 else size + 1


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


def verify_document(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("protocol") != "EXP-ECDLP-ENERGY-001-v1":
        raise AssertionError("unexpected protocol")
    if document.get("valid") is not True:
        raise AssertionError("generator did not declare a valid result")
    config = document["config"]
    bit_sizes = config["bit_sizes"]
    base_seed = exact_int(config["seed"], "config.seed")
    target_count = exact_int(config["target_count"], "config.target_count", 1)
    rho_trial_count = exact_int(config["rho_trials"], "config.rho_trials", 1)
    expected_families = [
        "random",
        "x_interval",
        "square_map",
        "rational_union",
        "scalar_progression_positive_control",
    ]
    if config["families"] != expected_families:
        raise AssertionError("factor-base family schedule mismatch")
    if any(type(value) is not int for value in bit_sizes):
        raise AssertionError("bit sizes are not exact integers")
    if len(document["instances"]) != len(bit_sizes):
        raise AssertionError("instance count does not match bit-size schedule")

    verified_instances = []
    for expected_bits, instance in zip(bit_sizes, document["instances"]):
        record = instance["curve"]
        p = exact_int(record["p"], "curve.p", 3)
        a = exact_int(record["a"], "curve.a", 0)
        b = exact_int(record["b"], "curve.b", 0)
        order = exact_int(record["order"], "curve.order", 2)
        q = exact_int(record["q"], "curve.q", 2)
        cofactor = exact_int(record["cofactor"], "curve.cofactor", 1)
        bits = exact_int(record["bits"], "curve.bits", 8)
        if bits != expected_bits or p.bit_length() != bits:
            raise AssertionError("curve bit size mismatch")
        replay_curve_selection(bits, base_seed + bits * 1009, record)
        if p % 4 != 3 or not is_prime(p) or not is_prime(q):
            raise AssertionError("field or subgroup modulus is not prime as claimed")
        if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
            raise AssertionError("singular curve")
        independent_order = curve_order(p, a, b)
        if (
            independent_order != order
            or order != cofactor * q
            or q < p // 16
            or cofactor > 16
        ):
            raise AssertionError("curve order or large-subgroup condition failed")
        if exact_int(record["trace"], "curve.trace") != p + 1 - order:
            raise AssertionError("curve trace mismatch")
        if p + 1 - order == 0:
            raise AssertionError("supersingular trace-zero curve")
        generator = point_list(record["generator"], "curve.generator")
        if not on_curve(generator, p, a, b) or generator is None or mul(q, generator, p, a) is not None:
            raise AssertionError("generator failed subgroup verification")

        targets = instance["targets"]
        if len(targets) != target_count:
            raise AssertionError("target count mismatch")
        target_rng = random.Random(base_seed ^ (bits << 24) ^ 0xA11CE)
        expected_target_scalars: list[int] = []
        seen_target_scalars: set[int] = set()
        while len(expected_target_scalars) < target_count:
            candidate = target_rng.randrange(1, q)
            if candidate not in seen_target_scalars:
                seen_target_scalars.add(candidate)
                expected_target_scalars.append(candidate)
        for index, target_record in enumerate(targets):
            scalar = exact_int(target_record["scalar"], f"targets[{index}].scalar", 1)
            point = point_list(target_record["point"], f"targets[{index}].point")
            if (
                scalar >= q
                or scalar != expected_target_scalars[index]
                or mul(scalar, generator, p, a) != point
            ):
                raise AssertionError(f"target {index} scalar witness failed")

        if exact_int(instance["factor_base_size"], "factor_base_size", 2) != expected_factor_base_size(q):
            raise AssertionError("factor-base size schedule mismatch")
        if [family["name"] for family in instance["families"]] != expected_families:
            raise AssertionError("instance family order mismatch")
        family_checks = []
        for family_index, family in enumerate(instance["families"]):
            family_seed = base_seed ^ (bits << 20) ^ (family_index * 0x9E3779B1)
            family_checks.append(
                verify_family(
                    family,
                    p,
                    a,
                    b,
                    q,
                    generator,
                    targets,
                    family_seed,
                )
            )
        random_family = instance["families"][0]
        if random_family["name"] != "random":
            raise AssertionError("first family is not the random control")
        random_energy = random_family["pair_additive_energy"]
        random_success = random_family["target_success_probability"]
        random_offline = random_family["offline_ops"]["group_operations"]
        random_online_success = random_family[
            "online_group_operations_per_successful_target"
        ]
        for family in instance["families"]:
            expected_energy_ratio = family["pair_additive_energy"] / random_energy
            if not math.isclose(
                family["pair_additive_energy_ratio_to_random"], expected_energy_ratio, rel_tol=0, abs_tol=1e-15
            ):
                raise AssertionError(f"{family['name']}: energy ratio mismatch")
            expected_success_ratio = (
                family["target_success_probability"] / random_success if random_success > 0 else None
            )
            if family["five_term_target_success_ratio_to_random"] != expected_success_ratio:
                raise AssertionError(f"{family['name']}: target success ratio mismatch")
            expected_offline_ratio = family["offline_ops"]["group_operations"] / random_offline
            if not math.isclose(
                family["offline_group_operations_ratio_to_random"], expected_offline_ratio, rel_tol=0, abs_tol=1e-15
            ):
                raise AssertionError(f"{family['name']}: offline ratio mismatch")
            family_online_success = family[
                "online_group_operations_per_successful_target"
            ]
            expected_online_ratio = (
                family_online_success / random_online_success
                if family_online_success is not None and random_online_success is not None
                else None
            )
            if family["online_ops_per_success_ratio_to_random"] != expected_online_ratio:
                raise AssertionError(f"{family['name']}: online success-cost ratio mismatch")

        rho_trials = instance["rho"]["trials"]
        if len(rho_trials) != rho_trial_count:
            raise AssertionError("rho trial count mismatch")
        rho_checks = []
        for trial_index, trial in enumerate(rho_trials):
            known = exact_int(trial["known_scalar"], "rho.known_scalar", 1)
            recovered = exact_int(trial["recovered_scalar"], "rho.recovered_scalar", 0)
            target = point_list(trial["target"], "rho.target")
            replayed = replay_rho(
                p,
                a,
                q,
                generator,
                target,
                base_seed ^ (bits << 12) ^ trial_index,
            )
            expected_trial = {
                **replayed,
                "known_scalar": expected_target_scalars[trial_index % target_count],
                "target": list(target),
            }
            if trial != expected_trial:
                raise AssertionError("rho deterministic replay mismatch")
            if recovered != known or mul(recovered, generator, p, a) != target:
                raise AssertionError("rho scalar did not verify")
            if trial["verified"] is not True:
                raise AssertionError("rho verified flag is not exact true")
            rho_checks.append({"known_scalar": known, "verified": True})
        group_operation_counts = [
            trial["ops"]["group_operations"] for trial in rho_trials
        ]
        if instance["rho"]["median_group_operations"] != statistics.median(group_operation_counts):
            raise AssertionError("rho median operation count mismatch")
        if not math.isclose(
            instance["rho"]["mean_group_operations"],
            statistics.fmean(group_operation_counts),
            rel_tol=0,
            abs_tol=1e-15,
        ):
            raise AssertionError("rho mean operation count mismatch")
        if not math.isclose(
            instance["rho"]["analytic_sqrt_q"], math.sqrt(q), rel_tol=0, abs_tol=1e-15
        ):
            raise AssertionError("rho analytic sqrt(q) mismatch")
        verified_instances.append(
            {
                "curve_id": record["id"],
                "p": p,
                "q": q,
                "order_recomputed": independent_order,
                "families": family_checks,
                "rho_trials": rho_checks,
            }
        )

    promotion_counts = {"x_interval": 0, "square_map": 0, "rational_union": 0}
    for instance in document["instances"]:
        for family in instance["families"]:
            if family["name"] not in promotion_counts:
                continue
            if (
                family["pair_additive_energy_ratio_to_random"] >= 2.0
                and family["five_term_target_success_ratio_to_random"] is not None
                and family["five_term_target_success_ratio_to_random"] >= 1.5
                and family["offline_group_operations_ratio_to_random"] <= 4.0
            ):
                promotion_counts[family["name"]] += 1
    promoted = sorted(name for name, count in promotion_counts.items() if count >= 2)
    summary = document["summary"]
    if exact_int(summary["sizes_completed"], "summary.sizes_completed", 1) != len(
        document["instances"]
    ):
        raise AssertionError("summary completed-size count mismatch")
    if summary["all_rho_trials_verified"] is not True:
        raise AssertionError("summary rho verification flag is not exact true")
    if summary["promotion_counts"] != promotion_counts:
        raise AssertionError("summary promotion counts mismatch")
    if sorted(summary["promoted_coordinate_families"]) != promoted:
        raise AssertionError("summary promoted-family list mismatch")
    if summary["preflight_gate_passed"] is not bool(promoted):
        raise AssertionError("summary preflight gate mismatch")
    if summary["breakthrough_claim"] is not False:
        raise AssertionError("toy result asserted a breakthrough claim")
    expected_fits: dict[str, Any] = {}
    for name in expected_families:
        rows = [
            next(family for family in instance["families"] if family["name"] == name)
            for instance in document["instances"]
        ]
        expected_fits[name] = {
            "offline_group_operations_exponent": fit_exponent(
                [
                    (instance["curve"]["q"], row["offline_ops"]["group_operations"])
                    for instance, row in zip(document["instances"], rows)
                ]
            ),
            "online_group_operations_per_target_exponent": fit_exponent(
                [
                    (
                        instance["curve"]["q"],
                        row["online_group_operations_per_target"],
                    )
                    for instance, row in zip(document["instances"], rows)
                ]
            ),
            "amortized_total_group_operations_per_target_exponent": fit_exponent(
                [
                    (
                        instance["curve"]["q"],
                        row["offline_ops"]["group_operations"] / target_count
                        + row["online_group_operations_per_target"],
                    )
                    for instance, row in zip(document["instances"], rows)
                ]
            ),
            "interpretation": "exploratory toy fit; not an asymptotic claim",
        }
    if summary["family_fits"] != expected_fits:
        raise AssertionError("summary fitted exponents mismatch")
    return {
        "valid": True,
        "protocol": "EXP-ECDLP-ENERGY-001-v1-independent-verifier",
        "summary": {
            "instances_verified": len(verified_instances),
            "integer_counts_verified": True,
            "curve_orders_recomputed": True,
            "factor_base_sources_replayed": True,
            "five_term_witnesses_verified": True,
            "rho_outputs_verified": True,
            "promotion_counts": promotion_counts,
            "promoted_coordinate_families": promoted,
            "preflight_gate_passed": bool(promoted),
            "breakthrough_claim": False,
            "boundary": "Independent arithmetic verification of toy evidence only.",
        },
        "instances": verified_instances,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = args.input.read_bytes()
    document = json.loads(raw)
    result = verify_document(document)
    result["input"] = {
        "path": str(args.input),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
