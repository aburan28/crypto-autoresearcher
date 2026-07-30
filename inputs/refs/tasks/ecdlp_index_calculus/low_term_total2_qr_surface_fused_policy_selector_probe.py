#!/usr/bin/env python3
"""Select a public QR policy using prior live fused-stop evidence.

The public QR aggregate selector chooses policies by surface recovery counts.
This probe instead reads prior live fused-stop artifacts and freezes one policy
for a future window using only prior fused accounting. It is a selector for the
current toy construction target, not a faster-than-rho ECDLP solver.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_FUSED_SOURCES = [
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1040_1047_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1048_1055_adaptive_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1056_1063_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1064_1071_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1072_1079_high_coeff_sum_accept_extra_probe.json",
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1080_1087_high_coeff_sum_accept_extra_probe.json",
]
DEFAULT_TEST_FUSED_SOURCES = [
    DEFAULT_STATE_DIR / "low_term_total2_qr_surface_live_fused_stop_rule_1088_1095_high_coeff_sum_accept_extra_probe.json",
]
DEFAULT_OUT = DEFAULT_STATE_DIR / "low_term_total2_qr_surface_fused_policy_selector_1040_1087_train_to_1088_1095_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def window_label(path: Path) -> str:
    match = re.search(r"(\d{4}_\d{4})", path.name)
    return match.group(1) if match else path.stem


def group_id(case: dict[str, Any]) -> str:
    return f"{case.get('window')}:{case.get('target')}:{case.get('transfer_index')}"


def compact_case(path: Path, case: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": str(path),
        "window": str(case.get("window") or window_label(path)),
        "policy": case.get("policy"),
        "target": case.get("target"),
        "transfer_index": int_value(case.get("transfer_index")),
        "rho": int_value(case.get("rho")),
        "scalar_verified": bool(case.get("scalar_verified")),
        "fused_until_scalar_below_rho": bool(case.get("fused_until_scalar_below_rho")),
        "fused_until_scalar_ops": int_value(case.get("fused_until_scalar_ops")),
        "fused_until_scalar_ops_over_rho": case.get("fused_until_scalar_ops_over_rho"),
        "fused_all_fixed_policy_below_rho": bool(case.get("fused_all_fixed_policy_below_rho")),
        "fused_all_fixed_policy_ops_over_rho": case.get("fused_all_fixed_policy_ops_over_rho"),
        "live_cache_integrated_combined_below_rho": bool(
            case.get("live_cache_integrated_combined_below_rho")
        ),
        "live_cache_integrated_combined_ops_over_rho": case.get(
            "live_cache_integrated_combined_ops_over_rho"
        ),
        "strict_sum_until_scalar_below_rho": bool(case.get("strict_sum_until_scalar_below_rho")),
        "public_until_scalar_ops_over_rho": case.get("public_until_scalar_ops_over_rho"),
        "policy_row_count": int_value(case.get("policy_row_count")),
        "rejected_policy_row_count": int_value(case.get("rejected_policy_row_count")),
        "scanner_row_count": int_value(case.get("scanner_row_count")),
        "scanner_required_row_keys": case.get("scanner_required_row_keys") or [],
        "union_derived_secret": (case.get("scanner_union") or {}).get("union_derived_secret"),
    }


def load_cases(paths: list[Path], allow_missing: bool) -> tuple[list[dict[str, Any]], list[str]]:
    cases: list[dict[str, Any]] = []
    missing: list[str] = []
    for path in paths:
        if not path.exists():
            if allow_missing:
                missing.append(str(path))
                continue
            raise FileNotFoundError(path)
        payload = load_json(path)
        for case in payload.get("cases") or []:
            if isinstance(case, dict):
                cases.append(compact_case(path, case))
    return cases, missing


def evaluate_policy(policy: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [case for case in cases if case.get("policy") == policy]
    verified = [case for case in selected if case.get("scalar_verified")]
    below = [case for case in verified if case.get("fused_until_scalar_below_rho")]
    above = [case for case in verified if not case.get("fused_until_scalar_below_rho")]
    near = [
        case
        for case in above
        if number(case.get("fused_until_scalar_ops_over_rho"), 999.0) <= 1.05
    ]
    unique_below_groups = {group_id(case) for case in below}
    unique_verified_groups = {group_id(case) for case in verified}
    min_ops = (
        min(number(case.get("fused_until_scalar_ops_over_rho"), 999.0) for case in verified)
        if verified
        else None
    )
    mean_ops = (
        round(
            sum(number(case.get("fused_until_scalar_ops_over_rho"), 999.0) for case in verified)
            / len(verified),
            8,
        )
        if verified
        else None
    )
    mean_public_until = (
        round(
            sum(number(case.get("public_until_scalar_ops_over_rho"), 999.0) for case in verified)
            / len(verified),
            8,
        )
        if verified
        else None
    )
    rejected_rows = sum(int_value(case.get("rejected_policy_row_count")) for case in verified)
    source_windows = sorted({case.get("window") for case in selected if case.get("window")})
    return {
        "policy": policy,
        "source_window_count": len(source_windows),
        "source_windows": source_windows,
        "case_count": len(selected),
        "verified_count": len(verified),
        "verified_unique_group_count": len(unique_verified_groups),
        "below_rho_count": len(below),
        "below_rho_unique_group_count": len(unique_below_groups),
        "near_miss_le_1p05_count": len(near),
        "above_rho_count": len(above),
        "success_rate": ratio(len(below), len(verified)),
        "rejected_policy_row_count": rejected_rows,
        "min_fused_until_scalar_ops_over_rho": min_ops,
        "mean_fused_until_scalar_ops_over_rho": mean_ops,
        "mean_public_until_scalar_ops_over_rho": mean_public_until,
        "below_rho_cases": below,
        "near_miss_cases": near,
        "best_verified_cases": sorted(
            verified,
            key=lambda case: number(case.get("fused_until_scalar_ops_over_rho"), 999.0),
        )[:5],
    }


def score_policy(row: dict[str, Any], min_source_windows: int) -> list[Any]:
    has_support = int_value(row.get("below_rho_unique_group_count")) > 0
    enough_sources = int_value(row.get("source_window_count")) >= min_source_windows
    return [
        0 if enough_sources else 1,
        0 if has_support else 1,
        -int_value(row.get("below_rho_unique_group_count")),
        int_value(row.get("above_rho_count")),
        int_value(row.get("rejected_policy_row_count")),
        number(row.get("mean_fused_until_scalar_ops_over_rho"), 999.0),
        number(row.get("min_fused_until_scalar_ops_over_rho"), 999.0),
        row.get("policy"),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-fused-sources", nargs="+", type=Path, default=DEFAULT_TRAIN_FUSED_SOURCES)
    parser.add_argument("--test-fused-sources", nargs="+", type=Path, default=DEFAULT_TEST_FUSED_SOURCES)
    parser.add_argument(
        "--candidate-policies",
        default="",
        help="Comma-separated policy names. Defaults to all policies seen in the training fused cases.",
    )
    parser.add_argument(
        "--min-source-windows",
        type=int,
        default=2,
        help="Minimum training windows before a policy is treated as sufficiently covered.",
    )
    parser.add_argument(
        "--allow-missing-test-sources",
        action="store_true",
        help="Permit absent test artifacts so the selected policy can be pre-registered before a future window exists.",
    )
    parser.add_argument("--test-window", default="", help="Optional future-window label for the frozen policy.")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_cases, missing_train_sources = load_cases(args.train_fused_sources, False)
    test_cases, missing_test_sources = load_cases(args.test_fused_sources, args.allow_missing_test_sources)
    if args.candidate_policies:
        policies = [item.strip() for item in args.candidate_policies.split(",") if item.strip()]
    else:
        policies = sorted({case.get("policy") for case in train_cases if case.get("policy")})
    training_scores = [evaluate_policy(policy, train_cases) for policy in policies]
    for row in training_scores:
        row["score_tuple"] = score_policy(row, args.min_source_windows)
    training_scores.sort(key=lambda row: row["score_tuple"])
    selected = training_scores[0] if training_scores else None
    selected_policy = selected.get("policy") if selected else None
    heldout_score = evaluate_policy(selected_policy, test_cases) if selected_policy else None
    payload = {
        "schema": "ecdlp.low_term_total2_qr_surface_fused_policy_selector.v1",
        "created_at": now_iso(),
        "method": "prior_live_fused_stop_policy_selection",
        "parameters": {
            "train_fused_sources": [str(path) for path in args.train_fused_sources],
            "test_fused_sources": [str(path) for path in args.test_fused_sources],
            "candidate_policies": policies,
            "min_source_windows": args.min_source_windows,
            "allow_missing_test_sources": bool(args.allow_missing_test_sources),
            "missing_train_sources": missing_train_sources,
            "missing_test_sources": missing_test_sources,
            "test_window": args.test_window,
            "score_order": [
                "min_missing_training_window_coverage",
                "require_training_below_rho_support",
                "max_unique_below_rho_groups",
                "min_above_rho_count",
                "min_rejected_policy_rows",
                "min_mean_fused_until_scalar_ops_over_rho",
                "min_best_fused_until_scalar_ops_over_rho",
                "policy_name_tiebreak",
            ],
        },
        "selected_policy": selected_policy,
        "selected_training_score": selected,
        "training_scores": training_scores,
        "heldout_score": heldout_score,
        "honesty_boundary": [
            "This selector consumes prior live fused-stop artifacts, so it can only be used after those policies have been materialized on training windows.",
            "Policies without enough prior fused windows are penalized rather than promoted from one same-window near miss.",
            "The selected policy must still be validated with cache-integrated, strict-sum, all-policy fused, and rejected-row controls on the held-out window.",
        ],
    }
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "selected_policy": selected_policy,
                "selected_training_score": selected,
                "heldout_score": heldout_score,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
