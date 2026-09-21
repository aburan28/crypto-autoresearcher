#!/usr/bin/env python3
"""P1064 chronology-safe validation of the P1063 high-mean-ops signal."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1055_p231_source_charged_rank_audit as p1055
import low_term_total2_p1059_p231_rowkey_prefix_shared_source as p1059
import low_term_total2_p1063_p231_free_column_source_construction as p1063


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1064_p231_chronology_safe_high_mean_ops.md"
DEFAULT_P1054 = STATE_DIR / "low_term_total2_p1054_p231_public_materialization_gate_probe.json"
DEFAULT_P1059 = STATE_DIR / "low_term_total2_p1059_p231_rowkey_prefix_shared_source_probe.json"
DEFAULT_P1063 = STATE_DIR / "low_term_total2_p1063_p231_free_column_source_construction_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1064_p231_chronology_safe_high_mean_ops_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1064_p231_chronology_safe_high_mean_ops.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def digest_paths(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted({path for path in paths if path.exists()}):
        digest.update(str(path).encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact_result(result: dict[str, Any], max_windows: int = 24, max_cases: int = 16) -> dict[str, Any]:
    compact = dict(result)
    windows = compact.get("selected_windows") or []
    cases = compact.get("selected_case_details") or []
    compact["selected_windows"] = windows[:max_windows]
    compact["selected_windows_truncated"] = len(windows) > max_windows
    compact["selected_case_details"] = cases[:max_cases]
    compact["selected_case_details_truncated"] = len(cases) > max_cases
    return compact


def expression_from_p1063(path: Path) -> str:
    payload = load_json(path)
    expression = ((payload.get("summary") or {}).get("oracle_best_expression"))
    if not expression:
        raise ValueError(f"P1063 artifact has no oracle_best_expression: {path}")
    return str(expression)


def discovery_end_from_p1063(path: Path, anchor_window: str) -> int:
    payload = load_json(path)
    candidates = ((payload.get("controls") or {}).get("forward_oracle_candidates") or [])
    if not candidates:
        raise ValueError(f"P1063 artifact has no forward oracle candidates: {path}")
    windows = ((candidates[0].get("union") or {}).get("selected_windows") or [])
    discovery_windows = [window for window in windows if window != anchor_window]
    if not discovery_windows:
        raise ValueError("P1063 oracle has no non-anchor discovery window")
    return max(int(window.split("_", 1)[1]) for window in discovery_windows)


def condition_expression(feature: str, op: str, threshold: float) -> str:
    value = f"{threshold:.8f}".rstrip("0").rstrip(".")
    return f"{feature} {op} {value}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p1054", type=Path, default=DEFAULT_P1054)
    parser.add_argument("--p1059", type=Path, default=DEFAULT_P1059)
    parser.add_argument("--p1063", type=Path, default=DEFAULT_P1063)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--factor-glob", default=p1055.DEFAULT_FACTOR_GLOB)
    parser.add_argument("--selected-glob", default=p1055.DEFAULT_SELECTED_GLOB)
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--column", type=int, default=15)
    parser.add_argument("--priority-columns", default="6,7,10,14,15")
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--source", default="direct_source")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--train-min-start", type=int, default=10000)
    parser.add_argument("--train-max-start", type=int, default=11887)
    parser.add_argument("--gap-min-start", type=int, default=11888)
    parser.add_argument("--gap-max-start", type=int, default=11983)
    parser.add_argument("--forward-min-start", type=int, default=12200)
    parser.add_argument("--anchor-window", default="18464_18471")
    args = parser.parse_args()

    priority_columns = [int(item) for item in args.priority_columns.split(",") if item.strip()]
    selected_rowkey = p1063.selected_rowkey_from_p1059(args.p1059)
    records, p1054_expression, input_paths = p1063.load_p1054_records(args)
    forward_rows = [row for row in records if row["split"] == "forward_validation"]
    exact_expression = expression_from_p1063(args.p1063)
    discovery_end = discovery_end_from_p1063(args.p1063, args.anchor_window)
    validation_rows = [row for row in forward_rows if row["window_start"] > discovery_end]
    anchor_rows = [row for row in validation_rows if row["window"] == args.anchor_window]
    if not anchor_rows:
        raise ValueError(f"anchor window {args.anchor_window} is not in the validation split")

    cache: dict[Path, list[dict[str, Any]]] = {}
    bundles = p1063.prepare_bundles(forward_rows, cache, args)
    exact_selector = p1059.rowkey_first_selector(selected_rowkey)
    anchor_selector = p1063.exact_anchor_forward(exact_selector, args.anchor_window)
    anchor = p1063.evaluate_fast(anchor_rows, exact_selector, bundles, args)
    full_validation = p1063.evaluate_fast(validation_rows, p1059.all_cases_selector, bundles, args)
    full_validation_stats = p1063.marginal_stats(anchor, full_validation, priority_columns)

    anchor_mean = p1055.float_value(anchor_rows[0].get("mean_ops")) or 0.0
    relaxed_expression = condition_expression("mean_ops", ">=", anchor_mean)
    exact_rule = p1055.compile_rule(exact_expression)
    relaxed_rule = p1055.compile_rule(relaxed_expression)

    exact_result = p1063.evaluate_fast(
        validation_rows,
        p1063.union_selectors([anchor_selector, p1063.all_cases_when(exact_rule)]),
        bundles,
        args,
    )
    exact_stats = p1063.marginal_stats(anchor, exact_result, priority_columns)
    relaxed_result = p1063.evaluate_fast(
        validation_rows,
        p1063.union_selectors([anchor_selector, p1063.all_cases_when(relaxed_rule)]),
        bundles,
        args,
    )
    relaxed_stats = p1063.marginal_stats(anchor, relaxed_result, priority_columns)

    strict_success = exact_stats["marginal_rank_gain"] > 0 and exact_stats["marginal_charge_over_rho"] < 1.0
    relaxed_cost_reduced = (
        relaxed_stats["marginal_rank_gain"] > 0
        and relaxed_stats["marginal_charge_over_rho"] < full_validation_stats["marginal_charge_over_rho"]
    )
    relaxed_below_rho = relaxed_stats["marginal_rank_gain"] > 0 and relaxed_stats["marginal_charge_over_rho"] < 1.0

    if strict_success:
        claim_status = "POSITIVE_SIGNAL_P1064_EXACT_HIGH_MEAN_CHRONOLOGY_BELOW_RHO"
    elif relaxed_below_rho:
        claim_status = "POSITIVE_SIGNAL_P1064_RELAXED_HIGH_MEAN_CHRONOLOGY_BELOW_RHO"
    elif relaxed_cost_reduced:
        claim_status = "POSITIVE_SIGNAL_P1064_RELAXED_HIGH_MEAN_COLUMN10_COST_REDUCED_NOT_RHO"
    elif exact_stats["marginal_rank_gain"] <= 0:
        claim_status = "NEGATIVE_RESULT_P1064_EXACT_HIGH_MEAN_NO_HOLDOUT_COVERAGE"
    else:
        claim_status = "NEGATIVE_RESULT_P1064_HIGH_MEAN_NO_COST_REDUCTION"

    payload = {
        "artifact_hashes": {
            "contract": sha256_file(args.contract) if args.contract.exists() else None,
            "input_artifact_count": len([path for path in input_paths if path.exists()]),
            "input_artifact_digest": digest_paths(input_paths),
            "p1054": sha256_file(args.p1054) if args.p1054.exists() else None,
            "p1059": sha256_file(args.p1059) if args.p1059.exists() else None,
            "p1063": sha256_file(args.p1063) if args.p1063.exists() else None,
            "script": sha256_file(Path(__file__)),
        },
        "artifacts": {
            "contract": str(args.contract),
            "p1054": str(args.p1054),
            "p1059": str(args.p1059),
            "p1063": str(args.p1063),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "claim_taxonomy": [
            "TOY-EVIDENCE",
            "MODEL-BOUND",
            "NO-SALT-REPLAY",
            "DISCOVERY-DERIVED",
            "ANCHOR-DERIVED-RELAXATION",
            "CHRONOLOGY-SAFE-HOLDOUT",
            "FREE-COLUMN-PRESSURE",
            "POLLARD-RHO-BOUNDARY",
            "TARGET-DESCENT-OPEN",
        ],
        "controls": {
            "anchor": compact_result(anchor),
            "exact_high_mean": compact_result(exact_result),
            "exact_high_mean_stats": exact_stats,
            "full_validation": compact_result(full_validation),
            "full_validation_stats": full_validation_stats,
            "relaxed_anchor_mean": compact_result(relaxed_result),
            "relaxed_anchor_mean_stats": relaxed_stats,
        },
        "honesty_boundary": {
            "anchor_mean_relaxation_uses_prior_p1059_anchor": True,
            "cryptographic_scale_unproved": True,
            "exact_p1063_threshold_is_discovery_derived": True,
            "not_a_complete_index_calculus_algorithm": True,
            "not_a_deployed_curve_break": True,
            "relaxed_signal_above_rho": not relaxed_below_rho,
            "target_descent_not_implemented": True,
        },
        "parameters": {
            "anchor_mean_ops": round(anchor_mean, 8),
            "anchor_window": args.anchor_window,
            "column": args.column,
            "discovery_end": discovery_end,
            "exact_expression": exact_expression,
            "order": args.order,
            "p1054_rule": p1054_expression,
            "priority_columns": priority_columns,
            "relaxed_expression": relaxed_expression,
            "selected_rowkey_control": list(selected_rowkey),
            "selector": args.selector,
            "source": args.source,
            "target": args.target,
            "top_k": args.top_k,
        },
        "record_counts": {
            "anchor_windows": len(anchor_rows),
            "forward_windows": len(forward_rows),
            "validation_windows": len(validation_rows),
        },
        "schema": SCHEMA,
        "summary": {
            "anchor_exact_charge": anchor["strict_source_charge_over_rho"],
            "anchor_exact_free_columns": anchor["base_plus_source_free_columns"],
            "anchor_exact_rank_gain": anchor["source_rank_gain_over_base"],
            "claim_status": claim_status,
            "exact_expression": exact_expression,
            "exact_marginal_charge": exact_stats["marginal_charge_over_rho"],
            "exact_marginal_rank_gain": exact_stats["marginal_rank_gain"],
            "exact_removed_free_columns": exact_stats["removed_free_columns"],
            "full_validation_marginal_charge": full_validation_stats["marginal_charge_over_rho"],
            "full_validation_marginal_rank_gain": full_validation_stats["marginal_rank_gain"],
            "full_validation_removed_free_columns": full_validation_stats["removed_free_columns"],
            "relaxed_expression": relaxed_expression,
            "relaxed_marginal_charge": relaxed_stats["marginal_charge_over_rho"],
            "relaxed_marginal_rank_gain": relaxed_stats["marginal_rank_gain"],
            "relaxed_removed_free_columns": relaxed_stats["removed_free_columns"],
            "strict_success": strict_success,
            "weak_positive": strict_success or relaxed_cost_reduced,
        },
        "timestamp_utc": now_iso(),
    }
    payload["strict_success"] = bool(strict_success)
    write_json(args.out, payload)
    print(
        "claim={claim} strict_success={success} exact_gain={exact_gain} "
        "relaxed_gain={relaxed_gain} relaxed_charge={relaxed_charge} "
        "full_charge={full_charge} out={out}".format(
            claim=claim_status,
            success=payload["strict_success"],
            exact_gain=payload["summary"]["exact_marginal_rank_gain"],
            relaxed_gain=payload["summary"]["relaxed_marginal_rank_gain"],
            relaxed_charge=payload["summary"]["relaxed_marginal_charge"],
            full_charge=payload["summary"]["full_validation_marginal_charge"],
            out=args.out,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
