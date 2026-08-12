#!/usr/bin/env python3
"""P894 no-label frozen selector validation for full-factor union dedup."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p893_raw_selector_repair_full_factor_dedup as p893


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p894_no_label_selector_freeze_full_factor_dedup.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p894_no_label_selector_freeze_full_factor_dedup_probe.json"
DEFAULT_VALIDATION_SOURCES = [
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_792_799_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_800_807_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_808_815_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_816_823_summary.json",
    STATE_DIR / "low_term_total2_expanded_leaf_rescue_824_831_summary.json",
]
SCHEMA = "ecdlp.low_term_total2_p894_no_label_selector_freeze_full_factor_dedup.v1"
TARGET = "22050.cf1@11731"
FROZEN_POLICIES = {"balanced", "recall_first"}
FROZEN_SELECTORS = {"mode_cost_low_term_support_total2", "mode_low_term_support_total2"}
FROZEN_ROW_SELECTOR = "target_cap3_ow3_hw3_lw0_sw0_cw0_aw1"
FROZEN_TOP_K = 4
FROZEN_LEAF_SET = [90]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p893.int_value(value, default)


def row_leaf_is_frozen(row_leaf: dict[str, Any]) -> bool:
    return [int_value(item) for item in row_leaf.get("leaf_indices") or []] == FROZEN_LEAF_SET


def frozen_selector_matches(case: dict[str, Any]) -> bool:
    row_leaf_keys = case.get("row_leaf_keys") or []
    return (
        case.get("target") == TARGET
        and case.get("policy") in FROZEN_POLICIES
        and case.get("selector") in FROZEN_SELECTORS
        and case.get("row_selector") == FROZEN_ROW_SELECTOR
        and int_value(case.get("top_k")) == FROZEN_TOP_K
        and int_value(case.get("selected_row_count")) == 2
        and int_value(case.get("selected_leaf_count")) == 2
        and len(row_leaf_keys) == 2
        and all(row_leaf_is_frozen(row_leaf) for row_leaf in row_leaf_keys)
    )


def cases_for_source(source: Path) -> list[dict[str, Any]]:
    payload = load_json(source)
    out = []
    for case in payload.get("positive_cases") or []:
        if frozen_selector_matches(case):
            out.append({**case, "summary_path": str(source)})
    return out


def distinct_row_set(item: dict[str, Any]) -> tuple[Any, ...]:
    case = item.get("case") or {}
    return tuple(
        (str(row_leaf.get("row_key")), tuple(int_value(index) for index in row_leaf.get("leaf_indices") or []))
        for row_leaf in case.get("row_leaf_keys") or []
    )


def determine_claim(evaluated: list[dict[str, Any]]) -> str:
    if any(item.get("strict_below_rho") for item in evaluated):
        return "P894_NO_LABEL_SELECTOR_FREEZE_TRANSFERS_FULL_FACTOR_DEDUP_BELOW_RHO"
    if any((item.get("case") or {}).get("public_key_verified") for item in evaluated):
        return "NEGATIVE_RESULT_P894_SELECTOR_VERIFIES_BUT_FACTOR_DEDUP_NOT_BELOW_RHO"
    if evaluated:
        return "NEGATIVE_RESULT_P894_SELECTOR_SELECTS_NO_VERIFIER_CLOSURE"
    return "NEGATIVE_RESULT_P894_SELECTOR_SELECTS_NO_VALIDATION_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    sources = [Path(path) for path in (args.source or DEFAULT_VALIDATION_SOURCES)]
    cases = [case for source in sources for case in cases_for_source(source)]
    ps = p893.p842.load_module("ecdlp_public_slice_for_p894", p893.p842.PUBLIC_SLICE_SCRIPT)
    records_by_key = p893.load_records_for_sources(ps, sources, int(args.max_cases_per_source), int(args.max_factor_degree))
    evaluated = [p893.evaluate_case(ps, records_by_key, case) for case in cases]
    strict = [item for item in evaluated if item.get("strict_below_rho")]
    reconstructed = [item for item in evaluated if item.get("reconstructed")]
    verifier_positive = [item for item in evaluated if (item.get("case") or {}).get("public_key_verified")]
    distinct_selected = {distinct_row_set(item) for item in evaluated}
    distinct_strict = {distinct_row_set(item) for item in strict}
    return {
        "artifacts": {
            "contract": str(DEFAULT_CONTRACT),
            "script": str(Path(__file__)),
        },
        "claim_status": determine_claim(evaluated),
        "created_at": now_iso(),
        "evaluated_cases": evaluated,
        "frozen_selector": {
            "forbidden_selection_inputs": [
                "source_verified",
                "public_key_verified",
                "below_rho",
                "ops_over_rho",
                "rank",
                "relation_count",
                "derived_secret",
            ],
            "leaf_indices": FROZEN_LEAF_SET,
            "policies": sorted(FROZEN_POLICIES),
            "row_selector": FROZEN_ROW_SELECTOR,
            "selected_leaf_count": 2,
            "selected_row_count": 2,
            "selectors": sorted(FROZEN_SELECTORS),
            "target": TARGET,
            "top_k": FROZEN_TOP_K,
        },
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "NO-LABEL SELECTOR FREEZE: verifier labels are excluded from selection, but the tuple is calibrated from one prior positive row set.",
            "POLLARD-RHO BOUNDARY: this is not a complete general faster-than-rho ECDLP algorithm.",
        ],
        "method": "p894_no_label_selector_freeze_full_factor_dedup",
        "parameters": {
            "fixed_value": p893.FIXED_VALUE,
            "max_cases_per_source": int(args.max_cases_per_source),
            "max_factor_degree": int(args.max_factor_degree),
            "source_count": len(sources),
            "target": TARGET,
        },
        "schema": SCHEMA,
        "source_paths": [str(source) for source in sources],
        "summary": {
            "distinct_selected_row_set_count": len(distinct_selected),
            "distinct_strict_row_set_count": len(distinct_strict),
            "failed_reconstruction_count": len([item for item in evaluated if item.get("errors")]),
            "min_reconstructed_union_dedup_ops_over_rho": (
                min(float(item["concrete_union_dedup_ops_over_rho"]) for item in reconstructed if item.get("concrete_union_dedup_ops_over_rho") is not None)
                if reconstructed
                else None
            ),
            "reconstructed_count": len(reconstructed),
            "selected_case_count": len(evaluated),
            "strict_below_rho_count": len(strict),
            "transfers_with_strict_below_rho": sorted({(item.get("case") or {}).get("transfer_index") for item in strict}),
            "verifier_positive_selected_count": len(verifier_positive),
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, action="append")
    parser.add_argument("--max-cases-per-source", type=int, default=0)
    parser.add_argument("--max-factor-degree", type=int, default=1)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    write_json(args.out, payload)
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "frozen_selector": payload["frozen_selector"],
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
