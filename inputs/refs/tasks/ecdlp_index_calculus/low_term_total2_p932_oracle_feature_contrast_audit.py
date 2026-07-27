#!/usr/bin/env python3
"""P932 leave-one-window oracle-feature contrast audit."""

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
import low_term_total2_p931_margin_aware_abstaining_selector as p931


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p932_oracle_feature_contrast_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p932_oracle_feature_contrast_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P931_SOURCE = STATE_DIR / "low_term_total2_p931_margin_aware_abstaining_selector_probe.json"
SCHEMA = "ecdlp.low_term_total2_p932_oracle_feature_contrast_audit.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
CONTRAST_STRATEGIES = (
    {"name": "loo_token_rank_min2", "min_inner_wins": 2, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "loo_token_rank_min3", "min_inner_wins": 3, "min_score": -1_000_000.0, "cost_first": False},
    {"name": "loo_token_score_min2", "min_inner_wins": 2, "min_score": 0.0, "cost_first": False},
    {"name": "loo_token_score_min3", "min_inner_wins": 3, "min_score": 0.0, "cost_first": False},
    {"name": "loo_token_score_min4", "min_inner_wins": 4, "min_score": 0.0, "cost_first": False},
    {"name": "loo_token_score_min2_score1", "min_inner_wins": 2, "min_score": 1.0, "cost_first": False},
    {"name": "loo_token_cost_first_min2", "min_inner_wins": 2, "min_score": 0.0, "cost_first": True},
    {"name": "posthoc_all_token_rank_min2", "min_inner_wins": 2, "min_score": -1_000_000.0, "cost_first": False, "posthoc": True},
    {"name": "posthoc_all_token_score_min2", "min_inner_wins": 2, "min_score": 0.0, "cost_first": False, "posthoc": True},
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


def predicate_class(name: str) -> str:
    if name.startswith("gap_eq_"):
        return "gap_eq"
    if name.startswith("gap_ne_"):
        return "gap_ne"
    if name.startswith("gap_le_"):
        return "gap_le"
    if name.startswith("gap_ge_"):
        return "gap_ge"
    if name.startswith("cost_le_"):
        return "cost_le"
    if name.startswith("cost_ge_"):
        return "cost_ge"
    for prefix in ("salt_min_mod", "salt_max_mod", "salt_sum_mod", "source_index_mod", "transfer_mod"):
        if name.startswith(prefix):
            return prefix
    if name.startswith("ops_eq_"):
        return "ops_eq"
    return name.split("_", 1)[0]


def cost_bucket(cost: int) -> str:
    if cost < 1200:
        return "cost_lt_1200"
    if cost < 1300:
        return "cost_1200_1299"
    if cost < 1400:
        return "cost_1300_1399"
    if cost < 1500:
        return "cost_1400_1499"
    if cost < 1600:
        return "cost_1500_1599"
    return "cost_1600_plus"


def feature_tokens(candidate: dict[str, Any]) -> set[str]:
    rule = candidate.get("rule") or {}
    predicates = [str(name) for name in rule.get("predicate_names") or []]
    tokens = {
        f"family={candidate.get('rule_family')}",
        f"arity={len(predicates)}",
        f"inner_win={candidate.get('inner_win_count')}",
        f"inner_rec={candidate.get('inner_recovered_positive_count')}",
        f"train_tp={candidate.get('train_true_positive_count')}",
        f"train_windows={candidate.get('train_positive_source_window_count')}",
        cost_bucket(int_value(candidate.get("full_public_cost_ops"))),
    }
    for predicate in predicates:
        tokens.add(f"predclass={predicate_class(predicate)}")
    # Exact predicates are diagnostic but can overfit; keep them separate in the artifact.
    for predicate in predicates:
        tokens.add(f"pred={predicate}")
    return tokens


def selected_indices(rule: dict[str, Any], rows: list[dict[str, Any]], atoms_by_name: dict[str, Any]) -> set[int]:
    return p929.selected_indices_for_rules([rule], rows, atoms_by_name)


def candidate_records_for_window(
    window: str,
    context: dict[str, Any],
    fit_rows: list[dict[str, Any]],
    heldout_rows: list[dict[str, Any]],
    public_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    rows_by_index: dict[int, dict[str, Any]],
    companion_cost: int,
    p919_cost: int,
    seed_rule: dict[str, Any],
) -> list[dict[str, Any]]:
    seed_public = p929.selected_indices_for_rules([seed_rule], public_rows, atoms_by_name)
    seed_heldout = p929.selected_indices_for_rules([seed_rule], heldout_rows, atoms_by_name)
    heldout_positive = {int_value(row.get("index")) for row in heldout_rows if class_a_positive(row)}
    out: list[dict[str, Any]] = []
    for rule in p930.clean_candidate_rules(context, seed_rule):
        public_indices = seed_public | selected_indices(rule, public_rows, atoms_by_name)
        full_public_cost = companion_cost + p930.c19_cost(public_indices, rows_by_index)
        if full_public_cost >= p919_cost:
            continue
        inner = p930.inner_cv_score(rule, seed_rule, fit_rows, rows_by_index)
        if int_value(inner.get("inner_false_count")) != 0:
            continue
        heldout_selected = seed_heldout | selected_indices(rule, heldout_rows, atoms_by_name)
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
            "rule_name": rule_name(rule),
            "selected_c19_indices": sorted(public_indices),
            "source_window": window,
            "train_positive_source_window_count": int_value(rule.get("train_positive_source_window_count")),
            "train_selected_cost_ops": int_value(rule.get("train_selected_cost_ops")),
            "train_true_positive_count": int_value(rule.get("train_true_positive_count")),
        }
        record["tokens"] = sorted(feature_tokens(record))
        out.append(record)
    return out


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


def choose_contrast_candidate(
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
        key = (
            int_value(candidate.get("full_public_cost_ops")),
            -score,
            -int_value(candidate.get("inner_win_count")),
            -int_value(candidate.get("inner_recovered_positive_count")),
            candidate.get("rule_name"),
        ) if cost_first else (
            -score,
            -int_value(candidate.get("inner_win_count")),
            -int_value(candidate.get("inner_recovered_positive_count")),
            int_value(candidate.get("full_public_cost_ops")),
            candidate.get("rule_name"),
        )
        if best_key is None or key < best_key:
            best_key = key
            best = {**candidate, "contrast_score": score, "selection_key": list(key)}
    return best


def compact_candidate(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not candidate:
        return {}
    return {
        "contrast_score": candidate.get("contrast_score"),
        "full_public_cost_ops": candidate.get("full_public_cost_ops"),
        "heldout_false_count": candidate.get("heldout_false_count"),
        "heldout_new_recovered_count": candidate.get("heldout_new_recovered_count"),
        "heldout_new_recovered_indices": candidate.get("heldout_new_recovered_indices"),
        "inner_recovered_positive_count": candidate.get("inner_recovered_positive_count"),
        "inner_win_count": candidate.get("inner_win_count"),
        "is_positive": candidate.get("is_positive"),
        "rule_family": candidate.get("rule_family"),
        "rule_name": candidate.get("rule_name"),
        "selection_key": candidate.get("selection_key"),
        "tokens": candidate.get("tokens"),
        "train_true_positive_count": candidate.get("train_true_positive_count"),
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
    seed = summaries.get("seed_only_control") or {}
    seed_rec = int_value(seed.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if name in {"seed_only_control", "oracle_cost_ceiling_upper_bound", "posthoc_all_token_score_min2"}:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P932_LOO_CONTRAST_SELECTS_COST_SAFE_SUPPORT_GAIN"
    if any(
        name.startswith("loo_")
        and int_value(summary.get("heldout_recovered_positive_count")) > seed_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P932_LOO_CONTRAST_GAINS_SUPPORT_BUT_FAILS_GATE"
    return "NEGATIVE_RESULT_P932_LOO_CONTRAST_DOES_NOT_BEAT_SEED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p931_payload = load_json(args.p931_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    public_rows = p923.c19_public_rows(records)
    rows_by_index = {int_value(row.get("index")): row for row in public_rows}
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
    companion_report = p922.full_policy_report("p932_companion_c90_c8_only", records, set(), target_rank)
    companion_cost = int_value(p922.compact_policy(companion_report).get("charged_candidate_cost_ops"))
    fallback = p926.fallback_map()[p929.P928_BEST_STRATEGY]
    contexts: dict[str, dict[str, Any]] = {}
    all_candidates: dict[str, list[dict[str, Any]]] = {}
    controls: dict[str, dict[str, tuple[list[dict[str, Any]], dict[str, Any]]]] = {}

    for window in windows:
        fit_rows = [row for row in p903_blind_rows if p923.source_window(row) != window]
        heldout_rows = [row for row in p903_blind_rows if p923.source_window(row) == window]
        context = p926.fit_context(fit_rows)
        atoms_by_name = context.get("atoms_by_name") or {}
        _source, seed_rule = p926.choose_rule(context, fallback)
        candidates = candidate_records_for_window(
            window,
            context,
            fit_rows,
            heldout_rows,
            public_rows,
            atoms_by_name,
            rows_by_index,
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
        controls[window] = {
            "seed_only_control": ([seed_rule] if seed_rule else [], {"selector": "p928_seed"}),
            "oracle_cost_ceiling_upper_bound": (
                p929.oracle_cost_ceiling_ensemble(
                    context,
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

    strategy_items: dict[str, list[dict[str, Any]]] = {
        "seed_only_control": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    for strategy in CONTRAST_STRATEGIES:
        strategy_items[str(strategy["name"])] = []

    all_flat_candidates = [candidate for candidates in all_candidates.values() for candidate in candidates]
    posthoc_weights = train_token_weights(all_flat_candidates)
    loo_weight_summaries: dict[str, Any] = {}

    for window in windows:
        ctx = contexts[window]
        atoms_by_name = ctx["atoms_by_name"]
        heldout_rows = ctx["heldout_rows"]
        seed_rule = ctx["seed_rule"]
        train_candidates = [
            candidate
            for other_window, candidates in all_candidates.items()
            for candidate in candidates
            if other_window != window
        ]
        loo_weights = train_token_weights(train_candidates)
        loo_weight_summaries[window] = top_token_summary(loo_weights, 6)
        strategy_rules: dict[str, tuple[list[dict[str, Any]], dict[str, Any]]] = dict(controls[window])
        for strategy in CONTRAST_STRATEGIES:
            strategy_name = str(strategy["name"])
            weights = posthoc_weights if strategy.get("posthoc") else loo_weights
            chosen = choose_contrast_candidate(
                all_candidates[window],
                weights,
                int_value(strategy["min_inner_wins"]),
                float(strategy["min_score"]),
                bool(strategy["cost_first"]),
            )
            if chosen:
                rules = [seed_rule, chosen["rule"]]
                metadata = {
                    "selector": "posthoc_token_contrast" if strategy.get("posthoc") else "loo_token_contrast",
                    "chosen_candidate": compact_candidate(chosen),
                    "cost_first": bool(strategy["cost_first"]),
                    "min_inner_wins": int_value(strategy["min_inner_wins"]),
                    "min_score": float(strategy["min_score"]),
                }
            else:
                rules = [seed_rule] if seed_rule else []
                metadata = {
                    "selector": "posthoc_token_contrast" if strategy.get("posthoc") else "loo_token_contrast",
                    "chosen_candidate": {},
                    "cost_first": bool(strategy["cost_first"]),
                    "min_inner_wins": int_value(strategy["min_inner_wins"]),
                    "min_score": float(strategy["min_score"]),
                }
            strategy_rules[strategy_name] = (rules, metadata)
        for name, (rules, metadata) in strategy_rules.items():
            strategy_items[name].append(
                {
                    "fit_row_count": len(ctx["fit_rows"]),
                    "heldout_source_window": window,
                    "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
                    "no_p903_score": p929.score_ensemble(
                        f"p932_{name}_no_p903",
                        rules,
                        p903_blind_rows,
                        atoms_by_name,
                        p903_blind_records,
                        target_rank,
                        p919_cost,
                    ),
                    "p903_score": p929.score_ensemble(
                        f"p932_{name}_p903",
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
            "families": dict(Counter(str(candidate.get("rule_family")) for candidate in candidates)),
            "positive_families": dict(
                Counter(str(candidate.get("rule_family")) for candidate in candidates if candidate.get("is_positive"))
            ),
        }
        for window, candidates in all_candidates.items()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p931_source": str(args.p931_source),
            "script": str(Path(__file__)),
        },
        "candidate_contrast": {
            "candidate_counts": candidate_counts,
            "loo_top_tokens_by_window": loo_weight_summaries,
            "posthoc_top_tokens": top_token_summary(posthoc_weights, 12),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "fresh_window_summary": p925.fresh_window_summary(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous choices remove P903 and current outer heldout support labels.",
            "LEAVE-ONE-CONTRAST: LOO token weights use labels from other heldout windows, not the current outer window.",
            "POSTHOC-CONTROL: posthoc_all_token_score_min2 uses all heldout labels and is diagnostic only.",
            "ORACLE-CONTROL: the oracle upper bound uses current outer heldout labels and is not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p932_oracle_feature_contrast_audit",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "contrast_strategies": list(CONTRAST_STRATEGIES),
            "p903_c19_indices": sorted(p903_indices),
            "p931_claim": p931_payload.get("claim_status"),
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
    parser.add_argument("--p931-source", type=Path, default=P931_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in ["seed_only_control", "loo_token_rank_min2", "loo_token_rank_min3", "loo_token_score_min2", "posthoc_all_token_rank_min2", "oracle_cost_ceiling_upper_bound"]:
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
