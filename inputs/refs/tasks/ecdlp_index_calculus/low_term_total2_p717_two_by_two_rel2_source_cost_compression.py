#!/usr/bin/env python3
"""P717 source-cost compression audit for P716 two-by-two rel2 hits."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p709_source_replay_no_archive_oracle as p709
import low_term_total2_p716_rel2_source_generation_enrichment as p716


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P716 = STATE_DIR / "low_term_total2_p716_rel2_source_generation_enrichment_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p717_two_by_two_rel2_source_cost_compression_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p716.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p716.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def compression_ratio(source_charge: float, fallback_charge: float, window_count: int) -> dict[str, Any]:
    total = source_charge + fallback_charge
    return {
        "beats_rho_marginal": bool(total < window_count),
        "source_charge_over_rho": round(source_charge, 8),
        "source_plus_fallback_over_rho": round(total, 8),
        "vs_independent_rho_over_rho": window_count,
    }


def compact_context(profile: dict[str, Any]) -> dict[str, Any]:
    scan = profile.get("scan") or {}
    return {
        "challenge_seed": profile.get("challenge_seed"),
        "cost_parts": profile.get("cost_parts") or {},
        "preassociation_filter_ops_over_rho": scan.get("preassociation_filter_ops_over_rho"),
        "relation_count": scan.get("relation_count"),
        "row_key": profile.get("row_key"),
        "row_pool_fingerprint": profile.get("row_pool_fingerprint"),
        "row_seed_prefix": profile.get("row_seed_prefix"),
        "scout_seed_prefix": profile.get("scout_seed_prefix"),
        "selected_leaf_indices": profile.get("selected_leaf_indices") or [],
        "selected_leaf_signature_keys": profile.get("selected_leaf_signature_keys") or [],
    }


def replay_with_profiles(source: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    verifier, contexts, product_factor, max_relations = p709.direct_source.timing_probe.selected_contexts_from_source_case(
        source,
        row["source_case"],
    )
    direct_rows, direct_ops, rho, row_profiles = p709.direct_source.timing_probe.direct_witness_rows(verifier, contexts)
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = p709.direct_source.direct_witness_probe.union_derive(verifier, direct_rows, built_by_row, "_scan")
    return {
        "context_count": len(contexts),
        "direct_ops": direct_ops,
        "direct_ops_over_rho": p709.direct_source.ratio(direct_ops, rho),
        "max_relations": max_relations,
        "product_factor": product_factor,
        "public_key_verified": bool(direct_union.get("union_public_key_verified")),
        "rank": int_value(direct_union.get("union_rank")),
        "rho": rho,
        "row_profiles": row_profiles,
        "union_derived_secret": direct_union.get("union_derived_secret"),
    }


def selected_attempts(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    build_args = argparse.Namespace(
        max_transfer=args.max_transfer,
        min_transfer=args.min_transfer,
        p709=args.p709,
        source_pattern=args.source_pattern,
        target=args.target,
        thresholds="0.544,0.568,0.616,1.0",
    )
    reports, metadata = p716.build_window_reports(build_args)
    policy = p716.SourcePolicy("two_by_two_any_cost_le_1p0", "two_by_two_any", 1.0)
    attempts: list[dict[str, Any]] = []
    for report in reports:
        accepted = [row for row in report["candidates"] if p716.policy_accepts(policy, row)]
        accepted.sort(key=p716.row_sort_key)
        if not accepted:
            continue
        row = accepted[0]
        source = metadata["source_cache"][str(row["source"])]
        replay = replay_with_profiles(source, row)
        attempts.append(
            {
                "direct_ops_over_rho": float_value(replay.get("direct_ops_over_rho")),
                "hit": bool(replay.get("public_key_verified")),
                "rank": int_value(replay.get("rank")),
                "replay": replay,
                "row": p716.sample_row(row, None),
                "source": report["source"],
                "window_end": report["window_end"],
                "window_start": report["window_start"],
            }
        )
    return attempts, {
        "source_window_count": len(reports),
        "candidate_window_count": sum(1 for report in reports if report["candidates"]),
    }


def context_rows(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for attempt_index, attempt in enumerate(attempts):
        replay = attempt.get("replay") or {}
        for context_index, profile in enumerate(replay.get("row_profiles") or []):
            scan = profile.get("scan") or {}
            cost_parts = profile.get("cost_parts") or {}
            ops = int_value(cost_parts.get("reconstructed_preassociation_filter_ops"), int_value(scan.get("preassociation_filter_ops")))
            rows.append(
                {
                    "attempt_index": attempt_index,
                    "challenge_seed": profile.get("challenge_seed"),
                    "context_index": context_index,
                    "hit": bool(attempt.get("hit")),
                    "ops": ops,
                    "ops_over_rho": float_value(scan.get("preassociation_filter_ops_over_rho")),
                    "profile": profile,
                    "rho": int_value((attempt.get("replay") or {}).get("rho")),
                    "row_key": profile.get("row_key"),
                    "row_pool_ops": int_value((profile.get("cost_parts") or {}).get("row_pool_ops")),
                    "row_seed_prefix": profile.get("row_seed_prefix"),
                    "scan": scan,
                    "selected_leaf_indices": tuple(int_value(value) for value in profile.get("selected_leaf_indices") or []),
                    "selected_leaf_signature_keys": tuple(str(value) for value in profile.get("selected_leaf_signature_keys") or []),
                    "source": attempt.get("source"),
                    "window_start": attempt.get("window_start"),
                }
            )
    return rows


def sum_ops_over_rho(rows: list[dict[str, Any]], ops_key: str = "ops") -> float:
    total = 0.0
    for row in rows:
        rho = int_value(row.get("rho"), 0)
        if rho:
            total += int_value(row.get(ops_key)) / rho
        else:
            total += float_value(row.get("ops_over_rho"))
    return round(total, 8)


def grouped_min_charge(rows: list[dict[str, Any]], key_fn) -> tuple[float, int, list[dict[str, Any]]]:
    groups: dict[Any, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(key_fn(row), []).append(row)
    chosen = []
    for key, members in groups.items():
        best = min(members, key=lambda row: (float_value(row.get("ops_over_rho"), 999999.0), str(row.get("source"))))
        chosen.append({"key": repr(key), "member_count": len(members), "sample": compact_context(best.get("profile") or {})})
    charge = sum(float_value(item["sample"].get("preassociation_filter_ops_over_rho")) for item in chosen)
    return round(charge, 8), len(groups), sorted(chosen, key=lambda item: (-int_value(item.get("member_count")), item["key"]))[:12]


def row_pool_reuse_charge(rows: list[dict[str, Any]]) -> tuple[float, dict[str, Any]]:
    total_ops_over_rho = sum_ops_over_rho(rows)
    row_pool_all = 0.0
    for row in rows:
        rho = int_value(row.get("rho"), 0)
        row_pool_all += int_value(row.get("row_pool_ops")) / rho if rho else 0.0
    row_pool_by_seed: dict[str, float] = {}
    for row in rows:
        seed = str(row.get("row_seed_prefix"))
        rho = int_value(row.get("rho"), 0)
        charge = int_value(row.get("row_pool_ops")) / rho if rho else 0.0
        row_pool_by_seed[seed] = min(row_pool_by_seed.get(seed, charge), charge)
    shared_pool_charge = sum(row_pool_by_seed.values())
    compressed = total_ops_over_rho - row_pool_all + shared_pool_charge
    return round(compressed, 8), {
        "row_pool_charge_all_over_rho": round(row_pool_all, 8),
        "row_pool_charge_shared_over_rho": round(shared_pool_charge, 8),
        "unique_row_seed_prefix_count": len(row_pool_by_seed),
    }


def model_report(name: str, source_charge: float, fallback_charge: float, window_count: int, extra: dict[str, Any]) -> dict[str, Any]:
    return {
        **compression_ratio(source_charge, fallback_charge, window_count),
        **extra,
        "model": name,
    }


def determine_claim(summary: dict[str, Any], models: list[dict[str, Any]]) -> str:
    admissible = [
        model
        for model in models
        if model.get("model") in {"exact_context_reuse", "same_challenge_leaf_signature_reuse", "row_pool_reuse"}
    ]
    if any(model.get("beats_rho_marginal") for model in admissible):
        return "P717_ADMISSIBLE_ROW_REUSE_BEATS_RHO_FOR_TWO_BY_TWO_REL2"
    lower_bound = next((model for model in models if model.get("model") == "global_row_key_full_reuse_lower_bound"), {})
    if lower_bound.get("beats_rho_marginal"):
        return "P717_EXACT_REUSE_NEGATIVE_BUT_GLOBAL_ROWKEY_LOWER_BOUND_BELOW_RHO"
    if int_value(summary.get("context_reuse_duplicate_count")):
        return "P717_ROW_REUSE_HAS_SAVINGS_BUT_REMAINS_ABOVE_RHO"
    return "NEGATIVE_RESULT_P717_NO_ADMISSIBLE_ROW_REUSE_SAVING"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    attempts, meta = selected_attempts(args)
    rows = context_rows(attempts)
    hit_count = sum(1 for attempt in attempts if attempt.get("hit"))
    fallback_charge = float_value(meta["source_window_count"] - hit_count)
    independent_charge = round(sum(float_value(attempt.get("direct_ops_over_rho")) for attempt in attempts), 8)
    exact_charge, exact_group_count, exact_samples = grouped_min_charge(
        rows,
        lambda row: (row.get("source"), row.get("row_key"), row.get("selected_leaf_indices")),
    )
    challenge_signature_charge, challenge_signature_group_count, challenge_signature_samples = grouped_min_charge(
        rows,
        lambda row: (
            row.get("challenge_seed"),
            row.get("row_key"),
            row.get("selected_leaf_signature_keys"),
        ),
    )
    row_key_signature_charge, row_key_signature_group_count, row_key_signature_samples = grouped_min_charge(
        rows,
        lambda row: (row.get("row_key"), row.get("selected_leaf_signature_keys")),
    )
    global_row_key_charge, global_row_key_group_count, global_row_key_samples = grouped_min_charge(
        rows,
        lambda row: row.get("row_key"),
    )
    row_pool_charge, row_pool_meta = row_pool_reuse_charge(rows)
    models = [
        model_report(
            "independent_direct",
            independent_charge,
            fallback_charge,
            meta["source_window_count"],
            {"admissibility": "verified_individual_replay", "group_count": len(rows)},
        ),
        model_report(
            "exact_context_reuse",
            exact_charge,
            fallback_charge,
            meta["source_window_count"],
            {
                "admissibility": "replay_compatible_same_source_context",
                "group_count": exact_group_count,
                "samples": exact_samples,
            },
        ),
        model_report(
            "same_challenge_leaf_signature_reuse",
            challenge_signature_charge,
            fallback_charge,
            meta["source_window_count"],
            {
                "admissibility": "same_challenge_same_leaf_signature",
                "group_count": challenge_signature_group_count,
                "samples": challenge_signature_samples,
            },
        ),
        model_report(
            "row_pool_reuse",
            row_pool_charge,
            fallback_charge,
            meta["source_window_count"],
            {"admissibility": "heuristic_public_row_pool_reuse", **row_pool_meta},
        ),
        model_report(
            "row_key_leaf_signature_lower_bound",
            row_key_signature_charge,
            fallback_charge,
            meta["source_window_count"],
            {
                "admissibility": "lower_bound_cross_challenge_leaf_signature_reuse",
                "group_count": row_key_signature_group_count,
                "samples": row_key_signature_samples,
            },
        ),
        model_report(
            "global_row_key_full_reuse_lower_bound",
            global_row_key_charge,
            fallback_charge,
            meta["source_window_count"],
            {
                "admissibility": "optimistic_lower_bound_not_verified",
                "group_count": global_row_key_group_count,
                "samples": global_row_key_samples,
            },
        ),
    ]
    context_count = len(rows)
    exact_duplicate_count = context_count - exact_group_count
    challenge_signature_duplicate_count = context_count - challenge_signature_group_count
    summary = {
        "attempt_count": len(attempts),
        "context_count": context_count,
        "context_reuse_duplicate_count": exact_duplicate_count,
        "factor_bank_charge_over_rho": factor_charge,
        "fallback_charge_over_rho": fallback_charge,
        "hit_count": hit_count,
        "independent_source_charge_over_rho": independent_charge,
        "new_bank_source_threshold_over_rho": round(hit_count - factor_charge, 8),
        "rho_baseline_over_rho": meta["source_window_count"],
        "same_challenge_leaf_signature_duplicate_count": challenge_signature_duplicate_count,
        "source_window_count": meta["source_window_count"],
        "source_threshold_over_rho": hit_count,
    }
    for model in models:
        summary[f"{model['model']}_source_charge_over_rho"] = model["source_charge_over_rho"]
        summary[f"{model['model']}_total_over_rho"] = model["source_plus_fallback_over_rho"]
        summary[f"{model['model']}_beats_rho_marginal"] = model["beats_rho_marginal"]
    claim_status = determine_claim(summary, models)
    return {
        "artifacts": {"p709": str(Path(args.p709)), "p716": str(Path(args.p716))},
        "claim_status": claim_status,
        "compression_models": models,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "Exact context reuse is the only same-source replay-compatible compression tested here.",
            "Row-pool reuse is heuristic; global row-key reuse is an optimistic lower bound, not a verified algorithm.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p717_two_by_two_rel2_source_cost_compression",
        "parameters": {
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "policy": "two_by_two_any_cost_le_1p0:budget1",
            "source_pattern": args.source_pattern,
            "target": args.target,
        },
        "schema": "ecdlp.low_term_total2_p717_two_by_two_rel2_source_cost_compression.v1",
        "summary": summary,
        "attempt_samples": [
            {
                "direct_ops_over_rho": attempt.get("direct_ops_over_rho"),
                "hit": attempt.get("hit"),
                "rank": attempt.get("rank"),
                "row": attempt.get("row"),
                "source": attempt.get("source"),
                "window_start": attempt.get("window_start"),
            }
            for attempt in attempts[:8]
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p716", default=str(DEFAULT_P716))
    parser.add_argument("--source-pattern", default=p716.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"compression_models": payload["compression_models"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
