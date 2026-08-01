#!/usr/bin/env python3
"""P863 p231 forward-window rejected-row replication audit."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p850_split_lane_fresh_disjoint_validation as p850
import low_term_total2_p862_p231_rejected_relation_lane_replay as p862


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p863_p231_forward_window_replication.md"
DEFAULT_P231_SUMMARY = STATE_DIR / "low_term_total2_p231_frozen_prefix_leaf_rescue_1168_1175_summary.json"
DEFAULT_P231_SAGE = STATE_DIR / "low_term_total2_ffe_sage_factor_p231_frozen_prefix_1168_1175_probe.json"
DEFAULT_P231_QROOT = (
    STATE_DIR / "low_term_total2_ffe_public_factor_quadratic_root_p231_frozen_prefix_1168_1175_probe.json"
)
DEFAULT_P845 = STATE_DIR / "low_term_total2_p845_public_factor_surface_slack_guard_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p863_p231_forward_window_replication_probe.json"
SCHEMA = "ecdlp.low_term_total2_p863_p231_forward_window_replication.v1"


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


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def summary_counts(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "below_rho_case_count": int_value(summary.get("below_rho_case_count")),
        "best_case": summary.get("best_case"),
        "selector_counts": summary.get("selector_counts") or {},
        "target_counts": summary.get("target_counts") or {},
        "verified_case_count": int_value(summary.get("verified_case_count")),
    }


def guard_threshold(p845_payload: dict[str, Any]) -> int:
    return int_value(p845_payload["selected_guard"]["guard"]["threshold"])


def float_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if value is not None:
            values.append(float(value))
    return values


def compact_qroot_row(row: dict[str, Any], features: dict[str, Any], threshold: int) -> dict[str, Any]:
    surface_ffe_ops = int_value(features.get("surface_ffe_ops"))
    return {
        "candidate_factor_leaf_indices": row.get("factor_zero_leaf_indices") or [],
        "chosen_candidate": row.get("chosen_candidate"),
        "chosen_false_positive_source": bool(row.get("chosen_false_positive_source")),
        "ops_over_rho": row.get("public_factor_quadratic_root_ops_over_rho"),
        "p845_rejected": surface_ffe_ops > threshold,
        "preserves_selected_root_pairs": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "public_factor_quadratic_root_beats_rho": bool(row.get("public_factor_quadratic_root_beats_rho")),
        "row_key": row.get("row_key"),
        "selected_leaf_count": row.get("selected_leaf_count"),
        "surface_ffe_ops": surface_ffe_ops,
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "transfer_index": int_value(row.get("transfer_index")),
    }


def qroot_guard_audit(
    qroot_payload: dict[str, Any],
    threshold: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    best_policy = str((qroot_payload.get("summary") or {}).get("best_policy") or "")
    policy_rows = (qroot_payload.get("policy_rows") or {}).get(best_policy) or []
    active_rows = [row for row in policy_rows if row.get("chosen_candidate")]
    sage_cache: dict[str, dict[str, Any]] = {}
    audited_rows: list[dict[str, Any]] = []
    replay_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for row in active_rows:
        try:
            features = p850.candidate_surface_features(qroot_payload, row, sage_cache)
        except Exception as exc:  # pragma: no cover - diagnostic preservation.
            errors.append(
                {
                    "error": f"{type(exc).__name__}: {exc}",
                    "row_key": row.get("row_key"),
                    "surface_id": row.get("surface_id"),
                }
            )
            continue
        compact = compact_qroot_row(row, features, threshold)
        audited_rows.append(compact)
        if compact["p845_rejected"]:
            replay_rows.append({**row, "_candidate_surface_features": features})

    rejected = [row for row in audited_rows if row.get("p845_rejected")]
    below_rows = [row for row in audited_rows if row.get("public_factor_quadratic_root_beats_rho")]
    preserving_rows = [row for row in audited_rows if row.get("preserves_selected_root_pairs")]
    false_rows = [row for row in audited_rows if row.get("chosen_false_positive_source")]
    rejected_below = [row for row in rejected if row.get("public_factor_quadratic_root_beats_rho")]
    rejected_preserving = [row for row in rejected if row.get("preserves_selected_root_pairs")]
    rejected_false = [row for row in rejected if row.get("chosen_false_positive_source")]
    ratios = float_values(active_rows, "public_factor_quadratic_root_ops_over_rho")
    return (
        {
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
            "p845_rejected_below_rho_row_count": len(rejected_below),
            "p845_rejected_false_positive_row_count": len(rejected_false),
            "p845_rejected_preserving_row_count": len(rejected_preserving),
            "p845_rejected_row_count": len(rejected),
            "preserving_row_count": len(preserving_rows),
            "surface_count": len(policy_rows),
        },
        replay_rows,
    )


def empty_bundle_summary() -> tuple[dict[str, list[dict[str, Any]]], dict[str, dict[str, Any]], dict[str, Any]]:
    rows_by_policy = {policy: [] for policy in p862.p859.POLICIES}
    summaries = {policy: p862.summarize_bundle_policy([]) for policy in p862.p859.POLICIES}
    best_policy = p862.p859.POLICIES[0]
    return rows_by_policy, summaries, {"best_policy": best_policy, "best_policy_summary": summaries[best_policy]}


def replay_rejected_rows(
    args: argparse.Namespace,
    qroot_payload: dict[str, Any],
    replay_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    if not replay_rows:
        group_rows_by_policy, policy_summaries, bundle_summary = empty_bundle_summary()
        direct = p862.direct_summary([])
        return {
            "bundle_group_rows": group_rows_by_policy,
            "bundle_policy_summaries": policy_summaries,
            "bundle_summary": bundle_summary,
            "direct_replay_rows": [],
            "direct_summary": direct,
            "errors": [],
        }

    verifier = p862.p848.relation_probe.load_verifier_module()
    records = verifier.load_records()
    signature_cache: dict[str, dict[str, Any]] = {}
    context_cache: dict[
        tuple[Any, ...],
        tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]],
    ] = {}
    direct_rows = [
        p850.analyze_rejected_row(
            verifier,
            records,
            args.p231_qroot,
            qroot_payload,
            row,
            row["_candidate_surface_features"],
            signature_cache,
            context_cache,
            args.max_variants,
        )
        for row in replay_rows
    ]
    rows_by_policy, bundle_errors = p862.collect_bundle_policy_rows(
        verifier,
        records,
        args.p231_qroot,
        qroot_payload,
        direct_rows,
    )
    group_rows_by_policy, policy_summaries, bundle_summary = p862.summarize_bundles(rows_by_policy)
    direct = p862.direct_summary(direct_rows)
    all_errors = [
        {"source": "direct", **row}
        for row in direct_rows
        if row.get("error")
    ] + [{"source": "bundle", **row} for row in bundle_errors]
    return {
        "bundle_group_rows": group_rows_by_policy,
        "bundle_policy_summaries": policy_summaries,
        "bundle_summary": bundle_summary,
        "direct_replay_rows": [p862.compact_direct_row(row) for row in direct_rows],
        "direct_summary": direct,
        "errors": all_errors,
    }


def determine_claim(source: dict[str, Any], guard: dict[str, Any], replay: dict[str, Any]) -> str:
    if int_value(guard.get("error_count")) or replay.get("errors"):
        return "NEGATIVE_RESULT_P863_AUDIT_ERRORS"
    if int_value(source.get("below_rho_case_count")) == 0:
        return "NEGATIVE_RESULT_P863_FORWARD_WINDOW_NO_SOURCE_SIGNAL"
    if int_value(guard.get("p845_rejected_row_count")) == 0:
        if int_value(guard.get("charged_below_rho_row_count")) > 0:
            return "NEGATIVE_RESULT_P863_FORWARD_QROOT_POSITIVE_BUT_P845_REJECTED_SUPPLY_STARVED"
        return "NEGATIVE_RESULT_P863_FORWARD_WINDOW_NO_QROOT_SIGNAL"

    direct_below = int_value((replay.get("direct_summary") or {}).get("below_rho_direct_verified_count")) > 0
    best_summary = (replay.get("bundle_summary") or {}).get("best_policy_summary") or {}
    bundle_selected = int_value(best_summary.get("groups_with_verified_pair_selected_cost_below_rho")) > 0
    bundle_streaming = int_value(best_summary.get("groups_with_streaming_below_rho_verified_pair")) > 0
    bundle_conservative = int_value(best_summary.get("groups_with_conservative_below_rho_verified_pair")) > 0
    if direct_below and bundle_conservative:
        return "P863_P231_FORWARD_REJECTED_ROWS_VERIFY_AND_BUNDLE_PAIR_BELOW_RHO"
    if bundle_conservative:
        return "P863_P231_FORWARD_REJECTED_BUNDLE_PAIR_BELOW_RHO"
    if direct_below and bundle_streaming:
        return "P863_P231_FORWARD_REJECTED_ROWS_VERIFY_AND_STREAMING_BUNDLE_PAIR_BELOW_RHO"
    if direct_below and bundle_selected:
        return "P863_P231_FORWARD_REJECTED_ROWS_VERIFY_AND_SELECTED_BUNDLE_PAIR_BELOW_RHO"
    if direct_below:
        return "P863_P231_FORWARD_REJECTED_ROWS_VERIFY_AS_DIRECT_RELATIONS"
    if bundle_selected:
        return "P863_P231_FORWARD_REJECTED_BUNDLE_SELECTED_PAIR_ONLY"
    return "NEGATIVE_RESULT_P863_FORWARD_REJECTED_RELATION_REPLAY_NOT_FOUND"


def claim_taxonomy(claim: str) -> str:
    if claim.startswith("NEGATIVE_RESULT_"):
        return "NEGATIVE RESULT"
    return "OBSERVATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    source_payload = load_json(args.p231_summary)
    sage_payload = load_json(args.p231_sage)
    qroot_payload = load_json(args.p231_qroot)
    p845_payload = load_json(args.p845)
    source = summary_counts(source_payload)
    threshold = guard_threshold(p845_payload)
    guard, replay_rows = qroot_guard_audit(qroot_payload, threshold)
    replay = replay_rejected_rows(args, qroot_payload, replay_rows)
    sage_summary = sage_payload.get("summary") or {}
    qroot_summary = qroot_payload.get("summary") or {}
    claim = determine_claim(source, guard, replay)
    best_bundle_summary = (replay.get("bundle_summary") or {}).get("best_policy_summary") or {}
    next_action = (
        "Build P864 as a p231 forward-window sweep over 1176_1183 and 1184_1191 with the same P845 gate, then replay the first window that emits public P845-rejected rows; keep non-rejected false-positive qroot rows as precision controls only."
        if int_value(guard.get("p845_rejected_row_count")) == 0
        else "Build P864 as a sparse-rank and target-descent audit for replicated p231 rejected-row relation-lane outputs."
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p231_qroot": str(args.p231_qroot),
            "p231_sage": str(args.p231_sage),
            "p231_summary": str(args.p231_summary),
            "p845_source": str(args.p845),
            "script": str(Path(__file__)),
        },
        "bundle_group_rows": replay.get("bundle_group_rows"),
        "bundle_policy_summaries": replay.get("bundle_policy_summaries"),
        "bundle_summary": replay.get("bundle_summary"),
        "claim_status": claim,
        "claim_taxonomy": claim_taxonomy(claim),
        "created_at": now_iso(),
        "direct_replay_rows": replay.get("direct_replay_rows"),
        "direct_summary": replay.get("direct_summary"),
        "errors": replay.get("errors") or guard.get("errors") or [],
        "guard_audit": guard,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FORWARD-WINDOW BOUNDARY: this is the adjacent p231 window 1168_1175, not asymptotic evidence.",
            "PUBLIC-SELECTION BOUNDARY: replay candidates must pass public qroot selection and the frozen P845 rejection gate.",
            "P845 BOUNDARY: surface_ffe_ops equal to the threshold is kept; only rows with surface_ffe_ops greater than the threshold are rejected.",
            "PRECISION-CONTROL BOUNDARY: non-rejected false-positive qroot rows are controls, not P862 rejected-row replay supply.",
            "POLLARD-RHO BOUNDARY: this is relation-supply evidence for an index-calculus path, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p863_p231_forward_window_replication",
        "p231_source_summary": source,
        "parameters": {
            "bundle_policies": list(p862.p859.POLICIES),
            "event_policy_after_scan": p862.p859.EVENT_POLICY,
            "max_variants": args.max_variants,
            "p231_window": args.window,
            "p845_surface_ffe_ops_threshold": threshold,
            "qroot_policy": guard.get("best_policy"),
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
                "The saved P845 threshold remains the correct public rejection boundary for the p231 forward window.",
                "The p231 frozen-prefix forward windows are close enough to test replication, but each window must be reported separately.",
                "Non-rejected qroot rows may be useful precision controls but are not counted as rejected-row replay supply.",
            ],
            "evidence_so_far": [
                f"Forward source below-rho cases: {source.get('below_rho_case_count')}/{source.get('verified_case_count')}.",
                f"Best qroot policy {guard.get('best_policy')} has {guard.get('charged_below_rho_row_count')} below-rho rows, {guard.get('preserving_row_count')} preserving rows, and {guard.get('false_positive_row_count')} false-positive rows.",
                f"P845 rejected rows available for replay: {guard.get('p845_rejected_row_count')}.",
                f"Direct below-rho verified replay rows: {(replay.get('direct_summary') or {}).get('below_rho_direct_verified_count')}/{(replay.get('direct_summary') or {}).get('direct_replay_row_count')}.",
                f"Best bundle conservative below-rho groups: {best_bundle_summary.get('groups_with_conservative_below_rho_verified_pair')}.",
            ],
            "failure_modes": [
                "The P862 rejected-row signal may be localized to transfer 1167.",
                "The P845 threshold may reject too rarely in adjacent p231 windows, starving replay even when qroot materialization is positive.",
                "A non-rejected false-positive qroot row can be relation-useful, but promoting it would change the public selection rule and must be tested under a separate contract.",
            ],
            "next_concrete_action": next_action,
            "status": claim_taxonomy(claim),
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
            "best_bundle_conservative_below_rho_group_count": best_bundle_summary.get(
                "groups_with_conservative_below_rho_verified_pair"
            ),
            "best_bundle_policy": (replay.get("bundle_summary") or {}).get("best_policy"),
            "best_bundle_selected_below_rho_group_count": best_bundle_summary.get(
                "groups_with_verified_pair_selected_cost_below_rho"
            ),
            "best_bundle_streaming_below_rho_group_count": best_bundle_summary.get(
                "groups_with_streaming_below_rho_verified_pair"
            ),
            "claim_status": claim,
            "direct_below_rho_verified_count": (replay.get("direct_summary") or {}).get(
                "below_rho_direct_verified_count"
            ),
            "direct_verified_count": (replay.get("direct_summary") or {}).get("direct_verified_count"),
            "error_count": len(replay.get("errors") or []) + int_value(guard.get("error_count")),
            "p231_below_rho_case_count": source.get("below_rho_case_count"),
            "p231_verified_case_count": source.get("verified_case_count"),
            "p845_rejected_false_positive_row_count": guard.get("p845_rejected_false_positive_row_count"),
            "p845_rejected_preserving_row_count": guard.get("p845_rejected_preserving_row_count"),
            "p845_rejected_row_count": guard.get("p845_rejected_row_count"),
            "p845_surface_ffe_ops_threshold": threshold,
            "qroot_below_rho_row_count": guard.get("charged_below_rho_row_count"),
            "qroot_false_positive_row_count": guard.get("false_positive_row_count"),
            "qroot_max_ops_over_rho": guard.get("max_ops_over_rho"),
            "qroot_mean_ops_over_rho": guard.get("mean_ops_over_rho"),
            "qroot_min_ops_over_rho": guard.get("min_ops_over_rho"),
            "qroot_policy": guard.get("best_policy"),
            "qroot_preserving_row_count": guard.get("preserving_row_count"),
            "qroot_surface_count": guard.get("surface_count"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p231-summary", type=Path, default=DEFAULT_P231_SUMMARY)
    parser.add_argument("--p231-sage", type=Path, default=DEFAULT_P231_SAGE)
    parser.add_argument("--p231-qroot", type=Path, default=DEFAULT_P231_QROOT)
    parser.add_argument("--p845", type=Path, default=DEFAULT_P845)
    parser.add_argument("--max-variants", type=int, default=2048)
    parser.add_argument("--window", default="1168_1175")
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
