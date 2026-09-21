#!/usr/bin/env python3
"""Audit replay-window features for the strictbridge11779 ruleprefix2 corpus.

This is a post-replay feature audit, not a deployable predictor.  It records
which public replay/log features separate no-projection, trace-only, and
verified-bridge windows so later scheduler work has a concrete data table.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


DIRECT_COUNT_RE = re.compile(r"direct_source_case_count=(\d+)")


def load_json(path: Path) -> dict[str, Any]:
    with path.open() as fh:
        return json.load(fh)


def pct(numer: int, denom: int) -> float:
    if denom == 0:
        return 0.0
    return round(numer / denom, 6)


def bucket_count(value: int) -> str:
    if value <= 0:
        return "0"
    if value <= 2:
        return "1_2"
    if value <= 4:
        return "3_4"
    return "5_plus"


def tested_bucket(value: int) -> str:
    if value <= 4:
        return "lte4"
    if value <= 8:
        return "5_8"
    if value <= 12:
        return "9_12"
    return "13_plus"


def support_key(supports: list[Any]) -> str:
    parts: list[str] = []
    for support in supports:
        if isinstance(support, list):
            parts.append(",".join(str(x) for x in support))
    return ";".join(parts) if parts else ""


def direct_source_count(window: str, log_dir: Path) -> int | None:
    start, end = window.split("_", 1)
    path = log_dir / f"ecdlp_direct_lowterm_support5_bridge_{start}_{end}_launch.log"
    if not path.exists():
        return None
    text = path.read_text(errors="replace")
    matches = DIRECT_COUNT_RE.findall(text)
    if not matches:
        return None
    return int(matches[-1])


def summarize_slices(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    out: dict[str, Any] = {}
    for value, group_rows in sorted(groups.items()):
        positive = sum(1 for row in group_rows if row["category"] == "verified_bridge")
        trace_only = sum(1 for row in group_rows if row["category"] == "trace_only")
        no_projection = sum(1 for row in group_rows if row["category"] == "no_projection")
        out[value] = {
            "window_count": len(group_rows),
            "verified_bridge_count": positive,
            "trace_only_count": trace_only,
            "no_projection_count": no_projection,
            "verified_bridge_rate": pct(positive, len(group_rows)),
        }
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", required=True, type=Path)
    parser.add_argument("--log-dir", default=Path("jobs/campaign_logs"), type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    summary = load_json(args.summary)
    rows: list[dict[str, Any]] = []
    support_counter: Counter[str] = Counter()
    direct_miss_positive_windows: list[str] = []

    for row in summary.get("rows", []):
        scout_path = Path(row["path"])
        scout = load_json(scout_path)
        scout_summary = scout.get("summary", {})
        window = row["window"]
        direct_count = direct_source_count(window, args.log_dir)
        supports = row.get("form_supports") or []
        support_signature = support_key(supports)
        if row["category"] == "verified_bridge" and support_signature:
            support_counter[support_signature] += 1
        if row["category"] == "verified_bridge" and direct_count == 0:
            direct_miss_positive_windows.append(window)
        best_costs = [
            item.get("direct_ops_over_rho")
            for item in scout_summary.get("best_verified", [])
            if isinstance(item.get("direct_ops_over_rho"), (int, float))
        ]
        nonzero_count = int(scout_summary.get("nonzero_projection_selection_count") or 0)
        pair_count = int(scout_summary.get("pair_count") or 0)
        tested = int(scout_summary.get("tested_selection_count") or row.get("tested_selection_count") or 0)
        rows.append(
            {
                "window": window,
                "category": row["category"],
                "claim_status": row.get("claim_status"),
                "path": row["path"],
                "pair_count": pair_count,
                "tested_selection_count": tested,
                "tested_bucket": tested_bucket(tested),
                "nonzero_projection_selection_count": nonzero_count,
                "nonzero_projection_bucket": bucket_count(nonzero_count),
                "verified_nonzero_projection_selection_count": int(
                    scout_summary.get("verified_nonzero_projection_selection_count") or 0
                ),
                "candidate_certificate_count": int(scout_summary.get("candidate_certificate_count") or 0),
                "direct_below_rho_verified_count": int(scout_summary.get("direct_below_rho_verified_count") or 0),
                "direct_source_case_count": direct_count,
                "direct_source_bucket": "missing"
                if direct_count is None
                else ("0" if direct_count == 0 else "positive"),
                "best_direct_ops_over_rho": min(best_costs) if best_costs else None,
                "support_signature": support_signature,
            }
        )

    category_counts = Counter(row["category"] for row in rows)
    positive_rows = [row for row in rows if row["category"] == "verified_bridge"]
    direct_costs = [
        row["best_direct_ops_over_rho"]
        for row in positive_rows
        if isinstance(row["best_direct_ops_over_rho"], (int, float))
    ]

    audit = {
        "schema": "low_term_total2_rule_replay_feature_audit.v1",
        "honesty_boundary": {
            "claim_status": "POST_REPLAY_FEATURE_AUDIT_ONLY",
            "not_a_predictor": True,
            "not_target_descent": True,
            "not_faster_than_rho_claim": True,
        },
        "inputs": {
            "summary": str(args.summary),
            "log_dir": str(args.log_dir),
        },
        "summary": {
            "window_count": len(rows),
            "verified_bridge_count": category_counts.get("verified_bridge", 0),
            "trace_only_count": category_counts.get("trace_only", 0),
            "no_projection_count": category_counts.get("no_projection", 0),
            "verified_bridge_rate": pct(category_counts.get("verified_bridge", 0), len(rows)),
            "candidate_certificate_count": sum(row["candidate_certificate_count"] for row in rows),
            "direct_below_rho_verified_count": sum(row["direct_below_rho_verified_count"] for row in rows),
            "best_direct_ops_over_rho": min(direct_costs) if direct_costs else None,
            "mean_positive_direct_ops_over_rho": round(mean(direct_costs), 8) if direct_costs else None,
            "direct_miss_positive_windows": direct_miss_positive_windows,
        },
        "slices": {
            "by_nonzero_projection_bucket": summarize_slices(rows, "nonzero_projection_bucket"),
            "by_tested_bucket": summarize_slices(rows, "tested_bucket"),
            "by_direct_source_bucket": summarize_slices(rows, "direct_source_bucket"),
        },
        "support_signature_counts": dict(support_counter.most_common()),
        "rows": rows,
        "interpretation": [
            "TOY-EVIDENCE: this audits same-target post-replay features for 22050.cf1@11731 only.",
            "HEURISTIC: survival slices are descriptive on this corpus and are not validated predictors.",
            "OPEN: convert these features into a preregistered scheduler and test on a fresh same-curve target.",
        ],
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as fh:
        json.dump(audit, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(audit["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
