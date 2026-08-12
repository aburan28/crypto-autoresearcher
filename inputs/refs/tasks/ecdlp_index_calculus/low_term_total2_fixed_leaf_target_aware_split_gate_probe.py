#!/usr/bin/env python3
"""Target-aware split product gate for fixed-leaf two-row probes.

This is a follow-up to the global split selector.  The global selector freezes
the lower-noise strict product route, but the 1184..1191 density control exposes
a target-diversity rescue on `67.a1@9803`.  This probe uses prior-window
target-specific product metrics to choose a product route per target, then
combines those selected product rows with the already-public low-prefix route.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_split_public_gate_summary_probe as split_summary


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_fixed_leaf_target_aware_split_gate_1184_1191_diagnostic_probe.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float:
    if not denominator:
        return 0.0
    return round(float(numerator) / float(denominator), 8)


def parse_labeled_paths(raw: str) -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" in chunk:
            label, path = chunk.split("=", 1)
            out.append((label.strip(), Path(path.strip())))
        else:
            path = Path(chunk)
            out.append((path.stem, path))
    return out


def selected_product_cases(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        row
        for row in (artifact.get("cases") or [])
        if row.get("public_product_gate_selected")
    ]


def target_metrics(route: str, labeled_paths: list[tuple[str, Path]]) -> dict[str, Any]:
    by_target: dict[str, dict[str, Any]] = {}
    windows = []
    for label, path in labeled_paths:
        artifact = load_json(path)
        cases = selected_product_cases(artifact)
        window_targets = {}
        for row in cases:
            target = str(row.get("target"))
            metric = by_target.setdefault(
                target,
                {
                    "target": target,
                    "route": route,
                    "selected_count": 0,
                    "verified_count": 0,
                    "below_rho_count": 0,
                    "false_positive_count": 0,
                    "verified_above_rho_count": 0,
                },
            )
            window_metric = window_targets.setdefault(
                target,
                {
                    "target": target,
                    "selected_count": 0,
                    "verified_count": 0,
                    "below_rho_count": 0,
                    "false_positive_count": 0,
                    "verified_above_rho_count": 0,
                },
            )
            verified = bool(row.get("shared_product_union_public_key_verified"))
            below = bool(verified and row.get("shared_product_ledger_beats_rho"))
            metric["selected_count"] += 1
            window_metric["selected_count"] += 1
            if verified:
                metric["verified_count"] += 1
                window_metric["verified_count"] += 1
                if below:
                    metric["below_rho_count"] += 1
                    window_metric["below_rho_count"] += 1
                else:
                    metric["verified_above_rho_count"] += 1
                    window_metric["verified_above_rho_count"] += 1
            else:
                metric["false_positive_count"] += 1
                window_metric["false_positive_count"] += 1
        windows.append(
            {
                "label": label,
                "path": str(path),
                "targets": {
                    target: finalize_metric(metric)
                    for target, metric in sorted(window_targets.items())
                },
            }
        )
    return {
        "route": route,
        "windows": windows,
        "targets": {
            target: finalize_metric(metric)
            for target, metric in sorted(by_target.items())
        },
    }


def finalize_metric(metric: dict[str, Any]) -> dict[str, Any]:
    selected = int_value(metric.get("selected_count"))
    verified = int_value(metric.get("verified_count"))
    below = int_value(metric.get("below_rho_count"))
    false_positive = int_value(metric.get("false_positive_count"))
    verified_above = int_value(metric.get("verified_above_rho_count"))
    return {
        **metric,
        "selected_precision": ratio(below, selected),
        "verified_success_rate": ratio(below, verified),
        "noise_per_below_rho": ratio(false_positive + verified_above, below),
        "score_tuple": [
            ratio(below, selected),
            -ratio(false_positive + verified_above, below),
            ratio(below, verified),
            below,
            -selected,
        ],
    }


def choose_target_routes(route_metrics: list[dict[str, Any]], fallback_route: str) -> dict[str, Any]:
    targets = sorted(
        {
            target
            for route in route_metrics
            for target in (route.get("targets") or {}).keys()
        }
    )
    choices = {}
    for target in targets:
        candidates = []
        for route in route_metrics:
            metric = (route.get("targets") or {}).get(target)
            if not metric:
                continue
            candidates.append(metric)
        viable = [row for row in candidates if int_value(row.get("below_rho_count")) > 0]
        if viable:
            chosen = max(
                viable,
                key=lambda row: (
                    float(row.get("selected_precision") or 0.0),
                    -float(row.get("noise_per_below_rho") or 10**9),
                    float(row.get("verified_success_rate") or 0.0),
                    int_value(row.get("below_rho_count")),
                    -int_value(row.get("selected_count")),
                ),
            )
        else:
            chosen = next(
                (row for row in candidates if row.get("route") == fallback_route),
                candidates[0] if candidates else {},
            )
        choices[target] = {
            "selected_route": chosen.get("route"),
            "reason": (
                "target-specific prior selected precision among routes with "
                "below-rho evidence; fallback to global route if no target route "
                "had prior below-rho evidence"
            ),
            "candidates": candidates,
        }
    return choices


def compact_cases_by_target(product: dict[str, Any], route: str, target_routes: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in selected_product_cases(product):
        target = str(row.get("target"))
        if (target_routes.get(target) or {}).get("selected_route") != route:
            continue
        rows.append(split_summary.compact_product_case(row))
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return split_summary.summarize(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-strict-products", required=True)
    parser.add_argument("--train-density-products", required=True)
    parser.add_argument("--holdout-strict-product", type=Path, required=True)
    parser.add_argument("--holdout-density-product", type=Path, required=True)
    parser.add_argument("--holdout-low-prefix", type=Path, required=True)
    parser.add_argument("--fallback-route", default="strict_duplicate_ge5_product_ge1")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    route_metrics = [
        target_metrics(
            "strict_duplicate_ge5_product_ge1",
            parse_labeled_paths(args.train_strict_products),
        ),
        target_metrics(
            "density_duplicate_ge_half_product_ge1",
            parse_labeled_paths(args.train_density_products),
        ),
    ]
    target_routes = choose_target_routes(route_metrics, args.fallback_route)
    strict_product = load_json(args.holdout_strict_product)
    density_product = load_json(args.holdout_density_product)
    low_prefix = load_json(args.holdout_low_prefix)
    rows = (
        compact_cases_by_target(strict_product, "strict_duplicate_ge5_product_ge1", target_routes)
        + compact_cases_by_target(density_product, "density_duplicate_ge_half_product_ge1", target_routes)
        + split_summary.selected_low_prefix_rows(low_prefix)
    )
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_target_aware_split_gate.v1",
        "method": "target_aware_prior_window_product_route_selector",
        "training_routes": route_metrics,
        "target_routes": target_routes,
        "holdout_sources": {
            "strict_product": str(args.holdout_strict_product),
            "density_product": str(args.holdout_density_product),
            "low_prefix": str(args.holdout_low_prefix),
        },
        "summary": summarize(rows),
        "selected_cases": rows,
        "honesty_boundary": [
            "The target-aware route rule is a post-P237 diagnostic, not the globally preregistered 1184..1191 selector.",
            "Route choices are computed from prior-window target-specific product metrics only.",
            "Holdout verifier rank, derived secret, and below-rho status are measured after target-aware route selection.",
            "This is controlled toy-prime evidence, not a deployed-curve ECDLP break.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    print(json.dumps(output["target_routes"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
