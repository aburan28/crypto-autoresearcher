#!/usr/bin/env python3
"""Audit a public stop rule for the low-term top-k7 shared-product route.

This is a narrower integrated-collection probe than the selected-row replay
artifacts. It scans public strict-product rows in artifact order, applies a
public prefilter, charges a small public screen for rows that fail the stop
predicate, and stops at the first row satisfying the predicate. The selected
row is then charged with the measured shared-product ledger from the existing
strict-product artifact.

It still does not charge one-process source generation or target descent.
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


def compact_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
    metrics = row.get("gate_metrics") or {}
    return {
        "artifact_index": index,
        "direct_ops_over_rho": row.get("direct_verifier_replay_ops_over_rho"),
        "hit_root_ops": int_value(metrics.get("direct_selected_hit_root_ops")),
        "public_key_verified": bool(row.get("shared_product_union_public_key_verified")),
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


def public_prefilter(row: dict[str, Any], target: str, selector: str, top_k: int) -> bool:
    return (
        bool(row.get("public_product_gate_selected"))
        and row.get("target") == target
        and row.get("selector") == selector
        and int_value(row.get("top_k")) == top_k
    )


def stop_predicate(row: dict[str, Any], min_root_saved: int, min_hit_root_ops: int) -> bool:
    metrics = row.get("gate_metrics") or {}
    return (
        int_value(metrics.get("shared_signature_root_saved_ops")) >= min_root_saved
        and int_value(metrics.get("direct_selected_hit_root_ops")) >= min_hit_root_ops
    )


def audit_artifact(
    path: Path,
    target: str,
    selector: str,
    top_k: int,
    min_root_saved: int,
    min_hit_root_ops: int,
) -> dict[str, Any]:
    payload = load_json(path)
    rows = [
        (index, row)
        for index, row in enumerate(payload.get("cases") or [])
        if public_prefilter(row, target, selector, top_k)
    ]
    rejected_before_stop: list[dict[str, Any]] = []
    selected: tuple[int, dict[str, Any]] | None = None
    for index, row in rows:
        if stop_predicate(row, min_root_saved, min_hit_root_ops):
            selected = (index, row)
            break
        rejected_before_stop.append(compact_row(index, row))

    if selected is None:
        return {
            "artifact": str(path),
            "candidate_prefilter_count": len(rows),
            "claim_status": "PUBLIC_STOP_RULE_ABSTAINS",
            "rejected_before_stop": rejected_before_stop,
            "rejected_before_stop_count": len(rejected_before_stop),
            "rejected_screen_ops_before_stop": sum(row["screen_ops"] for row in rejected_before_stop),
            "selected": None,
            "window": window_label(path),
        }

    selected_index, selected_row = selected
    selected_compact = compact_row(selected_index, selected_row)
    rejected_screen_ops = sum(row["screen_ops"] for row in rejected_before_stop)
    selected_shared_ops = selected_compact["shared_ops"]
    rho = selected_compact["rho"]
    screened_total_ops = rejected_screen_ops + selected_shared_ops
    selected_passes = (
        selected_compact["public_key_verified"]
        and selected_shared_ops > 0
        and selected_shared_ops < rho
    )
    screened_passes = (
        selected_compact["public_key_verified"]
        and screened_total_ops > 0
        and screened_total_ops < rho
    )
    return {
        "artifact": str(path),
        "candidate_prefilter_count": len(rows),
        "claim_status": (
            "PUBLIC_STOP_RULE_SCREENED_BELOW_RHO"
            if screened_passes
            else "PUBLIC_STOP_RULE_SELECTED_ONLY_BELOW_RHO" if selected_passes else "PUBLIC_STOP_RULE_NEGATIVE"
        ),
        "rejected_before_stop": rejected_before_stop,
        "rejected_before_stop_count": len(rejected_before_stop),
        "rejected_screen_ops_before_stop": rejected_screen_ops,
        "screened_total_ops": screened_total_ops,
        "screened_total_ops_over_rho": ratio(screened_total_ops, rho),
        "screened_total_passes_rho": screened_passes,
        "selected": selected_compact,
        "selected_only_passes_rho": selected_passes,
        "window": window_label(path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict-products", required=True, help="Comma-separated strict product JSON artifacts")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_span_total10")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--min-root-saved", type=int, default=1)
    parser.add_argument("--min-hit-root-ops", type=int, default=3)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = [Path(item) for item in args.strict_products.split(",") if item]
    audits = [
        audit_artifact(
            path,
            target=args.target,
            selector=args.selector,
            top_k=args.top_k,
            min_root_saved=args.min_root_saved,
            min_hit_root_ops=args.min_hit_root_ops,
        )
        for path in paths
    ]
    stopped = [audit for audit in audits if audit.get("selected")]
    summary = {
        "abstained_count": sum(1 for audit in audits if not audit.get("selected")),
        "claim_status": (
            "PUBLIC_STOP_RULE_SCREENED_SWEEP_POSITIVE"
            if stopped and all(audit.get("screened_total_passes_rho") for audit in stopped)
            else "PUBLIC_STOP_RULE_SWEEP_MIXED"
        ),
        "screened_below_rho_count": sum(1 for audit in stopped if audit.get("screened_total_passes_rho")),
        "selected_only_below_rho_count": sum(1 for audit in stopped if audit.get("selected_only_passes_rho")),
        "stopped_count": len(stopped),
        "unverified_stop_count": sum(
            1
            for audit in stopped
            if not ((audit.get("selected") or {}).get("public_key_verified"))
        ),
        "verified_above_screened_rho_count": sum(
            1
            for audit in stopped
            if (audit.get("selected") or {}).get("public_key_verified")
            and not audit.get("screened_total_passes_rho")
        ),
        "window_count": len(audits),
    }
    payload = {
        "audits": audits,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this charges a public row-stop screen plus selected shared-product rows, not one-process source generation.",
            "UNTESTED: target descent is not implemented.",
        ],
        "method": "low_term_total2_public_stop_rule_collector",
        "parameters": {
            "min_hit_root_ops": args.min_hit_root_ops,
            "min_root_saved": args.min_root_saved,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
        },
        "schema": "ecdlp.low_term_total2_public_stop_rule_collector.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
