#!/usr/bin/env python3
"""Independent, linear-oracle validation for the fixed constructor screen.

This module imports no candidate or candidate arithmetic.  Its scalar tables and
O(r)-per-query sum-of-slopes primitive are validator-only objects.  Merely
importing this file does not execute a candidate screen.  A complete CLI check
requires the separately frozen protocol and the actual record stream.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from math import isqrt
from pathlib import Path
import re
from typing import Any, Iterable

Point = tuple[int, int] | None
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
DEFAULT_FIXTURE = {"p": 11, "a": 1, "b": 6, "r": 13, "seed_base": [2, 7]}
DEFAULT_ALPHA = [0, 1, 2, -2, -3]
DEFAULT_BETA = [1, 2, 3, 4, -1, -2, -3, -4]
DEFAULT_CONTROLS = {
    "invalid_anchor": {"alpha": -1, "beta": 1},
    "fiber": {"alpha": DEFAULT_ALPHA, "beta": 0},
    "wrong_root": True,
    "aa_replay": {"alpha": 0, "beta": 1, "reference_id": "candidate:a0:b1"},
}


def point(value: Any, p: int) -> Point:
    if value is None:
        return None
    if not isinstance(value, (tuple, list)) or len(value) != 2:
        raise ValueError("point must be null or a two-integer coordinate array")
    if any(type(x) is not int or not 0 <= x < p for x in value):
        raise ValueError("point coordinates must be canonical field integers")
    return int(value[0]), int(value[1])


def encoded(value: Point) -> list[int] | None:
    return list(value) if value is not None else None


def prime(n: int, counts: Counter[str] | None = None) -> bool:
    if type(n) is not int or n < 2:
        return False
    for divisor in range(2, isqrt(n) + 1):
        if counts is not None:
            counts["input_primality_trial_division"] += 1
        if n % divisor == 0:
            return False
    return True


class OracleGroup:
    """Separate affine implementation, with explicit validator work counters."""

    def __init__(self, model: dict[str, int]):
        self.p, self.a, self.b, self.r = (model[k] for k in ("p", "a", "b", "r"))
        self.counts: Counter[str] = Counter()
        if not prime(self.p, self.counts) or self.p <= 3 or not prime(self.r, self.counts) or self.r % 2 == 0 or self.r == self.p:
            raise ValueError("validator domain requires p>3 and odd prime r!=p")
        self.counts["input_discriminant_check"] += 1
        if (4 * self.a**3 + 27 * self.b**2) % self.p == 0:
            raise ValueError("singular curve")
        self.model = {k: model[k] for k in ("p", "a", "b", "r")}

    def addf(self, x: int, y: int) -> int:
        self.counts["field_add"] += 1
        return (x + y) % self.p

    def subf(self, x: int, y: int) -> int:
        self.counts["field_subtract"] += 1
        return (x - y) % self.p

    def mulf(self, x: int, y: int) -> int:
        self.counts["field_multiply"] += 1
        return x * y % self.p

    def square(self, x: int) -> int:
        self.counts["field_square"] += 1
        return x * x % self.p

    def inverse(self, x: int) -> int:
        self.counts["field_inverse"] += 1
        if x % self.p == 0:
            raise ZeroDivisionError("zero field inverse")
        return pow(x, -1, self.p)

    def eq(self, x: Any, y: Any) -> bool:
        self.counts["equality"] += 1
        return x == y

    def on_curve(self, value: Point) -> bool:
        self.counts["point_check"] += 1
        if value is None:
            return True
        x, y = value
        return self.eq(self.square(y), self.addf(self.addf(self.mulf(self.square(x), x), self.mulf(self.a, x)), self.b))

    def neg(self, value: Point) -> Point:
        self.counts["group_negate"] += 1
        return None if value is None else (value[0], self.subf(0, value[1]))

    def slope(self, left: Point, right: Point) -> int:
        self.counts["slope"] += 1
        if self.eq(left, None) or self.eq(right, None):
            self.counts["identity_slope"] += 1
            return 0
        assert left is not None and right is not None
        x, y = left
        z, w = right
        if self.eq(x, z):
            if self.eq(self.addf(y, w), 0):
                self.counts["vertical_slope"] += 1
                return 0
            numerator = self.addf(self.mulf(3, self.square(x)), self.a)
            denominator = self.mulf(2, y)
        else:
            numerator, denominator = self.subf(w, y), self.subf(z, x)
        return self.mulf(numerator, self.inverse(denominator))

    def add(self, left: Point, right: Point) -> Point:
        self.counts["group_add"] += 1
        if self.eq(left, None):
            self.counts["identity_add"] += 1
            return right
        if self.eq(right, None):
            self.counts["identity_add"] += 1
            return left
        assert left is not None and right is not None
        x, y = left
        z, w = right
        if self.eq(x, z) and self.eq(self.addf(y, w), 0):
            self.counts["vertical_add"] += 1
            return None
        lam = self.slope(left, right)
        out_x = self.subf(self.subf(self.square(lam), x), z)
        out_y = self.subf(self.mulf(lam, self.subf(x, out_x)), y)
        return out_x, out_y

    def multiply(self, scalar: int, value: Point) -> Point:
        """Independent repeated addition (linear, intentionally not candidate code)."""
        self.counts["scalar_multiply_calls"] += 1
        if scalar < 0:
            value, scalar = self.neg(value), -scalar
        out = None
        for _ in range(scalar):
            out = self.add(out, value)
        return out

    def orbit(self, base: Point) -> list[Point]:
        if base is None or not self.on_curve(base):
            raise ValueError("base is not a nonidentity curve point")
        out: list[Point] = [None]
        current = None
        seen = {None}
        for _ in range(1, self.r):
            current = self.add(current, base)
            if current in seen or not self.on_curve(current):
                raise ValueError("base does not have exact declared order")
            out.append(current)
            seen.add(current)
        if self.add(current, base) is not None:
            raise ValueError("base does not have exact declared order")
        self.counts["oracle_table_entries"] += len(out)
        return out

    def primitive(self, target: Point, orbit: list[Point]) -> int:
        """Z(R)=-sum_{T in G} lambda(R,T)/r; O(r), no binary D recurrence."""
        self.counts["primitive_oracle_queries"] += 1
        total = 0
        for other in orbit:
            self.counts["primitive_oracle_terms"] += 1
            total = self.addf(total, self.slope(target, other))
        return self.mulf(self.subf(0, total), self.inverse(self.r % self.p))

    def character(self, value: int) -> int:
        """Count a square-and-multiply implementation rather than a free pow."""
        value %= self.p
        self.counts["character_calls"] += 1
        exponent, out = (self.p - 1) // 2, 1
        while exponent:
            if exponent & 1:
                out = self.mulf(out, value)
            exponent >>= 1
            if exponent:
                value = self.square(value)
        return -1 if out == self.p - 1 else out

    def power(self, value: int, exponent: int) -> int:
        out = 1
        while exponent:
            if exponent & 1:
                out = self.mulf(out, value)
            exponent >>= 1
            if exponent:
                value = self.square(value)
        return out


def truth_half(scalar: int, r: int) -> int:
    if not 0 <= scalar < r:
        raise ValueError("truth scalar outside canonical range")
    return int(scalar > (r - 1) // 2)


def wrong_root(oracle: OracleGroup, base: Point, target: Point) -> dict[str, Any]:
    """Public anchored square-root control; at seed F11 base sigma=-f^3."""
    assert base is not None
    p = oracle.p
    if p % 4 != 3:
        return {"status": "UNDEFINED", "bit": None, "reason": "DOMAIN_UNSUPPORTED"}
    base_f = oracle.square(base[1])
    anchor_root = oracle.power(base_f, (p + 1) // 4)
    if anchor_root == 0:
        return {"status": "UNDEFINED", "bit": None, "reason": "ZERO_ANCHOR"}
    factor = oracle.mulf(base[1], oracle.inverse(anchor_root))
    if target is None:
        return {"status": "BIT", "bit": 0, "reason": None, "root": None, "z": 0, "g": None, "anchor": anchor_root, "normalized": None}
    root = oracle.mulf(factor, oracle.power(oracle.square(target[1]), (p + 1) // 4))
    if target[1] == root:
        bit = 0
    elif target[1] == -root % p:
        bit = 1
    else:
        return {"status": "UNDEFINED", "bit": None, "reason": "ROOT_SIGN_MISMATCH", "root": root, "z": None, "g": None, "anchor": anchor_root, "normalized": None}
    return {"status": "BIT", "bit": bit, "reason": None, "root": root, "z": None, "g": None, "anchor": anchor_root, "normalized": None}


def expected_result(oracle: OracleGroup, base: Point, target: Point, arm: dict[str, Any], z: dict[Point, int]) -> dict[str, Any]:
    """Independent arithmetic check; no scalar index is consulted here."""
    if arm["kind"] == "wrong_root":
        return wrong_root(oracle, base, target)
    assert base is not None
    p, zp = oracle.p, z[base]
    common = {"bit": None, "g": None, "anchor": None, "normalized": None, "z": None}
    if p % 4 != 3:
        return dict(common, status="UNDEFINED", reason="DOMAIN_UNSUPPORTED")
    if base[1] == 0:
        return dict(common, status="UNDEFINED", reason="ZERO_BASE_Y")
    if zp == 0:
        return dict(common, status="UNDEFINED", reason="ZERO_BASE_Z")
    alpha, beta = arm["alpha_integer"] % p, arm["beta_integer"] % p
    anchor = oracle.mulf(oracle.addf(1, alpha), zp)
    if anchor == 0:
        return dict(common, anchor=anchor, status="UNDEFINED", reason="ZERO_ANCHOR")
    if target is None:
        return dict(common, z=0, anchor=anchor, status="BIT", bit=0, reason=None)
    c = oracle.mulf(zp, oracle.inverse(base[1]))
    inner = oracle.addf(alpha, oracle.mulf(oracle.mulf(beta, c), oracle.subf(target[0], base[0])))
    numerator = oracle.addf(z[target], oracle.mulf(oracle.mulf(c, target[1]), inner))
    values = dict(common, z=z[target], g=numerator, anchor=anchor)
    if numerator == 0:
        return dict(values, status="UNDEFINED", reason="ZERO_NUMERATOR")
    norm = oracle.mulf(numerator, oracle.inverse(anchor))
    values["normalized"] = norm
    return dict(values, status="BIT", bit=(1 - oracle.character(norm)) // 2, reason=None)


def retained_bit_reduction(oracle: OracleGroup, base: Point, target: Point, bits: dict[Point, int | None]) -> dict[str, Any]:
    """Validator-only reduction check: table reads, zero constructor evaluations."""
    current, v = target, 0
    digits: list[int] = []
    length = oracle.r.bit_length() + 1
    for index in range(length):
        digit = bits.get(current)
        if digit not in (0, 1):
            return {"status": "UNDEFINED", "scalar": None, "verified": False, "digits": digits,
                    "predicate_calls": 0, "predicate_evaluations": 0, "retained_bit_reads": len(digits) + 1,
                    "oracle_table_verifier_only": True}
        digits.append(digit)
        v = (v << 1) | digit
        if index + 1 < length:
            current = oracle.add(current, current)
    denominator = 1 << len(digits)
    scalar = (oracle.r * v + denominator - 1) // denominator
    verified = 0 <= scalar < oracle.r and oracle.multiply(scalar, base) == target
    return {"status": "RECOVERED" if verified else "FAILED", "scalar": scalar, "verified": verified, "digits": digits,
            "predicate_calls": 0, "predicate_evaluations": 0, "retained_bit_reads": len(digits),
            "oracle_table_verifier_only": True}


def public_gate(oracle: OracleGroup, base: Point, orbit: list[Point], bits: dict[Point, int | None], target_order: list[Point] | None = None) -> dict[str, Any]:
    """Decide the public all-point identity/pulse gate, without scalar truth."""
    targets = target_order if target_order is not None else [None] + sorted(t for t in orbit if t is not None)
    middle, negative = oracle.multiply((oracle.r - 1) // 2, base), oracle.neg(base)
    residual = []
    undefined = len(targets) != oracle.r or set(targets) != set(orbit) or any(bits.get(t) not in (0, 1) for t in orbit)
    for target in targets:
        following = oracle.add(target, base)
        left, right = bits.get(following), bits.get(target)
        pulse = int(target == middle) - int(target == negative)
        residual.append(None if left not in (0, 1) or right not in (0, 1) else left - right - pulse)
    passed = not undefined and bits.get(None) == 0 and all(value == 0 for value in residual)
    reason = None if passed else ("UNDEFINED_COVERAGE" if undefined else "IDENTITY_OR_TWO_PULSE_FAILURE")
    return {"pass": passed, "not_attempted_reason": reason, "two_pulse_residual": residual,
            "target_order": [encoded(t) for t in targets]}


def group_obligations(oracle: OracleGroup, base: Point, orbit: list[Point], bits: dict[Point, int | None], *, allow_recovery: bool = True) -> dict[str, Any]:
    truth = {target: truth_half(i, oracle.r) for i, target in enumerate(orbit)}
    undefined = [encoded(t) for t in orbit if bits.get(t) not in (0, 1)]
    mismatches = [{"target": encoded(t), "expected_bit": truth[t], "observed_bit": bits.get(t)} for t in orbit if bits.get(t) in (0, 1) and bits[t] != truth[t]]
    gate = public_gate(oracle, base, orbit, bits)
    residual = gate["two_pulse_residual"]
    oddness = []
    for target in orbit[1:]:
        a, b = bits.get(target), bits.get(oracle.neg(target))
        if a in (0, 1) and b in (0, 1) and a + b != 1:
            oddness.append(encoded(target))
    ordering_pass = not undefined and not mismatches and bits.get(None) == 0 and all(x == 0 for x in residual)
    recoveries = []
    if ordering_pass and allow_recovery:
        recoveries = [{"target": encoded(t), **retained_bit_reduction(oracle, base, t, bits)} for t in orbit]
    return {
        "coverage_pass": not undefined,
        "ordering_pass": ordering_pass,
        "undefined_count": len(undefined),
        "undefined_targets": undefined,
        "truth_mismatch_count": len(mismatches),
        "first_counterexample": mismatches[0] if mismatches else ({"target": undefined[0], "status": "UNDEFINED"} if undefined else None),
        "two_pulse_residual": residual,
        "two_pulse_target_order": gate["target_order"],
        "public_gate": gate,
        "oddness_failures": oddness,
        "retained_bit_reduction_attempted": bool(recoveries),
        "retained_bit_reduction_verified_count": sum(x["verified"] for x in recoveries),
        "retained_bit_reduction_pass": bool(recoveries) and all(x["verified"] for x in recoveries),
        "retained_bit_reductions": recoveries,
        "actual_recovery_attempted": False,
        "actual_recovery_verified_count": 0,
        "actual_recovery_pass": False,
    }


def count_map(value: Any) -> bool:
    return isinstance(value, dict) and all(type(number) is int and number >= 0 for number in value.values())


def validate_fresh_recovery(oracle: OracleGroup, base: Point, target: Point, arm: dict[str, Any], z: dict[Point, int], result: dict[str, Any]) -> dict[str, Any]:
    """Independently check a real fresh-call trace, never synthesize its calls."""
    errors: list[str] = []
    length = oracle.r.bit_length() + 1
    trace = result.get("predicate_trace")
    if not isinstance(trace, list):
        return {"pass": False, "errors": ["predicate_trace missing"], "predicate_evaluations": 0, "evaluate_counts": {}, "reduction_counts": {}}
    if len(trace) != length or any(type(result.get(field)) is not int or result.get(field) != length for field in ("predicate_calls", "predicate_evaluations")):
        errors.append("fresh recovery requires exactly L fresh predicate evaluations")
    if type(result.get("retained_bit_reads")) is not int or result.get("retained_bit_reads") != 0 or result.get("oracle_table_verifier_only") is not False:
        errors.append("actual recovery must perform zero retained-bit reads and use no validator table")
    evaluate_counts: Counter[str] = Counter()
    current, value = target, 0
    for index, entry in enumerate(trace):
        try:
            observed_target = point(entry["target"], oracle.p)
            if observed_target != current:
                errors.append(f"trace {index} has wrong public doubling target")
            answer = entry["answer"]
            for field in ("z", "g", "anchor", "normalized", "root"):
                field_value = answer.get(field)
                if field_value is not None and (type(field_value) is not int or not 0 <= field_value < oracle.p):
                    errors.append(f"trace {index} answer field {field} is noncanonical")
            expected = expected_result(oracle, base, current, arm, z)
            fields = ("status", "bit", "reason", "z", "g", "anchor", "normalized", "root")
            for field in fields:
                if answer.get(field) != expected.get(field):
                    errors.append(f"trace {index} answer field {field} mismatch")
            if answer.get("status") != "BIT" or type(answer.get("bit")) is not int or answer.get("bit") not in (0, 1):
                errors.append(f"trace {index} does not provide a defined bit")
            else:
                value = (value << 1) | answer["bit"]
            if not count_map(entry["counters"]):
                errors.append(f"trace {index} counters malformed")
            else:
                evaluate_counts.update(entry["counters"])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"trace {index} malformed: {exc}")
        if index + 1 < length:
            current = oracle.add(current, current)
    denominator = 1 << length
    scalar = (oracle.r * value + denominator - 1) // denominator
    verified = len(trace) == length and 0 <= scalar < oracle.r and oracle.multiply(scalar, base) == target
    expected_status = "RECOVERED" if verified else "REJECTED_FINAL_VERIFICATION"
    for field, expected in (("status", expected_status), ("candidate_scalar", scalar),
                            ("scalar", scalar if verified else None),
                            ("reason", None if verified else "FINAL_VERIFICATION_FAILED")):
        if result.get(field) != expected:
            errors.append(f"fresh recovery {field} mismatch")
    if type(result.get("candidate_scalar")) is not int or (result.get("scalar") is not None and type(result["scalar"]) is not int):
        errors.append("fresh recovery scalar fields must be integers or the permitted null")
    if not count_map(result.get("evaluate_counts")) or dict(evaluate_counts) != result.get("evaluate_counts"):
        errors.append("fresh recovery evaluation counter sum mismatch")
    if not count_map(result.get("reduction_counts")):
        errors.append("fresh recovery reduction counters malformed")
    return {"pass": not errors and verified, "errors": errors, "predicate_evaluations": len(trace),
            "evaluate_counts": dict(evaluate_counts), "reduction_counts": result.get("reduction_counts", {}),
            "candidate_scalar": scalar, "public_final_check": verified}


def arm_key(arm: dict[str, Any]) -> tuple[Any, ...]:
    return arm["kind"], arm.get("alpha_integer"), arm.get("beta_integer")


def screen_plan(protocol: dict[str, Any] | None) -> dict[str, Any]:
    """Read the same public plan envelope independently of the compute module."""
    protocol = protocol or {}
    plan = protocol.get("extensions", {}).get("nongeneric_screen", protocol)
    return plan.get("screen_plan", plan)


def fixture_and_plan(protocol: dict[str, Any] | None) -> tuple[dict[str, Any], list[int], list[tuple[str, int | None, int | None]]]:
    protocol = screen_plan(protocol)
    fixture = protocol.get("fixture", DEFAULT_FIXTURE)
    scales = protocol.get("scales", list(range(1, 11)))
    alpha = protocol.get("alpha", DEFAULT_ALPHA)
    beta = protocol.get("beta", DEFAULT_BETA)
    controls = protocol.get("controls", DEFAULT_CONTROLS)
    arms = [("candidate", a, b) for a in alpha for b in beta]
    invalid = controls.get("invalid_anchor")
    if invalid:
        arms.append(("invalid_anchor", invalid["alpha"], invalid["beta"]))
    fiber = controls.get("fiber")
    if fiber:
        arms.extend(("fiber", a, fiber["beta"]) for a in fiber["alpha"])
    if controls.get("wrong_root"):
        arms.append(("wrong_root", None, None))
    aa = controls.get("aa_replay")
    if aa:
        arms.append(("aa_replay", aa["alpha"], aa["beta"]))
    return fixture, scales, arms


def _model_key(model: dict[str, int]) -> tuple[int, ...]:
    return tuple(model[k] for k in ("p", "a", "b", "r"))


def _record_group(record: dict[str, Any]) -> tuple[Any, ...]:
    return record["scale_u"], _model_key(record["model"]), tuple(record["base"]), arm_key(record["arm"])


def verify_records(records: Iterable[dict[str, Any]], protocol: dict[str, Any] | None = None, require_complete: bool = False, *, protocol_sha256: str | None = None, recovery_records: Iterable[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Validate arithmetic/integrity separately from fixed-template outcomes.

    With require_complete=False this is a software-test helper, not a scientific
    screen result.  Complete CLI validation derives the exact expected case set
    from the protocol and rejects missing, duplicate and unexpected cases.
    """
    records = list(records)
    plan = screen_plan(protocol)
    errors: list[dict[str, Any]] = []
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    ids, case_keys = set(), set()
    fingerprints, protocol_hashes = set(), set()
    fixture, scales, planned_arms = fixture_and_plan(protocol)
    if require_complete:
        if fixture != DEFAULT_FIXTURE or scales != list(range(1, 11)):
            errors.append({"error": "complete check requires the exact mandatory F11 fixture and all ten ordered scaling units"})
        candidate_plan = [arm for arm in planned_arms if arm[0] == "candidate"]
        if candidate_plan != [("candidate", a, b) for a in DEFAULT_ALPHA for b in DEFAULT_BETA]:
            errors.append({"error": "complete check requires the exact forty fixed integer templates"})
        if set(planned_arms) != set(fixture_and_plan(None)[2]):
            errors.append({"error": "complete check requires every fixed control arm"})
    fixture_oracle = OracleGroup(fixture)
    seed = point(fixture["seed_base"], fixture["p"])
    seed_orbit = fixture_oracle.orbit(seed)
    expected_groups: set[tuple[Any, ...]] = set()
    for u in scales:
        model = {"p": fixture["p"], "a": fixture["a"] * pow(u, 4, fixture["p"]) % fixture["p"], "b": fixture["b"] * pow(u, 6, fixture["p"]) % fixture["p"], "r": fixture["r"]}
        for base in seed_orbit[1:]:
            assert base is not None
            scaled = (base[0] * u**2 % fixture["p"], base[1] * u**3 % fixture["p"])
            for arm in planned_arms:
                expected_groups.add((u, _model_key(model), scaled, arm))

    for index, rec in enumerate(records):
        try:
            if rec.get("schema") != "nongeneric.case/v1":
                raise ValueError("record schema must be nongeneric.case/v1")
            p = rec["model"]["p"]
            base, target = point(rec["base"], p), point(rec["target"], p)
            if base is None:
                raise ValueError("identity base")
            if rec["case_id"] in ids:
                raise ValueError("duplicate case_id")
            ids.add(rec["case_id"])
            if not isinstance(rec.get("group_id"), str) or not rec["group_id"]:
                raise ValueError("missing group_id")
            for field in ("source_fingerprint", "protocol_sha256"):
                if not isinstance(rec.get(field), str) or not HEX64.fullmatch(rec[field]):
                    raise ValueError(f"invalid {field}")
            fingerprints.add(rec["source_fingerprint"])
            protocol_hashes.add(rec["protocol_sha256"])
            arm = rec["arm"]
            if arm_key(arm) not in planned_arms:
                raise ValueError("unplanned arm")
            expected_arm_id = "wrong_root:anchored_power_root" if arm["kind"] == "wrong_root" else f"{arm['kind']}:a{arm['alpha_integer']}:b{arm['beta_integer']}"
            if arm.get("id") != expected_arm_id:
                raise ValueError("noncanonical arm id")
            if arm["kind"] == "aa_replay" and arm.get("reference_id") != "candidate:a0:b1":
                raise ValueError("A/A reference id changed")
            if arm["kind"] != "wrong_root":
                if any(type(arm.get(k)) is not int for k in ("alpha_integer", "beta_integer", "alpha", "beta")):
                    raise ValueError("integer/reduced arm coefficients missing")
                if arm["alpha"] != arm["alpha_integer"] % p or arm["beta"] != arm["beta_integer"] % p:
                    raise ValueError("coefficient reduction mismatch")
            elif any(arm.get(k) is not None for k in ("alpha_integer", "beta_integer", "alpha", "beta")):
                raise ValueError("wrong-root arm must not carry parameter coefficients")
            key = _record_group(rec)
            if key not in expected_groups:
                raise ValueError("model/base/scale/arm outside fixed fixture")
            case_key = (key, target)
            if case_key in case_keys:
                raise ValueError("duplicate group-target case")
            case_keys.add(case_key)
            result = rec["result"]
            if result["status"] not in ("BIT", "UNDEFINED"):
                raise ValueError("unrecognized result status")
            if result["status"] == "BIT" and (type(result.get("bit")) is not int or result["bit"] not in (0, 1)):
                raise ValueError("BIT requires an exact integer bit")
            if result["status"] == "UNDEFINED" and result.get("bit") is not None:
                raise ValueError("UNDEFINED must retain null bit")
            if result["status"] == "UNDEFINED" and not isinstance(result.get("reason"), str):
                raise ValueError("UNDEFINED must state its reason")
            if result["status"] == "BIT" and result.get("reason") is not None:
                raise ValueError("BIT must not carry an undefined reason")
            for field in ("z", "g", "anchor", "normalized", "root"):
                value = result.get(field)
                if value is not None and (type(value) is not int or not 0 <= value < p):
                    raise ValueError(f"{field} must be null or a canonical field integer")
            for phase in ("setup", "evaluate"):
                counts = rec["counters"][phase]
                if not isinstance(counts, dict) or any(type(v) is not int or v < 0 for v in counts.values()):
                    raise ValueError("operation counters must be nonnegative integer maps")
            if "setup_charged" in rec:
                if type(rec["setup_charged"]) is not bool or rec["setup_charged"] != (target is None):
                    raise ValueError("setup_charged must be true exactly on the identity row")
            groups[key].append(rec)
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append({"record_index": index, "error": str(exc)})

    if len(fingerprints) > 1:
        errors.append({"error": "source fingerprint changed within stream"})
    if len(protocol_hashes) > 1:
        errors.append({"error": "protocol hash changed within stream"})
    if protocol_sha256 is not None and protocol_hashes != {protocol_sha256}:
        errors.append({"error": "records do not bind the supplied exact protocol bytes"})
    expected_fingerprint = plan.get("source_manifest_sha256") or plan.get("source_fingerprint")
    if expected_fingerprint is not None and fingerprints != {expected_fingerprint}:
        errors.append({"error": "source fingerprint does not match protocol"})

    oracle_cache: dict[tuple[Any, ...], tuple[OracleGroup, list[Point], dict[Point, int]]] = {}
    arithmetic_counts: Counter[str] = Counter()
    oracle_counts: Counter[str] = Counter(fixture_oracle.counts)
    recovery_counts: Counter[str] = Counter()
    group_reports = []
    record_lookup: dict[tuple[Any, ...], dict[Point, dict[str, Any]]] = {}
    reference_orbits: dict[tuple[Any, ...], dict[Point, int]] = {}
    reindex_checked = 0
    source_counter_totals: dict[str, Counter[str]] = {"evaluate": Counter(), "setup_once_per_group": Counter()}
    for key, rows in sorted(groups.items(), key=lambda item: repr(item[0])):
        first = rows[0]
        model, base = first["model"], point(first["base"], first["model"]["p"])
        oracle_key = _model_key(model), base
        if oracle_key not in oracle_cache:
            oracle = OracleGroup(model)
            orbit = oracle.orbit(base)
            z = {target: oracle.primitive(target, orbit) for target in orbit}
            # Full cocycle and oddness checks on the independent primitive.
            for left in orbit:
                if z[oracle.neg(left)] != -z[left] % oracle.p:
                    errors.append({"error": "independent primitive oddness failure", "model": model, "target": encoded(left)})
                for right in orbit:
                    expected = (z[left] + z[right] + oracle.slope(left, right)) % oracle.p
                    if z[oracle.add(left, right)] != expected:
                        errors.append({"error": "independent primitive cocycle failure", "model": model, "left": encoded(left), "right": encoded(right)})
            oracle_counts.update(oracle.counts)
            oracle.counts.clear()
            oracle_cache[oracle_key] = oracle, orbit, z
        oracle, orbit, z = oracle_cache[oracle_key]
        by_target = {point(rec["target"], oracle.p): rec for rec in rows}
        record_lookup[key] = by_target
        if len({row["group_id"] for row in rows}) != 1:
            errors.append({"group": repr(key), "error": "group_id changed within group"})
        if len({json.dumps(row["arm"], sort_keys=True) for row in rows}) != 1:
            errors.append({"group": repr(key), "error": "arm metadata changed within group"})
        if len({json.dumps(row["counters"]["setup"], sort_keys=True) for row in rows}) != 1:
            errors.append({"group": repr(key), "error": "setup counters changed within group"})
        charged_rows = [row for row in rows if "setup_charged" in row]
        if charged_rows and len(charged_rows) != len(rows):
            errors.append({"group": repr(key), "error": "setup_charged field coverage changed within group"})
        if len(rows) == fixture["r"] and charged_rows and sum(row["setup_charged"] for row in charged_rows) != 1:
            errors.append({"group": repr(key), "error": "complete group must charge setup exactly once"})
        source_counter_totals["setup_once_per_group"].update(first["counters"]["setup"])
        reference_key = first["scale_u"], _model_key(model)
        if reference_key not in reference_orbits:
            u = first["scale_u"]
            assert seed is not None
            reference_base = (seed[0] * u**2 % oracle.p, seed[1] * u**3 % oracle.p)
            reference_orbits[reference_key] = {t: i for i, t in enumerate(oracle.orbit(reference_base))}
            oracle_counts.update(oracle.counts)
            oracle.counts.clear()
        reference_indices = reference_orbits[reference_key]
        base_index = reference_indices[base]
        inverse_index = pow(base_index, -1, oracle.r)
        bits: dict[Point, int | None] = {}
        for target, rec in by_target.items():
            if target not in z:
                errors.append({"case_id": rec["case_id"], "error": "target outside subgroup"})
                continue
            reindex_checked += 1
            from_reference = truth_half(reference_indices[target] * inverse_index % oracle.r, oracle.r)
            from_orbit = truth_half(orbit.index(target), oracle.r)
            if from_reference != from_orbit:
                errors.append({"case_id": rec["case_id"], "error": "independent generator reindex truth mismatch"})
            expected = expected_result(oracle, base, target, rec["arm"], z)
            result = rec["result"]
            for field in ("status", "bit", "reason"):
                if result.get(field) != expected.get(field):
                    errors.append({"case_id": rec["case_id"], "field": field, "expected": expected.get(field), "observed": result.get(field)})
            fields = ("z", "g", "anchor", "normalized", "root") if rec["arm"]["kind"] == "wrong_root" else ("z", "g", "anchor", "normalized")
            for field in fields:
                if result.get(field) != expected.get(field):
                    errors.append({"case_id": rec["case_id"], "field": field, "expected": expected.get(field), "observed": result.get(field)})
            if result["status"] == "BIT":
                bits[target] = result["bit"]
                if target is not None:
                    sigma = target[1] * (1 - 2 * result["bit"]) % oracle.p
                    if sigma**2 % oracle.p != (target[0]**3 + oracle.a * target[0] + oracle.b) % oracle.p:
                        errors.append({"case_id": rec["case_id"], "error": "root/sign identity failed"})
            else:
                bits[target] = None
            source_counter_totals["evaluate"].update(rec["counters"]["evaluate"])
        arithmetic_counts.update(oracle.counts)
        oracle.counts.clear()
        obligation = group_obligations(oracle, base, orbit, bits)
        recovery_counts.update(oracle.counts)
        oracle.counts.clear()
        group_reports.append({"group_id": first["group_id"], "scale_u": first["scale_u"], "model": model, "base": encoded(base), "arm": first["arm"], "retained_target_count": len(by_target), **obligation})

    missing_groups = expected_groups - set(groups)
    missing_cases = sum(fixture["r"] - len(rows) for rows in groups.values()) + len(missing_groups) * fixture["r"]
    if require_complete and missing_cases:
        errors.append({"error": "incomplete fixed case plan", "missing_groups": len(missing_groups), "missing_cases": missing_cases})

    # Exact A/A result and counted-work comparison, evaluated independently upstream.
    aa_checked, aa_mismatches = 0, []
    for key, rows in groups.items():
        if key[3][0] != "aa_replay":
            continue
        reference_key = (*key[:3], ("candidate", key[3][1], key[3][2]))
        reference = record_lookup.get(reference_key, {})
        for row in rows:
            target = point(row["target"], row["model"]["p"])
            if target not in reference:
                if require_complete:
                    aa_mismatches.append({"case_id": row["case_id"], "error": "A/A reference missing"})
                continue
            aa_checked += 1
            other = reference[target]
            if row["result"] != other["result"] or row["counters"] != other["counters"]:
                aa_mismatches.append({"case_id": row["case_id"], "reference_case_id": other["case_id"]})
    errors.extend({"error": "A/A mismatch", **entry} for entry in aa_mismatches)

    # Coordinate covariance compares public matching inputs, never scalar truth.
    covariance_checked, covariance_failures = 0, []
    p = fixture["p"]
    for key, targets in record_lookup.items():
        u, _, base, arm = key
        if u == 1:
            continue
        inverse_u = pow(u, -1, p)
        unscaled_base = (base[0] * inverse_u**2 % p, base[1] * inverse_u**3 % p)
        original_key = (1, _model_key(fixture), unscaled_base, arm)
        original = record_lookup.get(original_key, {})
        for target, row in targets.items():
            unscaled_target = None if target is None else (target[0] * inverse_u**2 % p, target[1] * inverse_u**3 % p)
            if unscaled_target not in original:
                if require_complete:
                    covariance_failures.append({"case_id": row["case_id"], "error": "unscaled reference missing"})
                continue
            other = original[unscaled_target]
            covariance_checked += 1
            a, b = row["result"], other["result"]
            if (a["status"], a.get("bit"), a.get("reason")) != (b["status"], b.get("bit"), b.get("reason")):
                covariance_failures.append({"case_id": row["case_id"], "reference_case_id": other["case_id"]})
            if arm[0] != "wrong_root":
                for field in ("z", "g", "anchor"):
                    if a.get(field) is not None and b.get(field) is not None and a[field] != u * b[field] % p:
                        covariance_failures.append({"case_id": row["case_id"], "field": field})
                if a.get("normalized") != b.get("normalized"):
                    covariance_failures.append({"case_id": row["case_id"], "field": "normalized"})
            elif a.get("root") is not None and b.get("root") is not None and a["root"] != u**3 * b["root"] % p:
                covariance_failures.append({"case_id": row["case_id"], "field": "root"})
    errors.extend({"error": "coordinate covariance failure", **entry} for entry in covariance_failures)

    # Mandatory exact known-false controls. These assert instrument behavior;
    # they do not turn a scientific candidate failure into an integrity error.
    negative_controls = []
    if fixture == DEFAULT_FIXTURE:
        original_model = _model_key(fixture)
        assert seed is not None
        wrong_key = (1, original_model, seed, ("wrong_root", None, None))
        wrong_row = record_lookup.get(wrong_key, {}).get((8, 3))
        if wrong_row is not None:
            passed = wrong_row["result"].get("bit") == 1 and wrong_row["result"].get("root") == 8
            negative_controls.append({"control": "anchored_wrong_root_at_three_seedP", "pass": passed, "case_id": wrong_row["case_id"]})
        elif require_complete:
            negative_controls.append({"control": "anchored_wrong_root_at_three_seedP", "pass": False, "error": "required control point absent"})
        for alpha in DEFAULT_ALPHA:
            fiber_key = (1, original_model, seed, ("fiber", alpha, 0))
            rows = record_lookup.get(fiber_key, {})
            pair = [rows.get((3, 6)), rows.get((7, 9))]
            if all(row is not None for row in pair):
                answers = [row["result"] for row in pair]
                passed = any(answer["status"] == "UNDEFINED" for answer in answers) or answers[0]["bit"] != answers[1]["bit"]
                negative_controls.append({"control": "fiber_collision_at_five_six_seedP", "alpha_integer": alpha, "pass": passed, "case_ids": [row["case_id"] for row in pair]})
            elif require_complete:
                negative_controls.append({"control": "fiber_collision_at_five_six_seedP", "alpha_integer": alpha, "pass": False, "error": "required control points absent"})
    errors.extend({"error": "known-false control did not reproduce", **entry} for entry in negative_controls if not entry["pass"])

    # Explicit validator-only positive controls, reported separately from candidate rows.
    positive_reports = []
    positive_counts: Counter[str] = Counter()
    public_base_keys = {(key[0], key[1], key[2]) for key in groups}
    for scale_u, model_key, base in sorted(public_base_keys, key=repr):
        _, orbit, _ = oracle_cache[(model_key, base)]
        control = OracleGroup(dict(zip(("p", "a", "b", "r"), model_key)))
        control_orbit = control.orbit(base)
        bits = {target: truth_half(i, control.r) for i, target in enumerate(control_orbit)}
        report = group_obligations(control, base, control_orbit, bits)
        positive_reports.append({"scale_u": scale_u, "model": control.model, "base": encoded(base), "target_count": len(orbit), "ordering_pass": report["ordering_pass"], "retained_bit_reduction_pass": report["retained_bit_reduction_pass"], "retained_bit_reduction_verified_count": report["retained_bit_reduction_verified_count"], "predicate_evaluations": 0, "oracle_table_verifier_only": True})
        positive_counts.update(control.counts)
    if any(not x["ordering_pass"] or not x["retained_bit_reduction_pass"] for x in positive_reports):
        errors.append({"error": "validator-only truth-half positive control failed"})

    # A separate stream records actual fresh preparations and predicate calls.
    # Retained case bits decide only the public gate and are never substituted
    # for the trace below.  This verifier checks the supplied actual traces.
    supplied_recoveries = recovery_records is not None
    recovery_rows = list(recovery_records or [])
    recovery_lookup: dict[tuple[Any, ...], dict[str, Any]] = {}
    actual_recovery_reports = []
    actual_recovery_oracle_counts: Counter[str] = Counter()
    actual_source_counts = {phase: Counter() for phase in ("gate", "fresh_setup", "evaluate", "reduction")}
    group_reports_by_key = {_record_group(rows[0]): report for rows, report in zip((groups[key] for key in sorted(groups, key=repr)), group_reports)}
    for index, row in enumerate(recovery_rows):
        label = {"recovery_record_index": index, "group_id": row.get("group_id")}
        try:
            if row.get("schema") != "nongeneric.recovery-group/v1":
                raise ValueError("recovery schema must be nongeneric.recovery-group/v1")
            key = _record_group(row)
            if key not in groups:
                raise ValueError("recovery group has no corresponding retained public cases")
            if key in recovery_lookup:
                raise ValueError("duplicate recovery group")
            recovery_lookup[key] = row
            first = groups[key][0]
            for field in ("group_id", "model", "scale_u", "base", "arm", "source_fingerprint", "protocol_sha256"):
                if row.get(field) != first[field]:
                    raise ValueError(f"recovery group {field} does not bind its public case group")
            model, base = first["model"], point(first["base"], first["model"]["p"])
            oracle, orbit, z = oracle_cache[(_model_key(model), base)]
            retained = record_lookup[key]
            bits = {target: answer["result"]["bit"] if answer["result"]["status"] == "BIT" else None for target, answer in retained.items()}
            target_order = list(retained)
            expected_gate = public_gate(oracle, base, orbit, bits, target_order)
            gate = row["gate"]
            group_errors = []
            for field in ("pass", "not_attempted_reason", "two_pulse_residual", "target_order"):
                if gate.get(field) != expected_gate[field]:
                    group_errors.append(f"public gate {field} mismatch")
            if type(gate.get("pass")) is not bool or gate.get("scalar_truth_access") is not False:
                group_errors.append("public gate must be boolean and report no scalar-truth access")
            counters = row["counters"]
            for phase in ("gate", "fresh_setup", "evaluate", "reduction"):
                if not count_map(counters.get(phase)):
                    raise ValueError(f"recovery group {phase} counters malformed")
                actual_source_counts[phase].update(counters[phase])
            if gate.get("counters") != counters["gate"]:
                group_errors.append("gate counter copies disagree")
            if row.get("retained_bit_reads_in_recovery") != 0 or row.get("oracle_table_verifier_only") is not False:
                group_errors.append("actual recovery group must report zero retained-bit reads and no validator table")
            if any(type(row.get(field)) is not int or row.get(field) < 0 for field in ("retained_bit_reads_in_recovery", "predicate_evaluations", "fresh_preparations")):
                group_errors.append("actual recovery group call/read/preparation totals must be nonnegative integers")
            if row.get("fresh_preparations") != int(expected_gate["pass"]):
                group_errors.append("fresh preparation count mismatch")
            recoveries = row["recoveries"]
            if not isinstance(recoveries, list):
                raise ValueError("recoveries must be a list")
            checked_targets, verified_count, evaluations = set(), 0, 0
            evaluate_sum, reduction_sum = Counter(), Counter()
            trace_reports = []
            if not expected_gate["pass"]:
                if recoveries or row.get("predicate_evaluations") != 0:
                    group_errors.append("failed public gate must not launch recovery or predicates")
                if any(sum(counters[phase].values()) for phase in ("fresh_setup", "evaluate", "reduction")):
                    group_errors.append("failed public gate must charge no fresh recovery work")
            else:
                if counters["fresh_setup"] != first["counters"]["setup"]:
                    group_errors.append("fresh preparation counter vector differs from identical original setup")
                if len(recoveries) != len(orbit):
                    group_errors.append("passing gate requires every target recovery")
                for recovery_index, entry in enumerate(recoveries):
                    target = point(entry["target"], oracle.p)
                    if target not in retained or target in checked_targets:
                        group_errors.append("recovery target missing from group or duplicated")
                    checked_targets.add(target)
                    if recovery_index >= len(target_order) or target != target_order[recovery_index]:
                        group_errors.append("recovery target order differs from public gate input order")
                    checked = validate_fresh_recovery(oracle, base, target, first["arm"], z, entry["result"])
                    trace_reports.append({"target": encoded(target), **checked})
                    group_errors.extend(f"target {encoded(target)}: {message}" for message in checked["errors"])
                    verified_count += int(checked["pass"])
                    evaluations += checked["predicate_evaluations"]
                    evaluate_sum.update(checked["evaluate_counts"])
                    if count_map(checked["reduction_counts"]):
                        reduction_sum.update(checked["reduction_counts"])
                if checked_targets != set(orbit):
                    group_errors.append("passing gate did not recover the complete subgroup")
                if dict(evaluate_sum) != counters["evaluate"] or dict(reduction_sum) != counters["reduction"]:
                    group_errors.append("fresh group aggregate counters disagree with actual recovery traces")
                if row.get("predicate_evaluations") != evaluations or evaluations != len(orbit) * (oracle.r.bit_length() + 1):
                    group_errors.append("passing group requires thirteen times L fresh predicate evaluations")
            actual_recovery_oracle_counts.update(oracle.counts)
            oracle.counts.clear()
            actual_pass = bool(expected_gate["pass"] and not group_errors and verified_count == len(orbit))
            group_reports_by_key[key].update(actual_recovery_attempted=bool(expected_gate["pass"]),
                                             actual_recovery_verified_count=verified_count,
                                             actual_recovery_pass=actual_pass)
            actual_recovery_reports.append({"group_id": first["group_id"], "public_gate_pass": expected_gate["pass"],
                                            "not_attempted_reason": expected_gate["not_attempted_reason"],
                                            "actual_recovery_pass": actual_pass, "verified_target_count": verified_count,
                                            "predicate_evaluations": evaluations, "retained_bit_reads": 0,
                                            "errors": group_errors, "trace_reports": trace_reports})
            errors.extend({**label, "error": message} for message in group_errors)
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            errors.append({**label, "error": str(exc)})
    missing_recovery_groups = expected_groups - set(recovery_lookup)
    if require_complete and (not supplied_recoveries or missing_recovery_groups):
        errors.append({"error": "complete validation requires one recovery gate/trace record per planned group", "missing_recovery_groups": len(missing_recovery_groups)})
    recovery_aa_pairs = 0
    for key, row in recovery_lookup.items():
        if key[3][0] != "aa_replay":
            continue
        reference = recovery_lookup.get((*key[:3], ("candidate", key[3][1], key[3][2])))
        if reference is None:
            if require_complete:
                errors.append({"group_id": row["group_id"], "error": "recovery A/A reference missing"})
            continue
        recovery_aa_pairs += 1
        fields = ("gate", "recoveries", "counters", "predicate_evaluations", "retained_bit_reads_in_recovery", "fresh_preparations", "oracle_table_verifier_only")
        if any(row.get(field) != reference.get(field) for field in fields):
            errors.append({"group_id": row["group_id"], "error": "fresh recovery A/A mismatch"})

    by_arm: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for group in group_reports:
        by_arm[arm_key(group["arm"])].append(group)
    arm_reports = []
    expected_per_arm = len(scales) * (fixture["r"] - 1)
    for arm in planned_arms:
        actual = by_arm.get(arm, [])
        complete = len(actual) == expected_per_arm and all(x["retained_target_count"] == fixture["r"] for x in actual)
        arm_reports.append({"kind": arm[0], "alpha_integer": arm[1], "beta_integer": arm[2], "complete": complete, "group_count": len(actual), "ordering_pass_groups": sum(x["ordering_pass"] for x in actual), "actual_recovery_pass_groups": sum(x["actual_recovery_pass"] for x in actual), "undefined_count": sum(x["undefined_count"] for x in actual), "truth_mismatch_count": sum(x["truth_mismatch_count"] for x in actual), "finite_template_pass": not errors and complete and all(x["ordering_pass"] and x["actual_recovery_pass"] for x in actual)})
    aliases: dict[tuple[Any, ...], list[tuple[Any, ...]]] = defaultdict(list)
    for arm in planned_arms:
        if arm[0] == "candidate":
            aliases[(arm[1] % p, arm[2] % p)].append(arm)
    return {
        "schema": "classical.ecdlp.nongeneric-screen-verification/v1",
        "scope": "complete_fixed_fixture" if require_complete else "software_subset_not_scientific_screen",
        "independent_candidate_imports": False,
        "scalar_truth_scope": "validator-only O(r) enumeration; never candidate input",
        "primitive_oracle": "-sum_{T in G}lambda(R,T)/r, O(r) per query",
        "source_fingerprint": sorted(fingerprints),
        "protocol_sha256": sorted(protocol_hashes),
        "record_count": len(records),
        "accepted_record_count": sum(len(x) for x in groups.values()),
        "expected_record_count": len(expected_groups) * fixture["r"],
        "missing_case_count": missing_cases,
        "missing_group_count": len(missing_groups),
        "integrity_pass": not errors,
        "errors": errors,
        "candidate_arm_count": sum(arm[0] == "candidate" for arm in planned_arms),
        "candidate_modular_aliases": [values for values in aliases.values() if len(values) > 1],
        "aa_pairs_checked": aa_checked,
        "coordinate_pairs_checked": covariance_checked,
        "generator_reindex_truth_checked": reindex_checked,
        "validator_counts": {"oracle_and_laws": dict(oracle_counts), "arithmetic_record_checks": dict(arithmetic_counts), "retained_bit_reduction_and_obligations": dict(recovery_counts), "truth_half_positive_control": dict(positive_counts), "actual_fresh_recovery_trace_checks": dict(actual_recovery_oracle_counts)},
        "candidate_reported_counts": {k: dict(v) for k, v in source_counter_totals.items()},
        "candidate_counter_validation": "Nonnegative integer shape, stable setup per group and exact A/A equality; no independent candidate counter replay is claimed.",
        "setup_charge_validation": "If setup_charged is present, it is a boolean true exactly at O and appears on every retained row in that group; complete groups charge setup once.",
        "validator_positive_controls": positive_reports,
        "negative_controls": negative_controls,
        "actual_recovery_stream_supplied": supplied_recoveries,
        "actual_recovery_record_count": len(recovery_rows),
        "missing_recovery_group_count": len(missing_recovery_groups),
        "actual_recovery_aa_pairs_checked": recovery_aa_pairs,
        "actual_recovery_predicate_evaluations": sum(row["predicate_evaluations"] for row in actual_recovery_reports),
        "actual_recovery_verified_target_count": sum(row["verified_target_count"] for row in actual_recovery_reports),
        "actual_recovery_reported_counts": {phase: dict(counts) for phase, counts in actual_source_counts.items()},
        "actual_recovery_reports": actual_recovery_reports,
        "retained_bit_reduction_scope": "Verifier-only table-read consistency check with zero constructor evaluations. Actual solver calls are assessed only from the separate recovery trace stream.",
        "arm_reports": arm_reports,
        "group_reports": group_reports,
        "inference_limit": "Finite correctness only. No global ordering, novelty, complexity improvement or closure claim follows.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("records", type=Path)
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recoveries", type=Path, help="Required for complete validation: actual fresh-call recovery.jsonl stream")
    parser.add_argument("--software-subset", action="store_true", help="Explicitly not a scientific screen report")
    args = parser.parse_args()
    if not args.software_subset and args.recoveries is None:
        parser.error("complete validation requires --recoveries")
    raw_protocol = args.protocol.read_bytes()
    protocol = json.loads(raw_protocol)
    with args.records.open() as source:
        records = [json.loads(line) for line in source if line.strip()]
    recovery_records = None
    if args.recoveries:
        with args.recoveries.open() as source:
            recovery_records = [json.loads(line) for line in source if line.strip()]
    report = verify_records(records, protocol, require_complete=not args.software_subset,
                            protocol_sha256=hashlib.sha256(raw_protocol).hexdigest(), recovery_records=recovery_records)
    with args.output.open("x") as out:
        json.dump(report, out, sort_keys=True, indent=2)
        out.write("\n")
    print(json.dumps({"integrity_pass": report["integrity_pass"], "record_count": report["record_count"], "expected_record_count": report["expected_record_count"], "scope": report["scope"]}, sort_keys=True))
    return 0 if report["integrity_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
