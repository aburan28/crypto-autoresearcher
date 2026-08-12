#!/usr/bin/env python3
"""Scout source-only features for leaf-16 order-9887 relation routing.

Selection in this script uses only source-row metadata emitted before direct
selected-leaf hit-root replay. Gate/verifier outcomes are joined only as labels.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


STATE_DIR = Path("ecdlp_index_calculus_state")
DEFAULT_TRAIN_SOURCES = [
    STATE_DIR / "low_term_total2_order9887_p566_leaf16_frozen_root_saved_source_20605_20616_probe.json",
    STATE_DIR / "low_term_total2_order9887_p567_leaf16_phase_route_source_20617_20628_probe.json",
    STATE_DIR / "low_term_total2_order9887_p568_leaf16_right207_volume_source_20629_20640_probe.json",
]
DEFAULT_TRAIN_GATES = [
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p566_order9887_leaf16_frozen_root_saved_20605_20616_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p567_order9887_phase_route_20617_20628_density_gate_probe.json",
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p568_order9887_right207_volume_20629_20640_density_gate_probe.json",
]
DEFAULT_VALIDATION_SOURCE = STATE_DIR / "low_term_total2_order9887_p570_leaf16_pre_hit_source_20641_20652_probe.json"
DEFAULT_VALIDATION_GATE = (
    STATE_DIR / "low_term_total2_fixed_leaf_shared_product_gate_p570_order9887_pre_hit_source_20641_20652_density_gate_probe.json"
)
DEFAULT_OUT = STATE_DIR / "low_term_total2_p570_pre_hit_source_feature_scout_20641_20652_probe.json"


Feature = dict[str, Any]
Predicate = Callable[[Feature], bool]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text()) if path.exists() else {}


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


def float_value(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def ratio(numerator: int | float, denominator: int | float) -> float | None:
    if not denominator:
        return None
    return round(float(numerator) / float(denominator), 8)


def parse_paths(raw: str | None, defaults: list[Path]) -> list[Path]:
    if not raw:
        return defaults
    return [Path(item.strip()) for item in raw.split(",") if item.strip()]


def parse_salt(row_key: str) -> int | None:
    match = re.search(r"salt(\d+)", row_key)
    return int(match.group(1)) if match else None


def base_selector(selector: str) -> str:
    return selector.split("__", 1)[0]


def case_entry(target: str, transfer: int, selector: str, top_k: int) -> str:
    return f"{target}|{int(transfer)}|{selector}|{int(top_k)}"


def leaf_key(values: list[Any]) -> str:
    vals = [int_value(value) for value in values]
    return "-".join(f"{value:02d}" for value in vals)


def gate_labels(gate_paths: list[Path]) -> dict[str, dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    for path in gate_paths:
        gate = load_json(path)
        for case in gate.get("cases") or []:
            if not isinstance(case, dict):
                continue
            target = str(case.get("target"))
            transfer = int_value(case.get("transfer_index"))
            selector = str(case.get("selector"))
            top_k = int_value(case.get("top_k"))
            key = case_entry(target, transfer, selector, top_k)
            labels[key] = {
                "direct_below_rho": bool(case.get("direct_below_rho")),
                "direct_below_rho_verified": bool(
                    case.get("direct_below_rho") and case.get("direct_union_public_key_verified")
                ),
                "direct_ops_over_rho": case.get("direct_verifier_replay_ops_over_rho"),
                "direct_verified": bool(case.get("direct_union_public_key_verified")),
                "rank": int_value(case.get("direct_union_rank")),
                "relation_count": int_value(case.get("direct_union_relation_count")),
            }
    return labels


def source_rows(source_paths: list[Path], labels: dict[str, dict[str, Any]], source_prefix: str) -> list[Feature]:
    rows: list[Feature] = []
    for path in source_paths:
        source = load_json(path)
        for policy_name, policy in (source.get("policies") or {}).items():
            if not isinstance(policy, dict):
                continue
            for row in policy.get("stress_leaf_results") or []:
                if not isinstance(row, dict):
                    continue
                target = str(row.get("target"))
                transfer = int_value(row.get("transfer_index"))
                selector = str(row.get("selector"))
                top_k = int_value(row.get("top_k"))
                key = case_entry(target, transfer, selector, top_k)
                label = labels.get(key, {})
                row_keys = [str(item) for item in row.get("row_keys") or []]
                salts = [salt for salt in (parse_salt(row_key) for row_key in row_keys) if salt is not None]
                left = [int_value(item) for item in row.get("left_leaf_indices") or []]
                right = [int_value(item) for item in row.get("right_leaf_indices") or []]
                right_anchor = int_value(row.get("right_anchor"))
                feature: Feature = {
                    "base_selector": str(row.get("base_selector") or base_selector(selector)),
                    "case_entry": key,
                    "direct_below_rho_verified": bool(label.get("direct_below_rho_verified")),
                    "direct_ops_over_rho": label.get("direct_ops_over_rho"),
                    "direct_verified": bool(label.get("direct_verified")),
                    "leaf_signature": f"L{leaf_key(left)}_R{leaf_key(right)}",
                    "left_leaf_signature": leaf_key(left),
                    "policy_name": str(policy_name),
                    "policy_role": str(row.get("policy_role")),
                    "rank": int_value(label.get("rank")),
                    "relation_count": int_value(label.get("relation_count")),
                    "right_anchor": right_anchor,
                    "right_leaf_signature": leaf_key(right),
                    "row_pair": str(row.get("row_pair_public_id") or "+".join(f"salt{salt}" for salt in salts)),
                    "row_pair_key": str(row.get("row_pair_key")),
                    "salt_left": salts[0] if len(salts) >= 1 else None,
                    "salt_right": salts[1] if len(salts) >= 2 else None,
                    "selected_leaf_count": int_value(row.get("selected_leaf_count")),
                    "selector": selector,
                    "source_artifact": str(path),
                    "source_name": source_prefix,
                    "target": target,
                    "top_k": top_k,
                    "transfer_index": transfer,
                    "transfer_mod12": transfer % 12,
                    "transfer_mod7": transfer % 7,
                }
                rows.append(feature)
    rows.sort(key=lambda item: (item["transfer_index"], item["row_pair"], item["right_anchor"], item["selector"]))
    return rows


def source_right207_phase1or6(row: Feature) -> bool:
    return row["transfer_mod12"] in {1, 6} and row["salt_right"] == 207


def source_right207_phase1or6_anchor9(row: Feature) -> bool:
    return source_right207_phase1or6(row) and row["right_anchor"] == 9


def source_right207_phase6(row: Feature) -> bool:
    return row["transfer_mod12"] == 6 and row["salt_right"] == 207


def source_right207_phase1(row: Feature) -> bool:
    return row["transfer_mod12"] == 1 and row["salt_right"] == 207


def source_anchor9_phase1or6(row: Feature) -> bool:
    return row["transfer_mod12"] in {1, 6} and row["right_anchor"] == 9


def frozen_rule_specs() -> list[tuple[str, str, Predicate]]:
    return [
        (
            "source_right207_phase1or6",
            "transfer mod 12 in {1,6} and right row salt=207",
            source_right207_phase1or6,
        ),
        (
            "source_right207_phase1or6_anchor9",
            "transfer mod 12 in {1,6}, right row salt=207, right anchor=9",
            source_right207_phase1or6_anchor9,
        ),
        (
            "source_right207_phase6",
            "transfer mod 12=6 and right row salt=207",
            source_right207_phase6,
        ),
        (
            "source_right207_phase1",
            "transfer mod 12=1 and right row salt=207",
            source_right207_phase1,
        ),
        (
            "source_anchor9_phase1or6",
            "transfer mod 12 in {1,6} and right anchor=9",
            source_anchor9_phase1or6,
        ),
    ]


def compact_row(row: Feature) -> dict[str, Any]:
    return {
        "base_selector": row["base_selector"],
        "case_entry": row["case_entry"],
        "direct_below_rho_verified": row["direct_below_rho_verified"],
        "direct_ops_over_rho": row["direct_ops_over_rho"],
        "leaf_signature": row["leaf_signature"],
        "policy_role": row["policy_role"],
        "right_anchor": row["right_anchor"],
        "row_pair": row["row_pair"],
        "salt_left": row["salt_left"],
        "salt_right": row["salt_right"],
        "selector": row["selector"],
        "top_k": row["top_k"],
        "transfer_index": row["transfer_index"],
        "transfer_mod12": row["transfer_mod12"],
    }


def summarize_selection(rows: list[Feature], selected: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
    selected_verified = [row for row in selected if row["direct_verified"]]
    best = sorted(
        selected_positive,
        key=lambda row: (
            float_value(row.get("direct_ops_over_rho"), 10**18),
            int_value(row.get("transfer_index")),
            str(row.get("selector")),
        ),
    )
    return {
        "direct_below_rho_verified_count": len(selected_positive),
        "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
        "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
        "direct_verified_count": len(selected_verified),
        "direct_verified_precision": ratio(len(selected_verified), len(selected)),
        "examples": [compact_row(row) for row in best[:12]],
        "raw_positive_count": len(positives),
        "row_pair_counts": dict(Counter(str(row["row_pair"]) for row in selected).most_common(16)),
        "selected_case_entries": [row["case_entry"] for row in selected],
        "selected_direct_below_rho_verified_case_entries": [row["case_entry"] for row in selected_positive],
        "selected_count": len(selected),
        "selected_fraction": ratio(len(selected), len(rows)),
        "transfer_counts": dict(sorted(Counter(str(row["transfer_index"]) for row in selected).items(), key=lambda item: int(item[0]))),
    }


def evaluate_frozen_rules(rows: list[Feature]) -> list[dict[str, Any]]:
    reports = []
    for name, description, predicate in frozen_rule_specs():
        selected = [row for row in rows if predicate(row)]
        reports.append({"rule": name, "description": description, **summarize_selection(rows, selected)})
    reports.sort(key=lambda report: (0 if report["rule"] == "source_right207_phase1or6" else 1, str(report["rule"])))
    return reports


TOKEN_FIELDS = [
    "base_selector",
    "leaf_signature",
    "left_leaf_signature",
    "policy_role",
    "right_anchor",
    "right_leaf_signature",
    "row_pair",
    "salt_left",
    "salt_right",
    "selected_leaf_count",
    "top_k",
    "transfer_mod12",
    "transfer_mod7",
]


def token_for(row: Feature, field: str) -> str:
    return f"{field}={row.get(field)}"


def token_candidates(rows: list[Feature], max_size: int, min_selected: int) -> list[dict[str, Any]]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    token_to_rows: dict[tuple[str, ...], list[Feature]] = defaultdict(list)
    for row in rows:
        base_tokens = [token_for(row, field) for field in TOKEN_FIELDS]
        for size in range(1, max_size + 1):
            for combo in itertools.combinations(base_tokens, size):
                token_to_rows[combo].append(row)
    reports = []
    for tokens, selected in token_to_rows.items():
        if len(selected) < min_selected:
            continue
        selected_positive = [row for row in selected if row["direct_below_rho_verified"]]
        if not selected_positive:
            continue
        reports.append(
            {
                "direct_below_rho_verified_count": len(selected_positive),
                "direct_below_rho_verified_precision": ratio(len(selected_positive), len(selected)),
                "direct_below_rho_verified_recall": ratio(len(selected_positive), len(positives)),
                "examples": [compact_row(row) for row in selected_positive[:8]],
                "selected_count": len(selected),
                "selected_fraction": ratio(len(selected), len(rows)),
                "tokens": list(tokens),
            }
        )
    reports.sort(
        key=lambda report: (
            -float_value(report.get("direct_below_rho_verified_precision")),
            -int_value(report.get("direct_below_rho_verified_count")),
            int_value(report.get("selected_count")),
            report.get("tokens"),
        )
    )
    return reports[:80]


def dataset_summary(rows: list[Feature]) -> dict[str, Any]:
    positives = [row for row in rows if row["direct_below_rho_verified"]]
    return {
        "case_count": len(rows),
        "direct_below_rho_verified_count": len(positives),
        "direct_verified_count": sum(1 for row in rows if row["direct_verified"]),
        "positive_transfer_counts": dict(sorted(Counter(str(row["transfer_index"]) for row in positives).items(), key=lambda item: int(item[0]))),
        "source_artifact_counts": dict(Counter(str(row["source_artifact"]) for row in rows).most_common()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train-sources", default=None)
    parser.add_argument("--train-gates", default=None)
    parser.add_argument("--validation-source", type=Path, default=DEFAULT_VALIDATION_SOURCE)
    parser.add_argument("--validation-gate", type=Path, default=DEFAULT_VALIDATION_GATE)
    parser.add_argument("--max-token-size", type=int, default=3)
    parser.add_argument("--min-token-selected", type=int, default=4)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    train_sources = parse_paths(args.train_sources, DEFAULT_TRAIN_SOURCES)
    train_gates = parse_paths(args.train_gates, DEFAULT_TRAIN_GATES)
    train_rows = source_rows(train_sources, gate_labels(train_gates), "training")
    validation_rows = source_rows(
        [args.validation_source],
        gate_labels([args.validation_gate]),
        "validation",
    )
    train_rules = evaluate_frozen_rules(train_rows)
    validation_rules = evaluate_frozen_rules(validation_rows)
    main_validation = next(report for report in validation_rules if report["rule"] == "source_right207_phase1or6")
    payload = {
        "artifacts": {
            "train_gates": [str(path) for path in train_gates],
            "train_sources": [str(path) for path in train_sources],
            "validation_gate": str(args.validation_gate),
            "validation_source": str(args.validation_source),
        },
        "created_at": now_iso(),
        "honesty_boundary": [
            "TOY-EVIDENCE: order-9887 local verifier harness only.",
            "SOURCE-ONLY SELECTION: frozen rules and token conjunctions use source-row metadata only.",
            "LABEL BOUNDARY: direct verifier outcomes and rho comparisons are used only for scoring.",
            "NO SPEEDUP CLAIM: this is a source-feature enrichment scout before source-generation, sparse-LA, and target-descent costs are closed.",
        ],
        "method": "p570_pre_hit_source_feature_scout",
        "schema": "ecdlp.low_term_total2_p570_pre_hit_source_feature_scout.v1",
        "summary": {
            "claim_status": (
                "PRE_HIT_SOURCE_FEATURE_VALIDATION_POSITIVE"
                if main_validation["direct_below_rho_verified_count"]
                else "NEGATIVE_RESULT_PRE_HIT_SOURCE_FEATURE_RULE_NO_VALIDATION_POSITIVE"
            ),
            "main_rule": "source_right207_phase1or6",
            "training": {
                "dataset": dataset_summary(train_rows),
                "main_rule": next(report for report in train_rules if report["rule"] == "source_right207_phase1or6"),
            },
            "validation": {
                "dataset": dataset_summary(validation_rows),
                "main_rule": main_validation,
            },
        },
        "top_training_token_conjunctions": token_candidates(
            train_rows,
            args.max_token_size,
            args.min_token_selected,
        ),
        "training_rule_reports": train_rules,
        "validation_rule_reports": validation_rules,
    }
    write_json(args.out, payload)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
