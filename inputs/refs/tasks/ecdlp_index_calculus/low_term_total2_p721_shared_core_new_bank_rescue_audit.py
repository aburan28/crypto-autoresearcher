#!/usr/bin/env python3
"""P721 new-bank rescue audit for P720 shared-core temporal failures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p720_shared_core_temporal_generalization_audit as p720


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P720 = STATE_DIR / "low_term_total2_p720_shared_core_temporal_generalization_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p721_shared_core_new_bank_rescue_audit_probe.json"
FIXED_TWO_BY_TWO = "two_by_two_any_cost_le_1p0:budget1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p720.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p720.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_groups(raw: str) -> tuple[str, ...]:
    values = tuple(item.strip() for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one policy group is required")
    return values


def make_policy_budgets(
    groups: tuple[str, ...],
    thresholds: tuple[float, ...],
    budgets: tuple[int, ...],
) -> list[p720.SharedPolicyBudget]:
    allowed = set(groups)
    return [
        p720.SharedPolicyBudget(policy, budget)
        for policy in p716.make_policies(thresholds)
        if policy.group in allowed
        for budget in budgets
    ]


def compact_or_none(report: dict[str, Any] | None) -> dict[str, Any] | None:
    return None if report is None else p720.compact_report(report)


def evaluate_all(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[p720.SharedPolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> list[dict[str, Any]]:
    return [
        p720.evaluate_policy_budget(reports, metadata, combo, factor_charge, sample_limit)
        for combo in combos
    ]


def choose_combo(combos: list[p720.SharedPolicyBudget], report: dict[str, Any]) -> p720.SharedPolicyBudget:
    return p720.combo_by_name(combos, str(report.get("policy_budget")))


def fixed_combo(combos: list[p720.SharedPolicyBudget]) -> p720.SharedPolicyBudget | None:
    try:
        return p720.combo_by_name(combos, FIXED_TWO_BY_TWO)
    except KeyError:
        return None


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[p720.SharedPolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]

    train_marginal = evaluate_all(train, metadata, combos, 0.0, sample_limit)
    train_new = evaluate_all(train, metadata, combos, factor_charge, sample_limit)
    selected_marginal_train = p720.choose_best(train_marginal)
    selected_new_train = p720.choose_best(train_new)
    selected_marginal_combo = choose_combo(combos, selected_marginal_train)
    selected_new_combo = choose_combo(combos, selected_new_train)

    holdout_marginal = evaluate_all(holdout, metadata, combos, 0.0, sample_limit)
    holdout_new = evaluate_all(holdout, metadata, combos, factor_charge, sample_limit)
    selected_from_marginal_holdout_marginal = p720.evaluate_policy_budget(
        holdout,
        metadata,
        selected_marginal_combo,
        0.0,
        sample_limit,
    )
    selected_from_marginal_holdout_new = p720.evaluate_policy_budget(
        holdout,
        metadata,
        selected_marginal_combo,
        factor_charge,
        sample_limit,
    )
    selected_from_new_holdout_marginal = p720.evaluate_policy_budget(
        holdout,
        metadata,
        selected_new_combo,
        0.0,
        sample_limit,
    )
    selected_from_new_holdout_new = p720.evaluate_policy_budget(
        holdout,
        metadata,
        selected_new_combo,
        factor_charge,
        sample_limit,
    )

    fixed = fixed_combo(combos)
    fixed_holdout_marginal = None
    fixed_holdout_new = None
    if fixed is not None:
        fixed_holdout_marginal = p720.evaluate_policy_budget(holdout, metadata, fixed, 0.0, sample_limit)
        fixed_holdout_new = p720.evaluate_policy_budget(holdout, metadata, fixed, factor_charge, sample_limit)

    return {
        **split,
        "fixed_two_by_two_1p0_holdout_marginal_existing_bank": fixed_holdout_marginal,
        "fixed_two_by_two_1p0_holdout_new_bank": fixed_holdout_new,
        "heldout_oracle_best_marginal_existing_bank": p720.choose_best(holdout_marginal),
        "heldout_oracle_best_new_bank": p720.choose_best(holdout_new),
        "marginal_train_selected_holdout_marginal_existing_bank": selected_from_marginal_holdout_marginal,
        "marginal_train_selected_holdout_new_bank": selected_from_marginal_holdout_new,
        "marginal_train_selected_policy_budget": selected_marginal_combo.name,
        "new_bank_train_selected_holdout_marginal_existing_bank": selected_from_new_holdout_marginal,
        "new_bank_train_selected_holdout_new_bank": selected_from_new_holdout_new,
        "new_bank_train_selected_policy_budget": selected_new_combo.name,
        "top_train_marginal_existing_bank": sorted(train_marginal, key=p720.eval_sort_key)[:8],
        "top_train_new_bank": sorted(train_new, key=p720.eval_sort_key)[:8],
        "train_window_count": len(train),
        "window_ranges": {
            "holdout": [[report["window_start"], report["window_end"]] for report in holdout[:3]],
            "holdout_last": None if not holdout else [holdout[-1]["window_start"], holdout[-1]["window_end"]],
            "train": [[report["window_start"], report["window_end"]] for report in train[:3]],
            "train_last": None if not train else [train[-1]["window_start"], train[-1]["window_end"]],
        },
    }


def below_count(split_reports: list[dict[str, Any]], key: str) -> int:
    return sum(1 for report in split_reports if (report.get(key) or {}).get("beats_rho_with_fallback"))


def compact_split(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixed_new": compact_or_none(report.get("fixed_two_by_two_1p0_holdout_new_bank")),
        "heldout_oracle_new": compact_or_none(report.get("heldout_oracle_best_new_bank")),
        "marginal_train_selected_new": compact_or_none(report.get("marginal_train_selected_holdout_new_bank")),
        "marginal_train_selected_policy_budget": report.get("marginal_train_selected_policy_budget"),
        "new_bank_train_selected_new": compact_or_none(report.get("new_bank_train_selected_holdout_new_bank")),
        "new_bank_train_selected_policy_budget": report.get("new_bank_train_selected_policy_budget"),
        "split": report.get("split"),
        "window_ranges": report.get("window_ranges"),
    }


def evaluate_universe(
    name: str,
    groups: tuple[str, ...],
    reports: list[dict[str, Any]],
    splits: list[dict[str, Any]],
    metadata: dict[str, Any],
    thresholds: tuple[float, ...],
    budgets: tuple[int, ...],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    combos = make_policy_budgets(groups, thresholds, budgets)
    split_reports = [
        evaluate_split(split, reports, metadata, combos, factor_charge, sample_limit)
        for split in splits
    ]
    full_marginal = evaluate_all(reports, metadata, combos, 0.0, sample_limit)
    full_new = evaluate_all(reports, metadata, combos, factor_charge, sample_limit)
    fixed = fixed_combo(combos)
    fixed_full_marginal = None
    fixed_full_new = None
    if fixed is not None:
        fixed_full_marginal = p720.evaluate_policy_budget(reports, metadata, fixed, 0.0, sample_limit)
        fixed_full_new = p720.evaluate_policy_budget(reports, metadata, fixed, factor_charge, sample_limit)

    summary = {
        "best_full_marginal_policy_budget": (p720.choose_best(full_marginal) or {}).get("policy_budget"),
        "best_full_marginal_total_over_rho": (p720.choose_best(full_marginal) or {}).get(
            "source_replay_total_with_fallback_over_rho"
        ),
        "best_full_new_bank_policy_budget": (p720.choose_best(full_new) or {}).get("policy_budget"),
        "best_full_new_bank_total_over_rho": (p720.choose_best(full_new) or {}).get(
            "source_replay_total_with_fallback_over_rho"
        ),
        "fixed_two_by_two_1p0_holdout_new_bank_below_rho_splits": below_count(
            split_reports,
            "fixed_two_by_two_1p0_holdout_new_bank",
        ),
        "fixed_two_by_two_1p0_new_bank_total_over_rho": (fixed_full_new or {}).get(
            "source_replay_total_with_fallback_over_rho"
        ),
        "heldout_oracle_best_new_bank_below_rho_splits": below_count(
            split_reports,
            "heldout_oracle_best_new_bank",
        ),
        "marginal_train_selected_new_bank_below_rho_splits": below_count(
            split_reports,
            "marginal_train_selected_holdout_new_bank",
        ),
        "new_bank_train_selected_new_bank_below_rho_splits": below_count(
            split_reports,
            "new_bank_train_selected_holdout_new_bank",
        ),
        "policy_budget_count": len(combos),
        "split_count": len(split_reports),
    }
    return {
        "full_population": {
            "best_full_marginal": p720.choose_best(full_marginal),
            "best_full_new_bank": p720.choose_best(full_new),
            "fixed_two_by_two_1p0_marginal_existing_bank": fixed_full_marginal,
            "fixed_two_by_two_1p0_new_bank": fixed_full_new,
            "top_full_marginal": sorted(full_marginal, key=p720.eval_sort_key)[:12],
            "top_full_new_bank": sorted(full_new, key=p720.eval_sort_key)[:12],
        },
        "groups": groups,
        "name": name,
        "split_reports": split_reports,
        "summary": summary,
    }


def adjacent_same_family_probe(args: argparse.Namespace) -> dict[str, Any]:
    adjacent_args = argparse.Namespace(
        max_transfer=int_value(args.adjacent_max_transfer),
        min_transfer=int_value(args.adjacent_min_transfer),
        p709=args.p709,
        source_pattern=args.source_pattern,
        target=args.target,
        thresholds=args.thresholds,
    )
    paths = p716.p712.source_paths(adjacent_args)
    return {
        "available": bool(paths),
        "max_transfer": int_value(args.adjacent_max_transfer),
        "min_transfer": int_value(args.adjacent_min_transfer),
        "path_count": len(paths),
        "sample_paths": [str(path) for path in paths[:8]],
        "source_pattern": args.source_pattern,
    }


def split_by_name(universe: dict[str, Any], split_name: str) -> dict[str, Any]:
    for report in universe.get("split_reports") or []:
        if report.get("split") == split_name:
            return report
    return {}


def determine_claim(universe_reports: list[dict[str, Any]]) -> str:
    expanded = next((row for row in universe_reports if row.get("name") == "expanded_public_rel2"), {})
    base = next((row for row in universe_reports if row.get("name") == "base_two_by_two"), {})
    expanded_summary = expanded.get("summary") or {}
    base_summary = base.get("summary") or {}
    split_count = int_value(expanded_summary.get("split_count"))
    expanded_train_new = int_value(expanded_summary.get("new_bank_train_selected_new_bank_below_rho_splits"))
    expanded_oracle_new = int_value(expanded_summary.get("heldout_oracle_best_new_bank_below_rho_splits"))
    base_train_new = int_value(base_summary.get("new_bank_train_selected_new_bank_below_rho_splits"))
    start0 = split_by_name(expanded, "rolling_train24_holdout16_start0")
    start0_oracle = start0.get("heldout_oracle_best_new_bank") or {}
    if split_count and expanded_train_new == split_count:
        return "P721_EXPANDED_PUBLIC_REL2_TRAIN_NEW_BANK_RESCUES_ALL_SPLITS"
    if split_count and expanded_oracle_new == split_count:
        return "P721_EXPANDED_PUBLIC_REL2_ORACLE_RESCUES_ALL_SPLITS_BUT_SELECTION_OPEN"
    if base_train_new > int_value(base_summary.get("marginal_train_selected_new_bank_below_rho_splits")):
        return "P721_NEW_BANK_SELECTION_RESCUES_SELECTOR_SENSITIVE_SPLIT_ONLY"
    if start0_oracle and not start0_oracle.get("beats_rho_with_fallback"):
        return "NEGATIVE_RESULT_P721_SAME_STREAM_EXPANDED_ORACLE_START0_ABOVE_RHO"
    return "P721_PARTIAL_NEW_BANK_RESCUE_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p720_payload = load_json(Path(args.p720))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    thresholds = p720.parse_floats(args.thresholds)
    budgets = p720.parse_ints(args.attempt_budgets)
    build_args = argparse.Namespace(
        max_transfer=int_value(args.max_transfer),
        min_transfer=int_value(args.min_transfer),
        p709=args.p709,
        source_pattern=args.source_pattern,
        target=args.target,
        thresholds=args.thresholds,
    )
    reports, metadata = p716.build_window_reports(build_args)
    metadata["shared_replay_cache"] = {}
    metadata["shared_replay_errors"] = {}
    splits = p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )
    universes = [
        ("base_two_by_two", parse_groups(args.base_groups)),
        ("expanded_public_rel2", parse_groups(args.expanded_groups)),
    ]
    universe_reports = [
        evaluate_universe(
            name,
            groups,
            reports,
            splits,
            metadata,
            thresholds,
            budgets,
            factor_charge,
            int_value(args.sample_limit),
        )
        for name, groups in universes
    ]
    unique_mismatch_count = sum(
        1 for replay in metadata["shared_replay_cache"].values() if not replay.get("union_matches_all_fields")
    )
    adjacent = adjacent_same_family_probe(args)
    payload = {
        "adjacent_same_family_probe": adjacent,
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p720": str(Path(args.p720)),
        },
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "REPLAY-BACKED: every charged candidate uses the P719 shared-core replay path.",
            "SAME-STREAM EXPANSION: expanded policies use the same P231 selector-expanded windows, not a new source family.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p721_shared_core_new_bank_rescue_audit",
        "parameters": {
            "attempt_budgets": budgets,
            "base_groups": parse_groups(args.base_groups),
            "expanded_groups": parse_groups(args.expanded_groups),
            "factor_bank_charge_over_rho": factor_charge,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "source_pattern": args.source_pattern,
            "target": args.target,
            "thresholds": thresholds,
        },
        "p720_reference": {
            "claim_status": p720_payload.get("claim_status"),
            "summary": p720_payload.get("summary"),
        },
        "replay_metadata": {
            "candidate_count": sum(len(report["candidates"]) for report in reports),
            "candidate_window_count": sum(1 for report in reports if report["candidates"]),
            "group_candidate_counts": metadata.get("group_candidate_counts"),
            "shared_replay_cache_count": len(metadata["shared_replay_cache"]),
            "shared_replay_error_count": len(metadata["shared_replay_errors"]),
            "shared_replay_errors": metadata["shared_replay_errors"],
            "source_window_count": len(reports),
            "unique_mismatch_count": unique_mismatch_count,
        },
        "schema": "ecdlp.low_term_total2_p721_shared_core_new_bank_rescue_audit.v1",
        "universe_reports": universe_reports,
    }
    payload["claim_status"] = determine_claim(universe_reports)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjacent-max-transfer", type=int, default=20831)
    parser.add_argument("--adjacent-min-transfer", type=int, default=20808)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-groups", default="two_by_two_any")
    parser.add_argument(
        "--expanded-groups",
        default="baseline_total1,low_term_any,low_term_excluding_total1,cost_low_term_any,two_by_two_any,all_excluding_total1,all_rel2",
    )
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p720", default=str(DEFAULT_P720))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--source-pattern", default=p716.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.544,0.568,0.616,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "adjacent_same_family_probe": payload["adjacent_same_family_probe"],
                "claim_status": payload["claim_status"],
                "replay_metadata": payload["replay_metadata"],
                "universe_summaries": {
                    universe["name"]: universe["summary"]
                    for universe in payload["universe_reports"]
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(
        json.dumps(
            {
                "split_compact": {
                    universe["name"]: [
                        compact_split(report)
                        for report in universe["split_reports"]
                    ]
                    for universe in payload["universe_reports"]
                }
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
