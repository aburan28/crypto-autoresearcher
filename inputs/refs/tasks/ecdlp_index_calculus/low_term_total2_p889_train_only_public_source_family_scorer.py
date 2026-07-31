#!/usr/bin/env python3
"""P889 train-only public source-family scorer for P888's transfer gap."""

from __future__ import annotations

import argparse
import copy
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
import low_term_total2_p888_public_surface_family_prefilter as p888


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p889_train_only_public_source_family_scorer.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p889_train_only_public_source_family_scorer_probe.json"
DEFAULT_P842_SOURCE = STATE_DIR / "low_term_total2_p842_public_slice_motif_compression_audit_probe.json"
DEFAULT_P888_SOURCE = STATE_DIR / "low_term_total2_p888_public_surface_family_prefilter_probe.json"
DEFAULT_TRAINING_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_672_679_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_680_687_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_688_695_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_696_703_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_704_711_summary.json",
]
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_712_719_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_720_727_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_728_735_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_736_743_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_744_751_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p889_train_only_public_source_family_scorer.v1"
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


def slug(text: str) -> str:
    return (
        text.replace("<=", "lte")
        .replace(">=", "gte")
        .replace("..", "_to_")
        .replace("==", "eq")
        .replace("=", "eq")
        .replace(" ", "_")
        .replace("/", "_")
    )


def monomial_families() -> list[dict[str, Any]]:
    return [
        {"monomial_family": "m_lte36", "monomials_lte": 36},
        {"monomial_family": "m_lte38", "monomials_lte": 38},
        {"monomial_family": "m_lte44", "monomials_lte": 44},
        {"monomial_family": "m_eq36", "monomials_eq": 36},
        {"monomial_family": "m_34_to_38", "monomials_min": 34, "monomials_max": 38},
    ]


def surface_families() -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = [{"surface_family": "metadata_only"}]
    residue_moduli = [2, 3, 4, 5, 6, 8]
    for modulus in residue_moduli:
        for remainder in range(modulus):
            specs.append(
                {
                    "row_salt_modulus": modulus,
                    "row_salt_remainder": remainder,
                    "surface_family": f"salt_mod{modulus}",
                }
            )
            specs.append(
                {
                    "surface_family": f"transfer_mod{modulus}",
                    "transfer_modulus": modulus,
                    "transfer_remainder": remainder,
                }
            )
    for salt_modulus, transfer_modulus in [(3, 4), (4, 4), (5, 4), (3, 5)]:
        for salt_remainder in range(salt_modulus):
            for transfer_remainder in range(transfer_modulus):
                specs.append(
                    {
                        "row_salt_modulus": salt_modulus,
                        "row_salt_remainder": salt_remainder,
                        "surface_family": f"salt_mod{salt_modulus}_transfer_mod{transfer_modulus}",
                        "transfer_modulus": transfer_modulus,
                        "transfer_remainder": transfer_remainder,
                    }
                )
    return specs


def policy_specs() -> list[dict[str, Any]]:
    policies = []
    seen: set[str] = set()
    for monomial in monomial_families():
        for surface in surface_families():
            policy = {**monomial, **surface}
            name_parts = [str(policy["monomial_family"]), str(policy["surface_family"])]
            if policy.get("row_salt_modulus") is not None:
                name_parts.append(f"salt{policy['row_salt_remainder']}mod{policy['row_salt_modulus']}")
            if policy.get("transfer_modulus") is not None:
                name_parts.append(f"xfer{policy['transfer_remainder']}mod{policy['transfer_modulus']}")
            policy["name"] = slug("_".join(name_parts))
            if policy["name"] in seen:
                continue
            seen.add(policy["name"])
            policies.append(policy)
    return policies


def surface_matches_policy(record: dict[str, Any], policy: dict[str, Any]) -> bool:
    if record.get("target") != TARGET:
        return False
    if policy.get("row_salt_modulus") is not None:
        salt = p888.row_salt(record.get("row_key"))
        modulus = int_value(policy.get("row_salt_modulus"), 1)
        if salt is None or salt % modulus != int_value(policy.get("row_salt_remainder")):
            return False
    if policy.get("transfer_modulus") is not None:
        modulus = int_value(policy.get("transfer_modulus"), 1)
        if p842.transfer_index(record) % modulus != int_value(policy.get("transfer_remainder")):
            return False
    return True


def candidate_matches_metadata(candidate: dict[str, Any], policy: dict[str, Any]) -> bool:
    if candidate.get("axis") != "b" or int_value(candidate.get("fixed_value")) != FIXED_VALUE:
        return False
    monomials = int_value(candidate.get("selected_factor_monomials"))
    if policy.get("monomials_lte") is not None and monomials > int_value(policy.get("monomials_lte")):
        return False
    if policy.get("monomials_eq") is not None and monomials != int_value(policy.get("monomials_eq")):
        return False
    if policy.get("monomials_min") is not None and monomials < int_value(policy.get("monomials_min")):
        return False
    if policy.get("monomials_max") is not None and monomials > int_value(policy.get("monomials_max")):
        return False
    return True


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
        "surface_family_screen_ops_sum": sum(int_value(item.get("surface_family_screen_ops")) for item in surface_costs),
        "surface_family_selected_count": len([item for item in surface_costs if item.get("surface_family_selected")]),
        "surface_screen_ops_sum": sum(int_value(item.get("surface_screen_ops")) for item in surface_costs),
        "target_candidate_count_sum": sum(
            int_value(item.get("candidate_count")) for item in surface_costs if item.get("target") == TARGET
        ),
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


def selection_for_filtered(
    ps: Any,
    record: dict[str, Any],
    candidates: list[dict[str, Any]],
    filtered_indices: tuple[int, ...],
    policy_name: str,
    selection_cache: dict[tuple[str, tuple[int, ...]], dict[str, Any]],
) -> dict[str, Any]:
    if not filtered_indices:
        return p888.empty_selection(policy_name)
    cache_key = (str(record.get("surface_id")), filtered_indices)
    if cache_key not in selection_cache:
        filtered = [candidates[index] for index in filtered_indices]
        selection_cache[cache_key] = p842.evaluate_chosen(ps, record, filtered, policy_name)
    selection = copy.deepcopy(selection_cache[cache_key])
    selection["motif_policy"] = policy_name
    return selection


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
    print(f"p889 materializing {source_path} max_cases={ps_args.max_cases} policies={len(policies)}", flush=True)
    positive_cases = p881.source_positive_cases(source_path, int(max_cases_per_source))
    policy_results = {
        policy["name"]: {
            "recovered_rows": [],
            "surface_costs": [],
        }
        for policy in policies
    }
    selection_cache: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = {}
    scan_cache: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = {}
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
                surface_family_selected = surface_matches_policy(record, policy)
                filtered_indices = (
                    tuple(
                        index
                        for index, candidate in enumerate(candidates)
                        if candidate_matches_metadata(candidate, policy)
                    )
                    if surface_family_selected
                    else tuple()
                )
                selection = selection_for_filtered(ps, record, candidates, filtered_indices, policy_name, selection_cache)
                expensive_ops = int_value(selection.get("public_slice_motif_ops"))
                surface_screen_ops = 1
                surface_family_screen_ops = 1 if target_surface else 0
                candidate_screen_ops = len(candidates) if surface_family_selected else 0
                prefilter_total_ops = (
                    surface_screen_ops
                    + surface_family_screen_ops
                    + candidate_screen_ops
                    + expensive_ops
                )
                policy_results[policy_name]["surface_costs"].append(
                    {
                        "all_candidate_ops": int_value(all_selection.get("public_slice_motif_ops")),
                        "all_candidate_ops_over_rho": all_selection.get("public_slice_motif_ops_over_rho"),
                        "candidate_count": len(candidates),
                        "candidate_screen_ops": candidate_screen_ops,
                        "expensive_selected_ops": expensive_ops,
                        "expensive_selected_ops_over_rho": ratio(expensive_ops, rho),
                        "filtered_candidate_count": len(filtered_indices),
                        "generic_rho_steps": rho,
                        "prefilter_total_ops": prefilter_total_ops,
                        "prefilter_total_ops_over_rho": ratio(prefilter_total_ops, rho),
                        "row_key": record.get("row_key"),
                        "row_salt": p888.row_salt(record.get("row_key")),
                        "surface_family_screen_ops": surface_family_screen_ops,
                        "surface_family_selected": surface_family_selected,
                        "surface_id": surface_id,
                        "surface_screen_ops": surface_screen_ops,
                        "target": record.get("target"),
                        "transfer_index": p842.transfer_index(record),
                    }
                )
                if not p881.recovered_selection(selection):
                    continue
                filtered = [candidates[index] for index in filtered_indices]
                pairs = p881.selected_pairs(filtered)
                leaf_indices = sorted({leaf for leaf, _root in pairs})
                surface_context = surface_contexts.get(surface_id)
                if not surface_context:
                    policy_results[policy_name]["recovered_rows"].append(
                        {
                            "context_missing": True,
                            "leaf_indices": leaf_indices,
                            "row_key": record.get("row_key"),
                            "row_salt": p888.row_salt(record.get("row_key")),
                            "selection": selection,
                            "surface_id": surface_id,
                            "target": record.get("target"),
                            "transfer_index": p842.transfer_index(record),
                        }
                    )
                    continue
                scan_key = (surface_id, tuple(leaf_indices))
                if scan_key not in scan_cache:
                    scan_cache[scan_key] = direct_scan.scan_selected(
                        surface_context["verifier"],
                        surface_context["built"],
                        surface_context["components"],
                        set(leaf_indices),
                        surface_context["local_args"],
                    )
                scan = scan_cache[scan_key]
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
                        "row_salt": p888.row_salt(record.get("row_key")),
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


def policy_summary(policy: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    summary = report["summary"]
    cost = report["cost_summary"]
    cost_ratio = cost.get("prefilter_total_ops_over_sum_rho")
    return {
        "direct_below_rho_verified_context_count": int_value(summary.get("direct_below_rho_verified_context_count")),
        "family": policy.get("surface_family"),
        "filtered_candidate_count_sum": int_value(cost.get("filtered_candidate_count_sum")),
        "monomial_family": policy.get("monomial_family"),
        "motif_below_rho_verified_context_count": int_value(summary.get("motif_below_rho_verified_context_count")),
        "name": policy["name"],
        "prefilter_total_ops_over_sum_rho": cost_ratio,
        "prefilter_total_ops_sum": int_value(cost.get("prefilter_total_ops_sum")),
        "recovered_row_count": int_value(summary.get("recovered_row_count")),
        "row_public_key_verified_count": int_value(summary.get("row_public_key_verified_count")),
        "surface_family_selected_count": int_value(cost.get("surface_family_selected_count")),
        "target_context_verified_count": int_value(summary.get("target_context_verified_count")),
    }


def score_record(record: dict[str, Any]) -> tuple[Any, ...]:
    cost = record.get("prefilter_total_ops_over_sum_rho")
    cost_value = float(cost) if cost is not None else 10**9
    below_full_cost = cost is not None and cost_value < 1.0
    return (
        below_full_cost and record["motif_below_rho_verified_context_count"] > 0,
        below_full_cost and record["direct_below_rho_verified_context_count"] > 0,
        below_full_cost and record["target_context_verified_count"] > 0,
        record["motif_below_rho_verified_context_count"],
        record["target_context_verified_count"],
        record["row_public_key_verified_count"],
        record["recovered_row_count"],
        -cost_value,
        -record["surface_family_selected_count"],
    )


def select_training_policies(
    training: dict[str, Any],
    policies: list[dict[str, Any]],
    selected_policy_count: int,
    max_per_family: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_name = {policy["name"]: policy for policy in policies}
    records = [
        policy_summary(policy, training["policy_reports"][policy["name"]])
        for policy in policies
    ]
    records.sort(key=score_record, reverse=True)
    selected_records = []
    family_counts: dict[str, int] = {}
    for record in records:
        if len(selected_records) >= selected_policy_count:
            break
        cost = record.get("prefilter_total_ops_over_sum_rho")
        if cost is None or float(cost) >= 1.0:
            continue
        if record["target_context_verified_count"] <= 0:
            continue
        family = str(record["family"])
        if family_counts.get(family, 0) >= max_per_family:
            continue
        selected_records.append(record)
        family_counts[family] = family_counts.get(family, 0) + 1
    if not selected_records:
        selected_records = records[:selected_policy_count]
    selected_policies = [by_name[record["name"]] for record in selected_records]
    return selected_policies, records


def compact_phase(phase_report: dict[str, Any], policies: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "policy_reports": {
            policy["name"]: phase_report["policy_reports"][policy["name"]]
            for policy in policies
        },
        "source_reports": phase_report["source_reports"],
        "sources": phase_report["sources"],
    }


def validation_transfer_records(validation: dict[str, Any], selected_policies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        policy_summary(policy, validation["policy_reports"][policy["name"]])
        for policy in selected_policies
    ]


def determine_claim(validation_records: list[dict[str, Any]]) -> str:
    motif_transfer = [
        record
        for record in validation_records
        if record.get("prefilter_total_ops_over_sum_rho") is not None
        and float(record["prefilter_total_ops_over_sum_rho"]) < 1.0
        and record["motif_below_rho_verified_context_count"] > 0
    ]
    if motif_transfer:
        return "P889_TRAINED_PUBLIC_SCORER_TRANSFERS_MOTIF_BELOW_RHO_FULL_COST"
    direct_transfer = [
        record
        for record in validation_records
        if record.get("prefilter_total_ops_over_sum_rho") is not None
        and float(record["prefilter_total_ops_over_sum_rho"]) < 1.0
        and record["direct_below_rho_verified_context_count"] > 0
        and record["target_context_verified_count"] > 0
    ]
    if direct_transfer:
        return "P889_TRAINED_PUBLIC_SCORER_TRANSFERS_DIRECT_CONTEXT_BELOW_RHO_FULL_COST"
    target_transfer = [
        record
        for record in validation_records
        if record.get("prefilter_total_ops_over_sum_rho") is not None
        and float(record["prefilter_total_ops_over_sum_rho"]) < 1.0
        and record["target_context_verified_count"] > 0
    ]
    if target_transfer:
        return "P889_TRAINED_PUBLIC_SCORER_TRANSFERS_TARGET_CONTEXT_BELOW_FULL_COST"
    return "NEGATIVE_RESULT_P889_TRAINED_PUBLIC_SCORER_NO_VALIDATION_CONTEXT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    ps = p842.load_module("ecdlp_public_slice_for_p889", p842.PUBLIC_SLICE_SCRIPT)
    all_policies = policy_specs()
    training_sources = [Path(path) for path in (args.training_source or DEFAULT_TRAINING_SOURCES)]
    validation_sources = [Path(path) for path in (args.validation_source or DEFAULT_VALIDATION_SOURCES)]
    training_sources = training_sources[: int(args.max_training_sources)]
    validation_sources = validation_sources[: int(args.max_validation_sources)]
    training_all = evaluate_phase(
        ps,
        training_sources,
        all_policies,
        int(args.max_cases_per_source),
        int(args.max_factor_degree),
    )
    selected_policies, training_records = select_training_policies(
        training_all,
        all_policies,
        int(args.selected_policy_count),
        int(args.max_selected_per_family),
    )
    validation = evaluate_phase(
        ps,
        validation_sources,
        selected_policies,
        int(args.max_cases_per_source),
        int(args.max_factor_degree),
    )
    validation_records = validation_transfer_records(validation, selected_policies)
    p888_payload = load_json(args.p888_source) if args.p888_source.exists() else {}
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p842_source": str(args.p842_source),
            "p888_source": str(args.p888_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(validation_records),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP FFE quotient harness only.",
            "TRAIN-ONLY: selected policies are chosen from 672_711 before validating on 712_751.",
            "PUBLIC-FEATURE: scorer predicates use row/schedule and candidate metadata only.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p889_train_only_public_source_family_scorer",
        "p888_reference": {
            "claim_status": p888_payload.get("claim_status"),
            "same_policy_full_cost_transfer_policies": p888_payload.get("same_policy_full_cost_transfer_policies"),
        },
        "parameters": {
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "max_selected_per_family": int(args.max_selected_per_family),
            "policy_grid_count": len(all_policies),
            "selected_policy_count": len(selected_policies),
            "training_source_count": len(training_sources),
            "validation_source_count": len(validation_sources),
        },
        "policy_search_top": training_records[: min(len(training_records), int(args.search_summary_count))],
        "red_team_handoff": {
            "assumptions": [
                "The training slice contains enough signal to choose a reusable source-family scorer.",
                "Candidate monomial metadata can be screened before expensive selected-candidate work.",
                "A direct-context transfer is useful only as a component until motif/group accounting is reduced below rho.",
            ],
            "failure_modes": [
                "The scorer may choose a calibration-specific residue family.",
                "Validation may transfer direct context while still failing motif-below-rho group cost.",
                "The policy grid may miss features needed for rank-2 row-public-key verification.",
            ],
            "next_concrete_action": (
                "If P889 transfers direct context only, build P890 to compress or share the two-row motif cost for transfer-712-style companion rows."
            ),
        },
        "schema": SCHEMA,
        "selected_policies": selected_policies,
        "training_selected": compact_phase(training_all, selected_policies),
        "validation": validation,
        "validation_policy_summaries": validation_records,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p842-source", type=Path, default=DEFAULT_P842_SOURCE)
    parser.add_argument("--p888-source", type=Path, default=DEFAULT_P888_SOURCE)
    parser.add_argument("--training-source", type=Path, action="append")
    parser.add_argument("--validation-source", type=Path, action="append")
    parser.add_argument("--max-training-sources", type=int, default=len(DEFAULT_TRAINING_SOURCES))
    parser.add_argument("--max-validation-sources", type=int, default=len(DEFAULT_VALIDATION_SOURCES))
    parser.add_argument("--max-cases-per-source", type=int, default=0)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--selected-policy-count", type=int, default=12)
    parser.add_argument("--max-selected-per-family", type=int, default=3)
    parser.add_argument("--search-summary-count", type=int, default=80)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = {
        "claim_status": payload["claim_status"],
        "parameters": payload["parameters"],
        "selected_policies": [
            {
                "monomial_family": policy.get("monomial_family"),
                "name": policy["name"],
                "surface_family": policy.get("surface_family"),
            }
            for policy in payload["selected_policies"]
        ],
        "training_selected": {
            name: {
                "cost": report["cost_summary"],
                "summary": report["summary"],
            }
            for name, report in payload["training_selected"]["policy_reports"].items()
        },
        "validation": {
            name: {
                "cost": report["cost_summary"],
                "summary": report["summary"],
            }
            for name, report in payload["validation"]["policy_reports"].items()
        },
        "validation_policy_summaries": payload["validation_policy_summaries"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
