#!/usr/bin/env python3
"""Pre-register the fixed-leaf split public gate for the next holdout.

P236 left two product routes: a strict duplicate-signature product gate with
lower noise, and a density product gate with higher recall but many more
unverified selections.  This probe consumes only prior-window gate artifacts and
freezes a split route before the next source window is generated.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_fixed_leaf_split_gate_selector_1168_1183_preregister_1184_1191_probe.json"


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
    paths: list[tuple[str, Path]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" in chunk:
            label, path = chunk.split("=", 1)
            paths.append((label.strip(), Path(path.strip())))
        else:
            path = Path(chunk)
            paths.append((path.stem, path))
    return paths


def product_window_metrics(label: str, path: Path) -> dict[str, Any]:
    artifact = load_json(path)
    summary = artifact.get("summary") or {}
    selected = int_value(summary.get("public_product_gate_selected_count"))
    verified = int_value(summary.get("selected_shared_product_verified_count"))
    below = int_value(summary.get("selected_shared_product_below_rho_count"))
    false_positive = int_value(summary.get("gate_false_positive_count"))
    verified_above = int_value(summary.get("gate_verified_above_rho_count"))
    return {
        "label": label,
        "path": str(path),
        "gate_name": summary.get("gate_name") or (artifact.get("parameters") or {}).get("gate"),
        "selected_count": selected,
        "verified_count": verified,
        "below_rho_count": below,
        "false_positive_count": false_positive,
        "verified_above_rho_count": verified_above,
        "selected_precision": ratio(below, selected),
        "verified_success_rate": ratio(below, verified),
        "noise_per_below_rho": ratio(false_positive + verified_above, below),
        "false_positive_rate": ratio(false_positive, selected),
        "target_counts": summary.get("public_product_gate_selected_target_counts") or {},
        "below_rho_target_counts": summary.get("selected_shared_product_below_rho_target_counts") or {},
    }


def aggregate_product_route(route: str, windows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = sum(int_value(row.get("selected_count")) for row in windows)
    verified = sum(int_value(row.get("verified_count")) for row in windows)
    below = sum(int_value(row.get("below_rho_count")) for row in windows)
    false_positive = sum(int_value(row.get("false_positive_count")) for row in windows)
    verified_above = sum(int_value(row.get("verified_above_rho_count")) for row in windows)
    return {
        "route": route,
        "gate_name": windows[0].get("gate_name") if windows else None,
        "window_count": len(windows),
        "windows": windows,
        "selected_count": selected,
        "verified_count": verified,
        "below_rho_count": below,
        "false_positive_count": false_positive,
        "verified_above_rho_count": verified_above,
        "selected_precision": ratio(below, selected),
        "verified_success_rate": ratio(below, verified),
        "noise_per_below_rho": ratio(false_positive + verified_above, below),
        "false_positive_rate": ratio(false_positive, selected),
        "score_tuple": [
            ratio(below, selected),
            -ratio(false_positive + verified_above, below),
            ratio(below, verified),
            below,
            -selected,
        ],
    }


def low_prefix_window_metrics(label: str, path: Path) -> dict[str, Any]:
    artifact = load_json(path)
    summary = artifact.get("summary") or {}
    selected = int_value(summary.get("public_low_prefix_gate_selected_count"))
    verified = int_value(summary.get("selected_direct_verified_count"))
    below = int_value(summary.get("selected_direct_below_rho_count"))
    unverified = int_value(summary.get("selected_unverified_count"))
    verified_above = verified - below
    return {
        "label": label,
        "path": str(path),
        "gate_name": summary.get("gate_name") or (artifact.get("parameters") or {}).get("gate"),
        "selected_count": selected,
        "verified_count": verified,
        "below_rho_count": below,
        "unverified_count": unverified,
        "verified_above_rho_count": verified_above,
        "selected_precision": ratio(below, selected),
        "verified_success_rate": ratio(below, verified),
        "noise_per_below_rho": ratio(unverified + verified_above, below),
        "below_rho_target_counts": summary.get("selected_direct_below_rho_target_counts") or {},
    }


def aggregate_low_prefix(windows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = sum(int_value(row.get("selected_count")) for row in windows)
    verified = sum(int_value(row.get("verified_count")) for row in windows)
    below = sum(int_value(row.get("below_rho_count")) for row in windows)
    unverified = sum(int_value(row.get("unverified_count")) for row in windows)
    verified_above = sum(int_value(row.get("verified_above_rho_count")) for row in windows)
    return {
        "route": "target67_low_prefix_direct",
        "gate_name": windows[0].get("gate_name") if windows else None,
        "window_count": len(windows),
        "windows": windows,
        "selected_count": selected,
        "verified_count": verified,
        "below_rho_count": below,
        "unverified_count": unverified,
        "verified_above_rho_count": verified_above,
        "selected_precision": ratio(below, selected),
        "verified_success_rate": ratio(below, verified),
        "noise_per_below_rho": ratio(unverified + verified_above, below),
        "include_route": bool(windows and all(int_value(row.get("below_rho_count")) > 0 for row in windows)),
    }


def select_product_route(routes: list[dict[str, Any]]) -> dict[str, Any]:
    viable = [row for row in routes if int_value(row.get("below_rho_count")) > 0]
    if not viable:
        return {
            "selected_route": None,
            "reason": "no product route had a prior below-rho selected case",
            "status": "NO_PRODUCT_ROUTE_SELECTED",
        }
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
    return {
        "selected_route": chosen.get("route"),
        "selected_gate_name": chosen.get("gate_name"),
        "reason": (
            "selected by prior selected-case precision, then lower noise per "
            "below-rho recovery, then verified success rate and recall"
        ),
        "status": "PRODUCT_ROUTE_SELECTED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-products", required=True)
    parser.add_argument("--density-products", required=True)
    parser.add_argument("--low-prefix", required=True)
    parser.add_argument("--next-window", default="1184_1191")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    strict_windows = [
        product_window_metrics(label, path)
        for label, path in parse_labeled_paths(args.strict_products)
    ]
    density_windows = [
        product_window_metrics(label, path)
        for label, path in parse_labeled_paths(args.density_products)
    ]
    low_prefix_windows = [
        low_prefix_window_metrics(label, path)
        for label, path in parse_labeled_paths(args.low_prefix)
    ]
    product_routes = [
        aggregate_product_route("strict_duplicate_ge5_product_ge1", strict_windows),
        aggregate_product_route("density_duplicate_ge_half_product_ge1", density_windows),
    ]
    low_prefix = aggregate_low_prefix(low_prefix_windows)
    product_selection = select_product_route(product_routes)
    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_split_gate_selector.v1",
        "method": "prior_window_precision_guarded_split_gate_selector",
        "next_window": args.next_window,
        "training_sources": {
            "strict_products": args.strict_products,
            "density_products": args.density_products,
            "low_prefix": args.low_prefix,
        },
        "product_routes": product_routes,
        "low_prefix_route": low_prefix,
        "selection": {
            **product_selection,
            "include_low_prefix_route": bool(low_prefix.get("include_route")),
            "low_prefix_gate_name": low_prefix.get("gate_name"),
            "claim_status": (
                "SPLIT_GATE_PREREGISTERED"
                if product_selection.get("selected_route") and low_prefix.get("include_route")
                else "SPLIT_GATE_PREREGISTRATION_INCOMPLETE"
            ),
        },
        "honesty_boundary": [
            "The selector consumes only prior-window gate artifacts.",
            "Product-route selection uses prior selected-case precision before recall to avoid silently promoting noisy density routes.",
            "Low-prefix inclusion requires at least one target-67 below-rho selected case in every training window.",
            "Verifier rank, derived secret, and below-rho labels in training artifacts are used only to score prior gates before the next holdout is generated.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output["selection"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
