#!/usr/bin/env python3
"""P986 adaptive later-window validation of the P985 public high-gap guard."""

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
import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p986_p231_adaptive_high_gap_guard_validation.md"
DEFAULT_P985 = STATE_DIR / "low_term_total2_p985_p231_cumulative_false_positive_discriminator_probe.json"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p986_p231_adaptive_high_gap_guard_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p986_p231_adaptive_high_gap_guard_validation.v1"
FROZEN_GUARD = p985.PublicGuard(feature="max_salt", modulus=2, allowed=(0,))


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


def window_label(start: int) -> str:
    return f"{start}_{start + 7}"


def candidate_windows(start_transfer: int, stop_transfer: int, max_scan_windows: int) -> tuple[list[str], list[str]]:
    available: list[str] = []
    missing: list[str] = []
    current = start_transfer
    attempted = 0
    while current <= stop_transfer and attempted < max_scan_windows:
        window = window_label(current)
        if p868.source_path(window).exists():
            available.append(window)
        else:
            missing.append(window)
        current += 8
        attempted += 1
    return available, missing


def p985_controls(p985_payload: dict[str, Any]) -> dict[str, Any]:
    summary = p985_payload.get("summary") or {}
    promoted = ((p985_payload.get("calibration") or {}).get("promoted_guard") or {}).get("name")
    return {
        "p985_claim_expected": p985_payload.get("claim_status")
        == "NEGATIVE_RESULT_P985_DISCRIMINATOR_SELECTS_NO_VALIDATION_ROWS",
        "p985_control_pass": bool(summary.get("control_pass")),
        "p985_calibration_pass": bool(summary.get("calibration_pass")),
        "p985_guard_expected": promoted == FROZEN_GUARD.name,
        "p985_zero_high_gap_validation": int_value(summary.get("validation_high_gap_selected_case_count")) == 0,
    }


def scan_adaptive(
    args: argparse.Namespace,
    guard: p985.PublicGuard,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    available, missing = candidate_windows(args.start_transfer, args.stop_transfer, args.max_scan_windows)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    source_case_count_by_window: Counter[str] = Counter()
    first_stage_count_by_window: Counter[str] = Counter()
    second_stage_count_by_window: Counter[str] = Counter()
    high_gap_count_by_window: Counter[str] = Counter()
    guarded_count_by_window: Counter[str] = Counter()
    window_reports: list[dict[str, Any]] = []
    nonempty_high_gap_windows: list[str] = []
    high_gap_selected: list[dict[str, Any]] = []
    guarded_selected: list[dict[str, Any]] = []
    scanned_windows: list[str] = []

    for window in available:
        source = p868.load_json(p868.source_path(window))
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

        scanned_windows.append(window)
        window_high_gap_before = sum(high_gap_count_by_window.values())
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
            if not p985.high_gap_rule(public_features):
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
            high_gap_selected.append(row)
            if p985.guard_passes(row, guard):
                guarded_count_by_window[window] += 1
                guarded_selected.append(row)

        window_report = {
            "first_stage_selected_case_count": first_stage_count_by_window[window],
            "guarded_selected_case_count": guarded_count_by_window[window],
            "high_gap_selected_case_count": high_gap_count_by_window[window],
            "second_stage_selected_case_count": second_stage_count_by_window[window],
            "source_case_count": source_case_count_by_window[window],
            "source_path": str(p868.source_path(window)),
            "window": window,
        }
        window_reports.append(window_report)
        if sum(high_gap_count_by_window.values()) > window_high_gap_before:
            nonempty_high_gap_windows.append(window)
        if (
            len(nonempty_high_gap_windows) >= args.max_nonempty_windows
            and sum(high_gap_count_by_window.values()) >= args.min_high_gap_rows
        ):
            break

    if len(nonempty_high_gap_windows) >= args.max_nonempty_windows:
        stopped_reason = "max_nonempty_windows"
    elif sum(high_gap_count_by_window.values()) >= args.min_high_gap_rows and args.stop_after_min_rows:
        stopped_reason = "min_high_gap_rows"
    else:
        stopped_reason = "scan_budget_exhausted"

    counts = {
        "available_candidate_window_count": len(available),
        "available_candidate_windows": available,
        "first_stage_selected_case_count": sum(first_stage_count_by_window.values()),
        "first_stage_selected_count_by_window": dict(first_stage_count_by_window),
        "guarded_selected_case_count": sum(guarded_count_by_window.values()),
        "guarded_selected_count_by_window": dict(guarded_count_by_window),
        "high_gap_selected_case_count": sum(high_gap_count_by_window.values()),
        "high_gap_selected_count_by_window": dict(high_gap_count_by_window),
        "missing_candidate_window_count": len(missing),
        "missing_candidate_windows": missing,
        "nonempty_high_gap_window_count": len(nonempty_high_gap_windows),
        "nonempty_high_gap_windows": nonempty_high_gap_windows,
        "scanned_window_count": len(scanned_windows),
        "scanned_windows": scanned_windows,
        "second_stage_selected_case_count": sum(second_stage_count_by_window.values()),
        "second_stage_selected_count_by_window": dict(second_stage_count_by_window),
        "source_case_count": sum(source_case_count_by_window.values()),
        "source_count_by_window": dict(source_case_count_by_window),
        "source_windows": {window: str(p868.source_path(window)) for window in scanned_windows},
        "stopped_reason": stopped_reason,
        "window_reports": window_reports,
    }
    return high_gap_selected, guarded_selected, counts


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p985_path = Path(args.p985)
    p985_payload = load_json(p985_path)
    controls = p985_controls(p985_payload)
    control_pass = all(controls.values())
    high_gap_rows, guarded_rows, scan_counts = scan_adaptive(args, FROZEN_GUARD)
    high_gap_summary = p985.summarize_selected("adaptive_high_gap", high_gap_rows)
    guarded_summary = p985.summarize_selected("adaptive_guarded", guarded_rows)
    missed_broad_rows = [row for row in high_gap_rows if p985.is_broad(row) and not p985.guard_passes(row, FROZEN_GUARD)]
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in guarded_rows)
    high_gap_reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in high_gap_rows)

    success = bool(
        control_pass
        and high_gap_summary["selected_count"] > 0
        and high_gap_reconstruction_error_count == 0
        and guarded_summary["selected_count"] > 0
        and guarded_summary["broad_relation_group_count"] > 0
        and (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) < 1.0
        and not missed_broad_rows
    )
    if not control_pass:
        claim = "NEGATIVE_RESULT_P986_CONTROL_FAILURE"
    elif scan_counts["available_candidate_window_count"] == 0:
        claim = "NEGATIVE_RESULT_P986_NO_AVAILABLE_LATER_WINDOWS"
    elif high_gap_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P986_NO_HIGH_GAP_ROWS_IN_SCAN_BUDGET"
    elif high_gap_reconstruction_error_count != 0:
        claim = "NEGATIVE_RESULT_P986_RECONSTRUCTION_ERRORS"
    elif missed_broad_rows:
        claim = "NEGATIVE_RESULT_P986_GUARD_MISSES_ADAPTIVE_BROAD_ROWS"
    elif guarded_summary["selected_count"] == 0:
        claim = "NEGATIVE_RESULT_P986_GUARD_SELECTS_NO_ADAPTIVE_ROWS"
    elif guarded_summary["broad_relation_group_count"] == 0:
        claim = "NEGATIVE_RESULT_P986_GUARD_HAS_NO_BROAD_ROWS"
    elif (guarded_summary["broad_direct_relation_amortized_ops_over_rho"] or 10**9) >= 1.0:
        claim = "NEGATIVE_RESULT_P986_GUARD_NOT_BELOW_RHO_ON_ADAPTIVE_WINDOWS"
    elif success:
        claim = "P986_ADAPTIVE_GUARD_VALIDATES_BELOW_RHO_ON_NONEMPTY_WINDOWS"
    else:
        claim = "NEGATIVE_RESULT_P986_DIVERSITY_OR_INVARIANT_FAILURE"

    return {
        "artifacts": {
            "contract": str(args.contract),
            "p985_source": str(p985_path),
            "script": str(Path(__file__)),
            "source_windows": scan_counts["source_windows"],
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p985_source_sha256": sha256_file(p985_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "broad_label": p985.BROAD_LABEL,
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P986_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-GUARD: guard is imported from P985 calibration and not reselected here.",
            "PUBLIC-ADAPTIVE-WINDOWS: window inclusion uses public first-stage, second-stage, and high-gap availability.",
            "FALSE-POSITIVES-CHARGED: guarded amortization charges every guarded selected row.",
            "NO-END-TO-END-BREAK: this is not a complete faster-than-rho ECDLP algorithm, sparse linear algebra result, or target descent.",
        ],
        "method": "p986_p231_adaptive_high_gap_guard_validation",
        "parameters": {
            "base_high_gap_rule": p985.HIGH_GAP_RULE,
            "broad_label": p985.BROAD_LABEL,
            "first_stage_rule": p872.FIRST_STAGE_RULE,
            "frozen_guard": {"name": FROZEN_GUARD.name, "rule": FROZEN_GUARD.rule},
            "max_nonempty_windows": args.max_nonempty_windows,
            "max_scan_windows": args.max_scan_windows,
            "min_high_gap_rows": args.min_high_gap_rows,
            "second_stage_rule": p872.SECOND_STAGE_RULE,
            "start_transfer": args.start_transfer,
            "stop_after_min_rows": args.stop_after_min_rows,
            "stop_transfer": args.stop_transfer,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "scan": scan_counts,
        "schema": SCHEMA,
        "source_controls": controls,
        "summaries": [high_gap_summary, guarded_summary],
        "summary": {
            "control_pass": control_pass,
            "guard_validation_success": success,
            "high_gap_reconstruction_error_count": high_gap_reconstruction_error_count,
            "missed_broad_count": len(missed_broad_rows),
            "reconstruction_error_count": reconstruction_error_count,
            **{f"scan_{key}": value for key, value in scan_counts.items() if key not in ("source_windows", "window_reports")},
            **{f"high_gap_{key}": value for key, value in high_gap_summary.items()},
            **{f"guarded_{key}": value for key, value in guarded_summary.items()},
        },
        "validation_high_gap_cases": high_gap_rows,
        "validation_high_gap_cases_compact": [p985.compact_case(row, FROZEN_GUARD) for row in high_gap_rows],
        "validation_guarded_cases": guarded_rows,
        "validation_guarded_cases_compact": [p985.compact_case(row, FROZEN_GUARD) for row in guarded_rows],
        "missed_broad_cases_compact": [p985.compact_case(row, FROZEN_GUARD) for row in missed_broad_rows],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P986 contract path")
    parser.add_argument("--p985", default=str(DEFAULT_P985), help="P985 guard/control JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target ids")
    parser.add_argument("--start-transfer", type=int, default=11680, help="First transfer-window start")
    parser.add_argument("--stop-transfer", type=int, default=11896, help="Last transfer-window start")
    parser.add_argument("--max-scan-windows", type=int, default=28, help="Maximum candidate windows to inspect")
    parser.add_argument("--max-nonempty-windows", type=int, default=3, help="Stop after this many high-gap nonempty windows")
    parser.add_argument("--min-high-gap-rows", type=int, default=1, help="Minimum high-gap rows before adaptive stop can fire")
    parser.add_argument(
        "--stop-after-min-rows",
        action="store_true",
        help="Stop after min-high-gap-rows even if max-nonempty-windows has not been reached",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} windows={windows} nonempty={nonempty} high_gap={high_gap} "
        "guarded={guarded} guarded_broad_groups={broad_groups} "
        "guarded_broad_amortized={broad_amortized} missed_broad={missed} out={out}".format(
            claim=payload["claim_status"],
            windows=summary["scan_scanned_window_count"],
            nonempty=summary["scan_nonempty_high_gap_window_count"],
            high_gap=summary["scan_high_gap_selected_case_count"],
            guarded=summary["scan_guarded_selected_case_count"],
            broad_groups=summary["guarded_broad_relation_group_count"],
            broad_amortized=summary["guarded_broad_direct_relation_amortized_ops_over_rho"],
            missed=summary["missed_broad_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
