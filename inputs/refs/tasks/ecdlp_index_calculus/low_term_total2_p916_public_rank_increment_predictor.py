#!/usr/bin/env python3
"""P916 public rank-increment predictor over the P914/P915 archive set."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p916_public_rank_increment_predictor.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p916_public_rank_increment_predictor_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P915_SOURCE = STATE_DIR / "low_term_total2_p915_archive_rank6_cost_compression_probe.json"
SCHEMA = "ecdlp.low_term_total2_p916_public_rank_increment_predictor.v1"


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


def rank(report: dict[str, Any]) -> int:
    return p915.rank(report)


def charged_cost(record: dict[str, Any]) -> int:
    return p915.charged_cost(record)


def clause(record: dict[str, Any]) -> str:
    return p915.clause(record)


def short_clause(record: dict[str, Any]) -> str:
    return clause(record).split("_", 1)[0]


def salt_gap(record: dict[str, Any]) -> int:
    return p915.salt_gap(record)


def transfer_index(record: dict[str, Any]) -> int:
    return p915.transfer_index(record)


def public_report(name: str, selected: list[dict[str, Any]], target_rank: int, boundary: str) -> dict[str, Any]:
    return p915.policy_report(name, selected, boundary, target_rank, True)


def diagnostic_oracle(records: list[dict[str, Any]], target_rank: int) -> dict[str, Any]:
    return p915.greedy_rank_oracle(records, target_rank)


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return p915.compact_policy(policy)


def clause_names(records: list[dict[str, Any]]) -> dict[str, str]:
    names: dict[str, str] = {}
    for record in records:
        names[short_clause(record)] = clause(record)
    return names


def shaped_policy_records(
    records: list[dict[str, Any]],
    c19_max_cost: int,
    c19_high_gap_min: int,
    c90_max_cost: int,
    c8_max_cost: int,
    c8_gap_min: int,
) -> list[dict[str, Any]]:
    selected = []
    for record in records:
        cost = charged_cost(record)
        gap = salt_gap(record)
        name = short_clause(record)
        if name == "c19" and cost <= c19_max_cost and (gap <= 1 or gap >= c19_high_gap_min):
            selected.append(record)
        elif name == "c90" and cost <= c90_max_cost and gap in {2, 3}:
            selected.append(record)
        elif name == "c8" and cost <= c8_max_cost and gap >= c8_gap_min:
            selected.append(record)
    return selected


def per_clause_cost_records(records: list[dict[str, Any]], c19_max_cost: int, c90_max_cost: int, c8_max_cost: int) -> list[dict[str, Any]]:
    selected = []
    for record in records:
        cost = charged_cost(record)
        name = short_clause(record)
        if name == "c19" and cost <= c19_max_cost:
            selected.append(record)
        elif name == "c90" and cost <= c90_max_cost:
            selected.append(record)
        elif name == "c8" and cost <= c8_max_cost:
            selected.append(record)
    return selected


def c8_gap_records(records: list[dict[str, Any]], c19_max_cost: int, c90_max_cost: int, c8_max_cost: int, c8_gap_min: int) -> list[dict[str, Any]]:
    selected = []
    for record in records:
        cost = charged_cost(record)
        name = short_clause(record)
        if name == "c19" and cost <= c19_max_cost:
            selected.append(record)
        elif name == "c90" and cost <= c90_max_cost:
            selected.append(record)
        elif name == "c8" and cost <= c8_max_cost and salt_gap(record) >= c8_gap_min:
            selected.append(record)
    return selected


def candidate_reports(records: list[dict[str, Any]], target_rank: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    reports: list[dict[str, Any]] = []
    evaluated_counts = {"c8_gap": 0, "per_clause_cost": 0, "shaped_band": 0}
    costs_by_clause = {
        name: sorted({charged_cost(record) for record in records if short_clause(record) == name})
        for name in ("c19", "c90", "c8")
    }
    gaps = sorted({salt_gap(record) for record in records if salt_gap(record) >= 0})

    for c19_max in costs_by_clause["c19"]:
        for c90_max in costs_by_clause["c90"]:
            for c8_max in costs_by_clause["c8"]:
                evaluated_counts["per_clause_cost"] += 1
                reports.append(
                    public_report(
                        f"per_clause_cost_c19_le{c19_max}_c90_le{c90_max}_c8_le{c8_max}",
                        per_clause_cost_records(records, c19_max, c90_max, c8_max),
                        target_rank,
                        "PUBLIC-PRE-REPLAY: per-clause charged-cost thresholds.",
                    )
                )
                for c8_gap_min in gaps:
                    evaluated_counts["c8_gap"] += 1
                    reports.append(
                        public_report(
                            f"c19_le{c19_max}_c90_le{c90_max}_c8_le{c8_max}_c8_gapge{c8_gap_min}",
                            c8_gap_records(records, c19_max, c90_max, c8_max, c8_gap_min),
                            target_rank,
                            "PUBLIC-PRE-REPLAY: per-clause charged-cost thresholds plus c8 high-gap gate.",
                        )
                    )
                for c19_high_gap_min in (5, 6, 7, 8):
                    for c8_gap_min in (10, 11):
                        evaluated_counts["shaped_band"] += 1
                        reports.append(
                            public_report(
                                (
                                    f"shaped_c19_le{c19_max}_gaple1_or_ge{c19_high_gap_min}"
                                    f"_c90_le{c90_max}_gap2_3_c8_le{c8_max}_gapge{c8_gap_min}"
                                ),
                                shaped_policy_records(
                                    records,
                                    c19_max,
                                    c19_high_gap_min,
                                    c90_max,
                                    c8_max,
                                    c8_gap_min,
                                ),
                                target_rank,
                                "PUBLIC-PRE-REPLAY: clause-specific cost caps and salt-gap bands derived from public row features.",
                            )
                        )
    return reports, evaluated_counts


def best_target_preserving_public(reports: list[dict[str, Any]], target_rank: int) -> dict[str, Any]:
    valid = [
        report
        for report in reports
        if bool(report.get("matrix_consistent")) and rank(report) >= target_rank
    ]
    if not valid:
        return {}
    return min(
        valid,
        key=lambda report: (
            int_value(report.get("charged_candidate_cost_ops"), 10**12),
            int_value(report.get("selected_count"), 10**12),
            str(report.get("name")),
        ),
    )


def determine_claim(best: dict[str, Any], p915_public_cost: int) -> str:
    if best and int_value(best.get("charged_candidate_cost_ops"), 10**12) < p915_public_cost:
        return "P916_PUBLIC_RANK_INCREMENT_PREDICTOR_APPROACHES_ORACLE"
    if best:
        return "NEGATIVE_RESULT_P916_PUBLIC_PREDICTOR_NO_COST_GAIN_OVER_P915"
    return "NEGATIVE_RESULT_P916_NO_PUBLIC_PREDICTOR_PRESERVES_RANK6"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p915_payload = load_json(args.p915_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    p915_public_cost = int_value(((p915_payload.get("summary") or {}).get("best_public_policy") or {}).get("charged_candidate_cost_ops"), 10**12)
    p915_public_name = str(((p915_payload.get("summary") or {}).get("best_public_policy") or {}).get("name"))

    p915_positive_control = public_report(
        "p915_public_charged_cost_le_150_recomputed",
        [record for record in records if charged_cost(record) <= 150],
        target_rank,
        "PUBLIC-PRE-REPLAY POSITIVE CONTROL: recompute P915 charged-cost threshold.",
    )
    oracle = diagnostic_oracle(records, target_rank)
    reports, evaluated_counts = candidate_reports(records, target_rank)
    best = best_target_preserving_public(reports, target_rank)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p915_source": str(args.p915_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best, p915_public_cost),
        "created_at": now_iso(),
        "diagnostic_reports": [oracle],
        "evaluated_policy_counts": evaluated_counts,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "IN-SAMPLE: the public predictor is selected on P914/P915 rows and needs fresh or heldout validation.",
            "PUBLIC-FEATURE-PREDICTOR: selection predicates use charged cost, clause, salt gap, and public row metadata only.",
            "DIAGNOSTIC-ORACLE-BOUNDARY: oracle rows use verifier/rank outcomes and are not source policies.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p916_public_rank_increment_predictor",
        "parameters": {
            "p914_selected_count": len(records),
            "p915_best_public_cost": p915_public_cost,
            "p915_best_public_name": p915_public_name,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
        },
        "positive_controls": [p915_positive_control],
        "schema": SCHEMA,
        "summary": {
            "best_diagnostic": compact_policy(oracle),
            "best_public_policy": compact_policy(best),
            "best_public_selected_rows": best.get("selected_rows") if best else [],
            "cost_fraction_vs_oracle": ratio(
                int_value(best.get("charged_candidate_cost_ops")),
                int_value(oracle.get("charged_candidate_cost_ops")),
            )
            if best and oracle
            else None,
            "cost_saved_fraction_vs_p915_public": ratio(
                p915_public_cost - int_value(best.get("charged_candidate_cost_ops")),
                p915_public_cost,
            )
            if best
            else None,
            "positive_control": compact_policy(p915_positive_control),
            "top_public_policy_table": [
                compact_policy(report)
                for report in sorted(
                    reports,
                    key=lambda report: (
                        rank(report) < target_rank,
                        int_value(report.get("charged_candidate_cost_ops"), 10**12),
                        int_value(report.get("selected_count"), 10**12),
                        str(report.get("name")),
                    ),
                )[:12]
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p915-source", type=Path, default=P915_SOURCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "parameters": payload["parameters"],
                "summary": {
                    "best_diagnostic": payload["summary"]["best_diagnostic"],
                    "best_public_policy": payload["summary"]["best_public_policy"],
                    "cost_fraction_vs_oracle": payload["summary"]["cost_fraction_vs_oracle"],
                    "cost_saved_fraction_vs_p915_public": payload["summary"]["cost_saved_fraction_vs_p915_public"],
                    "positive_control": payload["summary"]["positive_control"],
                    "top_public_policy_table": payload["summary"]["top_public_policy_table"][:5],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
