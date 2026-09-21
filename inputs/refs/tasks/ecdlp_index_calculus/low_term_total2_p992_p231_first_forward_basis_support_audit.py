#!/usr/bin/env python3
"""P992 first-forward support audit for the P990 p231 term-basis signal."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p870_p231_public_rule_materialization as p870
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_p989_p231_relation_independence_readiness as p989
import low_term_total2_p990_p231_term_basis_normalization_audit as p990


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p992_p231_first_forward_basis_support_audit.md"
DEFAULT_P990 = STATE_DIR / "low_term_total2_p990_p231_term_basis_normalization_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p992_p231_first_forward_basis_support_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p992_p231_first_forward_basis_support_audit.v1"
DEFAULT_WINDOWS = ("11904_11911",)
DEFAULT_TARGET = "22050.cf1@11731"
TARGET_TERM_BASIS = "[3,3,5,5]"
TARGET_EXACT_TAIL = "{\"tail_coeffs\":[11777,11777],\"tail_support\":[4,6],\"terms\":[3,3,5,5]}"


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


def compact_form(form: dict[str, Any]) -> dict[str, Any]:
    return p989.compact_form(form)


def p990_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    best = (payload.get("diagnostics") or {}).get("best_groups") or []
    basis = next(
        (
            row
            for row in best
            if row.get("group_type") == "exact_term_basis" and row.get("group_key") == TARGET_TERM_BASIS
        ),
        None,
    )
    tail = next(
        (
            row
            for row in best
            if row.get("group_type") == "exact_tail_expression" and row.get("group_key") == TARGET_EXACT_TAIL
        ),
        None,
    )
    return {
        "p990_claim_expected": payload.get("claim_status") == "P990_TERM_BASIS_GROUP_DERIVES_SECRET",
        "p990_control_pass": bool(summary.get("control_pass")),
        "p990_target_basis_present": bool(basis),
        "p990_target_basis_derives": bool(basis and basis.get("mixed_wide_relations_derive_secret")),
        "p990_target_tail_present": bool(tail),
        "p990_target_tail_derives": bool(tail and tail.get("mixed_wide_relations_derive_secret")),
        "p990_target_tail_secret_expected": tail is not None and int_value(tail.get("derived_secret")) == 8377,
    }


def build_window_runtime(
    window: str,
    build_cache: dict[str, tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]],
) -> tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace]:
    source = p868.load_json(p868.source_path(window))
    params = p868.repair_probe.source_parameters(source)
    probe_args = p868.repair_probe.probe_args_from_source(source)
    cache_key = p868.json_key(
        {
            "bank_source": params.get("bank_source"),
            "config_source": params.get("config_source"),
            "direct_source": params.get("direct_source"),
            "radius": params.get("radius"),
            "transfer_source": params.get("transfer_source"),
        }
    )
    if cache_key not in build_cache:
        build_cache[cache_key] = (*p868.repair_probe.build_specs(params), probe_args)
    return build_cache[cache_key]


def scan_windows(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.windows)
    missing = [window for window in windows if not p868.source_path(window).exists()]
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    counts: dict[str, Counter[str]] = {
        "source": Counter(),
        "first_stage": Counter(),
        "second_stage": Counter(),
        "high_gap": Counter(),
    }
    reconstructed: list[dict[str, Any]] = []

    for window in [window for window in windows if window not in missing]:
        source = p868.load_json(p868.source_path(window))
        verifier, records, config_source, specs_by_target, probe_args = build_window_runtime(window, build_cache)
        for case in p868.iter_source_cases(source, window, targets):
            counts["source"][window] += 1
            context = p868.hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            features = p869.public_features(case, context)
            if not p870.frozen_rule(features):
                continue
            counts["first_stage"][window] += 1
            if not p872.second_stage_rule(features):
                continue
            counts["second_stage"][window] += 1
            if not p985.high_gap_rule(features):
                continue
            counts["high_gap"][window] += 1
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            compact = p872.compact_selected_case(labeled, features)
            rec = p989.reconstruct_case(compact, build_cache, context_cache)
            rec["direct_ops_over_rho"] = compact.get("direct_ops_over_rho")
            rec["public_features"] = compact.get("public_features")
            rec["source_policy"] = case.get("source_policy")
            rec["source_below_rho"] = case.get("source_below_rho")
            rec["source_public_key_verified"] = case.get("source_public_key_verified")
            reconstructed.append(rec)

    verifier = next(iter(build_cache.values()))[0] if build_cache else None
    scan_summary = {
        "available_window_count": len(windows) - len(missing),
        "available_windows": [window for window in windows if window not in missing],
        "first_stage_selected_case_count": sum(counts["first_stage"].values()),
        "first_stage_selected_count_by_window": dict(counts["first_stage"]),
        "high_gap_selected_case_count": sum(counts["high_gap"].values()),
        "high_gap_selected_count_by_window": dict(counts["high_gap"]),
        "missing_window_count": len(missing),
        "missing_windows": missing,
        "second_stage_selected_case_count": sum(counts["second_stage"].values()),
        "second_stage_selected_count_by_window": dict(counts["second_stage"]),
        "source_case_count": sum(counts["source"].values()),
        "source_count_by_window": dict(counts["source"]),
        "source_windows": {
            window: str(p868.source_path(window)) for window in windows if window not in missing
        },
    }
    return reconstructed, scan_summary, {"verifier": verifier}


def summarize_groups(reconstructed: list[dict[str, Any]], verifier: Any, baseline_rank: int) -> dict[str, Any]:
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    unique = p990.unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in unique if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = {
        str(case.get("case_id")): float(case.get("direct_ops_over_rho") or 0.0)
        for case in reconstructed
    }
    groups = p990.grouped_forms(unique)
    summaries: list[dict[str, Any]] = []
    if order:
        for group_type, by_key in groups.items():
            for group_key, forms in by_key.items():
                summaries.append(
                    p990.summarize_group(group_type, group_key, forms, costs, order, verifier, baseline_rank)
                )
    summaries.sort(
        key=lambda row: (
            not row.get("mixed_wide_relations_derive_secret"),
            row.get("selected_case_amortized_ops_over_rho")
            if row.get("selected_case_amortized_ops_over_rho") is not None
            else 10**9,
            row.get("group_type"),
            row.get("group_key"),
        )
    )
    target_basis = next(
        (
            row
            for row in summaries
            if row.get("group_type") == "exact_term_basis" and row.get("group_key") == TARGET_TERM_BASIS
        ),
        None,
    )
    target_tail = next(
        (
            row
            for row in summaries
            if row.get("group_type") == "exact_tail_expression" and row.get("group_key") == TARGET_EXACT_TAIL
        ),
        None,
    )
    basis_forms = [
        form
        for form in unique
        if p990.json_key([int_value(term) for term in form.get("terms") or []]) == TARGET_TERM_BASIS
    ]
    tail_forms = [form for form in unique if str(form.get("exact_tail_expression_key")) == TARGET_EXACT_TAIL]
    return {
        "all_group_summaries": summaries,
        "best_groups": summaries[:16],
        "exact_tail_group_count": len(groups.get("exact_tail_expression") or {}),
        "exact_term_basis_group_count": len(groups.get("exact_term_basis") or {}),
        "form_order": order or None,
        "form_order_count": len(orders),
        "raw_form_count": len(all_forms),
        "secret_deriving_group_count": sum(1 for row in summaries if row.get("mixed_wide_relations_derive_secret")),
        "target_basis": target_basis,
        "target_basis_forms_sample": [compact_form(form) for form in basis_forms[:16]],
        "target_exact_tail": target_tail,
        "target_exact_tail_forms_sample": [compact_form(form) for form in tail_forms[:16]],
        "unique_form_count": len(unique),
    }


def determine_claim(control_pass: bool, scan: dict[str, Any], groups: dict[str, Any], reconstruction_errors: int) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P992_CONTROL_FAILURE"
    if int_value(scan.get("missing_window_count")):
        return "NEGATIVE_RESULT_P992_FORWARD_SOURCE_WINDOWS_MISSING"
    if int_value(scan.get("high_gap_selected_case_count")) == 0:
        return "NEGATIVE_RESULT_P992_NO_FORWARD_HIGH_GAP_ROWS"
    if reconstruction_errors:
        return "NEGATIVE_RESULT_P992_RECONSTRUCTION_ERRORS"
    target_tail = groups.get("target_exact_tail") or {}
    target_basis = groups.get("target_basis") or {}
    if target_tail.get("mixed_wide_relations_derive_secret"):
        return "P992_FORWARD_TARGET_TAIL_DERIVES_SECRET"
    if target_basis.get("mixed_wide_relations_derive_secret"):
        return "P992_FORWARD_TARGET_BASIS_DERIVES_SECRET"
    if target_tail:
        return "P992_FORWARD_TARGET_TAIL_REAPPEARS"
    if target_basis:
        return "P992_FORWARD_TARGET_BASIS_REAPPEARS"
    return "NEGATIVE_RESULT_P992_TARGET_BASIS_NOT_OBSERVED_IN_FIRST_FORWARD_WINDOW"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p990_path = Path(args.p990)
    p990_payload = load_json(p990_path)
    controls = p990_controls(p990_payload)
    control_pass = all(controls.values())
    reconstructed, scan_summary, runtime = scan_windows(args)
    baseline_rank = int_value((p990_payload.get("summary") or {}).get("baseline_mixed_wide_relation_rank"))
    groups = summarize_groups(reconstructed, runtime.get("verifier"), baseline_rank)
    reconstruction_errors = sum(int_value(case.get("reconstructed_error_count")) for case in reconstructed)
    claim = determine_claim(control_pass, scan_summary, groups, reconstruction_errors)
    case_rank_hist = Counter(str(case.get("union_rank")) for case in reconstructed)
    target_basis = groups.get("target_basis") or {}
    target_tail = groups.get("target_exact_tail") or {}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p990_source": str(p990_path),
            "script": str(Path(__file__)),
            "source_windows": scan_summary.get("source_windows"),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p990_source_sha256": sha256_file(p990_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": {
                window: sha256_file(p868.source_path(window)) for window in args.windows
            },
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P992_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "diagnostics": {
            "best_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "reconstructed_cases": [
                {
                    "case_id": case.get("case_id"),
                    "direct_ops_over_rho": case.get("direct_ops_over_rho"),
                    "form_count": len(case.get("form_records") or []),
                    "public_features": case.get("public_features"),
                    "reconstructed_error_count": case.get("reconstructed_error_count"),
                    "transfer_index": case.get("transfer_index"),
                    "union_public_key_verified": case.get("union_public_key_verified"),
                    "union_rank": case.get("union_rank"),
                    "union_relation_count": case.get("union_relation_count"),
                    "window": case.get("window"),
                }
                for case in reconstructed
            ],
            "target_basis_forms_sample": groups["target_basis_forms_sample"],
            "target_exact_tail_forms_sample": groups["target_exact_tail_forms_sample"],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PUBLIC-SELECTION: rows are selected by P870/P872/P985 public high-gap rules before reconstruction.",
            "POST-RECONSTRUCTION-LABEL: term-basis and exact-tail labels are measured only after selected rows are reconstructed.",
            "SINGLE-FRESH-WINDOW: this is first-forward support evidence, not an asymptotic claim.",
            "NO-END-TO-END-BREAK: sparse linear algebra, target descent, and cryptographic-scale transfer remain open.",
        ],
        "method": "p992_p231_first_forward_basis_support_audit",
        "parameters": {
            "baseline_rank": baseline_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "target_exact_tail": TARGET_EXACT_TAIL,
            "target_term_basis": TARGET_TERM_BASIS,
            "windows": list(args.windows),
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            **scan_summary,
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "control_pass": control_pass,
            "exact_tail_group_count": groups["exact_tail_group_count"],
            "exact_term_basis_group_count": groups["exact_term_basis_group_count"],
            "form_order": groups["form_order"],
            "form_order_count": groups["form_order_count"],
            "raw_form_count": groups["raw_form_count"],
            "reconstructed_case_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_errors,
            "secret_deriving_group_count": groups["secret_deriving_group_count"],
            "target_basis_case_count": target_basis.get("case_count"),
            "target_basis_direct_sum_ops_over_rho": target_basis.get("direct_sum_ops_over_rho"),
            "target_basis_mixed_wide_relation_rank": target_basis.get("mixed_wide_relation_rank"),
            "target_basis_present": bool(target_basis),
            "target_basis_secret_derivation": bool(target_basis.get("mixed_wide_relations_derive_secret")),
            "target_exact_tail_case_count": target_tail.get("case_count"),
            "target_exact_tail_direct_sum_ops_over_rho": target_tail.get("direct_sum_ops_over_rho"),
            "target_exact_tail_mixed_wide_relation_rank": target_tail.get("mixed_wide_relation_rank"),
            "target_exact_tail_present": bool(target_tail),
            "target_exact_tail_secret_derivation": bool(target_tail.get("mixed_wide_relations_derive_secret")),
            "unique_form_count": groups["unique_form_count"],
        },
        "target_groups": {
            "exact_term_basis": target_basis or None,
            "exact_tail_expression": target_tail or None,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P992 contract path")
    parser.add_argument("--p990", default=str(DEFAULT_P990), help="P990 term-basis source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS), help="p231 source windows")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} windows={windows} source={source} high_gap={high_gap} "
        "cases={cases} forms={forms} target_basis={basis} target_tail={tail} "
        "tail_derives={tail_derives} out={out}".format(
            claim=payload["claim_status"],
            windows=",".join(args.windows),
            source=summary["source_case_count"],
            high_gap=summary["high_gap_selected_case_count"],
            cases=summary["reconstructed_case_count"],
            forms=summary["unique_form_count"],
            basis=summary["target_basis_present"],
            tail=summary["target_exact_tail_present"],
            tail_derives=summary["target_exact_tail_secret_derivation"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
