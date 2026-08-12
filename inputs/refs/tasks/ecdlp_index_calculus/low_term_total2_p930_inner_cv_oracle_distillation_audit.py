#!/usr/bin/env python3
"""P930 inner-CV oracle-distillation audit for P929 low-cost coverage."""

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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p930_inner_cv_oracle_distillation_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p930_inner_cv_oracle_distillation_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P929_SOURCE = STATE_DIR / "low_term_total2_p929_fit_only_support_ensemble_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p930_inner_cv_oracle_distillation_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
INNER_THRESHOLDS = (2, 3, 4, 5)


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


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p908.ratio(numerator, denominator)


def class_a_positive(row: dict[str, Any]) -> bool:
    return p929.class_a_positive(row)


def rule_name(rule: dict[str, Any] | None) -> str:
    return p929.rule_name(rule)


def fit_indices(rule: dict[str, Any] | None) -> set[int]:
    return p929.rule_indices(rule)


def row_cost(index: int, rows_by_index: dict[int, dict[str, Any]]) -> int:
    row = rows_by_index.get(index) or {}
    return int_value(row.get("charged_candidate_cost_ops"))


def c19_cost(indices: set[int], rows_by_index: dict[int, dict[str, Any]]) -> int:
    return sum(row_cost(index, rows_by_index) for index in indices if index in rows_by_index)


def fit_window_maps(fit_rows: list[dict[str, Any]]) -> tuple[dict[str, set[int]], dict[str, set[int]]]:
    by_window: dict[str, set[int]] = {}
    positive_by_window: dict[str, set[int]] = {}
    for row in fit_rows:
        window = p923.source_window(row)
        if row.get("partition") == VALIDATION_PARTITION or window == "unknown":
            continue
        index = int_value(row.get("index"))
        by_window.setdefault(window, set()).add(index)
        if class_a_positive(row):
            positive_by_window.setdefault(window, set()).add(index)
    return by_window, positive_by_window


def inner_cv_score(
    rule: dict[str, Any],
    seed: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    rows_by_index: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    by_window, positive_by_window = fit_window_maps(fit_rows)
    seed_fit = fit_indices(seed)
    rule_fit = fit_indices(rule)
    wins = 0
    recovered = 0
    false_count = 0
    selected_count = 0
    winning_windows: list[str] = []
    for window, positives in sorted(positive_by_window.items()):
        selected = (seed_fit | rule_fit) & by_window.get(window, set())
        seed_selected = seed_fit & by_window.get(window, set())
        false = [
            index
            for index in selected
            if not class_a_positive(rows_by_index.get(index) or {})
        ]
        new_recovered = (selected & positives) - (seed_selected & positives)
        false_count += len(false)
        selected_count += len(selected)
        if new_recovered and not false:
            wins += 1
            recovered += len(new_recovered)
            winning_windows.append(window)
    return {
        "inner_false_count": false_count,
        "inner_recovered_positive_count": recovered,
        "inner_selected_count": selected_count,
        "inner_win_count": wins,
        "inner_winning_windows": winning_windows,
    }


def clean_candidate_rules(context: dict[str, Any], seed: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        rule
        for rule in context.get("rules") or []
        if rule
        and rule_name(rule) != rule_name(seed)
        and int_value(rule.get("train_true_positive_count")) >= 1
        and int_value(rule.get("train_false_positive_count")) == 0
    ]


def choose_inner_cv_rule(
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
    p903_indices: set[int],
    seed: dict[str, Any],
    min_inner_wins: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    seed_fit = fit_indices(seed)
    p903_cost = c19_cost(p903_indices, rows_by_index)
    best_rule: dict[str, Any] | None = None
    best_score: dict[str, Any] = {}
    best_key: tuple[Any, ...] | None = None
    for rule in clean_candidate_rules(context, seed):
        rule_fit = fit_indices(rule)
        fit_proxy_cost = companion_cost + c19_cost(seed_fit | rule_fit, rows_by_index) + p903_cost
        if fit_proxy_cost >= p919_cost:
            continue
        score = inner_cv_score(rule, seed, fit_rows, rows_by_index)
        if int_value(score.get("inner_false_count")) != 0:
            continue
        if int_value(score.get("inner_win_count")) < min_inner_wins:
            continue
        key = (
            -int_value(score.get("inner_win_count")),
            -int_value(score.get("inner_recovered_positive_count")),
            fit_proxy_cost,
            int_value(rule.get("train_selected_cost_ops"), 10**12),
            len(rule.get("predicate_names") or []),
            rule_name(rule),
        )
        if best_key is None or key < best_key:
            best_key = key
            best_rule = rule
            best_score = {
                **score,
                "fit_proxy_cost_ops": fit_proxy_cost,
                "rule_family": p929.rule_family(rule),
                "selection_key": list(key),
            }
    if best_rule:
        return [seed, best_rule], best_score
    return ([seed] if seed else []), {
        "fit_proxy_cost_ops": companion_cost + c19_cost(seed_fit, rows_by_index) + p903_cost,
        "inner_false_count": 0,
        "inner_recovered_positive_count": 0,
        "inner_selected_count": 0,
        "inner_win_count": 0,
        "inner_winning_windows": [],
        "rule_family": None,
        "selection_key": None,
    }


def summarize(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    positive_windows = [item for item in items if int_value((item.get("heldout_support") or {}).get("positive_count")) > 0]
    return {
        "extra_rule_selected_count": sum(1 for item in items if len(item.get("rule_names") or []) > 1),
        "heldout_false_selected_count": sum(
            int_value((item.get("heldout_support") or {}).get("false_selected_count")) for item in items
        ),
        "heldout_positive_count": sum(
            int_value((item.get("heldout_support") or {}).get("positive_count")) for item in items
        ),
        "heldout_positive_window_count": len(positive_windows),
        "heldout_recovered_positive_count": sum(
            int_value((item.get("heldout_support") or {}).get("recovered_positive_count")) for item in items
        ),
        "heldout_recovered_positive_window_count": sum(
            1
            for item in positive_windows
            if int_value((item.get("heldout_support") or {}).get("recovered_positive_count")) > 0
        ),
        "no_p903_rank6_count": sum(
            1
            for item in items
            if int_value(((item.get("no_p903_score") or {}).get("score") or {}).get("total_factor_rank")) >= target_rank
        ),
        "p903_below_p919_count": sum(
            1
            for item in items
            if int_value(((item.get("p903_score") or {}).get("score") or {}).get("charged_candidate_cost_ops"), 10**12)
            < p919_cost
        ),
        "p903_pass_count": sum(1 for item in items if (item.get("p903_score") or {}).get("passes")),
        "p903_recovered_count": sum(
            1
            for item in items
            if int_value(((item.get("p903_score") or {}).get("score") or {}).get("validation_true_positive_count")) > 0
        ),
        "source_window_count": len(items),
    }


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    seed = summaries.get("seed_only_control") or {}
    seed_rec = int_value(seed.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if not name.startswith("inner_cv_min"):
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P930_INNER_CV_DISTILLS_AUTONOMOUS_COSTED_SELECTOR"
    if any(
        name.startswith("inner_cv_min")
        and int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P930_INNER_CV_GAINS_SUPPORT_BUT_FAILS_SAFETY_OR_COST"
    return "NEGATIVE_RESULT_P930_INNER_CV_COLLAPSES_TO_SEED_SUPPORT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p929_payload = load_json(args.p929_source)
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
    companion_report = p922.full_policy_report("p930_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value(p922.compact_policy(companion_report).get("charged_candidate_cost_ops"))
    fallback = p926.fallback_map()[p929.P928_BEST_STRATEGY]
    strategy_items: dict[str, list[dict[str, Any]]] = {"seed_only_control": [], "oracle_cost_ceiling_upper_bound": []}
    for threshold in INNER_THRESHOLDS:
        strategy_items[f"inner_cv_min{threshold}"] = []

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
        for threshold in INNER_THRESHOLDS:
            rules, meta = choose_inner_cv_rule(
                context,
                fit_rows,
                rows_by_index,
                companion_cost,
                p919_cost,
                p903_indices,
                seed_rule,
                threshold,
            )
            strategy_rules[f"inner_cv_min{threshold}"] = (rules, {"selector": "inner_cv", "min_inner_wins": threshold, **meta})
        for name, (rules, metadata) in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(fit_rows),
                    "heldout_source_window": window,
                    "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": p929.score_ensemble(
                        f"p930_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": p929.score_ensemble(
                        f"p930_{name}_p903",
                        rules,
                        public_rows,
                        atoms_by_name,
                        records,
                        target_rank,
                        p919_cost,
                    ),
                    "rule_families": [p929.rule_family(rule) for rule in rules],
                    "rule_names": [rule_name(rule) for rule in rules],
                    "selector_metadata": metadata,
                }
            )
    summaries = {name: summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p929_source": str(args.p929_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous strategies remove P903 and the outer heldout source before rule choice.",
            "INNER-CV-LABELS: inner source windows inside fit rows use class-A labels, but outer heldout and P903 labels are not used for autonomous choice.",
            "ORACLE-CONTROL: the oracle upper bound uses outer heldout support labels and is not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p930_inner_cv_oracle_distillation_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "inner_thresholds": list(INNER_THRESHOLDS),
            "p903_c19_indices": sorted(p903_indices),
            "p929_claim": p929_payload.get("claim_status"),
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
    parser.add_argument("--p929-source", type=Path, default=P929_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in ["seed_only_control", "inner_cv_min2", "inner_cv_min3", "inner_cv_min4", "inner_cv_min5", "oracle_cost_ceiling_upper_bound"]:
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
