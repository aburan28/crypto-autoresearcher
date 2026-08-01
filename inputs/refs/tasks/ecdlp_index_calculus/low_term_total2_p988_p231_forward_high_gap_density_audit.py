#!/usr/bin/env python3
"""P988 frozen forward density audit for the p231 public high-gap source."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_p986_p231_adaptive_high_gap_guard_validation as p986
import low_term_total2_p987_p231_cumulative_high_gap_relation_source as p987


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p988_p231_forward_high_gap_density_audit.md"
DEFAULT_P984 = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
DEFAULT_P986 = STATE_DIR / "low_term_total2_p986_p231_adaptive_high_gap_guard_validation_probe.json"
DEFAULT_P987 = STATE_DIR / "low_term_total2_p987_p231_cumulative_high_gap_relation_source_probe.json"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p988_p231_forward_high_gap_density_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p988_p231_forward_high_gap_density_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def source_controls(p987_payload: dict[str, Any]) -> dict[str, Any]:
    summary = p987_payload.get("summary") or {}
    return {
        "p987_claim_expected": p987_payload.get("claim_status")
        == "P987_CUMULATIVE_HIGH_GAP_RELATION_SOURCE_BELOW_RHO",
        "p987_control_pass": bool(summary.get("control_pass")),
        "p987_selected_eight": int_value(summary.get("cumulative_selected_count")) == 8,
        "p987_broad_groups_seven": int_value(summary.get("cumulative_broad_relation_group_count")) == 7,
        "p987_broad_amortized_expected": summary.get("cumulative_broad_direct_relation_amortized_ops_over_rho")
        == 0.94369135,
    }


def annotate_rows(rows: list[dict[str, Any]], audit_block: str) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        copied["audit_block"] = audit_block
        annotated.append(copied)
    return annotated


def scan_forward(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    high_gap_rows, _guarded_rows, scan_counts = p986.scan_adaptive(args, p986.FROZEN_GUARD)
    return annotate_rows(high_gap_rows, "p988_forward_high_gap"), scan_counts


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p984_path = Path(args.p984)
    p986_path = Path(args.p986)
    p987_path = Path(args.p987)
    p984_payload = load_json(p984_path)
    p986_payload = load_json(p986_path)
    p987_payload = load_json(p987_path)
    controls = source_controls(p987_payload)
    control_pass = all(controls.values())

    prior_rows = p987.rows_from_p984(p984_payload) + p987.rows_from_p986(p986_payload)
    forward_rows, scan_counts = scan_forward(args)
    combined_rows = prior_rows + forward_rows

    prior_summary = p985.summarize_selected("p987_base_replay", prior_rows)
    forward_summary = p985.summarize_selected("p988_forward", forward_rows)
    combined_summary = p985.summarize_selected("p987_plus_p988_forward", combined_rows)
    high_gap_reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in forward_rows)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in combined_rows)
    forward_density = {
        "first_stage_per_source_case": ratio(scan_counts["first_stage_selected_case_count"], scan_counts["source_case_count"]),
        "second_stage_per_source_case": ratio(scan_counts["second_stage_selected_case_count"], scan_counts["source_case_count"]),
        "high_gap_per_source_case": ratio(scan_counts["high_gap_selected_case_count"], scan_counts["source_case_count"]),
        "high_gap_per_scanned_window": ratio(scan_counts["high_gap_selected_case_count"], scan_counts["scanned_window_count"]),
        "broad_groups_per_scanned_window": ratio(
            forward_summary["broad_relation_group_count"], scan_counts["scanned_window_count"]
        ),
    }

    success = bool(
        control_pass
        and scan_counts["scanned_window_count"] == scan_counts["available_candidate_window_count"]
        and forward_summary["selected_count"] > 0
        and reconstruction_error_count == 0
        and combined_summary["broad_relation_group_count"] > prior_summary["broad_relation_group_count"]
        and (combined_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P988_CONTROL_FAILURE"
    elif scan_counts["available_candidate_window_count"] == 0:
        claim = "NEGATIVE_RESULT_P988_NO_AVAILABLE_FORWARD_WINDOWS"
    elif scan_counts["scanned_window_count"] != scan_counts["available_candidate_window_count"]:
        claim = "NEGATIVE_RESULT_P988_INCOMPLETE_FORWARD_SCAN"
    elif forward_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P988_NO_FORWARD_HIGH_GAP_ROWS"
    elif high_gap_reconstruction_error_count != 0:
        claim = "NEGATIVE_RESULT_P988_FORWARD_RECONSTRUCTION_ERRORS"
    elif combined_summary["broad_relation_group_count"] <= prior_summary["broad_relation_group_count"]:
        claim = "NEGATIVE_RESULT_P988_FORWARD_ADDS_NO_BROAD_GROUPS"
    elif (combined_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P988_FORWARD_DENSITY_NOT_BELOW_RHO"
    elif success:
        claim = "P988_FORWARD_HIGH_GAP_DENSITY_REMAINS_BELOW_RHO"
    else:
        claim = "NEGATIVE_RESULT_P988_INVARIANT_FAILURE"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p984_source": str(p984_path),
            "p986_source": str(p986_path),
            "p987_source": str(p987_path),
            "script": str(Path(__file__)),
            "source_windows": scan_counts["source_windows"],
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p984_source_sha256": sha256_file(p984_path),
            "p986_source_sha256": sha256_file(p986_path),
            "p987_source_sha256": sha256_file(p987_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": p985.BROAD_LABEL,
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P988_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "density": forward_density,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FORWARD-SCAN: no adaptive stopping on the forward interval.",
            "FALSE-POSITIVES-CHARGED: combined amortization charges every high-gap selected row.",
            "NO-PARITY-GUARD: P985 max-salt parity is excluded because P986 falsified it.",
            "NO-END-TO-END-BREAK: this is a relation-source component, not sparse linear algebra or target descent.",
        ],
        "method": "p988_p231_forward_high_gap_density_audit",
        "parameters": {
            "base_high_gap_rule": p985.HIGH_GAP_RULE,
            "broad_label": p985.BROAD_LABEL,
            "excluded_guard": "max_salt mod 2 in {0}",
            "first_stage_rule": p986.p872.FIRST_STAGE_RULE,
            "max_scan_windows": args.max_scan_windows,
            "second_stage_rule": p986.p872.SECOND_STAGE_RULE,
            "start_transfer": args.start_transfer,
            "stop_transfer": args.stop_transfer,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "scan": scan_counts,
        "schema": SCHEMA,
        "source_controls": controls,
        "summaries": [prior_summary, forward_summary, combined_summary],
        "summary": {
            "control_pass": control_pass,
            "forward_density_success": success,
            "high_gap_reconstruction_error_count": high_gap_reconstruction_error_count,
            "reconstruction_error_count": reconstruction_error_count,
            **{f"density_{key}": value for key, value in forward_density.items()},
            **{f"scan_{key}": value for key, value in scan_counts.items() if key not in ("source_windows", "window_reports")},
            **{f"prior_{key}": value for key, value in prior_summary.items()},
            **{f"forward_{key}": value for key, value in forward_summary.items()},
            **{f"combined_{key}": value for key, value in combined_summary.items()},
        },
        "forward_cases": forward_rows,
        "forward_cases_compact": [p985.compact_case(row) for row in forward_rows],
        "combined_cases_compact": [p985.compact_case(row) for row in combined_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P988 contract path")
    parser.add_argument("--p984", default=str(DEFAULT_P984), help="P984 cumulative high-gap JSON")
    parser.add_argument("--p986", default=str(DEFAULT_P986), help="P986 adaptive high-gap JSON")
    parser.add_argument("--p987", default=str(DEFAULT_P987), help="P987 cumulative relation-source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target ids")
    parser.add_argument("--start-transfer", type=int, default=11752, help="First forward transfer-window start")
    parser.add_argument("--stop-transfer", type=int, default=11896, help="Last forward transfer-window start")
    parser.add_argument("--max-scan-windows", type=int, default=19, help="Maximum candidate windows to inspect")
    parser.add_argument("--max-nonempty-windows", type=int, default=10**9, help=argparse.SUPPRESS)
    parser.add_argument("--min-high-gap-rows", type=int, default=10**9, help=argparse.SUPPRESS)
    parser.add_argument("--stop-after-min-rows", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} windows={windows} source={source} forward={forward} "
        "forward_broad_groups={forward_groups} combined_selected={combined_selected} "
        "combined_broad_groups={combined_groups} combined_broad_amortized={combined_amortized} out={out}".format(
            claim=payload["claim_status"],
            windows=summary["scan_scanned_window_count"],
            source=summary["scan_source_case_count"],
            forward=summary["forward_selected_count"],
            forward_groups=summary["forward_broad_relation_group_count"],
            combined_selected=summary["combined_selected_count"],
            combined_groups=summary["combined_broad_relation_group_count"],
            combined_amortized=summary["combined_broad_direct_relation_amortized_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
