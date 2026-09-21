#!/usr/bin/env python3
"""P906 certificate and factor-rank audit for P905 first-stop rows."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_direct_source_relation_equation_certificate as direct_export
import low_term_total2_p903_relaxed_family_grid_validation as p903
import low_term_total2_p904_leaf90_top7_forward_freeze as p904
import low_term_total2_p905_regime_switch_scheduler as p905
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p906_p905_first_stop_certificate_rank_audit.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p906_p905_first_stop_certificate_rank_audit_probe.json"
P905_SOURCE = STATE_DIR / "low_term_total2_p905_regime_switch_scheduler_probe.json"
SCHEMA = "ecdlp.low_term_total2_p906_p905_first_stop_certificate_rank_audit.v1"

SOURCE_PATHS_BY_SPLIT = {
    "train": p903.TRAIN_SOURCES,
    "validation": p903.VALIDATION_SOURCES,
    "forward": p904.FORWARD_SOURCES,
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
    try:
        return int(value)
    except (TypeError, ValueError):
        return int(default)


def ratio(numerator: int | float | None, denominator: int | float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return round(float(numerator) / float(denominator), 8)


def normalize_row_leaf_keys(row_leaf_keys: list[dict[str, Any]]) -> tuple[tuple[str, tuple[int, ...]], ...]:
    return tuple(
        sorted(
            (
                str(row.get("row_key")),
                tuple(int_value(leaf) for leaf in row.get("leaf_indices") or []),
            )
            for row in row_leaf_keys
            if isinstance(row, dict)
        )
    )


def source_cases(source: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for policy_name, result in (source.get("policies") or {}).items():
        if not isinstance(result, dict):
            continue
        row_selector = (result.get("row_selector") or {}).get("selector")
        for source_index, row in enumerate(result.get("stress_leaf_results") or []):
            if not isinstance(row, dict):
                continue
            case = dict(row)
            case["source_index"] = source_index
            case["source_policy"] = str(policy_name)
            case["row_selector"] = case.get("row_selector") or row_selector
            cases.append(case)
    return cases


def exact_case_matches(case: dict[str, Any], stop: dict[str, Any]) -> bool:
    return (
        str(case.get("target")) == str(stop.get("target") or p905.TARGET)
        and int_value(case.get("transfer_index")) == int_value(stop.get("transfer_index"))
        and str(case.get("selector")) == str(stop.get("selector"))
        and int_value(case.get("top_k")) == int_value(stop.get("top_k"))
        and p903.leaf_signature(case) == str(stop.get("leaf_signature"))
        and normalize_row_leaf_keys(case.get("row_leaf_keys") or [])
        == normalize_row_leaf_keys(stop.get("row_leaf_keys") or [])
    )


def find_source_case_for_stop(
    split: str,
    stop: dict[str, Any],
) -> tuple[Path, dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    attempts: list[dict[str, Any]] = []
    for source_path in SOURCE_PATHS_BY_SPLIT.get(split, []):
        source = load_json(source_path)
        matches = [case for case in source_cases(source) if exact_case_matches(case, stop)]
        attempts.append({"match_count": len(matches), "source": str(source_path)})
        if not matches:
            continue
        matches.sort(
            key=lambda row: (
                not bool(row.get("public_key_verified")),
                not bool(row.get("source_verified")),
                float(row.get("ops_over_rho") or 10**18),
                str(row.get("source_policy")),
            )
        )
        selected = dict(matches[0])
        selected["source"] = str(source_path)
        return source_path, source, selected, attempts
    raise ValueError(
        f"no exact P905 stop source case for split={split!r} "
        f"transfer={stop.get('transfer_index')!r} selector={stop.get('selector')!r}; "
        f"attempts={attempts}"
    )


def certificate_for_source_case(
    source: dict[str, Any],
    source_path: Path,
    source_case: dict[str, Any],
    split: str,
    stop: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    verifier, contexts, product_factor, _max_relations = direct_export.timing_probe.selected_contexts_from_source_case(
        source,
        source_case,
    )
    direct_rows, direct_ops, rho, _row_profiles = direct_export.timing_probe.direct_witness_rows(
        verifier,
        contexts,
    )
    built_by_row = {str(context["row_key"]): context["built"] for context in contexts}
    direct_union = direct_export.direct_witness_probe.union_derive(
        verifier,
        direct_rows,
        built_by_row,
        "_scan",
    )
    if not contexts:
        raise ValueError(f"no selected contexts for split={split!r} stop={stop!r}")
    order = int(contexts[0]["built"]["order"])
    events = direct_export.direct_unique_events(direct_rows)
    public_key_verified = bool(direct_union.get("union_public_key_verified"))
    derived_secret = direct_union.get("union_derived_secret")
    cert = {
        "_artifact": str(DEFAULT_OUT),
        "_artifact_offset": index,
        "_global_index": index,
        "certificate_status": (
            "PUBLIC_DIRECT_RELATION_EQUATIONS_VERIFY_PUBLIC_KEY"
            if public_key_verified
            else "PUBLIC_DIRECT_RELATION_EQUATIONS_NEED_REVIEW"
        ),
        "clause": str(stop.get("clause") or "unknown"),
        "derived_secret": derived_secret,
        "direct_export_route": "direct_source_exact_p905_stop",
        "expected_secret": derived_secret if public_key_verified else None,
        "forms": [direct_export.compact_form(event, order) for event in events],
        "forms_count": len(events),
        "order": order,
        "p905_first_stop": stop,
        "product_factor": product_factor,
        "public_key_verified": public_key_verified,
        "rank": int_value(direct_union.get("union_rank")),
        "scan_row_count": len(direct_rows),
        "selected": {
            "clause": str(stop.get("clause") or "unknown"),
            "direct_ops": direct_ops,
            "direct_ops_over_rho": ratio(direct_ops, rho),
            "rho": rho,
            "row_keys": source_case.get("row_keys") or [],
            "secret": derived_secret if public_key_verified else None,
            "selector": source_case.get("selector"),
            "shared_ops": None,
            "shared_ops_over_rho": None,
            "split": split,
            "target": source_case.get("target"),
            "top_k": int_value(source_case.get("top_k")),
            "transfer_index": int_value(source_case.get("transfer_index")),
        },
        "selected_term_support": direct_export.selected_term_support(contexts),
        "source": str(source_path),
        "source_case_selector": {
            "leaf_signature": p903.leaf_signature(source_case),
            "selector": source_case.get("selector"),
            "source_index": int_value(source_case.get("source_index")),
            "source_policy": source_case.get("source_policy"),
            "target": source_case.get("target"),
            "top_k": int_value(source_case.get("top_k")),
            "transfer_index": int_value(source_case.get("transfer_index")),
        },
        "timing": None,
        "window": split,
    }
    return cert


def first_good_stops(p905_payload: dict[str, Any]) -> list[dict[str, Any]]:
    primary = next(
        item
        for item in p905_payload.get("evaluated_schedulers") or []
        if item.get("name") == "p905_c8gap8_then_c90_then_c19"
    )
    stops: list[dict[str, Any]] = []
    for split in p905.SPLITS:
        split_row = ((primary.get("by_split") or {}).get(split) or {}).get("first_good_stop")
        if not isinstance(split_row, dict):
            raise ValueError(f"missing P905 first_good_stop for split={split!r}")
        stop = dict(split_row)
        stop["split"] = split
        stops.append(stop)
    return stops


def factor_audits(certificates: list[dict[str, Any]]) -> dict[str, Any]:
    orders = sorted({int_value(cert.get("order")) for cert in certificates})
    return {str(order): factor_bank.audit_order(certificates, order) for order in orders}


def determine_claim(certificates: list[dict[str, Any]], audits: dict[str, Any]) -> str:
    if not certificates or any(not bool(cert.get("public_key_verified")) for cert in certificates):
        return "NEGATIVE_RESULT_P906_P905_FIRST_STOP_CERTIFICATE_REPLAY_INCOMPLETE"
    if any(not bool(audit.get("matrix_consistent")) for audit in audits.values()):
        return "NEGATIVE_RESULT_P906_TARGET_ELIMINATED_FACTOR_BANK_INCONSISTENT"
    total_rank = sum(int_value(audit.get("rank")) for audit in audits.values())
    full_rank = any(bool(audit.get("full_rank")) for audit in audits.values())
    if full_rank:
        return "P906_P905_FIRST_STOPS_FULL_FACTOR_RANK_TARGET_DESCENT_CANDIDATE"
    if total_rank > 0:
        return "P906_P905_FIRST_STOPS_TARGET_ELIMINATED_FACTOR_RANK_SIGNAL"
    return "NEGATIVE_RESULT_P906_NO_TARGET_ELIMINATED_FACTOR_RANK_FROM_P905_FIRST_STOPS"


def summarize(certificates: list[dict[str, Any]], audits: dict[str, Any]) -> dict[str, Any]:
    total_unique = sum(int_value(audit.get("unique_factor_relation_count")) for audit in audits.values())
    total_rank = sum(int_value(audit.get("rank")) for audit in audits.values())
    total_deficiency = sum(int_value(audit.get("deficiency")) for audit in audits.values())
    total_derivable = sum(int_value(audit.get("factor_variables_derivable_count")) for audit in audits.values())
    full_rank_orders = sum(1 for audit in audits.values() if audit.get("full_rank"))
    return {
        "certificate_count": len(certificates),
        "factor_variables_derivable_count": total_derivable,
        "full_rank_order_count": full_rank_orders,
        "matrix_consistent_order_count": sum(1 for audit in audits.values() if audit.get("matrix_consistent")),
        "public_key_verified_certificate_count": sum(1 for cert in certificates if cert.get("public_key_verified")),
        "target_descent_implemented": False,
        "total_deficiency": total_deficiency,
        "total_factor_rank": total_rank,
        "total_unique_factor_relation_count": total_unique,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p905_payload = load_json(args.p905_source)
    stops = first_good_stops(p905_payload)
    certificates = []
    source_resolution = []
    for index, stop in enumerate(stops):
        split = str(stop.get("split"))
        source_path, source, source_case, attempts = find_source_case_for_stop(split, stop)
        cert = certificate_for_source_case(source, source_path, source_case, split, stop, index)
        certificates.append(cert)
        source_resolution.append(
            {
                "attempts": attempts,
                "leaf_signature": p903.leaf_signature(source_case),
                "matched_row_leaf_keys": normalize_row_leaf_keys(source_case.get("row_leaf_keys") or []),
                "source": str(source_path),
                "source_index": int_value(source_case.get("source_index")),
                "source_policy": source_case.get("source_policy"),
                "split": split,
                "transfer_index": int_value(source_case.get("transfer_index")),
            }
        )
    audits = factor_audits(certificates)
    claim_status = determine_claim(certificates, audits)
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p905_source": str(args.p905_source),
            "script": str(Path(__file__)),
        },
        "certificates": certificates,
        "claim_status": claim_status,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "MODEL-BOUND: factor columns are the verifier's current order-specific factor-base namespace.",
            "DIRECT-CERTIFICATE: certificates replay exact P905 first-stop row keys through the direct source exporter.",
            "RANK-SIGNAL-NOT-DESCENT: target-eliminated factor rank is evidence for a reusable factor-bank route, not a complete individual-log descent.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p906_p905_first_stop_certificate_rank_audit",
        "order_audits": audits,
        "parameters": {
            "p905_primary_scheduler": "p905_c8gap8_then_c90_then_c19",
            "rho_estimate": p905.RHO_ESTIMATE,
            "splits": list(p905.SPLITS),
            "target": p905.TARGET,
        },
        "rank_descent_obligations": {
            "can_promote_to_descent": any(audit.get("full_rank") for audit in audits.values()),
            "factor_relation_rank_computed": True,
            "individual_log_descent_integrated": False,
            "obligation": (
                "If factor rank is partial, collect more exact P905-scheduled certificates and "
                "test whether rank grows faster than source-generation cost. If full rank appears, "
                "run individual-log descent and compare total cost against Pollard rho."
            ),
            "relation_equations_exported": True,
            "target_eliminated_rank_integrated": True,
        },
        "schema": SCHEMA,
        "source_resolution": source_resolution,
        "summary": summarize(certificates, audits),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--p905-source", type=Path, default=P905_SOURCE)
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
