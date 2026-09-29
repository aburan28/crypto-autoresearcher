"""Independent fixed-definition checks for TASK-20260908-89741c.

This program reads the published fifth CM definition package and its declared
sources.  It does not import or execute the producer checker, an experiment
runner, an allocator, Sage, PARI, a signing path, or any scientific fixture.
"""

from __future__ import annotations

import argparse
import ast
import copy
import csv
import datetime as dt
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
from typing import Any, Callable

import jsonschema
import yaml


TASK_ID = "TASK-20260908-89741c"
SOURCE_SNAPSHOT = "2fd5bb8810983a42a9a217405530c2d6b3d08b75"
AUTHORITY_COMMIT = "dfc0547e0f0f692c3d252584d29916a018b135eb"
CLAIM_COMMIT = "c56222e87c717872b00dc65a4278cc6e6e8e6239"
PRODUCER_TASK = "TASK-20260908-e06add"
MAX_CASES = 640
CASE_TIMEOUT_SECONDS = 10
MAX_AGGREGATE_SECONDS = 1800
MEMORY_LIMIT_BYTES = 2 * 1024**3

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
HANDOFF_PATH = REPO / "ledger/handoffs/TASK-20260908-89741c.yaml"
PLAN_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/review-plan-TASK-20260908-89741c.yaml"
CONTRACT_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-e06add/EXP-ECDLP-1b1b99.yaml"
SCHEMA_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-e06add/schema.json"
PRODUCER_CHECKER_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-e06add/checks.py"
PRODUCER_RECEIPT_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-e06add/check-receipt.json"
PRODUCER_READINESS_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-e06add/readiness.md"
PREDECESSOR_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-5e3d88/EXP-ECDLP-1b1b99.yaml"
PREDECESSOR_SCHEMA_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-5e3d88/schema.json"
ORIGINAL_SPEC_PATH = REPO / "experiments/EXP-ECDLP-1b1b99/specification.yaml"
WRITER_PATH = REPO / "orchestration/adapter/manifest.py"
SNAPSHOT_RECEIPT_PATH = REPO / "coordination/experiment-reserve/BATCH-45b4d5/archives/TASK-20260908-13f032/snapshot.json"


def read_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


HANDOFF = read_yaml(HANDOFF_PATH)["handoff"]
PLAN = read_yaml(PLAN_PATH)["review_plan"]
CONTRACT = read_yaml(CONTRACT_PATH)
PREDECESSOR = read_yaml(PREDECESSOR_PATH)
ORIGINAL = read_yaml(ORIGINAL_SPEC_PATH)["experiment"]
SCHEMA = read_json(SCHEMA_PATH)
PREDECESSOR_SCHEMA = read_json(PREDECESSOR_SCHEMA_PATH)
PRODUCER_RECEIPT = read_json(PRODUCER_RECEIPT_PATH)
SNAPSHOT_RECEIPT = read_json(SNAPSHOT_RECEIPT_PATH)
EFFECTIVE = CONTRACT["effective_contract"]
COST = EFFECTIVE["cost_contract"]
CROSSWALK = COST["component_crosswalk"]["rows"]
CROSSWALK_BY_COMPONENT = {row["component"]: row for row in CROSSWALK}
COMPONENT_RELATION = SCHEMA["x-component-plane-arm-relation"]
OUTCOME_ROWS = SCHEMA["x-outcome-relation"]
OUTCOME_BY_CODE = {row["reason_code"]: row for row in OUTCOME_ROWS}
VALIDATOR = jsonschema.Draft202012Validator(
    SCHEMA, format_checker=jsonschema.FormatChecker()
)

FIXTURES = ["I0F0", "I0F1", "I1F0", "I1F1", "I2F0", "I2F1"]
ENDPOINTS = ["K0", "K1", "K2", "K3"]
COORDINATES = [1, 2, 3]
SEEDS = [606101, 606103]
Q_VALUES = [1, 16, 256, 4096]
BLOCKS = list(range(7))
TARGETS = [
    {
        "kind": "endpoint_coordinate",
        "fixture": fixture,
        "endpoint": endpoint,
        "coordinate": coordinate,
    }
    for fixture in FIXTURES
    for endpoint in ENDPOINTS
    for coordinate in COORDINATES
]

Case = tuple[str, Callable[[], bool]]
CASES: list[Case] = []
OBSERVATIONS: dict[str, Any] = {}


def add_case(name: str, function: Callable[[], bool]) -> None:
    CASES.append((name, function))


def require(condition: Any, message: str) -> bool:
    if not condition:
        raise AssertionError(message)
    return True


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def bound_source_bytes(relative: str, expected_hash: str) -> bytes:
    """Read a binding, with the one declared queue-history recovery."""
    current = (REPO / relative).read_bytes()
    if sha256_bytes(current) == expected_hash:
        return current
    if relative == "coordination/experiment-reserve/BATCH-45b4d5/dispatch_queue.json":
        recovery_commit = "209b4196d5fb0f008c465cc9a1cc8a2045e4967c"
        recovered = git("show", f"{recovery_commit}:{relative}", binary=True)
        require(sha256_bytes(recovered) == expected_hash, "queue recovery hash")
        OBSERVATIONS["administrative_queue_binding_recovery"] = {
            "path": relative,
            "bound_sha256": expected_hash,
            "recovery_commit": recovery_commit,
            "authority_sha256": sha256_bytes(current),
            "reason": "authority commit appended this review and archive tasks to the queue",
        }
        return recovered
    raise AssertionError(f"source hash mismatch {relative}")


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def strict_json(text: str) -> Any:
    def object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate JSON key")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValueError(f"nonfinite JSON number {value}")

    return json.loads(
        text, object_pairs_hook=object_pairs, parse_constant=reject_constant
    )


def numeric_lexical_profile(value: Any, path: tuple[Any, ...] = ()) -> bool:
    allowed_float_paths = {
        ("run", "timing", "wall_seconds"),
        ("run", "resources", "cpu_seconds"),
    }
    if isinstance(value, float) and path not in allowed_float_paths:
        raise ValueError("noncanonical floating-point lexeme")
    if isinstance(value, dict):
        for key, item in value.items():
            numeric_lexical_profile(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            numeric_lexical_profile(item, path + (index,))
    return True


def resource_reason_profile(document: dict[str, Any]) -> bool:
    resources = document["run"]["resources"]
    for value_key, reason_key in [
        ("peak_rss_bytes", "peak_rss_unavailable_reason"),
        ("cpu_nanoseconds", "cpu_unavailable_reason"),
    ]:
        require(
            (resources[value_key] is None) == (resources[reason_key] is not None),
            f"resource/reason identity {value_key}",
        )
    require(
        (resources["cpu_seconds"] is None) == (resources["cpu_nanoseconds"] is None),
        "CPU display/exact identity",
    )
    return True


def git(*args: str, binary: bool = False) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=CASE_TIMEOUT_SECONDS,
        check=False,
    )
    if result.returncode:
        raise AssertionError(
            f"git {' '.join(args)} failed {result.returncode}: "
            f"{result.stderr.decode('utf-8', errors='replace')}"
        )
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def schema_accepts(value: Any) -> bool:
    VALIDATOR.validate(value)
    return True


def schema_rejects(value: Any) -> bool:
    try:
        VALIDATOR.validate(value)
    except jsonschema.ValidationError:
        return True
    raise AssertionError("schema unexpectedly admitted fixed known-invalid object")


def fraction_object(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def fraction_value(value: dict[str, int], *, positive: bool = False) -> Fraction:
    require(set(value) == {"numerator", "denominator"}, "fraction key set")
    numerator = value["numerator"]
    denominator = value["denominator"]
    require(type(numerator) is int and type(denominator) is int, "fraction integer types")
    require(numerator >= (1 if positive else 0), "fraction numerator domain")
    require(denominator > 0, "fraction denominator domain")
    require(math.gcd(numerator, denominator) == 1, "fraction reduced form")
    return Fraction(numerator, denominator)


def med7(values: list[Fraction]) -> Fraction:
    require(len(values) == 7, "Med7 cardinality")
    return sorted(values)[3]


def med6(values: list[Fraction]) -> Fraction:
    require(len(values) == 6, "Med6 cardinality")
    ordered = sorted(values)
    return (ordered[2] + ordered[3]) / 2


def raw_row(
    component: str,
    *,
    relation: dict[str, Any] | None = None,
    arm: int | None = None,
    status: str = "complete",
    cpu: int | None = 37,
    wall: int | None = 41,
) -> dict[str, Any]:
    row_definition = CROSSWALK_BY_COMPONENT[component]
    scope = row_definition["allowed_scopes"][0]
    charge_kind = (
        "derived_rollup"
        if component in {
            "level_and_multiplicity_certificate",
            "all_six_algorithm_selection_trials",
        }
        else "exclusive_leaf"
    )
    if charge_kind == "derived_rollup":
        cpu = None
        wall = None
    row: dict[str, Any] = {
        "record_type": "raw_cost",
        "raw_cost_row_id": f"raw-{component}",
        "physical_event_id": f"event-{component}",
        "event_ordinal": 0,
        "component": component,
        "phase": row_definition["allowed_phases"][0],
        "status": status,
        "CPU_nanoseconds": cpu,
        "CPU_unavailable_reason": (
            "derived_rollup" if charge_kind == "derived_rollup" else (
                None if cpu is not None else "capture_failed"
            )
        ),
        "wall_nanoseconds": wall,
        "wall_unavailable_reason": (
            "derived_rollup" if charge_kind == "derived_rollup" else (
                None if wall is not None else "capture_failed"
            )
        ),
        "process_group_peak_RSS_bytes": 1024,
        "RSS_unavailable_reason": None,
        "operation_counts": None,
        "operation_counts_unavailable_reason": "uninstrumented_backend",
        "capture_interval": {
            "stream_id": "fixed-validator-stream",
            "process_group_id": 7,
            "cpu_started_ns": 0,
            "cpu_finished_ns": 37,
            "wall_started_ns": 0,
            "wall_finished_ns": 41,
            "reason": None,
        },
        "charge_kind": charge_kind,
        "source_leaf_ids": ["fixed-exclusive-leaf"] if charge_kind == "derived_rollup" else [],
        "scope": scope,
    }
    values = {
        "interval": "I0",
        "fixture": "I0F0",
        "kernel": "K0",
        "class": "C0",
        "endpoint": "K0",
        "coordinate": 1,
        "plane": "main",
        "seed": 606103,
        "q": 4096,
        "arm": 2,
        "block": 0,
        "repetition": 1,
    }
    if scope == "scaffolding":
        row["scaffold_kind"] = component
        if component == "top_level_control":
            row["owner"] = {
                "scope": "control_workload",
                "fixture": "I0F0",
                "coordinate": 1,
                "plane": "top_control",
                "seed": 606101,
                "q": 1,
                "arm": "direct_3_iota",
            }
        elif component == "identity_transport_control":
            row["owner"] = {
                "scope": "control_workload",
                "fixture": "I0F0",
                "coordinate": 1,
                "plane": "identity_control",
                "seed": 606101,
                "q": 1,
                "arm": "direct_iota",
            }
        else:
            row["owner"] = {"scope": "global"}
    else:
        for index in COST["raw_cost_tensor"]["scope_variants"][scope]["required_indices"]:
            row[index] = values[index]
    if component in COMPONENT_RELATION:
        selected_relation = relation or COMPONENT_RELATION[component][0]
        row["plane"] = selected_relation["plane"]
        row["arm"] = selected_relation["arms"][0] if arm is None else arm
        if row["plane"] == "selection":
            row["seed"] = 606101
            row["q"] = 256
    return row


def target_domain(row: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]] | None:
    targets = TARGETS
    scope = row["scope"]
    if scope == "global":
        return targets
    if scope == "interval":
        fixture = context["accepted_candidate_owner"].get(
            (row["interval"], row["event_ordinal"])
        )
        if fixture is None:
            return None
        return [target for target in targets if target["fixture"] == fixture]
    if scope == "fixture":
        return [target for target in targets if target["fixture"] == row["fixture"]]
    if scope == "kernel":
        return [
            target
            for target in targets
            if target["fixture"] == row["fixture"]
            and target["endpoint"] == row["kernel"]
        ]
    if scope == "class":
        members = context["class_members"].get((row["fixture"], row["class"]))
        if members is None:
            return None
        return [
            target
            for target in targets
            if target["fixture"] == row["fixture"]
            and target["endpoint"] in members
        ]
    if scope == "endpoint_coordinate":
        return [
            target
            for target in targets
            if target["fixture"] == row["fixture"]
            and target["endpoint"] == row["endpoint"]
            and target["coordinate"] == row["coordinate"]
        ]
    if scope == "selection_stratum":
        return [
            target
            for target in targets
            if target["fixture"].startswith(row["interval"])
            and target["coordinate"] == row["coordinate"]
        ]
    if scope in {"arm_workload", "timing_block", "block_repetition"}:
        return [
            target
            for target in targets
            if target["fixture"] == row["fixture"]
            and target["endpoint"] == row["endpoint"]
            and target["coordinate"] == row["coordinate"]
        ]
    if scope == "scaffolding":
        return []
    raise AssertionError(f"unknown scope {scope}")


def fixed_context() -> dict[str, Any]:
    return {
        "accepted_candidate_owner": {("I0", 0): "I0F0"},
        "class_members": {
            (fixture, class_id): (["K0", "K1"] if class_id == "C0" else ["K2", "K3"])
            for fixture in FIXTURES
            for class_id in ["C0", "C1"]
        },
        "winners": {
            (interval, coordinate): 2
            for interval in ["I0", "I1", "I2"]
            for coordinate in COORDINATES
        },
    }


def expected_groups(
    row: dict[str, Any], context: dict[str, Any]
) -> list[tuple[str, dict[str, Any], list[dict[str, Any]], str]]:
    if row["charge_kind"] == "derived_rollup":
        return []
    targets = target_domain(row, context)
    resources_known = row["CPU_nanoseconds"] is not None and row["wall_nanoseconds"] is not None
    if targets is None or not resources_known:
        return [
            (
                "actual_only_scaffolding",
                {"kind": "actual_only"},
                [{"kind": "physical_owner", "raw_cost_row_id": row["raw_cost_row_id"]}],
                "actual_only",
            )
        ]
    definition = CROSSWALK_BY_COMPONENT[row["component"]]
    family = definition["family"]
    cold = [
        {"kind": "cold", "q": q, "seed": seed}
        for seed in SEEDS
        for q in Q_VALUES
    ]
    groups: list[tuple[str, dict[str, Any], list[dict[str, Any]], str]] = []
    if family == "shared":
        for view in ["scalar", "transport"]:
            groups.extend((view, scenario, targets, "shared_setup") for scenario in cold)
    elif family == "transport":
        groups.extend(("transport", scenario, targets, "transport_setup") for scenario in cold)
    elif row["component"] in {
        "global_library_initialization",
        "baseline_selection_stratum_overhead",
    }:
        groups.extend(
            ("scalar", scenario, targets, "selection_actual_spend")
            for scenario in cold
        )
        if row["component"] == "global_library_initialization":
            groups.append(
                (
                    "selection_score_candidate",
                    {"kind": "selection_score", "candidate_arm": 7},
                    targets,
                    "selection_score",
                )
            )
    elif family == "arm_context" and row["plane"] == "selection":
        groups.extend(
            ("scalar", scenario, targets, "selection_actual_spend")
            for scenario in cold
        )
        groups.append(
            (
                "selection_score_candidate",
                {"kind": "selection_score", "candidate_arm": row["arm"]},
                targets,
                "selection_score",
            )
        )
    elif family == "arm_context" and row["plane"] == "main":
        scenario = {"kind": "cold", "q": row["q"], "seed": row["seed"]}
        winner = context["winners"][(row["fixture"][:2], row["coordinate"])]
        if row["arm"] == 1:
            groups.append(("transport", scenario, targets, "selected_main_work"))
        elif row["arm"] == winner:
            groups.append(("scalar", scenario, targets, "selected_main_work"))
    if not groups:
        groups.append(
            (
                "actual_only_scaffolding",
                {"kind": "actual_only"},
                [{"kind": "physical_owner", "raw_cost_row_id": row["raw_cost_row_id"]}],
                "actual_only",
            )
        )
    return groups


def make_edges(row: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for view, scenario, targets, reason in expected_groups(row, context):
        count = len(targets)
        require(count > 0, "allocation target domain is nonempty")
        for ordinal, target in enumerate(targets):
            edge: dict[str, Any] = {
                "record_type": "allocation_edge",
                "raw_cost_row_id": row["raw_cost_row_id"],
                "strategy_view": view,
                "scenario": copy.deepcopy(scenario),
                "target": copy.deepcopy(target),
                "weight": {"numerator": 1, "denominator": count},
                "allocated_CPU_nanoseconds": None,
                "allocated_CPU_unavailable_reason": row["CPU_unavailable_reason"],
                "allocated_wall_nanoseconds": None,
                "allocated_wall_unavailable_reason": row["wall_unavailable_reason"],
                "reason_code": reason,
            }
            for source, destination, reason_field in [
                ("CPU_nanoseconds", "allocated_CPU_nanoseconds", "allocated_CPU_unavailable_reason"),
                ("wall_nanoseconds", "allocated_wall_nanoseconds", "allocated_wall_unavailable_reason"),
            ]:
                if row[source] is not None:
                    edge[destination] = row[source] // count + int(ordinal < row[source] % count)
                    edge[reason_field] = None
            edges.append(edge)
    return edges


def check_allocation(
    rows: list[dict[str, Any]], edges: list[dict[str, Any]], context: dict[str, Any]
) -> bool:
    for row in rows:
        VALIDATOR.validate(row)
    for edge in edges:
        VALIDATOR.validate(edge)
    rows_by_id = {row["raw_cost_row_id"]: row for row in rows}
    require(len(rows_by_id) == len(rows), "duplicate raw row id")
    physical_ids = [
        row["physical_event_id"]
        for row in rows
        if row["charge_kind"] == "exclusive_leaf"
    ]
    require(len(physical_ids) == len(set(physical_ids)), "duplicate physical event")
    expected: dict[tuple[str, str, str], tuple[list[dict[str, Any]], str]] = {}
    for row in rows:
        for view, scenario, targets, reason in expected_groups(row, context):
            expected[(row["raw_cost_row_id"], view, canonical(scenario))] = (targets, reason)
    actual: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    edge_keys: set[tuple[str, str, str, str]] = set()
    for edge in edges:
        require(edge["raw_cost_row_id"] in rows_by_id, "edge source exists")
        key = (
            edge["raw_cost_row_id"],
            edge["strategy_view"],
            canonical(edge["scenario"]),
        )
        edge_key = (*key, canonical(edge["target"]))
        require(edge_key not in edge_keys, "duplicate allocation edge")
        edge_keys.add(edge_key)
        actual.setdefault(key, []).append(edge)
    require(set(actual) == set(expected), "complete allocation group set")
    for key, (targets, reason) in expected.items():
        group = actual[key]
        row = rows_by_id[key[0]]
        require(len(group) == len(targets), "complete target count")
        by_target = {canonical(edge["target"]): edge for edge in group}
        require(
            set(by_target) == {canonical(target) for target in targets},
            "exact target domain",
        )
        count = len(targets)
        for ordinal, target in enumerate(targets):
            edge = by_target[canonical(target)]
            require(edge["reason_code"] == reason, "edge reason relation")
            require(fraction_value(edge["weight"], positive=True) == Fraction(1, count), "edge weight")
            for source, destination, raw_reason, edge_reason in [
                (
                    "CPU_nanoseconds",
                    "allocated_CPU_nanoseconds",
                    "CPU_unavailable_reason",
                    "allocated_CPU_unavailable_reason",
                ),
                (
                    "wall_nanoseconds",
                    "allocated_wall_nanoseconds",
                    "wall_unavailable_reason",
                    "allocated_wall_unavailable_reason",
                ),
            ]:
                if row[source] is None:
                    require(edge[destination] is None, "unknown allocation stays null")
                    require(edge[edge_reason] == row[raw_reason], "unknown reason propagates")
                else:
                    expected_integer = row[source] // count + int(ordinal < row[source] % count)
                    require(edge[destination] == expected_integer, "canonical integer remainder")
                    require(edge[edge_reason] is None, "measured allocation has null reason")
    return True


def deterministic_writer_block(note: str | None = None) -> dict[str, Any]:
    module = ast.parse(WRITER_PATH.read_text(encoding="utf-8"))
    function = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "deterministic_block"
    )
    namespace: dict[str, Any] = {"Any": Any, "ADAPTER_VERSION": "fixed-adapter-version"}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(WRITER_PATH), "exec"), namespace)
    if note is None:
        return namespace["deterministic_block"]()
    return namespace["deterministic_block"](note=note)


def model_inference_block() -> dict[str, Any]:
    return {
        "requested_policy": "review-adversarial",
        "canonical_policy": "review-adversarial",
        "backend": "openai",
        "provider": "openai",
        "resolved_model_id": "gpt-5.6-sol",
        "model_provenance": "operator-supplied",
        "model_verified": False,
        "requested_reasoning_effort": "xhigh",
        "reasoning_effort": "xhigh",
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": True,
        "adapter_version": "fixed-adapter-version",
        "config_digest": "0" * 64,
    }


def base_manifest() -> dict[str, Any]:
    contract_hash = sha256_file(CONTRACT_PATH)
    schema_hash = sha256_file(SCHEMA_PATH)
    handoff_hash = sha256_file(HANDOFF_PATH)
    run_id = "RUN-ECDLP-a1b2c3"
    run_path = f"/fixed-validator/{run_id}"
    return {
        "run": {
            "id": run_id,
            "experiment_id": "EXP-ECDLP-1b1b99",
            "status": "partial_inconclusive",
            "code": {
                "commit": "0" * 40,
                "dirty": False,
                "command": "fixed abstract definition object",
                "dirty_diff_sha256": None,
                "source_sha256": {"fixed-source.py": "0" * 64},
            },
            "inference": deterministic_writer_block(),
            "environment": {
                "operating_system": "fixed-Darwin",
                "architecture": "arm64",
                "sage_version": None,
                "python_version": "fixed",
                "dependencies": {},
                "runtime_binding_sha256": EFFECTIVE["runtime_and_public_trust_binding"]["sha256"],
            },
            "inputs": {
                "curve_id": None,
                "seed": None,
                "parameters": {
                    "fixture_ids": FIXTURES,
                    "endpoint_ids": ENDPOINTS,
                    "coordinate_values": COORDINATES,
                    "seed_values": SEEDS,
                    "q_values": Q_VALUES,
                    "arm_values": list(range(1, 8)),
                    "timing_block_values": BLOCKS,
                    "primary_seed": 606103,
                    "primary_q": 4096,
                    "required_primary_cells": 36,
                    "effective_contract_sha256": contract_hash,
                },
                "fixture_artifact": "fixtures.json",
            },
            "timing": {
                "started_at": "2026-09-08T00:00:00Z",
                "finished_at": "2026-09-08T00:00:01Z",
                "wall_seconds": 1,
                "wall_nanoseconds": 1_000_000_000,
            },
            "resources": {
                "peak_rss_bytes": None,
                "peak_rss_unavailable_reason": "infrastructure_stopped",
                "cpu_seconds": None,
                "cpu_nanoseconds": None,
                "cpu_unavailable_reason": "not_observed_before_stop",
                "measurement_scope": "whole_process_group",
            },
            "result": {
                "metrics": {
                    "R_cells": [],
                    "R_global": [],
                    "q_star": [],
                    "branch": "inconclusive",
                    "coverage": {
                        "accepted_fixtures": 0,
                        "resolved_primary_cells": 0,
                        "main_block_rows": 0,
                        "selection_block_rows": 0,
                        "top_block_rows": 0,
                        "identity_block_rows": 0,
                        "all_controls_passed": False,
                    },
                },
                "valid": False,
                "invalid_reason": "MATRIX_INCOMPLETE",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
                "reason_code": "MATRIX_INCOMPLETE",
                "stage": "run_complete_timing_and_control_matrices",
            },
            "artifacts": {},
            "directory": {
                "path": run_path,
                "path_sha256": sha256_bytes(run_path.encode("utf-8")),
            },
            "admission": {
                "authorization_payload_sha256": "0" * 64,
                "effective_contract_sha256": contract_hash,
                "schema_sha256": schema_hash,
                "handoff_sha256": handoff_hash,
                "implementation_snapshot_commit": "0" * 40,
                "review_archive_commit": SOURCE_SNAPSHOT,
                "review_report_sha256": "0" * 64,
            },
        }
    }


def complete_manifest() -> dict[str, Any]:
    document = base_manifest()
    run = document["run"]
    run["status"] = "completed_valid"
    run["resources"] = {
        "peak_rss_bytes": 4096,
        "peak_rss_unavailable_reason": None,
        "cpu_seconds": 1,
        "cpu_nanoseconds": 1_000_000_000,
        "cpu_unavailable_reason": None,
        "measurement_scope": "whole_process_group",
    }
    run["result"].update(
        valid=True,
        invalid_reason=None,
        reason_code="VALID_COMPLETE_PANEL",
        stage="finalize_manifest_and_atomic_publish",
    )
    run["result"]["metrics"]["branch"] = "exact_finite_cost_gap_only"
    run["result"]["metrics"]["coverage"] = {
        "accepted_fixtures": 6,
        "resolved_primary_cells": 36,
        "main_block_rows": 28224,
        "selection_block_rows": 3024,
        "top_block_rows": 2016,
        "identity_block_rows": 2016,
        "all_controls_passed": True,
    }
    ratio = {"kind": "value", "value": fraction_object(1)}
    run["result"]["metrics"]["R_cells"] = [
        {
            "fixture": fixture,
            "class": class_id,
            "coordinate": coordinate,
            "seed": seed,
            "q": q,
            "ratio": copy.deepcopy(ratio),
            "leave_one_out": (
                [
                    {**copy.deepcopy(ratio), "omitted_block": block}
                    for block in BLOCKS
                ]
                if seed == 606103 and q == 4096
                else []
            ),
        }
        for fixture in FIXTURES
        for class_id in ["C0", "C1"]
        for coordinate in COORDINATES
        for seed in SEEDS
        for q in Q_VALUES
    ]
    run["result"]["metrics"]["R_global"] = [
        {"seed": seed, "q": q, "ratio": copy.deepcopy(ratio)}
        for seed in SEEDS
        for q in Q_VALUES
    ]
    run["result"]["metrics"]["q_star"] = [
        {
            "fixture": fixture,
            "class": class_id,
            "coordinate": coordinate,
            "result": {"kind": "crossing", "q": 1},
        }
        for fixture in FIXTURES
        for class_id in ["C0", "C1"]
        for coordinate in COORDINATES
    ]
    run["artifacts"] = {
        name: {"sha256": "0" * 64, "bytes": 1}
        for name in EFFECTIVE["artifact_custody"]["required_artifacts"]
        if name != "manifest.yaml"
    }
    return document


def outcome_manifest(reason_code: str) -> dict[str, Any]:
    relation = OUTCOME_BY_CODE[reason_code]
    document = complete_manifest() if relation["valid"] else base_manifest()
    run = document["run"]
    run["status"] = relation["status"]
    run["result"]["reason_code"] = reason_code
    run["result"]["stage"] = relation["stages"][0]
    run["result"]["valid"] = relation["valid"]
    run["result"]["invalid_reason"] = None if relation["valid"] else reason_code
    run["result"]["metrics"]["branch"] = relation["branches"][0]
    if reason_code == "POLICY_RESOLUTION_FAILED":
        inference = deterministic_writer_block("policy resolution failed")
        inference["resolution_error"] = "ValueError: fixed unavailable policy"
        inference["model_verified"] = False
        run["inference"] = inference
    return document


def validate_manifest_semantics(document: dict[str, Any]) -> bool:
    VALIDATOR.validate(document)
    run = document["run"]
    result = run["result"]
    relation = OUTCOME_BY_CODE[result["reason_code"]]
    require(run["status"] == relation["status"], "outcome status relation")
    require(result["stage"] in relation["stages"], "outcome stage relation")
    require(result["valid"] is relation["valid"], "outcome validity relation")
    require(result["metrics"]["branch"] in relation["branches"], "outcome branch relation")
    require(
        result["invalid_reason"] == (None if relation["valid"] else result["reason_code"]),
        "invalid reason identity",
    )
    started = dt.datetime.fromisoformat(run["timing"]["started_at"].replace("Z", "+00:00"))
    finished = dt.datetime.fromisoformat(run["timing"]["finished_at"].replace("Z", "+00:00"))
    require(finished >= started, "UTC chronology")
    require(
        run["directory"]["path_sha256"]
        == sha256_bytes(run["directory"]["path"].encode("utf-8")),
        "run directory hash",
    )
    if "resolution_error" in run["inference"]:
        require(result["reason_code"] == "POLICY_RESOLUTION_FAILED", "resolution failure reason")
        require(run["status"] == "refused_before_run", "resolution failure status")
    if run["status"] == "completed_valid":
        metrics = result["metrics"]
        cells = metrics["R_cells"]
        global_cells = metrics["R_global"]
        q_stars = metrics["q_star"]
        require(len(cells) == 288, "complete R-cell cardinality")
        require(len(global_cells) == 8, "complete global cardinality")
        require(len(q_stars) == 36, "complete q-star cardinality")
        cell_keys = {
            (row["fixture"], row["class"], row["coordinate"], row["seed"], row["q"])
            for row in cells
        }
        require(len(cell_keys) == 288, "unique R-cell keys")
        for row in cells:
            labels = [item["omitted_block"] for item in row["leave_one_out"]]
            if row["seed"] == 606103 and row["q"] == 4096:
                require(sorted(labels) == BLOCKS, "governing LOO labels")
            else:
                require(labels == [], "non-governing LOO empty")
        required_artifacts = set(EFFECTIVE["artifact_custody"]["required_artifacts"]) - {"manifest.yaml"}
        require(set(run["artifacts"]) == required_artifacts, "complete companion artifacts")
        require(all(item["bytes"] > 0 for item in run["artifacts"].values()), "nonempty artifacts")
    return True


def loo_source() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    endpoints = [
        {
            "scalar": {
                "setup": 3,
                "blocks": {block: fraction_object(Fraction(block * block + 1, 8)) for block in BLOCKS},
            },
            "transport": {
                "setup": 1,
                "blocks": {block: fraction_object(1) for block in BLOCKS},
            },
        },
        {
            "scalar": {
                "setup": 7,
                "blocks": {
                    block: fraction_object(Fraction([6, 2, 7, 1, 5, 3, 4][block], 7))
                    for block in BLOCKS
                },
            },
            "transport": {
                "setup": 2,
                "blocks": {
                    block: fraction_object(Fraction([2, 1, 3, 7, 4, 5, 6][block], 3))
                    for block in BLOCKS
                },
            },
        },
    ]
    items: list[dict[str, Any]] = []
    for omitted in BLOCKS:
        totals: dict[str, Fraction] = {}
        for strategy in ["scalar", "transport"]:
            totals[strategy] = sum(
                endpoint[strategy]["setup"]
                + med6(
                    [
                        fraction_value(endpoint[strategy]["blocks"][block])
                        for block in BLOCKS
                        if block != omitted
                    ]
                )
                for endpoint in endpoints
            )
        items.append(
            {
                "omitted_block": omitted,
                "kind": "value",
                "value": fraction_object(totals["scalar"] / totals["transport"]),
            }
        )
    return items, endpoints


def check_loo(items: list[dict[str, Any]], endpoints: list[dict[str, Any]]) -> bool:
    require(sorted(item["omitted_block"] for item in items) == BLOCKS, "LOO label identity")
    require(len(endpoints) == 2, "two endpoint inputs")
    for endpoint in endpoints:
        for strategy in ["scalar", "transport"]:
            require(set(endpoint[strategy]["blocks"]) == set(BLOCKS), "source block identity")
    for item in items:
        omitted = item["omitted_block"]
        totals: dict[str, Fraction] = {}
        for strategy in ["scalar", "transport"]:
            totals[strategy] = sum(
                endpoint[strategy]["setup"]
                + med6(
                    [
                        fraction_value(endpoint[strategy]["blocks"][block])
                        for block in BLOCKS
                        if block != omitted
                    ]
                )
                for endpoint in endpoints
            )
        require(totals["transport"] > 0, "positive transport denominator")
        require(item["kind"] == "value", "fixed LOO value")
        require(
            fraction_value(item["value"]) == totals["scalar"] / totals["transport"],
            "LOO label/value recomputation",
        )
    return True


def q_star(values: dict[int, Fraction | None]) -> str | int:
    for q in Q_VALUES:
        if values.get(q) is None:
            return "unresolved"
        if values[q] >= 1:
            return q
    return ">4096"


def parse_all_bound_structured_sources() -> bool:
    for item in HANDOFF["source_bindings"]:
        path = REPO / item["path"]
        suffix = path.suffix.lower()
        if suffix in {".yaml", ".yml"}:
            require(read_yaml(path) is not None, f"parsed YAML {item['path']}")
        elif suffix == ".json":
            require(read_json(path) is not None, f"parsed JSON {item['path']}")
        else:
            require(len(path.read_bytes()) > 0, f"nonempty source {item['path']}")
    return True


def register_source_and_custody_cases() -> None:
    require(len(HANDOFF["inputs"]) == 73, "handoff input count")
    require(len(HANDOFF["source_bindings"]) == 73, "handoff source binding count")
    for binding in HANDOFF["source_bindings"]:
        relative = binding["path"]
        expected_hash = binding["sha256"]
        add_case(
            f"source SHA-256 {relative}",
            lambda relative=relative, expected_hash=expected_hash: require(
                sha256_bytes(bound_source_bytes(relative, expected_hash)) == expected_hash,
                f"source hash mismatch {relative}",
            ),
        )
    add_case("all 73 bound sources are completely readable and structured files parse", parse_all_bound_structured_sources)
    add_case(
        "handoff input and source-binding path sets are identical",
        lambda: require(
            HANDOFF["inputs"] == [item["path"] for item in HANDOFF["source_bindings"]],
            "input/source order and path identity",
        ),
    )
    add_case(
        "review plan exact source snapshot and assignment",
        lambda: require(
            PLAN["source_snapshot"] == SOURCE_SNAPSHOT
            and all(joint["assigned_to"] == TASK_ID for joint in PLAN["joints"])
            and PLAN["proves_too_much"]["assigned_to"] == TASK_ID,
            "review plan binding",
        ),
    )
    add_case(
        "review inference requires native xhigh independent no fallback or degradation",
        lambda: require(
            HANDOFF["inference"]
            == {
                "policy": "review-adversarial",
                "reasoning_effort": "xhigh",
                "fallback_allowed": False,
                "degraded_allowed": False,
                "independent_session_required": True,
            },
            "review inference envelope",
        ),
    )

    def policy_binding() -> bool:
        policies = read_yaml(REPO / "orchestration/model-policies.yaml")
        bindings = read_yaml(REPO / "orchestration/model-bindings.yaml")
        policy = policies["policies"]["review-adversarial"]
        binding = bindings["bindings"]["openai"]["review-adversarial"]
        return require(
            policy["reasoning_effort"] == "xhigh"
            and policy["independent_session_required"] is True
            and binding["model"] == "gpt-5.6-sol"
            and "xhigh" in binding["request"]["reasoning"]["effort_map"],
            "native policy binding",
        )

    add_case("published native review policy binding", policy_binding)

    def snapshot_git_shape() -> bool:
        parent = git("show", "-s", "--format=%P", SOURCE_SNAPSHOT)
        changed = set(git("diff-tree", "--root", "--no-commit-id", "--name-only", "-r", SOURCE_SNAPSHOT).splitlines())
        expected = set(SNAPSHOT_RECEIPT["source_path_sha256"]) | {
            str(SNAPSHOT_RECEIPT_PATH.relative_to(REPO))
        }
        return require(
            parent == SNAPSHOT_RECEIPT["parent_sha"] and changed == expected,
            "snapshot parent/path set",
        )

    add_case("source snapshot exact parent and six-path tree delta", snapshot_git_shape)

    def snapshot_blob_hashes() -> bool:
        for relative, expected_hash in SNAPSHOT_RECEIPT["source_path_sha256"].items():
            blob = git("show", f"{SOURCE_SNAPSHOT}:{relative}", binary=True)
            require(sha256_bytes(blob) == expected_hash, f"snapshot blob {relative}")
        return True

    add_case("source snapshot five producer blobs match receipt", snapshot_blob_hashes)

    add_case(
        "source snapshot is ancestor of published authority",
        lambda: require(
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", SOURCE_SNAPSHOT, AUTHORITY_COMMIT],
                cwd=REPO,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=CASE_TIMEOUT_SECONDS,
                check=False,
            ).returncode
            == 0,
            "snapshot ancestry",
        ),
    )

    def authority_and_claim() -> bool:
        authority_parent = git("show", "-s", "--format=%P", AUTHORITY_COMMIT)
        claim_parent = git("show", "-s", "--format=%P", CLAIM_COMMIT)
        authority_paths = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", AUTHORITY_COMMIT).splitlines())
        claim_paths = set(git("diff-tree", "--no-commit-id", "--name-only", "-r", CLAIM_COMMIT).splitlines())
        expected_authority = {
            "coordination/experiment-reserve/BATCH-45b4d5/dispatch_queue.json",
            "coordination/experiment-reserve/BATCH-45b4d5/review-plan-TASK-20260908-89741c.yaml",
            "ledger/handoffs/TASK-20260908-705166.yaml",
            "ledger/handoffs/TASK-20260908-89741c.yaml",
        }
        expected_claim = {
            "coordination/experiment-reserve/BATCH-45b4d5/claims/TASK-20260908-89741c.1.claim.json"
        }
        return require(
            authority_parent == "209b4196d5fb0f008c465cc9a1cc8a2045e4967c"
            and claim_parent == AUTHORITY_COMMIT
            and authority_paths == expected_authority
            and claim_paths == expected_claim,
            "published authority/claim graph",
        )

    add_case("published authority and full claim commit graph", authority_and_claim)

    def bound_files_at_authority() -> bool:
        for binding in HANDOFF["source_bindings"]:
            source_commit = (
                "209b4196d5fb0f008c465cc9a1cc8a2045e4967c"
                if binding["path"]
                == "coordination/experiment-reserve/BATCH-45b4d5/dispatch_queue.json"
                else AUTHORITY_COMMIT
            )
            blob = git("show", f"{source_commit}:{binding['path']}", binary=True)
            require(sha256_bytes(blob) == binding["sha256"], f"authority blob {binding['path']}")
        return True

    add_case("all 73 bindings exist byte-identically at published authority", bound_files_at_authority)

    def producer_root_receipt_summary() -> bool:
        receipt = PRODUCER_RECEIPT
        invocation = receipt["invocations"][0]
        result = invocation["result"]
        return require(
            receipt["delegated_executed_cases"] == 0
            and receipt["root_executed_cases"] == 208
            and receipt["total_fixed_cases_including_parameters_failures_and_reruns"] == 208
            and receipt["maximum_fixed_cases"] == 512
            and receipt["suite_invocations"] == 1
            and receipt["failed_case_executions"] == 0
            and receipt["rerun_case_executions"] == 0
            and receipt["scientific_runs"] == 0
            and result["planned_cases"] == result["executed_cases"] == result["passed"] == 208
            and result["failed"] == 0,
            "producer root suite totals",
        )

    add_case("producer delegated-zero and root 208-of-208 accounting", producer_root_receipt_summary)

    def producer_case_chronology() -> bool:
        cases = PRODUCER_RECEIPT["invocations"][0]["result"]["cases"]
        require([case["ordinal"] for case in cases] == list(range(1, 209)), "producer ordinals")
        for case in cases:
            start = dt.datetime.fromisoformat(case["started_at_UTC"].replace("Z", "+00:00"))
            end = dt.datetime.fromisoformat(case["ended_at_UTC"].replace("Z", "+00:00"))
            require(end >= start, "producer case UTC order")
            require(case["wall_seconds"] <= 10 and case["cpu_seconds"] <= 10, "producer per-case limit")
            require(case["status"] == "passed", "producer case status")
        return True

    add_case("all 208 producer cases retain ordered absolute UTC and per-case telemetry", producer_case_chronology)

    def producer_invocation_chronology() -> bool:
        invocation = PRODUCER_RECEIPT["invocations"][0]
        reservation = invocation["prospective_reservation"]
        custody = invocation["command_custody"]
        result = invocation["result"]
        reserved = dt.datetime.fromisoformat(reservation["reserved_at_UTC"].replace("Z", "+00:00"))
        command_start = dt.datetime.fromisoformat(custody["started_at_UTC"].replace("Z", "+00:00"))
        command_end = dt.datetime.fromisoformat(custody["ended_at_UTC"].replace("Z", "+00:00"))
        inner_start = dt.datetime.fromisoformat(result["started_at_UTC"].replace("Z", "+00:00"))
        inner_end = dt.datetime.fromisoformat(result["ended_at_UTC"].replace("Z", "+00:00"))
        return require(
            reserved <= command_start <= inner_start <= inner_end <= command_end
            and reservation["reserved_cases"] == 208
            and reservation["prior_cases"] == 0
            and reservation["final_reserve"] == 208
            and custody["exit_code"] == 0,
            "producer reservation/invocation chronology",
        )

    add_case("producer reservation precedes sole root invocation", producer_invocation_chronology)

    def producer_authority_precedes_invocation() -> bool:
        decision_commit = git("log", "-1", "--format=%H", "--", "ledger/decisions/DEC-20260908-d799ba.yaml")
        operational_commit = git("log", "-1", "--format=%H", "--", "ledger/decisions/DEC-20260908-470b28.yaml")
        decision_time = dt.datetime.fromisoformat(git("show", "-s", "--format=%cI", decision_commit))
        operational_time = dt.datetime.fromisoformat(git("show", "-s", "--format=%cI", operational_commit))
        reserved = dt.datetime.fromisoformat(
            PRODUCER_RECEIPT["invocations"][0]["prospective_reservation"]["reserved_at_UTC"]
        )
        return require(
            decision_commit == "8e7f49ae40ad98030ad0da811f47218e3764db0d"
            and operational_commit == "799071497ecf7e22280f172c02dbae4da911e15f"
            and decision_time < operational_time < reserved,
            "published decisions precede root suite",
        )

    add_case("DEC-d799ba and DEC-470b28 precede root invocation", producer_authority_precedes_invocation)

    def producer_external_telemetry() -> bool:
        invocation = PRODUCER_RECEIPT["invocations"][0]
        telemetry = invocation["external_telemetry"]
        result = invocation["result"]
        return require(
            telemetry["wall_seconds"] == 13.94
            and telemetry["aggregate_cpu_seconds"] == 11.71
            and telemetry["maximum_observed_rss_bytes"] == 67846144
            and result["wall_seconds"] < MAX_AGGREGATE_SECONDS
            and result["cpu_seconds"] < MAX_AGGREGATE_SECONDS
            and result["memory_limit"]["attempted"] is True
            and result["memory_limit"]["enforced"] is False
            and result["memory_limit"]["error"]
            == "ValueError: current limit exceeds maximum limit",
            "producer external telemetry and failed RLIMIT_AS",
        )

    add_case("producer external wall/CPU/RSS and failed Darwin memory enforcement retained", producer_external_telemetry)

    def producer_hashes_and_integration() -> bool:
        receipt = PRODUCER_RECEIPT
        integration = receipt["root_integration"]
        final_hashes = receipt["final_nonreceipt_hashes"]
        paths = {
            "EXP-ECDLP-1b1b99.yaml": CONTRACT_PATH,
            "schema.json": SCHEMA_PATH,
            "checks.py": PRODUCER_CHECKER_PATH,
            "readiness.md": PRODUCER_READINESS_PATH,
        }
        return require(
            integration["integer_keys_restored"] == 7
            and len(integration["unchanged_sections"]) == 23
            and integration["changed_sections"] == ["cost_contract", "artifact_custody"]
            and all(final_hashes[name] == sha256_file(path) for name, path in paths.items()),
            "producer final hashes and integer restoration",
        )

    add_case("producer final hashes, seven integer keys, and 23 unchanged sections", producer_hashes_and_integration)

    def predecessor_chronology_gap() -> bool:
        receipt = read_json(
            REPO
            / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-5e3d88/check-receipt.json"
        )
        serialized = canonical(receipt)
        return require(
            "started_at_UTC" not in serialized
            and "ended_at_UTC" not in serialized
            and receipt["case_accounting"]["total_case_attempts"] == 246,
            "historical chronology gap remains",
        )

    add_case("predecessor 246-case receipt still lacks absolute suite chronology", predecessor_chronology_gap)


def register_contract_structure_cases() -> None:
    add_case(
        "fifth contract remains unapproved and performs no science",
        lambda: require(
            CONTRACT["approved_by"] is None
            and CONTRACT["execution_authorized"] is False
            and CONTRACT["evidence_eligible"] is False
            and CONTRACT["scientific_run_performed"] is False
            and CONTRACT["implementation_change_performed"] is False,
            "prospective-only flags",
        ),
    )

    def effective_section_diff() -> bool:
        before = PREDECESSOR["effective_contract"]
        after = CONTRACT["effective_contract"]
        changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
        OBSERVATIONS["effective_contract_changed_sections"] = sorted(changed)
        return require(changed == {"cost_contract", "artifact_custody"}, "effective section diff")

    add_case("exact parsed effective-contract diff changes only two sections", effective_section_diff)

    def scientific_sections_unchanged() -> bool:
        names = PRODUCER_RECEIPT["root_integration"]["unchanged_sections"]
        require(len(names) == 23 and len(set(names)) == 23, "23 section names")
        for name in names:
            require(
                PREDECESSOR["effective_contract"][name] == CONTRACT["effective_contract"][name],
                f"unchanged scientific section {name}",
            )
        return True

    add_case("all 23 declared scientific sections are parsed-object identical", scientific_sections_unchanged)
    add_case(
        "seven fixed arm identifiers retain integer key types",
        lambda: require(
            list(EFFECTIVE["arms"]["fixed_arm_ids"].keys()) == list(range(1, 8))
            and all(type(key) is int for key in EFFECTIVE["arms"]["fixed_arm_ids"]),
            "integer arm-map keys",
        ),
    )
    add_case(
        "original seeds q arms and 36-cell governing boundary remain represented",
        lambda: require(
            EFFECTIVE["test_boundary"]["selection_seed"] == 606101
            and EFFECTIVE["test_boundary"]["confirmation_seed"] == 606103
            and EFFECTIVE["test_boundary"]["q_values"] == Q_VALUES
            and EFFECTIVE["timing_matrix"]["required_values"]["arm_values"] == list(range(1, 8))
            and COST["primary_ratio"]["governing_cell_count"] == 36
            and "606101" in ORIGINAL["algorithms"]["baseline"]
            and "606103" in ORIGINAL["algorithms"]["baseline"],
            "original finite boundary",
        ),
    )
    add_case(
        "Med7 Med6 ratio q-star and thresholds remain exact",
        lambda: require(
            COST["exact_reducers"]["Med7"].startswith("Sort seven exact rational")
            and COST["exact_reducers"]["Med6"].startswith("Sort six exact rational")
            and COST["primary_ratio"]["direction"] == "scalar_total_divided_by_transport_total"
            and COST["q_star"]["ladder"] == Q_VALUES
            and "1.20" in EFFECTIVE["predictions"]["positive"]
            and "1.00" in EFFECTIVE["predictions"]["scoped_negative"],
            "numeric definitions",
        ),
    )
    add_case("independent Med7 repeated values", lambda: require(med7([Fraction(x) for x in [9, 1, 3, 3, 7, 5, 11]]) == 5, "Med7"))
    add_case("independent Med6 central mean", lambda: require(med6([Fraction(x) for x in [9, 1, 3, 7, 5, 11]]) == 6, "Med6"))
    add_case(
        "ratio of totals differs from mean of endpoint ratios",
        lambda: require(
            Fraction(sum([1, 1, 9, 9]), sum([1, 1, 3, 3])) == Fraction(5, 2)
            and sum(Fraction(a, b) for a, b in zip([1, 1, 9, 9], [1, 1, 3, 3])) / 4 == 2,
            "ratio-of-totals witness",
        ),
    )
    add_case("q-star first rung", lambda: require(q_star({1: Fraction(1), 16: Fraction(2), 256: Fraction(2), 4096: Fraction(2)}) == 1, "q-star first"))
    add_case("q-star later rung", lambda: require(q_star({1: Fraction(1, 2), 16: Fraction(3, 4), 256: Fraction(1), 4096: Fraction(2)}) == 256, "q-star later"))
    add_case("q-star no crossing", lambda: require(q_star({q: Fraction(1, 2) for q in Q_VALUES}) == ">4096", "q-star no crossing"))
    add_case("q-star missing earlier rung", lambda: require(q_star({1: Fraction(1, 2), 16: None, 256: Fraction(2), 4096: Fraction(2)}) == "unresolved", "q-star unresolved"))


def register_component_and_allocation_cases() -> None:
    add_case(
        "46 unique component rows equal the canonical registry",
        lambda: require(
            len(CROSSWALK) == 46
            and len(CROSSWALK_BY_COMPONENT) == 46
            and set(CROSSWALK_BY_COMPONENT)
            == set(COST["component_registry"]["canonical_components"]),
            "component registry coverage",
        ),
    )
    arm_rows = {
        row["component"]: row["allowed_plane_arm"]
        for row in CROSSWALK
        if isinstance(row["allowed_plane_arm"], list)
    }
    add_case(
        "exactly 17 arm-context rows and schema relation keys agree",
        lambda: require(
            len(arm_rows) == 17
            and arm_rows == COMPONENT_RELATION,
            "arm-context relation identity",
        ),
    )

    for component, relation_rows in COMPONENT_RELATION.items():
        for relation in relation_rows:
            for arm in relation["arms"]:
                add_case(
                    f"required component relation {component}/{relation['plane']}/arm{arm}",
                    lambda component=component, relation=relation, arm=arm: schema_accepts(
                        raw_row(component, relation=relation, arm=arm)
                    ),
                )

    possible = [(plane, arm) for plane in ["main", "selection"] for arm in range(1, 8)]
    for component, relation_rows in COMPONENT_RELATION.items():
        allowed = {
            (relation["plane"], arm)
            for relation in relation_rows
            for arm in relation["arms"]
        }
        wrong_plane, wrong_arm = next(pair for pair in possible if pair not in allowed)
        add_case(
            f"known-invalid component relation rejected {component}/{wrong_plane}/arm{wrong_arm}",
            lambda component=component, wrong_plane=wrong_plane, wrong_arm=wrong_arm: schema_rejects(
                {
                    **raw_row(component),
                    "plane": wrong_plane,
                    "arm": wrong_arm,
                    "seed": 606101 if wrong_plane == "selection" else 606103,
                    "q": 256 if wrong_plane == "selection" else 4096,
                }
            ),
        )

    for row in CROSSWALK:
        component = row["component"]
        if component not in COMPONENT_RELATION:
            add_case(
                f"non-arm component rejects fabricated arm context {component}",
                lambda component=component: schema_rejects(
                    {**raw_row(component), "plane": "main", "arm": 1}
                ),
            )

    add_case(
        "generic query serialization is admitted for transport and every scalar arm",
        lambda: require(
            all(
                schema_accepts(
                    raw_row(
                        "query_serialization",
                        relation={"plane": "main", "arms": [arm]},
                        arm=arm,
                    )
                )
                for arm in range(1, 8)
            ),
            "generic serialization coverage",
        ),
    )
    add_case(
        "input-output setup conversion is explicitly library-arm-only",
        lambda: require(
            schema_accepts(raw_row("input_output_setup_conversion"))
            and schema_rejects({**raw_row("input_output_setup_conversion"), "arm": 2}),
            "library-only setup conversion",
        ),
    )
    add_case(
        "table setup admits point-independent scalar metadata for arms2-through7",
        lambda: require(
            all(
                schema_accepts(
                    raw_row("table_setup", relation={"plane": "main", "arms": [arm]}, arm=arm)
                )
                for arm in range(2, 8)
            )
            and schema_rejects({**raw_row("table_setup"), "arm": 1}),
            "table setup domains",
        ),
    )
    add_case(
        "top control owner is representable without a quotient endpoint",
        lambda: schema_accepts(raw_row("top_level_control")),
    )
    add_case(
        "identity control owner is representable without a quotient endpoint",
        lambda: schema_accepts(raw_row("identity_transport_control")),
    )
    add_case(
        "top control rejects identity arm and fake endpoint",
        lambda: schema_rejects(
            {
                **raw_row("top_level_control"),
                "owner": {
                    **raw_row("top_level_control")["owner"],
                    "arm": "direct_iota",
                    "endpoint": "K0",
                },
            }
        ),
    )
    add_case(
        "numeric aliases floats and booleans do not enter integer axes",
        lambda: require(
            schema_accepts({**raw_row("scalar_multiplication"), "q": 4096.0})
            and _raises(
                lambda: numeric_lexical_profile(
                    {**raw_row("scalar_multiplication"), "q": 4096.0}
                ),
                ValueError,
            )
            and schema_rejects({**raw_row("scalar_multiplication"), "arm": True}),
            "schema plus mandatory lexical numeric predicate",
        ),
    )
    add_case(
        "strict JSON rejects recursive duplicate keys",
        lambda: require(
            _raises(lambda: strict_json('{"x":{"q":1,"q":16}}'), ValueError),
            "duplicate parser control",
        ),
    )
    add_case(
        "strict JSON rejects nonfinite numeric tokens",
        lambda: require(
            _raises(lambda: strict_json('{"x":NaN}'), ValueError),
            "nonfinite parser control",
        ),
    )

    context = fixed_context()

    def global_graph() -> bool:
        row = raw_row("global_library_initialization", cpu=73, wall=77)
        row["capture_interval"]["cpu_finished_ns"] = 73
        row["capture_interval"]["wall_finished_ns"] = 77
        edges = make_edges(row, context)
        require(len(edges) == 9 * 72, "global 9-view x 72-target edge count")
        return check_allocation([row], edges, context)

    add_case("global library full 72-target eight-cold-plus-candidate7 graph", global_graph)

    def broken_global(transform: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]) -> bool:
        row = raw_row("global_library_initialization", cpu=73, wall=77)
        row["capture_interval"]["cpu_finished_ns"] = 73
        row["capture_interval"]["wall_finished_ns"] = 77
        edges = transform(make_edges(row, context))
        return require(_raises(lambda: check_allocation([row], edges, context), (AssertionError, jsonschema.ValidationError)), "broken global rejected")

    add_case(
        "global charge cannot shrink to one eight-endpoint stratum",
        lambda: broken_global(
            lambda edges: [
                edge
                for edge in edges
                if edge["target"].get("fixture", "").startswith("I0")
                and edge["target"].get("coordinate") == 1
            ]
        ),
    )
    add_case(
        "global allocation missing target is rejected",
        lambda: broken_global(lambda edges: edges[:-1]),
    )
    add_case(
        "global allocation duplicate target is rejected",
        lambda: broken_global(lambda edges: edges + [copy.deepcopy(edges[-1])]),
    )

    def move_remainder(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        moved = copy.deepcopy(edges)
        moved[0]["allocated_CPU_nanoseconds"] -= 1
        moved[1]["allocated_CPU_nanoseconds"] += 1
        return moved

    add_case("global canonical integer remainder cannot move", lambda: broken_global(move_remainder))

    def change_candidate(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        changed = copy.deepcopy(edges)
        for edge in changed:
            if edge["scenario"]["kind"] == "selection_score":
                edge["scenario"]["candidate_arm"] = 6
        return changed

    add_case("global library score lifetime is candidate7 only", lambda: broken_global(change_candidate))

    def reason_alias(edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
        changed = copy.deepcopy(edges)
        changed[0]["reason_code"] = "actual_only"
        return changed

    add_case("global cold edge cannot use actual-only reason", lambda: broken_global(reason_alias))

    for component in [
        "construct_supplied_public_source_curve",
        "kernel_search",
        "baseline_selection_stratum_overhead",
        "scalar_multiplication",
        "transport_warmup",
        "reporting_and_artifact_publication",
    ]:
        add_case(
            f"complete edge groups for representative {component}",
            lambda component=component: check_allocation(
                [raw_row(component)], make_edges(raw_row(component), context), context
            ),
        )

    def nonwinner_actual_only() -> bool:
        row = raw_row("scalar_multiplication")
        row["arm"] = 3
        edges = make_edges(row, context)
        return require(
            len(edges) == 1
            and edges[0]["strategy_view"] == "actual_only_scaffolding"
            and check_allocation([row], edges, context),
            "nonwinner actual-only path",
        )

    add_case("nonprimary actual main arm is physical-only", nonwinner_actual_only)

    def unavailable_actual_only() -> bool:
        row = raw_row("kernel_search", status="partial", cpu=None, wall=None)
        edges = make_edges(row, context)
        return require(
            len(edges) == 1
            and edges[0]["allocated_CPU_nanoseconds"] is None
            and edges[0]["allocated_CPU_unavailable_reason"] == "capture_failed"
            and check_allocation([row], edges, context),
            "unavailable actual-only path",
        )

    add_case("partial unavailable physical charge stays null with reason", unavailable_actual_only)

    def actual_physical_sum_not_view_sum() -> bool:
        row = raw_row("global_library_initialization", cpu=73, wall=77)
        edges = make_edges(row, context)
        actual_cpu = sum(item["CPU_nanoseconds"] for item in [row] if item["charge_kind"] == "exclusive_leaf")
        view_cpu = sum(edge["allocated_CPU_nanoseconds"] for edge in edges)
        return require(actual_cpu == 73 and view_cpu == 9 * 73, "physical versus alternative views")

    add_case("actual campaign charges physical event once despite nine alternative views", actual_physical_sum_not_view_sum)


def _raises(function: Callable[[], Any], exceptions: type[BaseException] | tuple[type[BaseException], ...]) -> bool:
    try:
        function()
    except exceptions:
        return True
    return False


def register_inference_manifest_and_loo_cases() -> None:
    add_case("exact deterministic writer default block is admitted", lambda: schema_accepts({**base_manifest(), "run": {**base_manifest()["run"], "inference": deterministic_writer_block()}}))
    add_case("exact deterministic writer empty custom note is admitted", lambda: schema_accepts({**base_manifest(), "run": {**base_manifest()["run"], "inference": deterministic_writer_block("")}}))
    add_case("literal policy resolution failed note without error remains deterministic", lambda: schema_accepts({**base_manifest(), "run": {**base_manifest()["run"], "inference": deterministic_writer_block("policy resolution failed")}}))
    add_case("normal model writer shape is admitted", lambda: schema_accepts({**base_manifest(), "run": {**base_manifest()["run"], "inference": model_inference_block()}}))
    add_case("typed policy-resolution writer branch is admitted only on refusal outcome", lambda: validate_manifest_semantics(outcome_manifest("POLICY_RESOLUTION_FAILED")))

    def resolution_cannot_be_completed_valid() -> bool:
        document = complete_manifest()
        document["run"]["inference"] = outcome_manifest("POLICY_RESOLUTION_FAILED")["run"]["inference"]
        return schema_rejects(document)

    add_case("resolution error cannot become completed-valid science", resolution_cannot_be_completed_valid)

    add_case("complete 288-cell 8-global 36-qstar manifest", lambda: validate_manifest_semantics(complete_manifest()))

    for code in OUTCOME_BY_CODE:
        add_case(
            f"closed outcome admitted {code}",
            lambda code=code: validate_manifest_semantics(outcome_manifest(code)),
        )

        def wrong_status(code: str = code) -> bool:
            document = outcome_manifest(code)
            current = document["run"]["status"]
            document["run"]["status"] = next(
                candidate
                for candidate in [
                    "completed_valid",
                    "completed_invalid",
                    "partial_inconclusive",
                    "refused_before_run",
                    "infrastructure_stopped",
                ]
                if candidate != current
            )
            return schema_rejects(document)

        add_case(f"wrong status rejected {code}", wrong_status)

    add_case(
        "arbitrary banana reason rejected",
        lambda: schema_rejects(
            {
                **base_manifest(),
                "run": {
                    **base_manifest()["run"],
                    "result": {
                        **base_manifest()["run"]["result"],
                        "reason_code": "banana",
                        "invalid_reason": "banana",
                    },
                },
            }
        ),
    )
    add_case(
        "missing resource reason rejected",
        lambda: require(
            schema_accepts(
                {
                    **base_manifest(),
                    "run": {
                        **base_manifest()["run"],
                        "resources": {
                            **base_manifest()["run"]["resources"],
                            "peak_rss_unavailable_reason": None,
                        },
                    },
                }
            )
            and _raises(
                lambda: resource_reason_profile(
                    {
                        **base_manifest(),
                        "run": {
                            **base_manifest()["run"],
                            "resources": {
                                **base_manifest()["run"]["resources"],
                                "peak_rss_unavailable_reason": None,
                            },
                        },
                    }
                ),
                AssertionError,
            ),
            "schema plus mandatory resource-reason predicate",
        ),
    )
    add_case(
        "completed-valid failed-control object rejected",
        lambda: schema_rejects(
            {
                **complete_manifest(),
                "run": {
                    **complete_manifest()["run"],
                    "result": {
                        **complete_manifest()["run"]["result"],
                        "reason_code": "CONTROL_FAILED",
                        "invalid_reason": "CONTROL_FAILED",
                        "valid": False,
                    },
                },
            }
        ),
    )

    def no_typed_pre_run_refusal_union() -> bool:
        top_level_defs = set(SCHEMA["$defs"])
        top_level_variants = SCHEMA["oneOf"]
        refs = {variant.get("$ref") for variant in top_level_variants}
        required_refusal = {
            "refusal": {
                "status": "refused_before_run",
                "reason_code": "AUTH_MALFORMED",
                "stage": "authorize_and_claim_nonce",
                "detail": "fixed malformed bytes",
            }
        }
        require("refusal" not in top_level_defs and "typed_refusal" not in top_level_defs, "no refusal definition")
        require(refs == {"#/$defs/raw_cost", "#/$defs/allocation_edge", "#/$defs/manifest"}, "three-entry carrier union")
        require(schema_rejects(required_refusal), "standalone typed refusal is not representable")
        OBSERVATIONS["pre_run_refusal_interface"] = {
            "top_level_refs": sorted(refs),
            "standalone_AUTH_MALFORMED_rejected": True,
            "missing_definitions": ["refusal", "typed_refusal"],
        }
        return True

    add_case("breaking control: standalone AUTH_MALFORMED typed refusal has no schema branch", no_typed_pre_run_refusal_union)

    def full_manifest_demands_invented_pre_run_fields() -> bool:
        document = outcome_manifest("AUTH_MALFORMED")
        require(schema_accepts(document), "fully populated refusal manifest passes")
        required = set(SCHEMA["$defs"]["manifest"]["properties"]["run"]["required"])
        demanded = {"id", "code", "inputs", "timing", "resources", "directory", "admission"}
        require(demanded <= required, "full manifest pre-run demanded fields")
        for field in sorted(demanded):
            broken = copy.deepcopy(document)
            del broken["run"][field]
            require(schema_rejects(broken), f"missing pre-run field rejected {field}")
        OBSERVATIONS["pre_run_full_manifest_required_fields"] = sorted(demanded)
        return True

    add_case("breaking control: AUTH_MALFORMED full manifest requires allocated/source/custody fields", full_manifest_demands_invented_pre_run_fields)

    items, endpoints = loo_source()
    add_case("labelled fractional LOO jointly recomputes both strategies and endpoints", lambda: check_loo(items, endpoints))
    add_case("whole labelled LOO item permutation is harmless", lambda: check_loo(list(reversed(items)), endpoints))
    add_case(
        "LOO missing label rejected",
        lambda: require(_raises(lambda: check_loo(items[:-1], endpoints), AssertionError), "missing label"),
    )
    add_case(
        "LOO duplicate label rejected",
        lambda: require(_raises(lambda: check_loo(items[:-1] + [items[0]], endpoints), AssertionError), "duplicate label"),
    )

    def relabel_value() -> bool:
        changed = copy.deepcopy(items)
        changed[0]["omitted_block"], changed[6]["omitted_block"] = 6, 0
        return require(_raises(lambda: check_loo(changed, endpoints), AssertionError), "label/value substitution")

    add_case("LOO label-value substitution rejected", relabel_value)

    def unilateral_endpoint_deletion() -> bool:
        changed = copy.deepcopy(endpoints)
        del changed[0]["transport"]["blocks"][6]
        return require(_raises(lambda: check_loo(items, changed), AssertionError), "unilateral block deletion")

    add_case("one endpoint cannot delete a different block", unilateral_endpoint_deletion)

    def manifest_loo_permutation() -> bool:
        document = complete_manifest()
        for cell in document["run"]["result"]["metrics"]["R_cells"]:
            cell["leave_one_out"].reverse()
        return validate_manifest_semantics(document)

    add_case("manifest LOO array-order permutation preserves labels", manifest_loo_permutation)

    def manifest_loo_duplicate() -> bool:
        document = complete_manifest()
        cell = next(
            row
            for row in document["run"]["result"]["metrics"]["R_cells"]
            if row["leave_one_out"]
        )
        cell["leave_one_out"][0]["omitted_block"] = 1
        return schema_rejects(document)

    add_case("manifest duplicate omitted-block identity rejected", manifest_loo_duplicate)

    def costs_csv_round_trip() -> bool:
        row = raw_row("reporting_and_artifact_publication")
        edge = make_edges(row, fixed_context())[0]
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["record_type", "record_json"])
        for value in [row, edge]:
            writer.writerow([value["record_type"], canonical(value)])
        stream.seek(0)
        parsed = list(csv.reader(stream))
        require(parsed[0] == ["record_type", "record_json"], "CSV header")
        for record_type, text in parsed[1:]:
            value = strict_json(text)
            require(value["record_type"] == record_type, "CSV record type identity")
            VALIDATOR.validate(value)
        return True

    add_case("canonical two-column costs CSV round trip", costs_csv_round_trip)


def register_cases() -> None:
    register_source_and_custody_cases()
    register_contract_structure_cases()
    register_component_and_allocation_cases()
    register_inference_manifest_and_loo_cases()


def attempt_memory_limit() -> dict[str, Any]:
    result: dict[str, Any] = {
        "requested_bytes": MEMORY_LIMIT_BYTES,
        "attempted": True,
        "enforced": False,
    }
    try:
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
        result["enforced"] = True
    except (OSError, ValueError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
    return result


def execute_cases(
    reserved_cases: int,
    selected: list[tuple[int, str, Callable[[], bool]]] | None = None,
) -> dict[str, Any]:
    suite_started_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    wall_started = time.perf_counter()
    cpu_started = time.process_time()
    memory_limit = attempt_memory_limit()
    results: list[dict[str, Any]] = []

    def alarm_handler(signum: int, frame: Any) -> None:
        raise TimeoutError("fixed case exceeded 10 seconds")

    signal.signal(signal.SIGALRM, alarm_handler)
    selected_cases = selected or [
        (ordinal, name, function)
        for ordinal, (name, function) in enumerate(CASES, 1)
    ]
    for ordinal, name, function in selected_cases:
        require(time.perf_counter() - wall_started <= MAX_AGGREGATE_SECONDS, "aggregate wall limit")
        require(time.process_time() - cpu_started <= MAX_AGGREGATE_SECONDS, "aggregate CPU limit")
        case = {
            "ordinal": ordinal,
            "name": name,
            "started_at_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
            "status": "started",
        }
        case_wall = time.perf_counter()
        case_cpu = time.process_time()
        signal.alarm(CASE_TIMEOUT_SECONDS)
        try:
            require(function(), name)
            case["status"] = "passed"
        except BaseException as exc:
            case["status"] = "failed"
            case["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            signal.alarm(0)
            case["ended_at_UTC"] = dt.datetime.now(dt.timezone.utc).isoformat()
            case["wall_seconds"] = time.perf_counter() - case_wall
            case["cpu_seconds"] = time.process_time() - case_cpu
            results.append(case)

    wall_seconds = time.perf_counter() - wall_started
    cpu_seconds = time.process_time() - cpu_started
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    passed = sum(case["status"] == "passed" for case in results)
    failed = len(results) - passed
    return {
        "schema": "crypto.autoresearch.independent_definition_check.v1",
        "task_id": TASK_ID,
        "kind": "independent_fixed_definition_checks_only",
        "started_at_UTC": suite_started_utc,
        "ended_at_UTC": dt.datetime.now(dt.timezone.utc).isoformat(),
        "pre_reserved_cases": reserved_cases,
        "planned_cases": len(CASES),
        "selected_cases": len(selected_cases),
        "executed_cases": len(results),
        "passed": passed,
        "failed": failed,
        "cases": results,
        "wall_seconds": wall_seconds,
        "cpu_seconds": cpu_seconds,
        "memory_limit": memory_limit,
        "peak_rss_native": peak_rss,
        "peak_rss_bytes": peak_rss if sys.platform == "darwin" else peak_rss * 1024,
        "rss_units": "bytes on Darwin; KiB on Linux",
        "workers": 1,
        "scientific_runs": 0,
        "producer_checker_imported_or_executed": False,
        "jsonschema_version": __import__("importlib.metadata", fromlist=["version"]).version("jsonschema"),
        "observations": OBSERVATIONS,
        "hashes": {
            "handoff": sha256_file(HANDOFF_PATH),
            "review_plan": sha256_file(PLAN_PATH),
            "fifth_contract": sha256_file(CONTRACT_PATH),
            "fifth_schema": sha256_file(SCHEMA_PATH),
            "producer_checker_read_only": sha256_file(PRODUCER_CHECKER_PATH),
            "producer_receipt": sha256_file(PRODUCER_RECEIPT_PATH),
            "review_checker": sha256_file(Path(__file__)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", action="store_true")
    parser.add_argument("--reserved-cases", type=int)
    parser.add_argument("--prior-attempts", type=int, default=0)
    parser.add_argument("--final-reserve", type=int, default=0)
    parser.add_argument("--only-ordinals", type=str)
    arguments = parser.parse_args()
    register_cases()
    if arguments.count:
        print(
            json.dumps(
                {
                    "task_id": TASK_ID,
                    "planned_cases": len(CASES),
                    "executed_cases": 0,
                    "case_names": [name for name, _ in CASES],
                },
                indent=2,
            )
        )
        return 0
    selected = None
    if arguments.only_ordinals:
        ordinals = [int(value) for value in arguments.only_ordinals.split(",")]
        if len(ordinals) != len(set(ordinals)):
            parser.error("targeted ordinals must be unique")
        selected = [
            (ordinal, CASES[ordinal - 1][0], CASES[ordinal - 1][1])
            for ordinal in ordinals
            if 1 <= ordinal <= len(CASES)
        ]
        if len(selected) != len(ordinals):
            parser.error("targeted ordinal outside complete suite")
    expected_reservation = len(selected) if selected is not None else len(CASES)
    if arguments.reserved_cases != expected_reservation:
        parser.error("--reserved-cases must equal selected case count")
    if arguments.prior_attempts + arguments.reserved_cases + arguments.final_reserve > MAX_CASES:
        parser.error("cumulative 640-case limit exceeded")
    result = execute_cases(arguments.reserved_cases, selected)
    result["command"] = sys.argv
    result["prior_attempts"] = arguments.prior_attempts
    result["final_reserve"] = arguments.final_reserve
    print(json.dumps(result, indent=2))
    return int(result["failed"] != 0 or result["executed_cases"] != result["selected_cases"])


if __name__ == "__main__":
    raise SystemExit(main())
