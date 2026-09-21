#!/usr/bin/env python3
"""P908 public row-set dedup audit over P907 certificates."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p906_p905_first_stop_certificate_rank_audit as p906
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p908_p907_public_rowset_dedup_rank_cost.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p908_p907_public_rowset_dedup_rank_cost_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
SCHEMA = "ecdlp.low_term_total2_p908_p907_public_rowset_dedup_rank_cost.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def charged_cost(cert: dict[str, Any]) -> int:
    selection = cert.get("p907_selection") if isinstance(cert.get("p907_selection"), dict) else {}
    return int_value(selection.get("charged_candidate_cost_ops"), 1)


def scheduled_row(cert: dict[str, Any]) -> dict[str, Any]:
    row = cert.get("p905_scheduled_row")
    return row if isinstance(row, dict) else {}


def rowset_key(cert: dict[str, Any]) -> tuple[Any, ...]:
    row = scheduled_row(cert)
    return (
        str(row.get("split")),
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        str(row.get("leaf_signature")),
        tuple(p906.normalize_row_leaf_keys(row.get("row_leaf_keys") or [])),
    )


def transfer_leaf_key(cert: dict[str, Any]) -> tuple[Any, ...]:
    row = scheduled_row(cert)
    return (
        str(row.get("split")),
        str(row.get("target")),
        int_value(row.get("transfer_index")),
        str(row.get("leaf_signature")),
    )


def exact_selector_key(cert: dict[str, Any]) -> tuple[Any, ...]:
    row = scheduled_row(cert)
    return rowset_key(cert) + (str(row.get("selector")), int_value(row.get("top_k")))


def usable(cert: dict[str, Any]) -> bool:
    return factor_bank.certificate_is_usable(cert)


def first_by_key(certificates: list[dict[str, Any]], key_fn: Any) -> list[dict[str, Any]]:
    selected = []
    seen = set()
    for cert in certificates:
        key = key_fn(cert)
        if key in seen:
            continue
        seen.add(key)
        selected.append(cert)
    return selected


def first_usable_by_key(certificates: list[dict[str, Any]], key_fn: Any) -> list[dict[str, Any]]:
    selected = []
    seen = set()
    for cert in certificates:
        if not usable(cert):
            continue
        key = key_fn(cert)
        if key in seen:
            continue
        seen.add(key)
        selected.append(cert)
    return selected


def order_audits(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    usable_certs = [cert for cert in certificates if usable(cert)]
    orders = sorted({int_value(cert.get("order")) for cert in usable_certs})
    return {str(order): factor_bank.audit_order(usable_certs, order) for order in orders}


def audit_summary(audits: dict[str, Any]) -> dict[str, Any]:
    return {
        "factor_variables_derivable_count": sum(int_value(audit.get("factor_variables_derivable_count")) for audit in audits.values()),
        "full_rank_order_count": sum(1 for audit in audits.values() if audit.get("full_rank")),
        "matrix_consistent_order_count": sum(1 for audit in audits.values() if audit.get("matrix_consistent")),
        "order_count": len(audits),
        "total_deficiency": sum(int_value(audit.get("deficiency")) for audit in audits.values()),
        "total_factor_rank": sum(int_value(audit.get("rank")) for audit in audits.values()),
        "total_unique_factor_relation_count": sum(int_value(audit.get("unique_factor_relation_count")) for audit in audits.values()),
    }


def evaluate_policy(
    name: str,
    selected: list[dict[str, Any]],
    all_cost: int,
    discovery_boundary: str,
) -> dict[str, Any]:
    audits = order_audits(selected)
    summary = audit_summary(audits)
    cost = sum(charged_cost(cert) for cert in selected)
    usable_count = sum(1 for cert in selected if usable(cert))
    return {
        "charged_cost_ops": cost,
        "charged_cost_over_rho": ratio(cost, p905.RHO_ESTIMATE),
        "cost_fraction_vs_all_p907": ratio(cost, all_cost),
        "cost_saved_fraction_vs_all_p907": ratio(all_cost - cost, all_cost),
        "discovery_boundary": discovery_boundary,
        "matrix_consistent": all(bool(audit.get("matrix_consistent")) for audit in audits.values()) if audits else True,
        "name": name,
        "order_audits": audits,
        "selected_certificate_count": len(selected),
        "selected_transfer_sample": [
            {
                "clause": (cert.get("p907_selection") or {}).get("clause"),
                "selector": scheduled_row(cert).get("selector"),
                "split": scheduled_row(cert).get("split"),
                "transfer_index": int_value(scheduled_row(cert).get("transfer_index")),
                "usable": usable(cert),
            }
            for cert in selected[:16]
        ],
        "summary": summary,
        "usable_certificate_count": usable_count,
    }


def greedy_rank_increment_oracle(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    rank = 0
    for cert in certificates:
        if not usable(cert):
            continue
        candidate = selected + [cert]
        candidate_rank = audit_summary(order_audits(candidate))["total_factor_rank"]
        if candidate_rank > rank:
            selected.append(cert)
            rank = candidate_rank
    return selected


def policy_reports(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    all_cost = sum(charged_cost(cert) for cert in certificates)
    policies = [
        (
            "all_p907_selected_rows",
            certificates,
            "BASELINE: all selected rows replayed; public-verified gate applied only before factor-rank use.",
        ),
        (
            "public_rowset_first_pre_replay",
            first_by_key(certificates, rowset_key),
            "PUBLIC-PRE-REPLAY: one deterministic first certificate per public row-set key.",
        ),
        (
            "public_transfer_leaf_first_pre_replay",
            first_by_key(certificates, transfer_leaf_key),
            "PUBLIC-PRE-REPLAY: one deterministic first certificate per split/transfer/leaf signature.",
        ),
        (
            "exact_selector_identity_pre_replay",
            first_by_key(certificates, exact_selector_key),
            "PUBLIC-PRE-REPLAY CONTROL: exact selector identity, expected to match all P907 selected rows.",
        ),
        (
            "post_replay_usable_rowset_first_diagnostic",
            first_usable_by_key(certificates, rowset_key),
            "POST-REPLAY DIAGNOSTIC: requires knowing public verification before selecting representatives.",
        ),
        (
            "rank_increment_oracle_diagnostic",
            greedy_rank_increment_oracle(certificates),
            "ORACLE DIAGNOSTIC: uses rank outcome labels and is not a deployable source policy.",
        ),
    ]
    return [evaluate_policy(name, selected, all_cost, boundary) for name, selected, boundary in policies]


def determine_claim(reports: list[dict[str, Any]], baseline_rank: int) -> str:
    public = next(report for report in reports if report["name"] == "public_rowset_first_pre_replay")
    summary = public["summary"]
    if not public.get("matrix_consistent"):
        return "NEGATIVE_RESULT_P908_PUBLIC_ROWSET_DEDUP_INCONSISTENT"
    if int_value(summary.get("total_factor_rank")) < baseline_rank:
        return "NEGATIVE_RESULT_P908_PUBLIC_ROWSET_DEDUP_LOSES_RANK"
    saved = float(public.get("cost_saved_fraction_vs_all_p907") or 0.0)
    if saved >= 0.5:
        return "P908_PUBLIC_ROWSET_DEDUP_PRESERVES_RANK_WITH_COST_COMPRESSION"
    return "NEGATIVE_RESULT_P908_PUBLIC_ROWSET_DEDUP_SAVES_TOO_LITTLE"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p907_payload = load_json(args.p907_source)
    certificates = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    p907_summary = p907_payload.get("summary") if isinstance(p907_payload.get("summary"), dict) else {}
    baseline_rank = int_value(p907_summary.get("total_factor_rank"))
    reports = policy_reports(certificates)
    best_public = min(
        [report for report in reports if "PUBLIC-PRE-REPLAY" in report.get("discovery_boundary", "")],
        key=lambda report: (
            -int_value((report.get("summary") or {}).get("total_factor_rank")),
            int_value(report.get("charged_cost_ops")),
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(reports, baseline_rank),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "EXISTING-WINDOW: this reuses P907 replayed certificates and is not fresh validation.",
            "PUBLIC-PRE-REPLAY policies may be used as source policies; post-replay and oracle policies are diagnostics only.",
            "RANK-COST-COMPRESSION-NOT-DESCENT: rank preservation with lower cost is not full rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p908_p907_public_rowset_dedup_rank_cost",
        "parameters": {
            "p907_baseline_rank": baseline_rank,
            "p907_selected_certificate_count": len(certificates),
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
        },
        "policy_reports": reports,
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze the public row-set dedup policy on fresh windows, then measure rank "
                "growth per charged row-set before attempting factor solve or individual-log descent."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "summary": {
            "best_public_pre_replay_policy": {
                "charged_cost_ops": best_public.get("charged_cost_ops"),
                "charged_cost_over_rho": best_public.get("charged_cost_over_rho"),
                "cost_saved_fraction_vs_all_p907": best_public.get("cost_saved_fraction_vs_all_p907"),
                "name": best_public.get("name"),
                "selected_certificate_count": best_public.get("selected_certificate_count"),
                "total_factor_rank": (best_public.get("summary") or {}).get("total_factor_rank"),
                "total_unique_factor_relation_count": (best_public.get("summary") or {}).get("total_unique_factor_relation_count"),
                "usable_certificate_count": best_public.get("usable_certificate_count"),
            },
            "p907_baseline_cost_ops": sum(charged_cost(cert) for cert in certificates),
            "p907_baseline_rank": baseline_rank,
            "policy_count": len(reports),
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
