#!/usr/bin/env python3
"""P1026 affine-RHS obstruction audit for P1025 quotient rows."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1010_p231_stress_row_completion_11992 as p1010
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1026_p231_affine_rhs_obstruction_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1026_p231_affine_rhs_obstruction_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1026_p231_affine_rhs_obstruction_audit.v1"
ORDER = 11779
SALT_RE = re.compile(r"salt(\d+)")


FeatureFn = Callable[[dict[str, Any]], list[int]]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def parse_public(public_fingerprint: str) -> tuple[int, int]:
    try:
        value = json.loads(public_fingerprint)
    except json.JSONDecodeError:
        return 0, 0
    if isinstance(value, list) and len(value) >= 2:
        return int_value(value[0]) % ORDER, int_value(value[1]) % ORDER
    return 0, 0


def salt_values(row_keys: list[str]) -> list[int]:
    values = []
    for key in row_keys:
        match = SALT_RE.search(str(key))
        if match:
            values.append(int(match.group(1)))
    return sorted(values)


def salt_features(row_keys: list[str]) -> dict[str, int]:
    values = salt_values(row_keys)
    if not values:
        return {"salt_count": 0, "salt_gap": 0, "salt_max": 0, "salt_min": 0, "salt_sum": 0}
    return {
        "salt_count": len(values),
        "salt_gap": max(values) - min(values),
        "salt_max": max(values),
        "salt_min": min(values),
        "salt_sum": sum(values),
    }


def split_set(form: dict[str, Any]) -> set[str]:
    return p1025.split_set(form)


def relation_role(left: dict[str, Any], right: dict[str, Any]) -> str:
    return p1025.pair_role(left, right)


def reconstruct_inputs(args: argparse.Namespace) -> dict[str, Any]:
    training_windows = [*p1022.POSITIVE_CALIBRATION_WINDOWS, *p1022.VALIDATION_WINDOWS]
    all_windows = [*training_windows, *p1022.NEGATIVE_CALIBRATION_WINDOWS, *p1025.FRESH_WINDOWS]
    by_window, exists = p1010.build_window_rows(all_windows, args.targets, args.min_source_rank)
    training_rows = p1025.selected_rows_for_many(training_windows, by_window, "training_seed")
    negative_rows = p1025.selected_rows_for_many(p1022.NEGATIVE_CALIBRATION_WINDOWS, by_window, "negative_control")
    fresh_rows = p1025.selected_rows_for_many(p1025.FRESH_WINDOWS, by_window, "fresh_validation")
    training_reconstructed, training_forms = p1025.reconstruct_partition(training_rows)
    fresh_reconstructed, fresh_forms = p1025.reconstruct_partition(fresh_rows)
    forms = [*training_forms, *fresh_forms]
    form_orders = sorted({int_value(form.get("order")) for form in forms if int_value(form.get("order"))})
    forms_by_public: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        forms_by_public[str(form.get("public_fingerprint"))].append(form)
    return {
        "all_windows": all_windows,
        "exists": exists,
        "forms_by_public": forms_by_public,
        "form_orders": form_orders,
        "fresh_rows": fresh_rows,
        "negative_rows": negative_rows,
        "reconstructed": [*training_reconstructed, *fresh_reconstructed],
        "training_rows": training_rows,
    }


def target_relations_for_group(public: str, forms: list[dict[str, Any]], order: int) -> tuple[list[dict[str, Any]], int]:
    unique = p1023.unique_forms(forms)
    factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in unique] or [0])
    relations: list[dict[str, Any]] = []
    for left_index, left in enumerate(unique):
        for right_index in range(left_index + 1, len(unique)):
            right = unique[right_index]
            q_left, factors_left, rhs_left = factor_bank.form_parts(left, order, factor_count)
            q_right, factors_right, rhs_right = factor_bank.form_parts(right, order, factor_count)
            factor_coeffs = [
                (q_right * factors_left[index] - q_left * factors_right[index]) % order
                for index in range(factor_count)
            ]
            rhs = (q_right * rhs_left - q_left * rhs_right) % order
            canonical = factor_bank.canonical_relation(factor_coeffs, rhs, order)
            row_keys = sorted({*(str(value) for value in left.get("row_keys") or []), *(str(value) for value in right.get("row_keys") or [])})
            salts = salt_features(row_keys)
            base = {
                "left_form_index": left_index,
                "left_splits": sorted(split_set(left)),
                "pair": [left_index, right_index],
                "pair_role": relation_role(left, right),
                "public_fingerprint": public,
                "public_xy": list(parse_public(public)),
                "q_coeffs": [q_left, q_right],
                "right_form_index": right_index,
                "right_splits": sorted(split_set(right)),
                "row_key_signature": json_key(row_keys),
                "row_keys": row_keys,
                **salts,
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


def collect_scope_relations(forms_by_public: dict[str, list[dict[str, Any]]], order: int, seed_public: str) -> tuple[list[dict[str, Any]], int]:
    relations: list[dict[str, Any]] = []
    factor_count = 0
    for public, forms in sorted(forms_by_public.items()):
        has_fresh = any("fresh_validation" in split_set(form) for form in forms)
        if public != seed_public and not has_fresh:
            continue
        group_relations, group_factor_count = target_relations_for_group(public, forms, order)
        factor_count = max(factor_count, group_factor_count)
        for relation in group_relations:
            if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION":
                relations.append(relation)
    return relations, factor_count


def feature_models() -> list[dict[str, Any]]:
    return [
        {"features": ["1"], "name": "constant", "promotable": True, "fn": lambda row: [1]},
        {"features": ["1", "public_x"], "name": "public_x_affine", "promotable": True, "fn": lambda row: [1, row["public_xy"][0]]},
        {"features": ["1", "public_y"], "name": "public_y_affine", "promotable": True, "fn": lambda row: [1, row["public_xy"][1]]},
        {
            "features": ["1", "public_sum"],
            "name": "public_sum_affine",
            "promotable": True,
            "fn": lambda row: [1, (row["public_xy"][0] + row["public_xy"][1]) % ORDER],
        },
        {
            "features": ["1", "public_diff"],
            "name": "public_diff_affine",
            "promotable": True,
            "fn": lambda row: [1, (row["public_xy"][0] - row["public_xy"][1]) % ORDER],
        },
        {
            "features": ["1", "public_product"],
            "name": "public_product_affine",
            "promotable": True,
            "fn": lambda row: [1, (row["public_xy"][0] * row["public_xy"][1]) % ORDER],
        },
        {"features": ["1", "salt_sum"], "name": "salt_sum_affine", "promotable": True, "fn": lambda row: [1, row["salt_sum"]]},
        {"features": ["1", "salt_gap"], "name": "salt_gap_affine", "promotable": True, "fn": lambda row: [1, row["salt_gap"]]},
        {"features": ["1", "salt_min"], "name": "salt_min_affine", "promotable": True, "fn": lambda row: [1, row["salt_min"]]},
        {"features": ["1", "salt_max"], "name": "salt_max_affine", "promotable": True, "fn": lambda row: [1, row["salt_max"]]},
        {"features": ["1", "public_x", "public_y"], "name": "public_xy_interpolation", "promotable": False, "fn": lambda row: [1, row["public_xy"][0], row["public_xy"][1]]},
        {"features": ["1", "salt_min", "salt_max"], "name": "salt_minmax_interpolation", "promotable": False, "fn": lambda row: [1, row["salt_min"], row["salt_max"]]},
    ]


def predict(features: list[int], coefficients: list[int], order: int) -> int:
    return sum((value % order) * (coefficients[index] % order) for index, value in enumerate(features)) % order


def fit_model(samples: list[dict[str, Any]], model: dict[str, Any], order: int) -> dict[str, Any]:
    matrix = [[int_value(value) % order for value in model["fn"](sample)] for sample in samples]
    rhs = [int_value(sample.get("canonical_rhs")) % order for sample in samples]
    feature_count = len(matrix[0]) if matrix else 0
    rank = factor_bank.rank_mod(matrix, order) if matrix else 0
    solution = factor_bank.solve_mod(matrix, rhs, order) if matrix else None
    exact = bool(solution is not None and all(predict(matrix[index], solution, order) == rhs[index] for index in range(len(samples))))
    loo_tested = 0
    loo_passed = 0
    loo_skipped = 0
    for holdout in range(len(samples)):
        train_matrix = [row for index, row in enumerate(matrix) if index != holdout]
        train_rhs = [value for index, value in enumerate(rhs) if index != holdout]
        train_rank = factor_bank.rank_mod(train_matrix, order) if train_matrix else 0
        if train_rank < feature_count:
            loo_skipped += 1
            continue
        train_solution = factor_bank.solve_mod(train_matrix, train_rhs, order)
        if train_solution is None:
            loo_skipped += 1
            continue
        loo_tested += 1
        if predict(matrix[holdout], train_solution, order) == rhs[holdout]:
            loo_passed += 1
    return {
        "exact_fit": exact,
        "feature_count": feature_count,
        "feature_rank": rank,
        "features": model["features"],
        "loo_passed": loo_passed,
        "loo_skipped": loo_skipped,
        "loo_tested": loo_tested,
        "model": model["name"],
        "promotable_model_family": bool(model["promotable"]),
        "solution": solution,
        "underfit_or_inconsistent": solution is None,
        "viable_normalization": bool(model["promotable"] and exact and loo_tested == len(samples) and loo_passed == len(samples)),
    }


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row.get("canonical_coeffs"),
        "canonical_rhs": row.get("canonical_rhs"),
        "pair_role": row.get("pair_role"),
        "public_fingerprint": row.get("public_fingerprint"),
        "public_xy": row.get("public_xy"),
        "row_key_signature": row.get("row_key_signature"),
        "salt_gap": row.get("salt_gap"),
        "salt_max": row.get("salt_max"),
        "salt_min": row.get("salt_min"),
        "salt_sum": row.get("salt_sum"),
    }


def summarize_cluster(coeff_key: str, samples: list[dict[str, Any]], order: int) -> dict[str, Any]:
    rhs_values = sorted({int_value(sample.get("canonical_rhs")) % order for sample in samples})
    public_values = sorted({str(sample.get("public_fingerprint")) for sample in samples})
    model_results = [fit_model(samples, model, order) for model in feature_models()]
    viable = [result for result in model_results if result.get("viable_normalization")]
    exact_interpolations = [
        result
        for result in model_results
        if result.get("exact_fit") and not result.get("viable_normalization")
    ]
    return {
        "coefficient_key": coeff_key,
        "coefficients": samples[0].get("canonical_coeffs") if samples else [],
        "distinct_public_count": len(public_values),
        "distinct_publics": public_values,
        "distinct_rhs_count": len(rhs_values),
        "distinct_rhs_values": rhs_values,
        "exact_nonpromoted_model_count": len(exact_interpolations),
        "model_results": model_results,
        "sample_count": len(samples),
        "samples": [compact_relation(sample) for sample in samples],
        "viable_model_count": len(viable),
        "viable_models": viable,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reconstructed = reconstruct_inputs(args)
    order = ORDER if reconstructed["form_orders"] == [ORDER] else 0
    all_relations, factor_count = collect_scope_relations(reconstructed["forms_by_public"], order, args.seed_public) if order else ([], 0)
    clusters: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation in all_relations:
        clusters[json_key(relation.get("canonical_coeffs") or [])].append(relation)
    cluster_summaries = [
        summarize_cluster(coeff_key, samples, order)
        for coeff_key, samples in sorted(clusters.items())
        if len(samples) >= 2
    ]
    rhs_collision_clusters = [cluster for cluster in cluster_summaries if int_value(cluster.get("distinct_rhs_count")) > 1]
    viable_clusters = [cluster for cluster in rhs_collision_clusters if int_value(cluster.get("viable_model_count")) > 0]
    seed_rows = [relation for relation in all_relations if relation.get("public_fingerprint") == args.seed_public]
    seed_bank = p1025.quotient_bank_summary(seed_rows, order, factor_count) if order else {}
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed["reconstructed"])
    fresh_rows = reconstructed["fresh_rows"]
    negative_rows = reconstructed["negative_rows"]
    training_rows = reconstructed["training_rows"]
    repeated_coeff_011 = next(
        (
            cluster
            for cluster in rhs_collision_clusters
            if cluster.get("coefficients") and cluster["coefficients"][:3] == [0, 1, 1]
        ),
        None,
    )
    if negative_rows:
        claim = "NEGATIVE_RESULT_P1026_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif len(training_rows) != 14 or len(fresh_rows) != 3:
        claim = "NEGATIVE_RESULT_P1026_UNEXPECTED_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1026_RECONSTRUCTION_ERRORS"
    elif reconstructed["form_orders"] != [ORDER]:
        claim = "NEGATIVE_RESULT_P1026_INCONSISTENT_FORM_ORDER"
    elif not all(reconstructed["exists"].get(window) for window in p1025.FRESH_WINDOWS):
        claim = "NEGATIVE_RESULT_P1026_MISSING_FRESH_SOURCE_WINDOWS"
    elif seed_bank.get("rank") != 2 or not seed_bank.get("matrix_consistent"):
        claim = "NEGATIVE_RESULT_P1026_SEED_QUOTIENT_NOT_REPRODUCED"
    elif viable_clusters:
        claim = "P1026_AFFINE_RHS_NORMALIZATION_CANDIDATE"
    elif rhs_collision_clusters:
        claim = "NEGATIVE_RESULT_P1026_AFFINE_RHS_OBSTRUCTION_STANDS"
    else:
        claim = "NEGATIVE_RESULT_P1026_NO_REPEATED_RHS_COLLISION_CLUSTER"
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in reconstructed["all_windows"]
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1025_dependency_sha256": p1005.sha256_file(Path(p1025.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1026_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: only low-parameter affine public/salt models are tested.",
            "INDEX-CALCULUS PRECURSOR: RHS normalization is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; this audit tests quotient namespace consistency only.",
        ],
        "parameters": {
            "fresh_windows": p1025.FRESH_WINDOWS,
            "min_source_rank": args.min_source_rank,
            "modulus": ORDER,
            "seed_public": args.seed_public,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {
            "exists": reconstructed["exists"],
        },
        "summary": {
            "factor_count": factor_count,
            "fresh_selected_count": len(fresh_rows),
            "negative_control_selected_count": len(negative_rows),
            "reconstruction_error_count": reconstruction_error_count,
            "repeated_coeff_011_cluster": repeated_coeff_011,
            "repeated_cluster_count": len(cluster_summaries),
            "rhs_collision_cluster_count": len(rhs_collision_clusters),
            "seed_bank": seed_bank,
            "selected_relation_count": len(all_relations),
            "training_selected_count": len(training_rows),
            "viable_normalization_cluster_count": len(viable_clusters),
            "viable_normalization_clusters": viable_clusters,
        },
        "rhs_collision_clusters": rhs_collision_clusters,
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for builder labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--seed-public", default=p1025.SEED_PUBLIC, help="Seed public fingerprint")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} relations={relations} repeated={repeated} rhs_collisions={collisions} "
        "viable={viable} seed_rank={seed_rank} out={out}".format(
            claim=payload["claim_status"],
            relations=summary["selected_relation_count"],
            repeated=summary["repeated_cluster_count"],
            collisions=summary["rhs_collision_cluster_count"],
            viable=summary["viable_normalization_cluster_count"],
            seed_rank=(summary.get("seed_bank") or {}).get("rank"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
