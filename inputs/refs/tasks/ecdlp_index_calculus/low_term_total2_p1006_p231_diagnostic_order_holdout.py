#!/usr/bin/env python3
"""P1006 holdout test for P1005 diagnostic public early-stop orders."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1006_p231_diagnostic_order_holdout_11976_11983.md"
DEFAULT_P1005 = STATE_DIR / "low_term_total2_p1005_p231_context_safe_early_stop_order_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1006_p231_diagnostic_order_holdout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1006_p231_diagnostic_order_holdout.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_HOLDOUT_WINDOW = "11976_11983"
PRIMARY_ORDER = "gap_desc_salt_topk"
SECONDARY_ORDERS = ["leaf89_first_gap_desc", "salt_topk_transfer"]
CONTROL_ORDERS = ["gap_asc_salt_topk", "p996_public_order"]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def expanded_source_path(window: str) -> Path:
    return STATE_DIR / f"frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_col15_selector_expanded_probe.json"


def install_source_fallback() -> None:
    original_source_path = p1005.p998.p868.source_path

    def source_path_with_expanded_fallback(window: str) -> Path:
        base = original_source_path(window)
        if base.exists():
            return base
        expanded = expanded_source_path(window)
        if expanded.exists():
            return expanded
        return base

    p1005.p998.p868.source_path = source_path_with_expanded_fallback
    p1005.p998.p993.p868.source_path = source_path_with_expanded_fallback


def resolved_source(window: str) -> dict[str, Any]:
    base = STATE_DIR / f"frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_probe.json"
    expanded = expanded_source_path(window)
    if base.exists():
        return {"exists": True, "path": str(base), "source_variant": "unsuffixed"}
    if expanded.exists():
        return {"exists": True, "path": str(expanded), "source_variant": "col15_selector_expanded"}
    return {"exists": False, "path": str(base), "source_variant": "missing"}


def source_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"source_exists": False}
    payload = load_json(path)
    summaries = ((payload.get("summary") or {}).get("policy_summaries") or [])
    fixed = next((row for row in summaries if row.get("policy") == "fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1"), summaries[0] if summaries else {})
    return {
        "source_exists": True,
        "stress_leaf_below_rho": fixed.get("stress_leaf_below_rho"),
        "stress_leaf_best_ops_over_rho": fixed.get("stress_leaf_best_ops_over_rho"),
        "stress_leaf_verified": fixed.get("stress_leaf_verified"),
        "stress_row_below_rho": fixed.get("stress_row_below_rho"),
        "stress_row_verified": fixed.get("stress_row_verified"),
    }


def compact_first(summary: dict[str, Any]) -> dict[str, Any] | None:
    first = summary.get("first_scalar_valid_group")
    if not first:
        return None
    return {
        "charged_ops_over_rho": first.get("charged_ops_over_rho"),
        "derived_secret": first.get("derived_secret"),
        "direct_group_amortized_ops_over_rho": first.get("direct_group_amortized_ops_over_rho"),
        "group_case_ids": first.get("group_case_ids"),
        "group_key": first.get("group_key"),
        "group_type": first.get("group_type"),
        "ordered_index": first.get("ordered_index"),
        "public_fingerprint": first.get("public_fingerprint"),
        "row_keys": first.get("row_keys"),
    }


def order_by_name() -> dict[str, dict[str, Any]]:
    return {order["name"]: order for order in p1005.order_candidates()}


def summarize_orders(selected: list[dict[str, Any]], groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted = [PRIMARY_ORDER, *SECONDARY_ORDERS, *CONTROL_ORDERS]
    by_name = order_by_name()
    summaries = []
    for name in wanted:
        order = by_name[name]
        summary = p1005.first_hit_summary(selected, groups, order)
        summaries.append(
            {
                "first_scalar_valid_group": compact_first(summary),
                "first_scalar_valid_group_below_rho": summary.get("first_scalar_valid_group_below_rho"),
                "order_description": summary.get("order_description"),
                "order_name": name,
                "order_role": (
                    "primary"
                    if name == PRIMARY_ORDER
                    else "secondary"
                    if name in SECONDARY_ORDERS
                    else "control"
                ),
                "scalar_valid_group_count": summary.get("scalar_valid_group_count"),
                "total_selected_ops_over_rho": summary.get("total_selected_ops_over_rho"),
            }
        )
    return summaries


def coverage_diagnostic(examples: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [p1005.p998.score_rule(rule, examples) for rule in p1005.p998.candidate_rules()]
    scored.sort(
        key=lambda row: (
            -int(float(row.get("precision") or 0.0) == 1.0),
            -float(row.get("recall") or 0.0),
            float(row.get("useful_amortized_ops_over_rho") or 10**9),
            p1005.int_value(row.get("selected_count"), 10**9),
            str(row.get("name")),
        )
    )
    leaf_selectors = Counter(str((row.get("features") or {}).get("leaf_selector")) for row in examples)
    top_ks = Counter(str((row.get("features") or {}).get("top_k")) for row in examples)
    leaf_tuples = Counter(str(tuple((row.get("features") or {}).get("unique_leaf_indices") or [])) for row in examples)
    return {
        "example_count": len(examples),
        "leaf_selector_histogram": dict(leaf_selectors.most_common()),
        "p998_candidate_rules_top12": scored[:12],
        "source_positive_count": sum(1 for row in examples if row.get("label_positive")),
        "source_public_key_verified_count": sum(
            1 for row in examples if (row.get("source_case") or {}).get("source_public_key_verified")
        ),
        "top_k_histogram": dict(top_ks.most_common()),
        "unique_leaf_tuple_top10": dict(leaf_tuples.most_common(10)),
    }


def determine_claim(control_pass: bool, source_exists: bool, selected_count: int, scalar_group_count: int, orders: list[dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1006_P1005_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P1006_SOURCE_WINDOW_MISSING"
    if selected_count == 0:
        return "NEGATIVE_RESULT_P1006_BRANCH_SELECTS_NO_ROWS"
    if scalar_group_count == 0:
        return "NEGATIVE_RESULT_P1006_NO_CONTEXT_SAFE_SCALAR_VALID_GROUP"
    primary = next(row for row in orders if row["order_name"] == PRIMARY_ORDER)
    primary_first = primary.get("first_scalar_valid_group")
    if primary.get("first_scalar_valid_group_below_rho"):
        return "P1006_GAP_DESC_HOLDOUT_BELOW_RHO"
    secondary_hit = any(
        row.get("first_scalar_valid_group_below_rho") for row in orders if row.get("order_role") == "secondary"
    )
    if secondary_hit:
        return "P1006_SECONDARY_FROZEN_ORDER_HOLDOUT_BELOW_RHO"
    if primary_first:
        return "NEGATIVE_RESULT_P1006_FROZEN_ORDERS_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1006_FROZEN_ORDERS_NO_HIT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    install_source_fallback()
    p1005_payload = load_json(Path(args.p1005))
    control_pass = p1005_payload.get("claim_status") == "NEGATIVE_RESULT_P1005_TRAINED_PUBLIC_ORDER_ABOVE_RHO"
    source = resolved_source(args.window)
    selected: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {"lane": f"p998_branch_{args.window}", "window": args.window}
    lane: dict[str, Any] = {}
    groups: list[dict[str, Any]] = []
    orders: list[dict[str, Any]] = []
    coverage: dict[str, Any] = {}
    if source["exists"]:
        examples = p1005.p998.build_window_examples(args.window, args.targets, args.min_source_rank)
        coverage = coverage_diagnostic(examples)
        selected, metadata = p1005.p998_selected(args.window, args.targets, args.min_source_rank)
        lane, groups = p1005.scalar_valid_groups(selected, metadata, args.baseline_rank)
        orders = summarize_orders(selected, groups)
    claim = determine_claim(control_pass, bool(source["exists"]), len(selected), len(groups), orders)
    primary = next((row for row in orders if row.get("order_name") == PRIMARY_ORDER), {})
    best_frozen = [
        row
        for row in orders
        if row.get("order_role") in {"primary", "secondary"} and row.get("first_scalar_valid_group") is not None
    ]
    best_frozen.sort(
        key=lambda row: (
            not row.get("first_scalar_valid_group_below_rho"),
            (row.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho", 10**9),
            row.get("order_name"),
        )
    )
    source_path = Path(str(source["path"]))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1005_source": str(args.p1005),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1005_source_sha256": p1005.sha256_file(Path(args.p1005)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": p1005.sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1006_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "HOLDOUT BOUNDARY: P1005 diagnostics are treated as training priors; P1006 scores only 11976_11983.",
            "SOURCE-VARIANT BOUNDARY: if the unsuffixed source is absent, the existing col15_selector_expanded source is used and reported.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "FULL-ALGORITHM BOUNDARY: early scalar-valid hit is not full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p1006_p231_diagnostic_order_holdout",
        "order_results": orders,
        "p998_coverage_diagnostic": coverage,
        "p1005_control": {
            "claim_status": p1005_payload.get("claim_status"),
            "summary": p1005_payload.get("summary"),
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "control_orders": CONTROL_ORDERS,
            "min_source_rank": args.min_source_rank,
            "primary_order": PRIMARY_ORDER,
            "secondary_orders": SECONDARY_ORDERS,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "schema": SCHEMA,
        "source": {
            **source,
            "summary": source_summary(source_path),
        },
        "summary": {
            "best_frozen_order": best_frozen[0].get("order_name") if best_frozen else None,
            "best_frozen_order_charge": (
                (best_frozen[0].get("first_scalar_valid_group") or {}).get("charged_ops_over_rho")
                if best_frozen
                else None
            ),
            "claim_status": claim,
            "control_pass": control_pass,
            "primary_first_charge": (primary.get("first_scalar_valid_group") or {}).get("charged_ops_over_rho"),
            "primary_first_index": (primary.get("first_scalar_valid_group") or {}).get("ordered_index"),
            "primary_order_below_rho": primary.get("first_scalar_valid_group_below_rho"),
            "source_example_count": coverage.get("example_count"),
            "source_positive_count": coverage.get("source_positive_count"),
            "source_public_key_verified_count": coverage.get("source_public_key_verified_count"),
            "selected_count": len(selected),
            "source_exists": source["exists"],
            "source_variant": source["source_variant"],
            "total_selected_ops_over_rho": orders[0].get("total_selected_ops_over_rho") if orders else None,
            "validation_scalar_valid_group_count": len(groups),
        },
        "validation": {
            "analysis_summary": lane.get("summary"),
            "metadata": metadata,
            "scalar_valid_groups": [p1005.compact_group(group) for group in groups[:16]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1006 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1005", default=str(DEFAULT_P1005), help="P1005 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_HOLDOUT_WINDOW, help="Holdout window")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} source={source_variant} selected={selected} scalar_groups={groups} "
        "primary_charge={primary_charge} primary_index={primary_index} best_frozen={best} "
        "best_charge={best_charge} out={out}".format(
            claim=payload["claim_status"],
            source_variant=summary["source_variant"],
            selected=summary["selected_count"],
            groups=summary["validation_scalar_valid_group_count"],
            primary_charge=summary["primary_first_charge"],
            primary_index=summary["primary_first_index"],
            best=summary["best_frozen_order"],
            best_charge=summary["best_frozen_order_charge"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
