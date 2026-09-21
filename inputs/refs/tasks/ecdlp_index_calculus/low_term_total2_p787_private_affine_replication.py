#!/usr/bin/env python3
"""P787 frozen private-affine replication for P786 bridge hits."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P786_SCRIPT = TASK_DIR / "low_term_total2_p786_public_coordinate_bridge.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_P786_SUMMARY = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p787_private_affine_replication_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p787_private_affine_replication.md"
SCHEMA = "ecdlp.low_term_total2_p787_private_affine_replication.v1"


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


def split_group_pair(pair_key: str) -> tuple[str, str]:
    source, sep, dest = pair_key.partition("->")
    if not sep:
        raise ValueError(f"bad pair key {pair_key!r}")
    return source, dest


def p786_frozen_pairs(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    pairs = []
    for item in (payload.get("summary") or {}).get("pairs") or []:
        frozen = item.get("best_private_candidate") or {}
        transform = frozen.get("transform") or {}
        if transform.get("kind") != "affine_private":
            continue
        pairs.append(
            {
                "dest_group_key": str(item["dest_group_key"]),
                "dest_target": str(item["dest_target"]),
                "fit_eligible_target_count": int(frozen.get("eligible_target_count") or 0),
                "fit_map_kind": str(frozen["map_kind"]),
                "fit_mismatch_count": int(frozen.get("transfer_mismatch_count") or 0),
                "fit_recovered_count": int(frozen.get("transfer_recovered_count") or 0),
                "fit_transform": {
                    "a": int(transform["a"]),
                    "anchor_pairs": transform.get("anchor_pairs") or [],
                    "b": int(transform.get("b", 0)),
                    "kind": "affine_private",
                },
                "source_group_key": str(item["source_group_key"]),
                "source_target": str(item["source_target"]),
            }
        )
    if not pairs:
        raise ValueError(f"no P786 affine private candidates in {path}")
    return pairs


def find_public_map(p786: Any, source_fb: dict[str, Any], dest_fb: dict[str, Any], kind: str) -> dict[str, Any]:
    matches = [item for item in p786.public_index_maps(source_fb, dest_fb) if item["kind"] == kind]
    if len(matches) != 1:
        raise ValueError(f"expected one public map {kind!r}, got {len(matches)}")
    return matches[0]


def destination_case(p784: Any, item: dict[str, Any], namespace: str, replica: int) -> dict[str, Any]:
    return p784.case_from_group(
        item,
        p784.TRIM12_DELTA,
        namespace,
        f"destrep{replica}",
        p784.DEST_SEED_COUNT,
        p784.DEST_POOL_COUNT,
    )


def evaluate_replica(
    p784: Any,
    p786: Any,
    p751: Any,
    stack: dict[str, Any],
    source_solve: dict[str, Any],
    source_values: dict[int, int],
    dest_item: dict[str, Any],
    public_map: dict[str, Any],
    frozen_transform: dict[str, Any],
    args: argparse.Namespace,
    replica: int,
) -> dict[str, Any]:
    dest_case = destination_case(p784, dest_item, args.eval_seed_namespace, replica)
    dest_rows, dest_order = p784.collect_destination(stack, dest_case, args)
    values = p786.mapped_factor_values(public_map["mapping"], source_values, dest_order, frozen_transform)
    eligible_rows = p786.rows_supported_by_map(dest_rows, set(values), dest_order)
    if eligible_rows:
        substitution = p751.substitution_recovery(eligible_rows, values, dest_order)
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
        "dest_case": dest_case,
        "dest_rows_available": len(dest_rows),
        "eligible_target_count": len(eligible_rows),
        "expected_random_recovered": ratio(len(eligible_rows), dest_order),
        "replica": replica,
        "transfer_cost": cost,
        "transfer_mismatch_count": int(substitution["mismatch_count"]),
        "transfer_recovered_count": int(substitution["recovered_count"]),
        "transfer_recovered_sample": substitution.get("recovered_sample") or [],
    }


def aggregate_replica_results(items: list[dict[str, Any]]) -> dict[str, Any]:
    eligible = sum(int(item["eligible_target_count"]) for item in items)
    recovered = sum(int(item["transfer_recovered_count"]) for item in items)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in items)
    target_rho = sum(int((item["transfer_cost"] or {}).get("target_rho_baseline") or 0) for item in items)
    marginal = sum(int((item["transfer_cost"] or {}).get("marginal_total_unit_cost") or 0) for item in items)
    combined_total = sum(int((item["transfer_cost"] or {}).get("combined_total_unit_cost") or 0) for item in items)
    combined_target_rho = sum(int((item["transfer_cost"] or {}).get("combined_target_rho_baseline") or 0) for item in items)
    expected_random = sum(float(item.get("expected_random_recovered") or 0.0) for item in items)
    return {
        "combined_source_plus_dest_total_over_target_rho": ratio(combined_total, combined_target_rho),
        "combined_source_plus_dest_total_unit_cost": combined_total,
        "eligible_target_count": eligible,
        "expected_random_recovered": round(expected_random, 8),
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "replica_count": len(items),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_target_rho_baseline": target_rho,
    }


def evaluate_pair(
    p784: Any,
    p786: Any,
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
    dest_order = int(p786.public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))["base_order"])
    source_values = p786.normalized_factor_values(source_solve["factor_values"], dest_order)
    source_fb = p786.public_factor_base(stack, str(source_item["target"]), int(source_item["factor_base_size"]))
    dest_fb = p786.public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))
    public_map = find_public_map(p786, source_fb, dest_fb, frozen["fit_map_kind"])
    replicas = [
        evaluate_replica(
            p784,
            p786,
            p751,
            stack,
            source_solve,
            source_values,
            dest_item,
            public_map,
            frozen["fit_transform"],
            args,
            replica,
        )
        for replica in range(int(args.replicas))
    ]
    aggregate = aggregate_replica_results(replicas)
    return {
        "dest_group_key": frozen["dest_group_key"],
        "dest_target": frozen["dest_target"],
        "fit_eligible_target_count": frozen["fit_eligible_target_count"],
        "fit_map_kind": frozen["fit_map_kind"],
        "fit_mismatch_count": frozen["fit_mismatch_count"],
        "fit_recovered_count": frozen["fit_recovered_count"],
        "fit_transform": frozen["fit_transform"],
        "frozen_map": {key: value for key, value in public_map.items() if key != "mapping"},
        "replica_aggregate": aggregate,
        "replicas": replicas,
        "source_control_ok": bool(source_solve["control_ok"]),
        "source_group_key": frozen["source_group_key"],
        "source_recovery_ok": bool(source_solve["recovery_ok"]),
        "source_selected_strict_pass": bool(source_solve["selected_strict_pass"]),
        "source_solve": p786.summarize_solve(source_solve),
        "source_target": frozen["source_target"],
    }


def aggregate_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    aggregates = [item["replica_aggregate"] for item in pairs]
    eligible = sum(int(item["eligible_target_count"]) for item in aggregates)
    recovered = sum(int(item["transfer_recovered_count"]) for item in aggregates)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in aggregates)
    target_rho = sum(int(item.get("transfer_target_rho_baseline") or 0) for item in aggregates)
    marginal = sum(int(item.get("marginal_total_unit_cost") or 0) for item in aggregates)
    combined_total = sum(int(item.get("combined_source_plus_dest_total_unit_cost") or 0) for item in aggregates)
    expected_random = sum(float(item.get("expected_random_recovered") or 0.0) for item in aggregates)
    fit_recovered = sum(int(item["fit_recovered_count"]) for item in pairs)
    fit_eligible = sum(int(item["fit_eligible_target_count"]) for item in pairs)
    return {
        "combined_source_plus_dest_total_unit_cost": combined_total,
        "eligible_target_count": eligible,
        "expected_random_recovered": round(expected_random, 8),
        "fit_eligible_target_count": fit_eligible,
        "fit_recovered_count": fit_recovered,
        "fit_recovered_rate": ratio(fit_recovered, fit_eligible),
        "map_kind_counts": dict(Counter(str(item["fit_map_kind"]) for item in pairs)),
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "pair_count": len(pairs),
        "replica_count": sum(int(item["replica_aggregate"]["replica_count"]) for item in pairs),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_recovered_rate": ratio(recovered, eligible),
        "transfer_target_rho_baseline": target_rho,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    pair_count = int(summary["pair_count"])
    source_ok = (
        int(summary["source_control_ok_count"]) == pair_count
        and int(summary["source_selected_strict_pass_count"]) == pair_count
    )
    recovered = int(summary["replication_aggregate"]["transfer_recovered_count"])
    mismatches = int(summary["replication_aggregate"]["transfer_mismatch_count"])
    if source_ok and recovered == 0:
        return "NEGATIVE_RESULT_P787_PRIVATE_AFFINE_HITS_DO_NOT_REPLICATE_WITH_FROZEN_PARAMS"
    if source_ok and recovered > 0 and mismatches > recovered * 10:
        return "P787_PRIVATE_AFFINE_REPLICATION_MISMATCH_DOMINATED_SIGNAL"
    if source_ok and recovered > 0 and mismatches == 0:
        return "P787_PRIVATE_AFFINE_REPLICATION_CLEAN_SIGNAL"
    if not source_ok:
        return "NEGATIVE_RESULT_P787_SOURCE_CONTROL_FAILURE"
    return "NEGATIVE_RESULT_P787_PRIVATE_AFFINE_REPLICATION_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p786 = load_module("ecdlp_p786_for_p787", P786_SCRIPT)
    p784 = p786.load_module("ecdlp_p784_for_p787", p786.P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p787", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p787", p782.P780_SCRIPT)
    stack = p780.load_stack()
    frozen_pairs = p786_frozen_pairs(args.p786_summary)
    required = sorted({key for item in frozen_pairs for key in [item["source_group_key"], item["dest_group_key"]]})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [evaluate_pair(p784, p786, stack, base_groups, frozen, args) for frozen in frozen_pairs]
    recovered_by_pair = [float(item["replica_aggregate"]["transfer_recovered_count"]) for item in pair_results]
    summary = {
        "fit_aggregate": {
            "eligible_target_count": sum(int(item["fit_eligible_target_count"]) for item in pair_results),
            "mismatch_count": sum(int(item["fit_mismatch_count"]) for item in pair_results),
            "recovered_count": sum(int(item["fit_recovered_count"]) for item in pair_results),
        },
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "recovered_by_pair_stats": stat(recovered_by_pair),
        "replication_aggregate": aggregate_pairs(pair_results),
        "source_control_ok_count": sum(1 for item in pair_results if item["source_control_ok"]),
        "source_selected_strict_pass_count": sum(1 for item in pair_results if item["source_selected_strict_pass"]),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p786_summary": str(args.p786_summary),
            "p786_script": str(P786_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PRIVATE-DIAGNOSTIC: frozen affine parameters came from P786 destination factor-value fitting.",
            "FROZEN-PARAMETERS: no P787 destination factor logs or row outcomes are used for affine fitting.",
            "MODEL-BOUND: this tests only the P786 affine bridge candidates, not general target descent.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p787_private_affine_replication",
        "parameters": {
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
    parser.add_argument("--eval-seed-namespace", default="affinerep-v1")
    parser.add_argument("--replicas", type=int, default=2)
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
                "fit_aggregate": summary["summary"]["fit_aggregate"],
                "pair_count": summary["summary"]["pair_count"],
                "replication_aggregate": summary["summary"]["replication_aggregate"],
                "source_control_ok_count": summary["summary"]["source_control_ok_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
