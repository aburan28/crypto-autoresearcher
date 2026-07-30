#!/usr/bin/env python3
"""P915 cost-compression audit over the P914 archive rank-6 certificate set."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p915_archive_rank6_cost_compression.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p915_archive_rank6_cost_compression_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p915_archive_rank6_cost_compression.v1"


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


def records(p914_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in p914_payload.get("selected_rows") or [] if isinstance(row, dict)]
    certs = [cert for cert in p914_payload.get("certificates") or [] if isinstance(cert, dict)]
    out = []
    for index, (row, cert) in enumerate(zip(rows, certs)):
        out.append({"cert": cert, "index": index, "row": row})
    return out


def charged_cost(record: dict[str, Any]) -> int:
    return int_value((record.get("row") or {}).get("charged_candidate_cost_ops"), 1)


def transfer_index(record: dict[str, Any]) -> int:
    return int_value((record.get("row") or {}).get("transfer_index"))


def clause(record: dict[str, Any]) -> str:
    return str((record.get("row") or {}).get("clause"))


def salt_gap(record: dict[str, Any]) -> int:
    return int_value((record.get("row") or {}).get("salt_gap"), -1)


def rank(report: dict[str, Any]) -> int:
    return int_value((report.get("summary") or {}).get("total_factor_rank"))


def policy_report(
    name: str,
    selected: list[dict[str, Any]],
    boundary: str,
    target_rank: int,
    public_policy: bool,
) -> dict[str, Any]:
    certs = [record["cert"] for record in selected]
    audits = p908.order_audits(certs)
    summary = p908.audit_summary(audits)
    cost = sum(charged_cost(record) for record in selected)
    report = {
        "charged_candidate_cost_ops": cost,
        "charged_candidate_cost_over_rho": ratio(cost, p905.RHO_ESTIMATE),
        "discovery_boundary": boundary,
        "matrix_consistent": all(bool(audit.get("matrix_consistent")) for audit in audits.values()) if audits else True,
        "name": name,
        "order_audits": audits,
        "public_policy": public_policy,
        "selected_count": len(selected),
        "selected_rows": [compact_record(record) for record in selected],
        "summary": summary,
        "target_preserving": summary.get("total_factor_rank", 0) >= target_rank,
        "usable_certificate_count": sum(1 for cert in certs if p908.usable(cert)),
    }
    return report


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    row = record.get("row") or {}
    cert = record.get("cert") or {}
    return {
        "charged_candidate_cost_ops": charged_cost(record),
        "clause": row.get("clause"),
        "index": record.get("index"),
        "leaf_signature": row.get("leaf_signature"),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "salt_gap": row.get("salt_gap"),
        "selector_group": row.get("selector_group"),
        "transfer_index": row.get("transfer_index"),
        "usable": p908.usable(cert),
    }


def public_policy_reports(all_records: list[dict[str, Any]], target_rank: int) -> list[dict[str, Any]]:
    reports = [
        policy_report(
            "p914_full_selected_baseline",
            all_records,
            "PUBLIC-PRE-REPLAY POSITIVE CONTROL: full P914 selected representative set.",
            target_rank,
            True,
        )
    ]
    costs = sorted({charged_cost(record) for record in all_records})
    for threshold in costs:
        reports.append(
            policy_report(
                f"public_charged_cost_le_{threshold}",
                [record for record in all_records if charged_cost(record) <= threshold],
                "PUBLIC-PRE-REPLAY: charged candidate cost threshold over P914 representatives.",
                target_rank,
                True,
            )
        )
    ordered = sorted(all_records, key=lambda record: (charged_cost(record), transfer_index(record), clause(record), record["index"]))
    for count in range(1, len(ordered) + 1):
        reports.append(
            policy_report(
                f"public_cost_prefix_{count}",
                ordered[:count],
                "PUBLIC-PRE-REPLAY: cheapest-N prefix over P914 representatives.",
                target_rank,
                True,
            )
        )
    for gap in sorted({salt_gap(record) for record in all_records if salt_gap(record) >= 0}):
        reports.append(
            policy_report(
                f"public_salt_gap_le_{gap}",
                [record for record in all_records if salt_gap(record) <= gap],
                "PUBLIC-PRE-REPLAY CONTROL: salt-gap upper threshold.",
                target_rank,
                True,
            )
        )
        reports.append(
            policy_report(
                f"public_salt_gap_ge_{gap}",
                [record for record in all_records if salt_gap(record) >= gap],
                "PUBLIC-PRE-REPLAY CONTROL: salt-gap lower threshold.",
                target_rank,
                True,
            )
        )
    for value in sorted({clause(record) for record in all_records}):
        reports.append(
            policy_report(
                f"public_clause_{value}",
                [record for record in all_records if clause(record) == value],
                "PUBLIC-PRE-REPLAY CONTROL: single clause only.",
                target_rank,
                True,
            )
        )
    return reports


def greedy_rank_oracle(all_records: list[dict[str, Any]], target_rank: int) -> dict[str, Any]:
    selected: list[dict[str, Any]] = []
    current_rank = 0
    for record in sorted(all_records, key=lambda item: (charged_cost(item), transfer_index(item), item["index"])):
        if not p908.usable(record["cert"]):
            continue
        trial = selected + [record]
        report = policy_report(
            "rank_increment_oracle_diagnostic",
            trial,
            "ORACLE DIAGNOSTIC: uses verifier and rank outcomes; not a source policy.",
            target_rank,
            False,
        )
        trial_rank = rank(report)
        if trial_rank > current_rank:
            selected = trial
            current_rank = trial_rank
            if current_rank >= target_rank:
                break
    return policy_report(
        "rank_increment_oracle_diagnostic",
        selected,
        "ORACLE DIAGNOSTIC: uses verifier and rank outcomes; not a source policy.",
        target_rank,
        False,
    )


def best_public(policies: list[dict[str, Any]], baseline_cost: int, target_rank: int) -> dict[str, Any]:
    valid = [
        policy
        for policy in policies
        if bool(policy.get("public_policy"))
        and bool(policy.get("matrix_consistent"))
        and rank(policy) >= target_rank
        and int_value(policy.get("charged_candidate_cost_ops"), 10**12) < baseline_cost
    ]
    if not valid:
        return {}
    return min(
        valid,
        key=lambda policy: (
            int_value(policy.get("charged_candidate_cost_ops"), 10**12),
            int_value(policy.get("selected_count"), 10**12),
            str(policy.get("name")),
        ),
    )


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "charged_candidate_cost_ops": policy.get("charged_candidate_cost_ops"),
        "charged_candidate_cost_over_rho": policy.get("charged_candidate_cost_over_rho"),
        "matrix_consistent": policy.get("matrix_consistent"),
        "name": policy.get("name"),
        "public_policy": policy.get("public_policy"),
        "selected_count": policy.get("selected_count"),
        "target_preserving": policy.get("target_preserving"),
        "total_factor_rank": (policy.get("summary") or {}).get("total_factor_rank"),
        "total_unique_factor_relation_count": (policy.get("summary") or {}).get("total_unique_factor_relation_count"),
        "usable_certificate_count": policy.get("usable_certificate_count"),
    }


def determine_claim(best: dict[str, Any]) -> str:
    if best:
        return "P915_PUBLIC_COST_FILTER_COMPRESSES_ARCHIVE_RANK6"
    return "NEGATIVE_RESULT_P915_NO_PUBLIC_COST_FILTER_COMPRESSES_RANK6"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    all_records = records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    policies = public_policy_reports(all_records, target_rank)
    baseline = next(policy for policy in policies if policy["name"] == "p914_full_selected_baseline")
    baseline_cost = int_value(baseline.get("charged_candidate_cost_ops"), 10**12)
    oracle = greedy_rank_oracle(all_records, target_rank)
    best = best_public(policies, baseline_cost, target_rank)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best),
        "created_at": now_iso(),
        "diagnostic_reports": [oracle],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this compresses a historical archive-selected certificate set.",
            "IN-SAMPLE: public filters are chosen on the P914 certificate set and require fresh validation.",
            "DIAGNOSTIC-ORACLE-BOUNDARY: oracle rows use verifier/rank outcomes and are not source policies.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p915_archive_rank6_cost_compression",
        "parameters": {
            "p914_selected_count": len(all_records),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
        },
        "policy_reports": policies,
        "schema": SCHEMA,
        "summary": {
            "baseline_policy": compact_policy(baseline),
            "best_diagnostic": compact_policy(oracle),
            "best_public_policy": compact_policy(best),
            "cost_saved_fraction_vs_p914": ratio(
                baseline_cost - int_value(best.get("charged_candidate_cost_ops")),
                baseline_cost,
            )
            if best
            else None,
            "policy_count": len(policies),
            "top_public_policy_table": [
                compact_policy(policy)
                for policy in sorted(
                    policies,
                    key=lambda policy: (
                        rank(policy) < target_rank,
                        int_value(policy.get("charged_candidate_cost_ops"), 10**12),
                        int_value(policy.get("selected_count"), 10**12),
                        str(policy.get("name")),
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
                "summary": payload["summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
