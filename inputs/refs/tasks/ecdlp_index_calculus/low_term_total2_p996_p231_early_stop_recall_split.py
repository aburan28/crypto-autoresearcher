#!/usr/bin/env python3
"""P996 early-stop and recall split audit for the p231 leaf-89 branch."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p993_p231_branch_switch_selector_scout as p993
import low_term_total2_p995_p231_branch_precision_guard as p995


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p996_p231_early_stop_recall_split.md"
DEFAULT_P993 = STATE_DIR / "low_term_total2_p993_p231_branch_switch_selector_scout_probe.json"
DEFAULT_P994 = STATE_DIR / "low_term_total2_p994_p231_fixed_branch_forward_validation_probe.json"
DEFAULT_P995 = STATE_DIR / "low_term_total2_p995_p231_branch_precision_guard_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p996_p231_early_stop_recall_split_probe.json"
SCHEMA = "ecdlp.low_term_total2_p996_p231_early_stop_recall_split.v1"
DEFAULT_WINDOW = "11920_11927"
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


def leaf_indices(features: dict[str, Any]) -> list[int]:
    return [int_value(value) for value in features.get("unique_leaf_indices") or []]


def contains_leaf89(features: dict[str, Any]) -> bool:
    return 89 in leaf_indices(features)


def rule_specs() -> list[dict[str, Any]]:
    return [
        {
            "name": "p995_top7_leaf89",
            "description": "top_k <= 7 and unique_leaf_indices contains 89",
            "rule_type": "validated_guard",
            "predicate": lambda f: int_value(f.get("top_k")) <= 7 and contains_leaf89(f),
        },
        {
            "name": "top16_leaf89_recall_extension",
            "description": "top_k <= 16 and unique_leaf_indices contains 89",
            "rule_type": "recall_extension_diagnostic",
            "predicate": lambda f: int_value(f.get("top_k")) <= 16 and contains_leaf89(f),
        },
        {
            "name": "leaf89_any_top_diagnostic",
            "description": "unique_leaf_indices contains 89 with no top_k cap",
            "rule_type": "recall_extension_diagnostic",
            "predicate": contains_leaf89,
        },
    ]


def p995_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    guarded = summary.get("guarded_selection") or {}
    chosen = summary.get("chosen_guard") or {}
    return {
        "p995_claim_expected": payload.get("claim_status") == "P995_PRECISION_GUARD_FORWARD_SECRET_DERIVATION",
        "p995_control_pass": bool(summary.get("control_pass")),
        "p995_guard_expected": chosen.get("name") == "contains_leaf_89",
        "p995_selected_positive": int_value(guarded.get("selected_positive_count")) > 0,
        "p995_secret_deriving_group": int_value(summary.get("secret_deriving_group_count")) > 0,
    }


def row_for_training_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case.get("case_id"),
        "features": case.get("features") or {},
        "label_positive": bool(case.get("label_positive")),
        "source_ops_over_rho": case.get("source_ops_over_rho"),
        "transfer_index": case.get("transfer_index"),
    }


def summarize_rows(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row.get("label_positive")]
    selected_positive = [row for row in selected if row.get("label_positive")]
    selected_direct_sum = sum(float(row.get("source_ops_over_rho") or 0.0) for row in selected)
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(rows))
    return {
        "case_count": len(rows),
        "positive_count": len(positives),
        "positive_transfer_count": len({int_value(row.get("transfer_index")) for row in positives}),
        "precision": precision,
        "precision_lift_over_prevalence": safe_ratio(precision or 0.0, prevalence or 0.0) if prevalence else None,
        "prevalence": prevalence,
        "recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(selected_direct_sum, 8),
        "selected_positive_count": len(selected_positive),
        "selected_positive_transfer_count": len({int_value(row.get("transfer_index")) for row in selected_positive}),
    }


def summarize_examples(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    selected_ids = {id(row) for row in selected}
    selected_rows = []
    for example in examples:
        case = example.get("source_case") or {}
        row = {
            "case_id": example.get("case_id"),
            "features": example.get("features") or {},
            "label_positive": example.get("label_positive"),
            "source_ops_over_rho": case.get("source_ops_over_rho"),
            "transfer_index": case.get("transfer_index"),
        }
        rows.append(row)
        if id(example) in selected_ids:
            selected_rows.append(row)
    return summarize_rows(rows, selected_rows)


def public_selector_priority(features: dict[str, Any]) -> int:
    order = {
        "mode_hash_leaf_total6": 0,
        "mode_hybrid_support_monic_b_total6": 1,
        "mode_low_term_span_total10": 2,
        "mode_low_term_span_total3": 3,
    }
    return order.get(str(features.get("leaf_selector")), 99)


def public_order_key(example: dict[str, Any]) -> tuple[Any, ...]:
    features = example.get("features") or {}
    case = example.get("source_case") or {}
    return (
        int_value(features.get("top_k")),
        public_selector_priority(features),
        int_value(case.get("transfer_index")),
        int_value(features.get("salt_gap")),
        tuple(leaf_indices(features)),
        str(example.get("case_id")),
    )


def row_key_signature(example: dict[str, Any]) -> str:
    case = example.get("source_case") or {}
    keys = sorted(str(row.get("row_key")) for row in case.get("row_leaf_keys") or [])
    return json.dumps(keys, sort_keys=True, separators=(",", ":"))


def selected_case_summary(example: dict[str, Any], derives: bool) -> dict[str, Any]:
    case = example.get("source_case") or {}
    features = example.get("features") or {}
    return {
        "case_id": example.get("case_id"),
        "derives_secret": derives,
        "label_positive": example.get("label_positive"),
        "leaf_selector": features.get("leaf_selector"),
        "public_order_key": list(public_order_key(example)),
        "row_key_signature": row_key_signature(example),
        "source_ops_over_rho": case.get("source_ops_over_rho"),
        "source_rank": case.get("source_rank"),
        "top_k": features.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unique_leaf_indices": features.get("unique_leaf_indices"),
    }


def derive_case_ids(groups: dict[str, Any]) -> set[str]:
    case_ids: set[str] = set()
    for group in groups.get("best_groups") or []:
        if group.get("mixed_wide_relations_derive_secret"):
            case_ids.update(str(case_id) for case_id in group.get("case_ids") or [])
    return case_ids


def min_charge_by_key(selected: list[dict[str, Any]], key_fn: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    best: dict[Any, dict[str, Any]] = {}
    for example in selected:
        key = key_fn(example)
        cost = float((example.get("source_case") or {}).get("source_ops_over_rho") or 0.0)
        if key not in best or cost < float((best[key].get("source_case") or {}).get("source_ops_over_rho") or 0.0):
            best[key] = example
    charged = sorted(best.values(), key=public_order_key)
    return {
        "charged_case_count": len(charged),
        "charged_case_ids": [row.get("case_id") for row in charged],
        "charged_ops_over_rho": round(sum(float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0) for row in charged), 8),
    }


def early_stop_summary(selected: list[dict[str, Any]], deriving_case_ids: set[str]) -> dict[str, Any]:
    ordered = sorted(selected, key=public_order_key)
    cumulative = 0.0
    first_deriving: dict[str, Any] | None = None
    for index, example in enumerate(ordered, start=1):
        cumulative += float((example.get("source_case") or {}).get("source_ops_over_rho") or 0.0)
        if str(example.get("case_id")) in deriving_case_ids:
            first_deriving = {
                "case_id": example.get("case_id"),
                "direct_ops_over_rho": (example.get("source_case") or {}).get("source_ops_over_rho"),
                "ordered_index": index,
                "public_order_charged_ops_over_rho": round(cumulative, 8),
            }
            break
    return {
        "deriving_case_count": len(deriving_case_ids),
        "first_deriving_case": first_deriving,
        "first_derivation_below_rho": bool(first_deriving and first_deriving["public_order_charged_ops_over_rho"] < 1.0),
        "ordered_case_count": len(ordered),
        "ordered_cases": [
            selected_case_summary(example, str(example.get("case_id")) in deriving_case_ids)
            for example in ordered
        ],
        "public_order_total_ops_over_rho": round(cumulative if first_deriving else sum(float((row.get("source_case") or {}).get("source_ops_over_rho") or 0.0) for row in ordered), 8),
        "selected_duplicate_row_key_charge": min_charge_by_key(selected, row_key_signature),
        "selected_transfer_charge": min_charge_by_key(selected, lambda row: int_value((row.get("source_case") or {}).get("transfer_index"))),
    }


def analyze_rule(
    spec: dict[str, Any],
    training_rows: list[dict[str, Any]],
    examples: list[dict[str, Any]],
    baseline_rank: int,
) -> dict[str, Any]:
    predicate = spec["predicate"]
    selected_training = [row for row in training_rows if predicate(row.get("features") or {})]
    selected = [row for row in examples if predicate(row.get("features") or {})]
    reconstructed, verifier = p993.reconstruct_examples(selected)
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    deriving_case_ids = derive_case_ids(groups)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    return {
        "description": spec["description"],
        "diagnostics": {
            "best_reconstructed_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "selected_cases": [
                selected_case_summary(example, str(example.get("case_id")) in deriving_case_ids)
                for example in sorted(selected, key=public_order_key)
            ],
        },
        "early_stop": early_stop_summary(selected, deriving_case_ids),
        "name": spec["name"],
        "reconstruction": {
            "exact_tail_group_count": groups["exact_tail_group_count"],
            "exact_term_basis_group_count": groups["exact_term_basis_group_count"],
            "form_order": groups["form_order"],
            "raw_form_count": groups["raw_form_count"],
            "reconstructed_selected_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "secret_deriving_group_count": groups["secret_deriving_group_count"],
            "unique_form_count": groups["unique_form_count"],
        },
        "rule_type": spec["rule_type"],
        "training_selection": summarize_rows(training_rows, selected_training),
        "validation_selection": summarize_examples(examples, selected),
    }


def determine_claim(control_pass: bool, source_exists: bool, rule_results: dict[str, dict[str, Any]]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P996_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P996_SOURCE_WINDOW_MISSING"
    guard = rule_results.get("p995_top7_leaf89") or {}
    extension = rule_results.get("top16_leaf89_recall_extension") or {}
    guard_first = ((guard.get("early_stop") or {}).get("first_deriving_case") or {}).get("public_order_charged_ops_over_rho")
    extension_selection = extension.get("validation_selection") or {}
    extension_recon = extension.get("reconstruction") or {}
    if guard_first is None:
        return "NEGATIVE_RESULT_P996_GUARD_HAS_NO_DERIVING_EARLY_STOP_CASE"
    if float(guard_first) >= 1.0:
        return "NEGATIVE_RESULT_P996_GUARD_EARLY_STOP_NOT_BELOW_RHO"
    extension_clean = (
        extension_selection.get("precision") == 1.0
        and extension_selection.get("recall") == 1.0
        and int_value(extension_recon.get("reconstruction_error_count")) == 0
        and int_value(extension_recon.get("secret_deriving_group_count")) > 0
    )
    if extension_clean:
        return "P996_EARLY_STOP_BELOW_RHO_WITH_RECALL_EXTENSION_DIAGNOSTIC"
    return "P996_EARLY_STOP_BELOW_RHO_GUARD_ONLY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p993_path = Path(args.p993)
    p994_path = Path(args.p994)
    p995_path = Path(args.p995)
    p995_payload = load_json(p995_path)
    controls = p995_controls(p995_payload)
    control_pass = all(controls.values())
    source_path = p868.source_path(args.window)
    source_exists = source_path.exists()
    training_rows = p995.load_training_rows(p993_path, p994_path)
    if not hasattr(args, "train_transfer_max"):
        args.train_transfer_max = -1
    examples = p993.build_examples(args) if source_exists else []
    baseline_rank = int_value((p995_payload.get("summary") or {}).get("baseline_mixed_wide_relation_rank"))
    results = {
        spec["name"]: analyze_rule(spec, training_rows, examples, baseline_rank)
        for spec in rule_specs()
    }
    claim = determine_claim(control_pass, source_exists, results)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p993_source": str(p993_path),
            "p994_source": str(p994_path),
            "p995_source": str(p995_path),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p993_source_sha256": sha256_file(p993_path),
            "p994_source_sha256": sha256_file(p994_path),
            "p995_source_sha256": sha256_file(p995_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P996_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "EARLY-STOP BOUNDARY: first-derivation charge assumes the public scan can stop after reconstruction/verifier derivation is detected.",
            "RECALL-EXTENSION BOUNDARY: top_k <= 16 is chosen after seeing the P995 missed positive and must be frozen forward before promotion.",
            "PUBLIC-PREDICATE BOUNDARY: rule inputs are P869 public features only.",
            "SOURCE-LABEL BOUNDARY: source-positive labels are used for evaluation, not selector body.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p996_p231_early_stop_recall_split",
        "parameters": {
            "baseline_rank": baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "window": args.window,
        },
        "rule_results": results,
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "claim_status": claim,
            "control_pass": control_pass,
            "p995_guard_first_derivation_ops_over_rho": (((results.get("p995_top7_leaf89") or {}).get("early_stop") or {}).get("first_deriving_case") or {}).get("public_order_charged_ops_over_rho"),
            "p995_guard_full_charge_ops_over_rho": ((results.get("p995_top7_leaf89") or {}).get("validation_selection") or {}).get("selected_direct_sum_ops_over_rho"),
            "recall_extension_full_charge_ops_over_rho": ((results.get("top16_leaf89_recall_extension") or {}).get("validation_selection") or {}).get("selected_direct_sum_ops_over_rho"),
            "recall_extension_precision": ((results.get("top16_leaf89_recall_extension") or {}).get("validation_selection") or {}).get("precision"),
            "recall_extension_recall": ((results.get("top16_leaf89_recall_extension") or {}).get("validation_selection") or {}).get("recall"),
            "source_exists": source_exists,
            "training_row_count": len(training_rows),
            "validation_case_count": len(examples),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P996 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p993", default=str(DEFAULT_P993), help="P993 source JSON")
    parser.add_argument("--p994", default=str(DEFAULT_P994), help="P994 source JSON")
    parser.add_argument("--p995", default=str(DEFAULT_P995), help="P995 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="P995 validation source window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    extension = payload["rule_results"]["top16_leaf89_recall_extension"]
    extension_selection = extension["validation_selection"]
    print(
        "claim={claim} guard_first_ops_rho={guard_first} guard_full_ops_rho={guard_full} "
        "extension_selected={ext_sel} extension_pos={ext_pos} extension_precision={ext_precision} "
        "extension_recall={ext_recall} extension_derivers={ext_derivers} out={out}".format(
            claim=payload["claim_status"],
            guard_first=summary.get("p995_guard_first_derivation_ops_over_rho"),
            guard_full=summary.get("p995_guard_full_charge_ops_over_rho"),
            ext_sel=extension_selection.get("selected_count"),
            ext_pos=extension_selection.get("selected_positive_count"),
            ext_precision=extension_selection.get("precision"),
            ext_recall=extension_selection.get("recall"),
            ext_derivers=extension["reconstruction"].get("secret_deriving_group_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
