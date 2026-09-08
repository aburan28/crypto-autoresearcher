#!/usr/bin/env python3
"""Independent fixed-fixture definition checks for TASK-20260908-fdf173.

This program reads only the handoff-bound source bytes through Git.  It never
imports or runs a producer checker, a research runner, or an arithmetic backend.
It has exactly one fixed 128-case suite and writes no files.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import jsonschema
import yaml


REPO = Path(__file__).resolve().parents[5]
TASK = "TASK-20260908-fdf173"
SOURCE_SNAPSHOT = "8851545401e5f4eda918a82ed1b5b1bde46bbe88"
RECOVERED_APPROVAL = "fcbbb2b59d08c75df4eed71478f0e91a4e4f9f6c"
HANDOFF = "ledger/handoffs/TASK-20260908-fdf173.yaml"
REVIEW_PLAN = (
    "coordination/experiment-reserve/BATCH-45b4d5/"
    "review-plan-TASK-20260908-fdf173.yaml"
)
CONTRACT = (
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-5e3d88/EXP-ECDLP-1b1b99.yaml"
)
SCHEMA = (
    "coordination/experiment-reserve/BATCH-45b4d5/corrections/"
    "TASK-20260908-5e3d88/schema.json"
)
MAX_CASES = 128


class Reject(ValueError):
    pass


def git_bytes(commit: str, path: str) -> bytes:
    proc = subprocess.run(
        ["/usr/bin/git", "show", f"{commit}:{path}"],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise Reject(f"source object unavailable: {commit}:{path}")
    return proc.stdout


def bound_bytes(binding: dict) -> tuple[str, bytes]:
    path = binding["path"]
    if path == REVIEW_PLAN:
        return "live-parent-authority", (REPO / path).read_bytes()
    commit = binding.get("source_commit", SOURCE_SNAPSHOT)
    return commit, git_bytes(commit, path)


def reject_constant(value: str) -> None:
    raise Reject(f"nonfinite JSON token {value!r}")


def no_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    obj: dict = {}
    for key, value in pairs:
        if key in obj:
            raise Reject(f"duplicate JSON key {key!r}")
        obj[key] = value
    return obj


def strict_json(text: str) -> object:
    return json.loads(
        text,
        object_pairs_hook=no_duplicate_pairs,
        parse_constant=reject_constant,
    )


def canonical_integer(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise Reject("canonical integer required")
    return value


def exact_weight(value: object) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        raise Reject("weight must have only numerator and denominator")
    numerator = canonical_integer(value["numerator"])
    denominator = canonical_integer(value["denominator"])
    if numerator <= 0 or denominator <= 0:
        raise Reject("weight must be positive")
    if math.gcd(numerator, denominator) != 1:
        raise Reject("weight must be reduced")
    return Fraction(numerator, denominator)


def exact_keys(actual: dict, required: set[str]) -> None:
    if set(actual) != required:
        raise Reject(f"closed object keys differ: {sorted(actual)}")


def nullable_resource(value: object, reason: object) -> None:
    if value is None:
        if not isinstance(reason, str) or not reason:
            raise Reject("null resource needs exact reason")
    else:
        canonical_integer(value)
        if value < 0 or reason is not None:
            raise Reject("measured resource requires nonnegative integer and null reason")


def validate_edge(edge: dict) -> None:
    required = {
        "record_type", "raw_cost_row_id", "weight", "allocated_CPU_nanoseconds",
        "allocated_CPU_unavailable_reason", "allocated_wall_nanoseconds",
        "allocated_wall_unavailable_reason", "reason_code", "strategy_view",
        "scenario", "target",
    }
    exact_keys(edge, required)
    if edge["record_type"] != "allocation_edge" or not isinstance(edge["raw_cost_row_id"], str):
        raise Reject("edge identity is invalid")
    exact_weight(edge["weight"])
    nullable_resource(edge["allocated_CPU_nanoseconds"], edge["allocated_CPU_unavailable_reason"])
    nullable_resource(edge["allocated_wall_nanoseconds"], edge["allocated_wall_unavailable_reason"])
    scenario = edge["scenario"]
    target = edge["target"]
    view = edge["strategy_view"]
    if not isinstance(scenario, dict) or not isinstance(target, dict):
        raise Reject("scenario and target must be objects")
    kind = scenario.get("kind")
    if kind == "cold":
        exact_keys(scenario, {"kind", "q", "seed"})
        if view not in {"scalar", "transport"}:
            raise Reject("cold view invalid")
        if scenario["q"] not in {1, 16, 256, 4096} or scenario["seed"] not in {606101, 606103}:
            raise Reject("cold axes invalid")
        exact_keys(target, {"kind", "fixture", "endpoint", "coordinate"})
        if target.get("kind") != "endpoint_coordinate":
            raise Reject("cold target invalid")
    elif kind == "selection_score":
        exact_keys(scenario, {"kind", "candidate_arm"})
        if view != "selection_score_candidate" or scenario["candidate_arm"] not in {2, 3, 4, 5, 6, 7}:
            raise Reject("selection-score coupling invalid")
        exact_keys(target, {"kind", "fixture", "endpoint", "coordinate"})
        if target.get("kind") != "endpoint_coordinate":
            raise Reject("selection target invalid")
    elif kind == "actual_only":
        exact_keys(scenario, {"kind"})
        if view != "actual_only_scaffolding":
            raise Reject("actual-only view invalid")
        exact_keys(target, {"kind", "raw_cost_row_id"})
        if target.get("kind") != "physical_owner" or target.get("raw_cost_row_id") != edge["raw_cost_row_id"]:
            raise Reject("actual-only owner must be the same raw row")
        if exact_weight(edge["weight"]) != Fraction(1, 1):
            raise Reject("actual-only edge must be 1/1")
    else:
        raise Reject("unknown scenario kind")


def edge_key(edge: dict) -> str:
    return json.dumps(
        [edge["raw_cost_row_id"], edge["strategy_view"], edge["scenario"], edge["target"]],
        sort_keys=True,
        separators=(",", ":"),
    )


def reconcile_group(edges: list[dict], raw_cpu: int, raw_wall: int) -> None:
    if not edges:
        raise Reject("empty allocation group")
    seen = set()
    weights = Fraction(0, 1)
    cpu = 0
    wall = 0
    for edge in edges:
        validate_edge(edge)
        key = edge_key(edge)
        if key in seen:
            raise Reject("duplicate semantic edge")
        seen.add(key)
        weights += exact_weight(edge["weight"])
        cpu += edge["allocated_CPU_nanoseconds"]
        wall += edge["allocated_wall_nanoseconds"]
    if weights != Fraction(1, 1) or cpu != raw_cpu or wall != raw_wall:
        raise Reject("allocation does not reconcile exactly")


def schema_accepts(validator: jsonschema.Draft202012Validator, value: dict) -> None:
    errors = sorted(validator.iter_errors(value), key=lambda error: error.json_path)
    if errors:
        raise Reject(f"bound schema rejects fixture: {errors[0].message}")


def expect_reject(fn) -> None:
    try:
        fn()
    except Reject:
        return
    raise Reject("invalid fixture was accepted")


def main() -> int:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    handoff = json.loads((REPO / HANDOFF).read_text())["handoff"]
    source_results = []
    for binding in handoff["source_bindings"]:
        origin, data = bound_bytes(binding)
        actual = hashlib.sha256(data).hexdigest()
        source_results.append({
            "path": binding["path"], "origin": origin,
            "expected_sha256": binding["sha256"], "actual_sha256": actual,
            "passed": actual == binding["sha256"],
        })
    if not all(item["passed"] for item in source_results):
        raise Reject("source binding failure; dependent suite is refused")
    contract = yaml.safe_load(git_bytes(SOURCE_SNAPSHOT, CONTRACT))
    schema = json.loads(git_bytes(SOURCE_SNAPSHOT, SCHEMA))
    validator = jsonschema.Draft202012Validator(schema)
    rows = contract["effective_contract"]["cost_contract"]["component_crosswalk"]["rows"]
    cases = []

    def case(case_id: str, name: str, fn) -> None:
        begin_wall = time.perf_counter()
        begin_cpu = time.process_time()
        try:
            fn()
        except Exception as exc:  # an unexpected exception is retained as a failed attempt
            status, detail = "failed", f"{type(exc).__name__}: {exc}"
        else:
            status, detail = "passed", "expected observation obtained"
        cases.append({
            "ordinal": len(cases) + 1, "case_id": case_id, "name": name,
            "status": status, "detail": detail,
            "wall_seconds": time.perf_counter() - begin_wall,
            "cpu_seconds": time.process_time() - begin_cpu,
        })

    # Cases 1..46: every declared component row has a unique canonical phase/scope triple.
    for index, row in enumerate(rows, 1):
        component = row["component"]
        phase = row["allowed_phases"][0]
        scope = row["allowed_scopes"][0]
        def check_row(component=component, phase=phase, scope=scope):
            matches = [entry for entry in rows if entry["component"] == component]
            if len(matches) != 1 or phase not in matches[0]["allowed_phases"] or scope not in matches[0]["allowed_scopes"]:
                raise Reject("component triple is not uniquely closed")
            if component.strip() != component or component.upper() == component:
                raise Reject("component alias admitted")
        case(f"C{index:03d}", f"component triple {component}", check_row)

    reason_code = schema["$defs"]["allocation_edge"]["oneOf"][1]["properties"]["reason_code"]["enum"][0]
    def selection_edge(fixture: str, endpoint: str, coordinate: int) -> dict:
        return {
            "record_type": "allocation_edge", "raw_cost_row_id": "raw-global-library",
            "weight": {"numerator": 1, "denominator": 72},
            "allocated_CPU_nanoseconds": 1, "allocated_CPU_unavailable_reason": None,
            "allocated_wall_nanoseconds": 1, "allocated_wall_unavailable_reason": None,
            "reason_code": reason_code, "strategy_view": "selection_score_candidate",
            "scenario": {"kind": "selection_score", "candidate_arm": 7},
            "target": {"kind": "endpoint_coordinate", "fixture": fixture, "endpoint": endpoint, "coordinate": coordinate},
        }

    # Cases 47..118: each of the mandatory 72 global-library endpoints is represented once.
    ordinal = 47
    global_edges = []
    for fixture in ("I0F0", "I0F1", "I1F0", "I1F1", "I2F0", "I2F1"):
        for endpoint in ("K0", "K1", "K2", "K3"):
            for coordinate in (1, 2, 3):
                edge = selection_edge(fixture, endpoint, coordinate)
                global_edges.append(edge)
                case(f"C{ordinal:03d}", f"global-library selection target {fixture}/{endpoint}/{coordinate}", lambda edge=edge: (schema_accepts(validator, edge), validate_edge(edge)))
                ordinal += 1

    # Cases 119..128: fixed adversarial parsing and allocation fixtures.
    cold = {
        "record_type": "allocation_edge", "raw_cost_row_id": "raw-cold",
        "weight": {"numerator": 1, "denominator": 1},
        "allocated_CPU_nanoseconds": 3, "allocated_CPU_unavailable_reason": None,
        "allocated_wall_nanoseconds": 3, "allocated_wall_unavailable_reason": None,
        "reason_code": schema["$defs"]["allocation_edge"]["oneOf"][0]["properties"]["reason_code"]["enum"][0],
        "strategy_view": "scalar", "scenario": {"kind": "cold", "q": 256, "seed": 606101},
        "target": {"kind": "endpoint_coordinate", "fixture": "I0F0", "endpoint": "K0", "coordinate": 1},
    }
    actual = {
        "record_type": "allocation_edge", "raw_cost_row_id": "raw-publication",
        "weight": {"numerator": 1, "denominator": 1},
        "allocated_CPU_nanoseconds": 5, "allocated_CPU_unavailable_reason": None,
        "allocated_wall_nanoseconds": 5, "allocated_wall_unavailable_reason": None,
        "reason_code": schema["$defs"]["allocation_edge"]["oneOf"][2]["properties"]["reason_code"]["enum"][0],
        "strategy_view": "actual_only_scaffolding", "scenario": {"kind": "actual_only"},
        "target": {"kind": "physical_owner", "raw_cost_row_id": "raw-publication"},
    }
    case("C119", "valid actual-only owner has no q or seed", lambda: (schema_accepts(validator, actual), validate_edge(actual)))
    bad_actual_q = {**actual, "scenario": {"kind": "actual_only", "q": 1}}
    case("C120", "reject actual-only scenario with fabricated q", lambda: expect_reject(lambda: validate_edge(bad_actual_q)))
    bad_selection_seed = selection_edge("I0F0", "K0", 1)
    bad_selection_seed["scenario"] = {"kind": "selection_score", "candidate_arm": 7, "seed": 606101}
    case("C121", "reject selection-score scenario with fabricated seed", lambda: expect_reject(lambda: validate_edge(bad_selection_seed)))
    bad_fraction = {**cold, "weight": {"numerator": 2, "denominator": 4}}
    case("C122", "reject nonreduced fraction alias", lambda: expect_reject(lambda: validate_edge(bad_fraction)))
    short_edges = [{**cold, "weight": {"numerator": 1, "denominator": 2}, "allocated_CPU_nanoseconds": 4, "allocated_wall_nanoseconds": 4}, {**cold, "weight": {"numerator": 1, "denominator": 2}, "target": {"kind": "endpoint_coordinate", "fixture": "I0F0", "endpoint": "K1", "coordinate": 1}, "allocated_CPU_nanoseconds": 5, "allocated_wall_nanoseconds": 5}]
    case("C123", "reject integer allocation remainder loss", lambda: expect_reject(lambda: reconcile_group(short_edges, 10, 10)))
    duplicate_edges = [cold, dict(cold)]
    case("C124", "reject duplicate semantic edge identity", lambda: expect_reject(lambda: reconcile_group(duplicate_edges, 6, 6)))
    case("C125", "reject integral floating-point lexical value", lambda: expect_reject(lambda: canonical_integer(strict_json('{"n":1.0}')["n"])))
    case("C126", "reject Boolean as integer", lambda: expect_reject(lambda: canonical_integer(strict_json('{"n":true}')["n"])))
    case("C127", "reject nonfinite JSON token", lambda: expect_reject(lambda: strict_json('{"n":NaN}')))
    case("C128", "reject duplicate JSON object key", lambda: expect_reject(lambda: strict_json('{"n":1,"n":2}')))

    if len(cases) != MAX_CASES:
        raise Reject(f"internal case accounting error: {len(cases)} != {MAX_CASES}")
    # A whole-ledger reconciliation of the exact 72-target fixture is a source-only
    # arithmetic check; its 72 target attempts have already been reserved above.
    reconcile_group(global_edges, 72, 72)
    output = {
        "schema": "crypto.autoresearch.independent_definition_check_receipt.v1",
        "task_id": TASK,
        "source_snapshot": SOURCE_SNAPSHOT,
        "source_bindings": source_results,
        "source_bindings_passed": all(item["passed"] for item in source_results),
        "case_cap": MAX_CASES,
        "synthetic_cases": cases,
        "case_attempts": len(cases),
        "passed_attempts": sum(case["status"] == "passed" for case in cases),
        "failed_attempts": sum(case["status"] != "passed" for case in cases),
        "synthetic_scope": "fixed benign schema, serialization, and integer-allocation metadata only",
        "scientific_runs": 0,
        "scientific_code_imported": False,
        "producer_checker_imported_or_executed": False,
        "jsonschema_version": jsonschema.__version__,
        "workers": 1,
        "aggregate_wall_seconds": time.perf_counter() - started_wall,
        "aggregate_cpu_seconds": time.process_time() - started_cpu,
        "fixture_material": {
            "component_rows": 46,
            "global_selection_edges": 72,
            "adversarial_cases": ["actual_only_q", "selection_seed", "fraction_alias", "integer_remainder", "duplicate_edge", "float", "boolean", "nonfinite", "duplicate_key"],
            "cold_fixture": cold,
            "actual_only_fixture": actual,
        },
    }
    json.dump(output, sys.stdout, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return 0 if output["failed_attempts"] == 0 else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Reject as exc:
        print(json.dumps({"task_id": TASK, "fatal": str(exc)}, sort_keys=True))
        raise SystemExit(2)
