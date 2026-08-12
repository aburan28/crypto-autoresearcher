#!/usr/bin/env python3
"""P730 public per-window regime selector for P729 top-k oracle gap."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p720_shared_core_temporal_generalization_audit as p720
import low_term_total2_p729_selector_gap_rank_gated_transfer as p729


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p730_public_window_regime_selector_probe.json"
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
P729_REFERENCE = STATE_DIR / "low_term_total2_p729_selector_gap_rank_gated_transfer_probe.json"
BASE_PATTERN = p729.BASE_PATTERN
FRESH_PATTERN = p729.FRESH_PATTERN
FOCUS_SPLIT = "rolling_train24_holdout16_start16"

FIXED = "two_by_two_any_cost_le_1p0:budget1"
SHAPE_0928 = "all_rel2_cost_le_0p928_leaf2_row2:budget1"
TOPK7_1P0 = "all_rel2_cost_le_1p0_topk_le_7:budget1"
TOPK7_0928 = "all_rel2_cost_le_0p928_topk_le_7:budget1"
TOPK16_0928 = "all_rel2_cost_le_0p928_topk_le_16:budget1"
ALL_REL2_0568 = "all_rel2_cost_le_0p568:budget1"
REGIME_POLICY_BUDGETS = (
    FIXED,
    SHAPE_0928,
    TOPK7_1P0,
    TOPK7_0928,
    TOPK16_0928,
    ALL_REL2_0568,
)


@dataclass(frozen=True)
class WindowFeatures:
    all_count: int
    fixed_count: int
    fixed_min_cost: float | None
    fresh_count: int
    shape_count: int
    shape_min_cost: float | None
    topk7_count: int
    topk7_fresh_count: int
    topk7_min_cost: float | None
    topk16_count: int
    window_end: int
    window_start: int


@dataclass(frozen=True)
class RegimeRule:
    name: str
    description: str
    chooser: Callable[[WindowFeatures], str]


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


def parse_floats(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def parse_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one attempt budget is required")
    return tuple(sorted(set(values)))


def split_reports(reports: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    return p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )


def gate_accepts(gate: p729.PublicGate, report: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in report.get("candidates") or [] if p729.gate_accepts(gate, row)]
    return sorted(rows, key=p729.gate_sort_key)


def min_cost(rows: list[dict[str, Any]]) -> float | None:
    if not rows:
        return None
    return min(float_value(row.get("direct_ops_over_rho"), 999999.0) for row in rows)


def fresh_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row.get("p722_origin") == "fresh")


def window_features(report: dict[str, Any], gates: dict[str, p729.PublicGate]) -> WindowFeatures:
    all_rows = report.get("candidates") or []
    fixed_rows = gate_accepts(gates[FIXED], report)
    shape_rows = gate_accepts(gates[SHAPE_0928], report)
    topk7_rows = gate_accepts(gates[TOPK7_1P0], report)
    topk16_rows = gate_accepts(gates[TOPK16_0928], report)
    return WindowFeatures(
        all_count=len(all_rows),
        fixed_count=len(fixed_rows),
        fixed_min_cost=min_cost(fixed_rows),
        fresh_count=fresh_count(list(all_rows)),
        shape_count=len(shape_rows),
        shape_min_cost=min_cost(shape_rows),
        topk7_count=len(topk7_rows),
        topk7_fresh_count=fresh_count(topk7_rows),
        topk7_min_cost=min_cost(topk7_rows),
        topk16_count=len(topk16_rows),
        window_end=int_value(report.get("window_end")),
        window_start=int_value(report.get("window_start")),
    )


def feature_payload(features: WindowFeatures) -> dict[str, Any]:
    return {
        "all_count": features.all_count,
        "fixed_count": features.fixed_count,
        "fixed_min_cost": features.fixed_min_cost,
        "fresh_count": features.fresh_count,
        "shape_count": features.shape_count,
        "shape_min_cost": features.shape_min_cost,
        "topk16_count": features.topk16_count,
        "topk7_count": features.topk7_count,
        "topk7_fresh_count": features.topk7_fresh_count,
        "topk7_min_cost": features.topk7_min_cost,
        "window_end": features.window_end,
        "window_start": features.window_start,
    }


def make_rules() -> list[RegimeRule]:
    rules: list[RegimeRule] = [
        RegimeRule(f"always_{FIXED}", "Always use fixed two-by-two cost<=1.0.", lambda _f: FIXED),
        RegimeRule(f"always_{SHAPE_0928}", "Always use shape leaf2/row2 cost<=0.928.", lambda _f: SHAPE_0928),
        RegimeRule(f"always_{TOPK7_1P0}", "Always use all_rel2 top_k<=7 cost<=1.0.", lambda _f: TOPK7_1P0),
        RegimeRule(f"always_{TOPK7_0928}", "Always use all_rel2 top_k<=7 cost<=0.928.", lambda _f: TOPK7_0928),
        RegimeRule(f"always_{TOPK16_0928}", "Always use all_rel2 top_k<=16 cost<=0.928.", lambda _f: TOPK16_0928),
        RegimeRule(f"always_{ALL_REL2_0568}", "Always use all_rel2 cost<=0.568.", lambda _f: ALL_REL2_0568),
    ]

    def topk_if_count(threshold: int, fallback: str, topk: str = TOPK7_1P0) -> RegimeRule:
        return RegimeRule(
            f"if_topk7_count_ge_{threshold}_then_{topk}_else_{fallback}",
            f"Use {topk} when public top_k<=7 candidate count is at least {threshold}; otherwise {fallback}.",
            lambda f, threshold=threshold, fallback=fallback, topk=topk: topk if f.topk7_count >= threshold else fallback,
        )

    def topk_if_cost(limit: float, fallback: str, threshold: int = 1, topk: str = TOPK7_1P0) -> RegimeRule:
        token = str(limit).replace(".", "p")
        return RegimeRule(
            f"if_topk7_count_ge_{threshold}_and_min_cost_le_{token}_then_{topk}_else_{fallback}",
            f"Use {topk} when top_k<=7 count >= {threshold} and min public cost <= {limit}; otherwise {fallback}.",
            lambda f, limit=limit, threshold=threshold, fallback=fallback, topk=topk: (
                topk
                if f.topk7_count >= threshold and f.topk7_min_cost is not None and f.topk7_min_cost <= limit
                else fallback
            ),
        )

    def topk_if_density(delta: int, fallback: str, topk: str = TOPK7_1P0) -> RegimeRule:
        return RegimeRule(
            f"if_topk7_count_ge_shape_count_plus_{delta}_then_{topk}_else_{fallback}",
            f"Use {topk} when top_k<=7 count >= shape count plus {delta}; otherwise {fallback}.",
            lambda f, delta=delta, fallback=fallback, topk=topk: (
                topk if f.topk7_count >= f.shape_count + delta else fallback
            ),
        )

    def topk_if_fresh(threshold: int, fallback: str, topk: str = TOPK7_1P0) -> RegimeRule:
        return RegimeRule(
            f"if_topk7_fresh_count_ge_{threshold}_then_{topk}_else_{fallback}",
            f"Use {topk} when fresh top_k<=7 candidate count is at least {threshold}; otherwise {fallback}.",
            lambda f, threshold=threshold, fallback=fallback, topk=topk: (
                topk if f.topk7_fresh_count >= threshold else fallback
            ),
        )

    for fallback in (FIXED, SHAPE_0928):
        for threshold in (1, 2, 3, 5, 8, 13):
            rules.append(topk_if_count(threshold, fallback, TOPK7_1P0))
            rules.append(topk_if_count(threshold, fallback, TOPK7_0928))
        for threshold in (1, 2, 3):
            for limit in (0.568, 0.616, 0.888, 0.928, 1.0):
                rules.append(topk_if_cost(limit, fallback, threshold, TOPK7_1P0))
        for delta in (-8, -4, 0, 4, 8):
            rules.append(topk_if_density(delta, fallback, TOPK7_1P0))
        for threshold in (1, 2, 3, 5):
            rules.append(topk_if_fresh(threshold, fallback, TOPK7_1P0))
    return rules


def rule_window_attempt(
    report: dict[str, Any],
    metadata: dict[str, Any],
    gates: dict[str, p729.PublicGate],
    features: WindowFeatures,
    rule: RegimeRule,
) -> dict[str, Any]:
    policy_budget = rule.chooser(features)
    gate = gates[policy_budget]
    accepted = gate_accepts(gate, report)
    attempted_rows = accepted[: gate.budget]
    attempted_charge = 0.0
    hit = None
    mismatch_count = 0
    for row in attempted_rows:
        replay = p720.shared_replay_for_row(row, metadata)
        if replay is None:
            attempted_charge += float_value(row.get("direct_ops_over_rho"))
            continue
        attempted_charge += float_value(replay.get("shared_ops_over_rho"))
        if not replay.get("union_matches_all_fields"):
            mismatch_count += 1
        if replay.get("shared_hit"):
            hit = {"row": row, "shared_replay": replay}
            break
    return {
        "accepted_candidate_count": len(accepted),
        "attempted_candidate_count": len(attempted_rows),
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "features": feature_payload(features),
        "hit": hit,
        "hit_bool": hit is not None,
        "mismatch_count": mismatch_count,
        "policy_budget": policy_budget,
        "precheck_window": bool(accepted),
        "window_end": report.get("window_end"),
        "window_start": report.get("window_start"),
    }


def evaluate_rule(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: dict[str, p729.PublicGate],
    features_by_window: dict[tuple[int, int], WindowFeatures],
    rule: RegimeRule,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    mismatch_count = 0
    accepted_candidate_count = 0
    precheck_window_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    policy_counts: dict[str, int] = {}
    for report in reports:
        key = (int_value(report.get("window_start")), int_value(report.get("window_end")))
        attempt = rule_window_attempt(report, metadata, gates, features_by_window[key], rule)
        policy_counts[attempt["policy_budget"]] = policy_counts.get(attempt["policy_budget"], 0) + 1
        accepted_candidate_count += int_value(attempt["accepted_candidate_count"])
        attempted_count += int_value(attempt["attempted_candidate_count"])
        attempted_charge += float_value(attempt["attempted_source_charge_over_rho"])
        mismatch_count += int_value(attempt["mismatch_count"])
        if attempt["precheck_window"]:
            precheck_window_count += 1
        hit = attempt.get("hit")
        if hit:
            hit_count += 1
            if len(hit_samples) < sample_limit:
                hit_samples.append(
                    {
                        "features": attempt["features"],
                        "policy_budget": attempt["policy_budget"],
                        "row": p729.p716.sample_row(hit["row"], None),
                        "shared_replay": hit["shared_replay"],
                        "window_end": attempt["window_end"],
                        "window_start": attempt["window_start"],
                    }
                )
        else:
            fallback_charge += 1.0
            if len(miss_samples) < sample_limit:
                miss_samples.append(
                    {
                        "accepted_candidate_count": attempt["accepted_candidate_count"],
                        "features": attempt["features"],
                        "policy_budget": attempt["policy_budget"],
                        "window_end": attempt["window_end"],
                        "window_start": attempt["window_start"],
                    }
                )
    window_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "accepted_candidate_count": accepted_candidate_count,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "factor_charge_over_rho": round(factor_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "mismatch_count": mismatch_count,
        "miss_samples": miss_samples,
        "policy_counts": policy_counts,
        "precheck_window_count": precheck_window_count,
        "rule_description": rule.description,
        "rule_name": rule.name,
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
        str(report.get("rule_name")),
    )


def choose_best(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(rows, key=eval_sort_key)[0] if rows else {}


def total(report: dict[str, Any] | None) -> float | None:
    if report is None:
        return None
    value = report.get("source_replay_total_with_fallback_over_rho")
    return None if value is None else float_value(value)


def compact(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if report is None:
        return None
    return {
        "accepted_candidate_count": report.get("accepted_candidate_count"),
        "attempted_candidate_count": report.get("attempted_candidate_count"),
        "attempted_source_charge_over_rho": report.get("attempted_source_charge_over_rho"),
        "beats_rho_with_fallback": report.get("beats_rho_with_fallback"),
        "fallback_charge_over_rho": report.get("fallback_charge_over_rho"),
        "factor_charge_over_rho": report.get("factor_charge_over_rho"),
        "hit_count": report.get("hit_count"),
        "policy_counts": report.get("policy_counts"),
        "rule_name": report.get("rule_name"),
        "source_replay_total_with_fallback_over_rho": report.get("source_replay_total_with_fallback_over_rho"),
        "vs_independent_rho_with_fallback_over_rho": report.get("vs_independent_rho_with_fallback_over_rho"),
        "window_count": report.get("window_count"),
    }


def split_window_ranges(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "first": None if not reports else [reports[0]["window_start"], reports[0]["window_end"]],
        "last": None if not reports else [reports[-1]["window_start"], reports[-1]["window_end"]],
        "window_count": len(reports),
    }


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: dict[str, p729.PublicGate],
    features_by_window: dict[tuple[int, int], WindowFeatures],
    rules: list[RegimeRule],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_rule_scores = [
        evaluate_rule(train, metadata, gates, features_by_window, rule, factor_charge, sample_limit)
        for rule in rules
    ]
    selected_rule_name = str(choose_best(train_rule_scores).get("rule_name"))
    selected_rule = next(rule for rule in rules if rule.name == selected_rule_name)
    holdout_rule_scores = [
        evaluate_rule(holdout, metadata, gates, features_by_window, rule, factor_charge, sample_limit)
        for rule in rules
    ]
    fixed_rule = next(rule for rule in rules if rule.name == f"always_{FIXED}")
    topk_oracle_rule = next(rule for rule in rules if rule.name == f"always_{TOPK7_1P0}")
    return {
        **split,
        "best_heldout_rule_new_bank": choose_best(holdout_rule_scores),
        "fixed_reference_new_bank": evaluate_rule(
            holdout,
            metadata,
            gates,
            features_by_window,
            fixed_rule,
            factor_charge,
            sample_limit,
        ),
        "selected_holdout_new_bank": evaluate_rule(
            holdout,
            metadata,
            gates,
            features_by_window,
            selected_rule,
            factor_charge,
            sample_limit,
        ),
        "selected_rule_name": selected_rule.name,
        "top_train_rules": sorted(train_rule_scores, key=eval_sort_key)[:8],
        "topk7_oracle_reference_new_bank": evaluate_rule(
            holdout,
            metadata,
            gates,
            features_by_window,
            topk_oracle_rule,
            factor_charge,
            sample_limit,
        ),
        "window_ranges": {
            "holdout": split_window_ranges(holdout),
            "train": split_window_ranges(train),
        },
    }


def below_count(split_payloads: list[dict[str, Any]], key: str) -> int:
    return sum(1 for report in split_payloads if (report.get(key) or {}).get("beats_rho_with_fallback"))


def focus_report(split_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for report in split_payloads:
        if report.get("split") == FOCUS_SPLIT:
            return report
    return {}


def determine_claim(split_payloads: list[dict[str, Any]]) -> str:
    focus = focus_report(split_payloads)
    fixed = total(focus.get("fixed_reference_new_bank"))
    selected = total(focus.get("selected_holdout_new_bank"))
    best = total(focus.get("best_heldout_rule_new_bank"))
    fixed_below = below_count(split_payloads, "fixed_reference_new_bank")
    selected_below = below_count(split_payloads, "selected_holdout_new_bank")
    if fixed is not None and selected is not None and selected < fixed and selected < 16 and selected_below >= fixed_below:
        return "P730_PUBLIC_WINDOW_REGIME_SELECTOR_IMPROVES_FOCUS_WITH_NO_SPLIT_WIN_REGRESSION"
    if fixed is not None and selected is not None and selected < fixed and selected < 16:
        return "P730_PUBLIC_WINDOW_REGIME_SELECTOR_IMPROVES_FOCUS_BUT_SPLIT_STABILITY_OPEN"
    if any(
        total(report.get("selected_holdout_new_bank")) is not None
        and total(report.get("fixed_reference_new_bank")) is not None
        and total(report.get("selected_holdout_new_bank")) < total(report.get("fixed_reference_new_bank"))
        for report in split_payloads
    ):
        return "P730_PUBLIC_WINDOW_REGIME_SELECTOR_IMPROVES_AT_LEAST_ONE_SPLIT_BUT_NOT_FOCUS"
    if fixed is not None and best is not None and best < fixed:
        return "P730_WINDOW_REGIME_GAP_REMAINS_HELDOUT_RULE_ONLY"
    return "NEGATIVE_RESULT_P730_PUBLIC_WINDOW_REGIME_SELECTOR_DOES_NOT_IMPROVE_FIXED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p729_payload = load_json(Path(args.p729_reference))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    merged_reports, merged_metadata, merge_stats = p729.build_merged_reports(args)
    all_gates = p729.make_gates(
        merged_reports,
        parse_floats(args.thresholds),
        parse_ints(args.attempt_budgets),
        int_value(args.selector_limit),
    )
    gates = {policy_budget: p729.gate_by_policy_budget(all_gates, policy_budget) for policy_budget in REGIME_POLICY_BUDGETS}
    features_by_window = {
        (int_value(report.get("window_start")), int_value(report.get("window_end"))): window_features(report, gates)
        for report in merged_reports
    }
    rules = make_rules()
    split_payloads = [
        evaluate_split(
            split,
            merged_reports,
            merged_metadata,
            gates,
            features_by_window,
            rules,
            factor_charge,
            int_value(args.sample_limit),
        )
        for split in split_reports(merged_reports, args)
    ]
    focus = focus_report(split_payloads)
    replay_cache = merged_metadata.get("shared_replay_cache") or {}
    payload = {
        "artifacts": {
            "p729": str(Path(args.p729_reference)),
            "p709": str(Path(args.p709)),
        },
        "claim_status": "",
        "created_at": now_iso(),
        "focus_split": FOCUS_SPLIT,
        "focus_summary": {
            "best_heldout_rule_name": (focus.get("best_heldout_rule_new_bank") or {}).get("rule_name"),
            "best_heldout_rule_total": total(focus.get("best_heldout_rule_new_bank")),
            "fixed_total": total(focus.get("fixed_reference_new_bank")),
            "p729_focus_heldout_oracle_total": (p729_payload.get("focus_summary") or {}).get("heldout_oracle_total"),
            "p729_focus_train_selected_total": (p729_payload.get("focus_summary") or {}).get(
                "new_bank_train_selected_total"
            ),
            "rho_baseline": 16,
            "selected_rule_name": focus.get("selected_rule_name"),
            "selected_rule_total": total(focus.get("selected_holdout_new_bank")),
            "topk7_oracle_reference_total": total(focus.get("topk7_oracle_reference_new_bank")),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows are archived AutoLab toy-harness materializer rows.",
            "REPLAY-BACKED: charged candidates use the P719 shared-core replay path.",
            "LABEL-DISCIPLINE: train-selected rules are selected from training splits, not heldout verifier labels.",
            "PUBLIC-WINDOW FEATURES: rule predicates use only pre-replay candidate counts and public direct-cost descriptors.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p730_public_window_regime_selector",
        "parameters": {
            "attempt_budgets": parse_ints(args.attempt_budgets),
            "base_source_pattern": args.base_source_pattern,
            "factor_bank_charge_over_rho": factor_charge,
            "fresh_source_pattern": args.fresh_source_pattern,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "regime_policy_budgets": REGIME_POLICY_BUDGETS,
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "rule_count": len(rules),
            "selector_limit": int_value(args.selector_limit),
            "target": args.target,
            "thresholds": parse_floats(args.thresholds),
        },
        "replay_metadata": {
            "candidate_count": sum(len(report.get("candidates") or []) for report in merged_reports),
            "shared_replay_cache_count": len(replay_cache),
            "shared_replay_error_count": len(merged_metadata.get("shared_replay_errors") or {}),
            "shared_replay_errors": merged_metadata.get("shared_replay_errors") or {},
            "unique_union_mismatch_count": sum(
                1 for replay in replay_cache.values() if not replay.get("union_matches_all_fields")
            ),
        },
        "schema": "ecdlp.low_term_total2_p730_public_window_regime_selector.v1",
        "source_merge_stats": merge_stats,
        "split_reports": split_payloads,
        "split_summary": {
            "best_heldout_rule_below_rho_splits": below_count(split_payloads, "best_heldout_rule_new_bank"),
            "fixed_reference_below_rho_splits": below_count(split_payloads, "fixed_reference_new_bank"),
            "selected_rule_below_rho_splits": below_count(split_payloads, "selected_holdout_new_bank"),
            "split_count": len(split_payloads),
            "topk7_oracle_reference_below_rho_splits": below_count(split_payloads, "topk7_oracle_reference_new_bank"),
        },
        "window_feature_summary": {
            "features": [feature_payload(features) for features in features_by_window.values()],
        },
    }
    payload["claim_status"] = determine_claim(split_payloads)
    return payload


def compact_split(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "best_heldout_rule_new_bank": compact(report.get("best_heldout_rule_new_bank")),
        "fixed_reference_new_bank": compact(report.get("fixed_reference_new_bank")),
        "selected_holdout_new_bank": compact(report.get("selected_holdout_new_bank")),
        "selected_rule_name": report.get("selected_rule_name"),
        "split": report.get("split"),
        "topk7_oracle_reference_new_bank": compact(report.get("topk7_oracle_reference_new_bank")),
        "window_ranges": report.get("window_ranges"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=BASE_PATTERN)
    parser.add_argument("--fresh-source-pattern", default=FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p729-reference", default=str(P729_REFERENCE))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=4)
    parser.add_argument("--selector-limit", type=int, default=10)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.488,0.52,0.544,0.568,0.616,0.888,0.928,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "focus_summary": payload["focus_summary"],
                "replay_metadata": {
                    key: value
                    for key, value in payload["replay_metadata"].items()
                    if key != "shared_replay_errors"
                },
                "source_merge_stats": payload["source_merge_stats"],
                "split_compact": [compact_split(report) for report in payload["split_reports"]],
                "split_summary": payload["split_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
