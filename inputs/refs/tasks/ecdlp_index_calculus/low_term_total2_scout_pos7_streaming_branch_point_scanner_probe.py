#!/usr/bin/env python3
"""Sequential branch-point row scanner for the fixed scout-7 leaf-65 target.

The pre-row-pool root/point-intersection probe found a below-rho validation
ledger, but it measured row positions after replaying the full context builder.
This probe moves the row side one step closer to implementation:

* reconstruct the fixed scout-7 ``11,11,15,15`` branch from public candidate
  metadata and the shared target challenge;
* generate deterministic mixed rows sequentially with the original row seed;
* test direct point equality against the cached branch point;
* emit verifier-compatible relation forms from matching rows;
* charge no-hit contexts by scanning the full deterministic row stream.

This is still a toy-prime, target-coupled work order.  The direct kernel
artifact supplies evaluation labels only; rank labels are not features.
"""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

import argparse
import json
import random
from argparse import Namespace
from collections import Counter
from datetime import datetime, timezone
from math import ceil
from pathlib import Path
from typing import Any

import frontier_signed_eval_cover_projection_probe as eval_cover_probe
import frontier_signed_eval_cover_row_schedule_filter_robustness_probe as robustness_probe
import frontier_signed_sparse_sieve_probe
import frontier_signed_target_guided_probe as target_guided_probe
import low_term_total2_public_prefix_shared_leaf_repair_probe as repair_probe
import low_term_total2_scout_pos7_source_charged_collector as collector
import relation_probe
import signed_pair_mitm_probe
import signed_pair_unsigned_transfer_probe
import summation_bias_scan
from low_term_total2_scout_pos7_direct_leaf65_kernel_probe import (
    int_value,
    load_json,
    ratio,
    scout7_leaf65_terms,
    write_json,
)
from low_term_total2_scout_pos7_pre_rowpool_root_intersection_probe import (
    direct_context_for,
    point_equal,
    point_payload,
)


MODELS = (
    "stream_branch_first_cached_fractional",
    "stream_branch_first_context_setup_fractional",
    "stream_branch_first_context_setup_integer",
    "stream_branch_full_cached_fractional",
    "stream_branch_full_context_setup_fractional",
    "stream_branch_full_context_setup_integer",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_row_key(row_key: str) -> dict[str, Any]:
    target, mode, count, raw_salt = str(row_key).split(":", 3)
    if not raw_salt.startswith("salt"):
        raise ValueError(f"row key salt suffix not understood: {row_key!r}")
    return {
        "target": target,
        "row_mode": mode,
        "row_count": int(count),
        "row_salt": int(raw_salt.removeprefix("salt")),
    }


def transfer_args(args: argparse.Namespace, row_key: str, transfer_index: int) -> argparse.Namespace:
    parsed = parse_row_key(row_key)
    local_args = robustness_probe.clone_args(
        args,
        str(parsed["row_mode"]),
        int(args.row_pool),
        int(parsed["row_count"]),
        int(parsed["row_salt"]),
    )
    row_seed_prefix = str(local_args.seed)
    target = str(parsed["target"])
    local_args.challenge_mode = "shared_target_transfer_seed"
    local_args.challenge_seed = f"{args.seed}:shared-transfer:{int(transfer_index)}:{target}"
    local_args.row_seed_prefix = row_seed_prefix
    local_args.scout_seed_prefix = local_args.challenge_seed
    local_args.filter_seed_prefix = local_args.challenge_seed
    local_args.seed = local_args.challenge_seed
    return local_args


def cfg_for_row_key(config_source: dict[str, Any], row_key: str, row_pool: int) -> dict[str, Any]:
    parsed = parse_row_key(row_key)
    template = robustness_probe.template_for_target(config_source, str(parsed["target"]))
    base = robustness_probe.matching_source_row(
        config_source,
        template,
        str(parsed["row_mode"]),
        int(parsed["row_count"]),
    )
    return robustness_probe.schedule_cfg(
        base,
        str(parsed["row_mode"]),
        int(row_pool),
        int(parsed["row_count"]),
        int(parsed["row_salt"]),
    )


def branch_cache_key(cfg: dict[str, Any], args: argparse.Namespace) -> tuple[Any, ...]:
    return (
        str(cfg.get("target")),
        str(args.seed),
        int_value(cfg.get("factor_base_size"), int_value(args.factor_base_size)),
        int_value(cfg.get("signed_pair_limit") or cfg.get("selected_signed_pair_count")),
        str(cfg.get("signed_pair_selection_mode") or "point_collision_light"),
        int_value(cfg.get("scout_limit"), int_value(args.scout_limit)),
        str(cfg.get("scout_mode") or args.scout_mode),
        int_value(args.min_distinct_indices),
        int_value(args.min_unsigned_distinct_indices),
        bool(args.require_unit_coefficients),
    )


def static_branch_context(
    verifier: Any,
    records: list[dict[str, Any]],
    cfg: dict[str, Any],
    local_args: argparse.Namespace,
) -> dict[str, Any]:
    label, prime = relation_probe.parse_target(str(cfg["target"]))
    items = list(relation_probe.load_target_invariants(verifier, records, [(label, prime)]))
    if not items or isinstance(items[0], dict):
        raise ValueError(f"target invariant not found for {cfg.get('target')}")
    record, inv = items[0]
    ainvs = record["ainvs"]
    p = int(inv["p"])
    order = int(inv["base_order"])
    challenge, secret = relation_probe.make_challenge(verifier, inv, ainvs, str(local_args.seed))
    base = verifier.point_from_json(challenge["base"])
    public = verifier.point_from_json(challenge["public"])
    full_factor_base = [verifier.point_from_json(point) for point in challenge["factor_base"]]
    fb_size = int_value(cfg.get("factor_base_size"), int_value(local_args.factor_base_size))
    factor_base = full_factor_base[: max(4, min(fb_size, len(full_factor_base)))]
    active_challenge = dict(challenge)
    active_challenge["factor_base"] = [verifier.point_to_json(point) for point in factor_base]

    model = summation_bias_scan.short_weierstrass_model(ainvs, p)
    entries = signed_pair_mitm_probe.build_signed_pair_entries(verifier, factor_base, ainvs, p, model)
    sign_map = signed_pair_unsigned_transfer_probe.signed_index_map(verifier, factor_base, ainvs, p)
    signed_pair_limit = int_value(
        cfg.get("signed_pair_limit") or cfg.get("selected_signed_pair_count"),
        len(entries),
    )
    signed_pair_mode = str(cfg.get("signed_pair_selection_mode") or "point_collision_light")
    selected_entries = signed_pair_mitm_probe.select_entries(
        entries,
        signed_pair_limit,
        signed_pair_mode,
        f"{local_args.seed}:{cfg['target']}:{len(factor_base)}:{signed_pair_limit}:{signed_pair_mode}",
    )
    enum_args = Namespace(
        min_distinct_indices=local_args.min_distinct_indices,
        min_unsigned_distinct_indices=local_args.min_unsigned_distinct_indices,
        require_unit_coefficients=local_args.require_unit_coefficients,
    )
    candidates, candidate_stats = frontier_signed_sparse_sieve_probe.enumerate_convertible_pair_pairs(
        selected_entries,
        sign_map,
        model,
        p,
        enum_args,
    )
    scout_mode = str(cfg.get("scout_mode") or local_args.scout_mode)
    scout_limit = int_value(cfg.get("scout_limit"), int_value(local_args.scout_limit))
    scouts = eval_cover_probe.select_scout_candidates(
        candidates,
        [],
        p,
        scout_limit,
        scout_mode,
        f"{local_args.scout_seed_prefix}:eval-cover-scout:{cfg['target']}:{scout_mode}:{scout_limit}",
    )
    branch_scouts = [scout for scout in scouts if scout7_leaf65_terms(scout)]
    if not branch_scouts:
        raise ValueError("fixed scout-7 11,11,15,15 branch was not reconstructed")
    branch_scout = branch_scouts[0]
    candidate_point = verifier.add_points(branch_scout["left"]["point"], branch_scout["right"]["point"], ainvs, p)
    return {
        "active_challenge": active_challenge,
        "ainvs": ainvs,
        "base": base,
        "branch_scout": branch_scout,
        "candidate_point": candidate_point,
        "candidate_stats": candidate_stats,
        "convertible_pair_pair_candidates": len(candidates),
        "factor_base_size": len(factor_base),
        "model": model,
        "order": order,
        "p": p,
        "public": public,
        "scout_limit": scout_limit,
        "scout_mode": scout_mode,
        "scouts": scouts,
        "secret": secret,
        "selected_signed_pair_count": len(selected_entries),
    }


def row_seed_for(cfg: dict[str, Any], local_args: argparse.Namespace) -> str:
    row_pool = int_value(cfg.get("row_pool") or cfg.get("row_count") or local_args.row_pool)
    row_mode = str(cfg.get("row_mode") or local_args.row_mode)
    target = str(cfg.get("target"))
    return f"{local_args.row_seed_prefix}:eval-cover:{row_pool}:{target}:rows:{target}:{row_pool}:{row_mode}"


def row_scan_cost(first_trial: int | None, row_count: int, row_factor: int) -> dict[str, Any]:
    scanned = int(first_trial) if first_trial is not None else int(row_count)
    scanned = max(0, min(scanned, int(row_count)))
    row_factor = max(1, int(row_factor))
    return {
        "fractional_ops": round(scanned / row_factor, 8),
        "integer_ops": ceil(scanned / row_factor),
        "scanned_rows": scanned,
    }


def stream_context(
    verifier: Any,
    branch_context: dict[str, Any],
    cfg: dict[str, Any],
    local_args: argparse.Namespace,
    row_key: str,
    direct_context: dict[str, Any],
    form_keys: set[tuple[tuple[int, ...], int]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    p = int_value(branch_context["p"])
    order = int_value(branch_context["order"])
    row_pool = int_value(cfg.get("row_pool") or cfg.get("row_count") or local_args.row_pool)
    row_mode = str(cfg.get("row_mode") or local_args.row_mode)
    row_factor = max(1, int_value(local_args.row_factor, 1))
    rng = random.Random(row_seed_for(cfg, local_args))
    candidate_point = branch_context["candidate_point"]
    branch_scout = branch_context["branch_scout"]
    terms = [int_value(index) for index in branch_scout.get("unsigned_indices") or []]

    point_positions: list[int] = []
    point_match_records: list[dict[str, Any]] = []
    affine_equal_count = 0
    infinity_skips = 0
    for trial in range(1, row_pool + 1):
        a_value, b_value = target_guided_probe.mixed_row_coefficients(row_mode, trial, order, rng)
        point = verifier.add_points(
            verifier.mul_point(a_value, branch_context["base"], branch_context["ainvs"], p),
            verifier.mul_point(b_value, branch_context["public"], branch_context["ainvs"], p),
            branch_context["ainvs"],
            p,
        )
        x_value = summation_bias_scan.short_x(point, branch_context["model"], p)
        if x_value is None:
            infinity_skips += 1
        if not point_equal(point, candidate_point):
            continue
        affine_equal_count += 1
        point_positions.append(trial)
        relation = {"a": int(a_value), "b": int(b_value), "indices": terms}
        relation_terms = verifier.relation_terms(
            relation,
            branch_context["active_challenge"],
            branch_context["ainvs"],
            p,
        )
        if relation_terms is None:
            continue
        coeffs, rhs = verifier.relation_linear_form(
            relation,
            relation_terms,
            branch_context["active_challenge"],
            order,
        )
        form_key = (tuple(int_value(coeff) % order for coeff in coeffs), int_value(rhs) % order)
        duplicate = form_key in form_keys
        form_keys.add(form_key)
        point_match_records.append(
            {
                "form_duplicate": duplicate,
                "original_trial": trial,
                "q_coeff": int_value(coeffs[0]) % order,
                "rhs": int_value(rhs) % order,
                "row_key": row_key,
                "scout_pos": int_value(branch_scout.get("scout_pos")),
                "terms": terms,
            }
        )

    first_cost = row_scan_cost(min(point_positions) if point_positions else None, row_pool, row_factor)
    full_cost = row_scan_cost(row_pool, row_pool, row_factor)
    direct_affine_matches = int_value(direct_context.get("affine_match_count"))
    return (
        {
            "affine_equal_count": affine_equal_count,
            "branch_setup_ops": 1,
            "direct_affine_match_count": direct_affine_matches,
            "infinity_skips": infinity_skips,
            "point_first_scan": first_cost,
            "point_full_scan": full_cost,
            "point_match_count": len(point_match_records),
            "point_match_first_count": 1 if point_match_records else 0,
            "point_positions": point_positions,
            "row_count": row_pool,
            "row_factor": row_factor,
            "row_key": row_key,
            "row_mode": row_mode,
            "row_seed": row_seed_for(cfg, local_args),
            "stream_affine_match_count": len(point_match_records),
        },
        point_match_records,
    )


def zero_ops() -> dict[str, float]:
    return {name: 0.0 for name in MODELS}


def add_ops(left: dict[str, float], right: dict[str, Any]) -> None:
    for name in MODELS:
        left[name] = float(left.get(name, 0.0)) + float(right.get(name, 0.0))


def attempt_model_ops(contexts: list[dict[str, Any]], point_matches: list[dict[str, Any]]) -> dict[str, float]:
    first_fractional = sum(float(row["point_first_scan"]["fractional_ops"]) for row in contexts)
    first_integer = sum(int_value(row["point_first_scan"]["integer_ops"]) for row in contexts)
    full_fractional = sum(float(row["point_full_scan"]["fractional_ops"]) for row in contexts)
    full_integer = sum(int_value(row["point_full_scan"]["integer_ops"]) for row in contexts)
    branch_setup = sum(int_value(row.get("branch_setup_ops")) for row in contexts)
    first_match_ops = sum(int_value(row.get("point_match_first_count")) for row in contexts)
    full_match_ops = len(point_matches)
    return {
        "stream_branch_first_cached_fractional": round(first_fractional + first_match_ops, 8),
        "stream_branch_first_context_setup_fractional": round(first_fractional + branch_setup + first_match_ops, 8),
        "stream_branch_first_context_setup_integer": first_integer + branch_setup + first_match_ops,
        "stream_branch_full_cached_fractional": round(full_fractional + full_match_ops, 8),
        "stream_branch_full_context_setup_fractional": round(full_fractional + branch_setup + full_match_ops, 8),
        "stream_branch_full_context_setup_integer": full_integer + branch_setup + full_match_ops,
    }


def scan_attempt(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    branch_cache: dict[tuple[Any, ...], dict[str, Any]],
    direct_group: dict[str, Any],
    attempt: dict[str, Any],
    probe_args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    point_matches: list[dict[str, Any]] = []
    form_keys: set[tuple[tuple[int, ...], int]] = set()
    branch_fingerprints = []
    rho = int_value(attempt.get("rho"), int_value(direct_group.get("rho")))
    try:
        for row_key in [str(key) for key in attempt.get("row_keys") or []]:
            cfg = cfg_for_row_key(config_source, row_key, probe_args.row_pool)
            local_args = transfer_args(probe_args, row_key, int_value(attempt.get("transfer_index")))
            cache_key = branch_cache_key(cfg, local_args)
            branch_context = branch_cache.get(cache_key)
            if branch_context is None:
                branch_context = static_branch_context(verifier, records, cfg, local_args)
                branch_cache[cache_key] = branch_context
            branch_scout = branch_context["branch_scout"]
            branch_fingerprints.append(
                {
                    "row_key": row_key,
                    "scout_pos": int_value(branch_scout.get("scout_pos")),
                    "terms": [int_value(index) for index in branch_scout.get("unsigned_indices") or []],
                    "candidate_point": point_payload(branch_context.get("candidate_point")),
                    "selected_signed_pair_count": int_value(branch_context.get("selected_signed_pair_count")),
                    "convertible_pair_pair_candidates": int_value(branch_context.get("convertible_pair_pair_candidates")),
                }
            )
            profile, context_matches = stream_context(
                verifier,
                branch_context,
                cfg,
                local_args,
                row_key,
                direct_context_for(attempt, row_key),
                form_keys,
            )
            profiles.append(profile)
            point_matches.extend(context_matches)
        models = attempt_model_ops(profiles, point_matches)
        return (
            {
                "accepted_branch_first": sum(int_value(row.get("point_match_first_count")) for row in profiles) >= 2,
                "accepted_branch_full": len(point_matches) >= 2,
                "accepted_direct": bool(attempt.get("accepted")),
                "branch_fingerprints": branch_fingerprints,
                "context_rows": profiles,
                "model_ops": models,
                "model_ops_over_rho": {name: ratio(value, rho) for name, value in models.items()},
                "point_match_mismatch_count": sum(
                    1
                    for row in profiles
                    if int_value(row.get("stream_affine_match_count")) != int_value(row.get("direct_affine_match_count"))
                ),
                "point_matches": point_matches,
                "rank_gain": int_value(attempt.get("rank_gain")),
                "rho": rho,
                "row_keys": attempt.get("row_keys") or [],
                "transfer_index": int_value(attempt.get("transfer_index")),
            },
            errors,
        )
    except Exception as exc:  # noqa: BLE001 - preserve failed research cases.
        errors.append(
            {
                "error": "streaming_branch_attempt_failed",
                "message": str(exc),
                "transfer_index": int_value(attempt.get("transfer_index")),
            }
        )
        return ({}, errors)


def collect_group(
    verifier: Any,
    records: list[dict[str, Any]],
    config_source: dict[str, Any],
    branch_cache: dict[tuple[Any, ...], dict[str, Any]],
    direct_group: dict[str, Any],
    probe_args: argparse.Namespace,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    attempts: list[dict[str, Any]] = []
    branch_first_ops = zero_ops()
    branch_full_ops = zero_ops()
    branch_first_stop = None
    branch_full_stop = None
    for attempt in direct_group.get("attempts") or []:
        stream_attempt, attempt_errors = scan_attempt(
            verifier,
            records,
            config_source,
            branch_cache,
            direct_group,
            attempt,
            probe_args,
        )
        errors.extend({**item, "source_path": str(direct_group.get("source_path") or "")} for item in attempt_errors)
        if not stream_attempt:
            continue
        attempts.append(stream_attempt)
        if branch_first_stop is None:
            add_ops(branch_first_ops, {name: stream_attempt["model_ops"][name] for name in MODELS[:3]})
            if stream_attempt.get("accepted_branch_first"):
                branch_first_stop = stream_attempt
        if branch_full_stop is None:
            add_ops(branch_full_ops, {name: stream_attempt["model_ops"][name] for name in MODELS[3:]})
            if stream_attempt.get("accepted_branch_full"):
                branch_full_stop = stream_attempt

    model_ops = zero_ops()
    for name in MODELS[:3]:
        model_ops[name] = branch_first_ops[name]
    for name in MODELS[3:]:
        model_ops[name] = branch_full_ops[name]
    rho = int_value(direct_group.get("rho"))
    return (
        {
            "attempt_count": len(attempts),
            "attempts": attempts,
            "branch_first_stop": branch_first_stop,
            "branch_full_stop": branch_full_stop,
            "direct_has_rank_gain_stop": bool(direct_group.get("has_rank_gain_stop")),
            "has_branch_first_rank_gain_stop": bool(branch_first_stop and int_value(branch_first_stop.get("rank_gain")) > 0),
            "has_branch_first_stop": branch_first_stop is not None,
            "has_branch_full_rank_gain_stop": bool(branch_full_stop and int_value(branch_full_stop.get("rank_gain")) > 0),
            "has_branch_full_stop": branch_full_stop is not None,
            "has_direct_stop": bool(direct_group.get("has_accepted_stop")),
            "model_ops": model_ops,
            "model_ops_over_rho": {name: ratio(value, rho) for name, value in model_ops.items()},
            "rho": rho,
            "source_path": str(direct_group.get("source_path") or ""),
            "stop": direct_group.get("stop"),
            "window": direct_group.get("window"),
            "window_start": int_value(direct_group.get("window_start")),
        },
        errors,
    )


def split_groups(groups: list[dict[str, Any]], calibration_end: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return (
        [group for group in groups if int_value(group.get("window_start")) <= calibration_end],
        [group for group in groups if int_value(group.get("window_start")) > calibration_end],
    )


def stop_flags(group: dict[str, Any], model: str) -> tuple[bool, bool]:
    if model.startswith("stream_branch_first"):
        return bool(group.get("has_branch_first_stop")), bool(group.get("has_branch_first_rank_gain_stop"))
    return bool(group.get("has_branch_full_stop")), bool(group.get("has_branch_full_rank_gain_stop"))


def position_summary(values: list[int]) -> dict[str, Any]:
    values = sorted(int(value) for value in values)
    if not values:
        return {"count": 0}
    return {
        "count": len(values),
        "max": values[-1],
        "median": values[len(values) // 2],
        "min": values[0],
    }


def summarize(groups: list[dict[str, Any]]) -> dict[str, Any]:
    rho = max([int_value(group.get("rho")) for group in groups if int_value(group.get("rho")) > 0] or [0])
    model_summaries = {}
    for model in MODELS:
        ops = sum(float((group.get("model_ops") or {}).get(model) or 0.0) for group in groups)
        accepted = []
        rank_hits = []
        for group in groups:
            has_stop, has_rank = stop_flags(group, model)
            if has_stop:
                accepted.append(group)
            if has_rank:
                rank_hits.append(group)
        model_summaries[model] = {
            "accepted_stop_count": len(accepted),
            "cost_per_accepted_stop_over_rho": ratio(ops, rho * len(accepted)) if accepted and rho else None,
            "cost_per_rank_gain_stop_over_rho": ratio(ops, rho * len(rank_hits)) if rank_hits and rho else None,
            "ops": round(ops, 8),
            "ops_over_rho": ratio(ops, rho),
            "precision": ratio(len(rank_hits), len(accepted)) if accepted else None,
            "rank_gain_stop_count": len(rank_hits),
        }
    attempts = [attempt for group in groups for attempt in group.get("attempts") or []]
    context_rows = [
        context
        for attempt in attempts
        for context in attempt.get("context_rows") or []
    ]
    return {
        "attempt_count": len(attempts),
        "branch_first_stop_count": sum(1 for group in groups if group.get("has_branch_first_stop")),
        "branch_full_stop_count": sum(1 for group in groups if group.get("has_branch_full_stop")),
        "context_count": len(context_rows),
        "direct_stop_count": sum(1 for group in groups if group.get("has_direct_stop")),
        "group_count": len(groups),
        "model_summaries": model_summaries,
        "point_match_mismatch_count": sum(int_value(attempt.get("point_match_mismatch_count")) for attempt in attempts),
        "point_position_summary": position_summary([pos for row in context_rows for pos in row.get("point_positions") or []]),
        "rho": rho,
        "row_key_distribution": {
            key: count
            for key, count in sorted(
                Counter(str(row.get("row_key")) for row in context_rows).items(),
                key=lambda item: (-item[1], item[0]),
            )[:20]
        },
    }


def claim_status(validation: dict[str, Any]) -> str:
    if int_value(validation.get("point_match_mismatch_count")):
        return "SCOUT_POS7_STREAMING_BRANCH_POINT_NEEDS_REVIEW"
    models = validation.get("model_summaries") if isinstance(validation.get("model_summaries"), dict) else {}
    direct_stop_count = int_value(validation.get("direct_stop_count"))
    for model in (
        "stream_branch_full_context_setup_integer",
        "stream_branch_full_context_setup_fractional",
        "stream_branch_full_cached_fractional",
        "stream_branch_first_context_setup_fractional",
        "stream_branch_first_cached_fractional",
    ):
        summary = models.get(model) or {}
        cost = summary.get("cost_per_rank_gain_stop_over_rho")
        rank_hits = int_value(summary.get("rank_gain_stop_count"))
        precision = summary.get("precision")
        if cost is not None and float(cost) < 1.0 and rank_hits == direct_stop_count and rank_hits > 0 and precision == 1.0:
            return f"SCOUT_POS7_STREAMING_BRANCH_POINT_{model.upper()}_BELOW_RHO"
    return "SCOUT_POS7_STREAMING_BRANCH_POINT_STILL_ABOVE_RHO_OR_INCOMPLETE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--direct-kernel", required=True)
    parser.add_argument("--calibration-end", type=int, default=None)
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    direct_path = Path(args.direct_kernel)
    direct = load_json(direct_path)
    direct_params = direct.get("parameters") if isinstance(direct.get("parameters"), dict) else {}
    calibration_end = int_value(args.calibration_end, int_value(direct_params.get("calibration_end")))

    source_paths = sorted({str(group.get("source_path")) for group in direct.get("groups") or [] if group.get("source_path")})
    if not source_paths:
        raise SystemExit("direct kernel artifact has no source paths")
    first_source = load_json(Path(source_paths[0]))
    source_params = repair_probe.source_parameters(first_source)
    probe_args = repair_probe.probe_args_from_source(first_source)
    verifier, records, config_source, _specs_by_target = repair_probe.build_specs(source_params)

    groups: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    branch_cache: dict[tuple[Any, ...], dict[str, Any]] = {}
    for direct_group in direct.get("groups") or []:
        if not isinstance(direct_group, dict):
            continue
        stream_group, group_errors = collect_group(
            verifier,
            records,
            config_source,
            branch_cache,
            direct_group,
            probe_args,
        )
        groups.append(stream_group)
        errors.extend(group_errors)

    groups.sort(key=lambda row: (int_value(row.get("window_start")), str(row.get("source_path"))))
    calibration_groups, validation_groups = split_groups(groups, calibration_end)
    summary = {
        "calibration": summarize(calibration_groups),
        "validation": summarize(validation_groups),
    }
    payload = {
        "artifacts": {
            "direct_kernel": str(direct_path),
            "source_paths": source_paths,
        },
        "claim_status": claim_status(summary["validation"]),
        "cost_model_definitions": {
            "stream_branch_first_cached_fractional": "Generate mixed rows sequentially until the first branch-point match per context, or exhaustion on no-hit contexts; charge fractional row work plus one relation-form op per matched context.",
            "stream_branch_first_context_setup_fractional": "First-hit stream plus one fixed branch setup op per context.",
            "stream_branch_first_context_setup_integer": "First-hit stream with row work rounded to row-pool units plus fixed branch setup.",
            "stream_branch_full_cached_fractional": "Generate every mixed row in every context and test equality to the fixed branch point; charge fractional row work plus one relation-form op per point match.",
            "stream_branch_full_context_setup_fractional": "Full stream plus one fixed branch setup op per context.",
            "stream_branch_full_context_setup_integer": "Full stream with row work rounded to row-pool units plus fixed branch setup.",
        },
        "created_at": now_iso(),
        "errors": errors,
        "groups": groups,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: the fixed scout-7 branch is reconstructed from public candidate metadata under the shared target challenge.",
            "The row side is generated sequentially and does not build row hit polynomials, leaf associations, rows_by_x, or scheduled row pools.",
            "The direct kernel artifact supplies evaluation labels and expected point-match counts only; rank labels are not scanner features.",
            "A below-rho scanner ledger is an index-calculus precursor, not a deployed-curve ECDLP break.",
        ],
        "parameters": {
            "calibration_end": calibration_end,
            "direct_parameters": direct_params,
        },
        "schema": "ecdlp.low_term_total2_scout_pos7_streaming_branch_point_scanner_probe.v1",
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "error_count": len(errors),
                "summary": summary,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
