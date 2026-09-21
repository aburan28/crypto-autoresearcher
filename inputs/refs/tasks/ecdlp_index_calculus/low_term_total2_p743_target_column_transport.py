#!/usr/bin/env python3
"""P743 target-specific factor-column transport audit.

P742 showed that raw P740 factor values do not transfer from target
``22050.cf1@11731`` to ``67.a1@11789`` even though all visible candidate
columns are derived. This script tests the next narrower hypothesis: a stable
target-specific additive correction may explain the disjoint target's relation
forms and generalize from calibration certificates to held-out certificates.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import low_term_total2_factor_substitution_descent_audit as substitution
import low_term_total2_p740_disjoint_source_bank_transfer as p740
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_P742 = STATE_DIR / "low_term_total2_p742_disjoint_target_relation_transfer_probe.json"
DEFAULT_TRAINING_BANK = (
    STATE_DIR
    / "low_term_total2_target_eliminated_factor_relation_bank_dual_order_fullrank_11779_9887_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p743_target_column_transport_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p743_target_column_transport.md"
SCHEMA = "ecdlp.low_term_total2_p743_target_column_transport.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def stat(values: list[int | float]) -> dict[str, Any]:
    if not values:
        return {"count": 0, "max": None, "mean": None, "median": None, "min": None}
    return {
        "count": len(values),
        "max": max(values),
        "mean": round(mean(values), 8),
        "median": median(values),
        "min": min(values),
    }


def annotate_certificates(certs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []
    for index, cert in enumerate(certs):
        item = dict(cert)
        item["_artifact"] = str(cert.get("source") or "p743_p742_candidate_certificate")
        item["_artifact_offset"] = index
        item["_global_index"] = index
        annotated.append(item)
    return annotated


def usable_candidate_certificates(p742: dict[str, Any]) -> list[dict[str, Any]]:
    certs = [
        cert
        for cert in p742.get("candidate_certificates") or []
        if isinstance(cert, dict)
        and cert.get("certificate_status") == "P742_DISJOINT_TARGET_RELATION_CERTIFICATE_PASS"
        and cert.get("expected_secret") is not None
        and int_value(cert.get("forms_count")) > 0
    ]
    return annotate_certificates(certs)


def derive_old_factor_values(training_bank: Path, candidate_certs: list[dict[str, Any]], order: int) -> dict[str, Any]:
    training_paths = p740.training_paths_from_bank(training_bank)
    training_certs = factor_bank.load_certificates(training_paths)
    factor_count = substitution.factor_count_for(training_certs + candidate_certs, order)
    derivation = substitution.derive_factor_values(training_certs, order, factor_count)
    return {
        "derivation": derivation,
        "factor_count": factor_count,
        "training_certificate_count": len([cert for cert in training_certs if int_value(cert.get("order")) == order]),
        "training_paths": [str(path) for path in training_paths],
    }


def factor_value_map(derivation: dict[str, Any]) -> dict[int, int]:
    values = {}
    for key, row in (derivation.get("factor_values") or {}).items():
        values[int(key)] = int_value(row.get("value"))
    return values


def visible_columns(certs: list[dict[str, Any]], order: int) -> list[int]:
    cols = set()
    for cert in certs:
        for form in cert.get("forms") or []:
            q_coeff, factor_coeffs, _rhs = factor_bank.form_parts(form, order, 0)
            if q_coeff % order == 0:
                continue
            cols.update(index for index, coeff in enumerate(factor_coeffs) if coeff % order)
    return sorted(cols)


def correction_equations(
    certs: list[dict[str, Any]],
    order: int,
    factor_count: int,
    old_values: dict[int, int],
) -> tuple[list[list[int]], list[int], list[dict[str, Any]]]:
    matrix: list[list[int]] = []
    rhs_values: list[int] = []
    rows: list[dict[str, Any]] = []
    for cert in certs:
        expected = int_value(cert.get("expected_secret")) % order
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
            if q_coeff % order == 0:
                continue
            old_sum = sum(
                factor_coeffs[index] * old_values.get(index, 0)
                for index in range(factor_count)
            ) % order
            residual = (rhs - q_coeff * expected - old_sum) % order
            matrix.append([coeff % order for coeff in factor_coeffs])
            rhs_values.append(residual)
            rows.append(
                {
                    "certificate_index": int_value(cert.get("_global_index")),
                    "expected_secret": expected,
                    "factor_support": [index for index, coeff in enumerate(factor_coeffs) if coeff % order],
                    "form_index": form_index,
                    "old_recovered_secret": ((rhs - old_sum) * pow(q_coeff % order, -1, order)) % order,
                    "q_coeff": q_coeff % order,
                    "residual_rhs": residual,
                    "rhs": rhs % order,
                    "target": (cert.get("selected") or {}).get("target"),
                }
            )
    return matrix, rhs_values, rows


def solve_correction(
    train: list[dict[str, Any]],
    order: int,
    factor_count: int,
    old_values: dict[int, int],
) -> dict[str, Any]:
    matrix, rhs_values, rows = correction_equations(train, order, factor_count, old_values)
    rank = factor_bank.rank_mod(matrix, order)
    augmented_rank = factor_bank.rank_mod(
        [row + [rhs_values[index]] for index, row in enumerate(matrix)],
        order,
    )
    solution = factor_bank.solve_mod(matrix, rhs_values, order)
    correction = {index: value % order for index, value in enumerate(solution or []) if value % order}
    touched = sorted({col for row in rows for col in row["factor_support"]})
    return {
        "augmented_rank": augmented_rank,
        "consistent": augmented_rank == rank,
        "correction": correction,
        "correction_nonzero_count": len(correction),
        "equation_count": len(matrix),
        "rank": rank,
        "solved": solution is not None,
        "touched_columns": touched,
    }


def recover_with_correction(
    test: list[dict[str, Any]],
    order: int,
    factor_count: int,
    old_values: dict[int, int],
    correction: dict[int, int],
) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    verified = 0
    false = 0
    missing = {}
    reports = []
    for cert in test:
        expected = int_value(cert.get("expected_secret")) % order
        cert_verified = 0
        cert_false = 0
        form_reports = []
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            q_coeff, factor_coeffs, rhs = factor_bank.form_parts(form, order, factor_count)
            support = [index for index, coeff in enumerate(factor_coeffs) if coeff % order]
            if q_coeff % order == 0:
                status = "Q_COEFF_ZERO"
                recovered = None
            else:
                known_sum = sum(
                    factor_coeffs[index] * ((old_values.get(index, 0) + correction.get(index, 0)) % order)
                    for index in range(factor_count)
                ) % order
                recovered = ((rhs - known_sum) * pow(q_coeff % order, -1, order)) % order
                status = "TARGET_RECOVERED_BY_CORRECTED_FACTOR_SUBSTITUTION"
            status_counts[status] = status_counts.get(status, 0) + 1
            ok = bool(recovered is not None and recovered == expected)
            if ok:
                verified += 1
                cert_verified += 1
            elif recovered is not None:
                false += 1
                cert_false += 1
            for col in support:
                if col not in old_values and col not in correction:
                    missing[str(col)] = missing.get(str(col), 0) + 1
            form_reports.append(
                {
                    "derived_secret": recovered,
                    "expected_secret": expected,
                    "factor_support": support,
                    "form_index": form_index,
                    "q_coeff": q_coeff % order,
                    "status": status,
                    "verified_matches_expected": ok,
                }
            )
        reports.append(
            {
                "certificate_index": int_value(cert.get("_global_index")),
                "false_recoverable_form_count": cert_false,
                "source": cert.get("source"),
                "target": (cert.get("selected") or {}).get("target"),
                "verified_recoverable_form_count": cert_verified,
                "form_reports": form_reports[:4],
            }
        )
    total_forms = verified + false + status_counts.get("Q_COEFF_ZERO", 0)
    return {
        "candidate_reports": reports[:20],
        "false_recoverable_form_count": false,
        "missing_factor_column_counts": dict(sorted(missing.items(), key=lambda item: int(item[0]))),
        "status_counts": dict(sorted(status_counts.items())),
        "test_certificate_count": len(test),
        "test_form_count": total_forms,
        "verified_recoverable_form_count": verified,
    }


def split_report(
    name: str,
    train: list[dict[str, Any]],
    test: list[dict[str, Any]],
    order: int,
    factor_count: int,
    old_values: dict[int, int],
) -> dict[str, Any]:
    correction = solve_correction(train, order, factor_count, old_values)
    if correction["solved"]:
        result = recover_with_correction(test, order, factor_count, old_values, correction["correction"])
    else:
        result = {
            "candidate_reports": [],
            "false_recoverable_form_count": 0,
            "missing_factor_column_counts": {},
            "status_counts": {},
            "test_certificate_count": len(test),
            "test_form_count": sum(int_value(cert.get("forms_count")) for cert in test),
            "verified_recoverable_form_count": 0,
        }
    passed = (
        correction["solved"]
        and int_value(result.get("test_form_count")) > 0
        and result["verified_recoverable_form_count"] == result["test_form_count"]
        and result["false_recoverable_form_count"] == 0
    )
    return {
        "claim_status": (
            "P743_SPLIT_CORRECTION_HELDOUT_RECOVERY"
            if passed
            else "NEGATIVE_RESULT_P743_SPLIT_CORRECTION_HELDOUT_FAILURE"
        ),
        "correction": {
            key: value
            for key, value in correction.items()
            if key != "correction"
        },
        "correction_columns_sample": [
            {"column": index, "delta": correction["correction"][index]}
            for index in sorted(correction.get("correction") or {})[:16]
        ],
        "name": name,
        "passed": passed,
        "test_certificate_indices": [int_value(cert.get("_global_index")) for cert in test],
        "train_certificate_indices": [int_value(cert.get("_global_index")) for cert in train],
        "transfer_result": result,
    }


def build_splits(certs: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]:
    splits: list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]] = []
    splits.append(("all_fit_self_control", certs, certs))
    for size in [1, 2, 3, 4, 6, 8, 10, 11]:
        if size < len(certs):
            splits.append((f"prefix_train_{size}_heldout_{len(certs) - size}", certs[:size], certs[size:]))
    for index in range(len(certs)):
        train = [cert for pos, cert in enumerate(certs) if pos != index]
        test = [certs[index]]
        splits.append((f"leave_one_certificate_out_{index}", train, test))
    return splits


def determine_claim(split_reports: list[dict[str, Any]]) -> str:
    loo = [row for row in split_reports if str(row.get("name", "")).startswith("leave_one_certificate_out_")]
    prefix = [row for row in split_reports if str(row.get("name", "")).startswith("prefix_train_")]
    all_fit = next((row for row in split_reports if row.get("name") == "all_fit_self_control"), None)
    if loo and all(row.get("passed") for row in loo) and any(row.get("passed") for row in prefix):
        return "P743_TARGET_COLUMN_TRANSPORT_HELDOUT_SIGNAL"
    if all_fit and all_fit.get("passed") and any(row.get("passed") for row in loo):
        return "P743_TARGET_COLUMN_TRANSPORT_PARTIAL_HELDOUT_SIGNAL"
    if all_fit and all_fit.get("passed"):
        return "P743_COLUMN_CORRECTION_SELF_CONSISTENT_HELDOUT_OPEN"
    return "NEGATIVE_RESULT_P743_COLUMN_CORRECTION_INCONSISTENT"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p742 = load_json(Path(args.p742))
    certs = usable_candidate_certificates(p742)
    if not certs:
        raise ValueError("P742 artifact contains no usable candidate certificates")
    order = int_value(certs[0].get("order"))
    old = derive_old_factor_values(Path(args.training_bank), certs, order)
    old_values = factor_value_map(old["derivation"])
    factor_count = old["factor_count"]
    splits = build_splits(certs)
    reports = [
        split_report(name, train, test, order, factor_count, old_values)
        for name, train, test in splits
    ]
    prefix_passes = [row for row in reports if str(row.get("name", "")).startswith("prefix_train_") and row.get("passed")]
    loo_reports = [row for row in reports if str(row.get("name", "")).startswith("leave_one_certificate_out_")]
    payload = {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "p742": str(args.p742),
            "training_bank": str(args.training_bank),
            "training_certificate_paths": old["training_paths"],
        },
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "CALIBRATION-BOUND: corrections are fit from relation certificates with rowspace-derived benchmark secrets.",
            "MODEL-BOUND: correction columns live in the local verifier factor-column namespace.",
            "MANY-CHALLENGE SIGNAL ONLY: held-out challenge recovery after calibration is not a one-target faster-than-rho solver.",
            "NO DEPLOYED-CURVE CLAIM: fresh relation generation, target descent setup cost, and sparse linear algebra remain open.",
        ],
        "method": "p743_target_specific_additive_column_transport",
        "order": order,
        "parameters": {
            "candidate_certificate_count": len(certs),
            "factor_column_count": factor_count,
            "old_bank_derived_factor_columns": sorted(old_values),
            "p742_claim_status": p742.get("claim_status"),
            "raw_p742_false_recoverable_form_count": int_value((p742.get("transfer_audit") or {}).get("false_recoverable_form_count")),
            "raw_p742_verified_recoverable_form_count": int_value((p742.get("transfer_audit") or {}).get("verified_recoverable_form_count")),
            "target": (certs[0].get("selected") or {}).get("target"),
            "visible_candidate_columns": visible_columns(certs, order),
        },
        "schema": SCHEMA,
        "split_summary": {
            "all_fit_self_passed": bool(next((row for row in reports if row.get("name") == "all_fit_self_control"), {}).get("passed")),
            "leave_one_out_pass_count": sum(1 for row in loo_reports if row.get("passed")),
            "leave_one_out_split_count": len(loo_reports),
            "prefix_pass_count": len(prefix_passes),
            "prefix_split_count": sum(1 for row in reports if str(row.get("name", "")).startswith("prefix_train_")),
            "smallest_passing_prefix_train_count": min(
                [
                    int(str(row["name"]).split("_")[2])
                    for row in prefix_passes
                ],
                default=None,
            ),
        },
        "splits": reports,
        "training_derivation_summary": {
            "matrix_consistent": bool(old["derivation"].get("matrix_consistent")),
            "old_bank_factor_rank": int_value(old["derivation"].get("rank")),
            "old_bank_training_certificate_count": old["training_certificate_count"],
            "old_bank_unique_relation_count": int_value(old["derivation"].get("unique_relation_count")),
        },
    }
    payload["claim_status"] = determine_claim(reports)
    return payload


def summary_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    selected_splits = []
    for row in payload["splits"]:
        name = str(row.get("name"))
        if name == "all_fit_self_control" or name.startswith("prefix_train_") or name in {
            "leave_one_certificate_out_0",
            "leave_one_certificate_out_1",
            "leave_one_certificate_out_11",
        }:
            selected_splits.append(
                {
                    "claim_status": row["claim_status"],
                    "correction": row["correction"],
                    "name": name,
                    "passed": row["passed"],
                    "test_certificate_count": row["transfer_result"]["test_certificate_count"],
                    "test_form_count": row["transfer_result"]["test_form_count"],
                    "verified_recoverable_form_count": row["transfer_result"]["verified_recoverable_form_count"],
                    "false_recoverable_form_count": row["transfer_result"]["false_recoverable_form_count"],
                }
            )
    return {
        "schema": f"{SCHEMA}.summary",
        "created_at": payload["created_at"],
        "claim_status": payload["claim_status"],
        "honesty_boundary": payload["honesty_boundary"],
        "order": payload["order"],
        "parameters": payload["parameters"],
        "selected_splits": selected_splits,
        "split_summary": payload["split_summary"],
        "training_derivation_summary": payload["training_derivation_summary"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--p742", type=Path, default=DEFAULT_P742)
    parser.add_argument("--training-bank", type=Path, default=DEFAULT_TRAINING_BANK)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--summary-out", type=Path, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary_out = args.summary_out or args.out.with_name(args.out.stem.replace("_probe", "_summary") + args.out.suffix)
    summary = summary_from_payload(payload)
    write_json(summary_out, summary)
    print(f"wrote {args.out}")
    print(f"wrote {summary_out}")
    print(
        json.dumps(
            {
                "claim_status": summary["claim_status"],
                "parameters": summary["parameters"],
                "split_summary": summary["split_summary"],
                "training_derivation_summary": summary["training_derivation_summary"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
