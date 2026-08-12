#!/usr/bin/env python3
"""P1046 leave-one-public red-team for P1045 coordinate-residue rank gains."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1045_p231_yresidue_representation_change_rank_scout as p1045


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1046_p231_coordinate_residue_leaveone_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1046_p231_coordinate_residue_leaveone_redteam_probe.json"
DEFAULT_P1044_INPUT = p1045.DEFAULT_P1044_INPUT
DEFAULT_P1045_INPUT = p1045.DEFAULT_OUT
DEFAULT_INPUTS = p1045.DEFAULT_INPUTS
SCHEMA = "ecdlp.low_term_total2_p1046_p231_coordinate_residue_leaveone_redteam.v1"
ORDER = p1045.ORDER
FROZEN_MODEL_NAMES = ("public_x_mod_11", "public_y_mod_5")
SECONDARY_MODEL_NAMES = ("public_x_mod_5", "public_x_mod_7", "public_y_mod_7", "public_y_mod_11")
CONTROL_MODEL_NAMES = ("standard_index", "public_exact_index", "kummer_x_exact_index")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def short_model_result(result: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "name",
        "coefficient_rank",
        "augmented_rank",
        "consistent",
        "rank_gain_over_standard",
        "candidate_success",
        "heuristic_overlocal",
        "label_count",
        "reused_label_count",
        "singleton_label_count",
        "max_label_multiplicity",
        "residual_values",
    ]
    return {key: result.get(key) for key in keys}


def serializable_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def rows_from_records(records: list[dict[str, Any]], factor_count: int) -> list[dict[str, Any]]:
    unique_rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in records:
        if not record.get("toy_secret_verified"):
            continue
        if not record.get("residuals_agree_within_pair"):
            continue
        if (record.get("residuals") or [None])[0] != p1045.BASE_RESIDUAL:
            continue
        if tuple(tuple(item) for item in record.get("factor_signature") or []) != p1045.BASE_SIGNATURE:
            continue
        scalar = p1045.int_value(record.get("predicted_target")) % ORDER
        artifact = str(record.get("artifact") or "unknown_artifact")
        for side in ("left", "right"):
            form = record[side]
            residual = p1045.residual_for_form(form, scalar)
            key = p1045.form_key(form, factor_count, residual)
            if key not in unique_rows:
                unique_rows[key] = {
                    "artifacts": set(),
                    "form": form,
                    "pair_count": 0,
                    "residual": residual,
                    "scalar": scalar,
                }
            unique_rows[key]["artifacts"].add(artifact)
            unique_rows[key]["pair_count"] += 1
    rows = sorted(
        unique_rows.values(),
        key=lambda item: (
            p1045.p1036.form_window(item["form"]),
            p1045.public_key_value(item["form"]),
            p1045.q_coeff_value(item["form"]),
            p1045.int_value(item["form"].get("rhs")) % ORDER,
        ),
    )
    for ordinal, row in enumerate(rows):
        row["ordinal"] = ordinal
        row["primary_artifact"] = sorted(row["artifacts"])[0] if row["artifacts"] else "unknown_artifact"
    return rows


def label_entries(spec: dict[str, Any], row: dict[str, Any], factor_count: int) -> tuple[dict[str, int], list[str]]:
    form = row["form"]
    label_fn = spec["label_fn"]
    row_entries: dict[str, int] = defaultdict(int)
    labels = []
    for factor, coeff in p1045.form_signature(form, factor_count):
        label = p1045.json_key(label_fn(row["ordinal"], form, factor, coeff))
        row_entries[label] = (row_entries[label] + coeff) % ORDER
        labels.append(label)
    return dict(row_entries), labels


def label_index_for_rows(
    spec: dict[str, Any], rows: list[dict[str, Any]], factor_count: int
) -> tuple[dict[str, int], Counter[str]]:
    label_index: dict[str, int] = {}
    counter: Counter[str] = Counter()
    for row in rows:
        _entries, labels = label_entries(spec, row, factor_count)
        for label in labels:
            if label not in label_index:
                label_index[label] = len(label_index)
            counter[label] += 1
    return label_index, counter


def label_set_for_rows(spec: dict[str, Any], rows: list[dict[str, Any]], factor_count: int) -> set[str]:
    labels: set[str] = set()
    for row in rows:
        _entries, row_labels = label_entries(spec, row, factor_count)
        labels.update(row_labels)
    return labels


def matrix_for_rows(
    spec: dict[str, Any], rows: list[dict[str, Any]], factor_count: int, label_index: dict[str, int]
) -> tuple[list[list[int]], list[int]]:
    vectors = []
    rhs_values = []
    for row in rows:
        entries, _labels = label_entries(spec, row, factor_count)
        vector = [0] * len(label_index)
        for label, value in entries.items():
            if label in label_index:
                vector[label_index[label]] = value % ORDER
        vectors.append(vector)
        rhs_values.append(p1045.int_value(row["residual"]) % ORDER)
    return vectors, rhs_values


def rank_pair(vectors: list[list[int]], rhs_values: list[int]) -> tuple[int, int]:
    augmented = [[*vector, rhs] for vector, rhs in zip(vectors, rhs_values)]
    return p1045.p1043.mod_rank(vectors, ORDER), p1045.p1043.mod_rank(augmented, ORDER)


def compact_fold_result(
    holdout_key: str,
    train_rows: list[dict[str, Any]],
    holdout_rows: list[dict[str, Any]],
    spec: dict[str, Any],
    factor_count: int,
    label_index: dict[str, int],
) -> dict[str, Any]:
    train_vectors, train_rhs = matrix_for_rows(spec, train_rows, factor_count, label_index)
    holdout_vectors, holdout_rhs = matrix_for_rows(spec, holdout_rows, factor_count, label_index)
    train_coeff, train_aug = rank_pair(train_vectors, train_rhs)
    holdout_coeff, holdout_aug = rank_pair(holdout_vectors, holdout_rhs)
    combined_coeff, combined_aug = rank_pair(train_vectors + holdout_vectors, train_rhs + holdout_rhs)
    train_labels = label_set_for_rows(spec, train_rows, factor_count)
    holdout_labels = label_set_for_rows(spec, holdout_rows, factor_count)
    unseen_labels = sorted(holdout_labels - train_labels)
    unseen_count = len(unseen_labels)
    combined_consistent = combined_coeff == combined_aug
    train_consistent = train_coeff == train_aug
    no_unseen_labels = unseen_count == 0
    coeff_rank_gain = combined_coeff - train_coeff
    aug_rank_gain = combined_aug - train_aug
    return {
        "aug_rank_gain": aug_rank_gain,
        "combined_augmented_rank": combined_aug,
        "combined_coefficient_rank": combined_coeff,
        "combined_consistent": combined_consistent,
        "coeff_rank_gain": coeff_rank_gain,
        "holdout_augmented_rank": holdout_aug,
        "holdout_coefficient_rank": holdout_coeff,
        "holdout_key": holdout_key,
        "holdout_publics": sorted({p1045.public_key_value(row["form"]) for row in holdout_rows}),
        "holdout_rows": len(holdout_rows),
        "no_unseen_labels": no_unseen_labels,
        "predictive_consistent": bool(no_unseen_labels and train_consistent and combined_consistent),
        "rowspace_closed": bool(no_unseen_labels and coeff_rank_gain == 0 and aug_rank_gain == 0),
        "train_augmented_rank": train_aug,
        "train_coefficient_rank": train_coeff,
        "train_consistent": train_consistent,
        "train_rows": len(train_rows),
        "unseen_label_count": unseen_count,
        "unseen_label_sample": unseen_labels[:8],
    }


def leave_one_analysis(
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    factor_count: int,
    group_name: str,
    key_fn,
) -> dict[str, Any]:
    label_index, label_counter = label_index_for_rows(spec, rows, factor_count)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(key_fn(row))].append(row)
    folds = []
    for key in sorted(groups):
        holdout_rows = groups[key]
        train_rows = [row for row in rows if row not in holdout_rows]
        folds.append(compact_fold_result(key, train_rows, holdout_rows, spec, factor_count, label_index))
    return {
        "folds": folds,
        "group_name": group_name,
        "label_count": len(label_index),
        "label_multiplicity_histogram": serializable_counter(Counter(label_counter.values())),
        "summary": {
            "all_combined_consistent": all(fold["combined_consistent"] for fold in folds),
            "all_train_consistent": all(fold["train_consistent"] for fold in folds),
            "fold_count": len(folds),
            "no_unseen_label_fold_count": sum(1 for fold in folds if fold["no_unseen_labels"]),
            "predictive_consistent_fold_count": sum(1 for fold in folds if fold["predictive_consistent"]),
            "rowspace_closed_fold_count": sum(1 for fold in folds if fold["rowspace_closed"]),
            "unseen_label_fold_count": sum(1 for fold in folds if not fold["no_unseen_labels"]),
        },
    }


def residue_model_parts(name: str) -> tuple[str, int]:
    parts = name.split("_")
    if len(parts) != 4 or parts[0] != "public" or parts[2] != "mod":
        raise ValueError(f"not a public coordinate residue model: {name}")
    return parts[1], int(parts[3])


def public_bucket_map(name: str, rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    axis, modulus = residue_model_parts(name)
    mapping: dict[str, Any] = {}
    conflicts = []
    for row in rows:
        form = row["form"]
        public = p1045.public_key_value(form)
        bucket = p1045.coord_residue(form, axis, modulus)
        if public in mapping and mapping[public] != bucket:
            conflicts.append({"first": mapping[public], "public_fingerprint": public, "second": bucket})
        mapping[public] = bucket
    return mapping, conflicts


def shuffled_spec(name: str, mapping: dict[str, Any], shuffle_index: int) -> dict[str, Any]:
    def label_fn(_ordinal: int, form: dict[str, Any], index: int, _coeff: int) -> tuple[Any, ...]:
        return (f"{name}_shuffle", mapping.get(p1045.public_key_value(form), "missing"), index)

    return {
        "description": f"Deterministic shuffle control {shuffle_index} for {name}.",
        "label_fn": label_fn,
        "name": f"{name}_shuffle_{shuffle_index:03d}",
        "overlocal_by_design": False,
        "public_feature": True,
    }


def shuffle_analysis(
    name: str,
    rows: list[dict[str, Any]],
    form_rows: list[dict[str, Any]],
    factor_count: int,
    standard_rank: int,
    compressed_false_count: int,
    observed: dict[str, Any],
    shuffle_count: int,
) -> dict[str, Any]:
    public_to_bucket, bucket_conflicts = public_bucket_map(name, rows)
    publics = sorted(public_to_bucket)
    original_buckets = [public_to_bucket[public] for public in publics]
    results = []
    for index in range(shuffle_count):
        shuffled_buckets = list(original_buckets)
        random.Random(stable_seed(f"{SCHEMA}:{name}:{index}")).shuffle(shuffled_buckets)
        mapping = dict(zip(publics, shuffled_buckets))
        spec = shuffled_spec(name, mapping, index)
        result = p1045.evaluate_model(spec, form_rows, factor_count, standard_rank, compressed_false_count)
        results.append(result)
    observed_rank = int(observed["coefficient_rank"])
    rank_ge_observed = [
        result
        for result in results
        if result["consistent"] and int(result["coefficient_rank"]) >= observed_rank
    ]
    rank_equal_observed = [
        result
        for result in results
        if result["consistent"] and int(result["coefficient_rank"]) == observed_rank
    ]
    candidate_like = [result for result in results if result["candidate_success"]]
    rank_hist = Counter(int(result["coefficient_rank"]) for result in results)
    aug_hist = Counter(int(result["augmented_rank"]) for result in results)
    return {
        "bucket_conflict_count": len(bucket_conflicts),
        "bucket_conflicts": bucket_conflicts[:8],
        "bucket_histogram": serializable_counter(Counter(original_buckets)),
        "candidate_like_count": len(candidate_like),
        "consistent_count": sum(1 for result in results if result["consistent"]),
        "observed_coefficient_rank": observed_rank,
        "rank_equal_observed_count": len(rank_equal_observed),
        "rank_ge_observed_count": len(rank_ge_observed),
        "rank_ge_observed_fraction": len(rank_ge_observed) / shuffle_count if shuffle_count else 0.0,
        "rank_histogram": serializable_counter(rank_hist),
        "augmented_rank_histogram": serializable_counter(aug_hist),
        "sample_candidate_like": [short_model_result(result) for result in candidate_like[:5]],
        "shuffle_count": shuffle_count,
    }


def strict_validation_pass(
    full_model: dict[str, Any],
    leave_public: dict[str, Any],
    shuffle: dict[str, Any],
    compressed_false_count: int,
) -> bool:
    summary = leave_public["summary"]
    return bool(
        full_model["rank_gain_over_standard"]
        and full_model["consistent"]
        and compressed_false_count == 0
        and summary["fold_count"] > 0
        and summary["no_unseen_label_fold_count"] == summary["fold_count"]
        and summary["predictive_consistent_fold_count"] == summary["fold_count"]
        and shuffle["rank_ge_observed_count"] == 0
    )


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    compressed_records, p1045_form_rows, meta = p1045.load_artifact_records(input_paths)
    factor_count = p1045.int_value(meta["factor_count"])
    rows = rows_from_records(compressed_records, factor_count)
    p1044_payload = json.loads(Path(args.p1044_input).read_text(encoding="utf-8"))
    p1045_payload = json.loads(Path(args.p1045_input).read_text(encoding="utf-8")) if Path(args.p1045_input).exists() else {}
    p1044_summary = p1044_payload.get("summary") or {}
    compressed_false_count = p1045.int_value(p1044_summary.get("compressed_false_count"))
    compressed_true_count = p1045.int_value(p1044_summary.get("compressed_true_count"))
    compressed_prediction_count = p1045.int_value(p1044_summary.get("compressed_prediction_count"))
    specs = {spec["name"]: spec for spec in p1045.label_model_specs(factor_count)}
    standard = p1045.evaluate_model(specs["standard_index"], p1045_form_rows, factor_count, 0, compressed_false_count)
    standard_rank = int(standard["coefficient_rank"])
    controls = {
        name: short_model_result(p1045.evaluate_model(specs[name], p1045_form_rows, factor_count, standard_rank, compressed_false_count))
        for name in CONTROL_MODEL_NAMES
    }

    model_results = []
    for name in [*FROZEN_MODEL_NAMES, *SECONDARY_MODEL_NAMES]:
        spec = specs[name]
        full_model = p1045.evaluate_model(spec, p1045_form_rows, factor_count, standard_rank, compressed_false_count)
        leave_public = leave_one_analysis(
            spec,
            rows,
            factor_count,
            "public_fingerprint",
            lambda row: p1045.public_key_value(row["form"]),
        )
        leave_artifact = leave_one_analysis(
            spec,
            rows,
            factor_count,
            "primary_artifact",
            lambda row: row["primary_artifact"],
        )
        shuffle = shuffle_analysis(
            name,
            rows,
            p1045_form_rows,
            factor_count,
            standard_rank,
            compressed_false_count,
            full_model,
            args.shuffles,
        )
        model_results.append(
            {
                "artifact_holdout": leave_artifact,
                "full_model": short_model_result(full_model),
                "leave_one_public": leave_public,
                "name": name,
                "shuffle_control": shuffle,
                "strict_validation_pass": strict_validation_pass(
                    full_model, leave_public, shuffle, compressed_false_count
                ),
            }
        )

    strict_passes = [result for result in model_results if result["strict_validation_pass"]]
    frozen_partial_support = [
        result
        for result in model_results
        if result["name"] in FROZEN_MODEL_NAMES
        and result["leave_one_public"]["summary"]["predictive_consistent_fold_count"] > 0
    ]
    if strict_passes:
        claim = "P1046_COORDINATE_RESIDUE_LEAVEONE_VALIDATION_SIGNAL"
        taxonomy = "OBSERVATION"
    elif frozen_partial_support:
        claim = "NEGATIVE_RESULT_P1046_COORDINATE_RESIDUE_NOT_STRICTLY_VALIDATED"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1046_COORDINATE_RESIDUE_FAILS_LEAVEONE_VALIDATION"
        taxonomy = "NEGATIVE RESULT"

    public_histograms = {}
    for name in [*FROZEN_MODEL_NAMES, *SECONDARY_MODEL_NAMES]:
        mapping, conflicts = public_bucket_map(name, rows)
        public_histograms[name] = {
            "bucket_conflict_count": len(conflicts),
            "bucket_histogram": serializable_counter(Counter(mapping.values())),
            "public_count": len(mapping),
        }

    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1044_input": str(args.p1044_input),
            "p1045_input": str(args.p1045_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1044_input_sha256": p1005.sha256_file(Path(args.p1044_input)),
            "p1045_input_sha256": p1005.sha256_file(Path(args.p1045_input)) if Path(args.p1045_input).exists() else None,
            "script_sha256": p1005.sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "controls": controls,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 artifacts only.",
            "RED-TEAM: this validates or narrows P1045; it does not close the coordinate-residue route.",
            "STRICT-VALIDATION: every held-out public must use labels seen in training and shuffles must not match observed rank.",
            "BUCKET-SHUFFLE: controls preserve residue multiplicities but intentionally destroy coordinate/public alignment.",
            "NO-FRESH-MATERIALIZATION: rank rows come from persisted strict witness artifacts; P1044 supplies the false-positive guard.",
            "INDEX-CALCULUS PRECURSOR: even a positive result would not be sparse linear algebra closure or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target ECDLP scalar-search baseline.",
        ],
        "model_results": model_results,
        "parameters": {
            "base_residual": p1045.BASE_RESIDUAL,
            "base_signature": [list(item) for item in p1045.BASE_SIGNATURE],
            "factor_count": factor_count,
            "frozen_models": list(FROZEN_MODEL_NAMES),
            "modulus": ORDER,
            "secondary_models": list(SECONDARY_MODEL_NAMES),
            "shuffle_count": args.shuffles,
        },
        "p1044_broad_guard_summary": p1044_summary,
        "p1045_claim_status": p1045_payload.get("claim_status"),
        "public_bucket_summaries": public_histograms,
        "rank_input_summary": {
            **meta,
            "artifact_count": len({row["primary_artifact"] for row in rows}),
            "unique_form_count": len(rows),
            "unique_public_count": len({p1045.public_key_value(row["form"]) for row in rows}),
        },
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "frozen_partial_support_count": len(frozen_partial_support),
            "strict_validation_pass_count": len(strict_passes),
            "strict_validation_pass_models": [result["name"] for result in strict_passes],
            "tested_model_count": len(model_results),
            "unique_form_count": len(rows),
            "unique_public_count": len({p1045.public_key_value(row["form"]) for row in rows}),
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated persisted strict witness probe paths for rank rows",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1044-input", default=str(DEFAULT_P1044_INPUT), help="P1044 broad all-pool guard probe path")
    parser.add_argument("--p1045-input", default=str(DEFAULT_P1045_INPUT), help="P1045 probe path")
    parser.add_argument("--shuffles", type=int, default=64, help="Deterministic residue-bucket shuffle count")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} models={models} strict_pass={strict} partial={partial} forms={forms} publics={publics} compressed_false={false} out={out}".format(
            claim=payload["claim_status"],
            models=summary["tested_model_count"],
            strict=summary["strict_validation_pass_count"],
            partial=summary["frozen_partial_support_count"],
            forms=summary["unique_form_count"],
            publics=summary["unique_public_count"],
            false=summary["compressed_false_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
