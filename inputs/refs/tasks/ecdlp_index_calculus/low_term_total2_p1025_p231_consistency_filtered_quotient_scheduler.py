#!/usr/bin/env python3
"""P1025 consistency-filtered quotient scheduler for fresh leaf-19 windows."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit as p1024
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1025_p231_consistency_filtered_quotient_scheduler.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler.v1"
SEED_PUBLIC = "[9131,7063]"
FRESH_WINDOWS = [
    "12440_12447",
    "12448_12455",
    "12456_12463",
    "12464_12471",
    "12472_12479",
    "12480_12487",
    "12488_12495",
    "12496_12503",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def round8(value: float | None) -> float | None:
    return p1023.round8(value)


def split_set(form: dict[str, Any]) -> set[str]:
    splits = form.get("splits") if isinstance(form.get("splits"), list) else None
    if splits:
        return {str(value) for value in splits}
    split = form.get("split")
    return {str(split)} if split else set()


def has_fresh(form: dict[str, Any]) -> bool:
    return "fresh_validation" in split_set(form)


def pair_role(left: dict[str, Any], right: dict[str, Any]) -> str:
    left_fresh = has_fresh(left)
    right_fresh = has_fresh(right)
    if left_fresh and right_fresh:
        return "fresh_pair"
    if left_fresh or right_fresh:
        return "mixed_training_fresh_pair"
    return "training_pair"


def selected_rows_for_many(
    windows: list[str],
    by_window: dict[str, list[dict[str, Any]]],
    split: str,
) -> list[dict[str, Any]]:
    return p1023.selected_rows_for(windows, by_window, split)


def selected_false_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if not bool(row.get("label_positive")))


def selected_positive_count(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if bool(row.get("label_positive")))


def target_eliminated_relations(
    forms: list[dict[str, Any]],
    order: int,
    public_fingerprint: str,
) -> tuple[list[dict[str, Any]], int]:
    unique_forms = p1023.unique_forms(forms)
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique_forms] or [0])
    relations: list[dict[str, Any]] = []
    for left_index, left in enumerate(unique_forms):
        for right_index in range(left_index + 1, len(unique_forms)):
            right = unique_forms[right_index]
            q_left, factors_left, rhs_left = factor_bank.form_parts(left, order, factor_count)
            q_right, factors_right, rhs_right = factor_bank.form_parts(right, order, factor_count)
            factor_coeffs = [
                (q_right * factors_left[index] - q_left * factors_right[index]) % order
                for index in range(factor_count)
            ]
            rhs = (q_right * rhs_left - q_left * rhs_right) % order
            canonical = factor_bank.canonical_relation(factor_coeffs, rhs, order)
            base = {
                "left_form_index": left_index,
                "left_splits": sorted(split_set(left)),
                "pair": [left_index, right_index],
                "pair_role": pair_role(left, right),
                "public_fingerprint": public_fingerprint,
                "q_coeffs": [q_left, q_right],
                "right_form_index": right_index,
                "right_splits": sorted(split_set(right)),
            }
            if canonical is None:
                relations.append({**base, "relation_status": "TRIVIAL_ZERO_RELATION"})
                continue
            coeff_key, canonical_rhs = canonical
            support = [index for index, coeff in enumerate(coeff_key) if coeff % order]
            relations.append(
                {
                    **base,
                    "canonical_coeffs": list(coeff_key),
                    "canonical_rhs": canonical_rhs,
                    "factor_support": support,
                    "factor_support_size": len(support),
                    "relation_status": (
                        "TARGET_ELIMINATED_FACTOR_RELATION"
                        if support
                        else "INCONSISTENT_ZERO_COEFF_RELATION"
                    ),
                }
            )
    return relations, factor_count


def nontrivial(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [relation for relation in relations if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"]


def quotient_bank_summary(relations: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    return p1024.quotient_bank_summary(relations, order, factor_count)


def marginal_gain(
    base_relations: list[dict[str, Any]],
    candidate_relations: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> dict[str, Any]:
    return p1024.marginal_rank_gain(base_relations, candidate_relations, order, factor_count)


def compact_group_candidate(
    public: str,
    forms: list[dict[str, Any]],
    seed_relations: list[dict[str, Any]],
    order: int,
    factor_count: int,
) -> dict[str, Any]:
    unique = p1023.unique_forms(forms)
    relations, local_factor_count = target_eliminated_relations(unique, order, public)
    factor_count = max(factor_count, local_factor_count)
    candidate_relations = [
        relation
        for relation in relations
        if relation.get("pair_role") in {"mixed_training_fresh_pair", "fresh_pair"}
    ]
    candidate_bank = quotient_bank_summary(candidate_relations, order, factor_count)
    seed_plus_candidate = quotient_bank_summary([*seed_relations, *candidate_relations], order, factor_count)
    gain = marginal_gain(seed_relations, candidate_relations, order, factor_count)
    fresh_form_count = sum(1 for form in unique if has_fresh(form))
    return {
        "candidate_bank": candidate_bank,
        "fresh_unique_form_count": fresh_form_count,
        "marginal_gain_over_seed": gain,
        "public_fingerprint": public,
        "relation_count_involving_fresh": len(candidate_relations),
        "seed_plus_candidate_bank": seed_plus_candidate,
        "selected_for_promotion": bool(
            fresh_form_count
            and candidate_bank["factor_relation_count"] > 0
            and candidate_bank["matrix_consistent"]
            and seed_plus_candidate["matrix_consistent"]
            and int_value(gain.get("rank_gain")) > 0
        ),
        "unique_form_count": len(unique),
    }


def reconstruct_partition(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        return [], []
    selected_by_case = {p1023.row_case_id(row): row for row in rows}
    reconstructed, verifier, built_by_row = p1005.p1003.reconstruct_selected(rows)
    del verifier
    return reconstructed, p1023.annotated_form_records(reconstructed, built_by_row, selected_by_case)


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    training_windows = [*p1022.POSITIVE_CALIBRATION_WINDOWS, *p1022.VALIDATION_WINDOWS]
    all_windows = [*training_windows, *p1022.NEGATIVE_CALIBRATION_WINDOWS, *FRESH_WINDOWS]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    training_rows = selected_rows_for_many(training_windows, by_window, "training_seed")
    negative_rows = selected_rows_for_many(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control")
    fresh_rows = selected_rows_for_many(FRESH_WINDOWS, by_window, "fresh_validation")
    selected = [*training_rows, *fresh_rows]
    training_reconstructed, training_forms = reconstruct_partition(training_rows)
    fresh_reconstructed, fresh_forms = reconstruct_partition(fresh_rows)
    reconstructed = [*training_reconstructed, *fresh_reconstructed]
    forms = [*training_forms, *fresh_forms]
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    order = form_orders[0] if len(form_orders) == 1 else 0
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    forms_by_public: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_public[str(form.get("public_fingerprint"))].append(form)
    seed_forms = [
        form
        for form in forms_by_public.get(args.seed_public, [])
        if "training_seed" in split_set(form)
    ]
    seed_relations, seed_factor_count = target_eliminated_relations(seed_forms, order, args.seed_public)
    seed_bank = quotient_bank_summary(seed_relations, order, seed_factor_count)
    factor_count = max(
        [seed_factor_count, *[max([max(0, len(form.get("coeffs") or []) - 1) for form in group] or [0]) for group in forms_by_public.values()]]
    )
    candidates = [
        compact_group_candidate(public, group, nontrivial(seed_relations), order, factor_count)
        for public, group in sorted(forms_by_public.items())
        if any(has_fresh(form) for form in group) and len(p1023.unique_forms(group)) >= 2
    ]
    candidates.sort(
        key=lambda item: (
            0 if item.get("selected_for_promotion") else 1,
            -int_value((item.get("marginal_gain_over_seed") or {}).get("rank_gain")),
            str(item.get("public_fingerprint")),
        )
    )
    promotions = [candidate for candidate in candidates if candidate.get("selected_for_promotion")]
    internally_consistent = [
        candidate
        for candidate in candidates
        if (candidate.get("candidate_bank") or {}).get("matrix_consistent")
        and int_value((candidate.get("candidate_bank") or {}).get("factor_relation_count")) > 0
    ]
    seed_reproduced = (
        seed_bank["rank"] == 2
        and seed_bank["augmented_rank"] == 2
        and bool(seed_bank["matrix_consistent"])
    )
    if negative_rows:
        claim = "NEGATIVE_RESULT_P1025_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif not all(exists.get(window) for window in FRESH_WINDOWS):
        claim = "NEGATIVE_RESULT_P1025_MISSING_FRESH_SOURCE_WINDOWS"
    elif len(training_rows) != 14:
        claim = "NEGATIVE_RESULT_P1025_UNEXPECTED_TRAINING_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1025_RECONSTRUCTION_ERRORS"
    elif len(form_orders) != 1:
        claim = "NEGATIVE_RESULT_P1025_INCONSISTENT_FORM_ORDERS"
    elif not seed_reproduced:
        claim = "NEGATIVE_RESULT_P1025_SEED_QUOTIENT_NOT_REPRODUCED"
    elif not fresh_rows:
        claim = "NEGATIVE_RESULT_P1025_FRESH_RULE_SELECTS_NO_ROWS"
    elif selected_false_count(fresh_rows):
        claim = "P1025_FRESH_QUOTIENT_SEARCH_BLOCKED_BY_SELECTION_NOISE"
    elif promotions:
        claim = "P1025_SECOND_CONSISTENT_QUOTIENT_DIRECTION_FOUND"
    elif internally_consistent:
        claim = "P1025_LOCAL_CONSISTENT_FRESH_QUOTIENT_GLOBAL_RANK_PLATEAU"
    elif candidates:
        claim = "NEGATIVE_RESULT_P1025_FRESH_QUOTIENT_CANDIDATES_INCONSISTENT_OR_DEPENDENT"
    else:
        claim = "NEGATIVE_RESULT_P1025_NO_FRESH_QUOTIENT_CANDIDATES"
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in all_windows
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1024_dependency_sha256": p1005.sha256_file(Path(p1024.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1025_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "INDEX-CALCULUS PRECURSOR: consistency-filtered quotient rank is not sparse linear algebra closure or target descent.",
            "SEED BOUNDARY: P1025 uses the P1024 clean public [9131,7063] quotient class as a fixed seed.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; this audit tests relation-bank structure only.",
        ],
        "parameters": {
            "fresh_windows": FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "seed_public": args.seed_public,
            "training_windows": training_windows,
            "primary_rule": p1022.PRIMARY_RULE_NAME,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {
            "exists": exists,
        },
        "summary": {
            "candidate_group_count": len(candidates),
            "factor_count": factor_count,
            "fresh_false_selected_count": selected_false_count(fresh_rows),
            "fresh_positive_selected_count": selected_positive_count(fresh_rows),
            "fresh_selected_count": len(fresh_rows),
            "fresh_selected_ops_over_rho": round8(sum(p1023.selected_ops(row) for row in fresh_rows)),
            "internally_consistent_candidate_count": len(internally_consistent),
            "negative_control_selected_count": len(negative_rows),
            "promotion_count": len(promotions),
            "promotions": promotions[:8],
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "seed_bank": seed_bank,
            "seed_reproduced": seed_reproduced,
            "selected_count": len(selected),
            "training_selected_count": len(training_rows),
        },
        "candidate_groups": candidates[:24],
        "fresh_selected_rows": [p1023.compact_row(row) for row in fresh_rows],
        "negative_control_selected_rows": [p1023.compact_row(row) for row in negative_rows],
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--seed-public", default=SEED_PUBLIC, help="Seed public fingerprint")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} training={training} fresh={fresh} fresh_pos={fresh_pos} "
        "fresh_false={fresh_false} candidates={candidates} promotions={promotions} "
        "seed_rank={seed_rank}/{factors} out={out}".format(
            claim=payload["claim_status"],
            training=summary["training_selected_count"],
            fresh=summary["fresh_selected_count"],
            fresh_pos=summary["fresh_positive_selected_count"],
            fresh_false=summary["fresh_false_selected_count"],
            candidates=summary["candidate_group_count"],
            promotions=summary["promotion_count"],
            seed_rank=summary["seed_bank"]["rank"],
            factors=summary["factor_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
