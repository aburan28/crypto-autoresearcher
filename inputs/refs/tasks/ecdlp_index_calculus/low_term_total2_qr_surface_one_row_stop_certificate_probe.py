#!/usr/bin/env python3
"""Select a public one-row stop certificate for live QR/scanner kernels.

The fused stop-rule audits can beat rho when the scalar-bearing public row is
charged before later rejected policy rows. This probe asks a narrower question:
can a public rule select exactly one QR row to scan, using only public-row fields
from prior live cache kernels, and still recover the scalar below rho on a later
held-out window?

This is a construction-target selector. It does not prove a complete ECDLP
solver because it still consumes prebuilt public QR/cache artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = (
    DEFAULT_STATE_DIR
    / "low_term_total2_qr_surface_one_row_stop_certificate_1032_1095_train_to_1096_1103_probe.json"
)

CERTIFICATE_RULES = (
    "first_selector_eval_public_zero",
    "first_selector_eval_public_zero_public_charge_lt_rho",
    "first_selector_eval_public_zero_selector_eval_le_16",
    "first_selector_eval_public_zero_selector_eval_le_32",
    "first_selector_eval_public_zero_selector_eval_le_48",
    "unique_public_zero",
    "first_artifact_public_zero",
)


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


def window_label(path: Path, payload: dict[str, Any]) -> str:
    match = re.search(r"(\d{4}_\d{4})", path.name)
    if match:
        return match.group(1)
    transfers = [
        int_value(group.get("transfer_index"))
        for group in payload.get("groups") or []
        if int_value(group.get("transfer_index")) > 0
    ]
    if transfers:
        return f"{min(transfers)}_{max(transfers)}"
    return "unknown"


def scanner_rows_by_key(group: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(row.get("row_key")): row
        for row in group.get("scanner_rows") or []
        if isinstance(row, dict)
    }


def public_rows(group: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in group.get("public_rows") or [] if isinstance(row, dict)]


def public_zero(row: dict[str, Any]) -> bool:
    return bool(row.get("public_zero_recovered")) and bool(
        row.get("quadratic_same_selected_root_pairs")
    )


def expected_root_count(row: dict[str, Any]) -> int:
    return len(row.get("expected_root_pairs") or [])


def selector_eval_order(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for _index, row in sorted(
            enumerate(rows),
            key=lambda item: (int_value(item[1].get("selector_eval_ops")), item[0]),
        )
    ]


def select_row(rule: str, rows: list[dict[str, Any]], rho: int) -> dict[str, Any] | None:
    if not rows:
        return None
    if rule.startswith("first_selector_eval_public_zero"):
        row = selector_eval_order(rows)[0]
        if not public_zero(row) or expected_root_count(row) <= 0:
            return None
        if rule.endswith("_public_charge_lt_rho") and int_value(row.get("public_charge")) >= rho:
            return None
        threshold_match = re.search(r"_selector_eval_le_(\d+)$", rule)
        if threshold_match and int_value(row.get("selector_eval_ops")) > int(threshold_match.group(1)):
            return None
        return row
    if rule == "unique_public_zero":
        recovered = [
            row
            for row in rows
            if public_zero(row) and expected_root_count(row) > 0
        ]
        return recovered[0] if len(recovered) == 1 else None
    if rule == "first_artifact_public_zero":
        row = rows[0]
        return row if public_zero(row) and expected_root_count(row) > 0 else None
    raise ValueError(f"unknown certificate rule: {rule}")


def scanner_lookup_for_row(scanner_row: dict[str, Any] | None, params: dict[str, Any]) -> int:
    if scanner_row:
        return int_value(params.get("scanner_lookup_ops_per_row"), 1)
    return 0


def public_lookup_for_row(public_row: dict[str, Any], params: dict[str, Any]) -> int:
    if public_zero(public_row):
        return int_value(params.get("public_lookup_ops_per_row"), 1)
    return 0


def fused_one_row_ops(
    public_row: dict[str, Any],
    scanner_row: dict[str, Any] | None,
    params: dict[str, Any],
    union_orchestration_ops: int,
) -> int:
    public_charge = int_value(public_row.get("public_charge"))
    if not scanner_row:
        return public_charge
    preassociation = int_value(scanner_row.get("scanner_preassociation_filter_ops"))
    relation_count = int_value(scanner_row.get("scanner_relation_count"))
    return (
        max(public_charge, preassociation)
        + relation_count * int_value(params.get("relation_derive_ops_per_relation"), 1)
        + public_lookup_for_row(public_row, params)
        + scanner_lookup_for_row(scanner_row, params)
        + union_orchestration_ops
    )


def compact_public_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "row_key": row.get("row_key"),
        "public_zero_recovered": bool(row.get("public_zero_recovered")),
        "quadratic_same_selected_root_pairs": row.get("quadratic_same_selected_root_pairs"),
        "expected_root_pair_count": expected_root_count(row),
        "selector_eval_ops": int_value(row.get("selector_eval_ops")),
        "public_charge": int_value(row.get("public_charge")),
        "selected_factor_hash": row.get("selected_factor_hash"),
    }


def compact_scanner_row(row: dict[str, Any] | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "row_key": row.get("row_key"),
        "scanner_row_public_key_verified": bool(row.get("scanner_row_public_key_verified")),
        "scanner_rank": int_value(row.get("scanner_rank")),
        "scanner_relation_count": int_value(row.get("scanner_relation_count")),
        "scanner_preassociation_filter_ops": int_value(
            row.get("scanner_preassociation_filter_ops")
        ),
        "expected_root_pairs": row.get("expected_root_pairs") or [],
    }


def audit_group(
    source: Path,
    window: str,
    params: dict[str, Any],
    group: dict[str, Any],
    rule: str,
) -> dict[str, Any]:
    rows = public_rows(group)
    scanner_by_row = scanner_rows_by_key(group)
    rho = int_value(group.get("rho"))
    selected = select_row(rule, rows, rho)
    selected_key = str(selected.get("row_key")) if selected else ""
    scanner_row = scanner_by_row.get(selected_key)
    one_row_scalar_verified = bool((scanner_row or {}).get("scanner_row_public_key_verified"))
    union_ops = int_value(group.get("union_orchestration_ops")) if one_row_scalar_verified else 0
    ops = (
        fused_one_row_ops(selected, scanner_row, params, union_ops)
        if selected
        else None
    )
    policy = str(params.get("policy") or "unknown")
    return {
        "source": str(source),
        "window": window,
        "policy": policy,
        "certificate_rule": rule,
        "target": group.get("target"),
        "transfer_index": int_value(group.get("transfer_index")),
        "challenge_seed": group.get("challenge_seed"),
        "rho": rho,
        "policy_row_count": len(rows),
        "public_recovered_row_count": sum(1 for row in rows if public_zero(row)),
        "public_rejected_row_count": sum(1 for row in rows if not public_zero(row)),
        "scanner_row_count": len(scanner_by_row),
        "selected": selected is not None,
        "selected_row": compact_public_row(selected),
        "selected_scanner_row": compact_scanner_row(scanner_row),
        "one_row_scalar_verified": one_row_scalar_verified,
        "one_row_ops": ops,
        "one_row_ops_over_rho": ratio(ops, rho),
        "one_row_below_rho": bool(one_row_scalar_verified and ops is not None and ops < rho),
        "live_cache_integrated_combined_ops_over_rho": group.get(
            "cache_integrated_combined_ops_over_rho"
        ),
        "strict_combined_ops_over_rho": group.get("strict_combined_ops_over_rho"),
        "scanner_union_public_key_verified": bool(group.get("scanner_union_public_key_verified")),
        "scanner_union_derived_secret": group.get("scanner_union_derived_secret"),
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
        params = payload.get("parameters") or {}
        window = window_label(path, payload)
        for group in payload.get("groups") or []:
            if not isinstance(group, dict):
                continue
            for rule in CERTIFICATE_RULES:
                cases.append(audit_group(path, window, params, group, rule))
    return cases, missing


def evaluate_rule(rule: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [case for case in cases if case.get("certificate_rule") == rule and case.get("selected")]
    abstained = [case for case in cases if case.get("certificate_rule") == rule and not case.get("selected")]
    verified = [case for case in selected if case.get("one_row_scalar_verified")]
    below = [case for case in verified if case.get("one_row_below_rho")]
    false_positive = [case for case in selected if not case.get("one_row_scalar_verified")]
    above = [case for case in verified if not case.get("one_row_below_rho")]
    min_ops = (
        min(number(case.get("one_row_ops_over_rho"), 999.0) for case in verified)
        if verified
        else None
    )
    mean_ops = (
        round(
            sum(number(case.get("one_row_ops_over_rho"), 999.0) for case in verified)
            / len(verified),
            8,
        )
        if verified
        else None
    )
    return {
        "certificate_rule": rule,
        "case_count": len([case for case in cases if case.get("certificate_rule") == rule]),
        "selected_count": len(selected),
        "abstained_count": len(abstained),
        "verified_count": len(verified),
        "below_rho_count": len(below),
        "above_rho_count": len(above),
        "false_positive_count": len(false_positive),
        "precision": ratio(len(verified), len(selected)),
        "success_rate": ratio(len(below), len(verified)),
        "min_one_row_ops_over_rho": min_ops,
        "mean_one_row_ops_over_rho": mean_ops,
        "below_rho_cases": below,
        "above_rho_cases": above,
        "false_positive_cases": false_positive,
        "best_verified_cases": sorted(
            verified,
            key=lambda case: number(case.get("one_row_ops_over_rho"), 999.0),
        )[:8],
    }


def score_row(row: dict[str, Any]) -> list[Any]:
    return [
        1 if int_value(row.get("below_rho_count")) == 0 else 0,
        int_value(row.get("false_positive_count")),
        int_value(row.get("above_rho_count")),
        -int_value(row.get("below_rho_count")),
        -int_value(row.get("verified_count")),
        number(row.get("mean_one_row_ops_over_rho"), 999.0),
        number(row.get("min_one_row_ops_over_rho"), 999.0),
        row.get("certificate_rule"),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-kernel-sources", nargs="+", type=Path, required=True)
    parser.add_argument("--test-kernel-sources", nargs="+", type=Path, required=True)
    parser.add_argument("--allow-missing-test-sources", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_cases, missing_train_sources = load_cases(args.train_kernel_sources, False)
    test_cases, missing_test_sources = load_cases(
        args.test_kernel_sources,
        args.allow_missing_test_sources,
    )
    training_scores = [evaluate_rule(rule, train_cases) for rule in CERTIFICATE_RULES]
    for row in training_scores:
        row["score_tuple"] = score_row(row)
    training_scores.sort(key=lambda row: row["score_tuple"])
    selected_rule = training_scores[0]["certificate_rule"] if training_scores else None
    selected_training_score = training_scores[0] if training_scores else None
    heldout_score = evaluate_rule(selected_rule, test_cases) if selected_rule else None
    output = {
        "schema": "ecdlp.low_term_total2_qr_surface_one_row_stop_certificate.v1",
        "created_at": now_iso(),
        "method": "prior_live_cache_public_one_row_stop_certificate_selection",
        "parameters": {
            "train_kernel_sources": [str(path) for path in args.train_kernel_sources],
            "test_kernel_sources": [str(path) for path in args.test_kernel_sources],
            "allow_missing_test_sources": bool(args.allow_missing_test_sources),
            "missing_train_sources": missing_train_sources,
            "missing_test_sources": missing_test_sources,
            "candidate_certificate_rules": list(CERTIFICATE_RULES),
            "score_order": [
                "require_training_below_rho_support",
                "min_false_positive_count",
                "min_above_rho_count",
                "max_below_rho_count",
                "max_verified_count",
                "min_mean_one_row_ops_over_rho",
                "min_best_one_row_ops_over_rho",
                "certificate_rule_tiebreak",
            ],
        },
        "selected_certificate_rule": selected_rule,
        "selected_training_score": selected_training_score,
        "training_scores": training_scores,
        "heldout_score": heldout_score,
        "honesty_boundary": [
            "The selected certificate is public with respect to live cache-kernel public rows, but it still consumes prebuilt public QR artifacts.",
            "A one-row scalar check uses scanner_row_public_key_verified; multi-row groups are not treated as one-row successes unless the selected row verifies by itself.",
            "This audit selects a stop certificate only; a full solver claim still needs generator-integrated row production and end-to-end source charging.",
        ],
    }
    write_json(args.out, output)
    print(json.dumps({"selected_certificate_rule": selected_rule, "heldout_score": heldout_score}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
