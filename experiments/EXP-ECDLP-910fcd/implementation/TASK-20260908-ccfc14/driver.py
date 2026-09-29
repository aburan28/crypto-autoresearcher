#!/usr/bin/env python3
"""Fail-closed prospective runner for the frozen Tate calibration.

This module implements the approved protocol shape but does not start a
scientific run by default.  The only launch path requires a future, detached,
Coordinator-signed lock whose source closure, review custody, runtime, output
directory, nonce, and machine-protection record all bind to the bytes that
would execute.  No key, lock, RUN id, or scientific fixture is created here.
"""
from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import importlib.util
import json
import math
import os
import platform
import resource
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Callable, Iterable, Mapping, Sequence


TASK_ID = "TASK-20260908-ccfc14"
EXPERIMENT_ID = "EXP-ECDLP-910fcd"
FROZEN_APPROVAL_ID = "DEC-20260906-f73475"
IMPLEMENTATION_APPROVAL_ID = "DEC-20260908-cfcacc"
SPEC_SHA256 = "75148fa8dc182d14f0894b3e525418c72fc939338b6a60d2c07cd2fc9df32555"
PREDECESSOR_TASK_ID = "TASK-20260906-681152"
PREDECESSOR_REL = "experiments/EXP-ECDLP-910fcd/implementation/TASK-20260906-681152/driver.py"
PREDECESSOR_SHA256 = "1cb875e5d9cc50351f64357af7f20485c54243d2215fe3bf92cae250a0d097e0"
REVIEWED_SNAPSHOT_TASK_ID = "TASK-20260908-16ec11"
POLYNOMIAL_CAP = 4096
T_ATTEMPT_CAP = 128
TARGET_SEEDS = (606223, 606227)
PREPARATION_SEED = 606211
QUERY_COUNTS = (1, 64)
RESOURCE_LIMITS = {"maximum_memory_gb": 8, "maximum_workers": 1}
RUN_FILES = (
    "manifest.yaml", "command.txt", "environment.json", "raw-result.json",
    "fixtures.json", "raw.jsonl", "controls.json", "costs.csv",
    "certificates.json", "stdout.log", "stderr.log", "report.md",
)


class LaunchRefused(RuntimeError):
    """Future authority or custody was incomplete; no scientific work started."""


class RunInterrupted(RuntimeError):
    """A cancellation, watchdog, or resource guard interrupted future work."""


class PublicSchemaError(ValueError):
    """A would-be evaluator payload is not the exact public schema."""


@dataclass(frozen=True)
class RunFailure:
    classification: str
    stage: str
    exception_type: str
    detail: str


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


_prior_path = Path(__file__).resolve().parents[1] / PREDECESSOR_TASK_ID / "driver.py"
if not _prior_path.is_file() or sha256_file(_prior_path) != PREDECESSOR_SHA256:
    raise RuntimeError("hash-bound transitive arithmetic predecessor is unavailable or has drifted")
_prior_spec = importlib.util.spec_from_file_location("_tate_predecessor_ccfc14", _prior_path)
if _prior_spec is None or _prior_spec.loader is None:
    raise RuntimeError("unable to load hash-bound arithmetic predecessor")
prior = importlib.util.module_from_spec(_prior_spec)
sys.modules[_prior_spec.name] = prior
_prior_spec.loader.exec_module(prior)

PolynomialField = prior.PolynomialField
ShortWeierstrassCurve = prior.ShortWeierstrassCurve
SearchExhausted = prior.SearchExhausted
NoSolution = prior.NoSolution
PairingPole = prior.PairingPole


# Polynomial witnesses -----------------------------------------------------

def _trim(poly: list[int]) -> list[int]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def _sub(a: Sequence[int], b: Sequence[int], p: int) -> list[int]:
    return _trim([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % p
                  for i in range(max(len(a), len(b)))])


def _mul(a: Sequence[int], b: Sequence[int], p: int) -> list[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return _trim(out)


def _divmod(a: Sequence[int], b: Sequence[int], p: int) -> tuple[list[int], list[int]]:
    numerator, denominator = _trim(list(a)), _trim(list(b))
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    quotient = [0] * max(1, len(numerator) - len(denominator) + 1)
    inverse = pow(denominator[-1], -1, p)
    while numerator != [0] and len(numerator) >= len(denominator):
        coefficient = numerator[-1] * inverse % p
        offset = len(numerator) - len(denominator)
        quotient[offset] = coefficient
        for i, value in enumerate(denominator):
            numerator[offset + i] = (numerator[offset + i] - coefficient * value) % p
        _trim(numerator)
    return _trim(quotient), numerator


def _mod(a: Sequence[int], f: Sequence[int], p: int) -> list[int]:
    return _divmod(a, f, p)[1]


def _gcd(a: Sequence[int], b: Sequence[int], p: int) -> list[int]:
    x, y = _trim(list(a)), _trim(list(b))
    while y != [0]:
        x, y = y, _mod(x, y, p)
    inv = pow(x[-1], -1, p)
    return [(coefficient * inv) % p for coefficient in x]


def _x_power(exponent: int, f: Sequence[int], p: int) -> list[int]:
    out, base = [1], [0, 1]
    while exponent:
        if exponent & 1:
            out = _mod(_mul(out, base, p), f, p)
        base = _mod(_mul(base, base, p), f, p)
        exponent >>= 1
    return out


@dataclass(frozen=True)
class RabinCertificate:
    p: int
    degree: int
    lower_coefficients: tuple[int, ...]
    frobenius_x: tuple[int, ...]
    reduced_x: tuple[int, ...]
    gcd_witnesses: tuple[tuple[int, tuple[int, ...], tuple[int, ...]], ...]
    irreducible: bool


def rabin_irreducibility_certificate(p: int, coefficients: Sequence[int]) -> RabinCertificate:
    """Return complete Rabin witnesses, including the degree-one Fp case.

    The old implementation compared a reduced residue with unreduced ``X``.
    For a linear modulus, ``X`` is a constant residue.  Comparing both sides
    in Fp[X]/f fixes that error without weakening the k>1 gcd checks.
    """
    lower = tuple(int(value) % p for value in coefficients)
    degree = len(lower)
    if not prior.is_prime(p) or degree < 1 or lower[0] == 0:
        raise ValueError("invalid monic polynomial for Rabin criterion")
    modulus = list(lower) + [1]
    x = [0, 1]
    reduced_x = _mod(x, modulus, p)
    frobenius = _x_power(p ** degree, modulus, p)
    ok = frobenius == reduced_x
    witnesses: list[tuple[int, tuple[int, ...], tuple[int, ...]]] = []
    for ell, _ in prior.factor_integer(degree):
        residue = _x_power(p ** (degree // ell), modulus, p)
        divisor = _gcd(_sub(residue, reduced_x, p), modulus, p)
        witnesses.append((ell, tuple(residue), tuple(divisor)))
        ok = ok and divisor == [1]
    return RabinCertificate(
        p=p, degree=degree, lower_coefficients=lower,
        frobenius_x=tuple(frobenius), reduced_x=tuple(reduced_x),
        gcd_witnesses=tuple(witnesses), irreducible=bool(ok),
    )


def select_certified_modulus(p: int, k: int) -> tuple[int, tuple[int, ...], list[int], RabinCertificate]:
    tested: list[int] = []
    for index, coefficients in prior.bounded_monic_polynomials(p=p, k=k, cap=POLYNOMIAL_CAP):
        tested.append(index)
        certificate = rabin_irreducibility_certificate(p, coefficients)
        if certificate.irreducible:
            return index, coefficients, tested, certificate
    raise SearchExhausted("Rabin polynomial search exhausted its fixed 4096 candidate cap")


# Public evaluator schema --------------------------------------------------

def _require_exact_keys(value: Mapping[str, Any], expected: set[str], where: str) -> None:
    actual = set(value)
    if actual != expected:
        raise PublicSchemaError(f"{where} must contain exactly {sorted(expected)}; got {sorted(actual)}")


def _require_int(value: Any, where: str, *, minimum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise PublicSchemaError(f"{where} must be an integer")
    if minimum is not None and value < minimum:
        raise PublicSchemaError(f"{where} must be >= {minimum}")
    return value


def _require_vector(value: Any, width: int, p: int, where: str) -> list[int]:
    if not isinstance(value, list) or len(value) != width:
        raise PublicSchemaError(f"{where} must be a {width}-coefficient public vector")
    return [_require_int(entry, f"{where}[{index}]", minimum=0) % p for index, entry in enumerate(value)]


def _require_point(value: Any, width: int, p: int, where: str) -> list[list[int]] | None:
    if value is None:
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise PublicSchemaError(f"{where} must be null or a two-coordinate point")
    return [_require_vector(value[0], width, p, f"{where}.x"),
            _require_vector(value[1], width, p, f"{where}.y")]


def _json_load_no_duplicates(payload: bytes) -> dict[str, Any]:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise PublicSchemaError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result
    try:
        value = json.loads(payload, object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PublicSchemaError(f"malformed public evaluator JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise PublicSchemaError("public evaluator payload must be a JSON object")
    return value


def validate_public_payload(payload: bytes) -> dict[str, Any]:
    """Validate every boundary object with an allowlist, in parent and child."""
    data = _json_load_no_duplicates(payload)
    _require_exact_keys(data, {"fixture", "batch_id", "q", "block", "repetition", "order", "queries", "context"}, "payload")
    fixture = data["fixture"]
    context = data["context"]
    if not isinstance(fixture, dict) or not isinstance(context, dict):
        raise PublicSchemaError("fixture and context must be objects")
    _require_exact_keys(fixture, {"p", "A", "B", "N", "r", "k", "bit_block", "bin"}, "fixture")
    p = _require_int(fixture["p"], "fixture.p", minimum=5)
    k = _require_int(fixture["k"], "fixture.k", minimum=1)
    r = _require_int(fixture["r"], "fixture.r", minimum=2)
    for name in ("A", "B", "N", "bit_block"):
        _require_int(fixture[name], f"fixture.{name}", minimum=0)
    if fixture["bin"] not in {"1", "2", "3_6", "7_12"}:
        raise PublicSchemaError("fixture.bin is outside the frozen bins")
    _require_exact_keys(context, {"p", "k", "r", "modulus", "A", "B", "G", "T", "shift", "chi_g"}, "context")
    if (_require_int(context["p"], "context.p", minimum=5),
            _require_int(context["k"], "context.k", minimum=1),
            _require_int(context["r"], "context.r", minimum=2)) != (p, k, r):
        raise PublicSchemaError("fixture and context disagree on p, k, or r")
    _require_vector(context["modulus"], k, p, "context.modulus")
    _require_vector(context["A"], k, p, "context.A")
    _require_vector(context["B"], k, p, "context.B")
    _require_point(context["G"], k, p, "context.G")
    _require_point(context["T"], k, p, "context.T")
    _require_point(context["shift"], k, p, "context.shift")
    _require_vector(context["chi_g"], k, p, "context.chi_g")
    _require_int(data["batch_id"], "batch_id", minimum=0)
    q = _require_int(data["q"], "q", minimum=1)
    if q not in QUERY_COUNTS:
        raise PublicSchemaError("q must be one of the frozen q=1 or q=64 workloads")
    _require_int(data["block"], "block", minimum=0)
    _require_int(data["repetition"], "repetition", minimum=0)
    if data["order"] not in {"curve_first", "character_first"}:
        raise PublicSchemaError("order must be curve_first or character_first")
    queries = data["queries"]
    if not isinstance(queries, list) or len(queries) != q:
        raise PublicSchemaError("queries must contain exactly q public points")
    for index, query in enumerate(queries):
        _require_exact_keys(query, {"query_id", "Q"}, f"queries[{index}]") if isinstance(query, dict) else (_ for _ in ()).throw(PublicSchemaError("query must be an object"))
        _require_int(query["query_id"], f"queries[{index}].query_id", minimum=0)
        _require_point(query["Q"], k, p, f"queries[{index}].Q")
    return data


@dataclass(frozen=True)
class PublicEvaluatorInput:
    """A closed public-only batch; withheld labels have no representable field."""
    fixture: dict[str, Any]
    batch_id: int
    q: int
    block: int
    repetition: int
    order: str
    queries: list[dict[str, Any]]
    context: dict[str, Any]

    def mapping(self) -> dict[str, Any]:
        return {"fixture": self.fixture, "batch_id": self.batch_id, "q": self.q,
                "block": self.block, "repetition": self.repetition, "order": self.order,
                "queries": self.queries, "context": self.context}

    def serialize(self) -> bytes:
        encoded = canonical_json(self.mapping())
        validate_public_payload(encoded)
        return encoded

    @classmethod
    def from_payload(cls, payload: bytes) -> "PublicEvaluatorInput":
        value = validate_public_payload(payload)
        return cls(**value)


def audit_public_input(item: PublicEvaluatorInput) -> None:
    validate_public_payload(item.serialize())


def audit_public_payload(payload: bytes) -> None:
    validate_public_payload(payload)


def evaluator_subprocess_request(item: PublicEvaluatorInput) -> tuple[list[str], bytes]:
    return [sys.executable, str(Path(__file__).resolve()), "--evaluator-stdin"], item.serialize()


def _point(field: Any, encoded: list[list[int]] | None) -> Any:
    if encoded is None:
        return None
    return field.element(encoded[0]), field.element(encoded[1])


def _public_context(field: Any, curve: Any, G: Any, T: Any, shift: Any, chi_g: Any,
                    r: int, p: int, k: int) -> dict[str, Any]:
    def encode(point: Any) -> list[list[int]] | None:
        return None if point is None else [list(point[0]), list(point[1])]
    return {"p": p, "k": k, "r": r, "modulus": list(field.modulus),
            "A": list(curve.A), "B": list(curve.B), "G": encode(G), "T": encode(T),
            "shift": encode(shift), "chi_g": list(chi_g)}


# Pairing and explicit BSGS ------------------------------------------------

def extension_sqrt(field: Any, value: tuple[int, ...], search_cap: int = POLYNOMIAL_CAP) -> tuple[int, ...] | None:
    if value == field.zero:
        return field.zero
    size = field.p ** field.k
    if field.pow(value, (size - 1) // 2) != field.one:
        return None
    odd, s = size - 1, 0
    while not odd & 1:
        odd //= 2
        s += 1
    nonresidue = None
    for index in range(min(search_cap, size)):
        candidate = field.element(prior.polynomial_coefficients(index, p=field.p, k=field.k))
        if candidate != field.zero and field.pow(candidate, (size - 1) // 2) != field.one:
            nonresidue = candidate
            break
    if nonresidue is None:
        raise SearchExhausted("bounded extension nonresidue search exhausted")
    m, c, t, root = s, field.pow(nonresidue, odd), field.pow(value, odd), field.pow(value, (odd + 1) // 2)
    while t != field.one:
        i, square = 1, field.mul(t, t)
        while i < m and square != field.one:
            square = field.mul(square, square)
            i += 1
        if i == m:
            raise ArithmeticError("inconsistent extension quadratic-residue calculation")
        correction = field.pow(c, 1 << (m - i - 1))
        root = field.mul(root, correction)
        c = field.mul(correction, correction)
        t = field.mul(t, c)
        m = i
    return root if root <= field.neg(root) else field.neg(root)


def extension_point_attempts(field: Any, curve: Any, *, p: int, A: int, B: int, k: int,
                             seed: int, cap: int = T_ATTEMPT_CAP) -> tuple[list[Any], list[dict[str, Any]]]:
    points: list[Any] = []
    attempts: list[dict[str, Any]] = []
    parameters = (p, A, B, 0, k, 0, 0)
    counter = 0
    for ordinal in range(cap):
        coefficients = []
        for coordinate in range(k):
            draw, counter = prior.rejection_draw(
                purpose="field_x", parameters=parameters, seed=seed, counter=counter, n=p)
            coefficients.append(draw)
        x = field.element(coefficients)
        rhs = field.add(field.add(field.mul(field.mul(x, x), x), field.mul(curve.A, x)), curve.B)
        y = extension_sqrt(field, rhs)
        entry: dict[str, Any] = {"ordinal": ordinal, "x": list(x), "rng_counter_after": counter}
        if y is None:
            entry["status"] = "rejected_nonsquare"
        else:
            entry.update({"status": "point", "y": list(y)})
            points.append((x, y))
        attempts.append(entry)
    return points, attempts


def evaluate_shifted_tate(curve: Any, r: int, P: Any, T: Any, shift: Any, p: int, k: int) -> tuple[Any, int]:
    raw = prior.shifted_divisor_miller(curve=curve, r=r, P=P, T=T, shift=shift)
    return prior.reduced_tate(miller_value=raw, p=p, k=k, r=r, power=curve.field.pow)


def bounded_t_search(curve: Any, r: int, P: Any, field: Any, *, p: int, A: int, B: int,
                     k: int, seed: int) -> tuple[Any, Any, Any, list[dict[str, Any]], list[dict[str, Any]]]:
    points, point_attempts = extension_point_attempts(field, curve, p=p, A=A, B=B, k=k, seed=seed)
    attempts: list[dict[str, Any]] = []
    ordinal = 0
    for T in points:
        for shift in points:
            if ordinal >= T_ATTEMPT_CAP:
                return _raise_t_exhausted(attempts, point_attempts)
            current = {"ordinal": ordinal, "T": [list(T[0]), list(T[1])], "shift": [list(shift[0]), list(shift[1])]}
            ordinal += 1
            if curve.add(T, shift) is None:
                current["status"] = "rejected_shifted_divisor_infinity"
                attempts.append(current)
                continue
            try:
                chi, exponent = evaluate_shifted_tate(curve, r, P, T, shift, p, k)
                current["final_exponent"] = exponent
                if field.pow(chi, r) == field.one and chi != field.one:
                    current["status"] = "accepted"
                    current["chi_g"] = list(chi)
                    attempts.append(current)
                    return T, shift, chi, attempts, point_attempts
                current["status"] = "rejected_nonprimitive"
            except (PairingPole, ZeroDivisionError) as exc:
                current.update({"status": "rejected_pole", "exception": type(exc).__name__})
            attempts.append(current)
    return _raise_t_exhausted(attempts, point_attempts)


def _raise_t_exhausted(attempts: list[dict[str, Any]], point_attempts: list[dict[str, Any]]) -> Any:
    error = SearchExhausted("T/shift search exhausted its fixed 128 candidate cap")
    error.t_attempts = attempts  # type: ignore[attr-defined]
    error.point_attempts = point_attempts  # type: ignore[attr-defined]
    raise error


@dataclass(frozen=True)
class MultiplicativeTable:
    base: Any
    order: int
    m: int
    baby: dict[Any, int]
    giant_multiplier: Any


@dataclass(frozen=True)
class AdditiveTable:
    base: Any
    order: int
    m: int
    baby: dict[Any, int]
    giant_step: Any


def prepare_multiplicative_bsgs(base: Any, order: int, field: Any) -> MultiplicativeTable:
    if base == field.one:
        raise NoSolution("trivial character is explicitly ambiguous")
    m = math.isqrt(order - 1) + 1
    baby: dict[Any, int] = {}
    value = field.one
    for exponent in range(m):
        baby.setdefault(value, exponent)
        value = field.mul(value, base)
    return MultiplicativeTable(base, order, m, baby, field.inv(field.pow(base, m)))


def solve_multiplicative_bsgs(table: MultiplicativeTable, target: Any, field: Any) -> int:
    current = target
    for giant in range(table.m + 1):
        if current in table.baby:
            candidate = giant * table.m + table.baby[current]
            if candidate < table.order and field.pow(table.base, candidate) == target:
                return candidate
        current = field.mul(current, table.giant_multiplier)
    raise NoSolution("bounded multiplicative BSGS found no verified solution")


def prepare_additive_bsgs(curve: Any, base: Any, order: int) -> AdditiveTable:
    m = math.isqrt(order - 1) + 1
    baby: dict[Any, int] = {}
    value = None
    for exponent in range(m):
        baby.setdefault(value, exponent)
        value = curve.add(value, base)
    return AdditiveTable(base, order, m, baby, curve.neg(curve.scalar_mul(m, base)))


def solve_additive_bsgs(table: AdditiveTable, target: Any, curve: Any) -> int:
    current = target
    for giant in range(table.m + 1):
        if current in table.baby:
            candidate = giant * table.m + table.baby[current]
            if candidate < table.order and curve.scalar_mul(candidate, table.base) == target:
                return candidate
        current = curve.add(current, table.giant_step)
    raise NoSolution("bounded additive BSGS found no verified solution")


def bounded_multiplicative_bsgs(base: Any, target: Any, order: int, field: Any) -> int:
    return solve_multiplicative_bsgs(prepare_multiplicative_bsgs(base, order, field), target, field)


def bounded_additive_bsgs(curve: Any, G: Any, Q: Any, r: int) -> int:
    return solve_additive_bsgs(prepare_additive_bsgs(curve, G, r), Q, curve)


def _serialized_size(value: Any) -> int:
    return len(canonical_json(value))


def _rss_bytes() -> int | None:
    try:
        amount = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    except (AttributeError, OSError):
        return None
    return amount if sys.platform == "darwin" else amount * 1024


def _evaluate_public_payload(payload: bytes) -> dict[str, Any]:
    """Child entrypoint.  It repeats the closed-schema validation before work."""
    data = validate_public_payload(payload)
    context = data["context"]
    whole_cpu_start, whole_wall_start = time.process_time(), time.monotonic()
    construction_cpu_start = time.process_time()
    field = PolynomialField(context["p"], tuple(context["modulus"]))
    curve = ShortWeierstrassCurve(field, field.element(context["A"]), field.element(context["B"]))
    G = _point(field, context["G"])
    T = _point(field, context["T"])
    shift = _point(field, context["shift"])
    queries = [_point(field, row["Q"]) for row in data["queries"]]
    construction_cpu = time.process_time() - construction_cpu_start

    field_table_start = time.process_time()
    field_table = prepare_multiplicative_bsgs(field.element(context["chi_g"]), context["r"], field)
    field_table_cpu = time.process_time() - field_table_start
    curve_table_start = time.process_time()
    curve_table = prepare_additive_bsgs(curve, G, context["r"])
    curve_table_cpu = time.process_time() - curve_table_start

    timings = {"field_reconstruction": construction_cpu, "field_table": field_table_cpu,
               "curve_table": curve_table_cpu, "curve_giant_steps": 0.0,
               "chi_q": 0.0, "field_giant_steps": 0.0, "curve_verify": 0.0}
    results: list[dict[str, Any]] = []
    for query, encoded in zip(queries, data["queries"]):
        answer: dict[str, int] = {}
        for arm in (("curve", "character") if data["order"] == "curve_first" else ("character", "curve")):
            if arm == "curve":
                began = time.process_time()
                answer["curve_answer"] = solve_additive_bsgs(curve_table, query, curve)
                timings["curve_giant_steps"] += time.process_time() - began
            else:
                began = time.process_time()
                chi_q, _ = evaluate_shifted_tate(curve, context["r"], query, T, shift, context["p"], context["k"])
                timings["chi_q"] += time.process_time() - began
                began = time.process_time()
                answer["character_answer"] = solve_multiplicative_bsgs(field_table, chi_q, field)
                timings["field_giant_steps"] += time.process_time() - began
        began = time.process_time()
        verified = curve.scalar_mul(answer["character_answer"], G) == query
        timings["curve_verify"] += time.process_time() - began
        results.append({"query_id": encoded["query_id"], **answer, "curve_verification": verified})
    total_cpu = time.process_time() - whole_cpu_start
    response = {
        "batch_id": data["batch_id"], "order": data["order"], "results": results,
        "costs": {"cpu_seconds": timings, "wall_seconds": time.monotonic() - whole_wall_start,
                  "peak_rss_bytes": _rss_bytes(), "field_table_bytes": _serialized_size({str(key): value for key, value in field_table.baby.items()}),
                  "curve_table_bytes": _serialized_size({str(key): value for key, value in curve_table.baby.items()}),
                  "output_bytes": 0, "total_cpu_seconds": total_cpu,
                  "operation_counts": {"field": "unavailable_uninstrumented", "group": "unavailable_uninstrumented"}},
    }
    response["costs"]["output_bytes"] = _serialized_size(response)
    return response


# Resource isolation and evaluator launch --------------------------------

def _set_as_limit() -> None:
    limit = RESOURCE_LIMITS["maximum_memory_gb"] * 1024 ** 3
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))


def _limit_child() -> None:
    _set_as_limit()


def _kill_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=1)


def process_group_rss_bytes(pgid: int) -> int | None:
    """Portable best-effort group RSS accounting; None is recorded if unavailable."""
    try:
        listing = subprocess.run(["ps", "-o", "pid=,pgid=,rss="], capture_output=True, text=True,
                                 check=True, timeout=2)
    except (OSError, subprocess.SubprocessError):
        return None
    total = 0
    for line in listing.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[1].isdigit() and int(fields[1]) == pgid and fields[2].isdigit():
            total += int(fields[2]) * 1024
    return total


def invoke_public_evaluator(item: PublicEvaluatorInput, *, timeout_seconds: int,
                            checkpoint: Callable[[], None] | None = None) -> dict[str, Any]:
    """Invoke one serial child and kill its process group on timeout or RSS excess."""
    audit_public_input(item)
    command, payload = evaluator_subprocess_request(item)
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True, preexec_fn=_limit_child)
    memory_cap = RESOURCE_LIMITS["maximum_memory_gb"] * 1024 ** 3
    deadline = time.monotonic() + timeout_seconds
    peak_group_rss: int | None = None
    first_communicate = True
    try:
        while True:
            if checkpoint is not None:
                checkpoint()
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise subprocess.TimeoutExpired(command, timeout_seconds)
            try:
                stdout, stderr = process.communicate(input=payload if first_communicate else None,
                                                     timeout=min(0.25, remaining))
                break
            except subprocess.TimeoutExpired:
                first_communicate = False
                rss = process_group_rss_bytes(process.pid)
                if rss is not None:
                    peak_group_rss = max(peak_group_rss or 0, rss)
                    if rss > memory_cap:
                        _kill_process_group(process)
                        raise RunInterrupted("evaluator process-group RSS exceeded the signed 8GiB protection")
                continue
    except (subprocess.TimeoutExpired, RunInterrupted) as exc:
        _kill_process_group(process)
        if isinstance(exc, RunInterrupted):
            raise
        raise RunInterrupted("evaluator timeout; started evaluator process group was terminated") from exc
    if process.returncode:
        raise RuntimeError(f"public evaluator failed: {stderr.decode(errors='replace')}")
    result = json.loads(stdout)
    if not isinstance(result, dict) or set(result) != {"batch_id", "order", "results", "costs"}:
        raise PublicSchemaError("evaluator response has an unexpected schema")
    result["costs"]["process_group_peak_rss_bytes"] = peak_group_rss
    return result


@dataclass
class MachineProtection:
    watchdog_seconds: int
    started_monotonic: float = field(default_factory=time.monotonic)
    cancelled_signal: int | None = None

    def checkpoint(self) -> None:
        if self.cancelled_signal is not None:
            raise RunInterrupted(f"received signal {self.cancelled_signal}; completed progressive custody retained")
        if time.monotonic() - self.started_monotonic > self.watchdog_seconds:
            raise RunInterrupted("justified machine watchdog expired; progress retained without scientific inference")


def install_cancellation_handlers(guard: MachineProtection) -> dict[int, Any]:
    previous: dict[int, Any] = {}
    def handler(signum: int, _frame: Any) -> None:
        guard.cancelled_signal = signum
    for value in (signal.SIGINT, signal.SIGTERM):
        previous[value] = signal.signal(value, handler)
    return previous


def restore_cancellation_handlers(previous: Mapping[int, Any]) -> None:
    for signum, handler in previous.items():
        signal.signal(signum, handler)


# Frozen preparation, controls, costs -------------------------------------

def first_subgroup_generator_with_attempts(*, p: int, B: int, N: int, r: int) -> tuple[tuple[int, int], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    coefficient = N // r
    for x in range(min(p - 1, 4095) + 1):
        root = prior.sqrt_fp(x * x * x + x + B, p)
        if root is None:
            attempts.append({"x": x, "status": "rejected_nonsquare"})
            continue
        for y in sorted({root, (-root) % p}):
            point = (x, y)
            projected = _integer_curve_scalar(coefficient, point, p, B)
            if projected is None:
                attempts.append({"x": x, "y": y, "status": "rejected_projection_infinity"})
                continue
            if _integer_curve_scalar(r, projected, p, B) is None:
                attempts.append({"x": x, "y": y, "projected": list(projected), "status": "accepted"})
                return projected, attempts
            attempts.append({"x": x, "y": y, "projected": list(projected), "status": "rejected_wrong_order"})
    error = SearchExhausted("subgroup generator search exhausted fixed x/root scan")
    error.generator_attempts = attempts  # type: ignore[attr-defined]
    raise error


def _integer_curve_add(left: tuple[int, int] | None, right: tuple[int, int] | None, p: int, B: int) -> tuple[int, int] | None:
    if left is None:
        return right
    if right is None:
        return left
    x1, y1 = left
    x2, y2 = right
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if left == right:
        if y1 == 0:
            return None
        slope = (3 * x1 * x1 + 1) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def _integer_curve_scalar(scalar: int, point: tuple[int, int] | None, p: int, B: int) -> tuple[int, int] | None:
    result: tuple[int, int] | None = None
    addend = point
    while scalar:
        if scalar & 1:
            result = _integer_curve_add(result, addend, p, B)
        addend = _integer_curve_add(addend, addend, p, B)
        scalar >>= 1
    return result


def build_future_fixtures(progress: Callable[[dict[str, Any]], None] | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Frozen eight-fixture selector retaining every inspected candidate."""
    selected: list[dict[str, Any]] = []
    history: list[dict[str, Any]] = []
    for bits in (8, 10):
        assigned_bins: set[str] = set()
        for p in prior.first_primes_from(1 << bits, count=32):
            for B in range(16):
                candidate = {"p": p, "A": 1, "B": B, "bit_block": bits}
                if (4 + 27 * B * B) % p == 0:
                    history.append({**candidate, "status": "rejected_singular"})
                    continue
                N = prior.count_short_weierstrass_points(p, B)
                if N == p + 1:
                    history.append({**candidate, "N": N, "status": "rejected_supersingular"})
                    continue
                candidates = 0
                for r, valuation in sorted(prior.factor_integer(N), reverse=True):
                    row = {**candidate, "N": N, "r": r, "valuation": valuation}
                    if not (17 <= r <= 251 and r != p and valuation == 1):
                        history.append({**row, "status": "rejected_divisor"})
                        continue
                    k = prior.multiplicative_order_mod(p, r)
                    row["k"] = k
                    if k > 12:
                        history.append({**row, "representation_lower_bound_bits": k * math.ceil(math.log2(p)), "status": "excluded_high_k"})
                        continue
                    bin_name = prior.fixture_bin(k)
                    row["bin"] = bin_name
                    candidates += 1
                    if bin_name in assigned_bins:
                        history.append({**row, "status": "rejected_bin_already_selected"})
                    else:
                        selected.append(row)
                        assigned_bins.add(bin_name)
                        history.append({**row, "status": "selected"})
                    if progress is not None:
                        progress({"event": "fixture_candidate", "candidate": history[-1]})
                if candidates == 0:
                    history.append({**candidate, "N": N, "status": "rejected_no_eligible_divisor"})
        missing = {"1", "2", "3_6", "7_12"} - assigned_bins
        if missing:
            error = SearchExhausted(f"missing frozen fixture bins in {bits}-bit block: {sorted(missing)}")
            error.fixture_history = history  # type: ignore[attr-defined]
            raise error
    if len(selected) != 8:
        raise RuntimeError("frozen selector did not produce exactly eight selected fixtures")
    return selected, history


def fixed_q64_labels(fixture: Mapping[str, Any], seed: int) -> tuple[list[int], int]:
    """Draw a q=64 verifier-only label list once; q=1 is its literal prefix."""
    parameters = tuple(int(fixture[name]) for name in ("p", "A", "B", "r", "k")) + (0, 0)
    labels: list[int] = []
    counter = 0
    for _ in range(64):
        label, counter = prior.rejection_draw(
            purpose="query", parameters=parameters, seed=seed, counter=counter, n=int(fixture["r"]))
        labels.append(label)
    return labels, counter


def _fixture_public(fixture: Mapping[str, Any]) -> dict[str, Any]:
    return {name: int(fixture[name]) if name != "bin" else fixture[name]
            for name in ("p", "A", "B", "N", "r", "k", "bit_block", "bin")}


def exact_character_control(curve: Any, G: Any, T: Any, shift: Any, r: int, p: int, k: int) -> dict[str, Any]:
    chi_g, exponent = evaluate_shifted_tate(curve, r, G, T, shift, p, k)
    rows = []
    for scalar in range(r):
        observed, _ = evaluate_shifted_tate(curve, r, curve.scalar_mul(scalar, G), T, shift, p, k)
        rows.append({"a": scalar, "pass": observed == curve.field.pow(chi_g, scalar)})
    return {"chi_r_is_one": curve.field.pow(chi_g, r) == curve.field.one,
            "chi_nontrivial": chi_g != curve.field.one, "all_powers": all(row["pass"] for row in rows),
            "final_exponent": exponent, "rows": rows}


def isotropy_control(curve: Any, G: Any, r: int, p: int, k: int) -> dict[str, Any]:
    if k == 1:
        return {"applicable": False, "reason": "frozen protocol does not assert reduced-Tate self triviality at k=1"}
    try:
        chi, exponent = evaluate_shifted_tate(curve, r, G, G, curve.scalar_mul(2, G), p, k)
        return {"applicable": True, "trivial": chi == curve.field.one, "final_exponent": exponent}
    except PairingPole:
        return {"applicable": True, "trivial": False, "exception": "PairingPole"}


def coordinate_transport(curve: Any, point: Any, u: int) -> tuple[Any, Any]:
    field = curve.field
    scale = field.element(u)
    transported = ShortWeierstrassCurve(field, field.mul(curve.A, field.pow(scale, 4)), field.mul(curve.B, field.pow(scale, 6)))
    return transported, (field.mul(point[0], field.pow(scale, 2)), field.mul(point[1], field.pow(scale, 3)))


def dishonest_payload_control(item: PublicEvaluatorInput) -> dict[str, bool]:
    """Known-false label injection reaches both actual public boundary validators."""
    dishonest = item.mapping()
    dishonest["label"] = 7
    payload = canonical_json(dishonest)
    parent_rejected = child_rejected = False
    try:
        audit_public_payload(payload)
    except PublicSchemaError:
        parent_rejected = True
    try:
        _evaluate_public_payload(payload)
    except PublicSchemaError:
        child_rejected = True
    return {"parent_audit_rejected": parent_rejected, "child_entry_rejected": child_rejected,
            "passed": parent_rejected and child_rejected}


@dataclass
class ChargingLedger:
    shared_selection: float = 0.0
    field_construction: float = 0.0
    t_search: float = 0.0
    chi_g: float = 0.0
    field_table: float = 0.0
    chi_q: float = 0.0
    field_giant_steps: float = 0.0
    curve_table: float = 0.0
    curve_giant_steps: float = 0.0
    curve_verify: float = 0.0
    reconstruction: float = 0.0

    def character_total(self) -> float:
        return self.shared_selection + self.field_construction + self.t_search + self.chi_g + self.field_table + self.chi_q + self.field_giant_steps + self.curve_verify + self.reconstruction

    def curve_total(self) -> float:
        return self.shared_selection + self.curve_table + self.curve_giant_steps + self.curve_verify + self.reconstruction


def _future_cell(fixture: dict[str, Any], seed: int, shared_selection_cpu: float,
                 guard: MachineProtection, progress: Callable[[dict[str, Any]], None]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    """Future-only cell executor; uses fixed labels for all block/repeat replays."""
    p, A, B, r, k = (int(fixture[name]) for name in ("p", "A", "B", "r", "k"))
    field_started = time.process_time()
    polynomial_index, modulus, tested_indices, rabin = select_certified_modulus(p, k)
    field = PolynomialField(p, modulus)
    curve = ShortWeierstrassCurve(field, field.element(A), field.element(B))
    if "G" in fixture:
        encoded_generator = fixture["G"]
        if not isinstance(encoded_generator, list) or len(encoded_generator) != 2:
            raise ValueError("fixed calibration G must be an affine [x,y] point")
        generator = int(encoded_generator[0]), int(encoded_generator[1])
        generator_attempts = [{"status": "source_documented_fixed_generator", "point": list(generator)}]
    else:
        generator, generator_attempts = first_subgroup_generator_with_attempts(p=p, B=B, N=int(fixture["N"]), r=r)
    G = field.element(generator[0]), field.element(generator[1])
    field_cpu = time.process_time() - field_started
    t_started = time.process_time()
    T, shift, chi_g, t_attempts, point_attempts = bounded_t_search(curve, r, G, field, p=p, A=A, B=B, k=k, seed=PREPARATION_SEED)
    t_cpu = time.process_time() - t_started
    chi_started = time.process_time()
    if field.pow(chi_g, r) != field.one or chi_g == field.one:
        raise RuntimeError("accepted T did not produce a nontrivial rth root")
    chi_g_cpu = time.process_time() - chi_started
    public_context = _public_context(field, curve, G, T, shift, chi_g, r, p, k)
    labels, label_counter = fixed_q64_labels(fixture, seed)
    raw: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    elapsed_cpu = 0.0
    repetitions = 0
    while repetitions < 100:
        for block in range(7):
            order = "curve_first" if block % 2 == 0 else "character_first"
            for q in QUERY_COUNTS:
                workload = labels[:q]
                queries = []
                for query_id, label in enumerate(workload):
                    Q = curve.scalar_mul(label, G)
                    queries.append({"query_id": query_id, "Q": [list(Q[0]), list(Q[1])]})
                request = PublicEvaluatorInput(_fixture_public(fixture), batch_id=repetitions * 14 + block * 2 + (0 if q == 1 else 1),
                                               q=q, block=block, repetition=repetitions, order=order,
                                               queries=queries, context=public_context)
                result = invoke_public_evaluator(request, timeout_seconds=guard.watchdog_seconds, checkpoint=guard.checkpoint)
                for verifier_label, answer in zip(workload, result["results"]):
                    if answer["curve_answer"] != verifier_label or answer["character_answer"] != verifier_label or not answer["curve_verification"]:
                        raise RuntimeError("verifier-held label comparison or final curve verification failed")
                    raw.append({"fixture": _fixture_public(fixture), "seed": seed, "q": q, "block": block,
                                "repetition": repetitions, "order": order, "query_id": answer["query_id"],
                                "curve_answer": answer["curve_answer"], "character_answer": answer["character_answer"],
                                "verifier_match": True})
                costs = result["costs"]
                timer = costs["cpu_seconds"]
                ledger = ChargingLedger(shared_selection=shared_selection_cpu, field_construction=field_cpu,
                                       t_search=t_cpu, chi_g=chi_g_cpu, field_table=timer["field_table"],
                                       chi_q=timer["chi_q"], field_giant_steps=timer["field_giant_steps"],
                                       curve_table=timer["curve_table"], curve_giant_steps=timer["curve_giant_steps"],
                                       curve_verify=timer["curve_verify"], reconstruction=timer["field_reconstruction"])
                row = {"fixture_key": f"{fixture['bit_block']}:{fixture['bin']}:{p}:{B}:{r}", "seed": seed,
                       "q": q, "block": block, "repetition": repetitions, "arm_order": order,
                       **asdict(ledger), "character_total_cpu": ledger.character_total(), "curve_total_cpu": ledger.curve_total(),
                       "ratio_curve_over_character": (ledger.curve_total() / ledger.character_total()) if ledger.character_total() else None,
                       "wall_seconds": costs["wall_seconds"], "child_peak_rss_bytes": costs["peak_rss_bytes"],
                       "process_group_peak_rss_bytes": costs["process_group_peak_rss_bytes"], "field_table_bytes": costs["field_table_bytes"],
                       "curve_table_bytes": costs["curve_table_bytes"], "output_bytes": costs["output_bytes"],
                       "field_operation_count": costs["operation_counts"]["field"], "group_operation_count": costs["operation_counts"]["group"]}
                cost_rows.append(row)
                elapsed_cpu += costs["total_cpu_seconds"]
                progress({"event": "completed_batch", "fixture": _fixture_public(fixture), "seed": seed, "q": q,
                          "block": block, "repetition": repetitions, "cost_row": row})
        repetitions += 1
        if elapsed_cpu >= 0.1:
            break
    if elapsed_cpu < 0.1:
        raise RuntimeError("under-resolution after frozen 100 repeated complete workloads")
    transport_curve, tG = coordinate_transport(curve, G, 2)
    tT = coordinate_transport(curve, T, 2)[1]
    tS = coordinate_transport(curve, shift, 2)[1]
    tQ = transport_curve.scalar_mul(labels[0], tG)
    t_chi, _ = evaluate_shifted_tate(transport_curve, r, tG, tT, tS, p, k)
    transported_item = PublicEvaluatorInput(_fixture_public(fixture), 999999, 1, 0, 0, "curve_first",
                                            [{"query_id": 0, "Q": [list(tQ[0]), list(tQ[1])]}],
                                            _public_context(field, transport_curve, tG, tT, tS, t_chi, r, p, k))
    transported = invoke_public_evaluator(transported_item, timeout_seconds=guard.watchdog_seconds, checkpoint=guard.checkpoint)
    exact = exact_character_control(curve, G, T, shift, r, p, k)
    isotropy = isotropy_control(curve, G, r, p, k)
    null_ambiguous = False
    try:
        prepare_multiplicative_bsgs(field.one, r, field)
    except NoSolution:
        null_ambiguous = True
    injection = dishonest_payload_control(PublicEvaluatorInput(_fixture_public(fixture), 0, 1, 0, 0, "curve_first",
                                                               [{"query_id": 0, "Q": [list(curve.scalar_mul(labels[0], G)[0]), list(curve.scalar_mul(labels[0], G)[1])]}], public_context))
    flipped = field.add(chi_g, field.one)
    flipped_detected = any(evaluate_shifted_tate(curve, r, curve.scalar_mul(a, G), T, shift, p, k)[0] != field.pow(flipped, a) for a in range(r))
    controls = {"exact_character": exact, "base_field_isotropy": isotropy,
                "null_and_injection": {"trivial_character_ambiguous": null_ambiguous,
                                       "dishonest_encoder": injection, "flipped_coefficient_detected": flipped_detected},
                "coordinates": {"u": 2, "decoded_scalar_unchanged": all(row["curve_answer"] == labels[0] and row["character_answer"] == labels[0] for row in transported["results"])},
                "full_decoder": {"m": math.isqrt(r - 1) + 1, "baby": "0..m-1", "giant": "0..m", "curve_verified": all(row["verifier_match"] for row in raw)}}
    if not all(exact[name] for name in ("chi_r_is_one", "chi_nontrivial", "all_powers")):
        raise RuntimeError("exact character control failed")
    if isotropy.get("applicable") and not isotropy.get("trivial"):
        raise RuntimeError("base-field isotropy control failed")
    if not (null_ambiguous and injection["passed"] and flipped_detected and controls["coordinates"]["decoded_scalar_unchanged"]):
        raise RuntimeError("null, injection, flip, or coordinate control failed")
    certificate = {"fixture": _fixture_public(fixture), "polynomial_index": polynomial_index,
                   "tested_indices": tested_indices, "rabin": asdict(rabin), "generator_attempts": generator_attempts,
                   "extension_point_attempts": point_attempts, "T_attempts": t_attempts,
                   "accepted_final_exponent": (p ** k - 1) // r, "q64_labels_sha256": hashlib.sha256(canonical_json(labels)).hexdigest(),
                   "q64_rng_counter_after": label_counter}
    return {"fixture": _fixture_public(fixture), "seed": seed, "repetitions": repetitions, "raw": raw}, controls, cost_rows, certificate


def validate_panel_coverage(selected: list[dict[str, Any]], cell_records: list[dict[str, Any]], calibration: Mapping[str, Any] | None) -> dict[str, Any]:
    expected = {(bits, bin_name) for bits in (8, 10) for bin_name in ("1", "2", "3_6", "7_12")}
    observed = {(int(item["bit_block"]), str(item["bin"])) for item in selected}
    problems: list[str] = []
    if len(selected) != 8 or observed != expected:
        problems.append("selected fixtures do not form the exact eight-cell frozen panel")
    for fixture in selected:
        fixture_key = (fixture["bit_block"], fixture["bin"], fixture["p"], fixture["B"], fixture["r"], fixture["k"])
        seen = {entry["seed"] for entry in cell_records if (entry["fixture"]["bit_block"], entry["fixture"]["bin"], entry["fixture"]["p"], entry["fixture"]["B"], entry["fixture"]["r"], entry["fixture"]["k"]) == fixture_key}
        if set(TARGET_SEEDS) != seen:
            problems.append(f"fixture {fixture_key} does not have both frozen target seeds")
    if not calibration or calibration.get("status") != "completed_valid":
        problems.append("mandatory source-documented calibration is absent or invalid")
    elif not (calibration.get("controls", {}).get("exact_character", {}).get("all_powers")
              and calibration.get("controls", {}).get("null_and_injection", {}).get("dishonest_encoder", {}).get("passed")):
        problems.append("mandatory source-documented calibration lacks complete controls")
    for record in cell_records:
        controls = record["controls"]
        if not (controls["exact_character"]["all_powers"] and controls["null_and_injection"]["dishonest_encoder"]["passed"] and controls["full_decoder"]["curve_verified"]):
            problems.append("one cell lacks complete mandatory controls")
    return {"complete": not problems, "problems": problems, "expected_cells": 8,
            "selected_cells": len(selected), "seeds_per_fixture": list(TARGET_SEEDS)}


def decision_matrix(cost_rows: Sequence[Mapping[str, Any]], selected: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Frozen finite-panel predicates, emitted as data without a scientific conclusion."""
    selected_keys = {
        f"{item['bit_block']}:{item['bin']}:{item['p']}:{item['B']}:{item['r']}"
        for item in selected
    }
    per_cell_seed: dict[tuple[int, str, int], list[float]] = {}
    for row in cost_rows:
        if row["fixture_key"] in selected_keys and row["q"] == 64 and row["ratio_curve_over_character"] is not None:
            per_cell_seed.setdefault((int(row["seed"]), row["fixture_key"].split(":")[0], row["fixture_key"].split(":")[1]), []).append(float(row["ratio_curve_over_character"]))
    medians = {"|".join(map(str, key)): median(values) for key, values in per_cell_seed.items() if values}
    positive_bins = []
    for bin_name in ("1", "2", "3_6", "7_12"):
        holds = True
        for bits in (8, 10):
            for seed in TARGET_SEEDS:
                key = f"{seed}|{bits}|{bin_name}"
                holds = holds and medians.get(key, float("-inf")) >= 1.20
        if holds:
            positive_bins.append(bin_name)
    all_le_one = bool(medians) and all(value <= 1.0 for value in medians.values())
    return {"q": 64, "cell_seed_median_ratios": medians,
            "positive_predicate": {"at_least_one_bin_both_bit_blocks_both_seeds_ge_1_20": bool(positive_bins), "bins": positive_bins},
            "negative_predicate": {"all_cells_both_seeds_le_1_00": all_le_one},
            "interpretation": "uninterpreted frozen decision inputs; independent review decides any research conclusion"}


# Future launch authority and custody -------------------------------------

def _lock_payload(lock: Mapping[str, Any]) -> bytes:
    return canonical_json({key: value for key, value in lock.items() if key != "signature_b64"})


def _contains_bedrock(value: Any) -> bool:
    if isinstance(value, str):
        return "bedrock" in value.casefold()
    if isinstance(value, Mapping):
        return any(_contains_bedrock(key) or _contains_bedrock(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_bedrock(item) for item in value)
    return False


def repository_git_state() -> tuple[str, bool]:
    root = Path(__file__).resolve().parents[4]
    commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, check=True).stdout.strip())
    return commit, dirty


def _verify_detached_signature(public_key: Path, payload: bytes, signature: bytes) -> None:
    if not public_key.is_file():
        raise LaunchRefused("separately trusted Coordinator public key is unavailable")
    with tempfile.NamedTemporaryFile(dir=public_key.parent, prefix=".tate-lock-payload-", delete=False) as payload_file, \
         tempfile.NamedTemporaryFile(dir=public_key.parent, prefix=".tate-lock-signature-", delete=False) as signature_file:
        payload_file.write(payload)
        signature_file.write(signature)
        payload_path, signature_path = Path(payload_file.name), Path(signature_file.name)
    try:
        os.chmod(payload_path, 0o600)
        os.chmod(signature_path, 0o600)
        checked = subprocess.run(["openssl", "pkeyutl", "-verify", "-pubin", "-inkey", str(public_key), "-in", str(payload_path), "-sigfile", str(signature_path)], capture_output=True, text=True, timeout=10)
    finally:
        payload_path.unlink(missing_ok=True)
        signature_path.unlink(missing_ok=True)
    if checked.returncode != 0:
        raise LaunchRefused("Coordinator detached signature failed verification")


def canonical_run_paths(root: Path, run_id: str) -> dict[str, Path]:
    if not run_id or any(part in run_id for part in ("/", "\\", "..")):
        raise LaunchRefused("unsafe future run id")
    base = root.resolve() / "runs" / run_id
    return {name: base / name for name in RUN_FILES}


def verify_launch_lock(lock_path: Path, trusted_coordinator_public_key: Path, plan_path: Path,
                       run_id: str, run_root: Path) -> dict[str, Any]:
    """Fail closed unless a real future authority binds this exact execution."""
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LaunchRefused(f"unreadable future launch lock: {exc}") from exc
    required = {"kind", "experiment_id", "frozen_approval_decision_id", "implementation_approval_decision_id",
                "spec_sha256", "execution_plan_sha256", "source_closure", "review_archive", "runtime",
                "implementation_commit", "dirty_tree", "run_id", "nonce", "output_path", "resource_limits",
                "machine_protection", "signature_b64"}
    if not isinstance(lock, dict) or required - set(lock) or lock.get("kind") != "genuine_runtime_code_execution_lock":
        raise LaunchRefused("future lock lacks the complete canonical authority fields")
    if (lock["experiment_id"], lock["frozen_approval_decision_id"], lock["implementation_approval_decision_id"], lock["spec_sha256"]) != (EXPERIMENT_ID, FROZEN_APPROVAL_ID, IMPLEMENTATION_APPROVAL_ID, SPEC_SHA256):
        raise LaunchRefused("future lock binds another protocol or approval")
    if lock["execution_plan_sha256"] != sha256_file(plan_path):
        raise LaunchRefused("future lock execution-plan bytes differ")
    expected_closure = {str(Path(__file__).resolve()): sha256_file(Path(__file__)), str(_prior_path.resolve()): PREDECESSOR_SHA256}
    if lock["source_closure"] != expected_closure:
        raise LaunchRefused("future lock does not bind the exact transitive executed source closure")
    archive = lock["review_archive"]
    if not isinstance(archive, dict) or archive.get("snapshot_task_id") != REVIEWED_SNAPSHOT_TASK_ID or archive.get("verdict") != "PASS" or not isinstance(archive.get("reviewed_snapshot_commit"), str) or not isinstance(archive.get("review_task_id"), str) or not isinstance(archive.get("review_commit"), str) or archive.get("reviewed_snapshot_commit") == lock["implementation_commit"] or archive.get("review_commit") == lock["implementation_commit"] or archive.get("reviewed_source_closure") != expected_closure:
        raise LaunchRefused("future lock lacks a distinct reviewed snapshot/archive and passing fresh implementation verdict")
    runtime = lock["runtime"]
    if not isinstance(runtime, dict) or runtime.get("model_verified") is not True or _contains_bedrock(runtime):
        raise LaunchRefused("future lock runtime is unverified or selects prohibited Bedrock")
    if lock["run_id"] != run_id or not isinstance(lock["nonce"], str) or len(lock["nonce"]) < 32:
        raise LaunchRefused("future lock does not bind the allocated run id and nonce")
    expected_output = str(next(iter(canonical_run_paths(run_root, run_id).values())).parent)
    if lock["output_path"] != expected_output:
        raise LaunchRefused("future lock output path does not equal canonical run directory")
    if lock["resource_limits"] != RESOURCE_LIMITS:
        raise LaunchRefused("future lock resource tuple differs from enforced 8GiB/one-worker protection")
    protection = lock["machine_protection"]
    if not isinstance(protection, dict) or not (protection.get("parent_rlimit_as") and protection.get("child_rlimit_as") and protection.get("serial_worker") and protection.get("process_group_termination") and isinstance(protection.get("watchdog_seconds"), int) and protection["watchdog_seconds"] > 0 and isinstance(protection.get("watchdog_justification"), str) and protection["watchdog_justification"]):
        raise LaunchRefused("future lock lacks justified cancellation and machine-protection bindings")
    commit, dirty = repository_git_state()
    if lock["implementation_commit"] != commit or lock["dirty_tree"] is not False or dirty:
        raise LaunchRefused("future lock does not bind current clean implementation commit/bytes")
    try:
        signature = base64.b64decode(lock["signature_b64"], validate=True)
    except Exception as exc:
        raise LaunchRefused("future lock detached signature is malformed") from exc
    _verify_detached_signature(trusted_coordinator_public_key, _lock_payload(lock), signature)
    return lock


class ProgressiveRunWriter:
    """Write durable partial custody after each stage; publish atomically only once."""
    def __init__(self, root: Path, run_id: str):
        self.paths = canonical_run_paths(root, run_id)
        self.final = next(iter(self.paths.values())).parent
        if self.final.exists():
            raise LaunchRefused("canonical run id already exists and cannot be overwritten")
        self.partial = self.final.with_name(self.final.name + ".partial-" + uuid.uuid4().hex)
        self.partial.mkdir(parents=True, mode=0o700)
        self.events: list[dict[str, Any]] = []

    def checkpoint(self, event: Mapping[str, Any]) -> None:
        self.events.append(dict(event))
        destination = self.partial / "progress.json"
        temporary = destination.with_suffix(".tmp")
        temporary.write_bytes(canonical_json({"events": self.events, "updated_at": utc_now()}))
        os.replace(temporary, destination)

    def publish(self, records: Mapping[str, Any]) -> dict[str, Path]:
        _write_run_files(self.partial, records)
        os.replace(self.partial, self.final)
        return self.paths


def _write_run_files(directory: Path, records: Mapping[str, Any]) -> None:
    (directory / "manifest.yaml").write_bytes(canonical_json(records["manifest"]) + b"\n")
    (directory / "command.txt").write_text(str(records["command"]) + "\n", encoding="utf-8")
    (directory / "environment.json").write_bytes(canonical_json(records["environment"]) + b"\n")
    (directory / "raw-result.json").write_bytes(canonical_json(records["raw_result"]) + b"\n")
    (directory / "fixtures.json").write_bytes(canonical_json(records["fixtures"]) + b"\n")
    with (directory / "raw.jsonl").open("wb") as handle:
        for row in records["raw"]:
            handle.write(canonical_json(row) + b"\n")
    (directory / "controls.json").write_bytes(canonical_json(records["controls"]) + b"\n")
    rows = list(records["cost_rows"])
    fields = sorted({key for row in rows for key in row}) or ["no_cost_rows"]
    with (directory / "costs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    (directory / "certificates.json").write_bytes(canonical_json(records["certificates"]) + b"\n")
    (directory / "stdout.log").write_text(str(records.get("stdout", "")), encoding="utf-8")
    (directory / "stderr.log").write_text(str(records.get("stderr", "")), encoding="utf-8")
    (directory / "report.md").write_text(str(records["report"]), encoding="utf-8")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _environment() -> dict[str, Any]:
    return {"operating_system": platform.platform(), "architecture": platform.machine(),
            "python_version": sys.version, "dependencies": {"stdlib_only": True}}


def execute_authorized_run(lock_path: Path, key_path: Path, plan_path: Path, run_id: str, root: Path) -> dict[str, Path]:
    """Future-only scientific path; no caller may reach it before full lock validation."""
    lock = verify_launch_lock(lock_path, key_path, plan_path, run_id, root)
    _set_as_limit()
    protection = MachineProtection(lock["machine_protection"]["watchdog_seconds"])
    handlers = install_cancellation_handlers(protection)
    writer = ProgressiveRunWriter(root, run_id)
    started_wall, started_cpu = time.monotonic(), time.process_time()
    raw: list[dict[str, Any]] = []
    cells: list[dict[str, Any]] = []
    controls: dict[str, Any] = {}
    certificates: list[dict[str, Any]] = []
    cost_rows: list[dict[str, Any]] = []
    fixtures: dict[str, Any] = {"selected": [], "candidate_history": [], "calibration": None}
    failures: list[dict[str, Any]] = []
    status = "failed_implementation"
    try:
        selection_started = time.process_time()
        selected, history = build_future_fixtures(writer.checkpoint)
        selection_cpu = time.process_time() - selection_started
        fixtures.update({"selected": selected, "candidate_history": history})
        writer.checkpoint({"event": "fixture_selection_complete", "selected_count": len(selected), "selection_cpu_seconds": selection_cpu})
        shared_per_fixture = selection_cpu / 8
        for fixture in selected:
            for seed in TARGET_SEEDS:
                protection.checkpoint()
                cell, cell_controls, cell_costs, certificate = _future_cell(fixture, seed, shared_per_fixture, protection, writer.checkpoint)
                cells.append({**cell, "controls": cell_controls})
                raw.extend(cell["raw"])
                controls[f"{fixture['bit_block']}:{fixture['bin']}:{seed}"] = cell_controls
                cost_rows.extend(cell_costs)
                certificates.append(certificate)
                writer.checkpoint({"event": "cell_complete", "fixture": _fixture_public(fixture), "seed": seed,
                                   "raw_rows": len(cell["raw"]), "cost_rows": len(cell_costs)})
        # The source-documented fixture follows the same field, T/shift,
        # public-evaluator, controls, and cost path.  It is deliberately a
        # calibration, never a substitute for a missing selected fixture.
        calibration_fixture = {"p": 103, "A": 1, "B": 18, "N": 0, "G": [33, 91], "r": 19,
                               "k": 6, "bit_block": 0, "bin": "3_6"}
        calibration_cell, calibration_controls, calibration_costs, calibration_certificate = _future_cell(
            calibration_fixture, TARGET_SEEDS[0], 0.0, protection, writer.checkpoint)
        raw.extend(calibration_cell["raw"])
        cost_rows.extend(calibration_costs)
        certificates.append(calibration_certificate)
        calibration = {"status": "completed_valid", "fixture": calibration_cell["fixture"],
                       "seed": TARGET_SEEDS[0], "controls": calibration_controls,
                       "certificate": calibration_certificate}
        fixtures["calibration"] = calibration
        coverage = validate_panel_coverage(selected, cells, calibration)
        if not coverage["complete"]:
            raise RuntimeError("full frozen panel/calibration/control coverage gate failed: " + "; ".join(coverage["problems"]))
        status = "completed_valid"
    except SearchExhausted as exc:
        status = "completed_invalid"
        failures.append(asdict(RunFailure("partial_search_exhausted", "preparation", type(exc).__name__, str(exc))))
        fixtures["candidate_history"] = getattr(exc, "fixture_history", fixtures["candidate_history"])
        writer.checkpoint({"event": "partial_search_exhausted", "detail": str(exc)})
    except RunInterrupted as exc:
        status = "resource_exhaustion"
        failures.append(asdict(RunFailure("resource_exhaustion", "machine_protection", type(exc).__name__, str(exc))))
        writer.checkpoint({"event": "interrupted", "detail": str(exc)})
    except (PairingPole, PublicSchemaError) as exc:
        status = "completed_invalid"
        failures.append(asdict(RunFailure("invalid_measurement", "control_or_pairing", type(exc).__name__, str(exc))))
        writer.checkpoint({"event": "invalid_measurement", "detail": str(exc)})
    except OSError as exc:
        status = "failed_infrastructure"
        failures.append(asdict(RunFailure("infrastructure_error", "runner", type(exc).__name__, str(exc))))
        writer.checkpoint({"event": "infrastructure_error", "detail": str(exc)})
    except Exception as exc:
        status = "failed_implementation"
        failures.append(asdict(RunFailure("implementation_error", "runner", type(exc).__name__, str(exc))))
        writer.checkpoint({"event": "implementation_error", "detail": str(exc), "traceback": traceback.format_exc()})
    finally:
        restore_cancellation_handlers(handlers)
    coverage = validate_panel_coverage(fixtures["selected"], cells, fixtures["calibration"]) if fixtures["selected"] else {"complete": False, "problems": ["no complete selected panel"]}
    metrics = decision_matrix(cost_rows, fixtures["selected"]) if cost_rows else {"status": "not_computed", "reason": "no complete cost matrix"}
    command = f"{sys.executable} {Path(__file__).resolve()} --launch-lock {lock_path} --coordinator-public-key {key_path} --execution-plan {plan_path} --run-id {run_id} --run-root {root}"
    manifest = {"run": {"id": run_id, "experiment_id": EXPERIMENT_ID, "status": status,
                           "code": {"commit": lock["implementation_commit"], "dirty": False,
                                    "source_closure": lock["source_closure"]}, "inference": lock["runtime"],
                           "approval": {"frozen": FROZEN_APPROVAL_ID, "implementation": IMPLEMENTATION_APPROVAL_ID,
                                        "review_archive": lock["review_archive"]}, "command": command,
                           "inputs": {"seeds": [PREPARATION_SEED, *TARGET_SEEDS], "nonce": lock["nonce"]},
                           "timestamps": {"started_at": utc_now(), "finished_at": utc_now()},
                           "resources": {"wall_seconds": time.monotonic() - started_wall,
                                         "cpu_seconds_parent": time.process_time() - started_cpu,
                                         "peak_rss_bytes_parent": _rss_bytes(), "limits": RESOURCE_LIMITS,
                                         "machine_protection": lock["machine_protection"]},
                           "metrics": metrics, "coverage": coverage,
                           "validity": {"valid": status == "completed_valid", "failures": failures},
                           "artifacts": {name: str(path) for name, path in canonical_run_paths(root, run_id).items()}}}
    records = {"manifest": manifest, "command": command, "environment": _environment(),
               "raw_result": {"status": status, "failures": failures, "coverage": coverage, "decision_matrix": metrics},
               "fixtures": fixtures, "raw": raw, "controls": controls, "cost_rows": cost_rows,
               "certificates": certificates, "stderr": "\n".join(failure["detail"] for failure in failures),
               "report": "# Future run package\n\nThe runner records frozen decision inputs only. Independent review is required before any scientific interpretation.\n"}
    return writer.publish(records)


def coverage() -> dict[str, Any]:
    return {"task_id": TASK_ID, "mode": "prospective_nonlaunching", "rabin": "reduced-X degree-one comparison plus k>1 gcd witnesses",
            "public_schema": "closed recursive typed allowlist in parent and evaluator child",
            "workloads": "one fixed verifier-only q64 label list per fixture/seed, q1 prefix, actual alternating order",
            "costs": "per-cell/seed/q/block/repetition components, byte/RSS markers, median decision inputs",
            "custody": "progressive partial checkpoints and immutable canonical package publication",
            "authority": "detached signed future approval/source/review/runtime/run/nonce/output/machine-protection lock",
            "scientific_runs_started": 0}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prospective EXP-ECDLP-910fcd runner; dry run by default")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--launch-lock", type=Path)
    parser.add_argument("--coordinator-public-key", type=Path)
    parser.add_argument("--execution-plan", type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--run-root", type=Path, default=Path.cwd())
    parser.add_argument("--evaluator-stdin", action="store_true")
    args = parser.parse_args(argv)
    if args.evaluator_stdin:
        _limit_child()
        payload = sys.stdin.buffer.read()
        result = _evaluate_public_payload(payload)
        sys.stdout.buffer.write(canonical_json(result))
        return 0
    if args.launch_lock:
        if not all((args.coordinator_public_key, args.execution_plan, args.run_id)):
            raise LaunchRefused("launch requires lock, trusted public key, plan, and allocated run id")
        execute_authorized_run(args.launch_lock, args.coordinator_public_key, args.execution_plan, args.run_id, args.run_root)
        return 0
    print(json.dumps({"status": "dry_run_not_launched", "coverage": coverage()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
