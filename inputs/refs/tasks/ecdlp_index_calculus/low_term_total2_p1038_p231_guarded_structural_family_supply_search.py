#!/usr/bin/env python3
"""P1038 guarded repeated two-tail structural-family supply search."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import low_term_total2_p1005_p231_context_safe_early_stop_order as p1005
import low_term_total2_p1007_p231_expanded_source_policy_compatibility as p1007
import low_term_total2_p1022_p231_leaf19_rank_guard_12376 as p1022
import low_term_total2_p1023_p231_leaf19_relation_bank_audit as p1023
import low_term_total2_p1033_p231_leaf8_factor_label_extraction_scout as p1033
import low_term_total2_p1035_p231_leaf8_exact_tail_supply_expansion as p1035
import low_term_total2_p1036_p231_adjacent_family_supply_scout as p1036


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_CONTRACT = STATE_DIR / "experiment_contract_p1038_p231_guarded_structural_family_supply_search.md"
DEFAULT_OUT = STATE_DIR / "low_term_total2_p1038_p231_guarded_structural_family_supply_search_probe.json"
SCHEMA = "ecdlp.low_term_total2_p1038_p231_guarded_structural_family_supply_search.v1"
ORDER = p1033.ORDER
SIGNAL_WINDOW = p1036.SIGNAL_WINDOW
DEFAULT_START = "12504_12511"
DEFAULT_MAX_WINDOWS = 16
WINDOW_RE = re.compile(r"fixed_row_(\d+)_(\d+)_col15_selector_expanded_probe\.json$")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def int_value(value: Any, default: int = 0) -> int:
    return p1023.int_value(value, default)


def json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def parse_window(window: str) -> tuple[int, int]:
    left, right = window.split("_", 1)
    return int(left), int(right)


def discover_forward_windows(start_window: str, max_windows: int) -> list[str]:
    start, _end = parse_window(start_window)
    windows = []
    for path in STATE_DIR.glob("frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"):
        match = WINDOW_RE.search(path.name)
        if not match:
            continue
        left = int(match.group(1))
        right = int(match.group(2))
        if left >= start:
            windows.append((left, right, f"{left}_{right}"))
    windows.sort()
    return [window for _left, _right, window in windows[:max_windows]]


def term_gap(form: dict[str, Any]) -> int | None:
    terms = p1036.terms_tuple(form)
    if len(terms) < 3:
        return None
    return terms[2] - terms[0]


def tail_width(form: dict[str, Any]) -> int | None:
    tail = p1036.tail_support_tuple(form)
    if len(tail) != 2:
        return None
    return tail[-1] - tail[0]


def passes_guard(form: dict[str, Any]) -> bool:
    gap = term_gap(form)
    width = tail_width(form)
    return (gap is not None and gap >= 3) or (width is not None and width >= 3)


def family_descriptor(form: dict[str, Any]) -> dict[str, Any]:
    desc = p1036.family_descriptor(form)
    desc["term_gap"] = term_gap(form)
    desc["tail_width"] = tail_width(form)
    return desc


def compact_prediction(
    left_index: int,
    left: dict[str, Any],
    right_index: int,
    right: dict[str, Any],
    factors: int,
    predicted: int,
    verified: bool,
    source_secrets: list[int],
) -> dict[str, Any]:
    return {
        "left": p1036.compact_form(left_index, left, factors),
        "predicted_target": predicted,
        "right": p1036.compact_form(right_index, right, factors),
        "source_secrets": source_secrets,
        "toy_secret_verified": verified,
    }


def evaluate_object(
    forms: list[dict[str, Any]],
    factors: int,
    windows: list[str],
    spec: dict[str, Any],
) -> dict[str, Any]:
    groups: dict[tuple[str, str, str], list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, form in enumerate(forms):
        if p1036.form_window(form) not in windows:
            continue
        if not p1036.is_repeated_two_tail(form) or not passes_guard(form):
            continue
        key = (p1036.public_key(form), p1036.form_window(form), json_key(spec["key_fn"](form)))
        groups[key].append((index, form))

    evaluated_groups = []
    eligible_form_count = sum(len(group) for group in groups.values())
    q_diverse_group_count = 0
    factor_matchless_q_diverse_group_count = 0
    no_q_diversity_group_count = 0
    single_form_group_count = 0
    prediction_count = 0
    true_count = 0
    false_count = 0

    for (public, window, object_key), group in sorted(groups.items()):
        q_values = sorted({p1036.q_coeff(form) for _index, form in group})
        if len(group) < 2:
            single_form_group_count += 1
            if len(evaluated_groups) < 16:
                evaluated_groups.append(
                    {
                        "eligible_form_count": len(group),
                        "family": family_descriptor(group[0][1]),
                        "object_key": object_key,
                        "prediction_count": 0,
                        "predictions": [],
                        "public_fingerprint": public,
                        "q_values": q_values,
                        "window": window,
                    }
                )
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
                    compact_prediction(left_index, left, right_index, right, factors, predicted, verified, source_secrets)
                )
        if not predictions:
            factor_matchless_q_diverse_group_count += 1
        if predictions or len(evaluated_groups) < 24:
            evaluated_groups.append(
                {
                    "eligible_form_count": len(group),
                    "family": family_descriptor(group[0][1]),
                    "object_key": object_key,
                    "prediction_count": len(predictions),
                    "predictions": predictions[:12],
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


def aggregate_object_results(results: list[dict[str, Any]]) -> dict[str, Any]:
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
    summary = {field: sum(int_value(result.get(field)) for result in results) for field in fields}
    summary["validation_success"] = any(bool(result.get("validation_success")) for result in results)
    return summary


def evaluate_rows(rows: list[dict[str, Any]], windows: list[str], label: str, compressed: bool) -> dict[str, Any]:
    forms, meta = p1036.reconstruct_pool(rows, compressed)
    factors = int_value(meta.get("factor_count"))
    object_results = [evaluate_object(forms, factors, windows, spec) for spec in p1036.object_specs()]
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


def selected_rows_for_pool(
    by_window: dict[str, list[dict[str, Any]]],
    windows: list[str],
    predicate: p1035.RowPredicate,
) -> list[dict[str, Any]]:
    return p1035.selected_rows_for_pool(by_window, windows, predicate, "fresh_validation")


def evaluate_pool(
    pool: dict[str, Any],
    scout_by_window: dict[str, list[dict[str, Any]]],
    forward_by_window: dict[str, list[dict[str, Any]]],
    forward_windows: list[str],
) -> dict[str, Any]:
    predicate = pool["predicate"]
    scout_rows = selected_rows_for_pool(scout_by_window, [SIGNAL_WINDOW], predicate)
    forward_rows = selected_rows_for_pool(forward_by_window, forward_windows, predicate)
    evaluations = []
    for compressed in (False, True):
        suffix = "compressed" if compressed else "raw"
        evaluations.append(evaluate_rows(scout_rows, [SIGNAL_WINDOW], f"{pool['name']}_scout_{suffix}", compressed))
        evaluations.append(evaluate_rows(forward_rows, forward_windows, f"{pool['name']}_forward_{suffix}", compressed))
    scout_evals = [item for item in evaluations if "_scout_" in item["label"]]
    forward_evals = [item for item in evaluations if "_forward_" in item["label"]]
    forward_compressed = [item for item in forward_evals if item["label"].endswith("_compressed")]
    forward_raw = [item for item in forward_evals if item["label"].endswith("_raw")]
    return {
        "description": pool["description"],
        "evaluations": evaluations,
        "forward_compressed_summary": aggregate_summaries(forward_compressed),
        "forward_raw_summary": aggregate_summaries(forward_raw),
        "forward_summary": aggregate_summaries(forward_evals),
        "name": pool["name"],
        "row_counts": {
            "forward_rows": len(forward_rows),
            "scout_rows": len(scout_rows),
        },
        "scout_summary": aggregate_summaries(scout_evals),
    }


def determine_claim(pool_results: list[dict[str, Any]]) -> str:
    compressed_false = sum(int_value(result["forward_compressed_summary"].get("false_count")) for result in pool_results)
    compressed_predictions = sum(
        int_value(result["forward_compressed_summary"].get("prediction_count")) for result in pool_results
    )
    compressed_qdiv = sum(int_value(result["forward_compressed_summary"].get("q_diverse_group_count")) for result in pool_results)
    compressed_eligible = sum(int_value(result["forward_compressed_summary"].get("eligible_form_count")) for result in pool_results)
    if compressed_false:
        return "NEGATIVE_RESULT_P1038_GUARDED_COMPRESSED_FALSE_PREDICTION"
    if compressed_predictions:
        return "P1038_GUARDED_STRUCTURAL_FAMILY_SUPPLY_SIGNAL"
    if compressed_qdiv:
        return "NEGATIVE_RESULT_P1038_GUARDED_Q_DIVERSE_NO_FACTOR_MATCH"
    if compressed_eligible:
        return "NEGATIVE_RESULT_P1038_GUARDED_NO_Q_DIVERSE_GROUPS"
    return "NEGATIVE_RESULT_P1038_NO_GUARDED_REPEATED_TWO_TAIL_FORMS"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    forward_windows = discover_forward_windows(args.start_window, args.max_windows)
    scout_by_window, scout_exists = p1035.load_rows([SIGNAL_WINDOW], args.targets, args.min_source_rank)
    forward_by_window, forward_exists = p1035.load_rows(forward_windows, args.targets, args.min_source_rank)
    pool_results = [evaluate_pool(pool, scout_by_window, forward_by_window, forward_windows) for pool in p1035.pool_specs()]
    claim = determine_claim(pool_results)
    all_windows = [SIGNAL_WINDOW, *forward_windows]
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
            "p1037_guard_source_sha256": p1005.sha256_file(
                Path("tasks/ecdlp_index_calculus/low_term_total2_p1037_p231_public_consistency_guard_scout.py")
            ),
            "script_sha256": p1005.sha256_file(Path(__file__)),
            "source_sha256": source_hashes,
        },
        "claim_status": claim,
        "claim_taxonomy": "OBSERVATION" if claim.startswith("P1038_") else "NEGATIVE RESULT",
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled small-prime p231 ECDLP harness only.",
            "FROZEN-GUARD: term_gap_ge_3 OR tail_width_ge_3 was chosen by P1037 before this forward scan.",
            "COMPRESSED-PRIMARY: row-signature-compressed forward forms drive the claim; raw forms are diagnostic.",
            "STRICT-ELIMINATION: predictions require exact local factor-vector equality.",
            "INDEX-CALCULUS PRECURSOR: this is relation-generation supply, not sparse linear algebra or target descent.",
            "RHO BOUNDARY: Pollard rho remains the one-target scalar-search baseline.",
        ],
        "parameters": {
            "forward_windows": forward_windows,
            "guard": "term_gap_ge_3 OR tail_width_ge_3",
            "max_windows": args.max_windows,
            "min_source_rank": args.min_source_rank,
            "pool_names": [pool["name"] for pool in p1035.pool_specs()],
            "signal_window": SIGNAL_WINDOW,
            "start_window": args.start_window,
            "targets": [target.strip() for target in args.targets.split(",") if target.strip()],
        },
        "pool_results": pool_results,
        "schema": SCHEMA,
        "source": {
            "forward_exists": forward_exists,
            "scout_exists": scout_exists,
        },
        "summary": {
            "claim_status": claim,
            "forward_by_pool": [
                {
                    "compressed_eligible_form_count": result["forward_compressed_summary"]["eligible_form_count"],
                    "compressed_false_count": result["forward_compressed_summary"]["false_count"],
                    "compressed_factor_matchless_q_diverse_group_count": result["forward_compressed_summary"][
                        "factor_matchless_q_diverse_group_count"
                    ],
                    "compressed_prediction_count": result["forward_compressed_summary"]["prediction_count"],
                    "compressed_q_diverse_group_count": result["forward_compressed_summary"]["q_diverse_group_count"],
                    "compressed_true_count": result["forward_compressed_summary"]["true_count"],
                    "name": result["name"],
                    "raw_false_count": result["forward_raw_summary"]["false_count"],
                    "raw_prediction_count": result["forward_raw_summary"]["prediction_count"],
                    "row_count": result["row_counts"]["forward_rows"],
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
    parser.add_argument("--max-windows", type=int, default=DEFAULT_MAX_WINDOWS, help="Maximum forward windows to scan")
    parser.add_argument("--min-source-rank", type=int, default=0, help="Minimum source rank for expanded row loading")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    parser.add_argument("--start-window", default=DEFAULT_START, help="First forward window to scan")
    parser.add_argument("--targets", default=p1022.DEFAULT_TARGET, help="Comma-separated target filter")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    bits = []
    for item in payload["summary"]["forward_by_pool"]:
        bits.append(
            "{name}:rows={rows} c_eligible={eligible} c_qdiv={qdiv} c_pred={pred} c_false={false} raw_pred={raw_pred} raw_false={raw_false}".format(
                name=item["name"],
                rows=item["row_count"],
                eligible=item["compressed_eligible_form_count"],
                qdiv=item["compressed_q_diverse_group_count"],
                pred=item["compressed_prediction_count"],
                false=item["compressed_false_count"],
                raw_pred=item["raw_prediction_count"],
                raw_false=item["raw_false_count"],
            )
        )
    print(
        "claim={claim} windows={windows} out={out} {bits}".format(
            claim=payload["claim_status"],
            windows=",".join(payload["parameters"]["forward_windows"]),
            out=args.out,
            bits="; ".join(bits),
        )
    )


if __name__ == "__main__":
    main()
