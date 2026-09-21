#!/usr/bin/env python3
"""P1061 salt-family selector audit for independent non-anchor rank."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1058_p231_disjoint_replication_batching as p1058
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1061_p231_salt_family_independent_rank.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1056 = STATE_DIR / "low_term_total2_p1056_p231_public_source_cost_reducer_probe.json"
DEFAULT_P1057 = STATE_DIR / "low_term_total2_p1057_p231_single_anchor_direction_subgate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1060 = STATE_DIR / "low_term_total2_p1060_p231_rowkey_disjoint_descent_pressure_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1061_p231_salt_family_independent_rank_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1061_p231_salt_family_independent_rank.v1"


CaseRule = Callable[[dict[str, Any]], bool]

SALT_FEATURE_PRIORITY = {
    "salt_sum": 0,
    "salt_max": 1,
    "salt_gap": 2,
    "salt_min": 3,
    "has_high_ge_175": 4,
    "has_175": 5,
    "has_173": 6,
    "priority_both": 7,
    "priority_15": 8,
    "priority_6": 9,
}


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


def parse_window(value: str) -> tuple[int, int]:
    start, end = value.split("_", 1)
    return int(start), int(end)


def salt_values(case: dict[str, Any]) -> list[int]:
    salts = []
    for row_key in case.get("row_keys") or []:
        match = re.search(r"salt(\d+)", str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return sorted(salts)


def case_features(case: dict[str, Any]) -> dict[str, Any]:
    salts = salt_values(case)
    hits = {p1055.int_value(item) for item in case.get("priority_hits") or []}
    return {
        "has_173": 173 in salts,
        "has_175": 175 in salts,
        "has_high_ge_175": any(item >= 175 for item in salts),
        "ops": p1055.float_value(case.get("direct_ops_over_rho")),
        "priority_6": 6 in hits,
        "priority_15": 15 in hits,
        "priority_both": {6, 15}.issubset(hits),
        "salt_gap": max(salts) - min(salts) if len(salts) >= 2 else None,
        "salt_max": max(salts) if salts else None,
        "salt_min": min(salts) if salts else None,
        "salt_sum": sum(salts) if salts else None,
    }


def format_value(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.8f}".rstrip("0").rstrip(".")
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def condition_rule(feature: str, op: str, threshold: Any) -> tuple[str, CaseRule, dict[str, Any]]:
    expression = f"{feature} {op} {format_value(threshold)}"

    def rule(case: dict[str, Any]) -> bool:
        value = case_features(case).get(feature)
        if value is None:
            return False
        if op == ">=":
            return value >= threshold
        if op == "<=":
            return value <= threshold
        return value == threshold

    meta = {
        "complexity": 1,
        "features": [feature],
        "is_equality": op == "==",
        "ops": [op],
    }
    return expression, rule, meta


def rule_catalog(train_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    train_cases = [case for row in train_rows for case in row.get("source_cases") or []]
    conditions: list[dict[str, Any]] = []
    seen: set[str] = set()
    numeric_features = ["salt_sum", "salt_max", "salt_gap", "salt_min"]
    bool_features = ["has_high_ge_175", "has_175", "has_173", "priority_both", "priority_15", "priority_6"]
    for feature in numeric_features:
        values = sorted({case_features(case).get(feature) for case in train_cases if case_features(case).get(feature) is not None})
        for value in values:
            for op in (">=", "<=", "=="):
                expression, fn, meta = condition_rule(feature, op, value)
                if expression in seen:
                    continue
                seen.add(expression)
                conditions.append({"expression": expression, "fn": fn, **meta})
    for feature in bool_features:
        for value in (True, False):
            expression, fn, meta = condition_rule(feature, "==", value)
            if expression in seen:
                continue
            seen.add(expression)
            conditions.append({"expression": expression, "fn": fn, **meta})

    rules = list(conditions)
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
                    "features": left["features"] + right["features"],
                    "fn": lambda case, left=left["fn"], right=right["fn"]: left(case) and right(case),
                    "is_equality": left["is_equality"] or right["is_equality"],
                    "ops": left["ops"] + right["ops"],
                }
            )
    return rules


def first_matching_selector(rule: CaseRule) -> p1059.CaseSelector:
    def select(row: dict[str, Any]) -> list[dict[str, Any]]:
        matches = [case for case in row.get("source_cases") or [] if rule(case)]
        return p1059.first_by_transfer(matches)

    return select


def compact_result(result: dict[str, Any], max_windows: int = 20, max_cases: int = 16) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    cases = compact.get("selected_case_details") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    compact["selected_case_details"] = cases[:max_cases]
    compact["selected_case_details_truncated"] = len(cases) > max_cases
    return compact


def selected_rowkey_from_p1059(path: Path) -> tuple[str, ...]:
    payload = load_json(path)
    rowkey = ((payload.get("parameters") or {}).get("selected_rowkey")) or (
        (payload.get("summary") or {}).get("selected_rowkey")
    )
    if not rowkey:
        raise ValueError(f"P1059 artifact has no selected rowkey: {path}")
    return tuple(sorted(str(item) for item in rowkey))


def rule_generalization_key(rule: dict[str, Any], train: dict[str, Any]) -> tuple[Any, ...]:
    first_feature = min((SALT_FEATURE_PRIORITY.get(feature, 99) for feature in rule["features"]), default=99)
    non_equality = not rule["is_equality"]
    return (
        train["charge_per_rank_gain"] or float("inf"),
        -int(non_equality),
        rule["complexity"],
        first_feature,
        train["strict_source_charge_over_rho"],
        rule["expression"],
    )


def choose_family_rule(
    train_rows: list[dict[str, Any]],
    cache: dict[Path, list[dict[str, Any]]],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    candidates = []
    for rule in rule_catalog(train_rows):
        train = p1059.evaluate_case_policy(train_rows, first_matching_selector(rule["fn"]), cache, args)
        if train["source_rank_gain_over_base"] < args.min_train_rank_gain:
            continue
        if train["strict_source_charge_over_rho"] >= args.max_train_charge_over_rho:
            continue
        candidates.append({"rule": rule, "train": train})
    candidates.sort(key=lambda item: rule_generalization_key(item["rule"], item["train"]))
    public = [
        {
            "expression": item["rule"]["expression"],
            "features": item["rule"]["features"],
            "is_equality": item["rule"]["is_equality"],
            "train": compact_result(item["train"], max_windows=8, max_cases=8),
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
    parser.add_argument("--p1057", type=Path, default=DEFAULT_P1057)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1060", type=Path, default=DEFAULT_P1060)
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
    parser.add_argument("--anchor-window", default="18464_18471")
    parser.add_argument("--min-train-rank-gain", type=int, default=2)
    parser.add_argument("--max-train-charge-over-rho", type=float, default=1.0)
    parser.add_argument("--max-disjoint-charge-over-rho", type=float, default=1.0)
    args = parser.parse_args()

    selected_rowkey = selected_rowkey_from_p1059(args.p1059)
    records, p1054_expression, p1056_expression, p1057_expression, input_paths = p1058.load_records_and_rules(args)
    rows_by_split = {
        split: [row for row in records if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }
    anchor_start, anchor_end = parse_window(args.anchor_window)
    anchor_rows = [
        row
        for row in rows_by_split["forward_validation"]
        if row["window_start"] == anchor_start and row["window_end"] == anchor_end
    ]
    disjoint_forward_rows = [
        row
        for row in rows_by_split["forward_validation"]
        if row["window_end"] < anchor_start or row["window_start"] > anchor_end
    ]

    cache: dict[Path, list[dict[str, Any]]] = {}
    selected, top_candidates = choose_family_rule(rows_by_split["calibration"], cache, args)
    if selected is None:
        family_selector = lambda row: []
        selected_expression = None
        selected_rule = None
    else:
        selected_rule = selected["rule"]
        selected_expression = selected_rule["expression"]
        family_selector = first_matching_selector(selected_rule["fn"])

    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    family_results = {
        "calibration": compact_result(p1059.evaluate_case_policy(rows_by_split["calibration"], family_selector, cache, args)),
        "forward_all": compact_result(p1059.evaluate_case_policy(rows_by_split["forward_validation"], family_selector, cache, args)),
        "forward_anchor": compact_result(p1059.evaluate_case_policy(anchor_rows, family_selector, cache, args)),
        "forward_disjoint": compact_result(p1059.evaluate_case_policy(disjoint_forward_rows, family_selector, cache, args)),
        "calibration_plus_forward": compact_result(
            p1059.evaluate_case_policy(rows_by_split["calibration"] + rows_by_split["forward_validation"], family_selector, cache, args)
        ),
    }
    exact_results = {
        "forward_anchor": compact_result(p1059.evaluate_case_policy(anchor_rows, exact_selector, cache, args)),
        "forward_disjoint": compact_result(p1059.evaluate_case_policy(disjoint_forward_rows, exact_selector, cache, args)),
    }

    anchor_gain = exact_results["forward_anchor"]["source_rank_gain_over_base"]
    disjoint = family_results["forward_disjoint"]
    forward_all = family_results["forward_all"]
    extra_gain = forward_all["source_rank_gain_over_base"] - anchor_gain
    disjoint_packet_positive = (
        disjoint["selected_window_count"] > 0
        and disjoint["source_rank_gain_over_base"] > 0
        and disjoint["strict_source_charge_over_rho"] < args.max_disjoint_charge_over_rho
    )
    independent_positive = disjoint_packet_positive and extra_gain > 0
    if independent_positive:
        claim_status = "POSITIVE_SIGNAL_P1061_SALT_FAMILY_INDEPENDENT_DISJOINT_RANK"
    elif disjoint_packet_positive:
        claim_status = "POSITIVE_SIGNAL_P1061_SALT_FAMILY_DISJOINT_PACKET_RANK_DEPENDENT"
    elif selected is None:
        claim_status = "NEGATIVE_RESULT_P1061_NO_CALIBRATION_FAMILY"
    else:
        claim_status = "NEGATIVE_RESULT_P1061_NO_DISJOINT_FAMILY_PACKET"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1056": sha256_file(args.p1056) if args.p1056.exists() else None,
            "p1057": sha256_file(args.p1057) if args.p1057.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1060": sha256_file(args.p1060) if args.p1060.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1056": str(args.p1056),
            "p1057": str(args.p1057),
            "p1059": str(args.p1059),
            "p1060": str(args.p1060),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "CALIBRATION-SELECTED",
            "PUBLIC-SALT-FAMILY",
            "DISJOINT-RANK-PACKET",
            "CUMULATIVE-RANK-AUDIT",
            "INDEX-CALCULUS-PRECURSOR",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "exact_p1059_rowkey": exact_results,
            "selected_family": family_results,
        },
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "family_selected_from_calibration_only": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "rank_dependent_disjoint_packet_is_not_collector_closure": True,
            "target_descent_not_implemented": True,
        },
        "parameters": {
            "anchor_window": args.anchor_window,
            "column": args.column,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "p1056_rule": p1056_expression,
            "p1057_rule": p1057_expression,
            "selected_expression": selected_expression,
            "selected_rowkey_control": list(selected_rowkey),
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {
            "calibration_windows": len(rows_by_split["calibration"]),
            "forward_anchor_windows": len(anchor_rows),
            "forward_disjoint_windows": len(disjoint_forward_rows),
            "forward_windows": len(rows_by_split["forward_validation"]),
            "top_candidate_count": len(top_candidates),
        },
        "schema": SCHEMA,
        "summary": {
            "anchor_exact_charge": exact_results["forward_anchor"]["strict_source_charge_over_rho"],
            "anchor_exact_rank_gain": anchor_gain,
            "claim_status": claim_status,
            "cumulative_extra_gain_over_anchor": extra_gain,
            "family_forward_charge": forward_all["strict_source_charge_over_rho"],
            "family_forward_rank_gain": forward_all["source_rank_gain_over_base"],
            "family_forward_selected_windows": forward_all["selected_windows"],
            "non_anchor_charge": disjoint["strict_source_charge_over_rho"],
            "non_anchor_rank_gain": disjoint["source_rank_gain_over_base"],
            "non_anchor_selected_windows": disjoint["selected_windows"],
            "selected_expression": selected_expression,
            "strict_success": independent_positive,
            "weak_positive": disjoint_packet_positive,
        },
        "timestamp_utc": now_iso(),
        "top_calibration_candidates": top_candidates,
    }
    payload["strict_success"] = bool(payload["summary"]["strict_success"])
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} weak_positive={weak} rule={rule} "
        "non_anchor_charge={charge} non_anchor_gain={gain} extra_gain={extra} out={out}".format(
            claim=claim_status,
            success=payload["strict_success"],
            weak=payload["summary"]["weak_positive"],
            rule=selected_expression,
            charge=payload["summary"]["non_anchor_charge"],
            gain=payload["summary"]["non_anchor_rank_gain"],
            extra=payload["summary"]["cumulative_extra_gain_over_anchor"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
