#!/usr/bin/env python3
"""P982 frozen later-window validation of the P981 broad union/rank label."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p982_p231_broad_label_frozen_validation.md"
DEFAULT_P981 = STATE_DIR / "low_term_total2_p981_non_p867_union_relation_quality_probe.json"
DEFAULT_WINDOWS = (
    "11456_11463",
    "11464_11471",
    "11472_11479",
    "11480_11487",
    "11488_11495",
    "11496_11503",
    "11504_11511",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p982_p231_broad_label_frozen_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p982_p231_broad_label_frozen_validation.v1"
BROAD_LABEL = "union_public_key_verified AND union_rank >= 3 AND direct_ops_over_rho < 1"
FROZEN_SELECTOR_RULE = "top_k == 4 AND salt_gap >= 6"


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


def frozen_broad_selector(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) == 4 and int_value(features.get("salt_gap"), -1) >= 6


def is_direct_below_rho(case: dict[str, Any]) -> bool:
    return float_value(case.get("direct_ops_over_rho"), 10**9) < 1.0


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def is_broad(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 3 and is_direct_below_rho(case)


def relation_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        case.get("target"),
        int_value(case.get("transfer_index")),
        case.get("union_derived_secret"),
        json.dumps(case.get("row_leaf_keys") or [], sort_keys=True),
    )


def row_leaf_set_key(case: dict[str, Any]) -> str:
    rows = []
    for row_leaf in case.get("row_leaf_keys") or []:
        rows.append(
            {
                "leaf_indices": [int_value(value) for value in row_leaf.get("leaf_indices") or []],
                "row_key": row_leaf.get("row_key"),
            }
        )
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


def matrix_form_proxy_key(case: dict[str, Any]) -> tuple[Any, ...]:
    public = case.get("public_features") or {}
    return (
        case.get("target"),
        case.get("leaf_selector"),
        tuple(public.get("leaf_gap_tuple") or []),
        row_leaf_set_key(case),
        int_value(case.get("union_rank")),
        int_value(case.get("union_relation_count")),
        int_value(case.get("relation_form_count")),
    )


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


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    public = case.get("public_features") or {}
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "is_broad_union_rank_ge3": is_broad(case),
        "is_p867": is_p867(case),
        "leaf_selector": case.get("leaf_selector"),
        "matrix_form_proxy": list(matrix_form_proxy_key(case)),
        "relation_form_count": case.get("relation_form_count"),
        "salt_gap": public.get("salt_gap"),
        "top_k": public.get("top_k"),
        "transfer_index": public.get("transfer_index") or case.get("transfer_index"),
        "union_public_key_verified": is_union(case),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": public.get("window") or case.get("window"),
    }


def summarize_selected(selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_sum = sum(float_value(case.get("direct_ops_over_rho")) for case in selected_cases)
    p867 = [case for case in selected_cases if is_p867(case)]
    union_verified = [case for case in selected_cases if is_union(case)]
    broad = [case for case in selected_cases if is_broad(case)]
    non_p867_broad = [case for case in broad if not is_p867(case)]
    rank4 = [case for case in broad if int_value(case.get("union_rank")) >= 4]

    relation_groups = {relation_group_key(case) for case in selected_cases}
    p867_relation_groups = {relation_group_key(case) for case in p867}
    union_relation_groups = {relation_group_key(case) for case in union_verified}
    broad_relation_groups = {relation_group_key(case) for case in broad}
    non_p867_broad_relation_groups = {relation_group_key(case) for case in non_p867_broad}
    broad_matrix_proxy_keys = {matrix_form_proxy_key(case) for case in broad}
    broad_row_leaf_sets = {row_leaf_set_key(case) for case in broad}
    source_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for case in selected_cases:
        source_groups.setdefault(source_group_key(case), []).append(case)

    return {
        "broad_direct_relation_amortized_ops_over_rho": ratio(direct_sum, len(broad_relation_groups)),
        "broad_matrix_form_proxy_count": len(broad_matrix_proxy_keys),
        "broad_non_p867_count": len(non_p867_broad),
        "broad_non_p867_relation_group_count": len(non_p867_broad_relation_groups),
        "broad_precision": ratio(len(broad), len(selected_cases)),
        "broad_relation_group_count": len(broad_relation_groups),
        "broad_row_leaf_set_count": len(broad_row_leaf_sets),
        "broad_union_rank_ge3_count": len(broad),
        "cached_source_group_count": len(source_groups),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "duplicate_source_group_count": sum(1 for group in source_groups.values() if len(group) > 1),
        "leaf_selector_histogram": dict(sorted(Counter(str(case.get("leaf_selector")) for case in selected_cases).items())),
        "matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in selected_cases}),
        "max_direct_ops_over_rho": round8(
            max([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "min_direct_ops_over_rho": round8(
            min([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(selected_cases)),
        "p867_relation_group_count": len(p867_relation_groups),
        "rank4_broad_count": len(rank4),
        "rank_histogram": dict(sorted(Counter(str(case.get("union_rank")) for case in selected_cases).items())),
        "relation_form_count_sum": sum(int_value(case.get("relation_form_count")) for case in selected_cases),
        "relation_group_count": len(relation_groups),
        "sample_broad_cases": [compact_case(case) for case in broad[:8]],
        "sample_selected_cases": [compact_case(case) for case in selected_cases[:8]],
        "salt_gap_histogram": dict(
            sorted(Counter(str((case.get("public_features") or {}).get("salt_gap")) for case in selected_cases).items())
        ),
        "selected_all_direct_below_rho": bool(
            selected_cases and all(is_direct_below_rho(case) for case in selected_cases)
        ),
        "selected_count": len(selected_cases),
        "union_derived_secret_count": len({case.get("union_derived_secret") for case in broad}),
        "union_precision": ratio(len(union_verified), len(selected_cases)),
        "union_relation_count_sum": sum(int_value(case.get("union_relation_count")) for case in selected_cases),
        "union_relation_group_count": len(union_relation_groups),
        "union_verified_count": len(union_verified),
    }


def p981_controls(p981: dict[str, Any]) -> dict[str, Any]:
    summary = p981.get("summary") or {}
    return {
        "p981_claim_is_expected": p981.get("claim_status") == "P981_NON_P867_UNION_RANK_SIGNAL_IDENTIFIED_IN_P980",
        "p981_control_pass": bool(summary.get("control_pass")),
        "p981_success": bool(summary.get("success")),
        "p981_p980_broad_groups_expected": int_value(summary.get("p980_broad_relation_group_count")) == 2,
        "p981_p980_non_p867_expected": int_value(summary.get("p980_broad_non_p867_count")) == 2,
        "p981_p980_broad_amortized_expected": summary.get("p980_broad_direct_relation_amortized_ops_over_rho")
        == 0.79197081,
        "p981_p980_rank4_expected": int_value(summary.get("p980_rank4_union_count")) == 1,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p981_path = Path(args.p981)
    p981 = load_json(p981_path)
    p981_control_values = p981_controls(p981)
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
    frozen_selected_count_by_window: Counter[str] = Counter()
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
            if not frozen_broad_selector(public_features):
                continue
            frozen_selected_count_by_window[window] += 1
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

    selected_summary = summarize_selected(selected)
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in selected)
    control_pass = all(p981_control_values.values())
    success = bool(
        control_pass
        and reconstruction_error_count == 0
        and selected_summary["selected_count"] > 0
        and selected_summary["broad_relation_group_count"] > 0
        and (selected_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and selected_summary["broad_matrix_form_proxy_count"] > 0
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P982_CONTROL_FAILURE"
    elif selected_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P982_FROZEN_BROAD_SELECTOR_SELECTS_NO_LATER_ROWS"
    elif selected_summary["broad_relation_group_count"] == 0:
        claim = "NEGATIVE_RESULT_P982_FROZEN_BROAD_SELECTOR_HAS_NO_BROAD_UNION_RANK_ROWS"
    elif (selected_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P982_BROAD_LABEL_SIGNAL_NOT_BELOW_RHO_ON_LATER_WINDOWS"
    elif success:
        claim = "P982_FROZEN_BROAD_LABEL_VALIDATES_BELOW_RHO_ON_LATER_WINDOWS"
    else:
        claim = "NEGATIVE_RESULT_P982_BROAD_LABEL_DIVERSITY_OR_RECONSTRUCTION_FAILURE"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p981_source": str(p981_path),
            "script": str(Path(__file__)),
            "source_windows": {window: str(path) for window, path in source_paths.items()},
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p981_source_sha256": sha256_file(p981_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": BROAD_LABEL,
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P982_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-SELECTOR: the broad source selector is the P980 public high-gap rule and is applied before reconstruction.",
            "BROAD-LABEL-SIGNAL: union/rank usefulness is tracked separately from P867 motif usefulness.",
            "MATRIX-PROXY-ONLY: form diversity uses compact row/leaf/rank proxies, not a solved sparse linear algebra instance.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm or target descent.",
        ],
        "method": "p982_p231_broad_label_frozen_validation",
        "parameters": {
            "broad_label": BROAD_LABEL,
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "frozen_selector_rule": FROZEN_SELECTOR_RULE,
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": sorted(targets),
            "windows": windows,
        },
        "schema": SCHEMA,
        "selected_cases": selected,
        "selected_cases_compact": [compact_case(case) for case in selected],
        "selection_summary": selected_summary,
        "source_controls": p981_control_values,
        "summary": {
            "broad_validation_success": success,
            "control_pass": control_pass,
            "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
            "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
            "frozen_selected_case_count": sum(frozen_selected_count_by_window.values()),
            "frozen_selected_count_by_window": dict(frozen_selected_count_by_window),
            "reconstruction_error_count": reconstruction_error_count,
            "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
            "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
            "source_case_count": sum(source_case_count_by_window.values()),
            "source_count_by_window": dict(source_case_count_by_window),
            **selected_summary,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P982 contract path")
    parser.add_argument("--p981", default=str(DEFAULT_P981), help="P981 control JSON")
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
        "claim={claim} selected={selected} broad_groups={broad_groups} "
        "broad_amortized={broad_amortized} p867={p867} rank4={rank4} "
        "matrix_proxy={matrix_proxy} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            broad_groups=summary["broad_relation_group_count"],
            broad_amortized=summary["broad_direct_relation_amortized_ops_over_rho"],
            p867=summary["p867_positive_count"],
            rank4=summary["rank4_broad_count"],
            matrix_proxy=summary["broad_matrix_form_proxy_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
