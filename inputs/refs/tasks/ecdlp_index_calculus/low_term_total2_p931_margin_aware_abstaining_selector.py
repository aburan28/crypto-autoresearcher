#!/usr/bin/env python3
"""P931 margin-aware abstaining selector for P930 inner-CV failures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p922_support_class_cost_audit as p922
import low_term_total2_p923_train_only_support_class_redteam as p923
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925
import low_term_total2_p926_gap_source_fallback_audit as p926
import low_term_total2_p928_p903_blind_second_holdout_audit as p928
import low_term_total2_p929_fit_only_support_ensemble_audit as p929
import low_term_total2_p930_inner_cv_oracle_distillation_audit as p930


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p931_margin_aware_abstaining_selector.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p931_margin_aware_abstaining_selector_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P930_SOURCE = STATE_DIR / "low_term_total2_p930_inner_cv_oracle_distillation_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p931_margin_aware_abstaining_selector.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
MARGIN_STRATEGIES = (
    {"name": "margin0_min2", "margin": 0, "min_inner_wins": 2, "cost_first": False},
    {"name": "margin32_min2", "margin": 32, "min_inner_wins": 2, "cost_first": False},
    {"name": "margin64_min2", "margin": 64, "min_inner_wins": 2, "cost_first": False},
    {"name": "margin128_min2", "margin": 128, "min_inner_wins": 2, "cost_first": False},
    {"name": "margin0_min3", "margin": 0, "min_inner_wins": 3, "cost_first": False},
    {"name": "margin0_min4", "margin": 0, "min_inner_wins": 4, "cost_first": False},
    {"name": "cost_first_margin0_min2", "margin": 0, "min_inner_wins": 2, "cost_first": True},
    {"name": "cost_first_margin64_min2", "margin": 64, "min_inner_wins": 2, "cost_first": True},
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p908.int_value(value, default)


def public_c19_cost(indices: set[int], rows_by_index: dict[int, dict[str, Any]]) -> int:
    return p930.c19_cost(indices, rows_by_index)


def selected_public_indices(
    rules: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
) -> set[int]:
    return p929.selected_indices_for_rules(rules, public_rows, atoms_by_name)


def clean_candidate_rules(context: dict[str, Any], seed: dict[str, Any]) -> list[dict[str, Any]]:
    return p930.clean_candidate_rules(context, seed)


def choose_margin_rule(
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
    seed: dict[str, Any],
    margin: int,
    min_inner_wins: int,
    cost_first: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected = [seed] if seed else []
    seed_public_indices = selected_public_indices(selected, public_rows, atoms_by_name)
    seed_public_cost = companion_cost + public_c19_cost(seed_public_indices, rows_by_index)
    best_rule: dict[str, Any] | None = None
    best_score: dict[str, Any] = {}
    best_key: tuple[Any, ...] | None = None
    for rule in clean_candidate_rules(context, seed):
        rule_public_indices = selected_public_indices([rule], public_rows, atoms_by_name)
        selected_indices = seed_public_indices | rule_public_indices
        full_public_cost = companion_cost + public_c19_cost(selected_indices, rows_by_index)
        if full_public_cost >= p919_cost - margin:
            continue
        score = p930.inner_cv_score(rule, seed, fit_rows, rows_by_index)
        if int_value(score.get("inner_false_count")) != 0:
            continue
        if int_value(score.get("inner_win_count")) < min_inner_wins:
            continue
        if cost_first:
            key = (
                full_public_cost,
                -int_value(score.get("inner_win_count")),
                -int_value(score.get("inner_recovered_positive_count")),
                int_value(rule.get("train_selected_cost_ops"), 10**12),
                len(rule.get("predicate_names") or []),
                p929.rule_name(rule),
            )
        else:
            key = (
                -int_value(score.get("inner_win_count")),
                -int_value(score.get("inner_recovered_positive_count")),
                full_public_cost,
                int_value(rule.get("train_selected_cost_ops"), 10**12),
                len(rule.get("predicate_names") or []),
                p929.rule_name(rule),
            )
        if best_key is None or key < best_key:
            best_key = key
            best_rule = rule
            best_score = {
                **score,
                "cost_first": cost_first,
                "full_public_cost_ops": full_public_cost,
                "margin_ops": margin,
                "min_inner_wins": min_inner_wins,
                "rule_family": p929.rule_family(rule),
                "seed_public_cost_ops": seed_public_cost,
                "selection_key": list(key),
            }
    if best_rule:
        return [seed, best_rule], best_score
    return selected, {
        "cost_first": cost_first,
        "full_public_cost_ops": seed_public_cost,
        "inner_false_count": 0,
        "inner_recovered_positive_count": 0,
        "inner_selected_count": 0,
        "inner_win_count": 0,
        "inner_winning_windows": [],
        "margin_ops": margin,
        "min_inner_wins": min_inner_wins,
        "rule_family": None,
        "seed_public_cost_ops": seed_public_cost,
        "selection_key": None,
    }


def summarize(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return p930.summarize(items, target_rank, p919_cost)


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    seed = summaries.get("seed_only_control") or {}
    seed_rec = int_value(seed.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if name in {"seed_only_control", "oracle_cost_ceiling_upper_bound"}:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P931_MARGIN_SELECTOR_IMPROVES_SECOND_HOLDOUT_WITH_COST_SAFETY"
    if any(
        name not in {"seed_only_control", "oracle_cost_ceiling_upper_bound"}
        and int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P931_MARGIN_SELECTOR_GAINS_SUPPORT_BUT_FAILS_FULL_GATE"
    return "NEGATIVE_RESULT_P931_MARGIN_SELECTOR_ABSTAINS_TO_SEED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p930_payload = load_json(args.p930_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    rows_by_index = {int_value(row.get("index")): row for row in public_rows}
    p903_indices = p928.p903_c19_indices(public_rows)
    p903_blind_rows = p928.rows_excluding_indices(public_rows, p903_indices)
    p903_blind_records = p928.records_excluding_indices(records, p903_indices)
    windows = sorted(
        {
            p923.source_window(row)
            for row in p903_blind_rows
            if row.get("partition") != VALIDATION_PARTITION and p923.source_window(row) != "unknown"
        }
    )
    p919_report = p915.policy_report(
        "p919_best_policy_recomputed",
        p919.policy_records(
            records,
            c19_extra_mode="gap_eq5",
            c19_extra_cost_cap=180,
            c90_gap_mode="gap_le3",
            c90_cost_cap=128,
        ),
        "P919 positive control.",
        target_rank,
        True,
    )
    p919_cost = int_value(p919_report.get("charged_candidate_cost_ops"))
    companion_report = p922.full_policy_report("p931_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value(p922.compact_policy(companion_report).get("charged_candidate_cost_ops"))
    fallback = p926.fallback_map()[p929.P928_BEST_STRATEGY]
    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    for strategy in MARGIN_STRATEGIES:
        strategy_items[str(strategy["name"])] = []

    for window in windows:
        fit_rows = [row for row in p903_blind_rows if p923.source_window(row) != window]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        context = p926.fit_context(fit_rows)
        atoms_by_name = context.get("atoms_by_name") or {}
        _source, seed_rule = p926.choose_rule(context, fallback)
        strategy_rules: dict[str, tuple[list[dict[str, Any]], dict[str, Any]]] = {
            "seed_only_control": ([seed_rule] if seed_rule else [], {"selector": "p928_seed"}),
            "oracle_cost_ceiling_upper_bound": (
                p929.oracle_cost_ceiling_ensemble(
                    context,
                    heldout_rows,
                    public_rows,
                    atoms_by_name,
                    rows_by_index,
                    companion_cost,
                    p919_cost,
                    seed_rule,
                ),
                {"selector": "heldout_label_oracle"},
            ),
        }
        for strategy in MARGIN_STRATEGIES:
            rules, metadata = choose_margin_rule(
                context,
                fit_rows,
                public_rows,
                atoms_by_name,
                rows_by_index,
                companion_cost,
                p919_cost,
                seed_rule,
                int_value(strategy["margin"]),
                int_value(strategy["min_inner_wins"]),
                bool(strategy["cost_first"]),
            )
            strategy_rules[str(strategy["name"])] = (rules, {"selector": "margin_inner_cv", **metadata})
        for name, (rules, metadata) in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(fit_rows),
                    "heldout_source_window": window,
                    "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": p929.score_ensemble(
                        f"p931_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": p929.score_ensemble(
                        f"p931_{name}_p903",
                        rules,
                        public_rows,
                        atoms_by_name,
                        records,
                        target_rank,
                        p919_cost,
                    ),
                    "rule_families": [p929.rule_family(rule) for rule in rules],
                    "rule_names": [p929.rule_name(rule) for rule in rules],
                    "selector_metadata": metadata,
                }
            )
    summaries = {name: summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p930_source": str(args.p930_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous strategies remove P903 and the outer heldout source from support labels during rule choice.",
            "PUBLIC-COST-GATE: autonomous margin strategies may use label-free public selected-row costs, including outer source rows.",
            "ORACLE-CONTROL: the oracle upper bound uses outer heldout support labels and is not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p931_margin_aware_abstaining_selector",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "margin_strategies": list(MARGIN_STRATEGIES),
            "p903_c19_indices": sorted(p903_indices),
            "p930_claim": p930_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p919": p922.compact_policy(p919_report),
        },
        "schema": SCHEMA,
        "summary": {
            "second_holdout": strategy_items,
            "strategy_summaries": summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p930-source", type=Path, default=P930_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in ["seed_only_control", "margin0_min2", "margin64_min2", "margin0_min4", "cost_first_margin0_min2", "oracle_cost_ceiling_upper_bound"]:
        summary = summaries.get(name) or {}
        parts.append(
            "{name}:rec={rec}/{pos},false={false},p903_pass={passes}/{total}".format(
                name=name,
                rec=summary.get("heldout_recovered_positive_count"),
                pos=summary.get("heldout_positive_count"),
                false=summary.get("heldout_false_selected_count"),
                passes=summary.get("p903_pass_count"),
                total=summary.get("source_window_count"),
            )
        )
    print(
        "claim={claim} {parts} fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            parts=" | ".join(parts),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
