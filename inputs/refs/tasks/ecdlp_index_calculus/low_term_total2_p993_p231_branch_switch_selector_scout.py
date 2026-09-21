#!/usr/bin/env python3
"""P993 branch-switch selector scout for fresh p231 source-visible signal."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p869_p231_public_motif_predictor as p869
import low_term_total2_p985_p231_cumulative_false_positive_discriminator as p985
import low_term_total2_p989_p231_relation_independence_readiness as p989
import low_term_total2_p990_p231_term_basis_normalization_audit as p990
import low_term_total2_p992_p231_first_forward_basis_support_audit as p992


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p993_p231_branch_switch_selector_scout.md"
DEFAULT_P992 = STATE_DIR / "low_term_total2_p992_p231_first_forward_basis_support_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p993_p231_branch_switch_selector_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p993_p231_branch_switch_selector_scout.v1"
DEFAULT_WINDOW = "11904_11911"
DEFAULT_TARGET = "22050.cf1@11731"
TARGET_TERM_BASIS = p992.TARGET_TERM_BASIS
TARGET_EXACT_TAIL = p992.TARGET_EXACT_TAIL


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


def p992_controls(payload: dict[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    return {
        "p992_claim_expected": payload.get("claim_status") == "NEGATIVE_RESULT_P992_NO_FORWARD_HIGH_GAP_ROWS",
        "p992_control_pass": bool(summary.get("control_pass")),
        "p992_source_case_count_40": int_value(summary.get("source_case_count")) == 40,
        "p992_high_gap_zero": int_value(summary.get("high_gap_selected_case_count")) == 0,
        "p992_source_window_materialized": DEFAULT_WINDOW in set(summary.get("available_windows") or []),
    }


def public_case_summary(example: dict[str, Any]) -> dict[str, Any]:
    case = example["source_case"]
    features = example["features"]
    return {
        "case_id": example.get("case_id"),
        "features": {
            key: features.get(key)
            for key in (
                "all_has_double_pair",
                "count_double_pair",
                "count_shape_2p2",
                "count_span2",
                "leaf_gap_tuple",
                "leaf_selector",
                "leaf_selector_family",
                "salt_gap",
                "same_leaf_indices",
                "top_k",
                "unique_leaf_count",
                "unique_leaf_indices",
            )
        },
        "label_positive": example.get("label_positive"),
        "source_ops_over_rho": case.get("source_ops_over_rho"),
        "source_public_key_verified": case.get("source_public_key_verified"),
        "source_rank": case.get("source_rank"),
        "source_relation_count": case.get("source_relation_count"),
        "split": example.get("split"),
        "transfer_index": case.get("transfer_index"),
    }


def build_examples(args: argparse.Namespace) -> list[dict[str, Any]]:
    targets = {target.strip() for target in args.targets.split(",") if target.strip()}
    source = p868.load_json(p868.source_path(args.window))
    params = p868.repair_probe.source_parameters(source)
    probe_args = p868.repair_probe.probe_args_from_source(source)
    verifier, records, config_source, specs_by_target = p868.repair_probe.build_specs(params)
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    examples: list[dict[str, Any]] = []
    for case in p868.iter_source_cases(source, args.window, targets):
        context = p868.hit_stream_probe.scan_case_context(
            verifier,
            records,
            config_source,
            specs_by_target,
            case,
            probe_args,
            context_cache,
        )
        features = p869.public_features(case, context)
        transfer = int_value(case.get("transfer_index"))
        split = "train" if transfer <= args.train_transfer_max else "heldout"
        label_positive = bool(
            case.get("source_below_rho")
            and case.get("source_public_key_verified")
            and int_value(case.get("source_rank")) >= args.min_source_rank
        )
        examples.append(
            {
                "case_id": p869.public_case_id(case),
                "features": features,
                "label_positive": label_positive,
                "source_case": case,
                "split": split,
                "window": args.window,
            }
        )
    return examples


def summarize_split(examples: list[dict[str, Any]], selected: list[dict[str, Any]]) -> dict[str, Any]:
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


def choose_rule(train: list[dict[str, Any]]) -> tuple[dict[str, Any], Callable[[dict[str, Any]], bool], list[dict[str, Any]]]:
    chosen_metrics, chosen_fn, top_rules = p869.choose_rule(train)
    return chosen_metrics, chosen_fn, top_rules


def row_for_reconstruction(example: dict[str, Any]) -> dict[str, Any]:
    case = dict(example["source_case"])
    case["case_id"] = example["case_id"]
    case["direct_ops_over_rho"] = case.get("source_ops_over_rho")
    case["public_features"] = example.get("features")
    return case


def reconstruct_examples(examples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Any]:
    build_cache: dict[
        str,
        tuple[Any, list[dict[str, Any]], dict[str, Any], dict[str, dict[str, dict[str, Any]]], argparse.Namespace],
    ] = {}
    context_cache: dict[tuple[str, int, int, tuple[str, ...]], dict[str, Any]] = {}
    reconstructed = [
        p989.reconstruct_case(row_for_reconstruction(example), build_cache, context_cache)
        for example in examples
    ]
    for rec, example in zip(reconstructed, examples):
        rec["direct_ops_over_rho"] = (example.get("source_case") or {}).get("source_ops_over_rho")
        rec["label_positive"] = example.get("label_positive")
        rec["public_features"] = example.get("features")
    verifier = next(iter(build_cache.values()))[0] if build_cache else None
    return reconstructed, verifier


def summarize_groups(reconstructed: list[dict[str, Any]], verifier: Any, baseline_rank: int) -> dict[str, Any]:
    all_forms = [form for case in reconstructed for form in case.get("form_records") or []]
    unique = p990.unique_forms(all_forms)
    orders = sorted({int_value(form.get("order")) for form in unique if int_value(form.get("order"))})
    order = orders[0] if len(orders) == 1 else 0
    costs = {
        str(case.get("case_id")): float(case.get("direct_ops_over_rho") or 0.0)
        for case in reconstructed
    }
    grouped = p990.grouped_forms(unique)
    summaries: list[dict[str, Any]] = []
    if order:
        for group_type, by_key in grouped.items():
            for group_key, forms in by_key.items():
                summaries.append(p990.summarize_group(group_type, group_key, forms, costs, order, verifier, baseline_rank))
    summaries.sort(
        key=lambda row: (
            not row.get("mixed_wide_relations_derive_secret"),
            row.get("selected_case_amortized_ops_over_rho")
            if row.get("selected_case_amortized_ops_over_rho") is not None
            else 10**9,
            row.get("group_type"),
            row.get("group_key"),
        )
    )
    target_basis = next(
        (
            row
            for row in summaries
            if row.get("group_type") == "exact_term_basis" and row.get("group_key") == TARGET_TERM_BASIS
        ),
        None,
    )
    target_tail = next(
        (
            row
            for row in summaries
            if row.get("group_type") == "exact_tail_expression" and row.get("group_key") == TARGET_EXACT_TAIL
        ),
        None,
    )
    return {
        "best_groups": summaries[:16],
        "exact_tail_group_count": len(grouped.get("exact_tail_expression") or {}),
        "exact_term_basis_group_count": len(grouped.get("exact_term_basis") or {}),
        "form_order": order or None,
        "form_order_count": len(orders),
        "raw_form_count": len(all_forms),
        "secret_deriving_group_count": sum(1 for row in summaries if row.get("mixed_wide_relations_derive_secret")),
        "target_basis": target_basis,
        "target_exact_tail": target_tail,
        "unique_form_count": len(unique),
    }


def determine_claim(control_pass: bool, heldout: dict[str, Any], reconstruction_errors: int, groups: dict[str, Any]) -> str:
    if not control_pass:
        return "NEGATIVE_RESULT_P993_CONTROL_FAILURE"
    if int_value(heldout.get("selected_positive_count")) == 0:
        return "NEGATIVE_RESULT_P993_TRAIN_RULE_MISSES_HELDOUT_SOURCE_SIGNAL"
    if (heldout.get("precision_lift_over_prevalence") or 0.0) <= 1.0:
        return "P993_BRANCH_RULE_RECALLS_HELDOUT_SIGNAL_WITHOUT_PRECISION_LIFT"
    if reconstruction_errors:
        return "P993_BRANCH_RULE_RECALLS_HELDOUT_SIGNAL_BUT_RECONSTRUCTION_ERRORS"
    target_tail = groups.get("target_exact_tail") or {}
    target_basis = groups.get("target_basis") or {}
    if target_tail.get("mixed_wide_relations_derive_secret"):
        return "P993_BRANCH_RULE_RECONSTRUCTS_TARGET_TAIL_DERIVATION"
    if target_basis.get("mixed_wide_relations_derive_secret"):
        return "P993_BRANCH_RULE_RECONSTRUCTS_TARGET_BASIS_DERIVATION"
    if int_value(groups.get("secret_deriving_group_count")) > 0:
        return "P993_BRANCH_RULE_RECONSTRUCTS_SECRET_DERIVING_GROUP"
    return "P993_PUBLIC_BRANCH_SELECTOR_RECOVERS_HELDOUT_SOURCE_SIGNAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p992_path = Path(args.p992)
    p992_payload = load_json(p992_path)
    controls = p992_controls(p992_payload)
    control_pass = all(controls.values())
    examples = build_examples(args)
    train = [row for row in examples if row.get("split") == "train"]
    heldout = [row for row in examples if row.get("split") == "heldout"]
    chosen_metrics, chosen_fn, top_rules = choose_rule(train)
    train_selected = [row for row in train if chosen_fn(row["features"])]
    heldout_selected = [row for row in heldout if chosen_fn(row["features"])]
    reconstructed, verifier = reconstruct_examples(heldout_selected)
    baseline_rank = int_value(((p992_payload.get("summary") or {}).get("baseline_mixed_wide_relation_rank")))
    group_summary = summarize_groups(reconstructed, verifier, baseline_rank)
    reconstruction_error_count = sum(int_value(row.get("reconstructed_error_count")) for row in reconstructed)
    train_summary = summarize_split(train, train_selected)
    heldout_summary = summarize_split(heldout, heldout_selected)
    claim = determine_claim(control_pass, heldout_summary, reconstruction_error_count, group_summary)
    case_rank_hist = Counter(str(row.get("union_rank")) for row in reconstructed)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p992_source": str(p992_path),
            "script": str(Path(__file__)),
            "source_window": str(p868.source_path(args.window)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(Path(args.contract)),
            "p992_source_sha256": sha256_file(p992_path),
            "script_sha256": sha256_file(Path(__file__)),
            "source_sha256": sha256_file(p868.source_path(args.window)),
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P993_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "diagnostics": {
            "best_reconstructed_groups": group_summary["best_groups"],
            "case_rank_histogram": dict(sorted(case_rank_hist.items())),
            "heldout_selected_cases": [public_case_summary(row) for row in heldout_selected],
            "heldout_selected_reconstructed_cases": [
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
            "top_train_rules": top_rules,
            "train_selected_cases": [public_case_summary(row) for row in train_selected[:24]],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "TRAIN-ONLY SELECTOR: the chosen rule is selected only from early transfer labels.",
            "PUBLIC-PREDICATE BOUNDARY: selector features are public pre-reconstruction P869 features.",
            "SOURCE-LABEL BOUNDARY: source_public_key_verified/source_rank/source_below_rho are labels, not selector inputs.",
            "NO-END-TO-END-BREAK: held-out source recovery still needs relation independence, sparse linear algebra, and target descent.",
        ],
        "method": "p993_p231_branch_switch_selector_scout",
        "parameters": {
            "baseline_rank": baseline_rank,
            "min_source_rank": args.min_source_rank,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "train_transfer_max": args.train_transfer_max,
            "window": args.window,
        },
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "baseline_mixed_wide_relation_rank": baseline_rank,
            "chosen_rule": chosen_metrics,
            "claim_status": claim,
            "control_pass": control_pass,
            "exact_tail_group_count": group_summary["exact_tail_group_count"],
            "exact_term_basis_group_count": group_summary["exact_term_basis_group_count"],
            "form_order": group_summary["form_order"],
            "form_order_count": group_summary["form_order_count"],
            "heldout": heldout_summary,
            "raw_form_count": group_summary["raw_form_count"],
            "reconstructed_heldout_selected_count": len(reconstructed),
            "reconstruction_error_count": reconstruction_error_count,
            "secret_deriving_group_count": group_summary["secret_deriving_group_count"],
            "target_basis_present": bool(group_summary.get("target_basis")),
            "target_basis_secret_derivation": bool((group_summary.get("target_basis") or {}).get("mixed_wide_relations_derive_secret")),
            "target_exact_tail_present": bool(group_summary.get("target_exact_tail")),
            "target_exact_tail_secret_derivation": bool((group_summary.get("target_exact_tail") or {}).get("mixed_wide_relations_derive_secret")),
            "train": train_summary,
            "unique_form_count": group_summary["unique_form_count"],
        },
        "target_groups": {
            "exact_term_basis": group_summary.get("target_basis"),
            "exact_tail_expression": group_summary.get("target_exact_tail"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P993 contract path")
    parser.add_argument("--min-source-rank", type=int, default=2, help="Minimum source rank for positive labels")
    parser.add_argument("--p992", default=str(DEFAULT_P992), help="P992 source JSON")
    parser.add_argument("--targets", default=DEFAULT_TARGET, help="Comma-separated target filter")
    parser.add_argument("--train-transfer-max", type=int, default=11906, help="Largest transfer index used for training")
    parser.add_argument("--window", default=DEFAULT_WINDOW, help="Fresh p231 source window")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    rule = summary["chosen_rule"]
    heldout = summary["heldout"]
    print(
        "claim={claim} rule={rule} train_pos={train_pos} heldout_pos={held_pos} "
        "heldout_selected={held_sel} heldout_selected_pos={held_sel_pos} lift={lift} "
        "reconstructed={reconstructed} forms={forms} derivers={derivers} out={out}".format(
            claim=payload["claim_status"],
            rule=rule.get("name"),
            train_pos=(summary.get("train") or {}).get("positive_count"),
            held_pos=heldout.get("positive_count"),
            held_sel=heldout.get("selected_count"),
            held_sel_pos=heldout.get("selected_positive_count"),
            lift=heldout.get("precision_lift_over_prevalence"),
            reconstructed=summary.get("reconstructed_heldout_selected_count"),
            forms=summary.get("unique_form_count"),
            derivers=summary.get("secret_deriving_group_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
