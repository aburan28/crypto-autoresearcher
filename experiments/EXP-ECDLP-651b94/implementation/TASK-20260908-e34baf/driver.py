#!/usr/bin/env python3
"""Prospective, fail-closed runner for EXP-ECDLP-651b94.

This module contains the complete *future* finite protocol.  Importing it and
the default CLI do no fixture selection, Cayley calibration, collision census,
control panel, or timing measurement.  ``future-run`` is deliberately gated by
an externally authenticated Coordinator lock and a fresh archived review.

The correction successor implements DEC-20260907-38017a and the approved S5
source-architecture boundary in DEC-20260908-2dafc2.  It is not a launch lock,
a run record, or scientific evidence.
"""
from __future__ import annotations

import argparse
import base64
import csv
import copy
import contextlib
import hashlib
import importlib.util
import json
import math
import os
import platform
import re
import resource
import signal
import subprocess
import sys
import tempfile
import time
import types
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

import mpmath as mp
import yaml

from custody import FinalizationResult, finalize_run
from streaming import (
    GuardedDigestWriter,
    MAX_CHUNK_BYTES,
    append_jsonl,
    bounded_graph_size,
    copy_file,
    iter_jsonl,
    stream_json_array,
    write_json_document,
    write_json_value,
)

TASK_ID = "TASK-20260908-e34baf"
EXPERIMENT_ID = "EXP-ECDLP-651b94"
APPROVAL_ID = "DEC-20260906-f73475"
AMENDMENT_ID = "DEC-20260907-38017a"
CORRECTION_DECISION_ID = "DEC-20260908-2dafc2"
SPEC_SHA256 = "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee"
AMENDMENT_SHA256 = "a24e723fa1d499621957e1fd3939d3e95a0e1f9c003412396f6eec00d9052280"
MEMORY_LIMIT_BYTES = 8 * 1024**3
EXPLORATORY_SEEDS = tuple(range(606300, 606308))
HELDOUT_SEEDS = tuple(range(606308, 606316))
US = (1, 2, 3)
CAYLEY_GUARD_STRIDE = 16
MAX_SERIALIZATION_CHUNK_BYTES = MAX_CHUNK_BYTES
MAX_PROGRESS_EVENT_BYTES = 1024
MAX_PROGRESS_LOG_BYTES = 256 * 1024 * 1024
MAX_PROGRESS_LATEST_BYTES = 64 * 1024
MAX_GUARD_POLL_INTERVAL_SECONDS = 0.250
DISPATCH_VALIDATOR_RELATIVE_PATH = "tools/research_dispatch.py"
DISPATCH_VALIDATOR_SHA256 = "5c40d891369c38f8d9013603fdf627f286243dffe4443878dd9e75926ec32c5c"
GOAL_LANES_RELATIVE_PATH = "tools/goal_lanes.py"
GOAL_LANES_SHA256 = "89f99ecac689e1c331be6c8a14de410e25d460fd4662903b04c63513e7fee82c"
RESEARCH_BUDGET_RELATIVE_PATH = "orchestration/research_budget.py"
RESEARCH_BUDGET_SHA256 = "11a6360777bdf2c0fc6403cfcb77ab7b05a99fba4b7856f785850271bdc503a0"
MODEL_POLICIES_RELATIVE_PATH = "orchestration/model-policies.yaml"
MODEL_POLICIES_SHA256 = "1756cf3aa062f893c0d8f61bee5b5dd79348839457e8932935785e8061c38be8"
MODEL_BINDINGS_RELATIVE_PATH = "orchestration/model-bindings.yaml"
MODEL_BINDINGS_SHA256 = "fe2b465a80e65fb53b7ec533b6e2fd6162ce7ee87bf0bcab633f69d3e2b62fa1"
REVIEW_PLAN_VALIDATOR_RELATIVE_PATH = "tools/check_review_independence.py"
REVIEW_PLAN_VALIDATOR_SHA256 = "10815ff7446fec8e881c049fd5ab84f4f8a6c81fc283c6076f1b2f013dc319c5"
SMALL_MANIFEST_GRAPH_LIMIT_BYTES = 1024 * 1024
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


def repository_root() -> Path:
    return Path(__file__).resolve().parents[4]


ROOT = repository_root()
SPEC_PATH = ROOT / "experiments" / EXPERIMENT_ID / "specification.yaml"
AMENDMENT_PATH = ROOT / "experiments" / EXPERIMENT_ID / "amendments" / f"{AMENDMENT_ID}.yaml"
PLAN_PATH = Path(__file__).resolve().with_name("execution-plan.json")
STREAMING_PATH = Path(__file__).resolve().with_name("streaming.py")
CUSTODY_PATH = Path(__file__).resolve().with_name("custody.py")


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
    prepared_assignments: list[dict[str, Any]] = []
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
        bucket_counts = [sum(value == bucket for value in assignment.values()) for bucket in range(3)]
        prepared_assignments.append({
            "arm": arm,
            "assignment": assignment,
            "rng_counter_end": consumed,
            "bucket_counts": bucket_counts,
        })
        if on_partial:
            on_partial(
                "shuffle_assignment",
                arm,
                {
                    "state": "shuffle_assignment_completed",
                    "arm": arm,
                    "rng_counter_end": consumed,
                    "bucket_counts": bucket_counts,
                },
            )

    expected_bucket_counts = [sum(value == bucket for value in coordinate.values()) for bucket in range(3)]
    observed_bucket_counts = [row["bucket_counts"] for row in prepared_assignments]
    occupancy_result = {
        "occupancy": all(counts == expected_bucket_counts for counts in observed_bucket_counts),
        "expected_bucket_counts": expected_bucket_counts,
        "observed_bucket_counts": observed_bucket_counts,
        "assignments_completed": len(prepared_assignments),
    }
    if not occupancy_result["occupancy"]:
        partial = {
            "state": "partial_invalid_cell", "reason": "occupancy_control_failed",
            "expected_bucket_counts": expected_bucket_counts,
            "observed_bucket_counts": observed_bucket_counts,
            "assignments_completed": len(prepared_assignments),
            "null_censuses_started": 0,
        }
        if on_partial:
            on_partial("invalid_cell", 0, partial)
        raise MeasurementInvalidStop("occupancy control failed after seven completed shuffle assignments")

    # Only a fully prepared, occupancy-valid set of seven assignments may
    # start a null collision census.  The assignment objects stay live as the
    # current bounded cell and are discarded when this function returns.
    for prepared in prepared_assignments:
        arm = int(prepared["arm"])
        assignment = prepared["assignment"]
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
        result["rng_counter_end"] = prepared["rng_counter_end"]
        result["bucket_counts"] = prepared["bucket_counts"]
        shuffles.append(result)
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
    check: Callable[[], None] | None = None
    accepted_fixture_count: int = 0
    rejected_fixture_count: int = 0
    completed_cell_count: int = 0
    partial_certificate_count: int = 0
    scientific_certificate_count: int = 0
    diagnostic_row_count: int = 0
    cells_by_stream: dict[str, int] = field(
        default_factory=lambda: {"exploratory": 0, "heldout": 0}
    )
    seeds_by_stream: dict[str, set[int]] = field(
        default_factory=lambda: {"exploratory": set(), "heldout": set()}
    )
    decision_cells: list[dict[str, Any]] = field(default_factory=list)
    available_cell_count: int = 0
    unavailable_cell_count: int = 0
    progress_event_count: int = 0
    progress_bytes: int = 0
    latest_checkpoint_bytes: int = 0

    def _append(self, name: str, record: dict[str, Any]) -> None:
        append_jsonl(
            self.staging / name,
            record,
            check=self.check,
            purpose=f"spool:{name}",
        )

    def record_rejection(self, record: dict[str, Any]) -> None:
        self._append("fixture-rejections.jsonl", record)
        self.rejected_fixture_count += 1
        self.checkpoint("fixture_rejected")

    def record_fixture(self, record: dict[str, Any]) -> None:
        self._append("fixture-selections.jsonl", record)
        self.accepted_fixture_count += 1
        self.checkpoint("fixture_selected")

    def record_partial(self, record: dict[str, Any]) -> None:
        self._append("partial-certificates.jsonl", record)
        self.partial_certificate_count += 1
        self.checkpoint("partial_certificate_retained", {"state": record.get("state", "partial_certificate")})

    def record_scientific_certificate(self, record: dict[str, Any]) -> None:
        """Persist one scientific certificate without consuming progress budget."""
        self._append("scientific-certificates.jsonl", record)
        self.scientific_certificate_count += 1

    def record_cell(self, record: dict[str, Any]) -> None:
        self._append("completed-cells.jsonl", record)
        self.completed_cell_count += 1
        stream = record.get("stream")
        if stream in self.cells_by_stream:
            self.cells_by_stream[stream] += 1
            if isinstance(record.get("seed"), int):
                self.seeds_by_stream[stream].add(int(record["seed"]))
        if record.get("metric", {}).get("available"):
            self.available_cell_count += 1
        else:
            self.unavailable_cell_count += 1
        if stream == "heldout":
            # Only the compact fields required by the frozen global reducer
            # survive in memory.  Full cells remain in the append-only spool.
            self.decision_cells.append(
                {
                    "curve_id": record.get("curve_id"),
                    "seed": record.get("seed"),
                    "u": record.get("u"),
                    "metric": copy.deepcopy(record.get("metric", {})),
                    "validity": {"valid": bool(record.get("validity", {}).get("valid"))},
                }
            )
        self.checkpoint("cell_completed", {"completed_cells": self.completed_cell_count})

    def record_diagnostic(self, record: dict[str, Any]) -> None:
        """Retain a completed or interrupted diagnostic cost before later work."""
        self._append("diagnostics.jsonl", record)
        self.diagnostic_row_count += 1
        self.checkpoint("diagnostic_recorded")

    def records(self, name: str) -> Iterable[dict[str, Any]]:
        return iter_jsonl(self.staging / name)

    def flush_required_prefix(self) -> None:
        """Fsync every existing scientific/progress spool before a real probe or stop."""
        for name in (
            "fixture-rejections.jsonl",
            "fixture-selections.jsonl",
            "completed-cells.jsonl",
            "partial-certificates.jsonl",
            "scientific-certificates.jsonl",
            "diagnostics.jsonl",
            "progress-events.jsonl",
            "progress-latest.json",
        ):
            path = self.staging / name
            if path.exists():
                with path.open("rb") as handle:
                    os.fsync(handle.fileno())
        fsync_directory(self.staging)

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
                "fixtures": self.accepted_fixture_count, "rejected": self.rejected_fixture_count,
                "cells": self.completed_cell_count, "partial_certificates": self.partial_certificate_count,
                "scientific_certificates": self.scientific_certificate_count,
                "diagnostics": self.diagnostic_row_count, "progress_events": self.progress_event_count,
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

    def __post_init__(self) -> None:
        self.sink.check = self.check

    def should_probe(self) -> bool:
        """Check signals on every opportunity and throttle RSS reads to 250ms."""
        self.guard_requests += 1
        if self.cancelled:
            self.sink.flush_required_prefix()
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
                self.sink.flush_required_prefix()
                raise CancellationStop("operator cancellation observed")
            self._probe_pending = True
        elif not self._probe_pending and not self.should_probe():
            return
        self.sink.flush_required_prefix()
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
        "source_sha256": {
            "specification.yaml": sha256_file(SPEC_PATH),
            "amendment.yaml": sha256_file(AMENDMENT_PATH),
            "driver.py": sha256_file(Path(__file__)),
            "streaming.py": sha256_file(STREAMING_PATH),
            "custody.py": sha256_file(CUSTODY_PATH),
            "execution-plan.json": sha256_file(PLAN_PATH),
        },
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


class _PinnedInferenceConfig:
    """Minimal policy view used by the source-pinned canonical queue validator."""

    def __init__(self, policies_document: dict[str, Any]) -> None:
        adapter = policies_document.get("adapter")
        policies = policies_document.get("policies")
        if not isinstance(adapter, dict) or not isinstance(policies, dict):
            raise LaunchRefused("pinned model policy document is malformed")
        order = adapter.get("reasoning_effort_order")
        if not isinstance(order, list) or not order or not all(isinstance(item, str) for item in order):
            raise LaunchRefused("pinned model policy effort lattice is malformed")
        self.effort_order = order
        self.policy_table = policies
        self.aliases: dict[str, str] = {}
        for policy_id, policy in policies.items():
            if not isinstance(policy_id, str) or not isinstance(policy, dict):
                raise LaunchRefused("pinned model policy table is malformed")
            self.aliases[policy_id] = policy_id
            for alias in policy.get("aliases", []):
                if not isinstance(alias, str) or alias in self.aliases:
                    raise LaunchRefused("pinned model policy aliases are malformed")
                self.aliases[alias] = policy_id

    def canonical_policy(self, policy_id: str) -> str:
        try:
            return self.aliases[policy_id]
        except (KeyError, TypeError) as exc:
            raise ValueError(f"unknown inference policy {policy_id!r}") from exc


def _verify_trusted_validator_sources(reviewed_source_snapshot: str) -> None:
    sources = {
        DISPATCH_VALIDATOR_RELATIVE_PATH: DISPATCH_VALIDATOR_SHA256,
        GOAL_LANES_RELATIVE_PATH: GOAL_LANES_SHA256,
        RESEARCH_BUDGET_RELATIVE_PATH: RESEARCH_BUDGET_SHA256,
        MODEL_POLICIES_RELATIVE_PATH: MODEL_POLICIES_SHA256,
        MODEL_BINDINGS_RELATIVE_PATH: MODEL_BINDINGS_SHA256,
        REVIEW_PLAN_VALIDATOR_RELATIVE_PATH: REVIEW_PLAN_VALIDATOR_SHA256,
    }
    for relative, expected in sources.items():
        live = ROOT / relative
        if sha256_file(live) != expected:
            raise LaunchRefused(f"locally trusted validator source changed: {relative}")
        if git_blob_hash(reviewed_source_snapshot, relative) != expected:
            raise LaunchRefused(f"reviewed snapshot does not pin trusted validator source: {relative}")


def _load_source_module(name: str, path: Path) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise LaunchRefused(f"cannot load source-pinned validator module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@contextlib.contextmanager
def trusted_canonical_validators(reviewed_source_snapshot: str) -> Iterable[tuple[types.ModuleType, types.ModuleType]]:
    """Load only the independently source-pinned local validation code.

    ``research_dispatch`` normally imports the full runtime adapter.  Admission
    needs only the policy table queried by ``validate_inference``.  A tiny shim
    supplies that view from the pinned YAML, avoiding execution of any unbound
    adapter module while preserving the canonical queue validator itself.
    """
    _verify_trusted_validator_sources(reviewed_source_snapshot)
    try:
        policies_document = yaml.safe_load((ROOT / MODEL_POLICIES_RELATIVE_PATH).read_bytes())
        bindings_document = yaml.safe_load((ROOT / MODEL_BINDINGS_RELATIVE_PATH).read_bytes())
    except yaml.YAMLError as exc:
        raise LaunchRefused(f"pinned model configuration is unparsable: {exc}") from exc
    if not isinstance(bindings_document, dict) or not isinstance(bindings_document.get("bindings"), dict):
        raise LaunchRefused("pinned model binding document is malformed")
    config = _PinnedInferenceConfig(policies_document)
    module_names = (
        "orchestration",
        "orchestration.research_budget",
        "orchestration.adapter",
        "_spectral_pinned_research_dispatch",
        "_spectral_pinned_review_plan",
    )
    previous = {name: sys.modules.get(name) for name in module_names}
    try:
        package = types.ModuleType("orchestration")
        package.__path__ = [str(ROOT / "orchestration")]  # type: ignore[attr-defined]
        sys.modules["orchestration"] = package
        research_budget = _load_source_module(
            "orchestration.research_budget", ROOT / RESEARCH_BUDGET_RELATIVE_PATH
        )
        sys.modules["orchestration.research_budget"] = research_budget
        adapter = types.ModuleType("orchestration.adapter")
        adapter.load = lambda: config  # type: ignore[attr-defined]
        sys.modules["orchestration.adapter"] = adapter
        dispatch = _load_source_module(
            "_spectral_pinned_research_dispatch", ROOT / DISPATCH_VALIDATOR_RELATIVE_PATH
        )
        sys.modules["_spectral_pinned_research_dispatch"] = dispatch
        review_plan = _load_source_module(
            "_spectral_pinned_review_plan", ROOT / REVIEW_PLAN_VALIDATOR_RELATIVE_PATH
        )
        sys.modules["_spectral_pinned_review_plan"] = review_plan
        yield dispatch, review_plan
    finally:
        for name, module in previous.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


def _canonical_queue_copy(
    queue: Any,
    dispatch: types.ModuleType,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    copied = copy.deepcopy(queue)
    try:
        by_id = dispatch.validate_queue(
            copied, repository_verifier=dispatch.GitRepositoryVerifier(ROOT)
        )
    except Exception as exc:
        raise LaunchRefused(f"canonical dispatch queue validation failed: {exc}") from exc
    return copied, by_id


def _review_plan_root(document: Any) -> dict[str, Any]:
    if not isinstance(document, dict):
        raise LaunchRefused("precommitted review plan is not a mapping")
    plan = document.get("review_plan", document)
    if not isinstance(plan, dict):
        raise LaunchRefused("precommitted review plan root is not a mapping")
    return plan


def _resolve_and_validate_review_plan(
    *,
    handoff: dict[str, Any],
    precommitted_document: Any,
    admission: dict[str, Any],
    reviewed_source_snapshot: str,
    report_attestation: dict[str, Any],
    review_plan_validator: types.ModuleType,
) -> dict[str, Any]:
    precommitted = _review_plan_root(precommitted_document)
    inline = handoff.get("review_plan")
    path_bound = handoff.get("review_plan_path")
    if inline is None and path_bound is None:
        raise LaunchRefused("review handoff has neither an inline nor path-bound review plan")
    if path_bound is not None and path_bound != admission["review_plan_path"]:
        raise LaunchRefused("review handoff path-bound plan differs from the precommitted plan path")
    if inline is not None and _review_plan_root(inline) != precommitted:
        raise LaunchRefused("review handoff inline plan differs from the precommitted plan")
    required = {
        "claim_under_review", "coordinator_prior", "recorded_before_reviewers",
        "source_snapshot", "joints", "blindness", "proves_too_much",
        "blind_rederivation", "procedure_deviations",
    }
    if not required.issubset(precommitted):
        raise LaunchRefused("review plan omits a governed subsection")
    for field in ("claim_under_review", "coordinator_prior"):
        if not isinstance(precommitted.get(field), str) or not precommitted[field].strip():
            raise LaunchRefused(f"review plan {field} is empty")
    if precommitted.get("recorded_before_reviewers") is not True:
        raise LaunchRefused("review plan was not recorded before reviewers")
    if precommitted.get("source_snapshot") != reviewed_source_snapshot:
        raise LaunchRefused("review plan does not bind the reviewed source snapshot")
    joints = precommitted.get("joints")
    if not isinstance(joints, list) or not joints:
        raise LaunchRefused("review plan joints is not a nonempty list")
    for index, joint in enumerate(joints):
        if not isinstance(joint, dict):
            raise LaunchRefused(f"review plan joint {index} is not a mapping")
        for field in ("joint", "assigned_to", "attack_plan", "breaking_artifact"):
            if not isinstance(joint.get(field), str) or not joint[field].strip():
                raise LaunchRefused(f"review plan joint {index} has an empty {field}")
    blindness = precommitted.get("blindness")
    if not isinstance(blindness, dict) or not isinstance(blindness.get("mutual"), bool):
        raise LaunchRefused("review plan blindness does not declare mutual as boolean")
    lifted_for = blindness.get("lifted_for", [])
    if not isinstance(lifted_for, list) or not all(isinstance(item, str) and item for item in lifted_for):
        raise LaunchRefused("review plan blindness.lifted_for is malformed")
    if lifted_for and (not isinstance(blindness.get("rationale"), str) or not blindness["rationale"].strip()):
        raise LaunchRefused("review plan blindness lift lacks a rationale")
    proves_too_much = precommitted.get("proves_too_much")
    if not isinstance(proves_too_much, dict):
        raise LaunchRefused("review plan proves_too_much is not a mapping")
    if not isinstance(proves_too_much.get("objects"), list) or not proves_too_much["objects"] or not all(
        isinstance(item, str) and item.strip() for item in proves_too_much["objects"]
    ):
        raise LaunchRefused("review plan proves_too_much objects are empty")
    for field in ("failure_signature", "assigned_to"):
        if not isinstance(proves_too_much.get(field), str) or not proves_too_much[field].strip():
            raise LaunchRefused(f"review plan proves_too_much {field} is empty")
    rederivation = precommitted.get("blind_rederivation")
    if not isinstance(rederivation, dict) or not isinstance(rederivation.get("required"), bool):
        raise LaunchRefused("review plan blind_rederivation is malformed")
    for field in ("quantity", "parameters", "assigned_to"):
        if field in rederivation and (not isinstance(rederivation[field], str) or not rederivation[field].strip()):
            raise LaunchRefused(f"review plan blind_rederivation {field} is empty")
    blind_from = rederivation.get("blind_from", [])
    if not isinstance(blind_from, list) or not all(isinstance(item, str) and item for item in blind_from):
        raise LaunchRefused("review plan blind_rederivation.blind_from is malformed")
    if not isinstance(precommitted.get("procedure_deviations"), list) or not all(
        isinstance(item, str) and item.strip() for item in precommitted["procedure_deviations"]
    ):
        raise LaunchRefused("review plan procedure_deviations is not a text list")
    try:
        problems = review_plan_validator.check(
            precommitted, [(admission["review_report_path"], report_attestation)]
        )
    except Exception as exc:
        raise LaunchRefused(f"source-pinned review-plan validation failed: {exc}") from exc
    if problems:
        raise LaunchRefused(f"source-pinned review-plan validation failed: {problems[0]}")
    return precommitted


def _claimed_task_declaration(task: dict[str, Any]) -> dict[str, Any]:
    frozen = copy.deepcopy(task)
    # These two fields are the only review-task lifecycle bookkeeping admitted
    # after claim.  Every declaration, including dependencies and plan, stays
    # byte-semantic equal after canonical queue normalization.
    frozen.pop("state", None)
    frozen.pop("lease", None)
    return frozen


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
        claimed_queue = json.loads(git_blob_bytes(admission["review_claim_commit"], admission["external_queue_path"]))
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise LaunchRefused(f"archived review receipt/report/plan is unparsable: {exc}") from exc
    review = report.get("validation_report", report.get("review_report", report)) if isinstance(report, dict) else None
    if not isinstance(review, dict):
        raise LaunchRefused("review report does not contain a governed review mapping")
    attestation_for_plan = review.get("review_attestation")
    if not isinstance(attestation_for_plan, dict):
        raise LaunchRefused("review report lacks a plan-checkable attestation")
    with trusted_canonical_validators(reviewed_source_snapshot) as (dispatch, review_plan_validator):
        canonical_queue, by_id = _canonical_queue_copy(queue, dispatch)
        canonical_claimed_queue, claimed_by_id = _canonical_queue_copy(claimed_queue, dispatch)
        review_task = by_id.get(admission["review_task_id"])
        archive_task = by_id.get(admission["archive_task_id"])
        claimed_review_task = claimed_by_id.get(admission["review_task_id"])
        if review_task is None or archive_task is None or claimed_review_task is None:
            raise LaunchRefused("canonical queue omits the review, claimed predecessor, or archive")
        review_handoff_for_plan = review_task.get("handoff")
        if not isinstance(review_handoff_for_plan, dict):
            raise LaunchRefused("canonical review task lacks its handoff")
        validate_complete_review_handoff(
            review_handoff_for_plan, admission["review_task_id"]
        )
        _resolve_and_validate_review_plan(
            handoff=review_handoff_for_plan,
            precommitted_document=plan,
            admission=admission,
            reviewed_source_snapshot=reviewed_source_snapshot,
            report_attestation=attestation_for_plan,
            review_plan_validator=review_plan_validator,
        )
    if claimed_review_task.get("state") != "queued":
        raise LaunchRefused("review task was not queued in the pre-claim governed queue")
    if _claimed_task_declaration(claimed_review_task) != _claimed_task_declaration(review_task):
        raise LaunchRefused("completed review task changed a governed pre-claim declaration")
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
    plan_root = _review_plan_root(plan)
    if git_blob_hash(admission["review_plan_commit"], admission["review_plan_path"]) != admission["review_plan_sha256"]:
        raise LaunchRefused("review plan hash does not match its precommitted bytes")
    if review.get("review_plan_path") != admission["review_plan_path"] or review.get("review_plan_commit") != admission["review_plan_commit"]:
        raise LaunchRefused("review report does not bind the precommitted plan commit")
    plan_required = {"claim_under_review", "coordinator_prior", "recorded_before_reviewers", "source_snapshot", "joints", "blindness", "proves_too_much", "blind_rederivation", "procedure_deviations"}
    if not plan_required.issubset(plan_root) or plan_root.get("recorded_before_reviewers") is not True or plan_root.get("source_snapshot") != reviewed_source_snapshot:
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
        digest = hex_digest(digest, "review source-read hash")
        if git_blob_hash(reviewed_source_snapshot, path) != digest:
            raise LaunchRefused("review source-read hashes do not match the reviewed snapshot")
    binding_by_path = {
        row["path"]: row["sha256"]
        for row in review_handoff.get("source_bindings", [])
        if isinstance(row, dict) and isinstance(row.get("path"), str)
    }
    if any(source_reads.get(path) != digest for path, digest in binding_by_path.items()):
        raise LaunchRefused("review handoff binding digests differ from attested source-read digests")


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
        "amendment_sha256", "driver_sha256", "streaming_sha256", "custody_sha256",
        "execution_plan_sha256", "reviewed_source_snapshot",
        "executing_commit", "runtime", "resource_limits", "review_admission", "run_id", "run_allocation", "signature",
    }
    if set(lock) != required or lock.get("kind") != "coordinator_runtime_execution_lock" or lock.get("approved") is not True:
        raise LaunchRefused("lock lacks the complete Coordinator admission schema")
    canonical_run_id(lock["run_id"])
    if {"experiment_id": lock["experiment_id"], "approval_decision_id": lock["approval_decision_id"], "amendment_id": lock["amendment_id"], "spec_sha256": lock["spec_sha256"], "amendment_sha256": lock["amendment_sha256"]} != {"experiment_id": EXPERIMENT_ID, "approval_decision_id": APPROVAL_ID, "amendment_id": AMENDMENT_ID, "spec_sha256": SPEC_SHA256, "amendment_sha256": AMENDMENT_SHA256}:
        raise LaunchRefused("lock does not bind the frozen experiment and amendment")
    if sha256_file(SPEC_PATH) != SPEC_SHA256 or sha256_file(AMENDMENT_PATH) != AMENDMENT_SHA256:
        raise LaunchRefused("frozen source bytes differ from the approved bindings")
    if (
        lock["driver_sha256"] != sha256_file(Path(__file__))
        or lock["streaming_sha256"] != sha256_file(STREAMING_PATH)
        or lock["custody_sha256"] != sha256_file(CUSTODY_PATH)
        or lock["execution_plan_sha256"] != sha256_file(PLAN_PATH)
    ):
        raise LaunchRefused("lock source-module or execution-plan hash differs from executing bytes")
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    if (
        plan.get("driver", {}).get("sha256") != sha256_file(Path(__file__))
        or plan.get("streaming", {}).get("sha256") != sha256_file(STREAMING_PATH)
        or plan.get("custody", {}).get("sha256") != sha256_file(CUSTODY_PATH)
        or plan.get("future_operational_custody", {}).get("required_post_boundary_receipt")
        != "runtime-custody/<run_id>/operational-completion.json"
    ):
        raise LaunchRefused("execution plan does not bind current source modules and stable custody namespace")
    if lock["runtime"] != runtime_binding() or lock["resource_limits"] != {"process_group_memory_bytes": MEMORY_LIMIT_BYTES, "maximum_workers": 1}:
        raise LaunchRefused("lock runtime or machine-protection binding differs")
    current_commit = git_output("rev-parse", "HEAD")
    if lock["executing_commit"] != current_commit or git_output("status", "--porcelain"):
        raise LaunchRefused("execution must use the clean lock-bound executing commit")
    source_paths = {
        "specification": (SPEC_PATH, str(SPEC_PATH.relative_to(ROOT)), SPEC_SHA256),
        "amendment": (AMENDMENT_PATH, str(AMENDMENT_PATH.relative_to(ROOT)), AMENDMENT_SHA256),
        "driver": (Path(__file__), str(Path(__file__).resolve().relative_to(ROOT)), lock["driver_sha256"]),
        "streaming": (STREAMING_PATH, str(STREAMING_PATH.resolve().relative_to(ROOT)), lock["streaming_sha256"]),
        "custody": (CUSTODY_PATH, str(CUSTODY_PATH.resolve().relative_to(ROOT)), lock["custody_sha256"]),
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


def _spool_records(
    sink: ProgressSink,
    name: str,
    check: Callable[[], None] | None = None,
) -> Iterable[dict[str, Any]]:
    return iter_jsonl(sink.staging / name, check=check)


def _write_spool_array(
    writer: GuardedDigestWriter,
    sink: ProgressSink,
    name: str,
    transform: Callable[[dict[str, Any]], Any] | None = None,
) -> None:
    records = _spool_records(sink, name, writer.check)
    stream_json_array(
        writer,
        (transform(record) if transform is not None else record for record in records),
    )


class _CsvTextAdapter:
    """Give csv.DictWriter a text API backed by the bounded binary writer."""

    def __init__(self, writer: GuardedDigestWriter) -> None:
        self.writer = writer

    def write(self, text: str) -> int:
        self.writer.write_text(text)
        return len(text)


def _cost_rows(
    sink: ProgressSink,
    check: Callable[[], None] | None = None,
) -> Iterable[dict[str, Any]]:
    secondary_names = (
        "mean_first_repeat_length", "useful_fraction", "fixed_points", "two_cycles",
        "component_sizes", "max_tail_length", "max_cycle_length",
    )
    for cell in _spool_records(sink, "completed-cells.jsonl", check):
        common = {
            "curve_id": cell.get("curve_id"), "seed": cell.get("seed"),
            "u": cell.get("u"), "stream": cell.get("stream"),
            "d": cell.get("metric", {}).get("d"),
        }
        coordinate = cell.get("coordinate", {})
        yield {
            **common, "diagnostic_kind": "collision_census", "arm": "coordinate",
            **{key: coordinate.get(key) for key in (
                "starts", "successes", "transition_group_operations",
                "verification_group_operations", "group_additions",
                "group_doublings", "charged_cost",
            )},
            **coordinate.get("diagnostic_costs", {}),
            **coordinate.get("diagnostic_meter", {}),
            **coordinate.get("secondary", {}),
        }
        for arm in cell.get("nulls", []):
            yield {
                **common, "diagnostic_kind": "collision_census", "arm": arm.get("arm"),
                **{key: arm.get(key) for key in (
                    "starts", "successes", "transition_group_operations",
                    "verification_group_operations", "group_additions",
                    "group_doublings", "charged_cost",
                )},
                **arm.get("diagnostic_costs", {}),
                **arm.get("diagnostic_meter", {}),
                **arm.get("secondary", {}),
            }
        for name, cost in cell.get("diagnostic_costs", {}).items():
            entries = cost if isinstance(cost, list) else [cost]
            for entry in entries:
                yield {
                    **common, "diagnostic_kind": name, "arm": entry.get("arm"),
                    "starts": None, "successes": None,
                    "transition_group_operations": None,
                    "verification_group_operations": None,
                    "group_additions": None, "group_doublings": None,
                    "charged_cost": None, **entry,
                }
    for record in _spool_records(sink, "diagnostics.jsonl", check):
        if record.get("completed"):
            continue
        yield {
            "curve_id": None, "seed": None, "u": None, "stream": "partial", "d": None,
            "diagnostic_kind": record.get("diagnostic"), "arm": None,
            "starts": None, "successes": None,
            "transition_group_operations": None,
            "verification_group_operations": None,
            "group_additions": None, "group_doublings": None,
            "charged_cost": None, **record,
        }


def artifact_producers(
    *,
    lock: dict[str, Any],
    provenance: dict[str, Any],
    meter: ResourceMeter,
    sink: ProgressSink,
    status: str,
    error: str | None,
    decision: dict[str, Any],
) -> dict[str, Callable[[GuardedDigestWriter], None]]:
    """Return small producer closures; no closure contains complete artifact bytes."""
    resource_snapshot = meter.snapshot(finish=False)
    timing = resource_snapshot["timing"]
    retained_coverage = {
        "accepted_fixture_count": sink.accepted_fixture_count,
        "rejected_fixture_candidate_count": sink.rejected_fixture_count,
        "completed_cell_count": sink.completed_cell_count,
        "cells_by_stream": dict(sink.cells_by_stream),
        "seeds_by_stream": {
            stream: sorted(seeds) for stream, seeds in sink.seeds_by_stream.items()
        },
        "partial_certificate_count": sink.partial_certificate_count,
        "scientific_certificate_count": sink.scientific_certificate_count,
        "diagnostic_row_count": sink.diagnostic_row_count,
        "progress_event_count": sink.progress_event_count,
        "progress_event_bytes": sink.progress_bytes,
        "progress_latest_checkpoint_bytes": sink.latest_checkpoint_bytes,
    }
    metrics = {
        "global_decision": decision,
        "cells_recorded": sink.completed_cell_count,
        "rejected_fixture_candidates": sink.rejected_fixture_count,
        "retained_coverage": retained_coverage,
        "availability": {
            "available": sink.available_cell_count,
            "unavailable": sink.unavailable_cell_count,
        },
        "streamed_histories": {
            "cells": "raw.jsonl",
            "controls": "controls.json",
            "certificates": "certificates.json",
            "costs": "costs.csv",
        },
    }
    valid = status == "completed_valid"
    try:
        final_rss_boundary_sample: int | None = process_group_rss_bytes()
    except InfrastructureStop:
        final_rss_boundary_sample = None
    manifest = {
        "run": {
            "id": lock["run_id"], "experiment_id": EXPERIMENT_ID, "status": status,
            "code": provenance,
            "inference": {
                "requested_policy": "executor-implementation",
                "canonical_policy": "executor-implementation", "backend": None,
                "provider": None, "resolved_model_id": None,
                "model_provenance": "not-applicable", "model_verified": False,
                "requested_reasoning_effort": "xhigh", "reasoning_effort": "xhigh",
                "fallback_used": False, "fallback_reason": None,
                "degraded_requirements": [], "independent_session": False,
                "adapter_version": None, "config_digest": None,
            },
            "environment": {
                "operating_system": platform.platform(), "architecture": platform.machine(),
                "sage_version": None, "python_version": sys.version,
                "dependencies": {"mpmath": mp.__version__, "pyyaml": yaml.__version__},
            },
            "inputs": {
                "curve_id": None, "seed": None,
                "parameters": {
                    "frozen_exploratory_seeds": list(EXPLORATORY_SEEDS),
                    "frozen_heldout_seeds": list(HELDOUT_SEEDS), "u": list(US),
                },
            },
            "timing": {
                **timing,
                "wall_seconds": resource_snapshot["wall_seconds"],
                "timing_source": "payload_observed_boundary_before_durable_publication",
                "final_operational_receipt":
                    f"runtime-custody/{lock['run_id']}/operational-completion.json",
            },
            "resources": {
                "rss_boundary_sample_bytes": final_rss_boundary_sample,
                "rss_sample_scope": "one_payload_assembly_boundary_sample",
                "cpu_seconds": resource_snapshot["cpu_seconds"],
                "process_group_memory_limit_bytes": MEMORY_LIMIT_BYTES,
                "stage_costs": resource_snapshot["stages"],
            },
            "result": {
                "metrics": metrics, "valid": valid, "invalid_reason": error,
                "certificate": {
                    "kind": "none", "verified": True,
                    "verifier": "not-applicable-no-solve-claim",
                },
            },
            "artifacts": {
                "command": "command.txt", "environment": "environment.json",
                "stdout": "stdout.log", "stderr": "stderr.log",
                "raw_result": "raw-result.json", "integrity": "package-sha256.json",
            },
        }
    }
    bounded_graph_size(manifest, maximum_bytes=SMALL_MANIFEST_GRAPH_LIMIT_BYTES)

    def manifest_writer(writer: GuardedDigestWriter) -> None:
        # Canonical JSON is a YAML 1.2 document and preserves the checked string
        # key/value types without invoking an unguarded monolithic YAML dumper.
        write_json_document(writer, manifest)

    def fixtures_writer(writer: GuardedDigestWriter) -> None:
        writer.write(b'{"accepted":')
        _write_spool_array(writer, sink, "fixture-selections.jsonl")
        writer.write(b',"rejected":')
        _write_spool_array(writer, sink, "fixture-rejections.jsonl")
        writer.write(b"}\n")

    def raw_writer(writer: GuardedDigestWriter) -> None:
        path = sink.staging / "completed-cells.jsonl"
        if path.exists():
            copy_file(path, writer, check=writer.check)

    def controls_writer(writer: GuardedDigestWriter) -> None:
        _write_spool_array(
            writer,
            sink,
            "completed-cells.jsonl",
            lambda row: {
                "curve_id": row.get("curve_id"), "seed": row.get("seed"),
                "u": row.get("u"), "controls": row.get("controls"),
                "validity": row.get("validity"),
            },
        )
        writer.write(b"\n")

    def certificates_writer(writer: GuardedDigestWriter) -> None:
        writer.write(b'{"partial_certificates":')
        _write_spool_array(writer, sink, "partial-certificates.jsonl")
        writer.write(b',"scientific_records":')
        _write_spool_array(writer, sink, "scientific-certificates.jsonl")
        writer.write(b"}\n")

    def costs_writer(writer: GuardedDigestWriter) -> None:
        secondary_names = (
            "mean_first_repeat_length", "useful_fraction", "fixed_points",
            "two_cycles", "component_sizes", "max_tail_length", "max_cycle_length",
        )
        fieldnames = [
            "curve_id", "seed", "u", "stream", "diagnostic_kind", "arm",
            "starts", "successes", "transition_group_operations",
            "verification_group_operations", "group_additions", "group_doublings",
            "charged_cost", "scalar_inversions", "scalar_comparisons", "diagnostic",
            "partition_queries", "rng_counter_end", "diagnostic_wall_seconds",
            "diagnostic_cpu_seconds", "collision_table_peak_bytes", "completed", "error",
            "process_group_rss_start_bytes", "process_group_rss_end_bytes",
            "process_group_rss_boundary_sample_max_bytes",
            "process_group_rss_sample_scope", "process_group_rss_sample_cadence",
            "process_group_rss_error", *secondary_names, "d",
        ]
        csv_writer = csv.DictWriter(
            _CsvTextAdapter(writer), fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        csv_writer.writeheader()
        for row in _cost_rows(sink, writer.check):
            csv_writer.writerow(row)

    def report_writer(writer: GuardedDigestWriter) -> None:
        writer.write_text(
            "\n".join(
                [
                    f"# {EXPERIMENT_ID} future-run record", "",
                    f"Status: `{status}`.",
                    f"Global finite decision from the 96 held-out cells only: `{decision.get('branch', 'inconclusive')}`.",
                    "Large cells, certificates, controls, and diagnostic costs were emitted from append-only spools.",
                    f"The terminal operational receipt is retained at `runtime-custody/{lock['run_id']}/operational-completion.json` after durable payload publication.",
                    "The receipt excludes its own write/fsync duration and contains no self-hash.",
                    "The Cayley gap remains a separate reversible calibration and is not a rho spectral claim.",
                    f"Operational detail: {error or 'none'}.", "",
                ]
            )
        )

    def raw_result_writer(writer: GuardedDigestWriter) -> None:
        write_json_document(
            writer,
            {
                "metrics": metrics,
                "certificate": manifest["run"]["result"]["certificate"],
                "raw": {
                    "completed_cells_path": "raw.jsonl",
                    "certificates_path": "certificates.json",
                    "progress_events_retained_during_execution": sink.progress_event_count,
                    "error": error,
                },
            },
        )

    return {
        "manifest.yaml": manifest_writer,
        "fixtures.json": fixtures_writer,
        "raw.jsonl": raw_writer,
        "controls.json": controls_writer,
        "costs.csv": costs_writer,
        "certificates.json": certificates_writer,
        "stdout.log": lambda writer: None,
        "stderr.log": lambda writer: writer.write_text((error or "") + "\n"),
        "report.md": report_writer,
        "command.txt": lambda writer: writer.write_text(provenance["command"] + "\n"),
        "environment.json": lambda writer: write_json_document(writer, runtime_binding()),
        "raw-result.json": raw_result_writer,
    }


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


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
    primary_stop: BaseException | None = None
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
                                    # Scientific certificates have their own append-only
                                    # spool and do not consume the compact progress budget.
                                    sink.record_scientific_certificate({**base, "certificate": certificate})
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
        decision = global_decision(sink.decision_cells)
        status = "completed_valid" if decision["panel_valid"] else "completed_invalid"
        error = None if decision["panel_valid"] else ";".join(decision["reasons"])
        meter.exit("report")
        guard.check(force=True)
    except MeasurementInvalidStop as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "completed_invalid", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["frozen_validity_failure_immediate_stop"], "per_u": {}}
    except IncompleteFixtureStop as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "incomplete_fixture_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["incomplete_frozen_fixture_panel"], "per_u": {}}
    except CancellationStop as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "cancelled_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_cancellation"], "per_u": {}}
    except ResourceStop as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "resource_exhaustion_inconclusive", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_resource_stop"], "per_u": {}}
    except InfrastructureStop as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "failed_infrastructure", str(exc)
        decision = {"branch": "inconclusive", "reasons": ["operational_infrastructure_failure"], "per_u": {}}
    except Exception as exc:
        sink.flush_required_prefix()
        primary_stop = exc
        status, error = "failed_implementation", f"implementation_error: {type(exc).__name__}: {exc}"
        decision = {"branch": "inconclusive", "reasons": ["implementation_exception"], "per_u": {}}
    finally:
        meter.close_active()
    try:
        provenance = execution_provenance(command)
        meter.enter("artifact_producer_setup")
        producers = artifact_producers(
            lock=lock,
            provenance=provenance,
            meter=meter,
            sink=sink,
            status=status,
            error=error,
            decision=decision,
        )
        meter.exit("artifact_producer_setup")
        result: FinalizationResult = finalize_run(
            run_root=run_root,
            run_id=lock["run_id"],
            artifact_order=EXPERIMENT_ARTIFACTS,
            producers=producers,
            integrity_name="package-sha256.json",
            meter=meter,
            guard_telemetry=guard.telemetry,
            primary_stop=primary_stop,
            check=guard.check,
            on_progress=None,
            cleanup_paths=(progress_dir,),
        )
        return result.payload_artifact_sha256
    except (CancellationStop, ResourceStop, InfrastructureStop, MeasurementInvalidStop, IncompleteFixtureStop):
        raise
    except Exception as exc:
        raise InfrastructureStop(
            f"streaming artifact finalization failed with retained custody: {exc}"
        ) from exc
    finally:
        for signum, handler in original_handlers.items():
            signal.signal(signum, handler)


def protocol_coverage() -> dict[str, str]:
    return {
        "F-01_fixture_rejections": "fixture_scan/select_fixtures",
        "F-02_constant_O_execution": "constant_o_census",
        "F-03_validity_reduction": "reduce_validity/collision_census",
        "F-04_manifest_companions": "artifact_producers/custody.finalize_run",
        "F-05_incremental_progress": "ProgressSink/Guard/run_future_pipeline",
        "F-06_memory_and_advisory_costs": "process_group_rss_bytes/ResourceMeter",
        "F-07_atomic_publication": "custody.finalize_run",
        "F-08_custody_and_decision": "artifact_producers/global_decision/cayley_control",
        "F-09_review_admission": "verify_review_admission/verify_launch_admission",
        "V-01_repeated_addition_subgroup": "enumerate_subgroup",
        "V-02_exploratory_seed_custody": "EXPLORATORY_SEEDS/run_future_pipeline",
        "V-03_immediate_invalid_stop": "MeasurementInvalidStop/run_future_pipeline",
        "V-04_diagnostic_cost_custody": "collision_census/artifact_producers",
        "V-05_terminal_timing_bracket": "ResourceMeter/custody.finalize_run",
        "V-06_postrename_quarantine": "custody.finalize_run",
        "V-07_reviewed_source_execution_separation": "verify_review_admission/verify_launch_admission",
        "V-08_cayley_guard_stride": "_cayley_checkpoint/cayley_control",
        "S2-01_control_rng_pairing": "future_cell/deterministic_shuffle",
        "S2-02_typed_operational_outcomes": "IncompleteFixtureStop/run_future_pipeline",
        "S2-03_partial_coverage_and_cost_custody": "measured_diagnostic/ProgressSink/artifact_producers",
        "S2-04_publication_failure_durability": "custody.finalize_run",
        "S2-05_allocated_canonical_run_root": "canonical_run_id/verify_run_allocation",
        "S2-06_external_review_archive_admission": "verify_review_admission",
        "S2-07_valid_process_group_rss": "process_group_rss_bytes/Guard",
        "S2-08_dense_loop_guard_progress": "guarded_checkpoint/_cayley_checkpoint",
        "S3-01_complete_review_task_claim_and_attestation": "verify_review_admission/queue-relative-write-once-claims",
        "S3-02_parent_directory_fsync_quarantine_durability": "retain_publication_failure",
        "S3-03_failed_scalar_certificate_immediate_stop": "collision_census/MeasurementInvalidStop",
        "S3-04_interrupted_diagnostic_memory_custody": "measured_diagnostic/collision_census_with_custody",
        "S3-05_guarded_progress_through_assembly_publication": "guarded_checkpoint/artifact_producers/custody.finalize_run",
        "S5-01_complete_canonical_review_admission": "trusted_canonical_validators/verify_review_admission",
        "S5-02_streaming_artifacts": "streaming.GuardedDigestWriter/artifact_producers",
        "S5-03_stable_operational_companion": "custody.finalize_run/runtime-custody",
        "S5-04_pre_census_occupancy": "future_cell/prepared_assignments",
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
