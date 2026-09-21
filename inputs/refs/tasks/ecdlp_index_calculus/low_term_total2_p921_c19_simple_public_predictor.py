#!/usr/bin/env python3
"""P921 public predictor audit for the P920 c19 simple signature."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p914_archive_rank_growth_scout as p914
import low_term_total2_p915_archive_rank6_cost_compression as p915
import low_term_total2_p916_public_rank_increment_predictor as p916
import low_term_total2_p917_public_c8_residue_redteam as p917
import low_term_total2_p918_p917_partition_stress as p918
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p920_c19_gap5_structural_signature as p920


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p921_c19_simple_public_predictor.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p921_c19_simple_public_predictor_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P919_SOURCE = STATE_DIR / "low_term_total2_p919_public_validation_rank_recovery_probe.json"
P920_SOURCE = STATE_DIR / "low_term_total2_p920_c19_gap5_structural_signature_probe.json"
SCHEMA = "ecdlp.low_term_total2_p921_c19_simple_public_predictor.v1"
VALIDATION_PARTITION = "p903_validation_1024_1103"


FeatureFn = Callable[[dict[str, Any]], bool]


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


def is_c19(record: dict[str, Any]) -> bool:
    return p916.short_clause(record) == "c19"


def is_validation(record: dict[str, Any]) -> bool:
    return p918.partition_name(record) == VALIDATION_PARTITION


def source_cases_by_ordinal() -> dict[int, dict[str, Any]]:
    return {
        int_value(candidate["source_case"].get("archive_stream_ordinal")): candidate["source_case"]
        for candidate in p914.all_candidates(p914.archive_source_paths(STATE_DIR))
    }


def public_feature_row(record: dict[str, Any], source_case: dict[str, Any]) -> dict[str, Any]:
    salts = [int_value(value) for value in source_case.get("row_salts") or []]
    signatures = p920.relation_signatures(record)
    simple_signatures = [
        signature
        for signature in signatures
        if signature["factor_support_size"] == 2 and signature["support_values"] == [1, 1]
    ]
    return {
        "archive_stream_ordinal": (record.get("row") or {}).get("archive_stream_ordinal"),
        "charged_candidate_cost_ops": charged_cost(record),
        "has_simple_two_factor_relation": bool(simple_signatures),
        "index": record.get("index"),
        "ops_over_rho": (record.get("row") or {}).get("ops_over_rho"),
        "partition": p918.partition_name(record),
        "policy": source_case.get("policy"),
        "public_key_verified": (record.get("cert") or {}).get("public_key_verified"),
        "rank": (record.get("cert") or {}).get("rank"),
        "row_selector": source_case.get("row_selector"),
        "row_salts": salts,
        "salt_gap": salt_gap(record),
        "selected_leaf_count": source_case.get("selected_leaf_count"),
        "selected_row_count": source_case.get("selected_row_count"),
        "signature_keys": [
            {
                "canonical_rhs": signature["canonical_rhs"],
                "factor_support": signature["factor_support"],
                "support_values": signature["support_values"],
            }
            for signature in simple_signatures
        ],
        "source_index": source_case.get("source_index"),
        "source_path": source_case.get("source_path"),
        "source_verified": source_case.get("source_verified"),
        "strict_below_rho": (record.get("row") or {}).get("strict_below_rho"),
        "top_k": (record.get("row") or {}).get("top_k"),
        "transfer_index": transfer_index(record),
        "usable": p920.is_usable(record),
    }


def salt_sum(row: dict[str, Any]) -> int:
    return sum(int_value(value) for value in row.get("row_salts") or [])


def salt_min(row: dict[str, Any]) -> int:
    salts = [int_value(value) for value in row.get("row_salts") or []]
    return min(salts) if salts else -1


def salt_max(row: dict[str, Any]) -> int:
    salts = [int_value(value) for value in row.get("row_salts") or []]
    return max(salts) if salts else -1


def atom_list(train_rows: list[dict[str, Any]]) -> list[tuple[str, FeatureFn]]:
    atoms: list[tuple[str, FeatureFn]] = []

    def add(name: str, fn: FeatureFn) -> None:
        atoms.append((name, fn))

    for gap in sorted({int_value(row.get("salt_gap")) for row in train_rows}):
        add(f"gap_eq_{gap}", lambda row, gap=gap: int_value(row.get("salt_gap")) == gap)
        add(f"gap_ne_{gap}", lambda row, gap=gap: int_value(row.get("salt_gap")) != gap)
        add(f"gap_le_{gap}", lambda row, gap=gap: int_value(row.get("salt_gap")) <= gap)
        add(f"gap_ge_{gap}", lambda row, gap=gap: int_value(row.get("salt_gap")) >= gap)
    for cost in sorted({int_value(row.get("charged_candidate_cost_ops")) for row in train_rows}):
        add(f"cost_le_{cost}", lambda row, cost=cost: int_value(row.get("charged_candidate_cost_ops")) <= cost)
        add(f"cost_ge_{cost}", lambda row, cost=cost: int_value(row.get("charged_candidate_cost_ops")) >= cost)
    for ops in sorted({row.get("ops_over_rho") for row in train_rows}):
        add(f"ops_eq_{ops}", lambda row, ops=ops: row.get("ops_over_rho") == ops)
    for policy in sorted({str(row.get("policy")) for row in train_rows}):
        add(f"policy_{policy}", lambda row, policy=policy: str(row.get("policy")) == policy)
    for selector in sorted({str(row.get("row_selector")) for row in train_rows}):
        add(f"row_selector_{selector}", lambda row, selector=selector: str(row.get("row_selector")) == selector)
    for m in range(2, 17):
        for remainder in sorted({int_value(row.get("transfer_index")) % m for row in train_rows}):
            add(
                f"transfer_mod{m}_eq_{remainder}",
                lambda row, m=m, remainder=remainder: int_value(row.get("transfer_index")) % m == remainder,
            )
        for remainder in sorted({int_value(row.get("source_index")) % m for row in train_rows}):
            add(
                f"source_index_mod{m}_eq_{remainder}",
                lambda row, m=m, remainder=remainder: int_value(row.get("source_index")) % m == remainder,
            )
        for remainder in sorted({salt_sum(row) % m for row in train_rows}):
            add(
                f"salt_sum_mod{m}_eq_{remainder}",
                lambda row, m=m, remainder=remainder: salt_sum(row) % m == remainder,
            )
        for remainder in sorted({salt_min(row) % m for row in train_rows}):
            add(
                f"salt_min_mod{m}_eq_{remainder}",
                lambda row, m=m, remainder=remainder: salt_min(row) % m == remainder,
            )
        for remainder in sorted({salt_max(row) % m for row in train_rows}):
            add(
                f"salt_max_mod{m}_eq_{remainder}",
                lambda row, m=m, remainder=remainder: salt_max(row) % m == remainder,
            )
    return atoms


def selected_by_rule(rows: list[dict[str, Any]], names: list[str], atoms_by_name: dict[str, FeatureFn]) -> list[dict[str, Any]]:
    return [row for row in rows if all(atoms_by_name[name](row) for name in names)]


def rule_report(
    name: str,
    predicate_names: list[str],
    rows: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, FeatureFn],
) -> dict[str, Any]:
    train_selected = selected_by_rule(train_rows, predicate_names, atoms_by_name)
    validation_selected = selected_by_rule(validation_rows, predicate_names, atoms_by_name)
    all_selected = selected_by_rule(rows, predicate_names, atoms_by_name)
    train_positive_count = sum(1 for row in train_rows if row.get("has_simple_two_factor_relation"))
    validation_positive_count = sum(1 for row in validation_rows if row.get("has_simple_two_factor_relation"))
    return {
        "all_selected_count": len(all_selected),
        "all_selected_indices": [row.get("index") for row in all_selected],
        "name": name,
        "predicate_names": predicate_names,
        "selected_signature_histogram": signature_histogram(all_selected),
        "train_false_positive_count": sum(1 for row in train_selected if not row.get("has_simple_two_factor_relation")),
        "train_recall": ratio(
            sum(1 for row in train_selected if row.get("has_simple_two_factor_relation")),
            train_positive_count,
        ),
        "train_selected_count": len(train_selected),
        "train_selected_indices": [row.get("index") for row in train_selected],
        "train_true_positive_count": sum(1 for row in train_selected if row.get("has_simple_two_factor_relation")),
        "validation_recall": ratio(
            sum(1 for row in validation_selected if row.get("has_simple_two_factor_relation")),
            validation_positive_count,
        ),
        "validation_selected_count": len(validation_selected),
        "validation_selected_indices": [row.get("index") for row in validation_selected],
        "validation_true_positive_count": sum(1 for row in validation_selected if row.get("has_simple_two_factor_relation")),
    }


def signature_histogram(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[Any, ...]] = Counter()
    for row in rows:
        for signature in row.get("signature_keys") or []:
            key = (
                tuple(signature.get("factor_support") or []),
                tuple(signature.get("support_values") or []),
                int_value(signature.get("canonical_rhs")),
            )
            counts[key] += 1
    return [
        {
            "canonical_rhs": key[2],
            "count": count,
            "factor_support": list(key[0]),
            "support_values": list(key[1]),
        }
        for key, count in counts.most_common()
    ]


def search_rules(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, FeatureFn]]:
    train_rows = [row for row in rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in rows if row.get("partition") == VALIDATION_PARTITION]
    atoms = atom_list(train_rows)
    atoms_by_name = {name: fn for name, fn in atoms}
    reports: list[dict[str, Any]] = []
    for size in (1, 2):
        for combo in itertools.combinations([name for name, _fn in atoms], size):
            report = rule_report(
                "and__" + "__".join(combo),
                list(combo),
                rows,
                train_rows,
                validation_rows,
                atoms_by_name,
            )
            if report["train_selected_count"] == 0:
                continue
            if report["train_false_positive_count"] != 0:
                continue
            if report["validation_true_positive_count"] <= 0:
                continue
            reports.append(report)
    reports.sort(
        key=lambda report: (
            -int_value(report.get("train_true_positive_count")),
            -float(report.get("train_recall") or 0.0),
            int_value(report.get("train_selected_count")),
            len(report.get("predicate_names") or []),
            str(report.get("name")),
        )
    )
    return reports, atoms_by_name


def c19_predicate_from_public_rows(record: dict[str, Any], rows_by_index: dict[int, dict[str, Any]], best_rule: dict[str, Any], atoms_by_name: dict[str, FeatureFn]) -> bool:
    if not is_c19(record):
        return False
    row = rows_by_index.get(int_value(record.get("index")))
    if row is None:
        return False
    return all(atoms_by_name[name](row) for name in best_rule.get("predicate_names") or [])


def full_policy_records(
    records: list[dict[str, Any]],
    rows_by_index: dict[int, dict[str, Any]],
    best_rule: dict[str, Any],
    atoms_by_name: dict[str, FeatureFn],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for record in records:
        name = p916.short_clause(record)
        cost = charged_cost(record)
        gap = salt_gap(record)
        transfer = transfer_index(record)
        if name == "c19" and c19_predicate_from_public_rows(record, rows_by_index, best_rule, atoms_by_name):
            selected.append(record)
        elif name == "c90" and cost <= 128 and gap <= 3:
            selected.append(record)
        elif name == "c8" and cost <= 150 and gap >= 10 and transfer % 11 in {2, 4}:
            selected.append(record)
    return selected


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    out = p915.compact_policy(policy)
    out["false_selected_count"] = int_value(policy.get("selected_count")) - int_value(policy.get("usable_certificate_count"))
    return out


def determine_claim(best_rule: dict[str, Any], p919_cost: int, full_cost: int) -> str:
    if not best_rule:
        return "NEGATIVE_RESULT_P921_NO_PUBLIC_C19_SIMPLE_PREDICTOR"
    recall = float(best_rule.get("train_recall") or 0.0)
    if recall >= 0.5 and full_cost <= p919_cost:
        return "P921_PUBLIC_C19_SIMPLE_PREDICTOR_TRAIN_CLEAN_AND_COST_COMPETITIVE"
    if recall >= 0.5:
        return "P921_PUBLIC_C19_SIMPLE_PREDICTOR_TRAIN_CLEAN_VALIDATION_POSITIVE"
    return "P921_PUBLIC_C19_SIMPLE_PREDICTOR_LOW_RECALL_ONLY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p919_payload = load_json(args.p919_source)
    p920_payload = load_json(args.p920_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    source_by_ordinal = source_cases_by_ordinal()
    c19_records = [record for record in records if is_c19(record)]
    public_rows = [
        public_feature_row(record, source_by_ordinal[int_value((record.get("row") or {}).get("archive_stream_ordinal"))])
        for record in c19_records
    ]
    rule_reports, atoms_by_name = search_rules(public_rows)
    best_rule = rule_reports[0] if rule_reports else {}
    rows_by_index = {int_value(row.get("index")): row for row in public_rows}
    p917_records = p917.residue_policy_records(records, 11, {2, 4})
    p919_records = p919.policy_records(
        records,
        c19_extra_mode="gap_eq5",
        c19_extra_cost_cap=180,
        c90_gap_mode="gap_le3",
        c90_cost_cap=128,
    )
    p921_records = full_policy_records(records, rows_by_index, best_rule, atoms_by_name) if best_rule else []
    p917_report = p915.policy_report("p917_policy_recomputed", p917_records, "P917 control.", target_rank, True)
    p919_report = p915.policy_report("p919_best_policy_recomputed", p919_records, "P919 positive control.", target_rank, True)
    p921_report = p915.policy_report(
        "p921_best_c19_predictor_plus_p919_c90_c8",
        p921_records,
        "PUBLIC-PRE-REPLAY DIAGNOSTIC: best train-clean c19 simple predictor plus P919 c90/c8 rules.",
        target_rank,
        True,
    )
    p919_cost = int_value(p919_report.get("charged_candidate_cost_ops"))
    p921_cost = int_value(p921_report.get("charged_candidate_cost_ops"))
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p919_source": str(args.p919_source),
            "p920_source": str(args.p920_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best_rule, p919_cost, p921_cost),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "PUBLIC-PREDICTOR-DIAGNOSTIC: rules use public source features but are selected after seeing archive labels.",
            "FRESH-REPLAY-REQUIRED: freeze the reported rule before treating any future validation as evidence.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p921_c19_simple_public_predictor",
        "parameters": {
            "c19_record_count": len(public_rows),
            "p919_claim": p919_payload.get("claim_status"),
            "p920_claim": p920_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p917": compact_policy(p917_report),
            "p919": compact_policy(p919_report),
            "p921_full_policy": compact_policy(p921_report),
        },
        "schema": SCHEMA,
        "summary": {
            "best_rule": best_rule,
            "c19_public_rows": public_rows,
            "p921_selected_rows": [
                p920.compact_record(record)
                for record in p921_records
            ],
            "rule_count_train_clean_validation_positive": len(rule_reports),
            "top_rules": rule_reports[:12],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p919-source", type=Path, default=P919_SOURCE)
    parser.add_argument("--p920-source", type=Path, default=P920_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    best = (payload.get("summary") or {}).get("best_rule") or {}
    controls = payload.get("policy_controls") or {}
    p921 = controls.get("p921_full_policy") or {}
    print(
        "claim={claim} rules={rules} best={best} train_tp={tp} train_recall={recall} "
        "validation_tp={vtp} full_cost={cost} full_rank={rank} false={false} out={out}".format(
            claim=payload.get("claim_status"),
            rules=(payload.get("summary") or {}).get("rule_count_train_clean_validation_positive"),
            best=best.get("name"),
            tp=best.get("train_true_positive_count"),
            recall=best.get("train_recall"),
            vtp=best.get("validation_true_positive_count"),
            cost=p921.get("charged_candidate_cost_ops"),
            rank=p921.get("total_factor_rank"),
            false=p921.get("false_selected_count"),
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
