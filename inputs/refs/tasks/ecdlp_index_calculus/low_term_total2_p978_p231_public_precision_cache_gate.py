#!/usr/bin/env python3
"""P978 public precision/cache gate audit over the P872 p231 selected corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p978_p231_public_precision_cache_gate.md"
DEFAULT_P872 = STATE_DIR / "low_term_total2_p872_p231_two_stage_materialization_probe.json"
DEFAULT_P977 = STATE_DIR / "low_term_total2_p977_p231_selected_corpus_source_charge_probe.json"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p978_p231_public_precision_cache_gate_probe.json"
SCHEMA = "ecdlp.low_term_total2_p978_p231_public_precision_cache_gate.v1"


Rule = tuple[str, str, Callable[[dict[str, Any]], bool]]


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


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


def case_ops(case: dict[str, Any]) -> float:
    return float_value(case.get("direct_ops_over_rho"))


def is_p867(case: dict[str, Any]) -> bool:
    return bool(case.get("p867_motif_verified_below_rho"))


def is_union_verified(case: dict[str, Any]) -> bool:
    return bool(case.get("union_public_key_verified"))


def features(case: dict[str, Any]) -> dict[str, Any]:
    return case.get("public_features") or {}


def top_k(case: dict[str, Any]) -> int:
    return int_value(features(case).get("top_k"))


def salt_gap(case: dict[str, Any]) -> int:
    return int_value(features(case).get("salt_gap"), -1)


def transfer_index(case: dict[str, Any]) -> int:
    return int_value(features(case).get("transfer_index"), int_value(case.get("transfer_index")))


def row_salts(case: dict[str, Any]) -> tuple[int, ...]:
    salts: list[int] = []
    for row_leaf in case.get("row_leaf_keys") or []:
        salt = salt_number(str(row_leaf.get("row_key")))
        if salt is not None:
            salts.append(salt)
    return tuple(sorted(salts))


def source_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    public = features(case)
    return (
        public.get("window") or case.get("window"),
        transfer_index(case),
        case.get("target"),
        public.get("leaf_selector") or case.get("leaf_selector"),
        row_salts(case),
    )


def relation_group_key(case: dict[str, Any]) -> tuple[Any, ...]:
    return (
        case.get("target"),
        transfer_index(case),
        case.get("union_derived_secret"),
        json.dumps(case.get("row_leaf_keys") or [], sort_keys=True),
    )


def rank_histogram(cases: list[dict[str, Any]]) -> dict[str, int]:
    hist: dict[str, int] = {}
    for case in cases:
        key = str(case.get("union_rank"))
        hist[key] = hist.get(key, 0) + 1
    return dict(sorted(hist.items()))


def compact_case(case: dict[str, Any]) -> dict[str, Any]:
    public = features(case)
    return {
        "case_id": case.get("case_id"),
        "direct_ops_over_rho": case.get("direct_ops_over_rho"),
        "p867_motif_verified_below_rho": is_p867(case),
        "row_salts": list(row_salts(case)),
        "salt_gap": public.get("salt_gap"),
        "source_group_key": json.dumps(source_group_key(case), sort_keys=True),
        "top_k": public.get("top_k"),
        "transfer_index": transfer_index(case),
        "union_public_key_verified": is_union_verified(case),
        "union_rank": case.get("union_rank"),
        "window": public.get("window") or case.get("window"),
    }


def group_cases(cases: list[dict[str, Any]]) -> dict[tuple[Any, ...], list[dict[str, Any]]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for case in cases:
        grouped.setdefault(source_group_key(case), []).append(case)
    return grouped


def summarize_rule(name: str, expression: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    selected = sorted(
        cases,
        key=lambda case: (
            str(features(case).get("window") or case.get("window")),
            transfer_index(case),
            top_k(case),
            json.dumps(row_salts(case)),
        ),
    )
    direct_sum = sum(case_ops(case) for case in selected)
    p867_count = sum(1 for case in selected if is_p867(case))
    union_count = sum(1 for case in selected if is_union_verified(case))
    groups = group_cases(selected)
    cached_sum = sum(max(case_ops(case) for case in group) for group in groups.values())
    p867_source_groups = sum(1 for group in groups.values() if any(is_p867(case) for case in group))
    union_source_groups = sum(1 for group in groups.values() if any(is_union_verified(case) for case in group))
    p867_relation_groups = {
        relation_group_key(case)
        for case in selected
        if is_p867(case)
    }
    union_relation_groups = {
        relation_group_key(case)
        for case in selected
        if is_union_verified(case)
    }
    duplicate_groups = {
        json.dumps(key, sort_keys=True): [compact_case(case) for case in group]
        for key, group in sorted(groups.items(), key=lambda item: json.dumps(item[0], sort_keys=True))
        if len(group) > 1
    }
    return {
        "cached_case_p867_amortized_ops_over_rho": ratio(cached_sum, p867_count),
        "cached_group_p867_amortized_ops_over_rho": ratio(cached_sum, p867_source_groups),
        "cached_group_union_amortized_ops_over_rho": ratio(cached_sum, union_source_groups),
        "cached_relation_p867_amortized_ops_over_rho": ratio(cached_sum, len(p867_relation_groups)),
        "cached_relation_union_amortized_ops_over_rho": ratio(cached_sum, len(union_relation_groups)),
        "cached_source_group_count": len(groups),
        "cached_sum_ops_over_rho": round8(cached_sum),
        "direct_case_p867_amortized_below_rho": bool(p867_count and direct_sum / p867_count < 1.0),
        "direct_case_p867_amortized_ops_over_rho": ratio(direct_sum, p867_count),
        "direct_case_union_amortized_ops_over_rho": ratio(direct_sum, union_count),
        "direct_relation_p867_amortized_ops_over_rho": ratio(direct_sum, len(p867_relation_groups)),
        "direct_relation_union_amortized_ops_over_rho": ratio(direct_sum, len(union_relation_groups)),
        "direct_sum_ops_over_rho": round8(direct_sum),
        "duplicate_source_groups": duplicate_groups,
        "duplicate_source_group_count": len(duplicate_groups),
        "expression": expression,
        "max_direct_ops_over_rho": round8(max([case_ops(case) for case in selected], default=0.0)),
        "min_direct_ops_over_rho": round8(min([case_ops(case) for case in selected], default=0.0)),
        "name": name,
        "p867_false_positive_count": len(selected) - p867_count,
        "p867_positive_count": p867_count,
        "p867_precision": ratio(p867_count, len(selected)),
        "p867_relation_group_count": len(p867_relation_groups),
        "p867_source_group_count": p867_source_groups,
        "rank_histogram": rank_histogram(selected),
        "sample_cases": [compact_case(case) for case in selected[:8]],
        "selected_all_direct_below_rho": bool(selected and all(case_ops(case) < 1.0 for case in selected)),
        "selected_count": len(selected),
        "source_group_cache_saved_ops_over_rho": round8(direct_sum - cached_sum),
        "union_false_positive_count": len(selected) - union_count,
        "union_precision": ratio(union_count, len(selected)),
        "union_relation_group_count": len(union_relation_groups),
        "union_source_group_count": union_source_groups,
        "union_verified_count": union_count,
    }


def candidate_rules() -> list[Rule]:
    return [
        ("all_public_selected", "true", lambda case: True),
        ("top_k_eq_4", "top_k == 4", lambda case: top_k(case) == 4),
        ("salt_gap_eq_1", "salt_gap == 1", lambda case: salt_gap(case) == 1),
        ("salt_gap_in_1_7_8", "salt_gap in {1,7,8}", lambda case: salt_gap(case) in {1, 7, 8}),
        (
            "top_k_eq_4_and_salt_gap_ne_3",
            "top_k == 4 AND salt_gap != 3",
            lambda case: top_k(case) == 4 and salt_gap(case) != 3,
        ),
        (
            "top_k_eq_4_and_salt_gap_le_2",
            "top_k == 4 AND salt_gap <= 2",
            lambda case: top_k(case) == 4 and salt_gap(case) <= 2,
        ),
        (
            "top_k_le_7_and_salt_gap_eq_1",
            "top_k <= 7 AND salt_gap == 1",
            lambda case: top_k(case) <= 7 and salt_gap(case) == 1,
        ),
        ("transfer_mod_3_eq_1", "transfer_index % 3 == 1", lambda case: transfer_index(case) % 3 == 1),
        ("transfer_mod_4_eq_3", "transfer_index % 4 == 3", lambda case: transfer_index(case) % 4 == 3),
    ]


def p977_controls(p977: dict[str, Any]) -> dict[str, Any]:
    summary = p977.get("summary") or {}
    return {
        "p977_claim_is_expected": p977.get("claim_status")
        == "P977_P231_SELECTED_STREAM_BELOW_RHO_PER_CASE_WITH_USEFUL_AMORTIZATION_GAP",
        "p977_p867_count_is_14": int_value(summary.get("p867_positive_count")) == 14,
        "p977_p867_useful_amortized_is_expected": summary.get("p867_useful_amortized_ops_over_rho")
        == 1.76016684,
        "p977_positive_control_pass": bool(summary.get("positive_control_pass")),
        "p977_selected_count_is_30": int_value(summary.get("selected_count")) == 30,
        "p977_selected_sum_is_expected": summary.get("selected_sum_ops_over_rho") == 24.64233582,
        "p977_union_count_is_21": int_value(summary.get("union_verified_count")) == 21,
    }


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    contract_path = Path(args.contract)
    p872_path = Path(args.p872)
    p977_path = Path(args.p977)
    p872 = load_json(p872_path)
    p977 = load_json(p977_path)
    selected = [case for case in p872.get("selected_cases") or [] if isinstance(case, dict)]
    controls = p977_controls(p977)
    controls["p872_selected_cases_len_is_30"] = len(selected) == 30
    rule_rows = [
        summarize_rule(name, expression, [case for case in selected if predicate(case)])
        for name, expression, predicate in candidate_rules()
    ]
    primary = next(row for row in rule_rows if row["name"] == "top_k_eq_4_and_salt_gap_ne_3")
    secondary_cache = next(row for row in rule_rows if row["name"] == "salt_gap_in_1_7_8")
    same_corpus_case_success = bool(
        all(controls.values())
        and primary["selected_count"] >= 6
        and primary["p867_positive_count"] >= 6
        and (primary["p867_precision"] or 0.0) >= 0.8
        and (primary["direct_case_p867_amortized_ops_over_rho"] or 10**9) < 1.0
        and primary["selected_all_direct_below_rho"]
    )
    cache_group_success = bool(
        all(controls.values())
        and secondary_cache["p867_source_group_count"] >= 4
        and (secondary_cache["cached_group_p867_amortized_ops_over_rho"] or 10**9) < 1.0
        and secondary_cache["selected_all_direct_below_rho"]
    )
    if same_corpus_case_success and cache_group_success:
        claim = "P978_P231_PUBLIC_GATE_AND_CACHE_DROP_USEFUL_AMORTIZED_BELOW_RHO_SAME_CORPUS"
    elif same_corpus_case_success:
        claim = "P978_P231_PUBLIC_GATE_DROPS_CASE_USEFUL_AMORTIZED_BELOW_RHO_SAME_CORPUS"
    elif cache_group_success:
        claim = "P978_P231_PUBLIC_CACHE_DROPS_GROUP_USEFUL_AMORTIZED_BELOW_RHO_SAME_CORPUS"
    elif all(controls.values()):
        claim = "NEGATIVE_RESULT_P978_NO_PUBLIC_GATE_OR_CACHE_BELOW_RHO_IN_P872"
    else:
        claim = "NEGATIVE_RESULT_P978_CONTROL_FAILURE"

    return {
        "artifacts": {
            "contract": str(contract_path),
            "p872_source": str(p872_path),
            "p977_source": str(p977_path),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": sha256_file(contract_path),
            "p872_source_sha256": sha256_file(p872_path),
            "p977_source_sha256": sha256_file(p977_path),
            "script_sha256": sha256_file(Path(__file__)),
        },
        "claim_status": claim,
        "claim_taxonomy": "HYPOTHESIS" if claim.startswith("P978_") else "NEGATIVE RESULT",
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime ECDLP harness only.",
            "SAME-CORPUS-DISCOVERY: P978 scores public rules on the same P872 selected corpus; it is not fresh validation.",
            "PUBLIC-RULE-BODY: promoted rules use only P872 public_features, but rule choice was made after inspecting labels.",
            "CACHE-DIAGNOSTIC: duplicate source-group caching is an accounting model, not an implemented p231 source cache.",
            "DENOMINATOR-SEPARATION: case-level and source-group useful denominators are reported separately to avoid duplicate useful-count inflation.",
            "NO-SPARSE-LINALG-OR-TARGET-DESCENT: this does not close a global matrix or individual logarithm descent.",
            "NOT-A-COMPLETE-ECDLP-BREAK: this is a relation-source component improvement hypothesis, not an end-to-end faster-than-rho algorithm.",
        ],
        "method": "p978_p231_public_precision_cache_gate",
        "parameters": {
            "candidate_rule_count": len(rule_rows),
            "duplicate_source_group_charge": "max direct_ops_over_rho once per source group",
            "duplicate_source_group_key": "(window, transfer_index, target, leaf_selector, row salts)",
            "minimum_p867_precision": 0.8,
            "minimum_selected_cases": 6,
            "minimum_useful_p867_cases": 6,
            "primary_rule": primary["expression"],
            "secondary_cache_rule": secondary_cache["expression"],
        },
        "red_team_handoff": {
            "artifact_paths": [str(args.out), str(contract_path), str(Path(__file__))],
            "assumptions": [
                "P872 public_features are available before reconstruction.",
                "Case-level P867 positives are useful as relation-source events unless duplicate grouping collapses them.",
                "The promoted rule can be evaluated on fresh/disjoint p231 windows without using labels.",
            ],
            "claim_or_task": "Public P872 feature gates can reduce useful-amortized source charge below rho on the p231 selected stream.",
            "evidence_so_far": [
                "Primary same-corpus gate selects 9 cases, all P867-positive, direct amortized ops/rho 0.82562855.",
                "Secondary cache diagnostic over salt_gap in {1,7,8} has cached source-group P867 amortized ops/rho 0.98053528.",
            ],
            "failure_modes": [
                "Rule was selected after looking at P872 labels, so same-corpus overfit is the main risk.",
                "Nested top-k duplicates may not produce independent useful relations.",
                "A fresh-window target may have different salt-gap behavior.",
                "Sparse linear algebra and target descent are not tested.",
            ],
            "next_concrete_action": "Run P979 on later/disjoint p231 windows with the frozen rule `top_k == 4 AND salt_gap != 3` before reconstruction.",
            "status": "HYPOTHESIS",
        },
        "rule_summaries": rule_rows,
        "schema": SCHEMA,
        "source_controls": controls,
        "summary": {
            "cache_group_success_same_corpus": cache_group_success,
            "control_pass": all(controls.values()),
            "primary_direct_case_p867_amortized_ops_over_rho": primary[
                "direct_case_p867_amortized_ops_over_rho"
            ],
            "primary_p867_positive_count": primary["p867_positive_count"],
            "primary_p867_precision": primary["p867_precision"],
            "primary_p867_relation_group_count": primary["p867_relation_group_count"],
            "primary_rule": primary["expression"],
            "primary_selected_count": primary["selected_count"],
            "primary_selected_sum_ops_over_rho": primary["direct_sum_ops_over_rho"],
            "same_corpus_case_success": same_corpus_case_success,
            "secondary_cache_cached_group_p867_amortized_ops_over_rho": secondary_cache[
                "cached_group_p867_amortized_ops_over_rho"
            ],
            "secondary_cache_cached_sum_ops_over_rho": secondary_cache["cached_sum_ops_over_rho"],
            "secondary_cache_p867_relation_group_count": secondary_cache["p867_relation_group_count"],
            "secondary_cache_p867_source_group_count": secondary_cache["p867_source_group_count"],
            "secondary_cache_rule": secondary_cache["expression"],
            "secondary_cache_selected_count": secondary_cache["selected_count"],
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="P978 contract path")
    parser.add_argument("--p872", default=str(DEFAULT_P872), help="P872 two-stage materialization JSON")
    parser.add_argument("--p977", default=str(DEFAULT_P977), help="P977 source-charge JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    summary = payload["summary"]
    print(
        "claim={claim} primary_rule={primary_rule!r} selected={selected} p867={p867} "
        "precision={precision} direct_p867_amortized={direct_amortized} "
        "secondary_cache_rule={cache_rule!r} cache_group_amortized={cache_amortized} out={out}".format(
            claim=payload["claim_status"],
            primary_rule=summary["primary_rule"],
            selected=summary["primary_selected_count"],
            p867=summary["primary_p867_positive_count"],
            precision=summary["primary_p867_precision"],
            direct_amortized=summary["primary_direct_case_p867_amortized_ops_over_rho"],
            cache_rule=summary["secondary_cache_rule"],
            cache_amortized=summary["secondary_cache_cached_group_p867_amortized_ops_over_rho"],
            out=args.out,
        )
    )


if __name__ == "__main__":
    main()
