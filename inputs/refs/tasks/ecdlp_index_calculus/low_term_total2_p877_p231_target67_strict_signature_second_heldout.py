#!/usr/bin/env python3
"""P877 strict second-heldout validation for the P876 target67 signature."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_p876_p231_target67_non_p867_motif_selector as p876


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p877_p231_target67_strict_signature_second_heldout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p877_p231_target67_strict_signature_second_heldout_probe.json"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_HELDOUT_WINDOWS = (
    "11400_11407",
    "11408_11415",
    "11416_11423",
    "11424_11431",
    "11432_11439",
    "11440_11447",
    "11448_11455",
)
SCHEMA = "ecdlp.low_term_total2_p877_p231_target67_strict_signature_second_heldout.v1"
STRICT_RULE_NAME = (
    "top_k == 4 AND leaf_selector_family in {mode_hash_leaf,mode_hybrid_support_monic_b} "
    "AND selected_leaf_occurrence_count == 6 AND leaf_gap_tuple == [0,1,2]"
)
STRICT_FAMILIES = {"mode_hash_leaf", "mode_hybrid_support_monic_b"}
STRICT_GAP = (0, 1, 2)


def int_value(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_ratio(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 8)


def strict_signature(features: dict[str, Any]) -> bool:
    return (
        int_value(features.get("top_k")) == 4
        and str(features.get("leaf_selector_family")) in STRICT_FAMILIES
        and int_value(features.get("selected_leaf_occurrence_count")) == 6
        and p876.tuple_value(features.get("leaf_gap_tuple")) == STRICT_GAP
    )


def strict_rule_names(features: dict[str, Any]) -> list[str]:
    return [STRICT_RULE_NAME] if strict_signature(features) else []


def previous_motif_keys() -> tuple[set[str], set[str]]:
    path = STATE_DIR / "low_term_total2_p876_p231_target67_non_p867_motif_selector_probe.json"
    if not path.exists():
        return set(), set()
    payload = p868.load_json(path)
    motif_keys = set()
    exact_keys = set()
    for case in payload.get("heldout_selected_cases") or []:
        ratio = case.get("direct_ops_over_rho")
        if not case.get("union_public_key_verified") or ratio is None or float(ratio) >= 1.0:
            continue
        for derivation in case.get("matched_non_p867_same_tail_derivations") or []:
            motif_keys.add(p868.json_key(derivation.get("motif")))
            exact_keys.add(str(derivation.get("exact_tail_expression_key")))
    return motif_keys, exact_keys


def selected_motif_counts(rows: list[dict[str, Any]]) -> dict[str, Any]:
    motif_counter: Counter[str] = Counter()
    exact_counter: Counter[str] = Counter()
    for row in rows:
        case = row.get("case")
        if not case or not p876.is_non_p867_below_rho(case):
            continue
        for derivation in p876.matched_non_p867_derivations(case):
            motif_counter[p868.json_key(derivation.get("motif"))] += 1
            exact_counter[str(derivation.get("exact_tail_expression_key"))] += 1
    return {
        "exact_clusters": [
            {"count": count, "exact_tail_expression_key": key}
            for key, count in exact_counter.most_common()
        ],
        "motif_clusters": [
            {"count": count, "motif": json.loads(key)}
            for key, count in motif_counter.most_common()
        ],
    }


def recurrence_counts(rows: list[dict[str, Any]], previous_motifs: set[str], previous_exact: set[str]) -> dict[str, int]:
    motif_recurrent_cases = 0
    exact_recurrent_cases = 0
    for row in rows:
        case = row.get("case")
        if not case or not p876.is_non_p867_below_rho(case):
            continue
        derivations = p876.matched_non_p867_derivations(case)
        if any(p868.json_key(item.get("motif")) in previous_motifs for item in derivations):
            motif_recurrent_cases += 1
        if any(str(item.get("exact_tail_expression_key")) in previous_exact for item in derivations):
            exact_recurrent_cases += 1
    return {
        "previous_exact_recurrence_case_count": exact_recurrent_cases,
        "previous_motif_recurrence_case_count": motif_recurrent_cases,
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("below_rho_union_case_count")) > 0 and int_value(
        summary.get("previous_motif_recurrence_case_count")
    ) > 0:
        return "P877_STRICT_TARGET67_SIGNATURE_REPLICATES_SECOND_HELDOUT_MOTIF_BELOW_RHO"
    if int_value(summary.get("below_rho_union_case_count")) > 0:
        return "P877_STRICT_TARGET67_SIGNATURE_SELECTS_SECOND_HELDOUT_BELOW_RHO"
    if int_value(summary.get("public_selected_case_count")) > 0:
        return "NEGATIVE_RESULT_P877_STRICT_SIGNATURE_SELECTS_SECOND_HELDOUT_WITHOUT_BELOW_RHO"
    return "NEGATIVE_RESULT_P877_STRICT_SIGNATURE_SELECTS_ZERO_SECOND_HELDOUT_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = list(args.heldout_windows)
    rows, source_counts, sources = p876.build_rows(
        windows,
        args.target,
        strict_signature,
        reconstruct=True,
        selected_rule_names=strict_rule_names,
    )
    labeled_summary = p876.summarize_labeled(rows, source_counts)
    previous_motifs, previous_exact = previous_motif_keys()
    recurrence = recurrence_counts(rows, previous_motifs, previous_exact)
    summary = {
        **labeled_summary,
        **recurrence,
        "claim_status": None,
        "heldout_windows": windows,
        "selected_precision_below_rho": safe_ratio(
            labeled_summary.get("below_rho_union_case_count", 0),
            labeled_summary.get("public_selected_case_count", 0),
        ),
        "strict_rule": STRICT_RULE_NAME,
        "target": args.target,
    }
    claim = determine_claim(summary)
    summary["claim_status"] = claim

    selected_sorted = sorted(
        rows,
        key=lambda row: (
            not bool(row.get("case") and p876.is_non_p867_below_rho(row["case"])),
            float((row.get("case") or {}).get("direct_ops_over_rho") or 10**18),
            str(row["features"].get("case_id")),
        ),
    )
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
            "source_windows": sources,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P877_") else "NEGATIVE RESULT",
        "created_at": p872.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "TARGET-LOCAL BOUNDARY: P877 validates only 67.a1@9803 inside p231 fixed-row artifacts.",
            "SECOND-HELDOUT BOUNDARY: the selector is frozen from P876 before labels are revealed.",
            "MOTIF BOUNDARY: motif recurrence is diagnostic unless paired with below-rho verifier-backed recovery.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p877_p231_target67_strict_signature_second_heldout",
        "motif_clusters": selected_motif_counts(rows),
        "parameters": {
            "heldout_windows": windows,
            "strict_families": sorted(STRICT_FAMILIES),
            "strict_leaf_gap_tuple": list(STRICT_GAP),
            "strict_rule": STRICT_RULE_NAME,
            "target": args.target,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "The strict public signature was frozen from P876 before P877 labels were revealed.",
                "Only selected second-heldout cases are reconstructed.",
                "Exact and normalized motif recurrence are diagnostic, not a complete target-descent mechanism.",
            ],
            "claim_or_task": "Validate the frozen P876 target67 public signature on second-heldout windows.",
            "evidence_so_far": [
                f"Second-heldout selected cases: {summary.get('public_selected_case_count')}/{summary.get('source_case_count')}.",
                f"Second-heldout below-rho cases: {summary.get('below_rho_union_case_count')}.",
                f"Previous motif recurrence cases: {summary.get('previous_motif_recurrence_case_count')}.",
            ],
            "failure_modes": [
                "The signature may remain target-local to p231 fixed-row artifacts.",
                "No unselected-case recall is measured.",
                "A below-rho selector still needs a reusable algebraic relation-generation mechanism.",
            ],
            "next_concrete_action": (
                "If positive, build P878 to compare the strict signature against a random/top-k-matched public baseline on the same second-heldout windows."
            ),
            "status": "OBSERVATION" if claim.startswith("P877_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "selected_cases": [
            p876.compact_case(row["case"], row["features"], row["matched_rule_names"])
            for row in selected_sorted
            if row.get("case")
        ],
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--target", default=DEFAULT_TARGET)
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
