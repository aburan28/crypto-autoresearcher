#!/usr/bin/env python3
"""P980 frozen validation of the high-gap p231 public refinement."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p870_p231_public_rule_materialization as p870
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p980_p231_high_gap_frozen_refinement.md"
DEFAULT_P979 = STATE_DIR / "low_term_total2_p979_p231_frozen_public_gate_validation_probe.json"
DEFAULT_WINDOWS = (
    "11400_11407",
    "11408_11415",
    "11416_11423",
    "11424_11431",
    "11432_11439",
    "11440_11447",
    "11448_11455",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p980_p231_high_gap_frozen_refinement_probe.json"
SCHEMA = "ecdlp.low_term_total2_p980_p231_high_gap_frozen_refinement.v1"
THIRD_STAGE_RULE = "top_k == 4 AND salt_gap >= 6"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
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


def third_stage_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) == 4 and int_value(features.get("salt_gap"), -1) >= 6


def source_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    public = case.get("public_features") or {}
    row_salts = []
    for row_leaf in case.get("row_leaf_keys") or []:
        row_key = str(row_leaf.get("row_key"))
        if "salt" in row_key:
            row_salts.append(int_value(row_key.rsplit("salt", 1)[-1]))
    return (
        public.get("window") or case.get("window"),
        int_value(public.get("transfer_index"), int_value(case.get("transfer_index"))),
        case.get("target"),
        public.get("leaf_selector") or case.get("leaf_selector"),
        tuple(sorted(row_salts)),
    )


def relation_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("union_derived_secret"),
        json.dumps(case.get("row_leaf_keys") or [], sort_keys=True),
    )


def summarize_selected(selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_sum = sum(float_value(case.get("direct_ops_over_rho")) for case in selected_cases)
    p867 = [case for case in selected_cases if case.get("p867_motif_verified_below_rho")]
    union_verified = [case for case in selected_cases if case.get("union_public_key_verified")]
    p867_relation_groups = {relation_group_key(case) for case in p867}
    union_relation_groups = {relation_group_key(case) for case in union_verified}
    source_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for case in selected_cases:
        source_groups.setdefault(source_group_key(case), []).append(case)
    cached_sum = sum(
        max(float_value(case.get("direct_ops_over_rho")) for case in group)
        for group in source_groups.values()
    )
    p867_source_groups = sum(
        1 for group in source_groups.values() if any(case.get("p867_motif_verified_below_rho") for case in group)
    )
    ranks = Counter(str(case.get("union_rank")) for case in selected_cases)
    salt_gaps = Counter(str((case.get("public_features") or {}).get("salt_gap")) for case in selected_cases)
    p867_salt_gaps = Counter(
        str((case.get("public_features") or {}).get("salt_gap"))
        for case in p867
    )
    false_positive_salt_gaps = Counter(
        str((case.get("public_features") or {}).get("salt_gap"))
        for case in selected_cases
        if not case.get("p867_motif_verified_below_rho")
    )
    return {
        "cached_group_p867_amortized_ops_over_rho": ratio(cached_sum, p867_source_groups),
        "cached_relation_p867_amortized_ops_over_rho": ratio(cached_sum, len(p867_relation_groups)),
        "cached_source_group_count": len(source_groups),
        "cached_sum_ops_over_rho": round8(cached_sum),
        "direct_case_p867_amortized_ops_over_rho": ratio(direct_sum, len(p867)),
        "direct_relation_p867_amortized_ops_over_rho": ratio(direct_sum, len(p867_relation_groups)),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "duplicate_source_group_count": sum(1 for group in source_groups.values() if len(group) > 1),
        "false_positive_salt_gap_histogram": dict(sorted(false_positive_salt_gaps.items())),
        "max_direct_ops_over_rho": round8(max([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)),
        "min_direct_ops_over_rho": round8(min([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)),
        "p867_false_positive_count": len(selected_cases) - len(p867),
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(selected_cases)),
        "p867_relation_group_count": len(p867_relation_groups),
        "p867_salt_gap_histogram": dict(sorted(p867_salt_gaps.items())),
        "p867_source_group_count": p867_source_groups,
        "rank_histogram": dict(sorted(ranks.items())),
        "salt_gap_histogram": dict(sorted(salt_gaps.items())),
        "selected_all_direct_below_rho": bool(
            selected_cases and all(float_value(case.get("direct_ops_over_rho")) < 1.0 for case in selected_cases)
        ),
        "selected_count": len(selected_cases),
        "union_precision": ratio(len(union_verified), len(selected_cases)),
        "union_relation_group_count": len(union_relation_groups),
        "union_verified_count": len(union_verified),
    }


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    public = case.get("public_features") or {}
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "p867_motif_verified_below_rho": bool(case.get("p867_motif_verified_below_rho")),
        "salt_gap": public.get("salt_gap"),
        "top_k": public.get("top_k"),
        "transfer_index": public.get("transfer_index") or case.get("transfer_index"),
        "union_public_key_verified": bool(case.get("union_public_key_verified")),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": public.get("window") or case.get("window"),
    }


def p979_controls(p979: dict[str, Any]) -> dict[str, Any]:
    selected = [
        case
        for case in p979.get("selected_cases") or []
        if third_stage_rule(case.get("public_features") or {})
    ]
    baseline = summarize_selected(selected)
    return {
        "p979_claim_is_expected": p979.get("claim_status")
        == "NEGATIVE_RESULT_P979_FROZEN_GATE_HAS_FRESH_SIGNAL_BUT_NOT_BELOW_RHO_THRESHOLD",
        "p979_refined_amortized_expected": baseline.get("direct_relation_p867_amortized_ops_over_rho")
        == 0.96897811,
        "p979_refined_p867_is_4": int_value(baseline.get("p867_positive_count")) == 4,
        "p979_refined_precision_is_0p8": baseline.get("p867_precision") == 0.8,
        "p979_refined_relation_groups_is_4": int_value(baseline.get("p867_relation_group_count")) == 4,
        "p979_refined_selected_is_5": int_value(baseline.get("selected_count")) == 5,
    }, baseline


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p979_path = Path(args.p979)
    p979 = load_json(p979_path)
    windows = list(args.windows)
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    source_paths = {window: p868.source_path(window) for window in windows}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    source_case_count_by_window: Counter[str] = Counter()
    first_stage_count_by_window: Counter[str] = Counter()
    second_stage_count_by_window: Counter[str] = Counter()
    third_stage_count_by_window: Counter[str] = Counter()
    selected: list[dict[str, Any]] = []

    for window in windows:
        source = p868.load_json(source_paths[window])
        params = repair_probe.source_parameters(source)
        probe_args = repair_probe.probe_args_from_source(source)
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
            build_cache[cache_key] = (*repair_probe.build_specs(params), probe_args)
        verifier, records, config_source, specs_by_target, probe_args = build_cache[cache_key]

        for case in p868.iter_source_cases(source, window, targets):
            source_case_count_by_window[window] += 1
            context = hit_stream_probe.scan_case_context(
                verifier,
                records,
                config_source,
                specs_by_target,
                case,
                probe_args,
                context_cache,
            )
            public_features = p869.public_features(case, context)
            if not p870.frozen_rule(public_features):
                continue
            first_stage_count_by_window[window] += 1
            if not p872.second_stage_rule(public_features):
                continue
            second_stage_count_by_window[window] += 1
            if not third_stage_rule(public_features):
                continue
            third_stage_count_by_window[window] += 1
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            selected.append(p872.compact_selected_case(labeled, public_features))

    selection_summary = summarize_selected(selected)
    controls, p979_refined_baseline = p979_controls(p979)
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in selected)
    controls["reconstruction_errors_zero"] = reconstruction_error_count == 0
    success = bool(
        all(controls.values())
        and selection_summary["selected_count"] >= 4
        and selection_summary["p867_relation_group_count"] >= 3
        and (selection_summary["p867_precision"] or 0.0) >= 0.75
        and (selection_summary["direct_relation_p867_amortized_ops_over_rho"] or 10**9) < 1.0
        and reconstruction_error_count == 0
    )
    if not all(controls.values()):
        claim = "NEGATIVE_RESULT_P980_CONTROL_FAILURE"
    elif success:
        claim = "P980_HIGH_GAP_FROZEN_REFINEMENT_VALIDATES_BELOW_RHO_ON_STILL_LATER_WINDOWS"
    elif selection_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P980_HIGH_GAP_SELECTS_NO_STILL_LATER_CASES"
    elif selection_summary["p867_positive_count"] > 0:
        claim = "NEGATIVE_RESULT_P980_HIGH_GAP_HAS_SIGNAL_BUT_NOT_BELOW_RHO_THRESHOLD"
    else:
        claim = "NEGATIVE_RESULT_P980_HIGH_GAP_MISSES_STILL_LATER_P867_SIGNAL"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p979_source": str(p979_path),
            "script": str(Path(__file__)),
            "source_windows": {window: str(path) for window, path in source_paths.items()},
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p979_source_sha256": sha256_file(p979_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P980_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-REFINEMENT: the high-gap rule was derived from P979 and applied before reconstruction on P980 windows.",
            "STILL-LATER-BUT-SAME-FAMILY: validation windows are later/disjoint but remain p231 fixed-row family data.",
            "FALSE-POSITIVES-CHARGED: every selected case is charged in useful-amortized metrics.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this does not close a global matrix or individual logarithm descent.",
        ],
        "method": "p980_p231_high_gap_frozen_refinement",
        "parameters": {
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": sorted(targets),
            "third_stage_rule": THIRD_STAGE_RULE,
            "windows": windows,
        },
        "p979_refined_baseline": p979_refined_baseline,
        "selected_cases": selected,
        "selected_cases_compact": [compact_case(case) for case in selected],
        "selection_summary": selection_summary,
        "source_controls": controls,
        "summary": {
            "control_pass": all(controls.values()),
            "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
            "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
            "fresh_refinement_success": success,
            "p979_refined_baseline_direct_relation_p867_amortized_ops_over_rho": p979_refined_baseline.get(
                "direct_relation_p867_amortized_ops_over_rho"
            ),
            "p979_refined_baseline_p867_positive_count": p979_refined_baseline.get("p867_positive_count"),
            "p979_refined_baseline_p867_precision": p979_refined_baseline.get("p867_precision"),
            "p979_refined_baseline_selected_count": p979_refined_baseline.get("selected_count"),
            "reconstruction_error_count": reconstruction_error_count,
            "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
            "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
            "source_case_count": sum(source_case_count_by_window.values()),
            "source_count_by_window": dict(source_case_count_by_window),
            "third_stage_selected_case_count": sum(third_stage_count_by_window.values()),
            "third_stage_selected_count_by_window": dict(third_stage_count_by_window),
            **selection_summary,
        },
        "schema": SCHEMA,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P980 contract path")
    parser.add_argument("--p979", default=str(DEFAULT_P979), help="P979 frozen validation JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target ids")
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS), help="Validation windows")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} p867={p867} precision={precision} "
        "direct_relation_amortized={direct_relation} first_stage={first_stage} "
        "second_stage={second_stage} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            p867=summary["p867_positive_count"],
            precision=summary["p867_precision"],
            direct_relation=summary["direct_relation_p867_amortized_ops_over_rho"],
            first_stage=summary["first_stage_selected_case_count"],
            second_stage=summary["second_stage_selected_case_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
