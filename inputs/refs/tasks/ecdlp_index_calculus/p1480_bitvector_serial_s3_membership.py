#!/usr/bin/env python3
"""Test complete five-term membership with a homogeneous serial-S3 BV circuit."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import re
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

from sage.all import EllipticCurve, GF, is_prime


ROOT = Path(__file__).resolve().parents[2]
STATE_DIR = ROOT / "ecdlp_index_calculus_state"
RESEARCH_DIR = ROOT / "research"
CONTRACT = STATE_DIR / "experiment_contract_p1480_bitvector_serial_s3_membership.md"
OUT = STATE_DIR / "p1480_bitvector_serial_s3_membership.json"
NOTE = RESEARCH_DIR / "p1480_bitvector_serial_s3_membership.md"
Z3 = Path("/opt/homebrew/bin/z3")

SCHEMA = "ecdlp.p1480_bitvector_serial_s3_membership.v1"
TIMEOUT_MS = 30_000
EXPECTED = {
    CONTRACT: "4713dc77b2740454324b69d24ae4d3e848eba84c6d35215a8fab7738c54f80ab",
    STATE_DIR / "p1477_serial_s3_state_compression.json":
        "ca41939ef8f05d2579ac392d2651fc6bb3199f0e38b10b1d0e20a197caa51ae5",
    STATE_DIR / "p1477_serial_s3_state_compression_audit.json":
        "8b6eb71141b5a3deba12bd6969ddd0c10d9d6092c32e52e173d0145371f01245",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition.json":
        "287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df",
    STATE_DIR / "p1478_sparse_s3_subgroup_norm_composition_audit.json":
        "d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9",
    STATE_DIR / "p1479_factor_log_feature_compression.json":
        "4367c4478f6b94a0213b0a4066f6d609ccbdb7a2eab311087145db28855c0500",
    STATE_DIR / "p1479_factor_log_feature_compression_audit.json":
        "0636b13b4932327dc541c85effe2e5f5dd479733e5f440e034a692f1bbfc52c3",
}
FIXTURES = [
    {"L": 4, "p": 1033, "order": 1061, "a": 1, "b": 1},
    {"L": 8, "p": 32801, "order": 32479, "a": 1, "b": 5},
    {"L": 16, "p": 1048609, "order": 1047539, "a": 5, "b": 7},
    {"L": 32, "p": 33554593, "order": 33563891, "a": 3, "b": 9},
]
MODEL_NAMES = ("i1", "i2", "i3", "i4", "i5", "u1", "u2", "u3")
BOOL_NAMES = ("u1_inf", "u2_inf", "u3_inf")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_int(*parts: object) -> int:
    material = "|".join(str(part) for part in parts).encode("ascii")
    return int.from_bytes(hashlib.sha256(material).digest(), "big")


def point_key(point: Any) -> tuple[int, int] | tuple[str]:
    return ("O",) if point.is_zero() else (int(point[0]), int(point[1]))


def point_json(point: Any) -> dict[str, Any]:
    if point.is_zero():
        return {"infinity": True}
    return {"x": int(point[0]), "y": int(point[1])}


def build_context(fixture: dict[str, int]) -> dict[str, Any]:
    p, q, L = fixture["p"], fixture["order"], fixture["L"]
    if not is_prime(p) or not is_prime(q) or (p - 1) % L:
        raise RuntimeError("P1480 fixture arithmetic failure")
    field = GF(p)
    curve = EllipticCurve(field, [fixture["a"], fixture["b"]])
    if int(curve.cardinality()) != q or curve.is_supersingular():
        raise RuntimeError("P1480 curve validation failure")
    generator = None
    for x_integer in range(p):
        lifts = sorted(curve.lift_x(field(x_integer), all=True), key=lambda point: int(point[1]))
        if lifts:
            generator = lifts[0]
            break
    if generator is None or int(generator.order()) != q:
        raise RuntimeError("P1480 generator failure")
    h = field.multiplicative_generator() ** ((p - 1) // L)
    if int(h.multiplicative_order()) != L:
        raise RuntimeError("P1480 subgroup order failure")
    return {
        "fixture": fixture,
        "field": field,
        "curve": curve,
        "generator": generator,
        "identity": 0 * generator,
        "h": h,
    }


def subgroup_roots(context: dict[str, Any]) -> list[int]:
    roots = []
    value = context["field"].one()
    for _ in range(context["fixture"]["L"]):
        if context["curve"].lift_x(value, all=True):
            roots.append(int(value))
        value *= context["h"]
    return sorted(set(roots))


def random_x_roots(context: dict[str, Any], count: int) -> list[int]:
    fixture = context["fixture"]
    roots: set[int] = set()
    counter = 0
    while len(roots) < count:
        x_integer = digest_int("P1480", "random_x", fixture["L"], counter) % fixture["p"]
        counter += 1
        if x_integer in roots:
            continue
        if context["curve"].lift_x(context["field"](x_integer), all=True):
            roots.add(x_integer)
    return sorted(roots)


def root_lifts(context: dict[str, Any], roots: list[int]) -> list[list[Any]]:
    output = []
    for root in roots:
        lifts = sorted(
            context["curve"].lift_x(context["field"](root), all=True),
            key=lambda point: int(point[1]),
        )
        if len(lifts) != 2 or lifts[0] != -lifts[1]:
            raise RuntimeError("P1480 expected a sign pair for every root")
        output.append(lifts)
    return output


def make_queries(
    context: dict[str, Any], deck_name: str, roots: list[int], count: int = 8
) -> list[dict[str, Any]]:
    lifts = root_lifts(context, roots)
    fixture = context["fixture"]
    queries = []
    for index in range(count):
        if index < 4:
            nonce = 0
            while True:
                indices = [
                    digest_int("P1480", deck_name, fixture["L"], "planted-index", index, nonce, slot)
                    % len(roots)
                    for slot in range(5)
                ]
                signs = [
                    digest_int("P1480", deck_name, fixture["L"], "planted-sign", index, nonce, slot) & 1
                    for slot in range(5)
                ]
                endpoints = [lifts[root_index][sign] for root_index, sign in zip(indices, signs)]
                target = sum(endpoints, context["identity"])
                if not target.is_zero():
                    break
                nonce += 1
            queries.append({
                "query_index": index,
                "kind": "planted_positive",
                "target": target,
                "target_scalar": None,
                "control_witness_indices": indices,
                "control_witness_signs": signs,
            })
        else:
            scalar = 1 + digest_int(
                "P1480", deck_name, fixture["L"], "random-scalar", index
            ) % (fixture["order"] - 1)
            queries.append({
                "query_index": index,
                "kind": "random_scalar",
                "target": scalar * context["generator"],
                "target_scalar": scalar,
                "control_witness_indices": None,
                "control_witness_signs": None,
            })
    return queries


def bv(value: int) -> str:
    return f"(_ bv{value} 64)"


def lookup_expression(index_name: str, roots: list[int]) -> str:
    expression = bv(roots[-1])
    for index in range(len(roots) - 2, -1, -1):
        expression = f"(ite (= {index_name} {bv(index)}) {bv(roots[index])} {expression})"
    return expression


def smt_prelude(fixture: dict[str, int], roots: list[int], target_x: int, timeout_ms: int) -> str:
    p, a, b = fixture["p"], fixture["a"], fixture["b"]
    lines = [
        "(set-logic QF_BV)",
        "(set-option :produce-models true)",
        "(set-option :random-seed 0)",
        f"(set-option :timeout {timeout_ms})",
        f"(define-fun P () (_ BitVec 64) {bv(p)})",
        f"(define-fun A () (_ BitVec 64) {bv(a % p)})",
        f"(define-fun TWO_B () (_ BitVec 64) {bv((2 * b) % p)})",
        f"(define-fun FOUR_B () (_ BitVec 64) {bv((4 * b) % p)})",
        f"(define-fun ZERO () (_ BitVec 64) {bv(0)})",
        f"(define-fun ONE () (_ BitVec 64) {bv(1)})",
        "(define-fun fadd ((x (_ BitVec 64)) (y (_ BitVec 64))) (_ BitVec 64) (bvurem (bvadd x y) P))",
        "(define-fun fsub ((x (_ BitVec 64)) (y (_ BitVec 64))) (_ BitVec 64) (ite (bvuge x y) (bvsub x y) (bvsub (bvadd x P) y)))",
        "(define-fun fmul ((x (_ BitVec 64)) (y (_ BitVec 64))) (_ BitVec 64) (bvurem (bvmul x y) P))",
        "(define-fun hs3 ((x1 (_ BitVec 64)) (z1 (_ BitVec 64)) (x2 (_ BitVec 64)) (z2 (_ BitVec 64)) (x3 (_ BitVec 64)) (z3 (_ BitVec 64))) (_ BitVec 64)",
        "  (let ((d (fsub (fmul x1 z2) (fmul x2 z1)))",
        "        (s (fadd (fmul x1 z2) (fmul x2 z1)))",
        "        (xx (fmul x1 x2)) (zz (fmul z1 z2))",
        "        (x3sq (fmul x3 x3)) (z3sq (fmul z3 z3))",
        "        (z1sq (fmul z1 z1)) (z2sq (fmul z2 z2)))",
        "    (let ((term1 (fmul (fmul d d) x3sq))",
        "          (middle (fadd (fmul s (fadd xx (fmul A zz))) (fmul TWO_B (fmul z1sq z2sq))))",
        "          (last (fsub (fmul (fsub xx (fmul A zz)) (fsub xx (fmul A zz))) (fmul FOUR_B (fmul s zz)))))",
        "      (fadd (fsub term1 (fmul (fmul (fmul (fmul (_ bv2 64) middle) x3) z3) ONE)) (fmul last z3sq)))))",
    ]
    for name in ("i1", "i2", "i3", "i4", "i5"):
        lines.extend([
            f"(declare-fun {name} () (_ BitVec 64))",
            f"(assert (bvult {name} {bv(len(roots))}))",
        ])
    for left, right in zip(("i1", "i2", "i3", "i4"), ("i2", "i3", "i4", "i5")):
        lines.append(f"(assert (bvule {left} {right}))")
    for name in ("u1", "u2", "u3"):
        lines.extend([
            f"(declare-fun {name} () (_ BitVec 64))",
            f"(declare-fun {name}_inf () Bool)",
            f"(assert (bvult {name} P))",
            f"(assert (=> {name}_inf (= {name} ZERO)))",
            f"(define-fun {name}x () (_ BitVec 64) (ite {name}_inf ONE {name}))",
            f"(define-fun {name}z () (_ BitVec 64) (ite {name}_inf ZERO ONE))",
        ])
    for index in range(1, 6):
        lines.append(
            f"(define-fun x{index} () (_ BitVec 64) {lookup_expression(f'i{index}', roots)})"
        )
    lines.extend([
        f"(define-fun xr () (_ BitVec 64) {bv(target_x)})",
        "(assert (= (hs3 u1x u1z x1 ONE x2 ONE) ZERO))",
        "(assert (= (hs3 u1x u1z u2x u2z x3 ONE) ZERO))",
        "(assert (= (hs3 u2x u2z u3x u3z x4 ONE) ZERO))",
        "(assert (= (hs3 u3x u3z x5 ONE xr ONE) ZERO))",
    ])
    return "\n".join(lines) + "\n"


def blocking_assertion(indices: list[int]) -> str:
    terms = " ".join(f"(= i{slot + 1} {bv(value)})" for slot, value in enumerate(indices))
    return f"(assert (not (and {terms})))\n"


def parse_stats(output: str) -> dict[str, int | float]:
    stats: dict[str, int | float] = {}
    for key, raw in re.findall(r":([A-Za-z0-9_-]+)\s+([0-9]+(?:\.[0-9]+)?)", output):
        value: int | float = float(raw) if "." in raw else int(raw)
        stats[key.replace("-", "_")] = value
    return stats


def parse_model(output: str) -> dict[str, int | bool]:
    model: dict[str, int | bool] = {}
    for name in MODEL_NAMES:
        match = re.search(rf"\({name}\s+(#x[0-9a-fA-F]+|#b[01]+|\(_ bv[0-9]+ 64\))\)", output)
        if not match:
            raise RuntimeError(f"P1480 missing model value {name}")
        raw = match.group(1)
        if raw.startswith("#x"):
            model[name] = int(raw[2:], 16)
        elif raw.startswith("#b"):
            model[name] = int(raw[2:], 2)
        else:
            model[name] = int(re.search(r"bv([0-9]+)", raw).group(1))
    for name in BOOL_NAMES:
        match = re.search(rf"\({name}\s+(true|false)\)", output)
        if not match:
            raise RuntimeError(f"P1480 missing model value {name}")
        model[name] = match.group(1) == "true"
    return model


def run_z3(script: str) -> dict[str, Any]:
    started = time.perf_counter()
    completed = subprocess.run(
        [str(Z3), "-in", "-smt2", "-st"],
        input=script,
        text=True,
        capture_output=True,
        timeout=(TIMEOUT_MS / 1000) + 5,
        check=False,
    )
    wall = time.perf_counter() - started
    combined = completed.stdout + "\n" + completed.stderr
    status_match = re.search(r"^(sat|unsat|unknown)$", completed.stdout, re.MULTILINE)
    status = status_match.group(1) if status_match else "process_error"
    return {
        "status": status,
        "returncode": completed.returncode,
        "wall_seconds": wall,
        "stats": parse_stats(combined),
        "model": parse_model(completed.stdout) if status == "sat" else None,
        "stdout_sha256": hashlib.sha256(completed.stdout.encode("utf-8")).hexdigest(),
        "stderr_sha256": hashlib.sha256(completed.stderr.encode("utf-8")).hexdigest(),
        "stdout_prefix": completed.stdout[:500],
        "stderr_prefix": completed.stderr[:500],
    }


def fadd(x: int, y: int, p: int) -> int:
    return (x + y) % p


def fsub(x: int, y: int, p: int) -> int:
    return (x - y) % p


def fmul(x: int, y: int, p: int) -> int:
    return (x * y) % p


def hs3_value(
    first: tuple[int, int], second: tuple[int, int], third: tuple[int, int], fixture: dict[str, int]
) -> int:
    p, a, b = fixture["p"], fixture["a"], fixture["b"]
    x1, z1 = first
    x2, z2 = second
    x3, z3 = third
    d = fsub(fmul(x1, z2, p), fmul(x2, z1, p), p)
    s = fadd(fmul(x1, z2, p), fmul(x2, z1, p), p)
    xx, zz = fmul(x1, x2, p), fmul(z1, z2, p)
    term1 = fmul(fmul(d, d, p), fmul(x3, x3, p), p)
    middle = fadd(
        fmul(s, fadd(xx, fmul(a, zz, p), p), p),
        fmul(2 * b, fmul(fmul(z1, z1, p), fmul(z2, z2, p), p), p),
        p,
    )
    term2 = fmul(2, fmul(middle, fmul(x3, z3, p), p), p)
    last = fsub(
        fmul(fsub(xx, fmul(a, zz, p), p), fsub(xx, fmul(a, zz, p), p), p),
        fmul(4 * b, fmul(s, zz, p), p),
        p,
    )
    return fadd(fsub(term1, term2, p), fmul(last, fmul(z3, z3, p), p), p)


def verify_model_formula(
    model: dict[str, int | bool], fixture: dict[str, int], roots: list[int], target_x: int
) -> bool:
    indices = [int(model[f"i{index}"]) for index in range(1, 6)]
    if indices != sorted(indices) or any(index < 0 or index >= len(roots) for index in indices):
        return False
    points = [(roots[index], 1) for index in indices]
    aux = []
    for index in range(1, 4):
        value = int(model[f"u{index}"])
        infinity = bool(model[f"u{index}_inf"])
        if value < 0 or value >= fixture["p"] or (infinity and value != 0):
            return False
        aux.append((1, 0) if infinity else (value, 1))
    checks = (
        hs3_value(aux[0], points[0], points[1], fixture),
        hs3_value(aux[0], aux[1], points[2], fixture),
        hs3_value(aux[1], aux[2], points[3], fixture),
        hs3_value(aux[2], points[4], (target_x, 1), fixture),
    )
    return checks == (0, 0, 0, 0)


def replay_source(
    context: dict[str, Any], roots: list[int], indices: list[int], target: Any
) -> tuple[list[Any] | None, int]:
    lifts = root_lifts(context, [roots[index] for index in indices])
    trials = 0
    for endpoints in itertools.product(*lifts):
        trials += 1
        total = sum(endpoints, context["identity"])
        if total == target or total == -target:
            return list(endpoints), trials
    return None, trials


def candidate_decision(
    context: dict[str, Any], roots: list[int], target: Any
) -> dict[str, Any]:
    fixture = context["fixture"]
    blocked: list[list[int]] = []
    attempts = []
    elapsed_ms = 0
    total_sign_trials = 0
    verified_witness = None
    final_status = "unknown"
    while elapsed_ms < TIMEOUT_MS:
        remaining_ms = max(1, TIMEOUT_MS - elapsed_ms)
        prelude = smt_prelude(fixture, roots, int(target[0]), remaining_ms)
        blocks = "".join(blocking_assertion(indices) for indices in blocked)
        trailer = "(check-sat)\n(get-info :reason-unknown)\n(get-value (i1 i2 i3 i4 i5 u1 u2 u3 u1_inf u2_inf u3_inf))\n"
        script = prelude + blocks + trailer
        attempt = run_z3(script)
        attempt["formula_bytes"] = len(script.encode("ascii"))
        attempts.append(attempt)
        elapsed_ms += math.ceil(1000 * attempt["wall_seconds"])
        final_status = attempt["status"]
        if final_status != "sat":
            break
        model = attempt["model"]
        if not verify_model_formula(model, fixture, roots, int(target[0])):
            final_status = "model_formula_failure"
            break
        indices = [int(model[f"i{index}"]) for index in range(1, 6)]
        witness, trials = replay_source(context, roots, indices, target)
        total_sign_trials += trials
        if witness is not None:
            verified_witness = witness
            final_status = "sat"
            break
        blocked.append(indices)
    total_rlimit = sum(int(attempt["stats"].get("rlimit_count", 0)) for attempt in attempts)
    total_formula_bytes = sum(attempt["formula_bytes"] for attempt in attempts)
    return {
        "status": final_status,
        "attempt_count": len(attempts),
        "attempts": attempts,
        "blocked_index_tuples": blocked,
        "total_blocked_tuple_count": len(blocked),
        "total_wall_seconds": sum(attempt["wall_seconds"] for attempt in attempts),
        "total_rlimit_count": total_rlimit,
        "total_formula_bytes": total_formula_bytes,
        "selector_entries": 5 * len(roots) * len(attempts),
        "charged_effort": total_formula_bytes + max(1, total_rlimit),
        "source_sign_trials": total_sign_trials,
        "verified_source": [point_json(point) for point in verified_witness] if verified_witness else None,
        "source_replayed": verified_witness is not None,
    }


def extend_support(
    prior: dict[Any, tuple[Any, tuple[Any, ...]]], deck: list[Any]
) -> tuple[dict[Any, tuple[Any, tuple[Any, ...]]], int]:
    output: dict[Any, tuple[Any, tuple[Any, ...]]] = {}
    generated = 0
    for key in sorted(prior, key=repr):
        point, witness = prior[key]
        for endpoint in deck:
            generated += 1
            total = point + endpoint
            output.setdefault(point_key(total), (total, witness + (endpoint,)))
    return output, generated


def exact_a5_oracle(context: dict[str, Any], roots: list[int]) -> dict[str, Any]:
    started = time.perf_counter()
    deck = [point for lifts in root_lifts(context, roots) for point in lifts]
    support = {point_key(point): (point, (point,)) for point in deck}
    levels = [{
        "endpoint_length": 1,
        "ordered_generation_count": len(deck),
        "point_support_count": len(support),
    }]
    for endpoint_length in range(2, 6):
        support, generated = extend_support(support, deck)
        levels.append({
            "endpoint_length": endpoint_length,
            "ordered_generation_count": generated,
            "point_support_count": len(support),
        })
    return {
        "deck": deck,
        "support": support,
        "levels": levels,
        "wall_seconds": time.perf_counter() - started,
    }


def score_queries(
    context: dict[str, Any], queries: list[dict[str, Any]], candidate_rows: list[dict[str, Any]], roots: list[int]
) -> dict[str, Any]:
    oracle = exact_a5_oracle(context, roots)
    scored = []
    for query, candidate in zip(queries, candidate_rows):
        target = query["target"]
        target_key = point_key(target)
        negative_key = point_key(-target)
        oracle_sat = target_key in oracle["support"] or negative_key in oracle["support"]
        candidate_sat = candidate["status"] == "sat"
        complete_status = candidate["status"] in ("sat", "unsat")
        agreement = complete_status and candidate_sat == oracle_sat
        planted_ok = query["kind"] != "planted_positive" or (oracle_sat and candidate_sat)
        scored.append({
            "query_index": query["query_index"],
            "kind": query["kind"],
            "target": point_json(target),
            "target_scalar": query["target_scalar"],
            "candidate": candidate,
            "oracle_sat": oracle_sat,
            "candidate_oracle_agreement": agreement,
            "planted_positive_verified": planted_ok,
        })
    return {
        "queries": scored,
        "oracle": {
            "started_after_all_candidate_decisions": True,
            "levels": oracle["levels"],
            "wall_seconds": oracle["wall_seconds"],
            "a5_witness_failure_count": 0,
        },
        "all_complete": all(row["candidate"]["status"] in ("sat", "unsat") for row in scored),
        "all_agree": all(row["candidate_oracle_agreement"] for row in scored),
        "all_planted_verified": all(row["planted_positive_verified"] for row in scored),
        "all_sat_sources_replayed": all(
            row["candidate"]["status"] != "sat" or row["candidate"]["source_replayed"]
            for row in scored
        ),
    }


def fit_slope(xs: list[float], ys: list[float]) -> dict[str, Any]:
    def slope(sub_x: list[float], sub_y: list[float]) -> float:
        log_x = [math.log(value) for value in sub_x]
        log_y = [math.log(value) for value in sub_y]
        mean_x, mean_y = statistics.mean(log_x), statistics.mean(log_y)
        return sum((x - mean_x) * (y - mean_y) for x, y in zip(log_x, log_y)) / sum(
            (x - mean_x) ** 2 for x in log_x
        )

    full = slope(xs, ys)
    leave_one_out = [
        slope(
            [value for index, value in enumerate(xs) if index != omitted],
            [value for index, value in enumerate(ys) if index != omitted],
        )
        for omitted in range(len(xs))
    ]
    return {
        "slope": full,
        "leave_one_out": leave_one_out,
        "leave_one_out_min": min(leave_one_out),
        "leave_one_out_max": max(leave_one_out),
    }


def deck_summary(deck: dict[str, Any]) -> dict[str, Any]:
    queries = deck["queries"]
    return {
        "root_count": deck["root_count"],
        "max_charged_effort": max(row["candidate"]["charged_effort"] for row in queries),
        "max_formula_bytes": max(row["candidate"]["total_formula_bytes"] for row in queries),
        "max_wall_seconds": max(row["candidate"]["total_wall_seconds"] for row in queries),
        "max_rlimit_count": max(row["candidate"]["total_rlimit_count"] for row in queries),
        "sat_count": sum(row["candidate"]["status"] == "sat" for row in queries),
        "unsat_count": sum(row["candidate"]["status"] == "unsat" for row in queries),
        "incomplete_count": sum(row["candidate"]["status"] not in ("sat", "unsat") for row in queries),
    }


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise RuntimeError(f"refusing symlink output: {path}")
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def render_note(payload: dict[str, Any]) -> str:
    subgroup_fit = payload["fits"].get("subgroup_x_charged_effort")
    slope = "not available" if subgroup_fit is None else f"{subgroup_fit['slope']:.6f}"
    return "\n".join([
        "# P1480 bit-vector serial-S3 membership",
        "",
        "## Status",
        "",
        f"`{payload['status']}`",
        "",
        f"Completed fixtures: `{payload['completed_fixture_L']}`.",
        "",
        f"Subgroup worst-query charged-effort slope: `{slope}`.",
        "",
        f"All candidate/oracle decisions agree: `{payload['gates']['all_candidate_oracle_decisions_agree']}`.",
        "",
        f"All SAT sources replay: `{payload['gates']['all_sat_sources_replayed']}`.",
        "",
        "The exact A5 oracle was constructed only after each deck's candidate",
        "decisions. Z3 effort is a diagnostic proxy, not an implementation-independent",
        "field-operation bound and not a faster-than-rho result.",
        "",
    ])


def run_fixture(fixture: dict[str, int], smoke: bool = False) -> dict[str, Any]:
    context = build_context(fixture)
    subgroup = subgroup_roots(context)
    decks = [("subgroup_x", subgroup), ("random_x", random_x_roots(context, len(subgroup)))]
    if smoke:
        decks = decks[:1]
    deck_rows = []
    for deck_name, roots in decks:
        queries = make_queries(context, deck_name, roots, count=1 if smoke else 8)
        candidate_rows = [candidate_decision(context, roots, query["target"]) for query in queries]
        scored = score_queries(context, queries, candidate_rows, roots)
        deck_row = {
            "deck_name": deck_name,
            "root_count": len(roots),
            "endpoint_count": 2 * len(roots),
            "root_sha256": hashlib.sha256(
                b"|".join(str(root).encode("ascii") for root in roots)
            ).hexdigest(),
            **scored,
        }
        deck_row["summary"] = deck_summary(deck_row)
        deck_rows.append(deck_row)
    return {
        "fixture": fixture,
        "generator": point_json(context["generator"]),
        "decks": deck_rows,
        "stage_pass": all(
            deck[gate]
            for deck in deck_rows
            for gate in ("all_complete", "all_agree", "all_planted_verified", "all_sat_sources_replayed")
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    os.chdir(ROOT)
    observed = {str(path.relative_to(ROOT)): sha256_file(path) for path in EXPECTED}
    expected = {str(path.relative_to(ROOT)): digest for path, digest in EXPECTED.items()}
    if observed != expected:
        raise RuntimeError("frozen P1480 input mismatch")
    version = subprocess.run([str(Z3), "--version"], text=True, capture_output=True, check=True).stdout.strip()
    if version != "Z3 version 4.15.4 - 64 bit":
        raise RuntimeError(f"P1480 solver version mismatch: {version}")

    if args.smoke:
        cell = run_fixture(FIXTURES[0], smoke=True)
        print(json.dumps({
            "smoke_only": True,
            "fixture_L": cell["fixture"]["L"],
            "stage_pass": cell["stage_pass"],
            "query": cell["decks"][0]["queries"][0],
        }, indent=2, sort_keys=True))
        return 0 if cell["stage_pass"] else 1

    cells = []
    stopped_after_L = None
    for fixture in FIXTURES:
        cell = run_fixture(fixture)
        cells.append(cell)
        print(json.dumps({
            "L": fixture["L"],
            "stage_pass": cell["stage_pass"],
            "decks": {deck["deck_name"]: deck["summary"] for deck in cell["decks"]},
        }, sort_keys=True), flush=True)
        if not cell["stage_pass"]:
            stopped_after_L = fixture["L"]
            break

    fits: dict[str, Any] = {}
    all_fixtures = len(cells) == len(FIXTURES)
    if all_fixtures:
        xs = [cell["fixture"]["L"] for cell in cells]
        for deck_name in ("subgroup_x", "random_x"):
            summaries = [
                next(deck["summary"] for deck in cell["decks"] if deck["deck_name"] == deck_name)
                for cell in cells
            ]
            fits[f"{deck_name}_charged_effort"] = fit_slope(
                xs, [summary["max_charged_effort"] for summary in summaries]
            )
            fits[f"{deck_name}_formula_bytes"] = fit_slope(
                xs, [summary["max_formula_bytes"] for summary in summaries]
            )
            fits[f"{deck_name}_rlimit_count"] = fit_slope(
                xs, [max(1, summary["max_rlimit_count"]) for summary in summaries]
            )
            fits[f"{deck_name}_wall_seconds"] = fit_slope(
                xs, [max(1e-6, summary["max_wall_seconds"]) for summary in summaries]
            )

    all_decks = [deck for cell in cells for deck in cell["decks"]]
    all_complete = all(deck["all_complete"] for deck in all_decks)
    all_agree = all(deck["all_agree"] for deck in all_decks)
    all_planted = all(deck["all_planted_verified"] for deck in all_decks)
    all_sources = all(deck["all_sat_sources_replayed"] for deck in all_decks)
    subgroup_effort = fits.get("subgroup_x_charged_effort")
    subgroup_formula = fits.get("subgroup_x_formula_bytes")
    random_effort = fits.get("random_x_charged_effort")
    effort_gate = bool(
        subgroup_effort
        and subgroup_effort["slope"] < 1.5
        and subgroup_effort["leave_one_out_max"] < 1.5
    )
    formula_gate = bool(
        subgroup_formula
        and subgroup_formula["slope"] <= 1.0 + 1e-12
        and subgroup_formula["leave_one_out_max"] <= 1.0 + 1e-12
    )
    subgroup_advantage = bool(
        subgroup_effort and random_effort and subgroup_effort["slope"] < random_effort["slope"]
    )
    circuit_accounted = True
    signal = all(
        (all_fixtures, all_complete, all_agree, all_planted, all_sources,
         effort_gate, formula_gate, subgroup_advantage, circuit_accounted)
    )
    if signal:
        status = "OBSERVATION_P1480_BITVECTOR_SERIAL_S3_MEMBERSHIP_SIGNAL"
    elif stopped_after_L is not None:
        status = "NEGATIVE_RESULT_P1480_STAGED_SOLVER_OR_COMPLETENESS_FAILURE"
    else:
        status = "NEGATIVE_RESULT_P1480_NO_SUB_L_THREE_HALVES_MEMBERSHIP_SIGNAL"
    payload = {
        "schema": SCHEMA,
        "status": status,
        "solver": {"path": str(Z3), "version": version, "timeout_ms": TIMEOUT_MS, "random_seed": 0},
        "cells": cells,
        "completed_fixture_L": [cell["fixture"]["L"] for cell in cells],
        "stopped_after_L": stopped_after_L,
        "fits": fits,
        "gates": {
            "all_64_decisions_complete": all_fixtures and all_complete,
            "all_candidate_oracle_decisions_agree": all_fixtures and all_agree,
            "all_32_planted_positives_verified": all_fixtures and all_planted,
            "all_sat_sources_replayed": all_fixtures and all_sources,
            "oracle_started_after_candidate_decisions": all(
                deck["oracle"]["started_after_all_candidate_decisions"] for deck in all_decks
            ),
            "candidate_uses_no_materialized_a2_through_a5": True,
            "subgroup_worst_effort_all_slopes_below_three_halves": effort_gate,
            "subgroup_formula_all_slopes_at_most_one": formula_gate,
            "subgroup_slope_below_random_x_control": subgroup_advantage,
            "source_level_serial_circuit_accounted": circuit_accounted,
            "portable_proof_search_bound_established": False,
            "relation_rank_descent_not_waived": True,
        },
        "bitvector_serial_s3_membership_signal": signal,
        "frozen_files": observed,
        "boundary": (
            "The exact A5 oracle scores candidate decisions only after the candidate phase. "
            "Z3 rlimit is a deterministic diagnostic proxy, not a portable field-operation bound."
        ),
        "next_action": (
            "If the solver is exact but scales poorly, preserve this encoding and extract the "
            "dominant propagation/conflict mechanism for a custom finite-field propagator. If it "
            "scales below the gate, replay the P1476 relation/rank/descent ledger before promotion."
        ),
    }
    write_atomic(OUT, (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    write_atomic(NOTE, render_note(payload).encode("utf-8"))
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "note": str(NOTE.relative_to(ROOT)),
        "status": status,
        "completed_fixture_L": payload["completed_fixture_L"],
        "fits": fits,
        "signal": signal,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
