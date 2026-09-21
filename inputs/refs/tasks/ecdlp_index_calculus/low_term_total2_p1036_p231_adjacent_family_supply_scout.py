#!/usr/bin/env python3
"""P1036 adjacent repeated two-tail family supply scout."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1025_p231_consistency_filtered_quotient_scheduler as p1025
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1036_p231_adjacent_family_supply_scout.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1036_p231_adjacent_family_supply_scout_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1036_p231_adjacent_family_supply_scout.v1"
ORDER = p1033.ORDER
SIGNAL_WINDOW = p1035.SIGNAL_WINDOW

ObjectKeyFn = Callable[[dict[str, Any]], Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def form_window(form: dict[str, Any]) -> str:
    return str(form.get("window") or "")


def form_split(form: dict[str, Any]) -> str:
    return str(form.get("split") or "")


def public_key(form: dict[str, Any]) -> str:
    return p1033.public_key(form)


def q_coeff(form: dict[str, Any]) -> int:
    coeffs = form.get("coeffs") or []
    return int_value(coeffs[0]) % ORDER if coeffs else 0


def terms_tuple(form: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in form.get("terms") or [])


def tail_support_tuple(form: dict[str, Any]) -> tuple[int, ...]:
    return tuple(int_value(value) for value in form.get("tail_support") or [])


def factor_count(forms: list[dict[str, Any]]) -> int:
    return max([max(0, len(form.get("coeffs") or []) - 1) for form in forms] or [0])


def is_repeated_two_tail(form: dict[str, Any]) -> bool:
    terms = terms_tuple(form)
    tail = tail_support_tuple(form)
    return (
        form_split(form) == "fresh_validation"
        and len(terms) == 4
        and len(tail) == 2
        and terms[0] == terms[1]
        and terms[2] == terms[3]
        and terms[0] != terms[2]
    )


def gap_tail_shape(form: dict[str, Any]) -> tuple[Any, ...]:
    terms = terms_tuple(form)
    tail = tail_support_tuple(form)
    if not terms:
        return ("missing",)
    base = terms[0]
    term_gap = terms[2] - terms[0] if len(terms) >= 3 else None
    tail_gaps = tuple(value - base for value in tail)
    tail_width = tail[-1] - tail[0] if len(tail) == 2 else None
    return ("gap_tail_shape", term_gap, tail_gaps, tail_width)


def family_descriptor(form: dict[str, Any]) -> dict[str, Any]:
    return {
        "exact_tail_expression_key": str(form.get("exact_tail_expression_key") or ""),
        "gap_tail_shape": list(gap_tail_shape(form)),
        "motif_key": str(form.get("motif_key") or ""),
        "tail_support": list(tail_support_tuple(form)),
        "terms": list(terms_tuple(form)),
    }


def compact_form(index: int, form: dict[str, Any], factors: int) -> dict[str, Any]:
    compact = p1033.compact_form(index, form, factors)
    compact["exact_tail_expression_key"] = str(form.get("exact_tail_expression_key") or "")
    compact["motif_key"] = str(form.get("motif_key") or "")
    return compact


def exact_tail_key(form: dict[str, Any]) -> Any:
    return ("exact_tail", str(form.get("exact_tail_expression_key") or ""))


def motif_key(form: dict[str, Any]) -> Any:
    return ("motif", str(form.get("motif_key") or ""))


def terms_tail_key(form: dict[str, Any]) -> Any:
    return ("terms_tail", terms_tuple(form), tail_support_tuple(form))


def shifted_gap_tail_key(form: dict[str, Any]) -> Any:
    return gap_tail_shape(form)


def object_specs() -> list[dict[str, Any]]:
    return [
        {"description": "Exact tail expression object.", "key_fn": exact_tail_key, "name": "exact_tail"},
        {"description": "Normalized motif object.", "key_fn": motif_key, "name": "motif"},
        {"description": "Exact repeated terms and tail support.", "key_fn": terms_tail_key, "name": "terms_tail"},
        {"description": "Shift-normalized repeated-term gap plus tail gaps.", "key_fn": shifted_gap_tail_key, "name": "gap_tail_shape"},
    ]


def later_windows() -> list[str]:
    return [window for window in p1025.FRESH_WINDOWS if window > SIGNAL_WINDOW]


def reconstruct_pool(rows: list[dict[str, Any]], compressed: bool) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    forms, meta = p1035.reconstruct_pool(rows, compressed)
    meta = dict(meta)
    meta["factor_count"] = factor_count(forms)
    return forms, meta


def evaluate_object(
    forms: list[dict[str, Any]],
    factors: int,
    windows: list[str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, form in enumerate(forms):
        if form_window(form) not in windows or not is_repeated_two_tail(form):
            continue
        key = (public_key(form), form_window(form), json_key(spec["key_fn"](form)))
        groups[key].append((index, form))

    evaluated_groups = []
    prediction_count = 0
    true_count = 0
    false_count = 0
    q_diverse_group_count = 0
    factor_matchless_q_diverse_group_count = 0
    no_q_diversity_group_count = 0
    single_form_group_count = 0
    eligible_form_count = sum(len(group) for group in groups.values())

    for (public, window, object_key), group in sorted(groups.items()):
        q_values = sorted({q_coeff(form) for _index, form in group})
        if len(group) < 2:
            single_form_group_count += 1
            continue
        if len(q_values) < 2:
            no_q_diversity_group_count += 1
            continue
        q_diverse_group_count += 1

        predictions = []
        for left_offset, (left_index, left) in enumerate(group):
            for right_index, right in group[left_offset + 1 :]:
                predicted = p1033.derive_target_from_pair(left, right, factors)
                if predicted is None:
                    continue
                source_secrets = sorted(
                    {
                        int_value(value) % ORDER
                        for value in [left.get("source_secret"), right.get("source_secret")]
                        if value is not None
                    }
                )
                verified = bool(source_secrets and all(predicted == secret for secret in source_secrets))
                prediction_count += 1
                if verified:
                    true_count += 1
                else:
                    false_count += 1
                predictions.append(
                    {
                        "left": compact_form(left_index, left, factors),
                        "predicted_target": predicted,
                        "right": compact_form(right_index, right, factors),
                        "source_secrets": source_secrets,
                        "toy_secret_verified": verified,
                    }
                )
        if not predictions:
            factor_matchless_q_diverse_group_count += 1
        if predictions or len(evaluated_groups) < 16:
            representative = group[0][1]
            evaluated_groups.append(
                {
                    "eligible_form_count": len(group),
                    "family": family_descriptor(representative),
                    "object_key": object_key,
                    "predictions": predictions[:12],
                    "prediction_count": len(predictions),
                    "public_fingerprint": public,
                    "q_values": q_values,
                    "window": window,
                }
            )

    return {
        "eligible_form_count": eligible_form_count,
        "false_count": false_count,
        "factor_matchless_q_diverse_group_count": factor_matchless_q_diverse_group_count,
        "group_count": len(groups),
        "groups": evaluated_groups[:24],
        "model": spec["name"],
        "no_q_diversity_group_count": no_q_diversity_group_count,
        "prediction_count": prediction_count,
        "q_diverse_group_count": q_diverse_group_count,
        "single_form_group_count": single_form_group_count,
        "true_count": true_count,
        "validation_success": bool(prediction_count > 0 and false_count == 0),
    }


def aggregate_object_results(object_results: list[dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "eligible_form_count",
        "false_count",
        "factor_matchless_q_diverse_group_count",
        "group_count",
        "no_q_diversity_group_count",
        "prediction_count",
        "q_diverse_group_count",
        "single_form_group_count",
        "true_count",
    ]
    summary = {field: sum(int_value(result.get(field)) for result in object_results) for field in fields}
    summary["validation_success"] = any(bool(result.get("validation_success")) for result in object_results)
    return summary


def evaluate_rows(rows: list[dict[str, Any]], windows: list[str], label: str, compressed: bool) -> dict[str, Any]:
    forms, meta = reconstruct_pool(rows, compressed)
    factors = int_value(meta.get("factor_count"))
    object_results = [evaluate_object(forms, factors, windows, spec) for spec in object_specs()]
    summary = aggregate_object_results(object_results)
    summary["windows"] = windows
    return {
        "label": label,
        "meta": meta,
        "object_results": object_results,
        "summary": summary,
    }


def aggregate_summaries(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    fields = [
        "eligible_form_count",
        "false_count",
        "factor_matchless_q_diverse_group_count",
        "group_count",
        "no_q_diversity_group_count",
        "prediction_count",
        "q_diverse_group_count",
        "single_form_group_count",
        "true_count",
    ]
    summary = {field: sum(int_value(item["summary"].get(field)) for item in evaluations) for field in fields}
    summary["validation_success"] = any(bool(item["summary"].get("validation_success")) for item in evaluations)
    return summary


def evaluate_pool(
    pool: dict[str, Any],
    scout_by_window: dict[str, list[dict[str, Any]]],
    later_by_window: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    predicate = pool["predicate"]
    scout_rows = p1035.selected_rows_for_pool(scout_by_window, [SIGNAL_WINDOW], predicate, "fresh_validation")
    later_rows = p1035.selected_rows_for_pool(later_by_window, later_windows(), predicate, "fresh_validation")
    evaluations = []
    for compressed in (False, True):
        suffix = "compressed" if compressed else "raw"
        evaluations.append(evaluate_rows(scout_rows, [SIGNAL_WINDOW], f"{pool['name']}_scout_{suffix}", compressed))
        evaluations.append(evaluate_rows(later_rows, later_windows(), f"{pool['name']}_later_{suffix}", compressed))
    scout_evals = [item for item in evaluations if "_scout_" in item["label"]]
    later_evals = [item for item in evaluations if "_later_" in item["label"]]
    return {
        "description": pool["description"],
        "evaluations": evaluations,
        "later_summary": aggregate_summaries(later_evals),
        "name": pool["name"],
        "row_counts": {
            "later_rows": len(later_rows),
            "scout_rows": len(scout_rows),
        },
        "scout_summary": aggregate_summaries(scout_evals),
    }


def determine_claim(pool_results: list[dict[str, Any]]) -> str:
    later_false = sum(int_value(result["later_summary"].get("false_count")) for result in pool_results)
    later_predictions = sum(int_value(result["later_summary"].get("prediction_count")) for result in pool_results)
    later_q_diverse = sum(int_value(result["later_summary"].get("q_diverse_group_count")) for result in pool_results)
    later_eligible = sum(int_value(result["later_summary"].get("eligible_form_count")) for result in pool_results)
    if later_false:
        return "NEGATIVE_RESULT_P1036_ADJACENT_FAMILY_FALSE_PREDICTION"
    if later_predictions:
        return "P1036_ADJACENT_FAMILY_TARGET_PREDICTION_SIGNAL"
    if later_q_diverse:
        return "NEGATIVE_RESULT_P1036_Q_DIVERSE_GROUPS_NO_FACTOR_MATCH"
    if later_eligible:
        return "NEGATIVE_RESULT_P1036_NO_Q_DIVERSE_ADJACENT_GROUPS"
    return "NEGATIVE_RESULT_P1036_NO_REPEATED_TWO_TAIL_FORMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    scout_by_window, scout_exists = p1035.load_rows([SIGNAL_WINDOW], args.targets, args.min_source_rank)
    later_by_window, later_exists = p1035.load_rows(later_windows(), args.targets, args.min_source_rank)
    pool_results = [evaluate_pool(pool, scout_by_window, later_by_window) for pool in p1035.pool_specs()]
    claim = determine_claim(pool_results)
    all_windows = [SIGNAL_WINDOW, *later_windows()]
    source_hashes = {
        window: p1005.sha256_file(p1007.expanded_source_path(window))
        for window in all_windows
        if p1007.expanded_source_path(window).exists()
    }
    return {
        "artifacts": {
            "contract": str(args.contract),
            "script": str(Path(__file__)),
        },
        "artifact_hashes": {
            "contract_sha256": p1005.sha256_file(Path(args.contract)),
            "p1035_dependency_sha256": p1005.sha256_file(Path(p1035.__file__)),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1036_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "SCOUT: adjacent families are searched after P1035 and are not frozen validation.",
            "STRICT-ELIMINATION: target predictions require exact local factor-vector equality.",
            "INDEX-CALCULUS PRECURSOR: this is relation-generation evidence, not sparse linear algebra or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "later_windows": later_windows(),
            "min_source_rank": args.min_source_rank,
            "object_models": [spec["name"] for spec in object_specs()],
            "pool_names": [pool["name"] for pool in p1035.pool_specs()],
            "signal_window": SIGNAL_WINDOW,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "pool_results": pool_results,
        "schema": SCHEMA,
        "source": {
            "later_exists": later_exists,
            "scout_exists": scout_exists,
        },
        "summary": {
            "claim_status": claim,
            "later_by_pool": [
                {
                    "eligible_form_count": result["later_summary"]["eligible_form_count"],
                    "false_count": result["later_summary"]["false_count"],
                    "factor_matchless_q_diverse_group_count": result["later_summary"][
                        "factor_matchless_q_diverse_group_count"
                    ],
                    "name": result["name"],
                    "prediction_count": result["later_summary"]["prediction_count"],
                    "q_diverse_group_count": result["later_summary"]["q_diverse_group_count"],
                    "row_count": result["row_counts"]["later_rows"],
                    "true_count": result["later_summary"]["true_count"],
                }
                for result in pool_results
            ],
            "scout_by_pool": [
                {
                    "false_count": result["scout_summary"]["false_count"],
                    "name": result["name"],
                    "prediction_count": result["scout_summary"]["prediction_count"],
                    "q_diverse_group_count": result["scout_summary"]["q_diverse_group_count"],
                    "row_count": result["row_counts"]["scout_rows"],
                    "true_count": result["scout_summary"]["true_count"],
                }
                for result in pool_results
            ],
        },
        "timestamp": now_iso(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", default=str(DEFAULT_CONTRACT), help="Experiment contract path")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    bits = []
    for item in payload["summary"]["later_by_pool"]:
        bits.append(
            "{name}:rows={rows} eligible={eligible} qdiv={qdiv} pred={pred} false={false}".format(
                name=item["name"],
                rows=item["row_count"],
                eligible=item["eligible_form_count"],
                qdiv=item["q_diverse_group_count"],
                pred=item["prediction_count"],
                false=item["false_count"],
            )
        )
    print(
        "claim={claim} out={out} {bits}".format(
            claim=payload["claim_status"],
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
