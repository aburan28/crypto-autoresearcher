#!/usr/bin/env python3
"""P695 endpoint-event surface scout over the P658 order-9887 family.

P694 showed that direct-verified endpoint-support cases do not export endpoint
columns into relation forms.  This scout searches the broader source/product
surface for emitted relation events whose public form terms or coefficients
touch endpoint columns 0 or 15, then records whether any such events already
have direct verifier support or target-eliminated rank value.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_direct_source_relation_equation_certificate as direct_export
import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p694_endpoint_relation_event_export_audit as p694
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = p693.DEFAULT_SOURCE
DEFAULT_PRODUCT = p693.DEFAULT_PRODUCT
DEFAULT_OUT = STATE_DIR / "low_term_total2_p695_endpoint_event_surface_scout_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def selector_mode(selector: Any) -> str:
    return str(selector or "").split("__", 1)[0]


def support_key(values: list[int]) -> str:
    return ",".join(str(value) for value in values)


def event_priority_records(event_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        record
        for record in event_records
        if record.get("term_priority_hits") or record.get("coeff_priority_hits")
    ]


def coeff_priority_records(event_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [record for record in event_records if record.get("coeff_priority_hits")]


def compact_event(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "coeff_priority_hits": record.get("coeff_priority_hits") or [],
        "coeff_support": record.get("coeff_support") or [],
        "form_index": int_value(record.get("form_index")),
        "leaf_index": int_value(record.get("leaf_index")),
        "q_coeff": int_value(record.get("q_coeff")),
        "row_key": record.get("row_key"),
        "scout_pos": int_value(record.get("scout_pos")),
        "term_priority_hits": record.get("term_priority_hits") or [],
        "term_support": record.get("term_support") or [],
    }


def compact_case_report(
    product_case: dict[str, Any],
    source_case: dict[str, Any],
    selected_records: list[dict[str, Any]],
    event_records: list[dict[str, Any]],
    target_records: list[dict[str, Any]],
    union: dict[str, Any],
    direct_ops: int,
    rho: int,
    order: int,
    sample_limit: int,
) -> dict[str, Any]:
    endpoint_events = event_priority_records(event_records)
    coeff_events = coeff_priority_records(event_records)
    endpoint_target_relations = [record for record in target_records if record.get("priority_hits")]
    selected_endpoint_scouts = [record for record in selected_records if record.get("priority_hits")]
    selected_support = sorted(
        {
            column
            for record in selected_records
            for column in record.get("term_support") or []
        }
    )
    return {
        "direct_ops": direct_ops,
        "direct_ops_over_rho": round(direct_ops / max(1, rho), 8) if rho else None,
        "endpoint_relation_event_count": len(endpoint_events),
        "endpoint_relation_event_samples": [compact_event(record) for record in endpoint_events[:sample_limit]],
        "endpoint_target_relation_count": len(endpoint_target_relations),
        "exported_endpoint_coeff_event_count": len(coeff_events),
        "forms_count": len(event_records),
        "order": order,
        "relation_event_count": len(event_records),
        "rho": rho,
        "row_keys": product_case.get("row_keys") or source_case.get("row_keys") or [],
        "selected_endpoint_scout_count": len(selected_endpoint_scouts),
        "selected_term_support": selected_support,
        "selector": product_case.get("selector"),
        "selector_mode": selector_mode(product_case.get("selector")),
        "source_policy": source_case.get("_source_policy"),
        "target": product_case.get("target"),
        "target_relation_count": len(target_records),
        "top_k": int_value(product_case.get("top_k")),
        "transfer_index": int_value(product_case.get("transfer_index")),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_rank": int_value(union.get("union_rank")),
        "union_relation_count": int_value(union.get("union_relation_count")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["target_eliminated_endpoint_relation_count"]:
        return "P695_ENDPOINT_EVENT_TARGET_RELATION_CANDIDATE"
    if summary["direct_verified_endpoint_event_case_count"]:
        return "P695_DIRECT_VERIFIED_ENDPOINT_EVENTS_NEED_RANK_SCORING"
    if summary["exported_endpoint_coeff_event_count"]:
        return "P695_ENDPOINT_EVENTS_EXIST_NEED_VERIFIER_ROUTE"
    return "NEGATIVE_RESULT_P695_NO_ENDPOINT_RELATION_EVENTS_IN_P658_SURFACE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.source)
    product_path = Path(args.product)
    source = load_json(source_path)
    product = load_json(product_path)
    priority_columns = p693.parse_columns(args.priority_columns)
    source_index = p693.build_source_index(source)

    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}

    case_reports = []
    endpoint_case_reports = []
    endpoint_certificates = []
    relation_event_count = 0
    selected_endpoint_scout_count = 0
    missing_source_case_count = 0
    direct_verified_count = 0
    direct_verified_endpoint_event_count = 0
    target_eliminated_endpoint_relation_count = 0
    target_eliminated_endpoint_relation_case_count = 0
    endpoint_relation_event_count = 0
    exported_endpoint_coeff_event_count = 0
    endpoint_relation_event_case_count = 0
    exported_endpoint_coeff_case_count = 0
    priority_relation_event_counts: Counter[int] = Counter()
    priority_exported_coeff_counts: Counter[int] = Counter()
    priority_target_relation_counts: Counter[int] = Counter()
    endpoint_selector_modes: Counter[str] = Counter()
    endpoint_leaf_counts: Counter[int] = Counter()
    endpoint_support_shapes: Counter[str] = Counter()

    for product_case in p693.product_cases(product, args.target, int_value(args.max_cases)):
        source_case = source_index.get(p693.exact_case_key(product_case))
        if source_case is None:
            missing_source_case_count += 1
            continue
        context = hit_stream_probe.scan_case_context(
            verifier,
            records,
            config_source,
            specs_by_target,
            source_case,
            probe_args,
            context_cache,
        )
        contexts = p694.contexts_from_source_case(context, source_case)
        selected_records = p694.selected_scout_records(contexts, priority_columns)
        selected_endpoint_scout_count += sum(1 for record in selected_records if record.get("priority_hits"))
        direct_rows, direct_ops, rho, _profiles = direct_export.timing_probe.direct_witness_rows(
            verifier,
            contexts,
        )
        built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
        union = direct_export.direct_witness_probe.union_derive(
            verifier,
            direct_rows,
            built_by_row,
            "_scan",
        )
        if bool(union.get("union_public_key_verified")):
            direct_verified_count += 1
        order = int(contexts[0]["built"]["order"]) if contexts else 0
        events = direct_export.direct_unique_events(direct_rows)
        forms = [direct_export.compact_form(event, order) for event in events]
        cert = {
            "certificate_status": "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if bool(union.get("union_public_key_verified"))
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW",
            "forms": forms,
            "forms_count": len(forms),
            "order": order,
            "public_key_verified": bool(union.get("union_public_key_verified")),
            "rank": int_value(union.get("union_rank")),
            "selected": {
                "direct_ops_over_rho": round(direct_ops / max(1, rho), 8) if rho else None,
                "row_keys": product_case.get("row_keys") or source_case.get("row_keys") or [],
                "selector": product_case.get("selector"),
                "target": product_case.get("target"),
                "top_k": int_value(product_case.get("top_k")),
                "transfer_index": int_value(product_case.get("transfer_index")),
            },
        }
        event_records = p694.relation_event_records(direct_rows, order, priority_columns)
        target_records = p694.target_relation_records(cert, priority_columns)
        endpoint_events = event_priority_records(event_records)
        coeff_events = coeff_priority_records(event_records)
        endpoint_targets = [record for record in target_records if record.get("priority_hits")]
        relation_event_count += len(event_records)
        endpoint_relation_event_count += len(endpoint_events)
        exported_endpoint_coeff_event_count += len(coeff_events)
        target_eliminated_endpoint_relation_count += len(endpoint_targets)
        if endpoint_events:
            endpoint_relation_event_case_count += 1
            endpoint_selector_modes[selector_mode(product_case.get("selector"))] += 1
            for record in endpoint_events:
                endpoint_leaf_counts[int_value(record.get("leaf_index"))] += 1
                endpoint_support_shapes[support_key(record.get("coeff_support") or [])] += 1
                priority_relation_event_counts.update(record.get("term_priority_hits") or [])
        if coeff_events:
            exported_endpoint_coeff_case_count += 1
            for record in coeff_events:
                priority_exported_coeff_counts.update(record.get("coeff_priority_hits") or [])
        if endpoint_targets:
            target_eliminated_endpoint_relation_case_count += 1
            for record in endpoint_targets:
                priority_target_relation_counts.update(record.get("priority_hits") or [])
        if endpoint_events and bool(union.get("union_public_key_verified")):
            direct_verified_endpoint_event_count += 1
        if endpoint_events:
            report = compact_case_report(
                product_case,
                source_case,
                selected_records,
                event_records,
                target_records,
                union,
                direct_ops,
                rho,
                order,
                int_value(args.event_sample_limit, 6),
            )
            endpoint_case_reports.append(report)
            endpoint_certificates.append(cert)
        if len(case_reports) < int_value(args.sample_limit, 12):
            case_reports.append(
                compact_case_report(
                    product_case,
                    source_case,
                    selected_records,
                    event_records,
                    target_records,
                    union,
                    direct_ops,
                    rho,
                    order,
                    int_value(args.event_sample_limit, 6),
                )
            )

    endpoint_factor_audit = (
        factor_bank.audit_order(endpoint_certificates, int_value(args.order))
        if endpoint_certificates
        else {}
    )
    summary = {
        "case_count": len(p693.product_cases(product, args.target, int_value(args.max_cases))),
        "context_cache_entry_count": len(context_cache),
        "direct_verified_case_count": direct_verified_count,
        "direct_verified_endpoint_event_case_count": direct_verified_endpoint_event_count,
        "endpoint_event_candidate_factor_rank": endpoint_factor_audit.get("rank"),
        "endpoint_event_candidate_unique_factor_relation_count": endpoint_factor_audit.get("unique_factor_relation_count"),
        "endpoint_relation_event_case_count": endpoint_relation_event_case_count,
        "endpoint_relation_event_count": endpoint_relation_event_count,
        "exported_endpoint_coeff_case_count": exported_endpoint_coeff_case_count,
        "exported_endpoint_coeff_event_count": exported_endpoint_coeff_event_count,
        "missing_source_case_count": missing_source_case_count,
        "relation_event_count": relation_event_count,
        "selected_endpoint_scout_count": selected_endpoint_scout_count,
        "target_eliminated_endpoint_relation_case_count": target_eliminated_endpoint_relation_case_count,
        "target_eliminated_endpoint_relation_count": target_eliminated_endpoint_relation_count,
    }
    summary.update(
        {
            "endpoint_event_leaf_index_counts": {
                str(key): endpoint_leaf_counts[key] for key in sorted(endpoint_leaf_counts)
            },
            "endpoint_event_selector_mode_counts": dict(sorted(endpoint_selector_modes.items())),
            "endpoint_event_support_shape_counts": dict(endpoint_support_shapes.most_common(20)),
            "priority_columns": sorted(priority_columns),
            "priority_exported_coeff_counts": {
                str(column): priority_exported_coeff_counts[column] for column in sorted(priority_columns)
            },
            "priority_relation_event_counts": {
                str(column): priority_relation_event_counts[column] for column in sorted(priority_columns)
            },
            "priority_target_relation_counts": {
                str(column): priority_target_relation_counts[column] for column in sorted(priority_columns)
            },
        }
    )
    claim_status = determine_claim(summary)
    sample_limit = max(0, int_value(args.sample_limit, 12))
    return {
        "artifacts": {"product": str(product_path), "source": str(source_path)},
        "case_examples": {
            "endpoint_event_cases": endpoint_case_reports[:sample_limit],
            "scanned_cases": case_reports[:sample_limit],
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "endpoint_factor_audit": endpoint_factor_audit,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: endpoint relation events are local verifier public-form events on the current P658 source family.",
            "HEURISTIC: endpoint event hits are generator-steering evidence, not a full target descent.",
            "NEGATIVE SCOPE: no endpoint events here only rules out the current P658 emitted-event surface, not all endpoint-preserving generators.",
            "This is not a faster-than-Pollard-rho ECDLP algorithm.",
        ],
        "method": "p695_endpoint_event_surface_scout",
        "parameters": {
            "event_sample_limit": int_value(args.event_sample_limit),
            "max_cases": int_value(args.max_cases),
            "order": int_value(args.order),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p695_endpoint_event_surface_scout.v1",
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--order", type=int, default=9887)
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--event-sample-limit", type=int, default=6)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
