#!/usr/bin/env python3
"""Producer for the frozen TT first-norm rank diagnostic."""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence


SCRIPT_PATH = Path(__file__).resolve()
PROTOCOL = "EXP-ECDLP-TT-NORM-RANK-001-development-v3"
PROTOCOL_COMMIT = "ec0b9e075b1dfa77bca453fd452e56cfb514b7e4"
EXPERIMENT_ID = "EXP-ECDLP-TT-NORM-RANK-001"
INTERPRETATION = "SANITY_ONLY"
HARD_RSS_LIMIT = 2 * 1024**3
Point = tuple[int, int] | None
Projective = tuple[int, int, int]
Fp2 = tuple[int, int]

GATE_TEXT = [
    "01:t0=X1*X2",
    "02:t1=Y1*Y2",
    "03:t2=Z1*Z2",
    "04:t3=X1+Y1",
    "05:t4=X2+Y2",
    "06:t3=t3*t4",
    "07:t4=t0+t1",
    "08:t3=t3-t4",
    "09:t4=X1+Z1",
    "10:t5=X2+Z2",
    "11:t4=t4*t5",
    "12:t5=t0+t2",
    "13:t4=t4-t5",
    "14:t5=Y1+Z1",
    "15:X3=Y2+Z2",
    "16:t5=t5*X3",
    "17:X3=t1+t2",
    "18:t5=t5-X3",
    "19:Z3=a*t4",
    "20:X3=b3*t2",
    "21:Z3=X3+Z3",
    "22:X3=t1-Z3",
    "23:Z3=t1+Z3",
    "24:Y3=X3*Z3",
    "25:t1=t0+t0",
    "26:t1=t1+t0",
    "27:t2=a*t2",
    "28:t4=b3*t4",
    "29:t1=t1+t2",
    "30:t2=t0-t2",
    "31:t2=a*t2",
    "32:t4=t4+t2",
    "33:t0=t1*t4",
    "34:Y3=Y3+t0",
    "35:t0=t5*t4",
    "36:X3=t3*X3",
    "37:X3=X3-t0",
    "38:t0=t3*t1",
    "39:Z3=t5*Z3",
    "40:Z3=Z3+t0",
]
CURVE_IDS = ["C08", "C10", "C12", "C14", "C15", "C17"]
REGISTRY_NAMES = ["random_unique", "x_interval", "consecutive_scalar_control"]
MUTATION_IDS = [
    "M01-WRONG-B3",
    "M02-FLIP-GATE37",
    "M03-AFFINE-PRODUCER",
    "M04-ZERO-PROJECTIVE",
    "M05-WRONG-FROBENIUS",
    "M06-G-SQUARED",
    "M07-RANK-FIELD-PROVENANCE",
    "M08-RAW-BOND-AS-RANK",
    "M09-REVERSE-CUTS",
    "M10-POSTSELECT-TARGET",
    "M11-DUPLICATE-PRIMARY",
    "M12-SHARED-VERIFIER-CODE",
    "M13-OMIT-ENUMERATION-COST",
    "M14-OMIT-MEMORY",
    "M15-ASYMPTOTIC-LABEL",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise AssertionError(f"{path}: top-level JSON must be an object")
    return value


def stable_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def width_for(p: int) -> int:
    return max(1, (p.bit_length() + 7) // 8)


def digest_fp(values: Iterable[int], p: int) -> str:
    width = width_for(p)
    digest = hashlib.sha256()
    for value in values:
        digest.update((value % p).to_bytes(width, "big"))
    return digest.hexdigest()


def digest_fp2(values: Iterable[Fp2], p: int) -> str:
    width = width_for(p)
    digest = hashlib.sha256()
    for real, omega in values:
        digest.update((real % p).to_bytes(width, "big"))
        digest.update((omega % p).to_bytes(width, "big"))
    return digest.hexdigest()


def digest_projective(values: Iterable[Projective], p: int) -> str:
    width = width_for(p)
    digest = hashlib.sha256()
    for point in values:
        for coordinate in point:
            digest.update((coordinate % p).to_bytes(width, "big"))
    return digest.hexdigest()


def tuple_from_linear(linear_index: int, B: int) -> tuple[int, int, int, int, int]:
    digits = [0, 0, 0, 0, 0]
    value = linear_index
    for position in range(4, -1, -1):
        digits[position] = value % B
        value //= B
    if value:
        raise AssertionError("linear tuple index is out of range")
    return tuple(digits)  # type: ignore[return-value]


def sample_indices(length: int) -> list[int]:
    if length <= 0:
        return []
    return sorted({0, length // 2, length - 1})


def sha256_scalar(label: str, modulus: int) -> int:
    raw = int.from_bytes(hashlib.sha256(label.encode("ascii")).digest(), "big")
    return 1 + raw % (modulus - 1)


def rescale_factor(label: str, p: int) -> int:
    return sha256_scalar(label, p)


def projective_rescale(point: Projective, factor: int, p: int) -> Projective:
    return tuple(factor * value % p for value in point)  # type: ignore[return-value]


def fp2_mul(left: Fp2, right: Fp2, p: int, nu: int) -> Fp2:
    u1, v1 = left
    u2, v2 = right
    return (
        (u1 * u2 + nu * v1 * v2) % p,
        (u1 * v2 + v1 * u2) % p,
    )


def fp2_sub(left: Fp2, right: Fp2, p: int) -> Fp2:
    return (left[0] - right[0]) % p, (left[1] - right[1]) % p


def fp2_inv(value: Fp2, p: int, nu: int) -> Fp2:
    u, v = value
    denominator = (u * u - nu * v * v) % p
    if denominator == 0:
        raise ZeroDivisionError("zero Fp2 element")
    inverse = pow(denominator, -1, p)
    return u * inverse % p, -v * inverse % p


def fp2_zero(value: Fp2) -> bool:
    return value[0] == 0 and value[1] == 0


def projective_on_curve(point: Projective, p: int, a: int, b: int) -> bool:
    x, y, z = point
    if x % p == 0 and y % p == 0 and z % p == 0:
        return False
    return (y * y * z - x * x * x - a * x * z * z - b * z * z * z) % p == 0


def projective_to_affine(point: Projective, p: int) -> Point:
    x, y, z = (coordinate % p for coordinate in point)
    if z == 0:
        return None
    inverse = pow(z, -1, p)
    return x * inverse % p, y * inverse % p


def affine_to_projective(point: Point) -> Projective:
    return (0, 1, 0) if point is None else (point[0], point[1], 1)


def empty_field_ops() -> dict[str, int]:
    return {
        "additions": 0,
        "subtractions": 0,
        "multiplications": 0,
        "squarings": 0,
        "inversions": 0,
        "conjugations": 0,
        "comparisons": 0,
        "reductions": 0,
    }


def add_ops(target: dict[str, int], **increments: int) -> None:
    for key, value in increments.items():
        target[key] = target.get(key, 0) + value


def merge_ops(target: dict[str, int], source: dict[str, int]) -> None:
    for key, value in source.items():
        target[key] = target.get(key, 0) + value


def affine_add(
    left: Point,
    right: Point,
    p: int,
    a: int,
    operations: dict[str, int] | None = None,
) -> Point:
    if operations is not None:
        operations["comparisons"] += 1
    if left is None:
        return right
    if operations is not None:
        operations["comparisons"] += 1
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if operations is not None:
        operations["comparisons"] += 2
    if x1 == x2 and (y1 + y2) % p == 0:
        if operations is not None:
            add_ops(operations, additions=1, reductions=1)
        return None
    if left == right:
        numerator = (3 * x1 * x1 + a) % p
        denominator = (2 * y1) % p
        if operations is not None:
            add_ops(
                operations,
                additions=1,
                multiplications=2,
                squarings=1,
                inversions=1,
                reductions=5,
            )
    else:
        numerator = (y2 - y1) % p
        denominator = (x2 - x1) % p
        if operations is not None:
            add_ops(operations, subtractions=2, inversions=1, reductions=3)
    slope = numerator * pow(denominator, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    if operations is not None:
        add_ops(
            operations,
            subtractions=4,
            multiplications=2,
            squarings=1,
            reductions=5,
        )
    return x3, y3


def affine_mul(
    scalar: int,
    point: Point,
    p: int,
    a: int,
    operations: dict[str, int] | None = None,
) -> Point:
    if scalar < 0:
        if point is not None:
            point = point[0], (-point[1]) % p
        return affine_mul(-scalar, point, p, a, operations)
    result: Point = None
    addend = point
    while scalar:
        if scalar & 1:
            result = affine_add(result, addend, p, a, operations)
        scalar >>= 1
        if scalar:
            addend = affine_add(addend, addend, p, a, operations)
    return result


def rcb_add(left: Projective, right: Projective, p: int, a: int, b: int) -> Projective:
    """Literal local transcription of the frozen 40-gate RCB circuit."""
    X1, Y1, Z1 = left
    X2, Y2, Z2 = right
    b3 = (3 * b) % p
    t0 = X1 * X2 % p
    t1 = Y1 * Y2 % p
    t2 = Z1 * Z2 % p
    t3 = (X1 + Y1) % p
    t4 = (X2 + Y2) % p
    t3 = t3 * t4 % p
    t4 = (t0 + t1) % p
    t3 = (t3 - t4) % p
    t4 = (X1 + Z1) % p
    t5 = (X2 + Z2) % p
    t4 = t4 * t5 % p
    t5 = (t0 + t2) % p
    t4 = (t4 - t5) % p
    t5 = (Y1 + Z1) % p
    X3 = (Y2 + Z2) % p
    t5 = t5 * X3 % p
    X3 = (t1 + t2) % p
    t5 = (t5 - X3) % p
    Z3 = a * t4 % p
    X3 = b3 * t2 % p
    Z3 = (X3 + Z3) % p
    X3 = (t1 - Z3) % p
    Z3 = (t1 + Z3) % p
    Y3 = X3 * Z3 % p
    t1 = (t0 + t0) % p
    t1 = (t1 + t0) % p
    t2 = a * t2 % p
    t4 = b3 * t4 % p
    t1 = (t1 + t2) % p
    t2 = (t0 - t2) % p
    t2 = a * t2 % p
    t4 = (t4 + t2) % p
    t0 = t1 * t4 % p
    Y3 = (Y3 + t0) % p
    t0 = t5 * t4 % p
    X3 = t3 * X3 % p
    X3 = (X3 - t0) % p
    t0 = t3 * t1 % p
    Z3 = t5 * Z3 % p
    Z3 = (Z3 + t0) % p
    return X3, Y3, Z3


def rcb_add_mutated(
    left: Projective,
    right: Projective,
    p: int,
    a: int,
    b: int,
    mutation: str,
) -> Projective:
    X1, Y1, Z1 = left
    X2, Y2, Z2 = right
    b3 = b % p if mutation == "wrong_b3" else (3 * b) % p
    t0 = X1 * X2 % p
    t1 = Y1 * Y2 % p
    t2 = Z1 * Z2 % p
    t3 = (X1 + Y1) % p
    t4 = (X2 + Y2) % p
    t3 = t3 * t4 % p
    t4 = (t0 + t1) % p
    t3 = (t3 - t4) % p
    t4 = (X1 + Z1) % p
    t5 = (X2 + Z2) % p
    t4 = t4 * t5 % p
    t5 = (t0 + t2) % p
    t4 = (t4 - t5) % p
    t5 = (Y1 + Z1) % p
    X3 = (Y2 + Z2) % p
    t5 = t5 * X3 % p
    X3 = (t1 + t2) % p
    t5 = (t5 - X3) % p
    Z3 = a * t4 % p
    X3 = b3 * t2 % p
    Z3 = (X3 + Z3) % p
    X3 = (t1 - Z3) % p
    Z3 = (t1 + Z3) % p
    Y3 = X3 * Z3 % p
    t1 = (t0 + t0) % p
    t1 = (t1 + t0) % p
    t2 = a * t2 % p
    t4 = b3 * t4 % p
    t1 = (t1 + t2) % p
    t2 = (t0 - t2) % p
    t2 = a * t2 % p
    t4 = (t4 + t2) % p
    t0 = t1 * t4 % p
    Y3 = (Y3 + t0) % p
    t0 = t5 * t4 % p
    X3 = t3 * X3 % p
    X3 = (X3 + t0) % p if mutation == "flip_gate37" else (X3 - t0) % p
    t0 = t3 * t1 % p
    Z3 = t5 * Z3 % p
    Z3 = (Z3 + t0) % p
    return X3, Y3, Z3


def sum_five(
    points: Sequence[Projective], p: int, a: int, b: int, mutation: str | None = None
) -> Projective:
    if len(points) != 5:
        raise AssertionError("five RCB inputs are required")
    combine = rcb_add if mutation is None else None
    if combine is not None:
        value = combine(points[0], points[1], p, a, b)
        value = combine(value, points[2], p, a, b)
        value = combine(value, points[3], p, a, b)
        return combine(value, points[4], p, a, b)
    value = rcb_add_mutated(points[0], points[1], p, a, b, mutation)
    value = rcb_add_mutated(value, points[2], p, a, b, mutation)
    value = rcb_add_mutated(value, points[3], p, a, b, mutation)
    return rcb_add_mutated(value, points[4], p, a, b, mutation)


def rss_record() -> dict[str, Any]:
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    system = platform.system()
    if system == "Darwin":
        normalized = int(raw)
        rule = "Darwin ru_maxrss is bytes"
    else:
        normalized = int(raw) * 1024
        rule = "non-Darwin ru_maxrss is KiB multiplied by 1024"
    return {
        "platform": system,
        "raw_ru_maxrss": raw,
        "normalization": rule,
        "bytes": normalized,
    }


def enforce_rss() -> None:
    current = rss_record()["bytes"]
    if current > HARD_RSS_LIMIT:
        raise MemoryError(f"peak RSS {current} exceeded {HARD_RSS_LIMIT}")


def oriented_rows(values: Sequence[Any], B: int, cut: int) -> tuple[list[list[Any]], int, int]:
    left = B**cut
    right = B ** (5 - cut)
    if len(values) != left * right:
        raise AssertionError("tensor size does not match the declared cut")
    if left <= right:
        return (
            [list(values[row * right : (row + 1) * right]) for row in range(left)],
            left,
            right,
        )
    rows = [[values[row * right + column] for row in range(left)] for column in range(right)]
    return rows, right, left


def rank_fp(
    values: Sequence[int], B: int, cut: int, p: int
) -> tuple[int, dict[str, int], dict[str, int], str, dict[str, int]]:
    rows, r, c = oriented_rows(values, B, cut)
    basis: dict[int, list[int]] = {}
    traffic = {
        "materialization": 2 * r * c,
        "pivot_scan": 0,
        "elimination_update": 0,
        "normalization": 0,
        "certificate": 0,
        "total": 0,
    }
    arithmetic = {"multiplications": 0, "subtractions": 0, "inversions": 0}
    for row in rows:
        cursor = 0
        while cursor < c:
            traffic["pivot_scan"] += 1
            if row[cursor] == 0:
                cursor += 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = pow(row[cursor], -1, p)
                for position in range(c):
                    row[position] = row[position] * inverse % p
                traffic["normalization"] += 2 * c
                arithmetic["multiplications"] += c
                arithmetic["inversions"] += 1
                basis[cursor] = row
                break
            factor = row[cursor]
            for position in range(c):
                row[position] = (row[position] - factor * prior[position]) % p
            traffic["elimination_update"] += 3 * c
            arithmetic["multiplications"] += c
            arithmetic["subtractions"] += c
            cursor += 1
    width = width_for(p)
    pivot_width = max(1, (c.bit_length() + 7) // 8)
    certificate = hashlib.sha256()
    for pivot in sorted(basis):
        certificate.update(pivot.to_bytes(pivot_width, "big"))
        for entry in basis[pivot]:
            certificate.update(entry.to_bytes(width, "big"))
        traffic["certificate"] += c
    traffic["total"] = sum(value for key, value in traffic.items() if key != "total")
    P = r * c
    E = c * r * (r - 1) // 2
    upper = {"P": P, "E": E, "N": E + P, "T": 3 * E + 6 * P}
    if traffic["pivot_scan"] > P or traffic["total"] > upper["T"]:
        raise AssertionError("F_p rank traffic exceeded the v3 ceiling")
    return len(basis), traffic, arithmetic, certificate.hexdigest(), upper


def rank_fp2(
    values: Sequence[Fp2], B: int, cut: int, p: int, nu: int
) -> tuple[int, dict[str, int], dict[str, int], str, dict[str, int]]:
    rows, r, c = oriented_rows(values, B, cut)
    basis: dict[int, list[Fp2]] = {}
    traffic = {
        "materialization": 2 * r * c,
        "pivot_scan": 0,
        "elimination_update": 0,
        "normalization": 0,
        "certificate": 0,
        "total": 0,
    }
    arithmetic = {"multiplications": 0, "subtractions": 0, "inversions": 0}
    for row in rows:
        cursor = 0
        while cursor < c:
            traffic["pivot_scan"] += 1
            if fp2_zero(row[cursor]):
                cursor += 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = fp2_inv(row[cursor], p, nu)
                for position in range(c):
                    row[position] = fp2_mul(row[position], inverse, p, nu)
                traffic["normalization"] += 2 * c
                arithmetic["multiplications"] += c
                arithmetic["inversions"] += 1
                basis[cursor] = row
                break
            factor = row[cursor]
            for position in range(c):
                row[position] = fp2_sub(
                    row[position], fp2_mul(factor, prior[position], p, nu), p
                )
            traffic["elimination_update"] += 3 * c
            arithmetic["multiplications"] += c
            arithmetic["subtractions"] += c
            cursor += 1
    width = width_for(p)
    pivot_width = max(1, (c.bit_length() + 7) // 8)
    certificate = hashlib.sha256()
    for pivot in sorted(basis):
        certificate.update(pivot.to_bytes(pivot_width, "big"))
        for real, omega in basis[pivot]:
            certificate.update(real.to_bytes(width, "big"))
            certificate.update(omega.to_bytes(width, "big"))
        traffic["certificate"] += c
    traffic["total"] = sum(value for key, value in traffic.items() if key != "total")
    P = r * c
    E = c * r * (r - 1) // 2
    upper = {"P": P, "E": E, "N": E + P, "T": 3 * E + 6 * P}
    if traffic["pivot_scan"] > P or traffic["total"] > upper["T"]:
        raise AssertionError("F_p2 rank traffic exceeded the v3 ceiling")
    return len(basis), traffic, arithmetic, certificate.hexdigest(), upper


def hilbert_cap(B: int, degrees: Sequence[int], cut: int) -> int:
    dimensions = [min(B, 3 * degree) for degree in degrees]
    return min(math.prod(dimensions[:cut]), math.prod(dimensions[cut:]))


def empty_rank_aggregate() -> dict[str, Any]:
    return {
        "jobs": 0,
        "P": 0,
        "E": 0,
        "N": 0,
        "T": 0,
        "traffic": {
            "materialization": 0,
            "pivot_scan": 0,
            "elimination_update": 0,
            "normalization": 0,
            "certificate": 0,
            "total": 0,
        },
        "arithmetic": {"multiplications": 0, "subtractions": 0, "inversions": 0},
    }


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
    rank_aggregate: dict[str, dict[str, Any]] | None,
    control: bool = False,
) -> dict[str, Any]:
    if tensor == "g":
        degrees = [16, 16, 8, 4, 2]
    elif control:
        degrees = [B, B, B, B, B]
    else:
        power = exponent or 1
        degrees = [32 * power, 32 * power, 16 * power, 8 * power, 4 * power]
    cap = (
        min(B**cut, B ** (5 - cut))
        if control
        else hilbert_cap(B, degrees, cut)
    )
    if field == "F_p":
        rank, traffic, arithmetic, certificate, upper = rank_fp(
            values, B, cut, p  # type: ignore[arg-type]
        )
    elif field == "F_p2":
        rank, traffic, arithmetic, certificate, upper = rank_fp2(
            values, B, cut, p, nu  # type: ignore[arg-type]
        )
    else:
        raise AssertionError(f"unsupported rank field {field}")
    if rank > cap:
        raise AssertionError(f"{tensor} cut {cut} rank {rank} exceeded cap {cap}")
    if rank_aggregate is not None:
        aggregate = rank_aggregate[field]
        aggregate["jobs"] += 1
        for key in ("P", "E", "N", "T"):
            aggregate[key] += upper[key]
        for key in aggregate["traffic"]:
            aggregate["traffic"][key] += traffic[key]
        for key in aggregate["arithmetic"]:
            aggregate["arithmetic"][key] += arithmetic[key]
    return {
        "tensor": tensor,
        "exponent": exponent,
        "cut": cut,
        "field": field,
        "rank_kind": "exact",
        "rank": rank,
        "hilbert_cap": cap,
        "certificate_digest": certificate,
        "traffic": traffic,
        "accounting": {"upper": upper, "arithmetic": arithmetic},
    }


def new_state() -> dict[str, Any]:
    return {
        "rank": {"F_p": empty_rank_aggregate(), "F_p2": empty_rank_aggregate()},
        "cohort_rank": empty_rank_aggregate(),
        "operation_buckets": {
            name: {"F_p": empty_field_ops(), "F_p2": empty_field_ops(), "group_additions": 0}
            for name in (
                "manifest_replay",
                "rcb_source_tables",
                "affine_source_replay",
                "target_setup",
                "residuals",
                "norm_product",
                "norm_quadratic",
                "source_span",
                "powers",
                "rank_elimination",
                "cohort_span",
                "comparators",
                "certificate_digest",
            )
        },
        "counts": {
            "source_tables": 0,
            "source_tuple_evaluations": 0,
            "rcb_calls": 0,
            "semantic_cells": 0,
            "residual_norm_evaluations": 0,
            "power_squarings": 0,
            "cohort_span_jobs": 0,
            "comparator_jobs": 0,
            "comparator_candidate_additions": 0,
        },
        "mismatches": {
            "manifest": 0,
            "invalid_projective": 0,
            "source_affine_replay": 0,
            "source_projective_scaling": 0,
            "norm": 0,
            "non_base_field": 0,
            "source_span": 0,
            "zero_set": 0,
            "rescaling": 0,
            "rank_cap": 0,
            "rank_invariance": 0,
            "control_rank": 0,
            "schedule": 0,
            "traffic_ceiling": 0,
        },
        "traffic": {
            "source_input_words_read": 0,
            "source_output_words_written": 0,
            "source_cache_words_read": 0,
            "target_words_read": 0,
            "tensor_words_written": 0,
            "source_digest_bytes_read": 0,
            "tensor_digest_bytes_read": 0,
            "comparator_bytes_written": 0,
            "comparator_lookup_bytes": 0,
            "comparator_replay_bytes": 0,
        },
        "canonical_storage": {
            "source_output_bytes": 0,
            "g_tensor_bytes": 0,
            "h_tensor_bytes": 0,
            "power_tensor_bytes": 0,
            "comparator_retained_bytes": 0,
            "peak_live_model_bytes": 0,
        },
        "witness_count": 0,
        "no_hit_count": 0,
    }


def validate_inputs(
    manifest_record: dict[str, Any],
    matrix_record: dict[str, Any],
    mutation_record: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = manifest_record.get("manifest")
    matrix = matrix_record.get("execution_matrix")
    mutations = mutation_record.get("mutation_manifest")
    if not isinstance(manifest, dict) or not isinstance(matrix, dict) or not isinstance(mutations, dict):
        raise AssertionError("input envelopes are missing")
    if manifest.get("id") != "MANIFEST-ECDLP-TT-NORM-RANK-001" or manifest.get("version") != 1:
        raise AssertionError("unexpected instance manifest identity")
    if matrix.get("id") != "MATRIX-ECDLP-TT-NORM-RANK-003" or matrix.get("version") != 3:
        raise AssertionError("unexpected execution matrix identity")
    if mutations.get("id") != "MUTATIONS-ECDLP-TT-NORM-RANK-002" or mutations.get("version") != 2:
        raise AssertionError("unexpected mutation manifest identity")
    if manifest.get("experiment_id") != EXPERIMENT_ID or matrix.get("experiment_id") != EXPERIMENT_ID:
        raise AssertionError("experiment identity mismatch")
    if manifest.get("mode_order") != ["P1", "P2", "P3", "P4", "P5"]:
        raise AssertionError("mode order changed")
    if manifest.get("addition_tree") != "Add(Add(Add(Add(P1,P2),P3),P4),P5)":
        raise AssertionError("addition tree changed")
    law = manifest.get("addition_law")
    if not isinstance(law, dict) or law.get("b3") != "3*b mod p":
        raise AssertionError("b3 declaration changed")
    if law.get("gate_count") != 40 or law.get("normalized_gate_text") != GATE_TEXT:
        raise AssertionError("RCB gate text changed")
    gate_digest = hashlib.sha256("\n".join(GATE_TEXT).encode("ascii")).hexdigest()
    if gate_digest != law.get("normalized_gate_text_sha256"):
        raise AssertionError("RCB gate digest changed")
    instances = manifest.get("instances")
    if not isinstance(instances, list) or [row.get("curve_id") for row in instances] != CURVE_IDS:
        raise AssertionError("curve schedule changed")
    if matrix.get("curve_ids") != CURVE_IDS or matrix.get("optional_cells") != []:
        raise AssertionError("execution curve or optional-cell schedule changed")
    rank_fields = manifest.get("rank_field")
    if not isinstance(rank_fields, dict) or rank_fields.get("g_Q") != "F_p2" or rank_fields.get("h_Q_and_powers") != "F_p":
        raise AssertionError("rank-field provenance changed")
    mutation_rows = mutations.get("mutations")
    if not isinstance(mutation_rows, list) or [row.get("id") for row in mutation_rows] != MUTATION_IDS:
        raise AssertionError("mutation schedule changed")
    controls = mutations.get("controls")
    if not isinstance(controls, list) or len(controls) != 6:
        raise AssertionError("control schedule changed")
    expected_counts = {
        "source_tables": 24,
        "semantic_cells": 60,
        "ec_rank_jobs_per_path": 264,
        "control_rank_jobs_per_path": 24,
        "total_rank_jobs_per_path": 288,
        "cohort_span_jobs_per_path": 12,
        "d2_d3_comparator_jobs_per_path": 18,
    }
    if matrix.get("mandatory_job_counts") != expected_counts:
        raise AssertionError("mandatory count schedule changed")
    return manifest, matrix, mutations


def point_record_affine(record: dict[str, Any]) -> Point:
    value = record.get("affine")
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise AssertionError("invalid affine point record")
    return int(value[0]), int(value[1])


def point_record_projective(record: dict[str, Any]) -> Projective:
    value = record.get("projective")
    if not isinstance(value, list) or len(value) != 3:
        raise AssertionError("invalid projective point record")
    return int(value[0]), int(value[1]), int(value[2])


def audit_instance(instance: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    curve_id = str(instance["curve_id"])
    B = int(instance["factor_base_size_B"])
    p = int(instance["field"]["p"])
    curve = instance["curve"]
    a = int(curve["a"])
    b = int(curve["b"])
    q = int(instance["subgroup"]["q"])
    generator = point_record_affine(
        {"affine": instance["subgroup"]["generator_affine"]}
    )
    manifest_ops = state["operation_buckets"]["manifest_replay"]["F_p"]
    if generator is None:
        raise AssertionError("generator cannot be the identity")
    if not projective_on_curve(affine_to_projective(generator), p, a, b):
        raise AssertionError(f"{curve_id}: generator is off curve")
    registry_audits: dict[str, Any] = {}
    for family in REGISTRY_NAMES:
        rows = instance["registries"].get(family)
        if not isinstance(rows, list) or len(rows) != B:
            raise AssertionError(f"{curve_id}:{family}: registry size mismatch")
        ids = [str(row["point_id"]) for row in rows]
        affine = [point_record_affine(row) for row in rows]
        if len(set(ids)) != B or len(set(affine)) != B or any(point is None for point in affine):
            raise AssertionError(f"{curve_id}:{family}: uniqueness failure")
        for index, row in enumerate(rows):
            point = affine[index]
            if point is None or not projective_on_curve(affine_to_projective(point), p, a, b):
                raise AssertionError(f"{curve_id}:{family}: off-curve point")
            source = row["source"]
            if family == "random_unique":
                label = str(source["label"])
                scalar = sha256_scalar(label, q)
                if source.get("scalar") != scalar or affine_mul(scalar, generator, p, a, manifest_ops) != point:
                    raise AssertionError(f"{curve_id}:{family}: scalar provenance failure")
            elif family == "consecutive_scalar_control":
                scalar = index + 1
                if source.get("scalar") != scalar or affine_mul(scalar, generator, p, a, manifest_ops) != point:
                    raise AssertionError(f"{curve_id}:{family}: scalar control failure")
        registry_audits[family] = {
            "identifier_unique": True,
            "affine_unique": True,
            "entry_count": B,
            "point_ids_digest": stable_digest(ids),
            "affine_digest": stable_digest(affine),
        }
    for target in instance["primary_targets"]:
        source = target["source"]
        scalar = sha256_scalar(str(source["label"]), q)
        point = point_record_affine(target)
        if point is None or source.get("scalar") != scalar:
            raise AssertionError(f"{curve_id}: target scalar provenance failure")
        if affine_mul(scalar, generator, p, a, manifest_ops) != point:
            raise AssertionError(f"{curve_id}: target point provenance failure")
    extension = instance["quadratic_extension"]
    nu = int(extension["nu"])
    if extension.get("omega_trace") != 0 or extension.get("omega_norm") != (-nu) % p:
        raise AssertionError(f"{curve_id}: extension metadata failure")
    return {
        "curve_id": curve_id,
        "generator_fixed": bool(instance["subgroup"].get("generator_fixed")),
        "modulus_fixed": True,
        "curve_fixed": True,
        "registries_fixed": True,
        "targets_fixed": True,
        "special_modulus": {"p_mod_4": p % 4},
        "special_curve": {"j_invariant": curve["j_invariant"], "cofactor": curve["cofactor"]},
        "extension": copy.deepcopy(extension),
        "registries": registry_audits,
    }


def targets_for_instance(instance: dict[str, Any], state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    curve_id = instance["curve_id"]
    p = int(instance["field"]["p"])
    a = int(instance["curve"]["a"])
    b = int(instance["curve"]["b"])
    targets: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(instance["primary_targets"]):
        name = f"Q{index:02d}"
        targets[name] = {
            "target_id": record["point_id"],
            "affine": point_record_affine(record),
            "projective": point_record_projective(record),
            "source": copy.deepcopy(record["source"]),
        }
    identity = next(
        row for row in instance["control_targets"] if row["source"]["kind"] == "identity_control"
    )
    targets["IDENTITY"] = {
        "target_id": identity["point_id"],
        "affine": None,
        "projective": (0, 1, 0),
        "source": copy.deepcopy(identity["source"]),
    }
    planted = next(
        row
        for row in instance["control_targets"]
        if row["source"]["kind"] == "sum_first_five_with_repetition"
    )
    registry = instance["registries"][planted["source"]["registry"]]
    indices = [int(value) for value in planted["source"]["indices"]]
    projective_points = [point_record_projective(registry[index]) for index in indices]
    affine_points = [point_record_affine(registry[index]) for index in indices]
    planted_projective = sum_five(projective_points, p, a, b)
    affine_ops = state["operation_buckets"]["target_setup"]["F_p"]
    planted_affine = affine_add(affine_points[0], affine_points[1], p, a, affine_ops)
    for point in affine_points[2:]:
        planted_affine = affine_add(planted_affine, point, p, a, affine_ops)
    if projective_to_affine(planted_projective, p) != planted_affine:
        raise AssertionError(f"{curve_id}: planted target RCB replay failed")
    target_bucket = state["operation_buckets"]["target_setup"]
    target_bucket["group_additions"] += 8
    add_ops(
        target_bucket["F_p"],
        additions=4 * 17,
        subtractions=4 * 6,
        multiplications=4 * 18,
        reductions=4 * 41,
    )
    targets["PLANTED"] = {
        "target_id": planted["point_id"],
        "affine": planted_affine,
        "projective": planted_projective,
        "source": copy.deepcopy(planted["source"]),
    }
    return targets


def source_samples(outputs: Sequence[Projective], B: int) -> list[dict[str, Any]]:
    return [
        {
            "linear_index": index,
            "tuple_indices": list(tuple_from_linear(index, B)),
            "value": list(outputs[index]),
        }
        for index in sample_indices(len(outputs))
    ]


def build_source_table(
    instance: dict[str, Any],
    family: str,
    state: dict[str, Any],
    *,
    rescaled: bool,
    mutation: str | None = None,
    affine_outputs: bool = False,
) -> dict[str, Any]:
    curve_id = instance["curve_id"]
    B = int(instance["factor_base_size_B"])
    p = int(instance["field"]["p"])
    a = int(instance["curve"]["a"])
    b = int(instance["curve"]["b"])
    registry = instance["registries"][family]
    affine_points = [point_record_affine(record) for record in registry]
    mode_points: list[list[Projective]] = []
    mode_factors: list[list[int]] = []
    for mode in range(5):
        points: list[Projective] = []
        factors: list[int] = []
        for record in registry:
            point = point_record_projective(record)
            if rescaled:
                label = (
                    f"{EXPERIMENT_ID}|RESCALE|{curve_id}|P{mode + 1}|{record['point_id']}"
                )
                factor = rescale_factor(label, p)
                point = projective_rescale(point, factor, p)
            else:
                factor = 1
            points.append(point)
            factors.append(factor)
        mode_points.append(points)
        mode_factors.append(factors)
    outputs: list[Projective] = []
    affine_sums: list[Point] = []
    homogeneous_source_factors: list[int] = []
    homogeneous_h_factors: list[int] = []
    invalid = 0
    affine_mismatches = 0
    affine_ops = state["operation_buckets"]["affine_source_replay"]["F_p"]
    degrees = (16, 16, 8, 4, 2)
    for indices in itertools.product(range(B), repeat=5):
        inputs = [mode_points[mode][indices[mode]] for mode in range(5)]
        expected = affine_add(affine_points[indices[0]], affine_points[indices[1]], p, a, affine_ops)
        for mode in range(2, 5):
            expected = affine_add(expected, affine_points[indices[mode]], p, a, affine_ops)
        if affine_outputs:
            output = affine_to_projective(expected)
        else:
            output = sum_five(inputs, p, a, b, mutation)
        if not projective_on_curve(output, p, a, b):
            invalid += 1
        if output != (0, 0, 0) and projective_to_affine(output, p) != expected:
            affine_mismatches += 1
        factor = 1
        for mode, index in enumerate(indices):
            factor = factor * pow(mode_factors[mode][index], degrees[mode], p) % p
        outputs.append(output)
        affine_sums.append(expected)
        homogeneous_source_factors.append(factor)
        homogeneous_h_factors.append(factor * factor % p)
    tuple_count = B**5
    rcb_calls = 0 if affine_outputs else 4 * tuple_count
    state["counts"]["source_tables"] += 1
    state["counts"]["source_tuple_evaluations"] += tuple_count
    state["counts"]["rcb_calls"] += rcb_calls
    state["mismatches"]["invalid_projective"] += invalid
    state["mismatches"]["source_affine_replay"] += affine_mismatches
    state["operation_buckets"]["affine_source_replay"]["group_additions"] += 4 * tuple_count
    if rcb_calls:
        bucket = state["operation_buckets"]["rcb_source_tables"]
        bucket["group_additions"] += rcb_calls
        add_ops(
            bucket["F_p"],
            additions=17 * rcb_calls,
            subtractions=6 * rcb_calls,
            multiplications=18 * rcb_calls,
            reductions=41 * rcb_calls,
        )
    width = width_for(p)
    state["traffic"]["source_input_words_read"] += 15 * tuple_count
    state["traffic"]["source_output_words_written"] += 3 * tuple_count
    state["traffic"]["source_digest_bytes_read"] += 3 * width * tuple_count
    canonical_bytes = 3 * width * tuple_count
    state["canonical_storage"]["source_output_bytes"] += canonical_bytes
    state["canonical_storage"]["peak_live_model_bytes"] = max(
        state["canonical_storage"]["peak_live_model_bytes"], canonical_bytes
    )
    enforce_rss()
    return {
        "tuple_count": tuple_count,
        "rcb_calls": rcb_calls,
        "outputs": outputs,
        "affine_sums": affine_sums,
        "homogeneous_source_factors": homogeneous_source_factors,
        "homogeneous_h_factors": homogeneous_h_factors,
        "output_digest": digest_projective(outputs, p),
        "invalid_projective_count": invalid,
        "affine_replay_mismatches": affine_mismatches,
        "samples": source_samples(outputs, B),
    }


def semantic_samples(
    g_values: Sequence[Fp2],
    h_values: Sequence[int],
    powers: dict[int, list[int]],
    source_outputs: Sequence[Projective],
    B: int,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index in sample_indices(len(h_values)):
        records.append(
            {
                "linear_index": index,
                "tuple_indices": list(tuple_from_linear(index, B)),
                "source": list(source_outputs[index]),
                "g": list(g_values[index]),
                "h": h_values[index],
                "powers": {str(exponent): values[index] for exponent, values in powers.items()},
            }
        )
    return records


def evaluate_cell(
    instance: dict[str, Any],
    family: str,
    target_name: str,
    target: dict[str, Any],
    table: dict[str, Any],
    state: dict[str, Any],
    *,
    rescaled: bool,
    unscaled_h: Sequence[int] | None = None,
) -> tuple[dict[str, Any], list[Fp2], list[int], dict[int, list[int]]]:
    curve_id = instance["curve_id"]
    B = int(instance["factor_base_size_B"])
    p = int(instance["field"]["p"])
    nu = int(instance["quadratic_extension"]["nu"])
    trace = int(instance["quadratic_extension"]["omega_trace"])
    norm = int(instance["quadratic_extension"]["omega_norm"])
    target_projective = target["projective"]
    target_affine = target["affine"]
    target_scale = 1
    if rescaled:
        target_scale = rescale_factor(
            f"{EXPERIMENT_ID}|RESCALE|{curve_id}|Q00", p
        )
        target_projective = projective_rescale(target_projective, target_scale, p)
    xq, yq, zq = target_projective
    c1 = zq * zq % p
    c2 = -zq * (2 * xq + trace * yq) % p
    c3 = (xq * xq + trace * xq * yq + norm * yq * yq) % p
    c4 = trace * zq * zq % p
    c5 = -zq * (trace * xq + 2 * norm * yq) % p
    c6 = norm * zq * zq % p
    if trace == 0 and c4 != 0:
        raise AssertionError("trace-zero source coefficient c4 is nonzero")
    g_values: list[Fp2] = []
    h_values: list[int] = []
    norm_mismatches = 0
    non_base_field_count = 0
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
        if product[1] != 0:
            non_base_field_count += 1
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
        is_zero = fp2_zero(g)
        expected_zero = table["affine_sums"][linear_index] == target_affine
        if is_zero != expected_zero:
            zero_set_mismatches += 1
        witness_count += int(is_zero)
        if rescaled:
            if unscaled_h is None:
                raise AssertionError("rescaled cell requires unscaled h tensor")
            predicted = (
                unscaled_h[linear_index]
                * target_scale
                * target_scale
                * table["homogeneous_h_factors"][linear_index]
            ) % p
            if quadratic != predicted:
                rescaling_mismatches += 1
        g_values.append(g)
        h_values.append(quadratic)
    powers: dict[int, list[int]] = {}
    if family == "random_unique" and target_name == "Q00" and not rescaled:
        current = h_values
        for exponent in (2, 4, 8):
            current = [value * value % p for value in current]
            powers[exponent] = current
    count = len(h_values)
    state["counts"]["semantic_cells"] += 1
    state["counts"]["residual_norm_evaluations"] += count
    state["counts"]["power_squarings"] += len(powers) * count
    state["witness_count"] += witness_count
    state["no_hit_count"] += count - witness_count
    state["mismatches"]["norm"] += norm_mismatches
    state["mismatches"]["non_base_field"] += non_base_field_count
    state["mismatches"]["source_span"] += source_span_mismatches
    state["mismatches"]["zero_set"] += zero_set_mismatches
    state["mismatches"]["rescaling"] += rescaling_mismatches
    add_ops(
        state["operation_buckets"]["residuals"]["F_p"],
        multiplications=4 * count,
        subtractions=2 * count,
        comparisons=2 * count,
        reductions=6 * count,
    )
    add_ops(
        state["operation_buckets"]["norm_product"]["F_p2"],
        multiplications=count,
        conjugations=count,
        comparisons=count,
        reductions=count,
    )
    add_ops(
        state["operation_buckets"]["norm_product"]["F_p"],
        additions=2 * count,
        subtractions=count,
        multiplications=5 * count,
        comparisons=2 * count,
        reductions=8 * count,
    )
    add_ops(
        state["operation_buckets"]["norm_quadratic"]["F_p"],
        additions=2 * count,
        multiplications=3 * count,
        squarings=2 * count,
        comparisons=count,
        reductions=7 * count,
    )
    add_ops(
        state["operation_buckets"]["source_span"]["F_p"],
        additions=5 * count,
        multiplications=9 * count,
        squarings=3 * count,
        comparisons=count,
        reductions=17 * count,
    )
    add_ops(
        state["operation_buckets"]["powers"]["F_p"],
        squarings=len(powers) * count,
        reductions=len(powers) * count,
    )
    width = width_for(p)
    state["traffic"]["source_cache_words_read"] += 3 * count
    state["traffic"]["target_words_read"] += 3 * count
    state["traffic"]["tensor_words_written"] += (3 + len(powers)) * count
    state["traffic"]["tensor_digest_bytes_read"] += (
        3 + len(powers)
    ) * width * count
    state["canonical_storage"]["g_tensor_bytes"] += 2 * width * count
    state["canonical_storage"]["h_tensor_bytes"] += width * count
    state["canonical_storage"]["power_tensor_bytes"] += len(powers) * width * count
    live = (3 + len(powers)) * width * count
    state["canonical_storage"]["peak_live_model_bytes"] = max(
        state["canonical_storage"]["peak_live_model_bytes"], live
    )
    semantic = {
        "tuple_count": count,
        "g_digest": digest_fp2(g_values, p),
        "h_digest": digest_fp(h_values, p),
        "power_digests": {
            str(exponent): digest_fp(values, p) for exponent, values in powers.items()
        },
        "norm_mismatches": norm_mismatches,
        "non_base_field_count": non_base_field_count,
        "source_span_mismatches": source_span_mismatches,
        "zero_set_mismatches": zero_set_mismatches,
        "rescaling_mismatches": rescaling_mismatches,
        "witness_count": witness_count,
        "no_hit_count": count - witness_count,
        "g_value_count": len(set(g_values)),
        "h_value_count": len(set(h_values)),
        "samples": semantic_samples(g_values, h_values, powers, table["outputs"], B),
        "source_coefficients": [c1, c2, c3, c4, c5, c6],
    }
    cell_id = f"{curve_id}:{family}:{target_name}" + (":rescaled" if rescaled else "")
    return (
        {
            "cell_id": cell_id,
            "target_id": target["target_id"],
            "target_name": target_name,
            "rescaled": rescaled,
            "semantic": semantic,
            "ranks": [],
        },
        g_values,
        h_values,
        powers,
    )


def attach_rank_schedule(
    cell: dict[str, Any],
    g_values: Sequence[Fp2],
    h_values: Sequence[int],
    powers: dict[int, list[int]],
    *,
    family: str,
    target_name: str,
    rescaled: bool,
    B: int,
    p: int,
    nu: int,
    state: dict[str, Any],
) -> None:
    records: list[dict[str, Any]] = []
    full_h = target_name == "Q00" or (
        family == "random_unique" and target_name in {"IDENTITY", "PLANTED"}
    )
    if rescaled:
        full_h = family == "random_unique" and target_name == "Q00"
    if full_h:
        for cut in range(1, 5):
            records.append(
                rank_record(
                    h_values,
                    tensor="h",
                    exponent=1,
                    B=B,
                    cut=cut,
                    p=p,
                    nu=nu,
                    field="F_p",
                    rank_aggregate=state["rank"],
                )
            )
    elif target_name in {"Q01", "Q02"} and family in {"random_unique", "x_interval"}:
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
                rank_aggregate=state["rank"],
            )
        )
    if family == "random_unique" and target_name == "Q00" and not rescaled:
        for cut in range(1, 5):
            records.append(
                rank_record(
                    g_values,
                    tensor="g",
                    exponent=None,
                    B=B,
                    cut=cut,
                    p=p,
                    nu=nu,
                    field="F_p2",
                    rank_aggregate=state["rank"],
                )
            )
        for exponent in (2, 4, 8):
            for cut in range(1, 5):
                records.append(
                    rank_record(
                        powers[exponent],
                        tensor="h_power",
                        exponent=exponent,
                        B=B,
                        cut=cut,
                        p=p,
                        nu=nu,
                        field="F_p",
                        rank_aggregate=state["rank"],
                    )
                )
    cell["ranks"] = records
    enforce_rss()


def rank_vector_family(
    vectors: Sequence[Sequence[int]], p: int, state: dict[str, Any]
) -> tuple[int, dict[str, Any]]:
    if not vectors:
        return 0, {}
    c = len(vectors[0])
    rows = [list(vector) for vector in vectors]
    if any(len(row) != c for row in rows):
        raise AssertionError("cohort vectors differ in length")
    r = len(rows)
    basis: dict[int, list[int]] = {}
    traffic = {
        "materialization": 2 * r * c,
        "pivot_scan": 0,
        "elimination_update": 0,
        "normalization": 0,
        "certificate": 0,
        "total": 0,
    }
    arithmetic = {"multiplications": 0, "subtractions": 0, "inversions": 0}
    for row in rows:
        cursor = 0
        while cursor < c:
            traffic["pivot_scan"] += 1
            if row[cursor] == 0:
                cursor += 1
                continue
            prior = basis.get(cursor)
            if prior is None:
                inverse = pow(row[cursor], -1, p)
                for position in range(c):
                    row[position] = row[position] * inverse % p
                traffic["normalization"] += 2 * c
                arithmetic["multiplications"] += c
                arithmetic["inversions"] += 1
                basis[cursor] = row
                break
            factor = row[cursor]
            for position in range(c):
                row[position] = (row[position] - factor * prior[position]) % p
            traffic["elimination_update"] += 3 * c
            arithmetic["multiplications"] += c
            arithmetic["subtractions"] += c
            cursor += 1
    traffic["certificate"] = len(basis) * c
    traffic["total"] = sum(value for key, value in traffic.items() if key != "total")
    aggregate = state["cohort_rank"]
    aggregate["jobs"] += 1
    P = r * c
    E = c * r * (r - 1) // 2
    aggregate["P"] += P
    aggregate["E"] += E
    aggregate["N"] += E + P
    aggregate["T"] += 3 * E + 6 * P
    for key, value in traffic.items():
        aggregate["traffic"][key] += value
    for key, value in arithmetic.items():
        aggregate["arithmetic"][key] += value
    state["counts"]["cohort_span_jobs"] += 1
    return len(basis), {"traffic": traffic, "arithmetic": arithmetic}


def canonical_point_bytes(point: Point, p: int) -> bytes:
    width = width_for(p)
    if point is None:
        return b"\x00" + bytes(2 * width)
    return b"\x01" + point[0].to_bytes(width, "big") + point[1].to_bytes(width, "big")


def support_digest(points: Iterable[Point], p: int) -> str:
    digest = hashlib.sha256()
    encoded = sorted(canonical_point_bytes(point, p) for point in points)
    for record in encoded:
        digest.update(record)
    return digest.hexdigest()


def comparator_record(
    instance: dict[str, Any], family: str, state: dict[str, Any]
) -> dict[str, Any]:
    p = int(instance["field"]["p"])
    a = int(instance["curve"]["a"])
    B = int(instance["factor_base_size_B"])
    points = [point_record_affine(row) for row in instance["registries"][family]]
    operations = state["operation_buckets"]["comparators"]["F_p"]
    d2: dict[Point, tuple[int, int]] = {}
    candidate_additions = 0
    for i, left in enumerate(points):
        for j, right in enumerate(points):
            candidate_additions += 1
            d2.setdefault(affine_add(left, right, p, a, operations), (i, j))
    d3: dict[Point, tuple[int, int, int]] = {}
    for partial, witness in d2.items():
        for index, point in enumerate(points):
            candidate_additions += 1
            d3.setdefault(affine_add(partial, point, p, a, operations), (*witness, index))
    N2 = len(d2)
    N3 = len(d3)
    index_bytes = max(1, ((B - 1).bit_length() + 7) // 8)
    point_bytes = 1 + 2 * width_for(p)
    d2_record_bytes = point_bytes + 2 * index_bytes
    d3_record_bytes = point_bytes + 3 * index_bytes
    retained_bytes = N2 * d2_record_bytes + N3 * d3_record_bytes
    lookup_bytes = N2 * (point_bytes + 2 * index_bytes)
    replay_bytes = N2 * (point_bytes + 5 * index_bytes)
    state["counts"]["comparator_jobs"] += 1
    state["counts"]["comparator_candidate_additions"] += candidate_additions
    state["operation_buckets"]["comparators"]["group_additions"] += candidate_additions
    state["traffic"]["comparator_bytes_written"] += retained_bytes
    state["traffic"]["comparator_lookup_bytes"] += lookup_bytes
    state["traffic"]["comparator_replay_bytes"] += replay_bytes
    state["canonical_storage"]["comparator_retained_bytes"] += retained_bytes
    return {
        "N2": N2,
        "N3": N3,
        "candidate_additions": candidate_additions,
        "candidate_addition_upper_bound": B * B + B * N2,
        "index_bytes": index_bytes,
        "point_bytes": point_bytes,
        "d2_record_bytes": d2_record_bytes,
        "d3_record_bytes": d3_record_bytes,
        "retained_bytes": retained_bytes,
        "lookup_traffic_bytes": lookup_bytes,
        "replay_traffic_bytes": replay_bytes,
        "usable_automorphism_quotient": 2,
        "d2_digest": support_digest(d2, p),
        "d3_digest": support_digest(d3, p),
        "rho_total_group_work_formula": "C_rho*sqrt(q/2)",
    }


def control_tensors(
    mutation_manifest: dict[str, Any], state: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, list[int]]]:
    p = 947
    B = 4
    tuples = list(itertools.product(range(B), repeat=5))
    separable = [math.prod(index + 1 for index in indices) % p for indices in tuples]
    norm = [
        ((indices[0] + 1) ** 2 - 2 * (indices[1] + 1) ** 2) % p
        for indices in tuples
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
        for indices in tuples
    ]
    asymmetric: list[int] = []
    for _, i2, i3, i4, i5 in tuples:
        if i2 == 0 and i3 == 0:
            selected = 0
        elif i2 == 0:
            selected = 1 if i4 == 0 else 2
        else:
            selected = 3
        asymmetric.append(int(i5 == selected))
    values_by_id = {
        "CTRL-SEPARABLE": separable,
        "CTRL-NORM": norm,
        "CTRL-ZERO": zero,
        "CTRL-SPIKE": spike,
        "CTRL-DENSE": dense,
        "CTRL-ASYMMETRIC": asymmetric,
    }
    manifest_controls = mutation_manifest["controls"]
    results: list[dict[str, Any]] = []
    for declaration in manifest_controls:
        control_id = declaration["id"]
        values = values_by_id[control_id]
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
                rank_aggregate=state["rank"],
                control=True,
            )
            for cut in range(1, 5)
        ]
        cut_ranks = [record["rank"] for record in ranks]
        expected = declaration["expected_cut_ranks"]
        if cut_ranks != expected:
            state["mismatches"]["control_rank"] += 1
        samples = [
            {
                "linear_index": index,
                "tuple_indices": list(tuple_from_linear(index, B)),
                "value": values[index],
            }
            for index in sample_indices(len(values))
        ]
        results.append(
            {
                "id": control_id,
                "B": B,
                "field": "F_947",
                "cut_ranks": cut_ranks,
                "digest": digest_fp(values, p),
                "samples": samples,
                "ranks": ranks,
            }
        )
    return results, values_by_id


def public_source_record(table: dict[str, Any]) -> dict[str, Any]:
    return {
        "tuple_count": table["tuple_count"],
        "rcb_calls": table["rcb_calls"],
        "output_digest": table["output_digest"],
        "invalid_projective_count": table["invalid_projective_count"],
        "affine_replay_mismatches": table["affine_replay_mismatches"],
        "samples": table["samples"],
    }


def process_curve(instance: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    curve_id = instance["curve_id"]
    B = int(instance["factor_base_size_B"])
    p = int(instance["field"]["p"])
    q = int(instance["subgroup"]["q"])
    nu = int(instance["quadratic_extension"]["nu"])
    targets = targets_for_instance(instance, state)
    registry_results: list[dict[str, Any]] = []
    for family in REGISTRY_NAMES:
        table = build_source_table(instance, family, state, rescaled=False)
        names = (
            ["Q00", "Q01", "Q02", "IDENTITY", "PLANTED"]
            if family == "random_unique"
            else (["Q00", "Q01", "Q02"] if family == "x_interval" else ["Q00"])
        )
        cells: list[dict[str, Any]] = []
        h_by_target: dict[str, list[int]] = {}
        q00_ranks: list[dict[str, Any]] = []
        for target_name in names:
            cell, g_values, h_values, powers = evaluate_cell(
                instance,
                family,
                target_name,
                targets[target_name],
                table,
                state,
                rescaled=False,
            )
            attach_rank_schedule(
                cell,
                g_values,
                h_values,
                powers,
                family=family,
                target_name=target_name,
                rescaled=False,
                B=B,
                p=p,
                nu=nu,
                state=state,
            )
            h_by_target[target_name] = h_values
            if target_name == "Q00":
                q00_ranks = [record for record in cell["ranks"] if record["tensor"] == "h"]
            cells.append(cell)
        span_dimension: int | None = None
        span_record: dict[str, Any] | None = None
        if family in {"random_unique", "x_interval"}:
            span_dimension, span_accounting = rank_vector_family(
                [h_by_target[name] for name in ("Q00", "Q01", "Q02")], p, state
            )
            span_record = {
                "targets": [targets[name]["target_id"] for name in ("Q00", "Q01", "Q02")],
                "dimension": span_dimension,
                "scope": "tested_three_target_cohort_only",
                "accounting": span_accounting,
            }
        source = public_source_record(table)
        if family == "random_unique":
            rescaled_table = build_source_table(instance, family, state, rescaled=True)
            scaling_mismatches = 0
            for index, (plain, scaled) in enumerate(zip(table["outputs"], rescaled_table["outputs"])):
                factor = rescaled_table["homogeneous_source_factors"][index]
                predicted = tuple(factor * coordinate % p for coordinate in plain)
                if predicted != scaled:
                    scaling_mismatches += 1
            state["mismatches"]["source_projective_scaling"] += scaling_mismatches
            source["rescaled"] = public_source_record(rescaled_table)
            source["rescaled"]["projective_scaling_mismatches"] = scaling_mismatches
            rescaled_cell, rescaled_g, rescaled_h, rescaled_powers = evaluate_cell(
                instance,
                family,
                "Q00",
                targets["Q00"],
                rescaled_table,
                state,
                rescaled=True,
                unscaled_h=h_by_target["Q00"],
            )
            attach_rank_schedule(
                rescaled_cell,
                rescaled_g,
                rescaled_h,
                rescaled_powers,
                family=family,
                target_name="Q00",
                rescaled=True,
                B=B,
                p=p,
                nu=nu,
                state=state,
            )
            plain_profile = [(record["cut"], record["rank"]) for record in q00_ranks]
            scaled_profile = [
                (record["cut"], record["rank"]) for record in rescaled_cell["ranks"]
            ]
            if plain_profile != scaled_profile:
                state["mismatches"]["rank_invariance"] += 1
            cells.append(rescaled_cell)
            del rescaled_table, rescaled_g, rescaled_h
        comparator = comparator_record(instance, family, state)
        registry_result = {
            "name": family,
            "primary": family in {"random_unique", "x_interval"},
            "source": source,
            "comparator": comparator,
            "tested_cohort_span_dimension": span_dimension,
            "tested_cohort_span": span_record,
            "cells": cells,
        }
        registry_results.append(registry_result)
        del table, h_by_target
        enforce_rss()
    return {
        "curve_id": curve_id,
        "B": B,
        "p": p,
        "q": q,
        "curve": copy.deepcopy(instance["curve"]),
        "extension": copy.deepcopy(instance["quadratic_extension"]),
        "registries": registry_results,
    }


def git_snapshot() -> dict[str, Any]:
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=SCRIPT_PATH.parent,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_text = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        entries = [line for line in status_text.splitlines() if line]
        return {
            "available": True,
            "root": root,
            "head": head,
            "protocol_commit": PROTOCOL_COMMIT,
            "dirty": bool(entries),
            "status_entries": entries,
            "status_sha256": hashlib.sha256(status_text.encode("utf-8")).hexdigest(),
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "error": f"{type(exc).__name__}: {exc}"}


def build_provenance(
    manifest_path: Path, matrix_path: Path, mutation_path: Path
) -> dict[str, Any]:
    return {
        "manifest_sha256": sha256_file(manifest_path),
        "execution_matrix_sha256": sha256_file(matrix_path),
        "mutation_manifest_sha256": sha256_file(mutation_path),
        "generator_sha256": sha256_file(SCRIPT_PATH),
        "manifest_path": str(manifest_path.resolve()),
        "execution_matrix_path": str(matrix_path.resolve()),
        "mutation_manifest_path": str(mutation_path.resolve()),
        "generator_path": str(SCRIPT_PATH),
        "protocol_commit": PROTOCOL_COMMIT,
        "command": [sys.executable, *sys.argv],
        "cwd": os.getcwd(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "platform": platform.platform(),
        "git": git_snapshot(),
        "dependency_policy": "python_standard_library_only",
        "external_network": "not_used",
        "generator_imports_verifier": False,
        "generator_imports_existing_ec_math": False,
    }


def expected_rank_record(P: int, E: int, N: int, T: int) -> dict[str, Any]:
    return {
        "P": P,
        "E": E,
        "N": N,
        "T": T,
        "traffic": {
            "materialization": 2 * P,
            "pivot_scan": P,
            "elimination_update": 3 * E,
            "normalization": 2 * P,
            "certificate": P,
            "total": T,
        },
    }


def observed_rank_record(aggregate: dict[str, Any], base_words: int) -> dict[str, Any]:
    traffic = copy.deepcopy(aggregate["traffic"])
    return {
        "jobs": aggregate["jobs"],
        "P": traffic["materialization"] // 2,
        "E": traffic["elimination_update"] // 3,
        "N": aggregate["arithmetic"]["multiplications"],
        "T": traffic["total"],
        "traffic": traffic,
        "arithmetic": copy.deepcopy(aggregate["arithmetic"]),
        "ceiling": {key: aggregate[key] for key in ("P", "E", "N", "T")},
        "base_field_word_equivalents": base_words * traffic["total"],
    }


def populate_rank_operation_buckets(state: dict[str, Any]) -> None:
    bucket = state["operation_buckets"]["rank_elimination"]
    fp = state["rank"]["F_p"]["arithmetic"]
    add_ops(
        bucket["F_p"],
        multiplications=fp["multiplications"],
        subtractions=fp["subtractions"],
        inversions=fp["inversions"],
        reductions=fp["multiplications"] + fp["subtractions"] + fp["inversions"],
    )
    fp2 = state["rank"]["F_p2"]["arithmetic"]
    add_ops(
        bucket["F_p2"],
        multiplications=fp2["multiplications"],
        subtractions=fp2["subtractions"],
        inversions=fp2["inversions"],
        reductions=fp2["multiplications"] + fp2["subtractions"] + fp2["inversions"],
    )
    add_ops(
        bucket["F_p"],
        additions=2 * fp2["multiplications"],
        subtractions=2 * fp2["subtractions"] + 2 * fp2["inversions"],
        multiplications=5 * fp2["multiplications"] + 3 * fp2["inversions"],
        squarings=2 * fp2["inversions"],
        inversions=fp2["inversions"],
        reductions=(
            7 * fp2["multiplications"]
            + 2 * fp2["subtractions"]
            + 8 * fp2["inversions"]
        ),
    )
    cohort = state["cohort_rank"]["arithmetic"]
    add_ops(
        state["operation_buckets"]["cohort_span"]["F_p"],
        multiplications=cohort["multiplications"],
        subtractions=cohort["subtractions"],
        inversions=cohort["inversions"],
        reductions=cohort["multiplications"] + cohort["subtractions"] + cohort["inversions"],
    )


def total_operations(state: dict[str, Any]) -> dict[str, Any]:
    totals = {"F_p": empty_field_ops(), "F_p2": empty_field_ops(), "group_additions": 0}
    for bucket in state["operation_buckets"].values():
        merge_ops(totals["F_p"], bucket["F_p"])
        merge_ops(totals["F_p2"], bucket["F_p2"])
        totals["group_additions"] += bucket["group_additions"]
    return totals


def finalize_accounting(
    state: dict[str, Any],
    matrix: dict[str, Any],
    start_wall_ns: int,
    start_cpu_ns: int,
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    populate_rank_operation_buckets(state)
    aggregate = matrix["aggregate_counts_per_path"]
    mandatory = matrix["mandatory_job_counts"]
    fp_expected = expected_rank_record(
        aggregate["fp_rank_working_matrix_coefficients_including_controls"],
        aggregate["fp_rank_elimination_subtraction_upper_bound_including_controls"],
        aggregate["fp_rank_multiplication_upper_bound_including_controls"],
        aggregate["fp_rank_logical_traffic_words"],
    )
    fp2_expected = expected_rank_record(
        aggregate["fp2_rank_working_matrix_coefficients"],
        aggregate["fp2_rank_elimination_subtraction_upper_bound"],
        aggregate["fp2_rank_multiplication_upper_bound"],
        aggregate["fp2_rank_logical_traffic_words"],
    )
    frozen_expected = {
        "mandatory_counts": copy.deepcopy(mandatory),
        "source_tuple_evaluations": aggregate["source_tuple_evaluations"],
        "rcb_calls": aggregate["rcb_calls"],
        "residual_norm_evaluations": aggregate["residual_norm_evaluations"],
        "power_squarings": aggregate["power_squarings"],
        "rank": {"F_p": fp_expected, "F_p2": fp2_expected},
        "rank_base_field_word_equivalent_traffic_ceiling": aggregate[
            "rank_logical_traffic_upper_bound_base_field_word_equivalents"
        ],
        "comparator_candidate_additions_upper_bound": aggregate[
            "d2_d3_candidate_additions_upper_bound"
        ],
        "peak_rss_hard_limit_bytes": HARD_RSS_LIMIT,
    }
    fp_observed = observed_rank_record(state["rank"]["F_p"], 1)
    fp2_observed = observed_rank_record(state["rank"]["F_p2"], 2)
    rank_base_words = (
        fp_observed["base_field_word_equivalents"]
        + fp2_observed["base_field_word_equivalents"]
    )
    peak_rss = rss_record()
    full_enumeration = {
        "source_tables": state["counts"]["source_tables"],
        "tuple_count": state["counts"]["source_tuple_evaluations"],
        "rcb_calls": state["counts"]["rcb_calls"],
        "classification": "diagnostic_full_enumeration",
        "retained_as_advice": False,
    }
    logical_traffic = copy.deepcopy(state["traffic"])
    logical_traffic["rank"] = {
        "F_p": fp_observed["traffic"],
        "F_p2": fp2_observed["traffic"],
        "base_field_word_equivalents": rank_base_words,
    }
    logical_traffic["cohort_span_rank"] = copy.deepcopy(state["cohort_rank"]["traffic"])
    canonical_storage = copy.deepcopy(state["canonical_storage"])
    observed = {
        "full_enumeration": full_enumeration,
        "semantic": {
            "cells": state["counts"]["semantic_cells"],
            "residual_norm_evaluations": state["counts"]["residual_norm_evaluations"],
            "power_squarings": state["counts"]["power_squarings"],
            "witness_count": state["witness_count"],
            "no_hit_count": state["no_hit_count"],
            "success_probability": "not_applicable",
        },
        "rank": {"F_p": fp_observed, "F_p2": fp2_observed},
        "cohort_span": copy.deepcopy(state["cohort_rank"]),
        "comparators": {
            "jobs": state["counts"]["comparator_jobs"],
            "candidate_additions": state["counts"]["comparator_candidate_additions"],
        },
        "operation_buckets": copy.deepcopy(state["operation_buckets"]),
        "operation_totals": total_operations(state),
        "logical_traffic": logical_traffic,
        "canonical_storage": canonical_storage,
        "peak_rss": peak_rss,
        "wall_time_ns": time.perf_counter_ns() - start_wall_ns,
        "cpu_time_ns": time.process_time_ns() - start_cpu_ns,
    }
    schedule_checks = {
        "source_tables": state["counts"]["source_tables"] == mandatory["source_tables"],
        "semantic_cells": state["counts"]["semantic_cells"] == mandatory["semantic_cells"],
        "source_tuple_evaluations": state["counts"]["source_tuple_evaluations"]
        == aggregate["source_tuple_evaluations"],
        "rcb_calls": state["counts"]["rcb_calls"] == aggregate["rcb_calls"],
        "residual_norm_evaluations": state["counts"]["residual_norm_evaluations"]
        == aggregate["residual_norm_evaluations"],
        "power_squarings": state["counts"]["power_squarings"]
        == aggregate["power_squarings"],
        "rank_jobs": state["rank"]["F_p"]["jobs"] + state["rank"]["F_p2"]["jobs"]
        == mandatory["total_rank_jobs_per_path"],
        "cohort_span_jobs": state["counts"]["cohort_span_jobs"]
        == mandatory["cohort_span_jobs_per_path"],
        "comparator_jobs": state["counts"]["comparator_jobs"]
        == mandatory["d2_d3_comparator_jobs_per_path"],
        "rank_fp_ceiling": all(state["rank"]["F_p"][key] == fp_expected[key] for key in ("P", "E", "N", "T")),
        "rank_fp2_ceiling": all(state["rank"]["F_p2"][key] == fp2_expected[key] for key in ("P", "E", "N", "T")),
        "rank_traffic": rank_base_words
        <= aggregate["rank_logical_traffic_upper_bound_base_field_word_equivalents"],
        "comparator_additions": state["counts"]["comparator_candidate_additions"]
        <= aggregate["d2_d3_candidate_additions_upper_bound"],
        "rss": peak_rss["bytes"] <= HARD_RSS_LIMIT,
    }
    failed_schedule = sum(not value for value in schedule_checks.values())
    state["mismatches"]["schedule"] += failed_schedule
    state["mismatches"]["traffic_ceiling"] += int(not schedule_checks["rank_traffic"])
    mismatch_total = sum(state["mismatches"].values())
    summary = {
        "mandatory_counts": {
            "source_tables": state["counts"]["source_tables"],
            "semantic_cells": state["counts"]["semantic_cells"],
            "ec_rank_jobs": state["rank"]["F_p"]["jobs"]
            + state["rank"]["F_p2"]["jobs"]
            - mandatory["control_rank_jobs_per_path"],
            "control_rank_jobs": mandatory["control_rank_jobs_per_path"],
            "total_rank_jobs": state["rank"]["F_p"]["jobs"]
            + state["rank"]["F_p2"]["jobs"],
            "cohort_span_jobs": state["counts"]["cohort_span_jobs"],
            "comparator_jobs": state["counts"]["comparator_jobs"],
        },
        "schedule_checks": schedule_checks,
        "mismatch_totals": copy.deepcopy(state["mismatches"]),
        "mismatch_total": mismatch_total,
        "witness_count": state["witness_count"],
        "no_hit_count": state["no_hit_count"],
    }
    accounting = {
        "frozen_expected": frozen_expected,
        "observed": observed,
        "full_enumeration": full_enumeration,
        "canonical_storage": canonical_storage,
        "logical_traffic": logical_traffic,
        "peak_rss": peak_rss,
        "advice": {
            "status": "not_executed",
            "retained_bytes": 0,
            "source_tables_are_advice": False,
        },
        "preprocessing": {
            "status": "diagnostic_full_enumeration_only",
            "compiler_preprocessing": "not_executed",
        },
        "online_specialization": {"status": "not_executed"},
        "comparator_boundaries": {
            "diagnostic": "Theta(B^5), not a compiler",
            "D2_plus_D3": "Theta(B^2+B*N2), at most Theta(B^3)",
            "rho_vow": "C_rho*sqrt(q/|Aut|), no hidden preprocessing",
            "tier_B": "advice and preprocessing o(B^3); per-target resources o(B^2)",
            "tier_C": "each end-to-end resource o(B^2.5) under one distribution",
        },
    }
    valid = mismatch_total == 0 and all(schedule_checks.values())
    return accounting, summary, valid


def run_baseline(
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    mutation_manifest: dict[str, Any],
    provenance: dict[str, Any],
    start_wall_ns: int,
    start_cpu_ns: int,
) -> dict[str, Any]:
    state = new_state()
    audits = [audit_instance(instance, state) for instance in manifest["instances"]]
    controls, _ = control_tensors(mutation_manifest, state)
    instances: list[dict[str, Any]] = []
    for instance in manifest["instances"]:
        instances.append(process_curve(instance, state))
        enforce_rss()
    accounting, summary, valid = finalize_accounting(
        state, matrix, start_wall_ns, start_cpu_ns
    )
    provenance = copy.deepcopy(provenance)
    provenance["fixedness_audit"] = audits
    provenance["input_firewalls"] = {
        "selection_frozen_before_values": True,
        "mode_order": ["P1", "P2", "P3", "P4", "P5"],
        "addition_tree": "Add(Add(Add(Add(P1,P2),P3),P4),P5)",
        "rcb_gate_text_sha256": hashlib.sha256("\n".join(GATE_TEXT).encode("ascii")).hexdigest(),
        "rank_fields": {"g": "F_p2", "h_and_powers": "F_p"},
        "tuple_order": "lexicographic_i5_fastest",
    }
    return {
        "protocol": PROTOCOL,
        "mode": "baseline",
        "valid": valid,
        "interpretation": INTERPRETATION,
        "breakthrough_claim": False,
        "compiler_constructed": False,
        "success_probability": "not_applicable",
        "provenance": provenance,
        "controls": controls,
        "instances": instances,
        "accounting": accounting,
        "summary": summary,
    }


def mutated_norm_semantic(
    instance: dict[str, Any], table: dict[str, Any], target: dict[str, Any]
) -> dict[str, Any]:
    p = int(instance["field"]["p"])
    nu = int(instance["quadratic_extension"]["nu"])
    trace = int(instance["quadratic_extension"]["omega_trace"])
    norm = int(instance["quadratic_extension"]["omega_norm"])
    xq, yq, zq = target["projective"]
    g_values: list[Fp2] = []
    mutated_h: list[Fp2] = []
    mismatches = 0
    non_base = 0
    for x, y, z in table["outputs"]:
        ex = (zq * x - xq * z) % p
        ey = (zq * y - yq * z) % p
        g = (ex, ey)
        value = fp2_mul(g, g, p, nu)
        quadratic = (ex * ex + trace * ex * ey + norm * ey * ey) % p
        mismatches += int(value[1] != 0 or value[0] != quadratic)
        non_base += int(value[1] != 0)
        g_values.append(g)
        mutated_h.append(value)
    if mismatches == 0:
        raise AssertionError("wrong norm mutation did not create a mismatch")
    return {
        "tuple_count": len(g_values),
        "g_digest": digest_fp2(g_values, p),
        "h_digest": digest_fp2(mutated_h, p),
        "h_field": "F_p2",
        "norm_mismatches": mismatches,
        "non_base_field_count": non_base,
    }


def artifact_entry(
    mutation_by_id: dict[str, dict[str, Any]], mutation_id: str, artifact: dict[str, Any]
) -> dict[str, Any]:
    declaration = mutation_by_id[mutation_id]
    return {
        "id": mutation_id,
        "classification": declaration["classification"],
        "expected": "rejected",
        "detector_expected": copy.deepcopy(declaration["detectors"]),
        "artifact": artifact,
    }


def run_mutations(
    manifest: dict[str, Any],
    matrix: dict[str, Any],
    mutation_manifest: dict[str, Any],
    provenance: dict[str, Any],
    start_wall_ns: int,
    start_cpu_ns: int,
) -> dict[str, Any]:
    state = new_state()
    instance = manifest["instances"][0]
    if instance["curve_id"] != "C08":
        raise AssertionError("frozen mutation curve C08 is missing")
    targets = targets_for_instance(instance, state)
    target = targets["Q00"]
    p = int(instance["field"]["p"])
    B = int(instance["factor_base_size_B"])
    nu = int(instance["quadratic_extension"]["nu"])
    correct = build_source_table(instance, "random_unique", state, rescaled=False)
    correct_cell, correct_g, correct_h, correct_powers = evaluate_cell(
        instance,
        "random_unique",
        "Q00",
        target,
        correct,
        state,
        rescaled=False,
    )
    attach_rank_schedule(
        correct_cell,
        correct_g,
        correct_h,
        correct_powers,
        family="random_unique",
        target_name="Q00",
        rescaled=False,
        B=B,
        p=p,
        nu=nu,
        state=state,
    )
    wrong_b3 = build_source_table(
        instance, "random_unique", state, rescaled=False, mutation="wrong_b3"
    )
    wrong_b3_cell, _, _, _ = evaluate_cell(
        instance,
        "random_unique",
        "Q00",
        target,
        wrong_b3,
        state,
        rescaled=False,
    )
    flipped = build_source_table(
        instance, "random_unique", state, rescaled=False, mutation="flip_gate37"
    )
    flipped_cell, _, _, _ = evaluate_cell(
        instance,
        "random_unique",
        "Q00",
        target,
        flipped,
        state,
        rescaled=False,
    )
    affine = build_source_table(
        instance, "random_unique", state, rescaled=False, affine_outputs=True
    )
    affine_cell, _, _, _ = evaluate_cell(
        instance,
        "random_unique",
        "Q00",
        target,
        affine,
        state,
        rescaled=False,
    )
    controls, values_by_id = control_tensors(mutation_manifest, state)
    controls_by_id = {row["id"]: row for row in controls}
    mutation_by_id = {row["id"]: row for row in mutation_manifest["mutations"]}
    artifacts: list[dict[str, Any]] = []
    for mutation_id, table, cell in (
        ("M01-WRONG-B3", wrong_b3, wrong_b3_cell),
        ("M02-FLIP-GATE37", flipped, flipped_cell),
        ("M03-AFFINE-PRODUCER", affine, affine_cell),
    ):
        artifacts.append(
            artifact_entry(
                mutation_by_id,
                mutation_id,
                {
                    "cell_id": "C08:random_unique:Q00",
                    "source": {"output_digest": table["output_digest"]},
                    "semantic": {
                        "g_digest": cell["semantic"]["g_digest"],
                        "h_digest": cell["semantic"]["h_digest"],
                    },
                    "source_claim": "frozen_literal_RCB",
                },
            )
        )
    zero_outputs = list(correct["outputs"])
    zero_outputs[0] = (0, 0, 0)
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M04-ZERO-PROJECTIVE",
            {
                "cell_id": "C08:random_unique:Q00",
                "source": {
                    "output_digest": digest_projective(zero_outputs, p),
                    "invalid_projective_count": 1,
                    "first_output": [0, 0, 0],
                },
            },
        )
    )
    wrong_norm = mutated_norm_semantic(instance, correct, target)
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M05-WRONG-FROBENIUS",
            {
                "cell_id": "C08:random_unique:Q00",
                "conjugation": "identity",
                "semantic": copy.deepcopy(wrong_norm),
            },
        )
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M06-G-SQUARED",
            {
                "cell_id": "C08:random_unique:Q00",
                "assignment": "h=g*g",
                "semantic": copy.deepcopy(wrong_norm),
            },
        )
    )
    wrong_field_record = copy.deepcopy(controls_by_id["CTRL-NORM"]["ranks"][0])
    wrong_field_record["tensor"] = "h"
    wrong_field_record["field"] = "F_p2"
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M07-RANK-FIELD-PROVENANCE",
            {"control_id": "CTRL-NORM", "rank_record": wrong_field_record},
        )
    )
    g_cut_two = next(
        record
        for record in correct_cell["ranks"]
        if record["tensor"] == "g" and record["cut"] == 2
    )
    raw_record = copy.deepcopy(g_cut_two)
    raw_record.update(
        {
            "tensor": "h",
            "exponent": 1,
            "field": "F_p",
            "rank_kind": "raw_hadamard_product",
            "rank": min(B**2, g_cut_two["rank"] ** 2),
            "hilbert_cap": hilbert_cap(B, [32, 32, 16, 8, 4], 2),
        }
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M08-RAW-BOND-AS-RANK",
            {"cell_id": "C08:random_unique:Q00", "rank_record": raw_record},
        )
    )
    asymmetric_ranks = controls_by_id["CTRL-ASYMMETRIC"]["cut_ranks"]
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M09-REVERSE-CUTS",
            {
                "control_id": "CTRL-ASYMMETRIC",
                "reported_cut_ranks": list(reversed(asymmetric_ranks)),
            },
        )
    )
    candidate = instance["primary_targets"][1]
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M10-POSTSELECT-TARGET",
            {
                "cell_id": "C08:random_unique:Q00",
                "selection": "post_observation_minimum_rank",
                "candidate": {
                    "target_id": candidate["point_id"],
                    "label": candidate["source"]["label"],
                    "scalar": candidate["source"]["scalar"],
                },
                "frozen_q00_target_id": instance["primary_targets"][0]["point_id"],
            },
        )
    )
    duplicate_registry = copy.deepcopy(instance["registries"]["random_unique"])
    duplicate_registry[1] = copy.deepcopy(duplicate_registry[0])
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M11-DUPLICATE-PRIMARY",
            {
                "curve_id": "C08",
                "registry": "random_unique",
                "point_ids": [row["point_id"] for row in duplicate_registry],
                "affine": [row["affine"] for row in duplicate_registry],
            },
        )
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M12-SHARED-VERIFIER-CODE",
            {
                "source_role": "verifier",
                "imports": ["generate_tt_norm_rank", str(SCRIPT_PATH)],
            },
        )
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M13-OMIT-ENUMERATION-COST",
            {
                "accounting": {
                    "canonical_storage": {"bytes": 0},
                    "logical_traffic": {"base_field_words": 0},
                    "peak_rss": rss_record(),
                },
                "omitted_key": "full_enumeration",
            },
        )
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M14-OMIT-MEMORY",
            {
                "accounting": {
                    "full_enumeration": {"tuple_count": correct["tuple_count"]}
                },
                "omitted_keys": ["canonical_storage", "logical_traffic", "peak_rss"],
            },
        )
    )
    artifacts.append(
        artifact_entry(
            mutation_by_id,
            "M15-ASYMPTOTIC-LABEL",
            {"interpretation": "ASYMPTOTIC", "breakthrough_claim": True},
        )
    )
    ids = [row["id"] for row in artifacts]
    classes_match = all(
        row["classification"] == mutation_by_id[row["id"]]["classification"]
        for row in artifacts
    )
    expected_match = all(row["expected"] == "rejected" for row in artifacts)
    valid = ids == MUTATION_IDS and classes_match and expected_match
    elapsed_wall = time.perf_counter_ns() - start_wall_ns
    elapsed_cpu = time.process_time_ns() - start_cpu_ns
    top_accounting = {
        "frozen_expected": {"mutation_count": 15, "mutation_ids": MUTATION_IDS},
        "observed": {
            "attempted": len(artifacts),
            "dynamic_source_tables": state["counts"]["source_tables"],
            "wall_time_ns": elapsed_wall,
            "cpu_time_ns": elapsed_cpu,
        },
        "full_enumeration": {
            "classification": "mutation_fixture_generation",
            "tuple_count": state["counts"]["source_tuple_evaluations"],
            "rcb_calls": state["counts"]["rcb_calls"],
        },
        "canonical_storage": copy.deepcopy(state["canonical_storage"]),
        "logical_traffic": copy.deepcopy(state["traffic"]),
        "peak_rss": rss_record(),
    }
    return {
        "protocol": PROTOCOL,
        "mode": "mutations",
        "valid": valid,
        "interpretation": INTERPRETATION,
        "breakthrough_claim": False,
        "compiler_constructed": False,
        "success_probability": "not_applicable",
        "provenance": provenance,
        "controls": [],
        "instances": [],
        "mutation_artifacts": artifacts,
        "accounting": top_accounting,
        "summary": {
            "attempted": 15,
            "emitted": len(artifacts),
            "missing": [mutation_id for mutation_id in MUTATION_IDS if mutation_id not in ids],
            "unexpected": [mutation_id for mutation_id in ids if mutation_id not in MUTATION_IDS],
            "classification_mismatches": int(not classes_match),
            "expected_outcome_mismatches": int(not expected_match),
        },
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", required=True, choices=("baseline", "mutations"))
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--execution-matrix", required=True, type=Path)
    parser.add_argument("--mutation-manifest", required=True, type=Path)
    return parser.parse_args(argv)


def error_result(mode: str, provenance: dict[str, Any], exc: BaseException) -> dict[str, Any]:
    return {
        "protocol": PROTOCOL,
        "mode": mode,
        "valid": False,
        "interpretation": INTERPRETATION,
        "breakthrough_claim": False,
        "compiler_constructed": False,
        "success_probability": "not_applicable",
        "provenance": provenance,
        "controls": [],
        "instances": [],
        "accounting": {
            "frozen_expected": {},
            "observed": {},
            "full_enumeration": {},
            "canonical_storage": {},
            "logical_traffic": {},
            "peak_rss": rss_record(),
        },
        "summary": {
            "error_type": type(exc).__name__,
            "error": str(exc),
            "failure_mode": "implementation_or_input_failure_not_mathematical_evidence",
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    start_wall_ns = time.perf_counter_ns()
    start_cpu_ns = time.process_time_ns()
    args = parse_args(argv)
    provenance: dict[str, Any] = {}
    try:
        provenance = build_provenance(
            args.manifest, args.execution_matrix, args.mutation_manifest
        )
        manifest_record = load_json(args.manifest)
        matrix_record = load_json(args.execution_matrix)
        mutation_record = load_json(args.mutation_manifest)
        manifest, matrix, mutation_manifest = validate_inputs(
            manifest_record, matrix_record, mutation_record
        )
        if args.mode == "baseline":
            result = run_baseline(
                manifest,
                matrix,
                mutation_manifest,
                provenance,
                start_wall_ns,
                start_cpu_ns,
            )
        else:
            result = run_mutations(
                manifest,
                matrix,
                mutation_manifest,
                provenance,
                start_wall_ns,
                start_cpu_ns,
            )
    except Exception as exc:
        result = error_result(args.mode, provenance, exc)
    json.dump(result, sys.stdout, sort_keys=True, separators=(",", ":"), allow_nan=False)
    sys.stdout.write("\n")
    return 0 if result.get("valid") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
