#!/usr/bin/env python3
"""P1053 accepted-factor materialization bridge audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1053_p231_accepted_factor_materialization_bridge.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1053_p231_accepted_factor_materialization_bridge_probe.json"
DEFAULT_FACTOR_GLOB = (
    "low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json"
)
DEFAULT_SELECTED_GLOB = (
    "low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json"
)
SCHEMA = "ecdlp.low_term_total2_p1053_p231_accepted_factor_materialization_bridge.v1"


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


def window_from_name(path: Path) -> tuple[int, int] | None:
    match = re.search(r"_(\d+)_(\d+)_probe\.json$", path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def split_for(start: int, train_min: int, train_max: int, gap_min: int, gap_max: int, forward_min: int) -> str | None:
    if train_min <= start <= train_max:
        return "calibration"
    if gap_min <= start <= gap_max:
        return "p1052_gap"
    if start >= forward_min:
        return "forward_validation"
    return None


def parse_family_key(key: str) -> dict[str, Any]:
    parts = key.split("|")
    target = parts[0] if len(parts) > 0 else ""
    selector = parts[1] if len(parts) > 1 else ""
    top_k = None
    if len(parts) > 2:
        match = re.fullmatch(r"top(\d+)", parts[2])
        if match:
            top_k = int(match.group(1))
    source = parts[3] if len(parts) > 3 else ""
    return {"key": key, "source": source, "target": target, "top_k": top_k, "selector": selector}


def selected_support(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("selected_term_support") or []}


def selected_priority_hits(case: dict[str, Any]) -> set[int]:
    return {int_value(item) for item in case.get("priority_hits") or []}


def load_factor_reports(
    paths: list[Path],
    order: str,
    column: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
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
        for report in order_report.get("target_column_reports") or []:
            if int_value(report.get("column")) != column:
                continue
            support_counts = {
                "base_relation_support_count": int_value(report.get("base_relation_support_count")),
                "post_greedy_relation_support_count": int_value(report.get("post_greedy_relation_support_count")),
                "candidate_form_certificate_count": int_value(report.get("candidate_form_certificate_count")),
                "greedy_form_certificate_count": int_value(report.get("greedy_form_certificate_count")),
                "remaining_residual_support_count": int_value(report.get("remaining_residual_support_count")),
            }
            accepted_live_support = (
                support_counts["base_relation_support_count"]
                + support_counts["post_greedy_relation_support_count"]
                + support_counts["candidate_form_certificate_count"]
                + support_counts["greedy_form_certificate_count"]
            )
            family_counts = {
                str(key): int_value(value)
                for key, value in (report.get("candidate_form_families") or {}).items()
            }
            reports.append(
                {
                    "accepted_live_support_count": accepted_live_support,
                    "artifact": str(path),
                    "candidate_form_families": family_counts,
                    "column": column,
                    "is_materialized": accepted_live_support > 0,
                    "split": split,
                    "status": str(report.get("status")),
                    "support_counts": support_counts,
                    "window": f"{start}_{end}",
                    "window_end": end,
                    "window_start": start,
                }
            )
    reports.sort(key=lambda item: item["window_start"])
    return reports


def load_selected_cases(
    paths: list[Path],
    column: int,
    train_min: int,
    train_max: int,
    gap_min: int,
    gap_max: int,
    forward_min: int,
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        split = split_for(start, train_min, train_max, gap_min, gap_max, forward_min)
        if split is None:
            continue
        payload = load_json(path)
        for offset, case in enumerate(payload.get("case_reports") or []):
            if not isinstance(case, dict):
                continue
            support = selected_support(case)
            priority_hits = selected_priority_hits(case)
            direct_ops = float_value(case.get("direct_ops_over_rho"))
            shared_ops = float_value(case.get("shared_product_ops_over_rho"))
            cases.append(
                {
                    "artifact": str(path),
                    "artifact_offset": offset,
                    "direct_ops_over_rho": direct_ops,
                    "direct_public_key_verified": bool(case.get("direct_public_key_verified")),
                    "direct_verified_below_rho": bool(case.get("direct_public_key_verified")) and direct_ops is not None and direct_ops < 1.0,
                    "priority_column_hit": column in priority_hits or column in support,
                    "priority_hits": sorted(priority_hits),
                    "public_product_gate_selected": bool(case.get("public_product_gate_selected")),
                    "row_keys": case.get("row_keys") or [],
                    "selected_term_support": sorted(support),
                    "selector": str(case.get("selector")),
                    "shared_ops_over_rho": shared_ops,
                    "shared_product_public_key_verified": bool(case.get("shared_product_public_key_verified")),
                    "shared_verified_below_rho": bool(case.get("shared_product_public_key_verified")) and shared_ops is not None and shared_ops < 1.0,
                    "split": split,
                    "target": str(case.get("target")),
                    "top_k": int_value(case.get("top_k")),
                    "transfer_index": int_value(case.get("transfer_index")),
                    "window": f"{start}_{end}",
                    "window_end": end,
                    "window_start": start,
                }
            )
    cases.sort(key=lambda item: (item["window_start"], item["transfer_index"], item["selector"], item["top_k"]))
    return cases


def discover_calibration_families(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    family_counts: Counter[str] = Counter()
    materialized_windows: dict[str, set[str]] = defaultdict(set)
    for report in reports:
        if report["split"] != "calibration" or not report["is_materialized"]:
            continue
        for key, count in report["candidate_form_families"].items():
            if count > 0:
                family_counts[key] += count
                materialized_windows[key].add(report["window"])
    families = []
    for key, count in family_counts.most_common():
        parsed = parse_family_key(key)
        families.append(
            {
                **parsed,
                "calibration_family_count": count,
                "calibration_materialized_windows": sorted(materialized_windows[key]),
                "calibration_materialized_window_count": len(materialized_windows[key]),
            }
        )
    return families


def case_matches_family(case: dict[str, Any], family: dict[str, Any]) -> bool:
    if family.get("target") and case.get("target") != family["target"]:
        return False
    if family.get("selector") and case.get("selector") != family["selector"]:
        return False
    if family.get("top_k") is not None and int_value(case.get("top_k")) != int_value(family.get("top_k")):
        return False
    return True


def summarize_factor_reports(reports: list[dict[str, Any]], family: dict[str, Any] | None = None) -> dict[str, Any]:
    scoped = reports
    if family is not None:
        key = str(family.get("key"))
        scoped = [report for report in reports if int_value(report["candidate_form_families"].get(key)) > 0 or report["is_materialized"]]
    support_total = Counter()
    family_count = 0
    key = str(family.get("key")) if family else None
    for report in reports:
        for field, value in report["support_counts"].items():
            support_total[field] += int_value(value)
        if key is not None:
            family_count += int_value(report["candidate_form_families"].get(key))
    materialized = [report for report in reports if report["is_materialized"]]
    return {
        "window_count": len(reports),
        "materialized_window_count": len(materialized),
        "materialized_windows": [report["window"] for report in materialized],
        "status_counts": dict(sorted(Counter(report["status"] for report in reports).items())),
        "support_totals": dict(sorted(support_total.items())),
        "selected_family_certificate_count": family_count if family is not None else None,
        "selected_family_windows": sorted(
            report["window"] for report in reports if key is not None and int_value(report["candidate_form_families"].get(key)) > 0
        )
        if family is not None
        else None,
    }


def summarize_selected_cases(cases: list[dict[str, Any]], family: dict[str, Any] | None) -> dict[str, Any]:
    scoped = [case for case in cases if family is None or case_matches_family(case, family)]
    priority = [case for case in scoped if case["priority_column_hit"]]
    direct = [case for case in scoped if case["direct_public_key_verified"]]
    shared = [case for case in scoped if case["shared_product_public_key_verified"]]
    direct_below = [case for case in scoped if case["direct_verified_below_rho"]]
    shared_below = [case for case in scoped if case["shared_verified_below_rho"]]
    ops_values = [
        value
        for case in scoped
        for value in (case["direct_ops_over_rho"], case["shared_ops_over_rho"])
        if value is not None
    ]
    return {
        "case_count": len(scoped),
        "direct_below_rho_count": len(direct_below),
        "direct_verified_count": len(direct),
        "min_ops_over_rho": round(min(ops_values), 8) if ops_values else None,
        "priority_column_case_count": len(priority),
        "selected_window_count": len({case["window"] for case in scoped}),
        "selected_windows": sorted({case["window"] for case in scoped}),
        "shared_below_rho_count": len(shared_below),
        "shared_verified_count": len(shared),
    }


def split_records(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    return {
        "calibration": [item for item in items if item["split"] == "calibration"],
        "p1052_gap": [item for item in items if item["split"] == "p1052_gap"],
        "forward_validation": [item for item in items if item["split"] == "forward_validation"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", default="11779")
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    args = parser.parse_args()

    factor_paths = sorted(args.state_dir.glob(args.factor_glob))
    selected_paths = sorted(args.state_dir.glob(args.selected_glob))
    reports = load_factor_reports(
        factor_paths,
        args.order,
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    cases = load_selected_cases(
        selected_paths,
        args.column,
        args.train_min_start,
        args.train_max_start,
        args.gap_min_start,
        args.gap_max_start,
        args.forward_min_start,
    )
    families = discover_calibration_families(reports)
    selected_family = families[0] if families else None

    reports_by_split = split_records(reports)
    cases_by_split = split_records(cases)
    factor_summary = {
        split: summarize_factor_reports(split_reports, selected_family)
        for split, split_reports in reports_by_split.items()
    }
    selected_summary = {
        split: summarize_selected_cases(split_cases, selected_family)
        for split, split_cases in cases_by_split.items()
    }

    calibration_ok = bool(selected_family) and factor_summary["calibration"]["materialized_window_count"] > 0
    forward_materialized = factor_summary["forward_validation"]["materialized_window_count"] > 0
    forward_selected = selected_summary["forward_validation"]["priority_column_case_count"] > 0
    forward_below_rho = (
        selected_summary["forward_validation"]["direct_below_rho_count"]
        + selected_summary["forward_validation"]["shared_below_rho_count"]
    ) > 0
    strict_success = calibration_ok and forward_materialized and forward_selected and forward_below_rho

    gap_materialized = factor_summary["p1052_gap"]["materialized_window_count"] > 0
    if strict_success and gap_materialized:
        claim_status = "POSITIVE_SIGNAL_P1053_ACCEPTED_FACTOR_MATERIALIZATION_FORWARD_STABLE"
    elif strict_success:
        claim_status = "OBSERVATION_P1053_ACCEPTED_FACTOR_MATERIALIZATION_WITH_P1052_GAP_INSTABILITY"
    elif calibration_ok:
        claim_status = "NEGATIVE_RESULT_P1053_CALIBRATION_FAMILY_NO_FORWARD_MATERIALIZATION"
    else:
        claim_status = "NEGATIVE_RESULT_P1053_NO_CALIBRATION_MATERIALIZATION_FAMILY"

    selected_window_precisions = {}
    for split in ("calibration", "p1052_gap", "forward_validation"):
        selected_windows = selected_summary[split]["selected_window_count"]
        materialized_windows = factor_summary[split]["materialized_window_count"]
        selected_window_precisions[split] = (
            round(materialized_windows / selected_windows, 8) if selected_windows else None
        )

    artifact_hashes = {
        "contract": sha256_file(args.contract) if args.contract.exists() else None,
        "script": sha256_file(Path(__file__)),
        "factor_artifacts": {
            str(path): sha256_file(path)
            for path in factor_paths
            if window_from_name(path) is not None
        },
        "selected_artifacts": {
            str(path): sha256_file(path)
            for path in selected_paths
            if window_from_name(path) is not None
        },
    }
    payload = {
        "artifact_hashes": artifact_hashes,
        "artifacts": {
            "contract": str(args.contract),
            "factor_glob": args.factor_glob,
            "script": str(Path(__file__)),
            "selected_glob": args.selected_glob,
        },
        "calibration_families": families[:12],
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "ACCEPTED-FACTOR-MATERIALIZATION-AUDIT",
            "INDEX-CALCULUS-PRECURSOR",
            "SOURCE-CHARGED-INCOMPLETE",
            "NOT-SPARSE-LA-CLOSURE",
            "NOT-TARGET-DESCENT",
            "POLLARD-RHO-BOUNDARY",
        ],
        "factor_summary": factor_summary,
        "honesty_boundary": {
            "direct_or_shared_verifier_hits_are_diagnostic": True,
            "not_a_complete_index_calculus_solver": True,
            "not_a_faster_than_rho_claim": True,
            "source_charged_collector_required_next": True,
        },
        "parameters": {
            "column": args.column,
            "forward_min_start": args.forward_min_start,
            "gap_max_start": args.gap_max_start,
            "gap_min_start": args.gap_min_start,
            "order": args.order,
            "train_max_start": args.train_max_start,
            "train_min_start": args.train_min_start,
        },
        "schema": SCHEMA,
        "selected_family": selected_family,
        "selected_summary": selected_summary,
        "selected_window_precision": selected_window_precisions,
        "strict_success": strict_success,
        "summary": {
            "calibration_materialized_windows": factor_summary["calibration"]["materialized_window_count"],
            "claim_status": claim_status,
            "factor_report_count": len(reports),
            "forward_materialized_windows": factor_summary["forward_validation"]["materialized_window_count"],
            "forward_selected_family_cases": selected_summary["forward_validation"]["case_count"],
            "gap_materialized_windows": factor_summary["p1052_gap"]["materialized_window_count"],
            "selected_family_key": selected_family.get("key") if selected_family else None,
            "selected_family_train_count": selected_family.get("calibration_family_count") if selected_family else 0,
            "selected_report_case_count": len(cases),
            "strict_success": strict_success,
        },
        "timestamp": now_iso(),
    }
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={strict} family={family} "
        "calibration_materialized={cal} gap_materialized={gap} forward_materialized={forward} out={out}".format(
            claim=claim_status,
            strict=str(strict_success).lower(),
            family=selected_family.get("key") if selected_family else "none",
            cal=factor_summary["calibration"]["materialized_window_count"],
            gap=factor_summary["p1052_gap"]["materialized_window_count"],
            forward=factor_summary["forward_validation"]["materialized_window_count"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
