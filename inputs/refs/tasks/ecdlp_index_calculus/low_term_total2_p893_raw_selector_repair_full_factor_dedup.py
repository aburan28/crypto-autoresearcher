#!/usr/bin/env python3
"""P893 raw-selector repair audit for full-factor union dedup."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p882_public_post_motif_pairing_gate as p882
import low_term_total2_p891_union_level_factor_dedup_evaluator as p891


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p893_raw_selector_repair_full_factor_dedup.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p893_raw_selector_repair_full_factor_dedup_probe.json"
DEFAULT_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_752_759_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_760_767_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_768_775_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_776_783_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_784_791_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p893_raw_selector_repair_full_factor_dedup.v1"
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


def int_value(value: Any, default: int = 0) -> int:
    return p882.int_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p891.ratio(numerator, denominator)


def case_key(case: dict[str, Any]) -> tuple[Any, ...]:
    rows = tuple(
        (str(item.get("row_key")), tuple(int_value(index) for index in item.get("leaf_indices") or []))
        for item in case.get("row_leaf_keys") or []
    )
    return (
        str(case.get("source")),
        int_value(case.get("transfer_index")),
        str(case.get("target")),
        str(case.get("policy")),
        str(case.get("selector")),
        str(case.get("row_selector")),
        int_value(case.get("top_k")),
        rows,
    )


def wanted_cases(source_path: Path) -> list[dict[str, Any]]:
    payload = load_json(source_path)
    out = []
    seen: set[tuple[Any, ...]] = set()
    for case in payload.get("positive_cases") or []:
        if case.get("target") != TARGET:
            continue
        if not case.get("source_verified") or not case.get("public_key_verified"):
            continue
        if not case.get("row_leaf_keys"):
            continue
        key = case_key(case)
        if key in seen:
            continue
        seen.add(key)
        out.append({**case, "summary_path": str(source_path)})
    return out


def load_records_for_sources(
    ps: Any,
    sources: list[Path],
    max_cases_per_source: int,
    max_factor_degree: int,
) -> dict[tuple[int, str, str], dict[str, Any]]:
    records: dict[tuple[int, str, str], dict[str, Any]] = {}
    for source in sources:
        ps_args = p842.public_slice_args(ps)
        ps_args.signature_source = source
        ps_args.max_cases = int(max_cases_per_source)
        ps_args.max_factor_degree = int(max_factor_degree)
        surface_records, _case_results = p842.materialize_surface_records(ps, ps_args)
        for record in surface_records:
            if not isinstance(record, dict):
                continue
            key = (p842.transfer_index(record), str(record.get("target")), str(record.get("row_key")))
            records[key] = record
    return records


def record_rho(record: dict[str, Any]) -> int:
    cost_inputs = record.get("cost_inputs") or {}
    built = record.get("built") or {}
    return int_value(cost_inputs.get("generic_rho_steps") or built.get("generic_rho_steps"))


def evaluate_case(
    ps: Any,
    records_by_key: dict[tuple[int, str, str], dict[str, Any]],
    case: dict[str, Any],
) -> dict[str, Any]:
    row_summaries = []
    factor_occurrences: dict[tuple[Any, ...], dict[str, Any]] = {}
    leaf_work: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    selected_pair_sets = []
    errors = []
    rho_values = []
    requested_rows = case.get("row_leaf_keys") or []
    for row_leaf in requested_rows:
        row_key = str(row_leaf.get("row_key"))
        expected_leaf_indices = {int_value(index) for index in row_leaf.get("leaf_indices") or []}
        key = (int_value(case.get("transfer_index")), TARGET, row_key)
        record = records_by_key.get(key)
        if record is None:
            errors.append(f"missing record for {key}")
            continue
        rho_values.append(record_rho(record))
        candidate = p891.full_slice_candidate(ps, record, "b", FIXED_VALUE)
        if candidate is None:
            errors.append(f"missing full slice candidate for {key}")
            continue
        selected_leaf_indices = {int_value(leaf) for leaf, _root in candidate.get("selected_pairs") or []}
        if expected_leaf_indices and not expected_leaf_indices.issubset(selected_leaf_indices):
            errors.append(
                f"candidate leaves {sorted(selected_leaf_indices)} do not cover requested {sorted(expected_leaf_indices)} for {key}"
            )
            continue
        selection = p842.evaluate_chosen(ps, record, [candidate], "p893_raw_selector_repair_full_factor")
        if int_value(selection.get("selected_root_pair_count")) <= 0:
            errors.append(f"selection did not recover root pair for {key}")
            continue
        row_summary = p891.chosen_candidate_summary(record, candidate, selection)
        row_summaries.append(row_summary)
        selected_pair = p891.selected_pair_key(candidate)
        selected_pair_sets.append(selected_pair)
        leaf_key = (
            candidate.get("axis"),
            int_value(candidate.get("fixed_value")),
            int_value(candidate.get("min_leaf_index")),
            selected_pair,
        )
        leaf_variable_ops = (
            int_value(selection.get("relevant_leaf_evals"))
            + int_value(selection.get("quadratic_root_work"))
            + int_value(selection.get("recovered_root_count"))
        )
        leaf_work[leaf_key].append(leaf_variable_ops)
        for factor in candidate.get("factors_full") or candidate.get("factors") or []:
            signature = p891.factor_signature(candidate, factor)
            existing = factor_occurrences.setdefault(
                signature,
                {
                    "monomials": p891.factor_monomials(factor),
                    "rows": [],
                    "signature": list(signature),
                },
            )
            existing["rows"].append(row_key)

    fixed_overheads = [int_value(row.get("fixed_overhead")) for row in row_summaries]
    baseline_ops = sum(int_value(row.get("motif_ops")) for row in row_summaries)
    row_factor_work_sum = sum(
        int_value((row.get("selection_components") or {}).get("factor_work"))
        for row in row_summaries
    )
    unique_factor_work = sum(int_value(item.get("monomials")) for item in factor_occurrences.values())
    shared_leaf_work = sum(max(values) for values in leaf_work.values())
    union_dedup_ops = (max(fixed_overheads) if fixed_overheads else 0) + unique_factor_work + shared_leaf_work
    rho_estimate = max(rho_values) if rho_values else 0
    strict_target = rho_estimate - 1 if rho_estimate else None
    duplicate_factors = [
        item
        for item in factor_occurrences.values()
        if len(set(item.get("rows") or [])) > 1
    ]
    return {
        "baseline_motif_ops": baseline_ops,
        "baseline_motif_ops_over_rho": ratio(baseline_ops, rho_estimate),
        "case": {
            "below_rho": case.get("below_rho"),
            "ops_over_rho": case.get("ops_over_rho"),
            "policy": case.get("policy"),
            "public_key_verified": case.get("public_key_verified"),
            "rank": case.get("rank"),
            "relation_count": case.get("relation_count"),
            "row_leaf_keys": case.get("row_leaf_keys"),
            "row_selector": case.get("row_selector"),
            "selected_leaf_count": case.get("selected_leaf_count"),
            "selected_row_count": case.get("selected_row_count"),
            "selector": case.get("selector"),
            "source_verified": case.get("source_verified"),
            "summary_path": case.get("summary_path"),
            "top_k": case.get("top_k"),
            "transfer_index": case.get("transfer_index"),
        },
        "concrete_union_dedup_ops": union_dedup_ops,
        "concrete_union_dedup_ops_over_rho": ratio(union_dedup_ops, rho_estimate),
        "duplicate_factor_count": len(duplicate_factors),
        "duplicate_factor_work_saved": row_factor_work_sum - unique_factor_work,
        "duplicate_factors": duplicate_factors,
        "errors": errors,
        "fixed_overhead_charged": max(fixed_overheads) if fixed_overheads else 0,
        "fixed_overhead_values": fixed_overheads,
        "leaf_groups": {str(key): values for key, values in sorted(leaf_work.items())},
        "reconstructed": bool(row_summaries) and not errors,
        "rho_estimate": rho_estimate,
        "row_count": len(row_summaries),
        "row_factor_work_sum": row_factor_work_sum,
        "row_summaries": row_summaries,
        "selected_pair_sets": [list(pair_set) for pair_set in selected_pair_sets],
        "shared_leaf_work": shared_leaf_work,
        "strict_below_rho": bool(strict_target is not None and union_dedup_ops <= strict_target and not errors),
        "strict_below_rho_margin_ops": (strict_target - union_dedup_ops) if strict_target is not None else None,
        "strict_below_rho_target_ops": strict_target,
        "unique_factor_count": len(factor_occurrences),
        "unique_factor_work": unique_factor_work,
    }


def determine_claim(evaluated: list[dict[str, Any]]) -> str:
    if any(item.get("strict_below_rho") for item in evaluated):
        return "P893_RAW_SELECTOR_REPAIR_FULL_FACTOR_DEDUP_BEATS_RHO_ON_FRESH_CONTEXT"
    if any(item.get("reconstructed") for item in evaluated):
        return "NEGATIVE_RESULT_P893_RAW_SELECTOR_REPAIRS_VERIFY_BUT_FACTOR_DEDUP_ABOVE_RHO"
    return "NEGATIVE_RESULT_P893_RAW_SELECTOR_CASES_DO_NOT_RECONSTRUCT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    sources = [Path(path) for path in (args.source or DEFAULT_SOURCES)]
    cases = [case for source in sources for case in wanted_cases(source)]
    ps = p842.load_module("ecdlp_public_slice_for_p893", p842.PUBLIC_SLICE_SCRIPT)
    records_by_key = load_records_for_sources(ps, sources, int(args.max_cases_per_source), int(args.max_factor_degree))
    evaluated = [evaluate_case(ps, records_by_key, case) for case in cases]
    strict = [item for item in evaluated if item.get("strict_below_rho")]
    reconstructed = [item for item in evaluated if item.get("reconstructed")]
    distinct_strict_row_sets = {
        tuple(
            (str(row.get("row_key")), tuple(int_value(index) for index in row.get("leaf_indices") or []))
            for row in ((item.get("case") or {}).get("row_leaf_keys") or [])
        )
        for item in strict
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(evaluated),
        "created_at": now_iso(),
        "evaluated_cases": evaluated,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SELECTOR-REPAIR AUDIT: raw positive cases provide row/leaf choices; this is not yet train-only.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p893_raw_selector_repair_full_factor_dedup",
        "parameters": {
            "fixed_value": FIXED_VALUE,
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "source_count": len(sources),
            "target": TARGET,
        },
        "schema": SCHEMA,
        "summary": {
            "distinct_strict_row_set_count": len(distinct_strict_row_sets),
            "failed_reconstruction_count": len([item for item in evaluated if item.get("errors")]),
            "raw_verified_candidate_count": len(cases),
            "reconstructed_count": len(reconstructed),
            "strict_below_rho_count": len(strict),
            "transfers_with_strict_below_rho": sorted({(item.get("case") or {}).get("transfer_index") for item in strict}),
            "min_union_dedup_ops_over_rho": (
                min(float(item["concrete_union_dedup_ops_over_rho"]) for item in reconstructed if item.get("concrete_union_dedup_ops_over_rho") is not None)
                if reconstructed
                else None
            ),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, action="append")
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
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
