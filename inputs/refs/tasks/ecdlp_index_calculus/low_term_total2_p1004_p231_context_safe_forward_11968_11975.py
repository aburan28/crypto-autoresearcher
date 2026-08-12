#!/usr/bin/env python3
"""P1004 context-safe forward validation on p231 window 11968_11975."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p998_p231_branch_ensemble_selector as p998
import low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order as p1000
import low_term_total2_p1001_p231_phase_shifted_hash_tuple as p1001
import low_term_total2_p1003_p231_context_safe_grouping_replay as p1003


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1004_p231_context_safe_forward_11968_11975.md"
DEFAULT_P1003 = STATE_DIR / "low_term_total2_p1003_p231_context_safe_grouping_replay_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1004_p231_context_safe_forward_11968_11975_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1004_p231_context_safe_forward_11968_11975.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_WINDOW = "11968_11975"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def p998_predicate(targets: str, min_source_rank: int):
    train_windows = [window.strip() for window in p998.DEFAULT_TRAIN_WINDOWS.split(",") if window.strip()]
    training_examples, _exists = p998.load_examples(train_windows, targets, min_source_rank)
    chosen, predicate, _scored = p998.choose_rule(training_examples)
    return chosen, predicate


def dedupe_examples(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        key = str(row.get("case_id"))
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def source_summary(source_path: Path) -> dict[str, Any]:
    if not source_path.exists():
        return {"source_exists": False}
    payload = load_json(source_path)
    summaries = ((payload.get("summary") or {}).get("policy_summaries") or [])
    fixed = next((row for row in summaries if row.get("policy") == "fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1"), summaries[0] if summaries else {})
    return {
        "source_exists": True,
        "stress_leaf_below_rho": fixed.get("stress_leaf_below_rho"),
        "stress_leaf_best_ops_over_rho": fixed.get("stress_leaf_best_ops_over_rho"),
        "stress_leaf_verified": fixed.get("stress_leaf_verified"),
        "stress_row_below_rho": fixed.get("stress_row_below_rho"),
        "stress_row_verified": fixed.get("stress_row_verified"),
    }


def build_lanes(window: str, targets: str, min_source_rank: int) -> list[tuple[list[dict[str, Any]], dict[str, Any]]]:
    examples = p998.build_window_examples(window, targets, min_source_rank)
    chosen, branch_predicate = p998_predicate(targets, min_source_rank)
    branch = [row for row in examples if branch_predicate(row.get("features") or {})]
    relaxed = [row for row in examples if p1000.frozen_rule(row.get("features") or {})]
    phase = [row for row in examples if p1001.shifted_rule(row.get("features") or {})]
    union = dedupe_examples(branch + relaxed + phase)
    return [
        (branch, {"lane": "p998_branch_ensemble_forward", "rule": chosen.get("name"), "window": window}),
        (relaxed, {"lane": "p1000_relaxed_top7_forward", "rule": "mode_hash_leaf_total6_top7_leaves_34_47_56", "window": window}),
        (phase, {"lane": "p1001_phase_tuple_forward", "rule": "mode_hash_leaf_total6_top12_16_leaves_47_56_84", "window": window}),
        (union, {"lane": "union_survivor_branches_forward", "rule": "p998_branch OR p1000_relaxed OR p1001_phase", "window": window}),
    ]


def determine_claim(control_pass: bool, source_exists: bool, lane_results: list[dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1004_P1003_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P1004_SOURCE_WINDOW_MISSING"
    scalar_valid_count = sum(int_value((row.get("summary") or {}).get("context_safe_scalar_valid_group_count")) for row in lane_results)
    best_costs = [
        float((row.get("summary") or {}).get("scalar_valid_best_amortized_ops_over_rho"))
        for row in lane_results
        if (row.get("summary") or {}).get("scalar_valid_best_amortized_ops_over_rho") is not None
    ]
    selected_count = sum(int_value((row.get("summary") or {}).get("selected_count")) for row in lane_results)
    if scalar_valid_count and best_costs and min(best_costs) < 1.0:
        return "P1004_CONTEXT_SAFE_FORWARD_SCALAR_VALID_BELOW_RHO"
    if scalar_valid_count:
        return "P1004_CONTEXT_SAFE_FORWARD_SCALAR_VALID_ABOVE_RHO"
    if selected_count:
        return "NEGATIVE_RESULT_P1004_SELECTED_ROWS_NO_CONTEXT_SAFE_SCALAR_VALID_GROUP"
    return "NEGATIVE_RESULT_P1004_BRANCHES_SELECT_NO_ROWS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p1003_payload = load_json(Path(args.p1003))
    control_pass = p1003_payload.get("claim_status") == "P1003_CONTEXT_SAFE_SCALAR_VALID_GROUP_SURVIVES"
    source_path = p868.source_path(args.window)
    source_exists = source_path.exists()
    lanes = build_lanes(args.window, args.targets, args.min_source_rank) if source_exists else []
    lane_results = [p1003.analyze_lane(selected, metadata, args.baseline_rank) for selected, metadata in lanes]
    claim = determine_claim(control_pass, source_exists, lane_results)
    best_costs = [
        float((row.get("summary") or {}).get("scalar_valid_best_amortized_ops_over_rho"))
        for row in lane_results
        if (row.get("summary") or {}).get("scalar_valid_best_amortized_ops_over_rho") is not None
    ]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1003_source": str(args.p1003),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p1003_source_sha256": sha256_file(Path(args.p1003)),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1004_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected.",
            "SCALAR-VALID-GATE: candidates must satisfy candidate*base == public.",
            "NO-END-TO-END-BREAK: relation collection, sparse linear algebra, and target descent remain open.",
        ],
        "lane_results": lane_results,
        "method": "p1004_p231_context_safe_forward_11968_11975",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "p1003_control": {
            "claim_status": p1003_payload.get("claim_status"),
            "summary": p1003_payload.get("summary"),
        },
        "schema": SCHEMA,
        "source": {
            "path": str(source_path),
            "sha256": sha256_file(source_path),
            "summary": source_summary(source_path),
        },
        "summary": {
            "best_scalar_valid_amortized_ops_over_rho": min(best_costs) if best_costs else None,
            "claim_status": claim,
            "control_pass": control_pass,
            "lane_count": len(lane_results),
            "lane_summaries": {row["metadata"]["lane"]: row["summary"] for row in lane_results},
            "source_exists": source_exists,
            "total_context_safe_scalar_valid_group_count": sum(
                int_value((row.get("summary") or {}).get("context_safe_scalar_valid_group_count")) for row in lane_results
            ),
            "total_selected_count": sum(int_value((row.get("summary") or {}).get("selected_count")) for row in lane_results),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1004 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1003", default=str(DEFAULT_P1003), help="P1003 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="Forward validation window")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} source_exists={source_exists} lanes={lanes} selected={selected} "
        "scalar_valid={valid} best={best} out={out}".format(
            claim=payload["claim_status"],
            source_exists=summary["source_exists"],
            lanes=summary["lane_count"],
            selected=summary["total_selected_count"],
            valid=summary["total_context_safe_scalar_valid_group_count"],
            best=summary["best_scalar_valid_amortized_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
