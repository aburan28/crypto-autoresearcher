#!/usr/bin/env python3
"""Replay source/product cases and search for nullspace-breaking candidates.

The direct bridge can produce many valid local certificates while still
repeating rows whose projection onto the remaining nullspace is zero.  This
scout looks one step earlier than certificate export: it replays bounded
product/source cases, builds the direct public forms, and classifies the
target-eliminated rows by nullspace projection.  It is a scheduling aid, not a
rank promotion by itself.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe
import low_term_total2_deficiency_direction_scorer as deficiency
import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import low_term_total2_nullspace_projection_obstruction_scout as obstruction
import low_term_total2_source_relation_equation_certificate as certificate_probe
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE_TEMPLATE = (
    "ecdlp_index_calculus_state/"
    "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_{window}_col15_selector_expanded_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_nullspace_source_candidate_scout_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def parse_paths(raw: str | None) -> list[Path]:
    if not raw:
        return []
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def parse_targets(raw: str) -> set[str]:
    return {item.strip() for item in raw.split(",") if item.strip()}


def window_label(path: Path) -> str:
    matches = re.findall(r"(?<!\d)(\d{4,})_(\d{4,})(?!\d)", path.name)
    if matches:
        start, end = matches[-1]
        return f"{start}_{end}"
    return path.stem


def source_for_window(template: str, window: str) -> Path:
    return Path(template.format(window=window))


def case_key(case: dict[str, Any], window: str) -> tuple[Any, ...]:
    return (
        window,
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("selector"),
        int_value(case.get("top_k")),
        tuple(sorted(str(item) for item in case.get("row_keys") or [])),
    )


def selected_term_support(contexts: list[dict[str, Any]]) -> list[int]:
    support: set[int] = set()
    for context in contexts:
        selected = {int_value(leaf) for leaf in context.get("selected_leaf_indices") or []}
        for scout in context["built"].get("scouts") or []:
            pos = scout.get("scout_pos")
            if pos in selected or (isinstance(pos, int) and pos - 1 in selected):
                support.update(int_value(index) for index, _sign in scout.get("signed_terms") or [])
    return sorted(support)


def direct_unique_events(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    seen: set[tuple[tuple[int, ...], int]] = set()
    for row in rows:
        scan = row.get("_scan") if isinstance(row.get("_scan"), dict) else {}
        for event in scan.get("relation_events") or []:
            coeffs, rhs, _terms = event["form"]
            key = (tuple(int(coeff) for coeff in coeffs), int(rhs))
            if key in seen:
                continue
            seen.add(key)
            events.append(event)
    return events


def compact_case(case: dict[str, Any], artifact: Path, window: str) -> dict[str, Any]:
    return {
        "artifact": str(artifact),
        "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
        "direct_public_key_verified": bool(case.get("direct_union_public_key_verified")),
        "public_product_gate_selected": bool(case.get("public_product_gate_selected")),
        "row_keys": case.get("row_keys") or [],
        "selector": case.get("selector"),
        "shared_product_public_key_verified": bool(case.get("shared_product_union_public_key_verified")),
        "target": case.get("target"),
        "top_k": int_value(case.get("top_k")),
        "transfer_index": int_value(case.get("transfer_index")),
        "window": window,
    }


def load_cases(
    product_artifacts: list[Path],
    targets: set[str],
    direct_verified_only: bool,
    selectors: set[str],
) -> list[tuple[Path, str, dict[str, Any]]]:
    rows: list[tuple[Path, str, dict[str, Any]]] = []
    seen: set[tuple[Any, ...]] = set()
    for artifact in product_artifacts:
        payload = load_json(artifact)
        window = window_label(artifact)
        for case in payload.get("cases") or []:
            if not isinstance(case, dict):
                continue
            if targets and str(case.get("target")) not in targets:
                continue
            if selectors and str(case.get("selector")) not in selectors:
                continue
            if direct_verified_only and not bool(case.get("direct_union_public_key_verified")):
                continue
            key = case_key(case, window)
            if key in seen:
                continue
            seen.add(key)
            rows.append((artifact, window, case))
    rows.sort(
        key=lambda item: (
            item[1],
            str(item[2].get("target")),
            int_value(item[2].get("transfer_index")),
            str(item[2].get("selector")),
            int_value(item[2].get("top_k")),
        )
    )
    return rows


def frontier_nullspace(frontier_paths: list[Path], order: int) -> tuple[list[dict[str, Any]], int]:
    frontier_certificates = factor_bank.load_certificates(frontier_paths)
    frontier_rows, _rhs, _rows_by_key, factor_count = deficiency.row_vectors(
        frontier_certificates,
        order,
    )
    rref_rows, pivot_columns = deficiency.rref_mod(frontier_rows, order)
    _free_columns, null_basis = deficiency.nullspace_basis(
        rref_rows,
        pivot_columns,
        factor_count,
        order,
    )
    return null_basis, factor_count


def replay_case(
    case: dict[str, Any],
    artifact: Path,
    window: str,
    source_template: str,
    order: int,
    null_basis: list[dict[str, Any]],
    factor_count: int,
) -> dict[str, Any]:
    compact = compact_case(case, artifact, window)
    source_path = source_for_window(source_template, window)
    source = load_json(source_path)
    source_case = context_probe.find_source_case(
        source,
        str(case.get("target")),
        int_value(case.get("transfer_index")),
        str(case.get("selector")),
        int_value(case.get("top_k")),
    )
    verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows, direct_ops, rho, _row_profiles = timing_probe.direct_witness_rows(verifier, contexts)
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = direct_witness_probe.union_derive(verifier, direct_rows, built_by_row, "_scan")
    if not contexts:
        raise ValueError(f"no selected contexts for {window} {case.get('target')}")
    case_order = int(contexts[0]["built"]["order"])
    events = direct_unique_events(direct_rows)
    forms = [certificate_probe.compact_form(event, case_order) for event in events]
    cert = {
        "_artifact": str(artifact),
        "_artifact_offset": 0,
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if bool(direct_union.get("union_public_key_verified"))
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW"
        ),
        "forms": forms,
        "forms_count": len(forms),
        "order": case_order,
        "public_key_verified": bool(direct_union.get("union_public_key_verified")),
        "rank": int_value(direct_union.get("union_rank")),
        "selected": {
            "direct_ops": direct_ops,
            "direct_ops_over_rho": round(direct_ops / rho, 8) if rho else None,
            "rho": rho,
            "selector": case.get("selector"),
            "target": case.get("target"),
            "top_k": int_value(case.get("top_k")),
            "transfer_index": int_value(case.get("transfer_index")),
        },
        "window": window,
    }
    status_counts: Counter[str] = Counter()
    samples = []
    for relation in factor_bank.target_eliminated_rows(cert):
        if relation.get("relation_status") != "TARGET_ELIMINATED_FACTOR_RELATION":
            continue
        report = obstruction.relation_report(cert, relation, null_basis, factor_count, order)
        status = str(report.get("status"))
        status_counts[status] += 1
        if len(samples) < 6 or status == "NONZERO_NULLSPACE_PROJECTION":
            samples.append(
                {
                    "factor_support": report.get("factor_support"),
                    "left_form": report.get("left_form"),
                    "pair": report.get("pair"),
                    "projections": report.get("projections"),
                    "q_coeffs": report.get("q_coeffs"),
                    "right_form": report.get("right_form"),
                    "status": status,
                }
            )
    nonzero = status_counts.get("NONZERO_NULLSPACE_PROJECTION", 0)
    cancellation = status_counts.get("ZERO_PROJECTION_BY_EQUAL_OPPOSITE_CANCELLATION", 0)
    if nonzero:
        work_order = "EXPORT_AND_PROMOTE_NONZERO_NULLSPACE_SOURCE_CASE"
    elif cancellation:
        work_order = "REJECT_SYMMETRIC_NULLSPACE_REPEAT_OR_FIND_ASYMMETRIC_PARTNER"
    elif status_counts:
        work_order = "LOW_PRIORITY_ZERO_PROJECTION_SOURCE_CASE"
    else:
        work_order = "NO_TARGET_ELIMINATED_FACTOR_ROWS"
    return {
        **compact,
        "case_order": case_order,
        "direct_ops_over_rho_replay": cert["selected"].get("direct_ops_over_rho"),
        "forms": [
            {
                "coeff_support": [
                    idx
                    for idx, coeff in enumerate((form.get("coeffs") or [])[1:])
                    if int_value(coeff) % case_order
                ],
                "terms": form.get("terms") or [],
            }
            for form in forms
        ],
        "forms_count": len(forms),
        "public_key_verified_replay": cert["public_key_verified"],
        "rank_replay": cert["rank"],
        "selected_term_support": selected_term_support(contexts),
        "source": str(source_path),
        "status_counts": dict(sorted(status_counts.items())),
        "target_eliminated_row_count": sum(status_counts.values()),
        "sample_relations": samples,
        "work_order": work_order,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontier-certificates", required=True)
    parser.add_argument("--product-artifacts", required=True)
    parser.add_argument("--source-template", default=DEFAULT_SOURCE_TEMPLATE)
    parser.add_argument("--targets", default="22050.cf1@11731")
    parser.add_argument("--selectors", default="")
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--max-cases", type=int, default=80)
    parser.add_argument("--direct-verified-only", action="store_true")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frontier_paths = parse_paths(args.frontier_certificates)
    product_paths = parse_paths(args.product_artifacts)
    selectors = parse_targets(args.selectors)
    targets = parse_targets(args.targets)
    null_basis, factor_count = frontier_nullspace(frontier_paths, int_value(args.order, 11779))
    candidate_cases = load_cases(
        product_paths,
        targets,
        direct_verified_only=bool(args.direct_verified_only),
        selectors=selectors,
    )
    reports = []
    errors = []
    for artifact, window, case in candidate_cases[: max(0, int_value(args.max_cases, 80))]:
        try:
            reports.append(
                replay_case(
                    case,
                    artifact,
                    window,
                    args.source_template,
                    int_value(args.order, 11779),
                    null_basis,
                    factor_count,
                )
            )
        except Exception as error:  # Preserve source-case failures for red-team review.
            errors.append({**compact_case(case, artifact, window), "error": str(error)})
    reports.sort(
        key=lambda row: (
            -int_value((row.get("status_counts") or {}).get("NONZERO_NULLSPACE_PROJECTION")),
            int_value((row.get("status_counts") or {}).get("ZERO_PROJECTION_BY_EQUAL_OPPOSITE_CANCELLATION")),
            -int_value(row.get("target_eliminated_row_count")),
            float(row.get("direct_ops_over_rho_replay") or row.get("direct_ops_over_rho") or 10**9),
            str(row.get("window")),
            int_value(row.get("transfer_index")),
        )
    )
    aggregate = Counter()
    work_orders = Counter()
    for report in reports:
        aggregate.update(report.get("status_counts") or {})
        work_orders[str(report.get("work_order"))] += 1
    if aggregate.get("NONZERO_NULLSPACE_PROJECTION"):
        claim_status = "NONZERO_NULLSPACE_SOURCE_CASE_FOUND"
    elif aggregate.get("ZERO_PROJECTION_BY_EQUAL_OPPOSITE_CANCELLATION"):
        claim_status = "NEGATIVE_RESULT_SOURCE_CASES_REPEAT_NULLSPACE_SYMMETRY"
    elif reports:
        claim_status = "NEGATIVE_RESULT_NO_SOURCE_NULLSPACE_PROJECTION"
    else:
        claim_status = "NO_SOURCE_CASES_REPLAYED"
    payload = {
        "artifacts": {
            "frontier_certificates": [str(path) for path in frontier_paths],
            "product_artifacts": [str(path) for path in product_paths],
            "source_template": args.source_template,
        },
        "case_reports": reports[:100],
        "claim_status": claim_status,
        "created_at": now_iso(),
        "errors": errors[:40],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source replays use the local direct selected-leaf verifier.",
            "NO SPEEDUP CLAIM: source candidates must still be exported and pass rank/frontier gates.",
        ],
        "parameters": {
            "direct_verified_only": bool(args.direct_verified_only),
            "max_cases": max(0, int_value(args.max_cases, 80)),
            "order": int_value(args.order, 11779),
            "selectors": sorted(selectors),
            "targets": sorted(targets),
        },
        "schema": "ecdlp.low_term_total2_nullspace_source_candidate_scout.v1",
        "summary": {
            "candidate_case_count": len(candidate_cases),
            "claim_status": claim_status,
            "error_count": len(errors),
            "replayed_case_count": len(reports),
            "status_counts": dict(sorted(aggregate.items())),
            "work_order_counts": dict(sorted(work_orders.items())),
        },
    }
    write_json(Path(args.out), payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
