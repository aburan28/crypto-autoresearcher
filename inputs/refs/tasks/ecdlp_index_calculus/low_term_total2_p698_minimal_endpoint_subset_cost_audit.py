#!/usr/bin/env python3
"""P698 minimal endpoint subset and replay-cost audit.

P697 showed that all P696 endpoint-coefficient forms close the order-9887
factor-bank gap.  This audit searches for the smallest endpoint-form subset
that still derives the missing columns, then charges the unique leaf scans that
emit those forms.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p691_factor_bank_deficiency_target_audit as p691
import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = p697.DEFAULT_SOURCE
DEFAULT_PRODUCT = p697.DEFAULT_PRODUCT
DEFAULT_OUT = STATE_DIR / "low_term_total2_p698_minimal_endpoint_subset_cost_audit_probe.json"
ORDER = p697.ORDER


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def scan_key(record: dict[str, Any]) -> tuple[str, int]:
    return str(record.get("row_key")), int_value(record.get("leaf_index"))


def scan_cost(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_key: dict[tuple[str, int], dict[str, Any]] = {}
    for record in records:
        key = scan_key(record)
        by_key.setdefault(
            key,
            {
                "direct_ops_over_rho": float_value(record.get("direct_ops_over_rho")),
                "leaf_index": key[1],
                "row_key": key[0],
            },
        )
    return {
        "unique_leaf_scan_count": len(by_key),
        "unique_leaf_scan_ops_over_rho": round(
            sum(float_value(item.get("direct_ops_over_rho")) for item in by_key.values()),
            8,
        ),
        "unique_leaf_scans": sorted(by_key.values(), key=lambda item: (item["row_key"], item["leaf_index"])),
    }


def empty_union() -> dict[str, Any]:
    return {
        "union_derived_secret": None,
        "union_public_key_verified": False,
        "union_rank": 0,
        "union_relation_count": 0,
    }


def candidate_state_for_records(records: list[dict[str, Any]], target: str) -> dict[str, Any]:
    cert = p697.pseudo_certificate("p698_subset_candidate", records, target, empty_union())
    return p697.bank_state([cert])


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row["canonical_coeffs"],
        "canonical_rhs": row["canonical_rhs"],
        "factor_support": row["factor_support"],
        "multiplicity": row.get("multiplicity"),
        "pair": row.get("pair"),
    }


def evaluate_subset(
    indices: tuple[int, ...],
    records: list[dict[str, Any]],
    target: str,
    base_state: dict[str, Any],
    base_relation_keys: set[tuple[tuple[int, ...], int]],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    chosen = [records[index] for index in indices]
    candidate_state = candidate_state_for_records(chosen, target)
    new_unique = [
        row for row in candidate_state["unique"] if p697.relation_key(row) not in base_relation_keys
    ]
    with_matrix = base_state["matrix"] + [row["canonical_coeffs"] for row in new_unique]
    with_rhs = base_state["rhs"] + [int_value(row["canonical_rhs"]) % ORDER for row in new_unique]
    rank_after = factor_bank.rank_mod(with_matrix, ORDER)
    augmented_rank_after = factor_bank.rank_mod(
        [row + [with_rhs[index]] for index, row in enumerate(with_matrix)],
        ORDER,
    )
    columns_after, missing_after = p691.derive_columns(
        with_matrix,
        with_rhs,
        int_value(base_state["factor_count"]),
    )
    base_derivable = sum(1 for column in base_state["columns"] if column["derivable"])
    after_derivable = sum(1 for column in columns_after if column["derivable"])
    missing_set = set(priority_columns)
    new_missing_touch = [row for row in new_unique if set(row["factor_support"]) & missing_set]
    newly_derivable_priority = sorted(
        column
        for column in priority_columns
        if column in set(base_state["missing_columns"]) and column not in set(missing_after)
    )
    costs = scan_cost(chosen)
    return {
        "augmented_rank_after": augmented_rank_after,
        "candidate_factor_relation_count": len(candidate_state["raw"]),
        "candidate_rank": candidate_state["rank"],
        "candidate_unique_factor_relation_count": len(candidate_state["unique"]),
        "candidate_unique_missing_touch_count": sum(
            1 for row in candidate_state["unique"] if set(row["factor_support"]) & missing_set
        ),
        "factor_variables_derivable_gain": after_derivable - base_derivable,
        "form_count": len(indices),
        "form_indices": list(indices),
        "matrix_consistent_after": augmented_rank_after == rank_after,
        "missing_columns_after": missing_after,
        "new_missing_touch_relation_count": len(new_missing_touch),
        "new_missing_touch_relation_samples": [
            compact_relation(row) for row in new_missing_touch[:sample_limit]
        ],
        "new_unique_factor_relation_count": len(new_unique),
        "newly_derivable_priority_columns": newly_derivable_priority,
        "rank_after": rank_after,
        "rank_before": base_state["rank"],
        "rank_gain": rank_after - base_state["rank"],
        "selected_form_samples": [
            p697.compact_event_sample(record) for record in chosen[:sample_limit]
        ],
        "unique_factor_relation_count_after": len(base_state["unique"]) + len(new_unique),
        "unique_factor_relation_count_before": len(base_state["unique"]),
        "unique_factor_relation_gain": len(new_unique),
        **costs,
    }


def closes_priority_gap(evaluation: dict[str, Any], priority_columns: set[int]) -> bool:
    return (
        int_value(evaluation.get("rank_gain")) >= len(priority_columns)
        and sorted(evaluation.get("newly_derivable_priority_columns") or []) == sorted(priority_columns)
        and bool(evaluation.get("matrix_consistent_after"))
    )


def attach_union_verification(
    evaluation: dict[str, Any],
    verifier: Any,
    records: list[dict[str, Any]],
    target: str,
) -> dict[str, Any]:
    chosen = [records[index] for index in evaluation["form_indices"]]
    union = p697.union_derive(verifier, chosen)
    out = dict(evaluation)
    out["union_derived_secret"] = union.get("union_derived_secret")
    out["union_public_key_verified"] = bool(union.get("union_public_key_verified"))
    out["union_rank"] = int_value(union.get("union_rank"))
    out["union_relation_count"] = int_value(union.get("union_relation_count"))
    out["certificate_status"] = (
        "PUBLIC_AGGREGATE_SUBSET_VERIFIES_TARGET"
        if out["union_public_key_verified"]
        else "RELATION_VALID_SUBSET_DOES_NOT_INDEPENDENTLY_DERIVE_TARGET"
    )
    return out


def subset_search(
    verifier: Any,
    records: list[dict[str, Any]],
    target: str,
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    base_relation_keys = {p697.relation_key(row) for row in base_state["unique"]}
    success_counts: Counter[int] = Counter()
    evaluated_counts: Counter[int] = Counter()
    first_closing_by_size: dict[int, dict[str, Any]] = {}
    minimal_rank_closing: dict[str, Any] | None = None
    minimal_verified: dict[str, Any] | None = None
    for size in range(2, len(records) + 1):
        for indices in itertools.combinations(range(len(records)), size):
            evaluated_counts[size] += 1
            evaluation = evaluate_subset(
                indices,
                records,
                target,
                base_state,
                base_relation_keys,
                priority_columns,
                sample_limit,
            )
            if not closes_priority_gap(evaluation, priority_columns):
                continue
            success_counts[size] += 1
            verified = attach_union_verification(evaluation, verifier, records, target)
            if size not in first_closing_by_size:
                first_closing_by_size[size] = verified
            if minimal_rank_closing is None or (
                verified["form_count"],
                verified["unique_leaf_scan_ops_over_rho"],
                -verified["unique_factor_relation_gain"],
            ) < (
                minimal_rank_closing["form_count"],
                minimal_rank_closing["unique_leaf_scan_ops_over_rho"],
                -minimal_rank_closing["unique_factor_relation_gain"],
            ):
                minimal_rank_closing = verified
            if verified["union_public_key_verified"] and (
                minimal_verified is None
                or (
                    verified["form_count"],
                    verified["unique_leaf_scan_ops_over_rho"],
                    -verified["unique_factor_relation_gain"],
                )
                < (
                    minimal_verified["form_count"],
                    minimal_verified["unique_leaf_scan_ops_over_rho"],
                    -minimal_verified["unique_factor_relation_gain"],
                )
            ):
                minimal_verified = verified
        if minimal_rank_closing is not None and minimal_verified is not None:
            break
    return {
        "evaluated_subset_counts_by_size": {
            str(size): evaluated_counts[size] for size in sorted(evaluated_counts)
        },
        "first_closing_subset_by_size": {
            str(size): first_closing_by_size[size] for size in sorted(first_closing_by_size)
        },
        "minimal_rank_closing_subset": minimal_rank_closing,
        "minimal_verified_subset": minimal_verified,
        "rank_closing_subset_counts_by_size": {
            str(size): success_counts[size] for size in sorted(success_counts)
        },
    }


def determine_claim(summary: dict[str, Any], minimal: dict[str, Any] | None) -> str:
    if not minimal:
        return "NEGATIVE_RESULT_P698_NO_PROPER_ENDPOINT_SUBSET_CLOSES_RANK_GAP"
    if float_value(minimal.get("unique_leaf_scan_ops_over_rho")) <= 1.0:
        return "P698_MINIMAL_ENDPOINT_SUBSET_BELOW_RHO_FULL_RANK"
    return "P698_MINIMAL_ENDPOINT_SUBSET_FULL_RANK_ABOVE_RHO_DIRECT_CHARGE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    verifier, row_contexts, context_cache_entry_count, missing_source_case_count = p697.build_row_contexts(args)
    mutation = p697.collect_mutation_records(
        verifier,
        row_contexts,
        priority_columns,
        int_value(args.max_endpoint_leaves),
    )
    endpoint_coeff_records = p697.unique_records(mutation["endpoint_coeff_records"])
    for index, record in enumerate(endpoint_coeff_records):
        record["_endpoint_form_index"] = index
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    full_endpoint_union = p697.union_derive(verifier, endpoint_coeff_records)
    full_endpoint_cert = p697.pseudo_certificate(
        "p698_full_endpoint_coeff_control",
        endpoint_coeff_records,
        args.target,
        full_endpoint_union,
    )
    full_endpoint_eval = p697.evaluate_candidate(
        "p698_full_endpoint_coeff_control",
        base,
        base_state,
        full_endpoint_cert,
        priority_columns,
        int_value(args.sample_limit, 12),
    )
    full_endpoint_eval.update(scan_cost(endpoint_coeff_records))
    search = subset_search(
        verifier,
        endpoint_coeff_records,
        args.target,
        base_state,
        priority_columns,
        int_value(args.sample_limit, 12),
    )
    minimal = search["minimal_rank_closing_subset"]
    summary = {
        "base_certificate_count": len(base),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": base_state["rank"],
        "base_unique_factor_relation_count": len(base_state["unique"]),
        "context_cache_entry_count": context_cache_entry_count,
        "endpoint_coeff_unique_form_count": len(endpoint_coeff_records),
        "endpoint_leaf_count": mutation["endpoint_leaf_count"],
        "endpoint_leaf_hit_root_count": mutation["endpoint_leaf_hit_root_count"],
        "excluded_p690_candidate_count": len(excluded_candidates),
        "full_endpoint_form_count": len(endpoint_coeff_records),
        "full_endpoint_rank_gain": int_value(full_endpoint_eval.get("rank_gain")),
        "full_endpoint_unique_leaf_scan_ops_over_rho": full_endpoint_eval[
            "unique_leaf_scan_ops_over_rho"
        ],
        "minimal_rank_closing_form_count": int_value((minimal or {}).get("form_count")),
        "minimal_rank_closing_ops_over_rho": (minimal or {}).get("unique_leaf_scan_ops_over_rho"),
        "minimal_verified_form_count": int_value((search["minimal_verified_subset"] or {}).get("form_count")),
        "minimal_verified_ops_over_rho": (search["minimal_verified_subset"] or {}).get(
            "unique_leaf_scan_ops_over_rho"
        ),
        "missing_source_case_count": missing_source_case_count,
        "priority_columns": sorted(priority_columns),
        "scanned_endpoint_leaf_count": mutation["scanned_endpoint_leaf_count"],
    }
    summary.update(
        {
            "priority_coeff_event_counts": {
                str(column): mutation["priority_coeff_counts"][column] for column in sorted(priority_columns)
            },
            "priority_leaf_counts": {
                str(column): mutation["priority_leaf_counts"][column] for column in sorted(priority_columns)
            },
        }
    )
    claim_status = determine_claim(summary, minimal)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "product": str(Path(args.product)),
            "source": str(Path(args.source)),
        },
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "full_endpoint_coeff_control": full_endpoint_eval,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: subset cost is charged for unique public leaf scans that emit chosen endpoint forms, not for a full public discovery policy.",
            "HEURISTIC: full rank in this toy factor bank is an index-calculus precursor, not a complete relation collection or target descent.",
            "A subset above rho is still useful for amortized index-calculus development but is not a direct individual-log win.",
        ],
        "method": "p698_minimal_endpoint_subset_cost_audit",
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "max_endpoint_leaves": int_value(args.max_endpoint_leaves),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p698_minimal_endpoint_subset_cost_audit.v1",
        "subset_search": search,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "minimal_rank_closing_subset": payload["subset_search"]["minimal_rank_closing_subset"],
                "minimal_verified_subset": payload["subset_search"]["minimal_verified_subset"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
