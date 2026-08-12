#!/usr/bin/env python3
"""Independent verifier for EXP-ECDLP-TT-NORM-RANK-001."""
from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import platform
import resource
import sys
import time
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence


SCRIPT_PATH = Path(__file__).resolve()
EXPERIMENT_ROOT = SCRIPT_PATH.parents[1]
GENERATOR_PATH = EXPERIMENT_ROOT / "src" / "generate_tt_norm_rank.py"
PROTOCOL = "EXP-ECDLP-TT-NORM-RANK-001-development-v3"
INTERPRETATION = "SANITY_ONLY"
Point = tuple[int, int] | None
Projective = tuple[int, int, int]
Fp2 = tuple[int, int]


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path}: top-level JSON must be an object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def exact_int(value: Any, label: str, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise AssertionError(f"{label} must be an exact integer")
    if minimum is not None and value < minimum:
        raise AssertionError(f"{label} must be at least {minimum}")
    return value


def exact_bool(value: Any, label: str) -> bool:
    if type(value) is not bool:
        raise AssertionError(f"{label} must be a boolean")
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


def affine_on_curve(point: Point, p: int, a: int, b: int) -> bool:
    if point is None:
        return True
    x, y = point
    return (
        0 <= x < p
        and 0 <= y < p
        and (y * y - x * x * x - a * x - b) % p == 0
    )


def projective_on_curve(point: Projective, p: int, a: int, b: int) -> bool:
    x, y, z = point
    if x % p == 0 and y % p == 0 and z % p == 0:
        return False
    return (
        y * y * z - x * x * x - a * x * z * z - b * z * z * z
    ) % p == 0


def affine_neg(point: Point, p: int) -> Point:
    return None if point is None else (point[0], (-point[1]) % p)


def affine_add(left: Point, right: Point, p: int, a: int) -> Point:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def affine_mul(scalar: int, point: Point, p: int, a: int) -> Point:
    if scalar < 0:
        return affine_mul(-scalar, affine_neg(point, p), p, a)
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = affine_add(result, addend, p, a)
        scalar >>= 1
        if scalar:
            addend = affine_add(addend, addend, p, a)
    return result


def curve_order(p: int, a: int, b: int) -> int:
    result = 1
    exponent = (p - 1) // 2
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            result += 1
        elif pow(rhs, exponent, p) == 1:
            result += 2
    return result


def canonical_square_root(rhs: int, p: int) -> int | None:
    rhs %= p
    if rhs == 0:
        return 0
    if pow(rhs, (p - 1) // 2, p) != 1:
        return None
    if p % 4 != 3:
        raise AssertionError("frozen square-root replay requires p=3 mod 4")
    root = pow(rhs, (p + 1) // 4, p)
    if root * root % p != rhs:
        return None
    return min(root, (-root) % p)


def projective_to_affine(point: Projective, p: int) -> Point:
    x, y, z = (coordinate % p for coordinate in point)
    if z == 0:
        return None
    inverse = pow(z, -1, p)
    return x * inverse % p, y * inverse % p


def affine_to_projective(point: Point) -> Projective:
    return (0, 1, 0) if point is None else (point[0], point[1], 1)


def rcb_combine(
    left: Projective,
    right: Projective,
    p: int,
    a: int,
    b: int,
) -> Projective:
    """Independent algebraic transcription of RCB Algorithm 1."""
    x1, y1, z1 = left
    x2, y2, z2 = right
    u0 = x1 * x2 % p
    u1 = y1 * y2 % p
    u2 = z1 * z2 % p
    cross_xy = ((x1 + y1) * (x2 + y2) - u0 - u1) % p
    cross_xz = ((x1 + z1) * (x2 + z2) - u0 - u2) % p
    cross_yz = ((y1 + z1) * (y2 + z2) - u1 - u2) % p

    z3 = (a * cross_xz + 3 * b * u2) % p
    x3 = (u1 - z3) % p
    z3 = (u1 + z3) % p
    y3 = x3 * z3 % p

    linear = (3 * u0 + a * u2) % p
    correction = (3 * b * cross_xz + a * (u0 - a * u2)) % p
    y3 = (y3 + linear * correction) % p
    x3 = (cross_xy * x3 - cross_yz * correction) % p
    z3 = (cross_yz * z3 + cross_xy * linear) % p
    return x3, y3, z3


def sum_five_rcb(points: Sequence[Projective], p: int, a: int, b: int) -> Projective:
    if len(points) != 5:
        raise AssertionError("exactly five points are required")
    result = rcb_combine(points[0], points[1], p, a, b)
    result = rcb_combine(result, points[2], p, a, b)
    result = rcb_combine(result, points[3], p, a, b)
    return rcb_combine(result, points[4], p, a, b)


def fp2_add(left: Fp2, right: Fp2, p: int) -> Fp2:
    return (left[0] + right[0]) % p, (left[1] + right[1]) % p


def fp2_sub(left: Fp2, right: Fp2, p: int) -> Fp2:
    return (left[0] - right[0]) % p, (left[1] - right[1]) % p


def fp2_mul(left: Fp2, right: Fp2, p: int, nu: int) -> Fp2:
    a, b = left
    c, d = right
    return (a * c + nu * b * d) % p, (a * d + b * c) % p


def fp2_inv(value: Fp2, p: int, nu: int) -> Fp2:
    a, b = value
    denominator = (a * a - nu * b * b) % p
    if denominator == 0:
        raise ZeroDivisionError("zero has no Fp2 inverse")
    inverse = pow(denominator, -1, p)
    return a * inverse % p, -b * inverse % p


def fp2_is_zero(value: Fp2) -> bool:
    return value[0] == 0 and value[1] == 0


def sha256_scalar(label: str, q: int) -> int:
    return int.from_bytes(hashlib.sha256(label.encode("ascii")).digest(), "big") % (
        q - 1
    ) + 1


def encoded_width(p: int) -> int:
    return max(1, (p.bit_length() + 7) // 8)


def digest_fp(values: Iterable[int], p: int) -> str:
    width = encoded_width(p)
    digest = hashlib.sha256()
    for value in values:
        digest.update((value % p).to_bytes(width, "big"))
    return digest.hexdigest()


def digest_fp2(values: Iterable[Fp2], p: int) -> str:
    width = encoded_width(p)
    digest = hashlib.sha256()
    for real, omega in values:
        digest.update((real % p).to_bytes(width, "big"))
        digest.update((omega % p).to_bytes(width, "big"))
    return digest.hexdigest()


def digest_projective(values: Iterable[Projective], p: int) -> str:
    width = encoded_width(p)
    digest = hashlib.sha256()
    for point in values:
        for coordinate in point:
            digest.update((coordinate % p).to_bytes(width, "big"))
    return digest.hexdigest()


def mixed_radix_tuple(linear_index: int, base: int) -> tuple[int, int, int, int, int]:
    digits = [0, 0, 0, 0, 0]
    remainder = linear_index
    for position in range(4, -1, -1):
        digits[position] = remainder % base
        remainder //= base
    if remainder:
        raise AssertionError("tuple index exceeds five-mode range")
    return tuple(digits)  # type: ignore[return-value]


def sample_indices(length: int) -> list[int]:
    return sorted({0, length // 2, length - 1})


def rescale_factor(label: str, p: int) -> int:
    return 1 + int.from_bytes(hashlib.sha256(label.encode("ascii")).digest(), "big") % (
        p - 1
    )


def rescale_projective(point: Projective, factor: int, p: int) -> Projective:
    return tuple(factor * coordinate % p for coordinate in point)  # type: ignore[return-value]


def rss_record() -> dict[str, Any]:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    system = platform.system()
    if system == "Darwin":
        normalized = int(raw)
        rule = "Darwin ru_maxrss is bytes"
    else:
        normalized = int(raw) * 1024
        rule = "non-Darwin ru_maxrss treated as KiB"
    return {
        "platform": system,
        "raw_ru_maxrss": raw,
        "normalization": rule,
        "bytes": normalized,
    }


def point_from_record(value: Any, label: str) -> Point:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise AssertionError(f"{label} must be an affine pair or null")
    return exact_int(value[0], f"{label}[0]", 0), exact_int(
        value[1], f"{label}[1]", 0
    )


def projective_from_record(value: Any, label: str) -> Projective:
    if not isinstance(value, list) or len(value) != 3:
        raise AssertionError(f"{label} must be a projective triple")
    return tuple(exact_int(item, f"{label}[{index}]", 0) for index, item in enumerate(value))  # type: ignore[return-value]


def audit_manifest(manifest_record: dict[str, Any]) -> list[dict[str, Any]]:
    manifest = manifest_record.get("manifest")
    if not isinstance(manifest, dict):
        raise AssertionError("manifest record is missing its sole manifest object")
    if manifest.get("id") != "MANIFEST-ECDLP-TT-NORM-RANK-001":
        raise AssertionError("unexpected instance manifest ID")
    if manifest.get("version") != 1:
        raise AssertionError("unexpected instance manifest version")
    if manifest.get("mode_order") != ["P1", "P2", "P3", "P4", "P5"]:
        raise AssertionError("mode order mismatch")
    if manifest.get("addition_tree") != "Add(Add(Add(Add(P1,P2),P3),P4),P5)":
        raise AssertionError("addition tree mismatch")
    addition_law = manifest.get("addition_law")
    if not isinstance(addition_law, dict):
        raise AssertionError("addition law record is missing")
    gate_lines = addition_law.get("normalized_gate_text")
    if not isinstance(gate_lines, list) or len(gate_lines) != 40:
        raise AssertionError("exactly 40 normalized RCB gates are required")
    gate_digest = hashlib.sha256("\n".join(gate_lines).encode("ascii")).hexdigest()
    if gate_digest != addition_law.get("normalized_gate_text_sha256"):
        raise AssertionError("RCB gate digest mismatch")
    if addition_law.get("b3") != "3*b mod p":
        raise AssertionError("b3 convention mismatch")

    instances = manifest.get("instances")
    if not isinstance(instances, list) or len(instances) != 6:
        raise AssertionError("six frozen instances are required")
    audited: list[dict[str, Any]] = []
    for instance in instances:
        if not isinstance(instance, dict):
            raise AssertionError("instance must be an object")
        curve_id = str(instance.get("curve_id"))
        p = exact_int(instance["field"]["p"], f"{curve_id}.p", 5)
        curve = instance.get("curve")
        subgroup = instance.get("subgroup")
        if not isinstance(curve, dict) or not isinstance(subgroup, dict):
            raise AssertionError(f"{curve_id}: curve or subgroup record missing")
        a = exact_int(curve["a"], f"{curve_id}.a", 0)
        b = exact_int(curve["b"], f"{curve_id}.b", 0)
        q = exact_int(subgroup["q"], f"{curve_id}.q", 3)
        size = exact_int(instance["factor_base_size_B"], f"{curve_id}.B", 2)
        if not is_prime(p) or not is_prime(q):
            raise AssertionError(f"{curve_id}: p and q must be prime")
        discriminant_term = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p
        if discriminant_term == 0:
            raise AssertionError(f"{curve_id}: singular curve")
        if curve_order(p, a, b) != q or curve.get("group_order") != q:
            raise AssertionError(f"{curve_id}: curve order mismatch")
        if curve.get("cofactor") != 1 or curve.get("frobenius_trace") != p + 1 - q:
            raise AssertionError(f"{curve_id}: trace or cofactor mismatch")
        expected_j = 1728 * 4 * pow(a, 3, p) * pow(discriminant_term, -1, p) % p
        if curve.get("j_invariant") != expected_j:
            raise AssertionError(f"{curve_id}: j-invariant mismatch")
        generator = point_from_record(subgroup["generator_affine"], f"{curve_id}.G")
        if generator is None or not affine_on_curve(generator, p, a, b):
            raise AssertionError(f"{curve_id}: generator is invalid")
        if affine_mul(q, generator, p, a) is not None:
            raise AssertionError(f"{curve_id}: generator order mismatch")
        if projective_from_record(
            subgroup["generator_projective"], f"{curve_id}.G_projective"
        ) != affine_to_projective(generator):
            raise AssertionError(f"{curve_id}: generator representations disagree")

        extension = instance.get("quadratic_extension")
        if not isinstance(extension, dict):
            raise AssertionError(f"{curve_id}: extension record missing")
        nu = exact_int(extension["nu"], f"{curve_id}.nu", 1)
        if pow(nu, (p - 1) // 2, p) != p - 1:
            raise AssertionError(f"{curve_id}: nu is not a nonresidue")
        if extension.get("omega_trace") != 0 or extension.get("omega_norm") != (-nu) % p:
            raise AssertionError(f"{curve_id}: extension trace or norm mismatch")
        if extension.get("conjugation") != "omega -> -omega":
            raise AssertionError(f"{curve_id}: conjugation mismatch")

        registries = instance.get("registries")
        if not isinstance(registries, dict) or set(registries) != {
            "random_unique",
            "x_interval",
            "consecutive_scalar_control",
        }:
            raise AssertionError(f"{curve_id}: registry family mismatch")
        expected_x_interval: list[Point] = []
        for x in range(p):
            root = canonical_square_root((x * x * x + a * x + b) % p, p)
            if root is not None:
                expected_x_interval.append((x, root))
                if len(expected_x_interval) == size:
                    break
        for family, records in registries.items():
            if not isinstance(records, list) or len(records) != size:
                raise AssertionError(f"{curve_id}:{family}: size mismatch")
            points: list[Point] = []
            identifiers: list[str] = []
            for index, record in enumerate(records):
                if not isinstance(record, dict):
                    raise AssertionError(f"{curve_id}:{family}: invalid point record")
                point_id = str(record.get("point_id"))
                affine = point_from_record(record.get("affine"), f"{point_id}.affine")
                projective = projective_from_record(
                    record.get("projective"), f"{point_id}.projective"
                )
                if affine is None or affine_to_projective(affine) != projective:
                    raise AssertionError(f"{point_id}: affine/projective mismatch")
                if not affine_on_curve(affine, p, a, b):
                    raise AssertionError(f"{point_id}: point is off curve")
                source = record.get("source")
                if not isinstance(source, dict):
                    raise AssertionError(f"{point_id}: source is missing")
                if family == "random_unique":
                    label = str(source.get("label"))
                    scalar = sha256_scalar(label, q)
                    if source.get("kind") != "sha256_to_scalar" or source.get("scalar") != scalar:
                        raise AssertionError(f"{point_id}: random source mismatch")
                    if affine_mul(scalar, generator, p, a) != affine:
                        raise AssertionError(f"{point_id}: random scalar replay mismatch")
                elif family == "x_interval":
                    if source.get("kind") != "first_affine_x" or affine != expected_x_interval[index]:
                        raise AssertionError(f"{point_id}: x-interval replay mismatch")
                else:
                    scalar = index + 1
                    if source.get("kind") != "consecutive_scalar_control" or source.get("scalar") != scalar:
                        raise AssertionError(f"{point_id}: scalar-control source mismatch")
                    if affine_mul(scalar, generator, p, a) != affine:
                        raise AssertionError(f"{point_id}: scalar-control replay mismatch")
                points.append(affine)
                identifiers.append(point_id)
            if len(set(points)) != size or len(set(identifiers)) != size:
                raise AssertionError(f"{curve_id}:{family}: duplicate primary entries")

        primary_targets = instance.get("primary_targets")
        if not isinstance(primary_targets, list) or len(primary_targets) != 3:
            raise AssertionError(f"{curve_id}: primary target count mismatch")
        for target in primary_targets:
            target_id = str(target.get("point_id"))
            affine = point_from_record(target.get("affine"), f"{target_id}.affine")
            projective = projective_from_record(
                target.get("projective"), f"{target_id}.projective"
            )
            source = target.get("source")
            if affine is None or affine_to_projective(affine) != projective or not isinstance(source, dict):
                raise AssertionError(f"{target_id}: malformed target")
            label = str(source.get("label"))
            scalar = sha256_scalar(label, q)
            if source.get("scalar") != scalar or affine_mul(scalar, generator, p, a) != affine:
                raise AssertionError(f"{target_id}: target scalar replay mismatch")
        audited.append(
            {
                "curve_id": curve_id,
                "p": p,
                "q": q,
                "a": a,
                "b": b,
                "B": size,
                "nu": nu,
                "j_invariant": expected_j,
                "manifest_valid": True,
            }
        )
    return audited


def audit_execution_matrix(record: dict[str, Any]) -> dict[str, Any]:
    matrix = record.get("execution_matrix")
    if not isinstance(matrix, dict):
        raise AssertionError("execution matrix is missing")
    if matrix.get("id") != "MATRIX-ECDLP-TT-NORM-RANK-003" or matrix.get("version") != 3:
        raise AssertionError("execution matrix version mismatch")
    counts = matrix.get("aggregate_counts_per_path")
    if not isinstance(counts, dict):
        raise AssertionError("aggregate execution counts are missing")
    fp_n = exact_int(counts["fp_rank_multiplication_upper_bound_including_controls"], "fp.N")
    fp_e = exact_int(counts["fp_rank_elimination_subtraction_upper_bound_including_controls"], "fp.E")
    fp_p = exact_int(counts["fp_rank_working_matrix_coefficients_including_controls"], "fp.P")
    k_n = exact_int(counts["fp2_rank_multiplication_upper_bound"], "fp2.N")
    k_e = exact_int(counts["fp2_rank_elimination_subtraction_upper_bound"], "fp2.E")
    k_p = exact_int(counts["fp2_rank_working_matrix_coefficients"], "fp2.P")
    if fp_n != fp_e + fp_p or k_n != k_e + k_p:
        raise AssertionError("N=E+P aggregate identity failed")
    fp_t = 3 * fp_e + 6 * fp_p
    k_t = 3 * k_e + 6 * k_p
    if counts.get("fp_rank_logical_traffic_words") != fp_t:
        raise AssertionError("F_p traffic aggregate mismatch")
    if counts.get("fp2_rank_logical_traffic_words") != k_t:
        raise AssertionError("F_p2 traffic aggregate mismatch")
    if counts.get("rank_logical_traffic_upper_bound_base_field_word_equivalents") != fp_t + 2 * k_t:
        raise AssertionError("base-word traffic conversion mismatch")
    jobs = matrix.get("mandatory_job_counts")
    expected_jobs = {
        "source_tables": 24,
        "semantic_cells": 60,
        "ec_rank_jobs_per_path": 264,
        "control_rank_jobs_per_path": 24,
        "total_rank_jobs_per_path": 288,
        "cohort_span_jobs_per_path": 12,
        "d2_d3_comparator_jobs_per_path": 18,
    }
    if not isinstance(jobs, dict) or any(jobs.get(key) != value for key, value in expected_jobs.items()):
        raise AssertionError("mandatory job count mismatch")
    if matrix.get("optional_cells") != []:
        raise AssertionError("optional cells are forbidden")
    return {"valid": True, "aggregate_counts": counts, "mandatory_job_counts": jobs}


def audit_mutation_manifest(record: dict[str, Any]) -> dict[str, Any]:
    manifest = record.get("mutation_manifest")
    if not isinstance(manifest, dict):
        raise AssertionError("mutation manifest is missing")
    mutations = manifest.get("mutations")
    controls = manifest.get("controls")
    if not isinstance(mutations, list) or len(mutations) != 15:
        raise AssertionError("exactly 15 mutations are required")
    if not isinstance(controls, list) or len(controls) != 6:
        raise AssertionError("exactly six tensor controls are required")
    ids = [str(row.get("id")) for row in mutations if isinstance(row, dict)]
    if len(ids) != 15 or len(set(ids)) != 15:
        raise AssertionError("mutation IDs must be unique")
    expected = [f"M{index:02d}" for index in range(1, 16)]
    if [item.split("-", 1)[0] for item in ids] != expected:
        raise AssertionError("mutation IDs or order differ from the frozen manifest")
    return {"valid": True, "mutation_count": 15, "control_count": 6}


def oriented_vectors(
    values: Sequence[Any], B: int, cut: int
) -> tuple[list[list[Any]], int, int]:
    original_rows = B**cut
    original_columns = B ** (5 - cut)
    if len(values) != original_rows * original_columns:
        raise AssertionError("tensor length does not match unfolding")
    if original_rows <= original_columns:
        vectors = [
            list(values[row * original_columns : (row + 1) * original_columns])
            for row in range(original_rows)
        ]
        return vectors, original_rows, original_columns
    vectors = [
        [values[row * original_columns + column] for row in range(original_rows)]
        for column in range(original_columns)
    ]
    return vectors, original_columns, original_rows


def rank_fp_right_pivots(
    values: Sequence[int], B: int, cut: int, p: int
) -> tuple[int, dict[str, Any], str]:
    vectors, r, c = oriented_vectors(values, B, cut)
    basis: dict[int, list[int]] = {}
    traffic = {
        "materialization": 2 * r * c,
        "pivot_scan": 0,
        "elimination_update": 0,
        "normalization": 0,
        "certificate": 0,
    }
    arithmetic = {"multiplications": 0, "subtractions": 0, "inversions": 0}
    for vector in vectors:
        cursor = c - 1
        while cursor >= 0:
            traffic["pivot_scan"] += 1
            if vector[cursor] % p == 0:
                cursor -= 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = pow(vector[cursor] % p, -1, p)
                vector[:] = [(entry * inverse) % p for entry in vector]
                traffic["normalization"] += 2 * c
                arithmetic["multiplications"] += c
                arithmetic["inversions"] += 1
                basis[cursor] = vector
                break
            factor = vector[cursor] % p
            vector[:] = [
                (entry - factor * pivot_entry) % p
                for entry, pivot_entry in zip(vector, prior)
            ]
            traffic["elimination_update"] += 3 * c
            arithmetic["multiplications"] += c
            arithmetic["subtractions"] += c
            cursor -= 1

    width = encoded_width(p)
    certificate = hashlib.sha256()
    for pivot in sorted(basis, reverse=True):
        certificate.update(pivot.to_bytes(max(1, (c.bit_length() + 7) // 8), "big"))
        for entry in basis[pivot]:
            certificate.update((entry % p).to_bytes(width, "big"))
        traffic["certificate"] += c
    total = sum(traffic.values())
    upper_p = r * c
    upper_e = c * r * (r - 1) // 2
    upper = {
        "P": upper_p,
        "E": upper_e,
        "N": upper_e + upper_p,
        "traffic": 3 * upper_e + 6 * upper_p,
    }
    if traffic["pivot_scan"] > upper_p or total > upper["traffic"]:
        raise AssertionError("F_p rank traffic exceeded the v3 ceiling")
    return len(basis), {
        "field": "F_p",
        "r": r,
        "c": c,
        "traffic": {**traffic, "total_field_words": total, "base_word_equivalents": total},
        "arithmetic": arithmetic,
        "upper": upper,
    }, certificate.hexdigest()


def rank_fp2_right_pivots(
    values: Sequence[Fp2], B: int, cut: int, p: int, nu: int
) -> tuple[int, dict[str, Any], str]:
    vectors, r, c = oriented_vectors(values, B, cut)
    basis: dict[int, list[Fp2]] = {}
    traffic = {
        "materialization": 2 * r * c,
        "pivot_scan": 0,
        "elimination_update": 0,
        "normalization": 0,
        "certificate": 0,
    }
    arithmetic = {"multiplications": 0, "subtractions": 0, "inversions": 0}
    for vector in vectors:
        cursor = c - 1
        while cursor >= 0:
            traffic["pivot_scan"] += 1
            if fp2_is_zero(vector[cursor]):
                cursor -= 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = fp2_inv(vector[cursor], p, nu)
                vector[:] = [fp2_mul(entry, inverse, p, nu) for entry in vector]
                traffic["normalization"] += 2 * c
                arithmetic["multiplications"] += c
                arithmetic["inversions"] += 1
                basis[cursor] = vector
                break
            factor = vector[cursor]
            vector[:] = [
                fp2_sub(entry, fp2_mul(factor, pivot_entry, p, nu), p)
                for entry, pivot_entry in zip(vector, prior)
            ]
            traffic["elimination_update"] += 3 * c
            arithmetic["multiplications"] += c
            arithmetic["subtractions"] += c
            cursor -= 1

    width = encoded_width(p)
    certificate = hashlib.sha256()
    for pivot in sorted(basis, reverse=True):
        certificate.update(pivot.to_bytes(max(1, (c.bit_length() + 7) // 8), "big"))
        for real, omega in basis[pivot]:
            certificate.update((real % p).to_bytes(width, "big"))
            certificate.update((omega % p).to_bytes(width, "big"))
        traffic["certificate"] += c
    total = sum(traffic.values())
    upper_p = r * c
    upper_e = c * r * (r - 1) // 2
    upper = {
        "P": upper_p,
        "E": upper_e,
        "N": upper_e + upper_p,
        "traffic": 3 * upper_e + 6 * upper_p,
    }
    if traffic["pivot_scan"] > upper_p or total > upper["traffic"]:
        raise AssertionError("F_p2 rank traffic exceeded the v3 ceiling")
    return len(basis), {
        "field": "F_p2",
        "r": r,
        "c": c,
        "traffic": {
            **traffic,
            "total_field_words": total,
            "base_word_equivalents": 2 * total,
        },
        "arithmetic": arithmetic,
        "upper": upper,
    }, certificate.hexdigest()


def hilbert_cap(B: int, degrees: Sequence[int], cut: int) -> int:
    dimensions = [min(B, 3 * degree) for degree in degrees]
    return min(math.prod(dimensions[:cut]), math.prod(dimensions[cut:]))


def rank_record(
    values: Sequence[int] | Sequence[Fp2],
    *,
    tensor: str,
    exponent: int | None,
    B: int,
    cut: int,
    p: int,
    nu: int,
    field: str,
) -> dict[str, Any]:
    if tensor == "g":
        degrees = [16, 16, 8, 4, 2]
    else:
        power = exponent or 1
        degrees = [32 * power, 32 * power, 16 * power, 8 * power, 4 * power]
    cap = hilbert_cap(B, degrees, cut)
    if field == "F_p":
        rank, accounting, certificate = rank_fp_right_pivots(
            values, B, cut, p  # type: ignore[arg-type]
        )
    elif field == "F_p2":
        rank, accounting, certificate = rank_fp2_right_pivots(
            values, B, cut, p, nu  # type: ignore[arg-type]
        )
    else:
        raise AssertionError(f"unsupported rank field: {field}")
    if rank > cap:
        raise AssertionError(f"{tensor} cut {cut}: rank {rank} exceeds Hilbert cap {cap}")
    return {
        "tensor": tensor,
        "exponent": exponent,
        "cut": cut,
        "field": field,
        "rank_kind": "exact",
        "rank": rank,
        "hilbert_cap": cap,
        "certificate_digest": certificate,
        "accounting": accounting,
    }


def control_tensors() -> list[dict[str, Any]]:
    p = 947
    B = 4
    index_space = list(itertools.product(range(B), repeat=5))
    separable = [math.prod(index + 1 for index in indices) % p for indices in index_space]
    norm = [
        ((indices[0] + 1) ** 2 - 2 * (indices[1] + 1) ** 2) % p
        for indices in index_space
    ]
    zero = [0] * (B**5)
    spike = [1] + [0] * (B**5 - 1)
    dense = [
        int.from_bytes(
            hashlib.sha256(
                ("TT-NORM-DENSE|" + "|".join(str(index) for index in indices)).encode(
                    "ascii"
                )
            ).digest(),
            "big",
        )
        % p
        for indices in index_space
    ]
    asymmetric: list[int] = []
    for _, i2, i3, i4, i5 in index_space:
        state = 0 if i2 == 0 and i3 == 0 else (1 if i2 == 0 else 2)
        if state == 0:
            value = int(i5 == 0)
        elif state == 1:
            value = int(i5 == (1 if i4 == 0 else 2))
        else:
            value = int(i5 == 3)
        asymmetric.append(value)
    definitions = [
        ("CTRL-SEPARABLE", separable, [1, 1, 1, 1]),
        ("CTRL-NORM", norm, [2, 1, 1, 1]),
        ("CTRL-ZERO", zero, [0, 0, 0, 0]),
        ("CTRL-SPIKE", spike, [1, 1, 1, 1]),
        ("CTRL-DENSE", dense, [4, 16, 16, 4]),
        ("CTRL-ASYMMETRIC", asymmetric, [1, 2, 3, 4]),
    ]
    results: list[dict[str, Any]] = []
    for control_id, values, expected in definitions:
        ranks = [
            rank_record(
                values,
                tensor="control",
                exponent=1,
                B=B,
                cut=cut,
                p=p,
                nu=2,
                field="F_p",
            )
            for cut in range(1, 5)
        ]
        actual = [record["rank"] for record in ranks]
        if actual != expected:
            raise AssertionError(f"{control_id}: expected {expected}, got {actual}")
        results.append(
            {
                "id": control_id,
                "B": B,
                "field": "F_947",
                "cut_ranks": actual,
                "digest": digest_fp(values, p),
                "ranks": ranks,
            }
        )
    return results


def target_for_cell(instance: dict[str, Any], target_name: str) -> tuple[str, Point, Projective]:
    p = instance["field"]["p"]
    a = instance["curve"]["a"]
    b = instance["curve"]["b"]
    curve_id = instance["curve_id"]
    if target_name.startswith("Q") and len(target_name) == 3:
        index = int(target_name[1:])
        record = instance["primary_targets"][index]
        return (
            record["point_id"],
            point_from_record(record["affine"], f"{curve_id}.{target_name}.affine"),
            projective_from_record(
                record["projective"], f"{curve_id}.{target_name}.projective"
            ),
        )
    if target_name == "IDENTITY":
        return f"{curve_id}-Q-IDENTITY", None, (0, 1, 0)
    if target_name == "PLANTED":
        control = next(
            row
            for row in instance["control_targets"]
            if row["source"]["kind"] == "sum_first_five_with_repetition"
        )
        indices = control["source"]["indices"]
        registry = instance["registries"][control["source"]["registry"]]
        point: Point = None
        projective_points: list[Projective] = []
        for index in indices:
            projective_points.append(
                projective_from_record(
                    registry[index]["projective"], "planted.registry.projective"
                )
            )
            point = affine_add(
                point,
                point_from_record(registry[index]["affine"], "planted.registry"),
                p,
                a,
            )
        projective = sum_five_rcb(projective_points, p, a, b)
        if projective_to_affine(projective, p) != point:
            raise AssertionError("planted target RCB replay mismatch")
        return control["point_id"], point, projective
    raise AssertionError(f"unknown target name: {target_name}")


def source_table(
    instance: dict[str, Any],
    family: str,
    *,
    rescaled: bool,
) -> dict[str, Any]:
    curve_id = instance["curve_id"]
    p = instance["field"]["p"]
    a = instance["curve"]["a"]
    b = instance["curve"]["b"]
    B = instance["factor_base_size_B"]
    registry = instance["registries"][family]
    affine_points = [point_from_record(row["affine"], f"{curve_id}:{family}") for row in registry]
    if any(point is None for point in affine_points):
        raise AssertionError("factor-base identity entries are forbidden")
    mode_points: list[list[Projective]] = []
    mode_factors: list[list[int]] = []
    for mode in range(5):
        points: list[Projective] = []
        factors: list[int] = []
        for record in registry:
            point = projective_from_record(record["projective"], "registry.projective")
            if rescaled:
                label = (
                    f"EXP-ECDLP-TT-NORM-RANK-001|RESCALE|{curve_id}|"
                    f"P{mode + 1}|{record['point_id']}"
                )
                factor = rescale_factor(label, p)
                point = rescale_projective(point, factor, p)
            else:
                factor = 1
            points.append(point)
            factors.append(factor)
        mode_points.append(points)
        mode_factors.append(factors)

    tuple_count = B**5
    outputs: list[Projective] = []
    affine_sums: list[Point] = []
    homogeneous_h_factors: list[int] = []
    invalid_projective = 0
    affine_mismatches = 0
    degrees = (16, 16, 8, 4, 2)
    for linear_index in range(tuple_count):
        indices = mixed_radix_tuple(linear_index, B)
        inputs = [mode_points[mode][indices[mode]] for mode in range(5)]
        output = sum_five_rcb(inputs, p, a, b)
        if not projective_on_curve(output, p, a, b):
            invalid_projective += 1
        expected: Point = None
        for index in indices:
            expected = affine_add(expected, affine_points[index], p, a)
        if projective_to_affine(output, p) != expected:
            affine_mismatches += 1
        outputs.append(output)
        affine_sums.append(expected)
        factor = 1
        for mode, index in enumerate(indices):
            factor = factor * pow(mode_factors[mode][index], 2 * degrees[mode], p) % p
        homogeneous_h_factors.append(factor)
    if invalid_projective or affine_mismatches:
        raise AssertionError(
            f"{curve_id}:{family}: invalid RCB outputs={invalid_projective}, "
            f"affine mismatches={affine_mismatches}"
        )
    return {
        "curve_id": curve_id,
        "family": family,
        "rescaled": rescaled,
        "tuple_count": tuple_count,
        "rcb_calls": 4 * tuple_count,
        "affine_replay_additions": 4 * tuple_count,
        "outputs": outputs,
        "affine_sums": affine_sums,
        "homogeneous_h_factors": homogeneous_h_factors,
        "output_digest": digest_projective(outputs, p),
        "invalid_projective_count": invalid_projective,
        "affine_replay_mismatches": affine_mismatches,
    }


def tensor_samples(
    g_values: Sequence[Fp2],
    h_values: Sequence[int],
    sources: Sequence[Projective],
    B: int,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for linear_index in sample_indices(len(h_values)):
        result.append(
            {
                "linear_index": linear_index,
                "tuple": list(mixed_radix_tuple(linear_index, B)),
                "source": list(sources[linear_index]),
                "g": list(g_values[linear_index]),
                "h": h_values[linear_index],
            }
        )
    return result


def evaluate_cell(
    instance: dict[str, Any],
    table: dict[str, Any],
    family: str,
    target_name: str,
    *,
    rescaled: bool,
    unscaled_h: Sequence[int] | None = None,
) -> tuple[dict[str, Any], list[Fp2], list[int], dict[int, list[int]]]:
    curve_id = instance["curve_id"]
    p = instance["field"]["p"]
    nu = instance["quadratic_extension"]["nu"]
    trace = instance["quadratic_extension"]["omega_trace"]
    norm = instance["quadratic_extension"]["omega_norm"]
    B = instance["factor_base_size_B"]
    target_id, target_affine, target_projective = target_for_cell(instance, target_name)
    target_scale = 1
    if rescaled:
        if family != "random_unique" or target_name != "Q00":
            raise AssertionError("only random_unique:Q00 has a rescaling cell")
        target_scale = rescale_factor(
            f"EXP-ECDLP-TT-NORM-RANK-001|RESCALE|{curve_id}|Q00", p
        )
        target_projective = rescale_projective(target_projective, target_scale, p)
    xq, yq, zq = target_projective
    c1 = zq * zq % p
    c2 = -zq * (2 * xq + trace * yq) % p
    c3 = (xq * xq + trace * xq * yq + norm * yq * yq) % p
    c4 = trace * zq * zq % p
    c5 = -zq * (trace * xq + 2 * norm * yq) % p
    c6 = norm * zq * zq % p
    if trace == 0 and c4 != 0:
        raise AssertionError("trace-zero basis must eliminate the XY coefficient")

    g_values: list[Fp2] = []
    h_values: list[int] = []
    norm_mismatches = 0
    source_span_mismatches = 0
    zero_set_mismatches = 0
    rescaling_mismatches = 0
    witness_count = 0
    for linear_index, source in enumerate(table["outputs"]):
        x, y, z = source
        ex = (zq * x - xq * z) % p
        ey = (zq * y - yq * z) % p
        g = (ex, ey)
        product = fp2_mul(g, (ex, -ey % p), p, nu)
        quadratic = (ex * ex + trace * ex * ey + norm * ey * ey) % p
        if product[1] != 0 or product[0] != quadratic:
            norm_mismatches += 1
        source_value = (
            c1 * x * x
            + c2 * x * z
            + c3 * z * z
            + c4 * x * y
            + c5 * y * z
            + c6 * y * y
        ) % p
        if source_value != quadratic:
            source_span_mismatches += 1
        is_zero = fp2_is_zero(g)
        expected_zero = table["affine_sums"][linear_index] == target_affine
        if is_zero != expected_zero:
            zero_set_mismatches += 1
        if is_zero:
            witness_count += 1
        if rescaled:
            if unscaled_h is None:
                raise AssertionError("rescaled cell requires unscaled h values")
            expected_h = (
                unscaled_h[linear_index]
                * target_scale
                * target_scale
                * table["homogeneous_h_factors"][linear_index]
            ) % p
            if quadratic != expected_h:
                rescaling_mismatches += 1
        g_values.append(g)
        h_values.append(quadratic)
    mismatch_total = (
        norm_mismatches
        + source_span_mismatches
        + zero_set_mismatches
        + rescaling_mismatches
    )
    if mismatch_total:
        raise AssertionError(
            f"{curve_id}:{family}:{target_name}: semantic mismatch total {mismatch_total}"
        )

    power_values: dict[int, list[int]] = {}
    power_digests: dict[str, str] = {}
    if family == "random_unique" and target_name == "Q00" and not rescaled:
        current = h_values
        for exponent in (2, 4, 8):
            current = [value * value % p for value in current]
            power_values[exponent] = current
            power_digests[str(exponent)] = digest_fp(current, p)
    cell_id = f"{curve_id}:{family}:{target_name}" + (":rescaled" if rescaled else "")
    semantic = {
        "tuple_count": len(h_values),
        "g_digest": digest_fp2(g_values, p),
        "h_digest": digest_fp(h_values, p),
        "power_digests": power_digests,
        "norm_mismatches": norm_mismatches,
        "source_span_mismatches": source_span_mismatches,
        "zero_set_mismatches": zero_set_mismatches,
        "rescaling_mismatches": rescaling_mismatches,
        "witness_count": witness_count,
        "g_value_count": len(set(g_values)),
        "h_value_count": len(set(h_values)),
        "samples": tensor_samples(g_values, h_values, table["outputs"], B),
    }
    return {
        "cell_id": cell_id,
        "target_id": target_id,
        "target_name": target_name,
        "rescaled": rescaled,
        "semantic": semantic,
        "ranks": [],
    }, g_values, h_values, power_values


def attach_rank_schedule(
    cell: dict[str, Any],
    g_values: Sequence[Fp2],
    h_values: Sequence[int],
    power_values: dict[int, list[int]],
    *,
    family: str,
    target_name: str,
    rescaled: bool,
    B: int,
    p: int,
    nu: int,
) -> None:
    records: list[dict[str, Any]] = []
    full_h = (
        target_name == "Q00"
        or (family == "random_unique" and target_name in {"IDENTITY", "PLANTED"})
    )
    if rescaled:
        full_h = family == "random_unique" and target_name == "Q00"
    if full_h:
        records.extend(
            rank_record(
                h_values,
                tensor="h",
                exponent=1,
                B=B,
                cut=cut,
                p=p,
                nu=nu,
                field="F_p",
            )
            for cut in range(1, 5)
        )
    elif target_name in {"Q01", "Q02"} and family in {
        "random_unique",
        "x_interval",
    }:
        records.append(
            rank_record(
                h_values,
                tensor="h",
                exponent=1,
                B=B,
                cut=2,
                p=p,
                nu=nu,
                field="F_p",
            )
        )
    if family == "random_unique" and target_name == "Q00" and not rescaled:
        records.extend(
            rank_record(
                g_values,
                tensor="g",
                exponent=None,
                B=B,
                cut=cut,
                p=p,
                nu=nu,
                field="F_p2",
            )
            for cut in range(1, 5)
        )
        for exponent in (2, 4, 8):
            records.extend(
                rank_record(
                    power_values[exponent],
                    tensor="h_power",
                    exponent=exponent,
                    B=B,
                    cut=cut,
                    p=p,
                    nu=nu,
                    field="F_p",
                )
                for cut in range(1, 5)
            )
    cell["ranks"] = records


def rank_vector_family(vectors: Sequence[Sequence[int]], p: int) -> int:
    if not vectors:
        return 0
    length = len(vectors[0])
    basis: dict[int, list[int]] = {}
    for source in vectors:
        if len(source) != length:
            raise AssertionError("cohort vectors have different lengths")
        vector = list(source)
        cursor = length - 1
        while cursor >= 0:
            if vector[cursor] % p == 0:
                cursor -= 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = pow(vector[cursor], -1, p)
                basis[cursor] = [value * inverse % p for value in vector]
                break
            factor = vector[cursor]
            vector = [
                (value - factor * pivot) % p
                for value, pivot in zip(vector, prior)
            ]
            cursor -= 1
    return len(basis)


def comparator_record(instance: dict[str, Any], family: str) -> dict[str, Any]:
    p = instance["field"]["p"]
    a = instance["curve"]["a"]
    B = instance["factor_base_size_B"]
    points = [
        point_from_record(row["affine"], f"{instance['curve_id']}:{family}")
        for row in instance["registries"][family]
    ]
    d2: dict[Point, tuple[int, int]] = {}
    additions = 0
    for i, left in enumerate(points):
        for j, right in enumerate(points):
            additions += 1
            d2.setdefault(affine_add(left, right, p, a), (i, j))
    d3: dict[Point, tuple[int, int, int]] = {}
    for partial, witness in d2.items():
        for k, point in enumerate(points):
            additions += 1
            d3.setdefault(affine_add(partial, point, p, a), (*witness, k))
    N2 = len(d2)
    N3 = len(d3)
    index_bytes = max(1, ((B - 1).bit_length() + 7) // 8)
    point_bytes = 1 + 2 * encoded_width(p)
    d2_record_bytes = point_bytes + 2 * index_bytes
    d3_record_bytes = point_bytes + 3 * index_bytes
    retained = N2 * d2_record_bytes + N3 * d3_record_bytes
    lookup_traffic = N2 * (point_bytes + 2 * index_bytes)
    replay_traffic = N2 * (point_bytes + 5 * index_bytes)
    return {
        "N2": N2,
        "N3": N3,
        "candidate_additions": additions,
        "candidate_addition_upper_bound": B * B + B * N2,
        "index_bytes": index_bytes,
        "point_bytes": point_bytes,
        "d2_record_bytes": d2_record_bytes,
        "d3_record_bytes": d3_record_bytes,
        "retained_bytes": retained,
        "lookup_traffic_bytes": lookup_traffic,
        "replay_traffic_bytes": replay_traffic,
        "usable_automorphism_quotient": 2,
        "rho_total_group_work_formula": "C_rho*sqrt(q/2)",
    }


def public_source_record(table: dict[str, Any]) -> dict[str, Any]:
    return {
        "tuple_count": table["tuple_count"],
        "rcb_calls": table["rcb_calls"],
        "affine_replay_additions": table["affine_replay_additions"],
        "output_digest": table["output_digest"],
        "invalid_projective_count": table["invalid_projective_count"],
        "affine_replay_mismatches": table["affine_replay_mismatches"],
    }


def rank_job_key(record: dict[str, Any]) -> tuple[str, int | None, int, str]:
    return (
        str(record.get("tensor")),
        record.get("exponent"),
        exact_int(record.get("cut"), "rank.cut", 1),
        str(record.get("field")),
    )


def sum_rank_accounting(
    controls: Sequence[dict[str, Any]], instances: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for control in controls:
        records.extend(control["ranks"])
    for instance in instances:
        for registry in instance["registries"]:
            for cell in registry["cells"]:
                records.extend(cell["ranks"])
    by_field: dict[str, dict[str, int]] = {
        "F_p": {"jobs": 0, "P": 0, "E": 0, "N": 0, "upper_traffic": 0, "observed_traffic": 0, "base_word_equivalents": 0},
        "F_p2": {"jobs": 0, "P": 0, "E": 0, "N": 0, "upper_traffic": 0, "observed_traffic": 0, "base_word_equivalents": 0},
    }
    for record in records:
        field = record["field"]
        accounting = record["accounting"]
        row = by_field[field]
        row["jobs"] += 1
        row["P"] += accounting["upper"]["P"]
        row["E"] += accounting["upper"]["E"]
        row["N"] += accounting["upper"]["N"]
        row["upper_traffic"] += accounting["upper"]["traffic"]
        row["observed_traffic"] += accounting["traffic"]["total_field_words"]
        row["base_word_equivalents"] += accounting["traffic"]["base_word_equivalents"]
    return {
        "job_count": len(records),
        "by_field": by_field,
        "observed_base_word_equivalents": sum(
            row["base_word_equivalents"] for row in by_field.values()
        ),
        "upper_base_word_equivalents": by_field["F_p"]["upper_traffic"]
        + 2 * by_field["F_p2"]["upper_traffic"],
    }


def recompute_baseline(
    manifest_record: dict[str, Any],
    matrix_record: dict[str, Any],
    mutation_record: dict[str, Any],
    *,
    development_curve_ids: set[str] | None = None,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    audited_instances = audit_manifest(manifest_record)
    matrix_audit = audit_execution_matrix(matrix_record)
    mutation_audit = audit_mutation_manifest(mutation_record)
    instances_source = manifest_record["manifest"]["instances"]
    audit_by_id = {row["curve_id"]: row for row in audited_instances}
    control_rows = control_tensors()
    instance_rows: list[dict[str, Any]] = []
    source_tuple_count = 0
    rcb_calls = 0
    residual_cells = 0
    power_squarings = 0
    cohort_span_jobs = 0
    comparator_jobs = 0

    for instance in instances_source:
        curve_id = instance["curve_id"]
        if development_curve_ids is not None and curve_id not in development_curve_ids:
            continue
        p = instance["field"]["p"]
        B = instance["factor_base_size_B"]
        nu = instance["quadratic_extension"]["nu"]
        registry_rows: list[dict[str, Any]] = []
        random_q00_h: list[int] | None = None
        for family in (
            "random_unique",
            "x_interval",
            "consecutive_scalar_control",
        ):
            table = source_table(instance, family, rescaled=False)
            source_tuple_count += table["tuple_count"]
            rcb_calls += table["rcb_calls"]
            if family in {"random_unique", "x_interval"}:
                target_names = ["Q00", "Q01", "Q02"]
            else:
                target_names = ["Q00"]
            if family == "random_unique":
                target_names += ["IDENTITY", "PLANTED"]
            cells: list[dict[str, Any]] = []
            primary_h: list[list[int]] = []
            for target_name in target_names:
                cell, g_values, h_values, power_values = evaluate_cell(
                    instance,
                    table,
                    family,
                    target_name,
                    rescaled=False,
                )
                residual_cells += table["tuple_count"]
                if family == "random_unique" and target_name == "Q00":
                    random_q00_h = h_values
                    power_squarings += 3 * table["tuple_count"]
                if target_name in {"Q00", "Q01", "Q02"} and family in {
                    "random_unique",
                    "x_interval",
                }:
                    primary_h.append(h_values)
                attach_rank_schedule(
                    cell,
                    g_values,
                    h_values,
                    power_values,
                    family=family,
                    target_name=target_name,
                    rescaled=False,
                    B=B,
                    p=p,
                    nu=nu,
                )
                cells.append(cell)
            cohort_span: int | None = None
            if family in {"random_unique", "x_interval"}:
                cohort_span = rank_vector_family(primary_h, p)
                cohort_span_jobs += 1
            comparator = comparator_record(instance, family)
            comparator_jobs += 1
            registry_rows.append(
                {
                    "name": family,
                    "source": public_source_record(table),
                    "comparator": comparator,
                    "tested_cohort_span_dimension": cohort_span,
                    "cells": cells,
                }
            )

        if random_q00_h is None:
            raise AssertionError(f"{curve_id}: random Q00 was not evaluated")
        rescaled_table = source_table(instance, "random_unique", rescaled=True)
        source_tuple_count += rescaled_table["tuple_count"]
        rcb_calls += rescaled_table["rcb_calls"]
        rescaled_cell, g_values, h_values, power_values = evaluate_cell(
            instance,
            rescaled_table,
            "random_unique",
            "Q00",
            rescaled=True,
            unscaled_h=random_q00_h,
        )
        residual_cells += rescaled_table["tuple_count"]
        attach_rank_schedule(
            rescaled_cell,
            g_values,
            h_values,
            power_values,
            family="random_unique",
            target_name="Q00",
            rescaled=True,
            B=B,
            p=p,
            nu=nu,
        )
        random_row = next(row for row in registry_rows if row["name"] == "random_unique")
        random_row["rescaled_source"] = public_source_record(rescaled_table)
        random_row["cells"].append(rescaled_cell)
        instance_rows.append(
            {
                **audit_by_id[curve_id],
                "registries": registry_rows,
            }
        )

    rank_accounting = sum_rank_accounting(control_rows, instance_rows)
    semantic_cell_count = sum(
        len(registry["cells"])
        for instance in instance_rows
        for registry in instance["registries"]
    )
    full_schedule = development_curve_ids is None
    observed = {
        "source_tables": 4 * len(instance_rows),
        "semantic_cells": semantic_cell_count,
        "source_tuple_evaluations": source_tuple_count,
        "rcb_calls": rcb_calls,
        "residual_norm_evaluations": residual_cells,
        "power_squarings": power_squarings,
        "rank_jobs": rank_accounting["job_count"],
        "cohort_span_jobs": cohort_span_jobs,
        "d2_d3_comparator_jobs": comparator_jobs,
    }
    if full_schedule:
        expected = matrix_audit["mandatory_job_counts"]
        required = {
            "source_tables": expected["source_tables"],
            "semantic_cells": expected["semantic_cells"],
            "rank_jobs": expected["total_rank_jobs_per_path"],
            "cohort_span_jobs": expected["cohort_span_jobs_per_path"],
            "d2_d3_comparator_jobs": expected["d2_d3_comparator_jobs_per_path"],
            "source_tuple_evaluations": 615868,
            "rcb_calls": 2463472,
            "residual_norm_evaluations": 1539670,
            "power_squarings": 461901,
        }
        if any(observed.get(key) != value for key, value in required.items()):
            raise AssertionError(f"observed schedule mismatch: {observed} != {required}")
        expected_traffic = matrix_audit["aggregate_counts"]
        by_field = rank_accounting["by_field"]
        if by_field["F_p"]["N"] != expected_traffic["fp_rank_multiplication_upper_bound_including_controls"]:
            raise AssertionError("F_p rank multiplication aggregate mismatch")
        if by_field["F_p"]["E"] != expected_traffic["fp_rank_elimination_subtraction_upper_bound_including_controls"]:
            raise AssertionError("F_p rank elimination aggregate mismatch")
        if by_field["F_p2"]["N"] != expected_traffic["fp2_rank_multiplication_upper_bound"]:
            raise AssertionError("F_p2 rank multiplication aggregate mismatch")
        if rank_accounting["upper_base_word_equivalents"] != 587622372:
            raise AssertionError("v3 aggregate rank traffic ceiling mismatch")
    elapsed = time.perf_counter_ns() - started
    return {
        "controls": control_rows,
        "instances": instance_rows,
        "accounting": {
            "frozen_expected": matrix_audit["aggregate_counts"],
            "observed": observed,
            "rank": rank_accounting,
            "wall_time_ns": elapsed,
            "peak_rss": rss_record(),
        },
        "summary": {
            "manifest_instances": len(instance_rows),
            "mutation_count": mutation_audit["mutation_count"],
            "control_count": len(control_rows),
            "semantic_cell_count": semantic_cell_count,
            "rank_job_count": rank_accounting["job_count"],
            "cohort_span_job_count": cohort_span_jobs,
            "comparator_job_count": comparator_jobs,
            "semantic_mismatches": 0,
            "hilbert_violations": 0,
            "full_schedule": full_schedule,
        },
    }


def object_map(rows: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise AssertionError(f"{label} must be a list")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AssertionError(f"{label}[{index}] must be an object")
        identifier = str(row.get(key))
        if identifier in result:
            raise AssertionError(f"{label} has duplicate {key}={identifier}")
        result[identifier] = row
    return result


def require_fields_equal(
    raw: dict[str, Any], expected: dict[str, Any], fields: Sequence[str], label: str
) -> None:
    for field in fields:
        if raw.get(field) != expected.get(field):
            raise AssertionError(
                f"{label}.{field} mismatch: {raw.get(field)!r} != {expected.get(field)!r}"
            )


def validate_hex_digest(value: Any, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise AssertionError(f"{label} must be a SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as error:
        raise AssertionError(f"{label} is not hexadecimal") from error


def compare_rank_records(
    raw_rows: Any, expected_rows: Sequence[dict[str, Any]], label: str
) -> None:
    raw_map = {rank_job_key(row): row for row in object_map_with_rank_keys(raw_rows, label)}
    expected_map = {rank_job_key(row): row for row in expected_rows}
    if set(raw_map) != set(expected_map):
        raise AssertionError(f"{label}: rank job key mismatch")
    for key, expected in expected_map.items():
        raw = raw_map[key]
        require_fields_equal(
            raw,
            expected,
            ("tensor", "exponent", "cut", "field", "rank_kind", "rank", "hilbert_cap"),
            f"{label}.{key}",
        )
        validate_hex_digest(raw.get("certificate_digest"), f"{label}.{key}.certificate")
        accounting = raw.get("accounting")
        if not isinstance(accounting, dict):
            accounting = {}
        traffic = accounting.get("traffic", raw.get("traffic"))
        if not isinstance(traffic, dict):
            raise AssertionError(f"{label}.{key}: traffic phases missing")
        for phase in (
            "materialization",
            "pivot_scan",
            "elimination_update",
            "normalization",
            "certificate",
        ):
            exact_int(traffic.get(phase), f"{label}.{key}.traffic.{phase}", 0)
        total = sum(traffic[phase] for phase in (
            "materialization",
            "pivot_scan",
            "elimination_update",
            "normalization",
            "certificate",
        ))
        declared_total = traffic.get("total_field_words", traffic.get("total"))
        if declared_total != total:
            raise AssertionError(f"{label}.{key}: rank traffic total mismatch")
        upper = expected["accounting"]["upper"]["traffic"]
        if total > upper:
            raise AssertionError(f"{label}.{key}: traffic exceeds frozen ceiling")
        base_words = traffic.get(
            "base_word_equivalents", total * (2 if raw["field"] == "F_p2" else 1)
        )
        if base_words != total * (2 if raw["field"] == "F_p2" else 1):
            raise AssertionError(f"{label}.{key}: extension traffic conversion mismatch")


def object_map_with_rank_keys(rows: Any, label: str) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        raise AssertionError(f"{label} must be a list")
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, int | None, int, str]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise AssertionError(f"{label}[{index}] must be an object")
        key = rank_job_key(row)
        if key in seen:
            raise AssertionError(f"{label}: duplicate rank job {key}")
        seen.add(key)
        result.append(row)
    return result


def compare_baseline(raw: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    raw_controls = object_map(raw.get("controls"), "id", "raw.controls")
    expected_controls = object_map(expected["controls"], "id", "expected.controls")
    if set(raw_controls) != set(expected_controls):
        raise AssertionError("control ID mismatch")
    for control_id, control in expected_controls.items():
        candidate = raw_controls[control_id]
        require_fields_equal(
            candidate, control, ("B", "field", "cut_ranks", "digest"), f"control.{control_id}"
        )
        compare_rank_records(candidate.get("ranks"), control["ranks"], f"control.{control_id}.ranks")

    raw_instances = object_map(raw.get("instances"), "curve_id", "raw.instances")
    expected_instances = object_map(expected["instances"], "curve_id", "expected.instances")
    if set(raw_instances) != set(expected_instances):
        raise AssertionError("curve instance ID mismatch")
    verified_cells = 0
    verified_ranks = 24
    for curve_id, expected_instance in expected_instances.items():
        candidate_instance = raw_instances[curve_id]
        require_fields_equal(
            candidate_instance,
            expected_instance,
            ("B", "p", "q"),
            f"instance.{curve_id}",
        )
        candidate_curve = candidate_instance.get("curve")
        candidate_extension = candidate_instance.get("extension")
        if not isinstance(candidate_curve, dict) or not isinstance(candidate_extension, dict):
            raise AssertionError(f"{curve_id}: curve or extension summary missing")
        for key in ("a", "b", "j_invariant"):
            if candidate_curve.get(key) != expected_instance[key]:
                raise AssertionError(f"{curve_id}: curve field {key} mismatch")
        if candidate_extension.get("nu") != expected_instance["nu"]:
            raise AssertionError(f"{curve_id}: extension nonresidue mismatch")
        raw_registries = object_map(
            candidate_instance.get("registries"), "name", f"{curve_id}.registries"
        )
        expected_registries = object_map(
            expected_instance["registries"], "name", f"expected.{curve_id}.registries"
        )
        if set(raw_registries) != set(expected_registries):
            raise AssertionError(f"{curve_id}: registry family mismatch")
        for family, expected_registry in expected_registries.items():
            candidate_registry = raw_registries[family]
            require_fields_equal(
                candidate_registry["source"],
                expected_registry["source"],
                (
                    "tuple_count",
                    "rcb_calls",
                    "output_digest",
                    "invalid_projective_count",
                    "affine_replay_mismatches",
                ),
                f"{curve_id}.{family}.source",
            )
            require_fields_equal(
                candidate_registry["comparator"],
                expected_registry["comparator"],
                (
                    "N2",
                    "N3",
                    "candidate_additions",
                    "candidate_addition_upper_bound",
                    "index_bytes",
                    "point_bytes",
                    "d2_record_bytes",
                    "d3_record_bytes",
                    "retained_bytes",
                    "lookup_traffic_bytes",
                    "replay_traffic_bytes",
                    "usable_automorphism_quotient",
                ),
                f"{curve_id}.{family}.comparator",
            )
            if candidate_registry.get("tested_cohort_span_dimension") != expected_registry.get(
                "tested_cohort_span_dimension"
            ):
                raise AssertionError(f"{curve_id}.{family}: tested cohort span mismatch")
            if "target_family_span_dimension" in candidate_registry:
                raise AssertionError("sampled cohort may not be labeled a target-family span")
            if "rescaled_source" in expected_registry:
                require_fields_equal(
                    candidate_registry.get("source", {}).get("rescaled", {}),
                    expected_registry["rescaled_source"],
                    (
                        "tuple_count",
                        "rcb_calls",
                        "output_digest",
                        "invalid_projective_count",
                        "affine_replay_mismatches",
                    ),
                    f"{curve_id}.{family}.rescaled_source",
                )
            raw_cells = object_map(
                candidate_registry.get("cells"), "cell_id", f"{curve_id}.{family}.cells"
            )
            expected_cells = object_map(
                expected_registry["cells"], "cell_id", f"expected.{curve_id}.{family}.cells"
            )
            if set(raw_cells) != set(expected_cells):
                raise AssertionError(f"{curve_id}.{family}: semantic cell mismatch")
            for cell_id, expected_cell in expected_cells.items():
                candidate_cell = raw_cells[cell_id]
                require_fields_equal(
                    candidate_cell,
                    expected_cell,
                    ("target_id", "target_name", "rescaled"),
                    cell_id,
                )
                require_fields_equal(
                    candidate_cell["semantic"],
                    expected_cell["semantic"],
                    (
                        "tuple_count",
                        "g_digest",
                        "h_digest",
                        "power_digests",
                        "norm_mismatches",
                        "source_span_mismatches",
                        "zero_set_mismatches",
                        "rescaling_mismatches",
                        "witness_count",
                        "g_value_count",
                        "h_value_count",
                    ),
                    f"{cell_id}.semantic",
                )
                candidate_semantic = candidate_cell["semantic"]
                if candidate_semantic.get("non_base_field_count", 0) != 0:
                    raise AssertionError(f"{cell_id}: h left the base field")
                if candidate_semantic.get("no_hit_count") != (
                    expected_cell["semantic"]["tuple_count"]
                    - expected_cell["semantic"]["witness_count"]
                ):
                    raise AssertionError(f"{cell_id}: no-hit count mismatch")
                raw_samples = candidate_semantic.get("samples")
                expected_samples = expected_cell["semantic"]["samples"]
                if not isinstance(raw_samples, list) or len(raw_samples) != len(expected_samples):
                    raise AssertionError(f"{cell_id}: deterministic sample count mismatch")
                for raw_sample, expected_sample in zip(raw_samples, expected_samples):
                    if not isinstance(raw_sample, dict):
                        raise AssertionError(f"{cell_id}: malformed deterministic sample")
                    if raw_sample.get("linear_index") != expected_sample["linear_index"]:
                        raise AssertionError(f"{cell_id}: sample index mismatch")
                    if raw_sample.get("tuple_indices") != expected_sample["tuple"]:
                        raise AssertionError(f"{cell_id}: sample tuple mismatch")
                    for field in ("source", "g", "h"):
                        if raw_sample.get(field) != expected_sample[field]:
                            raise AssertionError(f"{cell_id}: sample {field} mismatch")
                compare_rank_records(
                    candidate_cell.get("ranks"), expected_cell["ranks"], f"{cell_id}.ranks"
                )
                verified_cells += 1
                verified_ranks += len(expected_cell["ranks"])

    raw_summary = raw.get("summary")
    if not isinstance(raw_summary, dict):
        raise AssertionError("baseline summary is missing")
    expected_control_rank_jobs = sum(
        len(control["ranks"]) for control in expected["controls"]
    )
    required_counts = {
        "source_tables": 24,
        "semantic_cells": expected["summary"]["semantic_cell_count"],
        "ec_rank_jobs": expected["summary"]["rank_job_count"]
        - expected_control_rank_jobs,
        "control_rank_jobs": expected_control_rank_jobs,
        "total_rank_jobs": expected["summary"]["rank_job_count"],
        "cohort_span_jobs": expected["summary"]["cohort_span_job_count"],
        "comparator_jobs": expected["summary"]["comparator_job_count"],
    }
    if raw_summary.get("mandatory_counts") != required_counts:
        raise AssertionError("mandatory summary count mismatch")
    mismatch_totals = raw_summary.get("mismatch_totals")
    if (
        raw_summary.get("mismatch_total") != 0
        or not isinstance(mismatch_totals, dict)
        or not mismatch_totals
        or any(value != 0 for value in mismatch_totals.values())
    ):
        raise AssertionError("producer reported a semantic or schedule mismatch")
    expected_schedule_checks = {
        "cohort_span_jobs",
        "comparator_additions",
        "comparator_jobs",
        "power_squarings",
        "rank_fp2_ceiling",
        "rank_fp_ceiling",
        "rank_jobs",
        "rank_traffic",
        "rcb_calls",
        "residual_norm_evaluations",
        "rss",
        "semantic_cells",
        "source_tables",
        "source_tuple_evaluations",
    }
    schedule_checks = raw_summary.get("schedule_checks")
    if (
        not isinstance(schedule_checks, dict)
        or set(schedule_checks) != expected_schedule_checks
        or any(value is not True for value in schedule_checks.values())
    ):
        raise AssertionError("frozen schedule check mismatch")
    expected_witnesses = sum(
        cell["semantic"]["witness_count"]
        for instance in expected["instances"]
        for registry in instance["registries"]
        for cell in registry["cells"]
    )
    expected_semantic_evaluations = sum(
        cell["semantic"]["tuple_count"]
        for instance in expected["instances"]
        for registry in instance["registries"]
        for cell in registry["cells"]
    )
    if raw_summary.get("witness_count") != expected_witnesses:
        raise AssertionError("aggregate witness count mismatch")
    if raw_summary.get("no_hit_count") != expected_semantic_evaluations - expected_witnesses:
        raise AssertionError("aggregate no-hit count mismatch")

    raw_accounting = raw.get("accounting")
    if not isinstance(raw_accounting, dict):
        raise AssertionError("baseline accounting is missing")
    for required_bucket in (
        "full_enumeration",
        "canonical_storage",
        "logical_traffic",
        "peak_rss",
    ):
        if not isinstance(raw_accounting.get(required_bucket), dict):
            raise AssertionError(f"accounting.{required_bucket} is missing")
    observed = raw_accounting.get("observed")
    if not isinstance(observed, dict):
        raise AssertionError("observed accounting is missing")
    full_enumeration = observed.get("full_enumeration")
    if not isinstance(full_enumeration, dict):
        raise AssertionError("full-enumeration accounting is missing")
    require_fields_equal(
        full_enumeration,
        {
            "source_tables": 24,
            "tuple_count": 615868,
            "rcb_calls": 2463472,
            "classification": "diagnostic_full_enumeration",
            "retained_as_advice": False,
        },
        (
            "source_tables",
            "tuple_count",
            "rcb_calls",
            "classification",
            "retained_as_advice",
        ),
        "accounting.observed.full_enumeration",
    )
    semantic_accounting = observed.get("semantic")
    if not isinstance(semantic_accounting, dict):
        raise AssertionError("semantic accounting is missing")
    require_fields_equal(
        semantic_accounting,
        {
            "cells": 60,
            "residual_norm_evaluations": 1539670,
            "power_squarings": 461901,
            "witness_count": expected_witnesses,
            "no_hit_count": expected_semantic_evaluations - expected_witnesses,
            "success_probability": "not_applicable",
        },
        (
            "cells",
            "residual_norm_evaluations",
            "power_squarings",
            "witness_count",
            "no_hit_count",
            "success_probability",
        ),
        "accounting.observed.semantic",
    )
    cohort_accounting = observed.get("cohort_span")
    comparator_accounting = observed.get("comparators")
    if not isinstance(cohort_accounting, dict) or cohort_accounting.get("jobs") != 12:
        raise AssertionError("cohort-span accounting mismatch")
    expected_candidate_additions = sum(
        registry["comparator"]["candidate_additions"]
        for instance in expected["instances"]
        for registry in instance["registries"]
    )
    if not isinstance(comparator_accounting, dict) or comparator_accounting != {
        "jobs": 18,
        "candidate_additions": expected_candidate_additions,
    }:
        raise AssertionError("comparator accounting mismatch")

    peak = raw_accounting.get("peak_rss")
    if not isinstance(peak, dict) or exact_int(peak.get("bytes"), "peak_rss.bytes", 0) > 2 * 1024**3:
        raise AssertionError("peak RSS record is missing or exceeds 2 GiB")
    raw_rank = observed.get("rank")
    if not isinstance(raw_rank, dict):
        raise AssertionError("aggregate rank accounting missing")
    rank_ceilings = {
        "F_p": {"P": 6183256, "E": 152824740, "N": 159007996, "T": 495573756},
        "F_p2": {"P": 615868, "E": 14109700, "N": 14725568, "T": 46024308},
    }
    rank_jobs = {"F_p": 264, "F_p2": 24}
    observed_words = 0
    for field, ceiling in rank_ceilings.items():
        field_record = raw_rank.get(field)
        if not isinstance(field_record, dict):
            raise AssertionError(f"aggregate {field} rank accounting missing")
        values = {
            key: exact_int(field_record.get(key), f"accounting.rank.{field}.{key}", 0)
            for key in ("P", "E", "N", "T")
        }
        if field_record.get("jobs") != rank_jobs[field]:
            raise AssertionError(f"aggregate {field} rank job count mismatch")
        if values["N"] < values["E"] or values["N"] > values["P"] + values["E"]:
            raise AssertionError(f"aggregate {field} observed multiplication bound mismatch")
        if field_record.get("ceiling") != ceiling:
            raise AssertionError(f"aggregate {field} frozen ceiling mismatch")
        if any(values[key] > ceiling[key] for key in values):
            raise AssertionError(f"aggregate {field} rank accounting exceeds its ceiling")
        traffic = field_record.get("traffic")
        if not isinstance(traffic, dict) or traffic.get("total") != values["T"]:
            raise AssertionError(f"aggregate {field} traffic phase total mismatch")
        phase_total = sum(
            exact_int(traffic.get(phase), f"accounting.rank.{field}.traffic.{phase}", 0)
            for phase in (
                "materialization",
                "pivot_scan",
                "elimination_update",
                "normalization",
                "certificate",
            )
        )
        if phase_total != values["T"]:
            raise AssertionError(f"aggregate {field} traffic phases do not sum")
        actual_normalizations = values["N"] - values["E"]
        if (
            traffic.get("materialization") != 2 * values["P"]
            or traffic.get("pivot_scan") > values["P"]
            or traffic.get("elimination_update") != 3 * values["E"]
            or traffic.get("normalization") != 2 * actual_normalizations
            or traffic.get("certificate") != actual_normalizations
        ):
            raise AssertionError(f"aggregate {field} observed traffic identity mismatch")
        multiplier = 2 if field == "F_p2" else 1
        if field_record.get("base_field_word_equivalents") != multiplier * values["T"]:
            raise AssertionError(f"aggregate {field} base-word conversion mismatch")
        observed_words += multiplier * values["T"]
    logical_rank = raw_accounting["logical_traffic"].get("rank")
    if (
        not isinstance(logical_rank, dict)
        or logical_rank.get("base_field_word_equivalents") != observed_words
    ):
        raise AssertionError("logical rank traffic aggregate mismatch")
    if observed_words > 587622372:
        raise AssertionError("observed rank traffic exceeds the v3 ceiling")
    return {
        "verified_instances": len(expected_instances),
        "verified_cells": verified_cells,
        "verified_rank_jobs": verified_ranks,
        "verified_controls": len(expected_controls),
        "observed_rank_traffic_base_word_equivalents": observed_words,
    }


def enforce_firewall(raw: dict[str, Any], mode: str) -> None:
    if raw.get("protocol") != PROTOCOL:
        raise AssertionError("protocol label mismatch")
    if raw.get("mode") != mode:
        raise AssertionError("raw-result mode mismatch")
    if exact_bool(raw.get("valid"), "raw.valid") is not True:
        raise AssertionError("producer did not mark the result valid")
    if raw.get("interpretation") != INTERPRETATION:
        raise AssertionError("interpretation firewall mismatch")
    if exact_bool(raw.get("breakthrough_claim"), "breakthrough_claim") is not False:
        raise AssertionError("breakthrough claim is forbidden")
    if exact_bool(raw.get("compiler_constructed"), "compiler_constructed") is not False:
        raise AssertionError("compiler construction claim is forbidden")
    if raw.get("success_probability") != "not_applicable":
        raise AssertionError("deterministic semantic run has no success probability")


def verify_provenance(
    raw: dict[str, Any], manifest: Path, matrix: Path, mutations: Path
) -> dict[str, str]:
    expected = {
        "manifest_sha256": sha256_file(manifest),
        "execution_matrix_sha256": sha256_file(matrix),
        "mutation_manifest_sha256": sha256_file(mutations),
    }
    provenance = raw.get("provenance")
    if not isinstance(provenance, dict):
        raise AssertionError("producer provenance is missing")
    for key, digest in expected.items():
        if provenance.get(key) != digest:
            raise AssertionError(f"producer provenance mismatch for {key}")
    validate_hex_digest(provenance.get("generator_sha256"), "generator_sha256")
    local_generator_sha256 = sha256_file(GENERATOR_PATH)
    if provenance["generator_sha256"] != local_generator_sha256:
        raise AssertionError("producer source hash differs from the local frozen generator")
    expected["generator_sha256"] = local_generator_sha256
    expected["verifier_sha256"] = sha256_file(SCRIPT_PATH)
    return expected


def verifier_independence_audit() -> dict[str, Any]:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"), filename=str(SCRIPT_PATH))
    forbidden: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            forbidden.extend(alias.name for alias in node.names if "generate_tt_norm_rank" in alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "generate_tt_norm_rank" in module:
                forbidden.append(module)
    loaded = [
        str(getattr(module, "__file__", ""))
        for module in sys.modules.values()
        if "generate_tt_norm_rank" in str(getattr(module, "__file__", ""))
    ]
    if forbidden or loaded:
        raise AssertionError("verifier imported producer implementation")
    return {"generator_imports": forbidden, "generator_modules_loaded": loaded, "valid": True}


def baseline_cell(expected: dict[str, Any], cell_id: str) -> dict[str, Any]:
    for instance in expected["instances"]:
        for registry in instance["registries"]:
            for cell in registry["cells"]:
                if cell["cell_id"] == cell_id:
                    return cell
    raise AssertionError(f"expected cell not found: {cell_id}")


def baseline_registry(expected: dict[str, Any], curve_id: str, family: str) -> dict[str, Any]:
    instance = next(row for row in expected["instances"] if row["curve_id"] == curve_id)
    return next(row for row in instance["registries"] if row["name"] == family)


def detect_mutation(
    mutation_id: str,
    payload: dict[str, Any],
    expected_c08: dict[str, Any],
    manifest_record: dict[str, Any],
) -> tuple[bool, str]:
    expected_registry = baseline_registry(expected_c08, "C08", "random_unique")
    expected_cell = baseline_cell(expected_c08, "C08:random_unique:Q00")
    if mutation_id in {"M01-WRONG-B3", "M02-FLIP-GATE37", "M03-AFFINE-PRODUCER"}:
        source = payload.get("source")
        semantic = payload.get("semantic")
        if not isinstance(source, dict) or not isinstance(semantic, dict):
            return False, "mutated source and semantic digests are required"
        source_changed = source.get("output_digest") != expected_registry["source"]["output_digest"]
        value_changed = (
            semantic.get("g_digest") != expected_cell["semantic"]["g_digest"]
            or semantic.get("h_digest") != expected_cell["semantic"]["h_digest"]
        )
        return source_changed and value_changed, "independent RCB/value digest mismatch"
    if mutation_id == "M04-ZERO-PROJECTIVE":
        source = payload.get("source")
        if not isinstance(source, dict):
            return False, "mutated source payload is missing"
        return (
            source.get("invalid_projective_count") == 1
            and source.get("first_output") == [0, 0, 0]
        ), "nonzero projective validity gate"
    if mutation_id in {"M05-WRONG-FROBENIUS", "M06-G-SQUARED"}:
        semantic = payload.get("semantic")
        if not isinstance(semantic, dict):
            return False, "mutated semantic payload is missing"
        mismatch = exact_int(
            semantic.get("norm_mismatches", 0), f"{mutation_id}.norm_mismatches", 0
        )
        digest_changed = semantic.get("h_digest") != expected_cell["semantic"]["h_digest"]
        return mismatch > 0 and digest_changed, "product-versus-quadratic norm mismatch"
    if mutation_id == "M07-RANK-FIELD-PROVENANCE":
        rank = payload.get("rank_record")
        return isinstance(rank, dict) and rank.get("tensor") == "h" and rank.get("field") == "F_p2", "static rank-field provenance gate"
    if mutation_id == "M08-RAW-BOND-AS-RANK":
        rank = payload.get("rank_record")
        return isinstance(rank, dict) and rank.get("rank_kind") == "raw_hadamard_product", "rank-kind provenance gate"
    if mutation_id == "M09-REVERSE-CUTS":
        return (
            payload.get("control_id") == "CTRL-ASYMMETRIC"
            and payload.get("reported_cut_ranks") == [4, 3, 2, 1]
        ), "asymmetric cut profile"
    if mutation_id == "M10-POSTSELECT-TARGET":
        target = payload.get("candidate")
        if not isinstance(target, dict):
            return False, "postselected target payload is missing"
        frozen = manifest_record["manifest"]["instances"][0]["primary_targets"][0]
        frozen_source = frozen["source"]
        differs = (
            target.get("target_id") != frozen["point_id"]
            or target.get("label") != frozen_source["label"]
            or target.get("scalar") != frozen_source["scalar"]
        )
        selection_is_post_observation = (
            payload.get("selection") == "post_observation_minimum_rank"
            and payload.get("frozen_q00_target_id") == frozen["point_id"]
        )
        return differs and selection_is_post_observation, "target manifest and selection firewall"
    if mutation_id == "M11-DUPLICATE-PRIMARY":
        if payload.get("curve_id") != "C08" or payload.get("registry") != "random_unique":
            return False, "duplicate registry provenance is missing"
        identifiers = payload.get("point_ids")
        affine = payload.get("affine")
        if not isinstance(identifiers, list) or not isinstance(affine, list):
            return False, "duplicate registry lists are missing"
        duplicate = len(identifiers) != len(set(identifiers)) or len(affine) != len(
            {tuple(point) for point in affine}
        )
        return duplicate, "primary identifier and affine uniqueness gates"
    if mutation_id == "M12-SHARED-VERIFIER-CODE":
        imports = payload.get("imports")
        if not isinstance(imports, list):
            return False, "import list is missing"
        return any("generate_tt_norm_rank" in str(item) for item in imports), "AST import provenance gate"
    if mutation_id == "M13-OMIT-ENUMERATION-COST":
        accounting = payload.get("accounting")
        return isinstance(accounting, dict) and "full_enumeration" not in accounting, "required full-enumeration accounting key"
    if mutation_id == "M14-OMIT-MEMORY":
        accounting = payload.get("accounting")
        required = {"canonical_storage", "logical_traffic", "peak_rss"}
        return isinstance(accounting, dict) and not required.issubset(accounting), "required memory and traffic accounting keys"
    if mutation_id == "M15-ASYMPTOTIC-LABEL":
        return (
            payload.get("interpretation") == "ASYMPTOTIC"
            and payload.get("breakthrough_claim") is True
        ), "interpretation firewall"
    raise AssertionError(f"unrecognized mutation ID: {mutation_id}")


def verify_mutations(
    raw: dict[str, Any],
    manifest_record: dict[str, Any],
    matrix_record: dict[str, Any],
    mutation_record: dict[str, Any],
) -> dict[str, Any]:
    expected_c08 = recompute_baseline(
        manifest_record,
        matrix_record,
        mutation_record,
        development_curve_ids={"C08"},
    )
    frozen_rows = mutation_record["mutation_manifest"]["mutations"]
    frozen_ids = [row["id"] for row in frozen_rows]
    raw_rows = object_map(raw.get("mutation_artifacts"), "id", "mutation_artifacts")
    if set(raw_rows) != set(frozen_ids):
        raise AssertionError("mutation artifact IDs differ from the frozen manifest")
    detections: list[dict[str, Any]] = []
    for frozen in frozen_rows:
        mutation_id = frozen["id"]
        row = raw_rows[mutation_id]
        if row.get("classification") != frozen["classification"]:
            raise AssertionError(f"{mutation_id}: classification mismatch")
        if row.get("expected") != "rejected":
            raise AssertionError(f"{mutation_id}: expected outcome mismatch")
        payload = row.get("artifact")
        if not isinstance(payload, dict):
            raise AssertionError(f"{mutation_id}: artifact payload missing")
        detected, reason = detect_mutation(
            mutation_id, payload, expected_c08, manifest_record
        )
        if not detected:
            raise AssertionError(f"{mutation_id}: mutation survived its detector")
        detections.append(
            {
                "id": mutation_id,
                "classification": frozen["classification"],
                "detected": True,
                "reason": reason,
            }
        )
    summary = raw.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("mutation summary is missing")
    if summary.get("attempted") != 15:
        raise AssertionError("mutation attempted count mismatch")
    return {
        "attempted": 15,
        "detected": 15,
        "survived": 0,
        "detections": detections,
        "c08_replay_digest": stable_digest(expected_c08),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("baseline", "mutations"), required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--execution-matrix", type=Path, required=True)
    parser.add_argument("--mutation-manifest", type=Path, required=True)
    parser.add_argument("--raw-result", type=Path, required=True)
    return parser.parse_args(argv)


def verify(args: argparse.Namespace) -> dict[str, Any]:
    started = time.perf_counter_ns()
    manifest_record = read_json(args.manifest)
    matrix_record = read_json(args.execution_matrix)
    mutation_record = read_json(args.mutation_manifest)
    raw = read_json(args.raw_result)
    enforce_firewall(raw, args.mode)
    provenance = verify_provenance(
        raw, args.manifest, args.execution_matrix, args.mutation_manifest
    )
    independence = verifier_independence_audit()
    if args.mode == "baseline":
        replay = recompute_baseline(manifest_record, matrix_record, mutation_record)
        comparison = compare_baseline(raw, replay)
        independent_summary = replay["summary"]
        replay_digest = stable_digest(replay)
        mutation_summary = None
    else:
        comparison = verify_mutations(
            raw, manifest_record, matrix_record, mutation_record
        )
        independent_summary = {
            "mutation_count": comparison["attempted"],
            "detected": comparison["detected"],
            "survived": comparison["survived"],
        }
        replay_digest = comparison["c08_replay_digest"]
        mutation_summary = comparison["detections"]
    elapsed = time.perf_counter_ns() - started
    return {
        "protocol": PROTOCOL,
        "mode": f"{args.mode}_verification",
        "valid": True,
        "interpretation": INTERPRETATION,
        "breakthrough_claim": False,
        "compiler_constructed": False,
        "success_probability": "not_applicable",
        "provenance": {
            **provenance,
            "raw_result_sha256": sha256_file(args.raw_result),
        },
        "independence": independence,
        "comparison": comparison,
        "independent_summary": independent_summary,
        "independent_replay_digest": replay_digest,
        "mutation_detections": mutation_summary,
        "accounting": {
            "wall_time_ns": elapsed,
            "peak_rss": rss_record(),
            "verifier_replay_charged": True,
        },
        "boundary": (
            "Independent toy semantic replay only. No compiler, locator, relation, "
            "asymptotic, or ECDLP improvement is established."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = verify(args)
    print(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
