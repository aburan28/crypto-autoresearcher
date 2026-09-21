#!/usr/bin/env python3
"""P1023 relation-bank audit for the P1022 leaf-19 selected forms."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1020_p231_leaf19_saltgap_precision_12256 as p1020
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1023_p231_leaf19_relation_bank_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1023_p231_leaf19_relation_bank_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1023_p231_leaf19_relation_bank_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def round8(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def pad(values: list[int], width: int) -> list[int]:
    if len(values) >= width:
        return values[:]
    return values + [0] * (width - len(values))


def rank_mod(matrix: list[list[int]], modulus: int) -> dict[str, Any]:
    if not matrix or not modulus:
        return {"rank": 0, "nonunit_pivot_candidate_count": 0}
    width = max(len(row) for row in matrix)
    rows = [[int_value(value) % modulus for value in pad(row, width)] for row in matrix]
    rank = 0
    nonunit = 0
    for col in range(width):
        pivot = None
        for row in range(rank, len(rows)):
            value = rows[row][col] % modulus
            if value == 0:
                continue
            if math.gcd(value, modulus) == 1:
                pivot = row
                break
            nonunit += 1
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col] % modulus, -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank:
                continue
            factor = rows[row][col] % modulus
            if factor:
                rows[row] = [(left - factor * right) % modulus for left, right in zip(rows[row], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return {"rank": rank, "nonunit_pivot_candidate_count": nonunit}


def selected_ops(row: dict[str, Any]) -> float:
    try:
        return float(p1005.selected_ops(row))
    except (AttributeError, TypeError, ValueError):
        return float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0)


def selected_rows_for(
    windows: list[str],
    by_window: dict[str, list[dict[str, Any]]],
    split: str,
) -> list[dict[str, Any]]:
    factory = p1022.rank_guard_rule()["factory"]
    selected: list[dict[str, Any]] = []
    for window in windows:
        rows = by_window.get(window) or []
        predicate = factory(rows)
        for row in rows:
            if predicate(row):
                selected_row = dict(row)
                selected_row["_p1023_split"] = split
                selected_row["_p1023_window"] = window
                selected.append(selected_row)
    return selected


def row_case_id(row: dict[str, Any]) -> str:
    return str(row.get("case_id"))


def form_key(form: dict[str, Any]) -> str:
    return json_key(
        {
            "coeffs": [int_value(value) for value in form.get("coeffs") or []],
            "order": int_value(form.get("order")),
            "rhs": int_value(form.get("rhs")),
            "terms": [int_value(value) for value in form.get("terms") or []],
        }
    )


def coeff_key(form: dict[str, Any]) -> str:
    return json_key(
        {
            "coeffs": [int_value(value) for value in form.get("coeffs") or []],
            "order": int_value(form.get("order")),
        }
    )


def public_key(value: Any) -> str:
    if isinstance(value, list):
        return json_key([int_value(item) for item in value])
    if isinstance(value, tuple):
        return json_key([int_value(item) for item in value])
    return json_key(value)


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    source_case = row.get("source_case") or {}
    features = row.get("features") or {}
    return {
        "case_id": row.get("case_id"),
        "label_positive": row.get("label_positive"),
        "leaf_selector": features.get("leaf_selector"),
        "row_key_signature": p1005.p996.row_key_signature(row),
        "salt_gap": features.get("salt_gap"),
        "selected_ops_over_rho": round8(selected_ops(row)),
        "source_rank": source_case.get("source_rank"),
        "split": row.get("_p1023_split"),
        "top_k": features.get("top_k"),
        "transfer_index": source_case.get("transfer_index"),
        "unique_leaf_indices": features.get("unique_leaf_indices"),
        "window": row.get("_p1023_window") or row.get("window"),
    }


def annotated_form_records(
    reconstructed: list[dict[str, Any]],
    built_by_row: dict[str, dict[str, Any]],
    selected_by_case: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for case in reconstructed:
        selected = selected_by_case.get(str(case.get("case_id"))) or {}
        split = str(selected.get("_p1023_split") or "unknown")
        window = str(selected.get("_p1023_window") or case.get("window") or "")
        for form in case.get("form_records") or []:
            row_key = str(form.get("row_key"))
            built = built_by_row.get(row_key) or {}
            record = dict(form)
            record["challenge_seed"] = built.get("challenge_seed")
            record["public"] = built.get("public")
            record["public_fingerprint"] = public_key(built.get("public"))
            record["source_secret"] = built.get("secret")
            record["split"] = split
            record["window"] = window
            records.append(record)
    return records


def unique_forms(forms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for form in forms:
        key = form_key(form)
        if key not in by_key:
            by_key[key] = dict(form)
            by_key[key]["multiplicity"] = 0
            by_key[key]["case_ids"] = []
            by_key[key]["public_fingerprints"] = []
            by_key[key]["row_keys"] = []
            by_key[key]["splits"] = []
            by_key[key]["windows"] = []
        entry = by_key[key]
        entry["multiplicity"] += 1
        entry["case_ids"].append(form.get("case_id"))
        entry["public_fingerprints"].append(form.get("public_fingerprint"))
        entry["row_keys"].append(form.get("row_key"))
        entry["splits"].append(form.get("split"))
        entry["windows"].append(form.get("window"))
    for entry in by_key.values():
        for field in ("case_ids", "public_fingerprints", "row_keys", "splits", "windows"):
            entry[field] = sorted({str(value) for value in entry.get(field) or []})
    return list(by_key.values())


def rank_summary(forms: list[dict[str, Any]], order: int) -> dict[str, Any]:
    unique = unique_forms(forms)
    width = max([len(form.get("coeffs") or []) for form in unique], default=0)
    coeff_matrix = [pad([int_value(value) for value in form.get("coeffs") or []], width) for form in unique]
    augmented_matrix = [row + [int_value(form.get("rhs"))] for row, form in zip(coeff_matrix, unique)]
    coeff_rank = rank_mod(coeff_matrix, order)
    augmented_rank = rank_mod(augmented_matrix, order)
    coeff_rhs: dict[str, set[int]] = defaultdict(set)
    for form in unique:
        coeff_rhs[coeff_key(form)].add(int_value(form.get("rhs")) % order if order else int_value(form.get("rhs")))
    rhs_collision_count = sum(1 for values in coeff_rhs.values() if len(values) > 1)
    return {
        "augmented_rank": augmented_rank["rank"],
        "coefficient_column_count": width,
        "coefficient_rank": coeff_rank["rank"],
        "coefficient_rank_deficiency": max(0, width - coeff_rank["rank"]),
        "coefficient_rhs_collision_count": rhs_collision_count,
        "consistent_augmented_system": augmented_rank["rank"] == coeff_rank["rank"],
        "form_count": len(forms),
        "nonunit_pivot_candidate_count": coeff_rank["nonunit_pivot_candidate_count"],
        "unique_form_count": len(unique),
    }


def split_rank_summaries(forms: list[dict[str, Any]], order: int) -> dict[str, dict[str, Any]]:
    out = {}
    for split in sorted({str(form.get("split")) for form in forms}):
        out[split] = rank_summary([form for form in forms if form.get("split") == split], order)
    return out


def public_group_summaries(forms: list[dict[str, Any]], order: int) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        grouped[str(form.get("public_fingerprint"))].append(form)
    summaries = []
    for public, group in grouped.items():
        splits = sorted({str(form.get("split")) for form in group})
        calibration = [form for form in group if form.get("split") == "positive_calibration"]
        combined = group
        cal_rank = rank_summary(calibration, order)
        combined_rank = rank_summary(combined, order)
        summaries.append(
            {
                "calibration_coefficient_rank": cal_rank["coefficient_rank"],
                "combined_coefficient_rank": combined_rank["coefficient_rank"],
                "form_count": len(group),
                "public_fingerprint": public,
                "rank_gain_after_validation": combined_rank["coefficient_rank"] - cal_rank["coefficient_rank"],
                "splits": splits,
                "spans_calibration_and_validation": "positive_calibration" in splits and "validation" in splits,
                "unique_form_count": combined_rank["unique_form_count"],
            }
        )
    return sorted(summaries, key=lambda item: (-int_value(item.get("rank_gain_after_validation")), -int_value(item.get("unique_form_count")), str(item.get("public_fingerprint"))))


def cumulative_rank_trace(selected: list[dict[str, Any]], forms_by_case: dict[str, list[dict[str, Any]]], order: int) -> list[dict[str, Any]]:
    frozen_order = p1020.fixed_order()
    ordered = sorted(selected, key=frozen_order["key"])
    seen: dict[str, dict[str, Any]] = {}
    cumulative_ops = 0.0
    trace = []
    for index, row in enumerate(ordered, start=1):
        before = rank_summary(list(seen.values()), order)
        new_forms = 0
        for form in forms_by_case.get(row_case_id(row), []):
            key = form_key(form)
            if key not in seen:
                seen[key] = form
                new_forms += 1
        cumulative_ops += selected_ops(row)
        after = rank_summary(list(seen.values()), order)
        trace.append(
            {
                "case_id": row.get("case_id"),
                "cumulative_ops_over_rho": round8(cumulative_ops),
                "coefficient_rank_after": after["coefficient_rank"],
                "coefficient_rank_before": before["coefficient_rank"],
                "new_unique_forms": new_forms,
                "ordered_index": index,
                "rank_gain": after["coefficient_rank"] - before["coefficient_rank"],
                "selected_ops_over_rho": round8(selected_ops(row)),
                "split": row.get("_p1023_split"),
                "window": row.get("_p1023_window") or row.get("window"),
            }
        )
    return trace


def compact_form(form: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_ids": form.get("case_ids"),
        "coeffs": form.get("coeffs"),
        "multiplicity": form.get("multiplicity"),
        "order": form.get("order"),
        "public_fingerprints": form.get("public_fingerprints"),
        "rhs": form.get("rhs"),
        "row_keys": form.get("row_keys"),
        "splits": form.get("splits"),
        "support": form.get("support"),
        "terms": form.get("terms"),
        "windows": form.get("windows"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    all_windows = [
        *p1022.POSITIVE_CALIBRATION_WINDOWS,
        *p1022.NEGATIVE_CALIBRATION_WINDOWS,
        *p1022.VALIDATION_WINDOWS,
    ]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    positive_rows = selected_rows_for(p1022.POSITIVE_CALIBRATION_WINDOWS, by_window, "positive_calibration")
    negative_rows = selected_rows_for(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control")
    validation_rows = selected_rows_for(p1022.VALIDATION_WINDOWS, by_window, "validation")
    selected = [*positive_rows, *validation_rows]
    selected_by_case = {row_case_id(row): row for row in selected}

    reconstructed, verifier, built_by_row = p1005.p1003.reconstruct_selected(selected)
    del verifier
    forms = annotated_form_records(reconstructed, built_by_row, selected_by_case)
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    order = form_orders[0] if len(form_orders) == 1 else 0
    forms_by_case: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_case[str(form.get("case_id"))].append(form)

    calibration_forms = [form for form in forms if form.get("split") == "positive_calibration"]
    validation_forms = [form for form in forms if form.get("split") == "validation"]
    calibration_rank = rank_summary(calibration_forms, order)
    validation_rank = rank_summary(validation_forms, order)
    global_rank = rank_summary(forms, order)
    validation_over_calibration_rank_gain = global_rank["coefficient_rank"] - calibration_rank["coefficient_rank"]
    calibration_keys = {form_key(form) for form in calibration_forms}
    validation_keys = {form_key(form) for form in validation_forms}
    public_groups = public_group_summaries(forms, order)
    same_public_positive_gains = [
        group for group in public_groups if group["spans_calibration_and_validation"] and int_value(group["rank_gain_after_validation"]) > 0
    ]
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    primary_success = validation_over_calibration_rank_gain > 0 and bool(same_public_positive_gains)
    raw_global_positive = validation_over_calibration_rank_gain > 0
    context_local_positive = bool(same_public_positive_gains)
    claim = "P1023_RELATION_BANK_RANK_GAIN_CONTEXT_REUSABLE"
    if negative_rows:
        claim = "NEGATIVE_RESULT_P1023_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif len(positive_rows) != 10 or len(validation_rows) != 4:
        claim = "NEGATIVE_RESULT_P1023_UNEXPECTED_P1022_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1023_RECONSTRUCTION_ERRORS"
    elif len(form_orders) != 1:
        claim = "NEGATIVE_RESULT_P1023_INCONSISTENT_FORM_ORDERS"
    elif not validation_keys - calibration_keys:
        claim = "NEGATIVE_RESULT_P1023_VALIDATION_ADDS_NO_NOVEL_FORMS"
    elif primary_success:
        claim = "P1023_RELATION_BANK_RANK_GAIN_CONTEXT_REUSABLE"
    elif raw_global_positive:
        claim = "P1023_RELATION_BANK_RANK_GAIN_CONTEXT_GLUE_OPEN"
    elif context_local_positive:
        claim = "P1023_CONTEXT_LOCAL_RANK_GAIN_GLOBAL_BANK_PLATEAU"
    else:
        claim = "NEGATIVE_RESULT_P1023_VALIDATION_ADDS_NO_RELATION_BANK_RANK"

    unique = unique_forms(forms)
    duplicate_forms = [form for form in unique if int_value(form.get("multiplicity")) > 1]
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
            "p1022_dependency_sha256": p1005.sha256_file(Path(p1022.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1023_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "INDEX-CALCULUS PRECURSOR: this audits relation-bank rank contribution, not full sparse linear algebra or target descent.",
            "CONTEXT BOUNDARY: raw global rank is reported separately from same-public cross-split rank gain.",
            "RHO BOUNDARY: selected cost is compared with Pollard rho, but relation-bank rank gain is not an end-to-end faster-than-rho solver.",
        ],
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "fresh_validation_windows": p1022.VALIDATION_WINDOWS,
            "frozen_order": p1020.fixed_order()["name"],
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
            "calibration_rank": calibration_rank,
            "duplicate_unique_form_count": len(duplicate_forms),
            "form_order": order,
            "form_orders": form_orders,
            "global_rank": global_rank,
            "negative_control_selected_count": len(negative_rows),
            "positive_calibration_selected_count": len(positive_rows),
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "same_public_positive_rank_gain_count": len(same_public_positive_gains),
            "same_public_positive_rank_gains": same_public_positive_gains[:10],
            "success_flags": {
                "context_local_positive": context_local_positive,
                "primary_success": primary_success,
                "raw_global_positive": raw_global_positive,
            },
            "selected_count": len(selected),
            "split_rank_summaries": split_rank_summaries(forms, order),
            "unique_form_count": len(unique),
            "validation_novel_unique_form_count": len(validation_keys - calibration_keys),
            "validation_over_calibration_rank_gain": validation_over_calibration_rank_gain,
            "validation_rank": validation_rank,
            "validation_selected_count": len(validation_rows),
        },
        "selected_rows": [compact_row(row) for row in selected],
        "negative_control_selected_rows": [compact_row(row) for row in negative_rows],
        "rank_trace": cumulative_rank_trace(selected, forms_by_case, order),
        "public_group_summaries": public_groups,
        "duplicate_forms": [compact_form(form) for form in duplicate_forms[:25]],
        "top_unique_forms": [compact_form(form) for form in unique[:25]],
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline retained for P1022 comparability")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
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
        "claim={claim} selected={selected} negative={negative} forms={forms} "
        "global_rank={rank}/{cols} validation_rank_gain={gain} same_public_gains={same_public} "
        "validation_novel_forms={novel} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            negative=summary["negative_control_selected_count"],
            forms=summary["unique_form_count"],
            rank=summary["global_rank"]["coefficient_rank"],
            cols=summary["global_rank"]["coefficient_column_count"],
            gain=summary["validation_over_calibration_rank_gain"],
            same_public=summary["same_public_positive_rank_gain_count"],
            novel=summary["validation_novel_unique_form_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
