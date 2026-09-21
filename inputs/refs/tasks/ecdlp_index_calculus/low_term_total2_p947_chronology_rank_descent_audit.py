#!/usr/bin/env python3
"""P947 chronology-aware factor-bank rank/descent audit."""

from __future__ import annotations

import argparse
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (
    P939_SOURCE,
    int_value,
    load_rows,
    mean,
    now_iso,
    summarize_selected,
    window_start,
    write_json,
)
from tasks.ecdlp_index_calculus.low_term_total2_p944_past_support_seed import (
    Strategy,
    selected_by_strategy,
)


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p947_chronology_rank_descent_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p947_chronology_rank_descent_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p947_chronology_rank_descent_audit.v1"

P943_STRATEGY = Strategy(
    "p943_exact_hash_transfer_mod4",
    ("hash",),
    min_clean_count=2,
    transfer_modulus=4,
    transfer_radius=0,
)
P944_UNGUARDED_STRATEGY = Strategy(
    "p944_unguarded_same_hash_transfer_mod2",
    ("hash",),
    min_clean_count=2,
    transfer_modulus=2,
    transfer_radius=0,
)
P945_GUARDED_STRATEGY = Strategy(
    "p945_guarded_same_hash_transfer_mod2_even_holdout",
    ("hash",),
    min_clean_count=2,
    transfer_modulus=2,
    transfer_radius=0,
)

RELATION_EQUATION_FIELDS = (
    "base_order",
    "group_order",
    "order",
    "relation_coefficients",
    "linear_form_coefficients",
    "rhs",
    "relation_rhs",
    "scalar_rhs",
    "target_scalar_column",
    "factor_log_columns",
)


def sorted_windows(rows_by_window: dict[str, list[dict[str, Any]]]) -> list[str]:
    return sorted(rows_by_window, key=window_start)


def guarded_even_transfer(row: dict[str, Any]) -> bool:
    transfer = row.get("transfer_index")
    return transfer is not None and int(transfer) % 2 == 0


def row_vector(row: dict[str, Any]) -> list[int] | None:
    values = [row.get("constant"), row.get("b_coeff"), row.get("c_coeff")]
    if any(value is None for value in values):
        return None
    return [int(value) for value in values]


def modular_rank(matrix: list[list[int]], modulus: int) -> dict[str, Any]:
    if not matrix:
        return {"rank": 0, "row_count": 0, "column_count": 0, "nonunit_pivot_obstruction_count": 0}
    rows = [[int(cell) % modulus for cell in row] for row in matrix]
    row_count = len(rows)
    col_count = max((len(row) for row in rows), default=0)
    for row in rows:
        row.extend([0] * (col_count - len(row)))
    rank = 0
    nonunit_obstructions = 0
    for col in range(col_count):
        pivot = None
        nonunit_seen = False
        for pos in range(rank, row_count):
            value = rows[pos][col] % modulus
            if value == 0:
                continue
            if math.gcd(value, modulus) == 1:
                pivot = pos
                break
            nonunit_seen = True
        if pivot is None:
            if nonunit_seen:
                nonunit_obstructions += 1
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, modulus)
        rows[rank] = [(value * inv) % modulus for value in rows[rank]]
        for pos in range(row_count):
            if pos == rank:
                continue
            factor = rows[pos][col] % modulus
            if factor:
                rows[pos] = [
                    (rows[pos][idx] - factor * rows[rank][idx]) % modulus
                    for idx in range(col_count)
                ]
        rank += 1
        if rank == row_count:
            break
    return {
        "rank": rank,
        "row_count": row_count,
        "column_count": col_count,
        "nonunit_pivot_obstruction_count": nonunit_obstructions,
    }


def select_rows(
    selector: str,
    train_rows: list[dict[str, Any]],
    holdout_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if selector == "p943_exact_hash_transfer_mod4":
        return [row for row in holdout_rows if selected_by_strategy(row, train_rows, P943_STRATEGY)]
    if selector == "p944_unguarded_same_hash_transfer_mod2":
        return [row for row in holdout_rows if selected_by_strategy(row, train_rows, P944_UNGUARDED_STRATEGY)]
    if selector == "p945_guarded_same_hash_transfer_mod2_even_holdout":
        return [
            row
            for row in holdout_rows
            if guarded_even_transfer(row) and selected_by_strategy(row, train_rows, P945_GUARDED_STRATEGY)
        ]
    if selector == "oracle_all_clean_rows":
        return [row for row in holdout_rows if row.get("clean")]
    raise KeyError(selector)


def row_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        window_start(str(row.get("window"))),
        int_value(row.get("transfer_index")),
        int_value(row.get("salt")),
        str(row.get("hash")),
        str(row.get("row_key")),
    )


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "b_coeff": row.get("b_coeff"),
        "c_coeff": row.get("c_coeff"),
        "clean": bool(row.get("clean")),
        "constant": row.get("constant"),
        "false_positive": bool(row.get("false_positive")),
        "hash": row.get("hash"),
        "policy": row.get("policy"),
        "preserve": bool(row.get("preserve")),
        "ratio": row.get("ratio"),
        "row_key": row.get("row_key"),
        "target": row.get("target"),
        "target_prime": row.get("target_prime"),
        "transfer_index": row.get("transfer_index"),
        "window": row.get("window"),
    }


def cumulative_rank_events(rows: list[dict[str, Any]], modulus: int) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=row_sort_key)
    matrix: list[list[int]] = []
    events: list[dict[str, Any]] = []
    current_rank = 0
    cumulative_ratio = 0.0
    for row in ordered:
        vector = row_vector(row)
        if vector is None:
            continue
        matrix.append(vector)
        if row.get("ratio") is not None:
            cumulative_ratio += float(row["ratio"])
        rank_report = modular_rank(matrix, modulus)
        new_rank = int_value(rank_report.get("rank"))
        if new_rank > current_rank:
            events.append(
                {
                    "cumulative_ratio": round(cumulative_ratio, 8),
                    "cumulative_rank": new_rank,
                    "row": compact_row(row),
                }
            )
            current_rank = new_rank
    return events


def target_profile(rows: list[dict[str, Any]], target: str) -> dict[str, Any]:
    target_rows = [row for row in rows if str(row.get("target")) == target]
    target_prime = next((row.get("target_prime") for row in target_rows if row.get("target_prime") is not None), None)
    vectors = [row_vector(row) for row in target_rows]
    matrix = [vector for vector in vectors if vector is not None]
    unique_matrix = sorted({tuple(vector) for vector in matrix})
    ratios = [float(row["ratio"]) for row in target_rows if row.get("ratio") is not None]
    rank_report = (
        modular_rank(matrix, int(target_prime))
        if target_prime is not None
        else {"rank": 0, "row_count": len(matrix), "column_count": 3, "nonunit_pivot_obstruction_count": 0}
    )
    unique_rank_report = (
        modular_rank([list(vector) for vector in unique_matrix], int(target_prime))
        if target_prime is not None
        else {"rank": 0, "row_count": len(unique_matrix), "column_count": 3, "nonunit_pivot_obstruction_count": 0}
    )
    return {
        "coefficient_rank": rank_report,
        "coefficient_tuple_count": len(unique_matrix),
        "coefficient_tuples": [list(vector) for vector in unique_matrix],
        "cumulative_rank_events": cumulative_rank_events(target_rows, int(target_prime)) if target_prime is not None else [],
        "factor_hash_count": len({str(row.get("hash")) for row in target_rows}),
        "factor_hash_counts": dict(Counter(str(row.get("hash")) for row in target_rows).most_common()),
        "max_ratio": max(ratios) if ratios else None,
        "mean_ratio": mean(ratios),
        "min_ratio": min(ratios) if ratios else None,
        "ops_window_selected": sum(1 for row in target_rows if row.get("control_class") == "ops_rule_window"),
        "ratio_sum": round(sum(ratios), 8),
        "row_count": len(target_rows),
        "target": target,
        "target_prime": target_prime,
        "transfer_indices": sorted({int(row["transfer_index"]) for row in target_rows if row.get("transfer_index") is not None}),
        "unique_coefficient_rank": unique_rank_report,
        "window_counts": dict(Counter(str(row.get("window")) for row in target_rows).most_common()),
        "windows": sorted({str(row.get("window")) for row in target_rows}, key=window_start),
    }


def relation_field_inventory(rows: list[dict[str, Any]]) -> dict[str, Any]:
    present = sorted(field for field in RELATION_EQUATION_FIELDS if any(field in row for row in rows))
    missing = sorted(field for field in RELATION_EQUATION_FIELDS if field not in present)
    return {
        "available_relation_equation_fields": present,
        "ecdlp_relation_matrix_ready": False,
        "missing_relation_equation_fields": missing,
        "reason": (
            "Current normalized QR rows expose public factor coefficients and root-preservation metadata, "
            "but no verifier linear-form RHS/scalar/group-order columns."
        ),
    }


def selector_report(
    selector: str,
    rows_by_window: dict[str, list[dict[str, Any]]],
    include_rows: bool = False,
) -> dict[str, Any]:
    windows = sorted_windows(rows_by_window)
    holdouts: list[dict[str, Any]] = []
    selected_all: list[dict[str, Any]] = []
    for index, window in enumerate(windows):
        train_windows = windows[:index]
        train_rows = [row for train_window in train_windows for row in rows_by_window[train_window]]
        holdout_rows = rows_by_window[window]
        selected = select_rows(selector, train_rows, holdout_rows)
        selected_all.extend(selected)
        holdout = {
            "holdout_class": holdout_rows[0].get("control_class") if holdout_rows else None,
            "holdout_window": window,
            "train_row_count": len(train_rows),
            "train_window_count": len(train_windows),
            "train_windows": train_windows,
            **summarize_selected(selected, holdout_rows),
        }
        if not include_rows:
            holdout.pop("selected_rows", None)
        holdouts.append(holdout)

    clean_rows = [row for row in selected_all if row.get("clean")]
    dirty_rows = [
        row
        for row in selected_all
        if row.get("false_positive") or not row.get("preserve") or not row.get("clean")
    ]
    ops_holdouts = [item for item in holdouts if item.get("holdout_class") == "ops_rule_window"]
    ratios = [float(row["ratio"]) for row in selected_all if row.get("ratio") is not None]
    clean_targets = sorted({str(row.get("target")) for row in clean_rows})
    target_profiles = {target: target_profile(clean_rows, target) for target in clean_targets}
    max_rank = max((int_value(profile["coefficient_rank"].get("rank")) for profile in target_profiles.values()), default=0)
    max_unique_rank = max((int_value(profile["unique_coefficient_rank"].get("rank")) for profile in target_profiles.values()), default=0)
    return {
        "all_selected_clean": all(bool(row.get("clean")) for row in selected_all) if selected_all else False,
        "clean_factor_hash_count": len({str(row.get("hash")) for row in clean_rows}),
        "clean_row_count": len(clean_rows),
        "clean_target_count": len(clean_targets),
        "dirty_rows": [compact_row(row) for row in dirty_rows[:20]],
        "false_positive_count": sum(int_value(item.get("false_positive_count")) for item in holdouts),
        "holdouts": holdouts,
        "max_clean_coefficient_rank": max_rank,
        "max_clean_unique_coefficient_rank": max_unique_rank,
        "max_ratio": max(ratios) if ratios else None,
        "mean_ratio": mean(ratios),
        "min_ratio": min(ratios) if ratios else None,
        "non_preserving_count": sum(int_value(item.get("non_preserving_count")) for item in holdouts),
        "ops_holdouts_with_clean_selection": sum(1 for item in ops_holdouts if int_value(item.get("selected_clean_count")) > 0),
        "ops_window_count": len(ops_holdouts),
        "ratio_sum": round(sum(ratios), 8),
        "selected_count": len(selected_all),
        "selector": selector,
        "target_520_clean_selected": sum(
            int_value(item.get("selected_clean_count")) for item in ops_holdouts if item.get("holdout_window") == "520_535"
        ),
        "target_632_clean_selected": sum(
            int_value(item.get("selected_clean_count")) for item in ops_holdouts if item.get("holdout_window") == "632_639"
        ),
        "target_profiles": target_profiles,
        "windows_with_clean_selection": sum(1 for item in holdouts if int_value(item.get("selected_clean_count")) > 0),
    }


def determine_claim(primary: dict[str, Any], field_inventory: dict[str, Any]) -> str:
    if int_value(primary.get("false_positive_count")) or int_value(primary.get("non_preserving_count")):
        return "NEGATIVE_RESULT_P947_PRIMARY_SELECTOR_DIRTY"
    if int_value(primary.get("target_632_clean_selected")) == 0:
        return "NEGATIVE_RESULT_P947_PRIMARY_SELECTOR_LOSES_632_SIGNAL"
    if int_value(primary.get("max_clean_unique_coefficient_rank")) <= 1:
        return "NEGATIVE_RESULT_P947_FACTOR_BANK_RANK_COLLAPSES"
    if not field_inventory.get("ecdlp_relation_matrix_ready"):
        return "P947_FORWARD_FACTOR_BANK_RANK_PROXY_READY_ECDLP_RHS_MISSING"
    return "P947_FORWARD_FACTOR_BANK_READY_FOR_VERIFIER_RANK_DESCENT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    rows_by_window, artifact_summary = load_rows(args.p939_source)
    all_rows = [row for rows in rows_by_window.values() for row in rows]
    selectors = [
        "p943_exact_hash_transfer_mod4",
        "p944_unguarded_same_hash_transfer_mod2",
        "p945_guarded_same_hash_transfer_mod2_even_holdout",
        "oracle_all_clean_rows",
    ]
    reports = {
        selector: selector_report(selector, rows_by_window, include_rows=False)
        for selector in selectors
    }
    primary = reports["p945_guarded_same_hash_transfer_mod2_even_holdout"]
    field_inventory = relation_field_inventory(all_rows)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p939_source": str(args.p939_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(primary, field_inventory),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores normalized archive QR artifacts; no fresh 1160+ replay is claimed.",
            "FORWARD-CHRONOLOGY: public selectors use only numerically earlier windows for each holdout.",
            "TRAIN-LABEL-AUDIT: support seeds use training preservation/below-rho labels but never heldout labels.",
            "RANK-PROXY-NOT-DESCENT: coefficient rank of public factors is not a verifier relation-matrix rank.",
            "FAIL-CLOSED-DERIVATION: without verifier RHS/scalar/group-order fields, P947 cannot claim relation-derived ECDLP.",
            "POLLARD-RHO BOUNDARY: this is a public-factor relation-bank audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p947_chronology_rank_descent_audit",
        "parameters": {
            "hash_visible_row_count": len(all_rows),
            "hash_visible_window_count": len(rows_by_window),
            "source_window_count": len(artifact_summary),
        },
        "relation_field_inventory": field_inventory,
        "schema": SCHEMA,
        "summary": {
            "artifact_summary": artifact_summary,
            "rows_by_window_count": {
                window: len(rows)
                for window, rows in sorted(rows_by_window.items(), key=lambda item: window_start(item[0]))
            },
            "selector_reports": reports,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p939-source", type=Path, default=P939_SOURCE)
    return parser.parse_args()


def compact(report: dict[str, Any]) -> str:
    return (
        f"selected={report.get('selected_count')} clean={report.get('clean_row_count')} "
        f"false={report.get('false_positive_count')} nonpres={report.get('non_preserving_count')} "
        f"632={report.get('target_632_clean_selected')} "
        f"rank={report.get('max_clean_unique_coefficient_rank')}"
    )


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    reports = payload["summary"]["selector_reports"]
    print(
        f"claim={payload['claim_status']} "
        f"p943={compact(reports['p943_exact_hash_transfer_mod4'])} "
        f"p944_dirty={compact(reports['p944_unguarded_same_hash_transfer_mod2'])} "
        f"p945={compact(reports['p945_guarded_same_hash_transfer_mod2_even_holdout'])} "
        f"oracle={compact(reports['oracle_all_clean_rows'])} "
        f"rhs_ready={payload['relation_field_inventory']['ecdlp_relation_matrix_ready']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
