#!/usr/bin/env python3
"""P972 adjacent public-event source-generation audit."""

from __future__ import annotations

import argparse
import json
import sys
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
import low_term_total2_p963_rank3_completion_cost_audit as p963  # noqa: E402
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402
import low_term_total2_p966_public_early_stop_generalization as p966  # noqa: E402
import low_term_total2_p967_heldout_rank3_seed_early_stop as p967  # noqa: E402
import low_term_total2_p968_heldout_rank4_completion_from_p967 as p968  # noqa: E402
import low_term_total2_p969_heldout_rank3_seed_budget_rescue as p969  # noqa: E402
import low_term_total2_p970_rank4_from_p969_seed as p970  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p972_adjacent_public_event_source_generation.md"
DEFAULT_P969 = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
DEFAULT_P970 = STATE_DIR / "low_term_total2_p970_rank4_from_p969_seed_probe.json"
DEFAULT_P971 = STATE_DIR / "low_term_total2_p971_public_single_row_selector_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p972_adjacent_public_event_source_generation_probe.json"
SCHEMA = "ecdlp.low_term_total2_p972_adjacent_public_event_source_generation.v1"


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


def salt_number(row_key: str) -> int | None:
    short = row_short(row_key)
    if not short.startswith("salt"):
        return None
    try:
        return int(short.removeprefix("salt"))
    except ValueError:
        return None


def short_pair(row_keys: list[str]) -> str:
    return "+".join(row_short(key) for key in row_keys)


def same_public_context(base_built: dict[str, Any], candidate_built: dict[str, Any]) -> bool:
    return tuple(int(value) for value in base_built.get("public") or []) == tuple(
        int(value) for value in candidate_built.get("public") or []
    )


def p971_rule_names(p971_payload: dict[str, Any]) -> list[str]:
    names = []
    for score in p971_payload.get("rule_scores") or []:
        name = score.get("rule_name")
        if name:
            names.append(str(name))
    return names


def p970_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"available": False}
    payload = load_json(path)
    summary = payload.get("summary") or {}
    return {
        "available": True,
        "claim_status": payload.get("claim_status"),
        "public_rank4_count": summary.get("public_rank4_count"),
        "oracle_rank4_count": summary.get("oracle_rank4_count"),
        "full_scan_rank4_count": summary.get("full_scan_rank4_count"),
    }


def adjacent_pairs(args: argparse.Namespace) -> list[dict[str, Any]]:
    _cases, pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    out = []
    for pair in pairs:
        row_keys = [str(key) for key in pair.get("row_keys") or []]
        salts = [salt_number(key) for key in row_keys]
        if len(row_keys) != 2 or any(value is None for value in salts):
            continue
        if not all(int(args.salt_min) <= int(value) <= int(args.salt_max) for value in salts if value is not None):
            continue
        out.append(pair)
    if int(args.max_pairs) > 0:
        out = out[: int(args.max_pairs)]
    return out


def fallback_early(seed_ops: int, non_event_ops: int, rho: int) -> dict[str, Any]:
    ops = seed_ops + max(0, non_event_ops)
    return {
        "accepted_relation_count": 0,
        "below_rho": False,
        "derived_secret": None,
        "ops": ops,
        "ops_over_rho": round(ops / max(1, rho), 8),
        "processed_candidate_events": 0,
        "public_key_verified": False,
        "rank": 0,
        "saved_verification_ops": 0,
        "skipped_candidate_events": 0,
        "stop_event": None,
        "success": False,
    }


def first_public_event(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not events:
        return {}
    return (events[0] or {}).get("public_keys") or {}


def compact_candidate(row: dict[str, Any]) -> dict[str, Any]:
    early = row.get("early_stop") or {}
    return {
        "accepted_added_relation_count": row.get("accepted_added_relation_count"),
        "added_signature": row.get("added_signature"),
        "candidate_event_count": row.get("candidate_event_count"),
        "early_ops": early.get("ops"),
        "early_rank": early.get("rank"),
        "event_count_ge4": row.get("event_count_ge4"),
        "first_event": row.get("first_event") or {},
        "full_source_ops": row.get("full_source_ops"),
        "pair_key": row.get("pair_key"),
        "p971_full_screen_pass": row.get("p971_full_screen_pass"),
        "rank4_verified": row.get("rank4_verified"),
        "rank4_below_rho": row.get("rank4_below_rho"),
        "row_short": row.get("row_short"),
        "seed_ops": row.get("seed_ops"),
        "source_non_event_ops": row.get("source_non_event_ops"),
        "source_non_event_excess_over_below_rho": row.get("source_non_event_excess_over_below_rho"),
    }


def best_candidate_key(row: dict[str, Any]) -> tuple[Any, ...]:
    early = row.get("early_stop") or {}
    return (
        not bool(row.get("rank4_verified")),
        not bool(row.get("event_count_ge4")),
        int_value(row.get("source_non_event_ops"), 10**9),
        int_value(early.get("ops"), 10**9),
        -(int_value(row.get("source_support_count"))),
        row.get("pair_key") or "",
    )


def evaluate_candidate(
    args: argparse.Namespace,
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    base_built: dict[str, Any],
    base_events: list[dict[str, Any]],
    compressed_seed: dict[str, Any],
    row_key: str,
    leaf: int,
) -> dict[str, Any]:
    leaves = {row_key: {int(leaf)}}
    added = [{"leaf": int(leaf), "row_key": row_key}]
    scan = p961.scan_from_leaves(
        verifier,
        materialized,
        pair,
        leaves,
        f"p972_adjacent:{row_short(row_key)}:{leaf}",
        "p972_adjacent_single_leaf",
    )
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(verifier, materialized, leaves, added)
    seed_ops = int_value(compressed_seed.get("ops"))
    rho = int_value(compressed_seed.get("generic_rho_steps"))
    full_source_ops = int_value(scan.get("ops"))
    source_non_event_ops = full_source_ops - 2 * len(candidate_events)
    candidate_built = materialized["built_by_row"][row_key]
    context_ok = same_public_context(base_built, candidate_built)
    if context_ok and source_non_event_ops >= 0:
        early = p967.evaluate_rank_threshold(
            verifier,
            base_built,
            base_events,
            candidate_events,
            seed_ops,
            source_non_event_ops,
            rho,
            int(args.expected_secret),
            4,
        )
    else:
        early = fallback_early(seed_ops, source_non_event_ops, rho)
    processed = int_value(early.get("processed_candidate_events"))
    max_non_event_for_below_rho = rho - 1 - seed_ops - 2 * processed
    rank4_verified = (
        bool(early.get("public_key_verified"))
        and int_value(early.get("rank")) >= 4
        and early.get("derived_secret") == int(args.expected_secret)
    )
    event_count_ge4 = len(candidate_events) >= 4
    low_source_non_event = source_non_event_ops <= int(args.max_p971_non_event_ops)
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": bool(context_ok and source_non_event_ops >= 0),
        "added_signature": p966.added_signature(added),
        "candidate_event_count": len(candidate_events),
        "candidate_event_signatures": [p966.compact_event(event) for event in candidate_events],
        "event_count_ge4": event_count_ge4,
        "first_event": first_public_event(candidate_events),
        "full_source_ops": full_source_ops,
        "full_source_scan": p968.compact_scan(scan),
        "low_source_non_event": low_source_non_event,
        "max_non_event_for_below_rho": max_non_event_for_below_rho,
        "pair_key": short_pair([str(key) for key in pair.get("row_keys") or []]),
        "p971_event_count_screen_pass": bool(event_count_ge4 and seed_ops <= int(args.max_seed_ops)),
        "p971_full_screen_pass": bool(
            seed_ops <= int(args.max_seed_ops)
            and event_count_ge4
            and source_non_event_ops <= int(args.max_p971_non_event_ops)
        ),
        "public_context_ok": context_ok,
        "rank4_below_rho": bool((early.get("success"))),
        "rank4_verified": rank4_verified,
        "rho": rho,
        "row_key": row_key,
        "row_short": row_short(row_key),
        "salt": salt_number(row_key),
        "seed_ops": seed_ops,
        "source_non_event_excess_over_below_rho": source_non_event_ops - max_non_event_for_below_rho,
        "source_non_event_ops": source_non_event_ops,
        "source_support_count": pair.get("source_support_count"),
        "early_stop": early,
    }


def audit_adjacent_candidates(args: argparse.Namespace, reconstructed: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    compressed_seed = reconstructed["compressed_seed"]
    base_events = reconstructed["base_events"]
    base_row_key = p967.row_keys(compressed_seed)[0]
    base_built = reconstructed["materialized"]["built_by_row"][base_row_key]
    seed_leaves = {
        (str(row_key), int(leaf))
        for row_key, leaves in (reconstructed.get("seed_leaves") or {}).items()
        for leaf in leaves
    }
    by_leaf: dict[tuple[str, int], dict[str, Any]] = {}
    errors = []
    materialized_pair_count = 0
    for pair in adjacent_pairs(args):
        row_keys = [str(key) for key in pair.get("row_keys") or []]
        try:
            verifier, materialized_pair, materialized = p964.source_and_materialized(args, row_keys)
            materialized_pair_count += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"error": str(exc), "pair_key": short_pair(row_keys)})
            continue
        if materialized.get("errors"):
            errors.append({"errors": materialized.get("errors"), "pair_key": short_pair(row_keys)})
        for row in materialized["selected_rows"]:
            row_key = str(p963.leaf_public_probe.row_key(row))
            salt = salt_number(row_key)
            if salt is None or not (int(args.salt_min) <= salt <= int(args.salt_max)):
                continue
            for leaf in sorted(p963.candidate_leaf_set(row)):
                if (row_key, int(leaf)) in seed_leaves:
                    continue
                candidate = evaluate_candidate(
                    args,
                    verifier,
                    materialized,
                    materialized_pair,
                    base_built,
                    base_events,
                    compressed_seed,
                    row_key,
                    int(leaf),
                )
                key = (row_key, int(leaf))
                if key not in by_leaf or best_candidate_key(candidate) < best_candidate_key(by_leaf[key]):
                    by_leaf[key] = candidate
    candidates = list(by_leaf.values())
    candidates.sort(
        key=lambda row: (
            not bool(row.get("rank4_verified")),
            not bool(row.get("event_count_ge4")),
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            int_value(row.get("source_non_event_ops"), 10**9),
            row.get("row_short") or "",
            int_value((row.get("first_event") or {}).get("scout_pos"), 10**9),
        )
    )
    return candidates, errors, materialized_pair_count


def summarize(candidates: list[dict[str, Any]], reconstructed: dict[str, Any]) -> dict[str, Any]:
    rank4 = [row for row in candidates if row.get("rank4_verified")]
    rank4_below = [row for row in rank4 if row.get("rank4_below_rho")]
    event_ge4 = [row for row in candidates if row.get("event_count_ge4")]
    event_ge4_rank4 = [row for row in event_ge4 if row.get("rank4_verified")]
    full_screen = [row for row in candidates if row.get("p971_full_screen_pass")]
    full_screen_rank4 = [row for row in full_screen if row.get("rank4_verified")]
    best_rank4 = sorted(
        rank4,
        key=lambda row: (
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            int_value(row.get("source_non_event_excess_over_below_rho"), 10**9),
            row.get("added_signature") or "",
        ),
    )[0] if rank4 else None
    best_event_rank4 = sorted(
        event_ge4_rank4,
        key=lambda row: (
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            row.get("added_signature") or "",
        ),
    )[0] if event_ge4_rank4 else None
    claim = (
        "P972_PUBLIC_EVENT_SCREEN_SELECTS_RANK4_BELOW_RHO"
        if any(row.get("rank4_below_rho") for row in full_screen_rank4)
        else "P972_ADJACENT_PUBLIC_EVENT_COUNT_GENERATES_RANK4_SOURCE_SIGNAL_COST_GAP"
        if event_ge4_rank4
        else "P972_ADJACENT_SOURCE_ROWS_GENERATE_RANK4_COST_GAP_EVENT_SCREEN_WEAK"
        if rank4
        else "NEGATIVE_RESULT_P972_NO_ADJACENT_RANK4_SOURCE_SIGNAL"
    )
    compressed = reconstructed["compressed_seed"]
    return {
        "best_event_count_rank4": compact_candidate(best_event_rank4) if best_event_rank4 else None,
        "best_rank4": compact_candidate(best_rank4) if best_rank4 else None,
        "candidate_count": len(candidates),
        "claim_status": claim,
        "event_count_ge4_count": len(event_ge4),
        "event_count_ge4_rank4_count": len(event_ge4_rank4),
        "p969_control_pass": bool((reconstructed.get("control") or {}).get("control_pass")),
        "p971_full_screen_pass_count": len(full_screen),
        "p971_full_screen_rank4_count": len(full_screen_rank4),
        "rank4_below_rho_count": len(rank4_below),
        "rank4_verified_count": len(rank4),
        "rank4_verified_rows": [compact_candidate(row) for row in rank4],
        "seed_ops": compressed.get("ops"),
        "seed_rank": compressed.get("rank"),
        "seed_rho": compressed.get("generic_rho_steps"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p969_payload = load_json(Path(args.p969))
    p971_payload = load_json(Path(args.p971)) if Path(args.p971).exists() else {}
    reconstructed = p970.reconstruct_p969_seed(args, p969_payload)
    if not (reconstructed.get("control") or {}).get("control_pass"):
        raise ValueError(f"P969 reconstruction failed: {reconstructed.get('control')!r}")
    candidates, errors, materialized_pair_count = audit_adjacent_candidates(args, reconstructed)
    summary = summarize(candidates, reconstructed)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p969_result": str(args.p969),
            "p970_result": str(args.p970),
            "p971_result": str(args.p971),
            "script": str(Path(__file__)),
            "source": reconstructed["materialized"].get("source_path"),
        },
        "candidate_results": candidates,
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "frontier_seed": {
            "compressed_rank3_seed": p969.compact_result(reconstructed["compressed_seed"]),
            "p969_added": reconstructed["p969_added"],
            "rank2_seed": p969.compact_result(reconstructed["rank2_seed"]),
            "reconstruction_control": reconstructed["control"],
            "seed_leaves": p968.compact_leaves(reconstructed["seed_leaves"]),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "SOURCE-GENERATION-SIGNAL: rank-4 transitions here are component evidence for relation sourcing, not a full index-calculus algorithm.",
            "PUBLIC-FEATURE-SEPARATION: public event counts and source costs are used for screens; accepted relations and rank are scoring labels.",
            "NOT-BELOW-RHO-IF-COST-GAP: fresh adjacent row-source scans are fully charged, so above-rho rank-4 transitions are not speedups.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this audit stops at local rank-4 verifier evidence.",
        ],
        "materialization": {
            "errors": errors,
            "materialized_pair_count": materialized_pair_count,
        },
        "method": "p972_adjacent_public_event_source_generation",
        "parameters": {
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_p971_non_event_ops": int(args.max_p971_non_event_ops),
            "max_seed_ops": int(args.max_seed_ops),
            "p969": str(args.p969),
            "p970_baseline": p970_summary(Path(args.p970)),
            "p971_rule_names": p971_rule_names(p971_payload),
            "post_min": int(args.post_min),
            "salt_max": int(args.salt_max),
            "salt_min": int(args.salt_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "schema": SCHEMA,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", type=Path, default=STATE_DIR)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p969", type=Path, default=DEFAULT_P969)
    parser.add_argument("--p970", type=Path, default=DEFAULT_P970)
    parser.add_argument("--p971", type=Path, default=DEFAULT_P971)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--salt-min", type=int, default=201)
    parser.add_argument("--salt-max", type=int, default=209)
    parser.add_argument("--max-pairs", type=int, default=0)
    parser.add_argument("--max-seed-ops", type=int, default=122)
    parser.add_argument("--max-p971-non-event-ops", type=int, default=2)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best = summary.get("best_event_count_rank4") or summary.get("best_rank4") or {}
    print(
        f"claim={payload['claim_status']} "
        f"pairs={payload['materialization']['materialized_pair_count']} "
        f"candidates={summary['candidate_count']} "
        f"event_ge4={summary['event_count_ge4_count']} "
        f"event_ge4_rank4={summary['event_count_ge4_rank4_count']} "
        f"rank4={summary['rank4_verified_count']} "
        f"rank4_below_rho={summary['rank4_below_rho_count']} "
        f"p971_full_screen={summary['p971_full_screen_pass_count']} "
        f"best={best.get('added_signature')} "
        f"best_ops={best.get('early_ops')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
