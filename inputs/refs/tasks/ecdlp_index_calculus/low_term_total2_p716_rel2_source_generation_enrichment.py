#!/usr/bin/env python3
"""P716 bounded rel2 source-generation enrichment audit."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p711_rel2_source_neighborhood_replay as p711
import low_term_total2_p712_rel2_fresh_window_validation as p712
import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p716_rel2_source_generation_enrichment_probe.json"
TRUE_ENRICHED_GROUPS = {
    "all_excluding_total1",
    "cost_low_term_any",
    "low_term_excluding_total1",
    "two_by_two_any",
}


@dataclass(frozen=True)
class SourcePolicy:
    name: str
    group: str
    threshold: float | None = None


@dataclass(frozen=True)
class PolicyBudget:
    policy: SourcePolicy
    budget: int

    @property
    def name(self) -> str:
        return f"{self.policy.name}:budget{self.budget}"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p711.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p711.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_floats(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def parse_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one attempt budget is required")
    return tuple(sorted(set(values)))


def threshold_token(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def selector_mode(selector: Any) -> str:
    return p711.selector_mode(str(selector or ""))


def is_total1(row: dict[str, Any]) -> bool:
    return (
        selector_mode(row.get("selector")) == "mode_low_term_support_total1"
        and int_value(row.get("selected_leaf_count")) == 1
        and int_value(row.get("selected_row_count")) == 1
    )


def source_case_key(source_path: Path, row: dict[str, Any]) -> str:
    return p711.source_case_key(source_path, row)


def row_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        float_value(row.get("direct_ops_over_rho"), 999999.0),
        selector_priority(row),
        int_value((row.get("source_case") or {}).get("source_row_index")),
        str(row.get("row_pair")),
        tuple(str(part) for part in (row.get("source_case") or {}).get("row_keys") or []),
    )


def selector_priority(row: dict[str, Any]) -> int:
    selector = selector_mode(row.get("selector"))
    if selector == "mode_low_term_support_total1":
        return 0
    if selector.startswith("mode_low_term_support_total"):
        return 1
    if selector.startswith("mode_cost_low_term_support_total"):
        return 2
    if selector.startswith("mode_double_pair_first"):
        return 3
    return 4


def candidate_rows(source: dict[str, Any], source_path: Path, target: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for policy_name, policy in (source.get("policies") or {}).items():
        if not isinstance(policy, dict):
            continue
        row_selector = (policy.get("row_selector") or {}).get("selector")
        for row_index, row in enumerate(policy.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            if str(row.get("target")) != target:
                continue
            if int_value(row.get("relation_count")) != 2:
                continue
            source_case = {
                **row,
                "source_policy": policy_name,
                "source_row_index": row_index,
                "row_selector": row.get("row_selector") or row_selector,
            }
            key = source_case_key(source_path, source_case)
            if key in seen:
                continue
            seen.add(key)
            item = {
                "direct_ops_over_rho": float_value(row.get("ops_over_rho"), 999999.0),
                "key": key,
                "relation_count": 2,
                "row_pair": p711.row_pair(row.get("row_keys") or []),
                "selected_leaf_count": int_value(row.get("selected_leaf_count")),
                "selected_row_count": int_value(row.get("selected_row_count")),
                "selector": selector_mode(row.get("selector")),
                "source": str(source_path),
                "source_case": source_case,
                "source_public_key_verified_label": bool(row.get("public_key_verified")),
                "source_verified_label": bool(row.get("source_verified")),
            }
            rows.append(item)
    rows.sort(key=row_sort_key)
    return rows


def policy_accepts(policy: SourcePolicy, row: dict[str, Any]) -> bool:
    if policy.threshold is not None and float_value(row.get("direct_ops_over_rho"), 999999.0) > policy.threshold:
        return False
    selector = selector_mode(row.get("selector"))
    leaf_count = int_value(row.get("selected_leaf_count"))
    row_count = int_value(row.get("selected_row_count"))
    group = policy.group
    if group == "baseline_total1":
        return is_total1(row)
    if group == "low_term_any":
        return selector.startswith("mode_low_term_support_total")
    if group == "low_term_excluding_total1":
        return selector.startswith("mode_low_term_support_total") and not is_total1(row)
    if group == "cost_low_term_any":
        return selector.startswith("mode_cost_low_term_support_total")
    if group == "two_by_two_any":
        return leaf_count == 2 and row_count == 2
    if group == "all_excluding_total1":
        return not is_total1(row)
    if group == "all_rel2":
        return True
    raise ValueError(f"unknown policy group {group}")


def make_policies(thresholds: tuple[float, ...]) -> list[SourcePolicy]:
    groups = [
        ("baseline_total1", "baseline_total1"),
        ("low_term_any", "low_term_any"),
        ("low_term_excluding_total1", "low_term_excluding_total1"),
        ("cost_low_term_any", "cost_low_term_any"),
        ("two_by_two_any", "two_by_two_any"),
        ("all_excluding_total1", "all_excluding_total1"),
        ("all_rel2", "all_rel2"),
    ]
    policies: list[SourcePolicy] = []
    for name, group in groups:
        policies.append(SourcePolicy(name, group))
        for threshold in thresholds:
            policies.append(SourcePolicy(f"{name}_cost_le_{threshold_token(threshold)}", group, threshold))
    return policies


def make_policy_budgets(thresholds: tuple[float, ...], budgets: tuple[int, ...]) -> list[PolicyBudget]:
    return [PolicyBudget(policy, budget) for policy in make_policies(thresholds) for budget in budgets]


def build_window_reports(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    source_cache: dict[str, dict[str, Any]] = {}
    selector_counts: dict[str, int] = {}
    group_candidate_counts: dict[str, int] = {}
    for source_path in p712.source_paths(args):
        source = load_json(source_path)
        source_cache[str(source_path)] = source
        parsed = p712.window_range(source_path)
        if parsed is None:
            continue
        rows = candidate_rows(source, source_path, args.target)
        for row in rows:
            selector = selector_mode(row.get("selector"))
            selector_counts[selector] = selector_counts.get(selector, 0) + 1
        reports.append(
            {
                "candidates": rows,
                "source": str(source_path),
                "window_end": parsed[1],
                "window_start": parsed[0],
            }
        )
    reports.sort(key=lambda report: (int_value(report["window_start"]), int_value(report["window_end"]), report["source"]))
    for policy in make_policies(parse_floats(args.thresholds)):
        keys = {
            str(row["key"])
            for report in reports
            for row in report["candidates"]
            if policy_accepts(policy, row)
        }
        group_candidate_counts[policy.name] = len(keys)
    return reports, {
        "group_candidate_counts": group_candidate_counts,
        "replay_cache": {},
        "replay_error_count": 0,
        "replay_errors": {},
        "selector_counts": selector_counts,
        "source_cache": source_cache,
    }


def replay_row(row: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any] | None:
    key = str(row["key"])
    replay_cache = metadata["replay_cache"]
    replay_errors = metadata["replay_errors"]
    if key in replay_cache:
        return replay_cache[key]
    if key in replay_errors:
        return None
    source_path = Path(str(row["source"]))
    source = metadata["source_cache"][str(source_path)]
    try:
        replay = p711.replay_candidate(source, source_path, row)
    except Exception as exc:  # noqa: BLE001 - verifier failures are experiment evidence.
        replay_errors[key] = f"{type(exc).__name__}: {exc}"
        metadata["replay_error_count"] = len(replay_errors)
        return None
    replay_cache[key] = replay
    return replay


def sample_row(row: dict[str, Any], replay: dict[str, Any] | None = None) -> dict[str, Any]:
    source_case = row.get("source_case") or {}
    sample = {
        "direct_ops_over_rho": float_value(row.get("direct_ops_over_rho")),
        "row_keys": source_case.get("row_keys") or [],
        "row_pair": row.get("row_pair"),
        "selected_leaf_count": row.get("selected_leaf_count"),
        "selected_row_count": row.get("selected_row_count"),
        "selector": row.get("selector"),
        "source_policy": source_case.get("source_policy"),
        "source_row_index": int_value(source_case.get("source_row_index")),
        "top_k": int_value(source_case.get("top_k")),
        "transfer_index": int_value(source_case.get("transfer_index")),
    }
    if replay is not None:
        sample["replay"] = p711.sample_replay(replay)
    return sample


def evaluate_policy_budget(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combo: PolicyBudget,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    precheck_window_count = 0
    accepted_candidate_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    for report in reports:
        accepted = [
            row
            for row in report["candidates"]
            if policy_accepts(combo.policy, row)
        ]
        accepted.sort(key=row_sort_key)
        accepted_candidate_count += len(accepted)
        if accepted:
            precheck_window_count += 1
        hit = None
        charge = 0.0
        attempted = 0
        for row in accepted[: combo.budget]:
            attempted += 1
            replay = replay_row(row, metadata)
            charge += float_value(
                None if replay is None else replay.get("direct_ops_over_rho"),
                float_value(row.get("direct_ops_over_rho")),
            )
            if replay and replay.get("replay_public_key_verified"):
                hit = (row, replay)
                break
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(hit_samples) < sample_limit:
                hit_samples.append(
                    {
                        "row": sample_row(hit[0], hit[1]),
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
        else:
            fallback_charge += 1.0
            if len(miss_samples) < sample_limit:
                miss_samples.append(
                    {
                        "accepted_candidate_count": len(accepted),
                        "first_candidates": [sample_row(row) for row in accepted[: min(3, len(accepted))]],
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
    window_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "accepted_candidate_count": accepted_candidate_count,
        "attempt_budget": combo.budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "factor_charge_over_rho": round(factor_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "miss_samples": miss_samples,
        "policy": combo.policy.name,
        "policy_budget": combo.name,
        "policy_group": combo.policy.group,
        "policy_threshold": combo.policy.threshold,
        "precheck_window_count": precheck_window_count,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_per_window_over_rho": round(total / window_count, 8) if window_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": window_count,
        "window_count": window_count,
    }


def eval_sort_key(report: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(report.get("beats_rho_with_fallback")),
        float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
        -int_value(report.get("hit_count")),
        int_value(report.get("attempted_candidate_count")),
        str(report.get("policy_budget")),
    )


def choose_best(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(reports, key=eval_sort_key)[0] if reports else {}


def compact_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_budget": report.get("attempt_budget"),
        "attempted_candidate_count": report.get("attempted_candidate_count"),
        "attempted_source_charge_over_rho": report.get("attempted_source_charge_over_rho"),
        "beats_rho_with_fallback": report.get("beats_rho_with_fallback"),
        "fallback_charge_over_rho": report.get("fallback_charge_over_rho"),
        "hit_count": report.get("hit_count"),
        "policy_budget": report.get("policy_budget"),
        "policy_group": report.get("policy_group"),
        "policy_threshold": report.get("policy_threshold"),
        "precheck_window_count": report.get("precheck_window_count"),
        "source_replay_total_with_fallback_over_rho": report.get("source_replay_total_with_fallback_over_rho"),
        "vs_independent_rho_with_fallback_over_rho": report.get("vs_independent_rho_with_fallback_over_rho"),
    }


def combo_by_name(combos: list[PolicyBudget], name: str) -> PolicyBudget:
    for combo in combos:
        if combo.name == name:
            return combo
    raise KeyError(name)


def evaluate_all(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[PolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> list[dict[str, Any]]:
    return [
        evaluate_policy_budget(reports, metadata, combo, factor_charge, sample_limit)
        for combo in combos
    ]


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[PolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_marginal = evaluate_all(train, metadata, combos, 0.0, sample_limit)
    selected_train = choose_best(train_marginal)
    selected_combo = combo_by_name(combos, str(selected_train.get("policy_budget")))
    selected_holdout_marginal = evaluate_policy_budget(holdout, metadata, selected_combo, 0.0, sample_limit)
    selected_holdout_new = evaluate_policy_budget(holdout, metadata, selected_combo, factor_charge, sample_limit)
    oracle_marginal = choose_best(evaluate_all(holdout, metadata, combos, 0.0, sample_limit))
    oracle_new = choose_best(evaluate_all(holdout, metadata, combos, factor_charge, sample_limit))
    return {
        **split,
        "heldout_oracle_best_marginal_existing_bank": oracle_marginal,
        "heldout_oracle_best_new_bank": oracle_new,
        "selected_holdout_marginal_existing_bank": selected_holdout_marginal,
        "selected_holdout_new_bank": selected_holdout_new,
        "selected_policy_budget": selected_combo.name,
        "selected_train_marginal_existing_bank": selected_train,
        "top_train_marginal_existing_bank": sorted(train_marginal, key=eval_sort_key)[:8],
        "train_window_count": len(train),
        "window_ranges": {
            "holdout": [[report["window_start"], report["window_end"]] for report in holdout[:3]],
            "holdout_last": None if not holdout else [holdout[-1]["window_start"], holdout[-1]["window_end"]],
            "train": [[report["window_start"], report["window_end"]] for report in train[:3]],
            "train_last": None if not train else [train[-1]["window_start"], train[-1]["window_end"]],
        },
    }


def summarize_splits(split_reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "heldout_oracle_marginal_existing_bank_below_rho_splits": sum(
            1 for report in split_reports if report["heldout_oracle_best_marginal_existing_bank"].get("beats_rho_with_fallback")
        ),
        "heldout_oracle_new_bank_below_rho_splits": sum(
            1 for report in split_reports if report["heldout_oracle_best_new_bank"].get("beats_rho_with_fallback")
        ),
        "selected_holdout_marginal_existing_bank_below_rho_splits": sum(
            1 for report in split_reports if report["selected_holdout_marginal_existing_bank"].get("beats_rho_with_fallback")
        ),
        "selected_holdout_new_bank_below_rho_splits": sum(
            1 for report in split_reports if report["selected_holdout_new_bank"].get("beats_rho_with_fallback")
        ),
        "split_count": len(split_reports),
    }


def best_enriched(reports: list[dict[str, Any]]) -> dict[str, Any]:
    enriched = [
        report
        for report in reports
        if report.get("policy_group") in TRUE_ENRICHED_GROUPS
        and int_value(report.get("attempted_candidate_count")) > 0
    ]
    return choose_best(enriched)


def determine_claim(summary: dict[str, Any], full_population: dict[str, Any]) -> str:
    split_count = int_value(summary.get("split_count"))
    selected_marginal = int_value(summary.get("selected_holdout_marginal_existing_bank_below_rho_splits"))
    selected_new = int_value(summary.get("selected_holdout_new_bank_below_rho_splits"))
    best_baseline = full_population.get("best_baseline_marginal_existing_bank") or {}
    best_enriched_marginal = full_population.get("best_enriched_marginal_existing_bank") or {}
    best_enriched_new = full_population.get("best_enriched_new_bank") or {}
    if split_count and selected_marginal == split_count:
        return "P716_ENRICHED_REL2_GENERATOR_SELECTED_POLICY_BEATS_ALL_MARGINAL_HELDOUT_SPLITS"
    if selected_new:
        return "P716_ENRICHED_REL2_GENERATOR_HAS_NEW_BANK_HELDOUT_SIGNAL"
    if (
        int_value(best_enriched_marginal.get("hit_count")) > int_value(best_baseline.get("hit_count"))
        and float_value(best_enriched_marginal.get("source_replay_total_with_fallback_over_rho"), 999999.0)
        <= float_value(best_baseline.get("source_replay_total_with_fallback_over_rho"), 999999.0)
    ):
        return "P716_ENRICHMENT_IMPROVES_FULL_POPULATION_MARGINAL_COST"
    if int_value(best_enriched_marginal.get("hit_count")) > int_value(best_baseline.get("hit_count")):
        return "P716_ENRICHMENT_FINDS_EXTRA_HITS_BUT_SOURCE_COST_DOMINATES"
    if best_enriched_new.get("beats_rho_with_fallback"):
        return "P716_ENRICHED_POLICY_BEATS_FULL_POPULATION_NEW_BANK_BUT_NOT_HELDOUT"
    return "NEGATIVE_RESULT_P716_ENRICHED_REPLAY_DOES_NOT_IMPROVE_REL2_PATH"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    thresholds = parse_floats(args.thresholds)
    budgets = parse_ints(args.attempt_budgets)
    reports, metadata = build_window_reports(args)
    combos = make_policy_budgets(thresholds, budgets)
    splits = p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )
    full_marginal = evaluate_all(reports, metadata, combos, 0.0, int_value(args.sample_limit))
    full_new = evaluate_all(reports, metadata, combos, factor_charge, int_value(args.sample_limit))
    baseline_marginal = [
        report for report in full_marginal if report.get("policy_group") == "baseline_total1"
    ]
    baseline_new = [
        report for report in full_new if report.get("policy_group") == "baseline_total1"
    ]
    split_reports = [
        evaluate_split(split, reports, metadata, combos, factor_charge, int_value(args.sample_limit))
        for split in splits
    ]
    split_summary = summarize_splits(split_reports)
    full_population = {
        "best_baseline_marginal_existing_bank": choose_best(baseline_marginal),
        "best_baseline_new_bank": choose_best(baseline_new),
        "best_enriched_marginal_existing_bank": best_enriched(full_marginal),
        "best_enriched_new_bank": best_enriched(full_new),
        "best_marginal_existing_bank": choose_best(full_marginal),
        "best_new_bank": choose_best(full_new),
        "top_marginal_existing_bank": sorted(full_marginal, key=eval_sort_key)[:12],
        "top_new_bank": sorted(full_new, key=eval_sort_key)[:12],
    }
    candidate_count = sum(len(report["candidates"]) for report in reports)
    candidate_window_count = sum(1 for report in reports if report["candidates"])
    replay_errors = metadata["replay_errors"]
    replay_cache = metadata["replay_cache"]
    payload = {
        "artifacts": {"p709": str(Path(args.p709)), "p715": str(STATE_DIR / "low_term_total2_p715_rel2_marginal_policy_stress_probe.json")},
        "created_at": now_iso(),
        "full_population": full_population,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "NO LABEL-ONLY HELDOUT CLAIM: selected policies are chosen on training windows before heldout scoring.",
            "MARGINAL ACCOUNTING: existing-bank mode assumes reusable factor-bank work has already been paid by a many-target workflow.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p716_rel2_source_generation_enrichment",
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
            "candidate_count": candidate_count,
            "candidate_window_count": candidate_window_count,
            "group_candidate_counts": metadata["group_candidate_counts"],
            "policy_budget_count": len(combos),
            "replay_cache_count": len(replay_cache),
            "replay_error_count": len(replay_errors),
            "replay_errors": replay_errors,
            "selector_counts": metadata["selector_counts"],
            "source_window_count": len(reports),
        },
        "schema": "ecdlp.low_term_total2_p716_rel2_source_generation_enrichment.v1",
        "split_reports": split_reports,
        "summary": {
            **split_summary,
            "best_baseline_marginal_policy_budget": (full_population["best_baseline_marginal_existing_bank"] or {}).get("policy_budget"),
            "best_baseline_marginal_total_over_rho": (full_population["best_baseline_marginal_existing_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "best_enriched_marginal_hit_count": (full_population["best_enriched_marginal_existing_bank"] or {}).get("hit_count"),
            "best_enriched_marginal_policy_budget": (full_population["best_enriched_marginal_existing_bank"] or {}).get("policy_budget"),
            "best_enriched_marginal_total_over_rho": (full_population["best_enriched_marginal_existing_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "best_full_marginal_policy_budget": (full_population["best_marginal_existing_bank"] or {}).get("policy_budget"),
            "best_full_marginal_total_over_rho": (full_population["best_marginal_existing_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
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
    parser.add_argument("--source-pattern", default=p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.544,0.568,0.616,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"top_marginal": [compact_report(report) for report in payload["full_population"]["top_marginal_existing_bank"][:10]]}, indent=2, sort_keys=True))
    print(json.dumps({"split_compact": [
        {
            "split": report["split"],
            "selected_policy_budget": report["selected_policy_budget"],
            "selected_holdout_marginal": compact_report(report["selected_holdout_marginal_existing_bank"]),
            "selected_holdout_new": compact_report(report["selected_holdout_new_bank"]),
            "oracle_marginal": compact_report(report["heldout_oracle_best_marginal_existing_bank"]),
        }
        for report in payload["split_reports"]
    ]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": {
        "candidate_count": payload["replay_metadata"]["candidate_count"],
        "candidate_window_count": payload["replay_metadata"]["candidate_window_count"],
        "policy_budget_count": payload["replay_metadata"]["policy_budget_count"],
        "replay_cache_count": payload["replay_metadata"]["replay_cache_count"],
        "replay_error_count": payload["replay_metadata"]["replay_error_count"],
        "source_window_count": payload["replay_metadata"]["source_window_count"],
    }}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
