#!/usr/bin/env python3
"""P1077 holdout validation for the frozen P1076 diagnostic filters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1069_p231_forward_transfer_descent_accounting as p1069
import low_term_total2_p1071_p231_remaining_column_source_expansion as p1071
import low_term_total2_p1072_p231_topk7_split_validation as p1072
import low_term_total2_p1073_p231_topk7_order_compression as p1073
import low_term_total2_p1074_p231_disjoint_source_packet_validation as p1074
import low_term_total2_p1075_p231_public_window_router as p1075
import low_term_total2_p1076_p231_blocker_prefilter_audit as p1076


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1077_p231_frozen_filter_holdout.md"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_P1069 = STATE_DIR / "low_term_total2_p1069_p231_forward_transfer_descent_accounting_probe.json"
DEFAULT_P1072 = STATE_DIR / "low_term_total2_p1072_p231_topk7_split_validation_probe.json"
DEFAULT_P1075 = STATE_DIR / "low_term_total2_p1075_p231_public_window_router_probe.json"
DEFAULT_P1076 = STATE_DIR / "low_term_total2_p1076_p231_blocker_prefilter_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1077_p231_frozen_filter_holdout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1077_p231_frozen_filter_holdout.v1"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_prefix(prefix: dict[str, Any] | None) -> dict[str, Any] | None:
    if not prefix:
        return None
    return {
        "last_case_id": prefix.get("last_case_id"),
        "length": prefix.get("length"),
        "marginal_charge_over_rho": prefix.get("marginal_charge_over_rho"),
        "marginal_rank_gain": prefix.get("marginal_rank_gain"),
        "removed_free_columns": prefix.get("removed_free_columns") or [],
        "union_free_columns": prefix.get("union_free_columns") or [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
    parser.add_argument("--p1069", type=Path, default=DEFAULT_P1069)
    parser.add_argument("--p1072", type=Path, default=DEFAULT_P1072)
    parser.add_argument("--p1075", type=Path, default=DEFAULT_P1075)
    parser.add_argument("--p1076", type=Path, default=DEFAULT_P1076)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target-column", type=int, default=15)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=7)
    parser.add_argument("--promoted-selector", default="mode_low_term_support_total5")
    parser.add_argument("--promoted-top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1075_payload = load_json(args.p1075)
    p1076_payload = load_json(args.p1076)
    stage1_refs, validation_refs, stage1_packet, factor_rows, cache, inventory, factor_paths, selected_paths = p1073.build_context(args)
    carrier_window = (p1076_payload.get("feature_comparison") or {}).get("carrier", {}).get("window")
    winner_window = (p1075_payload.get("parameters") or {}).get("excluded_winner_window")
    excluded_windows = sorted({item for item in [carrier_window, winner_window] if item})
    heldout_refs = [ref for ref in validation_refs if ref["window"] not in set(excluded_windows)]
    window_policy = next(item for item in p1075.window_key_catalog() if item["name"] == "window_max_direct_ops_asc")
    case_policy = next(item for item in p1075.case_order_catalog() if item["name"] == "chronological")
    ordered = p1075.ordered_by_window_policy(heldout_refs, factor_rows, window_policy, case_policy)

    filter_results = []
    winners = []
    for item in p1076.diagnostic_filters():
        filtered = [ref for ref in ordered if item["rule"](ref)]
        result = p1072.prefix_scan(
            filtered,
            stage1_refs,
            stage1_packet,
            factor_rows,
            cache,
            args,
            priority_columns,
            args.target_column,
        )
        first_rank = compact_prefix(result.get("first_rank_gain_prefix"))
        first_target = compact_prefix(result.get("first_target_column_prefix"))
        final_stats = result.get("final_stats") or {}
        below_rho = bool(
            first_rank
            and (p1055.float_value(first_rank.get("marginal_charge_over_rho")) or float("inf")) < 1.0
        ) or bool(
            first_target
            and (p1055.float_value(first_target.get("marginal_charge_over_rho")) or float("inf")) < 1.0
        )
        row = {
            "below_rho_success": below_rho,
            "filter": item["name"],
            "filtered_case_count": len(filtered),
            "first_rank_gain_prefix": first_rank,
            "first_target_column_prefix": first_target,
            "final_stats": final_stats,
            "top_filtered_refs": [p1076.feature_summary(ref) for ref in filtered[:5]],
        }
        filter_results.append(row)
        if below_rho:
            winners.append(row)

    strict_success = bool(winners)
    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1077_FROZEN_FILTER_HOLDOUT_BELOW_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1077_FROZEN_FILTERS_NO_HELDOUT_DIRECTION"
    payload = {
        "artifact_hashes": {
            "contract": p1069.sha256_file(args.contract) if args.contract.exists() else None,
            "factor_artifact_count": len(factor_paths),
            "factor_artifact_digest": p1069.digest_paths(factor_paths),
            "p1059": p1069.sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1067": p1069.sha256_file(args.p1067) if args.p1067.exists() else None,
            "p1069": p1069.sha256_file(args.p1069) if args.p1069.exists() else None,
            "p1072": p1069.sha256_file(args.p1072) if args.p1072.exists() else None,
            "p1075": p1069.sha256_file(args.p1075) if args.p1075.exists() else None,
            "p1076": p1069.sha256_file(args.p1076) if args.p1076.exists() else None,
            "script": p1069.sha256_file(Path(__file__)),
            "selected_artifact_count": len(selected_paths),
            "selected_artifact_digest": p1069.digest_paths(selected_paths),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1059": str(args.p1059),
            "p1067": str(args.p1067),
            "p1069": str(args.p1069),
            "p1072": str(args.p1072),
            "p1075": str(args.p1075),
            "p1076": str(args.p1076),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "FROZEN-FILTER-HOLDOUT",
            "NEGATIVE-VALIDATION",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "filter_results": filter_results,
            "p1076_summary": p1076_payload.get("summary"),
        },
        "expanded_source_inventory": inventory,
        "honesty_boundary": {
            "known_positive_windows_excluded": excluded_windows,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "target_descent_closed": False,
        },
        "parameters": {
            "excluded_windows": excluded_windows,
            "filter_source": "P1076 diagnostic filters frozen before holdout",
            "heldout_windows": sorted({ref["window"] for ref in heldout_refs}, key=lambda value: int(value.split("_")[0])),
            "order": args.order,
            "priority_columns": priority_columns,
            "target": args.target,
            "target_column": args.target_column,
        },
        "record_counts": {
            "filter_count": len(filter_results),
            "heldout_case_count": len(heldout_refs),
            "heldout_window_count": len({ref["window"] for ref in heldout_refs}),
            "winner_count": len(winners),
        },
        "schema": SCHEMA,
        "strict_success": strict_success,
        "summary": {
            "claim_status": claim_status,
            "excluded_windows": excluded_windows,
            "heldout_case_count": len(heldout_refs),
            "heldout_window_count": len({ref["window"] for ref in heldout_refs}),
            "strict_success": strict_success,
            "winner_count": len(winners),
        },
        "timestamp_utc": p1071.now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} success={success} filters={filters} winners={winners} "
        "heldout_cases={cases} out={out}".format(
            claim=claim_status,
            success=strict_success,
            filters=len(filter_results),
            winners=len(winners),
            cases=len(heldout_refs),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
