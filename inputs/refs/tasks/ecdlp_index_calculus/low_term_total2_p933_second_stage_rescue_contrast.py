#!/usr/bin/env python3
"""P933 nested-LOO second-stage rescue contrast for P932 misses."""

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
import low_term_total2_p921_c19_simple_public_predictor as p921
import low_term_total2_p922_support_class_cost_audit as p922
import low_term_total2_p923_train_only_support_class_redteam as p923
import low_term_total2_p924_train_only_objective_audit as p924
import low_term_total2_p925_gap_source_tiebreaker_redteam as p925
import low_term_total2_p926_gap_source_fallback_audit as p926
import low_term_total2_p928_p903_blind_second_holdout_audit as p928
import low_term_total2_p929_fit_only_support_ensemble_audit as p929
import low_term_total2_p930_inner_cv_oracle_distillation_audit as p930
import low_term_total2_p932_oracle_feature_contrast_audit as p932


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p933_second_stage_rescue_contrast.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p933_second_stage_rescue_contrast_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P932_SOURCE = STATE_DIR / "low_term_total2_p932_oracle_feature_contrast_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p933_second_stage_rescue_contrast.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
FIRST_STAGE_MIN_INNER_WINS = 2
FIRST_STAGE_MIN_SCORE = -1_000_000.0
RESIDUAL_STRATEGIES = (
    {"name": "residual_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "residual_rank_min2", "min_inner_wins": 2, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "residual_rank_min3", "min_inner_wins": 3, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "residual_score_min1", "min_inner_wins": 1, "min_score": 0.0, "cost_first": False},
    {"name": "residual_cost_first_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": True},
    {"name": "posthoc_residual_rank_min1", "min_inner_wins": 1, "min_score": -1_000_000.0, "cost_first": False, "posthoc": True},
)
_ORIGINAL_HAS_SUPPORT_CLASS = p922.has_support_class
_ORIGINAL_SELECTED_BY_RULE = p922.selected_by_rule
_SUPPORT_CLASS_CACHE: dict[tuple[int, tuple[int, ...], int], bool] = {}
_ATOM_EVAL_CACHE: dict[tuple[int, str], bool] = {}
_SELECTED_BY_RULE_CACHE: dict[tuple[tuple[int, ...], tuple[str, ...]], list[dict[str, Any]]] = {}


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


def cached_has_support_class(row: dict[str, Any], class_spec: dict[str, Any]) -> bool:
    index = int_value(row.get("index"), id(row))
    support = tuple(int_value(value) for value in class_spec.get("support") or [])
    rhs = int_value(class_spec.get("rhs"))
    key = (index, support, rhs)
    if key not in _SUPPORT_CLASS_CACHE:
        _SUPPORT_CLASS_CACHE[key] = _ORIGINAL_HAS_SUPPORT_CLASS(row, class_spec)
    return _SUPPORT_CLASS_CACHE[key]


def row_index(row: dict[str, Any]) -> int:
    return int_value(row.get("index"), id(row))


def cached_atom_value(row: dict[str, Any], name: str, atoms_by_name: dict[str, Any]) -> bool:
    key = (row_index(row), name)
    if key not in _ATOM_EVAL_CACHE:
        _ATOM_EVAL_CACHE[key] = bool(atoms_by_name[name](row))
    return _ATOM_EVAL_CACHE[key]


def cached_selected_by_rule(
    rows: list[dict[str, Any]],
    predicate_names: list[str],
    atoms_by_name: dict[str, Any],
) -> list[dict[str, Any]]:
    row_indices = tuple(row_index(row) for row in rows)
    predicates = tuple(str(name) for name in predicate_names)
    key = (row_indices, predicates)
    if key not in _SELECTED_BY_RULE_CACHE:
        _SELECTED_BY_RULE_CACHE[key] = [
            row
            for row in rows
            if all(cached_atom_value(row, name, atoms_by_name) for name in predicates)
        ]
    return _SELECTED_BY_RULE_CACHE[key]


def install_support_class_cache() -> None:
    p922.has_support_class = cached_has_support_class
    p922.selected_by_rule = cached_selected_by_rule


def rule_name(rule: dict[str, Any] | None) -> str:
    return p929.rule_name(rule)


def selected_indices(rule: dict[str, Any], rows: list[dict[str, Any]], atoms_by_name: dict[str, Any]) -> set[int]:
    return p929.selected_indices_for_rules([rule], rows, atoms_by_name)


def margin_bucket(margin: int) -> str:
    if margin >= 300:
        return "margin_ge_300"
    if margin >= 200:
        return "margin_200_299"
    if margin >= 100:
        return "margin_100_199"
    if margin >= 50:
        return "margin_50_99"
    if margin >= 0:
        return "margin_0_49"
    return "margin_negative"


def cached_candidate_records_for_window(
    window: str,
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    fit_maps: tuple[dict[str, set[int]], dict[str, set[int]]],
    heldout_rows: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    rows_by_index: dict[int, dict[str, Any]],
    positive_by_index: dict[int, bool],
    companion_cost: int,
    p919_cost: int,
    seed_rule: dict[str, Any],
) -> list[dict[str, Any]]:
    seed_public = p929.selected_indices_for_rules([seed_rule], public_rows, atoms_by_name)
    seed_heldout = p929.selected_indices_for_rules([seed_rule], heldout_rows, atoms_by_name)
    seed_fit = p930.fit_indices(seed_rule)
    heldout_positive = {int_value(row.get("index")) for row in heldout_rows if class_a_positive(row)}
    out: list[dict[str, Any]] = []
    for rule in p930.clean_candidate_rules(context, seed_rule):
        rule_public = selected_indices(rule, public_rows, atoms_by_name)
        public_indices = seed_public | rule_public
        full_public_cost = companion_cost + p930.c19_cost(public_indices, rows_by_index)
        if full_public_cost >= p919_cost:
            continue
        inner = inner_cv_score_cached(rule, seed_fit, fit_maps, positive_by_index)
        if int_value(inner.get("inner_false_count")) != 0:
            continue
        rule_heldout = selected_indices(rule, heldout_rows, atoms_by_name)
        heldout_selected = seed_heldout | rule_heldout
        recovered = heldout_selected & heldout_positive
        seed_recovered = seed_heldout & heldout_positive
        new_recovered = recovered - seed_recovered
        false_indices = [
            index for index in heldout_selected if not class_a_positive(rows_by_index.get(index) or {})
        ]
        record = {
            **inner,
            "full_public_cost_ops": full_public_cost,
            "heldout_false_count": len(false_indices),
            "heldout_false_indices": sorted(false_indices),
            "heldout_new_recovered_count": len(new_recovered),
            "heldout_new_recovered_indices": sorted(new_recovered),
            "heldout_recovered_count": len(recovered),
            "heldout_recovered_indices": sorted(recovered),
            "is_positive": bool(new_recovered) and not false_indices,
            "rule": rule,
            "rule_family": p929.rule_family(rule),
            "rule_heldout_indices": sorted(rule_heldout),
            "rule_name": rule_name(rule),
            "rule_public_indices": sorted(rule_public),
            "seed_heldout_indices": sorted(seed_heldout),
            "seed_public_indices": sorted(seed_public),
            "selected_c19_indices": sorted(public_indices),
            "source_window": window,
            "train_positive_source_window_count": int_value(rule.get("train_positive_source_window_count")),
            "train_selected_cost_ops": int_value(rule.get("train_selected_cost_ops")),
            "train_true_positive_count": int_value(rule.get("train_true_positive_count")),
        }
        record["tokens"] = sorted(p932.feature_tokens(record))
        out.append(record)
    return out


def fast_search_support_rules(
    class_name: str,
    rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    require_validation_positive: bool,
) -> list[dict[str, Any]]:
    class_spec = p922.SUPPORT_CLASSES[class_name]
    train_rows = [row for row in rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in rows if row.get("partition") == VALIDATION_PARTITION]
    row_by_index = {row_index(row): row for row in rows}
    train_indices = [row_index(row) for row in train_rows]
    validation_indices = [row_index(row) for row in validation_rows]
    all_indices = [row_index(row) for row in rows]
    train_index_set = set(train_indices)
    validation_index_set = set(validation_indices)
    positive_by_index = {
        row_index(row): cached_has_support_class(row, class_spec)
        for row in rows
    }
    train_positive_count = sum(1 for index in train_indices if positive_by_index.get(index, False))
    validation_positive_count = sum(1 for index in validation_indices if positive_by_index.get(index, False))
    atom_selected: dict[str, set[int]] = {}
    for name in atoms_by_name:
        atom_selected[name] = {
            index
            for index in all_indices
            if cached_atom_value(row_by_index[index], name, atoms_by_name)
        }

    def build_report(predicate_names: list[str], selected_indices: set[int]) -> dict[str, Any] | None:
        selected_train = selected_indices & train_index_set
        if not selected_train:
            return None
        train_true = sum(1 for index in selected_train if positive_by_index.get(index, False))
        train_false = len(selected_train) - train_true
        if train_false != 0:
            return None
        selected_validation = selected_indices & validation_index_set
        validation_true = sum(1 for index in selected_validation if positive_by_index.get(index, False))
        if require_validation_positive and validation_true <= 0:
            return None
        selected_all_rows = [row_by_index[index] for index in all_indices if index in selected_indices]
        return {
            "all_selected_count": len(selected_indices),
            "all_selected_indices": [row.get("index") for row in selected_all_rows],
            "class_name": class_name,
            "name": "and__" + "__".join(predicate_names),
            "predicate_names": predicate_names,
            "selected_cost_ops": sum(int_value(row.get("charged_candidate_cost_ops")) for row in selected_all_rows),
            "selected_signature_histogram": p922.support_signature_histogram(selected_all_rows),
            "train_false_positive_count": train_false,
            "train_recall": ratio(train_true, train_positive_count),
            "train_selected_count": len(selected_train),
            "train_selected_indices": [row_by_index[index].get("index") for index in train_indices if index in selected_train],
            "train_true_positive_count": train_true,
            "validation_recall": ratio(validation_true, validation_positive_count) if validation_positive_count else None,
            "validation_selected_count": len(selected_validation),
            "validation_selected_indices": [
                row_by_index[index].get("index") for index in validation_indices if index in selected_validation
            ],
            "validation_true_positive_count": validation_true,
        }

    names = list(atoms_by_name)
    reports: list[dict[str, Any]] = []
    for name in names:
        report = build_report([name], atom_selected[name])
        if report:
            reports.append(report)
    for offset, left in enumerate(names):
        left_selected = atom_selected[left]
        for right in names[offset + 1 :]:
            selected = left_selected & atom_selected[right]
            if not selected:
                continue
            report = build_report([left, right], selected)
            if report:
                reports.append(report)
    reports.sort(
        key=lambda report: (
            -int_value(report.get("train_true_positive_count")),
            -float(report.get("train_recall") or 0.0),
            int_value(report.get("selected_cost_ops"), 10**12),
            len(report.get("predicate_names") or []),
            str(report.get("name")),
        )
    )
    return reports


def fast_fit_context(fit_rows: list[dict[str, Any]]) -> dict[str, Any]:
    fit_train = [row for row in fit_rows if row.get("partition") != VALIDATION_PARTITION]
    atoms_by_name = {name: fn for name, fn in p921.atom_list(fit_train)}
    raw_rules = fast_search_support_rules(CLASS_A, fit_rows, atoms_by_name, False)
    rules = [p924.enrich_rule(rule, fit_rows) for rule in raw_rules]
    best_key, tie_class = p924.choose_tie_class(rules, p924.objective_map()[p925.PRIMARY_OBJECTIVE])
    primary_rule = p925.select_gap5_source_index(tie_class)
    return {
        "atoms_by_name": atoms_by_name,
        "best_key": list(best_key) if best_key is not None else None,
        "primary_rule": primary_rule,
        "rules": rules,
        "tie_class": tie_class,
    }


def inner_cv_score_cached(
    rule: dict[str, Any],
    seed_fit: set[int],
    fit_maps: tuple[dict[str, set[int]], dict[str, set[int]]],
    positive_by_index: dict[int, bool],
) -> dict[str, Any]:
    by_window, positive_by_window = fit_maps
    rule_fit = p930.fit_indices(rule)
    wins = 0
    recovered = 0
    false_count = 0
    selected_count = 0
    winning_windows: list[str] = []
    for window, positives in sorted(positive_by_window.items()):
        selected = (seed_fit | rule_fit) & by_window.get(window, set())
        seed_selected = seed_fit & by_window.get(window, set())
        false = [index for index in selected if not positive_by_index.get(index, False)]
        new_recovered = (selected & positives) - (seed_selected & positives)
        false_count += len(false)
        selected_count += len(selected)
        if new_recovered and not false:
            wins += 1
            recovered += len(new_recovered)
            winning_windows.append(window)
    return {
        "inner_false_count": false_count,
        "inner_recovered_positive_count": recovered,
        "inner_selected_count": selected_count,
        "inner_win_count": wins,
        "inner_winning_windows": winning_windows,
    }


def train_token_weights(candidates: list[dict[str, Any]]) -> dict[str, float]:
    pos: Counter[str] = Counter()
    neg: Counter[str] = Counter()
    for candidate in candidates:
        target = pos if candidate.get("is_positive") else neg
        for token in candidate.get("tokens") or []:
            target[str(token)] += 1
    tokens = set(pos) | set(neg)
    return {token: math.log((pos[token] + 1.0) / (neg[token] + 1.0)) for token in tokens}


def token_counts(candidates: list[dict[str, Any]]) -> tuple[Counter[str], Counter[str]]:
    pos: Counter[str] = Counter()
    neg: Counter[str] = Counter()
    for candidate in candidates:
        target = pos if candidate.get("is_positive") else neg
        for token in candidate.get("tokens") or []:
            target[str(token)] += 1
    return pos, neg


def weights_from_counts(pos: Counter[str], neg: Counter[str]) -> dict[str, float]:
    tokens = set(pos) | set(neg)
    return {token: math.log((pos[token] + 1.0) / (neg[token] + 1.0)) for token in tokens}


def weight_builder_by_exclusion(
    candidates_by_window: dict[str, list[dict[str, Any]]],
) -> Any:
    counts_by_window = {
        window: token_counts(candidates)
        for window, candidates in candidates_by_window.items()
    }
    cache: dict[tuple[str, ...], dict[str, float]] = {}

    def weights(excluded_windows: set[str]) -> dict[str, float]:
        key = tuple(sorted(excluded_windows))
        if key in cache:
            return cache[key]
        pos: Counter[str] = Counter()
        neg: Counter[str] = Counter()
        for window, (win_pos, win_neg) in counts_by_window.items():
            if window in excluded_windows:
                continue
            pos.update(win_pos)
            neg.update(win_neg)
        cache[key] = weights_from_counts(pos, neg)
        return cache[key]

    return weights


def score_candidate(candidate: dict[str, Any], weights: dict[str, float]) -> float:
    return sum(weights.get(str(token), 0.0) for token in candidate.get("tokens") or [])


def choose_first_stage_candidate(candidates: list[dict[str, Any]], weights: dict[str, float]) -> dict[str, Any] | None:
    return p932.choose_contrast_candidate(
        candidates,
        weights,
        FIRST_STAGE_MIN_INNER_WINS,
        FIRST_STAGE_MIN_SCORE,
        False,
    )


def residual_tokens(
    candidate: dict[str, Any],
    first: dict[str, Any] | None,
    residual_public_cost: int,
    p919_cost: int,
    first_public: set[int] | None = None,
) -> set[str]:
    tokens = {f"candidate_{token}" for token in candidate.get("tokens") or []}
    tokens.add(f"resid_candidate_family={candidate.get('rule_family')}")
    tokens.add(f"resid_candidate_inner_win={candidate.get('inner_win_count')}")
    tokens.add(f"resid_candidate_inner_rec={candidate.get('inner_recovered_positive_count')}")
    tokens.add(f"resid_candidate_cost={p932.cost_bucket(int_value(candidate.get('full_public_cost_ops')))}")
    tokens.add(f"resid_union_margin={margin_bucket(p919_cost - residual_public_cost)}")
    if first:
        tokens.add(f"resid_first_family={first.get('rule_family')}")
        tokens.add(f"resid_first_inner_win={first.get('inner_win_count')}")
        tokens.add(f"resid_first_cost={p932.cost_bucket(int_value(first.get('full_public_cost_ops')))}")
        tokens.add(f"resid_family_pair={first.get('rule_family')}->{candidate.get('rule_family')}")
        first_public = first_public or set(int_value(index) for index in first.get("rule_public_indices") or [])
        cand_public = set(int_value(index) for index in candidate.get("rule_public_indices") or [])
        overlap = len(first_public & cand_public)
        if overlap >= 4:
            tokens.add("resid_public_overlap_ge4")
        elif overlap >= 2:
            tokens.add("resid_public_overlap_2_3")
        elif overlap == 1:
            tokens.add("resid_public_overlap_1")
        else:
            tokens.add("resid_public_overlap_0")
    else:
        tokens.add("resid_first_family=none")
    return tokens


def residual_records_for_window(
    candidates: list[dict[str, Any]],
    first: dict[str, Any] | None,
    heldout_positive: set[int],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
) -> list[dict[str, Any]]:
    first_name = rule_name((first or {}).get("rule")) if first else ""
    first_rule_public = set(int_value(index) for index in (first or {}).get("rule_public_indices") or [])
    first_rule_heldout = set(int_value(index) for index in (first or {}).get("rule_heldout_indices") or [])
    out: list[dict[str, Any]] = []
    for candidate in candidates:
        if rule_name(candidate.get("rule")) == first_name:
            continue
        seed_public = set(int_value(index) for index in candidate.get("seed_public_indices") or [])
        seed_heldout = set(int_value(index) for index in candidate.get("seed_heldout_indices") or [])
        cand_public = set(int_value(index) for index in candidate.get("rule_public_indices") or [])
        cand_heldout = set(int_value(index) for index in candidate.get("rule_heldout_indices") or [])
        public_union = seed_public | first_rule_public | cand_public
        residual_cost = companion_cost + p930.c19_cost(public_union, rows_by_index)
        if residual_cost >= p919_cost:
            continue
        first_heldout = seed_heldout | first_rule_heldout
        heldout_union = first_heldout | cand_heldout
        first_recovered = first_heldout & heldout_positive
        recovered = heldout_union & heldout_positive
        new_recovered = recovered - first_recovered
        false_indices = [
            index for index in heldout_union if not class_a_positive(rows_by_index.get(index) or {})
        ]
        record = {
            **candidate,
            "first_rule_family": (first or {}).get("rule_family"),
            "first_rule_name": first_name,
            "is_positive": bool(new_recovered) and not false_indices,
            "residual_false_count": len(false_indices),
            "residual_false_indices": sorted(false_indices),
            "residual_full_public_cost_ops": residual_cost,
            "residual_heldout_recovered_count": len(recovered),
            "residual_heldout_recovered_indices": sorted(recovered),
            "residual_new_recovered_count": len(new_recovered),
            "residual_new_recovered_indices": sorted(new_recovered),
            "residual_selected_c19_indices": sorted(public_union),
        }
        record["tokens"] = sorted(residual_tokens(record, first, residual_cost, p919_cost, first_rule_public))
        out.append(record)
    return out


def residual_records_cached(
    cache: dict[tuple[str, str], list[dict[str, Any]]],
    window: str,
    candidates: list[dict[str, Any]],
    first: dict[str, Any] | None,
    heldout_positive: set[int],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
) -> list[dict[str, Any]]:
    first_name = rule_name((first or {}).get("rule")) if first else ""
    key = (window, first_name)
    if key not in cache:
        cache[key] = residual_records_for_window(
            candidates,
            first,
            heldout_positive,
            rows_by_index,
            companion_cost,
            p919_cost,
        )
    return cache[key]


def choose_residual_candidate(
    candidates: list[dict[str, Any]],
    weights: dict[str, float],
    min_inner_wins: int,
    min_score: float,
    cost_first: bool,
) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    best_key: tuple[Any, ...] | None = None
    for candidate in candidates:
        if int_value(candidate.get("inner_win_count")) < min_inner_wins:
            continue
        score = score_candidate(candidate, weights)
        if score < min_score:
            continue
        if cost_first:
            key = (
                int_value(candidate.get("residual_full_public_cost_ops")),
                -score,
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                candidate.get("rule_name"),
            )
        else:
            key = (
                -score,
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                int_value(candidate.get("residual_full_public_cost_ops")),
                candidate.get("rule_name"),
            )
        if best_key is None or key < best_key:
            best_key = key
            best = {**candidate, "residual_contrast_score": score, "residual_selection_key": list(key)}
    return best


def compact_first(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not candidate:
        return {}
    return p932.compact_candidate(candidate)


def compact_residual(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not candidate:
        return {}
    return {
        "first_rule_family": candidate.get("first_rule_family"),
        "first_rule_name": candidate.get("first_rule_name"),
        "heldout_new_recovered_indices": candidate.get("heldout_new_recovered_indices"),
        "inner_recovered_positive_count": candidate.get("inner_recovered_positive_count"),
        "inner_win_count": candidate.get("inner_win_count"),
        "is_positive": candidate.get("is_positive"),
        "residual_contrast_score": candidate.get("residual_contrast_score"),
        "residual_false_count": candidate.get("residual_false_count"),
        "residual_full_public_cost_ops": candidate.get("residual_full_public_cost_ops"),
        "residual_new_recovered_count": candidate.get("residual_new_recovered_count"),
        "residual_new_recovered_indices": candidate.get("residual_new_recovered_indices"),
        "residual_selection_key": candidate.get("residual_selection_key"),
        "rule_family": candidate.get("rule_family"),
        "rule_name": candidate.get("rule_name"),
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
            "posthoc_residual_rank_min1",
        }:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > first_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P933_SECOND_STAGE_RESCUE_SUPPORT_GAIN"
    if any(
        name.startswith("residual_")
        and int_value(summary.get("heldout_recovered_positive_count")) > first_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P933_RESCUE_GAINS_SUPPORT_BUT_FAILS_GATE"
    return "NEGATIVE_RESULT_P933_SECOND_STAGE_DOES_NOT_BEAT_P932"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    install_support_class_cache()
    p914_payload = load_json(args.p914_source)
    p932_payload = load_json(args.p932_source) if args.p932_source.exists() else {}
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
    companion_report = p922.full_policy_report("p933_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value(p922.compact_policy(companion_report).get("charged_candidate_cost_ops"))
    fallback = p926.fallback_map()[p929.P928_BEST_STRATEGY]
    contexts: dict[str, dict[str, Any]] = {}
    all_candidates: dict[str, list[dict[str, Any]]] = {}
    heldout_positive_by_window: dict[str, set[int]] = {}

    for window in windows:
        fit_rows = [row for row in p903_blind_rows if p923.source_window(row) != window]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        context = fast_fit_context(fit_rows)
        atoms_by_name = context.get("atoms_by_name") or {}
        _source, seed_rule = p926.choose_rule(context, fallback)
        fit_maps = p930.fit_window_maps(fit_rows)
        candidates = cached_candidate_records_for_window(
            window,
            context,
            fit_rows,
            fit_maps,
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
            "seed_rule": seed_rule,
        }
        all_candidates[window] = candidates
        heldout_positive_by_window[window] = {
            int_value(row.get("index")) for row in heldout_rows if class_a_positive(row)
        }

    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": [],
        "p932_loo_token_rank_min2_reproduced": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    for strategy in RESIDUAL_STRATEGIES:
        strategy_items[str(strategy["name"])] = []

    first_stage_by_target: dict[str, dict[str, Any] | None] = {}
    residual_training_summaries: dict[str, Any] = {}
    posthoc_residual_pool: list[dict[str, Any]] = []
    first_stage_weights_excluding = weight_builder_by_exclusion(all_candidates)
    residual_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}

    for window in windows:
        first_weights = first_stage_weights_excluding({window})
        first = choose_first_stage_candidate(all_candidates[window], first_weights)
        first_stage_by_target[window] = first
        posthoc_residual_pool.extend(
            residual_records_cached(
                residual_cache,
                window,
                all_candidates[window],
                first,
                heldout_positive_by_window[window],
                rows_by_index,
                companion_cost,
                p919_cost,
            )
        )

    posthoc_residual_weights = train_token_weights(posthoc_residual_pool)

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
                {
                    "chosen_first_candidate": compact_first(first),
                    "selector": "p932_loo_token_rank_min2_reproduced",
                },
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

        residual_training_records: list[dict[str, Any]] = []
        for train_window in windows:
            if train_window == window:
                continue
            nested_first_weights = first_stage_weights_excluding({window, train_window})
            train_first = choose_first_stage_candidate(all_candidates[train_window], nested_first_weights)
            residual_training_records.extend(
                residual_records_cached(
                    residual_cache,
                    train_window,
                    all_candidates[train_window],
                    train_first,
                    heldout_positive_by_window[train_window],
                    rows_by_index,
                    companion_cost,
                    p919_cost,
                )
            )
        residual_weights = train_token_weights(residual_training_records)
        residual_training_summaries[window] = {
            "nested_training_record_count": len(residual_training_records),
            "nested_training_positive_count": sum(1 for item in residual_training_records if item.get("is_positive")),
            "top_tokens": top_token_summary(residual_weights, 8),
        }
        current_residual_candidates = residual_records_cached(
            residual_cache,
            window,
            all_candidates[window],
            first,
            heldout_positive_by_window[window],
            rows_by_index,
            companion_cost,
            p919_cost,
        )
        for strategy in RESIDUAL_STRATEGIES:
            strategy_name = str(strategy["name"])
            weights = posthoc_residual_weights if strategy.get("posthoc") else residual_weights
            chosen = choose_residual_candidate(
                current_residual_candidates,
                weights,
                int_value(strategy["min_inner_wins"]),
                float(strategy["min_score"]),
                bool(strategy["cost_first"]),
            )
            rules = list(first_rules)
            if chosen:
                rules.append(chosen["rule"])
            strategy_rules[strategy_name] = (
                rules,
                {
                    "chosen_first_candidate": compact_first(first),
                    "chosen_residual_candidate": compact_residual(chosen),
                    "cost_first": bool(strategy["cost_first"]),
                    "min_inner_wins": int_value(strategy["min_inner_wins"]),
                    "min_score": float(strategy["min_score"]),
                    "selector": "posthoc_residual_contrast" if strategy.get("posthoc") else "nested_loo_residual_contrast",
                },
            )

        for name, (rules, metadata) in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(ctx["fit_rows"]),
                    "heldout_source_window": window,
                    "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": p929.score_ensemble(
                        f"p933_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": p929.score_ensemble(
                        f"p933_{name}_p903",
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
            "residual_candidate_count": len(
                residual_records_cached(
                    residual_cache,
                    window,
                    candidates,
                    first_stage_by_target[window],
                    heldout_positive_by_window[window],
                    rows_by_index,
                    companion_cost,
                    p919_cost,
                )
            ),
            "residual_positive_candidate_count": sum(
                1
                for candidate in residual_records_cached(
                    residual_cache,
                    window,
                    candidates,
                    first_stage_by_target[window],
                    heldout_positive_by_window[window],
                    rows_by_index,
                    companion_cost,
                    p919_cost,
                )
                if candidate.get("is_positive")
            ),
        }
        for window, candidates in all_candidates.items()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p932_source": str(args.p932_source),
            "script": str(Path(__file__)),
        },
        "candidate_contrast": {
            "candidate_counts": candidate_counts,
            "nested_residual_training_by_window": residual_training_summaries,
            "posthoc_residual_top_tokens": top_token_summary(posthoc_residual_weights, 12),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous choices remove P903 and current outer heldout support labels.",
            "NESTED-LOO-RESIDUAL: residual training examples for a target window use nested first-stage choices that exclude target-window labels.",
            "POSTHOC-CONTROL: posthoc_residual_rank_min1 uses all residual labels and is diagnostic only.",
            "ORACLE-CONTROL: the oracle upper bound uses current outer heldout labels and is not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p933_second_stage_rescue_contrast",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "first_stage": {
                "min_inner_wins": FIRST_STAGE_MIN_INNER_WINS,
                "min_score": FIRST_STAGE_MIN_SCORE,
                "source": "P932 loo_token_rank_min2",
            },
            "p903_c19_indices": sorted(p903_indices),
            "p932_claim": p932_payload.get("claim_status"),
            "residual_strategies": list(RESIDUAL_STRATEGIES),
            "rho_estimate": p905.RHO_ESTIMATE,
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
    parser.add_argument("--p932-source", type=Path, default=P932_SOURCE)
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
        "residual_rank_min1",
        "residual_rank_min2",
        "residual_cost_first_min1",
        "posthoc_residual_rank_min1",
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
