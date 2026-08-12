#!/usr/bin/env python3
"""P873 disjoint-target materialization of the frozen P870+P871 p231 rule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import low_term_total2_p872_p231_two_stage_materialization as p872


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p873_p231_disjoint_target_two_stage_materialization.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p873_p231_disjoint_target_two_stage_materialization_probe.json"
DEFAULT_TARGET = "67.a1@9803"
SCHEMA = "ecdlp.low_term_total2_p873_p231_disjoint_target_two_stage_materialization.v1"


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def determine_p873_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("reconstruction_error_count")) and not int_value(
        summary.get("p867_motif_verified_below_rho_case_count")
    ):
        return "NEGATIVE_RESULT_P873_RECONSTRUCTION_ERRORS_BLOCK_DISJOINT_TARGET_MATERIALIZATION"
    if int_value(summary.get("p867_motif_verified_below_rho_case_count")) > 0 and int_value(
        summary.get("p867_motif_verified_window_count")
    ) >= 2:
        return "P873_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_P867_MOTIF_ON_DISJOINT_TARGET_MULTIWINDOW"
    if int_value(summary.get("p867_motif_verified_below_rho_case_count")) > 0:
        return "P873_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_P867_MOTIF_ON_DISJOINT_TARGET"
    if int_value(summary.get("p867_motif_verified_derivation_case_count")) > 0:
        return "P873_TWO_STAGE_PUBLIC_RULE_MATERIALIZES_DISJOINT_TARGET_MOTIF_ABOVE_RHO_ONLY"
    return "NEGATIVE_RESULT_P873_TWO_STAGE_PUBLIC_RULE_MISSES_DISJOINT_TARGET_P867_MOTIF"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    payload = p872.analyze(args)
    claim = determine_p873_claim(payload["summary"])
    payload["schema"] = SCHEMA
    payload["method"] = "p873_p231_disjoint_target_two_stage_materialization"
    payload["claim_status"] = claim
    payload["claim_taxonomy"] = "OBSERVATION" if claim.startswith("P873_") else "NEGATIVE RESULT"
    payload["summary"]["claim_status"] = claim
    payload["artifacts"]["contract"] = str(args.contract)
    payload["artifacts"]["script"] = str(Path(__file__))
    payload["honesty_boundary"] = [
        "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
        "CROSS-TARGET BOUNDARY: P873 tests one disjoint target within the same p231 fixed-row artifact family.",
        "FROZEN-RULE BOUNDARY: P873 applies P870/P871 rules without retraining on the disjoint target.",
        "MATERIALIZATION BOUNDARY: unselected cases are not reconstructed, so recall and all-case prevalence remain unknown.",
        "TARGET-DESCENT BOUNDARY: selected local derivations do not solve cross-public-key target descent.",
        "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
    ]
    payload["red_team_handoff"] = {
        "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
        "assumptions": [
            "The P870/P871 rules were fixed on 22050.cf1@11731 before this disjoint target was evaluated.",
            "Public feature rows are available before relation-event reconstruction.",
            "Unselected 67.a1@9803 cases are deliberately not labeled in this materialization run.",
        ],
        "claim_or_task": "Materialize the frozen two-stage public selector on disjoint target 67.a1@9803.",
        "evidence_so_far": [
            f"Second-stage selected cases: {payload['summary'].get('second_stage_selected_case_count')}/{payload['summary'].get('source_case_count')}.",
            f"Selected P867 below-rho cases: {payload['summary'].get('p867_motif_verified_below_rho_case_count')}.",
            f"Selected precision: {payload['summary'].get('p867_motif_verified_below_rho_precision')}.",
        ],
        "failure_modes": [
            "A positive still may be p231 fixed-row-family specific rather than general ECDLP structure.",
            "Selected-only evaluation cannot prove recall over unselected cases.",
            "Same-context motif derivations still leave target descent open.",
        ],
        "next_concrete_action": (
            "Build P874 to compare motif-positive groups across targets for target-descent utility, or run another disjoint-target stress."
        ),
        "status": "OBSERVATION" if claim.startswith("P873_") else "NEGATIVE RESULT",
    }
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--windows", nargs="+", default=list(p872.DEFAULT_WINDOWS))
    parser.add_argument("--targets", default=DEFAULT_TARGET)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = analyze(args)
    p872.write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
