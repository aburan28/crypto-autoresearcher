#!/usr/bin/env python3
"""P843 disjoint-bank public-factor replication audit.

P842 found a heldout public motif-compression signal, but the next gate is
whether a public selector survives disjoint transfer banks under a stricter
nonzero-slice criterion.  This audit reuses existing fresh public-factor
quadratic-root artifacts, chooses one public policy on early fresh banks, and
scores it on later disjoint banks.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p843_public_factor_disjoint_replication_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p843_public_factor_disjoint_replication_audit.md"
SCHEMA = "ecdlp.low_term_total2_p843_public_factor_disjoint_replication_audit.v1"

DEFAULT_ARTIFACTS = [
    (
        "fresh_96_127",
        "calibration",
        STATE_DIR
        / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_factor_quadratic_root_fresh_96_127_probe.json",
    ),
    (
        "fresh_128_135",
        "calibration",
        STATE_DIR
        / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_factor_quadratic_root_fresh_128_135_probe.json",
    ),
    (
        "fresh_312_327_expanded",
        "heldout",
        STATE_DIR
        / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_factor_quadratic_root_fresh_312_327_expanded_probe.json",
    ),
    (
        "fresh_360_375_expanded",
        "heldout",
        STATE_DIR
        / "frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_public_factor_quadratic_root_fresh_360_375_expanded_probe.json",
    ),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def ops_ratio(row: dict[str, Any]) -> float | None:
    value = row.get("public_factor_quadratic_root_ops_over_rho")
    if value is None:
        return None
    return float(value)


def is_nonzero_slice(row: dict[str, Any]) -> bool:
    return int(row.get("factor_zero_leaf_count") or 0) > 0 and int(row.get("selected_valid_leaf_count") or 0) > 0


def is_strict_success(row: dict[str, Any]) -> bool:
    return (
        bool(row.get("quadratic_preserves_selected_root_pairs"))
        and bool(row.get("public_factor_quadratic_root_beats_rho"))
        and is_nonzero_slice(row)
        and not bool(row.get("chosen_false_positive_source"))
        and not (row.get("missing_selected_root_pairs") or [])
    )


def row_digest(row: dict[str, Any], bank_id: str, role: str) -> dict[str, Any]:
    return {
        "bank_id": bank_id,
        "chosen_candidate": row.get("chosen_candidate"),
        "false_positive": bool(row.get("chosen_false_positive_source")),
        "nonzero_slice": is_nonzero_slice(row),
        "ops_over_rho": ops_ratio(row),
        "policy": row.get("policy"),
        "preserves": bool(row.get("quadratic_preserves_selected_root_pairs")),
        "role": role,
        "row_key": row.get("row_key"),
        "selected_root_pair_count": int(row.get("selected_root_pair_count") or 0),
        "strict_preserving_below_rho": is_strict_success(row),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
    }


def metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [ops_ratio(row) for row in rows if ops_ratio(row) is not None]
    preserving = [row for row in rows if row.get("quadratic_preserves_selected_root_pairs")]
    below = [row for row in rows if row.get("public_factor_quadratic_root_beats_rho")]
    nonzero = [row for row in rows if is_nonzero_slice(row)]
    false_positive = [row for row in rows if row.get("chosen_false_positive_source")]
    strict = [row for row in rows if is_strict_success(row)]
    missing_events = sum(len(row.get("missing_selected_root_pairs") or []) for row in rows)
    extra_events = sum(len(row.get("extra_selected_root_pairs") or []) for row in rows)
    return {
        "below_rho_count": len(below),
        "below_rho_rate": safe_ratio(len(below), len(rows)),
        "extra_selected_root_pair_event_count": int(extra_events),
        "false_positive_count": len(false_positive),
        "max_ops_over_rho": round(max(ratios), 8) if ratios else None,
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_ops_over_rho": round(min(ratios), 8) if ratios else None,
        "missing_selected_root_pair_event_count": int(missing_events),
        "nonzero_slice_count": len(nonzero),
        "nonzero_slice_rate": safe_ratio(len(nonzero), len(rows)),
        "preserving_count": len(preserving),
        "preserving_rate": safe_ratio(len(preserving), len(rows)),
        "strict_preserving_below_rho_count": len(strict),
        "strict_preserving_below_rho_rate": safe_ratio(len(strict), len(rows)),
        "surface_count": len(rows),
    }


def load_artifacts(artifacts: list[tuple[str, str, Path]]) -> list[dict[str, Any]]:
    loaded = []
    for bank_id, role, path in artifacts:
        payload = load_json(path)
        policy_rows = payload.get("policy_rows") or {}
        transfer_indices = [
            int(row["transfer_index"])
            for rows in policy_rows.values()
            for row in rows
            if row.get("transfer_index") is not None
        ]
        loaded.append(
            {
                "bank_id": bank_id,
                "path": str(path),
                "payload": payload,
                "role": role,
                "summary": payload.get("summary") or {},
                "transfer_range": [
                    min(transfer_indices) if transfer_indices else None,
                    max(transfer_indices) if transfer_indices else None,
                ],
            }
        )
    return loaded


def policy_names(loaded: list[dict[str, Any]]) -> list[str]:
    common: set[str] | None = None
    for item in loaded:
        names = set((item["payload"].get("policy_rows") or {}).keys())
        common = names if common is None else common & names
    return sorted(common or set())


def rows_for_policy(loaded: list[dict[str, Any]], policy: str, role: str | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for item in loaded:
        if role is not None and item["role"] != role:
            continue
        for row in (item["payload"].get("policy_rows") or {}).get(policy) or []:
            copied = dict(row)
            copied["_bank_id"] = item["bank_id"]
            copied["_role"] = item["role"]
            rows.append(copied)
    return rows


def choose_policy(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(
        summaries,
        key=lambda item: (
            int(item["calibration_metrics"]["strict_preserving_below_rho_count"]),
            -int(item["calibration_metrics"]["false_positive_count"]),
            int(item["calibration_metrics"]["preserving_count"]),
            int(item["calibration_metrics"]["nonzero_slice_count"]),
            -(
                float(item["calibration_metrics"]["mean_ops_over_rho"])
                if item["calibration_metrics"]["mean_ops_over_rho"] is not None
                else 10**9
            ),
            item["policy"],
        ),
        reverse=True,
    )[0]


def summarize_native_best(loaded: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in loaded:
        summary = item["summary"]
        rows.append(
            {
                "bank_id": item["bank_id"],
                "best_policy": summary.get("best_policy"),
                "best_policy_summary": summary.get("best_policy_summary"),
                "path": item["path"],
                "role": item["role"],
                "transfer_range": item["transfer_range"],
            }
        )
    return rows


def claim_status(heldout_metrics: dict[str, Any]) -> str:
    strict = int(heldout_metrics["strict_preserving_below_rho_count"])
    false_positives = int(heldout_metrics["false_positive_count"])
    preserving = int(heldout_metrics["preserving_count"])
    below = int(heldout_metrics["below_rho_count"])
    if strict > 0 and false_positives == 0:
        return "P843_DISJOINT_PUBLIC_FACTOR_POLICY_REPLICATES_STRICT_BELOW_RHO"
    if strict > 0:
        return "P843_DISJOINT_PUBLIC_FACTOR_POLICY_REPLICATES_WITH_FALSE_POSITIVES"
    if preserving > 0 and below > 0:
        return "P843_DISJOINT_PUBLIC_FACTOR_POLICY_HAS_MIXED_HELDOUT_SIGNAL"
    if preserving > 0:
        return "P843_DISJOINT_PUBLIC_FACTOR_POLICY_PRESERVES_ABOVE_RHO"
    return "NEGATIVE_RESULT_P843_PUBLIC_FACTOR_POLICY_NO_DISJOINT_REPLICATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    loaded = load_artifacts(DEFAULT_ARTIFACTS)
    policies = policy_names(loaded)
    policy_summaries = []
    for policy in policies:
        calibration_rows = rows_for_policy(loaded, policy, "calibration")
        heldout_rows = rows_for_policy(loaded, policy, "heldout")
        policy_summaries.append(
            {
                "calibration_metrics": metrics(calibration_rows),
                "heldout_metrics": metrics(heldout_rows),
                "policy": policy,
            }
        )

    selected = choose_policy(policy_summaries)
    selected_policy = str(selected["policy"])
    selected_calibration_rows = rows_for_policy(loaded, selected_policy, "calibration")
    selected_heldout_rows = rows_for_policy(loaded, selected_policy, "heldout")
    heldout_metrics = metrics(selected_heldout_rows)
    strict_heldout = [row for row in selected_heldout_rows if is_strict_success(row)]
    false_positive_heldout = [row for row in selected_heldout_rows if row.get("chosen_false_positive_source")]

    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "script": str(Path(__file__)),
            "sources": [
                {
                    "bank_id": item["bank_id"],
                    "path": item["path"],
                    "role": item["role"],
                    "transfer_range": item["transfer_range"],
                }
                for item in loaded
            ],
        },
        "calibration": {
            "metrics": metrics(selected_calibration_rows),
            "row_count": len(selected_calibration_rows),
            "strict_rows": [
                row_digest(row, str(row["_bank_id"]), str(row["_role"]))
                for row in selected_calibration_rows
                if is_strict_success(row)
            ],
        },
        "claim_status": claim_status(heldout_metrics),
        "created_at": now_iso(),
        "heldout": {
            "false_positive_rows": [
                row_digest(row, str(row["_bank_id"]), str(row["_role"]))
                for row in false_positive_heldout
            ],
            "metrics": heldout_metrics,
            "row_count": len(selected_heldout_rows),
            "strict_rows": [
                row_digest(row, str(row["_bank_id"]), str(row["_role"]))
                for row in strict_heldout
            ],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "DISJOINT-TRANSFER GATE: calibration banks are fresh_96_127 and fresh_128_135; heldout banks are fresh_312_327_expanded and fresh_360_375_expanded.",
            "PUBLIC-POLICY GATE: the same policy name is selected on calibration and scored on heldout.",
            "NONZERO-SLICE GATE: strict success requires a nonzero factor-zero leaf and a selected-valid leaf.",
            "POLLARD-RHO BOUNDARY: this is a relation-generation/root-recovery subproblem and not a complete faster-than-rho ECDLP algorithm.",
            "NO DEPLOYED-CURVE CLAIM: no production-key relevance or deployed-prime break is implied.",
        ],
        "method": "p843_public_factor_disjoint_replication_audit",
        "native_best_by_bank": summarize_native_best(loaded),
        "parameters": {
            "calibration_banks": [item["bank_id"] for item in loaded if item["role"] == "calibration"],
            "heldout_banks": [item["bank_id"] for item in loaded if item["role"] == "heldout"],
            "policy_selection": "maximize calibration strict_preserving_below_rho_count, then minimize false positives, then preserve/nonzero counts and mean ops/rho",
            "strict_success_definition": [
                "quadratic_preserves_selected_root_pairs",
                "public_factor_quadratic_root_beats_rho",
                "factor_zero_leaf_count > 0",
                "selected_valid_leaf_count > 0",
                "chosen_false_positive_source is false",
                "missing_selected_root_pairs is empty",
            ],
        },
        "policy_summaries": policy_summaries,
        "red_team_handoff": {
            "assumptions": [
                "Existing fresh public-factor artifacts are valid disjoint transfer-bank evidence.",
                "Policy-name stability is a reasonable public selector proxy across banks.",
                "Nonzero selected-valid leaves are a minimal direct-constructor compatibility gate.",
            ],
            "failure_modes": [
                "The chosen policy may replicate only on the same target family.",
                "A false-positive source can make a below-rho row unusable even when root recovery is cheap.",
                "The artifact-level policy selector may still hide factorization backend cost not present in the current score.",
            ],
            "next_concrete_action": (
                "If strict heldout replication survives, build P844 to replay the selected heldout rows through the direct relation constructor; "
                "if it fails, isolate policy features that caused false positives and add a target/leaf guard."
            ),
        },
        "schema": SCHEMA,
        "selected_policy": selected,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "heldout_metrics": payload["heldout"]["metrics"],
                "selected_policy": payload["selected_policy"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
