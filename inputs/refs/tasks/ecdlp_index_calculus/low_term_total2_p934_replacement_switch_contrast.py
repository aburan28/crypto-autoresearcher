#!/usr/bin/env python3
"""P934 nested-LOO replacement switch contrast for P932/P933 misses."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p922_support_class_cost_audit as p922
import low_term_total2_p923_train_only_support_class_redteam as p923
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925
import low_term_total2_p926_gap_source_fallback_audit as p926
import low_term_total2_p928_p903_blind_second_holdout_audit as p928
import low_term_total2_p929_fit_only_support_ensemble_audit as p929
import low_term_total2_p930_inner_cv_oracle_distillation_audit as p930
import low_term_total2_p932_oracle_feature_contrast_audit as p932
import low_term_total2_p933_second_stage_rescue_contrast as p933


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p934_replacement_switch_contrast.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p934_replacement_switch_contrast_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P933_SOURCE = STATE_DIR / "low_term_total2_p933_second_stage_rescue_contrast_probe.json"
SCHEMA = "ecdlp.low_term_total2_p934_replacement_switch_contrast.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
FIRST_STAGE_MIN_INNER_WINS = 2
FIRST_STAGE_MIN_SCORE = -1_000_000.0
SWITCH_STRATEGIES = (
    {"name": "switch_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "switch_rank_min2", "min_inner_wins": 2, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "switch_score_min1", "min_inner_wins": 1, "min_score": 0.0, "cost_first": False},
    {"name": "switch_cost_not_worse_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False, "require_cost_not_worse": True},
    {"name": "switch_inner_not_worse_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False, "require_inner_not_worse": True},
    {"name": "switch_pareto_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False, "require_cost_not_worse": True, "require_inner_not_worse": True},
    {"name": "switch_cost_first_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": True},
    {"name": "posthoc_switch_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False, "posthoc": True},
)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p908.int_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p908.ratio(numerator, denominator)


def class_a_positive(row: dict[str, Any]) -> bool:
    return p929.class_a_positive(row)


def rule_name(rule: dict[str, Any] | None) -> str:
    return p929.rule_name(rule)


def delta_bucket(delta: int) -> str:
    if delta <= -200:
        return "delta_le_-200"
    if delta <= -100:
        return "delta_-199_-100"
    if delta <= -1:
        return "delta_-99_-1"
    if delta == 0:
        return "delta_0"
    if delta < 100:
        return "delta_1_99"
    if delta < 200:
        return "delta_100_199"
    return "delta_ge_200"


def overlap_bucket(overlap: int) -> str:
    if overlap == 0:
        return "overlap_0"
    if overlap == 1:
        return "overlap_1"
    if overlap <= 3:
        return "overlap_2_3"
    return "overlap_ge4"


def train_token_weights(candidates: list[dict[str, Any]]) -> dict[str, float]:
    pos: Counter[str] = Counter()
    neg: Counter[str] = Counter()
    for candidate in candidates:
        target = pos if candidate.get("is_positive") else neg
        for token in candidate.get("tokens") or []:
            target[str(token)] += 1
    tokens = set(pos) | set(neg)
    return {token: math.log((pos[token] + 1.0) / (neg[token] + 1.0)) for token in tokens}


def score_candidate(candidate: dict[str, Any], weights: dict[str, float]) -> float:
    return sum(weights.get(str(token), 0.0) for token in candidate.get("tokens") or [])


def switch_tokens(candidate: dict[str, Any], first: dict[str, Any] | None) -> set[str]:
    tokens = {f"candidate_{token}" for token in candidate.get("tokens") or []}
    tokens.add(f"switch_candidate_family={candidate.get('rule_family')}")
    tokens.add(f"switch_candidate_inner_win={candidate.get('inner_win_count')}")
    tokens.add(f"switch_candidate_inner_rec={candidate.get('inner_recovered_positive_count')}")
    tokens.add(f"switch_candidate_cost={p932.cost_bucket(int_value(candidate.get('full_public_cost_ops')))}")
    if not first:
        tokens.add("switch_first_family=none")
        return tokens
    cost_delta = int_value(candidate.get("full_public_cost_ops")) - int_value(first.get("full_public_cost_ops"))
    inner_win_delta = int_value(candidate.get("inner_win_count")) - int_value(first.get("inner_win_count"))
    inner_rec_delta = int_value(candidate.get("inner_recovered_positive_count")) - int_value(first.get("inner_recovered_positive_count"))
    first_public = set(int_value(index) for index in first.get("rule_public_indices") or [])
    cand_public = set(int_value(index) for index in candidate.get("rule_public_indices") or [])
    tokens.update(
        {
            f"switch_first_family={first.get('rule_family')}",
            f"switch_first_inner_win={first.get('inner_win_count')}",
            f"switch_first_inner_rec={first.get('inner_recovered_positive_count')}",
            f"switch_first_cost={p932.cost_bucket(int_value(first.get('full_public_cost_ops')))}",
            f"switch_family_pair={first.get('rule_family')}->{candidate.get('rule_family')}",
            f"switch_cost_delta={delta_bucket(cost_delta)}",
            f"switch_inner_win_delta={delta_bucket(inner_win_delta)}",
            f"switch_inner_rec_delta={delta_bucket(inner_rec_delta)}",
            f"switch_public_overlap={overlap_bucket(len(first_public & cand_public))}",
            "switch_cost_not_worse" if cost_delta <= 0 else "switch_cost_worse",
            "switch_inner_win_not_worse" if inner_win_delta >= 0 else "switch_inner_win_worse",
            "switch_inner_rec_not_worse" if inner_rec_delta >= 0 else "switch_inner_rec_worse",
        }
    )
    return tokens


def switch_records_for_window(
    candidates: list[dict[str, Any]],
    first: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    first_name = rule_name((first or {}).get("rule")) if first else ""
    first_recovered = set(int_value(index) for index in (first or {}).get("heldout_recovered_indices") or [])
    first_count = len(first_recovered)
    first_cost = int_value((first or {}).get("full_public_cost_ops"))
    first_inner_wins = int_value((first or {}).get("inner_win_count"))
    first_inner_rec = int_value((first or {}).get("inner_recovered_positive_count"))
    out: list[dict[str, Any]] = []
    for candidate in candidates:
        candidate_name = rule_name(candidate.get("rule"))
        if candidate_name == first_name:
            continue
        recovered = set(int_value(index) for index in candidate.get("heldout_recovered_indices") or [])
        false_count = int_value(candidate.get("heldout_false_count"))
        cost = int_value(candidate.get("full_public_cost_ops"))
        record = {
            **candidate,
            "first_rule_family": (first or {}).get("rule_family"),
            "first_rule_name": first_name,
            "first_full_public_cost_ops": first_cost,
            "first_heldout_recovered_count": first_count,
            "first_heldout_recovered_indices": sorted(first_recovered),
            "first_inner_recovered_positive_count": first_inner_rec,
            "first_inner_win_count": first_inner_wins,
            "is_positive": false_count == 0 and len(recovered) > first_count,
            "switch_cost_delta_ops": cost - first_cost,
            "switch_inner_recovered_delta": int_value(candidate.get("inner_recovered_positive_count")) - first_inner_rec,
            "switch_inner_win_delta": int_value(candidate.get("inner_win_count")) - first_inner_wins,
            "switch_lost_recovered_indices": sorted(first_recovered - recovered),
            "switch_new_recovered_indices": sorted(recovered - first_recovered),
            "switch_recovered_delta": len(recovered) - first_count,
        }
        record["tokens"] = sorted(switch_tokens(record, first))
        out.append(record)
    return out


def switch_records_cached(
    cache: dict[tuple[str, str], list[dict[str, Any]]],
    window: str,
    candidates: list[dict[str, Any]],
    first: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    first_name = rule_name((first or {}).get("rule")) if first else ""
    key = (window, first_name)
    if key not in cache:
        cache[key] = switch_records_for_window(candidates, first)
    return cache[key]


def choose_switch_candidate(
    candidates: list[dict[str, Any]],
    weights: dict[str, float],
    min_inner_wins: int,
    min_score: float,
    cost_first: bool,
    require_cost_not_worse: bool,
    require_inner_not_worse: bool,
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_key: tuple[Any, ...] | None = None
    for candidate in candidates:
        if int_value(candidate.get("inner_win_count")) < min_inner_wins:
            continue
        if require_cost_not_worse and int_value(candidate.get("switch_cost_delta_ops")) > 0:
            continue
        if require_inner_not_worse and int_value(candidate.get("switch_inner_recovered_delta")) < 0:
            continue
        score = score_candidate(candidate, weights)
        if score < min_score:
            continue
        if cost_first:
            key = (
                int_value(candidate.get("full_public_cost_ops")),
                -score,
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                candidate.get("rule_name"),
            )
        else:
            key = (
                -score,
                -int_value(candidate.get("switch_recovered_delta")),
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                int_value(candidate.get("full_public_cost_ops")),
                candidate.get("rule_name"),
            )
        if best_key is None or key < best_key:
            best_key = key
            best = {**candidate, "switch_contrast_score": score, "switch_selection_key": list(key)}
    return best


def compact_switch(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not candidate:
        return {}
    return {
        "first_rule_family": candidate.get("first_rule_family"),
        "first_rule_name": candidate.get("first_rule_name"),
        "full_public_cost_ops": candidate.get("full_public_cost_ops"),
        "heldout_false_count": candidate.get("heldout_false_count"),
        "heldout_recovered_indices": candidate.get("heldout_recovered_indices"),
        "inner_recovered_positive_count": candidate.get("inner_recovered_positive_count"),
        "inner_win_count": candidate.get("inner_win_count"),
        "is_positive": candidate.get("is_positive"),
        "rule_family": candidate.get("rule_family"),
        "rule_name": candidate.get("rule_name"),
        "switch_contrast_score": candidate.get("switch_contrast_score"),
        "switch_cost_delta_ops": candidate.get("switch_cost_delta_ops"),
        "switch_lost_recovered_indices": candidate.get("switch_lost_recovered_indices"),
        "switch_new_recovered_indices": candidate.get("switch_new_recovered_indices"),
        "switch_recovered_delta": candidate.get("switch_recovered_delta"),
        "switch_selection_key": candidate.get("switch_selection_key"),
        "tokens": candidate.get("tokens"),
    }


def top_token_summary(weights: dict[str, float], limit: int = 12) -> dict[str, list[dict[str, Any]]]:
    positive = sorted(weights.items(), key=lambda item: (-item[1], item[0]))[:limit]
    negative = sorted(weights.items(), key=lambda item: (item[1], item[0]))[:limit]
    return {
        "positive": [{"token": token, "weight": weight} for token, weight in positive],
        "negative": [{"token": token, "weight": weight} for token, weight in negative],
    }


def summarize(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return p930.summarize(items, target_rank, p919_cost)


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    first = summaries.get("p932_loo_token_rank_min2_reproduced") or {}
    first_rec = int_value(first.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if name in {
            "seed_only_control",
            "p932_loo_token_rank_min2_reproduced",
            "oracle_cost_ceiling_upper_bound",
            "posthoc_switch_rank_min1",
        }:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > first_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P934_REPLACEMENT_SWITCH_SUPPORT_GAIN"
    if any(
        name.startswith("switch_")
        and int_value(summary.get("heldout_recovered_positive_count")) > first_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P934_SWITCH_GAINS_SUPPORT_BUT_FAILS_GATE"
    return "NEGATIVE_RESULT_P934_REPLACEMENT_SWITCH_DOES_NOT_BEAT_P932"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p933.install_support_class_cache()
    p914_payload = load_json(args.p914_source)
    p933_payload = load_json(args.p933_source) if args.p933_source.exists() else {}
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    rows_by_index = {int_value(row.get("index")): row for row in public_rows}
    positive_by_index = {index: class_a_positive(row) for index, row in rows_by_index.items()}
    p903_indices = p928.p903_c19_indices(public_rows)
    p903_blind_rows = p928.rows_excluding_indices(public_rows, p903_indices)
    p903_blind_records = p928.records_excluding_indices(records, p903_indices)
    windows = sorted(
        {
            p923.source_window(row)
            for row in p903_blind_rows
            if row.get("partition") != VALIDATION_PARTITION and p923.source_window(row) != "unknown"
        }
    )
    p919_report = p915.policy_report(
        "p919_best_policy_recomputed",
        p919.policy_records(
            records,
            c19_extra_mode="gap_eq5",
            c19_extra_cost_cap=180,
            c90_gap_mode="gap_le3",
            c90_cost_cap=128,
        ),
        "P919 positive control.",
        target_rank,
        True,
    )
    p919_cost = int_value(p919_report.get("charged_candidate_cost_ops"))
    companion_report = p922.full_policy_report("p934_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value(p922.compact_policy(companion_report).get("charged_candidate_cost_ops"))
    fallback = p926.fallback_map()[p929.P928_BEST_STRATEGY]
    contexts: dict[str, dict[str, Any]] = {}
    all_candidates: dict[str, list[dict[str, Any]]] = {}

    for window in windows:
        fit_rows = [row for row in p903_blind_rows if p923.source_window(row) != window]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        context = p933.fast_fit_context(fit_rows)
        atoms_by_name = context.get("atoms_by_name") or {}
        _source, seed_rule = p926.choose_rule(context, fallback)
        candidates = p933.cached_candidate_records_for_window(
            window,
            context,
            fit_rows,
            p930.fit_window_maps(fit_rows),
            heldout_rows,
            public_rows,
            atoms_by_name,
            rows_by_index,
            positive_by_index,
            companion_cost,
            p919_cost,
            seed_rule,
        )
        contexts[window] = {
            "atoms_by_name": atoms_by_name,
            "context": context,
            "fit_rows": fit_rows,
            "heldout_rows": heldout_rows,
            "heldout_positive": {int_value(row.get("index")) for row in heldout_rows if class_a_positive(row)},
            "seed_rule": seed_rule,
        }
        all_candidates[window] = candidates

    first_stage_weights_excluding = p933.weight_builder_by_exclusion(all_candidates)
    first_stage_by_target: dict[str, dict[str, Any] | None] = {}
    switch_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
    posthoc_switch_pool: list[dict[str, Any]] = []
    for window in windows:
        first = p933.choose_first_stage_candidate(
            all_candidates[window],
            first_stage_weights_excluding({window}),
        )
        first_stage_by_target[window] = first
        posthoc_switch_pool.extend(switch_records_cached(switch_cache, window, all_candidates[window], first))

    posthoc_switch_weights = train_token_weights(posthoc_switch_pool)
    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": [],
        "p932_loo_token_rank_min2_reproduced": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    for strategy in SWITCH_STRATEGIES:
        strategy_items[str(strategy["name"])] = []
    switch_training_summaries: dict[str, Any] = {}

    for window in windows:
        ctx = contexts[window]
        atoms_by_name = ctx["atoms_by_name"]
        heldout_rows = ctx["heldout_rows"]
        seed_rule = ctx["seed_rule"]
        first = first_stage_by_target[window]
        first_rules = [seed_rule] + ([first["rule"]] if first else [])
        strategy_rules: dict[str, tuple[list[dict[str, Any]], dict[str, Any]]] = {
            "seed_only_control": ([seed_rule] if seed_rule else [], {"selector": "p928_seed"}),
            "p932_loo_token_rank_min2_reproduced": (
                first_rules,
                {"selector": "p932_loo_token_rank_min2_reproduced", "chosen_first_candidate": p933.compact_first(first)},
            ),
            "oracle_cost_ceiling_upper_bound": (
                p929.oracle_cost_ceiling_ensemble(
                    ctx["context"],
                    heldout_rows,
                    public_rows,
                    atoms_by_name,
                    rows_by_index,
                    companion_cost,
                    p919_cost,
                    seed_rule,
                ),
                {"selector": "heldout_label_oracle"},
            ),
        }
        switch_training_records: list[dict[str, Any]] = []
        for train_window in windows:
            if train_window == window:
                continue
            nested_first = p933.choose_first_stage_candidate(
                all_candidates[train_window],
                first_stage_weights_excluding({window, train_window}),
            )
            switch_training_records.extend(
                switch_records_cached(switch_cache, train_window, all_candidates[train_window], nested_first)
            )
        switch_weights = train_token_weights(switch_training_records)
        switch_training_summaries[window] = {
            "nested_training_positive_count": sum(1 for item in switch_training_records if item.get("is_positive")),
            "nested_training_record_count": len(switch_training_records),
            "top_tokens": top_token_summary(switch_weights, 8),
        }
        current_switch_candidates = switch_records_cached(switch_cache, window, all_candidates[window], first)
        for strategy in SWITCH_STRATEGIES:
            strategy_name = str(strategy["name"])
            weights = posthoc_switch_weights if strategy.get("posthoc") else switch_weights
            chosen = choose_switch_candidate(
                current_switch_candidates,
                weights,
                int_value(strategy["min_inner_wins"]),
                float(strategy["min_score"]),
                bool(strategy["cost_first"]),
                bool(strategy.get("require_cost_not_worse")),
                bool(strategy.get("require_inner_not_worse")),
            )
            rules = [seed_rule] + ([chosen["rule"]] if chosen else ([first["rule"]] if first else []))
            strategy_rules[strategy_name] = (
                rules,
                {
                    "chosen_first_candidate": p933.compact_first(first),
                    "chosen_switch_candidate": compact_switch(chosen),
                    "cost_first": bool(strategy["cost_first"]),
                    "min_inner_wins": int_value(strategy["min_inner_wins"]),
                    "min_score": float(strategy["min_score"]),
                    "require_cost_not_worse": bool(strategy.get("require_cost_not_worse")),
                    "require_inner_not_worse": bool(strategy.get("require_inner_not_worse")),
                    "selector": "posthoc_switch_contrast" if strategy.get("posthoc") else "nested_loo_switch_contrast",
                },
            )
        for name, (rules, metadata) in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(ctx["fit_rows"]),
                    "heldout_source_window": window,
                    "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": p929.score_ensemble(
                        f"p934_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": p929.score_ensemble(
                        f"p934_{name}_p903",
                        rules,
                        public_rows,
                        atoms_by_name,
                        records,
                        target_rank,
                        p919_cost,
                    ),
                    "rule_families": [p929.rule_family(rule) for rule in rules],
                    "rule_names": [rule_name(rule) for rule in rules],
                    "selector_metadata": metadata,
                }
            )

    summaries = {name: summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    candidate_counts = {
        window: {
            "candidate_count": len(candidates),
            "positive_candidate_count": sum(1 for candidate in candidates if candidate.get("is_positive")),
            "switch_candidate_count": len(
                switch_records_cached(switch_cache, window, candidates, first_stage_by_target[window])
            ),
            "switch_positive_candidate_count": sum(
                1
                for candidate in switch_records_cached(switch_cache, window, candidates, first_stage_by_target[window])
                if candidate.get("is_positive")
            ),
        }
        for window, candidates in all_candidates.items()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p933_source": str(args.p933_source),
            "script": str(Path(__file__)),
        },
        "candidate_contrast": {
            "candidate_counts": candidate_counts,
            "nested_switch_training_by_window": switch_training_summaries,
            "posthoc_switch_top_tokens": top_token_summary(posthoc_switch_weights, 12),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous choices remove P903 and current outer heldout support labels.",
            "NESTED-LOO-SWITCH: switch training examples for a target window use nested first-stage choices that exclude target-window labels.",
            "POSTHOC-CONTROL: posthoc_switch_rank_min1 uses all switch labels and is diagnostic only.",
            "ORACLE-CONTROL: the oracle upper bound uses current outer heldout labels and is not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p934_replacement_switch_contrast",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "first_stage": {
                "min_inner_wins": FIRST_STAGE_MIN_INNER_WINS,
                "min_score": FIRST_STAGE_MIN_SCORE,
                "source": "P932 loo_token_rank_min2",
            },
            "p903_c19_indices": sorted(p903_indices),
            "p933_claim": p933_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "switch_strategies": list(SWITCH_STRATEGIES),
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p919": p922.compact_policy(p919_report),
        },
        "schema": SCHEMA,
        "summary": {
            "second_holdout": strategy_items,
            "strategy_summaries": summaries,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p933-source", type=Path, default=P933_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in [
        "seed_only_control",
        "p932_loo_token_rank_min2_reproduced",
        "switch_rank_min1",
        "switch_score_min1",
        "switch_cost_not_worse_rank_min1",
        "switch_pareto_rank_min1",
        "posthoc_switch_rank_min1",
        "oracle_cost_ceiling_upper_bound",
    ]:
        summary = summaries.get(name) or {}
        parts.append(
            "{name}:rec={rec}/{pos},false={false},p903_pass={passes}/{total}".format(
                name=name,
                rec=summary.get("heldout_recovered_positive_count"),
                pos=summary.get("heldout_positive_count"),
                false=summary.get("heldout_false_selected_count"),
                passes=summary.get("p903_pass_count"),
                total=summary.get("source_window_count"),
            )
        )
    print(
        "claim={claim} {parts} fresh1160={fresh} out={out}".format(
            claim=payload.get("claim_status"),
            parts=" | ".join(parts),
            fresh=(payload.get("fresh_window_summary") or {}).get("fresh_1160_plus_available"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
