#!/usr/bin/env python3
"""P990 term-basis grouping audit for P989 reconstructed p231 forms."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_p989_p231_relation_independence_readiness as p989
import relation_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p990_p231_term_basis_normalization_audit.md"
DEFAULT_P984 = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
DEFAULT_P986 = STATE_DIR / "low_term_total2_p986_p231_adaptive_high_gap_guard_validation_probe.json"
DEFAULT_P988 = STATE_DIR / "low_term_total2_p988_p231_forward_high_gap_density_audit_probe.json"
DEFAULT_P989 = STATE_DIR / "low_term_total2_p989_p231_relation_independence_readiness_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p990_p231_term_basis_normalization_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p990_p231_term_basis_normalization_audit.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def round8(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round8(float(numerator) / float(denominator))


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def normalized_terms(terms: list[int]) -> list[int]:
    if not terms:
        return []
    base = min(terms)
    return [int(term) - base for term in terms]


def source_controls(p989_payload: dict[str, Any]) -> dict[str, Any]:
    summary = p989_payload.get("summary") or {}
    return {
        "p989_claim_expected": p989_payload.get("claim_status") == "NEGATIVE_RESULT_P989_RELATION_FORMS_RANK_DEFICIENT",
        "p989_control_pass": bool(summary.get("control_pass")),
        "p989_broad_cases_twelve": int_value(summary.get("broad_case_count")) == 12,
        "p989_unique_forms_44": int_value(summary.get("unique_form_count")) == 44,
        "p989_columns_17": int_value(summary.get("coefficient_column_count")) == 17,
        "p989_coeff_rank_8": int_value(summary.get("coefficient_rank_mod_order")) == 8,
        "p989_verifier_rank_8": int_value(summary.get("mixed_wide_relation_rank")) == 8,
        "p989_no_secret_derivation": not bool(summary.get("mixed_wide_relations_derive_secret")),
        "p989_term_basis_count_7": int_value(summary.get("term_basis_count")) == 7,
    }


def reconstruct_inputs(args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    p984 = load_json(Path(args.p984))
    p986 = load_json(Path(args.p986))
    p988 = load_json(Path(args.p988))
    selected = p989.broad_rows(p984, p986, p988)
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]] = {}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    reconstructed = [p989.reconstruct_case(row, build_cache, context_cache) for row in selected]
    verifier = next(iter(build_cache.values()))[0] if build_cache else None
    return selected, reconstructed, {"verifier": verifier}


def case_costs(reconstructed: list[dict[str, Any]]) -> dict[str, float]:
    return {str(case.get("case_id")): float(case.get("direct_ops_over_rho") or 0.0) for case in reconstructed}


def unique_forms(forms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for form in forms:
        by_key.setdefault(p989.form_key(form), form)
    return list(by_key.values())


def verifier_rank(forms: list[dict[str, Any]], order: int, verifier: Any) -> dict[str, Any]:
    if not forms or not order or verifier is None:
        return {"mixed_wide_relation_rank": 0, "derived_secret": None, "mixed_wide_relations_derive_secret": False}
    verifier_forms = [
        ([int_value(value) for value in form.get("coeffs") or []], int_value(form.get("rhs")), [int_value(t) for t in form.get("terms") or []])
        for form in forms
    ]
    return relation_probe.linear_rank_probe(verifier, verifier_forms, order)


def summarize_group(
    group_type: str,
    group_key: str,
    forms: list[dict[str, Any]],
    costs_by_case: dict[str, float],
    order: int,
    verifier: Any,
    baseline_rank: int,
) -> dict[str, Any]:
    forms_unique = unique_forms(forms)
    case_ids = sorted({str(form.get("case_id")) for form in forms_unique})
    direct_sum = sum(costs_by_case.get(case_id, 0.0) for case_id in case_ids)
    width = max([len(form.get("coeffs") or []) for form in forms_unique], default=0)
    coeff_matrix = [
        p989.pad([int_value(value) for value in form.get("coeffs") or []], width)
        for form in forms_unique
    ]
    rank_info = p989.rank_mod(coeff_matrix, order) if order else {"rank": 0, "nonunit_pivot_candidate_count": 0}
    verify = verifier_rank(forms_unique, order, verifier)
    rank = int_value(rank_info.get("rank"))
    return {
        "below_rho_cost": bool(case_ids and direct_sum / len(case_ids) < 1.0),
        "case_count": len(case_ids),
        "case_ids": case_ids,
        "coefficient_column_count": width,
        "coefficient_rank_mod_order": rank,
        "coefficient_rank_ratio": ratio(rank, width),
        "derived_secret": verify.get("derived_secret"),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "form_count": len(forms),
        "group_key": group_key,
        "group_type": group_type,
        "improves_baseline_rank": rank > baseline_rank or int_value(verify.get("mixed_wide_relation_rank")) > baseline_rank,
        "mixed_wide_relation_rank": verify.get("mixed_wide_relation_rank"),
        "mixed_wide_relations_derive_secret": bool(verify.get("mixed_wide_relations_derive_secret")),
        "nonunit_pivot_candidate_count": rank_info.get("nonunit_pivot_candidate_count"),
        "selected_case_amortized_ops_over_rho": ratio(direct_sum, len(case_ids)),
        "term_basis_count": len({json_key(form.get("terms") or []) for form in forms_unique}),
        "unique_form_count": len(forms_unique),
    }


def grouped_forms(all_forms: list[dict[str, Any]]) -> dict[str, dict[str, list[dict[str, Any]]]]:
    groups: dict[str, dict[str, list[dict[str, Any]]]] = {
        "exact_term_basis": {},
        "normalized_term_gap": {},
        "exact_tail_expression": {},
    }
    for form in all_forms:
        terms = [int_value(term) for term in form.get("terms") or []]
        groups["exact_term_basis"].setdefault(json_key(terms), []).append(form)
        groups["normalized_term_gap"].setdefault(json_key(normalized_terms(terms)), []).append(form)
        groups["exact_tail_expression"].setdefault(str(form.get("exact_tail_expression_key")), []).append(form)
    return groups


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p989_path = Path(args.p989)
    p989_payload = load_json(p989_path)
    controls = source_controls(p989_payload)
    control_pass = all(controls.values())
    selected, reconstructed, runtime = reconstruct_inputs(args)
    verifier = runtime.get("verifier")
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    all_unique = unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in all_unique if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = case_costs(reconstructed)
    baseline_rank = int_value((p989_payload.get("summary") or {}).get("mixed_wide_relation_rank"))
    groups = grouped_forms(all_unique)
    group_summaries: list[dict[str, Any]] = []
    for group_type, by_key in groups.items():
        for group_key, forms in by_key.items():
            group_summaries.append(
                summarize_group(group_type, group_key, forms, costs, order, verifier, baseline_rank)
            )
    group_summaries.sort(
        key=lambda row: (
            not row["mixed_wide_relations_derive_secret"],
            -int_value(row["mixed_wide_relation_rank"]),
            -int_value(row["coefficient_rank_mod_order"]),
            row["selected_case_amortized_ops_over_rho"] if row["selected_case_amortized_ops_over_rho"] is not None else 10**9,
            row["group_type"],
            row["group_key"],
        )
    )
    below_rho = [row for row in group_summaries if row["below_rho_cost"]]
    rank_improvers = [row for row in below_rho if row["improves_baseline_rank"]]
    derivations = [row for row in below_rho if row["mixed_wide_relations_derive_secret"]]
    best_normalized = [row for row in group_summaries if row["group_type"] == "normalized_term_gap"][:8]
    dominant_exact = sorted(
        [row for row in group_summaries if row["group_type"] == "exact_term_basis"],
        key=lambda row: (-int_value(row["unique_form_count"]), row["group_key"]),
    )[:8]
    success = bool(control_pass and (derivations or rank_improvers))
    if not control_pass:
        claim = "NEGATIVE_RESULT_P990_CONTROL_FAILURE"
    elif derivations:
        claim = "P990_TERM_BASIS_GROUP_DERIVES_SECRET"
    elif rank_improvers:
        claim = "P990_TERM_BASIS_GROUP_IMPROVES_RANK_BELOW_RHO"
    elif below_rho:
        claim = "NEGATIVE_RESULT_P990_BASIS_GROUPS_BELOW_RHO_BUT_NO_RANK_GAIN"
    else:
        claim = "NEGATIVE_RESULT_P990_NO_BELOW_RHO_BASIS_GROUPS"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p984_source": str(Path(args.p984)),
            "p986_source": str(Path(args.p986)),
            "p988_source": str(Path(args.p988)),
            "p989_source": str(p989_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p984_source_sha256": sha256_file(Path(args.p984)),
            "p986_source_sha256": sha256_file(Path(args.p986)),
            "p988_source_sha256": sha256_file(Path(args.p988)),
            "p989_source_sha256": sha256_file(p989_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P990_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "POST-RECONSTRUCTION-GROUPS: term-basis and exact-tail groups are normalization targets, not validated public selectors.",
            "RANK-GATE: groups must beat P989 verifier rank 8 or derive a secret to count as progress.",
            "SOURCE-COST-CHARGED: per-group cost charges every broad case contributing a form to the group.",
            "NO-END-TO-END-BREAK: target descent and public basis prediction remain open.",
        ],
        "method": "p990_p231_term_basis_normalization_audit",
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "below_rho_group_count": len(below_rho),
            "broad_case_count": len(selected),
            "control_pass": control_pass,
            "dominant_exact_term_basis": dominant_exact[0] if dominant_exact else None,
            "exact_tail_group_count": len(groups["exact_tail_expression"]),
            "exact_term_basis_group_count": len(groups["exact_term_basis"]),
            "group_rank_success": success,
            "normalized_gap_group_count": len(groups["normalized_term_gap"]),
            "rank_improving_below_rho_group_count": len(rank_improvers),
            "secret_deriving_below_rho_group_count": len(derivations),
            "term_basis_count": len(groups["exact_term_basis"]),
            "unique_form_count": len(all_unique),
        },
        "diagnostics": {
            "best_groups": group_summaries[:24],
            "best_normalized_gap_groups": best_normalized,
            "dominant_exact_term_basis_groups": dominant_exact,
            "reconstructed_case_count": len(reconstructed),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P990 contract path")
    parser.add_argument("--p984", default=str(DEFAULT_P984), help="P984 cumulative high-gap JSON")
    parser.add_argument("--p986", default=str(DEFAULT_P986), help="P986 adaptive high-gap JSON")
    parser.add_argument("--p988", default=str(DEFAULT_P988), help="P988 forward density JSON")
    parser.add_argument("--p989", default=str(DEFAULT_P989), help="P989 rank-deficiency JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    best = (payload.get("diagnostics") or {}).get("best_groups") or []
    top = best[0] if best else {}
    print(
        "claim={claim} groups={groups} below_rho={below_rho} rank_improvers={rank_improvers} "
        "derivers={derivers} top={top_type}:{top_key} top_rank={top_rank} top_verifier_rank={top_vrank} "
        "top_cost={top_cost} out={out}".format(
            claim=payload["claim_status"],
            groups=summary["exact_term_basis_group_count"] + summary["normalized_gap_group_count"] + summary["exact_tail_group_count"],
            below_rho=summary["below_rho_group_count"],
            rank_improvers=summary["rank_improving_below_rho_group_count"],
            derivers=summary["secret_deriving_below_rho_group_count"],
            top_type=top.get("group_type"),
            top_key=top.get("group_key"),
            top_rank=top.get("coefficient_rank_mod_order"),
            top_vrank=top.get("mixed_wide_relation_rank"),
            top_cost=top.get("selected_case_amortized_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
