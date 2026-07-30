#!/usr/bin/env python3
"""P920 structural audit for the P919 c19 gap-5 validation recovery."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p916_public_rank_increment_predictor as p916
import low_term_total2_p918_p917_partition_stress as p918
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p920_c19_gap5_structural_signature.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p920_c19_gap5_structural_signature_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P919_SOURCE = STATE_DIR / "low_term_total2_p919_public_validation_rank_recovery_probe.json"
SCHEMA = "ecdlp.low_term_total2_p920_c19_gap5_structural_signature.v1"
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


def is_validation(record: dict[str, Any]) -> bool:
    return p918.partition_name(record) == VALIDATION_PARTITION


def is_c19(record: dict[str, Any]) -> bool:
    return p916.short_clause(record) == "c19"


def is_usable(record: dict[str, Any]) -> bool:
    return factor_bank.certificate_is_usable(record.get("cert") or {})


def target_relations(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        relation
        for relation in factor_bank.target_eliminated_rows(record.get("cert") or {})
        if relation.get("relation_status") == "TARGET_ELIMINATED_FACTOR_RELATION"
    ]


def relation_signature(relation: dict[str, Any]) -> dict[str, Any]:
    coeffs = [int_value(value) for value in relation.get("canonical_coeffs") or []]
    support = [int_value(value) for value in relation.get("factor_support") or []]
    values = [coeffs[index] for index in support]
    return {
        "canonical_rhs": int_value(relation.get("canonical_rhs")),
        "factor_support": support,
        "factor_support_size": int_value(relation.get("factor_support_size")),
        "pair": relation.get("pair"),
        "support_values": values,
    }


def has_simple_two_factor_relation(record: dict[str, Any]) -> bool:
    return any(
        signature["factor_support_size"] == 2 and signature["support_values"] == [1, 1]
        for signature in relation_signatures(record)
    )


def three_factor_relation_count(record: dict[str, Any]) -> int:
    return sum(
        1
        for signature in relation_signatures(record)
        if signature["factor_support_size"] == 3
    )


def relation_signatures(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [relation_signature(relation) for relation in target_relations(record)]


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    row = record.get("row") or {}
    cert = record.get("cert") or {}
    signatures = relation_signatures(record)
    return {
        "charged_candidate_cost_ops": charged_cost(record),
        "clause": row.get("clause"),
        "emitted_factor_relation_count": len(signatures),
        "forms_count": cert.get("forms_count"),
        "has_simple_two_factor_relation": any(
            signature["factor_support_size"] == 2 and signature["support_values"] == [1, 1]
            for signature in signatures
        ),
        "index": record.get("index"),
        "partition": p918.partition_name(record),
        "public_key_verified": cert.get("public_key_verified"),
        "rank": cert.get("rank"),
        "relation_signatures": signatures,
        "salt_gap": row.get("salt_gap"),
        "three_factor_relation_count": sum(
            1 for signature in signatures if signature["factor_support_size"] == 3
        ),
        "transfer_index": row.get("transfer_index"),
        "usable": is_usable(record),
    }


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    out = p915.compact_policy(policy)
    out["false_selected_count"] = int_value(policy.get("selected_count")) - int_value(policy.get("usable_certificate_count"))
    return out


def policy_report(name: str, records: list[dict[str, Any]], target_rank: int, boundary: str) -> dict[str, Any]:
    return p915.policy_report(name, records, boundary, target_rank, True)


def group_stats(rows: list[dict[str, Any]], key_name: str) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key_name))].append(row)
    out: dict[str, Any] = {}
    for key, items in sorted(groups.items()):
        out[key] = {
            "charged_candidate_cost_ops": sum(int_value(item.get("charged_candidate_cost_ops")) for item in items),
            "count": len(items),
            "simple_two_factor_count": sum(1 for item in items if item.get("has_simple_two_factor_relation")),
            "three_factor_relation_count": sum(int_value(item.get("three_factor_relation_count")) for item in items),
            "usable_count": sum(1 for item in items if item.get("usable")),
            "verified_count": sum(1 for item in items if item.get("public_key_verified")),
        }
    return out


def signature_histogram(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[Any, ...]] = Counter()
    examples: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        for signature in row.get("relation_signatures") or []:
            key = (
                tuple(signature.get("factor_support") or []),
                tuple(signature.get("support_values") or []),
                int_value(signature.get("canonical_rhs")),
            )
            counts[key] += 1
            examples.setdefault(
                key,
                {
                    "example_index": row.get("index"),
                    "example_transfer_index": row.get("transfer_index"),
                    "factor_support": list(key[0]),
                    "support_values": list(key[1]),
                    "canonical_rhs": key[2],
                },
            )
    out = []
    for key, count in counts.most_common():
        item = dict(examples[key])
        item["count"] = count
        out.append(item)
    return out


def determine_claim(
    gap5_rows: list[dict[str, Any]],
    simple_rows: list[dict[str, Any]],
    no_simple_rows: list[dict[str, Any]],
    validation_gap5_rows: list[dict[str, Any]],
) -> str:
    if (
        gap5_rows
        and all(row.get("usable") for row in gap5_rows)
        and simple_rows
        and all(row.get("usable") for row in simple_rows)
        and no_simple_rows
        and not any(row.get("usable") for row in no_simple_rows)
        and any(int_value(row.get("three_factor_relation_count")) > 0 for row in validation_gap5_rows)
    ):
        return "P920_C19_GAP5_HAS_CLEAN_SIMPLE_SIGNATURE_AND_VALIDATION_TRI_RELATION"
    if simple_rows and all(row.get("usable") for row in simple_rows):
        return "P920_C19_SIMPLE_SIGNATURE_IS_CLEAN_POST_REPLAY_FILTER"
    return "NEGATIVE_RESULT_P920_C19_GAP5_SIGNATURE_NOT_CLEAN"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p919_payload = load_json(args.p919_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    c19_records = [record for record in records if is_c19(record)]
    c19_rows = [compact_record(record) for record in c19_records]
    gap5_records = [record for record in c19_records if salt_gap(record) == 5]
    simple_records = [record for record in c19_records if has_simple_two_factor_relation(record)]
    no_simple_records = [record for record in c19_records if not has_simple_two_factor_relation(record)]
    validation_gap5_records = [record for record in gap5_records if is_validation(record)]
    train_gap5_records = [record for record in gap5_records if not is_validation(record)]
    p919_best = ((p919_payload.get("summary") or {}).get("best_validation_recovery_among_train_admissible") or {})
    p919_full_records = p919.policy_records(
        records,
        c19_extra_mode="gap_eq5",
        c19_extra_cost_cap=180,
        c90_gap_mode="gap_le3",
        c90_cost_cap=128,
    )
    p919_full_report = policy_report(
        "p919_best_policy_recomputed",
        p919_full_records,
        target_rank,
        "POSITIVE CONTROL: recompute P919 best validation-recovery policy.",
    )
    reports = {
        "c19_gap5_all": policy_report(
            "c19_gap5_all",
            gap5_records,
            target_rank,
            "PUBLIC DIAGNOSTIC: all c19 records with salt_gap == 5.",
        ),
        "c19_gap5_train": policy_report(
            "c19_gap5_train_nonvalidation",
            train_gap5_records,
            target_rank,
            "PUBLIC DIAGNOSTIC: non-validation c19 records with salt_gap == 5.",
        ),
        "c19_gap5_validation": policy_report(
            "c19_gap5_validation",
            validation_gap5_records,
            target_rank,
            "HELDOUT DIAGNOSTIC: validation c19 records with salt_gap == 5.",
        ),
        "c19_simple_two_factor_all": policy_report(
            "c19_simple_two_factor_all",
            simple_records,
            target_rank,
            "POST-REPLAY STRUCTURAL DIAGNOSTIC: c19 rows emitting a simple two-factor relation.",
        ),
        "c19_no_simple_two_factor": policy_report(
            "c19_no_simple_two_factor",
            no_simple_records,
            target_rank,
            "NEGATIVE CONTROL: c19 rows without the post-replay simple two-factor relation.",
        ),
    }
    gap5_rows = [compact_record(record) for record in gap5_records]
    simple_rows = [compact_record(record) for record in simple_records]
    no_simple_rows = [compact_record(record) for record in no_simple_records]
    validation_gap5_rows = [compact_record(record) for record in validation_gap5_records]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p919_source": str(args.p919_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(gap5_rows, simple_rows, no_simple_rows, validation_gap5_rows),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "STRUCTURAL-DIAGNOSTIC: simple relation signatures are observed after certificate replay and are not public pre-replay selectors.",
            "PUBLIC-GAP5-CLUE: salt_gap == 5 is public, but its observed precision still needs fresh-source validation.",
            "RANK-SIGNAL-NOT-DESCENT: c19 rank supply is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p920_c19_gap5_structural_signature",
        "parameters": {
            "c19_record_count": len(c19_records),
            "p919_best_policy": p919_best.get("name"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "positive_controls": [p919_full_report],
        "policy_reports": {name: compact_policy(report) for name, report in reports.items()},
        "schema": SCHEMA,
        "summary": {
            "c19_false_without_simple_count": sum(1 for row in no_simple_rows if not row.get("usable")),
            "c19_gap5_rows": gap5_rows,
            "c19_group_stats_by_gap": group_stats(c19_rows, "salt_gap"),
            "c19_group_stats_by_partition": group_stats(c19_rows, "partition"),
            "c19_no_simple_rows": no_simple_rows,
            "c19_row_count": len(c19_rows),
            "c19_signature_histogram": signature_histogram(c19_rows),
            "c19_simple_two_factor_precision": ratio(
                sum(1 for row in simple_rows if row.get("usable")),
                len(simple_rows),
            ),
            "c19_simple_two_factor_rows": simple_rows,
            "gap5_public_precision": ratio(
                sum(1 for row in gap5_rows if row.get("usable")),
                len(gap5_rows),
            ),
            "p919_best_policy_recomputed": compact_policy(p919_full_report),
            "validation_gap5_rows": validation_gap5_rows,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p919-source", type=Path, default=P919_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload.get("summary") or {}
    reports = payload.get("policy_reports") or {}
    print(
        "claim={claim} c19={c19} gap5_precision={gap5} simple_precision={simple} "
        "gap5_cost={gap5_cost} simple_count={simple_count} no_simple_false={no_simple_false} out={out}".format(
            claim=payload.get("claim_status"),
            c19=summary.get("c19_row_count"),
            gap5=summary.get("gap5_public_precision"),
            simple=summary.get("c19_simple_two_factor_precision"),
            gap5_cost=(reports.get("c19_gap5_all") or {}).get("charged_candidate_cost_ops"),
            simple_count=(reports.get("c19_simple_two_factor_all") or {}).get("selected_count"),
            no_simple_false=summary.get("c19_false_without_simple_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
