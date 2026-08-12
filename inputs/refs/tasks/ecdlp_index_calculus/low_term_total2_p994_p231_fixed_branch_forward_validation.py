#!/usr/bin/env python3
"""P994 fixed-rule forward validation for the P993 p231 branch selector."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p993_p231_branch_switch_selector_scout as p993


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p994_p231_fixed_branch_forward_validation.md"
DEFAULT_P993 = STATE_DIR / "low_term_total2_p993_p231_branch_switch_selector_scout_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p994_p231_fixed_branch_forward_validation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p994_p231_fixed_branch_forward_validation.v1"
DEFAULT_WINDOW = "11912_11919"
DEFAULT_TARGET = "22050.cf1@11731"
FROZEN_RULE = "top_k <= 7"


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


def p993_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    chosen = summary.get("chosen_rule") or {}
    return {
        "p993_claim_expected": payload.get("claim_status") == "P993_BRANCH_RULE_RECONSTRUCTS_SECRET_DERIVING_GROUP",
        "p993_control_pass": bool(summary.get("control_pass")),
        "p993_rule_expected": chosen.get("name") == FROZEN_RULE,
        "p993_heldout_positive_recovered": int_value((summary.get("heldout") or {}).get("selected_positive_count")) > 0,
        "p993_secret_deriving_group": int_value(summary.get("secret_deriving_group_count")) > 0,
    }


def frozen_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) <= 7


def summarize_selection(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in examples if row.get("label_positive")]
    selected_positive = [row for row in selected if row.get("label_positive")]
    selected_direct_sum = sum(float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0) for row in selected)
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(examples))
    return {
        "case_count": len(examples),
        "positive_count": len(positives),
        "positive_transfer_count": len({int_value((row.get("source_case") or {}).get("transfer_index")) for row in positives}),
        "precision": precision,
        "precision_lift_over_prevalence": safe_ratio(precision or 0.0, prevalence or 0.0) if prevalence else None,
        "prevalence": prevalence,
        "recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_direct_sum, 8),
        "selected_positive_count": len(selected_positive),
        "selected_positive_transfer_count": len({int_value((row.get("source_case") or {}).get("transfer_index")) for row in selected_positive}),
    }


def determine_claim(control_pass: bool, source_exists: bool, selection: dict[str, Any], reconstruction_errors: int, groups: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P994_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P994_SOURCE_WINDOW_MISSING"
    if int_value(selection.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P994_FIXED_BRANCH_MISSES_FORWARD_SOURCE_SIGNAL"
    if (selection.get("precision_lift_over_prevalence") or 0.0) <= 1.0:
        return "P994_FIXED_BRANCH_RECALLS_FORWARD_SIGNAL_WITHOUT_PRECISION_LIFT"
    if reconstruction_errors:
        return "P994_FIXED_BRANCH_RECALLS_FORWARD_SIGNAL_BUT_RECONSTRUCTION_ERRORS"
    if int_value(groups.get("secret_deriving_group_count")) > 0:
        return "P994_FIXED_BRANCH_FORWARD_SECRET_DERIVATION"
    return "P994_FIXED_BRANCH_FORWARD_RECOVERS_SOURCE_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p993_path = Path(args.p993)
    p993_payload = load_json(p993_path)
    controls = p993_controls(p993_payload)
    control_pass = all(controls.values())
    source_path = p868.source_path(args.window)
    source_exists = source_path.exists()
    if not hasattr(args, "train_transfer_max"):
        args.train_transfer_max = -1
    examples = p993.build_examples(args) if source_exists else []
    selected = [row for row in examples if frozen_rule(row["features"])]
    reconstructed, verifier = p993.reconstruct_examples(selected)
    baseline_rank = int_value((p993_payload.get("summary") or {}).get("baseline_mixed_wide_relation_rank"))
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    selection = summarize_selection(examples, selected)
    claim = determine_claim(control_pass, source_exists, selection, reconstruction_error_count, groups)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p993_source": str(p993_path),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p993_source_sha256": sha256_file(p993_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P994_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "diagnostics": {
            "best_reconstructed_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "selected_cases": [p993.public_case_summary(row) for row in selected],
            "selected_reconstructed_cases": [
                {
                    "case_id": row.get("case_id"),
                    "direct_ops_over_rho": row.get("direct_ops_over_rho"),
                    "form_count": len(row.get("form_records") or []),
                    "label_positive": row.get("label_positive"),
                    "reconstructed_error_count": row.get("reconstructed_error_count"),
                    "transfer_index": row.get("transfer_index"),
                    "union_public_key_verified": row.get("union_public_key_verified"),
                    "union_rank": row.get("union_rank"),
                    "union_relation_count": row.get("union_relation_count"),
                    "window": row.get("window"),
                }
                for row in reconstructed
            ],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-RULE: P994 applies the P993 rule without retraining on the forward window.",
            "PUBLIC-PREDICATE BOUNDARY: the selector uses only top_k before reconstruction.",
            "SOURCE-LABEL BOUNDARY: source-positive labels are used only for evaluation.",
            "NO-END-TO-END-BREAK: forward recovery still needs broader validation, sparse linear algebra, and target descent.",
        ],
        "method": "p994_p231_fixed_branch_forward_validation",
        "parameters": {
            "baseline_rank": baseline_rank,
            "frozen_rule": FROZEN_RULE,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "claim_status": claim,
            "control_pass": control_pass,
            "exact_tail_group_count": groups["exact_tail_group_count"],
            "exact_term_basis_group_count": groups["exact_term_basis_group_count"],
            "form_order": groups["form_order"],
            "form_order_count": groups["form_order_count"],
            "frozen_rule": FROZEN_RULE,
            "raw_form_count": groups["raw_form_count"],
            "reconstructed_selected_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "secret_deriving_group_count": groups["secret_deriving_group_count"],
            "selection": selection,
            "source_exists": source_exists,
            "target_basis_present": bool(groups.get("target_basis")),
            "target_basis_secret_derivation": bool((groups.get("target_basis") or {}).get("mixed_wide_relations_derive_secret")),
            "target_exact_tail_present": bool(groups.get("target_exact_tail")),
            "target_exact_tail_secret_derivation": bool((groups.get("target_exact_tail") or {}).get("mixed_wide_relations_derive_secret")),
            "unique_form_count": groups["unique_form_count"],
        },
        "target_groups": {
            "exact_term_basis": groups.get("target_basis"),
            "exact_tail_expression": groups.get("target_exact_tail"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P994 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p993", default=str(DEFAULT_P993), help="P993 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="Forward p231 source window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    selection = summary["selection"]
    print(
        "claim={claim} source_exists={source_exists} selected={selected} selected_pos={selected_pos} "
        "lift={lift} reconstructed={reconstructed} forms={forms} derivers={derivers} out={out}".format(
            claim=payload["claim_status"],
            source_exists=summary.get("source_exists"),
            selected=selection.get("selected_count"),
            selected_pos=selection.get("selected_positive_count"),
            lift=selection.get("precision_lift_over_prevalence"),
            reconstructed=summary.get("reconstructed_selected_count"),
            forms=summary.get("unique_form_count"),
            derivers=summary.get("secret_deriving_group_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
