#!/usr/bin/env python3
"""P917 public c8 transfer-residue red-team for the P916 predictor."""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p916_public_rank_increment_predictor as p916


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p917_public_c8_residue_redteam.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p917_public_c8_residue_redteam_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P916_SOURCE = STATE_DIR / "low_term_total2_p916_public_rank_increment_predictor_probe.json"
SCHEMA = "ecdlp.low_term_total2_p917_public_c8_residue_redteam.v1"


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


def charged_cost(record: dict[str, Any]) -> int:
    return p915.charged_cost(record)


def salt_gap(record: dict[str, Any]) -> int:
    return p915.salt_gap(record)


def transfer_index(record: dict[str, Any]) -> int:
    return p915.transfer_index(record)


def rank(report: dict[str, Any]) -> int:
    return p915.rank(report)


def short_clause(record: dict[str, Any]) -> str:
    return p916.short_clause(record)


def p916_base_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p916.shaped_policy_records(
        records,
        c19_max_cost=122,
        c19_high_gap_min=5,
        c90_max_cost=128,
        c8_max_cost=150,
        c8_gap_min=10,
    )


def residue_policy_records(
    records: list[dict[str, Any]],
    modulus: int,
    residues: set[int],
) -> list[dict[str, Any]]:
    selected = []
    for record in records:
        name = short_clause(record)
        cost = charged_cost(record)
        gap = salt_gap(record)
        if name == "c19" and cost <= 122 and (gap <= 1 or gap >= 5):
            selected.append(record)
        elif name == "c90" and cost <= 128 and gap in {2, 3}:
            selected.append(record)
        elif (
            name == "c8"
            and cost <= 150
            and gap >= 10
            and transfer_index(record) % modulus in residues
        ):
            selected.append(record)
    return selected


def policy_report(
    name: str,
    selected: list[dict[str, Any]],
    target_rank: int,
    boundary: str,
) -> dict[str, Any]:
    return p915.policy_report(name, selected, boundary, target_rank, True)


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return p915.compact_policy(policy)


def candidate_reports(records: list[dict[str, Any]], target_rank: int) -> tuple[list[dict[str, Any]], dict[str, int]]:
    reports: list[dict[str, Any]] = []
    counts = {"residue_subset": 0}
    for modulus in range(2, 17):
        c8_residues = sorted(
            {
                transfer_index(record) % modulus
                for record in records
                if short_clause(record) == "c8"
                and charged_cost(record) <= 150
                and salt_gap(record) >= 10
            }
        )
        for size in range(1, len(c8_residues) + 1):
            for combo in itertools.combinations(c8_residues, size):
                residues = set(combo)
                counts["residue_subset"] += 1
                reports.append(
                    policy_report(
                        f"p916_plus_c8_transfer_mod{modulus}_in_{'_'.join(str(item) for item in combo)}",
                        residue_policy_records(records, modulus, residues),
                        target_rank,
                        "PUBLIC-PRE-REPLAY: P916 shaped policy plus c8 transfer-index residue gate.",
                    )
                )
    return reports, counts


def best_public(reports: list[dict[str, Any]], target_rank: int) -> dict[str, Any]:
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


def determine_claim(best: dict[str, Any], p916_cost: int, oracle_cost: int) -> str:
    best_cost = int_value(best.get("charged_candidate_cost_ops"), 10**12) if best else 10**12
    if best and best_cost <= oracle_cost:
        return "P917_PUBLIC_C8_RESIDUE_GATE_MATCHES_GREEDY_ORACLE"
    if best and best_cost < p916_cost:
        return "P917_PUBLIC_C8_RESIDUE_GATE_IMPROVES_P916"
    if best:
        return "NEGATIVE_RESULT_P917_RESIDUE_GATE_NO_COST_GAIN_OVER_P916"
    return "NEGATIVE_RESULT_P917_NO_RESIDUE_GATE_PRESERVES_RANK6"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p916_payload = load_json(args.p916_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    p916_best = (p916_payload.get("summary") or {}).get("best_public_policy") or {}
    p916_cost = int_value(p916_best.get("charged_candidate_cost_ops"), 10**12)
    oracle = p915.greedy_rank_oracle(records, target_rank)
    oracle_cost = int_value(oracle.get("charged_candidate_cost_ops"), 10**12)
    p916_control = policy_report(
        "p916_shaped_policy_recomputed",
        p916_base_records(records),
        target_rank,
        "PUBLIC-PRE-REPLAY POSITIVE CONTROL: recompute P916 shaped policy.",
    )
    reports, evaluated_counts = candidate_reports(records, target_rank)
    best = best_public(reports, target_rank)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p916_source": str(args.p916_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best, p916_cost, oracle_cost),
        "created_at": now_iso(),
        "diagnostic_reports": [oracle],
        "evaluated_policy_counts": evaluated_counts,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "IN-SAMPLE: the transfer-residue gate is selected after seeing P916/P915 archive rows and needs heldout/fresh validation.",
            "PUBLIC-FEATURE-PREDICTOR: selection predicates use charged cost, clause, salt gap, and transfer-index residues only.",
            "DIAGNOSTIC-ORACLE-BOUNDARY: oracle rows use verifier/rank outcomes and are not source policies.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p917_public_c8_residue_redteam",
        "parameters": {
            "p916_best_public_cost": p916_cost,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
        },
        "positive_controls": [p916_control],
        "schema": SCHEMA,
        "summary": {
            "best_diagnostic": compact_policy(oracle),
            "best_public_policy": compact_policy(best),
            "best_public_selected_rows": best.get("selected_rows") if best else [],
            "cost_fraction_vs_oracle": ratio(
                int_value(best.get("charged_candidate_cost_ops")),
                oracle_cost,
            )
            if best
            else None,
            "cost_saved_fraction_vs_p916": ratio(
                p916_cost - int_value(best.get("charged_candidate_cost_ops")),
                p916_cost,
            )
            if best
            else None,
            "positive_control": compact_policy(p916_control),
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
    parser.add_argument("--p916-source", type=Path, default=P916_SOURCE)
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
                    "cost_saved_fraction_vs_p916": payload["summary"]["cost_saved_fraction_vs_p916"],
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
