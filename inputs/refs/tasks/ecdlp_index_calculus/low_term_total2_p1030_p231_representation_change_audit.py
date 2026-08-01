#!/usr/bin/env python3
"""P1030 representation-change audit for P1029 total-2 motif relations."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026
import low_term_total2_p1027_p231_public_context_augmented_quotient as p1027
import low_term_total2_p1029_p231_motif_neighbor_scout as p1029
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1030_p231_representation_change_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1030_p231_representation_change_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1030_p231_representation_change_audit.v1"
ORDER = p1026.ORDER

ContextFn = Callable[[dict[str, Any]], list[int]]


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
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def pad(values: list[int], width: int) -> list[int]:
    return values + [0] * max(0, width - len(values))


def rank_mod(matrix: list[list[int]], modulus: int = ORDER) -> int:
    return p1027.rank_mod(matrix, modulus)


def matrix_summary(rows: list[list[int]], rhs: list[int], modulus: int = ORDER) -> dict[str, Any]:
    return p1027.matrix_summary(rows, rhs, modulus)


def split_set(form: dict[str, Any]) -> set[str]:
    return p1025.split_set(form)


def pair_role(left: dict[str, Any], right: dict[str, Any]) -> str:
    return p1025.pair_role(left, right)


def parse_public(public_fingerprint: str) -> tuple[int, int]:
    return p1026.parse_public(public_fingerprint)


def relation_rows_for_forms(public: str, forms: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], int]:
    unique = p1023.unique_forms(forms)
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique] or [0])
    relations: list[dict[str, Any]] = []
    for left_index, left in enumerate(unique):
        for right_index in range(left_index + 1, len(unique)):
            right = unique[right_index]
            q_left, factors_left, rhs_left = factor_bank.form_parts(left, order, factor_count)
            q_right, factors_right, rhs_right = factor_bank.form_parts(right, order, factor_count)
            raw_coeffs = [
                (q_right * factors_left[index] - q_left * factors_right[index]) % order
                for index in range(factor_count)
            ]
            raw_rhs = (q_right * rhs_left - q_left * rhs_right) % order
            pivot = next((value for value in raw_coeffs if value % order), None)
            if pivot is None:
                continue
            scale = pow(pivot % order, -1, order)
            canonical_coeffs = [(value * scale) % order for value in raw_coeffs]
            canonical_rhs = (raw_rhs * scale) % order
            support = [index for index, coeff in enumerate(canonical_coeffs) if coeff % order]
            row_keys = sorted(
                {
                    *(str(value) for value in left.get("row_keys") or []),
                    *(str(value) for value in right.get("row_keys") or []),
                }
            )
            salts = p1026.salt_features(row_keys)
            relations.append(
                {
                    "canonical_coeffs": canonical_coeffs,
                    "canonical_rhs": canonical_rhs,
                    "factor_support": support,
                    "factor_support_size": len(support),
                    "left_form_index": left_index,
                    "left_splits": sorted(split_set(left)),
                    "pair": [left_index, right_index],
                    "pair_role": pair_role(left, right),
                    "public_fingerprint": public,
                    "public_xy": list(parse_public(public)),
                    "q_coeffs": [q_left % order, q_right % order],
                    "q_sum": (q_left + q_right) % order,
                    "q_diff": (q_right - q_left) % order,
                    "q_product": (q_left * q_right) % order,
                    "right_form_index": right_index,
                    "right_splits": sorted(split_set(right)),
                    "row_key_signature": json_key(row_keys),
                    "row_keys": row_keys,
                    "row_scale": scale,
                    **salts,
                }
            )
    return relations, factor_count


def rows_for_scope(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    compressed = p1029.dedupe_by_row_signature(rows)
    reconstructed, forms = p1025.reconstruct_partition(compressed)
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    order = form_orders[0] if form_orders == [ORDER] else 0
    forms_by_public: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_public[str(form.get("public_fingerprint"))].append(form)
    relations: list[dict[str, Any]] = []
    factor_count = 0
    if order:
        for public, group in sorted(forms_by_public.items()):
            local_relations, local_factor_count = relation_rows_for_forms(public, group, order)
            factor_count = max(factor_count, local_factor_count)
            relations.extend(local_relations)
    selection = p1029.selection_summary(rows)
    return relations, {
        "compressed_selected_count": len(compressed),
        "factor_count": factor_count,
        "form_count": len(forms),
        "form_orders": form_orders,
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
        "selection": selection,
        "unique_form_count": len(p1023.unique_forms(forms)),
    }


def build_scopes(args: argparse.Namespace) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    training_windows = [*p1022.POSITIVE_CALIBRATION_WINDOWS, *p1022.VALIDATION_WINDOWS]
    all_windows = [*training_windows, *p1022.NEGATIVE_CALIBRATION_WINDOWS, *p1025.FRESH_WINDOWS]
    by_window, exists = p1029.p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    reference = [
        *p1029.reference_rows(training_windows, by_window, "training_seed"),
        *p1029.reference_rows(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control"),
        *p1029.reference_rows(p1025.FRESH_WINDOWS, by_window, "fresh_validation"),
    ]
    scout_by_leaf: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for window in all_windows:
        split = p1029.split_for_window(window)
        for row in by_window.get(window) or []:
            if p1029.scout_predicate(row):
                scout_by_leaf[p1029.leaf_key(row)].append(p1029.annotate_row(row, window, split))
    return {
        "leaf19_reference": reference,
        "leaf8_neighbor": scout_by_leaf.get("[8]", []),
    }, exists


def factor_coeffs(row: dict[str, Any], factor_count: int) -> list[int]:
    return pad([int_value(value) % ORDER for value in row.get("canonical_coeffs") or []], factor_count)


def rhs_values(relations: list[dict[str, Any]]) -> list[int]:
    return [int_value(row.get("canonical_rhs")) % ORDER for row in relations]


def scaled(row: dict[str, Any], value: int) -> int:
    return (int_value(value) * int_value(row.get("row_scale"), 1)) % ORDER


def public_xy(row: dict[str, Any]) -> tuple[int, int]:
    x, y = parse_public(str(row.get("public_fingerprint")))
    return x, y


def lifted_models() -> list[dict[str, Any]]:
    return [
        {
            "description": "No lifted columns; raw factor-only baseline.",
            "name": "factor_only",
            "predictive": True,
            "context_fn": lambda row: [],
        },
        {
            "description": "Scaled quotient pair columns [q_left, q_right].",
            "name": "scaled_q_pair",
            "predictive": True,
            "context_fn": lambda row: [scaled(row, value) for value in row.get("q_coeffs") or []],
        },
        {
            "description": "Scaled quotient symmetric columns [q_sum, q_diff, q_product].",
            "name": "scaled_q_symmetric",
            "predictive": True,
            "context_fn": lambda row: [
                scaled(row, row.get("q_sum")),
                scaled(row, row.get("q_diff")),
                scaled(row, row.get("q_product")),
            ],
        },
        {
            "description": "Scaled public affine columns [1, public_x, public_y].",
            "name": "scaled_public_xy",
            "predictive": True,
            "context_fn": lambda row: [
                scaled(row, 1),
                scaled(row, public_xy(row)[0]),
                scaled(row, public_xy(row)[1]),
            ],
        },
        {
            "description": "Scaled salt-pair columns [1, salt_min, salt_max, salt_gap].",
            "name": "scaled_salt_minmax_gap",
            "predictive": True,
            "context_fn": lambda row: [
                scaled(row, 1),
                scaled(row, row.get("salt_min")),
                scaled(row, row.get("salt_max")),
                scaled(row, row.get("salt_gap")),
            ],
        },
        {
            "description": "Scaled quotient and salt interaction columns.",
            "name": "scaled_q_salt_interaction",
            "predictive": True,
            "context_fn": lambda row: [
                scaled(row, row.get("q_sum")),
                scaled(row, row.get("q_diff")),
                scaled(row, int_value(row.get("q_sum")) * int_value(row.get("salt_gap"))),
                scaled(row, int_value(row.get("q_diff")) * int_value(row.get("salt_gap"))),
            ],
        },
        {
            "description": "Scaled quotient and public-coordinate interaction columns.",
            "name": "scaled_q_public_interaction",
            "predictive": True,
            "context_fn": lambda row: [
                scaled(row, int_value(row.get("q_sum")) * public_xy(row)[0]),
                scaled(row, int_value(row.get("q_sum")) * public_xy(row)[1]),
                scaled(row, int_value(row.get("q_diff")) * public_xy(row)[0]),
                scaled(row, int_value(row.get("q_diff")) * public_xy(row)[1]),
            ],
        },
    ]


def model_matrix(relations: list[dict[str, Any]], model: dict[str, Any], factor_count: int) -> tuple[list[list[int]], list[list[int]], list[int]]:
    rows = []
    context_rows = []
    rhs = rhs_values(relations)
    for relation in relations:
        factors = factor_coeffs(relation, factor_count)
        context = [int_value(value) % ORDER for value in model["context_fn"](relation)]
        rows.append([*factors, *context])
        context_rows.append(context)
    return rows, context_rows, rhs


def heldout_public_check(
    relations: list[dict[str, Any]],
    rows: list[list[int]],
    rhs: list[int],
) -> dict[str, Any]:
    publics = sorted({str(row.get("public_fingerprint")) for row in relations})
    tested = 0
    passed = 0
    skipped = 0
    details = []
    indexed = list(zip(relations, rows, rhs))
    for public in publics:
        train = [(rel, row, value) for rel, row, value in indexed if rel.get("public_fingerprint") != public]
        heldout = [(rel, row, value) for rel, row, value in indexed if rel.get("public_fingerprint") == public]
        if not train or not heldout:
            continue
        train_rows = [row for _rel, row, _value in train]
        train_rhs = [value for _rel, _row, value in train]
        train_summary = matrix_summary(train_rows, train_rhs)
        if not train_summary["matrix_consistent"]:
            skipped += len(heldout)
            details.append({"heldout_public": public, "reason": "training matrix inconsistent", "tested": 0})
            continue
        train_augmented = [row + [train_rhs[index]] for index, row in enumerate(train_rows)]
        train_coeff_rank = rank_mod(train_rows)
        train_aug_rank = rank_mod(train_augmented)
        public_tested = 0
        public_passed = 0
        public_skipped = 0
        for _rel, held_row, held_rhs in heldout:
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


def summarize_lifted_model(relations: list[dict[str, Any]], model: dict[str, Any], factor_count: int) -> dict[str, Any]:
    rows, context_rows, rhs = model_matrix(relations, model, factor_count)
    matrix = matrix_summary(rows, rhs)
    factor_matrix = [factor_coeffs(row, factor_count) for row in relations]
    factor_rank = rank_mod(factor_matrix)
    context_rank = rank_mod(context_rows)
    factor_component_rank = max(0, matrix["coefficient_rank"] - context_rank)
    heldout = heldout_public_check(relations, rows, rhs)
    primary_success = bool(
        model["predictive"]
        and matrix["matrix_consistent"]
        and factor_component_rank > 0
        and heldout["heldout_tested"] > 0
        and heldout["heldout_passed"] == heldout["heldout_tested"]
    )
    return {
        "context_column_count": len(context_rows[0]) if context_rows else 0,
        "context_rank": context_rank,
        "description": model["description"],
        "factor_component_rank": factor_component_rank,
        "factor_rank": factor_rank,
        "heldout": heldout,
        "matrix": matrix,
        "model": model["name"],
        "predictive_model": bool(model["predictive"]),
        "primary_success": primary_success,
    }


def diagonal_scale(rows: list[list[int]]) -> list[list[int]]:
    return [[(value * (index + 2)) % ORDER for index, value in enumerate(row)] for row in rows]


def reverse_columns(rows: list[list[int]]) -> list[list[int]]:
    return [list(reversed(row)) for row in rows]


def shear_columns(rows: list[list[int]]) -> list[list[int]]:
    out = []
    for row in rows:
        item = row[:]
        if len(item) >= 3:
            item[1] = (item[1] + item[0]) % ORDER
            item[2] = (item[2] + 2 * item[1]) % ORDER
        out.append(item)
    return out


def invertible_controls(relations: list[dict[str, Any]], factor_count: int) -> list[dict[str, Any]]:
    rows = [factor_coeffs(row, factor_count) for row in relations]
    rhs = rhs_values(relations)
    controls = [
        ("identity", rows),
        ("reverse_columns", reverse_columns(rows)),
        ("diagonal_scale", diagonal_scale(rows)),
        ("upper_shear", shear_columns(rows)),
    ]
    return [
        {
            "control": name,
            "matrix": matrix_summary(control_rows, rhs),
        }
        for name, control_rows in controls
    ]


def projection_summary(relations: list[dict[str, Any]], factor_count: int, columns: tuple[int, ...]) -> dict[str, Any]:
    rows = [[factor_coeffs(row, factor_count)[index] for index in columns] for row in relations]
    rhs = rhs_values(relations)
    matrix = matrix_summary(rows, rhs)
    heldout = heldout_public_check(relations, rows, rhs)
    diagnostic_success = bool(
        matrix["matrix_consistent"]
        and matrix["coefficient_rank"] > 0
        and heldout["heldout_tested"] > 0
        and heldout["heldout_passed"] == heldout["heldout_tested"]
    )
    return {
        "columns": list(columns),
        "diagnostic_success": diagnostic_success,
        "heldout": heldout,
        "matrix": matrix,
        "noninjective": len(columns) < factor_count,
    }


def projection_scout(relations: list[dict[str, Any]], factor_count: int) -> list[dict[str, Any]]:
    active = sorted(
        {
            index
            for relation in relations
            for index, value in enumerate(factor_coeffs(relation, factor_count))
            if value % ORDER
        }
    )
    candidates = []
    for size in range(1, min(4, len(active)) + 1):
        for columns in itertools.combinations(active, size):
            candidates.append(projection_summary(relations, factor_count, columns))
    candidates.sort(
        key=lambda item: (
            0 if item.get("diagnostic_success") else 1,
            -int_value((item.get("matrix") or {}).get("coefficient_rank")),
            len(item.get("columns") or []),
            str(item.get("columns")),
        )
    )
    return candidates


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row.get("canonical_coeffs"),
        "canonical_rhs": row.get("canonical_rhs"),
        "factor_support": row.get("factor_support"),
        "pair_role": row.get("pair_role"),
        "public_fingerprint": row.get("public_fingerprint"),
        "q_coeffs": row.get("q_coeffs"),
        "row_key_signature": row.get("row_key_signature"),
        "salt_gap": row.get("salt_gap"),
        "salt_max": row.get("salt_max"),
        "salt_min": row.get("salt_min"),
    }


def summarize_scope(scope: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    relations, reconstruction = rows_for_scope(rows)
    factor_count = reconstruction["factor_count"]
    baseline_rows = [factor_coeffs(row, factor_count) for row in relations]
    baseline = matrix_summary(baseline_rows, rhs_values(relations)) if factor_count else matrix_summary([], [])
    lifted = [summarize_lifted_model(relations, model, factor_count) for model in lifted_models()] if factor_count else []
    projections = projection_scout(relations, factor_count) if factor_count else []
    controls = invertible_controls(relations, factor_count) if factor_count else []
    primary = [model for model in lifted if model.get("primary_success")]
    diagnostic = [projection for projection in projections if projection.get("diagnostic_success")]
    control_preserved = all(
        item["matrix"]["coefficient_rank"] == baseline["coefficient_rank"]
        and item["matrix"]["augmented_rank"] == baseline["augmented_rank"]
        and item["matrix"]["matrix_consistent"] == baseline["matrix_consistent"]
        for item in controls
    )
    return {
        "baseline": baseline,
        "diagnostic_projection_count": len(diagnostic),
        "diagnostic_projections": diagnostic[:8],
        "factor_count": factor_count,
        "invertible_control_preserved": control_preserved,
        "invertible_controls": controls,
        "lifted_model_summaries": lifted,
        "primary_model_count": len(primary),
        "primary_models": primary,
        "projection_scout_top": projections[:12],
        "reconstruction": reconstruction,
        "relation_count": len(relations),
        "relations": [compact_relation(row) for row in relations[:16]],
        "scope": scope,
    }


def determine_claim(scopes: list[dict[str, Any]]) -> str:
    if any(not scope.get("invertible_control_preserved") for scope in scopes):
        return "NEGATIVE_RESULT_P1030_INVERTIBLE_CONTROL_FAILED"
    if any(scope["reconstruction"]["reconstruction_error_count"] for scope in scopes):
        return "NEGATIVE_RESULT_P1030_RECONSTRUCTION_ERRORS"
    if any(scope.get("primary_model_count") for scope in scopes):
        return "P1030_QUOTIENT_NORMALIZED_REPRESENTATION_SIGNAL"
    if any(scope.get("diagnostic_projection_count") for scope in scopes):
        return "P1030_NONINJECTIVE_PROJECTION_DIAGNOSTIC_ONLY"
    return "NEGATIVE_RESULT_P1030_LINEAR_REPRESENTATION_CHANGES_NO_PROMOTION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scope_rows, exists = build_scopes(args)
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
            "p1029_dependency_sha256": p1005.sha256_file(Path(p1029.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1030_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: P1030 tests linear coordinate changes, lossy projections, and a fixed q/salt/public lift catalog only.",
            "RESTRICTED THEOREM: invertible linear factor-coordinate changes preserve coefficient and augmented ranks.",
            "INDEX-CALCULUS PRECURSOR: representation consistency is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline.",
        ],
        "parameters": {
            "fresh_windows": p1025.FRESH_WINDOWS,
            "lifted_models": [model["name"] for model in lifted_models()],
            "min_source_rank": args.min_source_rank,
            "negative_calibration_windows": p1022.NEGATIVE_CALIBRATION_WINDOWS,
            "projection_max_columns": 4,
            "scopes": list(scope_rows),
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {"exists": exists},
        "summary": {
            "claim_status": claim,
            "primary_model_count": sum(int_value(scope.get("primary_model_count")) for scope in scope_summaries),
            "diagnostic_projection_count": sum(int_value(scope.get("diagnostic_projection_count")) for scope in scope_summaries),
            "scope_count": len(scope_summaries),
            "scope_summaries": [
                {
                    "baseline": scope["baseline"],
                    "diagnostic_projection_count": scope["diagnostic_projection_count"],
                    "factor_count": scope["factor_count"],
                    "invertible_control_preserved": scope["invertible_control_preserved"],
                    "primary_model_count": scope["primary_model_count"],
                    "relation_count": scope["relation_count"],
                    "scope": scope["scope"],
                    "selected_count": scope["reconstruction"]["selection"]["selected_count"],
                    "fresh_false_count": scope["reconstruction"]["selection"]["fresh_false_count"],
                    "fresh_positive_count": scope["reconstruction"]["selection"]["fresh_positive_count"],
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
    scope_bits = []
    for scope in payload["summary"]["scope_summaries"]:
        baseline = scope["baseline"]
        scope_bits.append(
            "{scope}:rel={rel} rank={rank}/{aug} primary={primary} diag={diag}".format(
                scope=scope["scope"],
                rel=scope["relation_count"],
                rank=baseline["coefficient_rank"],
                aug=baseline["augmented_rank"],
                primary=scope["primary_model_count"],
                diag=scope["diagnostic_projection_count"],
            )
        )
    print(
        "claim={claim} primary={primary} diagnostics={diagnostics} out={out} {scopes}".format(
            claim=payload["claim_status"],
            primary=payload["summary"]["primary_model_count"],
            diagnostics=payload["summary"]["diagnostic_projection_count"],
            out=args.out,
            scopes="; ".join(scope_bits),
        )
    )


if __name__ == "__main__":
    main()
