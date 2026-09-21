#!/usr/bin/env python3
"""P1068 public gate-repair holdout for the P1067 source refresh."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059
import low_term_total2_p1063_p231_free_column_source_construction as p1063
import low_term_total2_p1064_p231_chronology_safe_high_mean_ops as p1064
import low_term_total2_p1065_p231_relaxed_high_mean_early_stop as p1065
import low_term_total2_p1066_p231_post_carrier_early_stop_holdout as p1066
import low_term_total2_p1067_p231_post_carrier_source_refresh as p1067


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1068_p231_gate_repair_holdout.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1063 = STATE_DIR / "low_term_total2_p1063_p231_free_column_source_construction_probe.json"
DEFAULT_P1065 = STATE_DIR / "low_term_total2_p1065_p231_relaxed_high_mean_early_stop_probe.json"
DEFAULT_P1067 = STATE_DIR / "low_term_total2_p1067_p231_post_carrier_source_refresh_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1068_p231_gate_repair_holdout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1068_p231_gate_repair_holdout.v1"

RuleFn = Callable[[dict[str, Any]], bool]


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


def rule_specs(train_case: dict[str, Any]) -> list[dict[str, Any]]:
    rowkeys = tuple(train_case["row_keys"])
    salt_min = train_case["salt_min"]
    salt_max = train_case["salt_max"]
    salt_sum = train_case["salt_sum"]
    return [
        {
            "expression": "exact_rowkeys",
            "fn": lambda ref, rowkeys=rowkeys: tuple(ref["row_keys"]) == rowkeys,
            "public_rule": True,
        },
        {
            "expression": "p1054_excluded AND exact_rowkeys",
            "fn": lambda ref, rowkeys=rowkeys: (not ref.get("p1054_selected")) and tuple(ref["row_keys"]) == rowkeys,
            "public_rule": True,
        },
        {
            "expression": f"p1054_excluded AND salt_min == {salt_min} AND salt_max == {salt_max}",
            "fn": lambda ref, salt_min=salt_min, salt_max=salt_max: (
                (not ref.get("p1054_selected")) and ref.get("salt_min") == salt_min and ref.get("salt_max") == salt_max
            ),
            "public_rule": True,
        },
        {
            "expression": f"p1054_excluded AND salt_sum == {salt_sum}",
            "fn": lambda ref, salt_sum=salt_sum: (not ref.get("p1054_selected")) and ref.get("salt_sum") == salt_sum,
            "public_rule": True,
        },
        {
            "expression": "p1054_excluded",
            "fn": lambda ref: not ref.get("p1054_selected"),
            "public_rule": True,
        },
    ]


def evaluate_rule(
    spec: dict[str, Any],
    validation_refs: list[dict[str, Any]],
    evaluation_rows: list[dict[str, Any]],
    anchor: dict[str, Any],
    anchor_selector: p1063.CaseSelector,
    bundles: dict[int, dict[str, Any]],
    args: argparse.Namespace,
    priority_columns: list[int],
) -> dict[str, Any]:
    selected = [ref for ref in validation_refs if spec["fn"](ref)]
    selected.sort(key=lambda ref: (ref["window_start"], ref["transfer_index"], ref["case_id"]))
    first_rank = None
    first_column = None
    checkpoints: list[dict[str, Any]] = []
    for length in range(1, len(selected) + 1):
        prefix = selected[:length]
        result = p1065.evaluate_with_cases(evaluation_rows, anchor_selector, prefix, bundles, args)
        stats = p1063.marginal_stats(anchor, result, priority_columns)
        checkpoint = {
            "last_case_id": prefix[-1]["case_id"],
            "length": length,
            "marginal_charge_over_rho": stats["marginal_charge_over_rho"],
            "marginal_rank_gain": stats["marginal_rank_gain"],
            "removed_free_columns": stats["removed_free_columns"],
            "union_free_columns": stats["union_free_columns"],
        }
        if stats["marginal_rank_gain"] > 0 and first_rank is None:
            first_rank = checkpoint
        if args.target_column in stats["removed_free_columns"] and first_column is None:
            first_column = checkpoint
        if stats["marginal_rank_gain"] > 0 or args.target_column in stats["removed_free_columns"] or length in (1, len(selected)):
            checkpoints.append(checkpoint)
    final = p1065.evaluate_with_cases(evaluation_rows, anchor_selector, selected, bundles, args)
    final_stats = p1063.marginal_stats(anchor, final, priority_columns)
    return {
        "checkpoints": checkpoints,
        "expression": spec["expression"],
        "final_stats": final_stats,
        "first_column_removal_prefix": first_column,
        "first_rank_gain_prefix": first_rank,
        "ordered_case_ids": [ref["case_id"] for ref in selected],
        "public_rule": bool(spec["public_rule"]),
        "selected_case_count": len(selected),
    }


def best_success(rule_results: list[dict[str, Any]], target_column: int) -> dict[str, Any] | None:
    candidates = []
    for result in rule_results:
        first = result.get("first_column_removal_prefix")
        if not first or target_column not in (first.get("removed_free_columns") or []):
            continue
        if first["marginal_charge_over_rho"] >= 1.0:
            continue
        candidates.append(result)
    if not candidates:
        return None
    candidates.sort(
        key=lambda item: (
            item["first_column_removal_prefix"]["marginal_charge_over_rho"],
            item["first_column_removal_prefix"]["length"],
            item["expression"],
        )
    )
    return candidates[0]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1063", type=Path, default=DEFAULT_P1063)
    parser.add_argument("--p1065", type=Path, default=DEFAULT_P1065)
    parser.add_argument("--p1067", type=Path, default=DEFAULT_P1067)
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
    p1067_payload = load_json(args.p1067)
    train_case = (p1067_payload.get("summary") or {}).get("best_single_rank_case")
    if not train_case:
        raise ValueError("P1067 artifact has no best_single_rank_case")
    train_window_end = int(str(train_case["window"]).split("_", 1)[1])
    holdout_after = p1066.carrier_window_end(p1065_payload)
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)

    all_rows, all_input_paths = p1067.load_all_joined_rows(args)
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
    train_rows = [row for row in refreshed_rows if row["window"] == train_case["window"]]
    validation_rows = [row for row in refreshed_rows if row["window_start"] > train_window_end]
    evaluation_rows = p1067.unique_rows(validation_p1054_rows + refreshed_rows)

    cache: dict[Path, list[dict[str, Any]]] = {}
    bundles = p1063.prepare_bundles(evaluation_rows, cache, args)
    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    anchor_selector = p1063.exact_anchor_forward(exact_selector, args.anchor_window)
    anchor = p1063.evaluate_fast(anchor_rows, exact_selector, bundles, args)

    validation_refs = []
    for row in validation_rows:
        for case in row.get("source_cases") or []:
            ref = p1065.case_ref(row, case, len(validation_refs))
            ref["p1054_selected"] = bool(p1054_rule(row))
            validation_refs.append(ref)
    single_audits = p1065.single_case_audits(
        evaluation_rows,
        anchor,
        anchor_selector,
        validation_refs,
        bundles,
        args,
        priority_columns,
    )
    for audit, ref in zip(single_audits, validation_refs):
        audit["p1054_selected"] = ref["p1054_selected"]

    rules = rule_specs(train_case)
    rule_results = [
        evaluate_rule(rule, single_audits, evaluation_rows, anchor, anchor_selector, bundles, args, priority_columns)
        for rule in rules
    ]
    success = best_success(rule_results, args.target_column)
    exact_rowkey = next(result for result in rule_results if result["expression"] == "exact_rowkeys")
    p1054_excluded_exact = next(result for result in rule_results if result["expression"] == "p1054_excluded AND exact_rowkeys")

    if success:
        claim_status = "POSITIVE_SIGNAL_P1068_GATE_REPAIR_HOLDOUT_BELOW_RHO"
    elif any(result.get("first_column_removal_prefix") for result in rule_results):
        claim_status = "OBSERVATION_P1068_GATE_REPAIR_HOLDOUT_ABOVE_RHO"
    else:
        claim_status = "NEGATIVE_RESULT_P1068_GATE_REPAIR_NO_HOLDOUT_COLUMN10"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in all_input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(all_input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1063": sha256_file(args.p1063) if args.p1063.exists() else None,
            "p1065": sha256_file(args.p1065) if args.p1065.exists() else None,
            "p1067": sha256_file(args.p1067) if args.p1067.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1059": str(args.p1059),
            "p1063": str(args.p1063),
            "p1065": str(args.p1065),
            "p1067": str(args.p1067),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "SAME-TARGET-HOLDOUT",
            "PUBLIC-GATE-REPAIR",
            "P1054-GATE-BOUNDARY",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "anchor": p1065.compact_result(anchor),
            "exact_rowkeys": exact_rowkey,
            "p1054_excluded_exact_rowkeys": p1054_excluded_exact,
            "rule_results": rule_results,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "same_target_holdout_not_fresh_target": True,
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
            "train_case": train_case,
            "train_window_end": train_window_end,
        },
        "record_counts": {
            "refreshed_windows": len(refreshed_rows),
            "train_windows": len(train_rows),
            "validation_case_count": len(validation_refs),
            "validation_rank_bearing_single_case_count": sum(
                1 for case in single_audits if p1055.int_value(case.get("single_marginal_rank_gain")) > 0
            ),
            "validation_windows": len(validation_rows),
        },
        "schema": SCHEMA,
        "strict_success": bool(success),
        "summary": {
            "best_success_expression": success["expression"] if success else None,
            "best_success_first_charge": (
                success["first_column_removal_prefix"]["marginal_charge_over_rho"] if success else None
            ),
            "best_success_first_length": success["first_column_removal_prefix"]["length"] if success else None,
            "claim_status": claim_status,
            "exact_rowkeys_first_charge": (
                exact_rowkey["first_column_removal_prefix"]["marginal_charge_over_rho"]
                if exact_rowkey.get("first_column_removal_prefix")
                else None
            ),
            "p1054_excluded_exact_first_charge": (
                p1054_excluded_exact["first_column_removal_prefix"]["marginal_charge_over_rho"]
                if p1054_excluded_exact.get("first_column_removal_prefix")
                else None
            ),
            "strict_success": bool(success),
            "target_column": args.target_column,
            "train_case_id": train_case["case_id"],
            "validation_windows": [row["window"] for row in validation_rows],
            "weak_positive": any(result.get("first_column_removal_prefix") for result in rule_results),
        },
        "timestamp_utc": now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} success={success} best_expr={expr} best_charge={charge} "
        "exact_charge={exact} excluded_exact_charge={excluded} out={out}".format(
            claim=claim_status,
            success=bool(success),
            expr=payload["summary"]["best_success_expression"],
            charge=payload["summary"]["best_success_first_charge"],
            exact=payload["summary"]["exact_rowkeys_first_charge"],
            excluded=payload["summary"]["p1054_excluded_exact_first_charge"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
