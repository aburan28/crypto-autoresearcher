#!/usr/bin/env python3
"""P1000 frozen relaxed hash-leaf salt-first validation for p231."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p993_p231_branch_switch_selector_scout as p993
import low_term_total2_p996_p231_early_stop_recall_split as p996
import low_term_total2_p998_p231_branch_ensemble_selector as p998
import low_term_total2_p999_p231_hash_basis_quality as p999


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1000_p231_relaxed_hash_leaf_salt_order.md"
DEFAULT_P999 = STATE_DIR / "low_term_total2_p999_p231_hash_basis_quality_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1000_p231_relaxed_hash_leaf_salt_order.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_CONTROL_WINDOW = "11944_11951"
DEFAULT_VALIDATION_WINDOW = "11952_11959"
FROZEN_LEAF_SELECTOR = "mode_hash_leaf_total6"
FROZEN_TOP_K = 7
FROZEN_LEAVES = [34, 47, 56]
TARGET_SHIFTED_BASIS = "[11,11,13,13]"
TARGET_SHIFTED_TAIL = '{"tail_coeffs":[11777,11777],"tail_support":[12,14],"terms":[11,11,13,13]}'


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


def selected_ops(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0)


def frozen_rule(features: dict[str, Any]) -> bool:
    return (
        str(features.get("leaf_selector")) == FROZEN_LEAF_SELECTOR
        and int_value(features.get("top_k")) == FROZEN_TOP_K
        and p999.leaf_indices(features) == FROZEN_LEAVES
    )


def salt_first_order_key(example: dict[str, Any]) -> tuple[Any, ...]:
    features = example.get("features") or {}
    case = example.get("source_case") or {}
    return (
        int_value(features.get("salt_gap")),
        int_value(case.get("transfer_index")),
        tuple(p999.leaf_indices(features)),
        p996.row_key_signature(example),
        str(example.get("case_id")),
    )


def jsonable_key(value: Any) -> Any:
    if isinstance(value, tuple):
        return [jsonable_key(item) for item in value]
    if isinstance(value, list):
        return [jsonable_key(item) for item in value]
    return value


def selected_case_summary(example: dict[str, Any], derives: bool, order_key_fn: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    return {
        **p998.feature_summary(example),
        "derives_secret": derives,
        "order_key": jsonable_key(order_key_fn(example)),
        "row_key_signature": p996.row_key_signature(example),
    }


def min_charge_by_key(
    selected: list[dict[str, Any]],
    dedupe_key_fn: Callable[[dict[str, Any]], Any],
    order_key_fn: Callable[[dict[str, Any]], Any],
) -> dict[str, Any]:
    best: dict[Any, dict[str, Any]] = {}
    for example in selected:
        key = dedupe_key_fn(example)
        if key not in best or selected_ops(example) < selected_ops(best[key]):
            best[key] = example
    charged = sorted(best.values(), key=order_key_fn)
    return {
        "charged_case_count": len(charged),
        "charged_case_ids": [row.get("case_id") for row in charged],
        "charged_ops_over_rho": round(sum(selected_ops(row) for row in charged), 8),
    }


def early_stop_summary(
    selected: list[dict[str, Any]],
    deriving_case_ids: set[str],
    order_name: str,
    order_key_fn: Callable[[dict[str, Any]], Any],
) -> dict[str, Any]:
    ordered = sorted(selected, key=order_key_fn)
    cumulative = 0.0
    first_deriving: dict[str, Any] | None = None
    for index, example in enumerate(ordered, start=1):
        cumulative += selected_ops(example)
        if str(example.get("case_id")) in deriving_case_ids:
            first_deriving = {
                "case_id": example.get("case_id"),
                "direct_ops_over_rho": selected_ops(example),
                "ordered_index": index,
                "charged_ops_over_rho": round(cumulative, 8),
            }
            break
    total = cumulative if first_deriving else sum(selected_ops(row) for row in ordered)
    return {
        "deriving_case_count": len(deriving_case_ids),
        "first_derivation_below_rho": bool(first_deriving and first_deriving["charged_ops_over_rho"] < 1.0),
        "first_deriving_case": first_deriving,
        "order_name": order_name,
        "ordered_case_count": len(ordered),
        "ordered_cases": [
            selected_case_summary(example, str(example.get("case_id")) in deriving_case_ids, order_key_fn)
            for example in ordered
        ],
        "total_ops_over_rho": round(total, 8),
        "duplicate_row_key_charge": min_charge_by_key(selected, p996.row_key_signature, order_key_fn),
        "transfer_charge": min_charge_by_key(
            selected,
            lambda row: int_value((row.get("source_case") or {}).get("transfer_index")),
            order_key_fn,
        ),
    }


def find_group(groups: list[dict[str, Any]], group_type: str, group_key: str) -> dict[str, Any] | None:
    for group in groups:
        if group.get("group_type") == group_type and group.get("group_key") == group_key:
            return group
    return None


def best_secret_deriving_group(groups: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [group for group in groups if group.get("mixed_wide_relations_derive_secret")]
    if not candidates:
        return None
    return min(
        candidates,
        key=lambda group: (
            group.get("selected_case_amortized_ops_over_rho")
            if group.get("selected_case_amortized_ops_over_rho") is not None
            else 10**9,
            group.get("group_type"),
            group.get("group_key"),
        ),
    )


def source_summary(source_path: Path) -> dict[str, Any]:
    if not source_path.exists():
        return {"source_exists": False}
    payload = load_json(source_path)
    summaries = ((payload.get("summary") or {}).get("policy_summaries") or [])
    fixed = next((row for row in summaries if row.get("policy") == "fixed_target_cap2_ow0_hw3_lw0_sw0_cw0_aw1"), summaries[0] if summaries else {})
    return {
        "source_exists": True,
        "stress_leaf_below_rho": fixed.get("stress_leaf_below_rho"),
        "stress_leaf_best_ops_over_rho": fixed.get("stress_leaf_best_ops_over_rho"),
        "stress_leaf_verified": fixed.get("stress_leaf_verified"),
        "stress_row_below_rho": fixed.get("stress_row_below_rho"),
        "stress_row_verified": fixed.get("stress_row_verified"),
    }


def analyze_window(window: str, targets: str, min_source_rank: int, baseline_rank: int) -> dict[str, Any]:
    source_path = p868.source_path(window)
    source_exists = source_path.exists()
    examples = p999.build_validation_examples(window, targets, min_source_rank) if source_exists else []
    selected = [row for row in examples if frozen_rule(row.get("features") or {})]
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
    case_rank_hist: dict[str, int] = {}
    for row in reconstructed:
        key = str(row.get("union_rank"))
        case_rank_hist[key] = case_rank_hist.get(key, 0) + 1
    secret_group = best_secret_deriving_group(best_groups)
    target_basis = find_group(best_groups, "exact_term_basis", TARGET_SHIFTED_BASIS)
    target_tail = find_group(best_groups, "exact_tail_expression", TARGET_SHIFTED_TAIL)
    source_selection = p999.summarize_source_selection(examples, selected)
    public_order = early_stop_summary(selected, deriving_case_ids, "p996_public_order", p996.public_order_key)
    salt_first_order = early_stop_summary(selected, deriving_case_ids, "salt_gap_then_transfer", salt_first_order_key)
    return {
        "diagnostics": {
            "best_reconstructed_groups": best_groups,
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "selected_cases_public_order": public_order.get("ordered_cases"),
            "selected_cases_salt_first_order": salt_first_order.get("ordered_cases"),
        },
        "early_stop": {
            "public_order": public_order,
            "salt_first_order": salt_first_order,
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
            "target_shifted_basis": target_basis,
            "target_shifted_basis_present": bool(target_basis),
            "target_shifted_basis_secret_derivation": bool((target_basis or {}).get("mixed_wide_relations_derive_secret")),
            "target_shifted_tail": target_tail,
            "target_shifted_tail_present": bool(target_tail),
            "target_shifted_tail_secret_derivation": bool((target_tail or {}).get("mixed_wide_relations_derive_secret")),
            "unique_form_count": groups.get("unique_form_count"),
        },
        "selection": source_selection,
        "source": {
            "path": str(source_path),
            "sha256": sha256_file(source_path),
            "summary": source_summary(source_path),
        },
        "source_exists": source_exists,
    }


def first_charge(window: dict[str, Any], order_name: str) -> float | None:
    first = (((window.get("early_stop") or {}).get(order_name) or {}).get("first_deriving_case") or {})
    value = first.get("charged_ops_over_rho")
    return float(value) if value is not None else None


def determine_claim(control: dict[str, Any], validation: dict[str, Any]) -> str:
    if not control.get("source_exists"):
        return "NEGATIVE_RESULT_P1000_CONTROL_SOURCE_MISSING"
    control_recon = control.get("reconstruction") or {}
    if not int_value(control_recon.get("secret_deriving_group_count")):
        return "NEGATIVE_RESULT_P1000_POSITIVE_CONTROL_NO_SECRET_DERIVATION"
    if not validation.get("source_exists"):
        return "NEGATIVE_RESULT_P1000_VALIDATION_SOURCE_MISSING"
    selection = validation.get("selection") or {}
    reconstruction = validation.get("reconstruction") or {}
    if int_value(selection.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P1000_RELAXED_HASH_LEAF_SELECTS_NO_ROWS"
    if int_value(reconstruction.get("reconstruction_error_count")):
        return "P1000_RELAXED_HASH_LEAF_RECONSTRUCTION_ERRORS"
    best_secret_cost = reconstruction.get("best_secret_deriving_selected_case_amortized_ops_over_rho")
    salt_first_charge = first_charge(validation, "salt_first_order")
    public_charge = first_charge(validation, "public_order")
    if salt_first_charge is not None and salt_first_charge < 1.0:
        return "P1000_RELAXED_HASH_LEAF_SALT_FIRST_DERIVATION_BELOW_RHO"
    if public_charge is not None and public_charge < 1.0:
        return "P1000_RELAXED_HASH_LEAF_PUBLIC_ORDER_DERIVATION_BELOW_RHO"
    if best_secret_cost is not None and float(best_secret_cost) < 1.0:
        return "P1000_RELAXED_HASH_LEAF_SECRET_AMORTIZED_BELOW_RHO"
    if int_value(reconstruction.get("secret_deriving_group_count")) > 0:
        return "P1000_RELAXED_HASH_LEAF_SECRET_DERIVATION_ABOVE_RHO"
    return "NEGATIVE_RESULT_P1000_RELAXED_HASH_LEAF_NO_FORWARD_SECRET_DERIVATION"


def summarize_window(window: dict[str, Any]) -> dict[str, Any]:
    selection = window.get("selection") or {}
    reconstruction = window.get("reconstruction") or {}
    return {
        "best_secret_deriving_selected_case_amortized_ops_over_rho": reconstruction.get("best_secret_deriving_selected_case_amortized_ops_over_rho"),
        "case_count": selection.get("case_count"),
        "first_derivation_public_order_ops_over_rho": first_charge(window, "public_order"),
        "first_derivation_salt_first_ops_over_rho": first_charge(window, "salt_first_order"),
        "reconstruction_error_count": reconstruction.get("reconstruction_error_count"),
        "reconstructed_selected_count": reconstruction.get("reconstructed_selected_count"),
        "secret_deriving_group_count": reconstruction.get("secret_deriving_group_count"),
        "selected_count": selection.get("selected_count"),
        "selected_direct_sum_ops_over_rho": selection.get("selected_direct_sum_ops_over_rho"),
        "selected_source_positive_count": selection.get("selected_positive_count"),
        "source_positive_count": selection.get("positive_count"),
        "source_precision": selection.get("precision"),
        "source_summary": (window.get("source") or {}).get("summary"),
        "source_useful_amortized_ops_over_rho": selection.get("useful_amortized_ops_over_rho"),
        "target_shifted_basis_secret_derivation": reconstruction.get("target_shifted_basis_secret_derivation"),
        "target_shifted_tail_secret_derivation": reconstruction.get("target_shifted_tail_secret_derivation"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    baseline_rank = 8
    control = analyze_window(args.control_window, args.targets, args.min_source_rank, baseline_rank)
    validation = analyze_window(args.validation_window, args.targets, args.min_source_rank, baseline_rank)
    claim = determine_claim(control, validation)
    p999_path = Path(args.p999)
    p999_payload = load_json(p999_path) if p999_path.exists() else {}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p999_source": str(p999_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p999_source_sha256": sha256_file(p999_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1000_") else "NEGATIVE RESULT",
        "control": control,
        "created_at": now_iso(),
        "frozen_rule": {
            "description": "mode_hash_leaf_total6 AND top_k == 7 AND unique_leaf_indices == [34,47,56]",
            "leaf_selector": FROZEN_LEAF_SELECTOR,
            "top_k": FROZEN_TOP_K,
            "unique_leaf_indices": FROZEN_LEAVES,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FROZEN-FROM-DIAGNOSTIC: the selector was derived post-hoc from P999 and is only being tested forward here.",
            "PUBLIC-PREDICATE BOUNDARY: rule inputs are public leaf selector, top-k, leaf tuple, salt gap, transfer, and row keys.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p1000_p231_relaxed_hash_leaf_salt_order",
        "parameters": {
            "baseline_rank": baseline_rank,
            "control_window": args.control_window,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "target_shifted_basis": TARGET_SHIFTED_BASIS,
            "target_shifted_tail": TARGET_SHIFTED_TAIL,
            "validation_window": args.validation_window,
        },
        "p999_reference": {
            "claim_status": p999_payload.get("claim_status"),
            "summary": p999_payload.get("summary"),
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "control": summarize_window(control),
            "control_pass": bool(int_value((control.get("reconstruction") or {}).get("secret_deriving_group_count"))),
            "validation": summarize_window(validation),
        },
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P1000 contract path")
    parser.add_argument("--control-window", default=DEFAULT_CONTROL_WINDOW, help="Positive-control source window")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--p999", default=str(DEFAULT_P999), help="P999 source JSON")
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
        "derivers={derivers} first_public={first_public} first_salt={first_salt} "
        "best_secret_amortized={best_secret_amortized} out={out}".format(
            claim=payload["claim_status"],
            control_pass=summary.get("control_pass"),
            selected=validation.get("selected_count"),
            source_pos=validation.get("selected_source_positive_count"),
            derivers=validation.get("secret_deriving_group_count"),
            first_public=validation.get("first_derivation_public_order_ops_over_rho"),
            first_salt=validation.get("first_derivation_salt_first_ops_over_rho"),
            best_secret_amortized=validation.get("best_secret_deriving_selected_case_amortized_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
