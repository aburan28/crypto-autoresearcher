#!/usr/bin/env python3
"""Score candidate certificates by marginal target-eliminated factor rank.

The target-eliminated relation bank can convert public row certificates into
factor-only equations, but later rows may be dependent.  This scorer compares a
base certificate bank with one candidate certificate at a time and reports the
rank gain, unique-relation gain, and rough public source-charge hints for each
candidate.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def audit_summary(certificates: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    orders = sorted({int_value(cert.get("order")) for cert in certificates})
    return {str(order): factor_bank.audit_order(certificates, order) for order in orders}


def selected_info(cert: dict[str, Any]) -> dict[str, Any]:
    selected = cert.get("selected") if isinstance(cert.get("selected"), dict) else {}
    rho = int_value(selected.get("rho"))
    shared_ops = selected.get("shared_ops")
    generated_plus_shared = None
    if shared_ops is not None:
        generated_plus_shared = int_value(shared_ops) + 1
    return {
        "artifact": cert.get("_artifact"),
        "artifact_offset": int_value(cert.get("_artifact_offset")),
        "clause": cert.get("clause") or selected.get("clause"),
        "direct_ops_over_rho": selected.get("direct_ops_over_rho"),
        "expected_secret": cert.get("expected_secret"),
        "forms_count": int_value(cert.get("forms_count")),
        "generated_plus_shared_ops_over_rho": ratio(generated_plus_shared, rho),
        "order": int_value(cert.get("order")),
        "rank": int_value(cert.get("rank")),
        "rho": rho,
        "selector": selected.get("selector"),
        "shared_ops_over_rho": selected.get("shared_ops_over_rho"),
        "target": selected.get("target"),
        "top_k": int_value(selected.get("top_k")),
        "transfer_index": int_value(selected.get("transfer_index")),
        "window": cert.get("window"),
    }


def candidate_scores(
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    base_audits = audit_summary(base_certificates)
    scores: list[dict[str, Any]] = []
    for candidate in candidate_certificates:
        order = str(int_value(candidate.get("order")))
        base_order = base_audits.get(order) or {
            "rank": 0,
            "unique_factor_relation_count": 0,
            "deficiency": 0,
            "factor_variable_count": 0,
        }
        after_audits = audit_summary(base_certificates + [candidate])
        after_order = after_audits[order]
        rank_gain = int_value(after_order.get("rank")) - int_value(base_order.get("rank"))
        unique_gain = int_value(after_order.get("unique_factor_relation_count")) - int_value(
            base_order.get("unique_factor_relation_count")
        )
        deficiency_delta = int_value(after_order.get("deficiency")) - int_value(base_order.get("deficiency"))
        scores.append(
            {
                "candidate": selected_info(candidate),
                "claim_status": (
                    "MARGINAL_FACTOR_RANK_GAIN"
                    if rank_gain > 0
                    else "DEPENDENT_FACTOR_ROWS_NO_RANK_GAIN"
                    if unique_gain > 0
                    else "NO_NEW_FACTOR_RELATIONS"
                ),
                "deficiency_delta": deficiency_delta,
                "order": order,
                "rank_after": int_value(after_order.get("rank")),
                "rank_before": int_value(base_order.get("rank")),
                "rank_gain": rank_gain,
                "unique_factor_relation_count_after": int_value(after_order.get("unique_factor_relation_count")),
                "unique_factor_relation_count_before": int_value(base_order.get("unique_factor_relation_count")),
                "unique_factor_relation_gain": unique_gain,
            }
        )
    scores.sort(
        key=lambda item: (
            -int_value(item.get("rank_gain")),
            -int_value(item.get("unique_factor_relation_gain")),
            str((item.get("candidate") or {}).get("artifact")),
            int_value((item.get("candidate") or {}).get("artifact_offset")),
        )
    )
    greedy_selected: list[dict[str, Any]] = []
    greedy_base = list(base_certificates)
    remaining = list(candidate_certificates)
    while remaining:
        round_scores, _summary = candidate_scores_no_greedy(greedy_base, remaining)
        best = round_scores[0] if round_scores else None
        if not best or int_value(best.get("rank_gain")) <= 0:
            break
        best_candidate_info = best.get("candidate") or {}
        best_artifact = str(best_candidate_info.get("artifact"))
        best_offset = int_value(best_candidate_info.get("artifact_offset"))
        selected_index = None
        for index, candidate in enumerate(remaining):
            if str(candidate.get("_artifact")) == best_artifact and int_value(candidate.get("_artifact_offset")) == best_offset:
                selected_index = index
                break
        if selected_index is None:
            break
        selected_candidate = remaining.pop(selected_index)
        greedy_base.append(selected_candidate)
        best["greedy_step"] = len(greedy_selected) + 1
        greedy_selected.append(best)
    summary = {
        "candidate_count": len(scores),
        "greedy_rank_gain_total": sum(int_value(item.get("rank_gain")) for item in greedy_selected),
        "greedy_selected_count": len(greedy_selected),
        "rank_gain_candidate_count": sum(1 for item in scores if int_value(item.get("rank_gain")) > 0),
        "unique_gain_candidate_count": sum(
            1 for item in scores if int_value(item.get("unique_factor_relation_gain")) > 0
        ),
        "max_rank_gain": max([int_value(item.get("rank_gain")) for item in scores] or [0]),
        "max_unique_factor_relation_gain": max(
            [int_value(item.get("unique_factor_relation_gain")) for item in scores] or [0]
        ),
    }
    return scores, greedy_selected, summary


def candidate_scores_no_greedy(
    base_certificates: list[dict[str, Any]],
    candidate_certificates: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    base_audits = audit_summary(base_certificates)
    scores: list[dict[str, Any]] = []
    for candidate in candidate_certificates:
        order = str(int_value(candidate.get("order")))
        base_order = base_audits.get(order) or {
            "rank": 0,
            "unique_factor_relation_count": 0,
            "deficiency": 0,
            "factor_variable_count": 0,
        }
        after_audits = audit_summary(base_certificates + [candidate])
        after_order = after_audits[order]
        rank_gain = int_value(after_order.get("rank")) - int_value(base_order.get("rank"))
        unique_gain = int_value(after_order.get("unique_factor_relation_count")) - int_value(
            base_order.get("unique_factor_relation_count")
        )
        deficiency_delta = int_value(after_order.get("deficiency")) - int_value(base_order.get("deficiency"))
        scores.append(
            {
                "candidate": selected_info(candidate),
                "claim_status": (
                    "MARGINAL_FACTOR_RANK_GAIN"
                    if rank_gain > 0
                    else "DEPENDENT_FACTOR_ROWS_NO_RANK_GAIN"
                    if unique_gain > 0
                    else "NO_NEW_FACTOR_RELATIONS"
                ),
                "deficiency_delta": deficiency_delta,
                "order": order,
                "rank_after": int_value(after_order.get("rank")),
                "rank_before": int_value(base_order.get("rank")),
                "rank_gain": rank_gain,
                "unique_factor_relation_count_after": int_value(after_order.get("unique_factor_relation_count")),
                "unique_factor_relation_count_before": int_value(base_order.get("unique_factor_relation_count")),
                "unique_factor_relation_gain": unique_gain,
            }
        )
    scores.sort(
        key=lambda item: (
            -int_value(item.get("rank_gain")),
            -int_value(item.get("unique_factor_relation_gain")),
            str((item.get("candidate") or {}).get("artifact")),
            int_value((item.get("candidate") or {}).get("artifact_offset")),
        )
    )
    summary = {
        "candidate_count": len(scores),
        "rank_gain_candidate_count": sum(1 for item in scores if int_value(item.get("rank_gain")) > 0),
        "unique_gain_candidate_count": sum(
            1 for item in scores if int_value(item.get("unique_factor_relation_gain")) > 0
        ),
    }
    return scores, summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-certificates", required=True, help="Comma-separated base certificate JSON files.")
    parser.add_argument("--candidate-certificates", required=True, help="Comma-separated candidate certificate JSON files.")
    parser.add_argument("--out", required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_paths = [Path(item) for item in args.base_certificates.split(",") if item.strip()]
    candidate_paths = [Path(item) for item in args.candidate_certificates.split(",") if item.strip()]
    base_certificates = factor_bank.load_certificates(base_paths)
    candidate_certificates = factor_bank.load_certificates(candidate_paths)
    scores, greedy_selected, summary = candidate_scores(base_certificates, candidate_certificates)
    payload = {
        "artifacts": {
            "base_certificates": [str(path) for path in base_paths],
            "candidate_certificates": [str(path) for path in candidate_paths],
        },
        "claim_status": (
            "MARGINAL_RANK_GAIN_CANDIDATES_FOUND"
            if summary["rank_gain_candidate_count"]
            else "NO_MARGINAL_RANK_GAIN_CANDIDATES"
            if scores
            else "NO_CANDIDATES"
        ),
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: rank is measured in the verifier's current order-specific factor-column namespace.",
            "HEURISTIC: marginal factor rank is a collector objective for index-calculus exploration, not a deployed-curve speedup claim.",
        ],
        "schema": "ecdlp.low_term_total2_factor_rank_candidate_scorer.v1",
        "greedy_selected": greedy_selected,
        "scores": scores,
        "summary": summary,
    }
    write_json(Path(args.out), payload)
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(json.dumps({"claim_status": payload["claim_status"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
