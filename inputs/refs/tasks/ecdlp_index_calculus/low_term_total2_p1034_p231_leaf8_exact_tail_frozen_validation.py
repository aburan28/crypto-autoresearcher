#!/usr/bin/env python3
"""P1034 frozen validation for the P1033 leaf-8 exact-tail signal."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1029_p231_motif_neighbor_scout as p1029
import low_term_total2_p1030_p231_representation_change_audit as p1030
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1034_p231_leaf8_exact_tail_frozen_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation.v1"
SIGNAL_WINDOW = "12440_12447"
FROZEN_TERMS = [8, 8, 11, 11]
FROZEN_TAIL_SUPPORT = [9, 12]

ObjectKeyFn = Callable[[dict[str, Any]], Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def form_window(form: dict[str, Any]) -> str:
    return str(form.get("window") or "")


def form_split(form: dict[str, Any]) -> str:
    return str(form.get("split") or "")


def public_key(form: dict[str, Any]) -> str:
    return p1033.public_key(form)


def compact_form(index: int, form: dict[str, Any], factor_count: int) -> dict[str, Any]:
    return p1033.compact_form(index, form, factor_count)


def validation_windows() -> list[str]:
    return [window for window in p1025.FRESH_WINDOWS if window > SIGNAL_WINDOW]


def selected_forms(args: argparse.Namespace, compressed: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scope_rows, exists = p1030.build_scopes(args)
    leaf8_rows = scope_rows.get("leaf8_neighbor", [])
    rows = p1029.dedupe_by_row_signature(leaf8_rows) if compressed else leaf8_rows
    reconstructed, forms = p1025.reconstruct_partition(rows)
    unique_or_raw = p1023.unique_forms(forms) if compressed else forms
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique_or_raw] or [0])
    return unique_or_raw, {
        "compressed": compressed,
        "exists": exists,
        "factor_count": factor_count,
        "form_count": len(forms),
        "input_row_count": len(rows),
        "leaf8_selected_count": len(leaf8_rows),
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
        "unique_form_count": len(p1023.unique_forms(forms)),
    }


def matches_frozen_policy(form: dict[str, Any]) -> bool:
    return (
        form_split(form) == "fresh_validation"
        and [int_value(value) for value in form.get("terms") or []] == FROZEN_TERMS
        and [int_value(value) for value in form.get("tail_support") or []] == FROZEN_TAIL_SUPPORT
    )


def exact_tail_key(form: dict[str, Any]) -> Any:
    return ("exact_tail", str(form.get("exact_tail_expression_key") or ""))


def motif_key(form: dict[str, Any]) -> Any:
    return ("motif", str(form.get("motif_key") or ""))


def object_specs() -> list[dict[str, Any]]:
    return [
        {"name": "exact_tail", "key_fn": exact_tail_key},
        {"name": "motif", "key_fn": motif_key},
    ]


def evaluate_object(
    forms: list[dict[str, Any]],
    factor_count: int,
    windows: list[str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, form in enumerate(forms):
        if form_window(form) not in windows or not matches_frozen_policy(form):
            continue
        key = (public_key(form), form_window(form), json_key(spec["key_fn"](form)))
        groups[key].append((index, form))
    evaluated_groups = []
    prediction_count = 0
    true_count = 0
    false_count = 0
    no_pair_group_count = 0
    eligible_form_count = sum(len(group) for group in groups.values())
    for (public, window, object_key), group in sorted(groups.items()):
        q_values = sorted({int_value((form.get("coeffs") or [0])[0]) for _index, form in group})
        predictions = []
        if len(group) < 2 or len(q_values) < 2:
            no_pair_group_count += 1
        for left_offset, (left_index, left) in enumerate(group):
            for right_index, right in group[left_offset + 1 :]:
                predicted = p1033.derive_target_from_pair(left, right, factor_count)
                if predicted is None:
                    continue
                secrets = sorted(
                    {
                        int_value(value)
                        for value in [left.get("source_secret"), right.get("source_secret")]
                        if value is not None
                    }
                )
                verified = bool(secrets and all(predicted == secret for secret in secrets))
                prediction_count += 1
                if verified:
                    true_count += 1
                else:
                    false_count += 1
                predictions.append(
                    {
                        "left": compact_form(left_index, left, factor_count),
                        "predicted_target": predicted,
                        "right": compact_form(right_index, right, factor_count),
                        "source_secrets": secrets,
                        "toy_secret_verified": verified,
                    }
                )
        evaluated_groups.append(
            {
                "eligible_form_count": len(group),
                "object_key": object_key,
                "predictions": predictions,
                "public_fingerprint": public,
                "q_values": q_values,
                "window": window,
            }
        )
    return {
        "eligible_form_count": eligible_form_count,
        "false_count": false_count,
        "group_count": len(groups),
        "groups": evaluated_groups,
        "model": spec["name"],
        "no_pair_group_count": no_pair_group_count,
        "prediction_count": prediction_count,
        "true_count": true_count,
        "validation_success": bool(prediction_count > 0 and false_count == 0),
    }


def evaluate_partition(forms: list[dict[str, Any]], meta: dict[str, Any], windows: list[str], label: str) -> dict[str, Any]:
    factor_count = int_value(meta.get("factor_count"))
    object_results = [evaluate_object(forms, factor_count, windows, spec) for spec in object_specs()]
    return {
        "label": label,
        "meta": meta,
        "object_results": object_results,
        "summary": {
            "eligible_form_count": sum(int_value(result.get("eligible_form_count")) for result in object_results),
            "false_count": sum(int_value(result.get("false_count")) for result in object_results),
            "group_count": sum(int_value(result.get("group_count")) for result in object_results),
            "no_pair_group_count": sum(int_value(result.get("no_pair_group_count")) for result in object_results),
            "prediction_count": sum(int_value(result.get("prediction_count")) for result in object_results),
            "true_count": sum(int_value(result.get("true_count")) for result in object_results),
            "validation_success": any(result.get("validation_success") for result in object_results),
            "windows": windows,
        },
    }


def determine_claim(raw_validation: dict[str, Any], compressed_validation: dict[str, Any], controls: list[dict[str, Any]]) -> str:
    if any(int_value(control["summary"].get("false_count")) for control in controls):
        return "NEGATIVE_RESULT_P1034_SCOUT_CONTROL_FAILED"
    if raw_validation["summary"]["validation_success"] or compressed_validation["summary"]["validation_success"]:
        return "P1034_FROZEN_EXACT_TAIL_VALIDATION_SIGNAL"
    if int_value(raw_validation["summary"].get("eligible_form_count")) or int_value(
        compressed_validation["summary"].get("eligible_form_count")
    ):
        return "NEGATIVE_RESULT_P1034_NO_LATER_ELIGIBLE_PAIR"
    return "NEGATIVE_RESULT_P1034_NO_LATER_ELIGIBLE_FORMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    raw_forms, raw_meta = selected_forms(args, compressed=False)
    compressed_forms, compressed_meta = selected_forms(args, compressed=True)
    later_windows = validation_windows()
    raw_control = evaluate_partition(raw_forms, raw_meta, [SIGNAL_WINDOW], "raw_scout_control")
    compressed_control = evaluate_partition(compressed_forms, compressed_meta, [SIGNAL_WINDOW], "compressed_scout_control")
    raw_validation = evaluate_partition(raw_forms, raw_meta, later_windows, "raw_later_validation")
    compressed_validation = evaluate_partition(
        compressed_forms,
        compressed_meta,
        later_windows,
        "compressed_later_validation",
    )
    claim = determine_claim(raw_validation, compressed_validation, [raw_control, compressed_control])
    all_windows = [
        *p1022.POSITIVE_CALIBRATION_WINDOWS,
        *p1022.VALIDATION_WINDOWS,
        *p1022.NEGATIVE_CALIBRATION_WINDOWS,
        *p1025.FRESH_WINDOWS,
    ]
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
            "p1033_dependency_sha256": p1005.sha256_file(Path(p1033.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1034_") else "NEGATIVE RESULT",
        "compressed_later_validation": compressed_validation,
        "compressed_scout_control": compressed_control,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-POLICY: P1034 only validates the exact P1033 same-window fresh exact-tail/motif policy.",
            "SUPPLY-NEGATIVE: no later eligible pair is not an algebraic disproof.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "frozen_tail_support": FROZEN_TAIL_SUPPORT,
            "frozen_terms": FROZEN_TERMS,
            "later_validation_windows": later_windows,
            "signal_window": SIGNAL_WINDOW,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "raw_later_validation": raw_validation,
        "raw_scout_control": raw_control,
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "compressed_later": compressed_validation["summary"],
            "compressed_scout_control": compressed_control["summary"],
            "raw_later": raw_validation["summary"],
            "raw_scout_control": raw_control["summary"],
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(
        "claim={claim} raw_later_pred={raw_pred} raw_later_eligible={raw_eligible} "
        "compressed_later_pred={comp_pred} out={out}".format(
            claim=payload["claim_status"],
            raw_pred=payload["summary"]["raw_later"]["prediction_count"],
            raw_eligible=payload["summary"]["raw_later"]["eligible_form_count"],
            comp_pred=payload["summary"]["compressed_later"]["prediction_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
