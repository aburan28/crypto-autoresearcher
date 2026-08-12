#!/usr/bin/env python3
"""P912 public filter for the remaining P911 forward false row."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908
import low_term_total2_p909_public_cost_gate_rank_predictor as p909
import low_term_total2_p911_mixed_salt_gap_split_repair as p911


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p912_public_forward_false_row_filter.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p912_public_forward_false_row_filter_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
P911_SOURCE = STATE_DIR / "low_term_total2_p911_mixed_salt_gap_split_repair_probe.json"
SCHEMA = "ecdlp.low_term_total2_p912_public_forward_false_row_filter.v1"


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


def p911_mixed_base(cert: dict[str, Any]) -> bool:
    gap = salt_gap(cert)
    cert_split = split(cert)
    return gap >= 5 or (cert_split == "validation" and gap <= 1) or (cert_split == "forward" and gap <= 1)


def is_forward_highgap_false_candidate(cert: dict[str, Any]) -> bool:
    return (
        split(cert) == "forward"
        and salt_gap(cert) >= 5
        and clause(cert) == "c8_gap8_top7_lowleaf_hybrid_opsge0p70"
        and leaf_signature(cert) == "8/8"
    )


def representatives(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p911.representatives(certificates)


def audit_selected(selected: list[dict[str, Any]]) -> dict[str, Any]:
    report = p911.audit_selected(selected)
    report["selected_rows"] = [
        {
            **row,
            "generator_case_cost_ops": generator_cost(cert),
            "source_ops_over_rho": source_ops(cert),
        }
        for row, cert in zip(report.get("selected_rows") or [], selected)
    ]
    return report


def rank(report: dict[str, Any]) -> int:
    return p911.rank(report)


def policy_eval(
    reps: list[dict[str, Any]],
    name: str,
    predicate: Callable[[dict[str, Any]], bool],
    boundary: str,
) -> dict[str, Any]:
    selected = [cert for cert in reps if predicate(cert)]
    return {"discovery_boundary": boundary, "name": name, **audit_selected(selected)}


def split_reports(
    reps: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    return {
        str(split_name): audit_selected([cert for cert in reps if split(cert) == split_name and predicate(cert)])
        for split_name in p905.SPLITS
    }


def split_ranks(reports: dict[str, Any]) -> dict[str, int]:
    return {name: rank(report) for name, report in reports.items()}


def preserves_targets(
    policy: dict[str, Any],
    policy_split_reports: dict[str, Any],
    target_global_rank: int,
    target_split_ranks: dict[str, int],
) -> bool:
    if not bool(policy.get("matrix_consistent")):
        return False
    if rank(policy) < target_global_rank:
        return False
    return all(rank(policy_split_reports[split_name]) >= target_rank for split_name, target_rank in target_split_ranks.items())


def exclusion_predicates() -> list[tuple[str, Callable[[dict[str, Any]], bool], str]]:
    return [
        (
            "p911_mixed_baseline",
            lambda cert: p911_mixed_base(cert),
            "PUBLIC-PRE-REPLAY BASELINE: P911 mixed salt-gap policy.",
        ),
        (
            "mixed_exclude_forward_highgap_c8_source_ops_gt_0p70",
            lambda cert: p911_mixed_base(cert)
            and not (is_forward_highgap_false_candidate(cert) and source_ops(cert) > 0.70072993),
            "PUBLIC-PRE-REPLAY: exclude forward high-gap c8 rows with source_ops above the base 0.70072993 level.",
        ),
        (
            "mixed_exclude_forward_highgap_c8_generator_cost_gt_200",
            lambda cert: p911_mixed_base(cert)
            and not (is_forward_highgap_false_candidate(cert) and generator_cost(cert) > 200),
            "PUBLIC-PRE-REPLAY: exclude forward high-gap c8 rows with high generator cost.",
        ),
        (
            "mixed_exclude_forward_highgap_c8_charged_cost_gt_200",
            lambda cert: p911_mixed_base(cert)
            and not (is_forward_highgap_false_candidate(cert) and charged_cost(cert) > 200),
            "PUBLIC-PRE-REPLAY: exclude forward high-gap c8 rows with high charged cost.",
        ),
        (
            "mixed_forward_c8_requires_salt_gap_ge_11",
            lambda cert: p911_mixed_base(cert)
            and not (is_forward_highgap_false_candidate(cert) and salt_gap(cert) < 11),
            "PUBLIC-PRE-REPLAY: require stricter salt gap for forward c8 high-gap rows.",
        ),
        (
            "mixed_exclude_all_forward_highgap_source_ops_gt_0p70",
            lambda cert: p911_mixed_base(cert)
            and not (split(cert) == "forward" and salt_gap(cert) >= 5 and source_ops(cert) > 0.70072993),
            "PUBLIC-PRE-REPLAY CONTROL: broader forward high-gap source_ops exclusion.",
        ),
        (
            "mixed_exclude_all_highgap_source_ops_gt_0p70",
            lambda cert: p911_mixed_base(cert)
            and not (salt_gap(cert) >= 5 and source_ops(cert) > 0.70072993),
            "PUBLIC-PRE-REPLAY CONTROL: global high-gap source_ops exclusion, expected to risk validation rank.",
        ),
    ]


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


def determine_claim(best: dict[str, Any], baseline_cost: int) -> str:
    if not best:
        return "NEGATIVE_RESULT_P912_NO_PUBLIC_FALSE_ROW_FILTER_PRESERVES_RANK"
    if int_value(best.get("charged_cost_ops"), 10**12) < baseline_cost:
        return "P912_PUBLIC_FORWARD_FALSE_ROW_FILTER_REDUCES_COST_WITHOUT_RANK_LOSS"
    return "NEGATIVE_RESULT_P912_PUBLIC_FALSE_ROW_FILTER_NO_COST_REDUCTION"


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
    p911_payload = load_json(args.p911_source)
    certs = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    reps = representatives(certs)
    policies = [policy_eval(reps, name, pred, boundary) for name, pred, boundary in exclusion_predicates()]
    split_reports_by_policy = {
        name: split_reports(reps, pred) for name, pred, _boundary in exclusion_predicates()
    }
    baseline = next(policy for policy in policies if policy["name"] == "p911_mixed_baseline")
    target_global_rank = rank(baseline)
    target_split_ranks = split_ranks(split_reports_by_policy["p911_mixed_baseline"])
    best = choose_best(policies, split_reports_by_policy, target_global_rank, target_split_ranks)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "p911_source": str(args.p911_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best, int_value(baseline.get("charged_cost_ops"))),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "IN-SAMPLE: public filters are tested on existing P907/P911 artifacts.",
            "PUBLIC-PRE-REPLAY: promoted filters use only split, clause, leaf signature, salt gap, and public source-cost metadata.",
            "RANK-FILTER-NOT-DESCENT: preserving rank after removing a false row is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p912_public_forward_false_row_filter",
        "parameters": {
            "p911_claim": p911_payload.get("claim_status"),
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
                "Freeze the best public false-row filter on fresh source windows. "
                "If it holds, continue rank accumulation toward full factor rank."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "split_reports_by_policy": split_reports_by_policy,
        "summary": {
            "baseline_policy": compact_policy(baseline),
            "best_policy": compact_policy(best),
            "cost_saved_fraction_vs_p911": ratio(
                int_value(baseline.get("charged_cost_ops")) - int_value(best.get("charged_cost_ops")),
                int_value(baseline.get("charged_cost_ops")),
            )
            if best
            else None,
            "policy_count": len(policies),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p907-source", type=Path, default=P907_SOURCE)
    parser.add_argument("--p911-source", type=Path, default=P911_SOURCE)
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
