#!/usr/bin/env python3
"""Validate the design bundle. This does not execute or approve experiments."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REQUIRED_EXPERIMENT_FIELDS = {
    "key", "title", "depends_on", "hypothesis", "arms", "parameters",
    "controls", "metrics", "success", "falsifier", "next_action", "implementation",
}
REQUIRED_DEGREE_FIELDS = {
    "input_max_degree", "final_basis_max_degree", "max_processed_degree",
    "certified_solving_degree", "first_observed_fall",
    "last_observed_fall_through_D", "certified_last_fall_degree",
    "dreg_top_homogeneous",
}
REQUIRED_COSTS = {
    "candidate_search", "graph_and_isogeny", "factor_base", "polynomial_build",
    "preprocessing", "solve_all_attempts", "extraction", "verification",
    "deduplication", "rank_filter", "linear_algebra", "toy_completion_check",
}
REQUIRED_OUTCOMES = {
    "completed", "no_certified_vertical_edge", "no_matched_factor_base",
    "unavailable_backend", "invalid_map", "invalid_solution_set",
    "no_dynamic_range", "right_censored", "failed_infrastructure",
    "no_useful_relations",
}


def validate(plan: dict[str, Any]) -> list[str]:
    """Return actionable design errors; passing is not scientific validation."""
    errors: list[str] = []
    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(plan.get("schema_version") == 1, "schema_version must be 1")
    require(plan.get("kind") == "experiment_design_bundle", "wrong bundle kind")
    require(plan.get("status") == "designed_not_dispatched", "design status required")
    require(plan.get("dispatchable") is False, "design bundle must not dispatch")
    require(plan.get("repository") == "aburan28/crypto-autoresearcher", "wrong repository")
    require(bool(plan.get("canonical_registration")), "registration boundary missing")
    budget = plan.get("budget", {})
    for name in ("total_cpu_hours", "total_wall_clock_seconds", "maximum_batches"):
        require(name in budget and budget[name] is None, f"{name} must remain advisory/null")
    for name in ("maximum_workers", "maximum_memory_gb", "process_watchdog_seconds"):
        value = budget.get(name)
        require(type(value) is int and value > 0, f"positive {name} required")
    require(bool(budget.get("watchdog_semantics")), "watchdog interpretation missing")

    metrics = plan.get("metrics", {})
    require(REQUIRED_DEGREE_FIELDS <= set(metrics.get("degree_fields", [])),
            "separate degree fields missing")
    require(REQUIRED_COSTS <= set(metrics.get("cost_components", [])),
            "complete cost accounting missing")
    for name in ("degree_rule", "rank_field", "zero_yield", "amortization_rule"):
        require(bool(metrics.get(name)), f"metric rule missing: {name}")
    require(REQUIRED_OUTCOMES <= set(plan.get("outcomes", [])), "outcome labels missing")
    for name in ("orientation", "factor_bases", "targets", "denominators", "holdout",
                 "statistics", "admission", "proof_search_map"):
        require(bool(plan.get("shared_protocol", {}).get(name)), f"protocol missing: {name}")

    profiles = plan.get("profiles", {})
    require(set(profiles) == {"smoke", "paired"}, "smoke and paired profiles required")
    for name, profile in profiles.items():
        for field in ("prime_fields", "binary_degrees", "factor_base_sizes",
                      "decomposition_lengths", "seeds", "isogeny_primes"):
            values = profile.get(field)
            require(isinstance(values, list) and bool(values)
                    and all(type(x) is int and x > 0 for x in values),
                    f"{name}: positive integer list required for {field}")
        require(all(x >= 4 for x in profile.get("decomposition_lengths", [])),
                f"{name}: do not reopen the closed m=3 screen")
        require(all(x <= 13 for x in profile.get("binary_degrees", [])),
                f"{name}: out-of-scope binary field")
        require(all(x <= 1021 for x in profile.get("prime_fields", [])),
                f"{name}: out-of-scope prime field")
        for field in ("classes_per_field", "vertices_per_class", "max_graph_distance",
                      "target_count", "replicates", "degree_checkpoint"):
            value = profile.get(field)
            require(type(value) is int and value > 0, f"{name}: invalid {field}")
    paired = profiles.get("paired", {})
    require(paired.get("classes_per_field", 0) >= 6, "paired class holdout coverage missing")
    require(len(paired.get("seeds", [])) >= 5, "paired seed replication missing")

    experiments = plan.get("experiments", [])
    require(isinstance(experiments, list) and bool(experiments), "experiments required")
    keys: list[str] = []
    for item in experiments:
        require(isinstance(item, dict), "experiment must be an object")
        if not isinstance(item, dict):
            continue
        key = item.get("key", "<missing>")
        require(isinstance(key, str), "experiment key must be a string")
        if not isinstance(key, str):
            continue
        keys.append(key)
        require(not (REQUIRED_EXPERIMENT_FIELDS - item.keys()), f"{key}: required fields missing")
        for field in ("hypothesis", "parameters", "success", "falsifier", "next_action", "implementation"):
            require(isinstance(item.get(field), str) and bool(item[field].strip()),
                    f"{key}: nonempty {field} required")
        for field in ("arms", "controls", "metrics"):
            require(isinstance(item.get(field), list) and len(item[field]) >= 2,
                    f"{key}: at least two {field} required")
        deps = item.get("depends_on")
        require(isinstance(deps, list) and all(isinstance(x, str) for x in deps),
                f"{key}: dependency list required")
        require("approved_by" not in item, f"{key}: no invented protocol approval")
    require(len(keys) == len(set(keys)), "duplicate experiment keys")
    graph = {x["key"]: x.get("depends_on", []) for x in experiments
             if isinstance(x, dict) and isinstance(x.get("key"), str)}
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(key: str) -> None:
        if key in visiting:
            errors.append(f"dependency cycle at {key}")
            return
        if key in visited:
            return
        visiting.add(key)
        deps = graph[key]
        if isinstance(deps, list):
            for dep in deps:
                if not isinstance(dep, str) or dep not in graph:
                    errors.append(f"{key}: unknown dependency {dep!r}")
                else:
                    visit(dep)
        visiting.remove(key)
        visited.add(key)
    for key in graph:
        visit(key)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=HERE / "campaign.json")
    args = parser.parse_args()
    try:
        plan = json.loads(args.path.read_text(encoding="utf-8"))
        if not isinstance(plan, dict):
            raise ValueError("top-level JSON must be an object")
        errors = validate(plan)
    except (OSError, ValueError, TypeError) as exc:
        print(f"INVALID: {exc}")
        return 2
    if errors:
        print("\n".join(f"INVALID: {x}" for x in errors))
        return 1
    print(f"PASS: {len(plan['experiments'])} experiment designs; no scientific runs or approval.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
