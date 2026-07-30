#!/usr/bin/env python3
"""P925 red-team for gap/source-index tie-breaking inside the P924 class-A tie class."""

from __future__ import annotations

import argparse
import glob
import json
import re
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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p925_gap_source_tiebreaker_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p925_gap_source_tiebreaker_redteam_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P924_SOURCE = STATE_DIR / "low_term_total2_p924_train_only_objective_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p925_gap_source_tiebreaker_redteam.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
PRIMARY_OBJECTIVE = "cost_first_min_tp2"


SelectorFn = Callable[[list[dict[str, Any]]], dict[str, Any]]


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


def predicate_names(rule: dict[str, Any]) -> list[str]:
    return [str(name) for name in rule.get("predicate_names") or []]


def gap_le_values(rule: dict[str, Any]) -> list[int]:
    out = []
    for name in predicate_names(rule):
        match = re.fullmatch(r"gap_le_(\d+)", name)
        if match:
            out.append(int(match.group(1)))
    return out


def source_index_atoms(rule: dict[str, Any]) -> list[tuple[int, int]]:
    out = []
    for name in predicate_names(rule):
        match = re.fullmatch(r"source_index_mod(\d+)_eq_(\d+)", name)
        if match:
            out.append((int(match.group(1)), int(match.group(2))))
    return out


def has_cost_or_salt_atom(rule: dict[str, Any]) -> bool:
    return any(name.startswith(("cost_", "salt_")) for name in predicate_names(rule))


def rule_name(rule: dict[str, Any]) -> str:
    return str(rule.get("name") or "")


def primary_tie_class(public_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any], list[Any] | None]:
    raw_rules, atoms_by_name = p923.fit_rules(public_rows)
    rules = [p924.enrich_rule(rule, public_rows) for rule in raw_rules]
    best_key, tie_class = p924.choose_tie_class(rules, p924.objective_map()[PRIMARY_OBJECTIVE])
    return tie_class, atoms_by_name, list(best_key) if best_key is not None else None


def select_p924_name(tie_class: list[dict[str, Any]]) -> dict[str, Any]:
    return min(tie_class, key=rule_name) if tie_class else {}


def select_source_index_any_gap(tie_class: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        rule
        for rule in tie_class
        if gap_le_values(rule) and source_index_atoms(rule)
    ]
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            min(gap_le_values(rule)),
            min(mod for mod, _rem in source_index_atoms(rule)),
            rule_name(rule),
        ),
    )


def select_gap5_source_index(tie_class: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [
        rule
        for rule in tie_class
        if source_index_atoms(rule) and any(value >= 5 for value in gap_le_values(rule))
    ]
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            min(value for value in gap_le_values(rule) if value >= 5),
            min(mod for mod, _rem in source_index_atoms(rule)),
            rule_name(rule),
        ),
    )


def select_source_index_no_gap_requirement(tie_class: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [rule for rule in tie_class if source_index_atoms(rule)]
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            1 if gap_le_values(rule) else 0,
            min(mod for mod, _rem in source_index_atoms(rule)),
            has_cost_or_salt_atom(rule),
            rule_name(rule),
        ),
    )


def select_gap_floor_no_source_requirement(tie_class: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = [rule for rule in tie_class if any(value >= 5 for value in gap_le_values(rule))]
    if not candidates:
        return {}
    return min(
        candidates,
        key=lambda rule: (
            min(value for value in gap_le_values(rule) if value >= 5),
            0 if source_index_atoms(rule) else 1,
            has_cost_or_salt_atom(rule),
            rule_name(rule),
        ),
    )


def selector_map() -> dict[str, SelectorFn]:
    return {
        "p924_name_tiebreak_control": select_p924_name,
        "source_index_any_gap_min_threshold_control": select_source_index_any_gap,
        "mechanism_gap5_source_index": select_gap5_source_index,
        "source_index_no_gap_requirement_control": select_source_index_no_gap_requirement,
        "gap_floor_no_source_requirement_control": select_gap_floor_no_source_requirement,
    }


def score_rule(
    selector_name: str,
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
        f"p925_{selector_name}_policy",
    )
    full = scored.get("full_policy") or {}
    scored["cost_saved_fraction_vs_p919"] = ratio(
        p919_cost - int_value(full.get("charged_candidate_cost_ops"), 10**12),
        p919_cost,
    )
    return scored


def score_selectors(
    tie_class: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> dict[str, Any]:
    out = {}
    for name, selector in selector_map().items():
        rule = selector(tie_class)
        out[name] = score_rule(name, rule, public_rows, atoms_by_name, records, target_rank, p919_cost)
    return out


def candidate_passes(scored: dict[str, Any], target_rank: int, p919_cost: int) -> bool:
    return p924.candidate_passes(scored, target_rank, p919_cost)


def compact_score(scored: dict[str, Any]) -> dict[str, Any]:
    rule = scored.get("rule") or {}
    full = scored.get("full_policy") or {}
    return {
        "charged_candidate_cost_ops": full.get("charged_candidate_cost_ops"),
        "cost_saved_fraction_vs_p919": scored.get("cost_saved_fraction_vs_p919"),
        "false_selected_count": full.get("false_selected_count"),
        "name": rule.get("name"),
        "predicate_names": rule.get("predicate_names"),
        "selected_c19_indices": scored.get("selected_c19_indices"),
        "target_preserving": full.get("target_preserving"),
        "total_factor_rank": full.get("total_factor_rank"),
        "train_selected_indices": rule.get("train_selected_indices"),
        "train_true_positive_count": rule.get("train_true_positive_count"),
        "validation_selected_indices": rule.get("validation_selected_indices"),
        "validation_true_positive_count": rule.get("validation_true_positive_count"),
    }


def leave_one_source_stress(
    public_rows: list[dict[str, Any]],
    records: list[dict[str, Any]],
    target_rank: int,
    p919_cost: int,
) -> list[dict[str, Any]]:
    windows = sorted(
        {
            p923.source_window(row)
            for row in public_rows
            if row.get("partition") != VALIDATION_PARTITION and p923.source_window(row) != "unknown"
        }
    )
    out = []
    for window in windows:
        fit_rows = [
            row
            for row in public_rows
            if row.get("partition") == VALIDATION_PARTITION or p923.source_window(row) != window
        ]
        tie_class, atoms_by_name, best_key = primary_tie_class(fit_rows)
        scores = score_selectors(tie_class, public_rows, atoms_by_name, records, target_rank, p919_cost)
        primary = scores.get("mechanism_gap5_source_index") or {}
        omitted_rows = [row for row in public_rows if p923.source_window(row) == window]
        out.append(
            {
                "fit_best_key": best_key,
                "fit_tie_class_size": len(tie_class),
                "omitted_indices": [row.get("index") for row in omitted_rows],
                "omitted_positive_count": sum(
                    1 for row in omitted_rows if p922.has_support_class(row, p922.SUPPORT_CLASSES[CLASS_A])
                ),
                "omitted_source_window": window,
                "primary_score": compact_score(primary),
                "primary_passes": candidate_passes(primary, target_rank, p919_cost),
            }
        )
    return out


def stress_summary(stress: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return {
        "leave_one_source_count": len(stress),
        "primary_below_p919_count": sum(
            1
            for item in stress
            if int_value((item.get("primary_score") or {}).get("charged_candidate_cost_ops"), 10**12) < p919_cost
        ),
        "primary_pass_count": sum(1 for item in stress if item.get("primary_passes")),
        "primary_rank_preserving_count": sum(
            1 for item in stress if int_value((item.get("primary_score") or {}).get("total_factor_rank")) >= target_rank
        ),
        "primary_validation_recovered_count": sum(
            1
            for item in stress
            if int_value((item.get("primary_score") or {}).get("validation_true_positive_count")) > 0
        ),
    }


def fresh_window_summary() -> dict[str, Any]:
    pattern = str(STATE_DIR / "frontier_public_leaf_policy_low_term_total2_fixed_row_*_expanded_probe.json")
    windows = []
    for path in glob.glob(pattern):
        match = re.search(r"_row_(\d+)_(\d+)_expanded_probe\.json$", path)
        if match:
            windows.append((int(match.group(1)), int(match.group(2)), path))
    windows.sort()
    return {
        "fresh_1160_plus_available": any(low >= 1160 for low, _high, _path in windows),
        "max_window": list(windows[-1][:2]) if windows else None,
        "window_count": len(windows),
    }


def determine_claim(primary: dict[str, Any], stress: list[dict[str, Any]], target_rank: int, p919_cost: int) -> str:
    if not primary:
        return "NEGATIVE_RESULT_P925_NO_GAP_SOURCE_TIEBREAKER_RULE"
    if not candidate_passes(primary, target_rank, p919_cost):
        return "NEGATIVE_RESULT_P925_GAP_SOURCE_TIEBREAKER_FAILS_ARCHIVE_VALIDATION"
    if all(item.get("primary_passes") for item in stress):
        return "P925_GAP_SOURCE_TIEBREAKER_STABLE_ARCHIVE_SELECTOR"
    return "P925_GAP_SOURCE_TIEBREAKER_RECOVERS_ARCHIVE_VALIDATION_BUT_SOURCE_STRESS_MIXED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p924_payload = load_json(args.p924_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    tie_class, atoms_by_name, best_key = primary_tie_class(public_rows)
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
    selector_scores = score_selectors(tie_class, public_rows, atoms_by_name, records, target_rank, p919_cost)
    stress = leave_one_source_stress(public_rows, records, target_rank, p919_cost)
    primary = selector_scores.get("mechanism_gap5_source_index") or {}
    passing_tie = []
    for rule in tie_class:
        scored = score_rule("tie_member", rule, public_rows, atoms_by_name, records, target_rank, p919_cost)
        if candidate_passes(scored, target_rank, p919_cost):
            passing_tie.append(compact_score(scored))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p924_source": str(args.p924_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(primary, stress, target_rank, p919_cost),
        "created_at": now_iso(),
        "fresh_window_summary": fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived validation after tie-breaker freeze.",
            "MECHANISM-PRIOR: the gap-5 boundary is archive-learned from prior c19 structure audits.",
            "TIEBREAKER-REDTEAM: controls test whether simpler tie-breaking would have worked.",
            "SOURCE-WINDOW-STRESS: leave-one-source-window reruns test brittleness inside the archive.",
            "FRESH-REPLAY-REQUIRED: no fresh compatible 1160+ row window is claimed here.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p925_gap_source_tiebreaker_redteam",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "p924_claim": p924_payload.get("claim_status"),
            "primary_objective": PRIMARY_OBJECTIVE,
            "primary_tie_best_key": best_key,
            "primary_tie_class_size": len(tie_class),
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
            "leave_one_source_stress": stress,
            "leave_one_source_summary": stress_summary(stress, target_rank, p919_cost),
            "passing_primary_tie_members": passing_tie,
            "selector_scores": {name: compact_score(score) for name, score in selector_scores.items()},
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p924-source", type=Path, default=P924_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    primary = ((payload.get("summary") or {}).get("selector_scores") or {}).get("mechanism_gap5_source_index") or {}
    stress = (payload.get("summary") or {}).get("leave_one_source_summary") or {}
    print(
        "claim={claim} rule={rule} cost={cost} rank={rank} validation_tp={validation_tp} "
        "stress_pass={stress_pass}/{stress_count} fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            rule=primary.get("name"),
            cost=primary.get("charged_candidate_cost_ops"),
            rank=primary.get("total_factor_rank"),
            validation_tp=primary.get("validation_true_positive_count"),
            stress_pass=stress.get("primary_pass_count"),
            stress_count=stress.get("leave_one_source_count"),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
