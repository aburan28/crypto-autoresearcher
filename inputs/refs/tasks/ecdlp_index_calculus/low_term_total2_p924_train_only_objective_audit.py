#!/usr/bin/env python3
"""P924 train-only objective audit for class-A support predictors."""

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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p924_train_only_objective_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p924_train_only_objective_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P922_SOURCE = STATE_DIR / "low_term_total2_p922_support_class_cost_audit_probe.json"
P923_SOURCE = STATE_DIR / "low_term_total2_p923_train_only_support_class_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p924_train_only_objective_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION


ScoreKey = tuple[int | str, ...]
ObjectiveFn = Callable[[dict[str, Any]], ScoreKey | None]


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


def train_rows(public_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in public_rows if row.get("partition") != VALIDATION_PARTITION]


def rule_train_indices(rule: dict[str, Any]) -> set[int]:
    return {int_value(index) for index in rule.get("train_selected_indices") or []}


def rule_arity(rule: dict[str, Any]) -> int:
    return len(rule.get("predicate_names") or [])


def enrich_rule(rule: dict[str, Any], public_rows: list[dict[str, Any]]) -> dict[str, Any]:
    rows_by_index = {int_value(row.get("index")): row for row in public_rows}
    indices = rule_train_indices(rule)
    selected_train_rows = [rows_by_index[index] for index in sorted(indices) if index in rows_by_index]
    positive_windows = {
        p923.source_window(row)
        for row in selected_train_rows
        if p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])
    }
    out = dict(rule)
    out["train_positive_source_window_count"] = len(positive_windows)
    out["train_selected_cost_ops"] = sum(int_value(row.get("charged_candidate_cost_ops")) for row in selected_train_rows)
    out["train_selected_source_windows"] = sorted({p923.source_window(row) for row in selected_train_rows})
    return out


def objective_map() -> dict[str, ObjectiveFn]:
    def max_train_tp(rule: dict[str, Any]) -> ScoreKey | None:
        return (
            -int_value(rule.get("train_true_positive_count")),
            -int(1_000_000 * float(rule.get("train_recall") or 0.0)),
            int_value(rule.get("train_selected_cost_ops"), 10**12),
            rule_arity(rule),
        )

    def cost_first_min_tp(min_tp: int) -> ObjectiveFn:
        def score(rule: dict[str, Any]) -> ScoreKey | None:
            if int_value(rule.get("train_true_positive_count")) < min_tp:
                return None
            return (
                int_value(rule.get("train_selected_cost_ops"), 10**12),
                -int_value(rule.get("train_true_positive_count")),
                rule_arity(rule),
            )

        return score

    def window_diverse_min_tp2(rule: dict[str, Any]) -> ScoreKey | None:
        if int_value(rule.get("train_true_positive_count")) < 2:
            return None
        return (
            -int_value(rule.get("train_positive_source_window_count")),
            int_value(rule.get("train_selected_cost_ops"), 10**12),
            -int_value(rule.get("train_true_positive_count")),
            rule_arity(rule),
        )

    return {
        "max_train_tp": max_train_tp,
        "cost_first_min_tp1": cost_first_min_tp(1),
        "cost_first_min_tp2": cost_first_min_tp(2),
        "cost_first_min_tp3": cost_first_min_tp(3),
        "window_diverse_min_tp2": window_diverse_min_tp2,
    }


def choose_tie_class(rules: list[dict[str, Any]], objective: ObjectiveFn) -> tuple[ScoreKey | None, list[dict[str, Any]]]:
    scored = [(key, rule) for rule in rules if (key := objective(rule)) is not None]
    if not scored:
        return None, []
    best_key = min(key for key, _rule in scored)
    tied = [rule for key, rule in scored if key == best_key]
    tied.sort(key=lambda rule: str(rule.get("name")))
    return best_key, tied


def score_candidate(
    rule: dict[str, Any],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
    name: str,
) -> dict[str, Any]:
    return p923.score_rule(
        name,
        p923.rule_key(rule),
        public_rows,
        atoms_by_name,
        records,
        target_rank,
        p919_cost,
    )


def candidate_passes(scored: dict[str, Any], target_rank: int, p919_cost: int) -> bool:
    rule = scored.get("rule") or {}
    full = scored.get("full_policy") or {}
    return (
        int_value(rule.get("validation_true_positive_count")) > 0
        and int_value(full.get("false_selected_count")) == 0
        and int_value(full.get("total_factor_rank")) >= target_rank
        and int_value(full.get("charged_candidate_cost_ops"), 10**12) < p919_cost
    )


def objective_report(
    name: str,
    objective: ObjectiveFn,
    rules: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    best_key, tie_class = choose_tie_class(rules, objective)
    deterministic = tie_class[0] if tie_class else {}
    scored_deterministic = (
        score_candidate(
            deterministic,
            public_rows,
            atoms_by_name,
            records,
            target_rank,
            p919_cost,
            f"p924_{name}_deterministic_policy",
        )
        if deterministic
        else {}
    )
    tie_scores = [
        score_candidate(
            rule,
            public_rows,
            atoms_by_name,
            records,
            target_rank,
            p919_cost,
            f"p924_{name}_tie_policy",
        )
        for rule in tie_class
    ]
    passing = [score for score in tie_scores if candidate_passes(score, target_rank, p919_cost)]
    validation_hits = [
        score for score in tie_scores if int_value(((score.get("rule") or {}).get("validation_true_positive_count"))) > 0
    ]
    def score_preview(score: dict[str, Any]) -> dict[str, Any]:
        rule = score.get("rule") or {}
        full = score.get("full_policy") or {}
        return {
            "charged_candidate_cost_ops": full.get("charged_candidate_cost_ops"),
            "name": rule.get("name"),
            "predicate_names": rule.get("predicate_names"),
            "selected_c19_indices": score.get("selected_c19_indices"),
            "target_preserving": full.get("target_preserving"),
            "total_factor_rank": full.get("total_factor_rank"),
            "train_selected_indices": rule.get("train_selected_indices"),
            "train_true_positive_count": rule.get("train_true_positive_count"),
            "validation_selected_indices": rule.get("validation_selected_indices"),
            "validation_true_positive_count": rule.get("validation_true_positive_count"),
        }

    return {
        "best_key": list(best_key) if best_key is not None else None,
        "deterministic_choice": scored_deterministic,
        "objective": name,
        "tie_class_all_pass_count": len(passing),
        "tie_class_passing_preview": [score_preview(score) for score in passing[:20]],
        "tie_class_preview": [
            {
                "name": rule.get("name"),
                "predicate_names": rule.get("predicate_names"),
                "train_positive_source_window_count": rule.get("train_positive_source_window_count"),
                "train_selected_cost_ops": rule.get("train_selected_cost_ops"),
                "train_selected_indices": rule.get("train_selected_indices"),
                "train_true_positive_count": rule.get("train_true_positive_count"),
                "validation_selected_indices": rule.get("validation_selected_indices"),
                "validation_true_positive_count": rule.get("validation_true_positive_count"),
            }
            for rule in tie_class[:20]
        ],
        "tie_class_size": len(tie_class),
        "tie_class_validation_recovered_count": len(validation_hits),
        "tie_class_validation_recovered_preview": [score_preview(score) for score in validation_hits[:20]],
    }


def determine_claim(primary: dict[str, Any], target_rank: int, p919_cost: int) -> str:
    deterministic = primary.get("deterministic_choice") or {}
    tie_size = int_value(primary.get("tie_class_size"))
    tie_pass = int_value(primary.get("tie_class_all_pass_count"))
    tie_validation = int_value(primary.get("tie_class_validation_recovered_count"))
    if not deterministic:
        return "NEGATIVE_RESULT_P924_PRIMARY_OBJECTIVE_HAS_NO_RULE"
    if not candidate_passes(deterministic, target_rank, p919_cost):
        return "NEGATIVE_RESULT_P924_PRIMARY_OBJECTIVE_DETERMINISTIC_RULE_FAILS"
    if tie_pass == tie_size and tie_validation == tie_size:
        return "P924_TRAIN_ONLY_COST_OBJECTIVE_STRONG_RECOVERS_VALIDATION"
    return "P924_TRAIN_ONLY_COST_OBJECTIVE_RECOVERS_VALIDATION_WITH_MIXED_TIE_CLASS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p922_payload = load_json(args.p922_source)
    p923_payload = load_json(args.p923_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    raw_rules, atoms_by_name = p923.fit_rules(public_rows)
    rules = [enrich_rule(rule, public_rows) for rule in raw_rules]
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
    reports = [
        objective_report(
            name,
            objective,
            rules,
            public_rows,
            atoms_by_name,
            records,
            target_rank,
            p919_cost,
        )
        for name, objective in objective_map().items()
    ]
    reports_by_name = {report["objective"]: report for report in reports}
    primary = reports_by_name["cost_first_min_tp2"]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p922_source": str(args.p922_source),
            "p923_source": str(args.p923_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(primary, target_rank, p919_cost),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived validation after train-only objective freeze.",
            "TRAIN-OBJECTIVE-AUDIT: objective definitions are predeclared in the contract.",
            "TIE-CLASS-BOUNDARY: mixed tie classes are not autonomous selectors.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p924_train_only_objective_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p922_claim": p922_payload.get("claim_status"),
            "p923_claim": p923_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "train_only_class_a_rule_count": len(rules),
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p919": p922.compact_policy(p919_report),
            "p923_primary": ((p923_payload.get("summary") or {}).get("primary_train_only_candidate") or {}),
        },
        "schema": SCHEMA,
        "summary": {
            "objective_reports": reports,
            "primary_objective": primary,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p922-source", type=Path, default=P922_SOURCE)
    parser.add_argument("--p923-source", type=Path, default=P923_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    primary = (payload.get("summary") or {}).get("primary_objective") or {}
    deterministic = primary.get("deterministic_choice") or {}
    rule = deterministic.get("rule") or {}
    full = deterministic.get("full_policy") or {}
    print(
        "claim={claim} primary={objective} tie={tie_size} tie_pass={tie_pass} tie_val={tie_val} "
        "rule={rule_name} cost={cost} rank={rank} validation_tp={validation_tp} out={out}".format(
            claim=payload.get("claim_status"),
            objective=primary.get("objective"),
            tie_size=primary.get("tie_class_size"),
            tie_pass=primary.get("tie_class_all_pass_count"),
            tie_val=primary.get("tie_class_validation_recovered_count"),
            rule_name=rule.get("name"),
            cost=full.get("charged_candidate_cost_ops"),
            rank=full.get("total_factor_rank"),
            validation_tp=rule.get("validation_true_positive_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
