#!/usr/bin/env python3
"""P907 rank-growth audit over all P905 primary scheduled rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_p906_p905_first_stop_certificate_rank_audit as p906
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p907_p905_scheduled_certificate_rank_growth.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p907_p905_scheduled_certificate_rank_growth_probe.json"
P906_SOURCE = STATE_DIR / "low_term_total2_p906_p905_first_stop_certificate_rank_audit_probe.json"
SCHEMA = "ecdlp.low_term_total2_p907_p905_scheduled_certificate_rank_growth.v1"
PRIMARY_SCHEDULER = "p905_c8gap8_then_c90_then_c19"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p905.int_value(value, default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    return p905.ratio(numerator, denominator)


def primary_clause_names() -> list[str]:
    scheduler = next(item for item in p905.SCHEDULERS if item.get("name") == PRIMARY_SCHEDULER)
    return [str(name) for name in scheduler.get("clause_names") or []]


def row_identity(stop: dict[str, Any]) -> tuple[Any, ...]:
    return (
        str(stop.get("split")),
        int_value(stop.get("transfer_index")),
        str(stop.get("selector")),
        int_value(stop.get("top_k")),
        tuple(p906.normalize_row_leaf_keys(stop.get("row_leaf_keys") or [])),
    )


def selected_stops() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = p905.load_rows()
    clauses = p905.clause_by_name()
    selected: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    by_split_clause: dict[str, dict[str, dict[str, int]]] = {}
    clause_names = primary_clause_names()
    for split in p905.SPLITS:
        split_rows = [row for row in rows if (row.get("case") or {}).get("split") == split]
        by_split_clause[str(split)] = {}
        for clause_index, clause_name in enumerate(clause_names):
            clause = clauses[clause_name]
            matches = sorted([row for row in split_rows if p905.matches_clause(row, clause)], key=p905.row_order_key)
            by_split_clause[str(split)][clause_name] = {
                "good_count": sum(1 for row in matches if p905.is_good(row)),
                "match_count": len(matches),
                "public_key_verified_count": sum(1 for row in matches if row.get("public_key_verified")),
                "strict_count": sum(1 for row in matches if row.get("strict_below_rho")),
            }
            for order_in_clause, row in enumerate(matches):
                stop = p905.compact_row(row, None, clause_name) or {}
                case = row.get("case") or {}
                stop.update(
                    {
                        "artifact_source": case.get("artifact_source"),
                        "clause": clause_name,
                        "clause_index": clause_index,
                        "global_stream_ordinal": case.get("global_stream_ordinal"),
                        "is_p905_good": p905.is_good(row),
                        "order_in_clause": order_in_clause,
                        "selected_row_index": len(selected),
                        "split": split,
                        "target": p905.TARGET,
                    }
                )
                key = row_identity(stop)
                if key in seen:
                    continue
                seen.add(key)
                selected.append(stop)
    return selected, {"by_split_clause": by_split_clause, "clause_names": clause_names}


def source_resolution_record(
    split: str,
    stop: dict[str, Any],
    source_path: Path,
    source_case: dict[str, Any],
    attempts: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "attempts": attempts,
        "clause": stop.get("clause"),
        "leaf_signature": p906.p903.leaf_signature(source_case),
        "matched_row_leaf_keys": p906.normalize_row_leaf_keys(source_case.get("row_leaf_keys") or []),
        "source": str(source_path),
        "source_index": int_value(source_case.get("source_index")),
        "source_policy": source_case.get("source_policy"),
        "split": split,
        "transfer_index": int_value(source_case.get("transfer_index")),
    }


def usable_certificates(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [cert for cert in certificates if factor_bank.certificate_is_usable(cert)]


def order_audits(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    usable = usable_certificates(certificates)
    orders = sorted({int_value(cert.get("order")) for cert in usable})
    return {str(order): factor_bank.audit_order(usable, order) for order in orders}


def summarize_order_audits(audits: dict[str, Any]) -> dict[str, Any]:
    return {
        "factor_variables_derivable_count": sum(int_value(audit.get("factor_variables_derivable_count")) for audit in audits.values()),
        "full_rank_order_count": sum(1 for audit in audits.values() if audit.get("full_rank")),
        "matrix_consistent_order_count": sum(1 for audit in audits.values() if audit.get("matrix_consistent")),
        "order_count": len(audits),
        "total_deficiency": sum(int_value(audit.get("deficiency")) for audit in audits.values()),
        "total_factor_rank": sum(int_value(audit.get("rank")) for audit in audits.values()),
        "total_unique_factor_relation_count": sum(int_value(audit.get("unique_factor_relation_count")) for audit in audits.values()),
    }


def charged_cost(stop: dict[str, Any]) -> int:
    return 1 + max(1, int_value(stop.get("generator_case_cost_ops"), 1))


def replay_certificates(stops: list[dict[str, Any]], out: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    certificates = []
    resolutions = []
    for index, stop in enumerate(stops):
        split = str(stop.get("split"))
        source_path, source, source_case, attempts = p906.find_source_case_for_stop(split, stop)
        cert = p906.certificate_for_source_case(source, source_path, source_case, split, stop, index)
        cert["_artifact"] = str(out)
        cert["_artifact_offset"] = index
        cert["_global_index"] = index
        cert["direct_export_route"] = "direct_source_exact_p905_primary_schedule_match"
        cert["p905_scheduled_row"] = cert.pop("p905_first_stop")
        cert["p907_selection"] = {
            "charged_candidate_cost_ops": charged_cost(stop),
            "clause": stop.get("clause"),
            "generator_case_cost_ops": int_value(stop.get("generator_case_cost_ops"), 1),
            "is_p905_good": bool(stop.get("is_p905_good")),
            "public_key_verified_in_p905": bool(stop.get("public_key_verified")),
            "selected_row_index": int_value(stop.get("selected_row_index")),
            "split": split,
            "strict_below_rho_in_p905": bool(stop.get("strict_below_rho")),
            "transfer_index": int_value(stop.get("transfer_index")),
        }
        certificates.append(cert)
        resolutions.append(source_resolution_record(split, stop, source_path, source_case, attempts))
    return certificates, resolutions


def prefix_rank_growth(certificates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    growth = []
    prefix: list[dict[str, Any]] = []
    charged_total = 0
    for index, cert in enumerate(certificates, start=1):
        selection = cert.get("p907_selection") if isinstance(cert.get("p907_selection"), dict) else {}
        charged_total += int_value(selection.get("charged_candidate_cost_ops"), 1)
        if factor_bank.certificate_is_usable(cert):
            prefix.append(cert)
        audits = order_audits(prefix)
        summary = summarize_order_audits(audits)
        growth.append(
            {
                "candidate_prefix_count": index,
                "charged_total_cost_ops": charged_total,
                "charged_total_cost_over_rho": ratio(charged_total, p905.RHO_ESTIMATE),
                "latest_certificate_public_key_verified": bool(cert.get("public_key_verified")),
                "latest_clause": selection.get("clause"),
                "latest_split": selection.get("split"),
                "latest_transfer_index": selection.get("transfer_index"),
                "total_factor_rank": summary["total_factor_rank"],
                "total_unique_factor_relation_count": summary["total_unique_factor_relation_count"],
                "usable_certificate_count": len(prefix),
            }
        )
    return growth


def cost_summary(stops: list[dict[str, Any]], certificates: list[dict[str, Any]]) -> dict[str, Any]:
    usable = usable_certificates(certificates)
    all_cost = sum(charged_cost(stop) for stop in stops)
    usable_indices = {int_value((cert.get("p907_selection") or {}).get("selected_row_index")) for cert in usable}
    usable_cost = sum(charged_cost(stop) for stop in stops if int_value(stop.get("selected_row_index")) in usable_indices)
    by_clause = Counter(str(stop.get("clause")) for stop in stops)
    usable_by_clause = Counter(str((cert.get("p907_selection") or {}).get("clause")) for cert in usable)
    return {
        "all_selected_candidate_count": len(stops),
        "all_selected_total_cost_ops": all_cost,
        "all_selected_total_cost_over_rho": ratio(all_cost, p905.RHO_ESTIMATE),
        "candidate_count_by_clause": dict(sorted(by_clause.items())),
        "usable_certificate_count_by_clause": dict(sorted(usable_by_clause.items())),
        "usable_candidate_total_cost_ops": usable_cost,
        "usable_candidate_total_cost_over_rho": ratio(usable_cost, p905.RHO_ESTIMATE),
    }


def first_stop_identity_set(p906_payload: dict[str, Any]) -> set[tuple[Any, ...]]:
    out: set[tuple[Any, ...]] = set()
    for cert in p906_payload.get("certificates") or []:
        stop = cert.get("p905_first_stop") if isinstance(cert.get("p905_first_stop"), dict) else {}
        if stop:
            out.add(row_identity(stop))
    return out


def determine_claim(
    p906_rank: int,
    certificates: list[dict[str, Any]],
    audits: dict[str, Any],
    first_stop_covered: bool,
) -> str:
    if not first_stop_covered:
        return "NEGATIVE_RESULT_P907_P906_FIRST_STOPS_NOT_COVERED"
    if any(not bool(audit.get("matrix_consistent")) for audit in audits.values()):
        return "NEGATIVE_RESULT_P907_SCHEDULED_FACTOR_BANK_INCONSISTENT"
    total_rank = sum(int_value(audit.get("rank")) for audit in audits.values())
    if any(bool(audit.get("full_rank")) for audit in audits.values()):
        return "P907_P905_SCHEDULED_CERTIFICATES_FULL_FACTOR_RANK_CANDIDATE_NEEDS_DESCENT"
    if total_rank > p906_rank:
        return "P907_P905_SCHEDULED_CERTIFICATES_RANK_GROWS_BUT_PARTIAL"
    if total_rank > 0:
        return "NEGATIVE_RESULT_P907_SCHEDULED_CERTIFICATES_NO_INCREMENTAL_RANK"
    if not usable_certificates(certificates):
        return "NEGATIVE_RESULT_P907_NO_USABLE_PUBLIC_CERTIFICATES"
    return "NEGATIVE_RESULT_P907_NO_TARGET_ELIMINATED_RANK"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p906_payload = p906.load_json(args.p906_source)
    p906_summary = p906_payload.get("summary") if isinstance(p906_payload.get("summary"), dict) else {}
    p906_rank = int_value(p906_summary.get("total_factor_rank"))
    stops, selection_summary = selected_stops()
    certificates, source_resolution = replay_certificates(stops, args.out)
    usable = usable_certificates(certificates)
    audits = order_audits(certificates)
    audit_summary = summarize_order_audits(audits)
    first_stops = first_stop_identity_set(p906_payload)
    covered = {row_identity(cert.get("p905_scheduled_row") or {}) for cert in certificates}
    first_stop_covered = first_stops.issubset(covered)
    claim_status = determine_claim(p906_rank, certificates, audits, first_stop_covered)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p906_source": str(args.p906_source),
            "script": str(Path(__file__)),
        },
        "certificates": certificates,
        "claim_status": claim_status,
        "cost_summary": cost_summary(stops, certificates),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "EXISTING-WINDOW: P907 reuses P903/P904/P905 artifacts and is not a fresh holdout.",
            "PUBLIC-VERIFICATION-GATE: non-public-verified direct replays are controls and do not contribute to factor rank.",
            "RANK-GROWTH-NOT-DESCENT: factor-rank growth is not individual-log descent or a complete index-calculus attack.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p907_p905_scheduled_certificate_rank_growth",
        "order_audits": audits,
        "parameters": {
            "p905_primary_scheduler": PRIMARY_SCHEDULER,
            "p906_baseline_rank": p906_rank,
            "rho_estimate": p905.RHO_ESTIMATE,
            "target": p905.TARGET,
        },
        "prefix_rank_growth": prefix_rank_growth(certificates),
        "rank_descent_obligations": {
            "can_promote_to_descent": any(audit.get("full_rank") for audit in audits.values()),
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "If rank remains partial, collect fresh P905-scheduled windows and fit rank per "
                "charged selected-row cost. If full rank appears, solve factor variables and run "
                "individual-log descent before any faster-than-rho claim."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "selection_summary": {
            **selection_summary,
            "p906_first_stop_covered": first_stop_covered,
            "p906_first_stop_count": len(first_stops),
            "selected_stop_count": len(stops),
            "usable_certificate_count": len(usable),
        },
        "source_resolution": source_resolution,
        "summary": {
            **audit_summary,
            "certificate_count": len(certificates),
            "p906_baseline_rank": p906_rank,
            "public_key_verified_certificate_count": len(usable),
            "rank_delta_vs_p906": audit_summary["total_factor_rank"] - p906_rank,
            "target_descent_implemented": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p906-source", type=Path, default=P906_SOURCE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "cost_summary": payload["cost_summary"],
                "parameters": payload["parameters"],
                "selection_summary": payload["selection_summary"],
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
