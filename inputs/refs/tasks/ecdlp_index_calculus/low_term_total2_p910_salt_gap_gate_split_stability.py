#!/usr/bin/env python3
"""P910 split-stability audit for the P909 salt-gap gate."""

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
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p910_salt_gap_gate_split_stability.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p910_salt_gap_gate_split_stability_probe.json"
P907_SOURCE = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
P909_SOURCE = STATE_DIR / "low_term_total2_p909_public_cost_gate_rank_predictor_probe.json"
SCHEMA = "ecdlp.low_term_total2_p910_salt_gap_gate_split_stability.v1"
FROZEN_GATE_NAME = "salt_gap_ge_5"


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


def split(cert: dict[str, Any]) -> str:
    return str(p908.scheduled_row(cert).get("split"))


def salt_gap(cert: dict[str, Any]) -> int:
    return p909.salt_gap(cert)


def charged_cost(cert: dict[str, Any]) -> int:
    return p908.charged_cost(cert)


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
        "selected_transfers": [
            {
                "charged_cost_ops": charged_cost(cert),
                "clause": (cert.get("p907_selection") or {}).get("clause"),
                "salt_gap": salt_gap(cert),
                "split": split(cert),
                "transfer_index": int_value(p908.scheduled_row(cert).get("transfer_index")),
                "usable": p908.usable(cert),
            }
            for cert in selected
        ],
        "summary": summary,
        "usable_certificate_count": sum(1 for cert in selected if p908.usable(cert)),
    }


def policy_eval(
    representatives: list[dict[str, Any]],
    name: str,
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    selected = [cert for cert in representatives if predicate(cert)]
    return {"name": name, **audit_selected(selected)}


def split_reports(
    representatives: list[dict[str, Any]],
    name: str,
    predicate: Callable[[dict[str, Any]], bool],
) -> dict[str, Any]:
    out = {}
    for split_name in p905.SPLITS:
        split_reps = [cert for cert in representatives if split(cert) == split_name]
        out[str(split_name)] = policy_eval(split_reps, name, predicate)
    return out


def rank(report: dict[str, Any]) -> int:
    return int_value((report.get("summary") or {}).get("total_factor_rank"))


def determine_claim(
    all_by_split: dict[str, Any],
    gate_by_split: dict[str, Any],
    global_gate: dict[str, Any],
    global_all: dict[str, Any],
) -> str:
    if not global_gate.get("matrix_consistent"):
        return "NEGATIVE_RESULT_P910_SALT_GAP_GATE_INCONSISTENT"
    if rank(global_gate) < rank(global_all):
        return "NEGATIVE_RESULT_P910_SALT_GAP_GATE_LOSES_GLOBAL_RANK"
    for split_name, all_report in all_by_split.items():
        all_rank = rank(all_report)
        gate_rank = rank(gate_by_split.get(split_name) or {})
        if all_rank > 0 and gate_rank < all_rank:
            return "NEGATIVE_RESULT_P910_SALT_GAP_GATE_LOSES_SPLIT_RANK"
    return "P910_SALT_GAP_GATE_PRESERVES_SPLIT_AND_GLOBAL_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p907_payload = load_json(args.p907_source)
    p909_payload = load_json(args.p909_source)
    certificates = [cert for cert in p907_payload.get("certificates") or [] if isinstance(cert, dict)]
    representatives = p909.public_rowset_representatives(certificates)
    gates: dict[str, Callable[[dict[str, Any]], bool]] = {
        "all_rowsets": lambda _cert: True,
        "salt_gap_ge_5": lambda cert: salt_gap(cert) >= 5,
        "salt_gap_le_4_control": lambda cert: salt_gap(cert) <= 4,
    }
    global_reports = {
        name: policy_eval(representatives, name, predicate)
        for name, predicate in gates.items()
    }
    split_policy_reports = {
        name: split_reports(representatives, name, predicate)
        for name, predicate in gates.items()
    }
    claim_status = determine_claim(
        split_policy_reports["all_rowsets"],
        split_policy_reports["salt_gap_ge_5"],
        global_reports["salt_gap_ge_5"],
        global_reports["all_rowsets"],
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p907_source": str(args.p907_source),
            "p909_source": str(args.p909_source),
            "script": str(Path(__file__)),
        },
        "claim_status": claim_status,
        "created_at": now_iso(),
        "frozen_gate": {
            "name": FROZEN_GATE_NAME,
            "source_claim": (p909_payload.get("claim_status") if isinstance(p909_payload, dict) else None),
            "threshold": 5,
        },
        "global_policy_reports": global_reports,
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "EXISTING-WINDOW: split stability is not fresh validation.",
            "FROZEN-GATE: salt_gap >= 5 is taken from P909 before this split-local audit.",
            "RANK-STABILITY-NOT-DESCENT: rank preservation is not full factor rank or individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p910_salt_gap_gate_split_stability",
        "parameters": {
            "rho_estimate": p905.RHO_ESTIMATE,
            "splits": list(p905.SPLITS),
            "target": p905.TARGET,
        },
        "rank_descent_obligations": {
            "can_promote_to_descent": False,
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "Freeze salt_gap >= 5 and replay it on fresh source windows. If it holds, "
                "continue rank accumulation until full factor rank or a sharper rank-increment predictor appears."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "split_policy_reports": split_policy_reports,
        "summary": {
            "all_rowsets_global": {
                "charged_cost_ops": global_reports["all_rowsets"]["charged_cost_ops"],
                "rank": rank(global_reports["all_rowsets"]),
                "unique_factor_relation_count": (global_reports["all_rowsets"].get("summary") or {}).get("total_unique_factor_relation_count"),
            },
            "salt_gap_ge_5_global": {
                "charged_cost_ops": global_reports["salt_gap_ge_5"]["charged_cost_ops"],
                "charged_cost_over_rho": global_reports["salt_gap_ge_5"]["charged_cost_over_rho"],
                "rank": rank(global_reports["salt_gap_ge_5"]),
                "unique_factor_relation_count": (global_reports["salt_gap_ge_5"].get("summary") or {}).get("total_unique_factor_relation_count"),
            },
            "salt_gap_le_4_control_global": {
                "charged_cost_ops": global_reports["salt_gap_le_4_control"]["charged_cost_ops"],
                "charged_cost_over_rho": global_reports["salt_gap_le_4_control"]["charged_cost_over_rho"],
                "rank": rank(global_reports["salt_gap_le_4_control"]),
                "unique_factor_relation_count": (global_reports["salt_gap_le_4_control"].get("summary") or {}).get("total_unique_factor_relation_count"),
            },
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p907-source", type=Path, default=P907_SOURCE)
    parser.add_argument("--p909-source", type=Path, default=P909_SOURCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
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
