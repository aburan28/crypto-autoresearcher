#!/usr/bin/env python3
"""P872 materialization of the frozen P870+P871 two-stage p231 rule."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_low_term_total2_ffe_hit_stream_probe as hit_stream_probe
import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p870_p231_public_rule_materialization as p870
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p872_p231_two_stage_materialization.md"
DEFAULT_WINDOWS = (
    "11288_11295",
    "11296_11303",
    "11304_11311",
    "11312_11319",
    "11320_11327",
    "11328_11335",
    "11336_11343",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json"
SCHEMA = "ecdlp.low_term_total2_p872_p231_two_stage_materialization.v1"
FIRST_STAGE_RULE = "top_k <= 12 AND all_has_double_pair"
SECOND_STAGE_RULE = "count_double_pair >= 7 AND salt_gap <= 8"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def second_stage_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("count_double_pair")) >= 7 and (
        features.get("salt_gap") is not None and int_value(features.get("salt_gap")) <= 8
    )


def compact_feature_row(features: dict[str, Any]) -> dict[str, Any]:
    return {
        "all_has_double_pair": features.get("all_has_double_pair"),
        "case_id": features.get("case_id"),
        "count_double_pair": features.get("count_double_pair"),
        "count_shape_2p2": features.get("count_shape_2p2"),
        "leaf_gap_tuple": features.get("leaf_gap_tuple"),
        "leaf_selector": features.get("leaf_selector"),
        "leaf_selector_family": features.get("leaf_selector_family"),
        "salt_gap": features.get("salt_gap"),
        "selected_leaf_occurrence_count": features.get("selected_leaf_occurrence_count"),
        "top_k": features.get("top_k"),
        "transfer_index": features.get("transfer_index"),
        "unique_leaf_count": features.get("unique_leaf_count"),
        "unique_leaf_indices": features.get("unique_leaf_indices"),
        "window": features.get("window"),
    }


def compact_selected_case(row: dict[str, Any], features: dict[str, Any]) -> dict[str, Any]:
    compact = p868.compact_case(row)
    compact["public_features"] = compact_feature_row(features)
    compact["p867_motif_verified_below_rho"] = bool(row.get("p867_motif_verified_below_rho"))
    compact["reconstructed_error_count"] = int_value(row.get("reconstructed_error_count"))
    return compact


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.windows)
    source_paths = {window: p868.source_path(window) for window in windows}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    source_case_count_by_window: Counter[str] = Counter()
    first_stage_count_by_window: Counter[str] = Counter()
    second_stage_count_by_window: Counter[str] = Counter()
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
            features = p869.public_features(case, context)
            if not p870.frozen_rule(features):
                continue
            first_stage_count_by_window[window] += 1
            if not second_stage_rule(features):
                continue
            second_stage_count_by_window[window] += 1
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            selected.append(
                {
                    "case": labeled,
                    "features": features,
                    "window": window,
                }
            )

    selected_cases = [row["case"] for row in selected]
    union_verified = [row for row in selected if row["case"].get("union_public_key_verified")]
    selected_below = [
        row
        for row in union_verified
        if row["case"].get("direct_ops_over_rho") is not None and float(row["case"]["direct_ops_over_rho"]) < 1.0
    ]
    p867_positive = [row for row in selected if row["case"].get("p867_motif_verified_below_rho")]
    p867_verified = [
        row for row in selected if int_value(row["case"].get("p867_motif_matched_derivation_count")) > 0
    ]
    unique_positive_groups = {
        (
            str(row["case"].get("target")),
            int_value(row["case"].get("transfer_index")),
            int_value(row["case"].get("union_derived_secret")),
            p868.json_key(row["case"].get("row_leaf_keys")),
        )
        for row in p867_positive
    }
    summary = {
        "claim_status": None,
        "first_stage_rule": FIRST_STAGE_RULE,
        "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
        "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
        "materialization_windows": windows,
        "p867_motif_verified_below_rho_case_count": len(p867_positive),
        "p867_motif_verified_below_rho_precision": safe_ratio(len(p867_positive), len(selected)),
        "p867_motif_verified_derivation_case_count": len(p867_verified),
        "p867_motif_verified_transfer_count": len(
            {int_value(row["case"].get("transfer_index")) for row in p867_positive}
        ),
        "p867_motif_verified_unique_scalar_group_count": len(unique_positive_groups),
        "p867_motif_verified_window_count": len({row["window"] for row in p867_positive}),
        "reconstructed_selected_case_count": len(selected_cases),
        "reconstruction_error_count": sum(int_value(row.get("reconstructed_error_count")) for row in selected_cases),
        "second_stage_rule": SECOND_STAGE_RULE,
        "second_stage_selected_case_count": len(selected),
        "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
        "selected_below_rho_union_case_count": len(selected_below),
        "selected_union_public_key_verified_case_count": len(union_verified),
        "source_case_count": sum(source_case_count_by_window.values()),
        "source_count_by_window": dict(source_case_count_by_window),
        "target_count": len(targets),
    }
    if int_value(summary["reconstruction_error_count"]) and not int_value(
        summary["p867_motif_verified_below_rho_case_count"]
    ):
        claim = "NEGATIVE_RESULT_P872_RECONSTRUCTION_ERRORS_BLOCK_TWO_STAGE_MATERIALIZATION"
    elif int_value(summary["p867_motif_verified_below_rho_case_count"]) > 0 and int_value(
        summary["p867_motif_verified_window_count"]
    ) >= 2:
        claim = "P872_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_P867_MOTIF_MULTIWINDOW"
    elif int_value(summary["p867_motif_verified_below_rho_case_count"]) > 0:
        claim = "P872_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_P867_MOTIF"
    elif int_value(summary["p867_motif_verified_derivation_case_count"]) > 0:
        claim = "P872_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_VERIFIED_MOTIF_ABOVE_RHO_ONLY"
    else:
        claim = "NEGATIVE_RESULT_P872_TWO_STAGE_PUBLIC_RULE_MISSES_LATER_P867_MOTIF"
    summary["claim_status"] = claim

    selected_sorted = sorted(
        selected,
        key=lambda row: (
            not bool(row["case"].get("p867_motif_verified_below_rho")),
            float(row["case"].get("direct_ops_over_rho") or 10**18),
            str(row["features"].get("case_id")),
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source_windows": {window: str(path) for window, path in source_paths.items()},
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P872_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FROZEN-RULE BOUNDARY: P872 applies P870/P871 rules without retraining on later windows.",
            "MATERIALIZATION BOUNDARY: unselected cases are not reconstructed, so recall and all-case prevalence remain unknown.",
            "SAME-P231-FAMILY BOUNDARY: materialization windows are later and unused by P870/P871 but still in the p231 fixed-row family.",
            "TARGET-DESCENT BOUNDARY: selected local derivations do not solve cross-public-key target descent.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p872_p231_two_stage_materialization",
        "parameters": {
            "first_stage_rule": FIRST_STAGE_RULE,
            "motif": p868.P867_MOTIF,
            "second_stage_rule": SECOND_STAGE_RULE,
            "targets": sorted(targets),
            "windows": windows,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "The P870/P871 rules were fixed before these materialization windows were evaluated.",
                "Public feature rows are available before relation-event reconstruction.",
                "Unselected cases are deliberately not labeled in this materialization run.",
            ],
            "claim_or_task": "Materialize the frozen two-stage public selector on later unused p231 windows.",
            "evidence_so_far": [
                f"Second-stage selected cases: {summary.get('second_stage_selected_case_count')}/{summary.get('source_case_count')}.",
                f"Selected P867 below-rho cases: {summary.get('p867_motif_verified_below_rho_case_count')}.",
                f"Selected precision: {summary.get('p867_motif_verified_below_rho_precision')}.",
            ],
            "failure_modes": [
                "The two-stage rule may still be p231-family specific.",
                "Selected-only evaluation cannot prove recall over unselected cases.",
                "Same-context motif derivations still leave target descent open.",
            ],
            "next_concrete_action": (
                "Build P873 to test target-descent utility of accumulated P867 motif-positive groups or to materialize the same two-stage rule on a disjoint target family."
            ),
            "status": "OBSERVATION" if claim.startswith("P872_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "selected_cases": [
            compact_selected_case(row["case"], row["features"])
            for row in selected_sorted
        ],
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS))
    parser.add_argument("--targets", default=DEFAULT_TARGET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
