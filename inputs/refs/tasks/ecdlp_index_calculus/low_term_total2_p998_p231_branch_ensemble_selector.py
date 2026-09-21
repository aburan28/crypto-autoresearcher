#!/usr/bin/env python3
"""P998 public branch-ensemble selector for p231 source branch switching."""

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
import low_term_total2_p996_p231_early_stop_recall_split as p996


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p998_p231_branch_ensemble_selector.md"
DEFAULT_P997 = STATE_DIR / "low_term_total2_p997_p231_frozen_top16_leaf89_forward_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p998_p231_branch_ensemble_selector_probe.json"
SCHEMA = "ecdlp.low_term_total2_p998_p231_branch_ensemble_selector.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_TRAIN_WINDOWS = "11904_11911,11912_11919,11920_11927,11928_11935"
DEFAULT_VALIDATION_WINDOW = "11936_11943"


Predicate = Callable[[dict[str, Any]], bool]


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


def contains_leaf89(features: dict[str, Any]) -> bool:
    return 89 in leaf_indices(features)


def selected_ops(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or row.get("source_ops_over_rho") or 0.0)


def selected_transfer(row: dict[str, Any]) -> int:
    return int_value((row.get("source_case") or {}).get("transfer_index", row.get("transfer_index")))


def feature_summary(row: dict[str, Any]) -> dict[str, Any]:
    features = row.get("features") or {}
    case = row.get("source_case") or {}
    return {
        "case_id": row.get("case_id"),
        "label_positive": row.get("label_positive"),
        "leaf_gap_tuple": features.get("leaf_gap_tuple"),
        "leaf_selector": features.get("leaf_selector"),
        "leaf_selector_family": features.get("leaf_selector_family"),
        "salt_gap": features.get("salt_gap"),
        "source_ops_over_rho": case.get("source_ops_over_rho"),
        "source_rank": case.get("source_rank"),
        "top_k": features.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "unique_leaf_indices": features.get("unique_leaf_indices"),
    }


def summarize_selection(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in examples if row.get("label_positive")]
    selected_positive = [row for row in selected if row.get("label_positive")]
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(examples))
    return {
        "case_count": len(examples),
        "positive_count": len(positives),
        "positive_transfer_count": len({selected_transfer(row) for row in positives}),
        "precision": precision,
        "precision_lift_over_prevalence": safe_ratio(precision or 0.0, prevalence or 0.0) if prevalence else None,
        "prevalence": prevalence,
        "recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
        "selected_positive_count": len(selected_positive),
        "selected_positive_transfer_count": len({selected_transfer(row) for row in selected_positive}),
    }


def useful_amortized(selection: dict[str, Any]) -> float | None:
    return safe_ratio(selection.get("selected_direct_sum_ops_over_rho"), selection.get("selected_positive_count"))


def p997_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "p997_claim_expected": payload.get("claim_status") == "NEGATIVE_RESULT_P997_FROZEN_TOP16_LEAF89_MISSES_FORWARD_SOURCE_SIGNAL",
        "p997_control_pass": bool(summary.get("control_pass")),
        "p997_leaf89_selected_zero_positive": int_value(summary.get("top16_selected_count")) > 0
        and int_value(summary.get("top16_selected_positive_count")) == 0,
    }


def build_window_examples(window: str, targets: str, min_source_rank: int) -> list[dict[str, Any]]:
    args = argparse.Namespace(
        min_source_rank=min_source_rank,
        targets=targets,
        train_transfer_max=-1,
        window=window,
    )
    rows = p993.build_examples(args)
    for row in rows:
        row["source_window"] = window
    return rows


def load_examples(windows: list[str], targets: str, min_source_rank: int) -> tuple[list[dict[str, Any]], dict[str, bool]]:
    out: list[dict[str, Any]] = []
    exists: dict[str, bool] = {}
    for window in windows:
        path = p868.source_path(window)
        exists[window] = path.exists()
        if path.exists():
            out.extend(build_window_examples(window, targets, min_source_rank))
    return out, exists


def primitive_rules() -> list[dict[str, Any]]:
    return [
        {
            "name": "leaf89_salt_not_1_3_top16",
            "description": "contains leaf 89, salt_gap not in {1,3}, top_k <= 16",
            "family": "leaf89",
            "predicate": lambda f: contains_leaf89(f)
            and int_value(f.get("salt_gap")) not in {1, 3}
            and int_value(f.get("top_k")) <= 16,
        },
        {
            "name": "leaf89_salt_ge2_not3_top16",
            "description": "contains leaf 89, salt_gap >= 2, salt_gap != 3, top_k <= 16",
            "family": "leaf89",
            "predicate": lambda f: contains_leaf89(f)
            and int_value(f.get("salt_gap")) >= 2
            and int_value(f.get("salt_gap")) != 3
            and int_value(f.get("top_k")) <= 16,
        },
        {
            "name": "leaf89_top16",
            "description": "contains leaf 89, top_k <= 16",
            "family": "leaf89",
            "predicate": lambda f: contains_leaf89(f) and int_value(f.get("top_k")) <= 16,
        },
        {
            "name": "leaf89_gap_ge70_top16",
            "description": "contains leaf 89, max leaf gap >= 70, top_k <= 16",
            "family": "leaf89",
            "predicate": lambda f: contains_leaf89(f)
            and (max_or_none(leaf_gap_tuple(f)) or -1) >= 70
            and int_value(f.get("top_k")) <= 16,
        },
        {
            "name": "hash_salt_le1_top12",
            "description": "mode_hash_leaf_total6, salt_gap <= 1, top_k <= 12",
            "family": "hash_low_gap",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("salt_gap")) <= 1
            and int_value(f.get("top_k")) <= 12,
        },
        {
            "name": "hash_salt_le2_top12",
            "description": "mode_hash_leaf_total6, salt_gap <= 2, top_k <= 12",
            "family": "hash_low_gap",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("salt_gap")) <= 2
            and int_value(f.get("top_k")) <= 12,
        },
        {
            "name": "hash_no89_salt_le1_top12",
            "description": "mode_hash_leaf_total6 without leaf 89, salt_gap <= 1, top_k <= 12",
            "family": "hash_low_gap",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and not contains_leaf89(f)
            and int_value(f.get("salt_gap")) <= 1
            and int_value(f.get("top_k")) <= 12,
        },
        {
            "name": "hash_leaf_gap_max_le37_top12",
            "description": "mode_hash_leaf_total6, max leaf gap <= 37, top_k <= 12",
            "family": "hash_low_gap",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and (max_or_none(leaf_gap_tuple(f)) or 10**9) <= 37
            and int_value(f.get("top_k")) <= 12,
        },
    ]


def candidate_rules() -> list[dict[str, Any]]:
    primitives = primitive_rules()
    out: list[dict[str, Any]] = []
    for rule in primitives:
        out.append({**rule, "kind": "primitive"})
    leaf_rules = [rule for rule in primitives if rule["family"] == "leaf89"]
    hash_rules = [rule for rule in primitives if rule["family"] == "hash_low_gap"]
    for leaf_rule in leaf_rules:
        for hash_rule in hash_rules:
            out.append(
                {
                    "description": f"{leaf_rule['description']} OR {hash_rule['description']}",
                    "family": "branch_ensemble",
                    "kind": "two_branch_or",
                    "left": leaf_rule["name"],
                    "name": f"{leaf_rule['name']}__OR__{hash_rule['name']}",
                    "predicate": lambda f, a=leaf_rule["predicate"], b=hash_rule["predicate"]: a(f) or b(f),
                    "right": hash_rule["name"],
                }
            )
    return out


def score_rule(rule: dict[str, Any], examples: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in examples if rule["predicate"](row.get("features") or {})]
    metrics = summarize_selection(examples, selected)
    return {
        "description": rule["description"],
        "family": rule["family"],
        "kind": rule["kind"],
        "left": rule.get("left"),
        "name": rule["name"],
        "right": rule.get("right"),
        "useful_amortized_ops_over_rho": useful_amortized(metrics),
        **metrics,
    }


def choose_rule(examples: list[dict[str, Any]]) -> tuple[dict[str, Any], Predicate, list[dict[str, Any]]]:
    rules = candidate_rules()
    scored = [score_rule(rule, examples) for rule in rules]
    scored.sort(
        key=lambda row: (
            -int(float(row.get("precision") or 0.0) == 1.0),
            -float(row.get("recall") or 0.0),
            float(row.get("useful_amortized_ops_over_rho") or 10**9),
            int_value(row.get("selected_count"), 10**9),
            0 if row.get("kind") == "two_branch_or" else 1,
            str(row.get("name")),
        )
    )
    chosen = next((row for row in scored if int_value(row.get("selected_positive_count")) > 0), scored[0])
    predicate_by_name = {rule["name"]: rule["predicate"] for rule in rules}
    return chosen, predicate_by_name[str(chosen["name"])], scored


def derive_case_ids(groups: dict[str, Any]) -> set[str]:
    case_ids: set[str] = set()
    for group in groups.get("best_groups") or []:
        if group.get("mixed_wide_relations_derive_secret"):
            case_ids.update(str(case_id) for case_id in group.get("case_ids") or [])
    return case_ids


def analyze_selection(examples: list[dict[str, Any]], selected: list[dict[str, Any]], baseline_rank: int) -> dict[str, Any]:
    reconstructed, verifier = p993.reconstruct_examples(selected)
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    deriving_case_ids = derive_case_ids(groups)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    selection = summarize_selection(examples, selected)
    return {
        "diagnostics": {
            "best_reconstructed_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "selected_cases": [
                {
                    **feature_summary(row),
                    "derives_secret": str(row.get("case_id")) in deriving_case_ids,
                    "row_key_signature": p996.row_key_signature(row),
                }
                for row in sorted(selected, key=p996.public_order_key)
            ],
        },
        "early_stop": p996.early_stop_summary(selected, deriving_case_ids),
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
        "selection": {
            **selection,
            "useful_amortized_ops_over_rho": useful_amortized(selection),
        },
    }


def determine_claim(control_pass: bool, source_exists: bool, validation: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P998_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P998_SOURCE_WINDOW_MISSING"
    selection = validation.get("selection") or {}
    reconstruction = validation.get("reconstruction") or {}
    early_stop = validation.get("early_stop") or {}
    if int_value(selection.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P998_BRANCH_ENSEMBLE_MISSES_FORWARD_SOURCE_SIGNAL"
    if (selection.get("precision_lift_over_prevalence") or 0.0) <= 1.0:
        return "P998_BRANCH_ENSEMBLE_RECALLS_FORWARD_WITHOUT_LIFT"
    if int_value(reconstruction.get("reconstruction_error_count")):
        return "P998_BRANCH_ENSEMBLE_RECALLS_FORWARD_BUT_RECONSTRUCTION_ERRORS"
    if int_value(reconstruction.get("secret_deriving_group_count")) == 0:
        return "P998_BRANCH_ENSEMBLE_FORWARD_SIGNAL_WITHOUT_SECRET_DERIVATION"
    if (selection.get("useful_amortized_ops_over_rho") or 10**9) < 1.0:
        return "P998_BRANCH_ENSEMBLE_FORWARD_USEFUL_AMORTIZED_BELOW_RHO"
    if early_stop.get("first_derivation_below_rho"):
        return "P998_BRANCH_ENSEMBLE_FORWARD_EARLY_STOP_BELOW_RHO"
    return "P998_BRANCH_ENSEMBLE_FORWARD_SECRET_DERIVATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    train_windows = [window.strip() for window in args.train_windows.split(",") if window.strip()]
    p997_payload = load_json(Path(args.p997))
    controls = p997_controls(p997_payload)
    control_pass = all(controls.values())
    training_examples, train_exists = load_examples(train_windows, args.targets, args.min_source_rank)
    chosen, predicate, scored_rules = choose_rule(training_examples)
    validation_path = p868.source_path(args.validation_window)
    source_exists = validation_path.exists()
    validation_examples = build_window_examples(args.validation_window, args.targets, args.min_source_rank) if source_exists else []
    selected_validation = [row for row in validation_examples if predicate(row.get("features") or {})]
    baseline_rank = 8
    validation = analyze_selection(validation_examples, selected_validation, baseline_rank) if source_exists else {}
    claim = determine_claim(control_pass, source_exists, validation)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p997_source": str(args.p997),
            "script": str(Path(__file__)),
            "source_window": str(validation_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p997_source_sha256": sha256_file(Path(args.p997)),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(validation_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P998_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "TRAINED-ENSEMBLE: rule is chosen from P993-P997 windows and must be judged by P998 validation.",
            "PUBLIC-PREDICATE BOUNDARY: rule inputs are public P869 features only.",
            "SOURCE-LABEL BOUNDARY: source labels are used for rule scoring and validation, not in predicate bodies.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p998_p231_branch_ensemble_selector",
        "parameters": {
            "baseline_rank": baseline_rank,
            "candidate_rule_count": len(scored_rules),
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_windows": train_windows,
            "validation_window": args.validation_window,
        },
        "rule_search": {
            "chosen_rule": chosen,
            "top_rules": scored_rules[:16],
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "chosen_rule_name": chosen.get("name"),
            "claim_status": claim,
            "control_pass": control_pass,
            "source_exists": source_exists,
            "train_exists": train_exists,
            "training_case_count": len(training_examples),
            "training_positive_count": sum(1 for row in training_examples if row.get("label_positive")),
            "validation_case_count": len(validation_examples),
            "validation_first_derivation_ops_over_rho": (((validation.get("early_stop") or {}).get("first_deriving_case") or {}).get("public_order_charged_ops_over_rho")),
            "validation_precision": ((validation.get("selection") or {}).get("precision")),
            "validation_recall": ((validation.get("selection") or {}).get("recall")),
            "validation_selected_count": ((validation.get("selection") or {}).get("selected_count")),
            "validation_selected_positive_count": ((validation.get("selection") or {}).get("selected_positive_count")),
            "validation_useful_amortized_ops_over_rho": ((validation.get("selection") or {}).get("useful_amortized_ops_over_rho")),
        },
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P998 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p997", default=str(DEFAULT_P997), help="P997 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--train-windows", default=DEFAULT_TRAIN_WINDOWS, help="Comma-separated training windows")
    parser.add_argument("--validation-window", default=DEFAULT_VALIDATION_WINDOW, help="Forward validation window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} rule={rule} source_exists={source_exists} selected={selected} "
        "selected_pos={selected_pos} precision={precision} recall={recall} useful={useful} "
        "first_derivation={first_derivation} out={out}".format(
            claim=payload["claim_status"],
            rule=summary.get("chosen_rule_name"),
            source_exists=summary.get("source_exists"),
            selected=summary.get("validation_selected_count"),
            selected_pos=summary.get("validation_selected_positive_count"),
            precision=summary.get("validation_precision"),
            recall=summary.get("validation_recall"),
            useful=summary.get("validation_useful_amortized_ops_over_rho"),
            first_derivation=summary.get("validation_first_derivation_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
