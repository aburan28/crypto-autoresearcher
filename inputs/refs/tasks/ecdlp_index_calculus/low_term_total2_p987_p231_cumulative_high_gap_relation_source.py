#!/usr/bin/env python3
"""P987 cumulative audit of the unguarded p231 high-gap relation source."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p987_p231_cumulative_high_gap_relation_source.md"
DEFAULT_P984 = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
DEFAULT_P986 = STATE_DIR / "low_term_total2_p986_p231_adaptive_high_gap_guard_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p987_p231_cumulative_high_gap_relation_source_probe.json"
SCHEMA = "ecdlp.low_term_total2_p987_p231_cumulative_high_gap_relation_source.v1"


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


def rows_from_p984(p984: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for section in ("prior_cases", "fresh_cases"):
        for case in p984.get(section) or []:
            if isinstance(case, dict):
                row = dict(case)
                row["audit_block"] = f"p984_{section}"
                rows.append(row)
    return rows


def rows_from_p986(p986: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in p986.get("validation_high_gap_cases") or []:
        if isinstance(case, dict):
            row = dict(case)
            row["audit_block"] = "p986_adaptive_high_gap"
            rows.append(row)
    return rows


def source_controls(p984: dict[str, Any], p986: dict[str, Any]) -> dict[str, Any]:
    s984 = p984.get("summary") or {}
    s986 = p986.get("summary") or {}
    return {
        "p984_claim_expected": p984.get("claim_status") == "NEGATIVE_RESULT_P984_CUMULATIVE_HIGH_GAP_NOT_BELOW_RHO",
        "p984_control_pass": bool(s984.get("control_pass")),
        "p984_cumulative_selected_five": int_value(s984.get("cumulative_selected_count")) == 5,
        "p984_cumulative_broad_groups_four": int_value(s984.get("cumulative_broad_relation_group_count")) == 4,
        "p984_cumulative_broad_amortized_expected": s984.get("cumulative_broad_direct_relation_amortized_ops_over_rho")
        == 1.01094891,
        "p986_claim_expected": p986.get("claim_status") == "NEGATIVE_RESULT_P986_GUARD_MISSES_ADAPTIVE_BROAD_ROWS",
        "p986_control_pass": bool(s986.get("control_pass")),
        "p986_high_gap_three": int_value(s986.get("high_gap_selected_count")) == 3,
        "p986_missed_broad_three": int_value(s986.get("missed_broad_count")) == 3,
        "p986_high_gap_broad_groups_three": int_value(s986.get("high_gap_broad_relation_group_count")) == 3,
        "p986_high_gap_broad_amortized_expected": s986.get("high_gap_broad_direct_relation_amortized_ops_over_rho")
        == 0.8540146,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p984_path = Path(args.p984)
    p986_path = Path(args.p986)
    p984 = load_json(p984_path)
    p986 = load_json(p986_path)
    controls = source_controls(p984, p986)
    control_pass = all(controls.values())
    p984_rows = rows_from_p984(p984)
    p986_rows = rows_from_p986(p986)
    cumulative_rows = p984_rows + p986_rows
    p984_summary = p985.summarize_selected("p984_replay", p984_rows)
    p986_summary = p985.summarize_selected("p986_adaptive_replay", p986_rows)
    cumulative_summary = p985.summarize_selected("p984_plus_p986_cumulative", cumulative_rows)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in cumulative_rows)

    success = bool(
        control_pass
        and cumulative_summary["selected_count"] == 8
        and cumulative_summary["broad_relation_group_count"] >= 7
        and (cumulative_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and reconstruction_error_count == 0
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P987_CONTROL_FAILURE"
    elif reconstruction_error_count != 0:
        claim = "NEGATIVE_RESULT_P987_RECONSTRUCTION_ERRORS"
    elif cumulative_summary["selected_count"] != 8:
        claim = "NEGATIVE_RESULT_P987_UNEXPECTED_SELECTED_COUNT"
    elif cumulative_summary["broad_relation_group_count"] < 7:
        claim = "NEGATIVE_RESULT_P987_BROAD_GROUP_DEDUP_COLLAPSE"
    elif (cumulative_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P987_CUMULATIVE_HIGH_GAP_NOT_BELOW_RHO"
    elif success:
        claim = "P987_CUMULATIVE_HIGH_GAP_RELATION_SOURCE_BELOW_RHO"
    else:
        claim = "NEGATIVE_RESULT_P987_INVARIANT_FAILURE"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p984_source": str(p984_path),
            "p986_source": str(p986_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p984_source_sha256": sha256_file(p984_path),
            "p986_source_sha256": sha256_file(p986_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": p985.BROAD_LABEL,
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P987_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SELECTED-ROW-AUDIT: this reuses P984/P986 selected rows and does not rescan new windows.",
            "FALSE-POSITIVES-CHARGED: cumulative amortization charges every selected high-gap row.",
            "NO-PARITY-GUARD: P985 max-salt parity is excluded because P986 falsified it.",
            "NO-END-TO-END-BREAK: this is a relation-source component, not sparse linear algebra or target descent.",
        ],
        "method": "p987_p231_cumulative_high_gap_relation_source",
        "parameters": {
            "base_high_gap_rule": p985.HIGH_GAP_RULE,
            "broad_label": p985.BROAD_LABEL,
            "excluded_guard": "max_salt mod 2 in {0}",
            "source_artifacts": [str(p984_path), str(p986_path)],
        },
        "schema": SCHEMA,
        "source_context": {
            "p984_fresh_source_case_count": (p984.get("summary") or {}).get("fresh_source_case_count"),
            "p984_fresh_windows": sorted(((p984.get("summary") or {}).get("fresh_source_count_by_window") or {}).keys()),
            "p986_scanned_window_count": (p986.get("summary") or {}).get("scan_scanned_window_count"),
            "p986_scanned_windows": (p986.get("summary") or {}).get("scan_scanned_windows"),
            "p986_source_case_count": (p986.get("summary") or {}).get("scan_source_case_count"),
        },
        "source_controls": controls,
        "summaries": [p984_summary, p986_summary, cumulative_summary],
        "summary": {
            "control_pass": control_pass,
            "cumulative_validation_success": success,
            "reconstruction_error_count": reconstruction_error_count,
            **{f"p984_{key}": value for key, value in p984_summary.items()},
            **{f"p986_{key}": value for key, value in p986_summary.items()},
            **{f"cumulative_{key}": value for key, value in cumulative_summary.items()},
        },
        "p984_cases_compact": [p985.compact_case(row) for row in p984_rows],
        "p986_cases_compact": [p985.compact_case(row) for row in p986_rows],
        "cumulative_cases_compact": [p985.compact_case(row) for row in cumulative_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P987 contract path")
    parser.add_argument("--p984", default=str(DEFAULT_P984), help="P984 cumulative high-gap JSON")
    parser.add_argument("--p986", default=str(DEFAULT_P986), help="P986 adaptive high-gap JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} broad_groups={broad_groups} "
        "direct_sum={direct_sum} broad_amortized={broad_amortized} "
        "rank_hist={rank_hist} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["cumulative_selected_count"],
            broad_groups=summary["cumulative_broad_relation_group_count"],
            direct_sum=summary["cumulative_direct_sum_ops_over_rho"],
            broad_amortized=summary["cumulative_broad_direct_relation_amortized_ops_over_rho"],
            rank_hist=summary["cumulative_rank_histogram"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
