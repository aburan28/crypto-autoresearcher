#!/usr/bin/env python3
"""P1028 relation-class split audit for leaf-19 quotient rows."""

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
import low_term_total2_p1026_p231_affine_rhs_obstruction_audit as p1026
import low_term_total2_p1027_p231_public_context_augmented_quotient as p1027


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1028_p231_relation_class_split_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1028_p231_relation_class_split_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1028_p231_relation_class_split_audit.v1"
ORDER = p1026.ORDER

KeyFn = Callable[[dict[str, Any]], str]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def relation_coeffs(row: dict[str, Any], factor_count: int) -> list[int]:
    return p1027.relation_factor_coeffs(row, factor_count)


def matrix_summary(relations: list[dict[str, Any]], factor_count: int) -> dict[str, Any]:
    rows = [relation_coeffs(row, factor_count) for row in relations]
    rhs = [int_value(row.get("canonical_rhs")) % ORDER for row in relations]
    return p1027.matrix_summary(rows, rhs, ORDER)


def heldout_public_check(relations: list[dict[str, Any]], factor_count: int) -> dict[str, Any]:
    publics = sorted({str(row.get("public_fingerprint")) for row in relations})
    tested = 0
    passed = 0
    skipped = 0
    details = []
    for public in publics:
        train = [row for row in relations if row.get("public_fingerprint") != public]
        heldout = [row for row in relations if row.get("public_fingerprint") == public]
        if not train or not heldout:
            continue
        train_rows = [relation_coeffs(row, factor_count) for row in train]
        train_rhs = [int_value(row.get("canonical_rhs")) % ORDER for row in train]
        train_summary = p1027.matrix_summary(train_rows, train_rhs, ORDER)
        if not train_summary["matrix_consistent"]:
            skipped += len(heldout)
            details.append({"heldout_public": public, "reason": "training matrix inconsistent", "tested": 0})
            continue
        train_augmented = [row + [train_rhs[index]] for index, row in enumerate(train_rows)]
        train_coeff_rank = p1027.rank_mod(train_rows, ORDER)
        train_aug_rank = p1027.rank_mod(train_augmented, ORDER)
        public_tested = 0
        public_passed = 0
        public_skipped = 0
        for relation in heldout:
            held_row = relation_coeffs(relation, factor_count)
            held_rhs = int_value(relation.get("canonical_rhs")) % ORDER
            coeff_in_span = p1027.rank_mod([*train_rows, held_row], ORDER) == train_coeff_rank
            if not coeff_in_span:
                skipped += 1
                public_skipped += 1
                continue
            tested += 1
            public_tested += 1
            aug_in_span = p1027.rank_mod([*train_augmented, held_row + [held_rhs]], ORDER) == train_aug_rank
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


def coefficient_family(row: dict[str, Any]) -> str:
    coeffs = [int_value(value) % ORDER for value in row.get("canonical_coeffs") or []]
    tail_zero = all(value == 0 for value in coeffs[3:])
    if len(coeffs) >= 3 and tail_zero and coeffs[0] == 0 and coeffs[1] == 1 and coeffs[2] == 1:
        return "zero_target_tail_1_1"
    if len(coeffs) >= 3 and tail_zero and coeffs[0] == 1 and coeffs[2] == (coeffs[1] + 1) % ORDER:
        return "unit_target_adjacent_tail"
    if len(coeffs) >= 3 and tail_zero:
        return "three_column_other"
    return "other"


def q_order_pattern(row: dict[str, Any]) -> str:
    q = [int_value(value) % ORDER for value in row.get("q_coeffs") or []]
    if len(q) < 2:
        return "q_unknown"
    if q[0] == q[1]:
        return "q_equal"
    if q[0] < q[1]:
        return "q_ascending"
    return "q_descending"


def class_specs() -> list[dict[str, Any]]:
    return [
        {"name": "exact_coefficients", "fn": lambda row: json_key(row.get("canonical_coeffs") or [])},
        {"name": "support_tuple", "fn": lambda row: json_key(row.get("factor_support") or [])},
        {"name": "support_size", "fn": lambda row: str(row.get("factor_support_size"))},
        {"name": "coefficient_family", "fn": coefficient_family},
        {"name": "exact_q_coefficients", "fn": lambda row: json_key(row.get("q_coeffs") or [])},
        {"name": "q_order_pattern", "fn": q_order_pattern},
        {"name": "salt_pair_signature", "fn": lambda row: json_key([row.get("salt_min"), row.get("salt_max")])},
        {"name": "row_key_signature", "fn": lambda row: str(row.get("row_key_signature"))},
    ]


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row.get("canonical_coeffs"),
        "canonical_rhs": row.get("canonical_rhs"),
        "coefficient_family": coefficient_family(row),
        "factor_support": row.get("factor_support"),
        "factor_support_size": row.get("factor_support_size"),
        "pair_role": row.get("pair_role"),
        "public_fingerprint": row.get("public_fingerprint"),
        "q_coeffs": row.get("q_coeffs"),
        "q_order_pattern": q_order_pattern(row),
        "row_key_signature": row.get("row_key_signature"),
        "salt_max": row.get("salt_max"),
        "salt_min": row.get("salt_min"),
    }


def summarize_class(partition: str, key: str, relations: list[dict[str, Any]], factor_count: int) -> dict[str, Any]:
    summary = matrix_summary(relations, factor_count)
    heldout = heldout_public_check(relations, factor_count)
    distinct_publics = sorted({str(row.get("public_fingerprint")) for row in relations})
    promotable = bool(
        len(distinct_publics) >= 2
        and summary["matrix_consistent"]
        and summary["coefficient_rank"] > 0
        and heldout["heldout_tested"] > 0
        and heldout["heldout_passed"] == heldout["heldout_tested"]
    )
    diagnostic = bool(summary["matrix_consistent"] and summary["coefficient_rank"] > 0 and not promotable)
    return {
        "class_key": key,
        "diagnostic_consistent_only": diagnostic,
        "distinct_public_count": len(distinct_publics),
        "distinct_publics": distinct_publics,
        "heldout": heldout,
        "matrix": summary,
        "partition": partition,
        "promotable": promotable,
        "relation_count": len(relations),
        "relations": [compact_relation(row) for row in relations[:12]],
    }


def relation_classes(relations: list[dict[str, Any]], factor_count: int) -> list[dict[str, Any]]:
    classes = []
    for spec in class_specs():
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for relation in relations:
            grouped[spec["fn"](relation)].append(relation)
        for key, rows in sorted(grouped.items()):
            if len(rows) < 2:
                continue
            classes.append(summarize_class(spec["name"], key, rows, factor_count))
    classes.sort(
        key=lambda item: (
            0 if item.get("promotable") else 1,
            0 if item.get("diagnostic_consistent_only") else 1,
            -int_value((item.get("matrix") or {}).get("coefficient_rank")),
            -int_value(item.get("relation_count")),
            str(item.get("partition")),
            str(item.get("class_key")),
        )
    )
    return classes


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reconstructed = p1026.reconstruct_inputs(args)
    order = ORDER if reconstructed["form_orders"] == [ORDER] else 0
    relations, factor_count = p1026.collect_scope_relations(reconstructed["forms_by_public"], order, args.seed_public) if order else ([], 0)
    full_summary = matrix_summary(relations, factor_count)
    classes = relation_classes(relations, factor_count)
    promotable = [item for item in classes if item.get("promotable")]
    diagnostic = [item for item in classes if item.get("diagnostic_consistent_only")]
    inconsistent = [item for item in classes if not item.get("promotable") and not item.get("diagnostic_consistent_only")]
    seed_rows = [row for row in relations if row.get("public_fingerprint") == args.seed_public]
    seed_bank = p1025.quotient_bank_summary(seed_rows, order, factor_count) if order else {}
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed["reconstructed"])
    if reconstructed["negative_rows"]:
        claim = "NEGATIVE_RESULT_P1028_NEGATIVE_CONTROL_SELECTED_ROWS"
    elif len(reconstructed["training_rows"]) != 14 or len(reconstructed["fresh_rows"]) != 3:
        claim = "NEGATIVE_RESULT_P1028_UNEXPECTED_SELECTION_SHAPE"
    elif reconstruction_error_count:
        claim = "NEGATIVE_RESULT_P1028_RECONSTRUCTION_ERRORS"
    elif reconstructed["form_orders"] != [ORDER]:
        claim = "NEGATIVE_RESULT_P1028_INCONSISTENT_FORM_ORDER"
    elif seed_bank.get("rank") != 2 or not seed_bank.get("matrix_consistent"):
        claim = "NEGATIVE_RESULT_P1028_SEED_QUOTIENT_NOT_REPRODUCED"
    elif full_summary["coefficient_rank"] != 2 or full_summary["augmented_rank"] != 3:
        claim = "NEGATIVE_RESULT_P1028_FACTOR_ONLY_CONTROL_MISMATCH"
    elif promotable:
        claim = "P1028_PROMOTABLE_RELATION_CLASS_FOUND"
    elif diagnostic:
        claim = "P1028_DIAGNOSTIC_CONSISTENT_CLASSES_ONLY"
    else:
        claim = "NEGATIVE_RESULT_P1028_NO_CONSISTENT_RELATION_CLASS"
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
            "p1027_dependency_sha256": p1005.sha256_file(Path(p1027.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1028_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "MODEL-BOUND: relation classes are limited to quotient-row signatures in the current leaf-19 family.",
            "INDEX-CALCULUS PRECURSOR: class consistency is not sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target baseline; this audit tests relation-class structure only.",
        ],
        "parameters": {
            "class_partitions": [spec["name"] for spec in class_specs()],
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
            "class_count": len(classes),
            "diagnostic_class_count": len(diagnostic),
            "diagnostic_classes": diagnostic[:8],
            "factor_count": factor_count,
            "fresh_selected_count": len(reconstructed["fresh_rows"]),
            "full_factor_only_summary": full_summary,
            "inconsistent_class_count": len(inconsistent),
            "negative_control_selected_count": len(reconstructed["negative_rows"]),
            "promotable_class_count": len(promotable),
            "promotable_classes": promotable[:8],
            "reconstruction_error_count": reconstruction_error_count,
            "relation_count": len(relations),
            "seed_bank": seed_bank,
            "training_selected_count": len(reconstructed["training_rows"]),
        },
        "classes": classes[:40],
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
        "claim={claim} relations={relations} classes={classes} promotable={promotable} "
        "diagnostic={diagnostic} full_rank={rank}/{aug} out={out}".format(
            claim=payload["claim_status"],
            relations=summary["relation_count"],
            classes=summary["class_count"],
            promotable=summary["promotable_class_count"],
            diagnostic=summary["diagnostic_class_count"],
            rank=summary["full_factor_only_summary"]["coefficient_rank"],
            aug=summary["full_factor_only_summary"]["augmented_rank"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
