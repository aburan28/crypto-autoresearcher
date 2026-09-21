#!/usr/bin/env python3
"""P977 p231 selected-corpus source-charge audit over the P872 import."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p977_p231_selected_corpus_source_charge.md"
DEFAULT_P872 = STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json"
DEFAULT_P976 = STATE_DIR / "low_term_total2_p976_fresh_disjoint_corpus_import_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p977_p231_selected_corpus_source_charge_probe.json"
SCHEMA = "ecdlp.low_term_total2_p977_p231_selected_corpus_source_charge.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256_file(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def float_value(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def round8(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 8)


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round8(float(numerator) / float(denominator))


def salt_number(row_key: str) -> int | None:
    match = re.search(r"salt(\d+)", str(row_key))
    if not match:
        return None
    return int(match.group(1))


def row_salts(cases: list[dict[str, Any]]) -> list[int]:
    salts: set[int] = set()
    for case in cases:
        for row_leaf in case.get("row_leaf_keys") or []:
            salt = salt_number(str(row_leaf.get("row_key")))
            if salt is not None:
                salts.add(salt)
    return sorted(salts)


def windows(cases: list[dict[str, Any]]) -> list[str]:
    return sorted({str(case.get("window")) for case in cases if case.get("window")})


def targets(cases: list[dict[str, Any]]) -> list[str]:
    return sorted({str(case.get("target")) for case in cases if case.get("target")})


def transfer_indices(cases: list[dict[str, Any]]) -> list[int]:
    return sorted({int_value(case.get("transfer_index")) for case in cases if case.get("transfer_index") is not None})


def direct_ratios(cases: list[dict[str, Any]]) -> list[float]:
    return [
        value
        for case in cases
        for value in [float_value(case.get("direct_ops_over_rho"))]
        if value is not None
    ]


def histogram(values: list[Any]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(value)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "leaf_selector": case.get("leaf_selector"),
        "p867_motif_verified_below_rho": bool(case.get("p867_motif_verified_below_rho")),
        "row_leaf_keys": case.get("row_leaf_keys"),
        "target": case.get("target"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "union_derived_secret": case.get("union_derived_secret"),
        "union_public_key_verified": bool(case.get("union_public_key_verified")),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": case.get("window"),
    }


def tier_summary(name: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    ratios = direct_ratios(cases)
    ratio_sum = sum(ratios)
    union_verified = [case for case in cases if case.get("union_public_key_verified")]
    p867_positive = [case for case in cases if case.get("p867_motif_verified_below_rho")]
    ranks = [case.get("union_rank") for case in cases if case.get("union_rank") is not None]
    relation_counts = [
        int_value(case.get("union_relation_count"))
        for case in cases
        if case.get("union_relation_count") is not None
    ]
    secrets = sorted({str(case.get("union_derived_secret")) for case in cases if case.get("union_derived_secret") is not None})
    return {
        "avg_direct_ops_over_rho": ratio(ratio_sum, len(ratios)) if ratios else None,
        "below_rho_count": sum(1 for value in ratios if value < 1.0),
        "count": len(cases),
        "distinct_secret_count": len(secrets),
        "distinct_secrets": secrets,
        "distinct_transfer_count": len(transfer_indices(cases)),
        "direct_ops_missing_count": len(cases) - len(ratios),
        "max_direct_ops_over_rho": round8(max(ratios)) if ratios else None,
        "min_direct_ops_over_rho": round8(min(ratios)) if ratios else None,
        "name": name,
        "p867_positive_count": len(p867_positive),
        "relation_count_sum": sum(relation_counts),
        "row_salts": row_salts(cases),
        "sample_cases": [compact_case(case) for case in cases[:5]],
        "target_count": len(targets(cases)),
        "targets": targets(cases),
        "transfer_indices": transfer_indices(cases),
        "union_rank_histogram": histogram(ranks),
        "union_verified_count": len(union_verified),
        "window_count": len(windows(cases)),
        "windows": windows(cases),
        "sum_direct_ops_over_rho": round8(ratio_sum),
    }


def p976_control_summary(p976: dict[str, Any]) -> dict[str, Any]:
    summary = p976.get("summary") or {}
    return {
        "p976_claim_is_import_ready": summary.get("claim_status") == "P976_FRESH_DISJOINT_P231_CORPUS_IMPORTED_FOR_NEXT_CACHE_STRESS",
        "p976_controls_pass": bool(summary.get("controls_pass")),
        "p976_primary_import_ready": bool(summary.get("primary_import_ready")),
        "p976_primary_is_p872": summary.get("primary_name") == "p872_two_stage_22050",
        "p976_reconstruction_errors_zero": int_value(summary.get("primary_reconstruction_error_count")) == 0,
        "p976_selected_count_is_30": int_value(summary.get("primary_selected_count")) == 30,
        "p976_union_verified_count_is_21": int_value((p976.get("candidate_corpora") or [{}])[0].get("union_verified_count")) == 21,
        "p976_p867_positive_count_is_14": int_value(summary.get("primary_p867_motif_positive_count")) == 14,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p872_path = Path(args.p872)
    p976_path = Path(args.p976)
    contract_path = Path(args.contract)
    p872 = load_json(p872_path)
    p976 = load_json(p976_path)
    p872_summary = p872.get("summary") or {}
    selected = [case for case in p872.get("selected_cases") or [] if isinstance(case, dict)]
    union_verified = [case for case in selected if case.get("union_public_key_verified")]
    p867_positive = [case for case in selected if case.get("p867_motif_verified_below_rho")]
    non_union_verified = [case for case in selected if not case.get("union_public_key_verified")]
    non_p867 = [case for case in selected if not case.get("p867_motif_verified_below_rho")]
    selected_tier = tier_summary("all_public_selected", selected)
    union_tier = tier_summary("union_public_key_verified", union_verified)
    p867_tier = tier_summary("p867_motif_positive", p867_positive)
    non_union_tier = tier_summary("non_union_verified_selected", non_union_verified)
    non_p867_tier = tier_summary("non_p867_selected", non_p867)

    p976_controls = p976_control_summary(p976)
    selected_total = selected_tier["sum_direct_ops_over_rho"] or 0.0
    selected_count = selected_tier["count"]
    union_count = len(union_verified)
    p867_count = len(p867_positive)
    p872_controls = {
        "p872_claim_is_two_stage": p872_summary.get("claim_status") == "P872_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_P867_MOTIF_MULTIWINDOW",
        "p872_public_second_stage_count_is_30": int_value(p872_summary.get("second_stage_selected_case_count")) == 30,
        "p872_reconstructed_count_is_30": int_value(p872_summary.get("reconstructed_selected_case_count")) == 30,
        "p872_reconstruction_errors_zero": int_value(p872_summary.get("reconstruction_error_count")) == 0,
        "p872_union_verified_count_is_21": int_value(p872_summary.get("selected_union_public_key_verified_case_count")) == 21,
        "p872_p867_positive_count_is_14": int_value(p872_summary.get("p867_motif_verified_below_rho_case_count")) == 14,
        "p872_selected_cases_len_is_30": selected_count == 30,
    }
    positive_control_pass = all(p872_controls.values()) and all(p976_controls.values())
    selected_all_below_rho = selected_count > 0 and selected_tier["below_rho_count"] == selected_count
    selected_avg_below_rho = (selected_tier["avg_direct_ops_over_rho"] or 10**9) < 1.0
    selected_max_below_rho = (selected_tier["max_direct_ops_over_rho"] or 10**9) < 1.0
    union_amortized = ratio(selected_total, union_count)
    p867_amortized = ratio(selected_total, p867_count)
    union_amortized_below = union_amortized is not None and union_amortized < 1.0
    p867_amortized_below = p867_amortized is not None and p867_amortized < 1.0

    if not positive_control_pass:
        claim = "NEGATIVE_RESULT_P977_CONTROL_FAILURE"
    elif selected_all_below_rho and selected_avg_below_rho and not p867_amortized_below:
        claim = "P977_P231_SELECTED_STREAM_BELOW_RHO_PER_CASE_WITH_USEFUL_AMORTIZATION_GAP"
    elif selected_all_below_rho and selected_avg_below_rho and p867_amortized_below:
        claim = "P977_P231_SELECTED_STREAM_USEFUL_AMORTIZED_BELOW_RHO"
    elif selected_all_below_rho:
        claim = "P977_P231_SELECTED_STREAM_INDIVIDUAL_BELOW_RHO_AVERAGE_GAP"
    else:
        claim = "NEGATIVE_RESULT_P977_SELECTED_STREAM_NOT_BELOW_RHO"

    return {
        "artifacts": {
            "contract": str(contract_path),
            "p872_source": str(p872_path),
            "p976_source": str(p976_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(contract_path),
            "p872_source_sha256": sha256_file(p872_path),
            "p976_source_sha256": sha256_file(p976_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SOURCE-CHARGE-AUDIT: direct ops/rho values are imported from P872 rather than recomputed here.",
            "PUBLIC-SELECTION: the charged portfolio is the full P872 public two-stage selected set.",
            "FALSE-POSITIVES-CHARGED: non-P867 and non-union-verified selected cases remain in the selected total.",
            "USEFUL-AMORTIZATION-GAP: selected per-case direct cost is below rho, but all-selected charge per useful verifier-backed case is above rho.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this does not close a global matrix or individual logarithm descent.",
            "NOT-A-COMPLETE-ECDLP-BREAK: this is an index-calculus source-generation component audit, not an end-to-end faster-than-rho ECDLP algorithm.",
        ],
        "method": "p977_p231_selected_corpus_source_charge",
        "parameters": {
            "baseline": "Pollard-rho direct operation ratios imported from P872",
            "first_stage_rule": p872_summary.get("first_stage_rule"),
            "import_bridge_claim": (p976.get("summary") or {}).get("claim_status"),
            "second_stage_rule": p872_summary.get("second_stage_rule"),
            "target": targets(selected),
        },
        "schema": SCHEMA,
        "source_controls": {
            "p872": p872_controls,
            "p976": p976_controls,
        },
        "summary": {
            "non_p867_selected_count": len(non_p867),
            "non_union_verified_selected_count": len(non_union_verified),
            "p867_positive_count": p867_count,
            "p867_positive_precision": ratio(p867_count, selected_count),
            "p867_useful_amortized_below_rho": bool(p867_amortized_below),
            "p867_useful_amortized_ops_over_rho": p867_amortized,
            "positive_control_pass": bool(positive_control_pass),
            "selected_all_below_rho": bool(selected_all_below_rho),
            "selected_avg_below_rho": bool(selected_avg_below_rho),
            "selected_avg_ops_over_rho": selected_tier["avg_direct_ops_over_rho"],
            "selected_count": selected_count,
            "selected_direct_below_rho_count": selected_tier["below_rho_count"],
            "selected_max_below_rho": bool(selected_max_below_rho),
            "selected_max_ops_over_rho": selected_tier["max_direct_ops_over_rho"],
            "selected_min_ops_over_rho": selected_tier["min_direct_ops_over_rho"],
            "selected_sum_ops_over_rho": selected_tier["sum_direct_ops_over_rho"],
            "union_verified_count": union_count,
            "union_verified_precision": ratio(union_count, selected_count),
            "union_verified_useful_amortized_below_rho": bool(union_amortized_below),
            "union_verified_useful_amortized_ops_over_rho": union_amortized,
        },
        "tiers": [
            selected_tier,
            union_tier,
            p867_tier,
            non_union_tier,
            non_p867_tier,
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P977 contract path")
    parser.add_argument("--p872", default=str(DEFAULT_P872), help="P872 two-stage materialization JSON")
    parser.add_argument("--p976", default=str(DEFAULT_P976), help="P976 import bridge JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} selected={selected} selected_sum={selected_sum} "
        "selected_avg={selected_avg} selected_max={selected_max} "
        "union_verified={union_verified} union_amortized={union_amortized} "
        "p867={p867} p867_amortized={p867_amortized} out={out}".format(
            claim=payload["claim_status"],
            selected=summary["selected_count"],
            selected_sum=summary["selected_sum_ops_over_rho"],
            selected_avg=summary["selected_avg_ops_over_rho"],
            selected_max=summary["selected_max_ops_over_rho"],
            union_verified=summary["union_verified_count"],
            union_amortized=summary["union_verified_useful_amortized_ops_over_rho"],
            p867=summary["p867_positive_count"],
            p867_amortized=summary["p867_useful_amortized_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
