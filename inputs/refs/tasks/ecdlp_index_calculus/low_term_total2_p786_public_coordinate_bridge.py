#!/usr/bin/env python3
"""P786 public coordinate bridge diagnostic for same-label cross-prime pairs."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


TASK_DIR = Path(__file__).resolve().parent
P784_SCRIPT = TASK_DIR / "low_term_total2_p784_disjoint_target_raw_transfer.py"
STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P777_SUMMARY = STATE_DIR / "low_term_total2_p777_merged_trim12_factor_first_cost_audit_summary.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p786_public_coordinate_bridge_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p786_public_coordinate_bridge.md"
SCHEMA = "ecdlp.low_term_total2_p786_public_coordinate_bridge.v1"

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
        "selected_rho_baseline": item["selected_rho_baseline"],
        "selected_strict_pass": item["selected_strict_pass"],
        "selected_total_unit_cost": item["selected_total_unit_cost"],
        "selected_weight2_over_rho": item["selected_weight2_over_rho"],
        "source_case": item["source_case"],
        "trim10_evaluated": bool(item.get("trim10_evaluated")),
    }


def public_factor_base(stack: dict[str, Any], target: str, factor_base_size: int) -> dict[str, Any]:
    p746 = stack["p746"]
    relprobe = stack["relprobe"]
    verifier, record, inv = p746.load_target(relprobe, target)
    challenge, _secret = relprobe.make_challenge(
        verifier,
        inv,
        record["ainvs"],
        "p786-public-factor-base",
        factor_base_size,
    )
    points = [
        {"index": index, "x": int(point[0]), "y": int(point[1])}
        for index, point in enumerate(challenge["factor_base"])
    ]
    return {
        "base_order": int(inv["base_order"]),
        "factor_base_size": len(points),
        "label": str(inv["label"]),
        "p": int(inv["p"]),
        "points": points,
        "target": target,
    }


def by_x(points: list[dict[str, int]]) -> dict[int, list[dict[str, int]]]:
    grouped: dict[int, list[dict[str, int]]] = defaultdict(list)
    for point in points:
        grouped[int(point["x"])].append(point)
    return {x: sorted(items, key=lambda item: (int(item["y"]), int(item["index"]))) for x, items in grouped.items()}


def map_summary(kind: str, mapping: dict[int, int], source_meta: dict[str, Any], dest_meta: dict[str, Any]) -> dict[str, Any]:
    dest_values = list(mapping.values())
    source_x = {int(item["index"]): int(item["x"]) for item in source_meta["points"]}
    dest_x = {int(item["index"]): int(item["x"]) for item in dest_meta["points"]}
    exact_x = sum(1 for source_index, dest_index in mapping.items() if source_x.get(source_index) == dest_x.get(dest_index))
    return {
        "duplicate_dest_count": len(dest_values) - len(set(dest_values)),
        "exact_x_pair_count": exact_x,
        "kind": kind,
        "mapping_size": len(mapping),
        "mapping_sample": [
            {
                "dest": int(dest_index),
                "dest_x": dest_x.get(dest_index),
                "source": int(source_index),
                "source_x": source_x.get(source_index),
            }
            for source_index, dest_index in sorted(mapping.items())[:12]
        ],
        "unique_dest_count": len(set(dest_values)),
    }


def public_index_maps(source_meta: dict[str, Any], dest_meta: dict[str, Any]) -> list[dict[str, Any]]:
    source_points = source_meta["points"]
    dest_points = dest_meta["points"]
    limit = min(len(source_points), len(dest_points))
    maps: list[dict[str, Any]] = []

    identity = {index: index for index in range(limit)}
    maps.append({"mapping": identity, **map_summary("identity_rank", identity, source_meta, dest_meta)})

    source_rank = sorted(source_points, key=lambda item: (item["x"] / source_meta["p"], item["y"] / source_meta["p"], item["index"]))
    dest_rank = sorted(dest_points, key=lambda item: (item["x"] / dest_meta["p"], item["y"] / dest_meta["p"], item["index"]))
    normalized_rank = {int(source_rank[index]["index"]): int(dest_rank[index]["index"]) for index in range(limit)}
    maps.append({"mapping": normalized_rank, **map_summary("normalized_x_rank", normalized_rank, source_meta, dest_meta)})

    source_by_x = by_x(source_points)
    dest_by_x = by_x(dest_points)
    common_x = sorted(set(source_by_x) & set(dest_by_x))
    for kind, reverse_dest, parity_sort in [
        ("exact_common_x_low_to_low", False, False),
        ("exact_common_x_low_to_high", True, False),
        ("exact_common_x_parity", False, True),
    ]:
        mapping: dict[int, int] = {}
        for x_value in common_x:
            left = list(source_by_x[x_value])
            right = list(dest_by_x[x_value])
            if parity_sort:
                left = sorted(left, key=lambda item: (item["y"] % 2, item["y"], item["index"]))
                right = sorted(right, key=lambda item: (item["y"] % 2, item["y"], item["index"]))
            elif reverse_dest:
                right = list(reversed(right))
            for source_point, dest_point in zip(left, right):
                mapping[int(source_point["index"])] = int(dest_point["index"])
        maps.append({"common_x_count": len(common_x), "mapping": mapping, **map_summary(kind, mapping, source_meta, dest_meta)})
    return maps


def transform_value(value: int, order: int, transform: dict[str, Any]) -> int:
    kind = str(transform["kind"])
    if kind == "raw":
        return value % order
    if kind == "signed":
        return (-value) % order
    if kind in {"scalar_origin_private", "affine_private"}:
        return (int(transform["a"]) * value + int(transform.get("b", 0))) % order
    raise ValueError(f"unknown transform kind {kind!r}")


def agreement_stats(
    mapping: dict[int, int],
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
    transform: dict[str, Any],
) -> dict[str, Any]:
    pairs = [
        (source_index, dest_index)
        for source_index, dest_index in sorted(mapping.items())
        if source_index in source_values and dest_index in dest_values
    ]
    matches = [
        (source_index, dest_index)
        for source_index, dest_index in pairs
        if transform_value(source_values[source_index], dest_order, transform) == dest_values[dest_index]
    ]
    anchor_count = len(transform.get("anchor_pairs") or [])
    return {
        "anchor_count": anchor_count,
        "expected_random_match_count": ratio(len(pairs), dest_order),
        "excess_match_count": max(0, len(matches) - anchor_count),
        "match_count": len(matches),
        "match_rate": ratio(len(matches), len(pairs)),
        "matched_pair_sample": [{"source": int(source), "dest": int(dest)} for source, dest in matches[:12]],
        "value_pair_count": len(pairs),
    }


def fit_scalar_origin_private(
    mapping: dict[int, int],
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for source_index, dest_index in sorted(mapping.items()):
        if source_index not in source_values or dest_index not in dest_values:
            continue
        source = source_values[source_index] % dest_order
        if not source:
            continue
        try:
            a = (dest_values[dest_index] * pow(source, -1, dest_order)) % dest_order
        except ValueError:
            continue
        transform = {"anchor_pairs": [{"source": source_index, "dest": dest_index}], "a": int(a), "b": 0, "kind": "scalar_origin_private"}
        stats = agreement_stats(mapping, source_values, dest_values, dest_order, transform)
        candidate = {**transform, **stats}
        if best is None or int(candidate["match_count"]) > int(best["match_count"]):
            best = candidate
    if best is not None:
        return best
    transform = {"anchor_pairs": [], "a": 0, "b": 0, "kind": "scalar_origin_private"}
    return {**transform, **agreement_stats(mapping, source_values, dest_values, dest_order, transform)}


def fit_affine_private(
    mapping: dict[int, int],
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
) -> dict[str, Any]:
    pairs = [
        (source_index, dest_index, source_values[source_index] % dest_order, dest_values[dest_index] % dest_order)
        for source_index, dest_index in sorted(mapping.items())
        if source_index in source_values and dest_index in dest_values
    ]
    best: dict[str, Any] | None = None
    for left_pos, left in enumerate(pairs):
        for right in pairs[left_pos + 1 :]:
            denom = (right[2] - left[2]) % dest_order
            if not denom:
                continue
            try:
                inv = pow(denom, -1, dest_order)
            except ValueError:
                continue
            a = ((right[3] - left[3]) * inv) % dest_order
            b = (left[3] - a * left[2]) % dest_order
            transform = {
                "anchor_pairs": [
                    {"source": int(left[0]), "dest": int(left[1])},
                    {"source": int(right[0]), "dest": int(right[1])},
                ],
                "a": int(a),
                "b": int(b),
                "kind": "affine_private",
            }
            stats = agreement_stats(mapping, source_values, dest_values, dest_order, transform)
            candidate = {**transform, **stats}
            if best is None or int(candidate["match_count"]) > int(best["match_count"]):
                best = candidate
    if best is not None:
        return best
    transform = {"anchor_pairs": [], "a": 0, "b": 0, "kind": "affine_private"}
    return {**transform, **agreement_stats(mapping, source_values, dest_values, dest_order, transform)}


def candidate_transforms(
    mapping: dict[int, int],
    source_values: dict[int, int],
    dest_values: dict[int, int],
    dest_order: int,
) -> list[dict[str, Any]]:
    base = []
    for transform in [{"kind": "raw"}, {"kind": "signed"}]:
        base.append({**transform, **agreement_stats(mapping, source_values, dest_values, dest_order, transform)})
    base.append(fit_scalar_origin_private(mapping, source_values, dest_values, dest_order))
    base.append(fit_affine_private(mapping, source_values, dest_values, dest_order))
    return sorted(base, key=lambda item: (int(item["match_count"]), str(item["kind"])), reverse=True)


def mapped_factor_values(
    mapping: dict[int, int],
    source_values: dict[int, int],
    dest_order: int,
    transform: dict[str, Any],
) -> dict[int, int]:
    out: dict[int, int] = {}
    for source_index, dest_index in mapping.items():
        if source_index not in source_values:
            continue
        out[int(dest_index)] = transform_value(source_values[source_index], dest_order, transform)
    return out


def supported_form(form: dict[str, Any], mapped_dest_indices: set[int], order: int) -> bool:
    coeffs = [int(value) % order for value in form.get("coeffs") or []]
    if not coeffs or not coeffs[0]:
        return False
    for factor_index, coeff in enumerate(coeffs[1:]):
        if coeff and factor_index not in mapped_dest_indices:
            return False
    return True


def rows_supported_by_map(rows: list[dict[str, Any]], mapped_dest_indices: set[int], order: int) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        forms = [form for form in row.get("forms") or [] if supported_form(form, mapped_dest_indices, order)]
        if not forms:
            continue
        copied = dict(row)
        copied["forms"] = forms
        out.append(copied)
    return out


def evaluate_bridge_candidate(
    p784: Any,
    p751: Any,
    dest_rows: list[dict[str, Any]],
    dest_order: int,
    source_solve: dict[str, Any],
    source_values: dict[int, int],
    dest_values: dict[int, int],
    public_map: dict[str, Any],
    transform: dict[str, Any],
) -> dict[str, Any]:
    mapping = public_map["mapping"]
    values = mapped_factor_values(mapping, source_values, dest_order, transform)
    eligible_rows = rows_supported_by_map(dest_rows, set(values), dest_order)
    if eligible_rows:
        substitution = p751.substitution_recovery(eligible_rows, values, dest_order)
    else:
        substitution = {
            "mismatch_count": 0,
            "operation_counts": {"total_field_ops": 0},
            "recovered_count": 0,
            "recovered_sample": [],
        }
    transfer_cost = p784.heldout_cost(
        eligible_rows,
        substitution,
        int(source_solve["selected_total_unit_cost"]),
        int(source_solve["selected_rho_baseline"]),
        2,
    )
    return {
        "agreement": {
            key: transform[key]
            for key in [
                "anchor_count",
                "excess_match_count",
                "expected_random_match_count",
                "match_count",
                "match_rate",
                "matched_pair_sample",
                "value_pair_count",
            ]
            if key in transform
        },
        "eligible_target_count": len(eligible_rows),
        "map_kind": public_map["kind"],
        "mapped_factor_count": len(values),
        "mapping_size": public_map["mapping_size"],
        "public_map": {key: value for key, value in public_map.items() if key != "mapping"},
        "transfer_cost": transfer_cost,
        "transfer_mismatch_count": int(substitution["mismatch_count"]),
        "transfer_recovered_count": int(substitution["recovered_count"]),
        "transfer_recovered_sample": substitution.get("recovered_sample") or [],
        "transform": {
            key: value
            for key, value in transform.items()
            if key
            in {
                "a",
                "anchor_count",
                "anchor_pairs",
                "b",
                "excess_match_count",
                "kind",
                "match_count",
                "match_rate",
                "value_pair_count",
            }
        },
    }


def best_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        candidates,
        key=lambda item: (
            int(item["transfer_recovered_count"]),
            int(item["eligible_target_count"]),
            int((item.get("agreement") or {}).get("match_count") or 0),
            -int((item.get("agreement") or {}).get("anchor_count") or 0),
        ),
    )


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

    source_meta = p784.target_metadata(p746, relprobe, str(source_item["target"]))
    dest_meta = p784.target_metadata(p746, relprobe, str(dest_item["target"]))
    source_fb = public_factor_base(stack, str(source_item["target"]), int(source_item["factor_base_size"]))
    dest_fb = public_factor_base(stack, str(dest_item["target"]), int(dest_item["factor_base_size"]))
    source_values = normalized_factor_values(source["factor_values"], dest_order)
    dest_values = normalized_factor_values(dest_fit["factor_values"], dest_order)

    candidates = []
    for public_map in public_index_maps(source_fb, dest_fb):
        for transform in candidate_transforms(public_map["mapping"], source_values, dest_values, dest_order):
            candidates.append(
                evaluate_bridge_candidate(
                    p784,
                    p751,
                    dest_rows,
                    dest_order,
                    source,
                    source_values,
                    dest_values,
                    public_map,
                    transform,
                )
            )
    best = best_candidate(candidates)
    public_candidates = [
        item
        for item in candidates
        if str((item.get("transform") or {}).get("kind")) in {"raw", "signed"}
    ]
    private_candidates = [
        item
        for item in candidates
        if str((item.get("transform") or {}).get("kind")) in {"scalar_origin_private", "affine_private"}
    ]
    exact_x_candidates = [item for item in candidates if str(item["map_kind"]).startswith("exact_common_x")]
    exact_x_best = best_candidate(exact_x_candidates) if exact_x_candidates else None
    return {
        "best_candidate": best,
        "best_private_candidate": best_candidate(private_candidates),
        "best_public_candidate": best_candidate(public_candidates),
        "candidate_count": len(candidates),
        "candidates": sorted(
            candidates,
            key=lambda item: (
                str(item["map_kind"]),
                str((item.get("transform") or {}).get("kind")),
            ),
        ),
        "dest_case": dest_case,
        "dest_fit_solve": summarize_solve(dest_fit),
        "dest_group_key": dest_group,
        "dest_metadata": dest_meta,
        "dest_order": dest_order,
        "dest_rows_available": len(dest_rows),
        "dest_target": str(dest_item["target"]),
        "exact_x_best_candidate": exact_x_best,
        "factor_bucket": f"fb{int(source_item['factor_base_size'])}",
        "public_factor_base": {
            "dest_first_x": [item["x"] for item in dest_fb["points"][:12]],
            "source_first_x": [item["x"] for item in source_fb["points"][:12]],
        },
        "same_label": source_meta["label"] == dest_meta["label"],
        "same_order": source_meta["base_order"] == dest_meta["base_order"],
        "same_prime": source_meta["p"] == dest_meta["p"],
        "source_group_key": source_group,
        "source_metadata": source_meta,
        "source_order": source["order"],
        "source_solve": summarize_solve(source),
        "source_target": str(source_item["target"]),
    }


def aggregate_best(pairs: list[dict[str, Any]], key: str = "best_candidate") -> dict[str, Any]:
    selected = [item[key] for item in pairs if item.get(key)]
    target_count = sum(int(item["eligible_target_count"]) for item in selected)
    recovered = sum(int(item["transfer_recovered_count"]) for item in selected)
    mismatches = sum(int(item["transfer_mismatch_count"]) for item in selected)
    target_rho = sum(int((item["transfer_cost"] or {}).get("target_rho_baseline") or 0) for item in selected)
    marginal = sum(int((item["transfer_cost"] or {}).get("marginal_total_unit_cost") or 0) for item in selected)
    combined_total = sum(int((item["transfer_cost"] or {}).get("combined_total_unit_cost") or 0) for item in selected)
    combined_target_rho = sum(int((item["transfer_cost"] or {}).get("combined_target_rho_baseline") or 0) for item in selected)
    return {
        "best_map_kinds": dict(Counter(str(item["map_kind"]) for item in selected)),
        "best_transform_kinds": dict(Counter(str((item.get("transform") or {}).get("kind")) for item in selected)),
        "combined_source_plus_dest_total_over_target_rho": ratio(combined_total, combined_target_rho),
        "combined_source_plus_dest_total_unit_cost": combined_total,
        "eligible_target_count": target_count,
        "marginal_total_unit_cost": marginal,
        "marginal_total_unit_cost_over_dest_target_rho": ratio(marginal, target_rho),
        "pair_count": len(selected),
        "transfer_mismatch_count": mismatches,
        "transfer_recovered_count": recovered,
        "transfer_target_rho_baseline": target_rho,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    pair_count = int(summary["pair_count"])
    controls_ok = (
        int(summary["source_control_ok_count"]) == pair_count
        and int(summary["dest_fit_control_ok_count"]) == pair_count
        and int(summary["source_selected_strict_pass_count"]) == pair_count
        and int(summary["dest_fit_selected_strict_pass_count"]) == pair_count
        and int(summary["dest_capacity_ok_count"]) == pair_count
    )
    public_recovered = int(summary["best_public_candidate_aggregate"]["transfer_recovered_count"])
    public_mismatches = int(summary["best_public_candidate_aggregate"]["transfer_mismatch_count"])
    private_recovered = int(summary["best_private_candidate_aggregate"]["transfer_recovered_count"])
    if controls_ok and public_recovered > 0 and public_mismatches == 0:
        return "P786_PUBLIC_COORDINATE_BRIDGE_TRANSFER_SIGNAL"
    if controls_ok and private_recovered > 0:
        return "P786_PRIVATE_AFFINE_MISMATCH_DOMINATED_DIAGNOSTIC_SIGNAL"
    if controls_ok and public_recovered == 0 and private_recovered == 0:
        return "NEGATIVE_RESULT_P786_PUBLIC_COORDINATE_BRIDGE_NO_TRANSFER_WITH_CONTROLS"
    if int(summary["source_control_ok_count"]) != pair_count or int(summary["dest_fit_control_ok_count"]) != pair_count:
        return "NEGATIVE_RESULT_P786_CONTROL_FAILURE"
    return "NEGATIVE_RESULT_P786_PUBLIC_COORDINATE_BRIDGE_INCONCLUSIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p784 = load_module("ecdlp_p784_for_p786", P784_SCRIPT)
    p782 = p784.load_module("ecdlp_p782_for_p786", p784.P782_SCRIPT)
    p780 = p782.load_module("ecdlp_p780_for_p786", p782.P780_SCRIPT)
    stack = p780.load_stack()
    pairs = parse_pairs(args.pairs)
    required = sorted({group for pair in pairs for group in pair})
    base_groups = p784.normalized_groups(args.p777_summary, required)
    pair_results = [evaluate_pair(p784, stack, base_groups, source, dest, args) for source, dest in pairs]
    all_candidates = [candidate for pair in pair_results for candidate in pair["candidates"]]
    exact_x_best_targets = [
        float(pair["exact_x_best_candidate"]["eligible_target_count"])
        for pair in pair_results
        if pair.get("exact_x_best_candidate")
    ]
    best_matches = [float((pair["best_candidate"].get("agreement") or {}).get("match_count") or 0) for pair in pair_results]
    summary = {
        "best_candidate_aggregate": aggregate_best(pair_results, "best_candidate"),
        "best_candidate_match_stats": stat(best_matches),
        "best_private_candidate_aggregate": aggregate_best(pair_results, "best_private_candidate"),
        "best_public_candidate_aggregate": aggregate_best(pair_results, "best_public_candidate"),
        "candidate_count": len(all_candidates),
        "dest_capacity_ok_count": sum(1 for item in pair_results if int(item["dest_rows_available"]) == p784.DEST_TRANSFER_COUNT),
        "dest_fit_control_ok_count": sum(1 for item in pair_results if item["dest_fit_solve"]["control_ok"]),
        "dest_fit_selected_strict_pass_count": sum(1 for item in pair_results if item["dest_fit_solve"]["selected_strict_pass"]),
        "dest_transfer_count": p784.DEST_TRANSFER_COUNT,
        "exact_x_best_eligible_target_stats": stat(exact_x_best_targets),
        "exact_x_best_aggregate": aggregate_best(pair_results, "exact_x_best_candidate"),
        "map_kind_counts": dict(Counter(str(item["map_kind"]) for item in all_candidates)),
        "pair_count": len(pair_results),
        "pairs": pair_results,
        "source_control_ok_count": sum(1 for item in pair_results if item["source_solve"]["control_ok"]),
        "source_selected_strict_pass_count": sum(1 for item in pair_results if item["source_solve"]["selected_strict_pass"]),
        "transform_kind_counts": dict(Counter(str((item.get("transform") or {}).get("kind")) for item in all_candidates)),
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
            "PUBLIC-MAP: source-to-destination index maps are derived from public factor-base point coordinates before destination factor logs are used.",
            "PRIVATE-DIAGNOSTIC: scalar/affine value transforms use destination factor values only to test whether a public map exposes a low-complexity value relation.",
            "MODEL-BOUND: identity, normalized-x-rank, and exact-common-x bridge maps are tested; general rational maps and bridge relations are not ruled out.",
            "NO DEPLOYED-CURVE CLAIM: no large-prime scaling, production-key relevance, or complete faster-than-rho ECDLP algorithm is implied.",
        ],
        "method": "p786_public_coordinate_bridge",
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
    parser.add_argument("--seed-namespace", default="coordbridge-v1")
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
                "best_candidate_aggregate": summary["summary"]["best_candidate_aggregate"],
                "best_private_candidate_aggregate": summary["summary"]["best_private_candidate_aggregate"],
                "best_public_candidate_aggregate": summary["summary"]["best_public_candidate_aggregate"],
                "claim_status": summary["claim_status"],
                "dest_fit_control_ok_count": summary["summary"]["dest_fit_control_ok_count"],
                "exact_x_best_aggregate": summary["summary"]["exact_x_best_aggregate"],
                "pair_count": summary["summary"]["pair_count"],
                "source_control_ok_count": summary["summary"]["source_control_ok_count"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
