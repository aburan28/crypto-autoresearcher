#!/usr/bin/env python3
"""P927 nested source-holdout audit for the P926 fallback."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p922_support_class_cost_audit as p922
import low_term_total2_p923_train_only_support_class_redteam as p923
import low_term_total2_p924_train_only_objective_audit as p924
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925
import low_term_total2_p926_gap_source_fallback_audit as p926


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p927_nested_source_holdout_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p927_nested_source_holdout_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P926_SOURCE = STATE_DIR / "low_term_total2_p926_gap_source_fallback_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p927_nested_source_holdout_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION


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


def record_source_window(record: dict[str, Any]) -> str:
    row = record.get("row") or {}
    source_path = row.get("source_path")
    if source_path:
        return p923.source_window_from_path(source_path)
    return "unknown"


def records_excluding_window(records: list[dict[str, Any]], window: str) -> list[dict[str, Any]]:
    return [record for record in records if record_source_window(record) != window]


def public_rows_excluding_window(public_rows: list[dict[str, Any]], window: str) -> list[dict[str, Any]]:
    return [row for row in public_rows if p923.source_window(row) != window]


def score_rule_nested(
    name: str,
    rule: dict[str, Any],
    score_public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    score_records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    if not rule:
        return {}
    predicate_names = p923.rule_key(rule)
    train_rows = [row for row in score_public_rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in score_public_rows if row.get("partition") == VALIDATION_PARTITION]
    support_report = p922.support_rule_report(
        CLASS_A,
        list(predicate_names),
        score_public_rows,
        train_rows,
        validation_rows,
        atoms_by_name,
    )
    selected_indices = {int_value(index) for index in support_report.get("all_selected_indices") or []}
    full_report = p922.full_policy_report(name, score_records, selected_indices, target_rank)
    full_compact = p922.compact_policy(full_report)
    cost = int_value(full_compact.get("charged_candidate_cost_ops"), 10**12)
    return {
        "cost_saved_fraction_vs_p919": ratio(p919_cost - cost, p919_cost),
        "full_policy": full_compact,
        "rule": support_report,
        "selected_c19_indices": sorted(selected_indices),
    }


def compact_score(scored: dict[str, Any]) -> dict[str, Any]:
    return p925.compact_score(scored)


def candidate_passes(scored: dict[str, Any], target_rank: int, p919_cost: int) -> bool:
    return p924.candidate_passes(scored, target_rank, p919_cost)


def score_context_nested(
    strategy_name: str,
    context: dict[str, Any],
    fallback: Any,
    score_public_rows: list[dict[str, Any]],
    score_records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    source, rule = p926.choose_rule(context, fallback)
    scored = score_rule_nested(
        strategy_name,
        rule,
        score_public_rows,
        context.get("atoms_by_name") or {},
        score_records,
        target_rank,
        p919_cost,
    )
    return {
        "fit_best_key": context.get("best_key"),
        "fit_tie_class_size": len(context.get("tie_class") or []),
        "passes": candidate_passes(scored, target_rank, p919_cost),
        "rule_source": source if rule else "none",
        "score": compact_score(scored),
    }


def p919_restricted_control(records: list[dict[str, Any]], target_rank: int, window: str) -> dict[str, Any]:
    restricted = records_excluding_window(records, window)
    report = p915.policy_report(
        f"p927_p919_restricted_without_{window}",
        p919.policy_records(
            restricted,
            c19_extra_mode="gap_eq5",
            c19_extra_cost_cap=180,
            c90_gap_mode="gap_le3",
            c90_cost_cap=128,
        ),
        "P927 restricted P919 control with the source window removed.",
        target_rank,
        True,
    )
    return p922.compact_policy(report)


def nested_stress(
    public_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, list[dict[str, Any]]]:
    windows = sorted(
        {
            p923.source_window(row)
            for row in public_rows
            if row.get("partition") != VALIDATION_PARTITION and p923.source_window(row) != "unknown"
        }
    )
    out = {name: [] for name in p926.fallback_map()}
    for window in windows:
        fit_rows = public_rows_excluding_window(public_rows, window)
        score_rows = public_rows_excluding_window(public_rows, window)
        score_records = records_excluding_window(records, window)
        context = p926.fit_context(fit_rows)
        omitted_rows = [row for row in public_rows if p923.source_window(row) == window]
        omitted_indices = [int_value(row.get("index")) for row in omitted_rows]
        base = {
            "omitted_indices": omitted_indices,
            "omitted_positive_count": sum(
                1 for row in omitted_rows if p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])
            ),
            "omitted_source_window": window,
            "p919_restricted_control": p919_restricted_control(records, target_rank, window),
            "primary_available": bool(context.get("primary_rule")),
        }
        for name, fallback in p926.fallback_map().items():
            item = score_context_nested(
                name,
                context,
                fallback,
                score_rows,
                score_records,
                target_rank,
                p919_cost,
            )
            selected = set(int_value(index) for index in ((item.get("score") or {}).get("selected_c19_indices") or []))
            item["heldout_row_selected_count"] = len(selected.intersection(omitted_indices))
            out[name].append({**base, **item})
    return out


def summarize_strategy(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return {
        "below_restricted_p919_count": sum(
            1
            for item in items
            if int_value((item.get("score") or {}).get("charged_candidate_cost_ops"), 10**12)
            < int_value((item.get("p919_restricted_control") or {}).get("charged_candidate_cost_ops"), 10**12)
        ),
        "below_p919_count": sum(
            1
            for item in items
            if int_value((item.get("score") or {}).get("charged_candidate_cost_ops"), 10**12) < p919_cost
        ),
        "fallback_used_count": sum(1 for item in items if item.get("rule_source") == "fallback"),
        "heldout_row_selected_count": sum(int_value(item.get("heldout_row_selected_count")) for item in items),
        "leave_one_source_count": len(items),
        "pass_count": sum(1 for item in items if item.get("passes")),
        "primary_preserved_count": sum(
            1 for item in items if item.get("primary_available") and item.get("rule_source") == "primary"
        ),
        "rank_preserving_count": sum(
            1 for item in items if int_value((item.get("score") or {}).get("total_factor_rank")) >= target_rank
        ),
        "validation_recovered_count": sum(
            1
            for item in items
            if int_value((item.get("score") or {}).get("validation_true_positive_count")) > 0
        ),
    }


def best_strategy(summary: dict[str, dict[str, Any]]) -> str:
    return min(
        summary,
        key=lambda name: (
            -int_value(summary[name].get("pass_count")),
            int_value(summary[name].get("heldout_row_selected_count")),
            int_value(summary[name].get("fallback_used_count")),
            name,
        ),
    )


def determine_claim(summary: dict[str, dict[str, Any]], best_name: str) -> str:
    best = summary.get(best_name) or {}
    total = int_value(best.get("leave_one_source_count"))
    passes = int_value(best.get("pass_count"))
    heldout_selected = int_value(best.get("heldout_row_selected_count"))
    if total and passes == total and heldout_selected == 0:
        return "P927_NESTED_SOURCE_HOLDOUT_STABLE_SELECTOR"
    if passes > 0:
        return "NEGATIVE_RESULT_P927_P926_FALLBACK_FAILS_FULL_NESTED_HOLDOUT"
    return "NEGATIVE_RESULT_P927_P926_FALLBACK_HAS_NO_NESTED_HOLDOUT_WINS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p926_payload = load_json(args.p926_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
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
    full_context = p926.fit_context(public_rows)
    full_scores = {
        name: p926.score_context(name, full_context, fallback, public_rows, records, target_rank, p919_cost)
        for name, fallback in p926.fallback_map().items()
    }
    stress = nested_stress(public_rows, records, target_rank, p919_cost)
    summaries = {name: summarize_strategy(items, target_rank, p919_cost) for name, items in stress.items()}
    best_name = best_strategy(summaries)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p926_source": str(args.p926_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries, best_name),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived validation after nested source holdout.",
            "NESTED-HOLDOUT-REDTEAM: held-out source rows are removed from c19 and companion rank supply.",
            "MECHANISM-PRIOR: the gap-5/source-index family is archive-learned.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible 1160+ row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p927_nested_source_holdout_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p926_claim": p926_payload.get("claim_status"),
            "p926_best_strategy": ((p926_payload.get("summary") or {}).get("best_strategy")),
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
            "best_strategy": best_name,
            "full_archive_scores": full_scores,
            "nested_strategy_summaries": summaries,
            "nested_strategy_stress": stress,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p926-source", type=Path, default=P926_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("nested_strategy_summaries") or {}
    best_name = (payload.get("summary") or {}).get("best_strategy")
    best = summaries.get(best_name) or {}
    print(
        "claim={claim} best={best_name} nested_pass={passes}/{total} heldout_selected={heldout_selected} "
        "fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            best_name=best_name,
            passes=best.get("pass_count"),
            total=best.get("leave_one_source_count"),
            heldout_selected=best.get("heldout_row_selected_count"),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
