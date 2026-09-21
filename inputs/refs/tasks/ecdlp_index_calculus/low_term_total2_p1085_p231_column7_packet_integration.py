#!/usr/bin/env python3
"""P1085 integrate the P1083 column-7 row and score the next direction."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1079_p231_remaining_column_residual_row_pivot as p1079
import low_term_total2_p1080_p231_full_corpus_residual_supply_scout as p1080
import low_term_total2_p1081_p231_carrier_quotient_representation_scout as p1081
import low_term_total2_p1082_p231_carrier_quotient_composability as p1082
import low_term_total2_p1083_p231_split_partner_or_column7_generator as p1083
import low_term_total2_p1084_p231_baseline_rhs_repair_column7 as p1084


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1085_p231_column7_packet_integration.md"
DEFAULT_P1083 = STATE_DIR / "low_term_total2_p1083_p231_split_partner_or_column7_generator_probe.json"
DEFAULT_P1084 = STATE_DIR / "low_term_total2_p1084_p231_baseline_rhs_repair_column7_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1085_p231_column7_packet_integration_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1085_p231_column7_packet_integration.v1"


def matrix_report(rows: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    coeffs = [p1079.pad([p1055.int_value(value) % order for value in row.get("coeffs") or []], factor_count) for row in rows]
    augmented = [[*row, p1055.int_value(src.get("rhs")) % order] for row, src in zip(coeffs, rows)]
    basis, pivots = gap.rref_rows(coeffs, order)
    aug_rank = p1082.rank(augmented, order)
    return {
        "augmented_excess": aug_rank - len(pivots),
        "augmented_matrix_rank": aug_rank,
        "coefficient_matrix_rank": len(pivots),
        "consistent": aug_rank == len(pivots),
        "free_columns": [index for index in range(factor_count) if index not in set(pivots)],
        "pivots": pivots,
        "row_count": len(rows),
    }


def route_by_artifact(args: argparse.Namespace) -> dict[str, str]:
    out: dict[str, str] = {}
    for spec in p1083.route_specs_from_args(args.route_glob):
        for path in sorted(args.state_dir.glob(spec["glob"])):
            out.setdefault(str(path), spec["id"])
    return out


def load_strict_rows(
    args: argparse.Namespace,
    factor_count: int,
) -> tuple[list[dict[str, Any]], dict[int, int], int]:
    strict_model = p1080.build_strict_model(args, factor_count)
    all_strict_certs = strict_model["strict_base_certs"] + strict_model["baseline_certs"]
    order_counts = Counter(p1055.int_value(cert.get("order")) for cert in all_strict_certs)
    strict_certs = p1083.same_order_certs(all_strict_certs, args.order)
    return p1081.row_model_rows(strict_certs, "coefficient", args.order, factor_count), dict(order_counts), len(strict_certs)


def load_candidate_rows(args: argparse.Namespace, factor_count: int) -> tuple[list[dict[str, Any]], dict[str, Any], list[Path]]:
    certs, route_info, paths = p1083.load_routed_certs(args)
    return p1081.row_model_rows(certs, "coefficient", args.order, factor_count), route_info, paths


def row_identity(row: dict[str, Any]) -> tuple[Any, ...]:
    summary = p1081.row_summary(row)
    return (
        summary.get("artifact"),
        summary.get("artifact_offset"),
        tuple(summary.get("pair") or []),
        tuple(summary.get("factor_support") or []),
        tuple(summary.get("row_keys") or []),
    )


def evaluated_rows(
    packet_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    routes: dict[str, str],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    model = p1082.build_model(packet_rows, candidate_rows, "identity", args.order)
    model["strict_rows"] = packet_rows
    packet_keys = {p1081.row_key(row, args.order) for row in packet_rows}
    seen: set[tuple[tuple[int, ...], int]] = set()
    out: list[dict[str, Any]] = []
    for index, row in enumerate(candidate_rows):
        key = p1081.row_key(row, args.order)
        if key in packet_keys or key in seen:
            continue
        seen.add(key)
        matrix = p1083.matrix_report_for_row(row, model["candidate_vectors"][index], model, args.order)
        route = p1083.route_for_row(row, routes)
        item = p1083.candidate_summary("packet_candidate", row, route, matrix, matrix, args.order)
        item["touches_remaining_priority_columns"] = sorted(
            set(item["support"]) & set(p1080.parse_columns(args.remaining_columns))
        )
        out.append(item)
    out.sort(
        key=lambda item: (
            not item["strict_success"],
            not bool(item["touches_remaining_priority_columns"]),
            -(item["matrix"].get("marginal_rank_gain") or 0),
            p1083.finite_charge(item.get("parent_certificate_charge_over_rho")),
            item["row"].get("artifact") or "",
            item["row"].get("artifact_offset") or 0,
        )
    )
    return out


def pick_column7_row(
    strict_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    routes: dict[str, str],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    model = p1082.build_model(strict_rows, candidate_rows, "identity", args.order)
    model["strict_rows"] = strict_rows
    seen: set[tuple[tuple[int, ...], int]] = set()
    choices: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for index, row in enumerate(candidate_rows):
        if 7 not in set(p1081.motif(row)):
            continue
        key = p1081.row_key(row, args.order)
        if key in seen:
            continue
        seen.add(key)
        matrix = p1083.matrix_report_for_row(row, model["candidate_vectors"][index], model, args.order)
        route = p1083.route_for_row(row, routes)
        item = p1083.candidate_summary("actual_column7", row, route, matrix, matrix, args.order)
        choices.append((item, row))
    choices.sort(
        key=lambda pair: (
            not pair[0]["strict_success"],
            p1083.finite_charge(pair[0].get("parent_certificate_charge_over_rho")),
            pair[0]["row"].get("artifact") or "",
            pair[0]["row"].get("artifact_offset") or 0,
        )
    )
    if not choices:
        return None, None
    return choices[0]


def compact_counter(counter: Counter[Any], limit: int = 16) -> list[dict[str, Any]]:
    return p1081.compact_counter(counter, limit=limit)


def support_counter(rows: list[dict[str, Any]]) -> Counter[tuple[int, ...]]:
    return Counter(p1081.motif(row) for row in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=p1080.DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=p1080.DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=p1080.DEFAULT_P1069)
    parser.add_argument("--p1073", type=Path, default=p1080.DEFAULT_P1073)
    parser.add_argument("--p1074", type=Path, default=p1080.DEFAULT_P1074)
    parser.add_argument("--p1079", type=Path, default=p1080.DEFAULT_P1079)
    parser.add_argument("--p1083", type=Path, default=DEFAULT_P1083)
    parser.add_argument("--p1084", type=Path, default=DEFAULT_P1084)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--route-glob", action="append", help="Override route as name=glob; may be repeated.")
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--remaining-columns", default="6,7")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    factor_count = 17
    strict_rows, strict_order_counts, strict_cert_count = load_strict_rows(args, factor_count)
    candidate_rows, route_info, paths = load_candidate_rows(args, factor_count)
    routes = route_by_artifact(args)
    p1083_payload = p1079.load_json(args.p1083) if args.p1083.exists() else {}
    p1084_payload = p1079.load_json(args.p1084) if args.p1084.exists() else {}

    before = matrix_report(strict_rows, args.order, factor_count)
    column7_item, column7_row = pick_column7_row(strict_rows, candidate_rows, routes, args)
    packet_rows = [*strict_rows]
    if column7_row is not None:
        packet_rows.append(column7_row)
    after = matrix_report(packet_rows, args.order, factor_count)
    evaluated_next = evaluated_rows(packet_rows, candidate_rows, routes, args)
    strict_next = [item for item in evaluated_next if item["strict_success"]]
    strict_next_remaining = [
        item for item in strict_next if item["touches_remaining_priority_columns"]
    ]
    next_item = (strict_next_remaining or strict_next or evaluated_next or [None])[0]
    remaining_priority_before = sorted(set(before["free_columns"]) & set(p1080.parse_columns(args.remaining_columns)))
    remaining_priority_after = sorted(set(after["free_columns"]) & set(p1080.parse_columns(args.remaining_columns)))

    column7_success = bool(column7_item and column7_item["strict_success"])
    next_success = bool(isinstance(next_item, dict) and next_item.get("strict_success"))
    if column7_success and next_success:
        claim_status = "POSITIVE_SIGNAL_P1085_COLUMN7_PACKET_PLUS_NEXT_DIRECTION"
    elif column7_success:
        claim_status = "OBSERVATION_P1085_COLUMN7_INTEGRATED_NEXT_DIRECTION_OPEN"
    else:
        claim_status = "NEGATIVE_RESULT_P1085_COLUMN7_PACKET_INTEGRATION_FAILED"

    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "p1083": p1069.sha256_file(args.p1083) if args.p1083.exists() else None,
            "p1084": p1069.sha256_file(args.p1084) if args.p1084.exists() else None,
            "route_artifact_count": len(paths),
            "route_artifact_digest": p1069.digest_paths(paths),
            "script": p1069.sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1083": str(args.p1083),
            "p1084": str(args.p1084),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "PACKET-INTEGRATION",
            "ORDER-FILTERED",
            "POLLARD-RHO-BOUNDARY",
        ],
        "controls": {
            "p1083_summary": p1083_payload.get("summary"),
            "p1084_summary": p1084_payload.get("summary"),
            "strict_certificate_order_counts_before_filter": compact_counter(Counter(strict_order_counts)),
            "strict_certificate_count_after_order_filter": strict_cert_count,
            "strict_row_count_after_order_filter": len(strict_rows),
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "existing_artifacts_only": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "secret_scalar_not_used": True,
            "target_descent_packet_not_individual_log_completion": True,
        },
        "packet": {
            "after_column7": after,
            "before_column7": before,
            "column7_item": column7_item,
            "column7_row_identity": row_identity(column7_row) if column7_row else None,
            "remaining_priority_columns_after": remaining_priority_after,
            "remaining_priority_columns_before": remaining_priority_before,
        },
        "parameters": {
            "factor_count": factor_count,
            "remaining_columns": p1080.parse_columns(args.remaining_columns),
            "route_globs": p1083.route_specs_from_args(args.route_glob),
            "target": args.target,
        },
        "route_info": route_info,
        "schema": SCHEMA,
        "strict_success": column7_success,
        "next_direction": {
            "best_next_candidate": next_item,
            "candidate_count": len(evaluated_next),
            "strict_next_count": len(strict_next),
            "strict_next_remaining_priority_count": len(strict_next_remaining),
            "top_candidates": evaluated_next[:24],
            "top_support_counts": compact_counter(support_counter(candidate_rows)),
        },
        "summary": {
            "claim_status": claim_status,
            "column7_row_added": bool(column7_row),
            "column7_strict_success": column7_success,
            "free_columns_after": after["free_columns"],
            "free_columns_before": before["free_columns"],
            "generic_rho_steps": 137,
            "next_candidate_route": next_item.get("route") if isinstance(next_item, dict) else None,
            "next_candidate_strict_success": next_success,
            "order_filtered_strict_rank": before["coefficient_matrix_rank"],
            "packet_augmented_rank_after": after["augmented_matrix_rank"],
            "packet_rank_after": after["coefficient_matrix_rank"],
            "parent_certificate_charge_over_rho": (
                column7_item.get("parent_certificate_charge_over_rho") if column7_item else None
            ),
            "remaining_priority_columns_after": remaining_priority_after,
            "remaining_priority_columns_before": remaining_priority_before,
            "strict_certificate_order_counts_before_filter": compact_counter(Counter(strict_order_counts)),
            "strict_certificate_count_after_order_filter": strict_cert_count,
            "strict_row_count_after_order_filter": len(strict_rows),
            "target_descent_consistent_after": after["consistent"],
            "verifier_status": "verified_artifact_rows_only",
        },
        "timestamp_utc": p1071.now_iso(),
    }
    p1079.write_json(args.out, payload)
    print(
        "claim={claim} column7={column7} rank={before_rank}->{after_rank} "
        "free={before_free}->{after_free} next_success={next_success} out={out}".format(
            claim=claim_status,
            column7=column7_success,
            before_rank=before["coefficient_matrix_rank"],
            after_rank=after["coefficient_matrix_rank"],
            before_free=before["free_columns"],
            after_free=after["free_columns"],
            next_success=next_success,
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
