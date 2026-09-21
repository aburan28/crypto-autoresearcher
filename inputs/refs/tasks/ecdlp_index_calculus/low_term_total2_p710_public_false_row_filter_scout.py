#!/usr/bin/env python3
"""P710 public false-row filter scout over P709 source replay traces.

The P709 source replay showed that the P708 top-k selector orders many cheap
false source rows before verifier-positive rows.  This scout tests public
feature filters on a chronological split over the P709 verifier-replayed prefix.
Held-out ordering uses only public row descriptors and training statistics from
earlier artifacts; verifier labels are used only for scoring after selection.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p710_public_false_row_filter_scout_probe.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_int_list(raw: str) -> list[int]:
    return [int(item.strip()) for item in raw.split(",") if item.strip()]


def selector_mode(selector: str | None) -> str:
    return str(selector or "").split("__", 1)[0] or "none"


def salt_from_row_key(row_key: str) -> str:
    match = re.search(r":salt(\d+)", row_key)
    return f"salt{match.group(1)}" if match else "unknown"


def row_pair(attempt: dict[str, Any]) -> str:
    salts = [salt_from_row_key(str(row_key)) for row_key in attempt.get("row_keys") or []]
    return "_".join(sorted(salts)) if salts else "none"


def parse_anchor(selector: str | None) -> str:
    raw = str(selector or "")
    match = re.search(r"_ra(\d+)", raw)
    if match:
        return f"anchor{int(match.group(1))}"
    match = re.search(r"anchor(\d+)", raw)
    return f"anchor{int(match.group(1))}" if match else "none"


def parse_right(selector: str | None) -> str:
    raw = str(selector or "")
    match = re.search(r"right(20[678]|\d+)", raw)
    return f"right{match.group(1)}" if match else "none"


def parse_leaf_signature(selector: str | None) -> str:
    raw = str(selector or "")
    match = re.search(r"_L([0-9]+)_R([0-9-]+)", raw)
    return f"L{match.group(1)}_R{match.group(2)}" if match else "none"


def cost_bucket(value: Any) -> str:
    cost = float_value(value, -1.0)
    if cost < 0:
        return "cost_none"
    if cost <= 0.50:
        return "cost_le_050"
    if cost <= 0.75:
        return "cost_le_075"
    if cost <= 1.00:
        return "cost_le_100"
    return "cost_gt_100"


def index_bucket(value: Any) -> str:
    index = int_value(value)
    if index == 0:
        return "idx0"
    if index <= 8:
        return "idx1_8"
    if index <= 32:
        return "idx9_32"
    if index <= 128:
        return "idx33_128"
    return "idx129_plus"


def feature_map(attempt: dict[str, Any]) -> dict[str, str]:
    mode = selector_mode(attempt.get("selector"))
    pair = row_pair(attempt)
    anchor = parse_anchor(attempt.get("selector"))
    right = parse_right(attempt.get("selector"))
    leaf_sig = parse_leaf_signature(attempt.get("selector"))
    leaf_shape = (
        f"leaf{int_value(attempt.get('selected_leaf_count'))}"
        f"|rows{int_value(attempt.get('selected_row_count'))}"
        f"|rel{int_value(attempt.get('relation_count'))}"
    )
    cost = cost_bucket(attempt.get("direct_ops_over_rho"))
    row_selector = str(attempt.get("row_selector") or "none")
    source_policy = str(attempt.get("source_policy") or "none")
    top_k = f"top{int_value(attempt.get('top_k'))}"
    features = {
        "anchor": anchor,
        "cost_bucket": cost,
        "leaf_signature": leaf_sig,
        "leaf_shape": leaf_shape,
        "mode_anchor": f"{mode}|{anchor}",
        "mode_cost": f"{mode}|{cost}",
        "mode_leaf_shape": f"{mode}|{leaf_shape}",
        "mode_pair": f"{mode}|{pair}",
        "mode_right": f"{mode}|{right}",
        "mode_row_selector": f"{mode}|{row_selector}",
        "mode_top_k": f"{mode}|{top_k}",
        "right_pair": f"{right}|{pair}",
        "row_index_bucket": index_bucket(attempt.get("source_row_index")),
        "row_pair": pair,
        "row_selector": row_selector,
        "selector_mode": mode,
        "source_policy": source_policy,
        "source_policy_pair": f"{source_policy}|{pair}",
        "top_k": top_k,
    }
    return {key: value for key, value in features.items() if value and "none" not in value}


def transfer_key(report: dict[str, Any]) -> int:
    values = [int_value(attempt.get("transfer_index"), 10**9) for attempt in report.get("attempts") or []]
    return min(values) if values else 10**9


def load_reports(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path)
    reports = []
    for report in payload.get("artifact_reports") or []:
        attempts = [
            {
                **attempt,
                "_artifact": report.get("artifact"),
                "_source": report.get("source"),
                "_features": feature_map(attempt),
            }
            for attempt in report.get("attempts") or []
            if not attempt.get("error")
        ]
        reports.append(
            {
                "artifact": report.get("artifact"),
                "attempts": attempts,
                "source": report.get("source"),
                "transfer_key": transfer_key(report),
            }
        )
    reports.sort(key=lambda item: (int_value(item.get("transfer_key")), str(item.get("artifact"))))
    return reports


def feature_stats(records: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for record in records:
        value = (record.get("_features") or {}).get(family)
        if not value:
            continue
        entry = grouped.setdefault(
            value,
            {
                "artifact_set": set(),
                "costs": [],
                "positive_artifact_set": set(),
                "positive_count": 0,
                "record_count": 0,
                "value": value,
            },
        )
        artifact = str(record.get("_artifact"))
        entry["artifact_set"].add(artifact)
        entry["costs"].append(float_value(record.get("direct_ops_over_rho")))
        entry["record_count"] += 1
        if record.get("replay_public_key_verified"):
            entry["positive_count"] += 1
            entry["positive_artifact_set"].add(artifact)
    stats = []
    for value, entry in grouped.items():
        record_count = int_value(entry["record_count"])
        positive_count = int_value(entry["positive_count"])
        costs = entry["costs"] or [0.0]
        stats.append(
            {
                "artifact_count": len(entry["artifact_set"]),
                "mean_cost_over_rho": round(mean(costs), 8),
                "positive_artifact_count": len(entry["positive_artifact_set"]),
                "positive_count": positive_count,
                "precision": round(positive_count / record_count, 8) if record_count else 0.0,
                "record_count": record_count,
                "value": value,
            }
        )
    stats.sort(
        key=lambda item: (
            -int_value(item["positive_artifact_count"]),
            -float_value(item["precision"]),
            float_value(item["mean_cost_over_rho"]),
            -int_value(item["record_count"]),
            str(item["value"]),
        )
    )
    return stats


def selected_attempts(
    attempts: list[dict[str, Any]],
    family: str,
    ranked_values: dict[str, tuple[int, dict[str, Any]]],
) -> list[dict[str, Any]]:
    selected = []
    for attempt in attempts:
        value = (attempt.get("_features") or {}).get(family)
        if value not in ranked_values:
            continue
        rank, stat = ranked_values[value]
        selected.append((rank, stat, attempt))
    selected.sort(
        key=lambda item: (
            item[0],
            -float_value(item[1].get("precision")),
            float_value(item[2].get("direct_ops_over_rho")),
            int_value(item[2].get("source_row_index")),
            str(item[2].get("selector")),
        )
    )
    return [attempt for _rank, _stat, attempt in selected]


def first_hit(attempts: list[dict[str, Any]], budget: int) -> tuple[dict[str, Any] | None, float]:
    charge = 0.0
    for attempt in attempts[:budget]:
        charge += float_value(attempt.get("direct_ops_over_rho"))
        if attempt.get("replay_public_key_verified"):
            return attempt, charge
    return None, charge


def compact_attempt(attempt: dict[str, Any] | None) -> dict[str, Any] | None:
    if attempt is None:
        return None
    return {
        "direct_ops_over_rho": attempt.get("direct_ops_over_rho"),
        "features": attempt.get("_features"),
        "relation_count": attempt.get("relation_count"),
        "replay_public_key_verified": bool(attempt.get("replay_public_key_verified")),
        "row_keys": attempt.get("row_keys"),
        "row_selector": attempt.get("row_selector"),
        "selector": attempt.get("selector"),
        "selected_leaf_count": attempt.get("selected_leaf_count"),
        "selected_row_count": attempt.get("selected_row_count"),
        "source_policy": attempt.get("source_policy"),
        "source_row_index": attempt.get("source_row_index"),
        "top_k": attempt.get("top_k"),
        "transfer_index": attempt.get("transfer_index"),
    }


def evaluate_policy(
    reports: list[dict[str, Any]],
    family: str,
    top_n: int,
    budget: int,
    factor_charge: float,
    min_train_artifacts: int,
    sample_limit: int,
) -> dict[str, Any]:
    hit_count = 0
    attempted_charge = 0.0
    fallback_charge = 0.0
    no_candidate_count = 0
    evaluated_count = 0
    samples = []
    misses = []
    for index, report in enumerate(reports):
        if index < min_train_artifacts:
            continue
        training = [
            attempt
            for prior in reports[:index]
            for attempt in prior.get("attempts") or []
        ]
        stats = feature_stats(training, family)
        ranked = {str(stat["value"]): (rank, stat) for rank, stat in enumerate(stats[:top_n])}
        selected = selected_attempts(report.get("attempts") or [], family, ranked)
        if not selected:
            no_candidate_count += 1
        hit, charge = first_hit(selected, budget)
        attempted_charge += charge
        evaluated_count += 1
        if hit:
            hit_count += 1
            if len(samples) < sample_limit:
                samples.append(
                    {
                        "artifact": report.get("artifact"),
                        "attempt": compact_attempt(hit),
                        "source": report.get("source"),
                    }
                )
        else:
            fallback_charge += 1.0
            if len(misses) < sample_limit:
                misses.append(
                    {
                        "artifact": report.get("artifact"),
                        "selected_count": len(selected),
                        "source": report.get("source"),
                    }
                )
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "attempt_budget": budget,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(evaluated_count and total < evaluated_count),
        "evaluated_artifact_count": evaluated_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "feature_family": family,
        "hit_count": hit_count,
        "hit_rate": round(hit_count / evaluated_count, 8) if evaluated_count else 0.0,
        "hit_samples": samples,
        "miss_samples": misses,
        "no_candidate_count": no_candidate_count,
        "policy": f"{family}:top{top_n}:budget{budget}:chronological",
        "source_replay_total_per_artifact_over_rho": round(total / evaluated_count, 8) if evaluated_count else None,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "top_n": top_n,
        "vs_independent_rho_with_fallback_over_rho": evaluated_count,
    }


def baseline_report(
    reports: list[dict[str, Any]],
    budget: int,
    factor_charge: float,
    min_train_artifacts: int,
) -> dict[str, Any]:
    evaluated = reports[min_train_artifacts:]
    hit_count = 0
    attempted_charge = 0.0
    fallback_charge = 0.0
    for report in evaluated:
        hit, charge = first_hit(report.get("attempts") or [], budget)
        attempted_charge += charge
        if hit:
            hit_count += 1
        else:
            fallback_charge += 1.0
    total = factor_charge + attempted_charge + fallback_charge
    evaluated_count = len(evaluated)
    return {
        "attempt_budget": budget,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "evaluated_artifact_count": evaluated_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / evaluated_count, 8) if evaluated_count else 0.0,
        "policy": f"p709_original_order_budget{budget}",
        "source_replay_total_per_artifact_over_rho": round(total / evaluated_count, 8) if evaluated_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": evaluated_count,
    }


def oracle_prefix_report(
    reports: list[dict[str, Any]],
    factor_charge: float,
    min_train_artifacts: int,
) -> dict[str, Any]:
    hit_count = 0
    attempted_charge = 0.0
    fallback_charge = 0.0
    for report in reports[min_train_artifacts:]:
        positives = [
            attempt
            for attempt in report.get("attempts") or []
            if attempt.get("replay_public_key_verified")
        ]
        if positives:
            positives.sort(key=lambda item: float_value(item.get("direct_ops_over_rho")))
            hit_count += 1
            attempted_charge += float_value(positives[0].get("direct_ops_over_rho"))
        else:
            fallback_charge += 1.0
    evaluated_count = max(0, len(reports) - min_train_artifacts)
    total = factor_charge + attempted_charge + fallback_charge
    return {
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "evaluated_artifact_count": evaluated_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / evaluated_count, 8) if evaluated_count else 0.0,
        "policy": "label_oracle_best_positive_inside_p709_prefix8",
        "source_replay_total_per_artifact_over_rho": round(total / evaluated_count, 8) if evaluated_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": evaluated_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]], baseline_reports: list[dict[str, Any]]) -> str:
    if any(
        report.get("beats_rho_with_fallback") and float_value(report.get("hit_rate")) >= 0.5
        for report in policy_reports
    ):
        return "P710_PUBLIC_FALSE_ROW_FILTER_BELOW_RHO_WITH_FALLBACK"
    best = min(
        policy_reports,
        key=lambda report: float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0),
        default=None,
    )
    baselines_by_budget = {int_value(report.get("attempt_budget")): report for report in baseline_reports}
    if best:
        base = baselines_by_budget.get(int_value(best.get("attempt_budget")))
        if (
            base
            and int_value(best.get("hit_count")) > int_value(base.get("hit_count"))
            and float_value(best.get("source_replay_total_with_fallback_over_rho"), 999999.0)
            < float_value(base.get("source_replay_total_with_fallback_over_rho"), 999999.0)
        ):
            return "P710_PUBLIC_FALSE_ROW_FILTER_IMPROVES_PREFIX_REPLAY_COST_OPEN"
        if (
            base
            and float_value(best.get("source_replay_total_with_fallback_over_rho"), 999999.0)
            < float_value(base.get("source_replay_total_with_fallback_over_rho"), 999999.0)
        ):
            return "NEGATIVE_RESULT_P710_ABSTENTION_FILTER_REDUCES_COST_RECALL_REGRESSES"
    if any(report.get("hit_count") for report in policy_reports):
        return "NEGATIVE_RESULT_P710_FALSE_ROW_FILTER_NO_USEFUL_IMPROVEMENT"
    return "NEGATIVE_RESULT_P710_NO_FALSE_ROW_FILTER_HITS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709 = load_json(Path(args.p709))
    factor_charge = float_value((p709.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    reports = load_reports(Path(args.p709))
    feature_families = sorted({
        key
        for report in reports
        for attempt in report.get("attempts") or []
        for key in (attempt.get("_features") or {})
    })
    if args.feature_families:
        requested = {item.strip() for item in args.feature_families.split(",") if item.strip()}
        feature_families = [family for family in feature_families if family in requested]
    top_values = parse_int_list(args.top_values)
    budgets = parse_int_list(args.attempt_budgets)
    policy_reports = [
        evaluate_policy(
            reports,
            family,
            top_n,
            budget,
            factor_charge,
            int_value(args.min_train_artifacts),
            int_value(args.sample_limit),
        )
        for family in feature_families
        for top_n in top_values
        for budget in budgets
    ]
    policy_reports.sort(
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_artifact_over_rho"), 999999.0),
            -float_value(report.get("hit_rate")),
            str(report.get("policy")),
        )
    )
    baseline_reports = [
        baseline_report(reports, budget, factor_charge, int_value(args.min_train_artifacts))
        for budget in budgets
    ]
    best = policy_reports[0] if policy_reports else None
    claim_status = determine_claim(policy_reports, baseline_reports)
    return {
        "artifacts": {"p709": str(Path(args.p709))},
        "baseline_reports": baseline_reports,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: this uses the first eight verifier-replayed P709 source attempts, not the full source-row space.",
            "NO LABEL LEAKAGE IN FILTER: held-out ordering uses public descriptors and earlier verification outcomes only.",
            "HEURISTIC: feature recurrence over this trace is not an asymptotic index-calculus theorem.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p710_public_false_row_filter_scout",
        "oracle_prefix8_report": oracle_prefix_report(reports, factor_charge, int_value(args.min_train_artifacts)),
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "feature_families": feature_families,
            "min_train_artifacts": int_value(args.min_train_artifacts),
            "top_values": top_values,
        },
        "policy_reports": policy_reports,
        "schema": "ecdlp.low_term_total2_p710_public_false_row_filter_scout.v1",
        "summary": {
            "artifact_count": len(reports),
            "best_hit_count": None if best is None else best.get("hit_count"),
            "best_hit_rate": None if best is None else best.get("hit_rate"),
            "best_policy": None if best is None else best.get("policy"),
            "best_source_replay_total_with_fallback_over_rho": (
                None if best is None else best.get("source_replay_total_with_fallback_over_rho")
            ),
            "evaluated_artifact_count": max(0, len(reports) - int_value(args.min_train_artifacts)),
            "feature_family_count": len(feature_families),
            "p709_claim_status": p709.get("claim_status"),
            "policy_count": len(policy_reports),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2,4")
    parser.add_argument("--feature-families", default="")
    parser.add_argument("--min-train-artifacts", type=int, default=12)
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--top-values", default="1,3,5,10,20")
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy_reports": payload["policy_reports"][:5]}, indent=2, sort_keys=True))
    print(json.dumps({"baseline_reports": payload["baseline_reports"], "oracle": payload["oracle_prefix8_report"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
