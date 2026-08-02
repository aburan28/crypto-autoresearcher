#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import random
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


SCRIPT_PATH = Path(__file__).resolve()
RECURSIVE_SOURCE = (
    SCRIPT_PATH.parents[2]
    / "EXP-ECDLP-RECURSIVE-001"
    / "src"
    / "recursive_expansion.py"
)
Point = tuple[int, int] | None
CANDIDATES = (
    "coset_prefix_chain",
    "quartic_composition_chain",
    "reciprocal_denominator_chain",
)
CONFIRMATORY_BITS = [10, 12, 14]
CONFIRMATORY_NULL_DRAWS = 2047
CONFIRMATORY_PREDICTOR_PERMUTATIONS = 127
CONFIRMATORY_NEGATIVE_CONTROL_REPLICATES = 8
REGISTERED_DEVELOPMENT_BITS = [8, 9, 10]
REGISTERED_DEVELOPMENT_CURVE_SEEDS = [2203, 2309, 2411]
REGISTERED_DEVELOPMENT_NULL_DRAWS = 3
REGISTERED_DEVELOPMENT_PREDICTOR_PERMUTATIONS = 127
REGISTERED_DEVELOPMENT_NEGATIVE_CONTROL_REPLICATES = 8
SEED_LOCK_DOMAIN = (
    "EXP-ECDLP-COORD-EXPANSION-001-COORD-ENERGY-CERT-V2.1-SEED"
)
SEED_LOCK_PATH = (
    SCRIPT_PATH.parents[1]
    / "development"
    / "COORD-ENERGY-CERT-V2.1"
    / "confirmatory-seed-lock.json"
)
MIN_BUCKET_COVERAGE_NUMERATOR = 1
MIN_BUCKET_COVERAGE_DENOMINATOR = 100


def load_recursive() -> Any:
    spec = importlib.util.spec_from_file_location(
        "recursive_expansion_coord_energy_v2", RECURSIVE_SOURCE
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {RECURSIVE_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RECURSIVE = load_recursive()


def file_hash(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            state.update(block)
    return state.hexdigest()


def load_seed_lock() -> dict[str, Any] | None:
    if not SEED_LOCK_PATH.exists():
        return None
    lock = json.loads(SEED_LOCK_PATH.read_text(encoding="ascii"))
    required = {
        "protocol",
        "freeze_commit",
        "derivation_domain",
        "curve_seeds",
        "construction_command",
    }
    if set(lock) != required:
        raise ValueError("confirmatory seed lock has unexpected fields")
    if (
        lock["protocol"]
        != "EXP-ECDLP-COORD-EXPANSION-001-coord-energy-cert-v2.1"
        or lock["derivation_domain"] != SEED_LOCK_DOMAIN
        or not isinstance(lock["freeze_commit"], str)
        or len(lock["freeze_commit"]) != 40
        or any(character not in "0123456789abcdef"
               for character in lock["freeze_commit"])
        or not isinstance(lock["construction_command"], str)
        or not isinstance(lock["curve_seeds"], list)
        or len(lock["curve_seeds"]) != 3
        or any(
            type(seed) is not int or seed < 1 or seed >= 2**31 - 1
            for seed in lock["curve_seeds"]
        )
        or len(set(lock["curve_seeds"])) != 3
    ):
        raise ValueError("invalid confirmatory seed lock")
    derived = []
    for index in range(3):
        encoded = (
            f"{SEED_LOCK_DOMAIN}|{lock['freeze_commit']}|{index}"
        ).encode("ascii")
        value = int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")
        derived.append(1 + value % (2**31 - 2))
    if lock["curve_seeds"] != derived:
        raise ValueError("confirmatory seed derivation mismatch")
    return lock


def digest(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode("ascii")
    ).hexdigest()


def stable_seed(*parts: Any) -> int:
    encoded = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "big")


def rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if platform.system() == "Darwin" else value * 1024)


def encode_point(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def decode_point(point: list[int] | None) -> Point:
    return None if point is None else (int(point[0]), int(point[1]))


def ec_add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        numerator = (3 * x1 * x1 + a) % p
        denominator = 2 * y1 % p
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
    slope = numerator * pow(denominator, p - 2, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def subgroup_census(
    generator: Point, q: int, p: int, a: int
) -> tuple[list[Point], dict[Point, int]]:
    points: list[Point] = []
    by_point: dict[Point, int] = {}
    current: Point = None
    for scalar in range(q):
        if current in by_point:
            raise ValueError("generator repeated before q")
        points.append(current)
        by_point[current] = scalar
        current = ec_add(current, generator, p, a)
    if current is not None or len(points) != q:
        raise ValueError("generator does not have recorded order")
    return points, by_point


def canonical_point(point: Point, p: int) -> Point:
    if point is None:
        return None
    x_coord, y_coord = point
    return x_coord, min(y_coord, (-y_coord) % p)


def point_for_x(curve: dict[str, Any], x_coord: int) -> Point:
    p, a, b = curve["p"], curve["a"], curve["b"]
    rhs = (x_coord**3 + a * x_coord + b) % p
    y_coord = pow(rhs, (p + 1) // 4, p)
    if y_coord * y_coord % p != rhs:
        return None
    return x_coord, min(y_coord, (-y_coord) % p)


def divisors(value: int) -> list[int]:
    small = []
    large = []
    divisor = 1
    while divisor * divisor <= value:
        if value % divisor == 0:
            small.append(divisor)
            if divisor * divisor != value:
                large.append(value // divisor)
        divisor += 1
    return small + list(reversed(large))


def prime_factors(value: int) -> list[int]:
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            factors.append(divisor)
            value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        factors.append(value)
    return factors


def primitive_root(p: int) -> tuple[int, int]:
    factors = set(prime_factors(p - 1))
    exponentiations = 0
    for candidate in range(2, p):
        valid = True
        for factor in factors:
            exponentiations += 1
            if pow(candidate, (p - 1) // factor, p) == 1:
                valid = False
                break
        if valid:
            return candidate, exponentiations
    raise RuntimeError("primitive root not found")


@dataclass
class BuildCounters:
    x_candidates: int = 0
    square_root_tests: int = 0
    inversions: int = 0
    legendre_tests: int = 0
    duplicate_x: int = 0
    rejected_noncurve_x: int = 0
    rejected_stratum: int = 0
    field_additions: int = 0
    field_multiplications: int = 0
    field_squarings: int = 0
    modular_exponentiations: int = 0
    subgroup_step_multiplications: int = 0
    primitive_root_test_exponentiations: int = 0


def append_candidate(
    curve: dict[str, Any],
    x_coord: int,
    source: dict[str, Any],
    selected: list[dict[str, Any]],
    seen_x: set[int],
    counters: BuildCounters,
) -> None:
    counters.x_candidates += 1
    if x_coord in seen_x:
        counters.duplicate_x += 1
        return
    seen_x.add(x_coord)
    counters.square_root_tests += 1
    counters.field_multiplications += 4
    counters.field_additions += 2
    counters.modular_exponentiations += 1
    point = point_for_x(curve, x_coord)
    if point is None:
        counters.rejected_noncurve_x += 1
        return
    selected.append(
        {
            "point": encode_point(point),
            "source": source,
        }
    )


def make_coset_prefix(
    curve: dict[str, Any],
    b_size: int,
    seed: int,
) -> dict[str, Any]:
    p = curve["p"]
    counters = BuildCounters()
    order = max(
        divisor for divisor in divisors(p - 1) if divisor <= 2 * b_size
    )
    root, root_tests = primitive_root(p)
    counters.primitive_root_test_exponentiations += root_tests
    subgroup_generator = pow(root, (p - 1) // order, p)
    counters.modular_exponentiations += 1
    quotient = (p - 1) // order
    offset = seed % quotient
    step = 1 + (seed // max(1, quotient)) % max(1, quotient)
    while math.gcd(step, quotient) != 1:
        step += 1
    selected: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    coset_records = []
    for coset_rank in range(quotient):
        coset_index = (offset + coset_rank * step) % quotient
        representative = pow(root, coset_index, p)
        tag = pow(representative, order, p)
        counters.modular_exponentiations += 2
        coset_records.append(
            {
                "rank": coset_rank,
                "index": coset_index,
                "representative": representative,
                "tag": tag,
            }
        )
        current = representative
        for subgroup_rank in range(order):
            append_candidate(
                curve,
                current,
                {
                    "coset_rank": coset_rank,
                    "coset_index": coset_index,
                    "subgroup_rank": subgroup_rank,
                    "coset_tag": tag,
                    "x": current,
                },
                selected,
                seen_x,
                counters,
            )
            if len(selected) == b_size:
                break
            current = current * subgroup_generator % p
            counters.field_multiplications += 1
            counters.subgroup_step_multiplications += 1
        if len(selected) == b_size:
            break
    if len(selected) != b_size:
        raise RuntimeError("coset-prefix chain exhausted")
    return {
        "family": "coset_prefix_chain",
        "seed": seed,
        "b_size": b_size,
        "points": [record["point"] for record in selected],
        "sources": [record["source"] for record in selected],
        "public_parameters": {
            "primitive_root": root,
            "subgroup_order": order,
            "subgroup_generator": subgroup_generator,
            "quotient_order": quotient,
            "coset_offset": offset,
            "coset_step": step,
            "visited_cosets": coset_records,
            "truncation_boundary": selected[-1]["source"],
        },
        "build_counters": counters.__dict__,
    }


def make_quartic_chain(
    curve: dict[str, Any],
    b_size: int,
    seed: int,
) -> dict[str, Any]:
    p = curve["p"]
    rng = random.Random(seed)
    c, d, e = (rng.randrange(p) for _ in range(3))
    selected: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    counters = BuildCounters()
    for t_value in range(8 * p):
        u_value = (t_value + c) % p
        v_value = (u_value * u_value + d) % p
        x_coord = (v_value * v_value + e) % p
        counters.field_additions += 3
        counters.field_squarings += 2
        append_candidate(
            curve,
            x_coord,
            {
                "t": t_value,
                "u": u_value,
                "v": v_value,
                "x": x_coord,
            },
            selected,
            seen_x,
            counters,
        )
        if len(selected) == b_size:
            break
    if len(selected) != b_size:
        raise RuntimeError("quartic chain exhausted")
    return {
        "family": "quartic_composition_chain",
        "seed": seed,
        "b_size": b_size,
        "points": [record["point"] for record in selected],
        "sources": [record["source"] for record in selected],
        "public_parameters": {
            "c": c,
            "d": d,
            "e": e,
            "truncation_t": selected[-1]["source"]["t"],
        },
        "build_counters": counters.__dict__,
    }


def legendre(value: int, p: int) -> int:
    value %= p
    if value == 0:
        return 0
    return 1 if pow(value, (p - 1) // 2, p) == 1 else -1


def make_reciprocal_chain(
    curve: dict[str, Any],
    b_size: int,
    seed: int,
) -> dict[str, Any]:
    p = curve["p"]
    rng = random.Random(seed)
    c, d, e = (rng.randrange(p) for _ in range(3))
    stratum = 1 if rng.randrange(2) else -1
    selected: list[dict[str, Any]] = []
    seen_x: set[int] = set()
    counters = BuildCounters()
    for t_value in range(16 * p):
        u_value = (t_value + c) % p
        denominator = (t_value + d) % p
        counters.field_additions += 2
        if denominator == 0:
            continue
        counters.legendre_tests += 1
        counters.modular_exponentiations += 1
        denominator_chi = legendre(denominator, p)
        if denominator_chi != stratum:
            counters.rejected_stratum += 1
            continue
        inverse = pow(denominator, p - 2, p)
        counters.inversions += 1
        counters.modular_exponentiations += 1
        numerator = u_value * u_value % p
        x_coord = (numerator * inverse + e) % p
        counters.field_additions += 1
        counters.field_squarings += 1
        counters.field_multiplications += 1
        append_candidate(
            curve,
            x_coord,
            {
                "t": t_value,
                "u": u_value,
                "numerator": numerator,
                "denominator": denominator,
                "denominator_inverse": inverse,
                "denominator_character": denominator_chi,
                "x": x_coord,
            },
            selected,
            seen_x,
            counters,
        )
        if len(selected) == b_size:
            break
    if len(selected) != b_size:
        raise RuntimeError("reciprocal-denominator chain exhausted")
    return {
        "family": "reciprocal_denominator_chain",
        "seed": seed,
        "b_size": b_size,
        "points": [record["point"] for record in selected],
        "sources": [record["source"] for record in selected],
        "public_parameters": {
            "c": c,
            "d": d,
            "e": e,
            "denominator_character_stratum": stratum,
            "truncation_t": selected[-1]["source"]["t"],
        },
        "build_counters": counters.__dict__,
    }


def make_factor_base(
    family: str,
    curve: dict[str, Any],
    b_size: int,
    seed: int,
) -> dict[str, Any]:
    builders = {
        "coset_prefix_chain": make_coset_prefix,
        "quartic_composition_chain": make_quartic_chain,
        "reciprocal_denominator_chain": make_reciprocal_chain,
    }
    result = builders[family](curve, b_size, seed)
    points = [decode_point(point) for point in result["points"]]
    if None in points or len(points) != len(set(points)):
        raise AssertionError("factor base points are not distinct nonidentity")
    result["point_set_digest"] = digest(result["points"])
    result["construction_digest"] = digest(
        {key: value for key, value in result.items() if key != "construction_digest"}
    )
    result["construction_used_scalar_census"] = False
    return result


def ordered_d2(scalars: tuple[int, ...], q: int) -> Counter[int]:
    return Counter((left + right) % q for left in scalars for right in scalars)


def ordered_d4(d2: Counter[int], q: int) -> Counter[int]:
    result: Counter[int] = Counter()
    for left, left_count in d2.items():
        for right, right_count in d2.items():
            result[(left + right) % q] += left_count * right_count
    return result


def histogram(counts: Counter[int]) -> dict[str, int]:
    return {
        str(value): count
        for value, count in sorted(Counter(counts.values()).items())
    }


def fourier_witness(
    scalars: tuple[int, ...], q: int
) -> dict[str, Any]:
    indicator = np.zeros(q, dtype=np.float64)
    indicator[list(scalars)] = 1.0
    transform = np.fft.fft(indicator)
    half = transform[1 : (q + 1) // 2]
    magnitudes = np.abs(half)
    index = int(np.argmax(magnitudes))
    frequency = index + 1
    coefficient = transform[frequency]
    conjugate = transform[q - frequency]
    return {
        "frequency": frequency,
        "real": round(float(coefficient.real), 12),
        "imag": round(float(coefficient.imag), 12),
        "magnitude": round(float(abs(coefficient)), 12),
        "magnitude_normalized": round(
            float(abs(coefficient)) / len(scalars), 12
        ),
        "conjugate_real": round(float(conjugate.real), 12),
        "conjugate_imag": round(float(conjugate.imag), 12),
        "conjugate_error": round(
            float(abs(conjugate - coefficient.conjugate())), 15
        ),
        "method": "numpy_fft_indicator_length_q",
        "replay_absolute_tolerance": 1e-9,
    }


def popular_difference_witness(
    scalars: tuple[int, ...],
    q: int,
    census: list[Point] | None = None,
) -> dict[str, Any]:
    counts: Counter[int] = Counter()
    for left in scalars:
        for right in scalars:
            if left != right:
                counts[(left - right) % q] += 1
    def difference_sort(item: tuple[int, int]) -> tuple[Any, ...]:
        difference, count = item
        if census is None:
            return -count, difference
        point = census[difference]
        point_key = (-1, 0, 0) if point is None else (0, point[0], point[1])
        return (-count, *point_key)

    top = sorted(counts.items(), key=difference_sort)[: len(scalars)]
    top_set = {difference for difference, _ in top}
    top_rank = {
        difference: index for index, (difference, _) in enumerate(top)
    }
    edges = []
    adjacency = {index: set() for index in range(len(scalars))}
    for left_index, left in enumerate(scalars):
        for right_index, right in enumerate(scalars):
            if left_index == right_index:
                continue
            difference = (left - right) % q
            if difference in top_set:
                edges.append(
                    [left_index, right_index, top_rank[difference]]
                )
                adjacency[left_index].add(right_index)
                adjacency[right_index].add(left_index)
    components = []
    unseen = set(adjacency)
    while unseen:
        root = min(unseen)
        stack = [root]
        component = []
        unseen.remove(root)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency[current], reverse=True):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    denominator = len(scalars) * (len(scalars) - 1)
    concentration = (
        sum(count for _, count in top) / denominator if denominator else 0.0
    )
    public_top = [
        {
            "difference_point": (
                encode_point(census[difference])
                if census is not None
                else None
            ),
            "count": count,
        }
        for difference, count in top
    ]
    return {
        "top_differences": [
            {
                "diagnostic_scalar_difference": difference,
                "difference_point": public_top[index][
                    "difference_point"
                ],
                "count": count,
            }
            for index, (difference, count) in enumerate(top)
        ],
        "edges": edges,
        "edge_density": round(len(edges) / max(1, denominator), 12),
        "top_b_count_sum": sum(count for _, count in top),
        "ordered_nonzero_pair_total": denominator,
        "top_b_concentration": round(concentration, 12),
        "component_sizes": sorted(
            (len(component) for component in components), reverse=True
        ),
        "public_witness_digest": digest(
            {
                "top": public_top,
                "edges": edges,
                "component_sizes": sorted(
                    (len(component) for component in components),
                    reverse=True,
                ),
            }
        ),
        "diagnostic_witness_digest": digest(
            {"top": top, "edges": edges, "components": components}
        ),
    }


def canonical_relation(vector: Iterable[int]) -> tuple[int, ...] | None:
    values = tuple(int(value) for value in vector)
    for value in values:
        if value == 0:
            continue
        return values if value > 0 else tuple(-item for item in values)
    return None


def independent_relation_basis(
    relations: Iterable[tuple[int, ...]]
) -> list[tuple[int, ...]]:
    pivots: dict[int, list[Fraction]] = {}
    originals: list[tuple[int, ...]] = []
    for relation in sorted(set(relations)):
        row = [Fraction(value) for value in relation]
        for pivot in sorted(pivots):
            if row[pivot]:
                factor = row[pivot]
                row = [
                    value - factor * base
                    for value, base in zip(row, pivots[pivot])
                ]
        nonzero = next(
            (index for index, value in enumerate(row) if value), None
        )
        if nonzero is None:
            continue
        scale = row[nonzero]
        row = [value / scale for value in row]
        for pivot, base in list(pivots.items()):
            if base[nonzero]:
                factor = base[nonzero]
                pivots[pivot] = [
                    value - factor * item
                    for value, item in zip(base, row)
                ]
        pivots[nonzero] = row
        originals.append(relation)
    return originals


def freiman_witness(
    scalars: tuple[int, ...], q: int
) -> dict[str, Any]:
    by_sum: dict[int, list[tuple[int, ...]]] = defaultdict(list)
    b_size = len(scalars)
    for left in range(b_size):
        for right in range(left, b_size):
            vector = [0] * b_size
            vector[left] += 1
            vector[right] += 1
            by_sum[(scalars[left] + scalars[right]) % q].append(tuple(vector))
    relations: set[tuple[int, ...]] = set()
    for vectors in by_sum.values():
        if len(vectors) < 2:
            continue
        anchor = vectors[0]
        for vector in vectors[1:]:
            relation = canonical_relation(
                left - right for left, right in zip(vector, anchor)
            )
            if relation is not None:
                relations.add(relation)
    basis = independent_relation_basis(relations)
    rank = len(basis)
    dimension = b_size - rank - 1
    return {
        "relation_count": len(relations),
        "relation_rank": rank,
        "dimension": dimension,
        "basis": [list(vector) for vector in basis],
        "basis_digest": digest([list(vector) for vector in basis]),
    }


def set_metrics(
    scalars: Iterable[int],
    q: int,
    retain_witnesses: bool,
    census: list[Point] | None = None,
) -> tuple[dict[str, Any], Counter[int]]:
    ordered = tuple(int(value) % q for value in scalars)
    if len(set(ordered)) != len(ordered):
        raise ValueError("scalar set is not distinct")
    b_size = len(ordered)
    d2 = ordered_d2(ordered, q)
    d4 = ordered_d4(d2, q)
    e2 = sum(value * value for value in d2.values())
    e4 = sum(value * value for value in d4.values())
    fourier = fourier_witness(ordered, q)
    differences = popular_difference_witness(
        ordered, q, census if retain_witnesses else None
    )
    freiman = freiman_witness(ordered, q)
    metrics: dict[str, Any] = {
        "b_size": b_size,
        "scalar_set_digest": digest(list(ordered)),
        "d2": {
            "representation_total": sum(d2.values()),
            "support": len(d2),
            "energy": e2,
            "normalized_energy_e2_over_b3": round(e2 / b_size**3, 12),
            "spectral_l4_e2_over_b4": round(e2 / b_size**4, 12),
            "maximum_multiplicity": max(d2.values()),
        },
        "d4": {
            "representation_total": sum(d4.values()),
            "support": len(d4),
            "energy": e4,
            "normalized_energy_e4_over_b7": round(e4 / b_size**7, 12),
            "maximum_multiplicity": max(d4.values()),
        },
        "fourier_magnitude_normalized": fourier["magnitude_normalized"],
        "popular_difference_density": differences[
            "top_b_concentration"
        ],
        "popular_difference_top_b_count_sum": differences[
            "top_b_count_sum"
        ],
        "freiman_dimension": freiman["dimension"],
        "freiman_relation_rank": freiman["relation_rank"],
        "freiman_relation_count": freiman["relation_count"],
        "diagnostic_classification": "DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE",
    }
    if retain_witnesses:
        metrics["d2"]["histogram"] = histogram(d2)
        metrics["d4"]["histogram"] = histogram(d4)
        metrics["certificates"] = {
            "fourier": fourier,
            "popular_difference": differences,
            "freiman": freiman,
            "encoding_words": {
                "fourier": 5,
                "popular_difference": (
                    2 * len(differences["top_differences"])
                    + 3 * len(differences["edges"])
                    + len(differences["component_sizes"])
                ),
                "freiman": sum(
                    sum(value != 0 for value in vector)
                    for vector in freiman["basis"]
                ),
            },
        }
    return metrics, d4


def random_canonical_scalar_set(
    q: int,
    b_size: int,
    p: int,
    census: list[Point],
    by_point: dict[Point, int],
    seed: int,
) -> tuple[tuple[int, ...], int]:
    rng = random.Random(seed)
    scalars: set[int] = set()
    attempts = 0
    while len(scalars) < b_size:
        attempts += 1
        sampled_scalar = rng.randrange(1, q)
        point = canonical_point(census[sampled_scalar], p)
        if point is None:
            continue
        scalars.add(by_point[point])
    return tuple(sorted(scalars)), attempts


def empirical_rank(
    candidate: float | int,
    null_values: list[float | int],
    direction: str,
) -> dict[str, Any]:
    if direction == "high":
        extreme = sum(value >= candidate for value in null_values)
        ties = sum(value == candidate for value in null_values)
        wins = sum(candidate > value for value in null_values)
    elif direction == "low":
        extreme = sum(value <= candidate for value in null_values)
        ties = sum(value == candidate for value in null_values)
        wins = sum(candidate < value for value in null_values)
    else:
        raise ValueError(f"unknown direction: {direction}")
    return {
        "candidate": candidate,
        "direction": direction,
        "null_draws": len(null_values),
        "extreme_or_tied": extreme,
        "ties": ties,
        "rank_p": round((1 + extreme) / (1 + len(null_values)), 12),
        "reference_tail_rank": round(
            (1 + extreme) / (1 + len(null_values)), 12
        ),
        "interpretation": (
            "canonical_random_reference_tail_not_exchangeability_p_value"
        ),
        "tie_aware_auc": round(
            (wins + 0.5 * ties) / len(null_values), 12
        ),
        "null_min": min(null_values),
        "null_median": sorted(null_values)[len(null_values) // 2],
        "null_max": max(null_values),
        "null_values_digest": digest(null_values),
    }


def holm(
    tests: list[dict[str, Any]], alpha: float
) -> list[dict[str, Any]]:
    ordered = sorted(tests, key=lambda row: (row["p"], row["id"]))
    count = len(ordered)
    previous_adjusted = 0.0
    still_rejecting = True
    results = []
    for index, row in enumerate(ordered):
        rank = index + 1
        multiplier = count - index
        adjusted = min(1.0, max(previous_adjusted, multiplier * row["p"]))
        critical = alpha / multiplier
        reject = still_rejecting and row["p"] <= critical
        if not reject:
            still_rejecting = False
        previous_adjusted = adjusted
        results.append(
            {
                **row,
                "holm_rank": rank,
                "critical_value": round(critical, 12),
                "adjusted_p": round(adjusted, 12),
                "reject": reject,
            }
        )
    return results


def feature_map(
    point: Point,
    curve: dict[str, Any],
    factor_base: dict[str, Any],
) -> dict[str, str]:
    p, a, b = curve["p"], curve["a"], curve["b"]
    points = [decode_point(value) for value in factor_base["points"]]
    factor_x = {value[0] for value in points if value is not None}
    if point is None:
        return {
            "infinity": "1",
            "x_bin_8": "O",
            "y_bin_8": "O",
            "chi_x": "O",
            "chi_x_minus_1": "O",
            "chi_x_minus_a": "O",
            "chi_x_minus_b": "O",
            "x_mod_3": "O",
            "x_mod_5": "O",
            "x_mod_7": "O",
            "in_factor_x": "0",
            "anchor_denominator_pattern": "OOO",
            "family_target_stratum": "O",
        }
    x_coord, y_coord = point

    def chi_text(value: int) -> str:
        return {1: "+", 0: "0", -1: "-"}[legendre(value, p)]

    anchors = [
        value[0] for value in points[:3] if value is not None
    ]
    anchor_pattern = "".join(
        chi_text(x_coord - anchor) for anchor in anchors
    ).ljust(3, "O")
    family = factor_base["family"]
    parameters = factor_base["public_parameters"]
    if family == "coset_prefix_chain":
        order = parameters["subgroup_order"]
        tags = {
            record["tag"] for record in parameters["visited_cosets"]
        }
        family_stratum = (
            "zero"
            if x_coord == 0
            else ("member" if pow(x_coord, order, p) in tags else "other")
        )
    elif family == "quartic_composition_chain":
        family_stratum = (
            chi_text(x_coord - parameters["e"])
            + chi_text(x_coord - parameters["d"])
        )
    else:
        family_stratum = (
            chi_text(x_coord - parameters["e"])
            + ":"
            + str(parameters["denominator_character_stratum"])
        )
    return {
        "infinity": "0",
        "x_bin_8": str(min(7, 8 * x_coord // p)),
        "y_bin_8": str(min(7, 8 * y_coord // p)),
        "chi_x": chi_text(x_coord),
        "chi_x_minus_1": chi_text(x_coord - 1),
        "chi_x_minus_a": chi_text(x_coord - a),
        "chi_x_minus_b": chi_text(x_coord - b),
        "x_mod_3": str(x_coord % 3),
        "x_mod_5": str(x_coord % 5),
        "x_mod_7": str(x_coord % 7),
        "in_factor_x": "1" if x_coord in factor_x else "0",
        "anchor_denominator_pattern": anchor_pattern,
        "family_target_stratum": family_stratum,
    }


def target_rows(
    curve_index: int,
    curve: dict[str, Any],
    census: list[Point],
    d4: Counter[int],
    factor_base: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    multiplicities = [d4.get(scalar, 0) for scalar in range(curve["q"])]
    ordered = sorted(multiplicities)
    threshold = max(
        1, ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]
    )
    rows = []
    digest_rows = []
    for scalar, point in enumerate(census):
        features = feature_map(point, curve, factor_base)
        multiplicity = multiplicities[scalar]
        row = {
            "curve_index": curve_index,
            "features": features,
            "multiplicity": multiplicity,
            "positive": multiplicity >= threshold,
        }
        rows.append(row)
        digest_rows.append(
            [features, multiplicity, row["positive"]]
        )
    return rows, {
        "curve_index": curve_index,
        "rows": len(rows),
        "threshold": threshold,
        "positive_rows": sum(row["positive"] for row in rows),
        "zero_support_rows": sum(row["multiplicity"] == 0 for row in rows),
        "row_digest": digest(digest_rows),
    }


def model_metrics(
    rows: list[dict[str, Any]], feature: str, buckets: set[str]
) -> dict[str, Any]:
    predicted = [
        row for row in rows if row["features"][feature] in buckets
    ]
    positives = [row for row in rows if row["positive"]]
    true_positive = sum(row["positive"] for row in predicted)
    base_mean = sum(row["multiplicity"] for row in rows) / len(rows)
    predicted_mean = (
        sum(row["multiplicity"] for row in predicted) / len(predicted)
        if predicted
        else base_mean
    )
    oracle_mean = (
        sum(row["multiplicity"] for row in positives) / len(positives)
        if positives
        else base_mean
    )
    denominator = oracle_mean - base_mean
    retained = (
        (predicted_mean - base_mean) / denominator
        if denominator > 0
        else 0.0
    )
    precision = true_positive / len(predicted) if predicted else 0.0
    recall = true_positive / len(positives) if positives else 0.0
    zero_rows = [row for row in rows if row["multiplicity"] == 0]
    zero_predicted = sum(
        row["features"][feature] in buckets for row in zero_rows
    )
    return {
        "rows": len(rows),
        "predicted": len(predicted),
        "positives": len(positives),
        "true_positive": true_positive,
        "precision": round(precision, 12),
        "recall": round(recall, 12),
        "f1": round(
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0,
            12,
        ),
        "base_mean_multiplicity": round(base_mean, 12),
        "predicted_mean_multiplicity": round(predicted_mean, 12),
        "oracle_mean_multiplicity": round(oracle_mean, 12),
        "retained_oracle_enrichment": round(retained, 12),
        "zero_support_rows": len(zero_rows),
        "zero_support_false_positive_rate": round(
            zero_predicted / len(zero_rows) if zero_rows else 0.0, 12
        ),
    }


def bucket_eligibility(
    training: list[dict[str, Any]], feature: str, bucket: str
) -> dict[str, Any]:
    by_curve: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in training:
        by_curve[row["curve_index"]].append(row)
    pooled_count = sum(
        row["features"][feature] == bucket for row in training
    )
    per_curve = []
    for curve_index in sorted(by_curve):
        rows = by_curve[curve_index]
        count = sum(row["features"][feature] == bucket for row in rows)
        per_curve.append(
            {
                "curve_index": curve_index,
                "rows": len(rows),
                "bucket_rows": count,
                "coverage": round(count / len(rows), 12),
                "passes": (
                    count > 0
                    and MIN_BUCKET_COVERAGE_DENOMINATOR * count
                    >= MIN_BUCKET_COVERAGE_NUMERATOR * len(rows)
                ),
            }
        )
    pooled_pass = (
        MIN_BUCKET_COVERAGE_DENOMINATOR * pooled_count
        >= MIN_BUCKET_COVERAGE_NUMERATOR * len(training)
    )
    return {
        "bucket": bucket,
        "pooled_rows": len(training),
        "pooled_bucket_rows": pooled_count,
        "pooled_coverage": round(pooled_count / len(training), 12),
        "pooled_pass": pooled_pass,
        "per_curve": per_curve,
        "eligible": pooled_pass and all(row["passes"] for row in per_curve),
    }


def fit_predictor(
    training: list[dict[str, Any]], heldout: list[dict[str, Any]]
) -> dict[str, Any]:
    feature_names = sorted(training[0]["features"])
    candidates = []
    feature_eligibility = {}
    for feature in feature_names:
        buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in training:
            buckets[row["features"][feature]].append(row)
        eligibility_rows = [
            bucket_eligibility(training, feature, bucket)
            for bucket in sorted(buckets)
        ]
        eligible = {
            row["bucket"] for row in eligibility_rows if row["eligible"]
        }
        feature_eligibility[feature] = {
            "bucket_count": len(eligibility_rows),
            "eligible_bucket_count": len(eligible),
            "eligible_buckets": sorted(eligible),
            "bucket_receipts_digest": digest(eligibility_rows),
        }
        if not eligible:
            continue
        ranked = sorted(
            eligible,
            key=lambda bucket: (
                -sum(row["multiplicity"] for row in buckets[bucket])
                / len(buckets[bucket]),
                bucket,
            ),
        )
        selected = {ranked[0]}
        training_metrics = model_metrics(training, feature, selected)
        candidates.append(
            (
                training_metrics["retained_oracle_enrichment"],
                training_metrics["f1"],
                feature,
                sorted(selected),
                training_metrics,
            )
        )
    if not candidates:
        raise ValueError("no predictor bucket satisfies training coverage")
    _, _, feature, selected, training_metrics = max(
        candidates, key=lambda item: (item[0], item[1], item[2], item[3])
    )
    heldout_metrics = model_metrics(heldout, feature, set(selected))
    selected_eligibility = bucket_eligibility(
        training, feature, selected[0]
    )
    eligibility = {
        "minimum_pooled_coverage": "1/100",
        "minimum_per_training_curve_coverage": "1/100",
        "comparison": "100*bucket_rows>=rows",
        "features": feature_eligibility,
        "selected": selected_eligibility,
    }
    eligibility["eligibility_digest"] = digest(eligibility)
    return {
        "feature": feature,
        "selected_buckets": selected,
        "training": training_metrics,
        "heldout": heldout_metrics,
        "eligibility": eligibility,
        "feature_values_depend_only_on_target_coordinates": True,
    }


def eligibility_boundary_controls() -> dict[str, Any]:
    def coverage_rows(counts: tuple[int, int]) -> list[dict[str, Any]]:
        rows = []
        for curve_index, count in enumerate(counts):
            for index in range(1000):
                rows.append(
                    {
                        "curve_index": curve_index,
                        "features": {
                            "boundary": (
                                "selected" if index < count else "other"
                            )
                        },
                        "multiplicity": 0,
                        "positive": False,
                    }
                )
        return rows

    boundary = {}
    for name, counts, expected in (
        ("below_one_percent", (9, 9), False),
        ("exactly_one_percent", (10, 10), True),
        ("two_percent", (20, 20), True),
        ("five_percent", (50, 50), True),
        ("pooled_one_percent_missing_curve", (20, 0), False),
    ):
        receipt = bucket_eligibility(
            coverage_rows(counts), "boundary", "selected"
        )
        boundary[name] = {
            "counts": list(counts),
            "expected_eligible": expected,
            "receipt": receipt,
            "passes": receipt["eligible"] == expected,
        }

    def balanced_rows(curve_offset: int) -> list[dict[str, Any]]:
        rows = []
        for local_curve in range(2):
            curve_index = curve_offset + local_curve
            for index in range(1000):
                bucket = "A" if index < 500 else "B"
                positive = index % 2 == 0
                rows.append(
                    {
                        "curve_index": curve_index,
                        "features": {"balanced": bucket},
                        "multiplicity": int(positive),
                        "positive": positive,
                    }
                )
        return rows

    balanced = fit_predictor(balanced_rows(0), balanced_rows(2))
    balanced_pass = (
        balanced["eligibility"]["selected"]["eligible"]
        and balanced["heldout"]["retained_oracle_enrichment"] == 0.0
        and balanced["heldout"]["recall"] == 0.5
    )

    def planted_rows(curve_offset: int) -> list[dict[str, Any]]:
        rows = []
        for local_curve in range(2):
            curve_index = curve_offset + local_curve
            for index in range(1000):
                signal = index < 11
                rows.append(
                    {
                        "curve_index": curve_index,
                        "features": {
                            "planted": "signal" if signal else "other"
                        },
                        "multiplicity": int(signal),
                        "positive": signal,
                    }
                )
        return rows

    planted = fit_predictor(planted_rows(0), planted_rows(2))
    planted_pass = (
        planted["selected_buckets"] == ["signal"]
        and planted["eligibility"]["selected"]["eligible"]
        and planted["heldout"]["retained_oracle_enrichment"] == 1.0
        and planted["heldout"]["recall"] == 1.0
    )
    return {
        "boundary": boundary,
        "balanced_null": {
            "model": balanced,
            "passes": balanced_pass,
        },
        "just_above_one_percent_positive": {
            "model": planted,
            "passes": planted_pass,
        },
        "all_pass": (
            all(row["passes"] for row in boundary.values())
            and balanced_pass
            and planted_pass
        ),
    }


def permute_rows(
    rows: list[dict[str, Any]], seed: int
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    by_curve: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_curve[row["curve_index"]].append(row)
    result = []
    for curve_index in sorted(by_curve):
        group = by_curve[curve_index]
        labels = [
            (row["multiplicity"], row["positive"]) for row in group
        ]
        rng.shuffle(labels)
        for row, (multiplicity, positive) in zip(group, labels):
            result.append(
                {
                    **row,
                    "multiplicity": multiplicity,
                    "positive": positive,
                }
            )
    return result


def predictor_with_permutations(
    family: str,
    training: list[dict[str, Any]],
    heldout: list[dict[str, Any]],
    permutations: int,
) -> dict[str, Any]:
    observed = fit_predictor(training, heldout)
    heldout_by_curve: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in heldout:
        heldout_by_curve[row["curve_index"]].append(row)
    per_curve = []
    for curve_index in sorted(heldout_by_curve):
        metrics = model_metrics(
            heldout_by_curve[curve_index],
            observed["feature"],
            set(observed["selected_buckets"]),
        )
        coverage = metrics["predicted"] / metrics["rows"]
        per_curve.append(
            {
                "curve_index": curve_index,
                "predicted_coverage": round(coverage, 12),
                "metrics": metrics,
                "passes": (
                    coverage >= 0.01
                    and metrics["recall"] >= 0.1
                    and metrics["precision"] > 0
                    and metrics["retained_oracle_enrichment"] >= 0.8
                ),
            }
        )
    observed_retained = observed["heldout"][
        "retained_oracle_enrichment"
    ]
    observed_score = max(0.0, observed_retained) * observed[
        "heldout"
    ]["recall"]
    null_values = []
    for permutation in range(permutations):
        seed = stable_seed(
            "coord-energy-cert-v21-predictor", family, permutation
        )
        null_model = fit_predictor(
            permute_rows(training, seed),
            permute_rows(heldout, seed ^ 0x9E3779B97F4A7C15),
        )
        null_values.append(
            max(
                0.0,
                null_model["heldout"][
                    "retained_oracle_enrichment"
                ],
            )
            * null_model["heldout"]["recall"]
        )
    p_value = (1 + sum(value >= observed_score for value in null_values)) / (
        1 + permutations
    )
    return {
        **observed,
        "permutation_test": {
            "draws": permutations,
            "statistic": "max(0,retained_oracle_enrichment)*recall",
            "observed_score": round(observed_score, 12),
            "extreme_or_tied": sum(
                value >= observed_score for value in null_values
            ),
            "rank_p": round(p_value, 12),
            "null_min": min(null_values),
            "null_median": sorted(null_values)[permutations // 2],
            "null_max": max(null_values),
            "null_digest": digest(null_values),
        },
        "bonferroni_critical_value": round(0.05 / len(CANDIDATES), 12),
        "heldout_per_curve": per_curve,
        "passes": (
            observed_retained >= 0.8
            and observed["heldout"]["precision"] > 0
            and observed["heldout"]["recall"] >= 0.1
            and all(row["passes"] for row in per_curve)
            and p_value <= 0.05 / len(CANDIDATES)
        ),
    }


def predictor_controls(
    all_curve_rows: list[
        tuple[int, int, list[Point], dict[str, Any]]
    ],
    candidate_rows: dict[str, dict[str, list[dict[str, Any]]]],
    heldout_bits: int,
    permutations: int,
    negative_control_replicates: int,
) -> dict[str, Any]:
    rows = []
    for curve_index, bits, census, curve in all_curve_rows:
        dummy_factor = {
            "family": "quartic_composition_chain",
            "points": [],
            "public_parameters": {"d": 0, "e": 0},
        }
        for point in census:
            features = feature_map(point, curve, dummy_factor)
            positive = features["chi_x_minus_1"] == "+"
            rows.append(
                {
                    "curve_index": curve_index,
                    "bits": bits,
                    "features": features,
                    "multiplicity": int(positive),
                    "positive": positive,
                }
            )
    training = [row for row in rows if row["bits"] < heldout_bits]
    heldout = [row for row in rows if row["bits"] == heldout_bits]
    positive_model = predictor_with_permutations(
        "public-coordinate-positive-control",
        training,
        heldout,
        permutations,
    )
    negative_families = {}
    all_negative_rows = []
    for family in CANDIDATES:
        family_replicates = []
        for replicate in range(negative_control_replicates):
            training_seed = stable_seed(
                "coord-energy-cert-v21-control",
                "candidate-matched-negative",
                family,
                replicate,
                "training",
            )
            heldout_seed = stable_seed(
                "coord-energy-cert-v21-control",
                "candidate-matched-negative",
                family,
                replicate,
                "heldout",
            )
            model = predictor_with_permutations(
                f"candidate-matched-negative-{family}-{replicate}",
                permute_rows(
                    candidate_rows[family]["training"], training_seed
                ),
                permute_rows(
                    candidate_rows[family]["heldout"], heldout_seed
                ),
                permutations,
            )
            replicate_pass = (
                model["eligibility"]["selected"]["eligible"]
                and not model["passes"]
                and model["heldout"][
                    "retained_oracle_enrichment"
                ]
                <= 0.2
                and not any(
                    row["passes"] for row in model["heldout_per_curve"]
                )
            )
            receipt = {
                "replicate": replicate,
                "training_label_seed": training_seed,
                "heldout_label_seed": heldout_seed,
                "model": model,
                "passes": replicate_pass,
            }
            family_replicates.append(receipt)
            all_negative_rows.append(receipt)
        negative_families[family] = {
            "replicates": family_replicates,
            "maximum_retained_oracle_enrichment": max(
                row["model"]["heldout"][
                    "retained_oracle_enrichment"
                ]
                for row in family_replicates
            ),
            "maximum_recall": max(
                row["model"]["heldout"]["recall"]
                for row in family_replicates
            ),
            "minimum_reference_tail_rank": min(
                row["model"]["permutation_test"]["rank_p"]
                for row in family_replicates
            ),
            "all_pass": all(row["passes"] for row in family_replicates),
        }
    negative_summary = {
        "replicates_per_family": negative_control_replicates,
        "total_replicates": len(all_negative_rows),
        "maximum_retained_oracle_enrichment": max(
            row["model"]["heldout"]["retained_oracle_enrichment"]
            for row in all_negative_rows
        ),
        "maximum_recall": max(
            row["model"]["heldout"]["recall"]
            for row in all_negative_rows
        ),
        "minimum_reference_tail_rank": min(
            row["model"]["permutation_test"]["rank_p"]
            for row in all_negative_rows
        ),
        "all_pass": all(row["passes"] for row in all_negative_rows),
    }
    return {
        "positive": positive_model,
        "negative_families": negative_families,
        "negative_summary": negative_summary,
        "positive_pass": (
            positive_model["feature"] == "chi_x_minus_1"
            and positive_model["selected_buckets"] == ["+"]
            and positive_model["eligibility"]["selected"]["eligible"]
            and positive_model["heldout"][
                "retained_oracle_enrichment"
            ]
            >= 0.95
            and positive_model["passes"]
        ),
        "negative_pass": negative_summary["all_pass"],
    }


def ap_scalars(
    q: int, b_size: int, seed: int
) -> tuple[int, int, tuple[int, ...]]:
    rng = random.Random(seed)
    start = rng.randrange(q)
    step = rng.randrange(1, q)
    scalars = tuple((start + index * step) % q for index in range(b_size))
    if len(set(scalars)) != b_size:
        raise AssertionError("AP control is not distinct")
    return start, step, scalars


def signed_ap_scalars(
    q: int,
    b_size: int,
    p: int,
    census: list[Point],
    by_point: dict[Point, int],
) -> tuple[int, ...]:
    scalars = []
    sampled = 1
    while len(scalars) < b_size:
        point = canonical_point(census[sampled], p)
        if point is not None:
            scalar = by_point[point]
            if scalar not in scalars:
                scalars.append(scalar)
        sampled += 1
    return tuple(sorted(scalars))


def negate(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def public_certificate_replay(
    points: list[Point],
    metrics: dict[str, Any],
    curve: dict[str, Any],
) -> dict[str, Any]:
    p, a = curve["p"], curve["a"]
    certificates = metrics["certificates"]
    freiman_valid = True
    for relation in certificates["freiman"]["basis"]:
        total: Point = None
        for point, coefficient in zip(points, relation):
            signed = point if coefficient >= 0 else negate(point, p)
            for _ in range(abs(coefficient)):
                total = ec_add(total, signed, p, a)
        if total is not None:
            freiman_valid = False
            break
    difference_counts: Counter[Point] = Counter()
    for left_index, left in enumerate(points):
        for right_index, right in enumerate(points):
            if left_index != right_index:
                difference_counts[
                    ec_add(left, negate(right, p), p, a)
                ] += 1
    top_public = sorted(
        difference_counts.items(),
        key=lambda item: (
            -item[1],
            -1 if item[0] is None else 0,
            0 if item[0] is None else item[0][0],
            0 if item[0] is None else item[0][1],
        ),
    )[: len(points)]
    recorded_top = certificates["popular_difference"][
        "top_differences"
    ]
    top_valid = [
        {
            "difference_point": encode_point(point),
            "count": count,
        }
        for point, count in top_public
    ] == [
        {
            "difference_point": row["difference_point"],
            "count": row["count"],
        }
        for row in recorded_top
    ]
    edge_valid = True
    for left_index, right_index, difference_rank in certificates[
        "popular_difference"
    ]["edges"]:
        actual = ec_add(
            points[left_index],
            negate(points[right_index], p),
            p,
            a,
        )
        expected = decode_point(
            recorded_top[difference_rank]["difference_point"]
        )
        if actual != expected:
            edge_valid = False
            break
    public_digest = digest(
        {
            "top": [
                {
                    "difference_point": row["difference_point"],
                    "count": row["count"],
                }
                for row in recorded_top
            ],
            "edges": certificates["popular_difference"]["edges"],
            "component_sizes": certificates["popular_difference"][
                "component_sizes"
            ],
        }
    )
    digest_valid = (
        public_digest
        == certificates["popular_difference"]["public_witness_digest"]
    )
    return {
        "freiman_ec_relations_valid": freiman_valid,
        "difference_top_valid": top_valid,
        "difference_edges_valid": edge_valid,
        "public_witness_digest": public_digest,
        "public_digest_valid": digest_valid,
        "valid": (
            freiman_valid and top_valid and edge_valid and digest_valid
        ),
    }


def git_provenance() -> dict[str, Any]:
    root = SCRIPT_PATH.parents[3]

    def run_git(*args: str) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    status = run_git("status", "--porcelain")
    return {
        "commit": run_git("rev-parse", "HEAD"),
        "tree": run_git("rev-parse", "HEAD^{tree}"),
        "dirty": bool(status),
        "status_digest": digest(status.splitlines()),
    }


def run(
    bits_values: list[int],
    curve_seeds: list[int],
    null_draws: int,
    predictor_permutations: int,
    negative_control_replicates: int,
    development_mode: bool,
) -> dict[str, Any]:
    started = time.perf_counter()
    started_unix = time.time()
    seed_lock = load_seed_lock()
    strict_confirmatory_configuration = (
        seed_lock is not None
        and bits_values == CONFIRMATORY_BITS
        and curve_seeds == seed_lock["curve_seeds"]
        and null_draws == CONFIRMATORY_NULL_DRAWS
        and predictor_permutations
        == CONFIRMATORY_PREDICTOR_PERMUTATIONS
        and negative_control_replicates
        == CONFIRMATORY_NEGATIVE_CONTROL_REPLICATES
        and not development_mode
    )
    registered_development_configuration = (
        bits_values == REGISTERED_DEVELOPMENT_BITS
        and curve_seeds == REGISTERED_DEVELOPMENT_CURVE_SEEDS
        and null_draws == REGISTERED_DEVELOPMENT_NULL_DRAWS
        and predictor_permutations
        == REGISTERED_DEVELOPMENT_PREDICTOR_PERMUTATIONS
        and negative_control_replicates
        == REGISTERED_DEVELOPMENT_NEGATIVE_CONTROL_REPLICATES
        and development_mode
    )
    execution_profile = (
        "confirmatory"
        if strict_confirmatory_configuration
        else (
            "registered_development"
            if registered_development_configuration
            else "exploratory_development"
        )
    )
    curve_records = []
    candidate_rows = []
    null_records = []
    control_rows = []
    predictor_rows: dict[str, dict[str, list[dict[str, Any]]]] = {
        family: {"training": [], "heldout": []} for family in CANDIDATES
    }
    predictor_row_receipts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    predictor_control_inputs = []
    seen_curve_ids: set[str] = set()
    for bits in bits_values:
        for curve_seed in curve_seeds:
            curve = RECURSIVE.generate_prime_order_curve(bits, curve_seed)
            if curve["id"] in seen_curve_ids:
                raise ValueError(f"duplicate generated curve: {curve['id']}")
            seen_curve_ids.add(curve["id"])
            curve_index = len(curve_records)
            p, q, a = curve["p"], curve["q"], curve["a"]
            generator = decode_point(curve["generator"])
            census, by_point = subgroup_census(generator, q, p, a)
            b_size = max(5, round(q ** (1 / 5)))
            curve_receipt = {
                "curve_index": curve_index,
                "bits": bits,
                "curve_seed": curve_seed,
                "curve": curve,
                "b_size": b_size,
                "census_digest": digest(
                    [encode_point(point) for point in census]
                ),
                "census_entries": len(census),
            }
            curve_records.append(curve_receipt)
            predictor_control_inputs.append(
                (curve_index, bits, census, curve)
            )
            null_metrics = []
            for draw in range(null_draws):
                seed = stable_seed(
                    "coord-energy-cert-v21-null",
                    curve["id"],
                    b_size,
                    draw,
                )
                scalars, sampling_attempts = random_canonical_scalar_set(
                    q, b_size, p, census, by_point, seed
                )
                metrics, _ = set_metrics(
                    scalars, q, retain_witnesses=False
                )
                compact = {
                    "draw": draw,
                    "seed": seed,
                    "sampling_attempts": sampling_attempts,
                    "canonicalizations": sampling_attempts,
                    "d2_support": metrics["d2"]["support"],
                    "d4_support": metrics["d4"]["support"],
                    "d4_energy_ordered": metrics["d4"]["energy"],
                    "d4_normalized_energy": metrics["d4"][
                        "normalized_energy_e4_over_b7"
                    ],
                    "fourier_magnitude": metrics[
                        "fourier_magnitude_normalized"
                    ],
                    "popular_difference_density": metrics[
                        "popular_difference_density"
                    ],
                    "popular_difference_top_b_count_sum": metrics[
                        "popular_difference_top_b_count_sum"
                    ],
                    "freiman_dimension": metrics["freiman_dimension"],
                    "freiman_relation_rank": metrics[
                        "freiman_relation_rank"
                    ],
                    "freiman_relation_count": metrics[
                        "freiman_relation_count"
                    ],
                    "scalar_set_digest": metrics["scalar_set_digest"],
                }
                null_metrics.append(compact)
            null_records.append(
                {
                    "curve_index": curve_index,
                    "curve_id": curve["id"],
                    "b_size": b_size,
                    "draws": null_metrics,
                    "draws_digest": digest(null_metrics),
                }
            )
            null_fields = {
                field: [row[field] for row in null_metrics]
                for field in (
                    "d4_energy_ordered",
                    "fourier_magnitude",
                    "popular_difference_top_b_count_sum",
                    "freiman_dimension",
                )
            }
            for family in CANDIDATES:
                family_seed = stable_seed(
                    "coord-energy-cert-v21-factor-base",
                    curve["id"],
                    family,
                )
                factor_base = make_factor_base(
                    family, curve, b_size, family_seed
                )
                points = [
                    decode_point(value) for value in factor_base["points"]
                ]
                scalars = tuple(by_point[point] for point in points)
                metrics, d4 = set_metrics(
                    scalars, q, retain_witnesses=True, census=census
                )
                public_replay = public_certificate_replay(
                    points, metrics, curve
                )
                tests = {
                    "d4_energy_ordered": empirical_rank(
                        metrics["d4"]["energy"],
                        null_fields["d4_energy_ordered"],
                        "high",
                    ),
                    "fourier_magnitude": empirical_rank(
                        metrics["fourier_magnitude_normalized"],
                        null_fields["fourier_magnitude"],
                        "high",
                    ),
                    "popular_difference_top_b_count_sum": empirical_rank(
                        metrics["popular_difference_top_b_count_sum"],
                        null_fields[
                            "popular_difference_top_b_count_sum"
                        ],
                        "high",
                    ),
                    "freiman_dimension": empirical_rank(
                        metrics["freiman_dimension"],
                        null_fields["freiman_dimension"],
                        "low",
                    ),
                }
                rows, row_receipt = target_rows(
                    curve_index, curve, census, d4, factor_base
                )
                split = "heldout" if bits == max(bits_values) else "training"
                predictor_rows[family][split].extend(rows)
                predictor_row_receipts[family].append(row_receipt)
                candidate_rows.append(
                    {
                        "curve_index": curve_index,
                        "curve_id": curve["id"],
                        "bits": bits,
                        "family": family,
                        "factor_base": factor_base,
                        "metrics": metrics,
                        "public_certificate_replay": public_replay,
                        "rank_tests": tests,
                    }
                )
            ap_start, ap_step, true_ap = ap_scalars(
                q,
                b_size,
                stable_seed("coord-energy-cert-v21-true-ap", curve["id"]),
            )
            true_metrics, _ = set_metrics(
                true_ap, q, retain_witnesses=True, census=census
            )
            true_public_replay = public_certificate_replay(
                [census[scalar] for scalar in true_ap],
                true_metrics,
                curve,
            )
            signed_ap = signed_ap_scalars(
                q, b_size, p, census, by_point
            )
            signed_metrics, _ = set_metrics(
                signed_ap, q, retain_witnesses=True, census=census
            )
            signed_public_replay = public_certificate_replay(
                [census[scalar] for scalar in signed_ap],
                signed_metrics,
                curve,
            )
            control_rows.append(
                {
                    "curve_index": curve_index,
                    "curve_id": curve["id"],
                    "b_size": b_size,
                    "true_ap": {
                        "start": ap_start,
                        "step": ap_step,
                        "scalars": list(true_ap),
                        "exact_progression_verified": all(
                            true_ap[index]
                            == (ap_start + index * ap_step) % q
                            for index in range(b_size)
                        ),
                        "metrics": true_metrics,
                        "public_certificate_replay": true_public_replay,
                        "d4_rank": empirical_rank(
                            true_metrics["d4"]["energy"],
                            null_fields["d4_energy_ordered"],
                            "high",
                        ),
                        "fourier_rank": empirical_rank(
                            true_metrics[
                                "fourier_magnitude_normalized"
                            ],
                            null_fields["fourier_magnitude"],
                            "high",
                        ),
                    },
                    "signed_ap": {
                        "scalars": list(signed_ap),
                        "metrics": signed_metrics,
                        "public_certificate_replay": signed_public_replay,
                        "d4_rank": empirical_rank(
                            signed_metrics["d4"]["energy"],
                            null_fields["d4_energy_ordered"],
                            "high",
                        ),
                    },
                }
            )
            print(
                f"measured {curve['id']} B={b_size} nulls={null_draws}",
                file=sys.stderr,
                flush=True,
            )
    energy_inputs = []
    certificate_inputs = []
    for row in candidate_rows:
        cell = f"{row['curve_index']}:{row['family']}"
        energy_inputs.append(
            {
                "id": f"{cell}:d4",
                "curve_index": row["curve_index"],
                "family": row["family"],
                "metric": "d4_energy_ordered",
                "p": row["rank_tests"]["d4_energy_ordered"]["rank_p"],
            }
        )
        for metric in (
            "fourier_magnitude",
            "popular_difference_top_b_count_sum",
            "freiman_dimension",
        ):
            certificate_inputs.append(
                {
                    "id": f"{cell}:{metric}",
                    "curve_index": row["curve_index"],
                    "family": row["family"],
                    "metric": metric,
                    "p": row["rank_tests"][metric]["rank_p"],
                }
            )
    energy_holm = holm(energy_inputs, 0.05)
    certificate_holm = holm(certificate_inputs, 0.05)
    energy_lookup = {row["id"]: row for row in energy_holm}
    certificate_lookup = {row["id"]: row for row in certificate_holm}
    predictors = {
        family: predictor_with_permutations(
            family,
            predictor_rows[family]["training"],
            predictor_rows[family]["heldout"],
            predictor_permutations,
        )
        for family in CANDIDATES
    }
    predictor_control = predictor_controls(
        predictor_control_inputs,
        predictor_rows,
        max(bits_values),
        predictor_permutations,
        negative_control_replicates,
    )
    boundary_control = eligibility_boundary_controls()
    family_gates = {}
    for family in CANDIDATES:
        family_cells = [
            row for row in candidate_rows if row["family"] == family
        ]
        energy_pass = all(
            energy_lookup[
                f"{row['curve_index']}:{family}:d4"
            ]["reject"]
            and row["rank_tests"]["d4_energy_ordered"][
                "tie_aware_auc"
            ]
            >= 0.65
            for row in family_cells
        )
        certificate_pass = all(
            any(
                certificate_lookup[
                    f"{row['curve_index']}:{family}:{metric}"
                ]["reject"]
                and row["rank_tests"][metric]["tie_aware_auc"] >= 0.65
                for metric in (
                    "popular_difference_top_b_count_sum",
                    "freiman_dimension",
                )
            )
            for row in family_cells
        )
        family_gates[family] = {
            "energy_all_nine": energy_pass,
            "certificate_each_curve": certificate_pass,
            "predictor_pass": predictors[family]["passes"],
            "public_producer_replay_all_cells": all(
                row["public_certificate_replay"]["valid"]
                for row in family_cells
            ),
            "screening_signal_before_controls_and_verification": (
                energy_pass
                and certificate_pass
                and predictors[family]["passes"]
                and all(
                    row["public_certificate_replay"]["valid"]
                    for row in family_cells
                )
            ),
            "positive_signal": False,
        }
    true_ap_pass = all(
        row["true_ap"]["exact_progression_verified"]
        and row["true_ap"]["metrics"]["freiman_dimension"] == 1
        and row["true_ap"]["d4_rank"]["rank_p"] <= 0.01
        and row["true_ap"]["fourier_rank"]["rank_p"] <= 0.01
        and row["true_ap"]["public_certificate_replay"]["valid"]
        for row in control_rows
    )
    signed_ap_pass = all(
        row["signed_ap"]["d4_rank"]["rank_p"] <= 0.01
        and row["signed_ap"]["public_certificate_replay"]["valid"]
        for row in control_rows
    )
    controls_pass = (
        true_ap_pass
        and signed_ap_pass
        and boundary_control["all_pass"]
        and predictor_control["positive_pass"]
        and predictor_control["negative_pass"]
    )
    predictor_calibration_pass = (
        registered_development_configuration
        and boundary_control["all_pass"]
        and predictor_control["positive_pass"]
        and predictor_control["negative_pass"]
    )
    construction_scalar_free = all(
        not row["factor_base"]["construction_used_scalar_census"]
        for row in candidate_rows
    )
    for gate in family_gates.values():
        gate["controls_pass"] = controls_pass
        gate["strict_confirmatory_configuration"] = (
            strict_confirmatory_configuration
        )
        gate["construction_scalar_free"] = construction_scalar_free
        gate["producer_screening_signal"] = (
            gate["screening_signal_before_controls_and_verification"]
            and controls_pass
            and strict_confirmatory_configuration
            and construction_scalar_free
        )
        gate["awaiting_independent_verification"] = True
    elapsed = time.perf_counter() - started
    finished_unix = time.time()
    peak_rss = rss_bytes()
    result = {
        "protocol": (
            "EXP-ECDLP-COORD-EXPANSION-001-"
            "coord-energy-cert-v2.1"
        ),
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
        ],
        "source": {
            "producer_sha256": file_hash(SCRIPT_PATH),
            "recursive_source_sha256": file_hash(RECURSIVE_SOURCE),
            "coordinate_energy_source_sha256": file_hash(
                Path(RECURSIVE.ENERGY_SOURCE_PATH)
            ),
            "contract_sha256": file_hash(
                SCRIPT_PATH.parents[1]
                / "development"
                / "COORD-ENERGY-CERT-V2.1"
                / "contract.md"
            ),
            "confirmatory_seed_lock_sha256": (
                file_hash(SEED_LOCK_PATH) if seed_lock is not None else None
            ),
            "numpy_version": np.__version__,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "git": git_provenance(),
            "command": [sys.executable, *sys.argv],
        },
        "config": {
            "bits": bits_values,
            "curve_seeds": curve_seeds,
            "null_draws": null_draws,
            "predictor_permutations": predictor_permutations,
            "negative_control_replicates": (
                negative_control_replicates
            ),
            "minimum_training_bucket_coverage": "1/100",
            "candidate_families": list(CANDIDATES),
            "target_factor_base_exponent": "1/5",
            "heldout_bits": max(bits_values),
            "development_mode": development_mode,
            "strict_confirmatory_configuration": (
                strict_confirmatory_configuration
            ),
            "registered_development_configuration": (
                registered_development_configuration
            ),
            "execution_profile": execution_profile,
            "primary_holm_tests": len(energy_inputs),
            "certificate_holm_tests": len(certificate_inputs),
        },
        "curves": curve_records,
        "nulls": null_records,
        "candidates": candidate_rows,
        "controls": {
            "curve_rows": control_rows,
            "predictor": predictor_control,
            "eligibility_boundary": boundary_control,
            "true_ap_pass": true_ap_pass,
            "signed_ap_pass": signed_ap_pass,
            "predictor_calibration_pass": predictor_calibration_pass,
            "all_pass": controls_pass,
        },
        "multiple_testing": {
            "primary_energy_holm": energy_holm,
            "certificate_holm": certificate_holm,
        },
        "predictor_row_receipts": predictor_row_receipts,
        "predictors": predictors,
        "family_gates": family_gates,
        "summary": {
            "curves": len(curve_records),
            "candidate_cells": len(candidate_rows),
            "null_sets": len(curve_records) * null_draws,
            "controls_pass": controls_pass,
            "predictor_calibration_pass": predictor_calibration_pass,
            "execution_profile": execution_profile,
            "candidate_positive_signals": sum(
                gate["positive_signal"] for gate in family_gates.values()
            ),
            "producer_screening_signals": sum(
                gate["producer_screening_signal"]
                for gate in family_gates.values()
            ),
            "all_representation_totals_valid": all(
                row["metrics"]["d2"]["representation_total"]
                == row["metrics"]["b_size"] ** 2
                and row["metrics"]["d4"]["representation_total"]
                == row["metrics"]["b_size"] ** 4
                for row in candidate_rows
            ),
            "scalar_labels_attack_advice": False,
            "construction_scalar_free": construction_scalar_free,
            "independent_verification_required": True,
            "algorithm_promotion_gate": False,
            "breakthrough_claim": False,
        },
        "accounting": {
            "boundary": (
                "producer-only toy census, candidate/null diagnostics, "
                "predictor fitting, and self-replay; excludes external "
                "wrapper, serialization, manifest, and verifier"
            ),
            "subgroup_census_additions": sum(
                row["curve"]["q"] for row in curve_records
            ),
            "curve_generation_attempts": sum(
                row["curve"]["curve_attempts"] for row in curve_records
            ),
            "curve_generation_order_count_legendre_tests": sum(
                row["curve"]["order_count_legendre_tests"]
                for row in curve_records
            ),
            "factor_base_build_counters": {
                field: sum(
                    row["factor_base"]["build_counters"][field]
                    for row in candidate_rows
                )
                for field in BuildCounters().__dict__
            },
            "null_sets": len(curve_records) * null_draws,
            "null_sampling_attempts": sum(
                draw["sampling_attempts"]
                for row in null_records
                for draw in row["draws"]
            ),
            "null_canonicalizations": sum(
                draw["canonicalizations"]
                for row in null_records
                for draw in row["draws"]
            ),
            "d2_pair_counter_updates": (
                sum(
                    null["b_size"] ** 2
                    for null in null_records
                    for _ in null["draws"]
                )
                + sum(
                    row["metrics"]["b_size"] ** 2
                    for row in candidate_rows
                )
                + sum(
                    control[name]["metrics"]["b_size"] ** 2
                    for control in control_rows
                    for name in ("true_ap", "signed_ap")
                )
            ),
            "d4_convolution_counter_updates": (
                sum(
                    draw["d2_support"] ** 2
                    for null in null_records
                    for draw in null["draws"]
                )
                + sum(
                    row["metrics"]["d2"]["support"] ** 2
                    for row in candidate_rows
                )
                + sum(
                    control[name]["metrics"]["d2"]["support"] ** 2
                    for control in control_rows
                    for name in ("true_ap", "signed_ap")
                )
            ),
            "freiman_relation_rows_considered": (
                sum(
                    draw["freiman_relation_count"]
                    for null in null_records
                    for draw in null["draws"]
                )
                + sum(
                    row["metrics"]["freiman_relation_count"]
                    for row in candidate_rows
                )
                + sum(
                    control[name]["metrics"]["freiman_relation_count"]
                    for control in control_rows
                    for name in ("true_ap", "signed_ap")
                )
            ),
            "fft_transforms": (
                len(curve_records) * null_draws
                + len(candidate_rows)
                + 2 * len(curve_records)
            ),
            "predictor_target_rows": sum(
                receipt["rows"]
                for receipts in predictor_row_receipts.values()
                for receipt in receipts
            ),
            "predictor_control_target_rows": sum(
                row["curve"]["q"] for row in curve_records
            ),
            "predictor_model_fits": (
                (
                    len(CANDIDATES)
                    + 1
                    + len(CANDIDATES)
                    * negative_control_replicates
                )
                * (predictor_permutations + 1)
                + 2
            ),
            "predictor_feature_candidate_evaluations": (
                (
                    len(CANDIDATES)
                    + 1
                    + len(CANDIDATES)
                    * negative_control_replicates
                )
                * (predictor_permutations + 1)
                * 13
                + 2
            ),
            "artifact_bytes": (
                "external_manifest_required_after_serialization"
            ),
        },
        "peak_rss_bytes": peak_rss,
        "started_unix_seconds": started_unix,
        "finished_unix_seconds": finished_unix,
        "total_wall_seconds": elapsed,
    }
    result["telemetry_digest"] = digest(
        {
            "peak_rss_bytes": peak_rss,
            "started_unix_seconds": started_unix,
            "finished_unix_seconds": finished_unix,
            "total_wall_seconds": elapsed,
        }
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bits", nargs="+", type=int, default=CONFIRMATORY_BITS
    )
    parser.add_argument(
        "--curve-seeds",
        nargs="+",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--null-draws", type=int, default=CONFIRMATORY_NULL_DRAWS
    )
    parser.add_argument(
        "--predictor-permutations",
        type=int,
        default=CONFIRMATORY_PREDICTOR_PERMUTATIONS,
    )
    parser.add_argument(
        "--negative-control-replicates",
        type=int,
        default=CONFIRMATORY_NEGATIVE_CONTROL_REPLICATES,
    )
    parser.add_argument("--development", action="store_true")
    args = parser.parse_args()
    seed_lock = load_seed_lock()
    if args.curve_seeds is None:
        if args.development:
            args.curve_seeds = REGISTERED_DEVELOPMENT_CURVE_SEEDS
        elif seed_lock is not None:
            args.curve_seeds = seed_lock["curve_seeds"]
        else:
            raise ValueError(
                "confirmatory seed lock is not frozen; "
                "non-confirmatory parameters require --development"
            )
    if sorted(set(args.bits)) != args.bits or len(args.bits) < 3:
        raise ValueError("bits must be at least three strictly increasing values")
    if len(set(args.curve_seeds)) != len(args.curve_seeds):
        raise ValueError("curve seeds must be distinct")
    if (
        args.null_draws < 1
        or args.predictor_permutations < 1
        or args.negative_control_replicates < 1
    ):
        raise ValueError("draw counts must be positive")
    exact_configuration = (
        seed_lock is not None
        and args.bits == CONFIRMATORY_BITS
        and args.curve_seeds == seed_lock["curve_seeds"]
        and args.null_draws == CONFIRMATORY_NULL_DRAWS
        and args.predictor_permutations
        == CONFIRMATORY_PREDICTOR_PERMUTATIONS
        and args.negative_control_replicates
        == CONFIRMATORY_NEGATIVE_CONTROL_REPLICATES
    )
    if not args.development and not exact_configuration:
        raise ValueError(
            "non-confirmatory parameters require --development"
        )
    result = run(
        args.bits,
        args.curve_seeds,
        args.null_draws,
        args.predictor_permutations,
        args.negative_control_replicates,
        args.development,
    )
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return (
        0
        if result["summary"]["all_representation_totals_valid"]
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
