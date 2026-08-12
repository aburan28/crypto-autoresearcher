#!/usr/bin/env python3
"""P865 multi-window accounting for p231 rejected-row relation supply."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p865_p231_multi_window_accounting.md"
DEFAULT_P861 = STATE_DIR / "low_term_total2_p861_p231_refresh_materialization_replay_probe.json"
DEFAULT_P862 = STATE_DIR / "low_term_total2_p862_p231_rejected_relation_lane_replay_probe.json"
DEFAULT_P863 = STATE_DIR / "low_term_total2_p863_p231_forward_window_replication_probe.json"
DEFAULT_P864 = STATE_DIR / "low_term_total2_p864_p231_forward_window_sweep_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p865_p231_multi_window_accounting_probe.json"
SCHEMA = "ecdlp.low_term_total2_p865_p231_multi_window_accounting.v1"


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


def float_values(rows: list[dict[str, Any]], key: str) -> list[float]:
    values = []
    for row in rows:
        value = row.get(key)
        if value is not None:
            values.append(float(value))
    return values


def source_group_key(row: dict[str, Any]) -> tuple[str, int, tuple[str, ...]]:
    return (
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        tuple(str(item) for item in (row.get("source_case_row_keys") or [])),
    )


def p862_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    bundle_ops = ((payload.get("bundle_summary") or {}).get("best_policy_summary") or {}).get(
        "min_conservative_ops_over_rho"
    )
    bundle_policy = (payload.get("bundle_summary") or {}).get("best_policy")
    for row in payload.get("direct_replay_rows") or []:
        variant = row.get("verified_direct_variant") or {}
        source_case = row.get("source_case") or {}
        union = variant.get("union") or {}
        rows.append(
            {
                "candidate_factor_leaf_indices": row.get("candidate_factor_leaf_indices") or [],
                "direct_ops_over_rho": variant.get("ops_over_rho"),
                "direct_rank": union.get("union_rank"),
                "direct_relation_count": union.get("union_relation_count"),
                "direct_variant": variant.get("name"),
                "direct_verified": bool(variant.get("verified")),
                "p845_surface_ffe_ops": row.get("p845_surface_ffe_ops"),
                "qroot_ops_over_rho": row.get("qroot_ops_over_rho"),
                "relation_discriminator_class": row.get("relation_discriminator_class"),
                "row_key": row.get("row_key"),
                "source": "P862",
                "source_case_ops_over_rho": source_case.get("ops_over_rho"),
                "source_case_rank": source_case.get("rank"),
                "source_case_relation_count": source_case.get("relation_count"),
                "source_case_row_keys": source_case.get("row_keys") or [],
                "target": row.get("target"),
                "transfer_index": row.get("transfer_index"),
                "union_derived_secret": union.get("union_derived_secret"),
                "window": "1160_1167",
                "best_bundle_policy": bundle_policy,
                "bundle_conservative_ops_over_rho": bundle_ops,
            }
        )
    return rows


def p864_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for summary in payload.get("window_summaries") or []:
        bundle_policy = summary.get("best_bundle_policy")
        bundle_ops = summary.get("best_bundle_conservative_ops_over_rho")
        for row in summary.get("rejected_rows") or []:
            rows.append(
                {
                    **row,
                    "source": "P864",
                    "union_derived_secret": row.get("union_derived_secret"),
                    "window": summary.get("window"),
                    "best_bundle_policy": bundle_policy,
                    "bundle_conservative_ops_over_rho": bundle_ops,
                }
            )
    return rows


def dedup_groups(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, tuple[str, ...]], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[source_group_key(row)].append(row)
    out = []
    for key, group_rows in sorted(grouped.items(), key=lambda item: (item[0][0], item[0][1], item[0][2])):
        direct_ops = float_values(group_rows, "direct_ops_over_rho")
        qroot_ops = float_values(group_rows, "qroot_ops_over_rho")
        bundle_ops = float_values(group_rows, "bundle_conservative_ops_over_rho")
        out.append(
            {
                "best_bundle_policy": sorted({str(row.get("best_bundle_policy")) for row in group_rows})[0],
                "bundle_conservative_ops_over_rho": min(bundle_ops) if bundle_ops else None,
                "candidate_leaf_sets": [
                    row.get("candidate_factor_leaf_indices") or []
                    for row in sorted(group_rows, key=lambda item: str(item.get("row_key")))
                ],
                "direct_ops_over_rho": min(direct_ops) if direct_ops else None,
                "direct_rank_max": max(int_value(row.get("direct_rank")) for row in group_rows),
                "direct_relation_count_max": max(int_value(row.get("direct_relation_count")) for row in group_rows),
                "direct_variants": sorted({str(row.get("direct_variant")) for row in group_rows}),
                "qroot_ops_over_rho_min": min(qroot_ops) if qroot_ops else None,
                "rejected_row_count": len(group_rows),
                "rejected_rows": [
                    {
                        "candidate_factor_leaf_indices": row.get("candidate_factor_leaf_indices") or [],
                        "direct_ops_over_rho": row.get("direct_ops_over_rho"),
                        "direct_rank": row.get("direct_rank"),
                        "direct_relation_count": row.get("direct_relation_count"),
                        "direct_variant": row.get("direct_variant"),
                        "p845_surface_ffe_ops": row.get("p845_surface_ffe_ops"),
                        "qroot_ops_over_rho": row.get("qroot_ops_over_rho"),
                        "relation_discriminator_class": row.get("relation_discriminator_class"),
                        "row_key": row.get("row_key"),
                        "source": row.get("source"),
                        "window": row.get("window"),
                    }
                    for row in sorted(group_rows, key=lambda item: (str(item.get("source")), str(item.get("row_key"))))
                ],
                "source_case_ops_over_rho_min": min(float_values(group_rows, "source_case_ops_over_rho"))
                if float_values(group_rows, "source_case_ops_over_rho")
                else None,
                "source_case_row_keys": list(key[2]),
                "target": key[0],
                "transfer_index": key[1],
                "union_derived_secrets": sorted(
                    {int_value(row.get("union_derived_secret")) for row in group_rows if row.get("union_derived_secret") is not None}
                ),
                "windows": sorted({str(row.get("window")) for row in group_rows}),
            }
        )
    return out


def window_table(p861: dict[str, Any], p862: dict[str, Any], p863: dict[str, Any], p864: dict[str, Any]) -> list[dict[str, Any]]:
    p861_summary = p861.get("summary") or {}
    p862_summary = p862.get("summary") or {}
    rows = [
        {
            "claim_status": p862_summary.get("claim_status") or p862.get("claim_status"),
            "direct_below_rho_verified_count": p862_summary.get("direct_below_rho_verified_count"),
            "p231_below_rho_case_count": p861_summary.get("p231_below_rho_case_count"),
            "p231_verified_case_count": p861_summary.get("p231_verified_case_count"),
            "p845_rejected_false_positive_row_count": p861_summary.get("p845_rejected_false_positive_row_count"),
            "p845_rejected_preserving_row_count": p861_summary.get("p845_rejected_preserving_row_count"),
            "p845_rejected_row_count": p861_summary.get("p845_rejected_row_count"),
            "qroot_below_rho_row_count": p861_summary.get("qroot_below_rho_row_count"),
            "qroot_false_positive_row_count": p861_summary.get("qroot_false_positive_row_count"),
            "qroot_preserving_row_count": p861_summary.get("qroot_preserving_row_count"),
            "qroot_surface_count": p861_summary.get("qroot_surface_count"),
            "replay_positive": int_value(p862_summary.get("direct_below_rho_verified_count")) > 0
            and int_value(p862_summary.get("best_bundle_conservative_below_rho_group_count")) > 0,
            "window": "1160_1167",
        }
    ]
    p863_summary = p863.get("summary") or {}
    rows.append(
        {
            "claim_status": p863_summary.get("claim_status"),
            "direct_below_rho_verified_count": p863_summary.get("direct_below_rho_verified_count"),
            "p231_below_rho_case_count": p863_summary.get("p231_below_rho_case_count"),
            "p231_verified_case_count": p863_summary.get("p231_verified_case_count"),
            "p845_rejected_false_positive_row_count": p863_summary.get("p845_rejected_false_positive_row_count"),
            "p845_rejected_preserving_row_count": p863_summary.get("p845_rejected_preserving_row_count"),
            "p845_rejected_row_count": p863_summary.get("p845_rejected_row_count"),
            "qroot_below_rho_row_count": p863_summary.get("qroot_below_rho_row_count"),
            "qroot_false_positive_row_count": p863_summary.get("qroot_false_positive_row_count"),
            "qroot_preserving_row_count": p863_summary.get("qroot_preserving_row_count"),
            "qroot_surface_count": p863_summary.get("qroot_surface_count"),
            "replay_positive": False,
            "window": "1168_1175",
        }
    )
    for summary in p864.get("window_summaries") or []:
        rows.append(
            {
                "claim_status": summary.get("claim_status"),
                "direct_below_rho_verified_count": summary.get("direct_below_rho_verified_count"),
                "p231_below_rho_case_count": summary.get("p231_below_rho_case_count"),
                "p231_verified_case_count": summary.get("p231_verified_case_count"),
                "p845_rejected_false_positive_row_count": summary.get("p845_rejected_false_positive_row_count"),
                "p845_rejected_preserving_row_count": summary.get("p845_rejected_preserving_row_count"),
                "p845_rejected_row_count": summary.get("p845_rejected_row_count"),
                "qroot_below_rho_row_count": summary.get("qroot_below_rho_row_count"),
                "qroot_false_positive_row_count": summary.get("qroot_false_positive_row_count"),
                "qroot_preserving_row_count": summary.get("qroot_preserving_row_count"),
                "qroot_surface_count": summary.get("qroot_surface_count"),
                "replay_positive": int_value(summary.get("direct_below_rho_verified_count")) > 0
                and int_value(summary.get("best_bundle_conservative_below_rho_group_count")) > 0,
                "window": summary.get("window"),
            }
        )
    return rows


def determine_claim(groups: list[dict[str, Any]], windows: list[dict[str, Any]]) -> str:
    if len(groups) >= 3 and all(
        row.get("direct_ops_over_rho") is not None
        and float(row["direct_ops_over_rho"]) < 1.0
        and row.get("bundle_conservative_ops_over_rho") is not None
        and float(row["bundle_conservative_ops_over_rho"]) < 1.0
        and int_value(row.get("direct_rank_max")) >= 2
        for row in groups
    ):
        return "P865_P231_MULTI_WINDOW_REJECTED_RELATION_SUPPLY_SURVIVES_DEDUP"
    if sum(1 for row in windows if row.get("replay_positive")) >= 2:
        return "P865_P231_MULTI_WINDOW_REPLAY_POSITIVE_BUT_DEDUP_WEAK"
    if any(int_value(row.get("p845_rejected_row_count")) > 0 for row in windows):
        return "NEGATIVE_RESULT_P865_REJECTED_ROWS_FAIL_MULTI_WINDOW_ACCOUNTING"
    return "NEGATIVE_RESULT_P865_P231_REJECTED_SUPPLY_NOT_FOUND"


def aggregate_summary(groups: list[dict[str, Any]], windows: list[dict[str, Any]], claim: str) -> dict[str, Any]:
    direct_ops = float_values(groups, "direct_ops_over_rho")
    bundle_ops = float_values(groups, "bundle_conservative_ops_over_rho")
    return {
        "claim_status": claim,
        "deduped_group_local_rank_sum": sum(int_value(row.get("direct_rank_max")) for row in groups),
        "deduped_group_local_relation_count_sum": sum(int_value(row.get("direct_relation_count_max")) for row in groups),
        "direct_below_rho_group_count": sum(1 for row in groups if row.get("direct_ops_over_rho") is not None and float(row["direct_ops_over_rho"]) < 1.0),
        "max_bundle_conservative_ops_over_rho": max(bundle_ops) if bundle_ops else None,
        "max_direct_ops_over_rho": max(direct_ops) if direct_ops else None,
        "min_bundle_conservative_ops_over_rho": min(bundle_ops) if bundle_ops else None,
        "min_direct_ops_over_rho": min(direct_ops) if direct_ops else None,
        "p231_below_rho_case_count": sum(int_value(row.get("p231_below_rho_case_count")) for row in windows),
        "p231_verified_case_count": sum(int_value(row.get("p231_verified_case_count")) for row in windows),
        "p845_rejected_false_positive_row_count": sum(int_value(row.get("p845_rejected_false_positive_row_count")) for row in windows),
        "p845_rejected_preserving_row_count": sum(int_value(row.get("p845_rejected_preserving_row_count")) for row in windows),
        "p845_rejected_row_count": sum(int_value(row.get("p845_rejected_row_count")) for row in windows),
        "positive_replay_window_count": sum(1 for row in windows if row.get("replay_positive")),
        "qroot_below_rho_row_count": sum(int_value(row.get("qroot_below_rho_row_count")) for row in windows),
        "qroot_false_positive_row_count": sum(int_value(row.get("qroot_false_positive_row_count")) for row in windows),
        "qroot_preserving_row_count": sum(int_value(row.get("qroot_preserving_row_count")) for row in windows),
        "qroot_surface_count": sum(int_value(row.get("qroot_surface_count")) for row in windows),
        "rejected_rows_per_p231_window": round(
            sum(int_value(row.get("p845_rejected_row_count")) for row in windows) / max(1, len(windows)),
            8,
        ),
        "rejected_rows_per_qroot_surface": round(
            sum(int_value(row.get("p845_rejected_row_count")) for row in windows)
            / max(1, sum(int_value(row.get("qroot_surface_count")) for row in windows)),
            8,
        ),
        "tested_p231_window_count": len(windows),
        "unique_source_case_group_count": len(groups),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p861 = load_json(args.p861)
    p862 = load_json(args.p862)
    p863 = load_json(args.p863)
    p864 = load_json(args.p864)
    replay_rows = p862_rows(p862) + p864_rows(p864)
    groups = dedup_groups(replay_rows)
    windows = window_table(p861, p862, p863, p864)
    claim = determine_claim(groups, windows)
    summary = aggregate_summary(groups, windows, claim)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p861_source": str(args.p861),
            "p862_source": str(args.p862),
            "p863_source": str(args.p863),
            "p864_source": str(args.p864),
            "script": str(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P865_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "deduped_source_case_groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "ACCOUNTING BOUNDARY: ranks are group-local direct-union ranks from saved replay artifacts, not a full cross-window sparse matrix rank.",
            "TARGET-DESCENT BOUNDARY: this does not solve individual logarithm descent for arbitrary targets.",
            "PUBLIC-SELECTION BOUNDARY: only qroot rows passing the frozen P845 rejection gate count as replay supply.",
            "POLLARD-RHO BOUNDARY: this is repeated relation-lane evidence for an index-calculus route, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p865_p231_multi_window_accounting",
        "red_team_handoff": {
            "assumptions": [
                "Distinct transfer indices and source-case row-key sets are treated as distinct local relation-use groups.",
                "Group-local direct-union ranks can be summed only as a conservative accounting signal, not as global matrix rank.",
                "The P845 threshold remains fixed at surface_ffe_ops > 64 across all p231 windows.",
            ],
            "evidence_so_far": [
                f"Positive replay windows: {summary.get('positive_replay_window_count')}/{summary.get('tested_p231_window_count')}.",
                f"Unique source-case groups after dedup: {summary.get('unique_source_case_group_count')}.",
                f"Deduped group-local rank sum: {summary.get('deduped_group_local_rank_sum')}; relation-count sum: {summary.get('deduped_group_local_relation_count_sum')}.",
                f"Rejected-row supply rate: {summary.get('rejected_rows_per_p231_window')} per p231 window and {summary.get('rejected_rows_per_qroot_surface')} per qroot surface.",
            ],
            "failure_modes": [
                "Frozen-prefix adjacency may inflate the apparent supply rate.",
                "Global sparse matrix rank may collapse when actual forms are reconstructed across windows.",
                "The relation supply is still only a source-lane mechanism; target descent and individual logarithms are untested.",
            ],
            "next_concrete_action": (
                "Build P866 to reconstruct full relation forms for the three deduped p231 source-case groups, compute actual sparse matrix rank over the relevant moduli, and test a first target-descent join instead of relying on compact saved ranks."
            ),
            "status": "OBSERVATION" if claim.startswith("P865_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "summary": summary,
        "window_accounting": windows,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p861", type=Path, default=DEFAULT_P861)
    parser.add_argument("--p862", type=Path, default=DEFAULT_P862)
    parser.add_argument("--p863", type=Path, default=DEFAULT_P863)
    parser.add_argument("--p864", type=Path, default=DEFAULT_P864)
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
