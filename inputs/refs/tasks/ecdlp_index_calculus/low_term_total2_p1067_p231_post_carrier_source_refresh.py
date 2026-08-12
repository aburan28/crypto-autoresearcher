#!/usr/bin/env python3
"""P1067 post-carrier source refresh beyond the P1054 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1064_p231_chronology_safe_high_mean_ops as p1064
import low_term_total2_p1065_p231_relaxed_high_mean_early_stop as p1065
import low_term_total2_p1066_p231_post_carrier_early_stop_holdout as p1066


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1067_p231_post_carrier_source_refresh.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1063 = STATE_DIR / "low_term_total2_p1063_p231_free_column_source_construction_probe.json"
DEFAULT_P1064 = STATE_DIR / "low_term_total2_p1064_p231_chronology_safe_high_mean_ops_probe.json"
DEFAULT_P1065 = STATE_DIR / "low_term_total2_p1065_p231_relaxed_high_mean_early_stop_probe.json"
DEFAULT_P1066 = STATE_DIR / "low_term_total2_p1066_p231_post_carrier_early_stop_holdout_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1067_p231_post_carrier_source_refresh.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted({path for path in paths if path.exists()}):
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_all_joined_rows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[Path]]:
    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    selected_paths = sorted(args.state_dir.glob(args.selected_glob))
    factor_windows = p1055.load_factor_windows(
        factor_paths,
        str(args.order),
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    source_windows = p1055.load_source_case_windows(
        selected_paths,
        args.target,
        args.selector,
        args.top_k,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    return p1055.join_windows(factor_windows, source_windows, args.column), factor_paths + selected_paths


def compact_cases(cases: list[dict[str, Any]], max_cases: int = 20) -> list[dict[str, Any]]:
    return cases[:max_cases]


def first_policy_with_column(policy_results: list[dict[str, Any]], target_column: int) -> dict[str, Any] | None:
    candidates = []
    for result in policy_results:
        first = result.get("first_column_removal_prefix")
        if not first or target_column not in (first.get("removed_free_columns") or []):
            continue
        candidates.append(result)
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            item["first_column_removal_prefix"]["marginal_charge_over_rho"],
            item["first_column_removal_prefix"]["length"],
            item["policy"],
        )
    )
    return candidates[0]


def unique_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_window: dict[str, dict[str, Any]] = {}
    for row in rows:
        by_window.setdefault(str(row["window"]), row)
    return [by_window[key] for key in sorted(by_window, key=lambda item: by_window[item]["window_start"])]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1063", type=Path, default=DEFAULT_P1063)
    parser.add_argument("--p1064", type=Path, default=DEFAULT_P1064)
    parser.add_argument("--p1065", type=Path, default=DEFAULT_P1065)
    parser.add_argument("--p1066", type=Path, default=DEFAULT_P1066)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--target-column", type=int, default=10)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    parser.add_argument("--anchor-window", default="18464_18471")
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    p1065_payload = load_json(args.p1065)
    p1066_payload = load_json(args.p1066)
    holdout_after = p1066.carrier_window_end(p1065_payload)
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)

    all_rows, all_input_paths = load_all_joined_rows(args)
    p1054_payload = p1055.load_json(args.p1054)
    p1054_expression = (
        ((p1054_payload.get("selected_rule") or {}).get("expression"))
        or ((p1054_payload.get("summary") or {}).get("selected_rule_expression"))
    )
    if not p1054_expression:
        raise ValueError("P1054 artifact has no selected rule expression")
    p1054_rule = p1055.compile_rule(str(p1054_expression))

    p1054_rows = [row for row in all_rows if p1054_rule(row)]
    forward_p1054_rows = [row for row in p1054_rows if row["split"] == "forward_validation"]
    discovery_end = p1064.discovery_end_from_p1063(args.p1063, args.anchor_window)
    validation_p1054_rows = [row for row in forward_p1054_rows if row["window_start"] > discovery_end]
    anchor_rows = [row for row in validation_p1054_rows if row["window"] == args.anchor_window]
    if not anchor_rows:
        raise ValueError(f"anchor window {args.anchor_window} is not in the validation split")

    refreshed_rows = [
        row
        for row in all_rows
        if row["split"] == "forward_validation" and row["window_start"] > holdout_after and row["case_count"] > 0
    ]
    p1054_holdout_rows = [row for row in refreshed_rows if p1054_rule(row)]
    non_p1054_rows = [row for row in refreshed_rows if not p1054_rule(row)]

    row_pool: dict[int, dict[str, Any]] = {}
    for row in validation_p1054_rows + refreshed_rows:
        row_pool[id(row)] = row
    evaluation_rows = unique_rows(validation_p1054_rows + refreshed_rows)
    cache: dict[Path, list[dict[str, Any]]] = {}
    bundles = p1063.prepare_bundles(list(row_pool.values()), cache, args)
    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    anchor_selector = p1063.exact_anchor_forward(exact_selector, args.anchor_window)
    anchor = p1063.evaluate_fast(anchor_rows, exact_selector, bundles, args)

    candidate_refs = []
    for row in refreshed_rows:
        for case in row.get("source_cases") or []:
            ref = p1065.case_ref(row, case, len(candidate_refs))
            ref["p1054_selected"] = bool(p1054_rule(row))
            candidate_refs.append(ref)

    single_audits = p1065.single_case_audits(
        evaluation_rows,
        anchor,
        anchor_selector,
        candidate_refs,
        bundles,
        args,
        priority_columns,
    )
    for audit, ref in zip(single_audits, candidate_refs):
        audit["p1054_selected"] = ref["p1054_selected"]

    policy_results = p1066.public_policy_results(
        single_audits,
        evaluation_rows,
        anchor,
        anchor_selector,
        bundles,
        args,
        priority_columns,
    )
    best_policy = first_policy_with_column(policy_results, args.target_column)
    rank_bearing_cases = [case for case in single_audits if p1055.int_value(case.get("single_marginal_rank_gain")) > 0]
    non_p1054_rank_cases = [case for case in rank_bearing_cases if not case.get("p1054_selected")]
    p1054_rank_cases = [case for case in rank_bearing_cases if case.get("p1054_selected")]
    below_rho_non_p1054_cases = [
        case
        for case in non_p1054_rank_cases
        if (p1055.float_value(case.get("single_marginal_charge_over_rho")) or float("inf")) < 1.0
        and args.target_column in (case.get("single_removed_free_columns") or [])
    ]
    public_below_rho = bool(
        best_policy
        and best_policy.get("first_column_removal_prefix")
        and best_policy["first_column_removal_prefix"]["marginal_charge_over_rho"] < 1.0
    )

    if below_rho_non_p1054_cases and public_below_rho:
        claim_status = "POSITIVE_SIGNAL_P1067_SOURCE_REFRESH_NON_P1054_BELOW_RHO_COLUMN10"
    elif below_rho_non_p1054_cases:
        claim_status = "OBSERVATION_P1067_NON_P1054_SINGLE_CASE_BELOW_RHO_NOT_PUBLIC_PREFIX"
    elif rank_bearing_cases:
        claim_status = "OBSERVATION_P1067_SOURCE_REFRESH_RANK_GAIN_ABOVE_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1067_SOURCE_REFRESH_NO_RANK_GAIN"

    best_single = None
    if rank_bearing_cases:
        rank_bearing_cases.sort(
            key=lambda case: (
                case["single_marginal_charge_over_rho"],
                case.get("p1054_selected", False),
                case["case_id"],
            )
        )
        best_single = rank_bearing_cases[0]

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in all_input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(all_input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1063": sha256_file(args.p1063) if args.p1063.exists() else None,
            "p1064": sha256_file(args.p1064) if args.p1064.exists() else None,
            "p1065": sha256_file(args.p1065) if args.p1065.exists() else None,
            "p1066": sha256_file(args.p1066) if args.p1066.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1059": str(args.p1059),
            "p1063": str(args.p1063),
            "p1064": str(args.p1064),
            "p1065": str(args.p1065),
            "p1066": str(args.p1066),
            "script": str(Path(__file__)),
        },
        "candidate_cases": compact_cases(single_audits),
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "SOURCE-REFRESH",
            "P1054-GATE-BOUNDARY",
            "FREE-COLUMN-PRESSURE",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "anchor": p1065.compact_result(anchor),
            "p1066_claim_status": p1066_payload.get("claim_status"),
            "p1066_record_counts": p1066_payload.get("record_counts"),
            "policy_results": policy_results,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "same_target_source_refresh_not_fresh_target": True,
            "target_descent_not_implemented": True,
        },
        "parameters": {
            "anchor_window": args.anchor_window,
            "column": args.column,
            "discovery_end": discovery_end,
            "holdout_after_window_end": holdout_after,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "priority_columns": priority_columns,
            "selected_rowkey_control": list(selected_rowkey),
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "target_column": args.target_column,
            "top_k": args.top_k,
        },
        "record_counts": {
            "candidate_case_count": len(single_audits),
            "forward_rows": len([row for row in all_rows if row["split"] == "forward_validation"]),
            "non_p1054_rank_bearing_single_case_count": len(non_p1054_rank_cases),
            "non_p1054_refreshed_windows": len(non_p1054_rows),
            "p1054_holdout_windows": len(p1054_holdout_rows),
            "p1054_rank_bearing_single_case_count": len(p1054_rank_cases),
            "refreshed_windows": len(refreshed_rows),
            "rank_bearing_single_case_count": len(rank_bearing_cases),
        },
        "rank_bearing_cases": rank_bearing_cases,
        "schema": SCHEMA,
        "strict_success": public_below_rho and bool(below_rho_non_p1054_cases),
        "summary": {
            "best_public_first_charge": (
                best_policy["first_column_removal_prefix"]["marginal_charge_over_rho"] if best_policy else None
            ),
            "best_public_first_length": (
                best_policy["first_column_removal_prefix"]["length"] if best_policy else None
            ),
            "best_public_policy": best_policy["policy"] if best_policy else None,
            "best_single_rank_case": best_single,
            "claim_status": claim_status,
            "non_p1054_below_rho_column_cases": len(below_rho_non_p1054_cases),
            "p1054_holdout_windows": [row["window"] for row in p1054_holdout_rows],
            "public_below_rho": public_below_rho,
            "refreshed_window_range": [
                refreshed_rows[0]["window"] if refreshed_rows else None,
                refreshed_rows[-1]["window"] if refreshed_rows else None,
            ],
            "rank_bearing_single_case_count": len(rank_bearing_cases),
            "strict_success": public_below_rho and bool(below_rho_non_p1054_cases),
            "target_column": args.target_column,
            "weak_positive": bool(rank_bearing_cases),
        },
        "timestamp_utc": now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} refreshed_windows={windows} cases={cases} rank_cases={rank_cases} "
        "non_p1054_rank_cases={non_p1054} best_policy={policy} best_charge={charge} out={out}".format(
            claim=claim_status,
            windows=len(refreshed_rows),
            cases=len(single_audits),
            rank_cases=len(rank_bearing_cases),
            non_p1054=len(non_p1054_rank_cases),
            policy=payload["summary"]["best_public_policy"],
            charge=payload["summary"]["best_public_first_charge"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
