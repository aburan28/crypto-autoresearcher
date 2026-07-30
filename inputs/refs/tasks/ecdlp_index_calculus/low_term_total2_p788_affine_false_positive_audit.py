#!/usr/bin/env python3
"""P788 shuffled-control audit for P787 private-affine hits."""

from __future__ import annotations

import argparse
import importlib.util
import json
import random
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P787_SCRIPT = TASK_DIR / "low_term_total2_p787_private_affine_replication.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p788_affine_false_positive_audit_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p788_affine_false_positive_audit.md"
SCHEMA = "ecdlp.low_term_total2_p788_affine_false_positive_audit.v1"


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


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def namespace_args(args: argparse.Namespace, seed_namespace: str) -> argparse.Namespace:
    values = vars(args).copy()
    values["seed_namespace"] = seed_namespace
    return argparse.Namespace(**values)


def selected_frozen_pairs(p787: Any, path: Path) -> list[dict[str, Any]]:
    pairs = [
        item
        for item in p787.p786_frozen_pairs(path)
        if str(item["fit_map_kind"]).startswith("exact_common_x") and int(item["fit_recovered_count"]) > 0
    ]
    if not pairs:
        raise ValueError(f"no exact-common-x P786 private affine hits in {path}")
    return pairs


def shuffled_mappings(mapping: dict[int, int], control_count: int, seed: str) -> list[dict[str, Any]]:
    source_indices = sorted(mapping)
    dest_indices = [int(mapping[index]) for index in source_indices]
    controls = []
    for control_index in range(control_count):
        rng = random.Random(f"{seed}:{control_index}")
        shuffled_sources = list(source_indices)
        for _attempt in range(8):
            rng.shuffle(shuffled_sources)
            if any(left != right for left, right in zip(shuffled_sources, source_indices)):
                break
        shuffled = {int(source): int(dest) for source, dest in zip(shuffled_sources, dest_indices)}
        controls.append(
            {
                "control_index": control_index,
                "mapping": shuffled,
                "moved_source_count": sum(1 for left, right in zip(shuffled_sources, source_indices) if left != right),
            }
        )
    return controls


def evaluate_on_rows(
    p784: Any,
    p786: Any,
    p751: Any,
    rows: list[dict[str, Any]],
    order: int,
    source_solve: dict[str, Any],
    source_values: dict[int, int],
    mapping: dict[int, int],
    transform: dict[str, Any],
) -> dict[str, Any]:
    values = p786.mapped_factor_values(mapping, source_values, order, transform)
    eligible_rows = p786.rows_supported_by_map(rows, set(values), order)
    if eligible_rows:
        substitution = p751.substitution_recovery(eligible_rows, values, order)
    else:
        substitution = {
            "mismatch_count": 0,
            "operation_counts": {"total_field_ops": 0},
            "recovered_count": 0,
            "recovered_sample": [],
        }
    cost = p784.heldout_cost(
        eligible_rows,
        substitution,
        int(source_solve["selected_total_unit_cost"]),
        int(source_solve["selected_rho_baseline"]),
        2,
    )
    return {
        "eligible_target_count": len(eligible_rows),
        "expected_random_recovered": ratio(len(eligible_rows), order),
        "transfer_cost": cost,
        "transfer_mismatch_count": int(substitution["mismatch_count"]),
        "transfer_recovered_count": int(substitution["recovered_count"]),
        "transfer_recovered_sample": substitution.get("recovered_sample") or [],
    }


def aggregate_results(items: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = sum(int(item["eligible_target_count"]) for item in items)
    recovered = sum(int(item["transfer_recovered_count"]) for item in items)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in items)
    target_rho = sum(int((item["transfer_cost"] or {}).get("target_rho_baseline") or 0) for item in items)
    marginal = sum(int((item["transfer_cost"] or {}).get("marginal_total_unit_cost") or 0) for item in items)
    expected_random = sum(float(item.get("expected_random_recovered") or 0.0) for item in items)
    return {
        "eligible_target_count": eligible,
        "expected_random_recovered": round(expected_random, 8),
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "result_count": len(items),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_recovered_rate": ratio(recovered, eligible),
        "transfer_target_rho_baseline": target_rho,
    }


def evaluate_pair(
    p784: Any,
    p786: Any,
    p787: Any,
    stack: dict[str, Any],
    base_groups: dict[str, dict[str, Any]],
    frozen: dict[str, Any],
    args: argparse.Namespace,
) -> dict[str, Any]:
    p751 = stack["p751"]
    source_item = base_groups[frozen["source_group_key"]]
    dest_item = base_groups[frozen["dest_group_key"]]
    source_args = namespace_args(args, args.source_fit_seed_namespace)
    source_solve = p786.selected_case(p784, stack, source_item, "source", source_args)
    dest_fb = p786.public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))
    source_fb = p786.public_factor_base(stack, str(source_item["target"]), int(source_item["factor_base_size"]))
    dest_order = int(dest_fb["base_order"])
    source_values = p786.normalized_factor_values(source_solve["factor_values"], dest_order)
    public_map = p787.find_public_map(p786, source_fb, dest_fb, frozen["fit_map_kind"])
    controls = shuffled_mappings(
        public_map["mapping"],
        int(args.control_count),
        f"{frozen['source_group_key']}->{frozen['dest_group_key']}:{frozen['fit_map_kind']}",
    )
    primary_results = []
    control_results: dict[int, list[dict[str, Any]]] = {item["control_index"]: [] for item in controls}
    for replica in range(int(args.replicas)):
        dest_case = p787.destination_case(p784, dest_item, args.eval_seed_namespace, replica)
        rows, order = p784.collect_destination(stack, dest_case, args)
        primary = evaluate_on_rows(
            p784,
            p786,
            p751,
            rows,
            order,
            source_solve,
            source_values,
            public_map["mapping"],
            frozen["fit_transform"],
        )
        primary["dest_case"] = dest_case
        primary["replica"] = replica
        primary_results.append(primary)
        for control in controls:
            result = evaluate_on_rows(
                p784,
                p786,
                p751,
                rows,
                order,
                source_solve,
                source_values,
                control["mapping"],
                frozen["fit_transform"],
            )
            result["moved_source_count"] = control["moved_source_count"]
            result["replica"] = replica
            control_results[control["control_index"]].append(result)
    control_aggregates = [
        {
            "control_index": control_index,
            **aggregate_results(results),
        }
        for control_index, results in sorted(control_results.items())
    ]
    primary_aggregate = aggregate_results(primary_results)
    control_recovered = [float(item["transfer_recovered_count"]) for item in control_aggregates]
    max_control = max((int(item["transfer_recovered_count"]) for item in control_aggregates), default=0)
    return {
        "control_aggregates": control_aggregates,
        "control_recovered_stats": stat(control_recovered),
        "dest_group_key": frozen["dest_group_key"],
        "dest_target": frozen["dest_target"],
        "fit_eligible_target_count": frozen["fit_eligible_target_count"],
        "fit_map_kind": frozen["fit_map_kind"],
        "fit_recovered_count": frozen["fit_recovered_count"],
        "fit_transform": frozen["fit_transform"],
        "frozen_map": {key: value for key, value in public_map.items() if key != "mapping"},
        "max_control_recovered_count": max_control,
        "primary_minus_max_control_recovered": int(primary_aggregate["transfer_recovered_count"]) - max_control,
        "primary_replica_aggregate": primary_aggregate,
        "primary_replicas": primary_results,
        "source_control_ok": bool(source_solve["control_ok"]),
        "source_group_key": frozen["source_group_key"],
        "source_selected_strict_pass": bool(source_solve["selected_strict_pass"]),
        "source_solve": p786.summarize_solve(source_solve),
        "source_target": frozen["source_target"],
    }


def aggregate_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    primary = [item["primary_replica_aggregate"] for item in pairs]
    control_max_sum = sum(int(item["max_control_recovered_count"]) for item in pairs)
    primary_recovered = sum(int(item["transfer_recovered_count"]) for item in primary)
    eligible = sum(int(item["eligible_target_count"]) for item in primary)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in primary)
    expected = sum(float(item.get("expected_random_recovered") or 0.0) for item in primary)
    return {
        "eligible_target_count": eligible,
        "expected_random_recovered": round(expected, 8),
        "fit_recovered_count": sum(int(item["fit_recovered_count"]) for item in pairs),
        "map_kind_counts": dict(Counter(str(item["fit_map_kind"]) for item in pairs)),
        "max_control_recovered_sum": control_max_sum,
        "pair_count": len(pairs),
        "primary_minus_max_control_recovered": primary_recovered - control_max_sum,
        "replica_count": sum(int(item["primary_replica_aggregate"]["result_count"]) for item in pairs),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": primary_recovered,
        "transfer_recovered_rate": ratio(primary_recovered, eligible),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    pair_count = int(summary["pair_count"])
    source_ok = (
        int(summary["source_control_ok_count"]) == pair_count
        and int(summary["source_selected_strict_pass_count"]) == pair_count
    )
    primary = int(summary["audit_aggregate"]["transfer_recovered_count"])
    primary_minus_control = int(summary["audit_aggregate"]["primary_minus_max_control_recovered"])
    mismatches = int(summary["audit_aggregate"]["transfer_mismatch_count"])
    if source_ok and primary > 0 and primary_minus_control > 0 and mismatches <= primary:
        return "P788_AFFINE_AUDIT_PRIMARY_EXCEEDS_CONTROLS_CLEAN_SIGNAL"
    if source_ok and primary > 0 and primary_minus_control > 0:
        return "P788_AFFINE_AUDIT_PRIMARY_EXCEEDS_CONTROLS_BUT_MISMATCH_DOMINATED"
    if source_ok and primary > 0 and primary_minus_control <= 0:
        return "NEGATIVE_RESULT_P788_AFFINE_HITS_MATCH_SHUFFLED_CONTROLS"
    if source_ok and primary == 0:
        return "NEGATIVE_RESULT_P788_AFFINE_HITS_DISAPPEAR_ON_LARGER_REPLICATION"
    if not source_ok:
        return "NEGATIVE_RESULT_P788_SOURCE_CONTROL_FAILURE"
    return "NEGATIVE_RESULT_P788_AFFINE_FALSE_POSITIVE_AUDIT_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p787 = load_module("ecdlp_p787_for_p788", P787_SCRIPT)
    p786 = p787.load_module("ecdlp_p786_for_p788", p787.P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p788", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p788", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p788", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = selected_frozen_pairs(p787, args.p786_summary)
    required = sorted({key for item in frozen_pairs for key in [item["source_group_key"], item["dest_group_key"]]})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [evaluate_pair(p784, p786, p787, stack, base_groups, frozen, args) for frozen in frozen_pairs]
    summary = {
        "audit_aggregate": aggregate_pairs(pair_results),
        "control_count": int(args.control_count),
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "replicas": int(args.replicas),
        "source_control_ok_count": sum(1 for item in pair_results if item["source_control_ok"]),
        "source_selected_strict_pass_count": sum(1 for item in pair_results if item["source_selected_strict_pass"]),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p787_script": str(P787_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PRIVATE-DIAGNOSTIC: affine parameters came from P786 destination factor-value fitting.",
            "FROZEN-PARAMETERS: no P788 destination factor logs or row outcomes are used for fitting.",
            "MATCHED-CONTROL: shuffled maps preserve destination factor support and eligible-row counts.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p788_affine_false_positive_audit",
        "parameters": {
            "control_count": args.control_count,
            "eval_seed_namespace": args.eval_seed_namespace,
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
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
        "schema": f"{SCHEMA}.summary",
        "artifacts": payload["artifacts"],
        "claim_status": payload["claim_status"],
        "created_at": payload["created_at"],
        "honesty_boundary": payload["honesty_boundary"],
        "method": payload["method"],
        "parameters": payload["parameters"],
        "summary": payload["summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p777-summary", type=Path, default=DEFAULT_P777_SUMMARY)
    parser.add_argument("--p786-summary", type=Path, default=DEFAULT_P786_SUMMARY)
    parser.add_argument("--source-fit-seed-namespace", default="coordbridge-v1")
    parser.add_argument("--eval-seed-namespace", default="affineaudit-v1")
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
                "audit_aggregate": summary["summary"]["audit_aggregate"],
                "claim_status": summary["claim_status"],
                "control_count": summary["summary"]["control_count"],
                "pair_count": summary["summary"]["pair_count"],
                "replicas": summary["summary"]["replicas"],
                "source_control_ok_count": summary["summary"]["source_control_ok_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
