#!/usr/bin/env python3
"""P1045 representation-change scout for the p231 y-residue relation stream."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1036_p231_adjacent_family_supply_scout as p1036
import low_term_total2_p1038_p231_guarded_structural_family_supply_search as p1038
import low_term_total2_p1039_p231_strict_leaf8_route_validation as p1039
import low_term_total2_p1041_p231_yresidue_strict_route_validation as p1041
import low_term_total2_p1043_p231_yresidue_relation_rank_audit as p1043
import low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout as p1044


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1045_p231_yresidue_representation_change_rank_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1045_p231_yresidue_representation_change_rank_scout_probe.json"
DEFAULT_P1044_INPUT = STATE_DIR / "low_term_total2_p1044_p231_yresidue_adjacent_family_rank_diversity_scout_probe.json"
DEFAULT_INPUTS = [
    STATE_DIR / "low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json",
    STATE_DIR / "low_term_total2_p1041_p231_yresidue_strict_route_validation_probe.json",
    STATE_DIR / "low_term_total2_p1042_p231_yresidue_second_holdout_validation_probe.json",
]
SCHEMA = "ecdlp.low_term_total2_p1045_p231_yresidue_representation_change_rank_scout.v1"
ORDER = p1033.ORDER
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 64
BASE_SIGNATURE = p1044.BASE_SIGNATURE
BASE_RESIDUAL = p1044.BASE_RESIDUAL

LabelFn = Callable[[int, dict[str, Any], int, int], Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def public_coords(form: dict[str, Any]) -> tuple[int, int] | tuple[()]:
    coords = p1041.public_coords(form)
    if len(coords) < 2:
        return ()
    return int_value(coords[0]) % ORDER, int_value(coords[1]) % ORDER


def public_key_value(form: dict[str, Any]) -> str:
    return str(form.get("public_fingerprint") or p1036.public_key(form))


def q_coeff_value(form: dict[str, Any]) -> int:
    if "q_coeff" in form:
        return int_value(form.get("q_coeff")) % ORDER
    return p1036.q_coeff(form)


def terms_tuple_value(form: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in form.get("terms") or [])


def tail_support_tuple_value(form: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in form.get("tail_support") or [])


def residue(value: int | None, modulus: int) -> Any:
    return "missing" if value is None else value % modulus


def coord_residue(form: dict[str, Any], axis: str, modulus: int) -> Any:
    coords = public_coords(form)
    if not coords:
        return "missing"
    x, y = coords
    return residue(x if axis == "x" else y, modulus)


def signed_coeff(coeff: int) -> int:
    coeff %= ORDER
    return coeff - ORDER if coeff > ORDER // 2 else coeff


def salt_parity(form: dict[str, Any]) -> tuple[Any, ...]:
    values = []
    for value in p1033.salt_tuple(form):
        if isinstance(value, int):
            values.append(value % 2)
        else:
            values.append(str(value))
    return tuple(values) or ("none",)


def support_tuple(form: dict[str, Any], factor_count: int) -> tuple[int, ...]:
    return tuple(index for index, _coeff in form_signature(form, factor_count))


def row_key_hash_bucket(form: dict[str, Any], modulus: int) -> int:
    text = json_key(p1033.row_keys(form))
    return sum((idx + 1) * ord(ch) for idx, ch in enumerate(text)) % modulus


def form_signature(form: dict[str, Any], factor_count: int) -> tuple[tuple[int, int], ...]:
    if form.get("nonzero_factors"):
        return tuple(
            sorted(
                (int_value(index), int_value(coeff) % ORDER)
                for index, coeff in (form.get("nonzero_factors") or [])
            )
        )
    return tuple(p1033.nonzero_factor_entries(form, factor_count))


def residual_for_form(form: dict[str, Any], scalar: int) -> int:
    q = q_coeff_value(form)
    rhs = int_value(form.get("rhs")) % ORDER
    return (rhs - q * scalar) % ORDER


def compact_form_summary(form: dict[str, Any], factor_count: int, residual: int) -> dict[str, Any]:
    return {
        "factor_signature": [list(item) for item in form_signature(form, factor_count)],
        "public_fingerprint": public_key_value(form),
        "q_coeff": q_coeff_value(form),
        "residual": residual,
        "rhs": int_value(form.get("rhs")) % ORDER,
        "row_keys": list(p1033.row_keys(form))[:4],
        "salt_tuple": list(p1033.salt_tuple(form)),
        "tail_support": list(tail_support_tuple_value(form)),
        "terms": list(terms_tuple_value(form)),
        "window": p1036.form_window(form),
        "x_mod_11": coord_residue(form, "x", 11),
        "y_mod_11": coord_residue(form, "y", 11),
    }


def pair_key(record: dict[str, Any]) -> tuple[Any, ...]:
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


def form_key(form: dict[str, Any], factor_count: int, residual: int) -> tuple[Any, ...]:
    return (
        p1036.form_window(form),
        public_key_value(form),
        q_coeff_value(form),
        int_value(form.get("rhs")) % ORDER,
        form_signature(form, factor_count),
        terms_tuple_value(form),
        tail_support_tuple_value(form),
        p1033.row_keys(form),
        residual,
    )


def label_model_specs(factor_count: int) -> list[dict[str, Any]]:
    return [
        {
            "description": "Positive control: standard global factor-index labels.",
            "label_fn": lambda _n, _form, index, _coeff: ("idx", index),
            "name": "standard_index",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Signed coefficient alias attached to the factor index.",
            "label_fn": lambda _n, _form, index, coeff: ("idx_signed_coeff", index, signed_coeff(coeff)),
            "name": "signed_index",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Signless coefficient alias attached to the factor index.",
            "label_fn": lambda _n, _form, index, coeff: ("idx_abs_coeff", index, p1033.coeff_class(coeff)),
            "name": "abs_coeff_index",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Repeated-term support family plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: (
                "terms_tail",
                terms_tuple_value(form),
                tail_support_tuple_value(form),
                index,
            ),
            "name": "support_split_terms_tail",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Frozen y-residue public bucket modulo 11 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_y_mod_11", coord_residue(form, "y", 11), index),
            "name": "public_y_mod_11",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "x-only Kummer-style public bucket modulo 11 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_x_mod_11", coord_residue(form, "x", 11), index),
            "name": "public_x_mod_11",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "Public y-residue bucket modulo 7 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_y_mod_7", coord_residue(form, "y", 7), index),
            "name": "public_y_mod_7",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "x-only public bucket modulo 7 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_x_mod_7", coord_residue(form, "x", 7), index),
            "name": "public_x_mod_7",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "Public y-residue bucket modulo 5 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_y_mod_5", coord_residue(form, "y", 5), index),
            "name": "public_y_mod_5",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "x-only public bucket modulo 5 plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("public_x_mod_5", coord_residue(form, "x", 5), index),
            "name": "public_x_mod_5",
            "overlocal_by_design": False,
            "public_feature": True,
        },
        {
            "description": "Salt parity context plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("salt_parity", salt_parity(form), index),
            "name": "salt_parity_index",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Coarse row-key hash bucket plus factor index.",
            "label_fn": lambda _n, form, index, _coeff: ("row_hash_mod_7", row_key_hash_bucket(form, 7), index),
            "name": "row_hash_mod_7_index",
            "overlocal_by_design": True,
            "public_feature": False,
        },
        {
            "description": "Exact public fingerprint plus factor index; diagnostic only.",
            "label_fn": lambda _n, form, index, _coeff: ("public_exact", public_key_value(form), index),
            "name": "public_exact_index",
            "overlocal_by_design": True,
            "public_feature": True,
        },
        {
            "description": "Exact x-coordinate plus factor index; diagnostic only.",
            "label_fn": lambda _n, form, index, _coeff: (
                "public_x_exact",
                public_coords(form)[0] if public_coords(form) else "missing",
                index,
            ),
            "name": "kummer_x_exact_index",
            "overlocal_by_design": True,
            "public_feature": True,
        },
        {
            "description": "Exact salt tuple plus factor index; diagnostic only.",
            "label_fn": lambda _n, form, index, _coeff: ("salt_exact", p1033.salt_tuple(form), index),
            "name": "salt_exact_index",
            "overlocal_by_design": True,
            "public_feature": False,
        },
        {
            "description": "Exact row key plus factor index; diagnostic only.",
            "label_fn": lambda _n, form, index, _coeff: ("row_key_exact", p1033.row_keys(form), index),
            "name": "row_key_exact_index",
            "overlocal_by_design": True,
            "public_feature": False,
        },
        {
            "description": "Exact nonzero support plus factor index; diagnostic only.",
            "label_fn": lambda _n, form, index, _coeff: ("support_exact", support_tuple(form, factor_count), index),
            "name": "support_exact_index",
            "overlocal_by_design": False,
            "public_feature": False,
        },
        {
            "description": "Per-form factor labels; positive over-local control.",
            "label_fn": lambda n, _form, index, _coeff: ("form_local", n, index),
            "name": "form_local_control",
            "overlocal_by_design": True,
            "public_feature": False,
        },
    ]


def collect_witness_pairs(
    forms: list[dict[str, Any]],
    factor_count: int,
    windows: list[str],
    pool: str,
) -> dict[str, Any]:
    window_set = set(windows)
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for form in forms:
        if p1036.form_window(form) not in window_set or not p1044.passes_p1044_filter(form):
            continue
        for spec in p1036.object_specs():
            key = (
                public_key_value(form),
                p1036.form_window(form),
                json_key((spec["name"], spec["key_fn"](form))),
            )
            grouped[key].append(form)

    records_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    q_diverse_group_count = 0
    for (_public, _window, object_key), group in grouped.items():
        if len({q_coeff_value(form) for form in group}) < 2:
            continue
        q_diverse_group_count += 1
        for left_offset, left in enumerate(group):
            for right in group[left_offset + 1 :]:
                predicted = p1033.derive_target_from_pair(left, right, factor_count)
                if predicted is None:
                    continue
                source_secrets = sorted(
                    {
                        int_value(value) % ORDER
                        for value in (left.get("source_secret"), right.get("source_secret"))
                        if value is not None
                    }
                )
                verified = bool(source_secrets and all(predicted == secret for secret in source_secrets))
                residuals = [residual_for_form(left, predicted), residual_for_form(right, predicted)]
                terms = terms_tuple_value(left)
                tail = tail_support_tuple_value(left)
                record = {
                    "factor_signature": [list(item) for item in form_signature(left, factor_count)],
                    "family_tail": list(tail),
                    "family_terms": list(terms),
                    "left": left,
                    "object_keys": {object_key},
                    "pools": {pool},
                    "predicted_target": predicted,
                    "public_fingerprint": public_key_value(left),
                    "q_pair": sorted([q_coeff_value(left), q_coeff_value(right)]),
                    "residuals": residuals,
                    "residuals_agree_within_pair": len(set(residuals)) == 1,
                    "rhs_pair": sorted([int_value(left.get("rhs")) % ORDER, int_value(right.get("rhs")) % ORDER]),
                    "right": right,
                    "source_secrets": source_secrets,
                    "toy_secret_verified": verified,
                    "window": p1036.form_window(left),
                }
                key = pair_key(record)
                if key in records_by_key:
                    records_by_key[key]["pools"].add(pool)
                    records_by_key[key]["object_keys"].add(object_key)
                    continue
                records_by_key[key] = record

    return {
        "eligible_form_count": sum(len(group) for group in grouped.values()),
        "group_count": len(grouped),
        "q_diverse_group_count": q_diverse_group_count,
        "records": list(records_by_key.values()),
    }


def load_compressed_records(
    forward_by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    all_records: dict[tuple[Any, ...], dict[str, Any]] = {}
    pool_summaries = []
    max_factor_count = 0
    for pool in p1035.pool_specs():
        forms, meta = p1044.reconstruct_by_window(forward_by_window, windows, pool["predicate"], True)
        factor_count = max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0])
        max_factor_count = max(max_factor_count, factor_count)
        result = collect_witness_pairs(forms, factor_count, windows, pool["name"])
        for record in result["records"]:
            key = pair_key(record)
            if key in all_records:
                all_records[key]["pools"].update(record["pools"])
                all_records[key]["object_keys"].update(record["object_keys"])
            else:
                all_records[key] = record
        pool_summaries.append(
            {
                "eligible_form_count": result["eligible_form_count"],
                "group_count": result["group_count"],
                "meta": meta,
                "name": pool["name"],
                "prediction_count": len(result["records"]),
                "q_diverse_group_count": result["q_diverse_group_count"],
                "row_count": len(p1039.selected_rows_for_pool(forward_by_window, windows, pool["predicate"])),
            }
        )

    records = sorted(all_records.values(), key=lambda item: (item["window"], item["public_fingerprint"], item["q_pair"]))
    unique_forms: dict[tuple[Any, ...], dict[str, Any]] = {}
    residual_conflicts = []
    for record in records:
        if not record["toy_secret_verified"]:
            continue
        if not record["residuals_agree_within_pair"]:
            continue
        if record["residuals"][0] != BASE_RESIDUAL:
            continue
        if tuple(tuple(item) for item in record["factor_signature"]) != BASE_SIGNATURE:
            continue
        scalar = int_value(record["predicted_target"]) % ORDER
        for side in ("left", "right"):
            form = record[side]
            residual = residual_for_form(form, scalar)
            key = form_key(form, max_factor_count, residual)
            if key in unique_forms:
                unique_forms[key]["pools"].update(record["pools"])
                unique_forms[key]["pair_count"] += 1
                continue
            unique_forms[key] = {
                "form": form,
                "pair_count": 1,
                "pools": set(record["pools"]),
                "residual": residual,
                "scalar": scalar,
            }
            if residual != BASE_RESIDUAL:
                residual_conflicts.append(compact_form_summary(form, max_factor_count, residual))

    form_rows = sorted(
        unique_forms.values(),
        key=lambda item: (
            p1036.form_window(item["form"]),
            public_key_value(item["form"]),
            q_coeff_value(item["form"]),
            int_value(item["form"].get("rhs")) % ORDER,
        ),
    )
    meta = {
        "factor_count": max_factor_count,
        "pool_summaries": pool_summaries,
        "residual_conflict_count": len(residual_conflicts),
        "residual_conflicts": residual_conflicts[:16],
    }
    return records, form_rows, meta


def load_artifact_records(input_paths: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    witness_groups = []
    for path in input_paths:
        witness_groups.extend(p1043.load_true_witness_groups(path))

    max_factor_index = 0
    records_by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for group in witness_groups:
        prediction = group["prediction"]
        left = prediction.get("left") or {}
        right = prediction.get("right") or {}
        for form in (left, right):
            for factor, _coeff in form_signature(form, 0):
                max_factor_index = max(max_factor_index, factor)
        scalar = int_value(prediction.get("predicted_target")) % ORDER
        residuals = [residual_for_form(left, scalar), residual_for_form(right, scalar)]
        record = {
            "artifact": group["artifact"],
            "factor_signature": [list(item) for item in form_signature(left, 0)],
            "family_tail": list(tail_support_tuple_value(left)),
            "family_terms": list(terms_tuple_value(left)),
            "left": left,
            "object_keys": set(group.get("models") or []),
            "pools": {p1043.PRIMARY_POOL},
            "predicted_target": scalar,
            "public_fingerprint": public_key_value(left),
            "q_pair": sorted([q_coeff_value(left), q_coeff_value(right)]),
            "residuals": residuals,
            "residuals_agree_within_pair": len(set(residuals)) == 1,
            "rhs_pair": sorted([int_value(left.get("rhs")) % ORDER, int_value(right.get("rhs")) % ORDER]),
            "right": right,
            "source_secrets": prediction.get("source_secrets") or [],
            "toy_secret_verified": bool(prediction.get("toy_secret_verified")),
            "window": p1036.form_window(left),
        }
        key = pair_key(record)
        if key in records_by_key:
            records_by_key[key]["object_keys"].update(record["object_keys"])
            records_by_key[key]["pools"].update(record["pools"])
        else:
            records_by_key[key] = record

    factor_count = max_factor_index + 1 if max_factor_index else 0
    unique_forms: dict[tuple[Any, ...], dict[str, Any]] = {}
    residual_conflicts = []
    for record in records_by_key.values():
        if not record["toy_secret_verified"]:
            continue
        if not record["residuals_agree_within_pair"]:
            continue
        if record["residuals"][0] != BASE_RESIDUAL:
            continue
        if tuple(tuple(item) for item in record["factor_signature"]) != BASE_SIGNATURE:
            continue
        scalar = int_value(record["predicted_target"]) % ORDER
        for side in ("left", "right"):
            form = record[side]
            residual = residual_for_form(form, scalar)
            key = form_key(form, factor_count, residual)
            if key in unique_forms:
                unique_forms[key]["pools"].update(record["pools"])
                unique_forms[key]["pair_count"] += 1
                continue
            unique_forms[key] = {
                "form": form,
                "pair_count": 1,
                "pools": set(record["pools"]),
                "residual": residual,
                "scalar": scalar,
            }
            if residual != BASE_RESIDUAL:
                residual_conflicts.append(compact_form_summary(form, factor_count, residual))

    form_rows = sorted(
        unique_forms.values(),
        key=lambda item: (
            p1036.form_window(item["form"]),
            public_key_value(item["form"]),
            q_coeff_value(item["form"]),
            int_value(item["form"].get("rhs")) % ORDER,
        ),
    )
    records = sorted(records_by_key.values(), key=lambda item: (item["artifact"], item["window"], item["public_fingerprint"]))
    return records, form_rows, {
        "factor_count": factor_count,
        "input_paths": [str(path) for path in input_paths],
        "rank_scope": "primary_strict_true_witness_artifacts",
        "residual_conflict_count": len(residual_conflicts),
        "residual_conflicts": residual_conflicts[:16],
        "witness_group_count": len(witness_groups),
    }


def evaluate_model(
    spec: dict[str, Any],
    form_rows: list[dict[str, Any]],
    factor_count: int,
    standard_rank: int,
    compressed_false_count: int,
) -> dict[str, Any]:
    label_index: dict[str, int] = {}
    label_counter: Counter[str] = Counter()
    row_vectors: list[list[int]] = []
    rhs_values: list[int] = []
    row_summaries = []
    label_fn: LabelFn = spec["label_fn"]

    for ordinal, item in enumerate(form_rows):
        form = item["form"]
        row_entries: dict[str, int] = defaultdict(int)
        labels_this_row = []
        for factor, coeff in form_signature(form, factor_count):
            label = json_key(label_fn(ordinal, form, factor, coeff))
            if label not in label_index:
                label_index[label] = len(label_index)
            row_entries[label] = (row_entries[label] + coeff) % ORDER
            labels_this_row.append(label)
            label_counter[label] += 1
        row = [0] * len(label_index)
        for label, value in row_entries.items():
            row[label_index[label]] = value % ORDER
        row_vectors.append(row)
        rhs_values.append(int_value(item["residual"]) % ORDER)
        row_summaries.append(
            {
                "labels": labels_this_row,
                "public_fingerprint": public_key_value(form),
                "q_coeff": q_coeff_value(form),
                "residual": int_value(item["residual"]) % ORDER,
                "window": p1036.form_window(form),
            }
        )

    final_width = len(label_index)
    normalized_rows = [row + [0] * (final_width - len(row)) for row in row_vectors]
    augmented_rows = [[*row, rhs] for row, rhs in zip(normalized_rows, rhs_values)]
    coefficient_rank = p1043.mod_rank(normalized_rows, ORDER)
    augmented_rank = p1043.mod_rank(augmented_rows, ORDER)
    residual_values = sorted({value % ORDER for value in rhs_values})
    reused_labels = [label for label, count in label_counter.items() if count >= 2]
    singleton_labels = [label for label, count in label_counter.items() if count == 1]
    max_label_multiplicity = max(label_counter.values() or [0])
    heuristic_overlocal = (
        bool(spec["overlocal_by_design"])
        or (len(label_index) >= len(form_rows) and max_label_multiplicity < 4)
        or max_label_multiplicity < 2
    )
    consistent = coefficient_rank == augmented_rank
    rank_gain = coefficient_rank > standard_rank
    candidate_success = bool(
        rank_gain
        and consistent
        and not heuristic_overlocal
        and bool(spec["public_feature"])
        and compressed_false_count == 0
        and residual_values == [BASE_RESIDUAL]
        and len(reused_labels) >= 2
    )
    return {
        "augmented_rank": augmented_rank,
        "candidate_success": candidate_success,
        "coefficient_rank": coefficient_rank,
        "consistent": consistent,
        "description": spec["description"],
        "heuristic_overlocal": heuristic_overlocal,
        "label_count": len(label_index),
        "max_label_multiplicity": max_label_multiplicity,
        "name": spec["name"],
        "overlocal_by_design": bool(spec["overlocal_by_design"]),
        "public_feature": bool(spec["public_feature"]),
        "rank_gain_over_standard": rank_gain,
        "residual_values": residual_values,
        "reused_label_count": len(reused_labels),
        "reused_labels_sample": reused_labels[:12],
        "row_count": len(form_rows),
        "row_sample": row_summaries[:8],
        "singleton_label_count": len(singleton_labels),
        "standard_rank": standard_rank,
    }


def serializable_pair_record(record: dict[str, Any], factor_count: int) -> dict[str, Any]:
    left_residual = residual_for_form(record["left"], int_value(record["predicted_target"]) % ORDER)
    right_residual = residual_for_form(record["right"], int_value(record["predicted_target"]) % ORDER)
    return {
        "factor_signature": record["factor_signature"],
        "family_tail": record["family_tail"],
        "family_terms": record["family_terms"],
        "left": compact_form_summary(record["left"], factor_count, left_residual),
        "object_key_count": len(record["object_keys"]),
        "pools": sorted(record["pools"]),
        "predicted_target": record["predicted_target"],
        "public_fingerprint": record["public_fingerprint"],
        "q_pair": record["q_pair"],
        "residuals": [left_residual, right_residual],
        "right": compact_form_summary(record["right"], factor_count, right_residual),
        "rhs_pair": record["rhs_pair"],
        "source_secrets": record["source_secrets"],
        "toy_secret_verified": record["toy_secret_verified"],
        "window": record["window"],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    input_paths = [Path(item) for item in args.inputs.split(",") if item.strip()]
    p1044_payload = json.loads(Path(args.p1044_input).read_text(encoding="utf-8"))
    windows = list(p1044_payload.get("parameters", {}).get("forward_windows") or [])
    forward_exists = p1044_payload.get("source", {}).get("forward_exists") or {}
    compressed_records, form_rows, meta = load_artifact_records(input_paths)
    factor_count = int_value(meta["factor_count"])
    p1044_summary = p1044_payload.get("summary") or {}
    compressed_true_count = int_value(p1044_summary.get("compressed_true_count"))
    compressed_false_count = int_value(p1044_summary.get("compressed_false_count"))
    compressed_prediction_count = int_value(p1044_summary.get("compressed_prediction_count"))
    false_records = [record for record in compressed_records if not record["toy_secret_verified"]]

    standard_spec = label_model_specs(factor_count)[0]
    standard_precheck = evaluate_model(standard_spec, form_rows, factor_count, 0, compressed_false_count)
    standard_rank = standard_precheck["coefficient_rank"]
    model_summaries = [
        evaluate_model(spec, form_rows, factor_count, standard_rank, compressed_false_count)
        for spec in label_model_specs(factor_count)
    ]
    model_summaries.sort(
        key=lambda item: (
            not item["candidate_success"],
            item["heuristic_overlocal"],
            not item["rank_gain_over_standard"],
            -item["coefficient_rank"],
            item["label_count"],
            item["name"],
        )
    )
    candidates = [item for item in model_summaries if item["candidate_success"]]
    overlocal_rank_gain = [
        item
        for item in model_summaries
        if item["rank_gain_over_standard"] and item["consistent"] and item["heuristic_overlocal"]
    ]
    if candidates:
        claim = "P1045_REPRESENTATION_RANK_GAIN_CANDIDATE"
        taxonomy = "OBSERVATION"
    elif overlocal_rank_gain:
        claim = "P1045_OVERLOCAL_RANK_GAIN_ONLY"
        taxonomy = "OBSERVATION"
    else:
        claim = "NEGATIVE_RESULT_P1045_NO_REPRESENTATION_RANK_GAIN"
        taxonomy = "NEGATIVE RESULT"

    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in windows
        if p1007.expanded_source_path(window).exists()
    }
    pair_records = [serializable_pair_record(record, factor_count) for record in compressed_records]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "inputs": [str(path) for path in input_paths],
            "p1044_input": str(args.p1044_input),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "input_sha256": {str(path): p1005.sha256_file(path) for path in input_paths},
            "p1044_input_sha256": p1005.sha256_file(Path(args.p1044_input)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": taxonomy,
        "compressed_false_records": [serializable_pair_record(record, factor_count) for record in false_records[:16]],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "REPRESENTATION-SCOUT: label rank gain is not sparse linear algebra closure.",
            "FROZEN-FILTER: y mod 11 in {2,7} and P1044 repeated-two-tail guards are reused unchanged.",
            "COMPRESSED-PRIMARY: only per-window row-signature-compressed records are scored for promotion.",
            "RANK-SCOPE: model rank is computed from persisted primary strict witness forms; P1044 supplies the all-pool zero-false guard.",
            "OVERLOCALITY: exact public, row, salt, and form-local labels are diagnostics unless reuse is substantial.",
            "INDEX-CALCULUS PRECURSOR: a positive result identifies a candidate coordinate system, not a full ECDLP algorithm.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "model_summaries": model_summaries,
        "parameters": {
            "base_residual": BASE_RESIDUAL,
            "base_signature": [list(item) for item in BASE_SIGNATURE],
            "factor_count": factor_count,
            "forward_windows": windows,
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "modulus": ORDER,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
            "y_allowed": sorted(p1041.Y_ALLOWED),
            "y_modulus": p1041.Y_MODULUS,
        },
        "p1044_broad_guard_summary": p1044_summary,
        "rank_input_summary": meta,
        "schema": SCHEMA,
        "source": {
            "forward_exists": forward_exists,
        },
        "summary": {
            "candidate_count": len(candidates),
            "claim_status": claim,
            "compressed_false_count": compressed_false_count,
            "compressed_prediction_count": compressed_prediction_count,
            "compressed_true_count": compressed_true_count,
            "nonoverlocal_rank_gain_count": sum(
                1
                for item in model_summaries
                if item["rank_gain_over_standard"] and item["consistent"] and not item["heuristic_overlocal"]
            ),
            "overlocal_rank_gain_count": len(overlocal_rank_gain),
            "standard_augmented_rank": standard_precheck["augmented_rank"],
            "standard_coefficient_rank": standard_rank,
            "top_candidates": candidates[:8],
            "unique_form_count": len(form_rows),
            "unique_public_count": len({public_key_value(item["form"]) for item in form_rows}),
            "unique_rank_witness_pair_count": len(compressed_records),
        },
        "timestamp": now_iso(),
        "true_witness_pairs": pair_records[:128],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument(
        "--inputs",
        default=",".join(str(path) for path in DEFAULT_INPUTS),
        help="Comma-separated persisted strict witness probe paths for rank rows",
    )
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum forward windows to scan")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--p1044-input", default=str(DEFAULT_P1044_INPUT), help="P1044 broad all-pool guard probe path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to scan")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} windows={first}..{last} compressed_pred={pred} compressed_false={false} forms={forms} standard_rank={std} nonoverlocal_rank_gain={gain} candidates={cand} out={out}".format(
            claim=payload["claim_status"],
            first=payload["parameters"]["forward_windows"][0] if payload["parameters"]["forward_windows"] else "none",
            last=payload["parameters"]["forward_windows"][-1] if payload["parameters"]["forward_windows"] else "none",
            pred=summary["compressed_prediction_count"],
            false=summary["compressed_false_count"],
            forms=summary["unique_form_count"],
            std=summary["standard_coefficient_rank"],
            gain=summary["nonoverlocal_rank_gain_count"],
            cand=summary["candidate_count"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
