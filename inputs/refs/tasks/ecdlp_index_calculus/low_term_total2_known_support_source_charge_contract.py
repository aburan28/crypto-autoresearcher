#!/usr/bin/env python3
"""Source-pressure contract for known-support one-relation descent.

The known-support preselector probe showed that the public predicate
``selected_support_size <= 10`` can predict held-out one-relation recoveries
in the direct bridge.  This contract asks the next accounting question:
how much source generation has to be charged before direct verification?

This is still not a shared-product conversion.  It reports both a full-artifact
negative-control charge and a narrower scheduled charge that assumes a future
collector generates only the frozen target/selector family.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_known_support_preselector_probe as support_probe


WINDOW_RE = re.compile(r"_(\d{4})_(\d{4})_")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def window_label(path: str | Path) -> str:
    match = WINDOW_RE.search(Path(path).name)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return Path(path).stem


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def cert_key(cert: dict[str, Any]) -> tuple[str, int]:
    return (str(cert.get("_artifact")), int_value(cert.get("_artifact_offset")))


def training_paths(audit: dict[str, Any]) -> list[Path]:
    artifacts = audit.get("artifacts") if isinstance(audit.get("artifacts"), dict) else {}
    return [Path(item) for item in artifacts.get("certificates") or []]


def load_certificates(paths: list[Path]) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    for path in paths:
        payload = load_json(path)
        for offset, cert in enumerate(payload.get("certificates") or []):
            if not isinstance(cert, dict):
                continue
            item = dict(cert)
            item["_artifact"] = str(path)
            item["_artifact_offset"] = offset
            item["_window"] = window_label(path)
            certs.append(item)
    return certs


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0.0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def scout_counts(
    scout_paths: list[Path],
    target: str,
    selector: str,
    top_ks: set[int] | None,
) -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    support_size_histogram: dict[str, int] = defaultdict(int)
    for path in scout_paths:
        payload = load_json(path)
        label = window_label(path)
        reports = [report for report in payload.get("case_reports") or [] if isinstance(report, dict)]
        target_selector_reports = [
            report
            for report in reports
            if str(report.get("target")) == target and str(report.get("selector")) == selector
        ]
        if top_ks is None:
            target_selector_topk_reports = target_selector_reports
        else:
            target_selector_topk_reports = [
                report for report in target_selector_reports if int_value(report.get("top_k")) in top_ks
            ]
        for report in target_selector_reports:
            support_size = len({int_value(value) for value in report.get("selected_term_support") or []})
            support_size_histogram[str(support_size)] += 1
        counts[label] = {
            "full_artifact_source_case_count": len(reports),
            "target_selector_source_case_count": len(target_selector_reports),
            "target_selector_topk_source_case_count": len(target_selector_topk_reports),
        }
    return counts, dict(sorted(support_size_histogram.items(), key=lambda item: int(item[0])))


def split_items(
    items: list[dict[str, Any]],
    calibration_max_transfer: int,
    future_tail_min_transfer: int | None,
) -> dict[str, list[dict[str, Any]]]:
    splits = {
        "calibration": [item for item in items if int_value(item.get("transfer_index")) <= calibration_max_transfer],
        "validation": [item for item in items if int_value(item.get("transfer_index")) > calibration_max_transfer],
    }
    if future_tail_min_transfer is not None:
        splits["old_validation"] = [
            item
            for item in items
            if calibration_max_transfer < int_value(item.get("transfer_index")) <= future_tail_min_transfer
        ]
        splits["future_tail"] = [
            item for item in items if int_value(item.get("transfer_index")) > future_tail_min_transfer
        ]
    return splits


def transfer_key(item: dict[str, Any]) -> tuple[str, int]:
    return (str(item.get("target")), int_value(item.get("transfer_index")))


def evaluate_split(
    items: list[dict[str, Any]],
    source_counts: dict[str, dict[str, int]],
    support_limit: int,
    source_row_unit_ops: int,
) -> dict[str, Any]:
    selected_items = [
        item
        for item in items
        if len({int_value(value) for value in item.get("selected_support") or []}) <= support_limit
    ]
    matching_selected = [item for item in selected_items if item.get("is_matching_recovery")]
    all_matching = [item for item in items if item.get("is_matching_recovery")]
    selected_direct_costs = [
        float(item["direct_cost_over_rho"])
        for item in selected_items
        if item.get("direct_cost_over_rho") is not None
    ]
    windows = sorted({str(item.get("window")) for item in items if item.get("window")})
    rho_by_window: dict[str, int] = {}
    for item in items:
        label = str(item.get("window"))
        rho = int_value(item.get("rho"))
        if label and rho:
            rho_by_window[label] = rho

    def source_cost(mode: str) -> float:
        total = 0.0
        for label in windows:
            rho = rho_by_window.get(label)
            if not rho:
                continue
            total += (source_counts.get(label, {}).get(mode, 0) * source_row_unit_ops) / rho
        return total

    source_full = source_cost("full_artifact_source_case_count")
    source_target_selector = source_cost("target_selector_source_case_count")
    source_target_selector_topk = source_cost("target_selector_topk_source_case_count")
    direct_sum = sum(selected_direct_costs)
    matching_count = len(matching_selected)

    def per_matching(cost: float) -> float | None:
        if not matching_count:
            return None
        return round(cost / matching_count, 8)

    matching_transfers = {transfer_key(item) for item in matching_selected}
    total_matching_transfers = {transfer_key(item) for item in all_matching}
    return {
        "all_matching_recovery_count": len(all_matching),
        "direct_selected_cost_over_rho": stat(selected_direct_costs),
        "direct_selected_cost_per_matching_recovery_over_rho": per_matching(direct_sum),
        "full_artifact_source_case_cost_over_rho": round(source_full, 8),
        "full_artifact_source_plus_direct_cost_per_matching_recovery_over_rho": per_matching(
            source_full + direct_sum
        ),
        "matching_recovery_count": matching_count,
        "matching_transfer_count": len(matching_transfers),
        "precision": round(matching_count / len(selected_items), 8) if selected_items else None,
        "recall": round(matching_count / len(all_matching), 8) if all_matching else None,
        "selected_certificate_count": len(selected_items),
        "source_window_count": len(windows),
        "target_selector_source_case_cost_over_rho": round(source_target_selector, 8),
        "target_selector_source_plus_direct_cost_per_matching_recovery_over_rho": per_matching(
            source_target_selector + direct_sum
        ),
        "target_selector_topk_source_case_cost_over_rho": round(source_target_selector_topk, 8),
        "target_selector_topk_source_plus_direct_cost_per_matching_recovery_over_rho": per_matching(
            source_target_selector_topk + direct_sum
        ),
        "total_certificate_count": len(items),
        "total_matching_transfer_count": len(total_matching_transfers),
        "transfer_recall": (
            round(len(matching_transfers) / len(total_matching_transfers), 8)
            if total_matching_transfers
            else None
        ),
    }


def add_training_amortization(metrics: dict[str, Any], training_cost: float) -> dict[str, Any]:
    result = {}
    for key, value in metrics.items():
        if not key.endswith("_cost_per_matching_recovery_over_rho") or not isinstance(value, (int, float)):
            continue
        result[key.replace("_cost_per_matching_recovery_over_rho", "_many_target_break_even_count")] = (
            round(training_cost / (1.0 - float(value)), 8) if float(value) < 1.0 else None
        )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--training-audit", required=True)
    parser.add_argument("--holdout-descent", required=True)
    parser.add_argument("--holdout-certificates", required=True)
    parser.add_argument("--scouts", required=True)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k-list", default="")
    parser.add_argument("--support-size-limit", type=int, default=10)
    parser.add_argument("--source-row-unit-ops", type=int, default=1)
    parser.add_argument("--calibration-max-transfer", type=int, default=2527)
    parser.add_argument("--future-tail-min-transfer", type=int)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cert_paths = support_probe.parse_paths(args.holdout_certificates)
    scout_paths = support_probe.parse_paths(args.scouts)
    top_ks = {int(item.strip()) for item in args.top_k_list.split(",") if item.strip()} or None

    descent = load_json(Path(args.holdout_descent))
    certs = load_certificates(cert_paths)
    annotated = support_probe.annotate_items(certs, descent, scout_paths)
    certs_by_key = {cert_key(cert): cert for cert in certs}
    for item in annotated:
        key = tuple(item.get("cert_key") or ())
        cert = certs_by_key.get((str(key[0]), int_value(key[1]))) if len(key) == 2 else None
        if cert is None:
            continue
        item["rho"] = int_value(selected(cert).get("rho"))
        item["window"] = str(cert.get("_window"))

    filtered_items = [
        item
        for item in annotated
        if str(item.get("target")) == args.target and str(item.get("selector")) == args.selector
    ]
    source_counts, support_size_histogram = scout_counts(scout_paths, args.target, args.selector, top_ks)

    training_audit = load_json(Path(args.training_audit))
    training_certs = load_certificates(training_paths(training_audit))
    training_direct_costs = [
        value
        for cert in training_certs
        if (value := float_value(selected(cert).get("direct_ops_over_rho"))) is not None
    ]
    training_direct_sum = sum(training_direct_costs)

    split_results = {}
    for name, split in split_items(filtered_items, args.calibration_max_transfer, args.future_tail_min_transfer).items():
        metrics = evaluate_split(split, source_counts, args.support_size_limit, args.source_row_unit_ops)
        split_results[name] = {
            **metrics,
            "training_amortization": add_training_amortization(metrics, training_direct_sum),
        }

    validation = split_results.get("validation", {})
    candidate_cost = validation.get("target_selector_source_plus_direct_cost_per_matching_recovery_over_rho")
    claim_status = (
        "KNOWN_SUPPORT_SOURCE_CHARGED_SCHEDULED_BELOW_RHO_SIGNAL"
        if isinstance(candidate_cost, (int, float)) and candidate_cost < 1.0
        else "KNOWN_SUPPORT_SOURCE_CHARGED_SCHEDULED_NEEDS_GAIN"
    )
    payload = {
        "artifacts": {
            "holdout_certificates": [str(path) for path in cert_paths],
            "holdout_descent": args.holdout_descent,
            "scouts": [str(path) for path in scout_paths],
            "training_audit": args.training_audit,
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": {
            "evidence": "TOY-EVIDENCE / MODEL-BOUND / HEURISTIC-COST",
            "not_claimed": [
                "shared-product amortized collector",
                "complete faster-than-rho prime-field ECDLP algorithm",
                "deployment-relevant break",
            ],
            "scope": "Source-pressure accounting for a frozen direct-source selected-support gate. Full-artifact source charge is a negative control; target-selector charge assumes a future public scheduled generator.",
        },
        "parameters": {
            "calibration_max_transfer": args.calibration_max_transfer,
            "future_tail_min_transfer": args.future_tail_min_transfer,
            "selector": args.selector,
            "source_row_unit_ops": args.source_row_unit_ops,
            "support_size_limit": args.support_size_limit,
            "target": args.target,
            "top_k_list": sorted(top_ks) if top_ks is not None else None,
        },
        "schema": "ecdlp.low_term_total2_known_support_source_charge_contract.v1",
        "source_counts_by_window": source_counts,
        "split_results": split_results,
        "support_size_histogram_for_target_selector": support_size_histogram,
        "training_cost": {
            "direct_ops_over_rho": stat(training_direct_costs),
            "direct_sum_over_rho": round(training_direct_sum, 8),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": claim_status, "validation": validation}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
