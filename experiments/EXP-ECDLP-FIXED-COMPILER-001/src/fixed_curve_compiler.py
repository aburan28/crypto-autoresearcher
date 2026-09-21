#!/usr/bin/env python3
"""Fixed-curve five-term relation compiler for authorized toy ECDLP research."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import math
import random
import statistics
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


PROTOCOL = "EXP-ECDLP-FIXED-COMPILER-001-development-v1"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
ENERGY_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-ENERGY-001"
    / "src"
    / "coordinate_energy.py"
)
CONTRACT_PATH = SCRIPT_PATH.parents[1] / "contract.md"
HYPOTHESIS_PATH = SCRIPT_PATH.parents[1] / "hypothesis.json"
LITERATURE_PATH = (
    REPO_ROOT
    / "notes"
    / "structured_group_coordinate_predicates_literature_20260717.md"
)
CANDIDATE_FAMILIES = ["x_interval", "square_map", "rational_union"]
NULL_FAMILIES = ["random_x", "random_scalar"]
POSITIVE_CONTROL = "scalar_progression"
ALL_FAMILIES = CANDIDATE_FAMILIES + NULL_FAMILIES + [POSITIVE_CONTROL]
FROZEN_CONFIG = {
    "bit_sizes": [12, 14, 16],
    "seeds": [3571001, 3571009, 3571021],
    "families": ALL_FAMILIES,
    "witness_caps": [1, 4],
    "occupancy_lambda": 0.5,
    "relations_per_target": 16,
    "relation_target_budget": 0,
    "descent_challenges": 4,
    "descent_attempt_limit": 128,
    "rho_trials": 2,
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def stable_digest(value: Any) -> str:
    return hashlib.sha256(stable_json_bytes(value)).hexdigest()


def load_energy_module() -> Any:
    spec = importlib.util.spec_from_file_location("fixed_compiler_energy", ENERGY_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load arithmetic source: {ENERGY_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ENERGY = load_energy_module()
Curve = ENERGY.Curve
Ops = ENERGY.Ops
Point = tuple[int, int] | None


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise TypeError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def exact_int_list(values: Iterable[int], label: str, minimum: int) -> list[int]:
    result = [exact_int(value, f"{label}[{index}]", minimum) for index, value in enumerate(values)]
    if not result:
        raise ValueError(f"{label} must not be empty")
    if len(result) != len(set(result)):
        raise ValueError(f"{label} must not contain duplicates")
    return result


def exact_probability(value: Any, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise TypeError(f"{label} must be a finite real number")
    result = float(value)
    if not 0.0 < result <= 1.0:
        raise ValueError(f"{label} must lie in (0,1]")
    return result


def deep_size(value: Any, seen: set[int] | None = None) -> int:
    if seen is None:
        seen = set()
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    size = sys.getsizeof(value)
    if isinstance(value, dict):
        return size + sum(
            deep_size(key, seen) + deep_size(item, seen)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set, frozenset)):
        return size + sum(deep_size(item, seen) for item in value)
    return size


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_from_json(value: list[int] | None) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ValueError("point must be null or a two-coordinate list")
    return exact_int(value[0], "point.x", 0), exact_int(value[1], "point.y", 0)


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def j_invariant(p: int, a: int, b: int) -> int:
    four_a3 = 4 * pow(a, 3, p) % p
    denominator = (four_a3 + 27 * pow(b, 2, p)) % p
    if denominator == 0:
        raise ValueError("singular curve")
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


def generate_clean_curve(bits: int, seed: int, max_attempts: int = 256) -> dict[str, Any]:
    exact_int(bits, "bits", 5)
    exact_int(seed, "seed", 0)
    p = ENERGY.find_field_prime(bits, seed ^ 0x6A09E667)
    rng = random.Random((seed << 17) ^ bits ^ 0xA54FF53A)
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
        generator_ops = Ops()
        start = rng.randrange(p)
        generator: Point = None
        source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = ENERGY.square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = (x, y)
            if curve.mul(order, candidate, generator_ops) is None:
                generator = candidate
                source_x = x
                break
        if generator is None:
            continue
        factors = ENERGY.prime_factors(p - 1)
        return {
            "id": f"fixed-compiler-toy-p{p}-a{a}-b{b}-q{order}",
            "bits": bits,
            "p": p,
            "p_mod_4": p % 4,
            "field_modulus_policy": (
                "first seeded bits-bit prime constrained to p mod 4 = 3; "
                "no selection on p-1 smoothness"
            ),
            "a": a,
            "b": b,
            "j_invariant": j_invariant(p, a, b),
            "order": order,
            "trace": p + 1 - order,
            "q": order,
            "cofactor": 1,
            "generator": point_json(generator),
            "generator_source_x": source_x,
            "curve_attempts": attempt,
            "order_count_legendre_tests": counted_orders * p,
            "generator_ops": asdict(generator_ops),
            "p_minus_1_factors": factors,
            "p_minus_1_largest_prime_factor": max(factors),
            "rejections": rejections,
            "selection_policy": (
                "first seeded nonsingular prime-order curve with trace not in "
                "{0,1} and j not in {0,1728}"
            ),
        }
    raise RuntimeError(f"clean prime-order curve search exhausted at {bits} bits")


def signed_class_count(fiber_count: int, terms: int) -> int:
    total = 0
    for residue_terms in range(terms % 2, terms + 1, 2):
        for support_size in range(1, min(fiber_count, residue_terms) + 1):
            total += (
                math.comb(fiber_count, support_size)
                * math.comb(residue_terms - 1, support_size - 1)
                * 2**support_size
            )
    return total


def choose_factor_base_size(q: int, occupancy_lambda: float) -> int:
    fiber_count = 1
    while signed_class_count(fiber_count, 5) / q < occupancy_lambda:
        fiber_count += 1
    return 2 * fiber_count


def binary_pow_field_multiplications(exponent: int) -> int:
    if exponent < 1:
        return 0
    return exponent.bit_length() - 1 + exponent.bit_count() - 1


def charged_build_diagnostics(factor_base: dict[str, Any], p: int) -> dict[str, Any]:
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
                "binary-square-and-multiply field-multiplication proxy plus "
                "coordinate RHS and explicit map arithmetic"
            ),
        }
    )
    return diagnostics


def make_random_x_factor_base(
    curve: Any,
    q: int,
    size: int,
    seed: int,
) -> dict[str, Any]:
    if size % 2:
        raise ValueError("sign-complete factor-base size must be even")
    rng = random.Random(seed)
    ops = Ops()
    diagnostics = {"x_candidates": 0, "square_root_tests": 0, "subgroup_tests": 0}
    fibers: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    for draw_index, x in enumerate(rng.sample(range(curve.p), curve.p)):
        point = ENERGY.point_for_x(curve, q, x, ops, diagnostics)
        if point is None or x in seen_x:
            continue
        seen_x.add(x)
        pair = ENERGY.canonical_fiber(curve, point)
        fibers.append(
            {
                "points": [point_json(pair[0]), point_json(pair[1])],
                "source": {"kind": "random_x", "draw_index": draw_index, "x": x},
            }
        )
        if len(fibers) == size // 2:
            break
    if len(fibers) != size // 2:
        raise RuntimeError("random-x factor-base generation exhausted the field")
    return {
        "name": "random_x",
        "size": size,
        "fibers": fibers,
        "points": [point for fiber in fibers for point in fiber["points"]],
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
    }


def sanitize_fibers(family: str, fibers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    safe: list[dict[str, Any]] = []
    allowed = {"kind", "x", "t", "c", "d", "e", "map", "draw_index"}
    for ordinal, fiber in enumerate(fibers):
        source = {
            key: value for key, value in fiber["source"].items() if key in allowed
        }
        source["kind"] = family
        source["ordinal"] = ordinal
        safe.append({"points": fiber["points"], "source": source})
    return safe


def make_factor_base(
    family: str,
    curve: Any,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    if family not in ALL_FAMILIES:
        raise ValueError(f"unsupported factor-base family: {family}")
    if family == "random_x":
        raw = make_random_x_factor_base(curve, q, size, seed)
    else:
        energy_name = {
            "random_scalar": "random",
            "scalar_progression": "scalar_progression_positive_control",
        }.get(family, family)
        raw = ENERGY.make_factor_base(
            energy_name,
            curve,
            q,
            generator,
            size,
            seed,
        )
    fibers = sanitize_fibers(family, raw["fibers"])
    record = {
        "name": family,
        "seed": seed,
        "size": size,
        "symmetry_mode": "sign_complete",
        "points": raw["points"],
        "fibers": fibers,
        "build_ops": raw["build_ops"],
        "build_diagnostics": raw["build_diagnostics"],
        "scalar_source_metadata_emitted": False,
        "solver_input_fields": ["points"],
    }
    record["charged_build_diagnostics"] = charged_build_diagnostics(record, curve.p)
    record["digest"] = stable_digest(record)
    return record


def verify_witness(
    curve: Any,
    points: list[Point],
    witness: tuple[int, ...],
    target: Point,
    ops: Any | None = None,
) -> bool:
    recovered: Point = None
    for index in witness:
        recovered = curve.add(recovered, points[index], ops)
    return recovered == target


@dataclass
class CompiledAdvice:
    mapping: dict[Point, list[tuple[int, int, int, int]]]
    multiplicities: dict[Point, int]
    record: dict[str, Any]
    build_ops: Ops


def compile_four_sum_advice(
    curve: Any,
    points: list[Point],
    witness_cap: int,
) -> CompiledAdvice:
    exact_int(witness_cap, "witness_cap", 1)
    ops = Ops()
    pair_sums: dict[tuple[int, int], Point] = {}
    for left in range(len(points)):
        for right in range(left, len(points)):
            pair_sums[(left, right)] = curve.add(points[left], points[right], ops)

    mapping: dict[Point, list[tuple[int, int, int, int]]] = {}
    multiplicities: dict[Point, int] = {}
    attempts = 0
    for witness in itertools.combinations_with_replacement(range(len(points)), 4):
        attempts += 1
        left = pair_sums[(witness[0], witness[1])]
        right = pair_sums[(witness[2], witness[3])]
        total = curve.add(left, right, ops)
        multiplicities[total] = multiplicities.get(total, 0) + 1
        bucket = mapping.setdefault(total, [])
        if len(bucket) < witness_cap:
            bucket.append(witness)

    entries = [
        {
            "point": point_json(point),
            "witnesses": [list(witness) for witness in mapping[point]],
            "full_multiplicity": multiplicities[point],
        }
        for point in sorted(mapping, key=point_sort_key)
    ]
    point_bits = 1 + 2 * curve.p.bit_length()
    index_bits = max(1, (len(points) - 1).bit_length())
    count_bits = max(1, witness_cap.bit_length())
    stored_witnesses = sum(len(bucket) for bucket in mapping.values())
    payload_bits = (
        len(points) * point_bits
        + len(mapping) * (point_bits + count_bits)
        + stored_witnesses * 4 * index_bits
    )
    artifact = {"factor_base": [point_json(point) for point in points], "advice": entries}
    multiplicity_values = list(multiplicities.values())
    record = {
        "witness_cap": witness_cap,
        "pair_multiset_attempts": math.comb(len(points) + 1, 2),
        "four_multiset_attempts": attempts,
        "expected_four_multiset_attempts": math.comb(len(points) + 3, 4),
        "four_sum_support_size": len(mapping),
        "stored_witness_count": stored_witnesses,
        "discarded_witness_count": attempts - stored_witnesses,
        "maximum_full_witness_multiplicity": max(multiplicity_values),
        "mean_full_witness_multiplicity": statistics.fmean(multiplicity_values),
        "multiplicity_histogram": {
            str(value): multiplicity_values.count(value)
            for value in sorted(set(multiplicity_values))
        },
        "build_ops": asdict(ops),
        "point_encoding_bits": point_bits,
        "factor_base_index_bits": index_bits,
        "payload_bit_lower_estimate": payload_bits,
        "payload_model": (
            "fixed-width affine point keys, bounded witness counts, and raw "
            "factor-base indices; excludes hash-table and allocator overhead"
        ),
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": deep_size({"points": points, "mapping": mapping}),
        "advice_digest": stable_digest(entries),
        "first_entries": entries[: min(4, len(entries))],
    }
    return CompiledAdvice(mapping, multiplicities, record, ops)


def build_exact_five_sum_support(
    curve: Any,
    advice: dict[Point, list[tuple[int, int, int, int]]],
    points: list[Point],
) -> tuple[set[Point], Ops]:
    ops = Ops()
    support: set[Point] = set()
    for partial in advice:
        for point in points:
            support.add(curve.add(partial, point, ops))
    return support, ops


def row_from_witness(witness: tuple[int, ...], width: int, q: int) -> tuple[int, ...]:
    row = [0] * width
    for index in witness:
        row[index] = (row[index] + 1) % q
    return tuple(row)


def query_target(
    curve: Any,
    target: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    relation_limit: int,
) -> dict[str, Any]:
    exact_int(relation_limit, "relation_limit", 1)
    ops = Ops()
    probes = 0
    witness_reads = 0
    relations: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    witness_verification_ops = Ops()
    for final_index, point in enumerate(points):
        complement = curve.add(target, curve.neg(point), ops)
        probes += 1
        bucket = advice.get(complement)
        if bucket is None:
            continue
        for partial_witness in bucket:
            witness_reads += 1
            witness = tuple(sorted(partial_witness + (final_index,)))
            if witness in seen:
                continue
            if not verify_witness(
                curve, points, witness, target, witness_verification_ops
            ):
                raise AssertionError("compiled witness does not sum to target")
            seen.add(witness)
            relations.append(witness)
            if len(relations) == relation_limit:
                break
        if len(relations) == relation_limit:
            break
    point_bytes = math.ceil((1 + 2 * curve.p.bit_length()) / 8)
    witness_bytes = math.ceil(4 * max(1, (len(points) - 1).bit_length()) / 8)
    return {
        "relations": relations,
        "ops": ops,
        "probes": probes,
        "witness_reads": witness_reads,
        "logical_key_bytes_read": probes * point_bytes,
        "logical_witness_bytes_read": witness_reads * witness_bytes,
        "witness_verification_audit_ops": witness_verification_ops,
    }


def audit_all_targets(
    curve: Any,
    q: int,
    generator: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    exact_support: set[Point],
    descent_attempt_limit: int,
) -> dict[str, Any]:
    target: Point = None
    enumeration_ops = Ops()
    query_ops = Ops()
    witness_verification_ops = Ops()
    probes: list[int] = []
    witness_reads = 0
    supported = 0
    first_witness: dict[str, Any] | None = None
    transcript: list[dict[str, Any]] = []
    support_flags: list[bool] = []
    for scalar in range(q):
        query = query_target(curve, target, points, advice, 1)
        query_ops.add(query["ops"])
        witness_verification_ops.add(query["witness_verification_audit_ops"])
        probes.append(query["probes"])
        witness_reads += query["witness_reads"]
        observed = bool(query["relations"])
        support_flags.append(observed)
        expected = target in exact_support
        if observed != expected:
            raise AssertionError("query support disagrees with exact five-sum support")
        if observed:
            supported += 1
            if first_witness is None:
                first_witness = {
                    "target_scalar": scalar,
                    "target": point_json(target),
                    "indices": list(query["relations"][0]),
                }
        transcript.append(
            {
                "scalar": scalar,
                "supported": observed,
                "probes": query["probes"],
                "witness_reads": query["witness_reads"],
            }
        )
        target = curve.add(target, generator, enumeration_ops)
    if target is not None:
        raise AssertionError("generator enumeration did not close after q steps")
    if supported != len(exact_support):
        raise AssertionError("support cardinality disagrees with exhaustive targets")
    next_distance = q + 1
    distances = [q + 1] * q
    for index in range(2 * q - 1, -1, -1):
        if support_flags[index % q]:
            next_distance = 0
        else:
            next_distance += 1
        if index < q:
            distances[index] = next_distance
    capped_attempts = [
        min(distance + 1, descent_attempt_limit) for distance in distances
    ]
    randomized_successes = sum(
        int(distance < descent_attempt_limit) for distance in distances
    )
    return {
        "supported_targets": supported,
        "group_order": q,
        "exact_success_probability": supported / q,
        "enumeration_audit_ops": asdict(enumeration_ops),
        "query_ops": asdict(query_ops),
        "witness_verification_audit_ops": asdict(witness_verification_ops),
        "average_first_witness_group_operations": query_ops.group_operations / q,
        "average_first_witness_probes": statistics.fmean(probes),
        "maximum_first_witness_probes": max(probes),
        "total_witness_reads": witness_reads,
        "probe_histogram": {
            str(value): probes.count(value) for value in sorted(set(probes))
        },
        "randomized_descent_attempt_limit": descent_attempt_limit,
        "exact_randomized_descent_success_probability": randomized_successes / q,
        "exact_randomized_descent_expected_capped_attempts": statistics.fmean(
            capped_attempts
        ),
        "exact_randomized_descent_maximum_attempts_to_hit": max(
            distance + 1 for distance in distances
        ),
        "transcript_sha256": stable_digest(transcript),
        "first_witness": first_witness,
    }


@dataclass
class LinearOps:
    row_additions: int = 0
    field_additions: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0

    def add(self, other: "LinearOps") -> None:
        for key, value in asdict(other).items():
            setattr(self, key, getattr(self, key) + value)


class IncrementalBasis:
    def __init__(self, width: int, q: int) -> None:
        self.width = width
        self.q = q
        self.rows: dict[int, tuple[list[int], int]] = {}
        self.ops = LinearOps()

    @property
    def rank(self) -> int:
        return len(self.rows)

    def insert(self, coefficients: tuple[int, ...], rhs: int) -> bool:
        row = [value % self.q for value in coefficients]
        value = rhs % self.q
        for pivot in sorted(self.rows):
            factor = row[pivot]
            if factor == 0:
                continue
            basis_row, basis_rhs = self.rows[pivot]
            self.ops.row_additions += 1
            for column in range(pivot, self.width):
                row[column] = (row[column] - factor * basis_row[column]) % self.q
                self.ops.field_multiplications += 1
                self.ops.field_additions += 1
            value = (value - factor * basis_rhs) % self.q
            self.ops.field_multiplications += 1
            self.ops.field_additions += 1
        pivot = next((index for index, item in enumerate(row) if item), None)
        if pivot is None:
            if value:
                raise AssertionError("valid relation system became inconsistent")
            return False
        inverse = pow(row[pivot], -1, self.q)
        self.ops.field_inversions += 1
        for column in range(pivot, self.width):
            row[column] = row[column] * inverse % self.q
            self.ops.field_multiplications += 1
        value = value * inverse % self.q
        self.ops.field_multiplications += 1
        self.rows[pivot] = (row, value)
        return True


def solve_full_rank(
    equations: list[dict[str, Any]],
    width: int,
    q: int,
) -> tuple[list[int], LinearOps]:
    if len(equations) < width:
        raise ValueError("not enough equations for a full-rank solve")
    matrix = [list(equation["coefficients"]) + [equation["rhs"]] for equation in equations]
    ops = LinearOps()
    pivot_row = 0
    for column in range(width):
        selected = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column] % q),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        inverse = pow(matrix[pivot_row][column] % q, -1, q)
        ops.field_inversions += 1
        for index in range(column, width + 1):
            matrix[pivot_row][index] = matrix[pivot_row][index] * inverse % q
            ops.field_multiplications += 1
        for row in range(len(matrix)):
            if row == pivot_row:
                continue
            factor = matrix[row][column] % q
            if factor == 0:
                continue
            ops.row_additions += 1
            for index in range(column, width + 1):
                matrix[row][index] = (
                    matrix[row][index] - factor * matrix[pivot_row][index]
                ) % q
                ops.field_multiplications += 1
                ops.field_additions += 1
        pivot_row += 1
        if pivot_row == width:
            break
    if pivot_row != width:
        raise ValueError("relation system is rank deficient")
    solution = [0] * width
    for row in matrix:
        pivot = next((index for index in range(width) if row[index] % q), None)
        if pivot is not None:
            solution[pivot] = row[-1] % q
    return solution, ops


def collect_relations(
    curve: Any,
    q: int,
    generator: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    seed: int,
    relations_per_target: int,
    target_budget: int,
) -> dict[str, Any]:
    target_budget = q if target_budget == 0 else min(target_budget, q)
    schedule = list(range(q))
    random.Random(seed ^ 0x3C6EF372).shuffle(schedule)
    basis = IncrementalBasis(len(points), q)
    target_ops = Ops()
    query_ops = Ops()
    witness_verification_ops = Ops()
    traffic = {"key_bytes": 0, "witness_bytes": 0, "probes": 0, "witness_reads": 0}
    unique_rows: dict[tuple[int, ...], int] = {}
    independent_equations: list[dict[str, Any]] = []
    supported_targets = 0
    relation_count = 0
    rank_trajectory: list[dict[str, int]] = []
    transcript: list[dict[str, Any]] = []
    for attempt_index, scalar in enumerate(schedule[:target_budget], start=1):
        target = curve.mul(scalar, generator, target_ops)
        query = query_target(
            curve,
            target,
            points,
            advice,
            relations_per_target,
        )
        query_ops.add(query["ops"])
        witness_verification_ops.add(query["witness_verification_audit_ops"])
        traffic["key_bytes"] += query["logical_key_bytes_read"]
        traffic["witness_bytes"] += query["logical_witness_bytes_read"]
        traffic["probes"] += query["probes"]
        traffic["witness_reads"] += query["witness_reads"]
        supported_targets += int(bool(query["relations"]))
        relation_count += len(query["relations"])
        target_new_rows = 0
        target_rank_before = basis.rank
        row_digests: list[str] = []
        for witness in query["relations"]:
            coefficients = row_from_witness(witness, len(points), q)
            row_digests.append(stable_digest([list(coefficients), scalar]))
            prior_rhs = unique_rows.get(coefficients)
            if prior_rhs is not None:
                if prior_rhs != scalar:
                    raise AssertionError(
                        "one coefficient row produced inconsistent target scalars"
                    )
                continue
            unique_rows[coefficients] = scalar
            equation = {
                "coefficients": list(coefficients),
                "rhs": scalar,
                "target": point_json(target),
                "target_scalar": scalar,
                "witness": list(witness),
            }
            if basis.insert(coefficients, scalar):
                independent_equations.append(equation)
                target_new_rows += 1
                rank_trajectory.append(
                    {
                        "attempted_targets": attempt_index,
                        "supported_targets": supported_targets,
                        "unique_rows": len(unique_rows),
                        "rank": basis.rank,
                    }
                )
        transcript.append(
            {
                "attempt": attempt_index,
                "scalar": scalar,
                "relation_count": len(query["relations"]),
                "new_independent_rows": target_new_rows,
                "rank_before": target_rank_before,
                "rank_after": basis.rank,
                "probes": query["probes"],
                "row_digests": row_digests,
            }
        )
        if basis.rank == len(points):
            break

    full_rank = basis.rank == len(points)
    solution: list[int] | None = None
    solve_ops = LinearOps()
    solution_verify_ops = Ops()
    solution_verified = False
    if full_rank:
        solution, solve_ops = solve_full_rank(independent_equations, len(points), q)
        solution_verified = all(
            curve.mul(scalar, generator, solution_verify_ops) == point
            for scalar, point in zip(solution, points)
        )
        if not solution_verified:
            raise AssertionError("linear solution does not reproduce factor-base points")
    return {
        "target_budget": target_budget,
        "target_schedule_sha256": stable_digest(schedule[:target_budget]),
        "targets_attempted": len(transcript),
        "supported_targets": supported_targets,
        "relations_returned": relation_count,
        "unique_coefficient_rows": len(unique_rows),
        "rank": basis.rank,
        "full_rank": full_rank,
        "rank_trajectory": rank_trajectory,
        "independent_equations": independent_equations,
        "incremental_linear_ops": asdict(basis.ops),
        "solve_linear_ops": asdict(solve_ops),
        "target_generation_ops": asdict(target_ops),
        "query_ops": asdict(query_ops),
        "witness_verification_audit_ops": asdict(witness_verification_ops),
        "logical_traffic": traffic,
        "transcript_sha256": stable_digest(transcript),
        "factor_base_logs": solution,
        "solution_verification_ops": asdict(solution_verify_ops),
        "factor_base_logs_verified": solution_verified,
    }


def solve_individual_log(
    curve: Any,
    q: int,
    generator: Point,
    target: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    factor_base_logs: list[int],
    seed: int,
    attempt_limit: int,
) -> dict[str, Any]:
    rng = random.Random(seed)
    randomizer = rng.randrange(q)
    randomization_ops = Ops()
    query_ops = Ops()
    witness_verification_ops = Ops()
    verification_ops = Ops()
    randomized = curve.add(
        target,
        curve.mul(randomizer, generator, randomization_ops),
        randomization_ops,
    )
    probes = 0
    key_bytes = 0
    witness_bytes = 0
    for attempt in range(1, attempt_limit + 1):
        query = query_target(curve, randomized, points, advice, 1)
        query_ops.add(query["ops"])
        witness_verification_ops.add(query["witness_verification_audit_ops"])
        probes += query["probes"]
        key_bytes += query["logical_key_bytes_read"]
        witness_bytes += query["logical_witness_bytes_read"]
        if query["relations"]:
            witness = query["relations"][0]
            recovered = (sum(factor_base_logs[index] for index in witness) - randomizer) % q
            verified = curve.mul(recovered, generator, verification_ops) == target
            if not verified:
                raise AssertionError("individual-log descent recovered the wrong scalar")
            return {
                "success": True,
                "attempts": attempt,
                "randomizer": randomizer,
                "randomized_target": point_json(randomized),
                "witness": list(witness),
                "recovered_scalar": recovered,
                "randomization_ops": asdict(randomization_ops),
                "query_ops": asdict(query_ops),
                "witness_verification_audit_ops": asdict(
                    witness_verification_ops
                ),
                "verification_ops": asdict(verification_ops),
                "logical_probes": probes,
                "logical_key_bytes_read": key_bytes,
                "logical_witness_bytes_read": witness_bytes,
                "verified": verified,
            }
        randomized = curve.add(randomized, generator, randomization_ops)
        randomizer = (randomizer + 1) % q
    return {
        "success": False,
        "attempts": attempt_limit,
        "randomizer": randomizer,
        "randomized_target": point_json(randomized),
        "witness": None,
        "recovered_scalar": None,
        "randomization_ops": asdict(randomization_ops),
        "query_ops": asdict(query_ops),
        "witness_verification_audit_ops": asdict(witness_verification_ops),
        "verification_ops": asdict(verification_ops),
        "logical_probes": probes,
        "logical_key_bytes_read": key_bytes,
        "logical_witness_bytes_read": witness_bytes,
        "verified": False,
    }


def run_descent_challenges(
    curve: Any,
    q: int,
    generator: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    factor_base_logs: list[int] | None,
    seed: int,
    challenge_count: int,
    attempt_limit: int,
) -> dict[str, Any]:
    if factor_base_logs is None:
        return {
            "status": "skipped_rank_deficient",
            "challenges": [],
            "all_verified": False,
        }
    rng = random.Random(seed ^ 0x1F83D9AB)
    challenge_generation_ops = Ops()
    challenges: list[dict[str, Any]] = []
    for challenge_index in range(challenge_count):
        known_scalar = rng.randrange(q)
        target = curve.mul(known_scalar, generator, challenge_generation_ops)
        result = solve_individual_log(
            curve,
            q,
            generator,
            target,
            points,
            advice,
            factor_base_logs,
            seed ^ (challenge_index + 1) * 0x9E3779B1,
            attempt_limit,
        )
        result.update(
            {
                "challenge_index": challenge_index,
                "target": point_json(target),
                "known_scalar_private_audit": known_scalar,
                "matches_private_scalar": result["recovered_scalar"] == known_scalar,
            }
        )
        challenges.append(result)
    return {
        "status": "completed",
        "challenges": challenges,
        "challenge_generation_audit_ops": asdict(challenge_generation_ops),
        "all_verified": all(
            challenge["success"]
            and challenge["verified"]
            and challenge["matches_private_scalar"]
            for challenge in challenges
        ),
    }


def sum_ops(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {key: sum(record.get(key, 0) for record in records) for key in sorted(keys)}


def run_matched_bsgs_preprocessing(
    curve: Any,
    q: int,
    generator: Point,
    advice_budget_bits: int,
    target_seed: int,
    challenge_count: int,
) -> dict[str, Any]:
    point_bits = 1 + 2 * curve.p.bit_length()
    scalar_bits = q.bit_length()
    entry_bits = point_bits + scalar_bits
    table_capacity = max(
        1,
        min(q, (advice_budget_bits - point_bits) // entry_bits),
    )
    if table_capacity * entry_bits + point_bits > advice_budget_bits:
        raise AssertionError("matched BSGS table exceeds the candidate advice budget")
    offline_ops = Ops()
    table: dict[Point, int] = {}
    current: Point = None
    for scalar in range(table_capacity):
        table[current] = scalar
        current = curve.add(current, generator, offline_ops)
    giant_step = current
    if len(table) != table_capacity:
        raise AssertionError("matched BSGS baby-step table contains a collision")

    rng = random.Random(target_seed ^ 0x1F83D9AB)
    challenge_generation_ops = Ops()
    verification_ops = Ops()
    challenge_rows = []
    giant_count = math.ceil(q / table_capacity)
    point_bytes = math.ceil(point_bits / 8)
    scalar_bytes = math.ceil(scalar_bits / 8)
    for challenge_index in range(challenge_count):
        known_scalar = rng.randrange(q)
        target = curve.mul(known_scalar, generator, challenge_generation_ops)
        gamma = target
        online_ops = Ops()
        probes = 0
        recovered: int | None = None
        for giant_index in range(giant_count):
            probes += 1
            baby_scalar = table.get(gamma)
            if baby_scalar is not None:
                recovered = (giant_index * table_capacity + baby_scalar) % q
                break
            if giant_index + 1 < giant_count:
                gamma = curve.add(gamma, curve.neg(giant_step), online_ops)
        verified = (
            recovered is not None
            and curve.mul(recovered, generator, verification_ops) == target
            and recovered == known_scalar
        )
        if not verified:
            raise AssertionError("matched BSGS failed a scheduled toy challenge")
        challenge_rows.append(
            {
                "challenge_index": challenge_index,
                "target": point_json(target),
                "known_scalar_private_audit": known_scalar,
                "recovered_scalar": recovered,
                "online_ops": asdict(online_ops),
                "table_probes": probes,
                "logical_bytes_read": probes * point_bytes + scalar_bytes,
                "verified": verified,
            }
        )
    online_values = [
        challenge["online_ops"]["group_operations"] for challenge in challenge_rows
    ]
    probe_values = [challenge["table_probes"] for challenge in challenge_rows]
    advice_bits = table_capacity * entry_bits + point_bits
    maximum_online = max(online_values)
    worst_case_online = max(0, giant_count - 1)
    return {
        "algorithm": "fixed-base BSGS with baby-step advice",
        "advice_budget_bits": advice_budget_bits,
        "advice_payload_bits": advice_bits,
        "unused_advice_bits": advice_budget_bits - advice_bits,
        "entry_bits": entry_bits,
        "table_capacity": table_capacity,
        "giant_step_count_bound": giant_count,
        "offline_ops": asdict(offline_ops),
        "challenge_generation_audit_ops": asdict(challenge_generation_ops),
        "verification_audit_ops": asdict(verification_ops),
        "challenges": challenge_rows,
        "all_verified": True,
        "average_online_group_operations": statistics.fmean(online_values),
        "maximum_online_group_operations": maximum_online,
        "worst_case_online_group_operation_bound": worst_case_online,
        "average_table_probes": statistics.fmean(probe_values),
        "maximum_table_probes": max(probe_values),
        "average_logical_bytes_read": statistics.fmean(
            challenge["logical_bytes_read"] for challenge in challenge_rows
        ),
        "worst_case_frontier_score": advice_bits * worst_case_online**2 / q,
        "boundary": (
            "same disclosed advice-bit budget and scheduled toy targets; generic "
            "group-operation/table-probe baseline, not a hardware benchmark"
        ),
    }


def compile_family_row(
    curve_record: dict[str, Any],
    family: str,
    factor_base_size: int,
    factor_base_seed: int,
    target_schedule_seed: int,
    witness_cap: int,
    relations_per_target: int,
    relation_target_budget: int,
    descent_challenges: int,
    descent_attempt_limit: int,
) -> dict[str, Any]:
    curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    factor_base = make_factor_base(
        family,
        curve,
        q,
        generator,
        factor_base_size,
        factor_base_seed,
    )
    points = [point_from_json(point) for point in factor_base["points"]]
    compiled = compile_four_sum_advice(curve, points, witness_cap)
    exact_support, support_ops = build_exact_five_sum_support(
        curve,
        compiled.mapping,
        points,
    )
    target_audit = audit_all_targets(
        curve,
        q,
        generator,
        points,
        compiled.mapping,
        exact_support,
        descent_attempt_limit,
    )
    relations = collect_relations(
        curve,
        q,
        generator,
        points,
        compiled.mapping,
        target_schedule_seed,
        relations_per_target,
        relation_target_budget,
    )
    descent = run_descent_challenges(
        curve,
        q,
        generator,
        points,
        compiled.mapping,
        relations["factor_base_logs"],
        target_schedule_seed,
        descent_challenges,
        descent_attempt_limit,
    )
    build_ops = factor_base["build_ops"]
    compiler_ops = compiled.record["build_ops"]
    charged = factor_base["charged_build_diagnostics"]
    offline_charged = {
        "group_operations": build_ops["group_operations"] + compiler_ops["group_operations"],
        "field_multiplications": (
            build_ops["field_multiplications"]
            + compiler_ops["field_multiplications"]
            + charged["charged_pow_field_multiplications"]
            + charged["coordinate_rhs_field_multiplications"]
            + charged["map_field_multiplications"]
        ),
        "field_inversions": (
            build_ops["field_inversions"]
            + compiler_ops["field_inversions"]
            + charged["map_field_inversions"]
        ),
    }
    epsilon = target_audit["exact_success_probability"]
    advice_bits = compiled.record["payload_bit_lower_estimate"]
    maximum_t = target_audit["maximum_first_witness_probes"]
    expected_t = target_audit["average_first_witness_probes"]
    frontier = {
        "advice_bits": advice_bits,
        "epsilon": epsilon,
        "group_order": q,
        "worst_case_query_bound": maximum_t,
        "exact_average_query_operations": expected_t,
        "payload_bits_worst_case_score": advice_bits * maximum_t**2 / (epsilon * q),
        "payload_bits_expected_score": advice_bits * expected_t**2 / (epsilon * q),
        "serialized_bits_worst_case_score": (
            8 * compiled.record["canonical_serialized_bytes"] * maximum_t**2 / (epsilon * q)
        ),
        "python_deep_bits_worst_case_score": (
            8 * compiled.record["python_deep_bytes"] * maximum_t**2 / (epsilon * q)
        ),
        "boundary": (
            "MODEL-BOUND diagnostic only: S uses disclosed bits or implementation "
            "bytes and T uses EC additions/probes; no lower-bound violation is claimed"
        ),
    }
    descent_attack_ops = [
        sum_ops(challenge["randomization_ops"], challenge["query_ops"])
        for challenge in descent["challenges"]
    ]
    aggregate_descent_ops = sum_ops(*descent_attack_ops) if descent_attack_ops else asdict(Ops())
    online_group_operations = [record["group_operations"] for record in descent_attack_ops]
    online_logical_bytes = [
        challenge["logical_key_bytes_read"]
        + challenge["logical_witness_bytes_read"]
        for challenge in descent["challenges"]
    ]
    preprocessing_group_operations = (
        offline_charged["group_operations"]
        + relations["target_generation_ops"]["group_operations"]
        + relations["query_ops"]["group_operations"]
    )
    factor_log_bits = (
        len(relations["factor_base_logs"]) * q.bit_length()
        if relations["factor_base_logs"] is not None
        else 0
    )
    full_advice_bits = advice_bits + factor_log_bits
    sampled_online_average = (
        statistics.fmean(online_group_operations) if online_group_operations else None
    )
    sampled_online_maximum = max(online_group_operations) if online_group_operations else None
    worst_case_online_group_bound = (
        2 * q.bit_length()
        + descent_attempt_limit * len(points)
        + max(0, descent_attempt_limit - 1)
    )
    exact_randomized_epsilon = target_audit[
        "exact_randomized_descent_success_probability"
    ]
    fixed_curve_online = {
        "generator_fixed": True,
        "field_modulus_special_structure": "p mod 4 = 3 only; p-1 was not selected",
        "curve_special_structure": "trace not in {0,1}; j not in {0,1728}; prime order",
        "supported_one_query_targets": len(exact_support),
        "one_query_success_probability": epsilon,
        "preprocessing_group_operations": preprocessing_group_operations,
        "preprocessing_linear_ops": {
            "incremental": relations["incremental_linear_ops"],
            "solve": relations["solve_linear_ops"],
        },
        "compiler_advice_bits": advice_bits,
        "factor_base_log_advice_bits": factor_log_bits,
        "full_online_advice_bits": full_advice_bits,
        "full_online_advice_canonical_bytes": (
            compiled.record["canonical_serialized_bytes"]
            + math.ceil(factor_log_bits / 8)
        ),
        "full_online_advice_python_deep_bytes": (
            compiled.record["python_deep_bytes"]
            + (
                deep_size(relations["factor_base_logs"])
                if relations["factor_base_logs"] is not None
                else 0
            )
        ),
        "sampled_challenge_count": len(descent["challenges"]),
        "sampled_online_successes": sum(
            int(challenge["success"]) for challenge in descent["challenges"]
        ),
        "sampled_average_online_group_operations": sampled_online_average,
        "sampled_maximum_online_group_operations": sampled_online_maximum,
        "sampled_average_logical_bytes_read": (
            statistics.fmean(online_logical_bytes) if online_logical_bytes else None
        ),
        "sampled_maximum_logical_bytes_read": (
            max(online_logical_bytes) if online_logical_bytes else None
        ),
        "descent_attempt_limit": descent_attempt_limit,
        "exact_randomized_success_probability_at_limit": exact_randomized_epsilon,
        "exact_expected_capped_attempts": target_audit[
            "exact_randomized_descent_expected_capped_attempts"
        ],
        "worst_case_online_group_operation_bound": worst_case_online_group_bound,
        "full_advice_bits_worst_case_frontier_score": (
            full_advice_bits
            * worst_case_online_group_bound**2
            / (exact_randomized_epsilon * q)
        ),
        "amortized_group_operations_per_target": {
            str(batch): (
                preprocessing_group_operations / batch + sampled_online_average
                if sampled_online_average is not None
                else None
            )
            for batch in (1, 8, 64, 1024)
        },
        "boundary": (
            "sampled toy online path; challenge verification and challenge-input "
            "generation are audit costs, while preprocessing includes factor-base "
            "construction, four-sum compilation, and relation collection"
        ),
    }
    matched_bsgs = run_matched_bsgs_preprocessing(
        curve,
        q,
        generator,
        full_advice_bits,
        target_schedule_seed,
        descent_challenges,
    )
    fixed_curve_online["matched_bsgs"] = {
        **matched_bsgs,
        "candidate_to_bsgs_average_online_group_operation_ratio": (
            sampled_online_average / matched_bsgs["average_online_group_operations"]
            if matched_bsgs["average_online_group_operations"]
            else None
        ),
        "candidate_to_bsgs_preprocessing_group_operation_ratio": (
            preprocessing_group_operations
            / matched_bsgs["offline_ops"]["group_operations"]
        ),
        "candidate_average_online_dominates_at_equal_advice": (
            sampled_online_average is not None
            and sampled_online_average
            < matched_bsgs["average_online_group_operations"]
        ),
        "candidate_to_bsgs_worst_case_group_operation_ratio": (
            worst_case_online_group_bound
            / matched_bsgs["worst_case_online_group_operation_bound"]
            if matched_bsgs["worst_case_online_group_operation_bound"]
            else None
        ),
        "candidate_worst_case_online_dominates_at_equal_advice": (
            worst_case_online_group_bound
            < matched_bsgs["worst_case_online_group_operation_bound"]
        ),
    }
    fixed_curve_online["matched_bsgs"]["candidate_online_dominates_at_equal_advice"] = (
        fixed_curve_online["matched_bsgs"][
            "candidate_average_online_dominates_at_equal_advice"
        ]
        and fixed_curve_online["matched_bsgs"][
            "candidate_worst_case_online_dominates_at_equal_advice"
        ]
    )
    attack_group_ops = (
        offline_charged["group_operations"]
        + relations["target_generation_ops"]["group_operations"]
        + relations["query_ops"]["group_operations"]
        + aggregate_descent_ops["group_operations"]
    )
    total_attack_cost_vector = {
        "group_operations": attack_group_ops,
        "fp_field_multiplications": (
            offline_charged["field_multiplications"]
            + relations["target_generation_ops"]["field_multiplications"]
            + relations["query_ops"]["field_multiplications"]
            + aggregate_descent_ops["field_multiplications"]
        ),
        "fp_field_inversions": (
            offline_charged["field_inversions"]
            + relations["target_generation_ops"]["field_inversions"]
            + relations["query_ops"]["field_inversions"]
            + aggregate_descent_ops["field_inversions"]
        ),
        "mod_q_field_additions": (
            relations["incremental_linear_ops"]["field_additions"]
            + relations["solve_linear_ops"]["field_additions"]
        ),
        "mod_q_field_multiplications": (
            relations["incremental_linear_ops"]["field_multiplications"]
            + relations["solve_linear_ops"]["field_multiplications"]
        ),
        "mod_q_field_inversions": (
            relations["incremental_linear_ops"]["field_inversions"]
            + relations["solve_linear_ops"]["field_inversions"]
        ),
        "logical_preprocessing_bytes_written": math.ceil(full_advice_bits / 8),
        "logical_relation_query_bytes_read": (
            relations["logical_traffic"]["key_bytes"]
            + relations["logical_traffic"]["witness_bytes"]
        ),
        "logical_individual_query_bytes_read": sum(online_logical_bytes),
        "boundary": (
            "attack-path vector; exhaustive support, witness replay, recovered-log "
            "verification, challenge generation, and result verification remain "
            "separately reported audit costs"
        ),
    }
    functional_gate = (
        relations["full_rank"]
        and relations["factor_base_logs_verified"]
        and descent["all_verified"]
    )
    return {
        "family": family,
        "eligibility": (
            "positive_control_only" if family == POSITIVE_CONTROL else "candidate_or_null"
        ),
        "factor_base": factor_base,
        "target_schedule_seed": target_schedule_seed,
        "witness_cap": witness_cap,
        "compiler": compiled.record,
        "exact_five_sum_support_size": len(exact_support),
        "exact_support_build_ops": asdict(support_ops),
        "target_audit": target_audit,
        "relations": relations,
        "descent": descent,
        "offline_charged_cost": offline_charged,
        "aggregate_descent_attack_ops": aggregate_descent_ops,
        "fixed_curve_online": fixed_curve_online,
        "rho_comparison": None,
        "total_attack_group_operations": attack_group_ops,
        "total_attack_cost_vector": total_attack_cost_vector,
        "preprocessing_frontier_diagnostic": frontier,
        "functional_gate_passed": functional_gate,
        "instance_signal_gate_passed": False,
        "routing_gate_passed": False,
        "matched_random_x_ratios": None,
        "matched_random_scalar_ratios": None,
        "claim_boundary": (
            "A functional pass proves only a toy relation/rank/descent path; "
            "it is not a sub-rho or fixed-curve frontier result"
        ),
    }


def row_ratios(row: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    support_ratio = (
        row["exact_five_sum_support_size"] / control["exact_five_sum_support_size"]
    )
    score_ratio = (
        row["preprocessing_frontier_diagnostic"]["payload_bits_worst_case_score"]
        / control["preprocessing_frontier_diagnostic"]["payload_bits_worst_case_score"]
    )
    offline_ratios = {
        key: (
            row["offline_charged_cost"][key] / control["offline_charged_cost"][key]
            if control["offline_charged_cost"][key]
            else (1.0 if row["offline_charged_cost"][key] == 0 else math.inf)
        )
        for key in row["offline_charged_cost"]
    }
    return {
        "support": support_ratio,
        "payload_bits_worst_case_score": score_ratio,
        "offline_charged_cost": offline_ratios,
    }


def attach_matched_null_ratios(rows: list[dict[str, Any]]) -> None:
    random_x_controls = {
        row["witness_cap"]: row for row in rows if row["family"] == "random_x"
    }
    random_scalar_controls = {
        row["witness_cap"]: row
        for row in rows
        if row["family"] == "random_scalar"
    }
    if set(random_x_controls) != set(random_scalar_controls):
        raise AssertionError("both matched null families are required at every witness cap")
    for row in rows:
        random_x_ratios = row_ratios(row, random_x_controls[row["witness_cap"]])
        random_scalar_ratios = row_ratios(
            row, random_scalar_controls[row["witness_cap"]]
        )
        row["matched_random_x_ratios"] = random_x_ratios
        row["matched_random_scalar_ratios"] = random_scalar_ratios
        row["instance_signal_gate_passed"] = (
            row["family"] in CANDIDATE_FAMILIES
            and row["functional_gate_passed"]
            and row["fixed_curve_online"]["matched_bsgs"][
                "candidate_online_dominates_at_equal_advice"
            ]
            and all(
                ratios["support"] >= 0.8
                and ratios["payload_bits_worst_case_score"] <= 0.8
                and all(
                    value <= 4.0
                    for value in ratios["offline_charged_cost"].values()
                )
                for ratios in (random_x_ratios, random_scalar_ratios)
            )
        )


def aggregate_routing(
    instances: list[dict[str, Any]],
    bit_sizes: list[int],
    seeds: list[int],
    witness_caps: list[int],
) -> dict[str, Any]:
    pass_seeds: dict[tuple[str, int, int], set[int]] = {
        (family, cap, bits): set()
        for family in CANDIDATE_FAMILIES
        for cap in witness_caps
        for bits in bit_sizes
    }
    for instance in instances:
        for row in instance["rows"]:
            if row["instance_signal_gate_passed"]:
                pass_seeds[(row["family"], row["witness_cap"], instance["curve"]["bits"])].add(
                    instance["seed"]
                )
    promoted = {
        (family, cap)
        for family in CANDIDATE_FAMILIES
        for cap in witness_caps
        if len(seeds) >= 2
        and all(len(pass_seeds[(family, cap, bits)]) >= 2 for bits in bit_sizes)
    }
    for instance in instances:
        for row in instance["rows"]:
            row["routing_gate_passed"] = (
                row["instance_signal_gate_passed"]
                and (row["family"], row["witness_cap"]) in promoted
            )
    return {
        "required_passing_seeds_per_size": 2,
        "configured_seed_count": len(seeds),
        "pass_seeds_by_family_cap_and_size": {
            f"{family}|{cap}|{bits}": sorted(pass_seeds[(family, cap, bits)])
            for family in CANDIDATE_FAMILIES
            for cap in witness_caps
            for bits in bit_sizes
        },
        "promoted_family_caps": [
            {"family": family, "witness_cap": cap}
            for family, cap in sorted(promoted)
        ],
    }


def attach_rho_comparison(rows: list[dict[str, Any]], rho: dict[str, Any]) -> None:
    rho_average = rho["average_group_operations"]
    for row in rows:
        online = row["fixed_curve_online"]["sampled_average_online_group_operations"]
        preprocessing = row["fixed_curve_online"]["preprocessing_group_operations"]
        crossover = None
        if online is not None and online < rho_average:
            crossover = math.ceil(preprocessing / (rho_average - online))
        row["rho_comparison"] = {
            "rho_average_group_operations": rho_average,
            "sampled_online_group_operations": online,
            "preprocessing_group_operations": preprocessing,
            "group_operation_only_crossover_targets": crossover,
            "boundary": (
                "toy group-operation crossover only; excludes memory capacity, "
                "bandwidth, linear-field costs, rho variance, and asymptotic inference"
            ),
        }


def run_rho_baseline(
    curve_record: dict[str, Any],
    seed: int,
    trials: int,
) -> dict[str, Any]:
    curve = Curve(curve_record["p"], curve_record["a"], curve_record["b"])
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    rng = random.Random(seed ^ 0x5BE0CD19)
    records = []
    for trial in range(trials):
        scalar = rng.randrange(1, q)
        target = curve.mul(scalar, generator)
        result = ENERGY.pollard_rho(
            curve,
            q,
            generator,
            target,
            seed ^ trial * 0x27D4EB2D,
        )
        if result["recovered_scalar"] != scalar:
            raise AssertionError("Pollard rho recovered the wrong scalar")
        records.append({**result, "known_scalar": scalar, "target": point_json(target)})
    return {
        "trials": records,
        "average_group_operations": statistics.fmean(
            record["ops"]["group_operations"] for record in records
        ),
        "all_verified": True,
    }


def fit_log_slope(rows: list[tuple[int, float]]) -> float | None:
    if len(rows) < 3 or any(value <= 0 for _, value in rows):
        return None
    xs = [math.log(q) for q, _ in rows]
    ys = [math.log(value) for _, value in rows]
    x_mean = statistics.fmean(xs)
    y_mean = statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def run_experiment(config: dict[str, Any]) -> dict[str, Any]:
    bit_sizes = exact_int_list(config["bit_sizes"], "bit_sizes", 5)
    seeds = exact_int_list(config["seeds"], "seeds", 0)
    witness_caps = exact_int_list(config["witness_caps"], "witness_caps", 1)
    occupancy_lambda = exact_probability(config["occupancy_lambda"], "occupancy_lambda")
    families = list(config["families"])
    if not families or len(families) != len(set(families)):
        raise ValueError("families must be nonempty and distinct")
    if any(family not in ALL_FAMILIES for family in families):
        raise ValueError("unsupported family in configuration")
    if not {"random_x", "random_scalar"}.issubset(families):
        raise ValueError("random_x and random_scalar are mandatory for matched ratios")
    relations_per_target = exact_int(config["relations_per_target"], "relations_per_target", 1)
    relation_target_budget = exact_int(config["relation_target_budget"], "relation_target_budget", 0)
    descent_challenges = exact_int(config["descent_challenges"], "descent_challenges", 1)
    descent_attempt_limit = exact_int(config["descent_attempt_limit"], "descent_attempt_limit", 1)
    rho_trials = exact_int(config["rho_trials"], "rho_trials", 1)

    instances: list[dict[str, Any]] = []
    used_primes: set[int] = set()
    for bits in bit_sizes:
        for seed in seeds:
            curve_record = generate_clean_curve(bits, seed + bits * 1009)
            if curve_record["p"] in used_primes:
                raise AssertionError("field modulus repeated across scheduled curves")
            used_primes.add(curve_record["p"])
            q = curve_record["q"]
            size = choose_factor_base_size(q, occupancy_lambda)
            target_schedule_seed = seed ^ bits * 0x7FEB352D
            rows: list[dict[str, Any]] = []
            for family_index, family in enumerate(families):
                factor_seed = seed ^ bits * 0x45D9F3B ^ family_index * 0x9E3779B1
                for witness_cap in witness_caps:
                    rows.append(
                        compile_family_row(
                            curve_record,
                            family,
                            size,
                            factor_seed,
                            target_schedule_seed,
                            witness_cap,
                            relations_per_target,
                            relation_target_budget,
                            descent_challenges,
                            descent_attempt_limit,
                        )
                    )
            attach_matched_null_ratios(rows)
            rho = run_rho_baseline(curve_record, seed, rho_trials)
            attach_rho_comparison(rows, rho)
            instances.append(
                {
                    "seed": seed,
                    "curve": curve_record,
                    "factor_base_size": size,
                    "sizing_rule": (
                        "smallest sign-complete even B with exact signed formal "
                        "five-term class count divided by q at least occupancy_lambda"
                    ),
                    "signed_five_term_class_count": signed_class_count(size // 2, 5),
                    "occupancy_lambda": occupancy_lambda,
                    "rows": rows,
                    "rho": rho,
                }
            )

    routing_summary = aggregate_routing(instances, bit_sizes, seeds, witness_caps)

    slopes: dict[str, dict[str, float | None]] = {}
    cost_slopes: dict[str, dict[str, dict[str, float | None]]] = {}
    for family in families:
        slopes[family] = {}
        cost_slopes[family] = {}
        for witness_cap in witness_caps:
            selected_rows = [
                (instance["curve"]["q"], row)
                for instance in instances
                for row in instance["rows"]
                if row["family"] == family and row["witness_cap"] == witness_cap
            ]
            slopes[family][str(witness_cap)] = fit_log_slope(
                [(q, row["total_attack_group_operations"]) for q, row in selected_rows]
            )
            cost_slopes[family][str(witness_cap)] = {
                "group_operations": slopes[family][str(witness_cap)],
                "fp_field_multiplications": fit_log_slope(
                    [
                        (q, row["total_attack_cost_vector"]["fp_field_multiplications"])
                        for q, row in selected_rows
                    ]
                ),
                "fp_field_inversions": fit_log_slope(
                    [
                        (q, row["total_attack_cost_vector"]["fp_field_inversions"])
                        for q, row in selected_rows
                    ]
                ),
                "advice_bits": fit_log_slope(
                    [
                        (q, row["fixed_curve_online"]["full_online_advice_bits"])
                        for q, row in selected_rows
                    ]
                ),
                "sampled_online_group_operations": fit_log_slope(
                    [
                        (
                            q,
                            row["fixed_curve_online"][
                                "sampled_average_online_group_operations"
                            ],
                        )
                        for q, row in selected_rows
                    ]
                ),
            }

    source_hashes = {
        "fixed_curve_compiler_sha256": sha256_file(SCRIPT_PATH),
        "coordinate_energy_sha256": sha256_file(ENERGY_PATH),
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "hypothesis_sha256": sha256_file(HYPOTHESIS_PATH),
        "literature_sha256": sha256_file(LITERATURE_PATH),
    }
    promoted_rows = [
        {
            "curve_id": instance["curve"]["id"],
            "family": row["family"],
            "witness_cap": row["witness_cap"],
        }
        for instance in instances
        for row in instance["rows"]
        if row["routing_gate_passed"]
    ]
    frozen = config == FROZEN_CONFIG
    return {
        "protocol": PROTOCOL,
        "claim_status": CLAIM_STATUS,
        "configuration": config,
        "configuration_is_frozen": frozen,
        "development_only": not frozen,
        "source_hashes": source_hashes,
        "instances": instances,
        "exploratory_total_group_operation_slopes": slopes,
        "exploratory_cost_slopes": cost_slopes,
        "routing_rows": promoted_rows,
        "routing_summary": routing_summary,
        "global_controls": {
            "all_curves_clean": all(
                instance["curve"]["trace"] not in (0, 1)
                and instance["curve"]["j_invariant"]
                not in (0, 1728 % instance["curve"]["p"])
                and instance["curve"]["q"] == instance["curve"]["order"]
                for instance in instances
            ),
            "all_fields_distinct": len(used_primes) == len(instances),
            "all_rho_verified": all(instance["rho"]["all_verified"] for instance in instances),
            "no_scalar_source_metadata_emitted": all(
                not row["factor_base"]["scalar_source_metadata_emitted"]
                for instance in instances
                for row in instance["rows"]
            ),
        },
        "interpretation": {
            "functional_result": (
                "A full-rank verified row is a toy end-to-end index-calculus path only."
            ),
            "routing_result": (
                "A routing row is a matched-control signal requiring a larger successor."
            ),
            "breakthrough_result": (
                "No sub-rho claim is permitted without a later all-cost fitted exponent below 0.5."
            ),
        },
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-sizes", type=int, nargs="+", default=FROZEN_CONFIG["bit_sizes"])
    parser.add_argument("--seeds", type=int, nargs="+", default=FROZEN_CONFIG["seeds"])
    parser.add_argument("--families", nargs="+", default=FROZEN_CONFIG["families"])
    parser.add_argument("--witness-caps", type=int, nargs="+", default=FROZEN_CONFIG["witness_caps"])
    parser.add_argument("--occupancy-lambda", type=float, default=FROZEN_CONFIG["occupancy_lambda"])
    parser.add_argument("--relations-per-target", type=int, default=FROZEN_CONFIG["relations_per_target"])
    parser.add_argument("--relation-target-budget", type=int, default=FROZEN_CONFIG["relation_target_budget"])
    parser.add_argument("--descent-challenges", type=int, default=FROZEN_CONFIG["descent_challenges"])
    parser.add_argument("--descent-attempt-limit", type=int, default=FROZEN_CONFIG["descent_attempt_limit"])
    parser.add_argument("--rho-trials", type=int, default=FROZEN_CONFIG["rho_trials"])
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = {
        "bit_sizes": args.bit_sizes,
        "seeds": args.seeds,
        "families": args.families,
        "witness_caps": args.witness_caps,
        "occupancy_lambda": args.occupancy_lambda,
        "relations_per_target": args.relations_per_target,
        "relation_target_budget": args.relation_target_budget,
        "descent_challenges": args.descent_challenges,
        "descent_attempt_limit": args.descent_attempt_limit,
        "rho_trials": args.rho_trials,
    }
    result = run_experiment(config)
    encoded = json.dumps(result, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if args.output is None:
        sys.stdout.write(encoded)
    else:
        args.output.write_text(encoded, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
