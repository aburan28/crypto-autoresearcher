#!/usr/bin/env python3
"""P1027 public-context augmented quotient audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1027_p231_public_context_augmented_quotient.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1027_p231_public_context_augmented_quotient_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1027_p231_public_context_augmented_quotient.v1"
ORDER = p1026.ORDER


FeatureFn = Callable[[dict[str, Any], list[str]], list[int]]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def parse_public(public_fingerprint: str) -> tuple[int, int]:
    return p1026.parse_public(public_fingerprint)


def pad(values: list[int], width: int) -> list[int]:
    return values + [0] * max(0, width - len(values))


def rank_mod(matrix: list[list[int]], modulus: int) -> int:
    if not matrix:
        return 0
    width = max(len(row) for row in matrix)
    rows = [pad([int_value(value) % modulus for value in row], width) for row in matrix]
    return p1026.factor_bank.rank_mod(rows, modulus)


def matrix_summary(rows: list[list[int]], rhs: list[int], modulus: int) -> dict[str, Any]:
    coeff_rank = rank_mod(rows, modulus)
    augmented_rank = rank_mod([row + [rhs[index] % modulus] for index, row in enumerate(rows)], modulus)
    return {
        "augmented_rank": augmented_rank,
        "coefficient_rank": coeff_rank,
        "matrix_consistent": augmented_rank == coeff_rank,
        "row_count": len(rows),
    }


def context_models() -> list[dict[str, Any]]:
    return [
        {
            "description": "No public/context variables; reproduces raw quotient inconsistency.",
            "name": "factor_only",
            "predictive": True,
            "context_fn": lambda row, publics: [],
        },
        {
            "description": "One free context variable per observed public fingerprint; diagnostic only.",
            "name": "public_onehot_context",
            "predictive": False,
            "context_fn": lambda row, publics: [1 if row["public_fingerprint"] == public else 0 for public in publics],
        },
        {
            "description": "Affine public-coordinate context columns [1, x, y].",
            "name": "public_xy_context",
            "predictive": True,
            "context_fn": lambda row, publics: [1, *parse_public(str(row.get("public_fingerprint")))],
        },
        {
            "description": "Affine public symmetric columns [1, x+y, x-y].",
            "name": "public_sumdiff_context",
            "predictive": True,
            "context_fn": lambda row, publics: [
                1,
                (parse_public(str(row.get("public_fingerprint")))[0] + parse_public(str(row.get("public_fingerprint")))[1]) % ORDER,
                (parse_public(str(row.get("public_fingerprint")))[0] - parse_public(str(row.get("public_fingerprint")))[1]) % ORDER,
            ],
        },
        {
            "description": "Salt-pair context columns [1, salt_min, salt_max].",
            "name": "salt_minmax_context",
            "predictive": True,
            "context_fn": lambda row, publics: [1, int_value(row.get("salt_min")), int_value(row.get("salt_max"))],
        },
    ]


def relation_factor_coeffs(row: dict[str, Any], factor_count: int) -> list[int]:
    return pad([int_value(value) % ORDER for value in row.get("canonical_coeffs") or []], factor_count)


def model_rows(relations: list[dict[str, Any]], model: dict[str, Any], publics: list[str], factor_count: int) -> tuple[list[list[int]], list[list[int]], list[int]]:
    coeff_rows = []
    context_rows = []
    rhs = []
    for relation in relations:
        factors = relation_factor_coeffs(relation, factor_count)
        context = [int_value(value) % ORDER for value in model["context_fn"](relation, publics)]
        coeff_rows.append([*factors, *context])
        context_rows.append(context)
        rhs.append(int_value(relation.get("canonical_rhs")) % ORDER)
    return coeff_rows, context_rows, rhs


def heldout_public_check(relations: list[dict[str, Any]], model: dict[str, Any], publics: list[str], factor_count: int) -> dict[str, Any]:
    tested = 0
    passed = 0
    skipped = 0
    details = []
    for public in publics:
        train = [row for row in relations if row.get("public_fingerprint") != public]
        heldout = [row for row in relations if row.get("public_fingerprint") == public]
        if not train or not heldout:
            continue
        train_rows, _train_context, train_rhs = model_rows(train, model, publics, factor_count)
        train_summary = matrix_summary(train_rows, train_rhs, ORDER)
        if not train_summary["matrix_consistent"]:
            skipped += len(heldout)
            details.append({"heldout_public": public, "reason": "training matrix inconsistent", "tested": 0})
            continue
        train_augmented = [row + [train_rhs[index]] for index, row in enumerate(train_rows)]
        train_coeff_rank = rank_mod(train_rows, ORDER)
        train_aug_rank = rank_mod(train_augmented, ORDER)
        public_tested = 0
        public_passed = 0
        public_skipped = 0
        for relation in heldout:
            held_rows, _held_context, held_rhs = model_rows([relation], model, publics, factor_count)
            coeff_in_span = rank_mod([*train_rows, held_rows[0]], ORDER) == train_coeff_rank
            if not coeff_in_span:
                skipped += 1
                public_skipped += 1
                continue
            tested += 1
            public_tested += 1
            aug_in_span = rank_mod([*train_augmented, held_rows[0] + [held_rhs[0]]], ORDER) == train_aug_rank
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


def summarize_model(relations: list[dict[str, Any]], model: dict[str, Any], publics: list[str], factor_count: int) -> dict[str, Any]:
    coeff_rows, context_rows, rhs = model_rows(relations, model, publics, factor_count)
    full = matrix_summary(coeff_rows, rhs, ORDER)
    factor_matrix = [relation_factor_coeffs(row, factor_count) for row in relations]
    factor_rank = rank_mod(factor_matrix, ORDER)
    context_rank = rank_mod(context_rows, ORDER)
    factor_component_rank = max(0, full["coefficient_rank"] - context_rank)
    heldout = heldout_public_check(relations, model, publics, factor_count)
    predictive = bool(model["predictive"])
    primary_success = bool(
        predictive
        and full["matrix_consistent"]
        and factor_component_rank > 0
        and heldout["heldout_tested"] > 0
        and heldout["heldout_passed"] == heldout["heldout_tested"]
    )
    diagnostic_success = bool(
        not predictive
        and full["matrix_consistent"]
        and factor_component_rank > 0
    )
    return {
        "context_column_count": len(context_rows[0]) if context_rows else 0,
        "context_rank": context_rank,
        "description": model["description"],
        "diagnostic_success": diagnostic_success,
        "factor_component_rank": factor_component_rank,
        "factor_rank": factor_rank,
        "heldout": heldout,
        "matrix": full,
        "model": model["name"],
        "predictive_model": predictive,
        "primary_success": primary_success,
    }


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row.get("canonical_coeffs"),
        "canonical_rhs": row.get("canonical_rhs"),
        "pair_role": row.get("pair_role"),
        "public_fingerprint": row.get("public_fingerprint"),
        "public_xy": row.get("public_xy"),
        "salt_gap": row.get("salt_gap"),
        "salt_max": row.get("salt_max"),
        "salt_min": row.get("salt_min"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reconstructed = p1026.reconstruct_inputs(args)
    order = ORDER if reconstructed["form_orders"] == [ORDER] else 0
    relations, factor_count = p1026.collect_scope_relations(reconstructed["forms_by_public"], order, args.seed_public) if order else ([], 0)
    publics = sorted({str(row.get("public_fingerprint")) for row in relations})
    model_summaries = [summarize_model(relations, model, publics, factor_count) for model in context_models()]
    primary_models = [model for model in model_summaries if model.get("primary_success")]
    diagnostic_models = [model for model in model_summaries if model.get("diagnostic_success")]
    seed_rows = [row for row in relations if row.get("public_fingerprint") == args.seed_public]
    seed_bank = p1025.quotient_bank_summary(seed_rows, order, factor_count) if order else {}
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed["reconstructed"])
    if reconstructed["negative_rows"]:
        claim = "NEGATIVE_RESULT_P1027_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif len(reconstructed["training_rows"]) != 14 or len(reconstructed["fresh_rows"]) != 3:
        claim = "NEGATIVE_RESULT_P1027_UNEXPECTED_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1027_RECONSTRUCTION_ERRORS"
    elif reconstructed["form_orders"] != [ORDER]:
        claim = "NEGATIVE_RESULT_P1027_INCONSISTENT_FORM_ORDER"
    elif seed_bank.get("rank") != 2 or not seed_bank.get("matrix_consistent"):
        claim = "NEGATIVE_RESULT_P1027_SEED_QUOTIENT_NOT_REPRODUCED"
    elif primary_models:
        claim = "P1027_PREDICTIVE_PUBLIC_CONTEXT_FACTOR_SIGNAL"
    elif diagnostic_models:
        claim = "P1027_NONPREDICTIVE_CONTEXT_CONSISTENCY_ONLY"
    else:
        claim = "NEGATIVE_RESULT_P1027_PUBLIC_CONTEXT_AUGMENTATION_NO_PROMOTION"
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
            "p1026_dependency_sha256": p1005.sha256_file(Path(p1026.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1027_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: context augmentation is tested only on P1026 quotient rows.",
            "INDEX-CALCULUS PRECURSOR: context consistency is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; this audit tests representation structure only.",
        ],
        "parameters": {
            "context_models": [model["name"] for model in context_models()],
            "fresh_windows": p1025.FRESH_WINDOWS,
            "modulus": ORDER,
            "seed_public": args.seed_public,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "schema": SCHEMA,
        "source": {
            "exists": reconstructed["exists"],
        },
        "summary": {
            "diagnostic_model_count": len(diagnostic_models),
            "diagnostic_models": diagnostic_models,
            "factor_count": factor_count,
            "fresh_selected_count": len(reconstructed["fresh_rows"]),
            "model_summaries": model_summaries,
            "negative_control_selected_count": len(reconstructed["negative_rows"]),
            "primary_model_count": len(primary_models),
            "primary_models": primary_models,
            "public_count": len(publics),
            "publics": publics,
            "reconstruction_error_count": reconstruction_error_count,
            "relation_count": len(relations),
            "seed_bank": seed_bank,
            "training_selected_count": len(reconstructed["training_rows"]),
        },
        "relations": [compact_relation(row) for row in relations],
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
        "claim={claim} relations={relations} publics={publics} primary={primary} "
        "diagnostic={diagnostic} seed_rank={seed_rank} out={out}".format(
            claim=payload["claim_status"],
            relations=summary["relation_count"],
            publics=summary["public_count"],
            primary=summary["primary_model_count"],
            diagnostic=summary["diagnostic_model_count"],
            seed_rank=(summary.get("seed_bank") or {}).get("rank"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
