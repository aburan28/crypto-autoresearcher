#!/usr/bin/env python3
"""P714 rel2 marginal-cost and public window-precheck audit."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p713_rel2_cost_threshold_temporal_split as p713


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_P713 = STATE_DIR / "low_term_total2_p713_rel2_cost_threshold_temporal_split_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p714_rel2_marginal_window_precheck_probe.json"


@dataclass(frozen=True)
class WindowPolicy:
    name: str
    threshold: float | None = None
    max_rel2_candidates: int | None = None
    exact_rel2_candidates: int | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def int_value(value: Any, default: int = 0) -> int:
    return p713.int_value(value, default)


def float_value(value: Any, default: float = 0.0) -> float:
    return p713.float_value(value, default)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def threshold_token(threshold: float) -> str:
    return str(threshold).replace(".", "p")


def parse_thresholds(raw: str) -> tuple[float, ...]:
    return tuple(float(item.strip()) for item in raw.split(",") if item.strip())


def policy_accepts_report(policy: WindowPolicy, report: dict[str, Any]) -> bool:
    count = len(report.get("rel2_candidates") or [])
    if policy.exact_rel2_candidates is not None and count != policy.exact_rel2_candidates:
        return False
    if policy.max_rel2_candidates is not None and count > policy.max_rel2_candidates:
        return False
    return True


def policy_accepts_row(policy: WindowPolicy, row: dict[str, Any]) -> bool:
    if policy.threshold is not None and float_value(row.get("direct_ops_over_rho"), 999999.0) > policy.threshold:
        return False
    return True


def make_window_policies(thresholds: tuple[float, ...]) -> list[WindowPolicy]:
    policies = [WindowPolicy("strict_rel2")]
    for threshold in thresholds:
        policies.append(WindowPolicy(f"cost_le_{threshold_token(threshold)}", threshold=threshold))
    for exact in (1,):
        policies.append(WindowPolicy(f"window_rel2_count_eq{exact}", exact_rel2_candidates=exact))
        for threshold in thresholds:
            policies.append(
                WindowPolicy(
                    f"window_rel2_count_eq{exact}_cost_le_{threshold_token(threshold)}",
                    threshold=threshold,
                    exact_rel2_candidates=exact,
                )
            )
    for maximum in (2,):
        policies.append(WindowPolicy(f"window_rel2_count_le{maximum}", max_rel2_candidates=maximum))
        for threshold in thresholds:
            policies.append(
                WindowPolicy(
                    f"window_rel2_count_le{maximum}_cost_le_{threshold_token(threshold)}",
                    threshold=threshold,
                    max_rel2_candidates=maximum,
                )
            )
    return policies


def sample_replay(replay: dict[str, Any] | None) -> dict[str, Any] | None:
    return p713.sample_replay(replay)


def evaluate_window_policy(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    policy: WindowPolicy,
    factor_charge: float,
    attempt_budget: int,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    precheck_window_count = 0
    hit_samples: list[dict[str, Any]] = []
    miss_samples: list[dict[str, Any]] = []
    for report in reports:
        accepted_rows: list[dict[str, Any]] = []
        if policy_accepts_report(policy, report):
            accepted_rows = [
                row
                for row in report.get("rel2_candidates") or []
                if policy_accepts_row(policy, row)
            ]
        if accepted_rows:
            precheck_window_count += 1
        hit = None
        charge = 0.0
        attempted = 0
        for row in accepted_rows[:attempt_budget]:
            attempted += 1
            charge += float_value(row.get("direct_ops_over_rho"))
            replay = replay_cache.get(str(row["key"]))
            if replay and replay.get("replay_public_key_verified"):
                hit = replay
                break
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
                        "accepted_candidate_count": len(accepted_rows),
                        "rel2_candidate_count": len(report.get("rel2_candidates") or []),
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
    window_count = len(reports)
    total = factor_charge + attempted_charge + fallback_charge
    hit_set_total = factor_charge + attempted_charge
    return {
        "attempt_budget": attempt_budget,
        "attempted_candidate_count": attempted_count,
        "attempted_source_charge_over_rho": round(attempted_charge, 8),
        "beats_rho_on_hit_set": bool(hit_count and hit_set_total < hit_count),
        "beats_rho_with_fallback": bool(window_count and total < window_count),
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "factor_charge_over_rho": round(factor_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": hit_samples,
        "miss_samples": miss_samples,
        "policy": policy.name,
        "policy_exact_rel2_candidates": policy.exact_rel2_candidates,
        "policy_max_rel2_candidates": policy.max_rel2_candidates,
        "policy_threshold": policy.threshold,
        "precheck_window_count": precheck_window_count,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_per_window_over_rho": round(total / window_count, 8) if window_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": window_count,
        "window_count": window_count,
    }


def best_report(reports: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not reports:
        return None
    return min(
        reports,
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
            -int_value(report.get("hit_count")),
            int_value(report.get("attempted_candidate_count")),
            str(report.get("policy")),
        ),
    )


def reaccount_p713_split_reports(p713_payload: dict[str, Any], factor_charge: float) -> list[dict[str, Any]]:
    rows = []
    for split in p713_payload.get("split_reports") or []:
        item = {
            "split": split.get("split"),
            "selected_policy": split.get("selected_policy"),
        }
        for key in ("selected_holdout", "fixed_0p55_holdout", "heldout_oracle_best"):
            report = split.get(key) or {}
            baseline = float_value(report.get("vs_independent_rho_with_fallback_over_rho"))
            new_total = float_value(report.get("source_replay_total_with_fallback_over_rho"))
            marginal_total = round(new_total - factor_charge, 8)
            item[key] = {
                "beats_marginal_existing_bank": bool(marginal_total < baseline),
                "beats_new_bank": bool(report.get("beats_rho_with_fallback")),
                "hit_count": int_value(report.get("hit_count")),
                "marginal_existing_bank_total_over_rho": marginal_total,
                "new_bank_total_over_rho": new_total,
                "policy": report.get("policy"),
                "vs_independent_rho_with_fallback_over_rho": baseline,
            }
        rows.append(item)
    return rows


def summarize_reaccounting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {"split_count": len(rows)}
    for key in ("selected_holdout", "fixed_0p55_holdout", "heldout_oracle_best"):
        summary[f"{key}_new_bank_below_rho_splits"] = sum(1 for row in rows if row[key]["beats_new_bank"])
        summary[f"{key}_marginal_existing_bank_below_rho_splits"] = sum(
            1 for row in rows if row[key]["beats_marginal_existing_bank"]
        )
    return summary


def split_window_policy_reports(
    p713_payload: dict[str, Any],
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    policies: list[WindowPolicy],
    factor_charge: float,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    split_reports = []
    for split in p713_payload.get("split_reports") or []:
        start = int_value(split.get("holdout_start_index"))
        end = int_value(split.get("holdout_end_index"))
        holdout_reports = reports[start:end]
        marginal_reports = [
            evaluate_window_policy(
                holdout_reports,
                replay_cache,
                policy,
                0.0,
                int_value(args.attempt_budget),
                int_value(args.sample_limit),
            )
            for policy in policies
        ]
        new_reports = [
            evaluate_window_policy(
                holdout_reports,
                replay_cache,
                policy,
                factor_charge,
                int_value(args.attempt_budget),
                int_value(args.sample_limit),
            )
            for policy in policies
        ]
        split_reports.append(
            {
                "best_marginal_existing_bank_public_precheck": best_report(marginal_reports),
                "best_new_bank_public_precheck": best_report(new_reports),
                "holdout_end_index": end,
                "holdout_start_index": start,
                "split": split.get("split"),
                "top_marginal_existing_bank_public_prechecks": sorted(
                    marginal_reports,
                    key=lambda report: (
                        not bool(report.get("beats_rho_with_fallback")),
                        float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
                        -int_value(report.get("hit_count")),
                        int_value(report.get("attempted_candidate_count")),
                        str(report.get("policy")),
                    ),
                )[:6],
            }
        )
    return split_reports


def determine_claim(reaccounting_summary: dict[str, Any], split_precheck_reports: list[dict[str, Any]]) -> str:
    selected_marginal = int_value(reaccounting_summary.get("selected_holdout_marginal_existing_bank_below_rho_splits"))
    fixed_marginal = int_value(reaccounting_summary.get("fixed_0p55_holdout_marginal_existing_bank_below_rho_splits"))
    public_precheck_marginal = sum(
        1
        for report in split_precheck_reports
        if (report.get("best_marginal_existing_bank_public_precheck") or {}).get("beats_rho_with_fallback")
    )
    if selected_marginal == int_value(reaccounting_summary.get("split_count")):
        return "P714_SELECTED_REL2_RULES_BEAT_RHO_ON_ALL_HELDOUT_SPLITS_AS_EXISTING_BANK_MARGINAL"
    if fixed_marginal or public_precheck_marginal:
        return "P714_EXISTING_BANK_MARGINAL_REL2_HAS_PARTIAL_HELDOUT_SIGNAL_BUT_PRECHECK_NOT_STABLE"
    return "NEGATIVE_RESULT_P714_REL2_NOT_USEFUL_EVEN_AS_EXISTING_BANK_MARGINAL"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    p713_payload = load_json(Path(args.p713))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    args.factor_charge = factor_charge
    thresholds = p713.parse_thresholds(args.thresholds)
    reports, metadata = p713.build_window_reports(args)
    policies = make_window_policies(thresholds)
    full_new_reports = [
        evaluate_window_policy(
            reports,
            metadata["replay_cache"],
            policy,
            factor_charge,
            int_value(args.attempt_budget),
            int_value(args.sample_limit),
        )
        for policy in policies
    ]
    full_marginal_reports = [
        evaluate_window_policy(
            reports,
            metadata["replay_cache"],
            policy,
            0.0,
            int_value(args.attempt_budget),
            int_value(args.sample_limit),
        )
        for policy in policies
    ]
    reaccounted_splits = reaccount_p713_split_reports(p713_payload, factor_charge)
    reaccounting_summary = summarize_reaccounting(reaccounted_splits)
    split_prechecks = split_window_policy_reports(
        p713_payload,
        reports,
        metadata["replay_cache"],
        policies,
        factor_charge,
        args,
    )
    public_precheck_marginal_below = sum(
        1
        for report in split_prechecks
        if (report.get("best_marginal_existing_bank_public_precheck") or {}).get("beats_rho_with_fallback")
    )
    return {
        "artifacts": {"p709": str(Path(args.p709)), "p713": str(Path(args.p713))},
        "claim_status": determine_claim(reaccounting_summary, split_prechecks),
        "created_at": now_iso(),
        "full_population": {
            "best_marginal_existing_bank": best_report(full_marginal_reports),
            "best_new_bank": best_report(full_new_reports),
            "top_marginal_existing_bank": sorted(
                full_marginal_reports,
                key=lambda report: (
                    not bool(report.get("beats_rho_with_fallback")),
                    float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
                    -int_value(report.get("hit_count")),
                    int_value(report.get("attempted_candidate_count")),
                    str(report.get("policy")),
                ),
            )[:8],
            "top_new_bank": sorted(
                full_new_reports,
                key=lambda report: (
                    not bool(report.get("beats_rho_with_fallback")),
                    float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
                    -int_value(report.get("hit_count")),
                    int_value(report.get("attempted_candidate_count")),
                    str(report.get("policy")),
                ),
            )[:8],
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: archived source artifacts outside the P709 source map, not live fresh harvesting.",
            "MARGINAL ACCOUNTING: existing-bank mode assumes the reusable factor bank has already been paid by a many-target workflow.",
            "NO LABEL-ONLY HELDOUT CLAIM: public prechecks use source-row metadata; heldout labels are used only for post-freeze scoring or explicitly marked oracle reaccounting.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p714_rel2_marginal_window_precheck",
        "parameters": {
            "attempt_budget": int_value(args.attempt_budget),
            "factor_bank_charge_over_rho": factor_charge,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "source_pattern": args.source_pattern,
            "target": args.target,
            "thresholds": thresholds,
        },
        "reaccounted_p713_splits": reaccounted_splits,
        "replay_metadata": {
            "rel2_candidate_count": sum(len(report.get("rel2_candidates") or []) for report in reports),
            "rel2_candidate_window_count": sum(1 for report in reports if report.get("rel2_candidates")),
            "replay_cache_count": len(metadata["replay_cache"]),
            "replay_error_count": metadata["replay_error_count"],
            "replay_errors": metadata["replay_errors"],
            "source_window_count": len(reports),
        },
        "schema": "ecdlp.low_term_total2_p714_rel2_marginal_window_precheck.v1",
        "split_public_precheck_reports": split_prechecks,
        "summary": {
            **reaccounting_summary,
            "best_full_marginal_policy": (best_report(full_marginal_reports) or {}).get("policy"),
            "best_full_marginal_total_over_rho": (best_report(full_marginal_reports) or {}).get("source_replay_total_with_fallback_over_rho"),
            "best_full_new_bank_policy": (best_report(full_new_reports) or {}).get("policy"),
            "best_full_new_bank_total_over_rho": (best_report(full_new_reports) or {}).get("source_replay_total_with_fallback_over_rho"),
            "public_precheck_marginal_existing_bank_below_rho_splits": public_precheck_marginal_below,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budget", type=int, default=1)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--p713", default=str(DEFAULT_P713))
    parser.add_argument("--sample-limit", type=int, default=6)
    parser.add_argument("--source-pattern", default=p713.p712.SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--thresholds", default="0.52,0.544,0.55,0.568,0.616")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"reaccounted_p713_splits": payload["reaccounted_p713_splits"]}, indent=2, sort_keys=True))
    print(json.dumps({"full_population": payload["full_population"]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

