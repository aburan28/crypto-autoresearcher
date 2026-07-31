#!/usr/bin/env python3
"""Public surface-level hazard guards for low-term total-2 QR rows.

P227 showed that a clean aggregate policy switch must abstain on 1136_1143:
every candidate policy has a public QR false-positive surface, even though the
best-ranked low_constant branch contains a true below-rho scalar route.  This
probe searches public row/surface guards that can reduce that false-positive
hazard without using scalar labels in selection.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_public_surface_hazard_guard_probe.json"
DEFAULT_POLICY = "low_constant"

GuardFn = Callable[[dict[str, Any]], bool]


@dataclass(frozen=True)
class Guard:
    name: str
    family: str
    specificity: int
    public_description: str
    predicate: GuardFn


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(part.strip()) for part in raw.split(",") if part.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**12) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def window_label(path: Path) -> str:
    match = re.search(r"(\d+_\d+)", path.name)
    return match.group(1) if match else path.stem


def salt_number(row_key: Any) -> int | None:
    match = re.search(r"salt(\d+)$", str(row_key or ""))
    return int(match.group(1)) if match else None


def base_public_row(row: dict[str, Any]) -> bool:
    return bool(row.get("public_zero_recovered") and row.get("fingerprint_complete"))


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    candidate = row.get("chosen_candidate") if isinstance(row.get("chosen_candidate"), dict) else {}
    coeffs = row.get("selected_factor_coefficients") or {}
    return {
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "row_key": row.get("row_key"),
        "salt": salt_number(row.get("row_key")),
        "policy": row.get("policy"),
        "candidate_count": int_value(row.get("candidate_count")),
        "evaluated_factor_count": int_value(row.get("evaluated_factor_count")),
        "selector_eval_ops": int_value(row.get("selector_eval_ops")),
        "factor_index": int_value(candidate.get("factor_index")),
        "factor_total_degree": int_value(candidate.get("factor_total_degree")),
        "factor_monomials": int_value(candidate.get("factor_monomials")),
        "selected_surface_zero_leaves": int_value(candidate.get("selected_surface_zero_leaves")),
        "factor_root_scan_ops": int_value(candidate.get("factor_root_scan_ops")),
        "selected_leaf_count": int_value(row.get("selected_leaf_count")),
        "factor_zero_leaf_count": int_value(row.get("factor_zero_leaf_count")),
        "selected_missed_leaf_count": int_value(row.get("selected_missed_leaf_count")),
        "selected_root_pair_count": int_value(row.get("selected_root_pair_count")),
        "recovered_root_count": int_value(row.get("recovered_root_count")),
        "root_recovery_ops_saved_vs_scan": int_value(row.get("root_recovery_ops_saved_vs_scan")),
        "public_factor_quadratic_root_ops": int_value(row.get("public_factor_quadratic_root_ops")),
        "public_factor_quadratic_root_ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "fingerprint_constant": coeffs.get("constant"),
        "fingerprint_b_coeff": coeffs.get("b_coeff"),
        "fingerprint_term_count": coeffs.get("term_count"),
        "public_zero_recovered": bool(row.get("public_zero_recovered")),
        "fingerprint_complete": bool(row.get("fingerprint_complete")),
        "evaluation_quadratic_preserves_selected_root_pairs": bool(
            row.get("quadratic_preserves_selected_root_pairs")
        ),
        "evaluation_chosen_false_positive_source": bool(row.get("chosen_false_positive_source")),
        "evaluation_public_factor_quadratic_root_beats_rho": bool(
            row.get("public_factor_quadratic_root_beats_rho")
        ),
    }


def load_policy_rows(paths: list[Path], policy: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in paths:
        data = load_json(path)
        policy_rows = data.get("policy_rows") if isinstance(data.get("policy_rows"), dict) else {}
        for row in policy_rows.get(policy) or []:
            if isinstance(row, dict):
                rows.append({"source": str(path), "window": window_label(path), **row})
    return rows


def build_guards(train_rows: list[dict[str, Any]]) -> list[Guard]:
    def guard(name: str, family: str, specificity: int, desc: str, fn: GuardFn) -> Guard:
        return Guard(name, family, specificity, desc, fn)

    guards: list[Guard] = [
        guard("public_zero", "base", 0, "chosen public factor has a complete zero row", base_public_row),
        guard(
            "no_selected_missed_leaf",
            "strict_local_zero",
            4,
            "chosen factor zeros every selected leaf inspected by the public QR row",
            lambda row: base_public_row(row) and int_value(row.get("selected_missed_leaf_count")) == 0,
        ),
        guard(
            "single_selected_leaf",
            "strict_local_zero",
            3,
            "public QR row is a single selected-leaf explanation",
            lambda row: base_public_row(row) and int_value(row.get("selected_leaf_count")) <= 1,
        ),
        guard(
            "single_zero_leaf_no_missed",
            "strict_local_zero",
            6,
            "single selected leaf, one public zero leaf, and no missed selected leaf",
            lambda row: (
                base_public_row(row)
                and int_value(row.get("selected_leaf_count")) <= 1
                and int_value(row.get("factor_zero_leaf_count")) == 1
                and int_value(row.get("selected_missed_leaf_count")) == 0
            ),
        ),
        guard(
            "root_savings_ge_12",
            "cost_margin",
            2,
            "direct QR root recovery saves at least 12 operations versus source root scan",
            lambda row: base_public_row(row) and int_value(row.get("root_recovery_ops_saved_vs_scan")) >= 12,
        ),
        guard(
            "selector_eval_ops_le_45",
            "cost_margin",
            2,
            "public selector work is at most 45 operations",
            lambda row: base_public_row(row) and int_value(row.get("selector_eval_ops")) <= 45,
        ),
    ]

    thresholds = sorted(
        {
            int_value(row.get("selector_eval_ops"))
            for row in train_rows
            if base_public_row(row) and row.get("selector_eval_ops") is not None
        }
    )
    for threshold in thresholds:
        guards.append(
            guard(
                f"selector_eval_ops_le_{threshold}",
                "selector_threshold",
                1,
                f"public selector work is at most {threshold} operations",
                lambda row, threshold=threshold: base_public_row(row)
                and int_value(row.get("selector_eval_ops")) <= threshold,
            )
        )
    return guards


def summarize_rows(rows: list[dict[str, Any]], guard: Guard) -> dict[str, Any]:
    selected = [row for row in rows if guard.predicate(row)]
    ratios = [
        float_value(row.get("public_factor_quadratic_root_ops_over_rho"))
        for row in selected
        if row.get("public_factor_quadratic_root_ops_over_rho") is not None
    ]
    false_positive = [
        row for row in selected if row.get("chosen_false_positive_source")
        or (row.get("fingerprint_complete") and not row.get("quadratic_preserves_selected_root_pairs"))
    ]
    preserving = [row for row in selected if row.get("quadratic_preserves_selected_root_pairs")]
    below_rho = [row for row in selected if row.get("public_factor_quadratic_root_beats_rho")]
    missed_total = sum(int_value(row.get("selected_missed_leaf_count")) for row in selected)
    return {
        "guard": guard.name,
        "guard_family": guard.family,
        "guard_specificity": guard.specificity,
        "public_description": guard.public_description,
        "surface_count": len(rows),
        "selected_surface_count": len(selected),
        "quadratic_preserving_surface_count": len(preserving),
        "quadratic_false_positive_surface_count": len(false_positive),
        "charged_below_rho_count": len(below_rho),
        "selected_missed_leaf_total": missed_total,
        "max_selected_leaf_count": max(
            [int_value(row.get("selected_leaf_count")) for row in selected] or [0]
        ),
        "mean_charged_ops_over_rho": round(sum(ratios) / len(ratios), 8) if ratios else None,
        "max_charged_ops_over_rho": max(ratios) if ratios else None,
        "precision": ratio(len(preserving), len(selected)),
        "selected_rows": [compact_row(row) for row in selected],
        "false_positive_rows": [compact_row(row) for row in false_positive],
        "best_rows": [
            compact_row(row)
            for row in sorted(
                selected,
                key=lambda row: (
                    float_value(row.get("public_factor_quadratic_root_ops_over_rho")),
                    str(row.get("surface_id")),
                ),
            )[:8]
        ],
    }


def guard_score(summary: dict[str, Any]) -> tuple[Any, ...]:
    eligible = bool(
        int_value(summary.get("selected_surface_count")) > 0
        and int_value(summary.get("quadratic_preserving_surface_count")) > 0
        and int_value(summary.get("quadratic_false_positive_surface_count")) == 0
    )
    return (
        0 if eligible else 1,
        int_value(summary.get("quadratic_false_positive_surface_count")),
        int_value(summary.get("selected_missed_leaf_total")),
        int_value(summary.get("max_selected_leaf_count")),
        -int_value(summary.get("charged_below_rho_count")),
        -int_value(summary.get("quadratic_preserving_surface_count")),
        float_value(summary.get("max_charged_ops_over_rho")),
        -int_value(summary.get("guard_specificity")),
        str(summary.get("guard")),
    )


def select_guard(train_rows: list[dict[str, Any]], guards: list[Guard]) -> dict[str, Any]:
    summaries = [summarize_rows(train_rows, guard) for guard in guards]
    summaries.sort(key=guard_score)
    selected = summaries[0] if summaries else None
    return {
        "selected_guard": selected.get("guard") if selected else None,
        "selected_guard_summary": selected,
        "ranked_guard_summaries": summaries,
    }


def online_stops_for_policy(data: dict[str, Any], policy: str) -> list[dict[str, Any]]:
    stops: list[dict[str, Any]] = []
    for key, replay in (data.get("replays") or {}).items():
        summary = replay.get("summary") if isinstance(replay, dict) else {}
        if not isinstance(summary, dict) or summary.get("policy") != policy:
            continue
        for kind in ("best_below_rho_stops", "best_scalar_stops"):
            for stop in summary.get(kind) or []:
                if isinstance(stop, dict):
                    stops.append({"replay_key": key, "stop_kind": kind, **stop})
    return stops


def stop_surface_ids(stop: dict[str, Any]) -> set[str]:
    surface_ids: set[str] = set()
    materialized = stop.get("materialized_stop_summary") or {}
    for surface_id in materialized.get("surface_ids") or []:
        surface_ids.add(str(surface_id))
    for attempt in stop.get("charged_attempts") or []:
        if isinstance(attempt, dict) and attempt.get("surface_id"):
            surface_ids.add(str(attempt.get("surface_id")))
    return surface_ids


def compact_stop(stop: dict[str, Any]) -> dict[str, Any]:
    return {
        "replay_key": stop.get("replay_key"),
        "stop_kind": stop.get("stop_kind"),
        "policy": stop.get("policy"),
        "order": stop.get("order"),
        "target": stop.get("target"),
        "transfer_index": stop.get("transfer_index"),
        "charged_source_attempt_ops": stop.get("charged_source_attempt_ops"),
        "charged_source_attempt_ops_over_rho": stop.get("charged_source_attempt_ops_over_rho"),
        "rho": stop.get("rho"),
        "stop_derived_secret": stop.get("stop_derived_secret"),
        "stop_public_key_verified": stop.get("stop_public_key_verified"),
        "stop_union_rank": stop.get("stop_union_rank"),
        "stop_union_relation_count": stop.get("stop_union_relation_count"),
        "surface_ids": sorted(stop_surface_ids(stop)),
    }


def evaluate_online(
    online_path: Path | None,
    policy: str,
    selected_surface_ids: set[str],
) -> dict[str, Any] | None:
    if not online_path or not online_path.exists():
        return None
    stops = online_stops_for_policy(load_json(online_path), policy)
    selected_stops = [
        stop
        for stop in stops
        if stop_surface_ids(stop) and stop_surface_ids(stop) <= selected_surface_ids
    ]
    below = [
        stop
        for stop in selected_stops
        if stop.get("charged_source_attempt_beats_rho") or stop.get("stop_kind") == "best_below_rho_stops"
    ]
    selected_stops.sort(key=lambda stop: float_value(stop.get("charged_source_attempt_ops_over_rho")))
    below.sort(key=lambda stop: float_value(stop.get("charged_source_attempt_ops_over_rho")))
    return {
        "online_source": str(online_path),
        "policy": policy,
        "scalar_stop_count": len(selected_stops),
        "below_rho_scalar_stop_count": len(below),
        "best_selected_scalar_stop": compact_stop(selected_stops[0]) if selected_stops else None,
        "best_selected_below_rho_stop": compact_stop(below[0]) if below else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-public-sources", default="")
    parser.add_argument("--test-public-source", type=Path)
    parser.add_argument("--test-online-source", type=Path)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    train_paths = parse_paths(args.train_public_sources)
    if not train_paths:
        raise ValueError("--train-public-sources is required")
    if not args.test_public_source or not args.test_public_source.exists():
        raise FileNotFoundError(args.test_public_source)

    train_rows = load_policy_rows(train_paths, args.policy)
    test_rows = load_policy_rows([args.test_public_source], args.policy)
    guards = build_guards(train_rows)
    selection = select_guard(train_rows, guards)
    selected_guard_name = selection.get("selected_guard")
    guard_by_name = {guard.name: guard for guard in guards}
    selected_guard = guard_by_name[selected_guard_name]
    test_summary = summarize_rows(test_rows, selected_guard)
    selected_surface_ids = {
        str(row.get("surface_id"))
        for row in test_rows
        if selected_guard.predicate(row) and row.get("surface_id")
    }
    online_evaluation = evaluate_online(args.test_online_source, args.policy, selected_surface_ids)

    output = {
        "schema": "ecdlp.low_term_total2_public_surface_hazard_guard.v1",
        "method": "select_public_qr_surface_hazard_guard_on_prior_windows_then_apply_to_holdout",
        "policy": args.policy,
        "train_public_sources": [str(path) for path in train_paths],
        "test_public_source": str(args.test_public_source),
        "test_online_source": str(args.test_online_source) if args.test_online_source else None,
        "selected_rule": (
            "choose zero-false-positive prior guard minimizing public missed-leaf hazard "
            "before preserving-count/cost"
        ),
        "selection": selection,
        "test_summary": test_summary,
        "online_evaluation": online_evaluation,
        "summary": {
            "policy": args.policy,
            "selected_guard": selected_guard.name,
            "train_selected_surface_count": int_value(
                (selection.get("selected_guard_summary") or {}).get("selected_surface_count")
            ),
            "train_false_positive_count": int_value(
                (selection.get("selected_guard_summary") or {}).get("quadratic_false_positive_surface_count")
            ),
            "test_selected_surface_count": int_value(test_summary.get("selected_surface_count")),
            "test_false_positive_count": int_value(test_summary.get("quadratic_false_positive_surface_count")),
            "test_preserving_count": int_value(test_summary.get("quadratic_preserving_surface_count")),
            "test_below_rho_public_qr_count": int_value(test_summary.get("charged_below_rho_count")),
            "test_online_below_rho": bool(
                online_evaluation and online_evaluation.get("best_selected_below_rho_stop")
            ),
            "best_online_selected_stop": (
                online_evaluation or {}
            ).get("best_selected_below_rho_stop"),
            "honesty_boundary": [
                "Guard predicates use public QR row features only.",
                "Prior-window preservation and false-positive labels are used only to choose/freeze the guard.",
                "Held-out preservation and scalar recovery are evaluation-only.",
                "This still starts from generated signature/source summaries and is not a standalone ECDLP solver.",
            ],
        },
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
