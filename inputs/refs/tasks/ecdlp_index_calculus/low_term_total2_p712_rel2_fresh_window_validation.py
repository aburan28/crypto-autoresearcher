#!/usr/bin/env python3
"""P712 temporal validation for the P711 strict rel2 source rule.

P711 found a sparse below-rho-with-fallback signal inside the P709-referenced
source-neighborhood model.  This scout removes every P709 source path, scans
later temporal source windows from the same public generator family, and charges
the full window population with direct source replay plus rho fallback.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p711_rel2_source_neighborhood_replay as p711


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P709 = STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p712_rel2_fresh_window_validation_probe.json"
SOURCE_PATTERN = "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"
P711_HIT_ROW_PAIRS = {
    "salt202_salt205",
    "salt204_salt209",
    "salt205_salt207",
    "salt207_salt208",
}


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


def parse_int_list(raw: str) -> list[int | str]:
    values: list[int | str] = []
    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        values.append(item if item == "all" else int(item))
    return values


def window_range(path: Path) -> tuple[int, int] | None:
    match = re.search(r"fixed_row_(\d+)_(\d+)_col15_selector_expanded_probe\.json$", path.name)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def source_paths(args: argparse.Namespace) -> list[Path]:
    p709_payload = load_json(Path(args.p709))
    p709_sources = {
        str(report.get("source"))
        for report in p709_payload.get("artifact_reports") or []
        if report.get("source")
    }
    paths: list[Path] = []
    for path in sorted(STATE_DIR.glob(args.source_pattern)):
        source = str(path)
        if source in p709_sources:
            continue
        parsed = window_range(path)
        if parsed is None:
            continue
        lo, hi = parsed
        if hi < int_value(args.min_transfer) or lo > int_value(args.max_transfer):
            continue
        paths.append(path)
    return paths


def policy_predicates() -> dict[str, Callable[[dict[str, Any]], bool]]:
    return {
        "strict_rel2": lambda row: int_value(row.get("relation_count")) == 2,
        "strict_rel2_p711_row_pairs": lambda row: (
            int_value(row.get("relation_count")) == 2 and row.get("row_pair") in P711_HIT_ROW_PAIRS
        ),
        "strict_rel2_low_cost_le_0_55": lambda row: (
            int_value(row.get("relation_count")) == 2
            and float_value(row.get("direct_ops_over_rho"), 999999.0) <= 0.55
        ),
        "any_relation": lambda row: True,
        "rel0_control": lambda row: int_value(row.get("relation_count")) == 0,
    }


def build_window_reports(args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    predicates = policy_predicates()
    replay_cache: dict[str, dict[str, Any]] = {}
    candidate_charge_cache: dict[str, float] = {}
    replay_errors: dict[str, str] = {}
    reports: list[dict[str, Any]] = []
    source_count = 0
    for source_path in source_paths(args):
        source_count += 1
        source = load_json(source_path)
        parsed = window_range(source_path)
        if parsed is None:
            continue
        rows = p711.candidate_rows(source, source_path, args.target)
        policy_rows: dict[str, list[dict[str, Any]]] = {}
        for policy, predicate in predicates.items():
            selected = [row for row in rows if predicate(row)]
            policy_rows[policy] = selected
            for row in selected:
                key = str(row["key"])
                candidate_charge_cache[key] = float_value(row.get("direct_ops_over_rho"))
                if key in replay_cache or key in replay_errors:
                    continue
                try:
                    replay_cache[key] = p711.replay_candidate(source, source_path, row)
                except Exception as exc:  # noqa: BLE001 - verifier failures are experiment evidence.
                    replay_errors[key] = f"{type(exc).__name__}: {exc}"
        reports.append(
            {
                "policy_candidate_keys": {
                    policy: [str(row["key"]) for row in selected]
                    for policy, selected in policy_rows.items()
                },
                "source": str(source_path),
                "window_end": parsed[1],
                "window_start": parsed[0],
            }
        )
    metadata = {
        "candidate_charge_cache": candidate_charge_cache,
        "policy_candidate_counts_unique": {
            policy: len({
                key
                for report in reports
                for key in report["policy_candidate_keys"].get(policy, [])
            })
            for policy in predicates
        },
        "replay_cache": replay_cache,
        "replay_error_count": len(replay_errors),
        "replay_errors": replay_errors,
        "source_count": source_count,
    }
    return reports, metadata


def first_hit(
    keys: list[str],
    replay_cache: dict[str, dict[str, Any]],
    charge_cache: dict[str, float],
    budget: int | str,
) -> tuple[dict[str, Any] | None, float, int]:
    selected_keys = keys if budget == "all" else keys[: int_value(budget)]
    charge = 0.0
    attempted = 0
    for key in selected_keys:
        attempted += 1
        replay = replay_cache.get(key)
        charge += float_value(
            None if replay is None else replay.get("direct_ops_over_rho"),
            charge_cache.get(key, 0.0),
        )
        if replay and replay.get("replay_public_key_verified"):
            return replay, charge, attempted
    return None, charge, attempted


def sample_replay(replay: dict[str, Any] | None) -> dict[str, Any] | None:
    if replay is None:
        return None
    return p711.sample_replay(replay)


def evaluate_policy(
    reports: list[dict[str, Any]],
    replay_cache: dict[str, dict[str, Any]],
    charge_cache: dict[str, float],
    policy: str,
    budget: int | str,
    factor_charge: float,
    sample_limit: int,
) -> dict[str, Any]:
    attempted_charge = 0.0
    attempted_count = 0
    fallback_charge = 0.0
    hit_count = 0
    no_candidate_count = 0
    samples: list[dict[str, Any]] = []
    misses: list[dict[str, Any]] = []
    for report in reports:
        keys = report["policy_candidate_keys"].get(policy, [])
        if not keys:
            no_candidate_count += 1
        hit, charge, attempted = first_hit(keys, replay_cache, charge_cache, budget)
        attempted_charge += charge
        attempted_count += attempted
        if hit:
            hit_count += 1
            if len(samples) < sample_limit:
                samples.append(
                    {
                        "replay": sample_replay(hit),
                        "source": report["source"],
                        "window_end": report["window_end"],
                        "window_start": report["window_start"],
                    }
                )
        else:
            fallback_charge += 1.0
            if len(misses) < sample_limit:
                misses.append(
                    {
                        "candidate_count": len(keys),
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
        "candidate_absent_window_count": no_candidate_count,
        "fallback_charge_over_rho": round(fallback_charge, 8),
        "hit_count": hit_count,
        "hit_rate": round(hit_count / window_count, 8) if window_count else 0.0,
        "hit_samples": samples,
        "miss_samples": misses,
        "policy": policy,
        "source_replay_total_per_hit_over_rho": round(hit_set_total / hit_count, 8) if hit_count else None,
        "source_replay_total_per_window_over_rho": round(total / window_count, 8) if window_count else None,
        "source_replay_total_with_fallback_over_rho": round(total, 8),
        "vs_independent_rho_with_fallback_over_rho": window_count,
    }


def determine_claim(policy_reports: list[dict[str, Any]]) -> str:
    strict = [report for report in policy_reports if report.get("policy") == "strict_rel2"]
    if any(report.get("beats_rho_with_fallback") for report in strict):
        return "P712_REL2_FRESH_WINDOWS_BELOW_RHO_WITH_FALLBACK"
    rel2_diagnostics = [
        report
        for report in policy_reports
        if str(report.get("policy")).startswith("strict_rel2_")
    ]
    if any(report.get("beats_rho_with_fallback") for report in rel2_diagnostics):
        return "P712_REL2_PUBLIC_DIAGNOSTIC_FRESH_WINDOWS_SPARSE_BELOW_RHO_PRIMARY_STRICT_ABOVE_RHO"
    if any(int_value(report.get("hit_count")) for report in strict):
        return "NEGATIVE_RESULT_P712_REL2_FRESH_WINDOWS_HIT_DENSITY_TOO_LOW"
    return "NEGATIVE_RESULT_P712_REL2_FRESH_WINDOWS_NO_VERIFIED_HITS"


def best_report(policy_reports: list[dict[str, Any]], policy: str) -> dict[str, Any] | None:
    reports = [report for report in policy_reports if report.get("policy") == policy]
    if not reports:
        return None
    return min(
        reports,
        key=lambda report: (
            float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
            -int_value(report.get("hit_count")),
            str(report.get("attempt_budget")),
        ),
    )


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p709_payload = load_json(Path(args.p709))
    factor_charge = float_value((p709_payload.get("parameters") or {}).get("factor_bank_charge_over_rho"), 0.992)
    reports, metadata = build_window_reports(args)
    budgets = parse_int_list(args.attempt_budgets)
    policies = sorted(policy_predicates())
    policy_reports = [
        evaluate_policy(
            reports,
            metadata["replay_cache"],
            metadata["candidate_charge_cache"],
            policy,
            budget,
            factor_charge,
            int_value(args.sample_limit),
        )
        for policy in policies
        for budget in budgets
    ]
    policy_reports.sort(
        key=lambda report: (
            not bool(report.get("beats_rho_with_fallback")),
            float_value(report.get("source_replay_total_per_window_over_rho"), 999999.0),
            -float_value(report.get("hit_rate")),
            str(report.get("policy")),
            str(report.get("attempt_budget")),
        )
    )
    best = policy_reports[0] if policy_reports else None
    strict_best = best_report(policy_reports, "strict_rel2")
    claim_status = determine_claim(policy_reports)
    return {
        "artifacts": {"p709": str(Path(args.p709))},
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source files are archived generated source artifacts outside the P709 source map, not a live fresh harvester.",
            "NO LABEL-ONLY SCORING: selected source cases are direct-verifier replayed and charged before success classification.",
            "HEURISTIC: temporal source replay is not an asymptotic index-calculus theorem.",
            "NO DEPLOYED-CURVE CLAIM: target descent, sparse linear algebra, and large-prime scaling remain open.",
        ],
        "method": "p712_rel2_fresh_window_validation",
        "parameters": {
            "attempt_budgets": budgets,
            "factor_bank_charge_over_rho": factor_charge,
            "max_transfer": int_value(args.max_transfer),
            "min_transfer": int_value(args.min_transfer),
            "policies": policies,
            "source_pattern": args.source_pattern,
            "target": args.target,
        },
        "policy_reports": policy_reports,
        "red_team": [
            "The denominator is full source-window count, not only windows with rel2 candidates.",
            "Every P709-referenced source path is excluded before scoring.",
            "The low-cost and P711-row-pair policies are diagnostics; the primary preregistered decision is strict_rel2.",
            "This still does not generate new source windows live; P713 must test a generator or a public narrowing rule.",
        ],
        "replay_metadata": {
            key: value
            for key, value in metadata.items()
            if key not in {"candidate_charge_cache", "replay_cache"}
        },
        "schema": "ecdlp.low_term_total2_p712_rel2_fresh_window_validation.v1",
        "summary": {
            "best_hit_count": None if best is None else best.get("hit_count"),
            "best_hit_rate": None if best is None else best.get("hit_rate"),
            "best_policy": None if best is None else best.get("policy"),
            "best_source_replay_total_with_fallback_over_rho": (
                None if best is None else best.get("source_replay_total_with_fallback_over_rho")
            ),
            "policy_count": len(policy_reports),
            "source_window_count": len(reports),
            "strict_rel2_best_hit_count": None if strict_best is None else strict_best.get("hit_count"),
            "strict_rel2_best_total_with_fallback_over_rho": (
                None if strict_best is None else strict_best.get("source_replay_total_with_fallback_over_rho")
            ),
            "strict_rel2_candidate_count": metadata["policy_candidate_counts_unique"].get("strict_rel2"),
            "unique_replayed_candidate_count": len(metadata["replay_cache"]),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--attempt-budgets", default="1,2,4,all")
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--p709", default=str(DEFAULT_P709))
    parser.add_argument("--sample-limit", type=int, default=8)
    parser.add_argument("--source-pattern", default=SOURCE_PATTERN)
    parser.add_argument("--target", default="67.a1@9803")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"best_policy_reports": payload["policy_reports"][:10]}, indent=2, sort_keys=True))
    print(json.dumps({"replay_metadata": payload["replay_metadata"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
