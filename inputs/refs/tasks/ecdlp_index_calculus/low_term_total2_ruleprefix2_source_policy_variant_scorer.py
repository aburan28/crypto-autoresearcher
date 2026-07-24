#!/usr/bin/env python3
"""Score source-generation policy variants for ruleprefix2 replay routing.

This is a pre-replay diagnostic.  It inspects public source artifacts and ranks
each policy summary using the same heuristic enrichment score as
``low_term_total2_ruleprefix2_source_enrichment_diagnostic.py``.  The output is
used to decide whether a source-generation variant has reached the high-score
bands that justify scarce replay budget.

It is not a validated predictor, not target descent, and not a speedup claim.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_ruleprefix2_source_enrichment_diagnostic as enrich


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return enrich.int_value(value, default)


def float_value(value: Any) -> float | None:
    return enrich.float_value(value)


def policy_summaries(source: dict[str, Any]) -> list[dict[str, Any]]:
    summaries = source.get("summary", {}).get("policy_summaries")
    if not isinstance(summaries, list):
        return []
    return [row for row in summaries if isinstance(row, dict)]


def source_label(path: Path) -> str:
    window = enrich.window_from_source(path)
    return window or path.stem


def policy_row(path: Path, policy: dict[str, Any], index: int) -> dict[str, Any]:
    row = {
        "policy": policy.get("policy") or f"policy_{index}",
        "policy_index": index,
        "row_selector": policy.get("row_selector"),
        "source_path": str(path),
        "source_label": source_label(path),
        "stress_leaf_below_rho": int_value(policy.get("stress_leaf_below_rho")),
        "stress_leaf_best_ops_over_rho": float_value(policy.get("stress_leaf_best_ops_over_rho")),
        "stress_leaf_verified": int_value(policy.get("stress_leaf_verified")),
        "stress_row_below_rho": int_value(policy.get("stress_row_below_rho")),
        "stress_row_verified": int_value(policy.get("stress_row_verified")),
    }
    for field in (
        "stress_leaf_verified",
        "stress_leaf_below_rho",
        "stress_row_verified",
        "stress_row_below_rho",
        "stress_leaf_best_ops_over_rho",
    ):
        row[f"{field}_bucket"] = enrich.source_bucket(field, row.get(field))
    row["enrichment_score"] = enrich.enrichment_score(row)
    row["replay_priority"] = (
        "high"
        if row["enrichment_score"] >= 5
        else "moderate"
        if row["enrichment_score"] >= 4
        else "low"
    )
    return row


def compact(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "source_label",
        "policy",
        "row_selector",
        "enrichment_score",
        "replay_priority",
        "stress_leaf_verified",
        "stress_leaf_below_rho",
        "stress_leaf_best_ops_over_rho",
        "stress_row_verified",
        "stress_row_below_rho",
        "source_path",
    ]
    return {key: row.get(key) for key in keys}


def leaf_selector_rows(source_path: Path, source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for policy, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        buckets: dict[str, dict[str, Any]] = defaultdict(
            lambda: {
                "below_rho_count": 0,
                "best_ops_over_rho": None,
                "leaf_result_count": 0,
                "public_verified_count": 0,
                "source_verified_count": 0,
                "top_transfer_counts": Counter(),
            }
        )
        for leaf in result.get("stress_leaf_results") or []:
            if not isinstance(leaf, dict):
                continue
            selector = str(leaf.get("selector") or leaf.get("leaf_selector") or "unknown")
            bucket = buckets[selector]
            bucket["leaf_result_count"] += 1
            if leaf.get("public_key_verified") is True:
                bucket["public_verified_count"] += 1
            if leaf.get("source_verified") is True:
                bucket["source_verified_count"] += 1
            ops = float_value(leaf.get("ops_over_rho"))
            if ops is not None:
                current = bucket.get("best_ops_over_rho")
                if current is None or ops < current:
                    bucket["best_ops_over_rho"] = ops
                if ops < 1.0:
                    bucket["below_rho_count"] += 1
            elif leaf.get("below_rho") is True:
                bucket["below_rho_count"] += 1
            transfer = leaf.get("transfer_index")
            if transfer is not None:
                bucket["top_transfer_counts"][str(transfer)] += 1
        for selector, bucket in buckets.items():
            rows.append(
                {
                    "below_rho_count": bucket["below_rho_count"],
                    "best_ops_over_rho": bucket["best_ops_over_rho"],
                    "leaf_result_count": bucket["leaf_result_count"],
                    "policy": str(policy),
                    "public_verified_count": bucket["public_verified_count"],
                    "row_selector": row_selector,
                    "selector": selector,
                    "source_label": source_label(source_path),
                    "source_path": str(source_path),
                    "source_verified_count": bucket["source_verified_count"],
                    "top_transfers": [
                        {"count": count, "transfer_index": transfer}
                        for transfer, count in bucket["top_transfer_counts"].most_common(5)
                    ],
                }
            )
    rows.sort(
        key=lambda row: (
            -int_value(row.get("below_rho_count")),
            -int_value(row.get("public_verified_count")),
            float(row.get("best_ops_over_rho") if row.get("best_ops_over_rho") is not None else 10**9),
            str(row.get("source_label")),
            str(row.get("policy")),
            str(row.get("selector")),
        )
    )
    return rows


def compact_leaf(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "source_label",
        "policy",
        "row_selector",
        "selector",
        "leaf_result_count",
        "public_verified_count",
        "source_verified_count",
        "below_rho_count",
        "best_ops_over_rho",
        "top_transfers",
        "source_path",
    ]
    return {key: row.get(key) for key in keys}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    priority_counts = Counter(str(row.get("replay_priority")) for row in rows)
    score_counts = Counter(str(row.get("enrichment_score")) for row in rows)
    high = [row for row in rows if int_value(row.get("enrichment_score")) >= 5]
    moderate = [row for row in rows if int_value(row.get("enrichment_score")) == 4]
    return {
        "high_policy_count": len(high),
        "moderate_policy_count": len(moderate),
        "policy_count": len(rows),
        "priority_counts": dict(sorted(priority_counts.items())),
        "score_counts": dict(sorted(score_counts.items(), key=lambda item: int(item[0]))),
        "source_count": len({row.get("source_path") for row in rows}),
        "top_score": max((int_value(row.get("enrichment_score")) for row in rows), default=None),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-glob", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--top-limit", type=int, default=20)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows: list[dict[str, Any]] = []
    leaf_rows: list[dict[str, Any]] = []
    missing_sources: list[str] = []
    for source_path in enrich.parse_paths(args.source_glob):
        if not source_path.exists():
            missing_sources.append(str(source_path))
            continue
        source = enrich.load_json(source_path)
        for index, policy in enumerate(policy_summaries(source)):
            rows.append(policy_row(source_path, policy, index))
        leaf_rows.extend(leaf_selector_rows(source_path, source))
    rows.sort(
        key=lambda row: (
            -int_value(row.get("enrichment_score")),
            -int_value(row.get("stress_leaf_verified")),
            -int_value(row.get("stress_row_verified")),
            str(row.get("source_label")),
            str(row.get("policy")),
        )
    )
    payload = {
        "schema": "ecdlp.low_term_total2_ruleprefix2_source_policy_variant_scorer.v1",
        "created_at": now_iso(),
        "honesty_boundary": {
            "HEURISTIC": True,
            "TOY_EVIDENCE": True,
            "not_a_validated_predictor": True,
            "not_target_descent": True,
            "not_faster_than_rho_claim": True,
            "pre_replay_source_features_only": True,
        },
        "inputs": {
            "missing_sources": missing_sources,
            "source_glob": args.source_glob,
            "top_limit": args.top_limit,
        },
        "summary": summarize(rows),
        "top_leaf_selectors": [compact_leaf(row) for row in leaf_rows[: args.top_limit]],
        "top_policies": [compact(row) for row in rows[: args.top_limit]],
        "leaf_selector_rows": [compact_leaf(row) for row in leaf_rows],
        "rows": [compact(row) for row in rows],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"top_policies": payload["top_policies"][:5]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
