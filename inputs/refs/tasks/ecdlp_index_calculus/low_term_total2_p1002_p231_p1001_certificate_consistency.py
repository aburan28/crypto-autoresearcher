#!/usr/bin/env python3
"""P1002 certificate consistency audit for the P1001 p231 phase-hash signal."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p989_p231_relation_independence_readiness as p989
import low_term_total2_p990_p231_term_basis_normalization_audit as p990
import low_term_total2_p993_p231_branch_switch_selector_scout as p993
import low_term_total2_p996_p231_early_stop_recall_split as p996
import low_term_total2_p1001_p231_phase_shifted_hash_tuple as p1001


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1002_p231_p1001_certificate_consistency.md"
DEFAULT_P1001 = STATE_DIR / "low_term_total2_p1001_p231_phase_shifted_hash_tuple_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1002_p231_p1001_certificate_consistency_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1002_p231_p1001_certificate_consistency.v1"
DEFAULT_WINDOW = "11960_11967"
DEFAULT_TARGET = "22050.cf1@11731"


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


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def selected_ops(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0)


def build_selected(
    window: str,
    targets: str,
    min_source_rank: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], Any, dict[str, dict[str, Any]]]:
    args = argparse.Namespace(
        min_source_rank=min_source_rank,
        targets=targets,
        train_transfer_max=-1,
        window=window,
    )
    examples = p993.build_examples(args)
    selected = [row for row in examples if p1001.shifted_rule(row.get("features") or {})]
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    reconstructed = [
        p989.reconstruct_case(p993.row_for_reconstruction(example), build_cache, context_cache)
        for example in selected
    ]
    verifier = next(iter(build_cache.values()))[0] if build_cache else None
    built_by_row = built_contexts(context_cache)
    return selected, reconstructed, verifier, built_by_row


def built_contexts(context_cache: dict[Any, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    built_by_row: dict[str, dict[str, Any]] = {}
    for context in context_cache.values():
        for row_key, built in (context.get("built_by_row") or {}).items():
            if built:
                built_by_row[str(row_key)] = built
    return built_by_row


def source_case_summary(example: dict[str, Any]) -> dict[str, Any]:
    case = example.get("source_case") or {}
    features = example.get("features") or {}
    return {
        "case_id": example.get("case_id"),
        "label_positive": example.get("label_positive"),
        "leaf_gap_tuple": features.get("leaf_gap_tuple"),
        "row_key_signature": p996.row_key_signature(example),
        "salt_gap": features.get("salt_gap"),
        "source_below_rho": case.get("source_below_rho"),
        "source_ops_over_rho": case.get("source_ops_over_rho"),
        "source_public_key_verified": case.get("source_public_key_verified"),
        "source_rank": case.get("source_rank"),
        "top_k": features.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unique_leaf_indices": features.get("unique_leaf_indices"),
    }


def reconstructed_case_summary(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "local_derivation_count": case.get("local_derivation_count"),
        "local_matched_derivation_count": case.get("local_matched_derivation_count"),
        "order": case.get("order"),
        "reconstructed_error_count": case.get("reconstructed_error_count"),
        "relation_form_count": case.get("relation_form_count"),
        "row_scans": case.get("row_scans"),
        "transfer_index": case.get("transfer_index"),
        "union_derived_secret": case.get("union_derived_secret"),
        "union_public_key_verified": case.get("union_public_key_verified"),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
    }


def scalar_validation(candidate: Any, built: dict[str, Any], verifier: Any) -> dict[str, Any]:
    order = int_value(built.get("order"))
    if candidate is None or not built or verifier is None or not order:
        return {
            "candidate": candidate,
            "candidate_matches_known_secret": False,
            "scalar_valid": False,
        }
    candidate_int = int_value(candidate) % order
    candidate_public = verifier.mul_point(candidate_int, built["base"], built["ainvs"], built["p"])
    scalar_valid = candidate_public == built["public"]
    known_secret = built.get("secret")
    return {
        "candidate": candidate_int,
        "candidate_matches_known_secret": known_secret is not None and candidate_int == int_value(known_secret) % order,
        "candidate_public": verifier.point_to_json(candidate_public),
        "challenge_public": verifier.point_to_json(built["public"]),
        "known_secret": known_secret,
        "order": order,
        "p": built.get("p"),
        "scalar_valid": bool(scalar_valid),
        "target": built.get("target"),
    }


def public_fingerprint(built: dict[str, Any], verifier: Any) -> str | None:
    if not built or verifier is None:
        return None
    return json.dumps(
        {
            "p": built.get("p"),
            "public": verifier.point_to_json(built["public"]),
            "target": built.get("target"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )


def row_context_validation(row_keys: list[str], candidate: Any, built_by_row: dict[str, dict[str, Any]], verifier: Any) -> dict[str, Any]:
    contexts = []
    for row_key in row_keys:
        built = built_by_row.get(str(row_key)) or {}
        validation = scalar_validation(candidate, built, verifier)
        contexts.append(
            {
                **validation,
                "public_fingerprint": public_fingerprint(built, verifier),
                "row_key": row_key,
            }
        )
    public_fingerprints = sorted({str(row.get("public_fingerprint")) for row in contexts if row.get("public_fingerprint")})
    known_secrets = sorted({int_value(row.get("known_secret")) for row in contexts if row.get("known_secret") is not None})
    scalar_valid_count = sum(1 for row in contexts if row.get("scalar_valid"))
    return {
        "all_row_keys_scalar_valid": bool(contexts and scalar_valid_count == len(contexts)),
        "any_row_key_scalar_valid": bool(scalar_valid_count),
        "context_consistent_scalar_valid": bool(len(public_fingerprints) == 1 and contexts and scalar_valid_count == len(contexts)),
        "distinct_known_secret_count": len(known_secrets),
        "distinct_known_secrets": known_secrets,
        "distinct_public_count": len(public_fingerprints),
        "public_fingerprints": public_fingerprints,
        "row_contexts": contexts,
        "row_key_count": len(contexts),
        "scalar_valid_row_key_count": scalar_valid_count,
    }


def group_forms(
    reconstructed: list[dict[str, Any]],
    verifier: Any,
    built_by_row: dict[str, dict[str, Any]],
    baseline_rank: int,
) -> list[dict[str, Any]]:
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    unique_forms = p990.unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in unique_forms if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = p990.case_costs(reconstructed)
    grouped = p990.grouped_forms(unique_forms)
    summaries: list[dict[str, Any]] = []
    for group_type, by_key in grouped.items():
        for group_key, forms in by_key.items():
            summary = p990.summarize_group(group_type, group_key, forms, costs, order, verifier, baseline_rank)
            if not summary.get("mixed_wide_relations_derive_secret"):
                continue
            forms_unique = p990.unique_forms(forms)
            candidate = summary.get("derived_secret")
            candidate_derivations = p868.local_derivations(forms_unique, candidate, order) if order else []
            row_keys = sorted({str(form.get("row_key")) for form in forms_unique})
            context_validation = row_context_validation(row_keys, candidate, built_by_row, verifier)
            summaries.append(
                {
                    **summary,
                    "candidate_tail_derivations": candidate_derivations,
                    "context_scalar_validation": context_validation,
                    "forms": [p868.compact_form(form) for form in forms_unique],
                    "scalar_valid_tail_derivation_count": sum(
                        1
                        for row in candidate_derivations
                        if row_context_validation(row.get("row_keys") or [], row.get("candidate_secret"), built_by_row, verifier).get(
                            "context_consistent_scalar_valid"
                        )
                    ),
                }
            )
    summaries.sort(
        key=lambda row: (
            not (row.get("context_scalar_validation") or {}).get("context_consistent_scalar_valid"),
            row.get("selected_case_amortized_ops_over_rho")
            if row.get("selected_case_amortized_ops_over_rho") is not None
            else 10**9,
            row.get("group_type"),
            row.get("group_key"),
        )
    )
    return summaries


def determine_claim(control_pass: bool, selected: list[dict[str, Any]], reconstructed: list[dict[str, Any]], groups: list[dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1002_P1001_CONTROL_FAILURE"
    if not selected:
        return "NEGATIVE_RESULT_P1002_NO_SELECTED_ROWS"
    if sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed):
        return "NEGATIVE_RESULT_P1002_RECONSTRUCTION_ERRORS"
    if not groups:
        return "NEGATIVE_RESULT_P1002_NO_SYNTACTIC_DERIVATION_TO_AUDIT"
    if any((group.get("context_scalar_validation") or {}).get("context_consistent_scalar_valid") for group in groups):
        return "P1002_P1001_DERIVATION_SCALAR_VALID"
    if any((group.get("context_scalar_validation") or {}).get("distinct_public_count", 0) > 1 for group in groups):
        return "NEGATIVE_RESULT_P1002_P1001_CROSS_CHALLENGE_SYNTACTIC_DERIVATION"
    return "NEGATIVE_RESULT_P1002_P1001_SYNTACTIC_DERIVATION_NOT_SCALAR_VALID"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p1001_path = Path(args.p1001)
    p1001_payload = load_json(p1001_path)
    p1001_summary = p1001_payload.get("summary") or {}
    control_pass = (
        p1001_payload.get("claim_status") == "P1001_PHASE_HASH_SALT_FIRST_DERIVATION_BELOW_RHO"
        and bool(p1001_summary.get("control_pass"))
        and ((p1001_summary.get("validation") or {}).get("secret_deriving_group_count") or 0) > 0
    )
    selected, reconstructed, verifier, built_by_row = build_selected(args.window, args.targets, args.min_source_rank)
    groups = group_forms(reconstructed, verifier, built_by_row, args.baseline_rank)
    scalar_valid_groups = [
        group for group in groups if (group.get("context_scalar_validation") or {}).get("context_consistent_scalar_valid")
    ]
    claim = determine_claim(control_pass, selected, reconstructed, groups)
    selected_source_positive = [row for row in selected if row.get("label_positive")]
    source_verified = [row for row in selected if (row.get("source_case") or {}).get("source_public_key_verified")]
    union_verified = [row for row in reconstructed if row.get("union_public_key_verified")]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1001_source": str(p1001_path),
            "script": str(Path(__file__)),
            "source_window": str(p868.source_path(args.window)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p1001_source_sha256": sha256_file(p1001_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(p868.source_path(args.window)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1002_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SYNTACTIC-LINEAR-SYSTEM BOUNDARY: derive_secret_from_relations only solves the relation matrix; P1002 separately checks scalar*base == public.",
            "SOURCE-LABEL BOUNDARY: direct source verification and reconstructed group verification are distinct checks.",
            "NO-END-TO-END-BREAK: a scalar-invalid syntactic derivation is not a discrete-log recovery.",
        ],
        "method": "p1002_p231_p1001_certificate_consistency",
        "p1001_reference": {
            "claim_status": p1001_payload.get("claim_status"),
            "summary": p1001_summary,
        },
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "schema": SCHEMA,
        "summary": {
            "candidate_group_count": len(groups),
            "claim_status": claim,
            "control_pass": control_pass,
            "context_distinct_known_secrets": sorted(
                {
                    secret
                    for group in groups
                    for secret in ((group.get("context_scalar_validation") or {}).get("distinct_known_secrets") or [])
                }
            ),
            "context_distinct_public_count_max": max(
                [int_value((group.get("context_scalar_validation") or {}).get("distinct_public_count")) for group in groups],
                default=0,
            ),
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed),
            "scalar_valid_group_count": len(scalar_valid_groups),
            "selected_count": len(selected),
            "selected_direct_sum_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
            "selected_source_positive_count": len(selected_source_positive),
            "source_public_key_verified_selected_count": len(source_verified),
            "syntactic_candidate_secrets": sorted({int_value(group.get("derived_secret")) for group in groups}),
            "union_public_key_verified_reconstructed_count": len(union_verified),
        },
        "diagnostics": {
            "mixed_wide_deriving_groups": groups,
            "reconstructed_cases": [reconstructed_case_summary(row) for row in reconstructed],
            "selected_cases": [source_case_summary(row) for row in selected],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1002 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1001", default=str(DEFAULT_P1001), help="P1001 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="P1001 validation window")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} syntactic_groups={groups} scalar_valid_groups={valid} "
        "context_secrets={secrets} max_publics={publics} candidates={candidates} "
        "source_verified={source_verified} union_verified={union_verified} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            groups=summary["candidate_group_count"],
            valid=summary["scalar_valid_group_count"],
            secrets=summary["context_distinct_known_secrets"],
            publics=summary["context_distinct_public_count_max"],
            candidates=summary["syntactic_candidate_secrets"],
            source_verified=summary["source_public_key_verified_selected_count"],
            union_verified=summary["union_public_key_verified_reconstructed_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
