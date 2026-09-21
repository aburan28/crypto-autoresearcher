#!/usr/bin/env python3
"""P720 temporal validation of P719 shared signed-pair-core source charges."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713
import low_term_total2_p716_rel2_source_generation_enrichment as p716
import low_term_total2_p719_shared_signed_pair_core_scanner_audit as p719
import low_term_total2_p709_source_replay_no_archive_oracle as p709


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P719 = STATE_DIR / "low_term_total2_p719_shared_signed_pair_core_scanner_audit_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p720_shared_core_temporal_generalization_audit_probe.json"


@dataclass(frozen=True)
class SharedPolicyBudget:
    policy: p716.SourcePolicy
    budget: int

    @property
    def name(self) -> str:
        return f"{self.policy.name}:budget{self.budget}"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p716.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p716.float_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_floats(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def parse_ints(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise ValueError("at least one attempt budget is required")
    return tuple(sorted(set(values)))


def threshold_token(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def make_shared_policy_budgets(thresholds: tuple[float, ...], budgets: tuple[int, ...]) -> list[SharedPolicyBudget]:
    policies = [p716.SourcePolicy("two_by_two_any", "two_by_two_any")]
    for threshold in thresholds:
        policies.append(
            p716.SourcePolicy(
                f"two_by_two_any_cost_le_{threshold_token(threshold)}",
                "two_by_two_any",
                threshold,
            )
        )
    return [SharedPolicyBudget(policy, budget) for policy in policies for budget in budgets]


def combo_by_name(combos: list[SharedPolicyBudget], name: str) -> SharedPolicyBudget:
    for combo in combos:
        if combo.name == name:
            return combo
    raise KeyError(name)


def eval_sort_key(report: dict[str, Any]) -> tuple[Any, ...]:
    return (
        not bool(report.get("beats_rho_with_fallback")),
        float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
        -int_value(report.get("hit_count")),
        int_value(report.get("attempted_candidate_count")),
        int_value(report.get("attempt_budget")),
        str(report.get("policy_budget")),
    )


def choose_best(reports: list[dict[str, Any]]) -> dict[str, Any]:
    return sorted(reports, key=eval_sort_key)[0] if reports else {}


def compact_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_budget": report.get("attempt_budget"),
        "attempted_candidate_count": report.get("attempted_candidate_count"),
        "attempted_source_charge_over_rho": report.get("attempted_source_charge_over_rho"),
        "beats_rho_with_fallback": report.get("beats_rho_with_fallback"),
        "fallback_charge_over_rho": report.get("fallback_charge_over_rho"),
        "factor_charge_over_rho": report.get("factor_charge_over_rho"),
        "hit_count": report.get("hit_count"),
        "policy_budget": report.get("policy_budget"),
        "policy_threshold": report.get("policy_threshold"),
        "precheck_window_count": report.get("precheck_window_count"),
        "source_replay_total_with_fallback_over_rho": report.get("source_replay_total_with_fallback_over_rho"),
        "vs_independent_rho_with_fallback_over_rho": report.get("vs_independent_rho_with_fallback_over_rho"),
        "window_count": report.get("window_count"),
    }


def shared_replay_for_row(row: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any] | None:
    key = str(row["key"])
    cache = metadata["shared_replay_cache"]
    errors = metadata["shared_replay_errors"]
    if key in cache:
        return cache[key]
    if key in errors:
        return None
    try:
        source = metadata["source_cache"][str(row["source"])]
        verifier, contexts, product_factor, max_relations = p709.direct_source.timing_probe.selected_contexts_from_source_case(
            source,
            row["source_case"],
        )
        direct_rows, direct_ops, rho, row_profiles = p709.direct_source.timing_probe.direct_witness_rows(
            verifier,
            contexts,
        )
        built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
        direct_union = p709.direct_source.direct_witness_probe.union_derive(
            verifier,
            direct_rows,
            built_by_row,
            "_scan",
        )
        context_records = [
            {
                "context": context,
                "context_index": index,
                "core_fingerprint": p719.p718.signed_pair_core_fingerprint(context["built"]),
                "profile": profile,
            }
            for index, (context, profile) in enumerate(zip(contexts, row_profiles))
        ]
        attempt = {
            "attempt_index": len(cache),
            "candidate": row,
            "contexts": context_records,
            "direct_ops": direct_ops,
            "direct_union": direct_union,
            "max_relations": max_relations,
            "product_factor": product_factor,
            "rho": rho,
            "source": str(row["source"]),
            "window_start": int_value((row.get("source_case") or {}).get("transfer_index")),
        }
        shared = p719.attempt_shared_scan(attempt)
        replay = {
            "cover_mismatch_count": int_value(shared.get("cover_mismatch_count")),
            "direct_hit": bool(shared.get("direct_hit")),
            "direct_ops": int_value(shared.get("direct_ops")),
            "direct_ops_over_rho": ratio(int_value(shared.get("direct_ops")), int_value(shared.get("rho"))),
            "event_mismatch_count": int_value(shared.get("event_mismatch_count")),
            "rank": int_value(shared.get("rank")),
            "rho": int_value(shared.get("rho")),
            "shared_hit": bool(shared.get("shared_hit")),
            "shared_ops": int_value(shared.get("shared_ops")),
            "shared_ops_over_rho": ratio(int_value(shared.get("shared_ops")), int_value(shared.get("rho"))),
            "signed_pair_core_group_count": int_value(shared.get("group_count")),
            "union_matches_all_fields": bool(shared.get("union_matches_all_fields")),
        }
        cache[key] = replay
        return replay
    except Exception as exc:  # noqa: BLE001 - verifier failures are experiment evidence.
        errors[key] = f"{type(exc).__name__}: {exc}"
        return None


def evaluate_policy_budget(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combo: SharedPolicyBudget,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    mismatch_count = 0
    precheck_window_count = 0
    accepted_candidate_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    for report in reports:
        accepted = [
            row
            for row in report["candidates"]
            if p716.policy_accepts(combo.policy, row)
        ]
        accepted.sort(key=p716.row_sort_key)
        accepted_candidate_count += len(accepted)
        if accepted:
            precheck_window_count += 1
        hit = None
        charge = 0.0
        attempted = 0
        for row in accepted[: combo.budget]:
            attempted += 1
            replay = shared_replay_for_row(row, metadata)
            if replay is None:
                charge += float_value(row.get("direct_ops_over_rho"))
                continue
            charge += float_value(replay.get("shared_ops_over_rho"))
            if not replay.get("union_matches_all_fields"):
                mismatch_count += 1
            if replay.get("shared_hit"):
                hit = (row, replay)
                break
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(hit_samples) < sample_limit:
                hit_samples.append(
                    {
                        "row": p716.sample_row(hit[0], None),
                        "shared_replay": hit[1],
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
        else:
            fallback_charge += 1.0
            if len(miss_samples) < sample_limit:
                miss_samples.append(
                    {
                        "accepted_candidate_count": len(accepted),
                        "first_candidates": [p716.sample_row(row, None) for row in accepted[: min(3, len(accepted))]],
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
    window_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "accepted_candidate_count": accepted_candidate_count,
        "attempt_budget": combo.budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "factor_charge_over_rho": round(factor_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "mismatch_count": mismatch_count,
        "miss_samples": miss_samples,
        "policy": combo.policy.name,
        "policy_budget": combo.name,
        "policy_group": combo.policy.group,
        "policy_threshold": combo.policy.threshold,
        "precheck_window_count": precheck_window_count,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_per_window_over_rho": round(total / window_count, 8) if window_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": window_count,
        "window_count": window_count,
    }


def evaluate_all(
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[SharedPolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> list[dict[str, Any]]:
    return [
        evaluate_policy_budget(reports, metadata, combo, factor_charge, sample_limit)
        for combo in combos
    ]


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    metadata: dict[str, Any],
    combos: list[SharedPolicyBudget],
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    train = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    train_marginal = evaluate_all(train, metadata, combos, 0.0, sample_limit)
    selected_train = choose_best(train_marginal)
    selected_combo = combo_by_name(combos, str(selected_train.get("policy_budget")))
    selected_holdout_marginal = evaluate_policy_budget(holdout, metadata, selected_combo, 0.0, sample_limit)
    selected_holdout_new = evaluate_policy_budget(holdout, metadata, selected_combo, factor_charge, sample_limit)
    oracle_marginal = choose_best(evaluate_all(holdout, metadata, combos, 0.0, sample_limit))
    oracle_new = choose_best(evaluate_all(holdout, metadata, combos, factor_charge, sample_limit))
    fixed_combo = combo_by_name(combos, "two_by_two_any_cost_le_1p0:budget1")
    return {
        **split,
        "fixed_two_by_two_1p0_holdout_marginal_existing_bank": evaluate_policy_budget(
            holdout, metadata, fixed_combo, 0.0, sample_limit
        ),
        "fixed_two_by_two_1p0_holdout_new_bank": evaluate_policy_budget(
            holdout, metadata, fixed_combo, factor_charge, sample_limit
        ),
        "heldout_oracle_best_marginal_existing_bank": oracle_marginal,
        "heldout_oracle_best_new_bank": oracle_new,
        "selected_holdout_marginal_existing_bank": selected_holdout_marginal,
        "selected_holdout_new_bank": selected_holdout_new,
        "selected_policy_budget": selected_combo.name,
        "selected_train_marginal_existing_bank": selected_train,
        "top_train_marginal_existing_bank": sorted(train_marginal, key=eval_sort_key)[:8],
        "train_window_count": len(train),
        "window_ranges": {
            "holdout": [[report["window_start"], report["window_end"]] for report in holdout[:3]],
            "holdout_last": None if not holdout else [holdout[-1]["window_start"], holdout[-1]["window_end"]],
            "train": [[report["window_start"], report["window_end"]] for report in train[:3]],
            "train_last": None if not train else [train[-1]["window_start"], train[-1]["window_end"]],
        },
    }


def summarize_splits(split_reports: list[dict[str, Any]]) -> dict[str, Any]:
    keys = (
        "selected_holdout_marginal_existing_bank",
        "selected_holdout_new_bank",
        "heldout_oracle_best_marginal_existing_bank",
        "heldout_oracle_best_new_bank",
        "fixed_two_by_two_1p0_holdout_marginal_existing_bank",
        "fixed_two_by_two_1p0_holdout_new_bank",
    )
    summary: dict[str, Any] = {"split_count": len(split_reports)}
    for key in keys:
        summary[f"{key}_below_rho_splits"] = sum(
            1 for report in split_reports if (report.get(key) or {}).get("beats_rho_with_fallback")
        )
    return summary


def best_by_budget(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for budget in sorted({int_value(report.get("attempt_budget")) for report in reports}):
        subset = [report for report in reports if int_value(report.get("attempt_budget")) == budget]
        if subset:
            rows.append(choose_best(subset))
    return rows


def determine_claim(summary: dict[str, Any], full_population: dict[str, Any]) -> str:
    split_count = int_value(summary.get("split_count"))
    selected_new = int_value(summary.get("selected_holdout_new_bank_below_rho_splits"))
    selected_marginal = int_value(summary.get("selected_holdout_marginal_existing_bank_below_rho_splits"))
    oracle_new = int_value(summary.get("heldout_oracle_best_new_bank_below_rho_splits"))
    fixed_new = int_value(summary.get("fixed_two_by_two_1p0_holdout_new_bank_below_rho_splits"))
    if split_count and selected_new == split_count:
        return "P720_SHARED_CORE_TRAIN_SELECTED_NEW_BANK_BEATS_ALL_HELDOUT_SPLITS"
    if selected_new:
        return "P720_SHARED_CORE_TRAIN_SELECTED_HAS_PARTIAL_NEW_BANK_HELDOUT_SIGNAL"
    if selected_marginal:
        return "P720_SHARED_CORE_TRAIN_SELECTED_MARGINAL_ONLY_HELDOUT_SIGNAL"
    if fixed_new or oracle_new:
        return "P720_SHARED_CORE_HELDOUT_SIGNAL_REQUIRES_FIXED_OR_ORACLE_POLICY"
    if (full_population.get("fixed_two_by_two_1p0_new_bank") or {}).get("beats_rho_with_fallback"):
        return "P720_SHARED_CORE_FULL_POPULATION_BELOW_RHO_BUT_HELDOUT_UNSTABLE"
    return "NEGATIVE_RESULT_P720_SHARED_CORE_TEMPORAL_GENERALIZATION_FAILS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p719_payload = load_json(Path(args.p719))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    thresholds = parse_floats(args.thresholds)
    budgets = parse_ints(args.attempt_budgets)
    reports, metadata = p716.build_window_reports(args)
    metadata["shared_replay_cache"] = {}
    metadata["shared_replay_errors"] = {}
    combos = make_shared_policy_budgets(thresholds, budgets)
    splits = p713.prefix_splits(reports) + p713.rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )
    split_reports = [
        evaluate_split(split, reports, metadata, combos, factor_charge, int_value(args.sample_limit))
        for split in splits
    ]
    full_marginal = evaluate_all(reports, metadata, combos, 0.0, int_value(args.sample_limit))
    full_new = evaluate_all(reports, metadata, combos, factor_charge, int_value(args.sample_limit))
    fixed_combo = combo_by_name(combos, "two_by_two_any_cost_le_1p0:budget1")
    full_population = {
        "best_marginal_existing_bank": choose_best(full_marginal),
        "best_marginal_existing_bank_by_budget": best_by_budget(full_marginal),
        "best_new_bank": choose_best(full_new),
        "best_new_bank_by_budget": best_by_budget(full_new),
        "fixed_two_by_two_1p0_marginal_existing_bank": evaluate_policy_budget(
            reports, metadata, fixed_combo, 0.0, int_value(args.sample_limit)
        ),
        "fixed_two_by_two_1p0_new_bank": evaluate_policy_budget(
            reports, metadata, fixed_combo, factor_charge, int_value(args.sample_limit)
        ),
        "top_marginal_existing_bank": sorted(full_marginal, key=eval_sort_key)[:10],
        "top_new_bank": sorted(full_new, key=eval_sort_key)[:10],
    }
    split_summary = summarize_splits(split_reports)
    mismatch_count = sum(int_value(row.get("mismatch_count")) for row in full_marginal)
    payload = {
        "artifacts": {
            "p709": str(Path(args.p709)),
            "p716": str(p716.DEFAULT_OUT),
            "p719": str(Path(args.p719)),
        },
        "created_at": now_iso(),
        "full_population": full_population,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source-generator stress rows outside the P709 source map, not live fresh harvesting.",
            "REPLAY-BACKED: charged candidates use the P719 shared-core replay check.",
            "NO LABEL-ONLY HELDOUT CLAIM: train-selected policies are chosen on training windows before heldout scoring.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "method": "p720_shared_core_temporal_generalization_audit",
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "rolling_holdout_size": int_value(args.rolling_holdout_size),
            "rolling_train_size": int_value(args.rolling_train_size),
            "source_pattern": args.source_pattern,
            "target": args.target,
            "thresholds": thresholds,
        },
        "replay_metadata": {
            "candidate_count": sum(len(report["candidates"]) for report in reports),
            "candidate_window_count": sum(1 for report in reports if report["candidates"]),
            "policy_budget_count": len(combos),
            "shared_replay_cache_count": len(metadata["shared_replay_cache"]),
            "shared_replay_error_count": len(metadata["shared_replay_errors"]),
            "shared_replay_errors": metadata["shared_replay_errors"],
            "source_window_count": len(reports),
            "total_mismatch_count_across_full_marginal_evals": mismatch_count,
        },
        "schema": "ecdlp.low_term_total2_p720_shared_core_temporal_generalization_audit.v1",
        "split_reports": split_reports,
        "summary": {
            **split_summary,
            "best_full_marginal_policy_budget": (full_population["best_marginal_existing_bank"] or {}).get("policy_budget"),
            "best_full_marginal_total_over_rho": (full_population["best_marginal_existing_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "best_full_new_bank_policy_budget": (full_population["best_new_bank"] or {}).get("policy_budget"),
            "best_full_new_bank_total_over_rho": (full_population["best_new_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "fixed_full_new_bank_total_over_rho": (full_population["fixed_two_by_two_1p0_new_bank"] or {}).get("source_replay_total_with_fallback_over_rho"),
            "p719_claim_status": p719_payload.get("claim_status"),
            "p719_shared_new_bank_total_over_rho": (p719_payload.get("summary") or {}).get("shared_new_bank_total_over_rho"),
            "shared_replay_error_count": len(metadata["shared_replay_errors"]),
            "total_mismatch_count": mismatch_count,
        },
    }
    payload["claim_status"] = determine_claim(payload["summary"], full_population)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2,4")
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p719", default=str(DEFAULT_P719))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--source-pattern", default=p716.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.544,0.568,0.616,1.0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"split_compact": [
        {
            "split": report.get("split"),
            "selected_policy_budget": report.get("selected_policy_budget"),
            "selected_holdout_marginal": compact_report(report["selected_holdout_marginal_existing_bank"]),
            "selected_holdout_new": compact_report(report["selected_holdout_new_bank"]),
            "oracle_new": compact_report(report["heldout_oracle_best_new_bank"]),
            "fixed_new": compact_report(report["fixed_two_by_two_1p0_holdout_new_bank"]),
        }
        for report in payload["split_reports"]
    ]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
