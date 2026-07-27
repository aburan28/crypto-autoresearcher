#!/usr/bin/env python3
"""P963 rank-3 completion-cost audit."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

import frontier_signed_eval_cover_row_side_sketch_fresh_salt_filter_rescue_guarded_relation_harvester_static_bank_shared_challenge_salt_neighborhood_loto_leaf_public_probe as leaf_public_probe  # noqa: E402
import low_term_total2_p959_fixed_public_rematerialization_audit as p959  # noqa: E402
import low_term_total2_p961_fixed_public_hybrid_cost_squeeze as p961  # noqa: E402
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p963_rank3_completion_cost_audit.md"
DEFAULT_P962 = STATE_DIR / "low_term_total2_p962_fixed_public_selector_frontier_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p963_rank3_completion_cost_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p963_rank3_completion_cost_audit.v1"
DEFAULT_COMPLETION_MODES = ",".join(
    [
        "low_term_span",
        "low_term_support",
        "hybrid_support_monic_b",
        "cost_hybrid_support_monic_b",
        "hybrid_double_monic_b",
        "low_monic_b",
        "low_monic_c",
        "double_pair_first",
        "cost_double_pair_first",
        "hash_leaf",
    ]
)
DEFAULT_COMPLETION_SCHEMES = "global_extra1,global_extra2,perrow_extra1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_csv(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 10**18) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def seed_records(p962: dict[str, Any], expected_secret: int) -> list[dict[str, Any]]:
    out = []
    seen: set[tuple[str, str, tuple[tuple[str, tuple[int, ...]], ...]]] = set()
    for row in p962.get("results") or []:
        if not row.get("public_key_verified"):
            continue
        if not row.get("below_rho"):
            continue
        if int_value(row.get("rank")) != 3:
            continue
        if row.get("derived_secret") != expected_secret:
            continue
        leaves = tuple(
            sorted(
                (
                    str(result.get("row_key")),
                    tuple(int(leaf) for leaf in result.get("leaf_indices") or []),
                )
                for result in row.get("row_results") or []
            )
        )
        key = (str(row.get("selector")), str(row.get("row_pair_key")), leaves)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    out.sort(key=lambda row: (float_value(row.get("ops_over_rho")), row.get("selector") or ""))
    return out


def row_pair_lookup(state_dir: Path, post_min: int, target: str) -> dict[tuple[str, ...], dict[str, Any]]:
    _cases, pairs = p959.source_row_pairs(state_dir, post_min, target)
    return {tuple(sorted(str(key) for key in pair.get("row_keys") or [])): pair for pair in pairs}


def seed_leaves(seed: dict[str, Any]) -> dict[str, set[int]]:
    return {
        str(row.get("row_key")): {int(leaf) for leaf in row.get("leaf_indices") or []}
        for row in seed.get("row_results") or []
    }


def candidate_leaf_set(row: dict[str, Any]) -> set[int]:
    return {
        int(leaf)
        for leaf in (leaf_public_probe.compress_probe.ranked(row).get("selected_leaf_indices") or [])
    }


def compact_feature(feature: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "leaf_index",
        "min_scout_pos",
        "double_pair_scout_count",
        "has_double_pair",
        "min_term_support_size",
        "min_term_span",
        "term_support_size",
        "monic_b",
        "monic_c",
        "max_shape_count",
    ]
    return {key: feature.get(key) for key in keys}


def feature_maps(materialized: dict[str, Any]) -> dict[str, dict[int, dict[str, Any]]]:
    return {
        row_key: {int(feature.get("leaf_index") or 0): feature for feature in features}
        for row_key, features in (materialized.get("feature_rows_by_row") or {}).items()
    }


def ranked_extra_candidates(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    mode: str,
    residue_modulus: int,
) -> list[dict[str, Any]]:
    spec = leaf_public_probe.LeafSelectorSpec(
        name=f"completion_{mode}",
        scope="mode",
        selection_mode="case_total",
        cap_per_row=0,
        total_leaf_cap=0,
        token_weight=0.0,
        leaf_index_weight=0.0,
        residue_weight=0.0,
        low_index_weight=0.0,
        public_mode=mode,
    )
    current = seed_leaves(seed)
    by_feature = feature_maps(materialized)
    candidates = []
    for row in materialized["selected_rows"]:
        row_key = str(leaf_public_probe.row_key(row))
        row_current = current.get(row_key, set())
        for leaf in sorted(candidate_leaf_set(row) - row_current):
            feature = by_feature.get(row_key, {}).get(leaf)
            if feature is None:
                continue
            score = leaf_public_probe.leaf_score(
                feature,
                Counter(),
                Counter(),
                Counter(),
                spec,
                int(residue_modulus),
            )
            row_ops = (
                leaf_public_probe.compress_probe.row_ops(row)
                if leaf_public_probe.row_cost_tiebreaker(spec)
                else 0
            )
            candidates.append(
                {
                    "feature": compact_feature(feature),
                    "leaf": int(leaf),
                    "row_key": row_key,
                    "score": [str(item) for item in score],
                    "sort_key": (score, row_ops, row_key, int(leaf)),
                }
            )
    candidates.sort(key=lambda row: row["sort_key"])
    for row in candidates:
        row.pop("sort_key", None)
    return candidates


def completion_leaves(
    materialized: dict[str, Any],
    seed: dict[str, Any],
    mode: str,
    scheme: str,
    residue_modulus: int,
) -> tuple[dict[str, set[int]], list[dict[str, Any]]]:
    current = {row_key: set(leaves) for row_key, leaves in seed_leaves(seed).items()}
    extras = ranked_extra_candidates(materialized, seed, mode, residue_modulus)
    selected_extras = []
    if scheme.startswith("global_extra"):
        count = int(scheme.removeprefix("global_extra"))
        selected_extras = extras[: max(0, count)]
    elif scheme.startswith("perrow_extra"):
        count = int(scheme.removeprefix("perrow_extra"))
        by_row: dict[str, list[dict[str, Any]]] = {}
        for extra in extras:
            by_row.setdefault(str(extra["row_key"]), []).append(extra)
        for row_key in sorted(by_row):
            selected_extras.extend(by_row[row_key][: max(0, count)])
        selected_extras.sort(key=lambda row: (str(row["row_key"]), int(row["leaf"])))
    else:
        raise ValueError(f"unsupported completion scheme: {scheme}")
    for extra in selected_extras:
        current.setdefault(str(extra["row_key"]), set()).add(int(extra["leaf"]))
    return current, selected_extras


def result_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(row.get("public_key_verified")),
        -int_value(row.get("rank")),
        not bool(row.get("below_rho")),
        float_value(row.get("ops_over_rho")),
        int_value(row.get("marginal_ops")),
        row.get("completion_mode") or "",
        row.get("completion_scheme") or "",
        row.get("seed_selector") or "",
    )


def attach_completion_metrics(
    scan: dict[str, Any],
    seed: dict[str, Any],
    added: list[dict[str, Any]],
    completion_mode: str,
    completion_scheme: str,
    selector_kind: str,
) -> dict[str, Any]:
    seed_ops = int_value(seed.get("ops"))
    rho = int_value(scan.get("generic_rho_steps"))
    ops = int_value(scan.get("ops"))
    return {
        "added_leaves": added,
        "below_rho": bool(scan.get("below_rho")),
        "completion_mode": completion_mode,
        "completion_scheme": completion_scheme,
        "derived_secret": scan.get("derived_secret"),
        "generic_rho_steps": rho,
        "marginal_ops": ops - seed_ops,
        "ops": ops,
        "ops_over_rho": scan.get("ops_over_rho"),
        "public_key_verified": bool(scan.get("public_key_verified")),
        "rank": int_value(scan.get("rank")),
        "rank_gain": int_value(scan.get("rank")) - int_value(seed.get("rank")),
        "relation_count": int_value(scan.get("relation_count")),
        "relation_gain": int_value(scan.get("relation_count")) - int_value(seed.get("relation_count")),
        "remaining_budget": rho - seed_ops,
        "rho_shortfall": max(0, ops - rho),
        "row_results": scan.get("row_results") or [],
        "seed_ops": seed_ops,
        "seed_ops_over_rho": seed.get("ops_over_rho"),
        "seed_rank": seed.get("rank"),
        "seed_relation_count": seed.get("relation_count"),
        "seed_selector": seed.get("selector"),
        "selector_kind": selector_kind,
    }


def public_completions(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    seed: dict[str, Any],
    modes: list[str],
    schemes: list[str],
    residue_modulus: int,
) -> list[dict[str, Any]]:
    results = []
    for mode in modes:
        for scheme in schemes:
            leaves, added = completion_leaves(materialized, seed, mode, scheme, residue_modulus)
            if not added:
                continue
            scan = p961.scan_from_leaves(
                verifier,
                materialized,
                pair,
                leaves,
                f"{seed.get('selector')}+{mode}:{scheme}",
                "public_completion",
            )
            results.append(attach_completion_metrics(scan, seed, added, mode, scheme, "public_completion"))
    results.sort(key=result_sort_key)
    return results


def oracle_completions(
    verifier: Any,
    materialized: dict[str, Any],
    pair: dict[str, Any],
    seed: dict[str, Any],
    max_extra_leaves: int,
) -> list[dict[str, Any]]:
    by_feature = feature_maps(materialized)
    current = seed_leaves(seed)
    extras = []
    for row in materialized["selected_rows"]:
        row_key = str(leaf_public_probe.row_key(row))
        for leaf in sorted(candidate_leaf_set(row) - current.get(row_key, set())):
            feature = by_feature.get(row_key, {}).get(leaf)
            extras.append(
                {
                    "feature": compact_feature(feature or {"leaf_index": leaf}),
                    "leaf": int(leaf),
                    "row_key": row_key,
                }
            )
    results = []
    for size in range(1, max(0, int(max_extra_leaves)) + 1):
        for subset in itertools.combinations(extras, size):
            leaves = {row_key: set(row_leaves) for row_key, row_leaves in current.items()}
            for extra in subset:
                leaves.setdefault(str(extra["row_key"]), set()).add(int(extra["leaf"]))
            label = "+".join(f"{extra['row_key'].split(':')[-1]}:{extra['leaf']}" for extra in subset)
            scan = p961.scan_from_leaves(
                verifier,
                materialized,
                pair,
                leaves,
                f"{seed.get('selector')}+oracle:{label}",
                "oracle_completion",
            )
            results.append(
                attach_completion_metrics(
                    scan,
                    seed,
                    [dict(extra) for extra in subset],
                    "oracle",
                    f"extra{size}",
                    "oracle_completion",
                )
            )
    results.sort(key=result_sort_key)
    return results


def compact_seed(seed: dict[str, Any]) -> dict[str, Any]:
    return {
        "below_rho": bool(seed.get("below_rho")),
        "derived_secret": seed.get("derived_secret"),
        "generic_rho_steps": seed.get("generic_rho_steps"),
        "ops": seed.get("ops"),
        "ops_over_rho": seed.get("ops_over_rho"),
        "public_key_verified": bool(seed.get("public_key_verified")),
        "rank": seed.get("rank"),
        "relation_count": seed.get("relation_count"),
        "remaining_budget": int_value(seed.get("generic_rho_steps")) - int_value(seed.get("ops")),
        "row_pair_key": seed.get("row_pair_key"),
        "row_results": seed.get("row_results") or [],
        "selector": seed.get("selector"),
    }


def summarize(seed_results: list[dict[str, Any]], public_results: list[dict[str, Any]], oracle_results: list[dict[str, Any]], expected_secret: int) -> dict[str, Any]:
    public_rank4 = [
        row
        for row in public_results
        if row.get("public_key_verified")
        and int_value(row.get("rank")) >= 4
        and row.get("derived_secret") == expected_secret
    ]
    public_rank4_below = [row for row in public_rank4 if row.get("below_rho")]
    oracle_rank4 = [
        row
        for row in oracle_results
        if row.get("public_key_verified")
        and int_value(row.get("rank")) >= 4
        and row.get("derived_secret") == expected_secret
    ]
    oracle_rank4_below = [row for row in oracle_rank4 if row.get("below_rho")]
    public_below_any = [
        row
        for row in public_results
        if row.get("public_key_verified") and row.get("derived_secret") == expected_secret and row.get("below_rho")
    ]
    claim = (
        "P963_PUBLIC_RANK3_COMPLETION_BELOW_RHO"
        if public_rank4_below
        else "P963_ORACLE_RANK3_COMPLETION_BELOW_RHO_PUBLIC_OPEN"
        if oracle_rank4_below
        else "NEGATIVE_RESULT_P963_RANK3_COMPLETION_COST_EXCEEDS_RHO"
        if public_rank4 or oracle_rank4
        else "NEGATIVE_RESULT_P963_RANK3_COMPLETION_NO_RANK4"
    )
    return {
        "best_oracle_rank4_completion": oracle_rank4[0] if oracle_rank4 else None,
        "best_public_below_rho_any_rank_completion": sorted(public_below_any, key=result_sort_key)[0] if public_below_any else None,
        "best_public_rank4_completion": public_rank4[0] if public_rank4 else None,
        "claim_status": claim,
        "oracle_completion_count": len(oracle_results),
        "oracle_rank4_below_rho_count": len(oracle_rank4_below),
        "oracle_rank4_count": len(oracle_rank4),
        "public_below_rho_any_rank_count": len(public_below_any),
        "public_completion_count": len(public_results),
        "public_rank4_below_rho_count": len(public_rank4_below),
        "public_rank4_count": len(public_rank4),
        "seed_count": len(seed_results),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p962 = load_json(Path(args.p962))
    seeds = seed_records(p962, int(args.expected_secret))
    pair_by_keys = row_pair_lookup(Path(args.state_dir), int(args.post_min), args.target)
    cases, _pairs = p959.source_row_pairs(Path(args.state_dir), int(args.post_min), args.target)
    source_path = p959.choose_source(cases, int(args.fixed_transfer))
    source = p959.p957.load_json(source_path)
    params = repair_probe.source_parameters(source)
    verifier, records, config_source, specs_by_target = repair_probe.build_specs(params)
    public_results = []
    oracle_results = []
    seed_results = []
    materialization_errors = []
    public_values = set()
    modes = parse_csv(args.completion_modes)
    schemes = parse_csv(args.completion_schemes)
    for seed in seeds:
        pair_key = tuple(sorted(str(key) for key in seed.get("row_keys") or []))
        pair = pair_by_keys.get(pair_key)
        if pair is None:
            materialization_errors.append({"error": "pair_not_found", "row_keys": list(pair_key), "seed": seed.get("selector")})
            continue
        materialized = p961.build_materialized(verifier, records, config_source, specs_by_target, pair, source, args)
        for public in p961.public_values_for(materialized):
            public_values.add(tuple(int(value) for value in public))
        for error in materialized.get("errors") or []:
            materialization_errors.append({"error": error, "row_keys": list(pair_key), "seed": seed.get("selector")})
        seed_scan = p961.scan_from_leaves(
            verifier,
            materialized,
            pair,
            seed_leaves(seed),
            str(seed.get("selector")),
            "seed_replay",
        )
        seed_payload = compact_seed(seed)
        seed_payload.update(
            {
                "replay_matches_rank": int_value(seed_scan.get("rank")) == int_value(seed.get("rank")),
                "replay_matches_ops": int_value(seed_scan.get("ops")) == int_value(seed.get("ops")),
                "replay_public_key_verified": bool(seed_scan.get("public_key_verified")),
            }
        )
        seed_results.append(seed_payload)
        public_results.extend(
            public_completions(
                verifier,
                materialized,
                pair,
                seed,
                modes,
                schemes,
                int(args.residue_modulus),
            )
        )
        oracle_results.extend(
            oracle_completions(
                verifier,
                materialized,
                pair,
                seed,
                int(args.max_oracle_extra_leaves),
            )
        )
    public_results.sort(key=result_sort_key)
    oracle_results.sort(key=result_sort_key)
    summary = summarize(seed_results, public_results, oracle_results, int(args.expected_secret))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p961_script": str(Path(p961.__file__)),
            "p962_result": str(args.p962),
            "script": str(Path(__file__)),
            "source": str(source_path),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "FIXED-PUBLIC: completions reuse the P962 fixed transfer challenge.",
            "PUBLIC-COMPLETION: public completion modes use public leaf features only.",
            "ORACLE-COMPLETION-DIAGNOSTIC: oracle subsets are lower bounds, not promoted algorithms.",
            "COMPONENT-SIGNAL-NOT-END-TO-END: this audits local relation completion, not full collection or target descent.",
        ],
        "materialization": {
            "errors": materialization_errors,
            "fixed_challenge_seed": f"{repair_probe.probe_args_from_source(source).seed}:shared-transfer:{int(args.fixed_transfer)}:{args.target}",
            "public_values": [list(value) for value in sorted(public_values)],
        },
        "method": "p963_rank3_completion_cost_audit",
        "oracle_completion_results": oracle_results,
        "parameters": {
            "completion_modes": modes,
            "completion_schemes": schemes,
            "expected_secret": int(args.expected_secret),
            "fixed_transfer": int(args.fixed_transfer),
            "max_oracle_extra_leaves": int(args.max_oracle_extra_leaves),
            "p962": str(args.p962),
            "post_min": int(args.post_min),
            "target": args.target,
            "top_k": int(args.top_k),
        },
        "public_completion_results": public_results,
        "schema": SCHEMA,
        "seed_results": seed_results,
        "summary": summary,
        "top_oracle_completion_results": oracle_results[: int(args.top_result_limit)],
        "top_public_completion_results": public_results[: int(args.top_result_limit)],
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
    parser.add_argument("--completion-modes", default=DEFAULT_COMPLETION_MODES)
    parser.add_argument("--completion-schemes", default=DEFAULT_COMPLETION_SCHEMES)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--residue-modulus", type=int, default=p959.DEFAULT_RESIDUE_MODULUS)
    parser.add_argument("--max-oracle-extra-leaves", type=int, default=2)
    parser.add_argument("--top-result-limit", type=int, default=32)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    best_public = summary.get("best_public_rank4_completion") or {}
    best_oracle = summary.get("best_oracle_rank4_completion") or {}
    print(
        f"claim={payload['claim_status']} "
        f"seeds={summary['seed_count']} "
        f"public_completions={summary['public_completion_count']} "
        f"public_rank4={summary['public_rank4_count']} "
        f"public_rank4_below={summary['public_rank4_below_rho_count']} "
        f"oracle_rank4={summary['oracle_rank4_count']} "
        f"oracle_rank4_below={summary['oracle_rank4_below_rho_count']} "
        f"best_public_rank4_ops_over_rho={best_public.get('ops_over_rho')} "
        f"best_oracle_rank4_ops_over_rho={best_oracle.get('ops_over_rho')} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
