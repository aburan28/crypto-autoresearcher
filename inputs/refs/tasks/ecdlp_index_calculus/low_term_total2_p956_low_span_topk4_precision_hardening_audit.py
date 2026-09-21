#!/usr/bin/env python3
"""P956 precision hardening for the post-1144 low-span direct gate."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p956_low_span_topk4_precision_hardening.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p956_low_span_topk4_precision_hardening_probe.json"
SCHEMA = "ecdlp.low_term_total2_p956_low_span_topk4_precision_hardening.v1"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_POST_MIN = 1144
DIRECT_RE = re.compile(
    r"low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_(\d+)_(\d+)_probe\.json$"
)

Record = dict[str, Any]


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


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_splits(raw: str) -> list[int]:
    return [int(part.strip()) for part in raw.split(",") if part.strip()]


def artifact_paths(state_dir: Path, post_min: int) -> list[tuple[int, int, Path]]:
    paths: list[tuple[int, int, Path]] = []
    for path in state_dir.glob("low_term_total2_fixed_leaf_low_prefix_direct_gate_target67_*_probe.json"):
        if path.name.startswith("._"):
            continue
        match = DIRECT_RE.search(path.name)
        if not match:
            continue
        start, end = int(match.group(1)), int(match.group(2))
        if start >= post_min:
            paths.append((start, end, path))
    return sorted(paths)


def row_salt_signature(row_keys: list[str]) -> str:
    salts = []
    for key in row_keys:
        parts = str(key).split(":")
        salts.append(parts[-1] if parts else str(key))
    return "+".join(sorted(salts))


def record_from_case(case: dict[str, Any], start: int, end: int, path: Path) -> Record:
    public_features = case.get("public_features") or {}
    verified = bool(case.get("direct_union_public_key_verified"))
    below = bool(verified and case.get("direct_below_rho"))
    row_keys = [str(value) for value in case.get("row_keys") or []]
    return {
        "artifact": str(path),
        "below_rho_verified": below,
        "direct_union_derived_secret": case.get("direct_union_derived_secret"),
        "direct_union_rank": int_value(case.get("direct_union_rank")),
        "direct_union_relation_count": int_value(case.get("direct_union_relation_count")),
        "direct_verifier_replay_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "end": end,
        "public_features": public_features,
        "public_low_prefix_gate_selected": bool(case.get("public_low_prefix_gate_selected")),
        "row_keys": row_keys,
        "row_salt_signature": row_salt_signature(row_keys),
        "selector": str(case.get("selector")),
        "start": start,
        "target": str(case.get("target")),
        "top_k": int_value(public_features.get("top_k") or case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "verified": verified,
        "window": f"{start}_{end}",
    }


def load_selected_records(state_dir: Path, post_min: int, target: str) -> tuple[list[Record], list[str]]:
    records: list[Record] = []
    paths_seen: list[str] = []
    for start, end, path in artifact_paths(state_dir, post_min):
        paths_seen.append(str(path))
        payload = load_json(path)
        for case in payload.get("cases") or []:
            if str(case.get("target")) != target:
                continue
            if not case.get("public_low_prefix_gate_selected"):
                continue
            records.append(record_from_case(case, start, end, path))
    return records, paths_seen


def policies() -> dict[str, Callable[[Record], bool]]:
    return {
        "all_selected": lambda _record: True,
        "top_k_4": lambda record: int_value(record.get("top_k")) == 4,
        "top_k_7": lambda record: int_value(record.get("top_k")) == 7,
    }


def summarize(records: list[Record]) -> dict[str, Any]:
    verified = [record for record in records if record.get("verified")]
    below = [record for record in records if record.get("below_rho_verified")]
    ratios = [
        float_value(record.get("direct_verifier_replay_ops_over_rho"))
        for record in below
        if float_value(record.get("direct_verifier_replay_ops_over_rho")) is not None
    ]
    return {
        "below_rho_verified_count": len(below),
        "below_rho_rate": ratio(len(below), len(records)) if records else None,
        "direct_below_rho_ops_over_rho_min": min(ratios) if ratios else None,
        "direct_below_rho_ops_over_rho_mean": round(mean(ratios), 8) if ratios else None,
        "selected_count": len(records),
        "unverified_count": len(records) - len(verified),
        "verified_count": len(verified),
        "verified_precision": ratio(len(verified), len(records)) if records else None,
    }


def select_policy(train_records: list[Record], candidate_names: list[str], min_train_selected: int) -> tuple[str, dict[str, dict[str, Any]]]:
    candidate_policies = policies()
    reports: dict[str, dict[str, Any]] = {}
    scored: list[tuple[tuple[Any, ...], str]] = []
    for name in candidate_names:
        selected = [record for record in train_records if candidate_policies[name](record)]
        report = summarize(selected)
        reports[name] = report
        selected_count = int_value(report.get("selected_count"))
        if selected_count < min_train_selected:
            continue
        score = (
            float_value(report.get("verified_precision"), 0.0),
            float_value(report.get("below_rho_rate"), 0.0),
            int_value(report.get("below_rho_verified_count")),
            -int_value(report.get("unverified_count")),
            name != "all_selected",
            name,
        )
        scored.append((score, name))
    if not scored:
        return "all_selected", reports
    return max(scored)[1], reports


def compact_case(record: Record) -> dict[str, Any]:
    return {
        "artifact": record.get("artifact"),
        "direct_union_derived_secret": record.get("direct_union_derived_secret"),
        "direct_union_rank": record.get("direct_union_rank"),
        "direct_union_relation_count": record.get("direct_union_relation_count"),
        "direct_verifier_replay_ops_over_rho": record.get("direct_verifier_replay_ops_over_rho"),
        "row_keys": record.get("row_keys") or [],
        "selector": record.get("selector"),
        "top_k": record.get("top_k"),
        "transfer_index": record.get("transfer_index"),
        "window": record.get("window"),
    }


def split_report(
    records: list[Record],
    split: int,
    candidate_names: list[str],
    min_train_selected: int,
    min_below_retention: float,
    min_unverified_reduction: float,
) -> dict[str, Any]:
    candidate_policies = policies()
    train_records = [record for record in records if int_value(record.get("start")) < split]
    test_records = [record for record in records if int_value(record.get("start")) >= split]
    selected_name, training_candidates = select_policy(train_records, candidate_names, min_train_selected)
    baseline = summarize(test_records)
    selected_records = [record for record in test_records if candidate_policies[selected_name](record)]
    selected = summarize(selected_records)
    baseline_below = int_value(baseline.get("below_rho_verified_count"))
    baseline_unverified = int_value(baseline.get("unverified_count"))
    below_retention = ratio(int_value(selected.get("below_rho_verified_count")), baseline_below) if baseline_below else None
    unverified_reduction = (
        round(1.0 - (float(int_value(selected.get("unverified_count"))) / float(baseline_unverified)), 8)
        if baseline_unverified
        else None
    )
    precision_lift = (
        round(float_value(selected.get("verified_precision"), 0.0) - float_value(baseline.get("verified_precision"), 0.0), 8)
        if selected.get("verified_precision") is not None and baseline.get("verified_precision") is not None
        else None
    )
    passing = bool(
        below_retention is not None
        and below_retention >= min_below_retention
        and unverified_reduction is not None
        and unverified_reduction >= min_unverified_reduction
        and int_value(selected.get("below_rho_verified_count")) > 0
    )
    best_cases = sorted(
        [record for record in selected_records if record.get("below_rho_verified")],
        key=lambda record: (
            float_value(record.get("direct_verifier_replay_ops_over_rho"), 10**18),
            int_value(record.get("transfer_index")),
        ),
    )[:5]
    return {
        "baseline_test_summary": baseline,
        "below_rho_retention": below_retention,
        "best_selected_below_rho_cases": [compact_case(record) for record in best_cases],
        "heldout_split_start": split,
        "passes_thresholds": passing,
        "precision_lift": precision_lift,
        "selected_policy": selected_name,
        "selected_test_summary": selected,
        "test_count": len(test_records),
        "train_count": len(train_records),
        "training_candidate_summaries": training_candidates,
        "unverified_reduction": unverified_reduction,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("passing_split_count")) >= int_value(summary.get("required_passing_splits")):
        return "P956_TOPK4_PUBLIC_ABSTENTION_REDUCES_UNVERIFIED_PRESERVES_BELOW_RHO"
    if int_value(summary.get("passing_split_count")) > 0:
        return "P956_PARTIAL_PUBLIC_ABSTENTION_HARDENING"
    return "NEGATIVE_RESULT_P956_NO_PUBLIC_TOPK_PRECISION_HARDENING"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    candidate_names = [name.strip() for name in args.candidates.split(",") if name.strip()]
    records, paths_seen = load_selected_records(Path(args.state_dir), int(args.post_min), args.target)
    split_reports = [
        split_report(
            records,
            split,
            candidate_names,
            int(args.min_train_selected),
            float(args.min_below_retention),
            float(args.min_unverified_reduction),
        )
        for split in parse_splits(args.splits)
    ]
    passing = [report for report in split_reports if report.get("passes_thresholds")]
    selected_policy_counts = Counter(str(report.get("selected_policy")) for report in split_reports)
    below_retentions = [
        float_value(report.get("below_rho_retention"))
        for report in split_reports
        if float_value(report.get("below_rho_retention")) is not None
    ]
    unverified_reductions = [
        float_value(report.get("unverified_reduction"))
        for report in split_reports
        if float_value(report.get("unverified_reduction")) is not None
    ]
    precision_lifts = [
        float_value(report.get("precision_lift"))
        for report in split_reports
        if float_value(report.get("precision_lift")) is not None
    ]
    summary = {
        "artifact_count": len(paths_seen),
        "candidate_policies": candidate_names,
        "claim_status": None,
        "min_below_rho_retention": min(below_retentions) if below_retentions else None,
        "min_precision_lift": min(precision_lifts) if precision_lifts else None,
        "min_unverified_reduction": min(unverified_reductions) if unverified_reductions else None,
        "passing_split_count": len(passing),
        "record_count": len(records),
        "required_passing_splits": int(args.required_passing_splits),
        "selected_policy_counts": dict(sorted(selected_policy_counts.items())),
        "split_count": len(split_reports),
        "total_summary": summarize(records),
    }
    summary["claim_status"] = determine_claim(summary)
    best_overall = sorted(
        [record for record in records if record.get("below_rho_verified") and int_value(record.get("top_k")) == 4],
        key=lambda record: (
            float_value(record.get("direct_verifier_replay_ops_over_rho"), 10**18),
            int_value(record.get("transfer_index")),
        ),
    )[: int(args.best_limit)]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "TRAINED-ABSTENTION: top-k rule selection uses earlier-window verifier outcomes and is then evaluated on held-out suffixes.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this reduces verifier waste in a materialized relation stream; it is not full relation collection, matrix solving, or target descent.",
            "POLLARD-RHO BOUNDARY: below-rho claims compare component verifier ops against toy rho.",
        ],
        "method": "p956_low_span_topk4_precision_hardening",
        "parameters": {
            "candidates": candidate_names,
            "min_below_retention": float(args.min_below_retention),
            "min_train_selected": int(args.min_train_selected),
            "min_unverified_reduction": float(args.min_unverified_reduction),
            "post_min": int(args.post_min),
            "required_passing_splits": int(args.required_passing_splits),
            "splits": parse_splits(args.splits),
            "target": args.target,
        },
        "schema": SCHEMA,
        "split_reports": split_reports,
        "summary": summary,
        "topk4_best_below_rho_cases": [compact_case(record) for record in best_overall],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=DEFAULT_POST_MIN)
    parser.add_argument("--splits", default="6000,8000,10000,11000")
    parser.add_argument("--candidates", default="all_selected,top_k_4,top_k_7")
    parser.add_argument("--min-train-selected", type=int, default=50)
    parser.add_argument("--min-below-retention", type=float, default=0.5)
    parser.add_argument("--min-unverified-reduction", type=float, default=0.5)
    parser.add_argument("--required-passing-splits", type=int, default=3)
    parser.add_argument("--best-limit", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"records={summary['record_count']} "
        f"splits={summary['split_count']} "
        f"passing={summary['passing_split_count']} "
        f"selected_policies={summary['selected_policy_counts']} "
        f"min_retention={summary['min_below_rho_retention']} "
        f"min_unverified_reduction={summary['min_unverified_reduction']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
