#!/usr/bin/env python3
"""P702 factor-substitution target verification for the P701 row-union closure.

P701 found a below-rho row-union replay that closes the order-9887 factor bank
but does not directly verify by aggregate rowspace derivation.  This audit asks
the narrower target-descent question: once the P701 endpoint rows close all
factor variables, do the preserved public endpoint forms recover a single
target secret that verifies against the public key?
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import low_term_total2_p693_endpoint_column_source_support_scout as p693
import low_term_total2_p697_endpoint_event_factor_rank_audit as p697
import low_term_total2_p699_public_minimal_endpoint_selector_persistence_audit as p699
import low_term_total2_p701_completion_form_reuse_audit as p701
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p702_factor_substitution_target_verification_probe.json"
DEFAULT_P701 = STATE_DIR / "low_term_total2_p701_completion_form_reuse_audit_probe.json"
ORDER = p697.ORDER


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def resolve_completion_index(args: argparse.Namespace) -> int:
    if args.completion_form_index is not None:
        return int_value(args.completion_form_index)
    p701_payload = load_json(Path(args.p701))
    summary = p701_payload.get("summary") or {}
    if summary.get("best_completion_form_index") is not None:
        return int_value(summary.get("best_completion_form_index"))
    return 16


def p701_surface_args(args: argparse.Namespace) -> SimpleNamespace:
    return SimpleNamespace(
        certificate=args.certificate,
        max_cases=args.max_cases,
        max_endpoint_leaves=args.max_endpoint_leaves,
        p698=args.p698,
        product=Path(args.product),
        sample_limit=args.sample_limit,
        source=Path(args.source),
        target=args.target,
    )


def p701_training_records(args: argparse.Namespace, priority_columns: set[int]) -> list[dict[str, Any]]:
    p698_payload = p699.load_json(Path(args.p698))
    calibration_args = SimpleNamespace(
        certificate=args.certificate,
        max_cases=args.max_cases,
        max_endpoint_leaves=args.max_endpoint_leaves,
        product=str(p699.DEFAULT_SURFACES[0][2]),
        sample_limit=args.sample_limit,
        source=str(p699.DEFAULT_SURFACES[0][1]),
        target=args.target,
    )
    _verifier, _meta, calibration_records = p699.collect_surface_records(
        calibration_args,
        Path(p699.DEFAULT_SURFACES[0][1]),
        Path(p699.DEFAULT_SURFACES[0][2]),
        priority_columns,
    )
    return p699.train_records_from_p698(p698_payload, calibration_records)


def reconstruct_p701_row_union(args: argparse.Namespace) -> dict[str, Any]:
    priority_columns = p693.parse_columns(args.priority_columns)
    surface_args = p701_surface_args(args)
    verifier, context_by_row, surface_meta, records = p701.collect_records_and_contexts(
        surface_args,
        priority_columns,
    )
    training_records = p701_training_records(args, priority_columns)
    stage_records = p701.stage_selector_records(records, training_records)
    by_index = p701.records_by_index(records)
    completion_index = resolve_completion_index(args)
    if completion_index not in by_index:
        raise ValueError(f"completion form index {completion_index} not found in P701 surface")
    completion_record = by_index[completion_index]
    chosen_records = stage_records + [completion_record]
    replay = p701.row_union_replay(verifier, context_by_row, chosen_records, priority_columns)
    return {
        "chosen_records": chosen_records,
        "completion_form_index": completion_index,
        "completion_record": completion_record,
        "context_by_row": context_by_row,
        "priority_columns": priority_columns,
        "replay": replay,
        "stage_records": stage_records,
        "surface_meta": surface_meta,
        "surface_records": records,
        "surface_record_count": len(records),
        "verifier": verifier,
    }


def factor_values_from_state(state: dict[str, Any]) -> dict[int, dict[str, Any]]:
    values: dict[int, dict[str, Any]] = {}
    for column in state.get("columns") or []:
        index = int_value(column.get("column"))
        if column.get("derivable"):
            values[index] = {
                "combination_row_count": int_value(column.get("combination_row_count")),
                "factor_variable": f"F:{ORDER}:column={index}",
                "value": int_value(column.get("value")) % ORDER,
            }
    return values


def support(coeffs: list[int], order: int) -> list[int]:
    return [index for index, value in enumerate(coeffs) if value % order]


def public_secret_matches(verifier: Any, built: dict[str, Any], candidate: int | None) -> bool:
    if candidate is None:
        return False
    return (
        verifier.mul_point(
            int(candidate) % int(built["order"]),
            built["base"],
            built["ainvs"],
            int(built["p"]),
        )
        == built["public"]
    )


def substitute_record(
    verifier: Any,
    record: dict[str, Any],
    record_index: int,
    factor_count: int,
    factor_values: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    form = record.get("form") or {}
    q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, ORDER, factor_count)
    form_support = support(factor_coeffs, ORDER)
    missing = [index for index in form_support if index not in factor_values]
    recovered: int | None = None
    if q_coeff % ORDER == 0:
        status = "Q_COEFF_ZERO"
    elif missing:
        status = "MISSING_FACTOR_VALUES"
    else:
        known_sum = sum(
            factor_coeffs[index] * int_value(factor_values[index].get("value"))
            for index in form_support
        ) % ORDER
        recovered = ((rhs - known_sum) * pow(q_coeff % ORDER, -1, ORDER)) % ORDER
        status = "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"
    built = record.get("_built") or {}
    public_key_verified = public_secret_matches(verifier, built, recovered) if built else False
    hidden_secret = int_value(built.get("secret")) % ORDER if built.get("secret") is not None else None
    return {
        "derived_secret": recovered,
        "factor_support": form_support,
        "form_index": int_value(record.get("form_index")),
        "hidden_secret": hidden_secret,
        "matches_hidden_secret": bool(recovered is not None and hidden_secret is not None and recovered == hidden_secret),
        "missing_factor_columns": missing,
        "public_key_verified": public_key_verified,
        "q_coeff": q_coeff % ORDER,
        "record_index": record_index,
        "row_key": str(record.get("row_key")),
        "rhs": rhs % ORDER,
        "source_endpoint_form_index": record.get("_endpoint_form_index"),
        "status": status,
    }


def compact_relation(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "canonical_coeffs": row.get("canonical_coeffs"),
        "canonical_rhs": row.get("canonical_rhs"),
        "factor_support": row.get("factor_support"),
        "multiplicity": row.get("multiplicity"),
        "pair": row.get("pair"),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if summary["public_key_verified_secret_count"] and not summary["false_public_secret_count"]:
        if summary["row_union_charge_over_rho"] <= 1.0 and summary["augmented_rank"] == summary["factor_count"]:
            return "P702_FACTOR_SUBSTITUTION_DERIVES_VERIFIED_TARGET_SECRET_BELOW_RHO"
        return "P702_FACTOR_SUBSTITUTION_DERIVES_VERIFIED_TARGET_SECRET_ABOVE_RHO"
    if summary["unique_derived_secret_count"] == 1 and summary["recoverable_form_count"]:
        return "P702_FACTOR_SUBSTITUTION_CONSISTENT_SECRET_UNVERIFIED"
    if summary["recoverable_form_count"]:
        return "NEGATIVE_RESULT_P702_FACTOR_SUBSTITUTION_INCONSISTENT"
    return "NEGATIVE_RESULT_P702_NO_FACTOR_SUBSTITUTION_TARGET_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    reconstructed = reconstruct_p701_row_union(args)
    verifier = reconstructed["verifier"]
    priority_columns = reconstructed["priority_columns"]
    replay = reconstructed["replay"]
    replay_records = replay["replayed_records"]
    base, excluded_candidates, bank_meta = p697.base_bank(
        [Path(path) for path in (args.certificate or [str(path) for path in p697.p690.DEFAULT_CERTIFICATE_PATHS])]
    )
    base_state = p697.bank_state(base)
    union = p697.union_derive(verifier, replay_records)
    endpoint_cert = p697.pseudo_certificate(
        "p702_p701_row_union_endpoint",
        replay_records,
        args.target,
        union,
    )
    endpoint_state = p697.bank_state([endpoint_cert])
    augmented_state = p697.bank_state(base + [endpoint_cert])
    factor_values = factor_values_from_state(augmented_state)
    substitution_reports = [
        substitute_record(
            verifier,
            record,
            index,
            int_value(augmented_state.get("factor_count")),
            factor_values,
        )
        for index, record in enumerate(replay_records)
    ]
    status_counts: Counter[str] = Counter(report["status"] for report in substitution_reports)
    derived_secret_counts: Counter[str] = Counter(
        str(report["derived_secret"])
        for report in substitution_reports
        if report.get("derived_secret") is not None
    )
    verified_secret_counts: Counter[str] = Counter(
        str(report["derived_secret"])
        for report in substitution_reports
        if report.get("derived_secret") is not None and report.get("public_key_verified")
    )
    false_public_secret_count = sum(
        1
        for report in substitution_reports
        if report.get("derived_secret") is not None and not report.get("public_key_verified")
    )
    row_union_charge = float_value(replay.get("row_replay_charge_over_rho"))
    summary = {
        "augmented_missing_columns": augmented_state["missing_columns"],
        "augmented_rank": int_value(augmented_state["rank"]),
        "base_missing_columns": base_state["missing_columns"],
        "base_rank": int_value(base_state["rank"]),
        "completion_form_index": reconstructed["completion_form_index"],
        "derived_factor_column_count": len(factor_values),
        "endpoint_unique_factor_relation_count": len(endpoint_state["unique"]),
        "excluded_p690_candidate_count": len(excluded_candidates),
        "factor_count": int_value(augmented_state.get("factor_count")),
        "false_public_secret_count": false_public_secret_count,
        "public_key_verified_secret_count": len(verified_secret_counts),
        "recoverable_form_count": status_counts["TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION"],
        "replayed_record_count": len(replay_records),
        "row_union_charge_over_rho": row_union_charge,
        "row_union_target_forms_preserved": bool(replay.get("target_forms_preserved")),
        "stage_form_indices": [
            int_value(record.get("_endpoint_form_index"))
            for record in reconstructed["stage_records"]
        ],
        "unique_derived_secret_count": len(derived_secret_counts),
        "union_public_key_verified": bool(union.get("union_public_key_verified")),
        "union_rank": int_value(union.get("union_rank")),
    }
    claim_status = determine_claim(summary)
    return {
        "artifacts": {
            "base_certificates": bank_meta["paths"],
            "p698": str(Path(args.p698)),
            "p701": str(Path(args.p701)),
            "product": str(Path(args.product)),
            "source": str(Path(args.source)),
        },
        "claim_status": claim_status,
        "created_at": p697.p696.now_iso(),
        "derived_factor_values": [factor_values[index] for index in sorted(factor_values)],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor values live in the current order-9887 low-term factor-column namespace.",
            "HEURISTIC: this verifies the P701 closure against its own preserved endpoint forms; it is not a fresh-target generalization test.",
            "NO DEPLOYED-CURVE CLAIM: relation generation, sparse linear algebra, target descent generality, and asymptotics remain open.",
        ],
        "method": "p702_factor_substitution_target_verification",
        "parameters": {
            "completion_form_index": reconstructed["completion_form_index"],
            "priority_columns": sorted(priority_columns),
            "target": args.target,
        },
        "p701_row_union_replay": {
            "missing_target_form_count": replay.get("missing_target_form_count"),
            "row_replay_charge_over_rho": replay.get("row_replay_charge_over_rho"),
            "row_replays": replay.get("row_replays"),
            "target_form_count": replay.get("target_form_count"),
            "target_forms_preserved": replay.get("target_forms_preserved"),
        },
        "rank_state": {
            "augmented_rank": augmented_state["rank"],
            "augmented_unique_relation_count": len(augmented_state["unique"]),
            "base_rank": base_state["rank"],
            "base_unique_relation_count": len(base_state["unique"]),
            "endpoint_rank": endpoint_state["rank"],
            "endpoint_unique_relations": [compact_relation(row) for row in endpoint_state["unique"]],
            "factor_count": augmented_state["factor_count"],
            "missing_columns": augmented_state["missing_columns"],
        },
        "schema": "ecdlp.low_term_total2_p702_factor_substitution_target_verification.v1",
        "secret_counts": {
            "derived": dict(sorted(derived_secret_counts.items(), key=lambda item: int(item[0]))),
            "public_key_verified": dict(sorted(verified_secret_counts.items(), key=lambda item: int(item[0]))),
        },
        "status_counts": dict(sorted(status_counts.items())),
        "substitution_reports": substitution_reports,
        "summary": summary,
        "surface_meta": reconstructed["surface_meta"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default=str(p701.DEFAULT_SOURCE))
    parser.add_argument("--product", default=str(p701.DEFAULT_PRODUCT))
    parser.add_argument("--target", default="67.a1@9803")
    parser.add_argument("--priority-columns", default="0,15")
    parser.add_argument("--p698", default=str(p701.DEFAULT_P698))
    parser.add_argument("--p701", default=str(DEFAULT_P701))
    parser.add_argument("--completion-form-index", type=int, default=None)
    parser.add_argument("--certificate", action="append", default=None, help="Base certificate artifact to include.")
    parser.add_argument("--max-cases", type=int, default=0)
    parser.add_argument("--max-endpoint-leaves", type=int, default=0)
    parser.add_argument("--sample-limit", type=int, default=12)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    print(json.dumps({"claim_status": payload["claim_status"], "summary": payload["summary"]}, indent=2, sort_keys=True))
    print(json.dumps({"secret_counts": payload["secret_counts"], "status_counts": payload["status_counts"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
