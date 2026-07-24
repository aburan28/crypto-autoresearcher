#!/usr/bin/env python3
"""P900 public prefilter/ordering audit over the P899 source stream."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_p899_source_generator_axis_stop_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p900_public_prefilter_ordering_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p900_public_prefilter_ordering_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p900_public_prefilter_ordering_audit.v1"
TARGET = "22050.cf1@11731"
POLICY = "leaf_b"
STRICT_TARGET_OPS = 136


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def row_salt(row_key: str) -> int:
    match = re.search(r"salt(\d+)$", str(row_key))
    return int(match.group(1)) if match else -1


def selector_group(selector: str) -> str:
    text = str(selector)
    if "low_leaf_index" in text:
        return "low_leaf"
    if "hybrid_support_monic_b" in text:
        return "hybrid"
    if "low_term_support" in text:
        return "low_term"
    return "other"


def compact_case(item: dict[str, Any]) -> dict[str, Any]:
    case = item.get("case") or {}
    row_leaf_keys = case.get("row_leaf_keys") or []
    leaves = [int_value(leaf) for row in row_leaf_keys for leaf in row.get("leaf_indices") or []]
    salts = [row_salt(str(row.get("row_key"))) for row in row_leaf_keys]
    source_ops = float_value(case.get("ops_over_rho"))
    return {
        "artifact_ord": int_value(case.get("source_stream_ordinal")),
        "concrete_union_dedup_ops": int_value(item.get("concrete_union_dedup_ops")),
        "concrete_union_dedup_ops_over_rho": item.get("concrete_union_dedup_ops_over_rho"),
        "leaf_signature": "/".join(str(leaf) for leaf in leaves),
        "policy": item.get("policy"),
        "public_key_verified": bool(case.get("public_key_verified")),
        "reconstructed": bool(item.get("reconstructed")),
        "rho_estimate": int_value(item.get("rho_estimate"), 137),
        "row_leaf_keys": row_leaf_keys,
        "row_salts": salts,
        "salt_gap": abs(salts[0] - salts[1]) if len(salts) == 2 else None,
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "selector": str(case.get("selector")),
        "selector_group": selector_group(str(case.get("selector"))),
        "source_case_cost_ops": int_value(item.get("source_case_cost_ops"), 1),
        "source_index": int_value(case.get("source_index")),
        "source_ops_over_rho": source_ops,
        "source_ops_bucket": round(source_ops, 2),
        "strict_below_rho": bool(item.get("strict_below_rho")),
        "target": str(case.get("target")),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
    }


def source_cases(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        compact_case(item)
        for item in payload.get("evaluated_policy_cases") or []
        if item.get("policy") == POLICY and (item.get("case") or {}).get("target") == TARGET
    ]
    return sorted(rows, key=lambda row: (row["artifact_ord"], row["selector"]))


def distinct_values(rows: list[dict[str, Any]], field: str) -> list[Any]:
    return sorted({row.get(field) for row in rows}, key=lambda value: str(value))


def filter_specs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [
        {"name": "all_artifact_order"},
        {
            "leaf_signature": "19/19",
            "name": "leaf19_only",
        },
        {
            "leaf_signature": "19/19",
            "name": "leaf19_top4",
            "top_k": 4,
        },
        {
            "leaf_signature": "19/19",
            "name": "leaf19_top4_low_leaf_or_hybrid",
            "selector_groups": ["hybrid", "low_leaf"],
            "top_k": 4,
        },
        {
            "leaf_signature": "19/19",
            "name": "leaf19_top4_low_leaf_or_hybrid_source_ops_ge_0p70",
            "selector_groups": ["hybrid", "low_leaf"],
            "source_ops_min": 0.70,
            "top_k": 4,
        },
        {
            "leaf_signature": "19/19",
            "name": "leaf19_top4_low_leaf_or_hybrid_source_ops_ge_0p70_salt_gap_ge5",
            "salt_gap_min": 5,
            "selector_groups": ["hybrid", "low_leaf"],
            "source_ops_min": 0.70,
            "top_k": 4,
        },
    ]
    for selector in distinct_values(rows, "selector"):
        if selector in (None, "None"):
            continue
        specs.append(
            {
                "leaf_signature": "19/19",
                "name": f"leaf19_top4_selector_{selector}",
                "selector": selector,
                "top_k": 4,
            }
        )
        specs.append(
            {
                "leaf_signature": "19/19",
                "name": f"leaf19_top4_selector_{selector}_source_ops_ge_0p70",
                "selector": selector,
                "source_ops_min": 0.70,
                "top_k": 4,
            }
        )
    for threshold in (0.63, 0.66, 0.69, 0.70, 0.71):
        specs.append(
            {
                "leaf_signature": "19/19",
                "name": f"leaf19_top4_any_selector_source_ops_ge_{str(threshold).replace('.', 'p')}",
                "source_ops_min": threshold,
                "top_k": 4,
            }
        )
    # Deduplicate by JSON representation while preserving order.
    out = []
    seen: set[str] = set()
    for spec in specs:
        key = json.dumps(spec, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(spec)
    return out


def matches(row: dict[str, Any], spec: dict[str, Any]) -> bool:
    if spec.get("leaf_signature") is not None and row.get("leaf_signature") != spec.get("leaf_signature"):
        return False
    if spec.get("top_k") is not None and int_value(row.get("top_k")) != int_value(spec.get("top_k")):
        return False
    if spec.get("selector") is not None and row.get("selector") != spec.get("selector"):
        return False
    groups = spec.get("selector_groups")
    if groups is not None and row.get("selector_group") not in set(groups):
        return False
    if spec.get("source_ops_min") is not None and float_value(row.get("source_ops_over_rho")) < float_value(spec.get("source_ops_min")):
        return False
    if spec.get("source_ops_max") is not None and float_value(row.get("source_ops_over_rho")) > float_value(spec.get("source_ops_max")):
        return False
    if spec.get("salt_gap_min") is not None and int_value(row.get("salt_gap"), -1) < int_value(spec.get("salt_gap_min")):
        return False
    if spec.get("salt_gap") is not None and int_value(row.get("salt_gap"), -1) != int_value(spec.get("salt_gap")):
        return False
    return True


def stop_is_good(row: dict[str, Any]) -> bool:
    return bool(row.get("strict_below_rho") and row.get("public_key_verified"))


def compact_stop(row: dict[str, Any] | None, total_cost: int | None = None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "artifact_ord": row.get("artifact_ord"),
        "concrete_union_dedup_ops": row.get("concrete_union_dedup_ops"),
        "concrete_union_dedup_ops_over_rho": row.get("concrete_union_dedup_ops_over_rho"),
        "leaf_signature": row.get("leaf_signature"),
        "public_key_verified": row.get("public_key_verified"),
        "row_salts": row.get("row_salts"),
        "salt_gap": row.get("salt_gap"),
        "selector": row.get("selector"),
        "selector_group": row.get("selector_group"),
        "source_case_cost_ops": row.get("source_case_cost_ops"),
        "source_index": row.get("source_index"),
        "source_ops_over_rho": row.get("source_ops_over_rho"),
        "strict_below_rho": row.get("strict_below_rho"),
        "top_k": row.get("top_k"),
        "total_cost_ops": total_cost,
        "transfer_index": row.get("transfer_index"),
    }


def evaluate_artifact_order(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    screen_cost = 0
    remat_cost = 0
    selected_before_stop = 0
    false_selected_before_stop = 0
    first_selected = None
    first_strict = None
    for row in rows:
        screen_cost += 1
        if not matches(row, spec):
            continue
        selected_before_stop += 1
        remat_cost += int_value(row.get("source_case_cost_ops"), 1)
        if first_selected is None:
            first_selected = row
        if row.get("strict_below_rho"):
            first_strict = row
            break
        false_selected_before_stop += 1
    total = screen_cost + remat_cost
    return {
        "false_selected_before_stop": false_selected_before_stop,
        "first_selected": compact_stop(first_selected),
        "first_strict_stop": compact_stop(first_strict, total),
        "first_strict_stop_good": stop_is_good(first_strict or {}),
        "mode": "artifact_order_screened",
        "rematerialization_cost_ops": remat_cost,
        "screen_cost_ops": screen_cost,
        "selected_before_stop_count": selected_before_stop,
        "total_cost_ops": total,
        "total_cost_over_rho": ratio(total, STRICT_TARGET_OPS + 1),
        "total_cost_within_strict_target": bool(first_strict and stop_is_good(first_strict) and total <= STRICT_TARGET_OPS),
    }


def evaluate_priority(rows: list[dict[str, Any]], spec: dict[str, Any], order: str) -> dict[str, Any]:
    selected = [row for row in rows if matches(row, spec)]
    if order == "artifact":
        ordered = sorted(selected, key=lambda row: (row["artifact_ord"], row["selector"]))
    elif order == "source_ops_desc_artifact":
        ordered = sorted(selected, key=lambda row: (-float_value(row["source_ops_over_rho"]), row["artifact_ord"], row["selector"]))
    elif order == "salt_gap_desc_artifact":
        ordered = sorted(selected, key=lambda row: (-int_value(row.get("salt_gap"), -1), row["artifact_ord"], row["selector"]))
    else:
        raise ValueError(f"unknown priority order: {order}")
    schedule_cost = 0
    remat_cost = 0
    false_selected_before_stop = 0
    first_strict = None
    first_selected = ordered[0] if ordered else None
    for row in ordered:
        schedule_cost += 1
        remat_cost += int_value(row.get("source_case_cost_ops"), 1)
        if row.get("strict_below_rho"):
            first_strict = row
            break
        false_selected_before_stop += 1
    total = schedule_cost + remat_cost
    return {
        "false_selected_before_stop": false_selected_before_stop,
        "first_selected": compact_stop(first_selected),
        "first_strict_stop": compact_stop(first_strict, total),
        "first_strict_stop_good": stop_is_good(first_strict or {}),
        "mode": f"priority_{order}",
        "rematerialization_cost_ops": remat_cost,
        "schedule_cost_ops": schedule_cost,
        "selected_before_stop_count": schedule_cost,
        "selected_count": len(selected),
        "total_cost_ops": total,
        "total_cost_over_rho": ratio(total, STRICT_TARGET_OPS + 1),
        "total_cost_within_strict_target": bool(first_strict and stop_is_good(first_strict) and total <= STRICT_TARGET_OPS),
    }


def evaluate_spec(rows: list[dict[str, Any]], spec: dict[str, Any]) -> dict[str, Any]:
    selected = [row for row in rows if matches(row, spec)]
    artifact = evaluate_artifact_order(rows, spec)
    priority = [
        evaluate_priority(rows, spec, "artifact"),
        evaluate_priority(rows, spec, "source_ops_desc_artifact"),
        evaluate_priority(rows, spec, "salt_gap_desc_artifact"),
    ]
    best_priority = min(priority, key=lambda item: item["total_cost_ops"] if item.get("first_strict_stop") else 10**18)
    return {
        "artifact_order": artifact,
        "best_priority": best_priority,
        "priority_orders": priority,
        "selected_count": len(selected),
        "selected_summary": {
            "strict_count": len([row for row in selected if row.get("strict_below_rho")]),
            "verified_count": len([row for row in selected if row.get("public_key_verified")]),
            "verified_strict_count": len([row for row in selected if stop_is_good(row)]),
        },
        "spec": spec,
    }


def determine_claim(evaluated: list[dict[str, Any]]) -> str:
    if any(item["artifact_order"].get("total_cost_within_strict_target") for item in evaluated):
        return "P900_PUBLIC_PREFILTER_ARTIFACT_ORDER_BEATS_RHO"
    if any(item["best_priority"].get("total_cost_within_strict_target") for item in evaluated):
        return "P900_DIAGNOSTIC_PRIORITY_PREFILTER_REACHES_RHO_NEEDS_GENERATOR"
    if any((item["best_priority"].get("first_strict_stop") or {}).get("public_key_verified") for item in evaluated):
        return "NEGATIVE_RESULT_P900_PREFILTER_FINDS_STRICT_BUT_COST_ABOVE_RHO"
    return "NEGATIVE_RESULT_P900_PREFILTER_MISSES_VERIFIED_STRICT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_json(args.source)
    rows = source_cases(payload)
    evaluated = [evaluate_spec(rows, spec) for spec in filter_specs(rows)]
    full_passes = [item for item in evaluated if item["artifact_order"].get("total_cost_within_strict_target")]
    priority_passes = [item for item in evaluated if item["best_priority"].get("total_cost_within_strict_target")]
    strict_finders = [item for item in evaluated if item["best_priority"].get("first_strict_stop")]
    best_artifact = min(
        [item for item in evaluated if item["artifact_order"].get("first_strict_stop")],
        key=lambda item: item["artifact_order"]["total_cost_ops"],
        default=None,
    )
    best_priority = min(
        [item for item in evaluated if item["best_priority"].get("first_strict_stop")],
        key=lambda item: item["best_priority"]["total_cost_ops"],
        default=None,
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source": str(args.source),
        },
        "claim_status": determine_claim(evaluated),
        "created_at": now_iso(),
        "evaluated_prefilters": evaluated,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-FEATURE AUDIT: filters use cheap case metadata from P899, not verifier labels.",
            "DIAGNOSTIC IF PRIORITY-ONLY: priority wins assume a future generator can enumerate the feature family directly.",
            "POLLARD-RHO BOUNDARY: this is a source prefilter audit, not a complete ECDLP algorithm.",
        ],
        "method": "p900_public_prefilter_ordering_audit",
        "parameters": {
            "policy": POLICY,
            "source_case_count": len(rows),
            "strict_target_ops": STRICT_TARGET_OPS,
            "target": TARGET,
        },
        "schema": SCHEMA,
        "summary": {
            "best_artifact_order_prefilter": best_artifact,
            "best_priority_prefilter": best_priority,
            "full_source_pass_count": len(full_passes),
            "prefilter_count": len(evaluated),
            "priority_diagnostic_pass_count": len(priority_passes),
            "strict_finder_count": len(strict_finders),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
