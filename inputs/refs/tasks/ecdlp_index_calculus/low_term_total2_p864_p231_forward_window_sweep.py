#!/usr/bin/env python3
"""P864 aggregate audit for p231 forward-window rejected-row replay."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p864_p231_forward_window_sweep.md"
DEFAULT_WINDOWS = ("1176_1183", "1184_1191")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p864_p231_forward_window_sweep_probe.json"
SCHEMA = "ecdlp.low_term_total2_p864_p231_forward_window_sweep.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def below_rho(value: Any) -> bool:
    return value is not None and float(value) < 1.0


def probe_path(window: str) -> Path:
    return STATE_DIR / f"low_term_total2_p864_p231_forward_window_{window}_probe.json"


def compact_rejected_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    direct_by_key = {
        (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            str(row.get("row_key")),
        ): row
        for row in payload.get("direct_replay_rows") or []
    }
    out = []
    for row in (payload.get("guard_audit") or {}).get("audited_rows") or []:
        if not row.get("p845_rejected"):
            continue
        key = (
            str(row.get("target")),
            int_value(row.get("transfer_index")),
            str(row.get("row_key")),
        )
        direct = direct_by_key.get(key) or {}
        variant = direct.get("verified_direct_variant") or {}
        source_case = direct.get("source_case") or {}
        out.append(
            {
                "candidate_factor_leaf_indices": row.get("candidate_factor_leaf_indices") or [],
                "direct_ops_over_rho": variant.get("ops_over_rho"),
                "direct_relation_count": (variant.get("union") or {}).get("union_relation_count"),
                "direct_rank": (variant.get("union") or {}).get("union_rank"),
                "direct_variant": variant.get("name"),
                "direct_verified": bool(variant.get("verified")),
                "p845_surface_ffe_ops": row.get("surface_ffe_ops"),
                "qroot_ops_over_rho": row.get("ops_over_rho"),
                "relation_discriminator_class": direct.get("relation_discriminator_class"),
                "row_key": row.get("row_key"),
                "source_case_ops_over_rho": source_case.get("ops_over_rho"),
                "source_case_relation_count": source_case.get("relation_count"),
                "source_case_rank": source_case.get("rank"),
                "source_case_row_keys": source_case.get("row_keys") or [],
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
                "union_derived_secret": (variant.get("union") or {}).get("union_derived_secret"),
            }
        )
    return out


def window_summary(window: str, payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    bundle_summary = (payload.get("bundle_summary") or {}).get("best_policy_summary") or {}
    rejected_rows = compact_rejected_rows(payload)
    return {
        "best_bundle_conservative_below_rho_group_count": summary.get(
            "best_bundle_conservative_below_rho_group_count"
        ),
        "best_bundle_conservative_ops_over_rho": bundle_summary.get("min_conservative_ops_over_rho"),
        "best_bundle_policy": summary.get("best_bundle_policy"),
        "best_bundle_selected_below_rho_group_count": summary.get("best_bundle_selected_below_rho_group_count"),
        "claim_status": summary.get("claim_status"),
        "direct_below_rho_verified_count": summary.get("direct_below_rho_verified_count"),
        "direct_verified_count": summary.get("direct_verified_count"),
        "error_count": summary.get("error_count"),
        "p231_below_rho_case_count": summary.get("p231_below_rho_case_count"),
        "p231_verified_case_count": summary.get("p231_verified_case_count"),
        "p845_rejected_false_positive_row_count": summary.get("p845_rejected_false_positive_row_count"),
        "p845_rejected_preserving_row_count": summary.get("p845_rejected_preserving_row_count"),
        "p845_rejected_row_count": summary.get("p845_rejected_row_count"),
        "qroot_below_rho_row_count": summary.get("qroot_below_rho_row_count"),
        "qroot_false_positive_row_count": summary.get("qroot_false_positive_row_count"),
        "qroot_max_ops_over_rho": summary.get("qroot_max_ops_over_rho"),
        "qroot_mean_ops_over_rho": summary.get("qroot_mean_ops_over_rho"),
        "qroot_min_ops_over_rho": summary.get("qroot_min_ops_over_rho"),
        "qroot_policy": summary.get("qroot_policy"),
        "qroot_preserving_row_count": summary.get("qroot_preserving_row_count"),
        "qroot_surface_count": summary.get("qroot_surface_count"),
        "rejected_rows": rejected_rows,
        "window": window,
    }


def determine_claim(summaries: list[dict[str, Any]]) -> str:
    if any(int_value(row.get("error_count")) for row in summaries):
        return "NEGATIVE_RESULT_P864_FORWARD_SWEEP_AUDIT_ERRORS"
    positive = [
        row
        for row in summaries
        if int_value(row.get("p845_rejected_row_count")) > 0
        and int_value(row.get("direct_below_rho_verified_count")) > 0
        and int_value(row.get("best_bundle_conservative_below_rho_group_count")) > 0
    ]
    if len(positive) == len(summaries) and summaries:
        return "P864_P231_FORWARD_SWEEP_REPLICATES_REJECTED_RELATION_LANE"
    if positive:
        return "P864_P231_FORWARD_SWEEP_PARTIAL_REJECTED_RELATION_LANE_REPLICATION"
    if any(int_value(row.get("p845_rejected_row_count")) > 0 for row in summaries):
        return "NEGATIVE_RESULT_P864_REJECTED_ROWS_DO_NOT_REPLAY_BELOW_RHO"
    if any(int_value(row.get("qroot_below_rho_row_count")) > 0 for row in summaries):
        return "NEGATIVE_RESULT_P864_QROOT_POSITIVE_BUT_P845_REJECTED_SUPPLY_STARVED"
    return "NEGATIVE_RESULT_P864_FORWARD_SWEEP_NO_QROOT_SIGNAL"


def aggregate_summary(summaries: list[dict[str, Any]], claim: str) -> dict[str, Any]:
    rejected_rows = [row for summary in summaries for row in summary.get("rejected_rows") or []]
    direct_ops = [
        float(row["direct_ops_over_rho"])
        for row in rejected_rows
        if row.get("direct_ops_over_rho") is not None
    ]
    bundle_ops = [
        float(summary["best_bundle_conservative_ops_over_rho"])
        for summary in summaries
        if summary.get("best_bundle_conservative_ops_over_rho") is not None
    ]
    return {
        "claim_status": claim,
        "direct_below_rho_verified_count": sum(int_value(row.get("direct_below_rho_verified_count")) for row in summaries),
        "error_count": sum(int_value(row.get("error_count")) for row in summaries),
        "max_bundle_conservative_ops_over_rho": max(bundle_ops) if bundle_ops else None,
        "max_direct_ops_over_rho": max(direct_ops) if direct_ops else None,
        "min_bundle_conservative_ops_over_rho": min(bundle_ops) if bundle_ops else None,
        "min_direct_ops_over_rho": min(direct_ops) if direct_ops else None,
        "p231_below_rho_case_count": sum(int_value(row.get("p231_below_rho_case_count")) for row in summaries),
        "p231_verified_case_count": sum(int_value(row.get("p231_verified_case_count")) for row in summaries),
        "p845_rejected_false_positive_row_count": sum(
            int_value(row.get("p845_rejected_false_positive_row_count")) for row in summaries
        ),
        "p845_rejected_preserving_row_count": sum(
            int_value(row.get("p845_rejected_preserving_row_count")) for row in summaries
        ),
        "p845_rejected_row_count": sum(int_value(row.get("p845_rejected_row_count")) for row in summaries),
        "positive_replay_window_count": sum(
            1
            for row in summaries
            if int_value(row.get("direct_below_rho_verified_count")) > 0
            and int_value(row.get("best_bundle_conservative_below_rho_group_count")) > 0
        ),
        "qroot_below_rho_row_count": sum(int_value(row.get("qroot_below_rho_row_count")) for row in summaries),
        "qroot_false_positive_row_count": sum(int_value(row.get("qroot_false_positive_row_count")) for row in summaries),
        "qroot_preserving_row_count": sum(int_value(row.get("qroot_preserving_row_count")) for row in summaries),
        "qroot_surface_count": sum(int_value(row.get("qroot_surface_count")) for row in summaries),
        "window_count": len(summaries),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    window_payloads = []
    for window in args.windows:
        path = probe_path(window)
        payload = load_json(path)
        window_payloads.append((window, path, payload))
    summaries = [window_summary(window, payload) for window, _, payload in window_payloads]
    claim = determine_claim(summaries)
    summary = aggregate_summary(summaries, claim)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "window_probes": {window: str(path) for window, path, _ in window_payloads},
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P864_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FORWARD-SWEEP BOUNDARY: this aggregates two adjacent p231 forward windows.",
            "PUBLIC-SELECTION BOUNDARY: replay candidates were selected by public qroot policy and the frozen P845 rejection gate.",
            "P845 BOUNDARY: rejected rows are relation-lane inputs, not standalone preserving factor packets.",
            "POLLARD-RHO BOUNDARY: below-rho relation-lane recovery is evidence for an index-calculus route, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p864_p231_forward_window_sweep",
        "red_team_handoff": {
            "assumptions": [
                "The P845 surface slack guard is a stable public selection boundary across p231 windows.",
                "The P862/P863 direct and source-case bundle replay costs are comparable across the adjacent p231 windows.",
                "Each window is counted separately; repeated row names across transfers do not imply cross-window independence.",
            ],
            "evidence_so_far": [
                f"Positive replay windows: {summary.get('positive_replay_window_count')}/{summary.get('window_count')}.",
                f"P845-rejected rows: {summary.get('p845_rejected_row_count')}; rejected false positives: {summary.get('p845_rejected_false_positive_row_count')}; rejected preserving rows: {summary.get('p845_rejected_preserving_row_count')}.",
                f"Direct below-rho verified rows: {summary.get('direct_below_rho_verified_count')}.",
                f"Bundle conservative below-rho ops/rho range: {summary.get('min_bundle_conservative_ops_over_rho')}..{summary.get('max_bundle_conservative_ops_over_rho')}.",
            ],
            "failure_modes": [
                "The forward windows may share frozen-prefix structure and therefore overstate independent replication.",
                "The source-case bundle costs still need sparse matrix/rank and target-descent integration.",
                "A rejected-row supply rate over only three positive p231 windows is not enough for asymptotic or deployment relevance.",
            ],
            "next_concrete_action": (
                "Build P865 as a multi-window sparse-rank and target-descent accounting audit over P862 plus P864 rejected-row outputs, deduplicating source-case scans and estimating relation supply versus Pollard rho."
            ),
            "status": "OBSERVATION" if claim.startswith("P864_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summary,
        "window_summaries": summaries,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS))
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
