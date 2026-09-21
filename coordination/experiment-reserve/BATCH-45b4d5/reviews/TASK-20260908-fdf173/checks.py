#!/usr/bin/env python3
"""Independent fixed definition checks for TASK-20260908-fdf173.

This checker is independently authored from the frozen contract and schema.  It
does not import or execute the producer checker, a scientific runner, Sage, or
PARI.  All generated objects are fixed benign JSON/YAML metadata or exact
integer/rational arithmetic.  The single suite has 120 explicitly charged
cases; source hashing and source parsing are recorded separately by the review
receipt and are not hidden here as cases.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import resource
import signal
import sys
import time
from datetime import datetime
from fractions import Fraction
from importlib.metadata import version
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
CONTRACT_PATH = ROOT / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-5e3d88/EXP-ECDLP-1b1b99.yaml"
SCHEMA_PATH = ROOT / "coordination/experiment-reserve/BATCH-45b4d5/corrections/TASK-20260908-5e3d88/schema.json"
HANDOFF_PATH = ROOT / "ledger/handoffs/TASK-20260908-fdf173.yaml"


class DuplicateKey(ValueError):
    pass


class StrictSafeLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise DuplicateKey(f"duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


StrictSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def strict_yaml(text: str):
    return yaml.load(text, Loader=StrictSafeLoader)


class FloatToken:
    def __init__(self, token: str):
        self.token = token


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def strict_json(text: str, record_kind: str):
    def bad_constant(token):
        raise ValueError(f"nonfinite JSON number: {token}")

    value = json.loads(
        text,
        object_pairs_hook=_unique_pairs,
        parse_float=FloatToken,
        parse_constant=bad_constant,
    )
    allowed_float_paths = {
        ("run", "timing", "wall_seconds"),
        ("run", "resources", "cpu_seconds"),
    } if record_kind == "manifest" else set()

    def convert(item, path=()):
        if isinstance(item, FloatToken):
            if path not in allowed_float_paths:
                raise ValueError(f"floating lexical number forbidden at {path}: {item.token}")
            number = float(item.token)
            if not math.isfinite(number):
                raise ValueError(f"nonfinite display number at {path}")
            return number
        if isinstance(item, dict):
            return {key: convert(child, path + (key,)) for key, child in item.items()}
        if isinstance(item, list):
            return [convert(child, path + (index,)) for index, child in enumerate(item)]
        return item

    return convert(value)


CONTRACT = strict_yaml(CONTRACT_PATH.read_text(encoding="utf-8"))
SCHEMA = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
EFFECTIVE = CONTRACT["effective_contract"]
COST = EFFECTIVE["cost_contract"]
COMPONENT_ROWS = COST["component_crosswalk"]["rows"]
COMPONENT_BY_NAME = {row["component"]: row for row in COMPONENT_ROWS}


def validator_for(definition: str):
    wrapper = {
        "$schema": SCHEMA["$schema"],
        "$defs": SCHEMA["$defs"],
        "$ref": f"#/$defs/{definition}",
    }
    return Draft202012Validator(wrapper, format_checker=FormatChecker())


VALIDATORS = {name: validator_for(name) for name in ("raw_cost", "allocation_edge", "manifest")}


def schema_valid(definition: str, value) -> bool:
    return not list(VALIDATORS[definition].iter_errors(value))


def canonical_fraction(value) -> bool:
    return (
        isinstance(value, dict)
        and type(value.get("numerator")) is int
        and type(value.get("denominator")) is int
        and value["numerator"] >= 0
        and value["denominator"] > 0
        and math.gcd(value["numerator"], value["denominator"]) == 1
    )


def resource_pair_ok(value, reason) -> bool:
    return (type(value) is int and value >= 0 and reason is None) or (
        value is None and isinstance(reason, str) and bool(reason)
    )


FIXTURES = ["I0F0", "I0F1", "I1F0", "I1F1", "I2F0", "I2F1"]
ENDPOINTS = ["K0", "K1", "K2", "K3"]
COORDINATES = [1, 2, 3]
SEEDS = [606101, 606103]
QS = [1, 16, 256, 4096]
ARMS = list(range(1, 8))
BLOCKS = list(range(7))


def scientific_owner(scope: str):
    values = {
        "global": {"scope": "global"},
        "interval": {"scope": "interval", "interval": "I0"},
        "fixture": {"scope": "fixture", "fixture": "I0F0"},
        "kernel": {"scope": "kernel", "fixture": "I0F0", "kernel": "K0"},
        "class": {"scope": "class", "fixture": "I0F0", "class": "C0"},
        "endpoint_coordinate": {
            "scope": "endpoint_coordinate", "fixture": "I0F0",
            "endpoint": "K0", "coordinate": 1,
        },
        "selection_stratum": {
            "scope": "selection_stratum", "interval": "I0", "coordinate": 1,
        },
        "arm_workload": {
            "scope": "arm_workload", "fixture": "I0F0", "endpoint": "K0",
            "coordinate": 1, "plane": "main", "seed": 606103, "q": 4096,
            "arm": 1,
        },
        "timing_block": {
            "scope": "timing_block", "fixture": "I0F0", "endpoint": "K0",
            "coordinate": 1, "plane": "main", "seed": 606103, "q": 4096,
            "arm": 1, "block": 0,
        },
        "block_repetition": {
            "scope": "block_repetition", "fixture": "I0F0", "endpoint": "K0",
            "coordinate": 1, "plane": "main", "seed": 606103, "q": 4096,
            "arm": 1, "block": 0, "repetition": 1,
        },
    }
    return copy.deepcopy(values[scope])


def component_owner(component: str):
    if component == "top_level_control":
        return {
            "scope": "control_block", "fixture": "I0F0", "coordinate": 1,
            "plane": "top_control", "seed": 606103, "q": 4096,
            "arm": "direct_3_iota", "block": 0,
        }
    if component == "identity_transport_control":
        return {
            "scope": "control_block", "fixture": "I0F0", "coordinate": 1,
            "plane": "identity_control", "seed": 606103, "q": 4096,
            "arm": "direct_iota", "block": 0,
        }
    if component == "reporting_and_artifact_publication":
        return {"scope": "global"}
    return scientific_owner("arm_workload")


def component_arm(component: str) -> int:
    if component in {"psi_evaluation", "iota_evaluation", "phi_evaluation", "transport_warmup"}:
        return 1
    if component in {"library_internal_setup", "library_input_conversion", "library_output_conversion", "library_scalar_conversion"}:
        return 7
    if component in {"scalar_multiplication", "every_per_point_table", "scalar_warmup"}:
        return 2
    return 1


def raw_row(component: str, *, status="complete", charge_kind=None):
    row_def = COMPONENT_BY_NAME[component]
    scope = row_def["allowed_scopes"][0]
    phase = row_def["allowed_phases"][0]
    if charge_kind is None:
        charge_kind = "derived_rollup" if component in {
            "level_and_multiplicity_certificate", "all_six_algorithm_selection_trials"
        } else "exclusive_leaf"
    derived = charge_kind == "derived_rollup"
    row = {
        "record_type": "raw_cost",
        "raw_cost_row_id": f"raw-{component}",
        "physical_event_id": f"event-{component}",
        "event_ordinal": 0,
        "component": component,
        "phase": phase,
        "status": status,
        "CPU_nanoseconds": None if derived else 73,
        "CPU_unavailable_reason": "derived_rollup" if derived else None,
        "wall_nanoseconds": None if derived else 91,
        "wall_unavailable_reason": "derived_rollup" if derived else None,
        "process_group_peak_RSS_bytes": 17,
        "RSS_unavailable_reason": None,
        "operation_counts": None if derived else {"group_additions": 1},
        "operation_counts_unavailable_reason": "derived_rollup" if derived else None,
        "capture_interval": {
            "stream_id": "stream-0",
            "process_group_id": None if derived else 17,
            "cpu_started_ns": None if derived else 10,
            "cpu_finished_ns": None if derived else 20,
            "wall_started_ns": None if derived else 30,
            "wall_finished_ns": None if derived else 40,
            "reason": "derived_rollup" if derived else None,
        },
        "charge_kind": charge_kind,
        "source_leaf_ids": ["leaf-0"] if derived else [],
        "scope": scope,
    }
    if scope == "scaffolding":
        row["scaffold_kind"] = component
        row["owner"] = component_owner(component)
    else:
        owner = scientific_owner(scope)
        row.update({key: value for key, value in owner.items() if key != "scope"})
        if "arm" in row:
            row["arm"] = component_arm(component)
    return row


def raw_semantics(row) -> bool:
    if not schema_valid("raw_cost", row):
        return False
    expected = COMPONENT_BY_NAME.get(row["component"])
    if not expected or row["phase"] not in expected["allowed_phases"] or row["scope"] not in expected["allowed_scopes"]:
        return False
    if row["scope"] == "scaffolding":
        if row["scaffold_kind"] != row["component"]:
            return False
        owner = row["owner"]
        if row["component"] == "top_level_control" and owner.get("plane") != "top_control":
            return False
        if row["component"] == "identity_transport_control" and owner.get("plane") != "identity_control":
            return False
    if row["charge_kind"] == "derived_rollup":
        if len(row["source_leaf_ids"]) != len(set(row["source_leaf_ids"])):
            return False
    elif row["source_leaf_ids"]:
        return False
    for value_key, reason_key in (
        ("CPU_nanoseconds", "CPU_unavailable_reason"),
        ("wall_nanoseconds", "wall_unavailable_reason"),
        ("process_group_peak_RSS_bytes", "RSS_unavailable_reason"),
        ("operation_counts", "operation_counts_unavailable_reason"),
    ):
        value, reason = row[value_key], row[reason_key]
        if value_key == "operation_counts":
            if not ((isinstance(value, dict) and reason is None) or (value is None and isinstance(reason, str))):
                return False
        elif not resource_pair_ok(value, reason):
            return False
        if row["charge_kind"] == "exclusive_leaf" and reason == "derived_rollup":
            return False
    capture = row["capture_interval"]
    for start, finish in (("cpu_started_ns", "cpu_finished_ns"), ("wall_started_ns", "wall_finished_ns")):
        if (capture[start] is None) != (capture[finish] is None):
            return False
        if capture[start] is not None and capture[finish] < capture[start]:
            return False
    return True


def fraction(numerator=1, denominator=1):
    return {"numerator": numerator, "denominator": denominator}


def endpoint_targets():
    return [
        {"kind": "endpoint_coordinate", "fixture": fixture, "endpoint": endpoint, "coordinate": coordinate}
        for fixture in FIXTURES for endpoint in ENDPOINTS for coordinate in COORDINATES
    ]


def allocation_edge(*, row_id="raw-x", view="scalar", scenario=None, target=None,
                    weight=None, cpu=73, wall=91, reason="shared_setup"):
    if scenario is None:
        scenario = {"kind": "cold", "q": 4096, "seed": 606103}
    if target is None:
        target = {"kind": "endpoint_coordinate", "fixture": "I0F0", "endpoint": "K0", "coordinate": 1}
    return {
        "record_type": "allocation_edge",
        "raw_cost_row_id": row_id,
        "weight": weight or fraction(),
        "allocated_CPU_nanoseconds": cpu,
        "allocated_CPU_unavailable_reason": None if cpu is not None else "not_observed_before_stop",
        "allocated_wall_nanoseconds": wall,
        "allocated_wall_unavailable_reason": None if wall is not None else "not_observed_before_stop",
        "reason_code": reason,
        "strategy_view": view,
        "scenario": copy.deepcopy(scenario),
        "target": copy.deepcopy(target),
    }


def allocation_semantics(edge) -> bool:
    if not schema_valid("allocation_edge", edge) or not canonical_fraction(edge["weight"]):
        return False
    if not resource_pair_ok(edge["allocated_CPU_nanoseconds"], edge["allocated_CPU_unavailable_reason"]):
        return False
    if not resource_pair_ok(edge["allocated_wall_nanoseconds"], edge["allocated_wall_unavailable_reason"]):
        return False
    if edge["scenario"]["kind"] == "actual_only":
        if edge["target"].get("raw_cost_row_id") != edge["raw_cost_row_id"]:
            return False
        if edge["weight"] != fraction() or edge["strategy_view"] != "actual_only_scaffolding":
            return False
    if edge["scenario"]["kind"] == "selection_score":
        if edge["scenario"]["candidate_arm"] not in range(2, 8):
            return False
    return True


def split_integer(cost: int, count: int):
    quotient, remainder = divmod(cost, count)
    return [quotient + (index < remainder) for index in range(count)]


def global_library_edges(cost=73):
    targets = endpoint_targets()
    values = split_integer(cost, len(targets))
    return [
        allocation_edge(
            row_id="raw-global-library",
            view="selection_score_candidate",
            scenario={"kind": "selection_score", "candidate_arm": 7},
            target=target,
            weight=fraction(1, 72),
            cpu=values[index],
            wall=values[index],
            reason="selection_score",
        )
        for index, target in enumerate(targets)
    ]


def allocation_group_ok(edges, *, raw_cpu=73, raw_wall=73, expected_targets=None) -> bool:
    if not edges or not all(allocation_semantics(edge) for edge in edges):
        return False
    first = edges[0]
    key = (first["raw_cost_row_id"], first["strategy_view"], json.dumps(first["scenario"], sort_keys=True))
    if any((edge["raw_cost_row_id"], edge["strategy_view"], json.dumps(edge["scenario"], sort_keys=True)) != key for edge in edges):
        return False
    semantic_targets = [json.dumps(edge["target"], sort_keys=True, separators=(",", ":")) for edge in edges]
    if len(semantic_targets) != len(set(semantic_targets)):
        return False
    if expected_targets is not None:
        wanted = [json.dumps(target, sort_keys=True, separators=(",", ":")) for target in expected_targets]
        if semantic_targets != wanted:
            return False
    weight_sum = sum(Fraction(edge["weight"]["numerator"], edge["weight"]["denominator"]) for edge in edges)
    if weight_sum != 1:
        return False
    cpu_expected = split_integer(raw_cpu, len(edges))
    wall_expected = split_integer(raw_wall, len(edges))
    if [edge["allocated_CPU_nanoseconds"] for edge in edges] != cpu_expected:
        return False
    if [edge["allocated_wall_nanoseconds"] for edge in edges] != wall_expected:
        return False
    return True


def reduced_fraction_object(value) -> bool:
    if value.get("kind") != "value":
        return value.get("kind") == "unavailable" and isinstance(value.get("reason"), str)
    return canonical_fraction(value.get("value", {}))


def ratio_value(n=1, d=1):
    return {"kind": "value", "value": fraction(n, d)}


def inference_block_clean():
    return {
        "requested_policy": None,
        "canonical_policy": None,
        "backend": None,
        "provider": None,
        "resolved_model_id": None,
        "model_provenance": "not-applicable",
        "model_verified": True,
        "requested_reasoning_effort": None,
        "reasoning_effort": None,
        "fallback_used": False,
        "fallback_reason": None,
        "degraded_requirements": [],
        "independent_session": False,
        "adapter_version": "1.0.0",
        "config_digest": None,
    }


def complete_metrics(ratio=fraction(1, 1), loo_values=None, branch="exact_finite_cost_gap_only"):
    if loo_values is None:
        loo_values = [fraction(1, 1) for _ in BLOCKS]
    cells = []
    for fixture in FIXTURES:
        for class_id in ("C0", "C1"):
            for coordinate in COORDINATES:
                for seed in SEEDS:
                    for q in QS:
                        governing = seed == 606103 and q == 4096
                        cells.append({
                            "fixture": fixture,
                            "class": class_id,
                            "coordinate": coordinate,
                            "seed": seed,
                            "q": q,
                            "ratio": {"kind": "value", "value": copy.deepcopy(ratio)},
                            "leave_one_out": [
                                {"kind": "value", "value": copy.deepcopy(item)}
                                for item in (loo_values if governing else [])
                            ],
                        })
    global_rows = [
        {"seed": seed, "q": q, "ratio": {"kind": "value", "value": copy.deepcopy(ratio)}}
        for seed in SEEDS for q in QS
    ]
    q_star = [
        {"fixture": fixture, "class": class_id, "coordinate": coordinate,
         "result": {"kind": "crossing", "q": 1}}
        for fixture in FIXTURES for class_id in ("C0", "C1") for coordinate in COORDINATES
    ]
    return {
        "R_cells": cells,
        "R_global": global_rows,
        "q_star": q_star,
        "branch": branch,
        "coverage": {
            "accepted_fixtures": 6,
            "resolved_primary_cells": 36,
            "main_block_rows": 28224,
            "selection_block_rows": 3024,
            "top_block_rows": 2016,
            "identity_block_rows": 2016,
            "all_controls_passed": True,
        },
    }


ARTIFACT_NAMES = [
    "fixtures.json", "raw.jsonl", "controls.json", "costs.csv",
    "certificates.json", "stdout.log", "stderr.log", "report.md",
    "command.txt", "environment.json", "raw-result.json",
]


def manifest(status="completed_valid"):
    completed = status == "completed_valid"
    contract_hash = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
    schema_hash = hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    handoff_hash = hashlib.sha256(HANDOFF_PATH.read_bytes()).hexdigest()
    run_path = "/fixed/review/RUN-ECDLP-abcdef"
    metrics = complete_metrics() if completed else {
        "R_cells": [], "R_global": [], "q_star": [], "branch": "inconclusive",
        "coverage": {
            "accepted_fixtures": 0, "resolved_primary_cells": 0,
            "main_block_rows": 0, "selection_block_rows": 0,
            "top_block_rows": 0, "identity_block_rows": 0,
            "all_controls_passed": False,
        },
    }
    artifacts = {
        name: {"sha256": hashlib.sha256(name.encode()).hexdigest(), "bytes": 1}
        for name in ARTIFACT_NAMES
    } if completed else {}
    return {
        "run": {
            "id": "RUN-ECDLP-abcdef",
            "experiment_id": "EXP-ECDLP-1b1b99",
            "status": status,
            "code": {
                "commit": "a" * 40, "dirty": False, "command": "fixed-review-command",
                "dirty_diff_sha256": None, "source_sha256": {"driver.py": "b" * 64},
            },
            "inference": inference_block_clean(),
            "environment": {
                "operating_system": "fixed-os", "architecture": "fixed-arch",
                "sage_version": None, "python_version": "3.14.3",
                "dependencies": {
                    "runtime-binding": {"version": "fixed", "sha256": "c" * 64, "unavailable_reason": None}
                },
                "runtime_binding_sha256": "b4919db935d24e7ec756daaf9c59cbbf2e663407f2c621b3e752d2b25bded27f",
            },
            "inputs": {
                "curve_id": None, "seed": None,
                "parameters": {
                    "fixture_ids": FIXTURES, "endpoint_ids": ENDPOINTS,
                    "coordinate_values": COORDINATES, "seed_values": SEEDS,
                    "q_values": QS, "arm_values": ARMS, "timing_block_values": BLOCKS,
                    "primary_seed": 606103, "primary_q": 4096,
                    "required_primary_cells": 36,
                    "effective_contract_sha256": contract_hash,
                },
                "fixture_artifact": "fixtures.json",
            },
            "timing": {
                "started_at": "2026-09-08T00:00:00+00:00",
                "finished_at": "2026-09-08T00:00:01+00:00",
                "wall_seconds": 1.0, "wall_nanoseconds": 1_000_000_000,
            },
            "resources": {
                "peak_rss_bytes": 1024 if completed else None,
                "peak_rss_unavailable_reason": None if completed else "not_observed_before_stop",
                "cpu_seconds": 0.5 if completed else None,
                "cpu_nanoseconds": 500_000_000 if completed else None,
                "cpu_unavailable_reason": None if completed else "not_observed_before_stop",
                "measurement_scope": "whole_process_group",
            },
            "result": {
                "metrics": metrics,
                "valid": completed,
                "invalid_reason": None if completed else "AUTH_MALFORMED",
                "certificate": {"kind": "none", "verified": None, "verifier": None},
            },
            "artifacts": artifacts,
            "directory": {
                "path": run_path,
                "path_sha256": hashlib.sha256(run_path.encode()).hexdigest(),
            },
            "admission": {
                "authorization_payload_sha256": "d" * 64,
                "effective_contract_sha256": contract_hash,
                "schema_sha256": schema_hash,
                "handoff_sha256": handoff_hash,
                "implementation_snapshot_commit": "e" * 40,
                "review_archive_commit": "f" * 40,
                "review_report_sha256": "1" * 64,
            },
        }
    }


def manifest_semantics(document) -> bool:
    if not schema_valid("manifest", document):
        return False
    run = document["run"]
    started = datetime.fromisoformat(run["timing"]["started_at"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(run["timing"]["finished_at"].replace("Z", "+00:00"))
    if finished < started:
        return False
    resources = run["resources"]
    if not resource_pair_ok(resources["peak_rss_bytes"], resources["peak_rss_unavailable_reason"]):
        return False
    if not resource_pair_ok(resources["cpu_nanoseconds"], resources["cpu_unavailable_reason"]):
        return False
    expected_contract = hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest()
    expected_schema = hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest()
    expected_handoff = hashlib.sha256(HANDOFF_PATH.read_bytes()).hexdigest()
    if run["inputs"]["parameters"]["effective_contract_sha256"] != expected_contract:
        return False
    if run["admission"]["effective_contract_sha256"] != expected_contract:
        return False
    if run["admission"]["schema_sha256"] != expected_schema or run["admission"]["handoff_sha256"] != expected_handoff:
        return False
    if run["status"] != "completed_valid":
        return run["result"]["valid"] is False and bool(run["result"]["invalid_reason"]) and run["result"]["metrics"]["branch"] == "inconclusive"
    metrics = run["result"]["metrics"]
    expected_cell_keys = {
        (fixture, class_id, coordinate, seed, q)
        for fixture in FIXTURES for class_id in ("C0", "C1")
        for coordinate in COORDINATES for seed in SEEDS for q in QS
    }
    cell_keys = [(row["fixture"], row["class"], row["coordinate"], row["seed"], row["q"]) for row in metrics["R_cells"]]
    if len(cell_keys) != 288 or set(cell_keys) != expected_cell_keys or len(set(cell_keys)) != 288:
        return False
    global_keys = [(row["seed"], row["q"]) for row in metrics["R_global"]]
    if len(global_keys) != 8 or set(global_keys) != {(seed, q) for seed in SEEDS for q in QS}:
        return False
    qstar_keys = [(row["fixture"], row["class"], row["coordinate"]) for row in metrics["q_star"]]
    if len(qstar_keys) != 36 or len(set(qstar_keys)) != 36:
        return False
    for row in metrics["R_cells"]:
        if not reduced_fraction_object(row["ratio"]):
            return False
        governing = row["seed"] == 606103 and row["q"] == 4096
        if len(row["leave_one_out"]) != (7 if governing else 0):
            return False
        if not all(reduced_fraction_object(item) for item in row["leave_one_out"]):
            return False
    if metrics["coverage"] != {
        "accepted_fixtures": 6, "resolved_primary_cells": 36,
        "main_block_rows": 28224, "selection_block_rows": 3024,
        "top_block_rows": 2016, "identity_block_rows": 2016,
        "all_controls_passed": True,
    }:
        return False
    if set(run["artifacts"]) != set(ARTIFACT_NAMES) or any(item["bytes"] <= 0 for item in run["artifacts"].values()):
        return False
    governing = [row for row in metrics["R_cells"] if row["seed"] == 606103 and row["q"] == 4096]
    ratios = [Fraction(row["ratio"]["value"]["numerator"], row["ratio"]["value"]["denominator"]) for row in governing]
    loos = [
        Fraction(item["value"]["numerator"], item["value"]["denominator"])
        for row in governing for item in row["leave_one_out"]
    ]
    if metrics["branch"] == "finite_panel_signal_only":
        return all(value >= Fraction(6, 5) for value in ratios + loos)
    if metrics["branch"] == "exact_finite_cost_gap_only":
        return all(value <= 1 for value in ratios + loos)
    return metrics["branch"] == "inconclusive"


def med7(values):
    if len(values) != 7:
        raise ValueError("Med7 requires seven values")
    return sorted(map(Fraction, values))[3]


def med6(values):
    if len(values) != 6:
        raise ValueError("Med6 requires six values")
    ordered = sorted(map(Fraction, values))
    return (ordered[2] + ordered[3]) / 2


def qstar(values):
    for q in QS:
        if values[q] is None:
            return "unresolved"
        if values[q] >= 1:
            return q
    return "greater_than_4096"


CASES = []


def check(name, function, fixture=None):
    if len(CASES) >= 128:
        raise RuntimeError("case 129 prohibited")
    ordinal = len(CASES) + 1
    started = time.perf_counter()
    cpu_started = time.process_time()
    record = {"ordinal": ordinal, "name": name, "status": "started"}
    if fixture is not None:
        record["fixture"] = fixture
    CASES.append(record)
    signal.alarm(10)
    try:
        observed = function()
        if observed is not True:
            raise AssertionError(f"expected True, observed {observed!r}")
        record["status"] = "passed"
        record["observed"] = True
    except BaseException as exc:
        record["status"] = "failed"
        record["observed"] = False
        record["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        signal.alarm(0)
        record["wall_seconds"] = time.perf_counter() - started
        record["cpu_seconds"] = time.process_time() - cpu_started


def expect_raises(exception, function):
    try:
        function()
    except exception:
        return True
    return False


def run_suite():
    # 1-3: schema/source internal structure.
    check("schema is valid Draft2020-12", lambda: (Draft202012Validator.check_schema(SCHEMA) is None))
    check("contract binds exact schema hash", lambda: CONTRACT["field_precedence"]["schema_binding"]["sha256"] == hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest())
    check("component registry is exactly 46 unique rows", lambda: len(COMPONENT_ROWS) == 46 == len(COMPONENT_BY_NAME) == len(COST["component_registry"]["canonical_components"]) and set(COMPONENT_BY_NAME) == set(COST["component_registry"]["canonical_components"]))

    # 4-49: every component/phase/scope row has a schema-admitted representative.
    for component in COST["component_registry"]["canonical_components"]:
        check(f"valid raw component triple: {component}", lambda component=component: raw_semantics(raw_row(component)))

    # 50-66: raw grammar, failure branches, controls, and unresolved arm binding.
    check("uppercase main plane rejected", lambda: not schema_valid("raw_cost", {**raw_row("psi_evaluation"), "plane": "MAIN"}))
    check("selection wrong seed rejected", lambda: not schema_valid("raw_cost", {**raw_row("scalar_multiplication"), "plane": "selection", "seed": 606103, "q": 256, "arm": 2}))
    check("top source control owner admitted", lambda: raw_semantics(raw_row("top_level_control")))
    check("identity source control owner admitted", lambda: raw_semantics(raw_row("identity_transport_control")))
    check("top control wrong arm rejected", lambda: not schema_valid("raw_cost", {**raw_row("top_level_control"), "owner": {**component_owner("top_level_control"), "arm": "direct_iota"}}))
    check("source control fake endpoint rejected", lambda: not schema_valid("raw_cost", {**raw_row("top_level_control"), "owner": {**component_owner("top_level_control"), "endpoint": "K0"}}))
    check("scaffold kind mismatch is schema-valid but semantic-invalid", lambda: schema_valid("raw_cost", {**raw_row("query_generation"), "scaffold_kind": "verifier_private_join"}) and not raw_semantics({**raw_row("query_generation"), "scaffold_kind": "verifier_private_join"}))
    check("psi evaluation on scalar arm is admitted by declared schema", lambda: schema_valid("raw_cost", {**raw_row("psi_evaluation"), "arm": 2}))
    check("scalar multiplication on transport arm is admitted by declared schema", lambda: schema_valid("raw_cost", {**raw_row("scalar_multiplication"), "arm": 1}))
    check("scalar warmup on transport arm is admitted by declared schema", lambda: schema_valid("raw_cost", {**raw_row("scalar_warmup"), "arm": 1}))
    partial = raw_row("discovery_all_candidates", status="partial")
    for key, reason_key in (("CPU_nanoseconds", "CPU_unavailable_reason"), ("wall_nanoseconds", "wall_unavailable_reason"), ("process_group_peak_RSS_bytes", "RSS_unavailable_reason")):
        partial[key], partial[reason_key] = None, "not_observed_before_stop"
    check("partial exclusive row with typed unavailable resources admitted", lambda: raw_semantics(partial))
    check("complete exclusive row with null RSS rejected", lambda: not schema_valid("raw_cost", {**raw_row("read_m"), "process_group_peak_RSS_bytes": None, "RSS_unavailable_reason": "capture_failed"}))
    check("derived rollup with exact source leaf admitted", lambda: raw_semantics(raw_row("level_and_multiplicity_certificate")))
    duplicate_leaf = raw_row("level_and_multiplicity_certificate")
    duplicate_leaf["source_leaf_ids"] = ["leaf-0", "leaf-0"]
    check("derived duplicate source leaf is schema-valid but semantic-invalid", lambda: schema_valid("raw_cost", duplicate_leaf) and not raw_semantics(duplicate_leaf))
    backwards = raw_row("read_m")
    backwards["capture_interval"]["wall_finished_ns"] = 29
    check("backwards capture interval is schema-valid but semantic-invalid", lambda: schema_valid("raw_cost", backwards) and not raw_semantics(backwards))
    check("recursive duplicate JSON key rejected", lambda: expect_raises(DuplicateKey, lambda: strict_json('{"record_type":"raw_cost","x":{"a":1,"a":2}}', "raw_cost")))
    check("nonfinite JSON number rejected", lambda: expect_raises(ValueError, lambda: strict_json('{"record_type":"raw_cost","CPU_nanoseconds":NaN}', "raw_cost")))
    check("integral float raw integer spelling rejected", lambda: expect_raises(ValueError, lambda: strict_json('{"record_type":"raw_cost","event_ordinal":1.0}', "raw_cost")))

    # 67-81: closed allocation objects and global domain arithmetic.
    check("cold allocation edge admitted", lambda: allocation_semantics(allocation_edge()))
    check("selection-score allocation edge admitted", lambda: allocation_semantics(allocation_edge(view="selection_score_candidate", scenario={"kind": "selection_score", "candidate_arm": 2}, reason="selection_score")))
    check("actual-only allocation edge admitted", lambda: allocation_semantics(allocation_edge(view="actual_only_scaffolding", scenario={"kind": "actual_only"}, target={"kind": "physical_owner", "raw_cost_row_id": "raw-x"}, reason="actual_only")))
    check("actual-only scenario with q rejected", lambda: not schema_valid("allocation_edge", allocation_edge(view="actual_only_scaffolding", scenario={"kind": "actual_only", "q": 1}, target={"kind": "physical_owner", "raw_cost_row_id": "raw-x"}, reason="actual_only")))
    check("selection-score scenario with stratum alias rejected", lambda: not schema_valid("allocation_edge", allocation_edge(view="selection_score_candidate", scenario={"kind": "selection_score", "candidate_arm": 2, "stratum": "I0-u1"}, reason="selection_score")))
    check("actual-only target must name same raw row", lambda: schema_valid("allocation_edge", allocation_edge(view="actual_only_scaffolding", scenario={"kind": "actual_only"}, target={"kind": "physical_owner", "raw_cost_row_id": "other"}, reason="actual_only")) and not allocation_semantics(allocation_edge(view="actual_only_scaffolding", scenario={"kind": "actual_only"}, target={"kind": "physical_owner", "raw_cost_row_id": "other"}, reason="actual_only")))
    check("unreduced allocation weight is schema-valid but semantic-invalid", lambda: schema_valid("allocation_edge", allocation_edge(weight=fraction(2, 4))) and not allocation_semantics(allocation_edge(weight=fraction(2, 4))))
    check("boolean allocation numerator rejected", lambda: not schema_valid("allocation_edge", allocation_edge(weight={"numerator": True, "denominator": 1})))
    null_bad = allocation_edge(cpu=None)
    null_bad["allocated_CPU_unavailable_reason"] = None
    check("null allocated CPU without reason is schema-valid but semantic-invalid", lambda: schema_valid("allocation_edge", null_bad) and not allocation_semantics(null_bad))
    reason_alias = allocation_edge(reason="actual_only")
    check("cold scalar edge accepts semantically mismatched reason code", lambda: schema_valid("allocation_edge", reason_alias))
    global_edges = global_library_edges(73)
    check("complete 72-edge global library allocation reconciles", lambda: len(global_edges) == 72 and allocation_group_ok(global_edges, expected_targets=endpoint_targets()))
    check("missing one global endpoint edge rejected", lambda: not allocation_group_ok(global_edges[:-1], expected_targets=endpoint_targets()))
    check("duplicate global endpoint edge rejected", lambda: not allocation_group_ok(global_edges[:-1] + [copy.deepcopy(global_edges[0])], expected_targets=endpoint_targets()))
    stratum_only = [edge for edge in global_edges if edge["target"]["fixture"].startswith("I0") and edge["target"]["coordinate"] == 1]
    check("one eight-endpoint stratum cannot replace 72-edge global domain", lambda: len(stratum_only) == 8 and not allocation_group_ok(stratum_only, expected_targets=endpoint_targets()))
    bad_remainder = copy.deepcopy(global_edges)
    bad_remainder[0]["allocated_CPU_nanoseconds"], bad_remainder[-1]["allocated_CPU_nanoseconds"] = 1, 2
    check("noncanonical integer remainder placement rejected", lambda: not allocation_group_ok(bad_remainder, expected_targets=endpoint_targets()))

    # 82-86: exact fixed arithmetic and cardinalities.
    check("Med7 is fourth exact order statistic", lambda: med7([7, 1, 6, 2, 5, 3, 4]) == 4)
    check("Med6 is exact central-pair mean", lambda: med6([1, 1, 1, 2, 2, 2]) == Fraction(3, 2))
    check("ratio of endpoint totals differs from mean of ratios", lambda: Fraction(1 + 9, 1 + 3) == Fraction(5, 2) and (Fraction(1, 1) + Fraction(9, 3)) / 2 == 2)
    check("q-star cannot skip unresolved earlier rung", lambda: qstar({1: None, 16: Fraction(2), 256: Fraction(2), 4096: Fraction(2)}) == "unresolved")
    check("all fixed matrix cardinalities rederive", lambda: (6*4*3*2*4*7*7, 9*8*6*7, 6*2*3, 6*2*3*4, 6*3*2*4*2*7, 6*4*3*258) == (28224, 3024, 36, 144, 2016, 18576))

    # 87-120: complete/failure manifest branches and cross-source conflicts.
    check("complete manifest passes schema and declared global predicates", lambda: manifest_semantics(manifest()))
    for status in ("completed_invalid", "partial_inconclusive", "refused_before_run", "infrastructure_stopped"):
        check(f"typed nonvalid manifest branch admitted: {status}", lambda status=status: manifest_semantics(manifest(status)))
    empty = manifest(); empty["run"]["result"]["metrics"]["R_cells"] = []
    check("empty completed-valid R_cells is schema-valid but semantic-invalid", lambda: schema_valid("manifest", empty) and not manifest_semantics(empty))
    zero_coverage = manifest(); zero_coverage["run"]["result"]["metrics"]["coverage"]["resolved_primary_cells"] = 0
    check("zero resolved cells is schema-valid but semantic-invalid", lambda: schema_valid("manifest", zero_coverage) and not manifest_semantics(zero_coverage))
    zero_bytes = manifest(); zero_bytes["run"]["artifacts"]["raw-result.json"]["bytes"] = 0
    check("zero-byte required artifact is schema-valid but semantic-invalid", lambda: schema_valid("manifest", zero_bytes) and not manifest_semantics(zero_bytes))
    unreduced = manifest(); unreduced["run"]["result"]["metrics"]["R_cells"][0]["ratio"] = ratio_value(2, 4)
    check("unreduced ratio is schema-valid but semantic-invalid", lambda: schema_valid("manifest", unreduced) and not manifest_semantics(unreduced))
    duplicate_cell = manifest(); duplicate_cell["run"]["result"]["metrics"]["R_cells"][-1] = copy.deepcopy(duplicate_cell["run"]["result"]["metrics"]["R_cells"][0])
    check("duplicate ratio tuple is schema-valid but semantic-invalid", lambda: schema_valid("manifest", duplicate_cell) and not manifest_semantics(duplicate_cell))
    loo_a = manifest(); varied = [
        fraction(1, 8), fraction(1, 4), fraction(3, 8), fraction(1, 2),
        fraction(5, 8), fraction(3, 4), fraction(7, 8),
    ]
    for row in loo_a["run"]["result"]["metrics"]["R_cells"]:
        if row["seed"] == 606103 and row["q"] == 4096:
            row["leave_one_out"] = [{"kind": "value", "value": copy.deepcopy(item)} for item in varied]
    loo_b = copy.deepcopy(loo_a)
    for row in loo_b["run"]["result"]["metrics"]["R_cells"]:
        row["leave_one_out"].reverse()
    loo_item_properties = SCHEMA["$defs"]["manifest"]["properties"]["run"]["properties"]["result"]["properties"]["metrics"]["properties"]["R_cells"]["items"]["properties"]["leave_one_out"]["items"]["oneOf"][0]["properties"]
    check("seven LOO values remain schema-valid under unlabeled reversal", lambda: "block" not in loo_item_properties and "omitted_block" not in loo_item_properties and manifest_semantics(loo_a) and manifest_semantics(loo_b))
    six_loo = manifest(); governing = next(row for row in six_loo["run"]["result"]["metrics"]["R_cells"] if row["seed"] == 606103 and row["q"] == 4096); governing["leave_one_out"].pop()
    check("six governing LOO entries is schema-valid but semantic-invalid", lambda: schema_valid("manifest", six_loo) and not manifest_semantics(six_loo))
    nongoverning_loo = manifest(); nongoverning_loo["run"]["result"]["metrics"]["R_cells"][0]["leave_one_out"] = [ratio_value()]
    check("non-governing LOO entry is schema-valid but semantic-invalid", lambda: schema_valid("manifest", nongoverning_loo) and not manifest_semantics(nongoverning_loo))
    positive = manifest(); positive["run"]["result"]["metrics"] = complete_metrics(ratio=fraction(6, 5), loo_values=[fraction(6, 5)]*7, branch="finite_panel_signal_only"); positive["run"]["result"]["metrics"]["R_cells"][-1]["ratio"] = ratio_value(1, 1)
    check("favorable global panel cannot rescue one unfavorable positive cell", lambda: schema_valid("manifest", positive) and not manifest_semantics(positive))
    false_valid = manifest("partial_inconclusive"); false_valid["run"]["result"]["valid"] = True
    check("non-completed status with valid true rejected", lambda: not schema_valid("manifest", false_valid))
    dirty = manifest(); dirty["run"]["code"]["dirty"] = True; dirty["run"]["code"]["dirty_diff_sha256"] = "2"*64
    check("completed-valid dirty source rejected", lambda: not schema_valid("manifest", dirty))
    missing_artifact = manifest(); del missing_artifact["run"]["artifacts"]["raw-result.json"]
    check("completed-valid missing companion rejected", lambda: not schema_valid("manifest", missing_artifact))
    from orchestration.adapter.manifest import deterministic_block
    adapter_manifest = manifest(); adapter_manifest["run"]["inference"] = deterministic_block()
    check("sole deterministic inference writer conflicts on note field", lambda: "note" in adapter_manifest["run"]["inference"] and not schema_valid("manifest", adapter_manifest))
    resolution_failure = manifest("refused_before_run"); resolution_failure["run"]["inference"] = deterministic_block("review-adversarial", note="policy resolution failed"); resolution_failure["run"]["inference"]["resolution_error"] = "RuntimeError: fixed refusal"
    check("resolution-failure inference block conflicts on preserved error fields", lambda: not schema_valid("manifest", resolution_failure))
    arbitrary_reason = manifest("infrastructure_stopped"); arbitrary_reason["run"]["result"]["invalid_reason"] = "banana"
    check("arbitrary manifest invalid_reason is admitted without status mapping", lambda: schema_valid("manifest", arbitrary_reason) and manifest_semantics(arbitrary_reason))
    model_manifest = manifest(); model_manifest["run"]["inference"] = {
        "requested_policy": "review-adversarial", "canonical_policy": "review-adversarial",
        "backend": "openai", "provider": "openai", "resolved_model_id": "gpt-5.6-sol",
        "model_provenance": "operator-supplied", "model_verified": False,
        "requested_reasoning_effort": "xhigh", "reasoning_effort": "xhigh",
        "fallback_used": False, "fallback_reason": None, "degraded_requirements": [],
        "independent_session": True, "adapter_version": "1.0.0", "config_digest": "sha256:fixed",
    }
    check("complete non-Bedrock inference block admitted", lambda: schema_valid("manifest", model_manifest))
    bedrock = copy.deepcopy(model_manifest); bedrock["run"]["inference"]["provider"] = "Amazon Bedrock"
    check("Bedrock provider rejected", lambda: not schema_valid("manifest", bedrock))
    reverse_time = manifest(); reverse_time["run"]["timing"]["finished_at"] = "2026-09-07T23:59:59+00:00"
    check("reverse UTC interval is schema-valid but semantic-invalid", lambda: schema_valid("manifest", reverse_time) and not manifest_semantics(reverse_time))
    null_resource = manifest("infrastructure_stopped"); null_resource["run"]["resources"]["peak_rss_unavailable_reason"] = None
    check("null manifest resource without reason is schema-valid but semantic-invalid", lambda: schema_valid("manifest", null_resource) and not manifest_semantics(null_resource))
    bad_contract = manifest(); bad_contract["run"]["inputs"]["parameters"]["effective_contract_sha256"] = "0"*64
    check("wrong effective-contract binding is schema-valid but semantic-invalid", lambda: schema_valid("manifest", bad_contract) and not manifest_semantics(bad_contract))
    bad_schema = manifest(); bad_schema["run"]["admission"]["schema_sha256"] = "0"*64
    check("wrong schema binding is schema-valid but semantic-invalid", lambda: schema_valid("manifest", bad_schema) and not manifest_semantics(bad_schema))
    self_hash = manifest(); self_hash["run"]["artifacts"]["manifest.yaml"] = {"sha256": "0"*64, "bytes": 1}
    check("manifest self-hash rejected", lambda: not schema_valid("manifest", self_hash))
    false_clean = manifest(); false_clean["run"]["code"]["dirty_diff_sha256"] = "0"*64
    check("clean source with dirty diff hash rejected", lambda: not schema_valid("manifest", false_clean))
    wrong_certificate = manifest(); wrong_certificate["run"]["result"]["certificate"]["kind"] = "discrete_log"
    check("scientific certificate claim rejected by finite measurement schema", lambda: not schema_valid("manifest", wrong_certificate))
    display_json = json.dumps(manifest(), separators=(",", ":")).replace('"wall_seconds":1.0', '"wall_seconds":1.25').replace('"cpu_seconds":0.5', '"cpu_seconds":0.25')
    check("two finite fractional display seconds accepted by strict parser", lambda: isinstance(strict_json(display_json, "manifest")["run"]["timing"]["wall_seconds"], float))
    float_index = json.dumps(manifest(), separators=(",", ":")).replace('"primary_q":4096', '"primary_q":4096.0')
    check("integral float manifest index rejected by strict parser", lambda: expect_raises(ValueError, lambda: strict_json(float_index, "manifest")))
    check("duplicate YAML mapping rejected", lambda: expect_raises(DuplicateKey, lambda: strict_yaml("run:\n  id: RUN-ECDLP-abcdef\n  id: RUN-ECDLP-fedcba\n")))
    bool_index = manifest(); bool_index["run"]["inputs"]["parameters"]["primary_q"] = True
    check("boolean manifest integer rejected", lambda: not schema_valid("manifest", bool_index))

    if len(CASES) != 120:
        raise RuntimeError(f"suite definition error: expected 120 cases, got {len(CASES)}")


def main():
    started = time.perf_counter()
    cpu_started = time.process_time()
    run_suite()
    output = {
        "schema": "crypto.autoresearch.independent_definition_checks.v1",
        "task_id": "TASK-20260908-fdf173",
        "scope": "fixed synthetic/static schema and exact arithmetic metadata only",
        "command_contract": "single fixed suite; no CLI parameters",
        "executed_cases": len(CASES),
        "passed": sum(item["status"] == "passed" for item in CASES),
        "failed": sum(item["status"] == "failed" for item in CASES),
        "cases": CASES,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu_started,
        "maximum_rss_native": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "rss_units": "bytes_on_Darwin",
        "workers": 1,
        "scientific_runs": 0,
        "dependencies": {
            "python": __import__("sys").version.split()[0],
            "jsonschema": version("jsonschema"),
            "PyYAML": version("PyYAML"),
        },
        "source_sha256": {
            "contract": hashlib.sha256(CONTRACT_PATH.read_bytes()).hexdigest(),
            "schema": hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest(),
            "handoff": hashlib.sha256(HANDOFF_PATH.read_bytes()).hexdigest(),
            "checker": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }
    print(json.dumps(output, indent=2, sort_keys=False))
    return 1 if output["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
