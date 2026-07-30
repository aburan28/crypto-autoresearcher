#!/usr/bin/env python3
"""P911 mixed salt-gap policy audit repairing P910 split-rank loss."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p909_public_cost_gate_rank_predictor as p909


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p911_mixed_salt_gap_split_repair.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p911_mixed_salt_gap_split_repair_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
SCHEMA = "ecdlp.low_term_total2_p911_mixed_salt_gap_split_repair.v1"


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


def scheduled_row(cert: dict[str, Any]) -> dict[str, Any]:
    return p908.scheduled_row(cert)


def split(cert: dict[str, Any]) -> str:
    return str(scheduled_row(cert).get("split"))


def salt_gap(cert: dict[str, Any]) -> int:
    return p909.salt_gap(cert)


def charged_cost(cert: dict[str, Any]) -> int:
    return p908.charged_cost(cert)


def representatives(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p909.public_rowset_representatives(certificates)


def audit_selected(selected: list[dict[str, Any]]) -> dict[str, Any]:
    audits = p908.order_audits(selected)
    summary = p908.audit_summary(audits)
    cost = sum(charged_cost(cert) for cert in selected)
    return {
        "charged_cost_ops": cost,
        "charged_cost_over_rho": ratio(cost, p905.RHO_ESTIMATE),
        "matrix_consistent": all(bool(audit.get("matrix_consistent")) for audit in audits.values()) if audits else True,
        "order_audits": audits,
        "selected_certificate_count": len(selected),
        "selected_rows": [
            {
                "charged_cost_ops": charged_cost(cert),
                "clause": (cert.get("p907_selection") or {}).get("clause"),
                "leaf_signature": scheduled_row(cert).get("leaf_signature"),
                "salt_gap": salt_gap(cert),
                "selector": scheduled_row(cert).get("selector"),
                "split": split(cert),
                "transfer_index": int_value(scheduled_row(cert).get("transfer_index")),
                "usable": p908.usable(cert),
            }
            for cert in selected
        ],
        "summary": summary,
        "usable_certificate_count": sum(1 for cert in selected if p908.usable(cert)),
    }


def rank(report: dict[str, Any]) -> int:
    return int_value((report.get("summary") or {}).get("total_factor_rank"))


def unique_relations(report: dict[str, Any]) -> int:
    return int_value((report.get("summary") or {}).get("total_unique_factor_relation_count"))


def policy_eval(
    reps: list[dict[str, Any]],
    name: str,
    predicate: Callable[[dict[str, Any]], bool],
    boundary: str,
) -> dict[str, Any]:
    selected = [cert for cert in reps if predicate(cert)]
    return {
        "discovery_boundary": boundary,
        "name": name,
        **audit_selected(selected),
    }


def split_policy_reports(
    reps: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    return {
        str(split_name): audit_selected([cert for cert in reps if split(cert) == split_name and predicate(cert)])
        for split_name in p905.SPLITS
    }


def split_ranks(reports: dict[str, Any]) -> dict[str, int]:
    return {split_name: rank(report) for split_name, report in reports.items()}


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
    return all(rank(split_reports[split_name]) >= target_rank for split_name, target_rank in target_split_ranks.items())


def mixed_predicate(validation_low_gap_max: int, forward_low_gap_max: int) -> Callable[[dict[str, Any]], bool]:
    def predicate(cert: dict[str, Any]) -> bool:
        gap = salt_gap(cert)
        cert_split = split(cert)
        return (
            gap >= 5
            or (cert_split == "validation" and gap <= validation_low_gap_max)
            or (cert_split == "forward" and gap <= forward_low_gap_max)
        )

    return predicate


def candidate_policies(reps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    policies: list[dict[str, Any]] = [
        policy_eval(
            reps,
            "all_rowsets_baseline",
            lambda _cert: True,
            "PUBLIC-PRE-REPLAY BASELINE: P908 public row-set representatives.",
        ),
        policy_eval(
            reps,
            "salt_gap_ge_5_redteam_control",
            lambda cert: salt_gap(cert) >= 5,
            "PUBLIC-PRE-REPLAY CONTROL: P909 high-salt-gap gate, expected to fail split stability.",
        ),
        policy_eval(
            reps,
            "salt_gap_le_4_control",
            lambda cert: salt_gap(cert) <= 4,
            "PUBLIC-PRE-REPLAY CONTROL: opposite low-salt-gap gate.",
        ),
    ]
    for validation_gap in range(1, 5):
        for forward_gap in range(1, 5):
            name = f"mixed_salt_gap_ge5_or_validation_le{validation_gap}_or_forward_le{forward_gap}"
            policies.append(
                policy_eval(
                    reps,
                    name,
                    mixed_predicate(validation_gap, forward_gap),
                    "PUBLIC-PRE-REPLAY: high-salt-gap rows plus split-local low-salt-gap complements.",
                )
            )
    return policies


def choose_best(
    policies: list[dict[str, Any]],
    split_reports_by_policy: dict[str, dict[str, Any]],
    target_global_rank: int,
    target_split_ranks: dict[str, int],
) -> dict[str, Any]:
    valid = [
        policy
        for policy in policies
        if "PUBLIC-PRE-REPLAY" in str(policy.get("discovery_boundary"))
        and preserves_targets(policy, split_reports_by_policy[str(policy["name"])], target_global_rank, target_split_ranks)
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


def determine_claim(best: dict[str, Any], all_cost: int) -> str:
    if not best:
        return "NEGATIVE_RESULT_P911_NO_MIXED_POLICY_PRESERVES_SPLIT_RANK"
    if int_value(best.get("charged_cost_ops"), 10**12) < all_cost:
        return "P911_MIXED_SALT_GAP_POLICY_REPAIRS_SPLIT_RANK_WITH_COST_COMPRESSION"
    return "NEGATIVE_RESULT_P911_MIXED_POLICY_NO_COST_COMPRESSION"


def compact_policy(policy: dict[str, Any]) -> dict[str, Any]:
    return {
        "charged_cost_ops": policy.get("charged_cost_ops"),
        "charged_cost_over_rho": policy.get("charged_cost_over_rho"),
        "name": policy.get("name"),
        "selected_certificate_count": policy.get("selected_certificate_count"),
        "total_factor_rank": (policy.get("summary") or {}).get("total_factor_rank"),
        "total_unique_factor_relation_count": (policy.get("summary") or {}).get("total_unique_factor_relation_count"),
        "usable_certificate_count": policy.get("usable_certificate_count"),
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p907_payload = load_json(args.p907_source)
    certs = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    reps = representatives(certs)
    policies = candidate_policies(reps)
    split_reports_by_policy = {
        str(policy["name"]): split_policy_reports(
            reps,
            (lambda name: (
                (lambda cert: True)
                if name == "all_rowsets_baseline"
                else (lambda cert: salt_gap(cert) >= 5)
                if name == "salt_gap_ge_5_redteam_control"
                else (lambda cert: salt_gap(cert) <= 4)
                if name == "salt_gap_le_4_control"
                else mixed_predicate(
                    int(name.split("_validation_le", 1)[1].split("_", 1)[0]),
                    int(name.split("_forward_le", 1)[1]),
                )
            ))(str(policy["name"])),
        )
        for policy in policies
    }
    all_policy = next(policy for policy in policies if policy["name"] == "all_rowsets_baseline")
    target_global_rank = rank(all_policy)
    target_split_ranks = split_ranks(split_reports_by_policy["all_rowsets_baseline"])
    best = choose_best(policies, split_reports_by_policy, target_global_rank, target_split_ranks)
    sorted_policies = sorted(
        policies,
        key=lambda policy: (
            0
            if preserves_targets(
                policy,
                split_reports_by_policy[str(policy["name"])],
                target_global_rank,
                target_split_ranks,
            )
            else 1,
            int_value(policy.get("charged_cost_ops"), 10**12),
            str(policy.get("name")),
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best, int_value(all_policy.get("charged_cost_ops"))),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "IN-SAMPLE: mixed policy is tuned on P907/P908/P910 artifacts and is not fresh validation.",
            "PUBLIC-PRE-REPLAY: the selected policy uses only split and public salt-gap thresholds.",
            "RANK-STABILITY-NOT-DESCENT: split-rank preservation is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p911_mixed_salt_gap_split_repair",
        "parameters": {
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
                "Freeze the best mixed public salt-gap policy on the next fresh source window. "
                "If it preserves split rank there, continue rank accumulation toward full factor rank."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "split_reports_by_policy": split_reports_by_policy,
        "summary": {
            "all_rowsets_baseline": compact_policy(all_policy),
            "best_mixed_policy": compact_policy(best),
            "cost_saved_fraction_vs_all_rowsets": ratio(
                int_value(all_policy.get("charged_cost_ops")) - int_value(best.get("charged_cost_ops")),
                int_value(all_policy.get("charged_cost_ops")),
            )
            if best
            else None,
            "policy_count": len(policies),
            "top_policy_table": [compact_policy(policy) for policy in sorted_policies[:10]],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p907-source", type=Path, default=P907_SOURCE)
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
