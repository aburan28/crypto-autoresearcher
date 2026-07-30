#!/usr/bin/env python3
"""P700 two-stage endpoint cost decomposition.

P699 found public selectors that give rank+1 below rho and full-rank closure
above rho.  This audit decomposes each public rank+1 stage by adding one
endpoint form at a time and charging the incremental completion cost.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p698_minimal_endpoint_subset_cost_audit as p698
import low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit as p699


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p700_two_stage_endpoint_cost_decomposition_probe.json"


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def record_index(record: dict[str, Any]) -> int:
    return int_value(record.get("_endpoint_form_index"))


def evaluate_record_set(
    name: str,
    records: list[dict[str, Any]],
    verifier: Any,
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    cost = p698.scan_cost(records)
    union = p697.union_derive(verifier, records)
    cert = p697.pseudo_certificate(name, records, target, union)
    evaluation = p697.evaluate_candidate(
        name,
        base,
        base_state,
        cert,
        priority_columns,
        sample_limit,
    )
    evaluation.update(
        {
            "selected_form_count": len(records),
            "selected_form_indices": [record_index(record) for record in records],
            "selected_unique_leaf_scan_count": cost["unique_leaf_scan_count"],
            "selected_unique_leaf_scan_ops_over_rho": cost["unique_leaf_scan_ops_over_rho"],
            "selected_unique_leaf_scans": cost["unique_leaf_scans"],
            "union_derived_secret": union.get("union_derived_secret"),
            "union_public_key_verified": bool(union.get("union_public_key_verified")),
            "union_rank": int_value(union.get("union_rank")),
            "union_relation_count": int_value(union.get("union_relation_count")),
        }
    )
    return evaluation


def compact_eval(evaluation: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "factor_variables_derivable_gain",
        "missing_columns_after",
        "new_missing_touch_relation_count",
        "newly_derivable_priority_columns",
        "rank_after",
        "rank_before",
        "rank_gain",
        "selected_form_count",
        "selected_form_indices",
        "selected_unique_leaf_scan_count",
        "selected_unique_leaf_scan_ops_over_rho",
        "union_derived_secret",
        "union_public_key_verified",
        "union_rank",
        "union_relation_count",
        "unique_factor_relation_gain",
    ]
    return {key: evaluation.get(key) for key in keys}


def completion_candidates(
    stage_records: list[dict[str, Any]],
    all_records: list[dict[str, Any]],
    verifier: Any,
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> list[dict[str, Any]]:
    stage_indices = {record_index(record) for record in stage_records}
    stage_cost = p698.scan_cost(stage_records)
    completions = []
    for record in all_records:
        if record_index(record) in stage_indices:
            continue
        combined = stage_records + [record]
        combined_eval = evaluate_record_set(
            "p700_stage_plus_completion",
            combined,
            verifier,
            target,
            base,
            base_state,
            priority_columns,
            sample_limit,
        )
        if int_value(combined_eval.get("rank_after")) < int_value(base_state["factor_count"]):
            continue
        combined_cost = float_value(combined_eval.get("selected_unique_leaf_scan_ops_over_rho"))
        completion = {
            "combined": compact_eval(combined_eval),
            "completion_form": p697.compact_event_sample(record),
            "completion_form_index": record_index(record),
            "completion_incremental_ops_over_rho": round(
                combined_cost - float_value(stage_cost["unique_leaf_scan_ops_over_rho"]),
                8,
            ),
        }
        completions.append(completion)
    completions.sort(
        key=lambda item: (
            not bool((item.get("combined") or {}).get("union_public_key_verified")),
            float_value((item.get("combined") or {}).get("selected_unique_leaf_scan_ops_over_rho"), 999.0),
            float_value(item.get("completion_incremental_ops_over_rho"), 999.0),
            int_value(item.get("completion_form_index")),
        )
    )
    return completions


def stage_report(
    surface: str,
    selector: dict[str, Any],
    selected: list[dict[str, Any]],
    all_records: list[dict[str, Any]],
    verifier: Any,
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
    stage_eval = evaluate_record_set(
        selector["name"],
        selected,
        verifier,
        target,
        base,
        base_state,
        priority_columns,
        sample_limit,
    )
    completions = []
    if int_value(stage_eval.get("rank_gain")) == 1:
        completions = completion_candidates(
            selected,
            all_records,
            verifier,
            target,
            base,
            base_state,
            priority_columns,
            sample_limit,
        )
    best_completion = completions[0] if completions else None
    best_verified = next(
        (
            completion
            for completion in completions
            if bool((completion.get("combined") or {}).get("union_public_key_verified"))
        ),
        None,
    )
    return {
        "best_completion": best_completion,
        "best_verified_completion": best_verified,
        "completion_count": len(completions),
        "completion_samples": completions[:sample_limit],
        "selector": selector["name"],
        "selector_rule": selector["rule"],
        "stage": compact_eval(stage_eval),
        "stage_selected_form_samples": [
            p697.compact_event_sample(record) for record in selected[:sample_limit]
        ],
        "surface": surface,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["below_rho_verified_full_completion_count"]:
        return "P700_TWO_STAGE_BELOW_RHO_VERIFIED_FULL_RANK"
    if summary["below_rho_rank1_stage_with_verified_completion_count"]:
        return "P700_RANK1_BELOW_RHO_COMPLETES_ABOVE_RHO"
    if summary["below_rho_rank1_stage_count"]:
        return "P700_RANK1_BELOW_RHO_STAGE_COMPLETION_OPEN"
    return "NEGATIVE_RESULT_P700_NO_BELOW_RHO_PUBLIC_RANK1_STAGE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    surfaces = p699.existing_surfaces(args)
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    p698_payload = p699.load_json(Path(args.p698))
    selectors = None
    surface_reports = []
    stage_reports = []

    for surface_index, (surface_name, source, product) in enumerate(surfaces):
        verifier, surface_meta, records = p699.collect_surface_records(args, source, product, priority_columns)
        if surface_index == 0:
            training_records = p699.train_records_from_p698(p698_payload, records)
            selectors = p699.make_selectors(training_records)
        if selectors is None:
            selectors = p699.make_selectors([])
        local_stage_reports = []
        for selector in selectors:
            selected = [record for record in records if selector["match"](record)]
            if not selected:
                continue
            report = stage_report(
                surface_name,
                selector,
                selected,
                records,
                verifier,
                args.target,
                base,
                base_state,
                priority_columns,
                int_value(args.sample_limit, 12),
            )
            local_stage_reports.append(report)
            stage_reports.append(report)
        surface_reports.append(
            {
                "product": str(product),
                "source": str(source),
                "stage_reports": [
                    {
                        "best_completion": report["best_completion"],
                        "best_verified_completion": report["best_verified_completion"],
                        "completion_count": report["completion_count"],
                        "selector": report["selector"],
                        "stage": report["stage"],
                    }
                    for report in local_stage_reports
                ],
                "surface": surface_name,
                "surface_meta": surface_meta,
            }
        )

    below_rho_rank1 = [
        report
        for report in stage_reports
        if int_value((report.get("stage") or {}).get("rank_gain")) == 1
        and float_value((report.get("stage") or {}).get("selected_unique_leaf_scan_ops_over_rho"), 999.0) <= 1.0
    ]
    verified_completion = [
        report
        for report in stage_reports
        if report.get("best_verified_completion") is not None
    ]
    below_rho_rank1_with_verified = [
        report for report in below_rho_rank1 if report.get("best_verified_completion") is not None
    ]
    below_rho_verified_full = [
        report
        for report in stage_reports
        if report.get("best_verified_completion")
        and float_value(
            ((report.get("best_verified_completion") or {}).get("combined") or {}).get(
                "selected_unique_leaf_scan_ops_over_rho"
            ),
            999.0,
        )
        <= 1.0
    ]
    best_verified_reports = sorted(
        verified_completion,
        key=lambda report: float_value(
            ((report.get("best_verified_completion") or {}).get("combined") or {}).get(
                "selected_unique_leaf_scan_ops_over_rho"
            ),
            999.0,
        ),
    )
    summary = {
        "base_factor_variable_count": int_value(base_state["factor_count"]),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": int_value(base_state["rank"]),
        "base_unique_factor_relation_count": len(base_state["unique"]),
        "below_rho_rank1_stage_count": len(below_rho_rank1),
        "below_rho_rank1_stage_with_verified_completion_count": len(below_rho_rank1_with_verified),
        "below_rho_verified_full_completion_count": len(below_rho_verified_full),
        "best_verified_combined_ops_over_rho": (
            ((best_verified_reports[0].get("best_verified_completion") or {}).get("combined") or {}).get(
                "selected_unique_leaf_scan_ops_over_rho"
            )
            if best_verified_reports
            else None
        ),
        "best_verified_completion_incremental_ops_over_rho": (
            (best_verified_reports[0].get("best_verified_completion") or {}).get(
                "completion_incremental_ops_over_rho"
            )
            if best_verified_reports
            else None
        ),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "public_rank1_stage_count": sum(
            1 for report in stage_reports if int_value((report.get("stage") or {}).get("rank_gain")) == 1
        ),
        "stage_report_count": len(stage_reports),
        "surface_count": len(surfaces),
        "verified_completion_count": len(verified_completion),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p698": str(Path(args.p698)),
        },
        "best_verified_completion_reports": [
            {
                "best_verified_completion": report["best_verified_completion"],
                "selector": report["selector"],
                "stage": report["stage"],
                "surface": report["surface"],
            }
            for report in best_verified_reports[: int_value(args.sample_limit, 12)]
        ],
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: stages use public endpoint descriptor selectors over reconstructed source surfaces.",
            "Completion search adds one endpoint form at a time; it is a decomposition audit, not a fresh public discovery algorithm.",
            "A below-rho first stage is not a faster-than-rho algorithm unless the verified full-rank combined charge is also below rho.",
        ],
        "method": "p700_two_stage_endpoint_cost_decomposition",
        "parameters": {
            "max_cases": int_value(args.max_cases),
            "max_endpoint_leaves": int_value(args.max_endpoint_leaves),
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p700_two_stage_endpoint_cost_decomposition.v1",
        "stage_reports": stage_reports,
        "summary": summary,
        "surface_reports": surface_reports,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--p698", default=str(p699.DEFAULT_P698))
    parser.add_argument("--surface", action="append", default=None, help="Surface as NAME|SOURCE|PRODUCT.")
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(
        json.dumps(
            {
                "best_verified_completion_reports": payload["best_verified_completion_reports"],
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
