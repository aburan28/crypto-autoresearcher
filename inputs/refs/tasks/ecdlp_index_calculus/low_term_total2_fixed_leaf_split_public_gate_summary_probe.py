#!/usr/bin/env python3
"""Combine split public gates for fixed-leaf two-row ECDLP probes."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_PRODUCT = DEFAULT_STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_1176_1183_probe.json"
DEFAULT_LOW_PREFIX = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_1176_1183_probe.json"
)
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_fixed_leaf_split_public_gate_1176_1183_probe.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio_value(value: Any) -> float:
    try:
        if value is None:
            return 10**18
        return float(value)
    except (TypeError, ValueError):
        return 10**18


def case_key(row: dict[str, Any]) -> str:
    row_keys = row.get("row_keys") or []
    return json.dumps(
        [
            row.get("target"),
            int_value(row.get("transfer_index")),
            row.get("selector"),
            int_value(row.get("top_k")),
            sorted(str(key) for key in row_keys),
        ],
        sort_keys=True,
    )


def solution_key(row: dict[str, Any]) -> str:
    """Group repeated top-k/selector variants for the same recovered row-pair."""
    row_keys = row.get("row_keys") or []
    return json.dumps(
        [
            row.get("target"),
            int_value(row.get("transfer_index")),
            sorted(str(key) for key in row_keys),
            row.get("derived_secret"),
        ],
        sort_keys=True,
    )


def best_by_solution(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(solution_key(row), []).append(row)
    best = []
    for variants in groups.values():
        chosen = min(
            variants,
            key=lambda row: (
                ratio_value(row.get("ops_over_rho")),
                str(row.get("route")),
                str(row.get("selector")),
                int_value(row.get("top_k")),
            ),
        )
        best.append({**chosen, "compressed_variant_count": len(variants)})
    return sorted(
        best,
        key=lambda row: (
            ratio_value(row.get("ops_over_rho")),
            str(row.get("route")),
            str(row.get("target")),
            int_value(row.get("transfer_index")),
        ),
    )


def compact_product_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "route": "duplicate_signature_shared_product",
        "target": row.get("target"),
        "transfer_index": int_value(row.get("transfer_index")),
        "selector": row.get("selector"),
        "top_k": int_value(row.get("top_k")),
        "row_keys": row.get("row_keys") or [],
        "ops_over_rho": row.get("shared_product_ledger_ops_over_rho"),
        "direct_ops_over_rho": row.get("direct_verifier_replay_ops_over_rho"),
        "public_key_verified": bool(row.get("shared_product_union_public_key_verified")),
        "beats_rho": bool(row.get("shared_product_ledger_beats_rho")),
        "rank": int_value(row.get("shared_product_union_rank")),
        "relation_count": int_value(row.get("shared_product_union_relation_count")),
        "derived_secret": row.get("shared_product_union_derived_secret"),
        "public_features": row.get("gate_metrics") or {},
    }


def compact_low_prefix_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "route": "low_prefix_direct",
        "target": row.get("target"),
        "transfer_index": int_value(row.get("transfer_index")),
        "selector": row.get("selector"),
        "top_k": int_value(row.get("top_k")),
        "row_keys": row.get("row_keys") or [],
        "ops_over_rho": row.get("direct_verifier_replay_ops_over_rho"),
        "public_key_verified": bool(row.get("direct_union_public_key_verified")),
        "beats_rho": bool(row.get("direct_below_rho")),
        "rank": int_value(row.get("direct_union_rank")),
        "relation_count": int_value(row.get("direct_union_relation_count")),
        "derived_secret": row.get("direct_union_derived_secret"),
        "public_features": row.get("public_features") or {},
    }


def selected_product_rows(product: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        compact_product_case(row)
        for row in (product.get("cases") or [])
        if row.get("public_product_gate_selected")
    ]


def selected_low_prefix_rows(low_prefix: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        compact_low_prefix_case(row)
        for row in (low_prefix.get("cases") or [])
        if row.get("public_low_prefix_gate_selected")
    ]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [row for row in rows if row.get("public_key_verified")]
    below = [row for row in verified if row.get("beats_rho")]
    verified_above = [row for row in verified if not row.get("beats_rho")]
    unique_keys = {case_key(row) for row in rows}
    distinct_verified = best_by_solution(verified)
    distinct_below = best_by_solution(below)
    distinct_verified_above = best_by_solution(verified_above)
    best = sorted(
        below,
        key=lambda row: (
            ratio_value(row.get("ops_over_rho")),
            str(row.get("route")),
            str(row.get("target")),
            int_value(row.get("transfer_index")),
        ),
    )[:10]
    return {
        "selected_route_case_count": len(rows),
        "selected_unique_case_count": len(unique_keys),
        "selected_route_counts": dict(Counter(str(row.get("route")) for row in rows).most_common()),
        "selected_target_counts": dict(Counter(str(row.get("target")) for row in rows).most_common()),
        "selected_verified_count": len(verified),
        "selected_verified_target_counts": dict(
            Counter(str(row.get("target")) for row in verified).most_common()
        ),
        "selected_below_rho_count": len(below),
        "selected_below_rho_target_counts": dict(
            Counter(str(row.get("target")) for row in below).most_common()
        ),
        "selected_below_rho_route_counts": dict(
            Counter(str(row.get("route")) for row in below).most_common()
        ),
        "selected_unverified_count": len(rows) - len(verified),
        "selected_verified_above_rho_count": len(verified_above),
        "selected_distinct_verified_solution_count": len(distinct_verified),
        "selected_distinct_below_rho_solution_count": len(distinct_below),
        "selected_distinct_below_rho_solution_target_counts": dict(
            Counter(str(row.get("target")) for row in distinct_below).most_common()
        ),
        "selected_distinct_below_rho_solution_route_counts": dict(
            Counter(str(row.get("route")) for row in distinct_below).most_common()
        ),
        "selected_distinct_verified_above_rho_solution_count": len(distinct_verified_above),
        "selected_compressed_verified_variant_count": len(verified) - len(distinct_verified),
        "selected_compressed_below_rho_variant_count": len(below) - len(distinct_below),
        "best_selected_below_rho_cases": best,
        "best_distinct_below_rho_solutions": distinct_below[:10],
        "claim_status": (
            "SPLIT_PUBLIC_GATE_POSITIVE" if below else "SPLIT_PUBLIC_GATE_NO_BELOW_RHO_SELECTED_CASE"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--product", type=Path, default=DEFAULT_PRODUCT)
    parser.add_argument("--low-prefix", type=Path, default=DEFAULT_LOW_PREFIX)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    product = load_json(args.product)
    low_prefix = load_json(args.low_prefix)
    rows = selected_product_rows(product) + selected_low_prefix_rows(low_prefix)
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_split_public_gate_summary.v1",
        "method": "split_public_gate_summary",
        "sources": {
            "product": str(args.product),
            "low_prefix": str(args.low_prefix),
        },
        "summary": summarize(rows),
        "selected_cases": rows,
        "honesty_boundary": [
            "This combines two already-public gates and preserves route labels.",
            "Shared-product rows use operation-ledger rho comparisons; low-prefix rows use direct verifier replay cost.",
            "Verifier rank, derived secret, and below-rho status are post-gate measurements.",
            "This is controlled toy-prime evidence, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
