#!/usr/bin/env python3
"""Prospective, fail-closed runner for EXP-ECDLP-651b94.

This module contains the complete *future* finite protocol.  Importing it and
the default CLI do no fixture selection, Cayley calibration, collision census,
control panel, or timing measurement.  ``future-run`` is deliberately gated by
an externally authenticated Coordinator lock and a fresh archived review.

The correction successor implements DEC-20260907-38017a and the S4 operational
custody repair.  It is not a launch lock, a run record, or scientific evidence.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import json
import math
import os
import platform
import re
import resource
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import mpmath as mp
import yaml

TASK_ID = "TASK-20260908-4cacf0"
EXPERIMENT_ID = "EXP-ECDLP-651b94"
APPROVAL_ID = "DEC-20260906-f73475"
AMENDMENT_ID = "DEC-20260907-38017a"
CORRECTION_DECISION_ID = "DEC-20260908-afe5b9"
SPEC_SHA256 = "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee"
AMENDMENT_SHA256 = "a24e723fa1d499621957e1fd3939d3e95a0e1f9c003412396f6eec00d9052280"
MEMORY_LIMIT_BYTES = 8 * 1024**3
EXPLORATORY_SEEDS = tuple(range(606300, 606308))
HELDOUT_SEEDS = tuple(range(606308, 606316))
US = (1, 2, 3)
CAYLEY_GUARD_STRIDE = 16
MAX_SERIALIZATION_CHUNK_BYTES = 64 * 1024
MAX_PROGRESS_EVENT_BYTES = 1024
MAX_PROGRESS_LOG_BYTES = 256 * 1024 * 1024
MAX_PROGRESS_LATEST_BYTES = 64 * 1024
MAX_GUARD_POLL_INTERVAL_SECONDS = 0.250
DISPATCH_VALIDATOR_RELATIVE_PATH = "tools/research_dispatch.py"
DISPATCH_VALIDATOR_SHA256 = "5c40d891369c38f8d9013603fdf627f286243dffe4443878dd9e75926ec32c5c"
GOAL_LANES_RELATIVE_PATH = "tools/goal_lanes.py"
GOAL_LANES_SHA256 = "89f99ecac689e1c331be6c8a14de410e25d460fd4662903b04c63513e7fee82c"
EXPERIMENT_ARTIFACTS = (
    "manifest.yaml", "fixtures.json", "raw.jsonl", "controls.json", "costs.csv",
    "certificates.json", "stdout.log", "stderr.log", "report.md", "command.txt",
    "environment.json", "raw-result.json", "package-sha256.json",
)
PURPOSES = {"query", "control", "field_x", "target", "shuffle"}
Point = tuple[int, int] | None


class LaunchRefused(RuntimeError):
    """A required future admission input is absent, forged, or inconsistent."""


class CancellationStop(RuntimeError):
    """An operator cancellation was observed at a bounded checkpoint."""


class ResourceStop(RuntimeError):
    """The process-group memory guard stopped the prospective execution."""


class InfrastructureStop(RuntimeError):
    """I/O, repository, or host failure; never a scientific outcome."""


class MeasurementInvalidStop(RuntimeError):
    """A frozen validity control or certificate failed and requires an immediate stop."""


class IncompleteFixtureStop(RuntimeError):
    """The frozen fixture panel cannot be completed without widening it."""


def canonical_json(value: Any) -> bytes:
    """Frozen JSON serialization used by the SHA-256 streams and lock payload."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(
    path: Path, *, check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "hash_verification",
) -> str:
    """Hash an artifact with at most 64 KiB resident I/O chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk_index in range(sys.maxsize):
            guarded_checkpoint(check, chunk_index * CAYLEY_GUARD_STRIDE, purpose, on_progress, chunk_index=chunk_index)
            chunk = handle.read(MAX_SERIALIZATION_CHUNK_BYTES)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sha256_chunks(
    value: bytes, *, check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "hashing",
) -> str:
    digest = hashlib.sha256()
    for chunk_index, offset in enumerate(range(0, len(value), MAX_SERIALIZATION_CHUNK_BYTES)):
        guarded_checkpoint(check, chunk_index * CAYLEY_GUARD_STRIDE, purpose, on_progress, chunk_index=chunk_index)
        digest.update(value[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])
    return digest.hexdigest()


def write_chunked(
    handle: Any, value: bytes, *, check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "publication_write",
) -> None:
    for chunk_index, offset in enumerate(range(0, len(value), MAX_SERIALIZATION_CHUNK_BYTES)):
        guarded_checkpoint(check, chunk_index * CAYLEY_GUARD_STRIDE, purpose, on_progress, chunk_index=chunk_index)
        handle.write(value[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])


def json_bytes_chunked(
    value: Any, *, check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "serialization",
) -> bytes:
    """Serialize through bounded encoder fragments, probing before each fragment."""
    encoded = bytearray()
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    for fragment_index, fragment in enumerate(encoder.iterencode(value)):
        guarded_checkpoint(check, fragment_index, purpose, on_progress, fragment_index=fragment_index)
        raw = fragment.encode("utf-8")
        for offset in range(0, len(raw), MAX_SERIALIZATION_CHUNK_BYTES):
            encoded.extend(raw[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])
    return bytes(encoded)


def yaml_bytes_chunked(
    value: Any, *, check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    purpose: str = "serialization",
) -> bytes:
    """YAML output is emitted through the same bounded writer boundary."""
    text = yaml.safe_dump(value, sort_keys=False)
    encoded = bytearray()
    raw = text.encode("utf-8")
    for chunk_index, offset in enumerate(range(0, len(raw), MAX_SERIALIZATION_CHUNK_BYTES)):
        guarded_checkpoint(check, chunk_index, purpose, on_progress, chunk_index=chunk_index)
        encoded.extend(raw[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])
    return bytes(encoded)


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


ROOT = repository_root()
SPEC_PATH = ROOT / "experiments" / EXPERIMENT_ID / "specification.yaml"
AMENDMENT_PATH = ROOT / "experiments" / EXPERIMENT_ID / "amendments" / f"{AMENDMENT_ID}.yaml"
PLAN_PATH = Path(__file__).resolve().with_name("execution-plan.json")


def stream_digest(*, purpose: str, params: Sequence[int], seed: int, counter: int) -> int:
    """Frozen SHA-256 source: [experiment,purpose,[p,A,B,r,k,u,arm],seed,counter]."""
    if purpose not in PURPOSES or len(params) != 7:
        raise ValueError("unknown purpose or non-frozen parameter tuple")
    if seed < 0 or counter < 0 or any(not isinstance(x, int) or x < 0 for x in params):
        raise ValueError("RNG inputs must be nonnegative integers")
    payload = json.dumps(
        [EXPERIMENT_ID, purpose, list(params), seed, counter],
        separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest(), "big")


def rejection_draw(*, purpose: str, params: Sequence[int], seed: int, counter: int, n: int) -> tuple[int, int]:
    if not 1 <= n <= 1 << 256:
        raise ValueError("uniform range must be in [1, 2^256]")
    limit = ((1 << 256) // n) * n
    while True:
        value = stream_digest(purpose=purpose, params=params, seed=seed, counter=counter)
        counter += 1  # n=1 also consumes exactly one digest.
        if value < limit:
            return value % n, counter


def guarded_checkpoint(
    check: Callable[[], None] | None, index: int, phase: str,
    on_progress: Callable[[dict[str, Any]], None] | None = None, **coordinates: int,
) -> None:
    """Persist coordinates before a bounded cancellation/RSS probe.

    This helper changes no random stream or scientific arithmetic: it only
    places future machine-protection probes at deterministic loop boundaries.
    """
    if check is not None and index % CAYLEY_GUARD_STRIDE == 0:
        # Guard instances poll at a monotonic cadence.  Their ``should_probe``
        # method checks cancellation on every existing guard opportunity and
        # only returns true when this coordinate must be persisted before an
        # actual RSS probe.  Generic check callables retain the frozen stride.
        owner = getattr(check, "__self__", None)
        should_probe = getattr(owner, "should_probe", None)
        if should_probe is not None and not should_probe():
            return
        if on_progress is not None:
            on_progress({"event": "guard_probe_pending", "phase": phase, "index": index, "guard_stride": CAYLEY_GUARD_STRIDE, **coordinates})
        check()


def deterministic_shuffle(
    values: Iterable[Any], *, purpose: str, params: Sequence[int], seed: int, counter: int = 0,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[list[Any], int]:
    result = list(values)
    for ordinal, index in enumerate(range(len(result) - 1, 0, -1)):
        guarded_checkpoint(check, ordinal, "shuffle_construction", on_progress, shuffle_index=index)
        other, counter = rejection_draw(
            purpose=purpose, params=params, seed=seed, counter=counter, n=index + 1
        )
        result[index], result[other] = result[other], result[index]
    return result, counter


@dataclass(frozen=True)
class Curve:
    p: int
    A: int
    B: int

    def __post_init__(self) -> None:
        if self.p < 5:
            raise ValueError("unsupported field")
        if self.discriminant() == 0:
            raise ValueError("singular curve")

    def discriminant(self) -> int:
        return (4 * self.A**3 + 27 * self.B**2) % self.p

    def on_curve(self, point: Point) -> bool:
        return point is None or (point[1] ** 2 - (point[0] ** 3 + self.A * point[0] + self.B)) % self.p == 0

    def neg(self, point: Point) -> Point:
        return None if point is None else (point[0], (-point[1]) % self.p)

    def add(self, left: Point, right: Point) -> Point:
        if left is None:
            return right
        if right is None:
            return left
        x1, y1 = left
        x2, y2 = right
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if left == right:
            if y1 % self.p == 0:
                return None
            slope = (3 * x1 * x1 + self.A) * pow(2 * y1, -1, self.p) % self.p
        else:
            slope = (y2 - y1) * pow((x2 - x1) % self.p, -1, self.p) % self.p
        x3 = (slope * slope - x1 - x2) % self.p
        return x3, (slope * (x1 - x3) - y1) % self.p

    def scalar(self, scalar: int, point: Point) -> Point:
        if scalar < 0:
            return self.scalar(-scalar, self.neg(point))
        out: Point = None
        current = point
        while scalar:
            if scalar & 1:
                out = self.add(out, current)
            current = self.add(current, current)
            scalar >>= 1
        return out


def is_prime(value: int) -> bool:
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    return all(value % divisor for divisor in range(3, math.isqrt(value) + 1, 2))


def factor(value: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    divisor = 2
    while divisor * divisor <= value:
        exponent = 0
        while value % divisor == 0:
            value //= divisor
            exponent += 1
        if exponent:
            result.append((divisor, exponent))
        divisor = 3 if divisor == 2 else divisor + 2
    return result + ([(value, 1)] if value > 1 else [])


def count_points(curve: Curve, check: Callable[[], None] = lambda: None) -> int:
    total = 1
    for x in range(curve.p):
        check()
        rhs = (x**3 + curve.A * x + curve.B) % curve.p
        if rhs == 0:
            total += 1
        elif pow(rhs, (curve.p - 1) // 2, curve.p) == 1:
            total += 2
    return total


def is_supersingular(curve: Curve, order: int) -> bool:
    return (order - 1) % curve.p == 0


def point_key(point: Point) -> tuple[int, int, int]:
    return (0, 0, 0) if point is None else (1, point[0], point[1])


def ordered_points(curve: Curve, check: Callable[[], None] = lambda: None) -> list[Point]:
    points: list[Point] = [None]
    for x in range(curve.p):
        check()
        rhs = (x**3 + curve.A * x + curve.B) % curve.p
        for y in range(curve.p):
            if y * y % curve.p == rhs:
                points.append((x, y))
    return points


def first_primes(bits: int, count: int = 32) -> list[int]:
    found: list[int] = []
    candidate = 1 << bits
    while len(found) < count:
        if is_prime(candidate):
            found.append(candidate)
        candidate += 1
    return found


def point_json(point: Point) -> list[int] | None:
    return None if point is None else [point[0], point[1]]


def fixture_scan(
    bits: int, check: Callable[[], None], on_rejection: Callable[[dict[str, Any]], None] | None = None,
    on_selection: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Frozen lexicographic candidate scan with a durable rejection ledger.

    Singular candidates are checked before ``Curve`` construction so a singular
    B records an ordinary rejection and never aborts the rest of the frozen
    scan.  The caller stops only after the first two eligible distinct p.
    """
    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    selected_p: set[int] = set()
    for p in first_primes(bits):
        for B in range(32):
            check()
            discriminator = (4 + 27 * B * B) % p
            candidate = {"bits": bits, "p": p, "A": 1, "B": B, "discriminant": discriminator}
            if discriminator == 0:
                record = {**candidate, "reason": "singular", "certificate": {"discriminant_mod_p": 0}}
                rejected.append(record)
                if on_rejection:
                    on_rejection(record)
                continue
            curve = Curve(p, 1, B)
            order = count_points(curve, check)
            if is_supersingular(curve, order):
                record = {**candidate, "N": order, "reason": "supersingular", "certificate": {"N_minus_1_mod_p": (order - 1) % p}}
                rejected.append(record)
                if on_rejection:
                    on_rejection(record)
                continue
            eligible = [(prime, exponent) for prime, exponent in factor(order) if 127 <= prime <= 509 and prime != p and exponent == 1]
            if not eligible:
                record = {**candidate, "N": order, "reason": "no_eligible_prime_order_subgroup", "certificate": {"factorization": factor(order)}}
                rejected.append(record)
                if on_rejection:
                    on_rejection(record)
                continue
            r = max(prime for prime, _ in eligible)
            generator: Point = None
            witness: Point = None
            for point in ordered_points(curve, check)[1:]:
                projected = curve.scalar(order // r, point)
                if projected is not None and curve.scalar(r, projected) is None:
                    generator, witness = projected, point
                    break
            if generator is None:
                record = {**candidate, "N": order, "r": r, "reason": "no_nonzero_certified_generator", "certificate": {"factorization": factor(order)}}
                rejected.append(record)
                if on_rejection:
                    on_rejection(record)
                continue
            record = {
                **candidate, "N": order, "r": r, "G": point_json(generator),
                "certificate": {"witness": point_json(witness), "N_over_r": order // r, "r_times_G_is_O": True},
            }
            if p not in selected_p:
                selected.append(record)
                selected_p.add(p)
                if on_selection:
                    on_selection(record)
                if len(selected) == 2:
                    return selected, rejected
            else:
                duplicate = {**record, "reason": "duplicate_selected_field", "certificate": record["certificate"]}
                rejected.append(duplicate)
                if on_rejection:
                    on_rejection(duplicate)
    return selected, rejected


def select_fixtures(check: Callable[[], None], sink: "ProgressSink | None" = None) -> tuple[dict[int, list[dict[str, Any]]], list[dict[str, Any]]]:
    selected: dict[int, list[dict[str, Any]]] = {}
    all_rejected: list[dict[str, Any]] = []
    for bits in (9, 11):
        def record_rejection(record: dict[str, Any]) -> None:
            if sink:
                sink.record_rejection(record)

        def record_selection(record: dict[str, Any]) -> None:
            if sink:
                sink.record_fixture(record)

        rows, discards = fixture_scan(bits, check, record_rejection, record_selection)
        all_rejected.extend(discards)
        if len(rows) != 2:
            raise IncompleteFixtureStop(f"frozen fixture panel incomplete for b={bits}; no widening permitted")
        selected[bits] = rows
    return selected, all_rejected


def coordinate_transport(curve: Curve, point: Point, u: int) -> Point:
    if point is None:
        return None
    return ((u * u * point[0]) % curve.p, (u * u * u * point[1]) % curve.p)


def coordinate_curve(curve: Curve, u: int) -> Curve:
    if u % curve.p == 0:
        raise ValueError("coordinate scale must be nonzero")
    return Curve(curve.p, (u**4 * curve.A) % curve.p, (u**6 * curve.B) % curve.p)


def enumerate_subgroup(
    curve: Curve, generator: Point, r: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[list[Point], dict[str, Any]]:
    """Enumerate O,G,...,(r-1)G through one checked repeated-addition chain.

    The returned certificate is retained with each future cell.  In particular,
    the order check comes from the accumulator after exactly r additions rather
    than recomputing each multiple with scalar multiplication.
    """
    points: list[Point] = []
    current: Point = None
    for scalar in range(r):
        guarded_checkpoint(check, scalar, "subgroup_enumeration", on_progress, scalar=scalar, subgroup_order=r)
        points.append(current)
        current = curve.add(current, generator)
    certificate = {
        "method": "checked_repeated_addition",
        "enumerated_scalars": [0, r - 1],
        "points_enumerated": len(points),
        "starts_at_infinity": points[0] is None,
        "distinct": len(set(points)) == r,
        "r_times_G_is_O": current is None,
    }
    if not certificate["starts_at_infinity"] or not certificate["distinct"] or not certificate["r_times_G_is_O"]:
        raise LaunchRefused("certified prime-order subgroup check failed")
    return sorted(points, key=point_key), certificate


def subgroup_points(
    curve: Curve, generator: Point, r: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> list[Point]:
    """Compatibility wrapper for callers that only require canonical point order."""
    points, _certificate = enumerate_subgroup(curve, generator, r, check, on_progress)
    return points


def rho_step(
    curve: Curve, point: Point, G: Point, Q: Point, A: int, B: int, r: int, assignment: dict[Point, int] | None
) -> tuple[Point, int, int, str]:
    bucket = 0 if point is None else (assignment[point] if assignment is not None else point[0] % 3)
    if bucket == 0:
        return curve.add(point, G), (A + 1) % r, B, "add"
    if bucket == 1:
        return curve.add(point, Q), A, (B + 1) % r, "add"
    return curve.add(point, point), (2 * A) % r, (2 * B) % r, "double"


def binary_verifier(curve: Curve, scalar: int, G: Point) -> tuple[Point, int, int]:
    result: Point = None
    additions = 0
    doublings = 0
    for bit in bin(scalar)[2:]:
        result = curve.add(result, result)
        doublings += 1
        if bit == "1":
            result = curve.add(result, G)
            additions += 1
    return result, additions, doublings


def collision_census(
    curve: Curve, G: Point, Q: Point, r: int, assignment: dict[Point, int] | None, check: Callable[[], None],
    on_certificate: Callable[[dict[str, Any]], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    on_invalid: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """All-start census with certificate, topology, and diagnostic-cost custody.

    Each start has one first-repeat certificate.  As all r subgroup starts are
    enumerated, their traces also cover every functional-graph component, so
    the retained component sizes and cycle statistics are diagnostics of the
    executed map rather than post-hoc descriptions.
    """
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    transition_work = verification_work = additions = doublings = successes = 0
    failed_certificates = scalar_inversions = scalar_comparisons = 0
    collision_table_peak_bytes = 0
    certificates: list[dict[str, Any]] = []
    component_members: dict[tuple[int, int, int], set[Point]] = {}
    fixed_point_components: set[tuple[int, int, int]] = set()
    two_cycle_components: set[tuple[int, int, int]] = set()
    first_repeat_lengths: list[int] = []
    tail_lengths: list[int] = []
    cycle_lengths: list[int] = []
    for start in range(r):
        guarded_checkpoint(check, start, "collision_start", on_progress, start=start, subgroup_order=r)
        state, A, B = curve.scalar(start, G), start, 0
        seen: dict[Point, tuple[int, int, int]] = {state: (A, B, 0)}
        trace: list[Point] = [state]
        for step in range(1, r + 2):
            guarded_checkpoint(
                check, start * (r + 2) + step, "collision_step", on_progress,
                start=start, step=step, subgroup_order=r,
            )
            state, A, B, operation = rho_step(curve, state, G, Q, A, B, r, assignment)
            transition_work += 1
            additions += int(operation == "add")
            doublings += int(operation == "double")
            collision_table_peak_bytes = max(
                collision_table_peak_bytes,
                sys.getsizeof(seen) + sum(sys.getsizeof(key) + sys.getsizeof(value) for key, value in seen.items()),
            )
            if state not in seen:
                seen[state] = (A, B, step)
                trace.append(state)
                continue
            oldA, oldB, first_seen = seen[state]
            denominator = (B - oldB) % r
            cycle_states = trace[first_seen:]
            if not cycle_states:
                raise InfrastructureStop("first-repeat certificate has an empty cycle")
            cycle_key = min((point_key(point) for point in cycle_states))
            component_members.setdefault(cycle_key, set()).update(trace)
            cycle_length = step - first_seen
            first_repeat_lengths.append(step)
            tail_lengths.append(first_seen)
            cycle_lengths.append(cycle_length)
            if cycle_length == 1:
                fixed_point_components.add(cycle_key)
            if cycle_length == 2:
                two_cycle_components.add(cycle_key)
            certificate: dict[str, Any] = {
                "start": start, "repeat_step": step, "first_seen_step": first_seen,
                "first_repeat_length": step, "tail_length": first_seen, "cycle_length": cycle_length,
                "cycle_representative": point_json(min(cycle_states, key=point_key)),
                "delta_b": denominator, "transition_work": step,
                "verification_additions": 0, "verification_doublings": 0,
                "scalar_inversions": 0, "scalar_comparisons": 0,
            }
            if denominator == 0:
                certificate.update({"classification": "fruitless_denominator", "candidate": None, "verified": False})
            else:
                scalar_inversions += 1
                certificate["scalar_inversions"] = 1
                candidate = ((oldA - A) * pow(denominator, -1, r)) % r
                recovered, verify_adds, verify_doubles = binary_verifier(curve, candidate, G)
                verification_work += verify_adds + verify_doubles
                scalar_comparisons += 1
                certificate["scalar_comparisons"] = 1
                verified = recovered == Q
                certificate.update({
                    "candidate": candidate, "verified": verified,
                    "verification_additions": verify_adds, "verification_doublings": verify_doubles,
                    "classification": "verified_solution" if verified else "failed_certificate",
                })
                if verified:
                    successes += 1
                else:
                    failed_certificates += 1
            certificates.append(certificate)
            if on_certificate:
                on_certificate(certificate)
            if not certificate["verified"] and certificate["classification"] == "failed_certificate":
                partial = {
                    "state": "partial_invalid_cell",
                    "reason": "failed_scalar_certificate",
                    "start": start,
                    "certificate": certificate,
                }
                if on_invalid:
                    on_invalid(partial)
                raise MeasurementInvalidStop(
                    f"failed scalar certificate retained at collision start={start} step={step}"
                )
            break
        else:  # The finite functional graph bound should make this unreachable.
            raise InfrastructureStop("first-repeat bound exhausted without a collision")
    charged = transition_work + verification_work
    component_sizes = sorted(len(members) for members in component_members.values())
    secondary = {
        "mean_first_repeat_length": sum(first_repeat_lengths) / len(first_repeat_lengths),
        "useful_fraction": successes / r,
        "fixed_points": len(fixed_point_components),
        "two_cycles": len(two_cycle_components),
        "component_sizes": component_sizes,
        "max_tail_length": max(tail_lengths),
        "max_cycle_length": max(cycle_lengths),
    }
    diagnostic_costs = {
        "diagnostic_wall_seconds": time.monotonic() - started_wall,
        "diagnostic_cpu_seconds": time.process_time() - started_cpu,
        "collision_table_peak_bytes": collision_table_peak_bytes,
        "scalar_inversions": scalar_inversions,
        "scalar_comparisons": scalar_comparisons,
    }
    return {
        "starts": r, "successes": successes, "failed_certificates": failed_certificates,
        "transition_group_operations": transition_work, "verification_group_operations": verification_work,
        "group_additions": additions, "group_doublings": doublings,
        "charged_cost": None if successes == 0 else charged / successes,
        "secondary": secondary, "diagnostic_costs": diagnostic_costs,
        "certificates": certificates,
    }


def collision_census_with_custody(
    curve: Curve, G: Point, Q: Point, r: int, assignment: dict[Point, int] | None,
    check: Callable[[], None], on_certificate: Callable[[dict[str, Any]], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    on_invalid: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Named lower-level census action for the failure-retaining meter wrapper."""
    return collision_census(curve, G, Q, r, assignment, check, on_certificate, on_progress, on_invalid)


def constant_o_census(
    starts: Sequence[Point], check: Callable[[], None], on_certificate: Callable[[dict[str, Any]], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Execute the known-false reset map for every start and retain every collision.

    The first transition is the constant O map and resets labels to (0,0).  A
    non-O start repeats O on the second transition; O itself repeats on the
    first.  This is intentionally a separate census, not a Boolean assertion.
    """
    certificates: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        guarded_checkpoint(check, index, "constant_o_start", on_progress, start=index)
        seen: dict[Point, tuple[int, int, int]] = {start: (index, 0, 0)}
        state: Point = start
        A = B = 0
        for step in range(1, 3):
            guarded_checkpoint(check, index * 2 + step, "constant_o_step", on_progress, start=index, step=step)
            state = None
            A = B = 0
            if state in seen:
                oldA, oldB, first_seen = seen[state]
                denominator = (B - oldB)
                certificate = {
                    "start": index, "repeat_step": step, "first_seen_step": first_seen,
                    "old_labels": [oldA, oldB], "new_labels": [A, B],
                    "delta_b": denominator, "candidate": None, "verified": False,
                    "classification": "fruitless_denominator" if denominator == 0 else "CONTROL_FAILURE",
                }
                certificates.append(certificate)
                if on_certificate:
                    on_certificate(certificate)
                break
            seen[state] = (A, B, step)
        else:
            raise InfrastructureStop("constant-O control did not reach a repeated O")
    nonzero_denominators = sum(item["delta_b"] != 0 for item in certificates)
    solves = sum(bool(item["verified"]) for item in certificates)
    return {
        "starts": len(starts), "collisions": certificates,
        "nonzero_denominators": nonzero_denominators, "solves": solves,
        "passed": len(certificates) == len(starts) and nonzero_denominators == 0 and solves == 0,
    }


def occupancy_assignment(
    points: Sequence[Point], coordinate_values: Sequence[int], *, params: Sequence[int], seed: int,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[dict[Point, int], int]:
    if len(points) != len(coordinate_values):
        raise ValueError("occupancy inputs differ in length")
    shuffled, counter = deterministic_shuffle(
        coordinate_values, purpose="shuffle", params=params, seed=seed, counter=0,
        check=check, on_progress=on_progress,
    )
    assignment: dict[Point, int] = {}
    for index, (point, value) in enumerate(zip(points, shuffled)):
        guarded_checkpoint(check, index, "shuffle_assignment", on_progress, point_index=index)
        assignment[point] = value
    return assignment, counter


def charged_work(result: dict[str, Any]) -> int:
    return int(result["transition_group_operations"]) + int(result["verification_group_operations"])


def pooled_null_cost(results: Sequence[dict[str, Any]]) -> tuple[int, int, float | None]:
    work = sum(charged_work(row) for row in results)
    successes = sum(int(row["successes"]) for row in results)
    return work, successes, None if successes == 0 else work / successes


def cell_difference(coordinate: dict[str, Any], shuffles: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """DEC-20260907-38017a pooled-side availability; never censors a zero null arm."""
    coordinate_work = charged_work(coordinate)
    null_work, null_successes, null_cost = pooled_null_cost(shuffles)
    coordinate_successes = int(coordinate["successes"])
    available = coordinate_successes > 0 and null_successes > 0
    coordinate_cost = None if coordinate_successes == 0 else coordinate_work / coordinate_successes
    reason = None
    if coordinate_successes == 0:
        reason = "coordinate_zero_success"
    elif null_successes == 0:
        reason = "pooled_null_zero_success"
    return {
        "available": available, "unavailable_reason": reason,
        "d": math.log(null_cost / coordinate_cost) if available else None,
        "coordinate_work": coordinate_work, "coordinate_successes": coordinate_successes,
        "coordinate_cost": coordinate_cost, "pooled_null_work": null_work,
        "pooled_null_successes": null_successes, "pooled_null_cost": null_cost,
        "zero_yield_null_arms": [index + 1 for index, row in enumerate(shuffles) if int(row["successes"]) == 0],
    }


def transition_table(
    curve: Curve, points: Sequence[Point], G: Point, Q: Point, r: int, assignment: dict[Point, int],
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[dict[Point, tuple[Point, int, int, str]], dict[Point, tuple[int, int]]]:
    scalar_by_point: dict[Point, int] = {}
    for scalar in range(r):
        guarded_checkpoint(check, scalar, "relabel_scalar_table", on_progress, scalar=scalar)
        scalar_by_point[curve.scalar(scalar, G)] = scalar
    table: dict[Point, tuple[Point, int, int, str]] = {}
    labels: dict[Point, tuple[int, int]] = {}
    for point_index, point in enumerate(points):
        guarded_checkpoint(check, point_index, "relabel_transition_table", on_progress, point_index=point_index)
        scalar = scalar_by_point[point]
        next_point, next_A, next_B, operation = rho_step(curve, point, G, Q, scalar, 0, r, assignment)
        # Store action increments, not final labels, so conjugation carries the action table.
        if operation == "double":
            table[point] = (next_point, 0, 0, operation)
        else:
            table[point] = (next_point, (next_A - scalar) % r, next_B, operation)
        labels[point] = (scalar, 0)
    return table, labels


def table_first_collision(
    table: dict[Point, tuple[Point, int, int, str]], start: Point, start_label: tuple[int, int], r: int,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    start_index: int = -1,
) -> tuple[int, int, int, int, int, str]:
    state = start
    A, B = start_label
    seen = {state: (A, B, 0)}
    additions = doublings = 0
    for step in range(1, len(table) + 2):
        guarded_checkpoint(check, step, "relabel_first_collision", on_progress, start_index=start_index, step=step)
        if state not in table:
            raise ValueError("transition table is incomplete")
        state, dA, dB, operation = table[state]
        if operation == "double":
            A, B = (2 * A) % r, (2 * B) % r
            doublings += 1
        else:
            A, B = (A + dA) % r, (B + dB) % r
            additions += 1
        if state in seen:
            oldA, oldB, _ = seen[state]
            return step, additions, doublings, (B - oldB) % r, (oldA - A) % r, operation
        seen[state] = (A, B, step)
    raise InfrastructureStop("complete transition table did not repeat")


def relabel_control(
    table: dict[Point, tuple[Point, int, int, str]], labels: dict[Point, tuple[int, int]], bijection: dict[Point, Point], r: int,
    check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> bool:
    if set(bijection) != set(table) or set(bijection.values()) != set(table):
        raise ValueError("control requires a bijection on every state")
    renamed: dict[Point, tuple[Point, int, int, str]] = {}
    for state_index, (state, (next_state, dA, dB, operation)) in enumerate(table.items()):
        guarded_checkpoint(check, state_index, "relabel_bijection", on_progress, state_index=state_index)
        renamed[bijection[state]] = (bijection[next_state], dA, dB, operation)
    for start_index, state in enumerate(table):
        guarded_checkpoint(check, start_index, "relabel_all_start", on_progress, start_index=start_index)
        if table_first_collision(table, state, labels[state], r, check, on_progress, start_index) != table_first_collision(
            renamed, bijection[state], labels[state], r, check, on_progress, start_index
        ):
            return False
    return True


def _cayley_checkpoint(
    check: Callable[[], None], index: int, phase: str,
    on_progress: Callable[[dict[str, Any]], None] | None, **coordinates: int,
) -> None:
    """Persist a resumable boundary before every bounded guard probe."""
    guarded_checkpoint(check, index, phase, on_progress, **coordinates)


def cayley_weights(
    r: int, g: int, q: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> list[list[mp.mpf]]:
    """Construct the dense lazy Cayley matrix with bounded allocation checks."""
    with mp.workprec(128):
        matrix: list[list[mp.mpf]] = []
        for state in range(r):
            _cayley_checkpoint(check, state, "matrix_row_allocation", on_progress, row_index=state)
            row: list[mp.mpf] = []
            for column in range(r):
                _cayley_checkpoint(check, column, "matrix_column_allocation", on_progress, row_index=state, column_index=column)
                row.append(mp.mpf(0))
            row[state] += mp.mpf("0.5")
            for delta in (g, -g, q, -q):
                row[(state + delta) % r] += mp.mpf("0.125")
            matrix.append(row)
        return matrix


def cayley_fourier_eigenvalues(
    r: int, g: int, q: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> list[mp.mpf]:
    with mp.workprec(128):
        values: list[mp.mpf] = []
        for index in range(r):
            _cayley_checkpoint(check, index, "fourier_eigenvalues", on_progress, frequency=index)
            values.append(
                mp.mpf("0.5") + mp.mpf("0.25") * mp.cos(2 * mp.pi * index * g / r)
                + mp.mpf("0.25") * mp.cos(2 * mp.pi * index * q / r)
            )
        return values


def cayley_tv_curve(
    r: int, g: int, q: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
    matrix: list[list[mp.mpf]] | None = None, lambdas: list[mp.mpf] | None = None,
) -> dict[str, Any]:
    steps = (0, 1, 2, 4, 8, 16, 32)
    with mp.workprec(128):
        matrix = matrix if matrix is not None else cayley_weights(r, g, q, check, on_progress)
        lambdas = lambdas if lambdas is not None else cayley_fourier_eigenvalues(r, g, q, check, on_progress)
        values: dict[str, Any] = {}
        for requested in steps:
            _cayley_checkpoint(check, requested, "tv_step", on_progress, requested_step=requested)
            distribution: list[mp.mpf] = []
            for index in range(r):
                _cayley_checkpoint(check, index, "distribution_allocation", on_progress, requested_step=requested)
                distribution.append(mp.mpf(int(index == 0)))
            for iteration in range(requested):
                _cayley_checkpoint(check, iteration, "matrix_vector_iteration", on_progress, requested_step=requested, iteration=iteration)
                next_distribution: list[mp.mpf] = []
                for destination in range(r):
                    _cayley_checkpoint(check, destination, "matrix_vector_destination", on_progress, requested_step=requested, iteration=iteration, destination=destination)
                    total = mp.mpf(0)
                    for origin in range(r):
                        _cayley_checkpoint(check, origin, "matrix_vector_origin", on_progress, requested_step=requested, iteration=iteration, destination=destination, origin=origin)
                        total += matrix[origin][destination] * distribution[origin]
                    next_distribution.append(total)
                distribution = next_distribution
            inverse: list[mp.mpf] = []
            for state in range(r):
                _cayley_checkpoint(check, state, "inverse_fourier_state", on_progress, requested_step=requested, state=state)
                total = mp.mpf(0)
                for index in range(r):
                    _cayley_checkpoint(check, index, "inverse_fourier_frequency", on_progress, requested_step=requested, state=state, frequency=index)
                    total += (lambdas[index] ** requested) * mp.e ** (2j * mp.pi * index * state / r)
                inverse.append(total.real / r)
            discrepancy = mp.mpf(0)
            point_tv = mp.mpf(0)
            inverse_tv = mp.mpf(0)
            uniform = mp.mpf(1) / r
            for index, (left, right) in enumerate(zip(distribution, inverse)):
                _cayley_checkpoint(check, index, "total_variation_reduction", on_progress, requested_step=requested, state_index=index)
                discrepancy += abs(left - right)
                point_tv += abs(left - uniform)
                inverse_tv += abs(right - uniform)
            values[str(requested)] = {
                "point_basis_tv": str(mp.mpf("0.5") * point_tv),
                "inverse_fourier_tv": str(mp.mpf("0.5") * inverse_tv),
                "basis_vs_inverse_tv_discrepancy": str(mp.mpf("0.5") * discrepancy),
            }
        return values


def cayley_control(
    r: int, g: int, q: int, check: Callable[[], None],
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Actual reversible Cayley calibration, separate from the rho transition graph."""
    with mp.workprec(128):
        matrix = cayley_weights(r, g, q, check, on_progress)
        rows: list[mp.mpf] = []
        columns: list[mp.mpf] = []
        for row_index in range(r):
            _cayley_checkpoint(check, row_index, "row_reduction", on_progress, row_index=row_index)
            row_total = mp.mpf(0)
            for column_index in range(r):
                _cayley_checkpoint(check, column_index, "row_reduction_column", on_progress, row_index=row_index, column_index=column_index)
                row_total += matrix[row_index][column_index]
            rows.append(row_total)
        for column_index in range(r):
            _cayley_checkpoint(check, column_index, "column_reduction", on_progress, column_index=column_index)
            column_total = mp.mpf(0)
            for row_index in range(r):
                _cayley_checkpoint(check, row_index, "column_reduction_row", on_progress, row_index=row_index, column_index=column_index)
                column_total += matrix[row_index][column_index]
            columns.append(column_total)
        expected = cayley_fourier_eigenvalues(r, g, q, check, on_progress)
        # Direct DFT of the first transition row independently checks the formula.
        actual: list[mp.mpf] = []
        for frequency in range(r):
            _cayley_checkpoint(check, frequency, "direct_dft_frequency", on_progress, frequency=frequency)
            total = mp.mpf(0)
            for state in range(r):
                _cayley_checkpoint(check, state, "direct_dft_state", on_progress, frequency=frequency, state=state)
                total += matrix[0][state] * mp.e ** (2j * mp.pi * frequency * state / r)
            actual.append(total.real)
        row_error = max(abs(value - 1) for value in rows + columns)
        eigen_error = max(abs(left - right) for left, right in zip(sorted(actual), sorted(expected)))
        tv = cayley_tv_curve(r, g, q, check, on_progress, matrix, expected)
        tv_error = max(mp.mpf(item["basis_vs_inverse_tv_discrepancy"]) for item in tv.values())
        gap = mp.mpf(1) - max(expected[1:])
        passed = row_error <= mp.mpf("1e-12") and eigen_error <= mp.mpf("1e-10") and tv_error <= mp.mpf("1e-10")
        return {
            "passed": bool(passed), "row_column_error": str(row_error), "eigenvalue_multiset_error": str(eigen_error),
            "max_basis_vs_inverse_tv_discrepancy": str(tv_error), "gap": str(gap), "workprec_bits": 128,
            "guard_stride": CAYLEY_GUARD_STRIDE, "total_variation": tv,
        }


def reduce_validity(coordinate: dict[str, Any], shuffles: Sequence[dict[str, Any]], controls: dict[str, Any]) -> dict[str, Any]:
    certificate_failures = int(coordinate["failed_certificates"]) + sum(int(row["failed_certificates"]) for row in shuffles)
    required_controls = {
        "cayley_exact": bool(controls["cayley"]["passed"]),
        "relabel": bool(controls["relabel"]),
        "occupancy": bool(controls["occupancy"]),
        "constant_o_no_nonzero_denominator": bool(controls["known_false"]["constant_o"]["nonzero_denominators"] == 0),
        "constant_o_zero_solves": bool(controls["known_false"]["constant_o"]["solves"] == 0),
        "mutated_candidate_fails_certificate": bool(controls["known_false"]["mutated_candidate_fails_certificate"]),
    }
    failed_controls = [name for name, passed in required_controls.items() if not passed]
    return {
        "valid": certificate_failures == 0 and not failed_controls,
        "certificate_failures": certificate_failures, "failed_controls": failed_controls,
        "control_results": required_controls,
    }


def fixture_to_curve(record: dict[str, Any]) -> tuple[Curve, Point, int]:
    curve = Curve(int(record["p"]), int(record["A"]), int(record["B"]))
    raw = record["G"]
    generator: Point = None if raw is None else (int(raw[0]), int(raw[1]))
    return curve, generator, int(record["r"])


def measured_diagnostic(
    name: str, action: Callable[[], Any],
    on_record: Callable[[dict[str, Any]], None] | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Return a prospective result and one custody row with actual RSS observations."""
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    try:
        rss_started = process_group_rss_bytes()
    except InfrastructureStop as telemetry_error:
        failed = {
            "diagnostic": name,
            "diagnostic_wall_seconds": time.monotonic() - started_wall,
            "diagnostic_cpu_seconds": time.process_time() - started_cpu,
            "completed": False,
            "error": f"{type(telemetry_error).__name__}: {telemetry_error}",
            "process_group_rss_error": "unavailable_before_diagnostic",
        }
        if on_record:
            on_record(failed)
        raise
    try:
        result = action()
    except Exception as exc:
        try:
            rss_ended = process_group_rss_bytes()
        except InfrastructureStop as telemetry_error:
            failed = {
                "diagnostic": name,
                "diagnostic_wall_seconds": time.monotonic() - started_wall,
                "diagnostic_cpu_seconds": time.process_time() - started_cpu,
                "completed": False,
                "error": f"{type(exc).__name__}: {exc}",
                "process_group_rss_start_bytes": rss_started,
                "process_group_rss_error": f"unavailable_after_interruption: {telemetry_error}",
            }
            if on_record:
                on_record(failed)
            raise InfrastructureStop(
                f"process-group RSS unavailable after interrupted diagnostic {name}: {telemetry_error}"
            ) from telemetry_error
        failed = {
            "diagnostic": name,
            "diagnostic_wall_seconds": time.monotonic() - started_wall,
            "diagnostic_cpu_seconds": time.process_time() - started_cpu,
            "completed": False,
            "error": f"{type(exc).__name__}: {exc}",
            "process_group_rss_start_bytes": rss_started,
            "process_group_rss_end_bytes": rss_ended,
            "process_group_rss_boundary_sample_max_bytes": max(rss_started, rss_ended),
            "process_group_rss_sample_scope": "diagnostic_start_and_end_boundaries",
            "process_group_rss_sample_cadence": "one_start_one_end",
        }
        if on_record:
            on_record(failed)
        raise
    try:
        rss_ended = process_group_rss_bytes()
    except InfrastructureStop as telemetry_error:
        failed = {
            "diagnostic": name,
            "diagnostic_wall_seconds": time.monotonic() - started_wall,
            "diagnostic_cpu_seconds": time.process_time() - started_cpu,
            "completed": False,
            "error": f"{type(telemetry_error).__name__}: {telemetry_error}",
            "process_group_rss_start_bytes": rss_started,
            "process_group_rss_error": "unavailable_after_diagnostic",
        }
        if on_record:
            on_record(failed)
        raise
    record = {
        "diagnostic": name,
        "diagnostic_wall_seconds": time.monotonic() - started_wall,
        "diagnostic_cpu_seconds": time.process_time() - started_cpu,
        "completed": True,
        "process_group_rss_start_bytes": rss_started,
        "process_group_rss_end_bytes": rss_ended,
        "process_group_rss_boundary_sample_max_bytes": max(rss_started, rss_ended),
        "process_group_rss_sample_scope": "diagnostic_start_and_end_boundaries",
        "process_group_rss_sample_cadence": "one_start_one_end",
    }
    if on_record:
        on_record(record)
    return result, record


def future_cell(
    fixture: dict[str, Any], seed: int, u: int, check: Callable[[], None],
    on_partial: Callable[[str, int, dict[str, Any]], None] | None = None,
    on_diagnostic: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    curve, G, r = fixture_to_curve(fixture)
    target_params = (curve.p, curve.A, curve.B, r, 0, 0, 0)
    target, _ = rejection_draw(purpose="target", params=target_params, seed=seed, counter=0, n=r - 1)
    target += 1
    Q = curve.scalar(target, G)
    transported_curve = coordinate_curve(curve, u)
    transported_G = coordinate_transport(curve, G, u)
    transported_Q = coordinate_transport(curve, Q, u)
    subgroup_progress = lambda state: on_partial("subgroup", 0, state) if on_partial else None
    (points, subgroup_certificate), subgroup_cost = measured_diagnostic(
        "subgroup_enumeration",
        lambda: enumerate_subgroup(transported_curve, transported_G, r, check, subgroup_progress),
        on_diagnostic,
    )

    coordinate_progress = lambda state: on_partial("coordinate_partition", 0, state) if on_partial else None

    def coordinate_partition() -> dict[Point, int]:
        values: dict[Point, int] = {}
        for point_index, point in enumerate(points):
            guarded_checkpoint(
                check, point_index, "coordinate_partition", coordinate_progress,
                point_index=point_index, subgroup_order=r,
            )
            values[point] = 0 if point is None else point[0] % 3
        return values

    coordinate, partition_cost = measured_diagnostic("coordinate_partition_queries", coordinate_partition, on_diagnostic)
    partition_cost["partition_queries"] = len(points)
    curve_id = f"p{curve.p}-B{curve.B}"
    coordinate_result, coordinate_census_cost = measured_diagnostic(
        "coordinate_collision_census",
        lambda: collision_census_with_custody(
            transported_curve, transported_G, transported_Q, r, coordinate, check,
            lambda certificate: on_partial("coordinate", 0, certificate) if on_partial else None,
            lambda state: on_partial("coordinate_collision", 0, state) if on_partial else None,
            lambda partial: on_partial("invalid_cell", 0, partial) if on_partial else None,
        ),
        on_diagnostic,
    )
    coordinate_result["diagnostic_meter"] = coordinate_census_cost
    coordinate_values = [coordinate[point] for point in points]
    shuffles: list[dict[str, Any]] = []
    shuffle_costs: list[dict[str, Any]] = []
    for arm in range(1, 8):
        guarded_checkpoint(
            check, arm, "shuffle_arm", lambda state, arm=arm: on_partial("shuffle_arm", arm, state) if on_partial else None,
            arm=arm, subgroup_order=r,
        )
        params = (curve.p, curve.A, curve.B, r, 0, u, arm)
        shuffle_progress = lambda state, arm=arm: on_partial("shuffle", arm, state) if on_partial else None
        (assignment, consumed), shuffle_cost = measured_diagnostic(
            "shuffle_construction",
            lambda: occupancy_assignment(points, coordinate_values, params=params, seed=seed, check=check, on_progress=shuffle_progress),
            on_diagnostic,
        )
        shuffle_cost.update({"arm": arm, "partition_queries": len(points), "rng_counter_end": consumed})
        shuffle_costs.append(shuffle_cost)
        result, collision_meter = measured_diagnostic(
            f"null_collision_census_arm_{arm}",
            lambda arm=arm: collision_census_with_custody(
                transported_curve, transported_G, transported_Q, r, assignment, check,
                lambda certificate: on_partial("null", arm, certificate) if on_partial else None,
                lambda state: on_partial("null_collision", arm, state) if on_partial else None,
                lambda partial: on_partial("invalid_cell", arm, partial) if on_partial else None,
            ),
            on_diagnostic,
        )
        result["diagnostic_meter"] = collision_meter
        result["arm"] = arm
        result["rng_counter_end"] = consumed
        result["bucket_counts"] = [sum(value == bucket for value in assignment.values()) for bucket in range(3)]
        shuffles.append(result)
    expected_bucket_counts = [sum(value == bucket for value in coordinate.values()) for bucket in range(3)]
    occupancy_result = {"occupancy": all(row["bucket_counts"] == expected_bucket_counts for row in shuffles)}
    if not occupancy_result["occupancy"]:
        partial = {
            "state": "partial_invalid_cell", "reason": "occupancy_control_failed",
            "expected_bucket_counts": expected_bucket_counts,
            "observed_bucket_counts": [row["bucket_counts"] for row in shuffles],
        }
        if on_partial:
            on_partial("invalid_cell", 0, partial)
        raise MeasurementInvalidStop("occupancy control failed after seven completed shuffle assignments")
    control_progress = lambda state: on_partial("relabel", 0, state) if on_partial else None
    (table, labels), relabel_table_cost = measured_diagnostic(
        "relabel_table",
        lambda: transition_table(transported_curve, points, transported_G, transported_Q, r, coordinate, check, control_progress),
        on_diagnostic,
    )
    permutation, _ = deterministic_shuffle(
        points, purpose="control", params=(curve.p, curve.A, curve.B, r, 0, 0, 0), seed=seed,
        check=check, on_progress=control_progress,
    )
    relabel, relabel_cost = measured_diagnostic(
        "relabel_control",
        lambda: relabel_control(table, labels, dict(zip(points, permutation)), r, check, control_progress),
        on_diagnostic,
    )
    if not relabel:
        partial = {
            "state": "partial_invalid_cell", "reason": "exact_relabel_control_failed",
            "relabel": False,
        }
        if on_partial:
            on_partial("invalid_cell", 0, partial)
        raise MeasurementInvalidStop("exact relabel control failed before later controls")
    constant_o, constant_o_cost = measured_diagnostic(
        "constant_o_census",
        lambda: constant_o_census(
            points, check,
            lambda certificate: on_partial("constant_o", 0, certificate) if on_partial else None,
            control_progress,
        ),
        on_diagnostic,
    )
    (mutated, _, _), mutated_verifier_cost = measured_diagnostic(
        "mutated_verifier",
        lambda: binary_verifier(transported_curve, (target + 1) % r, transported_G),
        on_diagnostic,
    )
    cayley, cayley_cost = measured_diagnostic(
        "cayley_control",
        lambda: cayley_control(
            r, 1, target, check,
            lambda state: on_partial("cayley_progress", -1, state) if on_partial else None,
        ),
        on_diagnostic,
    )
    controls = {
        "cayley": cayley, "relabel": relabel,
        "occupancy": occupancy_result["occupancy"],
        "known_false": {"constant_o": constant_o, "mutated_candidate_fails_certificate": mutated != transported_Q},
    }
    validity = reduce_validity(coordinate_result, shuffles, controls)
    metric = cell_difference(coordinate_result, shuffles)
    return {
        "curve_id": curve_id, "seed": seed, "u": u,
        "metric": metric, "coordinate": coordinate_result, "nulls": shuffles, "controls": controls, "validity": validity,
        "subgroup_enumeration": subgroup_certificate,
        "diagnostic_costs": {
            "subgroup_enumeration": subgroup_cost,
            "coordinate_partition_queries": partition_cost,
            "shuffle_construction": shuffle_costs,
            "relabel_table": relabel_table_cost,
            "relabel_control": relabel_cost,
            "constant_o_census": constant_o_cost,
            "mutated_verifier": mutated_verifier_cost,
            "cayley_control": cayley_cost,
        },
    }


def global_decision(cells: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Exact all-u finite decision; no best-coordinate selection or pooling across u."""
    expected = {(curve, seed, u) for curve in {row.get("curve_id") for row in cells} for seed in HELDOUT_SEEDS for u in US}
    present = {(row.get("curve_id"), row.get("seed"), row.get("u")) for row in cells}
    reasons: list[str] = []
    if len(cells) != 96 or len({row.get("curve_id") for row in cells}) != 4 or present != expected:
        reasons.append("incomplete_or_wrong_heldout_panel")
    if any(not row.get("validity", {}).get("valid") for row in cells):
        reasons.append("invalid_certificate_or_control")
    unavailable = any(not row.get("metric", {}).get("available") for row in cells)
    per_u: dict[str, Any] = {}
    if reasons:
        return {"branch": "inconclusive", "reasons": reasons, "per_u": per_u, "panel_valid": False}
    if unavailable:
        return {"branch": "inconclusive", "reasons": ["unavailable_inferential_cell"], "per_u": per_u, "panel_valid": True}
    threshold = math.log(1.20)
    for u in US:
        subset = [row for row in cells if row["u"] == u]
        curve_ids = sorted({row["curve_id"] for row in subset})
        overall = sum(float(row["metric"]["d"]) for row in subset) / 32
        curve_means = {curve_id: sum(float(row["metric"]["d"]) for row in subset if row["curve_id"] == curve_id) / 8 for curve_id in curve_ids}
        per_u[str(u)] = {
            "overall_mean_d": overall, "curve_mean_d": curve_means,
            "positive": overall >= threshold and all(value > 0 for value in curve_means.values()),
            "negative": all(float(row["metric"]["d"]) <= 0 for row in subset),
        }
    if all(row["positive"] for row in per_u.values()):
        branch = "positive"
    elif all(row["negative"] for row in per_u.values()):
        branch = "negative"
    else:
        branch = "inconclusive"
    return {"branch": branch, "reasons": [], "per_u": per_u, "threshold_log_1_20": threshold, "panel_valid": True}


@dataclass
class ResourceMeter:
    started_at_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_wall: float = field(default_factory=time.monotonic)
    started_cpu: float = field(default_factory=time.process_time)
    finished_at_utc: datetime | None = None
    finished_wall: float | None = None
    finished_cpu: float | None = None
    stages: dict[str, dict[str, float]] = field(default_factory=dict)

    def enter(self, name: str) -> float:
        self.stages[name] = {"wall_started": time.monotonic(), "cpu_started": time.process_time()}
        return self.stages[name]["wall_started"]

    def exit(self, name: str) -> None:
        stage = self.stages[name]
        stage["wall_seconds"] = time.monotonic() - stage.pop("wall_started")
        stage["cpu_seconds"] = time.process_time() - stage.pop("cpu_started")

    def close_active(self) -> None:
        """Record the current partial stage before a cancellation/failure package."""
        for name, stage in self.stages.items():
            if "wall_started" in stage:
                stage["wall_seconds"] = time.monotonic() - stage.pop("wall_started")
                stage["cpu_seconds"] = time.process_time() - stage.pop("cpu_started")

    def finish(self) -> None:
        """Capture the terminal UTC/monotonic/CPU bracket exactly once."""
        if self.finished_wall is None:
            self.finished_at_utc = datetime.now(timezone.utc)
            self.finished_wall = time.monotonic()
            self.finished_cpu = time.process_time()

    def snapshot(self, *, finish: bool = True) -> dict[str, Any]:
        """Return a terminal or explicitly intermediate timing observation."""
        if finish:
            self.finish()
        observed_at = self.finished_at_utc or datetime.now(timezone.utc)
        observed_wall = self.finished_wall if self.finished_wall is not None else time.monotonic()
        observed_cpu = self.finished_cpu if self.finished_cpu is not None else time.process_time()
        return {
            "wall_seconds": observed_wall - self.started_wall,
            "cpu_seconds": observed_cpu - self.started_cpu,
            "timing": {
                "started_at": self.started_at_utc.isoformat(),
                "observed_at": observed_at.isoformat(),
                "monotonic_started": self.started_wall,
                "monotonic_observed": observed_wall,
                "utc_interval_seconds": (observed_at - self.started_at_utc).total_seconds(),
                "terminal": self.finished_wall is not None,
            },
            "stages": self.stages,
        }


def process_group_rss_bytes() -> int:
    """Sum RSS of the current process group; failure is an infrastructure stop."""
    pgid = os.getpgid(0)
    current_pid = os.getpid()
    try:
        output = subprocess.run(
            ["ps", "-axo", "pid=,pgid=,rss="], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InfrastructureStop(f"cannot measure process-group RSS: {exc}") from exc
    total_kib = 0
    group_rows = 0
    current_row = False
    for line in output.splitlines():
        parts = line.split()
        if len(parts) != 3:
            raise InfrastructureStop("process-group RSS measurement has a malformed row")
        try:
            pid, row_pgid, rss_kib = (int(value) for value in parts)
        except ValueError as exc:
            raise InfrastructureStop("process-group RSS measurement has a nonnumeric row") from exc
        if pid <= 0 or row_pgid <= 0 or rss_kib < 0:
            raise InfrastructureStop("process-group RSS measurement has an invalid row")
        if pid == current_pid:
            if row_pgid != pgid:
                raise InfrastructureStop("current process RSS row does not match current process group")
            current_row = True
        if row_pgid == pgid:
            group_rows += 1
            total_kib += rss_kib
    if not current_row:
        raise InfrastructureStop("process-group RSS measurement lacks the current process row")
    if group_rows == 0:
        raise InfrastructureStop("process-group RSS measurement lacks a matching process-group row")
    return total_kib * 1024


@dataclass
class ProgressSink:
    staging: Path
    fixtures: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    cells: list[dict[str, Any]] = field(default_factory=list)
    partial_certificates: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)
    progress_event_count: int = 0
    progress_bytes: int = 0
    latest_checkpoint_bytes: int = 0

    def _append(self, name: str, record: dict[str, Any]) -> None:
        target = self.staging / name
        encoded = canonical_json(record) + b"\n"
        with target.open("ab") as handle:
            for offset in range(0, len(encoded), MAX_SERIALIZATION_CHUNK_BYTES):
                handle.write(encoded[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])
            handle.flush()
            os.fsync(handle.fileno())

    def record_rejection(self, record: dict[str, Any]) -> None:
        self.rejected.append(record)
        self._append("fixture-rejections.jsonl", record)
        self.checkpoint("fixture_rejected")

    def record_fixture(self, record: dict[str, Any]) -> None:
        self.fixtures.append(record)
        self._append("fixture-selections.jsonl", record)
        self.checkpoint("fixture_selected")

    def record_partial(self, record: dict[str, Any]) -> None:
        self.partial_certificates.append(record)
        self._append("partial-certificates.jsonl", record)
        self.checkpoint("partial_certificate_retained", {"state": record.get("state", "partial_certificate")})

    def record_cell(self, record: dict[str, Any]) -> None:
        self.cells.append(record)
        self._append("completed-cells.jsonl", record)
        self.checkpoint("cell_completed")

    def record_diagnostic(self, record: dict[str, Any]) -> None:
        """Retain a completed or interrupted diagnostic cost before later work."""
        self.diagnostics.append(record)
        self._append("diagnostics.jsonl", record)
        self.checkpoint("diagnostic_recorded")

    def record_progress(self, record: dict[str, Any]) -> None:
        """Append a bounded operational event then replace one compact latest state.

        Progress is deliberately not a certificate stream.  Each record is
        bounded before it reaches disk; the append-only log is linear in event
        count and the compact state is rewritten independently of its history.
        """
        encoded = canonical_json(record) + b"\n"
        if len(encoded) > MAX_PROGRESS_EVENT_BYTES:
            raise ResourceStop(
                f"progress event is {len(encoded)} bytes; cap is {MAX_PROGRESS_EVENT_BYTES}"
            )
        projected = self.progress_bytes + len(encoded)
        if projected > MAX_PROGRESS_LOG_BYTES:
            raise ResourceStop(
                f"progress event log would exceed {MAX_PROGRESS_LOG_BYTES} bytes"
            )
        path = self.staging / "progress-events.jsonl"
        with path.open("ab") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        self.progress_event_count += 1
        self.progress_bytes = projected
        latest = {
            "schema": "crypto.autoresearch.progress_latest.v1",
            "event": record.get("event", "progress"),
            "phase": record.get("phase"),
            "coordinates": {key: value for key, value in record.items() if key not in {"event", "phase", "at"}},
            "at": record.get("at", datetime.now(timezone.utc).isoformat()),
            "counts": {
                "fixtures": len(self.fixtures), "rejected": len(self.rejected),
                "cells": len(self.cells), "partial_certificates": len(self.partial_certificates),
                "diagnostics": len(self.diagnostics), "progress_events": self.progress_event_count,
                "progress_bytes": self.progress_bytes,
            },
        }
        latest_bytes = canonical_json(latest) + b"\n"
        if len(latest_bytes) > MAX_PROGRESS_LATEST_BYTES:
            raise ResourceStop(
                f"progress latest checkpoint is {len(latest_bytes)} bytes; cap is {MAX_PROGRESS_LATEST_BYTES}"
            )
        temporary = self.staging / ".progress-latest.tmp"
        target = self.staging / "progress-latest.json"
        with temporary.open("wb") as handle:
            for offset in range(0, len(latest_bytes), MAX_SERIALIZATION_CHUNK_BYTES):
                handle.write(latest_bytes[offset:offset + MAX_SERIALIZATION_CHUNK_BYTES])
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        fsync_directory(self.staging)
        self.latest_checkpoint_bytes = len(latest_bytes)

    def checkpoint(self, event: str, coordinates: dict[str, Any] | None = None) -> None:
        self.record_progress({"event": event, "at": datetime.now(timezone.utc).isoformat(), **(coordinates or {})})


@dataclass
class Guard:
    sink: ProgressSink
    cancelled: bool = False
    limit_bytes: int = MEMORY_LIMIT_BYTES
    last_poll_monotonic: float | None = None
    guard_requests: int = 0
    actual_polls: int = 0
    sampled_process_group_max_bytes: int | None = None
    _probe_pending: bool = False

    def should_probe(self) -> bool:
        """Check signals on every opportunity and throttle RSS reads to 250ms."""
        self.guard_requests += 1
        if self.cancelled:
            raise CancellationStop("operator cancellation observed")
        now = time.monotonic()
        if self.last_poll_monotonic is None or now - self.last_poll_monotonic >= MAX_GUARD_POLL_INTERVAL_SECONDS:
            self._probe_pending = True
            return True
        return False

    def check(self, *, force: bool = False) -> None:
        if force:
            self.guard_requests += 1
            if self.cancelled:
                raise CancellationStop("operator cancellation observed")
            self._probe_pending = True
        elif not self._probe_pending and not self.should_probe():
            return
        rss = process_group_rss_bytes()
        self.actual_polls += 1
        self.last_poll_monotonic = time.monotonic()
        self._probe_pending = False
        self.sampled_process_group_max_bytes = max(
            rss, self.sampled_process_group_max_bytes or rss,
        )
        if rss > self.limit_bytes:
            raise ResourceStop(f"process-group RSS {rss} exceeds {self.limit_bytes}")

    def telemetry(self) -> dict[str, Any]:
        return {
            "guard_requests": self.guard_requests,
            "actual_polls": self.actual_polls,
            "sampled_process_group_max_bytes": self.sampled_process_group_max_bytes,
            "sample_scope": "process_group_kernel_rss_at_guard_polls",
            "maximum_poll_interval_seconds": MAX_GUARD_POLL_INTERVAL_SECONDS,
            "cadence_limit_note": "A monotonic wall cadence samples eligible guard opportunities; it is not a real-time scheduling guarantee.",
        }


def git_output(*args: str) -> str:
    try:
        return subprocess.run(["git", "-C", str(ROOT), *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InfrastructureStop(f"repository provenance unavailable: {' '.join(args)}: {exc}") from exc


def execution_provenance(command: str) -> dict[str, Any]:
    commit = git_output("rev-parse", "HEAD")
    dirty = bool(git_output("status", "--porcelain"))
    return {
        "commit": commit, "dirty": dirty, "command": command,
        "source_sha256": {"specification.yaml": sha256_file(SPEC_PATH), "amendment.yaml": sha256_file(AMENDMENT_PATH), "driver.py": sha256_file(Path(__file__)), "execution-plan.json": sha256_file(PLAN_PATH)},
    }


def runtime_binding() -> dict[str, Any]:
    return {"python": sys.version.split()[0], "implementation": platform.python_implementation(), "system": platform.system(), "machine": platform.machine()}


def lock_payload(lock: dict[str, Any]) -> bytes:
    body = dict(lock)
    body.pop("signature", None)
    return canonical_json(body)


def verify_signature(public_key_b64: str, signature_b64: str, payload: bytes) -> None:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(base64.b64decode(public_key_b64, validate=True)).verify(base64.b64decode(signature_b64, validate=True), payload)
    except Exception as exc:  # cryptographic library exposes several exception classes
        raise LaunchRefused("Coordinator lock Ed25519 signature verification failed") from exc


def git_blob_bytes(commit: str, relative_path: str) -> bytes:
    try:
        return subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{relative_path}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LaunchRefused(f"archive commit does not contain {relative_path}") from exc


def git_blob_hash(commit: str, relative_path: str) -> str:
    return sha256_bytes(git_blob_bytes(commit, relative_path))


def git_commit_parent(commit: str) -> str:
    return git_output("rev-parse", f"{commit}^")


def git_changed_paths(commit: str) -> set[str]:
    return set(filter(None, git_output("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()))


def require_commit_ancestor(ancestor: str, descendant: str, description: str) -> None:
    try:
        subprocess.run(
            ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", ancestor, descendant],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LaunchRefused(f"required ancestry is absent: {description}") from exc


def require_commit_precedes(earlier: str, later: str, description: str) -> None:
    """Require a real lifecycle transition, never equality by accident."""
    if earlier == later:
        raise LaunchRefused(f"required lifecycle transition collapsed to one commit: {description}")
    require_commit_ancestor(earlier, later, description)


def _required_text(mapping: dict[str, Any], field: str, label: str) -> str:
    value = mapping.get(field)
    if not isinstance(value, str) or not value:
        raise LaunchRefused(f"{label}.{field} must be nonempty text")
    return value


def _required_paths(mapping: dict[str, Any], field: str, label: str) -> list[str]:
    value = mapping.get(field)
    if not isinstance(value, list) or not value or len(set(value)) != len(value):
        raise LaunchRefused(f"{label}.{field} must be a nonempty unique path list")
    paths: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item:
            raise LaunchRefused(f"{label}.{field} contains a non-text path")
        parsed = Path(item)
        if parsed.is_absolute() or ".." in parsed.parts or parsed.as_posix() != item:
            raise LaunchRefused(f"{label}.{field} contains an unsafe repository-relative path")
        paths.append(item)
    return paths


def validate_complete_review_handoff(handoff: Any, task_id: str) -> dict[str, Any]:
    """Validate the whole queue-embedded review envelope before admission.

    The canonical dispatcher and write-once lane implementation are pinned in
    ``verify_review_admission``.  This read-only structural mirror prevents a
    future lock from accepting a hand-written reduced task while avoiding any
    command execution or queue mutation during launch admission.
    """
    if not isinstance(handoff, dict):
        raise LaunchRefused("review task handoff is not a mapping")
    for field in ("id", "from", "to", "objective", "uncertainty_reduced", "archived_by"):
        _required_text(handoff, field, "review handoff")
    if handoff["id"] != task_id or handoff["to"] != "validator":
        raise LaunchRefused("review handoff does not bind the validator task id")
    inputs = _required_paths(handoff, "inputs", "review handoff")
    deliverables = _required_paths(handoff, "deliverables", "review handoff")
    write_scope = _required_paths(handoff, "write_scope", "review handoff")
    artifact_paths = _required_paths(handoff, "artifact_paths", "review handoff")
    if deliverables != write_scope or deliverables != artifact_paths:
        raise LaunchRefused("review handoff deliverables, scope, and artifact paths disagree")
    bindings = handoff.get("source_bindings")
    if not isinstance(bindings, list) or len(bindings) != len(inputs):
        raise LaunchRefused("review handoff lacks one source binding for every input")
    binding_paths: list[str] = []
    for row in bindings:
        if not isinstance(row, dict) or set(row) != {"path", "sha256"}:
            raise LaunchRefused("review handoff source binding does not use the pinned schema")
        path = row["path"]
        if not isinstance(path, str) or not isinstance(row["sha256"], str) or re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is None:
            raise LaunchRefused("review handoff source binding is malformed")
        binding_paths.append(path)
    if binding_paths != inputs:
        raise LaunchRefused("review handoff source bindings do not exactly cover inputs in order")
    for field in ("constraints", "completion_gate"):
        if not isinstance(handoff.get(field), list) or not handoff[field] or not all(isinstance(item, str) and item for item in handoff[field]):
            raise LaunchRefused(f"review handoff.{field} must be a nonempty text list")
    budget = handoff.get("budget")
    if not isinstance(budget, dict) or not {"wall_clock_seconds", "memory_gb", "maximum_runs"}.issubset(budget):
        raise LaunchRefused("review handoff lacks the complete budget envelope")
    inference = handoff.get("inference")
    if not isinstance(inference, dict) or inference.get("policy") != "review-adversarial" or inference.get("reasoning_effort") != "xhigh" or inference.get("independent_session_required") is not True or inference.get("fallback_allowed") is not False or inference.get("degraded_allowed") is not False:
        raise LaunchRefused("review handoff lacks the exact independent review envelope")
    return handoff


def validate_governed_review_queue(queue: Any, review_task_id: str, archive_task_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    if not isinstance(queue, dict) or queue.get("schema") != "crypto.autoresearch.dispatch_queue.v1":
        raise LaunchRefused("external authority queue does not use the canonical dispatch schema")
    if not isinstance(queue.get("objective"), str) or not queue["objective"] or not isinstance(queue.get("max_concurrent"), int) or queue["max_concurrent"] < 1:
        raise LaunchRefused("external authority queue lacks its governed objective or concurrency limit")
    tasks = queue.get("tasks")
    if not isinstance(tasks, list) or not tasks or any(not isinstance(item, dict) for item in tasks):
        raise LaunchRefused("external authority queue has no governed task list")
    identifiers = [item.get("id") for item in tasks]
    if len(set(identifiers)) != len(identifiers):
        raise LaunchRefused("external authority queue has duplicate task identifiers")
    review = next((item for item in tasks if item.get("id") == review_task_id), None)
    archive = next((item for item in tasks if item.get("id") == archive_task_id), None)
    if review is None or archive is None:
        raise LaunchRefused("external authority queue omits the review or its archive successor")
    for field in ("id", "title", "role", "state", "priority", "review_required", "depends_on", "read_scope", "write_scope", "artifact_paths", "handoff"):
        if field not in review:
            raise LaunchRefused(f"review task omits governed field {field}")
    if review.get("role") != "validator" or not isinstance(review.get("read_scope"), list):
        raise LaunchRefused("review task has an invalid governed role or read scope")
    handoff = validate_complete_review_handoff(review.get("handoff"), review_task_id)
    if review.get("read_scope") != handoff["inputs"] or review.get("write_scope") != handoff["write_scope"] or review.get("artifact_paths") != handoff["artifact_paths"]:
        raise LaunchRefused("review task and nested handoff scopes disagree")
    if review_task_id not in archive.get("depends_on", []):
        raise LaunchRefused("archive task does not depend on the completed review")
    return review, archive


def verify_review_admission(
    admission: dict[str, Any], reviewed_source_snapshot: str, executing_commit: str,
) -> None:
    """Verify a complete independent review through an external queue binding.

    The snapshot receipt deliberately records its parent and source hashes,
    never its own commit.  A later, lock-signed authority commit supplies the
    queue archive binding to that actual commit; both sides are checked against
    Git before a PASS can reach a future launch path.
    """
    required = {
        "external_authority_commit", "external_queue_path", "external_queue_sha256",
        "archive_task_id", "archive_commit", "snapshot_receipt_path", "snapshot_receipt_sha256",
        "review_task_id", "review_report_path", "review_report_sha256", "review_plan_path",
        "review_plan_commit", "review_plan_sha256", "reviewed_source_snapshot", "required_verdict",
        "review_claim_path", "review_claim_sha256", "review_claim_commit",
        "review_release_path", "review_release_sha256", "review_release_commit",
    }
    if set(admission) != required:
        raise LaunchRefused("review admission has missing or surplus fields")
    if admission["reviewed_source_snapshot"] != reviewed_source_snapshot or admission["required_verdict"] != "PASS":
        raise LaunchRefused("review admission does not name this reviewed source snapshot and PASS gate")
    if git_output("rev-parse", "HEAD") != executing_commit:
        raise LaunchRefused("executing checkout HEAD differs from lock executing_commit")
    require_commit_precedes(reviewed_source_snapshot, admission["review_plan_commit"], "reviewed source snapshot precedes the review plan")
    require_commit_precedes(admission["review_plan_commit"], admission["review_claim_commit"], "precommitted review plan precedes claim")
    require_commit_precedes(admission["review_claim_commit"], admission["review_release_commit"], "claim precedes completed release")
    require_commit_precedes(admission["review_release_commit"], admission["archive_commit"], "completed release precedes review archive")
    require_commit_precedes(admission["archive_commit"], admission["external_authority_commit"], "review archive precedes external queue authority")
    require_commit_ancestor(admission["external_authority_commit"], executing_commit, "external queue authority precedes executing commit")
    if git_blob_hash(reviewed_source_snapshot, DISPATCH_VALIDATOR_RELATIVE_PATH) != DISPATCH_VALIDATOR_SHA256 or git_blob_hash(reviewed_source_snapshot, GOAL_LANES_RELATIVE_PATH) != GOAL_LANES_SHA256:
        raise LaunchRefused("the canonical dispatch and write-once claim validators are not source-pinned at the reviewed snapshot")
    queue_bytes = git_blob_bytes(admission["external_authority_commit"], admission["external_queue_path"])
    if sha256_bytes(queue_bytes) != admission["external_queue_sha256"]:
        raise LaunchRefused("external queue bytes differ from the signed review admission")
    try:
        queue = json.loads(queue_bytes)
        receipt = json.loads(git_blob_bytes(admission["archive_commit"], admission["snapshot_receipt_path"]))
        report = yaml.safe_load(git_blob_bytes(admission["archive_commit"], admission["review_report_path"]))
        plan = yaml.safe_load(git_blob_bytes(admission["review_plan_commit"], admission["review_plan_path"]))
        queued_queue = json.loads(git_blob_bytes(admission["review_plan_commit"], admission["external_queue_path"]))
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise LaunchRefused(f"archived review receipt/report/plan is unparsable: {exc}") from exc
    review_task, archive_task = validate_governed_review_queue(
        queue, admission["review_task_id"], admission["archive_task_id"],
    )
    queued_review_task, _queued_archive_task = validate_governed_review_queue(
        queued_queue, admission["review_task_id"], admission["archive_task_id"],
    )
    if queued_review_task.get("state") != "queued":
        raise LaunchRefused("review task was not queued in the pre-claim governed queue")
    for field in ("id", "role", "read_scope", "write_scope", "artifact_paths", "handoff"):
        if queued_review_task.get(field) != review_task.get(field):
            raise LaunchRefused("completed review task changed a governed pre-claim declaration")
    archive_task = next((item for item in queue["tasks"] if isinstance(item, dict) and item.get("id") == admission["archive_task_id"]), None)
    if archive_task is None or archive_task.get("state") != "completed":
        raise LaunchRefused("external authority does not complete the review archive task")
    archive = archive_task.get("archive")
    if not isinstance(archive, dict) or archive.get("kind") != "snapshot":
        raise LaunchRefused("external authority queue lacks a snapshot archive binding")
    if archive.get("commit_sha") != admission["archive_commit"] or archive.get("parent_sha") != git_commit_parent(admission["archive_commit"]):
        raise LaunchRefused("external queue archive commit or parent does not match Git")
    if admission["review_task_id"] not in archive.get("source_task_ids", []) or admission["review_task_id"] not in archive.get("record_ids", []):
        raise LaunchRefused("external queue archive does not bind the review task")
    archive_hashes = archive.get("path_sha256")
    if not isinstance(archive_hashes, dict) or set(archive_hashes) != git_changed_paths(admission["archive_commit"]):
        raise LaunchRefused("external queue archive path set does not equal the committed diff")
    if any(git_blob_hash(admission["archive_commit"], path) != digest for path, digest in archive_hashes.items()):
        raise LaunchRefused("external queue archive hash does not match committed bytes")
    if archive_hashes.get(admission["snapshot_receipt_path"]) != admission["snapshot_receipt_sha256"] or archive_hashes.get(admission["review_report_path"]) != admission["review_report_sha256"]:
        raise LaunchRefused("external queue archive omits an admitted receipt or report hash")
    if git_blob_hash(admission["archive_commit"], admission["snapshot_receipt_path"]) != admission["snapshot_receipt_sha256"] or git_blob_hash(admission["archive_commit"], admission["review_report_path"]) != admission["review_report_sha256"]:
        raise LaunchRefused("admitted receipt or report bytes differ from its external queue hash")
    if not isinstance(receipt, dict) or receipt.get("task_id") != admission["archive_task_id"] or receipt.get("parent_sha") != git_commit_parent(admission["archive_commit"]):
        raise LaunchRefused("in-snapshot receipt does not bind the archive task parent")
    if "commit_sha" in receipt or "archive_commit" in receipt:
        raise LaunchRefused("in-snapshot receipt impermissibly self-names its containing commit")
    receipt_hashes = receipt.get("source_path_sha256")
    expected_receipt_hashes = {path: digest for path, digest in archive_hashes.items() if path != admission["snapshot_receipt_path"]}
    if not isinstance(receipt_hashes, dict) or receipt_hashes != expected_receipt_hashes:
        raise LaunchRefused("in-snapshot receipt does not bind the complete non-receipt source path set")
    if admission["review_task_id"] not in receipt.get("source_task_ids", []):
        raise LaunchRefused("in-snapshot receipt does not bind the review task")

    if review_task is None or review_task.get("state") != "completed" or review_task.get("role") != "validator":
        raise LaunchRefused("external authority does not complete the assigned validator review task")
    review_handoff = review_task.get("handoff")
    if not isinstance(review_handoff, dict) or review_handoff.get("id") != admission["review_task_id"] or review_handoff.get("to") != "validator":
        raise LaunchRefused("external authority review task lacks its validator handoff")
    declared_outputs = review_task.get("write_scope")
    if not isinstance(declared_outputs, list) or not declared_outputs or len(set(declared_outputs)) != len(declared_outputs) or any(not isinstance(path, str) or not path for path in declared_outputs):
        raise LaunchRefused("external authority review task has no complete declared output set")
    if review_task.get("artifact_paths") != declared_outputs or review_handoff.get("write_scope") != declared_outputs or review_handoff.get("artifact_paths") != declared_outputs:
        raise LaunchRefused("external authority review task output declarations disagree")
    if not set(declared_outputs).issubset(archive_hashes):
        raise LaunchRefused("external queue archive omits a declared validator output")

    def relative_path(value: Any, label: str) -> str:
        if not isinstance(value, str) or not value:
            raise LaunchRefused(f"{label} is not a repository-relative path")
        parsed = Path(value)
        if parsed.is_absolute() or ".." in parsed.parts or parsed.as_posix() != value:
            raise LaunchRefused(f"{label} is not a safe repository-relative path")
        return value

    def hex_digest(value: Any, label: str) -> str:
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise LaunchRefused(f"{label} is not a SHA-256 digest")
        return value

    def commit_id(value: Any, label: str) -> str:
        if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{40}", value) is None:
            raise LaunchRefused(f"{label} is not a full Git commit id")
        return value

    review = report.get("validation_report", report.get("review_report", report)) if isinstance(report, dict) else None
    if not isinstance(review, dict) or review.get("id") != admission["review_task_id"] or review.get("task_id") != admission["review_task_id"] or review.get("role") != "validator" or review.get("source_snapshot_commit") != reviewed_source_snapshot:
        raise LaunchRefused("review report does not attest the assigned validator task and corrected source snapshot")
    if review.get("artifact_paths") != declared_outputs:
        raise LaunchRefused("review report does not name the complete declared validator output set")
    claim_epoch = review.get("claim_epoch")
    if not isinstance(claim_epoch, int) or claim_epoch < 1:
        raise LaunchRefused("review report lacks a valid control-plane claim epoch")
    claim_path = relative_path(admission["review_claim_path"], "review claim path")
    release_path = relative_path(admission["review_release_path"], "review release path")
    queue_parent = Path(relative_path(admission["external_queue_path"], "external queue path")).parent
    expected_claim_path = (queue_parent / "claims" / f"{admission['review_task_id']}.{claim_epoch}.claim.json").as_posix()
    expected_release_path = (queue_parent / "claims" / f"{admission['review_task_id']}.{claim_epoch}.release.json").as_posix()
    if claim_path != expected_claim_path or release_path != expected_release_path:
        raise LaunchRefused("review admission does not use the queue's write-once claim/release paths")
    claim_commit = commit_id(admission["review_claim_commit"], "review claim commit")
    release_commit = commit_id(admission["review_release_commit"], "review release commit")
    require_commit_ancestor(claim_commit, admission["external_authority_commit"], "review claim precedes external queue authority")
    require_commit_ancestor(release_commit, admission["external_authority_commit"], "review release precedes external queue authority")
    try:
        claim_bytes = git_blob_bytes(claim_commit, claim_path)
        release_bytes = git_blob_bytes(release_commit, release_path)
        if git_blob_bytes(admission["external_authority_commit"], claim_path) != claim_bytes or git_blob_bytes(admission["external_authority_commit"], release_path) != release_bytes:
            raise LaunchRefused("external authority does not carry the claimed write-once provenance blobs")
        claim = json.loads(claim_bytes)
        release = json.loads(release_bytes)
    except (InfrastructureStop, json.JSONDecodeError) as exc:
        raise LaunchRefused(f"review claim/release provenance is unavailable or unparsable: {exc}") from exc
    if sha256_bytes(claim_bytes) != hex_digest(admission["review_claim_sha256"], "review claim hash") or sha256_bytes(release_bytes) != hex_digest(admission["review_release_sha256"], "review release hash"):
        raise LaunchRefused("review claim/release bytes differ from the signed admission")
    required_claim_fields = {"schema", "task_id", "epoch", "owner", "session", "branch", "worktree", "acquired_at", "expires_at", "write_scope", "supersedes", "forced"}
    if not isinstance(claim, dict) or set(claim) != required_claim_fields or claim.get("schema") != "crypto.autoresearch.task_claim.v1" or claim.get("task_id") != admission["review_task_id"] or claim.get("epoch") != claim_epoch or claim.get("write_scope") != declared_outputs or not isinstance(claim.get("owner"), str) or not claim["owner"] or not isinstance(claim.get("session"), str) or not claim["session"]:
        raise LaunchRefused("review claim does not bind the assigned task, scope, owner, and session")
    required_release_fields = {"schema", "task_id", "epoch", "owner", "outcome", "released_at", "was_expired", "note", "artifact_sha256"}
    if not isinstance(release, dict) or set(release) != required_release_fields or release.get("schema") != "crypto.autoresearch.task_release.v1" or release.get("task_id") != admission["review_task_id"] or release.get("epoch") != claim_epoch or release.get("owner") != claim["owner"] or release.get("outcome") != "completed" or not isinstance(release.get("released_at"), str) or not isinstance(release.get("was_expired"), bool) or not isinstance(release.get("note"), str):
        raise LaunchRefused("review release does not complete the matching write-once claim")
    release_hashes = release.get("artifact_sha256")
    expected_release_hashes = {path: archive_hashes[path] for path in declared_outputs}
    if not isinstance(release_hashes, dict) or release_hashes != expected_release_hashes:
        raise LaunchRefused("completed review release does not bind exact declared reviewer output hashes")
    if review.get("claim_owner") != claim["owner"] or review.get("claim_session") != claim["session"] or review.get("claim_epoch") != claim_epoch or review.get("claim_commit") != claim_commit:
        raise LaunchRefused("review report control-plane claim provenance disagrees with the actual claim")

    inference = review.get("inference")
    if not isinstance(inference, dict) or inference.get("requested_policy") != "review-adversarial" or inference.get("reasoning_effort") != "xhigh" or inference.get("independent_session") is not True or not isinstance(inference.get("resolved_model_id"), str) or not inference["resolved_model_id"] or not isinstance(inference.get("provenance"), str) or not inference["provenance"] or inference.get("fallback_used") is not False or inference.get("degraded_used") is not False or inference.get("bedrock_used") is not False:
        raise LaunchRefused("review report lacks the exact independent reviewer provenance")
    if review.get("owned_joint_verdict") != "PASS" or review.get("verdict") != "passed":
        raise LaunchRefused("review report does not carry the exact admitted PASS verdict")
    if not isinstance(plan, dict):
        raise LaunchRefused("review plan is not a mapping")
    plan_root = plan.get("review_plan", plan)
    if git_blob_hash(admission["review_plan_commit"], admission["review_plan_path"]) != admission["review_plan_sha256"]:
        raise LaunchRefused("review plan hash does not match its precommitted bytes")
    if review.get("review_plan_path") != admission["review_plan_path"] or review.get("review_plan_commit") != admission["review_plan_commit"]:
        raise LaunchRefused("review report does not bind the precommitted plan commit")
    plan_required = {"claim_under_review", "coordinator_prior", "recorded_before_reviewers", "source_snapshot", "joints", "blindness", "proves_too_much", "blind_rederivation", "procedure_deviations"}
    if not isinstance(plan_root, dict) or not plan_required.issubset(plan_root) or plan_root.get("recorded_before_reviewers") is not True or plan_root.get("source_snapshot") != reviewed_source_snapshot:
        raise LaunchRefused("review plan does not precommit this source snapshot")
    joints = plan_root.get("joints")
    matching_joints = [joint for joint in joints if isinstance(joint, dict) and joint.get("assigned_to") == admission["review_task_id"]] if isinstance(joints, list) else []
    if len(matching_joints) != 1 or not isinstance(matching_joints[0].get("joint"), str) or not matching_joints[0]["joint"] or not isinstance(matching_joints[0].get("attack_plan"), str) or not matching_joints[0]["attack_plan"] or not isinstance(matching_joints[0].get("breaking_artifact"), str) or not matching_joints[0]["breaking_artifact"]:
        raise LaunchRefused("review plan does not assign exactly one named joint to the validator")
    attestation = review.get("review_attestation")
    standard_attestation = {
        "task_id", "joints_owned", "complete_source_read", "review_plan_path", "source_reads",
        "sources_read", "read_sibling_reports", "blind_from_respected", "verdict",
    }
    if not isinstance(attestation, dict) or not standard_attestation.issubset(attestation):
        raise LaunchRefused("review report lacks the standard complete-source attestation")
    if attestation.get("task_id") != admission["review_task_id"] or attestation.get("joints_owned") != [matching_joints[0]["joint"]] or attestation.get("complete_source_read") is not True or attestation.get("review_plan_path") != admission["review_plan_path"] or not isinstance(attestation.get("sources_read"), list) or not all(isinstance(path, str) for path in attestation["sources_read"]) or attestation.get("read_sibling_reports") is not False or attestation.get("blind_from_respected") not in {True, False, None} or attestation.get("verdict") != "holds":
        raise LaunchRefused("review attestation does not bind the exact assigned joint and standard holds verdict")
    source_reads = attestation.get("source_reads")
    if not isinstance(source_reads, dict) or not source_reads:
        raise LaunchRefused("review report lacks exact source-read hashes")
    resolved_root = ROOT.resolve()
    required_reads = set(review_handoff["inputs"])
    if not required_reads.issubset(source_reads) or not set(source_reads).issubset(set(attestation["sources_read"])):
        raise LaunchRefused("review attestation omits a required exact source read")
    for path, digest in source_reads.items():
        path = relative_path(path, "review source-read path")
        if git_blob_hash(reviewed_source_snapshot, path) != hex_digest(digest, "review source-read hash"):
            raise LaunchRefused("review source-read hashes do not match the reviewed snapshot")


def canonical_experiment_run_root() -> Path:
    return (ROOT / "experiments" / EXPERIMENT_ID).resolve()


def canonical_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or re.fullmatch(r"RUN-ECDLP-[0-9a-f]{6}", run_id) is None:
        raise LaunchRefused("run id is not an allocated RUN-ECDLP-six-lowercase-hex identifier")


def verify_run_allocation(lock: dict[str, Any], run_root: Path) -> Path:
    """Require the signed allocation to name exactly the non-symlink experiment root."""
    allocation = lock.get("run_allocation")
    canonical_root = canonical_experiment_run_root()
    if not isinstance(allocation, dict) or set(allocation) != {"run_id", "experiment_id", "canonical_run_root", "authority_id"}:
        raise LaunchRefused("launch lock lacks the complete Coordinator run-allocation binding")
    if allocation["run_id"] != lock.get("run_id") or allocation["experiment_id"] != EXPERIMENT_ID or not isinstance(allocation["authority_id"], str) or not allocation["authority_id"]:
        raise LaunchRefused("run allocation does not bind this authoritative experiment/run identifier")
    try:
        allocated_root = Path(allocation["canonical_run_root"])
    except TypeError as exc:
        raise LaunchRefused("run allocation canonical root is malformed") from exc
    if allocated_root.is_symlink() or run_root.is_symlink():
        raise LaunchRefused("symlinked run roots are not admissible")
    if allocated_root.absolute() != canonical_root or allocated_root.resolve() != canonical_root:
        raise LaunchRefused("signed run allocation does not name the canonical experiment root")
    if run_root.absolute() != canonical_root or run_root.resolve() != canonical_root:
        raise LaunchRefused("requested run root differs from the canonical allocated experiment root")
    return canonical_root


def verify_launch_admission(lock_path: Path, trusted_public_key_b64: str) -> dict[str, Any]:
    """Verify real future authority, exact sources, resource guard, and archived review semantics."""
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LaunchRefused(f"genuine future launch lock unavailable or malformed: {exc}") from exc
    required = {
        "kind", "approved", "experiment_id", "approval_decision_id", "amendment_id", "spec_sha256",
        "amendment_sha256", "driver_sha256", "execution_plan_sha256", "reviewed_source_snapshot",
        "executing_commit", "runtime", "resource_limits", "review_admission", "run_id", "run_allocation", "signature",
    }
    if set(lock) != required or lock.get("kind") != "coordinator_runtime_execution_lock" or lock.get("approved") is not True:
        raise LaunchRefused("lock lacks the complete Coordinator admission schema")
    canonical_run_id(lock["run_id"])
    if {"experiment_id": lock["experiment_id"], "approval_decision_id": lock["approval_decision_id"], "amendment_id": lock["amendment_id"], "spec_sha256": lock["spec_sha256"], "amendment_sha256": lock["amendment_sha256"]} != {"experiment_id": EXPERIMENT_ID, "approval_decision_id": APPROVAL_ID, "amendment_id": AMENDMENT_ID, "spec_sha256": SPEC_SHA256, "amendment_sha256": AMENDMENT_SHA256}:
        raise LaunchRefused("lock does not bind the frozen experiment and amendment")
    if sha256_file(SPEC_PATH) != SPEC_SHA256 or sha256_file(AMENDMENT_PATH) != AMENDMENT_SHA256:
        raise LaunchRefused("frozen source bytes differ from the approved bindings")
    if lock["driver_sha256"] != sha256_file(Path(__file__)) or lock["execution_plan_sha256"] != sha256_file(PLAN_PATH):
        raise LaunchRefused("lock driver or execution-plan hash differs from executing bytes")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if plan.get("driver", {}).get("sha256") != sha256_file(Path(__file__)):
        raise LaunchRefused("execution plan does not bind the current driver bytes")
    if lock["runtime"] != runtime_binding() or lock["resource_limits"] != {"process_group_memory_bytes": MEMORY_LIMIT_BYTES, "maximum_workers": 1}:
        raise LaunchRefused("lock runtime or machine-protection binding differs")
    current_commit = git_output("rev-parse", "HEAD")
    if lock["executing_commit"] != current_commit or git_output("status", "--porcelain"):
        raise LaunchRefused("execution must use the clean lock-bound executing commit")
    source_paths = {
        "specification": (SPEC_PATH, str(SPEC_PATH.relative_to(ROOT)), SPEC_SHA256),
        "amendment": (AMENDMENT_PATH, str(AMENDMENT_PATH.relative_to(ROOT)), AMENDMENT_SHA256),
        "driver": (Path(__file__), str(Path(__file__).resolve().relative_to(ROOT)), lock["driver_sha256"]),
        "execution_plan": (PLAN_PATH, str(PLAN_PATH.resolve().relative_to(ROOT)), lock["execution_plan_sha256"]),
    }
    for label, (path, relative_path, expected_hash) in source_paths.items():
        if sha256_file(path) != expected_hash:
            raise LaunchRefused(f"executing {label} bytes differ from the lock")
        if git_blob_hash(lock["reviewed_source_snapshot"], relative_path) != expected_hash:
            raise LaunchRefused(f"reviewed source snapshot does not contain the lock-bound {label} bytes")
        if git_blob_hash(current_commit, relative_path) != expected_hash:
            raise LaunchRefused(f"executing commit does not contain the lock-bound {label} bytes")
    verify_signature(trusted_public_key_b64, lock["signature"], lock_payload(lock))
    verify_review_admission(lock["review_admission"], lock["reviewed_source_snapshot"], current_commit)
    return lock


def artifact_bytes(
    *, lock: dict[str, Any], provenance: dict[str, Any], meter: ResourceMeter, sink: ProgressSink,
    status: str, error: str | None, decision: dict[str, Any], check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, bytes]:
    # This is an observed payload boundary, deliberately not the terminal
    # runner boundary.  ``run_future_pipeline`` ends timing only after durable
    # publication and stores a separate operational completion receipt.
    resource_snapshot = meter.snapshot(finish=False)
    timing = resource_snapshot["timing"]
    assembly_index = 0

    def assembly_guard(phase: str, **coordinates: int) -> None:
        nonlocal assembly_index
        guarded_checkpoint(check, assembly_index, phase, on_progress, **coordinates)
        assembly_index += 1

    secondary_names = (
        "mean_first_repeat_length", "useful_fraction", "fixed_points", "two_cycles",
        "component_sizes", "max_tail_length", "max_cycle_length",
    )
    secondary_by_diagnostic: dict[str, dict[str, Any]] = {}
    diagnostic_costs: dict[str, Any] = {}
    for cell_index, cell in enumerate(sink.cells):
        assembly_guard("artifact_cell_summary", cell_index=cell_index)
        cell_key = f"{cell.get('curve_id')}:{cell.get('seed')}:{cell.get('u')}"
        for arm_index, (arm_name, result) in enumerate([("coordinate", cell.get("coordinate", {}))] + [
            (f"null-{arm.get('arm')}", arm) for arm in cell.get("nulls", [])
        ]):
            assembly_guard("artifact_cell_arm_summary", cell_index=cell_index, arm_index=arm_index)
            key = f"{cell_key}:{arm_name}"
            secondary_by_diagnostic[key] = dict(result.get("secondary", {}))
            diagnostic_costs[key] = dict(result.get("diagnostic_costs", {}))
        for diagnostic_index, (name, cost) in enumerate(cell.get("diagnostic_costs", {}).items()):
            if isinstance(cost, list):
                for item_index, item in enumerate(cost):
                    assembly_guard("artifact_cell_diagnostic", cell_index=cell_index, diagnostic_index=diagnostic_index, item_index=item_index)
                    diagnostic_costs[f"{cell_key}:{name}:{item.get('arm')}"] = item
            else:
                assembly_guard("artifact_cell_diagnostic", cell_index=cell_index, diagnostic_index=diagnostic_index, item_index=0)
                diagnostic_costs[f"{cell_key}:{name}"] = cost
    for index, record in enumerate(sink.diagnostics):
        if record.get("completed"):
            # Completed coordinate/null rows already have exactly one canonical
            # row in their cell; only interruption custody belongs to partial.
            continue
        assembly_guard("artifact_partial_diagnostic", diagnostic_index=index)
        diagnostic_costs[f"partial:{index}:{record.get('diagnostic', 'unknown')}"] = dict(record)
    cells_by_stream = {
        stream: sum(row.get("stream") == stream for row in sink.cells)
        for stream in ("exploratory", "heldout")
    }
    seeds_by_stream = {
        stream: sorted({int(row["seed"]) for row in sink.cells if row.get("stream") == stream and "seed" in row})
        for stream in ("exploratory", "heldout")
    }
    retained_coverage = {
        "accepted_fixture_count": len(sink.fixtures),
        "rejected_fixture_candidate_count": len(sink.rejected),
        "completed_cell_count": len(sink.cells),
        "cells_by_stream": cells_by_stream,
        "seeds_by_stream": seeds_by_stream,
        "partial_certificate_count": len(sink.partial_certificates),
        "diagnostic_row_count": len(sink.diagnostics),
        "progress_event_count": sink.progress_event_count,
        "progress_event_bytes": sink.progress_bytes,
        "progress_latest_checkpoint_bytes": sink.latest_checkpoint_bytes,
    }
    metrics = {
        "global_decision": decision, "cells_recorded": len(sink.cells), "rejected_fixture_candidates": len(sink.rejected),
        "retained_coverage": retained_coverage,
        "availability": {"available": sum(bool(row.get("metric", {}).get("available")) for row in sink.cells), "unavailable": sum(not bool(row.get("metric", {}).get("available")) for row in sink.cells)},
        "cayley_gap": {f"{row.get('curve_id')}:{row.get('seed')}:{row.get('u')}": row.get("controls", {}).get("cayley", {}).get("gap") for row in sink.cells},
        "secondary_by_diagnostic": secondary_by_diagnostic,
        "diagnostic_costs": diagnostic_costs,
    }
    for name in secondary_names:
        metrics[name] = {key: value.get(name) for key, value in secondary_by_diagnostic.items()}
    valid = status == "completed_valid"
    try:
        final_rss_boundary_sample: int | None = process_group_rss_bytes()
    except InfrastructureStop:
        # A prior operational failure may have made ps unavailable.  Preserve
        # the partial package and disclose that final RSS was unavailable.
        final_rss_boundary_sample = None
    manifest = {
        "run": {
            "id": lock["run_id"], "experiment_id": EXPERIMENT_ID, "status": status,
            "code": provenance, "inference": {"requested_policy": "executor-implementation", "canonical_policy": "executor-implementation", "backend": None, "provider": None, "resolved_model_id": None, "model_provenance": "not-applicable", "model_verified": False, "requested_reasoning_effort": "xhigh", "reasoning_effort": "xhigh", "fallback_used": False, "fallback_reason": None, "degraded_requirements": [], "independent_session": False, "adapter_version": None, "config_digest": None},
            "environment": {"operating_system": platform.platform(), "architecture": platform.machine(), "sage_version": None, "python_version": sys.version, "dependencies": {"mpmath": mp.__version__, "pyyaml": yaml.__version__}},
            "inputs": {
                "curve_id": None, "seed": None,
                "parameters": {"frozen_exploratory_seeds": list(EXPLORATORY_SEEDS), "frozen_heldout_seeds": list(HELDOUT_SEEDS), "u": list(US)},
            },
            "timing": {**timing, "wall_seconds": resource_snapshot["wall_seconds"], "timing_source": "payload_observed_boundary_before_durable_publication", "final_operational_receipt": "progress/operational-completion.json"},
            "resources": {"rss_boundary_sample_bytes": final_rss_boundary_sample, "rss_sample_scope": "one_payload_assembly_boundary_sample", "cpu_seconds": resource_snapshot["cpu_seconds"], "process_group_memory_limit_bytes": MEMORY_LIMIT_BYTES, "stage_costs": resource_snapshot["stages"]},
            "result": {"metrics": metrics, "valid": valid, "invalid_reason": error, "certificate": {"kind": "none", "verified": True, "verifier": "not-applicable-no-solve-claim"}},
            "artifacts": {"command": "command.txt", "environment": "environment.json", "stdout": "stdout.log", "stderr": "stderr.log", "raw_result": "raw-result.json", "integrity": "package-sha256.json"},
        }
    }
    fixtures = {"accepted": sink.fixtures, "rejected": sink.rejected}
    controls = [{"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "controls": row.get("controls"), "validity": row.get("validity")} for row in sink.cells]
    certificates = {
        "completed_cells": [{"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "coordinate": row.get("coordinate", {}).get("certificates", []), "nulls": [arm.get("certificates", []) for arm in row.get("nulls", [])], "constant_o": row.get("controls", {}).get("known_false", {}).get("constant_o", {}).get("collisions", [])} for row in sink.cells],
        "partial_certificates": sink.partial_certificates,
    }
    cost_rows: list[dict[str, Any]] = []
    for cell_index, row in enumerate(sink.cells):
        assembly_guard("artifact_cost_cell", cell_index=cell_index)
        common = {"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "stream": row.get("stream"), "d": row.get("metric", {}).get("d")}
        coordinate = row.get("coordinate", {})
        cost_rows.append({
            **common, "diagnostic_kind": "collision_census", "arm": "coordinate",
            **{key: coordinate.get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")},
            **coordinate.get("diagnostic_costs", {}), **coordinate.get("diagnostic_meter", {}), **coordinate.get("secondary", {}),
        })
        for arm_index, arm in enumerate(row.get("nulls", [])):
            assembly_guard("artifact_cost_null", cell_index=cell_index, arm_index=arm_index)
            cost_rows.append({
                **common, "diagnostic_kind": "collision_census", "arm": arm.get("arm"),
                **{key: arm.get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")},
                **arm.get("diagnostic_costs", {}), **arm.get("diagnostic_meter", {}), **arm.get("secondary", {}),
            })
        for diagnostic_index, (name, cost) in enumerate(row.get("diagnostic_costs", {}).items()):
            entries = cost if isinstance(cost, list) else [cost]
            for item_index, entry in enumerate(entries):
                assembly_guard("artifact_cost_diagnostic", cell_index=cell_index, diagnostic_index=diagnostic_index, item_index=item_index)
                cost_rows.append({
                    **common, "diagnostic_kind": name, "arm": entry.get("arm"), "starts": None, "successes": None,
                    "transition_group_operations": None, "verification_group_operations": None, "group_additions": None,
                    "group_doublings": None, "charged_cost": None, **entry,
                })
    for record in sink.diagnostics:
        if record.get("completed"):
            continue
        assembly_guard("artifact_cost_partial", diagnostic_index=len(cost_rows))
        cost_rows.append({
            "curve_id": None, "seed": None, "u": None, "stream": "partial", "d": None,
            "diagnostic_kind": record.get("diagnostic"), "arm": None, "starts": None, "successes": None,
            "transition_group_operations": None, "verification_group_operations": None, "group_additions": None,
            "group_doublings": None, "charged_cost": None, **record,
        })
    output = tempfile.SpooledTemporaryFile(mode="w+", newline="", max_size=1_000_000)
    fieldnames = [
        "curve_id", "seed", "u", "stream", "diagnostic_kind", "arm", "starts", "successes",
        "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings",
        "charged_cost", "scalar_inversions", "scalar_comparisons", "diagnostic", "partition_queries",
        "rng_counter_end", "diagnostic_wall_seconds", "diagnostic_cpu_seconds", "collision_table_peak_bytes", "completed", "error",
        "process_group_rss_start_bytes", "process_group_rss_end_bytes", "process_group_rss_boundary_sample_max_bytes", "process_group_rss_sample_scope", "process_group_rss_sample_cadence", "process_group_rss_error",
        *secondary_names, "d",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row_index, row in enumerate(cost_rows):
        assembly_guard("artifact_cost_serialization", row_index=row_index)
        writer.writerow(row)
    output.seek(0)
    costs = output.read().encode("utf-8")
    output.close()
    raw_lines = bytearray()
    for cell_index, row in enumerate(sink.cells):
        assembly_guard("artifact_raw_serialization", cell_index=cell_index)
        raw_lines.extend(canonical_json(row) + b"\n")
    report = "\n".join([
        f"# {EXPERIMENT_ID} future-run record", "", f"Status: `{status}`.",
        f"Global finite decision from the 96 held-out cells only: `{decision.get('branch', 'inconclusive')}`.",
        f"Payload observed timing boundary starts at `{timing['started_at']}` and was observed at `{timing['observed_at']}`; monotonic wall seconds: `{resource_snapshot['wall_seconds']}`.",
        "The terminal operational completion receipt is written after durable publication and is outside this payload timing boundary.",
        "The Cayley gap is a separate reversible calibration and is not a rho spectral claim.",
        "Routine wall/CPU estimates are measured and reported, but DEC-20260907-38017a supersedes their historical stop/invalidation semantics.",
        f"Operational detail: {error or 'none'}.", "",
    ]).encode("utf-8")
    command = provenance["command"] + "\n"
    environment = canonical_json(runtime_binding()) + b"\n"
    assembly_guard("artifact_manifest_serialization")
    manifest_bytes = yaml_bytes_chunked(manifest, check=check, on_progress=on_progress, purpose="artifact_manifest_serialization")
    assembly_guard("artifact_fixtures_serialization")
    fixtures_bytes = json_bytes_chunked(fixtures, check=check, on_progress=on_progress, purpose="artifact_fixtures_serialization") + b"\n"
    assembly_guard("artifact_controls_serialization")
    controls_bytes = json_bytes_chunked(controls, check=check, on_progress=on_progress, purpose="artifact_controls_serialization") + b"\n"
    assembly_guard("artifact_certificates_serialization")
    certificates_bytes = json_bytes_chunked(certificates, check=check, on_progress=on_progress, purpose="artifact_certificates_serialization") + b"\n"
    assembly_guard("artifact_raw_result_serialization")
    raw_result = json_bytes_chunked({"metrics": metrics, "certificate": manifest["run"]["result"]["certificate"], "raw": {"progress_events_path": "progress-events.jsonl", "progress_event_count": sink.progress_event_count, "partial_certificates": sink.partial_certificates, "error": error}}, check=check, on_progress=on_progress, purpose="artifact_raw_result_serialization") + b"\n"
    return {
        "manifest.yaml": manifest_bytes,
        "fixtures.json": fixtures_bytes, "raw.jsonl": bytes(raw_lines),
        "controls.json": controls_bytes, "costs.csv": costs,
        "certificates.json": certificates_bytes, "stdout.log": b"",
        "stderr.log": (error or "").encode("utf-8") + b"\n", "report.md": report,
        "command.txt": command.encode("utf-8"), "environment.json": environment, "raw-result.json": raw_result,
    }


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def retain_publication_failure(
    *, runs: Path, run_id: str, staging: Path, final: Path, error: Exception, phase: str,
) -> dict[str, Any]:
    """Quarantine a failed staging/final tree with a typed durable-state receipt.

    A failure after rename is deliberately distinct: the final path is first
    annotated, then moved under ``runs/incomplete``.  If the move itself fails,
    the annotation remains at the exposed path so it is never an unlabelled
    apparently-complete result directory.
    """
    source = final if final.exists() else staging if staging.exists() else None
    receipt = {
        "classification": "infrastructure_error", "run_id": run_id,
        "publication_state": "post_rename_durability_failed" if final.exists() else "pre_rename_publication_failed",
        "phase": phase, "error": f"{type(error).__name__}: {error}",
    }
    outcome: dict[str, Any] = {
        "receipt": receipt, "retained_path": None, "state": "unretained",
        "receipt_attempted": False, "receipt_written": False,
        "receipt_file_fsynced": False, "receipt_directory_fsynced": False,
        "quarantine_attempted": False, "quarantine_complete": False,
        "parent_directory_fsync_failed": None,
    }
    if source is None:
        return outcome

    def quarantine(candidate: Path) -> None:
        incomplete = runs / "incomplete"
        incomplete.mkdir(exist_ok=True)
        outcome["quarantine_attempted"] = True
        retained = incomplete / f"{run_id}-{uuid.uuid4().hex[:12]}"
        os.rename(candidate, retained)
        fsync_directory(incomplete)
        outcome["retained_path"] = str(retained)
        try:
            fsync_directory(runs)
        except OSError as parent_error:
            outcome["parent_directory_fsync_failed"] = f"{type(parent_error).__name__}: {parent_error}"
            outcome["state"] = "quarantine_parent_fsync_failed"
            outcome["quarantine_complete"] = False
            return
        outcome["state"] = "quarantined"
        outcome["quarantine_complete"] = True

    try:
        receipt_path = source / "publication-failure.json"
        outcome["receipt_attempted"] = True
        receipt_path.write_bytes(canonical_json(receipt) + b"\n")
        outcome["receipt_written"] = True
        with receipt_path.open("rb") as handle:
            os.fsync(handle.fileno())
        outcome["receipt_file_fsynced"] = True
        fsync_directory(source)
        outcome["receipt_directory_fsynced"] = True
    except OSError as retain_error:
        outcome["retention_error"] = f"{type(retain_error).__name__}: {retain_error}"
        # Do not call this annotated_final: neither file nor directory durability
        # was established.  Try to remove the canonical-looking path anyway.
        if final.exists():
            try:
                quarantine(final)
                if outcome["state"] == "quarantined":
                    # The move may be durable, but the failure receipt was not;
                    # preserve S2's distinction between quarantined bytes and a
                    # durably retained typed failure receipt.
                    outcome["state"] = "unretained"
            except OSError as quarantine_error:
                outcome["quarantine_error"] = f"{type(quarantine_error).__name__}: {quarantine_error}"
        return outcome
    try:
        quarantine(source)
    except OSError as retain_error:
        outcome.update({"state": "annotated_final" if final.exists() else "unretained", "retention_error": f"{type(retain_error).__name__}: {retain_error}"})
    return outcome


def atomic_publish(
    run_root: Path, run_id: str, payload: dict[str, bytes], check: Callable[[], None] | None = None,
    on_progress: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, str]:
    """Write verified files in a sibling staging directory, then atomically rename once."""
    if set(payload) != set(EXPERIMENT_ARTIFACTS[:-1]):
        raise ValueError("payload is missing a canonical experiment artifact")
    runs = run_root / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    final = runs / run_id
    if final.exists():
        raise LaunchRefused("allocated run id already has a final directory")
    staging = Path(tempfile.mkdtemp(prefix=f".{run_id}.staging-", dir=runs))
    publication_phase = "staging_write"
    try:
        hashes: dict[str, str] = {}
        for artifact_index, name in enumerate(EXPERIMENT_ARTIFACTS[:-1]):
            guarded_checkpoint(check, artifact_index * CAYLEY_GUARD_STRIDE, "publication_hashes", on_progress, artifact_index=artifact_index)
            hashes[name] = sha256_chunks(
                payload[name], check=check, on_progress=on_progress,
                purpose="publication_payload_hash",
            )
        for artifact_index, name in enumerate(EXPERIMENT_ARTIFACTS):
            value = (
                json_bytes_chunked({"artifact_sha256": hashes}, check=check, on_progress=on_progress, purpose="publication_integrity_serialization") + b"\n"
                if name == "package-sha256.json" else payload[name]
            )
            guarded_checkpoint(check, artifact_index * CAYLEY_GUARD_STRIDE, "publication_write", on_progress, artifact_index=artifact_index)
            target = staging / name
            with target.open("xb") as handle:
                write_chunked(handle, value, check=check, on_progress=on_progress)
                handle.flush()
                os.fsync(handle.fileno())
        publication_phase = "staging_hash_verification"
        for artifact_index, (name, digest) in enumerate(hashes.items()):
            guarded_checkpoint(check, artifact_index * CAYLEY_GUARD_STRIDE, "publication_hash_verification", on_progress, artifact_index=artifact_index)
            if sha256_file(staging / name, check=check, on_progress=on_progress, purpose="publication_hash_verification") != digest:
                raise InfrastructureStop(f"staged artifact hash mismatch: {name}")
        if set(path.name for path in staging.iterdir()) != set(EXPERIMENT_ARTIFACTS):
            raise InfrastructureStop("staged canonical artifact set is incomplete")
        publication_phase = "pre_rename_durability"
        guarded_checkpoint(check, 0, "publication_pre_rename_durability", on_progress, artifact_index=0)
        fsync_directory(staging)
        fsync_directory(runs)
        if final.exists():
            raise LaunchRefused("final run directory appeared during publication")
        publication_phase = "rename_to_canonical_final"
        guarded_checkpoint(check, 0, "publication_rename", on_progress, artifact_index=0)
        os.rename(staging, final)  # same filesystem because staging is a sibling of final
        publication_phase = "post_rename_durability"
        guarded_checkpoint(check, 0, "publication_post_rename_durability", on_progress, artifact_index=0)
        fsync_directory(runs)
        return hashes
    except (CancellationStop, ResourceStop) as exc:
        retention = retain_publication_failure(
            runs=runs, run_id=run_id, staging=staging, final=final, error=exc, phase=publication_phase,
        )
        # The retained custody state supplements, never reclassifies, the
        # original typed operational stop.
        _ = retention
        raise
    except Exception as exc:
        retention = retain_publication_failure(
            runs=runs, run_id=run_id, staging=staging, final=final, error=exc, phase=publication_phase,
        )
        if isinstance(exc, InfrastructureStop):
            raise
        raise InfrastructureStop(
            f"atomic publication failed at {publication_phase}; durable state={retention['state']}; "
            f"failure receipt retained if possible: {exc}"
        ) from exc


def retain_operational_completion(
    progress_dir: Path, *, meter: ResourceMeter, guard: Guard, state: str,
    payload_hashes: dict[str, str] | None, error: Exception | None,
) -> Path:
    """Persist the post-publication operational receipt outside its timing end.

    It intentionally has neither a self-hash nor a claim to include its own
    write/fsync time.  A future execution plan names it as required custody.
    """
    meter.finish()
    receipt = {
        "schema": "crypto.autoresearch.operational_completion_receipt.v1",
        "state": state,
        "timing_through_durable_payload": meter.snapshot(finish=False),
        "guard_telemetry": guard.telemetry(),
        "payload_artifact_sha256": payload_hashes,
        "error": None if error is None else f"{type(error).__name__}: {error}",
        "terminal_receipt_scope": "This receipt is written and fsynced after the measured durable-payload boundary; it contains no self-inclusive timing or self-hash.",
    }
    target = progress_dir / "operational-completion.json"
    with target.open("xb") as handle:
        write_chunked(handle, json_bytes_chunked(receipt, purpose="operational_receipt_serialization") + b"\n", purpose="operational_receipt_write")
        handle.flush()
        os.fsync(handle.fileno())
    fsync_directory(progress_dir)
    return target


def run_future_pipeline(lock: dict[str, Any], run_root: Path, command: str) -> dict[str, str]:
    """The real future path.  This is never invoked by this correction task."""
    run_root = verify_run_allocation(lock, run_root)
    staging_root = run_root / "runs"
    staging_root.mkdir(parents=True, exist_ok=True)
    progress_dir = Path(tempfile.mkdtemp(prefix=f".{lock['run_id']}.progress-", dir=staging_root))
    sink = ProgressSink(progress_dir)
    guard = Guard(sink)
    meter = ResourceMeter()
    original_handlers: dict[int, Any] = {}

    def cancel(_signal: int, _frame: Any) -> None:
        guard.cancelled = True

    for signum in (signal.SIGINT, signal.SIGTERM):
        original_handlers[signum] = signal.getsignal(signum)
        signal.signal(signum, cancel)
    status = "completed_invalid"
    error: str | None = None
    decision: dict[str, Any] = {"branch": "inconclusive", "reasons": ["not_started"], "per_u": {}}
    published = False
    try:
        meter.enter("prepare")
        selected, _rejected = select_fixtures(guard.check, sink)
        sink.checkpoint("fixtures_completed")
        guard.check(force=True)
        meter.exit("prepare")
        meter.enter("census")
        for stream, seeds in (("exploratory", EXPLORATORY_SEEDS), ("heldout", HELDOUT_SEEDS)):
            for rows in selected.values():
                for fixture in rows:
                    for seed in seeds:
                        for u in US:
                            sink.record_progress({
                                "event": "census_cell_in_progress",
                                "state": "census_cell_pending", "stream": stream,
                                "curve_id": f"p{fixture['p']}-B{fixture['B']}", "seed": seed, "u": u,
                            })
                            guard.check(force=True)
                            curve_id = f"p{fixture['p']}-B{fixture['B']}"

                            def record_partial(kind: str, arm: int, certificate: dict[str, Any]) -> None:
                                base = {"curve_id": curve_id, "seed": seed, "u": u, "kind": kind, "arm": arm}
                                if certificate.get("state") == "partial_invalid_cell":
                                    sink.record_partial({**base, "certificate": certificate})
                                elif "classification" in certificate:
                                    # Completed scalar certificates belong to their canonical
                                    # cell, while this compact event records progress only.
                                    sink.record_progress({"event": "scalar_certificate_completed", **base, "classification": certificate.get("classification")})
                                else:
                                    sink.record_progress({"event": "work_in_progress", **base, "phase": certificate.get("phase"), "index": certificate.get("index")})

                            cell = future_cell(fixture, seed, u, guard.check, record_partial, sink.record_diagnostic)
                            cell["stream"] = stream
                            sink.record_cell(cell)
                            if not cell["validity"]["valid"]:
                                sink.checkpoint("measurement_invalid_stop")
                                raise MeasurementInvalidStop(
                                    f"frozen validity failure at stream={stream} curve={curve_id} seed={seed} u={u}"
                                )
        meter.exit("census")
        guard.check(force=True)
        meter.enter("report")
        heldout_cells = [cell for cell in sink.cells if cell.get("stream") == "heldout"]
        decision = global_decision(heldout_cells)
        status = "completed_valid" if decision["panel_valid"] else "completed_invalid"
        error = None if decision["panel_valid"] else ";".join(decision["reasons"])
        meter.exit("report")
        guard.check(force=True)
    except MeasurementInvalidStop as exc:
        status, error = "completed_invalid", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["frozen_validity_failure_immediate_stop"], "per_u": {}}
    except IncompleteFixtureStop as exc:
        status, error = "incomplete_fixture_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["incomplete_frozen_fixture_panel"], "per_u": {}}
    except CancellationStop as exc:
        status, error = "cancelled_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_cancellation"], "per_u": {}}
    except ResourceStop as exc:
        status, error = "resource_exhaustion_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_resource_stop"], "per_u": {}}
    except InfrastructureStop as exc:
        status, error = "failed_infrastructure", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_infrastructure_failure"], "per_u": {}}
    except Exception as exc:
        status, error = "failed_implementation", f"implementation_error: {type(exc).__name__}: {exc}"
        decision = {"branch": "inconclusive", "reasons": ["implementation_exception"], "per_u": {}}
    finally:
        meter.close_active()
    try:
        artifact_progress = lambda state: sink.checkpoint("artifact_guard", state)
        provenance = execution_provenance(command)
        meter.enter("artifact_construction")
        payload = artifact_bytes(
            lock=lock, provenance=provenance, meter=meter, sink=sink, status=status, error=error,
            decision=decision, check=guard.check, on_progress=artifact_progress,
        )
        meter.exit("artifact_construction")
        meter.enter("publication")
        hashes = atomic_publish(
            run_root, lock["run_id"], payload, check=guard.check, on_progress=artifact_progress,
        )
        meter.exit("publication")
        meter.finish()
        retain_operational_completion(
            progress_dir, meter=meter, guard=guard, state="durable_payload_published",
            payload_hashes=hashes, error=None,
        )
        published = True
        return hashes
    except (CancellationStop, ResourceStop, InfrastructureStop) as exc:
        meter.close_active()
        meter.finish()
        retain_operational_completion(
            progress_dir, meter=meter, guard=guard, state="typed_incomplete_package_retained",
            payload_hashes=None, error=exc,
        )
        raise
    except Exception as exc:
        meter.close_active()
        meter.finish()
        retain_operational_completion(
            progress_dir, meter=meter, guard=guard, state="implementation_incomplete_package_retained",
            payload_hashes=None, error=exc,
        )
        raise InfrastructureStop(f"artifact construction or publication failed with retained progress custody: {exc}") from exc
    finally:
        for signum, handler in original_handlers.items():
            signal.signal(signum, handler)
        # Retain the only progress tree on every failure.  It is removed only
        # after a durable payload and the separately durable terminal receipt.
        if published:
            shutil.rmtree(progress_dir)


def protocol_coverage() -> dict[str, str]:
    return {
        "F-01_fixture_rejections": "fixture_scan/select_fixtures",
        "F-02_constant_O_execution": "constant_o_census",
        "F-03_validity_reduction": "reduce_validity/collision_census",
        "F-04_manifest_companions": "artifact_bytes/atomic_publish",
        "F-05_incremental_progress": "ProgressSink/Guard/run_future_pipeline",
        "F-06_memory_and_advisory_costs": "process_group_rss_bytes/ResourceMeter",
        "F-07_atomic_publication": "atomic_publish",
        "F-08_custody_and_decision": "artifact_bytes/global_decision/cayley_control",
        "F-09_review_admission": "verify_review_admission/verify_launch_admission",
        "V-01_repeated_addition_subgroup": "enumerate_subgroup",
        "V-02_exploratory_seed_custody": "EXPLORATORY_SEEDS/run_future_pipeline",
        "V-03_immediate_invalid_stop": "MeasurementInvalidStop/run_future_pipeline",
        "V-04_diagnostic_cost_custody": "collision_census/artifact_bytes",
        "V-05_terminal_timing_bracket": "ResourceMeter/artifact_bytes",
        "V-06_postrename_quarantine": "retain_publication_failure/atomic_publish",
        "V-07_reviewed_source_execution_separation": "verify_review_admission/verify_launch_admission",
        "V-08_cayley_guard_stride": "_cayley_checkpoint/cayley_control",
        "S2-01_control_rng_pairing": "future_cell/deterministic_shuffle",
        "S2-02_typed_operational_outcomes": "IncompleteFixtureStop/run_future_pipeline",
        "S2-03_partial_coverage_and_cost_custody": "measured_diagnostic/ProgressSink/artifact_bytes",
        "S2-04_publication_failure_durability": "retain_publication_failure",
        "S2-05_allocated_canonical_run_root": "canonical_run_id/verify_run_allocation",
        "S2-06_external_review_archive_admission": "verify_review_admission",
        "S2-07_valid_process_group_rss": "process_group_rss_bytes/Guard",
        "S2-08_dense_loop_guard_progress": "guarded_checkpoint/_cayley_checkpoint",
        "S3-01_complete_review_task_claim_and_attestation": "verify_review_admission/queue-relative-write-once-claims",
        "S3-02_parent_directory_fsync_quarantine_durability": "retain_publication_failure",
        "S3-03_failed_scalar_certificate_immediate_stop": "collision_census/MeasurementInvalidStop",
        "S3-04_interrupted_diagnostic_memory_custody": "measured_diagnostic/collision_census_with_custody",
        "S3-05_guarded_progress_through_assembly_publication": "guarded_checkpoint/artifact_bytes/atomic_publish",
        "pooled_side_availability": "cell_difference",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("coverage", help="print static protocol-to-code coverage; no scientific work")
    future = sub.add_parser("future-run", help="requires a real future Coordinator lock and archived PASS review")
    future.add_argument("--lock", type=Path, required=True)
    future.add_argument("--coordinator-public-key-b64", required=True)
    future.add_argument("--run-root", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "coverage":
        print(json.dumps(protocol_coverage(), indent=2, sort_keys=True))
        return 0
    lock = verify_launch_admission(args.lock, args.coordinator_public_key_b64)
    hashes = run_future_pipeline(lock, args.run_root, " ".join(sys.argv))
    print(json.dumps({"published_artifact_sha256": hashes}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
