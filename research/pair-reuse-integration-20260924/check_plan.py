#!/usr/bin/env python3
"""Check selected design-contract guardrails; does not admit or run research."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REQUIRED_ARMS = {"canonical_reused", "expanded_reused", "expanded_rebuilt"}
REQUIRED_COSTS = {
    "target_admission_and_generation", "base_discovery_or_loading",
    "field_conversion", "table_construction", "canonicalization_and_inverse_transport",
    "all_query_work_including_misses", "exact_witness_verification", "serialization",
    "process_lifetime",
}
REQUIRED_CONTROLS = {
    "Independent N19 replay of the accepted exact-three panel and all 6,909 frozen target-orbit cases before timing.",
    "Every returned witness replays by exact group addition to its original target and every summand is in the admitted base.",
    "Fresh process per job; no hidden target joins, previous table, point-to-log table, full-group catalog, or witness cache.",
}


def validate(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    def require(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)

    require(plan.get("schema_version") == 1, "schema_version must be 1")
    require(plan.get("kind") == "experiment_design_bundle", "wrong bundle kind")
    require(plan.get("repository") == "aburan28/crypto-autoresearcher", "wrong repository")
    require(plan.get("status") == "designed_not_dispatched", "must remain design-only")
    require(plan.get("dispatchable") is False, "dispatchable must be false")
    require("canonical EXP/H/IDEA id is minted" in plan.get("canonical_registration", ""),
            "canonical ID registration boundary missing")
    prereq = plan.get("prerequisite", {})
    require(prereq.get("pull_request") == 1382, "PR #1382 evidence gate missing")
    require("without weakening" in prereq.get("required_disposition", ""),
            "validation-repair safeguard missing")

    arms = plan.get("arms", {})
    require(set(arms) == REQUIRED_ARMS, "canonical, expanded-reused, and expanded-rebuilt arms required")
    require("Primary comparator" in arms.get("expanded_reused", ""),
            "expanded reused table must be primary comparator")
    require("per request" in arms.get("expanded_rebuilt", ""),
            "rebuild arm must charge each request")

    workloads = plan.get("workloads", {})
    require(workloads.get("query_counts") == [1, 32, 512], "query ladder mismatch")
    require(workloads.get("independent_target_streams_per_base") == 8,
            "eight independent streams required")
    require(workloads.get("technical_repetitions_per_cell") == 4,
            "technical repetition count missing")
    require("prefixes" in workloads.get("stream_rule", ""), "shared stream-prefix rule missing")
    require("withheld" in workloads.get("target_rule", ""), "target sidecar must be withheld")

    require(REQUIRED_COSTS <= set(plan.get("cost_components", [])), "cost boundary incomplete")
    require(REQUIRED_CONTROLS <= set(plan.get("controls", [])), "correctness or leakage controls missing")
    analysis = plan.get("analysis", {})
    require(analysis.get("primary_cell") == "N23/K16, M=512", "primary cell must be frozen")
    require("upper endpoint < 1.0" in analysis.get("promotion_gate", ""),
            "uncertainty gate missing")
    require("never UNSAT" in analysis.get("censoring", ""), "censoring rule missing")
    require(bool(plan.get("dispatch_gate")) and len(plan["dispatch_gate"]) == 3,
            "all three dispatch gates required")
    forbidden = {"approved_by", "run_id", "experiment_id", "result", "conclusion"}
    require(not (forbidden & set(plan)), "design must not fabricate approval, run, or result state")
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
        print("\n".join(f"INVALID: {error}" for error in errors))
        return 1
    print("PASS: integration design guardrails; no approval or experiment execution claimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
