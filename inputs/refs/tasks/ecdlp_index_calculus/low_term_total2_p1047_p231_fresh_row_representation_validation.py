#!/usr/bin/env python3
"""P1047 fresh-row representation validation after the P1046 bucket artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1038_p231_guarded_structural_family_supply_search as p1038
import low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout as p1044
import low_term_total2_p1045_p231_yresidue_representation_change_rank_scout as p1045


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1047_p231_fresh_row_representation_validation.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1047_p231_fresh_row_representation_validation_probe.json"
DEFAULT_P1046_INPUT = STATE_DIR / "low_term_total2_p1046_p231_coordinate_residue_leaveone_redteam_probe.json"
DEFAULT_INPUTS = p1045.DEFAULT_INPUTS
SCHEMA = "ecdlp.low_term_total2_p1047_p231_fresh_row_representation_validation.v1"
ORDER = p1045.ORDER
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 16
DEFAULT_SHUFFLES = 64

BucketFn = Callable[[dict[str, Any]], Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_seed(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def serializable_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(counter.items(), key=lambda item: str(item[0]))}


def public_xy(form: dict[str, Any]) -> tuple[int, int] | tuple[()]:
    coords = p1045.public_coords(form)
    if len(coords) < 2:
        return ()
    return coords


def inv_or_none(value: int) -> int | None:
    value %= ORDER
    if value == 0:
        return None
    return pow(value, ORDER - 2, ORDER)


def coord_value(form: dict[str, Any], axis: str) -> int | None:
    coords = public_xy(form)
    if not coords:
        return None
    x, y = coords
    return x if axis == "x" else y


def bucket_coord(axis: str, modulus: int) -> BucketFn:
    return lambda form: p1045.coord_residue(form, axis, modulus)


def bucket_xy_pair(modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        coords = public_xy(form)
        if not coords:
            return "missing"
        x, y = coords
        return (x % modulus, y % modulus)

    return bucket


def bucket_sum(modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        coords = public_xy(form)
        if not coords:
            return "missing"
        x, y = coords
        return (x + y) % modulus

    return bucket


def bucket_product(modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        coords = public_xy(form)
        if not coords:
            return "missing"
        x, y = coords
        return (x * y) % modulus

    return bucket


def bucket_discriminant(modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        coords = public_xy(form)
        if not coords:
            return "missing"
        x, y = coords
        return (x * x - 4 * y) % modulus

    return bucket


def bucket_rational_y_over_x_plus(shift: int, modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        coords = public_xy(form)
        if not coords:
            return "missing"
        x, y = coords
        inv = inv_or_none(x + shift)
        if inv is None:
            return "pole"
        return (y * inv) % ORDER % modulus

    return bucket


def bucket_kummer_x_symmetric(modulus: int) -> BucketFn:
    def bucket(form: dict[str, Any]) -> Any:
        x = coord_value(form, "x")
        if x is None:
            return "missing"
        inv = inv_or_none(x)
        if inv is None:
            return "pole"
        return (x + inv) % ORDER % modulus

    return bucket


def make_bucket_spec(name: str, description: str, bucket_fn: BucketFn) -> dict[str, Any]:
    def label_fn(_ordinal: int, form: dict[str, Any], index: int, _coeff: int) -> tuple[Any, ...]:
        return (name, bucket_fn(form), index)

    return {
        "bucket_fn": bucket_fn,
        "description": description,
        "label_fn": label_fn,
        "name": name,
        "overlocal_by_design": False,
        "public_feature": True,
    }


def representation_specs() -> list[dict[str, Any]]:
    return [
        make_bucket_spec("public_x_mod_11", "P1045 frozen x-coordinate residue modulo 11.", bucket_coord("x", 11)),
        make_bucket_spec("public_y_mod_5", "P1045 frozen y-coordinate residue modulo 5.", bucket_coord("y", 5)),
        make_bucket_spec("public_x_mod_7", "Secondary x-coordinate residue modulo 7.", bucket_coord("x", 7)),
        make_bucket_spec("public_y_mod_7", "Secondary y-coordinate residue modulo 7.", bucket_coord("y", 7)),
        make_bucket_spec("public_xy_pair_mod_5", "Coordinate-pair bucket modulo 5.", bucket_xy_pair(5)),
        make_bucket_spec("public_xy_pair_mod_7", "Coordinate-pair bucket modulo 7.", bucket_xy_pair(7)),
        make_bucket_spec("rational_y_over_x_mod_7", "Rational-map bucket y/x modulo 7.", bucket_rational_y_over_x_plus(0, 7)),
        make_bucket_spec("rational_y_over_x_plus_1_mod_7", "Rational-map bucket y/(x+1) modulo 7.", bucket_rational_y_over_x_plus(1, 7)),
        make_bucket_spec("kummer_x_plus_inv_mod_7", "Kummer-inspired x + 1/x bucket modulo 7.", bucket_kummer_x_symmetric(7)),
        make_bucket_spec("trace_sum_mod_7", "Trace-like public x+y bucket modulo 7.", bucket_sum(7)),
        make_bucket_spec("norm_product_mod_7", "Norm-like public x*y bucket modulo 7.", bucket_product(7)),
        make_bucket_spec("disc_x2_minus_4y_mod_7", "Discriminant-like x^2-4y bucket modulo 7.", bucket_discriminant(7)),
    ]


def prediction_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record["window"],
        record["public_fingerprint"],
        tuple(record["family_terms"]),
        tuple(record["family_tail"]),
        tuple(record["q_pair"]),
        tuple(record["rhs_pair"]),
        record["predicted_target"],
        tuple(tuple(item) for item in record["factor_signature"]),
    )


def collect_prediction_pairs(
    forms: list[dict[str, Any]],
    factor_count: int,
    windows: list[str],
    pool_name: str,
) -> list[dict[str, Any]]:
    window_set = set(windows)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        if p1044.p1036.form_window(form) not in window_set or not p1044.passes_p1044_filter(form):
            continue
        for spec in p1044.p1036.object_specs():
            key = (
                p1045.public_key_value(form),
                p1044.p1036.form_window(form),
                p1045.json_key((spec["name"], spec["key_fn"](form))),
            )
            grouped[key].append(form)

    records_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for (_public, _window, _object_key), group in grouped.items():
        if len({p1045.q_coeff_value(form) for form in group}) < 2:
            continue
        for left_offset, left in enumerate(group):
            for right in group[left_offset + 1 :]:
                predicted = p1044.p1033.derive_target_from_pair(left, right, factor_count)
                if predicted is None:
                    continue
                source_secrets = sorted(
                    {
                        p1045.int_value(value) % ORDER
                        for value in (left.get("source_secret"), right.get("source_secret"))
                        if value is not None
                    }
                )
                verified = bool(source_secrets and all(predicted == secret for secret in source_secrets))
                residuals = [p1045.residual_for_form(left, predicted), p1045.residual_for_form(right, predicted)]
                signature = p1045.form_signature(left, factor_count)
                record = {
                    "factor_signature": [list(item) for item in signature],
                    "family_tail": list(p1045.tail_support_tuple_value(left)),
                    "family_terms": list(p1045.terms_tuple_value(left)),
                    "left": left,
                    "pools": {pool_name},
                    "predicted_target": predicted,
                    "public_fingerprint": p1045.public_key_value(left),
                    "q_pair": sorted([p1045.q_coeff_value(left), p1045.q_coeff_value(right)]),
                    "residuals": residuals,
                    "residuals_agree_within_pair": len(set(residuals)) == 1,
                    "rhs_pair": sorted([p1045.int_value(left.get("rhs")) % ORDER, p1045.int_value(right.get("rhs")) % ORDER]),
                    "right": right,
                    "source_secrets": source_secrets,
                    "toy_secret_verified": verified,
                    "window": p1044.p1036.form_window(left),
                }
                key = prediction_key(record)
                if key in records_by_key:
                    records_by_key[key]["pools"].add(pool_name)
                else:
                    records_by_key[key] = record
    return sorted(records_by_key.values(), key=lambda item: (item["window"], item["public_fingerprint"], item["q_pair"]))


def rematerialize_broad_pairs(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    windows = p1038.discover_forward_windows(args.start_window, args.max_windows)
    forward_by_window, forward_exists = p1035.load_rows(windows, args.targets, args.min_source_rank)
    all_records: dict[tuple[Any, ...], dict[str, Any]] = {}
    pool_summaries = []
    max_factor_count = 0
    for pool in p1035.pool_specs():
        forms, meta = p1044.reconstruct_by_window(forward_by_window, windows, pool["predicate"], True)
        factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0])
        max_factor_count = max(max_factor_count, factor_count)
        records = collect_prediction_pairs(forms, factor_count, windows, pool["name"])
        for record in records:
            key = prediction_key(record)
            if key in all_records:
                all_records[key]["pools"].update(record["pools"])
            else:
                all_records[key] = record
        pool_summaries.append(
            {
                "compressed": True,
                "false_count": sum(1 for record in records if not record["toy_secret_verified"]),
                "form_count": len(forms),
                "meta": meta,
                "name": pool["name"],
                "prediction_count": len(records),
                "true_count": sum(1 for record in records if record["toy_secret_verified"]),
            }
        )
    records = sorted(all_records.values(), key=lambda item: (item["window"], item["public_fingerprint"], item["q_pair"]))
    return records, {
        "factor_count": max_factor_count,
        "forward_exists": forward_exists,
        "pool_summaries": pool_summaries,
        "windows": windows,
    }


def rows_from_form_items(form_rows: list[dict[str, Any]], factor_count: int, source: str) -> list[dict[str, Any]]:
    rows = []
    for item in form_rows:
        form = item["form"]
        residual = p1045.int_value(item["residual"]) % ORDER
        key = p1045.form_key(form, factor_count, residual)
        rows.append(
            {
                "form": form,
                "identity": p1045.json_key(key),
                "residual": residual,
                "scalar": p1045.int_value(item.get("scalar")) % ORDER,
                "source": source,
            }
        )
    return rows


def rows_from_prediction_pairs(records: list[dict[str, Any]], factor_count: int, source: str) -> list[dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for record in records:
        if not record["toy_secret_verified"] or not record["residuals_agree_within_pair"]:
            continue
        if not record.get("residuals") or record["residuals"][0] != p1045.BASE_RESIDUAL:
            continue
        if tuple(tuple(item) for item in record["factor_signature"]) != p1045.BASE_SIGNATURE:
            continue
        scalar = p1045.int_value(record["predicted_target"]) % ORDER
        for side in ("left", "right"):
            form = record[side]
            residual = p1045.residual_for_form(form, scalar)
            key = p1045.form_key(form, factor_count, residual)
            identity = p1045.json_key(key)
            if identity not in unique:
                unique[identity] = {
                    "form": form,
                    "identity": identity,
                    "pair_count": 0,
                    "pools": set(),
                    "residual": residual,
                    "scalar": scalar,
                    "source": source,
                    "windows": set(),
                }
            unique[identity]["pair_count"] += 1
            unique[identity]["pools"].update(record["pools"])
            unique[identity]["windows"].add(record["window"])
    rows = sorted(
        unique.values(),
        key=lambda item: (
            p1044.p1036.form_window(item["form"]),
            p1045.public_key_value(item["form"]),
            p1045.q_coeff_value(item["form"]),
            p1045.int_value(item["form"].get("rhs")) % ORDER,
        ),
    )
    for row in rows:
        row["pools"] = sorted(row["pools"])
        row["windows"] = sorted(row["windows"])
    return rows


def assign_ordinals(rows: list[dict[str, Any]]) -> None:
    for ordinal, row in enumerate(rows):
        row["ordinal"] = ordinal


def label_entries(spec: dict[str, Any], row: dict[str, Any], factor_count: int) -> tuple[dict[str, int], set[str]]:
    entries: dict[str, int] = defaultdict(int)
    labels: set[str] = set()
    label_fn = spec["label_fn"]
    for factor, coeff in p1045.form_signature(row["form"], factor_count):
        label = p1045.json_key(label_fn(row["ordinal"], row["form"], factor, coeff))
        entries[label] = (entries[label] + coeff) % ORDER
        labels.add(label)
    return dict(entries), labels


def build_label_index(spec: dict[str, Any], rows: list[dict[str, Any]], factor_count: int) -> tuple[dict[str, int], Counter[str]]:
    label_index: dict[str, int] = {}
    label_counter: Counter[str] = Counter()
    for row in rows:
        _entries, labels = label_entries(spec, row, factor_count)
        for label in labels:
            if label not in label_index:
                label_index[label] = len(label_index)
            label_counter[label] += 1
    return label_index, label_counter


def matrix_for_rows(
    spec: dict[str, Any],
    rows: list[dict[str, Any]],
    factor_count: int,
    label_index: dict[str, int],
) -> tuple[list[list[int]], list[int], list[set[str]]]:
    vectors = []
    rhs_values = []
    label_sets = []
    for row in rows:
        entries, labels = label_entries(spec, row, factor_count)
        vector = [0] * len(label_index)
        for label, value in entries.items():
            if label in label_index:
                vector[label_index[label]] = value % ORDER
        vectors.append(vector)
        rhs_values.append(p1045.int_value(row["residual"]) % ORDER)
        label_sets.append(labels)
    return vectors, rhs_values, label_sets


def rank_pair(vectors: list[list[int]], rhs_values: list[int]) -> tuple[int, int]:
    augmented = [[*vector, rhs] for vector, rhs in zip(vectors, rhs_values)]
    return p1045.p1043.mod_rank(vectors, ORDER), p1045.p1043.mod_rank(augmented, ORDER)


def standard_spec() -> dict[str, Any]:
    return {
        "bucket_fn": lambda _form: "standard",
        "description": "Standard factor-index baseline.",
        "label_fn": lambda _ordinal, _form, index, _coeff: ("idx", index),
        "name": "standard_index",
        "overlocal_by_design": False,
        "public_feature": False,
    }


def summarize_split_model(
    spec: dict[str, Any],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    factor_count: int,
    standard_train_rank: int,
    compressed_false_count: int,
) -> dict[str, Any]:
    all_rows = train_rows + validation_rows
    label_index, label_counter = build_label_index(spec, all_rows, factor_count)
    train_vectors, train_rhs, train_label_sets = matrix_for_rows(spec, train_rows, factor_count, label_index)
    validation_vectors, validation_rhs, validation_label_sets = matrix_for_rows(spec, validation_rows, factor_count, label_index)
    train_coeff, train_aug = rank_pair(train_vectors, train_rhs)
    validation_coeff, validation_aug = rank_pair(validation_vectors, validation_rhs)
    combined_coeff, combined_aug = rank_pair(train_vectors + validation_vectors, train_rhs + validation_rhs)
    train_labels = set().union(*train_label_sets) if train_label_sets else set()
    no_unseen_rows = [labels <= train_labels for labels in validation_label_sets]
    validation_publics = sorted({p1045.public_key_value(row["form"]) for row in validation_rows})
    train_publics = sorted({p1045.public_key_value(row["form"]) for row in train_rows})
    heldout_success = bool(
        validation_rows
        and all(no_unseen_rows)
        and train_coeff > standard_train_rank
        and train_coeff == train_aug
        and combined_coeff == combined_aug
        and compressed_false_count == 0
    )
    return {
        "bucket_histogram": serializable_counter(Counter(spec.get("bucket_fn", lambda _form: "none")(row["form"]) for row in all_rows)),
        "combined_augmented_rank": combined_aug,
        "combined_coefficient_rank": combined_coeff,
        "combined_consistent": combined_coeff == combined_aug,
        "heldout_success_predicate": heldout_success,
        "label_count": len(label_index),
        "label_multiplicity_histogram": serializable_counter(Counter(label_counter.values())),
        "max_label_multiplicity": max(label_counter.values() or [0]),
        "name": spec["name"],
        "rank_gain_over_standard_train": train_coeff > standard_train_rank,
        "reused_label_count": sum(1 for value in label_counter.values() if value >= 2),
        "singleton_label_count": sum(1 for value in label_counter.values() if value == 1),
        "train_augmented_rank": train_aug,
        "train_coefficient_rank": train_coeff,
        "train_consistent": train_coeff == train_aug,
        "train_public_count": len(train_publics),
        "train_publics": train_publics,
        "train_rows": len(train_rows),
        "validation_augmented_rank": validation_aug,
        "validation_coefficient_rank": validation_coeff,
        "validation_consistent": validation_coeff == validation_aug,
        "validation_no_unseen_row_count": sum(1 for value in no_unseen_rows if value),
        "validation_public_count": len(validation_publics),
        "validation_publics": validation_publics,
        "validation_rows": len(validation_rows),
        "validation_unseen_row_count": sum(1 for value in no_unseen_rows if not value),
    }


def shuffled_spec(spec: dict[str, Any], public_to_bucket: dict[str, Any], shuffle_index: int) -> dict[str, Any]:
    name = spec["name"]

    def bucket_fn(form: dict[str, Any]) -> Any:
        return public_to_bucket.get(p1045.public_key_value(form), "missing")

    def label_fn(_ordinal: int, form: dict[str, Any], index: int, _coeff: int) -> tuple[Any, ...]:
        return (f"{name}_shuffle", bucket_fn(form), index)

    return {
        "bucket_fn": bucket_fn,
        "description": f"Deterministic public-bucket shuffle for {name}.",
        "label_fn": label_fn,
        "name": f"{name}_shuffle_{shuffle_index:03d}",
        "overlocal_by_design": False,
        "public_feature": True,
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
    original_buckets = [spec["bucket_fn"](next(row["form"] for row in all_rows if p1045.public_key_value(row["form"]) == public)) for public in publics]
    results = []
    for index in range(shuffle_count):
        buckets = list(original_buckets)
        random.Random(stable_seed(f"{SCHEMA}:{spec['name']}:{index}")).shuffle(buckets)
        shuffled = shuffled_spec(spec, dict(zip(publics, buckets)), index)
        results.append(
            summarize_split_model(
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
    broad_records, broad_meta = rematerialize_broad_pairs(args)
    factor_count = max(p1045.int_value(strict_meta["factor_count"]), p1045.int_value(broad_meta["factor_count"]))
    strict_rows = rows_from_form_items(strict_form_rows, factor_count, "p1045_strict_train")
    train_ids = {row["identity"] for row in strict_rows}
    broad_rows_all = rows_from_prediction_pairs(broad_records, factor_count, "p1047_broad_validation")
    validation_rows = [row for row in broad_rows_all if row["identity"] not in train_ids]
    assign_ordinals(strict_rows + validation_rows)

    compressed_false_count = sum(1 for record in broad_records if not record["toy_secret_verified"])
    compressed_true_count = sum(1 for record in broad_records if record["toy_secret_verified"])
    compressed_prediction_count = len(broad_records)

    standard = summarize_split_model(
        standard_spec(),
        strict_rows,
        validation_rows,
        factor_count,
        0,
        compressed_false_count,
    )
    standard_train_rank = standard["train_coefficient_rank"]
    model_results = []
    for spec in representation_specs():
        observed = summarize_split_model(
            spec,
            strict_rows,
            validation_rows,
            factor_count,
            standard_train_rank,
            compressed_false_count,
        )
        shuffles = shuffle_analysis(
            spec,
            strict_rows,
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
                "description": spec["description"],
                "model": observed,
                "shuffle_control": shuffles,
                "strict_validation_pass": strict_pass,
            }
        )

    strict_passes = [item for item in model_results if item["strict_validation_pass"]]
    heldout_candidate_count = sum(1 for item in model_results if item["model"]["heldout_success_predicate"])
    if strict_passes:
        claim = "P1047_FRESH_ROW_REPRESENTATION_VALIDATION_SIGNAL"
        taxonomy = "OBSERVATION"
    elif not validation_rows:
        claim = "NEGATIVE_RESULT_P1047_NO_BROAD_ONLY_VALIDATION_ROWS_UNDER_BOUND"
        taxonomy = "NEGATIVE RESULT"
    elif heldout_candidate_count:
        claim = "NEGATIVE_RESULT_P1047_HELDOUT_CANDIDATES_FAIL_SHUFFLE_SEPARATION"
        taxonomy = "NEGATIVE RESULT"
    else:
        claim = "NEGATIVE_RESULT_P1047_NO_HELDOUT_REPRESENTATION_TRANSFER"
        taxonomy = "NEGATIVE RESULT"

    p1046_payload = json.loads(Path(args.p1046_input).read_text(encoding="utf-8")) if Path(args.p1046_input).exists() else {}
    windows = broad_meta["windows"]
    source_hashes = {
        window: p1005.sha256_file(p1044.p1007.expanded_source_path(window))
        for window in windows
        if p1044.p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1046_input": str(args.p1046_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1046_input_sha256": p1005.sha256_file(Path(args.p1046_input)) if Path(args.p1046_input).exists() else None,
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "BOUNDED-REMATERIALIZATION: validation uses a capped window block and is not a full P1044 rerun.",
            "FRESH-ROW-SPLIT: validation rows exclude P1045 strict train form identities but may share the same broad source family.",
            "REPRESENTATION-CATALOG: rational, Kummer, trace, and norm labels are public bucket experiments, not proven algebraic maps.",
            "SHUFFLE-REDTEAM: public-bucket shuffles test whether rank behavior is only bucket multiplicity.",
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
        "p1046_claim_status": p1046_payload.get("claim_status"),
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
            "train_rows": len(strict_rows),
            "unique_train_public_count": len({p1045.public_key_value(row["form"]) for row in strict_rows}),
        },
        "summary": {
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "heldout_candidate_count": heldout_candidate_count,
            "strict_validation_pass_count": len(strict_passes),
            "strict_validation_pass_models": [item["model"]["name"] for item in strict_passes],
            "tested_model_count": len(model_results),
            "train_rows": len(strict_rows),
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
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Bounded rematerialization window count")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1046-input", default=str(DEFAULT_P1046_INPUT), help="P1046 red-team probe path")
    parser.add_argument("--shuffles", type=int, default=DEFAULT_SHUFFLES, help="Deterministic public-bucket shuffle count")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to rematerialize")
    parser.add_argument("--targets", default=p1044.p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} train_rows={train} validation_rows={validation} compressed_pred={pred} compressed_false={false} heldout_candidates={heldout} strict_pass={passes} out={out}".format(
            claim=payload["claim_status"],
            train=summary["train_rows"],
            validation=summary["validation_rows"],
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            heldout=summary["heldout_candidate_count"],
            passes=summary["strict_validation_pass_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
