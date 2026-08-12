#!/usr/bin/env python3
"""P1055 source-charged rank audit for the P1054 public gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable

import low_term_total2_factor_rank_gap_diagnostic as gap
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1055_p231_source_charged_rank_audit.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1055_p231_source_charged_rank_audit_probe.json"
DEFAULT_FACTOR_GLOB = (
    "low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json"
)
DEFAULT_SELECTED_GLOB = (
    "low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json"
)
SCHEMA = "ecdlp.low_term_total2_p1055_p231_source_charged_rank_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None, "sum": 0}
    return {
        "count": len(values),
        "max": round(max(values), 8),
        "mean": round(mean(values), 8),
        "min": round(min(values), 8),
        "sum": round(sum(values), 8),
    }


def window_from_name(path: Path) -> tuple[int, int] | None:
    match = re.search(r"_(\d+)_(\d+)_probe\.json$", path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def window_key(start: int, end: int) -> str:
    return f"{start}_{end}"


def split_for(start: int, train_min: int, train_max: int, gap_min: int, gap_max: int, forward_min: int) -> str | None:
    if train_min <= start <= train_max:
        return "calibration"
    if gap_min <= start <= gap_max:
        return "p1052_gap"
    if start >= forward_min:
        return "forward_validation"
    return None


def extract_salts(row_keys: list[Any]) -> list[int]:
    salts = []
    for row_key in row_keys:
        match = re.search(r"salt(\d+)", str(row_key))
        if match:
            salts.append(int(match.group(1)))
    return salts


def selected_support(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("selected_term_support") or []}


def selected_priority_hits(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("priority_hits") or []}


def compile_rule(expression: str) -> Callable[[dict[str, Any]], bool]:
    expression = expression.strip()
    if " AND " in expression:
        parts = split_rule_parts(expression, " AND ")
        rules = [compile_condition(part) for part in parts]
        return lambda row: all(rule(row) for rule in rules)
    if " OR " in expression:
        parts = split_rule_parts(expression, " OR ")
        rules = [compile_condition(part) for part in parts]
        return lambda row: any(rule(row) for rule in rules)
    return compile_condition(expression)


def split_rule_parts(expression: str, sep: str) -> list[str]:
    return [part.strip().strip("() ") for part in expression.split(sep)]


def compile_condition(condition: str) -> Callable[[dict[str, Any]], bool]:
    condition = condition.strip().strip("() ")
    match = re.fullmatch(r"([A-Za-z0-9_]+)\s*(>=|<=|==)\s*(-?\d+(?:\.\d+)?)", condition)
    if not match:
        raise ValueError(f"unsupported P1054 rule condition: {condition!r}")
    feature, op, raw_threshold = match.groups()
    threshold: int | float = float(raw_threshold) if "." in raw_threshold else int(raw_threshold)

    def rule(row: dict[str, Any]) -> bool:
        value = row.get(feature)
        if value is None:
            return False
        if op == ">=":
            return value >= threshold
        if op == "<=":
            return value <= threshold
        return value == threshold

    return rule


def source_case_matches(case: dict[str, Any], target: str, selector: str, top_k: int) -> bool:
    return (
        str(case.get("target")) == target
        and str(case.get("selector")) == selector
        and int_value(case.get("top_k"), -1) == top_k
    )


def source_features(cases: list[dict[str, Any]], column: int) -> dict[str, Any]:
    all_salts = [salt for case in cases for salt in extract_salts(case.get("row_keys") or [])]
    transfers = [int_value(case.get("transfer_index")) for case in cases]
    direct_ops = [float_value(case.get("direct_ops_over_rho")) for case in cases]
    direct_ops = [value for value in direct_ops if value is not None]
    salt_min = min(all_salts) if all_salts else None
    salt_max = max(all_salts) if all_salts else None
    min_ops = min(direct_ops) if direct_ops else None
    max_ops = max(direct_ops) if direct_ops else None
    return {
        "case_count": len(cases),
        "diagnostic_direct_below_rho_count": sum(
            1
            for case in cases
            if bool(case.get("direct_public_key_verified"))
            and float_value(case.get("direct_ops_over_rho")) is not None
            and float_value(case.get("direct_ops_over_rho")) < 1.0
        ),
        "diagnostic_direct_verified_count": sum(1 for case in cases if bool(case.get("direct_public_key_verified"))),
        "diagnostic_shared_below_rho_count": sum(
            1
            for case in cases
            if bool(case.get("shared_product_public_key_verified"))
            and float_value(case.get("shared_product_ops_over_rho")) is not None
            and float_value(case.get("shared_product_ops_over_rho")) < 1.0
        ),
        "diagnostic_shared_verified_count": sum(1 for case in cases if bool(case.get("shared_product_public_key_verified"))),
        "has_source_family": bool(cases),
        "max_ops": max_ops,
        "mean_ops": mean(direct_ops) if direct_ops else None,
        "min_ops": min_ops,
        "op_range": max_ops - min_ops if min_ops is not None and max_ops is not None else None,
        "priority_count": sum(
            1
            for case in cases
            if column in selected_support(case) or column in selected_priority_hits(case)
        ),
        "salt_max": salt_max,
        "salt_min": salt_min,
        "salt_span": salt_max - salt_min if salt_min is not None and salt_max is not None else None,
        "transfer_span": max(transfers) - min(transfers) if transfers else None,
        "unique_salts": len(set(all_salts)),
    }


def load_source_case_windows(
    paths: list[Path],
    target: str,
    selector: str,
    top_k: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> dict[str, dict[str, Any]]:
    windows: dict[str, dict[str, Any]] = {}
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        split = split_for(start, train_min, train_max, gap_min, gap_max, forward_min)
        if split is None:
            continue
        payload = load_json(path)
        cases = [
            case
            for case in (payload.get("case_reports") or [])
            if isinstance(case, dict) and source_case_matches(case, target, selector, top_k)
        ]
        key = window_key(start, end)
        windows[key] = {
            "artifact": path,
            "cases": cases,
            "split": split,
            "window": key,
            "window_end": end,
            "window_start": start,
        }
    return windows


def load_factor_windows(
    paths: list[Path],
    order: str,
    column: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> dict[str, dict[str, Any]]:
    windows: dict[str, dict[str, Any]] = {}
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        split = split_for(start, train_min, train_max, gap_min, gap_max, forward_min)
        if split is None:
            continue
        payload = load_json(path)
        order_report = (payload.get("order_reports") or {}).get(order) or {}
        column_report = None
        for report in order_report.get("target_column_reports") or []:
            if int_value(report.get("column")) == column:
                column_report = report
                break
        if column_report is None:
            continue
        support_counts = {
            "base_relation_support_count": int_value(column_report.get("base_relation_support_count")),
            "candidate_form_certificate_count": int_value(column_report.get("candidate_form_certificate_count")),
            "greedy_form_certificate_count": int_value(column_report.get("greedy_form_certificate_count")),
            "post_greedy_relation_support_count": int_value(column_report.get("post_greedy_relation_support_count")),
            "remaining_residual_support_count": int_value(column_report.get("remaining_residual_support_count")),
        }
        accepted_live_support = (
            support_counts["base_relation_support_count"]
            + support_counts["candidate_form_certificate_count"]
            + support_counts["greedy_form_certificate_count"]
            + support_counts["post_greedy_relation_support_count"]
        )
        key = window_key(start, end)
        windows[key] = {
            "accepted_live_support_count": accepted_live_support,
            "artifact": path,
            "base_rank": int_value(order_report.get("base_rank")),
            "candidate_certificate_count": int_value(order_report.get("candidate_certificate_count")),
            "factor_variable_count": int_value(order_report.get("factor_variable_count")),
            "is_materialized": accepted_live_support > 0,
            "post_greedy_deficiency": int_value(order_report.get("post_greedy_deficiency")),
            "post_greedy_free_columns": order_report.get("post_greedy_free_columns") or [],
            "post_greedy_rank": int_value(order_report.get("post_greedy_rank")),
            "scorer_artifact": Path((payload.get("artifacts") or {}).get("scorer_artifact", "")),
            "split": split,
            "status": str(column_report.get("status")),
            "support_counts": support_counts,
            "window": key,
            "window_end": end,
            "window_start": start,
        }
    return windows


def join_windows(
    factor_windows: dict[str, dict[str, Any]],
    source_windows: dict[str, dict[str, Any]],
    column: int,
) -> list[dict[str, Any]]:
    rows = []
    for key, factor in factor_windows.items():
        source = source_windows.get(key, {})
        cases = source.get("cases") or []
        features = source_features(cases, column)
        rows.append(
            {
                **features,
                **factor,
                "source_artifact": str(source.get("artifact")) if source.get("artifact") else None,
                "source_cases": cases,
            }
        )
    rows.sort(key=lambda item: item["window_start"])
    return rows


def scorer_paths(path: Path) -> tuple[list[Path], list[Path]]:
    payload = load_json(path)
    artifacts = payload.get("artifacts") if isinstance(payload.get("artifacts"), dict) else {}
    return (
        [Path(item) for item in artifacts.get("base_certificates") or []],
        [Path(item) for item in artifacts.get("candidate_certificates") or []],
    )


def selected_cert_matches(
    cert: dict[str, Any],
    target: str,
    selector: str,
    top_k: int,
    source: str,
    start: int,
    end: int,
) -> bool:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    clause = str(cert.get("clause") or selected.get("clause") or "")
    transfer_index = int_value(selected.get("transfer_index"), -1)
    return (
        str(selected.get("target")) == target
        and str(selected.get("selector")) == selector
        and int_value(selected.get("top_k"), -1) == top_k
        and clause == source
        and start <= transfer_index <= end
    )


def cert_key(cert: dict[str, Any]) -> tuple[str, int]:
    return (str(cert.get("_artifact")), int_value(cert.get("_artifact_offset")))


def load_certs_cached(paths: list[Path], cache: dict[Path, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    certs: list[dict[str, Any]] = []
    for path in paths:
        if not path.exists():
            continue
        if path not in cache:
            cache[path] = factor_bank.load_certificates([path])
        certs.extend(cache[path])
    return certs


def direct_source_paths(candidate_paths: list[Path], start: int, end: int) -> list[Path]:
    suffix = f"_{start}_{end}_probe.json"
    return [
        path
        for path in candidate_paths
        if "direct_relation_equation_certificate_22050_col15_lowterm_support5" in path.name
        and path.name.endswith(suffix)
    ]


def rank_audit(
    base_certs: list[dict[str, Any]],
    source_certs: list[dict[str, Any]],
    order: int,
    factor_count_hint: int,
    column: int,
) -> dict[str, Any]:
    all_certs = [cert for cert in base_certs + source_certs if int_value(cert.get("order")) == order]
    factor_count = max(factor_count_hint, gap.factor_count_for_order(all_certs, order))
    base_rows = gap.unique_relation_rows(base_certs, order, factor_count)
    source_rows = gap.unique_relation_rows(source_certs, order, factor_count)
    base_basis, base_pivots = gap.rref_rows([row["coeffs"] for row in base_rows], order)
    source_basis, source_pivots = gap.rref_rows([row["coeffs"] for row in source_rows], order)
    plus_basis, plus_pivots = gap.rref_rows([row["coeffs"] for row in base_rows + source_rows], order)
    source_support = Counter()
    for row in source_rows:
        for item in row.get("factor_support") or []:
            source_support[int_value(item)] += 1
    return {
        "base_free_columns": [idx for idx in range(factor_count) if idx not in set(base_pivots)],
        "base_rank": len(base_pivots),
        "base_unique_row_count": len(base_rows),
        "base_plus_source_free_columns": [idx for idx in range(factor_count) if idx not in set(plus_pivots)],
        "base_plus_source_rank": len(plus_pivots),
        "column_free_after_source": column not in set(plus_pivots),
        "factor_variable_count": factor_count,
        "source_only_rank": len(source_pivots),
        "source_rank_gain_over_base": len(plus_pivots) - len(base_pivots),
        "source_rows_touching_column": source_support[column],
        "source_support_columns": sorted(source_support),
        "source_unique_row_count": len(source_rows),
    }


def summarize_cases(rows: list[dict[str, Any]]) -> dict[str, Any]:
    cases = [case for row in rows for case in row.get("source_cases") or []]
    direct_ops = [
        float_value(case.get("direct_ops_over_rho"))
        for case in cases
        if float_value(case.get("direct_ops_over_rho")) is not None
    ]
    return {
        "direct_ops_over_rho": stat(direct_ops),
        "direct_verified_below_rho_count": sum(
            1
            for case in cases
            if bool(case.get("direct_public_key_verified"))
            and float_value(case.get("direct_ops_over_rho")) is not None
            and float_value(case.get("direct_ops_over_rho")) < 1.0
        ),
        "direct_verified_count": sum(1 for case in cases if bool(case.get("direct_public_key_verified"))),
        "materialized_window_count": sum(1 for row in rows if row.get("is_materialized")),
        "selected_case_count": len(cases),
        "selected_window_count": len(rows),
        "selected_windows": [row["window"] for row in rows],
    }


def compact_windows(rows: list[dict[str, Any]], cert_counts: dict[str, int], rank_results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    compact = []
    for row in rows[:25]:
        rank = rank_results.get(row["window"]) or {}
        compact.append(
            {
                "accepted_live_support_count": row.get("accepted_live_support_count"),
                "direct_ops_sum_over_rho": round(
                    sum(
                        float_value(case.get("direct_ops_over_rho")) or 0.0
                        for case in row.get("source_cases") or []
                    ),
                    8,
                ),
                "is_materialized": row.get("is_materialized"),
                "post_greedy_free_columns": row.get("post_greedy_free_columns"),
                "post_greedy_rank": row.get("post_greedy_rank"),
                "source_cert_count": cert_counts.get(row["window"], 0),
                "source_rank_gain_over_base": rank.get("source_rank_gain_over_base"),
                "source_unique_row_count": rank.get("source_unique_row_count"),
                "status": row.get("status"),
                "window": row["window"],
            }
        )
    return compact


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=DEFAULT_SELECTED_GLOB)
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
    args = parser.parse_args()

    p1054 = load_json(args.p1054)
    expression = (
        ((p1054.get("selected_rule") or {}).get("expression"))
        or ((p1054.get("summary") or {}).get("selected_rule_expression"))
    )
    if not expression:
        raise ValueError("P1054 artifact has no selected rule expression")
    rule = compile_rule(str(expression))

    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    selected_paths = sorted(args.state_dir.glob(args.selected_glob))
    factor_windows = load_factor_windows(
        factor_paths,
        str(args.order),
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    source_windows = load_source_case_windows(
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
    records = join_windows(factor_windows, source_windows, args.column)
    selected_rows = [row for row in records if rule(row)]
    selected_by_split = {
        split: [row for row in selected_rows if row["split"] == split]
        for split in ("calibration", "p1052_gap", "forward_validation")
    }

    cert_cache: dict[Path, list[dict[str, Any]]] = {}
    base_paths_by_split: dict[str, set[Path]] = defaultdict(set)
    source_certs_by_split: dict[str, list[dict[str, Any]]] = defaultdict(list)
    selected_input_paths = [args.p1054, args.contract]
    per_window_rank: dict[str, dict[str, Any]] = {}
    per_window_cert_counts: dict[str, int] = {}
    missing_direct_paths: list[str] = []

    for row in selected_rows:
        scorer = row.get("scorer_artifact")
        if not isinstance(scorer, Path) or not scorer.exists():
            continue
        base_paths, candidate_paths = scorer_paths(scorer)
        direct_paths = direct_source_paths(candidate_paths, row["window_start"], row["window_end"])
        selected_input_paths.extend([row["artifact"], Path(row["source_artifact"]) if row.get("source_artifact") else Path()])
        selected_input_paths.extend(base_paths)
        selected_input_paths.extend(direct_paths)
        if not direct_paths:
            missing_direct_paths.append(row["window"])
        base_certs = load_certs_cached(base_paths, cert_cache)
        source_candidates = load_certs_cached(direct_paths, cert_cache)
        source_certs = [
            cert
            for cert in source_candidates
            if selected_cert_matches(
                cert,
                args.target,
                args.selector,
                args.top_k,
                args.source,
                row["window_start"],
                row["window_end"],
            )
        ]
        base_paths_by_split[row["split"]].update(base_paths)
        source_certs_by_split[row["split"]].extend(source_certs)
        per_window_cert_counts[row["window"]] = len(source_certs)
        per_window_rank[row["window"]] = rank_audit(
            base_certs,
            source_certs,
            args.order,
            int_value(row.get("factor_variable_count")),
            args.column,
        )

    split_rank: dict[str, dict[str, Any]] = {}
    split_case_summary: dict[str, dict[str, Any]] = {}
    for split, rows in selected_by_split.items():
        base_certs = load_certs_cached(sorted(base_paths_by_split[split]), cert_cache)
        unique_source = {
            cert_key(cert): cert
            for cert in source_certs_by_split[split]
        }
        factor_hint = max([int_value(row.get("factor_variable_count")) for row in rows] or [0])
        split_rank[split] = rank_audit(
            base_certs,
            list(unique_source.values()),
            args.order,
            factor_hint,
            args.column,
        )
        split_case_summary[split] = summarize_cases(rows)
        split_rank[split]["usable_source_certificate_count"] = len(unique_source)
        charge = split_case_summary[split]["direct_ops_over_rho"]["sum"]
        gain = split_rank[split]["source_rank_gain_over_base"]
        split_rank[split]["strict_source_charge_over_rho"] = charge
        split_rank[split]["strict_charge_per_rank_gain"] = (
            round(charge / gain, 8) if gain else None
        )

    forward_rank = split_rank["forward_validation"]
    forward_charge = forward_rank["strict_source_charge_over_rho"]
    if forward_rank["usable_source_certificate_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P1055_NO_FORWARD_SOURCE_CERTIFICATES"
    elif forward_rank["source_unique_row_count"] == 0:
        claim_status = "NEGATIVE_RESULT_P1055_NO_FORWARD_TARGET_ELIMINATED_ROWS"
    elif forward_rank["source_rank_gain_over_base"] <= 0:
        claim_status = "NEGATIVE_RESULT_P1055_NO_FORWARD_RANK_GAIN"
    elif forward_charge <= 1.0:
        claim_status = "POSITIVE_SIGNAL_P1055_SOURCE_CHARGED_RHO_CANDIDATE"
    else:
        claim_status = "POSITIVE_SIGNAL_P1055_SOURCE_CHARGED_RANK_GAIN_NOT_RHO_WIN"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in selected_input_paths if path.exists()]),
            "input_artifact_digest": digest_paths([path for path in selected_input_paths if path.exists()]),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "factor_glob": args.factor_glob,
            "p1054": str(args.p1054),
            "script": str(Path(__file__)),
            "selected_glob": args.selected_glob,
        },
        "case_charge_summary": split_case_summary,
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "HEURISTIC",
            "PUBLIC-SOURCE-GATE",
            "SOURCE-CHARGED",
            "TARGET-ELIMINATED-FACTOR-RANK",
            "INDEX-CALCULUS-PRECURSOR",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "honesty_boundary": {
            "cryptographic_scale_unproved": True,
            "direct_shared_verification_labels_excluded_from_gate": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_faster_than_rho_claim": claim_status != "POSITIVE_SIGNAL_P1055_SOURCE_CHARGED_RHO_CANDIDATE",
            "rank_measured_from_target_eliminated_certificate_rows": True,
            "strict_charge_sums_all_source_family_cases_in_selected_windows": True,
        },
        "missing_direct_source_windows": missing_direct_paths[:50],
        "parameters": {
            "column": args.column,
            "forward_min_start": args.forward_min_start,
            "gap_max_start": args.gap_max_start,
            "gap_min_start": args.gap_min_start,
            "order": args.order,
            "p1054_rule": expression,
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
            "train_max_start": args.train_max_start,
            "train_min_start": args.train_min_start,
        },
        "record_counts": {
            "factor_windows": len(factor_windows),
            "records": len(records),
            "selected_windows": len(selected_rows),
            "source_windows": len(source_windows),
        },
        "schema": SCHEMA,
        "selected_window_samples": {
            split: compact_windows(rows, per_window_cert_counts, per_window_rank)
            for split, rows in selected_by_split.items()
        },
        "split_rank_audit": split_rank,
        "summary": {
            "claim_status": claim_status,
            "forward_rank_gain": forward_rank["source_rank_gain_over_base"],
            "forward_source_charge_over_rho": forward_charge,
            "forward_unique_source_rows": forward_rank["source_unique_row_count"],
            "forward_usable_source_certificates": forward_rank["usable_source_certificate_count"],
            "p1052_gap_selected_windows": len(selected_by_split["p1052_gap"]),
            "p1054_rule": expression,
            "strict_success": claim_status.startswith("POSITIVE_SIGNAL"),
        },
        "timestamp": now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} forward_rank_gain={rank_gain} "
        "forward_charge={charge} forward_certs={certs} out={out}".format(
            claim=claim_status,
            success=payload["summary"]["strict_success"],
            rank_gain=forward_rank["source_rank_gain_over_base"],
            charge=forward_charge,
            certs=forward_rank["usable_source_certificate_count"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
