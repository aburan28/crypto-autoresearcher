#!/usr/bin/env python3
"""Audit source-row charged public stops for the low-term top-k7 route.

The public stop-rule collector charges only rejected prefilter screens plus the
selected shared-product row. This probe moves one accounting gate earlier for
the current strict-product artifact stream: it charges every strict-product
source row generated before the public stop, then charges rejected public
screens and the selected shared-product replay.

This is not a Sage/QR factorization source replay. It is a source-row charge for
the fixed-leaf strict-product stream used by the current low-term top-k7
candidate.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def window_label(path: Path) -> str:
    match = re.search(r"(\d{4})_(\d{4})", path.name)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return path.stem


def row_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("target"),
        int_value(row.get("transfer_index")),
        row.get("selector"),
        int_value(row.get("top_k")),
        tuple(row.get("row_keys") or []),
    )


def public_screen_ops(row: dict[str, Any]) -> int:
    metrics = row.get("gate_metrics") or {}
    return int_value(metrics.get("direct_selected_leaf_check_ops")) + int_value(
        metrics.get("direct_selected_hit_root_ops")
    )


def top_k_charge_allowed(row: dict[str, Any], top_k_max_charge: dict[int, int]) -> bool:
    limit = top_k_max_charge.get(int_value(row.get("top_k")))
    if limit is None:
        return True
    metrics = row.get("gate_metrics") or {}
    return int_value(metrics.get("shared_signature_root_charge"), 10**9) <= limit


def public_prefilter(
    row: dict[str, Any],
    target: str,
    selector: str,
    top_ks: set[int],
    top_k_max_charge: dict[int, int],
) -> bool:
    return (
        bool(row.get("public_product_gate_selected"))
        and row.get("target") == target
        and row.get("selector") == selector
        and int_value(row.get("top_k")) in top_ks
        and top_k_charge_allowed(row, top_k_max_charge)
    )


def stop_predicate(row: dict[str, Any], min_root_saved: int, min_hit_root_ops: int) -> bool:
    metrics = row.get("gate_metrics") or {}
    return (
        int_value(metrics.get("shared_signature_root_saved_ops")) >= min_root_saved
        and int_value(metrics.get("direct_selected_hit_root_ops")) >= min_hit_root_ops
    )


def compact_row(index: int, row: dict[str, Any], schedule_index: int | None = None) -> dict[str, Any]:
    metrics = row.get("gate_metrics") or {}
    compact = {
        "artifact_index": index,
        "direct_ops_over_rho": row.get("direct_verifier_replay_ops_over_rho"),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "public_key_verified": bool(row.get("shared_product_union_public_key_verified")),
        "rank": int_value(row.get("shared_product_union_rank")),
        "relation_count": int_value(row.get("shared_product_union_relation_count")),
        "rho": int_value(row.get("rho")),
        "root_saved_ops": int_value(metrics.get("shared_signature_root_saved_ops")),
        "row_key": row_key(row),
        "row_keys": row.get("row_keys") or [],
        "screen_ops": public_screen_ops(row),
        "secret": row.get("shared_product_union_derived_secret"),
        "selector": row.get("selector"),
        "shared_ops": int_value(row.get("shared_product_ledger_ops")),
        "shared_ops_over_rho": row.get("shared_product_ledger_ops_over_rho"),
        "target": row.get("target"),
        "top_k": int_value(row.get("top_k")),
        "transfer_index": int_value(row.get("transfer_index")),
    }
    if schedule_index is not None:
        compact["schedule_index"] = schedule_index
    return compact


def target_selector_topk_match(
    row: dict[str, Any],
    target: str,
    selector: str,
    top_ks: set[int],
    top_k_max_charge: dict[int, int],
) -> bool:
    return (
        row.get("target") == target
        and row.get("selector") == selector
        and int_value(row.get("top_k")) in top_ks
        and top_k_charge_allowed(row, top_k_max_charge)
    )


def row_order_key(
    row_order: str,
    index: int,
    row: dict[str, Any],
    target: str,
    selector: str,
    top_ks: set[int],
    top_k_max_charge: dict[int, int],
) -> tuple[Any, ...]:
    metrics = row.get("gate_metrics") or {}
    if row_order == "artifact":
        return (index,)
    if row_order == "target_selector_topk_first":
        return (
            0 if target_selector_topk_match(row, target, selector, top_ks, top_k_max_charge) else 1,
            index,
        )
    if row_order == "target_selector_topk_root_saved_first":
        return (
            0 if target_selector_topk_match(row, target, selector, top_ks, top_k_max_charge) else 1,
            -int_value(metrics.get("shared_signature_root_saved_ops")),
            -int_value(metrics.get("direct_selected_hit_root_ops")),
            int_value(metrics.get("shared_signature_root_charge"), 10**9),
            index,
        )
    if row_order == "public_prefilter_first":
        return (
            0 if public_prefilter(row, target, selector, top_ks, top_k_max_charge) else 1,
            index,
        )
    raise ValueError(f"unsupported row order: {row_order}")


def source_summary(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = load_json(path)
    params = data.get("parameters") if isinstance(data.get("parameters"), dict) else {}
    summaries = (data.get("summary") or {}).get("policy_summaries") or []
    first = summaries[0] if summaries else {}
    return {
        "artifact": str(path),
        "fixed_row_selectors": params.get("fixed_row_selectors"),
        "leaf_selectors": params.get("leaf_selectors"),
        "stress_leaf_below_rho": int_value(first.get("stress_leaf_below_rho")),
        "stress_leaf_verified": int_value(first.get("stress_leaf_verified")),
        "stress_row_below_rho": int_value(first.get("stress_row_below_rho")),
        "stress_row_verified": int_value(first.get("stress_row_verified")),
        "stress_transfer_indices": params.get("stress_transfer_indices"),
        "top_k_grid": params.get("top_k_grid"),
    }


def audit_artifact(
    strict_path: Path,
    source_path: Path | None,
    target: str,
    selector: str,
    top_ks: set[int],
    top_k_max_charge: dict[int, int],
    min_root_saved: int,
    min_hit_root_ops: int,
    source_row_unit_ops: int,
    row_order: str,
) -> dict[str, Any]:
    payload = load_json(strict_path)
    cases = [row for row in payload.get("cases") or [] if isinstance(row, dict)]
    ordered_cases = list(enumerate(cases))
    ordered_cases.sort(
        key=lambda item: row_order_key(
            row_order,
            item[0],
            item[1],
            target=target,
            selector=selector,
            top_ks=top_ks,
            top_k_max_charge=top_k_max_charge,
        )
    )
    rejected_before_stop: list[dict[str, Any]] = []
    selected: tuple[int, int, dict[str, Any]] | None = None
    generated_source_row_count = 0
    prefilter_before_stop_count = 0

    for schedule_index, (index, row) in enumerate(ordered_cases):
        generated_source_row_count += 1
        if not public_prefilter(row, target, selector, top_ks, top_k_max_charge):
            continue
        prefilter_before_stop_count += 1
        if stop_predicate(row, min_root_saved, min_hit_root_ops):
            selected = (index, schedule_index, row)
            break
        rejected_before_stop.append(compact_row(index, row, schedule_index))

    source_row_generation_ops = generated_source_row_count * source_row_unit_ops
    rejected_screen_ops = sum(row["screen_ops"] for row in rejected_before_stop)

    if selected is None:
        return {
            "artifact": str(strict_path),
            "claim_status": "SOURCE_ROW_CHARGED_PUBLIC_STOP_ABSTAINS",
            "generated_source_row_count": generated_source_row_count,
            "prefilter_before_stop_count": prefilter_before_stop_count,
            "rejected_before_stop": rejected_before_stop,
            "rejected_before_stop_count": len(rejected_before_stop),
            "rejected_screen_ops_before_stop": rejected_screen_ops,
            "selected": None,
            "source": source_summary(source_path),
            "source_row_generation_ops": source_row_generation_ops,
            "source_row_unit_ops": source_row_unit_ops,
            "strict_case_count": len(cases),
            "window": window_label(strict_path),
            "row_order": row_order,
        }

    selected_index, selected_schedule_index, selected_row = selected
    selected_compact = compact_row(selected_index, selected_row, selected_schedule_index)
    selected_shared_ops = selected_compact["shared_ops"]
    rho = selected_compact["rho"]
    source_charged_total_ops = source_row_generation_ops + rejected_screen_ops + selected_shared_ops
    source_charged_passes = (
        selected_compact["public_key_verified"]
        and source_charged_total_ops > 0
        and rho > 0
        and source_charged_total_ops < rho
    )
    selected_only_passes = (
        selected_compact["public_key_verified"]
        and selected_shared_ops > 0
        and rho > 0
        and selected_shared_ops < rho
    )
    return {
        "artifact": str(strict_path),
        "claim_status": (
            "SOURCE_ROW_CHARGED_PUBLIC_STOP_BELOW_RHO"
            if source_charged_passes
            else "SOURCE_ROW_CHARGED_PUBLIC_STOP_SELECTED_ONLY_BELOW_RHO"
            if selected_only_passes
            else "SOURCE_ROW_CHARGED_PUBLIC_STOP_NEGATIVE"
        ),
        "generated_source_row_count": generated_source_row_count,
        "prefilter_before_stop_count": prefilter_before_stop_count,
        "rejected_before_stop": rejected_before_stop,
        "rejected_before_stop_count": len(rejected_before_stop),
        "rejected_screen_ops_before_stop": rejected_screen_ops,
        "selected": selected_compact,
        "selected_only_passes_rho": selected_only_passes,
        "selected_shared_ops": selected_shared_ops,
        "source": source_summary(source_path),
        "source_charged_total_ops": source_charged_total_ops,
        "source_charged_total_ops_over_rho": ratio(source_charged_total_ops, rho),
        "source_charged_total_passes_rho": source_charged_passes,
        "source_row_generation_ops": source_row_generation_ops,
        "source_row_unit_ops": source_row_unit_ops,
        "strict_case_count": len(cases),
        "window": window_label(strict_path),
        "row_order": row_order,
    }


def parse_mapping(raw: str | None) -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    if not raw:
        return mapping
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            path = Path(item)
            mapping[window_label(path)] = path
            continue
        label, path = item.split("=", 1)
        mapping[label.strip()] = Path(path.strip())
    return mapping


def parse_top_ks(top_k: int, top_k_list: str | None) -> set[int]:
    if not top_k_list:
        return {top_k}
    values = {int(item.strip()) for item in top_k_list.split(",") if item.strip()}
    if not values:
        raise ValueError("--top-k-list did not contain any integer values")
    return values


def parse_top_k_max_charge(raw: str | None) -> dict[int, int]:
    limits: dict[int, int] = {}
    if not raw:
        return limits
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError("--top-k-max-charge entries must look like TOPK=MAX_CHARGE")
        key, value = item.split("=", 1)
        limits[int(key.strip())] = int(value.strip())
    return limits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-products", required=True, help="Comma-separated strict product JSON artifacts")
    parser.add_argument(
        "--sources",
        help="Optional comma-separated source artifacts, either paths or window=path mappings",
    )
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_span_total10")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument(
        "--top-k-list",
        help="Optional comma-separated public top-k set. Defaults to the single --top-k value.",
    )
    parser.add_argument(
        "--top-k-max-charge",
        help="Optional comma-separated top-k charge limits, e.g. 16=2. Unlisted top-k values are unconstrained.",
    )
    parser.add_argument("--min-root-saved", type=int, default=1)
    parser.add_argument("--min-hit-root-ops", type=int, default=3)
    parser.add_argument("--source-row-unit-ops", type=int, default=1)
    parser.add_argument(
        "--row-order",
        choices=[
            "artifact",
            "target_selector_topk_first",
            "target_selector_topk_root_saved_first",
            "public_prefilter_first",
        ],
        default="artifact",
        help="Source-row schedule to audit. Non-artifact orders are diagnostic backtests and need fresh validation.",
    )
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    strict_paths = [Path(item) for item in args.strict_products.split(",") if item.strip()]
    source_map = parse_mapping(args.sources)
    top_ks = parse_top_ks(args.top_k, args.top_k_list)
    top_k_max_charge = parse_top_k_max_charge(args.top_k_max_charge)
    audits = []
    for strict_path in strict_paths:
        label = window_label(strict_path)
        audits.append(
            audit_artifact(
                strict_path,
                source_map.get(label),
                target=args.target,
                selector=args.selector,
                top_ks=top_ks,
                top_k_max_charge=top_k_max_charge,
                min_root_saved=args.min_root_saved,
                min_hit_root_ops=args.min_hit_root_ops,
                source_row_unit_ops=args.source_row_unit_ops,
                row_order=args.row_order,
            )
        )

    stopped = [audit for audit in audits if audit.get("selected")]
    source_below = [audit for audit in stopped if audit.get("source_charged_total_passes_rho")]
    selected_only = [audit for audit in stopped if audit.get("selected_only_passes_rho")]
    summary = {
        "abstained_count": sum(1 for audit in audits if not audit.get("selected")),
        "claim_status": (
            "SOURCE_ROW_CHARGED_PUBLIC_STOP_SWEEP_POSITIVE"
            if stopped and len(source_below) == len(stopped)
            else "SOURCE_ROW_CHARGED_PUBLIC_STOP_SWEEP_MIXED"
        ),
        "source_charged_below_rho_count": len(source_below),
        "selected_only_below_rho_count": len(selected_only),
        "stopped_count": len(stopped),
        "total_generated_source_row_count": sum(int_value(audit.get("generated_source_row_count")) for audit in audits),
        "total_source_row_generation_ops": sum(int_value(audit.get("source_row_generation_ops")) for audit in audits),
        "unverified_stop_count": sum(
            1
            for audit in stopped
            if not ((audit.get("selected") or {}).get("public_key_verified"))
        ),
        "verified_above_source_charged_rho_count": sum(
            1
            for audit in stopped
            if (audit.get("selected") or {}).get("public_key_verified")
            and not audit.get("source_charged_total_passes_rho")
        ),
        "window_count": len(audits),
    }
    payload = {
        "audits": audits,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source-row generation is charged as one operation per strict-product case generated before the public stop.",
            "PARTIAL: this charges the fixed-leaf strict-product source row stream; it is not a Sage/QR factorization source replay.",
            "DIAGNOSTIC: non-artifact row orders are public-schedule backtests and must be frozen before fresh validation.",
            "UNTESTED: target descent is not implemented.",
        ],
        "method": "low_term_total2_source_row_charge_stop_rule_collector",
        "parameters": {
            "min_hit_root_ops": args.min_hit_root_ops,
            "min_root_saved": args.min_root_saved,
            "row_order": args.row_order,
            "selector": args.selector,
            "source_row_unit_ops": args.source_row_unit_ops,
            "target": args.target,
            "top_k": args.top_k,
            "top_k_list": sorted(top_ks),
            "top_k_max_charge": {str(key): value for key, value in sorted(top_k_max_charge.items())},
        },
        "schema": "ecdlp.low_term_total2_source_row_charge_stop_rule_collector.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
