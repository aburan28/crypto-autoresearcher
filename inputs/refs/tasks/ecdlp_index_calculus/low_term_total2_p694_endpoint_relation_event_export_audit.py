#!/usr/bin/env python3
"""P694 endpoint-priority relation-event export audit.

P693 verifies that selected leaves for direct-verified order-9887 cases expose
factor columns 0 and 15 before public form export.  P694 tests the next gate:
do those endpoint-bearing selected scouts become relation events, exported
linear-form coefficients, or target-eliminated factor relations?
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
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = p693.DEFAULT_SOURCE
DEFAULT_PRODUCT = p693.DEFAULT_PRODUCT
DEFAULT_OUT = STATE_DIR / "low_term_total2_p694_endpoint_relation_event_export_audit_probe.json"


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


def contexts_from_source_case(context: dict[str, Any], source_case: dict[str, Any]) -> list[dict[str, Any]]:
    contexts: list[dict[str, Any]] = []
    for item in hit_stream_probe.unique_row_leaf_keys(source_case):
        row_key = str(item.get("row_key") or "")
        built = context.get("built_by_row", {}).get(row_key)
        components = context.get("components_by_row", {}).get(row_key)
        local_args = context.get("local_args_by_row", {}).get(row_key)
        if not isinstance(built, dict) or not isinstance(components, dict) or local_args is None:
            continue
        contexts.append(
            {
                "built": built,
                "components": components,
                "local_args": local_args,
                "row_key": row_key,
                "selected_leaf_indices": {
                    int_value(leaf) for leaf in item.get("leaf_indices") or []
                },
            }
        )
    return contexts


def selected_scout_records(contexts: list[dict[str, Any]], priority_columns: set[int]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for context in contexts:
        built = context["built"]
        components = context["components"]
        scouts_by_pos = {
            int_value(scout.get("scout_pos")): scout
            for scout in built.get("scouts") or []
            if scout.get("scout_pos") is not None
        }
        leaves = components.get("leaves") or []
        for leaf_index in sorted(context["selected_leaf_indices"]):
            if leaf_index < 0 or leaf_index >= len(leaves):
                continue
            for scout_pos in leaves[leaf_index].get("scout_positions") or []:
                scout = scouts_by_pos.get(int_value(scout_pos))
                if not scout:
                    continue
                support = sorted({int_value(index) for index, _sign in scout.get("signed_terms") or []})
                priority_hits = sorted(set(support) & priority_columns)
                records.append(
                    {
                        "leaf_index": leaf_index,
                        "priority_hits": priority_hits,
                        "row_key": context["row_key"],
                        "scout_pos": int_value(scout_pos),
                        "term_support": support,
                    }
                )
    return records


def support_from_coeffs(coeffs: list[Any], order: int) -> list[int]:
    return [index for index, value in enumerate(coeffs) if int_value(value) % order]


def relation_event_records(
    direct_rows: list[dict[str, Any]],
    order: int,
    priority_columns: set[int],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in direct_rows:
        row_key = str(row.get("row_key") or "")
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, terms = event["form"]
            factor_coeffs = [int_value(value) % order for value in coeffs[1:]]
            coeff_support = support_from_coeffs(factor_coeffs, order)
            term_support = sorted({int_value(term) for term in terms})
            records.append(
                {
                    "coeff_priority_hits": sorted(set(coeff_support) & priority_columns),
                    "coeff_support": coeff_support,
                    "factor_coeffs": factor_coeffs,
                    "form_index": int_value(event.get("form_index")),
                    "leaf_index": int_value(event.get("leaf_index")),
                    "q_coeff": int_value(coeffs[0]) % order if coeffs else 0,
                    "rhs": int_value(rhs) % order,
                    "row_key": row_key,
                    "scout_pos": int_value(event.get("scout_pos")),
                    "term_priority_hits": sorted(set(term_support) & priority_columns),
                    "term_support": term_support,
                }
            )
    return records


def target_relation_records(cert: dict[str, Any], priority_columns: set[int]) -> list[dict[str, Any]]:
    records = []
    for relation in factor_bank.target_eliminated_rows(cert):
        support = [int_value(value) for value in relation.get("factor_support") or []]
        priority_hits = sorted(set(support) & priority_columns)
        if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION":
            records.append(
                {
                    "canonical_rhs": relation.get("canonical_rhs"),
                    "factor_support": support,
                    "pair": relation.get("pair"),
                    "priority_hits": priority_hits,
                    "relation_status": relation.get("relation_status"),
                }
            )
    return records


def compact_case(
    product_case: dict[str, Any],
    source_case: dict[str, Any],
    contexts: list[dict[str, Any]],
    selected_records: list[dict[str, Any]],
    event_records: list[dict[str, Any]],
    target_records: list[dict[str, Any]],
    union: dict[str, Any],
    direct_ops: int,
    rho: int,
    order: int,
) -> dict[str, Any]:
    endpoint_scout_keys = {
        (record["row_key"], int_value(record["scout_pos"]))
        for record in selected_records
        if record["priority_hits"]
    }
    endpoint_leaf_keys = {
        (record["row_key"], int_value(record["leaf_index"]))
        for record in selected_records
        if record["priority_hits"]
    }
    relation_scout_keys = {
        (record["row_key"], int_value(record["scout_pos"])) for record in event_records
    }
    relation_leaf_keys = {
        (record["row_key"], int_value(record["leaf_index"])) for record in event_records
    }
    endpoint_events = [
        record for record in event_records if record["term_priority_hits"] or record["coeff_priority_hits"]
    ]
    endpoint_coeff_events = [record for record in event_records if record["coeff_priority_hits"]]
    endpoint_target_relations = [record for record in target_records if record["priority_hits"]]
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
        "endpoint_relation_scout_overlap_count": len(endpoint_scout_keys & relation_scout_keys),
        "endpoint_selected_leaf_relation_overlap_count": len(endpoint_leaf_keys & relation_leaf_keys),
        "endpoint_target_relation_count": len(endpoint_target_relations),
        "exported_endpoint_coeff_event_count": len(endpoint_coeff_events),
        "forms_count": len(event_records),
        "order": order,
        "priority_hits": sorted(set(selected_support) & set().union(*(r["priority_hits"] for r in selected_records))),
        "relation_event_count": len(event_records),
        "rho": rho,
        "row_keys": product_case.get("row_keys") or source_case.get("row_keys") or [],
        "selected_endpoint_scout_count": sum(1 for record in selected_records if record["priority_hits"]),
        "selected_leaf_indices": sorted(
            {
                leaf_index
                for context in contexts
                for leaf_index in context.get("selected_leaf_indices", set())
            }
        ),
        "selected_term_support": selected_support,
        "selector": product_case.get("selector"),
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
        return "P694_ENDPOINT_RELATIONS_SURVIVE_TARGET_ELIMINATION"
    if summary["exported_endpoint_coeff_event_count"]:
        return "P694_ENDPOINT_COEFFS_EXPORT_BUT_DO_NOT_SURVIVE_TARGET_ELIMINATION"
    if summary["endpoint_relation_event_count"]:
        return "P694_ENDPOINT_TERMS_REACH_RELATION_EVENTS_WITHOUT_TARGET_PROGRESS"
    return "NEGATIVE_RESULT_P694_ENDPOINT_SUPPORT_NOT_EXPORTED_IN_RELATION_FORMS"


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
    certificates = []
    skipped_direct_verified_without_priority = 0
    skipped_missing_source = 0
    eligible_direct_verified = 0
    selected_column_counts: Counter[int] = Counter()
    selected_leaf_counts: Counter[int] = Counter()
    relation_column_counts: Counter[int] = Counter()
    coeff_column_counts: Counter[int] = Counter()
    target_column_counts: Counter[int] = Counter()
    relation_leaf_counts: Counter[int] = Counter()
    endpoint_leaf_counts: Counter[int] = Counter()

    for product_case in p693.product_cases(product, args.target, 0):
        if not p693.bool_field(product_case, "direct_union_public_key_verified", "direct_public_key_verified"):
            continue
        eligible_direct_verified += 1
        source_case = source_index.get(p693.exact_case_key(product_case))
        if source_case is None:
            skipped_missing_source += 1
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
        contexts = contexts_from_source_case(context, source_case)
        selected_records = selected_scout_records(contexts, priority_columns)
        selected_priority = {
            column
            for record in selected_records
            for column in record.get("priority_hits") or []
        }
        if not selected_priority:
            skipped_direct_verified_without_priority += 1
            continue
        if args.max_cases > 0 and len(case_reports) >= args.max_cases:
            break

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
        event_records = relation_event_records(direct_rows, order, priority_columns)
        target_records = target_relation_records(cert, priority_columns)
        report = compact_case(
            product_case,
            source_case,
            contexts,
            selected_records,
            event_records,
            target_records,
            union,
            direct_ops,
            rho,
            order,
        )
        case_reports.append(report)
        certificates.append(cert)
        for record in selected_records:
            selected_leaf_counts[int_value(record.get("leaf_index"))] += 1
            if record["priority_hits"]:
                endpoint_leaf_counts[int_value(record.get("leaf_index"))] += 1
            selected_column_counts.update(record.get("priority_hits") or [])
        for record in event_records:
            relation_leaf_counts[int_value(record.get("leaf_index"))] += 1
            relation_column_counts.update(record.get("term_priority_hits") or [])
            coeff_column_counts.update(record.get("coeff_priority_hits") or [])
        for record in target_records:
            target_column_counts.update(record.get("priority_hits") or [])

    target_endpoint_reports = [row for row in case_reports if row["endpoint_target_relation_count"]]
    exported_endpoint_reports = [row for row in case_reports if row["exported_endpoint_coeff_event_count"]]
    relation_endpoint_reports = [row for row in case_reports if row["endpoint_relation_event_count"]]
    leaf_overlap_reports = [
        row for row in case_reports if row["endpoint_selected_leaf_relation_overlap_count"]
    ]
    factor_audit = factor_bank.audit_order(certificates, int_value(args.order)) if certificates else {}
    summary = {
        "analyzed_case_count": len(case_reports),
        "candidate_factor_rank": factor_audit.get("rank"),
        "candidate_unique_factor_relation_count": factor_audit.get("unique_factor_relation_count"),
        "context_cache_entry_count": len(context_cache),
        "direct_replay_verified_count": sum(1 for row in case_reports if row["union_public_key_verified"]),
        "eligible_direct_verified_product_case_count": eligible_direct_verified,
        "endpoint_relation_event_case_count": len(relation_endpoint_reports),
        "endpoint_relation_event_count": sum(row["endpoint_relation_event_count"] for row in case_reports),
        "endpoint_relation_scout_overlap_count": sum(
            row["endpoint_relation_scout_overlap_count"] for row in case_reports
        ),
        "endpoint_selected_leaf_relation_overlap_case_count": len(leaf_overlap_reports),
        "endpoint_selected_leaf_relation_overlap_count": sum(
            row["endpoint_selected_leaf_relation_overlap_count"] for row in case_reports
        ),
        "exported_endpoint_coeff_case_count": len(exported_endpoint_reports),
        "exported_endpoint_coeff_event_count": sum(
            row["exported_endpoint_coeff_event_count"] for row in case_reports
        ),
        "relation_event_count": sum(row["relation_event_count"] for row in case_reports),
        "selected_endpoint_scout_count": sum(row["selected_endpoint_scout_count"] for row in case_reports),
        "skipped_direct_verified_without_priority_count": skipped_direct_verified_without_priority,
        "skipped_missing_source_count": skipped_missing_source,
        "target_eliminated_endpoint_relation_case_count": len(target_endpoint_reports),
        "target_eliminated_endpoint_relation_count": sum(
            row["endpoint_target_relation_count"] for row in case_reports
        ),
        "target_eliminated_factor_relation_count": sum(row["target_relation_count"] for row in case_reports),
    }
    summary.update(
        {
            "endpoint_selected_leaf_index_counts": {
                str(key): endpoint_leaf_counts[key] for key in sorted(endpoint_leaf_counts)
            },
            "priority_columns": sorted(priority_columns),
            "priority_selected_scout_counts": {
                str(column): selected_column_counts[column] for column in sorted(priority_columns)
            },
            "priority_relation_event_counts": {
                str(column): relation_column_counts[column] for column in sorted(priority_columns)
            },
            "priority_exported_coeff_counts": {
                str(column): coeff_column_counts[column] for column in sorted(priority_columns)
            },
            "priority_target_relation_counts": {
                str(column): target_column_counts[column] for column in sorted(priority_columns)
            },
            "relation_leaf_index_counts": {
                str(key): relation_leaf_counts[key] for key in sorted(relation_leaf_counts)
            },
            "selected_leaf_index_counts": {
                str(key): selected_leaf_counts[key] for key in sorted(selected_leaf_counts)
            },
        }
    )
    claim_status = determine_claim(summary)
    sample_limit = max(0, int_value(args.sample_limit, 12))
    return {
        "artifacts": {"product": str(product_path), "source": str(source_path)},
        "case_examples": {
            "endpoint_lost_before_relation_events": [
                row for row in case_reports if not row["endpoint_relation_event_count"]
            ][:sample_limit],
            "endpoint_relation_events": relation_endpoint_reports[:sample_limit],
            "endpoint_selected_leaf_relation_overlap": leaf_overlap_reports[:sample_limit],
            "exported_endpoint_coeffs": exported_endpoint_reports[:sample_limit],
            "target_eliminated_endpoint_relations": target_endpoint_reports[:sample_limit],
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "factor_audit": factor_audit,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: relation events are local verifier public-form events for selected leaves.",
            "HEURISTIC: endpoint selected-scout visibility is a generator-steering signal, not target descent by itself.",
            "NEGATIVE SCOPE: if no endpoint relation events appear, this only rules out case-level export conditioning for the current P658 direct-verified source family.",
            "This is not a faster-than-Pollard-rho ECDLP algorithm.",
        ],
        "method": "p694_endpoint_relation_event_export_audit",
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "order": int_value(args.order),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p694_endpoint_relation_event_export_audit.v1",
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
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
