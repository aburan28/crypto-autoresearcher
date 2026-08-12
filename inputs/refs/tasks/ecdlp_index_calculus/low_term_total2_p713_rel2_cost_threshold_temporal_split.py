#!/usr/bin/env python3
"""P713 temporal split validation for the P712 low-cost rel2 signal."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p711_rel2_source_neighborhood_replay as p711
import low_term_total2_p712_rel2_fresh_window_validation as p712


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p713_rel2_cost_threshold_temporal_split_probe.json"
THRESHOLDS = (0.52, 0.544, 0.55, 0.568, 0.616)


@dataclass(frozen=True)
class Policy:
    name: str
    threshold: float | None = None
    row_pairs: tuple[str, ...] = ()


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p711.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p711.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def threshold_token(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def parse_thresholds(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def policy_accepts(policy: Policy, row: dict[str, Any]) -> bool:
    if int_value(row.get("relation_count")) != 2:
        return False
    if policy.threshold is not None and float_value(row.get("direct_ops_over_rho"), 999999.0) > policy.threshold:
        return False
    if policy.row_pairs and str(row.get("row_pair")) not in set(policy.row_pairs):
        return False
    return True


def sample_replay(replay: dict[str, Any] | None) -> dict[str, Any] | None:
    if replay is None:
        return None
    return p711.sample_replay(replay)


def build_window_reports(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    replay_cache: dict[str, dict[str, Any]] = {}
    replay_errors: dict[str, str] = {}
    reports: list[dict[str, Any]] = []
    for source_path in p712.source_paths(args):
        source = load_json(source_path)
        parsed = p712.window_range(source_path)
        if parsed is None:
            continue
        rows = [
            row
            for row in p711.candidate_rows(source, source_path, args.target)
            if int_value(row.get("relation_count")) == 2
        ]
        for row in rows:
            key = str(row["key"])
            if key in replay_cache or key in replay_errors:
                continue
            try:
                replay_cache[key] = p711.replay_candidate(source, source_path, row)
            except Exception as exc:  # noqa: BLE001 - verifier failures are experiment evidence.
                replay_errors[key] = f"{type(exc).__name__}: {exc}"
        reports.append(
            {
                "rel2_candidate_keys": [str(row["key"]) for row in rows],
                "rel2_candidates": rows,
                "source": str(source_path),
                "window_end": parsed[1],
                "window_start": parsed[0],
            }
        )
    reports.sort(key=lambda report: (int_value(report["window_start"]), int_value(report["window_end"]), report["source"]))
    return reports, {
        "replay_cache": replay_cache,
        "replay_error_count": len(replay_errors),
        "replay_errors": replay_errors,
    }


def first_hit(
    rows: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    policy: Policy,
    budget: int,
) -> tuple[dict[str, Any] | None, float, int]:
    selected = [row for row in rows if policy_accepts(policy, row)]
    charge = 0.0
    attempted = 0
    for row in selected[:budget]:
        attempted += 1
        charge += float_value(row.get("direct_ops_over_rho"))
        replay = replay_cache.get(str(row["key"]))
        if replay and replay.get("replay_public_key_verified"):
            return replay, charge, attempted
    return None, charge, attempted


def evaluate_policy(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    policy: Policy,
    factor_charge: float,
    budget: int,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    candidate_window_count = 0
    fallback_charge = 0.0
    hit_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    for report in reports:
        selected = [row for row in report["rel2_candidates"] if policy_accepts(policy, row)]
        if selected:
            candidate_window_count += 1
        hit, charge, attempted = first_hit(report["rel2_candidates"], replay_cache, policy, budget)
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(hit_samples) < sample_limit:
                hit_samples.append(
                    {
                        "replay": sample_replay(hit),
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
                        "candidate_count": len(selected),
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
    window_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "attempt_budget": budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "candidate_window_count": candidate_window_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "miss_samples": miss_samples,
        "policy": policy.name,
        "policy_row_pairs": list(policy.row_pairs),
        "policy_threshold": policy.threshold,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_per_window_over_rho": round(total / window_count, 8) if window_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": window_count,
        "window_count": window_count,
    }


def fixed_policies(thresholds: tuple[float, ...]) -> list[Policy]:
    policies = [Policy("strict_rel2")]
    for threshold in thresholds:
        policies.append(Policy(f"cost_le_{threshold_token(threshold)}", threshold=threshold))
    return policies


def calibration_hit_pairs(
    train_reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
) -> list[str]:
    pairs: set[str] = set()
    for report in train_reports:
        for row in report["rel2_candidates"]:
            replay = replay_cache.get(str(row["key"]))
            if replay and replay.get("replay_public_key_verified"):
                pairs.add(str(row.get("row_pair")))
    return sorted(pairs)


def split_policies(
    train_reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    thresholds: tuple[float, ...],
) -> list[Policy]:
    policies = fixed_policies(thresholds)
    pairs = calibration_hit_pairs(train_reports, replay_cache)
    if pairs:
        policies.append(Policy("calibration_hit_pair_union", row_pairs=tuple(pairs)))
        for threshold in thresholds:
            policies.append(
                Policy(
                    f"calibration_hit_pair_union_cost_le_{threshold_token(threshold)}",
                    threshold=threshold,
                    row_pairs=tuple(pairs),
                )
            )
    for pair in pairs:
        policies.append(Policy(f"row_pair_{pair}", row_pairs=(pair,)))
        for threshold in thresholds:
            policies.append(Policy(f"row_pair_{pair}_cost_le_{threshold_token(threshold)}", threshold=threshold, row_pairs=(pair,)))
    return policies


def choose_policy(train_reports: list[dict[str, Any]], replay_cache: dict[str, dict[str, Any]], policies: list[Policy], args: argparse.Namespace) -> tuple[Policy, dict[str, Any], list[dict[str, Any]]]:
    train_evaluations = [
        evaluate_policy(
            train_reports,
            replay_cache,
            policy,
            float_value(args.factor_charge),
            int_value(args.attempt_budget),
            int_value(args.sample_limit),
        )
        for policy in policies
    ]
    train_evaluations.sort(
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
            -int_value(report.get("hit_count")),
            int_value(report.get("attempted_candidate_count")),
            str(report.get("policy")),
        )
    )
    best_report = train_evaluations[0]
    best_policy = next(policy for policy in policies if policy.name == best_report["policy"])
    return best_policy, best_report, train_evaluations


def prefix_splits(reports: list[dict[str, Any]]) -> list[dict[str, Any]]:
    n = len(reports)
    return [
        {
            "holdout_end_index": n,
            "holdout_start_index": int(n * 0.50),
            "split": "prefix_0p50",
            "train_end_index": int(n * 0.50),
            "train_start_index": 0,
        },
        {
            "holdout_end_index": n,
            "holdout_start_index": int(n * 0.67),
            "split": "prefix_0p67",
            "train_end_index": int(n * 0.67),
            "train_start_index": 0,
        },
    ]


def rolling_splits(reports: list[dict[str, Any]], train_size: int, holdout_size: int) -> list[dict[str, Any]]:
    n = len(reports)
    starts = [0, holdout_size]
    final_start = max(0, n - train_size - holdout_size)
    starts.append(final_start)
    splits = []
    for start in sorted(set(starts)):
        train_end = start + train_size
        holdout_end = train_end + holdout_size
        if holdout_end > n or start < 0:
            continue
        splits.append(
            {
                "holdout_end_index": holdout_end,
                "holdout_start_index": train_end,
                "split": f"rolling_train{train_size}_holdout{holdout_size}_start{start}",
                "train_end_index": train_end,
                "train_start_index": start,
            }
        )
    return splits


def evaluate_split(
    split: dict[str, Any],
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    thresholds: tuple[float, ...],
    args: argparse.Namespace,
) -> dict[str, Any]:
    train_reports = reports[int_value(split["train_start_index"]): int_value(split["train_end_index"])]
    holdout_reports = reports[int_value(split["holdout_start_index"]): int_value(split["holdout_end_index"])]
    policies = split_policies(train_reports, replay_cache, thresholds)
    selected_policy, selected_train, train_evaluations = choose_policy(train_reports, replay_cache, policies, args)
    selected_holdout = evaluate_policy(
        holdout_reports,
        replay_cache,
        selected_policy,
        float_value(args.factor_charge),
        int_value(args.attempt_budget),
        int_value(args.sample_limit),
    )
    fixed_055 = Policy("fixed_cost_le_0p55", threshold=0.55)
    fixed_055_holdout = evaluate_policy(
        holdout_reports,
        replay_cache,
        fixed_055,
        float_value(args.factor_charge),
        int_value(args.attempt_budget),
        int_value(args.sample_limit),
    )
    holdout_oracle_evaluations = [
        evaluate_policy(
            holdout_reports,
            replay_cache,
            policy,
            float_value(args.factor_charge),
            int_value(args.attempt_budget),
            int_value(args.sample_limit),
        )
        for policy in policies
    ]
    holdout_oracle_evaluations.sort(
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
            -int_value(report.get("hit_count")),
            int_value(report.get("attempted_candidate_count")),
            str(report.get("policy")),
        )
    )
    return {
        **split,
        "candidate_policy_count": len(policies),
        "calibration_hit_pairs": calibration_hit_pairs(train_reports, replay_cache),
        "fixed_0p55_holdout": fixed_055_holdout,
        "heldout_oracle_best": holdout_oracle_evaluations[0],
        "selected_holdout": selected_holdout,
        "selected_policy": selected_policy.name,
        "selected_train": selected_train,
        "top_train_policies": train_evaluations[:8],
        "train_window_count": len(train_reports),
        "window_ranges": {
            "holdout": [
                [report["window_start"], report["window_end"]]
                for report in holdout_reports[:3]
            ],
            "holdout_last": None if not holdout_reports else [holdout_reports[-1]["window_start"], holdout_reports[-1]["window_end"]],
            "train": [
                [report["window_start"], report["window_end"]]
                for report in train_reports[:3]
            ],
            "train_last": None if not train_reports else [train_reports[-1]["window_start"], train_reports[-1]["window_end"]],
        },
    }


def determine_claim(split_reports: list[dict[str, Any]]) -> str:
    selected = [report["selected_holdout"] for report in split_reports]
    fixed = [report["fixed_0p55_holdout"] for report in split_reports]
    if selected and all(report.get("beats_rho_with_fallback") for report in selected):
        return "P713_CALIBRATION_SELECTED_REL2_COST_RULES_BEAT_RHO_ON_ALL_HELDOUT_SPLITS"
    if any(report.get("beats_rho_with_fallback") for report in selected):
        return "P713_CALIBRATION_SELECTED_REL2_COST_RULES_PARTIAL_HELDOUT_POSITIVE"
    if any(report.get("beats_rho_with_fallback") for report in fixed):
        return "NEGATIVE_RESULT_P713_SELECTED_RULES_FAIL_BUT_FIXED_0P55_HAS_HELDOUT_SIGNAL"
    return "NEGATIVE_RESULT_P713_REL2_COST_THRESHOLD_DOES_NOT_GENERALIZE_ON_HELDOUT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    args.factor_charge = factor_charge
    thresholds = parse_thresholds(args.thresholds)
    reports, metadata = build_window_reports(args)
    splits = prefix_splits(reports) + rolling_splits(
        reports,
        int_value(args.rolling_train_size),
        int_value(args.rolling_holdout_size),
    )
    split_reports = [
        evaluate_split(split, reports, metadata["replay_cache"], thresholds, args)
        for split in splits
    ]
    selected_below = sum(1 for report in split_reports if report["selected_holdout"].get("beats_rho_with_fallback"))
    fixed_below = sum(1 for report in split_reports if report["fixed_0p55_holdout"].get("beats_rho_with_fallback"))
    oracle_below = sum(1 for report in split_reports if report["heldout_oracle_best"].get("beats_rho_with_fallback"))
    rel2_candidate_count = sum(len(report["rel2_candidates"]) for report in reports)
    rel2_candidate_window_count = sum(1 for report in reports if report["rel2_candidates"])
    return {
        "artifacts": {"p709": str(Path(args.p709)), "p712": str(p712.DEFAULT_OUT)},
        "claim_status": determine_claim(split_reports),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source artifacts outside the P709 source map, not live fresh harvesting.",
            "NO LABEL-ONLY SCORING ON HELDOUT: selected policies are frozen from training before heldout verifier replay is scored.",
            "HEURISTIC: a stable temporal threshold is not an asymptotic index-calculus theorem.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p713_rel2_cost_threshold_temporal_split",
        "parameters": {
            "attempt_budget": int_value(args.attempt_budget),
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
            "rel2_candidate_count": rel2_candidate_count,
            "rel2_candidate_window_count": rel2_candidate_window_count,
            "replay_cache_count": len(metadata["replay_cache"]),
            "replay_error_count": metadata["replay_error_count"],
            "replay_errors": metadata["replay_errors"],
            "source_window_count": len(reports),
        },
        "schema": "ecdlp.low_term_total2_p713_rel2_cost_threshold_temporal_split.v1",
        "split_reports": split_reports,
        "summary": {
            "fixed_0p55_below_rho_splits": fixed_below,
            "heldout_oracle_below_rho_splits": oracle_below,
            "selected_below_rho_splits": selected_below,
            "split_count": len(split_reports),
            "source_window_count": len(reports),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budget", type=int, default=1)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--rolling-holdout-size", type=int, default=16)
    parser.add_argument("--rolling-train-size", type=int, default=24)
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--source-pattern", default=p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.52,0.544,0.55,0.568,0.616")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"split_reports": payload["split_reports"]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

