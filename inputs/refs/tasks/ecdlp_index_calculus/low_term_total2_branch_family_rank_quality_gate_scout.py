#!/usr/bin/env python3
"""Rank-quality gate for branch-family streaming artifacts.

The branch-family streaming sweep shows a useful but bursty source stream:
some windows contain rank-2 verifier-derived stops, while nearby windows have
only rank-1 branch hits.  This scout asks whether a simple, public-ish
post-hit token can avoid spending the full source stream on rank-1/no-stop
windows.

The selector is deliberately narrow: scan attempts in source order up to a
budget and stop only when a branch has at least N unique relation forms.  The
label uses verifier-derived secret recovery, but the selector itself does not.
This remains a toy-prime, model-bound diagnostic and is not target descent.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODELS = (
    "family_full_context_setup_integer",
    "family_full_attempt_setup_integer",
    "family_row_scan_only_integer",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def window_start(group: dict[str, Any]) -> int:
    if int_value(group.get("window_start")):
        return int_value(group.get("window_start"))
    window = str(group.get("window") or "")
    if "_" in window:
        return int_value(window.split("_", 1)[0])
    return 0


def flatten_groups(paths: list[Path]) -> list[dict[str, Any]]:
    by_window: dict[str, dict[str, Any]] = {}
    for path in paths:
        payload = load_json(path)
        for group in payload.get("groups") or []:
            key = str(group.get("window") or group.get("source_path") or window_start(group))
            by_window[key] = {**group, "artifact_path": str(path)}
    return sorted(by_window.values(), key=lambda group: (window_start(group), str(group.get("window"))))


def selected_branch(attempt: dict[str, Any], min_forms: int) -> dict[str, Any] | None:
    for branch in attempt.get("branch_results") or []:
        if int_value(branch.get("accepted_relation_count")) >= min_forms:
            return branch
    return None


def apply_policy(groups: list[dict[str, Any]], attempt_budget: int, min_forms: int) -> dict[str, Any]:
    attempts_scanned = 0
    false_stop_count = 0
    true_stop_count = 0
    missed_true_stop_count = 0
    selected_count = 0
    scanned_group_count = len(groups)
    model_ops = {model: 0 for model in MODELS}
    examples: list[dict[str, Any]] = []
    missed_windows: list[str] = []
    selected_windows: list[str] = []
    rho = max([int_value(group.get("rho")) for group in groups] or [0])
    if rho <= 0:
        rho = 137
    for group in groups:
        group_selected = False
        group_verified = False
        for index, attempt in enumerate(group.get("attempts") or [], start=1):
            if index > attempt_budget:
                break
            attempts_scanned += 1
            for model in MODELS:
                model_ops[model] += int_value((attempt.get("model_ops") or {}).get(model))
            branch = selected_branch(attempt, min_forms)
            if branch is None:
                continue
            selected_count += 1
            group_selected = True
            group_verified = bool(branch.get("public_key_verified"))
            if group_verified:
                true_stop_count += 1
                selected_windows.append(str(group.get("window")))
            else:
                false_stop_count += 1
            examples.append(
                {
                    "accepted_relation_count": int_value(branch.get("accepted_relation_count")),
                    "attempt_index": index,
                    "branch_key": branch.get("branch_key"),
                    "public_key_verified": group_verified,
                    "rank": int_value(branch.get("rank")),
                    "transfer_index": attempt.get("transfer_index"),
                    "window": group.get("window"),
                }
            )
            break
        if group.get("has_public_key_verified_stop") and not group_verified:
            missed_true_stop_count += 1
            missed_windows.append(str(group.get("window")))
        if not group_selected and not group.get("attempts"):
            examples.append({"window": group.get("window"), "note": "no attempts in group"})
    summaries = {}
    for model in MODELS:
        summaries[model] = {
            "cost_per_true_stop_over_rho": ratio(model_ops[model], rho * true_stop_count) if true_stop_count else None,
            "ops": model_ops[model],
            "ops_over_rho": ratio(model_ops[model], rho),
        }
    return {
        "attempt_budget": attempt_budget,
        "attempts_scanned": attempts_scanned,
        "false_stop_count": false_stop_count,
        "group_count": scanned_group_count,
        "min_forms": min_forms,
        "missed_true_stop_count": missed_true_stop_count,
        "missed_windows": missed_windows,
        "model_summaries": summaries,
        "rho": rho,
        "selected_count": selected_count,
        "selected_windows": selected_windows,
        "true_stop_count": true_stop_count,
        "selected_examples": examples[:40],
    }


def choose_policy(calibration_groups: list[dict[str, Any]], max_budget: int, min_forms_values: list[int]) -> dict[str, Any] | None:
    candidates: list[dict[str, Any]] = []
    for min_forms in min_forms_values:
        for attempt_budget in range(1, max_budget + 1):
            summary = apply_policy(calibration_groups, attempt_budget, min_forms)
            candidates.append(summary)
    viable = [
        item
        for item in candidates
        if item["true_stop_count"] > 0
        and item["false_stop_count"] == 0
        and item["missed_true_stop_count"] == 0
    ]
    if not viable:
        viable = [
            item
            for item in candidates
            if item["true_stop_count"] > 0 and item["false_stop_count"] == 0
        ]
    if not viable:
        return None
    viable.sort(
        key=lambda item: (
            (item["model_summaries"]["family_full_context_setup_integer"]["cost_per_true_stop_over_rho"] is None),
            item["model_summaries"]["family_full_context_setup_integer"]["cost_per_true_stop_over_rho"] or 10**9,
            item["missed_true_stop_count"],
            item["attempt_budget"],
            item["min_forms"],
        )
    )
    return {**viable[0], "all_candidate_summaries": candidates}


def fixed_policy(calibration_groups: list[dict[str, Any]], attempt_budget: int, min_forms: int) -> dict[str, Any]:
    summary = apply_policy(calibration_groups, attempt_budget, min_forms)
    return {**summary, "fixed_policy": True}


def claim_status(validation: dict[str, Any] | None) -> str:
    if not validation:
        return "BRANCH_FAMILY_RANK_QUALITY_GATE_NO_VALIDATION"
    if validation.get("false_stop_count"):
        return "BRANCH_FAMILY_RANK_QUALITY_GATE_VALIDATION_FALSE_STOPS"
    if validation.get("missed_true_stop_count"):
        return "BRANCH_FAMILY_RANK_QUALITY_GATE_VALIDATION_MISSES_TRUE_STOPS"
    if int_value(validation.get("true_stop_count")) <= 0:
        return "BRANCH_FAMILY_RANK_QUALITY_GATE_NO_VALIDATION_TRUE_STOPS"
    cost = ((validation.get("model_summaries") or {}).get("family_full_context_setup_integer") or {}).get(
        "cost_per_true_stop_over_rho"
    )
    if cost is not None and float(cost) < 1.0:
        return "BRANCH_FAMILY_RANK_QUALITY_GATE_VALIDATION_FULL_CONTEXT_BELOW_RHO"
    return "BRANCH_FAMILY_RANK_QUALITY_GATE_VALIDATION_TRUE_STOPS_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", action="append", required=True, help="Branch-family sweep artifact; repeatable.")
    parser.add_argument("--calibration-end", type=int, required=True)
    parser.add_argument("--validation-min-start", type=int, default=0)
    parser.add_argument("--max-budget", type=int, default=8)
    parser.add_argument("--min-forms", type=int, action="append", default=[2])
    parser.add_argument("--fixed-attempt-budget", type=int, default=0)
    parser.add_argument("--fixed-min-forms", type=int, default=0)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in args.artifact]
    groups = flatten_groups(paths)
    calibration_groups = [group for group in groups if window_start(group) <= args.calibration_end]
    validation_groups = [group for group in groups if window_start(group) > args.calibration_end]
    if args.validation_min_start:
        validation_groups = [group for group in validation_groups if window_start(group) >= args.validation_min_start]
    policy_mode = "calibration_selected"
    if args.fixed_attempt_budget > 0:
        policy_mode = "fixed"
        selected = fixed_policy(
            calibration_groups,
            args.fixed_attempt_budget,
            args.fixed_min_forms if args.fixed_min_forms > 0 else int_value(args.min_forms[0], 2),
        )
    else:
        selected = choose_policy(calibration_groups, args.max_budget, args.min_forms)
    validation = None
    if selected:
        validation = apply_policy(validation_groups, int_value(selected.get("attempt_budget")), int_value(selected.get("min_forms")))
    payload = {
        "artifacts": {"input_artifacts": [str(path) for path in paths]},
        "calibration": selected,
        "claim_status": claim_status(validation),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this is a post-branch-hit rank-quality gate over saved branch-family sweeps.",
            "The selector uses accepted relation-form count, not derived secret, but still requires branch streaming/form emission.",
            "This can reduce no-stop/rank-1 spending under an attempt budget; it is not target descent or a deployed-curve break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "fixed_attempt_budget": args.fixed_attempt_budget,
            "fixed_min_forms": args.fixed_min_forms,
            "max_budget": args.max_budget,
            "min_forms_values": args.min_forms,
            "policy_mode": policy_mode,
            "validation_min_start": args.validation_min_start,
        },
        "schema": "ecdlp.low_term_total2_branch_family_rank_quality_gate_scout.v1",
        "source_group_count": len(groups),
        "source_windows": [str(group.get("window")) for group in groups],
        "validation": validation,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "calibration": {
                    key: selected.get(key) if selected else None
                    for key in ("attempt_budget", "min_forms", "true_stop_count", "false_stop_count", "missed_true_stop_count")
                },
                "validation": {
                    key: validation.get(key) if validation else None
                    for key in ("true_stop_count", "false_stop_count", "missed_true_stop_count", "model_summaries")
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
