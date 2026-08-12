#!/usr/bin/env python3
"""P964 rank-raising leaf cost decomposition."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_direct_witness_probe as direct_witness_probe  # noqa: E402
import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p961_fixed_public_hybrid_cost_squeeze as p961  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p964_rank_raising_leaf_cost_decomposition.md"
DEFAULT_P963 = STATE_DIR / "low_term_total2_p963_rank3_completion_cost_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p964_rank_raising_leaf_cost_decomposition_probe.json"
SCHEMA = "ecdlp.low_term_total2_p964_rank_raising_leaf_cost_decomposition.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def leaves_from_rows(rows: list[dict[str, Any]]) -> dict[str, set[int]]:
    return {
        str(row.get("row_key")): {int(leaf) for leaf in row.get("leaf_indices") or []}
        for row in rows
    }


def source_and_materialized(args: argparse.Namespace, row_keys: list[str]) -> tuple[Any, dict[str, Any], dict[str, Any]]:
    cases, pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    wanted = tuple(sorted(str(key) for key in row_keys))
    pair = None
    for candidate in pairs:
        if tuple(sorted(str(key) for key in candidate.get("row_keys") or [])) == wanted:
            pair = candidate
            break
    if pair is None:
        raise ValueError(f"row pair not found: {wanted!r}")
    source_path = p959.choose_source(cases, int(args.fixed_transfer))
    source = p959.p957.load_json(source_path)
    params = repair_probe.source_parameters(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    materialized = p961.build_materialized(verifier, records, config_source, specs_by_target, pair, source, args)
    materialized["source_path"] = str(source_path)
    return verifier, pair, materialized


def cost_breakdown_for_scan(built: dict[str, Any], local_args: argparse.Namespace, scan: dict[str, Any]) -> dict[str, Any]:
    selected_leaf_count = int_value(scan.get("selected_leaf_count"))
    selected_hit_roots = int_value(scan.get("selected_hit_roots"))
    selected_hit_events = int_value(scan.get("selected_hit_events"))
    row_factor = int_value(getattr(local_args, "row_factor", 1), 1)
    product_factor = int_value(getattr(local_args, "product_factor", 1), 1)
    selected_signed_pair_ops = int_value(built.get("selected_signed_pair_count"))
    row_pool_prescan_ops = ceil(int_value(built.get("row_pool")) / max(1, row_factor))
    product_leaf_ops = ceil(selected_leaf_count / max(1, product_factor))
    selected_hit_root_ops = selected_hit_roots
    selected_leaf_ops = selected_leaf_count
    selected_hit_event_verification_ops = 2 * selected_hit_events
    total = (
        selected_signed_pair_ops
        + row_pool_prescan_ops
        + product_leaf_ops
        + selected_hit_root_ops
        + selected_leaf_ops
        + selected_hit_event_verification_ops
    )
    reported = int_value(scan.get("preassociation_filter_ops"))
    return {
        "candidate_verifications": int_value(scan.get("candidate_verifications")),
        "matches_reported_ops": total == reported,
        "product_factor": product_factor,
        "product_leaf_ops": product_leaf_ops,
        "relation_count": int_value(scan.get("relation_count")),
        "reported_ops": reported,
        "row_factor": row_factor,
        "row_pool": int_value(built.get("row_pool")),
        "row_pool_prescan_ops": row_pool_prescan_ops,
        "rank": int_value(scan.get("rank")),
        "selected_hit_event_verification_ops": selected_hit_event_verification_ops,
        "selected_hit_events": selected_hit_events,
        "selected_hit_root_ops": selected_hit_root_ops,
        "selected_hit_roots": selected_hit_roots,
        "selected_leaf_count": selected_leaf_count,
        "selected_leaf_ops": selected_leaf_ops,
        "selected_signed_pair_ops": selected_signed_pair_ops,
        "total_ops": total,
    }


def scenario_breakdown(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    leaves_by_row: dict[str, set[int]],
    label: str,
) -> dict[str, Any]:
    row_breakdowns = []
    for row in materialized["selected_rows"]:
        row_key = str(row.get("row_key"))
        leaves = set(int(leaf) for leaf in leaves_by_row.get(row_key, set()))
        if not leaves:
            continue
        scan = direct_witness_probe.scan_selected(
            verifier,
            materialized["built_by_row"][row_key],
            materialized["components_by_row"][row_key],
            leaves,
            materialized["local_args_by_row"][row_key],
        )
        row_breakdowns.append(
            {
                "breakdown": cost_breakdown_for_scan(
                    materialized["built_by_row"][row_key],
                    materialized["local_args_by_row"][row_key],
                    scan,
                ),
                "leaves": sorted(leaves),
                "row_key": row_key,
            }
        )
    union = p961.scan_from_leaves(verifier, materialized, pair, leaves_by_row, label, "cost_decomposition")
    component_totals: dict[str, int] = {}
    component_keys = [
        "selected_signed_pair_ops",
        "row_pool_prescan_ops",
        "product_leaf_ops",
        "selected_hit_root_ops",
        "selected_leaf_ops",
        "selected_hit_event_verification_ops",
    ]
    for key in component_keys:
        component_totals[key] = sum(int_value(row["breakdown"].get(key)) for row in row_breakdowns)
    component_totals["total_ops"] = sum(component_totals[key] for key in component_keys)
    component_totals["reported_ops"] = sum(int_value(row["breakdown"].get("reported_ops")) for row in row_breakdowns)
    return {
        "component_totals": component_totals,
        "label": label,
        "row_breakdowns": row_breakdowns,
        "union": {
            "below_rho": bool(union.get("below_rho")),
            "derived_secret": union.get("derived_secret"),
            "generic_rho_steps": union.get("generic_rho_steps"),
            "ops": union.get("ops"),
            "ops_over_rho": union.get("ops_over_rho"),
            "public_key_verified": bool(union.get("public_key_verified")),
            "rank": union.get("rank"),
            "relation_count": union.get("relation_count"),
        },
    }


def diff_components(seed: dict[str, Any], completion: dict[str, Any]) -> dict[str, int]:
    keys = sorted(set(seed["component_totals"]) | set(completion["component_totals"]))
    return {
        key: int_value(completion["component_totals"].get(key)) - int_value(seed["component_totals"].get(key))
        for key in keys
    }


def row_diffs(seed: dict[str, Any], completion: dict[str, Any]) -> list[dict[str, Any]]:
    seed_rows = {row["row_key"]: row for row in seed.get("row_breakdowns") or []}
    completion_rows = {row["row_key"]: row for row in completion.get("row_breakdowns") or []}
    out = []
    for row_key in sorted(set(seed_rows) | set(completion_rows)):
        seed_breakdown = (seed_rows.get(row_key) or {}).get("breakdown") or {}
        completion_breakdown = (completion_rows.get(row_key) or {}).get("breakdown") or {}
        keys = sorted(set(seed_breakdown) | set(completion_breakdown))
        out.append(
            {
                "completion_leaves": (completion_rows.get(row_key) or {}).get("leaves") or [],
                "component_delta": {
                    key: int_value(completion_breakdown.get(key)) - int_value(seed_breakdown.get(key))
                    for key in keys
                    if isinstance(seed_breakdown.get(key, 0), (int, bool)) or isinstance(completion_breakdown.get(key, 0), (int, bool))
                },
                "row_key": row_key,
                "seed_leaves": (seed_rows.get(row_key) or {}).get("leaves") or [],
            }
        )
    return out


def reduction_targets(delta: dict[str, int], completion_ops: int, rho: int) -> list[dict[str, Any]]:
    shortfall = max(0, completion_ops - rho)
    out = []
    for key, value in sorted(delta.items(), key=lambda item: (-item[1], item[0])):
        if value <= 0:
            continue
        hypothetical_ops = completion_ops - value
        out.append(
            {
                "component": key,
                "component_delta": value,
                "crosses_rho_if_removed": hypothetical_ops < rho,
                "hypothetical_ops": hypothetical_ops,
                "hypothetical_ops_over_rho": round(hypothetical_ops / max(1, rho), 8),
                "shortfall_closed": min(value, shortfall),
            }
        )
    return out


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p963 = load_json(Path(args.p963))
    best = (p963.get("summary") or {}).get("best_public_rank4_completion") or {}
    if not best:
        raise ValueError("P963 has no public rank-4 completion to decompose")
    seed_selector = str(best.get("seed_selector"))
    seed = None
    for candidate in p963.get("seed_results") or []:
        if candidate.get("selector") == seed_selector:
            seed = candidate
            break
    if seed is None:
        raise ValueError(f"seed selector not found in P963 seed_results: {seed_selector}")
    row_keys = [str(row.get("row_key")) for row in seed.get("row_results") or []]
    verifier, pair, materialized = source_and_materialized(args, row_keys)
    seed_scenario = scenario_breakdown(verifier, materialized, pair, leaves_from_rows(seed.get("row_results") or []), "seed")
    completion_scenario = scenario_breakdown(
        verifier,
        materialized,
        pair,
        leaves_from_rows(best.get("row_results") or []),
        "rank4_completion",
    )
    delta = diff_components(seed_scenario, completion_scenario)
    rho = int_value(completion_scenario["union"].get("generic_rho_steps"))
    completion_ops = int_value(completion_scenario["union"].get("ops"))
    shortfall = max(0, completion_ops - rho)
    targets = reduction_targets(delta, completion_ops, rho)
    sufficient = [row for row in targets if int_value(row.get("component_delta")) >= shortfall and shortfall > 0]
    controls_pass = (
        int_value(seed_scenario["union"].get("ops")) == int_value(seed.get("ops"))
        and int_value(completion_scenario["union"].get("ops")) == int_value(best.get("ops"))
        and int_value(completion_scenario["union"].get("rank")) >= 4
        and all(row["breakdown"].get("matches_reported_ops") for row in seed_scenario.get("row_breakdowns") or [])
        and all(row["breakdown"].get("matches_reported_ops") for row in completion_scenario.get("row_breakdowns") or [])
    )
    claim = (
        "P964_COST_DECOMP_IDENTIFIES_SUFFICIENT_COMPONENT_TARGET"
        if controls_pass and sufficient
        else "NEGATIVE_RESULT_P964_NO_SINGLE_COMPONENT_CAN_CLOSE_GAP"
        if controls_pass
        else "NEGATIVE_RESULT_P964_COST_DECOMP_CONTROL_FAILURE"
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p963_result": str(args.p963),
            "script": str(Path(__file__)),
            "source": materialized.get("source_path"),
        },
        "claim_status": claim,
        "completion_scenario": completion_scenario,
        "component_delta": delta,
        "controls": {
            "completion_ops_matches_p963": int_value(completion_scenario["union"].get("ops")) == int_value(best.get("ops")),
            "controls_pass": controls_pass,
            "row_breakdowns_match_reported_ops": all(
                row["breakdown"].get("matches_reported_ops")
                for row in (seed_scenario.get("row_breakdowns") or []) + (completion_scenario.get("row_breakdowns") or [])
            ),
            "seed_ops_matches_p963": int_value(seed_scenario["union"].get("ops")) == int_value(seed.get("ops")),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "COST-DECOMPOSITION: this identifies accounting targets; it does not implement a cheaper algorithm.",
            "FIXED-PUBLIC: seed and completion use the P963 fixed public challenge.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this is local completion accounting, not full relation collection or target descent.",
        ],
        "method": "p964_rank_raising_leaf_cost_decomposition",
        "parameters": {
            "fixed_transfer": int(args.fixed_transfer),
            "p963": str(args.p963),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "p963_best_completion": best,
        "p963_seed": seed,
        "reduction_targets": targets,
        "row_component_delta": row_diffs(seed_scenario, completion_scenario),
        "schema": SCHEMA,
        "seed_scenario": seed_scenario,
        "summary": {
            "claim_status": claim,
            "completion_ops": completion_ops,
            "completion_ops_over_rho": completion_scenario["union"].get("ops_over_rho"),
            "component_delta": delta,
            "controls_pass": controls_pass,
            "rho": rho,
            "rho_shortfall": shortfall,
            "seed_ops": seed_scenario["union"].get("ops"),
            "sufficient_component_targets": sufficient,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p963", type=Path, default=DEFAULT_P963)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--top-k", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"controls_pass={summary['controls_pass']} "
        f"seed_ops={summary['seed_ops']} "
        f"completion_ops={summary['completion_ops']} "
        f"rho={summary['rho']} "
        f"shortfall={summary['rho_shortfall']} "
        f"sufficient_targets={len(summary['sufficient_component_targets'])} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
