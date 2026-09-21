#!/usr/bin/env python3
"""P922 support-class cost audit for the c19 simple-signature predictor."""

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
import low_term_total2_p917_public_c8_residue_redteam as p917
import low_term_total2_p919_public_validation_rank_recovery as p919
import low_term_total2_p920_c19_gap5_structural_signature as p920
import low_term_total2_p921_c19_simple_public_predictor as p921


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p922_support_class_cost_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p922_support_class_cost_audit_probe.json"
P914_SOURCE = STATE_DIR / "low_term_total2_p914_archive_rank_growth_scout_probe.json"
P919_SOURCE = STATE_DIR / "low_term_total2_p919_public_validation_rank_recovery_probe.json"
P921_SOURCE = STATE_DIR / "low_term_total2_p921_c19_simple_public_predictor_probe.json"
SCHEMA = "ecdlp.low_term_total2_p922_support_class_cost_audit.v1"
VALIDATION_PARTITION = "p903_validation_1024_1103"
SUPPORT_CLASSES = {
    "A_0_2_rhs11025": {"support": [0, 2], "rhs": 11025},
    "B_1_2_rhs11023": {"support": [1, 2], "rhs": 11023},
}


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


def has_support_class(row: dict[str, Any], class_spec: dict[str, Any]) -> bool:
    support = tuple(class_spec["support"])
    rhs = int_value(class_spec["rhs"])
    return any(
        tuple(signature.get("factor_support") or []) == support
        and list(signature.get("support_values") or []) == [1, 1]
        and int_value(signature.get("canonical_rhs")) == rhs
        for signature in row.get("signature_keys") or []
    )


def selected_by_rule(rows: list[dict[str, Any]], predicate_names: list[str], atoms_by_name: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in rows if all(atoms_by_name[name](row) for name in predicate_names)]


def support_signature_histogram(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p921.signature_histogram(rows)


def support_rule_report(
    class_name: str,
    predicate_names: list[str],
    rows: list[dict[str, Any]],
    train_rows: list[dict[str, Any]],
    validation_rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
) -> dict[str, Any]:
    class_spec = SUPPORT_CLASSES[class_name]
    selected_all = selected_by_rule(rows, predicate_names, atoms_by_name)
    selected_train = selected_by_rule(train_rows, predicate_names, atoms_by_name)
    selected_validation = selected_by_rule(validation_rows, predicate_names, atoms_by_name)
    train_positive_count = sum(1 for row in train_rows if has_support_class(row, class_spec))
    validation_positive_count = sum(1 for row in validation_rows if has_support_class(row, class_spec))
    return {
        "all_selected_count": len(selected_all),
        "all_selected_indices": [row.get("index") for row in selected_all],
        "class_name": class_name,
        "name": "and__" + "__".join(predicate_names),
        "predicate_names": predicate_names,
        "selected_cost_ops": sum(int_value(row.get("charged_candidate_cost_ops")) for row in selected_all),
        "selected_signature_histogram": support_signature_histogram(selected_all),
        "train_false_positive_count": sum(1 for row in selected_train if not has_support_class(row, class_spec)),
        "train_recall": ratio(
            sum(1 for row in selected_train if has_support_class(row, class_spec)),
            train_positive_count,
        ),
        "train_selected_count": len(selected_train),
        "train_selected_indices": [row.get("index") for row in selected_train],
        "train_true_positive_count": sum(1 for row in selected_train if has_support_class(row, class_spec)),
        "validation_recall": ratio(
            sum(1 for row in selected_validation if has_support_class(row, class_spec)),
            validation_positive_count,
        )
        if validation_positive_count
        else None,
        "validation_selected_count": len(selected_validation),
        "validation_selected_indices": [row.get("index") for row in selected_validation],
        "validation_true_positive_count": sum(1 for row in selected_validation if has_support_class(row, class_spec)),
    }


def search_support_rules(
    class_name: str,
    rows: list[dict[str, Any]],
    atoms_by_name: dict[str, Any],
    require_validation_positive: bool,
) -> list[dict[str, Any]]:
    train_rows = [row for row in rows if row.get("partition") != VALIDATION_PARTITION]
    validation_rows = [row for row in rows if row.get("partition") == VALIDATION_PARTITION]
    names = list(atoms_by_name)
    reports: list[dict[str, Any]] = []
    for size in (1, 2):
        for combo in itertools.combinations(names, size):
            report = support_rule_report(
                class_name,
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
            if require_validation_positive and report["validation_true_positive_count"] <= 0:
                continue
            reports.append(report)
    reports.sort(
        key=lambda report: (
            -int_value(report.get("train_true_positive_count")),
            -float(report.get("train_recall") or 0.0),
            int_value(report.get("selected_cost_ops"), 10**12),
            len(report.get("predicate_names") or []),
            str(report.get("name")),
        )
    )
    return reports


def records_from_c19_indices(records: list[dict[str, Any]], indices: set[int]) -> list[dict[str, Any]]:
    return [record for record in records if int_value(record.get("index")) in indices and p916.short_clause(record) == "c19"]


def combined_policy_records(
    records: list[dict[str, Any]],
    selected_c19_indices: set[int],
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for record in records:
        name = p916.short_clause(record)
        cost = charged_cost(record)
        gap = salt_gap(record)
        transfer = transfer_index(record)
        if name == "c19" and int_value(record.get("index")) in selected_c19_indices:
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


def full_policy_report(
    name: str,
    records: list[dict[str, Any]],
    selected_c19_indices: set[int],
    target_rank: int,
) -> dict[str, Any]:
    return p915.policy_report(
        name,
        combined_policy_records(records, selected_c19_indices),
        "PUBLIC-PRE-REPLAY DIAGNOSTIC: support-class c19 rule(s) plus P919 c90/c8 rules.",
        target_rank,
        True,
    )


def find_best_full_candidate(
    records: list[dict[str, Any]],
    target_rank: int,
    class_a_rules: list[dict[str, Any]],
    class_b_rules: list[dict[str, Any]],
    p919_cost: int,
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    # B is optional: the A-class validation row is the mandatory P922 recovery target.
    for rule_a in class_a_rules[:120]:
        b_choices: list[dict[str, Any] | None] = [None] + class_b_rules[:80]
        for rule_b in b_choices:
            indices = set(int_value(index) for index in rule_a.get("all_selected_indices") or [])
            if rule_b:
                indices.update(int_value(index) for index in rule_b.get("all_selected_indices") or [])
            report = full_policy_report(
                "p922_support_class_policy",
                records,
                indices,
                target_rank,
            )
            compact = compact_policy(report)
            if int_value(compact.get("total_factor_rank")) < target_rank:
                continue
            if int_value(compact.get("false_selected_count")) != 0:
                continue
            candidates.append(
                {
                    "cost_saved_fraction_vs_p919": ratio(
                        p919_cost - int_value(compact.get("charged_candidate_cost_ops")),
                        p919_cost,
                    ),
                    "rule_a": rule_a,
                    "rule_b": rule_b,
                    "selected_c19_indices": sorted(indices),
                    "full_policy": compact,
                }
            )
    candidates.sort(
        key=lambda item: (
            int_value((item.get("full_policy") or {}).get("charged_candidate_cost_ops"), 10**12),
            int_value((item.get("full_policy") or {}).get("selected_count"), 10**12),
            str((item.get("rule_a") or {}).get("name")),
            str((item.get("rule_b") or {}).get("name")),
        )
    )
    return candidates[0] if candidates else {}


def determine_claim(best: dict[str, Any], p919_cost: int) -> str:
    if not best:
        return "NEGATIVE_RESULT_P922_NO_SUPPORT_CLASS_POLICY_PRESERVES_RANK6"
    cost = int_value(((best.get("full_policy") or {}).get("charged_candidate_cost_ops")), 10**12)
    if cost < p919_cost:
        return "P922_SUPPORT_CLASS_A_PREDICTOR_REDUCES_COST_VS_P919"
    return "P922_SUPPORT_CLASS_PREDICTOR_RANK6_BUT_NOT_COST_COMPETITIVE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p914_payload = load_json(args.p914_source)
    p919_payload = load_json(args.p919_source)
    p921_payload = load_json(args.p921_source)
    records = p915.records(p914_payload)
    target_rank = int_value((p914_payload.get("summary") or {}).get("selected_rank"), 6)
    source_by_ordinal = p921.source_cases_by_ordinal()
    c19_records = [record for record in records if p916.short_clause(record) == "c19"]
    public_rows = [
        p921.public_feature_row(record, source_by_ordinal[int_value((record.get("row") or {}).get("archive_stream_ordinal"))])
        for record in c19_records
    ]
    atoms_by_name = {name: fn for name, fn in p921.atom_list([row for row in public_rows if row.get("partition") != VALIDATION_PARTITION])}
    class_a_rules = search_support_rules("A_0_2_rhs11025", public_rows, atoms_by_name, True)
    class_b_rules = search_support_rules("B_1_2_rhs11023", public_rows, atoms_by_name, False)

    p917_records = p917.residue_policy_records(records, 11, {2, 4})
    p919_records = p919.policy_records(
        records,
        c19_extra_mode="gap_eq5",
        c19_extra_cost_cap=180,
        c90_gap_mode="gap_le3",
        c90_cost_cap=128,
    )
    p921_indices = set(
        int_value(index)
        for index in (((p921_payload.get("summary") or {}).get("best_rule") or {}).get("all_selected_indices") or [])
    )
    p917_report = p915.policy_report("p917_policy_recomputed", p917_records, "P917 control.", target_rank, True)
    p919_report = p915.policy_report("p919_best_policy_recomputed", p919_records, "P919 positive control.", target_rank, True)
    p921_report = full_policy_report("p921_broad_c19_policy_recomputed", records, p921_indices, target_rank)
    p919_cost = int_value(p919_report.get("charged_candidate_cost_ops"))
    best = find_best_full_candidate(records, target_rank, class_a_rules, class_b_rules, p919_cost)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p914_source": str(args.p914_source),
            "p919_source": str(args.p919_source),
            "p921_source": str(args.p921_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best, p919_cost),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "ARCHIVE-SCOUT: this uses the P914 archive-selected certificate set.",
            "PUBLIC-PREDICTOR-DIAGNOSTIC: support-class rules use public source features but are selected after seeing archive labels.",
            "FRESH-REPLAY-REQUIRED: freeze the reported support-class rule before treating any future validation as evidence.",
            "RANK-SIGNAL-NOT-DESCENT: rank 6 is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p922_support_class_cost_audit",
        "parameters": {
            "c19_record_count": len(public_rows),
            "class_a_rule_count": len(class_a_rules),
            "class_b_rule_count": len(class_b_rules),
            "p919_claim": p919_payload.get("claim_status"),
            "p921_claim": p921_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_rank": target_rank,
            "validation_partition": VALIDATION_PARTITION,
        },
        "policy_controls": {
            "p917": compact_policy(p917_report),
            "p919": compact_policy(p919_report),
            "p921": compact_policy(p921_report),
        },
        "schema": SCHEMA,
        "summary": {
            "best_full_candidate": best,
            "class_a_top_rules": class_a_rules[:12],
            "class_b_top_rules": class_b_rules[:12],
            "c19_public_rows": public_rows,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p914-source", type=Path, default=P914_SOURCE)
    parser.add_argument("--p919-source", type=Path, default=P919_SOURCE)
    parser.add_argument("--p921-source", type=Path, default=P921_SOURCE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    best = ((payload.get("summary") or {}).get("best_full_candidate") or {})
    full = best.get("full_policy") or {}
    rule_a = best.get("rule_a") or {}
    rule_b = best.get("rule_b") or None
    print(
        "claim={claim} A_rules={a_rules} B_rules={b_rules} best_cost={cost} best_rank={rank} "
        "selected={selected} saved_vs_p919={saved} A={a_name} B={b_name} out={out}".format(
            claim=payload.get("claim_status"),
            a_rules=(payload.get("parameters") or {}).get("class_a_rule_count"),
            b_rules=(payload.get("parameters") or {}).get("class_b_rule_count"),
            cost=full.get("charged_candidate_cost_ops"),
            rank=full.get("total_factor_rank"),
            selected=full.get("selected_count"),
            saved=best.get("cost_saved_fraction_vs_p919"),
            a_name=rule_a.get("name"),
            b_name=(rule_b or {}).get("name") if rule_b else None,
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
