#!/usr/bin/env python3
"""P999 public hash-basis quality discriminator for p231."""

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
import low_term_total2_p998_p231_branch_ensemble_selector as p998


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p999_p231_hash_basis_quality.md"
DEFAULT_P998 = STATE_DIR / "low_term_total2_p998_p231_branch_ensemble_selector_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p999_p231_hash_basis_quality_probe.json"
SCHEMA = "ecdlp.low_term_total2_p999_p231_hash_basis_quality.v1"
DEFAULT_TARGET = "22050.cf1@11731"
DEFAULT_VALIDATION_WINDOW = "11944_11951"
TARGET_BASIS = "[6,6,9,9]"


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


def selected_ops(row: dict[str, Any]) -> float:
    return float((row.get("source_case") or {}).get("source_ops_over_rho") or row.get("source_ops_over_rho") or 0.0)


def selected_transfer(row: dict[str, Any]) -> int:
    return int_value((row.get("source_case") or {}).get("transfer_index", row.get("transfer_index")))


def p998_controls(payload: dict[str, Any]) -> dict[str, Any]:
    target = target_basis_group(payload)
    return {
        "p998_claim_expected": payload.get("claim_status") == "P998_BRANCH_ENSEMBLE_FORWARD_SECRET_DERIVATION",
        "p998_control_pass": bool((payload.get("summary") or {}).get("control_pass")),
        "p998_target_basis_present": bool(target),
        "p998_target_basis_derives": bool((target or {}).get("mixed_wide_relations_derive_secret")),
    }


def target_basis_group(payload: dict[str, Any]) -> dict[str, Any] | None:
    groups = (((payload.get("validation") or {}).get("diagnostics") or {}).get("best_reconstructed_groups") or [])
    for group in groups:
        if group.get("group_type") == "exact_term_basis" and group.get("group_key") == TARGET_BASIS:
            return group
    return None


def selected_training_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    target_group = target_basis_group(payload) or {}
    target_ids = {str(case_id) for case_id in target_group.get("case_ids") or []}
    rows = []
    for row in (((payload.get("validation") or {}).get("diagnostics") or {}).get("selected_cases") or []):
        features = {
            "leaf_gap_tuple": row.get("leaf_gap_tuple"),
            "leaf_selector": row.get("leaf_selector"),
            "leaf_selector_family": row.get("leaf_selector_family"),
            "salt_gap": row.get("salt_gap"),
            "top_k": row.get("top_k"),
            "unique_leaf_indices": row.get("unique_leaf_indices"),
        }
        rows.append(
            {
                "case_id": row.get("case_id"),
                "derives_secret": bool(row.get("derives_secret")),
                "features": features,
                "label_positive": bool(row.get("label_positive")),
                "source_ops_over_rho": row.get("source_ops_over_rho"),
                "source_rank": row.get("source_rank"),
                "target_basis_positive": str(row.get("case_id")) in target_ids,
                "transfer_index": row.get("transfer_index"),
            }
        )
    return rows


def summarize_training(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row.get("target_basis_positive")]
    selected_positive = [row for row in selected if row.get("target_basis_positive")]
    selected_source_positive = [row for row in selected if row.get("label_positive")]
    precision = safe_ratio(len(selected_positive), len(selected))
    prevalence = safe_ratio(len(positives), len(rows))
    return {
        "case_count": len(rows),
        "target_basis_positive_count": len(positives),
        "target_basis_precision": precision,
        "target_basis_precision_lift": safe_ratio(precision or 0.0, prevalence or 0.0) if prevalence else None,
        "target_basis_prevalence": prevalence,
        "target_basis_recall": safe_ratio(len(selected_positive), len(positives)),
        "selected_count": len(selected),
        "selected_direct_sum_ops_over_rho": round(sum(selected_ops(row) for row in selected), 8),
        "selected_source_positive_count": len(selected_source_positive),
        "selected_target_basis_positive_count": len(selected_positive),
    }


def summarize_source_selection(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
    base = p998.summarize_selection(examples, selected)
    return {
        **base,
        "useful_amortized_ops_over_rho": p998.useful_amortized(base),
    }


def candidate_rules() -> list[dict[str, Any]]:
    return [
        {
            "name": "hash_top7_leaf_34_47_56_salt_ge6",
            "description": "mode_hash_leaf_total6, top_k == 7, leaves [34,47,56], salt_gap >= 6",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and leaf_indices(f) == [34, 47, 56]
            and int_value(f.get("salt_gap")) >= 6,
        },
        {
            "name": "hash_top7_gap_0_13_22_salt_ge6",
            "description": "mode_hash_leaf_total6, top_k == 7, leaf gaps [0,13,22], salt_gap >= 6",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and leaf_gap_tuple(f) == [0, 13, 22]
            and int_value(f.get("salt_gap")) >= 6,
        },
        {
            "name": "hash_top7_gap_0_13_22_salt_ge4",
            "description": "mode_hash_leaf_total6, top_k == 7, leaf gaps [0,13,22], salt_gap >= 4",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and leaf_gap_tuple(f) == [0, 13, 22]
            and int_value(f.get("salt_gap")) >= 4,
        },
        {
            "name": "hash_top7_leaf_34_47_56",
            "description": "mode_hash_leaf_total6, top_k == 7, leaves [34,47,56]",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and leaf_indices(f) == [34, 47, 56],
        },
        {
            "name": "hash_gap_0_13_22_salt_ge6_top12",
            "description": "mode_hash_leaf_total6, leaf gaps [0,13,22], salt_gap >= 6, top_k <= 12",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and leaf_gap_tuple(f) == [0, 13, 22]
            and int_value(f.get("salt_gap")) >= 6
            and int_value(f.get("top_k")) <= 12,
        },
        {
            "name": "hash_top7_salt_ge6",
            "description": "mode_hash_leaf_total6, top_k == 7, salt_gap >= 6",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and int_value(f.get("salt_gap")) >= 6,
        },
        {
            "name": "hash_top7_gap_0_13_22",
            "description": "mode_hash_leaf_total6, top_k == 7, leaf gaps [0,13,22]",
            "predicate": lambda f: str(f.get("leaf_selector")) == "mode_hash_leaf_total6"
            and int_value(f.get("top_k")) == 7
            and leaf_gap_tuple(f) == [0, 13, 22],
        },
    ]


def score_rule(rule: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = [row for row in rows if rule["predicate"](row.get("features") or {})]
    return {
        "description": rule["description"],
        "name": rule["name"],
        **summarize_training(rows, selected),
    }


def choose_rule(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], Predicate, list[dict[str, Any]]]:
    rules = candidate_rules()
    scored = [score_rule(rule, rows) for rule in rules]
    scored.sort(
        key=lambda row: (
            -int(float(row.get("target_basis_precision") or 0.0) == 1.0),
            -float(row.get("target_basis_recall") or 0.0),
            int_value(row.get("selected_count"), 10**9),
            float(row.get("selected_direct_sum_ops_over_rho") or 10**9),
            str(row.get("name")),
        )
    )
    chosen = next((row for row in scored if int_value(row.get("selected_target_basis_positive_count")) > 0), scored[0])
    predicates = {rule["name"]: rule["predicate"] for rule in rules}
    return chosen, predicates[str(chosen["name"])], scored


def build_validation_examples(window: str, targets: str, min_source_rank: int) -> list[dict[str, Any]]:
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


def find_group(groups: dict[str, Any], group_type: str, group_key: str) -> dict[str, Any] | None:
    for group in groups.get("best_groups") or []:
        if group.get("group_type") == group_type and group.get("group_key") == group_key:
            return group
    return None


def derive_case_ids(groups: dict[str, Any]) -> set[str]:
    case_ids: set[str] = set()
    for group in groups.get("best_groups") or []:
        if group.get("mixed_wide_relations_derive_secret"):
            case_ids.update(str(case_id) for case_id in group.get("case_ids") or [])
    return case_ids


def analyze_validation(examples: list[dict[str, Any]], selected: list[dict[str, Any]], baseline_rank: int) -> dict[str, Any]:
    reconstructed, verifier = p993.reconstruct_examples(selected)
    groups = p993.summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    deriving_case_ids = derive_case_ids(groups)
    target_basis = find_group(groups, "exact_term_basis", TARGET_BASIS)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    selection = summarize_source_selection(examples, selected)
    return {
        "diagnostics": {
            "best_reconstructed_groups": groups["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "selected_cases": [
                {
                    **p998.feature_summary(row),
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
            "target_basis": target_basis,
            "target_basis_present": bool(target_basis),
            "target_basis_secret_derivation": bool((target_basis or {}).get("mixed_wide_relations_derive_secret")),
            "target_basis_selected_case_amortized_ops_over_rho": (target_basis or {}).get("selected_case_amortized_ops_over_rho"),
            "unique_form_count": groups["unique_form_count"],
        },
        "selection": selection,
    }


def determine_claim(control_pass: bool, source_exists: bool, validation: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P999_CONTROL_FAILURE"
    if not source_exists:
        return "NEGATIVE_RESULT_P999_SOURCE_WINDOW_MISSING"
    selection = validation.get("selection") or {}
    reconstruction = validation.get("reconstruction") or {}
    if int_value(selection.get("selected_count")) == 0:
        return "NEGATIVE_RESULT_P999_HASH_BASIS_RULE_SELECTS_NO_FORWARD_ROWS"
    if int_value(reconstruction.get("reconstruction_error_count")):
        return "P999_HASH_BASIS_FORWARD_RECONSTRUCTION_ERRORS"
    target_cost = reconstruction.get("target_basis_selected_case_amortized_ops_over_rho")
    if reconstruction.get("target_basis_secret_derivation") and (target_cost or 10**9) < 1.0:
        return "P999_HASH_BASIS_TARGET_FORWARD_BELOW_RHO"
    if int_value(reconstruction.get("secret_deriving_group_count")) > 0:
        return "P999_HASH_BASIS_RULE_FORWARD_SECRET_DERIVATION"
    return "NEGATIVE_RESULT_P999_HASH_BASIS_RULE_NO_FORWARD_SECRET_DERIVATION"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p998_path = Path(args.p998)
    p998_payload = load_json(p998_path)
    controls = p998_controls(p998_payload)
    control_pass = all(controls.values())
    training_rows = selected_training_rows(p998_payload)
    chosen, predicate, scored = choose_rule(training_rows)
    source_path = p868.source_path(args.validation_window)
    source_exists = source_path.exists()
    validation_examples = build_validation_examples(args.validation_window, args.targets, args.min_source_rank) if source_exists else []
    selected = [row for row in validation_examples if predicate(row.get("features") or {})]
    baseline_rank = 8
    validation = analyze_validation(validation_examples, selected, baseline_rank) if source_exists else {}
    claim = determine_claim(control_pass, source_exists, validation)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p998_source": str(p998_path),
            "script": str(Path(__file__)),
            "source_window": str(source_path),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p998_source_sha256": sha256_file(p998_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(source_path),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P999_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "RECONSTRUCTED-LABEL TRAINING: P999 trains on P998 reconstructed exact-basis membership, not source-positive labels.",
            "PUBLIC-PREDICATE BOUNDARY: rule inputs are public leaf selector, top-k, salt gap, and leaf tuple/gap features.",
            "NO-END-TO-END-BREAK: no sparse linear algebra, target descent, or cryptographic-size claim is established.",
        ],
        "method": "p999_p231_hash_basis_quality",
        "parameters": {
            "baseline_rank": baseline_rank,
            "candidate_rule_count": len(scored),
            "min_source_rank": args.min_source_rank,
            "target_basis": TARGET_BASIS,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "validation_window": args.validation_window,
        },
        "rule_search": {
            "chosen_rule": chosen,
            "top_rules": scored[:12],
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "chosen_rule_name": chosen.get("name"),
            "claim_status": claim,
            "control_pass": control_pass,
            "source_exists": source_exists,
            "training_row_count": len(training_rows),
            "training_target_basis_count": sum(1 for row in training_rows if row.get("target_basis_positive")),
            "validation_case_count": len(validation_examples),
            "validation_first_derivation_ops_over_rho": (((validation.get("early_stop") or {}).get("first_deriving_case") or {}).get("public_order_charged_ops_over_rho")),
            "validation_secret_deriving_group_count": ((validation.get("reconstruction") or {}).get("secret_deriving_group_count")),
            "validation_selected_count": ((validation.get("selection") or {}).get("selected_count")),
            "validation_source_positive_count": ((validation.get("selection") or {}).get("selected_positive_count")),
            "validation_source_precision": ((validation.get("selection") or {}).get("precision")),
            "validation_target_basis_present": ((validation.get("reconstruction") or {}).get("target_basis_present")),
            "validation_target_basis_secret_derivation": ((validation.get("reconstruction") or {}).get("target_basis_secret_derivation")),
            "validation_target_basis_selected_case_amortized_ops_over_rho": ((validation.get("reconstruction") or {}).get("target_basis_selected_case_amortized_ops_over_rho")),
        },
        "validation": validation,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P999 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for source-positive labels")
    parser.add_argument("--p998", default=str(DEFAULT_P998), help="P998 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
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
        "source_pos={source_pos} target_present={target_present} target_derives={target_derives} "
        "target_amortized={target_amortized} derivers={derivers} first_derivation={first_derivation} out={out}".format(
            claim=payload["claim_status"],
            rule=summary.get("chosen_rule_name"),
            source_exists=summary.get("source_exists"),
            selected=summary.get("validation_selected_count"),
            source_pos=summary.get("validation_source_positive_count"),
            target_present=summary.get("validation_target_basis_present"),
            target_derives=summary.get("validation_target_basis_secret_derivation"),
            target_amortized=summary.get("validation_target_basis_selected_case_amortized_ops_over_rho"),
            derivers=summary.get("validation_secret_deriving_group_count"),
            first_derivation=summary.get("validation_first_derivation_ops_over_rho"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
