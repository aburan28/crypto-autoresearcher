#!/usr/bin/env python3
"""P785 same-label cross-prime affine alignment diagnostic."""

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
P784_SCRIPT = TASK_DIR / "low_term_total2_p784_disjoint_target_raw_transfer.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p785_same_label_affine_alignment_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p785_same_label_affine_alignment.md"
SCHEMA = "ecdlp.low_term_total2_p785_same_label_affine_alignment.v1"

DEFAULT_PAIRS = [
    "fb96|114224.v1@9341->fb96|114224.v1@9421",
    "fb96|23232.cr1@8431->fb96|23232.cr1@8467",
    "fb112|67.a1@9377->fb112|67.a1@9829",
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


def stat(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "min": None}
    return {"count": len(values), "max": max(values), "mean": round(mean(values), 8), "min": min(values)}


def csv_strings(text: str) -> list[str]:
    return [item.strip() for item in text.split(",") if item.strip()]


def csv_ints(text: str) -> list[int]:
    return [int(item.strip()) for item in text.split(",") if item.strip()]


def parse_pairs(text: str) -> list[tuple[str, str]]:
    raw_pairs = csv_strings(text) or list(DEFAULT_PAIRS)
    pairs = []
    for raw in raw_pairs:
        source, sep, dest = raw.partition("->")
        if not sep or not source.strip() or not dest.strip():
            raise argparse.ArgumentTypeError(f"pair must have source->dest shape, got {raw!r}")
        pairs.append((source.strip(), dest.strip()))
    return pairs


def normalized_factor_values(values: dict[Any, Any], order: int) -> dict[int, int]:
    return {int(index): int(value) % order for index, value in values.items()}


def transform_value(value: int, order: int, mapping: dict[str, Any]) -> int:
    kind = str(mapping["kind"])
    if kind == "identity":
        return value % order
    if kind == "signed_identity":
        return (-value) % order
    if kind in {"scalar_origin_private", "affine_private"}:
        return (int(mapping["a"]) * value + int(mapping.get("b", 0))) % order
    raise ValueError(f"unknown map kind {kind!r}")


def transform_values(values: dict[int, int], order: int, mapping: dict[str, Any]) -> dict[int, int]:
    return {index: transform_value(value, order, mapping) for index, value in values.items()}


def map_agreement(
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
    mapping: dict[str, Any],
) -> dict[str, Any]:
    common = sorted(set(source_values) & set(dest_values))
    mapped = transform_values({index: source_values[index] for index in common}, dest_order, mapping)
    matches = [index for index in common if mapped[index] == dest_values[index]]
    return {
        "common_factor_count": len(common),
        "expected_random_match_count": ratio(len(common), dest_order),
        "match_count": len(matches),
        "match_rate": ratio(len(matches), len(common)),
        "matched_index_sample": matches[:12],
    }


def with_agreement(
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
    mapping: dict[str, Any],
) -> dict[str, Any]:
    out = dict(mapping)
    out.update(map_agreement(source_values, dest_values, dest_order, mapping))
    anchor_count = len(out.get("anchor_indices") or [])
    out["anchor_count"] = anchor_count
    out["excess_match_count"] = max(0, int(out["match_count"]) - anchor_count)
    return out


def best_scalar_origin(
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
) -> dict[str, Any]:
    common = sorted(set(source_values) & set(dest_values))
    best: dict[str, Any] | None = None
    for index in common:
        source = source_values[index] % dest_order
        if not source:
            continue
        try:
            a = (dest_values[index] * pow(source, -1, dest_order)) % dest_order
        except ValueError:
            continue
        candidate = with_agreement(
            source_values,
            dest_values,
            dest_order,
            {"kind": "scalar_origin_private", "a": int(a), "b": 0, "anchor_indices": [index]},
        )
        if best is None or int(candidate["match_count"]) > int(best["match_count"]):
            best = candidate
    return best or with_agreement(
        source_values,
        dest_values,
        dest_order,
        {"kind": "scalar_origin_private", "a": 0, "b": 0, "anchor_indices": []},
    )


def best_affine(
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
) -> dict[str, Any]:
    common = sorted(set(source_values) & set(dest_values))
    best: dict[str, Any] | None = None
    for pos, left in enumerate(common):
        sx_left = source_values[left] % dest_order
        dy_left = dest_values[left] % dest_order
        for right in common[pos + 1 :]:
            denom = (source_values[right] - sx_left) % dest_order
            if not denom:
                continue
            try:
                inv = pow(denom, -1, dest_order)
            except ValueError:
                continue
            a = ((dest_values[right] - dy_left) * inv) % dest_order
            b = (dy_left - a * sx_left) % dest_order
            candidate = with_agreement(
                source_values,
                dest_values,
                dest_order,
                {"kind": "affine_private", "a": int(a), "b": int(b), "anchor_indices": [left, right]},
            )
            if best is None or int(candidate["match_count"]) > int(best["match_count"]):
                best = candidate
    return best or with_agreement(
        source_values,
        dest_values,
        dest_order,
        {"kind": "affine_private", "a": 0, "b": 0, "anchor_indices": []},
    )


def candidate_maps(source_values: dict[int, int], dest_values: dict[int, int], dest_order: int) -> list[dict[str, Any]]:
    maps = [
        with_agreement(source_values, dest_values, dest_order, {"kind": "identity"}),
        with_agreement(source_values, dest_values, dest_order, {"kind": "signed_identity"}),
        best_scalar_origin(source_values, dest_values, dest_order),
        best_affine(source_values, dest_values, dest_order),
    ]
    return sorted(maps, key=lambda item: (int(item["match_count"]), str(item["kind"])), reverse=True)


def selected_case(p784: Any, stack: dict[str, Any], item: dict[str, Any], role: str, args: argparse.Namespace) -> dict[str, Any]:
    trim12 = p784.evaluate_source_candidate(
        stack,
        p784.case_from_group(
            item,
            p784.TRIM12_DELTA,
            args.seed_namespace,
            role,
            p784.SOURCE_SEED_COUNT,
            p784.SOURCE_POOL_COUNT,
        ),
        args,
    )
    public_weight = trim12.get("public_weight2_over_selected_rho")
    if public_weight is None or float(public_weight) < p784.PUBLIC_WEIGHT2_THRESHOLD:
        trim12["trim10_evaluated"] = False
        return trim12
    trim10 = p784.evaluate_source_candidate(
        stack,
        p784.case_from_group(
            item,
            p784.TRIM10_DELTA,
            args.seed_namespace,
            role,
            p784.SOURCE_SEED_COUNT,
            p784.SOURCE_POOL_COUNT,
            budget=int(item["budget"]) + 2,
        ),
        args,
    )
    trim10["trim10_evaluated"] = True
    trim10["public_trim12_weight2_over_rho"] = public_weight
    return trim10


def summarize_solve(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "control_mismatch_count": item["control_mismatch_count"],
        "control_ok": item["control_ok"],
        "control_recovered_count": item["control_recovered_count"],
        "control_target_count": item["control_target_count"],
        "factor_base_size": item["factor_base_size"],
        "policy": item["policy"],
        "rank": item["rank"],
        "recovery_ok": item["recovery_ok"],
        "selected_strict_pass": item["selected_strict_pass"],
        "selected_total_unit_cost": item["selected_total_unit_cost"],
        "selected_weight2_over_rho": item["selected_weight2_over_rho"],
        "source_case": item["source_case"],
        "trim10_evaluated": bool(item.get("trim10_evaluated")),
    }


def evaluate_pair(
    p784: Any,
    stack: dict[str, Any],
    base_groups: dict[str, dict[str, Any]],
    source_group: str,
    dest_group: str,
    args: argparse.Namespace,
) -> dict[str, Any]:
    p746 = stack["p746"]
    p751 = stack["p751"]
    relprobe = stack["relprobe"]
    source_item = base_groups[source_group]
    dest_item = base_groups[dest_group]
    if int(source_item["factor_base_size"]) != int(dest_item["factor_base_size"]):
        raise ValueError(f"source/dest factor-base mismatch: {source_group} -> {dest_group}")

    source = selected_case(p784, stack, source_item, "source", args)
    dest_fit = selected_case(p784, stack, dest_item, "destfit", args)
    dest_case = p784.case_from_group(
        dest_item,
        p784.TRIM12_DELTA,
        args.seed_namespace,
        "desttransfer",
        p784.DEST_SEED_COUNT,
        p784.DEST_POOL_COUNT,
    )
    dest_rows, dest_order = p784.collect_destination(stack, dest_case, args)

    source_values = normalized_factor_values(source["factor_values"], dest_order)
    dest_values = normalized_factor_values(dest_fit["factor_values"], dest_order)
    maps = candidate_maps(source_values, dest_values, dest_order)
    best_map = maps[0]
    mapped_values = transform_values(source_values, dest_order, best_map)
    transfer_substitution = p751.substitution_recovery(dest_rows, mapped_values, dest_order)
    transfer_cost = p784.heldout_cost(
        dest_rows,
        transfer_substitution,
        int(source["selected_total_unit_cost"]),
        int(source["selected_rho_baseline"]),
        2,
    )

    source_meta = p784.target_metadata(p746, relprobe, str(source_item["target"]))
    dest_meta = p784.target_metadata(p746, relprobe, str(dest_item["target"]))
    source_dest_fit_total = int(source["selected_total_unit_cost"]) + int(dest_fit["selected_total_unit_cost"])
    source_dest_fit_rho = int(source["selected_rho_baseline"]) + int(dest_fit["selected_rho_baseline"])
    return {
        "best_map": best_map,
        "dest_case": dest_case,
        "dest_fit_solve": summarize_solve(dest_fit),
        "dest_group_key": dest_group,
        "dest_metadata": dest_meta,
        "dest_order": dest_order,
        "dest_rows_available": len(dest_rows),
        "dest_target": str(dest_item["target"]),
        "diagnostic_fit_total_unit_cost": source_dest_fit_total,
        "diagnostic_fit_total_unit_cost_over_selected_rho": ratio(source_dest_fit_total, source_dest_fit_rho),
        "factor_bucket": f"fb{int(source_item['factor_base_size'])}",
        "maps": maps,
        "same_label": source_meta["label"] == dest_meta["label"],
        "same_order": source_meta["base_order"] == dest_meta["base_order"],
        "same_prime": source_meta["p"] == dest_meta["p"],
        "source_group_key": source_group,
        "source_metadata": source_meta,
        "source_order": source["order"],
        "source_solve": summarize_solve(source),
        "source_target": str(source_item["target"]),
        "transfer_cost": transfer_cost,
        "transfer_mismatch_count": int(transfer_substitution["mismatch_count"]),
        "transfer_recovered_count": int(transfer_substitution["recovered_count"]),
        "transfer_recovered_sample": transfer_substitution.get("recovered_sample") or [],
        "transfer_target_count": len(dest_rows),
    }


def aggregate_pairs(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    target_count = sum(int(item["transfer_target_count"]) for item in pairs)
    recovered = sum(int(item["transfer_recovered_count"]) for item in pairs)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in pairs)
    target_rho = sum(int((item["transfer_cost"] or {}).get("target_rho_baseline") or 0) for item in pairs)
    marginal = sum(int((item["transfer_cost"] or {}).get("marginal_total_unit_cost") or 0) for item in pairs)
    combined_total = sum(int((item["transfer_cost"] or {}).get("combined_total_unit_cost") or 0) for item in pairs)
    combined_target_rho = sum(int((item["transfer_cost"] or {}).get("combined_target_rho_baseline") or 0) for item in pairs)
    return {
        "combined_source_plus_dest_total_over_target_rho": ratio(combined_total, combined_target_rho),
        "combined_source_plus_dest_total_unit_cost": combined_total,
        "dest_target_count": target_count,
        "factor_bucket_counts": dict(Counter(str(item["factor_bucket"]) for item in pairs)),
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "pair_count": len(pairs),
        "same_label_pair_count": sum(1 for item in pairs if item["same_label"]),
        "same_order_pair_count": sum(1 for item in pairs if item["same_order"]),
        "same_prime_pair_count": sum(1 for item in pairs if item["same_prime"]),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_target_rho_baseline": target_rho,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    pair_count = int(summary["pair_count"])
    source_controls_ok = int(summary["source_control_ok_count"]) == pair_count
    dest_controls_ok = int(summary["dest_fit_control_ok_count"]) == pair_count
    source_strict_ok = int(summary["source_selected_strict_pass_count"]) == pair_count
    dest_strict_ok = int(summary["dest_fit_selected_strict_pass_count"]) == pair_count
    dest_ready = int(summary["dest_capacity_ok_count"]) == pair_count
    recovered = int(summary["transfer_aggregate"]["transfer_recovered_count"])
    target_count = int(summary["transfer_aggregate"]["dest_target_count"])
    mismatches = int(summary["transfer_aggregate"]["transfer_mismatch_count"])
    controls_ok = source_controls_ok and dest_controls_ok and source_strict_ok and dest_strict_ok and dest_ready
    if controls_ok and recovered == 0 and mismatches == target_count:
        return "NEGATIVE_RESULT_P785_SIMPLE_AFFINE_ALIGNMENT_NO_TRANSFER_WITH_CONTROLS"
    if controls_ok and recovered > 0:
        return "P785_SIMPLE_AFFINE_ALIGNMENT_PRIVATE_DIAGNOSTIC_SIGNAL"
    if not source_controls_ok or not dest_controls_ok:
        return "NEGATIVE_RESULT_P785_CONTROL_FAILURE"
    return "NEGATIVE_RESULT_P785_SIMPLE_AFFINE_ALIGNMENT_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p784 = load_module("ecdlp_p784_for_p785", P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p785", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p785", p782.P780_SCRIPT)
    stack = p780.load_stack()
    pairs = parse_pairs(args.pairs)
    required = sorted({group for pair in pairs for group in pair})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [evaluate_pair(p784, stack, base_groups, source, dest, args) for source, dest in pairs]
    best_matches = [float(item["best_map"]["match_count"]) for item in pair_results]
    best_excess_matches = [float(item["best_map"]["excess_match_count"]) for item in pair_results]
    best_rates = [
        float(item["best_map"]["match_rate"])
        for item in pair_results
        if item["best_map"].get("match_rate") is not None
    ]
    summary = {
        "best_map_kinds": dict(Counter(str(item["best_map"]["kind"]) for item in pair_results)),
        "best_map_excess_match_stats": stat(best_excess_matches),
        "best_map_match_stats": stat(best_matches),
        "best_map_match_rate_stats": stat(best_rates),
        "dest_capacity_ok_count": sum(1 for item in pair_results if int(item["dest_rows_available"]) == p784.DEST_TRANSFER_COUNT),
        "dest_fit_control_ok_count": sum(1 for item in pair_results if item["dest_fit_solve"]["control_ok"]),
        "dest_fit_selected_strict_pass_count": sum(1 for item in pair_results if item["dest_fit_solve"]["selected_strict_pass"]),
        "dest_transfer_count": p784.DEST_TRANSFER_COUNT,
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "source_control_ok_count": sum(1 for item in pair_results if item["source_solve"]["control_ok"]),
        "source_selected_strict_pass_count": sum(1 for item in pair_results if item["source_solve"]["selected_strict_pass"]),
        "transfer_aggregate": aggregate_pairs(pair_results),
    }
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p777_summary": str(args.p777_summary),
            "p784_script": str(P784_SCRIPT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summary),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "PRIVATE-DIAGNOSTIC: destination factor values are solved to test whether a simple alignment exists; this is not a deployable descent step.",
            "MODEL-BOUND: only indexwise identity, signed identity, scalar, and affine maps are tested.",
            "POSITIVE-CONTROL: source and destination same-target held-out rows must recover before interpreting cross-target failure.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p785_same_label_affine_alignment",
        "parameters": {
            "field_weights": csv_ints(args.field_weights),
            "max_relations": args.max_relations,
            "max_subsets": args.max_subsets,
            "pairs": [f"{source}->{dest}" for source, dest in pairs],
            "public_substitution_ops_per_selected": args.public_substitution_ops_per_selected,
            "public_weight2_threshold": p784.PUBLIC_WEIGHT2_THRESHOLD,
            "row_policy": args.row_policy,
            "seed_namespace": args.seed_namespace,
            "sparse_policies": csv_strings(args.sparse_policies),
            "train_selected_count": p784.TRAIN_SELECTED_COUNT,
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
    parser.add_argument("--pairs", default="")
    parser.add_argument("--seed-namespace", default="align-v1")
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
                "best_map_kinds": summary["summary"]["best_map_kinds"],
                "best_map_match_stats": summary["summary"]["best_map_match_stats"],
                "claim_status": summary["claim_status"],
                "dest_fit_control_ok_count": summary["summary"]["dest_fit_control_ok_count"],
                "pair_count": summary["summary"]["pair_count"],
                "source_control_ok_count": summary["summary"]["source_control_ok_count"],
                "transfer_aggregate": summary["summary"]["transfer_aggregate"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
