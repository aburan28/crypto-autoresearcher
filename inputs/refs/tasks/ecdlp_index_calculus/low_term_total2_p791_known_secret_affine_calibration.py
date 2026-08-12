#!/usr/bin/env python3
"""P791 known-secret affine calibration for the P790 anchor signal."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P789_SCRIPT = TASK_DIR / "low_term_total2_p789_recovered_row_structural_extraction.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p791_known_secret_affine_calibration_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p791_known_secret_affine_calibration.md"
SCHEMA = "ecdlp.low_term_total2_p791_known_secret_affine_calibration.v1"

DEFAULT_PREDICATES = [
    {"feature": "source_support_sum_mod_11", "value": "6"},
    {"feature": "support_span_bucket_8", "value": "9"},
    {"feature": "source_dest_y_parity_pairs", "value": "0,1"},
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def namespace_args(args: argparse.Namespace, seed_namespace: str) -> argparse.Namespace:
    values = vars(args).copy()
    values["seed_namespace"] = seed_namespace
    return argparse.Namespace(**values)


def predicate_name(predicate: dict[str, str]) -> str:
    return f"{predicate['feature']} == {predicate['value']}"


def record_matches(record: dict[str, Any], predicate: dict[str, str]) -> bool:
    return str((record.get("public_features") or {}).get(predicate["feature"])) == str(predicate["value"])


def has_anchor(record: dict[str, Any]) -> bool:
    return (record.get("private_fit_features") or {}).get("has_anchor_dest") == "true"


def row_key(record: dict[str, Any]) -> str:
    return f"{record['replica']}:{record['row_index']}:{record['chosen_form_index']}"


def count_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    anchor = [record for record in records if has_anchor(record)]
    non_anchor = [record for record in records if not has_anchor(record)]
    recovered = [record for record in records if record["matches_expected"]]
    anchor_recovered = [record for record in anchor if record["matches_expected"]]
    non_anchor_recovered = [record for record in non_anchor if record["matches_expected"]]
    return {
        "anchor_recovered_count": len(anchor_recovered),
        "anchor_recovered_rate": ratio(len(anchor_recovered), len(anchor)),
        "anchor_target_count": len(anchor),
        "non_anchor_recovered_count": len(non_anchor_recovered),
        "non_anchor_recovered_rate": ratio(len(non_anchor_recovered), len(non_anchor)),
        "non_anchor_target_count": len(non_anchor),
        "recovered_count": len(recovered),
        "recovered_rate": ratio(len(recovered), len(records)),
        "target_count": len(records),
    }


def compact_row(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "dest_support": record["dest_support"],
        "matches_expected": bool(record.get("matches_expected")),
        "pair_key": record["pair_key"],
        "private_fit_features": record["private_fit_features"],
        "public_features": {
            key: value
            for key, value in (record.get("public_features") or {}).items()
            if key
            in {
                "source_support_sum_mod_11",
                "support_span_bucket_8",
                "source_dest_y_parity_pairs",
                "support_sum_mod_11",
            }
        },
        "recovered_secret": record.get("recovered_secret"),
        "replica": int(record["replica"]),
        "row_index": int(record["row_index"]),
        "chosen_form_index": int(record["chosen_form_index"]),
        "seed_label": record["seed_label"],
        "source_support": record["source_support"],
        "target": record["target"],
    }


def known_secret_records(
    p789: Any,
    rows: list[dict[str, Any]],
    order: int,
    source_values: dict[int, int],
    pair_key: str,
    replica: int,
    source_by_index: dict[int, dict[str, int]],
    dest_by_index: dict[int, dict[str, int]],
    dest_to_source: dict[int, int],
    anchor_dest_indices: set[int],
) -> list[dict[str, Any]]:
    mapped_dest_indices = set(dest_to_source)
    records = []
    for row_index, row in enumerate(rows):
        supported = p789.supported_forms(row, mapped_dest_indices, order)
        if not supported:
            continue
        form_index, form = supported[0]
        coeffs = p789.form_coeffs(form, order)
        support = p789.form_support(coeffs, order)
        left_a = 0
        left_b = 0
        for dest_index in support:
            coeff = coeffs[1 + dest_index] % order
            source_index = int(dest_to_source[dest_index])
            left_a = (left_a + coeff * int(source_values[source_index])) % order
            left_b = (left_b + coeff) % order
        right = (int(form["rhs"]) - coeffs[0] * int(row["_expected_secret"])) % order
        placeholder_recovery = {
            "expected_secret": int(row["_expected_secret"]) % order,
            "matches_expected": False,
            "operation_counts": {},
            "recovered_secret": None,
            "secret_delta": 0,
            "support": support,
        }
        public_record = p789.row_feature_record(
            row,
            order,
            pair_key,
            replica,
            row_index,
            form_index,
            form,
            placeholder_recovery,
            source_by_index,
            dest_by_index,
            dest_to_source,
            anchor_dest_indices,
        )
        public_record["calibration_equation"] = {
            "left_a": int(left_a),
            "left_b": int(left_b),
            "right": int(right),
        }
        public_record["map_role"] = "known_secret_calibration_candidate"
        records.append(public_record)
    return records


def solve_affine_from_records(records: list[dict[str, Any]], order: int) -> dict[str, Any]:
    for left_pos, left in enumerate(records):
        left_eq = left["calibration_equation"]
        for right in records[left_pos + 1 :]:
            right_eq = right["calibration_equation"]
            det = (
                int(left_eq["left_a"]) * int(right_eq["left_b"])
                - int(right_eq["left_a"]) * int(left_eq["left_b"])
            ) % order
            if not det:
                continue
            try:
                inv_det = pow(det, -1, order)
            except ValueError:
                continue
            a_value = (
                (int(left_eq["right"]) * int(right_eq["left_b"]) - int(right_eq["right"]) * int(left_eq["left_b"]))
                * inv_det
            ) % order
            b_value = (
                (int(left_eq["left_a"]) * int(right_eq["right"]) - int(right_eq["left_a"]) * int(left_eq["right"]))
                * inv_det
            ) % order
            return {
                "a": int(a_value),
                "b": int(b_value),
                "calibration_rows": [compact_row(left), compact_row(right)],
                "determinant": int(det),
                "kind": "known_secret_affine_calibration",
                "row_count_scanned": left_pos + 2,
                "status": "solved",
            }
    return {
        "calibration_rows": [compact_row(record) for record in records[:4]],
        "kind": "known_secret_affine_calibration",
        "row_count_scanned": len(records),
        "status": "singular_or_insufficient",
    }


def affine_factor_values(
    mapping: dict[int, int],
    source_values: dict[int, int],
    order: int,
    transform: dict[str, Any],
) -> dict[int, int]:
    return {
        int(dest): (int(transform["a"]) * int(source_values[int(source)]) + int(transform["b"])) % order
        for source, dest in mapping.items()
        if int(source) in source_values
    }


def evaluate_transform(
    p789: Any,
    rows_by_replica: list[tuple[int, list[dict[str, Any]], int]],
    mapping: dict[int, int],
    source_values: dict[int, int],
    order: int,
    transform: dict[str, Any],
    pair_key: str,
    source_by_index: dict[int, dict[str, int]],
    dest_by_index: dict[int, dict[str, int]],
    anchor_dest_indices: set[int],
) -> list[dict[str, Any]]:
    factor_values = affine_factor_values(mapping, source_values, order, transform)
    dest_to_source = {int(dest): int(source) for source, dest in mapping.items()}
    records = []
    for replica, rows, row_order in rows_by_replica:
        if int(row_order) != int(order):
            raise ValueError(f"order changed within pair {pair_key}: {row_order} != {order}")
        replica_records, _ops = p789.evaluate_rows(
            rows,
            row_order,
            factor_values,
            pair_key,
            replica,
            source_by_index,
            dest_by_index,
            dest_to_source,
            anchor_dest_indices,
        )
        records.extend(replica_records)
    return records


def evaluate_predicate_fit(
    p789: Any,
    predicate: dict[str, str],
    calibration_candidates: list[dict[str, Any]],
    rows_by_replica: list[tuple[int, list[dict[str, Any]], int]],
    mapping: dict[int, int],
    source_values: dict[int, int],
    order: int,
    pair_key: str,
    source_by_index: dict[int, dict[str, int]],
    dest_by_index: dict[int, dict[str, int]],
    anchor_dest_indices: set[int],
) -> dict[str, Any]:
    selected_calibration = [record for record in calibration_candidates if record_matches(record, predicate)]
    transform = solve_affine_from_records(selected_calibration, order)
    report = {
        "calibration_candidate_count": len(selected_calibration),
        "predicate": predicate_name(predicate),
        "transform": transform,
    }
    if transform["status"] != "solved":
        report["all_heldout"] = count_records([])
        report["predicate_heldout"] = count_records([])
        report["recovered_rows"] = []
        return report
    scored_records = evaluate_transform(
        p789,
        rows_by_replica,
        mapping,
        source_values,
        order,
        transform,
        pair_key,
        source_by_index,
        dest_by_index,
        anchor_dest_indices,
    )
    calibration_keys = {row_key(record) for record in transform["calibration_rows"]}
    calibration_supports = {tuple(int(value) for value in record["dest_support"]) for record in transform["calibration_rows"]}
    heldout_records = [record for record in scored_records if row_key(record) not in calibration_keys]
    predicate_heldout = [record for record in heldout_records if record_matches(record, predicate)]
    support_reused = [
        record
        for record in predicate_heldout
        if tuple(int(value) for value in record["dest_support"]) in calibration_supports
    ]
    support_disjoint = [
        record
        for record in predicate_heldout
        if tuple(int(value) for value in record["dest_support"]) not in calibration_supports
    ]
    recovered = [record for record in predicate_heldout if record["matches_expected"]]
    report["all_heldout"] = count_records(heldout_records)
    report["predicate_heldout"] = count_records(predicate_heldout)
    report["predicate_heldout_support_disjoint"] = count_records(support_disjoint)
    report["predicate_heldout_support_reused"] = count_records(support_reused)
    report["recovered_rows"] = [compact_row(record) for record in recovered[:12]]
    return report


def max_control_counts(control_reports: list[dict[str, Any]]) -> dict[str, Any]:
    if not control_reports:
        return {
            "anchor_recovered_count": 0,
            "non_anchor_recovered_count": 0,
            "recovered_count": 0,
            "support_disjoint_recovered_count": 0,
            "support_reused_recovered_count": 0,
        }
    return {
        "anchor_recovered_count": max(
            int((report.get("predicate_heldout") or {}).get("anchor_recovered_count") or 0)
            for report in control_reports
        ),
        "non_anchor_recovered_count": max(
            int((report.get("predicate_heldout") or {}).get("non_anchor_recovered_count") or 0)
            for report in control_reports
        ),
        "recovered_count": max(
            int((report.get("predicate_heldout") or {}).get("recovered_count") or 0)
            for report in control_reports
        ),
        "support_disjoint_recovered_count": max(
            int((report.get("predicate_heldout_support_disjoint") or {}).get("recovered_count") or 0)
            for report in control_reports
        ),
        "support_reused_recovered_count": max(
            int((report.get("predicate_heldout_support_reused") or {}).get("recovered_count") or 0)
            for report in control_reports
        ),
    }


def evaluate_pair(
    p789: Any,
    p788: Any,
    p787: Any,
    p786: Any,
    p784: Any,
    stack: dict[str, Any],
    base_groups: dict[str, dict[str, Any]],
    frozen: dict[str, Any],
    predicates: list[dict[str, str]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source_item = base_groups[frozen["source_group_key"]]
    dest_item = base_groups[frozen["dest_group_key"]]
    pair_key = f"{frozen['source_group_key']}->{frozen['dest_group_key']}"
    source_args = namespace_args(args, args.source_fit_seed_namespace)
    source_solve = p786.selected_case(p784, stack, source_item, "source", source_args)
    source_fb = p786.public_factor_base(stack, str(source_item["target"]), int(source_item["factor_base_size"]))
    dest_fb = p786.public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))
    dest_order = int(dest_fb["base_order"])
    source_values = p786.normalized_factor_values(source_solve["factor_values"], dest_order)
    public_map = p787.find_public_map(p786, source_fb, dest_fb, frozen["fit_map_kind"])
    controls = p788.shuffled_mappings(
        public_map["mapping"],
        int(args.control_count),
        f"p791:{pair_key}:{frozen['fit_map_kind']}",
    )
    source_by_index = p789.point_map(source_fb)
    dest_by_index = p789.point_map(dest_fb)
    anchor_dest_indices = {int(item["dest"]) for item in frozen["fit_transform"].get("anchor_pairs") or []}

    rows_by_replica = []
    for replica in range(int(args.replicas)):
        dest_case = p787.destination_case(p784, dest_item, args.eval_seed_namespace, replica)
        rows, order = p784.collect_destination(stack, dest_case, args)
        rows_by_replica.append((replica, rows, order))
    primary_dest_to_source = {int(dest): int(source) for source, dest in public_map["mapping"].items()}
    primary_candidates = [
        record
        for replica, rows, order in rows_by_replica
        for record in known_secret_records(
            p789,
            rows,
            order,
            source_values,
            pair_key,
            replica,
            source_by_index,
            dest_by_index,
            primary_dest_to_source,
            anchor_dest_indices,
        )
    ]
    primary_reports = [
        evaluate_predicate_fit(
            p789,
            predicate,
            primary_candidates,
            rows_by_replica,
            public_map["mapping"],
            source_values,
            dest_order,
            pair_key,
            source_by_index,
            dest_by_index,
            anchor_dest_indices,
        )
        for predicate in predicates
    ]

    control_items = []
    for control in controls:
        control_mapping = control["mapping"]
        control_dest_to_source = {int(dest): int(source) for source, dest in control_mapping.items()}
        control_candidates = [
            record
            for replica, rows, order in rows_by_replica
            for record in known_secret_records(
                p789,
                rows,
                order,
                source_values,
                pair_key,
                replica,
                source_by_index,
                dest_by_index,
                control_dest_to_source,
                anchor_dest_indices,
            )
        ]
        predicate_reports = [
            evaluate_predicate_fit(
                p789,
                predicate,
                control_candidates,
                rows_by_replica,
                control_mapping,
                source_values,
                dest_order,
                pair_key,
                source_by_index,
                dest_by_index,
                anchor_dest_indices,
            )
            for predicate in predicates
        ]
        control_items.append(
            {
                "control_index": int(control["control_index"]),
                "moved_source_count": int(control["moved_source_count"]),
                "predicate_reports": predicate_reports,
            }
        )

    primary_by_predicate = {report["predicate"]: report for report in primary_reports}
    control_by_predicate = {
        predicate_name(predicate): [
            report
            for control in control_items
            for report in control["predicate_reports"]
            if report["predicate"] == predicate_name(predicate)
        ]
        for predicate in predicates
    }
    predicate_comparison = []
    for predicate in predicates:
        name = predicate_name(predicate)
        primary = primary_by_predicate[name]
        max_control = max_control_counts(control_by_predicate[name])
        predicate_comparison.append(
            {
                "max_control_predicate_heldout": max_control,
                "predicate": name,
                "primary_minus_max_control_anchor_recovered": int(primary["predicate_heldout"]["anchor_recovered_count"])
                - int(max_control["anchor_recovered_count"]),
                "primary_minus_max_control_non_anchor_recovered": int(
                    primary["predicate_heldout"]["non_anchor_recovered_count"]
                )
                - int(max_control["non_anchor_recovered_count"]),
                "primary_minus_max_control_recovered": int(primary["predicate_heldout"]["recovered_count"])
                - int(max_control["recovered_count"]),
                "primary_minus_max_control_support_disjoint_recovered": int(
                    primary["predicate_heldout_support_disjoint"]["recovered_count"]
                )
                - int(max_control["support_disjoint_recovered_count"]),
                "primary_minus_max_control_support_reused_recovered": int(
                    primary["predicate_heldout_support_reused"]["recovered_count"]
                )
                - int(max_control["support_reused_recovered_count"]),
                "primary_predicate_heldout": primary["predicate_heldout"],
                "primary_support_disjoint_heldout": primary["predicate_heldout_support_disjoint"],
                "primary_support_reused_heldout": primary["predicate_heldout_support_reused"],
                "primary_transform_status": primary["transform"]["status"],
            }
        )

    return {
        "anchor_dest_indices": sorted(anchor_dest_indices),
        "control_count": int(args.control_count),
        "controls": control_items,
        "dest_group_key": frozen["dest_group_key"],
        "fit_map_kind": frozen["fit_map_kind"],
        "pair_key": pair_key,
        "predicate_comparison": predicate_comparison,
        "primary_candidate_count": len(primary_candidates),
        "primary_predicate_reports": primary_reports,
        "source_control_ok": bool(source_solve["control_ok"]),
        "source_group_key": frozen["source_group_key"],
        "source_selected_strict_pass": bool(source_solve["selected_strict_pass"]),
    }


def sum_counts(items: list[dict[str, Any]], key: str) -> dict[str, int]:
    totals = Counter()
    for item in items:
        totals.update({name: int(value or 0) for name, value in (item.get(key) or {}).items() if name.endswith("_count")})
    return dict(totals)


def global_predicate_summary(pair_results: list[dict[str, Any]], predicates: list[dict[str, str]]) -> list[dict[str, Any]]:
    summaries = []
    for predicate in predicates:
        name = predicate_name(predicate)
        primary_reports = [
            report
            for pair in pair_results
            for report in pair["primary_predicate_reports"]
            if report["predicate"] == name
        ]
        comparisons = [
            comparison
            for pair in pair_results
            for comparison in pair["predicate_comparison"]
            if comparison["predicate"] == name
        ]
        primary_counts = sum_counts(primary_reports, "predicate_heldout")
        max_control_recovered_sum = sum(
            int((comparison["max_control_predicate_heldout"] or {}).get("recovered_count") or 0)
            for comparison in comparisons
        )
        max_control_anchor_sum = sum(
            int((comparison["max_control_predicate_heldout"] or {}).get("anchor_recovered_count") or 0)
            for comparison in comparisons
        )
        max_control_non_anchor_sum = sum(
            int((comparison["max_control_predicate_heldout"] or {}).get("non_anchor_recovered_count") or 0)
            for comparison in comparisons
        )
        max_control_support_disjoint_sum = sum(
            int((comparison["max_control_predicate_heldout"] or {}).get("support_disjoint_recovered_count") or 0)
            for comparison in comparisons
        )
        max_control_support_reused_sum = sum(
            int((comparison["max_control_predicate_heldout"] or {}).get("support_reused_recovered_count") or 0)
            for comparison in comparisons
        )
        solved_pairs = sum(1 for report in primary_reports if report["transform"]["status"] == "solved")
        primary_support_disjoint_counts = sum_counts(primary_reports, "predicate_heldout_support_disjoint")
        primary_support_reused_counts = sum_counts(primary_reports, "predicate_heldout_support_reused")
        summaries.append(
            {
                "max_control_anchor_recovered_sum": max_control_anchor_sum,
                "max_control_non_anchor_recovered_sum": max_control_non_anchor_sum,
                "max_control_recovered_sum": max_control_recovered_sum,
                "max_control_support_disjoint_recovered_sum": max_control_support_disjoint_sum,
                "max_control_support_reused_recovered_sum": max_control_support_reused_sum,
                "predicate": name,
                "primary_anchor_recovered_count": int(primary_counts.get("anchor_recovered_count") or 0),
                "primary_non_anchor_recovered_count": int(primary_counts.get("non_anchor_recovered_count") or 0),
                "primary_recovered_count": int(primary_counts.get("recovered_count") or 0),
                "primary_support_disjoint_recovered_count": int(
                    primary_support_disjoint_counts.get("recovered_count") or 0
                ),
                "primary_support_reused_recovered_count": int(
                    primary_support_reused_counts.get("recovered_count") or 0
                ),
                "primary_target_count": int(primary_counts.get("target_count") or 0),
                "primary_minus_max_control_anchor_recovered_sum": int(primary_counts.get("anchor_recovered_count") or 0)
                - max_control_anchor_sum,
                "primary_minus_max_control_non_anchor_recovered_sum": int(
                    primary_counts.get("non_anchor_recovered_count") or 0
                )
                - max_control_non_anchor_sum,
                "primary_minus_max_control_recovered_sum": int(primary_counts.get("recovered_count") or 0)
                - max_control_recovered_sum,
                "primary_minus_max_control_support_disjoint_recovered_sum": int(
                    primary_support_disjoint_counts.get("recovered_count") or 0
                )
                - max_control_support_disjoint_sum,
                "primary_minus_max_control_support_reused_recovered_sum": int(
                    primary_support_reused_counts.get("recovered_count") or 0
                )
                - max_control_support_reused_sum,
                "solved_pair_count": solved_pairs,
            }
        )
    return summaries


def determine_claim(summary: dict[str, Any]) -> str:
    if not summary["positive_control"]["source_controls_ok"]:
        return "NEGATIVE_RESULT_P791_SOURCE_CONTROL_FAILURE"
    if not any(int(report["solved_pair_count"]) for report in summary["global_predicate_summary"]):
        return "NEGATIVE_RESULT_P791_NO_CALIBRATION_SYSTEM_SOLVED"
    for report in summary["global_predicate_summary"]:
        if int(report["primary_support_disjoint_recovered_count"]) > int(
            report["max_control_support_disjoint_recovered_sum"]
        ):
            return "P791_PUBLIC_KNOWN_SECRET_CALIBRATION_ANCHOR_FREE_SIGNAL"
    for report in summary["global_predicate_summary"]:
        if int(report["primary_non_anchor_recovered_count"]) > int(report["max_control_non_anchor_recovered_sum"]):
            return "P791_MARGINAL_ANCHOR_FREE_SUPPORT_REUSE_EXCESS_OVER_CONTROLS"
    for report in summary["global_predicate_summary"]:
        if int(report["primary_anchor_recovered_count"]) > int(report["max_control_anchor_recovered_sum"]):
            return "P791_ANCHOR_CONDITIONED_KNOWN_SECRET_CALIBRATION_SIGNAL"
    if any(int(report["primary_recovered_count"]) for report in summary["global_predicate_summary"]):
        return "NEGATIVE_RESULT_P791_CALIBRATION_HITS_DO_NOT_BEAT_CONTROLS"
    return "NEGATIVE_RESULT_P791_KNOWN_SECRET_AFFINE_CALIBRATION_NO_HELDOUT_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p789 = load_module("ecdlp_p789_for_p791", P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p791", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p791", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p791", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p791", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p791", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p791", p782.P780_SCRIPT)
    stack = p780.load_stack()
    predicates = list(DEFAULT_PREDICATES)
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({key for item in frozen_pairs for key in [item["source_group_key"], item["dest_group_key"]]})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [
        evaluate_pair(p789, p788, p787, p786, p784, stack, base_groups, frozen, predicates, args)
        for frozen in frozen_pairs
    ]
    global_summary = global_predicate_summary(pair_results, predicates)
    positive_control = {
        "calibration_solved_for_any_predicate": any(
            int(report["solved_pair_count"]) for report in global_summary
        ),
        "source_controls_ok": all(pair["source_control_ok"] and pair["source_selected_strict_pass"] for pair in pair_results),
    }
    summary = {
        "control_count": int(args.control_count),
        "eval_seed_namespace": args.eval_seed_namespace,
        "global_predicate_summary": global_summary,
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "positive_control": positive_control,
        "registered_predicates": [predicate_name(predicate) for predicate in predicates],
        "replicas": int(args.replicas),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p789_script": str(P789_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "CHOSEN-SECRET-CALIBRATION: calibration rows use known deterministic secrets and are excluded from held-out scoring.",
            "NO-PRIVATE-FACTOR-LOGS: affine parameters are learned from relation equations, source factor values, and known calibration secrets, not destination factor logs.",
            "PRE-REGISTERED-PREDICATES: only the three non-seed P790 predicates are evaluated.",
            "MATCHED-CONTROL: shuffled maps run the same calibration and held-out scoring procedure.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p791_known_secret_affine_calibration",
        "parameters": {
            "control_count": args.control_count,
            "eval_seed_namespace": args.eval_seed_namespace,
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "registered_predicates": [predicate_name(predicate) for predicate in predicates],
            "replicas": args.replicas,
            "row_policy": args.row_policy,
            "source_fit_seed_namespace": args.source_fit_seed_namespace,
            "sparse_policies": csv_strings(args.sparse_policies),
            "walk_mode": args.walk_mode,
            "width": args.width,
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "schema": f"{SCHEMA}.summary",
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--source-fit-seed-namespace", default="coordbridge-v1")
    parser.add_argument("--eval-seed-namespace", default="affinecalib-v1")
    parser.add_argument("--replicas", type=int, default=5)
    parser.add_argument("--control-count", type=int, default=8)
    parser.add_argument("--row-policy", default="sequential_min_forms_ge_1")
    parser.add_argument("--sparse-policies", default="natural,support_asc,support_span_asc,pivot_low,pivot_high,coefficient_weight_asc")
    parser.add_argument("--width", type=int, default=2)
    parser.add_argument("--walk-mode", default="hash6")
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--max-subsets", type=int, default=25000)
    parser.add_argument("--field-weights", default="1,2")
    parser.add_argument("--public-substitution-ops-per-selected", type=int, default=6)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "global_predicate_summary": summary["summary"]["global_predicate_summary"],
                "positive_control": summary["summary"]["positive_control"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
