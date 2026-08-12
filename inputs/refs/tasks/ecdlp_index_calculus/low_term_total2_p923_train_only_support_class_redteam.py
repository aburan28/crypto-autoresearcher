#!/usr/bin/env python3
"""P923 train-only red-team for the P922 class-A support predictor."""

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
import low_term_total2_p916_public_rank_increment_predictor as p916
import low_term_total2_p917_public_c8_residue_redteam as p917
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p921_c19_simple_public_predictor as p921
import low_term_total2_p922_support_class_cost_audit as p922


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p923_train_only_support_class_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p923_train_only_support_class_redteam_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P921_SOURCE = STATE_DIR / "low_term_total2_p921_c19_simple_public_predictor_probe.json"
P922_SOURCE = STATE_DIR / "low_term_total2_p922_support_class_cost_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p923_train_only_support_class_redteam.v1"
CLASS_A = "A_0_2_rhs11025"
VALIDATION_PARTITION = p922.VALIDATION_PARTITION
P922_RULE = ("gap_le_5", "source_index_mod3_eq_2")


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


def rule_key(rule: dict[str, Any] | None) -> tuple[str, ...]:
    if not rule:
        return ()
    return tuple(str(name) for name in rule.get("predicate_names") or [])


def source_window_from_path(path: Any) -> str:
    match = re.search(r"_(\d+)_(\d+)_expanded_probe\.json$", str(path or ""))
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return "unknown"


def source_window(row: dict[str, Any]) -> str:
    return source_window_from_path(row.get("source_path"))


def c19_public_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    source_by_ordinal = p921.source_cases_by_ordinal()
    rows = []
    for record in records:
        if p916.short_clause(record) != "c19":
            continue
        ordinal = int_value((record.get("row") or {}).get("archive_stream_ordinal"))
        row = p921.public_feature_row(record, source_by_ordinal[ordinal])
        row["source_window"] = source_window(row)
        rows.append(row)
    return rows


def fit_rules(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    fit_train = [row for row in rows if row.get("partition") != VALIDATION_PARTITION]
    atoms_by_name = {name: fn for name, fn in p921.atom_list(fit_train)}
    return p922.search_support_rules(CLASS_A, rows, atoms_by_name, False), atoms_by_name


def score_rule(
    name: str,
    predicate_names: tuple[str, ...],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    train_rows = [row for row in public_rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in public_rows if row.get("partition") == VALIDATION_PARTITION]
    support_report = p922.support_rule_report(
        CLASS_A,
        list(predicate_names),
        public_rows,
        train_rows,
        validation_rows,
        atoms_by_name,
    )
    selected_indices = {int_value(index) for index in support_report.get("all_selected_indices") or []}
    full_report = p922.full_policy_report(name, records, selected_indices, target_rank)
    full_compact = p922.compact_policy(full_report)
    cost = int_value(full_compact.get("charged_candidate_cost_ops"), 10**12)
    return {
        "cost_saved_fraction_vs_p919": ratio(p919_cost - cost, p919_cost),
        "full_policy": full_compact,
        "rule": support_report,
        "selected_c19_indices": sorted(selected_indices),
    }


def leave_one_source_stress(
    public_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> list[dict[str, Any]]:
    out = []
    train_windows = sorted(
        {
            source_window(row)
            for row in public_rows
            if row.get("partition") != VALIDATION_PARTITION and source_window(row) != "unknown"
        }
    )
    validation_rows = [row for row in public_rows if row.get("partition") == VALIDATION_PARTITION]
    for window in train_windows:
        fit_rows = [
            row
            for row in public_rows
            if row.get("partition") == VALIDATION_PARTITION or source_window(row) != window
        ]
        rules, atoms_by_name = fit_rules(fit_rows)
        top = rules[0] if rules else {}
        scored = (
            score_rule(
                f"p923_leave_one_{window}_class_a_policy",
                rule_key(top),
                public_rows,
                atoms_by_name,
                records,
                target_rank,
                p919_cost,
            )
            if top
            else {}
        )
        omitted_rows = [row for row in public_rows if source_window(row) == window]
        out.append(
            {
                "fit_train_row_count": sum(1 for row in fit_rows if row.get("partition") != VALIDATION_PARTITION),
                "omitted_indices": [row.get("index") for row in omitted_rows],
                "omitted_positive_count": sum(
                    1 for row in omitted_rows if p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])
                ),
                "omitted_source_window": window,
                "rule": {
                    "name": top.get("name"),
                    "predicate_names": top.get("predicate_names"),
                    "train_false_positive_count": top.get("train_false_positive_count"),
                    "train_selected_count": top.get("train_selected_count"),
                    "train_true_positive_count": top.get("train_true_positive_count"),
                    "validation_selected_indices_during_fit": top.get("validation_selected_indices"),
                    "validation_true_positive_count_during_fit": top.get("validation_true_positive_count"),
                }
                if top
                else {},
                "score_on_full_archive_after_freeze": scored,
                "validation_row_count": len(validation_rows),
            }
        )
    return out


def determine_claim(primary: dict[str, Any], p919_cost: int, target_rank: int) -> str:
    full = primary.get("full_policy") or {}
    rule = primary.get("rule") or {}
    if not primary:
        return "NEGATIVE_RESULT_P923_NO_TRAIN_ONLY_CLASS_A_RULE"
    if int_value(rule.get("validation_true_positive_count")) <= 0:
        return "NEGATIVE_RESULT_P923_TRAIN_ONLY_CLASS_A_MISSES_VALIDATION"
    if int_value(full.get("false_selected_count")) != 0:
        return "NEGATIVE_RESULT_P923_TRAIN_ONLY_CLASS_A_SELECTS_FALSE_CERTIFICATE"
    if int_value(full.get("total_factor_rank")) < target_rank:
        return "NEGATIVE_RESULT_P923_TRAIN_ONLY_CLASS_A_LOSES_RANK6"
    if int_value(full.get("charged_candidate_cost_ops"), 10**12) >= p919_cost:
        return "P923_TRAIN_ONLY_CLASS_A_RECOVERS_VALIDATION_BUT_NOT_COST_COMPETITIVE"
    return "P923_TRAIN_ONLY_CLASS_A_RECOVERS_VALIDATION_AND_REDUCES_COST"


def summarize_stress(stress: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    recovered = 0
    rank_preserving = 0
    below_p919 = 0
    distinct_rules: dict[str, int] = {}
    for item in stress:
        scored = item.get("score_on_full_archive_after_freeze") or {}
        rule = scored.get("rule") or {}
        full = scored.get("full_policy") or {}
        name = str(((item.get("rule") or {}).get("name")) or "none")
        distinct_rules[name] = distinct_rules.get(name, 0) + 1
        if int_value(rule.get("validation_true_positive_count")) > 0:
            recovered += 1
        if int_value(full.get("total_factor_rank")) >= target_rank and int_value(full.get("false_selected_count")) == 0:
            rank_preserving += 1
        if int_value(full.get("charged_candidate_cost_ops"), 10**12) < p919_cost:
            below_p919 += 1
    return {
        "below_p919_count": below_p919,
        "distinct_top_rules": distinct_rules,
        "leave_one_source_count": len(stress),
        "rank_preserving_count": rank_preserving,
        "validation_recovered_count": recovered,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p921_payload = load_json(args.p921_source)
    p922_payload = load_json(args.p922_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = c19_public_rows(records)
    rules, atoms_by_name = fit_rules(public_rows)
    primary_rule = rules[0] if rules else {}

    p917_report = p915.policy_report(
        "p917_policy_recomputed",
        p917.residue_policy_records(records, 11, {2, 4}),
        "P917 control.",
        target_rank,
        True,
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

    primary = (
        score_rule(
            "p923_train_only_class_a_policy",
            rule_key(primary_rule),
            public_rows,
            atoms_by_name,
            records,
            target_rank,
            p919_cost,
        )
        if primary_rule
        else {}
    )
    p922_rule = score_rule(
        "p922_validation_selected_class_a_policy_recomputed",
        P922_RULE,
        public_rows,
        atoms_by_name,
        records,
        target_rank,
        p919_cost,
    )
    p922_rule_rank = next(
        (index + 1 for index, rule in enumerate(rules) if rule_key(rule) == P922_RULE),
        None,
    )
    stress = leave_one_source_stress(public_rows, records, target_rank, p919_cost)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p921_source": str(args.p921_source),
            "p922_source": str(args.p922_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(primary, p919_cost, target_rank),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores an archived validation row after train-only rule freeze.",
            "LEAKAGE-REDTEAM: primary rule selection does not require validation-positive recovery.",
            "SOURCE-WINDOW-STRESS: leave-one-source-window reruns test brittleness inside the archive.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p923_train_only_support_class_redteam",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p921_claim": p921_payload.get("claim_status"),
            "p922_claim": p922_payload.get("claim_status"),
            "p922_validation_selected_rule_rank_under_train_only_sort": p922_rule_rank,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "train_only_class_a_rule_count": len(rules),
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p917": p922.compact_policy(p917_report),
            "p919": p922.compact_policy(p919_report),
            "p922_validation_selected_rule_recomputed": p922_rule,
        },
        "schema": SCHEMA,
        "summary": {
            "c19_public_rows": public_rows,
            "leave_one_source_stress": stress,
            "leave_one_source_summary": summarize_stress(stress, target_rank, p919_cost),
            "primary_train_only_candidate": primary,
            "train_only_top_rules": rules[:12],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p921-source", type=Path, default=P921_SOURCE)
    parser.add_argument("--p922-source", type=Path, default=P922_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    primary = (payload.get("summary") or {}).get("primary_train_only_candidate") or {}
    full = primary.get("full_policy") or {}
    rule = primary.get("rule") or {}
    stress = (payload.get("summary") or {}).get("leave_one_source_summary") or {}
    print(
        "claim={claim} rules={rules} primary={rule_name} cost={cost} rank={rank} selected={selected} "
        "saved_vs_p919={saved} validation_tp={validation_tp} loo_recovered={loo_rec}/{loo_count} out={out}".format(
            claim=payload.get("claim_status"),
            rules=(payload.get("parameters") or {}).get("train_only_class_a_rule_count"),
            rule_name=rule.get("name"),
            cost=full.get("charged_candidate_cost_ops"),
            rank=full.get("total_factor_rank"),
            selected=full.get("selected_count"),
            saved=primary.get("cost_saved_fraction_vs_p919"),
            validation_tp=rule.get("validation_true_positive_count"),
            loo_rec=stress.get("validation_recovered_count"),
            loo_count=stress.get("leave_one_source_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
