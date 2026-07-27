#!/usr/bin/env python3
"""P729 public selector-gap audit over P728 target-materialized rows."""

from __future__ import annotations

import argparse
import copy
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p720_shared_core_temporal_generalization_audit as p720
import low_term_total2_p722_shared_core_fresh_density_rescue as p722


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p729_selector_gap_rank_gated_transfer_probe.json"
BASE_PATTERN = "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"
FRESH_PATTERN = "frontier_public_leaf_policy_p72*_target67_materialized_fixed_row_*_col15_selector_expanded_probe.json"
FOCUS_SPLIT = "rolling_train24_holdout16_start16"
FIXED_POLICY_BUDGET = "two_by_two_any_cost_le_1p0:budget1"
P728_ORACLE_POLICY_BUDGET = "all_rel2_cost_le_0p568:budget1"


@dataclass(frozen=True)
class PublicGate:
    name: str
    family: str
    budget: int
    threshold: float | None = None
    group: str | None = None
    selector: str | None = None
    source_policy: str | None = None
    source_cap: int | None = None
    top_k_le: int | None = None
    row_key_width: int | None = None
    leaf_count: int | None = None
    row_count: int | None = None
    rank_min: int | None = None

    @property
    def policy_budget(self) -> str:
        return f"{self.name}:budget{self.budget}"


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


def threshold_token(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def source_case(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_case") or {}


def source_rank(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("rank"))


def source_top_k(row: dict[str, Any]) -> int:
    return int_value(source_case(row).get("top_k"))


def row_key_width(row: dict[str, Any]) -> int:
    return len(source_case(row).get("row_keys") or [])


def source_policy(row: dict[str, Any]) -> str:
    return str(source_case(row).get("source_policy") or "")


def source_cap(row: dict[str, Any]) -> int | None:
    match = re.search(r"_cap(\d+)_", source_policy(row))
    return None if match is None else int(match.group(1))


def gate_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return p716.row_sort_key(row)


def group_accepts(group: str, row: dict[str, Any]) -> bool:
    return p716.policy_accepts(p716.SourcePolicy(group, group), row)


def gate_accepts(gate: PublicGate, row: dict[str, Any]) -> bool:
    if gate.threshold is not None and float_value(row.get("direct_ops_over_rho"), 999999.0) > gate.threshold:
        return False
    if gate.group is not None and not group_accepts(gate.group, row):
        return False
    if gate.selector is not None and str(row.get("selector")) != gate.selector:
        return False
    if gate.source_policy is not None and source_policy(row) != gate.source_policy:
        return False
    if gate.source_cap is not None and source_cap(row) != gate.source_cap:
        return False
    if gate.top_k_le is not None and source_top_k(row) > gate.top_k_le:
        return False
    if gate.row_key_width is not None and row_key_width(row) != gate.row_key_width:
        return False
    if gate.leaf_count is not None and int_value(row.get("selected_leaf_count")) != gate.leaf_count:
        return False
    if gate.row_count is not None and int_value(row.get("selected_row_count")) != gate.row_count:
        return False
    if gate.rank_min is not None and source_rank(row) < gate.rank_min:
        return False
    return True


def policy_name(
    base: str,
    threshold: float | None = None,
    suffixes: tuple[str, ...] = (),
) -> str:
    pieces = [base]
    if threshold is not None:
        pieces.append(f"cost_le_{threshold_token(threshold)}")
    pieces.extend(suffixes)
    return "_".join(pieces)


def collect_public_values(reports: list[dict[str, Any]], selector_limit: int) -> dict[str, Any]:
    selector_counts: dict[str, int] = {}
    source_policy_counts: dict[str, int] = {}
    caps: set[int] = set()
    topks: set[int] = set()
    widths: set[int] = set()
    shapes: set[tuple[int, int]] = set()
    ranks: set[int] = set()
    candidate_count = 0
    for report in reports:
        for row in report.get("candidates") or []:
            candidate_count += 1
            selector = str(row.get("selector"))
            selector_counts[selector] = selector_counts.get(selector, 0) + 1
            sp = source_policy(row)
            source_policy_counts[sp] = source_policy_counts.get(sp, 0) + 1
            cap = source_cap(row)
            if cap is not None:
                caps.add(cap)
            if source_top_k(row):
                topks.add(source_top_k(row))
            widths.add(row_key_width(row))
            shapes.add((int_value(row.get("selected_leaf_count")), int_value(row.get("selected_row_count"))))
            ranks.add(source_rank(row))
    top_selectors = [
        selector
        for selector, _count in sorted(selector_counts.items(), key=lambda item: (-item[1], item[0]))[:selector_limit]
    ]
    return {
        "candidate_count": candidate_count,
        "rank_values": sorted(ranks),
        "selector_counts": selector_counts,
        "source_policy_counts": source_policy_counts,
        "source_caps": sorted(caps),
        "top_eligible_selectors": top_selectors,
        "top_k_values": sorted(topks),
        "row_key_widths": sorted(widths),
        "shapes": sorted([list(shape) for shape in shapes]),
    }


def make_gates(
    reports: list[dict[str, Any]],
    thresholds: tuple[float, ...],
    budgets: tuple[int, ...],
    selector_limit: int,
) -> list[PublicGate]:
    public = collect_public_values(reports, selector_limit)
    seen: set[str] = set()
    gates: list[PublicGate] = []

    def add(gate: PublicGate) -> None:
        if gate.policy_budget in seen:
            return
        seen.add(gate.policy_budget)
        gates.append(gate)

    groups = ("all_rel2", "two_by_two_any", "low_term_any", "cost_low_term_any")
    focused_thresholds = tuple(t for t in thresholds if t in {0.568, 0.616, 0.928, 1.0})
    selector_thresholds = tuple(t for t in thresholds if t in {0.568, 0.928, 1.0})
    source_policy_thresholds = tuple(t for t in thresholds if t in {0.568, 1.0})
    topk_thresholds = tuple(t for t in thresholds if t in {0.568, 0.928, 1.0})

    for budget in budgets:
        for group in groups:
            add(PublicGate(name=group, family="base_group", budget=budget, group=group))
            for threshold in thresholds:
                add(
                    PublicGate(
                        name=policy_name(group, threshold),
                        family="base_group_threshold",
                        budget=budget,
                        group=group,
                        threshold=threshold,
                    )
                )

        for threshold in focused_thresholds:
            for group in ("all_rel2", "two_by_two_any"):
                add(
                    PublicGate(
                        name=policy_name(group, threshold, ("rank_ge_2",)),
                        family="rank_gate",
                        budget=budget,
                        group=group,
                        threshold=threshold,
                        rank_min=2,
                    )
                )
            for cap in public["source_caps"]:
                add(
                    PublicGate(
                        name=policy_name("all_rel2", threshold, (f"cap{cap}",)),
                        family="source_cap_gate",
                        budget=budget,
                        group="all_rel2",
                        threshold=threshold,
                        source_cap=cap,
                    )
                )
            for width in public["row_key_widths"]:
                add(
                    PublicGate(
                        name=policy_name("all_rel2", threshold, (f"rowwidth{width}",)),
                        family="row_width_gate",
                        budget=budget,
                        group="all_rel2",
                        threshold=threshold,
                        row_key_width=width,
                    )
                )

        for selector in public["top_eligible_selectors"]:
            selector_token = selector.replace("mode_", "").replace("_", "-")
            for threshold in selector_thresholds:
                add(
                    PublicGate(
                        name=policy_name(f"selector_{selector_token}", threshold),
                        family="selector_exact_gate",
                        budget=budget,
                        selector=selector,
                        threshold=threshold,
                    )
                )

        for sp in sorted(public["source_policy_counts"]):
            policy_token = sp.replace("fixed_target_", "target_")
            for threshold in source_policy_thresholds:
                add(
                    PublicGate(
                        name=policy_name(f"source_policy_{policy_token}", threshold),
                        family="source_policy_gate",
                        budget=budget,
                        source_policy=sp,
                        threshold=threshold,
                    )
                )

        for top_k in public["top_k_values"]:
            for threshold in topk_thresholds:
                add(
                    PublicGate(
                        name=policy_name("all_rel2", threshold, (f"topk_le_{top_k}",)),
                        family="topk_gate",
                        budget=budget,
                        group="all_rel2",
                        threshold=threshold,
                        top_k_le=top_k,
                    )
                )

        for leaf_count, row_count in [tuple(shape) for shape in public["shapes"]]:
            for threshold in focused_thresholds:
                add(
                    PublicGate(
                        name=policy_name("all_rel2", threshold, (f"leaf{leaf_count}_row{row_count}",)),
                        family="shape_gate",
                        budget=budget,
                        group="all_rel2",
                        threshold=threshold,
                        leaf_count=leaf_count,
                        row_count=row_count,
                    )
                )

    return gates


def sample_gate(gate: PublicGate) -> dict[str, Any]:
    return {
        "budget": gate.budget,
        "family": gate.family,
        "group": gate.group,
        "leaf_count": gate.leaf_count,
        "name": gate.name,
        "policy_budget": gate.policy_budget,
        "rank_min": gate.rank_min,
        "row_count": gate.row_count,
        "row_key_width": gate.row_key_width,
        "selector": gate.selector,
        "source_cap": gate.source_cap,
        "source_policy": gate.source_policy,
        "threshold": gate.threshold,
        "top_k_le": gate.top_k_le,
    }


def evaluate_gate(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gate: PublicGate,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    mismatch_count = 0
    precheck_window_count = 0
    accepted_candidate_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    for report in reports:
        accepted = [row for row in report.get("candidates") or [] if gate_accepts(gate, row)]
        accepted.sort(key=gate_sort_key)
        accepted_candidate_count += len(accepted)
        if accepted:
            precheck_window_count += 1
        hit = None
        charge = 0.0
        attempted = 0
        for row in accepted[: gate.budget]:
            attempted += 1
            replay = p720.shared_replay_for_row(row, metadata)
            if replay is None:
                charge += float_value(row.get("direct_ops_over_rho"))
                continue
            charge += float_value(replay.get("shared_ops_over_rho"))
            if not replay.get("union_matches_all_fields"):
                mismatch_count += 1
            if replay.get("shared_hit"):
                hit = (row, replay)
                break
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(hit_samples) < sample_limit:
                hit_samples.append(
                    {
                        "row": p716.sample_row(hit[0], None),
                        "shared_replay": hit[1],
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
                        "first_candidates": [p716.sample_row(row, None) for row in accepted[: min(3, len(accepted))]],
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
        "attempt_budget": gate.budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "factor_charge_over_rho": round(factor_charge, 8),
        "gate": sample_gate(gate),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "mismatch_count": mismatch_count,
        "miss_samples": miss_samples,
        "policy_budget": gate.policy_budget,
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
        int_value(report.get("attempt_budget")),
        str(report.get("policy_budget")),
    )


def choose_best(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(reports, key=eval_sort_key)[0] if reports else {}


def compact(report: dict[str, Any] | None) -> dict[str, Any] | None:
    if report is None:
        return None
    return {
        "attempt_budget": report.get("attempt_budget"),
        "attempted_candidate_count": report.get("attempted_candidate_count"),
        "attempted_source_charge_over_rho": report.get("attempted_source_charge_over_rho"),
        "beats_rho_with_fallback": report.get("beats_rho_with_fallback"),
        "fallback_charge_over_rho": report.get("fallback_charge_over_rho"),
        "factor_charge_over_rho": report.get("factor_charge_over_rho"),
        "gate": report.get("gate"),
        "hit_count": report.get("hit_count"),
        "policy_budget": report.get("policy_budget"),
        "precheck_window_count": report.get("precheck_window_count"),
        "source_replay_total_with_fallback_over_rho": report.get("source_replay_total_with_fallback_over_rho"),
        "vs_independent_rho_with_fallback_over_rho": report.get("vs_independent_rho_with_fallback_over_rho"),
        "window_count": report.get("window_count"),
    }


def evaluate_all(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: list[PublicGate],
    factor_charge: float,
    sample_limit: int,
) -> list[dict[str, Any]]:
    return [evaluate_gate(reports, metadata, gate, factor_charge, sample_limit) for gate in gates]


def gate_by_policy_budget(gates: list[PublicGate], policy_budget: str) -> PublicGate:
    for gate in gates:
        if gate.policy_budget == policy_budget:
            return gate
    raise KeyError(policy_budget)


def split_reports(reports: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    return p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    gates: list[PublicGate],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_marginal = evaluate_all(train, metadata, gates, 0.0, sample_limit)
    train_new = evaluate_all(train, metadata, gates, factor_charge, sample_limit)
    holdout_new = evaluate_all(holdout, metadata, gates, factor_charge, sample_limit)
    marginal_selected = gate_by_policy_budget(gates, str(choose_best(train_marginal).get("policy_budget")))
    new_selected = gate_by_policy_budget(gates, str(choose_best(train_new).get("policy_budget")))
    fixed_gate = gate_by_policy_budget(gates, FIXED_POLICY_BUDGET)
    oracle_reference_gate = gate_by_policy_budget(gates, P728_ORACLE_POLICY_BUDGET)
    marginal_selected_holdout_new = evaluate_gate(holdout, metadata, marginal_selected, factor_charge, sample_limit)
    new_selected_holdout_new = evaluate_gate(holdout, metadata, new_selected, factor_charge, sample_limit)
    fixed_holdout_new = evaluate_gate(holdout, metadata, fixed_gate, factor_charge, sample_limit)
    oracle_reference_holdout_new = evaluate_gate(holdout, metadata, oracle_reference_gate, factor_charge, sample_limit)
    return {
        **split,
        "fixed_reference_new_bank": fixed_holdout_new,
        "heldout_oracle_best_new_bank": choose_best(holdout_new),
        "marginal_train_selected_holdout_new_bank": marginal_selected_holdout_new,
        "marginal_train_selected_policy_budget": marginal_selected.policy_budget,
        "new_bank_train_selected_holdout_new_bank": new_selected_holdout_new,
        "new_bank_train_selected_policy_budget": new_selected.policy_budget,
        "p728_oracle_family_reference_new_bank": oracle_reference_holdout_new,
        "top_heldout_oracle_new_bank": sorted(holdout_new, key=eval_sort_key)[:8],
        "top_train_marginal_existing_bank": sorted(train_marginal, key=eval_sort_key)[:8],
        "top_train_new_bank": sorted(train_new, key=eval_sort_key)[:8],
        "train_window_count": len(train),
        "window_ranges": {
            "holdout": [[report["window_start"], report["window_end"]] for report in holdout[:3]],
            "holdout_last": None if not holdout else [holdout[-1]["window_start"], holdout[-1]["window_end"]],
            "train": [[report["window_start"], report["window_end"]] for report in train[:3]],
            "train_last": None if not train else [train[-1]["window_start"], train[-1]["window_end"]],
        },
    }


def below_count(split_payloads: list[dict[str, Any]], key: str) -> int:
    return sum(1 for report in split_payloads if (report.get(key) or {}).get("beats_rho_with_fallback"))


def total(report: dict[str, Any] | None) -> float | None:
    if report is None:
        return None
    value = report.get("source_replay_total_with_fallback_over_rho")
    return None if value is None else float_value(value)


def focus_report(split_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    for report in split_payloads:
        if report.get("split") == FOCUS_SPLIT:
            return report
    return {}


def determine_claim(split_payloads: list[dict[str, Any]]) -> str:
    focus = focus_report(split_payloads)
    fixed = total(focus.get("fixed_reference_new_bank"))
    selected = total(focus.get("new_bank_train_selected_holdout_new_bank"))
    oracle = total(focus.get("heldout_oracle_best_new_bank"))
    fixed_below = below_count(split_payloads, "fixed_reference_new_bank")
    selected_below = below_count(split_payloads, "new_bank_train_selected_holdout_new_bank")
    if fixed is not None and selected is not None and selected < fixed and selected < 16 and selected_below >= fixed_below:
        return "P729_PUBLIC_SELECTOR_IMPROVES_FOCUSED_LATER_HOLDOUT_WITH_NO_SPLIT_WIN_REGRESSION"
    if fixed is not None and selected is not None and selected < fixed and selected < 16:
        return "P729_PUBLIC_SELECTOR_IMPROVES_FOCUSED_LATER_HOLDOUT_BUT_SPLIT_STABILITY_OPEN"
    if any(
        total(report.get("new_bank_train_selected_holdout_new_bank")) is not None
        and total(report.get("fixed_reference_new_bank")) is not None
        and total(report.get("new_bank_train_selected_holdout_new_bank")) < total(report.get("fixed_reference_new_bank"))
        for report in split_payloads
    ):
        return "P729_PUBLIC_SELECTOR_NARROWS_AT_LEAST_ONE_SPLIT_BUT_NOT_FOCUSED_LATER_HOLDOUT"
    if oracle is not None and fixed is not None and oracle < fixed:
        return "P729_SELECTOR_GAP_REMAINS_HELDOUT_ORACLE_ONLY"
    return "NEGATIVE_RESULT_P729_PUBLIC_SELECTOR_GATES_DO_NOT_IMPROVE_P728_FIXED_BASELINE"


def compact_split(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "fixed_reference_new_bank": compact(report.get("fixed_reference_new_bank")),
        "heldout_oracle_best_new_bank": compact(report.get("heldout_oracle_best_new_bank")),
        "marginal_train_selected_holdout_new_bank": compact(report.get("marginal_train_selected_holdout_new_bank")),
        "marginal_train_selected_policy_budget": report.get("marginal_train_selected_policy_budget"),
        "new_bank_train_selected_holdout_new_bank": compact(report.get("new_bank_train_selected_holdout_new_bank")),
        "new_bank_train_selected_policy_budget": report.get("new_bank_train_selected_policy_budget"),
        "p728_oracle_family_reference_new_bank": compact(report.get("p728_oracle_family_reference_new_bank")),
        "split": report.get("split"),
        "window_ranges": report.get("window_ranges"),
    }


def build_merged_reports(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    base_reports, base_metadata = p722.build_reports(args, args.base_source_pattern)
    fresh_reports, fresh_metadata = p722.build_reports(args, args.fresh_source_pattern)
    merged_reports, merged_metadata, merge_stats = p722.merge_reports(
        base_reports,
        fresh_reports,
        base_metadata,
        fresh_metadata,
    )
    return merged_reports, merged_metadata, merge_stats


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    thresholds = parse_floats(args.thresholds)
    budgets = parse_ints(args.attempt_budgets)
    merged_reports, merged_metadata, merge_stats = build_merged_reports(args)
    public_values = collect_public_values(merged_reports, int_value(args.selector_limit))
    gates = make_gates(merged_reports, thresholds, budgets, int_value(args.selector_limit))
    split_payloads = [
        evaluate_split(split, merged_reports, merged_metadata, gates, factor_charge, int_value(args.sample_limit))
        for split in split_reports(merged_reports, args)
    ]
    full_new = evaluate_all(merged_reports, merged_metadata, gates, factor_charge, int_value(args.sample_limit))
    focus = focus_report(split_payloads)
    replay_cache = merged_metadata.get("shared_replay_cache") or {}
    payload = {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p728": str(STATE_DIR / "low_term_total2_p728_later_holdout_target67_shared_core_probe.json"),
        },
        "claim_status": "",
        "created_at": now_iso(),
        "focus_split": FOCUS_SPLIT,
        "focus_summary": {
            "fixed_total": total(focus.get("fixed_reference_new_bank")),
            "heldout_oracle_total": total(focus.get("heldout_oracle_best_new_bank")),
            "marginal_train_selected_policy_budget": focus.get("marginal_train_selected_policy_budget"),
            "marginal_train_selected_total": total(focus.get("marginal_train_selected_holdout_new_bank")),
            "new_bank_train_selected_policy_budget": focus.get("new_bank_train_selected_policy_budget"),
            "new_bank_train_selected_total": total(focus.get("new_bank_train_selected_holdout_new_bank")),
            "p728_oracle_family_reference_total": total(focus.get("p728_oracle_family_reference_new_bank")),
            "rho_baseline": 16,
        },
        "full_population": {
            "best_new_bank": choose_best(full_new),
            "fixed_reference_new_bank": evaluate_gate(
                merged_reports,
                merged_metadata,
                gate_by_policy_budget(gates, FIXED_POLICY_BUDGET),
                factor_charge,
                int_value(args.sample_limit),
            ),
            "p728_oracle_family_reference_new_bank": evaluate_gate(
                merged_reports,
                merged_metadata,
                gate_by_policy_budget(gates, P728_ORACLE_POLICY_BUDGET),
                factor_charge,
                int_value(args.sample_limit),
            ),
            "top_new_bank": sorted(full_new, key=eval_sort_key)[:12],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows are archived AutoLab toy-harness materializer rows.",
            "REPLAY-BACKED: charged candidates use the P719 shared-core replay path.",
            "LABEL-DISCIPLINE: train-selected policies are selected from training splits, not heldout verifier labels.",
            "PUBLIC-DESCRIPTOR UNIVERSE: policy families are generated from public row descriptors, not source_verified or public_key_verified labels.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p729_selector_gap_rank_gated_transfer",
        "parameters": {
            "attempt_budgets": budgets,
            "base_source_pattern": args.base_source_pattern,
            "factor_bank_charge_over_rho": factor_charge,
            "fixed_policy_budget": FIXED_POLICY_BUDGET,
            "fresh_source_pattern": args.fresh_source_pattern,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "p728_oracle_policy_budget": P728_ORACLE_POLICY_BUDGET,
            "policy_gate_count": len(gates),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "selector_limit": int_value(args.selector_limit),
            "target": args.target,
            "thresholds": thresholds,
        },
        "public_descriptor_summary": public_values,
        "replay_metadata": {
            "candidate_count": public_values["candidate_count"],
            "shared_replay_cache_count": len(replay_cache),
            "shared_replay_error_count": len(merged_metadata.get("shared_replay_errors") or {}),
            "shared_replay_errors": merged_metadata.get("shared_replay_errors") or {},
            "unique_union_mismatch_count": sum(
                1 for replay in replay_cache.values() if not replay.get("union_matches_all_fields")
            ),
        },
        "schema": "ecdlp.low_term_total2_p729_selector_gap_rank_gated_transfer.v1",
        "source_merge_stats": merge_stats,
        "split_reports": split_payloads,
        "split_summary": {
            "fixed_reference_new_bank_below_rho_splits": below_count(split_payloads, "fixed_reference_new_bank"),
            "heldout_oracle_best_new_bank_below_rho_splits": below_count(
                split_payloads,
                "heldout_oracle_best_new_bank",
            ),
            "marginal_train_selected_new_bank_below_rho_splits": below_count(
                split_payloads,
                "marginal_train_selected_holdout_new_bank",
            ),
            "new_bank_train_selected_new_bank_below_rho_splits": below_count(
                split_payloads,
                "new_bank_train_selected_holdout_new_bank",
            ),
            "p728_oracle_family_reference_new_bank_below_rho_splits": below_count(
                split_payloads,
                "p728_oracle_family_reference_new_bank",
            ),
            "split_count": len(split_payloads),
        },
    }
    payload["claim_status"] = determine_claim(split_payloads)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2")
    parser.add_argument("--base-source-pattern", default=BASE_PATTERN)
    parser.add_argument("--fresh-source-pattern", default=FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
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
