#!/usr/bin/env python3
"""Prospective, fail-closed runner for EXP-ECDLP-651b94.

This module contains the complete *future* finite protocol.  Importing it and
the default CLI do no fixture selection, Cayley calibration, collision census,
control panel, or timing measurement.  ``future-run`` is deliberately gated by
an externally authenticated Coordinator lock and a fresh archived review.

The correction successor implements DEC-20260907-38017a.  It is not a launch
lock, a run record, or scientific evidence.
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

TASK_ID = "TASK-20260908-111152"
EXPERIMENT_ID = "EXP-ECDLP-651b94"
APPROVAL_ID = "DEC-20260906-f73475"
AMENDMENT_ID = "DEC-20260907-38017a"
CORRECTION_DECISION_ID = "DEC-20260908-94664e"
SPEC_SHA256 = "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee"
AMENDMENT_SHA256 = "a24e723fa1d499621957e1fd3939d3e95a0e1f9c003412396f6eec00d9052280"
MEMORY_LIMIT_BYTES = 8 * 1024**3
EXPLORATORY_SEEDS = tuple(range(606300, 606308))
HELDOUT_SEEDS = tuple(range(606308, 606316))
US = (1, 2, 3)
CAYLEY_GUARD_STRIDE = 16
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


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
        if on_progress is not None:
            on_progress({"phase": phase, "index": index, "guard_stride": CAYLEY_GUARD_STRIDE, **coordinates})
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
    curve: Curve, generator: Point, r: int, check: Callable[[], None]
) -> tuple[list[Point], dict[str, Any]]:
    """Enumerate O,G,...,(r-1)G through one checked repeated-addition chain.

    The returned certificate is retained with each future cell.  In particular,
    the order check comes from the accumulator after exactly r additions rather
    than recomputing each multiple with scalar multiplication.
    """
    points: list[Point] = []
    current: Point = None
    for scalar in range(r):
        check()
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


def subgroup_points(curve: Curve, generator: Point, r: int, check: Callable[[], None]) -> list[Point]:
    """Compatibility wrapper for callers that only require canonical point order."""
    points, _certificate = enumerate_subgroup(curve, generator, r, check)
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
        check()
        state, A, B = curve.scalar(start, G), start, 0
        seen: dict[Point, tuple[int, int, int]] = {state: (A, B, 0)}
        trace: list[Point] = [state]
        for step in range(1, r + 2):
            check()
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


def constant_o_census(
    starts: Sequence[Point], check: Callable[[], None], on_certificate: Callable[[dict[str, Any]], None] | None = None
) -> dict[str, Any]:
    """Execute the known-false reset map for every start and retain every collision.

    The first transition is the constant O map and resets labels to (0,0).  A
    non-O start repeats O on the second transition; O itself repeats on the
    first.  This is intentionally a separate census, not a Boolean assertion.
    """
    certificates: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        check()
        seen: dict[Point, tuple[int, int, int]] = {start: (index, 0, 0)}
        state: Point = start
        A = B = 0
        for step in range(1, 3):
            check()
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
    """Return a prospective result and custody row, including failed partial work."""
    started_wall = time.monotonic()
    started_cpu = time.process_time()
    try:
        result = action()
    except Exception as exc:
        failed = {
            "diagnostic": name,
            "diagnostic_wall_seconds": time.monotonic() - started_wall,
            "diagnostic_cpu_seconds": time.process_time() - started_cpu,
            "completed": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
        if on_record:
            on_record(failed)
        raise
    record = {
        "diagnostic": name,
        "diagnostic_wall_seconds": time.monotonic() - started_wall,
        "diagnostic_cpu_seconds": time.process_time() - started_cpu,
        "completed": True,
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
    (points, subgroup_certificate), subgroup_cost = measured_diagnostic(
        "subgroup_enumeration",
        lambda: enumerate_subgroup(transported_curve, transported_G, r, check),
        on_diagnostic,
    )
    def coordinate_partition() -> dict[Point, int]:
        values: dict[Point, int] = {}
        for point_index, point in enumerate(points):
            guarded_checkpoint(check, point_index, "coordinate_partition", None, point_index=point_index)
            values[point] = 0 if point is None else point[0] % 3
        return values

    coordinate, partition_cost = measured_diagnostic("coordinate_partition_queries", coordinate_partition, on_diagnostic)
    partition_cost["partition_queries"] = len(points)
    curve_id = f"p{curve.p}-B{curve.B}"
    coordinate_result = collision_census(
        transported_curve, transported_G, transported_Q, r, coordinate, check,
        lambda certificate: on_partial("coordinate", 0, certificate) if on_partial else None,
    )
    coordinate_values = [coordinate[point] for point in points]
    shuffles: list[dict[str, Any]] = []
    shuffle_costs: list[dict[str, Any]] = []
    for arm in range(1, 8):
        check()
        params = (curve.p, curve.A, curve.B, r, 0, u, arm)
        shuffle_progress = lambda state, arm=arm: on_partial("shuffle", arm, state) if on_partial else None
        (assignment, consumed), shuffle_cost = measured_diagnostic(
            "shuffle_construction",
            lambda: occupancy_assignment(points, coordinate_values, params=params, seed=seed, check=check, on_progress=shuffle_progress),
            on_diagnostic,
        )
        shuffle_cost.update({"arm": arm, "partition_queries": len(points), "rng_counter_end": consumed})
        shuffle_costs.append(shuffle_cost)
        result = collision_census(
            transported_curve, transported_G, transported_Q, r, assignment, check,
            lambda certificate, arm=arm: on_partial("null", arm, certificate) if on_partial else None,
        )
        result["arm"] = arm
        result["rng_counter_end"] = consumed
        result["bucket_counts"] = [sum(value == bucket for value in assignment.values()) for bucket in range(3)]
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
    constant_o, constant_o_cost = measured_diagnostic(
        "constant_o_census",
        lambda: constant_o_census(points, check, lambda certificate: on_partial("constant_o", 0, certificate) if on_partial else None),
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
            lambda state: on_partial("cayley", -1, state) if on_partial else None,
        ),
        on_diagnostic,
    )
    controls = {
        "cayley": cayley, "relabel": relabel,
        "occupancy": all(row["bucket_counts"] == [sum(value == bucket for value in coordinate.values()) for bucket in range(3)] for row in shuffles),
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

    def snapshot(self) -> dict[str, Any]:
        self.finish()
        if self.finished_at_utc is None or self.finished_wall is None or self.finished_cpu is None:
            raise InfrastructureStop("resource meter did not capture a terminal timing bracket")
        return {
            "wall_seconds": self.finished_wall - self.started_wall,
            "cpu_seconds": self.finished_cpu - self.started_cpu,
            "timing": {
                "started_at": self.started_at_utc.isoformat(),
                "finished_at": self.finished_at_utc.isoformat(),
                "monotonic_started": self.started_wall,
                "monotonic_finished": self.finished_wall,
                "utc_interval_seconds": (self.finished_at_utc - self.started_at_utc).total_seconds(),
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
    events: list[dict[str, Any]] = field(default_factory=list)

    def _append(self, name: str, record: dict[str, Any]) -> None:
        target = self.staging / name
        with target.open("ab") as handle:
            handle.write(canonical_json(record) + b"\n")
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
        self.checkpoint("start_completed")

    def record_cell(self, record: dict[str, Any]) -> None:
        self.cells.append(record)
        self._append("completed-cells.jsonl", record)
        self.checkpoint("cell_completed")

    def record_diagnostic(self, record: dict[str, Any]) -> None:
        """Retain a completed or interrupted diagnostic cost before later work."""
        self.diagnostics.append(record)
        self._append("diagnostics.jsonl", record)
        self.checkpoint("diagnostic_recorded")

    def checkpoint(self, event: str) -> None:
        self.events.append({"event": event, "at": datetime.now(timezone.utc).isoformat()})
        data = canonical_json({"counts": {"fixtures": len(self.fixtures), "rejected": len(self.rejected), "cells": len(self.cells), "partial_certificates": len(self.partial_certificates), "diagnostics": len(self.diagnostics)}, "events": self.events})
        target = self.staging / "progress.json"
        with target.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())


@dataclass
class Guard:
    sink: ProgressSink
    cancelled: bool = False
    limit_bytes: int = MEMORY_LIMIT_BYTES

    def check(self) -> None:
        if self.cancelled:
            raise CancellationStop("operator cancellation observed")
        rss = process_group_rss_bytes()
        if rss > self.limit_bytes:
            raise ResourceStop(f"process-group RSS {rss} exceeds {self.limit_bytes}")


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
    }
    if set(admission) != required:
        raise LaunchRefused("review admission has missing or surplus fields")
    if admission["reviewed_source_snapshot"] != reviewed_source_snapshot or admission["required_verdict"] != "PASS":
        raise LaunchRefused("review admission does not name this reviewed source snapshot and PASS gate")
    if git_output("rev-parse", "HEAD") != executing_commit:
        raise LaunchRefused("executing checkout HEAD differs from lock executing_commit")
    require_commit_ancestor(reviewed_source_snapshot, admission["archive_commit"], "reviewed source snapshot precedes review archive")
    require_commit_ancestor(admission["review_plan_commit"], admission["archive_commit"], "precommitted review plan precedes review archive")
    require_commit_ancestor(admission["archive_commit"], admission["external_authority_commit"], "review archive precedes external queue authority")
    require_commit_ancestor(admission["external_authority_commit"], executing_commit, "external queue authority precedes executing commit")
    queue_bytes = git_blob_bytes(admission["external_authority_commit"], admission["external_queue_path"])
    if sha256_bytes(queue_bytes) != admission["external_queue_sha256"]:
        raise LaunchRefused("external queue bytes differ from the signed review admission")
    try:
        queue = json.loads(queue_bytes)
        receipt = json.loads(git_blob_bytes(admission["archive_commit"], admission["snapshot_receipt_path"]))
        report = yaml.safe_load(git_blob_bytes(admission["archive_commit"], admission["review_report_path"]))
        plan = yaml.safe_load(git_blob_bytes(admission["review_plan_commit"], admission["review_plan_path"]))
    except (json.JSONDecodeError, yaml.YAMLError) as exc:
        raise LaunchRefused(f"archived review receipt/report/plan is unparsable: {exc}") from exc
    if not isinstance(queue, dict) or not isinstance(queue.get("tasks"), list):
        raise LaunchRefused("external authority queue has no task list")
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
    review = report.get("validation_report", report.get("review_report", report)) if isinstance(report, dict) else {}
    if review.get("task_id") != admission["review_task_id"] or review.get("source_snapshot_commit") != reviewed_source_snapshot:
        raise LaunchRefused("review report does not attest the corrected source snapshot")
    if review.get("role") not in {"reviewer", "validator", "red-team"} or not isinstance(review.get("claim_owner"), str) or not review["claim_owner"] or not isinstance(review.get("claim_session"), str) or not review["claim_session"] or not isinstance(review.get("claim_epoch"), int) or review["claim_epoch"] < 1:
        raise LaunchRefused("review report lacks independent session/claim provenance")
    if review.get("owned_joint_verdict") not in {"PASS", "PASSED"} or review.get("verdict") not in {"pass", "passed", "PASS"}:
        raise LaunchRefused("review report did not pass the admitted implementation joint")
    inference = review.get("inference")
    if not isinstance(inference, dict) or inference.get("requested_policy") != "review-adversarial" or inference.get("reasoning_effort") != "xhigh" or inference.get("independent_session") is not True:
        raise LaunchRefused("review report lacks the independent review-adversarial inference envelope")
    if not isinstance(inference.get("resolved_model_id"), str) or not inference["resolved_model_id"] or not isinstance(inference.get("provenance"), str) or not inference["provenance"] or inference.get("fallback_used") is not False or inference.get("degraded_used") is not False or inference.get("bedrock_used") is not False:
        raise LaunchRefused("review inference provenance is incomplete or permissive")
    attestation = review.get("review_attestation")
    if not isinstance(attestation, dict) or attestation.get("complete_source_read") is not True or attestation.get("review_plan_path") != admission["review_plan_path"]:
        raise LaunchRefused("review report lacks a complete-source/read-plan attestation")
    source_reads = attestation.get("source_reads")
    if not isinstance(source_reads, dict):
        raise LaunchRefused("review report lacks exact source-read hashes")
    resolved_root = ROOT.resolve()
    required_reads = {
        str(Path(__file__).resolve().relative_to(resolved_root)),
        str(PLAN_PATH.resolve().relative_to(resolved_root)),
        str(SPEC_PATH.resolve().relative_to(resolved_root)),
        str(AMENDMENT_PATH.resolve().relative_to(resolved_root)),
    }
    if not required_reads.issubset(source_reads) or any(git_blob_hash(reviewed_source_snapshot, path) != source_reads[path] for path in required_reads):
        raise LaunchRefused("review source-read hashes do not match the reviewed snapshot")
    if not isinstance(plan, dict):
        raise LaunchRefused("review plan is not a mapping")
    plan_root = plan.get("review_plan", plan)
    if git_blob_hash(admission["review_plan_commit"], admission["review_plan_path"]) != admission["review_plan_sha256"]:
        raise LaunchRefused("review plan hash does not match its precommitted bytes")
    if review.get("review_plan_path") != admission["review_plan_path"] or review.get("review_plan_commit") != admission["review_plan_commit"]:
        raise LaunchRefused("review report does not bind the precommitted plan commit")
    if not isinstance(plan_root, dict) or plan_root.get("recorded_before_reviewers") is not True or plan_root.get("source_snapshot") != reviewed_source_snapshot:
        raise LaunchRefused("review plan does not precommit this source snapshot")
    joints = plan_root.get("joints")
    if not isinstance(joints, list) or not any(isinstance(joint, dict) and joint.get("assigned_to") == admission["review_task_id"] for joint in joints):
        raise LaunchRefused("review plan does not assign an owned joint to the admitted reviewer")


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
    *, lock: dict[str, Any], provenance: dict[str, Any], meter: ResourceMeter, sink: ProgressSink, status: str, error: str | None, decision: dict[str, Any]
) -> dict[str, bytes]:
    resource_snapshot = meter.snapshot()
    timing = resource_snapshot["timing"]
    secondary_names = (
        "mean_first_repeat_length", "useful_fraction", "fixed_points", "two_cycles",
        "component_sizes", "max_tail_length", "max_cycle_length",
    )
    secondary_by_diagnostic: dict[str, dict[str, Any]] = {}
    diagnostic_costs: dict[str, Any] = {}
    for cell in sink.cells:
        cell_key = f"{cell.get('curve_id')}:{cell.get('seed')}:{cell.get('u')}"
        for arm_name, result in [("coordinate", cell.get("coordinate", {}))] + [
            (f"null-{arm.get('arm')}", arm) for arm in cell.get("nulls", [])
        ]:
            key = f"{cell_key}:{arm_name}"
            secondary_by_diagnostic[key] = dict(result.get("secondary", {}))
            diagnostic_costs[key] = dict(result.get("diagnostic_costs", {}))
        for name, cost in cell.get("diagnostic_costs", {}).items():
            if isinstance(cost, list):
                for item in cost:
                    diagnostic_costs[f"{cell_key}:{name}:{item.get('arm')}"] = item
            else:
                diagnostic_costs[f"{cell_key}:{name}"] = cost
    for index, record in enumerate(sink.diagnostics):
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
        final_rss: int | None = process_group_rss_bytes()
    except InfrastructureStop:
        # A prior operational failure may have made ps unavailable.  Preserve
        # the partial package and disclose that final RSS was unavailable.
        final_rss = None
    manifest = {
        "run": {
            "id": lock["run_id"], "experiment_id": EXPERIMENT_ID, "status": status,
            "code": provenance, "inference": {"requested_policy": "executor-implementation", "canonical_policy": "executor-implementation", "backend": None, "provider": None, "resolved_model_id": None, "model_provenance": "not-applicable", "model_verified": False, "requested_reasoning_effort": "xhigh", "reasoning_effort": "xhigh", "fallback_used": False, "fallback_reason": None, "degraded_requirements": [], "independent_session": False, "adapter_version": None, "config_digest": None},
            "environment": {"operating_system": platform.platform(), "architecture": platform.machine(), "sage_version": None, "python_version": sys.version, "dependencies": {"mpmath": mp.__version__, "pyyaml": yaml.__version__}},
            "inputs": {
                "curve_id": None, "seed": None,
                "parameters": {"frozen_exploratory_seeds": list(EXPLORATORY_SEEDS), "frozen_heldout_seeds": list(HELDOUT_SEEDS), "u": list(US)},
            },
            "timing": {**timing, "wall_seconds": resource_snapshot["wall_seconds"], "timing_source": "runner_terminal_bracket"},
            "resources": {"peak_rss_bytes": final_rss, "cpu_seconds": resource_snapshot["cpu_seconds"], "process_group_memory_limit_bytes": MEMORY_LIMIT_BYTES, "stage_costs": resource_snapshot["stages"]},
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
    for row in sink.cells:
        common = {"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "stream": row.get("stream"), "d": row.get("metric", {}).get("d")}
        coordinate = row.get("coordinate", {})
        cost_rows.append({
            **common, "diagnostic_kind": "collision_census", "arm": "coordinate",
            **{key: coordinate.get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")},
            **coordinate.get("diagnostic_costs", {}), **coordinate.get("secondary", {}),
        })
        for arm in row.get("nulls", []):
            cost_rows.append({
                **common, "diagnostic_kind": "collision_census", "arm": arm.get("arm"),
                **{key: arm.get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")},
                **arm.get("diagnostic_costs", {}), **arm.get("secondary", {}),
            })
        for name, cost in row.get("diagnostic_costs", {}).items():
            entries = cost if isinstance(cost, list) else [cost]
            for entry in entries:
                cost_rows.append({
                    **common, "diagnostic_kind": name, "arm": entry.get("arm"), "starts": None, "successes": None,
                    "transition_group_operations": None, "verification_group_operations": None, "group_additions": None,
                    "group_doublings": None, "charged_cost": None, **entry,
                })
    for record in sink.diagnostics:
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
        *secondary_names, "d",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cost_rows)
    output.seek(0)
    costs = output.read().encode("utf-8")
    output.close()
    raw_lines = b"".join(canonical_json(row) + b"\n" for row in sink.cells)
    report = "\n".join([
        f"# {EXPERIMENT_ID} future-run record", "", f"Status: `{status}`.",
        f"Global finite decision from the 96 held-out cells only: `{decision.get('branch', 'inconclusive')}`.",
        f"Execution timing bracket: `{timing['started_at']}` to `{timing['finished_at']}`; monotonic wall seconds: `{resource_snapshot['wall_seconds']}`.",
        f"Actual retained coverage: `{json.dumps(retained_coverage, sort_keys=True)}`.",
        f"Actual secondary values: `{json.dumps(secondary_by_diagnostic, sort_keys=True)}`.",
        f"Actual diagnostic costs: `{json.dumps(diagnostic_costs, sort_keys=True)}`.",
        "The Cayley gap is a separate reversible calibration and is not a rho spectral claim.",
        "Routine wall/CPU estimates are measured and reported, but DEC-20260907-38017a supersedes their historical stop/invalidation semantics.",
        f"Operational detail: {error or 'none'}.", "",
    ]).encode("utf-8")
    command = provenance["command"] + "\n"
    environment = canonical_json(runtime_binding()) + b"\n"
    raw_result = canonical_json({"metrics": metrics, "certificate": manifest["run"]["result"]["certificate"], "raw": {"events": sink.events, "partial_certificates": sink.partial_certificates, "error": error}}) + b"\n"
    return {
        "manifest.yaml": yaml.safe_dump(manifest, sort_keys=False).encode("utf-8"),
        "fixtures.json": canonical_json(fixtures) + b"\n", "raw.jsonl": raw_lines,
        "controls.json": canonical_json(controls) + b"\n", "costs.csv": costs,
        "certificates.json": canonical_json(certificates) + b"\n", "stdout.log": b"",
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
    }
    if source is None:
        return outcome
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
                incomplete = runs / "incomplete"
                incomplete.mkdir(exist_ok=True)
                outcome["quarantine_attempted"] = True
                retained = incomplete / f"{run_id}-{uuid.uuid4().hex[:12]}"
                os.rename(final, retained)
                fsync_directory(incomplete)
                outcome.update({"retained_path": str(retained), "quarantine_complete": True})
            except OSError as quarantine_error:
                outcome["quarantine_error"] = f"{type(quarantine_error).__name__}: {quarantine_error}"
        return outcome
    try:
        incomplete = runs / "incomplete"
        incomplete.mkdir(exist_ok=True)
        retained = incomplete / f"{run_id}-{uuid.uuid4().hex[:12]}"
        outcome["quarantine_attempted"] = True
        os.rename(source, retained)
        fsync_directory(incomplete)
        try:
            fsync_directory(runs)
        except OSError:
            # The incomplete receipt and move are already the durable state;
            # retain the secondary parent-fsync error in the caller's message.
            pass
        outcome.update({"retained_path": str(retained), "state": "quarantined", "quarantine_complete": True})
    except OSError as retain_error:
        outcome.update({"state": "annotated_final" if final.exists() else "unretained", "retention_error": f"{type(retain_error).__name__}: {retain_error}"})
    return outcome


def atomic_publish(run_root: Path, run_id: str, payload: dict[str, bytes]) -> dict[str, str]:
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
        hashes = {name: sha256_bytes(value) for name, value in payload.items()}
        complete = dict(payload)
        complete["package-sha256.json"] = canonical_json({"artifact_sha256": hashes}) + b"\n"
        for name, value in complete.items():
            target = staging / name
            with target.open("xb") as handle:
                handle.write(value)
                handle.flush()
                os.fsync(handle.fileno())
        publication_phase = "staging_hash_verification"
        for name, digest in hashes.items():
            if sha256_file(staging / name) != digest:
                raise InfrastructureStop(f"staged artifact hash mismatch: {name}")
        if set(path.name for path in staging.iterdir()) != set(EXPERIMENT_ARTIFACTS):
            raise InfrastructureStop("staged canonical artifact set is incomplete")
        publication_phase = "pre_rename_durability"
        fsync_directory(staging)
        fsync_directory(runs)
        if final.exists():
            raise LaunchRefused("final run directory appeared during publication")
        publication_phase = "rename_to_canonical_final"
        os.rename(staging, final)  # same filesystem because staging is a sibling of final
        publication_phase = "post_rename_durability"
        fsync_directory(runs)
        return hashes
    except Exception as exc:
        retention = retain_publication_failure(
            runs=runs, run_id=run_id, staging=staging, final=final, error=exc, phase=publication_phase,
        )
        raise InfrastructureStop(
            f"atomic publication failed at {publication_phase}; durable state={retention['state']}; "
            f"failure receipt retained if possible: {exc}"
        ) from exc


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
    try:
        meter.enter("prepare")
        selected, _rejected = select_fixtures(guard.check, sink)
        sink.checkpoint("fixtures_completed")
        meter.exit("prepare")
        meter.enter("census")
        for stream, seeds in (("exploratory", EXPLORATORY_SEEDS), ("heldout", HELDOUT_SEEDS)):
            for rows in selected.values():
                for fixture in rows:
                    for seed in seeds:
                        for u in US:
                            guard.check()
                            curve_id = f"p{fixture['p']}-B{fixture['B']}"

                            def record_partial(kind: str, arm: int, certificate: dict[str, Any]) -> None:
                                sink.record_partial({"curve_id": curve_id, "seed": seed, "u": u, "kind": kind, "arm": arm, "certificate": certificate})

                            cell = future_cell(fixture, seed, u, guard.check, record_partial, sink.record_diagnostic)
                            cell["stream"] = stream
                            sink.record_cell(cell)
                            if not cell["validity"]["valid"]:
                                sink.checkpoint("measurement_invalid_stop")
                                raise MeasurementInvalidStop(
                                    f"frozen validity failure at stream={stream} curve={curve_id} seed={seed} u={u}"
                                )
        meter.exit("census")
        meter.enter("report")
        heldout_cells = [cell for cell in sink.cells if cell.get("stream") == "heldout"]
        decision = global_decision(heldout_cells)
        status = "completed_valid" if decision["panel_valid"] else "completed_invalid"
        error = None if decision["panel_valid"] else ";".join(decision["reasons"])
        meter.exit("report")
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
        meter.finish()
        for signum, handler in original_handlers.items():
            signal.signal(signum, handler)
    provenance = execution_provenance(command)
    payload = artifact_bytes(lock=lock, provenance=provenance, meter=meter, sink=sink, status=status, error=error, decision=decision)
    try:
        return atomic_publish(run_root, lock["run_id"], payload)
    finally:
        shutil.rmtree(progress_dir, ignore_errors=True)


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
