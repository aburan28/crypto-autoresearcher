#!/usr/bin/env python3
"""P897 public multi-slice rematerializer for P896 selected cases."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p893_raw_selector_repair_full_factor_dedup as p893
import low_term_total2_p896_selector_family_generalization as p896


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p897_multi_slice_rematerializer.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p897_multi_slice_rematerializer_probe.json"
DEFAULT_SOURCES = p896.DEFAULT_SOURCES
SCHEMA = "ecdlp.low_term_total2_p897_multi_slice_rematerializer.v1"
TARGET = p896.TARGET
POLICIES = ("leaf_b", "leaf_c", "min_factor_work", "min_motif_ops")
DETERMINISTIC_POLICIES = {"leaf_b", "leaf_c"}
DIAGNOSTIC_POLICIES = {"min_factor_work", "min_motif_ops"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p893.int_value(value, default)


def requested_leaf_indices(row_leaf: dict[str, Any]) -> list[int]:
    return [int_value(index) for index in row_leaf.get("leaf_indices") or []]


def record_key(case: dict[str, Any], row_key: str) -> tuple[int, str, str]:
    return (int_value(case.get("transfer_index")), TARGET, str(row_key))


def record_rho(record: dict[str, Any]) -> int:
    return p893.record_rho(record)


def selected_leaf_set(candidate: dict[str, Any]) -> set[int]:
    return {int_value(leaf) for leaf, _root in candidate.get("selected_pairs") or []}


def candidate_sort_key(option: dict[str, Any], policy: str) -> tuple[Any, ...]:
    selection = option.get("selection") or {}
    candidate = option.get("candidate") or {}
    if policy == "min_motif_ops":
        primary = int_value(selection.get("public_slice_motif_ops"), 10**9)
    else:
        primary = int_value(selection.get("factor_work"), 10**9)
    return (
        primary,
        int_value(candidate.get("selected_factor_monomials"), 10**9),
        int_value(candidate.get("selected_factor_count"), 10**9),
        str(candidate.get("axis")),
        int_value(candidate.get("fixed_value")),
    )


def option_summary(option: dict[str, Any]) -> dict[str, Any]:
    candidate = option.get("candidate") or {}
    selection = option.get("selection") or {}
    return {
        "axis": candidate.get("axis"),
        "covers_requested_leaves": option.get("covers_requested_leaves"),
        "fixed_value": candidate.get("fixed_value"),
        "fixed_value_mod": candidate.get("fixed_value_mod"),
        "leaf_source": option.get("leaf_source"),
        "motif_ops": selection.get("public_slice_motif_ops"),
        "motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
        "requested_leaf_indices": option.get("requested_leaf_indices"),
        "selected_factor_count": candidate.get("selected_factor_count"),
        "selected_factor_monomials": candidate.get("selected_factor_monomials"),
        "selected_leaf_indices": sorted(selected_leaf_set(candidate)),
        "selected_root_pair_count": selection.get("selected_root_pair_count"),
    }


def build_candidate_options(
    ps: Any,
    record: dict[str, Any],
    requested_leaves: list[int],
) -> list[dict[str, Any]]:
    coords = [
        coord
        for coord in ps.leaf_coords(record)
        if int_value(coord.get("leaf_index")) in set(requested_leaves)
    ]
    options = []
    seen: set[tuple[str, int]] = set()
    for coord in sorted(coords, key=lambda item: (int_value(item.get("leaf_index")), int_value(item.get("b")), int_value(item.get("c")))):
        leaf_index = int_value(coord.get("leaf_index"))
        for axis in ("b", "c"):
            fixed_value = int_value(coord.get(axis))
            key = (axis, fixed_value)
            if key in seen:
                continue
            seen.add(key)
            candidate = p893.p891.full_slice_candidate(ps, record, axis, fixed_value)
            if candidate is None:
                options.append(
                    {
                        "axis": axis,
                        "candidate": None,
                        "covers_requested_leaves": False,
                        "fixed_value": fixed_value,
                        "leaf_source": leaf_index,
                        "requested_leaf_indices": requested_leaves,
                        "selection": None,
                    }
                )
                continue
            selection = p893.p842.evaluate_chosen(ps, record, [candidate], "p897_multi_slice")
            option = {
                "axis": axis,
                "candidate": candidate,
                "covers_requested_leaves": set(requested_leaves).issubset(selected_leaf_set(candidate)),
                "fixed_value": fixed_value,
                "leaf_source": leaf_index,
                "requested_leaf_indices": requested_leaves,
                "selection": selection,
            }
            options.append(option)
    return options


def choose_option(options: list[dict[str, Any]], policy: str) -> dict[str, Any] | None:
    if policy in ("leaf_b", "leaf_c"):
        axis = policy[-1]
        for option in options:
            if option.get("axis") == axis:
                return option
        return None
    valid = [
        option
        for option in options
        if option.get("candidate") is not None
        and option.get("covers_requested_leaves")
        and int_value((option.get("selection") or {}).get("selected_root_pair_count")) > 0
    ]
    return min(valid, key=lambda option: candidate_sort_key(option, policy)) if valid else None


def row_result_for_policy(
    ps: Any,
    record: dict[str, Any],
    row_leaf: dict[str, Any],
    options: list[dict[str, Any]],
    policy: str,
) -> dict[str, Any]:
    row_key = str(row_leaf.get("row_key"))
    requested = requested_leaf_indices(row_leaf)
    chosen = choose_option(options, policy)
    if chosen is None:
        return {
            "error": f"no candidate option for policy {policy} row {row_key} leaves {requested}",
            "options": [option_summary(option) for option in options],
            "reconstructed": False,
            "requested_leaf_indices": requested,
            "row_key": row_key,
        }
    candidate = chosen.get("candidate")
    selection = chosen.get("selection")
    if candidate is None or selection is None:
        return {
            "chosen": option_summary(chosen),
            "error": f"missing slice candidate for policy {policy} row {row_key}",
            "options": [option_summary(option) for option in options],
            "reconstructed": False,
            "requested_leaf_indices": requested,
            "row_key": row_key,
        }
    if not chosen.get("covers_requested_leaves"):
        return {
            "chosen": option_summary(chosen),
            "error": f"chosen slice does not cover requested leaves {requested} for row {row_key}",
            "options": [option_summary(option) for option in options],
            "reconstructed": False,
            "requested_leaf_indices": requested,
            "row_key": row_key,
        }
    if int_value(selection.get("selected_root_pair_count")) <= 0:
        return {
            "chosen": option_summary(chosen),
            "error": f"chosen slice has no selected root pairs for row {row_key}",
            "options": [option_summary(option) for option in options],
            "reconstructed": False,
            "requested_leaf_indices": requested,
            "row_key": row_key,
        }
    return {
        "chosen": option_summary(chosen),
        "options": [option_summary(option) for option in options],
        "reconstructed": True,
        "requested_leaf_indices": requested,
        "row_key": row_key,
        "row_summary": p893.p891.chosen_candidate_summary(record, candidate, selection),
    }


def evaluate_case_policy(
    ps: Any,
    records_by_key: dict[tuple[int, str, str], dict[str, Any]],
    case: dict[str, Any],
    policy: str,
) -> dict[str, Any]:
    row_results = []
    row_summaries = []
    errors = []
    rho_values = []
    factor_occurrences: dict[tuple[Any, ...], dict[str, Any]] = {}
    leaf_work: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    selected_pair_sets = []
    candidate_search_options = 0
    candidate_search_valid_options = 0
    candidate_search_factor_work = 0
    candidate_search_motif_ops = 0

    for row_leaf in case.get("row_leaf_keys") or []:
        row_key = str(row_leaf.get("row_key"))
        key = record_key(case, row_key)
        record = records_by_key.get(key)
        if record is None:
            error = f"missing record for {key}"
            errors.append(error)
            row_results.append({"error": error, "reconstructed": False, "row_key": row_key})
            continue
        rho_values.append(record_rho(record))
        options = build_candidate_options(ps, record, requested_leaf_indices(row_leaf))
        candidate_search_options += len(options)
        valid_options = [
            option
            for option in options
            if option.get("candidate") is not None
            and option.get("covers_requested_leaves")
            and int_value((option.get("selection") or {}).get("selected_root_pair_count")) > 0
        ]
        candidate_search_valid_options += len(valid_options)
        candidate_search_factor_work += sum(int_value((option.get("selection") or {}).get("factor_work")) for option in valid_options)
        candidate_search_motif_ops += sum(int_value((option.get("selection") or {}).get("public_slice_motif_ops")) for option in valid_options)
        row_result = row_result_for_policy(ps, record, row_leaf, options, policy)
        row_results.append(row_result)
        if not row_result.get("reconstructed"):
            errors.append(str(row_result.get("error")))
            continue

        row_summary = row_result["row_summary"]
        row_summaries.append(row_summary)
        candidate = (row_result.get("chosen") or {})
        selected_pairs = tuple(sorted((int(leaf), int(root)) for leaf, root in (row_summary.get("candidate") or {}).get("selected_pairs") or []))
        selected_pair_sets.append(selected_pairs)
        leaf_key = (
            candidate.get("axis"),
            int_value(candidate.get("fixed_value")),
            int_value((row_summary.get("candidate") or {}).get("min_leaf_index")),
            selected_pairs,
        )
        components = row_summary.get("selection_components") or {}
        leaf_variable_ops = (
            int_value(components.get("relevant_leaf_evals"))
            + int_value(components.get("quadratic_root_work"))
            + int_value(components.get("recovered_root_count"))
        )
        leaf_work[leaf_key].append(leaf_variable_ops)
        for factor in (row_summary.get("factor_records") or []):
            signature = tuple(json.dumps(item, sort_keys=True) if isinstance(item, list) else item for item in factor.get("signature") or [])
            existing = factor_occurrences.setdefault(
                signature,
                {
                    "monomials": int_value(factor.get("monomials")),
                    "rows": [],
                    "signature": factor.get("signature"),
                },
            )
            existing["rows"].append(row_summary.get("row_key"))

    fixed_overheads = [int_value(row.get("fixed_overhead")) for row in row_summaries]
    baseline_ops = sum(int_value(row.get("motif_ops")) for row in row_summaries)
    row_factor_work_sum = sum(int_value((row.get("selection_components") or {}).get("factor_work")) for row in row_summaries)
    unique_factor_work = sum(int_value(item.get("monomials")) for item in factor_occurrences.values())
    shared_leaf_work = sum(max(values) for values in leaf_work.values())
    union_dedup_ops = (max(fixed_overheads) if fixed_overheads else 0) + unique_factor_work + shared_leaf_work
    rho_estimate = max(rho_values) if rho_values else 0
    strict_target = rho_estimate - 1 if rho_estimate else None
    duplicate_factors = [item for item in factor_occurrences.values() if len(set(item.get("rows") or [])) > 1]
    reconstructed = bool(row_summaries) and not errors and len(row_summaries) == len(case.get("row_leaf_keys") or [])
    return {
        "baseline_motif_ops": baseline_ops,
        "baseline_motif_ops_over_rho": p893.ratio(baseline_ops, rho_estimate),
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
        "candidate_search_factor_work": candidate_search_factor_work,
        "candidate_search_motif_ops": candidate_search_motif_ops,
        "candidate_search_options": candidate_search_options,
        "candidate_search_valid_options": candidate_search_valid_options,
        "concrete_union_dedup_ops": union_dedup_ops,
        "concrete_union_dedup_ops_over_rho": p893.ratio(union_dedup_ops, rho_estimate),
        "diagnostic_policy": policy in DIAGNOSTIC_POLICIES,
        "duplicate_factor_count": len(duplicate_factors),
        "duplicate_factor_work_saved": row_factor_work_sum - unique_factor_work,
        "duplicate_factors": duplicate_factors,
        "errors": errors,
        "fixed_overhead_charged": max(fixed_overheads) if fixed_overheads else 0,
        "fixed_overhead_values": fixed_overheads,
        "leaf_groups": {str(key): values for key, values in sorted(leaf_work.items(), key=lambda item: str(item[0]))},
        "policy": policy,
        "reconstructed": reconstructed,
        "rho_estimate": rho_estimate,
        "row_count": len(row_summaries),
        "row_factor_work_sum": row_factor_work_sum,
        "row_results": row_results,
        "row_summaries": row_summaries,
        "selected_pair_sets": [list(pair_set) for pair_set in selected_pair_sets],
        "shared_leaf_work": shared_leaf_work,
        "strict_below_rho": bool(strict_target is not None and union_dedup_ops <= strict_target and reconstructed),
        "strict_below_rho_margin_ops": (strict_target - union_dedup_ops) if strict_target is not None else None,
        "strict_below_rho_target_ops": strict_target,
        "unique_factor_count": len(factor_occurrences),
        "unique_factor_work": unique_factor_work,
    }


def distinct_row_set(item: dict[str, Any]) -> tuple[Any, ...]:
    case = item.get("case") or {}
    return tuple(
        (str(row_leaf.get("row_key")), tuple(int_value(index) for index in row_leaf.get("leaf_indices") or []))
        for row_leaf in case.get("row_leaf_keys") or []
    )


def summarize_policy(policy: str, evaluated: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [item for item in evaluated if item.get("policy") == policy]
    reconstructed = [item for item in rows if item.get("reconstructed")]
    strict = [item for item in rows if item.get("strict_below_rho")]
    return {
        "candidate_search_options": sum(int_value(item.get("candidate_search_options")) for item in rows),
        "candidate_search_valid_options": sum(int_value(item.get("candidate_search_valid_options")) for item in rows),
        "diagnostic_policy": policy in DIAGNOSTIC_POLICIES,
        "evaluated_case_count": len(rows),
        "failed_reconstruction_count": len([item for item in rows if item.get("errors")]),
        "min_reconstructed_union_dedup_ops_over_rho": (
            min(float(item["concrete_union_dedup_ops_over_rho"]) for item in reconstructed if item.get("concrete_union_dedup_ops_over_rho") is not None)
            if reconstructed
            else None
        ),
        "reconstructed_count": len(reconstructed),
        "strict_below_rho_count": len(strict),
        "strict_distinct_row_set_count": len({distinct_row_set(item) for item in strict}),
        "transfers_with_strict_below_rho": sorted({(item.get("case") or {}).get("transfer_index") for item in strict}),
    }


def determine_claim(evaluated: list[dict[str, Any]], claim_label: str) -> str:
    label = str(claim_label)
    if any(item.get("strict_below_rho") and item.get("policy") in DETERMINISTIC_POLICIES for item in evaluated):
        return f"{label}_DETERMINISTIC_MULTI_SLICE_FULL_FACTOR_DEDUP_BEATS_RHO"
    if any(item.get("strict_below_rho") and item.get("policy") in DIAGNOSTIC_POLICIES for item in evaluated):
        return f"{label}_DIAGNOSTIC_MULTI_SLICE_BEATS_RHO_NEEDS_PUBLIC_PREDICTOR"
    if any(item.get("reconstructed") for item in evaluated):
        return f"NEGATIVE_RESULT_{label}_MULTI_SLICE_RECONSTRUCTS_BUT_NOT_BELOW_RHO"
    if evaluated:
        return f"NEGATIVE_RESULT_{label}_MULTI_SLICE_NO_RECONSTRUCTION"
    return f"NEGATIVE_RESULT_{label}_MULTI_SLICE_SELECTS_NO_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    sources = [Path(path) for path in (args.source or DEFAULT_SOURCES)]
    cases = [case for source in sources for case in p896.cases_for_source(source)]
    ps = p893.p842.load_module("ecdlp_public_slice_for_p897", p893.p842.PUBLIC_SLICE_SCRIPT)
    records_by_key = p893.load_records_for_sources(ps, sources, int(args.max_cases_per_source), int(args.max_factor_degree))
    evaluated = [
        evaluate_case_policy(ps, records_by_key, case, policy)
        for case in cases
        for policy in POLICIES
    ]
    strict = [item for item in evaluated if item.get("strict_below_rho")]
    deterministic_strict = [item for item in strict if item.get("policy") in DETERMINISTIC_POLICIES]
    diagnostic_strict = [item for item in strict if item.get("policy") in DIAGNOSTIC_POLICIES]
    reconstructed = [item for item in evaluated if item.get("reconstructed")]
    verifier_positive_cases = [case for case in cases if case.get("public_key_verified")]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(evaluated, args.claim_label),
        "created_at": now_iso(),
        "evaluated_policy_cases": evaluated,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SELECTED-CONTEXT COMPONENT: selected leaf indices come from the no-label P896 selector-family cases.",
            "DETERMINISTIC POLICIES: leaf_b and leaf_c use only the selected leaf public coordinate on a fixed axis.",
            "DIAGNOSTIC POLICIES: min_factor_work and min_motif_ops inspect public factorization/cost metrics and need separately charged search before promotion.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": str(args.method),
        "parameters": {
            "diagnostic_policies": sorted(DIAGNOSTIC_POLICIES),
            "deterministic_policies": sorted(DETERMINISTIC_POLICIES),
            "input_case_count": len(cases),
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "policies": list(POLICIES),
            "source_count": len(sources),
            "target": TARGET,
        },
        "schema": SCHEMA,
        "source_paths": [str(source) for source in sources],
        "summary": {
            "deterministic_strict_below_rho_count": len(deterministic_strict),
            "diagnostic_strict_below_rho_count": len(diagnostic_strict),
            "distinct_deterministic_strict_row_set_count": len({distinct_row_set(item) for item in deterministic_strict}),
            "distinct_diagnostic_strict_row_set_count": len({distinct_row_set(item) for item in diagnostic_strict}),
            "evaluated_policy_case_count": len(evaluated),
            "input_case_count": len(cases),
            "policy_summaries": {policy: summarize_policy(policy, evaluated) for policy in POLICIES},
            "reconstructed_policy_case_count": len(reconstructed),
            "selected_verifier_positive_case_count": len(verifier_positive_cases),
            "strict_below_rho_count": len(strict),
            "transfers_with_deterministic_strict_below_rho": sorted({(item.get("case") or {}).get("transfer_index") for item in deterministic_strict}),
            "transfers_with_diagnostic_strict_below_rho": sorted({(item.get("case") or {}).get("transfer_index") for item in diagnostic_strict}),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, action="append")
    parser.add_argument("--max-cases-per-source", type=int, default=0)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--claim-label", default="P897")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--method", default="p897_multi_slice_rematerializer")
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
