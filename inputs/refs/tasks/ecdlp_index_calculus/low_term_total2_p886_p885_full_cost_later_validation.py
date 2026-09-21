#!/usr/bin/env python3
"""P886 disjoint-later validation of P885 with full public enumeration cost."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p880_public_slice_motif_fresh_source_validation as p880
import low_term_total2_p881_public_slice_motif_rank_descent_audit as p881
import low_term_total2_p882_public_post_motif_pairing_gate as p882
import low_term_total2_p883_p882_gate_no_retraining_replication as p883
import low_term_total2_p885_p882_rank_companion_gate as p885


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p886_p885_full_cost_later_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p886_p885_full_cost_later_validation_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P882_SOURCE = STATE_DIR / "low_term_total2_p882_public_post_motif_pairing_gate_probe.json"
DEFAULT_P885_SOURCE = STATE_DIR / "low_term_total2_p885_p882_rank_companion_gate_probe.json"
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_632_639_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_640_647_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_648_655_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_656_663_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_664_671_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p886_p885_full_cost_later_validation.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def int_value(value: Any, default: int = 0) -> int:
    return p882.int_value(value, default)


def rows_from_results(source_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for result in source_results
        if not result.get("error")
        for row in result.get("recovered_rows") or []
        if not row.get("context_missing")
    ]


def source_cost_summary(surface_costs: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = [float(item["full_candidate_ops_over_rho"]) for item in surface_costs if item.get("full_candidate_ops_over_rho") is not None]
    total_full_ops = sum(int_value(item.get("full_candidate_ops")) for item in surface_costs)
    total_rho = sum(int_value(item.get("generic_rho_steps")) for item in surface_costs)
    return {
        "candidate_count_sum": sum(int_value(item.get("candidate_count")) for item in surface_costs),
        "exact_motif_candidate_count_sum": sum(int_value(item.get("exact_motif_candidate_count")) for item in surface_costs),
        "full_candidate_ops_over_sum_rho": ratio(total_full_ops, total_rho),
        "full_candidate_ops_sum": total_full_ops,
        "full_candidate_ops_over_rho_max": round(max(ratios), 8) if ratios else None,
        "full_candidate_ops_over_rho_mean": round(mean(ratios), 8) if ratios else None,
        "full_candidate_ops_over_rho_min": round(min(ratios), 8) if ratios else None,
        "rho_sum": total_rho,
        "surface_count": len(surface_costs),
    }


def aggregate_full_cost(source_reports: list[dict[str, Any]], verified_contexts: list[dict[str, Any]]) -> dict[str, Any]:
    surface_costs = [
        item
        for report in source_reports
        for item in report.get("surface_costs") or []
    ]
    summary = source_cost_summary(surface_costs)
    best_verified_rho = None
    if verified_contexts:
        best_context = min(
            verified_contexts,
            key=lambda group: float(group.get("motif_ops_over_rho") if group.get("motif_ops_over_rho") is not None else 10**9),
        )
        rho = ratio(int_value(best_context.get("motif_ops")), float(best_context.get("motif_ops_over_rho") or 0.0))
        best_verified_rho = int(round(rho)) if rho is not None else None
    summary["full_candidate_ops_over_best_verified_context_rho"] = ratio(summary["full_candidate_ops_sum"], best_verified_rho)
    summary["best_verified_context_rho_estimate"] = best_verified_rho
    return summary


def evaluate_source_with_full_cost(
    ps: Any,
    source_path: Path,
    motif_set: dict[str, Any],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[str, Any]:
    ps_args = p842.public_slice_args(ps)
    ps_args.signature_source = source_path
    ps_args.max_cases = int(max_cases_per_source)
    ps_args.max_factor_degree = int(max_factor_degree)
    print(f"p886 materializing {source_path} max_cases={ps_args.max_cases}", flush=True)
    positive_cases = p881.source_positive_cases(source_path, int(max_cases_per_source))
    try:
        surface_records, case_results = p842.materialize_surface_records(ps, ps_args)
        surface_contexts = p881.surface_contexts_for_source(ps, ps_args, positive_cases)
        records_by_id = {
            str(record["surface_id"]): record
            for record in surface_records
            if isinstance(record, dict) and record.get("surface_id")
        }
        surface_ids = sorted(
            records_by_id,
            key=lambda surface_id: (
                p842.transfer_index(records_by_id[surface_id]),
                str(records_by_id[surface_id].get("target")),
                surface_id,
            ),
        )
        rows = []
        surface_costs = []
        direct_scan = ps.cross_surface_probe.direct_witness_probe
        for surface_id in surface_ids:
            record = records_by_id[surface_id]
            candidates = ps.build_public_candidates(record, int(max_factor_degree))
            all_selection = p842.evaluate_chosen(ps, record, candidates, "all_public_candidates")
            chosen = [candidate for candidate in candidates if p842.candidate_matches(candidate, motif_set)]
            selection = p842.evaluate_chosen(ps, record, chosen, str(motif_set["name"]))
            cost_inputs = record.get("cost_inputs") or {}
            rho = int_value(cost_inputs.get("generic_rho_steps") or (record.get("built") or {}).get("generic_rho_steps"))
            surface_costs.append(
                {
                    "candidate_count": len(candidates),
                    "exact_motif_candidate_count": len(chosen),
                    "full_candidate_ops": int_value(all_selection.get("public_slice_motif_ops")),
                    "full_candidate_ops_over_rho": all_selection.get("public_slice_motif_ops_over_rho"),
                    "generic_rho_steps": rho,
                    "row_key": record.get("row_key"),
                    "surface_id": surface_id,
                    "target": record.get("target"),
                    "transfer_index": p842.transfer_index(record),
                }
            )
            if not p881.recovered_selection(selection):
                continue
            pairs = p881.selected_pairs(chosen)
            leaf_indices = sorted({leaf for leaf, _root in pairs})
            surface_context = surface_contexts.get(surface_id)
            if not surface_context:
                rows.append(
                    {
                        "context_missing": True,
                        "leaf_indices": leaf_indices,
                        "row_key": record.get("row_key"),
                        "selection": selection,
                        "surface_id": surface_id,
                        "target": record.get("target"),
                        "transfer_index": p842.transfer_index(record),
                    }
                )
                continue
            scan = direct_scan.scan_selected(
                surface_context["verifier"],
                surface_context["built"],
                surface_context["components"],
                set(leaf_indices),
                surface_context["local_args"],
            )
            built = surface_context["built"]
            rows.append(
                {
                    "case": surface_context["case"],
                    "context_key": list(p881.context_key(surface_context)),
                    "context_missing": False,
                    "direct_ops": int_value(scan.get("preassociation_filter_ops")),
                    "direct_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
                    "event_summaries": scan.get("event_summaries") or [],
                    "forms": [p881.compact_form(event, str(record.get("row_key"))) for event in scan.get("relation_events") or []],
                    "generic_rho_steps": int_value(built.get("generic_rho_steps")),
                    "leaf_indices": leaf_indices,
                    "motif_ops": int_value(selection.get("public_slice_motif_ops")),
                    "motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
                    "rank": int_value(scan.get("rank")),
                    "relation_count": int_value(scan.get("relation_count")),
                    "row_key": record.get("row_key"),
                    "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                    "selection": selection,
                    "surface_id": surface_id,
                    "target": record.get("target"),
                    "transfer_index": p842.transfer_index(record),
                    "_built": built,
                    "_scan": scan,
                    "_verifier": surface_context["verifier"],
                }
            )
        return {
            "case_result_count": len(case_results or []),
            "cost_summary": source_cost_summary(surface_costs),
            "error": None,
            "positive_case_count": len(positive_cases),
            "recovered_rows": rows,
            "source": p880.source_summary(source_path),
            "surface_costs": surface_costs,
            "surface_count": len(surface_ids),
        }
    except Exception as exc:  # noqa: BLE001 - experiment evidence.
        return {
            "case_result_count": 0,
            "cost_summary": source_cost_summary([]),
            "error": f"{type(exc).__name__}: {exc}",
            "error_traceback": [],
            "positive_case_count": len(positive_cases),
            "recovered_rows": [],
            "source": p880.source_summary(source_path),
            "surface_costs": [],
            "surface_count": 0,
        }


def gate_report(ps: Any, source_results: list[dict[str, Any]], gate: dict[str, Any]) -> dict[str, Any]:
    gated_results = p882.filter_source_results(source_results, gate)
    gated_contexts = p881.aggregate_contexts(ps, gated_results)
    gated_summary = p881.aggregate_metrics(gated_results, gated_contexts)
    verified_contexts = [group for group in gated_contexts if group.get("target_context_public_key_verified")]
    return {
        "context_groups": gated_contexts,
        "full_cost_summary": aggregate_full_cost(gated_results, verified_contexts),
        "gate": gate,
        "row_summary": p882.summarize_gate_rows(rows_from_results(gated_results)),
        "source_results": p881.strip_internal_source_results(gated_results),
        "summary": gated_summary,
    }


def baseline_report(ps: Any, source_results: list[dict[str, Any]]) -> dict[str, Any]:
    contexts = p881.aggregate_contexts(ps, source_results)
    verified_contexts = [group for group in contexts if group.get("target_context_public_key_verified")]
    return {
        "context_groups": contexts,
        "full_cost_summary": aggregate_full_cost(source_results, verified_contexts),
        "source_results": p881.strip_internal_source_results(source_results),
        "summary": p881.aggregate_metrics(source_results, contexts),
    }


def determine_claim(p885_report: dict[str, Any]) -> str:
    summary = p885_report["summary"]
    full_cost = p885_report["full_cost_summary"]
    if int_value(summary.get("motif_below_rho_verified_context_count")) > 0:
        if (full_cost.get("full_candidate_ops_over_sum_rho") is not None) and float(full_cost["full_candidate_ops_over_sum_rho"]) < 1.0:
            return "P886_P885_GATE_CLOSES_LATER_CONTEXT_BELOW_RHO_WITH_FULL_ENUMERATION"
        return "P886_P885_GATE_CLOSES_LATER_CONTEXT_BELOW_SELECTED_COST_ONLY"
    if int_value(summary.get("target_context_verified_count")) > 0:
        return "P886_P885_GATE_CLOSES_LATER_CONTEXT_ABOVE_SELECTED_MOTIF_COST"
    if int_value(summary.get("matrix_rank_sum")) > 0:
        return "P886_P885_GATE_SELECTS_LATER_RANK_WITHOUT_CLOSURE"
    if int_value(summary.get("recovered_row_count")) > 0:
        return "P886_P885_GATE_SELECTS_LATER_ROWS_WITHOUT_RANK"
    return "NEGATIVE_RESULT_P886_P885_GATE_SELECTS_NO_LATER_ROWS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p842_payload = load_json(args.p842_source)
    p882_payload = load_json(args.p882_source)
    p885_payload = load_json(args.p885_source) if args.p885_source.exists() else None
    motif_set = p880.normalize_motif_set(p842_payload["selected_policy"]["motif_set"])
    ps = p842.load_module("ecdlp_public_slice_for_p886", p842.PUBLIC_SLICE_SCRIPT)
    sources = [Path(path) for path in (args.validation_source or DEFAULT_VALIDATION_SOURCES)]
    sources = sources[: int(args.max_validation_sources)]
    source_results = [
        evaluate_source_with_full_cost(
            ps,
            source,
            motif_set,
            int(args.max_cases_per_source),
            int(args.max_factor_degree),
        )
        for source in sources
    ]
    exact_p882_gate = p882_payload["selected_gate"]
    rank_companion_gate = p885.p885_gate()
    baseline = baseline_report(ps, source_results)
    exact_report = gate_report(ps, source_results, exact_p882_gate)
    p885_report = gate_report(ps, source_results, rank_companion_gate)
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p882_source": str(args.p882_source),
            "p885_source": str(args.p885_source),
            "script": str(Path(__file__)),
        },
        "baseline_all_recovered": baseline,
        "claim_status": determine_claim(p885_report),
        "created_at": now_iso(),
        "gate_derivation": {
            "exact_p882_gate": {
                "name": exact_p882_gate.get("name"),
                "predicates": exact_p882_gate.get("predicates") or [],
                "training_stats": exact_p882_gate.get("training_stats"),
            },
            "p885_claim_status": (p885_payload or {}).get("claim_status"),
            "p885_rank_companion_gate": rank_companion_gate,
        },
        "gate_reports": {
            "p882_exact": exact_report,
            "p885_rank_companion_m38": p885_report,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "NO-RETRAINING: P885 gate predicates are frozen before these sources are scored.",
            "PUBLIC-FEATURE BOUNDARY: gate predicates use only public row/motif fields.",
            "FULL-COST BOUNDARY: full enumeration is a conservative all-public-candidate scan over materialized positive-case surfaces.",
            "POST-SELECTION VERIFIER AUDIT: verifier rank/closure is measured after selection.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p886_p885_full_cost_later_validation",
        "parameters": {
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "validation_source_count": len(sources),
        },
        "red_team_handoff": {
            "assumptions": [
                "All-public-candidate scan cost is a conservative proxy for full public source enumeration.",
                "The frozen P885 gate has no access to later validation labels.",
                "Selected-row motif cost and full source-enumeration cost answer different questions and must both be reported.",
            ],
            "failure_modes": [
                "Selected-row below-rho closures may disappear when full source enumeration is charged.",
                "The signal may remain target-local to 22050.cf1@11731.",
                "Materialized positive-case surfaces are still a restricted harness, not deployed-scale source generation.",
            ],
            "next_concrete_action": (
                "If P886 is selected-cost positive but full-cost negative, search for a public prefilter that reduces candidate enumeration; "
                "if full-cost positive, run a wider disjoint validation and begin matrix/target-descent cost integration."
            ),
        },
        "schema": SCHEMA,
        "validation_sources": p883.source_positive_counts(sources),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p882-source", type=Path, default=DEFAULT_P882_SOURCE)
    parser.add_argument("--p885-source", type=Path, default=DEFAULT_P885_SOURCE)
    parser.add_argument("--validation-source", type=Path, action="append")
    parser.add_argument("--max-validation-sources", type=int, default=len(DEFAULT_VALIDATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=0)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "baseline_summary": payload["baseline_all_recovered"]["summary"],
                "claim_status": payload["claim_status"],
                "full_cost": payload["gate_reports"]["p885_rank_companion_m38"]["full_cost_summary"],
                "p882_exact_summary": payload["gate_reports"]["p882_exact"]["summary"],
                "p885_summary": payload["gate_reports"]["p885_rank_companion_m38"]["summary"],
                "parameters": payload["parameters"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
