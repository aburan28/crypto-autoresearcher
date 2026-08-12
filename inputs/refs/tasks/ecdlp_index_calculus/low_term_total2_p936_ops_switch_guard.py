#!/usr/bin/env python3
"""P936 ops-specific switch guard for the final P935 miss."""

from __future__ import annotations

import argparse
import json
import re
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
import low_term_total2_p933_second_stage_rescue_contrast as p933
import low_term_total2_p934_replacement_switch_contrast as p934


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p936_ops_switch_guard.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p936_ops_switch_guard_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P935_SOURCE = STATE_DIR / "low_term_total2_p935_switch_repeat_guard_probe.json"
SCHEMA = "ecdlp.low_term_total2_p936_ops_switch_guard.v1"
CLASS_A = p923.CLASS_A
VALIDATION_PARTITION = p923.VALIDATION_PARTITION
P935_BASE = "repeat2_switch_rank_min1"
DIAGNOSTIC_EXACT_OPS_RULE = "and__ops_eq_0.72992701"


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


def class_a_positive(row: dict[str, Any]) -> bool:
    return p929.class_a_positive(row)


def rule_name(rule: dict[str, Any] | None) -> str:
    return p929.rule_name(rule)


def is_ops_candidate(candidate: dict[str, Any]) -> bool:
    name = str(candidate.get("rule_name") or rule_name(candidate.get("rule")))
    return name.startswith("and__ops_eq_")


def ops_value(candidate: dict[str, Any]) -> float | None:
    name = str(candidate.get("rule_name") or rule_name(candidate.get("rule")))
    match = re.match(r"and__ops_eq_([0-9.]+)(?:__|$)", name)
    if not match:
        return None
    return float(match.group(1))


def is_singleton_ops(candidate: dict[str, Any]) -> bool:
    rule = candidate.get("rule") or {}
    return is_ops_candidate(candidate) and len(rule.get("predicate_names") or []) == 1


def compact_candidate(candidate: dict[str, Any] | None) -> dict[str, Any]:
    if not candidate:
        return {}
    return {
        "full_public_cost_ops": candidate.get("full_public_cost_ops"),
        "heldout_false_count": candidate.get("heldout_false_count"),
        "heldout_recovered_indices": candidate.get("heldout_recovered_indices"),
        "inner_recovered_positive_count": candidate.get("inner_recovered_positive_count"),
        "inner_win_count": candidate.get("inner_win_count"),
        "rule_family": candidate.get("rule_family"),
        "rule_name": candidate.get("rule_name"),
        "tokens": candidate.get("tokens"),
    }


def summarize(items: list[dict[str, Any]], target_rank: int, p919_cost: int) -> dict[str, Any]:
    return p930.summarize(items, target_rank, p919_cost)


def choose_best_ops(candidates: list[dict[str, Any]], mode: str) -> dict[str, Any] | None:
    ops = [candidate for candidate in candidates if is_ops_candidate(candidate)]
    if not ops:
        return None
    if mode == "cost":
        return min(
            ops,
            key=lambda candidate: (
                int_value(candidate.get("full_public_cost_ops"), 10**12),
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                str(candidate.get("rule_name")),
            ),
        )
    if mode == "inner":
        return max(
            ops,
            key=lambda candidate: (
                int_value(candidate.get("inner_win_count")),
                int_value(candidate.get("inner_recovered_positive_count")),
                -int_value(candidate.get("full_public_cost_ops"), 10**12),
                str(candidate.get("rule_name")),
            ),
        )
    raise ValueError(f"unknown ops selection mode {mode}")


def rule_current_count(candidate: dict[str, Any] | None) -> int:
    return len((candidate or {}).get("rule_heldout_indices") or [])


def choose_ops_window_count_gain(
    candidates: list[dict[str, Any]],
    base: dict[str, Any] | None,
    mode: str,
) -> dict[str, Any] | None:
    base_count = rule_current_count(base)
    base_cost = int_value((base or {}).get("full_public_cost_ops"), 10**12)
    ops = [
        candidate
        for candidate in candidates
        if is_ops_candidate(candidate)
        and rule_current_count(candidate) > base_count
    ]
    if mode.endswith("_not_worse"):
        ops = [candidate for candidate in ops if int_value(candidate.get("full_public_cost_ops"), 10**12) <= base_cost]
    if not ops:
        return None
    if mode.startswith("count_cost"):
        return min(
            ops,
            key=lambda candidate: (
                -rule_current_count(candidate),
                int_value(candidate.get("full_public_cost_ops"), 10**12),
                -int_value(candidate.get("inner_win_count")),
                -int_value(candidate.get("inner_recovered_positive_count")),
                str(candidate.get("rule_name")),
            ),
        )
    if mode.startswith("count_inner"):
        return max(
            ops,
            key=lambda candidate: (
                rule_current_count(candidate),
                int_value(candidate.get("inner_win_count")),
                int_value(candidate.get("inner_recovered_positive_count")),
                -int_value(candidate.get("full_public_cost_ops"), 10**12),
                str(candidate.get("rule_name")),
            ),
        )
    raise ValueError(f"unknown window-count ops mode {mode}")


def choose_high_singleton_ops_window_count_gain(
    candidates: list[dict[str, Any]],
    base: dict[str, Any] | None,
) -> dict[str, Any] | None:
    base_count = rule_current_count(base)
    ops = [
        candidate
        for candidate in candidates
        if is_singleton_ops(candidate)
        and ops_value(candidate) is not None
        and rule_current_count(candidate) > base_count
    ]
    if not ops:
        return None
    return max(
        ops,
        key=lambda candidate: (
            ops_value(candidate) or -1.0,
            rule_current_count(candidate),
            -int_value(candidate.get("full_public_cost_ops"), 10**12),
            int_value(candidate.get("inner_win_count")),
            int_value(candidate.get("inner_recovered_positive_count")),
            str(candidate.get("rule_name")),
        ),
    )


def candidate_by_name(candidates: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for candidate in candidates:
        if str(candidate.get("rule_name")) == name:
            return candidate
    return None


def determine_claim(summaries: dict[str, dict[str, Any]]) -> str:
    base = summaries.get("p935_repeat2_switch_rank_min1_reproduced") or {}
    base_rec = int_value(base.get("heldout_recovered_positive_count"))
    for name, summary in summaries.items():
        if name.endswith("_diagnostic") or name in {
            "p932_loo_token_rank_min2_reproduced",
            "p935_repeat2_switch_rank_min1_reproduced",
            "oracle_cost_ceiling_upper_bound",
        }:
            continue
        if (
            int_value(summary.get("heldout_recovered_positive_count")) > base_rec
            and int_value(summary.get("heldout_false_selected_count")) == 0
            and int_value(summary.get("p903_pass_count")) == int_value(summary.get("source_window_count"))
        ):
            return "P936_OPS_GUARD_CLOSES_P935_GAP"
    if any(
        name.startswith("ops_")
        and not name.endswith("_diagnostic")
        and int_value(summary.get("heldout_recovered_positive_count")) > base_rec
        for name, summary in summaries.items()
    ):
        return "NEGATIVE_RESULT_P936_OPS_GUARD_GAINS_SUPPORT_BUT_FAILS_GATE"
    diagnostic = summaries.get("ops_exact_0_72992701_diagnostic") or {}
    if (
        int_value(diagnostic.get("heldout_recovered_positive_count")) > base_rec
        and int_value(diagnostic.get("heldout_false_selected_count")) == 0
        and int_value(diagnostic.get("p903_pass_count")) == int_value(diagnostic.get("source_window_count"))
    ):
        return "DIAGNOSTIC_ONLY_P936_EXACT_OPS_VALUE_CLOSES_GAP"
    return "NEGATIVE_RESULT_P936_OPS_GUARD_DOES_NOT_BEAT_P935"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p933.install_support_class_cache()
    p914_payload = load_json(args.p914_source)
    p935_payload = load_json(args.p935_source) if args.p935_source.exists() else {}
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
    companion_report = p922.full_policy_report("p936_companion_c90_c8_only", records, set(), target_rank)
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
            "seed_rule": seed_rule,
        }
        all_candidates[window] = candidates

    first_stage_weights_excluding = p933.weight_builder_by_exclusion(all_candidates)
    first_stage_by_window: dict[str, dict[str, Any] | None] = {
        window: p933.choose_first_stage_candidate(all_candidates[window], first_stage_weights_excluding({window}))
        for window in windows
    }

    p935_items = ((p935_payload.get("summary") or {}).get("second_holdout") or {}).get(P935_BASE) or []
    p935_base_rule_by_window = {
        str(item.get("heldout_source_window")): str((item.get("rule_names") or ["", ""])[1] if len(item.get("rule_names") or []) > 1 else "")
        for item in p935_items
    }

    best_ops_cost_by_window = {window: choose_best_ops(all_candidates[window], "cost") for window in windows}
    best_ops_inner_by_window = {window: choose_best_ops(all_candidates[window], "inner") for window in windows}
    cost_rule_counts = Counter(str(candidate.get("rule_name")) for candidate in best_ops_cost_by_window.values() if candidate)
    inner_rule_counts = Counter(str(candidate.get("rule_name")) for candidate in best_ops_inner_by_window.values() if candidate)

    strategy_items: dict[str, list[dict[str, Any]]] = {
        "p932_loo_token_rank_min2_reproduced": [],
        "p935_repeat2_switch_rank_min1_reproduced": [],
        "ops_best_cost": [],
        "ops_best_inner": [],
        "ops_best_cost_repeat2": [],
        "ops_best_inner_repeat2": [],
        "ops_best_cost_not_worse": [],
        "ops_best_cost_repeat2_not_worse": [],
        "ops_window_count_gain_cost": [],
        "ops_window_count_gain_inner": [],
        "ops_window_count_gain_cost_not_worse": [],
        "ops_high_singleton_window_count_gain": [],
        "ops_exact_0_72992701_window_count_gain_diagnostic": [],
        "ops_exact_0_72992701_diagnostic": [],
        "oracle_cost_ceiling_upper_bound": [],
    }
    decisions: dict[str, list[dict[str, Any]]] = {name: [] for name in strategy_items}

    def make_item(
        name: str,
        window: str,
        rules: list[dict[str, Any]],
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        ctx = contexts[window]
        atoms_by_name = ctx["atoms_by_name"]
        heldout_rows = ctx["heldout_rows"]
        return {
            "fit_row_count": len(ctx["fit_rows"]),
            "heldout_source_window": window,
            "heldout_support": p929.support_report(rules, heldout_rows, atoms_by_name),
            "no_p903_score": p929.score_ensemble(
                f"p936_{name}_no_p903",
                rules,
                p903_blind_rows,
                atoms_by_name,
                p903_blind_records,
                target_rank,
                p919_cost,
            ),
            "p903_score": p929.score_ensemble(
                f"p936_{name}_p903",
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

    for window in windows:
        ctx = contexts[window]
        seed_rule = ctx["seed_rule"]
        first = first_stage_by_window[window]
        first_candidate_by_name = {str(candidate.get("rule_name")): candidate for candidate in all_candidates[window]}
        p935_rule_name = p935_base_rule_by_window.get(window) or rule_name((first or {}).get("rule"))
        p935_candidate = first_candidate_by_name.get(p935_rule_name) or first
        p932_rules = [seed_rule] + ([first["rule"]] if first else [])
        p935_rules = [seed_rule] + ([p935_candidate["rule"]] if p935_candidate else [])
        strategy_items["p932_loo_token_rank_min2_reproduced"].append(
            make_item("p932_loo_token_rank_min2_reproduced", window, p932_rules, {"selector": "p932_loo_token_rank_min2"})
        )
        strategy_items["p935_repeat2_switch_rank_min1_reproduced"].append(
            make_item(
                "p935_repeat2_switch_rank_min1_reproduced",
                window,
                p935_rules,
                {"selector": "p935_repeat2_switch_rank_min1", "base_rule_name": p935_rule_name},
            )
        )
        exact_ops = candidate_by_name(all_candidates[window], DIAGNOSTIC_EXACT_OPS_RULE)
        selections = {
            "ops_best_cost": best_ops_cost_by_window[window],
            "ops_best_inner": best_ops_inner_by_window[window],
            "ops_best_cost_repeat2": (
                best_ops_cost_by_window[window]
                if best_ops_cost_by_window[window]
                and cost_rule_counts[str(best_ops_cost_by_window[window].get("rule_name"))] >= 2
                else None
            ),
            "ops_best_inner_repeat2": (
                best_ops_inner_by_window[window]
                if best_ops_inner_by_window[window]
                and inner_rule_counts[str(best_ops_inner_by_window[window].get("rule_name"))] >= 2
                else None
            ),
            "ops_best_cost_not_worse": (
                best_ops_cost_by_window[window]
                if best_ops_cost_by_window[window]
                and int_value(best_ops_cost_by_window[window].get("full_public_cost_ops")) <= int_value(p935_candidate.get("full_public_cost_ops") if p935_candidate else 10**12)
                else None
            ),
            "ops_best_cost_repeat2_not_worse": (
                best_ops_cost_by_window[window]
                if best_ops_cost_by_window[window]
                and cost_rule_counts[str(best_ops_cost_by_window[window].get("rule_name"))] >= 2
                and int_value(best_ops_cost_by_window[window].get("full_public_cost_ops")) <= int_value(p935_candidate.get("full_public_cost_ops") if p935_candidate else 10**12)
                else None
            ),
            "ops_window_count_gain_cost": choose_ops_window_count_gain(all_candidates[window], p935_candidate, "count_cost"),
            "ops_window_count_gain_inner": choose_ops_window_count_gain(all_candidates[window], p935_candidate, "count_inner"),
            "ops_window_count_gain_cost_not_worse": choose_ops_window_count_gain(all_candidates[window], p935_candidate, "count_cost_not_worse"),
            "ops_high_singleton_window_count_gain": choose_high_singleton_ops_window_count_gain(all_candidates[window], p935_candidate),
            "ops_exact_0_72992701_window_count_gain_diagnostic": (
                exact_ops
                if exact_ops and rule_current_count(exact_ops) > rule_current_count(p935_candidate)
                else None
            ),
            "ops_exact_0_72992701_diagnostic": exact_ops,
        }
        for name, selected in selections.items():
            candidate = selected or p935_candidate
            rules = [seed_rule] + ([candidate["rule"]] if candidate else [])
            metadata = {
                "base_rule_name": p935_rule_name,
                "diagnostic_oracle_derived": name.endswith("_diagnostic"),
                "ops_cost_repeat_count": cost_rule_counts.get(str((best_ops_cost_by_window[window] or {}).get("rule_name")), 0),
                "ops_inner_repeat_count": inner_rule_counts.get(str((best_ops_inner_by_window[window] or {}).get("rule_name")), 0),
                "ops_selected_current_count": rule_current_count(selected),
                "ops_selected_value": ops_value(selected) if selected else None,
                "p935_base_current_count": rule_current_count(p935_candidate),
                "selected_ops_candidate": compact_candidate(selected),
                "selector": name,
            }
            item = make_item(name, window, rules, metadata)
            strategy_items[name].append(item)
            support = item.get("heldout_support") or {}
            decisions[name].append(
                {
                    "base_rule_name": p935_rule_name,
                    "heldout_false_indices": support.get("false_selected_indices"),
                    "heldout_recovered_positive_indices": support.get("recovered_positive_indices"),
                    "heldout_source_window": window,
                    "selected_rule_name": rule_name(candidate.get("rule")) if candidate else "",
                    "selected_source": "ops" if selected else "p935_base",
                }
            )
        oracle_rules = p929.oracle_cost_ceiling_ensemble(
            ctx["context"],
            ctx["heldout_rows"],
            public_rows,
            ctx["atoms_by_name"],
            rows_by_index,
            companion_cost,
            p919_cost,
            seed_rule,
        )
        strategy_items["oracle_cost_ceiling_upper_bound"].append(
            make_item("oracle_cost_ceiling_upper_bound", window, oracle_rules, {"selector": "heldout_label_oracle"})
        )

    summaries = {name: summarize(items, target_rank, p919_cost) for name, items in strategy_items.items()}
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p935_source": str(args.p935_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(summaries),
        "created_at": now_iso(),
        "decisions": decisions,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this scores archived rows; no fresh 1160+ compatible row window is claimed.",
            "P903-BLIND-FIT: autonomous choices remove P903 and current outer heldout support labels.",
            "OPS-GUARD: autonomous ops strategies use public ops-rule cost, inner-CV, and repeat counts only.",
            "DIAGNOSTIC-CONTROL: ops_exact_0_72992701_diagnostic is oracle-derived and not autonomous.",
            "SUPPORT-NOT-COST: a support gain is not promoted unless exact P903-restored policy remains below P919.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is an index-calculus selector audit, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p936_ops_switch_guard",
        "parameters": {
            "class_a": p922.SUPPORT_CLASSES[CLASS_A],
            "companion_c90_c8_cost_ops": companion_cost,
            "diagnostic_exact_ops_rule": DIAGNOSTIC_EXACT_OPS_RULE,
            "p903_c19_indices": sorted(p903_indices),
            "p935_claim": p935_payload.get("claim_status"),
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
    parser.add_argument("--p935-source", type=Path, default=P935_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summaries = (payload.get("summary") or {}).get("strategy_summaries") or {}
    parts = []
    for name in [
        "p935_repeat2_switch_rank_min1_reproduced",
        "ops_best_cost",
        "ops_best_cost_repeat2",
        "ops_best_cost_repeat2_not_worse",
        "ops_window_count_gain_cost",
        "ops_window_count_gain_inner",
        "ops_window_count_gain_cost_not_worse",
        "ops_high_singleton_window_count_gain",
        "ops_exact_0_72992701_window_count_gain_diagnostic",
        "ops_exact_0_72992701_diagnostic",
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
        "claim={claim} {parts} out={out}".format(
            claim=payload.get("claim_status"),
            parts=" | ".join(parts),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
