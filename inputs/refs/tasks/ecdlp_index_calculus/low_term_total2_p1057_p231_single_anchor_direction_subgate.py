#!/usr/bin/env python3
"""P1057 single-anchor direction subgate for the P1056 source-cost reducer."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1056_p231_public_source_cost_reducer as p1056


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1057_p231_single_anchor_direction_subgate.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1056 = STATE_DIR / "low_term_total2_p1056_p231_public_source_cost_reducer_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1057_p231_single_anchor_direction_subgate_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1057_p231_single_anchor_direction_subgate.v1"

DIRECTION_FEATURES = [
    "max_ops",
    "op_range",
    "mean_ops",
    "min_ops",
    "salt_span",
    "unique_salts",
    "transfer_span",
]
FEATURE_PRIORITY = {feature: idx for idx, feature in enumerate(DIRECTION_FEATURES)}


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


RuleFn = Callable[[dict[str, Any]], bool]


def format_threshold(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.8f}".rstrip("0").rstrip(".")
    return str(value)


def condition_rule(feature: str, op: str, threshold: Any) -> tuple[str, RuleFn]:
    expression = f"{feature} {op} {format_threshold(threshold)}"

    def rule(row: dict[str, Any]) -> bool:
        value = row.get(feature)
        if value is None:
            return False
        if op == ">=":
            return value >= threshold
        if op == "<=":
            return value <= threshold
        return value == threshold

    return expression, rule


def rule_catalog(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules = []
    seen = set()
    for feature in DIRECTION_FEATURES:
        values = sorted({row.get(feature) for row in train_rows if row.get(feature) is not None})
        for value in values:
            ops = [">=", "<="] if isinstance(value, float) else [">=", "<=", "=="]
            for op in ops:
                expression, fn = condition_rule(feature, op, value)
                if expression in seen:
                    continue
                seen.add(expression)
                rules.append(
                    {
                        "expression": expression,
                        "feature_priority": FEATURE_PRIORITY[feature],
                        "fn": fn,
                        "kind": "single",
                    }
                )
    return rules


def load_records(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str, str, list[Path]]:
    p1054_payload = p1055.load_json(args.p1054)
    p1054_expression = (
        ((p1054_payload.get("selected_rule") or {}).get("expression"))
        or ((p1054_payload.get("summary") or {}).get("selected_rule_expression"))
    )
    if not p1054_expression:
        raise ValueError("P1054 artifact has no selected rule expression")
    p1056_payload = p1055.load_json(args.p1056)
    p1056_expression = (
        ((p1056_payload.get("selected_rule") or {}).get("expression"))
        or ((p1056_payload.get("summary") or {}).get("selected_rule_expression"))
    )
    if not p1056_expression:
        raise ValueError("P1056 artifact has no selected rule expression")

    p1054_rule = p1055.compile_rule(str(p1054_expression))
    p1056_rule = p1055.compile_rule(str(p1056_expression))
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
    records = [
        row
        for row in p1055.join_windows(factor_windows, source_windows, args.column)
        if p1054_rule(row) and p1056_rule(row)
    ]
    return records, str(p1054_expression), str(p1056_expression), factor_paths + selected_paths


def evaluate(
    rows: list[dict[str, Any]],
    rule: RuleFn,
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    return p1056.evaluate_rows(
        rows,
        rule,
        cache,
        args.order,
        args.column,
        args.target,
        args.selector,
        args.top_k,
        args.source,
    )


def compact_result(result: dict[str, Any], max_windows: int = 20) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    return compact


def choose_rule(
    rules: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    full_train: dict[str, Any],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    baseline_cpg = full_train["charge_per_rank_gain"] or float("inf")
    candidates = []
    for rule in rules:
        result = evaluate(train_rows, rule["fn"], cache, args)
        cpg = result["charge_per_rank_gain"]
        if result["selected_window_count"] < args.min_train_windows:
            continue
        if result["source_rank_gain_over_base"] < args.min_train_rank_gain:
            continue
        if cpg is None or cpg >= baseline_cpg:
            continue
        candidates.append({"rule": rule, "train": result})
    candidates.sort(
        key=lambda item: (
            item["train"]["charge_per_rank_gain"],
            item["rule"]["feature_priority"],
            item["train"]["strict_source_charge_over_rho"],
            item["rule"]["expression"],
        )
    )
    public = [
        {
            "expression": item["rule"]["expression"],
            "feature_priority": item["rule"]["feature_priority"],
            "kind": item["rule"]["kind"],
            "train": compact_result(item["train"], max_windows=8),
        }
        for item in candidates[:20]
    ]
    return (candidates[0] if candidates else None), public


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1056", type=Path, default=DEFAULT_P1056)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    parser.add_argument("--min-train-windows", type=int, default=1)
    parser.add_argument("--min-train-rank-gain", type=int, default=2)
    args = parser.parse_args()

    records, p1054_expression, p1056_expression, input_paths = load_records(args)
    rows_by_split = {
        split: [row for row in records if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }
    cache: dict[Path, list[dict[str, Any]]] = {}
    true_rule = lambda row: True
    full_results = {
        split: evaluate(rows, true_rule, cache, args)
        for split, rows in rows_by_split.items()
    }
    rules = rule_catalog(rows_by_split["calibration"])
    selected, top_candidates = choose_rule(
        rules,
        rows_by_split["calibration"],
        full_results["calibration"],
        cache,
        args,
    )

    if selected is None:
        selected_results = None
        claim_status = "NEGATIVE_RESULT_P1057_NO_CALIBRATION_DIRECTION_SUBGATE"
    else:
        selected_results = {
            split: evaluate(rows, selected["rule"]["fn"], cache, args)
            for split, rows in rows_by_split.items()
        }
        forward = selected_results["forward_validation"]
        full_forward = full_results["forward_validation"]
        forward_cpg = forward["charge_per_rank_gain"]
        full_cpg = full_forward["charge_per_rank_gain"]
        if forward["source_rank_gain_over_base"] <= 0:
            claim_status = "NEGATIVE_RESULT_P1057_DIRECTION_SUBGATE_ZERO_FORWARD_RANK"
        elif forward_cpg is None or full_cpg is None or forward_cpg >= full_cpg:
            claim_status = "NEGATIVE_RESULT_P1057_DIRECTION_SUBGATE_NO_FORWARD_COST_GAIN"
        elif forward["strict_source_charge_over_rho"] <= 1.0:
            claim_status = "POSITIVE_SIGNAL_P1057_DIRECTION_TOTAL_RHO_CANDIDATE"
        elif forward_cpg <= 1.0:
            claim_status = "POSITIVE_SIGNAL_P1057_DIRECTION_CPG_BELOW_RHO_NOT_TOTAL_RHO"
        else:
            claim_status = "POSITIVE_SIGNAL_P1057_DIRECTION_COST_REDUCER_NOT_RHO_WIN"

    selected_summary = None
    if selected_results is not None:
        forward = selected_results["forward_validation"]
        full_forward = full_results["forward_validation"]
        selected_summary = {
            "charge_reduction_factor_vs_p1056": (
                round(full_forward["strict_source_charge_over_rho"] / forward["strict_source_charge_over_rho"], 8)
                if forward["strict_source_charge_over_rho"]
                else None
            ),
            "forward_charge_per_rank_gain": forward["charge_per_rank_gain"],
            "forward_p1056_charge_per_rank_gain": full_forward["charge_per_rank_gain"],
            "forward_rank_gain": forward["source_rank_gain_over_base"],
            "forward_selected_windows": forward["selected_window_count"],
            "forward_strict_source_charge_over_rho": forward["strict_source_charge_over_rho"],
            "rank_gain_retention_vs_p1056": (
                round(
                    forward["source_rank_gain_over_base"]
                    / full_forward["source_rank_gain_over_base"],
                    8,
                )
                if full_forward["source_rank_gain_over_base"]
                else None
            ),
        }

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1056": sha256_file(args.p1056) if args.p1056.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1056": str(args.p1056),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "LOW-SUPPORT",
            "HEURISTIC",
            "PUBLIC-DIRECTION-SUBGATE",
            "SOURCE-COST-REDUCTION",
            "TARGET-ELIMINATED-FACTOR-RANK",
            "INDEX-CALCULUS-PRECURSOR",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "full_p1056_results": {split: compact_result(result) for split, result in full_results.items()},
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "direct_shared_verification_labels_excluded_from_subgate": True,
            "low_support_single_calibration_anchor": args.min_train_windows == 1,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_faster_than_rho_claim": claim_status != "POSITIVE_SIGNAL_P1057_DIRECTION_TOTAL_RHO_CANDIDATE",
            "rank_measured_from_target_eliminated_certificate_rows": True,
            "subgate_selected_on_calibration_only": selected is not None,
        },
        "parameters": {
            "column": args.column,
            "direction_features": DIRECTION_FEATURES,
            "min_train_rank_gain": args.min_train_rank_gain,
            "min_train_windows": args.min_train_windows,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "p1056_rule": p1056_expression,
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {split: len(rows) for split, rows in rows_by_split.items()},
        "schema": SCHEMA,
        "selected_rule": None
        if selected is None
        else {
            "expression": selected["rule"]["expression"],
            "feature_priority": selected["rule"]["feature_priority"],
            "kind": selected["rule"]["kind"],
        },
        "selected_rule_results": None
        if selected_results is None
        else {split: compact_result(result) for split, result in selected_results.items()},
        "summary": {
            "claim_status": claim_status,
            "p1054_rule": p1054_expression,
            "p1056_rule": p1056_expression,
            "selected_rule_expression": None if selected is None else selected["rule"]["expression"],
            "selected_summary": selected_summary,
            "strict_success": claim_status.startswith("POSITIVE_SIGNAL"),
            "top_candidate_count": len(top_candidates),
        },
        "timestamp": now_iso(),
        "top_calibration_candidates": top_candidates,
    }
    write_json(args.out, payload)
    summary = payload["summary"]["selected_summary"] or {}
    print(
        "claim={claim} strict_success={success} rule={rule} "
        "forward_gain={gain} forward_charge={charge} forward_cpg={cpg} out={out}".format(
            claim=claim_status,
            success=payload["summary"]["strict_success"],
            rule=payload["summary"]["selected_rule_expression"],
            gain=summary.get("forward_rank_gain"),
            charge=summary.get("forward_strict_source_charge_over_rho"),
            cpg=summary.get("forward_charge_per_rank_gain"),
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
