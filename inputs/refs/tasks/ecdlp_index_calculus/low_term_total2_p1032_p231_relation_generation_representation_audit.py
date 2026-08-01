#!/usr/bin/env python3
"""P1032 pre-elimination relation-generation representation audit."""

from __future__ import annotations

import argparse
import hashlib
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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1032_p231_relation_generation_representation_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1032_p231_relation_generation_representation_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1032_p231_relation_generation_representation_audit.v1"
ORDER = p1026.ORDER
SALT_RE = re.compile(r"salt(\d+)")

KeyFn = Callable[[int, dict[str, Any]], str]


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


def stable_bucket(value: Any, buckets: int) -> str:
    digest = hashlib.sha256(json_key(value).encode("utf-8")).hexdigest()
    return f"bucket{int(digest[:12], 16) % buckets}"


def pad(values: list[int], width: int) -> list[int]:
    return values + [0] * max(0, width - len(values))


def rank_mod(matrix: list[list[int]]) -> int:
    return p1030.rank_mod(matrix, ORDER)


def matrix_summary(rows: list[list[int]], rhs: list[int]) -> dict[str, Any]:
    return p1030.matrix_summary(rows, rhs, ORDER)


def parse_public(public_fingerprint: str) -> tuple[int, int]:
    return p1030.parse_public(public_fingerprint)


def form_coeff_parts(form: dict[str, Any], factor_count: int) -> tuple[int, list[int], int]:
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


def split_key(form: dict[str, Any]) -> str:
    return json_key(sorted(p1025.split_set(form)) or ["unknown"])


def public_key(_index: int, form: dict[str, Any]) -> str:
    return str(form.get("public_fingerprint") or "missing-public")


def public_x_key(_index: int, form: dict[str, Any]) -> str:
    x, _y = parse_public(str(form.get("public_fingerprint") or "[0,0]"))
    return f"x:{x}"


def global_key(_index: int, _form: dict[str, Any]) -> str:
    return "global"


def form_key(index: int, _form: dict[str, Any]) -> str:
    return f"form:{index}"


def row_key_signature(_index: int, form: dict[str, Any]) -> str:
    return "rowkeys:" + json_key(row_keys(form))


def salt_pair_key(_index: int, form: dict[str, Any]) -> str:
    salts = []
    for key in row_keys(form):
        salts.extend(int(match.group(1)) for match in SALT_RE.finditer(key))
    return "salts:" + json_key(sorted(salts) or ["none"])


def support_key(_index: int, form: dict[str, Any]) -> str:
    coeffs = [int_value(value) % ORDER for value in form.get("coeffs") or []]
    support = [position for position, coeff in enumerate(coeffs[1:]) if coeff]
    return "support:" + json_key(support)


def split_slice_key(_index: int, form: dict[str, Any]) -> str:
    return "split:" + split_key(form)


def random4_key(index: int, form: dict[str, Any]) -> str:
    return "random4:" + stable_bucket([index, row_keys(form), public_key(index, form)], 4)


def model_specs() -> list[dict[str, Any]]:
    return [
        {
            "description": "Positive control: each form has independent factor labels; target is shared by public.",
            "factor_key": form_key,
            "name": "control_form_factor_public_target",
            "primary_eligible": False,
            "target_key": public_key,
        },
        {
            "description": "Over-permissive positive control: each form has independent factor and target labels.",
            "factor_key": form_key,
            "name": "control_form_factor_form_target",
            "primary_eligible": False,
            "target_key": form_key,
        },
        {
            "description": "Negative control: current global coefficient-position factor labels with public target labels.",
            "factor_key": global_key,
            "name": "negative_global_factor_public_target",
            "primary_eligible": False,
            "target_key": public_key,
        },
        {
            "description": "Negative control: deterministic four-bucket factor labels with public target labels.",
            "factor_key": random4_key,
            "name": "negative_random4_factor_public_target",
            "primary_eligible": False,
            "target_key": public_key,
        },
        {
            "description": "Candidate: factor labels keyed by public fingerprint; target labels by public fingerprint.",
            "factor_key": public_key,
            "name": "public_slice_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Candidate: x-only Kummer factor labels; target labels by public fingerprint.",
            "factor_key": public_x_key,
            "name": "kummer_x_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Candidate: x-only Kummer factor and target labels.",
            "factor_key": public_x_key,
            "name": "kummer_x_factor_x_target",
            "primary_eligible": True,
            "target_key": public_x_key,
        },
        {
            "description": "Candidate: row-key factor labels; target labels by public fingerprint.",
            "factor_key": row_key_signature,
            "name": "rowkey_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Candidate: salt-pair slice factor labels; target labels by public fingerprint.",
            "factor_key": salt_pair_key,
            "name": "salt_pair_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Candidate: factor labels keyed only by nonzero factor support; target labels by public fingerprint.",
            "factor_key": support_key,
            "name": "support_slice_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Candidate: training/fresh split factor labels; target labels by public fingerprint.",
            "factor_key": split_slice_key,
            "name": "split_slice_factor_public_target",
            "primary_eligible": True,
            "target_key": public_key,
        },
        {
            "description": "Diagnostic only: row-key factor and target labels.",
            "factor_key": row_key_signature,
            "name": "diagnostic_rowkey_factor_rowkey_target",
            "primary_eligible": False,
            "target_key": row_key_signature,
        },
        {
            "description": "Diagnostic only: salt-pair factor and target labels.",
            "factor_key": salt_pair_key,
            "name": "diagnostic_salt_pair_factor_salt_pair_target",
            "primary_eligible": False,
            "target_key": salt_pair_key,
        },
    ]


def unique_scope_forms(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    compressed = p1029.dedupe_by_row_signature(rows)
    reconstructed, forms = p1025.reconstruct_partition(compressed)
    unique = p1023.unique_forms(forms)
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique] or [0])
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    selection = p1029.selection_summary(rows)
    return unique, {
        "compressed_selected_count": len(compressed),
        "factor_count": factor_count,
        "form_count": len(forms),
        "form_orders": form_orders,
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
        "selection": selection,
        "unique_form_count": len(unique),
    }


def key_spans(forms: list[dict[str, Any]], key_fn: KeyFn) -> dict[str, int]:
    spans: dict[str, set[int]] = defaultdict(set)
    for index, form in enumerate(forms):
        spans[key_fn(index, form)].add(index)
    return {key: len(indices) for key, indices in spans.items()}


def build_matrix(
    forms: list[dict[str, Any]],
    factor_count: int,
    factor_key_fn: KeyFn,
    target_key_fn: KeyFn,
) -> tuple[list[list[int]], list[int], dict[str, Any]]:
    factor_labels = []
    target_labels = []
    factor_spans = key_spans(forms, factor_key_fn)
    target_spans = key_spans(forms, target_key_fn)
    for index, form in enumerate(forms):
        factor_key_value = factor_key_fn(index, form)
        target_key_value = target_key_fn(index, form)
        factor_labels.extend(("factor", factor_key_value, factor_index) for factor_index in range(factor_count))
        target_labels.append(("target", target_key_value))
    labels = sorted(set([*factor_labels, *target_labels]), key=repr)
    label_index = {label: offset for offset, label in enumerate(labels)}
    rows = []
    rhs = []
    for index, form in enumerate(forms):
        q_coeff, factors, form_rhs = form_coeff_parts(form, factor_count)
        row = [0] * len(labels)
        factor_key_value = factor_key_fn(index, form)
        for factor_index, coeff in enumerate(factors):
            label = ("factor", factor_key_value, factor_index)
            row[label_index[label]] = (row[label_index[label]] + coeff) % ORDER
        target_label = ("target", target_key_fn(index, form))
        row[label_index[target_label]] = (row[label_index[target_label]] + q_coeff) % ORDER
        rows.append(row)
        rhs.append(form_rhs)
    nonzero_factor_labels = {
        ("factor", factor_key_fn(index, form), factor_index)
        for index, form in enumerate(forms)
        for factor_index, coeff in enumerate(form_coeff_parts(form, factor_count)[1])
        if coeff % ORDER
    }
    factor_label_count = len({label for label in labels if label[0] == "factor"})
    target_label_count = len({label for label in labels if label[0] == "target"})
    per_form_factor_labels = len(forms) * factor_count
    return rows, rhs, {
        "factor_key_count": len(factor_spans),
        "factor_label_count": factor_label_count,
        "max_forms_per_factor_key": max(factor_spans.values(), default=0),
        "multi_form_factor_key_count": sum(1 for count in factor_spans.values() if count > 1),
        "nonzero_factor_label_count": len(nonzero_factor_labels),
        "per_form_factor_label_count": per_form_factor_labels,
        "target_key_count": len(target_spans),
        "target_label_count": target_label_count,
        "width": len(labels),
        "factor_label_compression_ratio": round8(factor_label_count / per_form_factor_labels)
        if per_form_factor_labels
        else None,
    }


def build_factor_matrix(
    forms: list[dict[str, Any]],
    factor_count: int,
    factor_key_fn: KeyFn,
) -> list[list[int]]:
    labels = sorted(
        {
            ("factor", factor_key_fn(index, form), factor_index)
            for index, form in enumerate(forms)
            for factor_index in range(factor_count)
        },
        key=repr,
    )
    label_index = {label: offset for offset, label in enumerate(labels)}
    rows = []
    for index, form in enumerate(forms):
        _q_coeff, factors, _rhs = form_coeff_parts(form, factor_count)
        row = [0] * len(labels)
        factor_key_value = factor_key_fn(index, form)
        for factor_index, coeff in enumerate(factors):
            label = ("factor", factor_key_value, factor_index)
            row[label_index[label]] = (row[label_index[label]] + coeff) % ORDER
        rows.append(row)
    return rows


def build_target_matrix(forms: list[dict[str, Any]], target_key_fn: KeyFn) -> list[list[int]]:
    labels = sorted(
        {("target", target_key_fn(index, form)) for index, form in enumerate(forms)},
        key=repr,
    )
    label_index = {label: offset for offset, label in enumerate(labels)}
    rows = []
    for index, form in enumerate(forms):
        q_coeff, _factors, _rhs = form_coeff_parts(form, 0)
        row = [0] * len(labels)
        label = ("target", target_key_fn(index, form))
        row[label_index[label]] = (row[label_index[label]] + q_coeff) % ORDER
        rows.append(row)
    return rows


def heldout_public_check(forms: list[dict[str, Any]], rows: list[list[int]], rhs: list[int]) -> dict[str, Any]:
    publics = sorted({str(form.get("public_fingerprint")) for form in forms})
    indexed = list(zip(forms, rows, rhs))
    tested = 0
    passed = 0
    skipped = 0
    details = []
    for public in publics:
        train = [(form, row, value) for form, row, value in indexed if str(form.get("public_fingerprint")) != public]
        heldout = [(form, row, value) for form, row, value in indexed if str(form.get("public_fingerprint")) == public]
        if not train or not heldout:
            continue
        train_rows = [row for _form, row, _value in train]
        train_rhs = [value for _form, _row, value in train]
        train_summary = matrix_summary(train_rows, train_rhs)
        if not train_summary["matrix_consistent"]:
            skipped += len(heldout)
            details.append({"heldout_public": public, "reason": "training matrix inconsistent", "tested": 0})
            continue
        train_coeff_rank = rank_mod(train_rows)
        train_augmented = [row + [train_rhs[index]] for index, row in enumerate(train_rows)]
        train_aug_rank = rank_mod(train_augmented)
        public_tested = 0
        public_passed = 0
        public_skipped = 0
        for _form, held_row, held_rhs in heldout:
            coeff_in_span = rank_mod([*train_rows, held_row]) == train_coeff_rank
            if not coeff_in_span:
                skipped += 1
                public_skipped += 1
                continue
            tested += 1
            public_tested += 1
            aug_in_span = rank_mod([*train_augmented, held_row + [held_rhs]]) == train_aug_rank
            if aug_in_span:
                passed += 1
                public_passed += 1
        details.append(
            {
                "heldout_public": public,
                "passed": public_passed,
                "skipped": public_skipped,
                "tested": public_tested,
                "training_augmented_rank": train_aug_rank,
                "training_coefficient_rank": train_coeff_rank,
            }
        )
    return {
        "details": details,
        "heldout_passed": passed,
        "heldout_skipped": skipped,
        "heldout_tested": tested,
    }


def summarize_model(forms: list[dict[str, Any]], factor_count: int, model: dict[str, Any]) -> dict[str, Any]:
    rows, rhs, label_summary = build_matrix(forms, factor_count, model["factor_key"], model["target_key"])
    matrix = matrix_summary(rows, rhs)
    factor_rank = rank_mod(build_factor_matrix(forms, factor_count, model["factor_key"]))
    target_rank = rank_mod(build_target_matrix(forms, model["target_key"]))
    factor_component_rank = max(0, matrix["coefficient_rank"] - target_rank)
    heldout = heldout_public_check(forms, rows, rhs)
    compressed = (
        label_summary["factor_label_count"] < label_summary["per_form_factor_label_count"]
        if label_summary["per_form_factor_label_count"]
        else False
    )
    primary_success = bool(
        model["primary_eligible"]
        and matrix["matrix_consistent"]
        and factor_component_rank > 0
        and compressed
        and int_value(label_summary.get("multi_form_factor_key_count")) > 0
    )
    diagnostic_success = bool(
        not model["primary_eligible"]
        and matrix["matrix_consistent"]
        and compressed
        and int_value(label_summary.get("multi_form_factor_key_count")) > 0
    )
    return {
        "description": model["description"],
        "diagnostic_success": diagnostic_success,
        "factor_component_rank": factor_component_rank,
        "factor_label_rank": factor_rank,
        "heldout": heldout,
        "label_summary": label_summary,
        "matrix": matrix,
        "model": model["name"],
        "primary_eligible": bool(model["primary_eligible"]),
        "primary_success": primary_success,
        "target_label_rank": target_rank,
    }


def compact_form(index: int, form: dict[str, Any]) -> dict[str, Any]:
    q_coeff, factors, rhs = form_coeff_parts(form, max(0, len(form.get("coeffs") or []) - 1))
    support = [offset for offset, value in enumerate(factors) if value % ORDER]
    return {
        "index": index,
        "public_fingerprint": form.get("public_fingerprint"),
        "q_coeff": q_coeff,
        "rhs": rhs,
        "row_keys": list(row_keys(form)),
        "split": sorted(p1025.split_set(form)),
        "support": support,
    }


def summarize_scope(scope: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    forms, reconstruction = unique_scope_forms(rows)
    factor_count = reconstruction["factor_count"]
    models = [summarize_model(forms, factor_count, model) for model in model_specs()] if factor_count else []
    primary = [model for model in models if model.get("primary_success")]
    diagnostics = [model for model in models if model.get("diagnostic_success")]
    controls = {model["model"]: model for model in models if model["model"].startswith("control_") or model["model"].startswith("negative_")}
    return {
        "controls": controls,
        "diagnostic_model_count": len(diagnostics),
        "diagnostic_models": diagnostics,
        "factor_count": factor_count,
        "forms": [compact_form(index, form) for index, form in enumerate(forms[:16])],
        "model_summaries": models,
        "primary_model_count": len(primary),
        "primary_models": primary,
        "reconstruction": reconstruction,
        "scope": scope,
    }


def determine_claim(scopes: list[dict[str, Any]]) -> str:
    if any(scope["reconstruction"]["reconstruction_error_count"] for scope in scopes):
        return "NEGATIVE_RESULT_P1032_RECONSTRUCTION_ERRORS"
    positive_controls = [
        (scope["controls"].get("control_form_factor_public_target") or {}).get("matrix", {})
        for scope in scopes
    ]
    if any(not control.get("matrix_consistent") for control in positive_controls):
        return "NEGATIVE_RESULT_P1032_POSITIVE_CONTROL_FAILED"
    if any(scope.get("primary_model_count") for scope in scopes):
        return "P1032_PRE_ELIMINATION_RELATION_OBJECT_MERGE_SIGNAL"
    if any(scope.get("diagnostic_model_count") for scope in scopes):
        return "P1032_DIAGNOSTIC_LOCAL_RELATION_OBJECT_SIGNAL_ONLY"
    return "NEGATIVE_RESULT_P1032_NO_TESTED_FACTOR_LABEL_MERGE"


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
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1032_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: P1032 tests a finite relation-object and factor-label catalog, not all possible representations.",
            "INDEX-CALCULUS PRECURSOR: a representation signal is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "fresh_windows": p1025.FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "model_names": [model["name"] for model in model_specs()],
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "scopes": list(scope_rows),
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {"exists": exists},
        "summary": {
            "claim_status": claim,
            "diagnostic_model_count": sum(int_value(scope.get("diagnostic_model_count")) for scope in scope_summaries),
            "primary_model_count": sum(int_value(scope.get("primary_model_count")) for scope in scope_summaries),
            "scope_count": len(scope_summaries),
            "scope_summaries": [
                {
                    "diagnostic_model_count": scope["diagnostic_model_count"],
                    "factor_count": scope["factor_count"],
                    "fresh_false_count": scope["reconstruction"]["selection"]["fresh_false_count"],
                    "fresh_positive_count": scope["reconstruction"]["selection"]["fresh_positive_count"],
                    "positive_control_consistent": bool(
                        ((scope["controls"].get("control_form_factor_public_target") or {}).get("matrix") or {}).get(
                            "matrix_consistent"
                        )
                    ),
                    "primary_model_count": scope["primary_model_count"],
                    "scope": scope["scope"],
                    "selected_count": scope["reconstruction"]["selection"]["selected_count"],
                    "unique_form_count": scope["reconstruction"]["unique_form_count"],
                }
                for scope in scope_summaries
            ],
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
            "{scope}:forms={forms} primary={primary} diagnostic={diagnostic} control={control}".format(
                scope=scope["scope"],
                forms=scope["unique_form_count"],
                primary=scope["primary_model_count"],
                diagnostic=scope["diagnostic_model_count"],
                control=scope["positive_control_consistent"],
            )
        )
    print(
        "claim={claim} primary={primary} diagnostic={diagnostic} out={out} {bits}".format(
            claim=payload["claim_status"],
            primary=payload["summary"]["primary_model_count"],
            diagnostic=payload["summary"]["diagnostic_model_count"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
