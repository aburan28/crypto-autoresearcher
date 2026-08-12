#!/usr/bin/env python3
"""Diagnose source features for strictbridge11779 ruleprefix2 replay yield.

This joins pre-replay public source summaries to post-replay outcomes.  The
output is a scheduler-enrichment diagnostic: which public stress features have
been associated with verified bridges in the observed toy corpus, and which
ready windows should be replayed or deprioritized next.

It is not a validated predictor, not target descent, and not a speedup claim.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


WINDOW_RE = re.compile(r"fixed_row_(\d+)_(\d+)_col15_selector_expanded_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def parse_paths(raw: str) -> list[Path]:
    paths: list[Path] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        matches = sorted(Path(path) for path in glob.glob(item))
        paths.extend(matches or [Path(item)])
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def window_from_source(path: Path) -> str:
    match = WINDOW_RE.search(path.name)
    if not match:
        return ""
    return f"{int(match.group(1))}_{int(match.group(2))}"


def window_start(window: str) -> int:
    try:
        return int(str(window).split("_", 1)[0])
    except (TypeError, ValueError):
        return 0


def pct(numer: int, denom: int) -> float:
    if denom <= 0:
        return 0.0
    return round(numer / denom, 6)


def first_policy_summary(source: dict[str, Any]) -> dict[str, Any]:
    summaries = source.get("summary", {}).get("policy_summaries")
    if not isinstance(summaries, list) or not summaries:
        return {}
    return summaries[0] if isinstance(summaries[0], dict) else {}


def source_features(source_path: Path) -> dict[str, Any]:
    payload = load_json(source_path)
    policy = first_policy_summary(payload)
    leaf_best = float_value(policy.get("stress_leaf_best_ops_over_rho"))
    return {
        "source_path": str(source_path),
        "stress_leaf_below_rho": int_value(policy.get("stress_leaf_below_rho")),
        "stress_leaf_best_ops_over_rho": leaf_best,
        "stress_leaf_verified": int_value(policy.get("stress_leaf_verified")),
        "stress_row_below_rho": int_value(policy.get("stress_row_below_rho")),
        "stress_row_verified": int_value(policy.get("stress_row_verified")),
    }


def replay_summary(replay_path: Path | None) -> dict[str, Any]:
    if replay_path is None or not replay_path.exists():
        return {}
    payload = load_json(replay_path)
    return payload.get("summary") if isinstance(payload.get("summary"), dict) else {}


def replay_category(summary: dict[str, Any]) -> str:
    if not summary:
        return "ready_unreplayed"
    if int_value(summary.get("candidate_certificate_count")) > 0:
        return "verified_bridge"
    if int_value(summary.get("nonzero_projection_selection_count")) > 0:
        return "trace_only"
    if summary.get("claim_status") == "NO_SELECTIONS_TESTED":
        return "no_selection"
    return "no_projection"


def source_bucket(name: str, value: Any) -> str:
    if name == "stress_leaf_verified":
        value = int_value(value)
        if value >= 50:
            return "50_plus"
        if value >= 33:
            return "33_49"
        if value >= 16:
            return "16_32"
        if value > 0:
            return "1_15"
        return "0"
    if name == "stress_leaf_below_rho":
        value = int_value(value)
        if value >= 33:
            return "33_plus"
        if value >= 24:
            return "24_32"
        if value >= 13:
            return "13_23"
        if value > 0:
            return "1_12"
        return "0"
    if name == "stress_row_verified":
        value = int_value(value)
        if value >= 21:
            return "21_plus"
        if value >= 16:
            return "16_20"
        if value >= 11:
            return "11_15"
        if value > 0:
            return "1_10"
        return "0"
    if name == "stress_row_below_rho":
        value = int_value(value)
        if value >= 4:
            return "4_plus"
        return str(value)
    if name == "stress_leaf_best_ops_over_rho":
        value = float_value(value)
        if value is None:
            return "missing"
        if value <= 0.5:
            return "lte_0.5"
        if value <= 0.7:
            return "0.5_0.7"
        if value <= 1.0:
            return "0.7_1.0"
        return "gt_1.0"
    return "unknown"


def enrichment_score(row: dict[str, Any]) -> int:
    score = 0
    leaf_verified = int_value(row.get("stress_leaf_verified"))
    leaf_below = int_value(row.get("stress_leaf_below_rho"))
    row_verified = int_value(row.get("stress_row_verified"))
    row_below = int_value(row.get("stress_row_below_rho"))
    best = float_value(row.get("stress_leaf_best_ops_over_rho"))
    if leaf_verified >= 50:
        score += 3
    elif leaf_verified >= 33:
        score += 1
    if leaf_below >= 33:
        score += 2
    elif leaf_below >= 24:
        score += 1
    if row_verified >= 21:
        score += 2
    elif row_verified >= 16:
        score += 1
    if row_below == 2:
        score += 1
    elif row_below >= 4:
        score -= 1
    if best is not None and best <= 0.5:
        score += 1
    return score


def bridge_like(category: str) -> bool:
    return category == "verified_bridge"


def nonpromoted(category: str) -> bool:
    return category in {"trace_only", "no_projection", "no_selection"}


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["category"] for row in rows)
    promoted = counts.get("verified_bridge", 0)
    observed = sum(counts[key] for key in ("verified_bridge", "trace_only", "no_projection", "no_selection"))
    scores = [int_value(row.get("enrichment_score")) for row in rows if row["category"] != "ready_unreplayed"]
    return {
        "window_count": len(rows),
        "observed_window_count": observed,
        "ready_unreplayed_count": counts.get("ready_unreplayed", 0),
        "verified_bridge_count": promoted,
        "trace_only_count": counts.get("trace_only", 0),
        "no_projection_count": counts.get("no_projection", 0),
        "no_selection_count": counts.get("no_selection", 0),
        "verified_bridge_rate": pct(promoted, observed),
        "enrichment_score_mean_observed": round(mean(scores), 8) if scores else None,
    }


def group_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    observed = [row for row in rows if row["category"] != "ready_unreplayed"]
    counts = Counter(row["category"] for row in observed)
    promoted = counts.get("verified_bridge", 0)
    return {
        "window_count": len(rows),
        "observed_window_count": len(observed),
        "ready_unreplayed_count": sum(1 for row in rows if row["category"] == "ready_unreplayed"),
        "verified_bridge_count": promoted,
        "trace_only_count": counts.get("trace_only", 0),
        "no_projection_count": counts.get("no_projection", 0),
        "no_selection_count": counts.get("no_selection", 0),
        "verified_bridge_rate_observed": pct(promoted, len(observed)),
    }


def grouped(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key))].append(row)
    return {
        value: group_stats(group_rows)
        for value, group_rows in sorted(groups.items())
    }


def threshold_report(rows: list[dict[str, Any]], field: str, min_count: int) -> list[dict[str, Any]]:
    observed = [row for row in rows if row["category"] != "ready_unreplayed"]
    values = sorted({int_value(row.get(field)) for row in observed})
    reports = []
    for threshold in values:
        group = [row for row in observed if int_value(row.get(field)) >= threshold]
        if len(group) < min_count:
            continue
        stats = group_stats(group)
        reports.append(
            {
                "field": field,
                "threshold": threshold,
                **stats,
            }
        )
    reports.sort(
        key=lambda item: (
            -float(item.get("verified_bridge_rate_observed") or 0.0),
            -int_value(item.get("observed_window_count")),
            int_value(item.get("threshold")),
        )
    )
    return reports[:12]


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "window",
        "category",
        "claim_status",
        "enrichment_score",
        "stress_leaf_verified",
        "stress_leaf_below_rho",
        "stress_leaf_best_ops_over_rho",
        "stress_row_verified",
        "stress_row_below_rho",
        "nonzero_projection_selection_count",
        "candidate_certificate_count",
        "tested_selection_count",
    ]
    return {key: row.get(key) for key in keys if key in row}


def build_rows(source_paths: list[Path], replay_dir: Path, replay_prefix: str) -> list[dict[str, Any]]:
    rows = []
    for source_path in source_paths:
        window = window_from_source(source_path)
        if not window:
            continue
        replay_path = replay_dir / f"{replay_prefix}_{window}_order11779_probe.json"
        features = source_features(source_path)
        replay = replay_summary(replay_path)
        category = replay_category(replay)
        row = {
            "window": window,
            "source_path": str(source_path),
            "replay_path": str(replay_path) if replay_path.exists() else None,
            "category": category,
            "claim_status": replay.get("claim_status"),
            "candidate_certificate_count": int_value(replay.get("candidate_certificate_count")),
            "nonzero_projection_selection_count": int_value(replay.get("nonzero_projection_selection_count")),
            "tested_selection_count": int_value(replay.get("tested_selection_count")),
            **features,
        }
        for field in (
            "stress_leaf_verified",
            "stress_leaf_below_rho",
            "stress_row_verified",
            "stress_row_below_rho",
            "stress_leaf_best_ops_over_rho",
        ):
            row[f"{field}_bucket"] = source_bucket(field, row.get(field))
        row["enrichment_score"] = enrichment_score(row)
        rows.append(row)
    rows.sort(key=lambda item: window_start(item["window"]))
    return rows


def ready_in_scope(
    rows: list[dict[str, Any]],
    min_start: int | None,
    max_start: int | None,
) -> list[dict[str, Any]]:
    ready = []
    for row in rows:
        if row["category"] != "ready_unreplayed":
            continue
        start = window_start(row["window"])
        if min_start is not None and start < min_start:
            continue
        if max_start is not None and start > max_start:
            continue
        ready.append(row)
    return sorted(
        ready,
        key=lambda row: (
            -int_value(row.get("enrichment_score")),
            -int_value(row.get("stress_leaf_verified")),
            -int_value(row.get("stress_row_verified")),
            window_start(row["window"]),
        ),
    )


def work_orders(rows: list[dict[str, Any]], ready: list[dict[str, Any]]) -> list[dict[str, Any]]:
    score_slices = grouped(rows, "enrichment_score")
    top_ready = ready[:5]
    orders: list[dict[str, Any]] = []
    if top_ready:
        best_score = int_value(top_ready[0].get("enrichment_score"))
        if best_score >= 5:
            orders.append(
                {
                    "action": "preregister_replay_high_source_enrichment_windows",
                    "status": "HYPOTHESIS",
                    "reason": "At least one ready window matches the highest observed source-enrichment score band.",
                    "ready_windows": [compact_row(row) for row in top_ready],
                    "next_action": "Replay only the top-ranked ready windows and compare certificate yield against queue-drain baseline.",
                }
            )
        else:
            orders.append(
                {
                    "action": "pause_blind_queue_drain_and_generate_enriched_sources",
                    "status": "HYPOTHESIS",
                    "reason": "Ready windows do not reach the high source-enrichment score bands; recent queue-drain batches were denominator-heavy.",
                    "ready_windows": [compact_row(row) for row in top_ready],
                    "next_action": "Run a source-generation or scheduler variant that targets higher stress_leaf_verified/stress_row_verified bands and then replay under the candidate-family gate.",
                }
            )
    else:
        orders.append(
            {
                "action": "no_ready_windows_in_requested_scope",
                "status": "OPEN",
                "reason": "No unreplayed source windows matched the requested ready-window start bounds.",
                "ready_windows": [],
                "next_action": "Refresh source generation or widen the ready-window scope before using this scheduler diagnostic.",
            }
        )
    orders.append(
        {
            "action": "prioritize_high_yield_nonzero_buckets_after_replay",
            "status": "OBSERVATION",
            "reason": "Post-replay 3_4 and 5_plus nonzero-nullspace buckets remain much higher-yield than 1_2; this diagnostic searches for pre-replay features that enrich those cases.",
            "evidence": score_slices,
            "next_action": "Keep adaptive candidate-family holdout as the promotion gate; use source features only to route scarce replay budget.",
        }
    )
    return orders


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-glob", required=True)
    parser.add_argument("--replay-dir", type=Path, default=Path("ecdlp_index_calculus_state"))
    parser.add_argument(
        "--replay-prefix",
        default="low_term_total2_nullspace_asymmetric_leaf_scout_strictbridge11779_ruleprefix2",
    )
    parser.add_argument("--min-threshold-count", type=int, default=5)
    parser.add_argument(
        "--ready-min-start",
        type=int,
        default=None,
        help="Only rank unreplayed ready windows whose transfer-window start is at least this value.",
    )
    parser.add_argument(
        "--ready-max-start",
        type=int,
        default=None,
        help="Only rank unreplayed ready windows whose transfer-window start is at most this value.",
    )
    parser.add_argument("--out", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(parse_paths(args.source_glob), args.replay_dir, args.replay_prefix)
    ready_all_count = sum(1 for row in rows if row["category"] == "ready_unreplayed")
    ready = ready_in_scope(rows, args.ready_min_start, args.ready_max_start)
    observed = [row for row in rows if row["category"] != "ready_unreplayed"]
    payload = {
        "schema": "ecdlp.low_term_total2_ruleprefix2_source_enrichment_diagnostic.v1",
        "created_at": now_iso(),
        "honesty_boundary": {
            "claim_status": "POST_REPLAY_SOURCE_FEATURE_DIAGNOSTIC_ONLY",
            "TOY_EVIDENCE": True,
            "HEURISTIC": True,
            "not_a_validated_predictor": True,
            "not_target_descent": True,
            "not_faster_than_rho_claim": True,
        },
        "inputs": {
            "source_glob": args.source_glob,
            "replay_dir": str(args.replay_dir),
            "replay_prefix": args.replay_prefix,
            "ready_min_start": args.ready_min_start,
            "ready_max_start": args.ready_max_start,
        },
        "summary": summarize(rows),
        "ready_scope": {
            "ready_unreplayed_total_count": ready_all_count,
            "ready_ranked_scope_count": len(ready),
            "ready_min_start": args.ready_min_start,
            "ready_max_start": args.ready_max_start,
        },
        "source_feature_slices": {
            "by_enrichment_score": grouped(rows, "enrichment_score"),
            "by_stress_leaf_verified_bucket": grouped(rows, "stress_leaf_verified_bucket"),
            "by_stress_leaf_below_rho_bucket": grouped(rows, "stress_leaf_below_rho_bucket"),
            "by_stress_row_verified_bucket": grouped(rows, "stress_row_verified_bucket"),
            "by_stress_row_below_rho_bucket": grouped(rows, "stress_row_below_rho_bucket"),
            "by_stress_leaf_best_ops_over_rho_bucket": grouped(rows, "stress_leaf_best_ops_over_rho_bucket"),
        },
        "top_thresholds": (
            threshold_report(rows, "stress_leaf_verified", args.min_threshold_count)
            + threshold_report(rows, "stress_leaf_below_rho", args.min_threshold_count)
            + threshold_report(rows, "stress_row_verified", args.min_threshold_count)
        ),
        "ready_ranked": [compact_row(row) for row in ready[:40]],
        "work_orders": work_orders(observed, ready),
        "rows": [compact_row(row) for row in rows],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(json.dumps({"top_ready": payload["ready_ranked"][:5]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
