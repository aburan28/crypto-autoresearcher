#!/usr/bin/env python3
"""P1024 target-eliminated quotient audit for P1023 leaf-19 form groups."""

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
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1024_p231_leaf19_target_elim_quotient_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1024_p231_leaf19_target_elim_quotient_audit.v1"
DEFAULT_FOCUS_PUBLICS = "[9131,7063];[5178,1815]"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def round8(value: float | None) -> float | None:
    return p1023.round8(value)


def parse_focus_publics(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(";") if item.strip()]


def split_set(form: dict[str, Any]) -> set[str]:
    splits = form.get("splits") if isinstance(form.get("splits"), list) else None
    if splits:
        return {str(item) for item in splits}
    split = form.get("split")
    return {str(split)} if split else set()


def pair_role(left: dict[str, Any], right: dict[str, Any]) -> str:
    left_splits = split_set(left)
    right_splits = split_set(right)
    has_validation = "validation" in left_splits or "validation" in right_splits
    has_calibration = "positive_calibration" in left_splits or "positive_calibration" in right_splits
    if has_validation and has_calibration:
        return "mixed_calibration_validation_pair"
    if has_validation:
        return "validation_pair"
    return "calibration_pair"


def relation_key(relation: dict[str, Any], order: int, factor_count: int) -> tuple[tuple[int, ...], int]:
    coeffs = factor_bank.pad([int_value(value) % order for value in relation.get("canonical_coeffs") or []], factor_count)
    return tuple(coeffs), int_value(relation.get("canonical_rhs")) % order


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


def quotient_bank_summary(relations: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    status_counts = Counter(str(relation.get("relation_status")) for relation in relations)
    role_counts = Counter(str(relation.get("pair_role")) for relation in relations)
    rows_by_key: dict[tuple[tuple[int, ...], int], dict[str, Any]] = {}
    for relation in relations:
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        key = relation_key(relation, order, factor_count)
        rows_by_key.setdefault(
            key,
            {
                "canonical_coeffs": list(key[0]),
                "canonical_rhs": key[1],
                "example_pair": relation.get("pair"),
                "factor_support": relation.get("factor_support"),
                "factor_support_size": relation.get("factor_support_size"),
                "multiplicity": 0,
                "pair_roles": [],
                "public_fingerprints": [],
            },
        )
        rows_by_key[key]["multiplicity"] += 1
        rows_by_key[key]["pair_roles"].append(relation.get("pair_role"))
        rows_by_key[key]["public_fingerprints"].append(relation.get("public_fingerprint"))
    unique_rows = list(rows_by_key.values())
    for row in unique_rows:
        row["pair_roles"] = sorted({str(value) for value in row.get("pair_roles") or []})
        row["public_fingerprints"] = sorted({str(value) for value in row.get("public_fingerprints") or []})
    matrix = [row["canonical_coeffs"] for row in unique_rows]
    rhs = [int_value(row["canonical_rhs"]) % order for row in unique_rows]
    rank = p1023.rank_mod(matrix, order)
    augmented = p1023.rank_mod([row + [rhs[index]] for index, row in enumerate(matrix)], order)
    return {
        "augmented_rank": augmented["rank"],
        "factor_count": factor_count,
        "factor_relation_count": sum(1 for relation in relations if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"),
        "matrix_consistent": augmented["rank"] == rank["rank"],
        "nonunit_pivot_candidate_count": rank["nonunit_pivot_candidate_count"],
        "pair_role_counts": dict(sorted(role_counts.items())),
        "rank": rank["rank"],
        "rank_deficiency": max(0, factor_count - rank["rank"]),
        "relation_status_counts": dict(sorted(status_counts.items())),
        "unique_factor_relation_count": len(unique_rows),
        "unique_relation_samples": unique_rows[:12],
    }


def marginal_rank_gain(base_relations: list[dict[str, Any]], candidate_relations: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    base = quotient_bank_summary(base_relations, order, factor_count)
    combined = quotient_bank_summary([*base_relations, *candidate_relations], order, factor_count)
    return {
        "base_rank": base["rank"],
        "candidate_relation_count": sum(1 for relation in candidate_relations if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"),
        "combined_rank": combined["rank"],
        "matrix_consistent": combined["matrix_consistent"],
        "rank_gain": combined["rank"] - base["rank"],
        "unique_candidate_relation_count": quotient_bank_summary(candidate_relations, order, factor_count)["unique_factor_relation_count"],
    }


def group_summary(public: str, forms: list[dict[str, Any]], order: int) -> dict[str, Any]:
    unique = p1023.unique_forms(forms)
    calibration_forms = [
        form for form in unique if "positive_calibration" in split_set(form)
    ]
    validation_forms = [
        form for form in unique if "validation" in split_set(form)
    ]
    combined_relations, factor_count = target_eliminated_relations(unique, order, public)
    calibration_relations, _ = target_eliminated_relations(calibration_forms, order, public)
    validation_relations = [
        relation
        for relation in combined_relations
        if relation.get("pair_role") in {"mixed_calibration_validation_pair", "validation_pair"}
    ]
    calibration_bank = quotient_bank_summary(calibration_relations, order, factor_count)
    combined_bank = quotient_bank_summary(combined_relations, order, factor_count)
    gain = marginal_rank_gain(calibration_relations, validation_relations, order, factor_count)
    return {
        "calibration_bank": calibration_bank,
        "calibration_unique_form_count": len(calibration_forms),
        "combined_bank": combined_bank,
        "combined_unique_form_count": len(unique),
        "focus_candidate": public in parse_focus_publics(DEFAULT_FOCUS_PUBLICS),
        "marginal_validation_gain": gain,
        "public_fingerprint": public,
        "validation_or_mixed_relation_count": len(validation_relations),
        "validation_unique_form_count": len(validation_forms),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    all_windows = [
        *p1022.POSITIVE_CALIBRATION_WINDOWS,
        *p1022.NEGATIVE_CALIBRATION_WINDOWS,
        *p1022.VALIDATION_WINDOWS,
    ]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    positive_rows = p1023.selected_rows_for(p1022.POSITIVE_CALIBRATION_WINDOWS, by_window, "positive_calibration")
    negative_rows = p1023.selected_rows_for(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control")
    validation_rows = p1023.selected_rows_for(p1022.VALIDATION_WINDOWS, by_window, "validation")
    selected = [*positive_rows, *validation_rows]
    selected_by_case = {p1023.row_case_id(row): row for row in selected}
    reconstructed, verifier, built_by_row = p1005.p1003.reconstruct_selected(selected)
    del verifier
    forms = p1023.annotated_form_records(reconstructed, built_by_row, selected_by_case)
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    order = form_orders[0] if len(form_orders) == 1 else 0
    forms_by_public: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_public[str(form.get("public_fingerprint"))].append(form)
    focus_publics = parse_focus_publics(args.focus_publics)
    group_summaries = [
        group_summary(public, group_forms, order)
        for public, group_forms in sorted(forms_by_public.items())
        if len(p1023.unique_forms(group_forms)) >= 2
    ]
    for group in group_summaries:
        group["focus_candidate"] = group["public_fingerprint"] in focus_publics
    all_calibration_relations: list[dict[str, Any]] = []
    all_validation_relations: list[dict[str, Any]] = []
    factor_count = 0
    for public, group_forms in sorted(forms_by_public.items()):
        unique = p1023.unique_forms(group_forms)
        group_factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique] or [0])
        factor_count = max(factor_count, group_factor_count)
        calibration_forms = [form for form in unique if "positive_calibration" in split_set(form)]
        calibration_relations, _ = target_eliminated_relations(calibration_forms, order, public)
        combined_relations, _ = target_eliminated_relations(unique, order, public)
        validation_relations = [
            relation
            for relation in combined_relations
            if relation.get("pair_role") in {"mixed_calibration_validation_pair", "validation_pair"}
        ]
        all_calibration_relations.extend(calibration_relations)
        all_validation_relations.extend(validation_relations)
    global_gain = marginal_rank_gain(all_calibration_relations, all_validation_relations, order, factor_count)
    global_calibration_bank = quotient_bank_summary(all_calibration_relations, order, factor_count)
    global_combined_bank = quotient_bank_summary([*all_calibration_relations, *all_validation_relations], order, factor_count)
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    focus_groups = [group for group in group_summaries if group.get("focus_candidate")]
    focus_positive_groups = [
        group
        for group in focus_groups
        if int_value((group.get("marginal_validation_gain") or {}).get("rank_gain")) > 0
        and bool((group.get("marginal_validation_gain") or {}).get("matrix_consistent"))
    ]
    primary_success = global_gain["rank_gain"] > 0 and bool(global_gain["matrix_consistent"])
    secondary_success = bool(focus_positive_groups)
    if negative_rows:
        claim = "NEGATIVE_RESULT_P1024_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif len(positive_rows) != 10 or len(validation_rows) != 4:
        claim = "NEGATIVE_RESULT_P1024_UNEXPECTED_P1022_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1024_RECONSTRUCTION_ERRORS"
    elif len(form_orders) != 1:
        claim = "NEGATIVE_RESULT_P1024_INCONSISTENT_FORM_ORDERS"
    elif global_combined_bank["factor_relation_count"] == 0:
        claim = "NEGATIVE_RESULT_P1024_NO_TARGET_ELIMINATED_FACTOR_RELATIONS"
    elif primary_success:
        claim = "P1024_TARGET_ELIMINATED_FACTOR_RANK_GAIN"
    elif secondary_success:
        claim = (
            "P1024_SAME_PUBLIC_QUOTIENT_RANK_GAIN_GLOBAL_PLATEAU"
            if global_combined_bank["matrix_consistent"]
            else "P1024_SAME_PUBLIC_QUOTIENT_RANK_GAIN_GLOBAL_INCONSISTENT_PLATEAU"
        )
    elif not global_combined_bank["matrix_consistent"]:
        claim = "NEGATIVE_RESULT_P1024_TARGET_ELIMINATED_ROWS_INCONSISTENT"
    else:
        claim = "NEGATIVE_RESULT_P1024_TARGET_ELIMINATED_GLOBAL_PLATEAU"
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
            "p1023_dependency_sha256": p1005.sha256_file(Path(p1023.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1024_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "INDEX-CALCULUS PRECURSOR: quotient rows are factor-bank evidence, not sparse linear algebra closure or target descent.",
            "CONTEXT BOUNDARY: target elimination is performed only inside same-public groups before quotient rows are pooled.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; quotient rank gain is not an end-to-end faster-than-rho solver.",
        ],
        "parameters": {
            "focus_publics": focus_publics,
            "fresh_validation_windows": p1022.VALIDATION_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "positive_calibration_windows": p1022.POSITIVE_CALIBRATION_WINDOWS,
            "primary_rule": p1022.PRIMARY_RULE_NAME,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {
            "exists": exists,
        },
        "summary": {
            "factor_count": factor_count,
            "focus_positive_group_count": len(focus_positive_groups),
            "focus_positive_groups": focus_positive_groups,
            "form_order": order,
            "form_orders": form_orders,
            "global_calibration_bank": global_calibration_bank,
            "global_combined_bank": global_combined_bank,
            "global_validation_marginal_gain": global_gain,
            "negative_control_selected_count": len(negative_rows),
            "positive_calibration_selected_count": len(positive_rows),
            "primary_success": primary_success,
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "secondary_success": secondary_success,
            "selected_count": len(selected),
            "validation_selected_count": len(validation_rows),
        },
        "group_summaries": sorted(
            group_summaries,
            key=lambda group: (
                0 if group.get("focus_candidate") else 1,
                -int_value((group.get("marginal_validation_gain") or {}).get("rank_gain")),
                str(group.get("public_fingerprint")),
            ),
        ),
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--focus-publics", default=DEFAULT_FOCUS_PUBLICS, help="Semicolon-separated public fingerprints")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} negative={negative} quotient_rank={rank}/{factors} "
        "calibration_rank={cal_rank} rank_gain={gain} focus_positive={focus} consistent={consistent} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            negative=summary["negative_control_selected_count"],
            rank=summary["global_combined_bank"]["rank"],
            factors=summary["factor_count"],
            cal_rank=summary["global_calibration_bank"]["rank"],
            gain=summary["global_validation_marginal_gain"]["rank_gain"],
            focus=summary["focus_positive_group_count"],
            consistent=summary["global_combined_bank"]["matrix_consistent"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
