#!/usr/bin/env python3
"""P1086 refresh public routes for a verified column-6 packet row."""

from __future__ import annotations

import argparse
import json
import shlex
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
import low_term_total2_p1085_p231_column7_packet_integration as p1085
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1086_p231_column6_generator_refresh.md"
DEFAULT_P1085 = STATE_DIR / "low_term_total2_p1085_p231_column7_packet_integration_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1086_p231_column6_generator_refresh_probe.json"
DEFAULT_RESEARCH_JSON = STATE_DIR / "p1086_column6_generator_refresh_probe.json"
DEFAULT_RESEARCH_MD = STATE_DIR / "p1086_column6_generator_refresh.md"
SCHEMA = "ecdlp.low_term_total2_p1086_p231_column6_generator_refresh.v1"

REFRESH_ROUTE_SPECS = [
    {
        "description": "Priority-conditioned direct exports for the col6/col15 route family.",
        "glob": "low_term_total2_priority_conditioned_case_selector_*col6_col15_probe_direct_*_probe.json",
        "id": "priority_conditioned_col6_col15_direct",
    },
]

KNOWN_DEPENDENT_SUPPORTS = {(3, 5, 6), (2, 4, 5, 6)}


def int_value(value: Any, default: int = 0) -> int:
    return p1055.int_value(value, default)


def finite_charge(value: float | None) -> float:
    return p1083.finite_charge(value)


def route_specs(route_globs: list[str] | None) -> list[dict[str, str]]:
    if route_globs:
        return p1083.route_specs_from_args(route_globs)
    return [*p1083.ROUTE_SPECS, *REFRESH_ROUTE_SPECS]


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    item = cert.get("selected")
    return item if isinstance(item, dict) else {}


def compact_counter(counter: Counter[Any], limit: int = 20) -> list[dict[str, Any]]:
    return p1081.compact_counter(counter, limit=limit)


def load_routed_certs(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any], list[Path]]:
    certs: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    paths: list[Path] = []
    info: dict[str, dict[str, Any]] = {
        spec["id"]: {
            "certificate_count": 0,
            "description": spec["description"],
            "glob": spec["glob"],
            "order_counts_before_filter": {},
            "path_count": 0,
            "target_filtered_count": 0,
        }
        for spec in route_specs(args.route_glob)
    }
    for spec in route_specs(args.route_glob):
        route_id = spec["id"]
        order_counts: Counter[int] = Counter()
        for path in sorted(args.state_dir.glob(spec["glob"])):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            paths.append(path)
            info[route_id]["path_count"] += 1
            for cert in factor_bank.load_certificates([path]):
                order = int_value(cert.get("order"))
                order_counts[order] += 1
                cert_selected = selected(cert)
                if order != args.order:
                    continue
                if str(cert_selected.get("target")) != args.target:
                    continue
                item = dict(cert)
                item["_p1086_route"] = route_id
                certs.append(item)
                info[route_id]["certificate_count"] += 1
        info[route_id]["order_counts_before_filter"] = dict(order_counts)
        info[route_id]["target_filtered_count"] = info[route_id]["certificate_count"]
    return certs, info, sorted(paths)


def route_by_artifact(args: argparse.Namespace) -> dict[str, str]:
    out: dict[str, str] = {}
    for spec in route_specs(args.route_glob):
        for path in sorted(args.state_dir.glob(spec["glob"])):
            out.setdefault(str(path), spec["id"])
    return out


def row_key(row: dict[str, Any], order: int) -> tuple[tuple[int, ...], int]:
    return p1081.row_key(row, order)


def row_identity(row: dict[str, Any] | None) -> tuple[Any, ...] | None:
    return p1085.row_identity(row) if row is not None else None


def support(row: dict[str, Any]) -> tuple[int, ...]:
    return p1081.motif(row)


def matrix_report(rows: list[dict[str, Any]], order: int, factor_count: int) -> dict[str, Any]:
    return p1085.matrix_report(rows, order, factor_count)


def reproduce_p1085_packet(
    args: argparse.Namespace,
    factor_count: int,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any] | None, dict[str, Any] | None]:
    strict_rows, strict_order_counts, strict_cert_count = p1085.load_strict_rows(args, factor_count)
    p1083_certs, _route_info, _paths = p1083.load_routed_certs(args)
    p1083_rows = p1081.row_model_rows(p1083_certs, "coefficient", args.order, factor_count)
    p1083_routes = p1085.route_by_artifact(args)
    column7_item, column7_row = p1085.pick_column7_row(strict_rows, p1083_rows, p1083_routes, args)
    packet_rows = [*strict_rows]
    if column7_row is not None:
        packet_rows.append(column7_row)
    before = matrix_report(strict_rows, args.order, factor_count)
    after = matrix_report(packet_rows, args.order, factor_count)
    packet = {
        "column7_item": column7_item,
        "column7_row_added": column7_row is not None,
        "column7_row_identity": row_identity(column7_row),
        "column7_strict_success": bool(column7_item and column7_item.get("strict_success")),
        "free_columns_after": after["free_columns"],
        "free_columns_before": before["free_columns"],
        "order_filtered_strict_rank": before["coefficient_matrix_rank"],
        "packet_augmented_rank_after": after["augmented_matrix_rank"],
        "packet_rank_after": after["coefficient_matrix_rank"],
        "p1085_reproduced": bool(
            column7_item
            and column7_item.get("strict_success")
            and before["coefficient_matrix_rank"] == 14
            and after["coefficient_matrix_rank"] == 15
            and after["augmented_matrix_rank"] == 15
            and after["free_columns"] == [6, 16]
        ),
        "remaining_priority_columns_after": sorted(set(after["free_columns"]) & {6, 7}),
        "remaining_priority_columns_before": sorted(set(before["free_columns"]) & {6, 7}),
        "strict_certificate_count_after_order_filter": strict_cert_count,
        "strict_certificate_order_counts_before_filter": compact_counter(Counter(strict_order_counts)),
        "strict_row_count_after_order_filter": len(strict_rows),
        "target_descent_consistent_after": after["consistent"],
    }
    return packet_rows, packet, column7_item, column7_row


def candidate_sort_key(item: dict[str, Any]) -> tuple[Any, ...]:
    matrix = item["matrix"]
    return (
        not item["strict_success"],
        item.get("known_dependent_support_control", False),
        -(matrix.get("marginal_rank_gain") or 0),
        not matrix.get("consistent"),
        not item.get("below_rho_parent_certificate"),
        finite_charge(item.get("parent_certificate_charge_over_rho")),
        item["row"].get("artifact") or "",
        item["row"].get("artifact_offset") or 0,
    )


def evaluate_column6_rows(
    packet_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    routes: dict[str, str],
    args: argparse.Namespace,
) -> dict[str, Any]:
    model = p1082.build_model(packet_rows, candidate_rows, "identity", args.order)
    model["strict_rows"] = packet_rows
    packet_keys = {row_key(row, args.order) for row in packet_rows}
    seen: set[tuple[tuple[int, ...], int]] = set()
    items: list[dict[str, Any]] = []
    route_counts: Counter[str] = Counter()
    support_counts: Counter[tuple[int, ...]] = Counter()
    known_dependent_count = 0
    for index, row in enumerate(candidate_rows):
        row_support = support(row)
        if 6 not in set(row_support):
            continue
        key = row_key(row, args.order)
        if key in packet_keys or key in seen:
            continue
        seen.add(key)
        route = p1083.route_for_row(row, routes)
        route_counts[route] += 1
        support_counts[row_support] += 1
        matrix = p1083.matrix_report_for_row(row, model["candidate_vectors"][index], model, args.order)
        item = p1083.candidate_summary("p1086_column6_candidate", row, route, matrix, matrix, args.order)
        item["known_dependent_support_control"] = bool(
            row_support in KNOWN_DEPENDENT_SUPPORTS and matrix.get("marginal_rank_gain") == 0
        )
        if item["known_dependent_support_control"]:
            known_dependent_count += 1
        items.append(item)
    items.sort(key=candidate_sort_key)
    strict_successes = [item for item in items if item["strict_success"]]
    below_rho = [item for item in items if item["below_rho_parent_certificate"]]
    best = (strict_successes or items or [None])[0]
    return {
        "best_column6_candidate": best,
        "below_rho_column6_support_row_count": len(below_rho),
        "column6_support_row_count": len(items),
        "known_dependent_support_control_count": known_dependent_count,
        "route_column6_counts": compact_counter(route_counts),
        "strict_column6_success_count": len(strict_successes),
        "top_column6_candidates": items[:32],
        "top_column6_support_counts": compact_counter(support_counts),
        "unique_column6_row_count": len(seen),
    }


def row_summary_for_representation(row: dict[str, Any]) -> dict[str, Any]:
    return p1081.row_summary(row)


def representation_report(
    packet_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    identity_model = p1082.build_model(packet_rows, candidate_rows, "identity", args.order)
    carrier_model = p1082.build_model(packet_rows, candidate_rows, "carrier_quotient_split6", args.order)
    with_carrier_model = p1082.build_model(packet_rows, candidate_rows, "split6", args.order)
    for model in (identity_model, carrier_model, with_carrier_model):
        model["strict_rows"] = packet_rows

    carrier_progress = p1082.progress_indices(candidate_rows, carrier_model, args.order, require_carrier_quotient=True)
    with_carrier_progress = p1082.progress_indices(
        candidate_rows,
        with_carrier_model,
        args.order,
        require_carrier_quotient=False,
    )
    collapse_count = 0
    nonzero_count = 0
    for index in carrier_progress:
        original_vector = identity_model["candidate_vectors"][index]
        residual = gap.reduce_row(original_vector, identity_model["strict_basis"], identity_model["strict_pivots"], args.order)
        if gap.normalize_vector(residual, args.order) is None:
            collapse_count += 1
        else:
            nonzero_count += 1

    top_rows = sorted(
        [candidate_rows[index] for index in carrier_progress],
        key=lambda row: (
            finite_charge(p1081.direct_charge(row)),
            row_summary_for_representation(row).get("artifact") or "",
            row_summary_for_representation(row).get("artifact_offset") or 0,
        ),
    )[:16]
    carrier_vectors = [carrier_model["candidate_vectors"][index] for index in carrier_progress]
    selected_rows = [candidate_rows[index] for index in carrier_progress]
    coeff_rank = p1082.rank([*carrier_model["strict_basis"], *carrier_vectors], args.order)
    aug_rank = p1082.rank(
        [
            *carrier_model["strict_aug_basis"],
            *[
                [*vector, int_value(row.get("rhs")) % args.order]
                for vector, row in zip(carrier_vectors, selected_rows)
            ],
        ],
        args.order,
    )
    best_charge = p1081.direct_charge(top_rows[0]) if top_rows else None
    best_rho = p1081.rho_steps(top_rows[0]) if top_rows else 137
    return {
        "carrier_quotient_augmented_matrix_rank": aug_rank,
        "carrier_quotient_coefficient_matrix_rank": coeff_rank,
        "carrier_quotient_consistent": coeff_rank == aug_rank,
        "carrier_quotient_progress_count": len(carrier_progress),
        "generic_rho_steps": best_rho or 137,
        "identity_projection_collapse_count": collapse_count,
        "identity_projection_nonzero_count": nonzero_count,
        "parent_certificate_charge_over_rho": best_charge,
        "representation_only": True,
        "split6_with_carrier_progress_count": len(with_carrier_progress),
        "top_carrier_quotient_rows": [row_summary_for_representation(row) for row in top_rows],
    }


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def actual_column6_case(report: dict[str, Any], column: int) -> bool:
    for key in ("priority_coeff_hits", "priority_term_hits", "coeff_support", "term_support"):
        if column in {int_value(item, -1) for item in list_value(report.get(key))}:
            return True
    return False


def metadata_column6_case(report: dict[str, Any], column: int) -> bool:
    return column in {int_value(item, -1) for item in list_value(report.get("selected_term_support"))}


def window_bounds(transfer_index: int, window_size: int) -> tuple[int, int]:
    start = transfer_index - (transfer_index % window_size)
    return start, start + window_size - 1


def direct_generation_command(source: str, case: dict[str, Any], out: str) -> str:
    case_arg = "|".join(
        [
            str(case["target"]),
            str(case["transfer_index"]),
            str(case["selector"]),
            str(case["top_k"]),
        ]
    )
    parts = [
        "python3",
        "tasks/ecdlp_index_calculus/low_term_total2_direct_source_relation_equation_certificate.py",
        "--source",
        source,
        "--cases",
        case_arg,
        "--out",
        out,
    ]
    return " ".join(shlex.quote(part) for part in parts)


def scan_column6_source_cases(args: argparse.Namespace) -> dict[str, Any]:
    paths = sorted(args.state_dir.glob(args.priority_scout_glob))
    actual_cases: list[dict[str, Any]] = []
    metadata_only_count = 0
    order11779_case_count = 0
    target_case_count = 0
    generated_commands: list[dict[str, Any]] = []
    for path in paths:
        payload = p1079.load_json(path)
        source_template = str((payload.get("artifacts") or {}).get("source_template") or "")
        for report in payload.get("case_reports") or []:
            if not isinstance(report, dict):
                continue
            if int_value(report.get("order")) != args.order:
                continue
            order11779_case_count += 1
            if str(report.get("target")) != args.target:
                continue
            target_case_count += 1
            actual = actual_column6_case(report, args.remaining_column)
            metadata_only = metadata_column6_case(report, args.remaining_column) and not actual
            if metadata_only:
                metadata_only_count += 1
            if not actual:
                continue
            transfer = int_value(report.get("transfer_index"))
            start, end = window_bounds(transfer, args.window_size)
            source = source_template.format(window=f"{start}_{end}", start=start, end=end) if source_template else ""
            out = str(
                args.state_dir
                / f"low_term_total2_direct_relation_equation_certificate_p1086_order11779_col6_{start}_{end}_probe.json"
            )
            case = {
                "artifact": str(path),
                "direct_ops_over_rho": report.get("direct_ops_over_rho")
                or report.get("source_charged_unit_ops_over_rho"),
                "priority_coeff_hits": report.get("priority_coeff_hits") or [],
                "priority_term_hits": report.get("priority_term_hits") or [],
                "public_key_verified_replay": report.get("public_key_verified_replay") or report.get("verified"),
                "row_keys": report.get("row_keys") or [],
                "selector": report.get("selector"),
                "source_artifact": source,
                "target": report.get("target"),
                "term_support": report.get("term_support") or [],
                "top_k": int_value(report.get("top_k")),
                "transfer_index": transfer,
            }
            actual_cases.append(case)
            generated_commands.append(
                {
                    "case": case,
                    "command": direct_generation_command(source, case, out) if source else None,
                    "out": out,
                    "source_artifact_exists": Path(source).exists() if source else False,
                }
            )
    return {
        "actual_order11779_target_column6_exported_case_count": len(actual_cases),
        "actual_order11779_target_column6_exported_cases": actual_cases[:24],
        "generation_commands": generated_commands[:24],
        "metadata_only_column6_case_count": metadata_only_count,
        "order11779_case_count": order11779_case_count,
        "priority_scout_artifact_count": len(paths),
        "target_order11779_case_count": target_case_count,
    }


def write_research_note(path: Path, payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    text = f"""# P1086 Column-6 Generator Refresh

## Handoff: P1086 column-6 refresh

### Claim or task
Refresh public source routes and representation views after P1085 to seek a verified below-rho order-11779 column-6 relation with marginal packet rank gain.

### Status
{summary["claim_status"]}

### Assumptions
- TOY-EVIDENCE: p231/order-11779 target family only.
- MODEL-BOUND: scanned local verifier-passing public certificate artifacts and local priority-scout route metadata.
- HEURISTIC: packet rank movement is an index-calculus precursor, not an individual-log completion.
- UNTESTED: no deployed prime-field curve relevance is claimed.

### Evidence so far
- P1085 packet reproduced: {summary["p1085_reproduced"]}; rank {summary["p1085_packet_rank"]}, free columns {summary["free_columns_after"]}.
- Column-6 support rows scored: {summary["column6_support_row_count"]}; strict successes: {summary["strict_column6_success_count"]}.
- Best coefficient candidate rank gain: {summary["marginal_rank_gain"]}; target-descent consistent: {summary["target_descent_consistent"]}.
- Actual order-11779 priority-scout column-6 exported cases: {summary["actual_order11779_target_column6_exported_case_count"]}.
- Scoped negative: {summary["scoped_negative"]}.

### Failure modes
- Existing below-rho column-6 supports remain rowspace-dependent against the P1085 packet.
- Order-9887 column-6 source hits are excluded from the order-11779 packet.
- Representation-only carrier-quotient progress is not accepted as a verified coefficient row.

### Next concrete action
Implement P1087 as a source-form generator that forces actual order-11779 column-6 exported forms before direct certificate export, using the P1086 scout gap as the guard.

### Artifact paths
- {payload["artifacts"]["result"]}
- {payload["artifacts"]["research_json"]}
- {payload["artifacts"]["research_md"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


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
    parser.add_argument("--p1085", type=Path, default=DEFAULT_P1085)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--research-json", type=Path, default=DEFAULT_RESEARCH_JSON)
    parser.add_argument("--research-md", type=Path, default=DEFAULT_RESEARCH_MD)
    parser.add_argument("--route-glob", action="append", help="Override route as name=glob; may be repeated.")
    parser.add_argument("--priority-scout-glob", default="low_term_total2_priority_column_form_scout_*col15_col6*_probe.json")
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--remaining-column", type=int, default=6)
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
    parser.add_argument("--window-size", type=int, default=8)
    args = parser.parse_args()

    factor_count = 17
    packet_rows, packet, column7_item, _column7_row = reproduce_p1085_packet(args, factor_count)
    p1085_payload = p1079.load_json(args.p1085) if args.p1085.exists() else {}
    candidate_certs, route_info, paths = load_routed_certs(args)
    candidate_rows = p1081.row_model_rows(candidate_certs, "coefficient", args.order, factor_count)
    routes = route_by_artifact(args)
    coefficient_scan = evaluate_column6_rows(packet_rows, candidate_rows, routes, args)
    source_case_scan = scan_column6_source_cases(args)
    representation = representation_report(packet_rows, candidate_rows, args)

    best = coefficient_scan["best_column6_candidate"] if isinstance(coefficient_scan["best_column6_candidate"], dict) else {}
    best_matrix = best.get("matrix") if isinstance(best.get("matrix"), dict) else {}
    strict_success = coefficient_scan["strict_column6_success_count"] > 0
    representation_signal = (
        representation["carrier_quotient_progress_count"] > 0
        and representation["identity_projection_nonzero_count"] > 0
    )
    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1086_VERIFIED_COLUMN6_PACKET_ROW"
    elif source_case_scan["actual_order11779_target_column6_exported_case_count"] > 0:
        claim_status = "OBSERVATION_P1086_COLUMN6_SOURCE_FORMS_NEED_DIRECT_CERTIFICATE_EXPORT"
    elif representation_signal:
        claim_status = "OBSERVATION_P1086_REPRESENTATION_COLUMN6_SIGNAL_NEEDS_COEFFICIENT_REALIZATION"
    else:
        claim_status = "NEGATIVE_RESULT_P1086_REFRESHED_ROUTES_NO_VERIFIED_COLUMN6_RANK_GAIN"

    scoped_negative = not strict_success
    summary = {
        "actual_order11779_target_column6_exported_case_count": source_case_scan[
            "actual_order11779_target_column6_exported_case_count"
        ],
        "augmented_matrix_rank": best_matrix.get("augmented_matrix_rank", packet["packet_augmented_rank_after"]),
        "best_column6_route": best.get("route"),
        "claim_status": claim_status,
        "coefficient_matrix_rank": best_matrix.get("coefficient_matrix_rank", packet["packet_rank_after"]),
        "column6_support_row_count": coefficient_scan["column6_support_row_count"],
        "free_columns_after": packet["free_columns_after"],
        "generic_rho_steps": 137,
        "known_dependent_support_control_count": coefficient_scan["known_dependent_support_control_count"],
        "marginal_rank_gain": best_matrix.get("marginal_rank_gain", 0),
        "p1085_packet_rank": packet["packet_rank_after"],
        "p1085_reproduced": packet["p1085_reproduced"],
        "parent_certificate_charge_over_rho": best.get("parent_certificate_charge_over_rho")
        or representation.get("parent_certificate_charge_over_rho"),
        "refreshed_route_artifact_count": len(paths),
        "representation_carrier_progress_count": representation["carrier_quotient_progress_count"],
        "scoped_negative": scoped_negative,
        "searched_or_newly_generated_source_routes": list(route_info),
        "strict_column6_success_count": coefficient_scan["strict_column6_success_count"],
        "target_descent_consistent": best_matrix.get("consistent", packet["target_descent_consistent_after"]),
        "unique_column6_row_count": coefficient_scan["unique_column6_row_count"],
        "verifier_status": "verified_artifact_rows_only",
    }
    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "p1085": p1069.sha256_file(args.p1085) if args.p1085.exists() else None,
            "route_artifact_count": len(paths),
            "route_artifact_digest": p1069.digest_paths(paths),
            "script": p1069.sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1085": str(args.p1085),
            "research_json": str(args.research_json),
            "research_md": str(args.research_md),
            "result": str(args.out),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "GENERATOR-REFRESH",
            "ORDER-FILTERED",
            "POLLARD-RHO-BOUNDARY",
        ],
        "coefficient_column6_scan": coefficient_scan,
        "controls": {
            "p1085_packet": packet,
            "p1085_summary": p1085_payload.get("summary"),
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "order_9887_hits_excluded_from_order_11779_packet": True,
            "representation_signal_not_counted_as_verified_coefficient_row": True,
            "secret_scalar_not_used": True,
        },
        "parameters": {
            "factor_count": factor_count,
            "priority_scout_glob": args.priority_scout_glob,
            "remaining_column": args.remaining_column,
            "route_globs": route_specs(args.route_glob),
            "target": args.target,
        },
        "representation_scan": representation,
        "route_info": route_info,
        "schema": SCHEMA,
        "source_case_scan": source_case_scan,
        "strict_success": strict_success,
        "summary": summary,
        "timestamp_utc": p1071.now_iso(),
    }
    p1079.write_json(args.out, payload)
    p1079.write_json(args.research_json, payload)
    write_research_note(args.research_md, payload)
    print(
        "claim={claim} p1085={p1085} column6_rows={rows} strict={strict} "
        "rank_gain={gain} free={free} scoped_negative={neg} out={out}".format(
            claim=claim_status,
            p1085=packet["p1085_reproduced"],
            rows=coefficient_scan["column6_support_row_count"],
            strict=coefficient_scan["strict_column6_success_count"],
            gain=summary["marginal_rank_gain"],
            free=packet["free_columns_after"],
            neg=scoped_negative,
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
