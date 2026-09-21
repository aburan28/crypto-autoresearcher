#!/usr/bin/env python3
"""P995 public precision guard for the p231 branch-switch selector."""

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
import low_term_total2_p994_p231_fixed_branch_forward_validation as p994


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p995_p231_branch_precision_guard.md"
DEFAULT_P993 = STATE_DIR / "low_term_total2_p993_p231_branch_switch_selector_scout_probe.json"
DEFAULT_P994 = STATE_DIR / "low_term_total2_p994_p231_fixed_branch_forward_validation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p995_p231_branch_precision_guard_probe.json"
SCHEMA = "ecdlp.low_term_total2_p995_p231_branch_precision_guard.v1"
DEFAULT_WINDOW = "11920_11927"
DEFAULT_TARGET = "22050.cf1@11731"
BASE_RULE = "top_k <= 7"


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


def leaf_gap_tuple(features: dict[str, Any]) -> list[int]:
    return [int_value(value) for value in features.get("leaf_gap_tuple") or []]


def max_or_none(values: list[int]) -> int | None:
    return max(values) if values else None


def frozen_base_rule(features: dict[str, Any]) -> bool:
    return int_value(features.get("top_k")) <= 7


def guard_specs() -> list[dict[str, Any]]:
    return [
        {
            "name": "contains_leaf_89",
            "description": "unique_leaf_indices contains 89",
            "complexity": 1,
            "predicate": lambda f: 89 in leaf_indices(f),
        },
        {
            "name": "max_leaf_index_ge_89",
            "description": "max(unique_leaf_indices) >= 89",
            "complexity": 2,
            "predicate": lambda f: (max_or_none(leaf_indices(f)) or -1) >= 89,
        },
        {
            "name": "max_leaf_gap_ge_70",
            "description": "max(leaf_gap_tuple) >= 70",
            "complexity": 2,
            "predicate": lambda f: (max_or_none(leaf_gap_tuple(f)) or -1) >= 70,
        },
        {
            "name": "unique_leaf_count_ge_3",
            "description": "unique_leaf_count >= 3",
            "complexity": 3,
            "predicate": lambda f: int_value(f.get("unique_leaf_count")) >= 3,
        },
        {
            "name": "unique_leaf_count_ge_4",
            "description": "unique_leaf_count >= 4",
            "complexity": 3,
            "predicate": lambda f: int_value(f.get("unique_leaf_count")) >= 4,
        },
        {
            "name": "unique_leaf_count_ge_5",
            "description": "unique_leaf_count >= 5",
            "complexity": 3,
            "predicate": lambda f: int_value(f.get("unique_leaf_count")) >= 5,
        },
        {
            "name": "same_leaf_indices",
            "description": "same_leaf_indices is true",
            "complexity": 3,
            "predicate": lambda f: bool(f.get("same_leaf_indices")),
        },
        {
            "name": "count_double_pair_ge_6",
            "description": "count_double_pair >= 6",
            "complexity": 4,
            "predicate": lambda f: int_value(f.get("count_double_pair")) >= 6,
        },
        {
            "name": "count_double_pair_ge_8",
            "description": "count_double_pair >= 8",
            "complexity": 4,
            "predicate": lambda f: int_value(f.get("count_double_pair")) >= 8,
        },
        {
            "name": "count_shape_2p2_ge_6",
            "description": "count_shape_2p2 >= 6",
            "complexity": 4,
            "predicate": lambda f: int_value(f.get("count_shape_2p2")) >= 6,
        },
        {
            "name": "count_shape_2p2_ge_8",
            "description": "count_shape_2p2 >= 8",
            "complexity": 4,
            "predicate": lambda f: int_value(f.get("count_shape_2p2")) >= 8,
        },
        {
            "name": "count_span2_ge_2",
            "description": "count_span2 >= 2",
            "complexity": 5,
            "predicate": lambda f: int_value(f.get("count_span2")) >= 2,
        },
        {
            "name": "count_span2_ge_4",
            "description": "count_span2 >= 4",
            "complexity": 5,
            "predicate": lambda f: int_value(f.get("count_span2")) >= 4,
        },
        {
            "name": "not_low_term_span_total3",
            "description": "leaf_selector != mode_low_term_span_total3",
            "complexity": 5,
            "predicate": lambda f: str(f.get("leaf_selector")) != "mode_low_term_span_total3",
        },
        {
            "name": "selector_hash_or_hybrid",
            "description": "leaf_selector is hash_leaf_total6 or hybrid_support_monic_b_total6",
            "complexity": 6,
            "predicate": lambda f: str(f.get("leaf_selector"))
            in {"mode_hash_leaf_total6", "mode_hybrid_support_monic_b_total6"},
        },
    ]


def p994_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    selection = summary.get("selection") or {}
    return {
        "p994_claim_expected": payload.get("claim_status") == "P994_FIXED_BRANCH_FORWARD_SECRET_DERIVATION",
        "p994_control_pass": bool(summary.get("control_pass")),
        "p994_forward_positive_recovered": int_value(selection.get("selected_positive_count")) > 0,
        "p994_rule_expected": summary.get("frozen_rule") == BASE_RULE,
        "p994_secret_deriving_group": int_value(summary.get("secret_deriving_group_count")) > 0,
    }


def load_training_rows(p993_path: Path, p994_path: Path) -> list[dict[str, Any]]:
    sources = [
        ("p993_heldout", p993_path, ("diagnostics", "heldout_selected_cases")),
        ("p994_forward", p994_path, ("diagnostics", "selected_cases")),
    ]
    rows: list[dict[str, Any]] = []
    for source_name, path, keys in sources:
        payload = load_json(path)
        cases: Any = payload
        for key in keys:
            cases = (cases or {}).get(key)
        for case in cases or []:
            features = case.get("features") or {}
            if not frozen_base_rule(features):
                continue
            rows.append(
                {
                    "case_id": case.get("case_id"),
                    "features": features,
                    "label_positive": bool(case.get("label_positive")),
                    "source": source_name,
                    "source_ops_over_rho": case.get("source_ops_over_rho"),
                    "source_public_key_verified": case.get("source_public_key_verified"),
                    "source_rank": case.get("source_rank"),
                    "source_relation_count": case.get("source_relation_count"),
                    "transfer_index": case.get("transfer_index"),
                }
            )
    return rows


def summarize_selection(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
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
    for example in examples:
        case = example.get("source_case") or {}
        rows.append(
            {
                "label_positive": example.get("label_positive"),
                "source_ops_over_rho": case.get("source_ops_over_rho"),
                "transfer_index": case.get("transfer_index"),
            }
        )
    selected_rows = []
    for example in selected:
        case = example.get("source_case") or {}
        selected_rows.append(
            {
                "label_positive": example.get("label_positive"),
                "source_ops_over_rho": case.get("source_ops_over_rho"),
                "transfer_index": case.get("transfer_index"),
            }
        )
    return summarize_selection(rows, selected_rows)


def score_guards(training_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], Callable[[dict[str, Any]], bool], list[dict[str, Any]]]:
    scored: list[dict[str, Any]] = []
    specs = guard_specs()
    for spec in specs:
        predicate = spec["predicate"]
        selected = [row for row in training_rows if predicate(row.get("features") or {})]
        metrics = summarize_selection(training_rows, selected)
        scored.append(
            {
                "complexity": spec["complexity"],
                "description": spec["description"],
                "name": spec["name"],
                **metrics,
            }
        )
    scored.sort(
        key=lambda row: (
            -int(float(row.get("precision") or 0.0) == 1.0),
            -int_value(row.get("selected_positive_count")),
            -float(row.get("recall") or 0.0),
            int_value(row.get("selected_count"), 10**9),
            float(row.get("selected_direct_sum_ops_over_rho") or 10**9),
            int_value(row.get("complexity"), 10**9),
            str(row.get("name")),
        )
    )
    chosen = next((row for row in scored if int_value(row.get("selected_positive_count")) > 0), scored[0] if scored else {})
    predicate_by_name = {spec["name"]: spec["predicate"] for spec in specs}
    chosen_fn = predicate_by_name.get(str(chosen.get("name")), lambda _features: False)
    return chosen, chosen_fn, scored


def determine_claim(
    control_pass: bool,
    source_exists: bool,
    chosen_guard: dict[str, Any],
    selection: dict[str, Any],
    reconstruction_errors: int,
    groups: dict[str, Any],
) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P995_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P995_SOURCE_WINDOW_MISSING"
    if int_value(chosen_guard.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P995_NO_TRAINING_GUARD_WITH_POSITIVE_RECALL"
    if int_value(selection.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P995_PRECISION_GUARD_MISSES_FORWARD_SOURCE_SIGNAL"
    if (selection.get("precision_lift_over_prevalence") or 0.0) <= 1.0:
        return "P995_PRECISION_GUARD_RECALLS_FORWARD_WITHOUT_LIFT"
    if reconstruction_errors:
        return "P995_PRECISION_GUARD_RECALLS_FORWARD_BUT_RECONSTRUCTION_ERRORS"
    if int_value(groups.get("secret_deriving_group_count")) > 0:
        if (selection.get("selected_direct_sum_ops_over_rho") or 10**9) < 1.0:
            return "P995_PRECISION_GUARD_FORWARD_BELOW_RHO_SECRET_DERIVATION"
        return "P995_PRECISION_GUARD_FORWARD_SECRET_DERIVATION"
    return "P995_PRECISION_GUARD_FORWARD_RECOVERS_SOURCE_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p993_path = Path(args.p993)
    p994_path = Path(args.p994)
    p994_payload = load_json(p994_path)
    controls = p994_controls(p994_payload)
    control_pass = all(controls.values())
    source_path = p868.source_path(args.window)
    source_exists = source_path.exists()
    training_rows = load_training_rows(p993_path, p994_path)
    chosen_guard, chosen_fn, scored_guards = score_guards(training_rows)
    if not hasattr(args, "train_transfer_max"):
        args.train_transfer_max = -1
    examples = p993.build_examples(args) if source_exists else []
    base_selected = [row for row in examples if frozen_base_rule(row["features"])]
    guarded_selected = [row for row in base_selected if chosen_fn(row["features"])]
    reconstructed, verifier = p993.reconstruct_examples(guarded_selected)
    baseline_rank = int_value((p994_payload.get("summary") or {}).get("baseline_mixed_wide_relation_rank"))
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    base_selection = summarize_examples(examples, base_selected)
    guarded_selection = summarize_examples(examples, guarded_selected)
    claim = determine_claim(control_pass, source_exists, chosen_guard, guarded_selection, reconstruction_error_count, groups)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p993_source": str(p993_path),
            "p994_source": str(p994_path),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p993_source_sha256": sha256_file(p993_path),
            "p994_source_sha256": sha256_file(p994_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P995_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "diagnostics": {
            "base_selected_cases": [p993.public_case_summary(row) for row in base_selected],
            "best_reconstructed_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "guard_candidate_scores": scored_guards,
            "guarded_selected_cases": [p993.public_case_summary(row) for row in guarded_selected],
            "guarded_selected_reconstructed_cases": [
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
            "training_rows": training_rows,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "TRAINED-GUARD: guard is chosen from P993/P994 selected rows before validation on 11920_11927.",
            "PUBLIC-PREDICATE BOUNDARY: guard inputs are P869 public features only.",
            "SOURCE-LABEL BOUNDARY: source-positive labels are used only for guard scoring and evaluation.",
            "PRECISION-ONLY STEP: this does not yet provide sparse linear algebra, target descent, or a full faster-than-rho algorithm.",
        ],
        "method": "p995_p231_branch_precision_guard",
        "parameters": {
            "base_rule": BASE_RULE,
            "baseline_rank": baseline_rank,
            "guard_search_count": len(scored_guards),
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "training_sources": [str(p993_path), str(p994_path)],
            "window": args.window,
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "base_selection": base_selection,
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "chosen_guard": chosen_guard,
            "claim_status": claim,
            "control_pass": control_pass,
            "exact_tail_group_count": groups["exact_tail_group_count"],
            "exact_term_basis_group_count": groups["exact_term_basis_group_count"],
            "form_order": groups["form_order"],
            "form_order_count": groups["form_order_count"],
            "guarded_selection": guarded_selection,
            "raw_form_count": groups["raw_form_count"],
            "reconstructed_guarded_selected_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "secret_deriving_group_count": groups["secret_deriving_group_count"],
            "source_exists": source_exists,
            "target_basis_present": bool(groups.get("target_basis")),
            "target_basis_secret_derivation": bool((groups.get("target_basis") or {}).get("mixed_wide_relations_derive_secret")),
            "target_exact_tail_present": bool(groups.get("target_exact_tail")),
            "target_exact_tail_secret_derivation": bool((groups.get("target_exact_tail") or {}).get("mixed_wide_relations_derive_secret")),
            "training_row_count": len(training_rows),
            "training_positive_count": sum(1 for row in training_rows if row.get("label_positive")),
            "unique_form_count": groups["unique_form_count"],
        },
        "target_groups": {
            "exact_term_basis": groups.get("target_basis"),
            "exact_tail_expression": groups.get("target_exact_tail"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P995 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p993", default=str(DEFAULT_P993), help="P993 source JSON")
    parser.add_argument("--p994", default=str(DEFAULT_P994), help="P994 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="Forward p231 source window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    guarded = summary["guarded_selection"]
    base = summary["base_selection"]
    guard = summary["chosen_guard"]
    print(
        "claim={claim} source_exists={source_exists} guard={guard} train_sel={train_sel} "
        "train_sel_pos={train_pos} base_selected={base_selected} guarded_selected={guarded_selected} "
        "guarded_pos={guarded_pos} guarded_lift={lift} guarded_ops_rho={ops} "
        "reconstructed={reconstructed} forms={forms} derivers={derivers} out={out}".format(
            claim=payload["claim_status"],
            source_exists=summary.get("source_exists"),
            guard=guard.get("name"),
            train_sel=guard.get("selected_count"),
            train_pos=guard.get("selected_positive_count"),
            base_selected=base.get("selected_count"),
            guarded_selected=guarded.get("selected_count"),
            guarded_pos=guarded.get("selected_positive_count"),
            lift=guarded.get("precision_lift_over_prevalence"),
            ops=guarded.get("selected_direct_sum_ops_over_rho"),
            reconstructed=summary.get("reconstructed_guarded_selected_count"),
            forms=summary.get("unique_form_count"),
            derivers=summary.get("secret_deriving_group_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
