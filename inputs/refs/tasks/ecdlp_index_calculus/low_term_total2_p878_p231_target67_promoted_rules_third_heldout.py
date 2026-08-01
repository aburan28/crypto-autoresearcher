#!/usr/bin/env python3
"""P878 third-heldout validation for P876 promoted target67 public rules."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_p876_p231_target67_non_p867_motif_selector as p876
import low_term_total2_p877_p231_target67_strict_signature_second_heldout as p877


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p878_p231_target67_promoted_rules_third_heldout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p878_p231_target67_promoted_rules_third_heldout_probe.json"
DEFAULT_RULE_SOURCE = STATE_DIR / "low_term_total2_p876_p231_target67_non_p867_motif_selector_probe.json"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_HELDOUT_WINDOWS = (
    "11456_11463",
    "11464_11471",
    "11472_11479",
    "11480_11487",
    "11488_11495",
    "11496_11503",
)
SCHEMA = "ecdlp.low_term_total2_p878_p231_target67_promoted_rules_third_heldout.v1"


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


def load_promoted_rules(path: Path) -> list[p876.CandidateRule]:
    payload = p868.load_json(path)
    rows = payload.get("promoted_candidate_rules") or []
    return [p876.rule_from_json(row) for row in rows]


def selected_by_rules(rules: list[p876.CandidateRule], features: dict[str, Any]) -> bool:
    return any(rule.matches(features) for rule in rules)


def matching_rule_names(rules: list[p876.CandidateRule], features: dict[str, Any]) -> list[str]:
    return [rule.name for rule in rules if rule.matches(features)]


def rule_summary(rows: list[dict[str, Any]], rules: list[p876.CandidateRule]) -> list[dict[str, Any]]:
    results = []
    for rule in rules:
        selected = [row for row in rows if rule.name in row.get("matched_rule_names", [])]
        cases = [row["case"] for row in selected if row.get("case")]
        union_verified = [case for case in cases if case.get("union_public_key_verified")]
        below = [
            case
            for case in union_verified
            if case.get("direct_ops_over_rho") is not None and float(case["direct_ops_over_rho"]) < 1.0
        ]
        non_p867 = [case for case in below if int_value(case.get("p867_motif_matched_derivation_count")) == 0]
        results.append(
            {
                **rule.to_json(),
                "below_rho_union_case_count": len(below),
                "non_p867_below_rho_case_count": len(non_p867),
                "public_selected_case_count": len(selected),
                "selected_precision_below_rho": safe_ratio(len(below), len(selected)),
                "union_public_key_verified_case_count": len(union_verified),
            }
        )
    return sorted(
        results,
        key=lambda row: (
            -int_value(row.get("below_rho_union_case_count")),
            -int_value(row.get("union_public_key_verified_case_count")),
            int_value(row.get("public_selected_case_count")),
            str(row.get("name")),
        ),
    )


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


def subset_summary(rows: list[dict[str, Any]], predicate: Any) -> dict[str, Any]:
    selected = [row for row in rows if predicate(row)]
    cases = [row["case"] for row in selected if row.get("case")]
    union_verified = [case for case in cases if case.get("union_public_key_verified")]
    below = [
        case
        for case in union_verified
        if case.get("direct_ops_over_rho") is not None and float(case["direct_ops_over_rho"]) < 1.0
    ]
    non_p867 = [case for case in below if int_value(case.get("p867_motif_matched_derivation_count")) == 0]
    return {
        "below_rho_union_case_count": len(below),
        "non_p867_below_rho_case_count": len(non_p867),
        "public_selected_case_count": len(selected),
        "selected_precision_below_rho": safe_ratio(len(below), len(selected)),
        "union_public_key_verified_case_count": len(union_verified),
    }


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("target_local_non_p867_below_rho_case_count")) > 0:
        return "P878_P876_PROMOTED_RULES_SELECT_THIRD_HELDOUT_NON_P867_BELOW_RHO"
    if int_value(summary.get("below_rho_union_case_count")) > 0:
        return "P878_P876_PROMOTED_RULES_SELECT_THIRD_HELDOUT_P867_BELOW_RHO"
    if int_value(summary.get("public_selected_case_count")) > 0:
        return "NEGATIVE_RESULT_P878_PROMOTED_RULES_SELECT_THIRD_HELDOUT_WITHOUT_BELOW_RHO"
    return "NEGATIVE_RESULT_P878_PROMOTED_RULES_SELECT_ZERO_THIRD_HELDOUT_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = list(args.heldout_windows)
    rules = load_promoted_rules(args.rule_source)

    rows, source_counts, sources = p876.build_rows(
        windows,
        args.target,
        lambda features: selected_by_rules(rules, features),
        reconstruct=True,
        selected_rule_names=lambda features: matching_rule_names(rules, features),
    )
    labeled_summary = p876.summarize_labeled(rows, source_counts)
    strict_subset = subset_summary(rows, lambda row: p877.strict_signature(row["features"]))
    broad_extra = subset_summary(rows, lambda row: not p877.strict_signature(row["features"]))
    summary = {
        **labeled_summary,
        "broad_extra_below_rho_union_case_count": broad_extra["below_rho_union_case_count"],
        "broad_extra_public_selected_case_count": broad_extra["public_selected_case_count"],
        "broad_extra_selected_precision_below_rho": broad_extra["selected_precision_below_rho"],
        "claim_status": None,
        "heldout_windows": windows,
        "promoted_rule_count": len(rules),
        "selected_precision_below_rho": safe_ratio(
            labeled_summary.get("below_rho_union_case_count", 0),
            labeled_summary.get("public_selected_case_count", 0),
        ),
        "strict_subset_below_rho_union_case_count": strict_subset["below_rho_union_case_count"],
        "strict_subset_public_selected_case_count": strict_subset["public_selected_case_count"],
        "strict_subset_selected_precision_below_rho": strict_subset["selected_precision_below_rho"],
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
            "rule_source": str(args.rule_source),
            "script": str(Path(__file__)),
            "source_windows": sources,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P878_") else "NEGATIVE RESULT",
        "created_at": p872.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "TARGET-LOCAL BOUNDARY: P878 validates only 67.a1@9803 inside p231 fixed-row artifacts.",
            "THIRD-HELDOUT BOUNDARY: selection uses P876 promoted public rules before labels are revealed.",
            "CALIBRATION BOUNDARY: P877 is a negative calibration result, not a proof against broader public selectors.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p878_p231_target67_promoted_rules_third_heldout",
        "motif_clusters": selected_motif_counts(rows),
        "parameters": {
            "heldout_windows": windows,
            "promoted_rules": [rule.to_json() for rule in rules],
            "rule_source": str(args.rule_source),
            "target": args.target,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "The rule set is loaded from P876 and is not changed after P878 labels are revealed.",
                "Only selected third-heldout cases are reconstructed.",
                "Below-rho promotion requires union public-key verification.",
            ],
            "claim_or_task": "Validate P876 promoted public-rule union on fresh third-heldout target67 windows.",
            "evidence_so_far": [
                f"Third-heldout selected cases: {summary.get('public_selected_case_count')}/{summary.get('source_case_count')}.",
                f"Third-heldout below-rho union cases: {summary.get('below_rho_union_case_count')}.",
                f"Broad-extra selected cases: {summary.get('broad_extra_public_selected_case_count')}.",
            ],
            "failure_modes": [
                "The P876 public rules may be target-local or window-local.",
                "The broad rule union may recover verifier-backed secrets but remain above rho.",
                "A below-rho relation selector still needs target descent and a reusable algebraic explanation.",
            ],
            "next_concrete_action": (
                "If positive, freeze the winning public rule subset and run a fourth heldout; if negative, switch to scoring relation-rank margin instead of exact public signatures."
            ),
            "status": "OBSERVATION" if claim.startswith("P878_") else "NEGATIVE RESULT",
        },
        "rule_summary": rule_summary(rows, rules),
        "schema": SCHEMA,
        "selected_cases": [
            p876.compact_case(row["case"], row["features"], row["matched_rule_names"])
            for row in selected_sorted
            if row.get("case")
        ],
        "strict_subset_summary": strict_subset,
        "broad_extra_summary": broad_extra,
        "summary": summary,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--rule-source", type=Path, default=DEFAULT_RULE_SOURCE)
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
