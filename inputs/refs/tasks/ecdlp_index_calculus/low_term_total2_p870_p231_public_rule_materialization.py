#!/usr/bin/env python3
"""P870 materialization of the frozen P869 public p231 motif rule."""

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
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p870_p231_public_rule_materialization.md"
DEFAULT_WINDOWS = (
    "1240_1247",
    "1248_1255",
    "1256_1263",
    "1264_1271",
    "1272_1279",
    "1280_1287",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p870_p231_public_rule_materialization_probe.json"
SCHEMA = "ecdlp.low_term_total2_p870_p231_public_rule_materialization.v1"
FROZEN_RULE_NAME = "top_k <= 12 AND all_has_double_pair"


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


def frozen_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) <= 12 and bool(features.get("all_has_double_pair"))


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


def build_window_contexts(
    windows: list[str],
    targets: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Path]]:
    source_paths = {window: p868.source_path(window) for window in windows}
    source_cases: list[dict[str, Any]] = []
    for window, path in source_paths.items():
        source = p868.load_json(path)
        for case in p868.iter_source_cases(source, window, targets):
            source_cases.append(case)
    return source_cases, source_paths


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    windows = list(args.windows)
    source_cases, source_paths = build_window_contexts(windows, targets)

    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    selected: list[dict[str, Any]] = []
    unselected_count_by_window: Counter[str] = Counter()
    source_count_by_window: Counter[str] = Counter()

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

        window_cases = [case for case in source_cases if case.get("window") == window]
        for case in window_cases:
            source_count_by_window[window] += 1
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
            if not frozen_rule(features):
                unselected_count_by_window[window] += 1
                continue
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
    selected_positive = [row for row in selected if row["case"].get("p867_motif_verified_below_rho")]
    selected_motif_verified = [
        row for row in selected if int_value(row["case"].get("p867_motif_matched_derivation_count")) > 0
    ]
    union_verified = [row for row in selected if row["case"].get("union_public_key_verified")]
    selected_below = [
        row
        for row in union_verified
        if row["case"].get("direct_ops_over_rho") is not None and float(row["case"]["direct_ops_over_rho"]) < 1.0
    ]
    unique_positive_groups = {
        (
            str(row["case"].get("target")),
            int_value(row["case"].get("transfer_index")),
            int_value(row["case"].get("union_derived_secret")),
            p868.json_key(row["case"].get("row_leaf_keys")),
        )
        for row in selected_positive
    }
    selected_precision = safe_ratio(len(selected_positive), len(selected))
    summary = {
        "claim_status": None,
        "frozen_rule": FROZEN_RULE_NAME,
        "materialization_windows": windows,
        "p867_motif_verified_below_rho_case_count": len(selected_positive),
        "p867_motif_verified_below_rho_precision": selected_precision,
        "p867_motif_verified_derivation_case_count": len(selected_motif_verified),
        "p867_motif_verified_transfer_count": len(
            {int_value(row["case"].get("transfer_index")) for row in selected_positive}
        ),
        "p867_motif_verified_unique_scalar_group_count": len(unique_positive_groups),
        "p867_motif_verified_window_count": len({row["window"] for row in selected_positive}),
        "reconstructed_selected_case_count": len(selected_cases),
        "reconstruction_error_count": sum(int_value(row.get("reconstructed_error_count")) for row in selected_cases),
        "selected_below_rho_union_case_count": len(selected_below),
        "selected_case_count": len(selected),
        "selected_count_by_window": dict(Counter(row["window"] for row in selected)),
        "selected_fraction": safe_ratio(len(selected), len(source_cases)),
        "selected_union_public_key_verified_case_count": len(union_verified),
        "source_case_count": len(source_cases),
        "source_count_by_window": dict(source_count_by_window),
        "target_count": len(targets),
        "unselected_case_count": sum(unselected_count_by_window.values()),
        "unselected_count_by_window": dict(unselected_count_by_window),
    }
    if int_value(summary["reconstruction_error_count"]) and not int_value(
        summary["p867_motif_verified_below_rho_case_count"]
    ):
        claim = "NEGATIVE_RESULT_P870_RECONSTRUCTION_ERRORS_BLOCK_PUBLIC_RULE_MATERIALIZATION"
    elif int_value(summary["p867_motif_verified_below_rho_case_count"]) > 0 and int_value(
        summary["p867_motif_verified_window_count"]
    ) >= 2:
        claim = "P870_PUBLIC_RULE_MATERIALIZES_P867_MOTIF_MULTIWINDOW"
    elif int_value(summary["p867_motif_verified_below_rho_case_count"]) > 0:
        claim = "P870_PUBLIC_RULE_MATERIALIZES_P867_MOTIF"
    elif int_value(summary["p867_motif_verified_derivation_case_count"]) > 0:
        claim = "P870_PUBLIC_RULE_MATERIALIZES_VERIFIED_MOTIF_ABOVE_RHO_ONLY"
    else:
        claim = "NEGATIVE_RESULT_P870_PUBLIC_RULE_MISSES_LATER_P867_MOTIF"
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
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P870_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "FROZEN-RULE BOUNDARY: P870 applies the P869 rule without retraining on later windows.",
            "MATERIALIZATION BOUNDARY: unselected cases are not reconstructed, so recall and all-case prevalence remain unknown.",
            "SAME-P231-FAMILY BOUNDARY: materialization windows are later and unseen by P869 but still in the p231 fixed-row family.",
            "TARGET-DESCENT BOUNDARY: selected local derivations do not solve cross-public-key target descent.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p870_p231_public_rule_materialization",
        "parameters": {
            "frozen_rule": FROZEN_RULE_NAME,
            "motif": p868.P867_MOTIF,
            "targets": sorted(targets),
            "windows": windows,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "The P869 rule was fixed before these materialization windows were evaluated.",
                "Public feature rows are available before relation-event reconstruction.",
                "Unselected cases are deliberately not labeled in this materialization run.",
            ],
            "claim_or_task": "Materialize the P869 public pre-scan rule on later unseen p231 windows.",
            "evidence_so_far": [
                f"Selected cases: {summary.get('selected_case_count')}/{summary.get('source_case_count')}.",
                f"Selected P867 below-rho cases: {summary.get('p867_motif_verified_below_rho_case_count')}.",
                f"Selected precision: {summary.get('p867_motif_verified_below_rho_precision')}.",
            ],
            "failure_modes": [
                "The frozen rule may select many false positives and need a second public precision gate.",
                "Because unselected cases are not reconstructed, P870 cannot claim full recall.",
                "Same-context motif derivations still leave target descent open.",
            ],
            "next_concrete_action": (
                "Build P871 as a second-stage public precision gate on P870 selected false positives, or run a paid full-label recall audit if precision/yield is ambiguous."
            ),
            "status": "OBSERVATION" if claim.startswith("P870_") else "NEGATIVE RESULT",
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
