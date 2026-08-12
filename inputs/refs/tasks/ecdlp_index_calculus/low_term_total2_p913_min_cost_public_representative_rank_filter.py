#!/usr/bin/env python3
"""P913 public representative replacement audit below the P912 cost."""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p911_mixed_salt_gap_split_repair as p911
import low_term_total2_p912_public_forward_false_row_filter as p912


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p913_min_cost_public_representative_rank_filter.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p913_min_cost_public_representative_rank_filter_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
P912_SOURCE = STATE_DIR / "low_term_total2_p912_public_forward_false_row_filter_probe.json"
SCHEMA = "ecdlp.low_term_total2_p913_min_cost_public_representative_rank_filter.v1"


Predicate = Callable[[dict[str, Any]], bool]


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p908.ratio(numerator, denominator)


def scheduled_row(cert: dict[str, Any]) -> dict[str, Any]:
    return p908.scheduled_row(cert)


def split(cert: dict[str, Any]) -> str:
    return p911.split(cert)


def salt_gap(cert: dict[str, Any]) -> int:
    return p911.salt_gap(cert)


def charged_cost(cert: dict[str, Any]) -> int:
    return p911.charged_cost(cert)


def generator_cost(cert: dict[str, Any]) -> int:
    row = scheduled_row(cert)
    return int_value(row.get("generator_case_cost_ops"), max(1, charged_cost(cert) - 1))


def source_ops(cert: dict[str, Any]) -> float:
    return float_value(scheduled_row(cert).get("ops_over_rho"))


def clause(cert: dict[str, Any]) -> str:
    return str((cert.get("p907_selection") or {}).get("clause") or scheduled_row(cert).get("clause"))


def leaf_signature(cert: dict[str, Any]) -> str:
    return str(scheduled_row(cert).get("leaf_signature"))


def transfer_index(cert: dict[str, Any]) -> int:
    return int_value(scheduled_row(cert).get("transfer_index"))


def selector_group(cert: dict[str, Any]) -> str:
    return str(scheduled_row(cert).get("selector_group"))


def slot_key(cert: dict[str, Any]) -> tuple[str, str, str]:
    return (split(cert), clause(cert), leaf_signature(cert))


def slot_name(key: tuple[str, str, str]) -> str:
    return "|".join(key)


def is_c90(cert: dict[str, Any]) -> bool:
    return clause(cert).startswith("c90_")


def is_p912_base(cert: dict[str, Any]) -> bool:
    return (
        p912.p911_mixed_base(cert)
        and not (split(cert) == "forward" and salt_gap(cert) >= 5 and source_ops(cert) > 0.70072993)
    )


def representatives(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p911.representatives(certificates)


def audit_selected(selected: list[dict[str, Any]]) -> dict[str, Any]:
    report = p912.audit_selected(selected)
    report["selected_rows"] = [
        {
            **row,
            "selector_group": selector_group(cert),
            "slot": slot_name(slot_key(cert)),
        }
        for row, cert in zip(report.get("selected_rows") or [], selected)
    ]
    return report


def rank(report: dict[str, Any]) -> int:
    return p911.rank(report)


def split_reports_for_selected(selected: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        str(split_name): audit_selected([cert for cert in selected if split(cert) == split_name])
        for split_name in p905.SPLITS
    }


def split_ranks(reports: dict[str, Any]) -> dict[str, int]:
    return {name: rank(report) for name, report in reports.items()}


def preserves_targets(
    global_report: dict[str, Any],
    split_reports: dict[str, Any],
    target_global_rank: int,
    target_split_ranks: dict[str, int],
) -> bool:
    if not bool(global_report.get("matrix_consistent")):
        return False
    if rank(global_report) < target_global_rank:
        return False
    return all(rank(split_reports[name]) >= target for name, target in target_split_ranks.items())


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "charged_cost_ops": policy.get("charged_cost_ops"),
        "charged_cost_over_rho": policy.get("charged_cost_over_rho"),
        "name": policy.get("name"),
        "promotable_source_policy": policy.get("promotable_source_policy"),
        "selected_certificate_count": policy.get("selected_certificate_count"),
        "target_preserving": policy.get("target_preserving"),
        "total_factor_rank": (policy.get("summary") or {}).get("total_factor_rank"),
        "total_unique_factor_relation_count": (policy.get("summary") or {}).get("total_unique_factor_relation_count"),
        "usable_certificate_count": policy.get("usable_certificate_count"),
    }


def policy_report(
    name: str,
    selected: list[dict[str, Any]],
    boundary: str,
    target_global_rank: int,
    target_split_ranks: dict[str, int],
    promotable: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    report = {
        "discovery_boundary": boundary,
        "name": name,
        "promotable_source_policy": promotable,
        **audit_selected(selected),
    }
    reports_by_split = split_reports_for_selected(selected)
    report["split_ranks"] = split_ranks(reports_by_split)
    report["target_preserving"] = preserves_targets(
        report, reports_by_split, target_global_rank, target_split_ranks
    )
    return report, reports_by_split


def choose_one_per_slot(
    reps: list[dict[str, Any]],
    baseline_selected: list[dict[str, Any]],
    include_predicate: Predicate,
    key_fn: Callable[[dict[str, Any]], tuple[Any, ...]],
) -> list[dict[str, Any]]:
    baseline_slots = {slot_key(cert) for cert in baseline_selected}
    selected = []
    for key in sorted(baseline_slots):
        candidates = [
            cert
            for cert in reps
            if slot_key(cert) == key and (is_p912_base(cert) or include_predicate(cert))
        ]
        if not candidates:
            continue
        selected.append(min(candidates, key=key_fn))
    return selected


def candidate_policy_specs() -> list[tuple[str, Predicate, Callable[[dict[str, Any]], tuple[Any, ...]], str]]:
    return [
        (
            "p912_plus_train_c90_lowgap_min_charged_per_slot",
            lambda cert: split(cert) == "train" and is_c90(cert) and salt_gap(cert) <= 4,
            lambda cert: (charged_cost(cert), generator_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY: P912 slots plus the train c90 low-gap public complement; choose the cheapest charged representative per slot.",
        ),
        (
            "p912_plus_train_forward_c90_lowgap_min_charged_per_slot",
            lambda cert: split(cert) in {"train", "forward"} and is_c90(cert) and salt_gap(cert) <= 4,
            lambda cert: (charged_cost(cert), generator_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY: P912 slots plus train/forward c90 low-gap public complements; choose the cheapest charged representative per slot.",
        ),
        (
            "p912_plus_all_c90_lowgap_min_charged_per_slot",
            lambda cert: is_c90(cert) and salt_gap(cert) <= 4,
            lambda cert: (charged_cost(cert), generator_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY: P912 slots plus all c90 low-gap public complements; choose the cheapest charged representative per slot.",
        ),
        (
            "p912_slot_min_charged_from_all_same_slot_reps",
            lambda cert: True,
            lambda cert: (charged_cost(cert), generator_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY CONTROL: choose the cheapest charged representative for every P912 split/clause/leaf slot.",
        ),
        (
            "p912_slot_min_source_ops_from_all_same_slot_reps",
            lambda cert: True,
            lambda cert: (source_ops(cert), charged_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY CONTROL: choose the lowest source-ops representative for every P912 split/clause/leaf slot.",
        ),
        (
            "p912_slot_first_transfer_from_all_same_slot_reps",
            lambda cert: True,
            lambda cert: (transfer_index(cert), charged_cost(cert)),
            "PUBLIC-PRE-REPLAY CONTROL: choose the earliest transfer representative for every P912 split/clause/leaf slot.",
        ),
        (
            "p912_slot_max_saltgap_from_all_same_slot_reps",
            lambda cert: True,
            lambda cert: (-salt_gap(cert), charged_cost(cert), transfer_index(cert)),
            "PUBLIC-PRE-REPLAY CONTROL: choose the largest salt-gap representative for every P912 split/clause/leaf slot.",
        ),
    ]


def brute_force_slot_oracle(
    reps: list[dict[str, Any]],
    baseline_selected: list[dict[str, Any]],
    target_global_rank: int,
    target_split_ranks: dict[str, int],
) -> list[dict[str, Any]]:
    baseline_slots = sorted({slot_key(cert) for cert in baseline_selected})
    choices_by_slot = [
        sorted([cert for cert in reps if slot_key(cert) == key], key=lambda cert: (charged_cost(cert), transfer_index(cert)))
        for key in baseline_slots
    ]
    best: list[dict[str, Any]] = []
    best_cost = 10**12
    for combo in itertools.product(*choices_by_slot):
        selected = list(combo)
        report = audit_selected(selected)
        if not preserves_targets(report, split_reports_for_selected(selected), target_global_rank, target_split_ranks):
            continue
        cost = int_value(report.get("charged_cost_ops"), 10**12)
        if cost < best_cost:
            best = selected
            best_cost = cost
    return best


def brute_force_subset_oracle(
    reps: list[dict[str, Any]],
    target_global_rank: int,
    target_split_ranks: dict[str, int],
) -> list[dict[str, Any]]:
    best: list[dict[str, Any]] = []
    best_cost = 10**12
    n = len(reps)
    for mask in range(1, 1 << n):
        selected = [reps[index] for index in range(n) if mask & (1 << index)]
        raw_cost = sum(charged_cost(cert) for cert in selected)
        if raw_cost >= best_cost:
            continue
        report = audit_selected(selected)
        if not preserves_targets(report, split_reports_for_selected(selected), target_global_rank, target_split_ranks):
            continue
        best = selected
        best_cost = raw_cost
    return best


def best_public_policy(policies: list[dict[str, Any]], baseline_cost: int) -> dict[str, Any]:
    valid = [
        policy
        for policy in policies
        if bool(policy.get("promotable_source_policy"))
        and bool(policy.get("target_preserving"))
        and int_value(policy.get("charged_cost_ops"), 10**12) < baseline_cost
    ]
    if not valid:
        return {}
    return min(
        valid,
        key=lambda policy: (
            int_value(policy.get("charged_cost_ops"), 10**12),
            int_value(policy.get("selected_certificate_count"), 10**12),
            str(policy.get("name")),
        ),
    )


def determine_claim(best: dict[str, Any]) -> str:
    if best:
        return "P913_PUBLIC_REPRESENTATIVE_REPLACEMENT_REDUCES_COST_WITHOUT_RANK_LOSS"
    return "NEGATIVE_RESULT_P913_NO_PUBLIC_REPRESENTATIVE_REPLACEMENT_BEATS_P912"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p907_payload = load_json(args.p907_source)
    p912_payload = load_json(args.p912_source)
    certs = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    reps = representatives(certs)

    baseline_selected = [cert for cert in reps if is_p912_base(cert)]
    baseline_report, baseline_split_reports = policy_report(
        "p912_baseline_recomputed",
        baseline_selected,
        "PUBLIC-PRE-REPLAY POSITIVE CONTROL: recompute the P912 source policy.",
        target_global_rank=5,
        target_split_ranks={"train": 2, "validation": 3, "forward": 3},
        promotable=True,
    )
    target_global_rank = rank(baseline_report)
    target_split_ranks = split_ranks(baseline_split_reports)
    baseline_cost = int_value(baseline_report.get("charged_cost_ops"), 10**12)

    policies = [baseline_report]
    split_reports_by_policy = {"p912_baseline_recomputed": baseline_split_reports}
    for name, include_predicate, key_fn, boundary in candidate_policy_specs():
        selected = choose_one_per_slot(reps, baseline_selected, include_predicate, key_fn)
        report, split_reports = policy_report(
            name,
            selected,
            boundary,
            target_global_rank,
            target_split_ranks,
            promotable=True,
        )
        policies.append(report)
        split_reports_by_policy[name] = split_reports

    slot_oracle_selected = brute_force_slot_oracle(reps, baseline_selected, target_global_rank, target_split_ranks)
    slot_oracle, slot_oracle_split_reports = policy_report(
        "slot_replacement_rank_oracle_diagnostic",
        slot_oracle_selected,
        "ORACLE DIAGNOSTIC: uses rank outcomes to choose among same-slot representatives; not a source policy.",
        target_global_rank,
        target_split_ranks,
        promotable=False,
    )
    subset_oracle_selected = brute_force_subset_oracle(reps, target_global_rank, target_split_ranks)
    subset_oracle, subset_oracle_split_reports = policy_report(
        "all_representatives_subset_rank_oracle_diagnostic",
        subset_oracle_selected,
        "ORACLE DIAGNOSTIC: uses rank outcomes and verifier labels over all representatives; not a source policy.",
        target_global_rank,
        target_split_ranks,
        promotable=False,
    )
    diagnostics = [slot_oracle, subset_oracle]
    split_reports_by_policy[slot_oracle["name"]] = slot_oracle_split_reports
    split_reports_by_policy[subset_oracle["name"]] = subset_oracle_split_reports

    best_public = best_public_policy(policies, baseline_cost)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "p912_source": str(args.p912_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best_public),
        "created_at": now_iso(),
        "diagnostic_reports": diagnostics,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "IN-SAMPLE: public representative rules are tested on existing P907/P912 artifacts.",
            "PUBLIC-PRE-REPLAY: promotable policies use split, clause, leaf signature, salt gap, source-cost metadata, and transfer ordering.",
            "DIAGNOSTIC-ORACLE-BOUNDARY: oracle reports use rank or verifier outcomes and cannot be promoted as source policies.",
            "RANK-FILTER-NOT-DESCENT: preserving rank at lower cost is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p913_min_cost_public_representative_rank_filter",
        "parameters": {
            "p912_claim": p912_payload.get("claim_status"),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
            "target_global_rank": target_global_rank,
            "target_split_ranks": target_split_ranks,
        },
        "policy_reports": policies,
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze any surviving public representative replacement on fresh source windows, then continue "
                "rank accumulation toward full factor rank before individual-log descent."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "split_reports_by_policy": split_reports_by_policy,
        "summary": {
            "baseline_policy": compact_policy(baseline_report),
            "best_diagnostic": compact_policy(min(diagnostics, key=lambda policy: int_value(policy.get("charged_cost_ops"), 10**12))),
            "best_public_policy": compact_policy(best_public),
            "cost_saved_fraction_vs_p912": ratio(
                baseline_cost - int_value(best_public.get("charged_cost_ops")),
                baseline_cost,
            )
            if best_public
            else None,
            "diagnostic_policy_count": len(diagnostics),
            "policy_count": len(policies),
            "representative_count": len(reps),
            "top_public_policy_table": [
                compact_policy(policy)
                for policy in sorted(
                    policies,
                    key=lambda policy: (
                        not bool(policy.get("target_preserving")),
                        int_value(policy.get("charged_cost_ops"), 10**12),
                        str(policy.get("name")),
                    ),
                )[:8]
            ],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p907-source", type=Path, default=P907_SOURCE)
    parser.add_argument("--p912-source", type=Path, default=P912_SOURCE)
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
