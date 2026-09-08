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

TASK_ID = "TASK-20260907-fde47b"
EXPERIMENT_ID = "EXP-ECDLP-651b94"
APPROVAL_ID = "DEC-20260906-f73475"
AMENDMENT_ID = "DEC-20260907-38017a"
SPEC_SHA256 = "97b44f40c8f9d52a587cf4fd9788dd391e42ce5c6dab8ec212a8af34cdfa4eee"
AMENDMENT_SHA256 = "a24e723fa1d499621957e1fd3939d3e95a0e1f9c003412396f6eec00d9052280"
MEMORY_LIMIT_BYTES = 8 * 1024**3
HELDOUT_SEEDS = tuple(range(606308, 606316))
US = (1, 2, 3)
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


def deterministic_shuffle(
    values: Iterable[Any], *, purpose: str, params: Sequence[int], seed: int, counter: int = 0
) -> tuple[list[Any], int]:
    result = list(values)
    for index in range(len(result) - 1, 0, -1):
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
            raise LaunchRefused(f"frozen fixture panel incomplete for b={bits}; no widening permitted")
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


def subgroup_points(curve: Curve, generator: Point, r: int, check: Callable[[], None]) -> list[Point]:
    points: list[Point] = []
    for scalar in range(r):
        check()
        points.append(curve.scalar(scalar, generator))
    if points[0] is not None or len(set(points)) != r or curve.scalar(r, generator) is not None:
        raise LaunchRefused("certified prime-order subgroup check failed")
    return sorted(points, key=point_key)


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
    """All-start, first-repeat census with certificate failure distinct from fruitlessness."""
    transition_work = verification_work = additions = doublings = successes = 0
    failed_certificates = 0
    certificates: list[dict[str, Any]] = []
    for start in range(r):
        check()
        state, A, B = curve.scalar(start, G), start, 0
        seen: dict[Point, tuple[int, int, int]] = {state: (A, B, 0)}
        for step in range(1, r + 2):
            check()
            state, A, B, operation = rho_step(curve, state, G, Q, A, B, r, assignment)
            transition_work += 1
            additions += int(operation == "add")
            doublings += int(operation == "double")
            if state not in seen:
                seen[state] = (A, B, step)
                continue
            oldA, oldB, first_seen = seen[state]
            denominator = (B - oldB) % r
            certificate: dict[str, Any] = {
                "start": start, "repeat_step": step, "first_seen_step": first_seen,
                "delta_b": denominator, "transition_work": step,
                "verification_additions": 0, "verification_doublings": 0,
            }
            if denominator == 0:
                certificate.update({"classification": "fruitless_denominator", "candidate": None, "verified": False})
            else:
                candidate = ((oldA - A) * pow(denominator, -1, r)) % r
                recovered, verify_adds, verify_doubles = binary_verifier(curve, candidate, G)
                verification_work += verify_adds + verify_doubles
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
    return {
        "starts": r, "successes": successes, "failed_certificates": failed_certificates,
        "transition_group_operations": transition_work, "verification_group_operations": verification_work,
        "group_additions": additions, "group_doublings": doublings,
        "charged_cost": None if successes == 0 else charged / successes,
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
    points: Sequence[Point], coordinate_values: Sequence[int], *, params: Sequence[int], seed: int
) -> tuple[dict[Point, int], int]:
    if len(points) != len(coordinate_values):
        raise ValueError("occupancy inputs differ in length")
    shuffled, counter = deterministic_shuffle(
        coordinate_values, purpose="shuffle", params=params, seed=seed, counter=0
    )
    return dict(zip(points, shuffled)), counter


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
    curve: Curve, points: Sequence[Point], G: Point, Q: Point, r: int, assignment: dict[Point, int]
) -> tuple[dict[Point, tuple[Point, int, int, str]], dict[Point, tuple[int, int]]]:
    scalar_by_point = {curve.scalar(s, G): s for s in range(r)}
    table: dict[Point, tuple[Point, int, int, str]] = {}
    labels: dict[Point, tuple[int, int]] = {}
    for point in points:
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
    table: dict[Point, tuple[Point, int, int, str]], start: Point, start_label: tuple[int, int], r: int
) -> tuple[int, int, int, int, int, str]:
    state = start
    A, B = start_label
    seen = {state: (A, B, 0)}
    additions = doublings = 0
    for step in range(1, len(table) + 2):
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
    table: dict[Point, tuple[Point, int, int, str]], labels: dict[Point, tuple[int, int]], bijection: dict[Point, Point], r: int
) -> bool:
    if set(bijection) != set(table) or set(bijection.values()) != set(table):
        raise ValueError("control requires a bijection on every state")
    renamed = {bijection[state]: (bijection[next_state], dA, dB, operation) for state, (next_state, dA, dB, operation) in table.items()}
    return all(
        table_first_collision(table, state, labels[state], r)
        == table_first_collision(renamed, bijection[state], labels[state], r)
        for state in table
    )


def cayley_weights(r: int, g: int, q: int) -> list[list[mp.mpf]]:
    with mp.workprec(128):
        matrix = [[mp.mpf(0) for _ in range(r)] for _ in range(r)]
        for state in range(r):
            matrix[state][state] += mp.mpf("0.5")
            for delta in (g, -g, q, -q):
                matrix[state][(state + delta) % r] += mp.mpf("0.125")
        return matrix


def cayley_fourier_eigenvalues(r: int, g: int, q: int) -> list[mp.mpf]:
    with mp.workprec(128):
        return [mp.mpf("0.5") + mp.mpf("0.25") * mp.cos(2 * mp.pi * index * g / r) + mp.mpf("0.25") * mp.cos(2 * mp.pi * index * q / r) for index in range(r)]


def cayley_tv_curve(r: int, g: int, q: int, check: Callable[[], None]) -> dict[str, Any]:
    steps = (0, 1, 2, 4, 8, 16, 32)
    with mp.workprec(128):
        matrix = cayley_weights(r, g, q)
        lambdas = cayley_fourier_eigenvalues(r, g, q)
        values: dict[str, Any] = {}
        for requested in steps:
            check()
            distribution = [mp.mpf(int(index == 0)) for index in range(r)]
            for _ in range(requested):
                check()
                distribution = [sum(matrix[origin][destination] * distribution[origin] for origin in range(r)) for destination in range(r)]
            inverse: list[mp.mpf] = []
            for state in range(r):
                check()
                inverse.append(sum((lambdas[index] ** requested) * mp.e ** (2j * mp.pi * index * state / r) for index in range(r)).real / r)
            discrepancy = mp.mpf("0.5") * sum(abs(left - right) for left, right in zip(distribution, inverse))
            uniform = mp.mpf(1) / r
            values[str(requested)] = {
                "point_basis_tv": str(mp.mpf("0.5") * sum(abs(value - uniform) for value in distribution)),
                "inverse_fourier_tv": str(mp.mpf("0.5") * sum(abs(value - uniform) for value in inverse)),
                "basis_vs_inverse_tv_discrepancy": str(discrepancy),
            }
        return values


def cayley_control(r: int, g: int, q: int, check: Callable[[], None]) -> dict[str, Any]:
    """Actual reversible Cayley calibration, separate from the rho transition graph."""
    with mp.workprec(128):
        matrix = cayley_weights(r, g, q)
        rows = [sum(row) for row in matrix]
        columns = [sum(matrix[row][column] for row in range(r)) for column in range(r)]
        expected = cayley_fourier_eigenvalues(r, g, q)
        # Direct DFT of the first transition row independently checks the formula.
        actual: list[mp.mpf] = []
        for frequency in range(r):
            check()
            actual.append(sum(matrix[0][state] * mp.e ** (2j * mp.pi * frequency * state / r) for state in range(r)).real)
        row_error = max(abs(value - 1) for value in rows + columns)
        eigen_error = max(abs(left - right) for left, right in zip(sorted(actual), sorted(expected)))
        tv = cayley_tv_curve(r, g, q, check)
        tv_error = max(mp.mpf(item["basis_vs_inverse_tv_discrepancy"]) for item in tv.values())
        gap = mp.mpf(1) - max(expected[1:])
        passed = row_error <= mp.mpf("1e-12") and eigen_error <= mp.mpf("1e-10") and tv_error <= mp.mpf("1e-10")
        return {
            "passed": bool(passed), "row_column_error": str(row_error), "eigenvalue_multiset_error": str(eigen_error),
            "max_basis_vs_inverse_tv_discrepancy": str(tv_error), "gap": str(gap), "workprec_bits": 128,
            "total_variation": tv,
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


def future_cell(
    fixture: dict[str, Any], seed: int, u: int, check: Callable[[], None],
    on_partial: Callable[[str, int, dict[str, Any]], None] | None = None,
) -> dict[str, Any]:
    curve, G, r = fixture_to_curve(fixture)
    target_params = (curve.p, curve.A, curve.B, r, 0, 0, 0)
    target, _ = rejection_draw(purpose="target", params=target_params, seed=seed, counter=0, n=r - 1)
    target += 1
    Q = curve.scalar(target, G)
    transported_curve = coordinate_curve(curve, u)
    transported_G = coordinate_transport(curve, G, u)
    transported_Q = coordinate_transport(curve, Q, u)
    points = subgroup_points(transported_curve, transported_G, r, check)
    coordinate = {point: 0 if point is None else point[0] % 3 for point in points}
    curve_id = f"p{curve.p}-B{curve.B}"
    coordinate_result = collision_census(
        transported_curve, transported_G, transported_Q, r, coordinate, check,
        lambda certificate: on_partial("coordinate", 0, certificate) if on_partial else None,
    )
    coordinate_values = [coordinate[point] for point in points]
    shuffles: list[dict[str, Any]] = []
    shuffle_assignments: list[dict[Point, int]] = []
    for arm in range(1, 8):
        check()
        params = (curve.p, curve.A, curve.B, r, 0, u, arm)
        assignment, consumed = occupancy_assignment(points, coordinate_values, params=params, seed=seed)
        shuffle_assignments.append(assignment)
        result = collision_census(
            transported_curve, transported_G, transported_Q, r, assignment, check,
            lambda certificate, arm=arm: on_partial("null", arm, certificate) if on_partial else None,
        )
        result["arm"] = arm
        result["rng_counter_end"] = consumed
        result["bucket_counts"] = [sum(value == bucket for value in assignment.values()) for bucket in range(3)]
        shuffles.append(result)
    table, labels = transition_table(transported_curve, points, transported_G, transported_Q, r, coordinate)
    permutation, _ = deterministic_shuffle(points, purpose="control", params=(curve.p, curve.A, curve.B, r, 0, u, 0), seed=seed)
    relabel = relabel_control(table, labels, dict(zip(points, permutation)), r)
    constant_o = constant_o_census(
        points, check, lambda certificate: on_partial("constant_o", 0, certificate) if on_partial else None
    )
    mutated, _, _ = binary_verifier(transported_curve, (target + 1) % r, transported_G)
    controls = {
        "cayley": cayley_control(r, 1, target, check), "relabel": relabel,
        "occupancy": all(row["bucket_counts"] == [sum(value == bucket for value in coordinate.values()) for bucket in range(3)] for row in shuffles),
        "known_false": {"constant_o": constant_o, "mutated_candidate_fails_certificate": mutated != transported_Q},
    }
    validity = reduce_validity(coordinate_result, shuffles, controls)
    metric = cell_difference(coordinate_result, shuffles)
    return {
        "curve_id": curve_id, "seed": seed, "u": u,
        "metric": metric, "coordinate": coordinate_result, "nulls": shuffles, "controls": controls, "validity": validity,
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
    started_wall: float = field(default_factory=time.monotonic)
    started_cpu: float = field(default_factory=time.process_time)
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

    def snapshot(self) -> dict[str, Any]:
        return {
            "wall_seconds": time.monotonic() - self.started_wall,
            "cpu_seconds": time.process_time() - self.started_cpu,
            "stages": self.stages,
        }


def process_group_rss_bytes() -> int:
    """Sum RSS of the current process group; failure is an infrastructure stop."""
    pgid = os.getpgid(0)
    try:
        output = subprocess.run(
            ["ps", "-axo", "pid=,pgid=,rss="], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise InfrastructureStop(f"cannot measure process-group RSS: {exc}") from exc
    total_kib = 0
    for line in output.splitlines():
        parts = line.split()
        if len(parts) == 3 and int(parts[1]) == pgid:
            total_kib += int(parts[2])
    return total_kib * 1024


@dataclass
class ProgressSink:
    staging: Path
    fixtures: list[dict[str, Any]] = field(default_factory=list)
    rejected: list[dict[str, Any]] = field(default_factory=list)
    cells: list[dict[str, Any]] = field(default_factory=list)
    partial_certificates: list[dict[str, Any]] = field(default_factory=list)
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

    def checkpoint(self, event: str) -> None:
        self.events.append({"event": event, "at": datetime.now(timezone.utc).isoformat()})
        data = canonical_json({"counts": {"fixtures": len(self.fixtures), "rejected": len(self.rejected), "cells": len(self.cells), "partial_certificates": len(self.partial_certificates)}, "events": self.events})
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


def git_blob_hash(commit: str, relative_path: str) -> str:
    try:
        payload = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{relative_path}"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LaunchRefused(f"archive commit does not contain {relative_path}") from exc
    return sha256_bytes(payload)


def require_archive_reachable(commit: str) -> None:
    try:
        subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", commit, "HEAD"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LaunchRefused("review archive commit is not reachable from the executing checkout") from exc


def verify_review_admission(admission: dict[str, Any], corrected_snapshot: str) -> None:
    required = {"archive_receipt_path", "archive_receipt_sha256", "archive_commit", "review_task_id", "review_report_path", "review_report_sha256", "corrected_source_snapshot", "required_verdict"}
    if set(admission) != required:
        raise LaunchRefused("review admission has missing or surplus fields")
    if admission["corrected_source_snapshot"] != corrected_snapshot or admission["required_verdict"] != "PASS":
        raise LaunchRefused("review admission does not name this corrected snapshot and PASS gate")
    require_archive_reachable(admission["archive_commit"])
    receipt_path = ROOT / admission["archive_receipt_path"]
    report_path = ROOT / admission["review_report_path"]
    if not receipt_path.is_file() or not report_path.is_file():
        raise LaunchRefused("archived review receipt or report is unavailable")
    if sha256_file(receipt_path) != admission["archive_receipt_sha256"] or sha256_file(report_path) != admission["review_report_sha256"]:
        raise LaunchRefused("review admission hash mismatch")
    if git_blob_hash(admission["archive_commit"], admission["archive_receipt_path"]) != admission["archive_receipt_sha256"] or git_blob_hash(admission["archive_commit"], admission["review_report_path"]) != admission["review_report_sha256"]:
        raise LaunchRefused("review archive commit bytes do not match the live admitted bytes")
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise LaunchRefused(f"archived review receipt/report is unparsable: {exc}") from exc
    review = report.get("validation_report", report.get("review_report", report)) if isinstance(report, dict) else {}
    hashes = receipt.get("path_sha256", {}) if isinstance(receipt, dict) else {}
    if admission["review_task_id"] not in receipt.get("source_task_ids", []) or hashes.get(admission["review_report_path"]) != admission["review_report_sha256"]:
        raise LaunchRefused("archive receipt does not bind the required review report/task")
    if review.get("task_id") != admission["review_task_id"] or review.get("source_snapshot_commit") != corrected_snapshot:
        raise LaunchRefused("review report does not attest the corrected source snapshot")
    if review.get("owned_joint_verdict") not in {"PASS", "PASSED"} or review.get("verdict") not in {"pass", "passed", "PASS"}:
        raise LaunchRefused("review report did not pass the admitted implementation joint")


def canonical_run_id(run_id: str) -> None:
    if not isinstance(run_id, str) or not run_id.startswith("RUN-") or "/" in run_id or "\\" in run_id or run_id in {".", ".."}:
        raise LaunchRefused("unsafe or unallocated run id")


def verify_launch_admission(lock_path: Path, trusted_public_key_b64: str) -> dict[str, Any]:
    """Verify real future authority, exact sources, resource guard, and archived review semantics."""
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LaunchRefused(f"genuine future launch lock unavailable or malformed: {exc}") from exc
    required = {"kind", "approved", "experiment_id", "approval_decision_id", "amendment_id", "spec_sha256", "amendment_sha256", "driver_sha256", "execution_plan_sha256", "corrected_source_snapshot", "runtime", "resource_limits", "review_admission", "run_id", "signature"}
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
    if lock["corrected_source_snapshot"] != current_commit or git_output("status", "--porcelain"):
        raise LaunchRefused("execution must use the clean reviewed corrected snapshot")
    verify_signature(trusted_public_key_b64, lock["signature"], lock_payload(lock))
    verify_review_admission(lock["review_admission"], current_commit)
    return lock


def artifact_bytes(
    *, lock: dict[str, Any], provenance: dict[str, Any], meter: ResourceMeter, sink: ProgressSink, status: str, error: str | None, decision: dict[str, Any]
) -> dict[str, bytes]:
    metrics = {
        "global_decision": decision, "cells_recorded": len(sink.cells), "rejected_fixture_candidates": len(sink.rejected),
        "availability": {"available": sum(bool(row.get("metric", {}).get("available")) for row in sink.cells), "unavailable": sum(not bool(row.get("metric", {}).get("available")) for row in sink.cells)},
        "cayley_gap": {f"{row.get('curve_id')}:{row.get('seed')}:{row.get('u')}": row.get("controls", {}).get("cayley", {}).get("gap") for row in sink.cells},
    }
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
            "inputs": {"curve_id": None, "seed": None, "parameters": {"frozen_heldout_seeds": list(HELDOUT_SEEDS), "u": list(US)}},
            "timing": {"started_at": datetime.now(timezone.utc).isoformat(), "finished_at": datetime.now(timezone.utc).isoformat(), "wall_seconds": meter.snapshot()["wall_seconds"], "timing_source": "runner"},
            "resources": {"peak_rss_bytes": final_rss, "cpu_seconds": meter.snapshot()["cpu_seconds"], "process_group_memory_limit_bytes": MEMORY_LIMIT_BYTES, "stage_costs": meter.snapshot()["stages"]},
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
        cost_rows.append({"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "arm": "coordinate", **{key: row.get("coordinate", {}).get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")}, "d": row.get("metric", {}).get("d")})
        for arm in row.get("nulls", []):
            cost_rows.append({"curve_id": row.get("curve_id"), "seed": row.get("seed"), "u": row.get("u"), "arm": arm.get("arm"), **{key: arm.get(key) for key in ("starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost")}, "d": row.get("metric", {}).get("d")})
    output = tempfile.SpooledTemporaryFile(mode="w+", newline="", max_size=1_000_000)
    fieldnames = ["curve_id", "seed", "u", "arm", "starts", "successes", "transition_group_operations", "verification_group_operations", "group_additions", "group_doublings", "charged_cost", "d"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cost_rows)
    output.seek(0)
    costs = output.read().encode("utf-8")
    output.close()
    raw_lines = b"".join(canonical_json(row) + b"\n" for row in sink.cells)
    report = "\n".join([
        f"# {EXPERIMENT_ID} future-run record", "", f"Status: `{status}`.",
        f"Global finite decision: `{decision.get('branch', 'inconclusive')}`.",
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
        for name, digest in hashes.items():
            if sha256_file(staging / name) != digest:
                raise InfrastructureStop(f"staged artifact hash mismatch: {name}")
        if set(path.name for path in staging.iterdir()) != set(EXPERIMENT_ARTIFACTS):
            raise InfrastructureStop("staged canonical artifact set is incomplete")
        fsync_directory(staging)
        fsync_directory(runs)
        if final.exists():
            raise LaunchRefused("final run directory appeared during publication")
        os.rename(staging, final)  # same filesystem because staging is a sibling of final
        fsync_directory(runs)
        return hashes
    except Exception as exc:
        incomplete = runs / "incomplete"
        incomplete.mkdir(exist_ok=True)
        receipt = staging / "publication-failure.json"
        try:
            receipt.write_bytes(canonical_json({"classification": "infrastructure_error", "run_id": run_id, "error": f"{type(exc).__name__}: {exc}"}) + b"\n")
            with receipt.open("rb") as handle:
                os.fsync(handle.fileno())
            retained = incomplete / f"{run_id}-{uuid.uuid4().hex[:12]}"
            os.rename(staging, retained)
            fsync_directory(incomplete)
        except OSError:
            pass
        raise InfrastructureStop(f"atomic publication failed; staged failure receipt retained if possible: {exc}") from exc


def run_future_pipeline(lock: dict[str, Any], run_root: Path, command: str) -> dict[str, str]:
    """The real future path.  This is never invoked by this correction task."""
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
        for rows in selected.values():
            for fixture in rows:
                for seed in HELDOUT_SEEDS:
                    for u in US:
                        guard.check()
                        curve_id = f"p{fixture['p']}-B{fixture['B']}"
                        def record_partial(kind: str, arm: int, certificate: dict[str, Any]) -> None:
                            sink.record_partial({"curve_id": curve_id, "seed": seed, "u": u, "kind": kind, "arm": arm, "certificate": certificate})

                        cell = future_cell(fixture, seed, u, guard.check, record_partial)
                        sink.record_cell(cell)
        meter.exit("census")
        meter.enter("report")
        decision = global_decision(sink.cells)
        status = "completed_valid" if decision["panel_valid"] else "completed_invalid"
        error = None if decision["panel_valid"] else ";".join(decision["reasons"])
        meter.exit("report")
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
        status, error = "completed_invalid", f"implementation_error: {type(exc).__name__}: {exc}"
        decision = {"branch": "inconclusive", "reasons": ["implementation_error"], "per_u": {}}
    finally:
        meter.close_active()
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
