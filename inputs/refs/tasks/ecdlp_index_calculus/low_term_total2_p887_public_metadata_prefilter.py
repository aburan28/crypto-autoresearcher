#!/usr/bin/env python3
"""P887 public metadata prefilter for the P886 all-candidate cost bottleneck."""

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
import low_term_total2_p886_p885_full_cost_later_validation as p886


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p887_public_metadata_prefilter.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p887_public_metadata_prefilter_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P886_SOURCE = STATE_DIR / "low_term_total2_p886_p885_full_cost_later_validation_probe.json"
DEFAULT_CALIBRATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_632_639_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_640_647_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_648_655_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_656_663_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_664_671_summary.json",
]
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_672_679_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_680_687_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_688_695_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_696_703_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_704_711_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p887_public_metadata_prefilter.v1"
TARGET = "22050.cf1@11731"
FIXED_VALUE = 10907


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


def policy_specs() -> list[dict[str, Any]]:
    return [
        {"name": "target_fixed10907_m32", "monomials_lte": 32},
        {"name": "target_fixed10907_m38", "monomials_lte": 38},
        {"name": "target_fixed10907_m44", "monomials_lte": 44},
    ]


def candidate_matches_policy(record: dict[str, Any], candidate: dict[str, Any], policy: dict[str, Any]) -> bool:
    if record.get("target") != TARGET:
        return False
    return (
        candidate.get("axis") == "b"
        and int_value(candidate.get("fixed_value")) == FIXED_VALUE
        and int_value(candidate.get("selected_factor_monomials")) <= int_value(policy.get("monomials_lte"))
    )


def surface_cost_summary(surface_costs: list[dict[str, Any]]) -> dict[str, Any]:
    total_prefilter_ops = sum(int_value(item.get("prefilter_total_ops")) for item in surface_costs)
    total_expensive_ops = sum(int_value(item.get("expensive_selected_ops")) for item in surface_costs)
    total_full_ops = sum(int_value(item.get("all_candidate_ops")) for item in surface_costs)
    total_rho = sum(int_value(item.get("generic_rho_steps")) for item in surface_costs)
    ratios = [
        float(item["prefilter_total_ops_over_rho"])
        for item in surface_costs
        if item.get("prefilter_total_ops_over_rho") is not None
    ]
    return {
        "all_candidate_ops_over_sum_rho": ratio(total_full_ops, total_rho),
        "all_candidate_ops_sum": total_full_ops,
        "candidate_count_sum": sum(int_value(item.get("candidate_count")) for item in surface_costs),
        "candidate_screen_ops_sum": sum(int_value(item.get("candidate_screen_ops")) for item in surface_costs),
        "expensive_selected_ops_over_sum_rho": ratio(total_expensive_ops, total_rho),
        "expensive_selected_ops_sum": total_expensive_ops,
        "filtered_candidate_count_sum": sum(int_value(item.get("filtered_candidate_count")) for item in surface_costs),
        "prefilter_total_ops_over_rho_max": round(max(ratios), 8) if ratios else None,
        "prefilter_total_ops_over_rho_mean": round(mean(ratios), 8) if ratios else None,
        "prefilter_total_ops_over_rho_min": round(min(ratios), 8) if ratios else None,
        "prefilter_total_ops_over_sum_rho": ratio(total_prefilter_ops, total_rho),
        "prefilter_total_ops_sum": total_prefilter_ops,
        "rho_sum": total_rho,
        "surface_count": len(surface_costs),
        "surface_screen_ops_sum": sum(int_value(item.get("surface_screen_ops")) for item in surface_costs),
        "target_surface_count": len([item for item in surface_costs if item.get("target") == TARGET]),
    }


def strip_internal(source_results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean = []
    for result in source_results:
        row_clean = []
        for row in result.get("recovered_rows") or []:
            row_clean.append({key: value for key, value in row.items() if not key.startswith("_")})
        clean.append({**result, "recovered_rows": row_clean})
    return clean


def evaluate_source(
    ps: Any,
    source_path: Path,
    policies: list[dict[str, Any]],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[str, Any]:
    ps_args = p842.public_slice_args(ps)
    ps_args.signature_source = source_path
    ps_args.max_cases = int(max_cases_per_source)
    ps_args.max_factor_degree = int(max_factor_degree)
    print(f"p887 materializing {source_path} max_cases={ps_args.max_cases}", flush=True)
    positive_cases = p881.source_positive_cases(source_path, int(max_cases_per_source))
    policy_results = {
        policy["name"]: {
            "recovered_rows": [],
            "surface_costs": [],
        }
        for policy in policies
    }
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
        direct_scan = ps.cross_surface_probe.direct_witness_probe
        for surface_id in surface_ids:
            record = records_by_id[surface_id]
            candidates = ps.build_public_candidates(record, int(max_factor_degree))
            all_selection = p842.evaluate_chosen(ps, record, candidates, "all_public_candidates")
            cost_inputs = record.get("cost_inputs") or {}
            rho = int_value(cost_inputs.get("generic_rho_steps") or (record.get("built") or {}).get("generic_rho_steps"))
            target_surface = record.get("target") == TARGET
            for policy in policies:
                policy_name = str(policy["name"])
                filtered = [candidate for candidate in candidates if candidate_matches_policy(record, candidate, policy)]
                if target_surface and filtered:
                    selection = p842.evaluate_chosen(ps, record, filtered, policy_name)
                    expensive_ops = int_value(selection.get("public_slice_motif_ops"))
                else:
                    selection = {
                        "chosen_count": 0,
                        "chosen_slices": [],
                        "missing_selected_root_pairs": [],
                        "motif_policy": policy_name,
                        "preserves_selected_root_pairs": False,
                        "public_slice_motif_beats_rho": False,
                        "public_slice_motif_ops": 0,
                        "public_slice_motif_ops_over_rho": None,
                        "selected_root_pair_count": 0,
                    }
                    expensive_ops = 0
                surface_screen_ops = 1
                candidate_screen_ops = len(candidates) if target_surface else 0
                prefilter_total_ops = surface_screen_ops + candidate_screen_ops + expensive_ops
                policy_results[policy_name]["surface_costs"].append(
                    {
                        "all_candidate_ops": int_value(all_selection.get("public_slice_motif_ops")),
                        "all_candidate_ops_over_rho": all_selection.get("public_slice_motif_ops_over_rho"),
                        "candidate_count": len(candidates),
                        "candidate_screen_ops": candidate_screen_ops,
                        "expensive_selected_ops": expensive_ops,
                        "expensive_selected_ops_over_rho": ratio(expensive_ops, rho),
                        "filtered_candidate_count": len(filtered),
                        "generic_rho_steps": rho,
                        "prefilter_total_ops": prefilter_total_ops,
                        "prefilter_total_ops_over_rho": ratio(prefilter_total_ops, rho),
                        "row_key": record.get("row_key"),
                        "surface_id": surface_id,
                        "surface_screen_ops": surface_screen_ops,
                        "target": record.get("target"),
                        "transfer_index": p842.transfer_index(record),
                    }
                )
                if not p881.recovered_selection(selection):
                    continue
                pairs = p881.selected_pairs(filtered)
                leaf_indices = sorted({leaf for leaf, _root in pairs})
                surface_context = surface_contexts.get(surface_id)
                if not surface_context:
                    policy_results[policy_name]["recovered_rows"].append(
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
                policy_results[policy_name]["recovered_rows"].append(
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
        out = {
            "case_result_count": len(case_results or []),
            "error": None,
            "positive_case_count": len(positive_cases),
            "source": p880.source_summary(source_path),
            "surface_count": len(surface_ids),
        }
        for policy in policies:
            policy_name = str(policy["name"])
            out[policy_name] = {
                "cost_summary": surface_cost_summary(policy_results[policy_name]["surface_costs"]),
                "recovered_rows": policy_results[policy_name]["recovered_rows"],
                "surface_costs": policy_results[policy_name]["surface_costs"],
            }
        return out
    except Exception as exc:  # noqa: BLE001 - experiment evidence.
        out = {
            "case_result_count": 0,
            "error": f"{type(exc).__name__}: {exc}",
            "positive_case_count": len(positive_cases),
            "source": p880.source_summary(source_path),
            "surface_count": 0,
        }
        for policy in policies:
            out[str(policy["name"])] = {
                "cost_summary": surface_cost_summary([]),
                "recovered_rows": [],
                "surface_costs": [],
            }
        return out


def source_results_for_policy(source_reports: list[dict[str, Any]], policy_name: str) -> list[dict[str, Any]]:
    return [
        {
            "case_result_count": report.get("case_result_count"),
            "cost_summary": report[policy_name]["cost_summary"],
            "error": report.get("error"),
            "positive_case_count": report.get("positive_case_count"),
            "recovered_rows": report[policy_name]["recovered_rows"],
            "source": report.get("source"),
            "surface_costs": report[policy_name]["surface_costs"],
            "surface_count": report.get("surface_count"),
        }
        for report in source_reports
    ]


def aggregate_policy(ps: Any, source_reports: list[dict[str, Any]], policy_name: str) -> dict[str, Any]:
    source_results = source_results_for_policy(source_reports, policy_name)
    contexts = p881.aggregate_contexts(ps, source_results)
    summary = p881.aggregate_metrics(source_results, contexts)
    cost_summary = surface_cost_summary([
        item
        for result in source_results
        for item in result.get("surface_costs") or []
    ])
    return {
        "context_groups": contexts,
        "cost_summary": cost_summary,
        "source_results": strip_internal(source_results),
        "summary": summary,
    }


def best_policy_report(phase_report: dict[str, Any], policies: list[dict[str, Any]]) -> dict[str, Any] | None:
    reports = []
    for policy in policies:
        name = str(policy["name"])
        report = phase_report["policy_reports"][name]
        summary = report["summary"]
        cost = report["cost_summary"]
        reports.append(
            {
                "name": name,
                "motif_below_rho_verified_context_count": int_value(summary.get("motif_below_rho_verified_context_count")),
                "prefilter_total_ops_over_sum_rho": cost.get("prefilter_total_ops_over_sum_rho"),
                "target_context_verified_count": int_value(summary.get("target_context_verified_count")),
            }
        )
    reports.sort(
        key=lambda item: (
            item["motif_below_rho_verified_context_count"] > 0,
            item["target_context_verified_count"] > 0,
            -(float(item["prefilter_total_ops_over_sum_rho"]) if item["prefilter_total_ops_over_sum_rho"] is not None else 10**9),
        ),
        reverse=True,
    )
    return reports[0] if reports else None


def determine_claim(calibration: dict[str, Any], validation: dict[str, Any], policies: list[dict[str, Any]]) -> str:
    best_cal = best_policy_report(calibration, policies)
    best_val = best_policy_report(validation, policies)
    cal_good = bool(
        best_cal
        and best_cal["motif_below_rho_verified_context_count"] > 0
        and best_cal["prefilter_total_ops_over_sum_rho"] is not None
        and float(best_cal["prefilter_total_ops_over_sum_rho"]) < 1.0
    )
    val_good = bool(
        best_val
        and best_val["motif_below_rho_verified_context_count"] > 0
        and best_val["prefilter_total_ops_over_sum_rho"] is not None
        and float(best_val["prefilter_total_ops_over_sum_rho"]) < 1.0
    )
    if cal_good and val_good:
        return "P887_PUBLIC_METADATA_PREFILTER_TRANSFERS_BELOW_RHO_FULL_COST"
    if cal_good:
        return "P887_PUBLIC_METADATA_PREFILTER_RESCUES_P886_CALIBRATION_FULL_COST_ONLY"
    if best_cal and best_cal["motif_below_rho_verified_context_count"] > 0:
        return "P887_PUBLIC_METADATA_PREFILTER_PRESERVES_SELECTED_CLOSURE_ABOVE_FULL_COST"
    return "NEGATIVE_RESULT_P887_PUBLIC_METADATA_PREFILTER_DROPS_CLOSURE"


def evaluate_phase(
    ps: Any,
    sources: list[Path],
    policies: list[dict[str, Any]],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[str, Any]:
    source_reports = [
        evaluate_source(ps, source, policies, max_cases_per_source, max_factor_degree)
        for source in sources
    ]
    return {
        "policy_reports": {
            str(policy["name"]): aggregate_policy(ps, source_reports, str(policy["name"]))
            for policy in policies
        },
        "source_reports": [
            {
                "case_result_count": report.get("case_result_count"),
                "error": report.get("error"),
                "positive_case_count": report.get("positive_case_count"),
                "source": report.get("source"),
                "surface_count": report.get("surface_count"),
            }
            for report in source_reports
        ],
        "sources": p883.source_positive_counts(sources),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    ps = p842.load_module("ecdlp_public_slice_for_p887", p842.PUBLIC_SLICE_SCRIPT)
    policies = policy_specs()
    calibration_sources = [Path(path) for path in (args.calibration_source or DEFAULT_CALIBRATION_SOURCES)]
    validation_sources = [Path(path) for path in (args.validation_source or DEFAULT_VALIDATION_SOURCES)]
    calibration_sources = calibration_sources[: int(args.max_calibration_sources)]
    validation_sources = validation_sources[: int(args.max_validation_sources)]
    calibration = evaluate_phase(ps, calibration_sources, policies, int(args.max_cases_per_source), int(args.max_factor_degree))
    validation = evaluate_phase(ps, validation_sources, policies, int(args.max_cases_per_source), int(args.max_factor_degree))
    p886_payload = load_json(args.p886_source) if args.p886_source.exists() else {}
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p886_source": str(args.p886_source),
            "script": str(Path(__file__)),
        },
        "calibration": calibration,
        "claim_status": determine_claim(calibration, validation, policies),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "PREFILTER-COST: charges surface screening, candidate metadata screening, and expensive selected-candidate work.",
            "NO-LABEL-VALIDATION: validation sources after 672 are disjoint from the P886 calibration slice.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p887_public_metadata_prefilter",
        "p886_reference": {
            "claim_status": p886_payload.get("claim_status"),
            "full_cost_summary": ((p886_payload.get("gate_reports") or {}).get("p885_rank_companion_m38") or {}).get("full_cost_summary"),
        },
        "parameters": {
            "calibration_source_count": len(calibration_sources),
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "validation_source_count": len(validation_sources),
        },
        "policies": policies,
        "red_team_handoff": {
            "assumptions": [
                "Fixed-value and monomial metadata can be screened before expensive root/factor recovery.",
                "One operation per public candidate is a conservative metadata-screening charge.",
                "Preserving transfer-636 closure is a calibration test; later sources are required for transfer.",
            ],
            "failure_modes": [
                "The prefilter may be target-local to 22050.cf1@11731.",
                "The metadata-screening model may still undercount a real source generator.",
                "Validation may fail even if calibration cost falls below rho.",
            ],
            "next_concrete_action": (
                "If P887 only calibrates, search for a schedule/row-family prefilter that transfers to 672+; "
                "if it transfers, widen validation and integrate matrix/target-descent cost."
            ),
        },
        "schema": SCHEMA,
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json")
    parser.add_argument("--p886-source", type=Path, default=DEFAULT_P886_SOURCE)
    parser.add_argument("--calibration-source", type=Path, action="append")
    parser.add_argument("--validation-source", type=Path, action="append")
    parser.add_argument("--max-calibration-sources", type=int, default=len(DEFAULT_CALIBRATION_SOURCES))
    parser.add_argument("--max-validation-sources", type=int, default=len(DEFAULT_VALIDATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=0)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = {
        "calibration": {
            name: {
                "cost": report["cost_summary"],
                "summary": report["summary"],
            }
            for name, report in payload["calibration"]["policy_reports"].items()
        },
        "claim_status": payload["claim_status"],
        "parameters": payload["parameters"],
        "validation": {
            name: {
                "cost": report["cost_summary"],
                "summary": report["summary"],
            }
            for name, report in payload["validation"]["policy_reports"].items()
        },
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
