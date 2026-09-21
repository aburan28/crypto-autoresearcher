#!/usr/bin/env python3
"""P926 fallback audit for P925 gap/source-index source-window failures."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p922_support_class_cost_audit as p922
import low_term_total2_p923_train_only_support_class_redteam as p923
import low_term_total2_p924_train_only_objective_audit as p924
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p926_gap_source_fallback_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p926_gap_source_fallback_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P925_SOURCE = STATE_DIR / "low_term_total2_p925_gap_source_tiebreaker_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p926_gap_source_fallback_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION


FallbackFn = Callable[[list[dict[str, Any]]], dict[str, Any]]


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


def fit_context(fit_rows: list[dict[str, Any]]) -> dict[str, Any]:
    raw_rules, atoms_by_name = p923.fit_rules(fit_rows)
    rules = [p924.enrich_rule(rule, fit_rows) for rule in raw_rules]
    best_key, tie_class = p924.choose_tie_class(rules, p924.objective_map()[p925.PRIMARY_OBJECTIVE])
    primary_rule = p925.select_gap5_source_index(tie_class)
    return {
        "atoms_by_name": atoms_by_name,
        "best_key": list(best_key) if best_key is not None else None,
        "primary_rule": primary_rule,
        "rules": rules,
        "tie_class": tie_class,
    }


def gap_source_candidates(rules: list[dict[str, Any]], min_tp: int = 1) -> list[dict[str, Any]]:
    return [
        rule
        for rule in rules
        if int_value(rule.get("train_true_positive_count")) >= min_tp
        and p925.source_index_atoms(rule)
        and any(value >= 5 for value in p925.gap_le_values(rule))
    ]


def min_gap(rule: dict[str, Any]) -> int:
    return min(value for value in p925.gap_le_values(rule) if value >= 5)


def min_source_mod(rule: dict[str, Any]) -> int:
    return min(mod for mod, _rem in p925.source_index_atoms(rule))


def select_min_cost(min_tp: int) -> FallbackFn:
    def select(rules: list[dict[str, Any]]) -> dict[str, Any]:
        candidates = gap_source_candidates(rules, min_tp)
        if not candidates:
            return {}
        return min(
            candidates,
            key=lambda rule: (
                int_value(rule.get("train_selected_cost_ops"), 10**12),
                -int_value(rule.get("train_true_positive_count")),
                min_gap(rule),
                min_source_mod(rule),
                p925.rule_name(rule),
            ),
        )

    return select


def select_min_gap(rules: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = gap_source_candidates(rules, 1)
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            min_gap(rule),
            int_value(rule.get("train_selected_cost_ops"), 10**12),
            -int_value(rule.get("train_true_positive_count")),
            min_source_mod(rule),
            p925.rule_name(rule),
        ),
    )


def select_min_mod(rules: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = gap_source_candidates(rules, 1)
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            min_source_mod(rule),
            min_gap(rule),
            int_value(rule.get("train_selected_cost_ops"), 10**12),
            -int_value(rule.get("train_true_positive_count")),
            p925.rule_name(rule),
        ),
    )


def fallback_map() -> dict[str, FallbackFn]:
    return {
        "fallback_global_gap5_source_min_cost_tp1": select_min_cost(1),
        "fallback_global_gap5_source_min_cost_tp2": select_min_cost(2),
        "fallback_global_gap5_source_min_gap": select_min_gap,
        "fallback_global_gap5_source_min_mod": select_min_mod,
    }


def choose_rule(context: dict[str, Any], fallback: FallbackFn) -> tuple[str, dict[str, Any]]:
    primary = context.get("primary_rule") or {}
    if primary:
        return "primary", primary
    rule = fallback(context.get("rules") or [])
    return "fallback", rule


def score_rule(
    name: str,
    rule: dict[str, Any],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    if not rule:
        return {}
    scored = p924.score_candidate(
        rule,
        public_rows,
        atoms_by_name,
        records,
        target_rank,
        p919_cost,
        f"p926_{name}_policy",
    )
    full = scored.get("full_policy") or {}
    scored["cost_saved_fraction_vs_p919"] = ratio(
        p919_cost - int_value(full.get("charged_candidate_cost_ops"), 10**12),
        p919_cost,
    )
    return scored


def compact_score(scored: dict[str, Any]) -> dict[str, Any]:
    return p925.compact_score(scored)


def candidate_passes(scored: dict[str, Any], target_rank: int, p919_cost: int) -> bool:
    return p924.candidate_passes(scored, target_rank, p919_cost)


def score_context(
    strategy_name: str,
    context: dict[str, Any],
    fallback: FallbackFn,
    public_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    source, rule = choose_rule(context, fallback)
    scored = score_rule(
        strategy_name,
        rule,
        public_rows,
        context.get("atoms_by_name") or {},
        records,
        target_rank,
        p919_cost,
    )
    return {
        "fit_best_key": context.get("best_key"),
        "fit_tie_class_size": len(context.get("tie_class") or []),
        "rule_source": source if rule else "none",
        "score": compact_score(scored),
        "passes": candidate_passes(scored, target_rank, p919_cost),
    }


def leave_one_source_stress(
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
    out = {name: [] for name in fallback_map()}
    for window in windows:
        fit_rows = [
            row
            for row in public_rows
            if row.get("partition") == VALIDATION_PARTITION or p923.source_window(row) != window
        ]
        context = fit_context(fit_rows)
        omitted_rows = [row for row in public_rows if p923.source_window(row) == window]
        base = {
            "omitted_indices": [row.get("index") for row in omitted_rows],
            "omitted_positive_count": sum(
                1 for row in omitted_rows if p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])
            ),
            "omitted_source_window": window,
            "primary_available": bool(context.get("primary_rule")),
        }
        for name, fallback in fallback_map().items():
            item = score_context(name, context, fallback, public_rows, records, target_rank, p919_cost)
            out[name].append({**base, **item})
    return out


def summarize_strategy(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return {
        "below_p919_count": sum(
            1
            for item in items
            if int_value((item.get("score") or {}).get("charged_candidate_cost_ops"), 10**12) < p919_cost
        ),
        "fallback_used_count": sum(1 for item in items if item.get("rule_source") == "fallback"),
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
            int_value(summary[name].get("fallback_used_count")),
            name,
        ),
    )


def determine_claim(summary: dict[str, dict[str, Any]], best_name: str) -> str:
    best = summary.get(best_name) or {}
    total = int_value(best.get("leave_one_source_count"))
    passes = int_value(best.get("pass_count"))
    preserved = int_value(best.get("primary_preserved_count"))
    fallback_used = int_value(best.get("fallback_used_count"))
    if total and passes == total and preserved + fallback_used == total:
        return "P926_GAP_SOURCE_FALLBACK_REPAIRS_ALL_SOURCE_STRESS"
    if passes > 15:
        return "P926_GAP_SOURCE_FALLBACK_IMPROVES_SOURCE_STRESS_BUT_NOT_FULLY"
    return "NEGATIVE_RESULT_P926_GAP_SOURCE_FALLBACK_DOES_NOT_IMPROVE_STRESS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p925_payload = load_json(args.p925_source)
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
    full_context = fit_context(public_rows)
    full_scores = {
        name: score_context(name, full_context, fallback, public_rows, records, target_rank, p919_cost)
        for name, fallback in fallback_map().items()
    }
    stress = leave_one_source_stress(public_rows, records, target_rank, p919_cost)
    summaries = {name: summarize_strategy(items, target_rank, p919_cost) for name, items in stress.items()}
    best_name = best_strategy(summaries)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p925_source": str(args.p925_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries, best_name),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived validation after fallback freeze.",
            "FALLBACK-REDTEAM: fallback only activates when the P925 primary rule is absent.",
            "MECHANISM-PRIOR: the gap-5/source-index family is archive-learned.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible 1160+ row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p926_gap_source_fallback_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p925_claim": p925_payload.get("claim_status"),
            "p925_stress_pass_count": ((p925_payload.get("summary") or {}).get("leave_one_source_summary") or {}).get("primary_pass_count"),
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
            "strategy_summaries": summaries,
            "strategy_stress": stress,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p925-source", type=Path, default=P925_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    best_name = (payload.get("summary") or {}).get("best_strategy")
    best = summaries.get(best_name) or {}
    print(
        "claim={claim} best={best_name} pass={passes}/{total} fallback_used={fallback_used} "
        "fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            best_name=best_name,
            passes=best.get("pass_count"),
            total=best.get("leave_one_source_count"),
            fallback_used=best.get("fallback_used_count"),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
