#!/usr/bin/env python3
"""P605 pre-hit public context-fingerprint delta scout.

This diagnostic compares P601 selected positives against P602-P604 selected
misses using source-public context fingerprints built before direct witness
replay. Direct verifier labels are joined only for evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import low_term_total2_fixed_leaf_shared_context_audit_probe as context_probe
import low_term_total2_fixed_leaf_shared_product_timing_probe as timing_probe
import low_term_total2_p604_public_feature_delta_recurrence_scout as p604


p594 = p604.p594
p602 = p604.p602
p603 = p604.p603

STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCE = STATE_DIR / "low_term_total2_order9887_p601_phase4_right207_anchor9_salt206_source_21137_21148_probe.json"
DEFAULT_TRAIN_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p601_order9887_phase4_right207_anchor9_salt206_21137_21148_density_gate_probe.json"
DEFAULT_ADJACENT_SOURCE = STATE_DIR / "low_term_total2_order9887_p602_phase8_supply_phase2_rank_source_21149_21160_probe.json"
DEFAULT_ADJACENT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p602_order9887_phase8_supply_phase2_rank_21149_21160_density_gate_probe.json"
DEFAULT_HALF_SOURCE = STATE_DIR / "low_term_total2_order9887_p603_exact_phase8_phase2_recurrence_source_21221_21232_probe.json"
DEFAULT_HALF_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p603_order9887_exact_phase8_phase2_recurrence_21221_21232_density_gate_probe.json"
DEFAULT_FULL_SOURCE = STATE_DIR / "low_term_total2_order9887_p604_public_feature_delta_recurrence_source_21305_21316_probe.json"
DEFAULT_FULL_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p604_order9887_public_feature_delta_recurrence_21305_21316_density_gate_probe.json"
DEFAULT_SOURCE = STATE_DIR / "low_term_total2_order9887_p605_public_context_fingerprint_delta_source_21317_21328_probe.json"
DEFAULT_GATE = STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p605_order9887_public_context_fingerprint_delta_21317_21328_density_gate_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p605_public_context_fingerprint_delta_scout_21317_21328_probe.json"

EXCLUDED_LABEL_FIELDS = {
    "below_rho",
    "direct_below_rho_verified",
    "direct_ops_over_rho",
    "direct_verified",
    "ops_over_rho",
    "public_key_verified",
    "rank",
    "relation_count",
    "row_selector_public_key_verified",
}


def sha_token(value: Any, size: int = 20) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()[:size]


def source_data(paths: list[Path]) -> dict[str, dict[str, Any]]:
    return {str(path): json.loads(path.read_text()) for path in paths}


def row_salt(row_key: str) -> str:
    match = re.search(r"salt(\d+)", row_key)
    return match.group(1) if match else "unknown"


def source_case(cache: dict[str, dict[str, Any]], row: p594.Feature) -> dict[str, Any]:
    source = cache[str(row["source_artifact"])]
    return context_probe.find_source_case(
        source,
        str(row["target"]),
        int(row["transfer_index"]),
        str(row["selector"]),
        int(row["top_k"]),
    )


def raw_source_tokens(case: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for key in (
        "base_selector",
        "mutation_kind",
        "policy_role",
        "row_pair_public_id",
        "row_selector",
        "selected_leaf_count",
        "selected_row_count",
        "source_verified",
        "target",
        "top_k",
    ):
        if key in EXCLUDED_LABEL_FIELDS:
            continue
        tokens.add(f"raw:{key}={case.get(key)}")
    tokens.add(f"raw:left_leaf_indices={json.dumps(case.get('left_leaf_indices') or [], sort_keys=True)}")
    tokens.add(f"raw:right_leaf_indices={json.dumps(case.get('right_leaf_indices') or [], sort_keys=True)}")
    tokens.add(f"raw:right_anchor={case.get('right_anchor')}")
    row_keys = [str(item) for item in case.get("row_keys") or []]
    tokens.add(f"raw:row_key_salts={','.join(row_salt(row_key) for row_key in row_keys)}")
    return tokens


def selected_leaf_roots(context: dict[str, Any], leaf_index: int) -> list[int]:
    built = context["built"]
    components = context["components"]
    p = p594.int_value(built.get("p"))
    leaf = components["leaves"][int(leaf_index)]
    roots = timing_probe.association_probe.roots_in_hit_set(
        leaf.get("poly") or [],
        components.get("hit_roots") or [],
        p,
    )
    return [int(root) for root in roots]


def context_tokens(cache: dict[str, dict[str, Any]], row: p594.Feature) -> dict[str, Any]:
    case = source_case(cache, row)
    _verifier, contexts, _product_factor, _max_relations = timing_probe.selected_contexts_from_source_case(
        cache[str(row["source_artifact"])],
        case,
    )
    tokens = raw_source_tokens(case)
    context_profiles: list[dict[str, Any]] = []
    total_selected_leaf_hit_roots = 0
    selected_leaf_signature_keys: list[str] = []
    selected_leaf_hit_signature_keys: list[str] = []
    row_context_shapes: list[dict[str, Any]] = []
    for context in contexts:
        built = context["built"]
        components = context["components"]
        selected = sorted(int(leaf) for leaf in context.get("selected_leaf_indices") or [])
        selected_profiles = []
        row_leaf_signature_keys = []
        row_hit_count = 0
        for leaf_index in selected:
            leaf = components["leaves"][leaf_index]
            signature = context_probe.leaf_signature(leaf)
            signature_key = sha_token(signature)
            selected_leaf_signature_keys.append(signature_key)
            row_leaf_signature_keys.append(signature_key)
            roots = selected_leaf_roots(context, leaf_index)
            total_selected_leaf_hit_roots += len(roots)
            row_hit_count += len(roots)
            tokens.add(f"leafsig:item={signature_key}")
            tokens.add(f"leafhit:count={len(roots)}")
            tokens.add(f"leafhit:has_hit={int(bool(roots))}")
            if roots:
                selected_leaf_hit_signature_keys.append(signature_key)
                tokens.add(f"leafhit:sig_has_hit={signature_key}")
            selected_profiles.append(
                {
                    "leaf_index": leaf_index,
                    "selected_hit_root_count": len(roots),
                    "signature_key": signature_key,
                }
            )
        row_shape = {
            "hit_roots_count": len(components.get("hit_roots") or []),
            "row_key_salt": row_salt(str(context["row_key"])),
            "row_pool": p594.int_value(built.get("row_pool")),
            "scheduled_row_count": p594.int_value(built.get("scheduled_row_count")),
            "selected_leaf_indices": selected,
            "selected_leaf_signature_set": sorted(row_leaf_signature_keys),
            "selected_leaf_total_hit_roots": row_hit_count,
        }
        row_context_shapes.append(row_shape)
        tokens.add(f"context:row_shape={sha_token(row_shape)}")
        tokens.add(f"context:row_salt={row_shape['row_key_salt']}")
        tokens.add(f"context:selected_leaf_indices={row_shape['row_key_salt']}:{','.join(map(str, selected))}")
        tokens.add(f"context:hit_roots_count={row_shape['hit_roots_count']}")
        tokens.add(f"context:selected_leaf_total_hit_roots={row_hit_count}")
        tokens.add(f"context:selected_leaf_has_hit={int(row_hit_count > 0)}")
        context_profiles.append(
            {
                "row_key": context["row_key"],
                "row_shape_hash": sha_token(row_shape),
                "selected_leaf_profiles": selected_profiles,
            }
        )
    selected_leaf_signature_set = sorted(selected_leaf_signature_keys)
    selected_leaf_hit_signature_set = sorted(set(selected_leaf_hit_signature_keys))
    tokens.add(f"context:selected_leaf_signature_set={sha_token(selected_leaf_signature_set)}")
    tokens.add(f"context:selected_leaf_hit_signature_set={sha_token(selected_leaf_hit_signature_set)}")
    tokens.add(f"context:total_selected_leaf_hit_roots={total_selected_leaf_hit_roots}")
    tokens.add(f"context:any_selected_leaf_hit={int(total_selected_leaf_hit_roots > 0)}")
    tokens.add(
        "context:all_rows_have_selected_leaf_hit="
        f"{int(all(shape['selected_leaf_total_hit_roots'] > 0 for shape in row_context_shapes))}"
    )
    portable_tokens = sorted(token for token in tokens if not token.startswith("raw:target="))
    return {
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": bool(row["direct_below_rho_verified"]),
        "direct_verified": bool(row["direct_verified"]),
        "portable_tokens": portable_tokens,
        "profile": {
            "context_profiles": context_profiles,
            "selected_leaf_hit_signature_set": selected_leaf_hit_signature_set,
            "selected_leaf_signature_set": selected_leaf_signature_set,
            "total_selected_leaf_hit_roots": total_selected_leaf_hit_roots,
        },
        "row": row,
    }


def cohort_summary(profiles: list[dict[str, Any]], name: str) -> dict[str, Any]:
    return {
        "cohort": name,
        "count": len(profiles),
        "direct_below_rho_verified_count": sum(1 for row in profiles if row["direct_below_rho_verified"]),
        "direct_verified_count": sum(1 for row in profiles if row["direct_verified"]),
        "examples": [
            {
                "case_entry": row["case_entry"],
                "direct_below_rho_verified": row["direct_below_rho_verified"],
                "direct_verified": row["direct_verified"],
                "total_selected_leaf_hit_roots": row["profile"]["total_selected_leaf_hit_roots"],
                "token_sample": row["portable_tokens"][:12],
            }
            for row in profiles[:8]
        ],
    }


def token_counts(profiles: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for profile in profiles:
        counts.update(set(profile["portable_tokens"]))
    return counts


def candidate_tokens(
    positives: list[dict[str, Any]],
    misses: list[dict[str, Any]],
    min_positive_count: int,
) -> list[dict[str, Any]]:
    pos_counts = token_counts(positives)
    miss_counts = token_counts(misses)
    out = []
    for token, pos_count in pos_counts.items():
        miss_count = miss_counts.get(token, 0)
        if pos_count < min_positive_count or miss_count:
            continue
        out.append(
            {
                "miss_count": miss_count,
                "positive_count": pos_count,
                "positive_fraction": p594.ratio(pos_count, len(positives)),
                "token": token,
            }
        )
    out.sort(key=lambda item: (-item["positive_count"], item["token"]))
    return out


def selected_by_token(profiles: list[dict[str, Any]], token: str | None) -> list[dict[str, Any]]:
    if not token:
        return []
    return [profile for profile in profiles if token in set(profile["portable_tokens"])]


def feature_report(rows: list[p594.Feature], selected_profiles: list[dict[str, Any]], name: str) -> dict[str, Any]:
    selected_entries = {profile["case_entry"] for profile in selected_profiles}
    selected_rows = [row for row in rows if row["case_entry"] in selected_entries]
    return p594.report(rows, selected_rows, name, f"P605 context fingerprint selector {name}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN_SOURCE)
    parser.add_argument("--train-gate", type=Path, default=DEFAULT_TRAIN_GATE)
    parser.add_argument("--adjacent-source", type=Path, default=DEFAULT_ADJACENT_SOURCE)
    parser.add_argument("--adjacent-gate", type=Path, default=DEFAULT_ADJACENT_GATE)
    parser.add_argument("--half-source", type=Path, default=DEFAULT_HALF_SOURCE)
    parser.add_argument("--half-gate", type=Path, default=DEFAULT_HALF_GATE)
    parser.add_argument("--full-source", type=Path, default=DEFAULT_FULL_SOURCE)
    parser.add_argument("--full-gate", type=Path, default=DEFAULT_FULL_GATE)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--gate", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--min-positive-count", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_paths = [args.train_source, args.adjacent_source, args.half_source, args.full_source, args.source]
    cache = source_data(source_paths)
    train_rows = p594.p570.source_rows([args.train_source], p594.p570.gate_labels([args.train_gate]), "p601_training")
    adjacent_rows = p594.p570.source_rows(
        [args.adjacent_source], p594.p570.gate_labels([args.adjacent_gate]), "p602_adjacent"
    )
    half_rows = p594.p570.source_rows([args.half_source], p594.p570.gate_labels([args.half_gate]), "p603_half")
    full_rows = p594.p570.source_rows([args.full_source], p594.p570.gate_labels([args.full_gate]), "p604_full")
    validation_rows = p594.p570.source_rows([args.source], p594.p570.gate_labels([args.gate]), "p605_validation")
    positive_rows = [
        row
        for row in train_rows
        if p604.p601_full_period_recurrence_union(row) and row["direct_verified"]
    ]
    miss_rows = [
        *[row for row in adjacent_rows if p603.adjacent_shift_phase8_phase2_union(row)],
        *[row for row in half_rows if p603.exact_phase8_phase2_recurrence_union(row)],
        *[row for row in full_rows if p604.p601_full_period_recurrence_union(row)],
    ]
    validation_pool_rows = [
        row
        for row in validation_rows
        if p602.phase8_salt206_supply_union(row) or p602.phase2_right208_anchor13_salt208(row)
    ]
    positive_profiles = [context_tokens(cache, row) for row in positive_rows]
    miss_profiles = [context_tokens(cache, row) for row in miss_rows]
    validation_profiles = [context_tokens(cache, row) for row in validation_pool_rows]
    candidates = candidate_tokens(positive_profiles, miss_profiles, args.min_positive_count)
    selected_token = candidates[0]["token"] if candidates else None
    validation_selected_profiles = selected_by_token(validation_profiles, selected_token)
    validation_report = feature_report(
        validation_rows,
        validation_selected_profiles,
        "p605_top_context_token_selector",
    )
    payload: dict[str, Any] = {
        "artifacts": {
            "adjacent_gate": str(args.adjacent_gate),
            "adjacent_source": str(args.adjacent_source),
            "full_gate": str(args.full_gate),
            "full_source": str(args.full_source),
            "gate": str(args.gate),
            "half_gate": str(args.half_gate),
            "half_source": str(args.half_source),
            "source": str(args.source),
            "train_gate": str(args.train_gate),
            "train_source": str(args.train_source),
        },
        "claim_status": None,
        "created_at": p594.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "PRE-HIT CONTEXT: context fingerprints are built before direct witness replay.",
            "LABEL BOUNDARY: direct verifier labels, rank, operations, and relation_count are used only for evaluation.",
            "NO SPEEDUP CLAIM: relation collection, sparse linear algebra, and individual logarithm/target descent remain separate gates.",
        ],
        "method": "p605_public_context_fingerprint_delta_scout",
        "schema": "ecdlp.low_term_total2_p605_public_context_fingerprint_delta_scout.v1",
        "summary": {
            "candidate_token_count": len(candidates),
            "context_profiles_built": len(positive_profiles) + len(miss_profiles) + len(validation_profiles),
            "miss_cohort": cohort_summary(miss_profiles, "p602_p603_p604_selected_misses"),
            "positive_cohort": cohort_summary(positive_profiles, "p601_selected_direct_verified"),
            "top_candidate_tokens": candidates[:20],
            "validation_dataset": p594.dataset_summary(validation_rows),
            "validation_pool_count": len(validation_pool_rows),
            "validation_report": validation_report,
        },
    }
    if validation_report["direct_below_rho_verified_count"]:
        claim_status = "P605_CONTEXT_TOKEN_BELOW_RHO_VALIDATION_POSITIVE"
    elif validation_report["direct_verified_count"]:
        claim_status = "P605_CONTEXT_TOKEN_DIRECT_VALIDATION_POSITIVE_ABOVE_RHO"
    elif candidates:
        claim_status = "NEGATIVE_RESULT_P605_CONTEXT_TOKEN_CANDIDATE_VALIDATION_QUIET"
    else:
        claim_status = "NEGATIVE_RESULT_P605_NO_PORTABLE_CONTEXT_TOKEN_SEPARATOR"
    payload["claim_status"] = claim_status
    payload["summary"]["claim_status"] = claim_status
    p594.write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
