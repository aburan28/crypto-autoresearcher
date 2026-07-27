#!/usr/bin/env python3
"""P1001 frozen phase-shifted hash-tuple validation for p231."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p993_p231_branch_switch_selector_scout as p993
import low_term_total2_p996_p231_early_stop_recall_split as p996
import low_term_total2_p999_p231_hash_basis_quality as p999
import low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order as p1000


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1001_p231_phase_shifted_hash_tuple.md"
DEFAULT_P1000 = STATE_DIR / "low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1001_p231_phase_shifted_hash_tuple_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1001_p231_phase_shifted_hash_tuple.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_CONTROL_WINDOW = "11952_11959"
DEFAULT_VALIDATION_WINDOW = "11960_11967"
FROZEN_LEAF_SELECTOR = "mode_hash_leaf_total6"
FROZEN_TOP_K_VALUES = [12, 16]
FROZEN_LEAVES = [47, 56, 84]


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


def shifted_rule(features: dict[str, Any]) -> bool:
    return (
        str(features.get("leaf_selector")) == FROZEN_LEAF_SELECTOR
        and int_value(features.get("top_k")) in set(FROZEN_TOP_K_VALUES)
        and p999.leaf_indices(features) == FROZEN_LEAVES
    )


def phase_order_key(example: dict[str, Any]) -> tuple[Any, ...]:
    features = example.get("features") or {}
    case = example.get("source_case") or {}
    return (
        int_value(features.get("salt_gap")),
        int_value(features.get("top_k")),
        int_value(case.get("transfer_index")),
        tuple(p999.leaf_indices(features)),
        p996.row_key_signature(example),
        str(example.get("case_id")),
    )


def analyze_window(window: str, targets: str, min_source_rank: int, baseline_rank: int) -> dict[str, Any]:
    source_path = p868.source_path(window)
    source_exists = source_path.exists()
    examples = p999.build_validation_examples(window, targets, min_source_rank) if source_exists else []
    selected = [row for row in examples if shifted_rule(row.get("features") or {})]
    reconstructed, verifier = p993.reconstruct_examples(selected) if selected else ([], None)
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank) if reconstructed else {
        "best_groups": [],
        "exact_tail_group_count": 0,
        "exact_term_basis_group_count": 0,
        "form_order": [],
        "raw_form_count": 0,
        "secret_deriving_group_count": 0,
        "unique_form_count": 0,
    }
    best_groups = groups.get("best_groups") or []
    deriving_case_ids = p999.derive_case_ids(groups)
    secret_group = p1000.best_secret_deriving_group(best_groups)
    source_selection = p999.summarize_source_selection(examples, selected)
    public_order = p1000.early_stop_summary(selected, deriving_case_ids, "p996_public_order", p996.public_order_key)
    phase_order = p1000.early_stop_summary(selected, deriving_case_ids, "salt_gap_topk_transfer", phase_order_key)
    selected_source_positives = [row for row in selected if row.get("label_positive")]
    return {
        "diagnostics": {
            "best_reconstructed_groups": best_groups,
            "selected_cases_phase_order": phase_order.get("ordered_cases"),
            "selected_cases_public_order": public_order.get("ordered_cases"),
            "selected_source_positive_case_ids": [row.get("case_id") for row in selected_source_positives],
        },
        "early_stop": {
            "phase_order": phase_order,
            "public_order": public_order,
        },
        "reconstruction": {
            "best_secret_deriving_group": secret_group,
            "best_secret_deriving_selected_case_amortized_ops_over_rho": (secret_group or {}).get("selected_case_amortized_ops_over_rho"),
            "exact_tail_group_count": groups.get("exact_tail_group_count"),
            "exact_term_basis_group_count": groups.get("exact_term_basis_group_count"),
            "form_order": groups.get("form_order"),
            "raw_form_count": groups.get("raw_form_count"),
            "reconstructed_selected_count": len(reconstructed),
            "reconstruction_error_count": sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed),
            "secret_deriving_group_count": groups.get("secret_deriving_group_count"),
            "unique_form_count": groups.get("unique_form_count"),
        },
        "selection": source_selection,
        "source": {
            "path": str(source_path),
            "sha256": sha256_file(source_path),
            "summary": p1000.source_summary(source_path),
        },
        "source_exists": source_exists,
    }


def first_charge(window: dict[str, Any], order_name: str) -> float | None:
    first = (((window.get("early_stop") or {}).get(order_name) or {}).get("first_deriving_case") or {})
    value = first.get("charged_ops_over_rho")
    return float(value) if value is not None else None


def determine_claim(control: dict[str, Any], validation: dict[str, Any]) -> str:
    if not control.get("source_exists"):
        return "NEGATIVE_RESULT_P1001_CONTROL_SOURCE_MISSING"
    control_selection = control.get("selection") or {}
    if int_value(control_selection.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1001_POSITIVE_CONTROL_SELECTS_NO_ROWS"
    if int_value(control_selection.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P1001_POSITIVE_CONTROL_NO_SOURCE_POSITIVES"
    if not validation.get("source_exists"):
        return "NEGATIVE_RESULT_P1001_VALIDATION_SOURCE_MISSING"
    selection = validation.get("selection") or {}
    reconstruction = validation.get("reconstruction") or {}
    if int_value(selection.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1001_PHASE_HASH_SELECTS_NO_ROWS"
    if int_value(reconstruction.get("reconstruction_error_count")):
        return "P1001_PHASE_HASH_RECONSTRUCTION_ERRORS"
    phase_charge = first_charge(validation, "phase_order")
    public_charge = first_charge(validation, "public_order")
    best_secret_cost = reconstruction.get("best_secret_deriving_selected_case_amortized_ops_over_rho")
    if phase_charge is not None and phase_charge < 1.0:
        return "P1001_PHASE_HASH_SALT_FIRST_DERIVATION_BELOW_RHO"
    if public_charge is not None and public_charge < 1.0:
        return "P1001_PHASE_HASH_PUBLIC_ORDER_DERIVATION_BELOW_RHO"
    if best_secret_cost is not None and float(best_secret_cost) < 1.0:
        return "P1001_PHASE_HASH_SECRET_AMORTIZED_BELOW_RHO"
    if int_value(reconstruction.get("secret_deriving_group_count")) > 0:
        return "P1001_PHASE_HASH_SECRET_DERIVATION_ABOVE_RHO"
    if int_value(selection.get("selected_positive_count")) > 0:
        useful = selection.get("useful_amortized_ops_over_rho")
        if useful is not None and float(useful) < 1.0:
            return "P1001_PHASE_HASH_SOURCE_SIGNAL_BELOW_RHO_NO_SECRET_DERIVATION"
        return "P1001_PHASE_HASH_SOURCE_SIGNAL_NO_SECRET_DERIVATION"
    return "NEGATIVE_RESULT_P1001_PHASE_HASH_NO_SOURCE_POSITIVES"


def summarize_window(window: dict[str, Any]) -> dict[str, Any]:
    selection = window.get("selection") or {}
    reconstruction = window.get("reconstruction") or {}
    return {
        "best_secret_deriving_selected_case_amortized_ops_over_rho": reconstruction.get("best_secret_deriving_selected_case_amortized_ops_over_rho"),
        "case_count": selection.get("case_count"),
        "first_derivation_phase_order_ops_over_rho": first_charge(window, "phase_order"),
        "first_derivation_public_order_ops_over_rho": first_charge(window, "public_order"),
        "reconstructed_selected_count": reconstruction.get("reconstructed_selected_count"),
        "reconstruction_error_count": reconstruction.get("reconstruction_error_count"),
        "secret_deriving_group_count": reconstruction.get("secret_deriving_group_count"),
        "selected_count": selection.get("selected_count"),
        "selected_direct_sum_ops_over_rho": selection.get("selected_direct_sum_ops_over_rho"),
        "selected_source_positive_count": selection.get("selected_positive_count"),
        "source_positive_count": selection.get("positive_count"),
        "source_precision": selection.get("precision"),
        "source_summary": (window.get("source") or {}).get("summary"),
        "source_useful_amortized_ops_over_rho": selection.get("useful_amortized_ops_over_rho"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    baseline_rank = 8
    control = analyze_window(args.control_window, args.targets, args.min_source_rank, baseline_rank)
    validation = analyze_window(args.validation_window, args.targets, args.min_source_rank, baseline_rank)
    claim = determine_claim(control, validation)
    p1000_path = Path(args.p1000)
    p1000_payload = load_json(p1000_path) if p1000_path.exists() else {}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p1000_source": str(p1000_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p1000_source_sha256": sha256_file(p1000_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1001_") else "NEGATIVE RESULT",
        "control": control,
        "created_at": now_iso(),
        "frozen_rule": {
            "description": "mode_hash_leaf_total6 AND top_k in {12,16} AND unique_leaf_indices == [47,56,84]",
            "leaf_selector": FROZEN_LEAF_SELECTOR,
            "top_k_values": FROZEN_TOP_K_VALUES,
            "unique_leaf_indices": FROZEN_LEAVES,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FROM-DIAGNOSTIC: the selector was derived from P1000 validation feature distribution.",
            "SOURCE-POSITIVE-BOUNDARY: source-positive rows are relation-source evidence, not a secret derivation or full index-calculus break.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p1001_p231_phase_shifted_hash_tuple",
        "p1000_reference": {
            "claim_status": p1000_payload.get("claim_status"),
            "summary": p1000_payload.get("summary"),
        },
        "parameters": {
            "baseline_rank": baseline_rank,
            "control_window": args.control_window,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_window": args.validation_window,
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "control": summarize_window(control),
            "control_pass": bool(int_value((control.get("selection") or {}).get("selected_positive_count"))),
            "validation": summarize_window(validation),
        },
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1001 contract path")
    parser.add_argument("--control-window", default=DEFAULT_CONTROL_WINDOW, help="Positive-control source window")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--p1000", default=str(DEFAULT_P1000), help="P1000 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--validation-window", default=DEFAULT_VALIDATION_WINDOW, help="Forward validation window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    validation = summary["validation"]
    print(
        "claim={claim} control_pass={control_pass} selected={selected} source_pos={source_pos} "
        "derivers={derivers} first_public={first_public} first_phase={first_phase} "
        "source_useful={source_useful} best_secret_amortized={best_secret_amortized} out={out}".format(
            claim=payload["claim_status"],
            control_pass=summary.get("control_pass"),
            selected=validation.get("selected_count"),
            source_pos=validation.get("selected_source_positive_count"),
            derivers=validation.get("secret_deriving_group_count"),
            first_public=validation.get("first_derivation_public_order_ops_over_rho"),
            first_phase=validation.get("first_derivation_phase_order_ops_over_rho"),
            source_useful=validation.get("source_useful_amortized_ops_over_rho"),
            best_secret_amortized=validation.get("best_secret_deriving_selected_case_amortized_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
