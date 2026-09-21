#!/usr/bin/env python3
"""P879 fourth-heldout validation for a public rank-margin token scorer."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import low_term_total2_p868_p231_fresh_skeleton_generator_audit as p868
import low_term_total2_p872_p231_two_stage_materialization as p872
import low_term_total2_p876_p231_target67_non_p867_motif_selector as p876


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p879_p231_target67_public_rank_margin_scorer.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p879_p231_target67_public_rank_margin_scorer_probe.json"
DEFAULT_RULE_SOURCE = STATE_DIR / "low_term_total2_p876_p231_target67_non_p867_motif_selector_probe.json"
DEFAULT_TARGET = "67.a1@9803"
DEFAULT_HELDOUT_WINDOWS = (
    "11504_11511",
    "11512_11519",
    "11520_11527",
    "11528_11535",
    "11536_11543",
    "11544_11551",
)
PRIOR_CASE_SOURCES = (
    (STATE_DIR / "low_term_total2_p876_p231_target67_non_p867_motif_selector_probe.json", "heldout_selected_cases"),
    (STATE_DIR / "low_term_total2_p877_p231_target67_strict_signature_second_heldout_probe.json", "selected_cases"),
    (STATE_DIR / "low_term_total2_p878_p231_target67_promoted_rules_third_heldout_probe.json", "selected_cases"),
)
SCHEMA = "ecdlp.low_term_total2_p879_p231_target67_public_rank_margin_scorer.v1"
SALT_RE = re.compile(r"salt(\d+)")


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


def tuple_value(value: Any) -> tuple[Any, ...]:
    return p876.tuple_value(value)


def extract_salts(features: dict[str, Any], row_leaf_keys: list[dict[str, Any]] | None = None) -> tuple[int, ...]:
    salts: list[int] = []
    for item in row_leaf_keys or []:
        match = SALT_RE.search(str(item.get("row_key")))
        if match:
            salts.append(int(match.group(1)))
    if not salts:
        for match in SALT_RE.finditer(str(features.get("case_id"))):
            salts.append(int(match.group(1)))
    return tuple(sorted(salts))


def token_set(features: dict[str, Any], row_leaf_keys: list[dict[str, Any]] | None = None) -> set[str]:
    tokens = {
        f"family={features.get('leaf_selector_family')}",
        f"selector={features.get('leaf_selector')}",
        f"top_k={int_value(features.get('top_k'))}",
        f"occurrence={int_value(features.get('selected_leaf_occurrence_count'))}",
        f"unique={int_value(features.get('unique_leaf_count'))}",
        f"leaf_gap={p868.json_key(tuple_value(features.get('leaf_gap_tuple')))}",
        f"unique_leaf_indices={p868.json_key(tuple_value(features.get('unique_leaf_indices')))}",
    }
    salt_gap = features.get("salt_gap")
    if salt_gap is not None:
        tokens.add(f"salt_gap={int_value(salt_gap)}")
    salts = extract_salts(features, row_leaf_keys)
    if salts:
        tokens.add(f"salt_pair={p868.json_key(salts)}")
        tokens.add(f"salt_min_mod4={min(salts) % 4}")
        tokens.add(f"salt_max_mod4={max(salts) % 4}")
        tokens.add(f"salt_sum_mod8={sum(salts) % 8}")
        tokens.add(f"family_salt_pair={features.get('leaf_selector_family')}:{p868.json_key(salts)}")
        tokens.add(f"selector_salt_pair={features.get('leaf_selector')}:{p868.json_key(salts)}")
    transfer_index = features.get("transfer_index")
    if transfer_index is not None:
        transfer = int_value(transfer_index)
        for modulus in (2, 4, 8, 16):
            tokens.add(f"transfer_mod{modulus}={transfer % modulus}")
    return tokens


def case_public_features(case: dict[str, Any]) -> dict[str, Any]:
    return dict(case.get("public_features") or {})


def is_success_case(case: dict[str, Any]) -> bool:
    ratio = case.get("direct_ops_over_rho")
    return bool(
        case.get("union_public_key_verified")
        and ratio is not None
        and float(ratio) < 1.0
        and int_value(case.get("p867_motif_matched_derivation_count")) == 0
    )


def load_prior_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for path, key in PRIOR_CASE_SOURCES:
        payload = p868.load_json(path)
        for case in payload.get(key) or []:
            case = dict(case)
            case["prior_source"] = path.name
            cases.append(case)
    return cases


def build_token_model(prior_cases: list[dict[str, Any]]) -> dict[str, Any]:
    token_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    positive_count = 0
    negative_count = 0
    for case in prior_cases:
        success = is_success_case(case)
        positive_count += int(success)
        negative_count += int(not success)
        features = case_public_features(case)
        for token in token_set(features, case.get("row_leaf_keys") or []):
            bucket = token_counts[token]
            if success:
                bucket[0] += 1
            else:
                bucket[1] += 1

    token_weights = {
        token: math.log((counts[0] + 1.0) / (counts[1] + 1.0))
        for token, counts in token_counts.items()
    }
    return {
        "negative_count": negative_count,
        "positive_count": positive_count,
        "token_counts": {token: {"negative": counts[1], "positive": counts[0]} for token, counts in token_counts.items()},
        "token_weights": token_weights,
    }


def score_features(model: dict[str, Any], features: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    weights = model["token_weights"]
    counts = model["token_counts"]
    contributions = []
    score = 0.0
    for token in sorted(token_set(features)):
        weight = float(weights.get(token, 0.0))
        if weight == 0.0:
            continue
        score += weight
        contributions.append(
            {
                "negative": counts[token]["negative"],
                "positive": counts[token]["positive"],
                "token": token,
                "weight": round(weight, 8),
            }
        )
    contributions.sort(key=lambda row: (-abs(float(row["weight"])), str(row["token"])))
    return round(score, 8), contributions[:12]


def load_promoted_rules(path: Path) -> list[p876.CandidateRule]:
    payload = p868.load_json(path)
    return [p876.rule_from_json(row) for row in payload.get("promoted_candidate_rules") or []]


def matching_rule_names(rules: list[p876.CandidateRule], features: dict[str, Any]) -> list[str]:
    return [rule.name for rule in rules if rule.matches(features)]


def selected_summary(rows: list[dict[str, Any]], source_counts: dict[str, int]) -> dict[str, Any]:
    summary = p876.summarize_labeled(rows, source_counts)
    summary["selected_precision_below_rho"] = safe_ratio(
        summary.get("below_rho_union_case_count", 0),
        summary.get("public_selected_case_count", 0),
    )
    return summary


def determine_claim(summary: dict[str, Any]) -> str:
    if int_value(summary.get("target_local_non_p867_below_rho_case_count")) > 0:
        return "P879_PUBLIC_RANK_MARGIN_SCORER_SELECTS_FOURTH_HELDOUT_NON_P867_BELOW_RHO"
    if int_value(summary.get("below_rho_union_case_count")) > 0:
        return "P879_PUBLIC_RANK_MARGIN_SCORER_SELECTS_FOURTH_HELDOUT_P867_BELOW_RHO"
    if int_value(summary.get("public_selected_case_count")) > 0:
        return "NEGATIVE_RESULT_P879_PUBLIC_SCORER_SELECTS_FOURTH_HELDOUT_WITHOUT_BELOW_RHO"
    return "NEGATIVE_RESULT_P879_PUBLIC_SCORER_SELECTS_ZERO_FOURTH_HELDOUT_CASES"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    windows = list(args.heldout_windows)
    prior_cases = load_prior_cases()
    model = build_token_model(prior_cases)
    rules = load_promoted_rules(args.rule_source)

    broad_rows, broad_source_counts, sources = p876.build_rows(
        windows,
        args.target,
        lambda features: bool(matching_rule_names(rules, features)),
        reconstruct=False,
        selected_rule_names=lambda features: matching_rule_names(rules, features),
    )
    scored_candidates = []
    for row in broad_rows:
        score, contributions = score_features(model, row["features"])
        scored_candidates.append(
            {
                "case_id": row["features"].get("case_id"),
                "features": row["features"],
                "matched_rule_names": row.get("matched_rule_names", []),
                "score": score,
                "score_token_contributions": contributions,
                "window": row.get("window"),
            }
        )
    scored_candidates.sort(
        key=lambda row: (
            -float(row["score"]),
            str(row["features"].get("window")),
            int_value(row["features"].get("transfer_index")),
            str(row["features"].get("leaf_selector")),
            str(row["case_id"]),
        )
    )
    selected_candidates = scored_candidates[: max(0, int(args.selection_budget))]
    selected_ids = {str(row["case_id"]) for row in selected_candidates}
    score_by_id = {str(row["case_id"]): row for row in selected_candidates}

    selected_rows, selected_source_counts, _ = p876.build_rows(
        windows,
        args.target,
        lambda features: str(features.get("case_id")) in selected_ids,
        reconstruct=True,
        selected_rule_names=lambda features: matching_rule_names(rules, features),
    )
    summary = selected_summary(selected_rows, selected_source_counts)
    summary.update(
        {
            "broad_candidate_count": len(broad_rows),
            "claim_status": None,
            "heldout_windows": windows,
            "prior_negative_count": model["negative_count"],
            "prior_positive_count": model["positive_count"],
            "prior_training_case_count": len(prior_cases),
            "promoted_rule_count": len(rules),
            "selection_budget": int(args.selection_budget),
            "target": args.target,
        }
    )
    claim = determine_claim(summary)
    summary["claim_status"] = claim

    selected_cases = []
    for row in selected_rows:
        case = row.get("case")
        if not case:
            continue
        case_id = str(row["features"].get("case_id"))
        score_row = score_by_id.get(case_id, {})
        compact = p876.compact_case(case, row["features"], row.get("matched_rule_names", []))
        compact["public_score"] = score_row.get("score")
        compact["score_rank"] = 1 + next(
            (index for index, candidate in enumerate(selected_candidates) if str(candidate["case_id"]) == case_id),
            10**9,
        )
        compact["score_token_contributions"] = score_row.get("score_token_contributions", [])
        selected_cases.append(compact)
    selected_cases.sort(
        key=lambda case: (
            not is_success_case(case),
            float(case.get("direct_ops_over_rho") or 10**18),
            int_value(case.get("score_rank"), 10**9),
        )
    )

    top_tokens = [
        {
            **model["token_counts"][token],
            "token": token,
            "weight": round(weight, 8),
        }
        for token, weight in sorted(
            model["token_weights"].items(),
            key=lambda item: (-abs(float(item[1])), str(item[0])),
        )[:24]
    ]
    return {
        "artifacts": {
            "contract": str(args.contract),
            "prior_case_sources": [{"path": str(path), "key": key} for path, key in PRIOR_CASE_SOURCES],
            "rule_source": str(args.rule_source),
            "script": str(Path(__file__)),
            "source_windows": sources,
        },
        "broad_candidates": [
            {
                "case_id": row["case_id"],
                "matched_rule_names": row["matched_rule_names"],
                "public_features": p876.compact_feature_row(row["features"]),
                "score": row["score"],
                "score_token_contributions": row["score_token_contributions"],
            }
            for row in scored_candidates[:64]
        ],
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P879_") else "NEGATIVE RESULT",
        "created_at": p872.now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP verifier harness.",
            "TARGET-LOCAL BOUNDARY: P879 validates only 67.a1@9803 inside p231 fixed-row artifacts.",
            "FOURTH-HELDOUT BOUNDARY: the public scorer is fit from P876-P878 before fourth-heldout labels are revealed.",
            "SCORE BOUNDARY: this is a public candidate-ranking test, not a complete target-descent method.",
            "POLLARD-RHO BOUNDARY: this is relation-lane selector evidence, not a complete faster-than-rho ECDLP algorithm.",
        ],
        "method": "p879_p231_target67_public_rank_margin_scorer",
        "parameters": {
            "heldout_windows": windows,
            "promoted_rules": [rule.to_json() for rule in rules],
            "score_model": "Laplace-smoothed signed public-token log-odds",
            "selection_budget": int(args.selection_budget),
            "target": args.target,
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(args.contract), str(Path(__file__))],
            "assumptions": [
                "Training labels are restricted to P876-P878 selected cases.",
                "Fourth-heldout candidate scoring uses only public features and row schedule tokens.",
                "Only top-scored fourth-heldout cases are reconstructed.",
            ],
            "claim_or_task": "Validate a public rank-margin token scorer on fresh fourth-heldout target67 windows.",
            "evidence_so_far": [
                f"Prior positive/negative cases: {model['positive_count']}/{model['negative_count']}.",
                f"Broad fourth-heldout candidates: {len(broad_rows)}.",
                f"Selected fourth-heldout cases: {summary.get('public_selected_case_count')}.",
                f"Below-rho selected cases: {summary.get('below_rho_union_case_count')}.",
            ],
            "failure_modes": [
                "The scorer may learn row-schedule phase artifacts rather than an algebraic relation mechanism.",
                "The broad candidate family may still be too narrow because it inherits the P876 promoted rule collapse.",
                "A below-rho selector still needs target descent and cross-target validation.",
            ],
            "next_concrete_action": (
                "If positive, freeze the winning public tokens and run a fifth heldout; if negative, switch from target67 exact signatures to quotient/slice predictor work from the guarded-family work order."
            ),
            "status": "OBSERVATION" if claim.startswith("P879_") else "NEGATIVE RESULT",
        },
        "schema": SCHEMA,
        "selected_cases": selected_cases,
        "summary": summary,
        "top_token_weights": top_tokens,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT)
    parser.add_argument("--heldout-windows", nargs="+", default=list(DEFAULT_HELDOUT_WINDOWS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--rule-source", type=Path, default=DEFAULT_RULE_SOURCE)
    parser.add_argument("--selection-budget", type=int, default=16)
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
