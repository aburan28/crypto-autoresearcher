#!/usr/bin/env python3
"""P954 temporal row-policy audit for the fresh 67 low-term-support signal."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_DIR = Path(__file__).resolve().parent
for candidate in (REPO_ROOT, TASK_DIR):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tasks.ecdlp_index_calculus.low_term_total2_p942_hash_context_discriminator import (  # noqa: E402
    int_value,
    load_json,
    now_iso,
    write_json,
)
from tasks.ecdlp_index_calculus.low_term_total2_p948_verifier_equation_attachment_audit import parse_challenge_seed  # noqa: E402
from tasks.ecdlp_index_calculus.low_term_total2_p953_fresh67_cost_reduction_audit import (  # noqa: E402
    group_key,
    group_union_report,
    scan_policy_prefix,
)
from tasks.ecdlp_index_calculus.low_term_total2_p950_public_ranked_prefix_replay import build_context  # noqa: E402

import frontier_signed_eval_cover_association_probe as association_probe  # noqa: E402
import frontier_signed_eval_cover_preassociation_filter_probe as preassociation_filter_probe  # noqa: E402
import relation_probe  # noqa: E402


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p954_fresh67_temporal_row_policy_audit.md"
DEFAULT_CONFIG_SOURCE = STATE_DIR / "frontier_signed_eval_cover_row_schedule_filter_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p954_fresh67_temporal_row_policy_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p954_fresh67_temporal_row_policy_audit.v1"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_WINDOWS = (
    "1000_1007",
    "1016_1023",
    "1024_1031",
    "1032_1039",
    "1040_1047",
    "1048_1055",
    "1072_1079",
    "1080_1087",
    "1088_1095",
    "1096_1103",
    "1104_1111",
    "1128_1135",
    "1136_1143",
)

PolicySpec = tuple[str, tuple[tuple[str, int], ...]]
LEAF_POLICY_SPECS: tuple[PolicySpec, ...] = (
    ("low_term_span_k5", (("low_term_span", 5),)),
    ("low_term_support_k5", (("low_term_support", 5),)),
    ("low_term_support_k8", (("low_term_support", 8),)),
    ("double_pair_first_k8", (("double_pair_first", 8),)),
    ("hybrid_support_monic_b_k20", (("hybrid_support_monic_b", 20),)),
    ("hybrid_support_monic_b_k27", (("hybrid_support_monic_b", 27),)),
    ("hybrid_double_monic_b_k20", (("hybrid_double_monic_b", 20),)),
    ("low_span5__low_support_k8", (("low_term_span", 5), ("low_term_support", 8))),
    ("low_span5__double_pair_k8", (("low_term_span", 5), ("double_pair_first", 8))),
)
SELECTOR_STRATEGIES = (
    "recall_first",
    "rho_first",
    "cost_first_verified",
    "balanced",
)


def parse_windows(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


def parse_policy_specs(raw: str | None) -> list[PolicySpec]:
    specs = list(LEAF_POLICY_SPECS)
    if not raw:
        return specs
    wanted = {item.strip() for item in raw.split(",") if item.strip()}
    return [spec for spec in specs if spec[0] in wanted]


def window_start(window: str) -> int:
    match = re.match(r"^(\d+)_\d+$", window)
    return int(match.group(1)) if match else 10**18


def artifact_for_window(window: str) -> Path:
    return STATE_DIR / f"low_term_total2_ffe_public_factor_quadratic_root_fresh_{window}_expanded_probe.json"


def source_clean(row: dict[str, Any]) -> bool:
    return bool(
        row.get("public_factor_quadratic_root_beats_rho")
        and row.get("quadratic_preserves_selected_root_pairs")
        and not row.get("chosen_false_positive_source")
    )


def compact_candidate_source(row: dict[str, Any], path: Path, window: str, source_policy: str) -> dict[str, Any]:
    coeffs = row.get("selected_factor_coefficients") or {}
    return {
        "artifact": str(path),
        "b_coeff": coeffs.get("b_coeff"),
        "c_coeff": coeffs.get("c_coeff"),
        "clean": source_clean(row),
        "constant": coeffs.get("constant"),
        "hash": row.get("selected_factor_hash"),
        "policy": source_policy,
        "ratio": row.get("public_factor_quadratic_root_ops_over_rho"),
        "row_key": row.get("row_key"),
        "source_has_exact_leaf": bool(row.get("factor_zero_leaf_indices") or row.get("selected_leaf_indices")),
        "source_selected_factor_hash": row.get("selected_factor_hash"),
        "surface_id": row.get("surface_id"),
        "target": row.get("target"),
        "target_prime": row.get("p"),
        "transfer_index": row.get("transfer_index"),
        "window": window,
    }


def source_sort_key(source: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(source.get("source_selected_factor_hash")),
        str(source.get("policy")),
        str(source.get("hash")),
    )


def load_union_sources(windows: list[str], target: str) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], list[dict[str, Any]]]:
    by_surface: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    summaries: list[dict[str, Any]] = []
    for window in windows:
        path = artifact_for_window(window)
        payload = load_json(path)
        policy_rows = payload.get("policy_rows") or {}
        target_rows = 0
        target_surfaces: set[str] = set()
        clean_surfaces: set[str] = set()
        for source_policy, rows in sorted(policy_rows.items()):
            for row in rows or []:
                if str(row.get("target")) != target or not row.get("surface_id"):
                    continue
                target_rows += 1
                selected = compact_candidate_source(row, path, window, str(source_policy))
                surface_id = str(selected["surface_id"])
                target_surfaces.add(surface_id)
                if selected.get("clean"):
                    clean_surfaces.add(surface_id)
                by_surface[surface_id].append((selected, row))
        summaries.append(
            {
                "artifact": str(path),
                "policy_count": len(policy_rows),
                "target_policy_row_count": target_rows,
                "target_unique_surface_count": len(target_surfaces),
                "target_unique_clean_surface_count": len(clean_surfaces),
                "window": window,
            }
        )
    selected_sources: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for surface_id, candidates in sorted(by_surface.items()):
        candidates = sorted(candidates, key=lambda pair: source_sort_key(pair[0]))
        selected_sources.append(candidates[0])
    return selected_sources, summaries


def compact_group(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "policy": group.get("policy"),
        "prefix_ops_over_rho": group.get("prefix_ops_over_rho"),
        "prefix_ops": group.get("prefix_ops"),
        "prefix_ops_beats_rho": group.get("prefix_ops_beats_rho"),
        "row_count": group.get("row_count"),
        "source_clean_row_count": group.get("source_clean_row_count"),
        "target": group.get("target"),
        "transfer_indices": group.get("transfer_indices"),
        "union_derived_secret": group.get("union_derived_secret"),
        "union_public_key_verified": group.get("union_public_key_verified"),
        "union_rank": group.get("union_rank"),
        "unique_form_count": group.get("unique_form_count"),
        "windows": group.get("windows"),
    }


def groups_for_policy(groups: list[dict[str, Any]], policy: str, train_filter: Any) -> list[dict[str, Any]]:
    return [
        group
        for group in groups
        if str(group.get("policy")) == policy and train_filter(group)
    ]


def policy_score(groups: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [group for group in groups if group.get("union_public_key_verified")]
    below = [group for group in verified if group.get("prefix_ops_beats_rho")]
    ratios = [
        float(group.get("prefix_ops_over_rho"))
        for group in groups
        if group.get("prefix_ops_over_rho") is not None
    ]
    verified_ratios = [
        float(group.get("prefix_ops_over_rho"))
        for group in verified
        if group.get("prefix_ops_over_rho") is not None
    ]
    return {
        "below_rho_verified_count": len(below),
        "group_count": len(groups),
        "max_union_rank": max((int_value(group.get("union_rank")) for group in groups), default=0),
        "mean_ops_over_rho": round(mean(ratios), 8) if ratios else None,
        "min_verified_ops_over_rho": min(verified_ratios) if verified_ratios else None,
        "verified_count": len(verified),
    }


def selector_key(strategy: str, policy: str, score: dict[str, Any]) -> tuple[Any, ...]:
    below = int_value(score.get("below_rho_verified_count"))
    verified = int_value(score.get("verified_count"))
    rank = int_value(score.get("max_union_rank"))
    mean_ratio = float(score.get("mean_ops_over_rho") or 10**18)
    support_tiebreak = policy == "low_term_support_k5"
    if strategy == "recall_first":
        return (below, verified, rank, -mean_ratio, support_tiebreak, policy)
    if strategy == "rho_first":
        return (below, -mean_ratio, verified, rank, support_tiebreak, policy)
    if strategy == "cost_first_verified":
        return (below, verified > 0, -mean_ratio, verified, rank, support_tiebreak, policy)
    if strategy == "balanced":
        return (below, verified - mean_ratio, verified, rank, support_tiebreak, policy)
    raise ValueError(f"unknown selector strategy: {strategy}")


def select_policy(
    groups: list[dict[str, Any]],
    policies: list[str],
    train_filter: Any,
    strategy: str,
) -> tuple[str | None, dict[str, Any], dict[str, dict[str, Any]]]:
    scores = {
        policy: policy_score(groups_for_policy(groups, policy, train_filter))
        for policy in policies
    }
    scores = {policy: score for policy, score in scores.items() if int_value(score.get("group_count")) > 0}
    if not scores:
        return None, {}, {}
    selected = max(
        scores,
        key=lambda policy: selector_key(strategy, policy, scores[policy]),
    )
    return selected, scores[selected], scores


def summarize_test(groups: list[dict[str, Any]]) -> dict[str, Any]:
    score = policy_score(groups)
    score["groups"] = [compact_group(group) for group in groups]
    score["below_rho_verified_groups"] = [
        compact_group(group)
        for group in groups
        if group.get("union_public_key_verified") and group.get("prefix_ops_beats_rho")
    ]
    return score


def split_report(
    split: str,
    groups: list[dict[str, Any]],
    policies: list[str],
    train_filter: Any,
    test_filter: Any,
    selector_strategy: str,
    extra: dict[str, Any],
) -> dict[str, Any]:
    selected, training, all_scores = select_policy(groups, policies, train_filter, selector_strategy)
    test_groups = [
        group
        for group in groups
        if selected is not None and str(group.get("policy")) == selected and test_filter(group)
    ]
    return {
        "all_training_scores": all_scores,
        "selected_policy": selected,
        "selector_strategy": selector_strategy,
        "split": split,
        "test_summary": summarize_test(test_groups),
        "training_summary": training,
        **extra,
    }


def transfer_set(group: dict[str, Any]) -> set[int]:
    return {int_value(value) for value in group.get("transfer_indices") or []}


def group_start(group: dict[str, Any]) -> int:
    windows = group.get("windows") or []
    return min((window_start(str(window)) for window in windows), default=10**18)


def build_splits(groups: list[dict[str, Any]], policies: list[str]) -> list[dict[str, Any]]:
    reports = []
    for strategy in SELECTOR_STRATEGIES:
        reports.extend(
            [
                split_report(
                    "train_before_1128_test_1128_1143",
                    groups,
                    policies,
                    lambda group: group_start(group) < 1128,
                    lambda group: 1128 <= group_start(group) <= 1143,
                    strategy,
                    {"train_window_lt": 1128, "test_window_range": [1128, 1143]},
                ),
                split_report(
                    "train_before_1136_test_1136_1143",
                    groups,
                    policies,
                    lambda group: group_start(group) < 1136,
                    lambda group: 1136 <= group_start(group) <= 1143,
                    strategy,
                    {"train_window_lt": 1136, "test_window_range": [1136, 1143]},
                ),
            ]
        )
        for transfer in (1131, 1133, 1140, 1143):
            reports.append(
                split_report(
                    f"rolling_transfer_{transfer}",
                    groups,
                    policies,
                    lambda group, transfer=transfer: max(transfer_set(group) or {-1}) < transfer,
                    lambda group, transfer=transfer: transfer in transfer_set(group),
                    strategy,
                    {"holdout_transfer": transfer},
                )
            )
    return reports


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("train_selected_below_rho_verified_split_count")):
        return "P954_TEMPORAL_POLICY_SELECTS_FRESH67_BELOW_RHO"
    if int_value(summary.get("fixed_low_term_support_below_rho_verified_count")):
        return "NEGATIVE_RESULT_P954_FIXED_SIGNAL_NOT_TRAIN_SELECTED"
    if int_value(summary.get("train_selected_verified_split_count")):
        return "P954_TEMPORAL_POLICY_VERIFIES_ABOVE_RHO_ONLY"
    return "NEGATIVE_RESULT_P954_TEMPORAL_POLICY_NO_VERIFICATION"


def summarize(
    row_results: list[dict[str, Any]],
    groups: list[dict[str, Any]],
    splits: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    source_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    verified = [group for group in groups if group.get("union_public_key_verified")]
    below = [group for group in verified if group.get("prefix_ops_beats_rho")]
    selected_positive_splits = [
        split
        for split in splits
        if int_value((split.get("test_summary") or {}).get("below_rho_verified_count")) > 0
    ]
    selected_verified_splits = [
        split
        for split in splits
        if int_value((split.get("test_summary") or {}).get("verified_count")) > 0
    ]
    fixed_low_support_below = [
        group
        for group in groups
        if str(group.get("policy")) == "low_term_support_k5"
        and group.get("union_public_key_verified")
        and group.get("prefix_ops_beats_rho")
    ]
    policy_summary = {
        policy: policy_score([group for group in groups if str(group.get("policy")) == policy])
        for policy in sorted({str(group.get("policy")) for group in groups})
    }
    summary = {
        "below_rho_verified_group_count": len(below),
        "candidate_surface_count": len({str(row.get("surface_id")) for row in row_results}),
        "claim_status": None,
        "error_count": len(errors),
        "fixed_low_term_support_below_rho_verified_count": len(fixed_low_support_below),
        "fixed_low_term_support_below_rho_groups": [compact_group(group) for group in fixed_low_support_below],
        "fresh_group_count": len(groups),
        "policy_summary": policy_summary,
        "row_scan_count": len(row_results),
        "rows_with_forms": sum(1 for row in row_results if int_value(row.get("linear_form_count")) > 0),
        "source_summaries": source_summaries,
        "train_selected_below_rho_verified_split_count": len(selected_positive_splits),
        "train_selected_below_rho_verified_splits": [
            {
                "selected_policy": split.get("selected_policy"),
                "selector_strategy": split.get("selector_strategy"),
                "split": split.get("split"),
                "test_summary": split.get("test_summary"),
                "training_summary": split.get("training_summary"),
            }
            for split in selected_positive_splits
        ],
        "train_selected_verified_split_count": len(selected_verified_splits),
        "unique_verifier_form_count": len(
            {
                (tuple(form.get("coeffs") or []), int_value(form.get("rhs")))
                for row in row_results
                for form in row.get("linear_forms") or []
            }
        ),
        "verified_group_count": len(verified),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVED-FRESH-STREAM: no post-1144 target-67 rows exist in the current artifacts, so P954 uses chronological pre-P953-to-P953 splits.",
            "UNION-SOURCE-ROWS: candidate surfaces are deduped across all artifact policies instead of using only each artifact's best policy.",
            "TRAINED-POLICY-NOT-END-TO-END: policy choice uses earlier verifier outcomes but still relies on archived source surface generation.",
            "POLLARD-RHO BOUNDARY: below-rho claims are charged prefix component comparisons against toy rho.",
        ],
    }
    summary["claim_status"] = determine_claim(summary)
    return summary


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = parse_windows(args.windows)
    specs = parse_policy_specs(args.policies)
    sources, source_summaries = load_union_sources(windows, args.target)
    verifier = relation_probe.load_verifier_module()
    records = verifier.load_records()
    config_source = load_json(args.config_source)
    context_cache: dict[str, tuple[dict[str, Any], dict[str, Any], Any, dict[str, Any]]] = {}
    row_results: list[dict[str, Any]] = []
    raw_rows_by_group: dict[str, list[dict[str, Any]]] = defaultdict(list)
    built_by_group: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []

    for selected, source in sources:
        challenge_seed = parse_challenge_seed(selected.get("surface_id"))
        if not challenge_seed:
            errors.append({**selected, "error": "missing challenge seed"})
            continue
        surface_id = str(selected["surface_id"])
        if surface_id not in context_cache:
            try:
                row_fields, built, local_args = build_context(
                    verifier,
                    records,
                    config_source,
                    args,
                    selected,
                    challenge_seed,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append({**selected, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if built.get("error"):
                errors.append({**selected, "error": built["error"]})
                continue
            scouts_by_pos = {int(scout["scout_pos"]): scout for scout in built["scouts"]}
            components = association_probe.build_components(built["scouts"], built["rows"], int(built["p"]))
            feature_rows = preassociation_filter_probe.leaf_public_features(components, scouts_by_pos, int(built["p"]))
            context_cache[surface_id] = (row_fields, built, local_args, {"components": components, "feature_rows": feature_rows})
        _row_fields, built, local_args, feature_cache = context_cache[surface_id]
        for policy, components_spec in specs:
            try:
                row = scan_policy_prefix(
                    verifier,
                    selected,
                    source,
                    built,
                    local_args,
                    policy,
                    components_spec,
                    feature_cache,
                )
            except Exception as exc:  # noqa: BLE001
                errors.append({**selected, "policy": policy, "error": f"{type(exc).__name__}: {exc}"})
                continue
            key = group_key(verifier, row, built)
            raw_rows_by_group[key].append(row)
            built_by_group.setdefault(key, built)
            row_results.append({key: value for key, value in row.items() if not key.startswith("_")})

    groups = [
        group_union_report(verifier, key, rows, built_by_group[key])
        for key, rows in sorted(raw_rows_by_group.items())
    ]
    splits = build_splits(groups, [policy for policy, _components in specs])
    summary = summarize(row_results, groups, splits, errors, source_summaries)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "claim_status": summary["claim_status"],
        "created_at": now_iso(),
        "errors": errors,
        "fresh_groups": groups,
        "method": "p954_fresh67_temporal_row_policy_audit",
        "parameters": {
            "config_source": str(args.config_source),
            "leaf_policies": [
                {
                    "components": [
                        {"budget_top_k": budget, "mode": mode}
                        for mode, budget in components
                    ],
                    "policy": policy,
                }
                for policy, components in specs
            ],
            "row_pool": args.row_pool,
            "scout_limit": args.scout_limit,
            "scout_mode": args.scout_mode,
            "scout_order": args.scout_order,
            "seed": args.seed,
            "target": args.target,
            "windows": windows,
        },
        "row_results": row_results,
        "schema": SCHEMA,
        "splits": splits,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--config-source", type=Path, default=DEFAULT_CONFIG_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--windows", default=",".join(DEFAULT_WINDOWS))
    parser.add_argument("--target", default=DEFAULT_TARGET)
    parser.add_argument("--policies", default=None)
    parser.add_argument("--filter-mode", default="low_term_span")
    parser.add_argument("--row-pool", type=int, default=512)
    parser.add_argument("--row-count", type=int, default=128)
    parser.add_argument("--scout-limit", type=int, default=192)
    parser.add_argument("--scout-mode", default="s3_coeff_spread")
    parser.add_argument("--scout-order", default="eval_cover_hits_high")
    parser.add_argument("--selected-limit", type=int, default=64)
    parser.add_argument("--factor-base-size", type=int, default=16)
    parser.add_argument("--max-relations", type=int, default=96)
    parser.add_argument("--min-distinct-indices", type=int, default=4)
    parser.add_argument("--min-unsigned-distinct-indices", type=int, default=2)
    parser.add_argument("--allow-combined-coefficients", dest="require_unit_coefficients", action="store_false")
    parser.set_defaults(require_unit_coefficients=True)
    parser.add_argument("--row-factor", type=int, default=512)
    parser.add_argument("--product-factor", type=int, default=4096)
    parser.add_argument("--seed", default="ecdlp-frontier-signed-dual-sieve-v1")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"surfaces={summary['candidate_surface_count']} "
        f"row_scans={summary['row_scan_count']} "
        f"groups={summary['fresh_group_count']} "
        f"verified={summary['verified_group_count']} "
        f"below_rho={summary['below_rho_verified_group_count']} "
        f"selected_below_splits={summary['train_selected_below_rho_verified_split_count']} "
        f"fixed_low_support_below={summary['fixed_low_term_support_below_rho_verified_count']} "
        f"errors={summary['error_count']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
