#!/usr/bin/env python3
"""P973 adjacent source-charge decomposition."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p961_fixed_public_hybrid_cost_squeeze as p961  # noqa: E402
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402
import low_term_total2_p966_public_early_stop_generalization as p966  # noqa: E402
import low_term_total2_p967_heldout_rank3_seed_early_stop as p967  # noqa: E402
import low_term_total2_p968_heldout_rank4_completion_from_p967 as p968  # noqa: E402
import low_term_total2_p969_heldout_rank3_seed_budget_rescue as p969  # noqa: E402
import low_term_total2_p970_rank4_from_p969_seed as p970  # noqa: E402
import low_term_total2_p972_adjacent_public_event_source_generation as p972  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p973_adjacent_source_charge_decomposition.md"
DEFAULT_P969 = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
DEFAULT_P972 = STATE_DIR / "low_term_total2_p972_adjacent_public_event_source_generation_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p973_adjacent_source_charge_decomposition_probe.json"
SCHEMA = "ecdlp.low_term_total2_p973_adjacent_source_charge_decomposition.v1"
COMPONENT_KEYS = [
    "selected_signed_pair_ops",
    "row_pool_prescan_ops",
    "product_leaf_ops",
    "selected_hit_root_ops",
    "selected_leaf_ops",
    "selected_hit_event_verification_ops",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def row_short(row_key: str) -> str:
    return str(row_key).rsplit(":", 1)[-1]


def row_keys_for_candidate(candidate: dict[str, Any]) -> list[str]:
    prefix = str(candidate["row_key"]).rsplit(":", 1)[0]
    return [f"{prefix}:{short}" for short in str(candidate["pair_key"]).split("+")]


def leaf_from_signature(signature: str) -> int:
    return int(str(signature).rsplit(":", 1)[-1])


def scout_fingerprint(built: dict[str, Any]) -> str:
    limit = int_value(built.get("selected_limit"), len(built.get("scouts") or []))
    sample = []
    for scout in (built.get("scouts") or [])[:limit]:
        sample.append(
            (
                int_value(scout.get("scout_pos")),
                tuple(int_value(item) for item in scout.get("unsigned_indices") or []),
                int_value(scout.get("s3_root_sum")),
                int_value(scout.get("s3_root_product")),
                int_value(scout.get("left_pos")),
                int_value(scout.get("right_pos")),
            )
        )
    return hashlib.sha256(repr(sample).encode()).hexdigest()[:16]


def compact_early(early: dict[str, Any]) -> dict[str, Any]:
    return {
        "accepted_relation_count": early.get("accepted_relation_count"),
        "below_rho": bool(early.get("below_rho")),
        "derived_secret": early.get("derived_secret"),
        "ops": early.get("ops"),
        "ops_over_rho": early.get("ops_over_rho"),
        "processed_candidate_events": early.get("processed_candidate_events"),
        "public_key_verified": bool(early.get("public_key_verified")),
        "rank": early.get("rank"),
        "success": bool(early.get("success")),
    }


def adjusted_ops(seed_ops: int, non_event_ops: int, processed_events: int, rho: int) -> dict[str, Any]:
    ops = seed_ops + non_event_ops + 2 * processed_events
    return {
        "below_rho": bool(ops < rho),
        "ops": ops,
        "ops_over_rho": round(ops / max(1, rho), 8),
    }


def component_sum(rows: list[dict[str, Any]], key: str = "breakdown") -> dict[str, int]:
    out = {component: 0 for component in COMPONENT_KEYS}
    for row in rows:
        breakdown = row.get(key) or {}
        for component in COMPONENT_KEYS:
            out[component] += int_value(breakdown.get(component))
    out["total_ops"] = sum(out[component] for component in COMPONENT_KEYS)
    out["source_non_event_ops"] = out["total_ops"] - out["selected_hit_event_verification_ops"]
    return out


class Materializer:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.cache: dict[tuple[str, ...], tuple[Any, dict[str, Any], dict[str, Any]]] = {}

    def get(self, row_keys: list[str]) -> tuple[Any, dict[str, Any], dict[str, Any]]:
        key = tuple(sorted(str(row_key) for row_key in row_keys))
        if key not in self.cache:
            self.cache[key] = p964.source_and_materialized(self.args, list(key))
        return self.cache[key]


def direct_breakdown(
    verifier: Any,
    materialized: dict[str, Any],
    row_key: str,
    leaves: set[int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    scan = p964.direct_witness_probe.scan_selected(
        verifier,
        materialized["built_by_row"][row_key],
        materialized["components_by_row"][row_key],
        leaves,
        materialized["local_args_by_row"][row_key],
    )
    breakdown = p964.cost_breakdown_for_scan(
        materialized["built_by_row"][row_key],
        materialized["local_args_by_row"][row_key],
        scan,
    )
    return scan, breakdown


def scan_leaf_candidate(
    args: argparse.Namespace,
    materializer: Materializer,
    reconstructed: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    row_key = str(candidate["row_key"])
    leaf = leaf_from_signature(str(candidate["added_signature"]))
    verifier, pair, materialized = materializer.get(row_keys_for_candidate(candidate))
    scan, breakdown = direct_breakdown(verifier, materialized, row_key, {leaf})
    leaves = {row_key: {leaf}}
    added = [{"leaf": leaf, "row_key": row_key}]
    candidate_events, metadata = p966.collect_added_candidate_events(verifier, materialized, leaves, added)
    seed_ops = int_value((reconstructed["compressed_seed"]).get("ops"))
    rho = int_value((reconstructed["compressed_seed"]).get("generic_rho_steps"))
    processed_events = int_value((candidate.get("early_stop") or {}).get("processed_candidate_events"))
    source_non_event = int_value(breakdown.get("total_ops")) - 2 * len(candidate_events)
    after_signed_pair = max(0, source_non_event - int_value(breakdown.get("selected_signed_pair_ops")))
    after_all_non_event = 0
    built = materialized["built_by_row"][row_key]
    return {
        "accepted_added_relation_count": metadata.get("accepted_relation_count"),
        "added_signature": candidate.get("added_signature"),
        "breakdown": breakdown,
        "candidate_event_count": len(candidate_events),
        "component_matches_reported": bool(breakdown.get("matches_reported_ops")),
        "early_stop": compact_early(candidate.get("early_stop") or {}),
        "event_count_ge4": bool(candidate.get("event_count_ge4")),
        "full_source_ops": breakdown.get("total_ops"),
        "pair_key": candidate.get("pair_key"),
        "rank4_verified": bool(candidate.get("rank4_verified")),
        "row_key": row_key,
        "row_short": row_short(row_key),
        "scout_fingerprint": scout_fingerprint(built),
        "selected_limit": built.get("selected_limit"),
        "selected_signed_pair_count": built.get("selected_signed_pair_count"),
        "source_non_event_ops": source_non_event,
        "one_shot_after_selected_signed_pair_reuse": adjusted_ops(seed_ops, after_signed_pair, processed_events, rho),
        "one_shot_after_full_non_event_cache": adjusted_ops(seed_ops, after_all_non_event, processed_events, rho),
        "selected_leaf_scan": p968.compact_scan(scan),
    }


def group_candidates(
    args: argparse.Namespace,
    materializer: Materializer,
    reconstructed: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        grouped[(str(candidate["pair_key"]), str(candidate["row_key"]))].append(candidate)
    out = []
    base_row_key = p967.row_keys(reconstructed["compressed_seed"])[0]
    base_built = reconstructed["materialized"]["built_by_row"][base_row_key]
    seed_ops = int_value(reconstructed["compressed_seed"].get("ops"))
    rho = int_value(reconstructed["compressed_seed"].get("generic_rho_steps"))
    for (pair_key, row_key), rows in sorted(grouped.items()):
        verifier, pair, materialized = materializer.get(row_keys_for_candidate(rows[0]))
        leaves = {row_key: {leaf_from_signature(str(row["added_signature"])) for row in rows}}
        added = [{"leaf": leaf, "row_key": row_key} for leaf in sorted(leaves[row_key])]
        scan, breakdown = direct_breakdown(verifier, materialized, row_key, set(leaves[row_key]))
        union = p961.scan_from_leaves(verifier, materialized, pair, leaves, f"p973_group:{pair_key}:{row_short(row_key)}", "p973_group")
        candidate_events, metadata = p966.collect_added_candidate_events(verifier, materialized, leaves, added)
        non_event = int_value(union.get("ops")) - 2 * len(candidate_events)
        early = p967.evaluate_rank_threshold(
            verifier,
            base_built,
            reconstructed["base_events"],
            candidate_events,
            seed_ops,
            non_event,
            rho,
            int(args.expected_secret),
            4,
        )
        single_sum = component_sum(rows)
        savings = {
            component: single_sum.get(component, 0) - int_value(breakdown.get(component))
            for component in COMPONENT_KEYS
        }
        savings["total_ops"] = single_sum.get("total_ops", 0) - int_value(breakdown.get("total_ops"))
        return_row = {
            "accepted_added_relation_count": metadata.get("accepted_relation_count"),
            "added_signatures": [row.get("added_signature") for row in rows],
            "breakdown": breakdown,
            "candidate_event_count": len(candidate_events),
            "early_stop": compact_early(early),
            "group_full_source_ops": union.get("ops"),
            "group_source_non_event_ops": non_event,
            "leaves": sorted(leaves[row_key]),
            "pair_key": pair_key,
            "row_key": row_key,
            "row_short": row_short(row_key),
            "savings_vs_single_scans": savings,
            "scout_fingerprint": scout_fingerprint(materialized["built_by_row"][row_key]),
            "single_scan_component_sum": single_sum,
            "union_scan": p968.compact_scan(union),
        }
        out.append(return_row)
    return out


def global_signed_pair_reuse_bound(groups: list[dict[str, Any]]) -> dict[str, Any]:
    totals = component_sum(groups)
    by_fingerprint: dict[str, list[int]] = defaultdict(list)
    for group in groups:
        by_fingerprint[str(group.get("scout_fingerprint"))].append(
            int_value((group.get("breakdown") or {}).get("selected_signed_pair_ops"))
        )
    saved = 0
    for values in by_fingerprint.values():
        if not values:
            continue
        saved += sum(values) - max(values)
    adjusted_total = totals["total_ops"] - saved
    adjusted_non_event = totals["source_non_event_ops"] - saved
    return {
        "actual_grouped_component_totals": totals,
        "global_signed_pair_saved_ops": saved,
        "scout_fingerprint_count": len(by_fingerprint),
        "signed_pair_reuse_total_ops": adjusted_total,
        "signed_pair_reuse_source_non_event_ops": adjusted_non_event,
    }


def portfolio_summary(name: str, candidates: list[dict[str, Any]], groups: list[dict[str, Any]], rho: int) -> dict[str, Any]:
    singles = component_sum(candidates)
    grouped = component_sum(groups)
    reuse = global_signed_pair_reuse_bound(groups)
    return {
        "actual_grouped_savings_vs_single": singles["total_ops"] - grouped["total_ops"],
        "actual_grouped_total_ops": grouped["total_ops"],
        "actual_grouped_total_ops_below_single_rho_budget": bool(grouped["total_ops"] < rho),
        "candidate_count": len(candidates),
        "name": name,
        "same_row_group_count": len(groups),
        "signed_pair_reuse_total_ops": reuse["signed_pair_reuse_total_ops"],
        "signed_pair_reuse_total_ops_below_single_rho_budget": bool(reuse["signed_pair_reuse_total_ops"] < rho),
        "single_scan_total_ops": singles["total_ops"],
        "single_scan_total_source_non_event_ops": singles["source_non_event_ops"],
        "source_rho": rho,
        **reuse,
    }


def rank4_candidates(p972_payload: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in p972_payload.get("candidate_results") or [] if row.get("rank4_verified")]


def summarize(
    reconstructed: dict[str, Any],
    single_breakdowns: list[dict[str, Any]],
    all_groups: list[dict[str, Any]],
    event_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    rho = int_value(reconstructed["compressed_seed"].get("generic_rho_steps"))
    event_candidates = [row for row in single_breakdowns if row.get("event_count_ge4")]
    all_portfolio = portfolio_summary("all_rank4", single_breakdowns, all_groups, rho)
    event_portfolio = portfolio_summary("event_count_ge4_rank4", event_candidates, event_groups, rho)
    selected_signed_removal = [
        row for row in single_breakdowns if (row.get("one_shot_after_selected_signed_pair_reuse") or {}).get("below_rho")
    ]
    full_cache = [
        row for row in single_breakdowns if (row.get("one_shot_after_full_non_event_cache") or {}).get("below_rho")
    ]
    claim = (
        "P973_SHARED_SIGNED_PAIR_BATCH_SOURCE_BOUND_BELOW_RHO_NOT_ONE_SHOT"
        if all_portfolio["signed_pair_reuse_total_ops_below_single_rho_budget"]
        and event_portfolio["signed_pair_reuse_total_ops_below_single_rho_budget"]
        and not selected_signed_removal
        else "P973_ACTUAL_GROUPING_SAVES_COST_WITHOUT_SOURCE_RHO_BOUND"
        if all_portfolio["actual_grouped_savings_vs_single"] > 0
        else "NEGATIVE_RESULT_P973_NO_SHAREABLE_SOURCE_COMPONENT"
    )
    return {
        "actual_same_row_group_savings": all_portfolio["actual_grouped_savings_vs_single"],
        "all_rank4_portfolio": all_portfolio,
        "claim_status": claim,
        "component_match_count": sum(1 for row in single_breakdowns if row.get("component_matches_reported")),
        "event_count_rank4_portfolio": event_portfolio,
        "rank4_candidate_count": len(single_breakdowns),
        "scout_fingerprint_count": len({row.get("scout_fingerprint") for row in single_breakdowns}),
        "single_full_non_event_cache_below_rho_count": len(full_cache),
        "single_selected_signed_pair_reuse_below_rho_count": len(selected_signed_removal),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p969_payload = load_json(Path(args.p969))
    p972_payload = load_json(Path(args.p972))
    reconstructed = p970.reconstruct_p969_seed(args, p969_payload)
    if not (reconstructed.get("control") or {}).get("control_pass"):
        raise ValueError(f"P969 reconstruction failed: {reconstructed.get('control')!r}")
    materializer = Materializer(args)
    rank4 = rank4_candidates(p972_payload)
    single_breakdowns = [
        scan_leaf_candidate(args, materializer, reconstructed, candidate)
        for candidate in rank4
    ]
    event_candidates = [row for row in single_breakdowns if row.get("event_count_ge4")]
    all_groups = group_candidates(args, materializer, reconstructed, single_breakdowns)
    event_groups = group_candidates(args, materializer, reconstructed, event_candidates)
    summary = summarize(reconstructed, single_breakdowns, all_groups, event_groups)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p969_result": str(args.p969),
            "p972_result": str(args.p972),
            "script": str(Path(__file__)),
            "source": reconstructed["materialized"].get("source_path"),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "frontier_seed": {
            "compressed_rank3_seed": p969.compact_result(reconstructed["compressed_seed"]),
            "p969_added": reconstructed["p969_added"],
            "reconstruction_control": reconstructed["control"],
        },
        "group_breakdowns": {
            "all_rank4": all_groups,
            "event_count_ge4_rank4": event_groups,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "COMPONENT-ACCOUNTING: this decomposes existing source scans; it does not implement a new verifier backend.",
            "BATCH-SOURCE-BOUNDARY: signed-pair reuse bounds are source-generation batch bounds, not one-shot ECDLP wins.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: rank-4 source rows are still local relation-generation evidence.",
        ],
        "method": "p973_adjacent_source_charge_decomposition",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "p969": str(args.p969),
            "p972": str(args.p972),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "rank4_candidate_breakdowns": single_breakdowns,
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p969", type=Path, default=DEFAULT_P969)
    parser.add_argument("--p972", type=Path, default=DEFAULT_P972)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    all_portfolio = summary["all_rank4_portfolio"]
    event_portfolio = summary["event_count_rank4_portfolio"]
    print(
        f"claim={payload['claim_status']} "
        f"rank4={summary['rank4_candidate_count']} "
        f"component_matches={summary['component_match_count']} "
        f"fingerprints={summary['scout_fingerprint_count']} "
        f"actual_savings={summary['actual_same_row_group_savings']} "
        f"all_signed_pair_bound={all_portfolio['signed_pair_reuse_total_ops']} "
        f"event_signed_pair_bound={event_portfolio['signed_pair_reuse_total_ops']} "
        f"one_shot_signed_pair_below={summary['single_selected_signed_pair_reuse_below_rho_count']} "
        f"full_non_event_cache_below={summary['single_full_non_event_cache_below_rho_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
