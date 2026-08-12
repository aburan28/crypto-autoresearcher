#!/usr/bin/env python3
"""P1035 relation-supply expansion for the frozen leaf-8 exact-tail rule."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1029_p231_motif_neighbor_scout as p1029
import low_term_total2_p1034_p231_leaf8_exact_tail_frozen_validation as p1034


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1035_p231_leaf8_exact_tail_supply_expansion.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion.v1"
SIGNAL_WINDOW = p1034.SIGNAL_WINDOW

RowPredicate = Callable[[dict[str, Any]], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def leaf_tuple(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in (row.get("features") or {}).get("unique_leaf_indices") or [])


def contains_leaf8(row: dict[str, Any]) -> bool:
    return 8 in set(leaf_tuple(row))


def exact_leaf8(row: dict[str, Any]) -> bool:
    return leaf_tuple(row) == (8,)


def p1029_leaf8_scout(row: dict[str, Any]) -> bool:
    return exact_leaf8(row) and p1029.scout_predicate(row)


def pool_specs() -> list[dict[str, Any]]:
    return [
        {
            "description": "Original P1029 exact leaf-8 scout route.",
            "name": "p1029_leaf8_scout",
            "predicate": p1029_leaf8_scout,
        },
        {
            "description": "Any exact leaf-8 candidate row, all selectors and source ranks.",
            "name": "leaf8_all_selectors",
            "predicate": exact_leaf8,
        },
        {
            "description": "Any row containing leaf 8 in the unique leaf tuple.",
            "name": "contains_leaf8",
            "predicate": contains_leaf8,
        },
        {
            "description": "All target rows in the selected windows.",
            "name": "all_target_rows",
            "predicate": lambda _row: True,
        },
    ]


def later_windows() -> list[str]:
    return [window for window in p1025.FRESH_WINDOWS if window > SIGNAL_WINDOW]


def load_rows(windows: list[str], targets: str, min_source_rank: int) -> tuple[dict[str, list[dict[str, Any]]], dict[str, bool]]:
    return p1029.p1010.build_window_rows(windows, targets, min_source_rank)


def selected_rows_for_pool(
    by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
    predicate: RowPredicate,
    split: str,
) -> list[dict[str, Any]]:
    rows = []
    for window in windows:
        for row in by_window.get(window) or []:
            if not predicate(row):
                continue
            item = dict(row)
            item["_p1023_window"] = window
            item["_p1023_split"] = split
            rows.append(item)
    return rows


def reconstruct_pool(rows: list[dict[str, Any]], compressed: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_rows = p1029.dedupe_by_row_signature(rows) if compressed else rows
    reconstructed, forms = p1025.reconstruct_partition(source_rows)
    out_forms = p1023.unique_forms(forms) if compressed else forms
    return out_forms, {
        "compressed": compressed,
        "form_count": len(forms),
        "input_row_count": len(source_rows),
        "raw_row_count": len(rows),
        "reconstructed_case_count": len(reconstructed),
        "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
        "unique_form_count": len(p1023.unique_forms(forms)),
    }


def evaluate_rows(rows: list[dict[str, Any]], windows: list[str], label: str, compressed: bool) -> dict[str, Any]:
    forms, meta = reconstruct_pool(rows, compressed)
    return p1034.evaluate_partition(forms, meta, windows, label)


def evaluate_pool(
    pool: dict[str, Any],
    scout_by_window: dict[str, list[dict[str, Any]]],
    later_by_window: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    predicate = pool["predicate"]
    scout_rows = selected_rows_for_pool(scout_by_window, [SIGNAL_WINDOW], predicate, "fresh_validation")
    later_rows = selected_rows_for_pool(later_by_window, later_windows(), predicate, "fresh_validation")
    evaluations = []
    for compressed in (False, True):
        evaluations.append(evaluate_rows(scout_rows, [SIGNAL_WINDOW], f"{pool['name']}_scout_raw" if not compressed else f"{pool['name']}_scout_compressed", compressed))
        evaluations.append(evaluate_rows(later_rows, later_windows(), f"{pool['name']}_later_raw" if not compressed else f"{pool['name']}_later_compressed", compressed))
    later_evals = [item for item in evaluations if "_later_" in item["label"]]
    scout_evals = [item for item in evaluations if "_scout_" in item["label"]]
    return {
        "description": pool["description"],
        "evaluations": evaluations,
        "later_summary": aggregate_summaries(later_evals),
        "name": pool["name"],
        "row_counts": {
            "later_rows": len(later_rows),
            "scout_rows": len(scout_rows),
        },
        "scout_summary": aggregate_summaries(scout_evals),
    }


def aggregate_summaries(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "eligible_form_count": sum(int_value(item["summary"].get("eligible_form_count")) for item in evaluations),
        "false_count": sum(int_value(item["summary"].get("false_count")) for item in evaluations),
        "group_count": sum(int_value(item["summary"].get("group_count")) for item in evaluations),
        "no_pair_group_count": sum(int_value(item["summary"].get("no_pair_group_count")) for item in evaluations),
        "prediction_count": sum(int_value(item["summary"].get("prediction_count")) for item in evaluations),
        "true_count": sum(int_value(item["summary"].get("true_count")) for item in evaluations),
        "validation_success": any(bool(item["summary"].get("validation_success")) for item in evaluations),
    }


def determine_claim(pool_results: list[dict[str, Any]]) -> str:
    if any(result["later_summary"]["false_count"] for result in pool_results):
        return "NEGATIVE_RESULT_P1035_FROZEN_RULE_FALSE_PREDICTION"
    if any(result["later_summary"]["prediction_count"] for result in pool_results):
        return "P1035_RELAXED_SUPPLY_VALIDATION_SIGNAL"
    if any(result["later_summary"]["eligible_form_count"] for result in pool_results):
        return "NEGATIVE_RESULT_P1035_RELAXED_SUPPLY_NO_ELIGIBLE_PAIR"
    return "NEGATIVE_RESULT_P1035_RELAXED_SUPPLY_NO_ELIGIBLE_FORMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scout_by_window, scout_exists = load_rows([SIGNAL_WINDOW], args.targets, args.min_source_rank)
    later_by_window, later_exists = load_rows(later_windows(), args.targets, args.min_source_rank)
    pool_results = [evaluate_pool(pool, scout_by_window, later_by_window) for pool in pool_specs()]
    claim = determine_claim(pool_results)
    all_windows = [SIGNAL_WINDOW, *later_windows()]
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
            "p1034_dependency_sha256": p1005.sha256_file(Path(p1034.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1035_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-RULE: target-prediction exact-tail/motif rule is unchanged from P1034.",
            "SUPPLY-EXPANSION: row selection is relaxed, but predictions require same-public same-window eligible pairs.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "later_windows": later_windows(),
            "min_source_rank": args.min_source_rank,
            "pool_names": [pool["name"] for pool in pool_specs()],
            "signal_window": SIGNAL_WINDOW,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "pool_results": pool_results,
        "schema": SCHEMA,
        "source": {
            "later_exists": later_exists,
            "scout_exists": scout_exists,
        },
        "summary": {
            "claim_status": claim,
            "later_by_pool": [
                {
                    "eligible_form_count": result["later_summary"]["eligible_form_count"],
                    "false_count": result["later_summary"]["false_count"],
                    "name": result["name"],
                    "prediction_count": result["later_summary"]["prediction_count"],
                    "row_count": result["row_counts"]["later_rows"],
                    "true_count": result["later_summary"]["true_count"],
                }
                for result in pool_results
            ],
            "scout_by_pool": [
                {
                    "false_count": result["scout_summary"]["false_count"],
                    "name": result["name"],
                    "prediction_count": result["scout_summary"]["prediction_count"],
                    "row_count": result["row_counts"]["scout_rows"],
                    "true_count": result["scout_summary"]["true_count"],
                }
                for result in pool_results
            ],
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    bits = []
    for item in payload["summary"]["later_by_pool"]:
        bits.append(
            "{name}:rows={rows} eligible={eligible} pred={pred} false={false}".format(
                name=item["name"],
                rows=item["row_count"],
                eligible=item["eligible_form_count"],
                pred=item["prediction_count"],
                false=item["false_count"],
            )
        )
    print(
        "claim={claim} out={out} {bits}".format(
            claim=payload["claim_status"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
