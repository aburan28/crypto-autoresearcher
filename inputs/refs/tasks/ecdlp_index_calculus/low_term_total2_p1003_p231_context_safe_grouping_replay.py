#!/usr/bin/env python3
"""P1003 context-safe grouping replay for recent p231 hash-leaf signals."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p989_p231_relation_independence_readiness as p989
import low_term_total2_p990_p231_term_basis_normalization_audit as p990
import low_term_total2_p993_p231_branch_switch_selector_scout as p993
import low_term_total2_p998_p231_branch_ensemble_selector as p998
import low_term_total2_p999_p231_hash_basis_quality as p999
import low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order as p1000
import low_term_total2_p1001_p231_phase_shifted_hash_tuple as p1001
import low_term_total2_p1002_p231_p1001_certificate_consistency as p1002


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1003_p231_context_safe_grouping_replay.md"
DEFAULT_P998 = STATE_DIR / "low_term_total2_p998_p231_branch_ensemble_selector_probe.json"
DEFAULT_P1002 = STATE_DIR / "low_term_total2_p1002_p231_p1001_certificate_consistency_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1003_p231_context_safe_grouping_replay_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1003_p231_context_safe_grouping_replay.v1"
DEFAULT_TARGET = "22050.cf1@11731"


Predicate = Callable[[dict[str, Any]], bool]


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


def validation_examples(window: str, targets: str, min_source_rank: int) -> list[dict[str, Any]]:
    return p998.build_window_examples(window, targets, min_source_rank)


def p998_lane(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    train_windows = [window.strip() for window in p998.DEFAULT_TRAIN_WINDOWS.split(",") if window.strip()]
    training_examples, train_exists = p998.load_examples(train_windows, targets, min_source_rank)
    chosen, predicate, _scored = p998.choose_rule(training_examples)
    examples = validation_examples(p998.DEFAULT_VALIDATION_WINDOW, targets, min_source_rank)
    return [row for row in examples if predicate(row.get("features") or {})], {
        "lane": "p998_validation_branch_ensemble",
        "rule": chosen.get("name"),
        "train_exists": train_exists,
        "window": p998.DEFAULT_VALIDATION_WINDOW,
    }


def p999_lane(targets: str, min_source_rank: int, p998_payload: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    training_rows = p999.selected_training_rows(p998_payload)
    chosen, predicate, _scored = p999.choose_rule(training_rows)
    examples = p999.build_validation_examples(p999.DEFAULT_VALIDATION_WINDOW, targets, min_source_rank)
    return [row for row in examples if predicate(row.get("features") or {})], {
        "lane": "p999_validation_fixed_hash_basis",
        "rule": chosen.get("name"),
        "window": p999.DEFAULT_VALIDATION_WINDOW,
    }


def p1000_control_lane(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = p999.build_validation_examples(p1000.DEFAULT_CONTROL_WINDOW, targets, min_source_rank)
    return [row for row in examples if p1000.frozen_rule(row.get("features") or {})], {
        "lane": "p1000_control_relaxed_top7",
        "rule": "mode_hash_leaf_total6_top7_leaves_34_47_56",
        "window": p1000.DEFAULT_CONTROL_WINDOW,
    }


def p1001_control_lane(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = p999.build_validation_examples(p1001.DEFAULT_CONTROL_WINDOW, targets, min_source_rank)
    return [row for row in examples if p1001.shifted_rule(row.get("features") or {})], {
        "lane": "p1001_control_phase_tuple",
        "rule": "mode_hash_leaf_total6_top12_16_leaves_47_56_84",
        "window": p1001.DEFAULT_CONTROL_WINDOW,
    }


def p1001_validation_lane(targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    examples = p999.build_validation_examples(p1001.DEFAULT_VALIDATION_WINDOW, targets, min_source_rank)
    return [row for row in examples if p1001.shifted_rule(row.get("features") or {})], {
        "lane": "p1001_validation_phase_tuple",
        "rule": "mode_hash_leaf_total6_top12_16_leaves_47_56_84",
        "window": p1001.DEFAULT_VALIDATION_WINDOW,
    }


def reconstruct_selected(selected: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Any, dict[str, dict[str, Any]]]:
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
    return reconstructed, verifier, p1002.built_contexts(context_cache)


def group_key_for_form(group_type: str, form: dict[str, Any]) -> str:
    terms = [int_value(term) for term in form.get("terms") or []]
    if group_type == "exact_term_basis":
        return p990.json_key(terms)
    if group_type == "normalized_term_gap":
        return p990.json_key(p990.normalized_terms(terms))
    if group_type == "exact_tail_expression":
        return str(form.get("exact_tail_expression_key"))
    raise ValueError(f"unknown group_type: {group_type}")


def summarize_group(
    group_type: str,
    group_key: str,
    forms: list[dict[str, Any]],
    costs: dict[str, float],
    order: int,
    verifier: Any,
    built_by_row: dict[str, dict[str, Any]],
    baseline_rank: int,
    public_fingerprint: str | None = None,
) -> dict[str, Any]:
    summary = p990.summarize_group(group_type, group_key, forms, costs, order, verifier, baseline_rank)
    row_keys = sorted({str(form.get("row_key")) for form in p990.unique_forms(forms)})
    context = p1002.row_context_validation(row_keys, summary.get("derived_secret"), built_by_row, verifier)
    return {
        **summary,
        "context_scalar_validation": context,
        "public_fingerprint": public_fingerprint,
        "row_keys": row_keys,
    }


def unsafe_group_summaries(
    unique_forms: list[dict[str, Any]],
    costs: dict[str, float],
    order: int,
    verifier: Any,
    built_by_row: dict[str, dict[str, Any]],
    baseline_rank: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    grouped = p990.grouped_forms(unique_forms)
    for group_type, by_key in grouped.items():
        for group_key, forms in by_key.items():
            out.append(summarize_group(group_type, group_key, forms, costs, order, verifier, built_by_row, baseline_rank))
    return out


def safe_group_summaries(
    unique_forms: list[dict[str, Any]],
    costs: dict[str, float],
    order: int,
    verifier: Any,
    built_by_row: dict[str, dict[str, Any]],
    baseline_rank: int,
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for form in unique_forms:
        built = built_by_row.get(str(form.get("row_key"))) or {}
        fingerprint = p1002.public_fingerprint(built, verifier) or "missing-public-context"
        for group_type in ("exact_term_basis", "normalized_term_gap", "exact_tail_expression"):
            group_key = group_key_for_form(group_type, form)
            grouped.setdefault((group_type, group_key, fingerprint), []).append(form)
    out = []
    for (group_type, group_key, fingerprint), forms in grouped.items():
        out.append(summarize_group(group_type, group_key, forms, costs, order, verifier, built_by_row, baseline_rank, fingerprint))
    return out


def compact_group(group: dict[str, Any]) -> dict[str, Any]:
    context = group.get("context_scalar_validation") or {}
    return {
        "case_count": group.get("case_count"),
        "context_consistent_scalar_valid": context.get("context_consistent_scalar_valid"),
        "derived_secret": group.get("derived_secret"),
        "direct_sum_ops_over_rho": group.get("direct_sum_ops_over_rho"),
        "distinct_known_secrets": context.get("distinct_known_secrets"),
        "distinct_public_count": context.get("distinct_public_count"),
        "group_key": group.get("group_key"),
        "group_type": group.get("group_type"),
        "mixed_wide_relation_rank": group.get("mixed_wide_relation_rank"),
        "mixed_wide_relations_derive_secret": group.get("mixed_wide_relations_derive_secret"),
        "public_fingerprint": group.get("public_fingerprint"),
        "row_keys": group.get("row_keys"),
        "selected_case_amortized_ops_over_rho": group.get("selected_case_amortized_ops_over_rho"),
    }


def analyze_lane(selected: list[dict[str, Any]], metadata: dict[str, Any], baseline_rank: int) -> dict[str, Any]:
    reconstructed, verifier, built_by_row = reconstruct_selected(selected)
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    unique_forms = p990.unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in unique_forms if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = p990.case_costs(reconstructed)
    unsafe = unsafe_group_summaries(unique_forms, costs, order, verifier, built_by_row, baseline_rank) if unique_forms else []
    safe = safe_group_summaries(unique_forms, costs, order, verifier, built_by_row, baseline_rank) if unique_forms else []
    unsafe_derivers = [row for row in unsafe if row.get("mixed_wide_relations_derive_secret")]
    safe_derivers = [row for row in safe if row.get("mixed_wide_relations_derive_secret")]
    scalar_valid = [row for row in safe_derivers if (row.get("context_scalar_validation") or {}).get("context_consistent_scalar_valid")]
    cross_context_unsafe = [
        row
        for row in unsafe_derivers
        if int_value((row.get("context_scalar_validation") or {}).get("distinct_public_count")) > 1
    ]
    selected_positive = [row for row in selected if row.get("label_positive")]
    selected_source_verified = [row for row in selected if (row.get("source_case") or {}).get("source_public_key_verified")]
    return {
        "diagnostics": {
            "best_context_safe_groups": [compact_group(row) for row in sorted(safe, key=group_sort_key)[:12]],
            "best_unsafe_groups": [compact_group(row) for row in sorted(unsafe, key=group_sort_key)[:12]],
            "reconstructed_cases": [p1002.reconstructed_case_summary(row) for row in reconstructed],
            "selected_cases": [p1002.source_case_summary(row) for row in selected],
        },
        "metadata": metadata,
        "summary": {
            "context_safe_group_count": len(safe),
            "context_safe_scalar_valid_group_count": len(scalar_valid),
            "context_safe_syntactic_deriving_group_count": len(safe_derivers),
            "cross_context_unsafe_deriving_group_count": len(cross_context_unsafe),
            "form_order": order or None,
            "raw_form_count": len(all_forms),
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed),
            "scalar_valid_best_amortized_ops_over_rho": min(
                [
                    float(row.get("selected_case_amortized_ops_over_rho"))
                    for row in scalar_valid
                    if row.get("selected_case_amortized_ops_over_rho") is not None
                ],
                default=None,
            ),
            "selected_count": len(selected),
            "selected_direct_sum_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
            "selected_source_positive_count": len(selected_positive),
            "selected_source_public_key_verified_count": len(selected_source_verified),
            "unique_form_count": len(unique_forms),
            "unsafe_group_count": len(unsafe),
            "unsafe_syntactic_deriving_group_count": len(unsafe_derivers),
        },
    }


def group_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    context = row.get("context_scalar_validation") or {}
    return (
        not context.get("context_consistent_scalar_valid"),
        not row.get("mixed_wide_relations_derive_secret"),
        row.get("selected_case_amortized_ops_over_rho")
        if row.get("selected_case_amortized_ops_over_rho") is not None
        else 10**9,
        row.get("group_type"),
        row.get("group_key"),
        row.get("public_fingerprint") or "",
    )


def determine_claim(control_pass: bool, lane_results: list[dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P1003_P1002_CONTROL_FAILURE"
    scalar_valid = sum(int_value((row.get("summary") or {}).get("context_safe_scalar_valid_group_count")) for row in lane_results)
    unsafe_derivers = sum(int_value((row.get("summary") or {}).get("unsafe_syntactic_deriving_group_count")) for row in lane_results)
    if scalar_valid:
        return "P1003_CONTEXT_SAFE_SCALAR_VALID_GROUP_SURVIVES"
    if unsafe_derivers:
        return "NEGATIVE_RESULT_P1003_CONTEXT_SAFE_GATE_REJECTS_PRIOR_SYNTACTIC_DERIVATIONS"
    return "NEGATIVE_RESULT_P1003_NO_SYNTACTIC_DERIVATIONS_IN_REPLAY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p998_payload = load_json(Path(args.p998))
    p1002_payload = load_json(Path(args.p1002))
    control_pass = p1002_payload.get("claim_status") == "NEGATIVE_RESULT_P1002_P1001_CROSS_CHALLENGE_SYNTACTIC_DERIVATION"
    lanes = [
        p998_lane(args.targets, args.min_source_rank),
        p999_lane(args.targets, args.min_source_rank, p998_payload),
        p1000_control_lane(args.targets, args.min_source_rank),
        p1001_control_lane(args.targets, args.min_source_rank),
        p1001_validation_lane(args.targets, args.min_source_rank),
    ]
    lane_results = [analyze_lane(selected, metadata, args.baseline_rank) for selected, metadata in lanes]
    claim = determine_claim(control_pass, lane_results)
    total_scalar_valid = sum(int_value((row.get("summary") or {}).get("context_safe_scalar_valid_group_count")) for row in lane_results)
    total_unsafe_derivers = sum(int_value((row.get("summary") or {}).get("unsafe_syntactic_deriving_group_count")) for row in lane_results)
    total_safe_derivers = sum(int_value((row.get("summary") or {}).get("context_safe_syntactic_deriving_group_count")) for row in lane_results)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p998_source": str(args.p998),
            "p1002_source": str(args.p1002),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p998_source_sha256": sha256_file(Path(args.p998)),
            "p1002_source_sha256": sha256_file(Path(args.p1002)),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1003_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CONTEXT-SAFE-GATE: groups spanning multiple public fingerprints are rejected before scalar claims.",
            "SCALAR-VALID-GATE: a candidate must satisfy candidate*base == public to count as recovery evidence.",
            "NO-END-TO-END-BREAK: this is a replay/hardening audit, not a full relation collection and target-descent algorithm.",
        ],
        "lane_results": lane_results,
        "method": "p1003_p231_context_safe_grouping_replay",
        "parameters": {
            "baseline_rank": args.baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "p1002_control": {
            "claim_status": p1002_payload.get("claim_status"),
            "summary": p1002_payload.get("summary"),
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "control_pass": control_pass,
            "lane_count": len(lane_results),
            "lane_summaries": {row["metadata"]["lane"]: row["summary"] for row in lane_results},
            "total_context_safe_scalar_valid_group_count": total_scalar_valid,
            "total_context_safe_syntactic_deriving_group_count": total_safe_derivers,
            "total_unsafe_syntactic_deriving_group_count": total_unsafe_derivers,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-rank", type=int, default=8, help="Rank baseline for group summaries")
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1003 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p998", default=str(DEFAULT_P998), help="P998 source JSON")
    parser.add_argument("--p1002", default=str(DEFAULT_P1002), help="P1002 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} lanes={lanes} unsafe_derivers={unsafe} safe_derivers={safe} "
        "scalar_valid={valid} out={out}".format(
            claim=payload["claim_status"],
            lanes=summary["lane_count"],
            unsafe=summary["total_unsafe_syntactic_deriving_group_count"],
            safe=summary["total_context_safe_syntactic_deriving_group_count"],
            valid=summary["total_context_safe_scalar_valid_group_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
