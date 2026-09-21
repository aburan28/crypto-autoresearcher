#!/usr/bin/env python3
"""Guarded target-aware split product gate for fixed-leaf two-row probes.

The target-aware split selector lets `67.a1@9803` use the higher-recall density
product route when prior target evidence supports it.  This follow-up adds a
second public guard for that noisy density route: score candidate guards on prior
windows using only public case shape and selected-leaf sharing metrics, freeze
one guard, then apply it to the holdout density rows before combining with the
strict-product and low-prefix routes.

The default path preserves the original density-only guard.  Optional
strict-route guards can be enabled for selected targets when prior public
strict-route metrics show that a feature such as root reuse reduces unverified
rows without importing verifier labels into the holdout decision.
"""

from __future__ import annotations

import argparse
import glob
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import functional_graph_qr_surface_transition_hybrid_gate_probe as graph_routes
import low_term_total2_fixed_leaf_split_public_gate_summary_probe as split_summary
import low_term_total2_fixed_leaf_target_aware_split_gate_probe as target_aware


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_fixed_leaf_guarded_target_aware_split_gate_1200_1207_probe.json"
)
TARGET_DENSITY_ROUTE = "density_duplicate_ge_half_product_ge1"
STRICT_ROUTE = "strict_duplicate_ge5_product_ge1"


GuardFn = Callable[[dict[str, Any]], bool]


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def metric_int(row: dict[str, Any], name: str, default: int = 0) -> int:
    return int_value((row.get("gate_metrics") or {}).get(name), default)


def graph_route_features(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("_graph_route_features") or {}


def graph_feature_int(row: dict[str, Any], name: str, default: int = 0) -> int:
    return int_value(graph_route_features(row).get(name), default)


def selector(row: dict[str, Any]) -> str:
    return str(row.get("selector") or "")


def top_k(row: dict[str, Any]) -> int:
    return int_value(row.get("top_k"))


def charge(row: dict[str, Any]) -> int:
    return metric_int(row, "shared_signature_root_charge", 10**9)


def saved_roots(row: dict[str, Any]) -> int:
    return metric_int(row, "shared_signature_root_saved_ops")


def product_saved(row: dict[str, Any]) -> int:
    return metric_int(row, "shared_selected_leaf_product_saved_ops")


def duplicate_check_saved(row: dict[str, Any]) -> int:
    return metric_int(row, "duplicate_selected_leaf_check_saved_ops")


def has_root_reuse(row: dict[str, Any]) -> bool:
    return saved_roots(row) >= 1


def charge_le2_root_reuse(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and charge(row) <= 2


def charge_le2_product_reuse(row: dict[str, Any]) -> bool:
    return product_saved(row) >= 1 and charge(row) <= 2


def family_shape_charge_le2(row: dict[str, Any]) -> bool:
    if not charge_le2_root_reuse(row):
        return False
    if selector(row) == "mode_low_term_span_total10":
        return top_k(row) <= 4
    if selector(row) == "mode_hybrid_support_monic_b_total6":
        return top_k(row) <= 12
    if selector(row) == "mode_hash_leaf_total6":
        return top_k(row) <= 4
    return False


def hybrid_lowterm_charge_le2(row: dict[str, Any]) -> bool:
    if not charge_le2_root_reuse(row):
        return False
    if selector(row) == "mode_low_term_span_total10":
        return top_k(row) <= 4
    if selector(row) == "mode_hybrid_support_monic_b_total6":
        return top_k(row) <= 12
    return False


def hash_or_top4_charge_le2(row: dict[str, Any]) -> bool:
    if not charge_le2_root_reuse(row):
        return False
    if selector(row) == "mode_hash_leaf_total6":
        return True
    return top_k(row) <= 4


def hash_top7_or_top4_charge_le2(row: dict[str, Any]) -> bool:
    if not charge_le2_root_reuse(row):
        return False
    if selector(row) == "mode_hash_leaf_total6":
        return top_k(row) <= 7
    return top_k(row) <= 4


def topk4_root_saved_charge_le1(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and top_k(row) == 4 and charge(row) <= 1


def topk_le4_root_saved_ge1(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and top_k(row) <= 4


def topk4_or_lowterm_charge2_topk16_root_saved(row: dict[str, Any]) -> bool:
    if topk_le4_root_saved_ge1(row):
        return True
    return (
        selector(row) == "mode_low_term_span_total10"
        and charge_le2_root_reuse(row)
        and top_k(row) <= 16
    )


def topk4_or_lowterm_charge2_or_hash_charge2_topk12_hit3_root_saved(
    row: dict[str, Any],
) -> bool:
    if topk4_or_lowterm_charge2_topk16_root_saved(row):
        return True
    return (
        selector(row) == "mode_hash_leaf_total6"
        and has_root_reuse(row)
        and charge(row) == 2
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 3
    )


def topk4_or_hash_charge2_topk12_hit3_root_saved(row: dict[str, Any]) -> bool:
    if topk_le4_root_saved_ge1(row):
        return True
    return (
        selector(row) == "mode_hash_leaf_total6"
        and has_root_reuse(row)
        and charge(row) == 2
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 3
    )


def topk4_or_hash12_hit3_or_hash12_hit5_root_saved(row: dict[str, Any]) -> bool:
    if topk4_or_hash_charge2_topk12_hit3_root_saved(row):
        return True
    return (
        selector(row) == "mode_hash_leaf_total6"
        and has_root_reuse(row)
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 5
    )


def topk4_or_hash12_hit5_root_saved_repaired(row: dict[str, Any]) -> bool:
    if topk_le4_root_saved_ge1(row):
        return True
    return (
        selector(row) == "mode_hash_leaf_total6"
        and has_root_reuse(row)
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 5
    )


def topk4_root_saved_precision_repaired(row: dict[str, Any]) -> bool:
    if top_k(row) > 4 or saved_roots(row) < 1:
        return False
    if selector(row) == "mode_low_term_span_total10":
        return (
            metric_int(row, "direct_selected_hit_root_ops") >= 3
            and metric_int(row, "unique_selected_leaf_signature_count") >= 4
        )
    if selector(row) in {
        "mode_hash_leaf_total6",
        "mode_hybrid_support_monic_b_total6",
    }:
        return (
            metric_int(row, "direct_selected_hit_root_ops") >= 4
            and charge(row) >= 3
        )
    return metric_int(row, "direct_selected_hit_root_ops") >= 4


def topk4_precision_or_hash12_hit5_root_saved_repaired(row: dict[str, Any]) -> bool:
    if topk4_root_saved_precision_repaired(row):
        return True
    return (
        selector(row) == "mode_hash_leaf_total6"
        and has_root_reuse(row)
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 5
    )


def hash_top7_hit3_charge3_no_root_shared_ops_ge_0p75(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and top_k(row) <= 7
        and metric_int(row, "direct_selected_hit_root_ops") >= 3
        and charge(row) == 3
        and saved_roots(row) == 0
        and metric_int(row, "unique_selected_leaf_signature_count") == 3
        and float_value(row.get("shared_product_ledger_ops_over_rho")) >= 0.75
    )


def hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and top_k(row) <= 12
        and metric_int(row, "direct_selected_hit_root_ops") >= 3
        and charge(row) == 3
        and saved_roots(row) == 0
        and metric_int(row, "unique_selected_leaf_signature_count") == 3
        and float_value(row.get("shared_product_ledger_ops_over_rho")) >= 0.75
    )


def hash_top7_root_saved_hit4_charge_le3_shared_ops_ge_0p75(
    row: dict[str, Any],
) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and top_k(row) <= 7
        and saved_roots(row) >= 1
        and metric_int(row, "direct_selected_hit_root_ops") >= 4
        and charge(row) <= 3
        and float_value(row.get("shared_product_ledger_ops_over_rho")) >= 0.75
    )


def topk4_or_hash12_hit5_or_hash_top7_no_root_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_or_hash12_hit3_or_hash12_hit5_root_saved(row)
        or hash_top7_hit3_charge3_no_root_shared_ops_ge_0p75(row)
    )


def topk4_or_hash12_hit5_or_hash_top7_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_or_hash12_hit5_or_hash_top7_no_root_ops_floor(row)
        or hash_top7_root_saved_hit4_charge_le3_shared_ops_ge_0p75(row)
    )


def topk4_or_hash12_hit5_or_hash_top12_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_or_hash12_hit5_or_hash_top7_ops_floor(row)
        or hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75(row)
    )


def topk4_or_hash12_hit5_or_hash_top12_no_root_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_or_hash12_hit3_or_hash12_hit5_root_saved(row)
        or hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75(row)
    )


def topk4_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_or_hash12_hit5_root_saved_repaired(row)
        or hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75(row)
    )


def topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_precision_or_hash12_hit5_root_saved_repaired(row)
        or hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75(row)
    )


def hash_product_saved_charge_le2_topk_le16(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and charge_le2_product_reuse(row)
        and top_k(row) <= 16
    )


def hash_product_saved_charge_le2_topk_le12(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and charge_le2_product_reuse(row)
        and top_k(row) <= 12
    )


def root_reuse_topk12_charge_ge5_else_not12(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and (top_k(row) != 12 or charge(row) >= 5)


def root_reuse_topk12_charge5_topk16_charge4(row: dict[str, Any]) -> bool:
    if not has_root_reuse(row):
        return False
    if top_k(row) == 12 and charge(row) < 5:
        return False
    if top_k(row) == 16 and charge(row) < 4:
        return False
    return True


def lowterm10_topk7_product_reuse(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_low_term_span_total10"
        and top_k(row) == 7
        and product_saved(row) >= 1
        and duplicate_check_saved(row) >= 5
    )


def lowterm10_topk7_product_reuse_root_saved(row: dict[str, Any]) -> bool:
    return lowterm10_topk7_product_reuse(row) and saved_roots(row) >= 1


def lowterm10_topk7_product_reuse_root_saved_charge_le6(
    row: dict[str, Any],
) -> bool:
    return lowterm10_topk7_product_reuse_root_saved(row) and charge(row) <= 6


def lowterm10_topk7_product_reuse_root_saved_charge4_or5(
    row: dict[str, Any],
) -> bool:
    return lowterm10_topk7_product_reuse_root_saved(row) and charge(row) in {4, 5}


def lowterm10_topk7_product_reuse_root_saved_charge_ge4_edge_le8(
    row: dict[str, Any],
) -> bool:
    return (
        lowterm10_topk7_product_reuse_root_saved(row)
        and charge(row) >= 4
        and graph_feature_int(row, "route_edge_max") <= 8
    )


def lowterm10_topk7_product_reuse_root_saved_low_charge_edge4_or16(
    row: dict[str, Any],
) -> bool:
    if not (
        lowterm10_topk7_product_reuse_root_saved(row)
        and graph_feature_int(row, "first_match_count") == 2
    ):
        return False
    if (
        charge(row) == 2
        and metric_int(row, "direct_selected_hit_root_ops") == 3
        and graph_feature_int(row, "route_edge_min") == 4
        and graph_feature_int(row, "route_edge_max") == 4
    ):
        return True
    return (
        charge(row) == 3
        and metric_int(row, "direct_selected_hit_root_ops") == 4
        and graph_feature_int(row, "route_edge_min") == 16
        and graph_feature_int(row, "route_edge_max") == 16
    )


def lowterm10_topk7_product_reuse_root_saved_charge45_or_low_charge_edge4_or16(
    row: dict[str, Any],
) -> bool:
    return (
        lowterm10_topk7_product_reuse_root_saved_charge4_or5(row)
        or lowterm10_topk7_product_reuse_root_saved_low_charge_edge4_or16(row)
    )


def lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge6(
    row: dict[str, Any],
) -> bool:
    return (
        lowterm10_topk7_product_reuse_root_saved_charge_le6(row)
        and metric_int(row, "direct_selected_hit_root_ops") >= 6
    )


def lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge7_or_saved_ge2(
    row: dict[str, Any],
) -> bool:
    return lowterm10_topk7_product_reuse_root_saved_charge_le6(row) and (
        metric_int(row, "direct_selected_hit_root_ops") >= 7 or saved_roots(row) >= 2
    )


def root_reuse_or_lowterm10_topk7_product_reuse(row: dict[str, Any]) -> bool:
    return (
        root_reuse_topk12_charge5_topk16_charge4(row)
        or lowterm10_topk7_product_reuse(row)
    )


def root_reuse_charge_ge4(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and charge(row) >= 4


def root_reuse_charge_ge4_or_topk7(row: dict[str, Any]) -> bool:
    return has_root_reuse(row) and (charge(row) >= 4 or top_k(row) == 7)


def graph_first_match_one_route_edge_max_ge16(row: dict[str, Any]) -> bool:
    return (
        graph_feature_int(row, "first_match_count") == 1
        and graph_feature_int(row, "route_edge_max") >= 16
    )


def lowterm10_topk7_graph_first_match_one(row: dict[str, Any]) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and graph_feature_int(row, "first_match_count") == 1
    )


def lowterm10_topk7_graph_route_edge_min4(row: dict[str, Any]) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and graph_feature_int(row, "route_edge_min") == 4
    )


def lowterm10_topk7_graph_route_edge_max_le8(row: dict[str, Any]) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and graph_feature_int(row, "route_edge_max") <= 8
    )


def lowterm10_topk7_graph_edge_min4_or_first_match_one(row: dict[str, Any]) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and (
            graph_feature_int(row, "route_edge_min") == 4
            or graph_feature_int(row, "first_match_count") == 1
        )
    )


def lowterm10_topk7_root_saved_charge3_hit4_graph_edge12_first2(
    row: dict[str, Any],
) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and saved_roots(row) == 1
        and charge(row) == 3
        and metric_int(row, "direct_selected_hit_root_ops") == 4
        and metric_int(row, "unique_selected_leaf_signature_count") >= 5
        and graph_feature_int(row, "first_match_count") == 2
        and graph_feature_int(row, "route_edge_min") == 12
        and graph_feature_int(row, "route_edge_max") == 12
    )


def graph_edge4_density_hash_top12_saved2_charge2_hit4(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hash_leaf_total6"
        and top_k(row) == 12
        and product_saved(row) >= 1
        and saved_roots(row) >= 2
        and charge(row) == 2
        and metric_int(row, "direct_selected_hit_root_ops") >= 4
        and metric_int(row, "unique_selected_leaf_signature_count") == 3
        and graph_feature_int(row, "first_match_count") == 2
        and graph_feature_int(row, "route_edge_min") == 4
        and graph_feature_int(row, "route_edge_max") == 4
    )


def graph_edge4_density_hybrid_topk7_saved1_charge2_hit3(row: dict[str, Any]) -> bool:
    return (
        selector(row) == "mode_hybrid_support_monic_b_total6"
        and top_k(row) == 7
        and product_saved(row) >= 1
        and saved_roots(row) == 1
        and charge(row) == 2
        and metric_int(row, "direct_selected_hit_root_ops") == 3
        and metric_int(row, "unique_selected_leaf_signature_count") == 3
        and graph_feature_int(row, "first_match_count") == 2
        and graph_feature_int(row, "route_edge_min") == 4
        and graph_feature_int(row, "route_edge_max") == 4
    )


def graph_edge4_density_lowterm10_topk7_saved1_charge3_hit4(
    row: dict[str, Any],
) -> bool:
    return (
        lowterm10_topk7_product_reuse(row)
        and saved_roots(row) == 1
        and charge(row) == 3
        and metric_int(row, "direct_selected_hit_root_ops") == 4
        and metric_int(row, "unique_selected_leaf_signature_count") >= 5
        and graph_feature_int(row, "first_match_count") == 2
        and graph_feature_int(row, "route_edge_min") == 4
        and graph_feature_int(row, "route_edge_max") == 4
    )


def graph_edge4_density_hash12_saved2_or_topk7_root_saved(
    row: dict[str, Any],
) -> bool:
    return (
        graph_edge4_density_hash_top12_saved2_charge2_hit4(row)
        or graph_edge4_density_hybrid_topk7_saved1_charge2_hit3(row)
        or graph_edge4_density_lowterm10_topk7_saved1_charge3_hit4(row)
    )


def topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor_or_graph_edge4_density(
    row: dict[str, Any],
) -> bool:
    return (
        topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor(row)
        or graph_edge4_density_hash12_saved2_or_topk7_root_saved(row)
    )


GUARDS: dict[str, GuardFn] = {
    "public_guard_none": lambda row: True,
    "public_guard_root_saved_ge1": has_root_reuse,
    "public_guard_root_saved_ge1_topk12_charge_ge5_else_not12": (
        root_reuse_topk12_charge_ge5_else_not12
    ),
    "public_guard_root_saved_ge1_topk12_charge5_topk16_charge4": (
        root_reuse_topk12_charge5_topk16_charge4
    ),
    "public_guard_root_saved_ge1_topk12_charge5_topk16_charge4_or_lowterm10_topk7_product_reuse": (
        root_reuse_or_lowterm10_topk7_product_reuse
    ),
    "public_guard_lowterm10_topk7_product_reuse": lowterm10_topk7_product_reuse,
    "public_guard_lowterm10_topk7_product_reuse_root_saved_ge1": (
        lowterm10_topk7_product_reuse_root_saved
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge_le6": (
        lowterm10_topk7_product_reuse_root_saved_charge_le6
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge4_or5": (
        lowterm10_topk7_product_reuse_root_saved_charge4_or5
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge_ge4_edge_le8": (
        lowterm10_topk7_product_reuse_root_saved_charge_ge4_edge_le8
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_low_charge_edge4_or16": (
        lowterm10_topk7_product_reuse_root_saved_low_charge_edge4_or16
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge45_or_low_charge_edge4_or16": (
        lowterm10_topk7_product_reuse_root_saved_charge45_or_low_charge_edge4_or16
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge6": (
        lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge6
    ),
    "public_guard_lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge7_or_saved_ge2": (
        lowterm10_topk7_product_reuse_root_saved_charge_le6_hit_ge7_or_saved_ge2
    ),
    "public_guard_root_saved_ge1_charge_ge4": root_reuse_charge_ge4,
    "public_guard_root_saved_ge1_charge_ge4_or_topk7": (
        root_reuse_charge_ge4_or_topk7
    ),
    "public_guard_charge_le2_root_saved_ge1": charge_le2_root_reuse,
    "public_guard_charge_le2_root_saved_ge1_topk_le16": (
        lambda row: charge_le2_root_reuse(row) and top_k(row) <= 16
    ),
    "public_guard_charge_le2_root_saved_ge1_topk_le12": (
        lambda row: charge_le2_root_reuse(row) and top_k(row) <= 12
    ),
    "public_guard_charge_le2_root_saved_ge1_topk_le7": (
        lambda row: charge_le2_root_reuse(row) and top_k(row) <= 7
    ),
    "public_guard_charge_le2_product_saved_ge1": charge_le2_product_reuse,
    "public_guard_charge_le2_product_saved_ge1_topk_le16": (
        lambda row: charge_le2_product_reuse(row) and top_k(row) <= 16
    ),
    "public_guard_charge_le2_product_saved_ge1_topk_le12": (
        lambda row: charge_le2_product_reuse(row) and top_k(row) <= 12
    ),
    "public_guard_charge_le2_product_saved_ge1_topk_le7": (
        lambda row: charge_le2_product_reuse(row) and top_k(row) <= 7
    ),
    "public_guard_family_shape_charge_le2": family_shape_charge_le2,
    "public_guard_hybrid_lowterm_charge_le2": hybrid_lowterm_charge_le2,
    "public_guard_hash_or_top4_charge_le2": hash_or_top4_charge_le2,
    "public_guard_hash_top7_or_top4_charge_le2": hash_top7_or_top4_charge_le2,
    "public_guard_topk4_root_saved_ge1_charge_le1": topk4_root_saved_charge_le1,
    "public_guard_topk_le4_root_saved_ge1": topk_le4_root_saved_ge1,
    "public_guard_topk_le4_root_saved_or_lowterm_charge2_topk16_root_saved": (
        topk4_or_lowterm_charge2_topk16_root_saved
    ),
    "public_guard_topk4_lowterm_charge2_or_hash_charge2_topk12_hit3_root_saved": (
        topk4_or_lowterm_charge2_or_hash_charge2_topk12_hit3_root_saved
    ),
    "public_guard_topk4_or_hash_charge2_topk12_hit3_root_saved": (
        topk4_or_hash_charge2_topk12_hit3_root_saved
    ),
    "public_guard_topk4_or_hash12_hit3_or_hash12_hit5_root_saved": (
        topk4_or_hash12_hit3_or_hash12_hit5_root_saved
    ),
    "public_guard_topk4_or_hash12_hit5_root_saved_repaired": (
        topk4_or_hash12_hit5_root_saved_repaired
    ),
    "public_guard_topk4_precision_or_hash12_hit5_root_saved_repaired": (
        topk4_precision_or_hash12_hit5_root_saved_repaired
    ),
    "public_guard_hash_top7_hit3_charge3_no_root_shared_ops_ge_0p75": (
        hash_top7_hit3_charge3_no_root_shared_ops_ge_0p75
    ),
    "public_guard_topk4_or_hash12_hit5_or_hash_top7_no_root_ops_floor": (
        topk4_or_hash12_hit5_or_hash_top7_no_root_ops_floor
    ),
    "public_guard_hash_top7_root_saved_hit4_charge_le3_shared_ops_ge_0p75": (
        hash_top7_root_saved_hit4_charge_le3_shared_ops_ge_0p75
    ),
    "public_guard_topk4_or_hash12_hit5_or_hash_top7_ops_floor": (
        topk4_or_hash12_hit5_or_hash_top7_ops_floor
    ),
    "public_guard_hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75": (
        hash_top12_hit3_charge3_no_root_shared_ops_ge_0p75
    ),
    "public_guard_topk4_or_hash12_hit5_or_hash_top12_ops_floor": (
        topk4_or_hash12_hit5_or_hash_top12_ops_floor
    ),
    "public_guard_topk4_or_hash12_hit5_or_hash_top12_no_root_ops_floor": (
        topk4_or_hash12_hit5_or_hash_top12_no_root_ops_floor
    ),
    "public_guard_topk4_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor": (
        topk4_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor
    ),
    "public_guard_topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor": (
        topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor
    ),
    "public_guard_hash_product_saved_charge_le2_topk_le16": (
        hash_product_saved_charge_le2_topk_le16
    ),
    "public_guard_hash_product_saved_charge_le2_topk_le12": (
        hash_product_saved_charge_le2_topk_le12
    ),
    "public_guard_graph_first_match_one_route_edge_max_ge16": (
        graph_first_match_one_route_edge_max_ge16
    ),
    "public_guard_lowterm10_topk7_graph_first_match_one": (
        lowterm10_topk7_graph_first_match_one
    ),
    "public_guard_lowterm10_topk7_graph_route_edge_min4": (
        lowterm10_topk7_graph_route_edge_min4
    ),
    "public_guard_lowterm10_topk7_graph_route_edge_max_le8": (
        lowterm10_topk7_graph_route_edge_max_le8
    ),
    "public_guard_lowterm10_topk7_graph_edge_min4_or_first_match_one": (
        lowterm10_topk7_graph_edge_min4_or_first_match_one
    ),
    "public_guard_lowterm10_topk7_root_saved_charge3_hit4_graph_edge12_first2": (
        lowterm10_topk7_root_saved_charge3_hit4_graph_edge12_first2
    ),
    "public_guard_graph_edge4_density_hash12_saved2_or_topk7_root_saved": (
        graph_edge4_density_hash12_saved2_or_topk7_root_saved
    ),
    "public_guard_topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor_or_graph_edge4_density": (
        topk4_precision_or_hash12_hit5_repaired_or_hash_top12_no_root_ops_floor_or_graph_edge4_density
    ),
}


def parse_route_sources(raw: str) -> list[tuple[str, Path]]:
    sources: list[tuple[str, Path]] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "=" in chunk:
            label, path = chunk.split("=", 1)
            sources.append((label.strip(), Path(path.strip())))
            continue
        matches = [Path(path) for path in glob.glob(chunk)]
        for path in sorted(matches or [Path(chunk)]):
            sources.append((graph_routes.replay.window_label(path), path))
    return sources


def route_feature_index(labeled_sources: list[tuple[str, Path]]) -> dict[tuple[str, str, int, str], dict[str, Any]]:
    paths = [path for _, path in labeled_sources if path.exists()]
    if not paths:
        return {}
    edges = graph_routes.replay.load_edges(paths)
    routes = graph_routes.replay.route_index(edges)
    features: dict[tuple[str, str, int, str], dict[str, Any]] = {}
    for route, route_edges in routes.items():
        if not route_edges:
            continue
        first_edge = graph_routes.streaming.route_leaf_first_edge(route, route_edges)
        first_features = graph_routes.first_edge_features(route, route_edges)
        label, target, transfer_index, row_key = route
        features[(str(label), str(target), int_value(transfer_index), str(row_key))] = {
            "first_row_keys": tuple(sorted(str(key) for key in first_edge.get("row_keys") or [])),
            "first_selector": str(first_edge.get("selector") or ""),
            "first_top_k": int_value(first_edge.get("top_k")),
            "first_ops_over_rho": float(first_features.get("first_ops_over_rho") or 0.0),
            "route_leaf_count": int_value(first_features.get("route_leaf_count")),
            "selected_leaf_count": int_value(first_features.get("selected_leaf_count")),
            "route_edge_count": int_value(first_features.get("route_edge_count")),
            "sibling_count": int_value(first_features.get("sibling_count")),
        }
    return features


def attach_graph_route_features(
    row: dict[str, Any],
    label: str,
    features: dict[tuple[str, str, int, str], dict[str, Any]] | None,
) -> dict[str, Any]:
    if not features:
        return row
    target = str(row.get("target") or "")
    transfer_index = int_value(row.get("transfer_index"))
    row_keys = [str(key) for key in row.get("row_keys") or []]
    endpoint_features = [
        item
        for item in (
            features.get((str(label), target, transfer_index, row_key))
            for row_key in row_keys
        )
        if item is not None
    ]
    row_key_signature = tuple(sorted(row_keys))
    first_match_count = sum(
        1
        for item in endpoint_features
        if tuple(item.get("first_row_keys") or ()) == row_key_signature
    )

    def values(name: str, default: int = 0) -> list[int]:
        return [int_value(item.get(name), default) for item in endpoint_features]

    graph_features = {
        "source_label": str(label),
        "route_count": len(endpoint_features),
        "first_match_count": first_match_count,
        "route_edge_min": min(values("route_edge_count", 10**9), default=0),
        "route_edge_max": max(values("route_edge_count"), default=0),
        "sibling_min": min(values("sibling_count", 10**9), default=0),
        "sibling_max": max(values("sibling_count"), default=0),
        "route_leaf_min": min(values("route_leaf_count", 10**9), default=0),
        "route_leaf_max": max(values("route_leaf_count"), default=0),
        "selected_leaf_min": min(values("selected_leaf_count", 10**9), default=0),
        "selected_leaf_max": max(values("selected_leaf_count"), default=0),
        "endpoint_first_edges": [
            {
                "first_selector": item.get("first_selector"),
                "first_top_k": item.get("first_top_k"),
                "first_ops_over_rho": item.get("first_ops_over_rho"),
                "route_edge_count": item.get("route_edge_count"),
                "sibling_count": item.get("sibling_count"),
            }
            for item in endpoint_features[:4]
        ],
    }
    return {**row, "_graph_route_features": graph_features}


def window_label_from_path(path: Path) -> str:
    name = path.name
    for chunk in name.split("_"):
        if "-" in chunk and chunk.replace("-", "").isdigit():
            return chunk
    return path.stem


def selected_rows_for_target(
    artifact: dict[str, Any],
    target: str,
    label: str = "",
    graph_features: dict[tuple[str, str, int, str], dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    return [
        attach_graph_route_features(row, label, graph_features)
        for row in target_aware.selected_product_cases(artifact)
        if str(row.get("target")) == target
    ]


def compact_guard_case(row: dict[str, Any], guard_name: str, route: str) -> dict[str, Any]:
    compact = split_summary.compact_product_case(row)
    compact.update(
        {
            "route": f"{route}:guarded:{guard_name}",
            "base_route": route,
            "guard_name": guard_name,
            "guard_public_features": {
                "selector": selector(row),
                "top_k": top_k(row),
                "direct_selected_leaf_check_ops": metric_int(
                    row, "direct_selected_leaf_check_ops"
                ),
                "duplicate_selected_leaf_check_saved_ops": metric_int(
                    row, "duplicate_selected_leaf_check_saved_ops"
                ),
                "shared_selected_leaf_product_saved_ops": metric_int(
                    row, "shared_selected_leaf_product_saved_ops"
                ),
                "direct_selected_hit_root_ops": metric_int(
                    row, "direct_selected_hit_root_ops"
                ),
                "shared_signature_root_charge": charge(row),
                "shared_signature_root_saved_ops": saved_roots(row),
                "unique_selected_leaf_signature_count": metric_int(
                    row, "unique_selected_leaf_signature_count"
                ),
                "graph_route_features": graph_route_features(row),
            },
        }
    )
    return compact


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
            below,
            -ratio(false_positive + verified_above, below),
            -selected,
        ],
    }


def evaluate_guard_rows(rows: list[dict[str, Any]], guard_fn: GuardFn) -> dict[str, Any]:
    selected = [row for row in rows if guard_fn(row)]
    verified = [row for row in selected if row.get("shared_product_union_public_key_verified")]
    below = [row for row in verified if row.get("shared_product_ledger_beats_rho")]
    return finalize_metric(
        {
            "selected_count": len(selected),
            "verified_count": len(verified),
            "below_rho_count": len(below),
            "false_positive_count": len(selected) - len(verified),
            "verified_above_rho_count": len(verified) - len(below),
        }
    )


def evaluate_guards(
    guard_names: list[str],
    labeled_paths: list[tuple[str, Path]],
    guard_target: str,
    graph_features: dict[tuple[str, str, int, str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    guard_metrics = {
        name: {
            "guard_name": name,
            "target": guard_target,
            "selected_count": 0,
            "verified_count": 0,
            "below_rho_count": 0,
            "false_positive_count": 0,
            "verified_above_rho_count": 0,
            "below_rho_window_count": 0,
            "windows": [],
        }
        for name in guard_names
    }
    for label, path in labeled_paths:
        artifact = target_aware.load_json(path)
        rows = selected_rows_for_target(artifact, guard_target, label, graph_features)
        for name in guard_names:
            window_metric = evaluate_guard_rows(rows, GUARDS[name])
            if int_value(window_metric.get("below_rho_count")) > 0:
                guard_metrics[name]["below_rho_window_count"] += 1
            for key in (
                "selected_count",
                "verified_count",
                "below_rho_count",
                "false_positive_count",
                "verified_above_rho_count",
            ):
                guard_metrics[name][key] += int_value(window_metric.get(key))
            guard_metrics[name]["windows"].append(
                {
                    "label": label,
                    "path": str(path),
                    **window_metric,
                }
            )
    return {
        name: finalize_metric(metric)
        for name, metric in sorted(guard_metrics.items())
    }


def choose_guard(
    guard_metrics: dict[str, Any],
    fallback_guard: str,
    score_mode: str,
) -> dict[str, Any]:
    viable = [
        metric
        for metric in guard_metrics.values()
        if int_value(metric.get("below_rho_count")) > 0
    ]
    if not viable:
        return {
            "selected_guard": fallback_guard,
            "reason": "fallback guard because no candidate retained prior below-rho evidence",
            "candidates": guard_metrics,
        }
    if score_mode == "balanced_recall":
        chosen = max(
            viable,
            key=lambda metric: (
                int_value(metric.get("below_rho_window_count")),
                int_value(metric.get("below_rho_count")),
                float(metric.get("selected_precision") or 0.0),
                -float(metric.get("noise_per_below_rho") or 10**9),
                -int_value(metric.get("selected_count")),
            ),
        )
        return {
            "selected_guard": chosen["guard_name"],
            "score_mode": score_mode,
            "reason": (
                "prior-window public guard below-rho window coverage, then "
                "retained below-rho count, then precision, then lower noise"
            ),
            "candidates": guard_metrics,
        }
    chosen = max(
        viable,
        key=lambda metric: (
            float(metric.get("selected_precision") or 0.0),
            int_value(metric.get("below_rho_window_count")),
            int_value(metric.get("below_rho_count")),
            -float(metric.get("noise_per_below_rho") or 10**9),
            -int_value(metric.get("selected_count")),
        ),
    )
    return {
        "selected_guard": chosen["guard_name"],
        "score_mode": score_mode,
        "reason": (
            "prior-window public guard precision, then below-rho window coverage, "
            "then retained below-rho count, then lower noise"
        ),
        "candidates": guard_metrics,
    }


def threshold_float(value: float | None) -> float | None:
    if value is None or value < 0:
        return None
    return value


def guard_passes_prior_thresholds(
    guard_choice: dict[str, Any],
    min_precision: float | None,
    max_noise_per_below_rho: float | None,
    min_below_rho_window_count: int,
) -> tuple[bool, dict[str, Any]]:
    selected_name = str(guard_choice.get("selected_guard") or "")
    metric = (guard_choice.get("candidates") or {}).get(selected_name) or {}
    precision = float(metric.get("selected_precision") or 0.0)
    noise = float(metric.get("noise_per_below_rho") or 0.0)
    window_count = int_value(metric.get("below_rho_window_count"))
    thresholds = {
        "enabled": bool(
            min_precision is not None
            or max_noise_per_below_rho is not None
            or min_below_rho_window_count > 0
        ),
        "selected_guard": selected_name,
        "selected_guard_prior_precision": precision,
        "selected_guard_prior_noise_per_below_rho": noise,
        "selected_guard_prior_below_rho_window_count": window_count,
        "min_prior_precision": min_precision,
        "max_prior_noise_per_below_rho": max_noise_per_below_rho,
        "min_prior_below_rho_window_count": min_below_rho_window_count,
        "failed_reasons": [],
    }
    if min_precision is not None and precision < min_precision:
        thresholds["failed_reasons"].append("prior_precision_below_threshold")
    if max_noise_per_below_rho is not None and noise > max_noise_per_below_rho:
        thresholds["failed_reasons"].append("prior_noise_above_threshold")
    if window_count < min_below_rho_window_count:
        thresholds["failed_reasons"].append("prior_below_rho_window_count_below_threshold")
    thresholds["passes"] = not thresholds["failed_reasons"]
    return bool(thresholds["passes"]), thresholds


def guarded_density_cases(
    product: dict[str, Any],
    target_routes: dict[str, Any],
    guard_target: str,
    guard_name: str,
    enable_density_branch: bool = True,
    holdout_label: str = "",
    graph_features: dict[tuple[str, str, int, str], dict[str, Any]] | None = None,
    extra_density_guard_targets: set[str] | None = None,
    extra_density_guard_name: str = "",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    extra_density_guard_targets = extra_density_guard_targets or set()
    extra_density_guard_name = extra_density_guard_name or guard_name
    selected = []
    rejected = []
    abstained = []
    for raw_row in target_aware.selected_product_cases(product):
        row = attach_graph_route_features(raw_row, holdout_label, graph_features)
        target = str(row.get("target"))
        route_selected_density = (
            target_routes.get(target) or {}
        ).get("selected_route") == TARGET_DENSITY_ROUTE
        forced_density_target = target in extra_density_guard_targets
        if not route_selected_density and not forced_density_target:
            continue
        if target == guard_target or forced_density_target:
            if not enable_density_branch:
                abstained.append(
                    {
                        "target": target,
                        "transfer_index": int_value(row.get("transfer_index")),
                        "selector": selector(row),
                        "top_k": top_k(row),
                        "row_keys": row.get("row_keys") or [],
                    }
                )
                continue
            active_guard_name = (
                extra_density_guard_name
                if forced_density_target and target != guard_target
                else guard_name
            )
            guard_fn = GUARDS[active_guard_name]
            if not guard_fn(row):
                rejected.append(
                    {
                        "target": target,
                        "transfer_index": int_value(row.get("transfer_index")),
                        "selector": selector(row),
                        "top_k": top_k(row),
                        "row_keys": row.get("row_keys") or [],
                        "guard_name": active_guard_name,
                    }
                )
                continue
            route_name = TARGET_DENSITY_ROUTE
            if forced_density_target and not route_selected_density:
                route_name = f"{TARGET_DENSITY_ROUTE}:extra_density_fallback"
            selected.append(compact_guard_case(row, active_guard_name, route_name))
        else:
            selected.append(split_summary.compact_product_case(row))
    return selected, {
        "guard_name": guard_name,
        "guard_target": guard_target,
        "extra_density_guard_targets": sorted(extra_density_guard_targets),
        "extra_density_guard_name": extra_density_guard_name,
        "density_branch_enabled": enable_density_branch,
        "abstained_density_product_case_count": len(abstained),
        "abstained_density_product_cases": abstained[:24],
        "rejected_density_product_case_count": len(rejected),
        "rejected_density_product_cases": rejected[:24],
    }


def guarded_strict_cases(
    product: dict[str, Any],
    target_routes: dict[str, Any],
    strict_guard_targets: set[str],
    strict_guard_name: str,
    strict_guard_names_by_target: dict[str, str] | None = None,
    strict_guard_enabled_by_target: dict[str, bool] | None = None,
    holdout_label: str = "",
    graph_features: dict[tuple[str, str, int, str], dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    strict_guard_names_by_target = strict_guard_names_by_target or {}
    strict_guard_enabled_by_target = strict_guard_enabled_by_target or {}
    selected = []
    rejected = []
    abstained = []
    for raw_row in target_aware.selected_product_cases(product):
        row = attach_graph_route_features(raw_row, holdout_label, graph_features)
        target = str(row.get("target"))
        if (target_routes.get(target) or {}).get("selected_route") != STRICT_ROUTE:
            continue
        if target in strict_guard_targets:
            guard_name = strict_guard_names_by_target.get(target, strict_guard_name)
            if not strict_guard_enabled_by_target.get(target, True):
                abstained.append(
                    {
                        "target": target,
                        "transfer_index": int_value(row.get("transfer_index")),
                        "selector": selector(row),
                        "top_k": top_k(row),
                        "row_keys": row.get("row_keys") or [],
                    }
                )
                continue
            guard_fn = GUARDS[guard_name]
            if not guard_fn(row):
                rejected.append(
                    {
                        "target": target,
                        "transfer_index": int_value(row.get("transfer_index")),
                        "selector": selector(row),
                        "top_k": top_k(row),
                        "row_keys": row.get("row_keys") or [],
                        "guard_name": guard_name,
                    }
                )
                continue
            selected.append(compact_guard_case(row, guard_name, STRICT_ROUTE))
        else:
            selected.append(split_summary.compact_product_case(row))
    return selected, {
        "guard_name": strict_guard_name,
        "guard_targets": sorted(strict_guard_targets),
        "selected_guard_by_target": {
            target: strict_guard_names_by_target.get(target, strict_guard_name)
            for target in sorted(strict_guard_targets)
        },
        "enabled_by_target": {
            target: strict_guard_enabled_by_target.get(target, True)
            for target in sorted(strict_guard_targets)
        },
        "abstained_strict_product_case_count": len(abstained),
        "abstained_strict_product_cases": abstained[:24],
        "rejected_strict_product_case_count": len(rejected),
        "rejected_strict_product_cases": rejected[:24],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-strict-products", required=True)
    parser.add_argument("--train-density-products", required=True)
    parser.add_argument("--holdout-strict-product", type=Path, required=True)
    parser.add_argument("--holdout-density-product", type=Path, required=True)
    parser.add_argument("--holdout-low-prefix", type=Path, required=True)
    parser.add_argument("--guard-target", default="67.a1@9803")
    parser.add_argument("--fallback-route", default=STRICT_ROUTE)
    parser.add_argument("--fallback-guard", default="public_guard_charge_le2_root_saved_ge1")
    parser.add_argument(
        "--strict-guard-targets",
        default="",
        help="Comma-separated targets whose strict route should also receive a public guard.",
    )
    parser.add_argument(
        "--strict-guard",
        default="public_guard_none",
        help="Public guard to apply to strict-route rows for --strict-guard-targets.",
    )
    parser.add_argument(
        "--strict-guard-candidates",
        default="",
        help=(
            "If non-empty, score these comma-separated public guard names on "
            "prior strict-product windows for each --strict-guard-targets target "
            "and apply the chosen guard instead of --strict-guard."
        ),
    )
    parser.add_argument(
        "--strict-fallback-guard",
        default="",
        help=(
            "Fallback strict guard when --strict-guard-candidates has no prior "
            "below-rho evidence. Defaults to --strict-guard."
        ),
    )
    parser.add_argument(
        "--strict-guard-score-mode",
        default="precision_first",
        choices=["precision_first", "balanced_recall"],
    )
    parser.add_argument(
        "--strict-guard-min-prior-precision",
        type=float,
        default=-1.0,
        help=(
            "If non-negative, abstain each guarded strict target unless its "
            "chosen strict guard's prior selected precision is at least this value."
        ),
    )
    parser.add_argument(
        "--strict-guard-max-prior-noise-per-below-rho",
        type=float,
        default=-1.0,
        help=(
            "If non-negative, abstain each guarded strict target when its chosen "
            "strict guard's prior noise per below-rho case is above this value."
        ),
    )
    parser.add_argument(
        "--strict-guard-min-prior-below-rho-window-count",
        type=int,
        default=0,
        help=(
            "Abstain each guarded strict target unless its chosen strict guard "
            "retained below-rho evidence in at least this many prior windows."
        ),
    )
    parser.add_argument(
        "--disable-low-prefix",
        action="store_true",
        help="Do not append the low-prefix direct branch to the combined route.",
    )
    parser.add_argument(
        "--guard-score-mode",
        default="precision_first",
        choices=["precision_first", "balanced_recall"],
    )
    parser.add_argument(
        "--guard-min-prior-precision",
        type=float,
        default=-1.0,
        help=(
            "If non-negative, abstain the guarded density target unless the "
            "chosen guard's prior selected precision is at least this value."
        ),
    )
    parser.add_argument(
        "--guard-max-prior-noise-per-below-rho",
        type=float,
        default=-1.0,
        help=(
            "If non-negative, abstain the guarded density target when the chosen "
            "guard's prior noise per below-rho case is above this value."
        ),
    )
    parser.add_argument(
        "--guard-min-prior-below-rho-window-count",
        type=int,
        default=0,
        help=(
            "Abstain the guarded density target unless the chosen guard retained "
            "below-rho evidence in at least this many prior windows."
        ),
    )
    parser.add_argument(
        "--guard-candidates",
        default=",".join(GUARDS.keys()),
        help="Comma-separated public guard names to score on prior windows.",
    )
    parser.add_argument(
        "--extra-density-guard-targets",
        default="",
        help=(
            "Comma-separated targets whose guarded density branch should be "
            "included as an extra fallback even when the target-aware route chooser selected strict."
        ),
    )
    parser.add_argument(
        "--extra-density-guard",
        default="",
        help=(
            "Public guard to apply to --extra-density-guard-targets. "
            "Defaults to the selected --guard-target density guard."
        ),
    )
    parser.add_argument(
        "--train-route-sources",
        default="",
        help=(
            "Optional comma-separated graph route source paths/globs for prior "
            "windows. Labels default to each source window label unless passed as label=path."
        ),
    )
    parser.add_argument(
        "--holdout-route-source",
        default="",
        help=(
            "Optional graph route source path/glob for the holdout product rows. "
            "When one source is provided its window label is used for holdout graph features."
        ),
    )
    parser.add_argument(
        "--holdout-route-label",
        default="",
        help="Optional explicit label to join holdout product rows to graph route features.",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    guard_names = [
        name.strip()
        for name in args.guard_candidates.split(",")
        if name.strip()
    ]
    unknown = [name for name in guard_names if name not in GUARDS]
    if unknown:
        raise ValueError(f"unknown guard candidates: {unknown}")
    if args.strict_guard not in GUARDS:
        raise ValueError(f"unknown strict guard: {args.strict_guard}")
    strict_guard_candidate_names = [
        name.strip()
        for name in args.strict_guard_candidates.split(",")
        if name.strip()
    ]
    unknown = [name for name in strict_guard_candidate_names if name not in GUARDS]
    if unknown:
        raise ValueError(f"unknown strict guard candidates: {unknown}")
    strict_fallback_guard = args.strict_fallback_guard or args.strict_guard
    if strict_fallback_guard not in GUARDS:
        raise ValueError(f"unknown strict fallback guard: {strict_fallback_guard}")
    if args.extra_density_guard and args.extra_density_guard not in GUARDS:
        raise ValueError(f"unknown extra density guard: {args.extra_density_guard}")
    strict_guard_targets = {
        target.strip()
        for target in args.strict_guard_targets.split(",")
        if target.strip()
    }
    extra_density_guard_targets = {
        target.strip()
        for target in args.extra_density_guard_targets.split(",")
        if target.strip()
    }
    train_route_sources = parse_route_sources(args.train_route_sources)
    holdout_route_sources = parse_route_sources(args.holdout_route_source)
    graph_features = route_feature_index([*train_route_sources, *holdout_route_sources])
    holdout_route_label = args.holdout_route_label
    if not holdout_route_label and len(holdout_route_sources) == 1:
        holdout_route_label = holdout_route_sources[0][0]

    train_strict = target_aware.parse_labeled_paths(args.train_strict_products)
    train_density = target_aware.parse_labeled_paths(args.train_density_products)
    route_metrics = [
        target_aware.target_metrics(STRICT_ROUTE, train_strict),
        target_aware.target_metrics(TARGET_DENSITY_ROUTE, train_density),
    ]
    target_routes = target_aware.choose_target_routes(route_metrics, args.fallback_route)
    guard_metrics = evaluate_guards(
        guard_names,
        train_density,
        args.guard_target,
        graph_features,
    )
    guard_choice = choose_guard(guard_metrics, args.fallback_guard, args.guard_score_mode)
    guard_name = guard_choice["selected_guard"]
    guard_threshold_passes, guard_thresholds = guard_passes_prior_thresholds(
        guard_choice,
        threshold_float(args.guard_min_prior_precision),
        threshold_float(args.guard_max_prior_noise_per_below_rho),
        max(0, args.guard_min_prior_below_rho_window_count),
    )
    strict_guard_choices: dict[str, Any] = {}
    strict_guard_thresholds: dict[str, Any] = {}
    strict_guard_names_by_target: dict[str, str] = {}
    strict_guard_enabled_by_target: dict[str, bool] = {}
    if strict_guard_candidate_names and strict_guard_targets:
        for strict_target in sorted(strict_guard_targets):
            target_guard_metrics = evaluate_guards(
                strict_guard_candidate_names,
                train_strict,
                strict_target,
                graph_features,
            )
            target_guard_choice = choose_guard(
                target_guard_metrics,
                strict_fallback_guard,
                args.strict_guard_score_mode,
            )
            target_guard_passes, target_guard_thresholds = guard_passes_prior_thresholds(
                target_guard_choice,
                threshold_float(args.strict_guard_min_prior_precision),
                threshold_float(args.strict_guard_max_prior_noise_per_below_rho),
                max(0, args.strict_guard_min_prior_below_rho_window_count),
            )
            strict_guard_choices[strict_target] = target_guard_choice
            strict_guard_thresholds[strict_target] = target_guard_thresholds
            strict_guard_names_by_target[strict_target] = str(
                target_guard_choice.get("selected_guard")
            )
            strict_guard_enabled_by_target[strict_target] = target_guard_passes
    else:
        for strict_target in sorted(strict_guard_targets):
            strict_guard_names_by_target[strict_target] = args.strict_guard
            strict_guard_enabled_by_target[strict_target] = True

    strict_product = target_aware.load_json(args.holdout_strict_product)
    density_product = target_aware.load_json(args.holdout_density_product)
    low_prefix = target_aware.load_json(args.holdout_low_prefix)
    strict_rows, strict_guard_application = guarded_strict_cases(
        strict_product,
        target_routes,
        strict_guard_targets,
        args.strict_guard,
        strict_guard_names_by_target,
        strict_guard_enabled_by_target,
        holdout_route_label,
        graph_features,
    )
    density_rows, guard_application = guarded_density_cases(
        density_product,
        target_routes,
        args.guard_target,
        guard_name,
        enable_density_branch=guard_threshold_passes,
        holdout_label=holdout_route_label,
        graph_features=graph_features,
        extra_density_guard_targets=extra_density_guard_targets,
        extra_density_guard_name=args.extra_density_guard,
    )
    low_rows = [] if args.disable_low_prefix else split_summary.selected_low_prefix_rows(low_prefix)
    rows = strict_rows + density_rows + low_rows
    summary = split_summary.summarize(rows)
    summary["guarded_density_rejected_count"] = guard_application[
        "rejected_density_product_case_count"
    ]
    summary["guarded_density_abstained_count"] = guard_application[
        "abstained_density_product_case_count"
    ]
    summary["selected_guarded_density_route_count"] = dict(
        Counter(str(row.get("route")) for row in density_rows).most_common()
    )
    summary["guarded_strict_rejected_count"] = strict_guard_application[
        "rejected_strict_product_case_count"
    ]
    summary["guarded_strict_abstained_count"] = strict_guard_application[
        "abstained_strict_product_case_count"
    ]
    summary["selected_guarded_strict_route_count"] = dict(
        Counter(
            str(row.get("route"))
            for row in strict_rows
            if str(row.get("route")).startswith(f"{STRICT_ROUTE}:guarded:")
        ).most_common()
    )

    output = {
        "schema": "ecdlp.low_term_total2_fixed_leaf_guarded_target_aware_split_gate.v1",
        "method": "target_aware_prior_window_product_route_selector_with_public_density_hazard_guard",
        "training_routes": route_metrics,
        "target_routes": target_routes,
        "guard_choice": guard_choice,
        "guard_prior_thresholds": guard_thresholds,
        "strict_guard_choices": strict_guard_choices,
        "strict_guard_prior_thresholds": strict_guard_thresholds,
        "guard_application": guard_application,
        "strict_guard_application": strict_guard_application,
        "low_prefix_application": {
            "enabled": not args.disable_low_prefix,
            "selected_low_prefix_case_count": len(low_rows),
        },
        "holdout_sources": {
            "strict_product": str(args.holdout_strict_product),
            "density_product": str(args.holdout_density_product),
            "low_prefix": str(args.holdout_low_prefix),
            "extra_density_guard_targets": sorted(extra_density_guard_targets),
            "train_route_sources": [
                {"label": label, "path": str(path)}
                for label, path in train_route_sources
            ],
            "holdout_route_sources": [
                {"label": label, "path": str(path)}
                for label, path in holdout_route_sources
            ],
            "holdout_route_label": holdout_route_label,
        },
        "summary": summary,
        "selected_cases": rows,
        "honesty_boundary": [
            "The guarded target-aware route is a post-P237 diagnostic frozen from prior windows before the holdout block.",
            "Target route choices use prior-window target-specific product metrics.",
            "The density hazard guard uses public selector/top-k and selected-leaf sharing metrics only.",
            "Optional strict-route guards use the same public feature family, with optional graph route features only when route sources are supplied, and are disabled by default.",
            "Graph route features use first-edge route shape and endpoint-neighborhood counts; they do not use verifier labels, recovered roots, ranks, secrets, or below-rho labels.",
            "Guard scoring uses prior-window verifier outcomes; holdout verifier rank, derived secret, and below-rho status are measured after selection.",
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
                "guard_choice": guard_choice,
                "strict_guard_choices": strict_guard_choices,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
