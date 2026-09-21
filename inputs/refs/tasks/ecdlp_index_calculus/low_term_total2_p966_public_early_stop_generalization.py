#!/usr/bin/env python3
"""P966 public early-stop generalization audit."""

from __future__ import annotations

import argparse
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
import low_term_total2_p963_rank3_completion_cost_audit as p963  # noqa: E402
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402
import low_term_total2_p965_public_hit_event_compression as p965  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p966_public_early_stop_generalization.md"
DEFAULT_P963 = STATE_DIR / "low_term_total2_p963_rank3_completion_cost_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p966_public_early_stop_generalization_probe.json"
SCHEMA = "ecdlp.low_term_total2_p966_public_early_stop_generalization.v1"
P965_SEED_SELECTOR = "mode_low_term_span_perrow1"
P965_ADDED_SIGNATURE = "salt203:0"


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


def row_short(row_key: str) -> str:
    return str(row_key).split(":")[-1]


def added_signature(added: list[dict[str, Any]]) -> str:
    return ",".join(f"{row_short(str(item.get('row_key')))}:{int_value(item.get('leaf'))}" for item in added)


def leaf_set_signature(rows: list[dict[str, Any]]) -> tuple[tuple[str, tuple[int, ...]], ...]:
    return tuple(
        sorted(
            (
                str(row.get("row_key")),
                tuple(sorted(int(leaf) for leaf in row.get("leaf_indices") or [])),
            )
            for row in rows
        )
    )


def completion_key(completion: dict[str, Any]) -> tuple[Any, ...]:
    return (
        completion.get("seed_selector"),
        completion.get("completion_mode"),
        completion.get("completion_scheme"),
        added_signature(completion.get("added_leaves") or []),
        leaf_set_signature(completion.get("row_results") or []),
    )


def completion_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int_value(row.get("ops"), 10**9),
        int_value(row.get("marginal_ops"), 10**9),
        row.get("seed_selector") or "",
        row.get("completion_mode") or "",
        row.get("completion_scheme") or "",
        added_signature(row.get("added_leaves") or []),
    )


def public_rank4_completions(p963_payload: dict[str, Any], expected_secret: int) -> list[dict[str, Any]]:
    out = []
    seen: set[tuple[Any, ...]] = set()
    for row in p963_payload.get("public_completion_results") or []:
        if not row.get("public_key_verified"):
            continue
        if int_value(row.get("rank")) < 4:
            continue
        if row.get("derived_secret") != expected_secret:
            continue
        key = completion_key(row)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    out.sort(key=completion_sort_key)
    return out


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "accepted_new_relation": bool(event.get("accepted_new_relation")),
        "accepted_relation": event.get("accepted_relation"),
        "event_index": int_value(event.get("event_index")),
        "global_event_index": int_value(event.get("global_event_index")),
        "leaf_index": int_value(event.get("leaf_index")),
        "original_trial": int_value(event.get("original_trial")),
        "public_keys": event.get("public_keys") or {},
        "row_key": event.get("row_key"),
        "row_short": event.get("row_short"),
        "scheduled_trial": int_value(event.get("scheduled_trial")),
    }


def collect_row_candidate_events(
    verifier: Any,
    built: dict[str, Any],
    components: dict[str, Any],
    selected: set[int],
    focus_leaves: set[int],
    row_key: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    p = int(built["p"])
    order = int(built["order"])
    cover = p965.preassociation_filter_probe.filtered_leaf_gcd_association(
        built["scouts"],
        components,
        p,
        selected,
    )
    scheduled_rows = p965.eval_cover_probe.schedule_rows(
        built["rows"],
        cover["row_hit_count"],
        int(built["scheduled_row_count"]),
    )
    ordered_scouts = p965.eval_cover_probe.order_scouts(
        built["scouts"],
        cover["hits_by_scout"],
        scheduled_rows,
        str(built["scout_order"]),
    )
    scout_to_leaf = p965.critical_leaf_probe.scout_leaf_map(components)
    scheduled_by_original = {int(row["original_trial"]): row for row in scheduled_rows}
    forms: list[tuple[Any, int, list[int]]] = []
    relations: list[dict[str, Any]] = []
    relation_events: list[dict[str, Any]] = []
    seen_forms: set[tuple[Any, int]] = set()
    candidate_events = []
    focus_event_index = 0
    short = row_short(row_key)
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
            accepted = p965.frontier_signed_target_guided_probe.add_relation_if_valid(
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
                    "row_key": row_key,
                    "scheduled_trial": int(row["trial"]),
                    "scout_pos": int(scout_pos),
                }
                relation_events.append(accepted_event)
            if leaf_index not in focus_leaves:
                continue
            focus_event_index += 1
            terms = [int(index) for index in scout["unsigned_indices"]]
            term_support = sorted(set(terms))
            event = {
                "accepted_new_relation": bool(accepted and len(relations) > before_relations),
                "accepted_relation": p965.compact_accepted_event(accepted_event, order) if accepted_event else None,
                "candidate_pos": int(candidate_pos),
                "event_index": focus_event_index,
                "leaf_index": int(leaf_index),
                "original_trial": int(row["original_trial"]),
                "public_keys": {
                    "all": "all",
                    "row_key": row_key,
                    "row_leaf": f"{row_key}:{leaf_index}",
                    "row_short": short,
                    "row_x": int(row.get("x") or 0),
                    "scout_pos": int(scout_pos),
                    "scout_s3_root_product": int(scout.get("s3_root_product") or 0),
                    "scout_s3_root_sum": int(scout.get("s3_root_sum") or 0),
                    "scout_unsigned_indices": ",".join(str(term) for term in terms),
                    "term_shape": p965.term_shape(terms),
                    "term_support": ",".join(str(term) for term in term_support),
                },
                "row_eval_cover_score": int(row.get("eval_cover_score") or 0),
                "row_key": row_key,
                "row_short": short,
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
                    "term_shape": p965.term_shape(terms),
                    "term_span": p965.term_span(terms),
                    "term_support_size": len(term_support),
                    "unsigned_indices": terms,
                    "x_gap": int(scout.get("x_gap") or 0),
                    "x_sum": int(scout.get("x_sum") or 0),
                },
            }
            if accepted_event:
                event["relation_event"] = accepted_event
            candidate_events.append(event)
    return candidate_events, {
        "all_relation_event_count": len(relation_events),
        "candidate_event_count": len(candidate_events),
        "cover_selected_hit_roots": int(cover.get("selected_hit_root_values") or 0),
        "focus_accepted_relation_count": sum(1 for event in candidate_events if event.get("accepted_new_relation")),
        "focus_leaves": sorted(focus_leaves),
        "relation_events": relation_events,
        "row_key": row_key,
        "selected": sorted(int(leaf) for leaf in selected),
    }


def collect_added_candidate_events(
    verifier: Any,
    materialized: dict[str, Any],
    completion_leaves: dict[str, set[int]],
    added: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    focus_by_row: dict[str, set[int]] = defaultdict(set)
    row_order = []
    for item in added:
        row_key = str(item.get("row_key"))
        if row_key not in focus_by_row:
            row_order.append(row_key)
        focus_by_row[row_key].add(int(item.get("leaf")))
    all_events = []
    row_metadata = []
    for row_key in row_order:
        events, metadata = collect_row_candidate_events(
            verifier,
            materialized["built_by_row"][row_key],
            materialized["components_by_row"][row_key],
            completion_leaves[row_key],
            focus_by_row[row_key],
            row_key,
        )
        row_metadata.append(metadata)
        all_events.extend(events)
    for index, event in enumerate(all_events, start=1):
        event["global_event_index"] = index
    return all_events, {
        "accepted_relation_count": sum(1 for event in all_events if event.get("accepted_new_relation")),
        "candidate_event_count": len(all_events),
        "row_metadata": row_metadata,
    }


def best_grouping_success(groups: list[dict[str, Any]]) -> dict[str, Any] | None:
    successes = [row for row in groups if row.get("success")]
    if not successes:
        return None
    successes.sort(key=lambda row: (int_value(row.get("ops"), 10**9), row.get("label") or ""))
    row = successes[0]
    return {
        "group_count": row.get("group_count"),
        "group_policy": row.get("group_policy"),
        "label": row.get("label"),
        "ops": row.get("ops"),
        "ops_over_rho": row.get("ops_over_rho"),
        "processed_candidate_events": row.get("processed_candidate_events"),
        "saved_verification_ops": row.get("saved_verification_ops"),
        "selector_kind": row.get("selector_kind"),
        "skipped_candidate_events": row.get("skipped_candidate_events"),
    }


def compact_early_result(early: dict[str, Any]) -> dict[str, Any]:
    return {
        "accepted_relation_count": early.get("accepted_relation_count"),
        "below_rho": bool(early.get("below_rho")),
        "derived_secret": early.get("derived_secret"),
        "ops": early.get("ops"),
        "ops_over_rho": early.get("ops_over_rho"),
        "processed_candidate_events": early.get("processed_candidate_events"),
        "public_key_verified": bool(early.get("public_key_verified")),
        "rank": early.get("rank"),
        "saved_verification_ops": early.get("saved_verification_ops"),
        "skipped_candidate_events": early.get("skipped_candidate_events"),
        "stop_event": compact_event(early["stop_event"]) if early.get("stop_event") else None,
        "success": bool(early.get("success")),
    }


def audit_completion(
    verifier: Any,
    materialized: dict[str, Any],
    seed: dict[str, Any],
    completion: dict[str, Any],
    expected_secret: int,
    event_cache: dict[tuple[Any, ...], tuple[list[dict[str, Any]], dict[str, Any]]],
    seed_event_cache: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    seed_selector = str(seed.get("selector"))
    if seed_selector not in seed_event_cache:
        seed_event_cache[seed_selector] = p965.seed_events(verifier, materialized, seed)
    base_events = seed_event_cache[seed_selector]
    added = completion.get("added_leaves") or []
    leaves = p964.leaves_from_rows(completion.get("row_results") or [])
    cache_key = (leaf_set_signature(completion.get("row_results") or []), added_signature(added))
    if cache_key not in event_cache:
        event_cache[cache_key] = collect_added_candidate_events(verifier, materialized, leaves, added)
    candidate_events, candidate_metadata = event_cache[cache_key]
    derive_row_key = str((completion.get("row_results") or [{}])[0].get("row_key"))
    built = materialized["built_by_row"][derive_row_key]
    rho = int_value(completion.get("generic_rho_steps"))
    seed_ops = int_value(seed.get("ops"))
    full_ops = int_value(completion.get("ops"))
    non_event_marginal_ops = full_ops - seed_ops - 2 * len(candidate_events)
    accounting_valid = len(candidate_events) > 0 and non_event_marginal_ops >= 0
    early = (
        p965.early_stop_result(
            verifier,
            built,
            base_events,
            candidate_events,
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
        )
        if accounting_valid
        else {
            "accepted_relation_count": 0,
            "below_rho": False,
            "ops": full_ops,
            "ops_over_rho": round(full_ops / max(1, rho), 8),
            "processed_candidate_events": len(candidate_events),
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    )
    groups = (
        p965.grouping_results(
            verifier,
            built,
            base_events,
            candidate_events,
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
        )
        if accounting_valid
        else []
    )
    signature = added_signature(added)
    is_p965_exact = seed_selector == P965_SEED_SELECTOR and signature == P965_ADDED_SIGNATURE and full_ops == 132
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": accounting_valid,
        "added_leaf_count": len(added),
        "added_signature": signature,
        "best_grouping_success": best_grouping_success(groups),
        "candidate_event_count": len(candidate_events),
        "candidate_event_signatures": [compact_event(event) for event in candidate_events],
        "completion_mode": completion.get("completion_mode"),
        "completion_scheme": completion.get("completion_scheme"),
        "early_stop": compact_early_result(early),
        "full_completion_ops": full_ops,
        "full_completion_ops_over_rho": completion.get("ops_over_rho"),
        "is_p965_exact": is_p965_exact,
        "non_event_marginal_ops": non_event_marginal_ops,
        "public_completion_rank": completion.get("rank"),
        "public_completion_verified": bool(completion.get("public_key_verified")),
        "rho": rho,
        "row_results": completion.get("row_results") or [],
        "seed_ops": seed_ops,
        "seed_ops_over_rho": seed.get("ops_over_rho"),
        "seed_selector": seed_selector,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    early_successes = [row for row in results if (row.get("early_stop") or {}).get("success")]
    p965_successes = [row for row in early_successes if row.get("is_p965_exact")]
    cross_seed_successes = [
        row
        for row in early_successes
        if row.get("seed_selector") != P965_SEED_SELECTOR or row.get("added_signature") != P965_ADDED_SIGNATURE
    ]
    distinct_success_seeds = sorted({str(row.get("seed_selector")) for row in early_successes})
    distinct_success_signatures = sorted({str(row.get("added_signature")) for row in early_successes})
    row_pair_keys = {
        tuple(sorted(row_short(str(item.get("row_key"))) for item in row.get("row_results") or []))
        for row in results
    }
    heldout_row_pair_count = len([key for key in row_pair_keys if key != ("salt203", "salt205")])
    claim = (
        "P966_PUBLIC_EARLY_STOP_GENERALIZES_ACROSS_SEED_SELECTORS_PARTIAL"
        if cross_seed_successes
        else "P966_REPRODUCES_P965_NO_CROSS_SEED_GENERALIZATION"
        if p965_successes
        else "NEGATIVE_RESULT_P966_PUBLIC_EARLY_STOP_NO_BELOW_RHO_GENERALIZATION"
    )
    best_success = None
    if early_successes:
        best_success = sorted(
            early_successes,
            key=lambda row: (
                int_value((row.get("early_stop") or {}).get("ops"), 10**9),
                row.get("seed_selector") or "",
                row.get("completion_mode") or "",
            ),
        )[0]
    return {
        "accounting_valid_count": sum(1 for row in results if row.get("accounting_valid")),
        "audited_completion_count": len(results),
        "best_success": {
            "added_signature": best_success.get("added_signature"),
            "completion_mode": best_success.get("completion_mode"),
            "completion_scheme": best_success.get("completion_scheme"),
            "early_stop": best_success.get("early_stop"),
            "seed_selector": best_success.get("seed_selector"),
        }
        if best_success
        else None,
        "claim_status": claim,
        "cross_seed_success_count": len(cross_seed_successes),
        "distinct_added_signature_count": len({str(row.get("added_signature")) for row in results}),
        "distinct_seed_count": len({str(row.get("seed_selector")) for row in results}),
        "distinct_success_added_signatures": distinct_success_signatures,
        "distinct_success_seeds": distinct_success_seeds,
        "early_success_count": len(early_successes),
        "heldout_row_pair_count": heldout_row_pair_count,
        "p965_exact_success_count": len(p965_successes),
        "row_pair_keys": ["+".join(key) for key in sorted(row_pair_keys)],
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p963_payload = load_json(Path(args.p963))
    completions = public_rank4_completions(p963_payload, int(args.expected_secret))
    if args.max_completions:
        completions = completions[: int(args.max_completions)]
    seed_by_selector = {str(row.get("selector")): row for row in p963_payload.get("seed_results") or []}
    if not completions:
        raise ValueError("P963 contains no public verified rank-4 completions to audit")
    first_seed = seed_by_selector[str(completions[0].get("seed_selector"))]
    row_keys = [str(row.get("row_key")) for row in first_seed.get("row_results") or []]
    verifier, _pair, materialized = p964.source_and_materialized(args, row_keys)
    event_cache: dict[tuple[Any, ...], tuple[list[dict[str, Any]], dict[str, Any]]] = {}
    seed_event_cache: dict[str, list[dict[str, Any]]] = {}
    results = []
    skipped = []
    for completion in completions:
        seed_selector = str(completion.get("seed_selector"))
        seed = seed_by_selector.get(seed_selector)
        if seed is None:
            skipped.append({"completion": completion_key(completion), "error": "seed_not_found"})
            continue
        results.append(
            audit_completion(
                verifier,
                materialized,
                seed,
                completion,
                int(args.expected_secret),
                event_cache,
                seed_event_cache,
            )
        )
    summary = summarize(results)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p963_result": str(args.p963),
            "p965_script": str(Path(p965.__file__)),
            "script": str(Path(__file__)),
            "source": materialized.get("source_path"),
        },
        "claim_status": summary["claim_status"],
        "completion_results": results,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: this audits P963 completions for one fixed public challenge.",
            "PUBLIC-EARLY-STOP: stopping uses rank and public-key verification, not hidden scalar selection.",
            "LIMITED-GENERALIZATION: P963 provides adjacent seed/completion variants but not held-out row pairs.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this does not prove full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p966_public_early_stop_generalization",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_completions": int(args.max_completions),
            "p963": str(args.p963),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "schema": SCHEMA,
        "skipped": skipped,
        "summary": summary,
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
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--max-completions", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"audited={summary['audited_completion_count']} "
        f"accounting_valid={summary['accounting_valid_count']} "
        f"early_success={summary['early_success_count']} "
        f"cross_seed_success={summary['cross_seed_success_count']} "
        f"distinct_success_seeds={len(summary['distinct_success_seeds'])} "
        f"heldout_row_pairs={summary['heldout_row_pair_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
