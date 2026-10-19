"""Stable digest of the scientific terms across preparation and approval.

Lifecycle metadata and runner paths may change at approval. The selected
sections below may not; this digest is checked at seed reveal.
"""
from __future__ import annotations

import hashlib
import json

SCIENTIFIC_KEYS = (
    "id", "hypothesis_id", "goal_id", "question_id", "source_plan", "controls",
    "independent_variables", "metrics", "relation_semantics", "preregistered_prediction",
    "analysis", "replication", "budget", "stopping_rules", "invalidation_rules",
    "required_artifacts", "success_criterion", "falsification_criterion",
    "decision_impact", "scope_relation",
)


def digest(experiment: dict) -> str:
    scientific = {key: experiment[key] for key in SCIENTIFIC_KEYS}
    inputs = dict(experiment["inputs"])
    inputs.pop("implementation", None)
    scientific["inputs"] = inputs
    encoded = json.dumps(scientific, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
