#!/usr/bin/env python3
"""P919 public validation-rank recovery audit for the P917 policy."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p916_public_rank_increment_predictor as p916
import low_term_total2_p917_public_c8_residue_redteam as p917
import low_term_total2_p918_p917_partition_stress as p918


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p919_public_validation_rank_recovery.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p919_public_validation_rank_recovery_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P917_SOURCE = STATE_DIR / "low_term_total2_p917_public_c8_residue_redteam_probe.json"
SCHEMA = "ecdlp.low_term_total2_p919_public_validation_rank_recovery.v1"
VALIDATION_PARTITION = "p903_validation_1024_1103"


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


def is_validation(record: dict[str, Any]) -> bool:
    return p918.partition_name(record) == VALIDATION_PARTITION


def report(name: str, selected: list[dict[str, Any]], target_rank: int, boundary: str) -> dict[str, Any]:
    return p915.policy_report(name, selected, boundary, target_rank, True)


def false_selected_count(policy: dict[str, Any]) -> int:
    return int_value(policy.get("selected_count")) - int_value(policy.get("usable_certificate_count"))


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    row = record.get("row") or {}
    cert = record.get("cert") or {}
    return {
        "charged_candidate_cost_ops": charged_cost(record),
        "clause": row.get("clause"),
        "index": record.get("index"),
        "leaf_signature": row.get("leaf_signature"),
        "partition": p918.partition_name(record),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "salt_gap": row.get("salt_gap"),
        "selector_group": row.get("selector_group"),
        "transfer_index": row.get("transfer_index"),
        "transfer_mod11": transfer_index(record) % 11,
        "usable": p908.usable(cert),
    }


def compact_policy(policy: dict[str, Any], baseline_cost: int | None = None) -> dict[str, Any]:
    out = p915.compact_policy(policy)
    out["false_selected_count"] = false_selected_count(policy)
    if baseline_cost not in (None, 0):
        out["charged_candidate_cost_fraction_vs_baseline"] = ratio(
            int_value(policy.get("charged_candidate_cost_ops")),
            baseline_cost,
        )
    return out


def gap_predicate(mode: str) -> Callable[[int], bool]:
    if mode == "p917_gap_2_3":
        return lambda gap: gap in {2, 3}
    if mode == "gap_le3":
        return lambda gap: 0 <= gap <= 3
    if mode == "gap_le4":
        return lambda gap: 0 <= gap <= 4
    if mode == "p917_c19":
        return lambda gap: gap <= 1 or gap >= 5
    if mode == "gap_eq5":
        return lambda gap: gap == 5
    if mode == "gap_eq8":
        return lambda gap: gap == 8
    if mode == "gap_ge5":
        return lambda gap: gap >= 5
    if mode == "gap_ge8":
        return lambda gap: gap >= 8
    raise ValueError(f"unknown gap mode {mode}")


def policy_records(
    records: list[dict[str, Any]],
    *,
    c19_extra_mode: str,
    c19_extra_cost_cap: int,
    c90_gap_mode: str,
    c90_cost_cap: int,
) -> list[dict[str, Any]]:
    c19_extra_gap = gap_predicate(c19_extra_mode)
    c90_gap = gap_predicate(c90_gap_mode)
    selected: list[dict[str, Any]] = []
    for record in records:
        name = short_clause(record)
        cost = charged_cost(record)
        gap = salt_gap(record)
        if name == "c19":
            p917_base = cost <= 122 and (gap <= 1 or gap >= 5)
            c19_rescue = cost <= c19_extra_cost_cap and c19_extra_gap(gap)
            if p917_base or c19_rescue:
                selected.append(record)
        elif name == "c90":
            if cost <= c90_cost_cap and c90_gap(gap):
                selected.append(record)
        elif (
            name == "c8"
            and cost <= 150
            and gap >= 10
            and transfer_index(record) % 11 in {2, 4}
        ):
            selected.append(record)
    return selected


def policy_name(c19_extra_mode: str, c19_extra_cost_cap: int, c90_gap_mode: str, c90_cost_cap: int) -> str:
    return (
        f"p917_plus_c19_{c19_extra_mode}_le{c19_extra_cost_cap}"
        f"_c90_{c90_gap_mode}_le{c90_cost_cap}"
    )


def analyze_candidate(
    records: list[dict[str, Any]],
    target_rank: int,
    *,
    c19_extra_mode: str,
    c19_extra_cost_cap: int,
    c90_gap_mode: str,
    c90_cost_cap: int,
    p917_train_cost: int,
) -> dict[str, Any]:
    name = policy_name(c19_extra_mode, c19_extra_cost_cap, c90_gap_mode, c90_cost_cap)
    selected = policy_records(
        records,
        c19_extra_mode=c19_extra_mode,
        c19_extra_cost_cap=c19_extra_cost_cap,
        c90_gap_mode=c90_gap_mode,
        c90_cost_cap=c90_cost_cap,
    )
    train_selected = [record for record in selected if not is_validation(record)]
    validation_selected = [record for record in selected if is_validation(record)]
    full_report = report(
        name,
        selected,
        target_rank,
        "PUBLIC-PRE-REPLAY: P917-compatible rule with fixed c19/c90 extension knobs.",
    )
    train_report = report(
        f"{name}_train_nonvalidation",
        train_selected,
        target_rank,
        "TRAINING ONLY: non-validation partitions; validation labels excluded.",
    )
    validation_report = report(
        f"{name}_validation_p903",
        validation_selected,
        target_rank,
        "HOLDOUT AUDIT: P903 validation partition; not used for train admissibility.",
    )
    train_cost = int_value(train_report.get("charged_candidate_cost_ops"))
    train_false = false_selected_count(train_report)
    train_rank = rank(train_report)
    admissible = (
        bool(train_report.get("matrix_consistent"))
        and train_rank >= target_rank
        and train_false == 0
        and train_cost <= 2 * p917_train_cost
    )
    return {
        "admissible_on_train": admissible,
        "c19_extra_cost_cap": c19_extra_cost_cap,
        "c19_extra_mode": c19_extra_mode,
        "c90_cost_cap": c90_cost_cap,
        "c90_gap_mode": c90_gap_mode,
        "full_policy": compact_policy(full_report, p917_train_cost),
        "full_selected_rows": [compact_record(record) for record in selected],
        "name": name,
        "train_policy": compact_policy(train_report, p917_train_cost),
        "train_selected_rows": [compact_record(record) for record in train_selected],
        "validation_policy": compact_policy(validation_report),
        "validation_selected_rows": [compact_record(record) for record in validation_selected],
    }


def candidate_grid(
    records: list[dict[str, Any]],
    target_rank: int,
    p917_train_cost: int,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for c19_extra_mode in ("p917_c19", "gap_eq5", "gap_eq8", "gap_ge5", "gap_ge8"):
        for c19_extra_cost_cap in (122, 135, 150, 180):
            for c90_gap_mode in ("p917_gap_2_3", "gap_le3", "gap_le4"):
                for c90_cost_cap in (128, 150, 180):
                    out.append(
                        analyze_candidate(
                            records,
                            target_rank,
                            c19_extra_mode=c19_extra_mode,
                            c19_extra_cost_cap=c19_extra_cost_cap,
                            c90_gap_mode=c90_gap_mode,
                            c90_cost_cap=c90_cost_cap,
                            p917_train_cost=p917_train_cost,
                        )
                    )
    return out


def train_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    train = candidate.get("train_policy") or {}
    return (
        0 if candidate.get("admissible_on_train") else 1,
        int_value(train.get("false_selected_count"), 10**12),
        int_value(train.get("charged_candidate_cost_ops"), 10**12),
        str(candidate.get("c19_extra_mode")),
        int_value(candidate.get("c19_extra_cost_cap"), 10**12),
        str(candidate.get("c90_gap_mode")),
        int_value(candidate.get("c90_cost_cap"), 10**12),
        str(candidate.get("name")),
    )


def validation_recovery_sort_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    validation = candidate.get("validation_policy") or {}
    train = candidate.get("train_policy") or {}
    return (
        0 if candidate.get("admissible_on_train") else 1,
        -int_value(validation.get("total_factor_rank")),
        int_value(validation.get("charged_candidate_cost_ops"), 10**12),
        int_value(train.get("charged_candidate_cost_ops"), 10**12),
        int_value(validation.get("false_selected_count"), 10**12),
        str(candidate.get("name")),
    )


def determine_claim(admissible: list[dict[str, Any]]) -> str:
    best_validation_rank = max(
        (int_value((candidate.get("validation_policy") or {}).get("total_factor_rank")) for candidate in admissible),
        default=0,
    )
    if best_validation_rank >= 3:
        return "P919_TRAIN_ADMISSIBLE_PUBLIC_EXTENSION_RECOVERS_VALIDATION_RANK3"
    if best_validation_rank > 0:
        return "P919_TRAIN_ADMISSIBLE_PUBLIC_EXTENSION_RECOVERS_PARTIAL_VALIDATION_RANK"
    return "NEGATIVE_RESULT_P919_NO_TRAIN_ADMISSIBLE_PUBLIC_EXTENSION_RECOVERS_VALIDATION_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p917_payload = load_json(args.p917_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    p917_full_selected = p917.residue_policy_records(records, 11, {2, 4})
    p917_train_selected = [record for record in p917_full_selected if not is_validation(record)]
    p917_validation_selected = [record for record in p917_full_selected if is_validation(record)]
    validation_all = [record for record in records if is_validation(record)]
    p917_full_report = report(
        "p917_full_policy_recomputed",
        p917_full_selected,
        target_rank,
        "POSITIVE CONTROL: exact P917 policy on all P914 records.",
    )
    p917_train_report = report(
        "p917_train_nonvalidation_recomputed",
        p917_train_selected,
        target_rank,
        "POSITIVE CONTROL: exact P917 policy restricted to non-validation rows.",
    )
    p917_validation_report = report(
        "p917_validation_p903_recomputed",
        p917_validation_selected,
        target_rank,
        "NEGATIVE CONTROL: exact P917 policy restricted to validation rows.",
    )
    validation_all_report = report(
        "p903_validation_all_representatives",
        validation_all,
        target_rank,
        "NEGATIVE CONTROL: all P914 representatives in the P903 validation partition.",
    )
    p917_train_cost = int_value(p917_train_report.get("charged_candidate_cost_ops"))
    candidates = candidate_grid(records, target_rank, p917_train_cost)
    admissible = [candidate for candidate in candidates if candidate.get("admissible_on_train")]
    validation_recovery = [
        candidate
        for candidate in admissible
        if int_value((candidate.get("validation_policy") or {}).get("total_factor_rank")) > 0
    ]
    best_train_only = sorted(candidates, key=train_sort_key)[0] if candidates else {}
    best_validation_recovery = (
        sorted(validation_recovery, key=validation_recovery_sort_key)[0] if validation_recovery else {}
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p917_source": str(args.p917_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(admissible),
        "created_at": now_iso(),
        "evaluated_policy_counts": {
            "admissible_on_train": len(admissible),
            "grid_total": len(candidates),
            "validation_recovery_admissible": len(validation_recovery),
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "HELDOUT-PARTITION-AUDIT: validation labels are excluded from train admissibility, but the holdout is still historical archive data.",
            "PUBLIC-FEATURE-PREDICTOR: selection predicates use charged cost, clause, salt gap, and transfer-index residue only.",
            "DIAGNOSTIC-HOLDOUT-SELECTION: best validation-recovery policy is reported for triage and must be frozen before fresh replay.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p919_public_validation_rank_recovery",
        "parameters": {
            "p917_claim": p917_payload.get("claim_status"),
            "p917_train_cost": p917_train_cost,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "train_cost_admissibility_factor": 2,
            "validation_partition": VALIDATION_PARTITION,
        },
        "positive_controls": [p917_full_report, p917_train_report],
        "negative_controls": [p917_validation_report, validation_all_report],
        "schema": SCHEMA,
        "summary": {
            "best_train_only_policy": best_train_only,
            "best_validation_recovery_among_train_admissible": best_validation_recovery,
            "p917_full_policy": compact_policy(p917_full_report, p917_train_cost),
            "p917_train_policy": compact_policy(p917_train_report, p917_train_cost),
            "p917_validation_policy": compact_policy(p917_validation_report),
            "top_train_admissible_table": sorted(admissible, key=train_sort_key)[:12],
            "top_validation_recovery_table": sorted(validation_recovery, key=validation_recovery_sort_key)[:12],
            "validation_all_representatives": compact_policy(validation_all_report),
            "validation_all_rows": [compact_record(record) for record in validation_all],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p917-source", type=Path, default=P917_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload.get("summary") or {}
    best = summary.get("best_validation_recovery_among_train_admissible") or {}
    best_validation = best.get("validation_policy") or {}
    print(
        "claim={claim} grid={grid} admissible={admissible} validation_recovery={recovery} "
        "best_validation_rank={rank} best_validation_cost={cost} out={out}".format(
            claim=payload.get("claim_status"),
            grid=(payload.get("evaluated_policy_counts") or {}).get("grid_total"),
            admissible=(payload.get("evaluated_policy_counts") or {}).get("admissible_on_train"),
            recovery=(payload.get("evaluated_policy_counts") or {}).get("validation_recovery_admissible"),
            rank=best_validation.get("total_factor_rank"),
            cost=best_validation.get("charged_candidate_cost_ops"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
