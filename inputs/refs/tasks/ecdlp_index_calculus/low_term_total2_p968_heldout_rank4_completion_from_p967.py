#!/usr/bin/env python3
"""P968 held-out rank-4 completion audit from the P967 compressed seed."""

from __future__ import annotations

import argparse
import itertools
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
import low_term_total2_p963_rank3_completion_cost_audit as p963  # noqa: E402
import low_term_total2_p964_rank_raising_leaf_cost_decomposition as p964  # noqa: E402
import low_term_total2_p965_public_hit_event_compression as p965  # noqa: E402
import low_term_total2_p966_public_early_stop_generalization as p966  # noqa: E402
import low_term_total2_p967_heldout_rank3_seed_early_stop as p967  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p968_heldout_rank4_completion_from_p967.md"
DEFAULT_P967 = STATE_DIR / "low_term_total2_p967_heldout_rank3_seed_early_stop_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p968_heldout_rank4_completion_from_p967_probe.json"
SCHEMA = "ecdlp.low_term_total2_p968_heldout_rank4_completion_from_p967.v1"


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


def leaf_signature(leaves_by_row: dict[str, set[int]]) -> tuple[tuple[str, tuple[int, ...]], ...]:
    return tuple((row_key, tuple(sorted(int(leaf) for leaf in leaves))) for row_key, leaves in sorted(leaves_by_row.items()))


def compact_leaves(leaves_by_row: dict[str, set[int]]) -> list[dict[str, Any]]:
    return [
        {
            "leaf_indices": sorted(int(leaf) for leaf in leaves),
            "row_key": row_key,
            "row_short": p966.row_short(row_key),
        }
        for row_key, leaves in sorted(leaves_by_row.items())
    ]


def compact_scan(scan: dict[str, Any]) -> dict[str, Any]:
    return {
        "below_rho": bool(scan.get("below_rho")),
        "derived_secret": scan.get("derived_secret"),
        "generic_rho_steps": scan.get("generic_rho_steps"),
        "ops": scan.get("ops"),
        "ops_over_rho": scan.get("ops_over_rho"),
        "public_key_verified": bool(scan.get("public_key_verified")),
        "rank": scan.get("rank"),
        "relation_count": scan.get("relation_count"),
        "row_results": scan.get("row_results") or [],
        "selected_leaf_count": scan.get("selected_leaf_count"),
        "unique_form_count": scan.get("unique_form_count"),
    }


def best_p967_success(p967_payload: dict[str, Any]) -> dict[str, Any]:
    successes = [row for row in p967_payload.get("audit_results") or [] if (row.get("early_stop") or {}).get("success")]
    if not successes:
        raise ValueError("P967 payload has no successful compressed rank-3 seed")
    successes.sort(key=lambda row: (int_value((row.get("early_stop") or {}).get("ops"), 10**9), row.get("added_signature") or ""))
    return successes[0]


def event_matches_stop(event: dict[str, Any], stop: dict[str, Any]) -> bool:
    if int_value(event.get("global_event_index")) != int_value(stop.get("global_event_index")):
        return False
    if not event.get("accepted_new_relation"):
        return False
    if (event.get("accepted_relation") or {}) != (stop.get("accepted_relation") or {}):
        return False
    event_public = event.get("public_keys") or {}
    stop_public = stop.get("public_keys") or {}
    keys = [
        "row_key",
        "row_leaf",
        "row_x",
        "scout_pos",
        "scout_unsigned_indices",
        "term_shape",
        "term_support",
    ]
    return all(str(event_public.get(key)) == str(stop_public.get(key)) for key in keys)


def reconstruct_compressed_seed(
    args: argparse.Namespace,
    p967_success: dict[str, Any],
) -> dict[str, Any]:
    seed = p967_success["seed"]
    completion = p967_success["completion"]
    verifier, pair, materialized = p964.source_and_materialized(args, p967.row_keys(seed))
    rank2_events = p965.seed_events(verifier, materialized, seed)
    rank3_leaves = p964.leaves_from_rows(completion.get("row_results") or [])
    added = p967.added_leaves(seed, completion)
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        rank3_leaves,
        added,
    )
    stop = (p967_success.get("early_stop") or {}).get("stop_event") or {}
    stop_event = None
    for event in candidate_events:
        if event_matches_stop(event, stop):
            stop_event = event
            break
    if stop_event is None or not stop_event.get("relation_event"):
        raise ValueError("could not reconstruct the P967 accepted stop relation event")
    base_events = rank2_events + [stop_event["relation_event"]]
    derive_row_key = p967.row_keys(completion)[0]
    built = materialized["built_by_row"][derive_row_key]
    derived = p965.public_derive(verifier, built, base_events)
    compressed_seed = dict(completion)
    compressed_seed.update(
        {
            "below_rho": True,
            "derived_secret": derived.get("derived_secret"),
            "generic_rho_steps": int_value(completion.get("generic_rho_steps")),
            "ops": int_value((p967_success.get("early_stop") or {}).get("ops")),
            "ops_over_rho": round(
                int_value((p967_success.get("early_stop") or {}).get("ops"))
                / max(1, int_value(completion.get("generic_rho_steps"))),
                8,
            ),
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": int_value(derived.get("rank")),
            "relation_count": int_value(derived.get("relation_count"), len(base_events)),
            "selector": (
                "p967_compressed_"
                f"{seed.get('selector')}_to_{completion.get('selector')}"
            ),
        }
    )
    control_pass = (
        int_value(derived.get("rank")) == 3
        and bool(derived.get("public_key_verified"))
        and derived.get("derived_secret") == int(args.expected_secret)
        and int_value(compressed_seed.get("ops")) == 123
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
            "p967_candidate_event_count": len(candidate_events),
            "public_key_verified": bool(derived.get("public_key_verified")),
            "rank": int_value(derived.get("rank")),
            "rank2_event_count": len(rank2_events),
            "stop_relation_event_count": 1,
        },
        "materialized": materialized,
        "pair": pair,
        "rank3_full_completion": completion,
        "rank3_leaves": rank3_leaves,
        "rank3_seed": seed,
        "verifier": verifier,
    }


def public_completion_specs(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    modes: list[str],
    schemes: list[str],
    residue_modulus: int,
) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    for mode in modes:
        for scheme in schemes:
            leaves, added = p963.completion_leaves(materialized, seed, mode, scheme, residue_modulus)
            if not added:
                continue
            key = ("public_completion", leaf_signature(leaves), p966.added_signature(added))
            source = {"completion_mode": mode, "completion_scheme": scheme}
            if key not in by_key:
                by_key[key] = {
                    "added": added,
                    "completion_mode": mode,
                    "completion_scheme": scheme,
                    "leaves": leaves,
                    "selector_kind": "public_completion",
                    "sources": [source],
                }
            else:
                by_key[key]["sources"].append(source)
    return list(by_key.values())


def oracle_completion_specs(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    max_extra_leaves: int,
) -> list[dict[str, Any]]:
    by_feature = p963.feature_maps(materialized)
    current = p963.seed_leaves(seed)
    extras = []
    for row in materialized["selected_rows"]:
        row_key = str(p963.leaf_public_probe.row_key(row))
        for leaf in sorted(p963.candidate_leaf_set(row) - current.get(row_key, set())):
            feature = by_feature.get(row_key, {}).get(leaf)
            extras.append(
                {
                    "feature": p963.compact_feature(feature or {"leaf_index": leaf}),
                    "leaf": int(leaf),
                    "row_key": row_key,
                }
            )
    specs = []
    seen: set[tuple[Any, ...]] = set()
    for size in range(1, max(0, int(max_extra_leaves)) + 1):
        for subset in itertools.combinations(extras, size):
            leaves = {row_key: set(row_leaves) for row_key, row_leaves in current.items()}
            for extra in subset:
                leaves.setdefault(str(extra["row_key"]), set()).add(int(extra["leaf"]))
            added = [dict(extra) for extra in subset]
            key = ("oracle_completion", leaf_signature(leaves), p966.added_signature(added))
            if key in seen:
                continue
            seen.add(key)
            label = "+".join(f"{p966.row_short(str(extra['row_key']))}:{extra['leaf']}" for extra in added)
            specs.append(
                {
                    "added": added,
                    "completion_mode": "oracle",
                    "completion_scheme": f"extra{size}:{label}",
                    "leaves": leaves,
                    "selector_kind": "oracle_completion",
                    "sources": [{"completion_mode": "oracle", "completion_scheme": f"extra{size}:{label}"}],
                }
            )
    return specs


def audit_completion(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    compressed_seed: dict[str, Any],
    rank3_full_completion: dict[str, Any],
    base_events: list[dict[str, Any]],
    spec: dict[str, Any],
    expected_secret: int,
) -> dict[str, Any]:
    leaves = spec["leaves"]
    added = spec["added"]
    label = (
        f"{compressed_seed.get('selector')}+"
        f"{spec.get('completion_mode')}:{spec.get('completion_scheme')}"
    )
    scan = p961.scan_from_leaves(verifier, materialized, pair, leaves, label, str(spec.get("selector_kind")))
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        leaves,
        added,
    )
    derive_row_key = p967.row_keys(rank3_full_completion)[0]
    built = materialized["built_by_row"][derive_row_key]
    rho = int_value(rank3_full_completion.get("generic_rho_steps"))
    compressed_seed_ops = int_value(compressed_seed.get("ops"))
    rank3_full_ops = int_value(rank3_full_completion.get("ops"))
    full_completion_ops = int_value(scan.get("ops"))
    non_event_marginal_ops = full_completion_ops - rank3_full_ops - 2 * len(candidate_events)
    accounting_valid = len(candidate_events) > 0 and non_event_marginal_ops >= 0
    if accounting_valid:
        early = p967.evaluate_rank_threshold(
            verifier,
            built,
            base_events,
            candidate_events,
            compressed_seed_ops,
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
            "ops": compressed_seed_ops + max(0, non_event_marginal_ops),
            "ops_over_rho": round((compressed_seed_ops + max(0, non_event_marginal_ops)) / max(1, rho), 8),
            "processed_candidate_events": len(candidate_events),
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    min_ops_after_one_event = (
        compressed_seed_ops + non_event_marginal_ops + 2
        if len(candidate_events) > 0
        else None
    )
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": accounting_valid,
        "added_leaf_count": len(added),
        "added_signature": p966.added_signature(added),
        "candidate_event_count": len(candidate_events),
        "candidate_event_signatures": [p966.compact_event(event) for event in candidate_events],
        "completion_leaves": compact_leaves(leaves),
        "completion_mode": spec.get("completion_mode"),
        "completion_scheme": spec.get("completion_scheme"),
        "cost_floor_after_one_event": {
            "below_rho_possible": bool(min_ops_after_one_event is not None and min_ops_after_one_event < rho),
            "min_ops_after_one_event": min_ops_after_one_event,
            "remaining_budget_before_added_event": rho - compressed_seed_ops,
            "rho": rho,
        },
        "early_stop": early,
        "full_completion_scan": compact_scan(scan),
        "full_completion_ops": full_completion_ops,
        "full_completion_ops_over_rho": scan.get("ops_over_rho"),
        "non_event_marginal_ops": non_event_marginal_ops,
        "rank3_full_ops": rank3_full_ops,
        "rho": rho,
        "seed_ops": compressed_seed_ops,
        "selector_kind": spec.get("selector_kind"),
        "sources": spec.get("sources") or [],
    }


def summarize(results: list[dict[str, Any]], control: dict[str, Any], expected_secret: int) -> dict[str, Any]:
    public_results = [row for row in results if row.get("selector_kind") == "public_completion"]
    oracle_results = [row for row in results if row.get("selector_kind") == "oracle_completion"]

    def verified_rank4(row: dict[str, Any]) -> bool:
        early = row.get("early_stop") or {}
        return (
            bool(early.get("public_key_verified"))
            and int_value(early.get("rank")) >= 4
            and early.get("derived_secret") == expected_secret
        )

    public_rank4 = [row for row in public_results if verified_rank4(row)]
    oracle_rank4 = [row for row in oracle_results if verified_rank4(row)]
    public_rank4_below = [row for row in public_rank4 if (row.get("early_stop") or {}).get("success")]
    oracle_rank4_below = [row for row in oracle_rank4 if (row.get("early_stop") or {}).get("success")]
    rank4_any = public_rank4 + oracle_rank4
    best_rank4 = sorted(rank4_any, key=lambda row: int_value((row.get("early_stop") or {}).get("ops"), 10**9))[0] if rank4_any else None
    strict_budget_possible = [
        row for row in results if ((row.get("cost_floor_after_one_event") or {}).get("below_rho_possible"))
    ]
    full_scan_rank4 = [
        row
        for row in results
        if (row.get("full_completion_scan") or {}).get("public_key_verified")
        and int_value((row.get("full_completion_scan") or {}).get("rank")) >= 4
        and (row.get("full_completion_scan") or {}).get("derived_secret") == expected_secret
    ]
    claim = (
        "P968_PUBLIC_HELDOUT_RANK4_COMPLETION_BELOW_RHO_FOUND"
        if public_rank4_below
        else "P968_ORACLE_HELDOUT_RANK4_COMPLETION_BELOW_RHO_PUBLIC_OPEN"
        if oracle_rank4_below
        else "NEGATIVE_RESULT_P968_HELDOUT_RANK4_COMPLETION_COST_BOUNDARY"
        if rank4_any or full_scan_rank4
        else "NEGATIVE_RESULT_P968_NO_HELDOUT_RANK4_COMPLETION_FROM_COMPRESSED_SEED"
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
        "compressed_seed_control_pass": bool(control.get("control_pass")),
        "full_scan_rank4_count": len(full_scan_rank4),
        "oracle_completion_count": len(oracle_results),
        "oracle_rank4_below_rho_count": len(oracle_rank4_below),
        "oracle_rank4_count": len(oracle_rank4),
        "public_completion_count": len(public_results),
        "public_rank4_below_rho_count": len(public_rank4_below),
        "public_rank4_count": len(public_rank4),
        "strict_budget_possible_count": len(strict_budget_possible),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p967_payload = load_json(Path(args.p967))
    p967_success = best_p967_success(p967_payload)
    reconstructed = reconstruct_compressed_seed(args, p967_success)
    if not reconstructed["control"]["control_pass"]:
        raise ValueError(f"P967 compressed seed reconstruction failed: {reconstructed['control']!r}")
    materialized = reconstructed["materialized"]
    compressed_seed = reconstructed["compressed_seed"]
    modes = p963.parse_csv(args.completion_modes)
    schemes = p963.parse_csv(args.completion_schemes)
    public_specs = public_completion_specs(
        materialized,
        compressed_seed,
        modes,
        schemes,
        int(args.residue_modulus),
    )
    oracle_specs = oracle_completion_specs(materialized, compressed_seed, int(args.max_oracle_extra_leaves))
    specs = public_specs + oracle_specs
    results = [
        audit_completion(
            reconstructed["verifier"],
            materialized,
            reconstructed["pair"],
            compressed_seed,
            reconstructed["rank3_full_completion"],
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
            "p967_result": str(args.p967),
            "script": str(Path(__file__)),
            "source": materialized.get("source_path"),
        },
        "claim_status": summary["claim_status"],
        "completion_results": results,
        "created_at": now_iso(),
        "frontier_seed": {
            "compressed_rank3_seed": p967.compact_result(compressed_seed),
            "rank3_full_completion": p967.compact_result(reconstructed["rank3_full_completion"]),
            "rank3_full_leaves": compact_leaves(reconstructed["rank3_leaves"]),
            "rank3_seed": p967.compact_result(reconstructed["rank3_seed"]),
            "reconstruction_control": reconstructed["control"],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "HELDOUT-ROW-PAIR: audits the P967 salt204+salt208 held-out row pair, not arbitrary curves.",
            "PUBLIC-COMPLETION: public completions use P963 public leaf features; oracle completions are diagnostic only.",
            "COMPRESSED-SEED ACCOUNTING: the rank-3 seed cost is P967's public early-stop ops, and every added candidate event costs 2 ops.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this audits local rank raising, not full relation collection, sparse linear algebra, or target descent.",
        ],
        "method": "p968_heldout_rank4_completion_from_p967",
        "parameters": {
            "completion_modes": modes,
            "completion_schemes": schemes,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_oracle_extra_leaves": int(args.max_oracle_extra_leaves),
            "p967": str(args.p967),
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
    parser.add_argument("--p967", type=Path, default=DEFAULT_P967)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=p959.p957.DEFAULT_TARGET)
    parser.add_argument("--post-min", type=int, default=p959.p957.DEFAULT_POST_MIN)
    parser.add_argument("--fixed-transfer", type=int, default=p959.DEFAULT_FIXED_TRANSFER)
    parser.add_argument("--expected-secret", type=int, default=2351)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--completion-modes", default=p963.DEFAULT_COMPLETION_MODES)
    parser.add_argument("--completion-schemes", default=p963.DEFAULT_COMPLETION_SCHEMES)
    parser.add_argument("--max-oracle-extra-leaves", type=int, default=2)
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
        f"control_pass={summary['compressed_seed_control_pass']} "
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
