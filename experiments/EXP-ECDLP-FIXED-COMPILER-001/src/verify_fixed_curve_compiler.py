#!/usr/bin/env python3
"""Independent replay verifier for EXP-ECDLP-FIXED-COMPILER-001."""
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
VERIFIER_PROTOCOL = "EXP-ECDLP-FIXED-COMPILER-001-independent-verifier-v1"
CLAIM_STATUS = ["HYPOTHESIS", "TOY-EVIDENCE", "HEURISTIC", "MODEL-BOUND"]
SCRIPT_PATH = Path(__file__).resolve()
REPO_ROOT = SCRIPT_PATH.parents[3]
GENERATOR_PATH = SCRIPT_PATH.with_name("fixed_curve_compiler.py")
ARITHMETIC_PATH = (
    REPO_ROOT
    / "experiments"
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "verify_recursive_expansion.py"
)
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


def load_arithmetic() -> Any:
    spec = importlib.util.spec_from_file_location("fixed_compiler_independent_arithmetic", ARITHMETIC_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load independent arithmetic: {ARITHMETIC_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


ARITH = load_arithmetic()
VerifyOps = ARITH.VerifyOps
Point = tuple[int, int] | None


def accumulate_ops(total: Any, delta: Any) -> None:
    for key, value in asdict(delta).items():
        setattr(total, key, getattr(total, key) + value)


def reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant rejected: {value}")


def reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key rejected: {key}")
        result[key] = value
    return result


def load_strict_json(path: Path) -> tuple[Any, str]:
    raw = path.read_bytes()
    document = json.loads(
        raw,
        object_pairs_hook=reject_duplicates,
        parse_constant=reject_constant,
    )
    return document, hashlib.sha256(raw).hexdigest()


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise AssertionError(f"{label} must be at least {minimum}")
    return value


def exact_int_list(values: Any, label: str, minimum: int) -> list[int]:
    if not isinstance(values, list):
        raise AssertionError(f"{label} must be a list")
    result = [exact_int(value, f"{label}[{index}]", minimum) for index, value in enumerate(values)]
    if not result or len(result) != len(set(result)):
        raise AssertionError(f"{label} must be nonempty and distinct")
    return result


def exact_probability(value: Any, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(value):
        raise AssertionError(f"{label} must be a finite real number")
    result = float(value)
    if not 0.0 < result <= 1.0:
        raise AssertionError(f"{label} must lie in (0,1]")
    return result


def assert_exact(actual: Any, expected: Any, path: str = "document") -> None:
    if type(actual) is not type(expected):
        raise AssertionError(
            f"{path}: type mismatch {type(actual).__name__} != {type(expected).__name__}"
        )
    if isinstance(expected, dict):
        if set(actual) != set(expected):
            raise AssertionError(
                f"{path}: key mismatch missing={sorted(set(expected) - set(actual))} "
                f"extra={sorted(set(actual) - set(expected))}"
            )
        for key in expected:
            assert_exact(actual[key], expected[key], f"{path}.{key}")
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            raise AssertionError(f"{path}: length mismatch {len(actual)} != {len(expected)}")
        for index, (observed, wanted) in enumerate(zip(actual, expected)):
            assert_exact(observed, wanted, f"{path}[{index}]")
    elif isinstance(expected, float):
        if not math.isfinite(actual) or actual != expected:
            raise AssertionError(f"{path}: float mismatch {actual!r} != {expected!r}")
    elif actual != expected:
        raise AssertionError(f"{path}: mismatch {actual!r} != {expected!r}")


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_tuple(value: list[int] | None) -> Point:
    if value is None:
        return None
    return exact_int(value[0], "point.x", 0), exact_int(value[1], "point.y", 0)


def point_sort_key(point: Point) -> tuple[int, int, int]:
    return (-1, 0, 0) if point is None else (0, point[0], point[1])


def j_invariant(p: int, a: int, b: int) -> int:
    four_a3 = 4 * pow(a, 3, p) % p
    denominator = (four_a3 + 27 * pow(b, 2, p)) % p
    if denominator == 0:
        raise AssertionError("singular curve")
    return 1728 * four_a3 * pow(denominator, -1, p) % p


def curve_rejection_reason(p: int, a: int, b: int, order: int) -> str | None:
    if (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p == 0:
        return "singular"
    trace = p + 1 - order
    if trace == 0:
        return "trace_zero"
    if trace == 1:
        return "anomalous_trace_one"
    if not ARITH.is_prime(order):
        return "composite_order"
    if j_invariant(p, a, b) in (0, 1728 % p):
        return "special_j"
    return None


def reconstruct_clean_curve(bits: int, seed: int, max_attempts: int = 256) -> dict[str, Any]:
    p = ARITH.field_prime(bits, seed ^ 0x6A09E667)
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
        counted_orders += 1
        order = ARITH.curve_order(p, a, b)
        rejection = curve_rejection_reason(p, a, b, order)
        if rejection is not None:
            rejections[rejection] += 1
            continue
        ops = VerifyOps()
        start = rng.randrange(p)
        generator: Point = None
        source_x: int | None = None
        for offset in range(p):
            x = (start + offset) % p
            y = ARITH.square_root((x * x * x + a * x + b) % p, p)
            if y is None:
                continue
            candidate = (x, y)
            if ARITH.point_mul(order, candidate, p, a, ops) is None:
                generator, source_x = candidate, x
                break
        if generator is None:
            continue
        factors = ARITH.prime_factors(p - 1)
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
            "generator_ops": asdict(ops),
            "p_minus_1_factors": factors,
            "p_minus_1_largest_prime_factor": max(factors),
            "rejections": rejections,
            "selection_policy": (
                "first seeded nonsingular prime-order curve with trace not in "
                "{0,1} and j not in {0,1728}"
            ),
        }
    raise AssertionError(f"clean prime-order curve search exhausted at {bits} bits")


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
    map_multiplications = 0
    map_inversions = 0
    if factor_base["name"] == "square_map":
        map_multiplications = square_root_tests
    elif factor_base["name"] == "rational_union":
        source = factor_base["fibers"][-1]["source"]
        final_t = source["t"]
        zero_t = (-source["e"]) % p
        map_inversions = final_t - int(zero_t < final_t)
        map_inversions += int(source["map"] == "mobius")
        map_multiplications = final_t + 1 + map_inversions
    diagnostics.update(
        {
            "legendre_exponentiations": square_root_tests,
            "square_root_exponentiations": successful_roots,
            "charged_pow_field_multiplications": (
                square_root_tests * binary_pow_field_multiplications((p - 1) // 2)
                + successful_roots
                * (binary_pow_field_multiplications((p + 1) // 4) + 1)
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


def sanitize_fibers(family: str, fibers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    allowed = {"kind", "x", "t", "c", "d", "e", "map", "draw_index"}
    result = []
    for ordinal, fiber in enumerate(fibers):
        source = {key: value for key, value in fiber["source"].items() if key in allowed}
        source["kind"] = family
        source["ordinal"] = ordinal
        result.append({"points": fiber["points"], "source": source})
    return result


def reconstruct_factor_base(
    family: str,
    p: int,
    a: int,
    b: int,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    arithmetic_name = {
        "random_scalar": "random",
        "scalar_progression": "scalar_progression_positive_control",
    }.get(family, family)
    raw = ARITH.raw_factor_base(arithmetic_name, p, a, b, q, generator, size, seed)
    record = {
        "name": family,
        "seed": seed,
        "size": size,
        "symmetry_mode": "sign_complete",
        "points": raw["points"],
        "fibers": sanitize_fibers(family, raw["fibers"]),
        "build_ops": raw["build_ops"],
        "build_diagnostics": raw["build_diagnostics"],
        "scalar_source_metadata_emitted": False,
        "solver_input_fields": ["points"],
    }
    record["charged_build_diagnostics"] = charged_build_diagnostics(record, p)
    record["digest"] = stable_digest(record)
    return record


def verify_witness(
    p: int,
    a: int,
    points: list[Point],
    witness: tuple[int, ...],
    target: Point,
    ops: Any | None = None,
) -> bool:
    recovered: Point = None
    for index in witness:
        recovered = ARITH.point_add(recovered, points[index], p, a, ops)
    return recovered == target


@dataclass
class Advice:
    mapping: dict[Point, list[tuple[int, int, int, int]]]
    record: dict[str, Any]


def reconstruct_advice(p: int, a: int, points: list[Point], witness_cap: int) -> Advice:
    ops = VerifyOps()
    pair_sums = {
        (left, right): ARITH.point_add(points[left], points[right], p, a, ops)
        for left in range(len(points))
        for right in range(left, len(points))
    }
    mapping: dict[Point, list[tuple[int, int, int, int]]] = {}
    multiplicities: dict[Point, int] = {}
    attempts = 0
    for witness in itertools.combinations_with_replacement(range(len(points)), 4):
        attempts += 1
        total = ARITH.point_add(
            pair_sums[(witness[0], witness[1])],
            pair_sums[(witness[2], witness[3])],
            p,
            a,
            ops,
        )
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
    point_bits = 1 + 2 * p.bit_length()
    index_bits = max(1, (len(points) - 1).bit_length())
    count_bits = max(1, witness_cap.bit_length())
    stored = sum(len(bucket) for bucket in mapping.values())
    artifact = {"factor_base": [point_json(point) for point in points], "advice": entries}
    multiplicity_values = list(multiplicities.values())
    record = {
        "witness_cap": witness_cap,
        "pair_multiset_attempts": math.comb(len(points) + 1, 2),
        "four_multiset_attempts": attempts,
        "expected_four_multiset_attempts": math.comb(len(points) + 3, 4),
        "four_sum_support_size": len(mapping),
        "stored_witness_count": stored,
        "discarded_witness_count": attempts - stored,
        "maximum_full_witness_multiplicity": max(multiplicity_values),
        "mean_full_witness_multiplicity": statistics.fmean(multiplicity_values),
        "multiplicity_histogram": {
            str(value): multiplicity_values.count(value)
            for value in sorted(set(multiplicity_values))
        },
        "build_ops": asdict(ops),
        "point_encoding_bits": point_bits,
        "factor_base_index_bits": index_bits,
        "payload_bit_lower_estimate": (
            len(points) * point_bits
            + len(mapping) * (point_bits + count_bits)
            + stored * 4 * index_bits
        ),
        "payload_model": (
            "fixed-width affine point keys, bounded witness counts, and raw "
            "factor-base indices; excludes hash-table and allocator overhead"
        ),
        "canonical_serialized_bytes": len(stable_json_bytes(artifact)),
        "python_deep_bytes": ARITH.deep_size({"points": points, "mapping": mapping}),
        "advice_digest": stable_digest(entries),
        "first_entries": entries[: min(4, len(entries))],
    }
    return Advice(mapping, record)


def exact_five_support(
    p: int,
    a: int,
    advice: dict[Point, list[tuple[int, int, int, int]]],
    points: list[Point],
) -> tuple[set[Point], VerifyOps]:
    ops = VerifyOps()
    support = {
        ARITH.point_add(partial, point, p, a, ops)
        for partial in advice
        for point in points
    }
    return support, ops


def query(
    p: int,
    a: int,
    target: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    limit: int,
) -> dict[str, Any]:
    ops = VerifyOps()
    relations: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    witness_verification_ops = VerifyOps()
    probes = 0
    reads = 0
    for final_index, point in enumerate(points):
        complement = ARITH.point_add(target, ARITH.point_neg(point, p), p, a, ops)
        probes += 1
        bucket = advice.get(complement)
        if bucket is None:
            continue
        for partial in bucket:
            reads += 1
            witness = tuple(sorted(partial + (final_index,)))
            if witness in seen:
                continue
            if not verify_witness(
                p, a, points, witness, target, witness_verification_ops
            ):
                raise AssertionError("independent witness check failed")
            seen.add(witness)
            relations.append(witness)
            if len(relations) == limit:
                break
        if len(relations) == limit:
            break
    point_bytes = math.ceil((1 + 2 * p.bit_length()) / 8)
    witness_bytes = math.ceil(4 * max(1, (len(points) - 1).bit_length()) / 8)
    return {
        "relations": relations,
        "ops": ops,
        "probes": probes,
        "witness_reads": reads,
        "logical_key_bytes_read": probes * point_bytes,
        "logical_witness_bytes_read": reads * witness_bytes,
        "witness_verification_audit_ops": witness_verification_ops,
    }


def audit_targets(
    p: int,
    a: int,
    q: int,
    generator: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    support: set[Point],
    descent_attempt_limit: int,
) -> dict[str, Any]:
    target: Point = None
    enumeration_ops = VerifyOps()
    query_ops = VerifyOps()
    witness_verification_ops = VerifyOps()
    probes = []
    reads = 0
    supported = 0
    first_witness = None
    transcript = []
    support_flags = []
    for scalar in range(q):
        result = query(p, a, target, points, advice, 1)
        accumulate_ops(query_ops, result["ops"])
        accumulate_ops(
            witness_verification_ops, result["witness_verification_audit_ops"]
        )
        probes.append(result["probes"])
        reads += result["witness_reads"]
        observed = bool(result["relations"])
        support_flags.append(observed)
        if observed != (target in support):
            raise AssertionError("independent target support mismatch")
        if observed:
            supported += 1
            if first_witness is None:
                first_witness = {
                    "target_scalar": scalar,
                    "target": point_json(target),
                    "indices": list(result["relations"][0]),
                }
        transcript.append(
            {
                "scalar": scalar,
                "supported": observed,
                "probes": result["probes"],
                "witness_reads": result["witness_reads"],
            }
        )
        target = ARITH.point_add(target, generator, p, a, enumeration_ops)
    if target is not None or supported != len(support):
        raise AssertionError("independent group enumeration mismatch")
    next_distance = q + 1
    distances = [q + 1] * q
    for index in range(2 * q - 1, -1, -1):
        if support_flags[index % q]:
            next_distance = 0
        else:
            next_distance += 1
        if index < q:
            distances[index] = next_distance
    capped_attempts = [min(distance + 1, descent_attempt_limit) for distance in distances]
    randomized_successes = sum(int(distance < descent_attempt_limit) for distance in distances)
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
        "total_witness_reads": reads,
        "probe_histogram": {str(value): probes.count(value) for value in sorted(set(probes))},
        "randomized_descent_attempt_limit": descent_attempt_limit,
        "exact_randomized_descent_success_probability": randomized_successes / q,
        "exact_randomized_descent_expected_capped_attempts": statistics.fmean(capped_attempts),
        "exact_randomized_descent_maximum_attempts_to_hit": max(distance + 1 for distance in distances),
        "transcript_sha256": stable_digest(transcript),
        "first_witness": first_witness,
    }


def coefficient_row(witness: tuple[int, ...], width: int, q: int) -> tuple[int, ...]:
    row = [0] * width
    for index in witness:
        row[index] = (row[index] + 1) % q
    return tuple(row)


@dataclass
class LinearOps:
    row_additions: int = 0
    field_additions: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0


class Basis:
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
            if not factor:
                continue
            prior, prior_rhs = self.rows[pivot]
            self.ops.row_additions += 1
            for column in range(pivot, self.width):
                row[column] = (row[column] - factor * prior[column]) % self.q
                self.ops.field_multiplications += 1
                self.ops.field_additions += 1
            value = (value - factor * prior_rhs) % self.q
            self.ops.field_multiplications += 1
            self.ops.field_additions += 1
        pivot = next((index for index, item in enumerate(row) if item), None)
        if pivot is None:
            if value:
                raise AssertionError("independent relation system inconsistent")
            return False
        inverse = pow(row[pivot], -1, self.q)
        self.ops.field_inversions += 1
        for column in range(pivot, self.width):
            row[column] = row[column] * inverse % self.q
            self.ops.field_multiplications += 1
        value = value * inverse % self.q
        self.ops.field_multiplications += 1
        self.rows[pivot] = row, value
        return True


def solve(equations: list[dict[str, Any]], width: int, q: int) -> tuple[list[int], LinearOps]:
    matrix = [list(row["coefficients"]) + [row["rhs"]] for row in equations]
    ops = LinearOps()
    pivot_row = 0
    for column in range(width):
        selected = next((row for row in range(pivot_row, len(matrix)) if matrix[row][column] % q), None)
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
            if not factor:
                continue
            ops.row_additions += 1
            for index in range(column, width + 1):
                matrix[row][index] = (matrix[row][index] - factor * matrix[pivot_row][index]) % q
                ops.field_multiplications += 1
                ops.field_additions += 1
        pivot_row += 1
        if pivot_row == width:
            break
    if pivot_row != width:
        raise AssertionError("independent relation system rank deficient")
    solution = [0] * width
    for row in matrix:
        pivot = next((index for index in range(width) if row[index] % q), None)
        if pivot is not None:
            solution[pivot] = row[-1] % q
    return solution, ops


def collect_relations(
    p: int,
    a: int,
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
    basis = Basis(len(points), q)
    target_ops = VerifyOps()
    query_ops = VerifyOps()
    witness_verification_ops = VerifyOps()
    traffic = {"key_bytes": 0, "witness_bytes": 0, "probes": 0, "witness_reads": 0}
    unique_rows: dict[tuple[int, ...], int] = {}
    independent = []
    supported = 0
    relation_count = 0
    trajectory = []
    transcript = []
    for attempt, scalar in enumerate(schedule[:target_budget], start=1):
        target = ARITH.point_mul(scalar, generator, p, a, target_ops)
        result = query(p, a, target, points, advice, relations_per_target)
        accumulate_ops(query_ops, result["ops"])
        accumulate_ops(
            witness_verification_ops, result["witness_verification_audit_ops"]
        )
        traffic["key_bytes"] += result["logical_key_bytes_read"]
        traffic["witness_bytes"] += result["logical_witness_bytes_read"]
        traffic["probes"] += result["probes"]
        traffic["witness_reads"] += result["witness_reads"]
        supported += int(bool(result["relations"]))
        relation_count += len(result["relations"])
        new_rows = 0
        rank_before = basis.rank
        row_digests = []
        for witness in result["relations"]:
            coefficients = coefficient_row(witness, len(points), q)
            row_digests.append(stable_digest([list(coefficients), scalar]))
            if coefficients in unique_rows:
                if unique_rows[coefficients] != scalar:
                    raise AssertionError("independent duplicate row RHS mismatch")
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
                independent.append(equation)
                new_rows += 1
                trajectory.append(
                    {
                        "attempted_targets": attempt,
                        "supported_targets": supported,
                        "unique_rows": len(unique_rows),
                        "rank": basis.rank,
                    }
                )
        transcript.append(
            {
                "attempt": attempt,
                "scalar": scalar,
                "relation_count": len(result["relations"]),
                "new_independent_rows": new_rows,
                "rank_before": rank_before,
                "rank_after": basis.rank,
                "probes": result["probes"],
                "row_digests": row_digests,
            }
        )
        if basis.rank == len(points):
            break
    full_rank = basis.rank == len(points)
    solution = None
    solve_ops = LinearOps()
    verify_ops = VerifyOps()
    verified = False
    if full_rank:
        solution, solve_ops = solve(independent, len(points), q)
        verified = all(
            ARITH.point_mul(scalar, generator, p, a, verify_ops) == point
            for scalar, point in zip(solution, points)
        )
        if not verified:
            raise AssertionError("independent factor-base log verification failed")
    return {
        "target_budget": target_budget,
        "target_schedule_sha256": stable_digest(schedule[:target_budget]),
        "targets_attempted": len(transcript),
        "supported_targets": supported,
        "relations_returned": relation_count,
        "unique_coefficient_rows": len(unique_rows),
        "rank": basis.rank,
        "full_rank": full_rank,
        "rank_trajectory": trajectory,
        "independent_equations": independent,
        "incremental_linear_ops": asdict(basis.ops),
        "solve_linear_ops": asdict(solve_ops),
        "target_generation_ops": asdict(target_ops),
        "query_ops": asdict(query_ops),
        "witness_verification_audit_ops": asdict(witness_verification_ops),
        "logical_traffic": traffic,
        "transcript_sha256": stable_digest(transcript),
        "factor_base_logs": solution,
        "solution_verification_ops": asdict(verify_ops),
        "factor_base_logs_verified": verified,
    }


def solve_individual(
    p: int,
    a: int,
    q: int,
    generator: Point,
    target: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    logs: list[int],
    seed: int,
    attempt_limit: int,
) -> dict[str, Any]:
    randomizer = random.Random(seed).randrange(q)
    randomization_ops = VerifyOps()
    query_ops = VerifyOps()
    witness_verification_ops = VerifyOps()
    verify_ops = VerifyOps()
    randomized = ARITH.point_add(
        target,
        ARITH.point_mul(randomizer, generator, p, a, randomization_ops),
        p,
        a,
        randomization_ops,
    )
    probes = key_bytes = witness_bytes = 0
    for attempt in range(1, attempt_limit + 1):
        result = query(p, a, randomized, points, advice, 1)
        accumulate_ops(query_ops, result["ops"])
        accumulate_ops(
            witness_verification_ops, result["witness_verification_audit_ops"]
        )
        probes += result["probes"]
        key_bytes += result["logical_key_bytes_read"]
        witness_bytes += result["logical_witness_bytes_read"]
        if result["relations"]:
            witness = result["relations"][0]
            recovered = (sum(logs[index] for index in witness) - randomizer) % q
            verified = ARITH.point_mul(recovered, generator, p, a, verify_ops) == target
            if not verified:
                raise AssertionError("independent descent verification failed")
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
                "verification_ops": asdict(verify_ops),
                "logical_probes": probes,
                "logical_key_bytes_read": key_bytes,
                "logical_witness_bytes_read": witness_bytes,
                "verified": verified,
            }
        randomized = ARITH.point_add(randomized, generator, p, a, randomization_ops)
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
        "verification_ops": asdict(verify_ops),
        "logical_probes": probes,
        "logical_key_bytes_read": key_bytes,
        "logical_witness_bytes_read": witness_bytes,
        "verified": False,
    }


def reconstruct_descent(
    p: int,
    a: int,
    q: int,
    generator: Point,
    points: list[Point],
    advice: dict[Point, list[tuple[int, int, int, int]]],
    logs: list[int] | None,
    seed: int,
    challenge_count: int,
    attempt_limit: int,
) -> dict[str, Any]:
    if logs is None:
        return {"status": "skipped_rank_deficient", "challenges": [], "all_verified": False}
    rng = random.Random(seed ^ 0x1F83D9AB)
    generation_ops = VerifyOps()
    challenges = []
    for index in range(challenge_count):
        known = rng.randrange(q)
        target = ARITH.point_mul(known, generator, p, a, generation_ops)
        result = solve_individual(
            p,
            a,
            q,
            generator,
            target,
            points,
            advice,
            logs,
            seed ^ (index + 1) * 0x9E3779B1,
            attempt_limit,
        )
        result.update(
            {
                "challenge_index": index,
                "target": point_json(target),
                "known_scalar_private_audit": known,
                "matches_private_scalar": result["recovered_scalar"] == known,
            }
        )
        challenges.append(result)
    return {
        "status": "completed",
        "challenges": challenges,
        "challenge_generation_audit_ops": asdict(generation_ops),
        "all_verified": all(
            challenge["success"] and challenge["verified"] and challenge["matches_private_scalar"]
            for challenge in challenges
        ),
    }


def sum_ops(*records: dict[str, int]) -> dict[str, int]:
    keys = set().union(*(record.keys() for record in records))
    return {key: sum(record.get(key, 0) for record in records) for key in sorted(keys)}


def reconstruct_matched_bsgs(
    p: int,
    a: int,
    q: int,
    generator: Point,
    advice_budget_bits: int,
    target_seed: int,
    challenge_count: int,
) -> dict[str, Any]:
    point_bits = 1 + 2 * p.bit_length()
    scalar_bits = q.bit_length()
    entry_bits = point_bits + scalar_bits
    table_capacity = max(1, min(q, (advice_budget_bits - point_bits) // entry_bits))
    if table_capacity * entry_bits + point_bits > advice_budget_bits:
        raise AssertionError("independent matched BSGS exceeds advice budget")
    offline_ops = VerifyOps()
    table: dict[Point, int] = {}
    current: Point = None
    for scalar in range(table_capacity):
        table[current] = scalar
        current = ARITH.point_add(current, generator, p, a, offline_ops)
    giant_step = current
    if len(table) != table_capacity:
        raise AssertionError("independent BSGS table collision")
    rng = random.Random(target_seed ^ 0x1F83D9AB)
    generation_ops = VerifyOps()
    verification_ops = VerifyOps()
    challenges = []
    giant_count = math.ceil(q / table_capacity)
    point_bytes = math.ceil(point_bits / 8)
    scalar_bytes = math.ceil(scalar_bits / 8)
    for challenge_index in range(challenge_count):
        known = rng.randrange(q)
        target = ARITH.point_mul(known, generator, p, a, generation_ops)
        gamma = target
        online_ops = VerifyOps()
        probes = 0
        recovered = None
        for giant_index in range(giant_count):
            probes += 1
            baby = table.get(gamma)
            if baby is not None:
                recovered = (giant_index * table_capacity + baby) % q
                break
            if giant_index + 1 < giant_count:
                gamma = ARITH.point_add(
                    gamma, ARITH.point_neg(giant_step, p), p, a, online_ops
                )
        verified = (
            recovered is not None
            and ARITH.point_mul(recovered, generator, p, a, verification_ops) == target
            and recovered == known
        )
        if not verified:
            raise AssertionError("independent matched BSGS challenge failed")
        challenges.append(
            {
                "challenge_index": challenge_index,
                "target": point_json(target),
                "known_scalar_private_audit": known,
                "recovered_scalar": recovered,
                "online_ops": asdict(online_ops),
                "table_probes": probes,
                "logical_bytes_read": probes * point_bytes + scalar_bytes,
                "verified": verified,
            }
        )
    online_values = [row["online_ops"]["group_operations"] for row in challenges]
    probe_values = [row["table_probes"] for row in challenges]
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
        "challenge_generation_audit_ops": asdict(generation_ops),
        "verification_audit_ops": asdict(verification_ops),
        "challenges": challenges,
        "all_verified": True,
        "average_online_group_operations": statistics.fmean(online_values),
        "maximum_online_group_operations": maximum_online,
        "worst_case_online_group_operation_bound": worst_case_online,
        "average_table_probes": statistics.fmean(probe_values),
        "maximum_table_probes": max(probe_values),
        "average_logical_bytes_read": statistics.fmean(
            row["logical_bytes_read"] for row in challenges
        ),
        "worst_case_frontier_score": advice_bits * worst_case_online**2 / q,
        "boundary": (
            "same disclosed advice-bit budget and scheduled toy targets; generic "
            "group-operation/table-probe baseline, not a hardware benchmark"
        ),
    }


def reconstruct_row(
    curve: dict[str, Any],
    family: str,
    size: int,
    factor_seed: int,
    target_seed: int,
    witness_cap: int,
    config: dict[str, Any],
) -> dict[str, Any]:
    p, a, b, q = curve["p"], curve["a"], curve["b"], curve["q"]
    generator = point_tuple(curve["generator"])
    factor_base = reconstruct_factor_base(family, p, a, b, q, generator, size, factor_seed)
    points = [point_tuple(point) for point in factor_base["points"]]
    advice = reconstruct_advice(p, a, points, witness_cap)
    support, support_ops = exact_five_support(p, a, advice.mapping, points)
    target_audit = audit_targets(
        p,
        a,
        q,
        generator,
        points,
        advice.mapping,
        support,
        config["descent_attempt_limit"],
    )
    relations = collect_relations(
        p,
        a,
        q,
        generator,
        points,
        advice.mapping,
        target_seed,
        config["relations_per_target"],
        config["relation_target_budget"],
    )
    descent = reconstruct_descent(
        p,
        a,
        q,
        generator,
        points,
        advice.mapping,
        relations["factor_base_logs"],
        target_seed,
        config["descent_challenges"],
        config["descent_attempt_limit"],
    )
    build_ops = factor_base["build_ops"]
    compiler_ops = advice.record["build_ops"]
    charged = factor_base["charged_build_diagnostics"]
    offline = {
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
    advice_bits = advice.record["payload_bit_lower_estimate"]
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
            8 * advice.record["canonical_serialized_bytes"] * maximum_t**2 / (epsilon * q)
        ),
        "python_deep_bits_worst_case_score": (
            8 * advice.record["python_deep_bytes"] * maximum_t**2 / (epsilon * q)
        ),
        "boundary": (
            "MODEL-BOUND diagnostic only: S uses disclosed bits or implementation "
            "bytes and T uses EC additions/probes; no lower-bound violation is claimed"
        ),
    }
    descent_records = [
        sum_ops(challenge["randomization_ops"], challenge["query_ops"])
        for challenge in descent["challenges"]
    ]
    aggregate_descent = sum_ops(*descent_records) if descent_records else asdict(VerifyOps())
    online_group_operations = [record["group_operations"] for record in descent_records]
    online_logical_bytes = [
        challenge["logical_key_bytes_read"] + challenge["logical_witness_bytes_read"]
        for challenge in descent["challenges"]
    ]
    preprocessing_group_operations = (
        offline["group_operations"]
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
        + config["descent_attempt_limit"] * len(points)
        + max(0, config["descent_attempt_limit"] - 1)
    )
    exact_randomized_epsilon = target_audit["exact_randomized_descent_success_probability"]
    fixed_curve_online = {
        "generator_fixed": True,
        "field_modulus_special_structure": "p mod 4 = 3 only; p-1 was not selected",
        "curve_special_structure": "trace not in {0,1}; j not in {0,1728}; prime order",
        "supported_one_query_targets": len(support),
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
            advice.record["canonical_serialized_bytes"] + math.ceil(factor_log_bits / 8)
        ),
        "full_online_advice_python_deep_bytes": (
            advice.record["python_deep_bytes"]
            + (
                ARITH.deep_size(relations["factor_base_logs"])
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
        "sampled_maximum_logical_bytes_read": max(online_logical_bytes) if online_logical_bytes else None,
        "descent_attempt_limit": config["descent_attempt_limit"],
        "exact_randomized_success_probability_at_limit": exact_randomized_epsilon,
        "exact_expected_capped_attempts": target_audit[
            "exact_randomized_descent_expected_capped_attempts"
        ],
        "worst_case_online_group_operation_bound": worst_case_online_group_bound,
        "full_advice_bits_worst_case_frontier_score": (
            full_advice_bits * worst_case_online_group_bound**2 / (exact_randomized_epsilon * q)
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
    matched_bsgs = reconstruct_matched_bsgs(
        p,
        a,
        q,
        generator,
        full_advice_bits,
        target_seed,
        config["descent_challenges"],
    )
    fixed_curve_online["matched_bsgs"] = {
        **matched_bsgs,
        "candidate_to_bsgs_average_online_group_operation_ratio": (
            sampled_online_average / matched_bsgs["average_online_group_operations"]
            if matched_bsgs["average_online_group_operations"]
            else None
        ),
        "candidate_to_bsgs_preprocessing_group_operation_ratio": (
            preprocessing_group_operations / matched_bsgs["offline_ops"]["group_operations"]
        ),
        "candidate_average_online_dominates_at_equal_advice": (
            sampled_online_average is not None
            and sampled_online_average < matched_bsgs["average_online_group_operations"]
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
    total_group = (
        offline["group_operations"]
        + relations["target_generation_ops"]["group_operations"]
        + relations["query_ops"]["group_operations"]
        + aggregate_descent["group_operations"]
    )
    total_attack_cost_vector = {
        "group_operations": total_group,
        "fp_field_multiplications": (
            offline["field_multiplications"]
            + relations["target_generation_ops"]["field_multiplications"]
            + relations["query_ops"]["field_multiplications"]
            + aggregate_descent["field_multiplications"]
        ),
        "fp_field_inversions": (
            offline["field_inversions"]
            + relations["target_generation_ops"]["field_inversions"]
            + relations["query_ops"]["field_inversions"]
            + aggregate_descent["field_inversions"]
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
    functional = relations["full_rank"] and relations["factor_base_logs_verified"] and descent["all_verified"]
    return {
        "family": family,
        "eligibility": "positive_control_only" if family == POSITIVE_CONTROL else "candidate_or_null",
        "factor_base": factor_base,
        "target_schedule_seed": target_seed,
        "witness_cap": witness_cap,
        "compiler": advice.record,
        "exact_five_sum_support_size": len(support),
        "exact_support_build_ops": asdict(support_ops),
        "target_audit": target_audit,
        "relations": relations,
        "descent": descent,
        "offline_charged_cost": offline,
        "aggregate_descent_attack_ops": aggregate_descent,
        "fixed_curve_online": fixed_curve_online,
        "rho_comparison": None,
        "total_attack_group_operations": total_group,
        "total_attack_cost_vector": total_attack_cost_vector,
        "preprocessing_frontier_diagnostic": frontier,
        "functional_gate_passed": functional,
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
    support_ratio = row["exact_five_sum_support_size"] / control["exact_five_sum_support_size"]
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


def attach_ratios(rows: list[dict[str, Any]]) -> None:
    random_x = {row["witness_cap"]: row for row in rows if row["family"] == "random_x"}
    random_scalar = {
        row["witness_cap"]: row for row in rows if row["family"] == "random_scalar"
    }
    if set(random_x) != set(random_scalar):
        raise AssertionError("both independent null families are required")
    for row in rows:
        random_x_ratios = row_ratios(row, random_x[row["witness_cap"]])
        random_scalar_ratios = row_ratios(row, random_scalar[row["witness_cap"]])
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
                and all(value <= 4.0 for value in ratios["offline_charged_cost"].values())
                for ratios in (random_x_ratios, random_scalar_ratios)
            )
        )


def aggregate_routing(
    instances: list[dict[str, Any]],
    bit_sizes: list[int],
    seeds: list[int],
    witness_caps: list[int],
) -> dict[str, Any]:
    pass_seeds = {
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


def reconstruct_rho(curve: dict[str, Any], seed: int, trials: int) -> dict[str, Any]:
    p, a, q = curve["p"], curve["a"], curve["q"]
    generator = point_tuple(curve["generator"])
    rng = random.Random(seed ^ 0x5BE0CD19)
    records = []
    for trial in range(trials):
        scalar = rng.randrange(1, q)
        target = ARITH.point_mul(scalar, generator, p, a)
        result = ARITH.replay_rho(p, a, q, generator, target, seed ^ trial * 0x27D4EB2D)
        if result["recovered_scalar"] != scalar:
            raise AssertionError("independent rho recovered wrong scalar")
        records.append({**result, "known_scalar": scalar, "target": point_json(target)})
    return {
        "trials": records,
        "average_group_operations": statistics.fmean(record["ops"]["group_operations"] for record in records),
        "all_verified": True,
    }


def fit_log_slope(rows: list[tuple[int, float]]) -> float | None:
    if len(rows) < 3 or any(value <= 0 for _, value in rows):
        return None
    xs = [math.log(q) for q, _ in rows]
    ys = [math.log(value) for _, value in rows]
    x_mean, y_mean = statistics.fmean(xs), statistics.fmean(ys)
    denominator = sum((value - x_mean) ** 2 for value in xs)
    if denominator == 0:
        return None
    return sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys)) / denominator


def validate_config(config: Any, enforce_frozen: bool) -> dict[str, Any]:
    if not isinstance(config, dict) or set(config) != set(FROZEN_CONFIG):
        raise AssertionError("configuration keys do not match protocol")
    bit_sizes = exact_int_list(config["bit_sizes"], "bit_sizes", 5)
    seeds = exact_int_list(config["seeds"], "seeds", 0)
    witness_caps = exact_int_list(config["witness_caps"], "witness_caps", 1)
    families = config["families"]
    if not isinstance(families, list) or not families or len(families) != len(set(families)):
        raise AssertionError("families must be nonempty and distinct")
    if any(family not in ALL_FAMILIES for family in families) or not {
        "random_x",
        "random_scalar",
    }.issubset(families):
        raise AssertionError("invalid family configuration")
    result = {
        "bit_sizes": bit_sizes,
        "seeds": seeds,
        "families": families,
        "witness_caps": witness_caps,
        "occupancy_lambda": exact_probability(config["occupancy_lambda"], "occupancy_lambda"),
        "relations_per_target": exact_int(config["relations_per_target"], "relations_per_target", 1),
        "relation_target_budget": exact_int(config["relation_target_budget"], "relation_target_budget", 0),
        "descent_challenges": exact_int(config["descent_challenges"], "descent_challenges", 1),
        "descent_attempt_limit": exact_int(config["descent_attempt_limit"], "descent_attempt_limit", 1),
        "rho_trials": exact_int(config["rho_trials"], "rho_trials", 1),
    }
    if enforce_frozen and result != FROZEN_CONFIG:
        raise AssertionError("canonical verification requires the frozen configuration")
    return result


def reconstruct_document(config: dict[str, Any]) -> dict[str, Any]:
    instances = []
    used_primes: set[int] = set()
    for bits in config["bit_sizes"]:
        for seed in config["seeds"]:
            curve = reconstruct_clean_curve(bits, seed + bits * 1009)
            if curve["p"] in used_primes:
                raise AssertionError("independent field modulus repetition")
            used_primes.add(curve["p"])
            size = choose_factor_base_size(curve["q"], config["occupancy_lambda"])
            target_seed = seed ^ bits * 0x7FEB352D
            rows = []
            for family_index, family in enumerate(config["families"]):
                factor_seed = seed ^ bits * 0x45D9F3B ^ family_index * 0x9E3779B1
                for cap in config["witness_caps"]:
                    rows.append(reconstruct_row(curve, family, size, factor_seed, target_seed, cap, config))
            attach_ratios(rows)
            rho = reconstruct_rho(curve, seed, config["rho_trials"])
            attach_rho_comparison(rows, rho)
            instances.append(
                {
                    "seed": seed,
                    "curve": curve,
                    "factor_base_size": size,
                    "sizing_rule": (
                        "smallest sign-complete even B with exact signed formal "
                        "five-term class count divided by q at least occupancy_lambda"
                    ),
                    "signed_five_term_class_count": signed_class_count(size // 2, 5),
                    "occupancy_lambda": config["occupancy_lambda"],
                    "rows": rows,
                    "rho": rho,
                }
            )
    routing_summary = aggregate_routing(
        instances, config["bit_sizes"], config["seeds"], config["witness_caps"]
    )
    slopes = {}
    cost_slopes = {}
    for family in config["families"]:
        slopes[family] = {}
        cost_slopes[family] = {}
        for cap in config["witness_caps"]:
            selected_rows = [
                (instance["curve"]["q"], row)
                for instance in instances
                for row in instance["rows"]
                if row["family"] == family and row["witness_cap"] == cap
            ]
            slopes[family][str(cap)] = fit_log_slope(
                [(q, row["total_attack_group_operations"]) for q, row in selected_rows]
            )
            cost_slopes[family][str(cap)] = {
                "group_operations": slopes[family][str(cap)],
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
        "fixed_curve_compiler_sha256": sha256_file(GENERATOR_PATH),
        "coordinate_energy_sha256": sha256_file(ENERGY_PATH),
        "contract_sha256": sha256_file(CONTRACT_PATH),
        "hypothesis_sha256": sha256_file(HYPOTHESIS_PATH),
        "literature_sha256": sha256_file(LITERATURE_PATH),
    }
    routing_rows = [
        {"curve_id": instance["curve"]["id"], "family": row["family"], "witness_cap": row["witness_cap"]}
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
        "routing_rows": routing_rows,
        "routing_summary": routing_summary,
        "global_controls": {
            "all_curves_clean": all(
                instance["curve"]["trace"] not in (0, 1)
                and instance["curve"]["j_invariant"] not in (0, 1728 % instance["curve"]["p"])
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
            "functional_result": "A full-rank verified row is a toy end-to-end index-calculus path only.",
            "routing_result": "A routing row is a matched-control signal requiring a larger successor.",
            "breakthrough_result": "No sub-rho claim is permitted without a later all-cost fitted exponent below 0.5.",
        },
    }


def verify_document(document: Any, enforce_frozen: bool = True) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise AssertionError("result must be an object")
    config = validate_config(document.get("configuration"), enforce_frozen)
    expected = reconstruct_document(config)
    assert_exact(document, expected)
    return {
        "verification_protocol": VERIFIER_PROTOCOL,
        "status": "verified",
        "canonical_configuration": config == FROZEN_CONFIG,
        "development_only": config != FROZEN_CONFIG,
        "generator_sha256": sha256_file(GENERATOR_PATH),
        "verifier_sha256": sha256_file(SCRIPT_PATH),
        "independent_arithmetic_sha256": sha256_file(ARITHMETIC_PATH),
        "verified_instances": len(expected["instances"]),
        "verified_rows": sum(len(instance["rows"]) for instance in expected["instances"]),
        "routing_rows": expected["routing_rows"],
        "claim_boundary": (
            "Verification establishes deterministic toy pipeline correctness only; "
            "it does not establish a sub-rho exponent or deployed-curve break."
        ),
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--allow-development", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    document, input_hash = load_strict_json(args.input)
    certificate = verify_document(document, enforce_frozen=not args.allow_development)
    certificate["input_sha256"] = input_hash
    print(json.dumps(certificate, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
