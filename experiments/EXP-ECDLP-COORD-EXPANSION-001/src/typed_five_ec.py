#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import platform
import random
import statistics
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


Point = tuple[int, int] | None
SCRIPT_PATH = Path(__file__).resolve()
COORDINATE_SOURCE = SCRIPT_PATH.with_name("coordinate_expansion.py")
TYPED_SOURCE = SCRIPT_PATH.with_name("typed_five_term.py")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load prerequisite: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


COORDINATE = load_module("coordinate_expansion_typed_five_ec", COORDINATE_SOURCE)
TYPED = load_module("typed_five_term_typed_five_ec", TYPED_SOURCE)
Curve = COORDINATE.Curve
Ops = COORDINATE.Ops


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def point_from_json(point: list[int] | None) -> Point:
    return None if point is None else (point[0], point[1])


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be at least {minimum}")
    return value


def add_ops(total: Ops, extra: Ops) -> None:
    total.add(extra)


def make_source_prf_x(
    curve: Any, q: int, size: int, seed: int
) -> dict[str, Any]:
    ops = Ops()
    diagnostics = {
        "x_candidates": 0,
        "square_root_tests": 0,
        "subgroup_tests": 0,
    }
    fibers = []
    seen_x = set()
    for draw_index in range(16 * curve.p):
        digest = hashlib.sha256(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|TYPED-FIVE-EC|R|"
                f"{seed}|{draw_index}"
            ).encode("ascii")
        ).digest()
        x = int.from_bytes(digest, "big") % curve.p
        if x in seen_x:
            continue
        seen_x.add(x)
        point = COORDINATE.ENERGY.point_for_x(
            curve, q, x, ops, diagnostics
        )
        if point is None:
            continue
        pair = COORDINATE.ENERGY.canonical_fiber(curve, point)
        fibers.append(
            {
                "points": [point_json(pair[0]), point_json(pair[1])],
                "source": {
                    "kind": "source_prf_x",
                    "draw_index": draw_index,
                    "x": x,
                },
            }
        )
        if len(fibers) == size:
            break
    if len(fibers) != size:
        raise RuntimeError("source-PRF x generation exhausted")
    return {
        "name": "source_prf_x",
        "symmetry_mode": "sign_canonical",
        "size": size,
        "points": [fiber["points"][0] for fiber in fibers],
        "fibers": fibers,
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
        "raw_sign_complete_size": 2 * size,
        "attack_eligible": True,
    }


def make_streamed_random_x(
    curve: Any, q: int, size: int, seed: int
) -> dict[str, Any]:
    rng = random.Random(seed)
    ops = Ops()
    diagnostics = {
        "x_candidates": 0,
        "square_root_tests": 0,
        "subgroup_tests": 0,
    }
    fibers = []
    seen_x = set()
    for draw_index in range(16 * curve.p):
        x = rng.randrange(curve.p)
        if x in seen_x:
            continue
        seen_x.add(x)
        point = COORDINATE.ENERGY.point_for_x(
            curve, q, x, ops, diagnostics
        )
        if point is None:
            continue
        pair = COORDINATE.ENERGY.canonical_fiber(curve, point)
        fibers.append(
            {
                "points": [point_json(pair[0]), point_json(pair[1])],
                "source": {
                    "kind": "random_x",
                    "draw_index": draw_index,
                    "x": x,
                },
            }
        )
        if len(fibers) == size:
            break
    if len(fibers) != size:
        raise RuntimeError("streamed random-x generation exhausted")
    return {
        "name": "random_x",
        "symmetry_mode": "sign_canonical",
        "size": size,
        "points": [fiber["points"][0] for fiber in fibers],
        "fibers": fibers,
        "build_ops": asdict(ops),
        "build_diagnostics": diagnostics,
        "raw_sign_complete_size": 2 * size,
        "attack_eligible": True,
    }


def make_transverse_factor_base(
    family: str,
    curve: Any,
    q: int,
    generator: Point,
    size: int,
    seed: int,
) -> dict[str, Any]:
    if family == "source_prf_x":
        result = make_source_prf_x(curve, q, size, seed)
    elif family == "random_x":
        result = make_streamed_random_x(curve, q, size, seed)
    else:
        source_family = (
            "scalar_progression_positive_control"
            if family == "scalar_progression_control"
            else family
        )
        result = COORDINATE.make_public_factor_base(
            source_family,
            "sign_canonical",
            curve,
            q,
            generator,
            size,
            seed,
        )
        result["name"] = family
        result["attack_eligible"] = family != "scalar_progression_control"
    points = [point_from_json(point) for point in result["points"]]
    if None in points or len(points) != len(set(points)):
        raise AssertionError("transverse factor base is not distinct/nonidentity")
    result["digest"] = canonical_digest(
        {key: value for key, value in result.items() if key != "digest"}
    )
    return result


def hash_to_curve_point(
    curve: Any,
    q: int,
    seed: int,
    label: str,
    forbidden: set[Point],
) -> tuple[Point, dict[str, Any], Ops]:
    ops = Ops()
    diagnostics = {
        "x_candidates": 0,
        "square_root_tests": 0,
        "subgroup_tests": 0,
    }
    seen_x = set()
    for draw_index in range(16 * curve.p):
        digest = hashlib.sha256(
            (
                "EXP-ECDLP-COORD-EXPANSION-001|TYPED-FIVE-EC|"
                f"{label}|{seed}|{draw_index}"
            ).encode("ascii")
        ).digest()
        x = int.from_bytes(digest, "big") % curve.p
        if x in seen_x:
            continue
        seen_x.add(x)
        point = COORDINATE.ENERGY.point_for_x(
            curve, q, x, ops, diagnostics
        )
        if point is None:
            continue
        point = COORDINATE.ENERGY.canonical_fiber(curve, point)[0]
        if point in forbidden:
            continue
        return point, {
            "label": label,
            "draw_index": draw_index,
            "x": x,
            "diagnostics": diagnostics,
        }, ops
    raise RuntimeError(f"hash-to-curve exhausted for {label}")


def build_public_progression(
    curve: Any,
    q: int,
    size: int,
    seed: int,
    forbidden: set[Point],
) -> dict[str, Any]:
    total_hash_ops = Ops()
    for attempt in range(min(q, 256)):
        p0, p0_source, p0_ops = hash_to_curve_point(
            curve, q, seed, f"P0|{attempt}", forbidden
        )
        add_ops(total_hash_ops, p0_ops)
        d, d_source, d_ops = hash_to_curve_point(
            curve, q, seed, f"D|{attempt}", forbidden | {p0}
        )
        add_ops(total_hash_ops, d_ops)
        progression_ops = Ops()
        points = []
        point = p0
        for _ in range(size):
            points.append(point)
            point = curve.add(point, d, progression_ops)
        if (
            None in points
            or len(points) != len(set(points))
            or set(points) & forbidden
        ):
            continue
        record = {
            "size": size,
            "p0": point_json(p0),
            "d": point_json(d),
            "points": [point_json(item) for item in points],
            "p0_source": p0_source,
            "d_source": d_source,
            "placement_attempt": attempt,
            "hash_to_curve_ops": asdict(total_hash_ops),
            "progression_ops": asdict(progression_ops),
        }
        record["digest"] = canonical_digest(record)
        return record
    raise RuntimeError("public progression construction exhausted")


def serialize_support(
    support: dict[Point, tuple[int, ...]]
) -> list[list[Any]]:
    return [
        [point_json(point), list(witness)]
        for point, witness in sorted(
            support.items(), key=lambda item: COORDINATE.point_sort_key(item[0])
        )
    ]


def compile_r_support(curve: Any, points: list[Point]) -> dict[str, Any]:
    started = time.perf_counter()
    levels = COORDINATE.build_point_levels(curve, points, 4)
    d3 = levels["levels"][3]
    d4 = levels["levels"][4]
    payload = {
        "D3": serialize_support(d3),
        "D4": serialize_support(d4),
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return {
        "levels_internal": levels,
        "d3_internal": d3,
        "d4_internal": d4,
        "summary": {
            "profiles": levels["profiles"],
            "d3_entries": len(d3),
            "d4_entries": len(d4),
            "persistent_json_bytes": len(encoded),
            "builder_deep_bytes": COORDINATE.deep_size(levels),
            "digest": hashlib.sha256(encoded).hexdigest(),
            "wall_seconds": time.perf_counter() - started,
            "advice_contains": [
                "coordinate R points and public source records",
                "point-keyed exact D3 witnesses",
                "point-keyed exact D4 witnesses",
            ],
            "advice_excludes": [
                "subgroup scalar census",
                "factor-base logarithms",
                "target logarithms",
                "D5 target support",
            ],
        },
    }


def verify_typed_witness(
    curve: Any,
    a_points: list[Point],
    r_points: list[Point],
    a_index: int,
    r_witness: tuple[int, ...],
    target: Point,
) -> bool:
    recovered = a_points[a_index]
    for index in r_witness:
        recovered = curve.add(recovered, r_points[index])
    return recovered == target


def query_d4(
    curve: Any,
    a_points: list[Point],
    r_points: list[Point],
    d4: dict[Point, tuple[int, ...]],
    target: Point,
) -> dict[str, Any]:
    ops = Ops()
    for probe, a_point in enumerate(a_points, 1):
        complement = curve.add(target, curve.neg(a_point), ops)
        witness = d4.get(complement)
        if witness is None:
            continue
        if not verify_typed_witness(
            curve, a_points, r_points, probe - 1, witness, target
        ):
            raise AssertionError("materialized D4 witness mismatch")
        return {
            "success": True,
            "a_index": probe - 1,
            "r_witness": witness,
            "a_probes": probe,
            "lookups": probe,
            "ops": asdict(ops),
        }
    return {
        "success": False,
        "a_index": None,
        "r_witness": None,
        "a_probes": len(a_points),
        "lookups": len(a_points),
        "ops": asdict(ops),
    }


def query_d4_all(
    curve: Any,
    a_points: list[Point],
    r_points: list[Point],
    d4: dict[Point, tuple[int, ...]],
    target: Point,
) -> dict[str, Any]:
    ops = Ops()
    hits = []
    for a_index, a_point in enumerate(a_points):
        complement = curve.add(target, curve.neg(a_point), ops)
        witness = d4.get(complement)
        if witness is None:
            continue
        if not verify_typed_witness(
            curve, a_points, r_points, a_index, witness, target
        ):
            raise AssertionError("materialized D4 witness mismatch")
        hits.append(
            {
                "a_index": a_index,
                "r_witness": witness,
            }
        )
    return {
        "success": bool(hits),
        "hits": hits,
        "a_probes": len(a_points),
        "lookups": len(a_points),
        "ops": asdict(ops),
    }


def query_r_plus_d3(
    curve: Any,
    a_points: list[Point],
    r_points: list[Point],
    d3: dict[Point, tuple[int, ...]],
    target: Point,
) -> dict[str, Any]:
    ops = Ops()
    lookups = 0
    for a_index, a_point in enumerate(a_points):
        after_a = curve.add(target, curve.neg(a_point), ops)
        for r_index, r_point in enumerate(r_points):
            complement = curve.add(after_a, curve.neg(r_point), ops)
            lookups += 1
            witness = d3.get(complement)
            if witness is None:
                continue
            four = (r_index,) + witness
            if not verify_typed_witness(
                curve, a_points, r_points, a_index, four, target
            ):
                raise AssertionError("R+D3 witness mismatch")
            return {
                "success": True,
                "a_index": a_index,
                "r_witness": four,
                "lookups": lookups,
                "ops": asdict(ops),
            }
    return {
        "success": False,
        "a_index": None,
        "r_witness": None,
        "lookups": lookups,
        "ops": asdict(ops),
    }


def full_relation_coefficients(
    a_index: int, r_witness: tuple[int, ...], r_size: int
) -> list[int]:
    counts = Counter(r_witness)
    return [1, a_index] + [counts[index] for index in range(r_size)]


def quotient_relation_coefficients(
    a_index: int, r_witness: tuple[int, ...], r_size: int
) -> list[int]:
    full = full_relation_coefficients(a_index, r_witness, r_size)
    if sum(full[2:]) != 4:
        raise AssertionError("typed relation does not contain four R terms")
    return full[:2] + full[3:]


@dataclass
class LinearOps:
    row_additions: int = 0
    field_additions: int = 0
    field_multiplications: int = 0
    field_inversions: int = 0


class IncrementalBasis:
    def __init__(self, width: int, q: int) -> None:
        self.width = width
        self.q = q
        self.rows: dict[int, tuple[list[int], int]] = {}
        self.ops = LinearOps()

    @property
    def rank(self) -> int:
        return len(self.rows)

    def insert(self, coefficients: list[int], rhs: int) -> bool:
        if len(coefficients) != self.width:
            raise ValueError("coefficient width mismatch")
        row = [value % self.q for value in coefficients]
        value = rhs % self.q
        for pivot in sorted(self.rows):
            factor = row[pivot]
            if factor == 0:
                continue
            prior, prior_rhs = self.rows[pivot]
            self.ops.row_additions += 1
            for column in range(pivot, self.width):
                row[column] = (
                    row[column] - factor * prior[column]
                ) % self.q
                self.ops.field_multiplications += 1
                self.ops.field_additions += 1
            value = (value - factor * prior_rhs) % self.q
            self.ops.field_multiplications += 1
            self.ops.field_additions += 1
        pivot = next((i for i, entry in enumerate(row) if entry), None)
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
        self.rows[pivot] = row, value
        return True


def solve_full_rank(
    equations: list[dict[str, Any]], width: int, q: int
) -> tuple[list[int], LinearOps]:
    if len(equations) < width:
        raise ValueError("not enough equations")
    matrix = [
        list(equation["coefficients"]) + [equation["rhs"]]
        for equation in equations
    ]
    ops = LinearOps()
    pivot_row = 0
    for column in range(width):
        selected = next(
            (
                row
                for row in range(pivot_row, len(matrix))
                if matrix[row][column] % q
            ),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = (
            matrix[selected],
            matrix[pivot_row],
        )
        inverse = pow(matrix[pivot_row][column] % q, -1, q)
        ops.field_inversions += 1
        for index in range(column, width + 1):
            matrix[pivot_row][index] = (
                matrix[pivot_row][index] * inverse % q
            )
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
                    matrix[row][index]
                    - factor * matrix[pivot_row][index]
                ) % q
                ops.field_multiplications += 1
                ops.field_additions += 1
        pivot_row += 1
    if pivot_row != width:
        raise ValueError("quotient relation system is rank deficient")
    solution = [0] * width
    for row in matrix:
        pivot = next(
            (index for index in range(width) if row[index] % q), None
        )
        if pivot is not None:
            solution[pivot] = row[-1] % q
    return solution, ops


def dot_mod(left: list[int], right: list[int], q: int) -> int:
    return sum(a * b for a, b in zip(left, right)) % q


def nonzero_scalar_stream(q: int, seed: int):
    rng = random.Random(seed)
    offset = rng.randrange(q - 1)
    step = rng.randrange(1, q - 1)
    while math.gcd(step, q - 1) != 1:
        step = step % (q - 2) + 1
    for index in range(q - 1):
        yield (offset + index * step) % (q - 1) + 1


def collect_relations(
    curve: Any,
    q: int,
    generator: Point,
    a_points: list[Point],
    r_points: list[Point],
    d4: dict[Point, tuple[int, ...]],
    seed: int,
) -> dict[str, Any]:
    width = len(r_points) + 1
    target_budget = min(q - 1, 64 * width)
    basis = IncrementalBasis(width, q)
    independent = []
    successful_targets = 0
    candidate_rows = 0
    dependent_count = 0
    target_ops = Ops()
    query_ops = Ops()
    probes = 0
    lookups = 0
    attempted_scalars = []
    target_transcript = []
    for target_index, scalar in enumerate(nonzero_scalar_stream(q, seed)):
        if target_index == target_budget:
            break
        target = curve.mul(scalar, generator, target_ops)
        query = query_d4_all(curve, a_points, r_points, d4, target)
        attempted_scalars.append(scalar)
        probes += query["a_probes"]
        lookups += query["lookups"]
        for key, value in query["ops"].items():
            setattr(query_ops, key, getattr(query_ops, key) + value)
        target_record = {
            "scalar": scalar,
            "target": point_json(target),
            "hits": [
                {
                    "a_index": hit["a_index"],
                    "r_witness": list(hit["r_witness"]),
                }
                for hit in query["hits"]
            ],
        }
        target_transcript.append(target_record)
        if not query["success"]:
            continue
        successful_targets += 1
        for hit in query["hits"]:
            candidate_rows += 1
            coefficients = quotient_relation_coefficients(
                hit["a_index"], hit["r_witness"], len(r_points)
            )
            equation = {
                "coefficients": coefficients,
                "rhs": scalar,
                "a_index": hit["a_index"],
                "r_witness": list(hit["r_witness"]),
            }
            if basis.insert(coefficients, scalar):
                independent.append(equation)
            else:
                dependent_count += 1
        if basis.rank == width:
            break
    if basis.rank != width:
        raise RuntimeError(
            f"quotient rank stopped at {basis.rank}/{width}"
        )
    solution, solve_ops = solve_full_rank(independent, width, q)
    return {
        "solution_internal": solution,
        "attempted_scalars_internal": set(attempted_scalars),
        "summary": {
            "quotient_width": width,
            "full_width": len(r_points) + 2,
            "predicted_full_rank": len(r_points) + 1,
            "gauge_null_vector": [-4, 0] + [1] * len(r_points),
            "targets_attempted": len(attempted_scalars),
            "successful_targets": successful_targets,
            "candidate_relation_rows": candidate_rows,
            "dependent_candidate_rows": dependent_count,
            "independent_rows": len(independent),
            "quotient_rank": basis.rank,
            "target_budget": target_budget,
            "a_probes_total": probes,
            "a_probes_per_target": probes / len(attempted_scalars),
            "lookups_total": lookups,
            "target_build_ops": asdict(target_ops),
            "query_ops": asdict(query_ops),
            "incremental_linear_ops": asdict(basis.ops),
            "solve_linear_ops": asdict(solve_ops),
            "attack_solution": solution,
            "independent_equations": independent,
            "target_transcript": target_transcript,
            "target_transcript_digest": canonical_digest(target_transcript),
            "first_equation": independent[0],
        },
    }


def held_out_descent(
    curve: Any,
    q: int,
    generator: Point,
    a_points: list[Point],
    r_points: list[Point],
    d3: dict[Point, tuple[int, ...]],
    d4: dict[Point, tuple[int, ...]],
    solution: list[int],
    excluded_scalars: set[int],
    seed: int,
    target_count: int,
) -> dict[str, Any]:
    target_ops = Ops()
    d4_query_ops = Ops()
    d3_query_ops = Ops()
    d4_lookups = 0
    d3_lookups = 0
    supported = 0
    verified = 0
    alternate_agreement = 0
    first = None
    transcript = []
    attempted = 0
    for scalar in nonzero_scalar_stream(q, seed):
        if scalar in excluded_scalars:
            continue
        if attempted == target_count:
            break
        attempted += 1
        target = curve.mul(scalar, generator, target_ops)
        query = query_d4(curve, a_points, r_points, d4, target)
        alternate = query_r_plus_d3(
            curve, a_points, r_points, d3, target
        )
        d4_lookups += query["lookups"]
        d3_lookups += alternate["lookups"]
        for key, value in query["ops"].items():
            setattr(d4_query_ops, key, getattr(d4_query_ops, key) + value)
        for key, value in alternate["ops"].items():
            setattr(d3_query_ops, key, getattr(d3_query_ops, key) + value)
        if query["success"] != alternate["success"]:
            raise AssertionError("D4 and R+D3 support disagree")
        record = {
            "scalar": scalar,
            "target": point_json(target),
            "materialized_d4": {
                "success": query["success"],
                "a_index": query["a_index"],
                "r_witness": (
                    list(query["r_witness"])
                    if query["r_witness"] is not None
                    else None
                ),
            },
            "r_scan_plus_d3": {
                "success": alternate["success"],
                "a_index": alternate["a_index"],
                "r_witness": (
                    list(alternate["r_witness"])
                    if alternate["r_witness"] is not None
                    else None
                ),
            },
            "recovered_scalar": None,
        }
        if not query["success"]:
            transcript.append(record)
            continue
        supported += 1
        coefficients = quotient_relation_coefficients(
            query["a_index"], query["r_witness"], len(r_points)
        )
        recovered = dot_mod(coefficients, solution, q)
        if recovered != scalar:
            raise AssertionError("held-out typed descent recovered wrong log")
        verified += 1
        alternate_coefficients = quotient_relation_coefficients(
            alternate["a_index"],
            alternate["r_witness"],
            len(r_points),
        )
        alternate_recovered = dot_mod(
            alternate_coefficients, solution, q
        )
        if alternate_recovered != scalar:
            raise AssertionError("R+D3 descent recovered wrong log")
        record["recovered_scalar"] = recovered
        transcript.append(record)
        alternate_agreement += 1
        if first is None:
            first = {
                "target": point_json(target),
                "known_scalar": scalar,
                "recovered_scalar": recovered,
                "a_index": query["a_index"],
                "r_witness": list(query["r_witness"]),
            }
    return {
        "target_count": attempted,
        "supported_targets": supported,
        "verified_targets": verified,
        "success_probability": supported / max(1, attempted),
        "all_supported_verified": supported == verified,
        "alternate_r_plus_d3_agreement": alternate_agreement,
        "materialized_d4": {
            "lookups": d4_lookups,
            "lookups_per_target": d4_lookups / max(1, attempted),
            "query_ops": asdict(d4_query_ops),
        },
        "r_scan_plus_d3": {
            "lookups": d3_lookups,
            "lookups_per_target": d3_lookups / max(1, attempted),
            "query_ops": asdict(d3_query_ops),
        },
        "target_build_ops": asdict(target_ops),
        "transcript": transcript,
        "transcript_digest": canonical_digest(transcript),
        "first_verified_descent": first,
    }


def exact_support(
    curve: Any, a_points: list[Point], d4: dict[Point, tuple[int, ...]], q: int
) -> dict[str, Any]:
    ops = Ops()
    support = {
        curve.add(a_point, d4_point, ops)
        for a_point in a_points
        for d4_point in d4
    }
    return {
        "support_entries": len(support),
        "nonidentity_entries": len(support - {None}),
        "nonidentity_probability": len(support - {None}) / (q - 1),
        "diagnostic_ops": asdict(ops),
        "classification": "POINT_SUPPORT_AUDIT_NOT_ATTACK_ADVICE",
    }


def diagnostic_verify(
    curve: Any,
    q: int,
    generator: Point,
    progression: dict[str, Any],
    r_points: list[Point],
    solution: list[int],
) -> dict[str, Any]:
    census, census_record = COORDINATE.subgroup_log_census(
        curve, q, generator
    )
    p0 = point_from_json(progression["p0"])
    d = point_from_json(progression["d"])
    p0_log = census[p0]
    d_log = census[d]
    r_logs = [census[point] for point in r_points]
    expected = [
        (p0_log + 4 * r_logs[0]) % q,
        d_log,
    ] + [
        (value - r_logs[0]) % q for value in r_logs[1:]
    ]
    if solution != expected:
        raise AssertionError("quotient solution differs from diagnostic logs")
    return {
        "classification": "POST_HOC_DIAGNOSTIC_ONLY_NOT_ATTACK_ADVICE",
        "census": census_record,
        "quotient_solution_verified": True,
        "solution_digest": canonical_digest(solution),
        "expected_solution_digest": canonical_digest(expected),
    }


def run_family(
    curve: Any,
    curve_record: dict[str, Any],
    family: str,
    progression_size: int,
    transverse_size: int,
    seed: int,
    held_out_targets: int,
) -> dict[str, Any]:
    q = curve_record["q"]
    generator = point_from_json(curve_record["generator"])
    factor_base = make_transverse_factor_base(
        family,
        curve,
        q,
        generator,
        transverse_size,
        seed ^ 0x243F6A88,
    )
    r_points = [point_from_json(point) for point in factor_base["points"]]
    progression = build_public_progression(
        curve,
        q,
        progression_size,
        seed ^ 0x85A308D3,
        set(r_points),
    )
    a_points = [point_from_json(point) for point in progression["points"]]
    frozen_digest = canonical_digest(
        {
            "factor_base_digest": factor_base["digest"],
            "progression_digest": progression["digest"],
        }
    )
    compiler = compile_r_support(curve, r_points)
    relation = collect_relations(
        curve,
        q,
        generator,
        a_points,
        r_points,
        compiler["d4_internal"],
        seed ^ 0x13198A2E,
    )
    descent = held_out_descent(
        curve,
        q,
        generator,
        a_points,
        r_points,
        compiler["d3_internal"],
        compiler["d4_internal"],
        relation["solution_internal"],
        relation["attempted_scalars_internal"],
        seed ^ 0x03707344,
        held_out_targets,
    )
    support = exact_support(curve, a_points, compiler["d4_internal"], q)
    diagnostic = diagnostic_verify(
        curve,
        q,
        generator,
        progression,
        r_points,
        relation["solution_internal"],
    )
    if frozen_digest != canonical_digest(
        {
            "factor_base_digest": factor_base["digest"],
            "progression_digest": progression["digest"],
        }
    ):
        raise AssertionError("public construction mutated after freeze")
    factor_base_public = {
        key: value
        for key, value in factor_base.items()
        if key not in ("factor_base_scalars",)
    }
    result = {
        "family": family,
        "run_seed": seed,
        "attack_eligible": factor_base["attack_eligible"],
        "factor_base": factor_base_public,
        "progression": progression,
        "frozen_public_construction_digest": frozen_digest,
        "compiler": compiler["summary"],
        "relations": relation["summary"],
        "held_out_descent": descent,
        "exact_support": support,
        "diagnostic": diagnostic,
        "rho_reference": {
            "sqrt_q": math.sqrt(q),
            "materialized_d4_entries_over_sqrt_q": (
                compiler["summary"]["d4_entries"] / math.sqrt(q)
            ),
            "d3_entries_over_sqrt_q": (
                compiler["summary"]["d3_entries"] / math.sqrt(q)
            ),
        },
        "valid": True,
        "breakthrough_claim": False,
    }
    return result


def fit_exponent(points: list[tuple[int, float]]) -> float | None:
    return COORDINATE.fit_exponent(points)


def run_experiment(
    bit_sizes: list[int],
    seed: int,
    families: list[str],
    occupancy_lambda: float,
    held_out_targets: int,
) -> dict[str, Any]:
    for index, bits in enumerate(bit_sizes):
        exact_int(bits, f"bit_sizes[{index}]", 8)
    exact_int(seed, "seed")
    exact_int(held_out_targets, "held_out_targets", 1)
    allowed = {
        "random_x",
        "source_prf_x",
        "x_interval",
        "rational_union",
        "scalar_progression_control",
    }
    if not families or any(family not in allowed for family in families):
        raise ValueError("unsupported or empty family list")
    if occupancy_lambda <= 0:
        raise ValueError("occupancy_lambda must be positive")
    started = time.perf_counter()
    instances = []
    for bits in bit_sizes:
        curve_record = COORDINATE.generate_admissible_curve(
            bits, seed + bits * 1009
        )
        q = curve_record["q"]
        curve = Curve(
            curve_record["p"], curve_record["a"], curve_record["b"]
        )
        progression_size, transverse_size = TYPED.choose_sizes(
            q, occupancy_lambda
        )
        family_results = []
        for family_index, family in enumerate(families):
            family_results.append(
                run_family(
                    curve,
                    curve_record,
                    family,
                    progression_size,
                    transverse_size,
                    seed ^ (bits << 20) ^ (family_index * 0x9E3779B1),
                    held_out_targets,
                )
            )
        instances.append(
            {
                "curve": curve_record,
                "progression_size": progression_size,
                "transverse_size": transverse_size,
                "formal_occupancy": (
                    progression_size
                    * math.comb(transverse_size + 3, 4)
                    / q
                ),
                "families": family_results,
            }
        )
    scaling = {}
    for family in families:
        rows = [
            (instance["curve"]["q"], result)
            for instance in instances
            for result in instance["families"]
            if result["family"] == family
        ]
        scaling[family] = {
            "transverse_size": fit_exponent(
                [(q, result["factor_base"]["size"]) for q, result in rows]
            ),
            "d3_entries": fit_exponent(
                [(q, result["compiler"]["d3_entries"]) for q, result in rows]
            ),
            "d4_entries": fit_exponent(
                [(q, result["compiler"]["d4_entries"]) for q, result in rows]
            ),
            "relation_target_group_operations": fit_exponent(
                [
                    (
                        q,
                        result["relations"]["target_build_ops"][
                            "group_operations"
                        ]
                        + result["relations"]["query_ops"]["group_operations"],
                    )
                    for q, result in rows
                ]
            ),
            "d4_lookups_per_held_out_target": fit_exponent(
                [
                    (
                        q,
                        result["held_out_descent"]["materialized_d4"][
                            "lookups_per_target"
                        ],
                    )
                    for q, result in rows
                ]
            ),
            "r_d3_lookups_per_held_out_target": fit_exponent(
                [
                    (
                        q,
                        result["held_out_descent"]["r_scan_plus_d3"][
                            "lookups_per_target"
                        ],
                    )
                    for q, result in rows
                ]
            ),
        }
    attack_rows = [
        result
        for instance in instances
        for result in instance["families"]
        if result["attack_eligible"]
    ]
    return {
        "protocol": "EXP-ECDLP-COORD-EXPANSION-001-typed-five-ec-v1",
        "claim_status": [
            "HYPOTHESIS",
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NOVELTY-UNVERIFIED",
        ],
        "valid": True,
        "source": {
            "typed_five_ec_sha256": sha256_file(SCRIPT_PATH),
            "coordinate_expansion_sha256": sha256_file(COORDINATE_SOURCE),
            "typed_five_term_sha256": sha256_file(TYPED_SOURCE),
        },
        "config": {
            "bit_sizes": bit_sizes,
            "seed": seed,
            "families": families,
            "occupancy_lambda": occupancy_lambda,
            "held_out_targets": held_out_targets,
        },
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
        "instances": instances,
        "fitted_exponents": scaling,
        "summary": {
            "attack_eligible_rows": len(attack_rows),
            "all_quotient_ranks_full": all(
                row["relations"]["quotient_rank"]
                == row["relations"]["quotient_width"]
                for row in attack_rows
            ),
            "all_quotient_solutions_verified": all(
                row["diagnostic"]["quotient_solution_verified"]
                for row in attack_rows
            ),
            "all_supported_descents_verified": all(
                row["held_out_descent"]["all_supported_verified"]
                for row in attack_rows
            ),
            "minimum_exact_support_probability": min(
                row["exact_support"]["nonidentity_probability"]
                for row in attack_rows
            ),
            "success_gate": all(
                row["relations"]["quotient_rank"]
                == row["relations"]["quotient_width"]
                and row["diagnostic"]["quotient_solution_verified"]
                and row["held_out_descent"]["all_supported_verified"]
                and row["exact_support"]["nonidentity_probability"] >= 0.25
                for row in attack_rows
            ),
            "breakthrough_claim": False,
            "boundary": (
                "Functional toy relation architecture with materialized D4. "
                "No compressed compiler, sub-rho preprocessing, exponent "
                "improvement, or deployment claim."
            ),
        },
        "total_wall_seconds": time.perf_counter() - started,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bit-sizes", nargs="+", type=int, required=True)
    parser.add_argument("--seed", type=int, default=271828)
    parser.add_argument(
        "--families",
        nargs="+",
        default=[
            "random_x",
            "source_prf_x",
            "x_interval",
            "rational_union",
            "scalar_progression_control",
        ],
    )
    parser.add_argument("--occupancy-lambda", type=float, default=0.5)
    parser.add_argument("--held-out-targets", type=int, default=64)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(
        json.dumps(
            run_experiment(
                args.bit_sizes,
                args.seed,
                args.families,
                args.occupancy_lambda,
                args.held_out_targets,
            ),
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
