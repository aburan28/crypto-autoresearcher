#!/usr/bin/env python3
"""P918 partition stress audit for the P917 public policy."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p917_public_c8_residue_redteam as p917


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p918_p917_partition_stress.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p918_p917_partition_stress_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P917_SOURCE = STATE_DIR / "low_term_total2_p917_public_c8_residue_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p918_p917_partition_stress.v1"
PARTITIONS = (
    ("pre_p901_520_975", 520, 975),
    ("p901_train_976_1023", 976, 1023),
    ("p903_validation_1024_1103", 1024, 1103),
    ("p904_forward_1104_1159", 1104, 1159),
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


def transfer_index(record: dict[str, Any]) -> int:
    return p915.transfer_index(record)


def charged_cost(record: dict[str, Any]) -> int:
    return p915.charged_cost(record)


def rank(report: dict[str, Any]) -> int:
    return p915.rank(report)


def partition_name(record: dict[str, Any]) -> str:
    transfer = transfer_index(record)
    for name, low, high in PARTITIONS:
        if low <= transfer <= high:
            return name
    return "outside_partition"


def source_window(record: dict[str, Any]) -> str:
    row = record.get("row") or {}
    source_path = str(row.get("source_path") or "")
    match = re.search(r"_(\d+)_(\d+)_expanded_probe\.json$", source_path)
    if match:
        return f"{match.group(1)}_{match.group(2)}"
    return "unknown"


def p917_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p917.residue_policy_records(records, 11, {2, 4})


def report(
    name: str,
    selected: list[dict[str, Any]],
    target_rank: int,
    boundary: str,
    public_policy: bool = True,
) -> dict[str, Any]:
    item = p915.policy_report(name, selected, boundary, target_rank, public_policy)
    item["charged_candidate_cost_over_p917_full"] = None
    return item


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    row = record.get("row") or {}
    cert = record.get("cert") or {}
    return {
        "charged_candidate_cost_ops": charged_cost(record),
        "clause": row.get("clause"),
        "index": record.get("index"),
        "partition": partition_name(record),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "salt_gap": row.get("salt_gap"),
        "source_window": source_window(record),
        "transfer_index": row.get("transfer_index"),
        "transfer_mod11": transfer_index(record) % 11,
        "usable": p908.usable(cert),
    }


def compact_policy(policy: dict[str, Any], p917_cost: int | None = None) -> dict[str, Any]:
    out = p915.compact_policy(policy)
    if p917_cost not in (None, 0):
        out["charged_candidate_cost_fraction_vs_p917"] = ratio(
            int_value(policy.get("charged_candidate_cost_ops")),
            p917_cost,
        )
    return out


def partition_reports(records: list[dict[str, Any]], target_rank: int, p917_cost: int) -> dict[str, Any]:
    out: dict[str, Any] = {}
    selected_full = p917_records(records)
    for name, _low, _high in PARTITIONS:
        partition_all = [record for record in records if partition_name(record) == name]
        partition_p917 = [record for record in selected_full if partition_name(record) == name]
        all_report = report(
            f"{name}_all_p914_representatives",
            partition_all,
            target_rank,
            "PARTITION DIAGNOSTIC: all P914 representatives inside this partition.",
            public_policy=False,
        )
        p917_report = report(
            f"{name}_p917_policy",
            partition_p917,
            target_rank,
            "PUBLIC-PRE-REPLAY PARTITION: exact P917 policy restricted to this partition.",
            public_policy=True,
        )
        out[name] = {
            "all_representatives": compact_policy(all_report, p917_cost),
            "p917_policy": compact_policy(p917_report, p917_cost),
            "p917_selected_rows": [compact_record(record) for record in partition_p917],
            "representative_count": len(partition_all),
        }
    return out


def leave_one_out_reports(records: list[dict[str, Any]], target_rank: int, p917_cost: int) -> dict[str, Any]:
    selected_full = p917_records(records)
    out: dict[str, Any] = {}
    for name, _low, _high in PARTITIONS:
        kept = [record for record in selected_full if partition_name(record) != name]
        loo = report(
            f"leave_out_{name}",
            kept,
            target_rank,
            "PUBLIC-PRE-REPLAY ABLATION: exact P917 policy with one temporal partition removed.",
            public_policy=True,
        )
        out[name] = {
            "policy": compact_policy(loo, p917_cost),
            "selected_rows": [compact_record(record) for record in kept],
        }
    return out


def cumulative_rank(records: list[dict[str, Any]], target_rank: int, p917_cost: int) -> list[dict[str, Any]]:
    selected = sorted(p917_records(records), key=lambda record: (transfer_index(record), charged_cost(record)))
    out = []
    prefix: list[dict[str, Any]] = []
    for record in selected:
        prefix.append(record)
        item = report(
            "p917_cumulative_prefix",
            prefix,
            target_rank,
            "PUBLIC-PRE-REPLAY DIAGNOSTIC: cumulative exact P917 rows in transfer order.",
            public_policy=True,
        )
        out.append(
            {
                "charged_candidate_cost_ops": item.get("charged_candidate_cost_ops"),
                "charged_candidate_cost_fraction_vs_p917": ratio(
                    int_value(item.get("charged_candidate_cost_ops")),
                    p917_cost,
                ),
                "latest_row": compact_record(record),
                "selected_count": item.get("selected_count"),
                "total_factor_rank": (item.get("summary") or {}).get("total_factor_rank"),
                "total_unique_factor_relation_count": (item.get("summary") or {}).get("total_unique_factor_relation_count"),
                "usable_certificate_count": item.get("usable_certificate_count"),
            }
        )
    return out


def determine_claim(full: dict[str, Any], leave_out: dict[str, Any], partitions: dict[str, Any], target_rank: int) -> str:
    if rank(full) < target_rank:
        return "NEGATIVE_RESULT_P918_P917_FULL_CONTROL_FAILED"
    essential = [
        name
        for name, payload in leave_out.items()
        if int_value((payload.get("policy") or {}).get("total_factor_rank")) < target_rank
    ]
    if essential:
        return "NEGATIVE_RESULT_P918_P917_RANK6_NOT_PARTITION_STABLE"
    partition_success = [
        name
        for name, payload in partitions.items()
        if int_value(((payload.get("p917_policy") or {})).get("total_factor_rank")) >= target_rank
    ]
    if partition_success:
        return "P918_P917_PARTITION_STABLE_RANK6_SIGNAL"
    return "P918_P917_LEAVE_ONE_OUT_STABLE_BUT_NO_SINGLE_PARTITION_RANK6"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p917_payload = load_json(args.p917_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    selected = p917_records(records)
    full_report = report(
        "p917_full_policy_recomputed",
        selected,
        target_rank,
        "PUBLIC-PRE-REPLAY POSITIVE CONTROL: exact P917 policy on the full archive set.",
        public_policy=True,
    )
    p917_cost = int_value(full_report.get("charged_candidate_cost_ops"))
    partitions = partition_reports(records, target_rank, p917_cost)
    leave_out = leave_one_out_reports(records, target_rank, p917_cost)
    cumulative = cumulative_rank(records, target_rank, p917_cost)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p917_source": str(args.p917_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(full_report, leave_out, partitions, target_rank),
        "created_at": now_iso(),
        "cumulative_rank": cumulative,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "PARTITION-STRESS: this is not clean fresh validation because P917 was derived after seeing the archive.",
            "PUBLIC-FEATURE-PREDICTOR: the exact P917 policy uses charged cost, clause, salt gap, and transfer-index residue only.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "leave_one_partition_out": leave_out,
        "method": "p918_p917_partition_stress",
        "parameters": {
            "partition_count": len(PARTITIONS),
            "p917_claim": p917_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
        },
        "partition_reports": partitions,
        "positive_controls": [full_report],
        "schema": SCHEMA,
        "summary": {
            "essential_partitions": [
                name
                for name, payload in leave_out.items()
                if int_value((payload.get("policy") or {}).get("total_factor_rank")) < target_rank
            ],
            "full_p917_policy": compact_policy(full_report, p917_cost),
            "partition_p917_ranks": {
                name: (payload.get("p917_policy") or {}).get("total_factor_rank")
                for name, payload in partitions.items()
            },
            "partition_representative_ranks": {
                name: (payload.get("all_representatives") or {}).get("total_factor_rank")
                for name, payload in partitions.items()
            },
            "p917_selected_rows": [compact_record(record) for record in selected],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p917-source", type=Path, default=P917_SOURCE)
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
