#!/usr/bin/env python3
"""P976 fresh/disjoint p231 corpus import bridge for post-P975 cache stress."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p976_fresh_disjoint_corpus_import.md"
DEFAULT_P975 = STATE_DIR / "low_term_total2_p975_public_event_cache_stress_probe.json"
DEFAULT_P870 = STATE_DIR / "low_term_total2_p870_p231_public_rule_materialization_probe.json"
DEFAULT_P872 = STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json"
DEFAULT_P875 = STATE_DIR / "low_term_total2_p875_p231_disjoint_target_topk_materialization_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p976_fresh_disjoint_corpus_import_probe.json"
SCHEMA = "ecdlp.low_term_total2_p976_fresh_disjoint_corpus_import.v1"


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


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


def float_value(value: Any, default: float | None = None) -> float | None:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


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


def targets(cases: list[dict[str, Any]]) -> list[str]:
    return sorted({str(case.get("target")) for case in cases if case.get("target")})


def windows(cases: list[dict[str, Any]]) -> list[str]:
    return sorted({str(case.get("window")) for case in cases if case.get("window")})


def direct_ratios(cases: list[dict[str, Any]]) -> list[float]:
    return [
        float(value)
        for case in cases
        for value in [case.get("direct_ops_over_rho")]
        if value is not None
    ]


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    return {
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "leaf_selector": case.get("leaf_selector"),
        "p867_motif_verified_below_rho": bool(case.get("p867_motif_verified_below_rho")),
        "row_leaf_keys": case.get("row_leaf_keys"),
        "same_tail_matched_derivation_count": case.get("same_tail_matched_derivation_count"),
        "target": case.get("target"),
        "top_k": case.get("top_k"),
        "transfer_index": case.get("transfer_index"),
        "union_derived_secret": case.get("union_derived_secret"),
        "union_public_key_verified": bool(case.get("union_public_key_verified")),
        "union_rank": case.get("union_rank"),
        "union_relation_count": case.get("union_relation_count"),
        "window": case.get("window"),
    }


def summarize_materialization(
    name: str,
    payload: dict[str, Any],
    p975_targets: set[str],
    p975_salts: set[int],
) -> dict[str, Any]:
    summary = payload.get("summary") or {}
    selected = [case for case in payload.get("selected_cases") or [] if isinstance(case, dict)]
    selected_targets = set(targets(selected))
    selected_salts = set(row_salts(selected))
    p867_positive = [case for case in selected if case.get("p867_motif_verified_below_rho")]
    union_verified = [case for case in selected if case.get("union_public_key_verified")]
    union_below = [
        case
        for case in union_verified
        if case.get("direct_ops_over_rho") is not None and float(case["direct_ops_over_rho"]) < 1.0
    ]
    p867_ratios = direct_ratios(p867_positive)
    union_below_ratios = direct_ratios(union_below)
    disjoint_target = bool(selected_targets and selected_targets.isdisjoint(p975_targets))
    outside_salt_scope = bool(selected_salts and selected_salts.isdisjoint(p975_salts))
    public_selection = bool(
        "rule" in json.dumps(summary).lower()
        or "selected_case_count" in summary
        or "second_stage_selected_case_count" in summary
    )
    selected_count = len(selected)
    p867_count = len(p867_positive)
    reconstruction_errors = int_value(summary.get("reconstruction_error_count"))
    return {
        "below_rho_union_count": len(union_below),
        "claim_status": payload.get("claim_status"),
        "disjoint_target_from_p975": disjoint_target,
        "import_ready": bool(
            (disjoint_target or outside_salt_scope)
            and public_selection
            and reconstruction_errors == 0
            and p867_count >= 10
            and (ratio(p867_count, selected_count) or 0) >= 0.4
        ),
        "max_p867_ops_over_rho": max(p867_ratios) if p867_ratios else None,
        "max_union_below_ops_over_rho": max(union_below_ratios) if union_below_ratios else None,
        "method": payload.get("method"),
        "min_p867_ops_over_rho": min(p867_ratios) if p867_ratios else None,
        "name": name,
        "outside_p975_salt_scope": outside_salt_scope,
        "p867_false_positive_count": selected_count - p867_count,
        "p867_motif_positive_count": p867_count,
        "p867_precision": ratio(p867_count, selected_count),
        "public_pre_reconstruction_selection": public_selection,
        "reconstruction_error_count": reconstruction_errors,
        "sample_p867_positive_cases": [compact_case(case) for case in p867_positive[:5]],
        "selected_count": selected_count,
        "selected_salts": sorted(selected_salts),
        "selected_targets": sorted(selected_targets),
        "selected_windows": windows(selected),
        "source_case_count": summary.get("source_case_count"),
        "summary": summary,
        "union_verified_count": len(union_verified),
    }


def p975_controls(p975: dict[str, Any]) -> dict[str, Any]:
    summary = p975.get("summary") or {}
    return {
        "p975_cached_ops_is_90": int_value(summary.get("cached_total_ops")) == 90,
        "p975_rank4_selected_is_3": int_value(summary.get("rank4_selected_count")) == 3,
        "p975_scope_limited": bool(summary.get("scope_limited_no_wider_or_disjoint_source")),
        "p975_selected_is_3": int_value(summary.get("selected_count")) == 3,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    p975 = load_json(Path(args.p975))
    p870 = load_json(Path(args.p870))
    p872 = load_json(Path(args.p872))
    p875 = load_json(Path(args.p875))
    controls = p975_controls(p975)
    source_scope = p975.get("source_scope") or {}
    p975_targets = set(source_scope.get("available_targets") or [])
    p975_salts = {int_value(value) for value in source_scope.get("p959_target_salts") or []}
    candidates = [
        summarize_materialization("p870_first_stage_22050", p870, p975_targets, p975_salts),
        summarize_materialization("p872_two_stage_22050", p872, p975_targets, p975_salts),
        summarize_materialization("p875_topk_target67_diagnostic", p875, p975_targets, p975_salts),
    ]
    candidates.sort(
        key=lambda row: (
            not bool(row.get("import_ready")),
            -int_value(row.get("p867_motif_positive_count")),
            float_value(row.get("max_p867_ops_over_rho"), 10**9) or 10**9,
            row.get("name") or "",
        )
    )
    primary = candidates[0]
    controls_pass = all(bool(value) for value in controls.values())
    if controls_pass and primary.get("import_ready"):
        claim = "P976_FRESH_DISJOINT_P231_CORPUS_IMPORTED_FOR_NEXT_CACHE_STRESS"
    elif controls_pass and (primary.get("disjoint_target_from_p975") or primary.get("outside_p975_salt_scope")):
        claim = "P976_FRESH_DISJOINT_CORPUS_FOUND_BUT_NOT_IMPORT_READY"
    elif not controls_pass:
        claim = "NEGATIVE_RESULT_P976_P975_CONTROL_FAILURE"
    else:
        claim = "NEGATIVE_RESULT_P976_NO_FRESH_DISJOINT_CORPUS_IMPORT"
    return {
        "artifacts": {
            "contract": str(args.contract),
            "p870_source": str(args.p870),
            "p872_source": str(args.p872),
            "p875_source": str(args.p875),
            "p975_source": str(args.p975),
            "script": str(Path(__file__)),
        },
        "candidate_corpora": candidates,
        "claim_status": claim,
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "BRIDGE-AUDIT: this imports a fresh/disjoint source corpus for the next experiment; it does not port P974 cache accounting by itself.",
            "PUBLIC-SELECTION: imported p231 cases were selected by public rules before reconstruction in their source artifacts.",
            "FALSE-POSITIVE-CHARGING-OPEN: the next cache/source-charge stress must charge all selected p231 cases, including non-P867 motif selections.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this does not close a global matrix or individual logarithm descent.",
        ],
        "method": "p976_fresh_disjoint_corpus_import",
        "parameters": {
            "min_import_p867_positive_count": 10,
            "min_import_p867_precision": 0.4,
            "p975_scope_targets": sorted(p975_targets),
            "p975_scope_salts": sorted(p975_salts),
        },
        "p975_controls": controls,
        "primary_import": primary,
        "schema": SCHEMA,
        "summary": {
            "claim_status": claim,
            "candidate_corpus_count": len(candidates),
            "controls_pass": controls_pass,
            "primary_disjoint_target_from_p975": primary.get("disjoint_target_from_p975"),
            "primary_import_ready": primary.get("import_ready"),
            "primary_name": primary.get("name"),
            "primary_outside_p975_salt_scope": primary.get("outside_p975_salt_scope"),
            "primary_p867_motif_positive_count": primary.get("p867_motif_positive_count"),
            "primary_p867_precision": primary.get("p867_precision"),
            "primary_reconstruction_error_count": primary.get("reconstruction_error_count"),
            "primary_selected_count": primary.get("selected_count"),
            "primary_target": primary.get("selected_targets"),
            "primary_windows": primary.get("selected_windows"),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--p975", type=Path, default=DEFAULT_P975)
    parser.add_argument("--p870", type=Path, default=DEFAULT_P870)
    parser.add_argument("--p872", type=Path, default=DEFAULT_P872)
    parser.add_argument("--p875", type=Path, default=DEFAULT_P875)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    summary = payload["summary"]
    print(
        f"claim={payload['claim_status']} "
        f"primary={summary['primary_name']} "
        f"selected={summary['primary_selected_count']} "
        f"p867_positive={summary['primary_p867_motif_positive_count']} "
        f"precision={summary['primary_p867_precision']} "
        f"disjoint_target={summary['primary_disjoint_target_from_p975']} "
        f"outside_salts={summary['primary_outside_p975_salt_scope']} "
        f"import_ready={summary['primary_import_ready']} "
        f"out={args.out}"
    )


if __name__ == "__main__":
    main()
