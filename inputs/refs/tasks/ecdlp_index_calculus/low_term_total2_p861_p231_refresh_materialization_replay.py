#!/usr/bin/env python3
"""P861 p231 refresh materialization and replay-supply audit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p850_split_lane_fresh_disjoint_validation as p850


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p861_p231_refresh_materialization_replay.md"
DEFAULT_NEGATIVE_SUMMARY = STATE_DIR / "low_term_total2_expanded_leaf_rescue_1152_1159_summary.json"
DEFAULT_P231_SUMMARY = STATE_DIR / "low_term_total2_p231_frozen_prefix_leaf_rescue_1160_1167_summary.json"
DEFAULT_P231_SAGE = STATE_DIR / "low_term_total2_ffe_sage_factor_p231_frozen_prefix_1160_1167_probe.json"
DEFAULT_P231_QROOT = (
    STATE_DIR / "low_term_total2_ffe_public_factor_quadratic_root_p231_frozen_prefix_1160_1167_probe.json"
)
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p861_p231_refresh_materialization_replay_probe.json"
SCHEMA = "ecdlp.low_term_total2_p861_p231_refresh_materialization_replay.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p850.int_value(value, default)


def float_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if value is not None:
            values.append(float(value))
    return values


def summary_counts(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "below_rho_case_count": int_value(summary.get("below_rho_case_count")),
        "best_case_present": summary.get("best_case") is not None,
        "selector_counts": summary.get("selector_counts") or {},
        "target_counts": summary.get("target_counts") or {},
        "verified_case_count": int_value(summary.get("verified_case_count")),
    }


def guard_threshold(p845_payload: dict[str, Any]) -> int:
    return int_value(p845_payload["selected_guard"]["guard"]["threshold"])


def qroot_guard_audit(qroot_payload: dict[str, Any], threshold: int) -> dict[str, Any]:
    best_policy = str((qroot_payload.get("summary") or {}).get("best_policy") or "")
    policy_rows = (qroot_payload.get("policy_rows") or {}).get(best_policy) or []
    active_rows = [row for row in policy_rows if row.get("chosen_candidate")]
    below_rows = [row for row in active_rows if row.get("public_factor_quadratic_root_beats_rho")]
    preserving_rows = [row for row in active_rows if row.get("quadratic_preserves_selected_root_pairs")]
    false_rows = [row for row in active_rows if row.get("chosen_false_positive_source")]
    sage_cache: dict[str, dict[str, Any]] = {}
    audited_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in active_rows:
        try:
            features = p850.candidate_surface_features(qroot_payload, row, sage_cache)
        except Exception as exc:  # pragma: no cover - preserve diagnostic in artifact.
            errors.append(
                {
                    "row_key": row.get("row_key"),
                    "surface_id": row.get("surface_id"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            continue
        surface_ffe_ops = int_value(features.get("surface_ffe_ops"))
        audited_rows.append(
            {
                "below_rho": bool(row.get("public_factor_quadratic_root_beats_rho")),
                "chosen_false_positive_source": bool(row.get("chosen_false_positive_source")),
                "ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
                "p845_rejected": surface_ffe_ops > threshold,
                "policy": best_policy,
                "preserves_selected_root_pairs": bool(row.get("quadratic_preserves_selected_root_pairs")),
                "row_key": row.get("row_key"),
                "selected_leaf_count": row.get("selected_leaf_count"),
                "surface_ffe_ops": surface_ffe_ops,
                "surface_id": row.get("surface_id"),
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
            }
        )
    rejected = [row for row in audited_rows if row.get("p845_rejected")]
    rejected_preserving = [row for row in rejected if row.get("preserves_selected_root_pairs")]
    rejected_false = [row for row in rejected if row.get("chosen_false_positive_source")]
    ratios = float_values(active_rows, "public_factor_quadratic_root_ops_over_rho")
    return {
        "active_row_count": len(active_rows),
        "audited_rows": audited_rows,
        "best_policy": best_policy,
        "charged_below_rho_row_count": len(below_rows),
        "error_count": len(errors),
        "errors": errors,
        "false_positive_row_count": len(false_rows),
        "guard_threshold": threshold,
        "max_ops_over_rho": max(ratios) if ratios else None,
        "mean_ops_over_rho": round(sum(ratios) / len(ratios), 8) if ratios else None,
        "min_ops_over_rho": min(ratios) if ratios else None,
        "p845_rejected_below_rho_row_count": sum(1 for row in rejected if row.get("below_rho")),
        "p845_rejected_false_positive_row_count": len(rejected_false),
        "p845_rejected_preserving_row_count": len(rejected_preserving),
        "p845_rejected_row_count": len(rejected),
        "preserving_row_count": len(preserving_rows),
        "surface_count": len(policy_rows),
    }


def determine_claim(negative: dict[str, Any], p231: dict[str, Any], guard: dict[str, Any]) -> str:
    if int_value(guard.get("error_count")):
        return "NEGATIVE_RESULT_P861_AUDIT_ERRORS"
    if int_value(p231.get("below_rho_case_count")) == 0:
        return "NEGATIVE_RESULT_P861_NO_P231_SOURCE_CASES"
    if int_value(guard.get("p845_rejected_row_count")) > 0 and int_value(guard.get("preserving_row_count")) > 0:
        if int_value(guard.get("false_positive_row_count")) > 0:
            return "P861_P231_REFRESH_REOPENS_REPLAY_SUPPLY_WITH_PRECISION_GAP"
        return "P861_P231_REFRESH_REOPENS_CLEAN_REPLAY_SUPPLY"
    if int_value(guard.get("preserving_row_count")) > 0:
        return "P861_P231_REFRESH_MATERIALIZES_QROOT_BUT_P845_REPLAY_SUPPLY_STARVED"
    if int_value(negative.get("below_rho_case_count")) == 0:
        return "NEGATIVE_RESULT_P861_REFRESH_NARROWS_TO_P231_PRECISION_OR_NEW_FAMILY"
    return "NEGATIVE_RESULT_P861_REFRESH_NO_MATERIALIZED_QROOT_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    negative_payload = load_json(args.negative_summary)
    p231_payload = load_json(args.p231_summary)
    sage_payload = load_json(args.p231_sage)
    qroot_payload = load_json(args.p231_qroot)
    p845_payload = load_json(args.p845)
    negative = summary_counts(negative_payload)
    p231 = summary_counts(p231_payload)
    threshold = guard_threshold(p845_payload)
    guard = qroot_guard_audit(qroot_payload, threshold)
    sage_summary = sage_payload.get("summary") or {}
    qroot_summary = qroot_payload.get("summary") or {}
    claim = determine_claim(negative, p231, guard)
    next_action = (
        "Build P862 to run the P859/P860 variable-anchor/source-case replay on the P861 p231 P845-rejected rows, while adding a public precision gate for the two false-positive qroot rows."
        if int_value(guard.get("p845_rejected_row_count")) > 0
        else "Build P862 as a precision-gated p231 row-selector refresh or generate the next p231 family window; current qroot rows do not reopen P845 rejected-row replay supply."
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "negative_summary": str(args.negative_summary),
            "p231_qroot": str(args.p231_qroot),
            "p231_sage": str(args.p231_sage),
            "p231_summary": str(args.p231_summary),
            "p845_source": str(args.p845),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "guard_audit": guard,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "SOURCE-FAMILY BOUNDARY: 1152_1159 low-term total-2 is a negative control; p231 1160_1167 is an adjacent public source family, not the same distribution.",
            "PRECISION BOUNDARY: below-rho qroot rows are not enough when false-positive selected factors remain.",
            "P845 BOUNDARY: replay supply means public surface_ffe_ops exceeds the saved P845 guard threshold, not that relation replay has already succeeded.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus relation-supply step, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p861_p231_refresh_materialization_replay",
        "negative_control": negative,
        "p231_source_summary": p231,
        "parameters": {
            "negative_window": "1152_1159",
            "p231_window": "1160_1167",
            "p845_surface_ffe_ops_threshold": threshold,
        },
        "qroot_summary": {
            "all_holdout_splits_below_rho": qroot_summary.get("all_holdout_splits_below_rho"),
            "all_holdout_splits_false_positive_free": qroot_summary.get("all_holdout_splits_false_positive_free"),
            "all_holdout_splits_preserve": qroot_summary.get("all_holdout_splits_preserve"),
            "best_policy": qroot_summary.get("best_policy"),
            "best_policy_summary": qroot_summary.get("best_policy_summary"),
            "surface_count": qroot_summary.get("surface_count"),
            "transfer_holdout_summary": qroot_summary.get("transfer_holdout_summary"),
        },
        "red_team_handoff": {
            "assumptions": [
                "The P845 surface slack guard remains the correct boundary for standalone factor rejection and relation-lane replay supply.",
                "The p231 frozen-prefix family is a legitimate source refresh candidate but must be labeled as adjacent-family evidence.",
                "False-positive qroot rows must be gated or routed separately before any stronger replay claim.",
            ],
            "evidence_so_far": [
                f"1152_1159 low-term total-2 below-rho cases: {negative.get('below_rho_case_count')}.",
                f"p231 1160_1167 below-rho cases: {p231.get('below_rho_case_count')}.",
                f"Best qroot policy {guard.get('best_policy')} has {guard.get('charged_below_rho_row_count')} below-rho rows, {guard.get('preserving_row_count')} preserving rows, and {guard.get('false_positive_row_count')} false-positive rows.",
                f"P845 rejected rows available for replay: {guard.get('p845_rejected_row_count')}.",
            ],
            "failure_modes": [
                "The p231 family may not replicate on future windows.",
                "False-positive factor rows may inflate below-rho counts unless a public precision gate is added.",
                "P845-rejected rows still need full P859/P860 variable-anchor/source-case replay; this artifact only audits supply.",
            ],
            "next_concrete_action": next_action,
            "status": "HYPOTHESIS" if claim.startswith("P861_") else "NEGATIVE RESULT",
        },
        "sage_summary": {
            "case_count": sage_summary.get("case_count"),
            "min_preserving_sage_factor_root_scan_ops_over_rho": sage_summary.get(
                "min_preserving_sage_factor_root_scan_ops_over_rho"
            ),
            "preserving_sage_factor_root_scan_below_rho_count": sage_summary.get(
                "preserving_sage_factor_root_scan_below_rho_count"
            ),
            "surface_count": sage_summary.get("surface_count"),
            "surfaces_with_any_preserving_sage_factor_candidate": sage_summary.get(
                "surfaces_with_any_preserving_sage_factor_candidate"
            ),
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "negative_below_rho_case_count": negative.get("below_rho_case_count"),
            "p231_below_rho_case_count": p231.get("below_rho_case_count"),
            "p231_verified_case_count": p231.get("verified_case_count"),
            "qroot_best_policy": guard.get("best_policy"),
            "qroot_below_rho_row_count": guard.get("charged_below_rho_row_count"),
            "qroot_false_positive_row_count": guard.get("false_positive_row_count"),
            "qroot_min_ops_over_rho": guard.get("min_ops_over_rho"),
            "qroot_preserving_row_count": guard.get("preserving_row_count"),
            "qroot_surface_count": guard.get("surface_count"),
            "p845_rejected_row_count": guard.get("p845_rejected_row_count"),
            "p845_rejected_preserving_row_count": guard.get("p845_rejected_preserving_row_count"),
            "p845_rejected_false_positive_row_count": guard.get("p845_rejected_false_positive_row_count"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--negative-summary", type=Path, default=DEFAULT_NEGATIVE_SUMMARY)
    parser.add_argument("--p231-summary", type=Path, default=DEFAULT_P231_SUMMARY)
    parser.add_argument("--p231-sage", type=Path, default=DEFAULT_P231_SAGE)
    parser.add_argument("--p231-qroot", type=Path, default=DEFAULT_P231_QROOT)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
