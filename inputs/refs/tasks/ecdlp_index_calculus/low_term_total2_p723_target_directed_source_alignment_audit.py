#!/usr/bin/env python3
"""P723 target-directed source-alignment audit for the P722 hard split."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import low_term_total2_p712_rel2_fresh_window_validation as p712
import low_term_total2_p716_rel2_source_generation_enrichment as p716


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_OUT = STATE_DIR / "low_term_total2_p723_target_directed_source_alignment_audit_probe.json"
BASE_PATTERN = "frontier_public_leaf_policy_p231_frozen_prefix_fixed_row_*_col15_selector_expanded_probe.json"
FRESH_PATTERN = "frontier_public_leaf_policy_p722_density*_fixed_row_*_col15_selector_expanded_probe.json"
TARGET = "67.a1@9803"
NEGATIVE_TARGET = "22050.cf1@11731"
TRAIN_RANGE = (20232, 20439)
HARD_RANGE = (20440, 20591)
HARD_HOLES = ((20488, 20495), (20504, 20511), (20512, 20519))


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def target_prefix(row_key: Any) -> str:
    text = str(row_key or "")
    return text.split(":uniform:", 1)[0] if ":uniform:" in text else text.split(":salt", 1)[0]


def row_leaf_keys(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in row.get("row_leaf_keys") or [] if isinstance(item, dict)]


def row_key_targets(row: dict[str, Any]) -> tuple[str, ...]:
    keys = [target_prefix(key) for key in row.get("row_keys") or []]
    keys.extend(target_prefix(item.get("row_key")) for item in row_leaf_keys(row))
    return tuple(sorted(set(key for key in keys if key)))


def target_key_exact(row: dict[str, Any], target: str = TARGET) -> bool:
    targets = row_key_targets(row)
    return bool(targets) and all(item == target for item in targets)


def leaf_indices(row: dict[str, Any]) -> tuple[int, ...]:
    values: list[int] = []
    for item in row_leaf_keys(row):
        values.extend(p716.int_value(value) for value in item.get("leaf_indices") or [])
    return tuple(sorted(values))


def leaf_shape(row: dict[str, Any]) -> tuple[int, ...]:
    return tuple(sorted(len(item.get("leaf_indices") or []) for item in row_leaf_keys(row)))


def row_pair(row: dict[str, Any]) -> str:
    salts: list[str] = []
    for key in row.get("row_keys") or []:
        text = str(key)
        salts.append(text.rsplit(":", 1)[-1])
    return "_".join(sorted(salts))


def raw_row_key(row: dict[str, Any], source_path: Path, policy_name: str, row_index: int) -> tuple[Any, ...]:
    return (
        str(source_path),
        policy_name,
        row_index,
        row.get("target"),
        p716.int_value(row.get("transfer_index")),
        p716.selector_mode(row.get("selector")),
        p716.int_value(row.get("top_k")),
        tuple(str(key) for key in row.get("row_keys") or []),
        tuple((str(item.get("row_key")), tuple(p716.int_value(v) for v in item.get("leaf_indices") or [])) for item in row_leaf_keys(row)),
        p716.int_value(row.get("relation_count")),
    )


def source_paths(pattern: str, min_transfer: int, max_transfer: int, p709: str) -> list[Path]:
    args = argparse.Namespace(
        min_transfer=min_transfer,
        max_transfer=max_transfer,
        p709=p709,
        source_pattern=pattern,
    )
    return p712.source_paths(args)


def load_raw_rows(pattern: str, min_transfer: int, max_transfer: int, p709: str, origin: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for source_path in source_paths(pattern, min_transfer, max_transfer, p709):
        source = load_json(source_path)
        parsed = p712.window_range(source_path)
        if parsed is None:
            continue
        for policy_name, policy in (source.get("policies") or {}).items():
            if not isinstance(policy, dict):
                continue
            row_selector = (policy.get("row_selector") or {}).get("selector")
            for row_index, row in enumerate(policy.get("stress_leaf_results") or []):
                if not isinstance(row, dict):
                    continue
                key = raw_row_key(row, source_path, str(policy_name), row_index)
                if key in seen:
                    continue
                seen.add(key)
                item = {
                    "below_rho": bool(row.get("below_rho")),
                    "direct_ops_over_rho": p716.float_value(row.get("ops_over_rho"), 999999.0),
                    "key": "|".join(str(part) for part in key),
                    "leaf_indices": leaf_indices(row),
                    "leaf_shape": leaf_shape(row),
                    "origin": origin,
                    "policy": str(policy_name),
                    "public_key_verified": bool(row.get("public_key_verified")),
                    "relation_count": p716.int_value(row.get("relation_count")),
                    "row_key_targets": row_key_targets(row),
                    "row_keys": [str(key) for key in row.get("row_keys") or []],
                    "row_leaf_keys": row.get("row_leaf_keys") or [],
                    "row_pair": row_pair(row),
                    "row_selector": row.get("row_selector") or row_selector,
                    "selected_leaf_count": p716.int_value(row.get("selected_leaf_count")),
                    "selected_row_count": p716.int_value(row.get("selected_row_count")),
                    "selector": p716.selector_mode(row.get("selector")),
                    "source": str(source_path),
                    "source_verified": bool(row.get("source_verified")),
                    "target": str(row.get("target")),
                    "target_key_exact": target_key_exact(row),
                    "top_k": p716.int_value(row.get("top_k")),
                    "transfer_index": p716.int_value(row.get("transfer_index")),
                    "window_end": parsed[1],
                    "window_start": parsed[0],
                }
                rows.append(item)
    rows.sort(key=lambda row: (
        p716.int_value(row.get("window_start")),
        p716.int_value(row.get("transfer_index")),
        str(row.get("target")),
        p716.float_value(row.get("direct_ops_over_rho"), 999999.0),
        str(row.get("selector")),
    ))
    return rows


def in_range(row: dict[str, Any], bounds: tuple[int, int]) -> bool:
    transfer = p716.int_value(row.get("transfer_index"))
    return bounds[0] <= transfer <= bounds[1]


def in_any_range(row: dict[str, Any], ranges: tuple[tuple[int, int], ...]) -> bool:
    return any(in_range(row, bounds) for bounds in ranges)


def compact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "origin": row.get("origin"),
        "target": row.get("target"),
        "transfer_index": row.get("transfer_index"),
        "selector": row.get("selector"),
        "top_k": row.get("top_k"),
        "relation_count": row.get("relation_count"),
        "ops_over_rho": row.get("direct_ops_over_rho"),
        "row_pair": row.get("row_pair"),
        "leaf_indices": list(row.get("leaf_indices") or []),
        "row_key_targets": list(row.get("row_key_targets") or []),
        "target_key_exact": row.get("target_key_exact"),
    }


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    targets = Counter(str(row.get("target")) for row in rows)
    selectors = Counter(str(row.get("selector")) for row in rows)
    top_k = Counter(str(row.get("top_k")) for row in rows)
    rel2 = [row for row in rows if p716.int_value(row.get("relation_count")) == 2]
    target_key_rows = [row for row in rows if row.get("target_key_exact")]
    return {
        "below_rho_count": sum(1 for row in rows if row.get("below_rho")),
        "count": len(rows),
        "examples": [compact_row(row) for row in rows[:6]],
        "public_key_verified_count": sum(1 for row in rows if row.get("public_key_verified")),
        "rel2_count": len(rel2),
        "rel2_verified_count": sum(1 for row in rel2 if row.get("public_key_verified")),
        "selector_counts": dict(selectors.most_common(8)),
        "target_counts": dict(targets.most_common()),
        "target_key_exact_count": len(target_key_rows),
        "target_key_rel2_count": sum(1 for row in target_key_rows if p716.int_value(row.get("relation_count")) == 2),
        "top_k_counts": dict(top_k.most_common(8)),
    }


def feature_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    rel2 = [row for row in rows if p716.int_value(row.get("relation_count")) == 2 and row.get("target_key_exact")]
    return {
        "leaf_indices": sorted({idx for row in rel2 for idx in row.get("leaf_indices") or []}),
        "leaf_shapes": sorted({tuple(row.get("leaf_shape") or []) for row in rel2}),
        "row_pairs": sorted({str(row.get("row_pair")) for row in rel2}),
        "selector_topk_pairs": sorted({(str(row.get("selector")), p716.int_value(row.get("top_k"))) for row in rel2}),
        "selectors": sorted({str(row.get("selector")) for row in rel2}),
        "top_k": sorted({p716.int_value(row.get("top_k")) for row in rel2}),
        "train_rel2_count": len(rel2),
    }


def make_policies(profile: dict[str, Any]) -> dict[str, Callable[[dict[str, Any]], bool]]:
    selectors = set(profile["selectors"])
    top_k_values = set(profile["top_k"])
    selector_topk_pairs = {tuple(item) for item in profile["selector_topk_pairs"]}
    leaf_shapes = {tuple(item) for item in profile["leaf_shapes"]}
    row_pairs = set(profile["row_pairs"])
    leaf_index_values = set(profile["leaf_indices"])
    return {
        "target_key_any": lambda row: bool(row.get("target_key_exact")),
        "target_key_rel2": lambda row: bool(row.get("target_key_exact")) and p716.int_value(row.get("relation_count")) == 2,
        "target_key_train_selector_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and str(row.get("selector")) in selectors,
        "target_key_train_topk_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and p716.int_value(row.get("top_k")) in top_k_values,
        "target_key_train_selector_topk_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and (str(row.get("selector")), p716.int_value(row.get("top_k"))) in selector_topk_pairs,
        "target_key_train_leafshape_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and tuple(row.get("leaf_shape") or []) in leaf_shapes,
        "target_key_train_leafindex_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and bool(set(row.get("leaf_indices") or []) & leaf_index_values),
        "target_key_train_rowpair_rel2": lambda row: bool(row.get("target_key_exact"))
        and p716.int_value(row.get("relation_count")) == 2
        and str(row.get("row_pair")) in row_pairs,
        "rel2_any_no_target_key_control": lambda row: p716.int_value(row.get("relation_count")) == 2,
        "train_selector_topk_no_target_key_control": lambda row: p716.int_value(row.get("relation_count")) == 2
        and (str(row.get("selector")), p716.int_value(row.get("top_k"))) in selector_topk_pairs,
    }


def evaluate_policy(rows: list[dict[str, Any]], accepts: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    accepted = [row for row in rows if accepts(row)]
    return {
        "accepted": summarize_rows(accepted),
        "accepted_count": len(accepted),
        "accepted_rel2_count": sum(1 for row in accepted if p716.int_value(row.get("relation_count")) == 2),
        "accepted_target_key_count": sum(1 for row in accepted if row.get("target_key_exact")),
        "accepted_targets": dict(Counter(str(row.get("target")) for row in accepted).most_common()),
        "total_count": len(rows),
    }


def determine_claim(datasets: dict[str, list[dict[str, Any]]], policy_results: dict[str, Any]) -> str:
    p722_target = datasets["p722_fresh_target"]
    p722_target_rel2 = [row for row in p722_target if p716.int_value(row.get("relation_count")) == 2]
    if not p722_target:
        return "NEGATIVE_RESULT_P723_P722_HAS_NO_TARGET67_MATERIALIZED_ROWS"
    if not p722_target_rel2:
        return "P723_TARGET67_RAW_ROWS_FOUND_REL2_CONVERSION_OPEN"
    for policy, by_dataset in policy_results.items():
        if not policy.startswith("target_key"):
            continue
        if by_dataset["p722_fresh_target"]["accepted_rel2_count"] and by_dataset["p722_fresh_negative"]["accepted_count"] == 0:
            return "P723_TARGET_DIRECTED_DESCRIPTOR_FINDS_FRESH_TARGET67_REL2"
    return "NEGATIVE_RESULT_P723_TARGET67_REL2_NOT_PUBLICLY_SEPARATED"


def analyze(args: argparse.Namespace) -> dict[str, Any]:
    base_rows = load_raw_rows(
        args.base_source_pattern,
        p716.int_value(args.min_transfer),
        p716.int_value(args.max_transfer),
        args.p709,
        "base_p231",
    )
    fresh_rows = load_raw_rows(
        args.fresh_source_pattern,
        p716.int_value(args.min_transfer),
        p716.int_value(args.max_transfer),
        args.p709,
        "fresh_p722",
    )
    datasets = {
        "base_train_target": [row for row in base_rows if row.get("target") == args.target and in_range(row, TRAIN_RANGE)],
        "base_holdout_target": [row for row in base_rows if row.get("target") == args.target and in_range(row, HARD_RANGE)],
        "base_hard_hole_target": [row for row in base_rows if row.get("target") == args.target and in_any_range(row, HARD_HOLES)],
        "base_train_negative": [row for row in base_rows if row.get("target") == args.negative_target and in_range(row, TRAIN_RANGE)],
        "base_holdout_negative": [row for row in base_rows if row.get("target") == args.negative_target and in_range(row, HARD_RANGE)],
        "p722_fresh_target": [row for row in fresh_rows if row.get("target") == args.target],
        "p722_fresh_negative": [row for row in fresh_rows if row.get("target") == args.negative_target],
        "p722_fresh_all": fresh_rows,
    }
    profile = feature_profile(datasets["base_train_target"])
    policies = make_policies(profile)
    policy_results = {
        name: {dataset: evaluate_policy(rows, accepts) for dataset, rows in datasets.items()}
        for name, accepts in policies.items()
    }
    payload = {
        "claim_status": "",
        "created_at": now_iso(),
        "dataset_summaries": {name: summarize_rows(rows) for name, rows in datasets.items()},
        "descriptor_profile": profile,
        "hard_holes": [list(item) for item in HARD_HOLES],
        "honesty_boundary": [
            "TOY-EVIDENCE: controlled toy-prime ECDLP harness only.",
            "MODEL-BOUND: source rows are archived AutoLab toy-harness artifacts.",
            "PUBLIC-DESCRIPTOR ONLY: target labels, row keys, selectors, top-k, leaf counts, relation counts, and transfer windows are used; no scalar or verifier-derived secret is used for selection.",
            "NO DEPLOYED-CURVE CLAIM: sparse linear algebra, target descent, and large-prime scaling remain open.",
        ],
        "interpretation": "",
        "method": "p723_target_directed_source_alignment_audit",
        "parameters": {
            "base_source_pattern": args.base_source_pattern,
            "fresh_source_pattern": args.fresh_source_pattern,
            "hard_range": list(HARD_RANGE),
            "max_transfer": p716.int_value(args.max_transfer),
            "min_transfer": p716.int_value(args.min_transfer),
            "negative_target": args.negative_target,
            "target": args.target,
            "train_range": list(TRAIN_RANGE),
        },
        "policy_evaluations": policy_results,
        "schema": "ecdlp.low_term_total2_p723_target_directed_source_alignment_audit.v1",
    }
    payload["claim_status"] = determine_claim(datasets, policy_results)
    if payload["claim_status"] == "NEGATIVE_RESULT_P723_P722_HAS_NO_TARGET67_MATERIALIZED_ROWS":
        payload["interpretation"] = (
            "P722 failed before leaf replay for target 67: the fresh artifacts contain no materialized "
            "target-67 rows. Public target-key descriptors preserve known P231 target-67 rows and reject "
            "the P722 22050 negative control, so P724 should force target-67 row-key materialization "
            "before selector or rel2 tuning."
        )
    else:
        payload["interpretation"] = (
            "P722 contains target-67 material; inspect policy_evaluations to decide whether the next "
            "step is rel2 conversion, descriptor separation, or shared-core replay."
        )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-source-pattern", default=BASE_PATTERN)
    parser.add_argument("--fresh-source-pattern", default=FRESH_PATTERN)
    parser.add_argument("--max-transfer", type=int, default=20807)
    parser.add_argument("--min-transfer", type=int, default=20232)
    parser.add_argument("--negative-target", default=NEGATIVE_TARGET)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument(
        "--p709",
        default=str(STATE_DIR / "low_term_total2_p709_source_replay_no_archive_oracle_probe.json"),
    )
    parser.add_argument("--target", default=TARGET)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = analyze(args)
    write_json(Path(args.out), payload)
    compact_datasets = {
        name: {
            key: summary[key]
            for key in (
                "count",
                "rel2_count",
                "public_key_verified_count",
                "target_key_exact_count",
                "target_key_rel2_count",
                "target_counts",
                "top_k_counts",
            )
        }
        for name, summary in payload["dataset_summaries"].items()
    }
    print(
        json.dumps(
            {
                "claim_status": payload["claim_status"],
                "dataset_summaries": compact_datasets,
                "descriptor_profile": payload["descriptor_profile"],
                "interpretation": payload["interpretation"],
                "selected_policy_checks": {
                    name: {
                        dataset: {
                            "accepted_count": result[dataset]["accepted_count"],
                            "accepted_rel2_count": result[dataset]["accepted_rel2_count"],
                            "accepted_target_key_count": result[dataset]["accepted_target_key_count"],
                            "accepted_targets": result[dataset]["accepted_targets"],
                            "total_count": result[dataset]["total_count"],
                        }
                        for dataset in ("base_holdout_target", "p722_fresh_negative", "p722_fresh_target")
                    }
                    for name, result in payload["policy_evaluations"].items()
                    if name in {
                        "target_key_any",
                        "target_key_rel2",
                        "target_key_train_selector_topk_rel2",
                        "rel2_any_no_target_key_control",
                    }
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
