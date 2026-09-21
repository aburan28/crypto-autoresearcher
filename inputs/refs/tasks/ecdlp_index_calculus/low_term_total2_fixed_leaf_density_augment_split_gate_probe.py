#!/usr/bin/env python3
"""Augment target-aware split gates with a guarded density route for one target.

The target-aware selector chooses one product route per target.  That keeps the
route simple, but it can miss lower-cost density-only recoveries on targets whose
prior density route has no verified-above-rho history.  This probe freezes the
usual target-aware route map, then adds an extra public guard over density rows
for one augment target before applying the holdout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_guarded_target_aware_split_gate_probe as guarded
import low_term_total2_fixed_leaf_split_public_gate_summary_probe as split_summary
import low_term_total2_fixed_leaf_target_aware_split_gate_probe as target_aware


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
TARGET_DENSITY_ROUTE = "density_duplicate_ge_half_product_ge1"
STRICT_ROUTE = "strict_duplicate_ge5_product_ge1"


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def choose_augment_guard(
    guard_metrics: dict[str, Any],
    fallback_guard: str,
) -> dict[str, Any]:
    viable = [
        metric
        for metric in guard_metrics.values()
        if int_value(metric.get("below_rho_count")) > 0
        and int_value(metric.get("verified_above_rho_count")) == 0
    ]
    if not viable:
        return {
            "selected_guard": fallback_guard,
            "reason": "fallback guard because no candidate had prior below-rho evidence with zero verified-above-rho rows",
            "candidates": guard_metrics,
        }
    chosen = max(
        viable,
        key=lambda metric: (
            float(metric.get("selected_precision") or 0.0),
            int_value(metric.get("below_rho_window_count")),
            int_value(metric.get("below_rho_count")),
            -int_value(metric.get("false_positive_count")),
            -int_value(metric.get("selected_count")),
        ),
    )
    return {
        "selected_guard": chosen["guard_name"],
        "reason": (
            "prior-window augment guard precision among guards with below-rho "
            "support and zero verified-above-rho rows"
        ),
        "candidates": guard_metrics,
    }


def guarded_base_density_rows(
    density_product: dict[str, Any],
    target_routes: dict[str, Any],
    guard_target: str,
    guard_name: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    return guarded.guarded_density_cases(
        density_product,
        target_routes,
        guard_target,
        guard_name,
    )


def augment_density_rows(
    density_product: dict[str, Any],
    target_routes: dict[str, Any],
    augment_target: str,
    augment_guard_name: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    guard_fn = guarded.GUARDS[augment_guard_name]
    selected = []
    rejected = []
    for row in target_aware.selected_product_cases(density_product):
        target = str(row.get("target"))
        if target != augment_target:
            continue
        if (target_routes.get(target) or {}).get("selected_route") == TARGET_DENSITY_ROUTE:
            continue
        if not guard_fn(row):
            rejected.append(
                {
                    "target": target,
                    "transfer_index": int_value(row.get("transfer_index")),
                    "selector": guarded.selector(row),
                    "top_k": guarded.top_k(row),
                    "row_keys": row.get("row_keys") or [],
                }
            )
            continue
        selected.append(
            guarded.compact_guard_case(
                row,
                augment_guard_name,
                f"{TARGET_DENSITY_ROUTE}:augment:{augment_target}",
            )
        )
    return selected, {
        "guard_name": augment_guard_name,
        "augment_target": augment_target,
        "rejected_density_product_case_count": len(rejected),
        "rejected_density_product_cases": rejected[:24],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-strict-products", required=True)
    parser.add_argument("--train-density-products", required=True)
    parser.add_argument("--holdout-strict-product", type=Path, required=True)
    parser.add_argument("--holdout-density-product", type=Path, required=True)
    parser.add_argument("--holdout-low-prefix", type=Path, required=True)
    parser.add_argument("--augment-target", default="22050.cf1@11731")
    parser.add_argument("--guard-target", default="67.a1@9803")
    parser.add_argument("--fallback-route", default=STRICT_ROUTE)
    parser.add_argument("--fallback-guard", default="public_guard_charge_le2_root_saved_ge1")
    parser.add_argument(
        "--guard-score-mode",
        default="balanced_recall",
        choices=["precision_first", "balanced_recall"],
    )
    parser.add_argument(
        "--guard-candidates",
        default=",".join(guarded.GUARDS.keys()),
    )
    parser.add_argument(
        "--augment-guard-candidates",
        default=",".join(guarded.GUARDS.keys()),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_STATE_DIR
        / "low_term_total2_fixed_leaf_density_augment_split_gate_probe.json",
    )
    args = parser.parse_args()

    guard_names = [name.strip() for name in args.guard_candidates.split(",") if name.strip()]
    augment_guard_names = [
        name.strip() for name in args.augment_guard_candidates.split(",") if name.strip()
    ]
    unknown = [name for name in guard_names + augment_guard_names if name not in guarded.GUARDS]
    if unknown:
        raise ValueError(f"unknown guard candidates: {sorted(set(unknown))}")

    train_strict = target_aware.parse_labeled_paths(args.train_strict_products)
    train_density = target_aware.parse_labeled_paths(args.train_density_products)
    route_metrics = [
        target_aware.target_metrics(STRICT_ROUTE, train_strict),
        target_aware.target_metrics(TARGET_DENSITY_ROUTE, train_density),
    ]
    target_routes = target_aware.choose_target_routes(route_metrics, args.fallback_route)

    guard_metrics = guarded.evaluate_guards(guard_names, train_density, args.guard_target)
    guard_choice = guarded.choose_guard(
        guard_metrics,
        args.fallback_guard,
        args.guard_score_mode,
    )
    augment_guard_metrics = guarded.evaluate_guards(
        augment_guard_names,
        train_density,
        args.augment_target,
    )
    augment_guard_choice = choose_augment_guard(
        augment_guard_metrics,
        args.fallback_guard,
    )

    strict_product = target_aware.load_json(args.holdout_strict_product)
    density_product = target_aware.load_json(args.holdout_density_product)
    low_prefix = target_aware.load_json(args.holdout_low_prefix)
    strict_rows = target_aware.compact_cases_by_target(
        strict_product,
        STRICT_ROUTE,
        target_routes,
    )
    density_rows, guard_application = guarded_base_density_rows(
        density_product,
        target_routes,
        args.guard_target,
        guard_choice["selected_guard"],
    )
    augment_rows, augment_application = augment_density_rows(
        density_product,
        target_routes,
        args.augment_target,
        augment_guard_choice["selected_guard"],
    )
    low_rows = split_summary.selected_low_prefix_rows(low_prefix)
    rows = strict_rows + density_rows + augment_rows + low_rows
    summary = split_summary.summarize(rows)
    summary["guarded_density_rejected_count"] = guard_application[
        "rejected_density_product_case_count"
    ]
    summary["augment_density_selected_count"] = len(augment_rows)
    summary["augment_density_rejected_count"] = augment_application[
        "rejected_density_product_case_count"
    ]

    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_density_augment_split_gate.v1",
        "method": "target_aware_split_with_guarded_density_augment",
        "training_routes": route_metrics,
        "target_routes": target_routes,
        "guard_choice": guard_choice,
        "augment_guard_choice": augment_guard_choice,
        "guard_application": guard_application,
        "augment_application": augment_application,
        "holdout_sources": {
            "strict_product": str(args.holdout_strict_product),
            "density_product": str(args.holdout_density_product),
            "low_prefix": str(args.holdout_low_prefix),
        },
        "summary": summary,
        "selected_cases": rows,
        "honesty_boundary": [
            "This is a post-P243 diagnostic augment, not the original precision-first guard.",
            "Route choices and guard choices are frozen from prior-window public product metadata before holdout application.",
            "The augment guard uses public selector/top-k and selected-leaf sharing metrics only.",
            "Verifier rank, derived secret, and below-rho status are measured only after selection.",
            "This is controlled toy-prime evidence, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "target_routes": target_routes,
                "guard_choice": {
                    "selected_guard": guard_choice.get("selected_guard"),
                    "score_mode": args.guard_score_mode,
                },
                "augment_guard_choice": {
                    "selected_guard": augment_guard_choice.get("selected_guard"),
                    "reason": augment_guard_choice.get("reason"),
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
