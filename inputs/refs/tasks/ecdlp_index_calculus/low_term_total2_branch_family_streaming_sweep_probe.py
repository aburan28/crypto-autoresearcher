#!/usr/bin/env python3
"""Branch-family streaming supply sweep for the low-term scout surface.

The fixed scout-7 branch-point scanner proves that a single cached branch can
be tested by sequentially generating mixed rows.  Fresh windows after 4879 did
not supply new fixed-branch stops, so this probe asks the next supply question:
if a small public family of early scout branches is tested with one row stream
per context, do nearby branches produce fresh verifier-derived relation stops?

This remains a toy-prime, model-bound diagnostic.  It charges row scans and
branch-family setup, derives only inside the controlled verifier challenge, and
does not target real systems.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_target_guided_probe as target_guided_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_scout_pos7_source_charged_collector as collector
import relation_probe
import summation_bias_scan
from low_term_total2_auxiliary_relation_event_assembly_scout import label
from low_term_total2_scout_pos7_direct_leaf65_kernel_probe import int_value, load_json, ratio, write_json
from low_term_total2_scout_pos7_pre_rowpool_root_intersection_probe import point_payload
from low_term_total2_scout_pos7_streaming_branch_point_scanner_probe import (
    branch_cache_key,
    cfg_for_row_key,
    row_seed_for,
    static_branch_context,
    transfer_args,
)


MODELS = (
    "family_full_context_setup_integer",
    "family_full_attempt_setup_integer",
    "family_row_scan_only_integer",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def branch_key(scout: dict[str, Any]) -> str:
    terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
    return f"pos{int_value(scout.get('scout_pos'))}:{label(terms)}"


def build_branch_family(
    verifier: Any,
    branch_context: dict[str, Any],
    scout_pos_min: int,
    scout_pos_max: int,
) -> list[dict[str, Any]]:
    family = []
    p = int_value(branch_context.get("p"))
    for scout in branch_context.get("scouts") or []:
        scout_pos = int_value(scout.get("scout_pos"))
        if scout_pos < scout_pos_min or scout_pos > scout_pos_max:
            continue
        terms = [int_value(index) for index in scout.get("unsigned_indices") or []]
        point = verifier.add_points(scout["left"]["point"], scout["right"]["point"], branch_context["ainvs"], p)
        family.append(
            {
                "candidate_point": point,
                "candidate_point_payload": point_payload(point),
                "scout_pos": scout_pos,
                "terms": terms,
                "terms_label": label(terms),
                "branch_key": branch_key(scout),
            }
        )
    family.sort(key=lambda item: (int_value(item.get("scout_pos")), str(item.get("terms_label"))))
    return family


def row_scan_integer(row_count: int, row_factor: int) -> int:
    return ceil(max(0, int(row_count)) / max(1, int(row_factor)))


def stream_family_context(
    verifier: Any,
    branch_context: dict[str, Any],
    family: list[dict[str, Any]],
    cfg: dict[str, Any],
    local_args: argparse.Namespace,
    row_key: str,
    form_keys_by_branch: dict[str, set[tuple[tuple[int, ...], int]]],
) -> tuple[dict[str, Any], dict[str, list[tuple[Any, int, list[int]]]], list[dict[str, Any]]]:
    p = int_value(branch_context["p"])
    order = int_value(branch_context["order"])
    row_pool = int_value(cfg.get("row_pool") or cfg.get("row_count") or local_args.row_pool)
    row_mode = str(cfg.get("row_mode") or local_args.row_mode)
    row_factor = max(1, int_value(local_args.row_factor, 1))
    point_map: dict[tuple[int, int] | None, list[dict[str, Any]]] = defaultdict(list)
    for branch in family:
        point_map[branch.get("candidate_point_payload")].append(branch)

    rng = random.Random(row_seed_for(cfg, local_args))
    forms_by_branch: dict[str, list[tuple[Any, int, list[int]]]] = defaultdict(list)
    hit_records: list[dict[str, Any]] = []
    point_match_count = 0
    infinity_skips = 0
    for trial in range(1, row_pool + 1):
        a_value, b_value = target_guided_probe.mixed_row_coefficients(row_mode, trial, order, rng)
        point = verifier.add_points(
            verifier.mul_point(a_value, branch_context["base"], branch_context["ainvs"], p),
            verifier.mul_point(b_value, branch_context["public"], branch_context["ainvs"], p),
            branch_context["ainvs"],
            p,
        )
        if summation_bias_scan.short_x(point, branch_context["model"], p) is None:
            infinity_skips += 1
        for branch in point_map.get(point_payload(point), []):
            branch_id = str(branch["branch_key"])
            relation = {"a": int(a_value), "b": int(b_value), "indices": [int(index) for index in branch["terms"]]}
            relation_terms = verifier.relation_terms(
                relation,
                branch_context["active_challenge"],
                branch_context["ainvs"],
                p,
            )
            if relation_terms is None or not verifier.verify_relation(
                relation,
                branch_context["active_challenge"],
                branch_context["ainvs"],
                p,
                branch_context["base"],
                branch_context["public"],
            ):
                continue
            coeffs, rhs = verifier.relation_linear_form(
                relation,
                relation_terms,
                branch_context["active_challenge"],
                order,
            )
            form_key = (tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order)
            seen = form_keys_by_branch.setdefault(branch_id, set())
            duplicate = form_key in seen
            if not duplicate:
                seen.add(form_key)
                forms_by_branch[branch_id].append((tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order, relation_terms))
            point_match_count += 1
            hit_records.append(
                {
                    "branch_key": branch_id,
                    "duplicate": duplicate,
                    "original_trial": trial,
                    "q_coeff": int_value(coeffs[0]) % order,
                    "rhs": int_value(rhs) % order,
                    "row_key": row_key,
                    "scout_pos": int_value(branch.get("scout_pos")),
                    "terms": branch.get("terms") or [],
                    "terms_label": branch.get("terms_label"),
                }
            )
    return (
        {
            "branch_candidate_count": len(family),
            "hit_branch_count": len({str(hit.get("branch_key")) for hit in hit_records}),
            "hit_branch_keys": sorted({str(hit.get("branch_key")) for hit in hit_records}),
            "infinity_skips": infinity_skips,
            "point_match_count": point_match_count,
            "row_count": row_pool,
            "row_factor": row_factor,
            "row_key": row_key,
            "row_mode": row_mode,
            "row_scan_integer_ops": row_scan_integer(row_pool, row_factor),
        },
        forms_by_branch,
        hit_records,
    )


def merge_forms(left: dict[str, list[tuple[Any, int, list[int]]]], right: dict[str, list[tuple[Any, int, list[int]]]]) -> None:
    for key, forms in right.items():
        left.setdefault(key, []).extend(forms)


def attempt_model_ops(context_rows: list[dict[str, Any]], branch_count: int, hit_records: list[dict[str, Any]]) -> dict[str, int]:
    row_scan_ops = sum(int_value(row.get("row_scan_integer_ops")) for row in context_rows)
    context_setup = sum(int_value(row.get("branch_candidate_count")) for row in context_rows)
    attempt_setup = int(branch_count)
    relation_ops = len([hit for hit in hit_records if not hit.get("duplicate")])
    return {
        "family_full_context_setup_integer": row_scan_ops + context_setup + relation_ops,
        "family_full_attempt_setup_integer": row_scan_ops + attempt_setup + relation_ops,
        "family_row_scan_only_integer": row_scan_ops + relation_ops,
    }


def scan_attempt(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    branch_cache: dict[tuple[Any, ...], dict[str, Any]],
    row: dict[str, Any],
    probe_args: argparse.Namespace,
    scout_pos_min: int,
    scout_pos_max: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    try:
        transfer_index = int_value(row.get("transfer_index"))
        form_keys_by_branch: dict[str, set[tuple[tuple[int, ...], int]]] = {}
        forms_by_branch: dict[str, list[tuple[Any, int, list[int]]]] = {}
        context_rows: list[dict[str, Any]] = []
        hit_records: list[dict[str, Any]] = []
        branch_count = 0
        branch_samples: list[dict[str, Any]] = []
        branch_context_for_derive: dict[str, Any] | None = None
        for row_key in [str(key) for key in row.get("row_keys") or []]:
            cfg = cfg_for_row_key(config_source, row_key, probe_args.row_pool)
            local_args = transfer_args(probe_args, row_key, transfer_index)
            cache_key = branch_cache_key(cfg, local_args)
            branch_context = branch_cache.get(cache_key)
            if branch_context is None:
                branch_context = static_branch_context(verifier, records, cfg, local_args)
                branch_cache[cache_key] = branch_context
            branch_context_for_derive = branch_context
            family = build_branch_family(verifier, branch_context, scout_pos_min, scout_pos_max)
            branch_count = max(branch_count, len(family))
            branch_samples = branch_samples or [
                {
                    "branch_key": branch["branch_key"],
                    "candidate_point": branch["candidate_point_payload"],
                    "scout_pos": branch["scout_pos"],
                    "terms": branch["terms"],
                    "terms_label": branch["terms_label"],
                }
                for branch in family[: min(8, len(family))]
            ]
            profile, context_forms, context_hits = stream_family_context(
                verifier,
                branch_context,
                family,
                cfg,
                local_args,
                row_key,
                form_keys_by_branch,
            )
            context_rows.append(profile)
            merge_forms(forms_by_branch, context_forms)
            hit_records.extend(context_hits)
        if branch_context_for_derive is None:
            return ({}, errors)
        order = int_value(branch_context_for_derive.get("order"))
        secret = int_value(branch_context_for_derive.get("secret"), -1)
        branch_results = []
        for key, forms in sorted(forms_by_branch.items(), key=lambda item: (-len(item[1]), item[0])):
            derived = relation_probe.linear_rank_probe(verifier, forms, order)
            verified = bool(derived.get("mixed_wide_relations_derive_secret") and int_value(derived.get("derived_secret"), -2) == secret)
            branch_results.append(
                {
                    "accepted_relation_count": len(forms),
                    "branch_key": key,
                    "derived_secret": derived.get("derived_secret"),
                    "public_key_verified": verified,
                    "rank": int_value(derived.get("mixed_wide_relation_rank")),
                }
            )
        verified_branches = [branch for branch in branch_results if branch.get("public_key_verified")]
        models = attempt_model_ops(context_rows, branch_count, hit_records)
        rho = 0
        if branch_context_for_derive:
            rho = int_value((branch_context_for_derive.get("active_challenge") or {}).get("generic_rho_steps"))
        return (
            {
                "accepted": bool(verified_branches),
                "best_branch": verified_branches[0] if verified_branches else (branch_results[0] if branch_results else None),
                "branch_count": branch_count,
                "branch_result_count": len(branch_results),
                "branch_results": branch_results[:20],
                "branch_samples": branch_samples,
                "context_rows": context_rows,
                "hit_records": hit_records[:80],
                "model_ops": models,
                "model_ops_over_rho": {name: ratio(value, rho) for name, value in models.items()},
                "public_key_verified_branch_count": len(verified_branches),
                "rho": rho,
                "row_keys": row.get("row_keys") or [],
                "source_policy": row.get("source_policy"),
                "top_k": int_value(row.get("top_k")),
                "transfer_index": transfer_index,
            },
            errors,
        )
    except Exception as exc:  # noqa: BLE001 - preserve research failures.
        errors.append(
            {
                "error": "branch_family_attempt_failed",
                "message": str(exc),
                "transfer_index": int_value(row.get("transfer_index")),
            }
        )
        return ({}, errors)


def collect_group(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    branch_cache: dict[tuple[Any, ...], dict[str, Any]],
    source_path: Path,
    rows: list[dict[str, Any]],
    probe_args: argparse.Namespace,
    scout_pos_min: int,
    scout_pos_max: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempts = []
    errors: list[dict[str, Any]] = []
    stop = None
    for row in rows:
        attempt, attempt_errors = scan_attempt(
            verifier,
            records,
            config_source,
            branch_cache,
            row,
            probe_args,
            scout_pos_min,
            scout_pos_max,
        )
        errors.extend({**item, "source_path": str(source_path)} for item in attempt_errors)
        if not attempt:
            continue
        attempts.append(attempt)
        if attempt.get("accepted"):
            stop = attempt
            break
    window = collector.artifact_window(source_path)
    model_ops = {
        model: sum(int_value((attempt.get("model_ops") or {}).get(model)) for attempt in attempts)
        for model in MODELS
    }
    rho = max([int_value(attempt.get("rho")) for attempt in attempts if int_value(attempt.get("rho"))] or [0])
    return (
        {
            "attempt_count": len(attempts),
            "attempts": attempts,
            "has_public_key_verified_stop": stop is not None,
            "model_ops": model_ops,
            "model_ops_over_rho": {name: ratio(value, rho) for name, value in model_ops.items()},
            "rho": rho,
            "source_path": str(source_path),
            "stop": stop,
            "window": f"{window[0]}_{window[1]}" if window else "",
            "window_start": window[0] if window else (int_value(attempts[0].get("transfer_index")) if attempts else 0),
        },
        errors,
    )


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    verified = [group for group in groups if group.get("has_public_key_verified_stop")]
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    model_summaries = {}
    for model in MODELS:
        ops = sum(int_value((group.get("model_ops") or {}).get(model)) for group in groups)
        model_summaries[model] = {
            "cost_per_verified_stop_over_rho": ratio(ops, rho * len(verified)) if verified and rho else None,
            "ops": ops,
            "ops_over_rho": ratio(ops, rho),
            "verified_stop_count": len(verified),
        }
    branch_counts = Counter()
    for group in verified:
        branch = ((group.get("stop") or {}).get("best_branch") or {}).get("branch_key")
        if branch:
            branch_counts[str(branch)] += 1
    context_rows = [
        context
        for group in groups
        for attempt in group.get("attempts") or []
        for context in attempt.get("context_rows") or []
    ]
    return {
        "attempt_count": sum(int_value(group.get("attempt_count")) for group in groups),
        "context_count": len(context_rows),
        "group_count": len(groups),
        "hit_context_count": sum(1 for row in context_rows if int_value(row.get("point_match_count")) > 0),
        "model_summaries": model_summaries,
        "rho": rho,
        "top_verified_branches": [
            {"branch_key": key, "verified_stop_count": count}
            for key, count in branch_counts.most_common(12)
        ],
        "verified_stop_count": len(verified),
    }


def claim_status(summary: dict[str, Any]) -> str:
    validation = summary.get("validation") if isinstance(summary.get("validation"), dict) else {}
    verified = int_value(validation.get("verified_stop_count"))
    if verified <= 0:
        return "BRANCH_FAMILY_STREAMING_SWEEP_NO_VALIDATION_DERIVED_STOPS"
    models = validation.get("model_summaries") if isinstance(validation.get("model_summaries"), dict) else {}
    for model in ("family_full_context_setup_integer", "family_full_attempt_setup_integer", "family_row_scan_only_integer"):
        cost = (models.get(model) or {}).get("cost_per_verified_stop_over_rho")
        if cost is not None and float(cost) < 1.0:
            return f"BRANCH_FAMILY_STREAMING_SWEEP_{model.upper()}_BELOW_RHO"
    return "BRANCH_FAMILY_STREAMING_SWEEP_VALIDATION_STOPS_ABOVE_RHO"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-glob",
        default="ecdlp_index_calculus_state/frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json",
    )
    parser.add_argument("--target", default="22050.cf1@11731")
    parser.add_argument("--selector", default="mode_low_term_support_total5")
    parser.add_argument("--top-k", type=int, default=16)
    parser.add_argument("--min-transfer", type=int, default=4824)
    parser.add_argument("--calibration-end", type=int, default=4919)
    parser.add_argument("--scout-pos-min", type=int, default=1)
    parser.add_argument("--scout-pos-max", type=int, default=24)
    parser.add_argument("--max-source-paths", type=int, default=0)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_paths = [
        path
        for path in collector.parse_paths(args.source_glob)
        if (window := collector.artifact_window(path)) is not None and window[0] >= args.min_transfer
    ]
    source_paths.sort(key=lambda path: collector.artifact_window(path) or (0, 0))
    if args.max_source_paths > 0:
        source_paths = source_paths[: args.max_source_paths]
    if not source_paths:
        raise SystemExit("no source paths selected")
    first_source = load_json(source_paths[0])
    source_params = repair_probe.source_parameters(first_source)
    probe_args = repair_probe.probe_args_from_source(first_source)
    verifier, records, config_source, _specs_by_target = repair_probe.build_specs(source_params)
    branch_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    groups = []
    errors: list[dict[str, Any]] = []
    rows_by_source_count: dict[str, int] = {}
    for source_path in source_paths:
        source = load_json(source_path)
        rows = collector.source_cases(source_path, source, args.target, args.selector, args.top_k, args.min_transfer)
        rows_by_source_count[str(source_path)] = len(rows)
        if not rows:
            continue
        group, group_errors = collect_group(
            verifier,
            records,
            config_source,
            branch_cache,
            source_path,
            rows,
            probe_args,
            args.scout_pos_min,
            args.scout_pos_max,
        )
        groups.append(group)
        errors.extend(group_errors)
    groups.sort(key=lambda row: (int_value(row.get("window_start")), str(row.get("source_path"))))
    calibration_groups, validation_groups = split_groups(groups, args.calibration_end)
    summary = {
        "calibration": summarize(calibration_groups),
        "validation": summarize(validation_groups),
    }
    payload = {
        "artifacts": {"source_paths": [str(path) for path in source_paths]},
        "claim_status": claim_status(summary),
        "cost_model_definitions": {
            "family_full_context_setup_integer": "Sequentially generate every mixed row once per context, test all selected branch points by point-map lookup, charge one setup op per branch per context, plus one relation-form op per unique branch hit.",
            "family_full_attempt_setup_integer": "Same row stream, but branch-family setup is charged once per source attempt because branch points are shared across row keys under the same transfer challenge.",
            "family_row_scan_only_integer": "Row scan plus emitted relation forms only; diagnostic lower boundary that omits branch-family point-map setup.",
        },
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: branch candidates come from the public scout selector under the shared-transfer challenge.",
            "The sweep stores a branch point map for many branches; it is a source-supply diagnostic, not the final fixed-branch scanner.",
            "Verifier-derived stops are checked only inside the generated toy challenge.",
            "A validation stop below rho would be an index-calculus precursor requiring follow-up source-density and target-descent checks, not a deployed-curve break.",
        ],
        "parameters": {
            "calibration_end": args.calibration_end,
            "max_source_paths": args.max_source_paths,
            "min_transfer": args.min_transfer,
            "scout_pos_max": args.scout_pos_max,
            "scout_pos_min": args.scout_pos_min,
            "selector": args.selector,
            "target": args.target,
            "top_k": args.top_k,
        },
        "rows_by_source_count": rows_by_source_count,
        "schema": "ecdlp.low_term_total2_branch_family_streaming_sweep_probe.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "error_count": len(errors), "summary": summary}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
