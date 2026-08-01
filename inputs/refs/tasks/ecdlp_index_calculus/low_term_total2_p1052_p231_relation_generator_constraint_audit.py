#!/usr/bin/env python3
"""P1052 selected-leaf to factor-signature bridge audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1052_p231_relation_generator_constraint_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1052_p231_relation_generator_constraint_audit_probe.json"
DEFAULT_SELECTED_GLOB = (
    "low_term_total2_selected_leaf_term_support_scout_22050_col15_selector_expanded_*_probe.json"
)
DEFAULT_COLUMN_GLOB = (
    "low_term_total2_factor_column_target_scout_target67_22050_multibranch_plus_priority_hash6_plus_direct_col15_lowterm_support5_*_probe.json"
)
SCHEMA = "ecdlp.low_term_total2_p1052_p231_relation_generator_constraint_audit.v1"


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


def support_tuple(case: dict[str, Any]) -> tuple[int, ...]:
    return tuple(sorted(int_value(item) for item in case.get("selected_term_support") or []))


def selector_family(selector: str) -> str:
    if "low_term" in selector:
        return "low_term"
    if "hybrid" in selector:
        return "hybrid"
    if "hash" in selector:
        return "hash"
    if "cost" in selector:
        return "cost"
    if "double" in selector:
        return "double"
    return "other"


def load_selected_cases(paths: list[Path], min_start: int, max_start: int, priority_column: int) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        if start < min_start or start > max_start:
            continue
        payload = load_json(path)
        for offset, case in enumerate(payload.get("case_reports") or []):
            if not isinstance(case, dict):
                continue
            support = support_tuple(case)
            priority_hits = tuple(sorted(int_value(item) for item in case.get("priority_hits") or []))
            direct_ops = float_value(case.get("direct_ops_over_rho"))
            shared_ops = float_value(case.get("shared_product_ops_over_rho"))
            cases.append(
                {
                    "artifact": str(path),
                    "artifact_offset": offset,
                    "direct_ops_over_rho": direct_ops,
                    "direct_verified_priority": bool(priority_hits and case.get("direct_public_key_verified")),
                    "gate_selected": bool(case.get("public_product_gate_selected")),
                    "priority_hit": priority_column in set(priority_hits) or priority_column in set(support),
                    "priority_hits": list(priority_hits),
                    "row_keys": case.get("row_keys") or [],
                    "selected_term_support": list(support),
                    "selector": str(case.get("selector")),
                    "selector_family": selector_family(str(case.get("selector"))),
                    "shared_ops_over_rho": shared_ops,
                    "shared_product_rank": int_value(case.get("shared_product_rank")),
                    "shared_verified_priority": bool(priority_hits and case.get("shared_product_public_key_verified")),
                    "support_size": len(support),
                    "target": case.get("target"),
                    "top_k": int_value(case.get("top_k")),
                    "transfer_index": int_value(case.get("transfer_index")),
                    "window": f"{start}_{end}",
                    "window_end": end,
                    "window_start": start,
                }
            )
    cases.sort(key=lambda item: (item["window_start"], item["transfer_index"], item["selector"], item["top_k"]))
    return cases


def column_report_for(payload: dict[str, Any], order: str, column: int) -> dict[str, Any] | None:
    order_report = (payload.get("order_reports") or {}).get(order) or {}
    for report in order_report.get("target_column_reports") or []:
        if int_value(report.get("column")) == column:
            return report
    return None


def load_column_reports(paths: list[Path], min_start: int, max_start: int, order: str, column: int) -> list[dict[str, Any]]:
    reports = []
    for path in paths:
        window = window_from_name(path)
        if window is None:
            continue
        start, end = window
        if start < min_start or start > max_start:
            continue
        payload = load_json(path)
        report = column_report_for(payload, order, column)
        if not report:
            continue
        accepted_support = (
            int_value(report.get("base_relation_support_count"))
            + int_value(report.get("post_greedy_relation_support_count"))
            + int_value(report.get("candidate_form_certificate_count"))
            + int_value(report.get("greedy_form_certificate_count"))
        )
        reports.append(
            {
                "accepted_or_live_support_count": accepted_support,
                "artifact": str(path),
                "base_relation_support_count": int_value(report.get("base_relation_support_count")),
                "candidate_form_certificate_count": int_value(report.get("candidate_form_certificate_count")),
                "column": column,
                "greedy_form_certificate_count": int_value(report.get("greedy_form_certificate_count")),
                "is_post_greedy_free": bool(report.get("is_post_greedy_free")),
                "post_greedy_relation_support_count": int_value(report.get("post_greedy_relation_support_count")),
                "status": str(report.get("status")),
                "window": f"{start}_{end}",
                "window_end": end,
                "window_start": start,
            }
        )
    reports.sort(key=lambda item: item["window_start"])
    return reports


RuleFn = Callable[[dict[str, Any]], bool]


def rule_catalog(cases: list[dict[str, Any]], priority_column: int) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []

    def add(name: str, description: str, fn: RuleFn) -> None:
        rules.append({"description": description, "fn": fn, "name": name})

    add("priority_hit", f"selected leaf support contains priority column {priority_column}", lambda row: row["priority_hit"])
    add(
        "gate_selected_priority",
        f"product gate selected and selected support contains priority column {priority_column}",
        lambda row: row["priority_hit"] and row["gate_selected"],
    )
    for top_k in sorted({int_value(row.get("top_k")) for row in cases}):
        add(f"top_k_eq_{top_k}", f"top_k == {top_k}", lambda row, top_k=top_k: row["top_k"] == top_k)
        add(
            f"gate_priority_top_k_eq_{top_k}",
            f"gate-selected priority case with top_k == {top_k}",
            lambda row, top_k=top_k: row["priority_hit"] and row["gate_selected"] and row["top_k"] == top_k,
        )
    for family in sorted({str(row.get("selector_family")) for row in cases}):
        add(f"family_eq_{family}", f"selector family == {family}", lambda row, family=family: row["selector_family"] == family)
        add(
            f"gate_priority_family_eq_{family}",
            f"gate-selected priority case with selector family == {family}",
            lambda row, family=family: row["priority_hit"] and row["gate_selected"] and row["selector_family"] == family,
        )
    for selector in sorted({str(row.get("selector")) for row in cases}):
        safe = re.sub(r"[^A-Za-z0-9]+", "_", selector).strip("_")
        add(f"selector_eq_{safe}", f"selector == {selector}", lambda row, selector=selector: row["selector"] == selector)
    for threshold in (8, 10, 12, 15):
        add(
            f"support_size_le_{threshold}",
            f"selected term support size <= {threshold}",
            lambda row, threshold=threshold: row["support_size"] <= threshold,
        )
        add(
            f"gate_priority_support_size_le_{threshold}",
            f"gate-selected priority case with support size <= {threshold}",
            lambda row, threshold=threshold: row["priority_hit"] and row["gate_selected"] and row["support_size"] <= threshold,
        )
    for motif in ((7, 15), (8, 11), (10, 14), (10, 15), (11, 15), (14, 15)):
        name = "_".join(str(item) for item in motif)
        motif_set = set(motif)
        add(
            f"contains_motif_{name}",
            f"selected term support contains {motif}",
            lambda row, motif_set=motif_set: motif_set <= set(row["selected_term_support"]),
        )
        add(
            f"gate_priority_contains_motif_{name}",
            f"gate-selected priority case containing {motif}",
            lambda row, motif_set=motif_set: row["priority_hit"] and row["gate_selected"] and motif_set <= set(row["selected_term_support"]),
        )
    return rules


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_ops = [row["direct_ops_over_rho"] for row in cases if row["direct_verified_priority"] and row["direct_ops_over_rho"] is not None]
    shared_ops = [row["shared_ops_over_rho"] for row in cases if row["shared_verified_priority"] and row["shared_ops_over_rho"] is not None]
    priority_count = sum(1 for row in cases if row["priority_hit"])
    gate_priority_count = sum(1 for row in cases if row["priority_hit"] and row["gate_selected"])
    direct_count = sum(1 for row in cases if row["direct_verified_priority"])
    shared_count = sum(1 for row in cases if row["shared_verified_priority"])
    return {
        "case_count": len(cases),
        "direct_verified_priority_count": direct_count,
        "direct_verified_priority_precision": round(direct_count / priority_count, 8) if priority_count else None,
        "direct_verified_priority_with_ops_below_rho": sum(1 for value in direct_ops if value < 1.0),
        "gate_selected_priority_count": gate_priority_count,
        "priority_hit_count": priority_count,
        "selector_family_counts": dict(sorted(Counter(row["selector_family"] for row in cases).items())),
        "shared_verified_priority_count": shared_count,
        "shared_verified_priority_precision": round(shared_count / priority_count, 8) if priority_count else None,
        "shared_verified_priority_with_ops_below_rho": sum(1 for value in shared_ops if value < 1.0),
        "support_size_histogram": {str(key): value for key, value in sorted(Counter(row["support_size"] for row in cases).items())},
        "window_count": len({row["window"] for row in cases}),
        "windows": sorted({row["window"] for row in cases}),
    }


def evaluate_rule(rule: dict[str, Any], cases: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in cases if rule["fn"](row)]
    direct = [row for row in selected if row["direct_verified_priority"]]
    shared = [row for row in selected if row["shared_verified_priority"]]
    shared_below_rho = [
        row
        for row in shared
        if row["shared_ops_over_rho"] is not None and row["shared_ops_over_rho"] < 1.0
    ]
    return {
        "direct_verified_count": len(direct),
        "direct_verified_precision": round(len(direct) / len(selected), 8) if selected else None,
        "selected_count": len(selected),
        "selected_window_count": len({row["window"] for row in selected}),
        "selected_windows": sorted({row["window"] for row in selected}),
        "shared_below_rho_count": len(shared_below_rho),
        "shared_ops_over_rho_min": min([row["shared_ops_over_rho"] for row in shared if row["shared_ops_over_rho"] is not None] or [None]),
        "shared_verified_count": len(shared),
        "shared_verified_precision": round(len(shared) / len(selected), 8) if selected else None,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    state_dir = Path(args.state_dir)
    selected_paths = sorted(state_dir.glob(args.selected_glob))
    column_paths = sorted(state_dir.glob(args.column_glob))
    cases = load_selected_cases(selected_paths, args.min_start, args.max_start, args.priority_column)
    column_reports = load_column_reports(
        column_paths,
        args.min_start,
        args.max_start,
        str(args.order),
        args.priority_column,
    )
    train_cases = [row for row in cases if row["window_start"] <= args.train_max_start]
    validation_cases = [row for row in cases if row["window_start"] >= args.validation_min_start]
    validation_reports = [row for row in column_reports if row["window_start"] >= args.validation_min_start]

    train_summary = summarize_cases(train_cases)
    validation_summary = summarize_cases(validation_cases)
    train_baseline = train_summary["shared_verified_priority_precision"] or 0.0
    validation_baseline = validation_summary["shared_verified_priority_precision"] or 0.0

    rule_results = []
    for rule in rule_catalog(train_cases + validation_cases, args.priority_column):
        train_eval = evaluate_rule(rule, train_cases)
        validation_eval = evaluate_rule(rule, validation_cases)
        if train_eval["selected_count"] < args.min_train_selected:
            continue
        if validation_eval["selected_count"] < args.min_validation_selected:
            continue
        rule_results.append(
            {
                "description": rule["description"],
                "name": rule["name"],
                "train": train_eval,
                "validation": validation_eval,
            }
        )
    rule_results.sort(
        key=lambda item: (
            -(item["train"]["shared_verified_precision"] or 0),
            -item["train"]["shared_verified_count"],
            -(item["validation"]["shared_verified_precision"] or 0),
            item["name"],
        )
    )

    factor_signature_materialized_count = sum(
        1 for report in validation_reports if int_value(report.get("accepted_or_live_support_count")) > 0
    )
    best_rules = rule_results[:12]
    strict_passes = []
    for item in rule_results:
        train_precision = item["train"]["shared_verified_precision"] or 0.0
        validation_precision = item["validation"]["shared_verified_precision"] or 0.0
        if (
            train_precision > train_baseline
            and validation_precision > validation_baseline
            and item["validation"]["shared_below_rho_count"] > 0
            and factor_signature_materialized_count > 0
        ):
            strict_passes.append(item)

    positive_control_ok = train_summary["priority_hit_count"] > 0 and validation_summary["priority_hit_count"] > 0
    if strict_passes:
        claim = "P1052_RELATION_GENERATOR_FACTOR_SIGNATURE_SIGNAL"
        taxonomy = "OBSERVATION"
    elif positive_control_ok and validation_summary["shared_verified_priority_count"] > 0 and factor_signature_materialized_count == 0:
        claim = "NEGATIVE_RESULT_P1052_SELECTED_LEAF_VERIFIER_SIGNAL_FACTOR_SIGNATURE_GAP"
        taxonomy = "NEGATIVE RESULT"
    elif positive_control_ok:
        claim = "NEGATIVE_RESULT_P1052_NO_VALIDATED_SELECTED_LEAF_FACTOR_SIGNATURE_BRIDGE"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "P1052_POSITIVE_CONTROL_FAILED_NO_PRIORITY_VISIBILITY"
        taxonomy = "OPEN"

    used_paths = sorted({Path(row["artifact"]) for row in cases} | {Path(row["artifact"]) for row in column_reports})
    return {
        "artifacts": {
            "column_glob": str(state_dir / args.column_glob),
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "selected_glob": str(state_dir / args.selected_glob),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "input_sha256": {str(path): sha256_file(path) for path in used_paths},
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "column_reports": column_reports,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "PRE-RELATION: selected-leaf support is source-generation evidence, not an accepted factor equation.",
            "FACTOR-SIGNATURE-BRIDGE: promotion requires accepted factor-row or live-form support for the priority column.",
            "SOURCE-CHARGED-INCOMPLETE: this audit reports selected-case ops/rho but does not replace a full rejected-row collector.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "max_start": args.max_start,
            "min_start": args.min_start,
            "min_train_selected": args.min_train_selected,
            "min_validation_selected": args.min_validation_selected,
            "order": args.order,
            "priority_column": args.priority_column,
            "train_max_start": args.train_max_start,
            "validation_min_start": args.validation_min_start,
        },
        "rule_results": rule_results,
        "schema": SCHEMA,
        "strict_validation_passes": strict_passes,
        "summary": {
            "best_rule_names": [item["name"] for item in best_rules[:5]],
            "candidate_rule_count": len(rule_results),
            "claim_status": claim,
            "factor_signature_materialized_count": factor_signature_materialized_count,
            "positive_control_ok": positive_control_ok,
            "selected_artifact_count": len({row["artifact"] for row in cases}),
            "strict_validation_pass_count": len(strict_passes),
            "train": train_summary,
            "validation": validation_summary,
            "validation_column_status_counts": dict(sorted(Counter(row["status"] for row in validation_reports).items())),
        },
        "timestamp": now_iso(),
        "top_rule_results": best_rules,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--column-glob", default=DEFAULT_COLUMN_GLOB)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT))
    parser.add_argument("--max-start", type=int, default=11983)
    parser.add_argument("--min-start", type=int, default=11888)
    parser.add_argument("--min-train-selected", type=int, default=8)
    parser.add_argument("--min-validation-selected", type=int, default=8)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--priority-column", type=int, default=15)
    parser.add_argument("--selected-glob", default=DEFAULT_SELECTED_GLOB)
    parser.add_argument("--state-dir", default=str(STATE_DIR))
    parser.add_argument("--train-max-start", type=int, default=11919)
    parser.add_argument("--validation-min-start", type=int, default=11968)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} train_cases={train_cases} validation_cases={validation_cases} validation_shared={validation_shared} factor_materialized={factor_materialized} strict_pass={strict_pass} out={out}".format(
            claim=payload["claim_status"],
            train_cases=summary["train"]["case_count"],
            validation_cases=summary["validation"]["case_count"],
            validation_shared=summary["validation"]["shared_verified_priority_count"],
            factor_materialized=summary["factor_signature_materialized_count"],
            strict_pass=summary["strict_validation_pass_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
