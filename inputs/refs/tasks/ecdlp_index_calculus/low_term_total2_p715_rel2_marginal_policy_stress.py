#!/usr/bin/env python3
"""P715 train-selected rel2 marginal policy and attempt-budget stress test."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p714_rel2_marginal_window_precheck as p714


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p715_rel2_marginal_policy_stress_probe.json"


@dataclass(frozen=True)
class PolicyBudget:
    policy: p714.WindowPolicy
    budget: int

    @property
    def name(self) -> str:
        return f"{self.policy.name}:budget{self.budget}"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p714.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p714.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one attempt budget is required")
    return tuple(sorted(set(values)))


def eval_sort_key(report: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(report.get("beats_rho_with_fallback")),
        float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
        -int_value(report.get("hit_count")),
        int_value(report.get("attempted_candidate_count")),
        int_value(report.get("attempt_budget")),
        str(report.get("policy_budget")),
    )


def evaluate_policy_budget(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    combo: PolicyBudget,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    report = p714.evaluate_window_policy(
        reports,
        replay_cache,
        combo.policy,
        factor_charge,
        combo.budget,
        sample_limit,
    )
    report["policy_budget"] = combo.name
    return report


def evaluate_all(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    combos: list[PolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> list[dict[str, Any]]:
    return [
        evaluate_policy_budget(reports, replay_cache, combo, factor_charge, sample_limit)
        for combo in combos
    ]


def choose_best(reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not reports:
        return {}
    return sorted(reports, key=eval_sort_key)[0]


def combo_by_name(combos: list[PolicyBudget], name: str) -> PolicyBudget:
    for combo in combos:
        if combo.name == name:
            return combo
    raise KeyError(name)


def make_policy_budgets(thresholds: tuple[float, ...], budgets: tuple[int, ...]) -> list[PolicyBudget]:
    policies = p714.make_window_policies(thresholds)
    return [PolicyBudget(policy, budget) for policy in policies for budget in budgets]


def fixed_combo_reports(
    holdout_reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    combos: list[PolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, dict[str, Any]]:
    wanted = (
        "cost_le_0p544:budget1",
        "cost_le_0p55:budget1",
        "strict_rel2:budget1",
        "window_rel2_count_le2_cost_le_0p568:budget1",
    )
    rows: dict[str, dict[str, Any]] = {}
    for name in wanted:
        try:
            combo = combo_by_name(combos, name)
        except KeyError:
            continue
        rows[name] = {
            "marginal_existing_bank": evaluate_policy_budget(
                holdout_reports,
                replay_cache,
                combo,
                0.0,
                sample_limit,
            ),
            "new_bank": evaluate_policy_budget(
                holdout_reports,
                replay_cache,
                combo,
                factor_charge,
                sample_limit,
            ),
        }
    return rows


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    combos: list[PolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train_reports = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout_reports = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_marginal = evaluate_all(train_reports, replay_cache, combos, 0.0, sample_limit)
    selected_train = choose_best(train_marginal)
    selected_combo = combo_by_name(combos, str(selected_train.get("policy_budget")))
    selected_holdout_marginal = evaluate_policy_budget(
        holdout_reports,
        replay_cache,
        selected_combo,
        0.0,
        sample_limit,
    )
    selected_holdout_new = evaluate_policy_budget(
        holdout_reports,
        replay_cache,
        selected_combo,
        factor_charge,
        sample_limit,
    )
    holdout_marginal_oracle = choose_best(evaluate_all(holdout_reports, replay_cache, combos, 0.0, sample_limit))
    holdout_new_oracle = choose_best(evaluate_all(holdout_reports, replay_cache, combos, factor_charge, sample_limit))
    return {
        **split,
        "candidate_policy_budget_count": len(combos),
        "fixed_controls": fixed_combo_reports(holdout_reports, replay_cache, combos, factor_charge, sample_limit),
        "heldout_oracle_best_marginal_existing_bank": holdout_marginal_oracle,
        "heldout_oracle_best_new_bank": holdout_new_oracle,
        "selected_holdout_marginal_existing_bank": selected_holdout_marginal,
        "selected_holdout_new_bank": selected_holdout_new,
        "selected_policy_budget": selected_combo.name,
        "selected_train_marginal_existing_bank": selected_train,
        "top_train_marginal_existing_bank": sorted(train_marginal, key=eval_sort_key)[:8],
        "train_window_count": len(train_reports),
        "window_ranges": {
            "holdout": [[report["window_start"], report["window_end"]] for report in holdout_reports[:3]],
            "holdout_last": None if not holdout_reports else [holdout_reports[-1]["window_start"], holdout_reports[-1]["window_end"]],
            "train": [[report["window_start"], report["window_end"]] for report in train_reports[:3]],
            "train_last": None if not train_reports else [train_reports[-1]["window_start"], train_reports[-1]["window_end"]],
        },
    }


def best_by_budget(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    budgets = sorted({int_value(report.get("attempt_budget")) for report in reports})
    rows = []
    for budget in budgets:
        subset = [report for report in reports if int_value(report.get("attempt_budget")) == budget]
        if subset:
            rows.append(choose_best(subset))
    return rows


def summarize_splits(split_reports: list[dict[str, Any]]) -> dict[str, Any]:
    selected_marginal = [
        report["selected_holdout_marginal_existing_bank"]
        for report in split_reports
    ]
    selected_new = [
        report["selected_holdout_new_bank"]
        for report in split_reports
    ]
    oracle_marginal = [
        report["heldout_oracle_best_marginal_existing_bank"]
        for report in split_reports
    ]
    oracle_new = [
        report["heldout_oracle_best_new_bank"]
        for report in split_reports
    ]
    selected_gt1 = sum(1 for report in split_reports if int_value(report["selected_holdout_marginal_existing_bank"].get("attempt_budget")) > 1)
    return {
        "heldout_oracle_marginal_existing_bank_below_rho_splits": sum(
            1 for report in oracle_marginal if report.get("beats_rho_with_fallback")
        ),
        "heldout_oracle_new_bank_below_rho_splits": sum(
            1 for report in oracle_new if report.get("beats_rho_with_fallback")
        ),
        "selected_attempt_budget_gt1_splits": selected_gt1,
        "selected_holdout_marginal_existing_bank_below_rho_splits": sum(
            1 for report in selected_marginal if report.get("beats_rho_with_fallback")
        ),
        "selected_holdout_new_bank_below_rho_splits": sum(
            1 for report in selected_new if report.get("beats_rho_with_fallback")
        ),
        "split_count": len(split_reports),
    }


def determine_claim(summary: dict[str, Any], full_population: dict[str, Any]) -> str:
    split_count = int_value(summary.get("split_count"))
    selected_marginal = int_value(summary.get("selected_holdout_marginal_existing_bank_below_rho_splits"))
    selected_new = int_value(summary.get("selected_holdout_new_bank_below_rho_splits"))
    best_new = full_population.get("best_new_bank") or {}
    best_marginal_by_budget = full_population.get("best_marginal_existing_bank_by_budget") or []
    budget1_hits = 0
    budget_gt1_hits = 0
    for report in best_marginal_by_budget:
        if int_value(report.get("attempt_budget")) == 1:
            budget1_hits = int_value(report.get("hit_count"))
        elif int_value(report.get("attempt_budget")) > 1:
            budget_gt1_hits = max(budget_gt1_hits, int_value(report.get("hit_count")))
    if split_count and selected_marginal == split_count:
        return "P715_TRAIN_SELECTED_REL2_MARGINAL_POLICY_BEATS_ALL_HELDOUT_SPLITS"
    if selected_new:
        return "P715_TRAIN_SELECTED_REL2_POLICY_HAS_NEW_BANK_HELDOUT_SIGNAL"
    if best_new.get("beats_rho_with_fallback") and int_value(best_new.get("attempt_budget")) > 1:
        return "P715_HIGHER_REL2_ATTEMPT_BUDGET_IMPROVES_FULL_POPULATION_NEW_BANK"
    if selected_marginal or budget_gt1_hits > budget1_hits:
        return "P715_PARTIAL_MARGINAL_SIGNAL_BUT_HELDOUT_POLICY_STILL_UNSTABLE"
    return "NEGATIVE_RESULT_P715_REL2_FILTERING_AND_BUDGET_EXPANSION_DO_NOT_STABILIZE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    args.factor_charge = factor_charge
    thresholds = p714.parse_thresholds(args.thresholds)
    budgets = parse_ints(args.attempt_budgets)
    reports, metadata = p713.build_window_reports(args)
    combos = make_policy_budgets(thresholds, budgets)
    splits = p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )
    split_reports = [
        evaluate_split(split, reports, metadata["replay_cache"], combos, factor_charge, int_value(args.sample_limit))
        for split in splits
    ]
    full_marginal = evaluate_all(reports, metadata["replay_cache"], combos, 0.0, int_value(args.sample_limit))
    full_new = evaluate_all(reports, metadata["replay_cache"], combos, factor_charge, int_value(args.sample_limit))
    full_population = {
        "best_marginal_existing_bank": choose_best(full_marginal),
        "best_marginal_existing_bank_by_budget": best_by_budget(full_marginal),
        "best_new_bank": choose_best(full_new),
        "best_new_bank_by_budget": best_by_budget(full_new),
        "top_marginal_existing_bank": sorted(full_marginal, key=eval_sort_key)[:10],
        "top_new_bank": sorted(full_new, key=eval_sort_key)[:10],
    }
    split_summary = summarize_splits(split_reports)
    rel2_candidate_count = sum(len(report.get("rel2_candidates") or []) for report in reports)
    rel2_candidate_window_count = sum(1 for report in reports if report.get("rel2_candidates"))
    payload = {
        "artifacts": {"p709": str(Path(args.p709)), "p713": str(p713.DEFAULT_OUT), "p714": str(p714.DEFAULT_OUT)},
        "created_at": now_iso(),
        "full_population": full_population,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source artifacts outside the P709 source map, not live fresh harvesting.",
            "NO LABEL-ONLY HELDOUT CLAIM: selected policies are chosen on training windows before heldout scoring.",
            "MARGINAL ACCOUNTING: existing-bank mode assumes reusable factor-bank work has already been paid by a many-target workflow.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p715_rel2_marginal_policy_stress",
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "source_pattern": args.source_pattern,
            "target": args.target,
            "thresholds": thresholds,
        },
        "replay_metadata": {
            "policy_budget_count": len(combos),
            "rel2_candidate_count": rel2_candidate_count,
            "rel2_candidate_window_count": rel2_candidate_window_count,
            "replay_cache_count": len(metadata["replay_cache"]),
            "replay_error_count": metadata["replay_error_count"],
            "replay_errors": metadata["replay_errors"],
            "source_window_count": len(reports),
        },
        "schema": "ecdlp.low_term_total2_p715_rel2_marginal_policy_stress.v1",
        "split_reports": split_reports,
        "summary": {
            **split_summary,
            "best_full_marginal_attempt_budget": (full_population["best_marginal_existing_bank"] or {}).get("attempt_budget"),
            "best_full_marginal_policy_budget": (full_population["best_marginal_existing_bank"] or {}).get("policy_budget"),
            "best_full_marginal_total_over_rho": (full_population["best_marginal_existing_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "best_full_new_bank_attempt_budget": (full_population["best_new_bank"] or {}).get("attempt_budget"),
            "best_full_new_bank_policy_budget": (full_population["best_new_bank"] or {}).get("policy_budget"),
            "best_full_new_bank_total_over_rho": (full_population["best_new_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
        },
    }
    payload["claim_status"] = determine_claim(payload["summary"], full_population)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2,4")
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--source-pattern", default=p713.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.52,0.544,0.55,0.568,0.616")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"split_reports": payload["split_reports"]}, indent=2, sort_keys=True))
    print(json.dumps({"full_population": payload["full_population"]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
