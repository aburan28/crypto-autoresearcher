#!/usr/bin/env python3
"""P701 completion-form reuse audit.

P700 isolated a below-rho P659 rank+1 endpoint stage whose cheapest full-rank
completion remains above rho and unverified under independent leaf-scan
accounting.  This audit reruns combined multi-leaf scans per row to test
whether the completion can reuse row/scout work rather than paying a full
independent leaf charge.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p698_minimal_endpoint_subset_cost_audit as p698
import low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit as p699
import low_term_total2_p700_two_stage_endpoint_cost_decomposition as p700


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p659_salt204_right206_anchor11_right208_source_22343_22355_probe.json"
DEFAULT_PRODUCT = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p659_order9887_salt204_right206_anchor11_right208_22343_22355_density_gate_probe.json"
DEFAULT_P698 = p699.DEFAULT_P698
DEFAULT_OUT = STATE_DIR / "low_term_total2_p701_completion_form_reuse_audit_probe.json"


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


def form_key(record: dict[str, Any]) -> tuple[tuple[int, ...], int]:
    form = record.get("form") or {}
    return tuple(int_value(value) for value in form.get("coeffs") or []), int_value(form.get("rhs"))


def records_by_index(records: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {int_value(record.get("_endpoint_form_index")): record for record in records}


def stage_selector_records(
    records: list[dict[str, Any]],
    training_records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    selectors = p699.make_selectors(training_records)
    selector = next(item for item in selectors if item["name"] == "coeff_support")
    return [record for record in records if selector["match"](record)]


def surface_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        certificate=args.certificate,
        max_cases=args.max_cases,
        max_endpoint_leaves=args.max_endpoint_leaves,
        product=str(args.product),
        sample_limit=args.sample_limit,
        source=str(args.source),
        target=args.target,
    )


def collect_records_and_contexts(
    args: argparse.Namespace,
    priority_columns: set[int],
) -> tuple[Any, dict[str, dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    local_args = surface_args(args)
    verifier, row_contexts, context_cache_entry_count, missing_source_case_count = p697.build_row_contexts(local_args)
    mutation = p697.collect_mutation_records(
        verifier,
        row_contexts,
        priority_columns,
        int_value(args.max_endpoint_leaves),
    )
    records = p697.unique_records(mutation["endpoint_coeff_records"])
    for index, record in enumerate(records):
        record["_endpoint_form_index"] = index
        record["_public_features"] = p699.record_features(record)
    context_by_row = {str(context["row_key"]): context for context in row_contexts.values()}
    meta = {
        "context_cache_entry_count": context_cache_entry_count,
        "endpoint_coeff_unique_form_count": len(records),
        "endpoint_leaf_count": mutation["endpoint_leaf_count"],
        "endpoint_leaf_hit_root_count": mutation["endpoint_leaf_hit_root_count"],
        "missing_source_case_count": missing_source_case_count,
        "priority_coeff_event_counts": {
            str(column): mutation["priority_coeff_counts"][column] for column in sorted(priority_columns)
        },
        "priority_leaf_counts": {
            str(column): mutation["priority_leaf_counts"][column] for column in sorted(priority_columns)
        },
        "scanned_endpoint_leaf_count": mutation["scanned_endpoint_leaf_count"],
    }
    return verifier, context_by_row, meta, records


def row_union_replay(
    verifier: Any,
    context_by_row: dict[str, dict[str, Any]],
    chosen_records: list[dict[str, Any]],
    priority_columns: set[int],
) -> dict[str, Any]:
    leaves_by_row: dict[str, set[int]] = {}
    target_keys = {form_key(record) for record in chosen_records}
    for record in chosen_records:
        leaves_by_row.setdefault(str(record.get("row_key")), set()).add(int_value(record.get("leaf_index")))
    replay_records: list[dict[str, Any]] = []
    row_replays = []
    for row_key, leaves in sorted(leaves_by_row.items()):
        context = context_by_row.get(row_key)
        if not context:
            continue
        scan = p697.direct_export.direct_witness_probe.scan_selected(
            verifier,
            context["built"],
            context["components"],
            set(leaves),
            context["local_args"],
        )
        row_replays.append(
            {
                "leaf_indices": sorted(leaves),
                "preassociation_filter_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
                "relation_count": int_value(scan.get("relation_count")),
                "row_key": row_key,
                "row_public_key_verified": bool(scan.get("row_public_key_verified")),
                "selected_hit_roots": int_value(scan.get("selected_hit_roots")),
            }
        )
        for event in scan.get("relation_events") or []:
            leaf_index = int_value(event.get("leaf_index"))
            support = p697.p696.leaf_support(context, leaf_index)
            record = p697.relation_record(
                context,
                leaf_index,
                support,
                scan,
                event,
                priority_columns,
            )
            replay_records.append(record)
    unique_records = p697.unique_records(replay_records)
    replay_keys = {form_key(record) for record in unique_records}
    return {
        "missing_target_form_count": len(target_keys - replay_keys),
        "replayed_records": unique_records,
        "row_replay_charge_over_rho": round(
            sum(float_value(row.get("preassociation_filter_ops_over_rho")) for row in row_replays),
            8,
        ),
        "row_replays": row_replays,
        "target_form_count": len(target_keys),
        "target_forms_preserved": target_keys <= replay_keys,
    }


def evaluate_records_with_external_charge(
    name: str,
    records: list[dict[str, Any]],
    charge_over_rho: float,
    verifier: Any,
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any]:
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
            "external_charge_over_rho": round(charge_over_rho, 8),
            "record_count": len(records),
            "union_derived_secret": union.get("union_derived_secret"),
            "union_public_key_verified": bool(union.get("union_public_key_verified")),
            "union_rank": int_value(union.get("union_rank")),
            "union_relation_count": int_value(union.get("union_relation_count")),
        }
    )
    return evaluation


def compact_eval(evaluation: dict[str, Any]) -> dict[str, Any]:
    return {
        "charge_over_rho": evaluation.get("external_charge_over_rho")
        or evaluation.get("selected_unique_leaf_scan_ops_over_rho"),
        "factor_variables_derivable_gain": int_value(evaluation.get("factor_variables_derivable_gain")),
        "missing_columns_after": evaluation.get("missing_columns_after") or [],
        "new_missing_touch_relation_count": int_value(evaluation.get("new_missing_touch_relation_count")),
        "newly_derivable_priority_columns": evaluation.get("newly_derivable_priority_columns") or [],
        "rank_after": int_value(evaluation.get("rank_after")),
        "rank_gain": int_value(evaluation.get("rank_gain")),
        "record_count": int_value(evaluation.get("record_count") or evaluation.get("selected_form_count")),
        "union_derived_secret": evaluation.get("union_derived_secret"),
        "union_public_key_verified": bool(evaluation.get("union_public_key_verified")),
        "union_rank": int_value(evaluation.get("union_rank")),
        "unique_factor_relation_gain": int_value(evaluation.get("unique_factor_relation_gain")),
    }


def candidate_report(
    record: dict[str, Any],
    stage_records: list[dict[str, Any]],
    verifier: Any,
    context_by_row: dict[str, dict[str, Any]],
    target: str,
    base: list[dict[str, Any]],
    base_state: dict[str, Any],
    priority_columns: set[int],
    sample_limit: int,
) -> dict[str, Any] | None:
    combined_records = stage_records + [record]
    independent = p700.evaluate_record_set(
        "p701_independent_stage_plus_completion",
        combined_records,
        verifier,
        target,
        base,
        base_state,
        priority_columns,
        sample_limit,
    )
    if int_value(independent.get("rank_after")) < int_value(base_state["factor_count"]):
        return None
    replay = row_union_replay(verifier, context_by_row, combined_records, priority_columns)
    row_union_eval = evaluate_records_with_external_charge(
        "p701_row_union_replay",
        replay["replayed_records"],
        float_value(replay["row_replay_charge_over_rho"]),
        verifier,
        target,
        base,
        base_state,
        priority_columns,
        sample_limit,
    )
    stage_cost = p698.scan_cost(stage_records)
    independent_cost = float_value(independent.get("selected_unique_leaf_scan_ops_over_rho"))
    row_union_cost = float_value(replay.get("row_replay_charge_over_rho"))
    return {
        "completion_form": p697.compact_event_sample(record),
        "completion_form_index": int_value(record.get("_endpoint_form_index")),
        "independent": p700.compact_eval(independent),
        "independent_increment_over_stage": round(
            independent_cost - float_value(stage_cost.get("unique_leaf_scan_ops_over_rho")),
            8,
        ),
        "row_overlap_with_stage": [
            p697.compact_event_sample(stage)
            for stage in stage_records
            if str(stage.get("row_key")) == str(record.get("row_key"))
        ],
        "row_union": compact_eval(row_union_eval),
        "row_union_increment_over_stage": round(
            row_union_cost - float_value(stage_cost.get("unique_leaf_scan_ops_over_rho")),
            8,
        ),
        "row_union_replay": {
            "missing_target_form_count": replay["missing_target_form_count"],
            "row_replays": replay["row_replays"],
            "target_form_count": replay["target_form_count"],
            "target_forms_preserved": replay["target_forms_preserved"],
        },
        "row_union_savings_over_independent": round(independent_cost - row_union_cost, 8),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["row_union_verified_below_rho_count"]:
        return "P701_COMPLETION_REUSE_BELOW_RHO_VERIFIED"
    if summary["row_union_full_rank_below_rho_count"]:
        return "P701_COMPLETION_REUSE_BELOW_RHO_UNVERIFIED"
    if summary["row_union_saving_candidate_count"]:
        return "P701_COMPLETION_REUSE_SAVES_COST_ABOVE_RHO"
    return "NEGATIVE_RESULT_P701_NO_COMPLETION_REUSE_COST_SAVING"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    verifier, context_by_row, surface_meta, records = collect_records_and_contexts(args, priority_columns)
    p698_payload = p699.load_json(Path(args.p698))

    calibration_args = SimpleNamespace(
        certificate=args.certificate,
        max_cases=args.max_cases,
        max_endpoint_leaves=args.max_endpoint_leaves,
        product=str(p699.DEFAULT_SURFACES[0][2]),
        sample_limit=args.sample_limit,
        source=str(p699.DEFAULT_SURFACES[0][1]),
        target=args.target,
    )
    _cal_verifier, _cal_meta, calibration_records = p699.collect_surface_records(
        calibration_args,
        Path(p699.DEFAULT_SURFACES[0][1]),
        Path(p699.DEFAULT_SURFACES[0][2]),
        priority_columns,
    )
    training_records = p699.train_records_from_p698(p698_payload, calibration_records)
    stage_records = stage_selector_records(records, training_records)
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    stage_eval = p700.evaluate_record_set(
        "p701_p659_coeff_support_stage",
        stage_records,
        verifier,
        args.target,
        base,
        base_state,
        priority_columns,
        int_value(args.sample_limit, 12),
    )
    stage_indices = {int_value(record.get("_endpoint_form_index")) for record in stage_records}
    candidate_reports = []
    for record in records:
        if int_value(record.get("_endpoint_form_index")) in stage_indices:
            continue
        report = candidate_report(
            record,
            stage_records,
            verifier,
            context_by_row,
            args.target,
            base,
            base_state,
            priority_columns,
            int_value(args.sample_limit, 12),
        )
        if report:
            candidate_reports.append(report)
    candidate_reports.sort(
        key=lambda report: (
            not bool((report.get("row_union") or {}).get("union_public_key_verified")),
            float_value((report.get("row_union") or {}).get("charge_over_rho"), 999.0),
            float_value(report.get("row_union_increment_over_stage"), 999.0),
            int_value(report.get("completion_form_index")),
        )
    )
    row_union_below_rho = [
        report for report in candidate_reports if float_value((report.get("row_union") or {}).get("charge_over_rho"), 999.0) <= 1.0
    ]
    row_union_verified_below_rho = [
        report
        for report in row_union_below_rho
        if bool((report.get("row_union") or {}).get("union_public_key_verified"))
    ]
    row_union_saving = [
        report for report in candidate_reports if float_value(report.get("row_union_savings_over_independent")) > 0.0
    ]
    best = candidate_reports[0] if candidate_reports else None
    summary = {
        "base_rank": int_value(base_state["rank"]),
        "base_missing_columns": base_state["missing_columns"],
        "candidate_completion_count": len(candidate_reports),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "row_union_full_rank_below_rho_count": len(row_union_below_rho),
        "row_union_saving_candidate_count": len(row_union_saving),
        "row_union_verified_below_rho_count": len(row_union_verified_below_rho),
        "stage_form_indices": [int_value(record.get("_endpoint_form_index")) for record in stage_records],
        "stage_rank_gain": int_value(stage_eval.get("rank_gain")),
        "stage_unique_leaf_scan_ops_over_rho": stage_eval.get("selected_unique_leaf_scan_ops_over_rho"),
        "surface_endpoint_coeff_unique_form_count": len(records),
    }
    if best:
        summary.update(
            {
                "best_completion_form_index": best["completion_form_index"],
                "best_independent_charge_over_rho": (best.get("independent") or {}).get("selected_unique_leaf_scan_ops_over_rho"),
                "best_row_union_charge_over_rho": (best.get("row_union") or {}).get("charge_over_rho"),
                "best_row_union_increment_over_stage": best.get("row_union_increment_over_stage"),
                "best_row_union_savings_over_independent": best.get("row_union_savings_over_independent"),
                "best_row_union_verified": bool((best.get("row_union") or {}).get("union_public_key_verified")),
            }
        )
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p698": str(Path(args.p698)),
            "product": str(Path(args.product)),
            "source": str(Path(args.source)),
        },
        "candidate_reports": candidate_reports,
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: reuse is tested only by actual combined row-level multi-leaf replay on the reconstructed P659 surface.",
            "A row-union charge is accepted only when the combined replay emits relation forms and rank is recomputed from emitted public forms.",
            "A cost saving without aggregate verification is a generator-routing signal, not a faster-than-rho individual-log result.",
        ],
        "method": "p701_completion_form_reuse_audit",
        "parameters": {
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p701_completion_form_reuse_audit.v1",
        "stage_evaluation": p700.compact_eval(stage_eval),
        "stage_form_samples": [p697.compact_event_sample(record) for record in stage_records],
        "summary": summary,
        "surface_meta": surface_meta,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--p698", default=str(DEFAULT_P698))
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    args = parser.parse_args()
    args.source = Path(args.source)
    args.product = Path(args.product)
    return args


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_candidate": payload["candidate_reports"][:1]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
