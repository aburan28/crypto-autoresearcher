#!/usr/bin/env python3
"""P1048 coefficient-transform representation audit after P1047 bucket failure."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1045_p231_yresidue_representation_change_rank_scout as p1045
import low_term_total2_p1047_p231_fresh_row_representation_validation as p1047


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1048_p231_coefficient_transform_representation_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1048_p231_coefficient_transform_representation_audit_probe.json"
DEFAULT_P1047_INPUT = STATE_DIR / "low_term_total2_p1047_p231_fresh_row_representation_validation_probe.json"
DEFAULT_INPUTS = p1045.DEFAULT_INPUTS
SCHEMA = "ecdlp.low_term_total2_p1048_p231_coefficient_transform_representation_audit.v1"
ORDER = p1045.ORDER
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 64
DEFAULT_SHUFFLES = 64

FeatureFn = Callable[[dict[str, Any]], int]
WeightFn = Callable[[dict[str, Any], int, int], int]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def int_feature(value: int | None, default: int = 0) -> int:
    return default if value is None else value % ORDER


def inv_or_zero(value: int) -> int:
    value %= ORDER
    if value == 0:
        return 0
    return pow(value, ORDER - 2, ORDER)


def public_xy(form: dict[str, Any]) -> tuple[int, int] | tuple[()]:
    coords = p1045.public_coords(form)
    if len(coords) < 2:
        return ()
    return coords


def feature_x(form: dict[str, Any]) -> int:
    coords = public_xy(form)
    return 0 if not coords else coords[0] % ORDER


def feature_y(form: dict[str, Any]) -> int:
    coords = public_xy(form)
    return 0 if not coords else coords[1] % ORDER


def feature_x_mod_11(form: dict[str, Any]) -> int:
    return feature_x(form) % 11


def feature_y_mod_5(form: dict[str, Any]) -> int:
    return feature_y(form) % 5


def feature_y_over_x(form: dict[str, Any]) -> int:
    x = feature_x(form)
    y = feature_y(form)
    return (y * inv_or_zero(x)) % ORDER


def feature_y_over_x_plus_1(form: dict[str, Any]) -> int:
    x = feature_x(form)
    y = feature_y(form)
    return (y * inv_or_zero(x + 1)) % ORDER


def feature_kummer_x_plus_inv(form: dict[str, Any]) -> int:
    x = feature_x(form)
    return (x + inv_or_zero(x)) % ORDER


def feature_trace_sum(form: dict[str, Any]) -> int:
    return (feature_x(form) + feature_y(form)) % ORDER


def feature_norm_product(form: dict[str, Any]) -> int:
    return (feature_x(form) * feature_y(form)) % ORDER


def feature_discriminant(form: dict[str, Any]) -> int:
    x = feature_x(form)
    y = feature_y(form)
    return (x * x - 4 * y) % ORDER


def feature_specs() -> list[dict[str, Any]]:
    return [
        {"name": "x_full", "fn": feature_x},
        {"name": "y_full", "fn": feature_y},
        {"name": "x_mod_11", "fn": feature_x_mod_11},
        {"name": "y_mod_5", "fn": feature_y_mod_5},
        {"name": "y_over_x", "fn": feature_y_over_x},
        {"name": "y_over_x_plus_1", "fn": feature_y_over_x_plus_1},
        {"name": "kummer_x_plus_inv", "fn": feature_kummer_x_plus_inv},
        {"name": "trace_sum", "fn": feature_trace_sum},
        {"name": "norm_product", "fn": feature_norm_product},
        {"name": "disc_x2_minus_4y", "fn": feature_discriminant},
    ]


def make_weight_fn(feature_fn: FeatureFn, mode: str) -> WeightFn:
    def feature(form: dict[str, Any]) -> int:
        return feature_fn(form) % ORDER

    if mode == "factor_delta_linear":
        return lambda form, factor, _coeff: (1 + ((factor - 8) % ORDER) * feature(form)) % ORDER
    if mode == "factor_index_linear":
        return lambda form, factor, _coeff: (1 + (factor % ORDER) * feature(form)) % ORDER
    if mode == "left_feature_right_one":
        return lambda form, factor, _coeff: feature(form) if factor == 8 else 1
    if mode == "left_one_right_feature":
        return lambda form, factor, _coeff: 1 if factor == 8 else feature(form)
    if mode == "signed_factor_delta":
        return lambda form, factor, _coeff: (1 - feature(form)) % ORDER if factor == 8 else (1 + feature(form)) % ORDER
    raise ValueError(f"unknown transform mode: {mode}")


def transform_specs() -> list[dict[str, Any]]:
    modes = [
        ("factor_delta_linear", "multiplier 1 + (factor-8)*feature"),
        ("factor_index_linear", "multiplier 1 + factor*feature"),
        ("left_feature_right_one", "feature on factor 8, identity on factor 11"),
        ("left_one_right_feature", "identity on factor 8, feature on factor 11"),
        ("signed_factor_delta", "1-feature on factor 8, 1+feature on factor 11"),
    ]
    specs = []
    for feature in feature_specs():
        for mode, description in modes:
            name = f"{feature['name']}__{mode}"
            specs.append(
                {
                    "description": f"{feature['name']} coefficient transform: {description}.",
                    "feature_fn": feature["fn"],
                    "feature_name": feature["name"],
                    "mode": mode,
                    "name": name,
                    "weight_fn": make_weight_fn(feature["fn"], mode),
                }
            )
    return specs


def standard_spec() -> dict[str, Any]:
    return {
        "description": "Standard global factor-index coefficients.",
        "feature_fn": lambda _form: 0,
        "feature_name": "standard",
        "mode": "standard",
        "name": "standard_index",
        "weight_fn": lambda _form, _factor, _coeff: 1,
    }


def serializable_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def label_index_for_rows(rows: list[dict[str, Any]], factor_count: int) -> dict[int, int]:
    labels = sorted(
        {
            factor
            for row in rows
            for factor, _coeff in p1045.form_signature(row["form"], factor_count)
        }
    )
    return {factor: offset for offset, factor in enumerate(labels)}


def matrix_for_rows(
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    factor_count: int,
    label_index: dict[int, int],
) -> tuple[list[list[int]], list[int]]:
    weight_fn: WeightFn = spec["weight_fn"]
    vectors = []
    rhs_values = []
    for row in rows:
        vector = [0] * len(label_index)
        for factor, coeff in p1045.form_signature(row["form"], factor_count):
            transformed = (coeff % ORDER) * (weight_fn(row["form"], factor, coeff) % ORDER)
            vector[label_index[factor]] = (vector[label_index[factor]] + transformed) % ORDER
        vectors.append(vector)
        rhs_values.append(p1045.int_value(row["residual"]) % ORDER)
    return vectors, rhs_values


def rank_pair(vectors: list[list[int]], rhs_values: list[int]) -> tuple[int, int]:
    augmented = [[*vector, rhs] for vector, rhs in zip(vectors, rhs_values)]
    return p1045.p1043.mod_rank(vectors, ORDER), p1045.p1043.mod_rank(augmented, ORDER)


def feature_histogram(spec: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, int]:
    feature_fn: FeatureFn = spec["feature_fn"]
    return serializable_counter(Counter(feature_fn(row["form"]) % ORDER for row in rows))


def summarize_model(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    factor_count: int,
    standard_train_rank: int,
    compressed_false_count: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    label_index = label_index_for_rows(all_rows, factor_count)
    train_vectors, train_rhs = matrix_for_rows(spec, train_rows, factor_count, label_index)
    validation_vectors, validation_rhs = matrix_for_rows(spec, validation_rows, factor_count, label_index)
    train_coeff, train_aug = rank_pair(train_vectors, train_rhs)
    validation_coeff, validation_aug = rank_pair(validation_vectors, validation_rhs)
    combined_coeff, combined_aug = rank_pair(train_vectors + validation_vectors, train_rhs + validation_rhs)
    heldout_success = bool(
        validation_rows
        and train_coeff > standard_train_rank
        and train_coeff == train_aug
        and combined_coeff == combined_aug
        and compressed_false_count == 0
    )
    return {
        "combined_augmented_rank": combined_aug,
        "combined_coefficient_rank": combined_coeff,
        "combined_consistent": combined_coeff == combined_aug,
        "description": spec["description"],
        "feature_histogram": feature_histogram(spec, all_rows),
        "feature_name": spec["feature_name"],
        "heldout_success_predicate": heldout_success,
        "label_count": len(label_index),
        "labels": sorted(label_index),
        "mode": spec["mode"],
        "name": spec["name"],
        "rank_gain_over_standard_train": train_coeff > standard_train_rank,
        "train_augmented_rank": train_aug,
        "train_coefficient_rank": train_coeff,
        "train_consistent": train_coeff == train_aug,
        "train_rows": len(train_rows),
        "validation_augmented_rank": validation_aug,
        "validation_coefficient_rank": validation_coeff,
        "validation_consistent": validation_coeff == validation_aug,
        "validation_rows": len(validation_rows),
    }


def shuffled_spec(spec: dict[str, Any], public_to_feature: dict[str, int], shuffle_index: int) -> dict[str, Any]:
    mode = spec["mode"]

    def feature_fn(form: dict[str, Any]) -> int:
        return public_to_feature.get(p1045.public_key_value(form), 0) % ORDER

    return {
        "description": f"Deterministic public-feature shuffle {shuffle_index} for {spec['name']}.",
        "feature_fn": feature_fn,
        "feature_name": f"{spec['feature_name']}_shuffle",
        "mode": mode,
        "name": f"{spec['name']}__shuffle_{shuffle_index:03d}",
        "weight_fn": make_weight_fn(feature_fn, mode),
    }


def shuffle_analysis(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    factor_count: int,
    standard_train_rank: int,
    compressed_false_count: int,
    observed: dict[str, Any],
    shuffle_count: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    publics = sorted({p1045.public_key_value(row["form"]) for row in all_rows})
    feature_fn: FeatureFn = spec["feature_fn"]
    original_features = []
    for public in publics:
        form = next(row["form"] for row in all_rows if p1045.public_key_value(row["form"]) == public)
        original_features.append(feature_fn(form) % ORDER)
    results = []
    for index in range(shuffle_count):
        features = list(original_features)
        random.Random(stable_seed(f"{SCHEMA}:{spec['name']}:{index}")).shuffle(features)
        shuffled = shuffled_spec(spec, dict(zip(publics, features)), index)
        results.append(
            summarize_model(
                shuffled,
                train_rows,
                validation_rows,
                factor_count,
                standard_train_rank,
                compressed_false_count,
            )
        )
    observed_rank = int(observed["combined_coefficient_rank"])
    rank_ge = [
        result
        for result in results
        if result["combined_consistent"] and int(result["combined_coefficient_rank"]) >= observed_rank
    ]
    rank_equal = [
        result
        for result in results
        if result["combined_consistent"] and int(result["combined_coefficient_rank"]) == observed_rank
    ]
    success_like = [result for result in results if result["heldout_success_predicate"]]
    return {
        "rank_equal_observed_count": len(rank_equal),
        "rank_ge_observed_count": len(rank_ge),
        "rank_histogram": serializable_counter(Counter(result["combined_coefficient_rank"] for result in results)),
        "shuffle_count": shuffle_count,
        "success_like_count": len(success_like),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    strict_records, strict_form_rows, strict_meta = p1045.load_artifact_records(input_paths)
    broad_records, broad_meta = p1047.rematerialize_broad_pairs(args)
    factor_count = max(p1045.int_value(strict_meta["factor_count"]), p1045.int_value(broad_meta["factor_count"]))
    train_rows = p1047.rows_from_form_items(strict_form_rows, factor_count, "p1045_strict_train")
    train_ids = {row["identity"] for row in train_rows}
    broad_rows_all = p1047.rows_from_prediction_pairs(broad_records, factor_count, "p1048_broad_validation")
    validation_rows = [row for row in broad_rows_all if row["identity"] not in train_ids]
    p1047.assign_ordinals(train_rows + validation_rows)

    compressed_false_count = sum(1 for record in broad_records if not record["toy_secret_verified"])
    compressed_true_count = sum(1 for record in broad_records if record["toy_secret_verified"])
    compressed_prediction_count = len(broad_records)

    standard = summarize_model(
        standard_spec(),
        train_rows,
        validation_rows,
        factor_count,
        0,
        compressed_false_count,
    )
    standard_train_rank = standard["train_coefficient_rank"]
    model_results = []
    for spec in transform_specs():
        observed = summarize_model(
            spec,
            train_rows,
            validation_rows,
            factor_count,
            standard_train_rank,
            compressed_false_count,
        )
        shuffles = shuffle_analysis(
            spec,
            train_rows,
            validation_rows,
            factor_count,
            standard_train_rank,
            compressed_false_count,
            observed,
            args.shuffles,
        )
        strict_pass = bool(observed["heldout_success_predicate"] and shuffles["rank_ge_observed_count"] == 0)
        model_results.append(
            {
                "model": observed,
                "shuffle_control": shuffles,
                "strict_validation_pass": strict_pass,
            }
        )
    model_results.sort(
        key=lambda item: (
            not item["strict_validation_pass"],
            not item["model"]["heldout_success_predicate"],
            item["shuffle_control"]["rank_ge_observed_count"],
            -item["model"]["train_coefficient_rank"],
            item["model"]["name"],
        )
    )

    strict_passes = [item for item in model_results if item["strict_validation_pass"]]
    heldout_candidates = [item for item in model_results if item["model"]["heldout_success_predicate"]]
    rank_gain_models = [item for item in model_results if item["model"]["rank_gain_over_standard_train"]]
    train_consistent_rank_gain = [
        item
        for item in model_results
        if item["model"]["rank_gain_over_standard_train"] and item["model"]["train_consistent"]
    ]
    if strict_passes:
        claim = "P1048_COEFFICIENT_TRANSFORM_REPRESENTATION_SIGNAL"
        taxonomy = "OBSERVATION"
    elif heldout_candidates:
        claim = "NEGATIVE_RESULT_P1048_COEFFICIENT_TRANSFORMS_FAIL_SHUFFLE_SEPARATION"
        taxonomy = "NEGATIVE RESULT"
    elif train_consistent_rank_gain:
        claim = "NEGATIVE_RESULT_P1048_TRAIN_SIGNALS_FAIL_VALIDATION"
        taxonomy = "NEGATIVE RESULT"
    elif rank_gain_models:
        claim = "NEGATIVE_RESULT_P1048_RANK_GAINS_ARE_AUGMENTED_INCONSISTENT"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1048_NO_COEFFICIENT_TRANSFORM_RANK_GAIN"
        taxonomy = "NEGATIVE RESULT"

    p1047_payload = json.loads(Path(args.p1047_input).read_text(encoding="utf-8")) if Path(args.p1047_input).exists() else {}
    windows = broad_meta["windows"]
    source_hashes = {
        window: p1005.sha256_file(p1047.p1044.p1007.expanded_source_path(window))
        for window in windows
        if p1047.p1044.p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1047_input": str(args.p1047_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1047_input_sha256": p1005.sha256_file(Path(args.p1047_input)) if Path(args.p1047_input).exists() else None,
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "COEFFICIENT-TRANSFORM: global factor labels are fixed; only row coefficients are transformed by public functions.",
            "REPRESENTATION-CATALOG: tested transforms are candidate coordinate maps, not proven factor-base homomorphisms.",
            "FRESH-ROW-SPLIT: validation rows exclude P1045 strict train form identities.",
            "SHUFFLE-REDTEAM: public-feature shuffles test whether rank behavior is only feature multiplicity.",
            "INDEX-CALCULUS PRECURSOR: a pass would still require relation collection, sparse linear algebra, and target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "model_results": model_results,
        "parameters": {
            "base_residual": p1045.BASE_RESIDUAL,
            "base_signature": [list(item) for item in p1045.BASE_SIGNATURE],
            "factor_count": factor_count,
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "modulus": ORDER,
            "shuffle_count": args.shuffles,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "windows": windows,
        },
        "p1047_claim_status": p1047_payload.get("claim_status"),
        "rematerialized_broad_summary": {
            "all_base_rows": len(broad_rows_all),
            "broad_only_validation_rows": len(validation_rows),
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "forward_exists_count": sum(1 for value in broad_meta["forward_exists"].values() if value),
            "pool_summaries": broad_meta["pool_summaries"],
            "unique_broad_public_count": len({p1045.public_key_value(row["form"]) for row in broad_rows_all}),
            "unique_validation_public_count": len({p1045.public_key_value(row["form"]) for row in validation_rows}),
        },
        "schema": SCHEMA,
        "standard_control": standard,
        "strict_train_summary": {
            "input_paths": [str(path) for path in input_paths],
            "strict_pair_count": len(strict_records),
            "train_rows": len(train_rows),
            "unique_train_public_count": len({p1045.public_key_value(row["form"]) for row in train_rows}),
        },
        "summary": {
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "heldout_candidate_count": len(heldout_candidates),
            "rank_gain_model_count": len(rank_gain_models),
            "strict_validation_pass_count": len(strict_passes),
            "strict_validation_pass_models": [item["model"]["name"] for item in strict_passes],
            "tested_model_count": len(model_results),
            "train_consistent_rank_gain_count": len(train_consistent_rank_gain),
            "train_rows": len(train_rows),
            "validation_rows": len(validation_rows),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated persisted strict witness probe paths for train rows",
    )
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Rematerialization window count")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1047-input", default=str(DEFAULT_P1047_INPUT), help="P1047 fresh-row probe path")
    parser.add_argument("--shuffles", type=int, default=DEFAULT_SHUFFLES, help="Deterministic public-feature shuffle count")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to rematerialize")
    parser.add_argument("--targets", default=p1047.p1044.p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} train_rows={train} validation_rows={validation} compressed_pred={pred} compressed_false={false} rank_gain={rank_gain} train_consistent_rank_gain={consistent} heldout_candidates={heldout} strict_pass={passes} out={out}".format(
            claim=payload["claim_status"],
            train=summary["train_rows"],
            validation=summary["validation_rows"],
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            rank_gain=summary["rank_gain_model_count"],
            consistent=summary["train_consistent_rank_gain_count"],
            heldout=summary["heldout_candidate_count"],
            passes=summary["strict_validation_pass_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
