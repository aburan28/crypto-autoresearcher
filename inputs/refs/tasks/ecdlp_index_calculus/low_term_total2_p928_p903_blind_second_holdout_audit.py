#!/usr/bin/env python3
"""P928 P903-blind second-holdout audit for the P927 selector."""

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
import low_term_total2_p924_train_only_objective_audit as p924
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925
import low_term_total2_p926_gap_source_fallback_audit as p926
import low_term_total2_p927_nested_source_holdout_audit as p927


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p928_p903_blind_second_holdout_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p928_p903_blind_second_holdout_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P927_SOURCE = STATE_DIR / "low_term_total2_p927_nested_source_holdout_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p928_p903_blind_second_holdout_audit.v1"
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


def p903_c19_indices(public_rows: list[dict[str, Any]]) -> set[int]:
    return {
        int_value(row.get("index"))
        for row in public_rows
        if row.get("partition") == VALIDATION_PARTITION
    }


def rows_excluding_indices(public_rows: list[dict[str, Any]], indices: set[int]) -> list[dict[str, Any]]:
    return [row for row in public_rows if int_value(row.get("index")) not in indices]


def records_excluding_indices(records: list[dict[str, Any]], indices: set[int]) -> list[dict[str, Any]]:
    return [record for record in records if int_value(record.get("index")) not in indices]


def class_a_positive(row: dict[str, Any]) -> bool:
    return p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])


def selected_rows(rule: dict[str, Any], rows: list[dict[str, Any]], atoms_by_name: dict[str, Any]) -> list[dict[str, Any]]:
    if not rule:
        return []
    return p922.selected_by_rule(rows, list(p923.rule_key(rule)), atoms_by_name)


def heldout_support_report(rule: dict[str, Any], rows: list[dict[str, Any]], atoms_by_name: dict[str, Any]) -> dict[str, Any]:
    selected = selected_rows(rule, rows, atoms_by_name)
    positive = [row for row in rows if class_a_positive(row)]
    recovered = [row for row in selected if class_a_positive(row)]
    false = [row for row in selected if not class_a_positive(row)]
    return {
        "false_selected_count": len(false),
        "false_selected_indices": [row.get("index") for row in false],
        "positive_count": len(positive),
        "positive_indices": [row.get("index") for row in positive],
        "recall": ratio(len(recovered), len(positive)) if positive else None,
        "recovered_positive_count": len(recovered),
        "recovered_positive_indices": [row.get("index") for row in recovered],
        "selected_count": len(selected),
        "selected_indices": [row.get("index") for row in selected],
    }


def score_context(
    name: str,
    context: dict[str, Any],
    fallback: Any,
    score_public_rows: list[dict[str, Any]],
    score_records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    source, rule = p926.choose_rule(context, fallback)
    scored = p927.score_rule_nested(
        name,
        rule,
        score_public_rows,
        context.get("atoms_by_name") or {},
        score_records,
        target_rank,
        p919_cost,
    )
    return {
        "passes": p927.candidate_passes(scored, target_rank, p919_cost),
        "rule_source": source if rule else "none",
        "score": p927.compact_score(scored),
    }


def second_holdout_audit(
    public_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
    p903_indices: set[int],
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
    p903_blind_rows = rows_excluding_indices(public_rows, p903_indices)
    p903_blind_records = records_excluding_indices(records, p903_indices)
    for window in windows:
        fit_rows = [
            row
            for row in p903_blind_rows
            if p923.source_window(row) != window
        ]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        score_rows_without_p903 = p903_blind_rows
        score_records_without_p903 = p903_blind_records
        score_rows_with_p903 = public_rows
        score_records_with_p903 = records
        context = p926.fit_context(fit_rows)
        base = {
            "fit_row_count": len(fit_rows),
            "heldout_source_window": window,
            "heldout_support_positive_count": sum(1 for row in heldout_rows if class_a_positive(row)),
            "heldout_support_positive_indices": [
                row.get("index") for row in heldout_rows if class_a_positive(row)
            ],
        }
        for name, fallback in p926.fallback_map().items():
            source, rule = p926.choose_rule(context, fallback)
            support = heldout_support_report(rule, heldout_rows, context.get("atoms_by_name") or {})
            p903_score = score_context(
                f"p928_{name}_p903_score",
                context,
                fallback,
                score_rows_with_p903,
                score_records_with_p903,
                target_rank,
                p919_cost,
            )
            no_p903_score = score_context(
                f"p928_{name}_no_p903_score",
                context,
                fallback,
                score_rows_without_p903,
                score_records_without_p903,
                target_rank,
                p919_cost,
            )
            out[name].append(
                {
                    **base,
                    "heldout_support": support,
                    "no_p903_score": no_p903_score,
                    "p903_score": p903_score,
                    "rule_name": rule.get("name") if rule else None,
                    "rule_predicate_names": rule.get("predicate_names") if rule else None,
                    "rule_source": source if rule else "none",
                }
            )
    return out


def summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    positive_windows = [
        item for item in items if int_value(item.get("heldout_support_positive_count")) > 0
    ]
    return {
        "heldout_false_selected_count": sum(
            int_value((item.get("heldout_support") or {}).get("false_selected_count")) for item in items
        ),
        "heldout_positive_count": sum(int_value(item.get("heldout_support_positive_count")) for item in items),
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
            if int_value(((item.get("no_p903_score") or {}).get("score") or {}).get("total_factor_rank")) >= 6
        ),
        "p903_pass_count": sum(1 for item in items if (item.get("p903_score") or {}).get("passes")),
        "p903_recovered_count": sum(
            1
            for item in items
            if int_value(((item.get("p903_score") or {}).get("score") or {}).get("validation_true_positive_count")) > 0
        ),
        "source_window_count": len(items),
    }


def best_strategy(summaries: dict[str, dict[str, Any]]) -> str:
    return min(
        summaries,
        key=lambda name: (
            -int_value(summaries[name].get("p903_pass_count")),
            -int_value(summaries[name].get("heldout_recovered_positive_count")),
            int_value(summaries[name].get("heldout_false_selected_count")),
            name,
        ),
    )


def determine_claim(best_summary: dict[str, Any]) -> str:
    total = int_value(best_summary.get("source_window_count"))
    p903_pass = int_value(best_summary.get("p903_pass_count"))
    positives = int_value(best_summary.get("heldout_positive_count"))
    recovered = int_value(best_summary.get("heldout_recovered_positive_count"))
    false_count = int_value(best_summary.get("heldout_false_selected_count"))
    if total and p903_pass == total and positives and recovered == positives and false_count == 0:
        return "P928_P903_BLIND_SELECTOR_GENERALIZES_TO_SECOND_HOLDOUT"
    if total and p903_pass == total and recovered > 0:
        return "P928_P903_BLIND_SELECTOR_RECOVERS_P903_WITH_PARTIAL_SECOND_HOLDOUT"
    if total and p903_pass == total:
        return "P928_P903_BLIND_SELECTOR_RECOVERS_P903_ONLY"
    return "NEGATIVE_RESULT_P928_P903_BLIND_SELECTOR_FAILS_P903_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p927_payload = load_json(args.p927_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    p903_indices = p903_c19_indices(public_rows)
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
    audit = second_holdout_audit(public_rows, records, p903_indices, target_rank, p919_cost)
    summaries = {name: summarize(items) for name, items in audit.items()}
    best_name = best_strategy(summaries)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p927_source": str(args.p927_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries.get(best_name) or {}),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived P903 after P903-blind rule-family choice.",
            "SECOND-HOLDOUT-REDTEAM: non-P903 source windows are used as independent support-score windows.",
            "P903-RANK-DEPENDENCY: no-P903 rank is tracked separately from P903-restored rank.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible 1160+ row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p928_p903_blind_second_holdout_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p903_c19_indices": sorted(p903_indices),
            "p927_claim": p927_payload.get("claim_status"),
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
            "second_holdout": audit,
            "strategy_summaries": summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p927-source", type=Path, default=P927_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    best = (payload.get("summary") or {}).get("best_strategy")
    best_summary = summaries.get(best) or {}
    print(
        "claim={claim} best={best} p903_pass={p903_pass}/{windows} "
        "heldout_recovered={rec}/{pos} no_p903_rank6={no_rank6} fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            best=best,
            p903_pass=best_summary.get("p903_pass_count"),
            windows=best_summary.get("source_window_count"),
            rec=best_summary.get("heldout_recovered_positive_count"),
            pos=best_summary.get("heldout_positive_count"),
            no_rank6=best_summary.get("no_p903_rank6_count"),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
