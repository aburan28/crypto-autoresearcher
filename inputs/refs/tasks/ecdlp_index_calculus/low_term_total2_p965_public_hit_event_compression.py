#!/usr/bin/env python3
"""P965 public hit-event compression audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_critical_leaf_probe as critical_leaf_probe  # noqa: E402
import frontier_signed_eval_cover_dependency_circuit_probe as dependency_circuit_probe  # noqa: E402
import frontier_signed_eval_cover_preassociation_filter_probe as preassociation_filter_probe  # noqa: E402
import frontier_signed_eval_cover_projection_probe as eval_cover_probe  # noqa: E402
import frontier_signed_target_guided_probe  # noqa: E402
import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p965_public_hit_event_compression.md"
DEFAULT_P964 = STATE_DIR / "low_term_total2_p964_rank_raising_leaf_cost_decomposition_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p965_public_hit_event_compression_probe.json"
SCHEMA = "ecdlp.low_term_total2_p965_public_hit_event_compression.v1"


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


def term_shape(terms: list[int]) -> str:
    counts = sorted(Counter(int(term) for term in terms).values(), reverse=True)
    return "+".join(str(count) for count in counts)


def term_span(terms: list[int]) -> int | None:
    values = [int(term) for term in terms]
    if not values:
        return None
    return max(values) - min(values)


def public_derive(verifier: Any, built: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    return dependency_circuit_probe.public_derive_from_events(
        verifier,
        events,
        int(built["order"]),
        built["base"],
        built["public"],
        built["ainvs"],
        int(built["p"]),
    )


def seed_events(verifier: Any, materialized: dict[str, Any], seed: dict[str, Any]) -> list[dict[str, Any]]:
    events = []
    for row in seed.get("row_results") or []:
        row_key = str(row.get("row_key"))
        leaves = {int(leaf) for leaf in row.get("leaf_indices") or []}
        if not leaves:
            continue
        scan = p964.direct_witness_probe.scan_selected(
            verifier,
            materialized["built_by_row"][row_key],
            materialized["components_by_row"][row_key],
            leaves,
            materialized["local_args_by_row"][row_key],
        )
        for event in scan.get("relation_events") or []:
            item = dict(event)
            item["row_key"] = row_key
            events.append(item)
    return events


def compact_accepted_event(event: dict[str, Any], order: int) -> dict[str, Any]:
    summary = dependency_circuit_probe.event_summary(0, event, order)
    return {
        "factor_support": summary.get("factor_support"),
        "leaf_index": summary.get("leaf_index"),
        "q_coeff": summary.get("q_coeff"),
        "rhs": summary.get("rhs"),
        "term_shape": summary.get("term_shape"),
        "terms": summary.get("terms"),
    }


def collect_candidate_events(
    verifier: Any,
    built: dict[str, Any],
    components: dict[str, Any],
    selected: set[int],
    focus_leaf: int,
    local_args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p = int(built["p"])
    order = int(built["order"])
    cover = preassociation_filter_probe.filtered_leaf_gcd_association(
        built["scouts"],
        components,
        p,
        selected,
    )
    scheduled_rows = eval_cover_probe.schedule_rows(
        built["rows"],
        cover["row_hit_count"],
        int(built["scheduled_row_count"]),
    )
    ordered_scouts = eval_cover_probe.order_scouts(
        built["scouts"],
        cover["hits_by_scout"],
        scheduled_rows,
        str(built["scout_order"]),
    )
    scout_to_leaf = critical_leaf_probe.scout_leaf_map(components)
    scheduled_by_original = {int(row["original_trial"]): row for row in scheduled_rows}
    forms: list[tuple[Any, int, list[int]]] = []
    relations: list[dict[str, Any]] = []
    relation_events: list[dict[str, Any]] = []
    seen_forms: set[tuple[Any, int]] = set()
    candidate_events = []
    focus_event_index = 0
    for candidate_pos, scout in enumerate(ordered_scouts[: int(built["selected_limit"])], start=1):
        scout_pos = int(scout["scout_pos"])
        leaf_index = int(scout_to_leaf.get(scout_pos, -1))
        hit_rows = [
            scheduled_by_original[int(trial)]
            for trial in cover["hits_by_scout"].get(scout_pos, [])
            if int(trial) in scheduled_by_original
        ]
        candidate_point = verifier.add_points(scout["left"]["point"], scout["right"]["point"], built["ainvs"], p)
        for row in hit_rows:
            before_forms = len(forms)
            before_relations = len(relations)
            accepted = frontier_signed_target_guided_probe.add_relation_if_valid(
                verifier,
                built["challenge"],
                built["base"],
                built["public"],
                built["ainvs"],
                p,
                order,
                candidate_point,
                [int(index) for index in scout["unsigned_indices"]],
                row,
                forms,
                seen_forms,
                relations,
            )
            accepted_event = None
            if accepted:
                accepted_event = {
                    "candidate_pos": int(candidate_pos),
                    "form": forms[-1],
                    "form_index": before_forms,
                    "leaf_index": int(leaf_index),
                    "original_trial": int(row["original_trial"]),
                    "scheduled_trial": int(row["trial"]),
                    "scout_pos": int(scout_pos),
                }
                relation_events.append(accepted_event)
            if leaf_index != int(focus_leaf):
                continue
            focus_event_index += 1
            terms = [int(index) for index in scout["unsigned_indices"]]
            term_support = sorted(set(terms))
            event = {
                "accepted_new_relation": bool(accepted and len(relations) > before_relations),
                "accepted_relation": compact_accepted_event(accepted_event, order) if accepted_event else None,
                "candidate_pos": int(candidate_pos),
                "event_index": focus_event_index,
                "leaf_index": int(leaf_index),
                "original_trial": int(row["original_trial"]),
                "public_keys": {
                    "all": "all",
                    "row_x": int(row.get("x") or 0),
                    "scout_pos": int(scout_pos),
                    "scout_s3_root_product": int(scout.get("s3_root_product") or 0),
                    "scout_s3_root_sum": int(scout.get("s3_root_sum") or 0),
                    "scout_unsigned_indices": ",".join(str(term) for term in terms),
                    "term_shape": term_shape(terms),
                    "term_support": ",".join(str(term) for term in term_support),
                },
                "row_eval_cover_score": int(row.get("eval_cover_score") or 0),
                "row_x": int(row.get("x") or 0),
                "scheduled_trial": int(row["trial"]),
                "scout_features": {
                    "left_pos": int(scout.get("left_pos") or 0),
                    "left_x": int(scout.get("left_x") or 0),
                    "right_pos": int(scout.get("right_pos") or 0),
                    "right_x": int(scout.get("right_x") or 0),
                    "s3_root_product": int(scout.get("s3_root_product") or 0),
                    "s3_root_sum": int(scout.get("s3_root_sum") or 0),
                    "scout_pos": int(scout_pos),
                    "term_shape": term_shape(terms),
                    "term_span": term_span(terms),
                    "term_support_size": len(term_support),
                    "unsigned_indices": terms,
                    "x_gap": int(scout.get("x_gap") or 0),
                    "x_sum": int(scout.get("x_sum") or 0),
                },
            }
            if accepted_event:
                event["relation_event"] = accepted_event
            candidate_events.append(event)
    focus_accepted_relation_count = sum(1 for event in candidate_events if event.get("accepted_new_relation"))
    metadata = {
        "accepted_relation_count": focus_accepted_relation_count,
        "all_relation_event_count": len(relation_events),
        "candidate_event_count": len(candidate_events),
        "cover_selected_hit_roots": int(cover.get("selected_hit_root_values") or 0),
        "focus_leaf": int(focus_leaf),
        "focus_accepted_relation_count": focus_accepted_relation_count,
        "relation_events": relation_events,
        "selected": sorted(int(leaf) for leaf in selected),
    }
    return candidate_events, metadata


def completion_ops(seed_ops: int, non_event_marginal_ops: int, verification_events: int) -> int:
    return int(seed_ops) + int(non_event_marginal_ops) + 2 * int(verification_events)


def evaluate_event_set(
    verifier: Any,
    built: dict[str, Any],
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    processed_count: int,
    total_candidate_event_count: int,
    seed_ops: int,
    non_event_marginal_ops: int,
    rho: int,
    expected_secret: int,
    label: str,
) -> dict[str, Any]:
    accepted_events = [event["relation_event"] for event in candidate_events if event.get("relation_event")]
    derived = public_derive(verifier, built, base_events + accepted_events)
    ops = completion_ops(seed_ops, non_event_marginal_ops, processed_count)
    return {
        "accepted_relation_count": len(accepted_events),
        "below_rho": bool(ops < rho),
        "derived_secret": derived.get("derived_secret"),
        "label": label,
        "ops": ops,
        "ops_over_rho": round(ops / max(1, rho), 8),
        "processed_candidate_events": int(processed_count),
        "public_key_verified": bool(derived.get("public_key_verified")),
        "rank": int(derived.get("rank") or 0),
        "saved_verification_ops": 2 * (int(total_candidate_event_count) - int(processed_count)),
        "skipped_candidate_events": int(total_candidate_event_count) - int(processed_count),
        "success": bool(
            ops < rho
            and derived.get("public_key_verified")
            and int(derived.get("rank") or 0) >= 4
            and derived.get("derived_secret") == expected_secret
        ),
    }


def early_stop_result(
    verifier: Any,
    built: dict[str, Any],
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    seed_ops: int,
    non_event_marginal_ops: int,
    rho: int,
    expected_secret: int,
) -> dict[str, Any]:
    accepted_so_far = []
    for index, event in enumerate(candidate_events, start=1):
        if event.get("relation_event"):
            accepted_so_far.append(event)
        result = evaluate_event_set(
            verifier,
            built,
            base_events,
            accepted_so_far,
            index,
            len(candidate_events),
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
            "public_early_stop_on_derivation",
        )
        if result["public_key_verified"] and int(result["rank"]) >= 4 and result["derived_secret"] == expected_secret:
            result["stop_event"] = event
            return result
    result = evaluate_event_set(
        verifier,
        built,
        base_events,
        [event for event in candidate_events if event.get("relation_event")],
        len(candidate_events),
        len(candidate_events),
        seed_ops,
        non_event_marginal_ops,
        rho,
        expected_secret,
        "public_early_stop_on_derivation",
    )
    result["stop_event"] = None
    return result


def grouping_results(
    verifier: Any,
    built: dict[str, Any],
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    seed_ops: int,
    non_event_marginal_ops: int,
    rho: int,
    expected_secret: int,
) -> list[dict[str, Any]]:
    results = []
    policies = [
        "all",
        "scout_pos",
        "row_x",
        "term_shape",
        "term_support",
        "scout_unsigned_indices",
        "scout_s3_root_sum",
        "scout_s3_root_product",
    ]
    for policy in policies:
        grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for event in candidate_events:
            grouped[event["public_keys"][policy]].append(event)
        representatives = [events[0] for _key, events in sorted(grouped.items(), key=lambda item: str(item[0]))]
        representative_result = evaluate_event_set(
            verifier,
            built,
            base_events,
            representatives,
            len(representatives),
            len(candidate_events),
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
            f"representative_first_by_{policy}",
        )
        representative_result["group_count"] = len(grouped)
        representative_result["group_policy"] = policy
        representative_result["selector_kind"] = "representative"
        results.append(representative_result)
        shared_result = evaluate_event_set(
            verifier,
            built,
            base_events,
            candidate_events,
            len(grouped),
            len(candidate_events),
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
            f"group_share_by_{policy}",
        )
        shared_result["group_count"] = len(grouped)
        shared_result["group_policy"] = policy
        shared_result["selector_kind"] = "group_share"
        results.append(shared_result)
    results.sort(
        key=lambda row: (
            not bool(row.get("success")),
            not bool(row.get("public_key_verified")),
            -int(row.get("rank") or 0),
            int(row.get("ops") or 10**9),
            row.get("label") or "",
        )
    )
    return results


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p964_payload = load_json(Path(args.p964))
    seed = p964_payload["p963_seed"]
    completion = p964_payload["p963_best_completion"]
    row_keys = [str(row.get("row_key")) for row in seed.get("row_results") or []]
    verifier, pair, materialized = p964.source_and_materialized(args, row_keys)
    base_events = seed_events(verifier, materialized, seed)
    added = completion.get("added_leaves") or []
    if not added:
        raise ValueError("P964 completion has no added leaf")
    focus_row_key = str(added[0]["row_key"])
    focus_leaf = int(added[0]["leaf"])
    completion_leaves = p964.leaves_from_rows(completion.get("row_results") or [])
    built = materialized["built_by_row"][focus_row_key]
    components = materialized["components_by_row"][focus_row_key]
    local_args = materialized["local_args_by_row"][focus_row_key]
    candidate_events, candidate_metadata = collect_candidate_events(
        verifier,
        built,
        components,
        completion_leaves[focus_row_key],
        focus_leaf,
        local_args,
    )
    rho = int_value(completion.get("generic_rho_steps"))
    seed_ops = int_value(seed.get("ops"))
    full_ops = int_value(completion.get("ops"))
    full_added_verification_ops = 2 * len(candidate_events)
    non_event_marginal_ops = full_ops - seed_ops - full_added_verification_ops
    early = early_stop_result(
        verifier,
        built,
        base_events,
        candidate_events,
        seed_ops,
        non_event_marginal_ops,
        rho,
        int(args.expected_secret),
    )
    groups = grouping_results(
        verifier,
        built,
        base_events,
        candidate_events,
        seed_ops,
        non_event_marginal_ops,
        rho,
        int(args.expected_secret),
    )
    representative_successes = [row for row in groups if row.get("selector_kind") == "representative" and row.get("success")]
    group_share_successes = [row for row in groups if row.get("selector_kind") == "group_share" and row.get("success")]
    controls_pass = (
        len(candidate_events) == 6
        and full_ops == 132
        and seed_ops == 117
        and non_event_marginal_ops == 3
        and int_value(candidate_metadata.get("accepted_relation_count")) == 1
    )
    claim = (
        "P965_PUBLIC_EARLY_STOP_HIT_EVENT_COMPRESSION_BELOW_RHO"
        if controls_pass and early.get("success")
        else "P965_PUBLIC_REPRESENTATIVE_HIT_EVENT_COMPRESSION_BELOW_RHO"
        if controls_pass and representative_successes
        else "P965_PUBLIC_GROUP_SHARE_HIT_EVENT_COMPRESSION_TARGET"
        if controls_pass and group_share_successes
        else "NEGATIVE_RESULT_P965_PUBLIC_HIT_EVENT_COMPRESSION_NO_BELOW_RHO"
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p964_result": str(args.p964),
            "script": str(Path(__file__)),
            "source": materialized.get("source_path"),
        },
        "candidate_events": candidate_events,
        "candidate_metadata": candidate_metadata,
        "claim_status": claim,
        "controls": {
            "accepted_relation_count_is_one": int_value(candidate_metadata.get("accepted_relation_count")) == 1,
            "candidate_event_count_is_six": len(candidate_events) == 6,
            "controls_pass": controls_pass,
            "full_ops_matches_p964": full_ops == 132,
            "non_event_marginal_ops": non_event_marginal_ops,
            "seed_ops_matches_p964": seed_ops == 117,
        },
        "created_at": now_iso(),
        "early_stop_result": early,
        "grouping_results": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: this compresses one P964 fixed-public rank-raising leaf.",
            "PUBLIC-EARLY-STOP: derivation is checked against the public key, not hidden scalar knowledge.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this does not prove full relation collection or target descent.",
        ],
        "method": "p965_public_hit_event_compression",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "focus_leaf": focus_leaf,
            "focus_row_key": focus_row_key,
            "p964": str(args.p964),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "schema": SCHEMA,
        "summary": {
            "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
            "candidate_event_count": len(candidate_events),
            "claim_status": claim,
            "compressed_ops": early.get("ops"),
            "compressed_ops_over_rho": early.get("ops_over_rho"),
            "controls_pass": controls_pass,
            "early_stop_success": bool(early.get("success")),
            "full_completion_ops": full_ops,
            "full_completion_ops_over_rho": completion.get("ops_over_rho"),
            "non_event_marginal_ops": non_event_marginal_ops,
            "representative_success_count": len(representative_successes),
            "rho": rho,
            "saved_verification_ops": early.get("saved_verification_ops"),
            "seed_ops": seed_ops,
            "skipped_candidate_events": early.get("skipped_candidate_events"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p964", type=Path, default=DEFAULT_P964)
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
    print(
        f"claim={payload['claim_status']} "
        f"controls_pass={summary['controls_pass']} "
        f"candidate_events={summary['candidate_event_count']} "
        f"accepted={summary['accepted_added_relation_count']} "
        f"compressed_ops={summary['compressed_ops']} "
        f"compressed_ops_over_rho={summary['compressed_ops_over_rho']} "
        f"saved_verification_ops={summary['saved_verification_ops']} "
        f"early_success={summary['early_stop_success']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
