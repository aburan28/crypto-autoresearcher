#!/usr/bin/env python3
"""Pre-rank selector scout for branch-family ECDLP relation supply.

The branch-family sweep artifacts contain attempts where public branch hits are
streamed before verifier-derived rank/secret labels are used.  This diagnostic
searches for simple public selectors that predict rank-2 relation stops before
linear-rank acceptance.

Two feature families are reported separately:

* metadata_only: source/row-key metadata available before branch-hit scanning;
* hit_shape: public branch-hit multiplicities available after row scan, before
  using relation rank or derived-secret labels.

This remains toy-prime, model-bound relation-supply work.  A successful selector
is an index-calculus precursor signal, not target descent or a deployed break.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODELS = (
    "family_full_context_setup_integer",
    "family_full_attempt_setup_integer",
    "family_row_scan_only_integer",
    "shape_full_context_setup_integer",
    "shape_row_scan_only_integer",
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


def attempt_true(attempt: dict[str, Any]) -> bool:
    if attempt.get("accepted") or int_value(attempt.get("public_key_verified_branch_count")) > 0:
        return True
    return any(bool(branch.get("public_key_verified")) for branch in attempt.get("branch_results") or [])


def group_true(group: dict[str, Any]) -> bool:
    if group.get("has_public_key_verified_stop"):
        return True
    return any(attempt_true(attempt) for attempt in group.get("attempts") or [])


def row_key_salts(row_keys: list[Any]) -> list[int]:
    salts: list[int] = []
    for row_key in row_keys:
        match = re.search(r":salt(\d+)$", str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def gap_bucket(value: int) -> str:
    if value <= 1:
        return "0_1"
    if value <= 4:
        return "2_4"
    if value <= 8:
        return "5_8"
    return "9_plus"


def metadata_tokens(group: dict[str, Any], attempt: dict[str, Any]) -> set[str]:
    tokens = {
        f"meta.source_policy={attempt.get('source_policy')}",
        f"meta.top_k={int_value(attempt.get('top_k'))}",
        f"meta.row_key_count={len(attempt.get('row_keys') or [])}",
        f"meta.branch_count={int_value(attempt.get('branch_count'))}",
    }
    transfer_index = int_value(attempt.get("transfer_index"))
    if transfer_index:
        tokens.add(f"meta.transfer_mod2={transfer_index % 2}")
        tokens.add(f"meta.transfer_mod4={transfer_index % 4}")
        tokens.add(f"meta.transfer_mod8={transfer_index % 8}")
        tokens.add(f"meta.window_offset={transfer_index - window_start(group)}")
    salts = row_key_salts(attempt.get("row_keys") or [])
    if salts:
        tokens.add(f"meta.salt_count={len(salts)}")
        tokens.add(f"meta.salt_sum_mod4={sum(salts) % 4}")
        tokens.add(f"meta.salt_sum_mod8={sum(salts) % 8}")
        if len(salts) >= 2:
            gap = abs(max(salts) - min(salts))
            tokens.add(f"meta.salt_gap_bucket={gap_bucket(gap)}")
            tokens.add(f"meta.salt_gap_mod4={gap % 4}")
    return {token for token in tokens if not token.endswith("=None")}


def hit_branch_counts(attempt: dict[str, Any], nonduplicate_only: bool) -> Counter[str]:
    counts: Counter[str] = Counter()
    for hit in attempt.get("hit_records") or []:
        if nonduplicate_only and hit.get("duplicate"):
            continue
        branch_key = str(hit.get("branch_key") or "")
        if branch_key:
            counts[branch_key] += 1
    return counts


def threshold_tokens(prefix: str, value: int, max_threshold: int = 5) -> set[str]:
    return {f"{prefix}>={threshold}" for threshold in range(1, min(value, max_threshold) + 1)}


def hit_shape_tokens(_group: dict[str, Any], attempt: dict[str, Any]) -> set[str]:
    counts = hit_branch_counts(attempt, nonduplicate_only=False)
    nonduplicate_counts = hit_branch_counts(attempt, nonduplicate_only=True)
    context_rows = attempt.get("context_rows") or []
    hit_rows = [row for row in context_rows if int_value(row.get("point_match_count")) > 0]
    max_context_matches = max([int_value(row.get("point_match_count")) for row in context_rows] or [0])
    total_hits = sum(counts.values())
    total_nonduplicate_hits = sum(nonduplicate_counts.values())
    max_same = max(counts.values() or [0])
    max_same_nonduplicate = max(nonduplicate_counts.values() or [0])

    tokens: set[str] = set()
    tokens.update(threshold_tokens("hit.total_hits", total_hits))
    tokens.update(threshold_tokens("hit.nonduplicate_total_hits", total_nonduplicate_hits))
    tokens.update(threshold_tokens("hit.unique_hit_branches", len(counts)))
    tokens.update(threshold_tokens("hit.nonduplicate_unique_hit_branches", len(nonduplicate_counts)))
    tokens.update(threshold_tokens("hit.max_same_branch_hits", max_same))
    tokens.update(threshold_tokens("hit.nonduplicate_max_same_branch_hits", max_same_nonduplicate))
    tokens.update(threshold_tokens("hit.hit_context_rows", len(hit_rows)))
    tokens.update(threshold_tokens("hit.max_context_point_match_count", max_context_matches))
    for branch_key, count in counts.items():
        tokens.add(f"hit.contains_branch_key={branch_key}")
        if count >= 2:
            tokens.add(f"hit.duplicated_branch_key={branch_key}")
    for branch_key, count in nonduplicate_counts.items():
        if count >= 2:
            tokens.add(f"hit.nonduplicate_duplicated_branch_key={branch_key}")
    return tokens


def tokens_for(mode: str, group: dict[str, Any], attempt: dict[str, Any]) -> set[str]:
    if mode == "metadata_only":
        return metadata_tokens(group, attempt)
    if mode == "hit_shape":
        return hit_shape_tokens(group, attempt)
    raise ValueError(f"unknown mode: {mode}")


def model_ops_for_attempt(attempt: dict[str, Any]) -> dict[str, int]:
    existing = attempt.get("model_ops") or {}
    context_rows = attempt.get("context_rows") or []
    row_scan_ops = sum(int_value(row.get("row_scan_integer_ops")) for row in context_rows)
    context_setup_ops = sum(int_value(row.get("branch_candidate_count")) for row in context_rows)
    return {
        "family_full_context_setup_integer": int_value(existing.get("family_full_context_setup_integer")),
        "family_full_attempt_setup_integer": int_value(existing.get("family_full_attempt_setup_integer")),
        "family_row_scan_only_integer": int_value(existing.get("family_row_scan_only_integer")),
        "shape_full_context_setup_integer": row_scan_ops + context_setup_ops,
        "shape_row_scan_only_integer": row_scan_ops,
    }


def rule_specificity(rule_token: str) -> int:
    if "branch_key=" in rule_token:
        return 5
    if "source_policy=" in rule_token:
        return 4
    if "window_offset=" in rule_token or "salt_" in rule_token:
        return 3
    if "transfer_mod" in rule_token:
        return 2
    return 1


def candidate_tokens(groups: list[dict[str, Any]], mode: str, attempt_budget: int) -> list[str]:
    tokens: set[str] = set()
    for group in groups:
        for index, attempt in enumerate(group.get("attempts") or [], start=1):
            if attempt_budget and index > attempt_budget:
                break
            tokens.update(tokens_for(mode, group, attempt))
    return sorted(tokens)


def apply_rule(groups: list[dict[str, Any]], mode: str, rule_token: str, attempt_budget: int) -> dict[str, Any]:
    attempts_scanned = 0
    selected_count = 0
    true_stop_count = 0
    false_stop_count = 0
    missed_true_stop_count = 0
    selected_examples: list[dict[str, Any]] = []
    missed_windows: list[str] = []
    selected_windows: list[str] = []
    model_ops = {model: 0 for model in MODELS}
    rho = max([int_value(group.get("rho")) for group in groups] or [0])
    if rho <= 0:
        rho = 137

    for group in groups:
        selected_true = False
        for index, attempt in enumerate(group.get("attempts") or [], start=1):
            if attempt_budget and index > attempt_budget:
                break
            attempts_scanned += 1
            attempt_ops = model_ops_for_attempt(attempt)
            for model in MODELS:
                model_ops[model] += attempt_ops[model]
            if rule_token not in tokens_for(mode, group, attempt):
                continue
            selected_count += 1
            is_true = attempt_true(attempt)
            selected_true = is_true
            if is_true:
                true_stop_count += 1
                selected_windows.append(str(group.get("window")))
            else:
                false_stop_count += 1
            counts = hit_branch_counts(attempt, nonduplicate_only=True)
            selected_examples.append(
                {
                    "attempt_index": index,
                    "best_branch": (attempt.get("best_branch") or {}).get("branch_key"),
                    "hit_branch_counts": dict(sorted(counts.items())),
                    "public_key_verified": is_true,
                    "rule_token": rule_token,
                    "transfer_index": attempt.get("transfer_index"),
                    "window": group.get("window"),
                }
            )
            break
        if group_true(group) and not selected_true:
            missed_true_stop_count += 1
            missed_windows.append(str(group.get("window")))

    model_summaries = {}
    for model in MODELS:
        model_summaries[model] = {
            "cost_per_true_stop_over_rho": ratio(model_ops[model], rho * true_stop_count) if true_stop_count else None,
            "ops": model_ops[model],
            "ops_over_rho": ratio(model_ops[model], rho),
        }
    return {
        "attempt_budget": attempt_budget,
        "attempts_scanned": attempts_scanned,
        "false_stop_count": false_stop_count,
        "group_count": len(groups),
        "missed_true_stop_count": missed_true_stop_count,
        "missed_windows": missed_windows,
        "mode": mode,
        "model_summaries": model_summaries,
        "rho": rho,
        "rule_specificity": rule_specificity(rule_token),
        "rule_token": rule_token,
        "selected_count": selected_count,
        "selected_examples": selected_examples[:40],
        "selected_windows": selected_windows,
        "true_group_count": sum(1 for group in groups if group_true(group)),
        "true_stop_count": true_stop_count,
    }


def choose_rule(groups: list[dict[str, Any]], mode: str, attempt_budget: int) -> dict[str, Any] | None:
    summaries = [apply_rule(groups, mode, token, attempt_budget) for token in candidate_tokens(groups, mode, attempt_budget)]
    useful = [summary for summary in summaries if summary["true_stop_count"] > 0]
    if not useful:
        return None
    total_true = sum(1 for group in groups if group_true(group))
    viable = [
        summary
        for summary in useful
        if summary["false_stop_count"] == 0
        and summary["missed_true_stop_count"] == 0
        and summary["true_stop_count"] == total_true
    ]
    if not viable:
        viable = [summary for summary in useful if summary["false_stop_count"] == 0]
    if not viable:
        viable = useful
    viable.sort(
        key=lambda summary: (
            summary["false_stop_count"],
            summary["missed_true_stop_count"],
            -summary["true_stop_count"],
            summary["model_summaries"]["shape_full_context_setup_integer"]["cost_per_true_stop_over_rho"] or 10**9,
            summary["rule_specificity"],
            summary["rule_token"],
        )
    )
    return {
        **viable[0],
        "candidate_count": len(summaries),
        "top_candidate_summaries": sorted(
            summaries,
            key=lambda summary: (
                summary["false_stop_count"],
                summary["missed_true_stop_count"],
                -summary["true_stop_count"],
                summary["rule_specificity"],
                summary["rule_token"],
            ),
        )[:20],
    }


def claim_status(hit_validation: dict[str, Any] | None, metadata_validation: dict[str, Any] | None) -> str:
    if hit_validation:
        if hit_validation.get("false_stop_count"):
            return "BRANCH_FAMILY_PRECONTEXT_HIT_SHAPE_VALIDATION_FALSE_STOPS"
        if hit_validation.get("missed_true_stop_count"):
            return "BRANCH_FAMILY_PRECONTEXT_HIT_SHAPE_VALIDATION_MISSES"
        if int_value(hit_validation.get("true_stop_count")) > 0:
            cost = ((hit_validation.get("model_summaries") or {}).get("shape_full_context_setup_integer") or {}).get(
                "cost_per_true_stop_over_rho"
            )
            if cost is not None and float(cost) < 1.0:
                return "BRANCH_FAMILY_PRECONTEXT_HIT_SHAPE_VALIDATION_SHAPE_CONTEXT_BELOW_RHO"
            return "BRANCH_FAMILY_PRECONTEXT_HIT_SHAPE_VALIDATION_TRUE_STOPS_ABOVE_RHO"
        return "BRANCH_FAMILY_PRECONTEXT_HIT_SHAPE_NO_VALIDATION_TRUE_STOPS"
    if metadata_validation and int_value(metadata_validation.get("true_stop_count")) > 0:
        if metadata_validation.get("false_stop_count"):
            return "BRANCH_FAMILY_PRECONTEXT_METADATA_VALIDATION_FALSE_STOPS"
        if metadata_validation.get("missed_true_stop_count"):
            return "BRANCH_FAMILY_PRECONTEXT_METADATA_VALIDATION_MISSES"
        return "BRANCH_FAMILY_PRECONTEXT_METADATA_VALIDATION_TRUE_STOPS"
    return "BRANCH_FAMILY_PRECONTEXT_NO_HIT_SHAPE_RULE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", action="append", required=True, help="Branch-family sweep artifact; repeatable.")
    parser.add_argument("--calibration-start", type=int, default=0)
    parser.add_argument("--calibration-end", type=int, required=True)
    parser.add_argument("--validation-min-start", type=int, default=0)
    parser.add_argument("--validation-max-start", type=int, default=0)
    parser.add_argument("--attempt-budget", type=int, default=4)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in args.artifact]
    groups = flatten_groups(paths)
    calibration_groups = [
        group
        for group in groups
        if window_start(group) <= args.calibration_end
        and (not args.calibration_start or window_start(group) >= args.calibration_start)
    ]
    validation_groups = [group for group in groups if window_start(group) > args.calibration_end]
    if args.validation_min_start:
        validation_groups = [group for group in validation_groups if window_start(group) >= args.validation_min_start]
    if args.validation_max_start:
        validation_groups = [group for group in validation_groups if window_start(group) <= args.validation_max_start]

    mode_results: dict[str, dict[str, Any]] = {}
    for mode in ("metadata_only", "hit_shape"):
        selected = choose_rule(calibration_groups, mode, args.attempt_budget)
        validation = None
        if selected:
            validation = apply_rule(validation_groups, mode, str(selected.get("rule_token")), args.attempt_budget)
        mode_results[mode] = {
            "calibration": selected,
            "validation": validation,
        }

    payload = {
        "artifacts": {"input_artifacts": [str(path) for path in paths]},
        "claim_status": claim_status(
            mode_results["hit_shape"].get("validation"),
            mode_results["metadata_only"].get("validation"),
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selector is learned from saved branch-family sweeps.",
            "metadata_only tokens are available before branch-hit scanning but may be too weak.",
            "hit_shape tokens are available after public row/branch hit scanning and before relation-rank or derived-secret acceptance.",
            "Verifier labels are used only for scoring; this is relation-supply triage, not target descent or a deployed-curve break.",
        ],
        "parameters": {
            "attempt_budget": args.attempt_budget,
            "calibration_end": args.calibration_end,
            "calibration_start": args.calibration_start,
            "validation_max_start": args.validation_max_start,
            "validation_min_start": args.validation_min_start,
        },
        "schema": "ecdlp.low_term_total2_branch_family_precontext_rank_predictor_scout.v1",
        "source_group_count": len(groups),
        "source_windows": [str(group.get("window")) for group in groups],
        "splits": {
            "calibration_group_count": len(calibration_groups),
            "calibration_windows": [str(group.get("window")) for group in calibration_groups],
            "validation_group_count": len(validation_groups),
            "validation_windows": [str(group.get("window")) for group in validation_groups],
        },
        "modes": mode_results,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "hit_shape": {
                    "calibration_rule": ((mode_results["hit_shape"].get("calibration") or {}).get("rule_token")),
                    "validation": {
                        key: (mode_results["hit_shape"].get("validation") or {}).get(key)
                        for key in ("true_stop_count", "false_stop_count", "missed_true_stop_count", "model_summaries")
                    },
                },
                "metadata_only": {
                    "calibration_rule": ((mode_results["metadata_only"].get("calibration") or {}).get("rule_token")),
                    "validation": {
                        key: (mode_results["metadata_only"].get("validation") or {}).get(key)
                        for key in ("true_stop_count", "false_stop_count", "missed_true_stop_count")
                    },
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
