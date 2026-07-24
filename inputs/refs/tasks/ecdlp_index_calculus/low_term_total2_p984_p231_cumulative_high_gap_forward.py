#!/usr/bin/env python3
"""P984 cumulative forward audit of the unguarded p231 high-gap rule."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p984_p231_cumulative_high_gap_forward.md"
DEFAULT_P982 = STATE_DIR / "low_term_total2_p982_p231_broad_label_frozen_validation_probe.json"
DEFAULT_P983 = STATE_DIR / "low_term_total2_p983_p231_rank_quality_residue_guard_probe.json"
DEFAULT_WINDOWS = (
    "11568_11575",
    "11576_11583",
    "11584_11591",
    "11592_11599",
    "11600_11607",
    "11608_11615",
    "11616_11623",
)
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p984_p231_cumulative_high_gap_forward_probe.json"
SCHEMA = "ecdlp.low_term_total2_p984_p231_cumulative_high_gap_forward.v1"
BROAD_LABEL = "union_public_key_verified AND union_rank >= 3 AND direct_ops_over_rho < 1"
HIGH_GAP_RULE = "top_k == 4 AND salt_gap >= 6"


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


def high_gap_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) == 4 and int_value(features.get("salt_gap"), -1) >= 6


def row_salts(case: dict[str, Any]) -> list[int]:
    salts = []
    for row_leaf in case.get("row_leaf_keys") or []:
        row_key = str(row_leaf.get("row_key"))
        if "salt" in row_key:
            salts.append(int_value(row_key.rsplit("salt", 1)[-1]))
    return sorted(salts)


def is_direct_below_rho(case: dict[str, Any]) -> bool:
    return float_value(case.get("direct_ops_over_rho"), 10**9) < 1.0


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def is_broad(case: dict[str, Any]) -> bool:
    return is_union(case) and int_value(case.get("union_rank")) >= 3 and is_direct_below_rho(case)


def is_rank4_broad(case: dict[str, Any]) -> bool:
    return is_broad(case) and int_value(case.get("union_rank")) >= 4


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


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    public = case.get("public_features") or {}
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "is_broad_union_rank_ge3": is_broad(case),
        "is_p867": is_p867(case),
        "is_rank4_broad": is_rank4_broad(case),
        "leaf_selector": case.get("leaf_selector"),
        "matrix_form_proxy": list(matrix_form_proxy_key(case)),
        "relation_form_count": case.get("relation_form_count"),
        "row_salts": row_salts(case),
        "salt_gap": public.get("salt_gap"),
        "top_k": public.get("top_k"),
        "transfer_index": public.get("transfer_index") or case.get("transfer_index"),
        "union_public_key_verified": is_union(case),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": public.get("window") or case.get("window"),
    }


def summarize_selected(name: str, selected_cases: list[dict[str, Any]]) -> dict[str, Any]:
    direct_sum = sum(float_value(case.get("direct_ops_over_rho")) for case in selected_cases)
    broad = [case for case in selected_cases if is_broad(case)]
    rank4 = [case for case in broad if int_value(case.get("union_rank")) >= 4]
    p867 = [case for case in selected_cases if is_p867(case)]
    union_verified = [case for case in selected_cases if is_union(case)]
    broad_relation_groups = {relation_group_key(case) for case in broad}
    rank4_relation_groups = {relation_group_key(case) for case in rank4}
    return {
        "broad_direct_relation_amortized_ops_over_rho": ratio(direct_sum, len(broad_relation_groups)),
        "broad_matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in broad}),
        "broad_non_p867_count": sum(1 for case in broad if not is_p867(case)),
        "broad_precision": ratio(len(broad), len(selected_cases)),
        "broad_relation_group_count": len(broad_relation_groups),
        "broad_row_leaf_set_count": len({row_leaf_set_key(case) for case in broad}),
        "broad_union_rank_ge3_count": len(broad),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "leaf_selector_histogram": dict(sorted(Counter(str(case.get("leaf_selector")) for case in selected_cases).items())),
        "matrix_form_proxy_count": len({matrix_form_proxy_key(case) for case in selected_cases}),
        "max_direct_ops_over_rho": round8(
            max([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "min_direct_ops_over_rho": round8(
            min([float_value(case.get("direct_ops_over_rho")) for case in selected_cases], default=0.0)
        ),
        "name": name,
        "p867_positive_count": len(p867),
        "p867_precision": ratio(len(p867), len(selected_cases)),
        "p867_relation_group_count": len({relation_group_key(case) for case in p867}),
        "rank4_broad_count": len(rank4),
        "rank4_direct_relation_amortized_ops_over_rho": ratio(direct_sum, len(rank4_relation_groups)),
        "rank4_relation_group_count": len(rank4_relation_groups),
        "rank_histogram": dict(sorted(Counter(str(case.get("union_rank")) for case in selected_cases).items())),
        "relation_form_count_sum": sum(int_value(case.get("relation_form_count")) for case in selected_cases),
        "relation_group_count": len({relation_group_key(case) for case in selected_cases}),
        "sample_broad_cases": [compact_case(case) for case in broad[:12]],
        "sample_selected_cases": [compact_case(case) for case in selected_cases[:12]],
        "salt_gap_histogram": dict(
            sorted(Counter(str((case.get("public_features") or {}).get("salt_gap")) for case in selected_cases).items())
        ),
        "selected_all_direct_below_rho": bool(
            selected_cases and all(is_direct_below_rho(case) for case in selected_cases)
        ),
        "selected_count": len(selected_cases),
        "union_precision": ratio(len(union_verified), len(selected_cases)),
        "union_relation_group_count": len({relation_group_key(case) for case in union_verified}),
        "union_verified_count": len(union_verified),
    }


def selected_from_p982(p982: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in p982.get("selected_cases") or []:
        if isinstance(case, dict):
            row = dict(case)
            row["audit_block"] = "p982_prior"
            rows.append(row)
    return rows


def selected_from_p983(p983: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in p983.get("validation_high_gap_cases") or []:
        if isinstance(case, dict):
            row = dict(case)
            row["audit_block"] = "p983_prior"
            rows.append(row)
    return rows


def source_controls(p982: dict[str, Any], p983: dict[str, Any]) -> dict[str, Any]:
    s982 = p982.get("summary") or {}
    s983 = p983.get("summary") or {}
    return {
        "p982_claim_expected": p982.get("claim_status")
        == "NEGATIVE_RESULT_P982_BROAD_LABEL_SIGNAL_NOT_BELOW_RHO_ON_LATER_WINDOWS",
        "p982_selected_two": int_value(s982.get("selected_count")) == 2,
        "p982_broad_groups_one": int_value(s982.get("broad_relation_group_count")) == 1,
        "p982_broad_amortized_expected": s982.get("broad_direct_relation_amortized_ops_over_rho") == 1.50364964,
        "p983_claim_expected": p983.get("claim_status") == "NEGATIVE_RESULT_P983_RESIDUE_GUARD_SELECTS_NO_LATER_ROWS",
        "p983_high_gap_one": int_value(s983.get("high_gap_selected_case_count")) == 1,
        "p983_base_broad_groups_one": int_value(s983.get("base_broad_relation_group_count")) == 1,
        "p983_base_broad_amortized_expected": s983.get("base_broad_direct_relation_amortized_ops_over_rho") == 0.84671533,
    }


def analyze_fresh(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
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
    high_gap_count_by_window: Counter[str] = Counter()
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
            if not high_gap_rule(public_features):
                continue
            high_gap_count_by_window[window] += 1
            labeled = p868.analyze_case(
                verifier,
                records,
                config_source,
                specs_by_target,
                probe_args,
                context_cache,
                case,
            )
            row = p872.compact_selected_case(labeled, public_features)
            row["audit_block"] = "p984_fresh"
            selected.append(row)

    counts = {
        "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
        "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
        "high_gap_selected_case_count": sum(high_gap_count_by_window.values()),
        "high_gap_selected_count_by_window": dict(high_gap_count_by_window),
        "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
        "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
        "source_case_count": sum(source_case_count_by_window.values()),
        "source_count_by_window": dict(source_case_count_by_window),
        "source_windows": {window: str(path) for window, path in source_paths.items()},
    }
    return selected, counts


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p982_path = Path(args.p982)
    p983_path = Path(args.p983)
    p982 = load_json(p982_path)
    p983 = load_json(p983_path)
    controls = source_controls(p982, p983)
    prior_rows = selected_from_p982(p982) + selected_from_p983(p983)
    fresh_rows, fresh_counts = analyze_fresh(args)
    cumulative_rows = prior_rows + fresh_rows
    prior_summary = summarize_selected("prior_p982_p983", prior_rows)
    fresh_summary = summarize_selected("fresh_p984", fresh_rows)
    cumulative_summary = summarize_selected("cumulative_p982_p983_p984", cumulative_rows)
    reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in cumulative_rows)
    fresh_reconstruction_error_count = sum(int_value(case.get("reconstructed_error_count")) for case in fresh_rows)
    control_pass = all(controls.values())
    success = bool(
        control_pass
        and reconstruction_error_count == 0
        and fresh_summary["selected_count"] > 0
        and cumulative_summary["broad_relation_group_count"] >= 2
        and (cumulative_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and cumulative_summary["rank4_relation_group_count"] > 0
        and cumulative_summary["broad_matrix_form_proxy_count"] >= cumulative_summary["broad_relation_group_count"]
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P984_CONTROL_FAILURE"
    elif fresh_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P984_FRESH_HIGH_GAP_SELECTS_NO_ROWS"
    elif (cumulative_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P984_CUMULATIVE_HIGH_GAP_NOT_BELOW_RHO"
    elif success:
        claim = "P984_CUMULATIVE_HIGH_GAP_VALIDATES_BROAD_SOURCE_BELOW_RHO"
    else:
        claim = "NEGATIVE_RESULT_P984_CUMULATIVE_HIGH_GAP_DIVERSITY_OR_RANK_FAILURE"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p982_source": str(p982_path),
            "p983_source": str(p983_path),
            "script": str(Path(__file__)),
            "source_windows": fresh_counts["source_windows"],
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p982_source_sha256": sha256_file(p982_path),
            "p983_source_sha256": sha256_file(p983_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": BROAD_LABEL,
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P984_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-PUBLIC-SELECTION: high-gap rows are selected before reconstruction.",
            "FALSE-POSITIVES-CHARGED: cumulative amortization charges every selected high-gap row.",
            "MATRIX-PROXY-ONLY: diversity uses compact relation proxies, not a solved sparse linear algebra instance.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm or target descent.",
        ],
        "method": "p984_p231_cumulative_high_gap_forward",
        "parameters": {
            "broad_label": BROAD_LABEL,
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "high_gap_rule": HIGH_GAP_RULE,
            "prior_sources": ["p982", "p983"],
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "windows": list(args.windows),
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summaries": [prior_summary, fresh_summary, cumulative_summary],
        "summary": {
            "control_pass": control_pass,
            "cumulative_broad_validation_success": success,
            "fresh_reconstruction_error_count": fresh_reconstruction_error_count,
            "reconstruction_error_count": reconstruction_error_count,
            **{f"fresh_{key}": value for key, value in fresh_counts.items() if key != "source_windows"},
            **{f"prior_{key}": value for key, value in prior_summary.items()},
            **{f"fresh_{key}": value for key, value in fresh_summary.items()},
            **{f"cumulative_{key}": value for key, value in cumulative_summary.items()},
        },
        "prior_cases": prior_rows,
        "prior_cases_compact": [compact_case(case) for case in prior_rows],
        "fresh_cases": fresh_rows,
        "fresh_cases_compact": [compact_case(case) for case in fresh_rows],
        "cumulative_cases_compact": [compact_case(case) for case in cumulative_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P984 contract path")
    parser.add_argument("--p982", default=str(DEFAULT_P982), help="P982 prior block JSON")
    parser.add_argument("--p983", default=str(DEFAULT_P983), help="P983 prior block JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target ids")
    parser.add_argument("--windows", nargs="+", default=list(DEFAULT_WINDOWS), help="Fresh validation windows")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} fresh_selected={fresh_selected} cumulative_selected={cum_selected} "
        "cumulative_broad_groups={broad_groups} cumulative_broad_amortized={broad_amortized} "
        "rank4_groups={rank4_groups} out={out}".format(
            claim=payload["claim_status"],
            fresh_selected=summary["fresh_selected_count"],
            cum_selected=summary["cumulative_selected_count"],
            broad_groups=summary["cumulative_broad_relation_group_count"],
            broad_amortized=summary["cumulative_broad_direct_relation_amortized_ops_over_rho"],
            rank4_groups=summary["cumulative_rank4_relation_group_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
