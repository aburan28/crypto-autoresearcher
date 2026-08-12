#!/usr/bin/env python3
"""P1039 strict validation of the P1038 P1029 leaf-8 route."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1036_p231_adjacent_family_supply_scout as p1036
import low_term_total2_p1038_p231_guarded_structural_family_supply_search as p1038


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1039_p231_strict_leaf8_route_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1039_p231_strict_leaf8_route_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1039_p231_strict_leaf8_route_validation.v1"
SIGNAL_WINDOW = p1038.SIGNAL_WINDOW
DEFAULT_START = "12632_12639"
DEFAULT_MAX_WINDOWS = 16
STRICT_TERMS = (8, 8, 11, 11)
STRICT_TAIL = (9, 12)
PRIMARY_POOL = "p1029_leaf8_scout"


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def strict_family(form: dict[str, Any]) -> bool:
    return (
        p1036.is_repeated_two_tail(form)
        and p1036.terms_tuple(form) == STRICT_TERMS
        and p1036.tail_support_tuple(form) == STRICT_TAIL
        and p1038.passes_guard(form)
    )


def strict_forms_for_windows(forms: list[dict[str, Any]], windows: list[str]) -> list[dict[str, Any]]:
    window_set = set(windows)
    return [form for form in forms if p1036.form_window(form) in window_set and strict_family(form)]


def evaluate_rows(rows: list[dict[str, Any]], windows: list[str], label: str, compressed: bool) -> dict[str, Any]:
    forms, meta = p1036.reconstruct_pool(rows, compressed)
    factors = int_value(meta.get("factor_count"))
    strict_forms = strict_forms_for_windows(forms, windows)
    object_results = [
        p1038.evaluate_object(strict_forms, factors, windows, spec)
        for spec in p1036.object_specs()
    ]
    summary = p1038.aggregate_object_results(object_results)
    summary["strict_form_count"] = len(strict_forms)
    summary["windows"] = windows
    return {
        "label": label,
        "meta": meta,
        "object_results": object_results,
        "summary": summary,
    }


def selected_rows_for_pool(
    by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
    predicate: p1035.RowPredicate,
) -> list[dict[str, Any]]:
    return p1035.selected_rows_for_pool(by_window, windows, predicate, "fresh_validation")


def aggregate_summaries(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    summary = p1038.aggregate_summaries(evaluations)
    summary["strict_form_count"] = sum(int_value(item["summary"].get("strict_form_count")) for item in evaluations)
    return summary


def evaluate_pool(
    pool: dict[str, Any],
    scout_by_window: dict[str, list[dict[str, Any]]],
    forward_by_window: dict[str, list[dict[str, Any]]],
    forward_windows: list[str],
) -> dict[str, Any]:
    predicate = pool["predicate"]
    scout_rows = selected_rows_for_pool(scout_by_window, [SIGNAL_WINDOW], predicate)
    forward_rows = selected_rows_for_pool(forward_by_window, forward_windows, predicate)
    evaluations = []
    scout_evals = []
    forward_evals = []
    for compressed in (False, True):
        suffix = "compressed" if compressed else "raw"
        scout_eval = evaluate_rows(scout_rows, [SIGNAL_WINDOW], f"{pool['name']}_scout_{suffix}", compressed)
        forward_eval = evaluate_rows(forward_rows, forward_windows, f"{pool['name']}_forward_{suffix}", compressed)
        evaluations.extend([scout_eval, forward_eval])
        scout_evals.append(scout_eval)
        forward_evals.append(forward_eval)
    forward_compressed = [item for item in forward_evals if item["label"].endswith("_compressed")]
    forward_raw = [item for item in forward_evals if item["label"].endswith("_raw")]
    return {
        "description": pool["description"],
        "evaluations": evaluations,
        "forward_compressed_summary": aggregate_summaries(forward_compressed),
        "forward_raw_summary": aggregate_summaries(forward_raw),
        "forward_summary": aggregate_summaries(forward_evals),
        "is_primary": pool["name"] == PRIMARY_POOL,
        "name": pool["name"],
        "row_counts": {
            "forward_rows": len(forward_rows),
            "scout_rows": len(scout_rows),
        },
        "scout_summary": aggregate_summaries(scout_evals),
    }


def determine_claim(pool_results: list[dict[str, Any]]) -> str:
    primary = next(result for result in pool_results if result["name"] == PRIMARY_POOL)
    compressed = primary["forward_compressed_summary"]
    false_count = int_value(compressed.get("false_count"))
    prediction_count = int_value(compressed.get("prediction_count"))
    q_diverse_count = int_value(compressed.get("q_diverse_group_count"))
    strict_form_count = int_value(compressed.get("strict_form_count"))
    if false_count:
        return "NEGATIVE_RESULT_P1039_STRICT_ROUTE_FALSE_PREDICTION"
    if prediction_count:
        return "P1039_STRICT_ROUTE_FORWARD_SUPPLY_SIGNAL"
    if q_diverse_count:
        return "NEGATIVE_RESULT_P1039_STRICT_ROUTE_Q_DIVERSE_NO_FACTOR_MATCH"
    if strict_form_count:
        return "NEGATIVE_RESULT_P1039_STRICT_ROUTE_NO_Q_DIVERSE_GROUPS"
    return "NEGATIVE_RESULT_P1039_STRICT_ROUTE_NO_ELIGIBLE_SUPPLY"


def pool_specs() -> list[dict[str, Any]]:
    specs = p1035.pool_specs()
    return [spec for spec in specs if spec["name"] == PRIMARY_POOL] + [
        spec for spec in specs if spec["name"] != PRIMARY_POOL
    ]


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    forward_windows = p1038.discover_forward_windows(args.start_window, args.max_windows)
    scout_by_window, scout_exists = p1035.load_rows([SIGNAL_WINDOW], args.targets, args.min_source_rank)
    forward_by_window, forward_exists = p1035.load_rows(forward_windows, args.targets, args.min_source_rank)
    results = [evaluate_pool(pool, scout_by_window, forward_by_window, forward_windows) for pool in pool_specs()]
    claim = determine_claim(results)
    primary = next(result for result in results if result["name"] == PRIMARY_POOL)
    diagnostics = [result for result in results if result["name"] != PRIMARY_POOL]
    diagnostic_compressed_false = sum(
        int_value(result["forward_compressed_summary"].get("false_count")) for result in diagnostics
    )
    diagnostic_raw_false = sum(int_value(result["forward_raw_summary"].get("false_count")) for result in diagnostics)
    all_windows = [SIGNAL_WINDOW, *forward_windows]
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
            "p1038_source_sha256": p1005.sha256_file(
                Path("tasks/ecdlp_index_calculus/low_term_total2_p1038_p231_guarded_structural_family_supply_search.py")
            ),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1039_") else "NEGATIVE RESULT",
        "diagnostic_summary": {
            "compressed_false_count": diagnostic_compressed_false,
            "raw_false_count": diagnostic_raw_false,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "STRICT-ROUTE: the primary claim only covers p1029_leaf8_scout.",
            "FROZEN-FAMILY: terms [8,8,11,11] and tail [9,12] are fixed from P1033/P1038 before this scan.",
            "COMPRESSED-PRIMARY: row-signature-compressed primary forward forms drive the claim.",
            "DIAGNOSTIC-POOLS: widened pools are red-team diagnostics and do not promote the strict-route claim.",
            "INDEX-CALCULUS PRECURSOR: this is relation-generation supply, not sparse linear algebra or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "forward_windows": forward_windows,
            "guard": "term_gap_ge_3 OR tail_width_ge_3",
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "primary_pool": PRIMARY_POOL,
            "strict_tail": list(STRICT_TAIL),
            "strict_terms": list(STRICT_TERMS),
            "signal_window": SIGNAL_WINDOW,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "pool_results": results,
        "primary_summary": primary["forward_compressed_summary"],
        "schema": SCHEMA,
        "source": {
            "forward_exists": forward_exists,
            "scout_exists": scout_exists,
        },
        "summary": {
            "claim_status": claim,
            "diagnostic_compressed_false_count": diagnostic_compressed_false,
            "diagnostic_raw_false_count": diagnostic_raw_false,
            "forward_by_pool": [
                {
                    "compressed_eligible_form_count": result["forward_compressed_summary"]["eligible_form_count"],
                    "compressed_false_count": result["forward_compressed_summary"]["false_count"],
                    "compressed_factor_matchless_q_diverse_group_count": result["forward_compressed_summary"][
                        "factor_matchless_q_diverse_group_count"
                    ],
                    "compressed_prediction_count": result["forward_compressed_summary"]["prediction_count"],
                    "compressed_q_diverse_group_count": result["forward_compressed_summary"]["q_diverse_group_count"],
                    "compressed_strict_form_count": result["forward_compressed_summary"]["strict_form_count"],
                    "compressed_true_count": result["forward_compressed_summary"]["true_count"],
                    "is_primary": result["is_primary"],
                    "name": result["name"],
                    "raw_false_count": result["forward_raw_summary"]["false_count"],
                    "raw_prediction_count": result["forward_raw_summary"]["prediction_count"],
                    "raw_strict_form_count": result["forward_raw_summary"]["strict_form_count"],
                    "row_count": result["row_counts"]["forward_rows"],
                }
                for result in results
            ],
            "primary_forward_compressed": primary["forward_compressed_summary"],
            "scout_by_pool": [
                {
                    "false_count": result["scout_summary"]["false_count"],
                    "is_primary": result["is_primary"],
                    "name": result["name"],
                    "prediction_count": result["scout_summary"]["prediction_count"],
                    "q_diverse_group_count": result["scout_summary"]["q_diverse_group_count"],
                    "row_count": result["row_counts"]["scout_rows"],
                    "strict_form_count": result["scout_summary"]["strict_form_count"],
                    "true_count": result["scout_summary"]["true_count"],
                }
                for result in results
            ],
        },
        "timestamp": p1038.now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum forward windows to scan")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to scan")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    p1038.write_json(Path(args.out), payload)
    bits = []
    for item in payload["summary"]["forward_by_pool"]:
        bits.append(
            "{name}:rows={rows} strict={strict} c_qdiv={qdiv} c_pred={pred} c_false={false} raw_pred={raw_pred} raw_false={raw_false}".format(
                name=item["name"],
                rows=item["row_count"],
                strict=item["compressed_strict_form_count"],
                qdiv=item["compressed_q_diverse_group_count"],
                pred=item["compressed_prediction_count"],
                false=item["compressed_false_count"],
                raw_pred=item["raw_prediction_count"],
                raw_false=item["raw_false_count"],
            )
        )
    print(
        "claim={claim} windows={windows} out={out} {bits}".format(
            claim=payload["claim_status"],
            windows=",".join(payload["parameters"]["forward_windows"]),
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
