#!/usr/bin/env python3
"""P970 rank-4 completion audit from the P969 event-local seed."""

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
import low_term_total2_p965_public_hit_event_compression as p965  # noqa: E402
import low_term_total2_p966_public_early_stop_generalization as p966  # noqa: E402
import low_term_total2_p967_heldout_rank3_seed_early_stop as p967  # noqa: E402
import low_term_total2_p968_heldout_rank4_completion_from_p967 as p968  # noqa: E402
import low_term_total2_p969_heldout_rank3_seed_budget_rescue as p969  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p970_rank4_from_p969_seed.md"
DEFAULT_P969 = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p970_rank4_from_p969_seed_probe.json"
SCHEMA = "ecdlp.low_term_total2_p970_rank4_from_p969_seed.v1"


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


def best_p969_event_success(p969_payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    candidates = []
    for audit in p969_payload.get("seed_audits") or []:
        seed = audit.get("seed") or {}
        for result in audit.get("completion_results") or []:
            if result.get("selector_kind") != "p967_event_subset":
                continue
            if not result.get("budget_success"):
                continue
            candidates.append((seed, result))
    if not candidates:
        raise ValueError("P969 payload has no event-local budget success")
    candidates.sort(key=lambda item: (int_value((item[1].get("early_stop") or {}).get("ops"), 10**9), item[1].get("added_signature") or ""))
    return candidates[0]


def reconstruct_p969_seed(args: argparse.Namespace, p969_payload: dict[str, Any]) -> dict[str, Any]:
    seed, success = best_p969_event_success(p969_payload)
    added = success.get("added") or []
    if not added:
        added_signature = str(success.get("added_signature") or "")
        added = [
            {
                "leaf": int(part.split(":")[-1]),
                "row_key": next(
                    row["row_key"]
                    for row in seed.get("row_results") or []
                    if str(row.get("row_key")).endswith(part.split(":")[0])
                ),
            }
            for part in added_signature.split(",")
            if part
        ]
    verifier, pair, materialized = p964.source_and_materialized(args, p967.row_keys(seed))
    base_rank2_events = p965.seed_events(verifier, materialized, seed)
    p969_leaves = p969.add_to_leaves(seed, added)
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        p969_leaves,
        added,
    )
    stop = (success.get("early_stop") or {}).get("stop_event") or {}
    stop_event = None
    for event in candidate_events:
        if p968.event_matches_stop(event, stop):
            stop_event = event
            break
    if stop_event is None or not stop_event.get("relation_event"):
        raise ValueError("could not reconstruct P969 event-local accepted relation")
    base_events = base_rank2_events + [stop_event["relation_event"]]
    derive_row_key = p967.row_keys(seed)[0]
    built = materialized["built_by_row"][derive_row_key]
    derived = p965.public_derive(verifier, built, base_events)
    seed_scan = p961.scan_from_leaves(
        verifier,
        materialized,
        pair,
        p969_leaves,
        "p969_event_local_seed",
        "p969_seed_replay",
    )
    compressed_seed = {
        "below_rho": True,
        "derived_secret": derived.get("derived_secret"),
        "generic_rho_steps": seed.get("generic_rho_steps"),
        "ops": int_value((success.get("early_stop") or {}).get("ops")),
        "ops_over_rho": round(int_value((success.get("early_stop") or {}).get("ops")) / max(1, int_value(seed.get("generic_rho_steps"))), 8),
        "public_key_verified": bool(derived.get("public_key_verified")),
        "rank": int_value(derived.get("rank")),
        "relation_count": len(base_events),
        "row_pair_key": seed.get("row_pair_key"),
        "row_results": seed_scan.get("row_results") or [],
        "selector": f"p969_event_local_{seed.get('selector')}_plus_{p966.added_signature(added)}",
    }
    control_pass = (
        int_value(compressed_seed.get("rank")) == 3
        and bool(compressed_seed.get("public_key_verified"))
        and compressed_seed.get("derived_secret") == int(args.expected_secret)
        and int_value(compressed_seed.get("ops")) == 122
    )
    return {
        "base_events": base_events,
        "candidate_metadata": candidate_metadata,
        "compressed_seed": compressed_seed,
        "control": {
            "accepted_stop_event": p966.compact_event(stop_event),
            "base_event_count": len(base_events),
            "control_pass": control_pass,
            "derived_secret": derived.get("derived_secret"),
            "full_seed_scan": p968.compact_scan(seed_scan),
            "p969_candidate_event_count": len(candidate_events),
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": int_value(derived.get("rank")),
            "rank2_event_count": len(base_rank2_events),
            "stop_relation_event_count": 1,
        },
        "full_seed_ops": int_value(seed_scan.get("ops")),
        "materialized": materialized,
        "pair": pair,
        "p969_added": added,
        "rank2_seed": seed,
        "seed_leaves": p969_leaves,
        "verifier": verifier,
    }


def evaluate_rank4(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    compressed_seed: dict[str, Any],
    seed_full_ops: int,
    base_events: list[dict[str, Any]],
    spec: dict[str, Any],
    expected_secret: int,
) -> dict[str, Any]:
    leaves = spec["leaves"]
    added = spec["added"]
    scan = p961.scan_from_leaves(
        verifier,
        materialized,
        pair,
        leaves,
        f"{compressed_seed.get('selector')}+{spec.get('completion_mode')}:{spec.get('completion_scheme')}",
        str(spec.get("selector_kind")),
    )
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        leaves,
        added,
    )
    derive_row_key = p967.row_keys(compressed_seed)[0]
    built = materialized["built_by_row"][derive_row_key]
    rho = int_value(compressed_seed.get("generic_rho_steps"))
    seed_ops = int_value(compressed_seed.get("ops"))
    full_ops = int_value(scan.get("ops"))
    non_event_marginal_ops = full_ops - int(seed_full_ops) - 2 * len(candidate_events)
    accounting_valid = len(candidate_events) > 0 and non_event_marginal_ops >= 0
    if accounting_valid:
        early = p967.evaluate_rank_threshold(
            verifier,
            built,
            base_events,
            candidate_events,
            seed_ops,
            non_event_marginal_ops,
            rho,
            expected_secret,
            4,
        )
    else:
        early = {
            "accepted_relation_count": 0,
            "below_rho": False,
            "derived_secret": None,
            "ops": seed_ops + max(0, non_event_marginal_ops),
            "ops_over_rho": round((seed_ops + max(0, non_event_marginal_ops)) / max(1, rho), 8),
            "processed_candidate_events": len(candidate_events),
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    min_ops_after_one_event = seed_ops + non_event_marginal_ops + 2 if len(candidate_events) else None
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": accounting_valid,
        "added_leaf_count": len(added),
        "added_signature": p966.added_signature(added),
        "candidate_event_count": len(candidate_events),
        "candidate_event_signatures": [p966.compact_event(event) for event in candidate_events],
        "completion_leaves": p968.compact_leaves(leaves),
        "completion_mode": spec.get("completion_mode"),
        "completion_scheme": spec.get("completion_scheme"),
        "cost_floor_after_one_event": {
            "below_rho_possible": bool(min_ops_after_one_event is not None and min_ops_after_one_event < rho),
            "min_ops_after_one_event": min_ops_after_one_event,
            "remaining_budget_before_added_event": rho - seed_ops,
            "rho": rho,
        },
        "early_stop": early,
        "full_completion_scan": p968.compact_scan(scan),
        "full_completion_ops": full_ops,
        "non_event_marginal_ops": non_event_marginal_ops,
        "rho": rho,
        "seed_full_ops": seed_full_ops,
        "seed_ops": seed_ops,
        "selector_kind": spec.get("selector_kind"),
        "sources": spec.get("sources") or [],
    }


def summarize(results: list[dict[str, Any]], control: dict[str, Any], expected_secret: int) -> dict[str, Any]:
    def verified_rank4(row: dict[str, Any]) -> bool:
        early = row.get("early_stop") or {}
        return (
            bool(early.get("public_key_verified"))
            and int_value(early.get("rank")) >= 4
            and early.get("derived_secret") == expected_secret
        )

    public = [row for row in results if row.get("selector_kind") == "public_completion"]
    oracle = [row for row in results if row.get("selector_kind") == "oracle_completion"]
    public_rank4 = [row for row in public if verified_rank4(row)]
    oracle_rank4 = [row for row in oracle if verified_rank4(row)]
    public_rank4_below = [row for row in public_rank4 if (row.get("early_stop") or {}).get("success")]
    oracle_rank4_below = [row for row in oracle_rank4 if (row.get("early_stop") or {}).get("success")]
    full_scan_rank4 = [
        row
        for row in results
        if (row.get("full_completion_scan") or {}).get("public_key_verified")
        and int_value((row.get("full_completion_scan") or {}).get("rank")) >= 4
        and (row.get("full_completion_scan") or {}).get("derived_secret") == expected_secret
    ]
    strict_budget_possible = [row for row in results if (row.get("cost_floor_after_one_event") or {}).get("below_rho_possible")]
    best_rank4 = sorted(public_rank4 + oracle_rank4, key=lambda row: int_value((row.get("early_stop") or {}).get("ops"), 10**9))[0] if public_rank4 or oracle_rank4 else None
    claim = (
        "P970_PUBLIC_RANK4_FROM_P969_SEED_BELOW_RHO_FOUND"
        if public_rank4_below
        else "P970_ORACLE_RANK4_FROM_P969_SEED_BELOW_RHO_PUBLIC_OPEN"
        if oracle_rank4_below
        else "NEGATIVE_RESULT_P970_RANK4_FROM_P969_SEED_COST_BOUNDARY"
        if public_rank4 or oracle_rank4 or full_scan_rank4
        else "NEGATIVE_RESULT_P970_NO_RANK4_FROM_P969_SEED"
    )
    return {
        "accounting_valid_count": sum(1 for row in results if row.get("accounting_valid")),
        "audited_completion_count": len(results),
        "best_verified_rank4_completion": {
            "added_signature": best_rank4.get("added_signature"),
            "early_stop": best_rank4.get("early_stop"),
            "selector_kind": best_rank4.get("selector_kind"),
            "completion_mode": best_rank4.get("completion_mode"),
            "completion_scheme": best_rank4.get("completion_scheme"),
        }
        if best_rank4
        else None,
        "claim_status": claim,
        "full_scan_rank4_count": len(full_scan_rank4),
        "oracle_completion_count": len(oracle),
        "oracle_rank4_below_rho_count": len(oracle_rank4_below),
        "oracle_rank4_count": len(oracle_rank4),
        "p969_seed_control_pass": bool(control.get("control_pass")),
        "public_completion_count": len(public),
        "public_rank4_below_rho_count": len(public_rank4_below),
        "public_rank4_count": len(public_rank4),
        "strict_budget_possible_count": len(strict_budget_possible),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p969_payload = load_json(Path(args.p969))
    reconstructed = reconstruct_p969_seed(args, p969_payload)
    if not reconstructed["control"]["control_pass"]:
        raise ValueError(f"P969 seed reconstruction failed: {reconstructed['control']!r}")
    modes = p963.parse_csv(args.completion_modes)
    schemes = p963.parse_csv(args.completion_schemes)
    public_specs = p968.public_completion_specs(
        reconstructed["materialized"],
        reconstructed["compressed_seed"],
        modes,
        schemes,
        int(args.residue_modulus),
    )
    oracle_specs = p968.oracle_completion_specs(
        reconstructed["materialized"],
        reconstructed["compressed_seed"],
        int(args.max_oracle_extra_leaves),
    )
    specs = public_specs + oracle_specs
    results = [
        evaluate_rank4(
            reconstructed["verifier"],
            reconstructed["materialized"],
            reconstructed["pair"],
            reconstructed["compressed_seed"],
            reconstructed["full_seed_ops"],
            reconstructed["base_events"],
            spec,
            int(args.expected_secret),
        )
        for spec in specs
    ]
    results.sort(
        key=lambda row: (
            row.get("selector_kind") != "public_completion",
            not bool((row.get("early_stop") or {}).get("public_key_verified")),
            -int_value((row.get("early_stop") or {}).get("rank")),
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            row.get("added_signature") or "",
        )
    )
    summary = summarize(results, reconstructed["control"], int(args.expected_secret))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p969_result": str(args.p969),
            "script": str(Path(__file__)),
            "source": reconstructed["materialized"].get("source_path"),
        },
        "claim_status": summary["claim_status"],
        "completion_results": results,
        "created_at": now_iso(),
        "frontier_seed": {
            "compressed_rank3_seed": p969.compact_result(reconstructed["compressed_seed"]),
            "p969_added": reconstructed["p969_added"],
            "rank2_seed": p969.compact_result(reconstructed["rank2_seed"]),
            "reconstruction_control": reconstructed["control"],
            "seed_full_ops": reconstructed["full_seed_ops"],
            "seed_leaves": p968.compact_leaves(reconstructed["seed_leaves"]),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "EVENT-LOCAL-SEED: the starting rank-3 seed is P969 event-local/post-discovery, not a standalone public selector.",
            "PUBLIC-ORACLE-SEPARATION: public completions and oracle diagnostics are counted separately.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this audits local rank-4 completion, not full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p970_rank4_from_p969_seed",
        "parameters": {
            "completion_modes": modes,
            "completion_schemes": schemes,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_oracle_extra_leaves": int(args.max_oracle_extra_leaves),
            "p969": str(args.p969),
            "post_min": int(args.post_min),
            "residue_modulus": int(args.residue_modulus),
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
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--completion-modes", default=p963.DEFAULT_COMPLETION_MODES)
    parser.add_argument("--completion-schemes", default=p963.DEFAULT_COMPLETION_SCHEMES)
    parser.add_argument("--max-oracle-extra-leaves", type=int, default=3)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best = summary.get("best_verified_rank4_completion") or {}
    best_early = best.get("early_stop") or {}
    print(
        f"claim={payload['claim_status']} "
        f"control_pass={summary['p969_seed_control_pass']} "
        f"audited={summary['audited_completion_count']} "
        f"public_rank4={summary['public_rank4_count']} "
        f"public_rank4_below={summary['public_rank4_below_rho_count']} "
        f"oracle_rank4={summary['oracle_rank4_count']} "
        f"oracle_rank4_below={summary['oracle_rank4_below_rho_count']} "
        f"full_scan_rank4={summary['full_scan_rank4_count']} "
        f"strict_budget_possible={summary['strict_budget_possible_count']} "
        f"best_rank4_ops={best_early.get('ops')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
