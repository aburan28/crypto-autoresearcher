#!/usr/bin/env python3
"""P969 held-out rank-3 seed budget-rescue audit."""

from __future__ import annotations

import argparse
import itertools
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


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p969_heldout_rank3_seed_budget_rescue.md"
DEFAULT_P967 = STATE_DIR / "low_term_total2_p967_heldout_rank3_seed_early_stop_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p969_heldout_rank3_seed_budget_rescue_probe.json"
SCHEMA = "ecdlp.low_term_total2_p969_heldout_rank3_seed_budget_rescue.v1"


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


def seed_signature(seed: dict[str, Any]) -> tuple[Any, ...]:
    return (
        seed.get("selector"),
        seed.get("row_pair_key"),
        p968.leaf_signature(p964.leaves_from_rows(seed.get("row_results") or [])),
    )


def add_to_leaves(seed: dict[str, Any], added: list[dict[str, Any]]) -> dict[str, set[int]]:
    leaves = p964.leaves_from_rows(seed.get("row_results") or [])
    for item in added:
        leaves.setdefault(str(item["row_key"]), set()).add(int(item["leaf"]))
    return leaves


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


def frontier_rank2_seeds(p967_payload: dict[str, Any], expected_secret: int) -> list[dict[str, Any]]:
    seeds = []
    seen: set[tuple[Any, ...]] = set()
    for row in (p967_payload.get("frontier") or {}).get("rank2_seed_candidates") or []:
        if not row.get("public_key_verified"):
            continue
        if row.get("derived_secret") != expected_secret:
            continue
        if not row.get("below_rho"):
            continue
        if int_value(row.get("rank")) != 2:
            continue
        key = seed_signature(row)
        if key in seen:
            continue
        seen.add(key)
        seeds.append(row)
    seeds.sort(key=lambda row: (int_value(row.get("ops"), 10**9), row.get("selector") or ""))
    return seeds


def add_spec(
    by_key: dict[tuple[Any, ...], dict[str, Any]],
    seed: dict[str, Any],
    selector_kind: str,
    completion_mode: str,
    completion_scheme: str,
    leaves: dict[str, set[int]],
    added: list[dict[str, Any]],
    source: dict[str, Any],
) -> None:
    if not added:
        return
    key = (
        seed_signature(seed),
        selector_kind,
        p968.leaf_signature(leaves),
        p966.added_signature(added),
    )
    if key not in by_key:
        by_key[key] = {
            "added": [dict(item) for item in added],
            "completion_mode": completion_mode,
            "completion_scheme": completion_scheme,
            "leaves": {row_key: set(row_leaves) for row_key, row_leaves in leaves.items()},
            "selector_kind": selector_kind,
            "sources": [source],
        }
    else:
        by_key[key]["sources"].append(source)


def p967_subset_specs(
    p967_payload: dict[str, Any],
    seed: dict[str, Any],
    by_key: dict[tuple[Any, ...], dict[str, Any]],
) -> None:
    for audit in p967_payload.get("audit_results") or []:
        audit_seed = audit.get("seed") or {}
        if seed_signature(audit_seed) != seed_signature(seed):
            continue
        added = p967.added_leaves(audit_seed, audit.get("completion") or {})
        for size in range(1, len(added) + 1):
            for subset in itertools.combinations(added, size):
                subset_added = [dict(item) for item in subset]
                label = p966.added_signature(subset_added)
                add_spec(
                    by_key,
                    seed,
                    "p967_event_subset",
                    "p967_added_subset",
                    f"extra{size}:{label}",
                    add_to_leaves(seed, subset_added),
                    subset_added,
                    {
                        "audit_added_signature": audit.get("added_signature"),
                        "audit_completion_selector": (audit.get("completion") or {}).get("selector"),
                        "audit_early_stop_ops": (audit.get("early_stop") or {}).get("ops"),
                        "kind": "p967_added_subset",
                    },
                )


def public_specs(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    modes: list[str],
    schemes: list[str],
    residue_modulus: int,
    by_key: dict[tuple[Any, ...], dict[str, Any]],
) -> None:
    for mode in modes:
        for scheme in schemes:
            leaves, added = p963.completion_leaves(materialized, seed, mode, scheme, residue_modulus)
            add_spec(
                by_key,
                seed,
                "public_completion",
                mode,
                scheme,
                leaves,
                added,
                {"completion_mode": mode, "completion_scheme": scheme, "kind": "public_completion"},
            )


def oracle_specs(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    max_extra_leaves: int,
    by_key: dict[tuple[Any, ...], dict[str, Any]],
) -> None:
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
    for size in range(1, max(0, int(max_extra_leaves)) + 1):
        for subset in itertools.combinations(extras, size):
            added = [dict(item) for item in subset]
            label = p966.added_signature(added)
            add_spec(
                by_key,
                seed,
                "oracle_completion",
                "oracle",
                f"extra{size}:{label}",
                add_to_leaves(seed, added),
                added,
                {"completion_mode": "oracle", "completion_scheme": f"extra{size}:{label}", "kind": "oracle_completion"},
            )


def completion_specs(
    p967_payload: dict[str, Any],
    materialized: dict[str, Any],
    seed: dict[str, Any],
    modes: list[str],
    schemes: list[str],
    residue_modulus: int,
    max_extra_leaves: int,
) -> list[dict[str, Any]]:
    by_key: dict[tuple[Any, ...], dict[str, Any]] = {}
    p967_subset_specs(p967_payload, seed, by_key)
    public_specs(materialized, seed, modes, schemes, residue_modulus, by_key)
    oracle_specs(materialized, seed, max_extra_leaves, by_key)
    specs = list(by_key.values())
    specs.sort(
        key=lambda row: (
            {"public_completion": 0, "p967_event_subset": 1, "oracle_completion": 2}.get(str(row.get("selector_kind")), 9),
            len(row.get("added") or []),
            p966.added_signature(row.get("added") or []),
            row.get("completion_mode") or "",
            row.get("completion_scheme") or "",
        )
    )
    return specs


def verified_rank_at_budget(early: dict[str, Any], expected_secret: int, budget_ops: int) -> bool:
    return (
        bool(early.get("public_key_verified"))
        and int_value(early.get("rank")) >= 3
        and early.get("derived_secret") == expected_secret
        and int_value(early.get("ops"), 10**9) <= int(budget_ops)
    )


def verified_rank3(early: dict[str, Any], expected_secret: int) -> bool:
    return (
        bool(early.get("public_key_verified"))
        and int_value(early.get("rank")) >= 3
        and early.get("derived_secret") == expected_secret
    )


def audit_completion(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    seed: dict[str, Any],
    base_events: list[dict[str, Any]],
    spec: dict[str, Any],
    expected_secret: int,
    budget_ops: int,
) -> dict[str, Any]:
    leaves = spec["leaves"]
    added = spec["added"]
    label = f"{seed.get('selector')}+{spec.get('completion_mode')}:{spec.get('completion_scheme')}"
    scan = p961.scan_from_leaves(verifier, materialized, pair, leaves, label, str(spec.get("selector_kind")))
    candidate_events, candidate_metadata = p966.collect_added_candidate_events(
        verifier,
        materialized,
        leaves,
        added,
    )
    derive_row_key = p967.row_keys(seed)[0]
    built = materialized["built_by_row"][derive_row_key]
    rho = int_value(seed.get("generic_rho_steps"))
    seed_ops = int_value(seed.get("ops"))
    full_completion_ops = int_value(scan.get("ops"))
    non_event_marginal_ops = full_completion_ops - seed_ops - 2 * len(candidate_events)
    accounting_valid = non_event_marginal_ops >= 0
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
            3,
        )
    else:
        early = {
            "accepted_relation_count": 0,
            "below_rho": False,
            "derived_secret": None,
            "ops": full_completion_ops,
            "ops_over_rho": round(full_completion_ops / max(1, rho), 8),
            "processed_candidate_events": len(candidate_events),
            "public_key_verified": False,
            "rank": 0,
            "saved_verification_ops": 0,
            "skipped_candidate_events": 0,
            "stop_event": None,
            "success": False,
        }
    budget_success = verified_rank_at_budget(early, expected_secret, budget_ops)
    return {
        "accepted_added_relation_count": candidate_metadata.get("accepted_relation_count"),
        "accounting_valid": accounting_valid,
        "added_leaf_count": len(added),
        "added_signature": p966.added_signature(added),
        "budget_success": budget_success,
        "candidate_event_count": len(candidate_events),
        "candidate_event_signatures": [p966.compact_event(event) for event in candidate_events],
        "completion_leaves": p968.compact_leaves(leaves),
        "completion_mode": spec.get("completion_mode"),
        "completion_scheme": spec.get("completion_scheme"),
        "early_stop": early,
        "full_completion_scan": p968.compact_scan(scan),
        "full_completion_ops": full_completion_ops,
        "full_completion_ops_over_rho": scan.get("ops_over_rho"),
        "non_event_marginal_ops": non_event_marginal_ops,
        "rho": rho,
        "seed_ops": seed_ops,
        "seed_selector": seed.get("selector"),
        "selector_kind": spec.get("selector_kind"),
        "sources": spec.get("sources") or [],
    }


def audit_seed(
    args: argparse.Namespace,
    p967_payload: dict[str, Any],
    seed: dict[str, Any],
    modes: list[str],
    schemes: list[str],
) -> dict[str, Any]:
    verifier, pair, materialized = p964.source_and_materialized(args, p967.row_keys(seed))
    base_events = p965.seed_events(verifier, materialized, seed)
    derive_row_key = p967.row_keys(seed)[0]
    base_derived = p965.public_derive(verifier, materialized["built_by_row"][derive_row_key], base_events)
    specs = completion_specs(
        p967_payload,
        materialized,
        seed,
        modes,
        schemes,
        int(args.residue_modulus),
        int(args.max_oracle_extra_leaves),
    )
    results = [
        audit_completion(
            verifier,
            materialized,
            pair,
            seed,
            base_events,
            spec,
            int(args.expected_secret),
            int(args.budget_ops),
        )
        for spec in specs
    ]
    results.sort(
        key=lambda row: (
            not bool(row.get("budget_success")),
            not verified_rank3(row.get("early_stop") or {}, int(args.expected_secret)),
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            {"public_completion": 0, "p967_event_subset": 1, "oracle_completion": 2}.get(str(row.get("selector_kind")), 9),
            row.get("added_signature") or "",
        )
    )
    return {
        "base_control": {
            "base_event_count": len(base_events),
            "derived_secret": base_derived.get("derived_secret"),
            "public_key_verified": bool(base_derived.get("public_key_verified")),
            "rank": int_value(base_derived.get("rank")),
        },
        "completion_results": results,
        "materialization": {
            "errors": materialized.get("errors") or [],
            "source": materialized.get("source_path"),
        },
        "seed": compact_result(seed),
        "spec_count": len(specs),
    }


def summarize(seed_audits: list[dict[str, Any]], expected_secret: int) -> dict[str, Any]:
    results = [row for audit in seed_audits for row in audit.get("completion_results") or []]
    budget_successes = [row for row in results if row.get("budget_success")]
    public_budget = [row for row in budget_successes if row.get("selector_kind") == "public_completion"]
    event_budget = [row for row in budget_successes if row.get("selector_kind") == "p967_event_subset"]
    oracle_budget = [row for row in budget_successes if row.get("selector_kind") == "oracle_completion"]
    verified_rank3_results = [row for row in results if verified_rank3(row.get("early_stop") or {}, expected_secret)]
    full_scan_rank3 = [
        row
        for row in results
        if (row.get("full_completion_scan") or {}).get("public_key_verified")
        and int_value((row.get("full_completion_scan") or {}).get("rank")) >= 3
        and (row.get("full_completion_scan") or {}).get("derived_secret") == expected_secret
    ]
    best_budget = sorted(
        budget_successes,
        key=lambda row: (
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            {"public_completion": 0, "p967_event_subset": 1, "oracle_completion": 2}.get(str(row.get("selector_kind")), 9),
            row.get("added_signature") or "",
        ),
    )[0] if budget_successes else None
    best_rank3 = sorted(
        verified_rank3_results,
        key=lambda row: (
            int_value((row.get("early_stop") or {}).get("ops"), 10**9),
            row.get("selector_kind") or "",
            row.get("added_signature") or "",
        ),
    )[0] if verified_rank3_results else None
    claim = (
        "P969_PUBLIC_HELDOUT_RANK3_SEED_BUDGET_RESCUE_FOUND"
        if public_budget
        else "P969_EVENT_LOCAL_HELDOUT_RANK3_SEED_BUDGET_RESCUE_FOUND"
        if event_budget
        else "P969_ORACLE_HELDOUT_RANK3_SEED_BUDGET_RESCUE_FOUND_PUBLIC_OPEN"
        if oracle_budget
        else "P969_REPRODUCES_P967_NO_BUDGET_RESCUE"
        if any(int_value((row.get("early_stop") or {}).get("ops"), 10**9) == 123 for row in verified_rank3_results)
        else "NEGATIVE_RESULT_P969_COMPRESSED_SEED_BUDGET_RESCUE_NO_PUBLIC_EVENT"
        if full_scan_rank3
        else "NEGATIVE_RESULT_P969_NO_HELDOUT_RANK3_SEED_BUDGET_RESCUE"
    )
    return {
        "accounting_valid_count": sum(1 for row in results if row.get("accounting_valid")),
        "audited_completion_count": len(results),
        "best_budget_success": {
            "added_signature": best_budget.get("added_signature"),
            "early_stop": best_budget.get("early_stop"),
            "full_completion_ops": best_budget.get("full_completion_ops"),
            "non_event_marginal_ops": best_budget.get("non_event_marginal_ops"),
            "selector_kind": best_budget.get("selector_kind"),
            "seed_selector": best_budget.get("seed_selector"),
        }
        if best_budget
        else None,
        "best_verified_rank3": {
            "added_signature": best_rank3.get("added_signature"),
            "early_stop": best_rank3.get("early_stop"),
            "selector_kind": best_rank3.get("selector_kind"),
            "seed_selector": best_rank3.get("seed_selector"),
        }
        if best_rank3
        else None,
        "budget_success_count": len(budget_successes),
        "claim_status": claim,
        "event_local_budget_success_count": len(event_budget),
        "full_scan_rank3_count": len(full_scan_rank3),
        "oracle_budget_success_count": len(oracle_budget),
        "public_budget_success_count": len(public_budget),
        "rank2_seed_count": len(seed_audits),
        "verified_rank3_count": len(verified_rank3_results),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p967_payload = load_json(Path(args.p967))
    seeds = frontier_rank2_seeds(p967_payload, int(args.expected_secret))
    if int(args.max_seeds) > 0:
        seeds = seeds[: int(args.max_seeds)]
    modes = p963.parse_csv(args.completion_modes)
    schemes = p963.parse_csv(args.completion_schemes)
    seed_audits = [audit_seed(args, p967_payload, seed, modes, schemes) for seed in seeds]
    summary = summarize(seed_audits, int(args.expected_secret))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p967_result": str(args.p967),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "HELDOUT-ROW-PAIR: audits the P967 salt204+salt208 held-out row pair frontier.",
            "EVENT-LOCAL-SUBSET: P967 added-leaf subset successes are post-discovery compression diagnostics, not standalone public source selectors.",
            "PUBLIC-ORACLE-SEPARATION: public completion successes and oracle diagnostics are counted separately.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this audits rank-3 seed budget, not full relation collection, sparse linear algebra, rank-4 completion, or target descent.",
        ],
        "method": "p969_heldout_rank3_seed_budget_rescue",
        "parameters": {
            "budget_ops": int(args.budget_ops),
            "completion_modes": modes,
            "completion_schemes": schemes,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_oracle_extra_leaves": int(args.max_oracle_extra_leaves),
            "max_seeds": int(args.max_seeds),
            "p967": str(args.p967),
            "post_min": int(args.post_min),
            "residue_modulus": int(args.residue_modulus),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "schema": SCHEMA,
        "seed_audits": seed_audits,
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
    parser.add_argument("--budget-ops", type=int, default=122)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--completion-modes", default=p963.DEFAULT_COMPLETION_MODES)
    parser.add_argument("--completion-schemes", default=p963.DEFAULT_COMPLETION_SCHEMES)
    parser.add_argument("--max-oracle-extra-leaves", type=int, default=2)
    parser.add_argument("--max-seeds", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best = summary.get("best_budget_success") or {}
    best_early = best.get("early_stop") or {}
    print(
        f"claim={payload['claim_status']} "
        f"seeds={summary['rank2_seed_count']} "
        f"audited={summary['audited_completion_count']} "
        f"budget_success={summary['budget_success_count']} "
        f"public_budget={summary['public_budget_success_count']} "
        f"event_local_budget={summary['event_local_budget_success_count']} "
        f"oracle_budget={summary['oracle_budget_success_count']} "
        f"verified_rank3={summary['verified_rank3_count']} "
        f"best_budget_ops={best_early.get('ops')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
