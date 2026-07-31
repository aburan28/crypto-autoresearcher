#!/usr/bin/env python3
"""P997 frozen forward validation for the p231 top-k-16 leaf89 rule."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p996_p231_early_stop_recall_split as p996


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p997_p231_frozen_top16_leaf89_forward.md"
DEFAULT_P993 = STATE_DIR / "low_term_total2_p993_p231_branch_switch_selector_scout_probe.json"
DEFAULT_P994 = STATE_DIR / "low_term_total2_p994_p231_fixed_branch_forward_validation_probe.json"
DEFAULT_P995 = STATE_DIR / "low_term_total2_p995_p231_branch_precision_guard_probe.json"
DEFAULT_P996 = STATE_DIR / "low_term_total2_p996_p231_early_stop_recall_split_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p997_p231_frozen_top16_leaf89_forward_probe.json"
SCHEMA = "ecdlp.low_term_total2_p997_p231_frozen_top16_leaf89_forward.v1"
DEFAULT_WINDOW = "11928_11935"
DEFAULT_TARGET = "22050.cf1@11731"


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


def safe_ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def p996_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "p996_claim_expected": payload.get("claim_status") == "P996_EARLY_STOP_BELOW_RHO_WITH_RECALL_EXTENSION_DIAGNOSTIC",
        "p996_control_pass": bool(summary.get("control_pass")),
        "p996_guard_first_below_rho": (summary.get("p995_guard_first_derivation_ops_over_rho") or 10**9) < 1.0,
        "p996_recall_extension_clean": summary.get("recall_extension_precision") == 1.0 and summary.get("recall_extension_recall") == 1.0,
    }


def useful_amortized(selection: dict[str, Any]) -> float | None:
    return safe_ratio(selection.get("selected_direct_sum_ops_over_rho"), selection.get("selected_positive_count"))


def determine_claim(control_pass: bool, source_exists: bool, top16: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P997_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P997_SOURCE_WINDOW_MISSING"
    selection = top16.get("validation_selection") or {}
    reconstruction = top16.get("reconstruction") or {}
    early_stop = top16.get("early_stop") or {}
    if int_value(selection.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P997_FROZEN_TOP16_LEAF89_MISSES_FORWARD_SOURCE_SIGNAL"
    if (selection.get("precision_lift_over_prevalence") or 0.0) <= 1.0:
        return "P997_FROZEN_TOP16_LEAF89_RECALLS_FORWARD_WITHOUT_LIFT"
    if int_value(reconstruction.get("reconstruction_error_count")):
        return "P997_FROZEN_TOP16_LEAF89_RECALLS_FORWARD_BUT_RECONSTRUCTION_ERRORS"
    if int_value(reconstruction.get("secret_deriving_group_count")) == 0:
        return "P997_FROZEN_TOP16_LEAF89_FORWARD_SIGNAL_WITHOUT_SECRET_DERIVATION"
    if (useful_amortized(selection) or 10**9) < 1.0:
        return "P997_FROZEN_TOP16_LEAF89_FORWARD_USEFUL_AMORTIZED_BELOW_RHO"
    if early_stop.get("first_derivation_below_rho"):
        return "P997_FROZEN_TOP16_LEAF89_FORWARD_EARLY_STOP_BELOW_RHO"
    return "NEGATIVE_RESULT_P997_FROZEN_TOP16_LEAF89_EARLY_STOP_NOT_BELOW_RHO"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p996_path = Path(args.p996)
    p996_payload = load_json(p996_path)
    controls = p996_controls(p996_payload)
    control_pass = all(controls.values())
    source_path = p868.source_path(args.window)
    source_exists = source_path.exists()
    p996_args = argparse.Namespace(
        contract=args.contract,
        min_source_rank=args.min_source_rank,
        p993=args.p993,
        p994=args.p994,
        p995=args.p995,
        targets=args.targets,
        train_transfer_max=-1,
        window=args.window,
    )
    base_payload = p996.analyze(p996_args) if source_exists else {"rule_results": {}, "summary": {}}
    top16 = (base_payload.get("rule_results") or {}).get("top16_leaf89_recall_extension") or {}
    selection = top16.get("validation_selection") or {}
    claim = determine_claim(control_pass, source_exists, top16)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p996_source": str(p996_path),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p996_source_sha256": sha256_file(p996_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P997_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FORWARD: top_k <= 16 AND leaf89 was fixed from P996 before this source window was scored.",
            "PUBLIC-PREDICATE BOUNDARY: selector inputs are P869 public features only.",
            "SOURCE-LABEL BOUNDARY: source-positive labels are used for evaluation, not selector body.",
            "EARLY-STOP BOUNDARY: below-rho early-stop requires detecting a secret-deriving reconstructed relation during the scan.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p997_p231_frozen_top16_leaf89_forward",
        "parameters": {
            "frozen_rule": "top_k <= 16 AND unique_leaf_indices contains 89",
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "rule_results": base_payload.get("rule_results") or {},
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "claim_status": claim,
            "control_pass": control_pass,
            "source_exists": source_exists,
            "top16_first_derivation_ops_over_rho": (((top16.get("early_stop") or {}).get("first_deriving_case") or {}).get("public_order_charged_ops_over_rho")),
            "top16_full_charge_ops_over_rho": selection.get("selected_direct_sum_ops_over_rho"),
            "top16_precision": selection.get("precision"),
            "top16_recall": selection.get("recall"),
            "top16_selected_count": selection.get("selected_count"),
            "top16_selected_positive_count": selection.get("selected_positive_count"),
            "top16_useful_amortized_ops_over_rho": useful_amortized(selection),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P997 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p993", default=str(DEFAULT_P993), help="P993 source JSON")
    parser.add_argument("--p994", default=str(DEFAULT_P994), help="P994 source JSON")
    parser.add_argument("--p995", default=str(DEFAULT_P995), help="P995 source JSON")
    parser.add_argument("--p996", default=str(DEFAULT_P996), help="P996 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="Forward p231 source window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} source_exists={source_exists} selected={selected} selected_pos={selected_pos} "
        "precision={precision} recall={recall} full_ops_rho={full_ops} useful_amortized={useful} "
        "first_derivation_ops_rho={first_ops} out={out}".format(
            claim=payload["claim_status"],
            source_exists=summary.get("source_exists"),
            selected=summary.get("top16_selected_count"),
            selected_pos=summary.get("top16_selected_positive_count"),
            precision=summary.get("top16_precision"),
            recall=summary.get("top16_recall"),
            full_ops=summary.get("top16_full_charge_ops_over_rho"),
            useful=summary.get("top16_useful_amortized_ops_over_rho"),
            first_ops=summary.get("top16_first_derivation_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
