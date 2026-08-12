#!/usr/bin/env python3
"""P790 fresh validation of P789 anchor-confounded public predicates."""

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
DEFAULT_P789_SUMMARY = STATE_DIR / "low_term_total2_p789_recovered_row_structural_extraction_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p790_predicate_fresh_validation_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p790_predicate_fresh_validation.md"
SCHEMA = "ecdlp.low_term_total2_p790_predicate_fresh_validation.v1"

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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def predicate_counts(records: list[dict[str, Any]], predicate: dict[str, str]) -> dict[str, Any]:
    selected = [record for record in records if record_matches(record, predicate)]
    return {
        "predicate": predicate_name(predicate),
        **count_records(selected),
    }


def recovered_sample(records: list[dict[str, Any]], limit: int = 12) -> list[dict[str, Any]]:
    return [
        {
            "dest_support": record["dest_support"],
            "matches_expected": record["matches_expected"],
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
                    "seed_index_mod_7",
                }
            },
            "recovered_secret": record["recovered_secret"],
            "replica": record["replica"],
            "seed_label": record["seed_label"],
            "source_support": record["source_support"],
            "target": record["target"],
        }
        for record in records
        if record["matches_expected"]
    ][:limit]


def control_summary(control_records: dict[int, list[dict[str, Any]]], predicates: list[dict[str, str]]) -> list[dict[str, Any]]:
    summaries = []
    for control_index, records in sorted(control_records.items()):
        summaries.append(
            {
                "aggregate": count_records(records),
                "control_index": control_index,
                "predicate_counts": [predicate_counts(records, predicate) for predicate in predicates],
                "recovered_rows": recovered_sample(records),
            }
        )
    return summaries


def max_control_by_predicate(control_items: list[dict[str, Any]], predicates: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    out = {}
    for predicate in predicates:
        name = predicate_name(predicate)
        matching = [
            item
            for control in control_items
            for item in control["predicate_counts"]
            if item["predicate"] == name
        ]
        out[name] = {
            "max_anchor_recovered_count": max((int(item["anchor_recovered_count"]) for item in matching), default=0),
            "max_non_anchor_recovered_count": max(
                (int(item["non_anchor_recovered_count"]) for item in matching),
                default=0,
            ),
            "max_recovered_count": max((int(item["recovered_count"]) for item in matching), default=0),
        }
    return out


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
        f"p790:{pair_key}:{frozen['fit_map_kind']}",
    )
    source_by_index = p789.point_map(source_fb)
    dest_by_index = p789.point_map(dest_fb)
    anchor_dest_indices = {int(item["dest"]) for item in frozen["fit_transform"].get("anchor_pairs") or []}

    primary_records = []
    control_records: dict[int, list[dict[str, Any]]] = {control["control_index"]: [] for control in controls}
    replica_reports = []
    expected_random = 0.0
    for replica in range(int(args.replicas)):
        dest_case = p787.destination_case(p784, dest_item, args.eval_seed_namespace, replica)
        rows, order = p784.collect_destination(stack, dest_case, args)
        primary_values = p786.mapped_factor_values(
            public_map["mapping"],
            source_values,
            order,
            frozen["fit_transform"],
        )
        dest_to_source = {int(dest): int(source) for source, dest in public_map["mapping"].items()}
        records, _ops = p789.evaluate_rows(
            rows,
            order,
            primary_values,
            pair_key,
            replica,
            source_by_index,
            dest_by_index,
            dest_to_source,
            anchor_dest_indices,
        )
        primary_records.extend(records)
        expected_random += len(records) / order if order else 0.0
        replica_report = {
            "aggregate": count_records(records),
            "dest_rows_available": len(rows),
            "predicate_counts": [predicate_counts(records, predicate) for predicate in predicates],
            "recovered_rows": recovered_sample(records),
            "replica": replica,
        }
        replica_reports.append(replica_report)
        for control in controls:
            control_values = p786.mapped_factor_values(
                control["mapping"],
                source_values,
                order,
                frozen["fit_transform"],
            )
            control_dest_to_source = {int(dest): int(source) for source, dest in control["mapping"].items()}
            control_row_records, _control_ops = p789.evaluate_rows(
                rows,
                order,
                control_values,
                pair_key,
                replica,
                source_by_index,
                dest_by_index,
                control_dest_to_source,
                anchor_dest_indices,
            )
            control_records[control["control_index"]].extend(control_row_records)

    controls_summary = control_summary(control_records, predicates)
    max_controls = max_control_by_predicate(controls_summary, predicates)
    return {
        "anchor_dest_indices": sorted(anchor_dest_indices),
        "control_count": int(args.control_count),
        "controls": controls_summary,
        "dest_group_key": frozen["dest_group_key"],
        "fit_map_kind": frozen["fit_map_kind"],
        "max_controls_by_predicate": max_controls,
        "pair_key": pair_key,
        "primary_aggregate": {
            **count_records(primary_records),
            "expected_random_recovered": round(expected_random, 8),
        },
        "primary_predicate_counts": [predicate_counts(primary_records, predicate) for predicate in predicates],
        "primary_records": primary_records,
        "primary_recovered_rows": recovered_sample(primary_records),
        "replicas": replica_reports,
        "source_control_ok": bool(source_solve["control_ok"]),
        "source_group_key": frozen["source_group_key"],
        "source_selected_strict_pass": bool(source_solve["selected_strict_pass"]),
    }


def global_predicate_summary(pair_results: list[dict[str, Any]], predicates: list[dict[str, str]]) -> list[dict[str, Any]]:
    all_primary = [record for pair in pair_results for record in pair["primary_records"]]
    reports = []
    for predicate in predicates:
        name = predicate_name(predicate)
        primary = predicate_counts(all_primary, predicate)
        max_control_recovered_sum = 0
        max_control_anchor_recovered_sum = 0
        max_control_non_anchor_recovered_sum = 0
        for pair in pair_results:
            maxes = pair["max_controls_by_predicate"][name]
            max_control_recovered_sum += int(maxes["max_recovered_count"])
            max_control_anchor_recovered_sum += int(maxes["max_anchor_recovered_count"])
            max_control_non_anchor_recovered_sum += int(maxes["max_non_anchor_recovered_count"])
        reports.append(
            {
                **primary,
                "primary_minus_max_control_anchor_recovered_sum": int(primary["anchor_recovered_count"])
                - max_control_anchor_recovered_sum,
                "primary_minus_max_control_non_anchor_recovered_sum": int(primary["non_anchor_recovered_count"])
                - max_control_non_anchor_recovered_sum,
                "primary_minus_max_control_recovered_sum": int(primary["recovered_count"])
                - max_control_recovered_sum,
                "max_control_anchor_recovered_sum": max_control_anchor_recovered_sum,
                "max_control_non_anchor_recovered_sum": max_control_non_anchor_recovered_sum,
                "max_control_recovered_sum": max_control_recovered_sum,
            }
        )
    return reports


def determine_claim(summary: dict[str, Any]) -> str:
    if not summary["positive_control"]["source_controls_ok"]:
        return "NEGATIVE_RESULT_P790_SOURCE_CONTROL_FAILURE"
    for report in summary["global_predicate_summary"]:
        if int(report["non_anchor_recovered_count"]) > int(report["max_control_non_anchor_recovered_sum"]):
            return "P790_PUBLIC_ANCHOR_FREE_VALIDATION_SIGNAL_MISMATCH_DOMINATED"
    for report in summary["global_predicate_summary"]:
        if int(report["anchor_recovered_count"]) > int(report["max_control_anchor_recovered_sum"]):
            return "P790_ANCHOR_CONDITIONED_REPLICATION_NO_PUBLIC_BRIDGE"
    if any(int(report["recovered_count"]) for report in summary["global_predicate_summary"]):
        return "NEGATIVE_RESULT_P790_PREDICATE_HITS_DO_NOT_BEAT_CONTROLS"
    return "NEGATIVE_RESULT_P790_P789_PUBLIC_PREDICATES_DO_NOT_REPLICATE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p789 = load_module("ecdlp_p789_for_p790", P789_SCRIPT)
    p788 = p789.load_module("ecdlp_p788_for_p790", p789.P788_SCRIPT)
    p787 = p788.load_module("ecdlp_p787_for_p790", p788.P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p790", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p790", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p790", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p790", p782.P780_SCRIPT)
    stack = p780.load_stack()
    p789_summary = load_json(args.p789_summary)
    predicates = list(DEFAULT_PREDICATES)
    frozen_pairs = p788.selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({key for item in frozen_pairs for key in [item["source_group_key"], item["dest_group_key"]]})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [
        evaluate_pair(p789, p788, p787, p786, p784, stack, base_groups, frozen, predicates, args)
        for frozen in frozen_pairs
    ]
    all_primary = [record for pair in pair_results for record in pair["primary_records"]]
    global_reports = global_predicate_summary(pair_results, predicates)
    positive_control = {
        "p789_claim_status": p789_summary["claim_status"],
        "source_controls_ok": all(pair["source_control_ok"] for pair in pair_results)
        and all(pair["source_selected_strict_pass"] for pair in pair_results),
    }
    summary = {
        "control_count": int(args.control_count),
        "fresh_eval_seed_namespace": args.eval_seed_namespace,
        "global_primary_aggregate": count_records(all_primary),
        "global_predicate_summary": global_reports,
        "pair_count": len(pair_results),
        "pairs": [
            {
                key: value
                for key, value in pair.items()
                if key != "primary_records"
            }
            for pair in pair_results
        ],
        "positive_control": positive_control,
        "registered_predicates": [predicate_name(predicate) for predicate in predicates],
        "replicas": int(args.replicas),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p789_summary": str(args.p789_summary),
            "p789_script": str(P789_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "FRESH-NAMESPACE: destination rows use affinevalid-v1, distinct from P789's affineaudit-v1 replay.",
            "PRE-REGISTERED-PREDICATES: only three non-seed P789 predicates are evaluated for validation.",
            "ANCHOR-STRATIFIED: anchor-free and private-anchor-conditioned recoveries are reported separately.",
            "MATCHED-CONTROL: shuffled maps preserve destination support and eligible-row counts.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p790_predicate_fresh_validation",
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
        "primary_row_records": all_primary,
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
    parser.add_argument("--p789-summary", type=Path, default=DEFAULT_P789_SUMMARY)
    parser.add_argument("--source-fit-seed-namespace", default="coordbridge-v1")
    parser.add_argument("--eval-seed-namespace", default="affinevalid-v1")
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
                "global_primary_aggregate": summary["summary"]["global_primary_aggregate"],
                "positive_control": summary["summary"]["positive_control"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
