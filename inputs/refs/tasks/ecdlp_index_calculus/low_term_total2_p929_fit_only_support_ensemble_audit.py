#!/usr/bin/env python3
"""P929 fit-only support ensemble audit for the P928 second-holdout misses."""

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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p929_fit_only_support_ensemble_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p929_fit_only_support_ensemble_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P928_SOURCE = STATE_DIR / "low_term_total2_p928_p903_blind_second_holdout_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p929_fit_only_support_ensemble_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
P928_BEST_STRATEGY = "fallback_global_gap5_source_min_cost_tp1"
STRICT_SUPPORT_FAMILIES = {"gap_source", "gap_saltmax5", "cost_saltsum", "saltmin"}


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


def rule_name(rule: dict[str, Any] | None) -> str:
    return str((rule or {}).get("name") or "")


def rule_indices(rule: dict[str, Any] | None) -> set[int]:
    return {int_value(index) for index in (rule or {}).get("all_selected_indices") or []}


def class_a_positive(row: dict[str, Any]) -> bool:
    return p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])


def rule_family(rule: dict[str, Any]) -> str:
    predicate_text = " ".join(str(name) for name in rule.get("predicate_names") or [])
    if "source_index_mod" in predicate_text and "gap_le_" in predicate_text:
        return "gap_source"
    if "salt_max_mod5_eq_1" in predicate_text and "gap_le_" in predicate_text:
        return "gap_saltmax5"
    if "cost_ge_" in predicate_text and "salt_sum_mod" in predicate_text:
        return "cost_saltsum"
    if "salt_min_mod" in predicate_text:
        return "saltmin"
    if "ops_eq_" in predicate_text:
        return "ops_eq"
    if "cost_" in predicate_text and "salt_" in predicate_text:
        return "cost_salt"
    if "salt_" in predicate_text and "source_index_mod" in predicate_text:
        return "salt_source"
    return "other"


def selected_by_rule(rule: dict[str, Any] | None, rows: list[dict[str, Any]], atoms_by_name: dict[str, Any]) -> list[dict[str, Any]]:
    if not rule:
        return []
    return p922.selected_by_rule(rows, list(p923.rule_key(rule)), atoms_by_name)


def selected_indices_for_rules(
    rules: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
) -> set[int]:
    selected: set[int] = set()
    for rule in rules:
        selected.update(int_value(row.get("index")) for row in selected_by_rule(rule, rows, atoms_by_name))
    return selected


def support_report(
    rules: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
) -> dict[str, Any]:
    selected_indices = selected_indices_for_rules(rules, rows, atoms_by_name)
    selected = [row for row in rows if int_value(row.get("index")) in selected_indices]
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


def score_ensemble(
    name: str,
    rules: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    selected_indices = selected_indices_for_rules(rules, public_rows, atoms_by_name)
    full_report = p922.full_policy_report(name, records, selected_indices, target_rank)
    full = p922.compact_policy(full_report)
    train_rows = [row for row in public_rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in public_rows if row.get("partition") == VALIDATION_PARTITION]
    train_selected = [row for row in train_rows if int_value(row.get("index")) in selected_indices]
    validation_selected = [row for row in validation_rows if int_value(row.get("index")) in selected_indices]
    cost = int_value(full.get("charged_candidate_cost_ops"), 10**12)
    compact = {
        "charged_candidate_cost_ops": full.get("charged_candidate_cost_ops"),
        "cost_saved_fraction_vs_p919": ratio(p919_cost - cost, p919_cost),
        "false_selected_count": full.get("false_selected_count"),
        "rule_names": [rule_name(rule) for rule in rules],
        "selected_c19_indices": sorted(selected_indices),
        "target_preserving": full.get("target_preserving"),
        "total_factor_rank": full.get("total_factor_rank"),
        "train_true_positive_count": sum(1 for row in train_selected if class_a_positive(row)),
        "validation_selected_indices": [row.get("index") for row in validation_selected],
        "validation_true_positive_count": sum(1 for row in validation_selected if class_a_positive(row)),
    }
    return {
        "passes": (
            int_value(compact.get("validation_true_positive_count")) > 0
            and int_value(compact.get("false_selected_count")) == 0
            and int_value(compact.get("total_factor_rank")) >= target_rank
            and cost < p919_cost
        ),
        "score": compact,
    }


def clean_rules(context: dict[str, Any], min_tp: int = 1) -> list[dict[str, Any]]:
    return [
        rule
        for rule in context.get("rules") or []
        if int_value(rule.get("train_true_positive_count")) >= min_tp
        and int_value(rule.get("train_false_positive_count")) == 0
    ]


def greedy_support_ensemble(
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    seed: dict[str, Any],
    max_rules: int = 2,
) -> list[dict[str, Any]]:
    selected = [seed] if seed else []
    covered = set().union(*(rule_indices(rule) for rule in selected)) if selected else set()
    fit_positive = {int_value(row.get("index")) for row in fit_rows if class_a_positive(row)}
    while len(selected) < max_rules:
        best_rule: dict[str, Any] | None = None
        best_key: tuple[Any, ...] | None = None
        selected_names = {rule_name(rule) for rule in selected}
        for rule in clean_rules(context, min_tp=4):
            if rule_name(rule) in selected_names:
                continue
            if int_value(rule.get("train_positive_source_window_count")) < 4:
                continue
            if rule_family(rule) not in STRICT_SUPPORT_FAMILIES:
                continue
            new_fit = (rule_indices(rule) & fit_positive) - covered
            if not new_fit:
                continue
            key = (
                -len(new_fit),
                int_value(rule.get("train_selected_cost_ops"), 10**12),
                -int_value(rule.get("train_positive_source_window_count")),
                -int_value(rule.get("train_true_positive_count")),
                len(rule.get("predicate_names") or []),
                rule_name(rule),
            )
            if best_key is None or key < best_key:
                best_key = key
                best_rule = rule
        if not best_rule:
            break
        selected.append(best_rule)
        covered.update(rule_indices(best_rule))
    return selected


def cost_proxy_for_indices(
    selected_indices: set[int],
    companion_cost: int,
    rows_by_index: dict[int, dict[str, Any]],
) -> int:
    return companion_cost + sum(
        int_value(rows_by_index[index].get("charged_candidate_cost_ops"))
        for index in selected_indices
        if index in rows_by_index
    )


def train_cost_ceiling_ensemble(
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    p903_blind_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
    seed: dict[str, Any],
) -> list[dict[str, Any]]:
    selected = [seed] if seed else []
    seed_blind = selected_indices_for_rules(selected, p903_blind_rows, atoms_by_name)
    fit_positive = {int_value(row.get("index")) for row in fit_rows if class_a_positive(row)}
    covered = set().union(*(rule_indices(rule) for rule in selected)) if selected else set()
    best_rule: dict[str, Any] | None = None
    best_key: tuple[Any, ...] | None = None
    for rule in clean_rules(context, min_tp=1):
        if rule_name(rule) in {rule_name(item) for item in selected}:
            continue
        candidate_indices = seed_blind | selected_indices_for_rules([rule], p903_blind_rows, atoms_by_name)
        proxy_cost = cost_proxy_for_indices(candidate_indices, companion_cost, rows_by_index)
        if proxy_cost >= p919_cost:
            continue
        new_fit = (rule_indices(rule) & fit_positive) - covered
        if not new_fit:
            continue
        key = (
            -len(new_fit),
            proxy_cost,
            -int_value(rule.get("train_positive_source_window_count")),
            -int_value(rule.get("train_true_positive_count")),
            len(rule.get("predicate_names") or []),
            rule_name(rule),
        )
        if best_key is None or key < best_key:
            best_key = key
            best_rule = rule
    if best_rule:
        selected.append(best_rule)
    return selected


def oracle_cost_ceiling_ensemble(
    context: dict[str, Any],
    heldout_rows: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
    seed: dict[str, Any],
) -> list[dict[str, Any]]:
    selected = [seed] if seed else []
    seed_public = selected_indices_for_rules(selected, public_rows, atoms_by_name)
    heldout_positive = {int_value(row.get("index")) for row in heldout_rows if class_a_positive(row)}
    seed_heldout = selected_indices_for_rules(selected, heldout_rows, atoms_by_name)
    best_rule: dict[str, Any] | None = None
    best_key: tuple[Any, ...] | None = None
    for rule in clean_rules(context, min_tp=1):
        if rule_name(rule) in {rule_name(item) for item in selected}:
            continue
        candidate_public = seed_public | selected_indices_for_rules([rule], public_rows, atoms_by_name)
        proxy_cost = cost_proxy_for_indices(candidate_public, companion_cost, rows_by_index)
        if proxy_cost >= p919_cost:
            continue
        candidate_heldout = seed_heldout | selected_indices_for_rules([rule], heldout_rows, atoms_by_name)
        false = [
            row
            for row in heldout_rows
            if int_value(row.get("index")) in candidate_heldout and not class_a_positive(row)
        ]
        if false:
            continue
        recovered = candidate_heldout & heldout_positive
        new_recovered = recovered - (seed_heldout & heldout_positive)
        if not new_recovered:
            continue
        key = (
            -len(recovered),
            proxy_cost,
            -int_value(rule.get("train_true_positive_count")),
            len(rule.get("predicate_names") or []),
            rule_name(rule),
        )
        if best_key is None or key < best_key:
            best_key = key
            best_rule = rule
    if best_rule:
        selected.append(best_rule)
    return selected


def summarize(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    positive_windows = [item for item in items if int_value((item.get("heldout_support") or {}).get("positive_count")) > 0]
    return {
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
    support = summaries.get("fit_only_support_k2_strict_family") or {}
    costed = summaries.get("fit_only_train_cost_ceiling") or {}
    if (
        int_value(costed.get("p903_pass_count")) == int_value(costed.get("source_window_count"))
        and int_value(costed.get("heldout_recovered_positive_count")) > int_value(seed.get("heldout_recovered_positive_count"))
        and int_value(costed.get("heldout_false_selected_count")) == 0
    ):
        return "P929_FIT_ONLY_COSTED_ENSEMBLE_IMPROVES_SECOND_HOLDOUT"
    if (
        int_value(support.get("heldout_recovered_positive_count")) > int_value(seed.get("heldout_recovered_positive_count"))
        and int_value(support.get("heldout_false_selected_count")) == 0
    ):
        return "P929_FIT_ONLY_SUPPORT_ENSEMBLE_IMPROVES_RECALL_BUT_FAILS_COST"
    return "NEGATIVE_RESULT_P929_NO_AUTONOMOUS_SECOND_HOLDOUT_SUPPORT_GAIN"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p928_payload = load_json(args.p928_source)
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
    companion_report = p922.full_policy_report("p929_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value((p922.compact_policy(companion_report)).get("charged_candidate_cost_ops"))
    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": [],
        "fit_only_support_k2_strict_family": [],
        "fit_only_train_cost_ceiling": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    fallback = p926.fallback_map()[P928_BEST_STRATEGY]
    for window in windows:
        fit_rows = [row for row in p903_blind_rows if p923.source_window(row) != window]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        context = p926.fit_context(fit_rows)
        atoms_by_name = context.get("atoms_by_name") or {}
        _source, seed_rule = p926.choose_rule(context, fallback)
        strategy_rules = {
            "seed_only_control": [seed_rule] if seed_rule else [],
            "fit_only_support_k2_strict_family": greedy_support_ensemble(context, fit_rows, seed_rule, 2),
            "fit_only_train_cost_ceiling": train_cost_ceiling_ensemble(
                context,
                fit_rows,
                p903_blind_rows,
                atoms_by_name,
                rows_by_index,
                companion_cost,
                p919_cost,
                seed_rule,
            ),
            "oracle_cost_ceiling_upper_bound": oracle_cost_ceiling_ensemble(
                context,
                heldout_rows,
                public_rows,
                atoms_by_name,
                rows_by_index,
                companion_cost,
                p919_cost,
                seed_rule,
            ),
        }
        for name, rules in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(fit_rows),
                    "heldout_source_window": window,
                    "heldout_support": support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": score_ensemble(
                        f"p929_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": score_ensemble(
                        f"p929_{name}_p903",
                        rules,
                        public_rows,
                        atoms_by_name,
                        records,
                        target_rank,
                        p919_cost,
                    ),
                    "rule_families": [rule_family(rule) for rule in rules],
                    "rule_names": [rule_name(rule) for rule in rules],
                }
            )
    summaries = {name: summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p928_source": str(args.p928_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous strategies remove P903 and the heldout source window before rule choice.",
            "ORACLE-CONTROL: the oracle upper bound uses heldout support labels and is not an autonomous selector.",
            "SUPPORT-NOT-COST: a support-recall gain is not promoted unless the P903-restored full policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus relation-selection audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p929_fit_only_support_ensemble_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "p903_c19_indices": sorted(p903_indices),
            "p928_best_strategy": (p928_payload.get("summary") or {}).get("best_strategy"),
            "p928_claim": p928_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "strict_support_families": sorted(STRICT_SUPPORT_FAMILIES),
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p919": p922.compact_policy(p919_report),
        },
        "schema": SCHEMA,
        "summary": {
            "strategy_summaries": summaries,
            "second_holdout": strategy_items,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p928-source", type=Path, default=P928_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    support = summaries.get("fit_only_support_k2_strict_family") or {}
    costed = summaries.get("fit_only_train_cost_ceiling") or {}
    oracle = summaries.get("oracle_cost_ceiling_upper_bound") or {}
    print(
        "claim={claim} support_rec={srec}/{spos} support_false={sfalse} support_p903_pass={spass}/{windows} "
        "costed_rec={crec}/{cpos} costed_p903_pass={cpass}/{windows} oracle_rec={orec}/{opos} "
        "oracle_p903_pass={opass}/{windows} fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            srec=support.get("heldout_recovered_positive_count"),
            spos=support.get("heldout_positive_count"),
            sfalse=support.get("heldout_false_selected_count"),
            spass=support.get("p903_pass_count"),
            windows=support.get("source_window_count"),
            crec=costed.get("heldout_recovered_positive_count"),
            cpos=costed.get("heldout_positive_count"),
            cpass=costed.get("p903_pass_count"),
            orec=oracle.get("heldout_recovered_positive_count"),
            opos=oracle.get("heldout_positive_count"),
            opass=oracle.get("p903_pass_count"),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
