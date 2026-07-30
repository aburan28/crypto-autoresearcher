#!/usr/bin/env python3
"""P891 concrete union-level factor dedup audit for P889 companion rows."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p842_public_slice_motif_compression_audit as p842
import low_term_total2_p881_public_slice_motif_rank_descent_audit as p881
import low_term_total2_p882_public_post_motif_pairing_gate as p882
import low_term_total2_p888_public_surface_family_prefilter as p888


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p891_union_level_factor_dedup_evaluator.md"
DEFAULT_P889_SOURCE = STATE_DIR / "low_term_total2_p889_train_only_public_source_family_scorer_probe.json"
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_expanded_leaf_rescue_712_719_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p891_union_level_factor_dedup_evaluator_probe.json"
SCHEMA = "ecdlp.low_term_total2_p891_union_level_factor_dedup_evaluator.v1"
TARGET = "22050.cf1@11731"
FIXED_VALUE = 10907
POLICY_NAME = "m_lte36_transfer_mod3_xfer1mod3"


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
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def factor_terms(factor: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple((int(a), int(b)) for a, b in factor.get("terms") or [])


def factor_signature(candidate: dict[str, Any], factor: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(factor.get("axis") or candidate.get("axis")),
        int_value(factor.get("fixed_value") or candidate.get("fixed_value")),
        int_value(factor.get("degree")),
        factor_terms(factor),
    )


def factor_monomials(factor: dict[str, Any]) -> int:
    return int_value(factor.get("monomials")) or len(factor.get("terms") or [])


def candidate_matches(candidate: dict[str, Any], monomial_cap: int) -> bool:
    return (
        candidate.get("axis") == "b"
        and int_value(candidate.get("fixed_value")) == FIXED_VALUE
        and int_value(candidate.get("selected_factor_monomials")) <= int(monomial_cap)
    )


def full_slice_candidate(ps: Any, surface_record: dict[str, Any], axis: str, fixed_value: int) -> dict[str, Any] | None:
    p = int(surface_record["p"])
    coords = [
        coord
        for coord in ps.leaf_coords(surface_record)
        if int(coord[axis]) == int(fixed_value)
    ]
    if not coords:
        return None
    specialized = ps.slice_factor_probe.specialize_resultant(surface_record["surface"], axis, fixed_value, p)
    if specialized.is_zero:
        return None
    factors = [
        {
            **factor,
            "axis": axis,
            "fixed_value": int(fixed_value),
            "covered_selected_values": [],
        }
        for factor in ps.slice_factor_probe.factor_rows(specialized, p)
        if 0 < int(factor["degree"]) <= 1
    ]
    if not factors:
        return None
    variable_values = [int(coord["c"] if axis == "b" else coord["b"]) for coord in coords]
    plan = {
        "axis": axis,
        "slice_count": 1,
        "selected_factor_count": len(factors),
        "selected_factor_monomials": sum(int(factor["monomials"]) for factor in factors),
        "selected_factor_max_degree": max(int(factor["degree"]) for factor in factors),
        "factors": factors,
    }
    candidate = ps.evaluate_candidate(surface_record, plan, coords)
    candidate.update(
        {
            "axis": axis,
            "fixed_value": int(fixed_value),
            "fixed_value_mod": int(fixed_value) % p,
            "factors_full": factors,
            "factors_truncated_count": len(candidate.get("factors") or []),
            "max_leaf_index": max(int(coord["leaf_index"]) for coord in coords),
            "max_variable_value": max(variable_values),
            "min_leaf_index": min(int(coord["leaf_index"]) for coord in coords),
            "min_variable_value": min(variable_values),
        }
    )
    return candidate


def row_variable_ops(selection: dict[str, Any]) -> int:
    return (
        int_value(selection.get("factor_work"))
        + int_value(selection.get("relevant_leaf_evals"))
        + int_value(selection.get("quadratic_root_work"))
        + int_value(selection.get("recovered_root_count"))
    )


def selected_pair_key(candidate: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple(sorted((int(leaf), int(root)) for leaf, root in candidate.get("selected_pairs") or []))


def chosen_candidate_summary(record: dict[str, Any], candidate: dict[str, Any], selection: dict[str, Any]) -> dict[str, Any]:
    factors = candidate.get("factors_full") or candidate.get("factors") or []
    factor_records = [
        {
            "factor_index": factor.get("factor_index"),
            "monomials": factor_monomials(factor),
            "signature": list(factor_signature(candidate, factor)),
        }
        for factor in factors
    ]
    variable_ops = row_variable_ops(selection)
    motif_ops = int_value(selection.get("public_slice_motif_ops"))
    return {
        "candidate": {
            "axis": candidate.get("axis"),
            "factor_zero_leaf_count": candidate.get("factor_zero_leaf_count"),
            "factor_zero_leaf_indices": candidate.get("factor_zero_leaf_indices"),
            "fixed_value": candidate.get("fixed_value"),
            "max_leaf_index": candidate.get("max_leaf_index"),
            "min_leaf_index": candidate.get("min_leaf_index"),
            "recovered_root_count": candidate.get("recovered_root_count"),
            "relevant_leaf_count": candidate.get("relevant_leaf_count"),
            "selected_factor_count": candidate.get("selected_factor_count"),
            "selected_factor_monomials": candidate.get("selected_factor_monomials"),
            "selected_pairs": candidate.get("selected_pairs"),
            "stored_factor_preview_count": candidate.get("factors_truncated_count"),
        },
        "factor_records": factor_records,
        "fixed_overhead": motif_ops - variable_ops,
        "motif_ops": motif_ops,
        "motif_ops_over_rho": selection.get("public_slice_motif_ops_over_rho"),
        "row_key": record.get("row_key"),
        "row_salt": p888.row_salt(record.get("row_key")),
        "selection_components": {
            "factor_work": selection.get("factor_work"),
            "factor_zero_leaf_evals": selection.get("factor_zero_leaf_evals"),
            "quadratic_root_work": selection.get("quadratic_root_work"),
            "recovered_root_count": selection.get("recovered_root_count"),
            "relevant_leaf_evals": selection.get("relevant_leaf_evals"),
            "selected_root_pair_count": selection.get("selected_root_pair_count"),
            "variable_ops": variable_ops,
        },
        "transfer_index": p842.transfer_index(record),
    }


def load_records_for_validation(ps: Any, source_path: Path, max_cases: int, max_factor_degree: int) -> dict[str, dict[str, Any]]:
    ps_args = p842.public_slice_args(ps)
    ps_args.signature_source = source_path
    ps_args.max_cases = int(max_cases)
    ps_args.max_factor_degree = int(max_factor_degree)
    surface_records, _case_results = p842.materialize_surface_records(ps, ps_args)
    return {
        str(record.get("row_key")): record
        for record in surface_records
        if isinstance(record, dict)
        and record.get("target") == TARGET
        and p842.transfer_index(record) == 712
    }


def validation_groups(p889_payload: dict[str, Any], policy_name: str) -> list[dict[str, Any]]:
    policy_report = ((p889_payload.get("validation") or {}).get("policy_reports") or {}).get(policy_name) or {}
    return [
        group
        for group in policy_report.get("context_groups") or []
        if group.get("target_context_public_key_verified") and group.get("target") == TARGET
    ]


def evaluate_group(
    ps: Any,
    records_by_row: dict[str, dict[str, Any]],
    group: dict[str, Any],
    monomial_cap: int,
) -> dict[str, Any]:
    row_summaries = []
    factor_occurrences: dict[tuple[Any, ...], dict[str, Any]] = {}
    leaf_work: dict[tuple[Any, ...], list[int]] = defaultdict(list)
    selected_pair_sets = []
    for row_key in group.get("row_keys") or []:
        record = records_by_row[str(row_key)]
        candidate = full_slice_candidate(ps, record, "b", FIXED_VALUE)
        chosen = [candidate] if candidate and candidate_matches(candidate, monomial_cap) else []
        selection = p842.evaluate_chosen(ps, record, chosen, POLICY_NAME)
        if len(chosen) != 1:
            raise RuntimeError(f"expected exactly one chosen candidate for {row_key}, got {len(chosen)}")
        candidate = chosen[0]
        row_summary = chosen_candidate_summary(record, candidate, selection)
        row_summaries.append(row_summary)
        selected_pair_sets.append(selected_pair_key(candidate))
        leaf_key = (
            candidate.get("axis"),
            int_value(candidate.get("fixed_value")),
            int_value(candidate.get("min_leaf_index")),
            selected_pair_key(candidate),
        )
        leaf_variable_ops = (
            int_value(selection.get("relevant_leaf_evals"))
            + int_value(selection.get("quadratic_root_work"))
            + int_value(selection.get("recovered_root_count"))
        )
        leaf_work[leaf_key].append(leaf_variable_ops)
        for factor in candidate.get("factors_full") or candidate.get("factors") or []:
            signature = factor_signature(candidate, factor)
            existing = factor_occurrences.setdefault(
                signature,
                {
                    "monomials": factor_monomials(factor),
                    "rows": [],
                    "signature": list(signature),
                },
            )
            existing["rows"].append(str(row_key))

    fixed_overheads = [int_value(row.get("fixed_overhead")) for row in row_summaries]
    baseline_ops = sum(int_value(row.get("motif_ops")) for row in row_summaries)
    row_factor_work_sum = sum(int_value((row.get("selection_components") or {}).get("factor_work")) for row in row_summaries)
    unique_factor_work = sum(int_value(item.get("monomials")) for item in factor_occurrences.values())
    duplicate_factor_work_saved = row_factor_work_sum - unique_factor_work
    shared_leaf_work = sum(max(values) for values in leaf_work.values())
    union_dedup_ops = (max(fixed_overheads) if fixed_overheads else 0) + unique_factor_work + shared_leaf_work
    rho_estimate = int(round(float(group["motif_ops"]) / float(group["motif_ops_over_rho"])))
    strict_target = rho_estimate - 1
    duplicate_factors = [
        item
        for item in factor_occurrences.values()
        if len(set(item.get("rows") or [])) > 1
    ]
    return {
        "baseline_motif_ops": baseline_ops,
        "baseline_motif_ops_over_rho": ratio(baseline_ops, rho_estimate),
        "concrete_union_dedup_ops": union_dedup_ops,
        "concrete_union_dedup_ops_over_rho": ratio(union_dedup_ops, rho_estimate),
        "context": {
            "challenge_seed": group.get("challenge_seed"),
            "direct_ops": group.get("direct_ops"),
            "direct_ops_over_rho": group.get("direct_ops_over_rho"),
            "matrix_rank": group.get("matrix_rank"),
            "motif_ops": group.get("motif_ops"),
            "motif_ops_over_rho": group.get("motif_ops_over_rho"),
            "row_keys": group.get("row_keys"),
            "target": group.get("target"),
            "union": group.get("union"),
        },
        "duplicate_factor_count": len(duplicate_factors),
        "duplicate_factor_work_saved": duplicate_factor_work_saved,
        "duplicate_factors": duplicate_factors,
        "fixed_overhead_charged": max(fixed_overheads) if fixed_overheads else 0,
        "fixed_overhead_values": fixed_overheads,
        "leaf_groups": {str(key): values for key, values in sorted(leaf_work.items())},
        "row_factor_work_sum": row_factor_work_sum,
        "row_summaries": row_summaries,
        "rho_estimate": rho_estimate,
        "selected_pair_sets": [list(pair_set) for pair_set in selected_pair_sets],
        "shared_leaf_work": shared_leaf_work,
        "strict_below_rho_margin_ops": strict_target - union_dedup_ops,
        "strict_below_rho_target_ops": strict_target,
        "unique_factor_count": len(factor_occurrences),
        "unique_factor_work": unique_factor_work,
    }


def determine_claim(evaluated: list[dict[str, Any]]) -> str:
    if any(int_value(item.get("concrete_union_dedup_ops")) <= int_value(item.get("strict_below_rho_target_ops")) for item in evaluated):
        return "P891_UNION_FACTOR_DEDUP_BEATS_RHO_ON_TRANSFERRED_CONTEXT"
    if any(int_value(item.get("concrete_union_dedup_ops")) < int_value(item.get("rho_estimate")) for item in evaluated):
        return "P891_UNION_FACTOR_DEDUP_BELOW_RHO_ESTIMATE_NONSTRICT"
    return "NEGATIVE_RESULT_P891_UNION_FACTOR_DEDUP_STILL_ABOVE_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p889_payload = load_json(args.p889_source)
    ps = p842.load_module("ecdlp_public_slice_for_p891", p842.PUBLIC_SLICE_SCRIPT)
    records_by_row = load_records_for_validation(ps, args.validation_source, int(args.max_cases_per_source), int(args.max_factor_degree))
    groups = validation_groups(p889_payload, args.policy_name)
    evaluated = [evaluate_group(ps, records_by_row, group, int(args.monomial_cap)) for group in groups]
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p889_source": str(args.p889_source),
            "script": str(Path(__file__)),
            "validation_source": str(args.validation_source),
        },
        "claim_status": determine_claim(evaluated),
        "created_at": now_iso(),
        "evaluated_contexts": evaluated,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "COST-COMPONENT: concrete factor deduplication is an accounting/evaluator component, not a full solver.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p891_union_level_factor_dedup_evaluator",
        "parameters": {
            "context_count": len(evaluated),
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "monomial_cap": int(args.monomial_cap),
            "policy_name": args.policy_name,
        },
        "red_team_handoff": {
            "assumptions": [
                "Identical selected factor signatures can be evaluated once across companion rows.",
                "Rows sharing fixed value, selected leaf, and selected root can share leaf/root variable work.",
                "The max fixed-overhead charge is a conservative proxy for union-level fixed setup.",
            ],
            "failure_modes": [
                "Identical factor signatures may still require row-local binding work not counted here.",
                "The fixed-overhead decomposition is inferred from the current cost formula.",
                "The result remains a selected-context component and needs wider train-selected validation.",
            ],
            "next_concrete_action": (
                "If P891 beats rho, run P892 to apply the same union factor-dedup evaluator to all P889 selected validation policies and the next fresh sources 752_791."
            ),
        },
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p889-source", type=Path, default=DEFAULT_P889_SOURCE)
    parser.add_argument("--validation-source", type=Path, default=DEFAULT_VALIDATION_SOURCE)
    parser.add_argument("--policy-name", default=POLICY_NAME)
    parser.add_argument("--monomial-cap", type=int, default=36)
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
                "evaluated_contexts": payload["evaluated_contexts"],
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
