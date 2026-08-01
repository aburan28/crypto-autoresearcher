#!/usr/bin/env python3
"""P1033 leaf-8 factor-label extraction scout after P1032."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026
import low_term_total2_p1029_p231_motif_neighbor_scout as p1029
import low_term_total2_p1030_p231_representation_change_audit as p1030


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1033_p231_leaf8_factor_label_extraction_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout.v1"
ORDER = p1026.ORDER
SALT_RE = re.compile(r"salt(\d+)")

FactorLabelFn = Callable[[int, dict[str, Any], int, int], Any]
ObjectKeyFn = Callable[[dict[str, Any], int], Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def round8(value: float | None) -> float | None:
    return p1023.round8(value)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def pad(values: list[int], width: int) -> list[int]:
    return values + [0] * max(0, width - len(values))


def rank_mod(matrix: list[list[int]]) -> int:
    return p1030.rank_mod(matrix, ORDER)


def matrix_summary(rows: list[list[int]], rhs: list[int]) -> dict[str, Any]:
    return p1030.matrix_summary(rows, rhs, ORDER)


def parse_public(public_fingerprint: str) -> tuple[int, int]:
    return p1030.parse_public(public_fingerprint)


def form_parts(form: dict[str, Any], factor_count: int) -> tuple[int, list[int], int]:
    coeffs = [int_value(value) % ORDER for value in form.get("coeffs") or []]
    q_coeff = coeffs[0] if coeffs else 0
    factors = pad(coeffs[1:], factor_count)
    rhs = int_value(form.get("rhs")) % ORDER
    return q_coeff, factors, rhs


def row_keys(form: dict[str, Any]) -> tuple[str, ...]:
    values = tuple(str(value) for value in form.get("row_keys") or [] if str(value))
    if values:
        return values
    row_key = str(form.get("row_key") or "")
    return (row_key,) if row_key else ("missing-row-key",)


def salt_tuple(form: dict[str, Any]) -> tuple[Any, ...]:
    salts = []
    for key in row_keys(form):
        salts.extend(int(match.group(1)) for match in SALT_RE.finditer(key))
    return tuple(sorted(salts)) or ("none",)


def public_key(form: dict[str, Any]) -> str:
    return str(form.get("public_fingerprint") or "missing-public")


def public_x_key(form: dict[str, Any]) -> str:
    x, _y = parse_public(public_key(form))
    return f"x:{x}"


def support_tuple(form: dict[str, Any], factor_count: int) -> tuple[int, ...]:
    _q, factors, _rhs = form_parts(form, factor_count)
    return tuple(index for index, coeff in enumerate(factors) if coeff % ORDER)


def coeff_class(coeff: int) -> int:
    coeff %= ORDER
    return min(coeff, (-coeff) % ORDER)


def nonzero_factor_entries(form: dict[str, Any], factor_count: int) -> list[tuple[int, int]]:
    _q, factors, _rhs = form_parts(form, factor_count)
    return [(index, coeff) for index, coeff in enumerate(factors) if coeff % ORDER]


def factor_model_specs() -> list[dict[str, Any]]:
    return [
        {
            "description": "Negative control: global term labels.",
            "label_fn": lambda _n, _form, index, _coeff: ("term", index),
            "name": "negative_global_term",
            "primary_eligible": False,
        },
        {
            "description": "Term plus signed coefficient.",
            "label_fn": lambda _n, _form, index, coeff: ("term_coeff", index, coeff % ORDER),
            "name": "term_coeff",
            "primary_eligible": True,
        },
        {
            "description": "Term plus signless coefficient.",
            "label_fn": lambda _n, _form, index, coeff: ("term_abscoeff", index, coeff_class(coeff)),
            "name": "term_abscoeff",
            "primary_eligible": True,
        },
        {
            "description": "Public fingerprint plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("public", public_key(form), index),
            "name": "public_term",
            "primary_eligible": True,
        },
        {
            "description": "x-only Kummer class plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("x", public_x_key(form), index),
            "name": "kummer_x_term",
            "primary_eligible": True,
        },
        {
            "description": "Row-key plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("row", row_keys(form), index),
            "name": "row_term",
            "primary_eligible": True,
        },
        {
            "description": "Salt plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("salt", salt_tuple(form), index),
            "name": "salt_term",
            "primary_eligible": True,
        },
        {
            "description": "Exact nonzero support plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("support", support_tuple(form, 16), index),
            "name": "support_term",
            "primary_eligible": True,
        },
        {
            "description": "Tail support plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("tail_support", json_key(form.get("tail_support")), index),
            "name": "tail_support_term",
            "primary_eligible": True,
        },
        {
            "description": "Normalized motif key plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("motif", str(form.get("motif_key") or ""), index),
            "name": "motif_term",
            "primary_eligible": True,
        },
        {
            "description": "Exact tail expression plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("exact_tail", str(form.get("exact_tail_expression_key") or ""), index),
            "name": "exact_tail_term",
            "primary_eligible": True,
        },
        {
            "description": "Row-key plus support plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("row_support", row_keys(form), support_tuple(form, 16), index),
            "name": "row_support_term",
            "primary_eligible": True,
        },
        {
            "description": "Salt plus support plus term.",
            "label_fn": lambda _n, form, index, _coeff: ("salt_support", salt_tuple(form), support_tuple(form, 16), index),
            "name": "salt_support_term",
            "primary_eligible": True,
        },
        {
            "description": "Row-key plus signed coefficient plus term.",
            "label_fn": lambda _n, form, index, coeff: ("row_coeff", row_keys(form), index, coeff % ORDER),
            "name": "row_coeff_term",
            "primary_eligible": True,
        },
        {
            "description": "Salt plus signed coefficient plus term.",
            "label_fn": lambda _n, form, index, coeff: ("salt_coeff", salt_tuple(form), index, coeff % ORDER),
            "name": "salt_coeff_term",
            "primary_eligible": True,
        },
        {
            "description": "Positive control: every nonzero factor entry is form-local.",
            "label_fn": lambda n, _form, index, _coeff: ("form", n, index),
            "name": "control_form_term",
            "primary_eligible": False,
        },
    ]


def unique_scope_forms(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    compressed = p1029.dedupe_by_row_signature(rows)
    reconstructed, forms = p1025.reconstruct_partition(compressed)
    unique = p1023.unique_forms(forms)
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique] or [0])
    return unique, {
        "compressed_selected_count": len(compressed),
        "factor_count": factor_count,
        "form_count": len(forms),
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
        "selection": p1029.selection_summary(rows),
        "unique_form_count": len(unique),
    }


def build_factor_matrix(
    forms: list[dict[str, Any]],
    factor_count: int,
    label_fn: FactorLabelFn,
) -> tuple[list[list[int]], list[int], dict[str, Any]]:
    labels = set()
    spans: dict[tuple[str, str], set[int]] = defaultdict(set)
    for form_index, form in enumerate(forms):
        labels.add(("target", public_key(form)))
        for factor_index, coeff in nonzero_factor_entries(form, factor_count):
            label = ("factor", json_key(label_fn(form_index, form, factor_index, coeff)))
            labels.add(label)
            spans[label].add(form_index)
    labels = sorted(labels, key=repr)
    label_index = {label: offset for offset, label in enumerate(labels)}
    rows = []
    rhs = []
    for form_index, form in enumerate(forms):
        q_coeff, _factors, form_rhs = form_parts(form, factor_count)
        row = [0] * len(labels)
        target_label = ("target", public_key(form))
        row[label_index[target_label]] = (row[label_index[target_label]] + q_coeff) % ORDER
        for factor_index, coeff in nonzero_factor_entries(form, factor_count):
            label = ("factor", json_key(label_fn(form_index, form, factor_index, coeff)))
            row[label_index[label]] = (row[label_index[label]] + coeff) % ORDER
        rows.append(row)
        rhs.append(form_rhs)
    factor_label_count = len([label for label in labels if label[0] == "factor"])
    target_label_count = len([label for label in labels if label[0] == "target"])
    per_form_factor_label_count = sum(len(nonzero_factor_entries(form, factor_count)) for form in forms)
    return rows, rhs, {
        "factor_label_count": factor_label_count,
        "factor_label_compression_ratio": round8(factor_label_count / per_form_factor_label_count)
        if per_form_factor_label_count
        else None,
        "max_forms_per_factor_label": max([len(values) for values in spans.values()] or [0]),
        "multi_form_factor_label_count": sum(1 for values in spans.values() if len(values) > 1),
        "per_form_factor_label_count": per_form_factor_label_count,
        "target_label_count": target_label_count,
        "width": len(labels),
    }


def compact_form(index: int, form: dict[str, Any], factor_count: int) -> dict[str, Any]:
    q_coeff, factors, rhs = form_parts(form, factor_count)
    return {
        "index": index,
        "public_fingerprint": public_key(form),
        "q_coeff": q_coeff,
        "rhs": rhs,
        "row_keys": list(row_keys(form)),
        "salt_tuple": list(salt_tuple(form)),
        "source_secret": form.get("source_secret"),
        "split": form.get("split"),
        "tail_support": form.get("tail_support"),
        "terms": form.get("terms"),
        "window": form.get("window"),
        "nonzero_factors": [[index, coeff] for index, coeff in enumerate(factors) if coeff % ORDER],
    }


def summarize_factor_model(
    forms: list[dict[str, Any]],
    factor_count: int,
    model: dict[str, Any],
) -> dict[str, Any]:
    rows, rhs, label_summary = build_factor_matrix(forms, factor_count, model["label_fn"])
    matrix = matrix_summary(rows, rhs)
    compressed = label_summary["factor_label_count"] < label_summary["per_form_factor_label_count"]
    primary_success = bool(
        model["primary_eligible"]
        and matrix["matrix_consistent"]
        and compressed
        and int_value(label_summary.get("multi_form_factor_label_count")) > 0
    )
    single_form_relief = []
    if not matrix["matrix_consistent"] and matrix["augmented_rank"] == matrix["coefficient_rank"] + 1:
        for remove_index in range(len(forms)):
            subset = [form for index, form in enumerate(forms) if index != remove_index]
            sub_rows, sub_rhs, _sub_labels = build_factor_matrix(subset, factor_count, model["label_fn"])
            sub_matrix = matrix_summary(sub_rows, sub_rhs)
            if sub_matrix["matrix_consistent"]:
                single_form_relief.append(compact_form(remove_index, forms[remove_index], factor_count))
    return {
        "description": model["description"],
        "label_summary": label_summary,
        "matrix": matrix,
        "model": model["name"],
        "primary_eligible": bool(model["primary_eligible"]),
        "primary_success": primary_success,
        "single_form_relief": single_form_relief[:12],
        "single_form_relief_count": len(single_form_relief),
    }


def object_specs() -> list[dict[str, Any]]:
    return [
        {
            "description": "Same public, row key, and exact nonzero factor vector.",
            "key_fn": lambda form, factor_count: ("row_vector", row_keys(form), nonzero_factor_entries(form, factor_count)),
            "name": "row_vector",
        },
        {
            "description": "Same public, salt, terms, and tail support.",
            "key_fn": lambda form, _factor_count: (
                "salt_terms_tail",
                salt_tuple(form),
                tuple(int_value(value) for value in form.get("terms") or []),
                tuple(int_value(value) for value in form.get("tail_support") or []),
            ),
            "name": "salt_terms_tail",
        },
        {
            "description": "Same public and exact tail expression.",
            "key_fn": lambda form, _factor_count: ("exact_tail", str(form.get("exact_tail_expression_key") or "")),
            "name": "exact_tail",
        },
        {
            "description": "Same public and normalized motif key.",
            "key_fn": lambda form, _factor_count: ("motif", str(form.get("motif_key") or "")),
            "name": "motif",
        },
    ]


def derive_target_from_pair(left: dict[str, Any], right: dict[str, Any], factor_count: int) -> int | None:
    q_left, factors_left, rhs_left = form_parts(left, factor_count)
    q_right, factors_right, rhs_right = form_parts(right, factor_count)
    if factors_left != factors_right:
        return None
    denom = (q_left - q_right) % ORDER
    if not denom:
        return None
    return ((rhs_left - rhs_right) * pow(denom, -1, ORDER)) % ORDER


def shares_window(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_windows = set(str(value) for value in left.get("windows") or [left.get("window")])
    right_windows = set(str(value) for value in right.get("windows") or [right.get("window")])
    return bool(left_windows & right_windows)


def shares_split(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_splits = set(str(value) for value in left.get("splits") or [left.get("split")])
    right_splits = set(str(value) for value in right.get("splits") or [right.get("split")])
    return bool(left_splits & right_splits)


def both_fresh(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return "fresh_validation" in set(left.get("splits") or [left.get("split")]) and "fresh_validation" in set(
        right.get("splits") or [right.get("split")]
    )


def prediction_policy_name(left: dict[str, Any], right: dict[str, Any]) -> list[str]:
    names = ["all_pairs"]
    if shares_window(left, right):
        names.append("same_window")
    if shares_split(left, right):
        names.append("same_split")
    if both_fresh(left, right):
        names.append("both_fresh")
    if shares_window(left, right) and both_fresh(left, right):
        names.append("same_window_both_fresh")
    return names


def target_prediction_summary(forms: list[dict[str, Any]], factor_count: int, spec: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[tuple[str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, form in enumerate(forms):
        grouped[(public_key(form), json_key(spec["key_fn"](form, factor_count)))].append((index, form))
    policy_counts: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"false_count": 0, "prediction_count": 0, "samples": [], "true_count": 0}
    )
    groups = []
    for (public, object_key), group in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1])):
        if len(group) < 2:
            continue
        predictions = []
        for left_offset, (left_index, left) in enumerate(group):
            for right_index, right in group[left_offset + 1 :]:
                predicted = derive_target_from_pair(left, right, factor_count)
                if predicted is None:
                    continue
                source_secrets = sorted(
                    {
                        int_value(value)
                        for value in [left.get("source_secret"), right.get("source_secret")]
                        if value is not None
                    }
                )
                verified = bool(source_secrets and all(predicted == secret % ORDER for secret in source_secrets))
                sample = {
                    "left": compact_form(left_index, left, factor_count),
                    "object_key": object_key,
                    "policies": prediction_policy_name(left, right),
                    "predicted_target": predicted,
                    "public_fingerprint": public,
                    "right": compact_form(right_index, right, factor_count),
                    "source_secrets": source_secrets,
                    "toy_secret_verified": verified,
                }
                predictions.append(sample)
                for policy in sample["policies"]:
                    counts = policy_counts[policy]
                    counts["prediction_count"] += 1
                    if verified:
                        counts["true_count"] += 1
                    else:
                        counts["false_count"] += 1
                    if len(counts["samples"]) < 8:
                        counts["samples"].append(sample)
        if predictions:
            groups.append(
                {
                    "object_key": object_key,
                    "prediction_count": len(predictions),
                    "predictions": predictions[:8],
                    "public_fingerprint": public,
                    "source_secrets": sorted(
                        {
                            int_value(item[1].get("source_secret"))
                            for item in group
                            if item[1].get("source_secret") is not None
                        }
                    ),
                }
            )
    policies = {policy: dict(counts) for policy, counts in sorted(policy_counts.items())}
    zero_false = [
        {"policy": policy, **{key: value for key, value in counts.items() if key != "samples"}}
        for policy, counts in policies.items()
        if int_value(counts.get("true_count")) > 0 and int_value(counts.get("false_count")) == 0
    ]
    return {
        "description": spec["description"],
        "groups": groups[:12],
        "local_object_group_count": len(groups),
        "model": spec["name"],
        "policies": policies,
        "zero_false_policies": zero_false,
    }


def summarize_scope(scope: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    forms, reconstruction = unique_scope_forms(rows)
    factor_count = reconstruction["factor_count"]
    factor_models = [summarize_factor_model(forms, factor_count, model) for model in factor_model_specs()] if forms else []
    target_predictions = [target_prediction_summary(forms, factor_count, spec) for spec in object_specs()] if forms else []
    primary_models = [model for model in factor_models if model.get("primary_success")]
    zero_false_prediction_models = [
        model
        for model in target_predictions
        if any(policy.get("policy") == "same_window_both_fresh" for policy in model.get("zero_false_policies") or [])
    ]
    return {
        "factor_count": factor_count,
        "factor_model_summaries": factor_models,
        "primary_model_count": len(primary_models),
        "primary_models": primary_models,
        "reconstruction": reconstruction,
        "scope": scope,
        "target_prediction_model_count": len(zero_false_prediction_models),
        "target_prediction_models": zero_false_prediction_models,
        "target_prediction_summaries": target_predictions,
    }


def determine_claim(scopes: list[dict[str, Any]]) -> str:
    if any(scope["reconstruction"]["reconstruction_error_count"] for scope in scopes):
        return "NEGATIVE_RESULT_P1033_RECONSTRUCTION_ERRORS"
    controls = [
        model
        for scope in scopes
        for model in scope.get("factor_model_summaries") or []
        if model.get("model") == "control_form_term"
    ]
    if any(not ((control.get("matrix") or {}).get("matrix_consistent")) for control in controls):
        return "NEGATIVE_RESULT_P1033_POSITIVE_CONTROL_FAILED"
    if any(scope.get("primary_model_count") for scope in scopes):
        return "P1033_PUBLIC_SHARED_FACTOR_LABEL_MERGE_SIGNAL"
    leaf8 = next((scope for scope in scopes if scope.get("scope") == "leaf8_neighbor"), {})
    if int_value(leaf8.get("target_prediction_model_count")) > 0:
        return "P1033_LEAF8_ROW_LOCAL_TARGET_PREDICTION_SIGNAL"
    if any(
        int_value(model.get("single_form_relief_count")) > 0
        for scope in scopes
        for model in scope.get("factor_model_summaries") or []
    ):
        return "P1033_FACTOR_LABEL_OBSTRUCTION_LOCALIZED"
    return "NEGATIVE_RESULT_P1033_NO_FACTOR_LABEL_OR_TARGET_PREDICTION_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scope_rows, exists = p1030.build_scopes(args)
    scope_summaries = [summarize_scope(scope, rows) for scope, rows in scope_rows.items()]
    claim = determine_claim(scope_summaries)
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
            "p1030_dependency_sha256": p1005.sha256_file(Path(p1030.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1033_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: P1033 tests a finite metadata-derived factor-label catalog.",
            "SCOUT: target-prediction subpolicies are not frozen validation.",
            "INDEX-CALCULUS PRECURSOR: this is not sparse linear algebra closure or asymptotic target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "factor_models": [model["name"] for model in factor_model_specs()],
            "fresh_windows": p1025.FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "object_models": [model["name"] for model in object_specs()],
            "scopes": list(scope_rows),
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {"exists": exists},
        "summary": {
            "claim_status": claim,
            "primary_model_count": sum(int_value(scope.get("primary_model_count")) for scope in scope_summaries),
            "scope_count": len(scope_summaries),
            "scope_summaries": [
                {
                    "factor_count": scope["factor_count"],
                    "fresh_false_count": scope["reconstruction"]["selection"]["fresh_false_count"],
                    "fresh_positive_count": scope["reconstruction"]["selection"]["fresh_positive_count"],
                    "primary_model_count": scope["primary_model_count"],
                    "scope": scope["scope"],
                    "selected_count": scope["reconstruction"]["selection"]["selected_count"],
                    "target_prediction_model_count": scope["target_prediction_model_count"],
                    "unique_form_count": scope["reconstruction"]["unique_form_count"],
                }
                for scope in scope_summaries
            ],
            "target_prediction_model_count": sum(
                int_value(scope.get("target_prediction_model_count")) for scope in scope_summaries
            ),
        },
        "scopes": scope_summaries,
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
    bits = []
    for scope in payload["summary"]["scope_summaries"]:
        bits.append(
            "{scope}:forms={forms} primary={primary} target_pred={target_pred}".format(
                scope=scope["scope"],
                forms=scope["unique_form_count"],
                primary=scope["primary_model_count"],
                target_pred=scope["target_prediction_model_count"],
            )
        )
    print(
        "claim={claim} primary={primary} target_prediction={target_pred} out={out} {bits}".format(
            claim=payload["claim_status"],
            primary=payload["summary"]["primary_model_count"],
            target_pred=payload["summary"]["target_prediction_model_count"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
