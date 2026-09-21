#!/usr/bin/env python3
"""P1056 public source-cost reducer for the P1054/P1055 rank signal."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1056_p231_public_source_cost_reducer.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1055 = STATE_DIR / "low_term_total2_p1055_p231_source_charged_rank_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1056_p231_public_source_cost_reducer_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1056_p231_public_source_cost_reducer.v1"

PUBLIC_FEATURES = [
    "case_count",
    "priority_count",
    "unique_salts",
    "salt_span",
    "salt_min",
    "salt_max",
    "transfer_span",
    "min_ops",
    "mean_ops",
    "max_ops",
    "op_range",
]


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
    conditions: list[dict[str, Any]] = []
    seen_expressions: set[str] = set()
    for feature in PUBLIC_FEATURES:
        values = sorted({row.get(feature) for row in train_rows if row.get(feature) is not None})
        for value in values:
            ops = [">=", "<="] if isinstance(value, float) else [">=", "<=", "=="]
            for op in ops:
                expression, fn = condition_rule(feature, op, value)
                if expression in seen_expressions:
                    continue
                seen_expressions.add(expression)
                conditions.append({"complexity": 1, "expression": expression, "fn": fn, "kind": "single"})
    rules = list(conditions)
    seen = {item["expression"] for item in rules}
    for left_index, left in enumerate(conditions):
        for right in conditions[left_index + 1 :]:
            expression = f"({left['expression']}) AND ({right['expression']})"
            if expression in seen:
                continue
            seen.add(expression)
            rules.append(
                {
                    "complexity": 2,
                    "expression": expression,
                    "fn": lambda row, left=left["fn"], right=right["fn"]: left(row) and right(row),
                    "kind": "and2",
                }
            )
    return rules


def selected_certificates_for_row(
    row: dict[str, Any],
    cache: dict[Path, list[dict[str, Any]]],
    target: str,
    selector: str,
    top_k: int,
    source: str,
) -> tuple[list[Path], list[dict[str, Any]], list[Path]]:
    scorer = row.get("scorer_artifact")
    if not isinstance(scorer, Path) or not scorer.exists():
        return [], [], []
    base_paths, candidate_paths = p1055.scorer_paths(scorer)
    direct_paths = p1055.direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
    source_candidates = p1055.load_certs_cached(direct_paths, cache)
    source_certs = [
        cert
        for cert in source_candidates
        if p1055.selected_cert_matches(
            cert,
            target,
            selector,
            top_k,
            source,
            row["window_start"],
            row["window_end"],
        )
    ]
    return base_paths, source_certs, direct_paths


def strict_charge(row: dict[str, Any]) -> float:
    return sum(
        p1055.float_value(case.get("direct_ops_over_rho")) or 0.0
        for case in row.get("source_cases") or []
    )


def evaluate_rows(
    rows: list[dict[str, Any]],
    rule: RuleFn,
    cache: dict[Path, list[dict[str, Any]]],
    order: int,
    column: int,
    target: str,
    selector: str,
    top_k: int,
    source: str,
) -> dict[str, Any]:
    selected = [row for row in rows if rule(row)]
    base_paths: set[Path] = set()
    direct_paths: set[Path] = set()
    source_certificates: dict[tuple[str, int], dict[str, Any]] = {}
    charge = 0.0
    for row in selected:
        base, source_certs, direct = selected_certificates_for_row(row, cache, target, selector, top_k, source)
        base_paths.update(base)
        direct_paths.update(direct)
        charge += strict_charge(row)
        for cert in source_certs:
            source_certificates[p1055.cert_key(cert)] = cert
    base_certs = p1055.load_certs_cached(sorted(base_paths), cache)
    factor_hint = max([p1055.int_value(row.get("factor_variable_count")) for row in selected] or [0])
    rank = p1055.rank_audit(
        base_certs,
        list(source_certificates.values()),
        order,
        factor_hint,
        column,
    )
    gain = rank["source_rank_gain_over_base"]
    source_case_count = sum(len(row.get("source_cases") or []) for row in selected)
    return {
        "base_plus_source_free_columns": rank["base_plus_source_free_columns"],
        "base_plus_source_rank": rank["base_plus_source_rank"],
        "base_rank": rank["base_rank"],
        "charge_per_rank_gain": round(charge / gain, 8) if gain else None,
        "direct_certificate_artifact_count": len(direct_paths),
        "factor_variable_count": rank["factor_variable_count"],
        "selected_case_count": source_case_count,
        "selected_window_count": len(selected),
        "selected_windows": [row["window"] for row in selected],
        "source_rank_gain_over_base": gain,
        "source_rows_touching_column": rank["source_rows_touching_column"],
        "source_unique_row_count": rank["source_unique_row_count"],
        "strict_source_charge_over_rho": round(charge, 8),
        "usable_source_certificate_count": len(source_certificates),
    }


def compact_result(result: dict[str, Any], max_windows: int = 30) -> dict[str, Any]:
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
    order: int,
    column: int,
    target: str,
    selector: str,
    top_k: int,
    source: str,
    min_train_windows: int,
    min_train_rank_gain: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    baseline_cpg = full_train["charge_per_rank_gain"] or float("inf")
    candidates = []
    for rule in rules:
        result = evaluate_rows(
            train_rows,
            rule["fn"],
            cache,
            order,
            column,
            target,
            selector,
            top_k,
            source,
        )
        cpg = result["charge_per_rank_gain"]
        if result["selected_window_count"] < min_train_windows:
            continue
        if result["source_rank_gain_over_base"] < min_train_rank_gain:
            continue
        if cpg is None or cpg >= baseline_cpg:
            continue
        candidates.append({"rule": rule, "train": result})
    candidates.sort(
        key=lambda item: (
            item["train"]["charge_per_rank_gain"],
            item["rule"]["complexity"],
            -item["train"]["source_rank_gain_over_base"],
            item["train"]["strict_source_charge_over_rho"],
            item["rule"]["expression"],
        )
    )
    public = [
        {
            "expression": item["rule"]["expression"],
            "kind": item["rule"]["kind"],
            "complexity": item["rule"]["complexity"],
            "train": compact_result(item["train"], max_windows=8),
        }
        for item in candidates[:20]
    ]
    return (candidates[0] if candidates else None), public


def load_records(args: argparse.Namespace) -> tuple[list[dict[str, Any]], str, list[Path]]:
    p1054_payload = p1055.load_json(args.p1054)
    expression = (
        ((p1054_payload.get("selected_rule") or {}).get("expression"))
        or ((p1054_payload.get("summary") or {}).get("selected_rule_expression"))
    )
    if not expression:
        raise ValueError("P1054 artifact has no selected rule expression")
    p1054_rule = p1055.compile_rule(str(expression))
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
        if p1054_rule(row)
    ]
    return records, str(expression), factor_paths + selected_paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1055", type=Path, default=DEFAULT_P1055)
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
    parser.add_argument("--min-train-windows", type=int, default=2)
    parser.add_argument("--min-train-rank-gain", type=int, default=2)
    args = parser.parse_args()

    records, p1054_expression, input_paths = load_records(args)
    rows_by_split = {
        split: [row for row in records if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }
    cache: dict[Path, list[dict[str, Any]]] = {}
    true_rule = lambda row: True
    full_results = {
        split: evaluate_rows(
            rows,
            true_rule,
            cache,
            args.order,
            args.column,
            args.target,
            args.selector,
            args.top_k,
            args.source,
        )
        for split, rows in rows_by_split.items()
    }
    rules = rule_catalog(rows_by_split["calibration"])
    selected, top_candidates = choose_rule(
        rules,
        rows_by_split["calibration"],
        full_results["calibration"],
        cache,
        args.order,
        args.column,
        args.target,
        args.selector,
        args.top_k,
        args.source,
        args.min_train_windows,
        args.min_train_rank_gain,
    )

    if selected is None:
        selected_results = None
        claim_status = "NEGATIVE_RESULT_P1056_NO_CALIBRATION_COST_REDUCER"
    else:
        selected_results = {
            split: evaluate_rows(
                rows,
                selected["rule"]["fn"],
                cache,
                args.order,
                args.column,
                args.target,
                args.selector,
                args.top_k,
                args.source,
            )
            for split, rows in rows_by_split.items()
        }
        forward = selected_results["forward_validation"]
        full_forward = full_results["forward_validation"]
        forward_improves = (
            forward["source_rank_gain_over_base"] > 0
            and forward["charge_per_rank_gain"] is not None
            and full_forward["charge_per_rank_gain"] is not None
            and forward["charge_per_rank_gain"] < full_forward["charge_per_rank_gain"]
        )
        if not forward_improves:
            claim_status = "NEGATIVE_RESULT_P1056_CALIBRATION_COST_REDUCER_FAILS_FORWARD"
        elif forward["strict_source_charge_over_rho"] <= 1.0:
            claim_status = "POSITIVE_SIGNAL_P1056_SUBGATE_RHO_CANDIDATE"
        else:
            claim_status = "POSITIVE_SIGNAL_P1056_PUBLIC_COST_REDUCER_NOT_RHO_WIN"

    selected_summary = None
    if selected_results is not None:
        full_forward = full_results["forward_validation"]
        forward = selected_results["forward_validation"]
        selected_summary = {
            "charge_reduction_factor": (
                round(full_forward["strict_source_charge_over_rho"] / forward["strict_source_charge_over_rho"], 8)
                if forward["strict_source_charge_over_rho"]
                else None
            ),
            "forward_charge_per_rank_gain": forward["charge_per_rank_gain"],
            "forward_full_charge_per_rank_gain": full_forward["charge_per_rank_gain"],
            "forward_rank_gain": forward["source_rank_gain_over_base"],
            "forward_selected_windows": forward["selected_window_count"],
            "forward_strict_source_charge_over_rho": forward["strict_source_charge_over_rho"],
            "rank_gain_retention": (
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
            "p1055": sha256_file(args.p1055) if args.p1055.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1055": str(args.p1055),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "HEURISTIC",
            "PUBLIC-SOURCE-SUBGATE",
            "SOURCE-COST-REDUCTION",
            "TARGET-ELIMINATED-FACTOR-RANK",
            "INDEX-CALCULUS-PRECURSOR",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "full_p1054_gate_results": {split: compact_result(result) for split, result in full_results.items()},
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "direct_shared_verification_labels_excluded_from_subgate": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_faster_than_rho_claim": claim_status != "POSITIVE_SIGNAL_P1056_SUBGATE_RHO_CANDIDATE",
            "rank_measured_from_target_eliminated_certificate_rows": True,
            "subgate_selected_on_calibration_only": selected is not None,
        },
        "parameters": {
            "column": args.column,
            "min_train_rank_gain": args.min_train_rank_gain,
            "min_train_windows": args.min_train_windows,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "public_features": PUBLIC_FEATURES,
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {
            split: len(rows)
            for split, rows in rows_by_split.items()
        },
        "schema": SCHEMA,
        "selected_rule": None
        if selected is None
        else {
            "complexity": selected["rule"]["complexity"],
            "expression": selected["rule"]["expression"],
            "kind": selected["rule"]["kind"],
        },
        "selected_rule_results": None
        if selected_results is None
        else {split: compact_result(result) for split, result in selected_results.items()},
        "summary": {
            "claim_status": claim_status,
            "p1054_rule": p1054_expression,
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
