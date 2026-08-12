#!/usr/bin/env python3
"""Generate pinned-row source artifacts from order-9887 mutation lanes.

P554 identified recurrent row pairs whose current supports are off-family.
This probe moves one step upstream: pin the row keys from each lane, evaluate
public low-term total-2 leaf selectors on those rows, and emit a normal source
artifact that the existing shared-product gate and priority-column scout can
replay.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_compress_probe as compress_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_public_probe as leaf_public_probe
import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_trim_probe as leaf_trim_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_LANES = STATE_DIR / "low_term_total2_order9887_source_policy_mutation_lanes_20544_20639_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_order9887_pinned_family_source_probe.json"
DEFAULT_LEAF_SELECTORS = (
    "mode_cost_low_term_support_total2,"
    "mode_low_term_support_total2,"
    "mode_double_pair_first_total2"
)
DEFAULT_EXTRA_TOP_K = "7,12,16"
LEAF_SELECTOR_RE = re.compile(r"mode_([a-z0-9_]+)_(total|perrow)([0-9]+)")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def parse_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_int_csv(raw: str | None) -> list[int]:
    return [int(item) for item in parse_csv(raw)]


def parse_leaf_selector(raw: str) -> leaf_public_probe.LeafSelectorSpec:
    match = LEAF_SELECTOR_RE.fullmatch(raw)
    if not match:
        raise ValueError(f"unsupported leaf selector: {raw}")
    public_mode, cap_mode, cap_raw = match.groups()
    cap = int(cap_raw)
    return leaf_public_probe.LeafSelectorSpec(
        name=raw,
        scope="mode",
        selection_mode="case_total" if cap_mode == "total" else "per_row",
        cap_per_row=cap if cap_mode == "perrow" else 0,
        total_leaf_cap=cap if cap_mode == "total" else 0,
        token_weight=0.0,
        leaf_index_weight=0.0,
        residue_weight=0.0,
        low_index_weight=0.0,
        public_mode=public_mode,
    )


def empty_leaf_profiles() -> dict[str, Any]:
    return {
        "target_tokens": defaultdict(Counter),
        "global_tokens": Counter(),
        "target_leaf_indices": defaultdict(Counter),
        "global_leaf_indices": Counter(),
        "target_residues": defaultdict(Counter),
        "global_residues": Counter(),
    }


def source_artifact_candidates(lanes: dict[str, Any]) -> list[Path]:
    paths = []
    for lane in list_value(lanes.get("lanes")):
        spec = dict_value(lane.get("source_policy_mutation"))
        for raw in list_value(spec.get("source_artifact_candidates")):
            path = Path(str(raw))
            if path.exists():
                paths.append(path)
    return paths


def source_parameters_from_lanes(lanes: dict[str, Any]) -> dict[str, Any]:
    for path in source_artifact_candidates(lanes):
        payload = load_json(path)
        params = payload.get("parameters")
        if isinstance(params, dict):
            return dict(params)
    raise FileNotFoundError("no source artifact candidate with parameters found in lanes")


def lane_top_ks(lane: dict[str, Any], extra_top_ks: list[int]) -> list[int]:
    spec = dict_value(lane.get("source_policy_mutation"))
    values = [int_value(item) for item in list_value(spec.get("preferred_top_k_values"))]
    values.extend(extra_top_ks)
    values.append(int_value(dict_value(lane.get("base_case")).get("top_k")))
    return sorted({value for value in values if value > 0})


def lane_leaf_selectors(lane: dict[str, Any], extra_leaf_selectors: list[str]) -> list[str]:
    spec = dict_value(lane.get("source_policy_mutation"))
    values = [str(item) for item in list_value(spec.get("preferred_selectors")) if str(item)]
    values.extend(extra_leaf_selectors)
    return sorted(set(values))


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [row for row in rows if row.get("public_key_verified")]
    source_verified = [row for row in rows if row.get("source_verified")]
    ops = [float(row["ops_over_rho"]) for row in verified if float_value(row.get("ops_over_rho")) is not None]
    by_selector: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_lane: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_selector[str(row.get("selector"))].append(row)
        by_lane[str(row.get("lane_id"))].append(row)
    return {
        "case_count": len(rows),
        "public_key_verified_count": len(verified),
        "source_verified_count": len(source_verified),
        "below_rho_count": sum(1 for row in verified if row.get("below_rho")),
        "best_ops_over_rho": round(min(ops), 8) if ops else None,
        "selector_counts": {key: len(value) for key, value in sorted(by_selector.items())},
        "selector_verified_counts": {
            key: sum(1 for row in value if row.get("public_key_verified"))
            for key, value in sorted(by_selector.items())
        },
        "lane_counts": {key: len(value) for key, value in sorted(by_lane.items())},
        "lane_verified_counts": {
            key: sum(1 for row in value if row.get("public_key_verified"))
            for key, value in sorted(by_lane.items())
        },
    }


def compact_source_union(verifier: Any, selected_rows: list[dict[str, Any]], built_by_row: dict[str, dict[str, Any]]) -> dict[str, Any]:
    union = compress_probe.subset_union(verifier, selected_rows, built_by_row)
    generic_rho = max((int_value(row.get("generic_rho_steps")) for row in selected_rows), default=0)
    ops = sum(compress_probe.row_ops(row) for row in selected_rows)
    return {
        "generic_rho_steps": generic_rho,
        "ops": ops,
        "ops_over_rho": ratio(ops, generic_rho) if generic_rho else None,
        "public_key_verified": bool(union.get("union_public_key_verified")),
        "rank": int_value(union.get("union_rank")),
        "relation_count": int_value(union.get("union_relation_count")),
    }


def compact_result(
    lane: dict[str, Any],
    top_k: int,
    selector: str,
    source_union: dict[str, Any],
    result: dict[str, Any],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    base_case = dict_value(lane.get("base_case"))
    spec = dict_value(lane.get("source_policy_mutation"))
    case = {
        "source_verified": source_union.get("public_key_verified"),
        "target": base_case.get("target"),
        "top_k": top_k,
        "transfer_index": int_value(base_case.get("transfer_index")),
        "row_selector": {
            "public_key_verified": source_union.get("public_key_verified"),
            "row_keys": list_value(spec.get("pin_row_keys")),
        },
    }
    compact = leaf_public_probe.compact_case_result(case, result)
    compact.update(
        {
            "desired_family": list_value(lane.get("desired_family")),
            "desired_family_key": lane.get("desired_family_key"),
            "errors": errors,
            "lane_id": lane.get("lane_id"),
            "row_keys": list_value(spec.get("pin_row_keys")),
            "row_selector": f"{lane.get('lane_id')}_pinned_row_pair",
            "source_union": source_union,
        }
    )
    return compact


def evaluate_lane(
    lane: dict[str, Any],
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    specs_by_target: dict[str, dict[str, dict[str, Any]]],
    probe_args: argparse.Namespace,
    leaf_selectors: list[str],
    top_ks: list[int],
    residue_modulus: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_case = dict_value(lane.get("base_case"))
    spec = dict_value(lane.get("source_policy_mutation"))
    target = str(base_case.get("target"))
    transfer_index = int_value(base_case.get("transfer_index"))
    row_keys = [str(item) for item in list_value(spec.get("pin_row_keys"))]
    leaf_specs = [parse_leaf_selector(raw) for raw in leaf_selectors]
    rows: list[dict[str, Any]] = []
    lane_errors: list[dict[str, Any]] = []
    for top_k in top_ks:
        (
            selected_rows,
            built_by_row,
            components_by_row,
            local_args_by_row,
            feature_rows_by_row,
            errors,
        ) = leaf_trim_probe.scan_selected_rows(
            verifier,
            records,
            config_source,
            specs_by_target.get(target, {}),
            row_keys,
            transfer_index,
            top_k,
            probe_args,
        )
        lane_errors.extend(
            {
                **error,
                "lane_id": lane.get("lane_id"),
                "top_k": top_k,
            }
            for error in errors
        )
        source_union = compact_source_union(verifier, selected_rows, built_by_row)
        profiles = empty_leaf_profiles()
        for leaf_spec in leaf_specs:
            result = leaf_public_probe.evaluate_leaf_selector(
                verifier,
                selected_rows,
                built_by_row,
                components_by_row,
                local_args_by_row,
                feature_rows_by_row,
                target,
                profiles,
                leaf_spec,
                residue_modulus,
            )
            rows.append(compact_result(lane, top_k, leaf_spec.name, source_union, result, errors))
    return rows, lane_errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lanes", type=Path, default=DEFAULT_LANES)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--leaf-selectors", default=DEFAULT_LEAF_SELECTORS)
    parser.add_argument("--extra-leaf-selectors", default="")
    parser.add_argument("--extra-top-k", default=DEFAULT_EXTRA_TOP_K)
    parser.add_argument("--leaf-residue-modulus", type=int, default=16)
    parser.add_argument("--lane-limit", type=int, default=12)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    lanes = load_json(args.lanes)
    params = source_parameters_from_lanes(lanes)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    # Reuse the same operation model as the source artifacts that generated P554.
    base_source = load_json(source_artifact_candidates(lanes)[0])
    probe_args = repair_probe.probe_args_from_source(base_source)
    leaf_selector_defaults = parse_csv(args.leaf_selectors)
    leaf_selector_extras = parse_csv(args.extra_leaf_selectors)
    extra_top_ks = parse_int_csv(args.extra_top_k)

    policies: dict[str, dict[str, Any]] = {}
    all_rows: list[dict[str, Any]] = []
    all_errors: list[dict[str, Any]] = []
    selected_lanes = [lane for lane in list_value(lanes.get("lanes")) if isinstance(lane, dict)][: args.lane_limit]
    for lane in selected_lanes:
        leaf_selectors = lane_leaf_selectors(lane, leaf_selector_defaults + leaf_selector_extras)
        top_ks = lane_top_ks(lane, extra_top_ks)
        rows, errors = evaluate_lane(
            lane,
            verifier,
            records,
            config_source,
            specs_by_target,
            probe_args,
            leaf_selectors,
            top_ks,
            int(args.leaf_residue_modulus),
        )
        all_rows.extend(rows)
        all_errors.extend(errors)
        policies[str(lane.get("lane_id"))] = {
            "lane": lane,
            "row_selector": {
                "selector": f"{lane.get('lane_id')}_pinned_row_pair",
                "spec": {
                    "pin_row_keys": dict_value(lane.get("source_policy_mutation")).get("pin_row_keys"),
                    "desired_family": lane.get("desired_family"),
                    "desired_family_key": lane.get("desired_family_key"),
                },
            },
            "stress_leaf_results": rows,
            "stress_leaf_summary": summarize_rows(rows),
        }

    output = {
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: pinned source rows reuse the current shared-challenge low-term total2 verifier model.",
            "HEURISTIC: forcing a row pair and public leaf selector is a source-generation test, not a relation certificate.",
            "NO SPEEDUP CLAIM: downstream shared-product replay, priority-family exactness, direct export, substitution, sparse-LA, target descent, and rho accounting remain separate gates.",
        ],
        "method": "p554_pinned_row_pair_family_source_generation",
        "parameters": {
            **params,
            "extra_leaf_selectors": leaf_selector_extras,
            "extra_top_k": extra_top_ks,
            "lane_limit": args.lane_limit,
            "lanes": str(args.lanes),
            "leaf_residue_modulus": args.leaf_residue_modulus,
            "leaf_selectors": leaf_selector_defaults,
            "out": str(args.out),
        },
        "policies": policies,
        "schema": "ecdlp.low_term_total2_order9887_pinned_family_source_probe.v1",
        "summary": {
            **summarize_rows(all_rows),
            "error_count": len(all_errors),
            "lane_count": len(selected_lanes),
            "result_count": len(all_rows),
        },
        "errors": all_errors[:40],
    }
    write_json(args.out, output)
    print(json.dumps(output["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
