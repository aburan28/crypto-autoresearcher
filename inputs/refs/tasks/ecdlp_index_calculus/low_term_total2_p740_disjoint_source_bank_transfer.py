#!/usr/bin/env python3
"""P740 disjoint-source factor-bank transfer audit for order 11779.

P739 showed that P738's bounded target-descent signal survives several family
holdouts, but the disjoint-target axis was untestable.  This audit mines an
older full-rank order-11779 factor-relation bank and asks a narrower useful
question: can factor values derived from source/window-disjoint training
certificates recover the newer P738 target forms without any P738 training?
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import low_term_total2_factor_substitution_descent_audit as substitution
import low_term_total2_target_eliminated_factor_relation_bank as factor_bank


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAINING_BANK = (
    STATE_DIR
    / "low_term_total2_target_eliminated_factor_relation_bank_dual_order_fullrank_11779_9887_probe.json"
)
DEFAULT_P738 = STATE_DIR / "low_term_total2_p738_modular_coefficient_descent_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p740_disjoint_source_bank_transfer_probe.json"
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_order11779_p740_disjoint_source_bank_transfer.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def int_value(value: Any, default: int = 0) -> int:
    return factor_bank.int_value(value, default)


def selected(cert: dict[str, Any]) -> dict[str, Any]:
    value = cert.get("selected")
    return value if isinstance(value, dict) else {}


def selected_target(cert: dict[str, Any]) -> str:
    return str(selected(cert).get("target") or "unknown")


def selected_source(cert: dict[str, Any]) -> str:
    return str(cert.get("source") or selected(cert).get("source") or cert.get("_artifact") or "")


def transfer_index(cert: dict[str, Any]) -> int:
    return int_value(selected(cert).get("transfer_index"))


def cert_index(cert: dict[str, Any]) -> int:
    return int_value(cert.get("_global_index"), int_value(cert.get("_artifact_offset")))


def parse_window(raw: Any) -> tuple[int, int] | None:
    if isinstance(raw, (list, tuple)) and len(raw) >= 2:
        return int_value(raw[0]), int_value(raw[1])
    text = str(raw or "")
    match = re.search(r"(\d+)[_-](\d+)", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def cert_window(cert: dict[str, Any]) -> tuple[int, int] | None:
    return parse_window(cert.get("window") or selected(cert).get("window"))


def windows_overlap(left: tuple[int, int] | None, right: tuple[int, int] | None) -> bool:
    if left is None or right is None:
        return False
    lo1, hi1 = sorted(left)
    lo2, hi2 = sorted(right)
    return lo1 <= hi2 and lo2 <= hi1


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


def training_paths_from_bank(path: Path) -> list[Path]:
    payload = load_json(path)
    paths = [
        Path(str(item))
        for item in (payload.get("artifacts") or {}).get("certificates") or []
        if str(item).strip()
    ]
    if not paths:
        raise ValueError(f"training bank has no artifact certificate list: {path}")
    return paths


def annotate_p738_certificates(p738: dict[str, Any], artifact: Path) -> list[dict[str, Any]]:
    certificates: list[dict[str, Any]] = []
    for index, cert in enumerate(p738.get("certificates") or []):
        if not isinstance(cert, dict):
            continue
        item = dict(cert)
        item["_artifact"] = str(artifact)
        item["_artifact_offset"] = int_value(item.get("_artifact_offset"), index)
        item["_global_index"] = int_value(item.get("_global_index"), index)
        certificates.append(item)
    return certificates


def target_counts(certs: list[dict[str, Any]], order: int) -> dict[str, int]:
    counts = Counter(
        selected_target(cert)
        for cert in certs
        if int_value(cert.get("order")) == order
    )
    return dict(sorted(counts.items()))


def source_window_overlap_report(
    training: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    order: int,
) -> dict[str, Any]:
    training_order = [cert for cert in training if int_value(cert.get("order")) == order]
    candidate_order = [cert for cert in candidates if int_value(cert.get("order")) == order]
    training_artifacts = {str(cert.get("_artifact") or "") for cert in training_order}
    candidate_sources = {selected_source(cert) for cert in candidate_order}
    candidate_artifacts = {str(cert.get("_artifact") or "") for cert in candidate_order}
    artifact_overlap = sorted((training_artifacts & candidate_sources) | (training_artifacts & candidate_artifacts))
    transfer_overlap = sorted(
        set(transfer_index(cert) for cert in training_order)
        & set(transfer_index(cert) for cert in candidate_order)
    )
    window_overlaps = []
    training_windows = [(cert, cert_window(cert)) for cert in training_order]
    candidate_windows = [(cert, cert_window(cert)) for cert in candidate_order]
    for train_cert, train_window in training_windows:
        for candidate_cert, candidate_window in candidate_windows:
            if not windows_overlap(train_window, candidate_window):
                continue
            window_overlaps.append(
                {
                    "candidate_certificate_index": cert_index(candidate_cert),
                    "candidate_transfer_index": transfer_index(candidate_cert),
                    "candidate_window": list(candidate_window) if candidate_window else None,
                    "training_artifact": train_cert.get("_artifact"),
                    "training_certificate_index": cert_index(train_cert),
                    "training_transfer_index": transfer_index(train_cert),
                    "training_window": list(train_window) if train_window else None,
                }
            )
            if len(window_overlaps) >= 20:
                break
        if len(window_overlaps) >= 20:
            break
    return {
        "artifact_overlap_count": len(artifact_overlap),
        "artifact_overlaps": artifact_overlap[:20],
        "candidate_artifact_count": len(candidate_artifacts),
        "candidate_source_count": len(candidate_sources),
        "training_artifact_count": len(training_artifacts),
        "transfer_overlap_count": len(transfer_overlap),
        "transfer_overlaps": transfer_overlap[:20],
        "window_overlap_count_sampled": len(window_overlaps),
        "window_overlap_samples": window_overlaps,
    }


def form_support(form: dict[str, Any], order: int) -> list[int]:
    coeffs = [int_value(value) % order for value in form.get("coeffs") or []]
    return [index for index, coeff in enumerate(coeffs[1:]) if coeff % order]


def audit_candidates(
    training: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    order: int,
) -> dict[str, Any]:
    training_order = [cert for cert in training if int_value(cert.get("order")) == order]
    candidate_order = [cert for cert in candidates if int_value(cert.get("order")) == order]
    factor_count = substitution.factor_count_for(training_order + candidate_order, order)
    derivation = substitution.derive_factor_values(training_order, order, factor_count)
    factor_values = derivation["factor_values"]
    status_counts: Counter[str] = Counter()
    missing_counts: Counter[str] = Counter()
    verified_forms = 0
    false_forms = 0
    verified_candidates = 0
    false_candidates = 0
    candidate_reports = []
    support_size_values = []
    for cert in candidate_order:
        reports = []
        cert_verified = 0
        cert_false = 0
        for form_index, form in enumerate(cert.get("forms") or []):
            if not isinstance(form, dict):
                continue
            support = form_support(form, order)
            support_size_values.append(len(support))
            report = substitution.audit_candidate_form(cert, form, form_index, order, factor_count, factor_values)
            status_counts[str(report.get("status"))] += 1
            for column in report.get("missing_factor_columns") or []:
                missing_counts[str(column)] += 1
            if report.get("verified_matches_expected"):
                verified_forms += 1
                cert_verified += 1
            elif report.get("status") == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
                false_forms += 1
                cert_false += 1
            if report.get("verified_matches_expected") or report.get("status") == "TARGET_RECOVERED_BY_FACTOR_SUBSTITUTION":
                reports.append(report)
        if cert_verified:
            verified_candidates += 1
        if cert_false:
            false_candidates += 1
        if cert_verified or cert_false or len(candidate_reports) < 16:
            candidate_reports.append(
                {
                    "candidate_certificate_index": cert_index(cert),
                    "candidate_source": selected_source(cert),
                    "false_recoverable_form_count": cert_false,
                    "form_reports": reports[:8],
                    "target": selected_target(cert),
                    "transfer_index": transfer_index(cert),
                    "verified_recoverable_form_count": cert_verified,
                    "window": cert.get("window") or selected(cert).get("window"),
                }
            )
    return {
        "candidate_certificate_count": len(candidate_order),
        "candidate_form_count": sum(
            1
            for cert in candidate_order
            for form in cert.get("forms") or []
            if isinstance(form, dict)
        ),
        "candidate_reports": candidate_reports[:40],
        "candidate_with_false_recovery_count": false_candidates,
        "candidate_with_verified_recovery_count": verified_candidates,
        "derived_factor_column_count": len(factor_values),
        "derived_factor_columns": sorted(factor_values),
        "factor_column_count": factor_count,
        "factor_rank": derivation["rank"],
        "false_recoverable_form_count": false_forms,
        "form_support_size_stats": stat(support_size_values),
        "matrix_consistent": derivation["matrix_consistent"],
        "missing_factor_column_counts": dict(sorted(missing_counts.items(), key=lambda item: int(item[0]))),
        "status_counts": dict(sorted(status_counts.items())),
        "training_certificate_count": len(training_order),
        "training_relation_count": derivation["relation_count"],
        "training_unique_relation_count": derivation["unique_relation_count"],
        "verified_recoverable_form_count": verified_forms,
    }


def determine_claim(audit: dict[str, Any], overlap: dict[str, Any], target_inventory: dict[str, Any]) -> str:
    if int_value(audit.get("false_recoverable_form_count")):
        return "P740_SOURCE_BANK_FALSE_RECOVERY_NEEDS_REVIEW"
    if int_value(target_inventory.get("disjoint_order11779_candidate_target_count")) and int_value(
        audit.get("verified_recoverable_form_count")
    ):
        return "P740_DISJOINT_TARGET_FACTOR_BANK_TRANSFER_SIGNAL"
    if (
        int_value(audit.get("verified_recoverable_form_count"))
        and not int_value(overlap.get("artifact_overlap_count"))
        and not int_value(overlap.get("transfer_overlap_count"))
        and not int_value(overlap.get("window_overlap_count_sampled"))
    ):
        return "P740_DISJOINT_SOURCE_FACTOR_BANK_TRANSFER_SIGNAL"
    if int_value(audit.get("verified_recoverable_form_count")):
        return "P740_FACTOR_BANK_TRANSFER_SIGNAL_WITH_OVERLAP_BOUNDARY"
    return "NEGATIVE_RESULT_P740_SOURCE_BANK_TRANSFER_NO_TARGET_RECOVERY"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    order = int_value(args.order)
    training_bank = Path(args.training_bank)
    p738_path = Path(args.candidate_p738)
    training_paths = training_paths_from_bank(training_bank)
    training_certs = factor_bank.load_certificates(training_paths)
    p738 = load_json(p738_path)
    candidate_certs = annotate_p738_certificates(p738, p738_path)
    if not candidate_certs:
        raise ValueError("candidate P738 probe does not contain full certificates")
    transfer_audit = audit_candidates(training_certs, candidate_certs, order)
    overlap = source_window_overlap_report(training_certs, candidate_certs, order)
    training_targets = target_counts(training_certs, order)
    candidate_targets = target_counts(candidate_certs, order)
    disjoint_candidate_targets = sorted(set(candidate_targets) - set(training_targets))
    target_inventory = {
        "candidate_targets": candidate_targets,
        "disjoint_order11779_candidate_target_count": len(disjoint_candidate_targets),
        "disjoint_order11779_candidate_targets": disjoint_candidate_targets,
        "training_targets": training_targets,
    }
    payload = {
        "artifacts": {
            "candidate_p738": str(p738_path),
            "contract": str(DEFAULT_CONTRACT),
            "training_bank": str(training_bank),
            "training_certificate_paths": [str(path) for path in training_paths],
        },
        "claim_status": "",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: factor columns are the local verifier order-specific factor-base namespace.",
            "SOURCE-DISJOINT: success excludes P738 certificates from training and checks artifact, transfer, and window overlap.",
            "NO DISJOINT-TARGET CLAIM unless disjoint_order11779_candidate_target_count is positive.",
            "NO DEPLOYED-CURVE CLAIM: relation generation, sparse linear algebra, arbitrary target descent, and large-prime scaling remain open.",
        ],
        "method": "p740_disjoint_source_bank_transfer",
        "order": order,
        "parameters": {
            "candidate_p738_claim_status": p738.get("claim_status"),
            "pollard_rho_baseline_steps_floor": int(order**0.5),
            "training_bank_claim_status": load_json(training_bank).get("claim_status"),
        },
        "source_window_overlap": overlap,
        "target_inventory": target_inventory,
        "transfer_audit": transfer_audit,
        "schema": "ecdlp.low_term_total2_p740_disjoint_source_bank_transfer.v1",
    }
    payload["claim_status"] = determine_claim(transfer_audit, overlap, target_inventory)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-p738", default=str(DEFAULT_P738))
    parser.add_argument("--order", type=int, default=11779)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--training-bank", default=str(DEFAULT_TRAINING_BANK))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    compact = {
        "claim_status": payload["claim_status"],
        "order": payload["order"],
        "source_window_overlap": payload["source_window_overlap"],
        "target_inventory": payload["target_inventory"],
        "transfer_summary": {
            key: value
            for key, value in payload["transfer_audit"].items()
            if key not in {"candidate_reports", "derived_factor_columns"}
        },
    }
    print(json.dumps(compact, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
