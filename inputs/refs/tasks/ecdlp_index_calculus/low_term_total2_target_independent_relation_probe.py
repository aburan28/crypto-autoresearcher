#!/usr/bin/env python3
"""Search source artifacts for target-independent relation equations.

The current certificate bank proves local target recovery but does not expose
reusable factor-base logs.  A minimal next test is to ask whether the public
source-case scanner ever emits relation forms with zero target coefficient:

    0 * secret(Q) + sum_j a_j log(F_j) = rhs mod order.

Such rows would be target-independent factor-base equations that can be fed into
the linear descent audit.  Absence in a bounded scan is a scoped negative result
for that source schedule, not for index calculus.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "min": min(values),
    }


def source_cases(source: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for row in result.get("stress_leaf_results") or []:
            if not isinstance(row, dict):
                continue
            out.append(
                {
                    **row,
                    "source_policy": policy_name,
                    "row_selector": row.get("row_selector") or row_selector,
                }
            )
    out.sort(
        key=lambda row: (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
            int_value(row.get("top_k")),
            str(row.get("source_policy")),
        )
    )
    return out


def events_from_scan_rows(scan_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int, tuple[int, ...]]] = set()
    for row in scan_rows:
        for event in (row.get("relation_events") or row.get("_events") or []):
            if not isinstance(event, dict) or "form" not in event:
                continue
            coeffs, rhs, terms = event["form"]
            key = (
                tuple(int_value(coeff) for coeff in coeffs),
                int_value(rhs),
                tuple(int_value(term) for term in terms),
            )
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def compact_zero_event(
    event: dict[str, Any],
    order: int,
    case: dict[str, Any],
    source_path: Path,
) -> dict[str, Any]:
    coeffs, rhs, terms = event["form"]
    return {
        "coeffs_nonzero_positions": [
            index for index, coeff in enumerate(coeffs) if int_value(coeff) % order
        ],
        "factor_support_size": sum(1 for coeff in coeffs[1:] if int_value(coeff) % order),
        "rhs": int_value(rhs) % order,
        "source": str(source_path),
        "target": case.get("target"),
        "terms": [int_value(term) for term in terms],
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "selector": case.get("selector"),
    }


def scan_case(source: dict[str, Any], source_path: Path, case: dict[str, Any]) -> dict[str, Any]:
    verifier, contexts, _product_factor, max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        case,
    )
    covers, _product_profile = timing_probe.shared_product_pair_association(contexts)
    scan_rows = timing_probe.scan_from_covers(verifier, contexts, covers, max_relations)
    events = events_from_scan_rows(scan_rows)
    order = int_value(contexts[0]["built"].get("order")) if contexts else 0
    q_coeffs = []
    zero_events = []
    for event in events:
        coeffs, _rhs, _terms = event["form"]
        q_coeff = int_value(coeffs[0]) % order if coeffs else 0
        q_coeffs.append(q_coeff)
        if q_coeff == 0:
            zero_events.append(compact_zero_event(event, order, case, source_path))
    return {
        "event_count": len(events),
        "order": order,
        "q_zero_event_count": len(zero_events),
        "q_zero_events": zero_events[:5],
        "q_zero_nonempty_factor_count": sum(1 for event in zero_events if event["factor_support_size"] > 0),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "selector": case.get("selector"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", required=True, help="Comma-separated source artifact paths.")
    parser.add_argument("--target")
    parser.add_argument("--selector")
    parser.add_argument("--top-k", type=int)
    parser.add_argument("--max-cases", type=int, default=200)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_paths = [Path(item) for item in args.sources.split(",") if item.strip()]
    case_summaries: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    considered = 0
    for source_path in source_paths:
        source = load_json(source_path)
        for case in source_cases(source):
            if args.target and str(case.get("target")) != args.target:
                continue
            if args.selector and str(case.get("selector")) != args.selector:
                continue
            if args.top_k is not None and int_value(case.get("top_k")) != args.top_k:
                continue
            if considered >= args.max_cases:
                break
            considered += 1
            try:
                summary = scan_case(source, source_path, case)
                summary["source"] = str(source_path)
                case_summaries.append(summary)
            except Exception as exc:  # pragma: no cover - artifact records failures.
                errors.append(
                    {
                        "error": str(exc),
                        "source": str(source_path),
                        "target": case.get("target"),
                        "top_k": int_value(case.get("top_k")),
                        "transfer_index": int_value(case.get("transfer_index")),
                        "selector": case.get("selector"),
                    }
                )
        if considered >= args.max_cases:
            break
    zero_cases = [case for case in case_summaries if int_value(case.get("q_zero_event_count")) > 0]
    order_counts = Counter(str(case.get("order")) for case in case_summaries)
    selector_counts = Counter(str(case.get("selector")) for case in case_summaries)
    event_counts = [int_value(case.get("event_count")) for case in case_summaries]
    payload = {
        "artifacts": {"sources": [str(path) for path in source_paths]},
        "case_summaries": case_summaries,
        "claim_status": (
            "TARGET_INDEPENDENT_Q_ZERO_RELATIONS_FOUND"
            if zero_cases
            else "NEGATIVE_RESULT_NO_Q_ZERO_RELATIONS_IN_BOUNDED_SCAN"
        ),
        "created_at": now_iso(),
        "errors": errors[:20],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: q-zero means zero coefficient for the current target variable in the verifier relation form.",
            "NEGATIVE RESULT scope: bounded scan over the provided public source artifacts, not all possible representations or source schedules.",
        ],
        "parameters": {
            "max_cases": args.max_cases,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
        },
        "schema": "ecdlp.low_term_total2_target_independent_relation_probe.v1",
        "summary": {
            "case_count": len(case_summaries),
            "error_count": len(errors),
            "event_count": sum(event_counts),
            "event_count_stats": stat(event_counts),
            "order_counts": dict(sorted(order_counts.items())),
            "q_zero_case_count": len(zero_cases),
            "q_zero_event_count": sum(int_value(case.get("q_zero_event_count")) for case in case_summaries),
            "q_zero_nonempty_factor_count": sum(
                int_value(case.get("q_zero_nonempty_factor_count")) for case in case_summaries
            ),
            "selector_counts": dict(sorted(selector_counts.items())),
        },
        "zero_event_samples": [
            event
            for case in zero_cases[:10]
            for event in (case.get("q_zero_events") or [])
        ][:20],
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
