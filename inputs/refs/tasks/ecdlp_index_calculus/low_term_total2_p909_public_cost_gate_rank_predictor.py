#!/usr/bin/env python3
"""P909 public cost-gate predictor over P908 row-set representatives."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p908_p907_public_rowset_dedup_rank_cost as p908


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p909_public_cost_gate_rank_predictor.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p909_public_cost_gate_rank_predictor_probe.json"
P908_SOURCE = STATE_DIR / "low_term_total2_p908_p907_public_rowset_dedup_rank_cost_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
SCHEMA = "ecdlp.low_term_total2_p909_public_cost_gate_rank_predictor.v1"


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


def public_rowset_representatives(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return p908.first_by_key(certificates, p908.rowset_key)


def charged_cost(cert: dict[str, Any]) -> int:
    return p908.charged_cost(cert)


def generator_cost(cert: dict[str, Any]) -> int:
    row = scheduled_row(cert)
    return int_value(row.get("generator_case_cost_ops"), max(1, charged_cost(cert) - 1))


def audit_policy(
    name: str,
    selected: list[dict[str, Any]],
    boundary: str,
    all_cost: int,
) -> dict[str, Any]:
    audits = p908.order_audits(selected)
    summary = p908.audit_summary(audits)
    cost = sum(charged_cost(cert) for cert in selected)
    return {
        "charged_cost_ops": cost,
        "charged_cost_over_rho": ratio(cost, p905.RHO_ESTIMATE),
        "cost_fraction_vs_p908_rowset": ratio(cost, all_cost),
        "cost_saved_fraction_vs_p908_rowset": ratio(all_cost - cost, all_cost),
        "discovery_boundary": boundary,
        "matrix_consistent": all(bool(audit.get("matrix_consistent")) for audit in audits.values()) if audits else True,
        "name": name,
        "order_audits": audits,
        "selected_certificate_count": len(selected),
        "selected_sample": [
            {
                "charged_cost_ops": charged_cost(cert),
                "clause": (cert.get("p907_selection") or {}).get("clause"),
                "generator_case_cost_ops": generator_cost(cert),
                "leaf_signature": scheduled_row(cert).get("leaf_signature"),
                "ops_over_rho": scheduled_row(cert).get("ops_over_rho"),
                "salt_gap": scheduled_row(cert).get("salt_gap"),
                "selector_group": scheduled_row(cert).get("selector_group"),
                "split": scheduled_row(cert).get("split"),
                "transfer_index": int_value(scheduled_row(cert).get("transfer_index")),
                "usable": p908.usable(cert),
            }
            for cert in selected[:20]
        ],
        "summary": summary,
        "usable_certificate_count": sum(1 for cert in selected if p908.usable(cert)),
    }


def policy_from_filter(
    name: str,
    representatives: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    boundary: str,
    all_cost: int,
) -> dict[str, Any]:
    return audit_policy(name, [cert for cert in representatives if predicate(cert)], boundary, all_cost)


def source_ops(cert: dict[str, Any]) -> float:
    return float_value(scheduled_row(cert).get("ops_over_rho"))


def salt_gap(cert: dict[str, Any]) -> int:
    return int_value(scheduled_row(cert).get("salt_gap"), -1)


def clause(cert: dict[str, Any]) -> str:
    return str((cert.get("p907_selection") or {}).get("clause") or scheduled_row(cert).get("clause"))


def selector_group(cert: dict[str, Any]) -> str:
    return str(scheduled_row(cert).get("selector_group"))


def leaf_signature(cert: dict[str, Any]) -> str:
    return str(scheduled_row(cert).get("leaf_signature"))


def rank_increment_oracle(representatives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    rank = 0
    for cert in representatives:
        if not p908.usable(cert):
            continue
        candidate = selected + [cert]
        candidate_rank = p908.audit_summary(p908.order_audits(candidate))["total_factor_rank"]
        if candidate_rank > rank:
            selected.append(cert)
            rank = candidate_rank
    return selected


def candidate_policy_reports(representatives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_cost = sum(charged_cost(cert) for cert in representatives)
    reports = [
        audit_policy(
            "p908_public_rowset_first_baseline",
            representatives,
            "PUBLIC-PRE-REPLAY BASELINE: one deterministic first certificate per public row-set key.",
            all_cost,
        )
    ]
    generator_thresholds = sorted({generator_cost(cert) for cert in representatives})
    for threshold in generator_thresholds:
        reports.append(
            policy_from_filter(
                f"public_generator_cost_le_{threshold}",
                representatives,
                lambda cert, threshold=threshold: generator_cost(cert) <= threshold,
                "PUBLIC-PRE-REPLAY: source generator cost is public metadata after source-case evaluation and is charged.",
                all_cost,
            )
        )
    charged_thresholds = sorted({charged_cost(cert) for cert in representatives})
    for threshold in charged_thresholds:
        reports.append(
            policy_from_filter(
                f"public_charged_cost_le_{threshold}",
                representatives,
                lambda cert, threshold=threshold: charged_cost(cert) <= threshold,
                "PUBLIC-PRE-REPLAY: charged source-case cost gate.",
                all_cost,
            )
        )
    for threshold in sorted({source_ops(cert) for cert in representatives}):
        reports.append(
            policy_from_filter(
                f"public_source_ops_le_{str(threshold).replace('.', 'p')}",
                representatives,
                lambda cert, threshold=threshold: source_ops(cert) <= threshold,
                "PUBLIC-PRE-REPLAY: source ops/rho metadata threshold.",
                all_cost,
            )
        )
    for threshold in sorted({salt_gap(cert) for cert in representatives}):
        reports.append(
            policy_from_filter(
                f"public_salt_gap_ge_{threshold}",
                representatives,
                lambda cert, threshold=threshold: salt_gap(cert) >= threshold,
                "PUBLIC-PRE-REPLAY: row-salt gap threshold.",
                all_cost,
            )
        )
        reports.append(
            policy_from_filter(
                f"public_salt_gap_le_{threshold}",
                representatives,
                lambda cert, threshold=threshold: salt_gap(cert) <= threshold,
                "PUBLIC-PRE-REPLAY: row-salt gap threshold.",
                all_cost,
            )
        )
    for value in sorted({clause(cert) for cert in representatives}):
        reports.append(
            policy_from_filter(
                f"public_clause_{value}",
                representatives,
                lambda cert, value=value: clause(cert) == value,
                "PUBLIC-PRE-REPLAY CONTROL: single P905 clause only.",
                all_cost,
            )
        )
    for value in sorted({selector_group(cert) for cert in representatives}):
        reports.append(
            policy_from_filter(
                f"public_selector_group_{value}",
                representatives,
                lambda cert, value=value: selector_group(cert) == value,
                "PUBLIC-PRE-REPLAY CONTROL: selector group only.",
                all_cost,
            )
        )
    for value in sorted({leaf_signature(cert) for cert in representatives}):
        reports.append(
            policy_from_filter(
                f"public_leaf_signature_{value.replace('/', '_')}",
                representatives,
                lambda cert, value=value: leaf_signature(cert) == value,
                "PUBLIC-PRE-REPLAY CONTROL: leaf signature only.",
                all_cost,
            )
        )
    reports.append(
        audit_policy(
            "post_replay_usable_rowset_diagnostic",
            [cert for cert in representatives if p908.usable(cert)],
            "POST-REPLAY DIAGNOSTIC: requires knowing public verification before source selection.",
            all_cost,
        )
    )
    reports.append(
        audit_policy(
            "rank_increment_oracle_diagnostic",
            rank_increment_oracle(representatives),
            "ORACLE DIAGNOSTIC: uses rank-increment outcome labels and is not a source policy.",
            all_cost,
        )
    )
    return reports


def is_public_pre_replay(report: dict[str, Any]) -> bool:
    boundary = str(report.get("discovery_boundary") or "")
    return "PUBLIC-PRE-REPLAY" in boundary


def rank(report: dict[str, Any]) -> int:
    return int_value((report.get("summary") or {}).get("total_factor_rank"))


def best_public_report(reports: list[dict[str, Any]], target_rank: int) -> dict[str, Any]:
    candidates = [
        report
        for report in reports
        if is_public_pre_replay(report)
        and bool(report.get("matrix_consistent"))
        and rank(report) >= target_rank
    ]
    if not candidates:
        return {}
    return min(candidates, key=lambda report: int_value(report.get("charged_cost_ops"), 10**12))


def determine_claim(best_public: dict[str, Any], baseline_cost: int, target_rank: int) -> str:
    if not best_public:
        return "NEGATIVE_RESULT_P909_NO_PUBLIC_POLICY_PRESERVES_RANK"
    if rank(best_public) < target_rank:
        return "NEGATIVE_RESULT_P909_PUBLIC_COST_GATE_LOSES_RANK"
    if int_value(best_public.get("charged_cost_ops")) < baseline_cost:
        return "P909_PUBLIC_COST_GATE_PRESERVES_RANK_AND_REDUCES_COST"
    return "NEGATIVE_RESULT_P909_PUBLIC_COST_GATE_NO_COST_IMPROVEMENT"


def representative_records(representatives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "charged_cost_ops": charged_cost(cert),
            "clause": clause(cert),
            "forms_count": int_value(cert.get("forms_count")),
            "generator_case_cost_ops": generator_cost(cert),
            "leaf_signature": leaf_signature(cert),
            "public_key_verified": bool(cert.get("public_key_verified")),
            "rank": int_value(cert.get("rank")),
            "salt_gap": salt_gap(cert),
            "selector": scheduled_row(cert).get("selector"),
            "selector_group": selector_group(cert),
            "source_ops_over_rho": source_ops(cert),
            "split": scheduled_row(cert).get("split"),
            "transfer_index": int_value(scheduled_row(cert).get("transfer_index")),
        }
        for cert in representatives
    ]


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p907_payload = load_json(args.p907_source)
    p908_payload = load_json(args.p908_source)
    certificates = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    representatives = public_rowset_representatives(certificates)
    reports = candidate_policy_reports(representatives)
    p908_best = ((p908_payload.get("summary") or {}).get("best_public_pre_replay_policy") or {})
    target_rank = int_value(p908_best.get("total_factor_rank"), 5)
    baseline_cost = int_value(p908_best.get("charged_cost_ops"), sum(charged_cost(cert) for cert in representatives))
    best_public = best_public_report(reports, target_rank)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "p908_source": str(args.p908_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(best_public, baseline_cost, target_rank),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "IN-SAMPLE: policies are fit and tested on existing P907/P908 certificates.",
            "PUBLIC-COST-FEATURE: generator/charged cost gates use public source-case metadata but are not free; selected costs are charged.",
            "POST-REPLAY and ORACLE policies are diagnostic lower bounds only.",
            "RANK-PREDICTOR-NOT-DESCENT: rank-preserving cost reduction is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p909_public_cost_gate_rank_predictor",
        "parameters": {
            "p908_baseline_cost_ops": baseline_cost,
            "p908_baseline_rank": target_rank,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
        },
        "policy_reports": reports,
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze the best public cost gate before fresh-window replay; then test usable/rank-increment "
                "recall without tuning on that window. Full-rank factor solve remains required before target descent."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "representative_records": representative_records(representatives),
        "schema": SCHEMA,
        "summary": {
            "best_public_policy": {
                "charged_cost_ops": best_public.get("charged_cost_ops"),
                "charged_cost_over_rho": best_public.get("charged_cost_over_rho"),
                "cost_saved_fraction_vs_p908_rowset": best_public.get("cost_saved_fraction_vs_p908_rowset"),
                "name": best_public.get("name"),
                "selected_certificate_count": best_public.get("selected_certificate_count"),
                "total_factor_rank": (best_public.get("summary") or {}).get("total_factor_rank"),
                "total_unique_factor_relation_count": (best_public.get("summary") or {}).get("total_unique_factor_relation_count"),
                "usable_certificate_count": best_public.get("usable_certificate_count"),
            },
            "policy_count": len(reports),
            "representative_count": len(representatives),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p907-source", type=Path, default=P907_SOURCE)
    parser.add_argument("--p908-source", type=Path, default=P908_SOURCE)
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
