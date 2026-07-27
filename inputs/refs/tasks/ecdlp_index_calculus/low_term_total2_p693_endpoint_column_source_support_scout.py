#!/usr/bin/env python3
"""P693 endpoint-column selected-term support scout for order-9887 rows.

P691/P692 found that the current order-9887 factor bank has a two-column
deficiency on factor columns 0 and 15, and that current certificates never
export those columns into public forms.  This scout looks one step earlier:
for product/source cases, replay selected contexts once per row/transfer cache
key and record whether the selected leaf scouts even see the priority factor
columns before public relation forms are exported.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = (
    STATE_DIR
    / "low_term_total2_order9887_p658_phase3_right207_salt207_postquiet_source_22330_22342_probe.json"
)
DEFAULT_PRODUCT = (
    STATE_DIR
    / "low_term_total2_fixed_leaf_shared_product_gate_p658_order9887_phase3_right207_salt207_postquiet_22330_22342_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p693_endpoint_column_source_support_scout_probe.json"


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


def parse_columns(raw: str) -> set[int]:
    return {int(part.strip()) for part in raw.split(",") if part.strip()}


def bool_field(row: dict[str, Any], *keys: str) -> bool:
    return any(row.get(key) is True for key in keys)


def exact_case_key(row: dict[str, Any]) -> tuple[str, int, str, int]:
    return (
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        str(row.get("selector")),
        int_value(row.get("top_k")),
    )


def source_case_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for offset, row in enumerate(result.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            rows.append(
                {
                    **row,
                    "_source_policy": str(policy_name),
                    "_source_policy_offset": offset,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    return rows


def build_source_index(source: dict[str, Any]) -> dict[tuple[str, int, str, int], dict[str, Any]]:
    by_key: dict[tuple[str, int, str, int], list[dict[str, Any]]] = {}
    for row in source_case_rows(source):
        by_key.setdefault(exact_case_key(row), []).append(row)
    out: dict[tuple[str, int, str, int], dict[str, Any]] = {}
    for key, rows in by_key.items():
        rows.sort(
            key=lambda row: (
                not bool(row.get("public_key_verified")),
                not bool(row.get("source_verified")),
                float(row.get("ops_over_rho") or 10**18),
                str(row.get("_source_policy")),
            )
        )
        out[key] = rows[0]
    return out


def product_cases(product: dict[str, Any], target: str, max_cases: int) -> list[dict[str, Any]]:
    rows = [
        row
        for row in product.get("cases") or []
        if isinstance(row, dict) and (not target or str(row.get("target")) == target)
    ]
    if max_cases > 0:
        rows = rows[:max_cases]
    return rows


def selected_term_support_from_context(context: dict[str, Any], source_case: dict[str, Any]) -> list[int]:
    support: set[int] = set()
    for item in hit_stream_probe.unique_row_leaf_keys(source_case):
        row_key = str(item.get("row_key") or "")
        built = context.get("built_by_row", {}).get(row_key)
        components = context.get("components_by_row", {}).get(row_key)
        if not isinstance(built, dict):
            continue
        if not isinstance(components, dict):
            continue
        scouts_by_pos = {
            int_value(scout.get("scout_pos")): scout
            for scout in built.get("scouts") or []
            if scout.get("scout_pos") is not None
        }
        leaves = components.get("leaves") or []
        for leaf_index in {int_value(leaf) for leaf in item.get("leaf_indices") or []}:
            if leaf_index < 0 or leaf_index >= len(leaves):
                continue
            for scout_pos in leaves[leaf_index].get("scout_positions") or []:
                scout = scouts_by_pos.get(int_value(scout_pos))
                if scout:
                    support.update(int_value(index) for index, _sign in scout.get("signed_terms") or [])
    return sorted(support)


def selected_leaf_indices(source_case: dict[str, Any]) -> list[int]:
    indices: set[int] = set()
    for item in hit_stream_probe.unique_row_leaf_keys(source_case):
        indices.update(int_value(leaf) for leaf in item.get("leaf_indices") or [])
    return sorted(indices)


def compact_case_report(
    product_case: dict[str, Any],
    source_case: dict[str, Any],
    support: list[int],
    priority_columns: set[int],
) -> dict[str, Any]:
    priority_hits = sorted(set(support) & priority_columns)
    direct_verified = bool_field(product_case, "direct_union_public_key_verified", "direct_public_key_verified")
    shared_verified = bool_field(
        product_case,
        "shared_product_union_public_key_verified",
        "shared_product_public_key_verified",
    )
    return {
        "direct_below_rho": bool(product_case.get("direct_below_rho")),
        "direct_ops_over_rho": product_case.get("direct_verifier_replay_ops_over_rho")
        or product_case.get("direct_ops_over_rho"),
        "direct_public_key_verified": direct_verified,
        "priority_hits": priority_hits,
        "public_product_gate_selected": bool(product_case.get("public_product_gate_selected")),
        "row_keys": product_case.get("row_keys") or source_case.get("row_keys") or [],
        "selected_leaf_indices": selected_leaf_indices(source_case),
        "selected_term_support": support,
        "selector": product_case.get("selector"),
        "shared_product_ops_over_rho": product_case.get("shared_product_ledger_ops_over_rho")
        or product_case.get("shared_product_ops_over_rho"),
        "shared_product_public_key_verified": shared_verified,
        "source_policy": source_case.get("_source_policy"),
        "source_verified": bool(source_case.get("source_verified")),
        "target": product_case.get("target"),
        "top_k": int_value(product_case.get("top_k")),
        "transfer_index": int_value(product_case.get("transfer_index")),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["direct_verified_priority_hit_count"]:
        return "P693_ENDPOINT_COLUMNS_VISIBLE_IN_DIRECT_VERIFIED_SELECTED_TERMS_NEED_FORM_EXPORT"
    if summary["priority_hit_count"]:
        return "P693_ENDPOINT_COLUMNS_VISIBLE_IN_SELECTED_TERMS_NEED_VERIFIER_ROUTE"
    return "NEGATIVE_RESULT_P693_ENDPOINT_COLUMNS_NOT_VISIBLE_IN_SELECTED_TERMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.source)
    product_path = Path(args.product)
    source = load_json(source_path)
    product = load_json(product_path)
    priority_columns = parse_columns(args.priority_columns)
    source_index = build_source_index(source)

    params = repair_probe.source_parameters(source)
    probe_args = repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}

    reports = []
    missing_source_cases = []
    support_counts: Counter[int] = Counter()
    priority_column_counts: Counter[int] = Counter()
    priority_direct_verified_counts: Counter[int] = Counter()
    selected_leaf_counts: Counter[int] = Counter()

    for product_case in product_cases(product, args.target, int_value(args.max_cases)):
        key = exact_case_key(product_case)
        source_case = source_index.get(key)
        if source_case is None:
            missing_source_cases.append(
                {
                    "selector": product_case.get("selector"),
                    "target": product_case.get("target"),
                    "top_k": int_value(product_case.get("top_k")),
                    "transfer_index": int_value(product_case.get("transfer_index")),
                }
            )
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
        support = selected_term_support_from_context(context, source_case)
        report = compact_case_report(product_case, source_case, support, priority_columns)
        reports.append(report)
        support_counts.update(support)
        selected_leaf_counts.update(report["selected_leaf_indices"])
        for column in report["priority_hits"]:
            priority_column_counts[column] += 1
            if report["direct_public_key_verified"]:
                priority_direct_verified_counts[column] += 1

    priority_reports = [row for row in reports if row["priority_hits"]]
    direct_verified_priority_reports = [
        row for row in priority_reports if row["direct_public_key_verified"]
    ]
    direct_below_rho_priority_reports = [
        row for row in priority_reports if row["direct_below_rho"]
    ]
    gate_selected_priority_reports = [
        row for row in priority_reports if row["public_product_gate_selected"]
    ]
    shared_verified_priority_reports = [
        row for row in priority_reports if row["shared_product_public_key_verified"]
    ]
    summary = {
        "case_count": len(reports),
        "context_cache_entry_count": len(context_cache),
        "direct_below_rho_priority_hit_count": len(direct_below_rho_priority_reports),
        "direct_verified_priority_hit_count": len(direct_verified_priority_reports),
        "gate_selected_priority_hit_count": len(gate_selected_priority_reports),
        "missing_source_case_count": len(missing_source_cases),
        "priority_column_counts": {
            str(column): priority_column_counts[column] for column in sorted(priority_columns)
        },
        "priority_direct_verified_column_counts": {
            str(column): priority_direct_verified_counts[column] for column in sorted(priority_columns)
        },
        "priority_hit_count": len(priority_reports),
        "selected_leaf_index_counts": {
            str(key): selected_leaf_counts[key] for key in sorted(selected_leaf_counts)
        },
        "shared_verified_priority_hit_count": len(shared_verified_priority_reports),
        "support_counts": {str(key): support_counts[key] for key in sorted(support_counts)},
    }
    claim_status = determine_claim(summary)
    sample_limit = max(0, int_value(args.sample_limit, 12))
    return {
        "artifacts": {
            "product": str(product_path),
            "source": str(source_path),
        },
        "case_examples": {
            "direct_verified_priority_hits": direct_verified_priority_reports[:sample_limit],
            "gate_selected_priority_hits": gate_selected_priority_reports[:sample_limit],
            "priority_hits": priority_reports[:sample_limit],
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: selected-term support is upstream generator evidence, not a public relation certificate.",
            "HEURISTIC: endpoint-column visibility can guide an index-calculus relation generator, but does not prove target descent or a below-rho algorithm.",
            "OPEN: any priority hit must still pass public relation-form export, target elimination, rank, and individual-log descent gates.",
            "This is not a faster-than-Pollard-rho ECDLP algorithm.",
        ],
        "method": "p693_endpoint_column_selected_term_support_scout",
        "missing_source_cases": missing_source_cases[:sample_limit],
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p693_endpoint_column_source_support_scout.v1",
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
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
