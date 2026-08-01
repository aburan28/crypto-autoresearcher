#!/usr/bin/env python3
"""P1076 blocker prefilter/amortization audit for the P1075 near miss."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1072_p231_topk7_split_validation as p1072
import low_term_total2_p1073_p231_topk7_order_compression as p1073
import low_term_total2_p1074_p231_disjoint_source_packet_validation as p1074
import low_term_total2_p1075_p231_public_window_router as p1075


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1076_p231_blocker_prefilter_audit.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1072 = STATE_DIR / "low_term_total2_p1072_p231_topk7_split_validation_probe.json"
DEFAULT_P1073 = STATE_DIR / "low_term_total2_p1073_p231_topk7_order_compression_probe.json"
DEFAULT_P1074 = STATE_DIR / "low_term_total2_p1074_p231_disjoint_source_packet_validation_probe.json"
DEFAULT_P1075 = STATE_DIR / "low_term_total2_p1075_p231_public_window_router_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1076_p231_blocker_prefilter_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1076_p231_blocker_prefilter_audit.v1"

FilterRule = Callable[[dict[str, Any]], bool]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def support(ref: dict[str, Any]) -> list[int]:
    return sorted(int(item) for item in ref.get("selected_term_support") or [])


def feature_summary(ref: dict[str, Any]) -> dict[str, Any]:
    salts = p1073.salts(ref)
    return {
        "case_id": ref["case_id"],
        "direct_ops_over_rho": p1073.direct_ops(ref),
        "offset": ref["transfer_index"] - ref["window_start"],
        "priority_hits": ref.get("priority_hits") or [],
        "priority_count": p1073.priority_count(ref),
        "row_keys": ref.get("row_keys") or [],
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "salt_span": max(salts) - min(salts) if salts else None,
        "salt_sum": sum(salts) if salts else None,
        "selected_term_support": support(ref),
        "support_size": len(support(ref)),
        "transfer_index": ref["transfer_index"],
        "window": ref["window"],
        "window_start": ref["window_start"],
    }


def selected_case_for_ref(args: argparse.Namespace, ref: dict[str, Any]) -> dict[str, Any] | None:
    path = args.state_dir / f"low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_{ref['window']}_probe.json"
    if not path.exists():
        return None
    payload = load_json(path)
    for case in payload.get("case_reports") or []:
        if (
            isinstance(case, dict)
            and str(case.get("target")) == args.target
            and str(case.get("selector")) == args.selector
            and p1055.int_value(case.get("top_k"), -1) == args.top_k
            and p1055.int_value(case.get("transfer_index"), -1) == p1055.int_value(ref.get("transfer_index"), -2)
        ):
            return case
    return None


def row_support_digest(cert: dict[str, Any], order: int, factor_hint: int = 64) -> dict[str, Any]:
    rows = gap.unique_relation_rows([cert], order, factor_hint)
    if not rows:
        return {"coeff_len": 0, "factor_support": [], "row_count": 0}
    coeffs = rows[0]["coeffs"]
    return {
        "coeff_len": len(coeffs),
        "factor_support": [idx for idx, coeff in enumerate(coeffs) if coeff],
        "row_count": len(rows),
    }


def cert_descriptor(cert: dict[str, Any], order: int) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": cert.get("_artifact_offset"),
        "clause": cert.get("clause") or selected.get("clause"),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "forms_count": cert.get("forms_count"),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "row_keys": selected.get("row_keys") or [],
        "row_support": row_support_digest(cert, order),
        "selector": selected.get("selector"),
        "target": selected.get("target"),
        "top_k": selected.get("top_k"),
        "transfer_index": selected.get("transfer_index"),
    }


def cert_context_for_ref(
    args: argparse.Namespace,
    ref: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
) -> dict[str, Any]:
    row = factor_rows[ref["window"]]
    scorer = row["scorer_artifact"]
    base_paths, candidate_paths = p1055.scorer_paths(scorer)
    direct_paths = p1055.direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
    all_direct_certs = p1055.load_certs_cached(direct_paths, cache)
    matched = [
        cert
        for cert in all_direct_certs
        if p1071.cert_matches_ref(cert, ref, ref.get("source") or args.source)
    ]
    selected_case = selected_case_for_ref(args, ref)
    return {
        "all_direct_certificates": [cert_descriptor(cert, args.order) for cert in all_direct_certs],
        "base_certificate_count": len(p1055.load_certs_cached(base_paths, cache)),
        "base_paths": [str(path) for path in base_paths],
        "direct_paths": [str(path) for path in direct_paths],
        "matched_direct_certificates": [cert_descriptor(cert, args.order) for cert in matched],
        "matched_direct_certificate_count": len(matched),
        "scorer_artifact": str(scorer),
        "scorer_summary": (load_json(scorer).get("summary") if scorer.exists() else None),
        "selected_case_labels": (
            {
                "direct_public_key_verified": selected_case.get("direct_public_key_verified"),
                "public_product_gate_selected": selected_case.get("public_product_gate_selected"),
                "shared_product_ops_over_rho": selected_case.get("shared_product_ops_over_rho"),
                "shared_product_public_key_verified": selected_case.get("shared_product_public_key_verified"),
                "shared_product_rank": selected_case.get("shared_product_rank"),
            }
            if selected_case
            else None
        ),
    }


def diagnostic_filters() -> list[dict[str, Any]]:
    return [
        {"name": "salt_max_le_170", "rule": lambda ref: p1073.salt_max(ref) <= 170},
        {"name": "salt_min_le_165", "rule": lambda ref: p1073.salt_min(ref) <= 165},
        {"name": "salt_sum_le_335", "rule": lambda ref: p1073.salt_sum(ref) <= 335},
        {"name": "salt_span_le_5", "rule": lambda ref: p1073.salt_span(ref) <= 5},
        {"name": "offset_ge_5", "rule": lambda ref: (ref["transfer_index"] - ref["window_start"]) >= 5},
        {"name": "direct_ops_ge_0_75", "rule": lambda ref: p1073.direct_ops(ref) >= 0.75},
        {"name": "has_salt165", "rule": lambda ref: 165 in p1073.salts(ref)},
        {"name": "has_salt170", "rule": lambda ref: 170 in p1073.salts(ref)},
        {"name": "no_salt174", "rule": lambda ref: 174 not in p1073.salts(ref)},
    ]


def scan_filtered(
    ordered: list[dict[str, Any]],
    rule: FilterRule,
    stage1_refs: list[dict[str, Any]],
    stage1_packet: dict[str, Any],
    factor_rows: dict[str, dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
    priority_columns: list[int],
    carrier_case_id: str,
) -> dict[str, Any]:
    filtered = [ref for ref in ordered if rule(ref)]
    result = p1072.prefix_scan(
        filtered,
        stage1_refs,
        stage1_packet,
        factor_rows,
        cache,
        args,
        priority_columns,
        args.target_column,
    )
    first = result.get("first_target_column_prefix")
    carrier_rank = next((idx + 1 for idx, ref in enumerate(filtered) if ref["case_id"] == carrier_case_id), None)
    return {
        "carrier_rank": carrier_rank,
        "filtered_case_count": len(filtered),
        "first_target_column_prefix": first,
        "keeps_carrier": carrier_rank is not None,
        "strict_below_rho": p1074.below_rho(first),
        "top_filtered_refs": [feature_summary(ref) for ref in filtered[:5]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1072", type=Path, default=DEFAULT_P1072)
    parser.add_argument("--p1073", type=Path, default=DEFAULT_P1073)
    parser.add_argument("--p1074", type=Path, default=DEFAULT_P1074)
    parser.add_argument("--p1075", type=Path, default=DEFAULT_P1075)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target-column", type=int, default=15)
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

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1075_payload = load_json(args.p1075)
    stage1_refs, validation_refs, stage1_packet, factor_rows, cache, inventory, factor_paths, selected_paths = p1073.build_context(args)
    best_policy = (p1075_payload.get("summary") or {}).get("best_policy") or {}
    ordered_case_ids = best_policy.get("ordered_case_ids") or []
    if len(ordered_case_ids) < 2:
        raise ValueError("P1075 best policy does not expose blocker/carrier prefix")
    blocker_case_id = ordered_case_ids[0]
    carrier_case_id = (p1075_payload.get("summary") or {}).get("carrier_case_id")
    refs_by_id = {ref["case_id"]: ref for ref in validation_refs}
    blocker_ref = refs_by_id[blocker_case_id]
    carrier_ref = refs_by_id[carrier_case_id]
    window_policy = next(item for item in p1075.window_key_catalog() if item["name"] == "window_max_direct_ops_asc")
    case_policy = next(item for item in p1075.case_order_catalog() if item["name"] == "chronological")
    winner_window = (p1075_payload.get("parameters") or {}).get("excluded_winner_window")
    routed_refs = [ref for ref in validation_refs if ref["window"] != winner_window]
    best_ordered = p1075.ordered_by_window_policy(routed_refs, factor_rows, window_policy, case_policy)

    blocker_ctx = cert_context_for_ref(args, blocker_ref, factor_rows, cache)
    carrier_ctx = cert_context_for_ref(args, carrier_ref, factor_rows, cache)
    combined_charge = round(p1073.direct_ops(blocker_ref) + p1073.direct_ops(carrier_ref), 8)
    carrier_charge = p1073.direct_ops(carrier_ref)
    required_savings = round(max(0.0, combined_charge - 1.0), 8)
    remaining_prefilter_budget = round(max(0.0, 1.0 - carrier_charge), 8)
    filter_results = []
    for item in diagnostic_filters():
        scan = scan_filtered(
            best_ordered,
            item["rule"],
            stage1_refs,
            stage1_packet,
            factor_rows,
            cache,
            args,
            priority_columns,
            carrier_case_id,
        )
        filter_results.append(
            {
                **scan,
                "diagnostic_only": True,
                "filter": item["name"],
                "posthoc_from_blocker_contrast": True,
            }
        )
    diagnostic_winners = [
        item
        for item in filter_results
        if item["strict_below_rho"] and item["keeps_carrier"]
    ]
    strict_success = False
    diagnostic_success = bool(diagnostic_winners)
    if diagnostic_success:
        claim_status = "OBSERVATION_P1076_POSTHOC_PUBLIC_BLOCKER_FILTERS_RESTORE_BELOW_RHO_NEED_HOLDOUT"
    else:
        claim_status = "NEGATIVE_RESULT_P1076_NO_PREFILTER_OR_AMORTIZATION_SIGNAL"

    direct_path_overlap = sorted(set(blocker_ctx["direct_paths"]) & set(carrier_ctx["direct_paths"]))
    base_path_overlap = sorted(set(blocker_ctx["base_paths"]) & set(carrier_ctx["base_paths"]))
    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1072": p1069.sha256_file(args.p1072) if args.p1072.exists() else None,
            "p1073": p1069.sha256_file(args.p1073) if args.p1073.exists() else None,
            "p1074": p1069.sha256_file(args.p1074) if args.p1074.exists() else None,
            "p1075": p1069.sha256_file(args.p1075) if args.p1075.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1072": str(args.p1072),
            "p1073": str(args.p1073),
            "p1074": str(args.p1074),
            "p1075": str(args.p1075),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "POSTHOC-DIAGNOSTIC",
            "BLOCKER-PREFILTER",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "best_p1075_policy": best_policy,
            "blocker_certificate_context": blocker_ctx,
            "carrier_certificate_context": carrier_ctx,
            "diagnostic_filter_results": filter_results,
        },
        "expanded_source_inventory": inventory,
        "feature_comparison": {
            "blocker": feature_summary(blocker_ref),
            "carrier": feature_summary(carrier_ref),
            "priority_hits_equal": (blocker_ref.get("priority_hits") or []) == (carrier_ref.get("priority_hits") or []),
            "row_key_overlap": sorted(set(blocker_ref.get("row_keys") or []) & set(carrier_ref.get("row_keys") or [])),
            "salt_overlap": sorted(set(p1073.salts(blocker_ref)) & set(p1073.salts(carrier_ref))),
            "selected_term_support_equal": support(blocker_ref) == support(carrier_ref),
        },
        "honesty_boundary": {
            "certificate_selector_rejection_is_post_generation_label": True,
            "diagnostic_filters_are_posthoc": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "strict_prefilter_validated": strict_success,
            "target_descent_closed": False,
        },
        "parameters": {
            "blocker_case_id": blocker_case_id,
            "carrier_case_id": carrier_case_id,
            "carrier_only_charge_over_rho": carrier_charge,
            "combined_prefix_charge_over_rho": combined_charge,
            "remaining_prefilter_budget_over_rho": remaining_prefilter_budget,
            "required_savings_over_rho": required_savings,
            "source": args.source,
            "target": args.target,
        },
        "record_counts": {
            "diagnostic_filter_count": len(filter_results),
            "diagnostic_winner_count": len(diagnostic_winners),
            "direct_path_overlap_count": len(direct_path_overlap),
            "shared_base_path_count": len(base_path_overlap),
        },
        "schema": SCHEMA,
        "strict_success": strict_success,
        "summary": {
            "blocker_matched_direct_certificate_count": blocker_ctx["matched_direct_certificate_count"],
            "carrier_matched_direct_certificate_count": carrier_ctx["matched_direct_certificate_count"],
            "claim_status": claim_status,
            "diagnostic_success": diagnostic_success,
            "diagnostic_winner_filters": [item["filter"] for item in diagnostic_winners],
            "direct_path_overlap_count": len(direct_path_overlap),
            "remaining_prefilter_budget_over_rho": remaining_prefilter_budget,
            "required_savings_over_rho": required_savings,
            "shared_base_path_count": len(base_path_overlap),
            "strict_success": strict_success,
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={strict} diagnostic_success={diag} "
        "filters={filters} winners={winners} blocker_certs={bc} carrier_certs={cc} out={out}".format(
            claim=claim_status,
            strict=strict_success,
            diag=diagnostic_success,
            filters=len(filter_results),
            winners=len(diagnostic_winners),
            bc=blocker_ctx["matched_direct_certificate_count"],
            cc=carrier_ctx["matched_direct_certificate_count"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
