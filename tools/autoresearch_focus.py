#!/usr/bin/env python3
"""Validate and select a small, decision-focused autoresearch queue."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import sys
from pathlib import Path
from typing import Any


SCHEMA_V1 = "crypto.autoresearch.focus_queue.v1"
SCHEMA_V2 = "crypto.autoresearch.focus_queue.v2"
SCHEMA = "crypto.autoresearch.focus_queue.v3"
PLAN_SCHEMA = "crypto.autoresearch.focus_plan.v3"
SCORE_FIELDS = (
    "decision_impact",
    "falsifiability",
    "mechanism_novelty",
    "reproduction_readiness",
    "cost_efficiency",
)
WEIGHTS = {
    "decision_impact": 5,
    "falsifiability": 4,
    "mechanism_novelty": 3,
    "reproduction_readiness": 3,
    "cost_efficiency": 2,
}
TERMINAL_STATES = {"completed_positive", "completed_negative", "inconclusive"}
QUEUE_STATES = {"queued", "active"}
ALL_STATES = QUEUE_STATES | TERMINAL_STATES | {"blocked", "deferred"}
CONFIDENCE = {"low", "medium", "high"}
CLAIM_VERDICTS = {
    "reproduced",
    "partially_reproduced",
    "not_reproduced",
    "not_attempted",
    "open",
    "invalidated",
}
RUN_STATES = {"planned", "running", "completed", "failed", "cancelled", "invalid"}
CORRECTION_RECORD_TYPES = {"candidate", "claim", "run"}


class QueueError(ValueError):
    pass


def canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def require_text(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise QueueError(f"{location}.{field} must be nonempty text")


def require_text_list(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise QueueError(f"{location}.{field} must be a text list")


def require_positive_number(record: dict[str, Any], field: str, location: str) -> None:
    value = record.get(field)
    if (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or value <= 0
    ):
        raise QueueError(f"{location}.{field} must be a positive number")


def validate_attention_contract(candidate: dict[str, Any], location: str) -> None:
    contract = candidate.get("attention_contract")
    if not isinstance(contract, dict):
        raise QueueError(f"{location}.attention_contract must be an object")
    for field in (
        "decisive_evidence",
        "inconclusive_decision",
        "local_ambiguity_rule",
        "rerank_trigger",
    ):
        require_text(contract, field, f"{location}.attention_contract")
    require_text_list(
        contract, "peripheral_exclusions", f"{location}.attention_contract"
    )
    if not contract["peripheral_exclusions"]:
        raise QueueError(
            f"{location}.attention_contract.peripheral_exclusions must not be empty"
        )


def validate_resource_estimate(
    candidate: dict[str, Any], location: str, require_stages: bool = False
) -> None:
    estimate = candidate.get("resource_estimate")
    if not isinstance(estimate, dict):
        raise QueueError(f"{location}.resource_estimate must be an object")
    for field in ("wall_clock_seconds", "cpu_hours", "maximum_memory_gb"):
        if field == "maximum_memory_gb" or estimate.get(field) is not None:
            require_positive_number(estimate, field, f"{location}.resource_estimate")
    maximum_runs = estimate.get("maximum_runs")
    if (
        maximum_runs is not None and (not isinstance(maximum_runs, int)
        or isinstance(maximum_runs, bool)
        or maximum_runs < 1)
    ):
        raise QueueError(
            f"{location}.resource_estimate.maximum_runs must be a positive integer"
        )
    for field in (
        "dominant_cost",
        "complexity_hypothesis",
        "sharding_plan",
        "stop_rule",
    ):
        require_text(estimate, field, f"{location}.resource_estimate")
    if not require_stages:
        return

    if not estimate.get("stages"):
        return  # Stage cost estimates are optional, not execution permissions.
    require_text(estimate, "dominant_stage_id", f"{location}.resource_estimate")
    stages = estimate.get("stages")
    if not isinstance(stages, list) or not stages:
        raise QueueError(
            f"{location}.resource_estimate.stages must be a nonempty list"
        )
    stage_ids = []
    for index, stage in enumerate(stages):
        stage_location = f"{location}.resource_estimate.stages[{index}]"
        if not isinstance(stage, dict):
            raise QueueError(f"{stage_location} must be an object")
        for field in ("id", "purpose", "dominant_operation", "stop_rule"):
            require_text(stage, field, stage_location)
        for field in ("wall_clock_seconds", "cpu_hours", "maximum_memory_gb"):
            if field == "maximum_memory_gb" or stage.get(field) is not None:
                require_positive_number(stage, field, stage_location)
        parallel_shards = stage.get("parallel_shards")
        if (
            not isinstance(parallel_shards, int)
            or isinstance(parallel_shards, bool)
            or parallel_shards < 1
        ):
            raise QueueError(
                f"{stage_location}.parallel_shards must be a positive integer"
            )
        stage_ids.append(stage["id"])
    if len(stage_ids) != len(set(stage_ids)):
        raise QueueError(f"{location}.resource_estimate stage IDs must be unique")
    if estimate["dominant_stage_id"] not in set(stage_ids):
        raise QueueError(
            f"{location}.resource_estimate.dominant_stage_id is not a stage"
        )

    # Time and CPU estimates need not reconcile: they are advisory, not caps.
    stage_memory = max(stage["maximum_memory_gb"] for stage in stages)
    if stage_memory > estimate["maximum_memory_gb"]:
        raise QueueError(
            f"{location}.resource_estimate stage memory exceeds the campaign maximum"
        )


def validate_claims(
    queue: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_run: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    claims = queue.get("claims")
    if not isinstance(claims, list):
        raise QueueError("queue.claims must be a list")
    claim_ids = []
    for index, claim in enumerate(claims):
        location = f"claims[{index}]"
        if not isinstance(claim, dict):
            raise QueueError(f"{location} must be an object")
        for field in (
            "id",
            "statement",
            "scope",
            "target_result",
            "observed_result",
        ):
            require_text(claim, field, location)
        if claim.get("verdict") not in CLAIM_VERDICTS:
            raise QueueError(f"{location}.verdict is invalid")
        if not isinstance(claim.get("independently_verified"), bool):
            raise QueueError(f"{location}.independently_verified must be boolean")
        for field in (
            "evidence_artifacts",
            "evidence_runs",
            "linked_experiments",
            "scope_deviations",
            "blockers",
        ):
            require_text_list(claim, field, location)
        unknown = set(claim["linked_experiments"]) - set(by_id)
        if unknown:
            raise QueueError(
                f"{location}.linked_experiments contains unknown IDs {sorted(unknown)}"
            )
        evidence_bearing = claim["verdict"] in {
            "reproduced",
            "partially_reproduced",
            "not_reproduced",
            "invalidated",
        }
        if evidence_bearing and (
            not claim["evidence_artifacts"] or not claim["evidence_runs"]
        ):
            raise QueueError(
                f"{location} evidence-bearing verdict requires artifacts and runs"
            )
        unknown_runs = set(claim["evidence_runs"]) - set(by_run)
        if unknown_runs:
            raise QueueError(
                f"{location}.evidence_runs contains unknown IDs {sorted(unknown_runs)}"
            )
        noncompleted_runs = [
            run_id
            for run_id in claim["evidence_runs"]
            if by_run[run_id]["status"] != "completed"
        ]
        if noncompleted_runs:
            raise QueueError(
                f"{location}.evidence_runs contains noncompleted runs {noncompleted_runs}"
            )
        if evidence_bearing:
            run_artifacts = {
                artifact
                for run_id in claim["evidence_runs"]
                for artifact in by_run[run_id]["artifacts"]
            }
            missing_artifacts = set(claim["evidence_artifacts"]) - run_artifacts
            if missing_artifacts:
                raise QueueError(
                    f"{location}.evidence_artifacts are not bound to cited runs "
                    f"{sorted(missing_artifacts)}"
                )
            run_experiments = {
                by_run[run_id]["experiment_id"] for run_id in claim["evidence_runs"]
            }
            missing_experiments = run_experiments - set(claim["linked_experiments"])
            if missing_experiments:
                raise QueueError(
                    f"{location}.linked_experiments omits evidence-run experiments "
                    f"{sorted(missing_experiments)}"
                )
        if claim["verdict"] == "reproduced" and not claim["independently_verified"]:
            raise QueueError(f"{location} reproduced claim requires independent verification")
        if claim["verdict"] in {"open", "not_attempted"} and claim[
            "independently_verified"
        ]:
            raise QueueError(
                f"{location} open or unattempted claim cannot be independently verified"
            )
        claim_ids.append(claim["id"])
    if len(claim_ids) != len(set(claim_ids)):
        raise QueueError("claim IDs must be unique")
    return {claim["id"]: claim for claim in claims}


def assert_acyclic(
    graph: dict[str, list[str]], graph_name: str
) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise QueueError(f"{graph_name} contains a cycle at {node}")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph.get(node, []):
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def validate_runs(
    queue: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    runs = queue.get("runs")
    if not isinstance(runs, list):
        raise QueueError("queue.runs must be a list")
    run_ids = []
    for index, run in enumerate(runs):
        location = f"runs[{index}]"
        if not isinstance(run, dict):
            raise QueueError(f"{location} must be an object")
        for field in ("id", "experiment_id", "purpose"):
            require_text(run, field, location)
        if run["experiment_id"] not in by_id:
            raise QueueError(f"{location}.experiment_id is unknown")
        if run.get("status") not in RUN_STATES:
            raise QueueError(f"{location}.status is invalid")
        require_text_list(run, "depends_on_runs", location)
        require_text_list(run, "artifacts", location)
        failure_reason = run.get("failure_reason")
        if failure_reason is not None and (
            not isinstance(failure_reason, str) or not failure_reason.strip()
        ):
            raise QueueError(f"{location}.failure_reason must be null or nonempty text")
        if run["status"] == "completed" and not run["artifacts"]:
            raise QueueError(f"{location} completed run requires artifacts")
        if run["status"] in {"failed", "cancelled", "invalid"} and not failure_reason:
            raise QueueError(f"{location} {run['status']} run requires failure_reason")
        if run["status"] in {"planned", "running", "completed"} and failure_reason:
            raise QueueError(f"{location} non-failure run cannot have failure_reason")
        run_ids.append(run["id"])
    if len(run_ids) != len(set(run_ids)):
        raise QueueError("run IDs must be unique")
    by_run = {run["id"]: run for run in runs}
    for run in runs:
        unknown = set(run["depends_on_runs"]) - set(by_run)
        if unknown:
            raise QueueError(f"run {run['id']} has unknown dependencies {sorted(unknown)}")
        if run["id"] in run["depends_on_runs"]:
            raise QueueError(f"run {run['id']} depends on itself")
    assert_acyclic(
        {run["id"]: run["depends_on_runs"] for run in runs}, "run graph"
    )
    return by_run


def correction_path(field: str, location: str) -> list[Any]:
    path: list[Any] = []
    for segment in field.split("."):
        if not segment:
            raise QueueError(f"{location}.field has invalid path {field}")
        name = segment.split("[", 1)[0]
        if not name:
            raise QueueError(f"{location}.field has invalid path {field}")
        path.append(name)
        remainder = segment[len(name):]
        while remainder:
            if not remainder.startswith("[") or "]" not in remainder:
                raise QueueError(f"{location}.field has invalid path {field}")
            index_text, remainder = remainder[1:].split("]", 1)
            if not index_text.isdigit():
                raise QueueError(f"{location}.field has invalid index in {field}")
            path.append(int(index_text))
    return path


def nested_value(record: dict[str, Any], field: str, location: str) -> Any:
    value: Any = record
    for part in correction_path(field, location):
        if isinstance(part, str) and isinstance(value, dict) and part in value:
            value = value[part]
        elif (
            isinstance(part, int)
            and isinstance(value, list)
            and 0 <= part < len(value)
        ):
            value = value[part]
        else:
            raise QueueError(f"{location}.field references unknown path {field}")
    return value


def set_nested_value(
    record: dict[str, Any], field: str, corrected_value: Any, location: str
) -> None:
    parts = correction_path(field, location)
    parent: Any = record
    for part in parts[:-1]:
        if isinstance(part, str) and isinstance(parent, dict) and part in parent:
            parent = parent[part]
        elif (
            isinstance(part, int)
            and isinstance(parent, list)
            and 0 <= part < len(parent)
        ):
            parent = parent[part]
        else:
            raise QueueError(f"{location}.field references unknown path {field}")
    final = parts[-1]
    if isinstance(final, str) and isinstance(parent, dict) and final in parent:
        parent[final] = copy.deepcopy(corrected_value)
    elif (
        isinstance(final, int)
        and isinstance(parent, list)
        and 0 <= final < len(parent)
    ):
        parent[final] = copy.deepcopy(corrected_value)
    else:
        raise QueueError(f"{location}.field references unknown path {field}")


def materialize_corrections(queue: dict[str, Any]) -> dict[str, Any]:
    effective = copy.deepcopy(queue)
    corrections = queue.get("corrections", [])
    records = {
        "candidate": {
            candidate["id"]: candidate for candidate in effective.get("candidates", [])
        },
        "claim": {claim["id"]: claim for claim in effective.get("claims", [])},
        "run": {run["id"]: run for run in effective.get("runs", [])},
    }
    chains: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = {}
    for index, correction in enumerate(corrections):
        key = (
            correction["record_type"],
            correction["record_id"],
            correction["field"],
        )
        chains.setdefault(key, []).append((index, correction))

    for (record_type, record_id, field), chain in chains.items():
        first_index, first = chain[0]
        first_location = f"corrections[{first_index}]"
        expected_prior = first["prior_value"]
        for index, correction in chain:
            location = f"corrections[{index}]"
            if correction["prior_value"] != expected_prior:
                raise QueueError(
                    f"{location}.prior_value does not continue correction chain for "
                    f"{record_type}:{record_id}.{field}"
                )
            expected_prior = correction["corrected_value"]

        record = records[record_type][record_id]
        actual = nested_value(record, field, first_location)
        final_value = chain[-1][1]["corrected_value"]
        if actual != first["prior_value"] and actual != final_value:
            raise QueueError(
                f"{first_location}.prior_value does not match base or materialized "
                f"{record_type}:{record_id}.{field}"
            )
        set_nested_value(record, field, final_value, first_location)
    effective["corrections"] = []
    return effective


def validate_corrections(
    queue: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_claim: dict[str, dict[str, Any]],
    by_run: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    corrections = queue.get("corrections")
    if not isinstance(corrections, list):
        raise QueueError("queue.corrections must be a list")
    correction_ids = []
    records = {"candidate": by_id, "claim": by_claim, "run": by_run}
    for index, correction in enumerate(corrections):
        location = f"corrections[{index}]"
        if not isinstance(correction, dict):
            raise QueueError(f"{location} must be an object")
        for field in ("id", "recorded_at", "record_id", "field", "reason"):
            require_text(correction, field, location)
        record_type = correction.get("record_type")
        if record_type not in CORRECTION_RECORD_TYPES:
            raise QueueError(f"{location}.record_type is invalid")
        if correction["record_id"] not in records[record_type]:
            raise QueueError(f"{location}.record_id is unknown")
        if correction["field"] == "id" or correction["field"].startswith("id."):
            raise QueueError(f"{location}.field cannot change a record ID")
        if "prior_value" not in correction or "corrected_value" not in correction:
            raise QueueError(f"{location} must preserve prior_value and corrected_value")
        if correction["prior_value"] == correction["corrected_value"]:
            raise QueueError(f"{location} must change the recorded value")
        require_text_list(correction, "evidence_artifacts", location)
        correction_ids.append(correction["id"])
    if len(correction_ids) != len(set(correction_ids)):
        raise QueueError("correction IDs must be unique")
    return materialize_corrections(queue)


def validate_outcome(candidate: dict[str, Any], location: str) -> None:
    outcome = candidate.get("outcome")
    if not isinstance(outcome, dict):
        raise QueueError(f"{location}.outcome must be an object")
    state = outcome.get("state")
    if state not in {"untested", "positive", "negative", "inconclusive"}:
        raise QueueError(f"{location}.outcome.state is invalid")
    verified = outcome.get("independently_verified")
    if not isinstance(verified, bool):
        raise QueueError(
            f"{location}.outcome.independently_verified must be boolean"
        )
    artifacts = outcome.get("artifacts")
    if not isinstance(artifacts, list) or not all(
        isinstance(item, str) and item.strip() for item in artifacts
    ):
        raise QueueError(f"{location}.outcome.artifacts must be a text list")
    status = candidate["status"]
    expected = {
        "completed_positive": "positive",
        "completed_negative": "negative",
        "inconclusive": "inconclusive",
    }.get(status)
    if expected is not None and state != expected:
        raise QueueError(
            f"{location} status {status} requires outcome state {expected}"
        )
    if status in TERMINAL_STATES and not artifacts:
        raise QueueError(f"{location} terminal outcome requires artifacts")


def validate_candidate(candidate: Any, index: int, schema: str) -> None:
    location = f"candidates[{index}]"
    if not isinstance(candidate, dict):
        raise QueueError(f"{location} must be an object")
    for field in (
        "id",
        "title",
        "uncertainty",
        "positive_decision",
        "negative_decision",
        "next_action",
    ):
        require_text(candidate, field, location)
    if candidate.get("status") not in ALL_STATES:
        raise QueueError(f"{location}.status is invalid")
    if schema in {SCHEMA_V2, SCHEMA} and candidate["status"] in QUEUE_STATES:
        validate_resource_estimate(candidate, location, require_stages=schema == SCHEMA)
    if schema == SCHEMA and candidate["status"] in QUEUE_STATES:
        validate_attention_contract(candidate, location)
    dependencies = candidate.get("dependencies")
    if not isinstance(dependencies, list) or not all(
        isinstance(item, str) and item.strip() for item in dependencies
    ):
        raise QueueError(f"{location}.dependencies must be a text list")
    ambiguities = candidate.get("ambiguities")
    if not isinstance(ambiguities, list):
        raise QueueError(f"{location}.ambiguities must be a list")
    for ambiguity_index, ambiguity in enumerate(ambiguities):
        ambiguity_location = f"{location}.ambiguities[{ambiguity_index}]"
        if not isinstance(ambiguity, dict):
            raise QueueError(f"{ambiguity_location} must be an object")
        for field in ("question", "resolution", "basis"):
            require_text(ambiguity, field, ambiguity_location)
        if ambiguity.get("confidence") not in CONFIDENCE:
            raise QueueError(f"{ambiguity_location}.confidence is invalid")
    scores = candidate.get("scores")
    if not isinstance(scores, dict) or set(scores) != set(SCORE_FIELDS):
        raise QueueError(
            f"{location}.scores must contain exactly {list(SCORE_FIELDS)}"
        )
    for field in SCORE_FIELDS:
        value = scores[field]
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= 4:
            raise QueueError(f"{location}.scores.{field} must be an integer 0..4")
    expansion_of = candidate.get("expansion_of")
    if expansion_of is not None and (
        not isinstance(expansion_of, str) or not expansion_of.strip()
    ):
        raise QueueError(f"{location}.expansion_of must be null or nonempty text")
    validate_outcome(candidate, location)


def validate_queue(queue: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(queue, dict):
        raise QueueError("queue must be an object")
    schema = queue.get("schema")
    if schema not in {SCHEMA_V1, SCHEMA_V2, SCHEMA}:
        raise QueueError(
            f"schema must be {SCHEMA_V1}, {SCHEMA_V2}, or {SCHEMA}"
        )
    require_text(queue, "objective", "queue")
    max_active = queue.get("max_active")
    if not isinstance(max_active, int) or isinstance(max_active, bool) or not 1 <= max_active <= 3:
        raise QueueError("queue.max_active must be an integer 1..3")
    candidates = queue.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise QueueError("queue.candidates must be a nonempty list")
    for index, candidate in enumerate(candidates):
        validate_candidate(candidate, index, schema)
    ids = [candidate["id"] for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise QueueError("candidate IDs must be unique")
    by_id = {candidate["id"]: candidate for candidate in candidates}
    for candidate in candidates:
        for dependency in candidate["dependencies"]:
            if dependency not in by_id:
                raise QueueError(
                    f"{candidate['id']} has unknown dependency {dependency}"
                )
            if dependency == candidate["id"]:
                raise QueueError(f"{candidate['id']} depends on itself")
        expansion_of = candidate.get("expansion_of")
        if expansion_of is not None and expansion_of not in by_id:
            raise QueueError(
                f"{candidate['id']} expands unknown candidate {expansion_of}"
            )
    assert_acyclic(
        {candidate["id"]: candidate["dependencies"] for candidate in candidates},
        "candidate graph",
    )
    active = [candidate["id"] for candidate in candidates if candidate["status"] == "active"]
    if len(active) > max_active:
        raise QueueError(
            f"active candidate count {len(active)} exceeds max_active {max_active}"
        )
    for candidate_id in active:
        active_blockers = blockers(by_id[candidate_id], by_id)
        if active_blockers:
            raise QueueError(
                f"active candidate {candidate_id} is blocked: {active_blockers}"
            )
    if schema == SCHEMA:
        by_run = validate_runs(queue, by_id)
        by_claim = validate_claims(queue, by_id, by_run)
        effective = validate_corrections(queue, by_id, by_claim, by_run)
        if queue["corrections"]:
            validate_queue(effective)
    return by_id


def score(candidate: dict[str, Any]) -> int:
    return sum(candidate["scores"][field] * WEIGHTS[field] for field in SCORE_FIELDS)


def blockers(
    candidate: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> list[str]:
    output = []
    for dependency in candidate["dependencies"]:
        if by_id[dependency]["status"] not in TERMINAL_STATES:
            output.append(f"dependency_not_terminal:{dependency}")
    parent_id = candidate.get("expansion_of")
    if parent_id is not None:
        parent = by_id[parent_id]
        if parent["outcome"]["state"] == "positive" and not parent["outcome"][
            "independently_verified"
        ]:
            output.append(f"positive_parent_not_independently_verified:{parent_id}")
    if candidate["status"] == "blocked":
        output.append("candidate_marked_blocked")
    return output


def expansion_edge_kind(
    candidate: dict[str, Any], by_id: dict[str, dict[str, Any]]
) -> str:
    parent = by_id[candidate["expansion_of"]]
    state = parent["outcome"]["state"]
    if state == "positive":
        verification = (
            "verified" if parent["outcome"]["independently_verified"] else "unverified"
        )
        return f"{verification}_positive_expansion"
    return f"{state}_scope_expansion"


def select(queue: dict[str, Any]) -> dict[str, Any]:
    validate_queue(queue)
    source_queue = queue
    effective_queue = (
        materialize_corrections(queue) if queue["schema"] == SCHEMA else queue
    )
    by_id = validate_queue(effective_queue)
    has_resource_estimates = effective_queue["schema"] in {SCHEMA_V2, SCHEMA}
    claims = effective_queue.get("claims", [])
    runs = effective_queue.get("runs", [])
    active = [
        candidate
        for candidate in effective_queue["candidates"]
        if candidate["status"] == "active"
    ]
    eligible = [
        candidate
        for candidate in effective_queue["candidates"]
        if candidate["status"] == "queued" and not blockers(candidate, by_id)
    ]
    eligible.sort(key=lambda candidate: (-score(candidate), candidate["id"]))
    selected = active + eligible[: effective_queue["max_active"] - len(active)]
    selected_ids = {candidate["id"] for candidate in selected}
    deferred = []
    for candidate in effective_queue["candidates"]:
        if candidate["id"] in selected_ids or candidate["status"] in TERMINAL_STATES:
            continue
        candidate_blockers = blockers(candidate, by_id)
        if candidate_blockers:
            reason = candidate_blockers
        elif candidate["status"] == "deferred":
            reason = ["candidate_marked_deferred"]
        else:
            reason = ["focus_cap"]
        deferred.append({
            "id": candidate["id"],
            "score": score(candidate),
            "reason": reason,
        })
    completed = [
        {
            "id": candidate["id"],
            "status": candidate["status"],
            "outcome": candidate["outcome"],
        }
        for candidate in effective_queue["candidates"]
        if candidate["status"] in TERMINAL_STATES
    ]
    plan = {
        "schema": PLAN_SCHEMA,
        "source_schema": effective_queue["schema"],
        "objective": effective_queue["objective"],
        "source_queue_sha256": digest(source_queue),
        "max_active": effective_queue["max_active"],
        "critical_experiments": [
            {
                "rank": rank,
                "id": candidate["id"],
                "title": candidate["title"],
                "status": candidate["status"],
                "focus_score": score(candidate),
                "uncertainty": candidate["uncertainty"],
                "positive_decision": candidate["positive_decision"],
                "negative_decision": candidate["negative_decision"],
                "next_action": candidate["next_action"],
                "ambiguity_resolutions": candidate["ambiguities"],
                "attention_contract": candidate.get("attention_contract"),
                "resource_estimate": candidate.get("resource_estimate"),
            }
            for rank, candidate in enumerate(selected, start=1)
        ],
        "deferred": sorted(deferred, key=lambda item: (-item["score"], item["id"])),
        "completed_receipts": completed,
        "claim_matrix": claims,
        "experiment_graph": {
            "candidate_nodes": [
                {
                    "id": candidate["id"],
                    "title": candidate["title"],
                    "status": candidate["status"],
                }
                for candidate in effective_queue["candidates"]
            ],
            "candidate_edges": [
                {
                    "from": dependency,
                    "to": candidate["id"],
                    "kind": "dependency",
                }
                for candidate in effective_queue["candidates"]
                for dependency in candidate["dependencies"]
            ]
            + [
                {
                    "from": candidate["expansion_of"],
                    "to": candidate["id"],
                    "kind": expansion_edge_kind(candidate, by_id),
                }
                for candidate in effective_queue["candidates"]
                if candidate.get("expansion_of") is not None
            ],
            "run_nodes": runs,
            "run_edges": [
                {"from": dependency, "to": run["id"]}
                for run in runs
                for dependency in run["depends_on_runs"]
            ],
        },
        "corrections": source_queue.get("corrections", []),
        "gates": {
            "focus_cap_respected": len(selected) <= effective_queue["max_active"] <= 3,
            "all_selected_dependencies_terminal": all(
                not blockers(candidate, by_id) for candidate in selected
            ),
            "all_ambiguities_resolved": all(
                ambiguity["resolution"] and ambiguity["basis"]
                for candidate in selected
                for ambiguity in candidate["ambiguities"]
            ),
            "positive_expansion_requires_independent_verification": True,
            "all_selected_have_resource_estimates": (
                not has_resource_estimates
                or all(candidate.get("resource_estimate") for candidate in selected)
            ),
            "all_selected_have_attention_contracts": (
                effective_queue["schema"] != SCHEMA
                or all(candidate.get("attention_contract") for candidate in selected)
            ),
            "stage_estimates_are_advisory": True,
            "reproduced_claims_independently_verified": all(
                claim["independently_verified"]
                for claim in claims
                if claim["verdict"] == "reproduced"
            ),
            "claim_evidence_uses_completed_runs_only": True,
            "candidate_and_run_graphs_acyclic": True,
            "corrections_preserve_prior_values": True,
            "failed_cancelled_invalid_runs_are_not_claim_evidence": True,
        },
    }
    plan["plan_sha256"] = digest(plan)
    return plan


def markdown_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def render_markdown(plan: dict[str, Any]) -> str:
    lines = [
        "# Focused Autoresearch Plan",
        "",
        plan["objective"],
        "",
        "## Critical Experiments",
        "",
        "| Rank | ID | Status | Score | Wall h | CPU h | Memory GiB | Max runs |",
        "|---:|---|---|---:|---:|---:|---:|---:|",
    ]
    for experiment in plan["critical_experiments"]:
        estimate = experiment.get("resource_estimate") or {}
        wall_seconds = estimate.get("wall_clock_seconds")
        wall_hours = f"{wall_seconds / 3600:g}" if wall_seconds is not None else "n/a"
        lines.append(
            f"| {experiment['rank']} | `{markdown_cell(experiment['id'])}` | "
            f"{markdown_cell(experiment['status'])} | {experiment['focus_score']} | "
            f"{wall_hours} | {estimate.get('cpu_hours', 'n/a')} | "
            f"{estimate.get('maximum_memory_gb', 'n/a')} | "
            f"{estimate.get('maximum_runs', 'n/a')} |"
        )
    if not plan["critical_experiments"]:
        lines.append("| - | none | - | - | - | - | - | - |")

    lines.extend(["", "## Attention Contracts", ""])
    if not plan["critical_experiments"]:
        lines.append("No critical experiments selected.")
    for experiment in plan["critical_experiments"]:
        contract = experiment.get("attention_contract")
        if not contract:
            lines.extend([
                f"### {experiment['id']}",
                "",
                "Legacy queue; no attention contract recorded.",
            ])
            continue
        lines.extend([
            f"### {experiment['id']}",
            "",
            f"**Decisive evidence:** {contract['decisive_evidence']}",
            "",
            f"**If inconclusive:** {contract['inconclusive_decision']}",
            "",
            f"**Local ambiguity rule:** {contract['local_ambiguity_rule']}",
            "",
            f"**Rerank trigger:** {contract['rerank_trigger']}",
            "",
            "**Excluded peripheral work:**",
        ])
        lines.extend(f"- {item}" for item in contract["peripheral_exclusions"])

    lines.extend([
        "",
        "## Optional Stage Estimates",
        "",
        "| Experiment | Stage | Wall seconds | CPU h | Memory GiB | Shards | Dominant |",
        "|---|---|---:|---:|---:|---:|---:|",
    ])
    stage_rows = 0
    for experiment in plan["critical_experiments"]:
        estimate = experiment.get("resource_estimate") or {}
        dominant_stage_id = estimate.get("dominant_stage_id")
        for stage in estimate.get("stages") or []:
            stage_rows += 1
            lines.append(
                f"| `{markdown_cell(experiment['id'])}` | "
                f"`{markdown_cell(stage['id'])}` | "
                f"{stage.get('wall_clock_seconds', 'n/a')} | {stage.get('cpu_hours', 'n/a')} | "
                f"{stage['maximum_memory_gb']} | {stage['parallel_shards']} | "
                f"{str(stage['id'] == dominant_stage_id).lower()} |"
            )
    if not stage_rows:
        lines.append("| none | - | - | - | - | - | - |")

    lines.extend([
        "",
        "## Claim Matrix",
        "",
        "| Claim | Verdict | Independently verified | Linked experiments |",
        "|---|---|---:|---|",
    ])
    for claim in plan.get("claim_matrix", []):
        linked = ", ".join(f"`{item}`" for item in claim["linked_experiments"])
        lines.append(
            f"| `{markdown_cell(claim['id'])}` | {markdown_cell(claim['verdict'])} | "
            f"{str(claim['independently_verified']).lower()} | {linked} |"
        )
    if not plan.get("claim_matrix"):
        lines.append("| none | - | - | - |")

    for claim in plan.get("claim_matrix", []):
        lines.extend([
            "",
            f"### {claim['id']}",
            "",
            f"**Statement:** {claim['statement']}",
            "",
            f"**Scope:** {claim['scope']}",
            "",
            f"**Target:** {claim['target_result']}",
            "",
            f"**Observed:** {claim['observed_result']}",
        ])
        if claim["scope_deviations"]:
            lines.extend(["", "**Scope deviations:**"])
            lines.extend(f"- {item}" for item in claim["scope_deviations"])
        if claim["blockers"]:
            lines.extend(["", "**Blockers:**"])
            lines.extend(f"- {item}" for item in claim["blockers"])

    graph = plan.get("experiment_graph", {})
    lines.extend([
        "",
        "## Run Table",
        "",
        "| Run | Experiment | Status | Depends on | Failure reason |",
        "|---|---|---|---|---|",
    ])
    for run in graph.get("run_nodes", []):
        dependencies = ", ".join(f"`{item}`" for item in run["depends_on_runs"])
        lines.append(
            f"| `{markdown_cell(run['id'])}` | `{markdown_cell(run['experiment_id'])}` | "
            f"{markdown_cell(run['status'])} | {dependencies or '-'} | "
            f"{markdown_cell(run.get('failure_reason') or '-')} |"
        )
    if not graph.get("run_nodes"):
        lines.append("| none | - | - | - | - |")

    lines.extend(["", "## Experiment Dependencies", ""])
    candidate_edges = graph.get("candidate_edges", [])
    if candidate_edges:
        lines.extend(
            f"- `{edge['from']}` -> `{edge['to']}` ({edge['kind']})"
            for edge in candidate_edges
        )
    else:
        lines.append("- None")

    lines.extend(["", "## Corrections", ""])
    corrections = plan.get("corrections", [])
    if corrections:
        for correction in corrections:
            lines.extend([
                f"### {correction['id']}",
                "",
                f"- Record: `{correction['record_type']}:{correction['record_id']}`",
                f"- Field: `{correction['field']}`",
                f"- Prior: `{markdown_cell(correction['prior_value'])}`",
                f"- Corrected: `{markdown_cell(correction['corrected_value'])}`",
                f"- Reason: {correction['reason']}",
                "",
            ])
    else:
        lines.append("No corrections recorded.")

    lines.extend(["", "## Gates", ""])
    lines.extend(
        f"- `{gate}`: {str(value).lower()}"
        for gate, value in sorted(plan["gates"].items())
    )
    lines.extend(["", f"Plan SHA-256: `{plan['plan_sha256']}`", ""])
    return "\n".join(lines)


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QueueError(f"cannot load {path}: {exc}") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path, help="write a deterministic Markdown report")
    parser.add_argument(
        "--check-only", action="store_true", help="validate without selecting"
    )
    args = parser.parse_args()
    try:
        queue = load(args.queue)
        validate_queue(queue)
        if args.check_only:
            print(json.dumps({"valid": True, "queue_sha256": digest(queue)}, indent=2))
            return 0
        plan = select(queue)
    except QueueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, indent=2), file=sys.stderr)
        return 2
    encoded = (json.dumps(plan, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if args.output is not None:
        write_atomic(args.output, encoded)
    if args.report is not None:
        write_atomic(args.report, render_markdown(plan).encode("utf-8"))
    print(encoded.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
