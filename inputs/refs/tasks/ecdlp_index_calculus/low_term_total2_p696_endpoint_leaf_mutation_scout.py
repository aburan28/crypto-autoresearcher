#!/usr/bin/env python3
"""P696 endpoint leaf-mutation scout.

P695 rules out endpoint-bearing relation events on the selected P658 surface.
This scout mutates one layer earlier inside the reconstructed row contexts:
scan every candidate leaf whose scout positions contain endpoint columns 0 or
15, then test whether selecting that leaf alone can emit an endpoint-bearing
public relation event.
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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = p693.DEFAULT_SOURCE
DEFAULT_PRODUCT = p693.DEFAULT_PRODUCT
DEFAULT_OUT = STATE_DIR / "low_term_total2_p696_endpoint_leaf_mutation_scout_probe.json"


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


def support_key(values: list[int]) -> str:
    return ",".join(str(value) for value in values)


def row_context_key(context: dict[str, Any]) -> tuple[str, int, int, str]:
    built = context["built"]
    return (
        str(built.get("target")),
        int_value(built.get("transfer_index")),
        int_value(built.get("top_k")),
        str(context.get("row_key")),
    )


def leaf_support(context: dict[str, Any], leaf_index: int) -> dict[str, Any]:
    built = context["built"]
    components = context["components"]
    leaves = components.get("leaves") or []
    if leaf_index < 0 or leaf_index >= len(leaves):
        return {"priority_hits": [], "scout_positions": [], "term_support": []}
    scouts_by_pos = {
        int_value(scout.get("scout_pos")): scout
        for scout in built.get("scouts") or []
        if scout.get("scout_pos") is not None
    }
    support: set[int] = set()
    scout_positions = [int_value(pos) for pos in leaves[leaf_index].get("scout_positions") or []]
    for scout_pos in scout_positions:
        scout = scouts_by_pos.get(scout_pos)
        if scout:
            support.update(int_value(index) for index, _sign in scout.get("signed_terms") or [])
    return {"scout_positions": scout_positions, "term_support": sorted(support)}


def event_records_from_scan(row_key: str, scan: dict[str, Any], order: int, priority_columns: set[int]) -> list[dict[str, Any]]:
    return p694.relation_event_records([{"row_key": row_key, "_scan": scan}], order, priority_columns)


def compact_candidate(
    context: dict[str, Any],
    leaf_index: int,
    support: dict[str, Any],
    scan: dict[str, Any],
    events: list[dict[str, Any]],
    priority_columns: set[int],
    event_sample_limit: int,
) -> dict[str, Any]:
    built = context["built"]
    order = int_value(built.get("order"))
    endpoint_events = [
        event for event in events if event.get("term_priority_hits") or event.get("coeff_priority_hits")
    ]
    coeff_events = [event for event in events if event.get("coeff_priority_hits")]
    return {
        "direct_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "endpoint_coeff_event_count": len(coeff_events),
        "endpoint_event_count": len(endpoint_events),
        "endpoint_event_samples": [
            {
                "coeff_priority_hits": event.get("coeff_priority_hits") or [],
                "coeff_support": event.get("coeff_support") or [],
                "form_index": int_value(event.get("form_index")),
                "q_coeff": int_value(event.get("q_coeff")) % order,
                "rhs": int_value(event.get("rhs")) % order,
                "scout_pos": int_value(event.get("scout_pos")),
                "term_priority_hits": event.get("term_priority_hits") or [],
                "term_support": event.get("term_support") or [],
            }
            for event in endpoint_events[:event_sample_limit]
        ],
        "generic_rho_steps": int_value(built.get("generic_rho_steps")),
        "leaf_index": leaf_index,
        "priority_hits": sorted(set(support["term_support"]) & priority_columns),
        "relation_event_count": len(events),
        "relation_rank": int_value(scan.get("rank")),
        "relation_count": int_value(scan.get("relation_count")),
        "row_key": context.get("row_key"),
        "scout_positions": support["scout_positions"],
        "selected_hit_events": int_value(scan.get("selected_hit_events")),
        "selected_hit_roots": int_value(scan.get("selected_hit_roots")),
        "target": built.get("target"),
        "term_support": support["term_support"],
        "top_k": int_value(built.get("top_k")),
        "transfer_index": int_value(built.get("transfer_index")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["endpoint_coeff_event_count"]:
        return "P696_ENDPOINT_LEAF_MUTATION_EVENT_CANDIDATES_FOUND"
    if summary["endpoint_leaf_relation_event_count"]:
        return "P696_ENDPOINT_LEAVES_EMIT_ONLY_NONENDPOINT_EVENTS"
    return "NEGATIVE_RESULT_P696_ENDPOINT_LEAF_MUTATIONS_NO_RELATION_EVENTS"


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
    row_contexts: dict[tuple[str, int, int, str], dict[str, Any]] = {}
    missing_source_case_count = 0

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
        for row_context in p694.contexts_from_source_case(context, source_case):
            row_contexts.setdefault(row_context_key(row_context), row_context)

    endpoint_leaf_count = 0
    scanned_endpoint_leaf_count = 0
    endpoint_leaf_relation_event_count = 0
    endpoint_coeff_event_count = 0
    endpoint_event_count = 0
    relation_event_count = 0
    endpoint_leaf_hit_root_count = 0
    priority_leaf_counts: Counter[int] = Counter()
    priority_event_counts: Counter[int] = Counter()
    priority_coeff_counts: Counter[int] = Counter()
    leaf_index_counts: Counter[int] = Counter()
    event_support_shapes: Counter[str] = Counter()
    candidate_reports = []
    relation_reports = []

    for key, context in sorted(row_contexts.items()):
        leaves = context["components"].get("leaves") or []
        for leaf_index in range(len(leaves)):
            support = leaf_support(context, leaf_index)
            priority_hits = sorted(set(support["term_support"]) & priority_columns)
            if not priority_hits:
                continue
            endpoint_leaf_count += 1
            priority_leaf_counts.update(priority_hits)
            leaf_index_counts[leaf_index] += 1
            if args.max_endpoint_leaves > 0 and scanned_endpoint_leaf_count >= args.max_endpoint_leaves:
                continue
            scanned_endpoint_leaf_count += 1
            scan = direct_export.direct_witness_probe.scan_selected(
                verifier,
                context["built"],
                context["components"],
                {leaf_index},
                context["local_args"],
            )
            order = int_value(context["built"].get("order"))
            events = event_records_from_scan(str(context["row_key"]), scan, order, priority_columns)
            endpoint_events = [
                event for event in events if event.get("term_priority_hits") or event.get("coeff_priority_hits")
            ]
            coeff_events = [event for event in events if event.get("coeff_priority_hits")]
            relation_event_count += len(events)
            endpoint_event_count += len(endpoint_events)
            endpoint_coeff_event_count += len(coeff_events)
            if int_value(scan.get("selected_hit_roots")):
                endpoint_leaf_hit_root_count += 1
            if events:
                endpoint_leaf_relation_event_count += 1
                if len(relation_reports) < int_value(args.sample_limit, 12):
                    relation_reports.append(
                        compact_candidate(
                            context,
                            leaf_index,
                            support,
                            scan,
                            events,
                            priority_columns,
                            int_value(args.event_sample_limit, 6),
                        )
                    )
            if endpoint_events and len(candidate_reports) < int_value(args.sample_limit, 12):
                candidate_reports.append(
                    compact_candidate(
                        context,
                        leaf_index,
                        support,
                        scan,
                        events,
                        priority_columns,
                        int_value(args.event_sample_limit, 6),
                    )
                )
            for event in endpoint_events:
                priority_event_counts.update(event.get("term_priority_hits") or [])
                event_support_shapes[support_key(event.get("coeff_support") or [])] += 1
            for event in coeff_events:
                priority_coeff_counts.update(event.get("coeff_priority_hits") or [])

    summary = {
        "context_cache_entry_count": len(context_cache),
        "endpoint_coeff_event_count": endpoint_coeff_event_count,
        "endpoint_event_count": endpoint_event_count,
        "endpoint_leaf_count": endpoint_leaf_count,
        "endpoint_leaf_hit_root_count": endpoint_leaf_hit_root_count,
        "endpoint_leaf_relation_event_count": endpoint_leaf_relation_event_count,
        "missing_source_case_count": missing_source_case_count,
        "relation_event_count": relation_event_count,
        "row_context_count": len(row_contexts),
        "scanned_endpoint_leaf_count": scanned_endpoint_leaf_count,
    }
    summary.update(
        {
            "endpoint_event_support_shape_counts": dict(event_support_shapes.most_common(20)),
            "endpoint_leaf_index_counts": {
                str(key): leaf_index_counts[key] for key in sorted(leaf_index_counts)
            },
            "priority_columns": sorted(priority_columns),
            "priority_endpoint_coeff_event_counts": {
                str(column): priority_coeff_counts[column] for column in sorted(priority_columns)
            },
            "priority_endpoint_event_counts": {
                str(column): priority_event_counts[column] for column in sorted(priority_columns)
            },
            "priority_endpoint_leaf_counts": {
                str(column): priority_leaf_counts[column] for column in sorted(priority_columns)
            },
        }
    )
    claim_status = determine_claim(summary)
    return {
        "artifacts": {"product": str(product_path), "source": str(source_path)},
        "case_examples": {
            "endpoint_event_leaf_candidates": candidate_reports,
            "endpoint_leaves_with_any_relation_event": relation_reports,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: single-leaf mutation scans reuse reconstructed P658 row contexts.",
            "HEURISTIC: endpoint event candidates are generator-steering evidence, not target descent.",
            "NEGATIVE SCOPE: no candidates here rules out single-leaf endpoint mutations in current contexts, not multi-leaf or fresh-row generators.",
            "This is not a faster-than-Pollard-rho ECDLP algorithm.",
        ],
        "method": "p696_endpoint_leaf_mutation_scout",
        "parameters": {
            "event_sample_limit": int_value(args.event_sample_limit),
            "max_cases": int_value(args.max_cases),
            "max_endpoint_leaves": int_value(args.max_endpoint_leaves),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p696_endpoint_leaf_mutation_scout.v1",
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
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
