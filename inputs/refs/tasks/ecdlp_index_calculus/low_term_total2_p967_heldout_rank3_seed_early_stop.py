#!/usr/bin/env python3
"""P967 held-out row-pair rank-3 early-stop seed audit."""

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
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402
import low_term_total2_p965_public_hit_event_compression as p965  # noqa: E402
import low_term_total2_p966_public_early_stop_generalization as p966  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p967_heldout_rank3_seed_early_stop.md"
DEFAULT_P962 = STATE_DIR / "low_term_total2_p962_fixed_public_selector_frontier_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p967_heldout_rank3_seed_early_stop_probe.json"
SCHEMA = "ecdlp.low_term_total2_p967_heldout_rank3_seed_early_stop.v1"
EXCLUDED_ROW_PAIR = "salt203+salt205"


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


def leaves_by_row(result: dict[str, Any]) -> dict[str, set[int]]:
    return {
        str(row.get("row_key")): {int(leaf) for leaf in row.get("leaf_indices") or []}
        for row in result.get("row_results") or []
    }


def row_keys(result: dict[str, Any]) -> list[str]:
    return [str(row.get("row_key")) for row in result.get("row_results") or []]


def leaf_signature(result: dict[str, Any]) -> tuple[tuple[str, tuple[int, ...]], ...]:
    return tuple(
        sorted(
            (
                str(row.get("row_key")),
                tuple(sorted(int(leaf) for leaf in row.get("leaf_indices") or [])),
            )
            for row in result.get("row_results") or []
        )
    )


def is_leaf_superset(seed: dict[str, Any], completion: dict[str, Any]) -> bool:
    seed_leaves = leaves_by_row(seed)
    completion_leaves = leaves_by_row(completion)
    if set(seed_leaves) != set(completion_leaves):
        return False
    return all(seed_leaves[row_key].issubset(completion_leaves[row_key]) for row_key in seed_leaves)


def added_leaves(seed: dict[str, Any], completion: dict[str, Any]) -> list[dict[str, Any]]:
    seed_leaves = leaves_by_row(seed)
    completion_leaves = leaves_by_row(completion)
    out = []
    for row_key in sorted(completion_leaves):
        for leaf in sorted(completion_leaves[row_key] - seed_leaves.get(row_key, set())):
            out.append({"leaf": int(leaf), "row_key": row_key})
    return out


def compact_result(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "below_rho": bool(row.get("below_rho")),
        "derived_secret": row.get("derived_secret"),
        "generic_rho_steps": row.get("generic_rho_steps"),
        "ops": row.get("ops"),
        "ops_over_rho": row.get("ops_over_rho"),
        "public_key_verified": bool(row.get("public_key_verified")),
        "rank": row.get("rank"),
        "relation_count": row.get("relation_count"),
        "row_pair_key": row.get("row_pair_key"),
        "row_results": row.get("row_results") or [],
        "selector": row.get("selector"),
    }


def frontier_pairs(p962_payload: dict[str, Any], expected_secret: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    verified = [
        row
        for row in p962_payload.get("results") or []
        if row.get("public_key_verified")
        and row.get("derived_secret") == expected_secret
        and row.get("row_pair_key") != EXCLUDED_ROW_PAIR
    ]
    seeds = [
        row
        for row in verified
        if row.get("below_rho")
        and int_value(row.get("rank")) == 2
    ]
    completions = [
        row
        for row in verified
        if int_value(row.get("rank")) >= 3
    ]
    pairs = []
    seen: set[tuple[Any, ...]] = set()
    for seed in seeds:
        for completion in completions:
            if seed.get("row_pair_key") != completion.get("row_pair_key"):
                continue
            if not is_leaf_superset(seed, completion):
                continue
            added = added_leaves(seed, completion)
            if not added:
                continue
            key = (
                seed.get("selector"),
                completion.get("selector"),
                seed.get("row_pair_key"),
                leaf_signature(seed),
                leaf_signature(completion),
            )
            if key in seen:
                continue
            seen.add(key)
            pairs.append({"added_leaves": added, "completion": completion, "seed": seed})
    pairs.sort(
        key=lambda item: (
            int_value(item["completion"].get("ops"), 10**9),
            int_value(item["seed"].get("ops"), 10**9),
            item["seed"].get("selector") or "",
            item["completion"].get("selector") or "",
        )
    )
    return seeds, completions, pairs


def evaluate_rank_threshold(
    verifier: Any,
    built: dict[str, Any],
    base_events: list[dict[str, Any]],
    candidate_events: list[dict[str, Any]],
    seed_ops: int,
    non_event_marginal_ops: int,
    rho: int,
    expected_secret: int,
    target_rank: int,
) -> dict[str, Any]:
    accepted_so_far = []
    last_result = None
    for index, event in enumerate(candidate_events, start=1):
        if event.get("relation_event"):
            accepted_so_far.append(event)
        accepted_events = [item["relation_event"] for item in accepted_so_far if item.get("relation_event")]
        derived = p965.public_derive(verifier, built, base_events + accepted_events)
        ops = p965.completion_ops(seed_ops, non_event_marginal_ops, index)
        result = {
            "accepted_relation_count": len(accepted_events),
            "below_rho": bool(ops < rho),
            "derived_secret": derived.get("derived_secret"),
            "ops": ops,
            "ops_over_rho": round(ops / max(1, rho), 8),
            "processed_candidate_events": index,
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": int_value(derived.get("rank")),
            "saved_verification_ops": 2 * (len(candidate_events) - index),
            "skipped_candidate_events": len(candidate_events) - index,
            "stop_event": p966.compact_event(event),
            "success": bool(
                ops < rho
                and derived.get("public_key_verified")
                and int_value(derived.get("rank")) >= target_rank
                and derived.get("derived_secret") == expected_secret
            ),
        }
        last_result = result
        if result["public_key_verified"] and int_value(result["rank"]) >= target_rank and result["derived_secret"] == expected_secret:
            return result
    if last_result is None:
        return {
            "accepted_relation_count": 0,
            "below_rho": False,
            "derived_secret": None,
            "ops": seed_ops + non_event_marginal_ops,
            "ops_over_rho": round((seed_ops + non_event_marginal_ops) / max(1, rho), 8),
            "processed_candidate_events": 0,
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    return last_result


def audit_pair(
    verifier: Any,
    materialized: dict[str, Any],
    seed: dict[str, Any],
    completion: dict[str, Any],
    added: list[dict[str, Any]],
    expected_secret: int,
) -> dict[str, Any]:
    base_events = p965.seed_events(verifier, materialized, seed)
    completion_leaves = p964.leaves_from_rows(completion.get("row_results") or [])
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        completion_leaves,
        added,
    )
    derive_row_key = row_keys(completion)[0]
    built = materialized["built_by_row"][derive_row_key]
    seed_ops = int_value(seed.get("ops"))
    completion_ops = int_value(completion.get("ops"))
    rho = int_value(completion.get("generic_rho_steps"))
    non_event_marginal_ops = completion_ops - seed_ops - 2 * len(candidate_events)
    accounting_valid = len(candidate_events) > 0 and non_event_marginal_ops >= 0
    early = (
        evaluate_rank_threshold(
            verifier,
            built,
            base_events,
            candidate_events,
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
            int_value(completion.get("rank"), 3),
        )
        if accounting_valid
        else {
            "accepted_relation_count": 0,
            "below_rho": False,
            "derived_secret": None,
            "ops": completion_ops,
            "ops_over_rho": round(completion_ops / max(1, rho), 8),
            "processed_candidate_events": len(candidate_events),
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    )
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": accounting_valid,
        "added_leaf_count": len(added),
        "added_signature": p966.added_signature(added),
        "candidate_event_count": len(candidate_events),
        "completion": compact_result(completion),
        "early_stop": early,
        "non_event_marginal_ops": non_event_marginal_ops,
        "rho": rho,
        "seed": compact_result(seed),
        "seed_ops": seed_ops,
    }


def summarize(seeds: list[dict[str, Any]], completions: list[dict[str, Any]], pairs: list[dict[str, Any]], audits: list[dict[str, Any]]) -> dict[str, Any]:
    successes = [row for row in audits if (row.get("early_stop") or {}).get("success")]
    best_success = None
    if successes:
        best_success = sorted(successes, key=lambda row: int_value((row.get("early_stop") or {}).get("ops"), 10**9))[0]
    row_pairs = sorted({str(row.get("row_pair_key")) for row in seeds + completions})
    claim = (
        "P967_HELDOUT_ROWPAIR_RANK3_SEED_BELOW_RHO_FOUND"
        if successes
        else "NEGATIVE_RESULT_P967_HELDOUT_RANK3_EARLY_STOP_NO_BELOW_RHO"
        if pairs
        else "NEGATIVE_RESULT_P967_HELDOUT_RANK3_SOURCE_FRONTIER_GAP"
    )
    return {
        "accounting_valid_count": sum(1 for row in audits if row.get("accounting_valid")),
        "audited_pair_count": len(audits),
        "best_success": {
            "added_signature": best_success.get("added_signature"),
            "completion_selector": (best_success.get("completion") or {}).get("selector"),
            "early_stop": best_success.get("early_stop"),
            "row_pair_key": (best_success.get("seed") or {}).get("row_pair_key"),
            "seed_selector": (best_success.get("seed") or {}).get("selector"),
        }
        if best_success
        else None,
        "claim_status": claim,
        "completion_count": len(completions),
        "early_success_count": len(successes),
        "heldout_row_pair_count": len(row_pairs),
        "heldout_row_pairs": row_pairs,
        "rank2_seed_count": len(seeds),
        "seed_completion_pair_count": len(pairs),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p962_payload = load_json(Path(args.p962))
    seeds, completions, pairs = frontier_pairs(p962_payload, int(args.expected_secret))
    if int(args.max_pairs) > 0:
        pairs = pairs[: int(args.max_pairs)]
    materialized_cache: dict[str, tuple[Any, dict[str, Any]]] = {}
    audits = []
    materialization_errors = []
    for pair in pairs:
        seed = pair["seed"]
        key = str(seed.get("row_pair_key"))
        if key not in materialized_cache:
            try:
                verifier, _source_pair, materialized = p964.source_and_materialized(args, row_keys(seed))
                materialized_cache[key] = (verifier, materialized)
            except Exception as exc:  # noqa: BLE001
                materialization_errors.append({"error": repr(exc), "row_pair_key": key})
                continue
        verifier, materialized = materialized_cache[key]
        audits.append(
            audit_pair(
                verifier,
                materialized,
                seed,
                pair["completion"],
                pair["added_leaves"],
                int(args.expected_secret),
            )
        )
    summary = summarize(seeds, completions, pairs, audits)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p962_result": str(args.p962),
            "p966_script": str(Path(p966.__file__)),
            "script": str(Path(__file__)),
        },
        "audit_results": audits,
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "frontier": {
            "completion_candidates": [compact_result(row) for row in completions],
            "materialization_errors": materialization_errors,
            "rank2_seed_candidates": [compact_result(row) for row in seeds],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "HELDOUT-ROW-PAIR: excludes salt203+salt205 and audits available P962 row-pair material.",
            "RANK3-SEED-GENERATION: this creates or rejects a seed for later rank-4 completion; it is not itself a full rank-4 break.",
            "PUBLIC-EARLY-STOP: stopping uses public rank and public-key verification, not hidden scalar selection.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this does not prove full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p967_heldout_rank3_seed_early_stop",
        "parameters": {
            "excluded_row_pair": EXCLUDED_ROW_PAIR,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_pairs": int(args.max_pairs),
            "p962": str(args.p962),
            "post_min": int(args.post_min),
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
    parser.add_argument("--p962", type=Path, default=DEFAULT_P962)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--max-pairs", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"heldout_row_pairs={summary['heldout_row_pair_count']} "
        f"rank2_seeds={summary['rank2_seed_count']} "
        f"rank3_completions={summary['completion_count']} "
        f"seed_completion_pairs={summary['seed_completion_pair_count']} "
        f"audited={summary['audited_pair_count']} "
        f"early_success={summary['early_success_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
